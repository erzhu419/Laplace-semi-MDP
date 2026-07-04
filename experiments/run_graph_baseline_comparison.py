#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import (
    GridWorld,
    decision_boundary_states,
    endpoint_boundary_states,
    graph_adjacency,
    junction_boundary_states,
    shortest_path_distance_matrix,
    spectral_boundary_states,
)
from run_first_boundary_targeted import (
    MAPS,
    candidate_boundary_states,
    critical_saliency,
    evaluate_boundary,
    markdown_table,
    run_one,
    write_csv,
)


FIXED_METHODS = {
    "fixed_endpoints": "endpoints",
    "fixed_junction": "junction",
    "fixed_decision": "decision",
    "fixed_spectral25": "spectral_25",
    "fixed_bottleneck15": "bottleneck",
    "fixed_turn_articulation": "turn_articulation",
    "fixed_eigen_extrema4": "eigen_extrema_4",
    "fixed_eigen_extrema8": "eigen_extrema_8",
    "fixed_eigen_extrema12": "eigen_extrema_12",
    "fixed_coverage8": "coverage_8",
    "fixed_coverage12": "coverage_12",
}


LEARNED_RECIPES: Dict[str, Dict[str, object]] = {
    "learned_soft3": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "never",
        "compute_struct_distinct": False,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "threshold",
        "struct_mdl_edge_cost_weight": 0.1,
    },
    "learned_raw_residual12": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 1.2,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "threshold",
        "compute_struct_distinct": False,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.1,
    },
    "learned_struct_distinct4": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 4.0,
        "residual_threshold_mode": "struct_distinct",
        "residual_split_policy": "threshold",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.1,
    },
    "learned_struct_mdl_e05": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "mdl",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.5,
    },
    "learned_struct_mdl_e1": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "mdl",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 1.0,
    },
    "learned_struct_mdl_hard_eigen12": {
        "candidate_kind": "articulation_eigen_extrema_12",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "mdl",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.5,
    },
    "learned_struct_mdl_hard_coverage12": {
        "candidate_kind": "articulation_coverage_12",
        "proposal_kind": "candidate",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "mdl",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.5,
    },
    "learned_struct_mdl_proposal_eigen12": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "eigen_extrema_12",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "mdl",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.5,
    },
    "learned_struct_mdl_proposal_coverage12": {
        "candidate_kind": "articulation_only",
        "proposal_kind": "coverage_12",
        "candidate_top_fraction": 0.15,
        "residual_kind": "turn_articulation",
        "residual_top_fraction": 0.15,
        "residual_threshold": 0.5,
        "residual_threshold_mode": "raw",
        "residual_split_policy": "mdl",
        "compute_struct_distinct": True,
        "soft_kind": "combined",
        "soft_top_fraction": 0.15,
        "soft_threshold": 3.0,
        "soft_split_policy": "never",
        "struct_mdl_edge_cost_weight": 0.5,
    },
}


def parse_count_suffix(method_kind: str) -> int:
    try:
        return int(method_kind.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Method kind must end with a count suffix: {method_kind}") from exc


def eigenoption_terminal_boundary_states(grid: GridWorld, target_count: int, keep_symbols: str = "SG") -> List[int]:
    """Approximate Laplacian eigenoption subgoals via extrema of low-frequency PVFs."""

    keep = set(grid.symbol_states(keep_symbols))
    if len(keep) >= target_count:
        return sorted(keep)

    adjacency = graph_adjacency(grid)
    degree = adjacency.sum(axis=1)
    inv_sqrt_degree = np.zeros_like(degree)
    positive = degree > 0
    inv_sqrt_degree[positive] = 1.0 / np.sqrt(degree[positive])
    normalized_laplacian = np.eye(grid.n_states) - (
        inv_sqrt_degree[:, None] * adjacency * inv_sqrt_degree[None, :]
    )
    eigenvalues, eigenvectors = np.linalg.eigh(normalized_laplacian)
    order = np.argsort(eigenvalues)

    boundary = set(keep)
    for vector_idx in order[1:]:
        vector = eigenvectors[:, int(vector_idx)]
        candidates = [int(np.argmin(vector)), int(np.argmax(vector))]
        for state in sorted(candidates, key=lambda s: (-abs(float(vector[s])), s)):
            boundary.add(state)
            if len(boundary) >= target_count:
                return sorted(boundary)
    return sorted(boundary)


def coverage_boundary_states(grid: GridWorld, target_count: int, keep_symbols: str = "SG") -> List[int]:
    """Topological-map style farthest-point landmarks in shortest-path metric."""

    boundary = set(grid.symbol_states(keep_symbols))
    if len(boundary) >= target_count:
        return sorted(boundary)

    distances = shortest_path_distance_matrix(grid)
    while len(boundary) < target_count:
        best_state = None
        best_distance = -1.0
        for state in range(grid.n_states):
            if state in boundary:
                continue
            nearest = min(float(distances[state, b]) for b in boundary)
            if nearest > best_distance + 1e-12 or (
                abs(nearest - best_distance) <= 1e-12 and (best_state is None or state < best_state)
            ):
                best_distance = nearest
                best_state = state
        if best_state is None:
            break
        boundary.add(best_state)
    return sorted(boundary)


def fixed_boundary(grid: GridWorld, method_kind: str, gamma: float, slip: float, top_fraction: float) -> List[int]:
    goal = grid.symbol_states("G")[0]
    if method_kind == "endpoints":
        return endpoint_boundary_states(grid)
    if method_kind == "junction":
        return junction_boundary_states(grid)
    if method_kind == "decision":
        return decision_boundary_states(grid)
    if method_kind == "spectral_25":
        return spectral_boundary_states(grid, fraction=0.25)
    if method_kind.startswith("eigen_extrema_"):
        return eigenoption_terminal_boundary_states(grid, target_count=parse_count_suffix(method_kind))
    if method_kind.startswith("coverage_"):
        return coverage_boundary_states(grid, target_count=parse_count_suffix(method_kind))
    return candidate_boundary_states(
        grid=grid,
        kind=method_kind,
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=top_fraction,
    )


def learned_boundary(
    method_name: str,
    rows: Tuple[str, ...],
    slip: float,
    gamma: float,
    max_splits: int,
) -> Tuple[List[int], Dict[str, object]]:
    recipe = LEARNED_RECIPES[method_name]
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
    )
    grid = GridWorld(rows)
    boundary = set(endpoint_boundary_states(grid))
    for row in trace:
        if row.get("stop_reason") == "continue" and row.get("split_candidate_state") is not None:
            boundary.add(int(row["split_candidate_state"]))
    constructor_final = dict(trace[-1])
    last_split = next(
        (
            row
            for row in reversed(trace)
            if row.get("stop_reason") == "continue" and row.get("split_candidate_state") is not None
        ),
        None,
    )
    if last_split is not None:
        constructor_final["last_split_source"] = last_split.get("split_candidate_source", "none")
        constructor_final["last_split_state"] = last_split.get("split_candidate_state")
        constructor_final["last_split_coord"] = last_split.get("split_candidate_coord")
        constructor_final["last_split_score"] = last_split.get("split_candidate_score", 0.0)
    else:
        constructor_final["last_split_source"] = "none"
        constructor_final["last_split_state"] = None
        constructor_final["last_split_coord"] = None
        constructor_final["last_split_score"] = 0.0
    return sorted(boundary), constructor_final


def state_from_external_item(item: object, grid: GridWorld) -> int:
    coord_to_idx, _ = grid.index_maps()

    if isinstance(item, (int, np.integer)):
        state = int(item)
    elif isinstance(item, str):
        stripped = item.strip()
        if stripped.isdigit():
            state = int(stripped)
        else:
            coord_text = stripped.strip("()[]")
            parts = coord_text.replace(",", " ").split()
            if len(parts) != 2:
                raise ValueError(f"Cannot parse boundary state or coord: {item!r}")
            coord = (int(parts[0]), int(parts[1]))
            if coord not in coord_to_idx:
                raise ValueError(f"Boundary coord {coord} is not an open cell.")
            state = coord_to_idx[coord]
    elif isinstance(item, Mapping):
        for key in ("state", "state_id", "boundary_state", "id"):
            if key in item:
                return state_from_external_item(item[key], grid)
        if "coord" in item:
            return state_from_external_item(item["coord"], grid)
        row = item.get("row", item.get("r"))
        col = item.get("col", item.get("c"))
        if row is None or col is None:
            raise ValueError(f"Cannot parse boundary mapping: {item!r}")
        coord = (int(row), int(col))
        if coord not in coord_to_idx:
            raise ValueError(f"Boundary coord {coord} is not an open cell.")
        state = coord_to_idx[coord]
    elif isinstance(item, Sequence) and not isinstance(item, (bytes, bytearray)):
        if len(item) != 2:
            raise ValueError(f"Cannot parse boundary sequence: {item!r}")
        coord = (int(item[0]), int(item[1]))
        if coord not in coord_to_idx:
            raise ValueError(f"Boundary coord {coord} is not an open cell.")
        state = coord_to_idx[coord]
    else:
        raise ValueError(f"Cannot parse boundary item: {item!r}")

    if state < 0 or state >= grid.n_states:
        raise ValueError(f"Boundary state {state} is outside [0, {grid.n_states}).")
    return state


def select_external_payload(data: object, map_name: str, slip: float) -> object:
    if not isinstance(data, Mapping):
        return data

    slip_keys = [str(slip), f"{slip:.2f}", f"{slip:.3f}"]
    for key in [f"{map_name}:{k}" for k in slip_keys]:
        if key in data:
            return data[key]
    if map_name in data:
        scoped = data[map_name]
        if isinstance(scoped, Mapping):
            for key in slip_keys:
                if key in scoped:
                    return scoped[key]
            for key in ("boundary_states", "boundary", "states", "boundary_coords", "coords"):
                if key in scoped:
                    return scoped[key]
        return scoped
    for key in ("boundary_states", "boundary", "states", "boundary_coords", "coords"):
        if key in data:
            return data[key]
    return data


def load_external_boundary(path: Path, grid: GridWorld, map_name: str, slip: float) -> List[int]:
    start = grid.symbol_states("S")[0]
    goal = grid.symbol_states("G")[0]

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        payload = select_external_payload(data, map_name, slip)
        if isinstance(payload, Mapping):
            payload = select_external_payload(payload, map_name, slip)
        if isinstance(payload, Mapping):
            raise ValueError(f"Could not find a boundary list in {path}.")
        boundary = [state_from_external_item(item, grid) for item in payload]  # type: ignore[arg-type]
    else:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                rows = list(reader)
                if any(name in reader.fieldnames for name in ("state", "state_id", "boundary_state", "id")):
                    boundary = [state_from_external_item(row, grid) for row in rows]
                elif any(name in reader.fieldnames for name in ("row", "r")) and any(
                    name in reader.fieldnames for name in ("col", "c")
                ):
                    boundary = [state_from_external_item(row, grid) for row in rows]
                else:
                    raise ValueError(f"CSV boundary file {path} needs state/state_id or row,col columns.")
            else:
                boundary = []

    boundary_set = set(boundary)
    boundary_set.update({start, goal})
    return sorted(boundary_set)


def parse_external_boundary_specs(specs: Sequence[str]) -> List[Tuple[str, Path]]:
    parsed: List[Tuple[str, Path]] = []
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"External boundary spec must be METHOD=PATH, got: {spec}")
        method, path_text = spec.split("=", 1)
        method = method.strip()
        if not method:
            raise ValueError(f"External boundary method name is empty in spec: {spec}")
        path = Path(path_text).expanduser()
        if not path.exists():
            raise ValueError(f"External boundary file does not exist: {path}")
        parsed.append((method, path))
    return parsed


def evaluate_uniform(
    method: str,
    method_family: str,
    map_name: str,
    grid: GridWorld,
    boundary: Sequence[int],
    constructor_final: Mapping[str, object],
    gamma: float,
    slip: float,
    residual_lens: str,
    residual_top_fraction: float,
    soft_kind: str,
    soft_top_fraction: float,
) -> Dict[str, object]:
    goal = grid.symbol_states("G")[0]
    if residual_lens == "none":
        residual_boundary = endpoint_boundary_states(grid)
    else:
        residual_boundary = candidate_boundary_states(
            grid=grid,
            kind=residual_lens,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=residual_top_fraction,
        )
    if soft_kind == "none":
        soft_state_cost = np.zeros(grid.n_states, dtype=float)
    else:
        soft_state_cost = critical_saliency(
            grid=grid,
            kind=soft_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=soft_top_fraction,
        )
    row, _ = evaluate_boundary(
        map_name=map_name,
        grid=grid,
        boundary=boundary,
        candidate_boundary=boundary,
        residual_boundary=residual_boundary,
        soft_state_cost=soft_state_cost,
        slip=slip,
        gamma=gamma,
        local_horizon=999.0,
        hidden_threshold=1e-6,
        soft_threshold=3.0,
        residual_threshold=0.5,
        residual_reward_weight=0.05,
        residual_hit_weight=0.0,
        residual_threshold_mode="raw",
        compute_struct_distinct=True,
        struct_mdl_node_cost_weight=1.0,
        struct_mdl_edge_cost_weight=0.5,
        struct_mdl_exposure_bit_weight=1.0,
        struct_mdl_min_gain=0.0,
        residual_kind=residual_lens,
        residual_top_fraction=residual_top_fraction,
        soft_kind=soft_kind,
        soft_top_fraction=soft_top_fraction,
        soft_cost_weight=1.0,
        candidate_kind=method,
        candidate_top_fraction=0.15,
    )
    row.update(
        {
            "method": method,
            "method_family": method_family,
            "eval_residual_lens": residual_lens,
            "eval_soft_kind": soft_kind,
            "constructor_stop": constructor_final.get("stop_reason", "fixed"),
            "constructor_step": constructor_final.get("step", 0),
            "constructor_n_boundary": constructor_final.get("n_boundary", len(boundary)),
            "constructor_split_source": constructor_final.get("split_candidate_source", "fixed"),
            "constructor_last_split_source": constructor_final.get("last_split_source", "fixed"),
            "constructor_last_split_state": constructor_final.get("last_split_state", ""),
            "constructor_last_split_coord": constructor_final.get("last_split_coord", ""),
            "constructor_last_split_score": constructor_final.get("last_split_score", 0.0),
        }
    )
    n_edges = max(1.0, float(row["n_edges_valid"]))
    n_boundary = max(1.0, float(row["n_boundary"]))
    row["struct_hidden_distinct_per_edge"] = float(row["struct_hidden_distinct_valid_total"]) / n_edges
    row["soft_cost_per_edge"] = float(row["soft_cost_valid_total"]) / n_edges
    row["target_policy_tv_per_edge"] = float(row["target_policy_tv_total"]) / n_edges
    row["description_length_per_edge"] = float(row["description_length_proxy"]) / n_edges
    row["description_length_per_boundary"] = float(row["description_length_proxy"]) / n_boundary
    return row


def summarize(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "method",
        "method_family",
        "map",
        "slip",
        "n_boundary",
        "n_edges_valid",
        "start_gap",
        "value_gap_max",
        "model_residual_max",
        "residual_backup_value_norm_max",
        "struct_hidden_prob_max",
        "struct_hidden_distinct_valid_total",
        "struct_hidden_distinct_per_edge",
        "soft_cost_valid_total",
        "target_policy_tv_total",
        "description_length_proxy",
        "constructor_stop",
        "constructor_last_split_source",
    ]
    lines = [
        "# Graph Baseline Comparison",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"fixed_methods = {args.fixed_methods}",
        f"learned_methods = {args.learned_methods}",
        f"external_boundary_files = {args.boundary_files}",
        f"maps = {args.maps}, slips = {args.slips}, gamma = {args.gamma}",
        f"eval_residual_lens = {args.eval_residual_lens}, eval_soft_kind = {args.eval_soft_kind}",
        "",
        "## Results",
        "",
        markdown_table(rows, columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fixed and learned graph-option abstraction baselines.")
    parser.add_argument("--maps", nargs="+", default=["open_room", "four_rooms", "maze"])
    parser.add_argument("--slips", type=float, nargs="+", default=[0.0, 0.05])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--fixed-methods", nargs="+", default=list(FIXED_METHODS.keys()))
    parser.add_argument(
        "--learned-methods",
        nargs="+",
        default=[
            "learned_soft3",
            "learned_raw_residual12",
            "learned_struct_distinct4",
            "learned_struct_mdl_e05",
            "learned_struct_mdl_e1",
        ],
    )
    parser.add_argument("--fixed-top-fraction", type=float, default=0.15)
    parser.add_argument("--eval-residual-lens", default="turn_articulation")
    parser.add_argument("--eval-residual-top-fraction", type=float, default=0.15)
    parser.add_argument("--eval-soft-kind", default="combined")
    parser.add_argument("--eval-soft-top-fraction", type=float, default=0.15)
    parser.add_argument("--max-splits", type=int, default=20)
    parser.add_argument(
        "--boundary-files",
        nargs="*",
        default=[],
        metavar="METHOD=PATH",
        help="Evaluate external option-discovery/landmark outputs as boundary proposals.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/graph_baseline_comparison"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    external_boundary_specs = parse_external_boundary_specs(args.boundary_files)
    rows_out: List[Dict[str, object]] = []
    for map_name in args.maps:
        if map_name not in MAPS:
            raise ValueError(f"Unknown map: {map_name}")
        for slip in args.slips:
            grid = GridWorld(MAPS[map_name])
            for method in args.fixed_methods:
                if method not in FIXED_METHODS:
                    raise ValueError(f"Unknown fixed method: {method}")
                boundary = fixed_boundary(
                    grid=grid,
                    method_kind=FIXED_METHODS[method],
                    gamma=args.gamma,
                    slip=slip,
                    top_fraction=args.fixed_top_fraction,
                )
                row = evaluate_uniform(
                    method=method,
                    method_family="fixed",
                    map_name=map_name,
                    grid=grid,
                    boundary=boundary,
                    constructor_final={"stop_reason": "fixed", "n_boundary": len(boundary)},
                    gamma=args.gamma,
                    slip=slip,
                    residual_lens=args.eval_residual_lens,
                    residual_top_fraction=args.eval_residual_top_fraction,
                    soft_kind=args.eval_soft_kind,
                    soft_top_fraction=args.eval_soft_top_fraction,
                )
                rows_out.append(row)
                print(f"{method:28s} {map_name:10s} slip={slip:.2f} B={row['n_boundary']:3d}")
            for method, path in external_boundary_specs:
                boundary = load_external_boundary(path=path, grid=grid, map_name=map_name, slip=slip)
                row = evaluate_uniform(
                    method=method,
                    method_family="external_boundary",
                    map_name=map_name,
                    grid=grid,
                    boundary=boundary,
                    constructor_final={"stop_reason": "external_file", "n_boundary": len(boundary)},
                    gamma=args.gamma,
                    slip=slip,
                    residual_lens=args.eval_residual_lens,
                    residual_top_fraction=args.eval_residual_top_fraction,
                    soft_kind=args.eval_soft_kind,
                    soft_top_fraction=args.eval_soft_top_fraction,
                )
                rows_out.append(row)
                print(f"{method:28s} {map_name:10s} slip={slip:.2f} B={row['n_boundary']:3d}")
            for method in args.learned_methods:
                if method not in LEARNED_RECIPES:
                    raise ValueError(f"Unknown learned method: {method}")
                boundary, constructor_final = learned_boundary(
                    method_name=method,
                    rows=MAPS[map_name],
                    slip=slip,
                    gamma=args.gamma,
                    max_splits=args.max_splits,
                )
                row = evaluate_uniform(
                    method=method,
                    method_family="learned",
                    map_name=map_name,
                    grid=grid,
                    boundary=boundary,
                    constructor_final=constructor_final,
                    gamma=args.gamma,
                    slip=slip,
                    residual_lens=args.eval_residual_lens,
                    residual_top_fraction=args.eval_residual_top_fraction,
                    soft_kind=args.eval_soft_kind,
                    soft_top_fraction=args.eval_soft_top_fraction,
                )
                rows_out.append(row)
                print(f"{method:28s} {map_name:10s} slip={slip:.2f} B={row['n_boundary']:3d}")

    write_csv(args.out_dir / "comparison.csv", rows_out)
    (args.out_dir / "comparison.json").write_text(json.dumps(rows_out, indent=2) + "\n", encoding="utf-8")
    summarize(rows_out, args.out_dir / "summary.md", args)
    print(f"Wrote {args.out_dir / 'comparison.csv'}")
    print(f"Wrote {args.out_dir / 'comparison.json'}")
    print(f"Wrote {args.out_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
