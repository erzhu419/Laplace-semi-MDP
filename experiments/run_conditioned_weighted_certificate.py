#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401
import numpy as np

from bellman_kron import GridWorld, shortest_path_policy_to_target, transition_matrix_for_policy
from compression_experiment_utils import parse_map_specs, resolve_method_spec
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import construct_boundary, json_default
from run_rd_operator_theorem_checks import build_recipe_context
from run_weighted_spectral_certificate import (
    collatz_certificate_at_q,
    finite_float,
    first_hit_blocks,
    geometric_tail,
    prefix_tail_stats,
    row_q_bound,
    spectral_radius,
    terminal_scales,
    terminal_sets_for_basis,
)


def write_csv_all_fields(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def condition_caps(raw_caps: Sequence[float]) -> List[float]:
    caps = sorted({float(cap) for cap in raw_caps if math.isfinite(float(cap)) and float(cap) > 0.0})
    return caps + [float("inf")]


def q_targets_for_rho(rho: float, n_grid: int) -> np.ndarray:
    if not math.isfinite(rho) or rho >= 1.0:
        return np.asarray([], dtype=float)
    fractions = np.unique(
        np.concatenate(
            [
                np.geomspace(1e-8, 1.0, max(8, n_grid // 2)),
                np.linspace(0.001, 1.0, max(8, n_grid // 2)),
            ]
        )
    )
    targets = rho + (1.0 - rho) * fractions
    return np.asarray([q for q in targets if rho < q < 1.0], dtype=float)


def normalized_weights(weights: np.ndarray) -> np.ndarray:
    if len(weights) == 0:
        return weights
    w_min = float(np.min(weights))
    if w_min <= 0.0 or not math.isfinite(w_min):
        return weights
    return weights / w_min


def certificate_candidate(
    P: np.ndarray,
    P_IT: np.ndarray,
    start_pos: int,
    q_target: float,
    objective_K: int,
) -> Dict[str, object] | None:
    cert = collatz_certificate_at_q(P, q_target)
    q = finite_float(cert.get("q"))
    weights = normalized_weights(np.asarray(cert.get("weights", []), dtype=float))
    if not bool(cert.get("ok")) or not math.isfinite(q) or q >= 1.0 or len(weights) == 0:
        return None
    w_min = float(np.min(weights))
    w_max = float(np.max(weights))
    cond = w_max / max(1e-300, w_min)
    entry_scale, row_scale = terminal_scales(P_IT, weights)
    w_start = float(weights[start_pos])
    objective_bound = geometric_tail(q, row_scale * w_start, objective_K)
    Pw = P @ weights
    residual = q * weights - Pw
    scale = np.maximum(1.0, np.maximum(np.abs(q * weights), np.abs(Pw)))
    relative_residual = residual / scale
    return {
        "q": q,
        "q_target": q_target,
        "weights": weights,
        "weight_min": w_min,
        "weight_max": w_max,
        "weight_dynamic_range": cond,
        "entry_scale": entry_scale,
        "row_scale": row_scale,
        "weight_start": w_start,
        "objective_tail_bound": objective_bound,
        "weighted_slack_min_abs": float(np.min(residual)),
        "weighted_slack_min_rel": float(np.min(relative_residual)),
        "weighted_violation_max_abs": float(max(0.0, np.max(-residual))),
        "weighted_violation_max_rel": float(max(0.0, np.max(-relative_residual))),
        "solve_method": cert.get("solve_method", ""),
    }


def best_conditioned_certificates(
    P: np.ndarray,
    P_IT: np.ndarray,
    start_pos: int,
    caps: Sequence[float],
    objective_K: int,
    n_grid: int,
) -> Dict[float, Dict[str, object] | None]:
    rho = spectral_radius(P)
    best: Dict[float, Dict[str, object] | None] = {cap: None for cap in caps}
    for q_target in q_targets_for_rho(rho, n_grid=n_grid):
        candidate = certificate_candidate(
            P=P,
            P_IT=P_IT,
            start_pos=start_pos,
            q_target=float(q_target),
            objective_K=objective_K,
        )
        if candidate is None:
            continue
        cond = finite_float(candidate["weight_dynamic_range"], float("inf"))
        bound = finite_float(candidate["objective_tail_bound"], float("inf"))
        for cap in caps:
            if cond > cap:
                continue
            current = best[cap]
            if current is None or bound < finite_float(current["objective_tail_bound"], float("inf")):
                best[cap] = candidate
    return best


def frac_ceil(value: float, denominator: int) -> Fraction:
    if not math.isfinite(value):
        raise ValueError("Cannot rationalize non-finite value")
    return Fraction(math.ceil(value * denominator), denominator)


def rationalize_nearest(value: float, denominator: int) -> Fraction:
    if not math.isfinite(value):
        raise ValueError("Cannot rationalize non-finite value")
    return Fraction(round(value * denominator), denominator)


def rational_audit(
    P: np.ndarray,
    weights: np.ndarray,
    q: float,
    p_denominator: int,
    w_denominator: int,
    q_denominator: int,
    q_buffer: float,
) -> Dict[str, object]:
    if len(weights) == 0 or not math.isfinite(q) or q >= 1.0:
        return {
            "rational_verified": False,
            "rational_status": "invalid_float_certificate",
        }
    normalized = normalized_weights(weights)
    if np.min(normalized) <= 0.0:
        return {
            "rational_verified": False,
            "rational_status": "nonpositive_weight",
        }
    safe_buffer = min(max(0.0, q_buffer), max(0.0, (1.0 - q) / 4.0))
    q_safe = q + safe_buffer
    if q_safe >= 1.0:
        return {
            "rational_verified": False,
            "rational_status": "q_buffer_exceeds_one",
        }
    q_frac = frac_ceil(q_safe, q_denominator)
    if q_frac >= 1:
        return {
            "rational_verified": False,
            "rational_status": "rational_q_exceeds_one",
            "rational_q": float(q_frac),
        }
    w_frac = [rationalize_nearest(float(w), w_denominator) for w in normalized]
    if any(w <= 0 for w in w_frac):
        return {
            "rational_verified": False,
            "rational_status": "rounded_nonpositive_weight",
            "rational_q": float(q_frac),
        }
    p_frac = [
        [Fraction(float(P[i, j])).limit_denominator(p_denominator) for j in range(P.shape[1])]
        for i in range(P.shape[0])
    ]
    max_violation = Fraction(0)
    min_slack = None
    failing_rows = 0
    for i in range(P.shape[0]):
        lhs = sum(p_frac[i][j] * w_frac[j] for j in range(P.shape[1]))
        rhs = q_frac * w_frac[i]
        slack = rhs - lhs
        if min_slack is None or slack < min_slack:
            min_slack = slack
        if slack < 0:
            failing_rows += 1
            violation = -slack
            if violation > max_violation:
                max_violation = violation
    verified = failing_rows == 0
    return {
        "rational_verified": verified,
        "rational_status": "rational_verified" if verified else "rational_violation",
        "rational_q": float(q_frac),
        "rational_q_num": q_frac.numerator,
        "rational_q_den": q_frac.denominator,
        "rational_min_slack": float(min_slack) if min_slack is not None else float("nan"),
        "rational_max_violation": float(max_violation),
        "rational_failing_rows": failing_rows,
    }


def run_one(
    family: str,
    size: int,
    map_label: str,
    rows: Tuple[str, ...],
    boundary_method: str,
    args: argparse.Namespace,
) -> List[Dict[str, object]]:
    grid = GridWorld(rows)
    recipe = LEARNED_RECIPES[args.recipe]
    context = build_recipe_context(rows=rows, recipe=recipe, gamma=args.gamma, slip=args.slip)
    actual_method = resolve_method_spec(boundary_method, grid)
    boundary, _constructor = construct_boundary(
        method=actual_method,
        map_name=map_label,
        rows=rows,
        grid=grid,
        slip=args.slip,
        gamma=args.gamma,
        max_splits=args.max_splits,
        seed=args.seed,
    )
    boundary = sorted(set(int(state) for state in boundary))
    caps = condition_caps(args.condition_caps)
    objective_K = max(args.k_values)
    out: List[Dict[str, object]] = []
    for target_state in boundary:
        target_policy = shortest_path_policy_to_target(grid, int(target_state), slip=args.slip)
        P_free, _r_free = transition_matrix_for_policy(grid, target_policy, absorbing=[])
        for src_state in boundary:
            if int(src_state) == int(target_state):
                continue
            for basis in args.terminal_basis:
                terminals = terminal_sets_for_basis(basis, int(src_state), boundary, context)
                if not terminals:
                    continue
                P_II, P_IT, _interior, start_pos = first_hit_blocks(P_free, int(src_state), terminals)
                best_by_cap = best_conditioned_certificates(
                    P=P_II,
                    P_IT=P_IT,
                    start_pos=start_pos,
                    caps=caps,
                    objective_K=objective_K,
                    n_grid=args.q_grid_size,
                )
                actual_by_k = {
                    K: prefix_tail_stats(P_II, P_IT, start_pos, K)
                    for K in args.k_values
                }
                for cap in caps:
                    cert = best_by_cap[cap]
                    cap_label = "inf" if math.isinf(cap) else f"{cap:g}"
                    base: Dict[str, object] = {
                        "map_family": family,
                        "map_size": size,
                        "map": map_label,
                        "boundary_method": actual_method,
                        "terminal_basis": basis,
                        "src_state": int(src_state),
                        "target_state": int(target_state),
                        "condition_cap": cap_label,
                        "condition_cap_float": cap,
                        "n_interior": int(P_II.shape[0]),
                        "n_terminals": int(P_IT.shape[1]),
                        "spectral_radius": spectral_radius(P_II),
                        "row_q": row_q_bound(P_II),
                    }
                    for K, actual in actual_by_k.items():
                        base[f"actual_tail_row_K{K}"] = actual["actual_tail_row_sum"]
                    if cert is None:
                        out.append(
                            {
                                **base,
                                "certificate_found": False,
                                "certificate_status": "no_conditioned_certificate",
                            }
                        )
                        continue
                    q = finite_float(cert["q"])
                    weights = np.asarray(cert["weights"], dtype=float)
                    audit = rational_audit(
                        P=P_II,
                        weights=weights,
                        q=q,
                        p_denominator=args.p_denominator,
                        w_denominator=args.w_denominator,
                        q_denominator=args.q_denominator,
                        q_buffer=args.q_buffer,
                    )
                    row = {
                        **base,
                        "certificate_found": True,
                        "certificate_status": (
                            "rational_verified_conditioned_certificate"
                            if bool(audit.get("rational_verified"))
                            else "float_conditioned_certificate_only"
                        ),
                        "weighted_q": q,
                        "weighted_q_target": finite_float(cert["q_target"]),
                        "weighted_q_lt_1": q < 1.0,
                        "weight_min": finite_float(cert["weight_min"]),
                        "weight_max": finite_float(cert["weight_max"]),
                        "weight_dynamic_range": finite_float(cert["weight_dynamic_range"]),
                        "weight_start": finite_float(cert["weight_start"]),
                        "row_scale": finite_float(cert["row_scale"]),
                        "entry_scale": finite_float(cert["entry_scale"]),
                        "weighted_slack_min_abs": finite_float(cert["weighted_slack_min_abs"]),
                        "weighted_slack_min_rel": finite_float(cert["weighted_slack_min_rel"]),
                        "weighted_violation_max_abs": finite_float(cert["weighted_violation_max_abs"]),
                        "weighted_violation_max_rel": finite_float(cert["weighted_violation_max_rel"]),
                        "objective_tail_bound": finite_float(cert["objective_tail_bound"]),
                        "solve_method": cert["solve_method"],
                        **audit,
                    }
                    for K in args.k_values:
                        q_value = finite_float(cert["q"])
                        scale = finite_float(cert["row_scale"]) * finite_float(cert["weight_start"])
                        row[f"conditioned_row_tail_K{K}"] = geometric_tail(q_value, scale, K)
                    out.append(row)
    return out


def aggregate_rows(rows: Sequence[Mapping[str, object]], K_values: Sequence[int]) -> List[Dict[str, object]]:
    keys = sorted({(row["map"], row["terminal_basis"], row["condition_cap"]) for row in rows})
    out: List[Dict[str, object]] = []
    k_show = max(K_values)
    for map_label, basis, cap in keys:
        group = [
            row for row in rows
            if (row["map"], row["terminal_basis"], row["condition_cap"]) == (map_label, basis, cap)
        ]
        found = [row for row in group if bool(row.get("certificate_found", False))]
        row = {
            "map": map_label,
            "terminal_basis": basis,
            "condition_cap": cap,
            "n_edges": len(group),
            "certificates_found": len(found),
            "rational_verified": sum(1 for item in found if bool(item.get("rational_verified", False))),
            "spectral_radius_max": max((finite_float(item["spectral_radius"], 0.0) for item in group), default=0.0),
            "row_q_max": max((finite_float(item["row_q"], 0.0) for item in group), default=0.0),
            "weighted_q_max": max((finite_float(item.get("weighted_q"), 0.0) for item in found), default=0.0),
            "weight_dynamic_range_max": max(
                (finite_float(item.get("weight_dynamic_range"), 0.0) for item in found),
                default=0.0,
            ),
            f"conditioned_row_tail_K{k_show}_max": max(
                (finite_float(item.get(f"conditioned_row_tail_K{k_show}"), 0.0) for item in found),
                default=0.0,
            ),
            f"actual_tail_row_K{k_show}_max": max(
                (finite_float(item.get(f"actual_tail_row_K{k_show}"), 0.0) for item in group),
                default=0.0,
            ),
            "rational_max_violation_max": max(
                (finite_float(item.get("rational_max_violation"), 0.0) for item in found),
                default=0.0,
            ),
        }
        out.append(row)
    return out


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    aggregate = aggregate_rows(rows, args.k_values)
    k_show = max(args.k_values)
    columns = [
        "map",
        "terminal_basis",
        "condition_cap",
        "n_edges",
        "certificates_found",
        "rational_verified",
        "spectral_radius_max",
        "row_q_max",
        "weighted_q_max",
        "weight_dynamic_range_max",
        f"conditioned_row_tail_K{k_show}_max",
        f"actual_tail_row_K{k_show}_max",
        "rational_max_violation_max",
    ]
    lines = [
        "# Conditioned Weighted Spectral Certificate",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"terminal_basis = {list(args.terminal_basis)}",
        f"condition_caps = {list(args.condition_caps)} plus inf",
        f"k_values = {list(args.k_values)}",
        "",
        "This table adds a conditioned Collatz search and an exact Fraction audit of the rounded certificate.",
        "The audit verifies the rounded inequality `P_II w <= q w` over rationals; it does not replace the tighter frontier-tail runtime certificate.",
        "",
        markdown_table([{col: row.get(col, "") for col in columns} for row in aggregate], columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Conditioned/rational diagnostics for weighted spectral Green certificates.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:128", "open_room:12", "maze:13", "four_rooms:11"])
    parser.add_argument("--boundary-methods", nargs="+", default=["endpoints"])
    parser.add_argument("--terminal-basis", nargs="+", choices=["boundary", "candidate", "residual", "proposal"], default=["boundary", "residual"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument("--condition-caps", type=float, nargs="+", default=[1e2, 1e4, 1e6, 1e9, 1e12])
    parser.add_argument("--k-values", type=int, nargs="+", default=[32, 64, 128])
    parser.add_argument("--q-grid-size", type=int, default=160)
    parser.add_argument("--p-denominator", type=int, default=1000000)
    parser.add_argument("--w-denominator", type=int, default=1000000)
    parser.add_argument("--q-denominator", type=int, default=1000000000)
    parser.add_argument("--q-buffer", type=float, default=1e-6)
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/conditioned_weighted_certificate"))
    args = parser.parse_args()

    rows: List[Dict[str, object]] = []
    for family, size, map_label, map_rows in parse_map_specs(args.map_specs):
        for boundary_method in args.boundary_methods:
            rows.extend(
                run_one(
                    family=family,
                    size=size,
                    map_label=map_label,
                    rows=map_rows,
                    boundary_method=boundary_method,
                    args=args,
                )
            )
    summary = aggregate_rows(rows, args.k_values)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "conditioned_certificate_edges.csv", rows)
    write_csv_all_fields(args.out_dir / "conditioned_certificate_summary.csv", summary)
    (args.out_dir / "conditioned_certificate_edges.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "conditioned_certificate_summary.json").write_text(
        json.dumps(summary, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
