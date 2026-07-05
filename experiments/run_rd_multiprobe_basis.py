#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import GridWorld, endpoint_boundary_states
from compression_experiment_utils import parse_map_specs
from run_first_boundary_targeted import candidate_boundary_states, critical_saliency
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_rd_operator_theorem_checks import (
    boundary_rate,
    evaluate_recipe_boundary,
    finite_float,
    hidden_distortions,
    json_default,
    operator_marginal_rows,
    write_csv,
)


def deterministic_unit(key: str) -> float:
    value = 1469598103934665603
    for ch in key:
        value ^= ord(ch)
        value *= 1099511628211
        value &= (1 << 64) - 1
    return value / float(1 << 64)


def resolve_count_kind(kind: str, grid: GridWorld) -> str:
    if kind.endswith("_sqrt"):
        base = kind[: -len("_sqrt")]
        count = max(4, int(math.ceil(math.sqrt(grid.n_states))))
        return f"{base}_{min(count, grid.n_states)}"
    if kind.endswith("_quarter"):
        base = kind[: -len("_quarter")]
        count = max(4, int(math.ceil(0.25 * grid.n_states)))
        return f"{base}_{min(count, grid.n_states)}"
    return kind


def candidate_set_for_kind(
    grid: GridWorld,
    kind: str,
    gamma: float,
    slip: float,
    top_fraction: float,
) -> List[int]:
    goal = grid.symbol_states("G")[0]
    return candidate_boundary_states(
        grid=grid,
        kind=resolve_count_kind(kind, grid),
        goal_state=goal,
        gamma=gamma,
        slip=slip,
        top_fraction=top_fraction,
    )


def fixed_basis(
    map_name: str,
    grid: GridWorld,
    kinds: Sequence[str],
    gamma: float,
    slip: float,
    top_fraction: float,
    random_count: int,
) -> List[int]:
    basis = set(endpoint_boundary_states(grid))
    for kind in kinds:
        basis.update(candidate_set_for_kind(grid, kind, gamma=gamma, slip=slip, top_fraction=top_fraction))
    if random_count > 0:
        candidates = [state for state in range(grid.n_states) if state not in basis]
        ranked = sorted(
            candidates,
            key=lambda state: (deterministic_unit(f"{map_name}:basis:{state}"), -state),
            reverse=True,
        )
        basis.update(ranked[: min(random_count, len(ranked))])
    return sorted(basis)


def residual_train_basis(
    grid: GridWorld,
    train_probes: Sequence[str],
    gamma: float,
    slip: float,
    top_fraction: float,
) -> List[int]:
    basis = set(endpoint_boundary_states(grid))
    for probe in train_probes:
        basis.update(candidate_set_for_kind(grid, probe, gamma=gamma, slip=slip, top_fraction=top_fraction))
    return sorted(basis)


def build_probe_context(
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    fixed_candidate_basis: Sequence[int],
    residual_kind: str,
    gamma: float,
    slip: float,
    probe_top_fraction: float,
) -> Dict[str, object]:
    grid = GridWorld(rows)
    goal = grid.symbol_states("G")[0]
    if residual_kind == "none":
        residual_boundary = endpoint_boundary_states(grid)
    elif residual_kind == "hard":
        residual_boundary = fixed_candidate_basis
    else:
        residual_boundary = candidate_boundary_states(
            grid=grid,
            kind=residual_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=probe_top_fraction,
        )

    soft_kind = str(recipe["soft_kind"])
    if soft_kind == "none":
        soft_state_cost = np.zeros(grid.n_states, dtype=float)
    else:
        soft_state_cost = critical_saliency(
            grid=grid,
            kind=soft_kind,
            goal_state=goal,
            gamma=gamma,
            slip=slip,
            top_fraction=float(recipe["soft_top_fraction"]),
        )
    return {
        "grid": grid,
        "candidate_boundary": sorted(set(fixed_candidate_basis)),
        "residual_boundary": sorted(set(residual_boundary)),
        "proposal_boundary": sorted(set(fixed_candidate_basis)),
        "soft_state_cost": soft_state_cost,
    }


def tail_cvar(values: Sequence[float], alpha: float) -> float:
    if not values:
        return 0.0
    alpha = min(max(float(alpha), 0.0), 0.999999)
    sorted_values = sorted((float(value) for value in values), reverse=True)
    tail_count = max(1, int(math.ceil((1.0 - alpha) * len(sorted_values))))
    return float(np.mean(sorted_values[:tail_count]))


def smoothmax(values: Sequence[float], tau: float) -> float:
    if not values:
        return 0.0
    tau = max(1e-9, float(tau))
    array = np.asarray(values, dtype=float)
    center = float(np.max(array))
    return float(center + tau * np.log(np.sum(np.exp((array - center) / tau))))


def risk_value(values: Sequence[float], risk_kind: str, alpha: float, eta: float, tau: float) -> float:
    vals = [float(value) for value in values]
    if not vals:
        return 0.0
    if risk_kind == "single":
        return vals[0]
    if risk_kind == "mean":
        return float(np.mean(vals))
    if risk_kind == "max":
        return max(vals)
    if risk_kind == "cvar":
        return tail_cvar(vals, alpha=alpha)
    if risk_kind == "mean_cvar":
        return (1.0 - eta) * float(np.mean(vals)) + eta * tail_cvar(vals, alpha=alpha)
    if risk_kind == "smoothmax":
        return smoothmax(vals, tau=tau)
    raise ValueError(f"Unknown risk kind: {risk_kind}")


def grouped_risk_value(
    probes: Sequence[str],
    values: Sequence[float],
    risk_kind: str,
    alpha: float,
    eta: float,
    tau: float,
    probe_groups: Mapping[str, str] | None = None,
) -> float:
    if not risk_kind.startswith("group_"):
        return risk_value(values, risk_kind, alpha=alpha, eta=eta, tau=tau)
    if probe_groups is None:
        raise ValueError(f"{risk_kind} requires probe_groups.")
    grouped: Dict[str, List[float]] = {}
    for probe, value in zip(probes, values):
        group = probe_groups.get(str(probe), str(probe))
        grouped.setdefault(group, []).append(float(value))
    group_values: List[float] = []
    for group in sorted(grouped):
        vals = grouped[group]
        if risk_kind == "group_mean_cvar":
            group_values.append((1.0 - eta) * float(np.mean(vals)) + eta * tail_cvar(vals, alpha=alpha))
        elif risk_kind == "group_max_cvar":
            group_values.append(tail_cvar(vals, alpha=alpha))
        elif risk_kind == "group_mean_max":
            group_values.append(max(vals))
        else:
            raise ValueError(f"Unknown grouped risk kind: {risk_kind}")
    if risk_kind == "group_max_cvar":
        return max(group_values) if group_values else 0.0
    return float(np.mean(group_values)) if group_values else 0.0


def multiprobe_candidate_scores(
    map_name: str,
    step: int,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    train_probes: Sequence[str],
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    probe_top_fraction: float,
    risk_kind: str,
    cvar_alpha: float,
    cvar_eta: float,
    smooth_tau: float,
    probe_groups: Mapping[str, str] | None = None,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    per_probe_rows: Dict[str, List[Dict[str, object]]] = {}
    probe_debug: List[Dict[str, object]] = []
    before_values: List[float] = []
    for probe in train_probes:
        context = build_probe_context(
            rows,
            recipe=recipe,
            fixed_candidate_basis=basis,
            residual_kind=probe,
            gamma=gamma,
            slip=slip,
            probe_top_fraction=probe_top_fraction,
        )
        step_rows, _base_row, _edge_rows = operator_marginal_rows(
            map_name=map_name,
            step=step,
            context=context,
            recipe=recipe,
            boundary=boundary,
            gamma=gamma,
            slip=slip,
            lambda_struct=lambda_struct,
            edge_weight=edge_weight,
            max_candidates=0,
            with_frozen_recompute=True,
            with_actual_recompute=False,
            with_recompute_modes=False,
        )
        per_probe_rows[probe] = step_rows
        before = finite_float(step_rows[0].get("frozen_bits_before")) if step_rows else 0.0
        before_values.append(before)
        probe_debug.append(
            {
                "map": map_name,
                "step": step,
                "probe": probe,
                "n_candidates": len(step_rows),
                "distortion_before_bits": before,
                "top_probe_state": (
                    int(max(step_rows, key=lambda row: finite_float(row["bits_fd_operator_score"]))["candidate_state"])
                    if step_rows
                    else None
                ),
            }
        )

    by_probe_state = {
        probe: {int(row["candidate_state"]): row for row in probe_rows}
        for probe, probe_rows in per_probe_rows.items()
    }
    candidate_states = sorted(set(basis) - set(boundary))
    risk_before = grouped_risk_value(
        train_probes,
        before_values,
        risk_kind,
        alpha=cvar_alpha,
        eta=cvar_eta,
        tau=smooth_tau,
        probe_groups=probe_groups,
    )
    rows_out: List[Dict[str, object]] = []
    for candidate in candidate_states:
        deltas: List[float] = []
        after_values: List[float] = []
        rate_deltas: List[float] = []
        probe_details: Dict[str, Dict[str, float]] = {}
        for probe_index, probe in enumerate(train_probes):
            probe_row = by_probe_state.get(probe, {}).get(int(candidate))
            before = before_values[probe_index]
            delta = finite_float(probe_row.get("bits_fd_delta")) if probe_row is not None else 0.0
            rate_delta = finite_float(probe_row.get("rate_delta")) if probe_row is not None else 0.0
            deltas.append(delta)
            after_values.append(before - delta)
            rate_deltas.append(rate_delta)
            probe_details[probe] = {
                "before_bits": before,
                "delta_bits": delta,
                "after_bits": before - delta,
                "rate_delta": rate_delta,
            }
        risk_after = grouped_risk_value(
            train_probes,
            after_values,
            risk_kind,
            alpha=cvar_alpha,
            eta=cvar_eta,
            tau=smooth_tau,
            probe_groups=probe_groups,
        )
        rate_delta = float(np.mean(rate_deltas)) if rate_deltas else 0.0
        score = lambda_struct * (risk_before - risk_after) - rate_delta
        rows_out.append(
            {
                "map": map_name,
                "step": step,
                "risk_kind": risk_kind,
                "candidate_state": int(candidate),
                "n_boundary": len(boundary),
                "n_basis": len(basis),
                "n_train_probes": len(train_probes),
                "risk_before": risk_before,
                "risk_after": risk_after,
                "risk_delta": risk_before - risk_after,
                "rate_delta": rate_delta,
                "operator_score": score,
                "mean_probe_delta": float(np.mean(deltas)) if deltas else 0.0,
                "max_probe_delta": max(deltas) if deltas else 0.0,
                "min_probe_delta": min(deltas) if deltas else 0.0,
                "probe_details": json.dumps(probe_details, sort_keys=True),
            }
        )
    rows_out.sort(key=lambda row: (float(row["operator_score"]), -int(row["candidate_state"])), reverse=True)
    for rank, row in enumerate(rows_out, start=1):
        row["rank"] = rank
    return rows_out, probe_debug


def select_boundary(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    train_probes: Sequence[str],
    gamma: float,
    slip: float,
    lambda_struct: float,
    edge_weight: str,
    probe_top_fraction: float,
    risk_kind: str,
    cvar_alpha: float,
    cvar_eta: float,
    smooth_tau: float,
    max_splits: int,
    greedy_positive_only: bool,
    probe_groups: Mapping[str, str] | None = None,
) -> Tuple[List[int], List[Dict[str, object]], List[Dict[str, object]], float]:
    boundary = sorted(set(endpoint_boundary_states(GridWorld(rows))).intersection(set(basis)))
    trace: List[Dict[str, object]] = []
    candidate_rows: List[Dict[str, object]] = []
    probe_rows: List[Dict[str, object]] = []
    started = time.perf_counter()
    for step in range(max_splits):
        scored, probe_debug = multiprobe_candidate_scores(
            map_name=map_name,
            step=step,
            rows=rows,
            recipe=recipe,
            basis=basis,
            boundary=boundary,
            train_probes=train_probes,
            gamma=gamma,
            slip=slip,
            lambda_struct=lambda_struct,
            edge_weight=edge_weight,
            probe_top_fraction=probe_top_fraction,
            risk_kind=risk_kind,
            cvar_alpha=cvar_alpha,
            cvar_eta=cvar_eta,
            smooth_tau=smooth_tau,
            probe_groups=probe_groups,
        )
        candidate_rows.extend(scored)
        probe_rows.extend(probe_debug)
        if not scored:
            trace.append(
                {
                    "map": map_name,
                    "risk_kind": risk_kind,
                    "step": step,
                    "selected_state": None,
                    "stop_reason": "no_candidate",
                    "n_boundary": len(boundary),
                }
            )
            break
        best = scored[0]
        state = int(best["candidate_state"])
        stop_reason = "continue"
        if greedy_positive_only and float(best["operator_score"]) <= 0.0:
            stop_reason = "non_positive_score"
        elif state in set(boundary):
            stop_reason = "already_boundary"
        trace.append(
            {
                "map": map_name,
                "risk_kind": risk_kind,
                "step": step,
                "selected_state": state,
                "n_boundary_before": len(boundary),
                "n_basis": len(basis),
                "operator_score": best["operator_score"],
                "risk_before": best["risk_before"],
                "risk_after": best["risk_after"],
                "risk_delta": best["risk_delta"],
                "rate_delta": best["rate_delta"],
                "stop_reason": stop_reason,
            }
        )
        if stop_reason != "continue":
            break
        boundary = sorted(set(boundary).union({state}))
    return boundary, trace, candidate_rows + probe_rows, time.perf_counter() - started


def evaluate_probe(
    map_name: str,
    rows: Tuple[str, ...],
    recipe: Mapping[str, object],
    basis: Sequence[int],
    boundary: Sequence[int],
    probe: str,
    gamma: float,
    slip: float,
    edge_weight: str,
    probe_top_fraction: float,
) -> Dict[str, object]:
    context = build_probe_context(
        rows,
        recipe=recipe,
        fixed_candidate_basis=basis,
        residual_kind=probe,
        gamma=gamma,
        slip=slip,
        probe_top_fraction=probe_top_fraction,
    )
    row, edge_rows = evaluate_recipe_boundary(
        map_name=map_name,
        context=context,
        recipe=recipe,
        boundary=boundary,
        gamma=gamma,
        slip=slip,
    )
    distortions = hidden_distortions(edge_rows, boundary=boundary, edge_weight=edge_weight)
    return {
        "rate_bits": boundary_rate(row, recipe),
        "hidden_bits": max(0.0, distortions["bits"]),
        "hidden_linear": max(0.0, distortions["linear"]),
        "start_gap": finite_float(row.get("start_gap"), default=float("nan")),
        "value_gap_max": finite_float(row.get("value_gap_max"), default=float("nan")),
        "n_edges_valid": int(row["n_edges_valid"]),
    }


def aggregate_probe_metrics(prefix: str, values: Sequence[float], alpha: float) -> Dict[str, object]:
    vals = [float(value) for value in values]
    return {
        f"{prefix}_mean": float(np.mean(vals)) if vals else 0.0,
        f"{prefix}_max": max(vals) if vals else 0.0,
        f"{prefix}_cvar": tail_cvar(vals, alpha=alpha) if vals else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare fixed multi-task basis plus multi-probe RD risk against residual-adaptive bases."
    )
    parser.add_argument("--map-specs", nargs="+", default=["maze:9", "four_rooms:9", "open_room:7"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument("--basis-modes", nargs="+", default=["fixed", "residual_train"])
    parser.add_argument(
        "--fixed-basis-kinds",
        nargs="+",
        default=["turn_articulation", "eigen_extrema_sqrt", "coverage_sqrt"],
    )
    parser.add_argument("--fixed-random-count", type=int, default=2)
    parser.add_argument("--train-probes", nargs="+", default=["junction", "bottleneck"])
    parser.add_argument("--test-probes", nargs="+", default=["turn_articulation", "combined", "value_gradient"])
    parser.add_argument("--risk-kinds", nargs="+", default=["single", "mean", "mean_cvar", "max"])
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
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/rd_multiprobe_basis"))
    args = parser.parse_args()

    recipe = LEARNED_RECIPES[args.recipe]
    summary_rows: List[Dict[str, object]] = []
    eval_rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []
    candidate_rows: List[Dict[str, object]] = []
    started = time.perf_counter()

    for _family, _size, map_label, map_rows in parse_map_specs(args.map_specs):
        grid = GridWorld(map_rows)
        for basis_mode in args.basis_modes:
            if basis_mode == "fixed":
                basis = fixed_basis(
                    map_label,
                    grid=grid,
                    kinds=args.fixed_basis_kinds,
                    gamma=args.gamma,
                    slip=args.slip,
                    top_fraction=args.probe_top_fraction,
                    random_count=args.fixed_random_count,
                )
            elif basis_mode == "residual_train":
                basis = residual_train_basis(
                    grid,
                    train_probes=args.train_probes,
                    gamma=args.gamma,
                    slip=args.slip,
                    top_fraction=args.probe_top_fraction,
                )
            else:
                raise ValueError(f"Unknown basis mode: {basis_mode}")

            for risk_kind in args.risk_kinds:
                boundary, trace, candidates, selection_time = select_boundary(
                    map_name=map_label,
                    rows=map_rows,
                    recipe=recipe,
                    basis=basis,
                    train_probes=args.train_probes,
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
                trace_rows.extend({**row, "basis_mode": basis_mode} for row in trace)
                candidate_rows.extend({**row, "basis_mode": basis_mode} for row in candidates)

                train_bits: List[float] = []
                test_bits: List[float] = []
                start_gaps: List[float] = []
                for split_name, probes in [("train", args.train_probes), ("test", args.test_probes)]:
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
                        if math.isfinite(float(metrics["start_gap"])):
                            start_gaps.append(float(metrics["start_gap"]))
                        eval_rows.append(
                            {
                                "map": map_label,
                                "basis_mode": basis_mode,
                                "risk_kind": risk_kind,
                                "split": split_name,
                                "probe": probe,
                                "n_basis": len(basis),
                                "n_boundary": len(boundary),
                                "boundary": list(boundary),
                                **metrics,
                            }
                        )
                summary_rows.append(
                    {
                        "map": map_label,
                        "basis_mode": basis_mode,
                        "risk_kind": risk_kind,
                        "n_basis": len(basis),
                        "n_boundary": len(boundary),
                        "selection_time_sec": selection_time,
                        **aggregate_probe_metrics("train_bits", train_bits, args.cvar_alpha),
                        **aggregate_probe_metrics("test_bits", test_bits, args.cvar_alpha),
                        "test_minus_train_mean": (
                            float(np.mean(test_bits)) - float(np.mean(train_bits))
                            if train_bits and test_bits
                            else 0.0
                        ),
                        "start_gap_mean": float(np.mean(start_gaps)) if start_gaps else 0.0,
                        "start_gap_max": max(start_gaps) if start_gaps else 0.0,
                        "boundary": list(boundary),
                    }
                )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "summary.csv", summary_rows)
    write_csv(args.out_dir / "probe_eval.csv", eval_rows)
    write_csv(args.out_dir / "selection_trace.csv", trace_rows)
    write_csv(args.out_dir / "candidate_scores.csv", candidate_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "summary.md").write_text(
        "# Fixed Basis Multi-Probe RD\n\n"
        f"- recipe: `{args.recipe}`\n"
        f"- train_probes: `{', '.join(args.train_probes)}`\n"
        f"- test_probes: `{', '.join(args.test_probes)}`\n"
        f"- risk_kinds: `{', '.join(args.risk_kinds)}`\n"
        f"- elapsed_sec: {time.perf_counter() - started:.3f}\n\n"
        "## Summary\n\n"
        + "\n".join(
            (
                f"- {row['map']} {row['basis_mode']} {row['risk_kind']}: "
                f"B={row['n_boundary']}/{row['n_basis']}, "
                f"train_mean={float(row['train_bits_mean']):.4g}, "
                f"test_mean={float(row['test_bits_mean']):.4g}, "
                f"test_cvar={float(row['test_bits_cvar']):.4g}, "
                f"gap={float(row['test_minus_train_mean']):.4g}, "
                f"start_gap_max={float(row['start_gap_max']):.4g}"
            )
            for row in summary_rows
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
