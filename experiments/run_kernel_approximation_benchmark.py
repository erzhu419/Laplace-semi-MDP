#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from compression_experiment_utils import build_compressed_model_measured, parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def model_row(
    family: str,
    size: int,
    map_label: str,
    method: str,
    kernel_label: str,
    model: Mapping[str, object],
) -> Dict[str, object]:
    full = model["full_result"]
    smdp = model["smdp_result"]
    total_time = (
        float(model["construction_time_sec"])
        + float(model["kernel_time_sec"])
        + float(smdp["time_sec"])
    )
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "method_spec": method,
        "method": model["method"],
        "kernel_label": kernel_label,
        "first_hit_mode": model.get("first_hit_mode", "exact"),
        "first_hit_truncation_steps": model.get("first_hit_truncation_steps", ""),
        "first_hit_tail_tol": model.get("first_hit_tail_tol", ""),
        "first_hit_used_steps_max": model.get("first_hit_used_steps_max", ""),
        "first_hit_used_steps_mean": model.get("first_hit_used_steps_mean", ""),
        "first_hit_tail_bound_max": model.get("first_hit_tail_bound_max", ""),
        "n_states": int(model["n_states"]),
        "n_boundary": int(model["n_boundary"]),
        "state_compression_ratio": float(model["n_states"]) / max(1.0, float(model["n_boundary"])),
        "construction_time_sec": float(model["construction_time_sec"]),
        "kernel_time_sec": float(model["kernel_time_sec"]),
        "smdp_solve_time_sec": float(smdp["time_sec"]),
        "compressed_total_time_sec": total_time,
        "full_vi_time_sec": float(full["time_sec"]),
        "planning_time_speedup_vs_full_vi": float(full["time_sec"]) / max(1e-12, float(smdp["time_sec"])),
        "total_time_speedup_vs_full_vi": float(full["time_sec"]) / max(1e-12, total_time),
        "start_gap_vs_full": float(model["start_gap"]),
        "value_gap_max_vs_full": float(model["value_gap_max"]),
        "occupancy_struct_hidden_distinct": float(model["occupancy_struct_hidden_distinct"]),
        "occupancy_model_residual": float(model["occupancy_model_residual"]),
        "struct_hidden_distinct_cvar95": float(model["struct_hidden_distinct_cvar95"]),
        "start_value": float(smdp["V"][model["boundary_to_pos"][model["start_state"]]]),
        "error": "",
    }


def error_row(
    family: str,
    size: int,
    map_label: str,
    method: str,
    kernel_label: str,
    message: str,
) -> Dict[str, object]:
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "method_spec": method,
        "method": method,
        "kernel_label": kernel_label,
        "first_hit_mode": "",
        "first_hit_truncation_steps": "",
        "first_hit_tail_tol": "",
        "first_hit_used_steps_max": "",
        "first_hit_used_steps_mean": "",
        "first_hit_tail_bound_max": "",
        "n_states": "",
        "n_boundary": "",
        "state_compression_ratio": "",
        "construction_time_sec": "",
        "kernel_time_sec": "",
        "smdp_solve_time_sec": "",
        "compressed_total_time_sec": "",
        "full_vi_time_sec": "",
        "planning_time_speedup_vs_full_vi": "",
        "total_time_speedup_vs_full_vi": "",
        "start_gap_vs_full": "",
        "value_gap_max_vs_full": "",
        "occupancy_struct_hidden_distinct": "",
        "occupancy_model_residual": "",
        "struct_hidden_distinct_cvar95": "",
        "start_value": "",
        "error": message,
    }


def add_exact_deltas(rows: List[Dict[str, object]]) -> None:
    exact_by_key: Dict[Tuple[str, str], Dict[str, object]] = {}
    for row in rows:
        if row.get("kernel_label") == "exact" and not row.get("error"):
            exact_by_key[(str(row["map"]), str(row["method_spec"]))] = row
    for row in rows:
        exact = exact_by_key.get((str(row["map"]), str(row["method_spec"])))
        if exact is None or row.get("error"):
            row["kernel_time_speedup_vs_exact"] = ""
            row["total_time_speedup_vs_exact"] = ""
            row["start_value_abs_diff_vs_exact"] = ""
            row["start_gap_delta_vs_exact"] = ""
            row["value_gap_delta_vs_exact"] = ""
            continue
        row["kernel_time_speedup_vs_exact"] = finite_float(exact["kernel_time_sec"]) / max(
            1e-12,
            finite_float(row["kernel_time_sec"]),
        )
        row["total_time_speedup_vs_exact"] = finite_float(exact["compressed_total_time_sec"]) / max(
            1e-12,
            finite_float(row["compressed_total_time_sec"]),
        )
        row["start_value_abs_diff_vs_exact"] = abs(
            finite_float(row["start_value"]) - finite_float(exact["start_value"])
        )
        row["start_gap_delta_vs_exact"] = finite_float(row["start_gap_vs_full"]) - finite_float(
            exact["start_gap_vs_full"]
        )
        row["value_gap_delta_vs_exact"] = finite_float(row["value_gap_max_vs_full"]) - finite_float(
            exact["value_gap_max_vs_full"]
        )


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    graph_rows = [row for row in rows if not row.get("error")]
    approximate = [row for row in graph_rows if row.get("kernel_label") != "exact"]
    best_kernel_speedup = max(
        (finite_float(row.get("kernel_time_speedup_vs_exact")) for row in approximate),
        default=float("nan"),
    )
    best_total_speedup = max(
        (finite_float(row.get("total_time_speedup_vs_exact")) for row in approximate),
        default=float("nan"),
    )
    max_start_diff = max(
        (finite_float(row.get("start_value_abs_diff_vs_exact"), 0.0) for row in approximate),
        default=float("nan"),
    )
    columns = [
        "map",
        "method_spec",
        "kernel_label",
        "first_hit_used_steps_max",
        "first_hit_tail_bound_max",
        "n_states",
        "n_boundary",
        "kernel_time_sec",
        "compressed_total_time_sec",
        "kernel_time_speedup_vs_exact",
        "total_time_speedup_vs_exact",
        "start_value_abs_diff_vs_exact",
        "start_gap_vs_full",
        "value_gap_max_vs_full",
        "planning_time_speedup_vs_full_vi",
        "total_time_speedup_vs_full_vi",
        "error",
    ]
    lines = [
        "# Kernel Approximation Benchmark",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"methods = {list(args.methods)}",
        f"k_values = {list(args.k_values)}",
        f"adaptive_tail_tols = {list(args.adaptive_tail_tols)}",
        f"adaptive_max_steps = {args.adaptive_max_steps}",
        "",
        "This isolates the current upfront bottleneck by comparing exact first-hit Green solves against fixed-K and adaptive Neumann-prefix kernels.",
        "",
        f"- best approximate kernel-time speedup vs exact: `{best_kernel_speedup:.4g}x`",
        f"- best approximate total-time speedup vs exact: `{best_total_speedup:.4g}x`",
        f"- worst start-value difference vs exact: `{max_start_diff:.4g}`",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare exact and truncated first-hit Green kernels.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:64", "open_room:10", "maze:13"])
    parser.add_argument("--methods", nargs="+", default=["endpoints", "turn_articulation", "graph_rd_surrogate_joint"])
    parser.add_argument("--k-values", type=int, nargs="+", default=[8, 16, 32])
    parser.add_argument("--adaptive-tail-tols", type=float, nargs="+", default=[1e-4, 1e-6])
    parser.add_argument("--adaptive-max-steps", type=int, default=512)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
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
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/kernel_approximation"))
    args = parser.parse_args()

    rows: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        for method in args.methods:
            kernel_specs = [("exact", "exact", 0, 0.0)]
            kernel_specs.extend((f"truncated_K{k}", "truncated", int(k), 0.0) for k in args.k_values)
            kernel_specs.extend(
                (
                    f"adaptive_eps{tail_tol:g}",
                    "adaptive",
                    int(args.adaptive_max_steps),
                    float(tail_tol),
                )
                for tail_tol in args.adaptive_tail_tols
            )
            for kernel_label, mode, k_steps, tail_tol in kernel_specs:
                try:
                    model = build_compressed_model_measured(
                        map_label=map_label,
                        rows=map_rows,
                        method_spec=method,
                        gamma=args.gamma,
                        slip=args.slip,
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
                        first_hit_mode=mode,
                        first_hit_truncation_steps=k_steps,
                        first_hit_tail_tol=tail_tol,
                    )
                    rows.append(model_row(family, size, map_label, method, kernel_label, model))
                except Exception as exc:
                    if not args.continue_on_error:
                        raise
                    rows.append(error_row(family, size, map_label, method, kernel_label, repr(exc)))

    add_exact_deltas(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "kernel_approximation.csv", rows)
    (args.out_dir / "kernel_approximation.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
