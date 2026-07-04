#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import (
    ACTIONS,
    BellmanKronReduction,
    GridWorld,
    all_boundary_states,
    bellman_kron_reduce,
    bellman_preservation_error,
    corridor_map,
    decision_boundary_states,
    default_map,
    edge_table,
    endpoint_boundary_states,
    four_rooms_map,
    junction_boundary_states,
    open_room_map,
    primitive_value_iteration,
    shortest_path_policy_to_target,
    smdp_value_iteration,
    spectral_boundary_states,
    transition_matrix_for_direction,
    transition_matrix_for_policy,
)


SelectorFn = Callable[[GridWorld], List[int]]
ReductionSet = Dict[str, BellmanKronReduction]


MAPS: Mapping[str, Tuple[str, ...]] = {
    "corridor": corridor_map(),
    "open_room": open_room_map(),
    "four_rooms": four_rooms_map(),
    "maze": default_map(),
}

SELECTORS: Mapping[str, SelectorFn] = {
    "all": all_boundary_states,
    "endpoints": endpoint_boundary_states,
    "junction": junction_boundary_states,
    "decision": decision_boundary_states,
    "spectral_25": lambda grid: spectral_boundary_states(grid, fraction=0.25),
}


def build_reductions(
    grid: GridWorld,
    boundary: Sequence[int],
    option_set: str,
    slip: float,
    gamma: float,
) -> Tuple[ReductionSet, Dict[str, np.ndarray], Dict[str, Tuple[np.ndarray, np.ndarray]]]:
    reductions: ReductionSet = {}
    valid_actions: Dict[str, np.ndarray] = {}
    primitive_models: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    n_boundary = len(boundary)

    if option_set == "directional":
        for action in ACTIONS:
            P, r = transition_matrix_for_direction(grid, action, slip=slip)
            reductions[action] = bellman_kron_reduce(P, r, boundary=boundary, gamma=gamma)
            primitive_models[action] = (P, r)
        return reductions, valid_actions, primitive_models

    if option_set == "targeted":
        for target_pos, target_state in enumerate(boundary):
            label = f"to_{target_pos:03d}"
            policy = shortest_path_policy_to_target(grid, target_state, slip=slip)
            P, r = transition_matrix_for_policy(grid, policy, absorbing=[target_state])
            reductions[label] = bellman_kron_reduce(P, r, boundary=boundary, gamma=gamma)
            primitive_models[label] = (P, r)
            valid = np.ones(n_boundary, dtype=bool)
            valid[target_pos] = False
            valid_actions[label] = valid
        return reductions, valid_actions, primitive_models

    raise ValueError(f"Unknown option set: {option_set}")


def count_valid_edges(
    reductions: Mapping[str, BellmanKronReduction],
    valid_actions: Mapping[str, np.ndarray],
    min_hit_probability: float,
) -> int:
    total = 0
    for action, red in reductions.items():
        valid = valid_actions.get(action, np.ones(len(red.boundary), dtype=bool))
        for i, is_valid in enumerate(valid):
            if not is_valid:
                continue
            total += int(np.sum(red.hit_probability[i] > min_hit_probability))
    return total


def nonzero_kernel_entries(
    reductions: Mapping[str, BellmanKronReduction],
    valid_actions: Mapping[str, np.ndarray],
    threshold: float,
) -> int:
    total = 0
    for action, red in reductions.items():
        valid = valid_actions.get(action, np.ones(len(red.boundary), dtype=bool))
        gamma_terminal = red.gamma_terminal.copy()
        gamma_terminal[~valid, :] = 0.0
        total += int(np.sum(np.abs(gamma_terminal) > threshold))
    return total


def preservation_error(
    reductions: Mapping[str, BellmanKronReduction],
    primitive_models: Mapping[str, Tuple[np.ndarray, np.ndarray]],
    rng: np.random.Generator,
) -> float:
    first = next(iter(reductions.values()))
    boundary_values = rng.normal(size=len(first.boundary))
    errors = []
    for action, red in reductions.items():
        P, r = primitive_models[action]
        errors.append(bellman_preservation_error(P, r, red, boundary_values))
    return float(max(errors))


def run_condition(
    map_name: str,
    rows: Tuple[str, ...],
    selector_name: str,
    selector: SelectorFn,
    option_set: str,
    slip: float,
    gamma: float,
    rng: np.random.Generator,
    min_hit_probability: float,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    boundary = selector(grid)
    start = grid.symbol_states("S")[0]
    goal = grid.symbol_states("G")[0]
    boundary_to_pos = {s: i for i, s in enumerate(boundary)}
    if start not in boundary_to_pos or goal not in boundary_to_pos:
        raise ValueError(f"Selector {selector_name} must retain S and G.")

    reductions, valid_actions, primitive_models = build_reductions(
        grid=grid,
        boundary=boundary,
        option_set=option_set,
        slip=slip,
        gamma=gamma,
    )
    bellman_error = preservation_error(reductions, primitive_models, rng)
    V_smdp, policy_smdp = smdp_value_iteration(
        reductions,
        goal_boundary_position=boundary_to_pos[goal],
        valid_actions=valid_actions or None,
    )
    V_full = primitive_value_iteration(grid, goal_state=goal, gamma=gamma, slip=slip)
    boundary_full = V_full[np.array(boundary)]
    value_gap = np.abs(V_smdp - boundary_full)
    all_edges = edge_table(reductions, grid, min_hit_probability=min_hit_probability)

    start_pos = boundary_to_pos[start]
    goal_pos = boundary_to_pos[goal]
    nonterminal = np.ones(len(boundary), dtype=bool)
    nonterminal[goal_pos] = False

    return {
        "map": map_name,
        "slip": slip,
        "selector": selector_name,
        "option_set": option_set,
        "gamma": gamma,
        "n_states": grid.n_states,
        "n_boundary": len(boundary),
        "n_options": len(reductions),
        "compression_ratio": len(boundary) / grid.n_states,
        "n_edges_all": len(all_edges),
        "n_edges_valid": count_valid_edges(reductions, valid_actions, min_hit_probability),
        "kernel_entries_valid": nonzero_kernel_entries(reductions, valid_actions, min_hit_probability),
        "bellman_error_max": bellman_error,
        "value_gap_max": float(value_gap[nonterminal].max()) if np.any(nonterminal) else 0.0,
        "value_gap_mean": float(value_gap[nonterminal].mean()) if np.any(nonterminal) else 0.0,
        "start_value_smdp": float(V_smdp[start_pos]),
        "start_value_primitive": float(V_full[start]),
        "start_gap": float(abs(V_smdp[start_pos] - V_full[start])),
        "start_best_option": policy_smdp[start_pos],
    }


def sort_key(row: Mapping[str, object]) -> Tuple[float, float, int, int]:
    return (
        float(row["start_gap"]),
        float(row["value_gap_max"]),
        int(row["n_boundary"]),
        int(row["n_options"]),
    )


def markdown_table(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for row in rows:
        vals = []
        for col in columns:
            val = row[col]
            if isinstance(val, float):
                if abs(val) < 1e-9:
                    vals.append(f"{val:.1e}")
                else:
                    vals.append(f"{val:.4g}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(rows: Sequence[Dict[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    by_map_slip: Dict[Tuple[str, float], List[Dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_map_slip[(str(row["map"]), float(row["slip"]))].append(row)

    best_rows = []
    for key in sorted(by_map_slip):
        best_rows.append(sorted(by_map_slip[key], key=sort_key)[0])

    compressed = [r for r in rows if int(r["n_boundary"]) < int(r["n_states"])]
    compressed_best = sorted(compressed, key=sort_key)[:16]

    all_boundary = [r for r in rows if r["selector"] == "all" and r["option_set"] == "directional"]
    max_bellman = max(float(r["bellman_error_max"]) for r in rows)
    min_start_gap = min(float(r["start_gap"]) for r in rows)

    lines = [
        "# Bellman-Kron 第一轮 ablation",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"gamma = {args.gamma}, slips = {args.slips}, edge_threshold = {args.min_hit_probability}",
        "",
        "## 读数方式",
        "",
        "`bellman_error_max` 检查固定 boundary/option 后，Schur complement 是否精确保留 Bellman backup；"
        "它应该接近数值零。`start_gap` 和 `value_gap_max` 才是抽象图加 option set 能不能表达原始最优控制的指标。",
        "",
        "## 总体 sanity",
        "",
        f"- 最大 Bellman preservation error: `{max_bellman:.3e}`。",
        f"- 最小 start planning gap: `{min_start_gap:.3e}`。",
        "- `targeted` option set 允许每个 boundary 有一个到目标 boundary 的反馈策略；它能测试“很粗的图 + 很强的 option model”上限，但会把复杂性藏进 option policy。",
        "- `directional` option set 更接近原始 primitive control；如果它在压缩后有 gap，通常说明 option set 不够表达高层最优控制，而不是 reduction 公式错了。",
        "",
        "## 每个地图/噪声下的最佳配置",
        "",
        markdown_table(
            best_rows,
            [
                "map",
                "slip",
                "selector",
                "option_set",
                "n_states",
                "n_boundary",
                "n_options",
                "compression_ratio",
                "start_gap",
                "value_gap_max",
                "bellman_error_max",
            ],
        ),
        "",
        "## 压缩配置里的前沿样例",
        "",
        markdown_table(
            compressed_best,
            [
                "map",
                "slip",
                "selector",
                "option_set",
                "n_states",
                "n_boundary",
                "n_options",
                "n_edges_valid",
                "start_gap",
                "value_gap_max",
            ],
        ),
        "",
        "## all-boundary primitive sanity baseline",
        "",
        markdown_table(
            sorted(all_boundary, key=lambda r: (str(r["map"]), float(r["slip"]))),
            [
                "map",
                "slip",
                "n_states",
                "n_boundary",
                "n_options",
                "start_gap",
                "value_gap_max",
                "bellman_error_max",
            ],
        ),
        "",
        "## 初步解释",
        "",
        "1. Bellman-Kron 本身在所有设置下都是代数精确的；如果 planning gap 出现，优先怀疑 boundary/option 选择，而不是 Schur complement。",
        "2. `endpoints + targeted` 往往会非常强，因为一个 option 可以携带完整的闭环路径策略；这证明 compact graph 可行，但也暴露了必须正则化 option 复杂度。",
        "3. 下一步不该只问“graph 更小吗”，而要问“graph 小了多少、option policy/model 花了多少复杂度、held-out rollout residual 是否仍然小”。",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bellman-Kron boundary/option ablations.")
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05])
    parser.add_argument("--option-sets", nargs="+", default=["directional", "targeted"])
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/ablation"))
    parser.add_argument("--min-hit-probability", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    rows: List[Dict[str, object]] = []
    for map_name, map_rows in MAPS.items():
        for slip in args.slips:
            for selector_name, selector in SELECTORS.items():
                for option_set in args.option_sets:
                    row = run_condition(
                        map_name=map_name,
                        rows=map_rows,
                        selector_name=selector_name,
                        selector=selector,
                        option_set=option_set,
                        slip=slip,
                        gamma=args.gamma,
                        rng=rng,
                        min_hit_probability=args.min_hit_probability,
                    )
                    rows.append(row)
                    print(
                        f"{map_name:10s} slip={slip:.2f} {selector_name:11s} "
                        f"{option_set:10s} B={row['n_boundary']:3d} "
                        f"gap={row['start_gap']:.3e} bellman={row['bellman_error_max']:.3e}"
                    )

    csv_path = args.out_dir / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path = args.out_dir / "results.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    report_path = args.out_dir / "summary.md"
    write_report(rows, report_path, args)
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
