#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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
        f"shard = {args.shard_index}/{args.num_shards}",
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


def read_existing_rows(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def completed_jobs(rows: Sequence[Mapping[str, object]]) -> set[tuple[str, str, str, str]]:
    done: set[tuple[str, str, str, str]] = set()
    for row in rows:
        key = (
            str(row.get("map", "")),
            str(row.get("maze_seed", "")),
            str(row.get("slip", "")),
            str(row.get("method", "")),
        )
        if all(key):
            done.add(key)
    return done


def write_outputs(rows: Sequence[Mapping[str, object]], args: argparse.Namespace, elapsed: float) -> None:
    summary_rows = build_summary_rows(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "random_maze_generalization.csv", rows)
    write_csv_all_fields(args.out_dir / "random_maze_generalization_summary.csv", summary_rows)
    (args.out_dir / "random_maze_generalization.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, summary_rows, args.out_dir / "summary.md", args, elapsed)


def progress_path(args: argparse.Namespace) -> Path:
    return args.progress_log or (args.out_dir / "progress.jsonl")


def log_progress(args: argparse.Namespace, event: str, **payload: object) -> None:
    path = progress_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.time(),
        "event": event,
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        **payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(rec, default=json_default) + "\n")


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
            "one_shot_rd",
            "one_shot_group_fd",
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
    parser.add_argument("--one-shot-threshold", type=float, default=0.15)
    parser.add_argument("--one-shot-steps", type=int, default=256)
    parser.add_argument("--one-shot-tail-tol", type=float, default=1e-6)
    parser.add_argument("--one-shot-probe-count", type=int, default=None)
    parser.add_argument("--one-shot-min-channel-support", type=int, default=2)
    parser.add_argument("--one-shot-exclusion-radius", type=int, default=1)
    parser.add_argument(
        "--one-shot-candidate-universe",
        choices=["all", "turn_articulation"],
        default="turn_articulation",
    )
    parser.add_argument("--beam-width", type=int, default=2)
    parser.add_argument("--beam-expand", type=int, default=4)
    parser.add_argument("--disable-probe-cache", action="store_true")
    parser.add_argument("--delta-backend", choices=["operator", "insertion_score"], default="operator")
    parser.add_argument("--first-hit-mode", choices=["exact", "truncated", "adaptive"], default="adaptive")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=512)
    parser.add_argument("--first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--progress-log", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/random_maze_generalization"))
    args = parser.parse_args()
    if args.num_shards < 1:
        raise ValueError("--num-shards must be >= 1")
    if args.shard_index < 0 or args.shard_index >= args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    started = time.perf_counter()
    jobs = [
        (size, maze_seed, slip, method)
        for size in args.sizes
        for maze_seed in args.maze_seeds
        for slip in args.slips
        for method in args.methods
    ]
    selected_jobs = [
        (job_index, *job)
        for job_index, job in enumerate(jobs)
        if job_index % args.num_shards == args.shard_index
    ]
    by_context: Dict[tuple[int, int, float], List[tuple[int, str]]] = {}
    for job_index, size, maze_seed, slip, method in selected_jobs:
        by_context.setdefault((size, maze_seed, slip), []).append((job_index, method))

    rows: List[Dict[str, object]] = (
        read_existing_rows(args.out_dir / "random_maze_generalization.csv") if args.resume else []
    )
    done = completed_jobs(rows)
    log_progress(
        args,
        "start",
        selected_jobs=len(selected_jobs),
        total_jobs=len(jobs),
        resumed_completed_jobs=len(done),
    )
    for context_index, ((size, maze_seed, slip), indexed_methods) in enumerate(
        sorted(by_context.items()), start=1
    ):
        map_rows = scaled_rows("maze", size, seed=maze_seed)
        map_label = f"random_maze_{size}_seed{maze_seed}"
        pending_methods = [
            (job_index, method)
            for job_index, method in indexed_methods
            if not (args.resume and (map_label, str(maze_seed), str(slip), method) in done)
        ]
        for job_index, method in indexed_methods:
            if args.resume and (map_label, str(maze_seed), str(slip), method) in done:
                log_progress(
                    args,
                    "skip_completed",
                    context_index=context_index,
                    selected_contexts=len(by_context),
                    job_index=job_index,
                    map=map_label,
                    maze_seed=maze_seed,
                    slip=slip,
                    method=method,
                )
        if not pending_methods:
            continue
        context_started = time.perf_counter()
        try:
            _grid, lens_groups, recipe, basis, endpoint_boundary, budgets, context_info = group_context(
                map_label=map_label,
                rows=map_rows,
                slip=slip,
                args=args,
            )
            for job_index, method in pending_methods:
                job_started = time.perf_counter()
                try:
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
                    done.add((map_label, str(maze_seed), str(slip), method))
                    log_progress(
                        args,
                        "job_done",
                        context_index=context_index,
                        selected_contexts=len(by_context),
                        job_index=job_index,
                        map=map_label,
                        maze_seed=maze_seed,
                        slip=slip,
                        method=method,
                        elapsed_sec=time.perf_counter() - job_started,
                    )
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
                            "method": method,
                            "error": repr(exc),
                        }
                    )
                    done.add((map_label, str(maze_seed), str(slip), method))
                    log_progress(
                        args,
                        "job_error",
                        context_index=context_index,
                        selected_contexts=len(by_context),
                        job_index=job_index,
                        map=map_label,
                        maze_seed=maze_seed,
                        slip=slip,
                        method=method,
                        elapsed_sec=time.perf_counter() - job_started,
                        error=repr(exc),
                    )
                write_outputs(rows, args, time.perf_counter() - started)
        except Exception as exc:
            if not args.continue_on_error:
                raise
            for job_index, method in pending_methods:
                rows.append(
                    {
                        "map_family": "random_maze",
                        "map_size": size,
                        "map": map_label,
                        "maze_seed": maze_seed,
                        "slip": slip,
                        "method": method,
                        "error": repr(exc),
                    }
                )
                done.add((map_label, str(maze_seed), str(slip), method))
                log_progress(
                    args,
                    "context_error",
                    context_index=context_index,
                    selected_contexts=len(by_context),
                    job_index=job_index,
                    map=map_label,
                    maze_seed=maze_seed,
                    slip=slip,
                    method=method,
                    elapsed_sec=time.perf_counter() - context_started,
                    error=repr(exc),
                )
            write_outputs(rows, args, time.perf_counter() - started)
    write_outputs(rows, args, time.perf_counter() - started)
    log_progress(args, "done", rows=len(rows), selected_jobs=len(selected_jobs), total_jobs=len(jobs))


if __name__ == "__main__":
    main()
