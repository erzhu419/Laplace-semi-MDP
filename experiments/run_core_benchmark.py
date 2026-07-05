#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import GridWorld
from compression_experiment_utils import (
    full_policy_iteration_measured,
    full_value_iteration_measured,
    kernel_nnz,
    parse_map_specs,
    resolve_method_spec,
    smdp_value_iteration_measured,
    transition_nnz_proxy,
    valid_edge_count,
)
from run_first_boundary_targeted import (
    build_first_boundary_reductions,
    candidate_boundary_states,
    critical_saliency,
    markdown_table,
    policy_boundary_occupancy,
    tail_cvar,
)
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import (
    construct_boundary,
    json_default,
    method_family,
    rollout_smdp_policy,
    stable_method_seed,
    write_csv_all_fields,
)
from run_rd_group_constrained import (
    evaluate_boundary_on_groups,
    fixed_basis,
    parse_group_specs,
    select_group_constrained_boundary,
)


FULL_METHOD = "full_vi"
GROUP_METHOD = "group_constrained_rd"


def construct_group_constrained_boundary(
    map_label: str,
    rows: Tuple[str, ...],
    grid: GridWorld,
    args: argparse.Namespace,
) -> Tuple[List[int], Dict[str, object], float]:
    lens_groups = parse_group_specs(args.group_lens_groups)
    recipe = dict(LEARNED_RECIPES[args.group_recipe])
    basis = fixed_basis(
        map_label,
        grid=grid,
        kinds=args.group_fixed_basis_kinds,
        gamma=args.gamma,
        slip=args.current_slip,
        top_fraction=args.group_probe_top_fraction,
        random_count=args.group_fixed_random_count,
    )
    endpoint_boundary = sorted(set(grid.symbol_states("SG")).intersection(set(basis)))
    endpoint_eval, _endpoint_rows = evaluate_boundary_on_groups(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=endpoint_boundary,
        lens_groups=lens_groups,
        budgets={group: 0.0 for group in lens_groups},
        test_probes=args.group_test_probes,
        gamma=args.gamma,
        slip=args.current_slip,
        edge_weight=args.group_edge_weight,
        probe_top_fraction=args.group_probe_top_fraction,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.group_cvar_alpha,
    )
    initial_group_risks: Dict[str, float] = endpoint_eval["group_risks"]  # type: ignore[assignment]
    budgets = {
        group: float(args.group_budget_frac) * float(initial_group_risks.get(group, 0.0))
        for group in lens_groups
    }
    boundary, trace, _candidates, _probes, selection_time = select_group_constrained_boundary(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        lens_groups=lens_groups,
        budgets=budgets,
        gamma=args.gamma,
        slip=args.current_slip,
        lambda_struct=args.group_lambda_struct,
        edge_weight=args.group_edge_weight,
        probe_top_fraction=args.group_probe_top_fraction,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.group_cvar_alpha,
        max_splits=args.group_max_splits,
        score_mode=args.group_score_mode,
        rate_tie_break=args.group_rate_tie_break,
        beam_width=args.group_beam_width,
        beam_expand=args.group_beam_expand,
    )
    final_eval, _final_rows = evaluate_boundary_on_groups(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        test_probes=args.group_test_probes,
        gamma=args.gamma,
        slip=args.current_slip,
        edge_weight=args.group_edge_weight,
        probe_top_fraction=args.group_probe_top_fraction,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.group_cvar_alpha,
    )
    constructor = {
        "constructor_method": GROUP_METHOD,
        "n_basis": len(basis),
        "budget_frac": args.group_budget_frac,
        "budgets": budgets,
        "initial_group_risks": initial_group_risks,
        "final_group_risks": final_eval["group_risks"],
        "final_group_violations": final_eval["group_violations"],
        "group_total_violation": final_eval["total_violation"],
        "group_max_violation": final_eval["max_violation"],
        "group_all_feasible": final_eval["all_groups_feasible"],
        "group_test_bits_mean": final_eval["test_bits_mean"],
        "group_test_bits_cvar": final_eval["test_bits_cvar"],
        "stop_reason": trace[-1]["stop_reason"] if trace else "none",
    }
    return sorted(set(boundary)), constructor, selection_time


def construct_benchmark_boundary(
    method_spec: str,
    map_label: str,
    rows: Tuple[str, ...],
    grid: GridWorld,
    slip: float,
    args: argparse.Namespace,
) -> Tuple[List[int], str, Dict[str, object], float]:
    if method_spec == GROUP_METHOD:
        args.current_slip = slip
        boundary, constructor, selection_time = construct_group_constrained_boundary(
            map_label=map_label,
            rows=rows,
            grid=grid,
            args=args,
        )
        return boundary, GROUP_METHOD, constructor, selection_time

    actual_method = resolve_method_spec(method_spec, grid)
    started = time.perf_counter()
    boundary, constructor = construct_boundary(
        method=actual_method,
        map_name=map_label,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=args.gamma,
        max_splits=args.max_splits,
        seed=args.seed,
    )
    return sorted(set(boundary)), actual_method, constructor, time.perf_counter() - started


def graph_family(method: str) -> str:
    if method == GROUP_METHOD:
        return "ours:group_constrained_rd"
    return method_family(method)


def full_vi_row(
    family: str,
    size: int,
    map_label: str,
    slip: float,
    grid: GridWorld,
    full_result: Mapping[str, object],
    pi_result: Mapping[str, object],
) -> Dict[str, object]:
    transition_nnz = transition_nnz_proxy(grid, slip)
    full_time = float(full_result["time_sec"])
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method_spec": FULL_METHOD,
        "method": FULL_METHOD,
        "method_family": "full_mdp:value_iteration",
        "n_states": grid.n_states,
        "n_boundary": grid.n_states,
        "n_edges_valid": "",
        "state_compression_ratio": 1.0,
        "transition_nnz_proxy": transition_nnz,
        "kernel_nnz": transition_nnz,
        "memory_compression_ratio": 1.0,
        "full_vi_iterations": int(full_result["iterations"]),
        "full_vi_time_sec": full_time,
        "full_vi_backup_count": int(full_result["backup_count"]),
        "full_pi_iterations": int(pi_result["iterations"]),
        "full_pi_time_sec": float(pi_result["time_sec"]),
        "full_pi_improvement_backup_count": int(pi_result["improvement_backup_count"]),
        "construction_time_sec": 0.0,
        "kernel_time_sec": 0.0,
        "smdp_solve_time_sec": full_time,
        "compressed_total_time_sec": full_time,
        "planning_time_speedup_vs_full_vi": 1.0,
        "total_time_speedup_vs_full_vi": 1.0,
        "backup_compression_ratio": 1.0,
        "start_gap": 0.0,
        "value_gap_max": 0.0,
        "occupancy_struct_hidden_distinct": 0.0,
        "struct_hidden_distinct_cvar95": 0.0,
        "success_rate": 1.0,
        "primitive_steps_mean": "",
        "option_steps_mean": "",
        "hidden_audit_distinct_mean": 0.0,
        "description_length_proxy": transition_nnz,
        "group_all_feasible": "",
        "group_test_bits_cvar": "",
        "constructor_stop_reason": "full_mdp",
    }


def build_graph_row(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    method_spec: str,
    slip: float,
    full_result: Mapping[str, object],
    pi_result: Mapping[str, object],
    args: argparse.Namespace,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    start_state = grid.symbol_states("S")[0]
    goal_state = grid.symbol_states("G")[0]
    boundary, method, constructor, construction_time = construct_benchmark_boundary(
        method_spec=method_spec,
        map_label=map_label,
        rows=rows,
        grid=grid,
        slip=slip,
        args=args,
    )
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    if start_state not in boundary_to_pos or goal_state not in boundary_to_pos:
        raise ValueError(f"{method_spec} boundary must contain start and goal on {map_label}.")

    residual_boundary = candidate_boundary_states(
        grid=grid,
        kind=args.audit_lens,
        goal_state=goal_state,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.audit_top_fraction,
    )
    soft_state_cost = critical_saliency(
        grid=grid,
        kind=args.soft_kind,
        goal_state=goal_state,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.soft_top_fraction,
    )
    v_full = np.asarray(full_result["V"], dtype=float)
    boundary_values = v_full[np.array(boundary, dtype=int)]
    value_scale_task = max(
        1.0,
        abs(float(v_full[start_state])),
        float(np.percentile(np.abs(boundary_values), 95)) if len(boundary_values) else 1.0,
    )

    kernel_started = time.perf_counter()
    reductions, valid_actions, _policies, _metadata, edge_rows = build_first_boundary_reductions(
        grid=grid,
        boundary=boundary,
        candidate_boundary=boundary,
        residual_boundary=residual_boundary,
        soft_state_cost=soft_state_cost,
        value_scale_task=value_scale_task,
        slip=slip,
        gamma=args.gamma,
        local_horizon=args.local_horizon,
        hidden_threshold=args.hidden_threshold,
        soft_threshold=args.soft_threshold,
        residual_threshold=args.residual_threshold,
        residual_reward_weight=args.residual_reward_weight,
        residual_hit_weight=args.residual_hit_weight,
        residual_threshold_mode=args.residual_threshold_mode,
        compute_struct_distinct=not args.no_struct_distinct,
        proposal_boundary=residual_boundary,
    )
    kernel_time = time.perf_counter() - kernel_started
    smdp_result = smdp_value_iteration_measured(
        reductions=reductions,
        valid_actions=valid_actions,
        goal_pos=boundary_to_pos[goal_state],
    )

    policy = smdp_result["policy"]
    occupancy = policy_boundary_occupancy(
        reductions=reductions,
        policy_smdp=policy,
        start_pos=boundary_to_pos[start_state],
        goal_pos=boundary_to_pos[goal_state],
    )
    occupancy_struct_hidden_distinct = 0.0
    occupancy_model_residual = 0.0
    for edge_row in edge_rows:
        src_pos = boundary_to_pos.get(int(edge_row["src_state"]))
        if src_pos is None:
            continue
        if str(edge_row["option"]) != str(policy.get(src_pos)) or not bool(edge_row["edge_valid"]):
            continue
        occ = float(occupancy[src_pos])
        occupancy_struct_hidden_distinct += occ * float(edge_row["struct_hidden_distinct"])
        occupancy_model_residual += occ * float(edge_row["model_residual"])

    v_smdp = np.asarray(smdp_result["V"], dtype=float)
    boundary_full = v_full[np.array(boundary, dtype=int)]
    nonterminal = np.ones(len(boundary), dtype=bool)
    nonterminal[boundary_to_pos[goal_state]] = False
    start_gap = float(abs(v_smdp[boundary_to_pos[start_state]] - v_full[start_state]))
    value_gap_max = (
        float(np.max(np.abs(v_smdp[nonterminal] - boundary_full[nonterminal])))
        if np.any(nonterminal)
        else 0.0
    )
    valid_struct_distinct = [
        float(row["struct_hidden_distinct"])
        for row in edge_rows
        if bool(row["edge_valid"])
    ]
    rollout = rollout_smdp_policy(
        grid=grid,
        boundary=boundary,
        audit_boundary=residual_boundary,
        policy_smdp={int(k): str(v) for k, v in dict(policy).items()},
        slip=slip,
        n_rollouts=args.n_rollouts,
        seed=stable_method_seed(args.seed, method_spec, map_label, slip),
        max_steps=args.max_steps or max(100, 12 * grid.n_states),
        max_option_steps=args.max_option_steps or max(20, 4 * grid.n_states),
    )

    transition_nnz = transition_nnz_proxy(grid, slip)
    k_nnz = kernel_nnz(reductions, valid_actions)
    smdp_time = float(smdp_result["time_sec"])
    full_time = float(full_result["time_sec"])
    total_time = construction_time + kernel_time + smdp_time
    row: Dict[str, object] = {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method_spec": method_spec,
        "method": method,
        "method_family": graph_family(method),
        "n_states": grid.n_states,
        "n_boundary": len(boundary),
        "n_edges_valid": valid_edge_count(valid_actions),
        "state_compression_ratio": float(grid.n_states) / max(1.0, float(len(boundary))),
        "transition_nnz_proxy": transition_nnz,
        "kernel_nnz": k_nnz,
        "memory_compression_ratio": transition_nnz / max(1.0, float(k_nnz)),
        "full_vi_iterations": int(full_result["iterations"]),
        "full_vi_time_sec": full_time,
        "full_vi_backup_count": int(full_result["backup_count"]),
        "full_pi_iterations": int(pi_result["iterations"]),
        "full_pi_time_sec": float(pi_result["time_sec"]),
        "full_pi_improvement_backup_count": int(pi_result["improvement_backup_count"]),
        "construction_time_sec": construction_time,
        "kernel_time_sec": kernel_time,
        "smdp_iterations": int(smdp_result["iterations"]),
        "smdp_solve_time_sec": smdp_time,
        "smdp_edge_backup_count": int(smdp_result["edge_backup_count"]),
        "compressed_total_time_sec": total_time,
        "planning_time_speedup_vs_full_vi": full_time / max(1e-12, smdp_time),
        "total_time_speedup_vs_full_vi": full_time / max(1e-12, total_time),
        "backup_compression_ratio": float(full_result["backup_count"]) / max(
            1.0,
            float(smdp_result["edge_backup_count"]),
        ),
        "start_gap": start_gap,
        "value_gap_max": value_gap_max,
        "occupancy_struct_hidden_distinct": float(occupancy_struct_hidden_distinct),
        "occupancy_model_residual": float(occupancy_model_residual),
        "struct_hidden_distinct_cvar95": tail_cvar(valid_struct_distinct),
        "description_length_proxy": float(len(boundary)) + float(valid_edge_count(valid_actions)),
        "constructor_stop_reason": constructor.get("stop_reason", ""),
        "constructor_last_split_source": constructor.get("last_split_source", ""),
        "constructor_last_split_state": constructor.get("last_split_state", ""),
        "group_all_feasible": constructor.get("group_all_feasible", ""),
        "group_total_violation": constructor.get("group_total_violation", ""),
        "group_test_bits_cvar": constructor.get("group_test_bits_cvar", ""),
        "boundary": list(boundary),
    }
    row.update(rollout)
    return row


def finite_float(value: object) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "map",
        "slip",
        "method_spec",
        "method",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "planning_time_speedup_vs_full_vi",
        "total_time_speedup_vs_full_vi",
        "backup_compression_ratio",
        "start_gap",
        "value_gap_max",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
        "success_rate",
        "primitive_steps_mean",
        "hidden_audit_distinct_mean",
        "group_all_feasible",
        "group_test_bits_cvar",
    ]
    graph_rows = [row for row in rows if row.get("method_spec") != FULL_METHOD]
    best_planning = max(
        (finite_float(row.get("planning_time_speedup_vs_full_vi")) or 0.0 for row in graph_rows),
        default=0.0,
    )
    max_gap = max((finite_float(row.get("start_gap")) or 0.0 for row in graph_rows), default=0.0)
    lines = [
        "# Core Benchmark",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"slips = {list(args.slips)}",
        f"methods = {list(args.methods)}",
        f"gamma = {args.gamma}, n_rollouts = {args.n_rollouts}",
        "",
        "This table evaluates full MDP value iteration and graph-SMDP planning under the same map/slip suite. "
        "Graph rows include boundary construction, exact first-boundary kernels, SMDP solve cost, value gap, and hidden-boundary audit metrics.",
        "",
        f"- best planning-only speedup over full VI in this run: `{best_planning:.4g}x`",
        f"- worst graph start-value gap in this run: `{max_gap:.4g}`",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified core benchmark across full VI, RD graph methods, and option-discovery baselines."
    )
    parser.add_argument(
        "--map-specs",
        nargs="+",
        default=["corridor:16,32", "open_room:7", "four_rooms:7", "maze:9"],
    )
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
    parser.add_argument(
        "--methods",
        nargs="+",
        default=[
            FULL_METHOD,
            "graph_rd_joint",
            "graph_rd_surrogate_joint",
            GROUP_METHOD,
            "eigenoptions_sqrt",
            "betweenness_sqrt",
            "random_landmarks_sqrt",
            "coverage_sqrt",
        ],
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=12)
    parser.add_argument("--n-rollouts", type=int, default=40)
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
    parser.add_argument("--no-struct-distinct", action="store_true")
    parser.add_argument("--group-recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument(
        "--group-lens-groups",
        nargs="+",
        default=[
            "topology:junction,bottleneck,turn_articulation,betweenness",
            "value:value_gradient",
            "stochastic:transition_entropy",
        ],
    )
    parser.add_argument("--group-test-probes", nargs="+", default=["combined"])
    parser.add_argument(
        "--group-fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--group-fixed-random-count", type=int, default=2)
    parser.add_argument("--group-budget-frac", type=float, default=0.25)
    parser.add_argument("--group-risk-kind", choices=["mean", "cvar", "max"], default="cvar")
    parser.add_argument("--group-score-mode", choices=["reduction", "reduction_per_rate", "lexicographic"], default="reduction")
    parser.add_argument("--group-rate-tie-break", type=float, default=1e-4)
    parser.add_argument("--group-probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--group-lambda-struct", type=float, default=8.0)
    parser.add_argument("--group-cvar-alpha", type=float, default=0.8)
    parser.add_argument(
        "--group-edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--group-max-splits", type=int, default=5)
    parser.add_argument("--group-beam-width", type=int, default=2)
    parser.add_argument("--group-beam-expand", type=int, default=4)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/core_benchmark"))
    args = parser.parse_args()

    rows_out: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        grid = GridWorld(map_rows)
        goal = grid.symbol_states("G")[0]
        for slip in args.slips:
            full_result = full_value_iteration_measured(
                grid=grid,
                goal_state=goal,
                gamma=args.gamma,
                slip=slip,
            )
            pi_result = full_policy_iteration_measured(
                grid=grid,
                goal_state=goal,
                gamma=args.gamma,
                slip=slip,
            )
            for method_spec in args.methods:
                if method_spec == FULL_METHOD:
                    rows_out.append(full_vi_row(family, size, map_label, slip, grid, full_result, pi_result))
                else:
                    rows_out.append(
                        build_graph_row(
                            family=family,
                            size=size,
                            map_label=map_label,
                            rows=map_rows,
                            method_spec=method_spec,
                            slip=slip,
                            full_result=full_result,
                            pi_result=pi_result,
                            args=args,
                        )
                    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "core_benchmark.csv", rows_out)
    (args.out_dir / "core_benchmark.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows_out, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
