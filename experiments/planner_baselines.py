from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np
from scipy import sparse

from bellman_kron import ACTIONS, GridWorld, action_distribution


@dataclass(frozen=True)
class SparseGridModel:
    transitions: Tuple[sparse.csr_matrix, ...]
    rewards: np.ndarray
    successors: Tuple[Tuple[Tuple[Tuple[int, float], ...], ...], ...]
    predecessors: Tuple[Tuple[int, ...], ...]
    goal_state: int

    @property
    def n_states(self) -> int:
        return int(self.rewards.shape[1])

    @property
    def n_actions(self) -> int:
        return int(self.rewards.shape[0])


def build_sparse_grid_model(grid: GridWorld, goal_state: int, slip: float) -> SparseGridModel:
    n_states = grid.n_states
    transitions: List[sparse.csr_matrix] = []
    successors_by_action: List[Tuple[Tuple[Tuple[int, float], ...], ...]] = []
    rewards = np.full((len(ACTIONS), n_states), grid.step_reward, dtype=float)
    predecessor_sets = [set() for _ in range(n_states)]

    for action_index, action in enumerate(ACTIONS):
        row_indices: List[int] = []
        col_indices: List[int] = []
        values: List[float] = []
        action_successors: List[Tuple[Tuple[int, float], ...]] = []
        for state in range(n_states):
            if state == goal_state:
                distribution = {goal_state: 1.0}
                rewards[action_index, state] = 0.0
            else:
                distribution: Dict[int, float] = {}
                for realized_action, probability in action_distribution(action, slip=slip).items():
                    next_state = grid.next_state(state, realized_action)
                    distribution[next_state] = distribution.get(next_state, 0.0) + float(probability)
            support = tuple(sorted((int(next_state), float(prob)) for next_state, prob in distribution.items()))
            action_successors.append(support)
            for next_state, probability in support:
                row_indices.append(state)
                col_indices.append(next_state)
                values.append(probability)
                if state != goal_state:
                    predecessor_sets[next_state].add(state)
        transitions.append(
            sparse.csr_matrix(
                (values, (row_indices, col_indices)),
                shape=(n_states, n_states),
                dtype=float,
            )
        )
        successors_by_action.append(tuple(action_successors))

    return SparseGridModel(
        transitions=tuple(transitions),
        rewards=rewards,
        successors=tuple(successors_by_action),
        predecessors=tuple(tuple(sorted(states)) for states in predecessor_sets),
        goal_state=int(goal_state),
    )


def _result(
    *,
    method: str,
    value: np.ndarray,
    iterations: int,
    time_sec: float,
    backup_count: int,
    residual: float,
    state_updates: int,
) -> Dict[str, object]:
    return {
        "method": method,
        "V": value,
        "iterations": int(iterations),
        "time_sec": float(time_sec),
        "backup_count": int(backup_count),
        "state_updates": int(state_updates),
        "bellman_residual": float(residual),
    }


def bellman_values(model: SparseGridModel, value: np.ndarray, gamma: float) -> np.ndarray:
    q_values = np.stack(
        [
            model.rewards[action] + gamma * model.transitions[action].dot(value)
            for action in range(model.n_actions)
        ],
        axis=0,
    )
    out = np.max(q_values, axis=0)
    out[model.goal_state] = 0.0
    return out


def bellman_residual(model: SparseGridModel, value: np.ndarray, gamma: float) -> float:
    return float(np.max(np.abs(bellman_values(model, value, gamma) - value)))


def sparse_value_iteration_measured(
    model: SparseGridModel,
    gamma: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Dict[str, object]:
    value = np.zeros(model.n_states, dtype=float)
    started = time.perf_counter()
    for iteration in range(1, max_iterations + 1):
        old = value
        value = bellman_values(model, old, gamma)
        delta = float(np.max(np.abs(value - old)))
        if delta < tol:
            elapsed = time.perf_counter() - started
            return _result(
                method="sparse_vectorized_vi",
                value=value,
                iterations=iteration,
                time_sec=elapsed,
                backup_count=iteration * model.n_states * model.n_actions,
                residual=bellman_residual(model, value, gamma),
                state_updates=iteration * model.n_states,
            )
    elapsed = time.perf_counter() - started
    return _result(
        method="sparse_vectorized_vi",
        value=value,
        iterations=max_iterations,
        time_sec=elapsed,
        backup_count=max_iterations * model.n_states * model.n_actions,
        residual=bellman_residual(model, value, gamma),
        state_updates=max_iterations * model.n_states,
    )


def _state_backup(model: SparseGridModel, value: np.ndarray, state: int, gamma: float) -> float:
    if state == model.goal_state:
        return 0.0
    best = -float("inf")
    for action in range(model.n_actions):
        continuation = sum(
            probability * float(value[next_state])
            for next_state, probability in model.successors[action][state]
        )
        best = max(best, float(model.rewards[action, state]) + gamma * continuation)
    return float(best)


def gauss_seidel_value_iteration_measured(
    model: SparseGridModel,
    gamma: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Dict[str, object]:
    value = np.zeros(model.n_states, dtype=float)
    started = time.perf_counter()
    state_updates = 0
    for iteration in range(1, max_iterations + 1):
        delta = 0.0
        for state in range(model.n_states):
            old_value = float(value[state])
            value[state] = _state_backup(model, value, state, gamma)
            delta = max(delta, abs(float(value[state]) - old_value))
            state_updates += 1
        if delta < tol:
            elapsed = time.perf_counter() - started
            return _result(
                method="gauss_seidel_vi",
                value=value,
                iterations=iteration,
                time_sec=elapsed,
                backup_count=state_updates * model.n_actions,
                residual=bellman_residual(model, value, gamma),
                state_updates=state_updates,
            )
    elapsed = time.perf_counter() - started
    return _result(
        method="gauss_seidel_vi",
        value=value,
        iterations=max_iterations,
        time_sec=elapsed,
        backup_count=state_updates * model.n_actions,
        residual=bellman_residual(model, value, gamma),
        state_updates=state_updates,
    )


def prioritized_sweeping_value_iteration_measured(
    model: SparseGridModel,
    gamma: float,
    tol: float = 1e-10,
    max_state_updates: int = 10_000_000,
) -> Dict[str, object]:
    value = np.zeros(model.n_states, dtype=float)
    heap: List[Tuple[float, int]] = []
    residual_cache = np.zeros(model.n_states, dtype=float)
    backup_count = 0
    started = time.perf_counter()

    for state in range(model.n_states):
        residual = abs(_state_backup(model, value, state, gamma) - float(value[state]))
        backup_count += model.n_actions
        residual_cache[state] = residual
        if residual > tol:
            heapq.heappush(heap, (-residual, state))

    state_updates = 0
    while heap and state_updates < max_state_updates:
        neg_priority, state = heapq.heappop(heap)
        queued_priority = -float(neg_priority)
        if queued_priority + 1e-15 < float(residual_cache[state]):
            continue
        updated = _state_backup(model, value, state, gamma)
        backup_count += model.n_actions
        current_residual = abs(updated - float(value[state]))
        if current_residual <= tol:
            residual_cache[state] = current_residual
            continue
        value[state] = updated
        residual_cache[state] = 0.0
        state_updates += 1
        for predecessor in model.predecessors[state]:
            residual = abs(_state_backup(model, value, predecessor, gamma) - float(value[predecessor]))
            backup_count += model.n_actions
            if residual > tol and residual > float(residual_cache[predecessor]) + 1e-15:
                residual_cache[predecessor] = residual
                heapq.heappush(heap, (-residual, predecessor))

    elapsed = time.perf_counter() - started
    residual = bellman_residual(model, value, gamma)
    return _result(
        method="prioritized_sweeping",
        value=value,
        iterations=state_updates,
        time_sec=elapsed,
        backup_count=backup_count,
        residual=residual,
        state_updates=state_updates,
    )


def quantiles(values: Iterable[float]) -> Tuple[float, float, float]:
    array = np.asarray([float(value) for value in values if math.isfinite(float(value))], dtype=float)
    if array.size == 0:
        return float("nan"), float("nan"), float("nan")
    return tuple(float(value) for value in np.quantile(array, [0.25, 0.5, 0.75]))  # type: ignore[return-value]
