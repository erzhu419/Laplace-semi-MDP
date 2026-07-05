#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from compression_experiment_utils import build_compressed_model_measured, parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


DEFAULT_RECORD_POINTS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987)


def add_full_vi_rows(
    rows: List[Dict[str, object]],
    map_family: str,
    map_size: int,
    map_label: str,
    model: Mapping[str, object],
) -> None:
    full = model["full_result"]
    start_state = int(model["start_state"])
    optimal_start = float(full["V"][start_state])
    n_states = int(model["n_states"])
    recorded_iterations = set()
    for item in full["trace"]:
        recorded_iterations.add(int(item["iteration"]))
        value = item["value"]
        rows.append(
            {
                "map_family": map_family,
                "map_size": map_size,
                "map": map_label,
                "planner": "full_vi",
                "method_spec": "full_mdp",
                "method": "full_mdp",
                "iteration": int(item["iteration"]),
                "n_states": n_states,
                "n_boundary": n_states,
                "state_compression_ratio": 1.0,
                "planning_backup_count": int(item["backup_count"]),
                "total_backup_count_proxy": int(item["backup_count"]),
                "planning_time_sec": float(item["time_sec"]),
                "total_time_sec": float(item["time_sec"]),
                "start_value_estimate": float(value[start_state]),
                "start_value_optimal": optimal_start,
                "start_value_error": abs(float(value[start_state]) - optimal_start),
                "final_start_gap_floor": 0.0,
                "occupancy_struct_hidden_distinct": 0.0,
                "struct_hidden_distinct_cvar95": 0.0,
            }
        )
    if int(full["iterations"]) not in recorded_iterations:
        rows.append(
            {
                "map_family": map_family,
                "map_size": map_size,
                "map": map_label,
                "planner": "full_vi",
                "method_spec": "full_mdp",
                "method": "full_mdp",
                "iteration": int(full["iterations"]),
                "n_states": n_states,
                "n_boundary": n_states,
                "state_compression_ratio": 1.0,
                "planning_backup_count": int(full["backup_count"]),
                "total_backup_count_proxy": int(full["backup_count"]),
                "planning_time_sec": float(full["time_sec"]),
                "total_time_sec": float(full["time_sec"]),
                "start_value_estimate": optimal_start,
                "start_value_optimal": optimal_start,
                "start_value_error": 0.0,
                "final_start_gap_floor": 0.0,
                "occupancy_struct_hidden_distinct": 0.0,
                "struct_hidden_distinct_cvar95": 0.0,
            }
        )


def add_graph_rows(
    rows: List[Dict[str, object]],
    map_family: str,
    map_size: int,
    map_label: str,
    model: Mapping[str, object],
) -> None:
    full = model["full_result"]
    smdp = model["smdp_result"]
    start_state = int(model["start_state"])
    start_pos = int(model["boundary_to_pos"][start_state])
    optimal_start = float(full["V"][start_state])
    upfront_time = float(model["construction_time_sec"]) + float(model["kernel_time_sec"])
    edge_count = int(model["n_edges_valid"])
    kernel_nnz = int(model["kernel_nnz"])
    recorded_iterations = set()
    for item in smdp["trace"]:
        recorded_iterations.add(int(item["iteration"]))
        value = item["value"]
        rows.append(
            {
                "map_family": map_family,
                "map_size": map_size,
                "map": map_label,
                "planner": "graph_smdp",
                "method_spec": model["method_spec"],
                "method": model["method"],
                "iteration": int(item["iteration"]),
                "n_states": int(model["n_states"]),
                "n_boundary": int(model["n_boundary"]),
                "state_compression_ratio": float(model["n_states"]) / max(1.0, float(model["n_boundary"])),
                "planning_backup_count": int(item["backup_count"]),
                "total_backup_count_proxy": kernel_nnz + int(item["backup_count"]),
                "planning_time_sec": float(item["time_sec"]),
                "total_time_sec": upfront_time + float(item["time_sec"]),
                "start_value_estimate": float(value[start_pos]),
                "start_value_optimal": optimal_start,
                "start_value_error": abs(float(value[start_pos]) - optimal_start),
                "final_start_gap_floor": float(model["start_gap"]),
                "occupancy_struct_hidden_distinct": float(model["occupancy_struct_hidden_distinct"]),
                "struct_hidden_distinct_cvar95": float(model["struct_hidden_distinct_cvar95"]),
                "edge_count": edge_count,
                "kernel_nnz": kernel_nnz,
            }
        )
    if int(smdp["iterations"]) not in recorded_iterations:
        rows.append(
            {
                "map_family": map_family,
                "map_size": map_size,
                "map": map_label,
                "planner": "graph_smdp",
                "method_spec": model["method_spec"],
                "method": model["method"],
                "iteration": int(smdp["iterations"]),
                "n_states": int(model["n_states"]),
                "n_boundary": int(model["n_boundary"]),
                "state_compression_ratio": float(model["n_states"]) / max(1.0, float(model["n_boundary"])),
                "planning_backup_count": int(smdp["edge_backup_count"]),
                "total_backup_count_proxy": kernel_nnz + int(smdp["edge_backup_count"]),
                "planning_time_sec": float(smdp["time_sec"]),
                "total_time_sec": upfront_time + float(smdp["time_sec"]),
                "start_value_estimate": float(smdp["V"][start_pos]),
                "start_value_optimal": optimal_start,
                "start_value_error": float(model["start_gap"]),
                "final_start_gap_floor": float(model["start_gap"]),
                "occupancy_struct_hidden_distinct": float(model["occupancy_struct_hidden_distinct"]),
                "struct_hidden_distinct_cvar95": float(model["struct_hidden_distinct_cvar95"]),
                "edge_count": edge_count,
                "kernel_nnz": kernel_nnz,
            }
        )


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    final_rows = [
        row
        for row in rows
        if int(row["iteration"]) == max(
            int(other["iteration"])
            for other in rows
            if other["map"] == row["map"]
            and other["planner"] == row["planner"]
            and other["method"] == row["method"]
        )
    ]
    columns = [
        "map",
        "planner",
        "method_spec",
        "method",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "iteration",
        "planning_backup_count",
        "planning_time_sec",
        "start_value_error",
        "final_start_gap_floor",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
    ]
    lines = [
        "# Reward Propagation Curve",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"methods = {list(args.methods)}",
        f"record_points = {list(args.record_points)}",
        "",
        "Rows in the CSV contain the full curve. The table below shows each planner's final recorded point.",
        "",
        markdown_table(final_rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record value-error curves versus Bellman backup budget.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:64", "maze:13"])
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["endpoints", "betweenness_sqrt", "graph_rd_surrogate_joint", "turn_articulation"],
    )
    parser.add_argument("--record-points", type=int, nargs="+", default=list(DEFAULT_RECORD_POINTS))
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/reward_propagation_curve"),
    )
    args = parser.parse_args()

    rows: List[Dict[str, object]] = []
    full_added = set()
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
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
                full_record_points=args.record_points,
                smdp_record_points=args.record_points,
            )
            if map_label not in full_added:
                add_full_vi_rows(rows, family, size, map_label, model)
                full_added.add(map_label)
            add_graph_rows(rows, family, size, map_label, model)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "reward_propagation_curve.csv", rows)
    (args.out_dir / "reward_propagation_curve.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
