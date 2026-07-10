#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import thread_limits  # noqa: F401


INK = "#20252b"
MUTED = "#68717c"
LINE = "#b8c0c8"
PANEL = "#f7f8fa"
BLUE = "#4c78a8"
TEAL = "#4f9b8f"
GOLD = "#d5a23f"
RED = "#c65d57"
PURPLE = "#7b6da8"


def panel_box(ax: object, x: float, y: float, w: float, h: float) -> None:
    from matplotlib.patches import FancyBboxPatch

    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.006,rounding_size=0.008",
            facecolor=PANEL,
            edgecolor=LINE,
            linewidth=0.8,
        )
    )


def arrow(ax: object, start: Sequence[float], end: Sequence[float], color: str = MUTED) -> None:
    from matplotlib.patches import FancyArrowPatch

    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=1.0,
            color=color,
            shrinkA=1.5,
            shrinkB=1.5,
        )
    )


def primitive_panel(ax: object, x: float, y: float, w: float, h: float) -> None:
    from matplotlib.patches import Rectangle

    panel_box(ax, x, y, w, h)
    ax.text(x + 0.012, y + h - 0.035, "a", weight="bold", fontsize=8, color=INK)
    ax.text(x + 0.038, y + h - 0.035, "Primitive finite MDP", weight="bold", fontsize=7.4, color=INK)

    cols, rows = 4, 4
    gx, gy = x + 0.028, y + 0.40
    cell = (w - 0.056) / cols
    walls = {(1, 0), (1, 1), (1, 3), (3, 1)}
    for row in range(rows):
        for col in range(cols):
            px = gx + col * cell
            py = gy + (rows - 1 - row) * cell
            wall = (col, row) in walls
            ax.add_patch(
                Rectangle(
                    (px, py),
                    cell,
                    cell,
                    facecolor="#d9dde2" if wall else "white",
                    edgecolor="#c7cdd4",
                    linewidth=0.45,
                )
            )
            if not wall:
                ax.plot(px + cell / 2, py + cell / 2, "o", ms=1.7, color="#aeb6bf")

    start = (gx + cell / 2, gy + cell / 2)
    goal = (gx + (cols - 0.5) * cell, gy + (rows - 0.5) * cell)
    ax.plot(*start, marker="s", ms=5.0, color=BLUE, mec="white", mew=0.5, zorder=4)
    ax.plot(*goal, marker="*", ms=7.0, color=RED, mec="white", mew=0.4, zorder=4)
    for col, row in ((0, 1), (2, 2), (2, 0)):
        px = gx + (col + 0.5) * cell
        py = gy + (rows - row - 0.5) * cell
        ax.plot(px, py, marker="o", ms=5.0, mfc="white", mec=GOLD, mew=1.1, zorder=4)

    ax.text(x + w / 2, y + 0.34, r"many primitive states $|\mathcal{S}|$", ha="center", fontsize=6.2, color=MUTED)
    ax.plot(x + 0.035, y + 0.20, marker="s", ms=4.0, color=BLUE, clip_on=False)
    ax.plot(x + 0.052, y + 0.20, marker="*", ms=5.5, color=RED, clip_on=False)
    ax.text(x + 0.068, y + 0.20, "mandatory boundary", va="center", fontsize=6.1, color=INK)
    ax.plot(x + 0.043, y + 0.105, marker="o", ms=4.4, mfc="white", mec=GOLD, mew=1.0)
    ax.text(x + 0.068, y + 0.105, "turn / articulation", va="center", fontsize=6.1, color=INK)
    ax.text(x + 0.068, y + 0.065, "candidate universe", va="center", fontsize=6.1, color=INK)


def response_panel(ax: object, x: float, y: float, w: float, h: float) -> None:
    import numpy as np
    from matplotlib.patches import Rectangle

    panel_box(ax, x, y, w, h)
    ax.text(x + 0.012, y + h - 0.035, "b", weight="bold", fontsize=8, color=INK)
    ax.text(x + 0.038, y + h - 0.035, "Frozen Green response", weight="bold", fontsize=7.4, color=INK)
    ax.text(
        x + w / 2,
        y + h - 0.105,
        r"$H_K=\sum_{t=0}^{K}(\gamma P_{II})^tP_{IC}$",
        ha="center",
        fontsize=7.2,
        color=INK,
    )

    values = np.asarray(
        [
            [0.05, 0.10, 0.25, 0.45, 0.65, 0.85],
            [0.08, 0.18, 0.35, 0.55, 0.72, 0.92],
            [0.12, 0.28, 0.58, 0.78, 0.62, 0.96],
            [0.20, 0.42, 0.70, 0.50, 0.82, 1.00],
        ]
    )
    gx, gy = x + 0.035, y + 0.30
    cell_w = (w - 0.07) / values.shape[1]
    cell_h = 0.27 / values.shape[0]
    cmap = __import__("matplotlib").colormaps["Blues"]
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            ax.add_patch(
                Rectangle(
                    (gx + col * cell_w, gy + (values.shape[0] - row - 1) * cell_h),
                    cell_w,
                    cell_h,
                    facecolor=cmap(0.12 + 0.72 * values[row, col]),
                    edgecolor="white",
                    linewidth=0.35,
                )
            )
    ax.text(x + w / 2, y + 0.265, "schematic first-hit exposure", ha="center", fontsize=6.0, color=MUTED)

    labels = (("flow", BLUE), ("Green", TEAL), ("control", PURPLE), ("topology", GOLD), ("stochastic", RED))
    start_x = x + 0.025
    for index, (label, color) in enumerate(labels):
        px = start_x + (index % 3) * 0.068
        py = y + 0.16 - (index // 3) * 0.065
        ax.plot(px, py, marker="o", ms=3.6, color=color)
        ax.text(px + 0.012, py, label, va="center", fontsize=5.8, color=INK)
    ax.text(x + w / 2, y + 0.055, "one sparse message-passing transform", ha="center", fontsize=5.9, color=INK)
    ax.text(x + w / 2, y + 0.020, "no candidate insertion or recompute", ha="center", fontsize=5.9, color=MUTED)


def boundary_panel(ax: object, x: float, y: float, w: float, h: float) -> None:
    panel_box(ax, x, y, w, h)
    ax.text(x + 0.012, y + h - 0.035, "c", weight="bold", fontsize=8, color=INK)
    ax.text(x + 0.038, y + h - 0.035, "Threshold once", weight="bold", fontsize=7.4, color=INK)
    ax.text(x + w / 2, y + h - 0.105, r"local maxima with $q\geq2$ support", ha="center", fontsize=6.1, color=INK)
    ax.text(x + w / 2, y + h - 0.150, "topology or stochastic gate", ha="center", fontsize=6.1, color=INK)

    nodes = {
        "S": (x + 0.035, y + 0.39),
        "b1": (x + 0.09, y + 0.55),
        "b2": (x + 0.13, y + 0.29),
        "G": (x + w - 0.035, y + 0.44),
    }
    edges = (("S", "b1"), ("S", "b2"), ("b1", "G"), ("b2", "G"), ("b1", "b2"))
    for source, target in edges:
        arrow(ax, nodes[source], nodes[target], color="#8b949e")
    for name, (px, py) in nodes.items():
        if name == "S":
            marker, color, size = "s", BLUE, 6.0
        elif name == "G":
            marker, color, size = "*", RED, 8.0
        else:
            marker, color, size = "o", GOLD, 6.0
        ax.plot(px, py, marker=marker, ms=size, color=color, mec="white", mew=0.6, zorder=5)
        ax.text(px, py - 0.075, name, ha="center", fontsize=5.9, color=INK)
    ax.text(x + w / 2, y + 0.16, "selected boundary graph", ha="center", fontsize=6.4, weight="bold", color=INK)
    ax.text(x + w / 2, y + 0.095, "build kernels once", ha="center", fontsize=6.2, color=INK)
    ax.text(x + w / 2, y + 0.040, "option edges replace interior states", ha="center", fontsize=5.8, color=MUTED)


def audit_panel(ax: object, x: float, y: float, w: float, h: float) -> None:
    from matplotlib.patches import FancyBboxPatch, Polygon

    panel_box(ax, x, y, w, h)
    ax.text(x + 0.012, y + h - 0.035, "d", weight="bold", fontsize=8, color=INK)
    ax.text(x + 0.038, y + h - 0.035, "Audit and plan", weight="bold", fontsize=7.4, color=INK)

    cx, cy = x + w / 2, y + 0.57
    diamond = Polygon(
        [(cx, cy + 0.10), (cx + 0.09, cy), (cx, cy - 0.10), (cx - 0.09, cy)],
        closed=True,
        facecolor="white",
        edgecolor=PURPLE,
        linewidth=1.0,
    )
    ax.add_patch(diamond)
    ax.text(cx, cy + 0.015, "value + group", ha="center", va="center", fontsize=6.0, color=INK)
    ax.text(cx, cy - 0.025, "audit", ha="center", va="center", fontsize=6.0, color=INK)

    pass_box = FancyBboxPatch(
        (x + 0.015, y + 0.13),
        0.10,
        0.17,
        boxstyle="round,pad=0.004,rounding_size=0.006",
        facecolor="#e8f3ef",
        edgecolor=TEAL,
        linewidth=0.8,
    )
    fail_box = FancyBboxPatch(
        (x + w - 0.115, y + 0.13),
        0.10,
        0.17,
        boxstyle="round,pad=0.004,rounding_size=0.006",
        facecolor="#f8ecea",
        edgecolor=RED,
        linewidth=0.8,
    )
    ax.add_patch(pass_box)
    ax.add_patch(fail_box)
    ax.text(x + 0.065, y + 0.245, "pass", ha="center", fontsize=5.8, color=TEAL, weight="bold")
    ax.text(x + 0.065, y + 0.19, "graph-SMDP", ha="center", fontsize=5.9, color=INK)
    ax.text(x + 0.065, y + 0.155, "planning", ha="center", fontsize=5.9, color=INK)
    ax.text(x + w - 0.065, y + 0.245, "fail", ha="center", fontsize=5.8, color=RED, weight="bold")
    ax.text(x + w - 0.065, y + 0.19, "adaptive RD", ha="center", fontsize=5.9, color=INK)
    ax.text(x + w - 0.065, y + 0.155, "fallback", ha="center", fontsize=5.9, color=INK)
    arrow(ax, (cx - 0.045, cy - 0.08), (x + 0.075, y + 0.30), color=TEAL)
    arrow(ax, (cx + 0.045, cy - 0.08), (x + w - 0.075, y + 0.30), color=RED)
    ax.text(cx, y + 0.065, "certify approximation error", ha="center", fontsize=5.8, color=MUTED)
    ax.text(cx, y + 0.025, "not global RD optimality", ha="center", fontsize=5.8, color=MUTED)


def main() -> None:
    parser = argparse.ArgumentParser(description="Draw the paper-facing one-shot operator pipeline.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/operator_pipeline_figure"),
    )
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    fig = plt.figure(figsize=(7.2, 3.0), dpi=220)
    ax = fig.add_axes([0.005, 0.01, 0.99, 0.98])
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    primitive_panel(ax, 0.01, 0.07, 0.205, 0.86)
    response_panel(ax, 0.255, 0.07, 0.225, 0.86)
    boundary_panel(ax, 0.52, 0.07, 0.205, 0.86)
    audit_panel(ax, 0.765, 0.07, 0.225, 0.86)
    arrow(ax, (0.217, 0.50), (0.253, 0.50))
    arrow(ax, (0.482, 0.50), (0.518, 0.50))
    arrow(ax, (0.727, 0.50), (0.763, 0.50))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.out_dir / "operator_pipeline"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    svg_path = stem.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", pad_inches=0.02)
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines())
        + "\n",
        encoding="utf-8",
    )
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    (args.out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Operator Pipeline Figure",
                "",
                "Core conclusion: one frozen sparse Green transform replaces candidate search; final kernels are built once, and failed value/group audits route to the adaptive fallback.",
                "",
                "- archetype: schematic-led composite",
                "- backend: Python/matplotlib only",
                "- exports: editable SVG, vector PDF, and 600 dpi PNG",
                "- review boundary: approximation certificates do not certify global RD-optimal threshold selection",
                "- source data: not applicable; the response heatmap is explicitly labeled schematic",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
