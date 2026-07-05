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
from bellman_kron import GridWorld
from compression_experiment_utils import (
    build_compressed_model_measured,
    parse_map_specs,
)
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def row_from_model(
    family: str,
    size: int,
    map_label: str,
    slip: float,
    model: Mapping[str, object],
) -> Dict[str, object]:
    full = model["full_result"]
    smdp = model["smdp_result"]
    full_time = float(full["time_sec"])
    smdp_time = float(smdp["time_sec"])
    total_compressed_time = (
        float(model["construction_time_sec"])
        + float(model["kernel_time_sec"])
        + smdp_time
    )
    transition_nnz = int(model["transition_nnz_proxy"])
    kernel_nnz = int(model["kernel_nnz"])
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method_spec": model["method_spec"],
        "method": model["method"],
        "first_hit_mode": model.get("first_hit_mode", "exact"),
        "first_hit_truncation_steps": model.get("first_hit_truncation_steps", ""),
        "first_hit_tail_tol": model.get("first_hit_tail_tol", ""),
        "first_hit_used_steps_max": model.get("first_hit_used_steps_max", ""),
        "first_hit_used_steps_mean": model.get("first_hit_used_steps_mean", ""),
        "first_hit_tail_bound_max": model.get("first_hit_tail_bound_max", ""),
        "n_states": int(model["n_states"]),
        "n_boundary": int(model["n_boundary"]),
        "n_edges_valid": int(model["n_edges_valid"]),
        "state_compression_ratio": float(model["n_states"]) / max(1.0, float(model["n_boundary"])),
        "transition_nnz_proxy": transition_nnz,
        "kernel_nnz": kernel_nnz,
        "memory_compression_ratio": transition_nnz / max(1.0, float(kernel_nnz)),
        "full_vi_iterations": int(full["iterations"]),
        "full_vi_time_sec": full_time,
        "full_vi_backup_count": int(full["backup_count"]),
        "construction_time_sec": float(model["construction_time_sec"]),
        "kernel_time_sec": float(model["kernel_time_sec"]),
        "upfront_time_sec": float(model["construction_time_sec"]) + float(model["kernel_time_sec"]),
        "smdp_iterations": int(smdp["iterations"]),
        "smdp_solve_time_sec": smdp_time,
        "smdp_edge_backup_count": int(smdp["edge_backup_count"]),
        "compressed_total_time_sec": total_compressed_time,
        "planning_time_speedup_vs_full_vi": full_time / max(1e-12, smdp_time),
        "total_time_speedup_vs_full_vi": full_time / max(1e-12, total_compressed_time),
        "backup_compression_ratio": float(full["backup_count"]) / max(1.0, float(smdp["edge_backup_count"])),
        "start_gap": float(model["start_gap"]),
        "value_gap_max": float(model["value_gap_max"]),
        "occupancy_struct_hidden_distinct": float(model["occupancy_struct_hidden_distinct"]),
        "occupancy_model_residual": float(model["occupancy_model_residual"]),
        "struct_hidden_distinct_cvar95": float(model["struct_hidden_distinct_cvar95"]),
        "error": "",
    }


def error_row(
    family: str,
    size: int,
    map_label: str,
    slip: float,
    method: str,
    rows: Sequence[str],
    message: str,
) -> Dict[str, object]:
    grid = GridWorld(tuple(rows))
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method_spec": method,
        "method": method,
        "first_hit_mode": "",
        "first_hit_truncation_steps": "",
        "first_hit_tail_tol": "",
        "first_hit_used_steps_max": "",
        "first_hit_used_steps_mean": "",
        "first_hit_tail_bound_max": "",
        "n_states": grid.n_states,
        "n_boundary": "",
        "n_edges_valid": "",
        "state_compression_ratio": "",
        "transition_nnz_proxy": "",
        "kernel_nnz": "",
        "memory_compression_ratio": "",
        "full_vi_iterations": "",
        "full_vi_time_sec": "",
        "full_vi_backup_count": "",
        "construction_time_sec": "",
        "kernel_time_sec": "",
        "upfront_time_sec": "",
        "smdp_iterations": "",
        "smdp_solve_time_sec": "",
        "smdp_edge_backup_count": "",
        "compressed_total_time_sec": "",
        "planning_time_speedup_vs_full_vi": "",
        "total_time_speedup_vs_full_vi": "",
        "backup_compression_ratio": "",
        "start_gap": "",
        "value_gap_max": "",
        "occupancy_struct_hidden_distinct": "",
        "occupancy_model_residual": "",
        "struct_hidden_distinct_cvar95": "",
        "error": message,
    }


def summarize(rows: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    ok_rows = [row for row in rows if not row.get("error")]
    graph_rows = [row for row in ok_rows if str(row.get("method_spec")) != "full_vi"]
    by_method: Dict[str, Dict[str, object]] = {}
    for method in sorted({str(row["method_spec"]) for row in graph_rows}):
        method_rows = [row for row in graph_rows if str(row["method_spec"]) == method]
        total_speedups = [finite_float(row.get("total_time_speedup_vs_full_vi")) for row in method_rows]
        planning_speedups = [finite_float(row.get("planning_time_speedup_vs_full_vi")) for row in method_rows]
        gaps = [finite_float(row.get("start_gap"), 0.0) for row in method_rows]
        by_method[method] = {
            "n_rows": len(method_rows),
            "max_n_states": max((int(row["n_states"]) for row in method_rows), default=0),
            "median_total_speedup": float(median(total_speedups)),
            "best_total_speedup": max(total_speedups, default=float("nan")),
            "median_planning_speedup": float(median(planning_speedups)),
            "best_planning_speedup": max(planning_speedups, default=float("nan")),
            "max_start_gap": max(gaps, default=float("nan")),
        }
    return {
        "n_rows": len(rows),
        "n_ok_rows": len(ok_rows),
        "n_error_rows": len(rows) - len(ok_rows),
        "max_n_states": max((int(row["n_states"]) for row in ok_rows), default=0),
        "best_total_speedup": max(
            (finite_float(row.get("total_time_speedup_vs_full_vi")) for row in graph_rows),
            default=float("nan"),
        ),
        "best_planning_speedup": max(
            (finite_float(row.get("planning_time_speedup_vs_full_vi")) for row in graph_rows),
            default=float("nan"),
        ),
        "max_start_gap": max((finite_float(row.get("start_gap"), 0.0) for row in graph_rows), default=float("nan")),
        "by_method": by_method,
    }


def median(values: Sequence[float]) -> float:
    vals = sorted(value for value in values if math.isfinite(value))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    if len(vals) % 2 == 1:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def write_report(
    rows: Sequence[Mapping[str, object]],
    summary: Mapping[str, object],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    columns = [
        "map",
        "slip",
        "method_spec",
        "first_hit_mode",
        "first_hit_truncation_steps",
        "first_hit_used_steps_max",
        "first_hit_tail_bound_max",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "memory_compression_ratio",
        "full_vi_time_sec",
        "upfront_time_sec",
        "smdp_solve_time_sec",
        "planning_time_speedup_vs_full_vi",
        "total_time_speedup_vs_full_vi",
        "backup_compression_ratio",
        "start_gap",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
        "error",
    ]
    method_rows = []
    for method, stats in dict(summary.get("by_method", {})).items():
        method_rows.append({"method_spec": method, **stats})
    method_columns = [
        "method_spec",
        "n_rows",
        "max_n_states",
        "median_total_speedup",
        "best_total_speedup",
        "median_planning_speedup",
        "best_planning_speedup",
        "max_start_gap",
    ]
    lines = [
        "# Large-Scale Compression",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"methods = {list(args.methods)}",
        f"first_hit_mode = {args.first_hit_mode}, first_hit_truncation_steps = {args.first_hit_truncation_steps}",
        f"gamma = {args.gamma}, slips = {list(args.slips)}",
        f"shard = {args.shard_index}/{args.num_shards}",
        "",
        "This run intentionally omits policy iteration so larger tabular maps do not pay the dense linear-solve cost. "
        "It measures the core claim: full-state Bellman propagation versus first-boundary graph-SMDP planning after graph/kernel construction.",
        "",
        f"- max states evaluated: `{summary['max_n_states']}`",
        f"- best total wall-time speedup over full VI: `{float(summary['best_total_speedup']):.4g}x`",
        f"- best planning-only speedup over full VI: `{float(summary['best_planning_speedup']):.4g}x`",
        f"- worst graph start-value gap: `{float(summary['max_start_gap']):.4g}`",
        f"- failed rows: `{summary['n_error_rows']}`",
        "",
        "## Method Summary",
        "",
        markdown_table(method_rows, method_columns) if method_rows else "_No graph rows._",
        "",
        "## Rows",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
            str(row.get("method_spec") or row.get("method") or ""),
        )
        if all(key):
            done.add(key)
    return done


def write_outputs(rows: Sequence[Mapping[str, object]], args: argparse.Namespace) -> None:
    summary = summarize(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "large_scale_compression.csv", rows)
    (args.out_dir / "large_scale_compression.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, summary, args.out_dir / "summary.md", args)


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
    parser = argparse.ArgumentParser(description="Large-scale VI versus compressed graph-SMDP scaling.")
    parser.add_argument(
        "--map-specs",
        nargs="+",
        default=[
            "corridor:64,128,256",
            "open_room:12,16,24",
            "four_rooms:11,15",
            "maze:13,17",
        ],
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        default=[
            "endpoints",
            "turn_articulation",
            "graph_rd_surrogate_joint",
            "betweenness_sqrt",
            "coverage_sqrt",
        ],
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--slips", type=float, nargs="+", default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=18)
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
    parser.add_argument("--no-struct-distinct", action="store_true")
    parser.add_argument("--first-hit-mode", choices=["exact", "truncated", "adaptive"], default="exact")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=32)
    parser.add_argument("--first-hit-tail-tol", type=float, default=0.0)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--progress-log", type=Path, default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/large_scale_compression"),
    )
    args = parser.parse_args()
    args.slips = list(args.slips if args.slips is not None else [args.slip])
    if args.num_shards < 1:
        raise ValueError("--num-shards must be >= 1")
    if args.shard_index < 0 or args.shard_index >= args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    jobs = [
        (family, size, map_label, map_rows, slip, method)
        for family, size, map_label, map_rows in parse_map_specs(args.map_specs)
        for slip in args.slips
        for method in args.methods
    ]
    selected_jobs = [
        (job_index, *job)
        for job_index, job in enumerate(jobs)
        if job_index % args.num_shards == args.shard_index
    ]

    rows: List[Dict[str, object]] = (
        read_existing_rows(args.out_dir / "large_scale_compression.csv") if args.resume else []
    )
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
            model = build_compressed_model_measured(
                map_label=map_label,
                rows=map_rows,
                method_spec=method,
                gamma=args.gamma,
                slip=slip,
                seed=args.seed,
                max_splits=args.max_splits,
                audit_lens=args.audit_lens,
                audit_top_fraction=args.audit_top_fraction,
                soft_kind=args.soft_kind,
                soft_top_fraction=args.soft_top_fraction,
                local_horizon=args.local_horizon,
                hidden_threshold=args.hidden_threshold,
                soft_threshold=args.soft_threshold,
                residual_threshold=args.residual_threshold,
                residual_threshold_mode=args.residual_threshold_mode,
                residual_reward_weight=args.residual_reward_weight,
                residual_hit_weight=args.residual_hit_weight,
                compute_struct_distinct=not args.no_struct_distinct,
                first_hit_mode=args.first_hit_mode,
                first_hit_truncation_steps=args.first_hit_truncation_steps,
                first_hit_tail_tol=args.first_hit_tail_tol,
            )
            rows.append(row_from_model(family, size, map_label, slip, model))
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
            rows.append(error_row(family, size, map_label, slip, method, map_rows, repr(exc)))
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
