from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import networkx as nx
import numpy as np
from scipy.linalg import eigh

from bellman_kron import (
    BellmanKronReduction,
    bellman_kron_reduce,
    discounted_interior_occupancy,
)


@dataclass(frozen=True)
class FiniteMDP:
    """Finite known-model MDP interface used by general-environment smoke tests.

    ``P[a, s, s2]`` is the transition kernel and ``R[a, s]`` is the expected
    immediate reward for taking action ``a`` in state ``s``.  This intentionally
    mirrors the mathematical objects used by the Green-kernel reducers instead
    of the older grid-only helper API.
    """

    name: str
    P: np.ndarray
    R: np.ndarray
    action_names: Tuple[str, ...]
    terminal_states: Tuple[int, ...] = ()
    goal_states: Tuple[int, ...] = ()
    start_states: Tuple[int, ...] = ()
    start_distribution: np.ndarray | None = None
    coords: np.ndarray | None = None
    state_labels: Tuple[str, ...] | None = None
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if self.P.ndim != 3:
            raise ValueError("P must have shape (n_actions, n_states, n_states).")
        if self.R.shape != self.P.shape[:2]:
            raise ValueError("R must have shape (n_actions, n_states).")
        if len(self.action_names) != self.P.shape[0]:
            raise ValueError("action_names length must match P.shape[0].")
        row_sums = self.P.sum(axis=2)
        if not np.allclose(row_sums, 1.0, atol=1e-8):
            raise ValueError("Each transition row in P must sum to one.")
        if self.start_distribution is not None:
            dist = np.asarray(self.start_distribution, dtype=float)
            if dist.shape != (self.n_states,):
                raise ValueError("start_distribution must have shape (n_states,).")
            if dist.sum() <= 0:
                raise ValueError("start_distribution must have positive mass.")

    @property
    def n_actions(self) -> int:
        return int(self.P.shape[0])

    @property
    def n_states(self) -> int:
        return int(self.P.shape[1])

    def transition_matrix_for_action(self, action_index: int) -> Tuple[np.ndarray, np.ndarray]:
        return self.P[int(action_index)].copy(), self.R[int(action_index)].copy()

    def terminal_set(self) -> set[int]:
        return set(int(s) for s in self.terminal_states)

    def start_distribution_or_uniform(self) -> np.ndarray:
        if self.start_distribution is not None:
            dist = np.asarray(self.start_distribution, dtype=float).copy()
            return dist / dist.sum()
        dist = np.zeros(self.n_states, dtype=float)
        starts = [int(s) for s in self.start_states if 0 <= int(s) < self.n_states]
        if starts:
            dist[starts] = 1.0 / len(starts)
        else:
            non_terminal = [s for s in range(self.n_states) if s not in self.terminal_set()]
            for s in non_terminal:
                dist[s] = 1.0 / max(1, len(non_terminal))
        return dist


def make_absorbing(P: np.ndarray, R: np.ndarray, terminal_states: Iterable[int]) -> Tuple[np.ndarray, np.ndarray]:
    P = np.asarray(P, dtype=float).copy()
    R = np.asarray(R, dtype=float).copy()
    for state in sorted(set(int(s) for s in terminal_states)):
        if 0 <= state < P.shape[1]:
            P[:, state, :] = 0.0
            P[:, state, state] = 1.0
            R[:, state] = 0.0
    return P, R


def finite_mdp_from_gym_toy_text(env_id: str, seed: int = 0) -> FiniteMDP:
    """Build a finite MDP from Gymnasium ToyText environments exposing ``env.P``."""

    import gymnasium as gym

    env = gym.make(env_id)
    raw = env.unwrapped
    if not hasattr(raw, "P"):
        env.close()
        raise ValueError(f"{env_id} does not expose a tabular P dictionary.")
    n_states = int(raw.observation_space.n)
    n_actions = int(raw.action_space.n)
    P = np.zeros((n_actions, n_states, n_states), dtype=float)
    R = np.zeros((n_actions, n_states), dtype=float)
    terminal_states: set[int] = set()
    goal_states: set[int] = set()
    for state in range(n_states):
        for action in range(n_actions):
            for prob, next_state, reward, terminated in raw.P[state][action]:
                ns = int(next_state)
                p = float(prob)
                r = float(reward)
                P[action, state, ns] += p
                R[action, state] += p * r
                if bool(terminated):
                    terminal_states.add(ns)
                    if r > 0.0:
                        goal_states.add(ns)

    P, R = make_absorbing(P, R, terminal_states)
    start_distribution = _gym_toy_text_start_distribution(raw, n_states)
    if start_distribution is None:
        obs, _info = env.reset(seed=seed)
        start_distribution = np.zeros(n_states, dtype=float)
        start_distribution[int(obs)] = 1.0
    start_states = tuple(np.flatnonzero(start_distribution > 0.0).astype(int).tolist())
    coords = _gym_toy_text_coords(raw, n_states)
    action_names = tuple(str(name) for name in getattr(raw, "action_names", range(n_actions)))
    if len(action_names) != n_actions:
        action_names = tuple(f"a{a}" for a in range(n_actions))
    env.close()
    return FiniteMDP(
        name=env_id,
        P=P,
        R=R,
        action_names=action_names,
        terminal_states=tuple(sorted(terminal_states)),
        goal_states=tuple(sorted(goal_states)),
        start_states=start_states,
        start_distribution=start_distribution,
        coords=coords,
        state_labels=tuple(str(s) for s in range(n_states)),
        metadata={"source": "gymnasium_toy_text", "env_id": env_id},
    )


def _gym_toy_text_start_distribution(raw: object, n_states: int) -> np.ndarray | None:
    if hasattr(raw, "initial_state_distrib"):
        dist = np.asarray(getattr(raw, "initial_state_distrib"), dtype=float)
        if dist.shape == (n_states,) and dist.sum() > 0:
            return dist / dist.sum()
    return None


def _gym_toy_text_coords(raw: object, n_states: int) -> np.ndarray:
    desc = getattr(raw, "desc", None)
    if desc is not None:
        rows, cols = np.asarray(desc).shape[:2]
        return np.array([(state // cols, state % cols) for state in range(n_states)], dtype=float)
    if hasattr(raw, "decode") and n_states == 500:
        coords = []
        for state in range(n_states):
            taxi_row, taxi_col, pass_loc, dest_idx = raw.decode(state)
            coords.append((float(taxi_row), float(taxi_col) + 0.08 * float(pass_loc) + 0.02 * float(dest_idx)))
        return np.asarray(coords, dtype=float)
    side = int(math.ceil(math.sqrt(n_states)))
    return np.array([(state // side, state % side) for state in range(n_states)], dtype=float)


def discretized_point_maze_mdp(
    layout: str = "umaze",
    bins_per_cell: int = 3,
    noise: float = 0.08,
    samples: int = 17,
    seed: int = 0,
) -> FiniteMDP:
    """Discretized sampled PointMaze-style MDP.

    The underlying state is a continuous point in a maze; the adapter stores the
    empirical transition kernel over grid bins.  The theorem claim should be made
    for this discretized empirical MDP, not for the continuous simulator itself.
    """

    rows = _point_maze_rows(layout)
    open_cells = [(r, c) for r, row in enumerate(rows) for c, ch in enumerate(row) if ch != "#"]
    states: List[Tuple[float, float]] = []
    labels: List[str] = []
    cell_of_state: List[Tuple[int, int]] = []
    for r, c in open_cells:
        for i in range(bins_per_cell):
            for j in range(bins_per_cell):
                y = r + (i + 0.5) / bins_per_cell
                x = c + (j + 0.5) / bins_per_cell
                states.append((y, x))
                labels.append(f"({y:.2f},{x:.2f})")
                cell_of_state.append((r, c))
    coord_to_state = {coord: idx for idx, coord in enumerate(states)}
    n_states = len(states)
    actions = (
        ("N", (-1.0, 0.0)),
        ("S", (1.0, 0.0)),
        ("W", (0.0, -1.0)),
        ("E", (0.0, 1.0)),
        ("NW", (-1.0, -1.0)),
        ("NE", (-1.0, 1.0)),
        ("SW", (1.0, -1.0)),
        ("SE", (1.0, 1.0)),
    )
    action_names = tuple(name for name, _delta in actions)
    start_cell = _find_symbol(rows, "S") or open_cells[0]
    goal_cell = _find_symbol(rows, "G") or open_cells[-1]
    start_states = tuple(i for i, cell in enumerate(cell_of_state) if cell == start_cell)
    goal_states = tuple(i for i, cell in enumerate(cell_of_state) if cell == goal_cell)
    start_distribution = np.zeros(n_states, dtype=float)
    for state in start_states:
        start_distribution[state] = 1.0 / max(1, len(start_states))

    rng = np.random.default_rng(seed)
    noise_samples = rng.normal(loc=0.0, scale=float(noise), size=(max(1, samples), 2))
    P = np.zeros((len(actions), n_states, n_states), dtype=float)
    R = np.full((len(actions), n_states), -1.0, dtype=float)
    open_set = set(open_cells)
    step_size = 0.72 / max(1, bins_per_cell)
    for action_index, (_name, delta) in enumerate(actions):
        direction = np.asarray(delta, dtype=float)
        norm = float(np.linalg.norm(direction))
        if norm > 0:
            direction = direction / norm
        for state, pos in enumerate(states):
            if state in goal_states:
                P[action_index, state, state] = 1.0
                R[action_index, state] = 0.0
                continue
            counts: Dict[int, int] = {}
            for eps in noise_samples:
                proposed = np.asarray(pos, dtype=float) + step_size * direction + eps / max(1, bins_per_cell)
                next_state = _project_point_maze_state(proposed, states, coord_to_state, open_set)
                counts[next_state] = counts.get(next_state, 0) + 1
            total = float(sum(counts.values()))
            for next_state, count in counts.items():
                P[action_index, state, next_state] += float(count) / total
    P, R = make_absorbing(P, R, goal_states)
    return FiniteMDP(
        name=f"PointMaze-{layout}-b{bins_per_cell}",
        P=P,
        R=R,
        action_names=action_names,
        terminal_states=tuple(sorted(goal_states)),
        goal_states=tuple(sorted(goal_states)),
        start_states=start_states,
        start_distribution=start_distribution,
        coords=np.asarray(states, dtype=float),
        state_labels=tuple(labels),
        metadata={
            "source": "discretized_point_maze",
            "layout": layout,
            "bins_per_cell": bins_per_cell,
            "noise": noise,
            "samples": samples,
        },
    )


def _point_maze_rows(layout: str) -> Tuple[str, ...]:
    if layout == "umaze":
        return (
            "#####",
            "#S..#",
            "###.#",
            "#G..#",
            "#####",
        )
    if layout == "medium":
        return (
            "#######",
            "#S....#",
            "###.###",
            "#.....#",
            "#.#####",
            "#....G#",
            "#######",
        )
    raise ValueError(f"Unknown point-maze layout: {layout}")


def _find_symbol(rows: Sequence[str], symbol: str) -> Tuple[int, int] | None:
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == symbol:
                return r, c
    return None


def _project_point_maze_state(
    proposed: np.ndarray,
    states: Sequence[Tuple[float, float]],
    coord_to_state: Mapping[Tuple[float, float], int],
    open_cells: set[Tuple[int, int]],
) -> int:
    y, x = float(proposed[0]), float(proposed[1])
    cell = (int(math.floor(y)), int(math.floor(x)))
    if cell not in open_cells:
        nearest = min(range(len(states)), key=lambda idx: float(np.sum((np.asarray(states[idx]) - proposed) ** 2)))
        return int(nearest)
    nearest = min(
        (idx for idx, pos in enumerate(states) if (int(math.floor(pos[0])), int(math.floor(pos[1]))) == cell),
        key=lambda idx: float(np.sum((np.asarray(states[idx]) - proposed) ** 2)),
    )
    return int(nearest)


MiniGridStateKey = Tuple[Tuple[int, int], int, bytes, Tuple[str, str, int] | None]


def finite_mdp_from_minigrid(env_id: str, seed: int = 0, max_states: int = 50_000) -> FiniteMDP:
    """Enumerate a fixed-seed MiniGrid task by symbolic simulator state.

    Requires the optional ``minigrid`` package.  The BFS uses deep-copied
    unwrapped env states, so this adapter is intentionally for small symbolic
    tasks such as FourRooms, MultiRoom, and DoorKey sanity checks.
    """

    import gymnasium as gym
    import minigrid  # noqa: F401

    env = gym.make(env_id)
    obs, _info = env.reset(seed=seed)
    raw = env.unwrapped
    start_key = _minigrid_state_key(raw)
    state_to_index: Dict[MiniGridStateKey, int] = {start_key: 0}
    env_by_index: List[object] = [copy.deepcopy(raw)]
    terminal_states: set[int] = set()
    goal_states: set[int] = set()
    transitions: Dict[Tuple[int, int], Tuple[int, float, bool]] = {}
    queue = [0]
    while queue:
        state = queue.pop(0)
        if state in terminal_states:
            continue
        raw_state = env_by_index[state]
        for action in range(int(raw.action_space.n)):
            child = copy.deepcopy(raw_state)
            _obs, reward, terminated, truncated, _info = child.step(action)
            key = _minigrid_state_key(child)
            if key not in state_to_index:
                if len(state_to_index) >= max_states:
                    env.close()
                    raise RuntimeError(f"{env_id} exceeded max_states={max_states}.")
                state_to_index[key] = len(state_to_index)
                env_by_index.append(copy.deepcopy(child))
                queue.append(state_to_index[key])
            next_state = state_to_index[key]
            done = bool(terminated or truncated)
            transitions[(state, action)] = (next_state, float(reward), done)
            if done:
                terminal_states.add(next_state)
                if float(reward) > 0.0:
                    goal_states.add(next_state)

    n_states = len(state_to_index)
    n_actions = int(raw.action_space.n)
    P = np.zeros((n_actions, n_states, n_states), dtype=float)
    R = np.zeros((n_actions, n_states), dtype=float)
    for state in range(n_states):
        for action in range(n_actions):
            if state in terminal_states:
                P[action, state, state] = 1.0
                continue
            next_state, reward, _done = transitions[(state, action)]
            P[action, state, next_state] = 1.0
            R[action, state] = reward
    P, R = make_absorbing(P, R, terminal_states)
    coords = np.zeros((n_states, 2), dtype=float)
    labels: List[str] = ["" for _ in range(n_states)]
    for key, idx in state_to_index.items():
        pos, direction, _grid_bytes, carrying = key
        coords[idx] = np.array([float(pos[1]), float(pos[0]) + 0.05 * float(direction)])
        labels[idx] = f"pos={pos},dir={direction},carry={carrying}"
    env.close()
    action_names = tuple(getattr(raw.actions(action), "name", str(action)) for action in range(n_actions))
    start_distribution = np.zeros(n_states, dtype=float)
    start_distribution[0] = 1.0
    return FiniteMDP(
        name=env_id,
        P=P,
        R=R,
        action_names=action_names,
        terminal_states=tuple(sorted(terminal_states)),
        goal_states=tuple(sorted(goal_states)),
        start_states=(0,),
        start_distribution=start_distribution,
        coords=coords,
        state_labels=tuple(labels),
        metadata={"source": "minigrid_symbolic_bfs", "env_id": env_id, "seed": seed},
    )


def _minigrid_state_key(raw: object) -> MiniGridStateKey:
    carrying_obj = getattr(raw, "carrying", None)
    carrying = None
    if carrying_obj is not None:
        carrying = (
            str(getattr(carrying_obj, "type", "")),
            str(getattr(carrying_obj, "color", "")),
            int(getattr(carrying_obj, "state", 0)),
        )
    pos_raw = getattr(raw, "agent_pos")
    pos = (int(pos_raw[0]), int(pos_raw[1]))
    return (
        pos,
        int(getattr(raw, "agent_dir")),
        raw.grid.encode().tobytes(),
        carrying,
    )


def transition_graph(mdp: FiniteMDP, threshold: float = 1e-12) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(mdp.n_states))
    for action in range(mdp.n_actions):
        src, dst = np.nonzero(mdp.P[action] > threshold)
        for s, ns in zip(src.tolist(), dst.tolist()):
            if s != ns:
                graph.add_edge(int(s), int(ns))
    return graph


def transition_digraph(mdp: FiniteMDP, threshold: float = 1e-12) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_nodes_from(range(mdp.n_states))
    for action in range(mdp.n_actions):
        src, dst = np.nonzero(mdp.P[action] > threshold)
        for s, ns in zip(src.tolist(), dst.tolist()):
            graph.add_edge(int(s), int(ns))
    return graph


def adjacency_matrix(mdp: FiniteMDP, threshold: float = 1e-12) -> np.ndarray:
    A = np.zeros((mdp.n_states, mdp.n_states), dtype=float)
    for action in range(mdp.n_actions):
        A = np.maximum(A, (mdp.P[action] > threshold).astype(float))
    np.fill_diagonal(A, 0.0)
    return np.maximum(A, A.T)


def endpoint_boundary(mdp: FiniteMDP, max_start_states: int = 16) -> List[int]:
    boundary = set(int(s) for s in mdp.terminal_states)
    starts = np.flatnonzero(mdp.start_distribution_or_uniform() > 0.0).astype(int).tolist()
    for state in starts[:max_start_states]:
        boundary.add(int(state))
    if not boundary:
        boundary.add(0)
    return sorted(boundary)


def betweenness_boundary(mdp: FiniteMDP, target_count: int) -> List[int]:
    boundary = set(endpoint_boundary(mdp))
    graph = transition_graph(mdp)
    scores = nx.betweenness_centrality(graph, normalized=True)
    ranked = sorted(range(mdp.n_states), key=lambda s: (-float(scores.get(s, 0.0)), s))
    for state in ranked:
        boundary.add(int(state))
        if len(boundary) >= target_count:
            break
    return sorted(boundary)


def spectral_boundary(mdp: FiniteMDP, target_count: int) -> List[int]:
    boundary = set(endpoint_boundary(mdp))
    if len(boundary) >= target_count:
        return sorted(boundary)
    A = adjacency_matrix(mdp)
    degree = A.sum(axis=1)
    inv_sqrt = np.zeros_like(degree)
    positive = degree > 0.0
    inv_sqrt[positive] = 1.0 / np.sqrt(degree[positive])
    L = np.eye(mdp.n_states) - inv_sqrt[:, None] * A * inv_sqrt[None, :]
    vals, vecs = eigh(L)
    order = np.argsort(vals)
    for vector_idx in order[1:]:
        vector = vecs[:, int(vector_idx)]
        for state in (int(np.argmin(vector)), int(np.argmax(vector))):
            boundary.add(state)
            if len(boundary) >= target_count:
                return sorted(boundary)
    return sorted(boundary)


def coverage_boundary(mdp: FiniteMDP, target_count: int) -> List[int]:
    boundary = set(endpoint_boundary(mdp))
    if len(boundary) >= target_count:
        return sorted(boundary)
    graph = transition_graph(mdp)
    lengths = dict(nx.all_pairs_shortest_path_length(graph))
    while len(boundary) < target_count:
        best_state = None
        best_distance = -1.0
        for state in range(mdp.n_states):
            if state in boundary:
                continue
            nearest = min(float(lengths.get(state, {}).get(b, mdp.n_states)) for b in boundary)
            if nearest > best_distance + 1e-12 or (
                abs(nearest - best_distance) <= 1e-12 and (best_state is None or state < best_state)
            ):
                best_state = state
                best_distance = nearest
        if best_state is None:
            break
        boundary.add(int(best_state))
    return sorted(boundary)


def taxi_factor_boundary(mdp: FiniteMDP) -> List[int]:
    """Taxi-specific task-variable boundary for the structured failure ablation.

    A purely spatial boundary can hide passenger/destination variables.  This
    selector keeps the states where the passenger status can change: successful
    pickup configurations, in-taxi landmark configurations, and successful
    dropoff configurations.  It is intentionally labeled Taxi-specific rather
    than a generic theorem-level selector.
    """

    if not mdp.name.startswith("Taxi") or mdp.n_states != 500:
        raise ValueError("taxi_factor_boundary only applies to Taxi-v3 style 500-state MDPs.")
    taxi_locs = ((0, 0), (0, 4), (4, 0), (4, 3))

    def encode(row: int, col: int, passenger: int, destination: int) -> int:
        return (((row * 5 + col) * 5 + passenger) * 4 + destination)

    boundary = set(endpoint_boundary(mdp))
    for passenger in range(4):
        pickup_row, pickup_col = taxi_locs[passenger]
        for destination in range(4):
            dest_row, dest_col = taxi_locs[destination]
            boundary.add(encode(pickup_row, pickup_col, passenger, destination))
            boundary.add(encode(pickup_row, pickup_col, 4, destination))
            boundary.add(encode(dest_row, dest_col, 4, destination))
            boundary.add(encode(dest_row, dest_col, destination, destination))
    return sorted(state for state in boundary if 0 <= state < mdp.n_states)


def taxi_landmark_modes_boundary(mdp: FiniteMDP) -> List[int]:
    """Stronger Taxi ablation retaining every passenger/destination mode at landmarks."""

    if not mdp.name.startswith("Taxi") or mdp.n_states != 500:
        raise ValueError("taxi_landmark_modes_boundary only applies to Taxi-v3 style 500-state MDPs.")
    taxi_locs = ((0, 0), (0, 4), (4, 0), (4, 3))

    def encode(row: int, col: int, passenger: int, destination: int) -> int:
        return (((row * 5 + col) * 5 + passenger) * 4 + destination)

    boundary = set(endpoint_boundary(mdp))
    for row, col in taxi_locs:
        for passenger in range(5):
            for destination in range(4):
                boundary.add(encode(row, col, passenger, destination))
    return sorted(state for state in boundary if 0 <= state < mdp.n_states)


def value_gradient_saliency(mdp: FiniteMDP, V: np.ndarray) -> np.ndarray:
    score = np.zeros(mdp.n_states, dtype=float)
    for state in range(mdp.n_states):
        base = float(V[state])
        diffs = []
        for action in range(mdp.n_actions):
            expected_next = float(mdp.P[action, state] @ V)
            diffs.append(abs(base - expected_next))
        score[state] = max(diffs) if diffs else 0.0
    return _normalize(score)


def transition_entropy_saliency(mdp: FiniteMDP) -> np.ndarray:
    score = np.zeros(mdp.n_states, dtype=float)
    for state in range(mdp.n_states):
        best = 0.0
        for action in range(mdp.n_actions):
            p = mdp.P[action, state]
            p = p[p > 1e-12]
            best = max(best, float(-np.sum(p * np.log(p))))
        score[state] = best
    return _normalize(score)


def _normalize(score: np.ndarray) -> np.ndarray:
    score = np.nan_to_num(score.astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    score[score < 0.0] = 0.0
    max_score = float(score.max(initial=0.0))
    if max_score > 0.0:
        score = score / max_score
    return score


def green_occupancy_boundary(
    mdp: FiniteMDP,
    target_count: int,
    gamma: float,
    V: np.ndarray,
    saliency_kind: str = "combined",
) -> List[int]:
    """Greedy generic Green-occupancy selector used for non-grid smoke tests."""

    boundary = set(endpoint_boundary(mdp))
    if len(boundary) >= target_count:
        return sorted(boundary)
    value_score = value_gradient_saliency(mdp, V)
    entropy_score = transition_entropy_saliency(mdp)
    if saliency_kind == "value_gradient":
        saliency = value_score
    elif saliency_kind == "transition_entropy":
        saliency = entropy_score
    else:
        graph = transition_graph(mdp)
        centrality = nx.betweenness_centrality(graph, normalized=True)
        bottleneck = _normalize(np.array([centrality.get(s, 0.0) for s in range(mdp.n_states)], dtype=float))
        saliency = _normalize(np.maximum.reduce([value_score, entropy_score, bottleneck]))

    while len(boundary) < target_count:
        B = sorted(boundary)
        candidate_scores = np.zeros(mdp.n_states, dtype=float)
        for action in range(mdp.n_actions):
            P_action, _r_action = mdp.transition_matrix_for_action(action)
            B_arr, interior, occupancy = discounted_interior_occupancy(P_action, B, gamma)
            if len(interior) == 0:
                continue
            boundary_weight = mdp.start_distribution_or_uniform()[B_arr]
            if boundary_weight.sum() <= 0.0:
                boundary_weight = np.full(len(B_arr), 1.0 / max(1, len(B_arr)), dtype=float)
            else:
                boundary_weight = boundary_weight / boundary_weight.sum()
            candidate_scores[interior] += boundary_weight @ occupancy
        candidate_scores *= (1.0 + saliency)
        candidate_scores[list(boundary)] = -np.inf
        next_state = int(np.argmax(candidate_scores))
        if not np.isfinite(candidate_scores[next_state]) or candidate_scores[next_state] <= 1e-12:
            break
        boundary.add(next_state)
    return sorted(boundary)


def full_value_iteration(
    mdp: FiniteMDP,
    gamma: float,
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Tuple[np.ndarray, int]:
    V = np.zeros(mdp.n_states, dtype=float)
    terminals = mdp.terminal_set()
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        q = mdp.R + gamma * np.einsum("asn,n->as", mdp.P, old)
        V = np.max(q, axis=0)
        if terminals:
            V[list(terminals)] = 0.0
        if float(np.max(np.abs(V - old))) < tol:
            return V, iteration
    return V, max_iterations


def graph_smdp_value_iteration(
    reductions: Mapping[str, BellmanKronReduction],
    terminal_positions: Sequence[int],
    tol: float = 1e-10,
    max_iterations: int = 10_000,
) -> Tuple[np.ndarray, int]:
    first = next(iter(reductions.values()))
    n_boundary = len(first.boundary)
    terminal_positions = tuple(int(pos) for pos in terminal_positions)
    V = np.zeros(n_boundary, dtype=float)
    for iteration in range(1, max_iterations + 1):
        old = V.copy()
        q_values = [red.reward + red.gamma_terminal @ old for red in reductions.values()]
        V = np.max(np.stack(q_values, axis=0), axis=0)
        if terminal_positions:
            V[list(terminal_positions)] = 0.0
        if float(np.max(np.abs(V - old))) < tol:
            return V, iteration
    return V, max_iterations


def build_smdp_reductions(mdp: FiniteMDP, boundary: Sequence[int], gamma: float) -> Dict[str, BellmanKronReduction]:
    reductions: Dict[str, BellmanKronReduction] = {}
    for action, name in enumerate(mdp.action_names):
        P_action, R_action = mdp.transition_matrix_for_action(action)
        reductions[name] = bellman_kron_reduce(P_action, R_action, boundary, gamma)
    return reductions


def build_targeted_smdp_reductions(
    mdp: FiniteMDP,
    boundary: Sequence[int],
    gamma: float,
) -> Dict[str, BellmanKronReduction]:
    reductions: Dict[str, BellmanKronReduction] = {}
    for target in sorted(set(int(state) for state in boundary)):
        P_policy, R_policy = shortest_path_target_policy_kernel(mdp, target)
        reductions[f"to_{target}"] = bellman_kron_reduce(P_policy, R_policy, boundary, gamma)
    return reductions


def shortest_path_target_policy_kernel(mdp: FiniteMDP, target: int) -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic option policy that greedily heads toward one target state.

    The policy is computed on the directed transition support graph, so it can
    use non-movement actions such as Taxi pickup/dropoff when those actions are
    required to reach a target factored state.
    """

    target = int(target)
    graph = transition_digraph(mdp)
    try:
        distances = nx.single_source_shortest_path_length(graph.reverse(copy=False), target)
    except nx.NetworkXError:
        distances = {target: 0}
    P_policy = np.zeros((mdp.n_states, mdp.n_states), dtype=float)
    R_policy = np.zeros(mdp.n_states, dtype=float)
    for state in range(mdp.n_states):
        if state == target:
            P_policy[state, state] = 1.0
            R_policy[state] = 0.0
            continue
        best_action = 0
        best_score = float("inf")
        for action in range(mdp.n_actions):
            score = 0.0
            unreachable_mass = 0.0
            for next_state, prob in enumerate(mdp.P[action, state]):
                if prob <= 1e-12:
                    continue
                dist = distances.get(next_state)
                if dist is None:
                    unreachable_mass += float(prob)
                else:
                    score += float(prob) * float(dist)
            score += unreachable_mass * float(mdp.n_states + 1)
            if score < best_score - 1e-12:
                best_score = score
                best_action = action
        P_policy[state] = mdp.P[best_action, state]
        R_policy[state] = mdp.R[best_action, state]
    return P_policy, R_policy


def lifted_graph_value(
    mdp: FiniteMDP,
    boundary: Sequence[int],
    boundary_value: np.ndarray,
    gamma: float,
) -> np.ndarray:
    boundary = sorted(set(int(s) for s in boundary))
    boundary_pos = {state: pos for pos, state in enumerate(boundary)}
    out = np.zeros(mdp.n_states, dtype=float)
    for state in boundary:
        out[state] = float(boundary_value[boundary_pos[state]])
    interior = np.array([state for state in range(mdp.n_states) if state not in boundary_pos], dtype=int)
    if len(interior) == 0:
        return out
    B = np.array(boundary, dtype=int)
    q_by_action = []
    for action in range(mdp.n_actions):
        P = mdp.P[action]
        P_II = P[np.ix_(interior, interior)]
        P_IB = P[np.ix_(interior, B)]
        rhs = mdp.R[action, interior] + gamma * P_IB @ boundary_value
        q_by_action.append(_solve_or_pinv(np.eye(len(interior)) - gamma * P_II, rhs))
    out[interior] = np.max(np.stack(q_by_action, axis=0), axis=0)
    return out


def _solve_or_pinv(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    try:
        return np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A) @ B


def evaluate_boundary_graph(
    mdp: FiniteMDP,
    boundary: Sequence[int],
    gamma: float,
    full_value: np.ndarray | None = None,
    option_mode: str = "primitive",
) -> Dict[str, object]:
    boundary = sorted(set(int(s) for s in boundary))
    if full_value is None:
        full_value, full_iterations = full_value_iteration(mdp, gamma=gamma)
    else:
        full_iterations = 0
    if option_mode == "primitive":
        reductions = build_smdp_reductions(mdp, boundary, gamma=gamma)
    elif option_mode == "boundary_targeted":
        reductions = build_targeted_smdp_reductions(mdp, boundary, gamma=gamma)
    else:
        raise ValueError(f"Unknown option_mode: {option_mode}")
    boundary_pos = {state: pos for pos, state in enumerate(boundary)}
    terminal_positions = [boundary_pos[s] for s in mdp.terminal_states if s in boundary_pos]
    V_boundary, smdp_iterations = graph_smdp_value_iteration(reductions, terminal_positions=terminal_positions)
    lifted = lifted_graph_value(mdp, boundary, V_boundary, gamma=gamma)
    start_dist = mdp.start_distribution_or_uniform()
    value_error = np.abs(full_value - lifted)
    return {
        "n_states": mdp.n_states,
        "n_actions": mdp.n_actions,
        "n_boundary": len(boundary),
        "state_compression_ratio": float(mdp.n_states / max(1, len(boundary))),
        "full_vi_iterations": int(full_iterations),
        "smdp_iterations": int(smdp_iterations),
        "start_value_full": float(start_dist @ full_value),
        "start_value_graph": float(start_dist @ lifted),
        "start_value_gap": float(abs(start_dist @ (full_value - lifted))),
        "value_gap_mean": float(start_dist @ value_error),
        "value_gap_max": float(np.max(value_error)),
        "kernel_nnz": int(sum(np.count_nonzero(red.gamma_terminal) for red in reductions.values())),
        "n_options": len(reductions),
        "option_mode": option_mode,
        "full_transition_nnz": int(np.count_nonzero(mdp.P)),
    }
