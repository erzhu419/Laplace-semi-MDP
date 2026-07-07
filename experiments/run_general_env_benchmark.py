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
    green_occupancy_boundary,
    spectral_boundary,
)


DEFAULT_ENV_SPECS = (
    "toytext:Taxi-v3",
    "toytext:FrozenLake8x8-v1",
    "toytext:CliffWalking-v1",
    "pointmaze:umaze:3",
)

DEFAULT_METHODS = ("endpoints", "betweenness", "spectral", "coverage", "green")


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
    raise ValueError(f"Unknown method: {method}")


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
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def write_summary(path: Path, rows: Sequence[Mapping[str, object]], errors: Sequence[Mapping[str, object]]) -> None:
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
        table = [["env", "method", "target", "B", "compression", "start_gap", "max_gap", "construct_s"]]
        for env, env_rows in sorted(by_env.items()):
            graph_rows = [row for row in env_rows if row.get("method") != "full_vi"]
            best = min(graph_rows, key=lambda row: (float(row["start_value_gap"]), int(row["n_boundary"])))
            table.append(
                [
                    env,
                    str(best["method"]),
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
    if errors:
        lines += ["## Skipped Or Failed Specs", ""]
        table = [["env_spec", "error"]]
        for error in errors:
            table.append([str(error.get("env_spec", "")), str(error.get("error", ""))[:160]])
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
            "start_value_full": float(start_dist @ full_value),
            "start_value_graph": float(start_dist @ full_value),
            "start_value_gap": 0.0,
            "value_gap_mean": 0.0,
            "value_gap_max": 0.0,
            "full_vi_iterations": full_iterations,
            "full_vi_time_sec": full_time,
            "construction_time_sec": 0.0,
            "smdp_eval_time_sec": full_time,
            "kernel_nnz": int((mdp.P != 0.0).sum()),
            "full_transition_nnz": int((mdp.P != 0.0).sum()),
            "n_terminal": len(mdp.terminal_states),
            "n_start_support": int((start_dist > 0.0).sum()),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    for method in args.methods:
        for target in args.target_counts:
            if method == "endpoints" and target != args.target_counts[0]:
                continue
            try:
                construct_started = time.perf_counter()
                boundary = construct_boundary(
                    mdp=mdp,
                    method=method,
                    target_count=int(target),
                    gamma=args.gamma,
                    full_value=full_value,
                )
                construct_time = time.perf_counter() - construct_started
                eval_started = time.perf_counter()
                metrics = evaluate_boundary_graph(mdp, boundary=boundary, gamma=args.gamma, full_value=full_value)
                eval_time = time.perf_counter() - eval_started
                row: Dict[str, object] = {
                    "env_spec": spec,
                    "env": mdp.name,
                    "source": (mdp.metadata or {}).get("source", ""),
                    "method": method,
                    "target_count": int(target),
                    "full_vi_iterations": full_iterations,
                    "full_vi_time_sec": full_time,
                    "construction_time_sec": construct_time,
                    "smdp_eval_time_sec": eval_time,
                    "n_terminal": len(mdp.terminal_states),
                    "n_start_support": int((start_dist > 0.0).sum()),
                    "timestamp": datetime.utcnow().isoformat(),
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
                        "error": repr(exc),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
    return rows, None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run finite-MDP graph abstraction smoke tests on ToyText, MiniGrid, and discretized PointMaze environments."
    )
    parser.add_argument("--env-specs", nargs="+", default=list(DEFAULT_ENV_SPECS))
    parser.add_argument("--methods", nargs="+", default=list(DEFAULT_METHODS))
    parser.add_argument("--target-counts", nargs="+", type=int, default=[8, 16, 32])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-states", type=int, default=50_000)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/general_env_benchmark"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    errors: List[Dict[str, object]] = []
    for spec in args.env_specs:
        env_rows, error = run_env(spec, args)
        rows.extend(env_rows)
        if error is not None:
            errors.append(error)
    write_csv(args.out_dir / "general_env_benchmark.csv", rows)
    write_csv(args.out_dir / "general_env_errors.csv", errors)
    (args.out_dir / "general_env_benchmark.json").write_text(
        json.dumps({"rows": rows, "errors": errors}, indent=2, sort_keys=True)
    )
    write_summary(args.out_dir / "summary.md", rows, errors)


if __name__ == "__main__":
    main()

