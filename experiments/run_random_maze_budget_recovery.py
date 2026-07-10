#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401

from compression_experiment_utils import scaled_rows
from run_first_boundary_targeted import markdown_table
from run_group_constrained_adaptive_table import group_context, run_method
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_solver_validity import run_actual_refine_beam


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: object) -> bool | None:
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def failed_contexts(rows: Sequence[Mapping[str, str]], method: str) -> List[Tuple[int, int, float]]:
    contexts = set()
    for row in rows:
        if str(row.get("method", "")) != method or row.get("error"):
            continue
        if parse_bool(row.get("group_all_feasible")) is not False:
            continue
        contexts.add((int(row["map_size"]), int(row["maze_seed"]), float(row["slip"])))
    return sorted(contexts)


def parse_context_specs(specs: Sequence[str]) -> Tuple[List[Tuple[int, int, float]], Dict[Tuple[int, int, float], int]]:
    contexts: List[Tuple[int, int, float]] = []
    failed_boundaries: Dict[Tuple[int, int, float], int] = {}
    for spec in specs:
        parts = spec.split(":")
        if len(parts) not in {3, 4}:
            raise ValueError("Context spec must be size:seed:slip[:failed_n_boundary].")
        context = (int(parts[0]), int(parts[1]), float(parts[2]))
        contexts.append(context)
        if len(parts) == 4:
            failed_boundaries[context] = int(parts[3])
    return sorted(set(contexts)), failed_boundaries


def experiment_args(args: argparse.Namespace, max_splits: int, budget_frac: float) -> SimpleNamespace:
    return SimpleNamespace(
        recipe=args.recipe,
        lens_groups=args.lens_groups,
        test_probes=args.test_probes,
        include_test_probes=True,
        fixed_basis_kinds=args.fixed_basis_kinds,
        fixed_random_count=args.fixed_random_count,
        budget_frac=budget_frac,
        group_risk_kind=args.group_risk_kind,
        score_mode=args.score_mode,
        rate_tie_break=args.rate_tie_break,
        probe_top_fraction=args.probe_top_fraction,
        gamma=args.gamma,
        seed=args.seed,
        lambda_struct=args.lambda_struct,
        cvar_alpha=args.cvar_alpha,
        edge_weight=args.edge_weight,
        max_splits=max_splits,
        max_extra_splits=max_splits,
        beam_width=args.beam_width,
        beam_expand=args.beam_expand,
        slip=0.0,
        disable_probe_cache=False,
        delta_backend="insertion_score",
        first_hit_mode="adaptive",
        first_hit_truncation_steps=args.first_hit_truncation_steps,
        first_hit_tail_tol=args.first_hit_tail_tol,
        local_horizon=1e9,
        hidden_threshold=1e-6,
        soft_threshold=3.0,
        residual_threshold=0.5,
        residual_threshold_mode="struct_distinct",
        residual_reward_weight=0.05,
        residual_hit_weight=0.0,
        no_struct_distinct=False,
    )


def build_recovery_summary(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("error"):
            continue
        grouped[
            (
                str(row.get("map", "")),
                str(row.get("slip", "")),
                str(row.get("budget_frac", "")),
            )
        ].append(row)
    summary: List[Dict[str, object]] = []
    for (map_name, slip, budget_frac), group in sorted(grouped.items()):
        ordered = sorted(group, key=lambda row: int(row.get("max_splits", 0)))
        recovered = [row for row in ordered if parse_bool(row.get("group_all_feasible")) is True]
        first = recovered[0] if recovered else None
        actual_rows = [row for row in ordered if row.get("method") == "actual_refine"]
        diagnostic_rows = actual_rows or ordered
        violations = [float(row.get("group_total_violation", math.inf)) for row in diagnostic_rows]
        best_violation = min(violations)
        violation_reduction = max(0.0, violations[0] - best_violation)
        max_splits_tested = max(int(row.get("max_splits", 0)) for row in diagnostic_rows)
        plateau = first is None and max_splits_tested > 5 and violation_reduction <= 1e-9
        summary.append(
            {
                "map": map_name,
                "slip": slip,
                "budget_frac": budget_frac,
                "recovered": first is not None,
                "recovery_method": first.get("method", "") if first else "",
                "minimal_max_splits": first.get("max_splits", "") if first else "",
                "minimal_n_boundary": first.get("n_boundary", "") if first else "",
                "added_vertices_over_failed": first.get("added_vertices_over_failed", "") if first else "",
                "max_splits_tested": max_splits_tested,
                "largest_n_boundary": max(
                    int(float(row.get("n_boundary", 0) or 0)) for row in diagnostic_rows
                ),
                "violation_reduction": violation_reduction,
                "best_total_violation": best_violation,
                "failure_class": (
                    "budget_recovered"
                    if first is not None
                    else "fixed_family_or_probe_plateau"
                    if plateau
                    else "budget_unresolved"
                ),
            }
        )
    return summary


def write_report(
    rows: Sequence[Mapping[str, object]],
    summary: Sequence[Mapping[str, object]],
    path: Path,
    args: argparse.Namespace,
) -> None:
    columns = [
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
    lines = [
        "# Random-Maze Boundary-Budget Recovery",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"max_splits = {list(args.max_splits_values)}, budget_fracs = {list(args.budget_fracs)}",
        "",
        "This ablation reruns only failed XL random-maze contexts and asks whether a modestly larger "
        "boundary budget restores group feasibility.",
        "Summary diagnostics prefer exact-refine rows when available. `fixed_family_or_probe_plateau` "
        "means that increasing the split cap beyond five did not reduce total group violation, so the "
        "failure should not be described as a boundary-rate shortage.",
        "",
        f"- failed contexts tested: `{len(summary)}`",
        f"- recovered contexts: `{sum(1 for row in summary if parse_bool(row.get('recovered')) is True)}`",
        "",
        markdown_table(summary, columns) if summary else "_No failed contexts found._",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def recovery_key(row: Mapping[str, object]) -> Tuple[str, str, str, str, str]:
    return (
        str(row.get("map", "")),
        str(row.get("slip", "")),
        str(row.get("budget_frac", "")),
        str(row.get("max_splits", "")),
        str(row.get("method", "")),
    )


def write_outputs(rows: Sequence[Mapping[str, object]], args: argparse.Namespace) -> None:
    summary = build_recovery_summary(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "random_maze_budget_recovery.csv", rows)
    write_csv_all_fields(args.out_dir / "random_maze_budget_recovery_summary.csv", summary)
    (args.out_dir / "random_maze_budget_recovery.json").write_text(
        json.dumps({"rows": rows, "summary": summary}, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, summary, args.out_dir / "summary.md", args)


def log_progress(args: argparse.Namespace, event: str, **payload: object) -> None:
    path = args.progress_log or (args.out_dir / "progress.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": time.time(),
        "event": event,
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        **payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, default=json_default) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover failed random-maze cases with larger boundary budgets.")
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=Path("experiments/output/random_maze_generalization/random_maze_generalization.csv"),
    )
    parser.add_argument("--source-method", default="group_constrained_incremental")
    parser.add_argument(
        "--contexts",
        nargs="*",
        default=[],
        help="Optional size:seed:slip[:failed_n_boundary] contexts, bypassing input CSV discovery.",
    )
    parser.add_argument("--max-splits-values", nargs="+", type=int, default=[5, 8, 12, 16])
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=["group_constrained_incremental", "actual_refine"],
        default=["group_constrained_incremental"],
    )
    parser.add_argument("--budget-fracs", nargs="+", type=float, default=[0.25])
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
    parser.add_argument("--group-risk-kind", choices=["mean", "cvar", "max"], default="cvar")
    parser.add_argument("--score-mode", choices=["reduction", "reduction_per_rate", "lexicographic"], default="reduction")
    parser.add_argument("--rate-tie-break", type=float, default=1e-4)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument("--edge-weight", choices=["occupancy", "uniform", "occupancy_or_uniform"], default="occupancy_or_uniform")
    parser.add_argument("--beam-width", type=int, default=2)
    parser.add_argument("--beam-expand", type=int, default=4)
    parser.add_argument("--first-hit-truncation-steps", type=int, default=512)
    parser.add_argument("--first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--progress-log", type=Path, default=None)
    parser.add_argument("--max-contexts", type=int, default=0)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument(
        "--shard-unit",
        choices=["context", "job"],
        default="context",
        help="Shard whole contexts or individual (context, budget, max-splits, method) jobs.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/random_maze_budget_recovery"),
    )
    args = parser.parse_args()

    if args.num_shards < 1 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("Require 0 <= shard-index < num-shards and num-shards >= 1.")
    source_rows = read_csv(args.input_csv)
    explicit_contexts, explicit_failed_boundaries = parse_context_specs(args.contexts)
    contexts = explicit_contexts or failed_contexts(source_rows, args.source_method)
    if args.max_contexts > 0:
        contexts = contexts[: args.max_contexts]
    if args.shard_unit == "context":
        contexts = [
            context
            for index, context in enumerate(contexts)
            if index % args.num_shards == args.shard_index
        ]
    failed_boundary_by_context = {
        (int(row["map_size"]), int(row["maze_seed"]), float(row["slip"])): int(float(row["n_boundary"]))
        for row in source_rows
        if str(row.get("method", "")) == args.source_method
        and parse_bool(row.get("group_all_feasible")) is False
        and not row.get("error")
    }
    failed_boundary_by_context.update(explicit_failed_boundaries)
    jobs = [
        (size, maze_seed, slip, budget_frac, max_splits, method)
        for size, maze_seed, slip in contexts
        for budget_frac in args.budget_fracs
        for max_splits in args.max_splits_values
        for method in args.methods
    ]
    if args.shard_unit == "job":
        jobs = [
            job
            for index, job in enumerate(jobs)
            if index % args.num_shards == args.shard_index
        ]

    rows: List[Dict[str, object]] = (
        [
            dict(row)
            for row in read_csv(args.out_dir / "random_maze_budget_recovery.csv")
            if not row.get("error")
        ]
        if args.resume
        else []
    )
    completed = {recovery_key(row) for row in rows if not row.get("error")}
    log_progress(args, "start", selected_jobs=len(jobs), resumed_jobs=len(completed))
    for job_index, (size, maze_seed, slip, budget_frac, max_splits, method) in enumerate(jobs):
        map_rows = scaled_rows("maze", size, seed=maze_seed)
        map_label = f"random_maze_{size}_seed{maze_seed}"
        key = (map_label, str(slip), str(budget_frac), str(max_splits), method)
        if args.resume and key in completed:
            log_progress(args, "skip_completed", job_index=job_index, map=map_label, max_splits=max_splits)
            continue
        started = time.perf_counter()
        run_args = experiment_args(args, max_splits=max_splits, budget_frac=budget_frac)
        run_args.slip = slip
        try:
            _grid, lens_groups, recipe, basis, endpoint_boundary, budgets, context_info = group_context(
                map_label=map_label,
                rows=map_rows,
                slip=slip,
                args=run_args,
            )
            if method == "group_constrained_incremental":
                row = run_method(
                    family="random_maze",
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
                    args=run_args,
                )
            else:
                boundary, final_eval, selection_time = run_actual_refine_beam(
                    map_label=map_label,
                    rows=map_rows,
                    recipe=recipe,
                    basis=basis,
                    start_boundary=endpoint_boundary,
                    lens_groups=lens_groups,
                    budgets=budgets,
                    beam_width=args.beam_width,
                    args=run_args,
                )
                row = {
                    "map_family": "random_maze",
                    "map_size": size,
                    "map": map_label,
                    "slip": slip,
                    "method": method,
                    "n_states": _grid.n_states,
                    "n_basis": len(basis),
                    "n_boundary": len(boundary),
                    "state_compression_ratio": _grid.n_states / max(1, len(boundary)),
                    "group_all_feasible": bool(final_eval["all_groups_feasible"]),
                    "group_total_violation": float(final_eval["total_violation"]),
                    "group_max_violation": float(final_eval["max_violation"]),
                    "group_risks": final_eval.get("group_risks", ""),
                    "group_violations": final_eval.get("group_violations", ""),
                    "selection_time_sec": selection_time,
                    "boundary": boundary,
                    "stop_reason": final_eval["stop_reason"],
                }
            row.update(
                {
                    "maze_seed": maze_seed,
                    "budget_frac": budget_frac,
                    "max_splits": max_splits,
                    "failed_n_boundary": failed_boundary_by_context.get((size, maze_seed, slip), ""),
                    "added_vertices_over_failed": int(row["n_boundary"])
                    - failed_boundary_by_context.get((size, maze_seed, slip), int(row["n_boundary"])),
                    "error": "",
                }
            )
            rows.append(row)
            completed.add(key)
            log_progress(
                args,
                "job_done",
                job_index=job_index,
                map=map_label,
                slip=slip,
                max_splits=max_splits,
                method=method,
                elapsed_sec=time.perf_counter() - started,
            )
        except Exception as exc:
            if not args.continue_on_error:
                raise
            rows.append(
                {
                    "map_family": "random_maze",
                    "map_size": size,
                    "map": map_label,
                    "maze_seed": maze_seed,
                    "slip": slip,
                    "budget_frac": budget_frac,
                    "max_splits": max_splits,
                    "method": method,
                    "error": repr(exc),
                }
            )
            log_progress(
                args,
                "job_error",
                job_index=job_index,
                map=map_label,
                slip=slip,
                max_splits=max_splits,
                method=method,
                elapsed_sec=time.perf_counter() - started,
                error=repr(exc),
            )
        write_outputs(rows, args)
    write_outputs(rows, args)
    log_progress(args, "done", rows=len(rows), selected_jobs=len(jobs))


if __name__ == "__main__":
    main()
