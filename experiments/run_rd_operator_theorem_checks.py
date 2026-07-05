#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import (
    GridWorld,
    endpoint_boundary_states,
    graph_adjacency,
    shortest_path_policy_to_target,
    transition_matrix_for_policy,
)
from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import (
    boundary_code_bits,
    candidate_boundary_states,
    critical_saliency,
    edge_code_bits,
    evaluate_boundary,
    rate_code_length,
)
from run_graph_baseline_comparison import LEARNED_RECIPES


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def json_default(obj: object) -> object:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def finite_float(value: object, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def parse_prob_map(raw: object) -> Dict[int, float]:
    if raw in (None, ""):
        return {}
    try:
        data = json.loads(str(raw))
    except json.JSONDecodeError:
        return {}
    return {int(k): finite_float(v) for k, v in data.items()}


def phi_bits(p: float, eps: float = 1e-12) -> float:
    p = min(max(float(p), 0.0), 1.0 - eps)
    return -math.log2(max(eps, 1.0 - p + eps))


def phi_bits_prime(p: float, eps: float = 1e-12) -> float:
    p = min(max(float(p), 0.0), 1.0 - eps)
    return 1.0 / (math.log(2.0) * max(eps, 1.0 - p + eps))


def phi_bits_second_upper(p: float, eps: float = 1e-12) -> float:
    p = min(max(float(p), 0.0), 1.0 - eps)
    denom = max(eps, 1.0 - p + eps)
    return 1.0 / (math.log(2.0) * denom * denom)


def recipe_value(recipe: Mapping[str, object], name: str, default: object) -> object:
    return recipe[name] if name in recipe else default


def build_recipe_context(
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    gamma: float,
    slip: float,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    candidate_kind = str(recipe["candidate_kind"])
    candidate_boundary = candidate_boundary_states(
        grid=grid,
        kind=candidate_kind,
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=float(recipe["candidate_top_fraction"]),
    )
    residual_kind = str(recipe["residual_kind"])
    if residual_kind == "none":
        residual_boundary = endpoint_boundary_states(grid)
    elif residual_kind == "hard":
        residual_boundary = candidate_boundary
    else:
        residual_boundary = candidate_boundary_states(
            grid=grid,
            kind=residual_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=float(recipe["residual_top_fraction"]),
        )
    proposal_kind = str(recipe_value(recipe, "proposal_kind", "candidate"))
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
            top_fraction=float(recipe["candidate_top_fraction"]),
        )
    soft_kind = str(recipe["soft_kind"])
    if soft_kind == "none":
        soft_state_cost = np.zeros(grid.n_states, dtype=float)
    else:
        soft_state_cost = critical_saliency(
            grid=grid,
            kind=soft_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=float(recipe["soft_top_fraction"]),
        )
    return {
        "grid": grid,
        "candidate_boundary": candidate_boundary,
        "residual_boundary": residual_boundary,
        "proposal_boundary": proposal_boundary,
        "soft_state_cost": soft_state_cost,
    }


def evaluate_recipe_boundary(
    map_name: str,
    context: Mapping[str, object],
    recipe: Mapping[str, object],
    boundary: Sequence[int],
    gamma: float,
    slip: float,
    first_hit_mode: str = "exact",
    first_hit_truncation_steps: int = 32,
    first_hit_tail_tol: float = 0.0,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    return evaluate_boundary(
        map_name=map_name,
        grid=context["grid"],  # type: ignore[arg-type]
        boundary=boundary,
        candidate_boundary=context["candidate_boundary"],  # type: ignore[arg-type]
        residual_boundary=context["residual_boundary"],  # type: ignore[arg-type]
        soft_state_cost=context["soft_state_cost"],  # type: ignore[arg-type]
        slip=slip,
        gamma=gamma,
        local_horizon=999.0,
        hidden_threshold=1e-6,
        soft_threshold=float(recipe["soft_threshold"]),
        residual_threshold=float(recipe["residual_threshold"]),
        residual_reward_weight=0.05,
        residual_hit_weight=0.0,
        residual_threshold_mode=str(recipe["residual_threshold_mode"]),
        compute_struct_distinct=False,
        struct_mdl_node_cost_weight=1.0,
        struct_mdl_edge_cost_weight=float(recipe["struct_mdl_edge_cost_weight"]),
        struct_mdl_exposure_bit_weight=1.0,
        struct_mdl_min_gain=0.0,
        residual_kind=str(recipe["residual_kind"]),
        residual_top_fraction=float(recipe["residual_top_fraction"]),
        soft_kind=str(recipe["soft_kind"]),
        soft_top_fraction=float(recipe["soft_top_fraction"]),
        soft_cost_weight=1.0,
        candidate_kind=str(recipe["candidate_kind"]),
        candidate_top_fraction=float(recipe["candidate_top_fraction"]),
        proposal_boundary=context["proposal_boundary"],  # type: ignore[arg-type]
        first_hit_mode=first_hit_mode,
        first_hit_truncation_steps=first_hit_truncation_steps,
        first_hit_tail_tol=first_hit_tail_tol,
    )


def boundary_rate(row: Mapping[str, object], recipe: Mapping[str, object]) -> float:
    return rate_code_length(
        row,
        option_pair_bit_cost=float(recipe_value(recipe, "exact_mdl_option_pair_bit_cost", 1.0)),
        policy_tv_bit_cost=float(recipe_value(recipe, "exact_mdl_policy_tv_bit_cost", 0.2)),
        policy_region_bit_cost=float(recipe_value(recipe, "exact_mdl_policy_region_bit_cost", 0.5)),
        include_edge_encoding=bool(recipe_value(recipe, "exact_mdl_include_edge_encoding", False)),
    )


def approximate_split_rate_delta(row: Mapping[str, object], recipe: Mapping[str, object]) -> float:
    n_states = int(row["n_states"])
    n_boundary = int(row["n_boundary"])
    n_edges_valid = int(row["n_edges_valid"])
    boundary_delta = boundary_code_bits(n_states, n_boundary + 1) - boundary_code_bits(n_states, n_boundary)
    if bool(recipe_value(recipe, "exact_mdl_include_edge_encoding", False)):
        edge_delta = edge_code_bits(n_boundary + 1, n_edges_valid + 2 * n_boundary) - edge_code_bits(
            n_boundary,
            n_edges_valid,
        )
    else:
        edge_delta = 0.0
    option_delta = float(recipe_value(recipe, "exact_mdl_option_pair_bit_cost", 1.0)) * float(2 * max(1, n_boundary))
    return float(boundary_delta + edge_delta + option_delta)


def active_edges(edge_rows: Sequence[Mapping[str, object]], edge_weight: str) -> List[Tuple[Mapping[str, object], float]]:
    out: List[Tuple[Mapping[str, object], float]] = []
    valid_rows = [edge_row for edge_row in edge_rows if bool(edge_row.get("edge_valid", False))]
    base_rows = valid_rows if valid_rows else list(edge_rows)
    occupancy_total = sum(finite_float(edge_row.get("policy_occupancy", 0.0)) for edge_row in base_rows)
    for edge_row in base_rows:
        if edge_weight == "occupancy" or (edge_weight == "occupancy_or_uniform" and occupancy_total > 1e-12):
            weight = finite_float(edge_row.get("policy_occupancy", 0.0))
        else:
            weight = 1.0
        if weight > 1e-12:
            out.append((edge_row, weight))
    return out


def hidden_distortions(
    edge_rows: Sequence[Mapping[str, object]],
    boundary: Sequence[int],
    edge_weight: str,
) -> Dict[str, float]:
    boundary_set = set(int(state) for state in boundary)
    linear = 0.0
    bits = 0.0
    for edge_row, weight in active_edges(edge_rows, edge_weight=edge_weight):
        probs = parse_prob_map(edge_row.get("residual_hidden_probs", "{}"))
        hidden_mass = sum(prob for state, prob in probs.items() if state not in boundary_set)
        linear += weight * hidden_mass
        bits += weight * phi_bits(hidden_mass)
    return {"linear": float(linear), "bits": float(bits)}


def edge_key(edge_row: Mapping[str, object]) -> Tuple[int, int]:
    return int(edge_row["src_state"]), int(edge_row["target_state"])


def hidden_mass_from_probs(probs: Mapping[int, float], hidden_set: set[int]) -> float:
    return sum(finite_float(prob) for state, prob in probs.items() if int(state) in hidden_set)


def spectral_energy_scores(grid: GridWorld, n_vectors: int = 6) -> np.ndarray:
    adjacency = graph_adjacency(grid)
    degree = np.diag(adjacency.sum(axis=1))
    laplacian = degree - adjacency
    if grid.n_states <= 1:
        return np.zeros(grid.n_states, dtype=float)
    values, vectors = np.linalg.eigh(laplacian)
    n_vec = max(1, min(n_vectors, grid.n_states - 1))
    nontrivial = vectors[:, 1 : n_vec + 1]
    lambdas = values[1 : n_vec + 1]
    scores = np.zeros(grid.n_states, dtype=float)
    for state in range(grid.n_states):
        for neighbor in np.flatnonzero(adjacency[state] > 0):
            diff = nontrivial[state] - nontrivial[neighbor]
            scores[state] += float(np.sum((lambdas + 1e-9) * diff * diff))
    max_score = float(scores.max(initial=0.0))
    if max_score > 0.0:
        scores = scores / max_score
    return scores


def deterministic_random_score(map_name: str, step: int, state: int) -> float:
    value = 1469598103934665603
    for ch in f"{map_name}:{step}:{state}":
        value ^= ord(ch)
        value *= 1099511628211
        value &= (1 << 64) - 1
    return value / float(1 << 64)


def rank_rows(rows: List[Dict[str, object]], field: str, out_field: str) -> None:
    ranked = sorted(rows, key=lambda row: (finite_float(row[field], -float("inf")), -int(row["candidate_state"])), reverse=True)
    for rank, row in enumerate(ranked, start=1):
        row[out_field] = rank


def kendall_tau(rows: Sequence[Mapping[str, object]], a: str, b: str) -> float | None:
    values: List[Tuple[float, float]] = []
    for row in rows:
        av = finite_float(row.get(a), default=float("nan"))
        bv = finite_float(row.get(b), default=float("nan"))
        if math.isfinite(av) and math.isfinite(bv):
            values.append((av, bv))
    concordant = 0
    discordant = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            da = values[i][0] - values[j][0]
            db = values[i][1] - values[j][1]
            product = da * db
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    total = concordant + discordant
    if total == 0:
        return None
    return (concordant - discordant) / total


def operator_marginal_rows(
    map_name: str,
    step: int,
    context: Mapping[str, object],
    recipe: Mapping[str, object],
    boundary: Sequence[int],
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    max_candidates: int,
    with_frozen_recompute: bool,
    with_actual_recompute: bool,
    with_recompute_modes: bool,
) -> Tuple[List[Dict[str, object]], Dict[str, object], List[Dict[str, object]]]:
    base_eval_start = time.perf_counter()
    row, edge_rows = evaluate_recipe_boundary(
        map_name=map_name,
        context=context,
        recipe=recipe,
        boundary=boundary,
        gamma=gamma,
        slip=slip,
    )
    base_eval_time = time.perf_counter() - base_eval_start
    score_start = time.perf_counter()
    grid: GridWorld = context["grid"]  # type: ignore[assignment]
    goal = grid.symbol_states("G")[0]
    betweenness_scores = critical_saliency(
        grid=grid,
        kind="betweenness",
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=1.0,
    )
    value_gradient_scores = critical_saliency(
        grid=grid,
        kind="value_gradient",
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=1.0,
    )
    spectral_scores = spectral_energy_scores(grid)
    degree_scores = np.array([float(len(grid.legal_actions(state))) for state in range(grid.n_states)])
    degree_max = float(degree_scores.max(initial=0.0))
    if degree_max > 0.0:
        degree_scores = degree_scores / degree_max
    universe = sorted(set(int(s) for s in context["proposal_boundary"]).union(boundary))  # type: ignore[arg-type]
    hidden_candidates = [state for state in universe if state not in set(boundary)]
    weighted_edges = active_edges(edge_rows, edge_weight=edge_weight)

    pre_scores: Dict[int, float] = {state: 0.0 for state in hidden_candidates}
    edge_kernels: List[Tuple[Mapping[str, object], float, Dict[int, float], float]] = []
    for edge_row, weight in weighted_edges:
        probs = parse_prob_map(edge_row.get("residual_hidden_probs", "{}"))
        hidden_mass = sum(prob for state, prob in probs.items() if state not in set(boundary))
        edge_kernels.append((edge_row, weight, probs, hidden_mass))
        for state, prob in probs.items():
            if state in pre_scores:
                pre_scores[state] += weight * prob

    ranked_candidates = sorted(hidden_candidates, key=lambda s: (pre_scores.get(s, 0.0), -s), reverse=True)
    if max_candidates > 0:
        ranked_candidates = ranked_candidates[:max_candidates]

    base_rate = boundary_rate(row, recipe)
    base_distortions = hidden_distortions(edge_rows, boundary=boundary, edge_weight=edge_weight)
    base_uniform_distortions = hidden_distortions(edge_rows, boundary=boundary, edge_weight="uniform")
    base_objective = base_rate + lambda_struct * base_distortions["bits"]
    base_uniform_objective = base_rate + lambda_struct * base_uniform_distortions["bits"]
    local_rate_delta = approximate_split_rate_delta(row, recipe)
    out: List[Dict[str, object]] = []
    recompute_time = 0.0
    for candidate_state in ranked_candidates:
        linear_delta = 0.0
        bits_fd_delta = 0.0
        bits_grad_delta = 0.0
        grad_abs_error_bound = 0.0
        contributing_edges = 0
        frozen_linear_after_direct = 0.0
        frozen_bits_after_direct = 0.0
        for edge_row, weight, probs, hidden_mass in edge_kernels:
            k_prob = finite_float(probs.get(candidate_state, 0.0))
            next_hidden_mass = max(0.0, hidden_mass - k_prob)
            frozen_linear_after_direct += weight * next_hidden_mass
            frozen_bits_after_direct += weight * phi_bits(next_hidden_mass)
            if k_prob <= 1e-12:
                continue
            contributing_edges += 1
            linear_delta += weight * k_prob
            fd_piece = phi_bits(hidden_mass) - phi_bits(max(0.0, hidden_mass - k_prob))
            grad_piece = phi_bits_prime(hidden_mass) * k_prob
            bits_fd_delta += weight * fd_piece
            bits_grad_delta += weight * grad_piece
            grad_abs_error_bound += weight * 0.5 * phi_bits_second_upper(hidden_mass) * k_prob * k_prob

        rate_delta = local_rate_delta
        frozen_recompute_score = float("nan")
        frozen_objective_after = float("nan")
        frozen_linear_after = float("nan")
        frozen_bits_after = float("nan")
        fd_minus_frozen = float("nan")
        if with_frozen_recompute:
            frozen_linear_after = frozen_linear_after_direct
            frozen_bits_after = frozen_bits_after_direct
            frozen_objective_after = base_rate + local_rate_delta + lambda_struct * frozen_bits_after
            frozen_recompute_score = base_objective - frozen_objective_after
            fd_minus_frozen = (lambda_struct * bits_fd_delta - rate_delta) - frozen_recompute_score

        actual_recompute_score = float("nan")
        actual_rate_delta = float("nan")
        adaptive_drift = float("nan")
        adaptive_drift_rate = float("nan")
        adaptive_drift_bits = float("nan")
        adaptive_drift_linear = float("nan")
        rate_only_score = float("nan")
        rate_only_drift = float("nan")
        occupancy_only_score = float("nan")
        occupancy_drift = float("nan")
        edge_only_score = float("nan")
        edge_drift = float("nan")
        edge_option_uniform_score = float("nan")
        edge_option_uniform_drift = float("nan")
        candidate_objective = float("nan")
        candidate_distortions = {"linear": float("nan"), "bits": float("nan")}
        if with_actual_recompute or with_recompute_modes:
            candidate_start = time.perf_counter()
            trial_boundary = sorted(set(boundary).union({int(candidate_state)}))
            candidate_row, candidate_edges = evaluate_recipe_boundary(
                map_name=map_name,
                context=context,
                recipe=recipe,
                boundary=trial_boundary,
                gamma=gamma,
                slip=slip,
            )
            recompute_time += time.perf_counter() - candidate_start
            candidate_rate = boundary_rate(candidate_row, recipe)
            actual_rate_delta = candidate_rate - base_rate
            rate_only_score = lambda_struct * bits_fd_delta - actual_rate_delta
            if with_frozen_recompute:
                rate_only_drift = rate_only_score - frozen_recompute_score

            candidate_distortions = hidden_distortions(
                candidate_edges,
                boundary=trial_boundary,
                edge_weight=edge_weight,
            )
            candidate_objective = candidate_rate + lambda_struct * candidate_distortions["bits"]
            actual_recompute_score = base_objective - candidate_objective

            if with_recompute_modes:
                trial_hidden_set = set(universe) - set(trial_boundary)
                candidate_weight_by_key = {
                    edge_key(candidate_edge): candidate_weight
                    for candidate_edge, candidate_weight in active_edges(candidate_edges, edge_weight=edge_weight)
                }
                candidate_row_by_key = {edge_key(candidate_edge): candidate_edge for candidate_edge in candidate_edges}

                occupancy_bits_after = 0.0
                occupancy_linear_after = 0.0
                edge_bits_after = 0.0
                edge_linear_after = 0.0
                for frozen_edge, frozen_weight, _probs, _hidden_mass in edge_kernels:
                    key = edge_key(frozen_edge)
                    candidate_weight = candidate_weight_by_key.get(key, 0.0)
                    frozen_probs = parse_prob_map(frozen_edge.get("residual_hidden_probs", "{}"))
                    frozen_after_mass = hidden_mass_from_probs(frozen_probs, trial_hidden_set)
                    occupancy_linear_after += candidate_weight * frozen_after_mass
                    occupancy_bits_after += candidate_weight * phi_bits(frozen_after_mass)

                    candidate_edge = candidate_row_by_key.get(key)
                    if candidate_edge is None:
                        continue
                    candidate_probs = parse_prob_map(candidate_edge.get("residual_hidden_probs", "{}"))
                    candidate_after_mass = hidden_mass_from_probs(candidate_probs, trial_hidden_set)
                    edge_linear_after += frozen_weight * candidate_after_mass
                    edge_bits_after += frozen_weight * phi_bits(candidate_after_mass)

                occupancy_after_objective = base_rate + local_rate_delta + lambda_struct * occupancy_bits_after
                occupancy_only_score = base_objective - occupancy_after_objective
                edge_after_objective = base_rate + local_rate_delta + lambda_struct * edge_bits_after
                edge_only_score = base_objective - edge_after_objective

                candidate_uniform_distortions = hidden_distortions(
                    candidate_edges,
                    boundary=trial_boundary,
                    edge_weight="uniform",
                )
                edge_option_uniform_after = (
                    base_rate + local_rate_delta + lambda_struct * candidate_uniform_distortions["bits"]
                )
                edge_option_uniform_score = base_uniform_objective - edge_option_uniform_after

                if with_frozen_recompute:
                    occupancy_drift = occupancy_only_score - frozen_recompute_score
                    edge_drift = edge_only_score - frozen_recompute_score
                    edge_option_uniform_drift = edge_option_uniform_score - frozen_recompute_score

            if with_frozen_recompute:
                actual_bits_delta = base_distortions["bits"] - candidate_distortions["bits"]
                actual_linear_delta = base_distortions["linear"] - candidate_distortions["linear"]
                adaptive_drift = actual_recompute_score - frozen_recompute_score
                adaptive_drift_rate = local_rate_delta - actual_rate_delta
                adaptive_drift_bits = lambda_struct * (actual_bits_delta - bits_fd_delta)
                adaptive_drift_linear = actual_linear_delta - linear_delta
        out.append(
            {
                "map": map_name,
                "step": step,
                "candidate_state": int(candidate_state),
                "candidate_coord": context["grid"].index_maps()[1][int(candidate_state)],  # type: ignore[index, union-attr]
                "n_boundary": len(boundary),
                "n_candidates_considered": len(ranked_candidates),
                "n_active_edges": len(weighted_edges),
                "contributing_edges": contributing_edges,
                "lambda_struct": lambda_struct,
                "edge_weight": edge_weight,
                "linear_delta": linear_delta,
                "raw_hidden_score": linear_delta,
                "random_score": deterministic_random_score(map_name, step, int(candidate_state)),
                "spectral_score": float(spectral_scores[int(candidate_state)]),
                "betweenness_score": float(betweenness_scores[int(candidate_state)]),
                "value_gradient_score": float(value_gradient_scores[int(candidate_state)]),
                "degree_score": float(degree_scores[int(candidate_state)]),
                "bits_fd_delta": bits_fd_delta,
                "bits_grad_delta": bits_grad_delta,
                "grad_minus_fd": bits_grad_delta - bits_fd_delta,
                "grad_abs_error": abs(bits_grad_delta - bits_fd_delta),
                "grad_abs_error_bound": grad_abs_error_bound,
                "rate_delta": rate_delta,
                "linear_operator_score": lambda_struct * linear_delta - rate_delta,
                "bits_fd_operator_score": lambda_struct * bits_fd_delta - rate_delta,
                "bits_grad_operator_score": lambda_struct * bits_grad_delta - rate_delta,
                "frozen_recompute_score": frozen_recompute_score,
                "fd_minus_frozen": fd_minus_frozen,
                "frozen_objective_before": base_objective,
                "frozen_objective_after": frozen_objective_after,
                "frozen_linear_before": base_distortions["linear"],
                "frozen_linear_after": frozen_linear_after,
                "frozen_bits_before": base_distortions["bits"],
                "frozen_bits_after": frozen_bits_after,
                "rate_only_score": rate_only_score,
                "rate_only_drift": rate_only_drift,
                "occupancy_only_score": occupancy_only_score,
                "occupancy_drift": occupancy_drift,
                "edge_only_score": edge_only_score,
                "edge_drift": edge_drift,
                "edge_option_uniform_score": edge_option_uniform_score,
                "edge_option_uniform_drift": edge_option_uniform_drift,
                "actual_recompute_score": actual_recompute_score,
                "actual_rate_delta": actual_rate_delta,
                "adaptive_drift": adaptive_drift,
                "adaptive_drift_rate": adaptive_drift_rate,
                "adaptive_drift_bits": adaptive_drift_bits,
                "adaptive_drift_linear": adaptive_drift_linear,
                "actual_objective_before": base_objective,
                "actual_objective_after": candidate_objective,
                "actual_linear_before": base_distortions["linear"],
                "actual_linear_after": candidate_distortions["linear"],
                "actual_bits_before": base_distortions["bits"],
                "actual_bits_after": candidate_distortions["bits"],
                "time_base_eval_sec": base_eval_time,
                "time_operator_score_sec": 0.0,
                "time_recompute_total_sec": 0.0,
                "recompute_speedup_proxy": float("nan"),
            }
        )

    score_time = max(0.0, time.perf_counter() - score_start - recompute_time)
    for diag in out:
        diag["time_operator_score_sec"] = score_time
        diag["time_recompute_total_sec"] = recompute_time
        diag["recompute_speedup_proxy"] = (
            recompute_time / max(1e-12, score_time)
            if recompute_time > 0.0
            else float("nan")
        )

    rank_fields = [
        ("linear_operator_score", "linear_rank"),
        ("bits_fd_operator_score", "bits_fd_rank"),
        ("bits_grad_operator_score", "bits_grad_rank"),
        ("raw_hidden_score", "raw_hidden_rank"),
        ("random_score", "random_rank"),
        ("spectral_score", "spectral_rank"),
        ("betweenness_score", "betweenness_rank"),
        ("value_gradient_score", "value_gradient_rank"),
        ("degree_score", "degree_rank"),
    ]
    if with_frozen_recompute:
        rank_fields.append(("frozen_recompute_score", "frozen_rank"))
    if with_recompute_modes:
        rank_fields.extend(
            [
                ("rate_only_score", "rate_only_rank"),
                ("occupancy_only_score", "occupancy_only_rank"),
                ("edge_only_score", "edge_only_rank"),
                ("edge_option_uniform_score", "edge_option_uniform_rank"),
            ]
        )
    if with_actual_recompute:
        rank_fields.append(("actual_recompute_score", "actual_rank"))
    for field, rank_field in rank_fields:
        rank_rows(out, field, rank_field)
    return out, row, edge_rows


def truncated_first_hit_probabilities(
    grid: GridWorld,
    src_state: int,
    target_state: int,
    terminals: Sequence[int],
    slip: float,
    k_steps: int,
) -> Dict[int, float]:
    terminals = sorted(set(int(state) for state in terminals if int(state) != int(src_state)))
    if not terminals:
        return {}
    policy = shortest_path_policy_to_target(grid, int(target_state), slip=slip)
    P, _r = transition_matrix_for_policy(grid, policy, absorbing=terminals)
    terminal_set = set(terminals)
    interior = np.array([state for state in range(grid.n_states) if state not in terminal_set], dtype=int)
    if len(interior) == 0:
        return {state: 0.0 for state in terminals}
    start_pos_raw = np.flatnonzero(interior == int(src_state))
    if len(start_pos_raw) == 0:
        return {state: 0.0 for state in terminals}
    start_pos = int(start_pos_raw[0])
    T = np.array(terminals, dtype=int)
    P_II = P[np.ix_(interior, interior)]
    P_IT = P[np.ix_(interior, T)]
    current = np.zeros(len(interior), dtype=float)
    current[start_pos] = 1.0
    approx = np.zeros(len(T), dtype=float)
    for _ in range(max(0, int(k_steps)) + 1):
        approx += current @ P_IT
        current = current @ P_II
    return {int(state): float(approx[pos]) for pos, state in enumerate(T)}


def truncation_rows(
    map_name: str,
    step: int,
    context: Mapping[str, object],
    boundary: Sequence[int],
    edge_rows: Sequence[Mapping[str, object]],
    slip: float,
    edge_weight: str,
    k_values: Sequence[int],
) -> List[Dict[str, object]]:
    grid: GridWorld = context["grid"]  # type: ignore[assignment]
    universe = sorted(set(int(s) for s in context["proposal_boundary"]).union(boundary))  # type: ignore[arg-type]
    hidden_candidates = [state for state in universe if state not in set(boundary)]
    weighted_edges = active_edges(edge_rows, edge_weight=edge_weight)
    exact_scores = {state: 0.0 for state in hidden_candidates}
    for edge_row, weight in weighted_edges:
        probs = parse_prob_map(edge_row.get("residual_hidden_probs", "{}"))
        for state in hidden_candidates:
            exact_scores[state] += weight * finite_float(probs.get(state, 0.0))
    exact_top = max(hidden_candidates, key=lambda s: (exact_scores.get(s, 0.0), -s)) if hidden_candidates else None

    rows: List[Dict[str, object]] = []
    for k_steps in k_values:
        k_started = time.perf_counter()
        approx_scores = {state: 0.0 for state in hidden_candidates}
        for edge_row, weight in weighted_edges:
            terminals = [state for state in universe if state != int(edge_row["src_state"])]
            approx = truncated_first_hit_probabilities(
                grid=grid,
                src_state=int(edge_row["src_state"]),
                target_state=int(edge_row["target_state"]),
                terminals=terminals,
                slip=slip,
                k_steps=int(k_steps),
            )
            for state in hidden_candidates:
                approx_scores[state] += weight * finite_float(approx.get(state, 0.0))
        errors = [abs(approx_scores[state] - exact_scores[state]) for state in hidden_candidates]
        approx_top = (
            max(hidden_candidates, key=lambda s: (approx_scores.get(s, 0.0), -s))
            if hidden_candidates
            else None
        )
        rows.append(
            {
                "map": map_name,
                "step": step,
                "k_steps": int(k_steps),
                "n_boundary": len(boundary),
                "n_candidates": len(hidden_candidates),
                "n_active_edges": len(weighted_edges),
                "mean_abs_score_error": float(np.mean(errors)) if errors else 0.0,
                "max_abs_score_error": max(errors) if errors else 0.0,
                "l1_score_error": float(sum(errors)),
                "exact_top_state": exact_top,
                "approx_top_state": approx_top,
                "top1_match": exact_top == approx_top,
                "exact_top_score": exact_scores.get(exact_top, 0.0) if exact_top is not None else 0.0,
                "approx_top_score": approx_scores.get(approx_top, 0.0) if approx_top is not None else 0.0,
                "time_truncated_green_sec": time.perf_counter() - k_started,
            }
        )
    return rows


def top_row(rows: Sequence[Mapping[str, object]], field: str) -> Mapping[str, object] | None:
    if not rows:
        return None
    return max(rows, key=lambda row: (finite_float(row.get(field), -float("inf")), -int(row["candidate_state"])))


def row_for_state(rows: Sequence[Mapping[str, object]], state: int | None) -> Mapping[str, object] | None:
    if state is None:
        return None
    for row in rows:
        if int(row["candidate_state"]) == int(state):
            return row
    return None


def actual_regret_for_choice(
    rows: Sequence[Mapping[str, object]],
    choice: Mapping[str, object] | None,
    actual_best: float,
) -> float | None:
    if choice is None or not math.isfinite(actual_best):
        return None
    actual_at_choice = finite_float(choice.get("actual_recompute_score"), default=float("nan"))
    if not math.isfinite(actual_at_choice):
        return None
    return actual_best - actual_at_choice


def aggregate_truncation(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, int], List[Mapping[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["map"]), int(row["k_steps"])), []).append(row)
    out: List[Dict[str, object]] = []
    for (map_name, k_steps), group in sorted(grouped.items()):
        out.append(
            {
                "map": map_name,
                "k_steps": k_steps,
                "n_steps": len(group),
                "top1_match_rate": sum(1 for row in group if bool(row["top1_match"])) / max(1, len(group)),
                "mean_abs_score_error": float(
                    np.mean([finite_float(row["mean_abs_score_error"]) for row in group])
                ),
                "max_abs_score_error": max(finite_float(row["max_abs_score_error"]) for row in group),
                "mean_time_truncated_green_sec": float(
                    np.mean([finite_float(row["time_truncated_green_sec"]) for row in group])
                ),
            }
        )
    return out


def runtime_rows(
    summary_rows: Sequence[Mapping[str, object]],
    trunc_summary_rows: Sequence[Mapping[str, object]],
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in summary_rows:
        n_candidates = max(1, int(row["n_candidates"]))
        fd_time = finite_float(row.get("time_operator_score_sec"))
        recompute_time = finite_float(row.get("time_recompute_total_sec"))
        out.append(
            {
                "map": row["map"],
                "step": row["step"],
                "method": "fd_grad_operator",
                "n_candidates": row["n_candidates"],
                "time_sec": fd_time,
                "time_per_candidate_sec": fd_time / n_candidates,
                "relative_to_fd_grad": 1.0,
            }
        )
        if recompute_time > 0.0:
            out.append(
                {
                    "map": row["map"],
                    "step": row["step"],
                    "method": "full_actual_recompute",
                    "n_candidates": row["n_candidates"],
                    "time_sec": recompute_time,
                    "time_per_candidate_sec": recompute_time / n_candidates,
                    "relative_to_fd_grad": recompute_time / max(1e-12, fd_time),
                }
            )
    for row in trunc_summary_rows:
        out.append(
            {
                "map": row["map"],
                "step": "all",
                "method": f"truncated_green_K{row['k_steps']}",
                "n_candidates": "",
                "time_sec": row["mean_time_truncated_green_sec"],
                "time_per_candidate_sec": "",
                "relative_to_fd_grad": "",
                "top1_match_rate": row["top1_match_rate"],
                "mean_abs_score_error": row["mean_abs_score_error"],
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the RD Boundary Green operator against finite differences and truncated Green kernels."
    )
    parser.add_argument("--map-specs", nargs="+", default=["maze:13", "four_rooms:13", "open_room:9"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--max-steps", type=int, default=4)
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--truncation-k", nargs="+", type=int, default=[1, 2, 4, 8, 16, 32])
    parser.add_argument("--with-frozen-recompute", action="store_true")
    parser.add_argument("--with-actual-recompute", action="store_true")
    parser.add_argument("--with-recompute-modes", action="store_true")
    parser.add_argument("--greedy-positive-only", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/rd_operator_theorem_checks"))
    args = parser.parse_args()
    with_frozen_recompute = args.with_frozen_recompute or args.with_recompute_modes
    with_actual_recompute = args.with_actual_recompute or args.with_recompute_modes

    recipe = LEARNED_RECIPES[args.recipe]
    marginal_rows: List[Dict[str, object]] = []
    trunc_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []
    started = time.perf_counter()

    for _family, _size, map_label, map_rows in parse_map_specs(args.map_specs):
        context = build_recipe_context(map_rows, recipe=recipe, gamma=args.gamma, slip=args.slip)
        grid: GridWorld = context["grid"]  # type: ignore[assignment]
        boundary = endpoint_boundary_states(grid)
        selected_sequence: List[int] = []
        for step in range(args.max_steps + 1):
            step_rows, base_row, edge_rows = operator_marginal_rows(
                map_name=map_label,
                step=step,
                context=context,
                recipe=recipe,
                boundary=boundary,
                gamma=args.gamma,
                slip=args.slip,
                lambda_struct=args.lambda_struct,
                edge_weight=args.edge_weight,
                max_candidates=args.max_candidates,
                with_frozen_recompute=with_frozen_recompute,
                with_actual_recompute=with_actual_recompute,
                with_recompute_modes=args.with_recompute_modes,
            )
            marginal_rows.extend(step_rows)
            trunc_rows.extend(
                truncation_rows(
                    map_name=map_label,
                    step=step,
                    context=context,
                    boundary=boundary,
                    edge_rows=edge_rows,
                    slip=args.slip,
                    edge_weight=args.edge_weight,
                    k_values=args.truncation_k,
                )
            )
            top_fd = top_row(step_rows, "bits_fd_operator_score")
            top_grad = top_row(step_rows, "bits_grad_operator_score")
            top_frozen = top_row(step_rows, "frozen_recompute_score") if with_frozen_recompute else None
            top_rate = top_row(step_rows, "rate_only_score") if args.with_recompute_modes else None
            top_occupancy = top_row(step_rows, "occupancy_only_score") if args.with_recompute_modes else None
            top_edge = top_row(step_rows, "edge_only_score") if args.with_recompute_modes else None
            top_edge_option = top_row(step_rows, "edge_option_uniform_score") if args.with_recompute_modes else None
            top_actual = top_row(step_rows, "actual_recompute_score") if with_actual_recompute else None
            top_raw_hidden = top_row(step_rows, "raw_hidden_score")
            top_random = top_row(step_rows, "random_score")
            top_spectral = top_row(step_rows, "spectral_score")
            top_betweenness = top_row(step_rows, "betweenness_score")
            top_value_gradient = top_row(step_rows, "value_gradient_score")
            top_degree = top_row(step_rows, "degree_score")
            mean_grad_error = (
                float(np.mean([finite_float(row["grad_abs_error"]) for row in step_rows]))
                if step_rows
                else 0.0
            )
            max_bound_ratio = max(
                (
                    finite_float(row["grad_abs_error"]) / max(1e-12, finite_float(row["grad_abs_error_bound"]))
                    for row in step_rows
                    if finite_float(row["grad_abs_error_bound"]) > 0.0
                ),
                default=0.0,
            )
            frozen_errors = [
                abs(finite_float(row["fd_minus_frozen"]))
                for row in step_rows
                if with_frozen_recompute
            ]
            adaptive_drifts = [
                abs(finite_float(row["adaptive_drift"]))
                for row in step_rows
                if with_actual_recompute and with_frozen_recompute
            ]
            fd_state = int(top_fd["candidate_state"]) if top_fd else None
            actual_best = finite_float(top_actual["actual_recompute_score"]) if top_actual else float("nan")
            top_fd_row = row_for_state(step_rows, fd_state)
            actual_at_fd = (
                finite_float(top_fd_row.get("actual_recompute_score"), default=float("nan"))
                if top_fd_row is not None
                else float("nan")
            )
            sorted_fd = sorted(
                step_rows,
                key=lambda row: (
                    finite_float(row["bits_fd_operator_score"], default=-float("inf")),
                    -int(row["candidate_state"]),
                ),
                reverse=True,
            )
            fd_margin = (
                finite_float(sorted_fd[0]["bits_fd_operator_score"])
                - finite_float(sorted_fd[1]["bits_fd_operator_score"])
                if len(sorted_fd) >= 2
                else None
            )
            epsilon_adapt = max(adaptive_drifts) if adaptive_drifts else None
            stability_condition = (
                fd_margin is not None
                and epsilon_adapt is not None
                and fd_margin > 2.0 * epsilon_adapt
            )
            actual_match_fd = (
                (int(top_actual["candidate_state"]) == fd_state)
                if with_actual_recompute and top_actual is not None and fd_state is not None
                else None
            )
            baseline_tops = {
                "raw_hidden": (top_raw_hidden, "raw_hidden_score"),
                "random": (top_random, "random_score"),
                "spectral": (top_spectral, "spectral_score"),
                "betweenness": (top_betweenness, "betweenness_score"),
                "value_gradient": (top_value_gradient, "value_gradient_score"),
                "degree": (top_degree, "degree_score"),
            }
            baseline_summary: Dict[str, object] = {}
            for baseline_name, (baseline_top, baseline_field) in baseline_tops.items():
                baseline_summary[f"top_{baseline_name}_state"] = (
                    int(baseline_top["candidate_state"]) if baseline_top else None
                )
                baseline_summary[f"top_{baseline_name}_match_fd"] = (
                    int(baseline_top["candidate_state"]) == fd_state
                    if baseline_top is not None and fd_state is not None
                    else None
                )
                baseline_summary[f"tau_{baseline_name}_vs_fd"] = kendall_tau(
                    step_rows,
                    "bits_fd_operator_score",
                    baseline_field,
                )
                baseline_summary[f"actual_regret_{baseline_name}"] = actual_regret_for_choice(
                    step_rows,
                    baseline_top,
                    actual_best,
                )
            baseline_summary["time_base_eval_sec"] = (
                finite_float(step_rows[0].get("time_base_eval_sec")) if step_rows else 0.0
            )
            baseline_summary["time_operator_score_sec"] = (
                finite_float(step_rows[0].get("time_operator_score_sec")) if step_rows else 0.0
            )
            baseline_summary["time_recompute_total_sec"] = (
                finite_float(step_rows[0].get("time_recompute_total_sec")) if step_rows else 0.0
            )
            baseline_summary["recompute_speedup_proxy"] = (
                finite_float(step_rows[0].get("recompute_speedup_proxy"), default=float("nan"))
                if step_rows
                else float("nan")
            )
            summary_rows.append(
                {
                    "map": map_label,
                    "step": step,
                    "n_boundary": len(boundary),
                    "n_candidates": len(step_rows),
                    "n_edges_valid": int(base_row["n_edges_valid"]),
                    "n_active_edges": len(active_edges(edge_rows, args.edge_weight)),
                    "top_fd_state": int(top_fd["candidate_state"]) if top_fd else None,
                    "top_fd_coord": top_fd["candidate_coord"] if top_fd else None,
                    "top_fd_score": finite_float(top_fd["bits_fd_operator_score"]) if top_fd else 0.0,
                    "fd_margin": fd_margin,
                    "epsilon_adapt_observed": epsilon_adapt,
                    "margin_stability_condition": stability_condition,
                    "margin_stability_correct": (
                        (actual_match_fd is True)
                        if stability_condition and actual_match_fd is not None
                        else None
                    ),
                    "top_grad_state": int(top_grad["candidate_state"]) if top_grad else None,
                    "top_grad_match_fd": (
                        int(top_grad["candidate_state"]) == int(top_fd["candidate_state"])
                        if top_fd and top_grad
                        else False
                    ),
                    "top_frozen_state": int(top_frozen["candidate_state"]) if top_frozen else None,
                    "top_frozen_match_fd": (
                        (int(top_frozen["candidate_state"]) == int(top_fd["candidate_state"]))
                        if with_frozen_recompute and top_fd and top_frozen
                        else None
                    ),
                    "top_rate_only_state": int(top_rate["candidate_state"]) if top_rate else None,
                    "top_rate_only_match_fd": (
                        int(top_rate["candidate_state"]) == int(top_fd["candidate_state"])
                        if top_fd and top_rate
                        else None
                    ),
                    "top_occupancy_only_state": int(top_occupancy["candidate_state"]) if top_occupancy else None,
                    "top_occupancy_only_match_fd": (
                        int(top_occupancy["candidate_state"]) == int(top_fd["candidate_state"])
                        if top_fd and top_occupancy
                        else None
                    ),
                    "top_edge_only_state": int(top_edge["candidate_state"]) if top_edge else None,
                    "top_edge_only_match_fd": (
                        int(top_edge["candidate_state"]) == int(top_fd["candidate_state"])
                        if top_fd and top_edge
                        else None
                    ),
                    "top_edge_option_uniform_state": (
                        int(top_edge_option["candidate_state"]) if top_edge_option else None
                    ),
                    "top_edge_option_uniform_match_fd": (
                        int(top_edge_option["candidate_state"]) == int(top_fd["candidate_state"])
                        if top_fd and top_edge_option
                        else None
                    ),
                    "top_actual_state": int(top_actual["candidate_state"]) if top_actual else None,
                    "top_actual_match_fd": (
                        actual_match_fd
                    ),
                    **baseline_summary,
                    "tau_rate_only_vs_fd": kendall_tau(step_rows, "bits_fd_operator_score", "rate_only_score"),
                    "tau_occupancy_only_vs_fd": kendall_tau(
                        step_rows,
                        "bits_fd_operator_score",
                        "occupancy_only_score",
                    ),
                    "tau_edge_only_vs_fd": kendall_tau(step_rows, "bits_fd_operator_score", "edge_only_score"),
                    "tau_edge_option_uniform_vs_fd": kendall_tau(
                        step_rows,
                        "bits_fd_operator_score",
                        "edge_option_uniform_score",
                    ),
                    "tau_actual_vs_fd": kendall_tau(step_rows, "bits_fd_operator_score", "actual_recompute_score"),
                    "actual_regret_of_fd": (
                        actual_best - actual_at_fd
                        if math.isfinite(actual_best) and math.isfinite(actual_at_fd)
                        else None
                    ),
                    "mean_grad_abs_error": mean_grad_error,
                    "max_grad_error_to_bound_ratio": max_bound_ratio,
                    "max_abs_fd_minus_frozen": max(frozen_errors) if frozen_errors else None,
                    "mean_abs_fd_minus_frozen": (
                        float(np.mean(frozen_errors)) if frozen_errors else None
                    ),
                    "max_abs_adaptive_drift": max(adaptive_drifts) if adaptive_drifts else None,
                    "mean_abs_adaptive_drift": (
                        float(np.mean(adaptive_drifts)) if adaptive_drifts else None
                    ),
                    "selected_sequence": list(selected_sequence),
                }
            )
            if step >= args.max_steps or top_fd is None:
                break
            if args.greedy_positive_only and finite_float(top_fd["bits_fd_operator_score"]) <= 0.0:
                break
            split_state = int(top_fd["candidate_state"])
            if split_state in set(boundary):
                break
            boundary = sorted(set(boundary).union({split_state}))
            selected_sequence.append(split_state)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    trunc_summary_rows = aggregate_truncation(trunc_rows)
    runtime_summary_rows = runtime_rows(summary_rows, trunc_summary_rows)
    write_csv(args.out_dir / "operator_marginals.csv", marginal_rows)
    write_csv(args.out_dir / "truncated_green.csv", trunc_rows)
    write_csv(args.out_dir / "truncation_summary.csv", trunc_summary_rows)
    write_csv(args.out_dir / "runtime_summary.csv", runtime_summary_rows)
    write_csv(args.out_dir / "summary.csv", summary_rows)
    (args.out_dir / "operator_marginals.json").write_text(
        json.dumps(marginal_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# RD Boundary Green Operator Checks\n\n"
        f"- recipe: `{args.recipe}`\n"
        f"- lambda_struct: {args.lambda_struct}\n"
        f"- edge_weight: `{args.edge_weight}`\n"
        f"- with_frozen_recompute: {with_frozen_recompute}\n"
        f"- with_actual_recompute: {with_actual_recompute}\n"
        f"- with_recompute_modes: {args.with_recompute_modes}\n"
        f"- elapsed_sec: {time.perf_counter() - started:.3f}\n\n"
        "## Step Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} step {row['step']}: "
                f"top_fd={row['top_fd_state']} {row['top_fd_coord']} "
                f"score={float(row['top_fd_score']):.4g}, "
                f"margin={row['fd_margin']}, "
                f"eps_adapt={row['epsilon_adapt_observed']}, "
                f"stable_if_margin={row['margin_stability_condition']}, "
                f"stable_ok={row['margin_stability_correct']}, "
                f"grad_match={row['top_grad_match_fd']}, "
                f"frozen_match={row['top_frozen_match_fd']}, "
                f"actual_match={row['top_actual_match_fd']}, "
                f"mean_grad_error={float(row['mean_grad_abs_error']):.3g}, "
                f"max_fd_minus_frozen={row['max_abs_fd_minus_frozen']}, "
                f"max_adaptive_drift={row['max_abs_adaptive_drift']}, "
                f"actual_regret_fd={row['actual_regret_of_fd']}"
            )
            for row in summary_rows
        )
        + "\n\n## Baseline Ranking Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} step {row['step']}: "
                f"raw={row['top_raw_hidden_state']} match={row['top_raw_hidden_match_fd']} "
                f"regret={row['actual_regret_raw_hidden']}, "
                f"spectral={row['top_spectral_state']} match={row['top_spectral_match_fd']} "
                f"regret={row['actual_regret_spectral']}, "
                f"betweenness={row['top_betweenness_state']} match={row['top_betweenness_match_fd']} "
                f"regret={row['actual_regret_betweenness']}, "
                f"value_grad={row['top_value_gradient_state']} match={row['top_value_gradient_match_fd']} "
                f"regret={row['actual_regret_value_gradient']}, "
                f"random={row['top_random_state']} match={row['top_random_match_fd']} "
                f"regret={row['actual_regret_random']}"
            )
            for row in summary_rows
        )
        + "\n\n## Runtime Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} step {row['step']}: "
                f"base_eval={float(row['time_base_eval_sec']):.4g}s, "
                f"fd_grad_score={float(row['time_operator_score_sec']):.4g}s, "
                f"actual_recompute={float(row['time_recompute_total_sec']):.4g}s, "
                f"recompute_over_operator={row['recompute_speedup_proxy']}"
            )
            for row in summary_rows
        )
        + (
            "\n\n## Recompute Mode Summary\n\n"
            + "\n".join(
                (
                    f"- {row['map']} step {row['step']}: "
                    f"rate_match={row['top_rate_only_match_fd']}, "
                    f"occ_match={row['top_occupancy_only_match_fd']}, "
                    f"edge_match={row['top_edge_only_match_fd']}, "
                    f"edge_option_match={row['top_edge_option_uniform_match_fd']}, "
                    f"tau_actual={row['tau_actual_vs_fd']}"
                )
                for row in summary_rows
            )
            if args.with_recompute_modes
            else ""
        )
        + "\n\n## Truncation Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} K={row['k_steps']}: "
                f"top1_match_rate={float(row['top1_match_rate']):.3g}, "
                f"mean_abs_error={float(row['mean_abs_score_error']):.3g}, "
                f"mean_time={float(row['mean_time_truncated_green_sec']):.4g}s"
            )
            for row in trunc_summary_rows
            if int(row["k_steps"]) in {4, 8, 16, 32}
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
