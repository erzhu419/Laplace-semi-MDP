#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import write_csv_all_fields


RiskMetric = Tuple[str, Callable[[float], float]]
RISK_METRICS: Tuple[RiskMetric, ...] = (
    ("student_score_margin", lambda value: -value),
    ("ensemble_top_state_agreement", lambda value: -value),
    ("ensemble_max_node_logit_std", lambda value: value),
    ("ensemble_selected_logit_std", lambda value: value),
    ("constraint_failure_probability", lambda value: value),
    ("constraint_max_group_probability", lambda value: value),
    ("constraint_predicted_gap", lambda value: value),
    ("constraint_combined_risk", lambda value: value),
)


def read_rows(path: Path) -> List[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def median(values: Iterable[float]) -> float:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(clean)) if clean else float("nan")


def passes_constraints(
    row: Mapping[str, object],
    prefix: str,
    max_normalized_gap: float,
) -> bool:
    return parse_bool(row.get(f"{prefix}_group_all_feasible")) and finite_float(
        row.get(f"{prefix}_normalized_start_gap"), float("inf")
    ) <= float(max_normalized_gap)


def calibrate_threshold(
    rows: Sequence[Mapping[str, object]],
    field: str,
    transform: Callable[[float], float],
    target_recall: float,
    max_normalized_gap: float,
) -> Tuple[float, int]:
    failed_risks = sorted(
        (
            transform(finite_float(row.get(field)))
            for row in rows
            if not passes_constraints(row, "student", max_normalized_gap)
            and math.isfinite(finite_float(row.get(field)))
        ),
        reverse=True,
    )
    if not failed_risks:
        return float("inf"), 0
    required = min(
        len(failed_risks),
        max(1, int(math.ceil(float(target_recall) * len(failed_risks)))),
    )
    return float(failed_risks[required - 1]), len(failed_risks)


def evaluate_rule(
    rows: Sequence[Mapping[str, object]],
    field: str,
    transform: Callable[[float], float],
    threshold: float,
    max_normalized_gap: float,
    audit_all: bool = False,
) -> Dict[str, object]:
    audited = []
    failures = []
    accepted = []
    path_times = []
    accepted_gaps = []
    for row in rows:
        value = finite_float(row.get(field))
        route = audit_all or (math.isfinite(value) and transform(value) >= threshold)
        student_feasible = passes_constraints(row, "student", max_normalized_gap)
        teacher_feasible = passes_constraints(row, "teacher", max_normalized_gap)
        fallback = route and not student_feasible
        accepted_feasible = student_feasible or (fallback and teacher_feasible)
        unaudited_time = (
            finite_float(row.get("student_selection_time_sec"), 0.0)
            + finite_float(row.get("student_kernel_time_sec"), 0.0)
            + finite_float(row.get("student_smdp_solve_time_sec"), 0.0)
        )
        if route and fallback:
            path_time = (
                finite_float(row.get("student_selection_time_sec"), 0.0)
                + finite_float(row.get("group_context_time_sec"), 0.0)
                + finite_float(row.get("group_audit_time_sec"), 0.0)
                + finite_float(row.get("teacher_pipeline_time_sec"), 0.0)
            )
        elif route:
            path_time = finite_float(row.get("student_audited_pipeline_time_sec"), unaudited_time)
        else:
            path_time = unaudited_time
        audited.append(route)
        failures.append(not student_feasible)
        accepted.append(accepted_feasible)
        path_times.append(path_time)
        if accepted_feasible:
            accepted_gaps.append(
                finite_float(row.get("teacher_normalized_start_gap"))
                if fallback
                else finite_float(row.get("student_normalized_start_gap"))
            )
    n_failures = sum(failures)
    caught = sum(route and failure for route, failure in zip(audited, failures))
    return {
        "n_rows": len(rows),
        "n_student_failures": n_failures,
        "audit_rate": sum(audited) / max(1, len(rows)),
        "failure_recall": caught / max(1, n_failures),
        "undetected_failures": n_failures - caught,
        "accepted_feasible_rate": sum(accepted) / max(1, len(rows)),
        "fallback_rate": sum(route and failure for route, failure in zip(audited, failures))
        / max(1, len(rows)),
        "median_selective_pipeline_time_sec": median(path_times),
        "median_selective_speedup_vs_teacher": median(
            finite_float(row.get("teacher_pipeline_time_sec"), 0.0) / max(1e-12, path_time)
            for row, path_time in zip(rows, path_times)
        ),
        "max_accepted_normalized_start_gap": max(accepted_gaps, default=float("nan")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate an empirical selective audit for GNN graph proposals.")
    parser.add_argument("--validation-csv", type=Path, required=True)
    parser.add_argument("--test-csv", type=Path, required=True)
    parser.add_argument("--target-recalls", type=float, nargs="+", default=[0.9, 1.0])
    parser.add_argument("--max-normalized-gap", type=float, default=0.01)
    parser.add_argument("--required-test-joint-pass-count", type=int, default=70)
    parser.add_argument("--max-undetected-test-failures", type=int, default=1)
    parser.add_argument("--min-accepted-pipeline-speedup", type=float, default=1.0)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/output/boundary_heatmap_selective_audit"),
    )
    args = parser.parse_args()
    validation = read_rows(args.validation_csv)
    test = read_rows(args.test_csv)
    n_validation_failures = sum(
        not passes_constraints(row, "student", args.max_normalized_gap)
        for row in validation
    )
    calibration_rows: List[Dict[str, object]] = []
    test_rows: List[Dict[str, object]] = []
    for target in args.target_recalls:
        candidates = []
        for field, transform in RISK_METRICS:
            threshold, n_failures = calibrate_threshold(
                validation,
                field=field,
                transform=transform,
                target_recall=target,
                max_normalized_gap=args.max_normalized_gap,
            )
            if n_validation_failures and n_failures == 0:
                continue
            validation_metrics = evaluate_rule(
                validation,
                field,
                transform,
                threshold,
                max_normalized_gap=args.max_normalized_gap,
            )
            candidate = {
                "target_validation_failure_recall": target,
                "metric": field,
                "risk_threshold": threshold,
                "n_calibration_failures": n_failures,
                **{f"validation_{key}": value for key, value in validation_metrics.items()},
            }
            candidates.append(candidate)
            calibration_rows.append(candidate)
        full_audit_metrics = evaluate_rule(
            validation,
            field="",
            transform=lambda value: value,
            threshold=float("-inf"),
            max_normalized_gap=args.max_normalized_gap,
            audit_all=True,
        )
        full_audit = {
            "target_validation_failure_recall": target,
            "metric": "full_audit",
            "risk_threshold": float("nan"),
            "n_calibration_failures": n_validation_failures,
            **{f"validation_{key}": value for key, value in full_audit_metrics.items()},
        }
        candidates.append(full_audit)
        calibration_rows.append(full_audit)
        eligible = [
            row
            for row in candidates
            if finite_float(row.get("validation_failure_recall"), 0.0)
            + 1e-12
            >= float(target)
        ]
        chosen = min(
            eligible or candidates,
            key=lambda row: (
                finite_float(row.get("validation_audit_rate"), 1.0),
                -finite_float(row.get("validation_failure_recall"), 0.0),
                str(row.get("metric")),
            ),
        )
        field = str(chosen["metric"])
        audit_all = field == "full_audit"
        transform = dict(RISK_METRICS).get(field, lambda value: value)
        result = evaluate_rule(
            test,
            field,
            transform,
            finite_float(chosen.get("risk_threshold"), float("-inf")),
            max_normalized_gap=args.max_normalized_gap,
            audit_all=audit_all,
        )
        test_rows.append(
            {
                "target_validation_failure_recall": target,
                "metric": field,
                "risk_threshold": chosen["risk_threshold"],
                "validation_audit_rate": chosen["validation_audit_rate"],
                "validation_failure_recall": chosen["validation_failure_recall"],
                **{f"test_{key}": value for key, value in result.items()},
            }
        )

    full_audit_test = evaluate_rule(
        test,
        field="",
        transform=lambda value: value,
        threshold=float("-inf"),
        max_normalized_gap=args.max_normalized_gap,
        audit_all=True,
    )
    strict_row = max(
        test_rows,
        key=lambda row: finite_float(row.get("target_validation_failure_recall"), 0.0),
    )
    raw_joint_pass_count = int(
        finite_float(strict_row.get("test_n_rows"), 0.0)
        - finite_float(strict_row.get("test_n_student_failures"), 0.0)
    )
    raw_gate = raw_joint_pass_count >= args.required_test_joint_pass_count
    routing_gate = int(
        finite_float(strict_row.get("test_undetected_failures"), float("inf"))
    ) <= args.max_undetected_test_failures
    runtime_gate = finite_float(
        strict_row.get("test_median_selective_speedup_vs_teacher"), 0.0
    ) > args.min_accepted_pipeline_speedup
    stopped_early = not (raw_gate and routing_gate and runtime_gate)
    go_no_go = {
        "status": "NO-GO" if stopped_early else "TOPOLOGY-HOLDOUT-PENDING",
        "raw_test_joint_pass_count": raw_joint_pass_count,
        "required_test_joint_pass_count": args.required_test_joint_pass_count,
        "raw_joint_pass_gate": raw_gate,
        "undetected_test_failures": int(
            finite_float(strict_row.get("test_undetected_failures"), 0.0)
        ),
        "max_undetected_test_failures": args.max_undetected_test_failures,
        "routing_safety_gate": routing_gate,
        "median_selective_speedup": finite_float(
            strict_row.get("test_median_selective_speedup_vs_teacher")
        ),
        "min_accepted_pipeline_speedup": args.min_accepted_pipeline_speedup,
        "runtime_gate": runtime_gate,
        "full_audit_median_speedup": finite_float(
            full_audit_test.get("median_selective_speedup_vs_teacher")
        ),
        "topology_holdout_gate": (
            "NOT-RUN: prespecified early stop after scale/routing gate"
            if stopped_early
            else "PENDING"
        ),
        "secondary_method_gate": False,
        "paper_position": "uncertified ablation; explicit Green/RD operator remains primary",
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "calibration_frontier.csv", calibration_rows)
    write_csv_all_fields(args.out_dir / "heldout_selective_audit.csv", test_rows)
    write_csv_all_fields(args.out_dir / "heldout_full_audit.csv", [full_audit_test])
    (args.out_dir / "go_no_go.json").write_text(
        json.dumps(go_no_go, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.out_dir / "summary.json").write_text(
        json.dumps(
            {
                "calibration": calibration_rows,
                "test": test_rows,
                "full_audit_test": full_audit_test,
                "go_no_go": go_no_go,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Empirical Selective Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Thresholds and the choice of uncertainty statistic use validation rows only. Failure means either a hard-group violation or normalized start gap above {args.max_normalized_gap:g}. The untouched scale-holdout table reports the resulting audit rate, failure recall, accepted joint-constraint rate, runtime, and value gap. This is an empirical routing policy, not a formal certificate; the production certificate remains the full group and value audit.",
        "",
        "## Calibration Frontier",
        "",
        markdown_table(calibration_rows, list(calibration_rows[0]) if calibration_rows else []),
        "",
        "## Held-Out Routing",
        "",
        markdown_table(test_rows, list(test_rows[0]) if test_rows else []),
        "",
        "## Prespecified Go/No-Go",
        "",
        markdown_table([go_no_go], list(go_no_go)),
        "",
        "The topology-holdout expansion is not launched after an earlier prespecified gate fails.",
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(test_rows, sort_keys=True))


if __name__ == "__main__":
    main()
