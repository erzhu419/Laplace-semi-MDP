from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import GridWorld
from compression_experiment_utils import scaled_rows


@dataclass(frozen=True)
class BoundaryHeatmapContext:
    map_family: str
    map_size: int
    topology_seed: int
    goal_variant: int
    map_name: str
    rows: Tuple[str, ...]
    split: str


def parse_family_sizes(specs: Sequence[str]) -> Dict[str, List[int]]:
    parsed: Dict[str, List[int]] = {}
    for spec in specs:
        family, raw_sizes = spec.split(":", 1)
        sizes = [int(item) for item in raw_sizes.split(",") if item]
        if not sizes:
            raise ValueError(f"Map spec has no sizes: {spec}")
        parsed.setdefault(family, []).extend(sizes)
    return {family: sorted(set(sizes)) for family, sizes in parsed.items()}


def size_holdout_split(size: int, family_sizes: Sequence[int]) -> str:
    sizes = sorted(set(int(value) for value in family_sizes))
    if len(sizes) < 3:
        raise ValueError("Boundary-heatmap scale splits require at least three sizes per family.")
    if int(size) == sizes[-1]:
        return "test"
    if int(size) == sizes[-2]:
        return "validation"
    return "train"


def replace_goal(rows: Tuple[str, ...], goal_state: int) -> Tuple[str, ...]:
    grid = GridWorld(rows)
    _coord_to_state, state_to_coord = grid.index_maps()
    goal_coord = state_to_coord[int(goal_state)]
    out: List[str] = []
    for row_index, row in enumerate(rows):
        chars = ["." if char == "G" else char for char in row]
        if row_index == goal_coord[0]:
            chars[goal_coord[1]] = "G"
        out.append("".join(chars))
    return tuple(out)


def _start_distances(grid: GridWorld, start: int) -> np.ndarray:
    distances = np.full(grid.n_states, np.inf, dtype=float)
    distances[int(start)] = 0.0
    queue = [int(start)]
    cursor = 0
    while cursor < len(queue):
        state = queue[cursor]
        cursor += 1
        for action in grid.legal_actions(state):
            neighbor = int(grid.next_state(state, action))
            if math.isfinite(float(distances[neighbor])):
                continue
            distances[neighbor] = distances[state] + 1.0
            queue.append(neighbor)
    return distances


def goal_variant_rows(
    rows: Tuple[str, ...],
    count: int,
    seed: int,
) -> List[Tuple[int, Tuple[str, ...]]]:
    """Return the original goal plus deterministic, distant alternatives."""

    grid = GridWorld(rows)
    start = grid.symbol_states("S")[0]
    original_goal = grid.symbol_states("G")[0]
    distances = _start_distances(grid, start)
    candidates = [
        state
        for state in range(grid.n_states)
        if state not in {start, original_goal} and math.isfinite(float(distances[state]))
    ]
    if not candidates or int(count) <= 1:
        return [(0, rows)]

    finite_distances = np.asarray([distances[state] for state in candidates], dtype=float)
    cutoff = float(np.quantile(finite_distances, 0.55))
    distant = [state for state in candidates if float(distances[state]) >= cutoff]
    ranked = sorted(
        distant,
        key=lambda state: (
            -float(distances[state]),
            ((int(state) + 1) * 1103515245 + (int(seed) + 17) * 12345) % 2147483647,
            int(state),
        ),
    )
    requested = min(max(0, int(count) - 1), len(ranked))
    if requested == 0:
        return [(0, rows)]
    positions = np.linspace(0, len(ranked) - 1, num=requested, dtype=int)
    selected: List[int] = []
    for position in positions.tolist():
        state = int(ranked[int(position)])
        if state not in selected:
            selected.append(state)
    return [(0, rows)] + [
        (index, replace_goal(rows, state))
        for index, state in enumerate(selected, start=1)
    ]


def expand_contexts(
    map_specs: Sequence[str],
    topology_seeds: Sequence[int],
    goal_variants: int,
) -> List[BoundaryHeatmapContext]:
    family_sizes = parse_family_sizes(map_specs)
    contexts: List[BoundaryHeatmapContext] = []
    for family, sizes in family_sizes.items():
        seeds = list(topology_seeds) if family in {"maze", "braid_maze"} else [0]
        for size in sizes:
            split = size_holdout_split(size, sizes)
            for topology_seed in seeds:
                base_rows = scaled_rows(family, size, seed=int(topology_seed))
                variants = goal_variant_rows(
                    base_rows,
                    count=goal_variants,
                    seed=int(topology_seed) + 1009 * int(size),
                )
                for goal_variant, rows in variants:
                    parts = [family, str(size)]
                    if family in {"maze", "braid_maze"}:
                        parts.append(f"seed{int(topology_seed)}")
                    parts.append(f"goal{int(goal_variant)}")
                    contexts.append(
                        BoundaryHeatmapContext(
                            map_family=family,
                            map_size=int(size),
                            topology_seed=int(topology_seed),
                            goal_variant=int(goal_variant),
                            map_name="_".join(parts),
                            rows=rows,
                            split=split,
                        )
                    )
    return contexts


def context_fields(context: BoundaryHeatmapContext) -> Dict[str, object]:
    return {
        "split": context.split,
        "map_family": context.map_family,
        "map_size": context.map_size,
        "map": context.map_name,
        "maze_seed": context.topology_seed,
        "topology_seed": context.topology_seed,
        "goal_variant": context.goal_variant,
        "map_rows": json.dumps(context.rows),
    }


def rows_from_record(row: Mapping[str, object]) -> Tuple[str, ...]:
    encoded = str(row.get("map_rows", "")).strip()
    if encoded:
        parsed = json.loads(encoded)
        if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
            raise ValueError("map_rows must encode a JSON list of strings.")
        return tuple(parsed)
    family = str(row.get("map_family", "maze"))
    if family == "random_maze":
        family = "maze"
    size = int(float(row.get("map_size", 0)))
    seed = int(float(row.get("topology_seed", row.get("maze_seed", 0))))
    return scaled_rows(family, size, seed=seed)
