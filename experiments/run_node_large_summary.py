#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

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


def group_by(rows: Sequence[Mapping[str, str]], key: str) -> Dict[str, List[Mapping[str, str]]]:
    grouped: Dict[str, List[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, ""))].append(row)
    return dict(grouped)


def summarize_large_scale(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for method, group in sorted(group_by(rows, "method_spec").items()):
        ok = [row for row in group if not row.get("error")]
        out.append(
            {
                "method_spec": method,
                "n_rows": len(ok),
                "max_n_states": max((int(finite_float(row.get("n_states"), 0.0)) for row in ok), default=0),
                "median_state_compression": median(finite_float(row.get("state_compression_ratio")) for row in ok),
                "median_planning_speedup": median(finite_float(row.get("planning_time_speedup_vs_full_vi")) for row in ok),
                "best_planning_speedup": max(
                    (finite_float(row.get("planning_time_speedup_vs_full_vi")) for row in ok),
                    default=float("nan"),
                ),
                "median_total_speedup": median(finite_float(row.get("total_time_speedup_vs_full_vi")) for row in ok),
                "best_total_speedup": max(
                    (finite_float(row.get("total_time_speedup_vs_full_vi")) for row in ok),
                    default=float("nan"),
                ),
                "max_start_gap": max((finite_float(row.get("start_gap"), 0.0) for row in ok), default=float("nan")),
                "max_tail_bound": max(
                    (finite_float(row.get("first_hit_tail_bound_max"), 0.0) for row in ok),
                    default=float("nan"),
                ),
            }
        )
    return out


def summarize_amortized(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    grouped: Dict[tuple[str, str], List[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("method_spec", "")), str(row.get("task_count", "")))].append(row)
    out: List[Dict[str, object]] = []
    for (method, task_count), group in sorted(grouped.items(), key=lambda item: (item[0][0], int(item[0][1] or 0))):
        out.append(
            {
                "method_spec": method,
                "task_count": task_count,
                "n_rows": len(group),
                "median_amortized_speedup": median(
                    finite_float(row.get("amortized_speedup_vs_full_vi")) for row in group
                ),
                "best_amortized_speedup": max(
                    (finite_float(row.get("amortized_speedup_vs_full_vi")) for row in group),
                    default=float("nan"),
                ),
                "median_planning_only_speedup": median(
                    finite_float(row.get("planning_only_speedup_vs_full_vi")) for row in group
                ),
                "median_break_even_task_count": median(
                    finite_float(row.get("break_even_task_count_estimate")) for row in group
                ),
                "median_backup_compression": median(finite_float(row.get("backup_compression_ratio")) for row in group),
                "max_start_gap": max((finite_float(row.get("start_gap_max"), 0.0) for row in group), default=float("nan")),
            }
        )
    return out


def summarize_edge_reward(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    grouped: Dict[tuple[str, str], List[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("variant", "")), str(row.get("task_count", "")))].append(row)
    out: List[Dict[str, object]] = []
    for (variant, task_count), group in sorted(grouped.items(), key=lambda item: (item[0][0], int(item[0][1] or 0))):
        out.append(
            {
                "variant": variant,
                "task_count": task_count,
                "n_rows": len(group),
                "median_amortized_speedup": median(
                    finite_float(row.get("amortized_speedup_vs_full_vi")) for row in group
                ),
                "best_amortized_speedup": max(
                    (finite_float(row.get("amortized_speedup_vs_full_vi")) for row in group),
                    default=float("nan"),
                ),
                "median_break_even_tasks": median(finite_float(row.get("break_even_num_tasks")) for row in group),
                "median_goal_interface": median(finite_float(row.get("goal_option_interface_size")) for row in group),
                "median_goal_policies": median(finite_float(row.get("n_goal_policies")) for row in group),
                "max_start_gap": max((finite_float(row.get("start_gap_max"), 0.0) for row in group), default=float("nan")),
            }
        )
    return out


def summarize_random(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for method, group in sorted(group_by(rows, "method").items()):
        ok = [row for row in group if not row.get("error")]
        out.append(
            {
                "method": method,
                "n_rows": len(ok),
                "feasible_rate": rate(parse_bool(row.get("group_all_feasible")) for row in ok),
                "median_n_boundary": median(finite_float(row.get("n_boundary")) for row in ok),
                "median_state_compression": median(finite_float(row.get("state_compression_ratio")) for row in ok),
                "median_selection_time_sec": median(finite_float(row.get("selection_time_sec")) for row in ok),
                "median_total_speedup": median(finite_float(row.get("total_speedup")) for row in ok),
                "max_group_total_violation": max(
                    (finite_float(row.get("group_total_violation"), 0.0) for row in ok),
                    default=float("nan"),
                ),
                "max_start_gap": max((finite_float(row.get("start_gap"), 0.0) for row in ok), default=float("nan")),
            }
        )
    return out


def summarize_threads(rows: Sequence[Mapping[str, str]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for size, group in sorted(group_by(rows, "size").items(), key=lambda item: int(item[0] or 0)):
        best = min(group, key=lambda row: finite_float(row.get("sec_per_solve"), float("inf")))
        out.append(
            {
                "size": size,
                "best_threads": best.get("threads", ""),
                "best_sec_per_solve": finite_float(best.get("sec_per_solve")),
                "best_speedup_vs_1_thread": finite_float(best.get("speedup_vs_1_thread")),
                "n_thread_settings": len(group),
            }
        )
    return out


def write_report(
    out_path: Path,
    large_rows: Sequence[Mapping[str, object]],
    amortized_rows: Sequence[Mapping[str, object]],
    random_rows: Sequence[Mapping[str, object]],
    thread_rows: Sequence[Mapping[str, object]],
    edge_reward_rows: Sequence[Mapping[str, object]],
    args: argparse.Namespace,
) -> None:
    large_columns = [
        "method_spec",
        "n_rows",
        "max_n_states",
        "median_state_compression",
        "median_planning_speedup",
        "best_planning_speedup",
        "median_total_speedup",
        "best_total_speedup",
        "max_start_gap",
        "max_tail_bound",
    ]
    amortized_columns = [
        "method_spec",
        "task_count",
        "n_rows",
        "median_amortized_speedup",
        "best_amortized_speedup",
        "median_planning_only_speedup",
        "median_break_even_task_count",
        "median_backup_compression",
        "max_start_gap",
    ]
    random_columns = [
        "method",
        "n_rows",
        "feasible_rate",
        "median_n_boundary",
        "median_state_compression",
        "median_selection_time_sec",
        "median_total_speedup",
        "max_group_total_violation",
        "max_start_gap",
    ]
    thread_columns = [
        "size",
        "best_threads",
        "best_sec_per_solve",
        "best_speedup_vs_1_thread",
        "n_thread_settings",
    ]
    edge_reward_columns = [
        "variant",
        "task_count",
        "n_rows",
        "median_amortized_speedup",
        "best_amortized_speedup",
        "median_break_even_tasks",
        "median_goal_interface",
        "median_goal_policies",
        "max_start_gap",
    ]
    best_amortized = max(
        (finite_float(row.get("best_amortized_speedup")) for row in amortized_rows),
        default=float("nan"),
    )
    best_large_total = max(
        (finite_float(row.get("best_total_speedup")) for row in large_rows),
        default=float("nan"),
    )
    best_edge_reward = max(
        (finite_float(row.get("best_amortized_speedup")) for row in edge_reward_rows),
        default=float("nan"),
    )
    lines = [
        "# Node Large Paper Summary",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report aggregates the large CPU-node experiments: scale compression, multi-task amortization, random-maze robustness, and thread tuning.",
        "",
        f"- best large-scale total speedup: `{best_large_total:.4g}x`",
        f"- best amortized multi-task speedup: `{best_amortized:.4g}x`",
        f"- best edge-reward/terminal extension speedup: `{best_edge_reward:.4g}x`",
        "",
        "## Thread Scaling",
        "",
        markdown_table(thread_rows, thread_columns) if thread_rows else "_No thread scaling rows._",
        "",
        "## Large-Scale Compression",
        "",
        markdown_table(large_rows, large_columns) if large_rows else "_No large-scale rows._",
        "",
        "## Multi-Task Amortization",
        "",
        markdown_table(amortized_rows, amortized_columns) if amortized_rows else "_No amortized rows._",
        "",
        "## Edge Reward And Terminal Extension",
        "",
        markdown_table(edge_reward_rows, edge_reward_columns) if edge_reward_rows else "_No edge-reward rows._",
        "",
        "## Random Maze Robustness",
        "",
        markdown_table(random_rows, random_columns) if random_rows else "_No random-maze rows._",
        "",
        "## Source Artifacts",
        "",
        f"- large scale: `{args.large_scale_csv}`",
        f"- amortized: `{args.amortized_csv}`",
        f"- edge reward: `{args.edge_reward_csv}`",
        f"- random maze: `{args.random_maze_csv}`",
        f"- thread scaling: `{args.thread_scaling_csv}`",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate large CPU-node paper experiments.")
    parser.add_argument(
        "--large-scale-csv",
        type=Path,
        default=Path("experiments/output/node_large_runs/latest/large_scale_compression/large_scale_compression.csv"),
    )
    parser.add_argument(
        "--amortized-csv",
        type=Path,
        default=Path("experiments/output/node_large_runs/latest/amortized_multitask/amortized_multitask.csv"),
    )
    parser.add_argument(
        "--edge-reward-csv",
        type=Path,
        default=Path("experiments/output/node_large_runs/latest/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv"),
    )
    parser.add_argument(
        "--random-maze-csv",
        type=Path,
        default=Path("experiments/output/node_large_runs/latest/random_maze_generalization/random_maze_generalization.csv"),
    )
    parser.add_argument(
        "--thread-scaling-csv",
        type=Path,
        default=Path("experiments/output/node_large_runs/latest/linear_solver_thread_scaling/linear_solver_thread_scaling.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/node_large_paper_summary"))
    args = parser.parse_args()

    large_rows = summarize_large_scale(read_csv_rows(args.large_scale_csv))
    amortized_rows = summarize_amortized(read_csv_rows(args.amortized_csv))
    edge_reward_rows = summarize_edge_reward(read_csv_rows(args.edge_reward_csv))
    random_rows = summarize_random(read_csv_rows(args.random_maze_csv))
    thread_rows = summarize_threads(read_csv_rows(args.thread_scaling_csv))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "large_scale_summary.csv", large_rows)
    write_csv_all_fields(args.out_dir / "amortized_summary.csv", amortized_rows)
    write_csv_all_fields(args.out_dir / "edge_reward_summary.csv", edge_reward_rows)
    write_csv_all_fields(args.out_dir / "random_maze_summary.csv", random_rows)
    write_csv_all_fields(args.out_dir / "thread_scaling_summary.csv", thread_rows)
    (args.out_dir / "node_large_paper_summary.json").write_text(
        json.dumps(
            {
                "large_scale": large_rows,
                "amortized": amortized_rows,
                "edge_reward": edge_reward_rows,
                "random_maze": random_rows,
                "thread_scaling": thread_rows,
            },
            indent=2,
            default=json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(args.out_dir / "summary.md", large_rows, amortized_rows, random_rows, thread_rows, edge_reward_rows, args)


if __name__ == "__main__":
    main()
