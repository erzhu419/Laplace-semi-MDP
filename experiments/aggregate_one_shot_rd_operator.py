#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Tuple

from run_one_shot_rd_operator import (
    attach_reference_comparisons,
    load_completed,
    summarize,
    write_report,
)
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def discover_csvs(patterns: List[str]) -> List[Path]:
    paths = {
        Path(match)
        for pattern in patterns
        for match in glob.glob(pattern, recursive=True)
        if Path(match).is_file()
    }
    return sorted(paths)


def row_key(row: Dict[str, object]) -> Tuple[str, str, str, str]:
    return (
        str(row.get("map", "")),
        str(row.get("slip", "")),
        str(row.get("method", "")),
        str(row.get("benchmark_mode", "end_to_end")),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded one-shot RD operator outputs.")
    parser.add_argument("--input-globs", nargs="+", required=True)
    parser.add_argument("--iterative-reference-csv", type=Path, default=Path(
        "experiments/output/large_scale_compression_adaptive/large_scale_compression.csv"
    ))
    parser.add_argument("--operator-only", action="store_true")
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.15])
    parser.add_argument("--probe-count", type=int, default=None)
    parser.add_argument("--operator-truncation-steps", type=int, default=256)
    parser.add_argument("--max-splits", type=int, default=18)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    input_paths = discover_csvs(args.input_globs)
    if not input_paths:
        raise FileNotFoundError(f"No CSVs matched: {args.input_globs}")
    merged: Dict[Tuple[str, str, str, str], Dict[str, object]] = {}
    for path in input_paths:
        for row in load_completed(path):
            key = row_key(row)
            previous = merged.get(key)
            if previous is not None and not previous.get("error") and row.get("error"):
                continue
            merged[key] = row
    rows = list(merged.values())
    historical = load_completed(args.iterative_reference_csv) if args.iterative_reference_csv.exists() else []
    attach_reference_comparisons(rows, historical_rows=historical)
    summary_rows = summarize(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "one_shot_rd_operator.csv", rows)
    write_csv_all_fields(args.out_dir / "one_shot_rd_operator_summary.csv", summary_rows)
    (args.out_dir / "one_shot_rd_operator.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    report_args = SimpleNamespace(
        out_dir=args.out_dir,
        operator_only=args.operator_only,
        thresholds=args.thresholds,
        probe_count=args.probe_count,
        operator_truncation_steps=args.operator_truncation_steps,
        max_splits=args.max_splits,
    )
    write_report(rows, summary_rows, report_args)
    print(f"inputs={len(input_paths)} rows={len(rows)} out={args.out_dir}")


if __name__ == "__main__":
    main()
