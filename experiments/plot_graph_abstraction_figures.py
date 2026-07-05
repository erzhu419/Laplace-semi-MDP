#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import thread_limits  # noqa: F401

from bellman_kron import GridWorld
from compression_experiment_utils import parse_map_specs


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_boundary(value: object) -> List[int]:
    if isinstance(value, list):
        return [int(v) for v in value]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return []
    if isinstance(parsed, list):
        return [int(v) for v in parsed]
    return []


def state_coords(grid: GridWorld, states: Sequence[int]) -> Tuple[List[float], List[float]]:
    _coord_to_idx, idx_to_coord = grid.index_maps()
    xs: List[float] = []
    ys: List[float] = []
    for state in states:
        if int(state) not in idx_to_coord:
            continue
        r, c = idx_to_coord[int(state)]
        xs.append(float(c))
        ys.append(float(r))
    return xs, ys


def draw_grid(ax: object, rows: Tuple[str, ...], boundaries: Mapping[str, Sequence[int]], title: str) -> None:
    import numpy as np

    grid = GridWorld(rows)
    height = len(rows)
    width = max(len(row) for row in rows)
    canvas = np.zeros((height, width), dtype=float)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            canvas[r, c] = 0.15 if ch == "#" else 0.98
    ax.imshow(canvas, cmap="gray", vmin=0.0, vmax=1.0, origin="upper")
    colors = {
        "endpoints": "#111111",
        "group_constrained": "#1f77b4",
        "group_constrained_operator": "#1f77b4",
        "group_constrained_incremental": "#ff7f0e",
    }
    markers = {
        "endpoints": "s",
        "group_constrained": "o",
        "group_constrained_operator": "o",
        "group_constrained_incremental": "x",
    }
    for method, states in boundaries.items():
        xs, ys = state_coords(grid, states)
        ax.scatter(
            xs,
            ys,
            s=54 if method != "endpoints" else 40,
            marker=markers.get(method, "o"),
            color=colors.get(method, "#2ca02c"),
            linewidths=1.5,
            label=method,
            alpha=0.9,
        )
    ax.set_title(title, fontsize=9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(height - 0.5, -0.5)


def row_key(row: Mapping[str, str]) -> Tuple[str, str, str]:
    return (str(row.get("map", "")), str(row.get("slip", "")), str(row.get("method", "")))


def write_report(out_dir: Path, figure_rows: Sequence[Mapping[str, object]], args: argparse.Namespace) -> None:
    lines = [
        "# Graph Abstraction Figures",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "These figures are reviewer-facing interpretability checks: they show which primitive states become graph vertices under endpoint-only, operator, and incremental group-constrained selectors.",
        "",
    ]
    for row in figure_rows:
        lines.append(f"- `{row['map']}` slip `{row['slip']}`: `{row['path']}`")
    lines.extend(
        [
            "",
            "## Source",
            "",
            f"- group-constrained adaptive CSV: `{args.group_adaptive_csv}`",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot boundary-graph interpretability figures.")
    parser.add_argument(
        "--group-adaptive-csv",
        type=Path,
        default=Path("experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv"),
    )
    parser.add_argument("--map-specs", nargs="+", default=["open_room:12", "four_rooms:11", "maze:13"])
    parser.add_argument("--slips", nargs="+", default=["0.0", "0.05"])
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/graph_abstraction_figures"))
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    map_rows = {label: rows for _family, _size, label, rows in parse_map_specs(args.map_specs)}
    rows = read_csv_rows(args.group_adaptive_csv)
    row_by_key = {row_key(row): row for row in rows if not row.get("error")}
    args.out_dir.mkdir(parents=True, exist_ok=True)

    figure_rows: List[Dict[str, object]] = []
    for map_label, rows_tuple in map_rows.items():
        for slip in args.slips:
            boundaries: Dict[str, List[int]] = {}
            for method in ["endpoints", "group_constrained", "group_constrained_operator", "group_constrained_incremental"]:
                row = row_by_key.get((map_label, str(slip), method))
                if row is not None:
                    boundaries[method] = parse_boundary(row.get("boundary", ""))
            if len(boundaries) <= 1:
                continue
            fig, ax = plt.subplots(figsize=(4.2, 4.2), dpi=180)
            draw_grid(ax, rows_tuple, boundaries, f"{map_label}, slip={slip}")
            ax.legend(loc="upper right", fontsize=6, frameon=True)
            fig.tight_layout(pad=0.5)
            filename = f"{map_label}_slip{str(slip).replace('.', 'p')}_boundaries.png"
            out_path = args.out_dir / filename
            fig.savefig(out_path, bbox_inches="tight", pad_inches=0.08)
            plt.close(fig)
            figure_rows.append({"map": map_label, "slip": slip, "path": out_path})

    if figure_rows:
        n = len(figure_rows)
        fig, axes = plt.subplots(1, n, figsize=(4.0 * n, 4.0), dpi=180)
        if n == 1:
            axes = [axes]
        for ax, row in zip(axes, figure_rows):
            map_label = str(row["map"])
            slip = str(row["slip"])
            boundaries = {}
            for method in ["endpoints", "group_constrained", "group_constrained_operator", "group_constrained_incremental"]:
                source = row_by_key.get((map_label, slip, method))
                if source is not None:
                    boundaries[method] = parse_boundary(source.get("boundary", ""))
            draw_grid(ax, map_rows[map_label], boundaries, f"{map_label}, slip={slip}")
        axes[-1].legend(loc="upper right", fontsize=6, frameon=True)
        fig.tight_layout(pad=0.6)
        combined = args.out_dir / "boundary_selection_panel.png"
        fig.savefig(combined, bbox_inches="tight", pad_inches=0.08)
        plt.close(fig)
        figure_rows.append({"map": "combined", "slip": "all", "path": combined})

    write_report(args.out_dir, figure_rows, args)


if __name__ == "__main__":
    main()
