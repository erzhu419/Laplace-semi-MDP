#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from run_first_boundary_targeted import (
    MAPS,
    GridWorld,
    candidate_boundary_states,
    critical_saliency,
    endpoint_boundary_states,
    evaluate_boundary,
    markdown_table,
    run_one,
    write_csv,
)


RECIPES: Dict[str, Dict[str, object]] = {
    "soft3": {
        "candidate_kind": "articulation_only",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "never",
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "threshold",
    },
    "raw_residual12": {
        "candidate_kind": "articulation_only",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 1.2,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "threshold",
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
    },
    "value_norm4": {
        "candidate_kind": "articulation_only",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 4.0,
        "residual_threshold_mode": "value_norm",
        "residual_split_policy": "threshold",
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
    },
}


def construct_boundary(
    recipe_name: str,
    rows: Tuple[str, ...],
    slip: float,
    gamma: float,
    max_splits: int,
) -> Tuple[GridWorld, List[int], List[int], Dict[str, object]]:
    recipe = RECIPES[recipe_name]
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    candidate_boundary = candidate_boundary_states(
        grid=grid,
        kind=str(recipe["candidate_kind"]),
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=float(recipe["candidate_top_fraction"]),
    )
    trace, _ = run_one(
        map_name="construct",
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
        compute_struct_distinct=False,
        struct_mdl_node_cost_weight=1.0,
        struct_mdl_edge_cost_weight=0.1,
        struct_mdl_exposure_bit_weight=1.0,
        struct_mdl_min_gain=0.0,
        soft_cost_weight=1.0,
        residual_split_policy=str(recipe["residual_split_policy"]),
        soft_split_policy=str(recipe["soft_split_policy"]),
        max_splits=max_splits,
    )
    boundary = set(endpoint_boundary_states(grid))
    for row in trace:
        if row.get("stop_reason") == "continue" and row.get("split_candidate_state") is not None:
            boundary.add(int(row["split_candidate_state"]))
    return grid, sorted(boundary), candidate_boundary, trace[-1]


def lens_boundary(
    grid: GridWorld,
    lens: str,
    gamma: float,
    slip: float,
    top_fraction: float,
) -> List[int]:
    goal = grid.symbol_states("G")[0]
    if lens == "none":
        return endpoint_boundary_states(grid)
    return candidate_boundary_states(
        grid=grid,
        kind=lens,
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=top_fraction,
    )


def summarize(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    lines = [
        "# Residual Probe Sensitivity",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"recipes = {args.recipes}",
        f"lenses = {args.lenses}",
        f"gamma = {args.gamma}, slips = {args.slips}, max_splits = {args.max_splits}",
        "",
        "## Rows",
        "",
        markdown_table(
            rows,
            [
                "recipe",
                "lens",
                "map",
                "slip",
                "n_boundary",
                "bres_size",
                "constructor_stop",
                "model_residual_max",
                "residual_backup_value_norm_max",
                "residual_hidden_mass_max",
                "beta_global",
                "l_gamma_row_max",
                "start_gap",
            ],
        ),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate learned graph boundaries under multiple residual probe lenses.")
    parser.add_argument("--maps", nargs="+", default=list(MAPS.keys()))
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--recipes", nargs="+", default=["soft3", "raw_residual12", "value_norm4"])
    parser.add_argument(
        "--lenses",
        nargs="+",
        default=["junction", "decision", "turn_articulation", "bottleneck", "combined"],
    )
    parser.add_argument("--lens-top-fraction", type=float, default=0.15)
    parser.add_argument("--max-splits", type=int, default=20)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/residual_probe_sensitivity"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows_out: List[Dict[str, object]] = []
    for recipe_name in args.recipes:
        if recipe_name not in RECIPES:
            raise ValueError(f"Unknown recipe: {recipe_name}")
        for map_name in args.maps:
            if map_name not in MAPS:
                raise ValueError(f"Unknown map: {map_name}")
            for slip in args.slips:
                grid, boundary, candidate_boundary, constructor_final = construct_boundary(
                    recipe_name=recipe_name,
                    rows=MAPS[map_name],
                    slip=slip,
                    gamma=args.gamma,
                    max_splits=args.max_splits,
                )
                for lens in args.lenses:
                    residual_boundary = lens_boundary(
                        grid=grid,
                        lens=lens,
                        gamma=args.gamma,
                        slip=slip,
                        top_fraction=args.lens_top_fraction,
                    )
                    row, _ = evaluate_boundary(
                        map_name=map_name,
                        grid=grid,
                        boundary=boundary,
                        candidate_boundary=candidate_boundary,
                        residual_boundary=residual_boundary,
                        soft_state_cost=np.zeros(grid.n_states, dtype=float),
                        slip=slip,
                        gamma=args.gamma,
                        local_horizon=999.0,
                        hidden_threshold=1e-6,
                        soft_threshold=3.0,
                        residual_threshold=1.2,
                        residual_reward_weight=0.05,
                        residual_hit_weight=0.0,
                        residual_threshold_mode="raw",
                        compute_struct_distinct=False,
                        struct_mdl_node_cost_weight=1.0,
                        struct_mdl_edge_cost_weight=0.1,
                        struct_mdl_exposure_bit_weight=1.0,
                        struct_mdl_min_gain=0.0,
                        residual_kind=lens,
                        residual_top_fraction=args.lens_top_fraction,
                        soft_kind="none",
                        soft_top_fraction=0.0,
                        soft_cost_weight=0.0,
                        candidate_kind=str(RECIPES[recipe_name]["candidate_kind"]),
                        candidate_top_fraction=float(RECIPES[recipe_name]["candidate_top_fraction"]),
                    )
                    row.update(
                        {
                            "recipe": recipe_name,
                            "lens": lens,
                            "bres_size": len(set(residual_boundary).union(boundary)),
                            "constructor_stop": constructor_final.get("stop_reason"),
                            "constructor_n_boundary": constructor_final.get("n_boundary"),
                            "constructor_model_residual_max": constructor_final.get("model_residual_max"),
                            "constructor_residual_backup_value_norm_max": constructor_final.get(
                                "residual_backup_value_norm_max"
                            ),
                        }
                    )
                    rows_out.append(row)
                print(
                    f"{recipe_name:14s} {map_name:10s} slip={slip:.2f} "
                    f"B={len(boundary):3d} stop={constructor_final.get('stop_reason')}"
                )

    write_csv(args.out_dir / "sensitivity.csv", rows_out)
    (args.out_dir / "sensitivity.json").write_text(json.dumps(rows_out, indent=2) + "\n", encoding="utf-8")
    summarize(rows_out, args.out_dir / "summary.md", args)
    print(f"Wrote {args.out_dir / 'sensitivity.csv'}")
    print(f"Wrote {args.out_dir / 'sensitivity.json'}")
    print(f"Wrote {args.out_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
