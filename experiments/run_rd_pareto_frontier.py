#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np


def to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def dominates(a: Mapping[str, object], b: Mapping[str, object], objectives: Sequence[str]) -> bool:
    a_vals = [to_float(a[col]) for col in objectives]
    b_vals = [to_float(b[col]) for col in objectives]
    if not all(np.isfinite(v) for v in a_vals + b_vals):
        return False
    return all(av <= bv + 1e-12 for av, bv in zip(a_vals, b_vals)) and any(
        av < bv - 1e-12 for av, bv in zip(a_vals, b_vals)
    )


def pareto_flags(rows: Sequence[Mapping[str, object]], objectives: Sequence[str]) -> List[bool]:
    flags: List[bool] = []
    for i, row in enumerate(rows):
        dominated = any(j != i and dominates(other, row, objectives) for j, other in enumerate(rows))
        flags.append(not dominated)
    return flags


def markdown_table(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                values.append(f"{value:.4g}" if np.isfinite(value) and abs(value) >= 1e-9 else str(value))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def group_key(row: Mapping[str, object], columns: Sequence[str]) -> Tuple[str, ...]:
    return tuple(str(row.get(column, "")) for column in columns)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract RD Pareto frontiers from graph baseline comparisons.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--group-columns", nargs="+", default=["map", "slip"])
    parser.add_argument(
        "--objectives",
        nargs="+",
        default=[
            "description_length_proxy",
            "occupancy_struct_hidden_distinct",
            "struct_hidden_distinct_cvar95",
        ],
    )
    parser.add_argument(
        "--display-columns",
        nargs="+",
        default=[
            "method",
            "method_family",
            "map",
            "slip",
            "n_boundary",
            "description_length_proxy",
            "occupancy_struct_hidden_distinct",
            "struct_hidden_distinct_cvar95",
            "struct_hidden_distinct_valid_total",
            "start_gap",
            "constructor_last_split_source",
        ],
    )
    args = parser.parse_args()

    rows = list(csv.DictReader(args.input.open(newline="", encoding="utf-8")))
    scored_rows: List[Dict[str, object]] = []
    frontier_rows: List[Dict[str, object]] = []
    grouped = sorted({group_key(row, args.group_columns) for row in rows})
    for key in grouped:
        group_rows = [row for row in rows if group_key(row, args.group_columns) == key]
        flags = pareto_flags(group_rows, args.objectives)
        for row, is_frontier in zip(group_rows, flags):
            scored = dict(row)
            scored["pareto_frontier"] = is_frontier
            scored["pareto_group"] = " / ".join(key)
            scored_rows.append(scored)
            if is_frontier:
                frontier_rows.append(scored)

    frontier_rows.sort(
        key=lambda row: (
            row.get("pareto_group", ""),
            to_float(row.get(args.objectives[0], float("inf"))),
            to_float(row.get(args.objectives[1], float("inf"))),
            to_float(row.get(args.objectives[2], float("inf"))),
        )
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "all_scored.csv", scored_rows)
    write_csv(args.out_dir / "frontier.csv", frontier_rows)
    (args.out_dir / "all_scored.json").write_text(json.dumps(scored_rows, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "frontier.json").write_text(json.dumps(frontier_rows, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# RD Pareto Frontier",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"input = {args.input}",
        f"group_columns = {args.group_columns}",
        f"objectives = {args.objectives}",
        "",
    ]
    for key in grouped:
        group = " / ".join(key)
        group_frontier = [row for row in frontier_rows if row.get("pareto_group") == group]
        lines.extend(
            [
                f"## {group}",
                "",
                markdown_table(group_frontier, args.display_columns),
                "",
            ]
        )
    (args.out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out_dir / 'frontier.csv'}")
    print(f"Wrote {args.out_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
