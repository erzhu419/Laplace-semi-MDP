#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import scaled_rows
from learned_green_horizon import (
    HORIZON_FEATURE_NAMES,
    ConservativeHorizonRegressor,
    feature_vector,
    graph_horizon_features,
)
from one_shot_rd_operator import OneShotRDResult, apply_one_shot_rd_operator
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import write_csv_all_fields


Context = Tuple[str, int, int, str, Tuple[str, ...], float]


def finite(values: Iterable[float]) -> List[float]:
    return [float(value) for value in values if math.isfinite(float(value))]


def median(values: Iterable[float]) -> float:
    clean = finite(values)
    return float(statistics.median(clean)) if clean else float("nan")


def mean(values: Iterable[float]) -> float:
    clean = finite(values)
    return float(statistics.fmean(clean)) if clean else float("nan")


def quantile(values: Iterable[float], level: float) -> float:
    clean = sorted(finite(values))
    if not clean:
        return float("nan")
    index = min(len(clean) - 1, max(0, int(math.ceil(level * len(clean)) - 1)))
    return float(clean[index])


def jaccard(left: Sequence[int], right: Sequence[int]) -> float:
    left_set = set(int(state) for state in left)
    right_set = set(int(state) for state in right)
    return len(left_set.intersection(right_set)) / max(1, len(left_set.union(right_set)))


def expand_contexts(
    split: str,
    map_specs: Sequence[str],
    maze_seeds: Sequence[int],
    slips: Sequence[float],
) -> List[Context]:
    contexts: List[Context] = []
    for spec in map_specs:
        family, raw_sizes = spec.split(":", 1)
        for raw_size in raw_sizes.split(","):
            size = int(raw_size)
            seeds = maze_seeds if family == "maze" else [0]
            for seed in seeds:
                label = f"{family}_{size}"
                if family == "maze":
                    label += f"_seed{int(seed)}"
                rows = scaled_rows(family, size, seed=int(seed))
                for slip in slips:
                    contexts.append((family, size, int(seed), label, rows, float(slip)))
    return contexts


def operator_kwargs(grid: GridWorld, slip: float, args: argparse.Namespace) -> Dict[str, object]:
    return {
        "grid": grid,
        "slip": float(slip),
        "gamma": args.gamma,
        "mandatory_boundary": endpoint_boundary_states(grid),
        "probe_count": args.probe_count,
        "tail_tol": args.tail_tol,
        "max_splits": args.max_splits,
        "channel_threshold": args.channel_threshold,
        "min_channel_support": args.min_channel_support,
        "mandatory_exclusion_radius": args.mandatory_exclusion_radius,
        "candidate_universe": args.candidate_universe,
    }


def collect_labels(
    split: str,
    contexts: Sequence[Context],
    args: argparse.Namespace,
) -> Tuple[List[Dict[str, object]], Dict[Tuple[str, float], OneShotRDResult]]:
    rows: List[Dict[str, object]] = []
    references: Dict[Tuple[str, float], OneShotRDResult] = {}
    for family, size, seed, label, map_rows, slip in contexts:
        grid = GridWorld(map_rows)
        features = graph_horizon_features(
            grid,
            slip=slip,
            gamma=args.gamma,
            mandatory_boundary=endpoint_boundary_states(grid),
        )
        started = time.perf_counter()
        result = apply_one_shot_rd_operator(
            **operator_kwargs(grid, slip, args),
            truncation_steps=args.max_horizon,
        )
        elapsed = time.perf_counter() - started
        frontier = float(result.diagnostics["frontier_max"])
        certified = frontier <= args.tail_tol
        row: Dict[str, object] = {
            "split": split,
            "map_family": family,
            "map_size": int(size),
            "maze_seed": int(seed),
            "map": label,
            "slip": float(slip),
            "n_states": grid.n_states,
            **features,
            "required_k": int(result.diagnostics["used_steps_max"]),
            "reference_frontier": frontier,
            "reference_certified": certified,
            "reference_operator_time_sec": elapsed,
            "green_steps_total": int(result.diagnostics["green_steps_total"]),
            "occupancy_steps_total": int(result.diagnostics["occupancy_steps_total"]),
            "reference_boundary": json.dumps(result.boundary),
        }
        rows.append(row)
        references[(label, float(slip))] = result
    return rows, references


def matrix(rows: Sequence[Mapping[str, object]]) -> Tuple[np.ndarray, np.ndarray]:
    usable = [
        row
        for row in rows
        if bool(row["reference_certified"])
        and int(row["required_k"]) > 0
        and float(row["turn_articulation_fraction"]) > 0.0
    ]
    return (
        np.stack(
            [feature_vector({name: float(row[name]) for name in HORIZON_FEATURE_NAMES}) for row in usable],
            axis=0,
        ),
        np.asarray([float(row["required_k"]) for row in usable], dtype=float),
    )


def add_predictions(
    rows: Sequence[Dict[str, object]],
    model: ConservativeHorizonRegressor,
) -> None:
    for row in rows:
        features = {name: float(row[name]) for name in HORIZON_FEATURE_NAMES}
        base_k = model.predict(features, conservative=False)
        proposed_k = model.predict(features, conservative=True)
        required_k = int(row["required_k"])
        row.update(
            {
                "base_predicted_k": base_k,
                "proposed_k": proposed_k,
                "base_error": base_k - required_k,
                "proposal_error": proposed_k - required_k,
                "proposal_first_pass_certified": proposed_k >= required_k,
                "continuation_steps_if_needed": max(0, required_k - proposed_k),
                "proposal_excess_steps": max(0, proposed_k - required_k),
                "proposal_to_fixed_work_ratio": proposed_k / max(1, model.max_steps),
            }
        )


def retry_with_certificate(
    grid: GridWorld,
    slip: float,
    proposed_k: int,
    args: argparse.Namespace,
) -> Tuple[OneShotRDResult, int, int, float, bool, OneShotRDResult]:
    limit = min(args.max_horizon, max(0, int(proposed_k)))
    attempts = 0
    elapsed = 0.0
    first_result: OneShotRDResult | None = None
    while True:
        started = time.perf_counter()
        result = apply_one_shot_rd_operator(
            **operator_kwargs(grid, slip, args),
            truncation_steps=limit,
        )
        elapsed += time.perf_counter() - started
        attempts += 1
        if first_result is None:
            first_result = result
        certified = float(result.diagnostics["frontier_max"]) <= args.tail_tol
        if certified or limit >= args.max_horizon:
            return result, limit, attempts, elapsed, certified, first_result
        limit = min(
            args.max_horizon,
            max(limit + 1, args.minimum_retry_horizon, int(math.ceil(limit * args.retry_growth))),
        )


def execute_test_rows(
    rows: Sequence[Dict[str, object]],
    references: Mapping[Tuple[str, float], OneShotRDResult],
    model: ConservativeHorizonRegressor,
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    execution: List[Dict[str, object]] = []
    for row in rows:
        family = str(row["map_family"])
        size = int(row["map_size"])
        seed = int(row["maze_seed"])
        label = str(row["map"])
        slip = float(row["slip"])
        grid = GridWorld(scaled_rows(family, size, seed=seed))
        reference = references[(label, slip)]

        proposal_started = time.perf_counter()
        inference_features = graph_horizon_features(
            grid,
            slip=slip,
            gamma=args.gamma,
            mandatory_boundary=endpoint_boundary_states(grid),
        )
        inferred_k = model.predict(inference_features, conservative=True)
        proposal_time = time.perf_counter() - proposal_started
        if inferred_k != int(row["proposed_k"]):
            raise AssertionError("Serialized feature prediction changed during execution audit.")

        fixed_started = time.perf_counter()
        fixed = apply_one_shot_rd_operator(
            **{**operator_kwargs(grid, slip, args), "tail_tol": 0.0},
            truncation_steps=args.fixed_horizon,
        )
        fixed_time = time.perf_counter() - fixed_started

        corrected, final_k, attempts, learned_time, certified, first = retry_with_certificate(
            grid,
            slip=slip,
            proposed_k=int(row["proposed_k"]),
            args=args,
        )
        learned_total_time = proposal_time + learned_time
        execution.append(
            {
                "map": label,
                "map_family": family,
                "map_size": size,
                "maze_seed": seed,
                "slip": slip,
                "n_states": grid.n_states,
                "required_k": int(row["required_k"]),
                "proposed_k": int(row["proposed_k"]),
                "learned_final_k": final_k,
                "learned_attempts": attempts,
                "learned_certified": certified,
                "proposal_inference_time_sec": proposal_time,
                "fixed_operator_time_sec": fixed_time,
                "adaptive_operator_time_sec": float(row["reference_operator_time_sec"]),
                "learned_operator_time_sec": learned_time,
                "learned_total_time_sec": learned_total_time,
                "learned_speedup_vs_fixed": fixed_time / max(1e-12, learned_total_time),
                "learned_speedup_vs_adaptive": float(row["reference_operator_time_sec"])
                / max(1e-12, learned_total_time),
                "fixed_boundary_jaccard": jaccard(reference.boundary, fixed.boundary),
                "proposal_boundary_jaccard": jaccard(reference.boundary, first.boundary),
                "corrected_boundary_jaccard": jaccard(reference.boundary, corrected.boundary),
                "proposal_frontier": float(first.diagnostics["frontier_max"]),
                "corrected_frontier": float(corrected.diagnostics["frontier_max"]),
            }
        )
    return execution


def prediction_summary(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for split in ("train", "calibration", "test"):
        group = [row for row in rows if row["split"] == split]
        nontrivial = [row for row in group if int(row["required_k"]) > 0]
        out.append(
            {
                "split": split,
                "n_rows": len(group),
                "n_nontrivial": len(nontrivial),
                "median_required_k": median(float(row["required_k"]) for row in nontrivial),
                "median_proposed_k": median(float(row["proposed_k"]) for row in nontrivial),
                "base_mae": mean(abs(float(row["base_error"])) for row in nontrivial),
                "proposal_mae": mean(abs(float(row["proposal_error"])) for row in nontrivial),
                "proposal_coverage": mean(
                    1.0 if bool(row["proposal_first_pass_certified"]) else 0.0
                    for row in nontrivial
                ),
                "median_excess_steps": median(
                    float(row["proposal_excess_steps"]) for row in nontrivial
                ),
                "p95_excess_steps": quantile(
                    (float(row["proposal_excess_steps"]) for row in nontrivial), 0.95
                ),
                "median_continuation_steps": median(
                    float(row["continuation_steps_if_needed"]) for row in nontrivial
                ),
            }
        )
    return out


def execution_summary(rows: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    return {
        "n_test_rows": len(rows),
        "proposal_first_pass_rate": mean(
            1.0 if int(row["learned_attempts"]) == 1 else 0.0 for row in rows
        ),
        "final_certificate_rate": mean(1.0 if bool(row["learned_certified"]) else 0.0 for row in rows),
        "median_fixed_time_sec": median(float(row["fixed_operator_time_sec"]) for row in rows),
        "median_adaptive_time_sec": median(float(row["adaptive_operator_time_sec"]) for row in rows),
        "median_learned_time_sec": median(float(row["learned_total_time_sec"]) for row in rows),
        "median_learned_speedup_vs_fixed": median(
            float(row["learned_speedup_vs_fixed"]) for row in rows
        ),
        "median_learned_speedup_vs_adaptive": median(
            float(row["learned_speedup_vs_adaptive"]) for row in rows
        ),
        "min_proposal_boundary_jaccard": min(
            (float(row["proposal_boundary_jaccard"]) for row in rows), default=float("nan")
        ),
        "min_corrected_boundary_jaccard": min(
            (float(row["corrected_boundary_jaccard"]) for row in rows), default=float("nan")
        ),
    }


def write_report(
    prediction_rows: Sequence[Mapping[str, object]],
    execution_rows: Sequence[Mapping[str, object]],
    model: ConservativeHorizonRegressor,
    args: argparse.Namespace,
) -> None:
    prediction = prediction_summary(prediction_rows)
    execution = execution_summary(execution_rows)
    prediction_columns = [
        "split",
        "n_rows",
        "n_nontrivial",
        "median_required_k",
        "median_proposed_k",
        "base_mae",
        "proposal_mae",
        "proposal_coverage",
        "median_excess_steps",
        "p95_excess_steps",
        "median_continuation_steps",
    ]
    execution_columns = list(execution)
    detail_columns = [
        "map",
        "slip",
        "required_k",
        "proposed_k",
        "learned_final_k",
        "learned_attempts",
        "learned_certified",
        "learned_speedup_vs_fixed",
        "learned_speedup_vs_adaptive",
        "proposal_boundary_jaccard",
        "corrected_boundary_jaccard",
    ]
    lines = [
        "# Trainable Green Horizon Pilot",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This pilot asks whether the truncation horizon can be amortized from one graph-level observation. A NumPy ridge model predicts K from transition-graph summaries; a split-conformal upper residual makes the proposal conservative. The proposal never replaces the frontier certificate: failed proposals grow geometrically and are re-audited.",
        "",
        f"target coverage = {args.coverage}, learned upper residual = {model.upper_residual:.6g}, tail tolerance = {args.tail_tol:g}",
        "",
        "## Prediction",
        "",
        markdown_table(prediction, prediction_columns),
        "",
        "## Execution",
        "",
        markdown_table([execution], execution_columns),
        "",
        "The fixed baseline deliberately executes every term through fixed K with no early stopping. The adaptive baseline is the current production behavior and checks the frontier every step. The learned implementation is a correctness-first prototype that restarts after an underprediction; a continuation implementation would remove that retry overhead.",
        "",
        "## Held-Out Rows",
        "",
        markdown_table(
            [{column: row.get(column, "") for column in detail_columns} for row in execution_rows],
            detail_columns,
        ),
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and audit a graph-conditioned Green horizon proposal.")
    parser.add_argument(
        "--train-map-specs",
        nargs="+",
        default=[
            "corridor:32,64,128",
            "open_room:8,10,12,16",
            "four_rooms:9,11,13,15",
            "maze:9,11,13,15",
        ],
    )
    parser.add_argument(
        "--calibration-map-specs",
        nargs="+",
        default=["corridor:192", "open_room:18", "four_rooms:17", "maze:17"],
    )
    parser.add_argument(
        "--test-map-specs",
        nargs="+",
        default=[
            "corridor:256,512",
            "open_room:20,24,32",
            "four_rooms:19,21,31",
            "maze:19,21,25",
        ],
    )
    parser.add_argument("--train-maze-seeds", type=int, nargs="+", default=list(range(6)))
    parser.add_argument("--calibration-maze-seeds", type=int, nargs="+", default=[6, 7])
    parser.add_argument("--test-maze-seeds", type=int, nargs="+", default=[8, 9, 10, 11])
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05, 0.1])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--tail-tol", type=float, default=1e-6)
    parser.add_argument("--max-horizon", type=int, default=512)
    parser.add_argument("--fixed-horizon", type=int, default=256)
    parser.add_argument("--coverage", type=float, default=0.95)
    parser.add_argument("--ridge", type=float, default=1e-3)
    parser.add_argument("--retry-growth", type=float, default=2.0)
    parser.add_argument("--minimum-retry-horizon", type=int, default=8)
    parser.add_argument("--probe-count", type=int, default=None)
    parser.add_argument("--channel-threshold", type=float, default=0.15)
    parser.add_argument("--min-channel-support", type=int, default=2)
    parser.add_argument("--mandatory-exclusion-radius", type=int, default=1)
    parser.add_argument("--candidate-universe", choices=["all", "turn_articulation"], default="turn_articulation")
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/learned_green_horizon"),
    )
    args = parser.parse_args()
    if not 0.0 < args.coverage <= 1.0:
        raise ValueError("--coverage must lie in (0, 1].")
    if args.retry_growth <= 1.0:
        raise ValueError("--retry-growth must be greater than one.")

    split_specs = [
        ("train", args.train_map_specs, args.train_maze_seeds),
        ("calibration", args.calibration_map_specs, args.calibration_maze_seeds),
        ("test", args.test_map_specs, args.test_maze_seeds),
    ]
    all_rows: List[Dict[str, object]] = []
    test_references: Dict[Tuple[str, float], OneShotRDResult] = {}
    for split, map_specs, seeds in split_specs:
        contexts = expand_contexts(split, map_specs, seeds, args.slips)
        rows, references = collect_labels(split, contexts, args)
        all_rows.extend(rows)
        if split == "test":
            test_references.update(references)

    train_rows = [row for row in all_rows if row["split"] == "train"]
    calibration_rows = [row for row in all_rows if row["split"] == "calibration"]
    train_x, train_y = matrix(train_rows)
    calibration_x, calibration_y = matrix(calibration_rows)
    model = ConservativeHorizonRegressor.fit(
        train_x,
        train_y,
        calibration_x,
        calibration_y,
        ridge=args.ridge,
        coverage=args.coverage,
        max_steps=args.max_horizon,
    )
    add_predictions(all_rows, model)
    test_rows = [row for row in all_rows if row["split"] == "test"]
    execution_rows = execute_test_rows(test_rows, test_references, model, args)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "horizon_dataset.csv", all_rows)
    write_csv_all_fields(args.out_dir / "held_out_execution.csv", execution_rows)
    (args.out_dir / "model.json").write_text(
        json.dumps(model.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_payload = {
        "prediction": prediction_summary(all_rows),
        "execution": execution_summary(execution_rows),
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(all_rows, execution_rows, model, args)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
