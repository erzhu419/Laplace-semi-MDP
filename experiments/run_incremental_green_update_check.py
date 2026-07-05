#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import (
    FirstHitGreenState,
    GridWorld,
    endpoint_boundary_states,
    first_hit_green_state,
    insert_first_hit_terminal,
    shortest_path_policy_to_target,
    transition_matrix_for_policy,
)
from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import fixed_basis, parse_group_specs
from run_rd_multiprobe_basis import build_probe_context
from run_rd_operator_theorem_checks import phi_bits


def row_position(state: FirstHitGreenState, start_state: int) -> int | None:
    matches = np.flatnonzero(state.interior == int(start_state))
    if len(matches) == 0:
        return None
    return int(matches[0])


def hidden_mass(state: FirstHitGreenState, start_state: int, boundary: Sequence[int]) -> float:
    row_pos = row_position(state, start_state)
    if row_pos is None:
        return 0.0
    boundary_set = set(int(s) for s in boundary)
    total = 0.0
    for col, terminal in enumerate(state.terminals.tolist()):
        if int(terminal) not in boundary_set:
            total += float(state.hit_probability[row_pos, col])
    return max(0.0, total)


def max_kernel_diff(a: FirstHitGreenState, b: FirstHitGreenState) -> float:
    if tuple(a.terminals.tolist()) != tuple(b.terminals.tolist()):
        return float("inf")
    if tuple(a.interior.tolist()) != tuple(b.interior.tolist()):
        return float("inf")
    if a.hit_probability.shape != b.hit_probability.shape:
        return float("inf")
    return float(np.max(np.abs(a.hit_probability - b.hit_probability), initial=0.0))


def top_state(scores: Mapping[int, float]) -> int | None:
    if not scores:
        return None
    return max(scores, key=lambda state: (float(scores[state]), -int(state)))


def finite_max(values: Sequence[float]) -> float:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return max(finite) if finite else float("nan")


def median(values: Sequence[float]) -> float:
    finite = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not finite:
        return float("nan")
    mid = len(finite) // 2
    if len(finite) % 2 == 1:
        return finite[mid]
    return 0.5 * (finite[mid - 1] + finite[mid])


def score_error(candidate_scores: Mapping[int, float], exact_scores: Mapping[int, float]) -> float:
    states = set(candidate_scores).union(exact_scores)
    if not states:
        return 0.0
    return max(abs(float(candidate_scores.get(state, 0.0)) - float(exact_scores.get(state, 0.0))) for state in states)


def run_case(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    slip: float,
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    grid = GridWorld(rows)
    lens_groups = parse_group_specs(args.lens_groups)
    train_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
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
    boundary = sorted(set(endpoint_boundary_states(grid)).intersection(set(basis)))
    candidates = [state for state in basis if state not in set(boundary)]
    if args.max_candidates > 0:
        candidates = candidates[: args.max_candidates]

    exact_scores: Dict[int, float] = defaultdict(float)
    current_scores: Dict[int, float] = defaultdict(float)
    static_scores: Dict[int, float] = defaultdict(float)
    update_scores: Dict[int, float] = defaultdict(float)
    score_update_scores: Dict[int, float] = defaultdict(float)

    parent_solve_time = 0.0
    static_solve_time = 0.0
    full_child_solve_time = 0.0
    update_time = 0.0
    scoring_time = 0.0
    score_update_time = 0.0
    parent_solves = 0
    static_solves = 0
    full_child_solves = 0
    insertion_updates = 0
    fresh_child_count = 0
    edges = 0
    update_kernel_errors: List[float] = []
    update_hidden_errors: List[float] = []
    static_hidden_errors: List[float] = []
    current_hidden_errors: List[float] = []
    score_update_hidden_errors: List[float] = []

    for probe in train_probes:
        context = build_probe_context(
            rows,
            recipe=recipe,
            fixed_candidate_basis=basis,
            residual_kind=probe,
            gamma=args.gamma,
            slip=slip,
            probe_top_fraction=args.probe_top_fraction,
        )
        residual_base = set(int(state) for state in context["residual_boundary"])  # type: ignore[index]
        for target_state in boundary:
            policy = shortest_path_policy_to_target(grid, int(target_state), slip=slip)
            P_free, _r_free = transition_matrix_for_policy(grid, policy, absorbing=[])
            for src_state in boundary:
                if int(src_state) == int(target_state):
                    continue
                edges += 1
                parent_terminals = sorted((residual_base.union(boundary)) - {int(src_state)})
                parent_start = time.perf_counter()
                parent = first_hit_green_state(P_free, parent_terminals)
                parent_solve_time += time.perf_counter() - parent_start
                parent_solves += 1

                static_terminals = sorted((residual_base.union(basis)) - {int(src_state)})
                static_start = time.perf_counter()
                static = first_hit_green_state(P_free, static_terminals)
                static_solve_time += time.perf_counter() - static_start
                static_solves += 1

                before = hidden_mass(parent, int(src_state), boundary)
                static_before = hidden_mass(static, int(src_state), boundary)
                parent_terminal_set = set(int(term) for term in parent.terminals.tolist())
                parent_interior_pos = {int(state): pos for pos, state in enumerate(parent.interior.tolist())}
                src_pos = row_position(parent, int(src_state))

                for candidate in candidates:
                    child_boundary = sorted(set(boundary).union({int(candidate)}))
                    if int(candidate) in parent_terminal_set:
                        direct_child = parent
                    else:
                        fresh_child_count += 1
                        child_terminals = sorted(parent_terminal_set.union({int(candidate)}))
                        full_start = time.perf_counter()
                        direct_child = first_hit_green_state(P_free, child_terminals)
                        full_child_solve_time += time.perf_counter() - full_start
                        full_child_solves += 1

                    update_start = time.perf_counter()
                    updated_child = insert_first_hit_terminal(parent, int(candidate))
                    update_time += time.perf_counter() - update_start
                    if int(candidate) not in parent_terminal_set:
                        insertion_updates += 1
                    update_kernel_errors.append(max_kernel_diff(direct_child, updated_child))

                    score_start = time.perf_counter()
                    exact_after = hidden_mass(direct_child, int(src_state), child_boundary)
                    current_after = hidden_mass(parent, int(src_state), child_boundary)
                    static_after = hidden_mass(static, int(src_state), child_boundary)
                    update_after = hidden_mass(updated_child, int(src_state), child_boundary)

                    exact_scores[int(candidate)] += phi_bits(before) - phi_bits(exact_after)
                    current_scores[int(candidate)] += phi_bits(before) - phi_bits(current_after)
                    static_scores[int(candidate)] += phi_bits(static_before) - phi_bits(static_after)
                    update_scores[int(candidate)] += phi_bits(before) - phi_bits(update_after)
                    scoring_time += time.perf_counter() - score_start

                    update_hidden_errors.append(abs(exact_after - update_after))
                    current_hidden_errors.append(abs(exact_after - current_after))
                    static_hidden_errors.append(abs(exact_after - static_after))

                    score_update_start = time.perf_counter()
                    if int(candidate) in parent_terminal_set:
                        score_update_after = current_after
                    else:
                        candidate_pos = parent_interior_pos[int(candidate)]
                        if src_pos is None:
                            score_update_after = 0.0
                        else:
                            pivot = float(parent.fundamental[candidate_pos, candidate_pos])
                            hit_candidate_before_boundary = (
                                float(parent.fundamental[src_pos, candidate_pos]) / max(1e-300, pivot)
                            )
                            candidate_to_old_hidden = hidden_mass(parent, int(candidate), boundary)
                            score_update_after = max(
                                0.0,
                                before - hit_candidate_before_boundary * candidate_to_old_hidden,
                            )
                    score_update_scores[int(candidate)] += phi_bits(before) - phi_bits(score_update_after)
                    score_update_time += time.perf_counter() - score_update_start
                    score_update_hidden_errors.append(abs(exact_after - score_update_after))

    exact_top = top_state(exact_scores)
    mode_specs = [
        {
            "mode": "full_recompute",
            "scores": exact_scores,
            "wall_time_sec": parent_solve_time + full_child_solve_time + scoring_time,
            "green_solve_time_sec": parent_solve_time + full_child_solve_time,
            "green_update_time_sec": 0.0,
            "n_green_solves": parent_solves + full_child_solves,
            "n_green_updates": 0,
            "max_kernel_error_vs_exact": 0.0,
            "max_hidden_error_vs_exact": 0.0,
        },
        {
            "mode": "current_frozen_operator",
            "scores": current_scores,
            "wall_time_sec": parent_solve_time + scoring_time,
            "green_solve_time_sec": parent_solve_time,
            "green_update_time_sec": 0.0,
            "n_green_solves": parent_solves,
            "n_green_updates": 0,
            "max_kernel_error_vs_exact": float("nan"),
            "max_hidden_error_vs_exact": finite_max(current_hidden_errors),
        },
        {
            "mode": "static_basis_reuse",
            "scores": static_scores,
            "wall_time_sec": static_solve_time + scoring_time,
            "green_solve_time_sec": static_solve_time,
            "green_update_time_sec": 0.0,
            "n_green_solves": static_solves,
            "n_green_updates": 0,
            "max_kernel_error_vs_exact": float("nan"),
            "max_hidden_error_vs_exact": finite_max(static_hidden_errors),
        },
        {
            "mode": "boundary_insertion_update",
            "scores": update_scores,
            "wall_time_sec": parent_solve_time + update_time + scoring_time,
            "green_solve_time_sec": parent_solve_time,
            "green_update_time_sec": update_time,
            "n_green_solves": parent_solves,
            "n_green_updates": insertion_updates,
            "max_kernel_error_vs_exact": finite_max(update_kernel_errors),
            "max_hidden_error_vs_exact": finite_max(update_hidden_errors),
        },
        {
            "mode": "boundary_insertion_score_update",
            "scores": score_update_scores,
            "wall_time_sec": parent_solve_time + score_update_time,
            "green_solve_time_sec": parent_solve_time,
            "green_update_time_sec": score_update_time,
            "n_green_solves": parent_solves,
            "n_green_updates": insertion_updates,
            "max_kernel_error_vs_exact": float("nan"),
            "max_hidden_error_vs_exact": finite_max(score_update_hidden_errors),
        },
    ]

    rows_out: List[Dict[str, object]] = []
    full_time = float(mode_specs[0]["wall_time_sec"])
    for mode in mode_specs:
        scores: Mapping[int, float] = mode["scores"]  # type: ignore[assignment]
        selected = top_state(scores)
        rows_out.append(
            {
                "map_family": family,
                "map_size": size,
                "map": map_label,
                "slip": slip,
                "mode": mode["mode"],
                "n_states": grid.n_states,
                "n_basis": len(basis),
                "n_boundary": len(boundary),
                "n_candidates": len(candidates),
                "n_probes": len(train_probes),
                "n_edges": edges,
                "selected_state": selected if selected is not None else "",
                "exact_selected_state": exact_top if exact_top is not None else "",
                "selected_state_match": bool(selected == exact_top),
                "max_score_error_vs_exact": score_error(scores, exact_scores),
                "max_kernel_error_vs_exact": mode["max_kernel_error_vs_exact"],
                "max_hidden_error_vs_exact": mode["max_hidden_error_vs_exact"],
                "wall_time_sec": float(mode["wall_time_sec"]),
                "speedup_vs_full_recompute": full_time / max(1e-12, float(mode["wall_time_sec"])),
                "green_solve_time_sec": float(mode["green_solve_time_sec"]),
                "green_update_time_sec": float(mode["green_update_time_sec"]),
                "operator_delta_time_sec": scoring_time,
                "n_green_solves": int(mode["n_green_solves"]),
                "n_green_updates": int(mode["n_green_updates"]),
                "fresh_child_count": int(fresh_child_count),
                "parent_update_rate": (
                    int(mode["n_green_updates"]) / max(1, fresh_child_count)
                    if str(mode["mode"]).startswith("boundary_insertion")
                    else 0.0
                ),
                "cache_hit_rate": 0.0,
            }
        )
    return rows_out


def aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    modes = sorted({str(row["mode"]) for row in rows})
    out: List[Dict[str, object]] = []
    for mode in modes:
        group = [row for row in rows if str(row["mode"]) == mode]
        out.append(
            {
                "mode": mode,
                "n_rows": len(group),
                "selected_state_match_rate": sum(1 for row in group if bool(row["selected_state_match"])) / max(1, len(group)),
                "median_wall_time_sec": median([float(row["wall_time_sec"]) for row in group]),
                "median_speedup_vs_full_recompute": median([float(row["speedup_vs_full_recompute"]) for row in group]),
                "max_speedup_vs_full_recompute": max(float(row["speedup_vs_full_recompute"]) for row in group),
                "max_score_error_vs_exact": finite_max([float(row["max_score_error_vs_exact"]) for row in group]),
                "max_kernel_error_vs_exact": finite_max([float(row["max_kernel_error_vs_exact"]) for row in group]),
                "max_hidden_error_vs_exact": finite_max([float(row["max_hidden_error_vs_exact"]) for row in group]),
                "median_n_green_solves": median([float(row["n_green_solves"]) for row in group]),
                "median_n_green_updates": median([float(row["n_green_updates"]) for row in group]),
                "median_parent_update_rate": median([float(row["parent_update_rate"]) for row in group]),
            }
        )
    return out


def write_report(
    rows: Sequence[Mapping[str, object]],
    aggregate: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    aggregate_columns = [
        "mode",
        "n_rows",
        "selected_state_match_rate",
        "median_wall_time_sec",
        "median_speedup_vs_full_recompute",
        "max_speedup_vs_full_recompute",
        "max_score_error_vs_exact",
        "max_kernel_error_vs_exact",
        "max_hidden_error_vs_exact",
        "median_n_green_solves",
        "median_n_green_updates",
        "median_parent_update_rate",
    ]
    row_columns = [
        "map",
        "slip",
        "mode",
        "n_states",
        "n_candidates",
        "selected_state",
        "exact_selected_state",
        "selected_state_match",
        "max_score_error_vs_exact",
        "max_kernel_error_vs_exact",
        "max_hidden_error_vs_exact",
        "wall_time_sec",
        "speedup_vs_full_recompute",
        "n_green_solves",
        "n_green_updates",
        "parent_update_rate",
    ]
    lines = [
        "# Incremental Green Update Check",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"slips = {list(args.slips)}",
        "",
        "This benchmark checks exact parent-to-child first-hit Green boundary insertion updates against direct child recomputation.",
        "",
        "## Aggregate",
        "",
        markdown_table([{col: row.get(col, "") for col in aggregate_columns} for row in aggregate], aggregate_columns),
        "",
        "## Rows",
        "",
        markdown_table([{col: row.get(col, "") for col in row_columns} for row in rows], row_columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check exact incremental first-hit Green insertion updates.")
    parser.add_argument("--map-specs", nargs="+", default=["open_room:7", "four_rooms:7", "maze:9"])
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
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
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--max-candidates", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/incremental_green_update"))
    args = parser.parse_args()

    rows_out: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        for slip in args.slips:
            rows_out.extend(
                run_case(
                    family=family,
                    size=size,
                    map_label=map_label,
                    rows=map_rows,
                    slip=slip,
                    args=args,
                )
            )
    aggregate = aggregate_rows(rows_out)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "incremental_green_update.csv", rows_out)
    write_csv_all_fields(args.out_dir / "incremental_green_update_aggregate.csv", aggregate)
    (args.out_dir / "incremental_green_update.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows_out, aggregate, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
