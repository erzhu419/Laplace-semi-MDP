#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from bellman_kron import GridWorld, shortest_path_policy_to_target, transition_matrix_for_policy
from compression_experiment_utils import parse_map_specs, resolve_method_spec
from run_first_boundary_targeted import markdown_table
from run_graph_baseline_comparison import LEARNED_RECIPES
from run_option_algorithm_comparison import construct_boundary, json_default
from run_rd_operator_theorem_checks import build_recipe_context


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


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def spectral_radius(P: np.ndarray) -> float:
    if P.size == 0:
        return 0.0
    eigvals = np.linalg.eigvals(P)
    return float(np.max(np.abs(eigvals), initial=0.0))


def row_q_bound(P: np.ndarray) -> float:
    if P.size == 0:
        return 0.0
    return float(np.max(np.sum(np.maximum(P, 0.0), axis=1), initial=0.0))


def geometric_tail(q: float, scale: float, K: int) -> float:
    if not math.isfinite(q) or q >= 1.0:
        return float("inf")
    if q < 0.0:
        return 0.0
    return float(scale * (q ** (K + 1)) / max(1e-12, 1.0 - q))


def collatz_certificate_at_q(P: np.ndarray, q_target: float) -> Dict[str, object]:
    if P.size == 0:
        return {
            "ok": True,
            "q": 0.0,
            "w_min": 1.0,
            "w_max": 1.0,
            "w_mean": 1.0,
            "violation": 0.0,
            "solve_method": "empty",
            "weights": np.ones(0, dtype=float),
        }
    n = P.shape[0]
    if not math.isfinite(q_target) or q_target <= 0.0:
        return {
            "ok": False,
            "q": float("nan"),
            "w_min": float("nan"),
            "w_max": float("nan"),
            "w_mean": float("nan"),
            "violation": float("nan"),
            "solve_method": "invalid_q",
            "weights": np.full(n, np.nan),
        }
    eye = np.eye(n, dtype=float)
    ones = np.ones(n, dtype=float)
    method = "solve"
    try:
        weights = np.linalg.solve(q_target * eye - P, ones)
    except np.linalg.LinAlgError:
        method = "pinv"
        weights = np.linalg.pinv(q_target * eye - P) @ ones
    weight_min = float(np.min(weights)) if len(weights) else 1.0
    weight_max = float(np.max(weights)) if len(weights) else 1.0
    if not np.all(np.isfinite(weights)) or weight_min <= 1e-12:
        return {
            "ok": False,
            "q": float("nan"),
            "w_min": finite_float(weight_min),
            "w_max": finite_float(weight_max),
            "w_mean": finite_float(np.mean(weights)) if len(weights) else 0.0,
            "violation": float("nan"),
            "solve_method": method,
            "weights": weights,
        }
    Pw = P @ weights
    ratios = np.divide(Pw, weights, out=np.full_like(Pw, np.inf), where=weights > 1e-12)
    q = float(np.max(ratios, initial=0.0))
    violation = float(np.max(Pw - q * weights, initial=0.0))
    return {
        "ok": q < 1.0 + 1e-10,
        "q": q,
        "w_min": weight_min,
        "w_max": weight_max,
        "w_mean": float(np.mean(weights)),
        "violation": violation,
        "solve_method": method,
        "weights": weights,
    }


def terminal_scales(P_IT: np.ndarray, weights: np.ndarray) -> Tuple[float, float]:
    if len(weights) and P_IT.size:
        entry_scale = float(np.max(P_IT / np.maximum(weights[:, None], 1e-12), initial=0.0))
        row_scale = float(np.max(np.sum(P_IT, axis=1) / np.maximum(weights, 1e-12), initial=0.0))
        return entry_scale, row_scale
    return 0.0, 0.0


def optimized_collatz_certificate(
    P: np.ndarray,
    P_IT: np.ndarray,
    start_pos: int,
    objective_K: int,
) -> Dict[str, object]:
    if P.size == 0:
        return collatz_certificate_at_q(P, 0.0)
    rho = spectral_radius(P)
    if not math.isfinite(rho) or rho >= 1.0:
        return collatz_certificate_at_q(P, float("nan"))
    fractions = np.unique(np.concatenate([
        np.geomspace(1e-5, 1.0, 80),
        np.linspace(0.01, 1.0, 40),
    ]))
    best: Dict[str, object] | None = None
    best_bound = float("inf")
    for fraction in fractions:
        q_target = rho + (1.0 - rho) * float(fraction)
        cert = collatz_certificate_at_q(P, q_target)
        q = finite_float(cert["q"])
        weights = np.asarray(cert["weights"], dtype=float)
        if not bool(cert["ok"]) or not math.isfinite(q) or q >= 1.0 or len(weights) == 0:
            continue
        _entry_scale, row_scale = terminal_scales(P_IT, weights)
        w_start = float(weights[start_pos])
        bound = geometric_tail(q, row_scale * w_start, objective_K)
        if bound < best_bound:
            best_bound = bound
            best = cert
            best["q_target"] = q_target
            best["objective_tail_bound"] = bound
    if best is not None:
        best["solve_method"] = f"optimized_{best['solve_method']}"
        return best
    return collatz_certificate_at_q(P, 1.0)


def first_hit_blocks(
    P: np.ndarray,
    start_state: int,
    terminals: Sequence[int],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    terminal_set = set(int(s) for s in terminals)
    if start_state in terminal_set:
        raise ValueError("start_state must not be terminal")
    all_states = np.arange(P.shape[0], dtype=int)
    interior = np.array([int(s) for s in all_states if int(s) not in terminal_set], dtype=int)
    terminal_arr = np.array(sorted(terminal_set), dtype=int)
    start_positions = np.flatnonzero(interior == int(start_state))
    if len(start_positions) == 0:
        raise ValueError("start_state missing from interior")
    P_II = P[np.ix_(interior, interior)]
    P_IT = P[np.ix_(interior, terminal_arr)] if len(terminal_arr) else np.zeros((len(interior), 0))
    return P_II, P_IT, interior, int(start_positions[0])


def prefix_tail_stats(P_II: np.ndarray, P_IT: np.ndarray, start_pos: int, K: int) -> Dict[str, float]:
    if P_II.size == 0:
        return {"actual_tail_entry_max": 0.0, "actual_tail_row_sum": 0.0}
    current = np.zeros(P_II.shape[0], dtype=float)
    current[start_pos] = 1.0
    prefix = np.zeros(P_IT.shape[1], dtype=float)
    for _ in range(max(0, int(K)) + 1):
        prefix += current @ P_IT
        current = current @ P_II
    try:
        exact = np.linalg.solve(np.eye(P_II.shape[0]) - P_II, P_IT)[start_pos]
    except np.linalg.LinAlgError:
        exact = (np.linalg.pinv(np.eye(P_II.shape[0]) - P_II) @ P_IT)[start_pos]
    tail = np.maximum(0.0, exact - prefix)
    return {
        "actual_tail_entry_max": float(np.max(tail, initial=0.0)),
        "actual_tail_row_sum": float(np.sum(tail)),
    }


def certificate_row(
    map_family: str,
    map_size: int,
    map_label: str,
    basis: str,
    src_state: int,
    target_state: int,
    P_II: np.ndarray,
    P_IT: np.ndarray,
    start_pos: int,
    K_values: Sequence[int],
) -> Dict[str, object]:
    row_q = row_q_bound(P_II)
    radius = spectral_radius(P_II)
    cert = optimized_collatz_certificate(
        P=P_II,
        P_IT=P_IT,
        start_pos=start_pos,
        objective_K=max(K_values) if K_values else 64,
    )
    weights = np.asarray(cert["weights"], dtype=float)
    w_start = float(weights[start_pos]) if len(weights) else 1.0
    entry_scale, row_scale = terminal_scales(P_IT, weights)
    row: Dict[str, object] = {
        "map_family": map_family,
        "map_size": map_size,
        "map": map_label,
        "terminal_basis": basis,
        "src_state": int(src_state),
        "target_state": int(target_state),
        "n_interior": int(P_II.shape[0]),
        "n_terminals": int(P_IT.shape[1]),
        "spectral_radius": radius,
        "row_q": row_q,
        "row_q_lt_1": row_q < 1.0,
        "weighted_q": finite_float(cert["q"]),
        "weighted_q_target": finite_float(cert.get("q_target", cert["q"])),
        "weighted_q_lt_1": bool(cert["ok"]) and finite_float(cert["q"]) < 1.0,
        "weighted_violation": finite_float(cert["violation"]),
        "weight_min": finite_float(cert["w_min"]),
        "weight_max": finite_float(cert["w_max"]),
        "weight_mean": finite_float(cert["w_mean"]),
        "weight_dynamic_range": finite_float(cert["w_max"]) / max(1e-12, finite_float(cert["w_min"], 0.0)),
        "weight_start": w_start,
        "entry_scale": entry_scale,
        "row_scale": row_scale,
        "solve_method": cert["solve_method"],
    }
    for K in K_values:
        q = finite_float(cert["q"])
        row[f"weighted_entry_tail_K{K}"] = geometric_tail(q, entry_scale * w_start, K)
        row[f"weighted_row_tail_K{K}"] = geometric_tail(q, row_scale * w_start, K)
        row[f"rowsum_tail_K{K}"] = geometric_tail(row_q, 1.0, K)
        actual = prefix_tail_stats(P_II, P_IT, start_pos, K)
        row[f"actual_tail_entry_K{K}"] = actual["actual_tail_entry_max"]
        row[f"actual_tail_row_K{K}"] = actual["actual_tail_row_sum"]
    return row


def terminal_sets_for_basis(
    basis: str,
    src_state: int,
    boundary: Sequence[int],
    context: Mapping[str, object],
) -> List[int]:
    if basis == "boundary":
        base = boundary
    elif basis == "candidate":
        base = context["candidate_boundary"]  # type: ignore[assignment]
    elif basis == "residual":
        base = context["residual_boundary"]  # type: ignore[assignment]
    elif basis == "proposal":
        base = context["proposal_boundary"]  # type: ignore[assignment]
    else:
        raise ValueError(f"Unknown terminal basis: {basis}")
    return sorted(int(s) for s in set(base) if int(s) != int(src_state))


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
    boundary = sorted(set(int(s) for s in boundary))
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
                try:
                    P_II, P_IT, _interior, start_pos = first_hit_blocks(P_free, int(src_state), terminals)
                except ValueError:
                    continue
                out.append(
                    certificate_row(
                        map_family=family,
                        map_size=size,
                        map_label=map_label,
                        basis=basis,
                        src_state=int(src_state),
                        target_state=int(target_state),
                        P_II=P_II,
                        P_IT=P_IT,
                        start_pos=start_pos,
                        K_values=args.k_values,
                    )
                )
    return out


def aggregate_rows(rows: Sequence[Mapping[str, object]], K_values: Sequence[int]) -> List[Dict[str, object]]:
    groups = sorted({(row["map"], row["terminal_basis"]) for row in rows})
    out: List[Dict[str, object]] = []
    for map_label, basis in groups:
        group = [row for row in rows if (row["map"], row["terminal_basis"]) == (map_label, basis)]
        row_count = len(group)
        agg: Dict[str, object] = {
            "map": map_label,
            "terminal_basis": basis,
            "n_edges": row_count,
            "row_q_lt_1": sum(1 for row in group if bool(row["row_q_lt_1"])),
            "weighted_q_lt_1": sum(1 for row in group if bool(row["weighted_q_lt_1"])),
            "spectral_radius_max": max((finite_float(row["spectral_radius"], 0.0) for row in group), default=0.0),
            "row_q_max": max((finite_float(row["row_q"], 0.0) for row in group), default=0.0),
            "weighted_q_max": max((finite_float(row["weighted_q"], 0.0) for row in group), default=0.0),
            "weight_max_max": max((finite_float(row["weight_max"], 0.0) for row in group), default=0.0),
            "weight_dynamic_range_max": max(
                (finite_float(row["weight_dynamic_range"], 0.0) for row in group),
                default=0.0,
            ),
        }
        for K in K_values:
            agg[f"weighted_row_tail_K{K}_max"] = max(
                (finite_float(row[f"weighted_row_tail_K{K}"], 0.0) for row in group),
                default=0.0,
            )
            agg[f"actual_tail_row_K{K}_max"] = max(
                (finite_float(row[f"actual_tail_row_K{K}"], 0.0) for row in group),
                default=0.0,
            )
        out.append(agg)
    return out


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path, args: argparse.Namespace) -> None:
    aggregate = aggregate_rows(rows, args.k_values)
    k_show = args.k_values[-1]
    columns = [
        "map",
        "terminal_basis",
        "n_edges",
        "row_q_lt_1",
        "weighted_q_lt_1",
        "spectral_radius_max",
        "row_q_max",
        "weighted_q_max",
        "weight_max_max",
        "weight_dynamic_range_max",
        f"weighted_row_tail_K{k_show}_max",
        f"actual_tail_row_K{k_show}_max",
    ]
    lines = [
        "# Weighted Spectral Certificate",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"map_specs = {list(args.map_specs)}",
        f"boundary_methods = {list(args.boundary_methods)}",
        f"terminal_basis = {list(args.terminal_basis)}",
        f"k_values = {list(args.k_values)}",
        "",
        "This checks a Collatz-style positive-vector certificate for first-hit Green tails:",
        "",
        "```text",
        "P_II w <= q w, q < 1",
        "tail <= c * w_start * q^(K+1) / (1-q)",
        "```",
        "",
        "It is a sufficient weighted spectral certificate; it is not used as the default runtime path yet.",
        "Large dynamic ranges mean the certificate can be mathematically valid but numerically awkward.",
        "",
        markdown_table([{col: row.get(col, "") for col in columns} for row in aggregate], columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Weighted spectral certificate diagnostics for first-hit Green tails.")
    parser.add_argument("--map-specs", nargs="+", default=["corridor:128", "open_room:12", "maze:13", "four_rooms:11"])
    parser.add_argument("--boundary-methods", nargs="+", default=["endpoints"])
    parser.add_argument("--terminal-basis", nargs="+", choices=["boundary", "candidate", "residual", "proposal"], default=["boundary", "residual"])
    parser.add_argument("--recipe", default="learned_rd_surrogate_joint_occ2_audit2")
    parser.add_argument("--k-values", type=int, nargs="+", default=[32, 64, 128])
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--slip", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/weighted_spectral_certificate"))
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
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "spectral_certificate_edges.csv", rows)
    aggregate = aggregate_rows(rows, args.k_values)
    write_csv_all_fields(args.out_dir / "spectral_certificate_summary.csv", aggregate)
    (args.out_dir / "spectral_certificate_edges.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "spectral_certificate_summary.json").write_text(
        json.dumps(aggregate, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
