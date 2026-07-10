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
from typing import Dict, List, Mapping, Tuple

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded GNN heatmap-teacher candidate rows.")
    parser.add_argument("--input-globs", nargs="+", required=True)
    parser.add_argument(
        "--context-input-globs",
        nargs="*",
        default=[],
        help="Optional full adaptive-teacher context CSVs produced by --full-teacher.",
    )
    parser.add_argument("--expected-contexts", type=int, default=0)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_teacher"),
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
        raise FileNotFoundError(f"No teacher CSVs matched: {args.input_globs}")
    merged: Dict[Tuple[str, str, str], Dict[str, object]] = {}
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (
                    str(row.get("map")),
                    f"{finite_float(row.get('slip'), 0.0):.12g}",
                    str(row.get("candidate_state")),
                )
                merged[key] = dict(row)
    rows = sorted(
        merged.values(),
        key=lambda row: (
            int(finite_float(row.get("map_size"), 0.0)),
            int(finite_float(row.get("maze_seed"), 0.0)),
            finite_float(row.get("slip"), 0.0),
            int(finite_float(row.get("rank"), 10**9)),
        ),
    )
    contexts: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        contexts.setdefault(
            (str(row.get("map")), f"{finite_float(row.get('slip'), 0.0):.12g}"), []
        ).append(row)
    failures = [row for row in rows if row.get("error")]
    if failures:
        raise RuntimeError(f"Teacher heatmap contains {len(failures)} failed context rows.")
    if args.expected_contexts and len(contexts) != args.expected_contexts:
        raise RuntimeError(
            f"Expected {args.expected_contexts} contexts, found {len(contexts)} across {len(paths)} files."
        )
    context_rows: List[Dict[str, object]] = []
    for (map_name, slip), group in sorted(contexts.items()):
        context_rows.append(
            {
                "map": map_name,
                "slip": slip,
                "map_size": group[0].get("map_size", ""),
                "maze_seed": group[0].get("maze_seed", ""),
                "n_states": group[0].get("n_states", ""),
                "n_candidates": len(group),
                "top_state": min(group, key=lambda row: int(finite_float(row.get("rank"), 10**9))).get(
                    "candidate_state", ""
                ),
                "teacher_time_sec": max(finite_float(row.get("teacher_time_sec"), 0.0) for row in group),
                "max_violation_reduction": max(
                    finite_float(row.get("violation_reduction"), 0.0) for row in group
                ),
            }
        )
    times = [float(row["teacher_time_sec"]) for row in context_rows]
    teacher_paths = sorted(
        {
            Path(match)
            for pattern in args.context_input_globs
            for match in glob.glob(pattern, recursive=True)
            if Path(match).is_file()
        }
    )
    teacher_by_context: Dict[Tuple[str, str], Dict[str, object]] = {}
    for path in teacher_paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (
                    str(row.get("map")),
                    f"{finite_float(row.get('slip'), 0.0):.12g}",
                )
                teacher_by_context[key] = dict(row)
    teacher_rows = sorted(
        teacher_by_context.values(),
        key=lambda row: (
            str(row.get("split", "")),
            str(row.get("map_family", "")),
            int(finite_float(row.get("map_size"), 0.0)),
            int(finite_float(row.get("topology_seed", row.get("maze_seed")), 0.0)),
            int(finite_float(row.get("goal_variant"), 0.0)),
            finite_float(row.get("slip"), 0.0),
        ),
    )
    teacher_failures = [row for row in teacher_rows if row.get("error")]
    if teacher_failures:
        raise RuntimeError(f"Adaptive teacher contains {len(teacher_failures)} failed contexts.")
    if teacher_rows and len(teacher_rows) != len(contexts):
        raise RuntimeError(
            f"Heatmap/adaptive teacher mismatch: {len(contexts)} heatmaps, {len(teacher_rows)} labels."
        )
    summary = {
        "n_input_files": len(paths),
        "n_contexts": len(contexts),
        "n_candidate_rows": len(rows),
        "median_candidates": statistics.median(
            int(row["n_candidates"]) for row in context_rows
        ),
        "median_teacher_time_sec": statistics.median(times),
        "total_teacher_time_sec": sum(times),
        "n_adaptive_teacher_contexts": len(teacher_rows),
        "adaptive_teacher_feasible_rate": (
            sum(str(row.get("group_all_feasible", "")).lower() == "true" for row in teacher_rows)
            / max(1, len(teacher_rows))
            if teacher_rows
            else None
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "boundary_heatmap_teacher.csv", rows)
    compact_fields = [
        "split",
        "map_family",
        "map_size",
        "map",
        "maze_seed",
        "topology_seed",
        "goal_variant",
        "slip",
        "n_states",
        "candidate_state",
        "rank",
        "is_top",
        "target_score",
        "target_reduction",
        "error",
    ]
    write_csv_all_fields(
        args.out_dir / "boundary_heatmap_targets.csv",
        [{field: row.get(field, "") for field in compact_fields} for row in rows],
    )
    write_csv_all_fields(args.out_dir / "context_summary.csv", context_rows)
    if teacher_rows:
        write_csv_all_fields(args.out_dir / "boundary_heatmap_contexts.csv", teacher_rows)
    (args.out_dir / "boundary_heatmap_teacher.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    if teacher_rows:
        (args.out_dir / "boundary_heatmap_contexts.json").write_text(
            json.dumps(teacher_rows, indent=2, default=json_default) + "\n",
            encoding="utf-8",
        )
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    columns = [
        "map",
        "slip",
        "n_states",
        "n_candidates",
        "top_state",
        "teacher_time_sec",
        "max_violation_reduction",
    ]
    lines = [
        "# Frozen Insertion-Score Heatmap Teacher",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"inputs = {len(paths)}, contexts = {len(contexts)}, candidate rows = {len(rows)}",
        f"median teacher time = {summary['median_teacher_time_sec']:.6g}s, total serial-equivalent time = {summary['total_teacher_time_sec']:.6g}s",
        "",
        markdown_table(context_rows, columns),
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
