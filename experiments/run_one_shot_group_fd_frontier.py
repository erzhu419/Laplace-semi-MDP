#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping

import thread_limits  # noqa: F401

from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_group_constrained_adaptive_table import evaluate_group_boundary, group_context
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import probe_delta_table, score_candidates


def write_report(rows: List[Mapping[str, object]], out_path: Path) -> None:
    columns = [
        "map",
        "slip",
        "top_m",
        "n_basis",
        "n_boundary",
        "state_compression_ratio",
        "group_all_feasible",
        "n_groups_feasible",
        "group_total_violation",
        "group_max_violation",
        "operator_time_sec",
        "audit_time_sec",
        "n_candidate_insertion_evaluations",
        "n_beam_expansions",
    ]
    lines = [
        "# One-Shot Frozen Group-FD Prefix Frontier",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Each map/slip context builds one frozen multi-probe Green finite-difference score and one deterministic candidate order. Every row audits a prefix of that same order; scores are never recomputed after insertion.",
        "",
        markdown_table(
            [{column: row.get(column, "") for column in columns} for row in rows],
            columns,
        ),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit fixed prefixes of one frozen group-RD score.")
    parser.add_argument("--map-specs", nargs="+", default=["open_room:12", "four_rooms:11", "maze:13"])
    parser.add_argument("--slips", type=float, nargs="+", default=[0.05])
    parser.add_argument("--top-m-values", type=int, nargs="+", default=[0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24])
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
    parser.add_argument("--test-probes", nargs="+", default=["combined", "value_gradient", "transition_entropy"])
    parser.add_argument("--include-test-probes", action="store_true")
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--budget-frac", type=float, default=0.25)
    parser.add_argument("--group-risk-kind", choices=["mean", "cvar", "max"], default="cvar")
    parser.add_argument("--score-mode", choices=["reduction", "reduction_per_rate", "lexicographic"], default="reduction")
    parser.add_argument("--rate-tie-break", type=float, default=1e-4)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--lambda-struct", type=float, default=8.0)
    parser.add_argument("--cvar-alpha", type=float, default=0.8)
    parser.add_argument("--edge-weight", choices=["occupancy", "uniform", "occupancy_or_uniform"], default="occupancy_or_uniform")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/one_shot_group_fd_frontier"))
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")

    contexts = [
        (family, size, map_label, map_rows, slip)
        for family, size, map_label, map_rows in parse_map_specs(args.map_specs)
        for slip in args.slips
    ]
    contexts = [
        context for index, context in enumerate(contexts)
        if index % args.num_shards == args.shard_index
    ]
    rows_out: List[Dict[str, object]] = []
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for family, size, map_label, map_rows, slip in contexts:
        grid, groups, recipe, basis, boundary0, budgets, _info = group_context(
            map_label, map_rows, slip, args
        )
        probes = sorted({probe for group in groups.values() for probe in group})
        started = time.perf_counter()
        before, deltas, _diagnostics = probe_delta_table(
            map_name=map_label,
            step=0,
            rows=map_rows,
            recipe=recipe,
            basis=basis,
            boundary=boundary0,
            probes=probes,
            gamma=args.gamma,
            slip=slip,
            lambda_struct=args.lambda_struct,
            edge_weight=args.edge_weight,
            probe_top_fraction=args.probe_top_fraction,
            delta_backend="operator",
        )
        scored, _risks, _violations = score_candidates(
            map_name=map_label,
            step=0,
            basis=basis,
            boundary=boundary0,
            lens_groups=groups,
            budgets=budgets,
            before_by_probe=before,
            deltas_by_state=deltas,
            group_risk_kind=args.group_risk_kind,
            cvar_alpha=args.cvar_alpha,
            score_mode=args.score_mode,
            rate_tie_break=args.rate_tie_break,
        )
        operator_time = time.perf_counter() - started
        order = [int(row["candidate_state"]) for row in scored]
        for top_m in args.top_m_values:
            if top_m > len(order):
                continue
            boundary = sorted(set(boundary0).union(order[:top_m]))
            audit_started = time.perf_counter()
            result = evaluate_group_boundary(
                map_label=map_label,
                rows=map_rows,
                slip=slip,
                boundary=boundary,
                lens_groups=groups,
                recipe=recipe,
                basis=basis,
                budgets=budgets,
                args=args,
            )
            rows_out.append(
                {
                    "map_family": family,
                    "map_size": size,
                    "map": map_label,
                    "slip": slip,
                    "top_m": top_m,
                    "n_states": grid.n_states,
                    "n_basis": len(basis),
                    "n_boundary": len(boundary),
                    "state_compression_ratio": grid.n_states / max(1, len(boundary)),
                    "boundary": json.dumps(boundary),
                    "candidate_order": json.dumps(order),
                    "group_all_feasible": bool(result["all_groups_feasible"]),
                    "n_groups_feasible": int(result["n_groups_feasible"]),
                    "group_total_violation": float(result["total_violation"]),
                    "group_max_violation": float(result["max_violation"]),
                    "group_risks": json.dumps(result["group_risks"], sort_keys=True),
                    "group_violations": json.dumps(result["group_violations"], sort_keys=True),
                    "operator_time_sec": operator_time,
                    "audit_time_sec": time.perf_counter() - audit_started,
                    "n_green_response_passes": len(probes),
                    "n_candidate_insertion_evaluations": 0,
                    "n_beam_expansions": 0,
                }
            )
            write_csv_all_fields(args.out_dir / "one_shot_group_fd_frontier.csv", rows_out)
            with (args.out_dir / "progress.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "map": map_label,
                            "slip": slip,
                            "top_m": top_m,
                            "group_all_feasible": bool(result["all_groups_feasible"]),
                        }
                    )
                    + "\n"
                )
        write_csv_all_fields(args.out_dir / "one_shot_group_fd_frontier.csv", rows_out)
    (args.out_dir / "one_shot_group_fd_frontier.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    write_report(rows_out, args.out_dir / "summary.md")


if __name__ == "__main__":
    main()
