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

from boundary_heatmap_contexts import (
    BoundaryHeatmapContext,
    context_fields,
    expand_contexts,
)
from compression_experiment_utils import scaled_rows
from run_first_boundary_targeted import markdown_table
from run_group_constrained_adaptive_table import group_context, run_method
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import ProbeDeltaCache, probe_delta_table, score_candidates


def read_existing(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def context_key(map_name: str, slip: float) -> Tuple[str, str]:
    return map_name, f"{float(slip):.12g}"


def completed_contexts(rows: Sequence[Mapping[str, object]]) -> set[Tuple[str, str]]:
    grouped: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        grouped.setdefault(context_key(str(row.get("map")), float(row.get("slip", 0.0))), []).append(row)
    return {
        key
        for key, group in grouped.items()
        if group and not any(row.get("error") for row in group)
    }


def legacy_random_context(size: int, seed: int) -> BoundaryHeatmapContext:
    if size <= 15:
        split = "train" if seed <= 7 else "validation"
    elif size == 17:
        split = "validation" if seed <= 3 else "test"
    else:
        split = "test"
    return BoundaryHeatmapContext(
        map_family="random_maze",
        map_size=int(size),
        topology_seed=int(seed),
        goal_variant=0,
        map_name=f"random_maze_{int(size)}_seed{int(seed)}",
        rows=scaled_rows("maze", int(size), seed=int(seed)),
        split=split,
    )


def write_report(rows: Sequence[Mapping[str, object]], path: Path, args: argparse.Namespace) -> None:
    contexts: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        contexts.setdefault(context_key(str(row.get("map")), float(row.get("slip", 0.0))), []).append(row)
    summary = []
    for (map_name, slip), group in sorted(contexts.items()):
        ok = [row for row in group if not row.get("error")]
        if not ok:
            continue
        summary.append(
            {
                "map": map_name,
                "slip": slip,
                "n_candidates": len(ok),
                "top_state": min(ok, key=lambda row: int(row["rank"]))["candidate_state"],
                "teacher_time_sec": max(float(row["teacher_time_sec"]) for row in ok),
                "max_violation_reduction": max(float(row["violation_reduction"]) for row in ok),
            }
        )
    columns = ["map", "slip", "n_candidates", "top_state", "teacher_time_sec", "max_violation_reduction"]
    lines = [
        "# Frozen Insertion-Score Heatmap Teacher",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Each context freezes the endpoint boundary, multi-probe basis, group budgets, option family, and active-edge semantics. It evaluates every candidate once with the insertion-score backend and exports the complete candidate heatmap; no state is inserted and no score is recomputed.",
        "",
        f"shard = {args.shard_index}/{args.num_shards}, contexts = {len(summary)}, candidate rows = {sum(len(group) for group in contexts.values())}",
        "",
        markdown_table(summary, columns),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export complete frozen insertion-score heatmaps for GNN distillation.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[11, 13, 15, 17, 19])
    parser.add_argument("--maze-seeds", type=int, nargs="+", default=list(range(12)))
    parser.add_argument(
        "--map-specs",
        nargs="*",
        default=[],
        help="Optional multifamily mode, for example open_room:7,9,11,13 maze:9,11,13,15.",
    )
    parser.add_argument("--topology-seeds", type=int, nargs="+", default=list(range(6)))
    parser.add_argument("--goal-variants", type=int, default=3)
    parser.add_argument(
        "--full-teacher",
        action="store_true",
        help="Also run the adaptive group-constrained selector and export context labels.",
    )
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05, 0.1])
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
    parser.add_argument(
        "--fixed-random-count",
        type=int,
        default=0,
        help="Keep zero for graph-observable labels; nonzero values reproduce the legacy hashed-basis ablation.",
    )
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
    parser.add_argument("--beam-width", type=int, default=2)
    parser.add_argument("--beam-expand", type=int, default=4)
    parser.add_argument("--disable-probe-cache", action="store_true")
    parser.add_argument("--delta-backend", choices=["operator", "insertion_score"], default="operator")
    parser.add_argument("--first-hit-mode", choices=["exact", "truncated", "adaptive"], default="adaptive")
    parser.add_argument("--first-hit-truncation-steps", type=int, default=512)
    parser.add_argument("--first-hit-tail-tol", type=float, default=1e-6)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_teacher"),
    )
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    graph_contexts = (
        expand_contexts(
            args.map_specs,
            topology_seeds=args.topology_seeds,
            goal_variants=args.goal_variants,
        )
        if args.map_specs
        else [
            legacy_random_context(int(size), int(seed))
            for size in args.sizes
            for seed in args.maze_seeds
        ]
    )
    all_contexts = [
        (context, float(slip))
        for context in graph_contexts
        for slip in args.slips
    ]
    contexts = [
        context
        for index, context in enumerate(all_contexts)
        if index % args.num_shards == args.shard_index
    ]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = args.out_dir / "boundary_heatmap_teacher.csv"
    rows_out = read_existing(output_csv) if args.resume else []
    teacher_csv = args.out_dir / "boundary_heatmap_contexts.csv"
    teacher_rows_out = read_existing(teacher_csv) if args.resume and args.full_teacher else []
    completed = completed_contexts(rows_out)
    if args.full_teacher:
        completed &= completed_contexts(teacher_rows_out)
    progress = args.out_dir / "progress.jsonl"

    for context, slip in contexts:
        map_name = context.map_name
        current_key = context_key(map_name, slip)
        if current_key in completed:
            continue
        rows_out = [
            row
            for row in rows_out
            if context_key(str(row.get("map")), float(row.get("slip", 0.0))) != current_key
        ]
        if args.full_teacher:
            teacher_rows_out = [
                row
                for row in teacher_rows_out
                if context_key(str(row.get("map")), float(row.get("slip", 0.0))) != current_key
            ]
        started = time.perf_counter()
        teacher_row_written = False
        try:
            map_rows = context.rows
            context_started = time.perf_counter()
            grid, groups, recipe, basis, boundary0, budgets, _info = group_context(
                map_name, map_rows, slip, args
            )
            context_elapsed = time.perf_counter() - context_started
            if args.full_teacher:
                teacher_row = run_method(
                    family=context.map_family,
                    size=context.map_size,
                    map_label=map_name,
                    rows=map_rows,
                    slip=slip,
                    method="group_constrained_incremental",
                    lens_groups=groups,
                    recipe=recipe,
                    basis=basis,
                    endpoint_boundary=boundary0,
                    budgets=budgets,
                    context_info=_info,
                    args=args,
                )
                teacher_rows_out.append({**teacher_row, **context_fields(context)})
                write_csv_all_fields(teacher_csv, teacher_rows_out)
                teacher_row_written = True
            heatmap_started = time.perf_counter()
            probes = sorted({probe for group in groups.values() for probe in group})
            cache = ProbeDeltaCache(enabled=True)
            before, deltas, diagnostics = probe_delta_table(
                map_name=map_name,
                step=0,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary0,
                probes=probes,
                gamma=args.gamma,
                slip=slip,
                lambda_struct=args.lambda_struct,
                edge_weight=args.edge_weight,
                probe_top_fraction=args.probe_top_fraction,
                probe_cache=cache,
                delta_backend="insertion_score",
            )
            scored, risks, violations = score_candidates(
                map_name=map_name,
                step=0,
                basis=basis,
                boundary=boundary0,
                lens_groups=groups,
                budgets=budgets,
                before_by_probe=before,
                deltas_by_state=deltas,
                group_risk_kind=args.group_risk_kind,
                cvar_alpha=args.cvar_alpha,
                score_mode=args.score_mode,
                rate_tie_break=args.rate_tie_break,
            )
            maximum_reduction = max(
                (float(row["violation_reduction"]) for row in scored), default=0.0
            )
            minimum_score = min((float(row["operator_score"]) for row in scored), default=0.0)
            maximum_score = max((float(row["operator_score"]) for row in scored), default=0.0)
            elapsed = context_elapsed + time.perf_counter() - heatmap_started
            context_rows: List[Dict[str, object]] = []
            for row in scored:
                reduction = float(row["violation_reduction"])
                raw_score = float(row["operator_score"])
                context_rows.append(
                    {
                        **context_fields(context),
                        "slip": slip,
                        "n_states": grid.n_states,
                        "n_basis": len(basis),
                        "boundary0": json.dumps(boundary0),
                        "candidate_state": int(row["candidate_state"]),
                        "rank": int(row["rank"]),
                        "is_top": int(row["rank"]) == 1,
                        "operator_score": raw_score,
                        "target_score": (raw_score - minimum_score)
                        / max(1e-12, maximum_score - minimum_score),
                        "violation_before": float(row["violation_before"]),
                        "violation_after": float(row["violation_after"]),
                        "violation_reduction": reduction,
                        "target_reduction": reduction / max(1e-12, maximum_reduction),
                        "groups_improved": int(row["groups_improved"]),
                        "max_after_violation": float(row["max_after_violation"]),
                        "group_risks_before": row["group_risks_before"],
                        "group_risks_after": row["group_risks_after"],
                        "group_violations_after": row["group_violations_after"],
                        "current_group_risks": json.dumps(risks, sort_keys=True),
                        "current_group_violations": json.dumps(violations, sort_keys=True),
                        "teacher_time_sec": elapsed,
                        "probe_profile": json.dumps(cache.summary(), sort_keys=True),
                        "n_probe_diagnostics": len(diagnostics),
                        "error": "",
                    }
                )
            rows_out.extend(context_rows)
            status = "ok"
            n_candidates = len(context_rows)
        except Exception as exc:
            if not args.continue_on_error:
                raise
            rows_out.append(
                {
                    **context_fields(context),
                    "slip": slip,
                    "candidate_state": -1,
                    "teacher_time_sec": time.perf_counter() - started,
                    "error": repr(exc),
                }
            )
            if args.full_teacher and not teacher_row_written:
                teacher_rows_out.append(
                    {
                        **context_fields(context),
                        "slip": slip,
                        "method": "group_constrained_incremental",
                        "error": repr(exc),
                    }
                )
                write_csv_all_fields(teacher_csv, teacher_rows_out)
            status = "error"
            n_candidates = 0
        write_csv_all_fields(output_csv, rows_out)
        with progress.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "map": map_name,
                        "slip": slip,
                        "status": status,
                        "n_candidates": n_candidates,
                    },
                    default=json_default,
                )
                + "\n"
            )
    write_csv_all_fields(output_csv, rows_out)
    if args.full_teacher:
        write_csv_all_fields(teacher_csv, teacher_rows_out)
    (args.out_dir / "boundary_heatmap_teacher.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    write_report(rows_out, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
