from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import networkx as nx
import numpy as np
from scipy import sparse

from bellman_kron import (
    ACTIONS,
    OPPOSITE,
    GridWorld,
    action_distribution,
    endpoint_boundary_states,
    graph_nx,
    shortest_path_policy_to_target,
)


@dataclass(frozen=True)
class OneShotRDResult:
    boundary: Tuple[int, ...]
    mandatory_boundary: Tuple[int, ...]
    probe_anchors: Tuple[int, ...]
    selected_states: Tuple[int, ...]
    channels: Mapping[str, np.ndarray]
    normalized_channels: Mapping[str, np.ndarray]
    combined_score: np.ndarray
    selection_reasons: Mapping[int, Tuple[str, ...]]
    timings: Mapping[str, float]
    diagnostics: Mapping[str, object]


def grid_neighbors(grid: GridWorld) -> Tuple[Tuple[int, ...], ...]:
    neighbors: List[Tuple[int, ...]] = []
    for state in range(grid.n_states):
        adjacent = {
            int(grid.next_state(state, action))
            for action in ACTIONS
            if int(grid.next_state(state, action)) != state
        }
        neighbors.append(tuple(sorted(adjacent)))
    return tuple(neighbors)


def _multi_source_distances(
    neighbors: Sequence[Sequence[int]],
    sources: Sequence[int],
) -> np.ndarray:
    distance = np.full(len(neighbors), np.inf, dtype=float)
    queue: deque[int] = deque()
    for source in sorted(set(int(state) for state in sources)):
        distance[source] = 0.0
        queue.append(source)
    while queue:
        state = queue.popleft()
        next_distance = distance[state] + 1.0
        for neighbor in neighbors[state]:
            if next_distance < distance[neighbor]:
                distance[neighbor] = next_distance
                queue.append(int(neighbor))
    return distance


def farthest_probe_anchors(
    grid: GridWorld,
    mandatory_boundary: Sequence[int],
    count: int,
) -> Tuple[int, ...]:
    neighbors = grid_neighbors(grid)
    selected = sorted(set(int(state) for state in mandatory_boundary))
    count = max(len(selected), min(int(count), grid.n_states))
    while len(selected) < count:
        distance = _multi_source_distances(neighbors, selected)
        candidates = [state for state in range(grid.n_states) if state not in selected]
        if not candidates:
            break
        next_state = min(candidates, key=lambda state: (-float(distance[state]), state))
        selected.append(int(next_state))
    return tuple(sorted(selected))


def sparse_policy_transition(
    grid: GridWorld,
    policy,
) -> sparse.csr_matrix:
    rows: List[int] = []
    cols: List[int] = []
    data: List[float] = []
    for state in range(grid.n_states):
        next_prob: Dict[int, float] = {}
        distribution = dict(policy(state))
        total = float(sum(distribution.values()))
        if total <= 0.0:
            raise ValueError(f"Policy has no probability mass at state {state}.")
        for action, probability in distribution.items():
            next_state = int(grid.next_state(state, action))
            next_prob[next_state] = next_prob.get(next_state, 0.0) + float(probability) / total
        for next_state, probability in next_prob.items():
            rows.append(state)
            cols.append(next_state)
            data.append(probability)
    return sparse.csr_matrix((data, (rows, cols)), shape=(grid.n_states, grid.n_states))


def truncated_target_green(
    transition: sparse.csr_matrix,
    terminals: Sequence[int],
    target: int,
    gamma: float,
    max_steps: int,
    tail_tol: float,
) -> Tuple[np.ndarray, int, float]:
    """Compute sum_{t=0}^K (gamma P_II)^t P_I,target by sparse propagation."""

    n_states = int(transition.shape[0])
    terminal_set = set(int(state) for state in terminals)
    if target not in terminal_set:
        raise ValueError("target must be one of the first-hit terminals")
    interior = np.array([state for state in range(n_states) if state not in terminal_set], dtype=int)
    response = np.zeros(n_states, dtype=float)
    response[int(target)] = 1.0
    if len(interior) == 0:
        return response, 0, 0.0

    q = transition[interior, :][:, interior].tocsr()
    frontier = np.asarray(transition[interior, int(target)].toarray()).reshape(-1)
    accumulated = frontier.copy()
    used_steps = 0
    for step in range(1, max(0, int(max_steps)) + 1):
        frontier = float(gamma) * np.asarray(q @ frontier).reshape(-1)
        accumulated += frontier
        used_steps = step
        if tail_tol > 0.0 and float(np.max(np.abs(frontier), initial=0.0)) <= tail_tol:
            break
    response[interior] = accumulated
    return response, used_steps, float(np.max(np.abs(frontier), initial=0.0))


def discounted_probe_occupancy(
    transition: sparse.csr_matrix,
    source: int,
    terminals: Sequence[int],
    gamma: float,
    max_steps: int,
    tail_tol: float,
) -> Tuple[np.ndarray, int, float]:
    n_states = int(transition.shape[0])
    stop_mask = np.zeros(n_states, dtype=bool)
    stop_mask[list(sorted(set(int(state) for state in terminals) - {int(source)}))] = True
    mass = np.zeros(n_states, dtype=float)
    mass[int(source)] = 1.0
    occupancy = np.zeros(n_states, dtype=float)
    used_steps = 0
    for step in range(max(0, int(max_steps)) + 1):
        active = mass.copy()
        active[stop_mask] = 0.0
        occupancy += active
        if step >= max_steps:
            break
        mass = float(gamma) * np.asarray(active @ transition).reshape(-1)
        used_steps = step + 1
        if tail_tol > 0.0 and float(np.max(np.abs(mass), initial=0.0)) <= tail_tol:
            break
    return occupancy, used_steps, float(np.max(np.abs(mass), initial=0.0))


def random_walk_laplacian_norm(
    features: np.ndarray,
    neighbors: Sequence[Sequence[int]],
) -> np.ndarray:
    features = np.asarray(features, dtype=float)
    if features.ndim == 1:
        features = features[:, None]
    scale = math.sqrt(max(1, features.shape[1]))
    out = np.zeros(features.shape[0], dtype=float)
    for state, adjacent in enumerate(neighbors):
        if not adjacent:
            continue
        local_mean = np.mean(features[np.asarray(adjacent, dtype=int)], axis=0)
        out[state] = float(np.linalg.norm(features[state] - local_mean) / scale)
    return out


def _policy_features(
    grid: GridWorld,
    anchors: Sequence[int],
    slip: float,
) -> Tuple[np.ndarray, List[sparse.csr_matrix]]:
    action_pos = {action: index for index, action in enumerate(ACTIONS)}
    features = np.zeros((grid.n_states, len(anchors) * len(ACTIONS)), dtype=float)
    transitions: List[sparse.csr_matrix] = []
    for anchor_pos, target in enumerate(anchors):
        policy = shortest_path_policy_to_target(grid, int(target), slip=slip)
        transitions.append(sparse_policy_transition(grid, policy))
        offset = anchor_pos * len(ACTIONS)
        for state in range(grid.n_states):
            for action, probability in policy(state).items():
                features[state, offset + action_pos[action]] = float(probability)
    return features, transitions


def _topology_channel(
    grid: GridWorld,
    neighbors: Sequence[Sequence[int]],
) -> np.ndarray:
    graph = graph_nx(grid)
    articulation = set(int(state) for state in nx.articulation_points(graph))
    degree = np.asarray([len(adjacent) for adjacent in neighbors], dtype=float)
    score = np.zeros(grid.n_states, dtype=float)
    for state in range(grid.n_states):
        actions = grid.legal_actions(state)
        is_straight = len(actions) == 2 and actions[0] == OPPOSITE.get(actions[1])
        degree_deficit = max(0.0, 4.0 - degree[state]) / 4.0
        neighbor_degree = (
            float(np.mean(degree[np.asarray(neighbors[state], dtype=int)]))
            if neighbors[state]
            else degree[state]
        )
        degree_contrast = min(1.0, abs(float(degree[state]) - neighbor_degree) / 2.0)
        turn = 1.0 if len(actions) == 2 and not is_straight else 0.0
        articulation_score = 1.0 if state in articulation and not is_straight else 0.0
        score[state] = max(articulation_score, 0.7 * turn, degree_deficit * degree_contrast)
    return score


def _turn_articulation_mask(
    grid: GridWorld,
) -> np.ndarray:
    articulation = set(int(state) for state in nx.articulation_points(graph_nx(grid)))
    mask = np.zeros(grid.n_states, dtype=bool)
    for state in range(grid.n_states):
        actions = grid.legal_actions(state)
        is_straight = len(actions) == 2 and actions[0] == OPPOSITE.get(actions[1])
        mask[state] = (state in articulation and not is_straight) or (
            len(actions) == 2 and not is_straight
        )
    return mask


def _transition_entropy_channel(grid: GridWorld, slip: float) -> np.ndarray:
    entropy = np.zeros(grid.n_states, dtype=float)
    for state in range(grid.n_states):
        action_entropies: List[float] = []
        for intended_action in ACTIONS:
            next_prob: Dict[int, float] = {}
            for action, probability in action_distribution(intended_action, slip=slip).items():
                next_state = int(grid.next_state(state, action))
                next_prob[next_state] = next_prob.get(next_state, 0.0) + float(probability)
            probabilities = np.asarray(list(next_prob.values()), dtype=float)
            probabilities = probabilities[probabilities > 0.0]
            action_entropies.append(float(-np.sum(probabilities * np.log(probabilities))))
        entropy[state] = max(action_entropies, default=0.0)
    return entropy


def normalize_channel(values: np.ndarray, eligible: np.ndarray) -> np.ndarray:
    values = np.maximum(0.0, np.nan_to_num(np.asarray(values, dtype=float)))
    positive = values[eligible & (values > 0.0)]
    if len(positive) == 0:
        return np.zeros_like(values)
    scale = float(np.percentile(positive, 95.0))
    if scale <= 1e-15:
        scale = float(np.max(positive))
    return np.clip(values / max(scale, 1e-15), 0.0, 1.0)


def _channel_local_maxima(
    values: np.ndarray,
    eligible: np.ndarray,
    neighbors: Sequence[Sequence[int]],
    threshold: float,
) -> List[int]:
    maxima: List[int] = []
    for state in np.flatnonzero(eligible & (values >= threshold)).astype(int).tolist():
        adjacent = [int(neighbor) for neighbor in neighbors[state] if eligible[int(neighbor)]]
        if not adjacent:
            maxima.append(state)
            continue
        neighbor_values = values[np.asarray(adjacent, dtype=int)]
        if values[state] + 1e-12 < float(np.max(neighbor_values, initial=0.0)):
            continue
        tied = [neighbor for neighbor in adjacent if abs(float(values[neighbor] - values[state])) <= 1e-12]
        if tied and state > min(tied):
            continue
        if float(values[state]) <= float(np.min(neighbor_values, initial=values[state])) + 1e-12:
            continue
        maxima.append(state)
    return maxima


def apply_one_shot_rd_operator(
    grid: GridWorld,
    slip: float,
    gamma: float = 0.97,
    mandatory_boundary: Sequence[int] | None = None,
    active_pairs: Sequence[Tuple[int, int]] | None = None,
    candidate_states: Sequence[int] | None = None,
    probe_anchors: Sequence[int] | None = None,
    probe_count: int | None = None,
    truncation_steps: int = 256,
    tail_tol: float = 1e-6,
    max_splits: int = 18,
    channel_threshold: float = 0.55,
    min_channel_support: int = 2,
    mandatory_exclusion_radius: int = 1,
    gate_channels: Sequence[str] = ("topology", "stochastic"),
    candidate_universe: str = "turn_articulation",
    include_probe_anchors: bool = False,
) -> OneShotRDResult:
    """Apply a frozen multi-channel Green operator once, then threshold once."""

    total_started = time.perf_counter()
    mandatory = tuple(sorted(set(mandatory_boundary or endpoint_boundary_states(grid))))
    if active_pairs is None:
        starts = grid.symbol_states("S")
        goals = grid.symbol_states("G")
        if starts and goals:
            active_pairs = [(int(starts[0]), int(goals[0]))]
        else:
            active_pairs = [
                (int(source), int(target))
                for source in mandatory
                for target in mandatory
                if int(source) != int(target)
            ]
    active_pairs = tuple((int(source), int(target)) for source, target in active_pairs)
    started = time.perf_counter()
    neighbors = grid_neighbors(grid)
    mandatory_mask = np.zeros(grid.n_states, dtype=bool)
    mandatory_mask[list(mandatory)] = True
    eligible = ~mandatory_mask
    structural_mask = _turn_articulation_mask(grid)
    if candidate_states is not None:
        supplied_mask = np.zeros(grid.n_states, dtype=bool)
        supplied_mask[
            [int(state) for state in candidate_states if 0 <= int(state) < grid.n_states]
        ] = True
        eligible &= supplied_mask
        effective_candidate_universe = "supplied"
    elif candidate_universe == "turn_articulation":
        eligible &= structural_mask
        effective_candidate_universe = candidate_universe
    elif candidate_universe != "all":
        raise ValueError(f"Unknown one-shot candidate universe: {candidate_universe!r}")
    else:
        effective_candidate_universe = candidate_universe
    if mandatory_exclusion_radius > 0:
        mandatory_distance = _multi_source_distances(neighbors, mandatory)
        eligible &= mandatory_distance > float(mandatory_exclusion_radius)
    candidate_universe_time = time.perf_counter() - started

    if not np.any(eligible):
        zeros = np.zeros(grid.n_states, dtype=float)
        timings = {
            "candidate_universe_time_sec": candidate_universe_time,
            "probe_build_time_sec": 0.0,
            "green_message_passing_time_sec": 0.0,
            "operator_apply_time_sec": 0.0,
            "threshold_time_sec": 0.0,
            "total_operator_time_sec": time.perf_counter() - total_started,
        }
        diagnostics = {
            "n_states": grid.n_states,
            "n_mandatory": len(mandatory),
            "n_probe_anchors": 0,
            "active_pairs": active_pairs,
            "n_selected": 0,
            "n_candidates": 0,
            "truncation_steps": int(truncation_steps),
            "used_steps_max": 0,
            "frontier_max": 0.0,
            "green_steps_by_anchor": {},
            "green_frontier_by_anchor": {},
            "occupancy_steps_by_pair": {},
            "occupancy_frontier_by_pair": {},
            "green_steps_total": 0,
            "occupancy_steps_total": 0,
            "tail_tol": float(tail_tol),
            "channel_threshold": float(channel_threshold),
            "min_channel_support": int(min_channel_support),
            "mandatory_exclusion_radius": int(mandatory_exclusion_radius),
            "gate_channels": tuple(str(name) for name in gate_channels),
            "candidate_universe": effective_candidate_universe,
            "max_splits": int(max_splits),
            "message_passing_sparse": True,
            "iterative_candidate_recompute": False,
            "n_green_response_passes": 0,
            "n_candidate_insertion_evaluations": 0,
            "n_beam_expansions": 0,
            "early_exit": "empty_candidate_universe",
        }
        empty_channels = {
            name: zeros.copy()
            for name in ("flow", "green", "control", "topology", "stochastic")
        }
        return OneShotRDResult(
            boundary=mandatory,
            mandatory_boundary=mandatory,
            probe_anchors=(),
            selected_states=(),
            channels=empty_channels,
            normalized_channels={name: values.copy() for name, values in empty_channels.items()},
            combined_score=zeros.copy(),
            selection_reasons={},
            timings=timings,
            diagnostics=diagnostics,
        )

    if probe_anchors is not None:
        anchors = tuple(
            sorted(
                set(mandatory)
                .union(int(state) for state in probe_anchors if 0 <= int(state) < grid.n_states)
                .union(target for _source, target in active_pairs)
            )
        )
    else:
        anchors = ()
    if not anchors and probe_count is None:
        probe_count = len(mandatory)

    started = time.perf_counter()
    if not anchors:
        anchors = farthest_probe_anchors(grid, mandatory, count=int(probe_count))
    policy_features, transitions = _policy_features(grid, anchors, slip=slip)
    probe_build_time = time.perf_counter() - started

    started = time.perf_counter()
    green_features = np.zeros((grid.n_states, len(anchors)), dtype=float)
    exposure = np.zeros(grid.n_states, dtype=float)
    used_steps = 0
    frontier_max = 0.0
    green_steps_by_anchor: Dict[str, int] = {}
    green_frontier_by_anchor: Dict[str, float] = {}
    occupancy_steps_by_pair: Dict[str, int] = {}
    occupancy_frontier_by_pair: Dict[str, float] = {}
    for anchor_pos, (target, transition) in enumerate(zip(anchors, transitions)):
        response, response_steps, response_frontier = truncated_target_green(
            transition=transition,
            terminals=anchors,
            target=int(target),
            gamma=gamma,
            max_steps=truncation_steps,
            tail_tol=tail_tol,
        )
        green_features[:, anchor_pos] = response
        green_steps_by_anchor[str(int(target))] = int(response_steps)
        green_frontier_by_anchor[str(int(target))] = float(response_frontier)
        used_steps = max(used_steps, response_steps)
        frontier_max = max(frontier_max, response_frontier)
        matching_sources = [source for source, pair_target in active_pairs if pair_target == int(target)]
        if matching_sources:
            for source in matching_sources:
                occupancy, occupancy_steps, occupancy_frontier = discounted_probe_occupancy(
                    transition=transition,
                    source=int(source),
                    terminals=tuple(sorted(set(mandatory).union({int(target)}))),
                    gamma=gamma,
                    max_steps=truncation_steps,
                    tail_tol=tail_tol,
                )
                pair_key = f"{int(source)}->{int(target)}"
                occupancy_steps_by_pair[pair_key] = int(occupancy_steps)
                occupancy_frontier_by_pair[pair_key] = float(occupancy_frontier)
                exposure = np.maximum(exposure, occupancy)
                used_steps = max(used_steps, occupancy_steps)
                frontier_max = max(frontier_max, occupancy_frontier)
    green_time = time.perf_counter() - started

    started = time.perf_counter()
    topology_raw = _topology_channel(grid, neighbors)
    green_curvature = random_walk_laplacian_norm(green_features, neighbors)
    policy_curvature = random_walk_laplacian_norm(policy_features, neighbors)
    entropy = _transition_entropy_channel(grid, slip=slip)
    entropy_curvature = random_walk_laplacian_norm(entropy, neighbors)
    exposure_scale = exposure / max(1e-15, float(np.max(exposure, initial=0.0)))
    exposure_gate = np.sqrt(np.clip(exposure_scale, 0.0, 1.0))
    topology_gate = 0.2 + 0.8 * topology_raw
    channels: Dict[str, np.ndarray] = {
        "flow": exposure_gate,
        "green": green_curvature * exposure_gate * topology_gate,
        "control": policy_curvature * exposure_gate * topology_gate,
        "topology": topology_raw * exposure_gate,
        "stochastic": entropy_curvature * exposure_gate,
    }
    anchor_mask = np.zeros(grid.n_states, dtype=bool)
    anchor_mask[list(anchors)] = True
    # An explicitly supplied candidate universe is authoritative.  In
    # particular, group-audit experiments may intentionally score anchors that
    # are not turn/articulation states.
    if not include_probe_anchors and candidate_states is None:
        eligible &= ~(anchor_mask & ~structural_mask)
    normalized = {name: normalize_channel(values, eligible) for name, values in channels.items()}
    score_time = time.perf_counter() - started

    started = time.perf_counter()
    reasons: Dict[int, List[str]] = {}
    for name, values in normalized.items():
        for state in _channel_local_maxima(values, eligible, neighbors, threshold=channel_threshold):
            reasons.setdefault(int(state), []).append(name)
    reasons = {
        state: names
        for state, names in reasons.items()
        if len(names) >= max(1, int(min_channel_support))
        and (not gate_channels or any(name in gate_channels for name in names))
    }
    combined = np.zeros(grid.n_states, dtype=float)
    support = np.zeros(grid.n_states, dtype=float)
    for values in normalized.values():
        combined = np.maximum(combined, values)
        support += values >= channel_threshold
    ranked = sorted(
        reasons,
        key=lambda state: (
            -float(normalized["flow"][state]),
            -float(support[state]),
            -float(combined[state]),
            -float(sum(values[state] for values in normalized.values())),
            int(state),
        ),
    )
    selected = tuple(sorted(ranked[: max(0, int(max_splits))]))
    boundary = tuple(sorted(set(mandatory).union(selected)))
    selection_time = time.perf_counter() - started

    timings = {
        "candidate_universe_time_sec": candidate_universe_time,
        "probe_build_time_sec": probe_build_time,
        "green_message_passing_time_sec": green_time,
        "operator_apply_time_sec": score_time,
        "threshold_time_sec": selection_time,
        "total_operator_time_sec": time.perf_counter() - total_started,
    }
    diagnostics: Dict[str, object] = {
        "n_states": grid.n_states,
        "n_mandatory": len(mandatory),
        "n_probe_anchors": len(anchors),
        "active_pairs": active_pairs,
        "n_selected": len(selected),
        "n_candidates": int(np.count_nonzero(eligible)),
        "truncation_steps": int(truncation_steps),
        "used_steps_max": int(used_steps),
        "frontier_max": float(frontier_max),
        "green_steps_by_anchor": green_steps_by_anchor,
        "green_frontier_by_anchor": green_frontier_by_anchor,
        "occupancy_steps_by_pair": occupancy_steps_by_pair,
        "occupancy_frontier_by_pair": occupancy_frontier_by_pair,
        "green_steps_total": int(sum(green_steps_by_anchor.values())),
        "occupancy_steps_total": int(sum(occupancy_steps_by_pair.values())),
        "tail_tol": float(tail_tol),
        "channel_threshold": float(channel_threshold),
        "min_channel_support": int(min_channel_support),
        "mandatory_exclusion_radius": int(mandatory_exclusion_radius),
        "gate_channels": tuple(str(name) for name in gate_channels),
        "candidate_universe": effective_candidate_universe,
        "max_splits": int(max_splits),
        "message_passing_sparse": True,
        "iterative_candidate_recompute": False,
        "n_green_response_passes": len(anchors),
        "n_candidate_insertion_evaluations": 0,
        "n_beam_expansions": 0,
    }
    return OneShotRDResult(
        boundary=boundary,
        mandatory_boundary=mandatory,
        probe_anchors=anchors,
        selected_states=selected,
        channels=channels,
        normalized_channels=normalized,
        combined_score=combined,
        selection_reasons={state: tuple(sorted(names)) for state, names in reasons.items()},
        timings=timings,
        diagnostics=diagnostics,
    )
