#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


METHOD_PAIRS = [
    ("certified", "adaptive_topk_certified_refine", "surrogate_topk_certified_refine"),
    ("exact", "adaptive_topk_exact_refine", "surrogate_topk_exact_refine"),
]


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_csv_globs(patterns: Sequence[str]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for pattern in patterns:
        for name in sorted(glob.glob(pattern)):
            source_path = Path(name)
            for row in read_csv_rows(source_path):
                enriched = dict(row)
                enriched.setdefault("source_file", str(source_path))
                rows.append(enriched)
    return rows


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


def objective_tuple(row: Mapping[str, object]) -> Tuple[float, float, int, float]:
    return (
        finite_float(row.get("group_total_violation"), 0.0),
        finite_float(row.get("group_max_violation"), 0.0),
        int(finite_float(row.get("n_boundary"), 0.0)),
        finite_float(row.get("start_gap"), 0.0),
    )


def lex_regret(reference: Tuple[float, float, int, float], candidate: Tuple[float, float, int, float]) -> float:
    """Positive if `candidate` is lexicographically worse than `reference`."""
    for ref_value, cand_value in zip(reference, candidate):
        gap = float(cand_value) - float(ref_value)
        if abs(gap) > 1e-12:
            return gap
    return 0.0


def row_key(row: Mapping[str, object]) -> Tuple[str, str]:
    return (str(row.get("map", "")), str(row.get("slip", "")))


def collect_step_info(step_rows: Sequence[Mapping[str, str]]) -> Dict[Tuple[str, str, str, str], Dict[str, object]]:
    grouped: Dict[Tuple[str, str, str, str], List[Mapping[str, str]]] = defaultdict(list)
    for row in step_rows:
        key = (
            str(row.get("map", "")),
            str(row.get("slip", "")),
            str(row.get("method", "")),
            str(row.get("top_k", "")),
        )
        grouped[key].append(row)
    out: Dict[Tuple[str, str, str, str], Dict[str, object]] = {}
    for key, rows in grouped.items():
        selected = [row for row in rows if str(row.get("selected_state", "")).strip()]
        used = [finite_float(row.get("adaptive_topk_used")) for row in rows]
        used = [value for value in used if math.isfinite(value)]
        ranks = [str(row.get("proposal_rank", "")) for row in selected if str(row.get("proposal_rank", "")).strip()]
        decisions = [str(row.get("adaptive_decision", "")) for row in rows if str(row.get("adaptive_decision", "")).strip()]
        out[key] = {
            "n_steps": len(rows),
            "selected_ranks": ";".join(ranks),
            "first_selected_rank": ranks[0] if ranks else "",
            "adaptive_decisions": ";".join(decisions),
            "adaptive_step_k_used_max": max(used) if used else "",
            "adaptive_step_k_used_median": median(used),
            "final_step_stop_reason": rows[-1].get("stop_reason", "") if rows else "",
        }
    return out


def build_paired_tables(
    adaptive_rows: Sequence[Mapping[str, str]],
    fixed_rows: Sequence[Mapping[str, str]],
    adaptive_step_info: Mapping[Tuple[str, str, str, str], Mapping[str, object]],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    paired: List[Dict[str, object]] = []
    regret: List[Dict[str, object]] = []
    failures: List[Dict[str, object]] = []
    adaptive_by_method = {
        (row.get("method", ""), row.get("top_k", ""), *row_key(row)): row
        for row in adaptive_rows
        if not row.get("error")
    }
    fixed_by_method = {
        (row.get("method", ""), row.get("top_k", ""), *row_key(row)): row
        for row in fixed_rows
        if not row.get("error")
    }
    all_keys = sorted({row_key(row) for row in adaptive_rows if not row.get("error")})
    for mode, adaptive_method, fixed_method in METHOD_PAIRS:
        for map_name, slip in all_keys:
            adaptive = adaptive_by_method.get((adaptive_method, "4", map_name, slip))
            fixed = fixed_by_method.get((fixed_method, "4", map_name, slip))
            if adaptive is None or fixed is None:
                continue
            adaptive_feasible = parse_bool(adaptive.get("group_all_feasible"))
            fixed_feasible = parse_bool(fixed.get("group_all_feasible"))
            fixed_obj = objective_tuple(fixed)
            adaptive_obj = objective_tuple(adaptive)
            regret_value = lex_regret(fixed_obj, adaptive_obj)
            step = adaptive_step_info.get((map_name, slip, adaptive_method, "4"), {})
            boundary_match = str(fixed.get("boundary", "")) == str(adaptive.get("boundary", ""))
            feasible_match = adaptive_feasible == fixed_feasible
            row = {
                "mode": mode,
                "map": map_name,
                "slip": slip,
                "fixed_method": fixed_method,
                "adaptive_method": adaptive_method,
                "fixed_topk": 4,
                "adaptive_cap": 4,
                "fixed_top4_feasible": fixed_feasible,
                "adaptive_topk_feasible": adaptive_feasible,
                "feasible_match": feasible_match,
                "boundary_match": boundary_match,
                "fixed_boundary": fixed.get("boundary", ""),
                "adaptive_boundary": adaptive.get("boundary", ""),
                "adaptive_k_used_mean": finite_float(adaptive.get("adaptive_topk_used_mean")),
                "adaptive_k_used_max": finite_float(adaptive.get("adaptive_topk_used_max")),
                "adaptive_cap_hits": int(finite_float(adaptive.get("adaptive_topk_cap_hits"), 0.0)),
                "adaptive_selected_ranks": step.get("selected_ranks", ""),
                "adaptive_first_selected_rank": step.get("first_selected_rank", ""),
                "adaptive_decisions": step.get("adaptive_decisions", ""),
                "fixed_selection_time_sec": finite_float(fixed.get("selection_time_sec")),
                "adaptive_selection_time_sec": finite_float(adaptive.get("selection_time_sec")),
                "selection_speedup_fixed_over_adaptive": finite_float(fixed.get("selection_time_sec"), 0.0)
                / max(1e-12, finite_float(adaptive.get("selection_time_sec"), 0.0)),
                "fixed_exact_refine_calls": int(finite_float(fixed.get("exact_refine_calls"), 0.0)),
                "adaptive_exact_refine_calls": int(finite_float(adaptive.get("exact_refine_calls"), 0.0)),
                "fixed_group_total_violation": finite_float(fixed.get("group_total_violation")),
                "adaptive_group_total_violation": finite_float(adaptive.get("group_total_violation")),
                "fixed_start_gap": finite_float(fixed.get("start_gap")),
                "adaptive_start_gap": finite_float(adaptive.get("start_gap")),
                "lexicographic_regret_vs_fixed": regret_value,
                "group_total_violation_delta": finite_float(adaptive.get("group_total_violation"), 0.0)
                - finite_float(fixed.get("group_total_violation"), 0.0),
                "start_gap_delta": finite_float(adaptive.get("start_gap"), 0.0)
                - finite_float(fixed.get("start_gap"), 0.0),
                "fixed_stop_reason": fixed.get("stop_reason", ""),
                "adaptive_stop_reason": adaptive.get("stop_reason", ""),
            }
            paired.append(row)
            regret.append(
                {
                    "mode": mode,
                    "map": map_name,
                    "slip": slip,
                    "both_feasible": adaptive_feasible is True and fixed_feasible is True,
                    "feasible_match": feasible_match,
                    "boundary_match": boundary_match,
                    "lexicographic_regret_vs_fixed": regret_value,
                    "group_total_violation_delta": row["group_total_violation_delta"],
                    "start_gap_delta": row["start_gap_delta"],
                    "adaptive_selected_ranks": row["adaptive_selected_ranks"],
                    "adaptive_decisions": row["adaptive_decisions"],
                }
            )
            if adaptive_feasible is not True:
                if fixed_feasible is True:
                    failure_class = "paired_mismatch_adaptive_trajectory"
                elif "no_positive" in str(adaptive.get("stop_reason", "")):
                    failure_class = "cap_exhausted_no_positive_feasible_gain"
                elif "budget" in str(adaptive.get("stop_reason", "")):
                    failure_class = "cap_envelope_or_boundary_budget_not_met"
                else:
                    failure_class = "fixed_cap_no_feasible_final_graph"
                failures.append(
                    {
                        "mode": mode,
                        "map": map_name,
                        "slip": slip,
                        "failure_class": failure_class,
                        "fixed_top4_feasible": fixed_feasible,
                        "adaptive_topk_feasible": adaptive_feasible,
                        "fixed_group_total_violation": finite_float(fixed.get("group_total_violation")),
                        "adaptive_group_total_violation": finite_float(adaptive.get("group_total_violation")),
                        "adaptive_k_used_mean": row["adaptive_k_used_mean"],
                        "adaptive_k_used_max": row["adaptive_k_used_max"],
                        "adaptive_cap_hits": row["adaptive_cap_hits"],
                        "fixed_stop_reason": fixed.get("stop_reason", ""),
                        "adaptive_stop_reason": adaptive.get("stop_reason", ""),
                        "adaptive_decisions": row["adaptive_decisions"],
                    }
                )
    return paired, regret, failures


def build_k_histogram(step_rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    buckets: Dict[Tuple[str, str, str], List[Mapping[str, str]]] = defaultdict(list)
    for row in step_rows:
        used = str(row.get("adaptive_topk_used", "")).strip()
        if not used:
            continue
        key = (str(row.get("method", "")), str(row.get("top_k", "")), used)
        buckets[key].append(row)
    out: List[Dict[str, object]] = []
    for (method, top_k, used), rows in sorted(buckets.items(), key=lambda item: (item[0][0], item[0][1], finite_float(item[0][2]))):
        decisions = Counter(str(row.get("adaptive_decision", "")) for row in rows)
        out.append(
            {
                "method": method,
                "top_k_cap": top_k,
                "k_used": int(finite_float(used, 0.0)),
                "n_steps": len(rows),
                "n_feasible_stop": decisions.get("feasible", 0),
                "n_clear_margin_stop": decisions.get("clear_margin", 0),
                "n_cap_hit": decisions.get("cap", 0),
                "n_cap_without_selected_feasible": sum(
                    1
                    for row in rows
                    if row.get("adaptive_decision") == "cap"
                    and parse_bool(row.get("selected_all_groups_feasible")) is not True
                ),
                "n_expand_marker": decisions.get("expand", 0),
            }
        )
    return out


def summarize_method_rows(rows: Sequence[Mapping[str, str]], source: str) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, str], List[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("error"):
            continue
        groups[(str(row.get("method", "")), str(row.get("top_k", "")))].append(row)
    out: List[Dict[str, object]] = []
    for (method, top_k), group in sorted(groups.items(), key=lambda item: (item[0][0], finite_float(item[0][1], -1.0))):
        out.append(
            {
                "source": source,
                "method": method,
                "top_k_or_cap": top_k,
                "n_rows": len(group),
                "feasible_rate": sum(1 for row in group if parse_bool(row.get("group_all_feasible")) is True)
                / max(1, len(group)),
                "median_selection_time_sec": median(finite_float(row.get("selection_time_sec")) for row in group),
                "median_upfront_time_sec": median(finite_float(row.get("upfront_time_sec")) for row in group),
                "total_exact_refine_calls": sum(int(finite_float(row.get("exact_refine_calls"), 0.0)) for row in group),
                "total_refined_candidates": sum(int(finite_float(row.get("refined_candidates_total"), 0.0)) for row in group),
                "median_adaptive_topk_used_mean": median(finite_float(row.get("adaptive_topk_used_mean")) for row in group),
                "max_adaptive_topk_used": max(
                    (finite_float(row.get("adaptive_topk_used_max"), 0.0) for row in group),
                    default=float("nan"),
                ),
            }
        )
    return out


def build_fixedk_vs_adaptive_summary(
    adaptive_rows: Sequence[Mapping[str, str]],
    fixed_rows: Sequence[Mapping[str, str]],
) -> List[Dict[str, object]]:
    fixed = [
        row for row in fixed_rows
        if row.get("method") in {"surrogate_topk_certified_refine", "surrogate_topk_exact_refine"}
    ]
    adaptive = [
        row for row in adaptive_rows
        if row.get("method") in {"adaptive_topk_certified_refine", "adaptive_topk_exact_refine"}
    ]
    return summarize_method_rows(fixed, "fixed_topk_ablation") + summarize_method_rows(adaptive, "adaptive_topk")


def build_failure_summary(failures: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, str], List[Mapping[str, object]]] = defaultdict(list)
    for row in failures:
        groups[(str(row.get("mode", "")), str(row.get("failure_class", "")))].append(row)
    out: List[Dict[str, object]] = []
    for (mode, failure_class), rows in sorted(groups.items()):
        out.append(
            {
                "mode": mode,
                "failure_class": failure_class,
                "n_rows": len(rows),
                "max_adaptive_group_total_violation": max(
                    (finite_float(row.get("adaptive_group_total_violation"), 0.0) for row in rows),
                    default=float("nan"),
                ),
                "maps": ";".join(sorted({str(row.get("map", "")) for row in rows})),
                "slips": ";".join(sorted({str(row.get("slip", "")) for row in rows})),
            }
        )
    return out


def write_report(
    *,
    out_dir: Path,
    paired: Sequence[Mapping[str, object]],
    k_histogram: Sequence[Mapping[str, object]],
    fixedk_summary: Sequence[Mapping[str, object]],
    regret: Sequence[Mapping[str, object]],
    failure_summary: Sequence[Mapping[str, object]],
) -> None:
    paired_match = sum(1 for row in paired if parse_bool(row.get("feasible_match")) is True)
    paired_total = len(paired)
    certified = [row for row in paired if row.get("mode") == "certified"]
    certified_speedups = [finite_float(row.get("selection_speedup_fixed_over_adaptive")) for row in certified]
    lines = [
        "# Adaptive Top-K Diagnostics",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report checks the feasible-envelope claim for adaptive top-k refinement against the fixed top-4 ablation. It treats adaptive top-k as a feasible-discovery backend, not as a proof of score-optimal split selection.",
        "",
        f"- paired feasible matches: `{paired_match}/{paired_total}`",
        f"- certified median fixed/adaptive selection speedup: `{median(certified_speedups):.4g}x`",
        "",
        "## Paired Feasibility",
        "",
        markdown_table(
            [
                {
                    key: row.get(key, "")
                    for key in [
                        "mode",
                        "map",
                        "slip",
                        "fixed_top4_feasible",
                        "adaptive_topk_feasible",
                        "feasible_match",
                        "adaptive_k_used_mean",
                        "selection_speedup_fixed_over_adaptive",
                        "lexicographic_regret_vs_fixed",
                    ]
                }
                for row in paired
            ],
            [
                "mode",
                "map",
                "slip",
                "fixed_top4_feasible",
                "adaptive_topk_feasible",
                "feasible_match",
                "adaptive_k_used_mean",
                "selection_speedup_fixed_over_adaptive",
                "lexicographic_regret_vs_fixed",
            ],
        )
        if paired
        else "_No paired rows found._",
        "",
        "## K-Used Histogram",
        "",
        markdown_table(k_histogram, ["method", "top_k_cap", "k_used", "n_steps", "n_feasible_stop", "n_cap_hit", "n_cap_without_selected_feasible"])
        if k_histogram
        else "_No adaptive step rows found._",
        "",
        "## Fixed-K Vs Adaptive Cap",
        "",
        markdown_table(
            fixedk_summary,
            [
                "source",
                "method",
                "top_k_or_cap",
                "n_rows",
                "feasible_rate",
                "median_selection_time_sec",
                "total_exact_refine_calls",
                "total_refined_candidates",
                "median_adaptive_topk_used_mean",
            ],
        )
        if fixedk_summary
        else "_No fixed/adaptive summary rows found._",
        "",
        "## Score-Regret Proxy",
        "",
        markdown_table(
            regret,
            [
                "mode",
                "map",
                "slip",
                "both_feasible",
                "feasible_match",
                "boundary_match",
                "lexicographic_regret_vs_fixed",
                "group_total_violation_delta",
                "start_gap_delta",
            ],
        )
        if regret
        else "_No regret rows found._",
        "",
        "## Failure Summary",
        "",
        markdown_table(failure_summary, ["mode", "failure_class", "n_rows", "max_adaptive_group_total_violation", "maps", "slips"])
        if failure_summary
        else "_No adaptive failures found._",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build diagnostics for adaptive feasible top-k refinement.")
    parser.add_argument("--adaptive-csv", type=Path, default=Path("experiments/output/hybrid_adaptive_topk_refine/hybrid_surrogate_refine.csv"))
    parser.add_argument("--fixed-csv", type=Path, default=Path("experiments/output/hybrid_topk_ablation/hybrid_surrogate_refine.csv"))
    parser.add_argument(
        "--adaptive-steps-glob",
        nargs="*",
        default=[
            "experiments/output/scheduler_large_runs/hybrid_adaptive_safe_xl_20260707_1410/*/hybrid_adaptive_topk_refine/hybrid_surrogate_refine_steps.csv",
        ],
    )
    parser.add_argument(
        "--fixed-steps-glob",
        nargs="*",
        default=[
            "experiments/output/scheduler_large_runs/hybrid_topk_xl_20260707_1228_v2/*/hybrid_topk_ablation/hybrid_surrogate_refine_steps.csv",
        ],
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/adaptive_topk_diagnostics"))
    args = parser.parse_args()

    adaptive_rows = read_csv_rows(args.adaptive_csv)
    fixed_rows = read_csv_rows(args.fixed_csv)
    adaptive_steps = read_csv_globs(args.adaptive_steps_glob)
    _fixed_steps = read_csv_globs(args.fixed_steps_glob)
    adaptive_step_info = collect_step_info(adaptive_steps)

    paired, regret, failures = build_paired_tables(adaptive_rows, fixed_rows, adaptive_step_info)
    k_histogram = build_k_histogram(adaptive_steps)
    fixedk_summary = build_fixedk_vs_adaptive_summary(adaptive_rows, fixed_rows)
    failure_summary = build_failure_summary(failures)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "paired_equivalence.csv", paired)
    write_csv_all_fields(args.out_dir / "k_used_histogram.csv", k_histogram)
    write_csv_all_fields(args.out_dir / "fixedk_vs_adaptive_summary.csv", fixedk_summary)
    write_csv_all_fields(args.out_dir / "score_regret.csv", regret)
    write_csv_all_fields(args.out_dir / "failure_modes.csv", failures)
    write_csv_all_fields(args.out_dir / "failure_mode_summary.csv", failure_summary)
    (args.out_dir / "adaptive_topk_diagnostics.json").write_text(
        json.dumps(
            {
                "paired_equivalence": paired,
                "k_used_histogram": k_histogram,
                "fixedk_vs_adaptive_summary": fixedk_summary,
                "score_regret": regret,
                "failure_modes": failures,
                "failure_mode_summary": failure_summary,
            },
            indent=2,
            default=json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        out_dir=args.out_dir,
        paired=paired,
        k_histogram=k_histogram,
        fixedk_summary=fixedk_summary,
        regret=regret,
        failure_summary=failure_summary,
    )
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
