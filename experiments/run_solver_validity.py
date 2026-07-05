#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import (
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


def objective_tuple(eval_result: Mapping[str, object], n_boundary: int) -> Tuple[float, float, int, float]:
    return (
        finite_float(eval_result.get("total_violation"), 0.0),
        finite_float(eval_result.get("max_violation"), 0.0),
        int(n_boundary),
        finite_float(eval_result.get("test_bits_cvar"), 0.0),
    )


def boundary_signature(boundary: Sequence[int]) -> str:
    return ",".join(str(int(state)) for state in sorted(set(boundary)))


def choose_oracle_pool(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    start_boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
) -> Tuple[List[int], List[Dict[str, object]]]:
    all_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    before_by_probe, deltas_by_state, _probe_rows = probe_delta_table(
        map_name=map_label,
        step=0,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=start_boundary,
        probes=all_probes,
        gamma=args.gamma,
        slip=args.slip,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
    )
    scored, _risks, _violations = score_candidates(
        map_name=map_label,
        step=0,
        basis=basis,
        boundary=start_boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        before_by_probe=before_by_probe,
        deltas_by_state=deltas_by_state,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.cvar_alpha,
        score_mode=args.score_mode,
        rate_tie_break=args.rate_tie_break,
    )
    if scored:
        pool = [int(row["candidate_state"]) for row in scored[: args.max_oracle_candidates]]
    else:
        pool = sorted(set(basis) - set(start_boundary))[: args.max_oracle_candidates]
    return pool, scored


def ranked_operator_candidates(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
) -> List[int]:
    all_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    before_by_probe, deltas_by_state, _probe_rows = probe_delta_table(
        map_name=map_label,
        step=0,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        probes=all_probes,
        gamma=args.gamma,
        slip=args.slip,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
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
    if scored:
        return [int(row["candidate_state"]) for row in scored]
    return sorted(set(basis) - set(boundary))


def exhaustive_oracle(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    start_boundary: Sequence[int],
    candidate_pool: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
) -> Tuple[Dict[str, object], List[Dict[str, object]], float]:
    started = time.perf_counter()
    oracle_rows: List[Dict[str, object]] = []
    best_row: Dict[str, object] | None = None
    best_obj: Tuple[float, float, int, float] | None = None
    max_extra = min(args.max_extra_splits, len(candidate_pool))
    for size in range(max_extra + 1):
        for subset in itertools.combinations(candidate_pool, size):
            boundary = sorted(set(start_boundary).union(int(state) for state in subset))
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
                slip=args.slip,
                edge_weight=args.edge_weight,
                probe_top_fraction=args.probe_top_fraction,
                group_risk_kind=args.group_risk_kind,
                cvar_alpha=args.cvar_alpha,
            )
            obj = objective_tuple(eval_result, len(boundary))
            row = {
                "map": map_label,
                "subset_size": size,
                "candidate_subset": list(subset),
                "n_boundary": len(boundary),
                "boundary": list(boundary),
                "objective_tuple": list(obj),
                "total_violation": obj[0],
                "max_violation": obj[1],
                "all_groups_feasible": bool(eval_result["all_groups_feasible"]),
                "test_bits_mean": finite_float(eval_result.get("test_bits_mean"), 0.0),
                "test_bits_cvar": finite_float(eval_result.get("test_bits_cvar"), 0.0),
                "group_risks": json.dumps(eval_result["group_risks"], sort_keys=True),
                "group_violations": json.dumps(eval_result["group_violations"], sort_keys=True),
            }
            oracle_rows.append(row)
            if best_obj is None or obj < best_obj:
                best_obj = obj
                best_row = row
    if best_row is None:
        raise ValueError(f"No oracle subsets evaluated for {map_label}.")
    return best_row, oracle_rows, time.perf_counter() - started


def run_beam(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    beam_width: int,
    args: argparse.Namespace,
) -> Tuple[List[int], Dict[str, object], float]:
    boundary, trace, _candidate_rows, _probe_rows, selection_time = select_group_constrained_boundary(
        map_name=map_label,
        rows=rows,
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
        max_splits=args.max_extra_splits,
        score_mode=args.score_mode,
        rate_tie_break=args.rate_tie_break,
        beam_width=beam_width,
        beam_expand=args.beam_expand,
    )
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
        slip=args.slip,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.cvar_alpha,
    )
    first_selected = None
    for row in trace:
        if row.get("selected_state") not in (None, ""):
            first_selected = int(row["selected_state"])
            break
    final = {
        "stop_reason": trace[-1].get("stop_reason", "") if trace else "none",
        "path": [int(row["selected_state"]) for row in trace if row.get("selected_state") not in (None, "")],
        "first_selected": first_selected,
        "total_violation": finite_float(eval_result.get("total_violation"), 0.0),
        "max_violation": finite_float(eval_result.get("max_violation"), 0.0),
        "all_groups_feasible": bool(eval_result["all_groups_feasible"]),
        "test_bits_mean": finite_float(eval_result.get("test_bits_mean"), 0.0),
        "test_bits_cvar": finite_float(eval_result.get("test_bits_cvar"), 0.0),
        "group_risks": json.dumps(eval_result["group_risks"], sort_keys=True),
        "group_violations": json.dumps(eval_result["group_violations"], sort_keys=True),
    }
    return boundary, final, selection_time


def run_actual_refine_beam(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    start_boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    beam_width: int,
    args: argparse.Namespace,
) -> Tuple[List[int], Dict[str, object], float]:
    started = time.perf_counter()

    def evaluate_node(boundary: Sequence[int], path: Sequence[int]) -> Dict[str, object]:
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
            slip=args.slip,
            edge_weight=args.edge_weight,
            probe_top_fraction=args.probe_top_fraction,
            group_risk_kind=args.group_risk_kind,
            cvar_alpha=args.cvar_alpha,
        )
        return {
            "boundary": tuple(sorted(set(boundary))),
            "path": list(path),
            "eval": eval_result,
            "objective": objective_tuple(eval_result, len(boundary)),
        }

    beam = [evaluate_node(start_boundary, [])]
    best_node = beam[0]
    for depth in range(args.max_extra_splits):
        expanded: List[Dict[str, object]] = []
        for node in beam:
            boundary = list(node["boundary"])  # type: ignore[arg-type]
            ranked = ranked_operator_candidates(
                map_label=map_label,
                rows=rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                args=args,
            )
            for state in ranked[: max(1, args.beam_expand)]:
                if state in set(boundary):
                    continue
                trial_boundary = sorted(set(boundary).union({state}))
                trial_path = list(node["path"]) + [state]  # type: ignore[operator]
                expanded.append(evaluate_node(trial_boundary, trial_path))
        if not expanded:
            break
        expanded.sort(key=lambda node: node["objective"])  # type: ignore[index]
        deduped: List[Dict[str, object]] = []
        seen = set()
        for node in expanded:
            key = tuple(node["boundary"])  # type: ignore[arg-type]
            if key in seen:
                continue
            seen.add(key)
            deduped.append(node)
            if len(deduped) >= max(1, beam_width):
                break
        beam = deduped
        if beam[0]["objective"] < best_node["objective"]:  # type: ignore[index, operator]
            best_node = beam[0]
        best_obj = best_node["objective"]  # type: ignore[index]
        if best_obj[0] <= 1e-9 and best_obj[1] <= 1e-9:
            break

    final_eval = best_node["eval"]  # type: ignore[assignment]
    path = list(best_node["path"])  # type: ignore[arg-type]
    final = {
        "stop_reason": "actual_refine_feasible" if bool(final_eval["all_groups_feasible"]) else "actual_refine_budget_not_met",
        "path": path,
        "first_selected": path[0] if path else None,
        "total_violation": finite_float(final_eval.get("total_violation"), 0.0),
        "max_violation": finite_float(final_eval.get("max_violation"), 0.0),
        "all_groups_feasible": bool(final_eval["all_groups_feasible"]),
        "test_bits_mean": finite_float(final_eval.get("test_bits_mean"), 0.0),
        "test_bits_cvar": finite_float(final_eval.get("test_bits_cvar"), 0.0),
        "group_risks": json.dumps(final_eval["group_risks"], sort_keys=True),
        "group_violations": json.dumps(final_eval["group_violations"], sort_keys=True),
    }
    return list(best_node["boundary"]), final, time.perf_counter() - started  # type: ignore[arg-type]


def run_map(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    args: argparse.Namespace,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    grid = GridWorld(rows)
    recipe = LEARNED_RECIPES[args.recipe]
    lens_groups = parse_group_specs(args.lens_groups)
    basis = fixed_basis(
        map_label,
        grid=grid,
        kinds=args.fixed_basis_kinds,
        gamma=args.gamma,
        slip=args.slip,
        top_fraction=args.probe_top_fraction,
        random_count=args.fixed_random_count,
    )
    start_boundary = sorted(set(endpoint_boundary_states(grid)).intersection(set(basis)))
    endpoint_eval, _endpoint_rows = evaluate_boundary_on_groups(
        map_name=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=start_boundary,
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
    budgets = {
        group: float(args.budget_frac) * float(initial_group_risks.get(group, 0.0))
        for group in lens_groups
    }
    oracle_pool, initial_scores = choose_oracle_pool(
        map_label=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        start_boundary=start_boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        args=args,
    )
    oracle_best, oracle_rows, oracle_time = exhaustive_oracle(
        map_label=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        start_boundary=start_boundary,
        candidate_pool=oracle_pool,
        lens_groups=lens_groups,
        budgets=budgets,
        args=args,
    )
    oracle_boundary = [int(state) for state in oracle_best["boundary"]]
    oracle_extra = sorted(set(oracle_boundary) - set(start_boundary))
    rank_by_state = {int(row["candidate_state"]): int(row["rank"]) for row in initial_scores}
    top_rank_in_oracle = min((rank_by_state.get(state, 10**9) for state in oracle_extra), default=None)

    summary_rows: List[Dict[str, object]] = []
    for solver in args.solvers:
        for beam_width in args.beam_widths:
            if solver == "operator":
                boundary, final_eval, selection_time = run_beam(
                    map_label=map_label,
                    rows=rows,
                    recipe=recipe,
                    basis=basis,
                    lens_groups=lens_groups,
                    budgets=budgets,
                    beam_width=beam_width,
                    args=args,
                )
            elif solver == "actual_refine":
                boundary, final_eval, selection_time = run_actual_refine_beam(
                    map_label=map_label,
                    rows=rows,
                    recipe=recipe,
                    basis=basis,
                    start_boundary=start_boundary,
                    lens_groups=lens_groups,
                    budgets=budgets,
                    beam_width=beam_width,
                    args=args,
                )
            else:
                raise ValueError(f"Unknown solver: {solver}")
            chosen_extra = sorted(set(boundary) - set(start_boundary))
            intersection = len(set(chosen_extra).intersection(oracle_extra))
            union = len(set(chosen_extra).union(oracle_extra))
            total_gap = finite_float(final_eval["total_violation"], 0.0) - finite_float(oracle_best["total_violation"], 0.0)
            max_gap = finite_float(final_eval["max_violation"], 0.0) - finite_float(oracle_best["max_violation"], 0.0)
            summary_rows.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_label,
                    "solver": solver,
                    "n_states": grid.n_states,
                    "n_basis": len(basis),
                    "n_start_boundary": len(start_boundary),
                    "n_oracle_pool": len(oracle_pool),
                    "oracle_pool_truncated": len(set(basis) - set(start_boundary)) > len(oracle_pool),
                    "max_extra_splits": args.max_extra_splits,
                    "oracle_evaluated_subsets": len(oracle_rows),
                    "oracle_time_sec": oracle_time,
                    "beam_width": beam_width,
                    "beam_expand": args.beam_expand,
                    "selection_time_sec": selection_time,
                    "start_boundary": list(start_boundary),
                    "oracle_extra": oracle_extra,
                    "chosen_extra": chosen_extra,
                    "oracle_boundary": oracle_boundary,
                    "chosen_boundary": list(boundary),
                    "same_boundary_as_oracle": boundary_signature(boundary) == boundary_signature(oracle_boundary),
                    "extra_jaccard_with_oracle": intersection / max(1, union),
                    "operator_top_rank_in_oracle_extra": top_rank_in_oracle if top_rank_in_oracle is not None else "",
                    "first_selected": final_eval["first_selected"],
                    "first_selected_in_oracle_extra": (
                        final_eval["first_selected"] in set(oracle_extra)
                        if final_eval["first_selected"] is not None
                        else False
                    ),
                    "oracle_total_violation": finite_float(oracle_best["total_violation"], 0.0),
                    "chosen_total_violation": finite_float(final_eval["total_violation"], 0.0),
                    "total_violation_gap": total_gap,
                    "oracle_max_violation": finite_float(oracle_best["max_violation"], 0.0),
                    "chosen_max_violation": finite_float(final_eval["max_violation"], 0.0),
                    "max_violation_gap": max_gap,
                    "oracle_all_feasible": bool(oracle_best["all_groups_feasible"]),
                    "chosen_all_feasible": bool(final_eval["all_groups_feasible"]),
                    "oracle_test_bits_cvar": finite_float(oracle_best["test_bits_cvar"], 0.0),
                    "chosen_test_bits_cvar": finite_float(final_eval["test_bits_cvar"], 0.0),
                    "test_bits_cvar_gap": finite_float(final_eval["test_bits_cvar"], 0.0)
                    - finite_float(oracle_best["test_bits_cvar"], 0.0),
                    "chosen_stop_reason": final_eval["stop_reason"],
                    "chosen_path": final_eval["path"],
                    "budgets": json.dumps(budgets, sort_keys=True),
                    "initial_group_risks": json.dumps(initial_group_risks, sort_keys=True),
                }
            )
    oracle_rows = [
        {
            **row,
            "map_family": family,
            "map_size": size,
            "n_states": grid.n_states,
            "n_basis": len(basis),
            "n_start_boundary": len(start_boundary),
            "candidate_pool": list(oracle_pool),
            "is_oracle_best": boundary_signature(row["boundary"]) == boundary_signature(oracle_boundary),
        }
        for row in oracle_rows
    ]
    return summary_rows, oracle_rows


def write_report(
    rows: Sequence[Mapping[str, object]],
    oracle_rows: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    aggregate_rows = solver_aggregate_rows(rows)
    aggregate_columns = [
        "solver",
        "beam_width",
        "n_rows",
        "boundary_match_rate",
        "zero_total_violation_gap_rate",
        "feasible_decision_match_rate",
        "mean_extra_jaccard",
        "median_selection_time_sec",
        "median_oracle_time_sec",
    ]
    columns = [
        "map",
        "solver",
        "beam_width",
        "n_states",
        "n_basis",
        "n_oracle_pool",
        "oracle_evaluated_subsets",
        "same_boundary_as_oracle",
        "extra_jaccard_with_oracle",
        "operator_top_rank_in_oracle_extra",
        "first_selected_in_oracle_extra",
        "oracle_total_violation",
        "chosen_total_violation",
        "total_violation_gap",
        "oracle_all_feasible",
        "chosen_all_feasible",
        "oracle_test_bits_cvar",
        "chosen_test_bits_cvar",
        "selection_time_sec",
        "oracle_time_sec",
        "chosen_stop_reason",
    ]
    exact_matches = sum(1 for row in rows if bool(row["same_boundary_as_oracle"]))
    zero_gap = sum(1 for row in rows if abs(float(row["total_violation_gap"])) <= 1e-9)
    feasible_matches = sum(
        1
        for row in rows
        if bool(row["oracle_all_feasible"]) == bool(row["chosen_all_feasible"])
    )
    lines = [
        "# Solver Validity",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"solvers = {list(args.solvers)}",
        f"beam_widths = {list(args.beam_widths)}, beam_expand = {args.beam_expand}",
        f"max_extra_splits = {args.max_extra_splits}, max_oracle_candidates = {args.max_oracle_candidates}",
        "",
        "For small candidate universes this exhaustively enumerates every subset up to the split budget, then compares operator-only and exact-refined beam group-constrained RD against that oracle. "
        "The exact-refined solver uses the frozen operator only to propose a small expansion set, then ranks those expansions by actual group RD evaluation.",
        "",
        f"- exact boundary matches: `{exact_matches}/{len(rows)}`",
        f"- zero total-violation gap rows: `{zero_gap}/{len(rows)}`",
        f"- feasible/infeasible decision matches: `{feasible_matches}/{len(rows)}`",
        f"- oracle subsets evaluated: `{len(oracle_rows)}`",
        "",
        "## Aggregate",
        "",
        markdown_table(aggregate_rows, aggregate_columns),
        "",
        "## Rows",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def median(values: Sequence[float]) -> float:
    vals = sorted(value for value in values if math.isfinite(value))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    if len(vals) % 2 == 1:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def solver_aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, int], List[Mapping[str, object]]] = {}
    for row in rows:
        key = (str(row["solver"]), int(row["beam_width"]))
        groups.setdefault(key, []).append(row)

    aggregate: List[Dict[str, object]] = []
    for (solver, beam_width), group in sorted(groups.items()):
        n = len(group)
        boundary_matches = sum(1 for row in group if bool(row["same_boundary_as_oracle"]))
        zero_gap = sum(1 for row in group if abs(float(row["total_violation_gap"])) <= 1e-9)
        feasible_matches = sum(
            1
            for row in group
            if bool(row["oracle_all_feasible"]) == bool(row["chosen_all_feasible"])
        )
        aggregate.append(
            {
                "solver": solver,
                "beam_width": beam_width,
                "n_rows": n,
                "boundary_match_rate": boundary_matches / max(1, n),
                "zero_total_violation_gap_rate": zero_gap / max(1, n),
                "feasible_decision_match_rate": feasible_matches / max(1, n),
                "mean_extra_jaccard": sum(float(row["extra_jaccard_with_oracle"]) for row in group) / max(1, n),
                "median_selection_time_sec": median([finite_float(row["selection_time_sec"]) for row in group]),
                "median_oracle_time_sec": median([finite_float(row["oracle_time_sec"]) for row in group]),
            }
        )
    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser(description="Exhaustive-oracle and beam-width validity check for group RD.")
    parser.add_argument("--map-specs", nargs="+", default=["open_room:7", "four_rooms:9", "maze:9"])
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
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-extra-splits", type=int, default=3)
    parser.add_argument("--max-oracle-candidates", type=int, default=8)
    parser.add_argument("--solvers", nargs="+", choices=["operator", "actual_refine"], default=["operator", "actual_refine"])
    parser.add_argument("--beam-widths", type=int, nargs="+", default=[1, 2, 4, 8])
    parser.add_argument("--beam-expand", type=int, default=6)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/solver_validity"))
    args = parser.parse_args()

    summary_rows: List[Dict[str, object]] = []
    oracle_rows: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        map_summary, map_oracle = run_map(family, size, map_label, map_rows, args)
        summary_rows.extend(map_summary)
        oracle_rows.extend(map_oracle)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "solver_validity.csv", summary_rows)
    write_csv_all_fields(args.out_dir / "oracle_subsets.csv", oracle_rows)
    (args.out_dir / "solver_validity.json").write_text(
        json.dumps(summary_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "oracle_subsets.json").write_text(
        json.dumps(oracle_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(summary_rows, oracle_rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
