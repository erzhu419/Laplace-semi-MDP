#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import parse_map_specs
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_rd_operator_theorem_checks import (
    build_recipe_context,
    boundary_rate,
    evaluate_recipe_boundary,
    finite_float,
    hidden_distortions,
    json_default,
    operator_marginal_rows,
    top_row,
    write_csv,
)


METHOD_FIELDS: Dict[str, str] = {
    "rd_fd": "bits_fd_operator_score",
    "raw_hidden": "raw_hidden_score",
    "random": "random_score",
    "spectral": "spectral_score",
    "betweenness": "betweenness_score",
    "value_gradient": "value_gradient_score",
    "degree": "degree_score",
}


def recipe_with_probe(recipe: Mapping[str, object], residual_kind: str) -> Dict[str, object]:
    out = dict(recipe)
    out["residual_kind"] = residual_kind
    out["residual_top_fraction"] = 1.0
    out["proposal_kind"] = "residual"
    return out


def replace_goal(rows: Tuple[str, ...], goal_state: int) -> Tuple[str, ...]:
    grid = GridWorld(rows)
    _coord_to_idx, idx_to_coord = grid.index_maps()
    new_goal_coord = idx_to_coord[int(goal_state)]
    out: List[str] = []
    for r, row in enumerate(rows):
        chars = list(row)
        for c, ch in enumerate(chars):
            if ch == "G":
                chars[c] = "."
        if r == new_goal_coord[0]:
            chars[new_goal_coord[1]] = "G"
        out.append("".join(chars))
    return tuple(out)


def heldout_goal_variants(rows: Tuple[str, ...], count: int) -> List[Tuple[str, Tuple[str, ...]]]:
    grid = GridWorld(rows)
    start = grid.symbol_states("S")[0]
    original_goal = grid.symbol_states("G")[0]
    _coord_to_idx, idx_to_coord = grid.index_maps()
    start_coord = idx_to_coord[start]

    def manhattan(state: int) -> int:
        coord = idx_to_coord[int(state)]
        return abs(coord[0] - start_coord[0]) + abs(coord[1] - start_coord[1])

    candidates = [state for state in range(grid.n_states) if state not in {start, original_goal}]
    ranked = sorted(candidates, key=lambda state: (manhattan(state), -state), reverse=True)
    variants = [("train_goal", rows)]
    for pos, state in enumerate(ranked[: max(0, int(count))], start=1):
        variants.append((f"heldout_goal_{pos}_state_{state}", replace_goal(rows, state)))
    return variants


def select_boundary(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    method: str,
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    max_splits: int,
    max_candidates: int,
    greedy_positive_only: bool,
) -> Tuple[List[int], List[Dict[str, object]], float]:
    context = build_recipe_context(rows, recipe=recipe, gamma=gamma, slip=slip)
    grid: GridWorld = context["grid"]  # type: ignore[assignment]
    boundary = endpoint_boundary_states(grid)
    trace_rows: List[Dict[str, object]] = []
    field = METHOD_FIELDS[method]
    started = time.perf_counter()
    for step in range(max_splits):
        rows_step, _base_row, _edge_rows = operator_marginal_rows(
            map_name=map_name,
            step=step,
            context=context,
            recipe=recipe,
            boundary=boundary,
            gamma=gamma,
            slip=slip,
            lambda_struct=lambda_struct,
            edge_weight=edge_weight,
            max_candidates=max_candidates,
            with_frozen_recompute=True,
            with_actual_recompute=False,
            with_recompute_modes=False,
        )
        selected = top_row(rows_step, field)
        fd_top = top_row(rows_step, "bits_fd_operator_score")
        if selected is None:
            trace_rows.append(
                {
                    "map": map_name,
                    "method": method,
                    "step": step,
                    "selected_state": None,
                    "stop_reason": "no_candidate",
                }
            )
            break
        selected_state = int(selected["candidate_state"])
        selected_score = finite_float(selected[field])
        trace_rows.append(
            {
                "map": map_name,
                "method": method,
                "step": step,
                "selected_state": selected_state,
                "selected_coord": selected["candidate_coord"],
                "selected_score": selected_score,
                "fd_top_state": int(fd_top["candidate_state"]) if fd_top else None,
                "fd_top_score": finite_float(fd_top["bits_fd_operator_score"]) if fd_top else None,
                "match_fd": (
                    selected_state == int(fd_top["candidate_state"])
                    if fd_top is not None
                    else None
                ),
                "n_boundary_before": len(boundary),
                "n_candidates": len(rows_step),
                "stop_reason": "continue",
            }
        )
        if greedy_positive_only and selected_score <= 0.0:
            trace_rows[-1]["stop_reason"] = "non_positive_score"
            break
        if selected_state in set(boundary):
            trace_rows[-1]["stop_reason"] = "already_boundary"
            break
        boundary = sorted(set(boundary).union({selected_state}))
    return boundary, trace_rows, time.perf_counter() - started


def evaluate_generalization(
    map_name: str,
    rows: Tuple[str, ...],
    selected_boundary: Sequence[int],
    recipe: Mapping[str, object],
    residual_kind: str | None,
    gamma: float,
    slip: float,
    edge_weight: str,
) -> Dict[str, object]:
    probe_recipe = dict(recipe) if residual_kind is None else recipe_with_probe(recipe, residual_kind)
    context = build_recipe_context(rows, recipe=probe_recipe, gamma=gamma, slip=slip)
    grid: GridWorld = context["grid"]  # type: ignore[assignment]
    boundary = sorted(set(int(state) for state in selected_boundary).union(endpoint_boundary_states(grid)))
    row, edge_rows = evaluate_recipe_boundary(
        map_name=map_name,
        context=context,
        recipe=probe_recipe,
        boundary=boundary,
        gamma=gamma,
        slip=slip,
    )
    distortions = hidden_distortions(edge_rows, boundary=boundary, edge_weight=edge_weight)
    uniform_distortions = hidden_distortions(edge_rows, boundary=boundary, edge_weight="uniform")
    return {
        "n_states": int(row["n_states"]),
        "n_boundary_eval": len(boundary),
        "endpoint_augmented_by": len(set(endpoint_boundary_states(grid)) - set(selected_boundary)),
        "n_edges_valid": int(row["n_edges_valid"]),
        "state_compression_ratio": float(row["n_states"]) / max(1.0, float(len(boundary))),
        "rate_bits": boundary_rate(row, probe_recipe),
        "hidden_linear": distortions["linear"],
        "hidden_bits": distortions["bits"],
        "uniform_hidden_linear": uniform_distortions["linear"],
        "uniform_hidden_bits": uniform_distortions["bits"],
        "start_gap": finite_float(row.get("start_gap"), default=float("nan")),
        "value_gap_max": finite_float(row.get("value_gap_max"), default=float("nan")),
        "occupancy_struct_hidden_distinct": finite_float(row.get("occupancy_struct_hidden_distinct")),
        "struct_hidden_distinct_cvar95": finite_float(row.get("struct_hidden_distinct_cvar95")),
    }


def summarize(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["map"]), str(row["method"])), []).append(row)
    out: List[Dict[str, object]] = []
    for (map_name, method), group in sorted(grouped.items()):
        heldout = [row for row in group if str(row["goal_variant"]) != "train_goal"]
        probes = [row for row in group if str(row["residual_probe"]) != "train_recipe"]
        out.append(
            {
                "map": map_name,
                "method": method,
                "n_eval_rows": len(group),
                "selected_boundary_size": group[0]["n_boundary_selected"] if group else None,
                "selection_time_sec": group[0]["selection_time_sec"] if group else None,
                "mean_hidden_bits": float(np.mean([finite_float(row["hidden_bits"]) for row in group])),
                "mean_heldout_goal_hidden_bits": (
                    float(np.mean([finite_float(row["hidden_bits"]) for row in heldout])) if heldout else None
                ),
                "mean_probe_hidden_bits": (
                    float(np.mean([finite_float(row["hidden_bits"]) for row in probes])) if probes else None
                ),
                "mean_start_gap": float(np.mean([finite_float(row["start_gap"]) for row in group])),
                "max_start_gap": max(finite_float(row["start_gap"]) for row in group),
                "mean_value_gap_max": float(np.mean([finite_float(row["value_gap_max"]) for row in group])),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate whether RD Boundary Green selections generalize across held-out goals and residual probes."
    )
    parser.add_argument("--map-specs", nargs="+", default=["maze:11", "four_rooms:11", "open_room:9"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument("--methods", nargs="+", default=list(METHOD_FIELDS))
    parser.add_argument(
        "--residual-probes",
        nargs="+",
        default=["train_recipe", "all", "turn_articulation", "betweenness", "value_gradient", "transition_entropy"],
    )
    parser.add_argument("--heldout-goal-count", type=int, default=2)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-splits", type=int, default=3)
    parser.add_argument("--max-candidates", type=int, default=24)
    parser.add_argument("--greedy-positive-only", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/rd_operator_generalization"))
    args = parser.parse_args()

    unknown = sorted(set(args.methods) - set(METHOD_FIELDS))
    if unknown:
        raise ValueError(f"Unknown method(s): {unknown}. Known: {sorted(METHOD_FIELDS)}")

    recipe = LEARNED_RECIPES[args.recipe]
    eval_rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []
    started = time.perf_counter()
    for _family, _size, map_label, map_rows in parse_map_specs(args.map_specs):
        for method in args.methods:
            boundary, method_trace, selection_time = select_boundary(
                map_name=map_label,
                rows=map_rows,
                recipe=recipe,
                method=method,
                gamma=args.gamma,
                slip=args.slip,
                lambda_struct=args.lambda_struct,
                edge_weight=args.edge_weight,
                max_splits=args.max_splits,
                max_candidates=args.max_candidates,
                greedy_positive_only=args.greedy_positive_only,
            )
            trace_rows.extend(method_trace)
            for goal_variant, goal_rows in heldout_goal_variants(map_rows, args.heldout_goal_count):
                for residual_probe in args.residual_probes:
                    probe_kind = str(recipe["residual_kind"]) if residual_probe == "train_recipe" else residual_probe
                    metrics = evaluate_generalization(
                        map_name=map_label,
                        rows=goal_rows,
                        selected_boundary=boundary,
                        recipe=recipe,
                        residual_kind=None if residual_probe == "train_recipe" else probe_kind,
                        gamma=args.gamma,
                        slip=args.slip,
                        edge_weight=args.edge_weight,
                    )
                    eval_rows.append(
                        {
                            "map": map_label,
                            "method": method,
                            "goal_variant": goal_variant,
                            "residual_probe": residual_probe,
                            "residual_kind_eval": probe_kind,
                            "n_boundary_selected": len(boundary),
                            "selected_boundary": list(boundary),
                            "selection_time_sec": selection_time,
                            **metrics,
                        }
                    )

    summary_rows = summarize(eval_rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "generalization.csv", eval_rows)
    write_csv(args.out_dir / "selection_trace.csv", trace_rows)
    write_csv(args.out_dir / "summary.csv", summary_rows)
    (args.out_dir / "generalization.json").write_text(
        json.dumps(eval_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# RD Operator Generalization\n\n"
        f"- recipe: `{args.recipe}`\n"
        f"- methods: `{', '.join(args.methods)}`\n"
        f"- residual_probes: `{', '.join(args.residual_probes)}`\n"
        f"- heldout_goal_count: {args.heldout_goal_count}\n"
        f"- elapsed_sec: {time.perf_counter() - started:.3f}\n\n"
        "## Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} {row['method']}: "
                f"mean_bits={float(row['mean_hidden_bits']):.4g}, "
                f"heldout_goal_bits={row['mean_heldout_goal_hidden_bits']}, "
                f"probe_bits={row['mean_probe_hidden_bits']}, "
                f"mean_start_gap={float(row['mean_start_gap']):.4g}, "
                f"max_start_gap={float(row['max_start_gap']):.4g}"
            )
            for row in summary_rows
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
