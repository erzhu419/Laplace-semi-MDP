from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Mapping, Sequence, Tuple

import networkx as nx
import numpy as np

from bellman_kron import GridWorld, endpoint_boundary_states, graph_nx
from one_shot_rd_operator import _turn_articulation_mask, grid_neighbors


HORIZON_FEATURE_NAMES: Tuple[str, ...] = (
    "log_n_states",
    "sqrt_n_states",
    "open_density",
    "log_aspect_ratio",
    "mean_degree",
    "degree_std",
    "dead_end_fraction",
    "junction_fraction",
    "turn_articulation_fraction",
    "articulation_fraction",
    "cycle_rank_per_state",
    "endpoint_distance",
    "endpoint_eccentricity",
    "covering_radius",
    "slip",
    "slip_endpoint_distance",
    "discount_horizon",
)


def _distances(neighbors: Sequence[Sequence[int]], source: int) -> np.ndarray:
    distance = np.full(len(neighbors), np.inf, dtype=float)
    distance[int(source)] = 0.0
    queue = [int(source)]
    cursor = 0
    while cursor < len(queue):
        state = queue[cursor]
        cursor += 1
        for neighbor in neighbors[state]:
            if math.isfinite(float(distance[int(neighbor)])):
                continue
            distance[int(neighbor)] = distance[state] + 1.0
            queue.append(int(neighbor))
    return distance


def graph_horizon_features(
    grid: GridWorld,
    slip: float,
    gamma: float,
    mandatory_boundary: Sequence[int] | None = None,
) -> Dict[str, float]:
    """Cheap graph summaries used by the first trainable horizon baseline."""

    mandatory = tuple(sorted(set(mandatory_boundary or endpoint_boundary_states(grid))))
    neighbors = grid_neighbors(grid)
    degree = np.asarray([len(adjacent) for adjacent in neighbors], dtype=float)
    graph = graph_nx(grid)
    articulation = set(int(state) for state in nx.articulation_points(graph))
    turn_mask = _turn_articulation_mask(grid)
    distances = [_distances(neighbors, state) for state in mandatory]
    finite_eccentricities = [
        float(np.max(distance[np.isfinite(distance)], initial=0.0)) for distance in distances
    ]
    endpoint_distance = 0.0
    for left_pos, left in enumerate(mandatory):
        for right in mandatory[left_pos + 1 :]:
            value = distances[left_pos][int(right)]
            if math.isfinite(float(value)):
                endpoint_distance = max(endpoint_distance, float(value))
    if distances:
        stacked = np.stack(distances, axis=0)
        nearest = np.min(stacked, axis=0)
        covering_radius = float(np.max(nearest[np.isfinite(nearest)], initial=0.0))
    else:
        covering_radius = 0.0
    n_states = max(1, grid.n_states)
    n_edges = int(graph.number_of_edges())
    n_components = int(nx.number_connected_components(graph))
    cycle_rank = max(0, n_edges - grid.n_states + n_components)
    aspect_ratio = max(grid.height, grid.width) / max(1, min(grid.height, grid.width))
    discount_horizon = 1.0 / max(1e-9, 1.0 - float(gamma))
    return {
        "log_n_states": math.log1p(grid.n_states),
        "sqrt_n_states": math.sqrt(grid.n_states),
        "open_density": grid.n_states / max(1, grid.height * grid.width),
        "log_aspect_ratio": math.log(max(1.0, aspect_ratio)),
        "mean_degree": float(np.mean(degree)) if len(degree) else 0.0,
        "degree_std": float(np.std(degree)) if len(degree) else 0.0,
        "dead_end_fraction": float(np.mean(degree <= 1.0)) if len(degree) else 0.0,
        "junction_fraction": float(np.mean(degree >= 3.0)) if len(degree) else 0.0,
        "turn_articulation_fraction": float(np.mean(turn_mask)) if len(turn_mask) else 0.0,
        "articulation_fraction": len(articulation) / n_states,
        "cycle_rank_per_state": cycle_rank / n_states,
        "endpoint_distance": endpoint_distance,
        "endpoint_eccentricity": max(finite_eccentricities, default=0.0),
        "covering_radius": covering_radius,
        "slip": float(slip),
        "slip_endpoint_distance": float(slip) * endpoint_distance,
        "discount_horizon": discount_horizon,
    }


def feature_vector(features: Mapping[str, float]) -> np.ndarray:
    return np.asarray([float(features[name]) for name in HORIZON_FEATURE_NAMES], dtype=float)


def _higher_quantile(values: np.ndarray, quantile: float) -> float:
    if len(values) == 0:
        return 0.0
    ordered = np.sort(np.asarray(values, dtype=float))
    index = int(math.ceil(float(quantile) * len(ordered)) - 1)
    return float(ordered[min(max(index, 0), len(ordered) - 1)])


@dataclass(frozen=True)
class ConservativeHorizonRegressor:
    """Ridge proposal plus a split-conformal upper residual correction."""

    feature_names: Tuple[str, ...]
    center: np.ndarray
    scale: np.ndarray
    coefficients: np.ndarray
    intercept: float
    upper_residual: float
    min_steps: int
    max_steps: int
    coverage: float

    @classmethod
    def fit(
        cls,
        train_features: np.ndarray,
        train_targets: np.ndarray,
        calibration_features: np.ndarray,
        calibration_targets: np.ndarray,
        ridge: float = 1e-3,
        coverage: float = 0.95,
        min_steps: int = 0,
        max_steps: int = 512,
    ) -> "ConservativeHorizonRegressor":
        train_features = np.asarray(train_features, dtype=float)
        train_targets = np.asarray(train_targets, dtype=float)
        calibration_features = np.asarray(calibration_features, dtype=float)
        calibration_targets = np.asarray(calibration_targets, dtype=float)
        if train_features.ndim != 2 or len(train_features) == 0:
            raise ValueError("At least one two-dimensional training feature row is required.")
        if train_features.shape[1] != len(HORIZON_FEATURE_NAMES):
            raise ValueError("Training feature width does not match HORIZON_FEATURE_NAMES.")
        center = np.mean(train_features, axis=0)
        scale = np.std(train_features, axis=0)
        scale = np.where(scale > 1e-12, scale, 1.0)
        standardized = (train_features - center) / scale
        design = np.column_stack([np.ones(len(standardized)), standardized])
        penalty = np.eye(design.shape[1], dtype=float)
        penalty[0, 0] = 0.0
        solution = np.linalg.solve(
            design.T @ design + float(ridge) * penalty,
            design.T @ train_targets,
        )
        intercept = float(solution[0])
        coefficients = np.asarray(solution[1:], dtype=float)
        if len(calibration_features):
            calibration_prediction = (
                (calibration_features - center) / scale
            ) @ coefficients + intercept
            upper_residual = max(
                0.0,
                _higher_quantile(calibration_targets - calibration_prediction, coverage),
            )
        else:
            upper_residual = 0.0
        return cls(
            feature_names=HORIZON_FEATURE_NAMES,
            center=center,
            scale=scale,
            coefficients=coefficients,
            intercept=intercept,
            upper_residual=float(upper_residual),
            min_steps=int(min_steps),
            max_steps=int(max_steps),
            coverage=float(coverage),
        )

    def predict_base(self, features: Mapping[str, float]) -> float:
        values = feature_vector(features)
        return float(((values - self.center) / self.scale) @ self.coefficients + self.intercept)

    def predict(self, features: Mapping[str, float], conservative: bool = True) -> int:
        # An empty structural universe triggers the operator's exact early exit.
        if float(features.get("turn_articulation_fraction", 0.0)) <= 0.0:
            return 0
        prediction = self.predict_base(features)
        if conservative:
            prediction += self.upper_residual
        return min(self.max_steps, max(self.min_steps, int(math.ceil(prediction))))

    def to_dict(self) -> Dict[str, object]:
        return {
            "feature_names": list(self.feature_names),
            "center": self.center.tolist(),
            "scale": self.scale.tolist(),
            "coefficients": self.coefficients.tolist(),
            "intercept": self.intercept,
            "upper_residual": self.upper_residual,
            "min_steps": self.min_steps,
            "max_steps": self.max_steps,
            "coverage": self.coverage,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ConservativeHorizonRegressor":
        return cls(
            feature_names=tuple(str(name) for name in payload["feature_names"]),  # type: ignore[index]
            center=np.asarray(payload["center"], dtype=float),  # type: ignore[arg-type]
            scale=np.asarray(payload["scale"], dtype=float),  # type: ignore[arg-type]
            coefficients=np.asarray(payload["coefficients"], dtype=float),  # type: ignore[arg-type]
            intercept=float(payload["intercept"]),  # type: ignore[arg-type]
            upper_residual=float(payload["upper_residual"]),  # type: ignore[arg-type]
            min_steps=int(payload["min_steps"]),  # type: ignore[arg-type]
            max_steps=int(payload["max_steps"]),  # type: ignore[arg-type]
            coverage=float(payload["coverage"]),  # type: ignore[arg-type]
        )
