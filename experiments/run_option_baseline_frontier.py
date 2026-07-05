#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from run_first_boundary_targeted import MAPS, markdown_table
from run_option_algorithm_comparison import (
    evaluate_method,
    json_default,
    write_csv_all_fields,
)


DEFAULT_K_VALUES = (4, 8, 12, 16, 24)
DEFAULT_FAMILIES = ("eigenoptions", "betweenness", "random_landmarks", "coverage")
DEFAULT_OBJECTIVES = (
    "description_length_proxy",
    "occupancy_struct_hidden_distinct",
    "struct_hidden_distinct_cvar95",
)


def expand_methods(
    families: Sequence[str],
    k_values: Sequence[int],
    include_endpoints: bool,
    include_graph_rd: bool,
    include_dense: bool,
) -> List[str]:
    methods: List[str] = []
    if include_endpoints:
        methods.append("endpoints")
    for family in families:
        for k in k_values:
            methods.append(f"{family}_{int(k)}")
    if include_graph_rd:
        methods.append("graph_rd_joint")
    if include_dense:
        methods.append("turn_articulation")
    return methods


def finite_float(row: Mapping[str, object], key: str) -> float:
    try:
        value = float(row[key])
    except (KeyError, TypeError, ValueError):
        return float("inf")
    return value if math.isfinite(value) else float("inf")


def is_dominated(
    row: Mapping[str, object],
    other: Mapping[str, object],
    objectives: Sequence[str],
    eps: float = 1e-12,
) -> bool:
    no_worse = all(finite_float(other, obj) <= finite_float(row, obj) + eps for obj in objectives)
    strictly_better = any(finite_float(other, obj) < finite_float(row, obj) - eps for obj in objectives)
    return bool(no_worse and strictly_better)


def mark_pareto_frontier(
    rows: Sequence[Dict[str, object]],
    objectives: Sequence[str],
) -> List[Dict[str, object]]:
    out = [dict(row) for row in rows]
    for i, row in enumerate(out):
        group = [
            other
            for other in out
            if other["map"] == row["map"] and float(other["slip"]) == float(row["slip"])
        ]
        dominated_by = [other["method"] for other in group if other is not row and is_dominated(row, other, objectives)]
        out[i]["pareto_frontier"] = len(dominated_by) == 0
        out[i]["pareto_dominated_by"] = ",".join(str(method) for method in dominated_by[:5])
    return out


def family_name(method: str) -> str:
    for suffix in ("_4", "_8", "_12", "_16", "_24", "_32"):
        if method.endswith(suffix):
            return method[: -len(suffix)]
    return method


def best_by_family(
    rows: Sequence[Mapping[str, object]],
    primary_metric: str,
) -> List[Mapping[str, object]]:
    best: Dict[Tuple[object, object, str], Mapping[str, object]] = {}
    for row in rows:
        key = (row["map"], row["slip"], family_name(str(row["method"])))
        if key not in best or finite_float(row, primary_metric) < finite_float(best[key], primary_metric):
            best[key] = row
    return list(best.values())


def write_report(
    rows: Sequence[Mapping[str, object]],
    frontier_rows: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    columns = [
        "method",
        "map",
        "slip",
        "n_boundary",
        "pareto_frontier",
        "success_rate",
        "primitive_steps_mean",
        "description_length_proxy",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
        "hidden_audit_distinct_mean",
    ]
    frontier_columns = [
        "method",
        "map",
        "slip",
        "n_boundary",
        "description_length_proxy",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
        "hidden_audit_distinct_mean",
    ]
    family_rows = best_by_family(rows, primary_metric=args.primary_metric)
    lines = [
        "# Option Baseline Frontier",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"k_values = {list(args.k_values)}",
        f"families = {list(args.families)}",
        f"objectives = {list(args.frontier_objectives)}",
        f"maps = {list(args.maps)}, slips = {list(args.slips)}, gamma = {args.gamma}",
        "",
        "## Pareto Frontier",
        "",
        markdown_table(frontier_rows, frontier_columns),
        "",
        "## Best By Family",
        "",
        markdown_table(family_rows, frontier_columns),
        "",
        "## All Rows",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep k for tabular option baselines and extract a Pareto frontier.")
    parser.add_argument("--maps", nargs="+", default=["maze"])
    parser.add_argument("--slips", type=float, nargs="+", default=[0.05])
    parser.add_argument("--families", nargs="+", default=list(DEFAULT_FAMILIES))
    parser.add_argument("--k-values", type=int, nargs="+", default=list(DEFAULT_K_VALUES))
    parser.add_argument("--frontier-objectives", nargs="+", default=list(DEFAULT_OBJECTIVES))
    parser.add_argument("--primary-metric", default="occupancy_struct_hidden_distinct")
    parser.add_argument("--include-endpoints", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-graph-rd", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-dense", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-rollouts", type=int, default=100)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument("--max-option-steps", type=int, default=0)
    parser.add_argument("--audit-lens", default="turn_articulation")
    parser.add_argument("--audit-top-fraction", type=float, default=0.15)
    parser.add_argument("--soft-kind", default="combined")
    parser.add_argument("--soft-top-fraction", type=float, default=0.15)
    parser.add_argument("--local-horizon", type=float, default=999.0)
    parser.add_argument("--hidden-threshold", type=float, default=1e-6)
    parser.add_argument("--soft-threshold", type=float, default=3.0)
    parser.add_argument("--residual-threshold", type=float, default=0.5)
    parser.add_argument("--residual-threshold-mode", default="struct_distinct")
    parser.add_argument("--residual-reward-weight", type=float, default=0.05)
    parser.add_argument("--residual-hit-weight", type=float, default=0.0)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/option_baseline_frontier_maze_slip005"),
    )
    args = parser.parse_args()

    args.methods = expand_methods(
        families=args.families,
        k_values=args.k_values,
        include_endpoints=args.include_endpoints,
        include_graph_rd=args.include_graph_rd,
        include_dense=args.include_dense,
    )
    rows: List[Dict[str, object]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        for slip in args.slips:
            for method in args.methods:
                rows.append(evaluate_method(method, map_name, MAPS[map_name], slip, args))

    rows = mark_pareto_frontier(rows, objectives=args.frontier_objectives)
    frontier_rows = [row for row in rows if bool(row["pareto_frontier"])]
    frontier_rows = sorted(
        frontier_rows,
        key=lambda row: (
            str(row["map"]),
            float(row["slip"]),
            finite_float(row, "description_length_proxy"),
            finite_float(row, "occupancy_struct_hidden_distinct"),
        ),
    )
    rows = sorted(
        rows,
        key=lambda row: (
            str(row["map"]),
            float(row["slip"]),
            family_name(str(row["method"])),
            int(row["n_boundary"]),
            str(row["method"]),
        ),
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "frontier_all.csv", rows)
    write_csv_all_fields(args.out_dir / "frontier_pareto.csv", frontier_rows)
    (args.out_dir / "frontier_all.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, frontier_rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
