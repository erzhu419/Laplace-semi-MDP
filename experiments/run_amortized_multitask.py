#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import GridWorld
from compression_experiment_utils import (
    full_value_iteration_measured,
    kernel_nnz,
    parse_map_specs,
    resolve_method_spec,
    smdp_value_iteration_measured,
    transition_nnz_proxy,
)
from run_first_boundary_targeted import build_first_boundary_reductions, markdown_table
from run_option_algorithm_comparison import construct_boundary, json_default, write_csv_all_fields


def choose_task_goals(grid: GridWorld, max_tasks: int) -> List[int]:
    start = grid.symbol_states("S")[0]
    original_goals = grid.symbol_states("G")
    candidates = [state for state in range(grid.n_states) if state != start]
    ordered: List[int] = []
    for goal in original_goals:
        if goal in candidates and goal not in ordered:
            ordered.append(goal)
    remaining = [state for state in candidates if state not in ordered]
    if max_tasks > len(ordered) and remaining:
        take = min(max_tasks - len(ordered), len(remaining))
        indices = np.linspace(0, len(remaining) - 1, num=take, dtype=int).tolist()
        for idx in indices:
            state = int(remaining[idx])
            if state not in ordered:
                ordered.append(state)
    return ordered[:max_tasks]


def choose_boundary_task_goals(grid: GridWorld, boundary: Sequence[int], max_tasks: int) -> List[int]:
    start = grid.symbol_states("S")[0]
    original_goals = grid.symbol_states("G")
    candidates = [int(state) for state in sorted(set(boundary)) if int(state) != start]
    ordered: List[int] = []
    for goal in original_goals:
        if goal in candidates and goal not in ordered:
            ordered.append(goal)
    remaining = [state for state in candidates if state not in ordered]
    if max_tasks > len(ordered) and remaining:
        take = min(max_tasks - len(ordered), len(remaining))
        indices = np.linspace(0, len(remaining) - 1, num=take, dtype=int).tolist()
        for idx in indices:
            state = int(remaining[idx])
            if state not in ordered:
                ordered.append(state)
    return ordered[:max_tasks]


def build_multitask_kernel(
    map_label: str,
    rows: Tuple[str, ...],
    method_spec: str,
    goals: Sequence[int],
    gamma: float,
    slip: float,
    seed: int,
    max_splits: int,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    start = grid.symbol_states("S")[0]
    actual_method = resolve_method_spec(method_spec, grid)
    t0 = time.perf_counter()
    base_boundary, constructor = construct_boundary(
        method=actual_method,
        map_name=map_label,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=gamma,
        max_splits=max_splits,
        seed=seed,
    )
    boundary = sorted(set(base_boundary).union({start}).union(int(goal) for goal in goals))
    construction_time = time.perf_counter() - t0
    t1 = time.perf_counter()
    reductions, valid_actions, _policies, metadata, _edge_rows = build_first_boundary_reductions(
        grid=grid,
        boundary=boundary,
        candidate_boundary=boundary,
        residual_boundary=boundary,
        soft_state_cost=np.zeros(grid.n_states, dtype=float),
        value_scale_task=1.0,
        slip=slip,
        gamma=gamma,
        local_horizon=999.0,
        hidden_threshold=1e-6,
        soft_threshold=3.0,
        residual_threshold=0.5,
        residual_reward_weight=0.0,
        residual_hit_weight=0.0,
        residual_threshold_mode="raw",
        compute_struct_distinct=False,
        proposal_boundary=boundary,
    )
    kernel_time = time.perf_counter() - t1
    return {
        "grid": grid,
        "method": actual_method,
        "method_spec": method_spec,
        "constructor": constructor,
        "boundary": boundary,
        "boundary_to_pos": {state: pos for pos, state in enumerate(boundary)},
        "reductions": reductions,
        "valid_actions": valid_actions,
        "metadata": metadata,
        "construction_time_sec": construction_time,
        "kernel_time_sec": kernel_time,
        "kernel_nnz": kernel_nnz(reductions, valid_actions),
        "transition_nnz_proxy": transition_nnz_proxy(grid, slip),
    }


def prefix_counts(max_tasks: int, requested: Sequence[int]) -> List[int]:
    out = sorted(set(min(max_tasks, int(count)) for count in requested if int(count) > 0))
    return [count for count in out if count > 0]


def run_method(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    method_spec: str,
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    grid = GridWorld(rows)
    start = grid.symbol_states("S")[0]
    model = build_multitask_kernel(
        map_label=map_label,
        rows=rows,
        method_spec=method_spec,
        goals=(),
        gamma=args.gamma,
        slip=args.slip,
        seed=args.seed,
        max_splits=args.max_splits,
    )
    if args.goal_source == "boundary":
        goals = choose_boundary_task_goals(grid, model["boundary"], max_tasks=args.max_tasks)
    else:
        goals = choose_task_goals(grid, max_tasks=args.max_tasks)
        if any(goal not in model["boundary_to_pos"] for goal in goals):
            model = build_multitask_kernel(
                map_label=map_label,
                rows=rows,
                method_spec=method_spec,
                goals=goals,
                gamma=args.gamma,
                slip=args.slip,
                seed=args.seed,
                max_splits=args.max_splits,
            )
    boundary_to_pos = model["boundary_to_pos"]
    reductions = model["reductions"]
    valid_actions = model["valid_actions"]

    task_rows: List[Dict[str, object]] = []
    for task_idx, goal in enumerate(goals, start=1):
        full = full_value_iteration_measured(
            grid=grid,
            goal_state=int(goal),
            gamma=args.gamma,
            slip=args.slip,
        )
        smdp = smdp_value_iteration_measured(
            reductions=reductions,
            valid_actions=valid_actions,
            goal_pos=int(boundary_to_pos[int(goal)]),
        )
        start_pos = int(boundary_to_pos[start])
        task_rows.append(
            {
                "task_idx": task_idx,
                "goal_state": int(goal),
                "full_vi_time_sec": float(full["time_sec"]),
                "full_vi_backup_count": int(full["backup_count"]),
                "smdp_solve_time_sec": float(smdp["time_sec"]),
                "smdp_edge_backup_count": int(smdp["edge_backup_count"]),
                "start_gap": abs(float(smdp["V"][start_pos]) - float(full["V"][start])),
            }
        )

    out: List[Dict[str, object]] = []
    for count in prefix_counts(len(task_rows), args.task_counts):
        prefix = task_rows[:count]
        full_time = sum(float(row["full_vi_time_sec"]) for row in prefix)
        smdp_time = sum(float(row["smdp_solve_time_sec"]) for row in prefix)
        full_backups = sum(int(row["full_vi_backup_count"]) for row in prefix)
        smdp_backups = sum(int(row["smdp_edge_backup_count"]) for row in prefix)
        upfront_time = float(model["construction_time_sec"]) + float(model["kernel_time_sec"])
        graph_total_time = upfront_time + smdp_time
        avg_full = full_time / max(1, count)
        avg_smdp = smdp_time / max(1, count)
        denominator = avg_full - avg_smdp
        break_even = upfront_time / denominator if denominator > 1e-12 else float("inf")
        gaps = [float(row["start_gap"]) for row in prefix]
        out.append(
            {
                "map_family": family,
                "map_size": size,
                "map": map_label,
                "method_spec": method_spec,
                "method": model["method"],
                "task_count": count,
                "goal_source": args.goal_source,
                "n_states": grid.n_states,
                "n_boundary": len(model["boundary"]),
                "state_compression_ratio": grid.n_states / max(1.0, float(len(model["boundary"]))),
                "transition_nnz_proxy": int(model["transition_nnz_proxy"]),
                "kernel_nnz": int(model["kernel_nnz"]),
                "construction_time_sec": float(model["construction_time_sec"]),
                "kernel_time_sec": float(model["kernel_time_sec"]),
                "upfront_time_sec": upfront_time,
                "full_total_time_sec": full_time,
                "graph_replan_time_sec": smdp_time,
                "graph_total_time_sec": graph_total_time,
                "amortized_speedup_vs_full_vi": full_time / max(1e-12, graph_total_time),
                "planning_only_speedup_vs_full_vi": full_time / max(1e-12, smdp_time),
                "break_even_task_count_estimate": break_even,
                "full_backup_count": full_backups,
                "smdp_edge_backup_count": smdp_backups,
                "backup_compression_ratio": full_backups / max(1.0, float(smdp_backups)),
                "start_gap_mean": float(np.mean(gaps)),
                "start_gap_max": float(np.max(gaps)),
            }
        )
    return out


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "map",
        "method_spec",
        "method",
        "task_count",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "upfront_time_sec",
        "full_total_time_sec",
        "graph_total_time_sec",
        "amortized_speedup_vs_full_vi",
        "break_even_task_count_estimate",
        "backup_compression_ratio",
        "start_gap_mean",
        "start_gap_max",
    ]
    lines = [
        "# Amortized Multi-Task Compression",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"methods = {list(args.methods)}",
        f"task_counts = {list(args.task_counts)}, max_tasks = {args.max_tasks}",
        f"goal_source = {args.goal_source}",
        "",
        "A boundary set and first-boundary kernels are built once, then reused across many terminal-goal tasks.",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_existing_rows(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def completed_jobs(rows: Sequence[Mapping[str, object]]) -> set[Tuple[str, str]]:
    return {
        (str(row.get("map", "")), str(row.get("method_spec", "")))
        for row in rows
        if row.get("map") and row.get("method_spec") and not row.get("error")
    }


def write_outputs(rows: Sequence[Mapping[str, object]], args: argparse.Namespace) -> None:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "amortized_multitask.csv", rows)
    (args.out_dir / "amortized_multitask.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


def progress_path(args: argparse.Namespace) -> Path:
    return args.progress_log or (args.out_dir / "progress.jsonl")


def log_progress(args: argparse.Namespace, event: str, **payload: object) -> None:
    record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        **payload,
    }
    text = json.dumps(record, sort_keys=True, default=json_default)
    print("AMORTIZED_PROGRESS " + text, flush=True)
    path = progress_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure amortized graph-SMDP cost across many reward/goal tasks.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:64", "open_room:10", "maze:13"])
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["endpoints", "betweenness_sqrt", "graph_rd_surrogate_joint", "turn_articulation"],
    )
    parser.add_argument("--task-counts", type=int, nargs="+", default=[1, 5, 10, 25, 50])
    parser.add_argument("--max-tasks", type=int, default=50)
    parser.add_argument("--goal-source", choices=["boundary", "all_states"], default="boundary")
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--progress-log", type=Path, default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/amortized_multitask"),
    )
    args = parser.parse_args()

    if args.num_shards < 1:
        raise ValueError("--num-shards must be >= 1")
    if args.shard_index < 0 or args.shard_index >= args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    jobs = [
        (family, size, map_label, map_rows, method)
        for family, size, map_label, map_rows in parse_map_specs(args.map_specs)
        for method in args.methods
    ]
    selected_jobs = [
        (job_index, *job)
        for job_index, job in enumerate(jobs)
        if job_index % args.num_shards == args.shard_index
    ]

    rows: List[Dict[str, object]] = (
        read_existing_rows(args.out_dir / "amortized_multitask.csv") if args.resume else []
    )
    done = completed_jobs(rows)
    log_progress(
        args,
        "start",
        shard_index=args.shard_index,
        num_shards=args.num_shards,
        selected_jobs=len(selected_jobs),
        total_jobs=len(jobs),
        resumed_completed_jobs=len(done),
    )

    completed_now = 0
    for progress_index, (job_index, family, size, map_label, map_rows, method) in enumerate(selected_jobs, start=1):
        key = (map_label, method)
        if args.resume and key in done:
            log_progress(
                args,
                "skip_completed",
                progress_index=progress_index,
                selected_jobs=len(selected_jobs),
                job_index=job_index,
                map=map_label,
                method_spec=method,
            )
            continue

        start_time = time.perf_counter()
        log_progress(
            args,
            "job_start",
            progress_index=progress_index,
            selected_jobs=len(selected_jobs),
            job_index=job_index,
            map=map_label,
            method_spec=method,
        )
        try:
            method_rows = run_method(family, size, map_label, map_rows, method, args)
        except Exception as exc:
            log_progress(
                args,
                "job_error",
                progress_index=progress_index,
                selected_jobs=len(selected_jobs),
                job_index=job_index,
                map=map_label,
                method_spec=method,
                elapsed_sec=time.perf_counter() - start_time,
                error=repr(exc),
            )
            if not args.continue_on_error:
                raise
            continue

        rows.extend(method_rows)
        done.add(key)
        completed_now += 1
        write_outputs(rows, args)
        log_progress(
            args,
            "job_done",
            progress_index=progress_index,
            selected_jobs=len(selected_jobs),
            job_index=job_index,
            map=map_label,
            method_spec=method,
            elapsed_sec=time.perf_counter() - start_time,
            rows_written=len(rows),
        )

    write_outputs(rows, args)
    log_progress(
        args,
        "done",
        shard_index=args.shard_index,
        num_shards=args.num_shards,
        completed_now=completed_now,
        total_rows=len(rows),
    )


if __name__ == "__main__":
    main()
