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

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def break_even_tasks(upfront_cost: float, full_time: float, graph_solve_time: float) -> int | str:
    saving_per_task = full_time - graph_solve_time
    if not math.isfinite(upfront_cost) or not math.isfinite(saving_per_task) or saving_per_task <= 0.0:
        return ""
    return int(math.ceil(max(0.0, upfront_cost) / max(1e-12, saving_per_task)))


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
) -> List[Dict[str, object]]:
    cert_by_key = choose_certification_rows(cert_rows)
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
        out.append(
            {
                "map": row.get("map", ""),
                "boundary_selector": method_spec,
                "method": "certified_adaptive_green_rd",
                "n_states": row.get("n_states", ""),
                "n_boundary": row.get("n_boundary", ""),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "memory_compression_ratio": finite_float(row.get("memory_compression_ratio")),
                "first_hit_used_steps_max": row.get("first_hit_used_steps_max", ""),
                "tail_bound_max": finite_float(row.get("first_hit_tail_bound_max")),
                "full_vi_time_sec": full_time,
                "upfront_time_sec": upfront,
                "smdp_solve_time_sec": smdp,
                "total_time_unique_top_fallback_sec": total_with_fallback,
                "total_time_with_tie_certificate_sec": total_with_tie_certificate,
                "planning_speedup": finite_float(row.get("planning_time_speedup_vs_full_vi")),
                "total_speedup_unique_top_fallback": full_time / max(1e-12, total_with_fallback),
                "total_speedup_tie_aware": full_time / max(1e-12, total_with_tie_certificate),
                "unique_top_break_even_tasks": break_even_tasks(upfront + fallback_proxy, full_time, smdp),
                "amortization_break_even_tasks": break_even_tasks(upfront + tie_proxy, full_time, smdp),
                "backup_compression_ratio": finite_float(row.get("backup_compression_ratio")),
                "start_gap": finite_float(row.get("start_gap")),
                "value_gap_max": finite_float(row.get("value_gap_max")),
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


def build_solver_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for (solver, beam_width), group in sorted(group_rows(rows, ["solver", "beam_width"]).items()):
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


def build_fair_frontier_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        out.append(
            {
                "method_group": row.get("method_group", ""),
                "n_rows": row.get("n_rows", ""),
                "pareto_rows": row.get("pareto_rows", ""),
                "median_rate_budget_boundary_frac": finite_float(row.get("median_rate_budget_boundary_frac")),
                "median_state_compression_ratio": finite_float(row.get("median_state_compression_ratio")),
                "median_start_gap": finite_float(row.get("median_start_gap")),
                "median_hidden_audit": finite_float(row.get("median_hidden_audit")),
                "mean_group_feasible_rate": finite_float(row.get("mean_group_feasible_rate")),
                "median_total_speedup": finite_float(row.get("median_total_speedup")),
                "median_success_rate": finite_float(row.get("median_success_rate")),
            }
        )
    return out


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


def write_report(
    out_path: Path,
    main_rows: Sequence[Mapping[str, object]],
    compact_rows: Sequence[Mapping[str, object]],
    group_adaptive_rows: Sequence[Mapping[str, object]],
    random_maze_rows: Sequence[Mapping[str, object]],
    fair_frontier_rows: Sequence[Mapping[str, object]],
    solver_rows: Sequence[Mapping[str, object]],
    certificate_rows: Sequence[Mapping[str, object]],
    discovery_profile_rows: Sequence[Mapping[str, object]],
    incremental_green_rows: Sequence[Mapping[str, object]],
    theorem_bridge_rows: Sequence[Mapping[str, object]],
    args: argparse.Namespace,
) -> None:
    main_columns = [
        "map",
        "boundary_selector",
        "method",
        "n_states",
        "n_boundary",
        "state_compression_ratio",
        "first_hit_used_steps_max",
        "tail_bound_max",
        "full_vi_time_sec",
        "upfront_time_sec",
        "smdp_solve_time_sec",
        "total_time_unique_top_fallback_sec",
        "total_time_with_tie_certificate_sec",
        "planning_speedup",
        "total_speedup_unique_top_fallback",
        "total_speedup_tie_aware",
        "unique_top_break_even_tasks",
        "amortization_break_even_tasks",
        "start_gap",
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
    fair_frontier_columns = [
        "method_group",
        "n_rows",
        "pareto_rows",
        "median_rate_budget_boundary_frac",
        "median_state_compression_ratio",
        "median_start_gap",
        "median_hidden_audit",
        "mean_group_feasible_rate",
        "median_total_speedup",
        "median_success_rate",
    ]
    solver_columns = [
        "solver",
        "beam_width",
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
    best_total_unique = max((finite_float(row.get("total_speedup_unique_top_fallback")) for row in main_rows), default=float("nan"))
    best_total_tie = max((finite_float(row.get("total_speedup_tie_aware")) for row in main_rows), default=float("nan"))
    worst_gap = max((finite_float(row.get("start_gap")) for row in main_rows), default=float("nan"))
    final_certs = next(
        (row for row in certificate_rows if row.get("certificate") == "adaptive_frontier_tail_plus_top_set_fallback"),
        {},
    )
    main_display = [{col: row.get(col, "") for col in main_columns} for row in main_rows]
    compact_display = [{col: row.get(col, "") for col in compact_columns} for row in compact_rows]
    group_adaptive_display = [{col: row.get(col, "") for col in group_adaptive_columns} for row in group_adaptive_rows]
    solver_display = [{col: row.get(col, "") for col in solver_columns} for row in solver_rows]
    certificate_display = [{col: row.get(col, "") for col in certificate_columns} for row in certificate_rows]
    group_rows = [row for row in group_adaptive_rows if row.get("method") == "group_constrained"]
    group_feasible = sum(1 for row in group_rows if parse_bool(row.get("group_all_feasible")))
    lines = [
        "# Submission Main Table",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report is the paper-facing aggregation layer. It does not rerun heavy experiments; it reads the current public CSV artifacts and aligns the main runtime result, compact baselines, exhaustive-oracle solver validity, and certificate appendices.",
        "",
        f"- best certified adaptive total speedup with unique-top fallback: `{best_total_unique:.4g}x`",
        f"- best certified adaptive total speedup with tie-aware certificate: `{best_total_tie:.4g}x`",
        f"- worst certified adaptive start-value gap in that table: `{worst_gap:.4g}`",
        f"- adaptive final certified decisions under unique-top fallback: `{final_certs.get('final_certified', '')}/{final_certs.get('rows', '')}`",
        f"- adaptive final certified decisions under tie-aware reporting: `{final_certs.get('tie_aware_final_certified', '')}/{final_certs.get('rows', '')}`",
        f"- larger group-constrained adaptive feasible rows: `{group_feasible}/{len(group_rows)}`",
        "- exact Green is the reference operator; certified adaptive Green plus tie-aware top-set/epsilon certificates are the runtime implementation; fixed-K and weighted spectral certificates are ablations/appendix diagnostics.",
        "",
        "## Main Runtime Table",
        "",
        markdown_table(main_display, main_columns) if main_display else "_No main runtime rows found._",
        "",
        "## Compact Baseline Aggregate",
        "",
        markdown_table(compact_display, compact_columns) if compact_display else "_No compact benchmark rows found._",
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
        "## Fair Budget Frontier",
        "",
        markdown_table(
            [{col: row.get(col, "") for col in fair_frontier_columns} for row in fair_frontier_rows],
            fair_frontier_columns,
        )
        if fair_frontier_rows
        else "_No fair-budget frontier rows found._",
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
        f"- core benchmark: `{args.core_csv}`",
        f"- adaptive certification: `{args.adaptive_cert_csv}`",
        f"- larger group-constrained adaptive: `{args.group_adaptive_csv}`",
        f"- random maze generalization: `{args.random_maze_csv}`",
        f"- fair budget frontier: `{args.fair_frontier_csv}`",
        f"- solver validity: `{args.solver_csv}`",
        f"- discovery profile/cache: `{args.discovery_profile_csv}`",
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
    parser.add_argument("--core-csv", type=Path, default=Path("experiments/output/core_benchmark/core_benchmark.csv"))
    parser.add_argument("--adaptive-cert-csv", type=Path, default=Path("experiments/output/adaptive_green_certification/certification_summary.csv"))
    parser.add_argument("--group-adaptive-csv", type=Path, default=Path("experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv"))
    parser.add_argument("--random-maze-csv", type=Path, default=Path("experiments/output/random_maze_generalization/random_maze_generalization.csv"))
    parser.add_argument("--fair-frontier-csv", type=Path, default=Path("experiments/output/fair_budget_frontier/fair_budget_frontier_summary.csv"))
    parser.add_argument("--solver-csv", type=Path, default=Path("experiments/output/solver_validity/solver_validity.csv"))
    parser.add_argument("--discovery-profile-csv", type=Path, default=Path("experiments/output/discovery_profile_cache/discovery_profile_cache.csv"))
    parser.add_argument("--incremental-green-csv", type=Path, default=Path("experiments/output/incremental_green_update/incremental_green_update_aggregate.csv"))
    parser.add_argument("--incremental-semantic-summary", type=Path, default=Path("experiments/output/group_incremental_semantic_diff/summary.md"))
    parser.add_argument("--figure-summary", type=Path, default=Path("experiments/output/graph_abstraction_figures/summary.md"))
    parser.add_argument("--theorem-bridge-csv", type=Path, default=Path("experiments/output/theorem_experiment_bridge/theorem_experiment_bridge.csv"))
    parser.add_argument("--thread-scaling-summary", type=Path, default=Path("experiments/output/linear_solver_thread_scaling/summary.md"))
    parser.add_argument("--weighted-cert-csv", type=Path, default=Path("experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv"))
    parser.add_argument("--conditioned-cert-csv", type=Path, default=Path("experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/submission_main_table"))
    args = parser.parse_args()

    large_rows = read_csv_rows(args.large_scale_csv)
    core_rows = read_csv_rows(args.core_csv)
    adaptive_rows = read_csv_rows(args.adaptive_cert_csv)
    group_adaptive_raw = read_csv_rows(args.group_adaptive_csv)
    random_maze_raw = read_csv_rows(args.random_maze_csv)
    fair_frontier_raw = read_csv_rows(args.fair_frontier_csv)
    solver_rows_raw = read_csv_rows(args.solver_csv)
    discovery_profile_raw = read_csv_rows(args.discovery_profile_csv)
    incremental_green_rows = read_csv_rows(args.incremental_green_csv)
    theorem_bridge_raw = read_csv_rows(args.theorem_bridge_csv)
    weighted_rows = read_csv_rows(args.weighted_cert_csv)
    conditioned_rows = read_csv_rows(args.conditioned_cert_csv)

    main_rows = build_main_runtime_rows(large_rows, adaptive_rows)
    compact_rows = build_compact_baseline_rows(core_rows)
    group_adaptive_rows = build_group_adaptive_rows(group_adaptive_raw)
    random_maze_rows = build_random_maze_rows(random_maze_raw)
    fair_frontier_rows = build_fair_frontier_rows(fair_frontier_raw)
    solver_rows = build_solver_rows(solver_rows_raw)
    discovery_profile_rows = build_discovery_profile_rows(discovery_profile_raw)
    theorem_bridge_rows = build_theorem_bridge_rows(theorem_bridge_raw)
    certificate_rows = build_certificate_rows(adaptive_rows, weighted_rows, conditioned_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "submission_runtime_table.csv", main_rows)
    write_csv_all_fields(args.out_dir / "compact_baseline_aggregate.csv", compact_rows)
    write_csv_all_fields(args.out_dir / "group_constrained_adaptive_table.csv", group_adaptive_rows)
    write_csv_all_fields(args.out_dir / "random_maze_generalization_aggregate.csv", random_maze_rows)
    write_csv_all_fields(args.out_dir / "fair_budget_frontier_aggregate.csv", fair_frontier_rows)
    write_csv_all_fields(args.out_dir / "solver_validity_aggregate.csv", solver_rows)
    write_csv_all_fields(args.out_dir / "discovery_profile_aggregate.csv", discovery_profile_rows)
    write_csv_all_fields(args.out_dir / "incremental_green_update_aggregate.csv", incremental_green_rows)
    write_csv_all_fields(args.out_dir / "theorem_experiment_bridge.csv", theorem_bridge_rows)
    write_csv_all_fields(args.out_dir / "certificate_appendix_summary.csv", certificate_rows)
    (args.out_dir / "submission_main_table.json").write_text(
        json.dumps(
            {
                "runtime_table": main_rows,
                "compact_baseline_aggregate": compact_rows,
                "group_constrained_adaptive_table": group_adaptive_rows,
                "random_maze_generalization_aggregate": random_maze_rows,
                "fair_budget_frontier_aggregate": fair_frontier_rows,
                "solver_validity_aggregate": solver_rows,
                "discovery_profile_aggregate": discovery_profile_rows,
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
        compact_rows,
        group_adaptive_rows,
        random_maze_rows,
        fair_frontier_rows,
        solver_rows,
        certificate_rows,
        discovery_profile_rows,
        incremental_green_rows,
        theorem_bridge_rows,
        args,
    )


if __name__ == "__main__":
    main()
