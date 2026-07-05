#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

import thread_limits  # noqa: F401

from compression_experiment_utils import scaled_rows
from run_first_boundary_targeted import markdown_table
from run_group_constrained_adaptive_table import (
    finite_float,
    group_context,
    run_method,
)
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def median(values: Sequence[float]) -> float:
    vals = sorted(value for value in values if math.isfinite(value))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def bool_rate(values: Sequence[object]) -> float:
    vals = [str(value).lower() in {"true", "1", "yes"} for value in values]
    return sum(1 for value in vals if value) / max(1, len(vals))


def build_summary_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[str, List[Mapping[str, object]]] = {}
    for row in rows:
        if row.get("error"):
            continue
        grouped.setdefault(str(row.get("method", "")), []).append(row)
    summary: List[Dict[str, object]] = []
    for method, group in sorted(grouped.items()):
        summary.append(
            {
                "method": method,
                "n_rows": len(group),
                "feasible_rate": bool_rate([row.get("group_all_feasible") for row in group]),
                "median_n_boundary": median([finite_float(row.get("n_boundary")) for row in group]),
                "median_state_compression_ratio": median(
                    [finite_float(row.get("state_compression_ratio")) for row in group]
                ),
                "median_selection_time_sec": median([finite_float(row.get("selection_time_sec")) for row in group]),
                "median_kernel_time_sec": median([finite_float(row.get("kernel_time_sec")) for row in group]),
                "median_total_speedup": median([finite_float(row.get("total_speedup")) for row in group]),
                "median_break_even_tasks": median([finite_float(row.get("break_even_tasks")) for row in group]),
                "max_group_total_violation": max(
                    (finite_float(row.get("group_total_violation"), 0.0) for row in group),
                    default=float("nan"),
                ),
                "max_start_gap": max(
                    (finite_float(row.get("start_gap"), 0.0) for row in group),
                    default=float("nan"),
                ),
                "max_tail_bound": max(
                    (finite_float(row.get("first_hit_tail_bound_max"), 0.0) for row in group),
                    default=float("nan"),
                ),
            }
        )
    return summary


def write_report(
    rows: Sequence[Mapping[str, object]],
    summary_rows: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
    elapsed: float,
) -> None:
    row_columns = [
        "map",
        "maze_seed",
        "slip",
        "method",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "group_all_feasible",
        "group_total_violation",
        "selection_time_sec",
        "delta_backend",
        "probe_green_kernel_time_sec",
        "active_weight_time_sec",
        "kernel_time_sec",
        "smdp_solve_time_sec",
        "planning_speedup",
        "total_speedup",
        "break_even_tasks",
        "start_gap",
        "first_hit_tail_bound_max",
        "stop_reason",
        "error",
    ]
    summary_columns = [
        "method",
        "n_rows",
        "feasible_rate",
        "median_n_boundary",
        "median_state_compression_ratio",
        "median_selection_time_sec",
        "median_kernel_time_sec",
        "median_total_speedup",
        "median_break_even_tasks",
        "max_group_total_violation",
        "max_start_gap",
        "max_tail_bound",
    ]
    ok_rows = [row for row in rows if not row.get("error")]
    lines = [
        "# Random Maze Generalization",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"sizes = {list(args.sizes)}",
        f"seeds = {list(args.maze_seeds)}",
        f"slips = {list(args.slips)}",
        f"methods = {list(args.methods)}",
        f"elapsed_sec = {elapsed:.3f}",
        "",
        "This is a topology-family stress test: each row uses a fresh DFS maze instance, then runs the same group-constrained boundary selector and compressed graph-SMDP evaluation.",
        "",
        f"- completed rows: `{len(ok_rows)}/{len(rows)}`",
        "",
        "## Method Summary",
        "",
        markdown_table(summary_rows, summary_columns) if summary_rows else "_No successful rows._",
        "",
        "## Rows",
        "",
        markdown_table([{col: row.get(col, "") for col in row_columns} for row in rows], row_columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stress-test group-constrained RD graph extraction on random DFS maze families."
    )
    parser.add_argument("--sizes", nargs="+", type=int, default=[9, 11])
    parser.add_argument("--maze-seeds", nargs="+", type=int, default=[0, 1])
    parser.add_argument("--slips", nargs="+", type=float, default=[0.05])
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=[
            "endpoints",
            "group_constrained",
            "group_constrained_operator",
            "group_constrained_incremental",
        ],
        default=["endpoints", "group_constrained_operator", "group_constrained_incremental"],
    )
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument(
        "--lens-groups",
        nargs="+",
        default=[
            "topology:junction,bottleneck,turn_articulation,betweenness",
            "value:value_gradient",
            "stochastic:transition_entropy",
        ],
    )
    parser.add_argument("--test-probes", nargs="+", default=["combined", "value_gradient", "transition_entropy"])
    parser.add_argument(
        "--include-test-probes",
        action="store_true",
        help="Also recompute held-out probe distortions when scoring final boundaries.",
    )
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--budget-frac", type=float, default=0.25)
    parser.add_argument("--group-risk-kind", choices=["mean", "cvar", "max"], default="cvar")
    parser.add_argument("--score-mode", choices=["reduction", "reduction_per_rate", "lexicographic"], default="reduction")
    parser.add_argument("--rate-tie-break", type=float, default=1e-4)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-splits", type=int, default=5)
    parser.add_argument("--beam-width", type=int, default=2)
    parser.add_argument("--beam-expand", type=int, default=4)
    parser.add_argument("--disable-probe-cache", action="store_true")
    parser.add_argument("--delta-backend", choices=["operator", "insertion_score"], default="operator")
    parser.add_argument("--first-hit-mode", choices=["exact", "truncated", "adaptive"], default="adaptive")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=512)
    parser.add_argument("--first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/random_maze_generalization"))
    args = parser.parse_args()

    started = time.perf_counter()
    rows: List[Dict[str, object]] = []
    for size in args.sizes:
        for maze_seed in args.maze_seeds:
            map_rows = scaled_rows("maze", size, seed=maze_seed)
            map_label = f"random_maze_{size}_seed{maze_seed}"
            for slip in args.slips:
                try:
                    _grid, lens_groups, recipe, basis, endpoint_boundary, budgets, context_info = group_context(
                        map_label=map_label,
                        rows=map_rows,
                        slip=slip,
                        args=args,
                    )
                    for method in args.methods:
                        row = run_method(
                            family="random_maze",
                            size=size,
                            map_label=map_label,
                            rows=map_rows,
                            slip=slip,
                            method=method,
                            lens_groups=lens_groups,
                            recipe=recipe,
                            basis=basis,
                            endpoint_boundary=endpoint_boundary,
                            budgets=budgets,
                            context_info=context_info,
                            args=args,
                        )
                        row["maze_seed"] = maze_seed
                        rows.append(row)
                except Exception as exc:
                    if not args.continue_on_error:
                        raise
                    rows.append(
                        {
                            "map_family": "random_maze",
                            "map_size": size,
                            "map": map_label,
                            "maze_seed": maze_seed,
                            "slip": slip,
                            "method": "",
                            "error": repr(exc),
                        }
                    )

    summary_rows = build_summary_rows(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "random_maze_generalization.csv", rows)
    write_csv_all_fields(args.out_dir / "random_maze_generalization_summary.csv", summary_rows)
    (args.out_dir / "random_maze_generalization.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, summary_rows, args.out_dir / "summary.md", args, time.perf_counter() - started)


if __name__ == "__main__":
    main()
