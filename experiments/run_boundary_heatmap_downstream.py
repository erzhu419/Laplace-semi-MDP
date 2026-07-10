#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from boundary_heatmap_contexts import rows_from_record
from compression_experiment_utils import build_compressed_model_measured
from run_group_constrained_adaptive_table import evaluate_group_boundary, group_context
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def load_rows(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def context_key(row: Mapping[str, object]) -> Tuple[str, str]:
    return str(row.get("map")), f"{finite_float(row.get('slip'), 0.0):.12g}"


def row_key(row: Mapping[str, object]) -> Tuple[str, str, str]:
    return (*context_key(row), str(row.get("method", row.get("student_method", ""))))


def run_context(
    prediction: Mapping[str, object],
    teacher: Mapping[str, object],
    args: argparse.Namespace,
) -> Dict[str, object]:
    map_name = str(prediction["map"])
    size = int(finite_float(prediction.get("map_size"), 0.0))
    seed = int(
        finite_float(
            prediction.get("topology_seed", prediction.get("maze_seed")),
            0.0,
        )
    )
    slip = finite_float(prediction.get("slip"), 0.0)
    map_rows = rows_from_record(prediction if prediction.get("map_rows") else teacher)
    boundary = sorted(int(state) for state in json.loads(str(prediction["predicted_boundary"])))

    context_started = time.perf_counter()
    _grid, groups, recipe, basis, _boundary0, budgets, _info = group_context(
        map_name, map_rows, slip, args
    )
    context_time = time.perf_counter() - context_started
    audit_started = time.perf_counter()
    audit = evaluate_group_boundary(
        map_label=map_name,
        rows=map_rows,
        slip=slip,
        boundary=boundary,
        lens_groups=groups,
        recipe=recipe,
        basis=basis,
        budgets=budgets,
        args=args,
    )
    audit_time = time.perf_counter() - audit_started

    model = build_compressed_model_measured(
        map_label=map_name,
        rows=map_rows,
        method_spec="gnn_boundary_heatmap",
        gamma=args.gamma,
        slip=slip,
        seed=seed,
        max_splits=args.max_splits,
        boundary_override=boundary,
        construction_time_override=finite_float(prediction.get("student_selection_time_sec"), 0.0),
        first_hit_mode=args.first_hit_mode,
        first_hit_truncation_steps=args.first_hit_truncation_steps,
        first_hit_tail_tol=args.first_hit_tail_tol,
    )
    smdp = model["smdp_result"]
    selection_time = finite_float(prediction.get("student_selection_time_sec"), 0.0)
    kernel_time = finite_float(model.get("kernel_time_sec"), 0.0)
    solve_time = finite_float(smdp.get("time_sec"), 0.0)  # type: ignore[union-attr]
    student_feasible = bool(audit["all_groups_feasible"])
    teacher_feasible = parse_bool(teacher.get("group_all_feasible"))
    fallback_used = not student_feasible
    teacher_selection = finite_float(teacher.get("selection_time_sec"), 0.0)
    teacher_kernel = finite_float(teacher.get("kernel_time_sec"), 0.0)
    teacher_solve = finite_float(teacher.get("smdp_solve_time_sec"), 0.0)
    student_audited_path = selection_time + context_time + audit_time + kernel_time + solve_time
    accepted_path = (
        selection_time + context_time + audit_time + teacher_selection + teacher_kernel + teacher_solve
        if fallback_used
        else student_audited_path
    )
    teacher_pipeline = teacher_selection + teacher_kernel + teacher_solve
    student_normalized_gap = finite_float(model.get("normalized_start_gap"))
    if not math.isfinite(student_normalized_gap):
        student_normalized_gap = abs(finite_float(model.get("start_gap"))) * (1.0 - args.gamma)
    teacher_normalized_gap = abs(finite_float(teacher.get("start_gap"))) * (1.0 - args.gamma)
    return {
        "map_family": prediction.get("map_family", teacher.get("map_family", "")),
        "map_size": size,
        "map": map_name,
        "maze_seed": seed,
        "topology_seed": seed,
        "goal_variant": prediction.get("goal_variant", teacher.get("goal_variant", 0)),
        "map_rows": prediction.get("map_rows", teacher.get("map_rows", "")),
        "slip": slip,
        "student_method": prediction.get("method", ""),
        "n_states": int(model["n_states"]),
        "student_boundary": json.dumps(boundary),
        "teacher_boundary": prediction.get("teacher_boundary", teacher.get("boundary", "")),
        "student_n_boundary": len(boundary),
        "teacher_n_boundary": int(finite_float(teacher.get("n_boundary"), 0.0)),
        "state_compression_ratio": int(model["n_states"]) / max(1, len(boundary)),
        "boundary_jaccard": finite_float(prediction.get("boundary_jaccard")),
        "top_set_hit": parse_bool(prediction.get("top_set_hit")),
        "top_set_regret": finite_float(prediction.get("top_set_regret")),
        "student_score_margin": finite_float(prediction.get("score_margin")),
        "ensemble_top_state_agreement": finite_float(
            prediction.get("ensemble_top_state_agreement")
        ),
        "ensemble_max_node_logit_std": finite_float(
            prediction.get("ensemble_max_node_logit_std")
        ),
        "ensemble_selected_logit_std": finite_float(
            prediction.get("ensemble_selected_logit_std")
        ),
        "student_group_all_feasible": student_feasible,
        "teacher_group_all_feasible": teacher_feasible,
        "accepted_group_all_feasible": student_feasible or teacher_feasible,
        "student_n_groups_feasible": int(audit["n_groups_feasible"]),
        "student_group_total_violation": float(audit["total_violation"]),
        "student_group_max_violation": float(audit["max_violation"]),
        "student_group_risks": json.dumps(audit["group_risks"], sort_keys=True),
        "student_group_violations": json.dumps(audit["group_violations"], sort_keys=True),
        "fallback_used": fallback_used,
        "student_start_gap": finite_float(model.get("start_gap")),
        "student_normalized_start_gap": student_normalized_gap,
        "teacher_start_gap": finite_float(teacher.get("start_gap")),
        "teacher_normalized_start_gap": teacher_normalized_gap,
        "accepted_normalized_start_gap": (
            teacher_normalized_gap if fallback_used else student_normalized_gap
        ),
        "graph_encoding_time_sec": finite_float(prediction.get("graph_encoding_time_sec"), 0.0),
        "gnn_forward_time_sec": finite_float(prediction.get("gnn_forward_time_sec"), 0.0),
        "student_selection_time_sec": selection_time,
        "group_context_time_sec": context_time,
        "group_audit_time_sec": audit_time,
        "student_kernel_time_sec": kernel_time,
        "student_smdp_solve_time_sec": solve_time,
        "student_audited_pipeline_time_sec": student_audited_path,
        "teacher_selection_time_sec": teacher_selection,
        "teacher_pipeline_time_sec": teacher_pipeline,
        "accepted_pipeline_time_sec": accepted_path,
        "selection_speedup_vs_teacher": teacher_selection / max(1e-12, selection_time),
        "selection_plus_audit_speedup_vs_teacher": teacher_selection
        / max(1e-12, selection_time + context_time + audit_time),
        "accepted_speedup_vs_teacher_pipeline": teacher_pipeline / max(1e-12, accepted_path),
        "error": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit GNN-predicted boundary graphs under the production RD protocol.")
    parser.add_argument(
        "--predictions-csv",
        type=Path,
        default=Path("experiments/models/boundary_heatmap_gnn/test_frontier_predictions.csv"),
    )
    parser.add_argument(
        "--teacher-csv",
        type=Path,
        default=Path("experiments/models/boundary_heatmap_gnn/selected_test_teacher.csv"),
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
    parser.add_argument(
        "--fixed-random-count",
        type=int,
        default=0,
        help="Keep zero for the graph-only teacher protocol.",
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
        default=Path("experiments/output/boundary_heatmap_downstream"),
    )
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")
    predictions = load_rows(args.predictions_csv)
    teacher_rows = {context_key(row): row for row in load_rows(args.teacher_csv)}
    jobs = [row for index, row in enumerate(predictions) if index % args.num_shards == args.shard_index]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output_csv = args.out_dir / "boundary_heatmap_downstream.csv"
    rows_out = load_rows(output_csv) if args.resume else []
    completed = {row_key(row) for row in rows_out if not row.get("error")}
    progress = args.out_dir / "progress.jsonl"
    for prediction in jobs:
        key = row_key(prediction)
        if key in completed:
            continue
        try:
            teacher = teacher_rows[context_key(prediction)]
            row = run_context(prediction, teacher, args)
            status = "ok"
        except Exception as exc:
            if not args.continue_on_error:
                raise
            row = {
                "map": prediction.get("map", ""),
                "map_size": prediction.get("map_size", ""),
                "maze_seed": prediction.get("maze_seed", ""),
                "slip": prediction.get("slip", ""),
                "student_method": prediction.get("method", ""),
                "error": repr(exc),
            }
            status = "error"
        rows_out.append(row)
        write_csv_all_fields(output_csv, rows_out)
        with progress.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "map": row.get("map"),
                        "slip": row.get("slip"),
                        "status": status,
                        "student_group_all_feasible": row.get("student_group_all_feasible", ""),
                    },
                    default=json_default,
                )
                + "\n"
            )
    write_csv_all_fields(output_csv, rows_out)
    (args.out_dir / "boundary_heatmap_downstream.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
