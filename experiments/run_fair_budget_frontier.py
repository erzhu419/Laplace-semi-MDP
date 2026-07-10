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
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def rate(values: Iterable[bool | None]) -> float:
    vals = [value for value in values if value is not None]
    return sum(1 for value in vals if value) / len(vals) if vals else float("nan")


def method_group(method: str, source: str) -> str:
    text = method.lower()
    if text in {"full_vi", "full_mdp"}:
        return "full_mdp"
    if text == "endpoints":
        return "baseline:endpoints"
    if "turn_articulation" in text:
        return "baseline:dense_turn"
    if "group_constrained" in text:
        return "ours:group_rd"
    if "graph_rd" in text:
        return "ours:rd_graph"
    if "eigen" in text:
        return "option_baseline:eigen"
    if "between" in text or "bottleneck" in text:
        return "option_baseline:bottleneck"
    if "random" in text:
        return "option_baseline:random"
    if "coverage" in text:
        return "option_baseline:coverage"
    if "exact_model_minimization" in text or "epsilon_homogeneous" in text:
        return "abstraction:model_minimization"
    if "qstar_oracle" in text:
        return "abstraction:qstar_oracle"
    if "policy_kron" in text:
        return "reduction:policy_kron_oracle"
    return source


def normalized_gap(row: Mapping[str, object], field: str, gamma: float) -> float:
    explicit = finite_float(row.get(f"normalized_{field}"))
    if math.isfinite(explicit):
        return explicit
    gap = finite_float(row.get(field))
    if not math.isfinite(gap):
        return float("nan")
    scale = finite_float(row.get("value_scale"))
    if not math.isfinite(scale) or scale <= 0.0:
        start_value = finite_float(
            row.get("start_value_full"),
            finite_float(row.get("start_value_primitive")),
        )
        scale = max(1.0, abs(start_value)) if math.isfinite(start_value) else 1.0 / max(1e-12, 1.0 - gamma)
    return gap / scale


def occupancy_audit(row: Mapping[str, object], n_states: float) -> Tuple[float, float, str]:
    audit = finite_float(row.get("occupancy_struct_hidden_distinct"))
    if math.isfinite(audit):
        return audit, audit / max(1.0, n_states), "occupancy_struct_hidden_distinct"
    audit = finite_float(row.get("hidden_audit_distinct_mean"))
    if math.isfinite(audit):
        return audit, audit / max(1.0, n_states), "rollout_hidden_distinct"
    return float("nan"), float("nan"), "not_measured"


def normalize_core_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        method = str(row.get("method_spec") or row.get("method") or "")
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        rate_budget = n_boundary / max(1.0, n_states)
        gamma = finite_float(row.get("gamma"), 0.97)
        audit, normalized_audit, audit_metric = occupancy_audit(row, n_states)
        out.append(
            {
                "source": "core_benchmark",
                "comparison_protocol": "core_benchmark",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "core_benchmark"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": rate_budget,
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": finite_float(row.get("planning_time_speedup_vs_full_vi")),
                "total_speedup": finite_float(row.get("total_time_speedup_vs_full_vi")),
                "start_gap": finite_float(row.get("start_gap")),
                "normalized_start_gap": normalized_gap(row, "start_gap", gamma),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "normalized_value_gap_max": normalized_gap(row, "value_gap_max", gamma),
                "hidden_audit": audit,
                "normalized_hidden_audit": normalized_audit,
                "audit_metric": audit_metric,
                "success_rate": finite_float(row.get("success_rate"), 1.0 if method == "full_vi" else float("nan")),
                "group_feasible": parse_bool(row.get("group_all_feasible")) if row.get("group_all_feasible", "") != "" else None,
                "budget_label": "exact_or_same_protocol",
            }
        )
    return out


def normalize_group_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        method = str(row.get("method", ""))
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        gamma = finite_float(row.get("gamma"), 0.97)
        audit = finite_float(row.get("group_total_violation"), 0.0)
        out.append(
            {
                "source": "group_constrained_adaptive",
                "comparison_protocol": "group_constrained_adaptive",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "group_constrained_adaptive"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": n_boundary / max(1.0, n_states),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": finite_float(row.get("planning_speedup")),
                "total_speedup": finite_float(row.get("total_speedup")),
                "start_gap": finite_float(row.get("start_gap")),
                "normalized_start_gap": normalized_gap(row, "start_gap", gamma),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "normalized_value_gap_max": normalized_gap(row, "value_gap_max", gamma),
                "hidden_audit": audit,
                "normalized_hidden_audit": audit,
                "audit_metric": "group_total_violation",
                "success_rate": float("nan"),
                "group_feasible": parse_bool(row.get("group_all_feasible")),
                "budget_label": f"group_budget_frac={row.get('budget_frac', '')}",
            }
        )
    return out


def normalize_large_scale_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        method = str(row.get("method_spec") or row.get("method") or "")
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        gamma = finite_float(row.get("gamma"), 0.97)
        audit, normalized_audit, audit_metric = occupancy_audit(row, n_states)
        out.append(
            {
                "source": "large_scale_compression",
                "comparison_protocol": "large_scale_compression",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "large_scale_compression"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": n_boundary / max(1.0, n_states),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": finite_float(row.get("planning_time_speedup_vs_full_vi")),
                "total_speedup": finite_float(row.get("total_time_speedup_vs_full_vi")),
                "start_gap": finite_float(row.get("start_gap")),
                "normalized_start_gap": normalized_gap(row, "start_gap", gamma),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "normalized_value_gap_max": normalized_gap(row, "value_gap_max", gamma),
                "hidden_audit": audit,
                "normalized_hidden_audit": normalized_audit,
                "audit_metric": audit_metric,
                "success_rate": float("nan"),
                "group_feasible": None,
                "budget_label": "large_scale_same_protocol",
            }
        )
    return out


def normalize_random_maze_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        method = str(row.get("method", ""))
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        gamma = finite_float(row.get("gamma"), 0.97)
        audit = finite_float(row.get("group_total_violation"), 0.0)
        out.append(
            {
                "source": "random_maze_generalization",
                "comparison_protocol": "random_maze_generalization",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "random_maze_generalization"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": n_boundary / max(1.0, n_states),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": finite_float(row.get("planning_speedup")),
                "total_speedup": finite_float(row.get("total_speedup")),
                "start_gap": finite_float(row.get("start_gap")),
                "normalized_start_gap": normalized_gap(row, "start_gap", gamma),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "normalized_value_gap_max": normalized_gap(row, "value_gap_max", gamma),
                "hidden_audit": audit,
                "normalized_hidden_audit": audit,
                "audit_metric": "group_total_violation",
                "success_rate": float("nan"),
                "group_feasible": parse_bool(row.get("group_all_feasible")),
                "budget_label": f"random_group_budget_frac={row.get('budget_frac', '')}",
            }
        )
    return out


def normalize_option_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        method = str(row.get("method") or row.get("method_family") or "")
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        gamma = finite_float(row.get("gamma"), 0.97)
        audit, normalized_audit, audit_metric = occupancy_audit(row, n_states)
        out.append(
            {
                "source": "option_baseline_frontier",
                "comparison_protocol": "option_baseline_frontier",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "option_baseline_frontier"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": n_boundary / max(1.0, n_states),
                "state_compression_ratio": n_states / max(1.0, n_boundary),
                "planning_speedup": float("nan"),
                "total_speedup": float("nan"),
                "start_gap": finite_float(row.get("start_gap")),
                "normalized_start_gap": normalized_gap(row, "start_gap", gamma),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "normalized_value_gap_max": normalized_gap(row, "value_gap_max", gamma),
                "hidden_audit": audit,
                "normalized_hidden_audit": normalized_audit,
                "audit_metric": audit_metric,
                "success_rate": finite_float(row.get("success_rate")),
                "group_feasible": parse_bool(row.get("feasible") or row.get("group_all_feasible")),
                "budget_label": "option_count_or_boundary_count",
            }
        )
    return out


def normalize_abstraction_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        method = str(row.get("method", ""))
        n_states = finite_float(row.get("n_states"))
        n_abstract = finite_float(row.get("n_abstract_states"))
        out.append(
            {
                "source": "abstraction_baseline_comparison",
                "comparison_protocol": "abstraction_baseline_comparison",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "abstraction_baseline_comparison"),
                "n_states": n_states,
                "n_boundary": n_abstract,
                "rate_budget_boundary_frac": n_abstract / max(1.0, n_states),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": float("nan"),
                "total_speedup": finite_float(row.get("total_speedup_median")),
                "start_gap": float("nan"),
                "normalized_start_gap": finite_float(row.get("normalized_policy_start_gap")),
                "value_gap_max": finite_float(row.get("policy_value_gap_max")),
                "normalized_value_gap_max": float("nan"),
                "hidden_audit": float("nan"),
                "normalized_hidden_audit": float("nan"),
                "audit_metric": "not_measured",
                "success_rate": float("nan"),
                "group_feasible": None,
                "budget_label": f"target_count={row.get('target_count', '')}",
                "representation_scope": row.get("representation_scope", ""),
            }
        )
    return out


def dominates(a: Mapping[str, object], b: Mapping[str, object], eps: float = 1e-12) -> bool:
    a_rate = finite_float(a.get("rate_budget_boundary_frac"))
    b_rate = finite_float(b.get("rate_budget_boundary_frac"))
    a_gap = finite_float(a.get("normalized_start_gap"))
    b_gap = finite_float(b.get("normalized_start_gap"))
    a_hidden = finite_float(a.get("normalized_hidden_audit"))
    b_hidden = finite_float(b.get("normalized_hidden_audit"))
    a_success = finite_float(a.get("success_rate"), 1.0)
    b_success = finite_float(b.get("success_rate"), 1.0)
    if not all(math.isfinite(x) for x in [a_rate, b_rate, a_gap, b_gap]):
        return False
    if not math.isfinite(a_hidden):
        a_hidden = 0.0
    if not math.isfinite(b_hidden):
        b_hidden = 0.0
    if not math.isfinite(a_success):
        a_success = 1.0
    if not math.isfinite(b_success):
        b_success = 1.0
    no_worse = (
        a_rate <= b_rate + eps
        and a_gap <= b_gap + eps
        and a_hidden <= b_hidden + eps
        and a_success + eps >= b_success
    )
    strictly_better = (
        a_rate < b_rate - eps
        or a_gap < b_gap - eps
        or a_hidden < b_hidden - eps
        or a_success > b_success + eps
    )
    return no_worse and strictly_better


def add_pareto_flags(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    by_case: Dict[Tuple[str, str, str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        by_case[
            (
                str(row.get("comparison_protocol", row.get("source", ""))),
                str(row.get("map", "")),
                str(row.get("slip", "")),
                str(row.get("audit_metric", "")),
            )
        ].append(row)
    out: List[Dict[str, object]] = []
    for _case, group in by_case.items():
        for row in group:
            dominated_by = [
                str(other.get("method", ""))
                for other in group
                if other is not row and dominates(other, row)
            ]
            out.append(
                {
                    **row,
                    "pareto_nondominated": not dominated_by,
                    "pareto_dominated_by": ";".join(dominated_by[:5]),
                }
            )
    return out


def build_summary(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                str(row.get("comparison_protocol", row.get("source", ""))),
                str(row.get("method_group", "")),
            )
        ].append(row)
    summary: List[Dict[str, object]] = []
    for (protocol, group_name), group in sorted(grouped.items()):
        summary.append(
            {
                "comparison_protocol": protocol,
                "method_group": group_name,
                "n_rows": len(group),
                "pareto_rows": sum(1 for row in group if bool(row.get("pareto_nondominated"))),
                "median_rate_budget_boundary_frac": median(
                    finite_float(row.get("rate_budget_boundary_frac")) for row in group
                ),
                "median_state_compression_ratio": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "median_start_gap": median(finite_float(row.get("start_gap")) for row in group),
                "median_normalized_start_gap": median(
                    finite_float(row.get("normalized_start_gap")) for row in group
                ),
                "median_hidden_audit": median(finite_float(row.get("hidden_audit")) for row in group),
                "median_normalized_hidden_audit": median(
                    finite_float(row.get("normalized_hidden_audit")) for row in group
                ),
                "mean_group_feasible_rate": rate(parse_bool(row.get("group_feasible")) for row in group),
                "median_total_speedup": median(finite_float(row.get("total_speedup")) for row in group),
                "median_success_rate": median(finite_float(row.get("success_rate")) for row in group),
            }
        )
    return summary


def bootstrap_median_interval(
    values: Sequence[float],
    rng: np.random.Generator,
    n_bootstrap: int,
) -> Tuple[float, float, float]:
    array = np.asarray([value for value in values if math.isfinite(value)], dtype=float)
    if array.size == 0:
        return float("nan"), float("nan"), float("nan")
    point = float(np.median(array))
    if array.size == 1 or n_bootstrap <= 0:
        return point, point, point
    sampled = rng.choice(array, size=(n_bootstrap, array.size), replace=True)
    medians = np.median(sampled, axis=1)
    low, high = np.quantile(medians, [0.025, 0.975])
    return point, float(low), float(high)


def _passes_constraints(
    row: Mapping[str, object],
    value_epsilon: float,
    audit_epsilon: float,
    success_floor: float,
) -> bool:
    value_gap = finite_float(row.get("normalized_start_gap"))
    if not math.isfinite(value_gap) or value_gap > value_epsilon + 1e-12:
        return False
    feasible = parse_bool(row.get("group_feasible"))
    if feasible is False:
        return False
    success = finite_float(row.get("success_rate"))
    if math.isfinite(success) and success + 1e-12 < success_floor:
        return False
    audit_metric = str(row.get("audit_metric", "not_measured"))
    audit = finite_float(row.get("normalized_hidden_audit"))
    if audit_metric == "not_measured":
        return math.isinf(audit_epsilon)
    return math.isfinite(audit) and audit <= audit_epsilon + 1e-12


def build_constrained_frontier(
    rows: Sequence[Mapping[str, object]],
    value_epsilons: Sequence[float],
    audit_epsilons: Sequence[float],
    success_floor: float,
    n_bootstrap: int,
    seed: int,
) -> List[Dict[str, object]]:
    available: Dict[Tuple[str, str, str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        available[
            (
                str(row.get("comparison_protocol", row.get("source", ""))),
                str(row.get("map", "")),
                str(row.get("slip", "")),
                str(row.get("method_group", "")),
            )
        ].append(row)

    output: List[Dict[str, object]] = []
    rng = np.random.default_rng(seed)
    protocols = sorted({key[0] for key in available})
    for value_epsilon in value_epsilons:
        for audit_epsilon in audit_epsilons:
            selected: Dict[Tuple[str, str, str, str], Mapping[str, object]] = {}
            for key, candidates in available.items():
                passing = [
                    row
                    for row in candidates
                    if _passes_constraints(row, value_epsilon, audit_epsilon, success_floor)
                ]
                if not passing:
                    continue
                selected[key] = min(
                    passing,
                    key=lambda row: (
                        finite_float(row.get("rate_budget_boundary_frac"), float("inf")),
                        -finite_float(row.get("total_speedup"), -float("inf")),
                    ),
                )

            for protocol in protocols:
                method_groups = sorted({key[3] for key in available if key[0] == protocol})
                case_sets = {
                    group: {
                        (key[1], key[2])
                        for key in selected
                        if key[0] == protocol and key[3] == group
                    }
                    for group in method_groups
                }
                paired_cases = set.intersection(*case_sets.values()) if method_groups else set()
                for group in method_groups:
                    group_available_cases = {
                        (key[1], key[2])
                        for key in available
                        if key[0] == protocol and key[3] == group
                    }
                    group_rows = [
                        row
                        for key, row in selected.items()
                        if key[0] == protocol and key[3] == group
                    ]
                    compression = [finite_float(row.get("state_compression_ratio")) for row in group_rows]
                    speedup = [finite_float(row.get("total_speedup")) for row in group_rows]
                    rate_budget = [finite_float(row.get("rate_budget_boundary_frac")) for row in group_rows]
                    comp_mid, comp_low, comp_high = bootstrap_median_interval(
                        compression, rng, n_bootstrap
                    )
                    speed_mid, speed_low, speed_high = bootstrap_median_interval(
                        speedup, rng, n_bootstrap
                    )
                    output.append(
                        {
                            "comparison_protocol": protocol,
                            "method_group": group,
                            "value_epsilon": value_epsilon,
                            "audit_epsilon": audit_epsilon,
                            "success_floor": success_floor,
                            "n_cases_available": len(group_available_cases),
                            "n_cases_feasible": len(group_rows),
                            "constraint_coverage_rate": len(group_rows) / max(1, len(group_available_cases)),
                            "paired_case_count": len(paired_cases),
                            "median_rate_budget_boundary_frac": median(rate_budget),
                            "median_state_compression_ratio": comp_mid,
                            "state_compression_ci95_low": comp_low,
                            "state_compression_ci95_high": comp_high,
                            "median_total_speedup": speed_mid,
                            "total_speedup_ci95_low": speed_low,
                            "total_speedup_ci95_high": speed_high,
                        }
                    )
    return output


def write_report(
    rows: Sequence[Mapping[str, object]],
    summary: Sequence[Mapping[str, object]],
    constrained: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    summary_columns = [
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
    row_columns = [
        "source",
        "comparison_protocol",
        "map",
        "slip",
        "method",
        "method_group",
        "n_states",
        "n_boundary",
        "rate_budget_boundary_frac",
        "state_compression_ratio",
        "start_gap",
        "normalized_start_gap",
        "hidden_audit",
        "normalized_hidden_audit",
        "audit_metric",
        "success_rate",
        "group_feasible",
        "total_speedup",
        "pareto_nondominated",
        "pareto_dominated_by",
    ]
    pareto = [row for row in rows if bool(row.get("pareto_nondominated"))]
    constrained_report = [
        row
        for row in constrained
        if abs(finite_float(row.get("value_epsilon")) - args.report_value_epsilon) <= 1e-15
        and (
            (math.isinf(finite_float(row.get("audit_epsilon"))) and math.isinf(args.report_audit_epsilon))
            or abs(finite_float(row.get("audit_epsilon")) - args.report_audit_epsilon) <= 1e-15
        )
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
    lines = [
        "# Fair Budget Frontier",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This aggregation keeps incomparable audit protocols separate, normalizes value gaps by a task value scale, and reports epsilon-constrained coverage before any cross-method summary. Pareto dominance is computed only within a shared source protocol and audit metric.",
        "",
        f"- total normalized rows: `{len(rows)}`",
        f"- Pareto non-dominated rows: `{len(pareto)}`",
        "",
        "## Method-Group Summary",
        "",
        markdown_table(summary, summary_columns) if summary else "_No summary rows._",
        "",
        "## Epsilon-Constrained Frontier",
        "",
        f"Canonical report slice: value epsilon `{args.report_value_epsilon}`, audit epsilon `{args.report_audit_epsilon}`. The CSV contains the full threshold grid.",
        "",
        markdown_table(constrained_report, constrained_columns) if constrained_report else "_No constrained rows._",
        "",
        "## Pareto Rows",
        "",
        markdown_table([{col: row.get(col, "") for col in row_columns} for row in pareto], row_columns)
        if pareto
        else "_No Pareto rows._",
        "",
        "## Source Artifacts",
        "",
        f"- core benchmark: `{args.core_csv}`",
        f"- large-scale compression: `{args.large_scale_csv}`",
        f"- group-constrained adaptive: `{args.group_adaptive_csv}`",
        f"- random maze generalization: `{args.random_maze_csv}`",
        f"- option baseline frontier: `{args.option_frontier_csv}`",
        f"- direct abstraction baselines: `{args.abstraction_csv}`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a fair rate/distortion frontier across graph and option baselines.")
    parser.add_argument("--core-csv", type=Path, default=Path("experiments/output/core_benchmark/core_benchmark.csv"))
    parser.add_argument(
        "--large-scale-csv",
        type=Path,
        default=Path("experiments/output/large_scale_compression_adaptive/large_scale_compression.csv"),
    )
    parser.add_argument(
        "--group-adaptive-csv",
        type=Path,
        default=Path("experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv"),
    )
    parser.add_argument(
        "--random-maze-csv",
        type=Path,
        default=Path("experiments/output/random_maze_generalization/random_maze_generalization.csv"),
    )
    parser.add_argument(
        "--option-frontier-csv",
        type=Path,
        default=Path("experiments/output/option_baseline_frontier_xl/frontier_all.csv"),
    )
    parser.add_argument(
        "--abstraction-csv",
        type=Path,
        default=Path("experiments/output/abstraction_baseline_comparison/abstraction_baseline_aggregate.csv"),
    )
    parser.add_argument("--value-epsilons", nargs="+", type=float, default=[1e-6, 1e-3, 1e-2, 5e-2])
    parser.add_argument("--audit-epsilons", nargs="+", type=float, default=[0.0, 1e-3, 1e-2, float("inf")])
    parser.add_argument("--success-floor", type=float, default=0.95)
    parser.add_argument("--report-value-epsilon", type=float, default=1e-2)
    parser.add_argument("--report-audit-epsilon", type=float, default=1e-3)
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/fair_budget_frontier"))
    args = parser.parse_args()

    rows = (
        normalize_core_rows(read_csv_rows(args.core_csv))
        + normalize_large_scale_rows(read_csv_rows(args.large_scale_csv))
        + normalize_group_rows(read_csv_rows(args.group_adaptive_csv))
        + normalize_random_maze_rows(read_csv_rows(args.random_maze_csv))
        + normalize_option_rows(read_csv_rows(args.option_frontier_csv))
        + normalize_abstraction_rows(read_csv_rows(args.abstraction_csv))
    )
    rows = add_pareto_flags(rows)
    summary = build_summary(rows)
    constrained = build_constrained_frontier(
        rows,
        value_epsilons=args.value_epsilons,
        audit_epsilons=args.audit_epsilons,
        success_floor=args.success_floor,
        n_bootstrap=args.bootstrap_reps,
        seed=args.bootstrap_seed,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "fair_budget_frontier.csv", rows)
    write_csv_all_fields(args.out_dir / "fair_budget_frontier_summary.csv", summary)
    write_csv_all_fields(args.out_dir / "epsilon_constrained_frontier.csv", constrained)
    (args.out_dir / "fair_budget_frontier.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, summary, constrained, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
