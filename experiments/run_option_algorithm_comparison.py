#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import zlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import networkx as nx
import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import (
    ACTIONS,
    GridWorld,
    endpoint_boundary_states,
    graph_adjacency,
    graph_nx,
    shortest_path_policy_to_target,
)
from run_first_boundary_targeted import (
    MAPS,
    candidate_boundary_states,
    critical_saliency,
    evaluate_boundary,
    markdown_table,
)
from run_graph_baseline_comparison import (
    coverage_boundary_states,
    eigenoption_terminal_boundary_states,
    learned_boundary,
)
from one_shot_rd_operator import apply_one_shot_rd_operator


DEFAULT_METHODS = (
    "endpoints",
    "eigenoptions_12",
    "betweenness_12",
    "random_landmarks_12",
    "coverage_12",
    "graph_rd_one_shot",
    "graph_rd_joint",
    "turn_articulation",
)


def parse_count_suffix(method: str) -> int:
    try:
        return int(method.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Method must end with a count suffix: {method}") from exc


def stable_method_seed(seed: int, method: str, map_name: str, slip: float) -> int:
    payload = f"{seed}:{method}:{map_name}:{slip:.6f}".encode("utf-8")
    return int(zlib.crc32(payload) & 0xFFFFFFFF)


def betweenness_boundary_states(grid: GridWorld, target_count: int, keep_symbols: str = "SG") -> List[int]:
    boundary = set(grid.symbol_states(keep_symbols))
    if len(boundary) >= target_count:
        return sorted(boundary)

    graph = graph_nx(grid)
    scores = nx.betweenness_centrality(graph, normalized=True)
    ranked = sorted(range(grid.n_states), key=lambda state: (-float(scores.get(state, 0.0)), state))
    for state in ranked:
        boundary.add(int(state))
        if len(boundary) >= target_count:
            break
    return sorted(boundary)


def random_landmark_boundary_states(
    grid: GridWorld,
    target_count: int,
    rng: np.random.Generator,
    keep_symbols: str = "SG",
) -> List[int]:
    boundary = set(grid.symbol_states(keep_symbols))
    if len(boundary) >= target_count:
        return sorted(boundary)

    candidates = np.array([state for state in range(grid.n_states) if state not in boundary], dtype=int)
    rng.shuffle(candidates)
    for state in candidates.tolist():
        boundary.add(int(state))
        if len(boundary) >= target_count:
            break
    return sorted(boundary)


def method_family(method: str) -> str:
    if method.startswith(("eigenoptions_", "laplacian_eigenoptions_")):
        return "option_algorithm:laplacian_eigenoptions"
    if method.startswith("betweenness_"):
        return "option_algorithm:bottleneck_betweenness"
    if method.startswith("random_landmarks_"):
        return "option_algorithm:random_landmarks"
    if method.startswith("coverage_"):
        return "option_algorithm:topological_coverage"
    if method.startswith("graph_rd_surrogate"):
        return "ours:rd_surrogate_graph"
    if method == "graph_rd_one_shot":
        return "ours:rd_one_shot_graph"
    if method.startswith("graph_rd_"):
        return "ours:rd_graph"
    if method in {"turn_articulation", "decision", "junction"}:
        return "diagnostic:dense_graph"
    return "diagnostic:small_graph"


def construct_boundary(
    method: str,
    map_name: str,
    rows: Tuple[str, ...],
    grid: GridWorld,
    slip: float,
    gamma: float,
    max_splits: int,
    seed: int,
) -> Tuple[List[int], Dict[str, object]]:
    constructor: Dict[str, object] = {"constructor_method": method}
    if method == "endpoints":
        return endpoint_boundary_states(grid), constructor
    if method in {"junction", "decision", "turn_articulation", "articulation_only"}:
        goal = grid.symbol_states("G")[0]
        return (
            candidate_boundary_states(
                grid,
                kind=method,
                goal_state=goal,
                gamma=gamma,
                slip=slip,
                top_fraction=0.15,
            ),
            constructor,
        )
    if method.startswith(("eigenoptions_", "laplacian_eigenoptions_")):
        return eigenoption_terminal_boundary_states(grid, target_count=parse_count_suffix(method)), constructor
    if method.startswith("betweenness_"):
        return betweenness_boundary_states(grid, target_count=parse_count_suffix(method)), constructor
    if method.startswith("random_landmarks_"):
        rng = np.random.default_rng(stable_method_seed(seed, method, map_name, slip))
        return random_landmark_boundary_states(grid, target_count=parse_count_suffix(method), rng=rng), constructor
    if method.startswith("coverage_"):
        return coverage_boundary_states(grid, target_count=parse_count_suffix(method)), constructor
    if method == "graph_rd_one_shot":
        result = apply_one_shot_rd_operator(
            grid=grid,
            slip=slip,
            gamma=gamma,
            mandatory_boundary=endpoint_boundary_states(grid),
            truncation_steps=256,
            tail_tol=1e-6,
            max_splits=max_splits,
            channel_threshold=0.15,
            min_channel_support=2,
            mandatory_exclusion_radius=1,
            candidate_universe="turn_articulation",
        )
        constructor.update(result.diagnostics)
        constructor.update(result.timings)
        constructor["constructor_stop_reason"] = "one_shot_threshold"
        return list(result.boundary), constructor
    if method == "graph_rd_joint":
        boundary, constructor_final = learned_boundary(
            "learned_rd_joint_occ2_audit2",
            rows=rows,
            slip=slip,
            gamma=gamma,
            max_splits=max_splits,
        )
        constructor.update(constructor_final)
        return boundary, constructor
    if method == "graph_rd_surrogate_joint":
        boundary, constructor_final = learned_boundary(
            "learned_rd_surrogate_joint_occ2_audit2",
            rows=rows,
            slip=slip,
            gamma=gamma,
            max_splits=max_splits,
        )
        constructor.update(constructor_final)
        return boundary, constructor
    raise ValueError(f"Unknown option comparison method: {method}")


def policy_from_row(row: Mapping[str, object]) -> Dict[int, str]:
    raw = str(row.get("policy_smdp_json", "{}"))
    parsed = json.loads(raw)
    return {int(k): str(v) for k, v in parsed.items()}


def sample_action(policy_dist: Mapping[str, float], rng: np.random.Generator) -> str:
    actions = [action for action in ACTIONS if float(policy_dist.get(action, 0.0)) > 0.0]
    if not actions:
        raise ValueError("Policy distribution has no positive-mass action.")
    probs = np.array([float(policy_dist[action]) for action in actions], dtype=float)
    probs = probs / probs.sum()
    return str(rng.choice(actions, p=probs))


def parse_option_target_position(option_label: str) -> int | None:
    if option_label == "TERMINAL" or "_to_" not in option_label:
        return None
    try:
        return int(option_label.rsplit("_to_", 1)[1])
    except ValueError:
        return None


def rollout_smdp_policy(
    grid: GridWorld,
    boundary: Sequence[int],
    audit_boundary: Sequence[int],
    policy_smdp: Mapping[int, str],
    slip: float,
    n_rollouts: int,
    seed: int,
    max_steps: int,
    max_option_steps: int,
) -> Dict[str, float]:
    start = grid.symbol_states("S")[0]
    goal = grid.symbol_states("G")[0]
    boundary = sorted(set(int(state) for state in boundary))
    boundary_set = set(boundary)
    audit_set = set(int(state) for state in audit_boundary)
    boundary_to_pos = {state: pos for pos, state in enumerate(boundary)}
    if start not in boundary_to_pos or goal not in boundary_to_pos:
        return {
            "success_rate": 0.0,
            "primitive_steps_mean": float("inf"),
            "primitive_steps_success_mean": float("nan"),
            "option_steps_mean": float("inf"),
            "hidden_audit_crossings_mean": float("inf"),
            "hidden_audit_distinct_mean": float("inf"),
        }

    rng = np.random.default_rng(seed)
    successes = 0
    primitive_steps: List[float] = []
    primitive_steps_success: List[float] = []
    option_steps: List[float] = []
    hidden_crossings: List[float] = []
    hidden_distinct: List[float] = []
    target_policy_cache: Dict[int, object] = {}

    for _ in range(n_rollouts):
        state = start
        total_steps = 0
        total_options = 0
        total_hidden_crossings = 0
        total_hidden_distinct: set[int] = set()
        success = False
        failed = False

        while total_steps < max_steps:
            if state == goal:
                success = True
                break
            src_pos = boundary_to_pos.get(state)
            if src_pos is None:
                failed = True
                break
            option = policy_smdp.get(src_pos, "TERMINAL")
            target_pos = parse_option_target_position(option)
            if target_pos is None or target_pos < 0 or target_pos >= len(boundary):
                failed = True
                break
            target_state = boundary[target_pos]
            if target_state not in target_policy_cache:
                target_policy_cache[target_state] = shortest_path_policy_to_target(
                    grid,
                    target=target_state,
                    slip=slip,
                )
            primitive_policy = target_policy_cache[target_state]
            source_state = state
            option_terminated = False

            for _option_step in range(max_option_steps):
                dist = primitive_policy(state)
                action = sample_action(dist, rng)
                state = grid.next_state(state, action)
                total_steps += 1
                if state in audit_set and state not in boundary_set:
                    total_hidden_crossings += 1
                    total_hidden_distinct.add(state)
                if state == goal:
                    success = True
                    total_options += 1
                    option_terminated = True
                    break
                if state in boundary_set and state != source_state:
                    total_options += 1
                    option_terminated = True
                    break
                if total_steps >= max_steps:
                    break

            if success or total_steps >= max_steps:
                break
            if not option_terminated:
                failed = True
                break

        if success and not failed:
            successes += 1
            primitive_steps_success.append(float(total_steps))
        primitive_steps.append(float(total_steps))
        option_steps.append(float(total_options))
        hidden_crossings.append(float(total_hidden_crossings))
        hidden_distinct.append(float(len(total_hidden_distinct)))

    return {
        "success_rate": float(successes / max(1, n_rollouts)),
        "primitive_steps_mean": float(np.mean(primitive_steps)) if primitive_steps else float("nan"),
        "primitive_steps_success_mean": (
            float(np.mean(primitive_steps_success)) if primitive_steps_success else float("nan")
        ),
        "option_steps_mean": float(np.mean(option_steps)) if option_steps else float("nan"),
        "hidden_audit_crossings_mean": float(np.mean(hidden_crossings)) if hidden_crossings else float("nan"),
        "hidden_audit_distinct_mean": float(np.mean(hidden_distinct)) if hidden_distinct else float("nan"),
    }


def graph_model_query_proxy(grid: GridWorld, method: str, constructor: Mapping[str, object]) -> float:
    edge_count = float(graph_adjacency(grid).sum() / 2.0)
    if method.startswith("random_landmarks_"):
        return 0.0
    if method.startswith("graph_rd_"):
        step = float(constructor.get("step", constructor.get("constructor_step", 0.0)) or 0.0)
        return step * (float(grid.n_states) + edge_count)
    if method == "endpoints":
        return 0.0
    return float(grid.n_states) + edge_count


def evaluate_method(
    method: str,
    map_name: str,
    rows: Tuple[str, ...],
    slip: float,
    args: argparse.Namespace,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    boundary, constructor = construct_boundary(
        method=method,
        map_name=map_name,
        rows=rows,
        grid=grid,
        slip=slip,
        gamma=args.gamma,
        max_splits=args.max_splits,
        seed=args.seed,
    )
    residual_boundary = candidate_boundary_states(
        grid,
        kind=args.audit_lens,
        goal_state=goal,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.audit_top_fraction,
    )
    soft_state_cost = critical_saliency(
        grid,
        kind=args.soft_kind,
        goal_state=goal,
        gamma=args.gamma,
        slip=slip,
        top_fraction=args.soft_top_fraction,
    )
    row, _edge_rows = evaluate_boundary(
        map_name=map_name,
        grid=grid,
        boundary=boundary,
        candidate_boundary=boundary,
        residual_boundary=residual_boundary,
        soft_state_cost=soft_state_cost,
        slip=slip,
        gamma=args.gamma,
        local_horizon=args.local_horizon,
        hidden_threshold=args.hidden_threshold,
        soft_threshold=args.soft_threshold,
        residual_threshold=args.residual_threshold,
        residual_reward_weight=args.residual_reward_weight,
        residual_hit_weight=args.residual_hit_weight,
        residual_threshold_mode=args.residual_threshold_mode,
        compute_struct_distinct=True,
        struct_mdl_node_cost_weight=1.0,
        struct_mdl_edge_cost_weight=0.5,
        struct_mdl_exposure_bit_weight=1.0,
        struct_mdl_min_gain=0.0,
        residual_kind=args.audit_lens,
        residual_top_fraction=args.audit_top_fraction,
        soft_kind=args.soft_kind,
        soft_top_fraction=args.soft_top_fraction,
        soft_cost_weight=1.0,
        candidate_kind=method,
        candidate_top_fraction=0.0,
        proposal_boundary=residual_boundary,
    )

    policy_smdp = policy_from_row(row)
    rollout = rollout_smdp_policy(
        grid=grid,
        boundary=boundary,
        audit_boundary=residual_boundary,
        policy_smdp=policy_smdp,
        slip=slip,
        n_rollouts=args.n_rollouts,
        seed=stable_method_seed(args.seed, method, map_name, slip),
        max_steps=args.max_steps or max(100, 12 * grid.n_states),
        max_option_steps=args.max_option_steps or max(20, 4 * grid.n_states),
    )
    row.update(rollout)
    row.update(
        {
            "method": method,
            "method_family": method_family(method),
            "audit_lens": args.audit_lens,
            "audit_boundary_size": len(set(residual_boundary)),
            "training_samples": 0,
            "kernel_estimation_rollouts": 0,
            "eval_rollouts": args.n_rollouts,
            "model_queries_proxy": graph_model_query_proxy(grid, method, constructor),
            "constructor_stop_reason": constructor.get("stop_reason", ""),
            "constructor_step": constructor.get("step", ""),
            "constructor_last_split_source": constructor.get("last_split_source", ""),
            "constructor_last_split_state": constructor.get("last_split_state", ""),
            "constructor_last_split_score": constructor.get("last_split_score", ""),
        }
    )
    return row


def write_csv_all_fields(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return
    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def json_default(obj: object) -> object:
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        if math.isfinite(float(obj)):
            return float(obj)
        return str(float(obj))
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "method",
        "method_family",
        "map",
        "slip",
        "n_boundary",
        "feasible",
        "success_rate",
        "primitive_steps_mean",
        "option_steps_mean",
        "start_gap",
        "value_gap_max",
        "occupancy_struct_hidden_distinct",
        "struct_hidden_distinct_cvar95",
        "hidden_audit_distinct_mean",
        "target_policy_tv_total",
        "description_length_proxy",
    ]
    lines = [
        "# Option Algorithm Comparison",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"methods = {list(args.methods)}",
        f"maps = {list(args.maps)}, slips = {list(args.slips)}, gamma = {args.gamma}",
        (
            "Tabular first pass: option terminations are selected in the original environment, "
            "option policies are shortest-path-to-subgoal, kernels are exact first-boundary reductions, "
            "and rollout metrics simulate the SMDP policy back in the original environment."
        ),
        f"audit_lens = {args.audit_lens}, n_rollouts = {args.n_rollouts}",
        "",
        "## Comparison",
        "",
        markdown_table(rows, columns),
        "",
        "## Notes",
        "",
        "- `training_samples = 0` means these are constructed tabular baselines, not trained Option-Critic-style agents.",
        "- `model_queries_proxy` is a rough graph/model-access proxy for construction cost, not a true sample-efficiency curve.",
        "- `hidden_audit_distinct_mean` is measured from original-environment rollouts against the audit lens.",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare tabular option-discovery baselines against extracted graph options."
    )
    parser.add_argument("--maps", nargs="+", default=["maze"])
    parser.add_argument("--slips", type=float, nargs="+", default=[0.05])
    parser.add_argument("--methods", nargs="+", default=list(DEFAULT_METHODS))
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--max-splits", type=int, default=40)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-rollouts", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=0)
    parser.add_argument("--max-option-steps", type=int, default=0)
    parser.add_argument("--audit-lens", default="turn_articulation")
    parser.add_argument("--audit-top-fraction", type=float, default=0.15)
    parser.add_argument("--soft-kind", default="combined")
    parser.add_argument("--soft-top-fraction", type=float, default=0.15)
    parser.add_argument("--local-horizon", type=float, default=999.0)
    parser.add_argument("--hidden-threshold", type=float, default=1e-6)
    parser.add_argument("--soft-threshold", type=float, default=3.0)
    parser.add_argument("--residual-threshold", type=float, default=0.5)
    parser.add_argument("--residual-threshold-mode", default="struct_distinct")
    parser.add_argument("--residual-reward-weight", type=float, default=0.05)
    parser.add_argument("--residual-hit-weight", type=float, default=0.0)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/option_algorithm_comparison_maze_slip005"),
    )
    args = parser.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        map_rows = MAPS[map_name]
        for slip in args.slips:
            for method in args.methods:
                rows.append(evaluate_method(method, map_name, map_rows, slip, args))

    write_csv_all_fields(out_dir / "comparison.csv", rows)
    (out_dir / "comparison.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
