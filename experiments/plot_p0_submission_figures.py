#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

import thread_limits  # noqa: F401


METHOD_LABELS = {
    "baseline:dense_turn": "dense turn",
    "baseline:endpoints": "endpoints",
    "option_baseline:bottleneck": "betweenness",
    "option_baseline:coverage": "coverage",
    "ours:rd_graph": "RD Green",
    "betweenness_sqrt": "betweenness",
    "coverage_sqrt": "coverage",
    "endpoints": "endpoints",
    "graph_rd_surrogate_joint": "RD Green",
    "turn_articulation": "dense turn",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def style_axis(ax: object) -> None:
    ax.grid(True, which="major", color="#d9d9d9", linewidth=0.6, alpha=0.8)
    ax.grid(True, which="minor", color="#eeeeee", linewidth=0.4, alpha=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def annotate(ax: object, x: float, y: float, label: str, dx: int = 5, dy: int = 4) -> None:
    ax.annotate(label, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=7)


def constrained_panel(ax: object, rows: Sequence[Mapping[str, str]]) -> None:
    offsets = {
        "baseline:endpoints": (6, 12),
        "ours:rd_graph": (6, -14),
        "baseline:dense_turn": (6, 4),
        "option_baseline:bottleneck": (6, 4),
        "option_baseline:coverage": (6, 4),
    }
    selected = [
        row
        for row in rows
        if row.get("comparison_protocol") == "large_scale_compression"
        and abs(number(row.get("value_epsilon")) - 0.01) <= 1e-12
        and abs(number(row.get("audit_epsilon")) - 0.001) <= 1e-12
    ]
    for row in selected:
        method = str(row.get("method_group", ""))
        x = number(row.get("constraint_coverage_rate"))
        y = number(row.get("median_state_compression_ratio"))
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        ours = method.startswith("ours:")
        ax.scatter(
            x,
            y,
            s=90 if ours else 54,
            marker="*" if ours else "o",
            color="#c43c39" if ours else "#2878b5",
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        dx, dy = offsets.get(method, (5, 4))
        annotate(ax, x, y, METHOD_LABELS.get(method, method), dx=dx, dy=dy)
    ax.set_yscale("log")
    ax.set_xlim(0.35, 1.04)
    ax.set_ylim(15.0, 650.0)
    ax.set_xlabel("constraint coverage")
    ax.set_ylabel("median state compression")
    ax.set_title("a  Constrained frontier")
    style_axis(ax)


def runtime_panel(ax: object, rows: Sequence[Mapping[str, str]]) -> None:
    for row in rows:
        method = str(row.get("boundary_selector", ""))
        x = number(row.get("strong_planner_median_planning_speedup"))
        y = number(row.get("strong_planner_median_total_speedup"))
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        ours = method == "graph_rd_surrogate_joint"
        x_low = number(row.get("strong_planner_planning_speedup_ci95_low"), x)
        x_high = number(row.get("strong_planner_planning_speedup_ci95_high"), x)
        y_low = number(row.get("strong_planner_total_speedup_ci95_low"), y)
        y_high = number(row.get("strong_planner_total_speedup_ci95_high"), y)
        ax.errorbar(
            x,
            y,
            xerr=[[max(0.0, x - x_low)], [max(0.0, x_high - x)]],
            yerr=[[max(0.0, y - y_low)], [max(0.0, y_high - y)]],
            fmt="none",
            ecolor="#777777",
            elinewidth=0.7,
            capsize=2,
            alpha=0.75,
            zorder=2,
        )
        ax.scatter(
            x,
            y,
            s=90 if ours else 54,
            marker="*" if ours else "o",
            color="#c43c39" if ours else "#2f9e73",
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        annotate(ax, x, y, METHOD_LABELS.get(method, method))
    ax.axhline(1.0, color="#333333", linestyle="--", linewidth=0.8)
    ax.axvline(1.0, color="#777777", linestyle=":", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("graph-planning speedup vs sparse VI")
    ax.set_ylabel("single-task total speedup")
    ax.set_title("b  Planning gain, upfront loss")
    style_axis(ax)


def decomposition_panel(ax: object, rows: Sequence[Mapping[str, str]]) -> None:
    import numpy as np

    converged = [row for row in rows if row.get("config_label") == "converged_k256_i256"]
    fields = [
        ("option_restriction_bias", "option"),
        ("boundary_abstraction_bias", "boundary"),
        ("kernel_actual_gap", "kernel"),
        ("planning_actual_gap", "planning"),
    ]
    medians: List[float] = []
    percentiles: List[float] = []
    labels: List[str] = []
    for field, label in fields:
        values = [
            number(row.get(field)) / max(1.0, number(row.get("value_scale"), 1.0))
            for row in converged
        ]
        values = [value for value in values if math.isfinite(value)]
        med = float(np.median(values))
        p95 = float(np.quantile(values, 0.95))
        medians.append(max(med, 1e-15))
        percentiles.append(max(p95, 1e-15))
        labels.append(label)
    positions = np.arange(len(labels))
    colors = ["#d95f5f", "#e5a84b", "#4c78a8", "#5b9e6f"]
    for position, med, p95, color in zip(positions, medians, percentiles, colors):
        ax.vlines(position, med, p95, color=color, linewidth=2.2, alpha=0.75)
        ax.scatter(position, med, s=42, marker="o", color=color, edgecolor="white", zorder=3)
        ax.scatter(position, p95, s=52, marker="^", color=color, edgecolor="white", zorder=3)
    ax.scatter([], [], s=42, marker="o", color="#777777", label="median")
    ax.scatter([], [], s=52, marker="^", color="#777777", label="95th percentile")
    ax.legend(loc="upper right", frameon=False)
    ax.set_xticks(positions, labels)
    ax.set_yscale("log")
    ax.set_ylabel("normalized gap (median; 95th percentile)")
    ax.set_title("c  End-to-end error accounting")
    style_axis(ax)


def external_panel(ax: object, rows: Sequence[Mapping[str, str]]) -> None:
    offsets = {
        "Taxi-v4": (7, 6),
        "CliffWalking-v1": (7, -13),
        "MiniGrid-DoorKey-5x5-v0": (7, 6),
        "MiniGrid-FourRooms-v0": (7, 5),
        "MiniGrid-MultiRoom-N2-S4-v0": (7, -12),
        "PointMaze-umaze-b3": (7, 5),
        "FrozenLake8x8-v1": (7, -12),
    }
    envs = sorted({str(row.get("env", "")) for row in rows if row.get("env")})
    for env in envs:
        candidates = [
            row
            for row in rows
            if row.get("env") == env
            and row.get("method") == "green_group_rd"
            and row.get("option_mode") == "primitive"
        ]
        feasible = [row for row in candidates if number(row.get("group_feasible_rate")) == 1.0]
        pool = feasible or candidates
        if not pool:
            continue
        row = min(pool, key=lambda item: number(item.get("median_normalized_start_gap"), float("inf")))
        x = number(row.get("median_state_compression_ratio"))
        y = number(row.get("median_normalized_start_gap"))
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        failure = env.startswith("Taxi") or number(row.get("group_feasible_rate")) < 1.0
        ax.scatter(
            x,
            y,
            s=72 if env.startswith("Taxi") else 48,
            marker="X" if env.startswith("Taxi") else "o",
            color="#c43c39" if failure else "#6f62a6",
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        short = env.replace("MiniGrid-", "MG-").replace("-v0", "").replace("-v1", "")
        dx, dy = offsets.get(env, (5, 4))
        annotate(ax, x, y, short, dx=dx, dy=dy)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.045, 3.5)
    ax.set_xlabel("state compression")
    ax.set_ylabel("median normalized start gap")
    ax.set_title("d  External finite-MDP stress")
    style_axis(ax)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper-facing P0 evidence panels.")
    parser.add_argument(
        "--frontier-csv",
        type=Path,
        default=Path("experiments/output/fair_budget_frontier/epsilon_constrained_frontier.csv"),
    )
    parser.add_argument(
        "--runtime-csv",
        type=Path,
        default=Path("experiments/output/submission_main_table/runtime_by_boundary_selector.csv"),
    )
    parser.add_argument(
        "--end-to-end-csv",
        type=Path,
        default=Path("experiments/output/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv"),
    )
    parser.add_argument(
        "--general-env-csv",
        type=Path,
        default=Path("experiments/output/general_env_benchmark/general_env_aggregate.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/p0_submission_figures"),
    )
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.2), dpi=180)
    constrained_panel(axes[0, 0], read_csv(args.frontier_csv))
    runtime_panel(axes[0, 1], read_csv(args.runtime_csv))
    decomposition_panel(axes[1, 0], read_csv(args.end_to_end_csv))
    external_panel(axes[1, 1], read_csv(args.general_env_csv))
    fig.tight_layout(pad=1.4, w_pad=1.8, h_pad=1.8)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    png = args.out_dir / "p0_evidence_panel.png"
    pdf = args.out_dir / "p0_evidence_panel.pdf"
    fig.savefig(png, bbox_inches="tight", pad_inches=0.06)
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    (args.out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# P0 Submission Figures",
                "",
                f"Generated: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "The four panels show the canonical constrained frontier, matched strong-planner accounting, converged end-to-end error decomposition, and five-seed external finite-MDP stress tests.",
                "",
                f"- PNG: `{png}`",
                f"- PDF: `{pdf}`",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
