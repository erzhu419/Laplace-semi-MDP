#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import (
    BellmanKronReduction,
    GridWorld,
    primitive_value_iteration,
    shortest_path_policy_to_target,
    smdp_value_iteration,
)
from run_first_boundary_targeted import (
    MAPS,
    build_first_boundary_reductions,
    candidate_boundary_states,
    critical_saliency,
    markdown_table,
)
from run_option_algorithm_comparison import (
    construct_boundary,
    json_default,
    parse_option_target_position,
    rollout_smdp_policy,
    sample_action,
    stable_method_seed,
    write_csv_all_fields,
)


def exact_first_boundary_model(
    method: str,
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    args: argparse.Namespace,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    boundary, constructor = construct_boundary(
        method=method,
        map_name=map_name,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=args.gamma,
        max_splits=args.max_splits,
        seed=args.seed,
    )
    boundary = sorted(set(boundary))
    residual_boundary = candidate_boundary_states(
        grid,
        kind=args.audit_lens,
        goal_state=goal,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.audit_top_fraction,
    )
    soft_state_cost = critical_saliency(
        grid,
        kind=args.soft_kind,
        goal_state=goal,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.soft_top_fraction,
    )
    V_full = primitive_value_iteration(grid, goal_state=goal, gamma=args.gamma, slip=slip)
    boundary_values = V_full[np.array(boundary, dtype=int)]
    value_scale_task = max(
        1.0,
        abs(float(V_full[grid.symbol_states("S")[0]])),
        float(np.percentile(np.abs(boundary_values), 95)) if len(boundary_values) > 0 else 1.0,
    )
    reductions, valid_actions, _policies, _metadata, _edge_rows = build_first_boundary_reductions(
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
        compute_struct_distinct=False,
        proposal_boundary=residual_boundary,
    )
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    V_exact, policy_exact = smdp_value_iteration(
        reductions,
        goal_boundary_position=boundary_to_pos[goal],
        valid_actions=valid_actions,
    )
    return {
        "grid": grid,
        "boundary": boundary,
        "residual_boundary": residual_boundary,
        "constructor": constructor,
        "reductions": reductions,
        "valid_actions": valid_actions,
        "V_full": V_full,
        "V_exact": V_exact,
        "policy_exact": policy_exact,
        "start_pos": boundary_to_pos[grid.symbol_states("S")[0]],
        "goal_pos": boundary_to_pos[goal],
    }


def empty_reduction(boundary: Sequence[int], gamma: float) -> BellmanKronReduction:
    n = len(boundary)
    gamma_terminal = np.zeros((n, n), dtype=float)
    reward = np.zeros(n, dtype=float)
    return BellmanKronReduction(
        boundary=np.array(boundary, dtype=int),
        interior=np.array([], dtype=int),
        gamma=gamma,
        gamma_terminal=gamma_terminal,
        reward=reward,
        laplacian=np.eye(n, dtype=float) - gamma_terminal,
        hit_probability=np.zeros((n, n), dtype=float),
        expected_tau=np.full((n, n), np.nan, dtype=float),
    )


def estimate_option_model_mc(
    grid: GridWorld,
    boundary: Sequence[int],
    slip: float,
    gamma: float,
    samples_per_option: int,
    seed: int,
    max_option_steps: int,
) -> Tuple[Dict[str, BellmanKronReduction], Dict[str, np.ndarray], Dict[str, float]]:
    boundary = sorted(set(boundary))
    n_boundary = len(boundary)
    boundary_set = set(boundary)
    rng = np.random.default_rng(seed)
    reductions: Dict[str, BellmanKronReduction] = {}
    valid_actions: Dict[str, np.ndarray] = {}
    target_policy_cache: Dict[int, object] = {}
    timeout_count = 0
    rollout_count = 0

    for target_pos, target_state in enumerate(boundary):
        if target_state not in target_policy_cache:
            target_policy_cache[target_state] = shortest_path_policy_to_target(
                grid,
                target=target_state,
                slip=slip,
            )
        primitive_policy = target_policy_cache[target_state]
        for src_pos, src_state in enumerate(boundary):
            if src_pos == target_pos:
                continue
            label = f"fb_{src_pos:03d}_to_{target_pos:03d}"
            reward_sum = 0.0
            hit_count = 0
            hit_counts = np.zeros(n_boundary, dtype=float)
            gamma_sums = np.zeros(n_boundary, dtype=float)
            tau_sums = np.zeros(n_boundary, dtype=float)
            terminals = boundary_set - {src_state}
            for _ in range(samples_per_option):
                rollout_count += 1
                state = src_state
                discounted_reward = 0.0
                discount = 1.0
                hit_pos = None
                tau = 0
                for step in range(1, max_option_steps + 1):
                    discounted_reward += discount * float(grid.step_reward)
                    dist = primitive_policy(state)
                    action = sample_action(dist, rng)
                    state = grid.next_state(state, action)
                    discount *= gamma
                    tau = step
                    if state in terminals:
                        hit_pos = boundary.index(state)
                        break
                reward_sum += discounted_reward
                if hit_pos is None:
                    timeout_count += 1
                    continue
                hit_count += 1
                hit_counts[hit_pos] += 1.0
                gamma_sums[hit_pos] += discount
                tau_sums[hit_pos] += float(tau)

            reduction = empty_reduction(boundary, gamma=gamma)
            if samples_per_option > 0:
                reduction.reward[src_pos] = reward_sum / float(samples_per_option)
                reduction.hit_probability[src_pos, :] = hit_counts / float(samples_per_option)
                reduction.gamma_terminal[src_pos, :] = gamma_sums / float(samples_per_option)
                reduction.expected_tau[src_pos, :] = np.divide(
                    tau_sums,
                    hit_counts,
                    out=np.full(n_boundary, np.nan, dtype=float),
                    where=hit_counts > 0,
                )
            reduction = BellmanKronReduction(
                boundary=reduction.boundary,
                interior=reduction.interior,
                gamma=reduction.gamma,
                gamma_terminal=reduction.gamma_terminal,
                reward=reduction.reward,
                laplacian=np.eye(n_boundary, dtype=float) - reduction.gamma_terminal,
                hit_probability=reduction.hit_probability,
                expected_tau=reduction.expected_tau,
            )
            valid = np.zeros(n_boundary, dtype=bool)
            valid[src_pos] = hit_count > 0
            reductions[label] = reduction
            valid_actions[label] = valid

    diagnostics = {
        "mc_option_rollouts": float(rollout_count),
        "mc_timeout_count": float(timeout_count),
        "mc_timeout_rate": float(timeout_count / max(1, rollout_count)),
    }
    return reductions, valid_actions, diagnostics


def evaluate_fixed_policy_exact(
    reductions: Mapping[str, BellmanKronReduction],
    policy: Mapping[int, str],
    goal_pos: int,
) -> np.ndarray:
    first = next(iter(reductions.values()))
    n = len(first.boundary)
    A = np.eye(n, dtype=float)
    b = np.zeros(n, dtype=float)
    for pos in range(n):
        if pos == goal_pos:
            A[pos, :] = 0.0
            A[pos, pos] = 1.0
            b[pos] = 0.0
            continue
        action = policy.get(pos)
        if action not in reductions:
            return np.full(n, np.nan, dtype=float)
        red = reductions[action]
        A[pos, :] -= red.gamma_terminal[pos, :]
        b[pos] = red.reward[pos]
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, b, rcond=None)[0]


def kernel_error_summary(
    exact: Mapping[str, BellmanKronReduction],
    estimated: Mapping[str, BellmanKronReduction],
) -> Dict[str, float]:
    gamma_l1: List[float] = []
    reward_abs: List[float] = []
    hit_l1: List[float] = []
    for label, exact_red in exact.items():
        est_red = estimated.get(label)
        if est_red is None:
            continue
        target_pos = parse_option_target_position(label)
        try:
            src_pos = int(label.split("_", 2)[1])
        except (IndexError, ValueError):
            src_pos = None
        if src_pos is None or target_pos is None:
            continue
        gamma_l1.append(float(np.sum(np.abs(exact_red.gamma_terminal[src_pos] - est_red.gamma_terminal[src_pos]))))
        hit_l1.append(float(np.sum(np.abs(exact_red.hit_probability[src_pos] - est_red.hit_probability[src_pos]))))
        reward_abs.append(float(abs(exact_red.reward[src_pos] - est_red.reward[src_pos])))
    return {
        "kernel_gamma_l1_mean": float(np.mean(gamma_l1)) if gamma_l1 else float("nan"),
        "kernel_hit_l1_mean": float(np.mean(hit_l1)) if hit_l1 else float("nan"),
        "kernel_reward_abs_mean": float(np.mean(reward_abs)) if reward_abs else float("nan"),
    }


def policy_disagreement(
    exact_policy: Mapping[int, str],
    estimated_policy: Mapping[int, str],
    goal_pos: int,
) -> float:
    positions = [pos for pos in exact_policy.keys() if pos != goal_pos]
    if not positions:
        return 0.0
    return float(
        sum(1 for pos in positions if exact_policy.get(pos) != estimated_policy.get(pos))
        / len(positions)
    )


def run_noise_case(
    method: str,
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    exact_model = exact_first_boundary_model(method, map_name, rows, slip, args)
    grid = exact_model["grid"]
    boundary = exact_model["boundary"]
    residual_boundary = exact_model["residual_boundary"]
    exact_reductions = exact_model["reductions"]
    V_exact = exact_model["V_exact"]
    exact_policy = exact_model["policy_exact"]
    start_pos = int(exact_model["start_pos"])
    goal_pos = int(exact_model["goal_pos"])
    out: List[Dict[str, object]] = []

    for samples_per_option in args.sample_sizes:
        for replicate in range(args.replicates):
            seed = stable_method_seed(
                args.seed + 1009 * replicate,
                f"{method}_kernel_{samples_per_option}",
                map_name,
                slip,
            )
            estimated_reductions, estimated_valid, mc_diag = estimate_option_model_mc(
                grid=grid,
                boundary=boundary,
                slip=slip,
                gamma=args.gamma,
                samples_per_option=int(samples_per_option),
                seed=seed,
                max_option_steps=args.max_option_steps or max(20, 4 * grid.n_states),
            )
            row: Dict[str, object] = {
                "method": method,
                "map": map_name,
                "slip": slip,
                "n_boundary": len(boundary),
                "sample_rollouts_per_option": int(samples_per_option),
                "replicate": replicate,
                "feasible_estimated_model": True,
            }
            try:
                V_estimated, estimated_policy = smdp_value_iteration(
                    estimated_reductions,
                    goal_boundary_position=goal_pos,
                    valid_actions=estimated_valid,
                )
            except ValueError as exc:
                row.update(
                    {
                        "feasible_estimated_model": False,
                        "infeasible_reason": str(exc),
                        "policy_value_loss_exact": float("inf"),
                        "estimated_model_start_error": float("inf"),
                        "policy_disagreement": 1.0,
                    }
                )
                row.update(mc_diag)
                out.append(row)
                continue

            V_policy_exact = evaluate_fixed_policy_exact(
                reductions=exact_reductions,
                policy=estimated_policy,
                goal_pos=goal_pos,
            )
            rollout = rollout_smdp_policy(
                grid=grid,
                boundary=boundary,
                audit_boundary=residual_boundary,
                policy_smdp=estimated_policy,
                slip=slip,
                n_rollouts=args.n_eval_rollouts,
                seed=stable_method_seed(seed, "eval", map_name, slip),
                max_steps=args.max_steps or max(100, 12 * grid.n_states),
                max_option_steps=args.max_option_steps or max(20, 4 * grid.n_states),
            )
            row.update(mc_diag)
            row.update(kernel_error_summary(exact_reductions, estimated_reductions))
            row.update(rollout)
            row.update(
                {
                    "start_value_exact_opt": float(V_exact[start_pos]),
                    "start_value_estimated_model": float(V_estimated[start_pos]),
                    "start_value_exact_under_est_policy": float(V_policy_exact[start_pos]),
                    "estimated_model_start_error": float(abs(V_estimated[start_pos] - V_exact[start_pos])),
                    "policy_value_loss_exact": float(max(0.0, V_exact[start_pos] - V_policy_exact[start_pos])),
                    "policy_disagreement": policy_disagreement(exact_policy, estimated_policy, goal_pos),
                }
            )
            out.append(row)
    return out


def aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[object, object, object, object], List[Mapping[str, object]]] = {}
    for row in rows:
        key = (row["method"], row["map"], row["slip"], row["sample_rollouts_per_option"])
        groups.setdefault(key, []).append(row)
    metrics = [
        "policy_value_loss_exact",
        "estimated_model_start_error",
        "policy_disagreement",
        "kernel_gamma_l1_mean",
        "kernel_hit_l1_mean",
        "kernel_reward_abs_mean",
        "success_rate",
        "primitive_steps_mean",
        "hidden_audit_distinct_mean",
        "mc_timeout_rate",
    ]
    out: List[Dict[str, object]] = []
    for key, group_rows in groups.items():
        method, map_name, slip, samples = key
        agg: Dict[str, object] = {
            "method": method,
            "map": map_name,
            "slip": slip,
            "sample_rollouts_per_option": samples,
            "n_boundary": group_rows[0].get("n_boundary", ""),
            "replicates": len(group_rows),
        }
        for metric in metrics:
            values = np.asarray([float(row.get(metric, np.nan)) for row in group_rows], dtype=float)
            finite = values[np.isfinite(values)]
            agg[f"{metric}_mean"] = float(np.mean(finite)) if len(finite) else float("nan")
            agg[f"{metric}_std"] = float(np.std(finite)) if len(finite) else float("nan")
        out.append(agg)
    return sorted(
        out,
        key=lambda row: (
            str(row["method"]),
            str(row["map"]),
            float(row["slip"]),
            int(row["sample_rollouts_per_option"]),
        ),
    )


def write_report(
    aggregate: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    columns = [
        "method",
        "map",
        "slip",
        "n_boundary",
        "sample_rollouts_per_option",
        "policy_value_loss_exact_mean",
        "estimated_model_start_error_mean",
        "policy_disagreement_mean",
        "kernel_gamma_l1_mean_mean",
        "kernel_reward_abs_mean_mean",
        "success_rate_mean",
        "hidden_audit_distinct_mean_mean",
    ]
    lines = [
        "# Rollout-Estimated SMDP Kernel Noise Curve",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"methods = {list(args.methods)}",
        f"sample_sizes = {list(args.sample_sizes)}, replicates = {args.replicates}",
        f"maps = {list(args.maps)}, slips = {list(args.slips)}, gamma = {args.gamma}",
        "",
        "Each row estimates first-boundary SMDP kernels from Monte Carlo option rollouts, solves planning on the estimated model, then evaluates that abstract policy on the exact SMDP model and by original-environment rollouts.",
        "",
        markdown_table(aggregate, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate first-boundary SMDP kernels from rollouts and measure noise.")
    parser.add_argument("--maps", nargs="+", default=["maze"])
    parser.add_argument("--slips", type=float, nargs="+", default=[0.05])
    parser.add_argument("--methods", nargs="+", default=["betweenness_12", "graph_rd_joint"])
    parser.add_argument("--sample-sizes", type=int, nargs="+", default=[1, 2, 5, 10, 20, 50])
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-eval-rollouts", type=int, default=100)
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
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/smdp_kernel_noise_maze_slip005"),
    )
    args = parser.parse_args()

    rows: List[Dict[str, object]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        for slip in args.slips:
            for method in args.methods:
                rows.extend(run_noise_case(method, map_name, MAPS[map_name], slip, args))
    aggregate = aggregate_rows(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "kernel_noise_raw.csv", rows)
    write_csv_all_fields(args.out_dir / "kernel_noise_aggregate.csv", aggregate)
    (args.out_dir / "kernel_noise_raw.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(aggregate, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
