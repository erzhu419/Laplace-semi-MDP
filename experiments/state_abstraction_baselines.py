from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import ACTIONS, BellmanKronReduction, GridWorld, action_distribution, bellman_kron_reduce
from finite_mdp_adapter import FiniteMDP, coverage_boundary


@dataclass(frozen=True)
class AbstractMDP:
    blocks: Tuple[Tuple[int, ...], ...]
    state_to_block: np.ndarray
    P: np.ndarray
    R: np.ndarray
    terminal_blocks: Tuple[int, ...]

    @property
    def n_states(self) -> int:
        return len(self.blocks)


def gridworld_finite_mdp(grid: GridWorld, goal_state: int, slip: float) -> FiniteMDP:
    n_states = grid.n_states
    P = np.zeros((len(ACTIONS), n_states, n_states), dtype=float)
    R = np.full((len(ACTIONS), n_states), grid.step_reward, dtype=float)
    for action_index, action in enumerate(ACTIONS):
        for state in range(n_states):
            if state == goal_state:
                P[action_index, state, state] = 1.0
                R[action_index, state] = 0.0
                continue
            for realized_action, probability in action_distribution(action, slip=slip).items():
                P[action_index, state, grid.next_state(state, realized_action)] += float(probability)
    start = grid.symbol_states("S")[0]
    start_distribution = np.zeros(n_states, dtype=float)
    start_distribution[start] = 1.0
    _, index_to_coord = grid.index_maps()
    coords = np.asarray([index_to_coord[state] for state in range(n_states)], dtype=float)
    return FiniteMDP(
        name="gridworld",
        P=P,
        R=R,
        action_names=ACTIONS,
        terminal_states=(goal_state,),
        goal_states=(goal_state,),
        start_states=(start,),
        start_distribution=start_distribution,
        coords=coords,
    )


def _quantized_key(values: Iterable[float], epsilon: float) -> Tuple[int | float, ...]:
    if epsilon <= 0.0:
        return tuple(round(float(value), 12) for value in values)
    return tuple(int(math.floor(float(value) / epsilon + 0.5)) for value in values)


def _state_to_block(blocks: Sequence[Sequence[int]], n_states: int) -> np.ndarray:
    mapping = np.empty(n_states, dtype=int)
    for block_index, block in enumerate(blocks):
        mapping[np.asarray(block, dtype=int)] = block_index
    return mapping


def epsilon_homogeneous_partition(
    mdp: FiniteMDP,
    epsilon: float,
    max_refinements: int = 100,
) -> Tuple[Tuple[int, ...], ...]:
    """Dean-Givan style approximate homogeneous partition.

    States are repeatedly split by immediate-reward vectors and action-wise
    transition mass into the current blocks. ``epsilon=0`` gives the exact
    finite precision refinement used as the model-minimization baseline.
    """

    terminals = mdp.terminal_set()
    reward_scale = max(1.0, float(np.max(np.abs(mdp.R), initial=0.0)))
    initial_groups: Dict[Tuple[object, ...], List[int]] = {}
    for state in range(mdp.n_states):
        key = (
            state in terminals,
            _quantized_key(mdp.R[:, state] / reward_scale, epsilon),
        )
        initial_groups.setdefault(key, []).append(state)
    blocks: Tuple[Tuple[int, ...], ...] = tuple(
        tuple(sorted(group)) for _key, group in sorted(initial_groups.items(), key=lambda item: str(item[0]))
    )

    for _ in range(max_refinements):
        mapping = _state_to_block(blocks, mdp.n_states)
        next_blocks: List[Tuple[int, ...]] = []
        for block in blocks:
            groups: Dict[Tuple[object, ...], List[int]] = {}
            for state in block:
                transition_features: List[float] = []
                for action in range(mdp.n_actions):
                    mass = np.bincount(
                        mapping,
                        weights=mdp.P[action, state],
                        minlength=len(blocks),
                    )
                    transition_features.extend(float(value) for value in mass)
                key = (
                    _quantized_key(mdp.R[:, state] / reward_scale, epsilon),
                    _quantized_key(transition_features, epsilon),
                )
                groups.setdefault(key, []).append(state)
            next_blocks.extend(
                tuple(sorted(group)) for _key, group in sorted(groups.items(), key=lambda item: str(item[0]))
            )
        refined = tuple(sorted(next_blocks, key=lambda block: (block[0], len(block))))
        if refined == blocks:
            return blocks
        blocks = refined
    return blocks


def partition_homogeneity_error(mdp: FiniteMDP, blocks: Sequence[Sequence[int]]) -> float:
    mapping = _state_to_block(blocks, mdp.n_states)
    worst = 0.0
    for block in blocks:
        if len(block) <= 1:
            continue
        reference = int(block[0])
        for state in block[1:]:
            worst = max(worst, float(np.max(np.abs(mdp.R[:, state] - mdp.R[:, reference]))))
            for action in range(mdp.n_actions):
                ref_mass = np.bincount(
                    mapping,
                    weights=mdp.P[action, reference],
                    minlength=len(blocks),
                )
                state_mass = np.bincount(
                    mapping,
                    weights=mdp.P[action, state],
                    minlength=len(blocks),
                )
                worst = max(worst, float(np.max(np.abs(state_mass - ref_mass))))
    return worst


def choose_epsilon_partition(
    mdp: FiniteMDP,
    target_count: int,
    epsilon_grid: Sequence[float] | None = None,
) -> Tuple[Tuple[Tuple[int, ...], ...], float]:
    target_count = max(1, min(int(target_count), mdp.n_states))
    if epsilon_grid is None:
        epsilon_grid = [0.0] + np.geomspace(1e-6, 4.0, 80).tolist()
    candidates: List[Tuple[Tuple[Tuple[int, ...], ...], float]] = []
    seen_signatures = set()
    for epsilon in epsilon_grid:
        partition = epsilon_homogeneous_partition(mdp, float(epsilon))
        signature = tuple(partition)
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        candidates.append((partition, float(epsilon)))
    within_budget = [item for item in candidates if len(item[0]) <= target_count]
    if within_budget:
        return max(within_budget, key=lambda item: (len(item[0]), -item[1]))
    return min(candidates, key=lambda item: (len(item[0]), item[1]))


def aggregate_mdp(mdp: FiniteMDP, blocks: Sequence[Sequence[int]]) -> AbstractMDP:
    blocks_tuple = tuple(tuple(int(state) for state in block) for block in blocks)
    mapping = _state_to_block(blocks_tuple, mdp.n_states)
    n_blocks = len(blocks_tuple)
    P = np.zeros((mdp.n_actions, n_blocks, n_blocks), dtype=float)
    R = np.zeros((mdp.n_actions, n_blocks), dtype=float)
    for block_index, block in enumerate(blocks_tuple):
        states = np.asarray(block, dtype=int)
        for action in range(mdp.n_actions):
            R[action, block_index] = float(np.mean(mdp.R[action, states]))
            mean_transition = np.mean(mdp.P[action, states, :], axis=0)
            P[action, block_index] = np.bincount(
                mapping,
                weights=mean_transition,
                minlength=n_blocks,
            )
    terminal_blocks = tuple(
        block_index
        for block_index, block in enumerate(blocks_tuple)
        if block and all(state in mdp.terminal_set() for state in block)
    )
    return AbstractMDP(
        blocks=blocks_tuple,
        state_to_block=mapping,
        P=P,
        R=R,
        terminal_blocks=terminal_blocks,
    )


def abstract_value_iteration(
    abstract: AbstractMDP,
    gamma: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Tuple[np.ndarray, np.ndarray, int]:
    value = np.zeros(abstract.n_states, dtype=float)
    terminal = np.asarray(abstract.terminal_blocks, dtype=int)
    policy = np.zeros(abstract.n_states, dtype=int)
    for iteration in range(1, max_iterations + 1):
        old = value
        q = abstract.R + gamma * np.einsum("abn,n->ab", abstract.P, old)
        value = np.max(q, axis=0)
        policy = np.argmax(q, axis=0)
        if terminal.size:
            value[terminal] = 0.0
            policy[terminal] = 0
        if float(np.max(np.abs(value - old))) < tol:
            return value, policy, iteration
    return value, policy, max_iterations


def evaluate_lifted_policy(
    mdp: FiniteMDP,
    policy: np.ndarray,
    gamma: float,
) -> np.ndarray:
    states = np.arange(mdp.n_states, dtype=int)
    P_policy = mdp.P[policy, states, :].copy()
    R_policy = mdp.R[policy, states].copy()
    for terminal in mdp.terminal_states:
        P_policy[int(terminal), :] = 0.0
        P_policy[int(terminal), int(terminal)] = 1.0
        R_policy[int(terminal)] = 0.0
    return np.linalg.solve(np.eye(mdp.n_states) - gamma * P_policy, R_policy)


def evaluate_partition(
    mdp: FiniteMDP,
    blocks: Sequence[Sequence[int]],
    full_value: np.ndarray,
    gamma: float,
) -> Dict[str, object]:
    started = time.perf_counter()
    abstract = aggregate_mdp(mdp, blocks)
    construction_time = time.perf_counter() - started
    solve_started = time.perf_counter()
    abstract_value, abstract_policy, iterations = abstract_value_iteration(abstract, gamma=gamma)
    solve_time = time.perf_counter() - solve_started
    lifted_value = abstract_value[abstract.state_to_block]
    lifted_policy = abstract_policy[abstract.state_to_block]
    policy_value = evaluate_lifted_policy(mdp, lifted_policy, gamma=gamma)
    start_distribution = mdp.start_distribution_or_uniform()
    return {
        "n_abstract_states": abstract.n_states,
        "state_compression_ratio": mdp.n_states / max(1, abstract.n_states),
        "construction_time_sec": construction_time,
        "solve_time_sec": solve_time,
        "iterations": iterations,
        "abstract_transition_nnz": int(np.count_nonzero(abstract.P)),
        "start_value_full": float(start_distribution @ full_value),
        "start_value_abstract": float(start_distribution @ lifted_value),
        "start_gap": float(abs(start_distribution @ (full_value - lifted_value))),
        "value_gap_max": float(np.max(np.abs(full_value - lifted_value))),
        "policy_start_gap": float(abs(start_distribution @ (full_value - policy_value))),
        "policy_value_gap_max": float(np.max(np.abs(full_value - policy_value))),
        "homogeneity_error": partition_homogeneity_error(mdp, blocks),
    }


def qstar_oracle_partition(
    mdp: FiniteMDP,
    full_value: np.ndarray,
    gamma: float,
    target_count: int,
    max_iterations: int = 100,
) -> Tuple[Tuple[int, ...], ...]:
    q_values = mdp.R.T + gamma * np.einsum("asn,n->sa", mdp.P, full_value)
    terminal_set = mdp.terminal_set()
    terminal_states = sorted(terminal_set)
    nonterminal = np.asarray([state for state in range(mdp.n_states) if state not in terminal_set], dtype=int)
    n_terminal_blocks = 1 if terminal_states else 0
    k = max(1, min(int(target_count) - n_terminal_blocks, len(nonterminal)))
    if len(nonterminal) <= k:
        blocks = [tuple([int(state)]) for state in nonterminal]
    else:
        features = q_values[nonterminal]
        centers = [0]
        min_distance = np.full(len(nonterminal), float("inf"), dtype=float)
        for _ in range(1, k):
            center = features[centers[-1]]
            min_distance = np.minimum(min_distance, np.sum((features - center) ** 2, axis=1))
            centers.append(int(np.argmax(min_distance)))
        centroid = features[np.asarray(centers, dtype=int)].copy()
        assignment = np.full(len(nonterminal), -1, dtype=int)
        for _ in range(max_iterations):
            distances = np.sum((features[:, None, :] - centroid[None, :, :]) ** 2, axis=2)
            next_assignment = np.argmin(distances, axis=1)
            if np.array_equal(next_assignment, assignment):
                break
            assignment = next_assignment
            for cluster in range(k):
                members = features[assignment == cluster]
                if len(members):
                    centroid[cluster] = np.mean(members, axis=0)
        blocks = [
            tuple(sorted(int(state) for state in nonterminal[assignment == cluster]))
            for cluster in range(k)
            if np.any(assignment == cluster)
        ]
    if terminal_states:
        blocks.append(tuple(terminal_states))
    return tuple(sorted(blocks, key=lambda block: block[0]))


def optimal_policy(mdp: FiniteMDP, value: np.ndarray, gamma: float) -> np.ndarray:
    q_values = mdp.R + gamma * np.einsum("asn,n->as", mdp.P, value)
    policy = np.argmax(q_values, axis=0).astype(int)
    for terminal in mdp.terminal_states:
        policy[int(terminal)] = 0
    return policy


def policy_kron_oracle(
    mdp: FiniteMDP,
    full_value: np.ndarray,
    gamma: float,
    target_count: int,
) -> Dict[str, object]:
    boundary = coverage_boundary(mdp, target_count=target_count)
    policy = optimal_policy(mdp, full_value, gamma=gamma)
    states = np.arange(mdp.n_states, dtype=int)
    P_policy = mdp.P[policy, states, :]
    R_policy = mdp.R[policy, states]
    started = time.perf_counter()
    reduction: BellmanKronReduction = bellman_kron_reduce(P_policy, R_policy, boundary, gamma)
    construction_time = time.perf_counter() - started
    solve_started = time.perf_counter()
    boundary_value = np.linalg.solve(
        np.eye(len(boundary)) - reduction.gamma_terminal,
        reduction.reward,
    )
    solve_time = time.perf_counter() - solve_started

    lifted = np.zeros(mdp.n_states, dtype=float)
    lifted[reduction.boundary] = boundary_value
    if len(reduction.interior):
        P_II = P_policy[np.ix_(reduction.interior, reduction.interior)]
        P_IB = P_policy[np.ix_(reduction.interior, reduction.boundary)]
        rhs = R_policy[reduction.interior] + gamma * P_IB @ boundary_value
        lifted[reduction.interior] = np.linalg.solve(
            np.eye(len(reduction.interior)) - gamma * P_II,
            rhs,
        )
    start_distribution = mdp.start_distribution_or_uniform()
    return {
        "n_abstract_states": len(boundary),
        "state_compression_ratio": mdp.n_states / max(1, len(boundary)),
        "construction_time_sec": construction_time,
        "solve_time_sec": solve_time,
        "abstract_transition_nnz": int(np.count_nonzero(reduction.gamma_terminal)),
        "start_value_full": float(start_distribution @ full_value),
        "start_value_abstract": float(start_distribution @ lifted),
        "start_gap": float(abs(start_distribution @ (full_value - lifted))),
        "value_gap_max": float(np.max(np.abs(full_value - lifted))),
        "policy_start_gap": 0.0,
        "policy_value_gap_max": 0.0,
        "homogeneity_error": float("nan"),
        "boundary": boundary,
    }
