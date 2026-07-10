#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import json
from pathlib import Path
from typing import Dict, List, Tuple

from run_one_shot_group_fd_frontier import write_report
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded one-shot group-FD prefix frontiers.")
    parser.add_argument("--input-globs", nargs="+", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(
        {
            Path(match)
            for pattern in args.input_globs
            for match in glob.glob(pattern, recursive=True)
            if Path(match).is_file()
        }
    )
    if not paths:
        raise FileNotFoundError(f"No CSVs matched: {args.input_globs}")
    rows: Dict[Tuple[str, str, str], Dict[str, object]] = {}
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                rows[(str(row.get("map")), str(row.get("slip")), str(row.get("top_m")))] = dict(row)
    merged: List[Dict[str, object]] = list(rows.values())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "one_shot_group_fd_frontier.csv", merged)
    (args.out_dir / "one_shot_group_fd_frontier.json").write_text(
        json.dumps(merged, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    write_report(merged, args.out_dir / "summary.md")
    print(f"inputs={len(paths)} rows={len(merged)} out={args.out_dir}")


if __name__ == "__main__":
    main()
