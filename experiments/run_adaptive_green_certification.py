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

import numpy as np

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import parse_map_specs, resolve_method_spec
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import construct_boundary, json_default
from run_rd_operator_theorem_checks import (
    active_edges,
    approximate_split_rate_delta,
    build_recipe_context,
    evaluate_recipe_boundary,
    finite_float,
    parse_prob_map,
    phi_bits,
)


def write_csv_all_fields(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
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


def edge_tail_bound(edge_row: Mapping[str, object]) -> float:
    candidates = [
        finite_float(edge_row.get("residual_first_hit_tail_bound"), float("nan")),
        finite_float(edge_row.get("first_hit_tail_bound"), float("nan")),
    ]
    finite = [value for value in candidates if math.isfinite(value)]
    return max(finite) if finite else float("inf")


def combined_tail_bound_max(edge_rows: Sequence[Mapping[str, object]]) -> float:
    finite: List[float] = []
    for row in edge_rows:
        bound = edge_tail_bound(row)
        if math.isfinite(bound):
            finite.append(bound)
    return max(finite, default=0.0)


def combined_used_steps_max(edge_rows: Sequence[Mapping[str, object]]) -> int:
    max_steps = 0
    for row in edge_rows:
        for key in (
            "first_hit_used_steps",
            "residual_first_hit_used_steps",
            "distinct_first_hit_used_steps_max",
        ):
            value = finite_float(row.get(key), 0.0)
            if math.isfinite(value):
                max_steps = max(max_steps, int(value))
    return max_steps


def edge_hidden_mass(edge_row: Mapping[str, object], boundary: Sequence[int]) -> float:
    boundary_set = set(int(state) for state in boundary)
    probs = parse_prob_map(edge_row.get("residual_hidden_probs", "{}"))
    return sum(float(prob) for state, prob in probs.items() if int(state) not in boundary_set)


def bits_fd_piece(hidden_mass: float, candidate_prob: float) -> float:
    h = min(max(float(hidden_mass), 0.0), 1.0 - 1e-12)
    p = min(max(float(candidate_prob), 0.0), h)
    return phi_bits(h) - phi_bits(max(0.0, h - p))


def candidate_score_rows(
    map_label: str,
    kernel_label: str,
    edge_rows: Sequence[Mapping[str, object]],
    base_row: Mapping[str, object],
    recipe: Mapping[str, object],
    boundary: Sequence[int],
    candidates: Sequence[int],
    lambda_struct: float,
    edge_weight: str,
    interval: bool,
) -> List[Dict[str, object]]:
    rate_delta = approximate_split_rate_delta(base_row, recipe)
    weighted_edges = active_edges(edge_rows, edge_weight=edge_weight)
    rows: List[Dict[str, object]] = []
    for candidate in candidates:
        point_delta = 0.0
        lower_delta = 0.0
        upper_delta = 0.0
        tail_weighted_sum = 0.0
        contributing_edges = 0
        for edge_row, weight in weighted_edges:
            probs = parse_prob_map(edge_row.get("residual_hidden_probs", "{}"))
            p_hat = finite_float(probs.get(int(candidate), 0.0), 0.0)
            h_hat = edge_hidden_mass(edge_row, boundary=boundary)
            point_piece = bits_fd_piece(h_hat, p_hat)
            if p_hat > 1e-12:
                contributing_edges += 1
            point_delta += float(weight) * point_piece
            if not interval:
                lower_delta += float(weight) * point_piece
                upper_delta += float(weight) * point_piece
                continue
            tail = max(0.0, edge_tail_bound(edge_row))
            tail_weighted_sum += float(weight) * tail
            if math.isfinite(tail):
                h_upper = min(1.0 - 1e-12, h_hat + tail)
                p_upper = min(h_upper, p_hat + tail)
                upper_piece = bits_fd_piece(h_upper, p_upper)
            else:
                upper_piece = float("inf")
            lower_delta += float(weight) * point_piece
            upper_delta += float(weight) * upper_piece

        point_score = lambda_struct * point_delta - rate_delta
        lower_score = lambda_struct * lower_delta - rate_delta
        upper_score = lambda_struct * upper_delta - rate_delta
        rows.append(
            {
                "map": map_label,
                "kernel_label": kernel_label,
                "candidate_state": int(candidate),
                "n_boundary": len(boundary),
                "n_candidates": len(candidates),
                "n_active_edges": len(weighted_edges),
                "contributing_edges": contributing_edges,
                "rate_delta": rate_delta,
                "bits_fd_delta": point_delta,
                "score_point": point_score,
                "score_lower": lower_score,
                "score_upper": upper_score,
                "score_interval_width": upper_score - lower_score,
                "tail_weighted_sum": tail_weighted_sum,
            }
        )
    rows.sort(key=lambda row: (finite_float(row["score_point"], -float("inf")), -int(row["candidate_state"])), reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["point_rank"] = rank
    return rows


def top_state(rows: Sequence[Mapping[str, object]], field: str) -> int | None:
    if not rows:
        return None
    return int(max(rows, key=lambda row: (finite_float(row.get(field), -float("inf")), -int(row["candidate_state"])))["candidate_state"])


def summarize_certification(
    map_family: str,
    map_size: int,
    map_label: str,
    boundary_method: str,
    tail_tol: float,
    max_steps: int,
    exact_row: Mapping[str, object],
    adaptive_row: Mapping[str, object],
    exact_scores: Sequence[Mapping[str, object]],
    adaptive_scores: Sequence[Mapping[str, object]],
    adaptive_edges: Sequence[Mapping[str, object]],
    exact_time_sec: float,
    adaptive_time_sec: float,
) -> Dict[str, object]:
    exact_top = top_state(exact_scores, "score_point")
    adaptive_top = top_state(adaptive_scores, "score_point")
    sorted_adaptive = sorted(
        adaptive_scores,
        key=lambda row: (finite_float(row["score_point"], -float("inf")), -int(row["candidate_state"])),
        reverse=True,
    )
    value_diff_vs_exact = abs(
        finite_float(adaptive_row.get("start_value_smdp"), float("nan"))
        - finite_float(exact_row.get("start_value_smdp"), float("nan"))
    )
    tail_bound_max = combined_tail_bound_max(adaptive_edges)
    used_steps_max = combined_used_steps_max(adaptive_edges)
    if not sorted_adaptive:
        return {
            "map_family": map_family,
            "map_size": map_size,
            "map": map_label,
            "boundary_method": boundary_method,
            "tail_tol": tail_tol,
            "adaptive_max_steps": max_steps,
            "n_states": int(exact_row.get("n_states", 0)),
            "n_boundary": int(exact_row.get("n_boundary", 0)),
            "n_candidates": 0,
            "exact_time_sec": exact_time_sec,
            "adaptive_time_sec": adaptive_time_sec,
            "speedup_vs_exact": exact_time_sec / max(1e-12, adaptive_time_sec),
            "used_steps_max": used_steps_max,
            "tail_bound_max": tail_bound_max,
            "value_diff_vs_exact": value_diff_vs_exact,
            "status": "no_candidates",
            "decision": "no_candidates",
        }
    top = sorted_adaptive[0]
    runner = sorted_adaptive[1] if len(sorted_adaptive) > 1 else None
    runner_upper = (
        max(finite_float(row["score_upper"], -float("inf")) for row in sorted_adaptive[1:])
        if len(sorted_adaptive) > 1
        else -float("inf")
    )
    top_lower = finite_float(top["score_lower"], -float("inf"))
    top_point = finite_float(top["score_point"], -float("inf"))
    runner_point = finite_float(runner["score_point"], -float("inf")) if runner else -float("inf")
    certified_margin = top_lower - runner_upper
    point_margin = top_point - runner_point
    max_width = max((finite_float(row["score_interval_width"], 0.0) for row in adaptive_scores), default=0.0)
    top_width = finite_float(top["score_interval_width"], 0.0)
    runner_width = finite_float(runner["score_interval_width"], 0.0) if runner else 0.0
    exact_score_by_state = {int(row["candidate_state"]): finite_float(row["score_point"]) for row in exact_scores}
    adaptive_score_by_state = {int(row["candidate_state"]): finite_float(row["score_point"]) for row in adaptive_scores}
    common_states = sorted(set(exact_score_by_state).intersection(adaptive_score_by_state))
    max_abs_score_error = max(
        (abs(exact_score_by_state[state] - adaptive_score_by_state[state]) for state in common_states),
        default=float("nan"),
    )
    return {
        "map_family": map_family,
        "map_size": map_size,
        "map": map_label,
        "boundary_method": boundary_method,
        "tail_tol": tail_tol,
        "adaptive_max_steps": max_steps,
        "n_states": int(exact_row["n_states"]),
        "n_boundary": int(exact_row["n_boundary"]),
        "n_candidates": len(adaptive_scores),
        "exact_time_sec": exact_time_sec,
        "adaptive_time_sec": adaptive_time_sec,
        "speedup_vs_exact": exact_time_sec / max(1e-12, adaptive_time_sec),
        "used_steps_max": used_steps_max,
        "tail_bound_max": tail_bound_max,
        "score_interval_max_width": max_width,
        "top_state_adaptive": adaptive_top,
        "top_state_exact": exact_top,
        "top1_match_exact": adaptive_top == exact_top,
        "top1_certified": certified_margin > 0.0,
        "top1_margin": point_margin,
        "top1_point_margin": point_margin,
        "top1_certified_margin": certified_margin,
        "top1_margin_over_bound": point_margin / max(1e-12, top_width + runner_width),
        "top1_margin_over_width": point_margin / max(1e-12, top_width + runner_width),
        "max_abs_score_error_vs_exact": max_abs_score_error,
        "value_diff_vs_exact": value_diff_vs_exact,
        "status": "ok",
        "decision": "accept" if certified_margin > 0.0 else "needs_refinement_or_exact_fallback",
    }


def run_one(
    family: str,
    size: int,
    map_label: str,
    map_rows: Tuple[str, ...],
    boundary_method: str,
    tail_tol: float,
    args: argparse.Namespace,
    exact_cache: Dict[Tuple[str, str], Tuple[Dict[str, object], List[Dict[str, object]], float]],
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    grid = GridWorld(map_rows)
    recipe = LEARNED_RECIPES[args.recipe]
    actual_method = resolve_method_spec(boundary_method, grid)
    boundary, _constructor = construct_boundary(
        method=actual_method,
        map_name=map_label,
        rows=map_rows,
        grid=grid,
        slip=args.slip,
        gamma=args.gamma,
        max_splits=args.max_splits,
        seed=args.seed,
    )
    if not boundary:
        boundary = endpoint_boundary_states(grid)
    context = build_recipe_context(
        rows=map_rows,
        recipe=recipe,
        gamma=args.gamma,
        slip=args.slip,
    )
    proposal_universe = set(int(s) for s in context["proposal_boundary"])  # type: ignore[arg-type]
    if args.candidate_universe == "proposal":
        candidate_universe = sorted(proposal_universe.union(boundary))
    elif args.candidate_universe == "all":
        candidate_universe = list(range(grid.n_states))
    else:
        candidate_universe = sorted(set(range(grid.n_states)).union(proposal_universe).union(boundary))
    candidates = [state for state in candidate_universe if state not in set(boundary)]
    cache_key = (map_label, actual_method)
    if cache_key not in exact_cache:
        started = time.perf_counter()
        exact_row, exact_edges = evaluate_recipe_boundary(
            map_name=map_label,
            context=context,
            recipe=recipe,
            boundary=boundary,
            gamma=args.gamma,
            slip=args.slip,
            first_hit_mode="exact",
        )
        exact_cache[cache_key] = (exact_row, exact_edges, time.perf_counter() - started)
    exact_row, exact_edges, exact_time_sec = exact_cache[cache_key]
    adaptive_started = time.perf_counter()
    adaptive_row, adaptive_edges = evaluate_recipe_boundary(
        map_name=map_label,
        context=context,
        recipe=recipe,
        boundary=boundary,
        gamma=args.gamma,
        slip=args.slip,
        first_hit_mode="adaptive",
        first_hit_truncation_steps=args.adaptive_max_steps,
        first_hit_tail_tol=tail_tol,
    )
    adaptive_time_sec = time.perf_counter() - adaptive_started
    exact_scores = candidate_score_rows(
        map_label=map_label,
        kernel_label="exact",
        edge_rows=exact_edges,
        base_row=exact_row,
        recipe=recipe,
        boundary=boundary,
        candidates=candidates,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        interval=False,
    )
    adaptive_scores = candidate_score_rows(
        map_label=map_label,
        kernel_label=f"adaptive_eps{tail_tol:g}",
        edge_rows=adaptive_edges,
        base_row=adaptive_row,
        recipe=recipe,
        boundary=boundary,
        candidates=candidates,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        interval=True,
    )
    summary = summarize_certification(
        map_family=family,
        map_size=size,
        map_label=map_label,
        boundary_method=actual_method,
        tail_tol=tail_tol,
        max_steps=args.adaptive_max_steps,
        exact_row=exact_row,
        adaptive_row=adaptive_row,
        exact_scores=exact_scores,
        adaptive_scores=adaptive_scores,
        adaptive_edges=adaptive_edges,
        exact_time_sec=exact_time_sec,
        adaptive_time_sec=adaptive_time_sec,
    )
    score_rows = [
        {
            **row,
            "map_family": family,
            "map_size": size,
            "boundary_method": actual_method,
            "tail_tol": tail_tol,
        }
        for row in exact_scores + adaptive_scores
    ]
    return summary, score_rows


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "map",
        "boundary_method",
        "tail_tol",
        "n_states",
        "n_boundary",
        "n_candidates",
        "used_steps_max",
        "tail_bound_max",
        "speedup_vs_exact",
        "score_interval_max_width",
        "top_state_adaptive",
        "top_state_exact",
        "top1_match_exact",
        "top1_certified",
        "top1_margin",
        "top1_certified_margin",
        "top1_margin_over_bound",
        "max_abs_score_error_vs_exact",
        "value_diff_vs_exact",
        "status",
        "decision",
    ]
    cert_count = sum(1 for row in rows if bool(row.get("top1_certified", False)))
    match_count = sum(1 for row in rows if bool(row.get("top1_match_exact", False)))
    display_rows: List[Dict[str, object]] = []
    for row in rows:
        display_row: Dict[str, object] = {}
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float) and not math.isfinite(value):
                value = ""
            display_row[col] = value
        display_rows.append(display_row)
    lines = [
        "# Adaptive Green Certification",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"boundary_methods = {list(args.boundary_methods)}",
        f"adaptive_tail_tols = {list(args.adaptive_tail_tols)}",
        f"candidate_universe = {args.candidate_universe}",
        "",
        "This table checks whether adaptive Green score intervals are narrow enough to certify the top RD split without falling back to exact Green.",
        "",
        f"- exact top-1 matches: `{match_count}/{len(rows)}`",
        f"- interval-certified top-1 decisions: `{cert_count}/{len(rows)}`",
        "- uncertified rows should refine the tolerance/horizon or use exact Green on the ambiguous top set.",
        "",
        markdown_table(display_rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score-interval certification for adaptive Green RD split decisions.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:128", "open_room:12", "maze:13"])
    parser.add_argument("--boundary-methods", nargs="+", default=["endpoints"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument("--adaptive-tail-tols", type=float, nargs="+", default=[1e-3, 1e-6])
    parser.add_argument("--adaptive-max-steps", type=int, default=512)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument(
        "--candidate-universe",
        choices=["all", "proposal", "proposal_or_all"],
        default="all",
        help="Candidate set to certify. 'all' checks every non-boundary grid state.",
    )
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/adaptive_green_certification"))
    args = parser.parse_args()

    summary_rows: List[Dict[str, object]] = []
    score_rows: List[Dict[str, object]] = []
    exact_cache: Dict[Tuple[str, str], Tuple[Dict[str, object], List[Dict[str, object]], float]] = {}
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        for boundary_method in args.boundary_methods:
            for tail_tol in args.adaptive_tail_tols:
                summary, scores = run_one(
                    family=family,
                    size=size,
                    map_label=map_label,
                    map_rows=map_rows,
                    boundary_method=boundary_method,
                    tail_tol=tail_tol,
                    args=args,
                    exact_cache=exact_cache,
                )
                summary_rows.append(summary)
                score_rows.extend(scores)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "certification_summary.csv", summary_rows)
    write_csv_all_fields(args.out_dir / "candidate_score_intervals.csv", score_rows)
    (args.out_dir / "certification_summary.json").write_text(
        json.dumps(summary_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "candidate_score_intervals.json").write_text(
        json.dumps(score_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(summary_rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
