#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import build_compressed_model_measured, parse_map_specs
from run_first_boundary_targeted import critical_saliency, markdown_table
from run_group_constrained_adaptive_table import (
    break_even_tasks,
    evaluate_group_boundary,
    group_context,
)
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import (
    ProbeDeltaCache,
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


def objective_tuple(eval_result: Mapping[str, object], n_boundary: int) -> Tuple[float, float, int, float]:
    return (
        finite_float(eval_result.get("total_violation"), 0.0),
        finite_float(eval_result.get("max_violation"), 0.0),
        int(n_boundary),
        finite_float(eval_result.get("test_bits_cvar"), 0.0),
    )


def top_rank_of(state: int | None, rows: Sequence[Mapping[str, object]]) -> int | None:
    if state is None:
        return None
    for rank, row in enumerate(rows, start=1):
        if int(row.get("candidate_state", -1)) == int(state):
            return rank
    return None


def proposal_rows(
    *,
    map_label: str,
    rows: Tuple[str, ...],
    grid: GridWorld,
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    probes: Sequence[str],
    proposal_backend: str,
    args: argparse.Namespace,
) -> Tuple[List[Dict[str, object]], float]:
    started = time.perf_counter()
    if proposal_backend in {"operator", "insertion_score"}:
        before_by_probe, deltas_by_state, _probe_diag = probe_delta_table(
            map_name=map_label,
            step=0,
            rows=rows,
            recipe=recipe,
            basis=basis,
            boundary=boundary,
            probes=probes,
            gamma=args.gamma,
            slip=args.current_slip,
            lambda_struct=args.lambda_struct,
            edge_weight=args.edge_weight,
            probe_top_fraction=args.probe_top_fraction,
            probe_cache=ProbeDeltaCache(enabled=not args.disable_probe_cache),
            delta_backend=proposal_backend,
        )
        scored, _risks, _violations = score_candidates(
            map_name=map_label,
            step=0,
            basis=basis,
            boundary=boundary,
            lens_groups=lens_groups,
            budgets=budgets,
            before_by_probe=before_by_probe,
            deltas_by_state=deltas_by_state,
            group_risk_kind=args.group_risk_kind,
            cvar_alpha=args.cvar_alpha,
            score_mode=args.score_mode,
            rate_tie_break=args.rate_tie_break,
        )
        return [dict(row) for row in scored], time.perf_counter() - started

    if proposal_backend == "heuristic_saliency":
        goal = grid.symbol_states("G")[0]
        saliency = critical_saliency(
            grid=grid,
            kind=args.heuristic_kind,
            goal_state=goal,
            gamma=args.gamma,
            slip=args.current_slip,
            top_fraction=args.probe_top_fraction,
        )
        candidates = sorted(set(int(state) for state in basis) - set(int(state) for state in boundary))
        scored = [
            {
                "candidate_state": int(state),
                "rank": rank,
                "operator_score": float(saliency[int(state)]),
                "violation_after": "",
                "violation_reduction": "",
                "groups_improved": "",
                "proposal_backend": proposal_backend,
            }
            for rank, state in enumerate(
                sorted(candidates, key=lambda state: (float(saliency[int(state)]), -int(state)), reverse=True),
                start=1,
            )
        ]
        return scored, time.perf_counter() - started

    raise ValueError(f"Unknown proposal backend: {proposal_backend}")


def exact_eval_timed(
    *,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
) -> Tuple[Dict[str, object], float]:
    started = time.perf_counter()
    out = evaluate_group_boundary(
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
    return out, time.perf_counter() - started


def objective_first_gap(
    better: Tuple[float, float, int, float],
    worse: Tuple[float, float, int, float],
    *,
    eps: float = 1e-12,
) -> float:
    """Positive when `better` is lexicographically better than `worse`."""
    for best_value, worse_value in zip(better, worse):
        gap = float(worse_value) - float(best_value)
        if abs(gap) > eps:
            return gap
    return 0.0


def adaptive_topk_schedule(top_k_cap: int, args: argparse.Namespace) -> List[int]:
    cap = max(1, int(top_k_cap))
    raw = [int(k) for k in getattr(args, "adaptive_topk_schedule", [1, 2, 4, 8]) if int(k) > 0]
    if not raw:
        raw = [1, 2, 4, 8]
    schedule = sorted({min(cap, k) for k in raw if k <= cap})
    if cap not in schedule:
        schedule.append(cap)
    return schedule


def run_refine_solver(
    *,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    grid: GridWorld,
    lens_groups: Mapping[str, Sequence[str]],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    start_boundary: Sequence[int],
    budgets: Mapping[str, float],
    proposal_backend: str,
    top_k: int,
    adaptive_topk: bool = False,
    args: argparse.Namespace,
) -> Tuple[List[int], Dict[str, object], List[Dict[str, object]], float]:
    boundary = sorted(set(int(state) for state in start_boundary))
    probes = sorted({probe for group_probes in lens_groups.values() for probe in group_probes})
    trace_rows: List[Dict[str, object]] = []
    proposal_time = 0.0
    refine_time = 0.0
    diagnostic_operator_time = 0.0
    exact_refine_calls = 0
    recall_hits = 0
    recall_steps = 0
    adaptive_topk_used_values: List[int] = []
    adaptive_topk_stop_reasons: List[str] = []
    refined_candidates_total = 0
    last_eval: Dict[str, object] | None = None
    stop_reason = "max_splits"
    args.current_slip = slip

    for step in range(args.max_splits + 1):
        current_eval, current_time = exact_eval_timed(
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
        refine_time += current_time
        exact_refine_calls += 1
        last_eval = current_eval
        current_obj = objective_tuple(current_eval, len(boundary))
        if bool(current_eval.get("all_groups_feasible", False)):
            stop_reason = "feasible"
            trace_rows.append(
                {
                    "map": map_label,
                    "slip": slip,
                    "solver": f"{proposal_backend}_{'adaptive_' if adaptive_topk else ''}top{top_k}_refine",
                    "step": step,
                    "selected_state": "",
                    "stop_reason": stop_reason,
                    "n_boundary": len(boundary),
                    "current_total_violation": current_obj[0],
                    "current_max_violation": current_obj[1],
                    "exact_refine_calls_cumulative": exact_refine_calls,
                }
            )
            break
        if step >= args.max_splits:
            stop_reason = "budget_not_met"
            trace_rows.append(
                {
                    "map": map_label,
                    "slip": slip,
                    "solver": f"{proposal_backend}_{'adaptive_' if adaptive_topk else ''}top{top_k}_refine",
                    "step": step,
                    "selected_state": "",
                    "stop_reason": stop_reason,
                    "n_boundary": len(boundary),
                    "current_total_violation": current_obj[0],
                    "current_max_violation": current_obj[1],
                    "exact_refine_calls_cumulative": exact_refine_calls,
                }
            )
            break

        proposed, prop_time = proposal_rows(
            map_label=map_label,
            rows=rows,
            grid=grid,
            recipe=recipe,
            basis=basis,
            boundary=boundary,
            lens_groups=lens_groups,
            budgets=budgets,
            probes=probes,
            proposal_backend=proposal_backend,
            args=args,
        )
        proposal_time += prop_time
        top_k_cap = max(1, top_k)
        proposed = proposed[:top_k_cap]

        exact_best_state = None
        exact_rank_in_proposal = None
        if args.with_recall_diagnostic and proposal_backend != "operator":
            exact_rows, exact_time = proposal_rows(
                map_label=map_label,
                rows=rows,
                grid=grid,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                probes=probes,
                proposal_backend="operator",
                args=args,
            )
            diagnostic_operator_time += exact_time
            if exact_rows:
                exact_best_state = int(exact_rows[0]["candidate_state"])
                exact_rank_in_proposal = top_rank_of(exact_best_state, proposed)
                recall_steps += 1
                if exact_rank_in_proposal is not None:
                    recall_hits += 1

        if not proposed:
            stop_reason = "no_proposal"
            trace_rows.append(
                {
                    "map": map_label,
                    "slip": slip,
                    "solver": f"{proposal_backend}_{'adaptive_' if adaptive_topk else ''}top{top_k}_refine",
                    "step": step,
                    "selected_state": "",
                    "stop_reason": stop_reason,
                    "n_boundary": len(boundary),
                    "current_total_violation": current_obj[0],
                    "current_max_violation": current_obj[1],
                    "proposal_time_sec": prop_time,
                    "exact_refine_calls_cumulative": exact_refine_calls,
                }
            )
            break

        trial_rows: List[Dict[str, object]] = []
        evaluated_ranks: set[int] = set()
        adaptive_used = min(top_k_cap, len(proposed))
        adaptive_decision = "fixed_topk"
        adaptive_margin = float("nan")
        adaptive_improvement = float("nan")
        schedule = adaptive_topk_schedule(top_k_cap, args) if adaptive_topk else [top_k_cap]
        for target_k in schedule:
            adaptive_used = min(target_k, len(proposed))
            for rank, proposal in enumerate(proposed[:adaptive_used], start=1):
                if rank in evaluated_ranks:
                    continue
                evaluated_ranks.add(rank)
                candidate = int(proposal["candidate_state"])
                trial_boundary = sorted(set(boundary).union({candidate}))
                trial_eval, trial_time = exact_eval_timed(
                    map_label=map_label,
                    rows=rows,
                    slip=slip,
                    boundary=trial_boundary,
                    lens_groups=lens_groups,
                    recipe=recipe,
                    basis=basis,
                    budgets=budgets,
                    args=args,
                )
                refine_time += trial_time
                exact_refine_calls += 1
                trial_rows.append(
                    {
                        "rank": rank,
                        "candidate_state": candidate,
                        "proposal_score": finite_float(proposal.get("operator_score"), 0.0),
                        "estimated_violation_after": proposal.get("violation_after", ""),
                        "eval": trial_eval,
                        "eval_time_sec": trial_time,
                        "objective": objective_tuple(trial_eval, len(trial_boundary)),
                    }
                )
            trial_rows.sort(key=lambda row: row["objective"])  # type: ignore[index]
            if not adaptive_topk or not trial_rows:
                break
            best_eval_so_far = trial_rows[0]["eval"]
            best_obj_so_far = trial_rows[0]["objective"]  # type: ignore[assignment]
            adaptive_improvement = objective_first_gap(best_obj_so_far, current_obj)
            if len(trial_rows) >= 2:
                adaptive_margin = objective_first_gap(
                    best_obj_so_far,
                    trial_rows[1]["objective"],  # type: ignore[arg-type]
                )
            best_is_feasible = bool(best_eval_so_far.get("all_groups_feasible", False))
            if (
                len(trial_rows) >= 2
                and best_is_feasible
                and adaptive_improvement >= args.adaptive_topk_margin
                and adaptive_margin >= args.adaptive_topk_margin
            ):
                adaptive_decision = "clear_margin"
                break
            if best_is_feasible:
                adaptive_decision = "feasible"
                break
            if adaptive_used >= min(top_k_cap, len(proposed)):
                adaptive_decision = "cap"
                break
            adaptive_decision = "expand"

        trial_rows.sort(key=lambda row: row["objective"])  # type: ignore[index]
        refined_candidates_total += len(trial_rows)
        if adaptive_topk:
            adaptive_topk_used_values.append(len(trial_rows))
            adaptive_topk_stop_reasons.append(adaptive_decision)
        best = trial_rows[0]
        best_obj = best["objective"]  # type: ignore[assignment]
        best_proposal_score = finite_float(best.get("proposal_score"), 0.0)
        if best_obj >= current_obj and best_proposal_score <= args.nonmonotone_min_proposal_score:
            stop_reason = "no_positive_exact_refine_gain"
            trace_rows.append(
                {
                    "map": map_label,
                    "slip": slip,
                    "solver": f"{proposal_backend}_{'adaptive_' if adaptive_topk else ''}top{top_k}_refine",
                    "step": step,
                    "selected_state": "",
                    "stop_reason": stop_reason,
                    "n_boundary": len(boundary),
                    "current_total_violation": current_obj[0],
                    "current_max_violation": current_obj[1],
                    "best_trial_state": int(best["candidate_state"]),
                    "best_trial_total_violation": best_obj[0],
                    "proposal_time_sec": prop_time,
                    "exact_top_state": exact_best_state if exact_best_state is not None else "",
                    "exact_top_rank_in_proposal_topk": exact_rank_in_proposal
                    if exact_rank_in_proposal is not None
                    else "",
                    "exact_refine_calls_cumulative": exact_refine_calls,
                    "adaptive_topk_used": len(trial_rows) if adaptive_topk else "",
                    "adaptive_decision": adaptive_decision if adaptive_topk else "",
                    "adaptive_margin": adaptive_margin if adaptive_topk else "",
                    "adaptive_improvement": adaptive_improvement if adaptive_topk else "",
                }
            )
            break

        selected = int(best["candidate_state"])
        selected_eval = best["eval"]  # type: ignore[assignment]
        accepted_nonmonotone = best_obj >= current_obj
        trace_rows.append(
            {
                "map": map_label,
                "slip": slip,
                "solver": f"{proposal_backend}_{'adaptive_' if adaptive_topk else ''}top{top_k}_refine",
                "step": step,
                "selected_state": selected,
                "stop_reason": "continue_nonmonotone" if accepted_nonmonotone else "continue",
                "n_boundary": len(boundary),
                "proposal_top_k": top_k,
                "proposal_time_sec": prop_time,
                "refined_candidates": len(trial_rows),
                "adaptive_topk_used": len(trial_rows) if adaptive_topk else "",
                "adaptive_decision": adaptive_decision if adaptive_topk else "",
                "adaptive_margin": adaptive_margin if adaptive_topk else "",
                "adaptive_improvement": adaptive_improvement if adaptive_topk else "",
                "current_total_violation": current_obj[0],
                "selected_total_violation": finite_float(selected_eval.get("total_violation"), 0.0),
                "selected_max_violation": finite_float(selected_eval.get("max_violation"), 0.0),
                "selected_all_groups_feasible": bool(selected_eval.get("all_groups_feasible", False)),
                "accepted_nonmonotone": accepted_nonmonotone,
                "proposal_rank": int(best["rank"]),
                "proposal_score": best_proposal_score,
                "exact_top_state": exact_best_state if exact_best_state is not None else "",
                "exact_top_rank_in_proposal_topk": exact_rank_in_proposal
                if exact_rank_in_proposal is not None
                else "",
                "exact_refine_calls_cumulative": exact_refine_calls,
            }
        )
        boundary = sorted(set(boundary).union({selected}))

    profile = {
        "stop_reason": stop_reason,
        "proposal_backend": proposal_backend,
        "top_k": top_k,
        "proposal_time_sec": proposal_time,
        "refine_time_sec": refine_time,
        "diagnostic_operator_time_sec": diagnostic_operator_time,
        "selection_time_sec": proposal_time + refine_time,
        "exact_refine_calls": exact_refine_calls,
        "surrogate_topk_recall_steps": recall_steps,
        "surrogate_topk_recall_hits": recall_hits,
        "surrogate_topk_recall": recall_hits / max(1, recall_steps) if recall_steps else "",
        "adaptive_topk": adaptive_topk,
        "adaptive_topk_schedule": ",".join(str(k) for k in adaptive_topk_schedule(top_k, args)) if adaptive_topk else "",
        "adaptive_topk_margin": args.adaptive_topk_margin if adaptive_topk else "",
        "adaptive_topk_used_mean": (
            sum(adaptive_topk_used_values) / len(adaptive_topk_used_values) if adaptive_topk_used_values else ""
        ),
        "adaptive_topk_used_max": max(adaptive_topk_used_values) if adaptive_topk_used_values else "",
        "adaptive_topk_cap_hits": sum(1 for reason in adaptive_topk_stop_reasons if reason == "cap"),
        "adaptive_topk_clear_margin_steps": sum(1 for reason in adaptive_topk_stop_reasons if reason == "clear_margin"),
        "adaptive_topk_feasible_steps": sum(1 for reason in adaptive_topk_stop_reasons if reason == "feasible"),
        "refined_candidates_total": refined_candidates_total,
        "nonmonotone_min_proposal_score": args.nonmonotone_min_proposal_score,
        "final_eval": last_eval or {},
    }
    return boundary, profile, trace_rows, proposal_time + refine_time


def run_existing_group_solver(
    *,
    method: str,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    lens_groups: Mapping[str, Sequence[str]],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    start_boundary: Sequence[int],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
) -> Tuple[List[int], Dict[str, object], List[Dict[str, object]], float]:
    if method == "endpoints":
        eval_result, eval_time = exact_eval_timed(
            map_label=map_label,
            rows=rows,
            slip=slip,
            boundary=start_boundary,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            budgets=budgets,
            args=args,
        )
        return list(start_boundary), {
            "stop_reason": "fixed_endpoints",
            "proposal_backend": "none",
            "top_k": 0,
            "proposal_time_sec": 0.0,
            "refine_time_sec": eval_time,
            "selection_time_sec": eval_time,
            "diagnostic_operator_time_sec": 0.0,
            "exact_refine_calls": 1,
            "surrogate_topk_recall": "",
            "final_eval": eval_result,
        }, [], eval_time

    delta_backend = "operator" if method == "exact_group_rd" else "insertion_score"
    probe_cache = ProbeDeltaCache(enabled=not args.disable_probe_cache)
    started = time.perf_counter()
    boundary, trace, _candidates, _probes, _raw_selection_time = select_group_constrained_boundary(
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
    selection_time = time.perf_counter() - started
    final_eval, eval_time = exact_eval_timed(
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
    selection_time += eval_time
    selection_profile = probe_cache.summary()
    step_rows = [
        {
            "map": map_label,
            "slip": slip,
            "solver": method,
            "step": int(row.get("step", 0)),
            "selected_state": row.get("selected_state", ""),
            "stop_reason": row.get("stop_reason", ""),
            "n_boundary": row.get("n_boundary", ""),
            "current_total_violation": row.get("total_violation", ""),
            "current_max_violation": row.get("max_violation", ""),
        }
        for row in trace
    ]
    return list(boundary), {
        "stop_reason": trace[-1].get("stop_reason", "none") if trace else "none",
        "proposal_backend": delta_backend,
        "top_k": "",
        "proposal_time_sec": finite_float(selection_profile.get("profiled_selection_time_sec"), selection_time),
        "refine_time_sec": eval_time,
        "selection_time_sec": selection_time,
        "diagnostic_operator_time_sec": 0.0,
        "exact_refine_calls": 1,
        "surrogate_topk_recall": "",
        "probe_green_kernel_time_sec": finite_float(selection_profile.get("probe_green_kernel_time_sec"), 0.0),
        "probe_operator_delta_time_sec": finite_float(selection_profile.get("probe_operator_delta_time_sec"), 0.0),
        "active_weight_time_sec": finite_float(selection_profile.get("active_weight_time_sec"), 0.0),
        "candidate_score_time_sec": finite_float(selection_profile.get("candidate_score_time_sec"), 0.0),
        "final_eval": final_eval,
    }, step_rows, selection_time


def run_method(
    *,
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    method: str,
    top_k: int,
    args: argparse.Namespace,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    grid, lens_groups, recipe, basis, start_boundary, budgets, context_info = group_context(
        map_label,
        rows,
        slip,
        args,
    )
    if method in {"endpoints", "exact_group_rd", "incremental_group_rd"}:
        boundary, profile, step_rows, selection_time = run_existing_group_solver(
            method=method,
            map_label=map_label,
            rows=rows,
            slip=slip,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            start_boundary=start_boundary,
            budgets=budgets,
            args=args,
        )
        final_kernel_mode = args.reference_first_hit_mode if method == "exact_group_rd" else args.certified_first_hit_mode
        refine_mode = "none"
    elif method == "surrogate_topk_exact_refine":
        boundary, profile, step_rows, selection_time = run_refine_solver(
            map_label=map_label,
            rows=rows,
            slip=slip,
            grid=grid,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            start_boundary=start_boundary,
            budgets=budgets,
            proposal_backend="insertion_score",
            top_k=top_k,
            args=args,
        )
        final_kernel_mode = args.reference_first_hit_mode
        refine_mode = "exact"
    elif method == "adaptive_topk_exact_refine":
        boundary, profile, step_rows, selection_time = run_refine_solver(
            map_label=map_label,
            rows=rows,
            slip=slip,
            grid=grid,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            start_boundary=start_boundary,
            budgets=budgets,
            proposal_backend="insertion_score",
            top_k=top_k,
            adaptive_topk=True,
            args=args,
        )
        final_kernel_mode = args.reference_first_hit_mode
        refine_mode = "adaptive_exact"
    elif method == "surrogate_topk_certified_refine":
        boundary, profile, step_rows, selection_time = run_refine_solver(
            map_label=map_label,
            rows=rows,
            slip=slip,
            grid=grid,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            start_boundary=start_boundary,
            budgets=budgets,
            proposal_backend="insertion_score",
            top_k=top_k,
            args=args,
        )
        final_kernel_mode = args.certified_first_hit_mode
        refine_mode = "certified_adaptive_green"
    elif method == "adaptive_topk_certified_refine":
        boundary, profile, step_rows, selection_time = run_refine_solver(
            map_label=map_label,
            rows=rows,
            slip=slip,
            grid=grid,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            start_boundary=start_boundary,
            budgets=budgets,
            proposal_backend="insertion_score",
            top_k=top_k,
            adaptive_topk=True,
            args=args,
        )
        final_kernel_mode = args.certified_first_hit_mode
        refine_mode = "adaptive_certified_adaptive_green"
    elif method == "heuristic_topk_exact_refine":
        boundary, profile, step_rows, selection_time = run_refine_solver(
            map_label=map_label,
            rows=rows,
            slip=slip,
            grid=grid,
            lens_groups=lens_groups,
            recipe=recipe,
            basis=basis,
            start_boundary=start_boundary,
            budgets=budgets,
            proposal_backend="heuristic_saliency",
            top_k=top_k,
            args=args,
        )
        final_kernel_mode = args.reference_first_hit_mode
        refine_mode = "exact"
    else:
        raise ValueError(f"Unknown method: {method}")

    constructor = {
        "constructor_method": method,
        "budget_frac": args.budget_frac,
        "budgets": budgets,
        "initial_group_risks": context_info["initial_group_risks"],
        "final_group_risks": profile.get("final_eval", {}).get("group_risks", {}),
        "final_group_violations": profile.get("final_eval", {}).get("group_violations", {}),
        "group_total_violation": profile.get("final_eval", {}).get("total_violation", ""),
        "group_all_feasible": profile.get("final_eval", {}).get("all_groups_feasible", ""),
        "selection_profile": profile,
    }
    model = build_compressed_model_measured(
        map_label=map_label,
        rows=rows,
        method_spec=f"{method}_hybrid_refine",
        gamma=args.gamma,
        slip=slip,
        seed=args.seed,
        max_splits=args.max_splits,
        local_horizon=args.local_horizon,
        first_hit_mode=final_kernel_mode,
        first_hit_truncation_steps=args.first_hit_truncation_steps,
        first_hit_tail_tol=args.first_hit_tail_tol,
        boundary_override=boundary,
        constructor_override=constructor,
        construction_time_override=selection_time,
    )
    full = model["full_result"]
    smdp = model["smdp_result"]
    full_time = float(full["time_sec"])
    total_time = float(model["construction_time_sec"]) + float(model["kernel_time_sec"]) + float(smdp["time_sec"])
    final_eval = profile.get("final_eval", {})
    if not isinstance(final_eval, Mapping):
        final_eval = {}
    row = {
        "map_family": family,
        "map_size": size,
        "map": map_label,
        "slip": slip,
        "method": method,
        "top_k": top_k if "topk" in method else "",
        "proposal_backend": profile.get("proposal_backend", ""),
        "refine_mode": refine_mode,
        "final_first_hit_mode": final_kernel_mode,
        "n_states": int(model["n_states"]),
        "n_basis": len(basis),
        "n_boundary": int(model["n_boundary"]),
        "state_compression_ratio": float(model["n_states"]) / max(1.0, float(model["n_boundary"])),
        "group_all_feasible": bool(final_eval.get("all_groups_feasible", False)),
        "n_groups_feasible": int(final_eval.get("n_groups_feasible", 0)),
        "group_total_violation": finite_float(final_eval.get("total_violation"), 0.0),
        "group_max_violation": finite_float(final_eval.get("max_violation"), 0.0),
        "selection_time_sec": float(model["construction_time_sec"]),
        "proposal_time_sec": finite_float(profile.get("proposal_time_sec"), 0.0),
        "refine_time_sec": finite_float(profile.get("refine_time_sec"), 0.0),
        "diagnostic_operator_time_sec": finite_float(profile.get("diagnostic_operator_time_sec"), 0.0),
        "probe_green_kernel_time_sec": finite_float(profile.get("probe_green_kernel_time_sec"), 0.0),
        "probe_operator_delta_time_sec": finite_float(profile.get("probe_operator_delta_time_sec"), 0.0),
        "active_weight_time_sec": finite_float(profile.get("active_weight_time_sec"), 0.0),
        "candidate_score_time_sec": finite_float(profile.get("candidate_score_time_sec"), 0.0),
        "exact_refine_calls": int(finite_float(profile.get("exact_refine_calls"), 0.0)),
        "surrogate_topk_recall": profile.get("surrogate_topk_recall", ""),
        "surrogate_topk_recall_hits": profile.get("surrogate_topk_recall_hits", ""),
        "surrogate_topk_recall_steps": profile.get("surrogate_topk_recall_steps", ""),
        "adaptive_topk": profile.get("adaptive_topk", ""),
        "adaptive_topk_schedule": profile.get("adaptive_topk_schedule", ""),
        "adaptive_topk_margin": profile.get("adaptive_topk_margin", ""),
        "adaptive_topk_used_mean": profile.get("adaptive_topk_used_mean", ""),
        "adaptive_topk_used_max": profile.get("adaptive_topk_used_max", ""),
        "adaptive_topk_cap_hits": profile.get("adaptive_topk_cap_hits", ""),
        "adaptive_topk_clear_margin_steps": profile.get("adaptive_topk_clear_margin_steps", ""),
        "adaptive_topk_feasible_steps": profile.get("adaptive_topk_feasible_steps", ""),
        "refined_candidates_total": profile.get("refined_candidates_total", ""),
        "kernel_time_sec": float(model["kernel_time_sec"]),
        "smdp_solve_time_sec": float(smdp["time_sec"]),
        "upfront_time_sec": float(model["construction_time_sec"]) + float(model["kernel_time_sec"]),
        "compressed_total_time_sec": total_time,
        "full_vi_time_sec": full_time,
        "planning_speedup": full_time / max(1e-12, float(smdp["time_sec"])),
        "total_speedup": full_time / max(1e-12, total_time),
        "break_even_tasks": break_even_tasks(
            float(model["construction_time_sec"]) + float(model["kernel_time_sec"]),
            full_time,
            float(smdp["time_sec"]),
        ),
        "start_gap": float(model["start_gap"]),
        "value_gap_max": float(model["value_gap_max"]),
        "first_hit_used_steps_max": model.get("first_hit_used_steps_max", ""),
        "first_hit_tail_bound_max": model.get("first_hit_tail_bound_max", ""),
        "stop_reason": profile.get("stop_reason", ""),
        "boundary": list(model["boundary"]),
    }
    for step_row in step_rows:
        step_row["method"] = method
        step_row["top_k"] = row["top_k"]
        step_row["map_family"] = family
        step_row["map_size"] = size
    return row, step_rows


def median(values: Sequence[float]) -> object:
    finite = sorted(value for value in values if math.isfinite(value))
    if not finite:
        return ""
    mid = len(finite) // 2
    if len(finite) % 2:
        return finite[mid]
    return 0.5 * (finite[mid - 1] + finite[mid])


def aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        groups.setdefault((str(row.get("method", "")), str(row.get("top_k", ""))), []).append(row)
    out: List[Dict[str, object]] = []
    for (method, top_k), group in sorted(groups.items()):
        n = len(group)
        break_evens = [
            float(row["break_even_tasks"])
            for row in group
            if str(row.get("break_even_tasks", "")).strip()
        ]
        recalls = [
            finite_float(row.get("surrogate_topk_recall"))
            for row in group
            if math.isfinite(finite_float(row.get("surrogate_topk_recall")))
        ]
        out.append(
            {
                "method": method,
                "top_k": top_k,
                "n_rows": n,
                "feasible_rate": sum(1 for row in group if bool(row.get("group_all_feasible", False))) / max(1, n),
                "median_n_boundary": median([finite_float(row.get("n_boundary")) for row in group]),
                "median_selection_time_sec": median([finite_float(row.get("selection_time_sec")) for row in group]),
                "median_kernel_time_sec": median([finite_float(row.get("kernel_time_sec")) for row in group]),
                "median_total_speedup": median([finite_float(row.get("total_speedup")) for row in group]),
                "best_total_speedup": max((finite_float(row.get("total_speedup")) for row in group), default=float("nan")),
                "median_break_even_tasks": median(break_evens),
                "max_group_total_violation": max((finite_float(row.get("group_total_violation"), 0.0) for row in group), default=0.0),
                "max_start_gap": max((finite_float(row.get("start_gap"), 0.0) for row in group), default=0.0),
                "mean_surrogate_topk_recall": sum(recalls) / len(recalls) if recalls else "",
                "total_exact_refine_calls": sum(int(finite_float(row.get("exact_refine_calls"), 0.0)) for row in group),
                "median_adaptive_topk_used_mean": median(
                    [finite_float(row.get("adaptive_topk_used_mean")) for row in group]
                ),
                "max_adaptive_topk_used": max(
                    (finite_float(row.get("adaptive_topk_used_max"), 0.0) for row in group),
                    default=0.0,
                ),
                "total_adaptive_topk_cap_hits": sum(
                    int(finite_float(row.get("adaptive_topk_cap_hits"), 0.0)) for row in group
                ),
                "total_refined_candidates": sum(
                    int(finite_float(row.get("refined_candidates_total"), 0.0)) for row in group
                ),
            }
        )
    return out


def write_report(
    *,
    out_dir: Path,
    rows: Sequence[Mapping[str, object]],
    aggregate: Sequence[Mapping[str, object]],
    args: argparse.Namespace,
    elapsed: float,
) -> None:
    aggregate_columns = [
        "method",
        "top_k",
        "n_rows",
        "feasible_rate",
        "median_n_boundary",
        "median_selection_time_sec",
        "median_kernel_time_sec",
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
    ]
    row_columns = [
        "map",
        "slip",
        "method",
        "top_k",
        "proposal_backend",
        "refine_mode",
        "final_first_hit_mode",
        "n_states",
        "n_boundary",
        "group_all_feasible",
        "group_total_violation",
        "selection_time_sec",
        "proposal_time_sec",
        "refine_time_sec",
        "exact_refine_calls",
        "surrogate_topk_recall",
        "adaptive_topk_used_mean",
        "adaptive_topk_used_max",
        "adaptive_topk_cap_hits",
        "adaptive_topk_clear_margin_steps",
        "adaptive_topk_feasible_steps",
        "refined_candidates_total",
        "kernel_time_sec",
        "planning_speedup",
        "total_speedup",
        "break_even_tasks",
        "start_gap",
        "first_hit_used_steps_max",
        "first_hit_tail_bound_max",
        "stop_reason",
    ]

    def display(value: object) -> object:
        if isinstance(value, float) and not math.isfinite(value):
            return ""
        return value

    lines = [
        "# Hybrid Surrogate + Exact/Certified Refine",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"slips = {list(args.slips)}",
        f"methods = {list(args.methods)}",
        f"top_k = {list(args.top_k)}",
        f"elapsed_sec = {elapsed:.3f}",
        "",
        "This table tests the practical pipeline recommended by the reviewer-style GPT pass: cheap surrogate proposal is allowed only to nominate a top-k set, while exact group evaluation or certified adaptive Green kernels perform the final refinement/audit.",
        "",
        "The intended interpretation is not that the surrogate replaces the exact RD objective; the exact/certified layer remains the decision and audit layer.",
        "",
        "## Aggregate",
        "",
        markdown_table(
            [{col: display(row.get(col, "")) for col in aggregate_columns} for row in aggregate],
            aggregate_columns,
        ),
        "",
        "## Rows",
        "",
        markdown_table(
            [{col: display(row.get(col, "")) for col in row_columns} for row in rows],
            row_columns,
        ),
        "",
        "## Takeaway",
        "",
        "- `exact_group_rd` remains the reference frozen-RD objective.",
        "- `incremental_group_rd` and `surrogate_topk_*` are practical acceleration layers.",
        "- `surrogate_topk_recall` measures whether the cheap proposal keeps the exact operator's best split inside the refinement set.",
        "- `surrogate_topk_certified_refine` reports the deployment path: surrogate proposal, exact group audit, then adaptive certified first-hit kernels for the graph-SMDP.",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def job_key(job: Mapping[str, object]) -> str:
    return "|".join(
        [
            str(job["map"]),
            str(job["slip"]),
            str(job["method"]),
            str(job["top_k"]),
        ]
    )


def load_csv_rows(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]


def append_progress(path: Path, payload: Mapping[str, object]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True, default=json_default) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hybrid surrogate proposal plus exact/certified top-k refinement table.")
    parser.add_argument("--map-specs", nargs="+", default=["open_room:12", "four_rooms:11", "maze:13"])
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=[
            "endpoints",
            "exact_group_rd",
            "incremental_group_rd",
            "surrogate_topk_exact_refine",
            "surrogate_topk_certified_refine",
            "adaptive_topk_exact_refine",
            "adaptive_topk_certified_refine",
            "heuristic_topk_exact_refine",
        ],
        default=[
            "endpoints",
            "exact_group_rd",
            "incremental_group_rd",
            "surrogate_topk_exact_refine",
            "surrogate_topk_certified_refine",
            "adaptive_topk_exact_refine",
            "adaptive_topk_certified_refine",
            "heuristic_topk_exact_refine",
        ],
    )
    parser.add_argument("--top-k", nargs="+", type=int, default=[4, 8])
    parser.add_argument("--adaptive-topk-schedule", nargs="+", type=int, default=[1, 2, 4, 8])
    parser.add_argument(
        "--adaptive-topk-margin",
        type=float,
        default=1e-9,
        help=(
            "Stop adaptive top-k refinement on a clear-margin certificate only when the "
            "exact best split is already group-feasible."
        ),
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
    parser.add_argument("--include-test-probes", action="store_true")
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
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-splits", type=int, default=4)
    parser.add_argument("--beam-width", type=int, default=1)
    parser.add_argument("--beam-expand", type=int, default=6)
    parser.add_argument("--heuristic-kind", default="combined")
    parser.add_argument(
        "--nonmonotone-min-proposal-score",
        type=float,
        default=1e-12,
        help=(
            "Allow exact-refined top-k candidates whose one-step exact group violation worsens "
            "when the proposal score remains positive. Group feasibility can be nonmonotone."
        ),
    )
    parser.add_argument("--reference-first-hit-mode", choices=["exact", "adaptive", "truncated"], default="exact")
    parser.add_argument("--certified-first-hit-mode", choices=["exact", "adaptive", "truncated"], default="adaptive")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=256)
    parser.add_argument("--first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--local-horizon", type=float, default=1e9)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--disable-probe-cache", action="store_true")
    parser.add_argument(
        "--with-recall-diagnostic",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Expensive: compute exact-operator top candidate for surrogate top-k recall diagnostics.",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/hybrid_surrogate_refine"))
    args = parser.parse_args()

    started = time.perf_counter()
    if args.num_shards < 1:
        raise ValueError("--num-shards must be >= 1.")
    if args.shard_index < 0 or args.shard_index >= args.num_shards:
        raise ValueError("--shard-index must be in [0, num_shards).")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.out_dir / "hybrid_surrogate_refine.csv"
    steps_path = args.out_dir / "hybrid_surrogate_refine_steps.csv"
    progress_path = args.out_dir / "progress.jsonl"
    rows_out: List[Dict[str, object]] = load_csv_rows(rows_path) if args.resume else []
    step_rows: List[Dict[str, object]] = load_csv_rows(steps_path) if args.resume else []
    completed = {
        "|".join(
            [
                str(row.get("map", "")),
                str(row.get("slip", "")),
                str(row.get("method", "")),
                str(row.get("top_k", "")) if str(row.get("top_k", "")).strip() else "0",
            ]
        )
        for row in rows_out
    }
    jobs: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        for slip in args.slips:
            for method in args.methods:
                top_ks = args.top_k if "topk" in method else [0]
                for top_k in top_ks:
                    jobs.append(
                        {
                            "family": family,
                            "size": size,
                            "map": map_label,
                            "rows": map_rows,
                            "slip": slip,
                            "method": method,
                            "top_k": top_k,
                        }
                    )
    jobs = [job for idx, job in enumerate(jobs) if idx % args.num_shards == args.shard_index]
    for index, job in enumerate(jobs, start=1):
        key = job_key(job)
        if args.resume and key in completed:
            append_progress(
                progress_path,
                {
                    "event": "skip_completed",
                    "job": key,
                    "index": index,
                    "total": len(jobs),
                    "time": datetime.now().isoformat(timespec="seconds"),
                },
            )
            continue
        append_progress(
            progress_path,
            {
                "event": "start",
                "job": key,
                "index": index,
                "total": len(jobs),
                "time": datetime.now().isoformat(timespec="seconds"),
            },
        )
        job_started = time.perf_counter()
        row, steps = run_method(
            family=str(job["family"]),
            size=int(job["size"]),
            map_label=str(job["map"]),
            rows=job["rows"],  # type: ignore[arg-type]
            slip=float(job["slip"]),
            method=str(job["method"]),
            top_k=int(job["top_k"]),
            args=args,
        )
        rows_out.append(row)
        step_rows.extend(steps)
        completed.add(key)
        aggregate = aggregate_rows(rows_out)
        write_csv_all_fields(rows_path, rows_out)
        write_csv_all_fields(args.out_dir / "hybrid_surrogate_refine_summary.csv", aggregate)
        write_csv_all_fields(steps_path, step_rows)
        (args.out_dir / "hybrid_surrogate_refine.json").write_text(
            json.dumps(rows_out, indent=2, default=json_default) + "\n",
            encoding="utf-8",
        )
        (args.out_dir / "hybrid_surrogate_refine_summary.json").write_text(
            json.dumps(aggregate, indent=2, default=json_default) + "\n",
            encoding="utf-8",
        )
        write_report(out_dir=args.out_dir, rows=rows_out, aggregate=aggregate, args=args, elapsed=time.perf_counter() - started)
        append_progress(
            progress_path,
            {
                "event": "complete",
                "job": key,
                "index": index,
                "total": len(jobs),
                "elapsed_sec": time.perf_counter() - job_started,
                "time": datetime.now().isoformat(timespec="seconds"),
            },
        )
    aggregate = aggregate_rows(rows_out)
    write_csv_all_fields(rows_path, rows_out)
    write_csv_all_fields(args.out_dir / "hybrid_surrogate_refine_summary.csv", aggregate)
    write_csv_all_fields(steps_path, step_rows)
    (args.out_dir / "hybrid_surrogate_refine.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "hybrid_surrogate_refine_summary.json").write_text(
        json.dumps(aggregate, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(out_dir=args.out_dir, rows=rows_out, aggregate=aggregate, args=args, elapsed=time.perf_counter() - started)
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
