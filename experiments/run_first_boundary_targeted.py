#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import networkx as nx
import numpy as np

from bellman_kron import (
    BellmanKronReduction,
    GridWorld,
    OPPOSITE,
    all_boundary_states,
    bellman_kron_reduce,
    corridor_map,
    critical_saliency,
    decision_boundary_states,
    default_map,
    endpoint_boundary_states,
    first_hit_interior_occupancy,
    first_hit_reduce,
    four_rooms_map,
    graph_adjacency,
    graph_nx,
    junction_boundary_states,
    open_room_map,
    primitive_value_iteration,
    shortest_path_distance_matrix,
    shortest_path_policy_to_target,
    smdp_value_iteration,
    transition_matrix_for_policy,
)
from run_ablation import policy_complexity_stats


MAPS: Dict[str, Tuple[str, ...]] = {
    "corridor": corridor_map(),
    "open_room": open_room_map(),
    "four_rooms": four_rooms_map(),
    "maze": default_map(),
}


def parse_count_suffix(kind: str) -> int:
    try:
        return int(kind.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Candidate kind must end with a count suffix: {kind}") from exc


def eigenoption_terminal_boundary_states(grid: GridWorld, target_count: int, keep_symbols: str = "SG") -> List[int]:
    keep = set(grid.symbol_states(keep_symbols))
    if len(keep) >= target_count:
        return sorted(keep)

    adjacency = graph_adjacency(grid)
    degree = adjacency.sum(axis=1)
    inv_sqrt_degree = np.zeros_like(degree)
    positive = degree > 0
    inv_sqrt_degree[positive] = 1.0 / np.sqrt(degree[positive])
    normalized_laplacian = np.eye(grid.n_states) - (
        inv_sqrt_degree[:, None] * adjacency * inv_sqrt_degree[None, :]
    )
    eigenvalues, eigenvectors = np.linalg.eigh(normalized_laplacian)
    order = np.argsort(eigenvalues)

    boundary = set(keep)
    for vector_idx in order[1:]:
        vector = eigenvectors[:, int(vector_idx)]
        candidates = [int(np.argmin(vector)), int(np.argmax(vector))]
        for state in sorted(candidates, key=lambda s: (-abs(float(vector[s])), s)):
            boundary.add(state)
            if len(boundary) >= target_count:
                return sorted(boundary)
    return sorted(boundary)


def coverage_boundary_states(grid: GridWorld, target_count: int, keep_symbols: str = "SG") -> List[int]:
    boundary = set(grid.symbol_states(keep_symbols))
    if len(boundary) >= target_count:
        return sorted(boundary)

    distances = shortest_path_distance_matrix(grid)
    while len(boundary) < target_count:
        best_state = None
        best_distance = -1.0
        for state in range(grid.n_states):
            if state in boundary:
                continue
            nearest = min(float(distances[state, b]) for b in boundary)
            if nearest > best_distance + 1e-12 or (
                abs(nearest - best_distance) <= 1e-12 and (best_state is None or state < best_state)
            ):
                best_state = state
                best_distance = nearest
        if best_state is None:
            break
        boundary.add(best_state)
    return sorted(boundary)


def candidate_boundary_states(
    grid: GridWorld,
    kind: str,
    goal_state: int,
    gamma: float,
    slip: float,
    top_fraction: float,
) -> List[int]:
    if kind == "all":
        candidates = all_boundary_states(grid)
    elif kind == "junction":
        candidates = junction_boundary_states(grid)
    elif kind == "decision":
        candidates = decision_boundary_states(grid)
    elif kind == "articulation_only":
        graph = graph_nx(grid)
        articulation = set(nx.articulation_points(graph))
        candidates = []
        for state in articulation:
            actions = grid.legal_actions(state)
            is_straight_corridor = len(actions) == 2 and actions[0] == OPPOSITE.get(actions[1])
            if not is_straight_corridor:
                candidates.append(state)
    elif kind == "turn_articulation":
        graph = graph_nx(grid)
        articulation = set(nx.articulation_points(graph))
        candidates = []
        for state in range(grid.n_states):
            actions = grid.legal_actions(state)
            degree = len(actions)
            is_straight_corridor = degree == 2 and actions[0] == OPPOSITE.get(actions[1])
            if (state in articulation and not is_straight_corridor) or (degree == 2 and not is_straight_corridor):
                candidates.append(state)
    elif kind.startswith("eigen_extrema_"):
        candidates = eigenoption_terminal_boundary_states(grid, target_count=parse_count_suffix(kind))
    elif kind.startswith("coverage_"):
        candidates = coverage_boundary_states(grid, target_count=parse_count_suffix(kind))
    elif kind.startswith("articulation_eigen_extrema_"):
        count = parse_count_suffix(kind)
        candidates = sorted(
            set(candidate_boundary_states(grid, "articulation_only", goal_state, gamma, slip, top_fraction)).union(
                eigenoption_terminal_boundary_states(grid, target_count=count)
            )
        )
    elif kind.startswith("turn_eigen_extrema_"):
        count = parse_count_suffix(kind)
        candidates = sorted(
            set(candidate_boundary_states(grid, "turn_articulation", goal_state, gamma, slip, top_fraction)).union(
                eigenoption_terminal_boundary_states(grid, target_count=count)
            )
        )
    elif kind.startswith("articulation_coverage_"):
        count = parse_count_suffix(kind)
        candidates = sorted(
            set(candidate_boundary_states(grid, "articulation_only", goal_state, gamma, slip, top_fraction)).union(
                coverage_boundary_states(grid, target_count=count)
            )
        )
    elif kind.startswith("turn_coverage_"):
        count = parse_count_suffix(kind)
        candidates = sorted(
            set(candidate_boundary_states(grid, "turn_articulation", goal_state, gamma, slip, top_fraction)).union(
                coverage_boundary_states(grid, target_count=count)
            )
        )
    else:
        score = critical_saliency(
            grid,
            kind=kind,
            goal_state=goal_state,
            gamma=gamma,
            slip=slip,
            top_fraction=top_fraction,
        )
        candidates = np.flatnonzero(score > 1e-12).astype(int).tolist()
    candidates = sorted(set(candidates).union(endpoint_boundary_states(grid)))
    return candidates


def empty_pair_reduction(boundary: Sequence[int], gamma: float) -> BellmanKronReduction:
    n_boundary = len(boundary)
    zeros = np.zeros((n_boundary, n_boundary), dtype=float)
    return BellmanKronReduction(
        boundary=np.array(boundary, dtype=int),
        interior=np.array([], dtype=int),
        gamma=gamma,
        gamma_terminal=zeros.copy(),
        reward=np.zeros(n_boundary, dtype=float),
        laplacian=np.eye(n_boundary, dtype=float),
        hit_probability=zeros.copy(),
        expected_tau=np.full((n_boundary, n_boundary), np.nan, dtype=float),
    )


def normalize_structural_prob(p_hidden: float, p_ref_upper: float) -> float:
    if p_ref_upper >= 1.0:
        return 0.0
    return max(0.0, (p_hidden - p_ref_upper) / max(1e-12, 1.0 - p_ref_upper))


def structural_bits(p_norm: float, eps: float = 1e-12) -> float:
    return float(-np.log2(max(eps, 1.0 - p_norm)))


def tail_cvar(values: Sequence[float], alpha: float = 0.95) -> float:
    if not values:
        return 0.0
    sorted_values = np.sort(np.asarray(values, dtype=float))
    start = min(len(sorted_values) - 1, int(np.floor(alpha * len(sorted_values))))
    return float(np.mean(sorted_values[start:]))


def log2_comb(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("inf")
    if k == 0 or k == n:
        return 0.0
    return float((math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(2.0))


def boundary_code_bits(n_states: int, n_boundary: int, n_fixed: int = 2) -> float:
    available = max(0, n_states - n_fixed)
    selected = max(0, n_boundary - n_fixed)
    return log2_comb(available, selected) + math.log2(max(2, selected + 1))


def edge_code_bits(n_boundary: int, n_edges_valid: int) -> float:
    possible = max(0, n_boundary * max(0, n_boundary - 1))
    if possible == 0:
        return 0.0
    return log2_comb(possible, min(n_edges_valid, possible))


def selection_code_bits(n_candidates: int, batch_size: int) -> float:
    if batch_size <= 1:
        return math.log2(max(2, n_candidates))
    return log2_comb(n_candidates, batch_size) + math.log2(max(2, batch_size + 1))


def build_first_boundary_reductions(
    grid: GridWorld,
    boundary: Sequence[int],
    candidate_boundary: Sequence[int],
    residual_boundary: Sequence[int],
    soft_state_cost: np.ndarray,
    value_scale_task: float,
    slip: float,
    gamma: float,
    local_horizon: float,
    hidden_threshold: float,
    soft_threshold: float,
    residual_threshold: float,
    residual_reward_weight: float,
    residual_hit_weight: float,
    residual_threshold_mode: str,
    compute_struct_distinct: bool,
    proposal_boundary: Sequence[int] | None = None,
) -> Tuple[
    Dict[str, BellmanKronReduction],
    Dict[str, np.ndarray],
    Dict[str, object],
    Dict[str, object],
    List[Dict[str, object]],
]:
    boundary = sorted(set(boundary))
    candidate_boundary = sorted(set(candidate_boundary).union(boundary))
    residual_boundary = sorted(set(residual_boundary).union(boundary))
    if proposal_boundary is None:
        proposal_boundary = candidate_boundary
    proposal_boundary = sorted(set(proposal_boundary).union(candidate_boundary).union(boundary))
    boundary_set = set(boundary)
    proposal_boundary_set = set(proposal_boundary)
    boundary_pos = {state: pos for pos, state in enumerate(boundary)}
    _, idx_to_coord = grid.index_maps()
    distances = shortest_path_distance_matrix(grid)

    reductions: Dict[str, BellmanKronReduction] = {}
    valid_actions: Dict[str, np.ndarray] = {}
    target_policies: Dict[str, object] = {}
    pair_policies: Dict[str, object] = {}
    edge_rows: List[Dict[str, object]] = []

    for target_pos, target_state in enumerate(boundary):
        target_policy = shortest_path_policy_to_target(grid, target_state, slip=slip)
        target_policies[f"to_{target_pos:03d}"] = target_policy
        P_free, r_free = transition_matrix_for_policy(grid, target_policy, absorbing=[])
        P_global, r_global = transition_matrix_for_policy(grid, target_policy, absorbing=[target_state])
        global_reduction = bellman_kron_reduce(P_global, r_global, boundary=boundary, gamma=gamma)
        for src_pos, src_state in enumerate(boundary):
            if src_state == target_state:
                continue

            label = f"fb_{src_pos:03d}_to_{target_pos:03d}"
            pair_policies[label] = target_policy
            terminals = [state for state in candidate_boundary if state != src_state]
            P, r = transition_matrix_for_policy(grid, target_policy, absorbing=terminals)
            first_hit = first_hit_reduce(
                P=P,
                r=r,
                start_state=src_state,
                terminals=terminals,
                gamma=gamma,
            )

            hidden_probs: Dict[int, float] = {}
            hidden_gamma_mass = 0.0
            visible_mass = 0.0
            for term, prob, discounted_prob in zip(
                first_hit.terminals,
                first_hit.hit_probability,
                first_hit.gamma_terminal,
            ):
                term_int = int(term)
                if term_int in boundary_set:
                    visible_mass += float(prob)
                else:
                    hidden_probs[term_int] = float(prob)
                    hidden_gamma_mass += float(discounted_prob)

            hidden_mass = float(sum(hidden_probs.values()))
            if hidden_probs:
                hidden_argmax, hidden_argmax_prob = max(hidden_probs.items(), key=lambda item: item[1])
            else:
                hidden_argmax, hidden_argmax_prob = None, 0.0

            residual_reward_abs = 0.0
            residual_gamma_l1 = 0.0
            residual_hit_l1 = 0.0
            residual_hidden_mass = 0.0
            residual_hidden_gamma_mass = 0.0
            residual_argmax = None
            residual_argmax_prob = 0.0
            residual_model = 0.0
            residual_backup_raw = 0.0
            residual_backup_value = 0.0
            residual_backup_value_norm = 0.0
            residual_reward_per_discounted_step = 0.0
            residual_gamma_relative = 0.0
            residual_tau_relative = 0.0
            struct_hidden_prob = 0.0
            struct_hit_prob = 0.0
            struct_nohit_prob = 0.0
            struct_reference_prob = 0.0
            struct_hidden_norm = 0.0
            struct_hidden_bits = 0.0
            struct_hidden_distinct = 0.0
            struct_hidden_distinct_bits = 0.0
            struct_distinct_scores: Dict[int, float] = {}
            struct_distinct_argmax = None
            struct_distinct_argmax_score = 0.0
            global_hit_row = global_reduction.hit_probability[src_pos]
            global_tau_row = global_reduction.expected_tau[src_pos]
            global_tau_mask = np.isfinite(global_tau_row) & (global_hit_row > 1e-12)
            expected_tau_global = (
                float(np.sum(global_hit_row[global_tau_mask] * global_tau_row[global_tau_mask]))
                / max(1e-12, float(np.sum(global_hit_row[global_tau_mask])))
                if np.any(global_tau_mask)
                else 0.0
            )
            beta_row = float(np.sum(global_reduction.gamma_terminal[src_pos]))
            beta_gap = max(1e-12, 1.0 - min(beta_row, 1.0 - 1e-12))
            l_gamma_row = (1.0 - beta_row) / max(1e-12, 1.0 - gamma)
            expected_tau_residual = 0.0
            residual_terminals = [state for state in residual_boundary if state != src_state]
            if residual_terminals:
                P_residual, r_residual = transition_matrix_for_policy(
                    grid,
                    target_policy,
                    absorbing=residual_terminals,
                )
                residual_first_hit = first_hit_reduce(
                    P=P_residual,
                    r=r_residual,
                    start_state=src_state,
                    terminals=residual_terminals,
                    gamma=gamma,
                )
                residual_gamma_boundary = np.zeros(len(boundary), dtype=float)
                residual_hit_boundary = np.zeros(len(boundary), dtype=float)
                residual_hidden_probs: Dict[int, float] = {}
                for term, prob, discounted_prob in zip(
                    residual_first_hit.terminals,
                    residual_first_hit.hit_probability,
                    residual_first_hit.gamma_terminal,
                ):
                    term_int = int(term)
                    if term_int in boundary_pos:
                        dst_pos = boundary_pos[term_int]
                        residual_gamma_boundary[dst_pos] = float(discounted_prob)
                        residual_hit_boundary[dst_pos] = float(prob)
                    else:
                        residual_hidden_probs[term_int] = float(prob)
                        residual_hidden_gamma_mass += float(discounted_prob)
                residual_hidden_mass = float(sum(residual_hidden_probs.values()))
                struct_hidden_prob = residual_hidden_mass
                struct_hit_prob = float(np.sum(residual_first_hit.hit_probability))
                struct_nohit_prob = max(0.0, 1.0 - struct_hit_prob)
                struct_hidden_norm = normalize_structural_prob(
                    struct_hidden_prob,
                    p_ref_upper=struct_reference_prob,
                )
                struct_hidden_bits = structural_bits(struct_hidden_norm)
                if compute_struct_distinct:
                    struct_score_states = sorted(
                        set(residual_hidden_probs).union(proposal_boundary_set - boundary_set - {src_state})
                    )
                    for hidden_state in struct_score_states:
                        distinct_terminals = sorted((boundary_set - {src_state}).union({int(hidden_state)}))
                        if not distinct_terminals:
                            continue
                        distinct_first_hit = first_hit_reduce(
                            P=P_free,
                            r=r_free,
                            start_state=src_state,
                            terminals=distinct_terminals,
                            gamma=gamma,
                        )
                        hidden_positions = np.flatnonzero(distinct_first_hit.terminals == int(hidden_state))
                        if len(hidden_positions) == 0:
                            continue
                        p_hidden_distinct = float(distinct_first_hit.hit_probability[int(hidden_positions[0])])
                        struct_distinct_scores[int(hidden_state)] = p_hidden_distinct
                        if int(hidden_state) in residual_hidden_probs:
                            struct_hidden_distinct += p_hidden_distinct
                            struct_hidden_distinct_bits += structural_bits(
                                normalize_structural_prob(p_hidden_distinct, p_ref_upper=struct_reference_prob)
                            )
                    if struct_distinct_scores:
                        struct_distinct_argmax, struct_distinct_argmax_score = max(
                            struct_distinct_scores.items(),
                            key=lambda item: item[1],
                        )
                if residual_hidden_probs:
                    residual_argmax, residual_argmax_prob = max(
                        residual_hidden_probs.items(),
                        key=lambda item: item[1],
                    )
                residual_reward_abs = abs(float(global_reduction.reward[src_pos] - residual_first_hit.reward))
                residual_gamma_l1 = float(
                    np.sum(np.abs(global_reduction.gamma_terminal[src_pos] - residual_gamma_boundary))
                )
                residual_hit_l1 = float(
                    np.sum(np.abs(global_reduction.hit_probability[src_pos] - residual_hit_boundary))
                )
                residual_model = (
                    residual_gamma_l1
                    + residual_reward_weight * residual_reward_abs
                    + residual_hit_weight * residual_hit_l1
                )
                residual_tau_mask = np.isfinite(residual_first_hit.expected_tau) & (
                    residual_first_hit.hit_probability > 1e-12
                )
                expected_tau_residual = (
                    float(
                        np.sum(
                            residual_first_hit.hit_probability[residual_tau_mask]
                            * residual_first_hit.expected_tau[residual_tau_mask]
                        )
                    )
                    / max(1e-12, float(np.sum(residual_first_hit.hit_probability[residual_tau_mask])))
                    if np.any(residual_tau_mask)
                    else 0.0
                )
                residual_backup_raw = residual_reward_abs + residual_gamma_l1
                residual_backup_value = residual_reward_abs + value_scale_task * residual_gamma_l1
                residual_backup_value_norm = residual_backup_value / (beta_gap * value_scale_task)
                residual_reward_per_discounted_step = residual_reward_abs / max(
                    1e-12,
                    abs(float(grid.step_reward)) * max(l_gamma_row, 1e-12),
                )
                residual_gamma_relative = residual_gamma_l1 / max(beta_row, 1e-12)
                residual_tau_relative = abs(expected_tau_residual - expected_tau_global) / (
                    1.0 + expected_tau_global
                )

            if residual_threshold_mode == "value_norm":
                residual_threshold_metric = residual_backup_value_norm
            elif residual_threshold_mode == "struct_prob":
                residual_threshold_metric = struct_hidden_norm
            elif residual_threshold_mode == "struct_bits":
                residual_threshold_metric = struct_hidden_bits
            elif residual_threshold_mode == "struct_distinct":
                residual_threshold_metric = struct_hidden_distinct
            else:
                residual_threshold_metric = residual_model

            soft_cost = 0.0
            soft_argmax = None
            soft_argmax_score = 0.0
            if np.any(soft_state_cost > 1e-12):
                pair_soft_cost = soft_state_cost.copy()
                pair_soft_cost[np.array(boundary, dtype=int)] = 0.0
                interior, occupancy = first_hit_interior_occupancy(
                    P=P,
                    start_state=src_state,
                    terminals=terminals,
                    gamma=gamma,
                )
                if len(interior) > 0:
                    soft_scores = occupancy * pair_soft_cost[interior]
                    soft_cost = float(soft_scores.sum())
                    if soft_scores.max(initial=0.0) > 1e-12:
                        best_idx = int(np.argmax(soft_scores))
                        soft_argmax = int(interior[best_idx])
                        soft_argmax_score = float(soft_scores[best_idx])

            within_horizon = float(distances[src_state, target_state]) <= local_horizon
            edge_valid = bool(within_horizon and hidden_mass <= hidden_threshold)
            reduction = empty_pair_reduction(boundary, gamma=gamma)
            reduction.reward[src_pos] = first_hit.reward
            for term, prob, discounted_prob, expected_tau in zip(
                first_hit.terminals,
                first_hit.hit_probability,
                first_hit.gamma_terminal,
                first_hit.expected_tau,
            ):
                term_int = int(term)
                if term_int not in boundary_pos:
                    continue
                dst_pos = boundary_pos[term_int]
                reduction.hit_probability[src_pos, dst_pos] = float(prob)
                reduction.gamma_terminal[src_pos, dst_pos] = float(discounted_prob)
                reduction.expected_tau[src_pos, dst_pos] = float(expected_tau)
            reduction = BellmanKronReduction(
                boundary=reduction.boundary,
                interior=reduction.interior,
                gamma=reduction.gamma,
                gamma_terminal=reduction.gamma_terminal,
                reward=reduction.reward,
                laplacian=np.eye(len(boundary), dtype=float) - reduction.gamma_terminal,
                hit_probability=reduction.hit_probability,
                expected_tau=reduction.expected_tau,
            )
            valid = np.zeros(len(boundary), dtype=bool)
            valid[src_pos] = edge_valid
            reductions[label] = reduction
            valid_actions[label] = valid

            edge_rows.append(
                {
                    "option": label,
                    "src_state": int(src_state),
                    "src_coord": idx_to_coord[int(src_state)],
                    "target_state": int(target_state),
                    "target_coord": idx_to_coord[int(target_state)],
                    "primitive_distance": float(distances[src_state, target_state]),
                    "within_horizon": within_horizon,
                    "edge_valid": edge_valid,
                    "visible_mass": visible_mass,
                    "hidden_mass": hidden_mass,
                    "hidden_gamma_mass": hidden_gamma_mass,
                    "hidden_argmax_state": hidden_argmax,
                    "hidden_argmax_coord": idx_to_coord[hidden_argmax] if hidden_argmax is not None else None,
                    "hidden_argmax_prob": hidden_argmax_prob,
                    "soft_cost": soft_cost,
                    "soft_argmax_state": soft_argmax,
                    "soft_argmax_coord": idx_to_coord[soft_argmax] if soft_argmax is not None else None,
                    "soft_argmax_score": soft_argmax_score,
                    "model_residual": residual_model,
                    "residual_threshold_metric": residual_threshold_metric,
                    "residual_reward_abs": residual_reward_abs,
                    "residual_gamma_l1": residual_gamma_l1,
                    "residual_hit_l1": residual_hit_l1,
                    "residual_backup_raw": residual_backup_raw,
                    "residual_backup_value": residual_backup_value,
                    "residual_backup_value_norm": residual_backup_value_norm,
                    "residual_reward_per_discounted_step": residual_reward_per_discounted_step,
                    "residual_gamma_relative": residual_gamma_relative,
                    "residual_tau_relative": residual_tau_relative,
                    "value_scale_task": value_scale_task,
                    "beta_row": beta_row,
                    "l_gamma_row": l_gamma_row,
                    "expected_tau_global": expected_tau_global,
                    "expected_tau_residual": expected_tau_residual,
                    "struct_hidden_prob": struct_hidden_prob,
                    "struct_hit_prob": struct_hit_prob,
                    "struct_nohit_prob": struct_nohit_prob,
                    "struct_reference_prob": struct_reference_prob,
                    "struct_hidden_norm": struct_hidden_norm,
                    "struct_hidden_bits": struct_hidden_bits,
                    "struct_hidden_distinct": struct_hidden_distinct,
                    "struct_hidden_distinct_bits": struct_hidden_distinct_bits,
                    "struct_distinct_argmax_state": struct_distinct_argmax,
                    "struct_distinct_argmax_coord": (
                        idx_to_coord[struct_distinct_argmax] if struct_distinct_argmax is not None else None
                    ),
                    "struct_distinct_argmax_score": struct_distinct_argmax_score,
                    "struct_distinct_scores": json.dumps(struct_distinct_scores, sort_keys=True),
                    "residual_hidden_mass": residual_hidden_mass,
                    "residual_hidden_gamma_mass": residual_hidden_gamma_mass,
                    "residual_argmax_state": residual_argmax,
                    "residual_argmax_coord": idx_to_coord[residual_argmax] if residual_argmax is not None else None,
                    "residual_argmax_prob": residual_argmax_prob,
                    "reward": first_hit.reward,
                }
            )

    valid_edge_rows = [row for row in edge_rows if bool(row["edge_valid"])]
    valid_struct_prob = [float(row["struct_hidden_prob"]) for row in valid_edge_rows]
    valid_struct_bits = [float(row["struct_hidden_bits"]) for row in valid_edge_rows]
    valid_struct_distinct = [float(row["struct_hidden_distinct"]) for row in valid_edge_rows]
    valid_struct_distinct_bits = [
        float(row["struct_hidden_distinct_bits"]) for row in valid_edge_rows
    ]
    metadata: Dict[str, object] = {
        "option_set": "first_boundary_targeted",
        "local_horizon": local_horizon,
        "hidden_threshold": hidden_threshold,
        "option_pair_count": len(edge_rows),
        "n_edges_valid": sum(1 for row in edge_rows if row["edge_valid"]),
        "hidden_mass_total": float(sum(float(row["hidden_mass"]) for row in edge_rows)),
        "hidden_mass_max": float(max((float(row["hidden_mass"]) for row in edge_rows), default=0.0)),
        "invalid_hidden_count": sum(
            1 for row in edge_rows if float(row["hidden_mass"]) > hidden_threshold
        ),
        "soft_cost_all_total": float(sum(float(row["soft_cost"]) for row in edge_rows)),
        "soft_cost_valid_total": float(
            sum(float(row["soft_cost"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "soft_cost_max": float(max((float(row["soft_cost"]) for row in edge_rows), default=0.0)),
        "soft_over_threshold_count": sum(
            1 for row in edge_rows if bool(row["edge_valid"]) and float(row["soft_cost"]) > soft_threshold
        ),
        "model_residual_valid_total": float(
            sum(float(row["model_residual"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "model_residual_max": float(max((float(row["model_residual"]) for row in edge_rows), default=0.0)),
        "residual_threshold_metric_valid_total": float(
            sum(float(row["residual_threshold_metric"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "residual_threshold_metric_max": float(
            max((float(row["residual_threshold_metric"]) for row in edge_rows), default=0.0)
        ),
        "residual_backup_value_norm_valid_total": float(
            sum(float(row["residual_backup_value_norm"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "residual_backup_value_norm_max": float(
            max((float(row["residual_backup_value_norm"]) for row in edge_rows), default=0.0)
        ),
        "struct_hidden_prob_valid_total": float(sum(valid_struct_prob)),
        "struct_hidden_prob_max": float(max((float(row["struct_hidden_prob"]) for row in edge_rows), default=0.0)),
        "struct_hidden_prob_cvar95": tail_cvar(valid_struct_prob),
        "struct_hidden_bits_valid_total": float(sum(valid_struct_bits)),
        "struct_hidden_bits_max": float(max((float(row["struct_hidden_bits"]) for row in edge_rows), default=0.0)),
        "struct_hidden_bits_cvar95": tail_cvar(valid_struct_bits),
        "struct_hidden_distinct_valid_total": float(sum(valid_struct_distinct)),
        "struct_hidden_distinct_max": float(
            max((float(row["struct_hidden_distinct"]) for row in edge_rows), default=0.0)
        ),
        "struct_hidden_distinct_cvar95": tail_cvar(valid_struct_distinct),
        "struct_hidden_distinct_bits_valid_total": float(sum(valid_struct_distinct_bits)),
        "struct_hidden_distinct_bits_max": float(
            max((float(row["struct_hidden_distinct_bits"]) for row in edge_rows), default=0.0)
        ),
        "struct_hidden_distinct_bits_cvar95": tail_cvar(valid_struct_distinct_bits),
        "struct_nohit_prob_max": float(max((float(row["struct_nohit_prob"]) for row in edge_rows), default=0.0)),
        "beta_global": float(max((float(row["beta_row"]) for row in edge_rows), default=0.0)),
        "l_gamma_row_max": float(max((float(row["l_gamma_row"]) for row in edge_rows), default=0.0)),
        "residual_hidden_mass_max": float(
            max((float(row["residual_hidden_mass"]) for row in edge_rows), default=0.0)
        ),
        "residual_over_threshold_count": sum(
            1
            for row in edge_rows
            if bool(row["edge_valid"]) and float(row["residual_threshold_metric"]) > residual_threshold
        ),
    }
    policies: Dict[str, object] = {
        "pair": pair_policies,
        "target": target_policies,
    }
    return reductions, valid_actions, policies, metadata, edge_rows


def choose_hidden_split(edge_rows: Sequence[Mapping[str, object]], hidden_threshold: float) -> Tuple[int | None, float]:
    mass_by_state: Dict[int, float] = defaultdict(float)
    for row in edge_rows:
        hidden_state = row["hidden_argmax_state"]
        hidden_mass = float(row["hidden_mass"])
        hidden_argmax_prob = float(row["hidden_argmax_prob"])
        if hidden_state is None or hidden_mass <= hidden_threshold:
            continue
        mass_by_state[int(hidden_state)] += hidden_argmax_prob
    if not mass_by_state:
        return None, 0.0
    state, score = max(mass_by_state.items(), key=lambda item: item[1])
    return int(state), float(score)


def choose_soft_split(edge_rows: Sequence[Mapping[str, object]], soft_threshold: float) -> Tuple[int | None, float]:
    score_by_state: Dict[int, float] = defaultdict(float)
    for row in edge_rows:
        soft_state = row["soft_argmax_state"]
        soft_cost = float(row["soft_cost"])
        soft_score = float(row["soft_argmax_score"])
        if soft_state is None or not bool(row["edge_valid"]) or soft_cost <= soft_threshold:
            continue
        score_by_state[int(soft_state)] += soft_score
    if not score_by_state:
        return None, 0.0
    state, score = max(score_by_state.items(), key=lambda item: item[1])
    return int(state), float(score)


def choose_residual_split(edge_rows: Sequence[Mapping[str, object]], residual_threshold: float) -> Tuple[int | None, float]:
    score_by_state: Dict[int, float] = defaultdict(float)
    for row in edge_rows:
        residual_state = row["residual_argmax_state"]
        residual_metric = float(row["residual_threshold_metric"])
        residual_prob = float(row["residual_argmax_prob"])
        if residual_state is None or not bool(row["edge_valid"]) or residual_metric <= residual_threshold:
            continue
        score_by_state[int(residual_state)] += residual_metric * residual_prob
    if not score_by_state:
        return None, 0.0
    state, score = max(score_by_state.items(), key=lambda item: item[1])
    return int(state), float(score)


def choose_mdl_struct_split(
    edge_rows: Sequence[Mapping[str, object]],
    n_states: int,
    n_boundary: int,
    node_cost_weight: float,
    edge_cost_weight: float,
    exposure_bit_weight: float,
    min_gain: float,
) -> Tuple[int | None, float, float, float]:
    benefit_by_state: Dict[int, float] = defaultdict(float)
    for row in edge_rows:
        if not bool(row["edge_valid"]):
            continue
        raw_scores = row.get("struct_distinct_scores", "{}")
        try:
            scores = json.loads(str(raw_scores))
        except json.JSONDecodeError:
            scores = {}
        edge_exposure = float(row.get("struct_hidden_distinct", 0.0))
        for state, score in scores.items():
            benefit_by_state[int(state)] += exposure_bit_weight * edge_exposure * float(score)

    node_cost = node_cost_weight * float(np.log2(max(2, n_states)))
    added_pair_edge_cost = edge_cost_weight * float(2 * max(1, n_boundary))
    split_cost = node_cost + added_pair_edge_cost
    if not benefit_by_state:
        return None, 0.0, 0.0, split_cost

    state, benefit = max(benefit_by_state.items(), key=lambda item: item[1])
    gain = float(benefit - split_cost)
    if gain <= min_gain:
        return None, gain, float(benefit), split_cost
    return int(state), gain, float(benefit), split_cost


def ranked_struct_proposal_states(edge_rows: Sequence[Mapping[str, object]]) -> List[Tuple[int, float]]:
    benefit_by_state: Dict[int, float] = defaultdict(float)
    for row in edge_rows:
        if not bool(row["edge_valid"]):
            continue
        raw_scores = row.get("struct_distinct_scores", "{}")
        try:
            scores = json.loads(str(raw_scores))
        except json.JSONDecodeError:
            scores = {}
        edge_exposure = float(row.get("struct_hidden_distinct", 0.0))
        for state, score in scores.items():
            benefit_by_state[int(state)] += edge_exposure * float(score)
    return sorted(benefit_by_state.items(), key=lambda item: item[1], reverse=True)


def mdl_code_length(
    row: Mapping[str, object],
    edge_rows: Sequence[Mapping[str, object]],
    struct_kind: str,
    option_pair_bit_cost: float,
    policy_tv_bit_cost: float,
    policy_region_bit_cost: float,
    model_residual_bit_cost: float,
    include_edge_encoding: bool,
) -> float:
    n_boundary = int(row["n_boundary"])
    n_edges_valid = int(row["n_edges_valid"])
    if struct_kind == "occupancy_distinct":
        struct_bits = float(row.get("occupancy_struct_hidden_distinct", 0.0))
    elif struct_kind == "occupancy_distinct_bits":
        struct_bits = float(row.get("occupancy_struct_hidden_distinct_bits", 0.0))
    elif struct_kind == "distinct_bits":
        struct_bits = float(row.get("struct_hidden_distinct_bits_valid_total", 0.0))
    elif struct_kind == "hidden_bits":
        struct_bits = float(row.get("struct_hidden_bits_valid_total", 0.0))
    else:
        struct_bits = float(row.get("struct_hidden_distinct_valid_total", 0.0))

    edge_bits = edge_code_bits(n_boundary, n_edges_valid) if include_edge_encoding else 0.0
    return (
        boundary_code_bits(int(row["n_states"]), n_boundary)
        + edge_bits
        + option_pair_bit_cost * float(row["n_pair_options"])
        + policy_tv_bit_cost * float(row["target_policy_tv_total"])
        + policy_region_bit_cost * float(row["target_policy_regions_total"])
        + model_residual_bit_cost * float(row["model_residual_valid_total"])
        + struct_bits
    )


def rate_code_length(
    row: Mapping[str, object],
    option_pair_bit_cost: float,
    policy_tv_bit_cost: float,
    policy_region_bit_cost: float,
    include_edge_encoding: bool,
) -> float:
    n_boundary = int(row["n_boundary"])
    n_edges_valid = int(row["n_edges_valid"])
    edge_bits = edge_code_bits(n_boundary, n_edges_valid) if include_edge_encoding else 0.0
    return (
        boundary_code_bits(int(row["n_states"]), n_boundary)
        + edge_bits
        + option_pair_bit_cost * float(row["n_pair_options"])
        + policy_tv_bit_cost * float(row["target_policy_tv_total"])
        + policy_region_bit_cost * float(row["target_policy_regions_total"])
    )


def structural_distortion(row: Mapping[str, object], struct_kind: str) -> float:
    if struct_kind == "occupancy_distinct_bits":
        return float(row.get("occupancy_struct_hidden_distinct_bits", 0.0))
    if struct_kind == "distinct":
        return float(row.get("struct_hidden_distinct_valid_total", 0.0))
    if struct_kind == "distinct_bits":
        return float(row.get("struct_hidden_distinct_bits_valid_total", 0.0))
    if struct_kind == "hidden_bits":
        return float(row.get("struct_hidden_bits_valid_total", 0.0))
    if struct_kind == "audit_prob_max":
        return float(row.get("struct_hidden_prob_max", 0.0))
    if struct_kind == "audit_prob_cvar95":
        return float(row.get("struct_hidden_prob_cvar95", 0.0))
    if struct_kind == "audit_distinct_max":
        return float(row.get("struct_hidden_distinct_max", 0.0))
    if struct_kind == "audit_distinct_cvar95":
        return float(row.get("struct_hidden_distinct_cvar95", 0.0))
    if struct_kind == "audit_distinct_bits_max":
        return float(row.get("struct_hidden_distinct_bits_max", 0.0))
    if struct_kind == "audit_distinct_bits_cvar95":
        return float(row.get("struct_hidden_distinct_bits_cvar95", 0.0))
    return float(row.get("occupancy_struct_hidden_distinct", 0.0))


def finite_budget_violation(value: float, budget: float) -> float:
    if not np.isfinite(budget):
        return 0.0
    return max(0.0, float(value) - float(budget))


def rate_distortion_components(
    row: Mapping[str, object],
    rate_bits: float,
    struct_kind: str,
    struct_budget: float,
    audit_kind: str,
    audit_budget: float,
    model_budget: float,
    value_budget: float,
    start_gap_budget: float,
    lambda_struct: float,
    lambda_audit: float,
    lambda_model: float,
    lambda_value: float,
    lambda_start_gap: float,
) -> Dict[str, float]:
    struct = structural_distortion(row, struct_kind)
    audit = 0.0 if audit_kind == "none" else structural_distortion(row, audit_kind)
    model = float(row.get("occupancy_model_residual", 0.0))
    value = float(row.get("value_gap_max", 0.0))
    start_gap = float(row.get("start_gap", 0.0))
    violation = (
        finite_budget_violation(struct, struct_budget)
        + finite_budget_violation(audit, audit_budget)
        + finite_budget_violation(model, model_budget)
        + finite_budget_violation(value, value_budget)
        + finite_budget_violation(start_gap, start_gap_budget)
    )
    objective = (
        rate_bits
        + lambda_struct * struct
        + lambda_audit * audit
        + lambda_model * model
        + lambda_value * value
        + lambda_start_gap * start_gap
    )
    return {
        "rate_bits": float(rate_bits),
        "struct": float(struct),
        "audit": float(audit),
        "model": float(model),
        "value": float(value),
        "start_gap": float(start_gap),
        "violation": float(violation),
        "objective": float(objective),
    }


def _struct_score_value(score: float, kind: str) -> float:
    if "bits" in kind:
        return structural_bits(normalize_structural_prob(score, p_ref_upper=0.0))
    return float(score)


def rd_operator_candidate_scores(
    row: Mapping[str, object],
    edge_rows: Sequence[Mapping[str, object]],
    boundary: Sequence[int],
    rd_struct_kind: str,
    rd_struct_budget: float,
    rd_audit_kind: str,
    rd_audit_budget: float,
    rd_model_budget: float,
    rd_value_budget: float,
    rd_start_gap_budget: float,
    rd_lambda_struct: float,
    rd_lambda_audit: float,
    rd_lambda_model: float,
    rd_lambda_value: float,
    rd_lambda_start_gap: float,
    option_pair_bit_cost: float,
    policy_tv_bit_cost: float,
    policy_region_bit_cost: float,
    include_edge_encoding: bool,
) -> Tuple[List[Dict[str, object]], Dict[str, float]]:
    """Cheap split surrogate from current edge exposure.

    This is the first explicit "operator" approximation to exact RD search:
    it scores a state by how much current policy-weighted and audit-tail
    hidden-boundary exposure would be resolved if that state became a vertex.
    """

    base_rate_bits = rate_code_length(
        row,
        option_pair_bit_cost=option_pair_bit_cost,
        policy_tv_bit_cost=policy_tv_bit_cost,
        policy_region_bit_cost=policy_region_bit_cost,
        include_edge_encoding=include_edge_encoding,
    )
    base = rate_distortion_components(
        row=row,
        rate_bits=base_rate_bits,
        struct_kind=rd_struct_kind,
        struct_budget=rd_struct_budget,
        audit_kind=rd_audit_kind,
        audit_budget=rd_audit_budget,
        model_budget=rd_model_budget,
        value_budget=rd_value_budget,
        start_gap_budget=rd_start_gap_budget,
        lambda_struct=rd_lambda_struct,
        lambda_audit=rd_lambda_audit,
        lambda_model=rd_lambda_model,
        lambda_value=rd_lambda_value,
        lambda_start_gap=rd_lambda_start_gap,
    )
    boundary_set = set(int(state) for state in boundary)
    n_states = int(row["n_states"])
    n_boundary = int(row["n_boundary"])
    struct_violation = finite_budget_violation(base["struct"], rd_struct_budget)
    audit_violation = finite_budget_violation(base["audit"], rd_audit_budget)
    value_violation = finite_budget_violation(base["value"], rd_value_budget)
    model_violation = finite_budget_violation(base["model"], rd_model_budget)
    start_gap_violation = finite_budget_violation(base["start_gap"], rd_start_gap_budget)
    base_violation = (
        struct_violation
        + audit_violation
        + value_violation
        + model_violation
        + start_gap_violation
    )
    valid_exposures = [
        float(edge_row.get("struct_hidden_distinct", 0.0))
        for edge_row in edge_rows
        if bool(edge_row.get("edge_valid", False))
    ]
    if valid_exposures:
        tail_cut = float(np.percentile(np.asarray(valid_exposures, dtype=float), 95.0))
    else:
        tail_cut = float("inf")

    candidate_scores: Dict[int, Dict[str, float]] = defaultdict(
        lambda: {
            "occupancy_struct_benefit": 0.0,
            "audit_tail_benefit": 0.0,
            "unweighted_struct_benefit": 0.0,
            "model_benefit": 0.0,
        }
    )
    for edge_row in edge_rows:
        if not bool(edge_row.get("edge_valid", False)):
            continue
        try:
            scores = json.loads(str(edge_row.get("struct_distinct_scores", "{}")))
        except json.JSONDecodeError:
            scores = {}
        if not scores:
            continue
        occupancy = float(edge_row.get("policy_occupancy", 0.0))
        exposure = float(edge_row.get("struct_hidden_distinct", 0.0))
        tail_weight = 1.0 if exposure >= tail_cut and exposure > 1e-12 else 0.0
        model_residual = float(edge_row.get("model_residual", 0.0))
        for raw_state, raw_score in scores.items():
            state = int(raw_state)
            if state in boundary_set:
                continue
            score = _struct_score_value(float(raw_score), rd_struct_kind)
            audit_score = _struct_score_value(float(raw_score), rd_audit_kind)
            candidate_scores[state]["occupancy_struct_benefit"] += occupancy * score
            candidate_scores[state]["audit_tail_benefit"] += tail_weight * audit_score
            candidate_scores[state]["unweighted_struct_benefit"] += score
            candidate_scores[state]["model_benefit"] += tail_weight * model_residual * float(raw_score)

    boundary_rate_delta = boundary_code_bits(n_states, n_boundary + 1) - boundary_code_bits(n_states, n_boundary)
    edge_rate_delta = edge_code_bits(n_boundary + 1, int(row["n_edges_valid"]) + 2 * n_boundary) - edge_code_bits(
        n_boundary,
        int(row["n_edges_valid"]),
    ) if include_edge_encoding else 0.0
    option_rate_delta = option_pair_bit_cost * float(2 * max(1, n_boundary))
    approx_rate_delta = boundary_rate_delta + edge_rate_delta + option_rate_delta

    struct_weight = 1.0 if struct_violation > 1e-12 else max(0.0, rd_lambda_struct)
    audit_weight = 1.0 if audit_violation > 1e-12 else max(0.0, rd_lambda_audit)
    model_weight = 1.0 if model_violation > 1e-12 else max(0.0, rd_lambda_model)
    if base_violation <= 1e-12 and struct_weight + audit_weight + model_weight <= 1e-12:
        struct_weight = 1.0

    diagnostics: List[Dict[str, object]] = []
    for state, parts in candidate_scores.items():
        struct_benefit = (
            parts["occupancy_struct_benefit"]
            if rd_struct_kind.startswith("occupancy")
            else parts["unweighted_struct_benefit"]
        )
        audit_benefit = parts["audit_tail_benefit"]
        model_benefit = parts["model_benefit"]
        violation_gain_proxy = (
            min(struct_violation, struct_benefit)
            + min(audit_violation, audit_benefit)
            + min(model_violation, model_benefit)
        )
        objective_gain_proxy = (
            struct_weight * struct_benefit
            + audit_weight * audit_benefit
            + model_weight * model_benefit
            - approx_rate_delta
        )
        score = violation_gain_proxy if base_violation > 1e-12 else objective_gain_proxy
        diagnostics.append(
            {
                "candidate_state": int(state),
                "operator_score": float(score),
                "violation_gain_proxy": float(violation_gain_proxy),
                "objective_gain_proxy": float(objective_gain_proxy),
                "struct_benefit_proxy": float(struct_benefit),
                "audit_benefit_proxy": float(audit_benefit),
                "model_benefit_proxy": float(model_benefit),
                "approx_rate_delta": float(approx_rate_delta),
            }
        )
    diagnostics.sort(
        key=lambda item: (
            float(item["operator_score"]),
            float(item["violation_gain_proxy"]),
            float(item["struct_benefit_proxy"]) + float(item["audit_benefit_proxy"]),
            -int(item["candidate_state"]),
        ),
        reverse=True,
    )
    return diagnostics, {
        **base,
        "base_rate_bits": float(base_rate_bits),
        "base_violation": float(base_violation),
        "approx_rate_delta": float(approx_rate_delta),
        "struct_violation": float(struct_violation),
        "audit_violation": float(audit_violation),
    }


def policy_boundary_occupancy(
    reductions: Mapping[str, BellmanKronReduction],
    policy_smdp: Mapping[int, str] | Sequence[str],
    start_pos: int,
    goal_pos: int,
) -> np.ndarray:
    n = len(policy_smdp)
    P_pi = np.zeros((n, n), dtype=float)
    for src_pos in range(n):
        if isinstance(policy_smdp, Mapping):
            action = policy_smdp.get(src_pos)
        else:
            action = policy_smdp[src_pos]
        if src_pos == goal_pos or action not in reductions:
            continue
        P_pi[src_pos, :] = reductions[action].hit_probability[src_pos]
    P_pi[goal_pos, :] = 0.0
    eye = np.eye(n, dtype=float)
    start = np.zeros(n, dtype=float)
    start[start_pos] = 1.0
    try:
        occupancy = np.linalg.solve(eye - P_pi.T, start)
    except np.linalg.LinAlgError:
        occupancy = np.linalg.lstsq(eye - P_pi.T, start, rcond=None)[0]
    return np.maximum(0.0, np.nan_to_num(occupancy, nan=0.0, posinf=0.0, neginf=0.0))


def evaluate_boundary(
    map_name: str,
    grid: GridWorld,
    boundary: Sequence[int],
    candidate_boundary: Sequence[int],
    residual_boundary: Sequence[int],
    soft_state_cost: np.ndarray,
    slip: float,
    gamma: float,
    local_horizon: float,
    hidden_threshold: float,
    soft_threshold: float,
    residual_threshold: float,
    residual_reward_weight: float,
    residual_hit_weight: float,
    residual_threshold_mode: str,
    compute_struct_distinct: bool,
    struct_mdl_node_cost_weight: float,
    struct_mdl_edge_cost_weight: float,
    struct_mdl_exposure_bit_weight: float,
    struct_mdl_min_gain: float,
    residual_kind: str,
    residual_top_fraction: float,
    soft_kind: str,
    soft_top_fraction: float,
    soft_cost_weight: float,
    candidate_kind: str,
    candidate_top_fraction: float,
    proposal_boundary: Sequence[int] | None = None,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    start = grid.symbol_states("S")[0]
    goal = grid.symbol_states("G")[0]
    boundary = sorted(set(boundary))
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    V_full = primitive_value_iteration(grid, goal_state=goal, gamma=gamma, slip=slip)
    boundary_values = V_full[np.array(boundary, dtype=int)]
    value_scale_task = max(
        1.0,
        abs(float(V_full[start])),
        float(np.percentile(np.abs(boundary_values), 95)) if len(boundary_values) > 0 else 1.0,
    )
    reductions, valid_actions, policies, metadata, edge_rows = build_first_boundary_reductions(
        grid=grid,
        boundary=boundary,
        candidate_boundary=candidate_boundary,
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
        proposal_boundary=proposal_boundary,
    )
    feasible = True
    start_gap = float("inf")
    value_gap_max = float("inf")
    start_value_smdp = float("nan")
    start_best_option = "INFEASIBLE"
    policy_smdp: Mapping[int, str] | List[str] = {}
    occupancy_by_boundary = np.zeros(len(boundary), dtype=float)
    if start in boundary_to_pos and goal in boundary_to_pos:
        try:
            V_smdp, policy_smdp = smdp_value_iteration(
                reductions,
                goal_boundary_position=boundary_to_pos[goal],
                valid_actions=valid_actions,
            )
            boundary_full = V_full[np.array(boundary)]
            value_gap = np.abs(V_smdp - boundary_full)
            nonterminal = np.ones(len(boundary), dtype=bool)
            nonterminal[boundary_to_pos[goal]] = False
            start_value_smdp = float(V_smdp[boundary_to_pos[start]])
            start_gap = float(abs(V_smdp[boundary_to_pos[start]] - V_full[start]))
            value_gap_max = float(value_gap[nonterminal].max()) if np.any(nonterminal) else 0.0
            start_best_option = policy_smdp[boundary_to_pos[start]]
            occupancy_by_boundary = policy_boundary_occupancy(
                reductions=reductions,
                policy_smdp=policy_smdp,
                start_pos=boundary_to_pos[start],
                goal_pos=boundary_to_pos[goal],
            )
        except ValueError:
            feasible = False
    else:
        feasible = False

    occupancy_struct_hidden_distinct = 0.0
    occupancy_struct_hidden_distinct_bits = 0.0
    occupancy_model_residual = 0.0
    occupancy_soft_cost = 0.0
    occupancy_mass_total = 0.0
    if feasible and len(policy_smdp) == len(boundary):
        for edge_row in edge_rows:
            src_state = int(edge_row["src_state"])
            src_pos = boundary_to_pos.get(src_state)
            if src_pos is None or src_pos >= len(policy_smdp):
                continue
            if str(edge_row["option"]) != str(policy_smdp[src_pos]) or not bool(edge_row["edge_valid"]):
                continue
            occ = float(occupancy_by_boundary[src_pos])
            edge_row["policy_occupancy"] = occ
            occupancy_mass_total += occ
            occupancy_struct_hidden_distinct += occ * float(edge_row["struct_hidden_distinct"])
            occupancy_struct_hidden_distinct_bits += occ * float(edge_row["struct_hidden_distinct_bits"])
            occupancy_model_residual += occ * float(edge_row["model_residual"])
            occupancy_soft_cost += occ * float(edge_row["soft_cost"])
    for edge_row in edge_rows:
        edge_row.setdefault("policy_occupancy", 0.0)

    pair_policy_metrics = policy_complexity_stats(grid, policies["pair"])
    target_policy_metrics = policy_complexity_stats(grid, policies["target"])
    hard_split_state, hard_split_score = choose_hidden_split(edge_rows, hidden_threshold=hidden_threshold)
    residual_split_state, residual_split_score = choose_residual_split(
        edge_rows,
        residual_threshold=residual_threshold,
    )
    (
        struct_mdl_split_state,
        struct_mdl_split_gain,
        struct_mdl_split_benefit,
        struct_mdl_split_cost,
    ) = choose_mdl_struct_split(
        edge_rows,
        n_states=grid.n_states,
        n_boundary=len(boundary),
        node_cost_weight=struct_mdl_node_cost_weight,
        edge_cost_weight=struct_mdl_edge_cost_weight,
        exposure_bit_weight=struct_mdl_exposure_bit_weight,
        min_gain=struct_mdl_min_gain,
    )
    soft_split_state, soft_split_score = choose_soft_split(edge_rows, soft_threshold=soft_threshold)
    _, idx_to_coord = grid.index_maps()
    row: Dict[str, object] = {
        "map": map_name,
        "slip": slip,
        "gamma": gamma,
        "candidate_kind": candidate_kind,
        "candidate_top_fraction": candidate_top_fraction,
        "residual_kind": residual_kind,
        "residual_top_fraction": residual_top_fraction,
        "soft_kind": soft_kind,
        "soft_top_fraction": soft_top_fraction,
        "local_horizon": local_horizon,
        "hidden_threshold": hidden_threshold,
        "soft_threshold": soft_threshold,
        "residual_threshold": residual_threshold,
        "residual_threshold_mode": residual_threshold_mode,
        "compute_struct_distinct": compute_struct_distinct,
        "struct_mdl_node_cost_weight": struct_mdl_node_cost_weight,
        "struct_mdl_edge_cost_weight": struct_mdl_edge_cost_weight,
        "struct_mdl_exposure_bit_weight": struct_mdl_exposure_bit_weight,
        "struct_mdl_min_gain": struct_mdl_min_gain,
        "residual_reward_weight": residual_reward_weight,
        "residual_hit_weight": residual_hit_weight,
        "value_scale_task": value_scale_task,
        "soft_cost_weight": soft_cost_weight,
        "n_states": grid.n_states,
        "n_boundary": len(boundary),
        "n_candidate_boundary": len(set(candidate_boundary).union(boundary)),
        "n_pair_options": int(metadata["option_pair_count"]),
        "n_edges_valid": int(metadata["n_edges_valid"]),
        "invalid_hidden_count": int(metadata["invalid_hidden_count"]),
        "hidden_mass_total": float(metadata["hidden_mass_total"]),
        "hidden_mass_max": float(metadata["hidden_mass_max"]),
        "soft_cost_all_total": float(metadata["soft_cost_all_total"]),
        "soft_cost_valid_total": float(metadata["soft_cost_valid_total"]),
        "soft_cost_max": float(metadata["soft_cost_max"]),
        "soft_over_threshold_count": int(metadata["soft_over_threshold_count"]),
        "model_residual_valid_total": float(metadata["model_residual_valid_total"]),
        "model_residual_max": float(metadata["model_residual_max"]),
        "residual_threshold_metric_valid_total": float(metadata["residual_threshold_metric_valid_total"]),
        "residual_threshold_metric_max": float(metadata["residual_threshold_metric_max"]),
        "residual_backup_value_norm_valid_total": float(metadata["residual_backup_value_norm_valid_total"]),
        "residual_backup_value_norm_max": float(metadata["residual_backup_value_norm_max"]),
        "struct_hidden_prob_valid_total": float(metadata["struct_hidden_prob_valid_total"]),
        "struct_hidden_prob_max": float(metadata["struct_hidden_prob_max"]),
        "struct_hidden_prob_cvar95": float(metadata["struct_hidden_prob_cvar95"]),
        "struct_hidden_bits_valid_total": float(metadata["struct_hidden_bits_valid_total"]),
        "struct_hidden_bits_max": float(metadata["struct_hidden_bits_max"]),
        "struct_hidden_bits_cvar95": float(metadata["struct_hidden_bits_cvar95"]),
        "struct_hidden_distinct_valid_total": float(metadata["struct_hidden_distinct_valid_total"]),
        "struct_hidden_distinct_max": float(metadata["struct_hidden_distinct_max"]),
        "struct_hidden_distinct_cvar95": float(metadata["struct_hidden_distinct_cvar95"]),
        "struct_hidden_distinct_bits_valid_total": float(metadata["struct_hidden_distinct_bits_valid_total"]),
        "struct_hidden_distinct_bits_max": float(metadata["struct_hidden_distinct_bits_max"]),
        "struct_hidden_distinct_bits_cvar95": float(metadata["struct_hidden_distinct_bits_cvar95"]),
        "struct_nohit_prob_max": float(metadata["struct_nohit_prob_max"]),
        "beta_global": float(metadata["beta_global"]),
        "l_gamma_row_max": float(metadata["l_gamma_row_max"]),
        "residual_hidden_mass_max": float(metadata["residual_hidden_mass_max"]),
        "residual_over_threshold_count": int(metadata["residual_over_threshold_count"]),
        "feasible": feasible,
        "start_value_smdp": start_value_smdp,
        "start_value_primitive": float(V_full[start]),
        "start_gap": start_gap,
        "value_gap_max": value_gap_max,
        "start_best_option": start_best_option,
        "policy_smdp_json": json.dumps(
            {str(k): str(v) for k, v in policy_smdp.items()}
            if isinstance(policy_smdp, Mapping)
            else {str(k): str(v) for k, v in enumerate(policy_smdp)}
        ),
        "boundary_states_json": json.dumps([int(state) for state in boundary]),
        "policy_tv_total": pair_policy_metrics["policy_tv_total"],
        "policy_regions_total": pair_policy_metrics["policy_regions_total"],
        "policy_tv_mean": pair_policy_metrics["policy_tv_mean"],
        "policy_regions_mean": pair_policy_metrics["policy_regions_mean"],
        "target_policy_tv_total": target_policy_metrics["policy_tv_total"],
        "target_policy_regions_total": target_policy_metrics["policy_regions_total"],
        "target_policy_tv_mean": target_policy_metrics["policy_tv_mean"],
        "target_policy_regions_mean": target_policy_metrics["policy_regions_mean"],
        "occupancy_mass_total": occupancy_mass_total,
        "occupancy_struct_hidden_distinct": occupancy_struct_hidden_distinct,
        "occupancy_struct_hidden_distinct_bits": occupancy_struct_hidden_distinct_bits,
        "occupancy_model_residual": occupancy_model_residual,
        "occupancy_soft_cost": occupancy_soft_cost,
        "hard_split_candidate_state": hard_split_state,
        "hard_split_candidate_coord": idx_to_coord[hard_split_state] if hard_split_state is not None else None,
        "hard_split_candidate_score": hard_split_score,
        "residual_split_candidate_state": residual_split_state,
        "residual_split_candidate_coord": idx_to_coord[residual_split_state] if residual_split_state is not None else None,
        "residual_split_candidate_score": residual_split_score,
        "struct_mdl_split_candidate_state": struct_mdl_split_state,
        "struct_mdl_split_candidate_coord": (
            idx_to_coord[struct_mdl_split_state] if struct_mdl_split_state is not None else None
        ),
        "struct_mdl_split_gain": struct_mdl_split_gain,
        "struct_mdl_split_benefit": struct_mdl_split_benefit,
        "struct_mdl_split_cost": struct_mdl_split_cost,
        "soft_split_candidate_state": soft_split_state,
        "soft_split_candidate_coord": idx_to_coord[soft_split_state] if soft_split_state is not None else None,
        "soft_split_candidate_score": soft_split_score,
    }
    row["description_length_proxy"] = (
        float(row["n_boundary"])
        + float(row["n_edges_valid"]) / max(1.0, float(row["n_boundary"]))
        + float(row["n_pair_options"])
        + 0.05 * float(row["n_pair_options"])
        + 0.20 * float(row["target_policy_tv_total"])
        + 0.50 * float(row["target_policy_regions_total"])
        + soft_cost_weight * float(row["soft_cost_valid_total"])
        + float(row["model_residual_valid_total"])
    )
    return row, edge_rows


def run_one(
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    gamma: float,
    candidate_kind: str,
    candidate_top_fraction: float,
    residual_kind: str,
    residual_top_fraction: float,
    soft_kind: str,
    soft_top_fraction: float,
    local_horizon: float,
    hidden_threshold: float,
    soft_threshold: float,
    residual_threshold: float,
    residual_reward_weight: float,
    residual_hit_weight: float,
    residual_threshold_mode: str,
    compute_struct_distinct: bool,
    struct_mdl_node_cost_weight: float,
    struct_mdl_edge_cost_weight: float,
    struct_mdl_exposure_bit_weight: float,
    struct_mdl_min_gain: float,
    soft_cost_weight: float,
    residual_split_policy: str,
    soft_split_policy: str,
    max_splits: int,
    proposal_kind: str = "candidate",
    exact_mdl_top_k: int = 8,
    exact_mdl_struct_kind: str = "occupancy_distinct",
    exact_mdl_option_pair_bit_cost: float = 1.0,
    exact_mdl_policy_tv_bit_cost: float = 0.2,
    exact_mdl_policy_region_bit_cost: float = 0.5,
    exact_mdl_model_residual_bit_cost: float = 1.0,
    exact_mdl_include_edge_encoding: bool = False,
    rd_top_k: int = 8,
    rd_struct_kind: str = "occupancy_distinct",
    rd_struct_budget: float = float("inf"),
    rd_audit_kind: str = "none",
    rd_audit_budget: float = float("inf"),
    rd_model_budget: float = float("inf"),
    rd_value_budget: float = float("inf"),
    rd_start_gap_budget: float = float("inf"),
    rd_lambda_struct: float = 0.0,
    rd_lambda_audit: float = 0.0,
    rd_lambda_model: float = 0.0,
    rd_lambda_value: float = 0.0,
    rd_lambda_start_gap: float = 0.0,
    rd_batch_k: int = 1,
    rd_candidate_rows: List[Dict[str, object]] | None = None,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    boundary = endpoint_boundary_states(grid)
    candidate_boundary = candidate_boundary_states(
        grid=grid,
        kind=candidate_kind,
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=candidate_top_fraction,
    )
    if residual_kind == "none":
        residual_boundary = boundary
    elif residual_kind == "hard":
        residual_boundary = candidate_boundary
    else:
        residual_boundary = candidate_boundary_states(
            grid=grid,
            kind=residual_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=residual_top_fraction,
        )
    if proposal_kind == "candidate":
        proposal_boundary = candidate_boundary
    elif proposal_kind == "residual":
        proposal_boundary = residual_boundary
    else:
        proposal_boundary = candidate_boundary_states(
            grid=grid,
            kind=proposal_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=candidate_top_fraction,
        )
    if soft_kind == "none":
        soft_state_cost = np.zeros(grid.n_states, dtype=float)
    else:
        soft_state_cost = critical_saliency(
            grid=grid,
            kind=soft_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=soft_top_fraction,
        )
    trace: List[Dict[str, object]] = []
    all_edges: List[Dict[str, object]] = []
    for step in range(max_splits + 1):
        row, edge_rows = evaluate_boundary(
            map_name=map_name,
            grid=grid,
            boundary=boundary,
            candidate_boundary=candidate_boundary,
            residual_boundary=residual_boundary,
            soft_state_cost=soft_state_cost,
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
            struct_mdl_node_cost_weight=struct_mdl_node_cost_weight,
            struct_mdl_edge_cost_weight=struct_mdl_edge_cost_weight,
            struct_mdl_exposure_bit_weight=struct_mdl_exposure_bit_weight,
            struct_mdl_min_gain=struct_mdl_min_gain,
            residual_kind=residual_kind,
            residual_top_fraction=residual_top_fraction,
            soft_kind=soft_kind,
            soft_top_fraction=soft_top_fraction,
            soft_cost_weight=soft_cost_weight,
            candidate_kind=candidate_kind,
            candidate_top_fraction=candidate_top_fraction,
            proposal_boundary=proposal_boundary,
        )
        row["step"] = step
        row["proposal_kind"] = proposal_kind
        row["n_proposal_boundary"] = len(proposal_boundary)
        for edge_row in edge_rows:
            edge_row.update({"map": map_name, "slip": slip, "step": step})
        trace.append(row)
        all_edges.extend(edge_rows)
        _, idx_to_coord = grid.index_maps()

        exact_mdl_split_state = None
        exact_mdl_split_gain = 0.0
        exact_mdl_base_bits = 0.0
        exact_mdl_candidate_bits = 0.0
        exact_mdl_candidates_evaluated = 0
        if residual_split_policy == "exact_mdl":
            ranked_candidates = [
                state for state, _ in ranked_struct_proposal_states(edge_rows) if state not in set(boundary)
            ]
            if exact_mdl_top_k > 0:
                ranked_candidates = ranked_candidates[:exact_mdl_top_k]
            exact_mdl_base_bits = mdl_code_length(
                row,
                edge_rows,
                struct_kind=exact_mdl_struct_kind,
                option_pair_bit_cost=exact_mdl_option_pair_bit_cost,
                policy_tv_bit_cost=exact_mdl_policy_tv_bit_cost,
                policy_region_bit_cost=exact_mdl_policy_region_bit_cost,
                model_residual_bit_cost=exact_mdl_model_residual_bit_cost,
                include_edge_encoding=exact_mdl_include_edge_encoding,
            )
            search_bits = math.log2(max(2, len(ranked_candidates)))
            best_candidate_bits = float("inf")
            best_gain = -float("inf")
            for candidate_state in ranked_candidates:
                trial_boundary = sorted(set(boundary).union({int(candidate_state)}))
                candidate_row, candidate_edges = evaluate_boundary(
                    map_name=map_name,
                    grid=grid,
                    boundary=trial_boundary,
                    candidate_boundary=candidate_boundary,
                    residual_boundary=residual_boundary,
                    soft_state_cost=soft_state_cost,
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
                    struct_mdl_node_cost_weight=struct_mdl_node_cost_weight,
                    struct_mdl_edge_cost_weight=struct_mdl_edge_cost_weight,
                    struct_mdl_exposure_bit_weight=struct_mdl_exposure_bit_weight,
                    struct_mdl_min_gain=struct_mdl_min_gain,
                    residual_kind=residual_kind,
                    residual_top_fraction=residual_top_fraction,
                    soft_kind=soft_kind,
                    soft_top_fraction=soft_top_fraction,
                    soft_cost_weight=soft_cost_weight,
                    candidate_kind=candidate_kind,
                    candidate_top_fraction=candidate_top_fraction,
                    proposal_boundary=proposal_boundary,
                )
                candidate_bits = mdl_code_length(
                    candidate_row,
                    candidate_edges,
                    struct_kind=exact_mdl_struct_kind,
                    option_pair_bit_cost=exact_mdl_option_pair_bit_cost,
                    policy_tv_bit_cost=exact_mdl_policy_tv_bit_cost,
                    policy_region_bit_cost=exact_mdl_policy_region_bit_cost,
                    model_residual_bit_cost=exact_mdl_model_residual_bit_cost,
                    include_edge_encoding=exact_mdl_include_edge_encoding,
                ) + search_bits
                gain = exact_mdl_base_bits - candidate_bits
                exact_mdl_candidates_evaluated += 1
                if gain > best_gain:
                    exact_mdl_split_state = int(candidate_state)
                    best_gain = float(gain)
                    best_candidate_bits = float(candidate_bits)
            if best_gain > struct_mdl_min_gain:
                exact_mdl_split_gain = best_gain
                exact_mdl_candidate_bits = best_candidate_bits
            else:
                exact_mdl_split_state = None
                exact_mdl_split_gain = best_gain if np.isfinite(best_gain) else 0.0
                exact_mdl_candidate_bits = best_candidate_bits if np.isfinite(best_candidate_bits) else 0.0
        row["exact_mdl_split_candidate_state"] = exact_mdl_split_state
        row["exact_mdl_split_candidate_coord"] = idx_to_coord[exact_mdl_split_state] if exact_mdl_split_state is not None else None
        row["exact_mdl_split_gain"] = exact_mdl_split_gain
        row["exact_mdl_base_bits"] = exact_mdl_base_bits
        row["exact_mdl_candidate_bits"] = exact_mdl_candidate_bits
        row["exact_mdl_candidates_evaluated"] = exact_mdl_candidates_evaluated

        rd_split_state = None
        rd_split_states: List[int] = []
        rd_split_gain = 0.0
        rd_base_rate_bits = 0.0
        rd_candidate_rate_bits = 0.0
        rd_base_objective = 0.0
        rd_candidate_objective = 0.0
        rd_base_violation = 0.0
        rd_candidate_violation = 0.0
        rd_violation_gain = 0.0
        rd_struct_delta = 0.0
        rd_model_delta = 0.0
        rd_audit_delta = 0.0
        rd_base_audit = 0.0
        rd_candidate_audit = 0.0
        rd_value_delta = 0.0
        rd_start_gap_delta = 0.0
        rd_struct_break_even_lambda = float("inf")
        rd_candidates_evaluated = 0
        rd_operator_candidates_scored = 0
        rd_operator_top_score = 0.0
        if residual_split_policy == "rd":
            ranked_candidates = [
                state for state, _ in ranked_struct_proposal_states(edge_rows) if state not in set(boundary)
            ]
            if rd_top_k > 0:
                ranked_candidates = ranked_candidates[:rd_top_k]

            rd_base_rate_bits = rate_code_length(
                row,
                option_pair_bit_cost=exact_mdl_option_pair_bit_cost,
                policy_tv_bit_cost=exact_mdl_policy_tv_bit_cost,
                policy_region_bit_cost=exact_mdl_policy_region_bit_cost,
                include_edge_encoding=exact_mdl_include_edge_encoding,
            )
            base_components = rate_distortion_components(
                row=row,
                rate_bits=rd_base_rate_bits,
                struct_kind=rd_struct_kind,
                struct_budget=rd_struct_budget,
                audit_kind=rd_audit_kind,
                audit_budget=rd_audit_budget,
                model_budget=rd_model_budget,
                value_budget=rd_value_budget,
                start_gap_budget=rd_start_gap_budget,
                lambda_struct=rd_lambda_struct,
                lambda_audit=rd_lambda_audit,
                lambda_model=rd_lambda_model,
                lambda_value=rd_lambda_value,
                lambda_start_gap=rd_lambda_start_gap,
            )
            rd_base_audit = base_components["audit"]
            rd_base_violation = base_components["violation"]
            rd_base_objective = base_components["objective"]
            best_key = None
            best_diag: Dict[str, object] | None = None
            single_diags: List[Dict[str, object]] = []
            all_diags: List[Dict[str, object]] = []

            def evaluate_rd_candidate(candidate_states: Sequence[int], mode: str, rank: int) -> Dict[str, object]:
                candidate_states_sorted = sorted({int(state) for state in candidate_states})
                trial_boundary = sorted(set(boundary).union(candidate_states_sorted))
                candidate_row, _candidate_edges = evaluate_boundary(
                    map_name=map_name,
                    grid=grid,
                    boundary=trial_boundary,
                    candidate_boundary=candidate_boundary,
                    residual_boundary=residual_boundary,
                    soft_state_cost=soft_state_cost,
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
                    struct_mdl_node_cost_weight=struct_mdl_node_cost_weight,
                    struct_mdl_edge_cost_weight=struct_mdl_edge_cost_weight,
                    struct_mdl_exposure_bit_weight=struct_mdl_exposure_bit_weight,
                    struct_mdl_min_gain=struct_mdl_min_gain,
                    residual_kind=residual_kind,
                    residual_top_fraction=residual_top_fraction,
                    soft_kind=soft_kind,
                    soft_top_fraction=soft_top_fraction,
                    soft_cost_weight=soft_cost_weight,
                    candidate_kind=candidate_kind,
                    candidate_top_fraction=candidate_top_fraction,
                    proposal_boundary=proposal_boundary,
                )
                batch_size = len(candidate_states_sorted)
                candidate_rate_bits = rate_code_length(
                    candidate_row,
                    option_pair_bit_cost=exact_mdl_option_pair_bit_cost,
                    policy_tv_bit_cost=exact_mdl_policy_tv_bit_cost,
                    policy_region_bit_cost=exact_mdl_policy_region_bit_cost,
                    include_edge_encoding=exact_mdl_include_edge_encoding,
                ) + selection_code_bits(len(ranked_candidates), batch_size)
                candidate_components = rate_distortion_components(
                    row=candidate_row,
                    rate_bits=candidate_rate_bits,
                    struct_kind=rd_struct_kind,
                    struct_budget=rd_struct_budget,
                    audit_kind=rd_audit_kind,
                    audit_budget=rd_audit_budget,
                    model_budget=rd_model_budget,
                    value_budget=rd_value_budget,
                    start_gap_budget=rd_start_gap_budget,
                    lambda_struct=rd_lambda_struct,
                    lambda_audit=rd_lambda_audit,
                    lambda_model=rd_lambda_model,
                    lambda_value=rd_lambda_value,
                    lambda_start_gap=rd_lambda_start_gap,
                )
                gain = base_components["objective"] - candidate_components["objective"]
                violation_gain = base_components["violation"] - candidate_components["violation"]
                struct_delta = base_components["struct"] - candidate_components["struct"]
                audit_delta = base_components["audit"] - candidate_components["audit"]
                model_delta = base_components["model"] - candidate_components["model"]
                value_delta = base_components["value"] - candidate_components["value"]
                start_gap_delta = base_components["start_gap"] - candidate_components["start_gap"]
                rate_delta = candidate_rate_bits - rd_base_rate_bits
                break_even = rate_delta / struct_delta if struct_delta > 1e-12 else float("inf")
                return {
                    "map": map_name,
                    "slip": slip,
                    "step": step,
                    "mode": mode,
                    "rank": rank,
                    "n_boundary": len(boundary),
                    "candidate_batch_size": batch_size,
                    "candidate_states": candidate_states_sorted,
                    "candidate_state": candidate_states_sorted[0] if batch_size == 1 else "",
                    "candidate_coords": [idx_to_coord[state] for state in candidate_states_sorted],
                    "base_rate_bits": rd_base_rate_bits,
                    "candidate_rate_bits": candidate_rate_bits,
                    "rate_delta": rate_delta,
                    "base_objective": base_components["objective"],
                    "candidate_objective": candidate_components["objective"],
                    "gain": gain,
                    "base_violation": base_components["violation"],
                    "candidate_violation": candidate_components["violation"],
                    "violation_gain": violation_gain,
                    "base_struct": base_components["struct"],
                    "candidate_struct": candidate_components["struct"],
                    "struct_delta": struct_delta,
                    "base_audit": base_components["audit"],
                    "candidate_audit": candidate_components["audit"],
                    "audit_delta": audit_delta,
                    "base_model": base_components["model"],
                    "candidate_model": candidate_components["model"],
                    "model_delta": model_delta,
                    "base_value": base_components["value"],
                    "candidate_value": candidate_components["value"],
                    "value_delta": value_delta,
                    "base_start_gap": base_components["start_gap"],
                    "candidate_start_gap": candidate_components["start_gap"],
                    "start_gap_delta": start_gap_delta,
                    "struct_break_even_lambda": break_even,
                    "selected": False,
                }

            for rank, candidate_state in enumerate(ranked_candidates, start=1):
                diag = evaluate_rd_candidate([int(candidate_state)], mode="single", rank=rank)
                single_diags.append(diag)
                all_diags.append(diag)

            def rd_sort_key(diag: Mapping[str, object]) -> Tuple[float, float, float, float]:
                if rd_base_violation > 1e-12:
                    return (
                        float(diag["violation_gain"]),
                        float(diag["gain"]),
                        float(diag["struct_delta"]) + float(diag["audit_delta"]),
                        -float(diag["candidate_rate_bits"]),
                    )
                return (
                    float(diag["gain"]),
                    float(diag["struct_delta"]) + float(diag["audit_delta"]),
                    float(diag["model_delta"]) + float(diag["value_delta"]) + float(diag["start_gap_delta"]),
                    -float(diag["candidate_rate_bits"]),
                )

            ranked_single_diags = sorted(single_diags, key=rd_sort_key, reverse=True)
            for batch_size in range(2, min(max(1, rd_batch_k), len(ranked_single_diags)) + 1):
                batch_states = [
                    int(state)
                    for diag in ranked_single_diags[:batch_size]
                    for state in diag["candidate_states"]
                ]
                diag = evaluate_rd_candidate(batch_states, mode="batch_prefix", rank=batch_size)
                all_diags.append(diag)

            for diag in all_diags:
                key = rd_sort_key(diag)
                if best_key is None or key > best_key:
                    best_key = key
                    best_diag = diag

            rd_candidates_evaluated = len(all_diags)
            if best_diag is not None:
                accept = (
                    rd_base_violation > 1e-12 and float(best_diag["violation_gain"]) > struct_mdl_min_gain
                ) or (
                    rd_base_violation <= 1e-12 and float(best_diag["gain"]) > struct_mdl_min_gain
                )
                if accept:
                    rd_split_states = [int(state) for state in best_diag["candidate_states"]]
                    rd_split_state = rd_split_states[0] if rd_split_states else None
                    best_diag["selected"] = True
                rd_split_gain = float(best_diag["gain"])
                rd_candidate_rate_bits = float(best_diag["candidate_rate_bits"])
                rd_candidate_objective = float(best_diag["candidate_objective"])
                rd_candidate_violation = float(best_diag["candidate_violation"])
                rd_violation_gain = float(best_diag["violation_gain"])
                rd_struct_delta = float(best_diag["struct_delta"])
                rd_audit_delta = float(best_diag["audit_delta"])
                rd_candidate_audit = float(best_diag["candidate_audit"])
                rd_model_delta = float(best_diag["model_delta"])
                rd_value_delta = float(best_diag["value_delta"])
                rd_start_gap_delta = float(best_diag["start_gap_delta"])
                rd_struct_break_even_lambda = float(best_diag["struct_break_even_lambda"])
            if rd_candidate_rows is not None:
                rd_candidate_rows.extend(all_diags)
        if residual_split_policy == "rd_surrogate":
            operator_diags, operator_base = rd_operator_candidate_scores(
                row=row,
                edge_rows=edge_rows,
                boundary=boundary,
                rd_struct_kind=rd_struct_kind,
                rd_struct_budget=rd_struct_budget,
                rd_audit_kind=rd_audit_kind,
                rd_audit_budget=rd_audit_budget,
                rd_model_budget=rd_model_budget,
                rd_value_budget=rd_value_budget,
                rd_start_gap_budget=rd_start_gap_budget,
                rd_lambda_struct=rd_lambda_struct,
                rd_lambda_audit=rd_lambda_audit,
                rd_lambda_model=rd_lambda_model,
                rd_lambda_value=rd_lambda_value,
                rd_lambda_start_gap=rd_lambda_start_gap,
                option_pair_bit_cost=exact_mdl_option_pair_bit_cost,
                policy_tv_bit_cost=exact_mdl_policy_tv_bit_cost,
                policy_region_bit_cost=exact_mdl_policy_region_bit_cost,
                include_edge_encoding=exact_mdl_include_edge_encoding,
            )
            if rd_top_k > 0:
                operator_diags = operator_diags[:rd_top_k]
            rd_operator_candidates_scored = len(operator_diags)
            rd_base_rate_bits = float(operator_base["base_rate_bits"])
            rd_base_objective = float(operator_base["objective"])
            rd_base_violation = float(operator_base["base_violation"])
            rd_base_audit = float(operator_base["audit"])
            if operator_diags:
                rd_operator_top_score = float(operator_diags[0]["operator_score"])
                positive = [
                    diag
                    for diag in operator_diags
                    if float(diag["operator_score"]) > struct_mdl_min_gain
                    or (
                        rd_base_violation > 1e-12
                        and float(diag["violation_gain_proxy"]) > struct_mdl_min_gain
                    )
                ]
                batch_size = min(max(1, rd_batch_k), len(positive))
                selected_diags = positive[:batch_size]
                if selected_diags:
                    rd_split_states = [int(diag["candidate_state"]) for diag in selected_diags]
                    rd_split_state = rd_split_states[0]
                    rd_split_gain = float(sum(float(diag["operator_score"]) for diag in selected_diags))
                    rd_violation_gain = float(
                        sum(float(diag["violation_gain_proxy"]) for diag in selected_diags)
                    )
                    rd_struct_delta = float(
                        sum(float(diag["struct_benefit_proxy"]) for diag in selected_diags)
                    )
                    rd_audit_delta = float(
                        sum(float(diag["audit_benefit_proxy"]) for diag in selected_diags)
                    )
                    rd_model_delta = float(
                        sum(float(diag["model_benefit_proxy"]) for diag in selected_diags)
                    )
                    rd_candidate_rate_bits = rd_base_rate_bits + float(
                        sum(float(diag["approx_rate_delta"]) for diag in selected_diags)
                    )
                    rd_candidate_objective = rd_base_objective - rd_split_gain
                    rd_candidate_violation = max(0.0, rd_base_violation - rd_violation_gain)
                    rd_candidate_audit = max(0.0, rd_base_audit - rd_audit_delta)
                    if rd_struct_delta > 1e-12:
                        rd_struct_break_even_lambda = (
                            rd_candidate_rate_bits - rd_base_rate_bits
                        ) / rd_struct_delta
                    for diag in selected_diags:
                        diag["selected"] = True
            if rd_candidate_rows is not None:
                for rank, diag in enumerate(operator_diags, start=1):
                    out_diag = {
                        "map": map_name,
                        "slip": slip,
                        "step": step,
                        "mode": "operator_surrogate",
                        "rank": rank,
                        "n_boundary": len(boundary),
                        "candidate_batch_size": 1,
                        "candidate_states": [int(diag["candidate_state"])],
                        "candidate_state": int(diag["candidate_state"]),
                        "candidate_coords": [idx_to_coord[int(diag["candidate_state"])]],
                        "base_rate_bits": rd_base_rate_bits,
                        "candidate_rate_bits": rd_base_rate_bits + float(diag["approx_rate_delta"]),
                        "rate_delta": float(diag["approx_rate_delta"]),
                        "base_objective": rd_base_objective,
                        "candidate_objective": rd_base_objective - float(diag["operator_score"]),
                        "gain": float(diag["operator_score"]),
                        "base_violation": rd_base_violation,
                        "candidate_violation": max(
                            0.0,
                            rd_base_violation - float(diag["violation_gain_proxy"]),
                        ),
                        "violation_gain": float(diag["violation_gain_proxy"]),
                        "base_struct": float(operator_base["struct"]),
                        "candidate_struct": max(
                            0.0,
                            float(operator_base["struct"]) - float(diag["struct_benefit_proxy"]),
                        ),
                        "struct_delta": float(diag["struct_benefit_proxy"]),
                        "base_audit": rd_base_audit,
                        "candidate_audit": max(
                            0.0,
                            rd_base_audit - float(diag["audit_benefit_proxy"]),
                        ),
                        "audit_delta": float(diag["audit_benefit_proxy"]),
                        "base_model": float(operator_base["model"]),
                        "candidate_model": max(
                            0.0,
                            float(operator_base["model"]) - float(diag["model_benefit_proxy"]),
                        ),
                        "model_delta": float(diag["model_benefit_proxy"]),
                        "base_value": float(operator_base["value"]),
                        "candidate_value": float(operator_base["value"]),
                        "value_delta": 0.0,
                        "base_start_gap": float(operator_base["start_gap"]),
                        "candidate_start_gap": float(operator_base["start_gap"]),
                        "start_gap_delta": 0.0,
                        "struct_break_even_lambda": rd_struct_break_even_lambda,
                        "selected": bool(diag.get("selected", False)),
                    }
                    rd_candidate_rows.append(out_diag)
        row["rd_split_candidate_state"] = rd_split_state
        row["rd_split_candidate_coord"] = idx_to_coord[rd_split_state] if rd_split_state is not None else None
        row["rd_split_candidate_states"] = rd_split_states
        row["rd_split_candidate_coords"] = [idx_to_coord[state] for state in rd_split_states]
        row["rd_split_batch_size"] = len(rd_split_states)
        row["rd_split_gain"] = rd_split_gain
        row["rd_base_rate_bits"] = rd_base_rate_bits
        row["rd_candidate_rate_bits"] = rd_candidate_rate_bits
        row["rd_base_objective"] = rd_base_objective
        row["rd_candidate_objective"] = rd_candidate_objective
        row["rd_base_violation"] = rd_base_violation
        row["rd_candidate_violation"] = rd_candidate_violation
        row["rd_violation_gain"] = rd_violation_gain
        row["rd_struct_delta"] = rd_struct_delta
        row["rd_base_audit"] = rd_base_audit
        row["rd_candidate_audit"] = rd_candidate_audit
        row["rd_audit_delta"] = rd_audit_delta
        row["rd_model_delta"] = rd_model_delta
        row["rd_value_delta"] = rd_value_delta
        row["rd_start_gap_delta"] = rd_start_gap_delta
        row["rd_struct_break_even_lambda"] = rd_struct_break_even_lambda
        row["rd_candidates_evaluated"] = rd_candidates_evaluated
        row["rd_operator_candidates_scored"] = rd_operator_candidates_scored
        row["rd_operator_top_score"] = rd_operator_top_score

        split_state = row["hard_split_candidate_state"]
        split_states: List[int] = [int(split_state)] if split_state is not None else []
        split_source = "hard_hidden"
        split_score = row["hard_split_candidate_score"]
        if split_state is None and residual_split_policy == "threshold":
            split_state = row["residual_split_candidate_state"]
            split_states = [int(split_state)] if split_state is not None else []
            split_score = row["residual_split_candidate_score"]
            split_source = f"residual_{residual_threshold_mode}"
        if split_state is None and residual_split_policy == "mdl":
            split_state = row["struct_mdl_split_candidate_state"]
            split_states = [int(split_state)] if split_state is not None else []
            split_score = row["struct_mdl_split_gain"]
            split_source = "residual_mdl"
        if split_state is None and residual_split_policy == "exact_mdl":
            split_state = row["exact_mdl_split_candidate_state"]
            split_states = [int(split_state)] if split_state is not None else []
            split_score = row["exact_mdl_split_gain"]
            split_source = "residual_exact_mdl"
        if split_state is None and residual_split_policy == "rd":
            split_state = row["rd_split_candidate_state"]
            split_states = [int(state) for state in row["rd_split_candidate_states"]]
            split_score = row["rd_violation_gain"] if row["rd_base_violation"] > 1e-12 else row["rd_split_gain"]
            split_source = "residual_rate_distortion"
        if split_state is None and residual_split_policy == "rd_surrogate":
            split_state = row["rd_split_candidate_state"]
            split_states = [int(state) for state in row["rd_split_candidate_states"]]
            split_score = row["rd_violation_gain"] if row["rd_base_violation"] > 1e-12 else row["rd_split_gain"]
            split_source = "residual_rd_surrogate"
        if split_state is None and soft_split_policy == "threshold":
            split_state = row["soft_split_candidate_state"]
            split_states = [int(split_state)] if split_state is not None else []
            split_score = row["soft_split_candidate_score"]
            split_source = "soft_threshold"
        row["split_candidate_state"] = split_state
        row["split_candidate_states"] = split_states
        row["split_candidate_score"] = split_score if split_state is not None else 0.0
        row["split_candidate_source"] = split_source if split_state is not None else "none"
        row["split_candidate_coord"] = idx_to_coord[int(split_state)] if split_state is not None else None
        row["split_candidate_coords"] = [idx_to_coord[state] for state in split_states]
        row["split_batch_size"] = len(split_states)
        if split_state is None:
            row["stop_reason"] = "hybrid_threshold"
            break
        if step >= max_splits:
            row["stop_reason"] = "max_splits"
            break
        row["stop_reason"] = "continue"
        boundary = sorted(set(boundary).union(split_states))

    if "stop_reason" not in trace[-1]:
        trace[-1]["stop_reason"] = "max_splits"
    return trace, all_edges


def markdown_table(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.4g}" if np.isfinite(val) and abs(val) >= 1e-9 else str(val))
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(rows: Sequence[Dict[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    final_rows: List[Dict[str, object]] = []
    for key in sorted({(row["map"], row["slip"]) for row in rows}):
        run_rows = [row for row in rows if (row["map"], row["slip"]) == key]
        final_rows.append(run_rows[-1])

    lines = [
        "# First-Boundary Targeted Split",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"candidate_kind = {args.candidate_kind}, candidate_top_fraction = {args.candidate_top_fraction}",
        f"residual_kind = {args.residual_kind}, residual_top_fraction = {args.residual_top_fraction}, residual_split_policy = {args.residual_split_policy}",
        f"soft_kind = {args.soft_kind}, soft_top_fraction = {args.soft_top_fraction}, soft_split_policy = {args.soft_split_policy}",
        f"gamma = {args.gamma}, slips = {args.slips}, hidden_threshold = {args.hidden_threshold}, local_horizon = {args.local_horizon}",
        (
            f"soft_threshold = {args.soft_threshold}, residual_threshold = {args.residual_threshold}, "
            f"residual_threshold_mode = {args.residual_threshold_mode}, "
            f"compute_struct_distinct = {getattr(args, 'effective_compute_struct_distinct', args.compute_struct_distinct)}, "
            f"struct_mdl_node_cost_weight = {args.struct_mdl_node_cost_weight}, "
            f"struct_mdl_edge_cost_weight = {args.struct_mdl_edge_cost_weight}, "
            f"struct_mdl_exposure_bit_weight = {args.struct_mdl_exposure_bit_weight}, "
            f"struct_mdl_min_gain = {args.struct_mdl_min_gain}, "
            f"residual_reward_weight = {args.residual_reward_weight}, residual_hit_weight = {args.residual_hit_weight}, "
            f"soft_cost_weight = {args.soft_cost_weight}"
        ),
        (
            f"rd_struct_kind = {getattr(args, 'rd_struct_kind', 'occupancy_distinct')}, "
            f"rd_struct_budget = {getattr(args, 'rd_struct_budget', float('inf'))}, "
            f"rd_audit_kind = {getattr(args, 'rd_audit_kind', 'none')}, "
            f"rd_audit_budget = {getattr(args, 'rd_audit_budget', float('inf'))}, "
            f"rd_model_budget = {getattr(args, 'rd_model_budget', float('inf'))}, "
            f"rd_value_budget = {getattr(args, 'rd_value_budget', float('inf'))}, "
            f"rd_start_gap_budget = {getattr(args, 'rd_start_gap_budget', float('inf'))}, "
            f"rd_batch_k = {getattr(args, 'rd_batch_k', 1)}, "
            f"rd_lambdas = "
            f"({getattr(args, 'rd_lambda_struct', 0.0)}, {getattr(args, 'rd_lambda_audit', 0.0)}, "
            f"{getattr(args, 'rd_lambda_model', 0.0)}, "
            f"{getattr(args, 'rd_lambda_value', 0.0)}, {getattr(args, 'rd_lambda_start_gap', 0.0)})"
        ),
        "",
        "## Final Rows",
        "",
        markdown_table(
            final_rows,
            [
                "map",
                "slip",
                "step",
                "n_boundary",
                "n_candidate_boundary",
                "n_edges_valid",
                "invalid_hidden_count",
                "hidden_mass_max",
                "soft_cost_valid_total",
                "soft_cost_max",
                "model_residual_valid_total",
                "model_residual_max",
                "residual_threshold_metric_valid_total",
                "residual_threshold_metric_max",
                "residual_backup_value_norm_max",
                "struct_hidden_prob_max",
                "struct_hidden_bits_valid_total",
                "struct_hidden_distinct_valid_total",
                "struct_hidden_distinct_cvar95",
                "occupancy_struct_hidden_distinct",
                "struct_mdl_split_benefit",
                "struct_mdl_split_cost",
                "struct_mdl_split_gain",
                "struct_mdl_split_candidate_coord",
                "exact_mdl_split_gain",
                "exact_mdl_split_candidate_coord",
                "exact_mdl_base_bits",
                "exact_mdl_candidate_bits",
                "rd_base_rate_bits",
                "rd_candidate_rate_bits",
                "rd_base_violation",
                "rd_candidate_violation",
                "rd_violation_gain",
                "rd_struct_delta",
                "rd_audit_delta",
                "rd_struct_break_even_lambda",
                "rd_split_batch_size",
                "rd_split_candidate_coord",
                "rd_split_candidate_coords",
                "residual_split_candidate_coord",
                "soft_split_candidate_coord",
                "feasible",
                "start_gap",
                "description_length_proxy",
                "split_candidate_coord",
                "split_candidate_source",
                "stop_reason",
            ],
        ),
        "",
        "## Split Trace",
        "",
        markdown_table(
            rows,
            [
                "map",
                "slip",
                "step",
                "n_boundary",
                "n_edges_valid",
                "hidden_mass_max",
                "invalid_hidden_count",
                "soft_cost_valid_total",
                "soft_cost_max",
                "model_residual_valid_total",
                "model_residual_max",
                "residual_threshold_metric_valid_total",
                "residual_threshold_metric_max",
                "residual_backup_value_norm_max",
                "struct_hidden_prob_max",
                "struct_hidden_bits_valid_total",
                "struct_hidden_distinct_valid_total",
                "struct_hidden_distinct_cvar95",
                "occupancy_struct_hidden_distinct",
                "struct_mdl_split_benefit",
                "struct_mdl_split_cost",
                "struct_mdl_split_gain",
                "exact_mdl_split_gain",
                "exact_mdl_base_bits",
                "exact_mdl_candidate_bits",
                "exact_mdl_candidates_evaluated",
                "rd_base_rate_bits",
                "rd_candidate_rate_bits",
                "rd_base_violation",
                "rd_candidate_violation",
                "rd_violation_gain",
                "rd_struct_delta",
                "rd_audit_delta",
                "rd_struct_break_even_lambda",
                "rd_candidates_evaluated",
                "rd_split_batch_size",
                "feasible",
                "start_gap",
                "split_candidate_coord",
                "split_candidate_coords",
                "split_batch_size",
                "split_candidate_source",
                "split_candidate_score",
                "stop_reason",
            ],
        ),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pair-specific targeted options that stop at the first candidate boundary.")
    parser.add_argument("--maps", nargs="+", default=list(MAPS.keys()))
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument(
        "--candidate-kind",
        choices=[
            "all",
            "junction",
            "decision",
            "articulation_only",
            "turn_articulation",
            "eigen_extrema_4",
            "eigen_extrema_8",
            "eigen_extrema_12",
            "coverage_8",
            "coverage_12",
            "articulation_eigen_extrema_12",
            "turn_eigen_extrema_12",
            "articulation_coverage_12",
            "turn_coverage_12",
            "bottleneck",
            "betweenness",
            "value_gradient",
            "transition_entropy",
            "combined",
        ],
        default="bottleneck",
    )
    parser.add_argument("--candidate-top-fraction", type=float, default=0.15)
    parser.add_argument(
        "--proposal-kind",
        choices=[
            "candidate",
            "residual",
            "all",
            "junction",
            "decision",
            "articulation_only",
            "turn_articulation",
            "eigen_extrema_4",
            "eigen_extrema_8",
            "eigen_extrema_12",
            "coverage_8",
            "coverage_12",
            "articulation_eigen_extrema_12",
            "turn_eigen_extrema_12",
            "articulation_coverage_12",
            "turn_coverage_12",
            "bottleneck",
            "betweenness",
            "value_gradient",
            "transition_entropy",
            "combined",
        ],
        default="candidate",
    )
    parser.add_argument(
        "--residual-kind",
        choices=[
            "none",
            "hard",
            "all",
            "junction",
            "decision",
            "articulation_only",
            "turn_articulation",
            "eigen_extrema_4",
            "eigen_extrema_8",
            "eigen_extrema_12",
            "coverage_8",
            "coverage_12",
            "articulation_eigen_extrema_12",
            "turn_eigen_extrema_12",
            "articulation_coverage_12",
            "turn_coverage_12",
            "bottleneck",
            "betweenness",
            "value_gradient",
            "transition_entropy",
            "combined",
        ],
        default="none",
    )
    parser.add_argument("--residual-top-fraction", type=float, default=0.15)
    parser.add_argument("--residual-threshold", type=float, default=0.5)
    parser.add_argument(
        "--residual-threshold-mode",
        choices=["raw", "value_norm", "struct_prob", "struct_bits", "struct_distinct"],
        default="raw",
    )
    parser.add_argument("--compute-struct-distinct", action="store_true")
    parser.add_argument("--residual-reward-weight", type=float, default=0.05)
    parser.add_argument("--residual-hit-weight", type=float, default=0.0)
    parser.add_argument(
        "--residual-split-policy",
        choices=["never", "threshold", "mdl", "exact_mdl", "rd", "rd_surrogate"],
        default="never",
    )
    parser.add_argument("--struct-mdl-node-cost-weight", type=float, default=1.0)
    parser.add_argument("--struct-mdl-edge-cost-weight", type=float, default=0.1)
    parser.add_argument("--struct-mdl-exposure-bit-weight", type=float, default=1.0)
    parser.add_argument("--struct-mdl-min-gain", type=float, default=0.0)
    parser.add_argument("--exact-mdl-top-k", type=int, default=8)
    parser.add_argument(
        "--exact-mdl-struct-kind",
        choices=["distinct", "distinct_bits", "hidden_bits", "occupancy_distinct", "occupancy_distinct_bits"],
        default="occupancy_distinct",
    )
    parser.add_argument("--exact-mdl-option-pair-bit-cost", type=float, default=1.0)
    parser.add_argument("--exact-mdl-policy-tv-bit-cost", type=float, default=0.2)
    parser.add_argument("--exact-mdl-policy-region-bit-cost", type=float, default=0.5)
    parser.add_argument("--exact-mdl-model-residual-bit-cost", type=float, default=1.0)
    parser.add_argument("--exact-mdl-include-edge-encoding", action="store_true")
    parser.add_argument("--rd-top-k", type=int, default=8)
    parser.add_argument(
        "--rd-struct-kind",
        choices=[
            "distinct",
            "distinct_bits",
            "hidden_bits",
            "occupancy_distinct",
            "occupancy_distinct_bits",
            "audit_prob_max",
            "audit_prob_cvar95",
            "audit_distinct_max",
            "audit_distinct_cvar95",
            "audit_distinct_bits_max",
            "audit_distinct_bits_cvar95",
        ],
        default="occupancy_distinct",
    )
    parser.add_argument("--rd-struct-budget", type=float, default=float("inf"))
    parser.add_argument(
        "--rd-audit-kind",
        choices=[
            "none",
            "distinct",
            "distinct_bits",
            "hidden_bits",
            "occupancy_distinct",
            "occupancy_distinct_bits",
            "audit_prob_max",
            "audit_prob_cvar95",
            "audit_distinct_max",
            "audit_distinct_cvar95",
            "audit_distinct_bits_max",
            "audit_distinct_bits_cvar95",
        ],
        default="none",
    )
    parser.add_argument("--rd-audit-budget", type=float, default=float("inf"))
    parser.add_argument("--rd-model-budget", type=float, default=float("inf"))
    parser.add_argument("--rd-value-budget", type=float, default=float("inf"))
    parser.add_argument("--rd-start-gap-budget", type=float, default=float("inf"))
    parser.add_argument("--rd-lambda-struct", type=float, default=0.0)
    parser.add_argument("--rd-lambda-audit", type=float, default=0.0)
    parser.add_argument("--rd-lambda-model", type=float, default=0.0)
    parser.add_argument("--rd-lambda-value", type=float, default=0.0)
    parser.add_argument("--rd-lambda-start-gap", type=float, default=0.0)
    parser.add_argument("--rd-batch-k", type=int, default=1)
    parser.add_argument(
        "--soft-kind",
        choices=["none", "bottleneck", "betweenness", "value_gradient", "transition_entropy", "combined"],
        default="none",
    )
    parser.add_argument("--soft-top-fraction", type=float, default=0.15)
    parser.add_argument("--soft-threshold", type=float, default=1e-6)
    parser.add_argument("--soft-cost-weight", type=float, default=1.0)
    parser.add_argument("--soft-split-policy", choices=["never", "threshold"], default="never")
    parser.add_argument("--local-horizon", type=float, default=999.0)
    parser.add_argument("--hidden-threshold", type=float, default=1e-6)
    parser.add_argument("--max-splits", type=int, default=16)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/first_boundary_targeted_bottleneck"))
    args = parser.parse_args()
    args.effective_compute_struct_distinct = (
        args.compute_struct_distinct
        or args.residual_threshold_mode == "struct_distinct"
        or args.residual_split_policy in {"mdl", "exact_mdl", "rd", "rd_surrogate"}
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    trace_rows: List[Dict[str, object]] = []
    edge_rows: List[Dict[str, object]] = []
    rd_candidate_rows: List[Dict[str, object]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        for slip in args.slips:
            trace, edges = run_one(
                map_name=map_name,
                rows=MAPS[map_name],
                slip=slip,
                gamma=args.gamma,
                candidate_kind=args.candidate_kind,
                candidate_top_fraction=args.candidate_top_fraction,
                residual_kind=args.residual_kind,
                residual_top_fraction=args.residual_top_fraction,
                soft_kind=args.soft_kind,
                soft_top_fraction=args.soft_top_fraction,
                local_horizon=args.local_horizon,
                hidden_threshold=args.hidden_threshold,
                soft_threshold=args.soft_threshold,
                residual_threshold=args.residual_threshold,
                residual_reward_weight=args.residual_reward_weight,
                residual_hit_weight=args.residual_hit_weight,
                residual_threshold_mode=args.residual_threshold_mode,
                compute_struct_distinct=args.effective_compute_struct_distinct,
                struct_mdl_node_cost_weight=args.struct_mdl_node_cost_weight,
                struct_mdl_edge_cost_weight=args.struct_mdl_edge_cost_weight,
                struct_mdl_exposure_bit_weight=args.struct_mdl_exposure_bit_weight,
                struct_mdl_min_gain=args.struct_mdl_min_gain,
                soft_cost_weight=args.soft_cost_weight,
                residual_split_policy=args.residual_split_policy,
                soft_split_policy=args.soft_split_policy,
                max_splits=args.max_splits,
                proposal_kind=args.proposal_kind,
                exact_mdl_top_k=args.exact_mdl_top_k,
                exact_mdl_struct_kind=args.exact_mdl_struct_kind,
                exact_mdl_option_pair_bit_cost=args.exact_mdl_option_pair_bit_cost,
                exact_mdl_policy_tv_bit_cost=args.exact_mdl_policy_tv_bit_cost,
                exact_mdl_policy_region_bit_cost=args.exact_mdl_policy_region_bit_cost,
                exact_mdl_model_residual_bit_cost=args.exact_mdl_model_residual_bit_cost,
                exact_mdl_include_edge_encoding=args.exact_mdl_include_edge_encoding,
                rd_top_k=args.rd_top_k,
                rd_struct_kind=args.rd_struct_kind,
                rd_struct_budget=args.rd_struct_budget,
                rd_audit_kind=args.rd_audit_kind,
                rd_audit_budget=args.rd_audit_budget,
                rd_model_budget=args.rd_model_budget,
                rd_value_budget=args.rd_value_budget,
                rd_start_gap_budget=args.rd_start_gap_budget,
                rd_lambda_struct=args.rd_lambda_struct,
                rd_lambda_audit=args.rd_lambda_audit,
                rd_lambda_model=args.rd_lambda_model,
                rd_lambda_value=args.rd_lambda_value,
                rd_lambda_start_gap=args.rd_lambda_start_gap,
                rd_batch_k=args.rd_batch_k,
                rd_candidate_rows=rd_candidate_rows,
            )
            trace_rows.extend(trace)
            edge_rows.extend(edges)
            final = trace[-1]
            print(
                f"{map_name:10s} slip={slip:.2f} steps={final['step']:2d} B={final['n_boundary']:3d} "
                f"valid={final['n_edges_valid']:3d} hidden_max={final['hidden_mass_max']:.3e} "
                f"res={final['model_residual_valid_total']:.3e} "
                f"metric={final['residual_threshold_metric_valid_total']:.3e} "
                f"soft={final['soft_cost_valid_total']:.3e} "
                f"feasible={final['feasible']} gap={final['start_gap']:.3e}"
            )

    write_csv(args.out_dir / "trace.csv", trace_rows)
    write_csv(args.out_dir / "edges.csv", edge_rows)
    write_csv(args.out_dir / "rd_candidates.csv", rd_candidate_rows)
    (args.out_dir / "trace.json").write_text(json.dumps(trace_rows, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "edges.json").write_text(json.dumps(edge_rows, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "rd_candidates.json").write_text(
        json.dumps(rd_candidate_rows, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(trace_rows, args.out_dir / "summary.md", args)
    print(f"Wrote {args.out_dir / 'trace.csv'}")
    print(f"Wrote {args.out_dir / 'edges.csv'}")
    if rd_candidate_rows:
        print(f"Wrote {args.out_dir / 'rd_candidates.csv'}")
    print(f"Wrote {args.out_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
