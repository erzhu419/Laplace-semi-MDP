#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import BellmanKronReduction, GridWorld, bellman_kron_reduce, bellman_kron_reduce_truncated
from compression_experiment_utils import parse_map_specs, resolve_method_spec
from finite_mdp_adapter import full_value_iteration, shortest_path_target_policy_kernel
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import construct_boundary, json_default, write_csv_all_fields
from state_abstraction_baselines import gridworld_finite_mdp


def truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def read_existing(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def option_bellman_backup(
    reductions: Sequence[BellmanKronReduction],
    value: np.ndarray,
    valid: np.ndarray,
    terminal_positions: Sequence[int],
) -> np.ndarray:
    q = np.stack([red.reward + red.gamma_terminal @ value for red in reductions], axis=0)
    q = np.where(valid, q, -np.inf)
    backed = np.max(q, axis=0)
    if terminal_positions:
        backed[np.asarray(terminal_positions, dtype=int)] = 0.0
    if np.any(~np.isfinite(backed)):
        bad = np.flatnonzero(~np.isfinite(backed)).tolist()
        raise ValueError(f"No valid option at positions {bad}.")
    return backed


def solve_option_model(
    reductions: Sequence[BellmanKronReduction],
    valid: np.ndarray,
    terminal_positions: Sequence[int],
    tol: float,
    max_iterations: int = 20_000,
) -> Tuple[np.ndarray, int]:
    value = np.zeros(len(reductions[0].boundary), dtype=float)
    for iteration in range(1, max_iterations + 1):
        backed = option_bellman_backup(reductions, value, valid, terminal_positions)
        if float(np.max(np.abs(backed - value))) < tol:
            return backed, iteration
        value = backed
    return value, max_iterations


def solve_finite_option_actions(
    policy_kernels: Sequence[Tuple[np.ndarray, np.ndarray]],
    target_states: Sequence[int],
    terminal_states: Sequence[int],
    gamma: float,
    tol: float,
) -> np.ndarray:
    n_states = policy_kernels[0][0].shape[0]
    terminal_set = set(int(state) for state in terminal_states)
    target_to_option = {int(target): index for index, target in enumerate(target_states)}
    value = np.zeros(n_states, dtype=float)
    for _iteration in range(20_000):
        old = value.copy()
        q = np.stack([reward + gamma * transition @ old for transition, reward in policy_kernels], axis=0)
        for state, option in target_to_option.items():
            if state not in terminal_set:
                q[option, state] = -np.inf
        value = np.max(q, axis=0)
        if terminal_set:
            value[np.asarray(sorted(terminal_set), dtype=int)] = 0.0
        if float(np.max(np.abs(value - old))) < tol:
            break
    return value


def valid_option_mask(
    boundary: Sequence[int],
    target_states: Sequence[int],
    terminal_states: Sequence[int],
) -> np.ndarray:
    valid = np.ones((len(target_states), len(boundary)), dtype=bool)
    boundary_pos = {int(state): pos for pos, state in enumerate(boundary)}
    terminal_set = set(int(state) for state in terminal_states)
    for option, target in enumerate(target_states):
        if int(target) in boundary_pos and int(target) not in terminal_set:
            valid[option, boundary_pos[int(target)]] = False
    for terminal in terminal_set:
        if terminal in boundary_pos:
            valid[:, boundary_pos[terminal]] = True
    return valid


def contraction_modulus(
    reductions: Sequence[BellmanKronReduction],
    terminal_positions: Sequence[int],
) -> float:
    terminal_set = set(int(pos) for pos in terminal_positions)
    return max(
        (
            float(np.sum(np.abs(red.gamma_terminal[pos])))
            for red in reductions
            for pos in range(len(red.boundary))
            if pos not in terminal_set
        ),
        default=0.0,
    )


def run_case(
    family: str,
    size: int,
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    method_spec: str,
    args: argparse.Namespace,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    start_state = grid.symbol_states("S")[0]
    goal_state = grid.symbol_states("G")[0]
    mdp = gridworld_finite_mdp(grid, goal_state=goal_state, slip=slip)
    full_value, full_iterations = full_value_iteration(mdp, gamma=args.gamma, tol=args.tol)

    method = resolve_method_spec(method_spec, grid)
    boundary, _constructor = construct_boundary(
        method=method,
        map_name=map_name,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=args.gamma,
        max_splits=args.max_splits,
        seed=args.seed,
    )
    boundary = sorted(set(int(state) for state in boundary).union(mdp.terminal_states, {start_state}))
    boundary_pos = {state: pos for pos, state in enumerate(boundary)}
    targets = list(boundary)
    policy_kernels = [shortest_path_target_policy_kernel(mdp, target) for target in targets]

    option_value = solve_finite_option_actions(
        policy_kernels,
        target_states=targets,
        terminal_states=mdp.terminal_states,
        gamma=args.gamma,
        tol=args.tol,
    )
    exact = [bellman_kron_reduce(P, reward, boundary, args.gamma) for P, reward in policy_kernels]
    approximate = [
        bellman_kron_reduce_truncated(
            P,
            reward,
            boundary,
            args.gamma,
            k_steps=args.truncation_steps,
            tail_tol=args.tail_tol,
        )
        for P, reward in policy_kernels
    ]
    terminal_positions = [boundary_pos[state] for state in mdp.terminal_states if state in boundary_pos]
    valid = valid_option_mask(boundary, targets, mdp.terminal_states)
    exact_value, exact_iterations = solve_option_model(exact, valid, terminal_positions, args.tol)
    kernel_value, kernel_iterations = solve_option_model(approximate, valid, terminal_positions, args.tol)

    solved_value = np.zeros(len(boundary), dtype=float)
    for _ in range(max(0, args.planning_iterations)):
        solved_value = option_bellman_backup(approximate, solved_value, valid, terminal_positions)
    planning_residual = float(
        np.max(np.abs(option_bellman_backup(approximate, solved_value, valid, terminal_positions) - solved_value))
    )

    boundary_index = np.asarray(boundary, dtype=int)
    primitive_boundary = full_value[boundary_index]
    option_boundary = option_value[boundary_index]
    option_bias = float(np.max(np.abs(primitive_boundary - option_boundary)))
    boundary_bias = float(np.max(np.abs(option_boundary - exact_value)))
    kernel_actual_gap = float(np.max(np.abs(exact_value - kernel_value)))
    planning_actual_gap = float(np.max(np.abs(kernel_value - solved_value)))
    primitive_to_solved_gap = float(np.max(np.abs(primitive_boundary - solved_value)))

    reward_residual = max(
        float(np.max(np.abs(exact_red.reward - approx_red.reward)))
        for exact_red, approx_red in zip(exact, approximate)
    )
    continuation_residual = max(
        float(np.max(np.sum(np.abs(exact_red.gamma_terminal - approx_red.gamma_terminal), axis=1)))
        for exact_red, approx_red in zip(exact, approximate)
    )
    beta = max(contraction_modulus(exact, terminal_positions), contraction_modulus(approximate, terminal_positions))
    value_max = float(np.max(np.abs(kernel_value)))
    denominator = 1.0 - beta
    kernel_bound = (
        (reward_residual + value_max * continuation_residual) / denominator
        if denominator > 0.0
        else float("inf")
    )
    planning_bound = planning_residual / denominator if denominator > 0.0 else float("inf")
    total_bound = option_bias + boundary_bias + kernel_bound + planning_bound
    triangle_actual = option_bias + boundary_bias + kernel_actual_gap + planning_actual_gap
    value_scale = max(1.0, float(np.percentile(np.abs(full_value), 95)), abs(float(full_value[start_state])))

    return {
        "map_family": family,
        "map_size": size,
        "map": map_name,
        "slip": slip,
        "method_spec": method_spec,
        "method": method,
        "n_states": mdp.n_states,
        "n_boundary": len(boundary),
        "state_compression_ratio": mdp.n_states / max(1, len(boundary)),
        "full_iterations": full_iterations,
        "exact_smdp_iterations": exact_iterations,
        "approximate_smdp_iterations": kernel_iterations,
        "planning_iterations": args.planning_iterations,
        "truncation_steps": args.truncation_steps,
        "tail_tol": args.tail_tol,
        "beta": beta,
        "option_restriction_bias": option_bias,
        "boundary_abstraction_bias": boundary_bias,
        "reward_kernel_residual": reward_residual,
        "continuation_kernel_residual_l1": continuation_residual,
        "kernel_actual_gap": kernel_actual_gap,
        "kernel_gap_bound": kernel_bound,
        "planning_residual": planning_residual,
        "planning_actual_gap": planning_actual_gap,
        "planning_gap_bound": planning_bound,
        "primitive_to_solved_gap": primitive_to_solved_gap,
        "actual_triangle_bound": triangle_actual,
        "certified_total_bound": total_bound,
        "certificate_holds": primitive_to_solved_gap <= total_bound + 1e-8,
        "normalized_primitive_to_solved_gap": primitive_to_solved_gap / value_scale,
        "normalized_certified_total_bound": total_bound / value_scale,
        "start_primitive_value": float(full_value[start_state]),
        "start_solved_value": float(solved_value[boundary_pos[start_state]]),
        "start_gap": float(abs(full_value[start_state] - solved_value[boundary_pos[start_state]])),
        "value_scale": value_scale,
        "error": "",
    }


def write_report(rows: Sequence[Mapping[str, object]], path: Path, args: argparse.Namespace) -> None:
    columns = [
        "map",
        "slip",
        "config_label",
        "method_spec",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "option_restriction_bias",
        "boundary_abstraction_bias",
        "kernel_actual_gap",
        "kernel_gap_bound",
        "planning_actual_gap",
        "planning_gap_bound",
        "primitive_to_solved_gap",
        "certified_total_bound",
        "certificate_holds",
    ]
    ok = [row for row in rows if not row.get("error")]
    lines = [
        "# Primitive-To-Graph End-To-End Gap Decomposition",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"configurations = {sorted({str(row.get('config_label', '')) for row in rows})}",
        "",
        "The option term compares primitive optimal control with per-step switching among the fixed target-policy library. The boundary term then charges committing to one option until the next retained vertex. Kernel and planning terms use contraction-residual certificates. All gaps are evaluated on the retained boundary, including the start state.",
        "",
        f"- certified rows: `{sum(1 for row in ok if truthy(row.get('certificate_holds')))}/{len(ok)}`",
        "",
        markdown_table([{column: row.get(column, "") for column in columns} for row in rows], columns),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure the four-term primitive-to-graph value-gap certificate.")
    parser.add_argument(
        "--map-specs",
        nargs="+",
        default=["corridor:16,32", "open_room:7", "four_rooms:7", "maze:9"],
    )
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["endpoints", "turn_articulation", "graph_rd_surrogate_joint"],
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--truncation-steps", type=int, default=32)
    parser.add_argument("--tail-tol", type=float, default=0.0)
    parser.add_argument("--planning-iterations", type=int, default=8)
    parser.add_argument("--config-label", default="fixed_k32_i8")
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/end_to_end_gap_decomposition"),
    )
    args = parser.parse_args()

    if args.num_shards < 1 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("Require 0 <= shard-index < num-shards and num-shards >= 1.")
    contexts = list(parse_map_specs(args.map_specs))
    jobs = [
        (family, size, map_name, map_rows, slip, method)
        for family, size, map_name, map_rows in contexts
        for slip in args.slips
        for method in args.methods
    ]
    selected = [job for index, job in enumerate(jobs) if index % args.num_shards == args.shard_index]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.out_dir / "end_to_end_gap_decomposition.csv"
    rows: List[Dict[str, object]] = read_existing(raw_path) if args.resume else []
    completed = {
        (
            str(row.get("map", "")),
            f"{float(row.get('slip', 0.0)):.12g}",
            str(row.get("method_spec", "")),
            str(row.get("config_label", "fixed_k32_i8")),
        )
        for row in rows
        if row.get("map")
    }
    for family, size, map_name, map_rows, slip, method in selected:
        key = (map_name, f"{slip:.12g}", method, args.config_label)
        if args.resume and key in completed:
            continue
        try:
            row = run_case(family, size, map_name, map_rows, slip, method, args)
            row["config_label"] = args.config_label
            rows.append(row)
        except Exception as exc:
            if not args.continue_on_error:
                raise
            rows.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_name,
                    "slip": slip,
                    "method_spec": method,
                    "config_label": args.config_label,
                    "error": repr(exc),
                }
            )
        write_csv_all_fields(raw_path, rows)

    write_csv_all_fields(raw_path, rows)
    (args.out_dir / "end_to_end_gap_decomposition.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
