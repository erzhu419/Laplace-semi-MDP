#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from run_first_boundary_targeted import markdown_table
from run_node_large_summary import summarize_amortized
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def discover_inputs(run_root: Path) -> List[Path]:
    patterns = [
        "amortized/amortized_multitask/amortized_multitask.csv",
        "amortized_shard_*/amortized_multitask/amortized_multitask.csv",
    ]
    paths: List[Path] = []
    for pattern in patterns:
        paths.extend(sorted(run_root.glob(pattern)))
    return sorted(set(paths))


def write_report(rows: Sequence[Mapping[str, object]], summary_rows: Sequence[Mapping[str, object]], out_path: Path) -> None:
    summary_columns = [
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
    lines = [
        "# Aggregated Amortized Multi-Task Shards",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"raw_rows = {len(rows)}",
        "",
        "## Summary",
        "",
        markdown_table(summary_rows, summary_columns) if summary_rows else "_No amortized rows._",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate scheduler amortized shard CSVs.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--input-csv", type=Path, nargs="*", default=[])
    args = parser.parse_args()

    inputs = args.input_csv or discover_inputs(args.run_root)
    rows: List[Dict[str, str]] = []
    for path in inputs:
        rows.extend(read_csv_rows(path))

    out_dir = args.out_dir or (args.run_root / "amortized_aggregate")
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(out_dir / "amortized_multitask.csv", rows)
    (out_dir / "amortized_multitask.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    summary_rows = summarize_amortized(rows)
    write_csv_all_fields(out_dir / "amortized_summary.csv", summary_rows)
    write_report(rows, summary_rows, out_dir / "summary.md")
    print(f"Aggregated {len(rows)} rows from {len(inputs)} shard CSVs into {out_dir}")


if __name__ == "__main__":
    main()
