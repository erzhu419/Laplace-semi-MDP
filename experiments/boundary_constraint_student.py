from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


GROUP_NAMES: Tuple[str, ...] = ("topology", "value", "stochastic")
PROPOSAL_KINDS: Tuple[str, ...] = (
    "learned_count",
    "top1",
    "top2",
    "top3",
    "nearest_start",
)


class BoundaryConstraintHead(nn.Module):
    """Multi-head downstream-risk predictor over a frozen graph encoding."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        dropout: float = 0.1,
        n_groups: int = len(GROUP_NAMES),
    ) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.hidden_dim = int(hidden_dim)
        self.dropout = float(dropout)
        self.n_groups = int(n_groups)
        self.trunk = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.group_margin_head = nn.Linear(hidden_dim, n_groups)
        self.group_failure_head = nn.Linear(hidden_dim, n_groups)
        self.gap_head = nn.Linear(hidden_dim, 1)
        self.joint_failure_head = nn.Linear(hidden_dim, 1)

    def forward(self, features: torch.Tensor) -> Dict[str, torch.Tensor]:
        hidden = self.trunk(features)
        return {
            "group_margin": F.softplus(self.group_margin_head(hidden)),
            "group_failure_logit": self.group_failure_head(hidden),
            "gap": F.softplus(self.gap_head(hidden)).squeeze(1),
            "joint_failure_logit": self.joint_failure_head(hidden).squeeze(1),
        }

    def config(self) -> Dict[str, object]:
        return {
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "dropout": self.dropout,
            "n_groups": self.n_groups,
        }


def _weighted_mean(values: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
    while weights.ndim < values.ndim:
        weights = weights.unsqueeze(-1)
    expanded = weights.expand_as(values)
    return torch.sum(values * expanded) / torch.clamp(torch.sum(expanded), min=1e-12)


def asymmetric_regression_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    sample_weights: torch.Tensor | None = None,
    underestimation_weight: float = 4.0,
) -> torch.Tensor:
    """Smooth regression plus an extra penalty when risk is underestimated."""

    base = F.smooth_l1_loss(prediction, target, reduction="none")
    under = torch.square(torch.relu(target - prediction))
    values = base + float(underestimation_weight) * under
    if sample_weights is None:
        return values.mean()
    return _weighted_mean(values, sample_weights)


def context_ranking_loss(
    risk_logits: torch.Tensor,
    failure_labels: torch.Tensor,
    context_ids: torch.Tensor,
    margin: float = 0.25,
) -> torch.Tensor:
    terms: List[torch.Tensor] = []
    for context_id in torch.unique(context_ids):
        mask = context_ids == context_id
        passing = risk_logits[mask & (failure_labels < 0.5)]
        failing = risk_logits[mask & (failure_labels > 0.5)]
        if len(passing) and len(failing):
            differences = failing[:, None] - passing[None, :]
            terms.append(F.softplus(float(margin) - differences).mean())
    if not terms:
        return torch.zeros((), dtype=risk_logits.dtype, device=risk_logits.device)
    return torch.stack(terms).mean()


def constraint_student_loss(
    outputs: Mapping[str, torch.Tensor],
    targets: Mapping[str, torch.Tensor],
    sample_weights: torch.Tensor,
    context_ids: torch.Tensor,
    group_positive_weights: torch.Tensor,
    joint_positive_weight: torch.Tensor,
    underestimation_weight: float = 4.0,
    ranking_weight: float = 0.5,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    group_margin_loss = asymmetric_regression_loss(
        outputs["group_margin"],
        targets["group_margin"],
        sample_weights,
        underestimation_weight=underestimation_weight,
    )
    gap_loss = asymmetric_regression_loss(
        outputs["gap"],
        targets["gap"],
        sample_weights,
        underestimation_weight=underestimation_weight,
    )
    group_bce_values = F.binary_cross_entropy_with_logits(
        outputs["group_failure_logit"],
        targets["group_failure"],
        pos_weight=group_positive_weights,
        reduction="none",
    )
    group_bce = _weighted_mean(group_bce_values, sample_weights)
    joint_bce_values = F.binary_cross_entropy_with_logits(
        outputs["joint_failure_logit"],
        targets["joint_failure"],
        pos_weight=joint_positive_weight,
        reduction="none",
    )
    joint_bce = _weighted_mean(joint_bce_values, sample_weights)
    ranking = context_ranking_loss(
        outputs["joint_failure_logit"],
        targets["joint_failure"],
        context_ids,
    )
    total = (
        group_margin_loss
        + gap_loss
        + 1.5 * group_bce
        + 2.0 * joint_bce
        + float(ranking_weight) * ranking
    )
    return total, {
        "group_margin_loss": float(group_margin_loss.detach().cpu()),
        "gap_loss": float(gap_loss.detach().cpu()),
        "group_bce": float(group_bce.detach().cpu()),
        "joint_bce": float(joint_bce.detach().cpu()),
        "ranking_loss": float(ranking.detach().cpu()),
        "total_loss": float(total.detach().cpu()),
    }


def merge_duplicate_proposals(
    rows: Sequence[Mapping[str, object]],
) -> Tuple[List[Dict[str, object]], int]:
    """Deduplicate proposal boundaries while retaining all proposal aliases."""

    merged: Dict[Tuple[int, ...], Dict[str, object]] = {}
    dropped = 0
    for raw in rows:
        row = dict(raw)
        boundary = tuple(sorted(int(state) for state in json.loads(str(row["predicted_boundary"]))))
        existing = merged.get(boundary)
        aliases = json.loads(str(row.get("proposal_aliases", "[]")))
        if not aliases:
            aliases = [str(row.get("proposal_kind", ""))]
        if existing is None:
            row["predicted_boundary"] = json.dumps(boundary)
            row["proposal_aliases"] = json.dumps(list(dict.fromkeys(aliases)))
            merged[boundary] = row
            continue
        previous = json.loads(str(existing.get("proposal_aliases", "[]")))
        existing["proposal_aliases"] = json.dumps(list(dict.fromkeys(previous + aliases)))
        dropped += 1
    return list(merged.values()), dropped


def topology_holdout_maps(
    rows: Sequence[Mapping[str, object]],
    holdout_fraction: float = 0.2,
    seed: int = 2027,
    failure_field: str = "joint_failure",
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """Make a deterministic map-level split so every slip stays together."""

    labels: Dict[str, List[bool]] = defaultdict(list)
    for row in rows:
        map_name = str(row["map"])
        value = row.get(failure_field, False)
        failed = bool(value) if isinstance(value, bool) else str(value).lower() in {
            "1",
            "true",
            "yes",
        }
        labels[map_name].append(failed)
    strata: Dict[str, List[str]] = defaultdict(list)
    for map_name, outcomes in labels.items():
        if all(outcomes):
            stratum = "all_fail"
        elif any(outcomes):
            stratum = "mixed"
        else:
            stratum = "all_pass"
        strata[stratum].append(map_name)
    holdout: set[str] = set()
    for stratum, maps in sorted(strata.items()):
        ordered = sorted(
            maps,
            key=lambda name: hashlib.sha256(
                f"{seed}:{stratum}:{name}".encode("utf-8")
            ).hexdigest(),
        )
        if len(ordered) <= 1:
            continue
        count = min(
            len(ordered) - 1,
            max(1, int(round(float(holdout_fraction) * len(ordered)))),
        )
        holdout.update(ordered[:count])
    all_maps = set(labels)
    if not holdout and len(all_maps) > 1:
        holdout.add(sorted(all_maps)[-1])
    training = tuple(sorted(all_maps - holdout))
    return training, tuple(sorted(holdout))


def choose_candidate_indices(
    context_keys: Sequence[Tuple[str, str]],
    risks: Sequence[float],
    boundary_sizes: Sequence[int],
    methods: Sequence[str],
) -> List[int]:
    """Choose one proposal per context with deterministic conservative ties."""

    grouped: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for index, key in enumerate(context_keys):
        grouped[key].append(index)
    selected = []
    for key in sorted(grouped):
        selected.append(
            min(
                grouped[key],
                key=lambda index: (
                    float(risks[index]),
                    int(boundary_sizes[index]),
                    str(methods[index]),
                    int(index),
                ),
            )
        )
    return selected


def tie_aware_auc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    positives = [float(score) for score, label in zip(scores, labels) if label]
    negatives = [float(score) for score, label in zip(scores, labels) if not label]
    if not positives or not negatives:
        return float("nan")
    wins = 0.0
    for positive in positives:
        for negative in negatives:
            wins += 1.0 if positive > negative else 0.5 if positive == negative else 0.0
    return wins / (len(positives) * len(negatives))


def positive_class_weights(labels: np.ndarray) -> np.ndarray:
    labels = np.asarray(labels, dtype=float)
    positives = np.sum(labels > 0.5, axis=0)
    negatives = labels.shape[0] - positives
    return np.clip(negatives / np.maximum(1.0, positives), 0.25, 20.0).astype(np.float32)


def finite_number(value: object, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default
