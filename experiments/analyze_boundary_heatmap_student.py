#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import write_csv_all_fields


def read_rows(path: Path) -> List[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def mean(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.fmean(clean)) if clean else float("nan")


def median(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(clean)) if clean else float("nan")


def rate(values: Iterable[bool]) -> float:
    clean = list(values)
    return sum(bool(value) for value in clean) / max(1, len(clean))


def context_key(row: Mapping[str, object]) -> Tuple[str, str, str]:
    return (
        str(row.get("map", "")),
        f"{finite_float(row.get('slip'), 0.0):.12g}",
        str(row.get("method", row.get("student_method", ""))),
    )


def tie_aware_auc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    positive = [score for score, label in zip(scores, labels) if label and math.isfinite(score)]
    negative = [score for score, label in zip(scores, labels) if not label and math.isfinite(score)]
    if not positive or not negative:
        return float("nan")
    wins = 0.0
    for left in positive:
        for right in negative:
            wins += 1.0 if left > right else 0.5 if left == right else 0.0
    return wins / (len(positive) * len(negative))


def selected_method(predictions: Sequence[Mapping[str, object]], requested: str) -> str:
    if requested:
        return requested
    methods = {str(row.get("method", "")) for row in predictions}
    if "gnn_ensemble" in methods:
        return "gnn_ensemble"
    if "gnn_ensemble_top1" in methods:
        return "gnn_ensemble_top1"
    candidates = sorted(method for method in methods if method.startswith("gnn_ensemble"))
    if not candidates:
        raise ValueError("No ensemble student method appears in the prediction table.")
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit GNN boundary heatmaps against simple rules and downstream constraints.")
    parser.add_argument(
        "--predictions-csv",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_gnn/predictions.csv"),
    )
    parser.add_argument(
        "--downstream-csv",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_downstream/boundary_heatmap_downstream.csv"),
    )
    parser.add_argument("--selected-method", default="")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_student_audit"),
    )
    args = parser.parse_args()

    predictions = read_rows(args.predictions_csv)
    downstream = read_rows(args.downstream_csv) if args.downstream_csv.exists() else []
    method = selected_method(predictions, args.selected_method)
    nearest = {
        (str(row.get("split")), str(row.get("map")), f"{finite_float(row.get('slip'), 0.0):.12g}"):
        str(row.get("predicted_boundary", ""))
        for row in predictions
        if row.get("method") == "baseline_nearest_start"
    }
    selected = [row for row in predictions if row.get("method") == method]
    selected_test = [row for row in selected if row.get("split") == "test"]
    prediction_by_key = {context_key(row): row for row in predictions}

    joined: List[Dict[str, object]] = []
    for raw in downstream:
        row = dict(raw)
        prediction = prediction_by_key.get(context_key(raw), {})
        for field in (
            "score_margin",
            "ensemble_top_state_agreement",
            "ensemble_max_node_logit_std",
            "ensemble_selected_logit_std",
        ):
            if not row.get(field):
                row[field] = prediction.get(field, "")
        joined.append(row)

    identity_rows: List[Dict[str, object]] = []
    for split in sorted({str(row.get("split")) for row in selected}):
        group = [row for row in selected if row.get("split") == split]
        identity_rows.append(
            {
                "split": split,
                "n_rows": len(group),
                "match_nearest_start_rate": rate(
                    str(row.get("predicted_boundary", ""))
                    == nearest.get(
                        (
                            split,
                            str(row.get("map")),
                            f"{finite_float(row.get('slip'), 0.0):.12g}",
                        ),
                        "",
                    )
                    for row in group
                ),
                "top_set_hit_rate": rate(parse_bool(row.get("top_set_hit")) for row in group),
                "teacher_tie_rate": rate(
                    int(finite_float(row.get("teacher_top_set_size"), 0.0)) > 1 for row in group
                ),
                "count_accuracy": rate(parse_bool(row.get("count_match")) for row in group),
                "mean_boundary_jaccard": mean(
                    finite_float(row.get("boundary_jaccard")) for row in group
                ),
            }
        )

    downstream_by_method: List[Dict[str, object]] = []
    for student_method in sorted({str(row.get("student_method", "")) for row in joined}):
        group = [row for row in joined if row.get("student_method") == student_method]
        downstream_by_method.append(
            {
                "student_method": student_method,
                "n_rows": len(group),
                "student_feasible_rate": rate(
                    parse_bool(row.get("student_group_all_feasible")) for row in group
                ),
                "teacher_feasible_rate": rate(
                    parse_bool(row.get("teacher_group_all_feasible")) for row in group
                ),
                "fallback_rate": rate(parse_bool(row.get("fallback_used")) for row in group),
                "median_compression": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "median_selection_speedup": median(
                    finite_float(row.get("selection_speedup_vs_teacher")) for row in group
                ),
                "median_audited_speedup": median(
                    finite_float(row.get("selection_plus_audit_speedup_vs_teacher"))
                    for row in group
                ),
                "max_normalized_start_gap": max(
                    (finite_float(row.get("student_normalized_start_gap")) for row in group),
                    default=float("nan"),
                ),
            }
        )

    selected_downstream = [row for row in joined if row.get("student_method") == method]
    if not selected_downstream and method == "gnn_ensemble":
        selected_downstream = [
            row for row in joined if row.get("student_method") == "gnn_ensemble_top1"
        ]
    family_rows: List[Dict[str, object]] = []
    for family in sorted({str(row.get("map_family", "")) for row in selected_downstream}):
        group = [row for row in selected_downstream if row.get("map_family") == family]
        family_rows.append(
            {
                "map_family": family,
                "n_rows": len(group),
                "student_feasible_rate": rate(
                    parse_bool(row.get("student_group_all_feasible")) for row in group
                ),
                "teacher_feasible_rate": rate(
                    parse_bool(row.get("teacher_group_all_feasible")) for row in group
                ),
                "mean_boundary_jaccard": mean(
                    finite_float(row.get("boundary_jaccard")) for row in group
                ),
                "median_compression": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "max_normalized_start_gap": max(
                    (finite_float(row.get("student_normalized_start_gap")) for row in group),
                    default=float("nan"),
                ),
            }
        )

    confidence_rows: List[Dict[str, object]] = []
    failure_labels = [not parse_bool(row.get("student_group_all_feasible")) for row in selected_downstream]
    for field, risk_transform in (
        ("score_margin", lambda value: -value),
        ("ensemble_top_state_agreement", lambda value: -value),
        ("ensemble_max_node_logit_std", lambda value: value),
        ("ensemble_selected_logit_std", lambda value: value),
    ):
        values = [finite_float(row.get(field)) for row in selected_downstream]
        risks = [risk_transform(value) if math.isfinite(value) else value for value in values]
        failed = [value for value, label in zip(values, failure_labels) if label]
        passed = [value for value, label in zip(values, failure_labels) if not label]
        confidence_rows.append(
            {
                "metric": field,
                "failure_detection_auc": tie_aware_auc(risks, failure_labels),
                "pass_median": median(passed),
                "failure_median": median(failed),
                "n_finite": sum(math.isfinite(value) for value in values),
            }
        )

    topk_groups: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in joined:
        if str(row.get("student_method", "")).startswith("gnn_ensemble_top"):
            topk_groups.setdefault(
                (str(row.get("map")), f"{finite_float(row.get('slip'), 0.0):.12g}"), []
            ).append(row)
    recovered = 0
    lost = 0
    for group in topk_groups.values():
        ordered = sorted(group, key=lambda row: int(str(row.get("student_method", "0")).rsplit("top", 1)[-1]))
        feasible = [parse_bool(row.get("student_group_all_feasible")) for row in ordered]
        recovered += any(not left and right for left, right in zip(feasible, feasible[1:]))
        lost += any(left and not right for left, right in zip(feasible, feasible[1:]))

    overview = {
        "selected_method": method,
        "n_prediction_rows": len(predictions),
        "n_selected_test_rows": len(selected_test),
        "n_downstream_rows": len(joined),
        "topk_contexts": len(topk_groups),
        "topk_recovery_contexts": recovered,
        "topk_feasibility_loss_contexts": lost,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "identity_summary.csv", identity_rows)
    write_csv_all_fields(args.out_dir / "downstream_summary.csv", downstream_by_method)
    write_csv_all_fields(args.out_dir / "family_summary.csv", family_rows)
    write_csv_all_fields(args.out_dir / "confidence_summary.csv", confidence_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(
            {
                "overview": overview,
                "identity": identity_rows,
                "downstream": downstream_by_method,
                "families": family_rows,
                "confidence": confidence_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Boundary Heatmap Student Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"selected method = `{method}`, prediction rows = {len(predictions)}, downstream rows = {len(joined)}",
        "",
        "## Explicit-Rule Identity",
        "",
        markdown_table(identity_rows, list(identity_rows[0]) if identity_rows else []),
        "",
        "## Downstream Feasibility",
        "",
        markdown_table(downstream_by_method, list(downstream_by_method[0]) if downstream_by_method else []),
        "",
        "## Family Holdout",
        "",
        markdown_table(family_rows, list(family_rows[0]) if family_rows else []),
        "",
        "## Selective-Audit Diagnostics",
        "",
        markdown_table(confidence_rows, list(confidence_rows[0]) if confidence_rows else []),
        "",
        f"Fixed top-k recovered feasibility in {recovered}/{len(topk_groups)} contexts and lost it in {lost}/{len(topk_groups)} contexts. The latter count is direct evidence that hard-group feasibility is not monotone in the number of frozen heatmap vertices.",
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(overview, sort_keys=True))


if __name__ == "__main__":
    main()
