#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import build_compressed_model_measured, parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from one_shot_rd_operator import apply_one_shot_rd_operator
from run_rd_group_constrained import (
    ProbeDeltaCache,
    evaluate_boundary_on_groups,
    fixed_basis,
    parse_group_specs,
    probe_delta_table,
    score_candidates,
    select_group_constrained_boundary,
)


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def break_even_tasks(upfront_cost: float, full_time: float, graph_solve_time: float) -> int | str:
    saving_per_task = full_time - graph_solve_time
    if not math.isfinite(upfront_cost) or not math.isfinite(saving_per_task) or saving_per_task <= 0.0:
        return ""
    return int(math.ceil(max(0.0, upfront_cost) / max(1e-12, saving_per_task)))


def group_context(
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    args: argparse.Namespace,
) -> Tuple[GridWorld, Dict[str, List[str]], Dict[str, object], List[int], List[int], Dict[str, float], Dict[str, object]]:
    grid = GridWorld(rows)
    lens_groups = parse_group_specs(args.lens_groups)
    recipe = dict(LEARNED_RECIPES[args.recipe])
    basis = fixed_basis(
        map_label,
        grid=grid,
        kinds=args.fixed_basis_kinds,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.probe_top_fraction,
        random_count=args.fixed_random_count,
    )
    endpoint_boundary = sorted(set(endpoint_boundary_states(grid)).intersection(set(basis)))
    endpoint_eval, _endpoint_rows = evaluate_boundary_on_groups(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=endpoint_boundary,
        lens_groups=lens_groups,
        budgets={group: 0.0 for group in lens_groups},
        test_probes=args.test_probes if args.include_test_probes else [],
        gamma=args.gamma,
        slip=slip,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.cvar_alpha,
    )
    initial_group_risks = {group: float(value) for group, value in endpoint_eval["group_risks"].items()}
    budgets = {
        group: float(args.budget_frac) * float(initial_group_risks.get(group, 0.0))
        for group in lens_groups
    }
    return grid, lens_groups, recipe, basis, endpoint_boundary, budgets, {
        "initial_group_risks": initial_group_risks,
        "endpoint_eval": endpoint_eval,
    }


def construct_group_boundary(
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    lens_groups: Mapping[str, Sequence[str]],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
    delta_backend: str,
) -> Tuple[List[int], Dict[str, object], float]:
    probe_cache = ProbeDeltaCache(enabled=not args.disable_probe_cache)
    boundary, trace, _candidates, _probes, selection_time = select_group_constrained_boundary(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        lens_groups=lens_groups,
        budgets=budgets,
        gamma=args.gamma,
        slip=slip,
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
        delta_backend=delta_backend,
    )
    selection_profile = probe_cache.summary()
    return sorted(set(boundary)), {
        "selection_trace": trace,
        "constructor_stop_reason": trace[-1]["stop_reason"] if trace else "none",
        "selection_profile": selection_profile,
        "delta_backend": delta_backend,
    }, selection_time


def group_eval_from_risks(group_risks: Mapping[str, float], group_violations: Mapping[str, float]) -> Dict[str, object]:
    violations = {group: float(value) for group, value in group_violations.items()}
    return {
        "group_risks": {group: float(value) for group, value in group_risks.items()},
        "group_violations": violations,
        "total_violation": sum(violations.values()),
        "max_violation": max(violations.values(), default=0.0),
        "n_groups_feasible": sum(1 for value in violations.values() if value <= 1e-9),
        "all_groups_feasible": all(value <= 1e-9 for value in violations.values()),
        "test_bits_mean": float("nan"),
        "test_bits_cvar": float("nan"),
    }


def group_eval_from_trace(trace: Sequence[Mapping[str, object]]) -> Dict[str, object] | None:
    if not trace:
        return None
    final = trace[-1]
    try:
        group_risks = json.loads(str(final.get("group_risks", "{}")))
        group_violations = json.loads(str(final.get("group_violations", "{}")))
    except json.JSONDecodeError:
        return None
    if not isinstance(group_risks, dict) or not isinstance(group_violations, dict):
        return None
    return group_eval_from_risks(group_risks, group_violations)


def evaluate_group_boundary(
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
) -> Dict[str, object]:
    eval_result, _eval_rows = evaluate_boundary_on_groups(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        test_probes=args.test_probes,
        gamma=args.gamma,
        slip=slip,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.cvar_alpha,
    )
    return dict(eval_result)


def run_method(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    method: str,
    lens_groups: Mapping[str, Sequence[str]],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    endpoint_boundary: Sequence[int],
    budgets: Mapping[str, float],
    context_info: Mapping[str, object],
    args: argparse.Namespace,
) -> Dict[str, object]:
    if method == "endpoints":
        boundary = list(endpoint_boundary)
        constructor = {"constructor_method": "endpoints"}
        selection_time = 0.0
        group_eval = dict(context_info["endpoint_eval"])  # type: ignore[arg-type]
    elif method == "one_shot_rd":
        operator = apply_one_shot_rd_operator(
            grid=GridWorld(rows),
            slip=slip,
            gamma=args.gamma,
            mandatory_boundary=endpoint_boundary,
            active_pairs=[
                (int(source), int(target))
                for source in endpoint_boundary
                for target in endpoint_boundary
                if int(source) != int(target)
            ],
            candidate_states=basis,
            probe_anchors=basis,
            probe_count=getattr(args, "one_shot_probe_count", None),
            truncation_steps=getattr(args, "one_shot_steps", 256),
            tail_tol=getattr(args, "one_shot_tail_tol", 1e-6),
            max_splits=args.max_splits,
            channel_threshold=getattr(args, "one_shot_threshold", 0.15),
            min_channel_support=getattr(args, "one_shot_min_channel_support", 2),
            mandatory_exclusion_radius=getattr(args, "one_shot_exclusion_radius", 1),
            gate_channels=(),
            candidate_universe=getattr(args, "one_shot_candidate_universe", "turn_articulation"),
        )
        boundary = list(operator.boundary)
        selection_time = float(operator.timings["total_operator_time_sec"])
        constructor = {
            "constructor_method": "one_shot_rd",
            "constructor_stop_reason": "one_shot_threshold",
            "delta_backend": "one_shot_sparse_green",
            "one_shot_diagnostics": operator.diagnostics,
            **operator.timings,
        }
        group_eval = evaluate_group_boundary(
            map_label=map_label,
            rows=rows,
            slip=slip,
            boundary=boundary,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            budgets=budgets,
            args=args,
        )
    elif method == "one_shot_group_fd":
        all_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
        probe_cache = ProbeDeltaCache(enabled=False)
        started = time.perf_counter()
        before_by_probe, deltas_by_state, probe_rows = probe_delta_table(
            map_name=map_label,
            step=0,
            rows=rows,
            recipe=recipe,
            basis=basis,
            boundary=endpoint_boundary,
            probes=all_probes,
            gamma=args.gamma,
            slip=slip,
            lambda_struct=args.lambda_struct,
            edge_weight=args.edge_weight,
            probe_top_fraction=args.probe_top_fraction,
            max_candidates=0,
            probe_cache=probe_cache,
            delta_backend="operator",
        )
        scored, predicted_risks, predicted_violations = score_candidates(
            map_name=map_label,
            step=0,
            basis=basis,
            boundary=endpoint_boundary,
            lens_groups=lens_groups,
            budgets=budgets,
            before_by_probe=before_by_probe,
            deltas_by_state=deltas_by_state,
            group_risk_kind=args.group_risk_kind,
            cvar_alpha=args.cvar_alpha,
            score_mode=args.score_mode,
            rate_tie_break=args.rate_tie_break,
        )
        selected = [int(row["candidate_state"]) for row in scored[: args.max_splits]]
        boundary = sorted(set(endpoint_boundary).union(selected))
        selection_time = time.perf_counter() - started
        constructor = {
            "constructor_method": "one_shot_group_fd",
            "constructor_stop_reason": "one_shot_frozen_top_m",
            "delta_backend": "one_shot_frozen_group_fd",
            "predicted_group_risks": predicted_risks,
            "predicted_group_violations": predicted_violations,
            "n_frozen_candidates": len(scored),
            "n_green_response_passes": len(all_probes),
            "n_candidate_insertion_evaluations": 0,
            "n_beam_expansions": 0,
            "probe_rows": probe_rows,
            "selection_profile": probe_cache.summary(),
        }
        group_eval = evaluate_group_boundary(
            map_label=map_label,
            rows=rows,
            slip=slip,
            boundary=boundary,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            budgets=budgets,
            args=args,
        )
    elif method in {"group_constrained", "group_constrained_operator", "group_constrained_incremental"}:
        if method == "group_constrained_incremental":
            delta_backend = "insertion_score"
        elif method == "group_constrained_operator":
            delta_backend = "operator"
        else:
            delta_backend = args.delta_backend
        boundary, constructor, selection_time = construct_group_boundary(
            map_label=map_label,
            rows=rows,
            slip=slip,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            budgets=budgets,
            args=args,
            delta_backend=delta_backend,
        )
        trace_group_eval = group_eval_from_trace(constructor.get("selection_trace", []))  # type: ignore[arg-type]
        group_eval = trace_group_eval
        if group_eval is None or args.include_test_probes or delta_backend != "operator":
            group_eval = evaluate_group_boundary(
                map_label=map_label,
                rows=rows,
                slip=slip,
                boundary=boundary,
                lens_groups=lens_groups,
                recipe=recipe,
                basis=basis,
                budgets=budgets,
                args=args,
            )
        if trace_group_eval is not None:
            trace_feasible = bool(trace_group_eval["all_groups_feasible"])
            exact_feasible = bool(group_eval["all_groups_feasible"])
            if delta_backend != "operator" and exact_feasible and not trace_feasible:
                prior_stop = str(constructor.get("constructor_stop_reason", "none"))
                constructor = {
                    **constructor,
                    "constructor_stop_reason": f"{prior_stop}_exact_feasible",
                }
            constructor = {
                **constructor,
                "trace_group_total_violation": trace_group_eval["total_violation"],
                "trace_group_max_violation": trace_group_eval["max_violation"],
                "trace_group_all_feasible": trace_group_eval["all_groups_feasible"],
            }
    else:
        raise ValueError(f"Unknown method: {method}")
    selection_profile = constructor.get("selection_profile", {})
    if not isinstance(selection_profile, Mapping):
        selection_profile = {}
    constructor = {
        **constructor,
        "budget_frac": args.budget_frac,
        "budgets": budgets,
        "initial_group_risks": context_info["initial_group_risks"],
        "final_group_risks": group_eval["group_risks"],
        "final_group_violations": group_eval["group_violations"],
        "group_total_violation": group_eval["total_violation"],
        "group_max_violation": group_eval["max_violation"],
        "group_all_feasible": group_eval["all_groups_feasible"],
    }
    model = build_compressed_model_measured(
        map_label=map_label,
        rows=rows,
        method_spec=f"{method}_adaptive_group_table",
        gamma=args.gamma,
        slip=slip,
        seed=args.seed,
        max_splits=args.max_splits,
        first_hit_mode=args.first_hit_mode,
        first_hit_truncation_steps=args.first_hit_truncation_steps,
        first_hit_tail_tol=args.first_hit_tail_tol,
        boundary_override=boundary,
        constructor_override=constructor,
        construction_time_override=selection_time,
    )
    full = model["full_result"]
    smdp = model["smdp_result"]
    full_time = float(full["time_sec"])
    selection_kernel_time = float(model["construction_time_sec"]) + float(model["kernel_time_sec"])
    total_time = selection_kernel_time + float(smdp["time_sec"])
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method": method,
        "budget_frac": args.budget_frac,
        "n_states": int(model["n_states"]),
        "n_basis": len(basis),
        "n_boundary": int(model["n_boundary"]),
        "state_compression_ratio": float(model["n_states"]) / max(1.0, float(model["n_boundary"])),
        "n_edges_valid": int(model["n_edges_valid"]),
        "group_all_feasible": bool(group_eval["all_groups_feasible"]),
        "n_groups_feasible": int(group_eval["n_groups_feasible"]),
        "group_total_violation": float(group_eval["total_violation"]),
        "group_max_violation": float(group_eval["max_violation"]),
        "trace_group_all_feasible": constructor.get("trace_group_all_feasible", ""),
        "trace_group_total_violation": constructor.get("trace_group_total_violation", ""),
        "trace_group_max_violation": constructor.get("trace_group_max_violation", ""),
        "group_test_bits_mean": float(group_eval["test_bits_mean"]),
        "group_test_bits_cvar": float(group_eval["test_bits_cvar"]),
        "selection_time_sec": float(model["construction_time_sec"]),
        "one_shot_candidate_universe_time_sec": float(
            finite_float(constructor.get("candidate_universe_time_sec"), 0.0)
        ),
        "one_shot_probe_build_time_sec": float(
            finite_float(constructor.get("probe_build_time_sec"), 0.0)
        ),
        "one_shot_green_time_sec": float(
            finite_float(constructor.get("green_message_passing_time_sec"), 0.0)
        ),
        "one_shot_apply_time_sec": float(
            finite_float(constructor.get("operator_apply_time_sec"), 0.0)
        ),
        "delta_backend": constructor.get("delta_backend", ""),
        "kernel_time_sec": float(model["kernel_time_sec"]),
        "upfront_time_sec": selection_kernel_time,
        "smdp_solve_time_sec": float(smdp["time_sec"]),
        "compressed_total_time_sec": total_time,
        "full_vi_time_sec": full_time,
        "full_vi_backup_count": int(full["backup_count"]),
        "smdp_edge_backup_count": int(smdp["edge_backup_count"]),
        "planning_speedup": full_time / max(1e-12, float(smdp["time_sec"])),
        "total_speedup": full_time / max(1e-12, total_time),
        "break_even_tasks": break_even_tasks(selection_kernel_time, full_time, float(smdp["time_sec"])),
        "backup_compression_ratio": float(full["backup_count"]) / max(1.0, float(smdp["edge_backup_count"])),
        "start_gap": float(model["start_gap"]),
        "value_gap_max": float(model["value_gap_max"]),
        "first_hit_mode": model.get("first_hit_mode", ""),
        "first_hit_used_steps_max": model.get("first_hit_used_steps_max", ""),
        "first_hit_tail_bound_max": model.get("first_hit_tail_bound_max", ""),
        "stop_reason": constructor.get("constructor_stop_reason", ""),
        "probe_cache_hits": int(finite_float(selection_profile.get("probe_cache_hits"), 0.0)),
        "probe_cache_misses": int(finite_float(selection_profile.get("probe_cache_misses"), 0.0)),
        "probe_cache_hit_rate": float(finite_float(selection_profile.get("probe_cache_hit_rate"), 0.0)),
        "probe_calls": int(finite_float(selection_profile.get("probe_calls"), 0.0)),
        "unique_probe_evals": int(finite_float(selection_profile.get("unique_probe_evals"), 0.0)),
        "probe_context_build_time_sec": float(finite_float(selection_profile.get("probe_context_build_time_sec"), 0.0)),
        "probe_green_kernel_time_sec": float(finite_float(selection_profile.get("probe_green_kernel_time_sec"), 0.0)),
        "probe_operator_delta_time_sec": float(finite_float(selection_profile.get("probe_operator_delta_time_sec"), 0.0)),
        "active_weight_time_sec": float(finite_float(selection_profile.get("active_weight_time_sec"), 0.0)),
        "active_weight_cache_hit_rate": float(finite_float(selection_profile.get("active_weight_cache_hit_rate"), 0.0)),
        "probe_call_overhead_time_sec": float(finite_float(selection_profile.get("probe_call_overhead_time_sec"), 0.0)),
        "candidate_score_time_sec": float(finite_float(selection_profile.get("candidate_score_time_sec"), 0.0)),
        "beam_expansion_time_sec": float(finite_float(selection_profile.get("beam_expansion_time_sec"), 0.0)),
        "profiled_selection_time_sec": float(finite_float(selection_profile.get("profiled_selection_time_sec"), 0.0)),
        "uncached_probe_eval_time_sec": float(finite_float(selection_profile.get("uncached_probe_eval_time_sec"), 0.0)),
        "boundary": list(model["boundary"]),
        "error": "",
    }


def error_row(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    method: str,
    message: str,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    return {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method": method,
        "n_states": grid.n_states,
        "error": message,
    }


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace, elapsed: float) -> None:
    columns = [
        "map",
        "slip",
        "method",
        "n_states",
        "n_basis",
        "n_boundary",
        "state_compression_ratio",
        "group_all_feasible",
        "n_groups_feasible",
        "group_total_violation",
        "group_max_violation",
        "trace_group_total_violation",
        "group_test_bits_cvar",
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
        "first_hit_used_steps_max",
        "first_hit_tail_bound_max",
        "stop_reason",
        "error",
    ]
    def display_value(value: object) -> object:
        if isinstance(value, float) and not math.isfinite(value):
            return ""
        return value

    ok_rows = [row for row in rows if not row.get("error")]
    feasible = sum(1 for row in ok_rows if bool(row.get("group_all_feasible", False)))
    best_planning = max((finite_float(row.get("planning_speedup")) for row in ok_rows), default=float("nan"))
    best_total = max((finite_float(row.get("total_speedup")) for row in ok_rows), default=float("nan"))
    method_columns = [
        "method",
        "n_rows",
        "feasible_rows",
        "feasible_rate",
        "median_n_boundary",
        "median_selection_time_sec",
        "median_probe_green_kernel_time_sec",
        "median_active_weight_time_sec",
        "median_candidate_score_time_sec",
        "median_probe_cache_hit_rate",
        "best_planning_speedup",
        "best_total_speedup",
        "median_break_even_tasks",
        "max_group_total_violation",
    ]
    method_rows: List[Dict[str, object]] = []
    def median(values: Sequence[float]) -> object:
        finite = sorted(value for value in values if math.isfinite(value))
        if not finite:
            return ""
        mid = len(finite) // 2
        if len(finite) % 2 == 1:
            return finite[mid]
        return 0.5 * (finite[mid - 1] + finite[mid])

    for method in sorted({str(row.get("method", "")) for row in ok_rows}):
        group = [row for row in ok_rows if str(row.get("method", "")) == method]
        break_evens = sorted(
            int(row["break_even_tasks"])
            for row in group
            if str(row.get("break_even_tasks", "")).strip()
        )
        mid = len(break_evens) // 2
        if not break_evens:
            median_break_even: object = ""
        elif len(break_evens) % 2 == 1:
            median_break_even = break_evens[mid]
        else:
            median_break_even = 0.5 * (break_evens[mid - 1] + break_evens[mid])
        method_rows.append(
            {
                "method": method,
                "n_rows": len(group),
                "feasible_rows": sum(1 for row in group if bool(row.get("group_all_feasible", False))),
                "feasible_rate": sum(1 for row in group if bool(row.get("group_all_feasible", False))) / max(1, len(group)),
                "median_n_boundary": sorted(int(row["n_boundary"]) for row in group)[len(group) // 2] if group else "",
                "median_selection_time_sec": median(finite_float(row.get("selection_time_sec")) for row in group),
                "median_probe_green_kernel_time_sec": median(finite_float(row.get("probe_green_kernel_time_sec")) for row in group),
                "median_active_weight_time_sec": median(finite_float(row.get("active_weight_time_sec")) for row in group),
                "median_candidate_score_time_sec": median(finite_float(row.get("candidate_score_time_sec")) for row in group),
                "median_probe_cache_hit_rate": median(finite_float(row.get("probe_cache_hit_rate")) for row in group),
                "best_planning_speedup": max((finite_float(row.get("planning_speedup")) for row in group), default=float("nan")),
                "best_total_speedup": max((finite_float(row.get("total_speedup")) for row in group), default=float("nan")),
                "median_break_even_tasks": median_break_even,
                "max_group_total_violation": max((finite_float(row.get("group_total_violation"), 0.0) for row in group), default=0.0),
            }
        )
    lines = [
        "# Larger Group-Constrained Adaptive Table",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"slips = {list(args.slips)}",
        f"methods = {list(args.methods)}",
        f"budget_frac = {args.budget_frac}",
        f"first_hit_mode = {args.first_hit_mode}, first_hit_tail_tol = {args.first_hit_tail_tol}",
        f"elapsed_sec = {elapsed:.3f}",
        "",
        "This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.",
        "",
        f"- feasible rows: `{feasible}/{len(ok_rows)}`",
        f"- best planning speedup: `{best_planning:.4g}x`",
        f"- best total speedup: `{best_total:.4g}x`",
        "",
        "## Method Summary",
        "",
        markdown_table(
            [{col: display_value(row.get(col, "")) for col in method_columns} for row in method_rows],
            method_columns,
        ),
        "",
        "## Rows",
        "",
        markdown_table([{col: display_value(row.get(col, "")) for col in columns} for row in rows], columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Larger group-constrained RD table with adaptive Green graph kernels.")
    parser.add_argument("--map-specs", nargs="+", default=["open_room:12", "four_rooms:11", "maze:13"])
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=[
            "endpoints",
            "group_constrained",
            "group_constrained_operator",
            "group_constrained_incremental",
            "one_shot_rd",
            "one_shot_group_fd",
        ],
        default=["endpoints", "group_constrained", "group_constrained_incremental"],
    )
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
    parser.add_argument("--test-probes", nargs="+", default=["combined", "value_gradient", "transition_entropy"])
    parser.add_argument(
        "--include-test-probes",
        action="store_true",
        help="Also evaluate held-out probe distortions. This is slower; the default table reports train-group feasibility.",
    )
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--budget-frac", type=float, default=0.25)
    parser.add_argument("--group-risk-kind", choices=["mean", "cvar", "max"], default="cvar")
    parser.add_argument("--score-mode", choices=["reduction", "reduction_per_rate", "lexicographic"], default="reduction")
    parser.add_argument("--rate-tie-break", type=float, default=1e-4)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-splits", type=int, default=5)
    parser.add_argument("--one-shot-threshold", type=float, default=0.15)
    parser.add_argument("--one-shot-steps", type=int, default=256)
    parser.add_argument("--one-shot-tail-tol", type=float, default=1e-6)
    parser.add_argument("--one-shot-probe-count", type=int, default=None)
    parser.add_argument("--one-shot-min-channel-support", type=int, default=2)
    parser.add_argument("--one-shot-exclusion-radius", type=int, default=1)
    parser.add_argument(
        "--one-shot-candidate-universe",
        choices=["all", "turn_articulation"],
        default="turn_articulation",
    )
    parser.add_argument("--beam-width", type=int, default=2)
    parser.add_argument("--beam-expand", type=int, default=4)
    parser.add_argument("--disable-probe-cache", action="store_true")
    parser.add_argument("--delta-backend", choices=["operator", "insertion_score"], default="operator")
    parser.add_argument("--first-hit-mode", choices=["exact", "truncated", "adaptive"], default="adaptive")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=512)
    parser.add_argument("--first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/group_constrained_adaptive_large"))
    args = parser.parse_args()

    started = time.perf_counter()
    rows: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        for slip in args.slips:
            _grid, lens_groups, recipe, basis, endpoint_boundary, budgets, context_info = group_context(
                map_label=map_label,
                rows=map_rows,
                slip=slip,
                args=args,
            )
            for method in args.methods:
                try:
                    rows.append(
                        run_method(
                            family=family,
                            size=size,
                            map_label=map_label,
                            rows=map_rows,
                            slip=slip,
                            method=method,
                            lens_groups=lens_groups,
                            recipe=recipe,
                            basis=basis,
                            endpoint_boundary=endpoint_boundary,
                            budgets=budgets,
                            context_info=context_info,
                            args=args,
                        )
                    )
                except Exception as exc:
                    if not args.continue_on_error:
                        raise
                    rows.append(error_row(family, size, map_label, map_rows, slip, method, repr(exc)))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "group_constrained_adaptive_large.csv", rows)
    (args.out_dir / "group_constrained_adaptive_large.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args, time.perf_counter() - started)


if __name__ == "__main__":
    main()
