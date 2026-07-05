from __future__ import annotations

import math
import time
from collections import deque
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import (
    ACTIONS,
    DELTAS,
    BellmanKronReduction,
    GridWorld,
    action_distribution,
    graph_adjacency,
)
from run_first_boundary_targeted import (
    build_first_boundary_reductions,
    candidate_boundary_states,
    critical_saliency,
    policy_boundary_occupancy,
    tail_cvar,
)
from run_option_algorithm_comparison import construct_boundary


def corridor_rows(length: int) -> Tuple[str, ...]:
    length = max(2, int(length))
    return (
        "#" * (length + 2),
        "#S" + "." * (length - 2) + "G#",
        "#" * (length + 2),
    )


def open_room_rows(side: int) -> Tuple[str, ...]:
    side = max(2, int(side))
    rows = []
    for r in range(side):
        chars = []
        for c in range(side):
            if r == 0 and c == 0:
                chars.append("S")
            elif r == side - 1 and c == side - 1:
                chars.append("G")
            else:
                chars.append(".")
        rows.append("#" + "".join(chars) + "#")
    wall = "#" * (side + 2)
    return tuple([wall] + rows + [wall])


def four_rooms_rows(side: int) -> Tuple[str, ...]:
    side = max(5, int(side))
    if side % 2 == 0:
        side += 1
    mid = side // 2
    door_a = max(1, side // 4)
    door_b = min(side - 2, side - 1 - side // 4)
    interior = [["." for _ in range(side)] for _ in range(side)]
    for r in range(side):
        if r not in {door_a, door_b}:
            interior[r][mid] = "#"
    for c in range(side):
        if c not in {door_a, door_b}:
            interior[mid][c] = "#"
    interior[0][0] = "S"
    interior[side - 1][side - 1] = "G"
    wall = "#" * (side + 2)
    return tuple([wall] + ["#" + "".join(row) + "#" for row in interior] + [wall])


def dfs_maze_rows(side: int, seed: int = 0) -> Tuple[str, ...]:
    side = max(5, int(side))
    if side % 2 == 0:
        side += 1
    rng = np.random.default_rng(seed + side * 997)
    maze = [["#" for _ in range(side)] for _ in range(side)]
    start = (1, 1)
    maze[start[0]][start[1]] = "."
    stack = [start]
    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            nr, nc = r + dr, c + dc
            if 1 <= nr < side - 1 and 1 <= nc < side - 1 and maze[nr][nc] == "#":
                neighbors.append((nr, nc, dr, dc))
        if not neighbors:
            stack.pop()
            continue
        nr, nc, dr, dc = neighbors[int(rng.integers(len(neighbors)))]
        maze[r + dr // 2][c + dc // 2] = "."
        maze[nr][nc] = "."
        stack.append((nr, nc))

    open_cells = [(r, c) for r in range(side) for c in range(side) if maze[r][c] == "."]
    goal = max(open_cells, key=lambda cell: cell[0] + cell[1])
    maze[start[0]][start[1]] = "S"
    maze[goal[0]][goal[1]] = "G"
    return tuple("".join(row) for row in maze)


def scaled_rows(family: str, size: int, seed: int = 0) -> Tuple[str, ...]:
    if family == "corridor":
        return corridor_rows(size)
    if family == "open_room":
        return open_room_rows(size)
    if family == "four_rooms":
        return four_rooms_rows(size)
    if family == "maze":
        return dfs_maze_rows(size, seed=seed)
    raise ValueError(f"Unknown scaled-map family: {family}")


def parse_map_specs(specs: Sequence[str]) -> List[Tuple[str, int, str, Tuple[str, ...]]]:
    out: List[Tuple[str, int, str, Tuple[str, ...]]] = []
    for spec in specs:
        family, raw_sizes = spec.split(":", 1)
        for raw_size in raw_sizes.split(","):
            size = int(raw_size)
            label = f"{family}_{size}"
            out.append((family, size, label, scaled_rows(family, size)))
    return out


def resolve_method_spec(method_spec: str, grid: GridWorld) -> str:
    if method_spec.endswith("_sqrt"):
        family = method_spec[: -len("_sqrt")]
        k = max(4, int(math.ceil(math.sqrt(grid.n_states))))
        return f"{family}_{min(k, grid.n_states)}"
    if method_spec.endswith("_quarter"):
        family = method_spec[: -len("_quarter")]
        k = max(4, int(math.ceil(0.25 * grid.n_states)))
        return f"{family}_{min(k, grid.n_states)}"
    return method_spec


def transition_nnz_proxy(grid: GridWorld, slip: float) -> int:
    nnz = 0
    for state in range(grid.n_states):
        for action in ACTIONS:
            if slip <= 0.0:
                nnz += 1
            else:
                next_states = {grid.next_state(state, slip_action) for slip_action in ACTIONS}
                nnz += len(next_states)
    return nnz


def full_value_iteration_measured(
    grid: GridWorld,
    goal_state: int,
    gamma: float,
    slip: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
    record_points: Iterable[int] = (),
) -> Dict[str, object]:
    start_time = time.perf_counter()
    V = np.zeros(grid.n_states, dtype=float)
    trace: List[Dict[str, object]] = []
    record_set = set(int(point) for point in record_points)
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        for state in range(grid.n_states):
            if state == goal_state:
                V[state] = 0.0
                continue
            q_values = []
            for action in ACTIONS:
                dist = action_distribution(action, slip=slip)
                q = grid.step_reward + gamma * sum(
                    prob * old[grid.next_state(state, slip_action)]
                    for slip_action, prob in dist.items()
                )
                q_values.append(q)
            V[state] = max(q_values)
        delta = float(np.max(np.abs(V - old)))
        if iteration in record_set:
            trace.append(
                {
                    "iteration": iteration,
                    "backup_count": iteration * grid.n_states * len(ACTIONS),
                    "delta": delta,
                    "time_sec": time.perf_counter() - start_time,
                    "value": V.copy(),
                }
            )
        if delta < tol:
            elapsed = time.perf_counter() - start_time
            return {
                "V": V,
                "iterations": iteration,
                "time_sec": elapsed,
                "backup_count": iteration * grid.n_states * len(ACTIONS),
                "trace": trace,
            }
    elapsed = time.perf_counter() - start_time
    return {
        "V": V,
        "iterations": max_iterations,
        "time_sec": elapsed,
        "backup_count": max_iterations * grid.n_states * len(ACTIONS),
        "trace": trace,
    }


def full_policy_iteration_measured(
    grid: GridWorld,
    goal_state: int,
    gamma: float,
    slip: float,
    max_iterations: int = 200,
) -> Dict[str, object]:
    start_time = time.perf_counter()
    policy = np.array(["N" for _ in range(grid.n_states)], dtype=object)
    for state in range(grid.n_states):
        legal = grid.legal_actions(state)
        policy[state] = legal[0] if legal else "N"

    V = np.zeros(grid.n_states, dtype=float)
    for iteration in range(1, max_iterations + 1):
        P = np.zeros((grid.n_states, grid.n_states), dtype=float)
        r = np.full(grid.n_states, grid.step_reward, dtype=float)
        for state in range(grid.n_states):
            if state == goal_state:
                P[state, state] = 1.0
                r[state] = 0.0
                continue
            for action, prob in action_distribution(str(policy[state]), slip=slip).items():
                P[state, grid.next_state(state, action)] += prob
        A = np.eye(grid.n_states, dtype=float) - gamma * P
        A[goal_state, :] = 0.0
        A[goal_state, goal_state] = 1.0
        r[goal_state] = 0.0
        V = np.linalg.solve(A, r)

        stable = True
        for state in range(grid.n_states):
            if state == goal_state:
                continue
            best_action = str(policy[state])
            best_q = -float("inf")
            for action in ACTIONS:
                dist = action_distribution(action, slip=slip)
                q = grid.step_reward + gamma * sum(
                    prob * V[grid.next_state(state, slip_action)]
                    for slip_action, prob in dist.items()
                )
                if q > best_q + 1e-12:
                    best_q = q
                    best_action = action
            if best_action != policy[state]:
                stable = False
                policy[state] = best_action
        if stable:
            elapsed = time.perf_counter() - start_time
            return {
                "V": V,
                "iterations": iteration,
                "time_sec": elapsed,
                "improvement_backup_count": iteration * grid.n_states * len(ACTIONS),
            }
    elapsed = time.perf_counter() - start_time
    return {
        "V": V,
        "iterations": max_iterations,
        "time_sec": elapsed,
        "improvement_backup_count": max_iterations * grid.n_states * len(ACTIONS),
    }


def valid_edge_count(valid_actions: Mapping[str, np.ndarray]) -> int:
    return int(sum(int(np.asarray(valid, dtype=bool).sum()) for valid in valid_actions.values()))


def kernel_nnz(reductions: Mapping[str, BellmanKronReduction], valid_actions: Mapping[str, np.ndarray]) -> int:
    total = 0
    for label, reduction in reductions.items():
        valid = np.asarray(valid_actions.get(label, np.zeros(len(reduction.boundary))), dtype=bool)
        for src_pos in np.flatnonzero(valid):
            total += int(np.count_nonzero(np.abs(reduction.gamma_terminal[int(src_pos)]) > 1e-12))
    return total


def smdp_value_iteration_measured(
    reductions: Mapping[str, BellmanKronReduction],
    valid_actions: Mapping[str, np.ndarray],
    goal_pos: int,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
    record_points: Iterable[int] = (),
) -> Dict[str, object]:
    first = next(iter(reductions.values()))
    n_boundary = len(first.boundary)
    edge_count = valid_edge_count(valid_actions)
    V = np.zeros(n_boundary, dtype=float)
    policy: Dict[int, str] = {}
    trace: List[Dict[str, object]] = []
    record_set = set(int(point) for point in record_points)
    start_time = time.perf_counter()
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        new = np.full(n_boundary, -np.inf, dtype=float)
        best_policy: Dict[int, str] = {}
        for label, reduction in reductions.items():
            valid = np.asarray(valid_actions.get(label, np.zeros(n_boundary)), dtype=bool)
            if not np.any(valid):
                continue
            valid_positions = np.flatnonzero(valid)
            q = reduction.reward[valid_positions] + reduction.gamma_terminal[valid_positions, :] @ old
            for pos, q_value in zip(valid_positions, q):
                pos_int = int(pos)
                if q_value > new[pos_int]:
                    new[pos_int] = float(q_value)
                    best_policy[pos_int] = label
        new[goal_pos] = 0.0
        best_policy[goal_pos] = "TERMINAL"
        if np.any(~np.isfinite(np.delete(new, goal_pos))):
            bad = np.flatnonzero(~np.isfinite(new)).tolist()
            raise ValueError(f"No valid SMDP option available at boundary positions {bad}.")
        V = new
        policy = best_policy
        delta = float(np.max(np.abs(V - old)))
        if iteration in record_set:
            trace.append(
                {
                    "iteration": iteration,
                    "backup_count": iteration * edge_count,
                    "delta": delta,
                    "time_sec": time.perf_counter() - start_time,
                    "value": V.copy(),
                    "policy": dict(policy),
                }
            )
        if delta < tol:
            elapsed = time.perf_counter() - start_time
            return {
                "V": V,
                "policy": policy,
                "iterations": iteration,
                "time_sec": elapsed,
                "edge_backup_count": iteration * edge_count,
                "trace": trace,
            }
    elapsed = time.perf_counter() - start_time
    return {
        "V": V,
        "policy": policy,
        "iterations": max_iterations,
        "time_sec": elapsed,
        "edge_backup_count": max_iterations * edge_count,
        "trace": trace,
    }


def build_compressed_model_measured(
    map_label: str,
    rows: Tuple[str, ...],
    method_spec: str,
    gamma: float,
    slip: float,
    seed: int = 0,
    max_splits: int = 18,
    audit_lens: str = "turn_articulation",
    audit_top_fraction: float = 0.15,
    soft_kind: str = "combined",
    soft_top_fraction: float = 0.15,
    local_horizon: float = 999.0,
    hidden_threshold: float = 1e-6,
    soft_threshold: float = 3.0,
    residual_threshold: float = 0.5,
    residual_threshold_mode: str = "struct_distinct",
    residual_reward_weight: float = 0.05,
    residual_hit_weight: float = 0.0,
    compute_struct_distinct: bool = True,
    full_record_points: Iterable[int] = (),
    smdp_record_points: Iterable[int] = (),
) -> Dict[str, object]:
    grid = GridWorld(rows)
    start_state = grid.symbol_states("S")[0]
    goal_state = grid.symbol_states("G")[0]
    actual_method = resolve_method_spec(method_spec, grid)

    t0 = time.perf_counter()
    boundary, constructor = construct_boundary(
        method=actual_method,
        map_name=map_label,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=gamma,
        max_splits=max_splits,
        seed=seed,
    )
    construction_time = time.perf_counter() - t0
    boundary = sorted(set(boundary))
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    if start_state not in boundary_to_pos or goal_state not in boundary_to_pos:
        raise ValueError(f"Boundary for {actual_method} must contain S and G.")

    residual_boundary = candidate_boundary_states(
        grid=grid,
        kind=audit_lens,
        goal_state=goal_state,
        gamma=gamma,
        slip=slip,
        top_fraction=audit_top_fraction,
    )
    soft_state_cost = critical_saliency(
        grid=grid,
        kind=soft_kind,
        goal_state=goal_state,
        gamma=gamma,
        slip=slip,
        top_fraction=soft_top_fraction,
    )
    full_result = full_value_iteration_measured(
        grid,
        goal_state,
        gamma=gamma,
        slip=slip,
        record_points=full_record_points,
    )
    V_full = full_result["V"]
    boundary_values = V_full[np.array(boundary, dtype=int)]
    value_scale_task = max(
        1.0,
        abs(float(V_full[start_state])),
        float(np.percentile(np.abs(boundary_values), 95)) if len(boundary_values) > 0 else 1.0,
    )

    t1 = time.perf_counter()
    reductions, valid_actions, _policies, metadata, edge_rows = build_first_boundary_reductions(
        grid=grid,
        boundary=boundary,
        candidate_boundary=boundary,
        residual_boundary=residual_boundary,
        soft_state_cost=soft_state_cost,
        value_scale_task=value_scale_task,
        slip=slip,
        gamma=gamma,
        local_horizon=local_horizon,
        hidden_threshold=hidden_threshold,
        soft_threshold=soft_threshold,
        residual_threshold=residual_threshold,
        residual_reward_weight=residual_reward_weight,
        residual_hit_weight=residual_hit_weight,
        residual_threshold_mode=residual_threshold_mode,
        compute_struct_distinct=compute_struct_distinct,
        proposal_boundary=residual_boundary,
    )
    kernel_time = time.perf_counter() - t1

    smdp_result = smdp_value_iteration_measured(
        reductions=reductions,
        valid_actions=valid_actions,
        goal_pos=boundary_to_pos[goal_state],
        record_points=smdp_record_points,
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
        src_state = int(edge_row["src_state"])
        src_pos = boundary_to_pos.get(src_state)
        if src_pos is None:
            continue
        if str(edge_row["option"]) != str(policy.get(src_pos)) or not bool(edge_row["edge_valid"]):
            continue
        occ = float(occupancy[src_pos])
        occupancy_struct_hidden_distinct += occ * float(edge_row["struct_hidden_distinct"])
        occupancy_model_residual += occ * float(edge_row["model_residual"])

    V_smdp = smdp_result["V"]
    boundary_full = V_full[np.array(boundary, dtype=int)]
    nonterminal = np.ones(len(boundary), dtype=bool)
    nonterminal[boundary_to_pos[goal_state]] = False
    start_gap = float(abs(V_smdp[boundary_to_pos[start_state]] - V_full[start_state]))
    value_gap_max = float(np.max(np.abs(V_smdp[nonterminal] - boundary_full[nonterminal]))) if np.any(nonterminal) else 0.0
    valid_struct_distinct = [
        float(row["struct_hidden_distinct"])
        for row in edge_rows
        if bool(row["edge_valid"])
    ]

    return {
        "grid": grid,
        "rows": rows,
        "method": actual_method,
        "method_spec": method_spec,
        "constructor": constructor,
        "boundary": boundary,
        "boundary_to_pos": boundary_to_pos,
        "residual_boundary": residual_boundary,
        "reductions": reductions,
        "valid_actions": valid_actions,
        "metadata": metadata,
        "full_result": full_result,
        "smdp_result": smdp_result,
        "construction_time_sec": construction_time,
        "kernel_time_sec": kernel_time,
        "start_state": start_state,
        "goal_state": goal_state,
        "n_states": grid.n_states,
        "n_boundary": len(boundary),
        "n_edges_valid": valid_edge_count(valid_actions),
        "transition_nnz_proxy": transition_nnz_proxy(grid, slip),
        "kernel_nnz": kernel_nnz(reductions, valid_actions),
        "start_gap": start_gap,
        "value_gap_max": value_gap_max,
        "occupancy_struct_hidden_distinct": float(occupancy_struct_hidden_distinct),
        "occupancy_model_residual": float(occupancy_model_residual),
        "struct_hidden_distinct_cvar95": tail_cvar(valid_struct_distinct),
    }
