#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
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
        "struct_hidden_prob_valid_total": float(
            sum(float(row["struct_hidden_prob"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "struct_hidden_prob_max": float(max((float(row["struct_hidden_prob"]) for row in edge_rows), default=0.0)),
        "struct_hidden_bits_valid_total": float(
            sum(float(row["struct_hidden_bits"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "struct_hidden_bits_max": float(max((float(row["struct_hidden_bits"]) for row in edge_rows), default=0.0)),
        "struct_hidden_distinct_valid_total": float(
            sum(float(row["struct_hidden_distinct"]) for row in edge_rows if bool(row["edge_valid"]))
        ),
        "struct_hidden_distinct_max": float(
            max((float(row["struct_hidden_distinct"]) for row in edge_rows), default=0.0)
        ),
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
        except ValueError:
            feasible = False
    else:
        feasible = False

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
        "struct_hidden_bits_valid_total": float(metadata["struct_hidden_bits_valid_total"]),
        "struct_hidden_bits_max": float(metadata["struct_hidden_bits_max"]),
        "struct_hidden_distinct_valid_total": float(metadata["struct_hidden_distinct_valid_total"]),
        "struct_hidden_distinct_max": float(metadata["struct_hidden_distinct_max"]),
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
        "policy_tv_total": pair_policy_metrics["policy_tv_total"],
        "policy_regions_total": pair_policy_metrics["policy_regions_total"],
        "policy_tv_mean": pair_policy_metrics["policy_tv_mean"],
        "policy_regions_mean": pair_policy_metrics["policy_regions_mean"],
        "target_policy_tv_total": target_policy_metrics["policy_tv_total"],
        "target_policy_regions_total": target_policy_metrics["policy_regions_total"],
        "target_policy_tv_mean": target_policy_metrics["policy_tv_mean"],
        "target_policy_regions_mean": target_policy_metrics["policy_regions_mean"],
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

        split_state = row["hard_split_candidate_state"]
        split_source = "hard_hidden"
        split_score = row["hard_split_candidate_score"]
        if split_state is None and residual_split_policy == "threshold":
            split_state = row["residual_split_candidate_state"]
            split_score = row["residual_split_candidate_score"]
            split_source = f"residual_{residual_threshold_mode}"
        if split_state is None and residual_split_policy == "mdl":
            split_state = row["struct_mdl_split_candidate_state"]
            split_score = row["struct_mdl_split_gain"]
            split_source = "residual_mdl"
        if split_state is None and soft_split_policy == "threshold":
            split_state = row["soft_split_candidate_state"]
            split_score = row["soft_split_candidate_score"]
            split_source = "soft_threshold"
        row["split_candidate_state"] = split_state
        row["split_candidate_score"] = split_score if split_state is not None else 0.0
        row["split_candidate_source"] = split_source if split_state is not None else "none"
        _, idx_to_coord = grid.index_maps()
        row["split_candidate_coord"] = idx_to_coord[int(split_state)] if split_state is not None else None
        if split_state is None:
            row["stop_reason"] = "hybrid_threshold"
            break
        if step >= max_splits:
            row["stop_reason"] = "max_splits"
            break
        row["stop_reason"] = "continue"
        boundary = sorted(set(boundary).union({int(split_state)}))

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
                "struct_mdl_split_benefit",
                "struct_mdl_split_cost",
                "struct_mdl_split_gain",
                "struct_mdl_split_candidate_coord",
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
                "struct_mdl_split_benefit",
                "struct_mdl_split_cost",
                "struct_mdl_split_gain",
                "feasible",
                "start_gap",
                "split_candidate_coord",
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
    parser.add_argument("--residual-split-policy", choices=["never", "threshold", "mdl"], default="never")
    parser.add_argument("--struct-mdl-node-cost-weight", type=float, default=1.0)
    parser.add_argument("--struct-mdl-edge-cost-weight", type=float, default=0.1)
    parser.add_argument("--struct-mdl-exposure-bit-weight", type=float, default=1.0)
    parser.add_argument("--struct-mdl-min-gain", type=float, default=0.0)
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
        or args.residual_split_policy == "mdl"
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    trace_rows: List[Dict[str, object]] = []
    edge_rows: List[Dict[str, object]] = []
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
    (args.out_dir / "trace.json").write_text(json.dumps(trace_rows, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "edges.json").write_text(json.dumps(edge_rows, indent=2) + "\n", encoding="utf-8")
    write_report(trace_rows, args.out_dir / "summary.md", args)
    print(f"Wrote {args.out_dir / 'trace.csv'}")
    print(f"Wrote {args.out_dir / 'edges.csv'}")
    print(f"Wrote {args.out_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
