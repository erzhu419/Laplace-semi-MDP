#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import run_one
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import json_default


def run_recipe(
    recipe_name: str,
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    gamma: float,
    max_splits: int,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], float]:
    recipe = LEARNED_RECIPES[recipe_name]
    candidate_rows: List[Dict[str, object]] = []
    start = time.perf_counter()
    trace, _edges = run_one(
        map_name=map_name,
        rows=rows,
        slip=slip,
        gamma=gamma,
        candidate_kind=str(recipe["candidate_kind"]),
        candidate_top_fraction=float(recipe["candidate_top_fraction"]),
        residual_kind=str(recipe["residual_kind"]),
        residual_top_fraction=float(recipe["residual_top_fraction"]),
        soft_kind=str(recipe["soft_kind"]),
        soft_top_fraction=float(recipe["soft_top_fraction"]),
        local_horizon=999.0,
        hidden_threshold=1e-6,
        soft_threshold=float(recipe["soft_threshold"]),
        residual_threshold=float(recipe["residual_threshold"]),
        residual_reward_weight=0.05,
        residual_hit_weight=0.0,
        residual_threshold_mode=str(recipe["residual_threshold_mode"]),
        compute_struct_distinct=bool(recipe["compute_struct_distinct"]),
        struct_mdl_node_cost_weight=1.0,
        struct_mdl_edge_cost_weight=float(recipe["struct_mdl_edge_cost_weight"]),
        struct_mdl_exposure_bit_weight=1.0,
        struct_mdl_min_gain=0.0,
        soft_cost_weight=1.0,
        residual_split_policy=str(recipe["residual_split_policy"]),
        soft_split_policy=str(recipe["soft_split_policy"]),
        max_splits=max_splits,
        proposal_kind=str(recipe.get("proposal_kind", "candidate")),
        exact_mdl_top_k=int(recipe.get("exact_mdl_top_k", 8)),
        exact_mdl_struct_kind=str(recipe.get("exact_mdl_struct_kind", "occupancy_distinct")),
        exact_mdl_option_pair_bit_cost=float(recipe.get("exact_mdl_option_pair_bit_cost", 1.0)),
        exact_mdl_policy_tv_bit_cost=float(recipe.get("exact_mdl_policy_tv_bit_cost", 0.2)),
        exact_mdl_policy_region_bit_cost=float(recipe.get("exact_mdl_policy_region_bit_cost", 0.5)),
        exact_mdl_model_residual_bit_cost=float(recipe.get("exact_mdl_model_residual_bit_cost", 1.0)),
        exact_mdl_include_edge_encoding=bool(recipe.get("exact_mdl_include_edge_encoding", False)),
        rd_top_k=int(recipe.get("rd_top_k", 8)),
        rd_struct_kind=str(recipe.get("rd_struct_kind", "occupancy_distinct")),
        rd_struct_budget=float(recipe.get("rd_struct_budget", float("inf"))),
        rd_audit_kind=str(recipe.get("rd_audit_kind", "none")),
        rd_audit_budget=float(recipe.get("rd_audit_budget", float("inf"))),
        rd_model_budget=float(recipe.get("rd_model_budget", float("inf"))),
        rd_value_budget=float(recipe.get("rd_value_budget", float("inf"))),
        rd_start_gap_budget=float(recipe.get("rd_start_gap_budget", float("inf"))),
        rd_lambda_struct=float(recipe.get("rd_lambda_struct", 0.0)),
        rd_lambda_audit=float(recipe.get("rd_lambda_audit", 0.0)),
        rd_lambda_model=float(recipe.get("rd_lambda_model", 0.0)),
        rd_lambda_value=float(recipe.get("rd_lambda_value", 0.0)),
        rd_lambda_start_gap=float(recipe.get("rd_lambda_start_gap", 0.0)),
        rd_batch_k=int(recipe.get("rd_batch_k", 1)),
        rd_candidate_rows=candidate_rows,
    )
    return trace, candidate_rows, time.perf_counter() - start


def selected_states_by_step(trace: Sequence[Mapping[str, object]]) -> Dict[int, List[int]]:
    out: Dict[int, List[int]] = {}
    for row in trace:
        if row.get("stop_reason") != "continue":
            continue
        states = row.get("split_candidate_states", [])
        if isinstance(states, str):
            try:
                states = json.loads(states)
            except json.JSONDecodeError:
                states = []
        out[int(row["step"])] = [int(state) for state in states]
    return out


def ranked_candidates_by_step(candidate_rows: Sequence[Mapping[str, object]]) -> Dict[int, List[int]]:
    grouped: Dict[int, List[Mapping[str, object]]] = {}
    for row in candidate_rows:
        if str(row.get("mode")) not in {"single", "operator_surrogate"}:
            continue
        grouped.setdefault(int(row["step"]), []).append(row)
    out: Dict[int, List[int]] = {}
    for step, rows in grouped.items():
        rows = sorted(rows, key=lambda row: int(row.get("rank", 10**9)))
        states: List[int] = []
        for row in rows:
            state = row.get("candidate_state", "")
            if state == "":
                continue
            states.append(int(state))
        out[step] = states
    return out


def rank_of(state: int, ranking: Sequence[int]) -> int | None:
    try:
        return list(ranking).index(int(state)) + 1
    except ValueError:
        return None


def compare_agreement(
    map_name: str,
    exact_trace: Sequence[Mapping[str, object]],
    exact_candidates: Sequence[Mapping[str, object]],
    surrogate_trace: Sequence[Mapping[str, object]],
    surrogate_candidates: Sequence[Mapping[str, object]],
) -> List[Dict[str, object]]:
    exact_selected = selected_states_by_step(exact_trace)
    surrogate_selected = selected_states_by_step(surrogate_trace)
    exact_ranked = ranked_candidates_by_step(exact_candidates)
    surrogate_ranked = ranked_candidates_by_step(surrogate_candidates)
    steps = sorted(set(exact_selected).union(surrogate_selected))
    rows: List[Dict[str, object]] = []
    for step in steps:
        exact_states = exact_selected.get(step, [])
        surrogate_states = surrogate_selected.get(step, [])
        exact_first = exact_states[0] if exact_states else None
        surrogate_first = surrogate_states[0] if surrogate_states else None
        rows.append(
            {
                "map": map_name,
                "step": step,
                "exact_selected_states": exact_states,
                "surrogate_selected_states": surrogate_states,
                "exact_first": exact_first,
                "surrogate_first": surrogate_first,
                "first_match": exact_first == surrogate_first,
                "exact_set_subset_surrogate": set(exact_states).issubset(set(surrogate_states)),
                "surrogate_set_subset_exact": set(surrogate_states).issubset(set(exact_states)),
                "exact_first_rank_in_surrogate": (
                    rank_of(exact_first, surrogate_ranked.get(step, [])) if exact_first is not None else None
                ),
                "surrogate_first_rank_in_exact": (
                    rank_of(surrogate_first, exact_ranked.get(step, [])) if surrogate_first is not None else None
                ),
                "surrogate_top8": surrogate_ranked.get(step, [])[:8],
                "exact_top8": exact_ranked.get(step, [])[:8],
            }
        )
    return rows


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare exact RD selected states with cheap RD-surrogate rankings.")
    parser.add_argument("--map-specs", nargs="+", default=["maze:13"])
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--exact-recipe", default="learned_rd_joint_occ2_audit2")
    parser.add_argument("--surrogate-recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/rd_surrogate_agreement"),
    )
    args = parser.parse_args()

    rows: List[Dict[str, object]] = []
    summary: List[Dict[str, object]] = []
    for _family, _size, map_label, map_rows in parse_map_specs(args.map_specs):
        exact_trace, exact_candidates, exact_time = run_recipe(
            args.exact_recipe,
            map_label,
            map_rows,
            slip=args.slip,
            gamma=args.gamma,
            max_splits=args.max_splits,
        )
        surrogate_trace, surrogate_candidates, surrogate_time = run_recipe(
            args.surrogate_recipe,
            map_label,
            map_rows,
            slip=args.slip,
            gamma=args.gamma,
            max_splits=args.max_splits,
        )
        agreement = compare_agreement(
            map_label,
            exact_trace=exact_trace,
            exact_candidates=exact_candidates,
            surrogate_trace=surrogate_trace,
            surrogate_candidates=surrogate_candidates,
        )
        rows.extend(agreement)
        comparable = [row for row in agreement if row["exact_first"] is not None and row["surrogate_first"] is not None]
        first_match_rate = (
            sum(1 for row in comparable if bool(row["first_match"])) / max(1, len(comparable))
        )
        exact_rank_hits = [
            int(row["exact_first_rank_in_surrogate"])
            for row in comparable
            if row["exact_first_rank_in_surrogate"] is not None
        ]
        summary.append(
            {
                "map": map_label,
                "exact_time_sec": exact_time,
                "surrogate_time_sec": surrogate_time,
                "speedup": exact_time / max(1e-12, surrogate_time),
                "exact_steps": len(selected_states_by_step(exact_trace)),
                "surrogate_steps": len(selected_states_by_step(surrogate_trace)),
                "first_match_rate": first_match_rate,
                "mean_exact_rank_in_surrogate": (
                    sum(exact_rank_hits) / len(exact_rank_hits) if exact_rank_hits else None
                ),
                "max_exact_rank_in_surrogate": max(exact_rank_hits) if exact_rank_hits else None,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "agreement.csv", rows)
    write_csv(args.out_dir / "summary.csv", summary)
    (args.out_dir / "agreement.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# RD Surrogate Agreement\n\n"
        + "\n".join(
            (
                f"- {row['map']}: speedup={float(row['speedup']):.3g}x, "
                f"first_match_rate={float(row['first_match_rate']):.3g}, "
                f"mean_exact_rank_in_surrogate={row['mean_exact_rank_in_surrogate']}"
            )
            for row in summary
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
