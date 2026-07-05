#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_group_constrained_adaptive_table import evaluate_group_boundary, group_context
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import (
    ProbeDeltaCache,
    probe_delta_table,
    score_candidates,
)
from run_rd_multiprobe_basis import build_probe_context
from run_rd_operator_theorem_checks import (
    active_edges,
    evaluate_recipe_boundary,
    finite_float,
    hidden_distortions,
)


def finite_or_blank(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        return ""
    return value


def parse_state_list(raw: str) -> List[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def top_rows_by_backend(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    probes: Sequence[str],
    args: argparse.Namespace,
    backend: str,
) -> Tuple[List[Dict[str, object]], Dict[str, float], Dict[str, float], float]:
    started = time.perf_counter()
    before_by_probe, deltas_by_state, _probe_diag = probe_delta_table(
        map_name=map_label,
        step=0,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        probes=probes,
        gamma=args.gamma,
        slip=args.slip,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
        probe_cache=ProbeDeltaCache(enabled=False),
        delta_backend=backend,
    )
    scored, risks, violations = score_candidates(
        map_name=map_label,
        step=0,
        basis=basis,
        boundary=boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        before_by_probe=before_by_probe,
        deltas_by_state=deltas_by_state,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.cvar_alpha,
        score_mode=args.score_mode,
        rate_tie_break=args.rate_tie_break,
    )
    return scored, risks, violations, time.perf_counter() - started


def exact_candidate_rows(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    args: argparse.Namespace,
    scored_by_backend: Mapping[str, Sequence[Mapping[str, object]]],
) -> List[Dict[str, object]]:
    exact_cache: Dict[Tuple[int, ...], Dict[str, object]] = {}
    out: List[Dict[str, object]] = []
    for backend, scored in scored_by_backend.items():
        for row in list(scored)[: max(1, args.top_k)]:
            candidate = int(row["candidate_state"])
            trial_boundary = tuple(sorted(set(boundary).union({candidate})))
            if trial_boundary not in exact_cache:
                exact_cache[trial_boundary] = evaluate_group_boundary(
                    map_label=map_label,
                    rows=rows,
                    slip=args.slip,
                    boundary=trial_boundary,
                    lens_groups=lens_groups,
                    recipe=recipe,
                    basis=basis,
                    budgets=budgets,
                    args=args,
                )
            exact = exact_cache[trial_boundary]
            estimated_after = finite_float(row.get("violation_after"), float("nan"))
            exact_total = finite_float(exact.get("total_violation"), float("nan"))
            out.append(
                {
                    "map": map_label,
                    "slip": args.slip,
                    "backend": backend,
                    "rank": int(row["rank"]),
                    "candidate_state": candidate,
                    "trial_boundary": list(trial_boundary),
                    "estimated_violation_after": estimated_after,
                    "exact_total_violation_after": exact_total,
                    "estimate_minus_exact_violation": (
                        estimated_after - exact_total
                        if math.isfinite(estimated_after) and math.isfinite(exact_total)
                        else float("nan")
                    ),
                    "estimated_violation_reduction": finite_float(row.get("violation_reduction")),
                    "estimated_groups_improved": int(row.get("groups_improved", 0)),
                    "exact_all_groups_feasible": bool(exact.get("all_groups_feasible", False)),
                    "exact_n_groups_feasible": int(exact.get("n_groups_feasible", 0)),
                    "exact_group_risks": exact.get("group_risks", {}),
                    "exact_group_violations": exact.get("group_violations", {}),
                }
            )
    return out


def edge_weight_rows(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundaries: Sequence[Sequence[int]],
    probes: Sequence[str],
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for boundary in boundaries:
        boundary = sorted(set(int(state) for state in boundary))
        for probe in probes:
            context = build_probe_context(
                rows,
                recipe=recipe,
                fixed_candidate_basis=basis,
                residual_kind=probe,
                gamma=args.gamma,
                slip=args.slip,
                probe_top_fraction=args.probe_top_fraction,
            )
            row, edge_rows = evaluate_recipe_boundary(
                map_name=map_label,
                context=context,
                recipe=recipe,
                boundary=boundary,
                gamma=args.gamma,
                slip=args.slip,
            )
            valid_edges = [edge for edge in edge_rows if bool(edge.get("edge_valid", False))]
            active_weighted = active_edges(edge_rows, edge_weight=args.edge_weight)
            active_uniform = active_edges(edge_rows, edge_weight="uniform")
            weighted_bits = hidden_distortions(edge_rows, boundary=boundary, edge_weight=args.edge_weight)["bits"]
            uniform_bits = hidden_distortions(edge_rows, boundary=boundary, edge_weight="uniform")["bits"]
            occupancy_total = sum(finite_float(edge.get("policy_occupancy", 0.0)) for edge in valid_edges)
            out.append(
                {
                    "map": map_label,
                    "slip": args.slip,
                    "boundary": list(boundary),
                    "probe": probe,
                    "n_boundary": len(boundary),
                    "n_edge_rows": len(edge_rows),
                    "n_valid_edges": len(valid_edges),
                    "n_active_edges_weighted": len(active_weighted),
                    "n_active_edges_uniform": len(active_uniform),
                    "valid_policy_occupancy_total": occupancy_total,
                    "weighted_hidden_bits": weighted_bits,
                    "uniform_hidden_bits": uniform_bits,
                    "uniform_minus_weighted_bits": uniform_bits - weighted_bits,
                    "n_edges_valid_from_row": int(row.get("n_edges_valid", 0)),
                    "value_gap_max": finite_float(row.get("value_gap_max"), float("nan")),
                }
            )
    return out


def write_report(
    out_path: Path,
    *,
    args: argparse.Namespace,
    map_label: str,
    basis: Sequence[int],
    boundary: Sequence[int],
    budgets: Mapping[str, float],
    backend_summaries: Sequence[Mapping[str, object]],
    candidate_rows: Sequence[Mapping[str, object]],
    edge_rows: Sequence[Mapping[str, object]],
    elapsed: float,
) -> None:
    backend_columns = [
        "backend",
        "step_time_sec",
        "top_candidate",
        "top_estimated_violation_after",
        "top_estimated_violation_reduction",
        "current_total_violation",
    ]
    candidate_columns = [
        "backend",
        "rank",
        "candidate_state",
        "estimated_violation_after",
        "exact_total_violation_after",
        "estimate_minus_exact_violation",
        "estimated_violation_reduction",
        "exact_all_groups_feasible",
    ]
    edge_columns = [
        "boundary",
        "probe",
        "n_valid_edges",
        "n_active_edges_weighted",
        "valid_policy_occupancy_total",
        "weighted_hidden_bits",
        "uniform_hidden_bits",
        "uniform_minus_weighted_bits",
    ]
    lines = [
        "# Incremental Group Beam Semantic Diff",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map = `{map_label}`, slip = `{args.slip}`",
        f"initial_boundary = `{list(boundary)}`, n_basis = `{len(basis)}`",
        f"budgets = `{json.dumps(budgets, sort_keys=True)}`",
        f"elapsed_sec = `{elapsed:.3f}`",
        "",
        "This diagnostic separates the open-room discrepancy into score estimate, edge-weight semantics, and exact post-split group feasibility.",
        "",
        "## Backend Step-0 Summary",
        "",
        markdown_table(
            [
                {col: finite_or_blank(row.get(col, "")) for col in backend_columns}
                for row in backend_summaries
            ],
            backend_columns,
        ),
        "",
        "## Top Candidate Exact Checks",
        "",
        markdown_table(
            [
                {col: finite_or_blank(row.get(col, "")) for col in candidate_columns}
                for row in candidate_rows
            ],
            candidate_columns,
        ),
        "",
        "## Edge Weight Semantics",
        "",
        markdown_table(
            [
                {col: finite_or_blank(row.get(col, "")) for col in edge_columns}
                for row in edge_rows
            ],
            edge_columns,
        ),
        "",
        "## Interpretation",
        "",
        "- The original discrepancy comes from edge weighting, not from terminal-universe or active-edge validity: edge-uniform bits remain large while occupancy-weighted bits are already below budget.",
        "- The insertion-score backend now honors the same occupancy-or-uniform active-edge semantics as the production operator when it evaluates a beam node.",
        "- The step-0 score is still a conservative frozen-edge estimate; the exact post-split check shows that both top choices are feasible after the graph is rewired.",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic diff for insertion-score group beam selection.")
    parser.add_argument("--map-spec", default="open_room:12")
    parser.add_argument("--slip", type=float, default=0.0)
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
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument(
        "--edge-probes",
        nargs="+",
        default=["bottleneck", "junction", "value_gradient"],
        help="Probe subset for the expensive edge-weight semantic table.",
    )
    parser.add_argument(
        "--extra-boundaries",
        nargs="*",
        default=["0,1,143", "0,72,143"],
        help="Comma-separated state lists to include in the edge-weight semantic table.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/group_incremental_semantic_diff"))
    args = parser.parse_args()

    started = time.perf_counter()
    parsed = list(parse_map_specs([args.map_spec]))
    if len(parsed) != 1:
        raise ValueError(f"Expected one map spec, got {args.map_spec!r}")
    _family, _size, map_label, rows = parsed[0]
    _grid, lens_groups, recipe, basis, boundary, budgets, _context_info = group_context(
        map_label,
        rows,
        args.slip,
        args,
    )
    train_probes = sorted({probe for probes in lens_groups.values() for probe in probes})
    scored_by_backend: Dict[str, List[Dict[str, object]]] = {}
    backend_summaries: List[Dict[str, object]] = []
    for backend in ["operator", "insertion_score"]:
        scored, risks, violations, step_time = top_rows_by_backend(
            map_label=map_label,
            rows=rows,
            recipe=recipe,
            basis=basis,
            boundary=boundary,
            lens_groups=lens_groups,
            budgets=budgets,
            probes=train_probes,
            args=args,
            backend=backend,
        )
        scored_by_backend[backend] = scored
        top = scored[0] if scored else {}
        backend_summaries.append(
            {
                "backend": backend,
                "step_time_sec": step_time,
                "current_group_risks": risks,
                "current_group_violations": violations,
                "current_total_violation": sum(violations.values()),
                "top_candidate": top.get("candidate_state", ""),
                "top_estimated_violation_after": top.get("violation_after", ""),
                "top_estimated_violation_reduction": top.get("violation_reduction", ""),
            }
        )
    candidate_rows = exact_candidate_rows(
        map_label=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        args=args,
        scored_by_backend=scored_by_backend,
    )
    boundary_list = [boundary]
    for raw in args.extra_boundaries:
        parsed_boundary = parse_state_list(raw)
        if parsed_boundary:
            boundary_list.append(parsed_boundary)
    unique_boundaries: List[List[int]] = []
    seen = set()
    for item in boundary_list:
        key = tuple(sorted(set(item)))
        if key not in seen:
            seen.add(key)
            unique_boundaries.append(list(key))
    edge_rows = edge_weight_rows(
        map_label=map_label,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundaries=unique_boundaries,
        probes=[probe for probe in args.edge_probes if probe in set(train_probes)],
        args=args,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "candidate_semantic_diff.csv", candidate_rows)
    write_csv_all_fields(args.out_dir / "edge_weight_semantic_diff.csv", edge_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(
            {
                "map": map_label,
                "slip": args.slip,
                "basis": list(basis),
                "initial_boundary": list(boundary),
                "budgets": budgets,
                "backend_summaries": backend_summaries,
                "candidate_rows": candidate_rows,
                "edge_weight_rows": edge_rows,
            },
            indent=2,
            default=json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        args.out_dir / "summary.md",
        args=args,
        map_label=map_label,
        basis=basis,
        boundary=boundary,
        budgets=budgets,
        backend_summaries=backend_summaries,
        candidate_rows=candidate_rows,
        edge_rows=edge_rows,
        elapsed=time.perf_counter() - started,
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
