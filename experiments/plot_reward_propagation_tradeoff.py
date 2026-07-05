#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np


def read_rows(path: Path) -> List[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows: List[Dict[str, object]] = []
        for row in csv.DictReader(f):
            rows.append(dict(row))
        return rows


def as_float(row: Mapping[str, object], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def method_label(row: Mapping[str, object]) -> str:
    if row.get("planner") == "full_vi":
        return "full VI"
    method = str(row.get("method", ""))
    if method == "graph_rd_joint":
        return "RD graph"
    if method.startswith("betweenness_"):
        return "betweenness"
    if method == "turn_articulation":
        return "turn graph"
    return method


def unique_preserve(values: Sequence[str]) -> List[str]:
    out: List[str] = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def plot_metric(rows: Sequence[Mapping[str, object]], metric: str, out_path: Path, title: str) -> None:
    maps = unique_preserve([str(row["map"]) for row in rows])
    labels = unique_preserve([method_label(row) for row in rows])
    marker_by_label = {
        "full VI": "o",
        "endpoints": "s",
        "betweenness": "^",
        "RD graph": "D",
        "turn graph": "P",
    }
    line_colors = {
        label: color
        for label, color in zip(labels, plt.rcParams["axes.prop_cycle"].by_key()["color"] * 4)
    }
    values = np.asarray([as_float(row, metric) for row in rows], dtype=float)
    vmax = float(np.nanmax(values)) if len(values) else 1.0
    if not np.isfinite(vmax) or vmax <= 0.0:
        vmax = 1.0

    fig, axes = plt.subplots(
        1,
        len(maps),
        figsize=(5.6 * len(maps), 4.6),
        squeeze=False,
        constrained_layout=True,
    )
    scatter = None
    for ax, map_name in zip(axes[0], maps):
        map_rows = [row for row in rows if str(row["map"]) == map_name]
        for label in labels:
            series = [row for row in map_rows if method_label(row) == label]
            if not series:
                continue
            series = sorted(series, key=lambda row: as_float(row, "planning_backup_count"))
            x = np.asarray([max(1.0, as_float(row, "planning_backup_count")) for row in series], dtype=float)
            y = np.asarray([max(1e-12, as_float(row, "start_value_error")) for row in series], dtype=float)
            c = np.asarray([as_float(row, metric) for row in series], dtype=float)
            ax.plot(x, y, color=line_colors[label], linewidth=1.3, alpha=0.65, label=label)
            scatter = ax.scatter(
                x,
                y,
                c=c,
                vmin=0.0,
                vmax=vmax,
                cmap="viridis",
                marker=marker_by_label.get(label, "o"),
                s=42,
                edgecolors="black",
                linewidths=0.35,
                zorder=3,
            )
        ax.set_title(map_name)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Planning backup count")
        ax.set_ylabel("Start value error")
        ax.grid(True, which="both", linewidth=0.4, alpha=0.35)
    handles, labels_for_legend = axes[0][0].get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels_for_legend,
            loc="outside lower center",
            ncol=min(5, len(handles)),
            frameon=False,
        )
    if scatter is not None:
        cbar = fig.colorbar(scatter, ax=axes.ravel().tolist(), shrink=0.82, pad=0.02)
        cbar.set_label(title)
    fig.suptitle(f"Bellman Propagation Compression Colored By {title}", fontsize=13, y=1.04)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    fig.savefig(out_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def write_report(out_dir: Path, input_csv: Path, image_paths: Sequence[Path]) -> None:
    lines = [
        "# Reward Propagation Tradeoff Plots",
        "",
        f"Input: `{input_csv}`",
        "",
    ]
    for path in image_paths:
        lines.append(f"- `{path.name}`")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot backup budget vs value error, colored by distortion metrics.")
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=Path("experiments/output/reward_propagation_curve_with_graphrd/reward_propagation_curve.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/reward_propagation_tradeoff_plots"),
    )
    args = parser.parse_args()

    rows = read_rows(args.input_csv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_occ = args.out_dir / "backup_vs_value_error_colored_by_docc.png"
    out_audit = args.out_dir / "backup_vs_value_error_colored_by_audit_cvar.png"
    plot_metric(
        rows,
        metric="occupancy_struct_hidden_distinct",
        out_path=out_occ,
        title="D_occ",
    )
    plot_metric(
        rows,
        metric="struct_hidden_distinct_cvar95",
        out_path=out_audit,
        title="Audit CVaR",
    )
    write_report(args.out_dir, args.input_csv, [out_occ, out_audit])


if __name__ == "__main__":
    main()
