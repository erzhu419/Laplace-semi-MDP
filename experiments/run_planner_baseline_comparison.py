#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import socket
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import GridWorld
from compression_experiment_utils import full_value_iteration_measured, parse_map_specs
from planner_baselines import (
    SparseGridModel,
    bellman_residual,
    build_sparse_grid_model,
    gauss_seidel_value_iteration_measured,
    prioritized_sweeping_value_iteration_measured,
    quantiles,
    sparse_value_iteration_measured,
)
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


Runner = Callable[[SparseGridModel, float, float], Dict[str, object]]


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def run_sparse(model: SparseGridModel, gamma: float, tol: float) -> Dict[str, object]:
    return sparse_value_iteration_measured(model, gamma=gamma, tol=tol)


def run_gauss_seidel(model: SparseGridModel, gamma: float, tol: float) -> Dict[str, object]:
    return gauss_seidel_value_iteration_measured(model, gamma=gamma, tol=tol)


def run_prioritized(model: SparseGridModel, gamma: float, tol: float) -> Dict[str, object]:
    return prioritized_sweeping_value_iteration_measured(model, gamma=gamma, tol=tol)


RUNNERS: Mapping[str, Runner] = {
    "sparse_vectorized_vi": run_sparse,
    "gauss_seidel_vi": run_gauss_seidel,
    "prioritized_sweeping": run_prioritized,
}


def run_legacy(
    grid: GridWorld,
    goal_state: int,
    gamma: float,
    slip: float,
    tol: float,
) -> Dict[str, object]:
    result = dict(
        full_value_iteration_measured(
            grid=grid,
            goal_state=goal_state,
            gamma=gamma,
            slip=slip,
            tol=tol,
        )
    )
    result["method"] = "legacy_python_sync_vi"
    result["state_updates"] = int(result["iterations"]) * grid.n_states
    return result


def read_existing(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def completed_jobs(rows: Sequence[Mapping[str, object]]) -> set[Tuple[str, str, str, str]]:
    return {
        (
            str(row.get("map", "")),
            str(row.get("slip", "")),
            str(row.get("method", "")),
            str(row.get("repeat", "")),
        )
        for row in rows
        if row.get("map") and row.get("method") and row.get("repeat") not in (None, "")
    }


def aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("error"):
            continue
        grouped[(str(row.get("map", "")), str(row.get("slip", "")), str(row.get("method", "")))].append(row)

    aggregate: List[Dict[str, object]] = []
    for group_index, ((map_name, slip, method), group) in enumerate(sorted(grouped.items())):
        q1_time, median_time, q3_time = quantiles(finite_float(row.get("time_sec")) for row in group)
        time_values = np.asarray([finite_float(row.get("time_sec")) for row in group], dtype=float)
        time_values = time_values[np.isfinite(time_values)]
        if len(time_values):
            rng = np.random.default_rng(1729 + group_index)
            samples = rng.choice(time_values, size=(2000, len(time_values)), replace=True)
            bootstrap_medians = np.median(samples, axis=1)
            ci_low, ci_high = np.quantile(bootstrap_medians, [0.025, 0.975])
        else:
            ci_low = ci_high = float("nan")
        q1_backups, median_backups, q3_backups = quantiles(
            finite_float(row.get("backup_count")) for row in group
        )
        aggregate.append(
            {
                "map": map_name,
                "map_family": group[0].get("map_family", ""),
                "map_size": group[0].get("map_size", ""),
                "slip": slip,
                "method": method,
                "n_states": group[0].get("n_states", ""),
                "n_repeats": len(group),
                "time_q1_sec": q1_time,
                "time_median_sec": median_time,
                "time_q3_sec": q3_time,
                "time_bootstrap_ci_low_sec": float(ci_low),
                "time_bootstrap_ci_high_sec": float(ci_high),
                "backup_q1": q1_backups,
                "backup_median": median_backups,
                "backup_q3": q3_backups,
                "max_value_error": max(finite_float(row.get("max_value_error"), 0.0) for row in group),
                "max_start_error": max(finite_float(row.get("start_value_error"), 0.0) for row in group),
                "max_bellman_residual": max(
                    finite_float(row.get("bellman_residual"), 0.0) for row in group
                ),
            }
        )
    return aggregate


def fastest_valid_rows(aggregate: Sequence[Mapping[str, object]], tolerance: float) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in aggregate:
        if finite_float(row.get("max_value_error")) <= tolerance:
            grouped[(str(row.get("map", "")), str(row.get("slip", "")))].append(row)
    out: List[Dict[str, object]] = []
    for (map_name, slip), group in sorted(grouped.items()):
        best = min(group, key=lambda row: finite_float(row.get("time_median_sec"), float("inf")))
        out.append(
            {
                "map": map_name,
                "slip": slip,
                "strongest_method": best.get("method", ""),
                "strongest_time_median_sec": best.get("time_median_sec", ""),
                "strongest_time_q1_sec": best.get("time_q1_sec", ""),
                "strongest_time_q3_sec": best.get("time_q3_sec", ""),
                "strongest_time_bootstrap_ci_low_sec": best.get("time_bootstrap_ci_low_sec", ""),
                "strongest_time_bootstrap_ci_high_sec": best.get("time_bootstrap_ci_high_sec", ""),
                "strongest_backup_median": best.get("backup_median", ""),
                "max_value_error": best.get("max_value_error", ""),
            }
        )
    return out


def write_report(
    aggregate: Sequence[Mapping[str, object]],
    strongest: Sequence[Mapping[str, object]],
    path: Path,
    args: argparse.Namespace,
) -> None:
    method_columns = [
        "map",
        "slip",
        "method",
        "n_states",
        "n_repeats",
        "time_q1_sec",
        "time_median_sec",
        "time_q3_sec",
        "time_bootstrap_ci_low_sec",
        "time_bootstrap_ci_high_sec",
        "backup_median",
        "max_value_error",
        "max_bellman_residual",
    ]
    strongest_columns = [
        "map",
        "slip",
        "strongest_method",
        "strongest_time_median_sec",
        "strongest_time_q1_sec",
        "strongest_time_q3_sec",
        "strongest_time_bootstrap_ci_low_sec",
        "strongest_time_bootstrap_ci_high_sec",
        "strongest_backup_median",
        "max_value_error",
    ]
    lines = [
        "# Strong Full-MDP Planner Baselines",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"methods = {list(args.methods)}, repeats = {args.repeats}, tolerance = {args.tol}",
        "",
        "Sparse-vectorized VI, Gauss-Seidel VI, and prioritized sweeping are compared on the same "
        "known transition model. The fastest numerically valid row is the conservative full-MDP "
        "wall-time denominator used by the submission table.",
        "",
        "## Fastest Valid Planner",
        "",
        markdown_table(strongest, strongest_columns) if strongest else "_No valid rows._",
        "",
        "## All Methods",
        "",
        markdown_table(aggregate, method_columns) if aggregate else "_No rows._",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare strong full-state planning implementations.")
    parser.add_argument(
        "--map-specs",
        nargs="+",
        default=["corridor:256,512,1024", "open_room:24,32", "four_rooms:21,31", "maze:21,31"],
    )
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05, 0.1])
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=["sparse_vectorized_vi", "gauss_seidel_vi", "prioritized_sweeping", "legacy_python_sync_vi"],
        default=["sparse_vectorized_vi", "gauss_seidel_vi", "prioritized_sweeping"],
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--valid-error-tol", type=float, default=1e-7)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument(
        "--shard-unit",
        choices=["job", "case_repeat", "case"],
        default="job",
        help="Keep methods together within a shard for paired timing when using case_repeat or case.",
    )
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/planner_baseline_comparison"),
    )
    args = parser.parse_args()

    if args.num_shards < 1 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("Require 0 <= shard-index < num-shards and num-shards >= 1.")
    cases = list(parse_map_specs(args.map_specs))
    if args.shard_unit == "job":
        jobs = [
            (family, size, map_name, map_rows, slip, method, repeat)
            for family, size, map_name, map_rows in cases
            for slip in args.slips
            for method in args.methods
            for repeat in range(args.repeats)
        ]
        selected = [job for index, job in enumerate(jobs) if index % args.num_shards == args.shard_index]
    elif args.shard_unit == "case_repeat":
        units = [
            (family, size, map_name, map_rows, slip, repeat)
            for family, size, map_name, map_rows in cases
            for slip in args.slips
            for repeat in range(args.repeats)
        ]
        selected_units = [unit for index, unit in enumerate(units) if index % args.num_shards == args.shard_index]
        selected = [
            (family, size, map_name, map_rows, slip, method, repeat)
            for family, size, map_name, map_rows, slip, repeat in selected_units
            for method in args.methods
        ]
    else:
        units = [
            (family, size, map_name, map_rows, slip)
            for family, size, map_name, map_rows in cases
            for slip in args.slips
        ]
        selected_units = [unit for index, unit in enumerate(units) if index % args.num_shards == args.shard_index]
        selected = [
            (family, size, map_name, map_rows, slip, method, repeat)
            for family, size, map_name, map_rows, slip in selected_units
            for repeat in range(args.repeats)
            for method in args.methods
        ]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.out_dir / "planner_baseline_runs.csv"
    rows: List[Dict[str, object]] = read_existing(raw_path) if args.resume else []
    done = completed_jobs(rows)
    model_cache: Dict[Tuple[str, float], SparseGridModel] = {}
    reference_cache: Dict[Tuple[str, float], np.ndarray] = {}

    for family, size, map_name, map_rows, slip, method, repeat in selected:
        key = (map_name, str(slip), method, str(repeat))
        if args.resume and key in done:
            continue
        try:
            grid = GridWorld(map_rows)
            goal_state = grid.symbol_states("G")[0]
            start_state = grid.symbol_states("S")[0]
            model_key = (map_name, float(slip))
            if model_key not in model_cache:
                model_cache[model_key] = build_sparse_grid_model(grid, goal_state=goal_state, slip=slip)
                reference_cache[model_key] = np.asarray(
                    sparse_value_iteration_measured(
                        model_cache[model_key], gamma=args.gamma, tol=min(args.tol, 1e-12)
                    )["V"],
                    dtype=float,
                )
            model = model_cache[model_key]
            reference = reference_cache[model_key]

            if repeat == 0:
                for _ in range(max(0, args.warmups)):
                    if method == "legacy_python_sync_vi":
                        run_legacy(grid, goal_state, args.gamma, slip, args.tol)
                    else:
                        RUNNERS[method](model, args.gamma, args.tol)

            if method == "legacy_python_sync_vi":
                result = run_legacy(grid, goal_state, args.gamma, slip, args.tol)
                result["bellman_residual"] = bellman_residual(model, np.asarray(result["V"]), args.gamma)
            else:
                result = RUNNERS[method](model, args.gamma, args.tol)
            value = np.asarray(result["V"], dtype=float)
            rows.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_name,
                    "slip": slip,
                    "method": method,
                    "repeat": repeat,
                    "pair_id": f"{map_name}|{slip}|{repeat}",
                    "host": socket.gethostname(),
                    "n_states": grid.n_states,
                    "iterations": result.get("iterations", ""),
                    "state_updates": result.get("state_updates", ""),
                    "backup_count": result.get("backup_count", ""),
                    "time_sec": result.get("time_sec", ""),
                    "bellman_residual": result.get("bellman_residual", ""),
                    "max_value_error": float(np.max(np.abs(value - reference))),
                    "start_value_error": float(abs(value[start_state] - reference[start_state])),
                    "error": "",
                }
            )
        except Exception as exc:
            if not args.continue_on_error:
                raise
            rows.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_name,
                    "slip": slip,
                    "method": method,
                    "repeat": repeat,
                    "pair_id": f"{map_name}|{slip}|{repeat}",
                    "host": socket.gethostname(),
                    "error": repr(exc),
                }
            )
        done.add(key)
        write_csv_all_fields(raw_path, rows)

    aggregate = aggregate_rows(rows)
    strongest = fastest_valid_rows(aggregate, tolerance=args.valid_error_tol)
    write_csv_all_fields(args.out_dir / "planner_baseline_aggregate.csv", aggregate)
    write_csv_all_fields(args.out_dir / "strongest_planner_by_case.csv", strongest)
    (args.out_dir / "planner_baseline_comparison.json").write_text(
        json.dumps({"runs": rows, "aggregate": aggregate, "strongest": strongest}, indent=2, default=json_default)
        + "\n",
        encoding="utf-8",
    )
    write_report(aggregate, strongest, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
