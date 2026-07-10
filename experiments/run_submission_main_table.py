#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_csv_many(paths: Sequence[Path]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for path in paths:
        source = path.parent.name or path.stem
        for row in read_csv_rows(path):
            enriched = dict(row)
            enriched.setdefault("source", source)
            rows.append(enriched)
    return rows


def write_csv_all_fields(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def parse_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def median(values: Iterable[float]) -> float:
    vals = sorted(value for value in values if math.isfinite(value))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def mean(values: Iterable[float]) -> float:
    vals = [value for value in values if math.isfinite(value)]
    return sum(vals) / len(vals) if vals else float("nan")


def rate(values: Iterable[bool | None]) -> float:
    vals = [value for value in values if value is not None]
    return sum(1 for value in vals if value) / len(vals) if vals else float("nan")


def bootstrap_median_interval(
    values: Iterable[float],
    seed: int,
    n_bootstrap: int = 5000,
) -> Tuple[float, float, float]:
    array = np.asarray([value for value in values if math.isfinite(value)], dtype=float)
    if array.size == 0:
        return float("nan"), float("nan"), float("nan")
    point = float(np.median(array))
    if array.size == 1 or n_bootstrap <= 0:
        return point, point, point
    rng = np.random.default_rng(seed)
    samples = rng.choice(array, size=(n_bootstrap, array.size), replace=True)
    low, high = np.quantile(np.median(samples, axis=1), [0.025, 0.975])
    return point, float(low), float(high)


def break_even_tasks(upfront_cost: float, full_time: float, graph_solve_time: float) -> int | str:
    saving_per_task = full_time - graph_solve_time
    if not math.isfinite(upfront_cost) or not math.isfinite(saving_per_task) or saving_per_task <= 0.0:
        return ""
    return int(math.ceil(max(0.0, upfront_cost) / max(1e-12, saving_per_task)))


def normalized_case_key(map_name: object, slip: object) -> Tuple[str, str]:
    parsed_slip = finite_float(slip)
    slip_key = f"{parsed_slip:.12g}" if math.isfinite(parsed_slip) else str(slip)
    return str(map_name), slip_key


def safe_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator) or denominator <= 0.0:
        return float("nan")
    return numerator / denominator


def normalized_gap(
    row: Mapping[str, object],
    gap_field: str,
    gamma: float,
) -> Tuple[float, str]:
    explicit = finite_float(row.get(f"normalized_{gap_field}"))
    if math.isfinite(explicit):
        return explicit, "reported_value_scale"
    gap = finite_float(row.get(gap_field))
    if not math.isfinite(gap):
        return float("nan"), "unavailable"
    scale = finite_float(row.get("value_scale"))
    if math.isfinite(scale) and scale > 0.0:
        return gap / scale, "reported_value_scale"
    start_value = finite_float(row.get("start_value_full"))
    if math.isfinite(start_value):
        return gap / max(1.0, abs(start_value)), "full_start_value"
    discounted_reward_bound = 1.0 / max(1e-12, 1.0 - gamma)
    return gap / discounted_reward_bound, "discounted_unit_reward_bound"


def group_rows(rows: Sequence[Mapping[str, object]], keys: Sequence[str]) -> Dict[Tuple[str, ...], List[Mapping[str, object]]]:
    groups: Dict[Tuple[str, ...], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row.get(key, "")) for key in keys)].append(row)
    return dict(groups)


def choose_certification_rows(rows: Sequence[Mapping[str, str]]) -> Dict[Tuple[str, str, str], Mapping[str, str]]:
    chosen: Dict[Tuple[str, str, str], Mapping[str, str]] = {}
    for row in rows:
        key = (str(row.get("map", "")), str(row.get("boundary_method", "")), str(row.get("tail_tol", "")))
        chosen[key] = row
    return chosen


def certification_lookup(
    cert_by_key: Mapping[Tuple[str, str, str], Mapping[str, str]],
    map_name: str,
    method_spec: str,
    tail_tol: object,
) -> Mapping[str, str] | None:
    method_key = "endpoints" if method_spec == "endpoints" else method_spec
    tail_key = str(tail_tol)
    direct = cert_by_key.get((map_name, method_key, tail_key))
    if direct is not None:
        return direct
    target = finite_float(tail_tol)
    if not math.isfinite(target):
        return None
    best: Mapping[str, str] | None = None
    best_dist = float("inf")
    for (candidate_map, candidate_method, candidate_tol), row in cert_by_key.items():
        if candidate_map != map_name or candidate_method != method_key:
            continue
        dist = abs(finite_float(candidate_tol, float("inf")) - target)
        if dist < best_dist:
            best = row
            best_dist = dist
    return best


def build_main_runtime_rows(
    large_rows: Sequence[Mapping[str, str]],
    cert_rows: Sequence[Mapping[str, str]],
    planner_rows: Sequence[Mapping[str, str]],
    gamma: float,
) -> List[Dict[str, object]]:
    cert_by_key = choose_certification_rows(cert_rows)
    planner_by_case = {
        normalized_case_key(row.get("map", ""), row.get("slip", "")): row
        for row in planner_rows
        if row.get("map")
    }
    out: List[Dict[str, object]] = []
    for row in large_rows:
        if row.get("error"):
            continue
        method_spec = str(row.get("method_spec", ""))
        cert = certification_lookup(
            cert_by_key,
            map_name=str(row.get("map", "")),
            method_spec=method_spec,
            tail_tol=row.get("first_hit_tail_tol", ""),
        )
        full_time = finite_float(row.get("full_vi_time_sec"), 0.0)
        upfront = finite_float(row.get("upfront_time_sec"), 0.0)
        smdp = finite_float(row.get("smdp_solve_time_sec"), 0.0)
        fallback_proxy = finite_float(cert.get("fallback_exact_time_proxy_sec", 0.0) if cert else 0.0, 0.0)
        tie_proxy = finite_float(
            cert.get("tie_aware_exact_time_proxy_sec", fallback_proxy) if cert else fallback_proxy,
            fallback_proxy,
        )
        total_with_fallback = upfront + smdp + fallback_proxy
        total_with_tie_certificate = upfront + smdp + tie_proxy
        planner = planner_by_case.get(normalized_case_key(row.get("map", ""), row.get("slip", "")))
        strong_time = finite_float(planner.get("strongest_time_median_sec")) if planner else float("nan")
        strong_q1 = finite_float(planner.get("strongest_time_q1_sec")) if planner else float("nan")
        strong_q3 = finite_float(planner.get("strongest_time_q3_sec")) if planner else float("nan")
        strong_ci_low = finite_float(planner.get("strongest_time_bootstrap_ci_low_sec")) if planner else float("nan")
        strong_ci_high = finite_float(planner.get("strongest_time_bootstrap_ci_high_sec")) if planner else float("nan")
        normalized_start, start_normalization = normalized_gap(row, "start_gap", gamma)
        normalized_max, max_normalization = normalized_gap(row, "value_gap_max", gamma)
        out.append(
            {
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "boundary_selector": method_spec,
                "method": "certified_adaptive_green_rd",
                "n_states": row.get("n_states", ""),
                "n_boundary": row.get("n_boundary", ""),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "memory_compression_ratio": finite_float(row.get("memory_compression_ratio")),
                "first_hit_used_steps_max": row.get("first_hit_used_steps_max", ""),
                "tail_bound_max": finite_float(row.get("first_hit_tail_bound_max")),
                "full_vi_time_sec": full_time,
                "legacy_full_vi_time_sec": full_time,
                "strong_full_planner_method": planner.get("strongest_method", "") if planner else "",
                "strong_full_planner_time_q1_sec": strong_q1,
                "strong_full_planner_time_median_sec": strong_time,
                "strong_full_planner_time_q3_sec": strong_q3,
                "strong_full_planner_time_bootstrap_ci_low_sec": strong_ci_low,
                "strong_full_planner_time_bootstrap_ci_high_sec": strong_ci_high,
                "upfront_time_sec": upfront,
                "smdp_solve_time_sec": smdp,
                "total_time_unique_top_fallback_sec": total_with_fallback,
                "total_time_with_tie_certificate_sec": total_with_tie_certificate,
                "planning_speedup": finite_float(row.get("planning_time_speedup_vs_full_vi")),
                "total_speedup_unique_top_fallback": full_time / max(1e-12, total_with_fallback),
                "total_speedup_tie_aware": full_time / max(1e-12, total_with_tie_certificate),
                "planning_speedup_vs_strong_planner": safe_ratio(strong_time, smdp),
                "total_speedup_unique_vs_strong_planner": safe_ratio(strong_time, total_with_fallback),
                "total_speedup_tie_vs_strong_planner": safe_ratio(strong_time, total_with_tie_certificate),
                "unique_top_break_even_tasks": break_even_tasks(upfront + fallback_proxy, full_time, smdp),
                "amortization_break_even_tasks": break_even_tasks(upfront + tie_proxy, full_time, smdp),
                "strong_planner_unique_break_even_tasks": break_even_tasks(
                    upfront + fallback_proxy, strong_time, smdp
                ),
                "strong_planner_tie_break_even_tasks": break_even_tasks(upfront + tie_proxy, strong_time, smdp),
                "backup_compression_ratio": finite_float(row.get("backup_compression_ratio")),
                "start_gap": finite_float(row.get("start_gap")),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "normalized_start_gap": normalized_start,
                "normalized_value_gap_max": normalized_max,
                "gap_normalization": (
                    start_normalization
                    if start_normalization == max_normalization
                    else f"start:{start_normalization};max:{max_normalization}"
                ),
                "tie_mode": cert.get("tie_mode", "") if cert else "",
                "epsilon_optimal_certified": cert.get("epsilon_optimal_certified", "") if cert else "",
                "epsilon_optimality_gap_bound": cert.get("epsilon_optimality_gap_bound", "") if cert else "",
                "tie_set_certified": cert.get("tie_set_certified", "") if cert else "",
                "tie_aware_fallback_used": cert.get("tie_aware_fallback_used", "") if cert else "",
                "curvature_fallback_used": cert.get("curvature_fallback_used", "") if cert else "",
                "interval_certified": cert.get("top1_certified", "") if cert else "",
                "fallback_used": cert.get("fallback_used", "") if cert else "",
                "ambiguous_set_size": cert.get("ambiguous_set_size", "") if cert else "",
                "fallback_reason": cert.get("fallback_reason", "") if cert else "",
                "final_certified": cert.get("final_certified", "") if cert else "",
                "tie_aware_final_certified": cert.get("tie_aware_final_certified", "") if cert else "",
                "final_certificate": cert.get("final_certificate", "") if cert else "",
            }
        )
    return out


def build_compact_baseline_rows(core_rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (method_spec,), rows in sorted(group_rows(core_rows, ["method_spec"]).items()):
        gaps = [finite_float(row.get("start_gap")) for row in rows]
        success = [finite_float(row.get("success_rate")) for row in rows]
        group_values = [parse_bool(row.get("group_all_feasible")) for row in rows if row.get("group_all_feasible", "") != ""]
        out.append(
            {
                "method_spec": method_spec,
                "n_rows": len(rows),
                "median_state_compression": median(finite_float(row.get("state_compression_ratio")) for row in rows),
                "median_planning_speedup": median(finite_float(row.get("planning_time_speedup_vs_full_vi")) for row in rows),
                "median_total_speedup": median(finite_float(row.get("total_time_speedup_vs_full_vi")) for row in rows),
                "max_start_gap": max((value for value in gaps if math.isfinite(value)), default=float("nan")),
                "mean_success_rate": mean(success),
                "max_hidden_audit_distinct": max(
                    (finite_float(row.get("hidden_audit_distinct_mean")) for row in rows),
                    default=float("nan"),
                ),
                "group_feasible_rate": rate(group_values),
            }
        )
    return out


def build_selector_runtime_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (selector,), group in sorted(group_rows(rows, ["boundary_selector"]).items()):
        strong_rows = [
            row
            for row in group
            if math.isfinite(finite_float(row.get("strong_full_planner_time_median_sec")))
        ]
        selector_seed = 7919 + sum((index + 1) * ord(char) for index, char in enumerate(selector))
        planning_median, planning_ci_low, planning_ci_high = bootstrap_median_interval(
            [finite_float(row.get("planning_speedup_vs_strong_planner")) for row in strong_rows],
            selector_seed,
        )
        total_median, total_ci_low, total_ci_high = bootstrap_median_interval(
            [finite_float(row.get("total_speedup_tie_vs_strong_planner")) for row in strong_rows],
            selector_seed + 1,
        )
        out.append(
            {
                "boundary_selector": selector,
                "n_rows": len(group),
                "n_strong_planner_rows": len(strong_rows),
                "median_state_compression": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "median_normalized_start_gap": median(
                    finite_float(row.get("normalized_start_gap")) for row in group
                ),
                "max_normalized_start_gap": max(
                    (
                        value
                        for row in group
                        if math.isfinite(value := finite_float(row.get("normalized_start_gap")))
                    ),
                    default=float("nan"),
                ),
                "legacy_median_total_speedup": median(
                    finite_float(row.get("total_speedup_tie_aware")) for row in group
                ),
                "strong_planner_median_planning_speedup": planning_median,
                "strong_planner_planning_speedup_ci95_low": planning_ci_low,
                "strong_planner_planning_speedup_ci95_high": planning_ci_high,
                "strong_planner_median_total_speedup": total_median,
                "strong_planner_total_speedup_ci95_low": total_ci_low,
                "strong_planner_total_speedup_ci95_high": total_ci_high,
                "strong_planner_best_total_speedup": max(
                    (finite_float(row.get("total_speedup_tie_vs_strong_planner")) for row in strong_rows),
                    default=float("nan"),
                ),
            }
        )
    return out


def build_abstraction_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        out.append(
            {
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": row.get("method", ""),
                "method_group": row.get("method_group", ""),
                "target_count": row.get("target_count", ""),
                "n_states": row.get("n_states", ""),
                "n_abstract_states": row.get("n_abstract_states", ""),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "normalized_start_gap": finite_float(row.get("normalized_start_gap")),
                "normalized_policy_start_gap": finite_float(row.get("normalized_policy_start_gap")),
                "homogeneity_error": finite_float(row.get("homogeneity_error")),
                "time_q1_sec": finite_float(row.get("time_q1_sec")),
                "time_median_sec": finite_float(row.get("time_median_sec")),
                "time_q3_sec": finite_float(row.get("time_q3_sec")),
                "total_speedup_median": finite_float(row.get("total_speedup_median")),
                "representation_scope": row.get("representation_scope", ""),
            }
        )
    return out


def build_constrained_rows(
    rows: Sequence[Mapping[str, str]],
    value_epsilon: float,
    audit_epsilon: float,
) -> List[Dict[str, object]]:
    def threshold_match(value: object, target: float) -> bool:
        parsed = finite_float(value)
        if math.isinf(target):
            return math.isinf(parsed)
        return math.isfinite(parsed) and abs(parsed - target) <= 1e-12

    return [
        dict(row)
        for row in rows
        if threshold_match(row.get("value_epsilon"), value_epsilon)
        and threshold_match(row.get("audit_epsilon"), audit_epsilon)
    ]


def build_general_env_aggregate_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    return [dict(row) for row in rows if row.get("method")]


def build_budget_recovery_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    return [dict(row) for row in rows if row.get("map")]


def build_end_to_end_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    return [dict(row) for row in rows if row.get("map") and not row.get("error")]


def build_solver_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (solver, beam_width, pool_mode, complete), group in sorted(
        group_rows(
            rows,
            ["solver", "beam_width", "oracle_pool_mode", "oracle_complete_candidate_universe"],
        ).items()
    ):
        boundary_matches = [parse_bool(row.get("same_boundary_as_oracle")) for row in group]
        feasible_matches = [
            (parse_bool(row.get("oracle_all_feasible")) == parse_bool(row.get("chosen_all_feasible")))
            for row in group
            if parse_bool(row.get("oracle_all_feasible")) is not None
            and parse_bool(row.get("chosen_all_feasible")) is not None
        ]
        out.append(
            {
                "solver": solver,
                "beam_width": beam_width,
                "oracle_pool_mode": pool_mode,
                "oracle_complete_candidate_universe": complete,
                "n_rows": len(group),
                "boundary_match_rate": rate(boundary_matches),
                "zero_total_violation_gap_rate": rate(
                    abs(finite_float(row.get("total_violation_gap"), 0.0)) <= 1e-9 for row in group
                ),
                "feasible_decision_match_rate": rate(feasible_matches),
                "median_selection_time_sec": median(finite_float(row.get("selection_time_sec")) for row in group),
                "median_oracle_time_sec": median(finite_float(row.get("oracle_time_sec")) for row in group),
            }
        )
    return out


def build_certificate_rows(
    adaptive_rows: Sequence[Mapping[str, str]],
    weighted_rows: Sequence[Mapping[str, str]],
    conditioned_rows: Sequence[Mapping[str, str]],
) -> List[Dict[str, object]]:
    adaptive = list(adaptive_rows)
    weighted = list(weighted_rows)
    conditioned = list(conditioned_rows)
    return [
        {
            "certificate": "adaptive_frontier_tail_plus_top_set_fallback",
            "rows": len(adaptive),
            "interval_certified": sum(1 for row in adaptive if parse_bool(row.get("top1_certified"))),
            "fallback_used": sum(1 for row in adaptive if parse_bool(row.get("fallback_used"))),
            "tie_fallback_used": sum(1 for row in adaptive if parse_bool(row.get("tie_fallback_used"))),
            "curvature_fallback_used": sum(1 for row in adaptive if parse_bool(row.get("curvature_fallback_used"))),
            "tie_set_certified": sum(1 for row in adaptive if parse_bool(row.get("tie_set_certified"))),
            "epsilon_optimal_certified": sum(1 for row in adaptive if parse_bool(row.get("epsilon_optimal_certified"))),
            "final_certified": sum(1 for row in adaptive if parse_bool(row.get("final_certified"))),
            "tie_aware_final_certified": sum(1 for row in adaptive if parse_bool(row.get("tie_aware_final_certified"))),
            "status": "runtime_decision_procedure",
        },
        {
            "certificate": "weighted_spectral_sufficient",
            "rows": len(weighted),
            "row_q_lt_1_edges": sum(int(finite_float(row.get("row_q_lt_1"), 0.0)) for row in weighted),
            "weighted_q_lt_1_edges": sum(int(finite_float(row.get("weighted_q_lt_1"), 0.0)) for row in weighted),
            "max_weight_dynamic_range": max(
                (finite_float(row.get("weight_dynamic_range_max")) for row in weighted),
                default=float("nan"),
            ),
            "status": "appendix_sufficient_certificate",
        },
        {
            "certificate": "conditioned_rational_weighted_audit",
            "rows": len(conditioned),
            "certificates_found": sum(int(finite_float(row.get("certificates_found"), 0.0)) for row in conditioned),
            "rational_verified": sum(int(finite_float(row.get("rational_verified"), 0.0)) for row in conditioned),
            "max_rational_violation": max(
                (finite_float(row.get("rational_max_violation_max"), 0.0) for row in conditioned),
                default=float("nan"),
            ),
            "status": "appendix_reproducibility_audit",
        },
    ]


def build_group_adaptive_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        out.append(
            {
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": row.get("method", ""),
                "n_states": row.get("n_states", ""),
                "n_basis": row.get("n_basis", ""),
                "n_boundary": row.get("n_boundary", ""),
                "group_all_feasible": row.get("group_all_feasible", ""),
                "n_groups_feasible": row.get("n_groups_feasible", ""),
                "group_total_violation": finite_float(row.get("group_total_violation")),
                "selection_time_sec": finite_float(row.get("selection_time_sec")),
                "delta_backend": row.get("delta_backend", ""),
                "probe_green_kernel_time_sec": finite_float(row.get("probe_green_kernel_time_sec")),
                "probe_operator_delta_time_sec": finite_float(row.get("probe_operator_delta_time_sec")),
                "active_weight_time_sec": finite_float(row.get("active_weight_time_sec")),
                "candidate_score_time_sec": finite_float(row.get("candidate_score_time_sec")),
                "probe_cache_hit_rate": finite_float(row.get("probe_cache_hit_rate")),
                "kernel_time_sec": finite_float(row.get("kernel_time_sec")),
                "smdp_solve_time_sec": finite_float(row.get("smdp_solve_time_sec")),
                "planning_speedup": finite_float(row.get("planning_speedup")),
                "total_speedup": finite_float(row.get("total_speedup")),
                "break_even_tasks": row.get("break_even_tasks", ""),
                "start_gap": finite_float(row.get("start_gap")),
                "first_hit_tail_bound_max": finite_float(row.get("first_hit_tail_bound_max")),
            }
        )
    return out


def build_discovery_profile_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (mode,), group in group_rows(rows, ["mode"]).items():
        out.append(
            {
                "mode": mode,
                "n_rows": len(group),
                "median_wall_time_sec": median(finite_float(row.get("wall_time_sec")) for row in group),
                "median_speedup_vs_full_recompute": median(
                    finite_float(row.get("speedup_vs_full_recompute")) for row in group
                ),
                "max_speedup_vs_full_recompute": max(
                    (finite_float(row.get("speedup_vs_full_recompute")) for row in group),
                    default=float("nan"),
                ),
                "median_probe_green_kernel_time_sec": median(
                    finite_float(row.get("probe_green_kernel_time_sec")) for row in group
                ),
                "median_probe_operator_delta_time_sec": median(
                    finite_float(row.get("probe_operator_delta_time_sec")) for row in group
                ),
                "median_full_recompute_time_sec": median(
                    finite_float(row.get("full_recompute_time_sec")) for row in group
                ),
                "median_candidate_score_time_sec": median(
                    finite_float(row.get("candidate_score_time_sec")) for row in group
                ),
                "median_probe_cache_hit_rate": median(
                    finite_float(row.get("probe_cache_hit_rate")) for row in group
                ),
            }
        )
    return sorted(out, key=lambda row: str(row["mode"]))


def build_hybrid_refine_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    def sort_key(item: Tuple[Tuple[str, ...], List[Mapping[str, object]]]) -> Tuple[str, str, int, str]:
        source, method, top_k = item[0]
        top_k_value = int(finite_float(top_k, -1.0)) if str(top_k).strip() else -1
        return source, method, top_k_value, top_k

    for (source, method, top_k), group in sorted(group_rows(rows, ["source", "method", "top_k"]).items(), key=sort_key):
        if not method:
            continue
        ok = [row for row in group if not row.get("error")]
        recalls = [
            finite_float(row.get("surrogate_topk_recall"))
            for row in ok
            if math.isfinite(finite_float(row.get("surrogate_topk_recall")))
        ]
        out.append(
            {
                "source": source,
                "method": method,
                "top_k": top_k,
                "n_rows": len(ok),
                "feasible_rate": rate(parse_bool(row.get("group_all_feasible")) for row in ok),
                "median_n_boundary": median(finite_float(row.get("n_boundary")) for row in ok),
                "median_selection_time_sec": median(finite_float(row.get("selection_time_sec")) for row in ok),
                "median_proposal_time_sec": median(finite_float(row.get("proposal_time_sec")) for row in ok),
                "median_refine_time_sec": median(finite_float(row.get("refine_time_sec")) for row in ok),
                "median_kernel_time_sec": median(finite_float(row.get("kernel_time_sec")) for row in ok),
                "median_upfront_time_sec": median(finite_float(row.get("upfront_time_sec")) for row in ok),
                "median_total_speedup": median(finite_float(row.get("total_speedup")) for row in ok),
                "best_total_speedup": max(
                    (finite_float(row.get("total_speedup")) for row in ok),
                    default=float("nan"),
                ),
                "median_break_even_tasks": median(finite_float(row.get("break_even_tasks")) for row in ok),
                "max_group_total_violation": max(
                    (finite_float(row.get("group_total_violation"), 0.0) for row in ok),
                    default=float("nan"),
                ),
                "max_start_gap": max(
                    (finite_float(row.get("start_gap"), 0.0) for row in ok),
                    default=float("nan"),
                ),
                "mean_surrogate_topk_recall": mean(recalls) if recalls else "",
                "total_exact_refine_calls": sum(int(finite_float(row.get("exact_refine_calls"), 0.0)) for row in ok),
                "median_adaptive_topk_used_mean": median(
                    finite_float(row.get("adaptive_topk_used_mean")) for row in ok
                ),
                "max_adaptive_topk_used": max(
                    (finite_float(row.get("adaptive_topk_used_max"), 0.0) for row in ok),
                    default=float("nan"),
                ),
                "total_adaptive_topk_cap_hits": sum(
                    int(finite_float(row.get("adaptive_topk_cap_hits"), 0.0)) for row in ok
                ),
                "total_refined_candidates": sum(
                    int(finite_float(row.get("refined_candidates_total"), 0.0)) for row in ok
                ),
                "median_probe_green_kernel_time_sec": median(
                    finite_float(row.get("probe_green_kernel_time_sec")) for row in ok
                ),
                "median_active_weight_time_sec": median(
                    finite_float(row.get("active_weight_time_sec")) for row in ok
                ),
                "median_candidate_score_time_sec": median(
                    finite_float(row.get("candidate_score_time_sec")) for row in ok
                ),
            }
        )
    return out


def build_random_maze_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (method,), group in sorted(group_rows(rows, ["method"]).items()):
        ok = [row for row in group if not row.get("error")]
        out.append(
            {
                "method": method,
                "n_rows": len(ok),
                "feasible_rate": rate(parse_bool(row.get("group_all_feasible")) for row in ok),
                "median_n_boundary": median(finite_float(row.get("n_boundary")) for row in ok),
                "median_state_compression": median(finite_float(row.get("state_compression_ratio")) for row in ok),
                "median_selection_time_sec": median(finite_float(row.get("selection_time_sec")) for row in ok),
                "median_total_speedup": median(finite_float(row.get("total_speedup")) for row in ok),
                "max_start_gap": max((finite_float(row.get("start_gap"), 0.0) for row in ok), default=float("nan")),
                "max_group_total_violation": max(
                    (finite_float(row.get("group_total_violation"), 0.0) for row in ok),
                    default=float("nan"),
                ),
            }
        )
    return out


def build_general_env_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    eligible = [
        row
        for row in rows
        if row.get("method") and row.get("method") != "full_vi" and not row.get("error")
    ]
    out: List[Dict[str, object]] = []
    for (env, method), group in sorted(group_rows(eligible, ["env", "method"]).items()):
        best = min(
            group,
            key=lambda row: (
                finite_float(row.get("start_value_gap"), float("inf")),
                finite_float(row.get("n_boundary"), float("inf")),
            ),
        )
        out.append(
            {
                "env": env,
                "source": best.get("source", ""),
                "method": method,
                "n_rows": len(group),
                "best_option_mode": best.get("option_mode", ""),
                "best_n_options": best.get("n_options", ""),
                "best_target_count": best.get("target_count", ""),
                "n_states": best.get("n_states", ""),
                "best_n_boundary": best.get("n_boundary", ""),
                "best_state_compression": best.get("state_compression_ratio", ""),
                "best_start_gap": best.get("start_value_gap", ""),
                "best_value_gap_max": best.get("value_gap_max", ""),
                "n_terminal": best.get("n_terminal", ""),
                "n_start_support": best.get("n_start_support", ""),
                "interpretation": (
                    "structured task-variable failure"
                    if env.startswith("Taxi")
                    else "finite-MDP portability smoke"
                ),
            }
        )
    return out


def build_fair_frontier_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        out.append(
            {
                "comparison_protocol": row.get("comparison_protocol", ""),
                "method_group": row.get("method_group", ""),
                "n_rows": row.get("n_rows", ""),
                "pareto_rows": row.get("pareto_rows", ""),
                "median_rate_budget_boundary_frac": finite_float(row.get("median_rate_budget_boundary_frac")),
                "median_state_compression_ratio": finite_float(row.get("median_state_compression_ratio")),
                "median_start_gap": finite_float(row.get("median_start_gap")),
                "median_normalized_start_gap": finite_float(row.get("median_normalized_start_gap")),
                "median_hidden_audit": finite_float(row.get("median_hidden_audit")),
                "median_normalized_hidden_audit": finite_float(row.get("median_normalized_hidden_audit")),
                "mean_group_feasible_rate": finite_float(row.get("mean_group_feasible_rate")),
                "median_total_speedup": finite_float(row.get("median_total_speedup")),
                "median_success_rate": finite_float(row.get("median_success_rate")),
            }
        )
    return out


def build_amortized_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (method_spec, task_count), group in sorted(group_rows(rows, ["method_spec", "task_count"]).items()):
        ok = [row for row in group if not row.get("error")]
        out.append(
            {
                "source": "amortized_multitask",
                "method_or_variant": method_spec,
                "task_count": task_count,
                "n_rows": len(ok),
                "median_amortized_speedup": median(
                    finite_float(row.get("amortized_speedup_vs_full_vi")) for row in ok
                ),
                "best_amortized_speedup": max(
                    (finite_float(row.get("amortized_speedup_vs_full_vi")) for row in ok),
                    default=float("nan"),
                ),
                "median_planning_only_speedup": median(
                    finite_float(row.get("planning_only_speedup_vs_full_vi")) for row in ok
                ),
                "median_break_even_tasks": median(finite_float(row.get("break_even_tasks")) for row in ok),
                "max_start_gap": max((finite_float(row.get("start_gap"), 0.0) for row in ok), default=float("nan")),
                "median_state_compression": median(finite_float(row.get("state_compression_ratio")) for row in ok),
            }
        )
    return out


def build_edge_reward_rows(
    rows: Sequence[Mapping[str, str]],
    gamma: float,
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (variant, task_count), group in sorted(group_rows(rows, ["variant", "task_count"]).items()):
        if not variant or variant == "error":
            continue
        ok = [row for row in group if not row.get("error")]
        normalized_start = [normalized_gap(row, "start_gap_max", gamma)[0] for row in ok]
        normalized_boundary = [normalized_gap(row, "boundary_gap_max", gamma)[0] for row in ok]
        out.append(
            {
                "source": "edge_reward_kernel_multitask",
                "method_or_variant": variant,
                "task_count": task_count,
                "n_rows": len(ok),
                "median_amortized_speedup": median(
                    finite_float(row.get("amortized_speedup_vs_full_vi")) for row in ok
                ),
                "best_amortized_speedup": max(
                    (finite_float(row.get("amortized_speedup_vs_full_vi")) for row in ok),
                    default=float("nan"),
                ),
                "median_planning_only_speedup": median(
                    finite_float(row.get("planning_only_speedup_vs_full_vi")) for row in ok
                ),
                "median_break_even_tasks": median(finite_float(row.get("break_even_num_tasks")) for row in ok),
                "max_start_gap": max((finite_float(row.get("start_gap_max"), 0.0) for row in ok), default=float("nan")),
                "max_normalized_start_gap": max(
                    (value for value in normalized_start if math.isfinite(value)),
                    default=float("nan"),
                ),
                "max_normalized_boundary_gap": max(
                    (value for value in normalized_boundary if math.isfinite(value)),
                    default=float("nan"),
                ),
                "median_state_compression": median(
                    finite_float(row.get("state_compression_ratio")) for row in ok
                ),
                "median_goal_interface": median(finite_float(row.get("goal_option_interface_size")) for row in ok),
                "median_goal_policies": median(finite_float(row.get("n_goal_policies")) for row in ok),
                "runtime_denominator": "legacy_dense_numpy_full_vi",
            }
        )
    return out


def build_multitask_rows(
    amortized_rows: Sequence[Mapping[str, str]],
    edge_reward_rows: Sequence[Mapping[str, str]],
    gamma: float,
) -> List[Dict[str, object]]:
    return build_amortized_rows(amortized_rows) + build_edge_reward_rows(edge_reward_rows, gamma)


def build_failure_mode_rows(
    main_rows: Sequence[Mapping[str, object]],
    group_adaptive_rows: Sequence[Mapping[str, object]],
    edge_reward_rows: Sequence[Mapping[str, str]],
    gamma: float,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    open_rows = [
        row for row in group_adaptive_rows
        if "open_room" in str(row.get("map", "")) and str(row.get("method", "")) in {"endpoints", "group_constrained", "group_constrained_incremental"}
    ]
    if open_rows:
        endpoint_rows = [row for row in open_rows if row.get("method") == "endpoints"]
        robust_rows = [row for row in open_rows if str(row.get("method", "")).startswith("group_constrained")]
        rows.append(
            {
                "failure_mode": "open_room_soft_over_split_or_hidden_boundary",
                "evidence": "group constraints expose endpoint infeasibility while incremental/group RD removes group violation",
                "n_rows": len(open_rows),
                "endpoint_feasible_rate": rate(parse_bool(row.get("group_all_feasible")) for row in endpoint_rows),
                "robust_feasible_rate": rate(parse_bool(row.get("group_all_feasible")) for row in robust_rows),
                "max_endpoint_violation": max(
                    (finite_float(row.get("group_total_violation"), 0.0) for row in endpoint_rows),
                    default=float("nan"),
                ),
                "max_robust_violation": max(
                    (finite_float(row.get("group_total_violation"), 0.0) for row in robust_rows),
                    default=float("nan"),
                ),
            }
        )
    corridor_rows = [row for row in main_rows if "corridor" in str(row.get("map", ""))]
    if corridor_rows:
        rows.append(
            {
                "failure_mode": "corridor_top_set_tie",
                "evidence": "long corridors create large epsilon/tie sets; tie-aware certificate reports cheap top-set exact fallback separately",
                "n_rows": len(corridor_rows),
                "max_ambiguous_set_size": max(
                    (finite_float(row.get("ambiguous_set_size"), 0.0) for row in corridor_rows),
                    default=float("nan"),
                ),
                "tie_set_certified_rate": rate(parse_bool(row.get("tie_set_certified")) for row in corridor_rows),
                "max_tie_aware_total_speedup": max(
                    (finite_float(row.get("total_speedup_tie_aware")) for row in corridor_rows),
                    default=float("nan"),
                ),
            }
        )
    edge_ok = [row for row in edge_reward_rows if not row.get("error")]
    if edge_ok:
        event_rows = [row for row in edge_ok if row.get("variant") == "fixed_B_event_hit_kernel"]
        gc_rows = [row for row in edge_ok if row.get("variant") == "fixed_B_goal_conditioned_event_options"]
        rows.append(
            {
                "failure_mode": "terminal_interior_goal_event_gap",
                "evidence": "fixed-B event kernels expose option/boundary restriction bias; goal-conditioned event options reduce gap but add query-time interface cost",
                "n_rows": len(event_rows) + len(gc_rows),
                "event_kernel_max_gap": max(
                    (finite_float(row.get("start_gap_max"), 0.0) for row in event_rows),
                    default=float("nan"),
                ),
                "event_kernel_max_normalized_gap": max(
                    (
                        value
                        for row in event_rows
                        if math.isfinite(value := normalized_gap(row, "start_gap_max", gamma)[0])
                    ),
                    default=float("nan"),
                ),
                "goal_conditioned_max_gap": max(
                    (finite_float(row.get("start_gap_max"), 0.0) for row in gc_rows),
                    default=float("nan"),
                ),
                "goal_conditioned_max_normalized_gap": max(
                    (
                        value
                        for row in gc_rows
                        if math.isfinite(value := normalized_gap(row, "start_gap_max", gamma)[0])
                    ),
                    default=float("nan"),
                ),
                "goal_conditioned_median_break_even": median(
                    finite_float(row.get("break_even_num_tasks")) for row in gc_rows
                ),
                "goal_conditioned_best_speedup": max(
                    (finite_float(row.get("amortized_speedup_vs_full_vi")) for row in gc_rows),
                    default=float("nan"),
                ),
            }
        )
    return rows


def build_theorem_bridge_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        out.append(
            {
                "paper_claim": row.get("paper_claim", ""),
                "proof_status": row.get("proof_status", ""),
                "experiment_status": row.get("experiment_status", ""),
                "manuscript_location": row.get("manuscript_location", ""),
                "remaining_gap": row.get("remaining_gap", ""),
            }
        )
    return out


def build_one_shot_summary_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    filtered = [
        row
        for row in rows
        if str(row.get("method", "")).startswith("one_shot_rd_") and not row.get("error")
    ]
    for (source, method), group in sorted(group_rows(filtered, ["source", "method"]).items()):
        out.append(
            {
                "source": source,
                "method": method,
                "n_rows": len(group),
                "median_n_boundary": median(finite_float(row.get("n_boundary")) for row in group),
                "median_state_compression": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "median_selection_time_sec": median(
                    finite_float(row.get("selection_time_sec")) for row in group
                ),
                "median_final_kernel_time_sec": median(
                    finite_float(row.get("final_kernel_time_sec")) for row in group
                ),
                "median_selection_speedup_vs_iterative": median(
                    finite_float(row.get("selection_speedup_vs_iterative")) for row in group
                ),
                "median_total_speedup_vs_iterative": median(
                    finite_float(row.get("total_speedup_vs_iterative")) for row in group
                ),
                "median_selection_speedup_vs_exact_search": median(
                    finite_float(row.get("selection_speedup_vs_exact_search")) for row in group
                ),
                "median_total_speedup_vs_exact_search": median(
                    finite_float(row.get("total_speedup_vs_exact_search")) for row in group
                ),
                "median_total_speedup_vs_sparse_vi": median(
                    finite_float(row.get("total_speedup_vs_sparse_vi")) for row in group
                ),
                "max_normalized_value_gap": max(
                    (finite_float(row.get("normalized_value_gap_max")) for row in group),
                    default=float("nan"),
                ),
                "median_D_occ": median(finite_float(row.get("D_occ")) for row in group),
                "median_boundary_jaccard_vs_iterative": median(
                    finite_float(row.get("boundary_jaccard_vs_iterative")) for row in group
                ),
            }
        )
    return out


def build_one_shot_group_prefix_rows(
    rows: Sequence[Mapping[str, str]],
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (map_name, slip), group in sorted(group_rows(rows, ["map", "slip"]).items()):
        ordered = sorted(group, key=lambda row: int(finite_float(row.get("top_m"), 0.0)))
        feasible = [
            int(finite_float(row.get("top_m"), 0.0))
            for row in ordered
            if parse_bool(row.get("group_all_feasible")) is True
        ]
        first_feasible = min(feasible) if feasible else None
        infeasible_after = bool(
            first_feasible is not None
            and any(
                int(finite_float(row.get("top_m"), 0.0)) > first_feasible
                and parse_bool(row.get("group_all_feasible")) is False
                for row in ordered
            )
        )
        feasible_rows = [
            row for row in ordered if parse_bool(row.get("group_all_feasible")) is True
        ]
        out.append(
            {
                "map": map_name,
                "slip": slip,
                "n_tested_prefixes": len(ordered),
                "max_tested_k": max(
                    (int(finite_float(row.get("top_m"), 0.0)) for row in ordered),
                    default=0,
                ),
                "any_feasible": bool(feasible),
                "feasible_prefixes": ",".join(str(value) for value in feasible),
                "first_feasible_k": first_feasible if first_feasible is not None else "",
                "infeasible_after_first_feasible": infeasible_after,
                "best_feasible_state_compression": max(
                    (finite_float(row.get("state_compression_ratio")) for row in feasible_rows),
                    default=float("nan"),
                ),
                "n_candidate_insertion_evaluations": max(
                    (
                        int(finite_float(row.get("n_candidate_insertion_evaluations"), 0.0))
                        for row in ordered
                    ),
                    default=0,
                ),
                "n_beam_expansions": max(
                    (int(finite_float(row.get("n_beam_expansions"), 0.0)) for row in ordered),
                    default=0,
                ),
            }
        )
    return out


def build_boundary_student_rows(
    proposal_rows: Sequence[Mapping[str, str]],
    baseline_rows: Sequence[Mapping[str, str]],
    selective_rows: Sequence[Mapping[str, str]],
    constraint_rows: Sequence[Mapping[str, str]],
    constraint_selective_rows: Sequence[Mapping[str, str]],
    constraint_full_audit_rows: Sequence[Mapping[str, str]],
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for source, rows in (
        ("learned_student", proposal_rows),
        ("explicit_baseline", baseline_rows),
        ("constraint_aware_student", constraint_rows),
    ):
        for row in rows:
            out.append(
                {
                    "source": source,
                    "proposal": row.get("student_method", ""),
                    "n_rows": row.get("n_rows", ""),
                    "mean_boundary_jaccard": row.get("mean_boundary_jaccard", ""),
                    "group_feasible_rate": row.get("student_feasible_rate", ""),
                    "student_joint_constraint_rate": row.get(
                        "student_joint_constraint_rate", ""
                    ),
                    "teacher_joint_constraint_rate": row.get(
                        "teacher_joint_constraint_rate", ""
                    ),
                    "accepted_group_feasible_rate": row.get(
                        "accepted_feasible_rate", ""
                    ),
                    "median_selection_speedup": row.get("median_selection_speedup_vs_teacher", ""),
                    "median_accepted_pipeline_speedup": row.get(
                        "median_accepted_speedup_vs_teacher_pipeline", ""
                    ),
                    "max_normalized_start_gap": row.get(
                        "max_student_normalized_start_gap", ""
                    ),
                    "certification_status": "uncertified proposal",
                    "gate_status": (
                        "raw pass; routing NO-GO"
                        if source == "constraint_aware_student"
                        else "ablation"
                    ),
                }
            )
    for source, rows in (
        ("empirical_selective_audit", selective_rows),
        ("constraint_aware_selective_audit", constraint_selective_rows),
    ):
        for row in rows:
            undetected = finite_float(row.get("test_undetected_failures"), float("inf"))
            out.append(
                {
                    "source": source,
                    "proposal": row.get("metric", ""),
                    "target_validation_failure_recall": row.get(
                        "target_validation_failure_recall", ""
                    ),
                    "n_rows": row.get("test_n_rows", ""),
                    "selective_accepted_joint_rate": row.get(
                        "test_accepted_feasible_rate", ""
                    ),
                    "median_accepted_pipeline_speedup": row.get(
                        "test_median_selective_speedup_vs_teacher", ""
                    ),
                    "max_normalized_start_gap": row.get(
                        "test_max_accepted_normalized_start_gap", ""
                    ),
                    "audit_rate": row.get("test_audit_rate", ""),
                    "failure_recall": row.get("test_failure_recall", ""),
                    "undetected_failures": row.get("test_undetected_failures", ""),
                    "certification_status": "empirical routing; not a certificate",
                    "gate_status": (
                        "NO-GO" if source == "constraint_aware_selective_audit" and undetected > 1 else "ablation"
                    ),
                }
            )
    for row in constraint_full_audit_rows:
        out.append(
            {
                "source": "constraint_aware_full_audit",
                "proposal": "full_production_audit",
                "n_rows": row.get("n_rows", ""),
                "selective_accepted_joint_rate": row.get("accepted_feasible_rate", ""),
                "median_accepted_pipeline_speedup": row.get(
                    "median_selective_speedup_vs_teacher", ""
                ),
                "max_normalized_start_gap": row.get(
                    "max_accepted_normalized_start_gap", ""
                ),
                "audit_rate": row.get("audit_rate", ""),
                "failure_recall": row.get("failure_recall", ""),
                "undetected_failures": row.get("undetected_failures", ""),
                "certification_status": "full empirical audit",
                "gate_status": "NO-GO: end-to-end speedup <= 1",
            }
        )
    return out


def write_report(
    out_path: Path,
    main_rows: Sequence[Mapping[str, object]],
    one_shot_rows: Sequence[Mapping[str, object]],
    one_shot_group_prefix_rows: Sequence[Mapping[str, object]],
    selector_runtime_rows: Sequence[Mapping[str, object]],
    planner_rows: Sequence[Mapping[str, object]],
    compact_rows: Sequence[Mapping[str, object]],
    abstraction_rows: Sequence[Mapping[str, object]],
    end_to_end_rows: Sequence[Mapping[str, object]],
    group_adaptive_rows: Sequence[Mapping[str, object]],
    random_maze_rows: Sequence[Mapping[str, object]],
    general_env_rows: Sequence[Mapping[str, object]],
    general_env_aggregate_rows: Sequence[Mapping[str, object]],
    fair_frontier_rows: Sequence[Mapping[str, object]],
    constrained_rows: Sequence[Mapping[str, object]],
    budget_recovery_rows: Sequence[Mapping[str, object]],
    multitask_rows: Sequence[Mapping[str, object]],
    failure_mode_rows: Sequence[Mapping[str, object]],
    solver_rows: Sequence[Mapping[str, object]],
    certificate_rows: Sequence[Mapping[str, object]],
    discovery_profile_rows: Sequence[Mapping[str, object]],
    hybrid_refine_rows: Sequence[Mapping[str, object]],
    incremental_green_rows: Sequence[Mapping[str, object]],
    theorem_bridge_rows: Sequence[Mapping[str, object]],
    adaptive_topk_tables: Mapping[str, Sequence[Mapping[str, object]]],
    boundary_student_rows: Sequence[Mapping[str, object]],
    args: argparse.Namespace,
) -> None:
    main_columns = [
        "map",
        "slip",
        "boundary_selector",
        "method",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "first_hit_used_steps_max",
        "tail_bound_max",
        "legacy_full_vi_time_sec",
        "strong_full_planner_method",
        "strong_full_planner_time_median_sec",
        "strong_full_planner_time_bootstrap_ci_low_sec",
        "strong_full_planner_time_bootstrap_ci_high_sec",
        "upfront_time_sec",
        "smdp_solve_time_sec",
        "total_time_unique_top_fallback_sec",
        "total_time_with_tie_certificate_sec",
        "planning_speedup",
        "planning_speedup_vs_strong_planner",
        "total_speedup_unique_top_fallback",
        "total_speedup_tie_aware",
        "total_speedup_tie_vs_strong_planner",
        "unique_top_break_even_tasks",
        "amortization_break_even_tasks",
        "strong_planner_tie_break_even_tasks",
        "start_gap",
        "normalized_start_gap",
        "gap_normalization",
        "tie_mode",
        "epsilon_optimal_certified",
        "tie_set_certified",
        "tie_aware_fallback_used",
        "curvature_fallback_used",
        "interval_certified",
        "fallback_used",
        "ambiguous_set_size",
        "tie_aware_final_certified",
    ]
    one_shot_columns = [
        "source",
        "method",
        "n_rows",
        "median_n_boundary",
        "median_state_compression",
        "median_selection_time_sec",
        "median_final_kernel_time_sec",
        "median_selection_speedup_vs_iterative",
        "median_total_speedup_vs_iterative",
        "median_selection_speedup_vs_exact_search",
        "median_total_speedup_vs_exact_search",
        "median_total_speedup_vs_sparse_vi",
        "max_normalized_value_gap",
        "median_D_occ",
        "median_boundary_jaccard_vs_iterative",
    ]
    one_shot_group_prefix_columns = [
        "map",
        "slip",
        "n_tested_prefixes",
        "max_tested_k",
        "any_feasible",
        "feasible_prefixes",
        "first_feasible_k",
        "infeasible_after_first_feasible",
        "best_feasible_state_compression",
        "n_candidate_insertion_evaluations",
        "n_beam_expansions",
    ]
    selector_runtime_columns = [
        "boundary_selector",
        "n_rows",
        "n_strong_planner_rows",
        "median_state_compression",
        "median_normalized_start_gap",
        "max_normalized_start_gap",
        "legacy_median_total_speedup",
        "strong_planner_median_planning_speedup",
        "strong_planner_planning_speedup_ci95_low",
        "strong_planner_planning_speedup_ci95_high",
        "strong_planner_median_total_speedup",
        "strong_planner_total_speedup_ci95_low",
        "strong_planner_total_speedup_ci95_high",
        "strong_planner_best_total_speedup",
    ]
    planner_columns = [
        "map",
        "slip",
        "strongest_method",
        "strongest_time_q1_sec",
        "strongest_time_median_sec",
        "strongest_time_q3_sec",
        "strongest_time_bootstrap_ci_low_sec",
        "strongest_time_bootstrap_ci_high_sec",
        "strongest_backup_median",
        "max_value_error",
    ]
    compact_columns = [
        "method_spec",
        "n_rows",
        "median_state_compression",
        "median_planning_speedup",
        "median_total_speedup",
        "max_start_gap",
        "mean_success_rate",
        "max_hidden_audit_distinct",
        "group_feasible_rate",
    ]
    abstraction_columns = [
        "map",
        "slip",
        "method",
        "target_count",
        "n_abstract_states",
        "state_compression_ratio",
        "normalized_start_gap",
        "normalized_policy_start_gap",
        "homogeneity_error",
        "time_median_sec",
        "total_speedup_median",
        "representation_scope",
    ]
    end_to_end_columns = [
        "map",
        "slip",
        "config_label",
        "method_spec",
        "n_boundary",
        "option_restriction_bias",
        "boundary_abstraction_bias",
        "kernel_actual_gap",
        "kernel_gap_bound",
        "planning_actual_gap",
        "planning_gap_bound",
        "primitive_to_solved_gap",
        "certified_total_bound",
        "certificate_holds",
        "normalized_primitive_to_solved_gap",
        "normalized_certified_total_bound",
    ]
    group_adaptive_columns = [
        "map",
        "slip",
        "method",
        "n_states",
        "n_basis",
        "n_boundary",
        "group_all_feasible",
        "n_groups_feasible",
        "group_total_violation",
        "selection_time_sec",
        "delta_backend",
        "probe_green_kernel_time_sec",
        "probe_operator_delta_time_sec",
        "active_weight_time_sec",
        "candidate_score_time_sec",
        "probe_cache_hit_rate",
        "kernel_time_sec",
        "smdp_solve_time_sec",
        "planning_speedup",
        "total_speedup",
        "break_even_tasks",
        "start_gap",
        "first_hit_tail_bound_max",
    ]
    random_maze_columns = [
        "method",
        "n_rows",
        "feasible_rate",
        "median_n_boundary",
        "median_state_compression",
        "median_selection_time_sec",
        "median_total_speedup",
        "max_start_gap",
        "max_group_total_violation",
    ]
    general_env_columns = [
        "env",
        "source",
        "method",
        "n_rows",
        "best_option_mode",
        "best_n_options",
        "best_target_count",
        "n_states",
        "best_n_boundary",
        "best_state_compression",
        "best_start_gap",
        "best_value_gap_max",
        "interpretation",
    ]
    general_env_aggregate_columns = [
        "env",
        "source",
        "method",
        "option_mode",
        "target_count",
        "n_seeds",
        "median_n_boundary",
        "median_state_compression_ratio",
        "median_normalized_start_gap",
        "max_normalized_start_gap",
        "median_normalized_value_gap_max",
        "group_feasible_rate",
        "median_construction_time_sec",
        "median_smdp_eval_time_sec",
    ]
    fair_frontier_columns = [
        "comparison_protocol",
        "method_group",
        "n_rows",
        "pareto_rows",
        "median_rate_budget_boundary_frac",
        "median_state_compression_ratio",
        "median_start_gap",
        "median_normalized_start_gap",
        "median_hidden_audit",
        "median_normalized_hidden_audit",
        "mean_group_feasible_rate",
        "median_total_speedup",
        "median_success_rate",
    ]
    constrained_columns = [
        "comparison_protocol",
        "method_group",
        "value_epsilon",
        "audit_epsilon",
        "n_cases_available",
        "n_cases_feasible",
        "constraint_coverage_rate",
        "paired_case_count",
        "median_rate_budget_boundary_frac",
        "median_state_compression_ratio",
        "state_compression_ci95_low",
        "state_compression_ci95_high",
        "median_total_speedup",
        "total_speedup_ci95_low",
        "total_speedup_ci95_high",
    ]
    budget_recovery_columns = [
        "map",
        "slip",
        "budget_frac",
        "recovered",
        "recovery_method",
        "minimal_max_splits",
        "minimal_n_boundary",
        "added_vertices_over_failed",
        "max_splits_tested",
        "largest_n_boundary",
        "violation_reduction",
        "best_total_violation",
        "failure_class",
    ]
    multitask_columns = [
        "source",
        "method_or_variant",
        "task_count",
        "n_rows",
        "median_amortized_speedup",
        "best_amortized_speedup",
        "median_planning_only_speedup",
        "median_break_even_tasks",
        "max_start_gap",
        "max_normalized_start_gap",
        "max_normalized_boundary_gap",
        "median_state_compression",
        "median_goal_interface",
        "median_goal_policies",
        "runtime_denominator",
    ]
    failure_columns = [
        "failure_mode",
        "evidence",
        "n_rows",
        "endpoint_feasible_rate",
        "robust_feasible_rate",
        "max_endpoint_violation",
        "max_robust_violation",
        "max_ambiguous_set_size",
        "tie_set_certified_rate",
        "max_tie_aware_total_speedup",
        "event_kernel_max_gap",
        "event_kernel_max_normalized_gap",
        "goal_conditioned_max_gap",
        "goal_conditioned_max_normalized_gap",
        "goal_conditioned_median_break_even",
        "goal_conditioned_best_speedup",
    ]
    solver_columns = [
        "solver",
        "beam_width",
        "oracle_pool_mode",
        "oracle_complete_candidate_universe",
        "n_rows",
        "boundary_match_rate",
        "zero_total_violation_gap_rate",
        "feasible_decision_match_rate",
        "median_selection_time_sec",
        "median_oracle_time_sec",
    ]
    certificate_columns = [
        "certificate",
        "rows",
        "interval_certified",
        "fallback_used",
        "tie_fallback_used",
        "curvature_fallback_used",
        "tie_set_certified",
        "epsilon_optimal_certified",
        "final_certified",
        "tie_aware_final_certified",
        "row_q_lt_1_edges",
        "weighted_q_lt_1_edges",
        "certificates_found",
        "rational_verified",
        "status",
    ]
    discovery_columns = [
        "mode",
        "n_rows",
        "median_wall_time_sec",
        "median_speedup_vs_full_recompute",
        "max_speedup_vs_full_recompute",
        "median_probe_green_kernel_time_sec",
        "median_probe_operator_delta_time_sec",
        "median_full_recompute_time_sec",
        "median_candidate_score_time_sec",
        "median_probe_cache_hit_rate",
    ]
    hybrid_refine_columns = [
        "source",
        "method",
        "top_k",
        "n_rows",
        "feasible_rate",
        "median_n_boundary",
        "median_selection_time_sec",
        "median_proposal_time_sec",
        "median_refine_time_sec",
        "median_kernel_time_sec",
        "median_upfront_time_sec",
        "median_total_speedup",
        "best_total_speedup",
        "median_break_even_tasks",
        "max_group_total_violation",
        "max_start_gap",
        "mean_surrogate_topk_recall",
        "total_exact_refine_calls",
        "median_adaptive_topk_used_mean",
        "max_adaptive_topk_used",
        "total_adaptive_topk_cap_hits",
        "total_refined_candidates",
        "median_probe_green_kernel_time_sec",
        "median_active_weight_time_sec",
        "median_candidate_score_time_sec",
    ]
    incremental_columns = [
        "mode",
        "n_rows",
        "selected_state_match_rate",
        "median_wall_time_sec",
        "median_speedup_vs_full_recompute",
        "max_speedup_vs_full_recompute",
        "max_score_error_vs_exact",
        "max_kernel_error_vs_exact",
        "max_hidden_error_vs_exact",
        "median_n_green_solves",
        "median_n_green_updates",
        "median_parent_update_rate",
    ]
    theorem_bridge_columns = [
        "paper_claim",
        "proof_status",
        "experiment_status",
        "manuscript_location",
        "remaining_gap",
    ]
    adaptive_topk_paired_columns = [
        "mode",
        "map",
        "slip",
        "fixed_top4_feasible",
        "adaptive_topk_feasible",
        "feasible_match",
        "adaptive_k_used_mean",
        "selection_speedup_fixed_over_adaptive",
        "lexicographic_regret_vs_fixed",
    ]
    adaptive_topk_hist_columns = [
        "method",
        "top_k_cap",
        "k_used",
        "n_steps",
        "n_feasible_stop",
        "n_cap_hit",
        "n_cap_without_selected_feasible",
    ]
    adaptive_topk_summary_columns = [
        "source",
        "method",
        "top_k_or_cap",
        "n_rows",
        "feasible_rate",
        "median_selection_time_sec",
        "total_exact_refine_calls",
        "total_refined_candidates",
        "median_adaptive_topk_used_mean",
    ]
    adaptive_topk_failure_columns = [
        "mode",
        "failure_class",
        "n_rows",
        "max_adaptive_group_total_violation",
        "maps",
        "slips",
    ]
    boundary_student_columns = [
        "source",
        "proposal",
        "target_validation_failure_recall",
        "n_rows",
        "mean_boundary_jaccard",
        "group_feasible_rate",
        "student_joint_constraint_rate",
        "teacher_joint_constraint_rate",
        "accepted_group_feasible_rate",
        "selective_accepted_joint_rate",
        "median_selection_speedup",
        "median_accepted_pipeline_speedup",
        "max_normalized_start_gap",
        "audit_rate",
        "failure_recall",
        "undetected_failures",
        "certification_status",
        "gate_status",
    ]
    best_total_unique = max((finite_float(row.get("total_speedup_unique_top_fallback")) for row in main_rows), default=float("nan"))
    best_total_tie = max((finite_float(row.get("total_speedup_tie_aware")) for row in main_rows), default=float("nan"))
    best_total_strong = max(
        (finite_float(row.get("total_speedup_tie_vs_strong_planner")) for row in main_rows),
        default=float("nan"),
    )
    strong_runtime_coverage = sum(
        1
        for row in main_rows
        if math.isfinite(finite_float(row.get("strong_full_planner_time_median_sec")))
    )
    best_multitask = max((finite_float(row.get("best_amortized_speedup")) for row in multitask_rows), default=float("nan"))
    best_edge_reward = max(
        (
            finite_float(row.get("best_amortized_speedup"))
            for row in multitask_rows
            if row.get("source") == "edge_reward_kernel_multitask"
            and row.get("method_or_variant") == "fixed_B_edge_reward_kernel"
        ),
        default=float("nan"),
    )
    worst_gap = max(
        (
            value
            for row in main_rows
            if math.isfinite(value := finite_float(row.get("start_gap")))
        ),
        default=float("nan"),
    )
    worst_normalized_gap = max(
        (
            value
            for row in main_rows
            if math.isfinite(value := finite_float(row.get("normalized_start_gap")))
        ),
        default=float("nan"),
    )
    final_certs = next(
        (row for row in certificate_rows if row.get("certificate") == "adaptive_frontier_tail_plus_top_set_fallback"),
        {},
    )
    main_display = [{col: row.get(col, "") for col in main_columns} for row in main_rows]
    compact_display = [{col: row.get(col, "") for col in compact_columns} for row in compact_rows]
    group_adaptive_display = [{col: row.get(col, "") for col in group_adaptive_columns} for row in group_adaptive_rows]
    solver_display = [{col: row.get(col, "") for col in solver_columns} for row in solver_rows]
    certificate_display = [{col: row.get(col, "") for col in certificate_columns} for row in certificate_rows]
    hybrid_refine_display = [{col: row.get(col, "") for col in hybrid_refine_columns} for row in hybrid_refine_rows]
    adaptive_paired = list(adaptive_topk_tables.get("paired_equivalence", []))
    adaptive_hist = list(adaptive_topk_tables.get("k_used_histogram", []))
    adaptive_summary = list(adaptive_topk_tables.get("fixedk_vs_adaptive_summary", []))
    adaptive_failure = list(adaptive_topk_tables.get("failure_mode_summary", []))
    paired_match = sum(1 for row in adaptive_paired if parse_bool(row.get("feasible_match")) is True)
    group_rows = [row for row in group_adaptive_rows if row.get("method") == "group_constrained"]
    group_feasible = sum(1 for row in group_rows if parse_bool(row.get("group_all_feasible")))
    hybrid_inputs = ", ".join(str(path) for path in args.hybrid_refine_csv)
    lines = [
        "# Submission Main Table",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report is the paper-facing aggregation layer. It keeps audit protocols separate, reports normalized gaps, and never treats the legacy Python VI denominator as the conservative runtime baseline when a matched strong planner measurement is available.",
        "",
        f"- best total speedup against the legacy Python VI implementation, unique-top fallback: `{best_total_unique:.4g}x`",
        f"- best total speedup against the legacy Python VI implementation, tie-aware certificate: `{best_total_tie:.4g}x`",
        f"- best tie-aware total speedup against the matched strongest full-state planner: `{best_total_strong:.4g}x`",
        f"- matched strong-planner coverage: `{strong_runtime_coverage}/{len(main_rows)}` runtime rows",
        f"- best multi-task amortized speedup in the current table: `{best_multitask:.4g}x` (legacy dense NumPy VI denominator)",
        f"- best fixed-B edge reward relabeling speedup: `{best_edge_reward:.4g}x` (not a matched sparse-VI claim)",
        f"- worst start-value gap in that table: `{worst_gap:.4g}`; normalized: `{worst_normalized_gap:.4g}`",
        f"- adaptive final certified decisions under unique-top fallback: `{final_certs.get('final_certified', '')}/{final_certs.get('rows', '')}`",
        f"- adaptive final certified decisions under tie-aware reporting: `{final_certs.get('tie_aware_final_certified', '')}/{final_certs.get('rows', '')}`",
        f"- larger group-constrained adaptive feasible rows: `{group_feasible}/{len(group_rows)}`",
        f"- adaptive top-k paired feasible matches: `{paired_match}/{len(adaptive_paired)}`",
        "- exact Green is the reference operator; certified adaptive Green plus tie-aware top-set/epsilon certificates are the runtime implementation; fixed-K and weighted spectral certificates are ablations/appendix diagnostics.",
        "",
        "## Main Runtime Table",
        "",
        markdown_table(main_display, main_columns) if main_display else "_No main runtime rows found._",
        "",
        "## One-Shot Operator Versus Search",
        "",
        "The one-shot rows measure one frozen sparse Green response and one threshold pass; iterative/exact search appears only in the paired speedup columns. Final-kernel time is reported separately, so extraction speed is not confused with graph-model construction.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in one_shot_columns} for row in one_shot_rows],
            one_shot_columns,
        )
        if one_shot_rows
        else "_No one-shot operator rows found._",
        "",
        "### Frozen Group-FD Prefix Audit",
        "",
        "This diagnostic freezes one exact multi-probe candidate order, audits prefixes without rescoring, and exposes nonmonotone feasibility caused by the changing boundary/option library.",
        "",
        markdown_table(one_shot_group_prefix_rows, one_shot_group_prefix_columns)
        if one_shot_group_prefix_rows
        else "_No frozen one-shot group-prefix rows found._",
        "",
        "### Learned Boundary Student Ablation",
        "",
        "The transition-graph GNN is an uncertified ablation, not a second proposed method. The bounded constraint-aware follow-up improves raw proposal quality but fails its routing gate: selective rows are invalid as safe pipelines when held-out failures remain undetected, while full audit is slower than the explicit backend.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in boundary_student_columns} for row in boundary_student_rows],
            boundary_student_columns,
        )
        if boundary_student_rows
        else "_No learned boundary-student rows found._",
        "",
        "## Runtime By Boundary Selector",
        "",
        "This aggregation prevents the fastest endpoint or topology selector from being reported as a typical RD-selector gain.",
        "",
        markdown_table(selector_runtime_rows, selector_runtime_columns)
        if selector_runtime_rows
        else "_No selector-level runtime rows found._",
        "",
        "## Strong Full-State Planner Audit",
        "",
        markdown_table(planner_rows, planner_columns) if planner_rows else "_Strong-planner measurements pending._",
        "",
        "## Compact Baseline Aggregate",
        "",
        markdown_table(compact_display, compact_columns) if compact_display else "_No compact benchmark rows found._",
        "",
        "## Direct State-Abstraction And Schur Baselines",
        "",
        "Exact/epsilon homogeneous aggregation preserves a primitive-action abstract MDP; Q*-aggregation and policy-Kron are explicitly labeled oracles because they consume full optimal information.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in abstraction_columns} for row in abstraction_rows],
            abstraction_columns,
        )
        if abstraction_rows
        else "_Direct abstraction baseline measurements pending._",
        "",
        "## Primitive-To-Graph Gap Decomposition",
        "",
        "This table separates option-family restriction from boundary commitment, kernel approximation, and incomplete graph planning. The certified bound is expected to be conservative; the actual component gaps are retained to expose looseness.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in end_to_end_columns} for row in end_to_end_rows],
            end_to_end_columns,
        )
        if end_to_end_rows
        else "_End-to-end decomposition measurements pending._",
        "",
        "## Larger Group-Constrained Adaptive",
        "",
        markdown_table(group_adaptive_display, group_adaptive_columns) if group_adaptive_display else "_No larger group-constrained adaptive rows found._",
        "",
        "## Random Maze Generalization",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in random_maze_columns} for row in random_maze_rows],
            random_maze_columns,
        )
        if random_maze_rows
        else "_No random-maze rows found._",
        "",
        "## Random-Maze Boundary-Budget Recovery",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in budget_recovery_columns} for row in budget_recovery_rows],
            budget_recovery_columns,
        )
        if budget_recovery_rows
        else "_Boundary-budget recovery measurements pending._",
        "",
        "## General Finite-MDP Portability Smoke",
        "",
        "These rows are adapter/claim-boundary evidence, not a replacement for the main grid compression table. PointMaze is a discretized empirical MDP; Taxi highlights structured state variables that purely spatial boundary selection does not preserve.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in general_env_columns} for row in general_env_rows],
            general_env_columns,
        )
        if general_env_rows
        else "_No general-environment rows found._",
        "",
        "## External Environment Multi-Seed Aggregate",
        "",
        "A low group-risk violation is not treated as a value guarantee: held-out normalized value gaps are reported next to group feasibility.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in general_env_aggregate_columns} for row in general_env_aggregate_rows],
            general_env_aggregate_columns,
        )
        if general_env_aggregate_rows
        else "_Multi-seed external-environment aggregate pending._",
        "",
        "## Fair Budget Frontier",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in fair_frontier_columns} for row in fair_frontier_rows],
            fair_frontier_columns,
        )
        if fair_frontier_rows
        else "_No fair-budget frontier rows found._",
        "",
        "## Epsilon-Constrained Frontier",
        "",
        f"Canonical slice: normalized value gap <= `{args.constrained_value_epsilon}` and normalized audit <= `{args.constrained_audit_epsilon}`. Coverage is reported before compression or speedup.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in constrained_columns} for row in constrained_rows],
            constrained_columns,
        )
        if constrained_rows
        else "_No methods satisfy or report the canonical constrained slice._",
        "",
        "## Multi-Task And Edge Reward Compression",
        "",
        "Edge-reward speedups in this legacy artifact use dense NumPy full-state VI. They support amortization and representation compression, but are not reported as wins over the matched sparse-vectorized planner. Gaps use the discounted unit-reward bound when the original shard did not record a task-specific value scale.",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in multitask_columns} for row in multitask_rows],
            multitask_columns,
        )
        if multitask_rows
        else "_No multi-task rows found._",
        "",
        "## Failure Modes",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in failure_columns} for row in failure_mode_rows],
            failure_columns,
        )
        if failure_mode_rows
        else "_No failure-mode rows found._",
        "",
        "## Solver Validity Aggregate",
        "",
        markdown_table(solver_display, solver_columns) if solver_display else "_No solver-validity rows found._",
        "",
        "## Discovery Profile Aggregate",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in discovery_columns} for row in discovery_profile_rows],
            discovery_columns,
        )
        if discovery_profile_rows
        else "_No discovery-profile rows found._",
        "",
        "## Hybrid Discovery Acceleration",
        "",
        markdown_table(hybrid_refine_display, hybrid_refine_columns)
        if hybrid_refine_display
        else "_No hybrid surrogate/refine rows found._",
        "",
        "## Adaptive Top-K Diagnostics",
        "",
        "### Paired Feasibility",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in adaptive_topk_paired_columns} for row in adaptive_paired],
            adaptive_topk_paired_columns,
        )
        if adaptive_paired
        else "_No adaptive top-k paired rows found._",
        "",
        "### K-Used Histogram",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in adaptive_topk_hist_columns} for row in adaptive_hist],
            adaptive_topk_hist_columns,
        )
        if adaptive_hist
        else "_No adaptive top-k histogram rows found._",
        "",
        "### Fixed-K Vs Adaptive Cap",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in adaptive_topk_summary_columns} for row in adaptive_summary],
            adaptive_topk_summary_columns,
        )
        if adaptive_summary
        else "_No adaptive top-k summary rows found._",
        "",
        "### Adaptive Failure Summary",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in adaptive_topk_failure_columns} for row in adaptive_failure],
            adaptive_topk_failure_columns,
        )
        if adaptive_failure
        else "_No adaptive top-k failure rows found._",
        "",
        "## Incremental Green Update Aggregate",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in incremental_columns} for row in incremental_green_rows],
            incremental_columns,
        )
        if incremental_green_rows
        else "_No incremental-Green rows found._",
        "",
        "## Theorem-To-Experiment Bridge",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in theorem_bridge_columns} for row in theorem_bridge_rows],
            theorem_bridge_columns,
        )
        if theorem_bridge_rows
        else "_No theorem bridge rows found._",
        "",
        "## Certificate Appendix Summary",
        "",
        markdown_table(certificate_display, certificate_columns) if certificate_display else "_No certificate rows found._",
        "",
        "## Source Artifacts",
        "",
        f"- large-scale adaptive: `{args.large_scale_csv}`",
        f"- one-shot operator suites: `{', '.join(str(path) for path in args.one_shot_csv)}`",
        f"- frozen one-shot group-prefix audit: `{args.one_shot_group_frontier_csv}`",
        f"- learned boundary student: `{args.boundary_student_csv}`",
        f"- explicit boundary-student baselines: `{args.boundary_student_baseline_csv}`",
        f"- empirical selective audit: `{args.boundary_student_selective_csv}`",
        f"- constraint-aware student: `{args.boundary_constraint_student_csv}`",
        f"- constraint-aware selective audit: `{args.boundary_constraint_selective_csv}`",
        f"- constraint-aware full audit: `{args.boundary_constraint_full_audit_csv}`",
        f"- strong full-state planners: `{args.planner_baseline_csv}`",
        f"- core benchmark: `{args.core_csv}`",
        f"- direct state-abstraction baselines: `{args.abstraction_csv}`",
        f"- primitive-to-graph gap decomposition: `{args.end_to_end_csv}`",
        f"- adaptive certification: `{args.adaptive_cert_csv}`",
        f"- larger group-constrained adaptive: `{args.group_adaptive_csv}`",
        f"- random maze generalization: `{args.random_maze_csv}`",
        f"- random-maze boundary-budget recovery: `{args.budget_recovery_csv}`",
        f"- general finite-MDP smoke: `{args.general_env_csv}`",
        f"- general finite-MDP multi-seed aggregate: `{args.general_env_aggregate_csv}`",
        f"- fair budget frontier: `{args.fair_frontier_csv}`",
        f"- epsilon-constrained frontier: `{args.constrained_frontier_csv}`",
        f"- amortized multitask: `{args.amortized_csv}`",
        f"- edge reward multitask: `{args.edge_reward_csv}`",
        f"- solver validity: `{args.solver_csv}`",
        f"- discovery profile/cache: `{args.discovery_profile_csv}`",
        f"- hybrid surrogate/refine: `{hybrid_inputs}`",
        f"- adaptive top-k diagnostics: `{args.adaptive_topk_diagnostics_dir}`",
        f"- incremental Green update: `{args.incremental_green_csv}`",
        f"- incremental group semantic diff: `{args.incremental_semantic_summary}`",
        f"- graph abstraction figures: `{args.figure_summary}`",
        f"- theorem/experiment bridge: `{args.theorem_bridge_csv}`",
        f"- linear solver thread scaling: `{args.thread_scaling_summary}`",
        f"- weighted spectral certificate: `{args.weighted_cert_csv}`",
        f"- conditioned rational certificate: `{args.conditioned_cert_csv}`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the paper-facing main table from existing experiment artifacts.")
    parser.add_argument("--large-scale-csv", type=Path, default=Path("experiments/output/large_scale_compression_adaptive/large_scale_compression.csv"))
    parser.add_argument(
        "--one-shot-csv",
        type=Path,
        nargs="*",
        default=[
            Path("experiments/output/one_shot_rd_operator/one_shot_rd_operator.csv"),
            Path("experiments/output/one_shot_rd_operator_random/one_shot_rd_operator.csv"),
            Path("experiments/output/one_shot_rd_operator_random_reference/one_shot_rd_operator.csv"),
            Path("experiments/output/one_shot_rd_operator_xl_end_to_end/one_shot_rd_operator.csv"),
        ],
    )
    parser.add_argument(
        "--one-shot-group-frontier-csv",
        type=Path,
        default=Path(
            "experiments/output/one_shot_group_fd_frontier/"
            "one_shot_group_fd_frontier.csv"
        ),
    )
    parser.add_argument(
        "--boundary-student-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_downstream_graphonly_test/summary.csv"
        ),
    )
    parser.add_argument(
        "--boundary-student-baseline-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_downstream_graphonly_baselines/summary.csv"
        ),
    )
    parser.add_argument(
        "--boundary-student-selective-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_selective_audit_graphonly/"
            "heldout_selective_audit.csv"
        ),
    )
    parser.add_argument(
        "--boundary-constraint-student-csv",
        type=Path,
        default=Path("experiments/output/boundary_constraint_student_test/summary.csv"),
    )
    parser.add_argument(
        "--boundary-constraint-selective-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_constraint_selective_audit/"
            "heldout_selective_audit.csv"
        ),
    )
    parser.add_argument(
        "--boundary-constraint-full-audit-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_constraint_selective_audit/"
            "heldout_full_audit.csv"
        ),
    )
    parser.add_argument("--planner-baseline-csv", type=Path, default=Path("experiments/output/planner_baseline_comparison/strongest_planner_by_case.csv"))
    parser.add_argument("--core-csv", type=Path, default=Path("experiments/output/core_benchmark/core_benchmark.csv"))
    parser.add_argument("--abstraction-csv", type=Path, default=Path("experiments/output/abstraction_baseline_comparison/abstraction_baseline_aggregate.csv"))
    parser.add_argument("--end-to-end-csv", type=Path, default=Path("experiments/output/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv"))
    parser.add_argument("--adaptive-cert-csv", type=Path, default=Path("experiments/output/adaptive_green_certification/certification_summary.csv"))
    parser.add_argument("--group-adaptive-csv", type=Path, default=Path("experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv"))
    parser.add_argument("--random-maze-csv", type=Path, default=Path("experiments/output/random_maze_generalization/random_maze_generalization.csv"))
    parser.add_argument("--budget-recovery-csv", type=Path, default=Path("experiments/output/random_maze_budget_recovery/random_maze_budget_recovery_summary.csv"))
    parser.add_argument("--general-env-csv", type=Path, default=Path("experiments/output/general_env_benchmark/general_env_benchmark.csv"))
    parser.add_argument("--general-env-aggregate-csv", type=Path, default=Path("experiments/output/general_env_benchmark/general_env_aggregate.csv"))
    parser.add_argument("--fair-frontier-csv", type=Path, default=Path("experiments/output/fair_budget_frontier/fair_budget_frontier_summary.csv"))
    parser.add_argument("--constrained-frontier-csv", type=Path, default=Path("experiments/output/fair_budget_frontier/epsilon_constrained_frontier.csv"))
    parser.add_argument("--constrained-value-epsilon", type=float, default=1e-2)
    parser.add_argument("--constrained-audit-epsilon", type=float, default=1e-3)
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.97,
        help="Discount used only for the conservative unit-reward normalization fallback.",
    )
    parser.add_argument("--amortized-csv", type=Path, default=Path("experiments/output/amortized_multitask/amortized_multitask.csv"))
    parser.add_argument("--edge-reward-csv", type=Path, default=Path("experiments/output/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv"))
    parser.add_argument("--solver-csv", type=Path, default=Path("experiments/output/solver_validity/solver_validity.csv"))
    parser.add_argument("--discovery-profile-csv", type=Path, default=Path("experiments/output/discovery_profile_cache/discovery_profile_cache.csv"))
    parser.add_argument(
        "--hybrid-refine-csv",
        type=Path,
        nargs="*",
        default=[
            Path("experiments/output/hybrid_surrogate_refine/hybrid_surrogate_refine.csv"),
            Path("experiments/output/hybrid_topk_ablation/hybrid_surrogate_refine.csv"),
            Path("experiments/output/hybrid_adaptive_topk_refine/hybrid_surrogate_refine.csv"),
        ],
        help="One or more hybrid surrogate/refine CSVs to aggregate into the discovery acceleration table.",
    )
    parser.add_argument("--incremental-green-csv", type=Path, default=Path("experiments/output/incremental_green_update/incremental_green_update_aggregate.csv"))
    parser.add_argument("--incremental-semantic-summary", type=Path, default=Path("experiments/output/group_incremental_semantic_diff/summary.md"))
    parser.add_argument("--figure-summary", type=Path, default=Path("experiments/output/graph_abstraction_figures/summary.md"))
    parser.add_argument("--theorem-bridge-csv", type=Path, default=Path("experiments/output/theorem_experiment_bridge/theorem_experiment_bridge.csv"))
    parser.add_argument("--thread-scaling-summary", type=Path, default=Path("experiments/output/linear_solver_thread_scaling/summary.md"))
    parser.add_argument("--weighted-cert-csv", type=Path, default=Path("experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv"))
    parser.add_argument("--conditioned-cert-csv", type=Path, default=Path("experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv"))
    parser.add_argument("--adaptive-topk-diagnostics-dir", type=Path, default=Path("experiments/output/adaptive_topk_diagnostics"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/submission_main_table"))
    args = parser.parse_args()

    large_rows = read_csv_rows(args.large_scale_csv)
    one_shot_raw = read_csv_many(args.one_shot_csv)
    one_shot_group_prefix_raw = read_csv_rows(args.one_shot_group_frontier_csv)
    boundary_student_raw = read_csv_rows(args.boundary_student_csv)
    boundary_student_baseline_raw = read_csv_rows(args.boundary_student_baseline_csv)
    boundary_student_selective_raw = read_csv_rows(args.boundary_student_selective_csv)
    boundary_constraint_student_raw = read_csv_rows(args.boundary_constraint_student_csv)
    boundary_constraint_selective_raw = read_csv_rows(args.boundary_constraint_selective_csv)
    boundary_constraint_full_audit_raw = read_csv_rows(
        args.boundary_constraint_full_audit_csv
    )
    planner_raw = read_csv_rows(args.planner_baseline_csv)
    core_rows = read_csv_rows(args.core_csv)
    abstraction_raw = read_csv_rows(args.abstraction_csv)
    end_to_end_raw = read_csv_rows(args.end_to_end_csv)
    adaptive_rows = read_csv_rows(args.adaptive_cert_csv)
    group_adaptive_raw = read_csv_rows(args.group_adaptive_csv)
    random_maze_raw = read_csv_rows(args.random_maze_csv)
    budget_recovery_raw = read_csv_rows(args.budget_recovery_csv)
    general_env_raw = read_csv_rows(args.general_env_csv)
    general_env_aggregate_raw = read_csv_rows(args.general_env_aggregate_csv)
    fair_frontier_raw = read_csv_rows(args.fair_frontier_csv)
    constrained_frontier_raw = read_csv_rows(args.constrained_frontier_csv)
    amortized_raw = read_csv_rows(args.amortized_csv)
    edge_reward_raw = read_csv_rows(args.edge_reward_csv)
    solver_rows_raw = read_csv_rows(args.solver_csv)
    discovery_profile_raw = read_csv_rows(args.discovery_profile_csv)
    hybrid_refine_raw = read_csv_many(args.hybrid_refine_csv)
    incremental_green_rows = read_csv_rows(args.incremental_green_csv)
    theorem_bridge_raw = read_csv_rows(args.theorem_bridge_csv)
    weighted_rows = read_csv_rows(args.weighted_cert_csv)
    conditioned_rows = read_csv_rows(args.conditioned_cert_csv)
    adaptive_topk_tables = {
        "paired_equivalence": read_csv_rows(args.adaptive_topk_diagnostics_dir / "paired_equivalence.csv"),
        "k_used_histogram": read_csv_rows(args.adaptive_topk_diagnostics_dir / "k_used_histogram.csv"),
        "fixedk_vs_adaptive_summary": read_csv_rows(args.adaptive_topk_diagnostics_dir / "fixedk_vs_adaptive_summary.csv"),
        "score_regret": read_csv_rows(args.adaptive_topk_diagnostics_dir / "score_regret.csv"),
        "failure_modes": read_csv_rows(args.adaptive_topk_diagnostics_dir / "failure_modes.csv"),
        "failure_mode_summary": read_csv_rows(args.adaptive_topk_diagnostics_dir / "failure_mode_summary.csv"),
    }

    main_rows = build_main_runtime_rows(large_rows, adaptive_rows, planner_raw, args.gamma)
    one_shot_rows = build_one_shot_summary_rows(one_shot_raw)
    one_shot_group_prefix_rows = build_one_shot_group_prefix_rows(one_shot_group_prefix_raw)
    boundary_student_rows = build_boundary_student_rows(
        boundary_student_raw,
        boundary_student_baseline_raw,
        boundary_student_selective_raw,
        boundary_constraint_student_raw,
        boundary_constraint_selective_raw,
        boundary_constraint_full_audit_raw,
    )
    selector_runtime_rows = build_selector_runtime_rows(main_rows)
    compact_rows = build_compact_baseline_rows(core_rows)
    abstraction_rows = build_abstraction_rows(abstraction_raw)
    end_to_end_rows = build_end_to_end_rows(end_to_end_raw)
    group_adaptive_rows = build_group_adaptive_rows(group_adaptive_raw)
    random_maze_rows = build_random_maze_rows(random_maze_raw)
    budget_recovery_rows = build_budget_recovery_rows(budget_recovery_raw)
    general_env_rows = build_general_env_rows(general_env_raw)
    general_env_aggregate_rows = build_general_env_aggregate_rows(general_env_aggregate_raw)
    fair_frontier_rows = build_fair_frontier_rows(fair_frontier_raw)
    constrained_rows = build_constrained_rows(
        constrained_frontier_raw,
        value_epsilon=args.constrained_value_epsilon,
        audit_epsilon=args.constrained_audit_epsilon,
    )
    multitask_rows = build_multitask_rows(amortized_raw, edge_reward_raw, args.gamma)
    failure_mode_rows = build_failure_mode_rows(main_rows, group_adaptive_rows, edge_reward_raw, args.gamma)
    solver_rows = build_solver_rows(solver_rows_raw)
    discovery_profile_rows = build_discovery_profile_rows(discovery_profile_raw)
    hybrid_refine_rows = build_hybrid_refine_rows(hybrid_refine_raw)
    theorem_bridge_rows = build_theorem_bridge_rows(theorem_bridge_raw)
    certificate_rows = build_certificate_rows(adaptive_rows, weighted_rows, conditioned_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "submission_runtime_table.csv", main_rows)
    write_csv_all_fields(args.out_dir / "one_shot_operator_summary.csv", one_shot_rows)
    write_csv_all_fields(
        args.out_dir / "one_shot_group_prefix_summary.csv", one_shot_group_prefix_rows
    )
    write_csv_all_fields(
        args.out_dir / "boundary_student_ablation.csv", boundary_student_rows
    )
    write_csv_all_fields(args.out_dir / "runtime_by_boundary_selector.csv", selector_runtime_rows)
    write_csv_all_fields(args.out_dir / "strong_planner_audit.csv", planner_raw)
    write_csv_all_fields(args.out_dir / "compact_baseline_aggregate.csv", compact_rows)
    write_csv_all_fields(args.out_dir / "direct_abstraction_baselines.csv", abstraction_rows)
    write_csv_all_fields(args.out_dir / "end_to_end_gap_decomposition.csv", end_to_end_rows)
    write_csv_all_fields(args.out_dir / "group_constrained_adaptive_table.csv", group_adaptive_rows)
    write_csv_all_fields(args.out_dir / "random_maze_generalization_aggregate.csv", random_maze_rows)
    write_csv_all_fields(args.out_dir / "random_maze_budget_recovery.csv", budget_recovery_rows)
    write_csv_all_fields(args.out_dir / "general_env_portability_smoke.csv", general_env_rows)
    write_csv_all_fields(args.out_dir / "general_env_multiseed_aggregate.csv", general_env_aggregate_rows)
    write_csv_all_fields(args.out_dir / "fair_budget_frontier_aggregate.csv", fair_frontier_rows)
    write_csv_all_fields(args.out_dir / "epsilon_constrained_frontier.csv", constrained_rows)
    write_csv_all_fields(args.out_dir / "multitask_edge_reward_aggregate.csv", multitask_rows)
    write_csv_all_fields(args.out_dir / "failure_modes.csv", failure_mode_rows)
    write_csv_all_fields(args.out_dir / "solver_validity_aggregate.csv", solver_rows)
    write_csv_all_fields(args.out_dir / "discovery_profile_aggregate.csv", discovery_profile_rows)
    write_csv_all_fields(args.out_dir / "discovery_acceleration_table.csv", hybrid_refine_rows)
    write_csv_all_fields(args.out_dir / "adaptive_topk_paired_equivalence.csv", adaptive_topk_tables["paired_equivalence"])
    write_csv_all_fields(args.out_dir / "adaptive_topk_k_used_histogram.csv", adaptive_topk_tables["k_used_histogram"])
    write_csv_all_fields(args.out_dir / "adaptive_topk_fixedk_vs_adaptive_summary.csv", adaptive_topk_tables["fixedk_vs_adaptive_summary"])
    write_csv_all_fields(args.out_dir / "adaptive_topk_score_regret.csv", adaptive_topk_tables["score_regret"])
    write_csv_all_fields(args.out_dir / "adaptive_topk_failure_modes.csv", adaptive_topk_tables["failure_modes"])
    write_csv_all_fields(args.out_dir / "adaptive_topk_failure_mode_summary.csv", adaptive_topk_tables["failure_mode_summary"])
    write_csv_all_fields(args.out_dir / "incremental_green_update_aggregate.csv", incremental_green_rows)
    write_csv_all_fields(args.out_dir / "theorem_experiment_bridge.csv", theorem_bridge_rows)
    write_csv_all_fields(args.out_dir / "certificate_appendix_summary.csv", certificate_rows)
    (args.out_dir / "submission_main_table.json").write_text(
        json.dumps(
            {
                "runtime_table": main_rows,
                "one_shot_operator_summary": one_shot_rows,
                "one_shot_group_prefix_summary": one_shot_group_prefix_rows,
                "boundary_student_ablation": boundary_student_rows,
                "runtime_by_boundary_selector": selector_runtime_rows,
                "strong_planner_audit": planner_raw,
                "compact_baseline_aggregate": compact_rows,
                "direct_abstraction_baselines": abstraction_rows,
                "end_to_end_gap_decomposition": end_to_end_rows,
                "group_constrained_adaptive_table": group_adaptive_rows,
                "random_maze_generalization_aggregate": random_maze_rows,
                "random_maze_budget_recovery": budget_recovery_rows,
                "general_env_portability_smoke": general_env_rows,
                "general_env_multiseed_aggregate": general_env_aggregate_rows,
                "fair_budget_frontier_aggregate": fair_frontier_rows,
                "epsilon_constrained_frontier": constrained_rows,
                "multitask_edge_reward_aggregate": multitask_rows,
                "failure_modes": failure_mode_rows,
                "solver_validity_aggregate": solver_rows,
                "discovery_profile_aggregate": discovery_profile_rows,
                "discovery_acceleration_table": hybrid_refine_rows,
                "adaptive_topk_diagnostics": adaptive_topk_tables,
                "incremental_green_update_aggregate": incremental_green_rows,
                "theorem_experiment_bridge": theorem_bridge_rows,
                "certificate_appendix_summary": certificate_rows,
            },
            indent=2,
            default=json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        args.out_dir / "summary.md",
        main_rows,
        one_shot_rows,
        one_shot_group_prefix_rows,
        selector_runtime_rows,
        planner_raw,
        compact_rows,
        abstraction_rows,
        end_to_end_rows,
        group_adaptive_rows,
        random_maze_rows,
        general_env_rows,
        general_env_aggregate_rows,
        fair_frontier_rows,
        constrained_rows,
        budget_recovery_rows,
        multitask_rows,
        failure_mode_rows,
        solver_rows,
        certificate_rows,
        discovery_profile_rows,
        hybrid_refine_rows,
        incremental_green_rows,
        theorem_bridge_rows,
        adaptive_topk_tables,
        boundary_student_rows,
        args,
    )


if __name__ == "__main__":
    main()
