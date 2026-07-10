#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import build_compressed_model_measured, parse_map_specs, scaled_rows
from one_shot_rd_operator import OneShotRDResult, apply_one_shot_rd_operator
from planner_baselines import build_sparse_grid_model, sparse_value_iteration_measured
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def median(values: Iterable[float]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(finite)) if finite else float("nan")


def maximum(values: Iterable[float]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return max(finite) if finite else float("nan")


def bool_text(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def threshold_label(threshold: float) -> str:
    return f"one_shot_rd_t{threshold:.2f}".replace(".", "p")


def jaccard(left: Sequence[int], right: Sequence[int]) -> float:
    left_set = set(int(state) for state in left)
    right_set = set(int(state) for state in right)
    union = left_set.union(right_set)
    return len(left_set.intersection(right_set)) / max(1, len(union))


def sparse_planner_reference(
    grid: GridWorld,
    slip: float,
    gamma: float,
    repeats: int,
) -> Dict[str, object]:
    goal = grid.symbol_states("G")[0]
    model = build_sparse_grid_model(grid, goal_state=goal, slip=slip)
    runs = [sparse_value_iteration_measured(model, gamma=gamma) for _ in range(max(1, repeats))]
    return {
        "time_sec": median(finite_float(run["time_sec"]) for run in runs),
        "backup_count": int(median(finite_float(run["backup_count"]) for run in runs)),
        "iterations": int(median(finite_float(run["iterations"]) for run in runs)),
        "residual_max": max(finite_float(run["bellman_residual"], 0.0) for run in runs),
    }


def row_from_model(
    family: str,
    size: int,
    map_label: str,
    slip: float,
    method: str,
    model: Mapping[str, object],
    planner: Mapping[str, object],
    operator: OneShotRDResult | None,
) -> Dict[str, object]:
    boundary = [int(state) for state in model["boundary"]]
    construction = finite_float(model.get("construction_time_sec"), 0.0)
    kernel = finite_float(model.get("kernel_time_sec"), 0.0)
    graph_solve = finite_float(model["smdp_result"].get("time_sec"), 0.0)  # type: ignore[union-attr]
    total = construction + kernel + graph_solve
    sparse_time = finite_float(planner.get("time_sec"), 0.0)
    row: Dict[str, object] = {
        "map_family": family,
        "map_size": int(size),
        "map": map_label,
        "slip": float(slip),
        "method": method,
        "n_states": int(model["n_states"]),
        "n_boundary": len(boundary),
        "state_compression_ratio": float(model["n_states"]) / max(1, len(boundary)),
        "boundary": json.dumps(boundary),
        "iterative_candidate_recompute": method in {"graph_rd_surrogate_joint", "graph_rd_joint"},
        "final_graph_kernel_build_count": 1,
        "selection_time_sec": construction,
        "final_kernel_time_sec": kernel,
        "graph_solve_time_sec": graph_solve,
        "total_time_sec": total,
        "sparse_vi_time_sec": sparse_time,
        "operator_speedup_vs_sparse_vi": sparse_time / max(1e-12, construction),
        "planning_speedup_vs_sparse_vi": sparse_time / max(1e-12, graph_solve),
        "total_speedup_vs_sparse_vi": sparse_time / max(1e-12, total),
        "start_gap": finite_float(model.get("start_gap")),
        "normalized_start_gap": finite_float(model.get("normalized_start_gap")),
        "value_gap_max": finite_float(model.get("value_gap_max")),
        "normalized_value_gap_max": finite_float(model.get("normalized_value_gap_max")),
        "D_occ": finite_float(model.get("occupancy_struct_hidden_distinct")),
        "D_model": finite_float(model.get("occupancy_model_residual")),
        "D_audit_cvar95": finite_float(model.get("struct_hidden_distinct_cvar95")),
        "error": "",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    if operator is not None:
        row.update(operator.timings)
        row.update(
            {
                "n_probe_anchors": len(operator.probe_anchors),
                "n_operator_selected": len(operator.selected_states),
                "probe_anchors": json.dumps(operator.probe_anchors),
                "selected_states": json.dumps(operator.selected_states),
                "selection_reasons": json.dumps(operator.selection_reasons, sort_keys=True),
                "operator_used_steps_max": operator.diagnostics["used_steps_max"],
                "operator_frontier_max": operator.diagnostics["frontier_max"],
                "operator_message_passing_sparse": True,
                "n_green_response_passes": operator.diagnostics["n_green_response_passes"],
                "n_candidate_insertion_evaluations": 0,
                "n_beam_expansions": 0,
            }
        )
    return row


def run_one_shot(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    threshold: float,
    planner: Mapping[str, object],
    args: argparse.Namespace,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    operator = apply_one_shot_rd_operator(
        grid=grid,
        slip=slip,
        gamma=args.gamma,
        mandatory_boundary=endpoint_boundary_states(grid),
        probe_count=args.probe_count,
        truncation_steps=args.operator_truncation_steps,
        tail_tol=args.operator_tail_tol,
        max_splits=args.max_splits,
        channel_threshold=threshold,
        min_channel_support=args.min_channel_support,
        mandatory_exclusion_radius=args.mandatory_exclusion_radius,
        candidate_universe=args.candidate_universe,
        include_probe_anchors=args.include_probe_anchors,
    )
    method = threshold_label(threshold)
    model = build_compressed_model_measured(
        map_label=map_label,
        rows=rows,
        method_spec=method,
        gamma=args.gamma,
        slip=slip,
        seed=args.seed,
        max_splits=args.max_splits,
        soft_kind="none",
        local_horizon=args.local_horizon,
        boundary_override=operator.boundary,
        constructor_override={**operator.diagnostics, **operator.timings},
        construction_time_override=operator.timings["total_operator_time_sec"],
        first_hit_mode=args.final_first_hit_mode,
        first_hit_truncation_steps=args.final_first_hit_steps,
        first_hit_tail_tol=args.final_first_hit_tail_tol,
    )
    return row_from_model(family, size, map_label, slip, method, model, planner, operator)


def run_one_shot_operator_only(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    threshold: float,
    args: argparse.Namespace,
) -> Dict[str, object]:
    """Measure boundary extraction without building graph kernels or solving either MDP."""

    grid = GridWorld(rows)
    operator = apply_one_shot_rd_operator(
        grid=grid,
        slip=slip,
        gamma=args.gamma,
        mandatory_boundary=endpoint_boundary_states(grid),
        probe_count=args.probe_count,
        truncation_steps=args.operator_truncation_steps,
        tail_tol=args.operator_tail_tol,
        max_splits=args.max_splits,
        channel_threshold=threshold,
        min_channel_support=args.min_channel_support,
        mandatory_exclusion_radius=args.mandatory_exclusion_radius,
        candidate_universe=args.candidate_universe,
        include_probe_anchors=args.include_probe_anchors,
    )
    method = threshold_label(threshold)
    row: Dict[str, object] = {
        "map_family": family,
        "map_size": int(size),
        "map": map_label,
        "slip": float(slip),
        "method": method,
        "benchmark_mode": "operator_only",
        "n_states": grid.n_states,
        "n_boundary": len(operator.boundary),
        "state_compression_ratio": grid.n_states / max(1, len(operator.boundary)),
        "boundary": json.dumps(operator.boundary),
        "iterative_candidate_recompute": False,
        "final_graph_kernel_build_count": 0,
        "selection_time_sec": operator.timings["total_operator_time_sec"],
        "final_kernel_time_sec": float("nan"),
        "graph_solve_time_sec": float("nan"),
        "total_time_sec": float("nan"),
        "sparse_vi_time_sec": float("nan"),
        "operator_speedup_vs_sparse_vi": float("nan"),
        "planning_speedup_vs_sparse_vi": float("nan"),
        "total_speedup_vs_sparse_vi": float("nan"),
        "start_gap": float("nan"),
        "normalized_start_gap": float("nan"),
        "value_gap_max": float("nan"),
        "normalized_value_gap_max": float("nan"),
        "D_occ": float("nan"),
        "D_model": float("nan"),
        "D_audit_cvar95": float("nan"),
        "n_probe_anchors": len(operator.probe_anchors),
        "n_operator_selected": len(operator.selected_states),
        "probe_anchors": json.dumps(operator.probe_anchors),
        "selected_states": json.dumps(operator.selected_states),
        "selection_reasons": json.dumps(operator.selection_reasons, sort_keys=True),
        "operator_used_steps_max": operator.diagnostics["used_steps_max"],
        "operator_frontier_max": operator.diagnostics["frontier_max"],
        "operator_message_passing_sparse": True,
        "n_green_response_passes": operator.diagnostics["n_green_response_passes"],
        "n_candidate_insertion_evaluations": 0,
        "n_beam_expansions": 0,
        "error": "",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    row.update(operator.timings)
    return row


def run_baseline(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    method: str,
    planner: Mapping[str, object],
    args: argparse.Namespace,
) -> Dict[str, object]:
    model = build_compressed_model_measured(
        map_label=map_label,
        rows=rows,
        method_spec=method,
        gamma=args.gamma,
        slip=slip,
        seed=args.seed,
        max_splits=args.max_splits,
        soft_kind="none",
        local_horizon=args.local_horizon,
        first_hit_mode=args.final_first_hit_mode,
        first_hit_truncation_steps=args.final_first_hit_steps,
        first_hit_tail_tol=args.final_first_hit_tail_tol,
    )
    return row_from_model(family, size, map_label, slip, method, model, planner, None)


def attach_reference_comparisons(
    rows: List[Dict[str, object]],
    historical_rows: Sequence[Mapping[str, object]] = (),
) -> None:
    historical_by_context = {
        (str(row.get("map")), float(row.get("slip", 0.0))): row
        for row in historical_rows
        if row.get("method_spec") == "graph_rd_surrogate_joint" and not row.get("error")
    }
    groups: Dict[Tuple[str, float], List[Dict[str, object]]] = {}
    for row in rows:
        if row.get("error"):
            continue
        groups.setdefault((str(row["map"]), float(row["slip"])), []).append(row)
    for group in groups.values():
        iterative = next((row for row in group if row["method"] == "graph_rd_surrogate_joint"), None)
        exact = next((row for row in group if row["method"] == "graph_rd_joint"), None)
        for row in group:
            boundary = json.loads(str(row["boundary"]))
            if iterative is not None:
                iterative_boundary = json.loads(str(iterative["boundary"]))
                row["boundary_jaccard_vs_iterative"] = jaccard(boundary, iterative_boundary)
                row["selection_speedup_vs_iterative"] = finite_float(iterative["selection_time_sec"]) / max(
                    1e-12, finite_float(row["selection_time_sec"])
                )
                row_total = finite_float(row.get("total_time_sec"))
                if math.isfinite(row_total):
                    row["total_speedup_vs_iterative"] = finite_float(
                        iterative["total_time_sec"]
                    ) / max(1e-12, row_total)
            else:
                historical = historical_by_context.get((str(row["map"]), float(row["slip"])))
                if historical is not None:
                    historical_selection = finite_float(historical.get("construction_time_sec"))
                    historical_total = finite_float(historical.get("compressed_total_time_sec"))
                    row["reference_iterative_n_boundary"] = finite_float(historical.get("n_boundary"))
                    row["reference_iterative_D_occ"] = finite_float(
                        historical.get("occupancy_struct_hidden_distinct")
                    )
                    row["selection_speedup_vs_iterative"] = historical_selection / max(
                        1e-12, finite_float(row["selection_time_sec"])
                    )
                    row_total = finite_float(row.get("total_time_sec"))
                    if math.isfinite(row_total):
                        row["total_speedup_vs_iterative"] = historical_total / max(
                            1e-12, row_total
                        )
            if exact is not None:
                exact_boundary = json.loads(str(exact["boundary"]))
                row["boundary_jaccard_vs_exact_search"] = jaccard(boundary, exact_boundary)
                row["selection_speedup_vs_exact_search"] = finite_float(
                    exact["selection_time_sec"]
                ) / max(1e-12, finite_float(row["selection_time_sec"]))
                row_total = finite_float(row.get("total_time_sec"))
                if math.isfinite(row_total):
                    row["total_speedup_vs_exact_search"] = finite_float(
                        exact["total_time_sec"]
                    ) / max(1e-12, row_total)


def summarize(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    summaries: List[Dict[str, object]] = []
    methods = sorted({str(row.get("method")) for row in rows if not row.get("error")})
    for method in methods:
        group = [row for row in rows if row.get("method") == method and not row.get("error")]
        summaries.append(
            {
                "method": method,
                "n_rows": len(group),
                "median_n_boundary": median(finite_float(row.get("n_boundary")) for row in group),
                "median_state_compression": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "median_selection_time_sec": median(
                    finite_float(row.get("selection_time_sec")) for row in group
                ),
                "median_final_kernel_time_sec": median(
                    finite_float(row.get("final_kernel_time_sec")) for row in group
                ),
                "median_total_time_sec": median(finite_float(row.get("total_time_sec")) for row in group),
                "median_total_speedup_vs_sparse_vi": median(
                    finite_float(row.get("total_speedup_vs_sparse_vi")) for row in group
                ),
                "median_selection_speedup_vs_iterative": median(
                    finite_float(row.get("selection_speedup_vs_iterative")) for row in group
                ),
                "median_total_speedup_vs_iterative": median(
                    finite_float(row.get("total_speedup_vs_iterative")) for row in group
                ),
                "median_selection_speedup_vs_exact_search": median(
                    finite_float(row.get("selection_speedup_vs_exact_search")) for row in group
                ),
                "median_total_speedup_vs_exact_search": median(
                    finite_float(row.get("total_speedup_vs_exact_search")) for row in group
                ),
                "max_normalized_start_gap": maximum(
                    finite_float(row.get("normalized_start_gap")) for row in group
                ),
                "max_normalized_value_gap": maximum(
                    finite_float(row.get("normalized_value_gap_max")) for row in group
                ),
                "median_D_occ": median(finite_float(row.get("D_occ")) for row in group),
                "median_D_audit_cvar95": median(
                    finite_float(row.get("D_audit_cvar95")) for row in group
                ),
                "median_boundary_jaccard_vs_iterative": median(
                    finite_float(row.get("boundary_jaccard_vs_iterative")) for row in group
                ),
            }
        )
    return summaries


def write_report(
    rows: Sequence[Mapping[str, object]],
    summary_rows: Sequence[Mapping[str, object]],
    args: argparse.Namespace,
) -> None:
    lines = [
        "# One-Shot RD Green Operator",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "The one-shot methods freeze the mandatory boundary and probe basis, run one truncated sparse Green pass, apply all RD channels once, and threshold once. They never insert a candidate or recompute the operator. In operator-only mode the benchmark stops there; otherwise it constructs final graph kernels exactly once.",
        "",
        f"operator_only = {args.operator_only}, thresholds = {args.thresholds}, probe_count = {args.probe_count}, operator_steps = {args.operator_truncation_steps}, max_splits = {args.max_splits}",
        "",
        "## Method Aggregate",
        "",
    ]
    columns = [
        "method",
        "n_rows",
        "median_n_boundary",
        "median_state_compression",
        "median_selection_time_sec",
        "median_final_kernel_time_sec",
        "median_total_speedup_vs_sparse_vi",
        "median_selection_speedup_vs_iterative",
        "median_total_speedup_vs_iterative",
        "median_selection_speedup_vs_exact_search",
        "median_total_speedup_vs_exact_search",
        "max_normalized_start_gap",
        "max_normalized_value_gap",
        "median_D_occ",
        "median_D_audit_cvar95",
        "median_boundary_jaccard_vs_iterative",
    ]
    lines.append(markdown_table(summary_rows, columns))
    lines += ["", "## Rows", ""]
    detail_columns = [
        "map",
        "slip",
        "method",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "selection_time_sec",
        "final_kernel_time_sec",
        "graph_solve_time_sec",
        "total_speedup_vs_sparse_vi",
        "selection_speedup_vs_iterative",
        "normalized_start_gap",
        "normalized_value_gap_max",
        "D_occ",
        "D_audit_cvar95",
        "boundary_jaccard_vs_iterative",
    ]
    lines.append(
        markdown_table(
            [
                {column: row.get(column, "") for column in detail_columns}
                for row in rows
                if not row.get("error")
            ],
            detail_columns,
        )
    )
    errors = [row for row in rows if row.get("error")]
    if errors:
        error_columns = ["map", "slip", "method", "error"]
        lines += [
            "",
            "## Errors",
            "",
            markdown_table(
                [{column: row.get(column, "") for column in error_columns} for row in errors],
                error_columns,
            ),
        ]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_completed(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark a one-pass sparse RD Green graph operator.")
    parser.add_argument(
        "--map-specs",
        nargs="*",
        default=["corridor:32", "open_room:10", "four_rooms:11", "maze:13"],
    )
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05, 0.1])
    parser.add_argument("--random-maze-sizes", type=int, nargs="*", default=[])
    parser.add_argument("--maze-seeds", type=int, nargs="+", default=list(range(5)))
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.1, 0.15, 0.2])
    parser.add_argument(
        "--baselines",
        nargs="*",
        default=["endpoints", "graph_rd_surrogate_joint"],
    )
    parser.add_argument(
        "--operator-only",
        action="store_true",
        help="Stop after one-shot boundary extraction; do not build final kernels or solve either MDP.",
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--probe-count", type=int, default=None)
    parser.add_argument("--operator-truncation-steps", type=int, default=256)
    parser.add_argument("--operator-tail-tol", type=float, default=1e-6)
    parser.add_argument("--channel-threshold", type=float, default=None)
    parser.add_argument("--min-channel-support", type=int, default=2)
    parser.add_argument("--mandatory-exclusion-radius", type=int, default=1)
    parser.add_argument("--candidate-universe", choices=["all", "turn_articulation"], default="turn_articulation")
    parser.add_argument("--include-probe-anchors", action="store_true")
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--local-horizon", type=float, default=1e9)
    parser.add_argument("--final-first-hit-mode", choices=["exact", "truncated", "adaptive"], default="adaptive")
    parser.add_argument("--final-first-hit-steps", type=int, default=128)
    parser.add_argument("--final-first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--planner-repeats", type=int, default=3)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--iterative-reference-csv",
        type=Path,
        default=Path(
            "experiments/output/large_scale_compression_adaptive/"
            "large_scale_compression.csv"
        ),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/one_shot_rd_operator"),
    )
    args = parser.parse_args()
    if args.channel_threshold is not None:
        args.thresholds = [float(args.channel_threshold)]
    if args.operator_only:
        args.baselines = []
    if not 0 <= args.shard_index < args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    contexts = list(parse_map_specs(args.map_specs))
    contexts.extend(
        (
            "random_maze",
            int(size),
            f"random_maze_{int(size)}_seed{int(seed)}",
            scaled_rows("maze", int(size), seed=int(seed)),
        )
        for size in args.random_maze_sizes
        for seed in args.maze_seeds
    )
    all_jobs: List[Tuple[str, int, str, Tuple[str, ...], float, str, float | None]] = []
    for family, size, map_label, rows in contexts:
        for slip in args.slips:
            for threshold in args.thresholds:
                all_jobs.append((family, size, map_label, rows, slip, threshold_label(threshold), threshold))
            for baseline in args.baselines:
                all_jobs.append((family, size, map_label, rows, slip, baseline, None))
    jobs = [job for index, job in enumerate(all_jobs) if index % args.num_shards == args.shard_index]

    output_csv = args.out_dir / "one_shot_rd_operator.csv"
    existing = load_completed(output_csv) if args.resume else []
    completed = {
        (str(row.get("map")), str(row.get("slip")), str(row.get("method")))
        for row in existing
        if not row.get("error")
    }
    rows_out: List[Dict[str, object]] = list(existing)
    planner_cache: Dict[Tuple[str, float], Dict[str, object]] = {}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.out_dir / "progress.jsonl"

    for family, size, map_label, map_rows, slip, method, threshold in jobs:
        key = (map_label, str(float(slip)), method)
        if key in completed:
            continue
        try:
            planner_key = (map_label, float(slip))
            if args.operator_only:
                if threshold is None:
                    continue
                row = run_one_shot_operator_only(
                    family, size, map_label, map_rows, slip, threshold, args
                )
            else:
                grid = GridWorld(map_rows)
                if planner_key not in planner_cache:
                    planner_cache[planner_key] = sparse_planner_reference(
                        grid, slip=slip, gamma=args.gamma, repeats=args.planner_repeats
                    )
            if not args.operator_only and threshold is None:
                row = run_baseline(
                    family, size, map_label, map_rows, slip, method, planner_cache[planner_key], args
                )
            elif not args.operator_only:
                row = run_one_shot(
                    family,
                    size,
                    map_label,
                    map_rows,
                    slip,
                    threshold,
                    planner_cache[planner_key],
                    args,
                )
        except Exception as exc:
            if not args.continue_on_error:
                raise
            row = {
                "map_family": family,
                "map_size": size,
                "map": map_label,
                "slip": slip,
                "method": method,
                "error": repr(exc),
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        rows_out.append(row)
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"map": map_label, "slip": slip, "method": method, "error": row.get("error", "")}) + "\n")
        write_csv_all_fields(output_csv, rows_out)

    historical_rows: List[Dict[str, object]] = []
    if args.iterative_reference_csv.exists():
        historical_rows = load_completed(args.iterative_reference_csv)
    attach_reference_comparisons(rows_out, historical_rows=historical_rows)
    summary_rows = summarize(rows_out)
    write_csv_all_fields(output_csv, rows_out)
    write_csv_all_fields(args.out_dir / "one_shot_rd_operator_summary.csv", summary_rows)
    (args.out_dir / "one_shot_rd_operator.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows_out, summary_rows, args)


if __name__ == "__main__":
    main()
