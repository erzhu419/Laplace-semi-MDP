#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def parse_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def median(values: Iterable[float]) -> float:
    vals = sorted(value for value in values if math.isfinite(value))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def rate(values: Iterable[bool | None]) -> float:
    vals = [value for value in values if value is not None]
    return sum(1 for value in vals if value) / len(vals) if vals else float("nan")


def method_group(method: str, source: str) -> str:
    text = method.lower()
    if text in {"full_vi", "full_mdp"}:
        return "full_mdp"
    if text == "endpoints":
        return "baseline:endpoints"
    if "turn_articulation" in text:
        return "baseline:dense_turn"
    if "group_constrained" in text:
        return "ours:group_rd"
    if "graph_rd" in text:
        return "ours:rd_graph"
    if "eigen" in text:
        return "option_baseline:eigen"
    if "between" in text or "bottleneck" in text:
        return "option_baseline:bottleneck"
    if "random" in text:
        return "option_baseline:random"
    if "coverage" in text:
        return "option_baseline:coverage"
    return source


def normalize_core_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        method = str(row.get("method_spec") or row.get("method") or "")
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        rate_budget = n_boundary / max(1.0, n_states)
        out.append(
            {
                "source": "core_benchmark",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "core_benchmark"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": rate_budget,
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": finite_float(row.get("planning_time_speedup_vs_full_vi")),
                "total_speedup": finite_float(row.get("total_time_speedup_vs_full_vi")),
                "start_gap": finite_float(row.get("start_gap")),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "hidden_audit": finite_float(row.get("hidden_audit_distinct_mean"), finite_float(row.get("occupancy_struct_hidden_distinct"))),
                "success_rate": finite_float(row.get("success_rate"), 1.0 if method == "full_vi" else float("nan")),
                "group_feasible": parse_bool(row.get("group_all_feasible")) if row.get("group_all_feasible", "") != "" else None,
                "budget_label": "exact_or_same_protocol",
            }
        )
    return out


def normalize_group_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        if row.get("error"):
            continue
        method = str(row.get("method", ""))
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        out.append(
            {
                "source": "group_constrained_adaptive",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "group_constrained_adaptive"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": n_boundary / max(1.0, n_states),
                "state_compression_ratio": finite_float(row.get("state_compression_ratio")),
                "planning_speedup": finite_float(row.get("planning_speedup")),
                "total_speedup": finite_float(row.get("total_speedup")),
                "start_gap": finite_float(row.get("start_gap")),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "hidden_audit": finite_float(row.get("group_total_violation"), 0.0),
                "success_rate": float("nan"),
                "group_feasible": parse_bool(row.get("group_all_feasible")),
                "budget_label": f"group_budget_frac={row.get('budget_frac', '')}",
            }
        )
    return out


def normalize_option_rows(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        method = str(row.get("method") or row.get("method_family") or "")
        n_states = finite_float(row.get("n_states"))
        n_boundary = finite_float(row.get("n_boundary"))
        out.append(
            {
                "source": "option_baseline_frontier",
                "map": row.get("map", ""),
                "slip": row.get("slip", ""),
                "method": method,
                "method_group": method_group(method, "option_baseline_frontier"),
                "n_states": n_states,
                "n_boundary": n_boundary,
                "rate_budget_boundary_frac": n_boundary / max(1.0, n_states),
                "state_compression_ratio": n_states / max(1.0, n_boundary),
                "planning_speedup": float("nan"),
                "total_speedup": float("nan"),
                "start_gap": finite_float(row.get("start_gap")),
                "value_gap_max": finite_float(row.get("value_gap_max")),
                "hidden_audit": finite_float(row.get("hidden_audit_distinct_mean"), finite_float(row.get("occupancy_struct_hidden_distinct"))),
                "success_rate": finite_float(row.get("success_rate")),
                "group_feasible": parse_bool(row.get("feasible")),
                "budget_label": "option_count_or_boundary_count",
            }
        )
    return out


def dominates(a: Mapping[str, object], b: Mapping[str, object], eps: float = 1e-12) -> bool:
    a_rate = finite_float(a.get("rate_budget_boundary_frac"))
    b_rate = finite_float(b.get("rate_budget_boundary_frac"))
    a_gap = finite_float(a.get("start_gap"))
    b_gap = finite_float(b.get("start_gap"))
    a_hidden = finite_float(a.get("hidden_audit"))
    b_hidden = finite_float(b.get("hidden_audit"))
    a_success = finite_float(a.get("success_rate"), 1.0)
    b_success = finite_float(b.get("success_rate"), 1.0)
    if not all(math.isfinite(x) for x in [a_rate, b_rate, a_gap, b_gap]):
        return False
    if not math.isfinite(a_hidden):
        a_hidden = 0.0
    if not math.isfinite(b_hidden):
        b_hidden = 0.0
    if not math.isfinite(a_success):
        a_success = 1.0
    if not math.isfinite(b_success):
        b_success = 1.0
    no_worse = (
        a_rate <= b_rate + eps
        and a_gap <= b_gap + eps
        and a_hidden <= b_hidden + eps
        and a_success + eps >= b_success
    )
    strictly_better = (
        a_rate < b_rate - eps
        or a_gap < b_gap - eps
        or a_hidden < b_hidden - eps
        or a_success > b_success + eps
    )
    return no_worse and strictly_better


def add_pareto_flags(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    by_case: Dict[Tuple[str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        by_case[(str(row.get("map", "")), str(row.get("slip", "")))].append(row)
    out: List[Dict[str, object]] = []
    for _case, group in by_case.items():
        for row in group:
            dominated_by = [
                str(other.get("method", ""))
                for other in group
                if other is not row and dominates(other, row)
            ]
            out.append(
                {
                    **row,
                    "pareto_nondominated": not dominated_by,
                    "pareto_dominated_by": ";".join(dominated_by[:5]),
                }
            )
    return out


def build_summary(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[str, List[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("method_group", ""))].append(row)
    summary: List[Dict[str, object]] = []
    for group_name, group in sorted(grouped.items()):
        summary.append(
            {
                "method_group": group_name,
                "n_rows": len(group),
                "pareto_rows": sum(1 for row in group if bool(row.get("pareto_nondominated"))),
                "median_rate_budget_boundary_frac": median(
                    finite_float(row.get("rate_budget_boundary_frac")) for row in group
                ),
                "median_state_compression_ratio": median(
                    finite_float(row.get("state_compression_ratio")) for row in group
                ),
                "median_start_gap": median(finite_float(row.get("start_gap")) for row in group),
                "median_hidden_audit": median(finite_float(row.get("hidden_audit")) for row in group),
                "mean_group_feasible_rate": rate(parse_bool(row.get("group_feasible")) for row in group),
                "median_total_speedup": median(finite_float(row.get("total_speedup")) for row in group),
                "median_success_rate": median(finite_float(row.get("success_rate")) for row in group),
            }
        )
    return summary


def write_report(
    rows: Sequence[Mapping[str, object]],
    summary: Sequence[Mapping[str, object]],
    out_path: Path,
    args: argparse.Namespace,
) -> None:
    summary_columns = [
        "method_group",
        "n_rows",
        "pareto_rows",
        "median_rate_budget_boundary_frac",
        "median_state_compression_ratio",
        "median_start_gap",
        "median_hidden_audit",
        "mean_group_feasible_rate",
        "median_total_speedup",
        "median_success_rate",
    ]
    row_columns = [
        "source",
        "map",
        "slip",
        "method",
        "method_group",
        "n_states",
        "n_boundary",
        "rate_budget_boundary_frac",
        "state_compression_ratio",
        "start_gap",
        "hidden_audit",
        "success_rate",
        "group_feasible",
        "total_speedup",
        "pareto_nondominated",
        "pareto_dominated_by",
    ]
    pareto = [row for row in rows if bool(row.get("pareto_nondominated"))]
    lines = [
        "# Fair Budget Frontier",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This table normalizes full-MDP, graph-RD, group-constrained RD, and option-discovery rows into the same rate/distortion frontier vocabulary. It is an aggregation layer; it does not rerun heavy experiments.",
        "",
        f"- total normalized rows: `{len(rows)}`",
        f"- Pareto non-dominated rows: `{len(pareto)}`",
        "",
        "## Method-Group Summary",
        "",
        markdown_table(summary, summary_columns) if summary else "_No summary rows._",
        "",
        "## Pareto Rows",
        "",
        markdown_table([{col: row.get(col, "") for col in row_columns} for row in pareto], row_columns)
        if pareto
        else "_No Pareto rows._",
        "",
        "## Source Artifacts",
        "",
        f"- core benchmark: `{args.core_csv}`",
        f"- group-constrained adaptive: `{args.group_adaptive_csv}`",
        f"- option baseline frontier: `{args.option_frontier_csv}`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a fair rate/distortion frontier across graph and option baselines.")
    parser.add_argument("--core-csv", type=Path, default=Path("experiments/output/core_benchmark/core_benchmark.csv"))
    parser.add_argument(
        "--group-adaptive-csv",
        type=Path,
        default=Path("experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv"),
    )
    parser.add_argument(
        "--option-frontier-csv",
        type=Path,
        default=Path("experiments/output/option_baseline_frontier_maze_slip005/frontier_all.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/fair_budget_frontier"))
    args = parser.parse_args()

    rows = (
        normalize_core_rows(read_csv_rows(args.core_csv))
        + normalize_group_rows(read_csv_rows(args.group_adaptive_csv))
        + normalize_option_rows(read_csv_rows(args.option_frontier_csv))
    )
    rows = add_pareto_flags(rows)
    summary = build_summary(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "fair_budget_frontier.csv", rows)
    write_csv_all_fields(args.out_dir / "fair_budget_frontier_summary.csv", summary)
    (args.out_dir / "fair_budget_frontier.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, summary, args.out_dir / "summary.md", args)


if __name__ == "__main__":
    main()
