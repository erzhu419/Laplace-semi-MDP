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
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
import torch
from torch.nn import functional as F

from boundary_constraint_student import (
    GROUP_NAMES,
    PROPOSAL_KINDS,
    BoundaryConstraintHead,
    choose_candidate_indices,
    constraint_student_loss,
    positive_class_weights,
    tie_aware_auc,
    topology_holdout_maps,
)
from boundary_heatmap_gnn import (
    BoundaryHeatmapGNN,
    GraphBoundarySample,
    collate_graphs,
    load_state_dict_npz,
    state_dict_to_npz,
)
from run_boundary_heatmap_gnn import (
    build_sample,
    load_heatmap_rows,
    load_teacher_rows,
)
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


ContextKey = Tuple[str, str]
CandidateKey = Tuple[str, str, str]


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def read_rows(path: Path) -> List[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def context_key(row: Mapping[str, object]) -> ContextKey:
    return str(row.get("map")), f"{finite_float(row.get('slip'), 0.0):.12g}"


def candidate_key(row: Mapping[str, object], audit: bool = False) -> CandidateKey:
    method_field = "student_method" if audit else "method"
    return (*context_key(row), str(row.get(method_field, "")))


def median(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(clean)) if clean else float("nan")


def sigmoid(value: np.ndarray) -> np.ndarray:
    clipped = np.clip(value, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def aggregate_hidden(hidden: torch.Tensor, states: Sequence[int]) -> Tuple[torch.Tensor, torch.Tensor]:
    if not states:
        zeros = torch.zeros(hidden.shape[1], dtype=hidden.dtype, device=hidden.device)
        return zeros, zeros
    selected = hidden[torch.as_tensor(sorted(set(states)), dtype=torch.long, device=hidden.device)]
    return torch.mean(selected, dim=0), torch.max(selected, dim=0).values


def candidate_feature_vector(
    sample: GraphBoundarySample,
    row: Mapping[str, object],
    hidden: torch.Tensor,
    pooled: torch.Tensor,
    node_logits: torch.Tensor,
    count_logits: torch.Tensor,
) -> np.ndarray:
    boundary = tuple(sorted(int(state) for state in json.loads(str(row["predicted_boundary"]))))
    mandatory = tuple(sorted(set(sample.mandatory).intersection(boundary)))
    extra = tuple(sorted(set(boundary) - set(sample.mandatory)))
    boundary_mean, boundary_max = aggregate_hidden(hidden, boundary)
    extra_mean, extra_max = aggregate_hidden(hidden, extra)
    mandatory_mean, _mandatory_max = aggregate_hidden(hidden, mandatory)
    eligible = np.flatnonzero(sample.eligible).astype(int)
    unselected = sorted(set(eligible.tolist()) - set(extra))
    selected_logits = node_logits[
        torch.as_tensor(extra, dtype=torch.long, device=node_logits.device)
    ] if extra else torch.empty(0, dtype=node_logits.dtype, device=node_logits.device)
    unselected_logits = node_logits[
        torch.as_tensor(unselected, dtype=torch.long, device=node_logits.device)
    ] if unselected else torch.empty(0, dtype=node_logits.dtype, device=node_logits.device)
    count_probability = F.softmax(count_logits, dim=0)[min(len(extra), len(count_logits) - 1)]
    score_margin = finite_float(row.get("score_margin"), 0.0)
    aliases = set(json.loads(str(row.get("proposal_aliases", "[]"))))
    alias_features = [1.0 if kind in aliases else 0.0 for kind in PROPOSAL_KINDS]
    scalar_features = [
        len(boundary) / max(1, sample.n_states),
        len(extra) / max(1, sample.n_states),
        len(extra) / max(1, len(count_logits) - 1),
        float(sample.slip),
        math.log1p(sample.n_states) / math.log(257.0),
        math.tanh(score_margin if math.isfinite(score_margin) else 20.0),
        float(torch.mean(selected_logits).detach().cpu()) if len(selected_logits) else 0.0,
        float(torch.max(selected_logits).detach().cpu()) if len(selected_logits) else -20.0,
        float(torch.max(unselected_logits).detach().cpu()) if len(unselected_logits) else -20.0,
        float(count_probability.detach().cpu()),
        *alias_features,
    ]
    tensor_features = torch.cat(
        [
            pooled,
            boundary_mean,
            boundary_max,
            extra_mean,
            extra_max,
            mandatory_mean,
        ],
        dim=0,
    ).detach().cpu().numpy()
    return np.concatenate([tensor_features, np.asarray(scalar_features, dtype=np.float32)]).astype(
        np.float32
    )


def load_base_model(model_dir: Path) -> Tuple[BoundaryHeatmapGNN, Dict[str, object]]:
    protocol = json.loads((model_dir / "protocol.json").read_text(encoding="utf-8"))
    selected_method = str(protocol["selected_student_method"])
    if not selected_method.startswith("gnn_seed_"):
        raise ValueError("Constraint-aware reranking requires a validation-selected single base GNN.")
    seed = int(selected_method.rsplit("_", 1)[1])
    weight_name = f"boundary_heatmap_seed{seed}.npz"
    model = BoundaryHeatmapGNN(**protocol["model_config"])
    load_state_dict_npz(model, model_dir / weight_name, protocol["weight_key_maps"][weight_name])
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return model, protocol


def build_samples(
    teacher_csv: Path,
    heatmap_csv: Path,
    protocol: Mapping[str, object],
    gamma: float,
    probe_top_fraction: float,
) -> Dict[ContextKey, GraphBoundarySample]:
    sample_args = argparse.Namespace(
        candidate_universe="all",
        fixed_basis_kinds=protocol["fixed_basis_kinds"],
        gamma=gamma,
        probe_top_fraction=probe_top_fraction,
        fixed_random_count=0,
        split_mode=str(protocol["split_mode"]),
        max_extra=int(protocol["model_config"]["max_extra"]),
    )
    teacher_rows = load_teacher_rows(teacher_csv, "group_constrained_incremental")
    heatmaps = load_heatmap_rows(heatmap_csv)
    return {
        context_key(row): build_sample(row, sample_args, heatmaps)
        for row in teacher_rows
    }


def extract_features(
    candidates: Sequence[Mapping[str, object]],
    samples: Mapping[ContextKey, GraphBoundarySample],
    base_model: BoundaryHeatmapGNN,
    base_protocol: Mapping[str, object],
    device: torch.device,
) -> Tuple[np.ndarray, Dict[ContextKey, float], Dict[ContextKey, float]]:
    grouped: Dict[ContextKey, List[int]] = defaultdict(list)
    for index, row in enumerate(candidates):
        grouped[context_key(row)].append(index)
    features: List[np.ndarray | None] = [None] * len(candidates)
    inference_times: Dict[ContextKey, float] = {}
    graph_times: Dict[ContextKey, float] = {}
    center = np.asarray(base_protocol["feature_center"], dtype=np.float32)
    scale = np.asarray(base_protocol["feature_scale"], dtype=np.float32)
    base_model = base_model.to(device)
    for key in sorted(grouped):
        sample = samples[key]
        graph_times[key] = float(sample.graph_encoding_time_sec)
        started = time.perf_counter()
        batch = collate_graphs(
            [sample],
            center,
            scale,
            device=device,
            max_extra=int(base_protocol["model_config"]["max_extra"]),
        )
        with torch.no_grad():
            hidden, pooled, node_context = base_model.encode(batch)
            node_logits, count_logits = base_model.decode(hidden, pooled, node_context)
            for index in grouped[key]:
                features[index] = candidate_feature_vector(
                    sample,
                    candidates[index],
                    hidden,
                    pooled[0],
                    node_logits,
                    count_logits[0],
                )
        inference_times[key] = time.perf_counter() - started
    if any(feature is None for feature in features):
        raise AssertionError("Missing candidate feature vector.")
    return np.stack(features), inference_times, graph_times  # type: ignore[arg-type]


def join_audits(
    candidates: Sequence[Mapping[str, object]],
    audit_paths: Sequence[Path],
    max_normalized_gap: float,
) -> Tuple[List[Dict[str, object]], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    audit_rows = [row for path in audit_paths for row in read_rows(path)]
    audits = {candidate_key(row, audit=True): row for row in audit_rows}
    if len(audits) != len(audit_rows):
        raise RuntimeError("Candidate downstream audit contains duplicate keys.")
    records: List[Dict[str, object]] = []
    violations = []
    gaps = []
    group_failures = []
    joint_failures = []
    for candidate in candidates:
        key = candidate_key(candidate)
        if key not in audits:
            raise RuntimeError(f"Missing downstream audit for candidate {key}.")
        audit = audits[key]
        if audit.get("error"):
            raise RuntimeError(f"Downstream audit failed for candidate {key}: {audit['error']}")
        predicted = sorted(json.loads(str(candidate["predicted_boundary"])))
        audited = sorted(json.loads(str(audit["student_boundary"])))
        if predicted != audited:
            raise RuntimeError(f"Audited boundary differs from candidate for {key}.")
        group_values = json.loads(str(audit.get("student_group_violations", "{}")))
        margin = np.asarray(
            [max(0.0, finite_float(group_values.get(group), 0.0)) for group in GROUP_NAMES],
            dtype=np.float64,
        )
        gap = abs(finite_float(audit.get("student_normalized_start_gap"), float("inf")))
        group_failure = margin > 1e-12
        joint_failure = bool(np.any(group_failure) or gap > float(max_normalized_gap))
        records.append({**dict(candidate), "audit": audit, "joint_failure": joint_failure})
        violations.append(margin)
        gaps.append(gap)
        group_failures.append(group_failure)
        joint_failures.append(joint_failure)
    return (
        records,
        np.asarray(violations, dtype=np.float64),
        np.asarray(gaps, dtype=np.float64),
        np.asarray(group_failures, dtype=np.float32),
        np.asarray(joint_failures, dtype=np.float32),
    )


def feature_normalization(features: np.ndarray, indices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    center = np.mean(features[indices], axis=0).astype(np.float32)
    scale = np.std(features[indices], axis=0).astype(np.float32)
    scale = np.where(scale > 1e-6, scale, 1.0).astype(np.float32)
    return center, scale


def target_scales(
    violations: np.ndarray,
    gaps: np.ndarray,
    indices: np.ndarray,
    max_normalized_gap: float,
) -> Tuple[np.ndarray, float]:
    transformed_groups = np.log1p(np.maximum(0.0, violations[indices]))
    group_scale = np.maximum(1.0, np.quantile(transformed_groups, 0.95, axis=0)).astype(
        np.float32
    )
    transformed_gap = np.log1p(np.maximum(0.0, gaps[indices]) / max_normalized_gap)
    gap_scale = max(1.0, float(np.quantile(transformed_gap, 0.95)))
    return group_scale, gap_scale


def transformed_targets(
    violations: np.ndarray,
    gaps: np.ndarray,
    group_scale: np.ndarray,
    gap_scale: float,
    max_normalized_gap: float,
) -> Tuple[np.ndarray, np.ndarray]:
    group_target = np.log1p(np.maximum(0.0, violations)) / group_scale[None, :]
    gap_target = np.log1p(np.maximum(0.0, gaps) / max_normalized_gap) / float(gap_scale)
    return np.clip(group_target, 0.0, 12.0), np.clip(gap_target, 0.0, 12.0)


def context_arrays(records: Sequence[Mapping[str, object]]) -> Tuple[np.ndarray, np.ndarray]:
    keys = [context_key(row) for row in records]
    counts = Counter(keys)
    mapping = {key: index for index, key in enumerate(sorted(counts))}
    context_ids = np.asarray([mapping[key] for key in keys], dtype=np.int64)
    weights = np.asarray([1.0 / counts[key] for key in keys], dtype=np.float32)
    weights /= max(1e-12, float(np.mean(weights)))
    return context_ids, weights


def make_tensors(
    features: np.ndarray,
    feature_center: np.ndarray,
    feature_scale: np.ndarray,
    group_target: np.ndarray,
    gap_target: np.ndarray,
    group_failure: np.ndarray,
    joint_failure: np.ndarray,
    context_ids: np.ndarray,
    sample_weights: np.ndarray,
    indices: np.ndarray,
    device: torch.device,
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor], torch.Tensor, torch.Tensor]:
    normalized = (features[indices] - feature_center) / feature_scale
    targets = {
        "group_margin": torch.as_tensor(group_target[indices], dtype=torch.float32, device=device),
        "gap": torch.as_tensor(gap_target[indices], dtype=torch.float32, device=device),
        "group_failure": torch.as_tensor(group_failure[indices], dtype=torch.float32, device=device),
        "joint_failure": torch.as_tensor(joint_failure[indices], dtype=torch.float32, device=device),
    }
    return (
        torch.as_tensor(normalized, dtype=torch.float32, device=device),
        targets,
        torch.as_tensor(context_ids[indices], dtype=torch.long, device=device),
        torch.as_tensor(sample_weights[indices], dtype=torch.float32, device=device),
    )


def prediction_arrays(
    model: BoundaryConstraintHead,
    normalized_features: np.ndarray,
    device: torch.device,
    group_scale: np.ndarray,
    gap_scale: float,
    max_normalized_gap: float,
) -> Dict[str, np.ndarray]:
    model.eval()
    with torch.no_grad():
        output = model(torch.as_tensor(normalized_features, dtype=torch.float32, device=device))
    group_probability = torch.sigmoid(output["group_failure_logit"]).cpu().numpy()
    joint_probability = torch.sigmoid(output["joint_failure_logit"]).cpu().numpy()
    group_margin = np.expm1(
        np.clip(output["group_margin"].cpu().numpy() * group_scale[None, :], 0.0, 40.0)
    )
    gap = max_normalized_gap * np.expm1(
        np.clip(output["gap"].cpu().numpy() * float(gap_scale), 0.0, 40.0)
    )
    gap_probability = sigmoid(6.0 * (gap / max_normalized_gap - 1.0))
    max_group_probability = np.max(group_probability, axis=1)
    combined = 0.60 * joint_probability + 0.25 * max_group_probability + 0.15 * gap_probability
    return {
        "group_probability": group_probability,
        "joint_probability": joint_probability,
        "group_margin": group_margin,
        "gap": gap,
        "gap_probability": gap_probability,
        "max_group_probability": max_group_probability,
        "combined_risk": combined,
    }


def selected_metrics(
    records: Sequence[Mapping[str, object]],
    predictions: Mapping[str, np.ndarray],
    joint_failure: np.ndarray,
    indices: np.ndarray,
) -> Dict[str, float]:
    context_keys = [context_key(records[index]) for index in indices]
    risks = predictions["combined_risk"]
    boundary_sizes = [
        len(json.loads(str(records[index]["predicted_boundary"]))) for index in indices
    ]
    methods = [str(records[index]["method"]) for index in indices]
    chosen_local = choose_candidate_indices(context_keys, risks, boundary_sizes, methods)
    chosen = indices[np.asarray(chosen_local, dtype=int)]
    labels = joint_failure[indices] > 0.5
    return {
        "n_contexts": float(len(chosen)),
        "joint_pass_rate": float(np.mean(joint_failure[chosen] < 0.5)),
        "joint_pass_count": float(np.sum(joint_failure[chosen] < 0.5)),
        "candidate_failure_auc": tie_aware_auc(risks, labels),
    }


def train_head(
    seed: int,
    epochs: int,
    eval_every: int,
    features: np.ndarray,
    records: Sequence[Mapping[str, object]],
    violations: np.ndarray,
    gaps: np.ndarray,
    group_failure: np.ndarray,
    joint_failure: np.ndarray,
    context_ids: np.ndarray,
    sample_weights: np.ndarray,
    train_indices: np.ndarray,
    holdout_indices: np.ndarray,
    device: torch.device,
    args: argparse.Namespace,
) -> Tuple[BoundaryConstraintHead, List[Dict[str, object]], Dict[str, object]]:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    center, scale = feature_normalization(features, train_indices)
    group_scale, gap_scale = target_scales(
        violations, gaps, train_indices, args.max_normalized_gap
    )
    group_target, gap_target = transformed_targets(
        violations, gaps, group_scale, gap_scale, args.max_normalized_gap
    )
    train_x, train_targets, train_contexts, train_weights = make_tensors(
        features,
        center,
        scale,
        group_target,
        gap_target,
        group_failure,
        joint_failure,
        context_ids,
        sample_weights,
        train_indices,
        device,
    )
    holdout_x, holdout_targets, holdout_contexts, holdout_weights = make_tensors(
        features,
        center,
        scale,
        group_target,
        gap_target,
        group_failure,
        joint_failure,
        context_ids,
        sample_weights,
        holdout_indices,
        device,
    )
    model = BoundaryConstraintHead(
        input_dim=features.shape[1],
        hidden_dim=args.hidden_dim,
        dropout=args.dropout,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    group_positive = torch.as_tensor(
        positive_class_weights(group_failure[train_indices]), dtype=torch.float32, device=device
    )
    joint_positive = torch.as_tensor(
        float(positive_class_weights(joint_failure[train_indices, None])[0]),
        dtype=torch.float32,
        device=device,
    )
    history: List[Dict[str, object]] = []
    best_state = copy.deepcopy(model.state_dict())
    best_record: Dict[str, object] = {
        "selection_key": (float("-inf"), float("-inf"), float("-inf"), float("-inf")),
        "epoch": 0,
    }
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        output = model(train_x)
        loss, components = constraint_student_loss(
            output,
            train_targets,
            train_weights,
            train_contexts,
            group_positive,
            joint_positive,
            underestimation_weight=args.underestimation_weight,
            ranking_weight=args.ranking_weight,
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()
        if epoch % eval_every and epoch != epochs:
            continue
        model.eval()
        with torch.no_grad():
            holdout_output = model(holdout_x)
            holdout_loss, holdout_components = constraint_student_loss(
                holdout_output,
                holdout_targets,
                holdout_weights,
                holdout_contexts,
                group_positive,
                joint_positive,
                underestimation_weight=args.underestimation_weight,
                ranking_weight=args.ranking_weight,
            )
        normalized_holdout = (features[holdout_indices] - center) / scale
        predicted = prediction_arrays(
            model,
            normalized_holdout,
            device,
            group_scale,
            gap_scale,
            args.max_normalized_gap,
        )
        metrics = selected_metrics(
            records,
            predicted,
            joint_failure,
            holdout_indices,
        )
        auc = finite_float(metrics["candidate_failure_auc"], 0.5)
        selection_key = (
            float(metrics["joint_pass_rate"]),
            auc,
            -float(holdout_loss.detach().cpu()),
            -float(epoch),
        )
        record = {
            "seed": seed,
            "epoch": epoch,
            **components,
            **{
                f"internal_holdout_{key}": value
                for key, value in holdout_components.items()
            },
            **{f"internal_holdout_{key}": value for key, value in metrics.items()},
            "selection_key": selection_key,
        }
        history.append(record)
        if selection_key > best_record["selection_key"]:
            best_record = record
            best_state = copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    return model, history, {
        **best_record,
        "feature_center": center,
        "feature_scale": scale,
        "group_target_scale": group_scale,
        "gap_target_scale": gap_scale,
    }


def retrain_full(
    seed: int,
    epochs: int,
    features: np.ndarray,
    violations: np.ndarray,
    gaps: np.ndarray,
    group_failure: np.ndarray,
    joint_failure: np.ndarray,
    context_ids: np.ndarray,
    sample_weights: np.ndarray,
    train_indices: np.ndarray,
    device: torch.device,
    args: argparse.Namespace,
) -> Tuple[BoundaryConstraintHead, Dict[str, object]]:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    center, scale = feature_normalization(features, train_indices)
    group_scale, gap_scale = target_scales(
        violations, gaps, train_indices, args.max_normalized_gap
    )
    group_target, gap_target = transformed_targets(
        violations, gaps, group_scale, gap_scale, args.max_normalized_gap
    )
    x, targets, contexts, weights = make_tensors(
        features,
        center,
        scale,
        group_target,
        gap_target,
        group_failure,
        joint_failure,
        context_ids,
        sample_weights,
        train_indices,
        device,
    )
    model = BoundaryConstraintHead(
        input_dim=features.shape[1], hidden_dim=args.hidden_dim, dropout=args.dropout
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    group_positive = torch.as_tensor(
        positive_class_weights(group_failure[train_indices]), dtype=torch.float32, device=device
    )
    joint_positive = torch.as_tensor(
        float(positive_class_weights(joint_failure[train_indices, None])[0]),
        dtype=torch.float32,
        device=device,
    )
    final_components: Dict[str, float] = {}
    for _epoch in range(max(1, epochs)):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        output = model(x)
        loss, final_components = constraint_student_loss(
            output,
            targets,
            weights,
            contexts,
            group_positive,
            joint_positive,
            underestimation_weight=args.underestimation_weight,
            ranking_weight=args.ranking_weight,
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()
    return model, {
        "feature_center": center,
        "feature_scale": scale,
        "group_target_scale": group_scale,
        "gap_target_scale": gap_scale,
        "final_training_loss": final_components,
    }


def augment_selected_rows(
    records: Sequence[Mapping[str, object]],
    predictions: Mapping[str, np.ndarray],
    selected_indices: Sequence[int],
    context_inference_times: Mapping[ContextKey, float],
    graph_times: Mapping[ContextKey, float],
    head_time_per_context: Mapping[ContextKey, float],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    selected_audits: List[Dict[str, object]] = []
    selected_predictions: List[Dict[str, object]] = []
    for index in selected_indices:
        record = records[index]
        audit = dict(record["audit"])  # type: ignore[arg-type]
        key = context_key(record)
        selection_time = (
            finite_float(graph_times.get(key), 0.0)
            + finite_float(context_inference_times.get(key), 0.0)
            + finite_float(head_time_per_context.get(key), 0.0)
        )
        previous_selection = finite_float(audit.get("student_selection_time_sec"), 0.0)
        delta = selection_time - previous_selection
        audit["proposal_source_method"] = audit.get("student_method", "")
        audit["student_method"] = "constraint_aware_gnn"
        audit["proposal_kind"] = record.get("proposal_kind", "")
        audit["proposal_aliases"] = record.get("proposal_aliases", "")
        audit["constraint_failure_probability"] = float(
            predictions["joint_probability"][index]
        )
        audit["constraint_max_group_probability"] = float(
            predictions["max_group_probability"][index]
        )
        audit["constraint_predicted_gap"] = float(predictions["gap"][index])
        audit["constraint_gap_failure_probability"] = float(
            predictions["gap_probability"][index]
        )
        audit["constraint_combined_risk"] = float(predictions["combined_risk"][index])
        audit["constraint_predicted_group_margins"] = json.dumps(
            {
                group: float(predictions["group_margin"][index, group_index])
                for group_index, group in enumerate(GROUP_NAMES)
            },
            sort_keys=True,
        )
        audit["constraint_predicted_group_probabilities"] = json.dumps(
            {
                group: float(predictions["group_probability"][index, group_index])
                for group_index, group in enumerate(GROUP_NAMES)
            },
            sort_keys=True,
        )
        audit["graph_encoding_time_sec"] = graph_times.get(key, 0.0)
        audit["gnn_forward_time_sec"] = context_inference_times.get(key, 0.0)
        audit["constraint_head_time_sec"] = head_time_per_context.get(key, 0.0)
        audit["student_selection_time_sec"] = selection_time
        for field in ("student_audited_pipeline_time_sec", "accepted_pipeline_time_sec"):
            previous = finite_float(audit.get(field))
            if math.isfinite(previous):
                audit[field] = max(0.0, previous + delta)
        teacher_selection = finite_float(audit.get("teacher_selection_time_sec"), 0.0)
        audit_time = finite_float(audit.get("group_context_time_sec"), 0.0) + finite_float(
            audit.get("group_audit_time_sec"), 0.0
        )
        teacher_pipeline = finite_float(audit.get("teacher_pipeline_time_sec"), 0.0)
        audit["selection_speedup_vs_teacher"] = teacher_selection / max(1e-12, selection_time)
        audit["selection_plus_audit_speedup_vs_teacher"] = teacher_selection / max(
            1e-12, selection_time + audit_time
        )
        audit["accepted_speedup_vs_teacher_pipeline"] = teacher_pipeline / max(
            1e-12, finite_float(audit.get("accepted_pipeline_time_sec"), 0.0)
        )
        selected_audits.append(audit)
        selected_predictions.append(
            {
                **{key_name: value for key_name, value in record.items() if key_name != "audit"},
                "method": "constraint_aware_gnn",
                "proposal_source_method": record.get("method", ""),
                "constraint_failure_probability": audit["constraint_failure_probability"],
                "constraint_max_group_probability": audit["constraint_max_group_probability"],
                "constraint_predicted_gap": audit["constraint_predicted_gap"],
                "constraint_combined_risk": audit["constraint_combined_risk"],
                "student_selection_time_sec": selection_time,
            }
        )
    return selected_audits, selected_predictions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train one bounded constraint-aware risk student over frozen GNN proposals."
    )
    parser.add_argument(
        "--candidate-csv",
        type=Path,
        default=Path("experiments/models/boundary_constraint_candidates/constraint_candidates.csv"),
    )
    parser.add_argument("--train-audit-csv", type=Path, required=True)
    parser.add_argument("--validation-audit-csv", type=Path, required=True)
    parser.add_argument("--test-audit-csv", type=Path, required=True)
    parser.add_argument(
        "--teacher-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_teacher_graphonly/boundary_heatmap_contexts.csv"
        ),
    )
    parser.add_argument(
        "--heatmap-teacher-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_teacher_graphonly/boundary_heatmap_targets.csv"
        ),
    )
    parser.add_argument(
        "--base-model-dir",
        type=Path,
        default=Path("experiments/models/boundary_heatmap_gnn_graphonly"),
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--max-normalized-gap", type=float, default=0.01)
    parser.add_argument("--training-seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--underestimation-weight", type=float, default=4.0)
    parser.add_argument("--ranking-weight", type=float, default=0.5)
    parser.add_argument("--internal-holdout-fraction", type=float, default=0.2)
    parser.add_argument("--internal-split-seed", type=int, default=2027)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("experiments/models/boundary_constraint_student"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_constraint_student"),
    )
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA training was requested but CUDA is unavailable.")
    torch.set_num_threads(1)
    if args.device == "auto":
        training_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        training_device = torch.device(args.device)
    inference_device = torch.device("cpu")
    candidates = read_rows(args.candidate_csv)
    base_model, base_protocol = load_base_model(args.base_model_dir)
    samples = build_samples(
        args.teacher_csv,
        args.heatmap_teacher_csv,
        base_protocol,
        args.gamma,
        args.probe_top_fraction,
    )
    features, context_inference_times, graph_times = extract_features(
        candidates, samples, base_model, base_protocol, inference_device
    )
    records, violations, gaps, group_failure, joint_failure = join_audits(
        candidates,
        [args.train_audit_csv, args.validation_audit_csv, args.test_audit_csv],
        args.max_normalized_gap,
    )
    context_ids, sample_weights = context_arrays(records)
    train_maps, internal_holdout_maps = topology_holdout_maps(
        [row for row in records if row.get("split") == "train"],
        holdout_fraction=args.internal_holdout_fraction,
        seed=args.internal_split_seed,
        failure_field="joint_failure",
    )
    train_map_set = set(train_maps)
    holdout_map_set = set(internal_holdout_maps)
    risk_train_indices = np.asarray(
        [
            index
            for index, row in enumerate(records)
            if row.get("split") == "train" and str(row.get("map")) in train_map_set
        ],
        dtype=int,
    )
    internal_holdout_indices = np.asarray(
        [
            index
            for index, row in enumerate(records)
            if row.get("split") == "train" and str(row.get("map")) in holdout_map_set
        ],
        dtype=int,
    )
    official_train_indices = np.asarray(
        [index for index, row in enumerate(records) if row.get("split") == "train"], dtype=int
    )
    if not len(risk_train_indices) or not len(internal_holdout_indices):
        raise RuntimeError("Internal topology split is empty.")

    histories: List[Dict[str, object]] = []
    seed_results: List[Tuple[BoundaryConstraintHead, Dict[str, object]]] = []
    for seed in args.training_seeds:
        model, history, best = train_head(
            seed,
            args.epochs,
            args.eval_every,
            features,
            records,
            violations,
            gaps,
            group_failure,
            joint_failure,
            context_ids,
            sample_weights,
            risk_train_indices,
            internal_holdout_indices,
            training_device,
            args,
        )
        histories.extend(history)
        seed_results.append((model, {**best, "seed": seed}))
    _selected_model, selected = max(
        seed_results,
        key=lambda item: tuple(item[1]["selection_key"]),
    )
    selected_seed = int(selected["seed"])
    selected_epoch = int(selected["epoch"])
    final_model, final_protocol = retrain_full(
        selected_seed,
        selected_epoch,
        features,
        violations,
        gaps,
        group_failure,
        joint_failure,
        context_ids,
        sample_weights,
        official_train_indices,
        training_device,
        args,
    )
    final_model = final_model.to(inference_device).eval()
    feature_center = np.asarray(final_protocol["feature_center"], dtype=np.float32)
    feature_scale = np.asarray(final_protocol["feature_scale"], dtype=np.float32)
    group_scale = np.asarray(final_protocol["group_target_scale"], dtype=np.float32)
    gap_scale = float(final_protocol["gap_target_scale"])
    normalized_features = (features - feature_center) / feature_scale
    predictions = prediction_arrays(
        final_model,
        normalized_features,
        inference_device,
        group_scale,
        gap_scale,
        args.max_normalized_gap,
    )

    grouped_indices: Dict[ContextKey, List[int]] = defaultdict(list)
    for index, record in enumerate(records):
        grouped_indices[context_key(record)].append(index)
    head_times: Dict[ContextKey, float] = {}
    for key, indices in grouped_indices.items():
        tensor = torch.as_tensor(
            normalized_features[np.asarray(indices, dtype=int)], dtype=torch.float32
        )
        with torch.no_grad():
            final_model(tensor)
        timings = []
        for _repeat in range(5):
            started = time.perf_counter()
            with torch.no_grad():
                final_model(tensor)
            timings.append(time.perf_counter() - started)
        head_times[key] = median(timings)

    split_summaries = []
    selected_by_split: Dict[str, List[int]] = {}
    candidate_prediction_rows: List[Dict[str, object]] = []
    for index, record in enumerate(records):
        candidate_prediction_rows.append(
            {
                **{key: value for key, value in record.items() if key != "audit"},
                **{
                    f"constraint_{group}_failure_probability": float(
                        predictions["group_probability"][index, group_index]
                    )
                    for group_index, group in enumerate(GROUP_NAMES)
                },
                "constraint_failure_probability": float(
                    predictions["joint_probability"][index]
                ),
                "constraint_max_group_probability": float(
                    predictions["max_group_probability"][index]
                ),
                "constraint_predicted_gap": float(predictions["gap"][index]),
                "constraint_gap_failure_probability": float(
                    predictions["gap_probability"][index]
                ),
                "constraint_combined_risk": float(predictions["combined_risk"][index]),
                "audited_joint_failure": bool(joint_failure[index] > 0.5),
            }
        )
    for split in ("train", "validation", "test"):
        indices = np.asarray(
            [index for index, row in enumerate(records) if row.get("split") == split], dtype=int
        )
        local_keys = [context_key(records[index]) for index in indices]
        local_sizes = [
            len(json.loads(str(records[index]["predicted_boundary"]))) for index in indices
        ]
        local_methods = [str(records[index]["method"]) for index in indices]
        chosen_local = choose_candidate_indices(
            local_keys,
            predictions["combined_risk"][indices],
            local_sizes,
            local_methods,
        )
        chosen = indices[np.asarray(chosen_local, dtype=int)].tolist()
        selected_by_split[split] = chosen
        context_groups: Dict[ContextKey, List[int]] = defaultdict(list)
        for index in indices:
            context_groups[context_key(records[index])].append(int(index))
        split_summaries.append(
            {
                "split": split,
                "n_candidates": len(indices),
                "n_contexts": len(chosen),
                "joint_pass_count": sum(joint_failure[index] < 0.5 for index in chosen),
                "joint_pass_rate": float(np.mean(joint_failure[chosen] < 0.5)),
                "oracle_union_pass_count": sum(
                    any(joint_failure[index] < 0.5 for index in group)
                    for group in context_groups.values()
                ),
                "oracle_union_pass_rate": sum(
                    any(joint_failure[index] < 0.5 for index in group)
                    for group in context_groups.values()
                )
                / max(1, len(context_groups)),
                "candidate_failure_auc": tie_aware_auc(
                    predictions["combined_risk"][indices], joint_failure[indices] > 0.5
                ),
                "median_selection_time_sec": median(
                    graph_times[context_key(records[index])]
                    + context_inference_times[context_key(records[index])]
                    + head_times[context_key(records[index])]
                    for index in chosen
                ),
            }
        )

    args.model_dir.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    weight_map = state_dict_to_npz(final_model, args.model_dir / "constraint_head.npz")
    write_csv_all_fields(args.model_dir / "candidate_risk_predictions.csv", candidate_prediction_rows)
    write_csv_all_fields(args.out_dir / "training_history.csv", histories)
    all_selected_audits: List[Dict[str, object]] = []
    for split, selected_indices in selected_by_split.items():
        selected_audits, selected_prediction_rows = augment_selected_rows(
            records,
            predictions,
            selected_indices,
            context_inference_times,
            graph_times,
            head_times,
        )
        all_selected_audits.extend(selected_audits)
        write_csv_all_fields(args.model_dir / f"selected_{split}_predictions.csv", selected_prediction_rows)
        write_csv_all_fields(args.out_dir / f"selected_{split}_downstream.csv", selected_audits)
    write_csv_all_fields(args.out_dir / "selected_downstream.csv", all_selected_audits)
    write_csv_all_fields(args.out_dir / "summary.csv", split_summaries)
    test_summary = next(row for row in split_summaries if row["split"] == "test")
    raw_gate = {
        "required_test_joint_pass_count": 70,
        "observed_test_joint_pass_count": int(test_summary["joint_pass_count"]),
        "raw_joint_pass_gate": int(test_summary["joint_pass_count"]) >= 70,
        "remaining_gates": [
            "validation-calibrated missed held-out failures <= 1",
            "accepted pipeline speedup > 1",
            "topology holdout does not collapse",
        ],
    }
    protocol = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "base_model_dir": str(args.base_model_dir),
        "base_model_method": base_protocol["selected_student_method"],
        "base_validation_reuse_note": (
            "The frozen boundary GNN was selected on the pre-existing validation split; "
            "the risk head uses only training labels for fitting and internal model selection."
        ),
        "training_device": str(training_device),
        "inference_device": str(inference_device),
        "selected_seed": selected_seed,
        "selected_epoch": selected_epoch,
        "selected_internal_record": {
            key: value
            for key, value in selected.items()
            if key not in {"feature_center", "feature_scale", "group_target_scale"}
        },
        "internal_train_maps": list(train_maps),
        "internal_holdout_maps": list(internal_holdout_maps),
        "all_slips_grouped_by_map": True,
        "model_config": final_model.config(),
        "weight_key_map": weight_map,
        "feature_center": feature_center.tolist(),
        "feature_scale": feature_scale.tolist(),
        "group_names": list(GROUP_NAMES),
        "group_target_scale": group_scale.tolist(),
        "gap_target_scale": gap_scale,
        "max_normalized_gap": args.max_normalized_gap,
        "underestimation_weight": args.underestimation_weight,
        "ranking_weight": args.ranking_weight,
        "proposal_family": list(PROPOSAL_KINDS),
        "risk_formula": "0.60*joint + 0.25*max_group + 0.15*gap_failure",
        "certificate_status": "uncertified proposal/routing extension",
        "production_rule": "Student proposes; Green operator certifies.",
    }
    (args.model_dir / "protocol.json").write_text(
        json.dumps(protocol, indent=2, default=json_default, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.json").write_text(
        json.dumps(
            {"splits": split_summaries, "raw_go_no_go": raw_gate},
            indent=2,
            default=json_default,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Constraint-Aware Boundary Student",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "The frozen transition-graph GNN emits a fixed five-proposal family. A multi-head risk student predicts the three group-violation channels, normalized value gap, and joint failure, using an asymmetric underestimation penalty. It reranks proposals but does not certify them and never performs candidate insertion, beam search, or Green recomputation.",
        "",
        "Student proposes; Green operator certifies.",
        "",
        markdown_table(split_summaries, list(split_summaries[0])),
        "",
        "## Prespecified Raw Gate",
        "",
        f"- test joint pass: {raw_gate['observed_test_joint_pass_count']}/90 (required >=70)",
        f"- raw gate: {'PASS' if raw_gate['raw_joint_pass_gate'] else 'NO-GO'}",
        "- independent validation calibration, accepted-pipeline runtime, and topology-holdout gates are evaluated separately.",
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"splits": split_summaries, "raw_go_no_go": raw_gate},
            default=json_default,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
