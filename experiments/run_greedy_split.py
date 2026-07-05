#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import (
    GridWorld,
    corridor_map,
    critical_saliency,
    default_map,
    discounted_interior_occupancy,
    endpoint_boundary_states,
    four_rooms_map,
    open_room_map,
    primitive_value_iteration,
    smdp_value_iteration,
)
from run_ablation import (
    build_reductions,
    bypass_stats,
    count_valid_edges,
    description_length_proxy,
    nonlocal_reachability_cost,
    nonzero_kernel_entries,
    policy_complexity_stats,
    reduction_duration_stats,
)


MAPS: Dict[str, Tuple[str, ...]] = {
    "corridor": corridor_map(),
    "open_room": open_room_map(),
    "four_rooms": four_rooms_map(),
    "maze": default_map(),
}


def attribution_scores(
    boundary: Sequence[int],
    primitive_models: Dict[str, Tuple[np.ndarray, np.ndarray]],
    valid_actions: Dict[str, np.ndarray],
    gamma: float,
    state_cost: np.ndarray,
) -> Dict[int, float]:
    attribution_by_state: Dict[int, float] = {}
    for option, (P, _) in primitive_models.items():
        _, interior, occupancy = discounted_interior_occupancy(P, boundary, gamma)
        if len(interior) == 0:
            continue
        valid = valid_actions.get(option, np.ones(len(boundary), dtype=bool))
        attribution = occupancy[valid].sum(axis=0) * state_cost[interior]
        for state, score in zip(interior, attribution):
            attribution_by_state[int(state)] = attribution_by_state.get(int(state), 0.0) + float(score)
    return attribution_by_state


def choose_split_state(
    boundary: Sequence[int],
    primitive_models: Dict[str, Tuple[np.ndarray, np.ndarray]],
    valid_actions: Dict[str, np.ndarray],
    gamma: float,
    state_cost: np.ndarray,
) -> Tuple[int | None, float]:
    attribution_by_state = attribution_scores(
        boundary=boundary,
        primitive_models=primitive_models,
        valid_actions=valid_actions,
        gamma=gamma,
        state_cost=state_cost,
    )
    if not attribution_by_state:
        return None, 0.0
    split_state, best_score = max(attribution_by_state.items(), key=lambda item: item[1])
    if best_score <= 1e-12:
        return None, best_score
    return int(split_state), best_score


def cost_components(row: Dict[str, object]) -> Dict[str, float]:
    graph_cost = float(row["n_boundary"]) + float(row["n_edges_valid"]) / max(1.0, float(row["n_boundary"]))
    option_cost = float(row["n_options"]) + 0.05 * float(row["option_pair_count"])
    policy_cost_total = 0.20 * float(row["policy_tv_total"]) + 0.50 * float(row["policy_regions_total"])
    policy_cost_mean = 0.20 * float(row["policy_tv_mean"]) + 0.50 * float(row["policy_regions_mean"])
    return {
        "graph_cost": graph_cost,
        "option_cost": option_cost,
        "policy_cost_total": policy_cost_total,
        "policy_cost_mean": policy_cost_mean,
        "bypass_cost": float(row["bypass_cost_total"]),
        "nonlocal_cost_component": float(row["nonlocal_cost"]),
        "start_gap_cost": float(row["start_gap"]),
        "value_gap_cost": float(row["value_gap_max"]),
    }


def weighted_objective(
    row: Dict[str, object],
    lambda_start_gap: float,
    lambda_value_gap: float,
    lambda_bypass: float,
    lambda_policy: float,
    lambda_graph: float,
    lambda_option: float,
    lambda_nonlocal: float,
    policy_cost_mode: str,
) -> float:
    components = cost_components(row)
    policy_key = "policy_cost_mean" if policy_cost_mode == "mean" else "policy_cost_total"
    return float(
        lambda_start_gap * components["start_gap_cost"]
        + lambda_value_gap * components["value_gap_cost"]
        + lambda_bypass * components["bypass_cost"]
        + lambda_policy * components[policy_key]
        + lambda_graph * components["graph_cost"]
        + lambda_option * components["option_cost"]
        + lambda_nonlocal * components["nonlocal_cost_component"]
    )


def evaluate_boundary(
    map_name: str,
    grid: GridWorld,
    boundary: Sequence[int],
    slip: float,
    gamma: float,
    option_set: str,
    critical_kind: str,
    critical_top_fraction: float,
    local_horizon: float,
    min_hit_probability: float,
    state_cost: np.ndarray,
    V_full: np.ndarray,
) -> Tuple[Dict[str, object], Dict[str, Tuple[np.ndarray, np.ndarray]], Dict[str, np.ndarray]]:
    start = grid.symbol_states("S")[0]
    goal = grid.symbol_states("G")[0]
    boundary = sorted(set(boundary))
    boundary_to_pos = {s: i for i, s in enumerate(boundary)}
    reductions, valid_actions, primitive_models, policies, option_metadata = build_reductions(
        grid=grid,
        boundary=boundary,
        option_set=option_set,
        slip=slip,
        gamma=gamma,
        local_horizon=local_horizon,
    )
    V_smdp, policy_smdp = smdp_value_iteration(
        reductions,
        goal_boundary_position=boundary_to_pos[goal],
        valid_actions=valid_actions or None,
    )
    boundary_full = V_full[np.array(boundary)]
    value_gap = np.abs(V_smdp - boundary_full)
    duration_mean, duration_max = reduction_duration_stats(reductions, valid_actions)
    bypass_mean, bypass_total = bypass_stats(
        boundary,
        reductions,
        primitive_models,
        valid_actions,
        gamma,
        state_cost,
    )
    policy_metrics = policy_complexity_stats(grid, policies)
    nonlocal_cost = nonlocal_reachability_cost(grid, reductions, valid_actions, local_horizon)

    start_pos = boundary_to_pos[start]
    goal_pos = boundary_to_pos[goal]
    nonterminal = np.ones(len(boundary), dtype=bool)
    nonterminal[goal_pos] = False
    row: Dict[str, object] = {
        "map": map_name,
        "slip": slip,
        "gamma": gamma,
        "option_set": option_set,
        "critical_kind": critical_kind,
        "critical_top_fraction": critical_top_fraction,
        "local_horizon": local_horizon,
        "n_states": grid.n_states,
        "n_boundary": len(boundary),
        "n_options": len(reductions),
        "option_pair_count": int(option_metadata["option_pair_count"]),
        "n_edges_valid": count_valid_edges(reductions, valid_actions, min_hit_probability),
        "kernel_entries_valid": nonzero_kernel_entries(reductions, valid_actions, min_hit_probability),
        "critical_nonzero": int(np.sum(state_cost > 1e-12)),
        "critical_mass": float(state_cost.sum()),
        "duration_mean": duration_mean,
        "duration_max": duration_max,
        "bypass_cost_mean": bypass_mean,
        "bypass_cost_total": bypass_total,
        "nonlocal_cost": nonlocal_cost,
        "value_gap_max": float(value_gap[nonterminal].max()) if np.any(nonterminal) else 0.0,
        "start_value_smdp": float(V_smdp[start_pos]),
        "start_value_primitive": float(V_full[start]),
        "start_gap": float(abs(V_smdp[start_pos] - V_full[start])),
        "start_best_option": policy_smdp[start_pos],
    }
    row.update(policy_metrics)
    row.update(cost_components(row))
    row["description_length_proxy"] = description_length_proxy(row)
    return row, primitive_models, valid_actions


def choose_objective_split_state(
    map_name: str,
    grid: GridWorld,
    boundary: Sequence[int],
    current_objective: float,
    attribution_by_state: Dict[int, float],
    slip: float,
    gamma: float,
    option_set: str,
    critical_kind: str,
    critical_top_fraction: float,
    local_horizon: float,
    min_hit_probability: float,
    state_cost: np.ndarray,
    V_full: np.ndarray,
    candidate_limit: int,
    lambda_start_gap: float,
    lambda_value_gap: float,
    lambda_bypass: float,
    lambda_policy: float,
    lambda_graph: float,
    lambda_option: float,
    lambda_nonlocal: float,
    policy_cost_mode: str,
) -> Tuple[int | None, float, float | None, float, int]:
    candidates = [
        (state, score)
        for state, score in attribution_by_state.items()
        if score > 1e-12 and state not in set(boundary)
    ]
    candidates.sort(key=lambda item: item[1], reverse=True)
    if candidate_limit > 0:
        candidates = candidates[:candidate_limit]
    if not candidates:
        return None, 0.0, None, 0.0, 0

    best_state: int | None = None
    best_score = 0.0
    best_objective: float | None = None
    for state, score in candidates:
        candidate_row, _, _ = evaluate_boundary(
            map_name=map_name,
            grid=grid,
            boundary=[*boundary, state],
            slip=slip,
            gamma=gamma,
            option_set=option_set,
            critical_kind=critical_kind,
            critical_top_fraction=critical_top_fraction,
            local_horizon=local_horizon,
            min_hit_probability=min_hit_probability,
            state_cost=state_cost,
            V_full=V_full,
        )
        objective = weighted_objective(
            candidate_row,
            lambda_start_gap=lambda_start_gap,
            lambda_value_gap=lambda_value_gap,
            lambda_bypass=lambda_bypass,
            lambda_policy=lambda_policy,
            lambda_graph=lambda_graph,
            lambda_option=lambda_option,
            lambda_nonlocal=lambda_nonlocal,
            policy_cost_mode=policy_cost_mode,
        )
        if best_objective is None or objective < best_objective:
            best_state = int(state)
            best_score = float(score)
            best_objective = float(objective)

    objective_delta = current_objective - best_objective if best_objective is not None else 0.0
    return best_state, best_score, best_objective, float(objective_delta), len(candidates)


def run_one(
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    gamma: float,
    option_set: str,
    critical_kind: str,
    critical_top_fraction: float,
    local_horizon: float,
    max_splits: int,
    bypass_threshold: float,
    min_hit_probability: float,
    split_strategy: str,
    candidate_limit: int,
    min_objective_improvement: float,
    lambda_start_gap: float,
    lambda_value_gap: float,
    lambda_bypass: float,
    lambda_policy: float,
    lambda_graph: float,
    lambda_option: float,
    lambda_nonlocal: float,
    policy_cost_mode: str,
) -> List[Dict[str, object]]:
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    boundary = endpoint_boundary_states(grid)
    state_cost = critical_saliency(
        grid,
        kind=critical_kind,
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=critical_top_fraction,
    )
    V_full = primitive_value_iteration(grid, goal_state=goal, gamma=gamma, slip=slip)
    split_rows: List[Dict[str, object]] = []

    for step in range(max_splits + 1):
        boundary = sorted(set(boundary))
        row, primitive_models, valid_actions = evaluate_boundary(
            map_name=map_name,
            grid=grid,
            boundary=boundary,
            slip=slip,
            gamma=gamma,
            option_set=option_set,
            critical_kind=critical_kind,
            critical_top_fraction=critical_top_fraction,
            local_horizon=local_horizon,
            min_hit_probability=min_hit_probability,
            state_cost=state_cost,
            V_full=V_full,
        )
        current_objective = weighted_objective(
            row,
            lambda_start_gap=lambda_start_gap,
            lambda_value_gap=lambda_value_gap,
            lambda_bypass=lambda_bypass,
            lambda_policy=lambda_policy,
            lambda_graph=lambda_graph,
            lambda_option=lambda_option,
            lambda_nonlocal=lambda_nonlocal,
            policy_cost_mode=policy_cost_mode,
        )
        scores = attribution_scores(
            boundary=boundary,
            primitive_models=primitive_models,
            valid_actions=valid_actions,
            gamma=gamma,
            state_cost=state_cost,
        )
        split_state: int | None
        split_score: float
        candidate_objective: float | None = None
        objective_delta = 0.0
        evaluated_candidates = 0
        if split_strategy == "bypass_attribution":
            split_state, split_score = choose_split_state(
                boundary=boundary,
                primitive_models=primitive_models,
                valid_actions=valid_actions,
                gamma=gamma,
                state_cost=state_cost,
            )
        elif split_strategy == "weighted_objective":
            split_state, split_score, candidate_objective, objective_delta, evaluated_candidates = choose_objective_split_state(
                map_name=map_name,
                grid=grid,
                boundary=boundary,
                current_objective=current_objective,
                attribution_by_state=scores,
                slip=slip,
                gamma=gamma,
                option_set=option_set,
                critical_kind=critical_kind,
                critical_top_fraction=critical_top_fraction,
                local_horizon=local_horizon,
                min_hit_probability=min_hit_probability,
                state_cost=state_cost,
                V_full=V_full,
                candidate_limit=candidate_limit,
                lambda_start_gap=lambda_start_gap,
                lambda_value_gap=lambda_value_gap,
                lambda_bypass=lambda_bypass,
                lambda_policy=lambda_policy,
                lambda_graph=lambda_graph,
                lambda_option=lambda_option,
                lambda_nonlocal=lambda_nonlocal,
                policy_cost_mode=policy_cost_mode,
            )
        else:
            raise ValueError(f"Unknown split strategy: {split_strategy}")

        stop_reason = "continue"
        selected_state = split_state
        if float(row["bypass_cost_total"]) <= bypass_threshold:
            stop_reason = "bypass_threshold"
            selected_state = None
        elif split_state is None:
            stop_reason = "no_candidate"
        elif split_strategy == "weighted_objective" and objective_delta <= min_objective_improvement:
            stop_reason = "no_objective_improvement"
            selected_state = None
        elif step >= max_splits:
            stop_reason = "max_splits"
            selected_state = None

        _, idx_to_coord = grid.index_maps()
        row.update(
            {
                "step": step,
                "split_strategy": split_strategy,
                "candidate_limit": candidate_limit,
                "policy_cost_mode": policy_cost_mode,
                "lambda_start_gap": lambda_start_gap,
                "lambda_value_gap": lambda_value_gap,
                "lambda_bypass": lambda_bypass,
                "lambda_policy": lambda_policy,
                "lambda_graph": lambda_graph,
                "lambda_option": lambda_option,
                "lambda_nonlocal": lambda_nonlocal,
                "split_objective": current_objective,
                "candidate_split_state": split_state,
                "candidate_split_coord": idx_to_coord[split_state] if split_state is not None else None,
                "candidate_split_score": split_score,
                "candidate_split_objective": candidate_objective,
                "objective_delta": objective_delta,
                "evaluated_candidates": evaluated_candidates,
                "selected_split_state": selected_state,
                "selected_split_coord": idx_to_coord[selected_state] if selected_state is not None else None,
                "selected_split_score": split_score if selected_state is not None else 0.0,
                "stop_reason": stop_reason,
            }
        )
        split_rows.append(row)

        if selected_state is None:
            break
        boundary.append(selected_state)

    return split_rows


def markdown_table(rows: Sequence[Dict[str, object]], columns: Sequence[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        vals = []
        for col in columns:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.4g}" if abs(val) >= 1e-9 else f"{val:.1e}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(rows: Sequence[Dict[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    final_rows: List[Dict[str, object]] = []
    for key in sorted({(r["map"], r["slip"]) for r in rows}):
        run_rows = [r for r in rows if (r["map"], r["slip"]) == key]
        final_rows.append(run_rows[-1])

    lines = [
        "# Greedy Split",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"option_set = {args.option_set}, critical_kind = {args.critical_kind}, critical_top_fraction = {args.critical_top_fraction}",
        f"gamma = {args.gamma}, slips = {args.slips}, max_splits = {args.max_splits}, bypass_threshold = {args.bypass_threshold}",
        f"split_strategy = {args.split_strategy}, policy_cost_mode = {args.policy_cost_mode}, candidate_limit = {args.candidate_limit}",
        (
            "objective = "
            f"{args.lambda_start_gap}*start_gap + {args.lambda_value_gap}*value_gap "
            f"+ {args.lambda_bypass}*bypass + {args.lambda_policy}*policy "
            f"+ {args.lambda_graph}*graph + {args.lambda_option}*option + {args.lambda_nonlocal}*nonlocal"
        ),
        "",
        "## Final Rows",
        "",
        markdown_table(
            final_rows,
            [
                "map",
                "slip",
                "step",
                "n_boundary",
                "start_gap",
                "bypass_cost_total",
                "split_objective",
                "objective_delta",
                "description_length_proxy",
                "policy_tv_total",
                "candidate_split_coord",
                "selected_split_state",
                "selected_split_coord",
                "stop_reason",
            ],
        ),
        "",
        "## Split Trace",
        "",
        markdown_table(
            rows,
            [
                "map",
                "slip",
                "step",
                "n_boundary",
                "start_gap",
                "bypass_cost_total",
                "split_objective",
                "objective_delta",
                "candidate_split_coord",
                "selected_split_state",
                "selected_split_coord",
                "selected_split_score",
                "stop_reason",
            ],
        ),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Greedily add boundary states that a chosen option bypasses.")
    parser.add_argument("--maps", nargs="+", default=list(MAPS.keys()))
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--option-set", default="targeted")
    parser.add_argument(
        "--critical-kind",
        choices=["none", "decision", "bottleneck", "betweenness", "value_gradient", "transition_entropy", "combined"],
        default="bottleneck",
    )
    parser.add_argument("--critical-top-fraction", type=float, default=0.15)
    parser.add_argument("--local-horizon", type=float, default=8.0)
    parser.add_argument("--max-splits", type=int, default=12)
    parser.add_argument("--bypass-threshold", type=float, default=1e-6)
    parser.add_argument("--min-hit-probability", type=float, default=1e-5)
    parser.add_argument(
        "--split-strategy",
        choices=["bypass_attribution", "weighted_objective"],
        default="bypass_attribution",
    )
    parser.add_argument("--candidate-limit", type=int, default=50)
    parser.add_argument("--min-objective-improvement", type=float, default=1e-9)
    parser.add_argument("--lambda-start-gap", type=float, default=100.0)
    parser.add_argument("--lambda-value-gap", type=float, default=10.0)
    parser.add_argument("--lambda-bypass", type=float, default=100.0)
    parser.add_argument("--lambda-policy", type=float, default=0.2)
    parser.add_argument("--lambda-graph", type=float, default=1.0)
    parser.add_argument("--lambda-option", type=float, default=1.0)
    parser.add_argument("--lambda-nonlocal", type=float, default=0.1)
    parser.add_argument("--policy-cost-mode", choices=["total", "mean"], default="total")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/greedy_split_bottleneck"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        for slip in args.slips:
            trace = run_one(
                map_name=map_name,
                rows=MAPS[map_name],
                slip=slip,
                gamma=args.gamma,
                option_set=args.option_set,
                critical_kind=args.critical_kind,
                critical_top_fraction=args.critical_top_fraction,
                local_horizon=args.local_horizon,
                max_splits=args.max_splits,
                bypass_threshold=args.bypass_threshold,
                min_hit_probability=args.min_hit_probability,
                split_strategy=args.split_strategy,
                candidate_limit=args.candidate_limit,
                min_objective_improvement=args.min_objective_improvement,
                lambda_start_gap=args.lambda_start_gap,
                lambda_value_gap=args.lambda_value_gap,
                lambda_bypass=args.lambda_bypass,
                lambda_policy=args.lambda_policy,
                lambda_graph=args.lambda_graph,
                lambda_option=args.lambda_option,
                lambda_nonlocal=args.lambda_nonlocal,
                policy_cost_mode=args.policy_cost_mode,
            )
            rows.extend(trace)
            final = trace[-1]
            print(
                f"{map_name:10s} slip={slip:.2f} steps={final['step']:2d} B={final['n_boundary']:3d} "
                f"gap={final['start_gap']:.3e} bypass={final['bypass_cost_total']:.3e} "
                f"dl={final['description_length_proxy']:.2f}"
            )

    csv_path = args.out_dir / "trace.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path = args.out_dir / "trace.json"
    json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    report_path = args.out_dir / "summary.md"
    write_report(rows, report_path, args)
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
