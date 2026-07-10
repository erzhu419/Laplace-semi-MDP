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
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import GridWorld
from compression_experiment_utils import parse_map_specs, transition_nnz_proxy
from planner_baselines import build_sparse_grid_model, quantiles, sparse_value_iteration_measured
from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from state_abstraction_baselines import (
    choose_epsilon_partition,
    epsilon_homogeneous_partition,
    evaluate_partition,
    gridworld_finite_mdp,
    policy_kron_oracle,
    qstar_oracle_partition,
)


METHODS = (
    "exact_model_minimization",
    "epsilon_homogeneous",
    "qstar_oracle_aggregation",
    "policy_kron_oracle",
)


def read_existing(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def target_counts(n_states: int, budget_fractions: Sequence[float], explicit: Sequence[int]) -> List[int]:
    counts = {max(2, min(n_states, int(value))) for value in explicit}
    counts.update(max(2, min(n_states, int(math.ceil(float(frac) * n_states)))) for frac in budget_fractions)
    return sorted(counts)


def normalized_gap(gap: float, full_value: np.ndarray) -> float:
    scale = max(1.0, float(np.max(full_value) - np.min(full_value)), float(np.max(np.abs(full_value))))
    return float(gap) / scale


def run_method(
    method: str,
    mdp,
    full_value: np.ndarray,
    gamma: float,
    target_count: int,
) -> Dict[str, object]:
    selection_started = time.perf_counter()
    epsilon: float | str = ""
    if method == "exact_model_minimization":
        blocks = epsilon_homogeneous_partition(mdp, epsilon=0.0)
        epsilon = 0.0
        selection_time = time.perf_counter() - selection_started
        metrics = evaluate_partition(mdp, blocks, full_value=full_value, gamma=gamma)
    elif method == "epsilon_homogeneous":
        blocks, epsilon = choose_epsilon_partition(mdp, target_count=target_count)
        selection_time = time.perf_counter() - selection_started
        metrics = evaluate_partition(mdp, blocks, full_value=full_value, gamma=gamma)
    elif method == "qstar_oracle_aggregation":
        blocks = qstar_oracle_partition(
            mdp,
            full_value=full_value,
            gamma=gamma,
            target_count=target_count,
        )
        selection_time = time.perf_counter() - selection_started
        metrics = evaluate_partition(mdp, blocks, full_value=full_value, gamma=gamma)
    elif method == "policy_kron_oracle":
        metrics = policy_kron_oracle(
            mdp,
            full_value=full_value,
            gamma=gamma,
            target_count=target_count,
        )
        selection_time = time.perf_counter() - selection_started - float(metrics["construction_time_sec"]) - float(
            metrics["solve_time_sec"]
        )
        selection_time = max(0.0, selection_time)
    else:
        raise ValueError(f"Unknown abstraction baseline: {method}")
    return {
        **metrics,
        "epsilon": epsilon,
        "selection_time_sec": selection_time,
    }


def aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str, str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("error"):
            continue
        grouped[
            (
                str(row.get("map", "")),
                str(row.get("slip", "")),
                str(row.get("method", "")),
                str(row.get("target_count", "")),
            )
        ].append(row)
    aggregate: List[Dict[str, object]] = []
    for (map_name, slip, method, target), group in sorted(grouped.items()):
        q1, median_total, q3 = quantiles(finite_float(row.get("total_time_sec")) for row in group)
        aggregate.append(
            {
                "map": map_name,
                "map_family": group[0].get("map_family", ""),
                "map_size": group[0].get("map_size", ""),
                "slip": slip,
                "method": method,
                "method_group": group[0].get("method_group", ""),
                "target_count": target,
                "n_states": group[0].get("n_states", ""),
                "n_abstract_states": group[0].get("n_abstract_states", ""),
                "state_compression_ratio": group[0].get("state_compression_ratio", ""),
                "normalized_start_gap": max(finite_float(row.get("normalized_start_gap"), 0.0) for row in group),
                "normalized_policy_start_gap": max(
                    finite_float(row.get("normalized_policy_start_gap"), 0.0) for row in group
                ),
                "value_gap_max": max(finite_float(row.get("value_gap_max"), 0.0) for row in group),
                "policy_value_gap_max": max(
                    finite_float(row.get("policy_value_gap_max"), 0.0) for row in group
                ),
                "homogeneity_error": max(
                    (finite_float(row.get("homogeneity_error")) for row in group),
                    default=float("nan"),
                ),
                "time_q1_sec": q1,
                "time_median_sec": median_total,
                "time_q3_sec": q3,
                "total_speedup_median": float(np.median([finite_float(row.get("total_speedup")) for row in group])),
                "n_repeats": len(group),
                "representation_scope": group[0].get("representation_scope", ""),
            }
        )
    return aggregate


def write_report(
    rows: Sequence[Mapping[str, object]],
    aggregate: Sequence[Mapping[str, object]],
    path: Path,
    args: argparse.Namespace,
) -> None:
    columns = [
        "map",
        "slip",
        "method",
        "target_count",
        "n_abstract_states",
        "state_compression_ratio",
        "normalized_start_gap",
        "normalized_policy_start_gap",
        "homogeneity_error",
        "time_median_sec",
        "total_speedup_median",
        "representation_scope",
    ]
    lines = [
        "# Direct State-Abstraction And Schur Baselines",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"methods = {list(args.methods)}, repeats = {args.repeats}",
        "",
        "The epsilon-homogeneous baseline performs approximate MDP model minimization; the Q*-aggregation "
        "row is a reward-aware oracle abstraction; and policy-Kron is a policy-specific Schur oracle that "
        "does not solve boundary selection or preserve the full action interface. Oracle rows include the "
        "full-state policy/value construction cost in total-time accounting.",
        "",
        f"- raw rows: `{len(rows)}`",
        f"- aggregate rows: `{len(aggregate)}`",
        "",
        markdown_table(aggregate, columns) if aggregate else "_No rows._",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Direct state abstraction and policy-Schur baselines.")
    parser.add_argument(
        "--map-specs",
        nargs="+",
        default=["corridor:16,32", "open_room:7", "four_rooms:7", "maze:9"],
    )
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    parser.add_argument("--budget-fracs", nargs="+", type=float, default=[0.05, 0.1, 0.2, 0.35])
    parser.add_argument("--target-counts", nargs="+", type=int, default=[])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/abstraction_baseline_comparison"),
    )
    args = parser.parse_args()

    if args.num_shards < 1 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("Require 0 <= shard-index < num-shards and num-shards >= 1.")
    contexts = list(parse_map_specs(args.map_specs))
    jobs: List[Tuple[str, str, str, int, int]] = []
    for _family, _size, map_name, map_rows in contexts:
        n_states = GridWorld(map_rows).n_states
        counts = target_counts(n_states, args.budget_fracs, args.target_counts)
        for slip in args.slips:
            for method in args.methods:
                for count in counts:
                    if method == "exact_model_minimization" and count != counts[0]:
                        continue
                    for repeat in range(args.repeats):
                        jobs.append((map_name, f"{slip:.12g}", method, count, repeat))
    selected = {job for index, job in enumerate(jobs) if index % args.num_shards == args.shard_index}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.out_dir / "abstraction_baseline_runs.csv"
    rows: List[Dict[str, object]] = read_existing(raw_path) if args.resume else []
    completed = {
        (
            str(row.get("map", "")),
            f"{finite_float(row.get('slip')):.12g}",
            str(row.get("method", "")),
            int(finite_float(row.get("target_count"), -1.0)),
            int(finite_float(row.get("repeat"), -1.0)),
        )
        for row in rows
        if row.get("map") and row.get("repeat", "") != ""
    }
    for family, size, map_name, map_rows in contexts:
        grid = GridWorld(map_rows)
        goal_state = grid.symbol_states("G")[0]
        for slip in args.slips:
            sparse_model = build_sparse_grid_model(grid, goal_state=goal_state, slip=slip)
            full_started = time.perf_counter()
            full_result = sparse_value_iteration_measured(sparse_model, gamma=args.gamma, tol=args.tol)
            full_time = time.perf_counter() - full_started
            full_value = np.asarray(full_result["V"], dtype=float)
            mdp = gridworld_finite_mdp(grid, goal_state=goal_state, slip=slip)
            exact_partition = epsilon_homogeneous_partition(mdp, epsilon=0.0)
            counts = target_counts(grid.n_states, args.budget_fracs, args.target_counts)
            for method in args.methods:
                for count in counts:
                    if method == "exact_model_minimization" and count != counts[0]:
                        continue
                    for repeat in range(args.repeats):
                        job_key = (map_name, f"{slip:.12g}", method, count, repeat)
                        if job_key not in selected or (args.resume and job_key in completed):
                            continue
                        try:
                            metrics = run_method(
                                method,
                                mdp=mdp,
                                full_value=full_value,
                                gamma=args.gamma,
                                target_count=count,
                            )
                            selection = float(metrics["selection_time_sec"])
                            construction = float(metrics["construction_time_sec"])
                            solve = float(metrics["solve_time_sec"])
                            oracle_full_cost = full_time if "oracle" in method else 0.0
                            total = selection + construction + solve + oracle_full_cost
                            start_gap = float(metrics["start_gap"])
                            policy_start_gap = float(metrics["policy_start_gap"])
                            rows.append(
                                {
                                    "map_family": family,
                                    "map_size": size,
                                    "map": map_name,
                                    "slip": slip,
                                    "method": method,
                                    "method_group": (
                                        "abstraction:model_minimization"
                                        if method in {"exact_model_minimization", "epsilon_homogeneous"}
                                        else "abstraction:qstar_oracle"
                                        if method == "qstar_oracle_aggregation"
                                        else "reduction:policy_kron_oracle"
                                    ),
                                    "representation_scope": (
                                        "full_action_abstract_mdp"
                                        if method != "policy_kron_oracle"
                                        else "fixed_optimal_policy_only"
                                    ),
                                    "repeat": repeat,
                                    "target_count": count,
                                    "n_states": grid.n_states,
                                    "n_abstract_states": metrics["n_abstract_states"],
                                    "state_compression_ratio": metrics["state_compression_ratio"],
                                    "epsilon": metrics.get("epsilon", ""),
                                    "exact_partition_states": len(exact_partition),
                                    "homogeneity_error": metrics["homogeneity_error"],
                                    "start_gap": start_gap,
                                    "normalized_start_gap": normalized_gap(start_gap, full_value),
                                    "value_gap_max": metrics["value_gap_max"],
                                    "policy_start_gap": policy_start_gap,
                                    "normalized_policy_start_gap": normalized_gap(policy_start_gap, full_value),
                                    "policy_value_gap_max": metrics["policy_value_gap_max"],
                                    "full_planner_time_sec": full_time,
                                    "selection_time_sec": selection,
                                    "construction_time_sec": construction,
                                    "solve_time_sec": solve,
                                    "oracle_full_policy_cost_sec": oracle_full_cost,
                                    "total_time_sec": total,
                                    "total_speedup": full_time / max(1e-12, total),
                                    "full_transition_nnz": transition_nnz_proxy(grid, slip),
                                    "abstract_transition_nnz": metrics["abstract_transition_nnz"],
                                    "error": "",
                                }
                            )
                        except Exception as exc:
                            rows.append(
                                {
                                    "map_family": family,
                                    "map_size": size,
                                    "map": map_name,
                                    "slip": slip,
                                    "method": method,
                                    "repeat": repeat,
                                    "target_count": count,
                                    "error": repr(exc),
                                }
                            )
                        write_csv_all_fields(raw_path, rows)

    aggregate = aggregate_rows(rows)
    write_csv_all_fields(raw_path, rows)
    write_csv_all_fields(args.out_dir / "abstraction_baseline_aggregate.csv", aggregate)
    (args.out_dir / "abstraction_baseline_comparison.json").write_text(
        json.dumps({"rows": rows, "aggregate": aggregate}, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, aggregate, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
