#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import random
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
import torch

from bellman_kron import GridWorld, endpoint_boundary_states
from boundary_heatmap_gnn import (
    NODE_FEATURE_NAMES,
    BoundaryHeatmapGNN,
    GraphBoundarySample,
    boundary_metrics,
    collate_graphs,
    feature_normalization,
    select_boundary,
    state_dict_to_npz,
    teacher_student_loss,
    transition_graph_encoding,
)
from boundary_heatmap_contexts import rows_from_record
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import fixed_basis
from state_abstraction_baselines import gridworld_finite_mdp


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def median(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(clean)) if clean else float("nan")


def mean(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.fmean(clean)) if clean else float("nan")


def split_for_context(size: int, seed: int) -> str:
    """Split by topology, never by slip, to prevent same-maze leakage."""

    if size <= 15:
        return "train" if seed <= 7 else "validation"
    if size == 17:
        return "validation" if seed <= 3 else "test"
    return "test"


def sample_split(row: Mapping[str, object], size: int, seed: int, mode: str) -> str:
    teacher_split = str(row.get("split") or split_for_context(size, seed))
    if mode == "teacher":
        return teacher_split
    family = str(row.get("map_family", ""))
    if family in {"maze", "braid_maze", "random_maze"}:
        topology_seed = int(finite_float(row.get("topology_seed", seed), float(seed)))
        if topology_seed <= 3:
            return "train"
        if topology_seed == 4:
            return "validation"
        return "test"
    return teacher_split


def load_teacher_rows(path: Path, method: str) -> List[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    selected = [row for row in rows if row.get("method") == method and not row.get("error")]
    dedup: Dict[Tuple[str, str], Dict[str, object]] = {}
    for row in selected:
        dedup[(str(row.get("map")), str(row.get("slip")))] = row
    return list(dedup.values())


def heatmap_key(map_name: str, slip: float) -> Tuple[str, str]:
    return map_name, f"{float(slip):.12g}"


def load_heatmap_rows(path: Path) -> Dict[Tuple[str, str], Dict[int, Dict[str, object]]]:
    if not path.exists():
        return {}
    contexts: Dict[Tuple[str, str], Dict[int, Dict[str, object]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            if raw.get("error"):
                continue
            state = int(finite_float(raw.get("candidate_state"), -1.0))
            if state < 0:
                continue
            contexts.setdefault(
                heatmap_key(str(raw.get("map")), finite_float(raw.get("slip"), 0.0)), {}
            )[state] = dict(raw)
    return contexts


def build_sample(
    row: Mapping[str, object],
    args: argparse.Namespace,
    heatmaps: Mapping[Tuple[str, str], Mapping[int, Mapping[str, object]]],
) -> GraphBoundarySample:
    started = time.perf_counter()
    size = int(finite_float(row.get("map_size"), 0.0))
    seed = int(finite_float(row.get("maze_seed"), 0.0))
    slip = float(row.get("slip", 0.0))
    map_name = str(row.get("map"))
    family = str(row.get("map_family", "random_maze"))
    map_rows = rows_from_record(row)
    grid = GridWorld(map_rows)
    goal = grid.symbol_states("G")[0]
    mdp = gridworld_finite_mdp(grid, goal_state=goal, slip=slip)
    mandatory = tuple(sorted(endpoint_boundary_states(grid)))
    if args.candidate_universe == "teacher_basis":
        candidate_states = fixed_basis(
            map_name,
            grid=grid,
            kinds=args.fixed_basis_kinds,
            gamma=args.gamma,
            slip=slip,
            top_fraction=args.probe_top_fraction,
            random_count=args.fixed_random_count,
        )
    else:
        candidate_states = list(range(grid.n_states))
    teacher_boundary = tuple(sorted(int(state) for state in json.loads(str(row.get("boundary", "[]")))))
    missing = set(teacher_boundary) - set(candidate_states)
    if missing:
        raise ValueError(f"Teacher boundary is outside the candidate universe: {map_name}: {missing}")
    node_features, edge_index, edge_weight = transition_graph_encoding(
        mdp,
        mandatory=mandatory,
        candidate_states=candidate_states,
        slip=slip,
        gamma=args.gamma,
    )
    eligible = np.zeros(grid.n_states, dtype=bool)
    eligible[np.asarray(sorted(set(candidate_states) - set(mandatory)), dtype=int)] = True
    labels = np.zeros(grid.n_states, dtype=np.float32)
    extra = sorted(set(teacher_boundary) - set(mandatory))
    labels[np.asarray(extra, dtype=int)] = 1.0
    score_targets = np.zeros(grid.n_states, dtype=np.float32)
    score_mask = np.zeros(grid.n_states, dtype=bool)
    heatmap = heatmaps.get(heatmap_key(map_name, slip), {})
    for state, heatmap_row in heatmap.items():
        if 0 <= int(state) < grid.n_states:
            score_targets[int(state)] = float(
                heatmap_row.get("target_reduction", heatmap_row.get("target_score", 0.0))
            )
            score_mask[int(state)] = True
    if heatmap:
        top_value = max(float(score_targets[state]) for state in heatmap)
        teacher_top_set = tuple(
            sorted(
                int(state)
                for state in heatmap
                if abs(float(score_targets[int(state)]) - top_value) <= 1e-9
            )
        )
    else:
        teacher_top_set = tuple(extra)
    return GraphBoundarySample(
        name=map_name,
        split=sample_split(row, size, seed, args.split_mode),
        map_family=family,
        map_size=size,
        maze_seed=seed,
        slip=slip,
        node_features=node_features,
        edge_index=edge_index,
        edge_weight=edge_weight,
        labels=labels,
        score_targets=score_targets,
        score_mask=score_mask,
        eligible=eligible,
        mandatory=mandatory,
        teacher_boundary=teacher_boundary,
        teacher_top_set=teacher_top_set,
        teacher_feasible=parse_bool(row.get("group_all_feasible")),
        teacher_selection_time_sec=finite_float(row.get("selection_time_sec"), 0.0),
        teacher_row=dict(row),
        graph_encoding_time_sec=time.perf_counter() - started,
    )


def batches(
    samples: Sequence[GraphBoundarySample],
    batch_size: int,
    rng: random.Random,
) -> Iterable[List[GraphBoundarySample]]:
    order = list(range(len(samples)))
    rng.shuffle(order)
    for start in range(0, len(order), max(1, int(batch_size))):
        yield [samples[index] for index in order[start : start + batch_size]]


def synchronize(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def model_outputs(
    model: BoundaryHeatmapGNN,
    samples: Sequence[GraphBoundarySample],
    center: np.ndarray,
    scale: np.ndarray,
    device: torch.device,
    max_extra: int,
    measure_per_graph_latency: bool = False,
) -> Tuple[List[np.ndarray], List[np.ndarray], List[float]]:
    model.eval()
    if measure_per_graph_latency:
        node_rows: List[np.ndarray] = []
        count_rows: List[np.ndarray] = []
        elapsed_rows: List[float] = []
        for sample in samples:
            synchronize(device)
            started = time.perf_counter()
            batch = collate_graphs(
                [sample], center, scale, device=device, max_extra=max_extra
            )
            with torch.no_grad():
                node_logits, count_logits = model(batch)
            synchronize(device)
            elapsed_rows.append(time.perf_counter() - started)
            node_rows.append(node_logits.detach().cpu().numpy().copy())
            count_rows.append(count_logits[0].detach().cpu().numpy().copy())
        return node_rows, count_rows, elapsed_rows

    batch = collate_graphs(samples, center, scale, device=device, max_extra=max_extra)
    synchronize(device)
    started = time.perf_counter()
    with torch.no_grad():
        node_logits, count_logits = model(batch)
    synchronize(device)
    elapsed = time.perf_counter() - started
    node = node_logits.detach().cpu().numpy()
    count = count_logits.detach().cpu().numpy()
    node_rows = [node[start:stop].copy() for start, stop in batch.graph_slices]
    count_rows = [count[index].copy() for index in range(len(samples))]
    return node_rows, count_rows, [elapsed / max(1, len(samples))] * len(samples)


def choose_inference_device(
    model: BoundaryHeatmapGNN,
    samples: Sequence[GraphBoundarySample],
    center: np.ndarray,
    scale: np.ndarray,
    max_extra: int,
    requested: str,
) -> Tuple[torch.device, Dict[str, float]]:
    if requested != "auto":
        if requested == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA inference was requested but CUDA is unavailable.")
        return torch.device(requested), {}

    candidates = [torch.device("cpu")]
    if torch.cuda.is_available():
        candidates.append(torch.device("cuda"))
    probe_samples = list(samples[: min(24, len(samples))])
    timings: Dict[str, float] = {}
    for candidate in candidates:
        probe_model = copy.deepcopy(model).to(candidate)
        model_outputs(
            probe_model,
            probe_samples[: min(2, len(probe_samples))],
            center,
            scale,
            device=candidate,
            max_extra=max_extra,
            measure_per_graph_latency=True,
        )
        _nodes, _counts, elapsed = model_outputs(
            probe_model,
            probe_samples,
            center,
            scale,
            device=candidate,
            max_extra=max_extra,
            measure_per_graph_latency=True,
        )
        timings[str(candidate)] = median(elapsed)
        del probe_model
        if candidate.type == "cuda":
            torch.cuda.empty_cache()
    selected = min(candidates, key=lambda candidate: (timings[str(candidate)], str(candidate)))
    return selected, timings


def validation_score(
    model: BoundaryHeatmapGNN,
    samples: Sequence[GraphBoundarySample],
    center: np.ndarray,
    scale: np.ndarray,
    device: torch.device,
    max_extra: int,
) -> Tuple[float, Dict[str, float]]:
    if not samples:
        return float("-inf"), {}
    node_rows, count_rows, _elapsed = model_outputs(
        model, samples, center, scale, device=device, max_extra=max_extra
    )
    rows = []
    for sample, node_logits, count_logits in zip(samples, node_rows, count_rows):
        prediction = select_boundary(sample, node_logits, count_logits)
        rows.append(boundary_metrics(sample, prediction["boundary"]))
    metrics = {
        "boundary_jaccard": mean(float(row["boundary_jaccard"]) for row in rows),
        "extra_jaccard": mean(float(row["extra_jaccard"]) for row in rows),
        "exact_boundary_rate": mean(1.0 if row["exact_boundary_match"] else 0.0 for row in rows),
        "count_accuracy": mean(1.0 if row["count_match"] else 0.0 for row in rows),
        "top_set_hit_rate": mean(1.0 if row["top_set_hit"] else 0.0 for row in rows),
        "mean_top_set_regret": mean(float(row["top_set_regret"]) for row in rows),
    }
    score = (
        metrics["boundary_jaccard"]
        + 0.25 * metrics["extra_jaccard"]
        + 0.10 * metrics["exact_boundary_rate"]
        + 0.05 * metrics["count_accuracy"]
        + 0.25 * metrics["top_set_hit_rate"]
        - 0.10 * metrics["mean_top_set_regret"]
    )
    return score, metrics


def train_one_model(
    training_seed: int,
    train_samples: Sequence[GraphBoundarySample],
    validation_samples: Sequence[GraphBoundarySample],
    center: np.ndarray,
    scale: np.ndarray,
    device: torch.device,
    positive_weight: float,
    args: argparse.Namespace,
) -> Tuple[BoundaryHeatmapGNN, List[Dict[str, object]], Dict[str, object]]:
    random.seed(training_seed)
    np.random.seed(training_seed)
    torch.manual_seed(training_seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(training_seed)
    model = BoundaryHeatmapGNN(
        input_dim=len(NODE_FEATURE_NAMES),
        hidden_dim=args.hidden_dim,
        num_layers=args.num_layers,
        dropout=args.dropout,
        max_extra=args.max_extra,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    rng = random.Random(training_seed)
    best_score = float("-inf")
    best_epoch = 0
    best_state = copy.deepcopy(model.state_dict())
    history: List[Dict[str, object]] = []
    stale = 0
    started = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        model.train()
        losses: List[Dict[str, float]] = []
        for graph_batch in batches(train_samples, args.batch_size, rng):
            batch = collate_graphs(
                graph_batch,
                center,
                scale,
                device=device,
                max_extra=args.max_extra,
            )
            optimizer.zero_grad(set_to_none=True)
            node_logits, count_logits = model(batch)
            loss, parts = teacher_student_loss(
                node_logits,
                count_logits,
                batch,
                positive_weight=positive_weight,
                ranking_weight=args.ranking_weight,
                count_weight=args.count_weight,
                score_weight=args.score_weight,
                score_temperature=args.score_temperature,
                ranking_margin=args.ranking_margin,
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.gradient_clip)
            optimizer.step()
            losses.append(parts)
        validation, validation_metrics = validation_score(
            model,
            validation_samples,
            center,
            scale,
            device=device,
            max_extra=args.max_extra,
        )
        row: Dict[str, object] = {
            "training_seed": training_seed,
            "epoch": epoch,
            "validation_score": validation,
            **{f"train_{name}": mean(loss[name] for loss in losses) for name in losses[0]},
            **{f"validation_{name}": value for name, value in validation_metrics.items()},
        }
        history.append(row)
        if validation > best_score + args.minimum_improvement:
            best_score = validation
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1
        if stale >= args.patience:
            break
    model.load_state_dict(best_state)
    return model, history, {
        "training_seed": training_seed,
        "best_epoch": best_epoch,
        "best_validation_score": best_score,
        "epochs_run": len(history),
        "training_time_sec": time.perf_counter() - started,
    }


def evaluate_models(
    models: Sequence[Tuple[int, BoundaryHeatmapGNN]],
    samples: Sequence[GraphBoundarySample],
    center: np.ndarray,
    scale: np.ndarray,
    device: torch.device,
    args: argparse.Namespace,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    per_model_outputs: Dict[
        int, Tuple[List[np.ndarray], List[np.ndarray], List[float]]
    ] = {}
    for seed, model in models:
        per_model_outputs[seed] = model_outputs(
            model,
            samples,
            center,
            scale,
            device=device,
            max_extra=args.max_extra,
            measure_per_graph_latency=True,
        )
    rows: List[Dict[str, object]] = []
    for sample_index, sample in enumerate(samples):
        ensemble_nodes = []
        ensemble_counts = []
        seed_selected_states: List[Tuple[int, ...]] = []
        forward_time = 0.0
        for seed, _model in models:
            node_rows, count_rows, elapsed_rows = per_model_outputs[seed]
            node_logits = node_rows[sample_index]
            count_logits = count_rows[sample_index]
            ensemble_nodes.append(node_logits)
            ensemble_counts.append(count_logits)
            forward_time += elapsed_rows[sample_index]
            prediction = select_boundary(sample, node_logits, count_logits)
            seed_selected_states.append(tuple(int(state) for state in prediction["selected_states"]))
            metrics = boundary_metrics(sample, prediction["boundary"])
            rows.append(
                prediction_row(
                    sample,
                    method=f"gnn_seed_{seed}",
                    prediction=prediction,
                    metrics=metrics,
                    forward_time_sec=elapsed_rows[sample_index],
                )
            )
        mean_nodes = np.mean(np.stack(ensemble_nodes, axis=0), axis=0)
        std_nodes = np.std(np.stack(ensemble_nodes, axis=0), axis=0)
        mean_counts = np.mean(np.stack(ensemble_counts, axis=0), axis=0)
        agreement_counts: Dict[Tuple[int, ...], int] = {}
        for selected_states in seed_selected_states:
            agreement_counts[selected_states] = agreement_counts.get(selected_states, 0) + 1
        ensemble_agreement = max(agreement_counts.values(), default=0) / max(1, len(models))
        for method, forced_count in (
            ("gnn_ensemble", None),
            ("gnn_ensemble_top1", 1),
            ("gnn_ensemble_top2", 2),
            ("gnn_ensemble_top3", 3),
        ):
            prediction = select_boundary(
                sample, mean_nodes, mean_counts, forced_count=forced_count
            )
            metrics = boundary_metrics(sample, prediction["boundary"])
            rows.append(
                prediction_row(
                    sample,
                    method=method,
                    prediction=prediction,
                    metrics=metrics,
                    forward_time_sec=forward_time,
                    diagnostics={
                        "ensemble_top_state_agreement": ensemble_agreement,
                        "ensemble_max_node_logit_std": float(np.max(std_nodes, initial=0.0)),
                        "ensemble_selected_logit_std": max(
                            (
                                float(std_nodes[int(state)])
                                for state in prediction["selected_states"]
                            ),
                            default=0.0,
                        ),
                    },
                )
            )
        feature_index = {name: index for index, name in enumerate(NODE_FEATURE_NAMES)}
        from_start = sample.node_features[:, feature_index["distance_from_start"]]
        to_goal = sample.node_features[:, feature_index["distance_to_goal"]]
        articulation = sample.node_features[:, feature_index["articulation"]]
        degree = sample.node_features[:, feature_index["out_degree"]]
        stable_seed = (
            sum((index + 1) * ord(char) for index, char in enumerate(sample.name))
            + int(round(1000.0 * sample.slip))
        )
        rng = np.random.default_rng(stable_seed)
        count_logits = np.full(args.max_extra + 1, -1.0, dtype=float)
        count_logits[1] = 1.0
        heuristic_builders = {
            "baseline_nearest_start": lambda: -from_start,
            "baseline_midpoint": lambda: -np.abs(from_start - to_goal) + 0.1 * articulation,
            "baseline_topology": lambda: 2.0 * articulation + degree,
            "baseline_random": lambda: rng.standard_normal(sample.n_states),
        }
        for method, build_scores in heuristic_builders.items():
            started = time.perf_counter()
            scores = build_scores()
            prediction = select_boundary(sample, scores, count_logits, forced_count=1)
            elapsed = time.perf_counter() - started
            rows.append(
                prediction_row(
                    sample,
                    method=method,
                    prediction=prediction,
                    metrics=boundary_metrics(sample, prediction["boundary"]),
                    forward_time_sec=elapsed,
                )
            )
    learned_methods = [f"gnn_seed_{seed}" for seed, _model in models] + [
        "gnn_ensemble",
        "gnn_ensemble_top1",
    ]
    validation_rows = [
        row
        for row in rows
        if row["split"] == "validation"
        and row["method"] in learned_methods
        and parse_bool(row["teacher_feasible"])
    ]
    method_scores = {
        method: mean(
            float(row["boundary_jaccard"])
            for row in validation_rows
            if row["method"] == method
        )
        for method in learned_methods
    }
    selected_method = max(method_scores, key=lambda method: (method_scores[method], method))
    return rows, {
        "selected_student_method": selected_method,
        "validation_boundary_jaccard_by_method": method_scores,
    }


def prediction_row(
    sample: GraphBoundarySample,
    method: str,
    prediction: Mapping[str, object],
    metrics: Mapping[str, object],
    forward_time_sec: float,
    diagnostics: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    boundary = tuple(int(state) for state in prediction["boundary"])  # type: ignore[union-attr]
    return {
        "split": sample.split,
        "method": method,
        "map_family": sample.map_family,
        "map_size": sample.map_size,
        "map": sample.name,
        "maze_seed": sample.maze_seed,
        "topology_seed": sample.teacher_row.get("topology_seed", sample.maze_seed),
        "goal_variant": sample.teacher_row.get("goal_variant", 0),
        "map_rows": sample.teacher_row.get("map_rows", ""),
        "slip": sample.slip,
        "n_states": sample.n_states,
        "teacher_feasible": sample.teacher_feasible,
        "teacher_n_boundary": len(sample.teacher_boundary),
        "teacher_extra_count": len(sample.teacher_extra),
        "predicted_n_boundary": len(boundary),
        "predicted_extra_count": prediction["predicted_extra_count"],
        "teacher_boundary": json.dumps(sample.teacher_boundary),
        "predicted_boundary": json.dumps(boundary),
        "selected_states": json.dumps(prediction["selected_states"]),
        "score_margin": prediction["score_margin"],
        **metrics,
        "graph_encoding_time_sec": sample.graph_encoding_time_sec,
        "gnn_forward_time_sec": forward_time_sec,
        "student_selection_time_sec": sample.graph_encoding_time_sec + forward_time_sec,
        "teacher_selection_time_sec": sample.teacher_selection_time_sec,
        "selection_speedup_vs_teacher": sample.teacher_selection_time_sec
        / max(1e-12, sample.graph_encoding_time_sec + forward_time_sec),
        **dict(diagnostics or {}),
    }


def summarize_predictions(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    summary: List[Dict[str, object]] = []
    nearest = {
        (str(row["split"]), str(row["map"]), f"{float(row['slip']):.12g}"): str(
            row["predicted_boundary"]
        )
        for row in rows
        if row["method"] == "baseline_nearest_start"
    }
    keys = sorted({(str(row["split"]), str(row["method"])) for row in rows})
    for split, method in keys:
        group = [row for row in rows if row["split"] == split and row["method"] == method]
        feasible_teacher = [row for row in group if parse_bool(row["teacher_feasible"])]
        summary.append(
            {
                "split": split,
                "method": method,
                "n_rows": len(group),
                "n_feasible_teacher_rows": len(feasible_teacher),
                "mean_boundary_jaccard": mean(float(row["boundary_jaccard"]) for row in group),
                "mean_extra_jaccard": mean(float(row["extra_jaccard"]) for row in group),
                "mean_extra_recall": mean(float(row["extra_recall"]) for row in group),
                "exact_boundary_rate": mean(
                    1.0 if parse_bool(row["exact_boundary_match"]) else 0.0 for row in group
                ),
                "count_accuracy": mean(1.0 if parse_bool(row["count_match"]) else 0.0 for row in group),
                "top_set_hit_rate": mean(1.0 if parse_bool(row["top_set_hit"]) else 0.0 for row in group),
                "mean_top_set_regret": mean(float(row["top_set_regret"]) for row in group),
                "mean_teacher_top_set_size": mean(
                    float(row["teacher_top_set_size"]) for row in group
                ),
                "teacher_tie_rate": mean(
                    1.0 if int(float(row["teacher_top_set_size"])) > 1 else 0.0
                    for row in group
                ),
                "match_nearest_start_rate": mean(
                    1.0
                    if str(row["predicted_boundary"])
                    == nearest.get(
                        (
                            str(row["split"]),
                            str(row["map"]),
                            f"{float(row['slip']):.12g}",
                        ),
                        "",
                    )
                    else 0.0
                    for row in group
                ),
                "feasible_teacher_mean_boundary_jaccard": mean(
                    float(row["boundary_jaccard"]) for row in feasible_teacher
                ),
                "median_student_selection_time_sec": median(
                    float(row["student_selection_time_sec"]) for row in group
                ),
                "median_selection_speedup_vs_teacher": median(
                    float(row["selection_speedup_vs_teacher"]) for row in group
                ),
            }
        )
    return summary


def write_report(
    summary_rows: Sequence[Mapping[str, object]],
    training_rows: Sequence[Mapping[str, object]],
    protocol: Mapping[str, object],
    args: argparse.Namespace,
) -> None:
    columns = [
        "split",
        "method",
        "n_rows",
        "n_feasible_teacher_rows",
        "mean_boundary_jaccard",
        "mean_extra_jaccard",
        "mean_extra_recall",
        "exact_boundary_rate",
        "count_accuracy",
        "top_set_hit_rate",
        "mean_top_set_regret",
        "mean_teacher_top_set_size",
        "teacher_tie_rate",
        "match_nearest_start_rate",
        "feasible_teacher_mean_boundary_jaccard",
        "median_student_selection_time_sec",
        "median_selection_speedup_vs_teacher",
    ]
    training_columns = [
        "training_seed",
        "best_epoch",
        "best_validation_score",
        "epochs_run",
        "training_time_sec",
    ]
    lines = [
        "# Transition-Graph GNN Boundary Heatmap",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "The group-constrained RD selector is the offline teacher. The student receives only the finite transition graph, candidate mask, start/goal/reward/transition features, and global slip/discount values. It emits one node heatmap and one graph-level extra-vertex count. Mandatory endpoints are inserted exactly, and no teacher score, candidate insertion, beam expansion, or Green recomputation is available to the student.",
        "",
        f"split mode = `{args.split_mode}`. Splits are assigned at the base-topology level, never by individual slip row. Teacher mode uses complete larger-scale holdouts; hybrid mode holds out maze topology seeds and retains deterministic-family scale holdouts.",
        "",
        f"training device = `{protocol.get('training_device')}`, inference device = `{protocol.get('inference_device')}`, selected validation mode = `{protocol.get('selected_student_method')}`",
        "",
        "## Prediction Summary",
        "",
        markdown_table(summary_rows, columns),
        "",
        "## Training Runs",
        "",
        markdown_table(training_rows, training_columns),
        "",
        "The selection speedup charges graph encoding, candidate-mask construction, and GNN forward time, but not the subsequent group audit or final graph-kernel construction. Those are evaluated separately by the downstream audit.",
        "",
        f"Teacher source: `{args.teacher_csv}`",
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a transition-graph GNN to imitate RD boundary graphs.")
    parser.add_argument(
        "--teacher-csv",
        type=Path,
        default=Path("experiments/output/random_maze_generalization/random_maze_generalization.csv"),
    )
    parser.add_argument(
        "--heatmap-teacher-csv",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_teacher/boundary_heatmap_teacher.csv"),
    )
    parser.add_argument("--teacher-method", default="group_constrained_incremental")
    parser.add_argument(
        "--split-mode",
        choices=["teacher", "hybrid_topology_scale"],
        default="teacher",
        help="Use teacher scale holdouts or hold out maze topologies while retaining deterministic-family scale holdouts.",
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument(
        "--candidate-universe",
        choices=["all", "teacher_basis"],
        default="all",
        help="all exposes every nonmandatory state; teacher_basis restricts deployment to the teacher vocabulary.",
    )
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument(
        "--fixed-random-count",
        type=int,
        default=0,
        help="Keep zero for the observable graph-only protocol; nonzero values reproduce the legacy hidden-basis ablation.",
    )
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--include-infeasible-teachers", action="store_true")
    parser.add_argument("--training-seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--max-extra", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--patience", type=int, default=25)
    parser.add_argument("--minimum-improvement", type=float, default=1e-5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=3e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--ranking-weight", type=float, default=1.0)
    parser.add_argument("--ranking-margin", type=float, default=1.0)
    parser.add_argument("--count-weight", type=float, default=0.35)
    parser.add_argument("--score-weight", type=float, default=1.0)
    parser.add_argument("--score-temperature", type=float, default=0.12)
    parser.add_argument("--positive-weight-cap", type=float, default=80.0)
    parser.add_argument("--gradient-clip", type=float, default=5.0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument(
        "--inference-device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Deployment device; auto benchmarks per-graph CPU and CUDA latency on validation graphs.",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("experiments/models/boundary_heatmap_gnn"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_gnn"),
    )
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false.")
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = False

    teacher_rows = load_teacher_rows(args.teacher_csv, args.teacher_method)
    heatmaps = load_heatmap_rows(args.heatmap_teacher_csv)
    samples = [build_sample(row, args, heatmaps) for row in teacher_rows]
    if len(samples) != len(teacher_rows):
        raise AssertionError("Every teacher row must produce exactly one graph sample.")
    train_all = [sample for sample in samples if sample.split == "train"]
    validation_all = [sample for sample in samples if sample.split == "validation"]
    train_samples = [
        sample
        for sample in train_all
        if args.include_infeasible_teachers or sample.teacher_feasible
    ]
    validation_samples = [sample for sample in validation_all if sample.teacher_feasible]
    if not train_samples or not validation_samples:
        raise ValueError("The split protocol produced an empty train or validation set.")
    center, scale = feature_normalization(train_samples)
    positives = sum(int(np.sum(sample.labels[sample.eligible])) for sample in train_samples)
    negatives = sum(int(np.sum(sample.eligible)) for sample in train_samples) - positives
    positive_weight = min(args.positive_weight_cap, negatives / max(1, positives))

    trained: List[Tuple[int, BoundaryHeatmapGNN]] = []
    history_rows: List[Dict[str, object]] = []
    training_rows: List[Dict[str, object]] = []
    key_maps: Dict[str, Dict[str, str]] = {}
    args.model_dir.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for training_seed in args.training_seeds:
        model, history, training = train_one_model(
            training_seed,
            train_samples,
            validation_samples,
            center,
            scale,
            device=device,
            positive_weight=positive_weight,
            args=args,
        )
        trained.append((training_seed, model))
        history_rows.extend(history)
        training_rows.append(training)
        weight_name = f"boundary_heatmap_seed{training_seed}.npz"
        key_maps[weight_name] = state_dict_to_npz(model, args.model_dir / weight_name)

    inference_device, inference_benchmark = choose_inference_device(
        trained[0][1],
        validation_samples,
        center,
        scale,
        max_extra=args.max_extra,
        requested=args.inference_device,
    )
    for _seed, model in trained:
        model.to(inference_device)
    prediction_rows, selection_protocol = evaluate_models(
        trained,
        samples,
        center,
        scale,
        device=inference_device,
        args=args,
    )
    summary_rows = summarize_predictions(prediction_rows)
    total_training_time = sum(float(row["training_time_sec"]) for row in training_rows)
    teacher_label_time = sum(sample.teacher_selection_time_sec for sample in train_samples)
    selected_method = str(selection_protocol["selected_student_method"])
    selected_test = [
        row
        for row in prediction_rows
        if row["split"] == "test" and row["method"] == selected_method
    ]
    saved_per_context = median(
        max(0.0, float(row["teacher_selection_time_sec"]) - float(row["student_selection_time_sec"]))
        for row in selected_test
    )
    protocol: Dict[str, object] = {
        **selection_protocol,
        "training_device": str(device),
        "inference_device": str(inference_device),
        "inference_device_benchmark_sec": inference_benchmark,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "n_teacher_rows": len(samples),
        "n_heatmap_contexts": len(heatmaps),
        "n_train_rows": len(train_all),
        "n_train_rows_used": len(train_samples),
        "n_validation_rows": len(validation_all),
        "n_test_rows": sum(1 for sample in samples if sample.split == "test"),
        "positive_weight": positive_weight,
        "teacher_label_selection_time_sec": teacher_label_time,
        "gnn_training_time_sec": total_training_time,
        "training_only_break_even_contexts": math.ceil(total_training_time / max(1e-12, saved_per_context)),
        "teacher_plus_training_break_even_contexts": math.ceil(
            (teacher_label_time + total_training_time) / max(1e-12, saved_per_context)
        ),
        "feature_names": list(NODE_FEATURE_NAMES),
        "feature_center": center.tolist(),
        "feature_scale": scale.tolist(),
        "model_config": trained[0][1].config(),
        "weight_key_maps": key_maps,
        "fixed_basis_kinds": args.fixed_basis_kinds,
        "candidate_universe": args.candidate_universe,
        "inference_timing": "single_graph_including_collation_and_device_transfer",
        "split_mode": args.split_mode,
        "probe_top_fraction": args.probe_top_fraction,
        "fixed_random_count": args.fixed_random_count,
    }
    write_csv_all_fields(args.out_dir / "predictions.csv", prediction_rows)
    write_csv_all_fields(args.out_dir / "prediction_summary.csv", summary_rows)
    write_csv_all_fields(args.out_dir / "training_history.csv", history_rows)
    write_csv_all_fields(args.out_dir / "training_runs.csv", training_rows)
    (args.out_dir / "protocol.json").write_text(
        json.dumps(protocol, indent=2, default=json_default, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary_rows, training_rows, protocol, args)

    # The scheduler snapshot excludes experiments/output. Publish only the
    # selected test predictions and metadata next to the compact model weights.
    deploy_rows = [
        row
        for row in prediction_rows
        if row["split"] == "test" and row["method"] == selected_method
    ]
    write_csv_all_fields(args.model_dir / "selected_test_predictions.csv", deploy_rows)
    write_csv_all_fields(
        args.model_dir / "selected_validation_predictions.csv",
        [
            row
            for row in prediction_rows
            if row["split"] == "validation" and row["method"] == selected_method
        ],
    )
    write_csv_all_fields(
        args.model_dir / "ensemble_test_predictions.csv",
        [
            row
            for row in prediction_rows
            if row["split"] == "test" and row["method"] == "gnn_ensemble"
        ],
    )
    write_csv_all_fields(
        args.model_dir / "ensemble_validation_predictions.csv",
        [
            row
            for row in prediction_rows
            if row["split"] == "validation" and row["method"] == "gnn_ensemble"
        ],
    )
    write_csv_all_fields(
        args.model_dir / "test_frontier_predictions.csv",
        [
            row
            for row in prediction_rows
            if row["split"] == "test"
            and row["method"] in {
                "gnn_ensemble_top1",
                "gnn_ensemble_top2",
                "gnn_ensemble_top3",
            }
        ],
    )
    write_csv_all_fields(
        args.model_dir / "test_baseline_predictions.csv",
        [
            row
            for row in prediction_rows
            if row["split"] == "test"
            and row["method"] in {"baseline_nearest_start", "baseline_topology"}
        ],
    )
    write_csv_all_fields(
        args.model_dir / "validation_baseline_predictions.csv",
        [
            row
            for row in prediction_rows
            if row["split"] == "validation"
            and row["method"] in {"baseline_nearest_start", "baseline_topology"}
        ],
    )
    write_csv_all_fields(
        args.model_dir / "selected_test_teacher.csv",
        [dict(sample.teacher_row) for sample in samples if sample.split == "test"],
    )
    write_csv_all_fields(
        args.model_dir / "selected_validation_teacher.csv",
        [dict(sample.teacher_row) for sample in samples if sample.split == "validation"],
    )
    (args.model_dir / "protocol.json").write_text(
        json.dumps(protocol, indent=2, default=json_default, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(protocol, indent=2, default=json_default, sort_keys=True))


if __name__ == "__main__":
    main()
