#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from bellman_kron import GridWorld
from compression_experiment_utils import parse_map_specs
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_rd_multiprobe_basis import (
    aggregate_probe_metrics,
    evaluate_probe,
    fixed_basis,
    json_default,
    select_boundary,
    write_csv,
)


def unique_ordered(items: Sequence[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def parse_group_specs(specs: Sequence[str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Lens group must have form name:probe,probe: {spec!r}")
        name, raw_probes = spec.split(":", 1)
        probes = [probe.strip() for probe in raw_probes.split(",") if probe.strip()]
        if not probes:
            raise ValueError(f"Lens group {name!r} has no probes.")
        groups[name.strip()] = unique_ordered(probes)
    return groups


def probe_groups_for_train(train_probes: Sequence[str], groups: Dict[str, List[str]]) -> List[str]:
    present: List[str] = []
    train_set = set(train_probes)
    for group_name, probes in groups.items():
        if train_set.intersection(probes):
            present.append(group_name)
    return present


def probe_group_map(groups: Dict[str, List[str]], extra_test_probes: Sequence[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for group_name, probes in groups.items():
        for probe in probes:
            out[probe] = group_name
    for probe in extra_test_probes:
        out.setdefault(probe, "extra")
    return out


def build_train_specs(
    groups: Dict[str, List[str]],
    extra_test_probes: Sequence[str],
    max_stratified_sets: int,
) -> List[Dict[str, object]]:
    grouped_probes = unique_ordered([probe for probes in groups.values() for probe in probes])
    all_probes = unique_ordered(grouped_probes + list(extra_test_probes))
    specs: List[Dict[str, object]] = []

    for heldout_probe in all_probes:
        train_probes = [probe for probe in all_probes if probe != heldout_probe]
        specs.append(
            {
                "protocol": "leave_one_lens_out",
                "heldout_probe": heldout_probe,
                "train_probes": train_probes,
                "test_probes": [heldout_probe],
            }
        )

    group_items = list(groups.items())
    for combo_index, combo in enumerate(itertools.product(*[probes for _name, probes in group_items])):
        if combo_index >= max_stratified_sets:
            break
        train_probes = unique_ordered(list(combo))
        test_probes = [probe for probe in all_probes if probe not in set(train_probes)]
        specs.append(
            {
                "protocol": "stratified_one_per_group",
                "heldout_probe": "multi",
                "train_probes": train_probes,
                "test_probes": test_probes,
            }
        )
    return specs


def evaluate_split(
    map_label: str,
    map_rows: Tuple[str, ...],
    recipe: Dict[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    train_probes: Sequence[str],
    test_probes: Sequence[str],
    gamma: float,
    slip: float,
    edge_weight: str,
    probe_top_fraction: float,
    cvar_alpha: float,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    eval_rows: List[Dict[str, object]] = []
    train_bits: List[float] = []
    test_bits: List[float] = []
    start_gaps: List[float] = []
    for split_name, probes, bucket in [
        ("train", train_probes, train_bits),
        ("test", test_probes, test_bits),
    ]:
        for probe in probes:
            metrics = evaluate_probe(
                map_name=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                probe=probe,
                gamma=gamma,
                slip=slip,
                edge_weight=edge_weight,
                probe_top_fraction=probe_top_fraction,
            )
            bucket.append(float(metrics["hidden_bits"]))
            if math.isfinite(float(metrics["start_gap"])):
                start_gaps.append(float(metrics["start_gap"]))
            eval_rows.append(
                {
                    "map": map_label,
                    "split": split_name,
                    "probe": probe,
                    "n_basis": len(basis),
                    "n_boundary": len(boundary),
                    "boundary": list(boundary),
                    **metrics,
                }
            )
    summary = {
        **aggregate_probe_metrics("train_bits", train_bits, cvar_alpha),
        **aggregate_probe_metrics("test_bits", test_bits, cvar_alpha),
        "test_minus_train_mean": (
            float(np.mean(test_bits)) - float(np.mean(train_bits))
            if train_bits and test_bits
            else 0.0
        ),
        "start_gap_mean": float(np.mean(start_gaps)) if start_gaps else 0.0,
        "start_gap_max": max(start_gaps) if start_gaps else 0.0,
    }
    return summary, eval_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leave-one-lens-out and stratified probe validation for fixed-basis multi-probe RD."
    )
    parser.add_argument("--map-specs", nargs="+", default=["maze:9", "four_rooms:9", "open_room:7"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument(
        "--lens-groups",
        nargs="+",
        default=[
            "topology:junction,bottleneck,turn_articulation,betweenness",
            "value:value_gradient",
            "stochastic:transition_entropy",
        ],
    )
    parser.add_argument("--extra-test-probes", nargs="+", default=["combined"])
    parser.add_argument("--risk-kinds", nargs="+", default=["mean_cvar", "max", "group_mean_cvar", "group_max_cvar"])
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--max-stratified-sets", type=int, default=4)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument("--cvar-eta", type=float, default=0.5)
    parser.add_argument("--smooth-tau", type=float, default=1.0)
    parser.add_argument(
        "--edge-weight",
        choices=["occupancy", "uniform", "occupancy_or_uniform"],
        default="occupancy_or_uniform",
    )
    parser.add_argument("--max-splits", type=int, default=3)
    parser.add_argument("--greedy-positive-only", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/rd_lens_validation"))
    args = parser.parse_args()

    groups = parse_group_specs(args.lens_groups)
    group_by_probe = probe_group_map(groups, args.extra_test_probes)
    train_specs = build_train_specs(
        groups,
        extra_test_probes=args.extra_test_probes,
        max_stratified_sets=args.max_stratified_sets,
    )
    recipe = dict(LEARNED_RECIPES[args.recipe])
    summary_rows: List[Dict[str, object]] = []
    eval_rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []
    started = time.perf_counter()

    for _family, _size, map_label, map_rows in parse_map_specs(args.map_specs):
        grid = GridWorld(map_rows)
        basis = fixed_basis(
            map_label,
            grid=grid,
            kinds=args.fixed_basis_kinds,
            gamma=args.gamma,
            slip=args.slip,
            top_fraction=args.probe_top_fraction,
            random_count=args.fixed_random_count,
        )
        for spec_index, spec in enumerate(train_specs):
            train_probes = list(spec["train_probes"])  # type: ignore[arg-type]
            test_probes = list(spec["test_probes"])  # type: ignore[arg-type]
            train_groups = probe_groups_for_train(train_probes, groups)
            for risk_kind in args.risk_kinds:
                boundary, trace, _candidates, selection_time = select_boundary(
                    map_name=map_label,
                    rows=map_rows,
                    recipe=recipe,
                    basis=basis,
                    train_probes=train_probes,
                    gamma=args.gamma,
                    slip=args.slip,
                    lambda_struct=args.lambda_struct,
                    edge_weight=args.edge_weight,
                    probe_top_fraction=args.probe_top_fraction,
                    risk_kind=risk_kind,
                    cvar_alpha=args.cvar_alpha,
                    cvar_eta=args.cvar_eta,
                    smooth_tau=args.smooth_tau,
                    max_splits=args.max_splits,
                    greedy_positive_only=args.greedy_positive_only,
                    probe_groups=group_by_probe,
                )
                metric_summary, metric_rows = evaluate_split(
                    map_label=map_label,
                    map_rows=map_rows,
                    recipe=recipe,
                    basis=basis,
                    boundary=boundary,
                    train_probes=train_probes,
                    test_probes=test_probes,
                    gamma=args.gamma,
                    slip=args.slip,
                    edge_weight=args.edge_weight,
                    probe_top_fraction=args.probe_top_fraction,
                    cvar_alpha=args.cvar_alpha,
                )
                summary_rows.append(
                    {
                        "map": map_label,
                        "spec_index": spec_index,
                        "protocol": spec["protocol"],
                        "heldout_probe": spec["heldout_probe"],
                        "risk_kind": risk_kind,
                        "train_probes": train_probes,
                        "test_probes": test_probes,
                        "train_groups": train_groups,
                        "n_train_groups": len(train_groups),
                        "n_basis": len(basis),
                        "n_boundary": len(boundary),
                        "selection_time_sec": selection_time,
                        "boundary": list(boundary),
                        **metric_summary,
                    }
                )
                for row in metric_rows:
                    eval_rows.append(
                        {
                            "spec_index": spec_index,
                            "protocol": spec["protocol"],
                            "heldout_probe": spec["heldout_probe"],
                            "risk_kind": risk_kind,
                            "train_probes": train_probes,
                            "test_probes": test_probes,
                            **row,
                        }
                    )
                for row in trace:
                    trace_rows.append(
                        {
                            "spec_index": spec_index,
                            "protocol": spec["protocol"],
                            "heldout_probe": spec["heldout_probe"],
                            "risk_kind": risk_kind,
                            "train_probes": train_probes,
                            "test_probes": test_probes,
                            **row,
                        }
                    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "summary.csv", summary_rows)
    write_csv(args.out_dir / "probe_eval.csv", eval_rows)
    write_csv(args.out_dir / "selection_trace.csv", trace_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# RD Lens Validation\n\n"
        f"- lens_groups: `{'; '.join(args.lens_groups)}`\n"
        f"- extra_test_probes: `{', '.join(args.extra_test_probes)}`\n"
        f"- risk_kinds: `{', '.join(args.risk_kinds)}`\n"
        f"- elapsed_sec: {time.perf_counter() - started:.3f}\n\n"
        "## Leave-One-Lens-Out\n\n"
        + "\n".join(
            (
                f"- {row['map']} holdout={row['heldout_probe']} {row['risk_kind']}: "
                f"B={row['n_boundary']}/{row['n_basis']}, "
                f"test_mean={float(row['test_bits_mean']):.4g}, "
                f"test_cvar={float(row['test_bits_cvar']):.4g}, "
                f"gap={float(row['test_minus_train_mean']):.4g}"
            )
            for row in summary_rows
            if row["protocol"] == "leave_one_lens_out"
        )
        + "\n\n## Stratified One-Per-Group\n\n"
        + "\n".join(
            (
                f"- {row['map']} train={row['train_probes']} {row['risk_kind']}: "
                f"B={row['n_boundary']}/{row['n_basis']}, "
                f"test_mean={float(row['test_bits_mean']):.4g}, "
                f"test_cvar={float(row['test_bits_cvar']):.4g}, "
                f"gap={float(row['test_minus_train_mean']):.4g}"
            )
            for row in summary_rows
            if row["protocol"] == "stratified_one_per_group"
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
