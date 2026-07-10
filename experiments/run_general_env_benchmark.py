#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401

from finite_mdp_adapter import (
    FiniteMDP,
    betweenness_boundary,
    coverage_boundary,
    discretized_point_maze_mdp,
    endpoint_boundary,
    evaluate_boundary_graph,
    finite_mdp_from_gym_toy_text,
    finite_mdp_from_minigrid,
    full_value_iteration,
    green_group_rd_boundary,
    green_occupancy_boundary,
    spectral_boundary,
    taxi_factor_boundary,
    taxi_landmark_modes_boundary,
)


DEFAULT_ENV_SPECS = (
    "toytext:Taxi-v3",
    "toytext:FrozenLake8x8-v1",
    "toytext:CliffWalking-v1",
    "pointmaze:umaze:3",
)

DEFAULT_METHODS = (
    "endpoints",
    "betweenness",
    "spectral",
    "coverage",
    "green",
    "green_group_rd",
    "taxi_factor",
    "taxi_landmark_modes",
)


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed


def median(values: Sequence[float]) -> float:
    finite = sorted(value for value in values if value == value)
    if not finite:
        return float("nan")
    middle = len(finite) // 2
    if len(finite) % 2:
        return finite[middle]
    return 0.5 * (finite[middle - 1] + finite[middle])


def parse_bool(value: object) -> bool | None:
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def aggregate_rows(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, str, str, str], List[Mapping[str, object]]] = {}
    for row in rows:
        if row.get("method") == "full_vi" or row.get("error"):
            continue
        key = (
            str(row.get("env", "")),
            str(row.get("method", "")),
            str(row.get("option_mode", "")),
            str(row.get("target_count", "")),
        )
        groups.setdefault(key, []).append(row)
    aggregate: List[Dict[str, object]] = []
    for (env, method, option_mode, target), group in sorted(groups.items()):
        feasibility = [
            parsed
            for parsed in (parse_bool(row.get("group_all_feasible")) for row in group)
            if parsed is not None
        ]
        aggregate.append(
            {
                "env": env,
                "source": group[0].get("source", ""),
                "method": method,
                "option_mode": option_mode,
                "target_count": target,
                "n_seeds": len({str(row.get("seed", "")) for row in group}),
                "median_n_boundary": median([finite_float(row.get("n_boundary")) for row in group]),
                "median_state_compression_ratio": median(
                    [finite_float(row.get("state_compression_ratio")) for row in group]
                ),
                "median_normalized_start_gap": median(
                    [finite_float(row.get("normalized_start_value_gap")) for row in group]
                ),
                "max_normalized_start_gap": max(
                    [finite_float(row.get("normalized_start_value_gap"), 0.0) for row in group],
                    default=float("nan"),
                ),
                "median_normalized_value_gap_max": median(
                    [finite_float(row.get("normalized_value_gap_max")) for row in group]
                ),
                "group_feasible_rate": (
                    sum(1 for value in feasibility if value) / len(feasibility)
                    if feasibility
                    else float("nan")
                ),
                "median_construction_time_sec": median(
                    [finite_float(row.get("construction_time_sec")) for row in group]
                ),
                "median_smdp_eval_time_sec": median(
                    [finite_float(row.get("smdp_eval_time_sec")) for row in group]
                ),
            }
        )
    return aggregate


def load_env_from_spec(spec: str, seed: int, max_states: int) -> FiniteMDP:
    parts = spec.split(":")
    kind = parts[0]
    if kind == "toytext":
        if len(parts) != 2:
            raise ValueError("ToyText spec must be toytext:<env_id>.")
        return finite_mdp_from_gym_toy_text(parts[1], seed=seed)
    if kind == "minigrid":
        if len(parts) != 2:
            raise ValueError("MiniGrid spec must be minigrid:<env_id>.")
        return finite_mdp_from_minigrid(parts[1], seed=seed, max_states=max_states)
    if kind == "pointmaze":
        layout = parts[1] if len(parts) >= 2 else "umaze"
        bins = int(parts[2]) if len(parts) >= 3 else 3
        return discretized_point_maze_mdp(layout=layout, bins_per_cell=bins, seed=seed)
    raise ValueError(f"Unknown env spec kind: {kind}.")


def construct_boundary(
    mdp: FiniteMDP,
    method: str,
    target_count: int,
    gamma: float,
    full_value,
) -> List[int]:
    target_count = max(target_count, len(endpoint_boundary(mdp)))
    target_count = min(target_count, mdp.n_states)
    if method == "endpoints":
        return endpoint_boundary(mdp)
    if method == "betweenness":
        return betweenness_boundary(mdp, target_count=target_count)
    if method == "spectral":
        return spectral_boundary(mdp, target_count=target_count)
    if method == "coverage":
        return coverage_boundary(mdp, target_count=target_count)
    if method == "green":
        return green_occupancy_boundary(
            mdp,
            target_count=target_count,
            gamma=gamma,
            V=full_value,
            saliency_kind="combined",
        )
    if method == "green_group_rd":
        boundary, _diagnostics = green_group_rd_boundary(
            mdp,
            target_count=target_count,
            gamma=gamma,
            value=full_value,
        )
        return boundary
    if method == "taxi_factor":
        return taxi_factor_boundary(mdp)
    if method == "taxi_landmark_modes":
        return taxi_landmark_modes_boundary(mdp)
    raise ValueError(f"Unknown method: {method}")


def method_applicable(mdp: FiniteMDP, method: str) -> bool:
    if method in {"taxi_factor", "taxi_landmark_modes"}:
        return mdp.name.startswith("Taxi") and mdp.n_states == 500
    return True


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        path.write_text("")
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def read_existing(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_summary(
    path: Path,
    rows: Sequence[Mapping[str, object]],
    aggregate: Sequence[Mapping[str, object]],
    errors: Sequence[Mapping[str, object]],
) -> None:
    lines = [
        "# General Environment Benchmark",
        "",
        "This smoke benchmark tests the finite-MDP adapter on non-handwritten-grid environments.",
        "The PointMaze rows are discretized empirical MDPs; theoretical claims apply to the discretized model.",
        "",
        f"- rows: {len(rows)}",
        f"- errors: {len(errors)}",
        "",
    ]
    if rows:
        by_env: Dict[str, List[Mapping[str, object]]] = {}
        for row in rows:
            by_env.setdefault(str(row["env"]), []).append(row)
        lines += ["## Best Rows By Env", ""]
        table = [["env", "method", "options", "target", "B", "compression", "start_gap", "max_gap", "construct_s"]]
        for env, env_rows in sorted(by_env.items()):
            graph_rows = [
                row
                for row in env_rows
                if row.get("method") != "full_vi" and not row.get("error") and "start_value_gap" in row
            ]
            if not graph_rows:
                continue
            best = min(graph_rows, key=lambda row: (float(row["start_value_gap"]), int(row["n_boundary"])))
            table.append(
                [
                    env,
                    str(best["method"]),
                    str(best.get("option_mode", "")),
                    str(best["target_count"]),
                    str(best["n_boundary"]),
                    f"{float(best['state_compression_ratio']):.2f}",
                    f"{float(best['start_value_gap']):.6g}",
                    f"{float(best['value_gap_max']):.6g}",
                    f"{float(best['construction_time_sec']):.4f}",
                ]
            )
        lines += markdown_table(table)
        lines.append("")
    if aggregate:
        lines += ["## Multi-Seed Aggregate", ""]
        columns = [
            "env",
            "method",
            "option_mode",
            "target_count",
            "n_seeds",
            "median_n_boundary",
            "median_state_compression_ratio",
            "median_normalized_start_gap",
            "max_normalized_start_gap",
            "median_normalized_value_gap_max",
            "group_feasible_rate",
            "median_construction_time_sec",
            "median_smdp_eval_time_sec",
        ]
        lines += markdown_table(
            [[str(row.get(column, "")) for column in columns] for row in [{column: column for column in columns}, *aggregate]]
        )
        lines.append("")
    if errors:
        lines += ["## Skipped Or Failed Specs", ""]
        table = [["env_spec", "method", "options", "target", "error"]]
        for error in errors:
            table.append(
                [
                    str(error.get("env_spec", "")),
                    str(error.get("method", "")),
                    str(error.get("option_mode", "")),
                    str(error.get("target_count", "")),
                    str(error.get("error", ""))[:160],
                ]
            )
        lines += markdown_table(table)
        lines.append("")
    path.write_text("\n".join(lines) + "\n")


def markdown_table(rows: Sequence[Sequence[str]]) -> List[str]:
    if not rows:
        return []
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    out = []
    out.append("| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(rows[0])) + " |")
    out.append("| " + " | ".join("-" * widths[i] for i in range(len(widths))) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)) + " |")
    return out


def run_env(spec: str, args: argparse.Namespace) -> Tuple[List[Dict[str, object]], Dict[str, object] | None]:
    try:
        mdp = load_env_from_spec(spec, seed=args.seed, max_states=args.max_states)
    except Exception as exc:
        return [], {"env_spec": spec, "error": repr(exc)}

    rows: List[Dict[str, object]] = []
    full_started = time.perf_counter()
    full_value, full_iterations = full_value_iteration(mdp, gamma=args.gamma, tol=args.tol)
    full_time = time.perf_counter() - full_started
    start_dist = mdp.start_distribution_or_uniform()
    start_value_full = float(start_dist @ full_value)
    value_scale = max(1.0, abs(start_value_full), max((abs(float(value)) for value in full_value), default=1.0))
    rows.append(
        {
            "env_spec": spec,
            "env": mdp.name,
            "source": (mdp.metadata or {}).get("source", ""),
            "method": "full_vi",
            "target_count": mdp.n_states,
            "n_states": mdp.n_states,
            "n_actions": mdp.n_actions,
            "n_boundary": mdp.n_states,
            "state_compression_ratio": 1.0,
            "start_value_full": start_value_full,
            "start_value_graph": start_value_full,
            "value_scale": value_scale,
            "start_value_gap": 0.0,
            "normalized_start_value_gap": 0.0,
            "value_gap_mean": 0.0,
            "value_gap_max": 0.0,
            "normalized_value_gap_max": 0.0,
            "full_vi_iterations": full_iterations,
            "full_vi_time_sec": full_time,
            "construction_time_sec": 0.0,
            "smdp_eval_time_sec": full_time,
            "kernel_nnz": int((mdp.P != 0.0).sum()),
            "n_options": mdp.n_actions,
            "option_mode": "full_mdp",
            "full_transition_nnz": int((mdp.P != 0.0).sum()),
            "n_terminal": len(mdp.terminal_states),
            "n_start_support": int((start_dist > 0.0).sum()),
            "timestamp": datetime.utcnow().isoformat(),
            "seed": args.current_seed,
        }
    )

    for method in args.methods:
        if not method_applicable(mdp, method):
            continue
        for target in args.target_counts:
            if method == "endpoints" and target != args.target_counts[0]:
                continue
            if method in {"taxi_factor", "taxi_landmark_modes"} and target != args.target_counts[0]:
                continue
            for option_mode in args.option_modes:
                try:
                    construct_started = time.perf_counter()
                    constructor_diagnostics: Dict[str, object] = {}
                    if method == "green_group_rd":
                        boundary, constructor_diagnostics = green_group_rd_boundary(
                            mdp,
                            target_count=int(target),
                            gamma=args.gamma,
                            value=full_value,
                            budget_frac=args.group_budget_frac,
                            truncation_steps=args.green_truncation_steps,
                            tail_tol=args.green_tail_tol,
                        )
                    else:
                        boundary = construct_boundary(
                            mdp=mdp,
                            method=method,
                            target_count=int(target),
                            gamma=args.gamma,
                            full_value=full_value,
                        )
                    construct_time = time.perf_counter() - construct_started
                    eval_started = time.perf_counter()
                    metrics = evaluate_boundary_graph(
                        mdp,
                        boundary=boundary,
                        gamma=args.gamma,
                        full_value=full_value,
                        option_mode=option_mode,
                    )
                    eval_time = time.perf_counter() - eval_started
                    row: Dict[str, object] = {
                        "env_spec": spec,
                        "env": mdp.name,
                        "source": (mdp.metadata or {}).get("source", ""),
                        "method": method,
                        "target_count": int(target),
                        "option_mode": option_mode,
                        "full_vi_iterations": full_iterations,
                        "full_vi_time_sec": full_time,
                        "construction_time_sec": construct_time,
                        "smdp_eval_time_sec": eval_time,
                        "n_terminal": len(mdp.terminal_states),
                        "n_start_support": int((start_dist > 0.0).sum()),
                        "timestamp": datetime.utcnow().isoformat(),
                        "seed": args.current_seed,
                        "group_all_feasible": constructor_diagnostics.get("group_all_feasible", ""),
                        "group_total_violation": constructor_diagnostics.get("group_total_violation", ""),
                        "group_initial_risks": json.dumps(
                            constructor_diagnostics.get("initial_group_risks", {}), sort_keys=True
                        ),
                        "group_final_risks": json.dumps(
                            constructor_diagnostics.get("final_group_risks", {}), sort_keys=True
                        ),
                    }
                    row.update(metrics)
                    rows.append(row)
                except Exception as exc:
                    rows.append(
                        {
                            "env_spec": spec,
                            "env": mdp.name,
                            "source": (mdp.metadata or {}).get("source", ""),
                            "method": method,
                            "target_count": int(target),
                            "option_mode": option_mode,
                            "error": repr(exc),
                            "timestamp": datetime.utcnow().isoformat(),
                            "seed": args.current_seed,
                        }
                    )
    return rows, None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run finite-MDP graph abstraction smoke tests on ToyText, MiniGrid, and discretized PointMaze environments."
    )
    parser.add_argument("--env-specs", nargs="+", default=list(DEFAULT_ENV_SPECS))
    parser.add_argument("--methods", nargs="+", default=list(DEFAULT_METHODS))
    parser.add_argument("--option-modes", nargs="+", default=["primitive"])
    parser.add_argument("--target-counts", nargs="+", type=int, default=[8, 16, 32])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--group-budget-frac", type=float, default=0.25)
    parser.add_argument("--green-truncation-steps", type=int, default=128)
    parser.add_argument("--green-tail-tol", type=float, default=1e-9)
    parser.add_argument("--max-states", type=int, default=50_000)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/general_env_benchmark"))
    args = parser.parse_args()

    if args.num_shards < 1 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("Require 0 <= shard-index < num-shards and num-shards >= 1.")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.out_dir / "general_env_benchmark.csv"
    rows: List[Dict[str, object]] = read_existing(raw_path) if args.resume else []
    errors: List[Dict[str, object]] = []
    seeds = list(args.seeds if args.seeds is not None else [args.seed])
    jobs = [(int(seed), spec) for seed in seeds for spec in args.env_specs]
    selected = [job for index, job in enumerate(jobs) if index % args.num_shards == args.shard_index]
    completed = {
        (int(float(row.get("seed", -1))), str(row.get("env_spec", "")))
        for row in rows
        if row.get("method") == "full_vi" and row.get("seed", "") != ""
    }
    progress_path = args.out_dir / "progress.jsonl"
    for seed, spec in selected:
        if args.resume and (seed, spec) in completed:
            continue
        args.current_seed = int(seed)
        args.seed = int(seed)
        env_rows, error = run_env(spec, args)
        rows.extend(env_rows)
        if error is not None:
            error = {**error, "seed": seed}
            errors.append(error)
        write_csv(raw_path, rows)
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "seed": seed,
                        "env_spec": spec,
                        "rows_added": len(env_rows),
                        "error": error.get("error", "") if error else "",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    row_errors = [
        {
            "env_spec": row.get("env_spec", ""),
            "env": row.get("env", ""),
            "method": row.get("method", ""),
            "option_mode": row.get("option_mode", ""),
            "target_count": row.get("target_count", ""),
            "error": row.get("error", ""),
        }
        for row in rows
        if row.get("error")
    ]
    all_errors = list(errors) + row_errors
    aggregate = aggregate_rows(rows)
    write_csv(raw_path, rows)
    write_csv(args.out_dir / "general_env_aggregate.csv", aggregate)
    write_csv(args.out_dir / "general_env_errors.csv", all_errors)
    (args.out_dir / "general_env_benchmark.json").write_text(
        json.dumps({"rows": rows, "errors": all_errors}, indent=2, sort_keys=True)
    )
    write_summary(args.out_dir / "summary.md", rows, aggregate, all_errors)


if __name__ == "__main__":
    main()
