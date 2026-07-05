#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_rd_group_constrained import (
    ProbeDeltaCache,
    fixed_basis,
    group_risks_from_probe_values,
    parse_group_specs,
    probe_delta_table,
    score_candidates,
)
from run_rd_multiprobe_basis import build_probe_context
from run_rd_operator_theorem_checks import finite_float, operator_marginal_rows


def best_state(candidate_rows: Sequence[Mapping[str, object]]) -> object:
    if not candidate_rows:
        return ""
    return int(candidate_rows[0]["candidate_state"])


def score_from_deltas(
    map_label: str,
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    before_by_probe: Mapping[str, float],
    deltas_by_state: Mapping[int, Mapping[str, float]],
    args: argparse.Namespace,
) -> Tuple[List[Dict[str, object]], float]:
    started = time.perf_counter()
    scoring_basis = sorted(set(int(state) for state in boundary).union(int(state) for state in deltas_by_state))
    candidate_rows, _group_risks, _group_violations = score_candidates(
        map_name=map_label,
        step=0,
        basis=scoring_basis if scoring_basis else basis,
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
    return candidate_rows, time.perf_counter() - started


def profile_operator_call(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    probes: Sequence[str],
    slip: float,
    args: argparse.Namespace,
    *,
    cache: ProbeDeltaCache | None,
) -> Dict[str, object]:
    started = time.perf_counter()
    before_by_probe, deltas_by_state, probe_rows = probe_delta_table(
        map_name=map_label,
        step=0,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        probes=probes,
        gamma=args.gamma,
        slip=slip,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
        max_candidates=args.max_candidates,
        probe_cache=cache,
    )
    candidate_rows, candidate_score_time = score_from_deltas(
        map_label=map_label,
        basis=basis,
        boundary=boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        before_by_probe=before_by_probe,
        deltas_by_state=deltas_by_state,
        args=args,
    )
    wall_time = time.perf_counter() - started
    profile = cache.summary() if cache is not None else {}
    return {
        "n_candidate_scores": len(candidate_rows),
        "selected_state": best_state(candidate_rows),
        "wall_time_sec": wall_time,
        "probe_context_build_time_sec": sum(float(row.get("context_build_time_sec", 0.0)) for row in probe_rows),
        "probe_green_kernel_time_sec": sum(float(row.get("green_kernel_time_sec", 0.0)) for row in probe_rows),
        "probe_operator_delta_time_sec": sum(float(row.get("operator_delta_time_sec", 0.0)) for row in probe_rows),
        "probe_uncached_time_sec": sum(float(row.get("probe_uncached_time_sec", 0.0)) for row in probe_rows),
        "candidate_score_time_sec": candidate_score_time,
        "probe_cache_hits": sum(1 for row in probe_rows if bool(row.get("cache_hit", False))),
        "probe_cache_misses": sum(1 for row in probe_rows if not bool(row.get("cache_hit", False))),
        "probe_cache_hit_rate": (
            sum(1 for row in probe_rows if bool(row.get("cache_hit", False))) / max(1, len(probe_rows))
        ),
        "profiled_selection_time_sec": profile.get("profiled_selection_time_sec", ""),
    }


def profile_full_recompute(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    budgets: Mapping[str, float],
    probes: Sequence[str],
    slip: float,
    args: argparse.Namespace,
) -> Dict[str, object]:
    started = time.perf_counter()
    before_by_probe: Dict[str, float] = {}
    deltas_by_state: Dict[int, Dict[str, float]] = {}
    context_build_time = 0.0
    green_time = 0.0
    operator_time = 0.0
    recompute_time = 0.0
    n_candidate_scores = 0
    for probe in probes:
        context_started = time.perf_counter()
        context = build_probe_context(
            rows,
            recipe=recipe,
            fixed_candidate_basis=basis,
            residual_kind=probe,
            gamma=args.gamma,
            slip=slip,
            probe_top_fraction=args.probe_top_fraction,
        )
        context_build_time += time.perf_counter() - context_started
        step_rows, _base_row, _edge_rows = operator_marginal_rows(
            map_name=map_label,
            step=0,
            context=context,
            recipe=recipe,
            boundary=boundary,
            gamma=args.gamma,
            slip=slip,
            lambda_struct=args.lambda_struct,
            edge_weight=args.edge_weight,
            max_candidates=args.max_candidates,
            with_frozen_recompute=True,
            with_actual_recompute=True,
            with_recompute_modes=False,
        )
        if step_rows:
            before_by_probe[probe] = max(0.0, finite_float(step_rows[0].get("actual_bits_before")))
            green_time += finite_float(step_rows[0].get("time_base_eval_sec"))
            operator_time += finite_float(step_rows[0].get("time_operator_score_sec"))
            recompute_time += finite_float(step_rows[0].get("time_recompute_total_sec"))
        else:
            before_by_probe[probe] = 0.0
        n_candidate_scores += len(step_rows)
        for row in step_rows:
            state = int(row["candidate_state"])
            actual_delta = finite_float(row.get("actual_bits_before")) - finite_float(row.get("actual_bits_after"))
            deltas_by_state.setdefault(state, {})[probe] = max(0.0, actual_delta)
    candidate_rows, candidate_score_time = score_from_deltas(
        map_label=map_label,
        basis=basis,
        boundary=boundary,
        lens_groups=lens_groups,
        budgets=budgets,
        before_by_probe=before_by_probe,
        deltas_by_state=deltas_by_state,
        args=args,
    )
    return {
        "n_candidate_scores": n_candidate_scores,
        "selected_state": best_state(candidate_rows),
        "wall_time_sec": time.perf_counter() - started,
        "probe_context_build_time_sec": context_build_time,
        "probe_green_kernel_time_sec": green_time,
        "probe_operator_delta_time_sec": operator_time,
        "full_recompute_time_sec": recompute_time,
        "candidate_score_time_sec": candidate_score_time,
        "probe_cache_hits": 0,
        "probe_cache_misses": len(probes),
        "probe_cache_hit_rate": 0.0,
    }


def make_budgets(
    map_label: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    lens_groups: Mapping[str, Sequence[str]],
    probes: Sequence[str],
    slip: float,
    args: argparse.Namespace,
) -> Dict[str, float]:
    before_by_probe, _deltas_by_state, _probe_rows = probe_delta_table(
        map_name=map_label,
        step=0,
        rows=rows,
        recipe=recipe,
        basis=basis,
        boundary=boundary,
        probes=probes,
        gamma=args.gamma,
        slip=slip,
        lambda_struct=args.lambda_struct,
        edge_weight=args.edge_weight,
        probe_top_fraction=args.probe_top_fraction,
        max_candidates=args.max_candidates,
        probe_cache=None,
    )
    group_risks = group_risks_from_probe_values(
        before_by_probe,
        lens_groups=lens_groups,
        group_risk_kind=args.group_risk_kind,
        cvar_alpha=args.cvar_alpha,
    )
    return {group: args.budget_frac * float(risk) for group, risk in group_risks.items()}


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    columns = [
        "map",
        "slip",
        "mode",
        "n_states",
        "n_basis",
        "n_boundary",
        "max_candidates",
        "n_candidate_scores",
        "selected_state",
        "wall_time_sec",
        "speedup_vs_full_recompute",
        "probe_context_build_time_sec",
        "probe_green_kernel_time_sec",
        "probe_operator_delta_time_sec",
        "full_recompute_time_sec",
        "candidate_score_time_sec",
        "probe_cache_hit_rate",
    ]
    lines = [
        "# Discovery Profile Cache Benchmark",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"slips = {list(args.slips)}",
        f"max_candidates = {args.max_candidates}",
        "",
        "This isolates one boundary-selection step and decomposes probe construction, Green-kernel evaluation, frozen/operator scoring, full adaptive candidate recompute, and cache hits.",
        "",
        markdown_table([{col: row.get(col, "") for col in columns} for row in rows], columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile group-RD discovery and cache/incremental operator costs.")
    parser.add_argument("--map-specs", nargs="+", default=["open_room:7", "four_rooms:7", "maze:9"])
    parser.add_argument("--slips", nargs="+", type=float, default=[0.0, 0.05])
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
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/discovery_profile_cache"))
    args = parser.parse_args()

    lens_groups = parse_group_specs(args.lens_groups)
    probes = sorted({probe for group_probes in lens_groups.values() for probe in group_probes})
    recipe = dict(LEARNED_RECIPES[args.recipe])
    rows_out: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        grid = GridWorld(map_rows)
        for slip in args.slips:
            basis = fixed_basis(
                map_label,
                grid=grid,
                kinds=args.fixed_basis_kinds,
                gamma=args.gamma,
                slip=slip,
                top_fraction=args.probe_top_fraction,
                random_count=args.fixed_random_count,
            )
            boundary = sorted(set(endpoint_boundary_states(grid)).intersection(set(basis)))
            budgets = make_budgets(
                map_label=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                probes=probes,
                slip=slip,
                args=args,
            )
            mode_rows: List[Dict[str, object]] = []
            full = profile_full_recompute(
                map_label=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                probes=probes,
                slip=slip,
                args=args,
            )
            mode_rows.append({"mode": "full_recompute", **full})
            current = profile_operator_call(
                map_label=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                probes=probes,
                slip=slip,
                args=args,
                cache=None,
            )
            mode_rows.append({"mode": "current_frozen_operator", **current})
            cache = ProbeDeltaCache(enabled=True)
            first = profile_operator_call(
                map_label=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                probes=probes,
                slip=slip,
                args=args,
                cache=cache,
            )
            mode_rows.append({"mode": "cached_incremental_first", **first})
            hit = profile_operator_call(
                map_label=map_label,
                rows=map_rows,
                recipe=recipe,
                basis=basis,
                boundary=boundary,
                lens_groups=lens_groups,
                budgets=budgets,
                probes=probes,
                slip=slip,
                args=args,
                cache=cache,
            )
            mode_rows.append({"mode": "cached_incremental_hit", **hit})
            full_time = float(full["wall_time_sec"])
            for row in mode_rows:
                wall_time = float(row["wall_time_sec"])
                rows_out.append(
                    {
                        "map_family": family,
                        "map_size": size,
                        "map": map_label,
                        "slip": slip,
                        "n_states": grid.n_states,
                        "n_basis": len(basis),
                        "n_boundary": len(boundary),
                        "max_candidates": args.max_candidates,
                        **row,
                        "speedup_vs_full_recompute": full_time / max(1e-12, wall_time),
                    }
                )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "discovery_profile_cache.csv", rows_out)
    (args.out_dir / "discovery_profile_cache.json").write_text(
        json.dumps(rows_out, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows_out, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
