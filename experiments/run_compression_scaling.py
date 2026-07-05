#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from bellman_kron import GridWorld
from compression_experiment_utils import (
    build_compressed_model_measured,
    full_policy_iteration_measured,
    parse_map_specs,
)
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def row_from_model(
    family: str,
    size: int,
    map_label: str,
    model: Mapping[str, object],
    pi_result: Mapping[str, object],
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
    kernel_nnz = int(model["kernel_nnz"])
    transition_nnz = int(model["transition_nnz_proxy"])
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "method_spec": model["method_spec"],
        "method": model["method"],
        "first_hit_mode": model.get("first_hit_mode", "exact"),
        "first_hit_truncation_steps": model.get("first_hit_truncation_steps", ""),
        "first_hit_used_steps_max": model.get("first_hit_used_steps_max", ""),
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
        "full_pi_iterations": int(pi_result["iterations"]),
        "full_pi_time_sec": float(pi_result["time_sec"]),
        "full_pi_improvement_backup_count": int(pi_result["improvement_backup_count"]),
        "construction_time_sec": float(model["construction_time_sec"]),
        "kernel_time_sec": float(model["kernel_time_sec"]),
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
    }


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "map",
        "method_spec",
        "method",
        "first_hit_mode",
        "first_hit_truncation_steps",
        "first_hit_used_steps_max",
        "first_hit_tail_bound_max",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "memory_compression_ratio",
        "full_vi_time_sec",
        "construction_time_sec",
        "kernel_time_sec",
        "smdp_solve_time_sec",
        "planning_time_speedup_vs_full_vi",
        "total_time_speedup_vs_full_vi",
        "backup_compression_ratio",
        "start_gap",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
    ]
    lines = [
        "# Compression Scaling",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"methods = {list(args.methods)}",
        f"gamma = {args.gamma}, slip = {args.slip}",
        "",
        "Exact first-boundary kernels are built once, then graph/SMDP planning propagates value over compressed boundary vertices and option edges.",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure state/edge compression and planning cost for graph SMDPs.")
    parser.add_argument(
        "--map-specs",
        nargs="+",
        default=[
            "corridor:16,32,64",
            "open_room:6,10",
            "four_rooms:7,11",
            "maze:9,13",
        ],
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["endpoints", "betweenness_sqrt", "graph_rd_surrogate_joint", "turn_articulation"],
    )
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
    parser.add_argument("--first-hit-mode", choices=["exact", "truncated", "adaptive"], default="exact")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=32)
    parser.add_argument("--first-hit-tail-tol", type=float, default=0.0)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/compression_scaling"),
    )
    args = parser.parse_args()

    rows: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        grid = GridWorld(map_rows)
        goal = grid.symbol_states("G")[0]
        pi_result = full_policy_iteration_measured(
            grid=grid,
            goal_state=goal,
            gamma=args.gamma,
            slip=args.slip,
        )
        for method in args.methods:
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
                first_hit_mode=args.first_hit_mode,
                first_hit_truncation_steps=args.first_hit_truncation_steps,
                first_hit_tail_tol=args.first_hit_tail_tol,
            )
            rows.append(row_from_model(family, size, map_label, model, pi_result))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "compression_scaling.csv", rows)
    (args.out_dir / "compression_scaling.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
