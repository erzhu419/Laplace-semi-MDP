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
    constant_policy,
    corridor_map,
    critical_saliency,
    decision_boundary_states,
    default_map,
    edge_table,
    endpoint_boundary_states,
    expected_discounted_interior_cost,
    four_rooms_map,
    junction_boundary_states,
    open_room_map,
    policy_complexity,
    primitive_value_iteration,
    shortest_path_distance_matrix,
    shortest_path_policy_to_target,
    smdp_value_iteration,
    spectral_boundary_states,
    transition_matrix_for_direction,
    transition_matrix_for_policy,
)


SelectorFn = Callable[[GridWorld], List[int]]
ReductionSet = Dict[str, BellmanKronReduction]
PolicySet = Dict[str, Callable[[int], Mapping[str, float]]]


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
    local_horizon: float,
) -> Tuple[ReductionSet, Dict[str, np.ndarray], Dict[str, Tuple[np.ndarray, np.ndarray]], PolicySet, Dict[str, object]]:
    reductions: ReductionSet = {}
    valid_actions: Dict[str, np.ndarray] = {}
    primitive_models: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    policies: PolicySet = {}
    option_metadata: Dict[str, object] = {"option_set": option_set, "local_horizon": local_horizon}
    n_boundary = len(boundary)

    if option_set == "directional":
        for action in ACTIONS:
            policy = constant_policy(action, slip=slip)
            P, r = transition_matrix_for_direction(grid, action, slip=slip)
            reductions[action] = bellman_kron_reduce(P, r, boundary=boundary, gamma=gamma)
            primitive_models[action] = (P, r)
            policies[action] = policy
        option_metadata["option_pair_count"] = len(ACTIONS) * n_boundary
        return reductions, valid_actions, primitive_models, policies, option_metadata

    if option_set in {"targeted", "global_targeted", "local_targeted"}:
        distances = shortest_path_distance_matrix(grid)
        pair_count = 0
        for target_pos, target_state in enumerate(boundary):
            label = f"to_{target_pos:03d}"
            policy = shortest_path_policy_to_target(grid, target_state, slip=slip)
            P, r = transition_matrix_for_policy(grid, policy, absorbing=[target_state])
            reductions[label] = bellman_kron_reduce(P, r, boundary=boundary, gamma=gamma)
            primitive_models[label] = (P, r)
            policies[label] = policy
            valid = np.ones(n_boundary, dtype=bool)
            valid[target_pos] = False
            if option_set == "local_targeted":
                for src_pos, src_state in enumerate(boundary):
                    if distances[src_state, target_state] > local_horizon:
                        valid[src_pos] = False
            valid_actions[label] = valid
            pair_count += int(np.sum(valid))
        option_metadata["option_pair_count"] = pair_count
        return reductions, valid_actions, primitive_models, policies, option_metadata

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


def valid_source_mask(action: str, red: BellmanKronReduction, valid_actions: Mapping[str, np.ndarray]) -> np.ndarray:
    return valid_actions.get(action, np.ones(len(red.boundary), dtype=bool))


def reduction_duration_stats(
    reductions: Mapping[str, BellmanKronReduction],
    valid_actions: Mapping[str, np.ndarray],
) -> Tuple[float, float]:
    values: List[float] = []
    for action, red in reductions.items():
        valid = valid_source_mask(action, red, valid_actions)
        tau = np.nan_to_num(red.expected_tau, nan=0.0, posinf=0.0)
        row_tau = np.sum(red.hit_probability * tau, axis=1)
        values.extend(float(v) for v in row_tau[valid])
    if not values:
        return 0.0, 0.0
    arr = np.array(values, dtype=float)
    return float(arr.mean()), float(arr.max())


def bypass_stats(
    boundary: Sequence[int],
    reductions: Mapping[str, BellmanKronReduction],
    primitive_models: Mapping[str, Tuple[np.ndarray, np.ndarray]],
    valid_actions: Mapping[str, np.ndarray],
    gamma: float,
    state_cost: np.ndarray,
) -> Tuple[float, float]:
    state_cost = state_cost.copy()
    state_cost[np.array(boundary, dtype=int)] = 0.0
    values: List[float] = []
    for action, red in reductions.items():
        P, _ = primitive_models[action]
        valid = valid_source_mask(action, red, valid_actions)
        cost = expected_discounted_interior_cost(P, boundary, gamma, state_cost)
        values.extend(float(v) for v in cost[valid])
    if not values:
        return 0.0, 0.0
    arr = np.array(values, dtype=float)
    return float(arr.mean()), float(arr.sum())


def policy_complexity_stats(grid: GridWorld, policies: Mapping[str, Callable[[int], Mapping[str, float]]]) -> Dict[str, float]:
    if not policies:
        return {"policy_tv_total": 0.0, "policy_regions_total": 0.0, "policy_tv_mean": 0.0, "policy_regions_mean": 0.0}
    tvs = []
    regions = []
    for policy in policies.values():
        metrics = policy_complexity(grid, policy)
        tvs.append(metrics["policy_tv"])
        regions.append(metrics["policy_regions"])
    tv_arr = np.array(tvs, dtype=float)
    region_arr = np.array(regions, dtype=float)
    return {
        "policy_tv_total": float(tv_arr.sum()),
        "policy_regions_total": float(region_arr.sum()),
        "policy_tv_mean": float(tv_arr.mean()),
        "policy_regions_mean": float(region_arr.mean()),
    }


def nonlocal_reachability_cost(
    grid: GridWorld,
    reductions: Mapping[str, BellmanKronReduction],
    valid_actions: Mapping[str, np.ndarray],
    local_horizon: float,
) -> float:
    distances = shortest_path_distance_matrix(grid)
    total = 0.0
    for action, red in reductions.items():
        valid = valid_source_mask(action, red, valid_actions)
        for i, src in enumerate(red.boundary):
            if not valid[i]:
                continue
            for j, dst in enumerate(red.boundary):
                excess = max(0.0, float(distances[int(src), int(dst)]) - local_horizon)
                total += float(red.hit_probability[i, j]) * excess
    return total


def description_length_proxy(row: Mapping[str, object]) -> float:
    graph_cost = float(row["n_boundary"]) + float(row["n_edges_valid"]) / max(1.0, float(row["n_boundary"]))
    option_cost = (
        float(row["n_options"])
        + 0.05 * float(row["option_pair_count"])
        + 0.20 * float(row["policy_tv_total"])
        + 0.50 * float(row["policy_regions_total"])
    )
    hidden_cost = float(row["bypass_cost_total"]) + 0.10 * float(row["nonlocal_cost"])
    return graph_cost + option_cost + hidden_cost


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
    local_horizon: float,
    critical_kind: str,
    critical_top_fraction: float,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    boundary = selector(grid)
    start = grid.symbol_states("S")[0]
    goal = grid.symbol_states("G")[0]
    boundary_to_pos = {s: i for i, s in enumerate(boundary)}
    if start not in boundary_to_pos or goal not in boundary_to_pos:
        raise ValueError(f"Selector {selector_name} must retain S and G.")

    reductions, valid_actions, primitive_models, policies, option_metadata = build_reductions(
        grid=grid,
        boundary=boundary,
        option_set=option_set,
        slip=slip,
        gamma=gamma,
        local_horizon=local_horizon,
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
    duration_mean, duration_max = reduction_duration_stats(reductions, valid_actions)
    state_cost = critical_saliency(
        grid,
        kind=critical_kind,
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=critical_top_fraction,
    )
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

    row = {
        "map": map_name,
        "slip": slip,
        "selector": selector_name,
        "option_set": option_set,
        "gamma": gamma,
        "n_states": grid.n_states,
        "n_boundary": len(boundary),
        "n_options": len(reductions),
        "option_pair_count": int(option_metadata["option_pair_count"]),
        "compression_ratio": len(boundary) / grid.n_states,
        "n_edges_all": len(all_edges),
        "n_edges_valid": count_valid_edges(reductions, valid_actions, min_hit_probability),
        "kernel_entries_valid": nonzero_kernel_entries(reductions, valid_actions, min_hit_probability),
        "critical_kind": critical_kind,
        "critical_top_fraction": critical_top_fraction,
        "critical_nonzero": int(np.sum(state_cost > 1e-12)),
        "critical_mass": float(state_cost.sum()),
        "duration_mean": duration_mean,
        "duration_max": duration_max,
        "bypass_cost_mean": bypass_mean,
        "bypass_cost_total": bypass_total,
        "nonlocal_cost": nonlocal_cost,
        "bellman_error_max": bellman_error,
        "value_gap_max": float(value_gap[nonterminal].max()) if np.any(nonterminal) else 0.0,
        "value_gap_mean": float(value_gap[nonterminal].mean()) if np.any(nonterminal) else 0.0,
        "start_value_smdp": float(V_smdp[start_pos]),
        "start_value_primitive": float(V_full[start]),
        "start_gap": float(abs(V_smdp[start_pos] - V_full[start])),
        "start_best_option": policy_smdp[start_pos],
    }
    row.update(policy_metrics)
    row["description_length_proxy"] = description_length_proxy(row)
    return row


def sort_key(row: Mapping[str, object]) -> Tuple[float, float, int, int]:
    return (
        float(row["start_gap"]),
        float(row["value_gap_max"]),
        int(row["n_boundary"]),
        int(row["n_options"]),
    )


def complexity_key(row: Mapping[str, object]) -> Tuple[float, float, float]:
    return (
        float(row["description_length_proxy"]),
        float(row["start_gap"]),
        float(row["value_gap_max"]),
    )


def pareto_front(rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    front: List[Dict[str, object]] = []
    ordered = sorted(rows, key=lambda r: (float(r["description_length_proxy"]), float(r["start_gap"])))
    best_gap = float("inf")
    for row in ordered:
        gap = float(row["start_gap"])
        if gap < best_gap - 1e-10:
            front.append(row)
            best_gap = gap
    return front


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
    compressed_complexity_best = sorted(compressed, key=complexity_key)[:16]
    low_gap = [r for r in rows if float(r["start_gap"]) <= args.good_gap_threshold]
    low_gap_complexity_best = sorted(low_gap, key=complexity_key)[:16]
    non_corridor_low_gap = [r for r in low_gap if r["map"] != "corridor"]
    non_corridor_low_gap_best = sorted(non_corridor_low_gap, key=complexity_key)[:16]
    endpoint_targeted = [
        r for r in rows if r["selector"] == "endpoints" and r["option_set"] == "targeted"
    ]
    front = pareto_front(rows)[:20]

    all_boundary = [r for r in rows if r["selector"] == "all" and r["option_set"] == "directional"]
    max_bellman = max(float(r["bellman_error_max"]) for r in rows)
    min_start_gap = min(float(r["start_gap"]) for r in rows)

    lines = [
        "# Bellman-Kron 第一轮 ablation",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"gamma = {args.gamma}, slips = {args.slips}, edge_threshold = {args.min_hit_probability}",
        f"local_horizon = {args.local_horizon}, good_gap_threshold = {args.good_gap_threshold}",
        f"critical_kind = {getattr(args, 'critical_kind', 'decision')}, critical_top_fraction = {getattr(args, 'critical_top_fraction', 0.15)}",
        "",
        "## 读数方式",
        "",
        "`bellman_error_max` 检查固定 boundary/option 后，Schur complement 是否精确保留 Bellman backup；"
        "它应该接近数值零。`start_gap` 和 `value_gap_max` 才是抽象图加 option set 能不能表达原始最优控制的指标。",
        "`bypass_cost_*` 用 decision boundary 作为 hidden critical set，惩罚 option 穿过本该暴露给高层 planner 的状态；"
        "`policy_tv_total` 和 `policy_regions_total` 粗略惩罚 option 内部策略表的复杂度。",
        "`description_length_proxy` 只是当前工作假设：`|B| + edges/|B| + |O| + 0.05*pairs + 0.20*policy_tv + 0.50*regions + bypass + 0.10*nonlocal`。",
        "",
        "## 总体 sanity",
        "",
        f"- 最大 Bellman preservation error: `{max_bellman:.3e}`。",
        f"- 最小 start planning gap: `{min_start_gap:.3e}`。",
        "- `targeted` option set 允许每个 boundary 有一个到目标 boundary 的反馈策略；它能测试“很粗的图 + 很强的 option model”上限，但会把复杂性藏进 option policy。",
        "- `local_targeted` 只允许 primitive distance 不超过 `local_horizon` 的 target option；不满足局部连通性的配置会被跳过。",
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
                "description_length_proxy",
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
                "critical_nonzero",
                "start_gap",
                "value_gap_max",
                "bypass_cost_total",
            ],
        ),
        "",
        "## 低复杂度配置",
        "",
        markdown_table(
            compressed_complexity_best,
            [
                "map",
                "slip",
                "selector",
                "option_set",
                "n_boundary",
                "n_options",
                "option_pair_count",
                "start_gap",
                "description_length_proxy",
                "bypass_cost_total",
                "policy_tv_total",
                "policy_regions_total",
            ],
        ),
        "",
        f"## start gap <= {args.good_gap_threshold} 的低复杂度候选",
        "",
        markdown_table(
            low_gap_complexity_best,
            [
                "map",
                "slip",
                "selector",
                "option_set",
                "n_boundary",
                "n_options",
                "start_gap",
                "description_length_proxy",
                "bypass_cost_total",
                "policy_tv_total",
            ],
        ),
        "",
        f"## 非 corridor 且 start gap <= {args.good_gap_threshold} 的候选",
        "",
        markdown_table(
            non_corridor_low_gap_best,
            [
                "map",
                "slip",
                "selector",
                "option_set",
                "n_boundary",
                "n_options",
                "start_gap",
                "description_length_proxy",
                "bypass_cost_total",
                "policy_tv_total",
            ],
        ),
        "",
        "## endpoints + targeted 退化解探针",
        "",
        markdown_table(
            sorted(endpoint_targeted, key=lambda r: (str(r["map"]), float(r["slip"]))),
            [
                "map",
                "slip",
                "start_gap",
                "description_length_proxy",
                "bypass_cost_total",
                "policy_tv_total",
                "policy_regions_total",
            ],
        ),
        "",
        "## 全配置 Pareto front 近似",
        "",
        markdown_table(
            front,
            [
                "map",
                "slip",
                "selector",
                "option_set",
                "n_boundary",
                "n_options",
                "start_gap",
                "description_length_proxy",
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
        "3. complexity-aware 指标会把“图很小但 option 跨过大量 decision states”的方案显式标出来；这一步不是最终 objective，而是防止退化解的第一根尺子。",
        "4. 下一步不该只问“graph 更小吗”，而要问“graph 小了多少、option policy/model 花了多少复杂度、held-out rollout residual 是否仍然小”。",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bellman-Kron boundary/option ablations.")
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05])
    parser.add_argument("--option-sets", nargs="+", default=["directional", "targeted", "local_targeted"])
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/ablation"))
    parser.add_argument("--min-hit-probability", type=float, default=1e-5)
    parser.add_argument("--local-horizon", type=float, default=8.0)
    parser.add_argument("--good-gap-threshold", type=float, default=0.2)
    parser.add_argument(
        "--critical-kind",
        choices=["none", "decision", "bottleneck", "betweenness", "value_gradient", "transition_entropy", "combined"],
        default="decision",
    )
    parser.add_argument("--critical-top-fraction", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    rows: List[Dict[str, object]] = []
    for map_name, map_rows in MAPS.items():
        for slip in args.slips:
            for selector_name, selector in SELECTORS.items():
                for option_set in args.option_sets:
                    try:
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
                            local_horizon=args.local_horizon,
                            critical_kind=args.critical_kind,
                            critical_top_fraction=args.critical_top_fraction,
                        )
                    except ValueError as exc:
                        print(f"skip {map_name:10s} slip={slip:.2f} {selector_name:11s} {option_set:14s}: {exc}")
                        continue
                    rows.append(row)
                    print(
                        f"{map_name:10s} slip={slip:.2f} {selector_name:11s} "
                        f"{option_set:14s} B={row['n_boundary']:3d} "
                        f"gap={row['start_gap']:.3e} dl={row['description_length_proxy']:.2f} "
                        f"bypass={row['bypass_cost_total']:.2f} bellman={row['bellman_error_max']:.3e}"
                    )

    if not rows:
        raise RuntimeError("No successful ablation rows were produced.")

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
