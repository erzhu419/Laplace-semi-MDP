#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Tuple

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def median(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(clean)) if clean else float("nan")


def rate(values: Iterable[bool]) -> float:
    clean = list(values)
    return sum(1 for value in clean if value) / max(1, len(clean))


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded GNN downstream audits.")
    parser.add_argument("--input-globs", nargs="+", required=True)
    parser.add_argument(
        "--predictions-csv",
        type=Path,
        default=None,
        help="Optionally rebind unchanged audited boundaries to newer deployment timing measurements.",
    )
    parser.add_argument("--expected-rows", type=int, default=0)
    parser.add_argument("--max-normalized-gap", type=float, default=0.01)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_downstream"),
    )
    args = parser.parse_args()
    paths = sorted(
        {
            Path(match)
            for pattern in args.input_globs
            for match in glob.glob(pattern, recursive=True)
            if Path(match).is_file()
        }
    )
    if not paths:
        raise FileNotFoundError(f"No downstream CSVs matched: {args.input_globs}")
    merged: Dict[Tuple[str, str, str], Dict[str, object]] = {}
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (
                    str(row.get("map")),
                    f"{finite_float(row.get('slip'), 0.0):.12g}",
                    str(row.get("student_method", "")),
                )
                merged[key] = dict(row)
    rows = sorted(
        merged.values(),
        key=lambda row: (
            int(finite_float(row.get("map_size"), 0.0)),
            int(finite_float(row.get("maze_seed"), 0.0)),
            finite_float(row.get("slip"), 0.0),
            str(row.get("student_method", "")),
        ),
    )
    if args.predictions_csv is not None:
        predictions: Dict[Tuple[str, str, str], Dict[str, object]] = {}
        with args.predictions_csv.open(newline="", encoding="utf-8") as handle:
            for prediction in csv.DictReader(handle):
                key = (
                    str(prediction.get("map")),
                    f"{finite_float(prediction.get('slip'), 0.0):.12g}",
                    str(prediction.get("method", "")),
                )
                predictions[key] = dict(prediction)
        for row in rows:
            key = (
                str(row.get("map")),
                f"{finite_float(row.get('slip'), 0.0):.12g}",
                str(row.get("student_method", "")),
            )
            prediction = predictions.get(key)
            if prediction is None:
                raise RuntimeError(f"No timing prediction matches audited row {key}.")
            audited_boundary = sorted(json.loads(str(row.get("student_boundary", "[]"))))
            predicted_boundary = sorted(
                json.loads(str(prediction.get("predicted_boundary", "[]")))
            )
            if audited_boundary != predicted_boundary:
                raise RuntimeError(
                    f"Cannot rebind timing because the audited boundary changed for {key}."
                )
            old_selection = finite_float(row.get("student_selection_time_sec"), 0.0)
            new_selection = finite_float(
                prediction.get("student_selection_time_sec"), old_selection
            )
            delta = new_selection - old_selection
            row["graph_encoding_time_sec"] = prediction.get(
                "graph_encoding_time_sec", row.get("graph_encoding_time_sec", "")
            )
            row["gnn_forward_time_sec"] = prediction.get(
                "gnn_forward_time_sec", row.get("gnn_forward_time_sec", "")
            )
            row["student_selection_time_sec"] = new_selection
            for field in (
                "student_audited_pipeline_time_sec",
                "accepted_pipeline_time_sec",
            ):
                previous = finite_float(row.get(field))
                if math.isfinite(previous):
                    row[field] = max(0.0, previous + delta)
            teacher_selection = finite_float(row.get("teacher_selection_time_sec"), 0.0)
            audit_time = finite_float(row.get("group_context_time_sec"), 0.0) + finite_float(
                row.get("group_audit_time_sec"), 0.0
            )
            teacher_pipeline = finite_float(row.get("teacher_pipeline_time_sec"), 0.0)
            accepted_pipeline = finite_float(row.get("accepted_pipeline_time_sec"), 0.0)
            row["selection_speedup_vs_teacher"] = teacher_selection / max(
                1e-12, new_selection
            )
            row["selection_plus_audit_speedup_vs_teacher"] = teacher_selection / max(
                1e-12, new_selection + audit_time
            )
            row["accepted_speedup_vs_teacher_pipeline"] = teacher_pipeline / max(
                1e-12, accepted_pipeline
            )
    errors = [row for row in rows if row.get("error")]
    if errors:
        raise RuntimeError(f"Downstream audit contains {len(errors)} error rows.")
    if args.expected_rows and len(rows) != args.expected_rows:
        raise RuntimeError(f"Expected {args.expected_rows} rows, found {len(rows)}.")
    def summarize(group: List[Mapping[str, object]]) -> Dict[str, object]:
        def joint_pass(row: Mapping[str, object], prefix: str) -> bool:
            return parse_bool(row.get(f"{prefix}_group_all_feasible")) and finite_float(
                row.get(f"{prefix}_normalized_start_gap"), float("inf")
            ) <= args.max_normalized_gap

        return {
            "student_method": str(group[0].get("student_method", "")),
            "n_rows": len(group),
            "teacher_feasible_rate": rate(parse_bool(row.get("teacher_group_all_feasible")) for row in group),
            "student_feasible_rate": rate(parse_bool(row.get("student_group_all_feasible")) for row in group),
            "student_joint_constraint_rate": rate(
                joint_pass(row, "student") for row in group
            ),
            "teacher_joint_constraint_rate": rate(
                joint_pass(row, "teacher") for row in group
            ),
            "accepted_joint_constraint_rate": rate(
                joint_pass(row, "student") or joint_pass(row, "teacher")
                for row in group
            ),
            "accepted_feasible_rate": rate(parse_bool(row.get("accepted_group_all_feasible")) for row in group),
            "fallback_rate": rate(parse_bool(row.get("fallback_used")) for row in group),
            "top_set_hit_rate": rate(parse_bool(row.get("top_set_hit")) for row in group),
            "mean_boundary_jaccard": sum(
                finite_float(row.get("boundary_jaccard"), 0.0) for row in group
            )
            / max(1, len(group)),
            "median_state_compression_ratio": median(
                finite_float(row.get("state_compression_ratio")) for row in group
            ),
            "max_student_normalized_start_gap": max(
                (finite_float(row.get("student_normalized_start_gap")) for row in group),
                default=float("nan"),
            ),
            "max_accepted_normalized_start_gap": max(
                (finite_float(row.get("accepted_normalized_start_gap")) for row in group),
                default=float("nan"),
            ),
            "max_student_group_total_violation": max(
                (finite_float(row.get("student_group_total_violation"), 0.0) for row in group),
                default=float("nan"),
            ),
            "median_student_selection_time_sec": median(
                finite_float(row.get("student_selection_time_sec")) for row in group
            ),
            "median_group_audit_time_sec": median(
                finite_float(row.get("group_context_time_sec"), 0.0)
                + finite_float(row.get("group_audit_time_sec"), 0.0)
                for row in group
            ),
            "median_selection_speedup_vs_teacher": median(
                finite_float(row.get("selection_speedup_vs_teacher")) for row in group
            ),
            "median_selection_plus_audit_speedup_vs_teacher": median(
                finite_float(row.get("selection_plus_audit_speedup_vs_teacher")) for row in group
            ),
            "median_accepted_speedup_vs_teacher_pipeline": median(
                finite_float(row.get("accepted_speedup_vs_teacher_pipeline")) for row in group
            ),
        }

    methods = sorted({str(row.get("student_method", "")) for row in rows})
    summary_rows = [summarize([row for row in rows if row.get("student_method") == method]) for method in methods]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "boundary_heatmap_downstream.csv", rows)
    write_csv_all_fields(args.out_dir / "summary.csv", summary_rows)
    (args.out_dir / "boundary_heatmap_downstream.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    columns = list(summary_rows[0]) if summary_rows else []
    detail_columns = [
        "map",
        "slip",
        "student_n_boundary",
        "boundary_jaccard",
        "top_set_hit",
        "student_group_all_feasible",
        "teacher_group_all_feasible",
        "fallback_used",
        "student_group_total_violation",
        "student_normalized_start_gap",
        "student_selection_time_sec",
        "group_context_time_sec",
        "group_audit_time_sec",
        "selection_speedup_vs_teacher",
        "selection_plus_audit_speedup_vs_teacher",
    ]
    lines = [
        "# GNN Boundary Heatmap Downstream Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "The student emits a graph without candidate insertion or Green recomputation. Every graph is then checked by the production hard-group audit. Failed student graphs invoke the separately timed group-constrained teacher fallback. Selection-only, selection-plus-audit, and accepted end-to-end paths are reported separately.",
        "",
        markdown_table(summary_rows, columns),
        "",
        "## Rows",
        "",
        markdown_table(
            [{column: row.get(column, "") for column in detail_columns} for row in rows],
            detail_columns,
        ),
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary_rows, sort_keys=True))


if __name__ == "__main__":
    main()
