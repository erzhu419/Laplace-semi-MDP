#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Iterable, List, Mapping, Sequence

from run_abstraction_baseline_comparison import aggregate_rows as aggregate_abstraction
from run_abstraction_baseline_comparison import write_report as write_abstraction_report
from run_end_to_end_gap_decomposition import write_report as write_end_to_end_report
from run_general_env_benchmark import aggregate_rows as aggregate_general_env
from run_general_env_benchmark import write_summary as write_general_env_report
from run_option_algorithm_comparison import json_default, write_csv_all_fields
from run_planner_baseline_comparison import aggregate_rows as aggregate_planners
from run_planner_baseline_comparison import fastest_valid_rows, write_report as write_planner_report
from run_random_maze_budget_recovery import build_recovery_summary, write_report as write_recovery_report
from run_random_maze_generalization import build_summary_rows as build_random_maze_summary
from run_random_maze_generalization import write_report as write_random_maze_report
from run_solver_validity import solver_aggregate_rows, write_report as write_solver_report


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHARDS = {
    "planner": 108,
    "abstraction": 72,
    "solver_oracle": 108,
    "general_env": 35,
    "end_to_end": 36,
    "budget_recovery": 7,
}


def validate_shards(
    run_root: Path,
    allow_incomplete: bool,
    require_taxi_patch: bool = False,
    require_four_rooms_patch: bool = False,
    require_paired_planner: bool = False,
    require_actual_recovery: bool = False,
    require_extended_actual_recovery: bool = False,
    require_converged_end_to_end: bool = False,
) -> List[Dict[str, object]]:
    coverage: List[Dict[str, object]] = []
    failures: List[str] = []
    fingerprints_by_suite: Dict[str, set[str]] = {}
    expected_shards = dict(EXPECTED_SHARDS)
    if require_taxi_patch:
        expected_shards["general_env_taxi"] = 5
    if require_four_rooms_patch:
        expected_shards["solver_oracle_four_rooms"] = 9
    if require_paired_planner:
        expected_shards["planner_paired"] = 135
    if require_actual_recovery:
        expected_shards["budget_recovery_actual"] = 7
    if require_extended_actual_recovery:
        expected_shards["budget_recovery_actual_extended"] = 3
    if require_converged_end_to_end:
        expected_shards["end_to_end_converged"] = 36
    for suite, expected in expected_shards.items():
        directories = sorted(path for path in run_root.glob(f"{suite}_shard_*_of_*") if path.is_dir())
        successful: List[Path] = []
        malformed: List[str] = []
        for directory in directories:
            marker = directory / "_SUCCESS.json"
            if not marker.exists():
                continue
            try:
                payload = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                malformed.append(f"{directory.name}: {exc}")
                continue
            if payload.get("suite") != suite or payload.get("label") != directory.name:
                malformed.append(f"{directory.name}: marker identity mismatch")
                continue
            fingerprint = str(payload.get("fingerprint", ""))
            if fingerprint:
                fingerprints_by_suite.setdefault(suite, set()).add(fingerprint)
            successful.append(directory)
        missing = expected - len(successful)
        coverage.append(
            {
                "suite": suite,
                "expected_shards": expected,
                "discovered_dirs": len(directories),
                "successful_shards": len(successful),
                "missing_shards": missing,
                "malformed_markers": len(malformed),
                "source_fingerprints": ";".join(
                    sorted(fingerprints_by_suite.get(suite, set()))
                ),
            }
        )
        if missing or malformed:
            failures.append(
                f"{suite}: expected {expected}, found {len(successful)} successful; "
                f"malformed={malformed[:3]}"
            )
    for suite, fingerprints in fingerprints_by_suite.items():
        if len(fingerprints) > 1:
            failures.append(f"{suite}: mixed workspace fingerprints: {sorted(fingerprints)}")
    if failures and not allow_incomplete:
        raise RuntimeError("Incomplete or inconsistent scheduler run:\n" + "\n".join(failures))
    return coverage


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def merge_rows(
    run_root: Path,
    pattern: str | Sequence[str],
    keys: Sequence[str],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    patterns = [pattern] if isinstance(pattern, str) else list(pattern)
    for item in patterns:
        for path in sorted(run_root.glob(item)):
            rows.extend(read_csv(path))
    deduped: List[Dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(str(row.get(name, "")) for name in keys)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, default=json_default) + "\n", encoding="utf-8")


def run_cmd(parts: Sequence[object]) -> None:
    print("+", " ".join(str(part) for part in parts), flush=True)
    subprocess.run([str(part) for part in parts], cwd=ROOT, check=True)


def publish_planners(run_root: Path) -> int:
    paired_paths = list(run_root.glob("planner_paired_shard_*/planner_baseline_comparison/planner_baseline_runs.csv"))
    pattern = (
        "planner_paired_shard_*/planner_baseline_comparison/planner_baseline_runs.csv"
        if paired_paths
        else "planner_shard_*/planner_baseline_comparison/planner_baseline_runs.csv"
    )
    rows = merge_rows(
        run_root,
        pattern,
        ["map", "slip", "method", "repeat"],
    )
    out = ROOT / "experiments/output/planner_baseline_comparison"
    out.mkdir(parents=True, exist_ok=True)
    aggregate = aggregate_planners(rows)
    strongest = fastest_valid_rows(aggregate, tolerance=1e-7)
    write_csv_all_fields(out / "planner_baseline_runs.csv", rows)
    write_csv_all_fields(out / "planner_baseline_aggregate.csv", aggregate)
    write_csv_all_fields(out / "strongest_planner_by_case.csv", strongest)
    write_json(out / "planner_baseline_comparison.json", {"runs": rows, "aggregate": aggregate, "strongest": strongest})
    write_planner_report(
        aggregate,
        strongest,
        out / "summary.md",
        SimpleNamespace(
            methods=["sparse_vectorized_vi", "gauss_seidel_vi", "prioritized_sweeping"],
            repeats=5,
            tol=1e-10,
        ),
    )
    return len(rows)


def publish_abstraction(run_root: Path) -> int:
    rows = merge_rows(
        run_root,
        "abstraction_shard_*/abstraction_baseline_comparison/abstraction_baseline_runs.csv",
        ["map", "slip", "method", "target_count", "repeat"],
    )
    out = ROOT / "experiments/output/abstraction_baseline_comparison"
    out.mkdir(parents=True, exist_ok=True)
    aggregate = aggregate_abstraction(rows)
    write_csv_all_fields(out / "abstraction_baseline_runs.csv", rows)
    write_csv_all_fields(out / "abstraction_baseline_aggregate.csv", aggregate)
    write_json(out / "abstraction_baseline_comparison.json", {"rows": rows, "aggregate": aggregate})
    write_abstraction_report(
        rows,
        aggregate,
        out / "summary.md",
        SimpleNamespace(
            methods=["exact_model_minimization", "epsilon_homogeneous", "qstar_oracle_aggregation", "policy_kron_oracle"],
            repeats=5,
        ),
    )
    return len(rows)


def publish_solver(run_root: Path) -> int:
    rows = merge_rows(
        run_root,
        [
            "solver_oracle_shard_*/solver_validity/solver_validity.csv",
            "solver_oracle_four_rooms_shard_*/solver_validity/solver_validity.csv",
        ],
        ["map", "slip", "budget_frac", "solver", "beam_width"],
    )
    oracle = merge_rows(
        run_root,
        [
            "solver_oracle_shard_*/solver_validity/oracle_subsets.csv",
            "solver_oracle_four_rooms_shard_*/solver_validity/oracle_subsets.csv",
        ],
        ["map", "slip", "budget_frac", "boundary"],
    )
    errors = merge_rows(
        run_root,
        [
            "solver_oracle_shard_*/solver_validity/solver_errors.csv",
            "solver_oracle_four_rooms_shard_*/solver_validity/solver_errors.csv",
        ],
        ["map", "slip", "budget_frac"],
    )
    completed_contexts = {(row.get("map"), row.get("slip"), row.get("budget_frac")) for row in rows}
    errors = [
        row
        for row in errors
        if (row.get("map"), row.get("slip"), row.get("budget_frac")) not in completed_contexts
    ]
    out = ROOT / "experiments/output/solver_validity"
    out.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(out / "solver_validity.csv", rows)
    write_csv_all_fields(out / "solver_validity_aggregate.csv", solver_aggregate_rows(rows))
    write_csv_all_fields(out / "oracle_subsets.csv", oracle)
    write_csv_all_fields(out / "solver_errors.csv", errors)
    write_json(out / "solver_validity.json", rows)
    write_json(out / "oracle_subsets.json", oracle)
    write_solver_report(
        rows,
        oracle,
        out / "summary.md",
        SimpleNamespace(
            map_specs=["open_room:5", "four_rooms:7", "maze:7"],
            random_maze_sizes=[5],
            random_maze_seeds=list(range(32)),
            slips=[0.0, 0.05, 0.1],
            budget_fracs=[0.1, 0.25, 0.5],
            solvers=["operator", "actual_refine"],
            beam_widths=[1, 2, 4, 8],
            beam_expand=6,
            max_extra_splits=2,
            max_oracle_candidates=12,
            oracle_pool_mode="all",
        ),
    )
    return len(rows)


def publish_general_env(run_root: Path) -> int:
    rows = merge_rows(
        run_root,
        [
            "general_env_shard_*/general_env_benchmark/general_env_benchmark.csv",
            "general_env_taxi_shard_*/general_env_benchmark/general_env_benchmark.csv",
        ],
        ["env_spec", "seed", "method", "option_mode", "target_count"],
    )
    errors = merge_rows(
        run_root,
        [
            "general_env_shard_*/general_env_benchmark/general_env_errors.csv",
            "general_env_taxi_shard_*/general_env_benchmark/general_env_errors.csv",
        ],
        ["env_spec", "seed", "method", "option_mode", "target_count", "error"],
    )
    if any(row.get("env_spec") == "toytext:Taxi-v4" for row in rows):
        errors = [row for row in errors if row.get("env_spec") != "toytext:Taxi-v3"]
    out = ROOT / "experiments/output/general_env_benchmark"
    out.mkdir(parents=True, exist_ok=True)
    aggregate = aggregate_general_env(rows)
    write_csv_all_fields(out / "general_env_benchmark.csv", rows)
    write_csv_all_fields(out / "general_env_aggregate.csv", aggregate)
    write_csv_all_fields(out / "general_env_errors.csv", errors)
    write_json(out / "general_env_benchmark.json", {"rows": rows, "errors": errors})
    write_general_env_report(out / "summary.md", rows, aggregate, errors)
    return len(rows)


def publish_end_to_end(run_root: Path) -> int:
    rows = merge_rows(
        run_root,
        [
            "end_to_end_shard_*/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv",
            "end_to_end_converged_shard_*/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv",
        ],
        ["map", "slip", "method_spec", "config_label"],
    )
    for row in rows:
        if not row.get("config_label"):
            row["config_label"] = "fixed_k32_i8"
    out = ROOT / "experiments/output/end_to_end_gap_decomposition"
    out.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(out / "end_to_end_gap_decomposition.csv", rows)
    write_json(out / "end_to_end_gap_decomposition.json", rows)
    write_end_to_end_report(
        rows,
        out / "summary.md",
        SimpleNamespace(truncation_steps=32, planning_iterations=8),
    )
    return len(rows)


def publish_budget_recovery(run_root: Path) -> int:
    rows = merge_rows(
        run_root,
        [
            "budget_recovery_shard_*/random_maze_budget_recovery/random_maze_budget_recovery.csv",
            "budget_recovery_actual_shard_*/random_maze_budget_recovery/random_maze_budget_recovery.csv",
            "budget_recovery_actual_extended_shard_*/random_maze_budget_recovery/random_maze_budget_recovery.csv",
        ],
        ["map", "slip", "budget_frac", "max_splits", "method"],
    )
    out = ROOT / "experiments/output/random_maze_budget_recovery"
    out.mkdir(parents=True, exist_ok=True)
    summary = build_recovery_summary(rows)
    write_csv_all_fields(out / "random_maze_budget_recovery.csv", rows)
    write_csv_all_fields(out / "random_maze_budget_recovery_summary.csv", summary)
    write_json(out / "random_maze_budget_recovery.json", {"rows": rows, "summary": summary})
    write_recovery_report(
        rows,
        summary,
        out / "summary.md",
        SimpleNamespace(max_splits_values=[5, 8, 12, 16], budget_fracs=[0.25]),
    )
    return len(rows)


def refresh_random_maze_summary() -> int:
    out = ROOT / "experiments/output/random_maze_generalization"
    rows = read_csv(out / "random_maze_generalization.csv")
    summary = build_random_maze_summary(rows)
    write_csv_all_fields(out / "random_maze_generalization_summary.csv", summary)
    write_random_maze_report(
        rows,
        summary,
        out / "summary.md",
        SimpleNamespace(
            sizes=[11, 13, 15, 17, 19],
            maze_seeds=list(range(12)),
            slips=[0.0, 0.05, 0.1],
            methods=["endpoints", "group_constrained_incremental"],
            shard_index=0,
            num_shards=1,
        ),
        elapsed=0.0,
    )
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate reviewer-P0 scheduler shards into tracked artifacts.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--skip-derived", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--require-taxi-patch", action="store_true")
    parser.add_argument("--require-four-rooms-patch", action="store_true")
    parser.add_argument("--require-paired-planner", action="store_true")
    parser.add_argument("--require-actual-recovery", action="store_true")
    parser.add_argument("--require-extended-actual-recovery", action="store_true")
    parser.add_argument("--require-converged-end-to-end", action="store_true")
    args = parser.parse_args()

    shard_coverage = validate_shards(
        args.run_root,
        args.allow_incomplete,
        args.require_taxi_patch,
        args.require_four_rooms_patch,
        args.require_paired_planner,
        args.require_actual_recovery,
        args.require_extended_actual_recovery,
        args.require_converged_end_to_end,
    )

    counts = {
        "planner": publish_planners(args.run_root),
        "abstraction": publish_abstraction(args.run_root),
        "solver_oracle": publish_solver(args.run_root),
        "general_env": publish_general_env(args.run_root),
        "end_to_end": publish_end_to_end(args.run_root),
        "budget_recovery": publish_budget_recovery(args.run_root),
        "random_maze_existing": refresh_random_maze_summary(),
    }
    if args.require_taxi_patch:
        counts["general_env_taxi"] = len(
            merge_rows(
                args.run_root,
                "general_env_taxi_shard_*/general_env_benchmark/general_env_benchmark.csv",
                ["env_spec", "seed", "method", "option_mode", "target_count"],
            )
        )
    if args.require_four_rooms_patch:
        counts["solver_oracle_four_rooms"] = len(
            merge_rows(
                args.run_root,
                "solver_oracle_four_rooms_shard_*/solver_validity/solver_validity.csv",
                ["map", "slip", "budget_frac", "solver", "beam_width"],
            )
        )
    if args.require_paired_planner:
        counts["planner_paired"] = len(
            merge_rows(
                args.run_root,
                "planner_paired_shard_*/planner_baseline_comparison/planner_baseline_runs.csv",
                ["map", "slip", "method", "repeat"],
            )
        )
    if args.require_actual_recovery:
        counts["budget_recovery_actual"] = len(
            merge_rows(
                args.run_root,
                "budget_recovery_actual_shard_*/random_maze_budget_recovery/random_maze_budget_recovery.csv",
                ["map", "slip", "budget_frac", "max_splits", "method"],
            )
        )
    if args.require_extended_actual_recovery:
        counts["budget_recovery_actual_extended"] = len(
            merge_rows(
                args.run_root,
                "budget_recovery_actual_extended_shard_*/random_maze_budget_recovery/random_maze_budget_recovery.csv",
                ["map", "slip", "budget_frac", "max_splits", "method"],
            )
        )
    if args.require_converged_end_to_end:
        counts["end_to_end_converged"] = len(
            merge_rows(
                args.run_root,
                "end_to_end_converged_shard_*/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv",
                ["map", "slip", "method_spec", "config_label"],
            )
        )
    out = ROOT / "experiments/output/p0_audit_aggregate"
    out.mkdir(parents=True, exist_ok=True)
    coverage_rows = []
    for row in shard_coverage:
        enriched = dict(row)
        enriched["rows"] = counts[str(row["suite"])]
        coverage_rows.append(enriched)
    write_csv_all_fields(out / "coverage.csv", coverage_rows)
    write_json(out / "coverage.json", {"rows": counts, "shards": shard_coverage})

    if not args.skip_derived:
        run_cmd([sys.executable, "experiments/run_fair_budget_frontier.py"])
        run_cmd([sys.executable, "experiments/run_theorem_experiment_bridge.py"])
        run_cmd([sys.executable, "experiments/run_submission_main_table.py"])
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
