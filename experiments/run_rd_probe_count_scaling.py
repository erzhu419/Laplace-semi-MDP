#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import thread_limits  # noqa: F401
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe-count scaling for fixed-basis multi-probe RD."
    )
    parser.add_argument("--map-specs", nargs="+", default=["maze:9", "four_rooms:9", "open_room:7"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument(
        "--probe-pool",
        nargs="+",
        default=["junction", "bottleneck", "turn_articulation", "combined", "value_gradient", "transition_entropy"],
    )
    parser.add_argument("--m-values", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    parser.add_argument("--risk-kinds", nargs="+", default=["mean", "mean_cvar", "max"])
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
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
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/rd_probe_count_scaling"))
    args = parser.parse_args()

    recipe = LEARNED_RECIPES[args.recipe]
    rows_out: List[Dict[str, object]] = []
    eval_rows: List[Dict[str, object]] = []
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
        for raw_m in args.m_values:
            m = max(1, min(int(raw_m), len(args.probe_pool) - 1))
            train_probes = args.probe_pool[:m]
            test_probes = args.probe_pool[m:]
            if not test_probes:
                continue
            for risk_kind in args.risk_kinds:
                boundary, _trace, _candidates, selection_time = select_boundary(
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
                )
                train_bits: List[float] = []
                test_bits: List[float] = []
                for split_name, probes in [("train", train_probes), ("test", test_probes)]:
                    for probe in probes:
                        metrics = evaluate_probe(
                            map_name=map_label,
                            rows=map_rows,
                            recipe=recipe,
                            basis=basis,
                            boundary=boundary,
                            probe=probe,
                            gamma=args.gamma,
                            slip=args.slip,
                            edge_weight=args.edge_weight,
                            probe_top_fraction=args.probe_top_fraction,
                        )
                        if split_name == "train":
                            train_bits.append(float(metrics["hidden_bits"]))
                        else:
                            test_bits.append(float(metrics["hidden_bits"]))
                        eval_rows.append(
                            {
                                "map": map_label,
                                "m_train": m,
                                "risk_kind": risk_kind,
                                "split": split_name,
                                "probe": probe,
                                "n_basis": len(basis),
                                "n_boundary": len(boundary),
                                **metrics,
                            }
                        )
                rows_out.append(
                    {
                        "map": map_label,
                        "m_train": m,
                        "risk_kind": risk_kind,
                        "train_probes": list(train_probes),
                        "test_probes": list(test_probes),
                        "n_basis": len(basis),
                        "n_boundary": len(boundary),
                        "selection_time_sec": selection_time,
                        **aggregate_probe_metrics("train_bits", train_bits, args.cvar_alpha),
                        **aggregate_probe_metrics("test_bits", test_bits, args.cvar_alpha),
                        "test_minus_train_mean": float(np.mean(test_bits)) - float(np.mean(train_bits)),
                        "boundary": list(boundary),
                    }
                )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "summary.csv", rows_out)
    write_csv(args.out_dir / "probe_eval.csv", eval_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# RD Probe Count Scaling\n\n"
        f"- probe_pool: `{', '.join(args.probe_pool)}`\n"
        f"- risk_kinds: `{', '.join(args.risk_kinds)}`\n"
        f"- elapsed_sec: {time.perf_counter() - started:.3f}\n\n"
        "## Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} m={row['m_train']} {row['risk_kind']}: "
                f"B={row['n_boundary']}/{row['n_basis']}, "
                f"train_mean={float(row['train_bits_mean']):.4g}, "
                f"test_mean={float(row['test_bits_mean']):.4g}, "
                f"test_cvar={float(row['test_bits_cvar']):.4g}, "
                f"gap={float(row['test_minus_train_mean']):.4g}"
            )
            for row in rows_out
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
