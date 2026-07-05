#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from compression_experiment_utils import parse_map_specs
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


def read_existing_rows(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def completed_jobs(rows: Sequence[Mapping[str, object]]) -> set[tuple[str, str, str]]:
    done: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (
            str(row.get("map", "")),
            str(row.get("slip", "")),
            str(row.get("method", "")),
        )
        if all(key):
            done.add(key)
    return done


def map_jobs(args: argparse.Namespace) -> List[Tuple[str, int, str, Tuple[str, ...]]]:
    if args.map_specs:
        return [
            (family, size, map_label, tuple(map_rows))
            for family, size, map_label, map_rows in parse_map_specs(args.map_specs)
        ]
    jobs: List[Tuple[str, int, str, Tuple[str, ...]]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        jobs.append((map_name, len(MAPS[map_name]), map_name, MAPS[map_name]))
    return jobs


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


def sorted_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    return sorted(
        [dict(row) for row in rows],
        key=lambda row: (
            str(row.get("map", "")),
            finite_float(row, "slip"),
            family_name(str(row.get("method", ""))),
            finite_float(row, "n_boundary"),
            str(row.get("method", "")),
        ),
    )


def write_outputs(rows: Sequence[Mapping[str, object]], args: argparse.Namespace) -> None:
    ok_rows = [dict(row) for row in rows if not row.get("error")]
    error_rows = [{**dict(row), "pareto_frontier": False, "pareto_dominated_by": ""} for row in rows if row.get("error")]
    marked_rows = mark_pareto_frontier(ok_rows, objectives=args.frontier_objectives) + error_rows
    marked_rows = sorted_rows(marked_rows)
    frontier_rows = [row for row in marked_rows if bool(row["pareto_frontier"])]
    frontier_rows = sorted(
        frontier_rows,
        key=lambda row: (
            str(row["map"]),
            float(row["slip"]),
            finite_float(row, "description_length_proxy"),
            finite_float(row, "occupancy_struct_hidden_distinct"),
        ),
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "frontier_all.csv", marked_rows)
    write_csv_all_fields(args.out_dir / "frontier_pareto.csv", frontier_rows)
    (args.out_dir / "frontier_all.json").write_text(
        json.dumps(marked_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(marked_rows, frontier_rows, args.out_dir / "summary.md", args)


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
        f"maps = {list(args.maps)}, map_specs = {list(args.map_specs or [])}, slips = {list(args.slips)}, gamma = {args.gamma}",
        f"shard = {args.shard_index}/{args.num_shards}",
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
    parser.add_argument("--map-specs", nargs="+", default=None)
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
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--progress-log", type=Path, default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/option_baseline_frontier_maze_slip005"),
    )
    args = parser.parse_args()
    if args.num_shards < 1:
        raise ValueError("--num-shards must be >= 1")
    if args.shard_index < 0 or args.shard_index >= args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    args.methods = expand_methods(
        families=args.families,
        k_values=args.k_values,
        include_endpoints=args.include_endpoints,
        include_graph_rd=args.include_graph_rd,
        include_dense=args.include_dense,
    )
    jobs = [
        (family, size, map_label, map_rows, slip, method)
        for family, size, map_label, map_rows in map_jobs(args)
        for slip in args.slips
        for method in args.methods
    ]
    selected_jobs = [
        (job_index, *job)
        for job_index, job in enumerate(jobs)
        if job_index % args.num_shards == args.shard_index
    ]

    rows: List[Dict[str, object]] = read_existing_rows(args.out_dir / "frontier_all.csv") if args.resume else []
    done = completed_jobs(rows)
    log_progress(
        args,
        "start",
        selected_jobs=len(selected_jobs),
        total_jobs=len(jobs),
        resumed_completed_jobs=len(done),
    )
    for progress_index, (job_index, family, size, map_label, map_rows, slip, method) in enumerate(
        selected_jobs, start=1
    ):
        key = (map_label, str(slip), method)
        if args.resume and key in done:
            log_progress(
                args,
                "skip_completed",
                progress_index=progress_index,
                selected_jobs=len(selected_jobs),
                job_index=job_index,
                map=map_label,
                slip=slip,
                method=method,
            )
            continue
        started = time.perf_counter()
        try:
            row = evaluate_method(method, map_label, map_rows, slip, args)
            row.update({"map_family": family, "map_size": size})
            rows.append(row)
            done.add(key)
            log_progress(
                args,
                "job_done",
                progress_index=progress_index,
                selected_jobs=len(selected_jobs),
                job_index=job_index,
                map=map_label,
                slip=slip,
                method=method,
                elapsed_sec=time.perf_counter() - started,
            )
        except Exception as exc:
            if not args.continue_on_error:
                raise
            rows.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_label,
                    "slip": slip,
                    "method": method,
                    "error": repr(exc),
                }
            )
            done.add(key)
            log_progress(
                args,
                "job_error",
                progress_index=progress_index,
                selected_jobs=len(selected_jobs),
                job_index=job_index,
                map=map_label,
                slip=slip,
                method=method,
                elapsed_sec=time.perf_counter() - started,
                error=repr(exc),
            )
        write_outputs(rows, args)
    write_outputs(rows, args)
    log_progress(args, "done", rows=len(rows), selected_jobs=len(selected_jobs), total_jobs=len(jobs))


if __name__ == "__main__":
    main()
