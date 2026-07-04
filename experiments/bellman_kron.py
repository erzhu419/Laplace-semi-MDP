from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
from scipy.linalg import eigh


Action = str
State = int

ACTIONS: Tuple[Action, ...] = ("N", "S", "W", "E")
DELTAS: Mapping[Action, Tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "W": (0, -1),
    "E": (0, 1),
}
OPPOSITE: Mapping[Action, Action] = {"N": "S", "S": "N", "W": "E", "E": "W"}


@dataclass(frozen=True)
class GridWorld:
    rows: Tuple[str, ...]
    step_reward: float = -1.0
    wall: str = "#"

    def __post_init__(self) -> None:
        widths = {len(r) for r in self.rows}
        if len(widths) != 1:
            raise ValueError("All grid rows must have the same width.")

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return len(self.rows[0])

    @property
    def open_cells(self) -> List[Tuple[int, int]]:
        return [
            (r, c)
            for r, row in enumerate(self.rows)
            for c, ch in enumerate(row)
            if ch != self.wall
        ]

    @property
    def n_states(self) -> int:
        return len(self.open_cells)

    def index_maps(self) -> Tuple[Dict[Tuple[int, int], State], Dict[State, Tuple[int, int]]]:
        cells = self.open_cells
        coord_to_idx = {coord: i for i, coord in enumerate(cells)}
        idx_to_coord = {i: coord for i, coord in enumerate(cells)}
        return coord_to_idx, idx_to_coord

    def char_at(self, state: State) -> str:
        _, idx_to_coord = self.index_maps()
        r, c = idx_to_coord[state]
        return self.rows[r][c]

    def symbol_states(self, symbols: Iterable[str]) -> List[State]:
        symbols = set(symbols)
        coord_to_idx, _ = self.index_maps()
        out: List[State] = []
        for coord, idx in coord_to_idx.items():
            if self.rows[coord[0]][coord[1]] in symbols:
                out.append(idx)
        return out

    def legal_actions(self, state: State) -> List[Action]:
        coord_to_idx, idx_to_coord = self.index_maps()
        r, c = idx_to_coord[state]
        legal: List[Action] = []
        for action, (dr, dc) in DELTAS.items():
            if (r + dr, c + dc) in coord_to_idx:
                legal.append(action)
        return legal

    def next_state(self, state: State, action: Action) -> State:
        coord_to_idx, idx_to_coord = self.index_maps()
        r, c = idx_to_coord[state]
        dr, dc = DELTAS[action]
        return coord_to_idx.get((r + dr, c + dc), state)


@dataclass(frozen=True)
class BellmanKronReduction:
    boundary: np.ndarray
    interior: np.ndarray
    gamma: float
    gamma_terminal: np.ndarray
    reward: np.ndarray
    laplacian: np.ndarray
    hit_probability: np.ndarray
    expected_tau: np.ndarray


def default_map() -> Tuple[str, ...]:
    return (
        "#####################",
        "#S....#.......#.....#",
        "#.###.#.#####.#.###.#",
        "#...#...#...#...#...#",
        "###.#####.#.#####.###",
        "#...#.....#.....#...#",
        "#.###.#.#####.#.###.#",
        "#.....#.......#....G#",
        "#####################",
    )


def corridor_map() -> Tuple[str, ...]:
    return (
        "#############",
        "#S.........G#",
        "#############",
    )


def open_room_map() -> Tuple[str, ...]:
    return (
        "#########",
        "#S......#",
        "#.......#",
        "#.......#",
        "#.......#",
        "#......G#",
        "#########",
    )


def four_rooms_map() -> Tuple[str, ...]:
    return (
        "#############",
        "#S....#.....#",
        "#.....#.....#",
        "#...........#",
        "#.....#.....#",
        "#.....#....G#",
        "#############",
    )


def decision_boundary_states(grid: GridWorld, keep_symbols: str = "SG") -> List[State]:
    """Keep endpoints, junctions, turns, and explicit symbolic states as graph nodes."""

    keep = set(grid.symbol_states(keep_symbols))
    boundaries: List[State] = []
    for s in range(grid.n_states):
        actions = grid.legal_actions(s)
        degree = len(actions)
        is_straight_corridor = degree == 2 and actions[0] == OPPOSITE.get(actions[1])
        if s in keep or degree != 2 or not is_straight_corridor:
            boundaries.append(s)
    return sorted(set(boundaries))


def all_boundary_states(grid: GridWorld, keep_symbols: str = "SG") -> List[State]:
    return list(range(grid.n_states))


def endpoint_boundary_states(grid: GridWorld, keep_symbols: str = "SG") -> List[State]:
    return sorted(set(grid.symbol_states(keep_symbols)))


def junction_boundary_states(grid: GridWorld, keep_symbols: str = "SG") -> List[State]:
    keep = set(grid.symbol_states(keep_symbols))
    boundaries: List[State] = []
    for s in range(grid.n_states):
        degree = len(grid.legal_actions(s))
        if s in keep or degree != 2:
            boundaries.append(s)
    return sorted(set(boundaries))


def graph_adjacency(grid: GridWorld) -> np.ndarray:
    n = grid.n_states
    A = np.zeros((n, n), dtype=float)
    for s in range(n):
        for action in grid.legal_actions(s):
            ns = grid.next_state(s, action)
            A[s, ns] = 1.0
            A[ns, s] = 1.0
    return A


def spectral_boundary_states(
    grid: GridWorld,
    keep_symbols: str = "SG",
    fraction: float = 0.35,
    n_vectors: int = 6,
) -> List[State]:
    """Select high local spectral-energy states as candidate graph landmarks."""

    n = grid.n_states
    keep = set(grid.symbol_states(keep_symbols))
    if n <= len(keep):
        return sorted(keep)
    A = graph_adjacency(grid)
    D = np.diag(A.sum(axis=1))
    L = D - A
    n_vec = max(1, min(n_vectors, n - 1))
    vals, vecs = eigh(L)
    nontrivial = vecs[:, 1 : n_vec + 1]
    lambdas = vals[1 : n_vec + 1]
    score = np.zeros(n, dtype=float)
    for s in range(n):
        for ns in np.flatnonzero(A[s] > 0):
            diff = nontrivial[s] - nontrivial[ns]
            score[s] += float(np.sum((lambdas + 1e-9) * diff * diff))
    k = max(len(keep), int(round(fraction * n)))
    chosen = set(np.argsort(score)[-k:].tolist())
    chosen.update(keep)
    return sorted(chosen)


def action_distribution(action: Action, slip: float = 0.0) -> Dict[Action, float]:
    """Directional option policy with optional uniform slippage to other actions."""

    if not 0.0 <= slip < 1.0:
        raise ValueError("slip must be in [0, 1).")
    other = [a for a in ACTIONS if a != action]
    dist = {a: slip / len(other) for a in other}
    dist[action] = 1.0 - slip
    return dist


def mix_slip(action: Action, slip: float = 0.0) -> Dict[Action, float]:
    return action_distribution(action, slip=slip)


def transition_matrix_for_direction(
    grid: GridWorld,
    action: Action,
    slip: float = 0.0,
    absorbing: Sequence[State] = (),
) -> Tuple[np.ndarray, np.ndarray]:
    """One-step primitive dynamics induced by a directional option."""

    n = grid.n_states
    absorbing_set = set(absorbing)
    P = np.zeros((n, n), dtype=float)
    r = np.full(n, grid.step_reward, dtype=float)
    dist = action_distribution(action, slip=slip)
    for s in range(n):
        if s in absorbing_set:
            P[s, s] = 1.0
            r[s] = 0.0
            continue
        for a, p in dist.items():
            ns = grid.next_state(s, a)
            P[s, ns] += p
    return P, r


PolicyFn = Callable[[State], Mapping[Action, float]]


def transition_matrix_for_policy(
    grid: GridWorld,
    policy: PolicyFn,
    absorbing: Sequence[State] = (),
) -> Tuple[np.ndarray, np.ndarray]:
    n = grid.n_states
    absorbing_set = set(absorbing)
    P = np.zeros((n, n), dtype=float)
    r = np.full(n, grid.step_reward, dtype=float)
    for s in range(n):
        if s in absorbing_set:
            P[s, s] = 1.0
            r[s] = 0.0
            continue
        dist = dict(policy(s))
        total = sum(dist.values())
        if total <= 0:
            raise ValueError(f"Policy has no mass at state {s}.")
        for a, p in dist.items():
            ns = grid.next_state(s, a)
            P[s, ns] += p / total
    return P, r


def shortest_path_policy_to_target(
    grid: GridWorld,
    target: State,
    slip: float = 0.0,
) -> PolicyFn:
    coord_to_idx, idx_to_coord = grid.index_maps()
    target_coord = idx_to_coord[target]
    distances: Dict[Tuple[int, int], int] = {target_coord: 0}
    frontier = [target_coord]
    while frontier:
        coord = frontier.pop(0)
        for dr, dc in DELTAS.values():
            prev = (coord[0] + dr, coord[1] + dc)
            if prev in coord_to_idx and prev not in distances:
                distances[prev] = distances[coord] + 1
                frontier.append(prev)

    def policy(state: State) -> Mapping[Action, float]:
        if state == target:
            return {"N": 1.0}
        r, c = idx_to_coord[state]
        best_action = "N"
        best_distance = float("inf")
        for action, (dr, dc) in DELTAS.items():
            nxt = (r + dr, c + dc)
            if nxt in coord_to_idx and distances.get(nxt, float("inf")) < best_distance:
                best_distance = distances[nxt]
                best_action = action
        return mix_slip(best_action, slip=slip)

    return policy


def _solve_or_pinv(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    try:
        return np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A) @ B


def bellman_kron_reduce(
    P: np.ndarray,
    r: np.ndarray,
    boundary: Sequence[State],
    gamma: float,
) -> BellmanKronReduction:
    """Eliminate interior states for a fixed option-induced transition matrix.

    The reduced kernel is
        Gamma = gamma P_BB + gamma^2 P_BI (I - gamma P_II)^-1 P_IB
    and the reduced reward is
        Rbar = r_B + gamma P_BI (I - gamma P_II)^-1 r_I.
    """

    n = P.shape[0]
    B = np.array(sorted(boundary), dtype=int)
    B_set = set(B.tolist())
    I = np.array([s for s in range(n) if s not in B_set], dtype=int)

    P_BB = P[np.ix_(B, B)]
    P_BI = P[np.ix_(B, I)]
    P_IB = P[np.ix_(I, B)]
    P_II = P[np.ix_(I, I)]
    r_B = r[B]
    r_I = r[I]

    if len(I) == 0:
        gamma_terminal = gamma * P_BB
        reward = r_B.copy()
        hit_probability = P_BB.copy()
        expected_tau = np.ones_like(P_BB)
    else:
        A_gamma = np.eye(len(I)) - gamma * P_II
        N_gamma_PIB = _solve_or_pinv(A_gamma, P_IB)
        gamma_terminal = gamma * P_BB + (gamma**2) * P_BI @ N_gamma_PIB
        reward = r_B + gamma * P_BI @ _solve_or_pinv(A_gamma, r_I)

        A_one = np.eye(len(I)) - P_II
        N_one_PIB = _solve_or_pinv(A_one, P_IB)
        hit_probability = P_BB + P_BI @ N_one_PIB
        N_one_PII_N_one_PIB = _solve_or_pinv(A_one, P_II @ N_one_PIB)
        dgamma_at_one = P_BB + 2.0 * P_BI @ N_one_PIB + P_BI @ N_one_PII_N_one_PIB
        expected_tau = np.divide(
            dgamma_at_one,
            hit_probability,
            out=np.full_like(dgamma_at_one, np.nan),
            where=hit_probability > 1e-12,
        )

    laplacian = np.eye(len(B)) - gamma_terminal
    return BellmanKronReduction(
        boundary=B,
        interior=I,
        gamma=gamma,
        gamma_terminal=gamma_terminal,
        reward=reward,
        laplacian=laplacian,
        hit_probability=hit_probability,
        expected_tau=expected_tau,
    )


def bellman_preservation_error(
    P: np.ndarray,
    r: np.ndarray,
    reduction: BellmanKronReduction,
    boundary_values: np.ndarray,
) -> float:
    """Compare reduced Bellman backup against the full system with fixed boundary values."""

    B = reduction.boundary
    I = reduction.interior
    gamma = reduction.gamma
    if len(I) == 0:
        full_q = r[B] + gamma * P[np.ix_(B, B)] @ boundary_values
    else:
        P_BB = P[np.ix_(B, B)]
        P_BI = P[np.ix_(B, I)]
        P_IB = P[np.ix_(I, B)]
        P_II = P[np.ix_(I, I)]
        r_I = r[I]
        V_I = _solve_or_pinv(
            np.eye(len(I)) - gamma * P_II,
            r_I + gamma * P_IB @ boundary_values,
        )
        full_q = r[B] + gamma * P_BB @ boundary_values + gamma * P_BI @ V_I
    reduced_q = reduction.reward + reduction.gamma_terminal @ boundary_values
    return float(np.max(np.abs(full_q - reduced_q)))


def smdp_value_iteration(
    reductions: Mapping[Action, BellmanKronReduction],
    goal_boundary_position: int,
    valid_actions: Mapping[Action, np.ndarray] | None = None,
    iterations: int = 10_000,
    tol: float = 1e-10,
) -> Tuple[np.ndarray, Dict[int, Action]]:
    """Solve max_o R_o + Gamma_o V on the boundary graph."""

    first = next(iter(reductions.values()))
    nB = len(first.boundary)
    V = np.zeros(nB, dtype=float)
    policy: Dict[int, Action] = {}
    for _ in range(iterations):
        old = V.copy()
        q_by_action = {}
        for action, red in reductions.items():
            q = red.reward + red.gamma_terminal @ old
            if valid_actions is not None and action in valid_actions:
                valid = np.asarray(valid_actions[action], dtype=bool)
                if valid.shape != (nB,):
                    raise ValueError(f"valid_actions[{action!r}] must have shape {(nB,)}.")
                q = q.copy()
                q[~valid] = -np.inf
            q_by_action[action] = q
        stacked = np.stack([q_by_action[a] for a in reductions], axis=0)
        best_values = stacked.max(axis=0)
        non_goal = np.ones(nB, dtype=bool)
        non_goal[goal_boundary_position] = False
        if np.any(~np.isfinite(best_values[non_goal])):
            bad = np.flatnonzero(non_goal & ~np.isfinite(best_values)).tolist()
            raise ValueError(f"No valid SMDP option available at boundary positions {bad}.")
        V = stacked.max(axis=0)
        best = stacked.argmax(axis=0)
        action_names = list(reductions.keys())
        policy = {i: action_names[int(best[i])] for i in range(nB)}
        V[goal_boundary_position] = 0.0
        policy[goal_boundary_position] = "TERMINAL"
        if np.max(np.abs(V - old)) < tol:
            break
    return V, policy


def primitive_value_iteration(
    grid: GridWorld,
    goal_state: State,
    gamma: float,
    slip: float = 0.0,
    iterations: int = 10_000,
    tol: float = 1e-10,
) -> np.ndarray:
    V = np.zeros(grid.n_states, dtype=float)
    for _ in range(iterations):
        old = V.copy()
        for s in range(grid.n_states):
            if s == goal_state:
                V[s] = 0.0
                continue
            qs = []
            for action in ACTIONS:
                dist = action_distribution(action, slip=slip)
                q = grid.step_reward
                q += gamma * sum(p * old[grid.next_state(s, a)] for a, p in dist.items())
                qs.append(q)
            V[s] = max(qs)
        if np.max(np.abs(V - old)) < tol:
            break
    return V


def edge_table(
    reductions: Mapping[Action, BellmanKronReduction],
    grid: GridWorld,
    min_hit_probability: float = 1e-8,
) -> List[Dict[str, object]]:
    _, idx_to_coord = grid.index_maps()
    rows: List[Dict[str, object]] = []
    for action, red in reductions.items():
        for i, src in enumerate(red.boundary):
            for j, dst in enumerate(red.boundary):
                prob = red.hit_probability[i, j]
                if prob <= min_hit_probability:
                    continue
                rows.append(
                    {
                        "src_state": int(src),
                        "dst_state": int(dst),
                        "src": idx_to_coord[int(src)],
                        "dst": idx_to_coord[int(dst)],
                        "option": action,
                        "hit_probability": float(prob),
                        "gamma_terminal": float(red.gamma_terminal[i, j]),
                        "expected_tau": float(red.expected_tau[i, j]),
                        "reward": float(red.reward[i]),
                    }
                )
    return rows


def boundary_signature(reductions: Mapping[Action, BellmanKronReduction]) -> np.ndarray:
    parts = []
    for red in reductions.values():
        parts.append(red.reward[:, None])
        parts.append(red.gamma_terminal)
        parts.append(np.nan_to_num(red.expected_tau, nan=0.0))
    return np.concatenate(parts, axis=1)


def merge_by_signature(signatures: np.ndarray, threshold: float) -> List[List[int]]:
    parent = list(range(len(signatures)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            if np.linalg.norm(signatures[i] - signatures[j]) <= threshold:
                union(i, j)
    groups: Dict[int, List[int]] = {}
    for i in range(len(signatures)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())
