from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import networkx as nx
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from finite_mdp_adapter import FiniteMDP, transition_digraph, transition_graph


NODE_FEATURE_NAMES: Tuple[str, ...] = (
    "start_mass",
    "is_start",
    "is_goal",
    "is_terminal",
    "is_mandatory",
    "is_candidate",
    "out_degree",
    "in_degree",
    "weighted_out_degree",
    "weighted_in_degree",
    "self_loop_mean",
    "self_loop_max",
    "transition_entropy_mean",
    "transition_entropy_max",
    "reward_mean",
    "reward_max",
    "reward_std",
    "distance_from_start",
    "distance_to_goal",
    "distance_balance",
    "articulation",
    "clustering",
    "coord_0",
    "coord_1",
    "coords_available",
    "log_n_states",
    "slip",
    "gamma",
)


@dataclass(frozen=True)
class GraphBoundarySample:
    name: str
    split: str
    map_family: str
    map_size: int
    maze_seed: int
    slip: float
    node_features: np.ndarray
    edge_index: np.ndarray
    edge_weight: np.ndarray
    labels: np.ndarray
    score_targets: np.ndarray
    score_mask: np.ndarray
    eligible: np.ndarray
    mandatory: Tuple[int, ...]
    teacher_boundary: Tuple[int, ...]
    teacher_top_set: Tuple[int, ...]
    teacher_feasible: bool
    teacher_selection_time_sec: float
    teacher_row: Mapping[str, object]
    graph_encoding_time_sec: float

    @property
    def n_states(self) -> int:
        return int(self.node_features.shape[0])

    @property
    def teacher_extra(self) -> Tuple[int, ...]:
        mandatory = set(self.mandatory)
        return tuple(state for state in self.teacher_boundary if state not in mandatory)


@dataclass(frozen=True)
class TorchGraphBatch:
    x: torch.Tensor
    adjacency: torch.Tensor
    labels: torch.Tensor
    score_targets: torch.Tensor
    score_mask: torch.Tensor
    eligible: torch.Tensor
    graph_slices: Tuple[Tuple[int, int], ...]
    count_targets: torch.Tensor
    samples: Tuple[GraphBoundarySample, ...]


def _multi_source_distances(
    graph: nx.Graph | nx.DiGraph,
    sources: Sequence[int],
    n_states: int,
) -> np.ndarray:
    distance = np.full(n_states, np.inf, dtype=float)
    queue: List[int] = []
    for source in sorted(set(int(state) for state in sources)):
        if 0 <= source < n_states:
            distance[source] = 0.0
            queue.append(source)
    cursor = 0
    while cursor < len(queue):
        state = queue[cursor]
        cursor += 1
        for neighbor in graph.neighbors(state):
            neighbor = int(neighbor)
            if math.isfinite(float(distance[neighbor])):
                continue
            distance[neighbor] = distance[state] + 1.0
            queue.append(neighbor)
    return distance


def _normalize_distance(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    scale = max(1.0, float(np.max(finite, initial=0.0)))
    return np.where(np.isfinite(values), values / scale, 1.0)


def transition_graph_encoding(
    mdp: FiniteMDP,
    mandatory: Sequence[int],
    candidate_states: Sequence[int],
    slip: float,
    gamma: float,
    threshold: float = 1e-12,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Encode a finite transition graph without teacher scores or search traces."""

    n_states = mdp.n_states
    mandatory_set = set(int(state) for state in mandatory)
    candidate_set = set(int(state) for state in candidate_states) - mandatory_set
    starts = tuple(int(state) for state in mdp.start_states)
    goals = tuple(int(state) for state in (mdp.goal_states or mdp.terminal_states))
    terminals = set(int(state) for state in mdp.terminal_states)
    start_distribution = mdp.start_distribution_or_uniform()

    support_directed = np.any(mdp.P > threshold, axis=0)
    np.fill_diagonal(support_directed, False)
    out_degree = np.sum(support_directed, axis=1).astype(float)
    in_degree = np.sum(support_directed, axis=0).astype(float)

    average_transition = np.mean(mdp.P, axis=0)
    off_diagonal = average_transition.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    symmetric = 0.5 * (off_diagonal + off_diagonal.T)
    weighted_out = np.sum(off_diagonal, axis=1)
    weighted_in = np.sum(off_diagonal, axis=0)
    self_loops = np.stack(
        [np.diag(mdp.P[action]) for action in range(mdp.n_actions)],
        axis=0,
    )

    entropy = np.zeros((mdp.n_actions, n_states), dtype=float)
    for action in range(mdp.n_actions):
        probabilities = np.clip(mdp.P[action], 1e-30, 1.0)
        entropy[action] = -np.sum(
            np.where(mdp.P[action] > 0.0, mdp.P[action] * np.log(probabilities), 0.0),
            axis=1,
        )

    directed = transition_digraph(mdp, threshold=threshold)
    undirected = transition_graph(mdp, threshold=threshold)
    from_start = _normalize_distance(_multi_source_distances(directed, starts, n_states))
    to_goal = _normalize_distance(
        _multi_source_distances(directed.reverse(copy=False), goals, n_states)
    )
    articulation = set(int(state) for state in nx.articulation_points(undirected))
    clustering = nx.clustering(undirected)

    coords = np.zeros((n_states, 2), dtype=float)
    coords_available = 0.0
    if mdp.coords is not None and np.asarray(mdp.coords).shape[0] == n_states:
        raw_coords = np.asarray(mdp.coords, dtype=float)
        width = min(2, raw_coords.shape[1]) if raw_coords.ndim == 2 else 0
        if width:
            coords_available = 1.0
            coords[:, :width] = raw_coords[:, :width]
            for axis in range(width):
                low = float(np.min(coords[:, axis]))
                high = float(np.max(coords[:, axis]))
                coords[:, axis] = (coords[:, axis] - low) / max(1e-12, high - low)

    degree_scale = max(1.0, float(max(np.max(out_degree), np.max(in_degree))))
    reward = np.asarray(mdp.R, dtype=float)
    features = np.column_stack(
        [
            start_distribution,
            np.asarray([state in starts for state in range(n_states)], dtype=float),
            np.asarray([state in goals for state in range(n_states)], dtype=float),
            np.asarray([state in terminals for state in range(n_states)], dtype=float),
            np.asarray([state in mandatory_set for state in range(n_states)], dtype=float),
            np.asarray([state in candidate_set for state in range(n_states)], dtype=float),
            out_degree / degree_scale,
            in_degree / degree_scale,
            weighted_out,
            weighted_in,
            np.mean(self_loops, axis=0),
            np.max(self_loops, axis=0),
            np.mean(entropy, axis=0),
            np.max(entropy, axis=0),
            np.mean(reward, axis=0),
            np.max(reward, axis=0),
            np.std(reward, axis=0),
            from_start,
            to_goal,
            from_start - to_goal,
            np.asarray([state in articulation for state in range(n_states)], dtype=float),
            np.asarray([float(clustering.get(state, 0.0)) for state in range(n_states)]),
            coords[:, 0],
            coords[:, 1],
            np.full(n_states, coords_available, dtype=float),
            np.full(n_states, math.log1p(n_states), dtype=float),
            np.full(n_states, float(slip), dtype=float),
            np.full(n_states, float(gamma), dtype=float),
        ]
    ).astype(np.float32)
    if features.shape[1] != len(NODE_FEATURE_NAMES):
        raise AssertionError("NODE_FEATURE_NAMES does not match the graph encoding width.")

    adjacency = symmetric.copy()
    adjacency += np.eye(n_states, dtype=float)
    degree = np.sum(adjacency, axis=1)
    inverse_sqrt = np.zeros_like(degree)
    positive = degree > 0.0
    inverse_sqrt[positive] = 1.0 / np.sqrt(degree[positive])
    adjacency = inverse_sqrt[:, None] * adjacency * inverse_sqrt[None, :]
    rows, cols = np.nonzero(adjacency > 0.0)
    edge_index = np.asarray([rows, cols], dtype=np.int64)
    edge_weight = adjacency[rows, cols].astype(np.float32)
    return features, edge_index, edge_weight


def feature_normalization(
    samples: Sequence[GraphBoundarySample],
) -> Tuple[np.ndarray, np.ndarray]:
    values = np.concatenate([sample.node_features for sample in samples], axis=0)
    center = np.mean(values, axis=0).astype(np.float32)
    scale = np.std(values, axis=0).astype(np.float32)
    scale = np.where(scale > 1e-6, scale, 1.0).astype(np.float32)
    return center, scale


def collate_graphs(
    samples: Sequence[GraphBoundarySample],
    center: np.ndarray,
    scale: np.ndarray,
    device: torch.device,
    max_extra: int,
) -> TorchGraphBatch:
    offsets: List[int] = []
    slices: List[Tuple[int, int]] = []
    cursor = 0
    for sample in samples:
        offsets.append(cursor)
        slices.append((cursor, cursor + sample.n_states))
        cursor += sample.n_states
    features = np.concatenate(
        [(sample.node_features - center) / scale for sample in samples], axis=0
    ).astype(np.float32)
    labels = np.concatenate([sample.labels for sample in samples]).astype(np.float32)
    score_targets = np.concatenate([sample.score_targets for sample in samples]).astype(np.float32)
    score_mask = np.concatenate([sample.score_mask for sample in samples]).astype(bool)
    eligible = np.concatenate([sample.eligible for sample in samples]).astype(bool)
    edge_indices = []
    edge_weights = []
    for offset, sample in zip(offsets, samples):
        edge_indices.append(sample.edge_index + int(offset))
        edge_weights.append(sample.edge_weight)
    indices = np.concatenate(edge_indices, axis=1)
    weights = np.concatenate(edge_weights)
    adjacency = torch.sparse_coo_tensor(
        torch.as_tensor(indices, dtype=torch.long, device=device),
        torch.as_tensor(weights, dtype=torch.float32, device=device),
        size=(cursor, cursor),
        device=device,
    ).coalesce()
    count_targets = torch.as_tensor(
        [min(max_extra, len(sample.teacher_extra)) for sample in samples],
        dtype=torch.long,
        device=device,
    )
    return TorchGraphBatch(
        x=torch.as_tensor(features, dtype=torch.float32, device=device),
        adjacency=adjacency,
        labels=torch.as_tensor(labels, dtype=torch.float32, device=device),
        score_targets=torch.as_tensor(score_targets, dtype=torch.float32, device=device),
        score_mask=torch.as_tensor(score_mask, dtype=torch.bool, device=device),
        eligible=torch.as_tensor(eligible, dtype=torch.bool, device=device),
        graph_slices=tuple(slices),
        count_targets=count_targets,
        samples=tuple(samples),
    )


class SparseGCNBlock(nn.Module):
    def __init__(self, hidden_dim: int, dropout: float) -> None:
        super().__init__()
        self.linear = nn.Linear(hidden_dim, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, adjacency: torch.Tensor) -> torch.Tensor:
        update = torch.sparse.mm(adjacency, x)
        update = self.linear(update)
        update = self.norm(update)
        update = self.dropout(F.gelu(update))
        return x + update


class BoundaryHeatmapGNN(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 4,
        dropout: float = 0.1,
        max_extra: int = 4,
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.hidden_dim = int(hidden_dim)
        self.num_layers = int(num_layers)
        self.dropout = float(dropout)
        self.max_extra = int(max_extra)
        self.input_projection = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        self.layers = nn.ModuleList(
            [SparseGCNBlock(hidden_dim, dropout=dropout) for _ in range(num_layers)]
        )
        self.context_projection = nn.Sequential(
            nn.Linear(2 * hidden_dim, hidden_dim),
            nn.GELU(),
        )
        self.node_head = nn.Sequential(
            nn.Linear(2 * hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
        )
        self.count_head = nn.Sequential(
            nn.Linear(2 * hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, max_extra + 1),
        )

    def forward(self, batch: TorchGraphBatch) -> Tuple[torch.Tensor, torch.Tensor]:
        hidden = self.input_projection(batch.x)
        for layer in self.layers:
            hidden = layer(hidden, batch.adjacency)
        pooled = []
        contexts = []
        for start, stop in batch.graph_slices:
            graph_hidden = hidden[start:stop]
            graph_pool = torch.cat(
                [torch.mean(graph_hidden, dim=0), torch.max(graph_hidden, dim=0).values],
                dim=0,
            )
            pooled.append(graph_pool)
            contexts.append(self.context_projection(graph_pool).expand(stop - start, -1))
        pooled_tensor = torch.stack(pooled, dim=0)
        node_context = torch.cat(contexts, dim=0)
        node_logits = self.node_head(torch.cat([hidden, node_context], dim=1)).squeeze(1)
        count_logits = self.count_head(pooled_tensor)
        return node_logits, count_logits

    def config(self) -> Dict[str, object]:
        return {
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "num_layers": self.num_layers,
            "dropout": self.dropout,
            "max_extra": self.max_extra,
        }


def teacher_student_loss(
    node_logits: torch.Tensor,
    count_logits: torch.Tensor,
    batch: TorchGraphBatch,
    positive_weight: float,
    ranking_weight: float,
    count_weight: float,
    score_weight: float,
    score_temperature: float,
    ranking_margin: float,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    eligible_logits = node_logits[batch.eligible]
    eligible_labels = batch.labels[batch.eligible]
    node_loss = F.binary_cross_entropy_with_logits(
        eligible_logits,
        eligible_labels,
        pos_weight=torch.as_tensor(positive_weight, device=node_logits.device),
    )
    ranking_terms = []
    for start, stop in batch.graph_slices:
        mask = batch.eligible[start:stop]
        labels = batch.labels[start:stop]
        logits = node_logits[start:stop]
        positive = logits[mask & (labels > 0.5)]
        negative = logits[mask & (labels <= 0.5)]
        if len(positive) and len(negative):
            differences = positive[:, None] - negative[None, :]
            ranking_terms.append(F.softplus(float(ranking_margin) - differences).mean())
    ranking_loss = (
        torch.stack(ranking_terms).mean()
        if ranking_terms
        else torch.zeros((), dtype=node_logits.dtype, device=node_logits.device)
    )
    score_terms = []
    for start, stop in batch.graph_slices:
        mask = batch.eligible[start:stop] & batch.score_mask[start:stop]
        if not torch.any(mask):
            continue
        target = F.softmax(
            batch.score_targets[start:stop][mask] / max(1e-6, float(score_temperature)),
            dim=0,
        )
        prediction = F.log_softmax(node_logits[start:stop][mask], dim=0)
        score_terms.append(-(target * prediction).sum())
    score_loss = (
        torch.stack(score_terms).mean()
        if score_terms
        else torch.zeros((), dtype=node_logits.dtype, device=node_logits.device)
    )
    count_loss = F.cross_entropy(count_logits, batch.count_targets)
    total = (
        node_loss
        + float(ranking_weight) * ranking_loss
        + float(score_weight) * score_loss
        + float(count_weight) * count_loss
    )
    return total, {
        "node_loss": float(node_loss.detach().cpu()),
        "ranking_loss": float(ranking_loss.detach().cpu()),
        "score_loss": float(score_loss.detach().cpu()),
        "count_loss": float(count_loss.detach().cpu()),
        "total_loss": float(total.detach().cpu()),
    }


def select_boundary(
    sample: GraphBoundarySample,
    node_logits: np.ndarray,
    count_logits: np.ndarray,
    forced_count: int | None = None,
) -> Dict[str, object]:
    eligible_states = np.flatnonzero(sample.eligible).astype(int)
    if forced_count is None:
        count = int(np.argmax(count_logits))
    else:
        count = int(forced_count)
    count = min(max(0, count), len(eligible_states))
    ranked = sorted(
        eligible_states.tolist(),
        key=lambda state: (-float(node_logits[state]), int(state)),
    )
    selected = tuple(sorted(ranked[:count]))
    boundary = tuple(sorted(set(sample.mandatory).union(selected)))
    next_score = float(node_logits[ranked[count]]) if count < len(ranked) else float("-inf")
    last_score = float(node_logits[ranked[count - 1]]) if count else float("inf")
    return {
        "boundary": boundary,
        "selected_states": selected,
        "predicted_extra_count": count,
        "score_margin": last_score - next_score if count and math.isfinite(next_score) else float("inf"),
        "node_probabilities": 1.0 / (1.0 + np.exp(-np.clip(node_logits, -40.0, 40.0))),
    }


def boundary_metrics(
    sample: GraphBoundarySample,
    predicted_boundary: Sequence[int],
) -> Dict[str, object]:
    teacher = set(sample.teacher_boundary)
    predicted = set(int(state) for state in predicted_boundary)
    mandatory = set(sample.mandatory)
    teacher_extra = teacher - mandatory
    predicted_extra = predicted - mandatory
    intersection = teacher_extra.intersection(predicted_extra)
    top_set = set(sample.teacher_top_set)
    selected_score = max(
        (float(sample.score_targets[state]) for state in predicted_extra if sample.score_mask[state]),
        default=0.0,
    )
    top_score = max(
        (float(sample.score_targets[state]) for state in top_set if sample.score_mask[state]),
        default=0.0,
    )
    return {
        "boundary_jaccard": len(teacher.intersection(predicted)) / max(1, len(teacher.union(predicted))),
        "extra_jaccard": len(intersection) / max(1, len(teacher_extra.union(predicted_extra))),
        "extra_precision": len(intersection) / max(1, len(predicted_extra)),
        "extra_recall": len(intersection) / max(1, len(teacher_extra)),
        "exact_boundary_match": teacher == predicted,
        "count_match": len(teacher_extra) == len(predicted_extra),
        "teacher_top_set_size": len(top_set),
        "top_set_hit": bool(top_set.intersection(predicted_extra)) if top_set else False,
        "top_set_regret": max(0.0, top_score - selected_score) if top_set else float("nan"),
    }


def state_dict_to_npz(
    model: BoundaryHeatmapGNN,
    path: Path,
) -> Dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays: Dict[str, np.ndarray] = {}
    key_map: Dict[str, str] = {}
    for index, (key, value) in enumerate(model.state_dict().items()):
        array_key = f"array_{index:04d}"
        arrays[array_key] = value.detach().cpu().numpy()
        key_map[array_key] = key
    np.savez_compressed(path, **arrays)
    return key_map


def load_state_dict_npz(
    model: BoundaryHeatmapGNN,
    path: Path,
    key_map: Mapping[str, str],
) -> None:
    with np.load(path) as payload:
        state = {
            str(key_map[array_key]): torch.as_tensor(payload[array_key])
            for array_key in payload.files
        }
    model.load_state_dict(state)
