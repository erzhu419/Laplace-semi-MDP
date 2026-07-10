#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import write_csv_all_fields


def read_rows(path: Path) -> List[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def joint_pass(
    row: Mapping[str, object],
    prefix: str,
    max_normalized_gap: float,
) -> bool:
    return parse_bool(row.get(f"{prefix}_group_all_feasible")) and abs(
        finite_float(row.get(f"{prefix}_normalized_start_gap"), float("inf"))
    ) <= float(max_normalized_gap)


def contingency_counts(
    rows: Sequence[Mapping[str, object]],
    max_normalized_gap: float,
) -> Dict[str, int]:
    counts = {
        "both_pass": 0,
        "reranker_only": 0,
        "reference_only": 0,
        "both_fail": 0,
    }
    for row in rows:
        reranker = joint_pass(row, "student", max_normalized_gap)
        reference = joint_pass(row, "teacher", max_normalized_gap)
        if reranker and reference:
            counts["both_pass"] += 1
        elif reranker:
            counts["reranker_only"] += 1
        elif reference:
            counts["reference_only"] += 1
        else:
            counts["both_fail"] += 1
    return counts


def exact_mcnemar_pvalue(reranker_only: int, reference_only: int) -> float:
    """Two-sided exact conditional McNemar test over discordant pairs."""

    discordant = int(reranker_only) + int(reference_only)
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, index)
        for index in range(min(int(reranker_only), int(reference_only)) + 1)
    ) / (2.0**discordant)
    return min(1.0, 2.0 * tail)


def paired_bootstrap_interval(
    differences: np.ndarray,
    confidence: float,
    n_resamples: int,
    seed: int,
) -> Tuple[float, float]:
    if differences.ndim != 1 or len(differences) == 0:
        raise ValueError("Paired differences must be a nonempty vector.")
    rng = np.random.default_rng(seed)
    chunk_size = min(20_000, max(1, n_resamples))
    means = []
    remaining = int(n_resamples)
    while remaining:
        count = min(chunk_size, remaining)
        indices = rng.integers(0, len(differences), size=(count, len(differences)))
        means.append(np.mean(differences[indices], axis=1))
        remaining -= count
    values = np.concatenate(means)
    alpha = 1.0 - float(confidence)
    low, high = np.quantile(values, [alpha / 2.0, 1.0 - alpha / 2.0])
    return float(low), float(high)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paired descriptive comparison of the reranker and adaptive RD reference."
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_constraint_student/selected_test_downstream.csv"
        ),
    )
    parser.add_argument("--max-normalized-gap", type=float, default=0.01)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--bootstrap-resamples", type=int, default=100_000)
    parser.add_argument("--bootstrap-seed", type=int, default=2027)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_constraint_pairing"),
    )
    args = parser.parse_args()
    if not 0.0 < args.confidence < 1.0:
        raise ValueError("--confidence must be in (0, 1).")
    if args.bootstrap_resamples <= 0:
        raise ValueError("--bootstrap-resamples must be positive.")

    rows = read_rows(args.input_csv)
    counts = contingency_counts(rows, args.max_normalized_gap)
    reranker_passes = counts["both_pass"] + counts["reranker_only"]
    reference_passes = counts["both_pass"] + counts["reference_only"]
    differences = np.asarray(
        [
            float(joint_pass(row, "student", args.max_normalized_gap))
            - float(joint_pass(row, "teacher", args.max_normalized_gap))
            for row in rows
        ],
        dtype=float,
    )
    ci_low, ci_high = paired_bootstrap_interval(
        differences,
        confidence=args.confidence,
        n_resamples=args.bootstrap_resamples,
        seed=args.bootstrap_seed,
    )
    pvalue = exact_mcnemar_pvalue(
        counts["reranker_only"], counts["reference_only"]
    )
    contingency = [
        {
            "reranker_outcome": "pass",
            "adaptive_reference_pass": counts["both_pass"],
            "adaptive_reference_fail": counts["reranker_only"],
        },
        {
            "reranker_outcome": "fail",
            "adaptive_reference_pass": counts["reference_only"],
            "adaptive_reference_fail": counts["both_fail"],
        },
    ]
    summary = {
        "n_pairs": len(rows),
        "reranker_joint_passes": reranker_passes,
        "adaptive_reference_joint_passes": reference_passes,
        **counts,
        "discordant_pairs": counts["reranker_only"] + counts["reference_only"],
        "paired_pass_rate_difference": float(np.mean(differences)),
        "paired_bootstrap_confidence": args.confidence,
        "paired_bootstrap_ci_low": ci_low,
        "paired_bootstrap_ci_high": ci_high,
        "paired_bootstrap_resamples": args.bootstrap_resamples,
        "paired_bootstrap_seed": args.bootstrap_seed,
        "exact_mcnemar_pvalue": pvalue,
        "comparison_status": "descriptive_different_objectives_and_guarantees",
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "paired_contingency.csv", contingency)
    write_csv_all_fields(args.out_dir / "paired_summary.csv", [summary])
    (args.out_dir / "paired_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Constraint-Aware Reranker Pairing",
        "",
        markdown_table(contingency, list(contingency[0])),
        "",
        markdown_table([summary], list(summary)),
        "",
        "This comparison is descriptive because the adaptive RD reference and the reranker optimize different objectives and provide different acceptance guarantees. The paired bootstrap interval and exact McNemar test quantify sample uncertainty; neither is used to claim learned-method superiority.",
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
