#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import (
    GridWorld,
    endpoint_boundary_states,
    first_hit_green_state,
    shortest_path_distance_matrix,
    shortest_path_policy_to_target,
    transition_matrix_for_policy,
)
from compression_experiment_utils import parse_map_specs
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_rd_multiprobe_basis import (
    aggregate_probe_metrics,
    build_probe_context,
    evaluate_probe,
    fixed_basis,
    json_default,
    select_boundary,
    tail_cvar,
    write_csv,
)
from run_rd_operator_theorem_checks import (
    active_edges,
    evaluate_recipe_boundary,
    finite_float,
    operator_marginal_rows,
    phi_bits,
)


def _round_key(value: float) -> float:
    return round(float(value), 12)


def _recipe_signature(recipe: Mapping[str, object]) -> str:
    return json.dumps(recipe, sort_keys=True, default=json_default)


@dataclass
class ProbeDeltaRecord:
    before_bits: float
    deltas_by_state: Dict[int, float]
    n_candidates: int
    context_build_time_sec: float
    green_kernel_time_sec: float
    operator_delta_time_sec: float
    recompute_time_sec: float
    call_overhead_time_sec: float
    total_uncached_time_sec: float


@dataclass
class ActiveWeightRecord:
    weights_by_edge: Dict[Tuple[int, int], float]
    n_active_edges: int
    eval_time_sec: float


@dataclass
class ProbeDeltaCache:
    enabled: bool = True
    records: Dict[Tuple[object, ...], ProbeDeltaRecord] = field(default_factory=dict)
    active_weight_records: Dict[Tuple[object, ...], ActiveWeightRecord] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0
    probe_calls: int = 0
    active_weight_hits: int = 0
    active_weight_misses: int = 0
    context_build_time_sec: float = 0.0
    green_kernel_time_sec: float = 0.0
    operator_delta_time_sec: float = 0.0
    recompute_time_sec: float = 0.0
    call_overhead_time_sec: float = 0.0
    active_weight_time_sec: float = 0.0
    candidate_score_time_sec: float = 0.0
    beam_expansion_time_sec: float = 0.0

    def key(
        self,
        *,
        map_name: str,
        rows: Tuple[str, ...],
        recipe: Mapping[str, object],
        basis: Sequence[int],
        boundary: Sequence[int],
        probe: str,
        gamma: float,
        slip: float,
        lambda_struct: float,
        edge_weight: str,
        probe_top_fraction: float,
        max_candidates: int,
        delta_backend: str = "operator",
    ) -> Tuple[object, ...]:
        return (
            map_name,
            tuple(rows),
            _recipe_signature(recipe),
            tuple(sorted(int(state) for state in basis)),
            tuple(sorted(int(state) for state in boundary)),
            str(probe),
            _round_key(gamma),
            _round_key(slip),
            _round_key(lambda_struct),
            str(edge_weight),
            _round_key(probe_top_fraction),
            int(max_candidates),
            str(delta_backend),
        )

    def active_weight_key(
        self,
        *,
        map_name: str,
        rows: Tuple[str, ...],
        recipe: Mapping[str, object],
        basis: Sequence[int],
        boundary: Sequence[int],
        gamma: float,
        slip: float,
        edge_weight: str,
        probe_top_fraction: float,
    ) -> Tuple[object, ...]:
        return (
            "active_weight",
            map_name,
            tuple(rows),
            _recipe_signature(recipe),
            tuple(sorted(int(state) for state in basis)),
            tuple(sorted(int(state) for state in boundary)),
            _round_key(gamma),
            _round_key(slip),
            str(edge_weight),
            _round_key(probe_top_fraction),
        )

    def get(self, key: Tuple[object, ...]) -> ProbeDeltaRecord | None:
        self.probe_calls += 1
        if not self.enabled:
            self.misses += 1
            return None
        record = self.records.get(key)
        if record is None:
            self.misses += 1
        else:
            self.hits += 1
        return record

    def get_active_weights(self, key: Tuple[object, ...]) -> ActiveWeightRecord | None:
        if not self.enabled:
            self.active_weight_misses += 1
            return None
        record = self.active_weight_records.get(key)
        if record is None:
            self.active_weight_misses += 1
        else:
            self.active_weight_hits += 1
        return record

    def put(self, key: Tuple[object, ...], record: ProbeDeltaRecord) -> None:
        if self.enabled:
            self.records[key] = record
        self.context_build_time_sec += float(record.context_build_time_sec)
        self.green_kernel_time_sec += float(record.green_kernel_time_sec)
        self.operator_delta_time_sec += float(record.operator_delta_time_sec)
        self.recompute_time_sec += float(record.recompute_time_sec)
        self.call_overhead_time_sec += float(record.call_overhead_time_sec)

    def put_active_weights(self, key: Tuple[object, ...], record: ActiveWeightRecord) -> None:
        if self.enabled:
            self.active_weight_records[key] = record
        self.active_weight_time_sec += float(record.eval_time_sec)

    def summary(self) -> Dict[str, object]:
        hit_rate = self.hits / max(1, self.hits + self.misses)
        active_weight_hit_rate = self.active_weight_hits / max(
            1,
            self.active_weight_hits + self.active_weight_misses,
        )
        profiled = (
            self.context_build_time_sec
            + self.green_kernel_time_sec
            + self.operator_delta_time_sec
            + self.recompute_time_sec
            + self.call_overhead_time_sec
            + self.active_weight_time_sec
            + self.candidate_score_time_sec
            + self.beam_expansion_time_sec
        )
        uncached_probe = (
            self.context_build_time_sec
            + self.green_kernel_time_sec
            + self.operator_delta_time_sec
            + self.recompute_time_sec
            + self.call_overhead_time_sec
        )
        return {
            "probe_cache_enabled": bool(self.enabled),
            "probe_cache_hits": int(self.hits),
            "probe_cache_misses": int(self.misses),
            "probe_cache_hit_rate": float(hit_rate),
            "probe_calls": int(self.probe_calls),
            "unique_probe_evals": int(len(self.records)) if self.enabled else int(self.misses),
            "active_weight_cache_hits": int(self.active_weight_hits),
            "active_weight_cache_misses": int(self.active_weight_misses),
            "active_weight_cache_hit_rate": float(active_weight_hit_rate),
            "active_weight_unique_evals": int(len(self.active_weight_records))
            if self.enabled
            else int(self.active_weight_misses),
            "active_weight_time_sec": float(self.active_weight_time_sec),
            "probe_context_build_time_sec": float(self.context_build_time_sec),
            "probe_green_kernel_time_sec": float(self.green_kernel_time_sec),
            "probe_operator_delta_time_sec": float(self.operator_delta_time_sec),
            "probe_recompute_time_sec": float(self.recompute_time_sec),
            "probe_call_overhead_time_sec": float(self.call_overhead_time_sec),
            "candidate_score_time_sec": float(self.candidate_score_time_sec),
            "beam_expansion_time_sec": float(self.beam_expansion_time_sec),
            "profiled_selection_time_sec": float(profiled),
            "uncached_probe_eval_time_sec": float(uncached_probe),
        }


def parse_group_specs(specs: Sequence[str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Lens group must have form name:probe,probe: {spec!r}")
        name, raw_probes = spec.split(":", 1)
        probes = [probe.strip() for probe in raw_probes.split(",") if probe.strip()]
        if not probes:
            raise ValueError(f"Lens group {name!r} has no probes.")
        groups[name.strip()] = probes
    return groups


def group_risk(values: Sequence[float], kind: str, cvar_alpha: float) -> float:
    if not values:
        return 0.0
    if kind == "mean":
        return float(np.mean(values))
    if kind == "max":
        return max(float(value) for value in values)
    if kind == "cvar":
        return tail_cvar([float(value) for value in values], alpha=cvar_alpha)
    raise ValueError(f"Unknown group risk kind: {kind}")


def group_risks_from_probe_values(
    probe_values: Mapping[str, float],
    lens_groups: Mapping[str, Sequence[str]],
    group_risk_kind: str,
    cvar_alpha: float,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for group_name, probes in lens_groups.items():
        values = [float(probe_values.get(probe, 0.0)) for probe in probes]
        out[group_name] = group_risk(values, kind=group_risk_kind, cvar_alpha=cvar_alpha)
    return out


def _green_row_position(green: object, state: int) -> int | None:
    interior = getattr(green, "interior")
    matches = np.flatnonzero(interior == int(state))
    if len(matches) == 0:
        return None
    return int(matches[0])


def _green_hidden_mass(green: object, start_state: int, visible_boundary: Sequence[int]) -> float:
    row_pos = _green_row_position(green, int(start_state))
    if row_pos is None:
        return 0.0
    visible = set(int(state) for state in visible_boundary)
    terminals = getattr(green, "terminals")
    hit_probability = getattr(green, "hit_probability")
    mass = 0.0
    for col, terminal in enumerate(terminals.tolist()):
        if int(terminal) not in visible:
            mass += finite_float(hit_probability[row_pos, col])
    return max(0.0, mass)


def _green_terminal_probability(green: object, start_state: int, terminal_state: int) -> float:
    row_pos = _green_row_position(green, int(start_state))
    if row_pos is None:
        return 0.0
    terminals = getattr(green, "terminals")
    matches = np.flatnonzero(terminals == int(terminal_state))
    if len(matches) == 0:
        return 0.0
    return finite_float(getattr(green, "hit_probability")[row_pos, int(matches[0])])


def active_weight_table_for_boundary(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    weight_probe: str,
    gamma: float,
    slip: float,
    edge_weight: str,
    probe_top_fraction: float,
) -> ActiveWeightRecord:
    started = time.perf_counter()
    context = build_probe_context(
        rows,
        recipe=recipe,
        fixed_candidate_basis=basis,
        residual_kind=weight_probe,
        gamma=gamma,
        slip=slip,
        probe_top_fraction=probe_top_fraction,
    )
    _weight_row, weight_edges = evaluate_recipe_boundary(
        map_name=map_name,
        context=context,
        recipe=recipe,
        boundary=boundary,
        gamma=gamma,
        slip=slip,
    )
    weights_by_edge = {
        (int(edge_row["src_state"]), int(edge_row["target_state"])): float(weight)
        for edge_row, weight in active_edges(weight_edges, edge_weight=edge_weight)
        if float(weight) > 1e-12
    }
    return ActiveWeightRecord(
        weights_by_edge=weights_by_edge,
        n_active_edges=len(weights_by_edge),
        eval_time_sec=time.perf_counter() - started,
    )


def probe_delta_table_insertion_score(
    map_name: str,
    step: int,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    probe: str,
    gamma: float,
    slip: float,
    probe_top_fraction: float,
    active_weight_by_edge: Mapping[Tuple[int, int], float] | None = None,
) -> ProbeDeltaRecord:
    started = time.perf_counter()
    context_start = time.perf_counter()
    context = build_probe_context(
        rows,
        recipe=recipe,
        fixed_candidate_basis=basis,
        residual_kind=probe,
        gamma=gamma,
        slip=slip,
        probe_top_fraction=probe_top_fraction,
    )
    context_time = time.perf_counter() - context_start
    grid: GridWorld = context["grid"]  # type: ignore[assignment]
    boundary = sorted(set(int(state) for state in boundary))
    basis_set = set(int(state) for state in basis)
    residual_base = set(int(state) for state in context["residual_boundary"])  # type: ignore[index]
    candidate_states = sorted(basis_set - set(boundary))
    distances = shortest_path_distance_matrix(grid)
    hidden_threshold = 1e-6
    local_horizon = 999.0

    edge_records: List[Dict[str, object]] = []
    green_time = 0.0
    score_time = 0.0
    for target_state in boundary:
        policy = shortest_path_policy_to_target(grid, int(target_state), slip=slip)
        P_free, _r_free = transition_matrix_for_policy(grid, policy, absorbing=[])
        for src_state in boundary:
            if int(src_state) == int(target_state):
                continue
            candidate_terminals = sorted(basis_set - {int(src_state)})
            green_start = time.perf_counter()
            candidate_green = first_hit_green_state(P_free, candidate_terminals)
            residual_terminals = sorted((residual_base.union(boundary)) - {int(src_state)})
            residual_green = first_hit_green_state(P_free, residual_terminals)
            green_time += time.perf_counter() - green_start

            score_start = time.perf_counter()
            candidate_hidden_mass = _green_hidden_mass(candidate_green, int(src_state), boundary)
            within_horizon = float(distances[int(src_state), int(target_state)]) <= local_horizon
            edge_valid = bool(within_horizon and candidate_hidden_mass <= hidden_threshold)
            before_mass = _green_hidden_mass(residual_green, int(src_state), boundary)
            before_bits = phi_bits(before_mass)
            terminal_set = set(int(term) for term in residual_green.terminals.tolist())
            interior_pos = {
                int(state): pos
                for pos, state in enumerate(residual_green.interior.tolist())
            }
            src_pos = _green_row_position(residual_green, int(src_state))
            candidate_after_bits: Dict[int, float] = {}
            for candidate in candidate_states:
                candidate = int(candidate)
                if candidate in terminal_set:
                    after_mass = max(
                        0.0,
                        before_mass - _green_terminal_probability(residual_green, int(src_state), candidate),
                    )
                else:
                    candidate_pos = interior_pos.get(candidate)
                    if src_pos is None or candidate_pos is None:
                        after_mass = before_mass
                    else:
                        pivot = finite_float(residual_green.fundamental[candidate_pos, candidate_pos])
                        if abs(pivot) <= 1e-300:
                            after_mass = before_mass
                        else:
                            p_hit_candidate = finite_float(
                                residual_green.fundamental[src_pos, candidate_pos],
                            ) / pivot
                            candidate_hidden = _green_hidden_mass(residual_green, candidate, boundary)
                            after_mass = max(0.0, before_mass - p_hit_candidate * candidate_hidden)
                candidate_after_bits[candidate] = phi_bits(after_mass)
            score_time += time.perf_counter() - score_start
            edge_records.append(
                {
                    "edge_key": (int(src_state), int(target_state)),
                    "edge_valid": edge_valid,
                    "before_bits": before_bits,
                    "candidate_after_bits": candidate_after_bits,
                }
            )

    if active_weight_by_edge is None:
        valid_records = [row for row in edge_records if bool(row["edge_valid"])]
        active_records = [(row, 1.0) for row in (valid_records if valid_records else edge_records)]
    else:
        active_records = [
            (row, float(active_weight_by_edge[tuple(row["edge_key"])]))  # type: ignore[arg-type]
            for row in edge_records
            if tuple(row["edge_key"]) in active_weight_by_edge
        ]
    before_bits_total = float(sum(weight * finite_float(row["before_bits"]) for row, weight in active_records))
    deltas_by_state: Dict[int, float] = {}
    for candidate in candidate_states:
        delta = 0.0
        for row, weight in active_records:
            after_bits = row["candidate_after_bits"][int(candidate)]  # type: ignore[index]
            delta += weight * (finite_float(row["before_bits"]) - finite_float(after_bits))
        deltas_by_state[int(candidate)] = max(0.0, float(delta))

    return ProbeDeltaRecord(
        before_bits=max(0.0, before_bits_total),
        deltas_by_state=deltas_by_state,
        n_candidates=len(candidate_states),
        context_build_time_sec=context_time,
        green_kernel_time_sec=green_time,
        operator_delta_time_sec=score_time,
        recompute_time_sec=0.0,
        call_overhead_time_sec=max(0.0, time.perf_counter() - started - context_time - green_time - score_time),
        total_uncached_time_sec=time.perf_counter() - started,
    )


def probe_delta_table(
    map_name: str,
    step: int,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    probes: Sequence[str],
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    probe_top_fraction: float,
    max_candidates: int = 0,
    probe_cache: ProbeDeltaCache | None = None,
    delta_backend: str = "operator",
) -> Tuple[Dict[str, float], Dict[int, Dict[str, float]], List[Dict[str, object]]]:
    before_by_probe: Dict[str, float] = {}
    deltas_by_state: Dict[int, Dict[str, float]] = {}
    diagnostics: List[Dict[str, object]] = []
    active_weight_record: ActiveWeightRecord | None = None
    active_weight_cache_hit = False
    if delta_backend == "insertion_score" and edge_weight != "uniform":
        weight_cache_key = (
            probe_cache.active_weight_key(
                map_name=map_name,
                rows=rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                gamma=gamma,
                slip=slip,
                edge_weight=edge_weight,
                probe_top_fraction=probe_top_fraction,
            )
            if probe_cache is not None
            else None
        )
        active_weight_record = (
            probe_cache.get_active_weights(weight_cache_key)
            if probe_cache is not None and weight_cache_key is not None
            else None
        )
        active_weight_cache_hit = active_weight_record is not None
        if active_weight_record is None:
            active_weight_record = active_weight_table_for_boundary(
                map_name=map_name,
                rows=rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                weight_probe=str(probes[0]) if probes else "none",
                gamma=gamma,
                slip=slip,
                edge_weight=edge_weight,
                probe_top_fraction=probe_top_fraction,
            )
            if probe_cache is not None and weight_cache_key is not None:
                probe_cache.put_active_weights(weight_cache_key, active_weight_record)
    for probe_index, probe in enumerate(probes):
        cache_key = (
            probe_cache.key(
                map_name=map_name,
                rows=rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                probe=probe,
                gamma=gamma,
                slip=slip,
                lambda_struct=lambda_struct,
                edge_weight=edge_weight,
                probe_top_fraction=probe_top_fraction,
                max_candidates=max_candidates,
                delta_backend=delta_backend,
            )
            if probe_cache is not None
            else None
        )
        record = probe_cache.get(cache_key) if probe_cache is not None and cache_key is not None else None
        cache_hit = record is not None
        if record is None:
            if delta_backend == "insertion_score":
                record = probe_delta_table_insertion_score(
                    map_name=map_name,
                    step=step,
                    rows=rows,
                    recipe=recipe,
                    basis=basis,
                    boundary=boundary,
                    probe=probe,
                    gamma=gamma,
                    slip=slip,
                    probe_top_fraction=probe_top_fraction,
                    active_weight_by_edge=(
                        active_weight_record.weights_by_edge
                        if active_weight_record is not None
                        else None
                    ),
                )
            else:
                context_start = time.perf_counter()
                context = build_probe_context(
                    rows,
                    recipe=recipe,
                    fixed_candidate_basis=basis,
                    residual_kind=probe,
                    gamma=gamma,
                    slip=slip,
                    probe_top_fraction=probe_top_fraction,
                )
                context_time = time.perf_counter() - context_start
                call_start = time.perf_counter()
                step_rows, _base_row, _edge_rows = operator_marginal_rows(
                    map_name=map_name,
                    step=step,
                    context=context,
                    recipe=recipe,
                    boundary=boundary,
                    gamma=gamma,
                    slip=slip,
                    lambda_struct=lambda_struct,
                    edge_weight=edge_weight,
                    max_candidates=max_candidates,
                    with_frozen_recompute=True,
                    with_actual_recompute=False,
                    with_recompute_modes=False,
                )
                call_time = time.perf_counter() - call_start
                before = finite_float(step_rows[0].get("frozen_bits_before")) if step_rows else 0.0
                deltas = {
                    int(row["candidate_state"]): max(0.0, finite_float(row.get("bits_fd_delta")))
                    for row in step_rows
                }
                green_time = finite_float(step_rows[0].get("time_base_eval_sec")) if step_rows else call_time
                operator_time = finite_float(step_rows[0].get("time_operator_score_sec")) if step_rows else 0.0
                recompute_time = finite_float(step_rows[0].get("time_recompute_total_sec")) if step_rows else 0.0
                overhead_time = max(0.0, call_time - green_time - operator_time - recompute_time)
                record = ProbeDeltaRecord(
                    before_bits=max(0.0, before),
                    deltas_by_state=deltas,
                    n_candidates=len(step_rows),
                    context_build_time_sec=context_time,
                    green_kernel_time_sec=green_time,
                    operator_delta_time_sec=operator_time,
                    recompute_time_sec=recompute_time,
                    call_overhead_time_sec=overhead_time,
                    total_uncached_time_sec=context_time + call_time,
                )
            if probe_cache is not None and cache_key is not None:
                probe_cache.put(cache_key, record)
        before_by_probe[probe] = max(0.0, record.before_bits)
        for state, delta in record.deltas_by_state.items():
            deltas_by_state.setdefault(int(state), {})[probe] = max(0.0, float(delta))
        diagnostics.append(
            {
                "map": map_name,
                "step": step,
                "probe": probe,
                "n_boundary": len(boundary),
                "n_basis": len(basis),
                "distortion_before_bits": max(0.0, record.before_bits),
                "n_candidates": int(record.n_candidates),
                "cache_hit": bool(cache_hit),
                "context_build_time_sec": float(record.context_build_time_sec) if not cache_hit else 0.0,
                "green_kernel_time_sec": float(record.green_kernel_time_sec) if not cache_hit else 0.0,
                "operator_delta_time_sec": float(record.operator_delta_time_sec) if not cache_hit else 0.0,
                "probe_uncached_time_sec": float(record.total_uncached_time_sec) if not cache_hit else 0.0,
                "active_weight_cache_hit": bool(active_weight_cache_hit),
                "active_weight_time_sec": (
                    float(active_weight_record.eval_time_sec)
                    if active_weight_record is not None and not active_weight_cache_hit and probe_index == 0
                    else 0.0
                ),
                "n_active_weight_edges": int(active_weight_record.n_active_edges)
                if active_weight_record is not None
                else 0,
                "delta_backend": delta_backend,
            }
        )
    return before_by_probe, deltas_by_state, diagnostics


def score_candidates(
    map_name: str,
    step: int,
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    before_by_probe: Mapping[str, float],
    deltas_by_state: Mapping[int, Mapping[str, float]],
    group_risk_kind: str,
    cvar_alpha: float,
    score_mode: str,
    rate_tie_break: float,
) -> Tuple[List[Dict[str, object]], Dict[str, float], Dict[str, float]]:
    current_group_risks = group_risks_from_probe_values(
        before_by_probe,
        lens_groups=lens_groups,
        group_risk_kind=group_risk_kind,
        cvar_alpha=cvar_alpha,
    )
    current_violations = {
        group: max(0.0, risk - float(budgets[group]))
        for group, risk in current_group_risks.items()
    }
    candidate_rows: List[Dict[str, object]] = []
    candidate_states = sorted(set(basis) - set(boundary))
    probe_order = sorted(before_by_probe)
    probe_index = {probe: pos for pos, probe in enumerate(probe_order)}
    before_vector = np.asarray([float(before_by_probe[probe]) for probe in probe_order], dtype=float)
    delta_matrix = np.zeros((len(candidate_states), len(probe_order)), dtype=float)
    for state_pos, state in enumerate(candidate_states):
        for probe, delta in deltas_by_state.get(int(state), {}).items():
            probe_pos = probe_index.get(probe)
            if probe_pos is not None:
                delta_matrix[state_pos, probe_pos] = float(delta)
    after_matrix = np.maximum(0.0, before_vector[None, :] - delta_matrix) if candidate_states else np.zeros((0, len(probe_order)))

    def group_risk_vector(probes: Sequence[str]) -> np.ndarray:
        positions = [probe_index[probe] for probe in probes if probe in probe_index]
        if not positions:
            return np.zeros(len(candidate_states), dtype=float)
        values = after_matrix[:, positions]
        if group_risk_kind == "mean":
            return np.mean(values, axis=1)
        if group_risk_kind == "max":
            return np.max(values, axis=1)
        if group_risk_kind == "cvar":
            sorted_values = np.sort(values, axis=1)
            start = min(len(positions) - 1, int(np.floor(cvar_alpha * len(positions))))
            return np.mean(sorted_values[:, start:], axis=1)
        raise ValueError(f"Unknown group risk kind: {group_risk_kind}")

    after_group_risk_arrays = {
        group: group_risk_vector(probes)
        for group, probes in lens_groups.items()
    }
    after_violation_arrays = {
        group: np.maximum(0.0, risks - float(budgets[group]))
        for group, risks in after_group_risk_arrays.items()
    }
    violation_before = sum(current_violations.values())
    if after_violation_arrays:
        violation_after_values = np.sum(np.vstack(list(after_violation_arrays.values())), axis=0)
        max_after_violation_values = np.max(np.vstack(list(after_violation_arrays.values())), axis=0)
    else:
        violation_after_values = np.zeros(len(candidate_states), dtype=float)
        max_after_violation_values = np.zeros(len(candidate_states), dtype=float)
    if after_group_risk_arrays:
        max_after_risk_values = np.max(np.vstack(list(after_group_risk_arrays.values())), axis=0)
    else:
        max_after_risk_values = np.zeros(len(candidate_states), dtype=float)
    group_order = list(lens_groups.keys())
    group_improved_matrix = [
        after_violation_arrays[group] + 1e-12 < float(current_violations[group])
        for group in group_order
    ]
    if group_improved_matrix:
        groups_improved_values = np.sum(np.vstack(group_improved_matrix), axis=0)
    else:
        groups_improved_values = np.zeros(len(candidate_states), dtype=int)

    for state_pos, state in enumerate(candidate_states):
        after_group_risks = {
            group: float(after_group_risk_arrays[group][state_pos])
            for group in group_order
        }
        after_violations = {
            group: float(after_violation_arrays[group][state_pos])
            for group in group_order
        }
        violation_after = float(violation_after_values[state_pos])
        violation_reduction = float(violation_before - violation_after)
        groups_improved = int(groups_improved_values[state_pos])
        max_after_violation = float(max_after_violation_values[state_pos])
        max_after_risk = float(max_after_risk_values[state_pos])
        approx_rate_delta = math.log2(max(2, len(basis))) + 2.0 * max(1, len(boundary))
        if score_mode == "reduction":
            score = violation_reduction - rate_tie_break * approx_rate_delta
        elif score_mode == "reduction_per_rate":
            score = violation_reduction / max(1e-9, approx_rate_delta)
        elif score_mode == "lexicographic":
            score = -max_after_violation + 1e-6 * violation_reduction - rate_tie_break * approx_rate_delta
        else:
            raise ValueError(f"Unknown score mode: {score_mode}")
        candidate_rows.append(
            {
                "map": map_name,
                "step": step,
                "candidate_state": state,
                "n_boundary": len(boundary),
                "n_basis": len(basis),
                "score_mode": score_mode,
                "operator_score": score,
                "violation_before": violation_before,
                "violation_after": violation_after,
                "violation_reduction": violation_reduction,
                "groups_improved": groups_improved,
                "max_after_violation": max_after_violation,
                "max_after_group_risk": max_after_risk,
                "approx_rate_delta": approx_rate_delta,
                "group_risks_before": json.dumps(current_group_risks, sort_keys=True),
                "group_risks_after": json.dumps(after_group_risks, sort_keys=True),
                "group_violations_after": json.dumps(after_violations, sort_keys=True),
                "score_backend": "numpy_vectorized",
            }
        )
    candidate_rows.sort(
        key=lambda row: (
            float(row["operator_score"]),
            float(row["violation_reduction"]),
            int(row["groups_improved"]),
            -int(row["candidate_state"]),
        ),
        reverse=True,
    )
    for rank, row in enumerate(candidate_rows, start=1):
        row["rank"] = rank
    return candidate_rows, current_group_risks, current_violations


def select_group_constrained_boundary(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    probe_top_fraction: float,
    group_risk_kind: str,
    cvar_alpha: float,
    max_splits: int,
    score_mode: str,
    rate_tie_break: float,
    beam_width: int,
    beam_expand: int,
    probe_cache: ProbeDeltaCache | None = None,
    delta_backend: str = "operator",
) -> Tuple[List[int], List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], float]:
    if delta_backend not in {"operator", "insertion_score"}:
        raise ValueError(f"Unknown delta backend: {delta_backend}")
    if beam_width > 1:
        return select_group_constrained_boundary_beam(
            map_name=map_name,
            rows=rows,
            recipe=recipe,
            basis=basis,
            lens_groups=lens_groups,
            budgets=budgets,
            gamma=gamma,
            slip=slip,
            lambda_struct=lambda_struct,
            edge_weight=edge_weight,
            probe_top_fraction=probe_top_fraction,
            group_risk_kind=group_risk_kind,
            cvar_alpha=cvar_alpha,
            max_splits=max_splits,
            score_mode=score_mode,
            rate_tie_break=rate_tie_break,
            beam_width=beam_width,
            beam_expand=beam_expand,
            probe_cache=probe_cache,
            delta_backend=delta_backend,
        )
    all_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    boundary = sorted(set(endpoint_boundary_states(GridWorld(rows))).intersection(set(basis)))
    trace_rows: List[Dict[str, object]] = []
    candidate_rows: List[Dict[str, object]] = []
    probe_rows: List[Dict[str, object]] = []
    started = time.perf_counter()
    for step in range(max_splits + 1):
        before_by_probe, deltas_by_state, probe_diag = probe_delta_table(
            map_name=map_name,
            step=step,
            rows=rows,
            recipe=recipe,
            basis=basis,
            boundary=boundary,
            probes=all_probes,
            gamma=gamma,
            slip=slip,
            lambda_struct=lambda_struct,
            edge_weight=edge_weight,
            probe_top_fraction=probe_top_fraction,
            probe_cache=probe_cache,
            delta_backend=delta_backend,
        )
        probe_rows.extend(probe_diag)
        score_started = time.perf_counter()
        scored, group_risks, group_violations = score_candidates(
            map_name=map_name,
            step=step,
            basis=basis,
            boundary=boundary,
            lens_groups=lens_groups,
            budgets=budgets,
            before_by_probe=before_by_probe,
            deltas_by_state=deltas_by_state,
            group_risk_kind=group_risk_kind,
            cvar_alpha=cvar_alpha,
            score_mode=score_mode,
            rate_tie_break=rate_tie_break,
        )
        if probe_cache is not None:
            probe_cache.candidate_score_time_sec += time.perf_counter() - score_started
        candidate_rows.extend(scored)
        total_violation = sum(group_violations.values())
        max_violation = max(group_violations.values(), default=0.0)
        if total_violation <= 1e-9:
            trace_rows.append(
                {
                    "map": map_name,
                    "step": step,
                    "selected_state": None,
                    "stop_reason": "feasible",
                    "n_boundary": len(boundary),
                    "total_violation": total_violation,
                    "max_violation": max_violation,
                    "group_risks": json.dumps(group_risks, sort_keys=True),
                    "group_violations": json.dumps(group_violations, sort_keys=True),
                }
            )
            break
        if step >= max_splits or not scored:
            trace_rows.append(
                {
                    "map": map_name,
                    "step": step,
                    "selected_state": None,
                    "stop_reason": "budget_not_met",
                    "n_boundary": len(boundary),
                    "total_violation": total_violation,
                    "max_violation": max_violation,
                    "group_risks": json.dumps(group_risks, sort_keys=True),
                    "group_violations": json.dumps(group_violations, sort_keys=True),
                }
            )
            break
        best = scored[0]
        if float(best["violation_reduction"]) <= 1e-12:
            trace_rows.append(
                {
                    "map": map_name,
                    "step": step,
                    "selected_state": None,
                    "stop_reason": "no_positive_violation_reduction",
                    "n_boundary": len(boundary),
                    "total_violation": total_violation,
                    "max_violation": max_violation,
                    "group_risks": json.dumps(group_risks, sort_keys=True),
                    "group_violations": json.dumps(group_violations, sort_keys=True),
                }
            )
            break
        selected_state = int(best["candidate_state"])
        trace_rows.append(
            {
                "map": map_name,
                "step": step,
                "selected_state": selected_state,
                "stop_reason": "continue",
                "n_boundary": len(boundary),
                "operator_score": best["operator_score"],
                "violation_before": best["violation_before"],
                "violation_after": best["violation_after"],
                "violation_reduction": best["violation_reduction"],
                "groups_improved": best["groups_improved"],
                "total_violation": total_violation,
                "max_violation": max_violation,
                "group_risks": json.dumps(group_risks, sort_keys=True),
                "group_violations": json.dumps(group_violations, sort_keys=True),
            }
        )
        boundary = sorted(set(boundary).union({selected_state}))
    return boundary, trace_rows, candidate_rows, probe_rows, time.perf_counter() - started


def select_group_constrained_boundary_beam(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    probe_top_fraction: float,
    group_risk_kind: str,
    cvar_alpha: float,
    max_splits: int,
    score_mode: str,
    rate_tie_break: float,
    beam_width: int,
    beam_expand: int,
    probe_cache: ProbeDeltaCache | None = None,
    delta_backend: str = "operator",
) -> Tuple[List[int], List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], float]:
    if delta_backend not in {"operator", "insertion_score"}:
        raise ValueError(f"Unknown delta backend: {delta_backend}")
    all_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    start_boundary = tuple(sorted(set(endpoint_boundary_states(GridWorld(rows))).intersection(set(basis))))
    beam: List[Dict[str, object]] = [
        {
            "boundary": start_boundary,
            "path": [],
            "priority": (float("inf"), float("inf"), len(start_boundary), 0),
        }
    ]
    best_node = beam[0]
    best_total_violation = float("inf")
    best_group_risks: Dict[str, float] = {}
    best_group_violations: Dict[str, float] = {}
    trace_rows: List[Dict[str, object]] = []
    candidate_rows: List[Dict[str, object]] = []
    probe_rows: List[Dict[str, object]] = []
    started = time.perf_counter()
    final_stop = "budget_not_met"

    for depth in range(max_splits + 1):
        expanded_nodes: List[Dict[str, object]] = []
        for beam_id, node in enumerate(beam):
            boundary = list(node["boundary"])  # type: ignore[arg-type]
            before_by_probe, deltas_by_state, probe_diag = probe_delta_table(
                map_name=map_name,
                step=depth,
                rows=rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                probes=all_probes,
                gamma=gamma,
                slip=slip,
                lambda_struct=lambda_struct,
                edge_weight=edge_weight,
                probe_top_fraction=probe_top_fraction,
                probe_cache=probe_cache,
                delta_backend=delta_backend,
            )
            probe_rows.extend({**row, "beam_id": beam_id, "path": list(node["path"])} for row in probe_diag)
            score_started = time.perf_counter()
            scored, group_risks, group_violations = score_candidates(
                map_name=map_name,
                step=depth,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                before_by_probe=before_by_probe,
                deltas_by_state=deltas_by_state,
                group_risk_kind=group_risk_kind,
                cvar_alpha=cvar_alpha,
                score_mode=score_mode,
                rate_tie_break=rate_tie_break,
            )
            if probe_cache is not None:
                probe_cache.candidate_score_time_sec += time.perf_counter() - score_started
            candidate_rows.extend(
                {**row, "beam_id": beam_id, "path": list(node["path"])}
                for row in scored
            )
            total_violation = sum(group_violations.values())
            max_violation = max(group_violations.values(), default=0.0)
            if (
                total_violation < best_total_violation - 1e-12
                or (
                    abs(total_violation - best_total_violation) <= 1e-12
                    and len(boundary) < len(best_node["boundary"])  # type: ignore[arg-type]
                )
            ):
                best_total_violation = total_violation
                best_node = node
                best_group_risks = group_risks
                best_group_violations = group_violations
            if total_violation <= 1e-9:
                best_node = node
                best_group_risks = group_risks
                best_group_violations = group_violations
                final_stop = "feasible"
                expanded_nodes = []
                break
            if depth >= max_splits:
                continue
            expand_started = time.perf_counter()
            for row in scored[: max(1, beam_expand)]:
                state = int(row["candidate_state"])
                if state in set(boundary):
                    continue
                new_boundary = tuple(sorted(set(boundary).union({state})))
                new_path = list(node["path"]) + [state]  # type: ignore[operator]
                expanded_nodes.append(
                    {
                        "boundary": new_boundary,
                        "path": new_path,
                        "priority": (
                            float(row["violation_after"]),
                            float(row["max_after_violation"]),
                            len(new_boundary),
                            -float(row["violation_reduction"]),
                            state,
                        ),
                    }
                )
            if probe_cache is not None:
                probe_cache.beam_expansion_time_sec += time.perf_counter() - expand_started
        if final_stop == "feasible":
            break
        if depth >= max_splits:
            break
        if not expanded_nodes:
            final_stop = "beam_exhausted"
            break
        expanded_nodes.sort(key=lambda node: node["priority"])  # type: ignore[index]
        deduped: List[Dict[str, object]] = []
        seen = set()
        for node in expanded_nodes:
            boundary_key = tuple(node["boundary"])  # type: ignore[arg-type]
            if boundary_key in seen:
                continue
            seen.add(boundary_key)
            deduped.append(node)
            if len(deduped) >= max(1, beam_width):
                break
        beam = deduped

    final_boundary = list(best_node["boundary"])  # type: ignore[arg-type]
    path = list(best_node["path"])  # type: ignore[arg-type]
    for step, state in enumerate(path):
        trace_rows.append(
            {
                "map": map_name,
                "step": step,
                "selected_state": state,
                "stop_reason": "continue",
                "n_boundary": len(start_boundary) + step,
                "selection_mode": "beam",
                "beam_width": beam_width,
                "beam_expand": beam_expand,
            }
        )
    trace_rows.append(
        {
            "map": map_name,
            "step": len(path),
            "selected_state": None,
            "stop_reason": final_stop,
            "n_boundary": len(final_boundary),
            "selection_mode": "beam",
            "beam_width": beam_width,
            "beam_expand": beam_expand,
            "total_violation": best_total_violation,
            "max_violation": max(best_group_violations.values(), default=0.0),
            "group_risks": json.dumps(best_group_risks, sort_keys=True),
            "group_violations": json.dumps(best_group_violations, sort_keys=True),
        }
    )
    return final_boundary, trace_rows, candidate_rows, probe_rows, time.perf_counter() - started


def evaluate_boundary_on_groups(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    test_probes: Sequence[str],
    gamma: float,
    slip: float,
    edge_weight: str,
    probe_top_fraction: float,
    group_risk_kind: str,
    cvar_alpha: float,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    eval_rows: List[Dict[str, object]] = []
    probe_values: Dict[str, float] = {}
    all_train_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    for split_name, probes in [("train", all_train_probes), ("test", list(test_probes))]:
        for probe in probes:
            metrics = evaluate_probe(
                map_name=map_name,
                rows=rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                probe=probe,
                gamma=gamma,
                slip=slip,
                edge_weight=edge_weight,
                probe_top_fraction=probe_top_fraction,
            )
            if split_name == "train":
                probe_values[probe] = float(metrics["hidden_bits"])
            eval_rows.append(
                {
                    "map": map_name,
                    "split": split_name,
                    "probe": probe,
                    "n_boundary": len(boundary),
                    "n_basis": len(basis),
                    "boundary": list(boundary),
                    **metrics,
                }
            )
    group_risks = group_risks_from_probe_values(
        probe_values,
        lens_groups=lens_groups,
        group_risk_kind=group_risk_kind,
        cvar_alpha=cvar_alpha,
    )
    group_violations = {group: max(0.0, risk - float(budgets[group])) for group, risk in group_risks.items()}
    test_bits = [
        float(row["hidden_bits"])
        for row in eval_rows
        if row["split"] == "test"
    ]
    return {
        "group_risks": group_risks,
        "group_violations": group_violations,
        "total_violation": sum(group_violations.values()),
        "max_violation": max(group_violations.values(), default=0.0),
        "n_groups_feasible": sum(1 for value in group_violations.values() if value <= 1e-9),
        "all_groups_feasible": all(value <= 1e-9 for value in group_violations.values()),
        **aggregate_probe_metrics("test_bits", test_bits, cvar_alpha),
    }, eval_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Greedy group-constrained RD over a fixed multi-task basis.")
    parser.add_argument("--map-specs", nargs="+", default=["maze:9", "four_rooms:9", "open_room:7"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument(
        "--lens-groups",
        nargs="+",
        default=[
            "topology:junction,bottleneck,turn_articulation,betweenness",
            "value:value_gradient",
            "stochastic:transition_entropy",
        ],
    )
    parser.add_argument("--test-probes", nargs="+", default=["combined"])
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--budget-fracs", nargs="+", type=float, default=[0.0, 0.25, 0.5])
    parser.add_argument("--group-risk-kind", choices=["mean", "cvar", "max"], default="cvar")
    parser.add_argument("--score-mode", choices=["reduction", "reduction_per_rate", "lexicographic"], default="reduction")
    parser.add_argument("--rate-tie-break", type=float, default=1e-4)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument("--cvar-eta", type=float, default=0.5)
    parser.add_argument("--smooth-tau", type=float, default=1.0)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-splits", type=int, default=8)
    parser.add_argument("--beam-width", type=int, default=1)
    parser.add_argument("--beam-expand", type=int, default=6)
    parser.add_argument("--disable-probe-cache", action="store_true")
    parser.add_argument("--delta-backend", choices=["operator", "insertion_score"], default="operator")
    parser.add_argument("--scalar-baselines", nargs="+", default=["mean_cvar", "max"])
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/rd_group_constrained"))
    args = parser.parse_args()

    lens_groups = parse_group_specs(args.lens_groups)
    recipe = dict(LEARNED_RECIPES[args.recipe])
    summary_rows: List[Dict[str, object]] = []
    eval_rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []
    candidate_rows: List[Dict[str, object]] = []
    probe_rows: List[Dict[str, object]] = []
    started = time.perf_counter()

    all_train_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    for _family, _size, map_label, map_rows in parse_map_specs(args.map_specs):
        grid = GridWorld(map_rows)
        basis = fixed_basis(
            map_label,
            grid=grid,
            kinds=args.fixed_basis_kinds,
            gamma=args.gamma,
            slip=args.slip,
            top_fraction=args.probe_top_fraction,
            random_count=args.fixed_random_count,
        )
        endpoint_boundary = sorted(set(endpoint_boundary_states(grid)).intersection(set(basis)))
        endpoint_eval, _endpoint_rows = evaluate_boundary_on_groups(
            map_name=map_label,
            rows=map_rows,
            recipe=recipe,
            basis=basis,
            boundary=endpoint_boundary,
            lens_groups=lens_groups,
            budgets={group: 0.0 for group in lens_groups},
            test_probes=args.test_probes,
            gamma=args.gamma,
            slip=args.slip,
            edge_weight=args.edge_weight,
            probe_top_fraction=args.probe_top_fraction,
            group_risk_kind=args.group_risk_kind,
            cvar_alpha=args.cvar_alpha,
        )
        initial_group_risks: Dict[str, float] = endpoint_eval["group_risks"]  # type: ignore[assignment]
        for budget_frac in args.budget_fracs:
            probe_cache = ProbeDeltaCache(enabled=not args.disable_probe_cache)
            budgets = {
                group: float(budget_frac) * float(initial_group_risks.get(group, 0.0))
                for group in lens_groups
            }
            boundary, trace, candidates, probes, selection_time = select_group_constrained_boundary(
                map_name=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                lens_groups=lens_groups,
                budgets=budgets,
                gamma=args.gamma,
                slip=args.slip,
                lambda_struct=args.lambda_struct,
                edge_weight=args.edge_weight,
                probe_top_fraction=args.probe_top_fraction,
                group_risk_kind=args.group_risk_kind,
                cvar_alpha=args.cvar_alpha,
                max_splits=args.max_splits,
                score_mode=args.score_mode,
                rate_tie_break=args.rate_tie_break,
                beam_width=args.beam_width,
                beam_expand=args.beam_expand,
                probe_cache=probe_cache,
                delta_backend=args.delta_backend,
            )
            profile = probe_cache.summary()
            final_eval, final_eval_rows = evaluate_boundary_on_groups(
                map_name=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                test_probes=args.test_probes,
                gamma=args.gamma,
                slip=args.slip,
                edge_weight=args.edge_weight,
                probe_top_fraction=args.probe_top_fraction,
                group_risk_kind=args.group_risk_kind,
                cvar_alpha=args.cvar_alpha,
            )
            summary_rows.append(
                {
                    "map": map_label,
                    "method": "group_constrained",
                    "budget_frac": budget_frac,
                    "n_basis": len(basis),
                    "n_boundary": len(boundary),
                    "selection_time_sec": selection_time,
                    "max_splits": args.max_splits,
                    "stop_reason": trace[-1]["stop_reason"] if trace else "none",
                    "budgets": budgets,
                    "initial_group_risks": initial_group_risks,
                    "final_group_risks": final_eval["group_risks"],
                    "final_group_violations": final_eval["group_violations"],
                    "total_violation": final_eval["total_violation"],
                    "max_violation": final_eval["max_violation"],
                    "n_groups_feasible": final_eval["n_groups_feasible"],
                    "all_groups_feasible": final_eval["all_groups_feasible"],
                    "test_bits_mean": final_eval["test_bits_mean"],
                    "test_bits_cvar": final_eval["test_bits_cvar"],
                    "boundary": list(boundary),
                    **profile,
                    "delta_backend": args.delta_backend,
                }
            )
            trace_rows.extend({**row, "budget_frac": budget_frac, "method": "group_constrained"} for row in trace)
            candidate_rows.extend({**row, "budget_frac": budget_frac} for row in candidates)
            probe_rows.extend({**row, "budget_frac": budget_frac} for row in probes)
            eval_rows.extend(
                {**row, "budget_frac": budget_frac, "method": "group_constrained"}
                for row in final_eval_rows
            )

            for scalar_kind in args.scalar_baselines:
                scalar_boundary, _scalar_trace, _scalar_candidates, scalar_time = select_boundary(
                    map_name=map_label,
                    rows=map_rows,
                    recipe=recipe,
                    basis=basis,
                    train_probes=all_train_probes,
                    gamma=args.gamma,
                    slip=args.slip,
                    lambda_struct=args.lambda_struct,
                    edge_weight=args.edge_weight,
                    probe_top_fraction=args.probe_top_fraction,
                    risk_kind=scalar_kind,
                    cvar_alpha=args.cvar_alpha,
                    cvar_eta=args.cvar_eta,
                    smooth_tau=args.smooth_tau,
                    max_splits=args.max_splits,
                    greedy_positive_only=False,
                )
                scalar_eval, scalar_eval_rows = evaluate_boundary_on_groups(
                    map_name=map_label,
                    rows=map_rows,
                    recipe=recipe,
                    basis=basis,
                    boundary=scalar_boundary,
                    lens_groups=lens_groups,
                    budgets=budgets,
                    test_probes=args.test_probes,
                    gamma=args.gamma,
                    slip=args.slip,
                    edge_weight=args.edge_weight,
                    probe_top_fraction=args.probe_top_fraction,
                    group_risk_kind=args.group_risk_kind,
                    cvar_alpha=args.cvar_alpha,
                )
                summary_rows.append(
                    {
                        "map": map_label,
                        "method": f"scalar_{scalar_kind}",
                        "budget_frac": budget_frac,
                        "n_basis": len(basis),
                        "n_boundary": len(scalar_boundary),
                        "selection_time_sec": scalar_time,
                        "max_splits": args.max_splits,
                        "stop_reason": "fixed_splits",
                        "budgets": budgets,
                        "initial_group_risks": initial_group_risks,
                        "final_group_risks": scalar_eval["group_risks"],
                        "final_group_violations": scalar_eval["group_violations"],
                        "total_violation": scalar_eval["total_violation"],
                        "max_violation": scalar_eval["max_violation"],
                        "n_groups_feasible": scalar_eval["n_groups_feasible"],
                        "all_groups_feasible": scalar_eval["all_groups_feasible"],
                        "test_bits_mean": scalar_eval["test_bits_mean"],
                        "test_bits_cvar": scalar_eval["test_bits_cvar"],
                        "boundary": list(scalar_boundary),
                    }
                )
                eval_rows.extend(
                    {**row, "budget_frac": budget_frac, "method": f"scalar_{scalar_kind}"}
                    for row in scalar_eval_rows
                )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "summary.csv", summary_rows)
    write_csv(args.out_dir / "probe_eval.csv", eval_rows)
    write_csv(args.out_dir / "selection_trace.csv", trace_rows)
    write_csv(args.out_dir / "candidate_scores.csv", candidate_rows)
    write_csv(args.out_dir / "probe_diagnostics.csv", probe_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# Group-Constrained RD\n\n"
        f"- lens_groups: `{'; '.join(args.lens_groups)}`\n"
        f"- group_risk_kind: `{args.group_risk_kind}`\n"
        f"- budget_fracs: `{', '.join(str(value) for value in args.budget_fracs)}`\n"
        f"- score_mode: `{args.score_mode}`\n"
        f"- beam_width: {args.beam_width}\n"
        f"- elapsed_sec: {time.perf_counter() - started:.3f}\n\n"
        "## Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} {row['method']} eps={row['budget_frac']}: "
                f"B={row['n_boundary']}/{row['n_basis']}, "
                f"feasible={row['all_groups_feasible']}, "
                f"groups_ok={row['n_groups_feasible']}, "
                f"total_violation={float(row['total_violation']):.4g}, "
                f"max_violation={float(row['max_violation']):.4g}, "
                f"test_cvar={float(row['test_bits_cvar']):.4g}, "
                f"stop={row['stop_reason']}"
            )
            for row in summary_rows
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
