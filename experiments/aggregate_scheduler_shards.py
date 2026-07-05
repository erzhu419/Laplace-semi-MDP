#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

from run_option_algorithm_comparison import json_default, write_csv_all_fields


ROOT = Path(__file__).resolve().parents[1]


SUITES = {
    "large_scale": {
        "patterns": [
            "large_scale/large_scale_compression/large_scale_compression.csv",
            "large_scale_shard_*/large_scale_compression/large_scale_compression.csv",
        ],
        "out": "large_scale_compression/large_scale_compression.csv",
        "publish": "experiments/output/large_scale_compression_adaptive/large_scale_compression.csv",
        "keys": ["map", "slip", "method_spec"],
    },
    "random_maze": {
        "patterns": [
            "thread_random/random_maze_generalization/random_maze_generalization.csv",
            "random_maze/random_maze_generalization/random_maze_generalization.csv",
            "random_maze_shard_*/random_maze_generalization/random_maze_generalization.csv",
        ],
        "out": "random_maze_generalization/random_maze_generalization.csv",
        "publish": "experiments/output/random_maze_generalization/random_maze_generalization.csv",
        "keys": ["map", "maze_seed", "slip", "method"],
    },
    "option_frontier": {
        "patterns": [
            "option_frontier/option_baseline_frontier/frontier_all.csv",
            "option_frontier_shard_*/option_baseline_frontier/frontier_all.csv",
        ],
        "out": "option_baseline_frontier/frontier_all.csv",
        "publish": "experiments/output/option_baseline_frontier_xl/frontier_all.csv",
        "keys": ["map", "slip", "method"],
    },
    "amortized": {
        "patterns": [
            "amortized/amortized_multitask/amortized_multitask.csv",
            "amortized_shard_*/amortized_multitask/amortized_multitask.csv",
        ],
        "out": "amortized_multitask/amortized_multitask.csv",
        "publish": "experiments/output/amortized_multitask/amortized_multitask.csv",
        "keys": ["map", "method_spec", "task_count"],
    },
    "edge_reward": {
        "patterns": [
            "edge_reward/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv",
            "edge_reward_shard_*/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv",
        ],
        "out": "edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv",
        "publish": "experiments/output/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv",
        "keys": ["map", "method_spec", "variant", "task_type", "task_count"],
    },
}


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find_inputs(run_root: Path, patterns: Sequence[str]) -> List[Path]:
    paths: List[Path] = []
    for pattern in patterns:
        paths.extend(sorted(run_root.glob(pattern)))
    return sorted(dict.fromkeys(paths))


def dedupe_rows(rows: Iterable[Mapping[str, object]], keys: Sequence[str]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(str(row.get(key_name, "")) for key_name in keys)
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(row))
    return out


def merge_suite(run_root: Path, out_root: Path, suite: str) -> tuple[Path, int, List[Path]]:
    spec = SUITES[suite]
    inputs = find_inputs(run_root, spec["patterns"])  # type: ignore[arg-type]
    rows: List[Dict[str, object]] = []
    for path in inputs:
        rows.extend(read_csv_rows(path))
    rows = dedupe_rows(rows, spec["keys"])  # type: ignore[arg-type]
    out_path = out_root / str(spec["out"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(out_path, rows)
    out_path.with_suffix(".json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    return out_path, len(rows), inputs


def run_cmd(cmd: Sequence[object]) -> None:
    print("+", " ".join(str(part) for part in cmd), flush=True)
    subprocess.run([str(part) for part in cmd], cwd=ROOT, check=True)


def maybe_publish(combined_paths: Mapping[str, Path], suites: Sequence[str]) -> Dict[str, Path]:
    published: Dict[str, Path] = {}
    for suite in suites:
        path = combined_paths.get(suite)
        if path is None:
            continue
        publish_path = ROOT / str(SUITES[suite]["publish"])
        publish_path.parent.mkdir(parents=True, exist_ok=True)
        rows = read_csv_rows(path)
        write_csv_all_fields(publish_path, rows)
        publish_path.with_suffix(".json").write_text(
            json.dumps(rows, indent=2, default=json_default) + "\n",
            encoding="utf-8",
        )
        published[suite] = publish_path
    return published


def build_derived_tables(paths: Mapping[str, Path], out_root: Path) -> None:
    fair_out = out_root / "fair_budget_frontier"
    submission_out = out_root / "submission_main_table"
    run_cmd(
        [
            sys.executable,
            "experiments/run_fair_budget_frontier.py",
            "--large-scale-csv",
            paths.get("large_scale", Path("missing")).as_posix(),
            "--random-maze-csv",
            paths.get("random_maze", Path("missing")).as_posix(),
            "--option-frontier-csv",
            paths.get("option_frontier", Path("missing")).as_posix(),
            "--out-dir",
            fair_out.as_posix(),
        ]
    )
    run_cmd(
        [
            sys.executable,
            "experiments/run_submission_main_table.py",
            "--large-scale-csv",
            paths.get("large_scale", Path("missing")).as_posix(),
            "--random-maze-csv",
            paths.get("random_maze", Path("missing")).as_posix(),
            "--fair-frontier-csv",
            (fair_out / "fair_budget_frontier_summary.csv").as_posix(),
            "--amortized-csv",
            paths.get("amortized", Path("missing")).as_posix(),
            "--edge-reward-csv",
            paths.get("edge_reward", Path("missing")).as_posix(),
            "--out-dir",
            submission_out.as_posix(),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate scheduler XL shard CSVs into paper-facing tables.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--suites", nargs="+", choices=sorted(SUITES), default=sorted(SUITES))
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--skip-derived", action="store_true")
    args = parser.parse_args()

    run_root = args.run_root
    out_root = args.out_dir or (run_root / "combined")
    combined_paths: Dict[str, Path] = {}
    summary_rows: List[Dict[str, object]] = []
    for suite in args.suites:
        out_path, n_rows, inputs = merge_suite(run_root, out_root, suite)
        combined_paths[suite] = out_path
        summary_rows.append(
            {
                "suite": suite,
                "n_rows": n_rows,
                "n_input_files": len(inputs),
                "combined_csv": str(out_path),
            }
        )
    write_csv_all_fields(out_root / "aggregate_summary.csv", summary_rows)
    (out_root / "aggregate_summary.json").write_text(
        json.dumps(summary_rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    if not args.skip_derived:
        build_derived_tables(combined_paths, out_root)
    if args.publish:
        published = maybe_publish(combined_paths, args.suites)
        if not args.skip_derived:
            if "option_frontier" in published:
                fair_paths = dict(published)
                build_derived_tables(fair_paths, ROOT / "experiments/output")
            else:
                build_derived_tables(published, ROOT / "experiments/output")
    print(f"Wrote aggregate to {out_root}")


if __name__ == "__main__":
    main()
