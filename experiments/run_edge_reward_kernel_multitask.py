#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import (
    ACTIONS,
    GridWorld,
    action_distribution,
    first_hit_interior_occupancy,
    first_hit_reduce,
    shortest_path_policy_to_target,
    smdp_value_iteration,
    transition_matrix_for_policy,
)
from compression_experiment_utils import parse_map_specs, resolve_method_spec
from run_first_boundary_targeted import (
    build_first_boundary_reductions,
    markdown_table,
)
from run_option_algorithm_comparison import construct_boundary, json_default, write_csv_all_fields


@dataclass(frozen=True)
class EdgeKernel:
    label: str
    src_pos: int
    dst_pos: int
    src_state: int
    dst_state: int
    gamma_row: np.ndarray
    occupancy_row: np.ndarray
    policy_matrix: np.ndarray


@dataclass(frozen=True)
class FixedBoundaryModel:
    grid: GridWorld
    boundary: List[int]
    boundary_to_pos: Dict[int, int]
    edges: List[EdgeKernel]
    construction_time_sec: float
    kernel_time_sec: float
    occupancy_nnz: int
    gamma_nnz: int


def full_additive_value_iteration(
    grid: GridWorld,
    reward: np.ndarray,
    gamma: float,
    slip: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Dict[str, object]:
    start_time = time.perf_counter()
    reward = np.asarray(reward, dtype=float)
    V = np.zeros(grid.n_states, dtype=float)
    action_mats = action_transition_matrices(grid, slip=slip)
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        q_values = np.stack([reward + gamma * (P @ old) for P in action_mats], axis=0)
        V = np.max(q_values, axis=0)
        if float(np.max(np.abs(V - old))) < tol:
            break
    return {
        "V": V,
        "iterations": iteration,
        "time_sec": time.perf_counter() - start_time,
        "backup_count": iteration * grid.n_states * len(ACTIONS),
    }


def full_terminal_value_iteration(
    grid: GridWorld,
    goal_state: int,
    gamma: float,
    slip: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Dict[str, object]:
    start_time = time.perf_counter()
    V = np.zeros(grid.n_states, dtype=float)
    action_mats = action_transition_matrices(grid, slip=slip)
    reward = np.full(grid.n_states, grid.step_reward, dtype=float)
    reward[int(goal_state)] = 0.0
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        q_values = np.stack([reward + gamma * (P @ old) for P in action_mats], axis=0)
        V = np.max(q_values, axis=0)
        V[int(goal_state)] = 0.0
        if float(np.max(np.abs(V - old))) < tol:
            break
    return {
        "V": V,
        "iterations": iteration,
        "time_sec": time.perf_counter() - start_time,
        "backup_count": iteration * grid.n_states * len(ACTIONS),
    }


def action_transition_matrices(grid: GridWorld, slip: float) -> List[np.ndarray]:
    mats: List[np.ndarray] = []
    for action in ACTIONS:
        P = np.zeros((grid.n_states, grid.n_states), dtype=float)
        for state in range(grid.n_states):
            for slip_action, prob in action_distribution(action, slip=slip).items():
                P[state, grid.next_state(state, slip_action)] += prob
        mats.append(P)
    return mats


def edge_smdp_value_iteration(
    n_boundary: int,
    edges: Sequence[EdgeKernel],
    edge_rewards: np.ndarray,
    gamma_rows: np.ndarray,
    terminal_pos: int | None = None,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Dict[str, object]:
    start_time = time.perf_counter()
    outgoing: Dict[int, List[int]] = {pos: [] for pos in range(n_boundary)}
    for edge_idx, edge in enumerate(edges):
        outgoing[int(edge.src_pos)].append(edge_idx)

    V = np.zeros(n_boundary, dtype=float)
    policy: Dict[int, str] = {}
    edge_backup_count = 0
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        for src_pos in range(n_boundary):
            if terminal_pos is not None and src_pos == terminal_pos:
                V[src_pos] = 0.0
                policy[src_pos] = "TERMINAL"
                continue
            candidates = outgoing.get(src_pos, [])
            if not candidates:
                raise ValueError(f"No outgoing edge for boundary position {src_pos}.")
            q_values = [
                float(edge_rewards[edge_idx] + gamma_rows[edge_idx] @ old)
                for edge_idx in candidates
            ]
            best_local = int(np.argmax(q_values))
            best_edge_idx = candidates[best_local]
            V[src_pos] = q_values[best_local]
            policy[src_pos] = edges[best_edge_idx].label
            edge_backup_count += len(candidates)
        if float(np.max(np.abs(V - old))) < tol:
            break
    return {
        "V": V,
        "policy": policy,
        "iterations": iteration,
        "time_sec": time.perf_counter() - start_time,
        "edge_backup_count": edge_backup_count,
    }


def boundary_value_gap(smdp_values: np.ndarray, full_values: np.ndarray, boundary: Sequence[int]) -> float:
    boundary_values = np.asarray(full_values, dtype=float)[np.array(boundary, dtype=int)]
    return float(np.max(np.abs(np.asarray(smdp_values, dtype=float) - boundary_values)))


def solve_or_pinv(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    try:
        return np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A) @ B


def break_even_num_tasks(upfront_time: float, full_time: float, recurring_graph_time: float, task_count: int) -> float:
    if task_count <= 0:
        return math.nan
    full_per_task = full_time / float(task_count)
    graph_per_task = recurring_graph_time / float(task_count)
    savings_per_task = full_per_task - graph_per_task
    if savings_per_task <= 1e-12:
        return math.inf
    return float(math.ceil(upfront_time / savings_per_task))


def choose_query_states(
    grid: GridWorld,
    boundary: Sequence[int],
    max_tasks: int,
    seed: int,
    prefer_interior: bool = True,
) -> List[int]:
    start = grid.symbol_states("S")[0]
    boundary_set = set(int(state) for state in boundary)
    if prefer_interior:
        candidates = [state for state in range(grid.n_states) if state not in boundary_set and state != start]
    else:
        candidates = [state for state in range(grid.n_states) if state != start]
    if not candidates:
        candidates = [state for state in range(grid.n_states) if state != start]
    original_goals = [state for state in grid.symbol_states("G") if state in candidates]
    ordered: List[int] = []
    for state in original_goals:
        if state not in ordered:
            ordered.append(int(state))
    remaining = [state for state in candidates if state not in ordered]
    if remaining:
        rng = np.random.default_rng(seed + grid.n_states * 1291 + len(boundary_set) * 17)
        perm = rng.permutation(remaining).tolist()
        for state in perm:
            if len(ordered) >= max_tasks:
                break
            ordered.append(int(state))
    return ordered[:max_tasks]


def additive_reward_for_query(grid: GridWorld, query_state: int, kind: str, seed: int) -> np.ndarray:
    if kind == "sparse":
        reward = np.full(grid.n_states, -0.01, dtype=float)
        reward[int(query_state)] = 1.0
        return reward
    if kind == "dense":
        rng = np.random.default_rng(seed + int(query_state) * 1009 + grid.n_states * 37)
        reward = rng.uniform(-0.05, 0.05, size=grid.n_states)
        reward[int(query_state)] += 0.5
        return reward.astype(float)
    raise ValueError(f"Unknown additive reward kind: {kind!r}")


def build_fixed_boundary_model(
    map_label: str,
    rows: Tuple[str, ...],
    method_spec: str,
    gamma: float,
    slip: float,
    seed: int,
    max_splits: int,
) -> FixedBoundaryModel:
    grid = GridWorld(rows)
    start_state = grid.symbol_states("S")[0]
    actual_method = resolve_method_spec(method_spec, grid)
    t0 = time.perf_counter()
    base_boundary, _constructor = construct_boundary(
        method=actual_method,
        map_name=map_label,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=gamma,
        max_splits=max_splits,
        seed=seed,
    )
    boundary = sorted(set(int(state) for state in base_boundary).union({int(start_state)}))
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    construction_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    edges: List[EdgeKernel] = []
    for dst_pos, dst_state in enumerate(boundary):
        policy = shortest_path_policy_to_target(grid, int(dst_state), slip=slip)
        P_free, _r_free = transition_matrix_for_policy(grid, policy, absorbing=[])
        for src_pos, src_state in enumerate(boundary):
            if src_state == dst_state:
                continue
            terminals = [state for state in boundary if state != src_state]
            first_hit = first_hit_reduce(
                P=P_free,
                r=np.zeros(grid.n_states, dtype=float),
                start_state=int(src_state),
                terminals=terminals,
                gamma=gamma,
            )
            gamma_row = np.zeros(len(boundary), dtype=float)
            for term, discounted_prob in zip(first_hit.terminals, first_hit.gamma_terminal):
                term_int = int(term)
                if term_int in boundary_to_pos:
                    gamma_row[boundary_to_pos[term_int]] = float(discounted_prob)

            occupancy_row = np.zeros(grid.n_states, dtype=float)
            occupancy_row[int(src_state)] = 1.0
            interior, occupancy = first_hit_interior_occupancy(
                P=P_free,
                start_state=int(src_state),
                terminals=terminals,
                gamma=gamma,
            )
            if len(interior) > 0:
                occupancy_row[interior] += occupancy
            label = f"fb_{src_pos:03d}_to_{dst_pos:03d}"
            edges.append(
                EdgeKernel(
                    label=label,
                    src_pos=src_pos,
                    dst_pos=dst_pos,
                    src_state=int(src_state),
                    dst_state=int(dst_state),
                    gamma_row=gamma_row,
                    occupancy_row=occupancy_row,
                    policy_matrix=P_free,
                )
            )
    kernel_time = time.perf_counter() - t1
    occupancy_nnz = int(sum(np.count_nonzero(np.abs(edge.occupancy_row) > 1e-12) for edge in edges))
    gamma_nnz = int(sum(np.count_nonzero(np.abs(edge.gamma_row) > 1e-12) for edge in edges))
    return FixedBoundaryModel(
        grid=grid,
        boundary=boundary,
        boundary_to_pos=boundary_to_pos,
        edges=edges,
        construction_time_sec=construction_time,
        kernel_time_sec=kernel_time,
        occupancy_nnz=occupancy_nnz,
        gamma_nnz=gamma_nnz,
    )


def event_kernel_for_goal(
    model: FixedBoundaryModel,
    goal_state: int,
    gamma: float,
) -> Tuple[np.ndarray, np.ndarray, float, int]:
    t0 = time.perf_counter()
    edge_rewards = np.zeros(len(model.edges), dtype=float)
    gamma_rows = np.zeros((len(model.edges), len(model.boundary)), dtype=float)
    event_nnz = 0
    for edge_idx, edge in enumerate(model.edges):
        if int(goal_state) == edge.src_state:
            continue
        terminals = sorted(set(model.boundary) - {edge.src_state} | {int(goal_state)})
        first_hit = first_hit_reduce(
            P=edge.policy_matrix,
            r=np.full(model.grid.n_states, model.grid.step_reward, dtype=float),
            start_state=edge.src_state,
            terminals=terminals,
            gamma=gamma,
        )
        edge_rewards[edge_idx] = float(first_hit.reward)
        for term, discounted_prob in zip(first_hit.terminals, first_hit.gamma_terminal):
            term_int = int(term)
            if term_int == int(goal_state):
                event_nnz += 1
                continue
            if term_int in model.boundary_to_pos:
                gamma_rows[edge_idx, model.boundary_to_pos[term_int]] = float(discounted_prob)
    event_time = time.perf_counter() - t0
    event_nnz += int(np.count_nonzero(np.abs(gamma_rows) > 1e-12))
    return edge_rewards, gamma_rows, event_time, event_nnz


def goal_conditioned_event_kernel_for_goal(
    model: FixedBoundaryModel,
    goal_state: int,
    gamma: float,
    slip: float,
    base_edge_rewards: np.ndarray,
    base_gamma_rows: np.ndarray,
    base_event_time: float,
    base_event_nnz: int,
) -> Tuple[List[EdgeKernel], np.ndarray, np.ndarray, float, int, int, float, float]:
    policy_start = time.perf_counter()
    goal_policy = shortest_path_policy_to_target(model.grid, int(goal_state), slip=slip)
    P_goal, _r_goal = transition_matrix_for_policy(model.grid, goal_policy, absorbing=[])
    policy_time = time.perf_counter() - policy_start

    solve_start = time.perf_counter()
    goal = int(goal_state)
    boundary_array = np.array(model.boundary, dtype=int)
    absorbing = sorted(set(model.boundary).union({goal}))
    absorbing_set = set(absorbing)
    interior = np.array([state for state in range(model.grid.n_states) if state not in absorbing_set], dtype=int)
    boundary_pos = {state: pos for pos, state in enumerate(model.boundary)}

    if len(interior) == 0:
        P_Bg = P_goal[np.ix_(boundary_array, [goal])][:, 0]
        P_BB = P_goal[np.ix_(boundary_array, boundary_array)]
        hit_rows = gamma * P_Bg
        gamma_rows = gamma * P_BB
        step_rewards = np.full(len(model.boundary), model.grid.step_reward, dtype=float)
    else:
        P_II = P_goal[np.ix_(interior, interior)]
        A = np.eye(len(interior), dtype=float) - gamma * P_II
        P_Ig = P_goal[np.ix_(interior, [goal])][:, 0]
        P_IB = P_goal[np.ix_(interior, boundary_array)]
        h_I = solve_or_pinv(A, gamma * P_Ig)
        G_I = solve_or_pinv(A, gamma * P_IB)
        v_I = solve_or_pinv(A, np.full(len(interior), model.grid.step_reward, dtype=float))

        P_Bg = P_goal[np.ix_(boundary_array, [goal])][:, 0]
        P_BI = P_goal[np.ix_(boundary_array, interior)]
        P_BB = P_goal[np.ix_(boundary_array, boundary_array)]
        hit_rows = gamma * P_Bg + gamma * (P_BI @ h_I)
        gamma_rows = gamma * P_BB + gamma * (P_BI @ G_I)
        step_rewards = model.grid.step_reward + gamma * (P_BI @ v_I)
    solve_time = time.perf_counter() - solve_start

    local_nnz = int(np.count_nonzero(np.abs(hit_rows) > 1e-12))
    local_nnz += int(np.count_nonzero(np.abs(gamma_rows) > 1e-12))
    local_edges: List[EdgeKernel] = []
    for src_pos, src_state in enumerate(model.boundary):
        src_pos = boundary_pos[int(src_state)]
        local_edges.append(
            EdgeKernel(
                label=f"gc_{src_pos:03d}_to_goal",
                src_pos=src_pos,
                dst_pos=-1,
                src_state=int(src_state),
                dst_state=int(goal_state),
                gamma_row=gamma_rows[src_pos].copy(),
                occupancy_row=np.zeros(model.grid.n_states, dtype=float),
                policy_matrix=P_goal,
            )
        )
    local_rewards = step_rewards.copy()
    combined_rewards = np.concatenate([base_edge_rewards, np.array(local_rewards, dtype=float)])
    combined_gamma = np.vstack([base_gamma_rows, gamma_rows])
    combined_edges = list(model.edges) + local_edges
    return (
        combined_edges,
        combined_rewards,
        combined_gamma,
        base_event_time + policy_time + solve_time,
        int(base_event_nnz + local_nnz),
        len(local_edges),
        policy_time,
        solve_time,
    )


def run_promote_goal_baseline(
    map_label: str,
    rows: Tuple[str, ...],
    base_boundary: Sequence[int],
    goals: Sequence[int],
    gamma: float,
    slip: float,
) -> Tuple[float, float, int, int, float]:
    grid = GridWorld(rows)
    start_state = grid.symbol_states("S")[0]
    boundary = sorted(set(int(state) for state in base_boundary).union({int(start_state)}).union(int(g) for g in goals))
    t0 = time.perf_counter()
    reductions, valid_actions, _policies, _metadata, _edge_rows = build_first_boundary_reductions(
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
    kernel_time = time.perf_counter() - t0
    solve_time = 0.0
    max_start_gap = 0.0
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    for goal in goals:
        t1 = time.perf_counter()
        values, _policy = smdp_value_iteration(
            reductions=reductions,
            goal_boundary_position=boundary_to_pos[int(goal)],
            valid_actions=valid_actions,
        )
        solve_time += time.perf_counter() - t1
        full = full_terminal_value_iteration(grid, int(goal), gamma=gamma, slip=slip)
        max_start_gap = max(
            max_start_gap,
            abs(float(values[boundary_to_pos[int(start_state)]]) - float(full["V"][start_state])),
        )
    gamma_nnz = int(
        sum(
            np.count_nonzero(np.abs(reduction.gamma_terminal) > 1e-12)
            for reduction in reductions.values()
        )
    )
    return kernel_time, solve_time, len(boundary), gamma_nnz, max_start_gap


def prefix_counts(max_tasks: int, requested: Sequence[int]) -> List[int]:
    out = sorted(set(min(max_tasks, int(count)) for count in requested if int(count) > 0))
    return [count for count in out if count > 0]


def run_map_method(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    method_spec: str,
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    model = build_fixed_boundary_model(
        map_label=map_label,
        rows=rows,
        method_spec=method_spec,
        gamma=args.gamma,
        slip=args.slip,
        seed=args.seed,
        max_splits=args.max_splits,
    )
    grid = model.grid
    start_state = grid.symbol_states("S")[0]
    start_pos = model.boundary_to_pos[int(start_state)]
    query_states = choose_query_states(
        grid,
        model.boundary,
        max_tasks=args.max_tasks,
        seed=args.seed,
        prefer_interior=True,
    )
    additive_rows_by_kind: Dict[str, List[Dict[str, object]]] = {
        kind: [] for kind in args.additive_reward_kinds
    }
    terminal_full_rows: List[Dict[str, object]] = []
    terminal_goal_conditioned_rows: List[Dict[str, object]] = []

    occupancy_matrix = np.stack([edge.occupancy_row for edge in model.edges], axis=0)
    fixed_gamma_rows = np.stack([edge.gamma_row for edge in model.edges], axis=0)

    for task_idx, query_state in enumerate(query_states, start=1):
        if args.include_additive:
            for reward_kind in args.additive_reward_kinds:
                reward = additive_reward_for_query(grid, query_state, reward_kind, args.seed)
                full = full_additive_value_iteration(grid, reward, gamma=args.gamma, slip=args.slip)
                t_relabel = time.perf_counter()
                edge_rewards = occupancy_matrix @ reward
                relabel_time = time.perf_counter() - t_relabel
                smdp = edge_smdp_value_iteration(
                    n_boundary=len(model.boundary),
                    edges=model.edges,
                    edge_rewards=edge_rewards,
                    gamma_rows=fixed_gamma_rows,
                )
                additive_rows_by_kind[reward_kind].append(
                    {
                        "task_idx": task_idx,
                        "query_state": int(query_state),
                        "reward_kind": reward_kind,
                        "full_time_sec": float(full["time_sec"]),
                        "full_backup_count": int(full["backup_count"]),
                        "relabel_time_sec": relabel_time,
                        "smdp_solve_time_sec": float(smdp["time_sec"]),
                        "smdp_edge_backup_count": int(smdp["edge_backup_count"]),
                        "start_gap": abs(float(smdp["V"][start_pos]) - float(full["V"][start_state])),
                        "boundary_gap": boundary_value_gap(smdp["V"], full["V"], model.boundary),
                    }
                )

        if args.include_terminal:
            full = full_terminal_value_iteration(grid, int(query_state), gamma=args.gamma, slip=args.slip)
            edge_rewards, gamma_rows, event_time, event_nnz = event_kernel_for_goal(
                model,
                goal_state=int(query_state),
                gamma=args.gamma,
            )
            smdp = edge_smdp_value_iteration(
                n_boundary=len(model.boundary),
                edges=model.edges,
                edge_rewards=edge_rewards,
                gamma_rows=gamma_rows,
            )
            terminal_full_rows.append(
                {
                    "task_idx": task_idx,
                    "query_state": int(query_state),
                    "full_time_sec": float(full["time_sec"]),
                    "full_backup_count": int(full["backup_count"]),
                    "event_kernel_time_sec": event_time,
                    "event_kernel_nnz": int(event_nnz),
                    "smdp_solve_time_sec": float(smdp["time_sec"]),
                    "smdp_edge_backup_count": int(smdp["edge_backup_count"]),
                    "start_gap": abs(float(smdp["V"][start_pos]) - float(full["V"][start_state])),
                    "boundary_gap": boundary_value_gap(smdp["V"], full["V"], model.boundary),
                    "goal_option_interface_size": 0,
                    "goal_conditioned_options": 0,
                }
            )
            if args.include_goal_conditioned_terminal:
                (
                    gc_edges,
                    gc_edge_rewards,
                    gc_gamma_rows,
                    gc_event_time,
                    gc_event_nnz,
                    gc_option_count,
                    gc_policy_build_time,
                    gc_batched_solve_time,
                ) = goal_conditioned_event_kernel_for_goal(
                    model,
                    goal_state=int(query_state),
                    gamma=args.gamma,
                    slip=args.slip,
                    base_edge_rewards=edge_rewards,
                    base_gamma_rows=gamma_rows,
                    base_event_time=event_time,
                    base_event_nnz=event_nnz,
                )
                gc_smdp = edge_smdp_value_iteration(
                    n_boundary=len(model.boundary),
                    edges=gc_edges,
                    edge_rewards=gc_edge_rewards,
                    gamma_rows=gc_gamma_rows,
                )
                terminal_goal_conditioned_rows.append(
                    {
                        "task_idx": task_idx,
                        "query_state": int(query_state),
                        "full_time_sec": float(full["time_sec"]),
                        "full_backup_count": int(full["backup_count"]),
                        "event_kernel_time_sec": gc_event_time,
                        "event_kernel_nnz": int(gc_event_nnz),
                        "goal_policy_build_time_sec": gc_policy_build_time,
                        "batched_event_solve_time_sec": gc_batched_solve_time,
                        "smdp_solve_time_sec": float(gc_smdp["time_sec"]),
                        "smdp_edge_backup_count": int(gc_smdp["edge_backup_count"]),
                        "start_gap": abs(float(gc_smdp["V"][start_pos]) - float(full["V"][start_state])),
                        "boundary_gap": boundary_value_gap(gc_smdp["V"], full["V"], model.boundary),
                        "goal_option_interface_size": gc_option_count,
                        "goal_conditioned_options": gc_option_count,
                    }
                )

    rows_out: List[Dict[str, object]] = []
    fixed_upfront = model.construction_time_sec + model.kernel_time_sec
    for count in prefix_counts(len(query_states), args.task_counts):
        if args.include_additive:
            for reward_kind, additive_full_rows in additive_rows_by_kind.items():
                if not additive_full_rows:
                    continue
                prefix = additive_full_rows[:count]
                full_time = sum(float(row["full_time_sec"]) for row in prefix)
                relabel_time = sum(float(row["relabel_time_sec"]) for row in prefix)
                solve_time = sum(float(row["smdp_solve_time_sec"]) for row in prefix)
                graph_total = fixed_upfront + relabel_time + solve_time
                gaps = [float(row["start_gap"]) for row in prefix]
                break_even = break_even_num_tasks(
                    fixed_upfront,
                    full_time,
                    relabel_time + solve_time,
                    count,
                )
                rows_out.append(
                    {
                        "map_family": family,
                        "map_size": size,
                        "map": map_label,
                        "method_spec": method_spec,
                        "variant": "fixed_B_edge_reward_kernel",
                        "task_type": f"additive_{reward_kind}",
                        "task_count": count,
                        "n_states": grid.n_states,
                        "n_boundary": len(model.boundary),
                        "state_compression_ratio": grid.n_states / max(1.0, float(len(model.boundary))),
                        "edge_count": len(model.edges),
                        "reward_kernel_nnz": model.occupancy_nnz,
                        "continuation_kernel_nnz": model.gamma_nnz,
                        "certified_kernel_error_bound": 0.0,
                        "goal_option_interface_size": 0,
                        "goal_conditioned_options": 0,
                        "n_goal_policies": 0,
                        "construction_time_sec": model.construction_time_sec,
                        "kernel_time_sec": model.kernel_time_sec,
                        "task_kernel_time_sec": relabel_time,
                        "policy_build_time_sec": 0.0,
                        "batched_event_solve_time_sec": 0.0,
                        "smdp_solve_time_sec": solve_time,
                        "full_total_time_sec": full_time,
                        "graph_total_time_sec": graph_total,
                        "break_even_num_tasks": break_even,
                        "amortized_speedup_vs_full_vi": full_time / max(1e-12, graph_total),
                        "planning_only_speedup_vs_full_vi": full_time / max(1e-12, solve_time + relabel_time),
                        "start_gap_mean": float(np.mean(gaps)),
                        "start_gap_max": float(np.max(gaps)),
                        "boundary_gap_max": float(np.max([float(row["boundary_gap"]) for row in prefix])),
                        "full_backup_count": sum(int(row["full_backup_count"]) for row in prefix),
                        "smdp_edge_backup_count": sum(int(row["smdp_edge_backup_count"]) for row in prefix),
                    }
                )
        if args.include_terminal and terminal_full_rows:
            prefix = terminal_full_rows[:count]
            full_time = sum(float(row["full_time_sec"]) for row in prefix)
            event_time = sum(float(row["event_kernel_time_sec"]) for row in prefix)
            solve_time = sum(float(row["smdp_solve_time_sec"]) for row in prefix)
            graph_total = fixed_upfront + event_time + solve_time
            gaps = [float(row["start_gap"]) for row in prefix]
            break_even = break_even_num_tasks(
                fixed_upfront,
                full_time,
                event_time + solve_time,
                count,
            )
            rows_out.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_label,
                    "method_spec": method_spec,
                    "variant": "fixed_B_event_hit_kernel",
                    "task_type": "terminal_goal",
                    "task_count": count,
                    "n_states": grid.n_states,
                    "n_boundary": len(model.boundary),
                    "state_compression_ratio": grid.n_states / max(1.0, float(len(model.boundary))),
                    "edge_count": len(model.edges),
                    "reward_kernel_nnz": sum(int(row["event_kernel_nnz"]) for row in prefix),
                    "continuation_kernel_nnz": model.gamma_nnz,
                    "certified_kernel_error_bound": 0.0,
                    "goal_option_interface_size": 0,
                    "goal_conditioned_options": 0,
                    "n_goal_policies": 0,
                    "construction_time_sec": model.construction_time_sec,
                    "kernel_time_sec": model.kernel_time_sec,
                    "task_kernel_time_sec": event_time,
                    "policy_build_time_sec": 0.0,
                    "batched_event_solve_time_sec": 0.0,
                    "smdp_solve_time_sec": solve_time,
                    "full_total_time_sec": full_time,
                    "graph_total_time_sec": graph_total,
                    "break_even_num_tasks": break_even,
                    "amortized_speedup_vs_full_vi": full_time / max(1e-12, graph_total),
                    "planning_only_speedup_vs_full_vi": full_time / max(1e-12, event_time + solve_time),
                    "start_gap_mean": float(np.mean(gaps)),
                    "start_gap_max": float(np.max(gaps)),
                    "boundary_gap_max": float(np.max([float(row["boundary_gap"]) for row in prefix])),
                    "full_backup_count": sum(int(row["full_backup_count"]) for row in prefix),
                    "smdp_edge_backup_count": sum(int(row["smdp_edge_backup_count"]) for row in prefix),
                }
            )
            if args.include_goal_conditioned_terminal and terminal_goal_conditioned_rows:
                gc_prefix = terminal_goal_conditioned_rows[:count]
                gc_full_time = sum(float(row["full_time_sec"]) for row in gc_prefix)
                gc_event_time = sum(float(row["event_kernel_time_sec"]) for row in gc_prefix)
                gc_policy_time = sum(float(row["goal_policy_build_time_sec"]) for row in gc_prefix)
                gc_batched_time = sum(float(row["batched_event_solve_time_sec"]) for row in gc_prefix)
                gc_solve_time = sum(float(row["smdp_solve_time_sec"]) for row in gc_prefix)
                gc_total = fixed_upfront + gc_event_time + gc_solve_time
                gc_gaps = [float(row["start_gap"]) for row in gc_prefix]
                gc_interface = sum(int(row["goal_option_interface_size"]) for row in gc_prefix)
                gc_break_even = break_even_num_tasks(
                    fixed_upfront + gc_event_time,
                    gc_full_time,
                    gc_solve_time,
                    count,
                )
                rows_out.append(
                    {
                        "map_family": family,
                        "map_size": size,
                        "map": map_label,
                        "method_spec": method_spec,
                        "variant": "fixed_B_goal_conditioned_event_options",
                        "task_type": "terminal_goal",
                        "task_count": count,
                        "n_states": grid.n_states,
                        "n_boundary": len(model.boundary),
                        "state_compression_ratio": grid.n_states / max(1.0, float(len(model.boundary))),
                        "edge_count": len(model.edges) + len(model.boundary),
                        "reward_kernel_nnz": sum(int(row["event_kernel_nnz"]) for row in gc_prefix),
                        "continuation_kernel_nnz": model.gamma_nnz,
                        "certified_kernel_error_bound": 0.0,
                        "goal_option_interface_size": gc_interface,
                        "goal_conditioned_options": gc_interface,
                        "n_goal_policies": count,
                        "construction_time_sec": model.construction_time_sec,
                        "kernel_time_sec": model.kernel_time_sec,
                        "task_kernel_time_sec": gc_event_time,
                        "policy_build_time_sec": gc_policy_time,
                        "batched_event_solve_time_sec": gc_batched_time,
                        "smdp_solve_time_sec": gc_solve_time,
                        "full_total_time_sec": gc_full_time,
                        "graph_total_time_sec": gc_total,
                        "break_even_num_tasks": gc_break_even,
                        "amortized_speedup_vs_full_vi": gc_full_time / max(1e-12, gc_total),
                        "planning_only_speedup_vs_full_vi": gc_full_time / max(1e-12, gc_event_time + gc_solve_time),
                        "start_gap_mean": float(np.mean(gc_gaps)),
                        "start_gap_max": float(np.max(gc_gaps)),
                        "boundary_gap_max": float(np.max([float(row["boundary_gap"]) for row in gc_prefix])),
                        "epsilon_opt_empirical": float(np.max(gc_gaps)),
                        "full_backup_count": sum(int(row["full_backup_count"]) for row in gc_prefix),
                        "smdp_edge_backup_count": sum(int(row["smdp_edge_backup_count"]) for row in gc_prefix),
                    }
                )
            if args.include_promote_baseline:
                t_promote = time.perf_counter()
                promote_kernel, promote_solve, promote_n_boundary, promote_nnz, promote_gap = (
                    run_promote_goal_baseline(
                        map_label=map_label,
                        rows=rows,
                        base_boundary=model.boundary,
                        goals=query_states[:count],
                        gamma=args.gamma,
                        slip=args.slip,
                    )
                )
                promote_construction = time.perf_counter() - t_promote - promote_kernel - promote_solve
                promote_total = promote_kernel + promote_solve
                promote_break_even = break_even_num_tasks(
                    max(0.0, promote_construction) + promote_kernel,
                    full_time,
                    promote_solve,
                    count,
                )
                rows_out.append(
                    {
                        "map_family": family,
                        "map_size": size,
                        "map": map_label,
                        "method_spec": method_spec,
                        "variant": "promote_goals_to_B",
                        "task_type": "terminal_goal",
                        "task_count": count,
                        "n_states": grid.n_states,
                        "n_boundary": promote_n_boundary,
                        "state_compression_ratio": grid.n_states / max(1.0, float(promote_n_boundary)),
                        "edge_count": promote_n_boundary * max(0, promote_n_boundary - 1),
                        "reward_kernel_nnz": 0,
                        "continuation_kernel_nnz": promote_nnz,
                        "certified_kernel_error_bound": 0.0,
                        "goal_option_interface_size": count,
                        "goal_conditioned_options": count,
                        "n_goal_policies": 0,
                        "construction_time_sec": max(0.0, promote_construction),
                        "kernel_time_sec": promote_kernel,
                        "task_kernel_time_sec": 0.0,
                        "policy_build_time_sec": 0.0,
                        "batched_event_solve_time_sec": 0.0,
                        "smdp_solve_time_sec": promote_solve,
                        "full_total_time_sec": full_time,
                        "graph_total_time_sec": promote_total,
                        "break_even_num_tasks": promote_break_even,
                        "amortized_speedup_vs_full_vi": full_time / max(1e-12, promote_total),
                        "planning_only_speedup_vs_full_vi": full_time / max(1e-12, promote_solve),
                        "start_gap_mean": np.nan,
                        "start_gap_max": promote_gap,
                        "boundary_gap_max": np.nan,
                        "full_backup_count": sum(int(row["full_backup_count"]) for row in prefix),
                        "smdp_edge_backup_count": np.nan,
                    }
                )
    value_scale = 1.0 / max(1e-12, 1.0 - args.gamma)
    for row in rows_out:
        row["value_scale"] = value_scale
        row["gap_normalization"] = "discounted_unit_reward_bound"
        for field in ("start_gap_mean", "start_gap_max", "boundary_gap_max"):
            value = float(row.get(field, np.nan))
            row[f"normalized_{field}"] = value / value_scale if math.isfinite(value) else np.nan
    return rows_out


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    summary_rows: List[Dict[str, object]] = []
    grouped: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("variant")), str(row.get("task_type"))), []).append(row)
    for (variant, task_type), group in sorted(grouped.items()):
        speedups = [float(row["amortized_speedup_vs_full_vi"]) for row in group]
        planning = [float(row["planning_only_speedup_vs_full_vi"]) for row in group]
        gaps = [float(row["start_gap_max"]) for row in group if str(row.get("start_gap_max")) != "nan"]
        boundary_gaps = [float(row["boundary_gap_max"]) for row in group if str(row.get("boundary_gap_max")) != "nan"]
        interfaces = [float(row.get("goal_option_interface_size", 0.0)) for row in group]
        policies = [float(row.get("n_goal_policies", 0.0)) for row in group]
        break_even = [float(row.get("break_even_num_tasks", np.nan)) for row in group]
        finite_break_even = [value for value in break_even if math.isfinite(value)]
        summary_rows.append(
            {
                "variant": variant,
                "task_type": task_type,
                "n_rows": len(group),
                "median_n_boundary": float(np.median([float(row["n_boundary"]) for row in group])),
                "median_total_speedup": float(np.median(speedups)),
                "best_total_speedup": float(np.max(speedups)),
                "median_planning_speedup": float(np.median(planning)),
                "max_start_gap": float(np.max(gaps)) if gaps else np.nan,
                "max_boundary_gap": float(np.max(boundary_gaps)) if boundary_gaps else np.nan,
                "median_goal_interface": float(np.median(interfaces)),
                "median_goal_policies": float(np.median(policies)),
                "median_break_even_tasks": float(np.median(finite_break_even)) if finite_break_even else np.inf,
            }
        )

    columns = [
        "map",
        "method_spec",
        "variant",
        "task_type",
        "task_count",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "full_total_time_sec",
        "graph_total_time_sec",
        "amortized_speedup_vs_full_vi",
        "planning_only_speedup_vs_full_vi",
        "break_even_num_tasks",
        "goal_option_interface_size",
        "n_goal_policies",
        "policy_build_time_sec",
        "batched_event_solve_time_sec",
        "start_gap_max",
        "boundary_gap_max",
    ]
    lines = [
        "# Edge Reward Kernel Multi-Task",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"methods = {list(args.methods)}",
        f"task_counts = {list(args.task_counts)}, max_tasks = {args.max_tasks}",
        f"additive_reward_kinds = {list(args.additive_reward_kinds)}",
        f"shard = {args.shard_index}/{args.num_shards}",
        "",
        "This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.",
        "Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.",
        "The goal-conditioned variant appends query-time local options to the event model while keeping `B` fixed, and counts their interface size separately.",
        "Its shared/batched backend builds one goal-conditioned policy per queried goal and solves all boundary-start event rows together.",
        "",
        "## Summary",
        "",
        markdown_table(
            summary_rows,
            [
                "variant",
                "task_type",
                "n_rows",
                "median_n_boundary",
                "median_total_speedup",
                "best_total_speedup",
                "median_planning_speedup",
                "max_start_gap",
                "max_boundary_gap",
                "median_goal_interface",
                "median_goal_policies",
                "median_break_even_tasks",
            ],
        ),
        "",
        "## Rows",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fixed-B edge reward/event kernel multi-task benchmark.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:64", "open_room:10", "maze:13"])
    parser.add_argument("--methods", nargs="+", default=["endpoints", "turn_articulation"])
    parser.add_argument("--task-counts", type=int, nargs="+", default=[1, 5, 10, 25])
    parser.add_argument("--max-tasks", type=int, default=25)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument(
        "--additive-reward-kinds",
        nargs="+",
        choices=["sparse", "dense"],
        default=["sparse", "dense"],
        help="Additive reward families to evaluate without changing the boundary graph.",
    )
    parser.add_argument(
        "--additive-reward-kind",
        choices=["sparse", "dense"],
        default=None,
        help="Deprecated single-kind alias kept for old scripts.",
    )
    parser.add_argument("--include-additive", action="store_true", default=True)
    parser.add_argument("--no-additive", dest="include_additive", action="store_false")
    parser.add_argument("--include-terminal", action="store_true", default=True)
    parser.add_argument("--no-terminal", dest="include_terminal", action="store_false")
    parser.add_argument("--include-goal-conditioned-terminal", action="store_true", default=True)
    parser.add_argument(
        "--no-goal-conditioned-terminal",
        dest="include_goal_conditioned_terminal",
        action="store_false",
    )
    parser.add_argument("--include-promote-baseline", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/edge_reward_kernel_multitask"))
    args = parser.parse_args()
    if args.additive_reward_kind is not None:
        args.additive_reward_kinds = [args.additive_reward_kind]

    rows: List[Dict[str, object]] = []
    jobs = [
        (family, size, map_label, map_rows, method)
        for family, size, map_label, map_rows in parse_map_specs(args.map_specs)
        for method in args.methods
    ]
    if args.num_shards > 1:
        if args.shard_index < 0 or args.shard_index >= args.num_shards:
            raise ValueError("--shard-index must be in [0, --num-shards).")
        jobs = [job for idx, job in enumerate(jobs) if idx % args.num_shards == args.shard_index]

    for family, size, map_label, map_rows, method in jobs:
        try:
            rows.extend(run_map_method(family, size, map_label, map_rows, method, args))
        except Exception as exc:
            if not args.continue_on_error:
                raise
            rows.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_label,
                    "method_spec": method,
                    "variant": "error",
                    "task_type": "error",
                    "error": repr(exc),
                }
            )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "edge_reward_kernel_multitask.csv", rows)
    (args.out_dir / "edge_reward_kernel_multitask.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)
    print(f"Wrote {len(rows)} rows to {args.out_dir}")


if __name__ == "__main__":
    main()
