# Empirical Selective Audit

Generated: 2026-07-11T05:06:54

Thresholds and the choice of uncertainty statistic use validation rows only. Failure means either a hard-group violation or normalized start gap above 0.01. The untouched scale-holdout table reports the resulting audit rate, failure recall, accepted joint-constraint rate, runtime, and value gap. This is an empirical routing policy, not a formal certificate; the production certificate remains the full group and value audit.

## Calibration Frontier

| target_validation_failure_recall | metric | risk_threshold | n_calibration_failures | validation_n_rows | validation_n_student_failures | validation_audit_rate | validation_failure_recall | validation_undetected_failures | validation_accepted_feasible_rate | validation_fallback_rate | validation_median_selective_pipeline_time_sec | validation_median_selective_speedup_vs_teacher | validation_max_accepted_normalized_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.9 | student_score_margin | -0.5826 | 5 | 90 | 5 | 0.6778 | 1 | 0 | 0.9667 | 0.05556 | 5.167 | 0.4492 | 0.009605 |
| 0.9 | constraint_failure_probability | 0.005476 | 5 | 90 | 5 | 0.8 | 1 | 0 | 0.9667 | 0.05556 | 5.458 | 0.4227 | 0.009605 |
| 0.9 | constraint_max_group_probability | 0.01692 | 5 | 90 | 5 | 0.1778 | 1 | 0 | 0.9667 | 0.05556 | 0.1478 | 14.79 | 0.009605 |
| 0.9 | constraint_predicted_gap | 0.0009546 | 5 | 90 | 5 | 0.5 | 1 | 0 | 0.9667 | 0.05556 | 2.142 | 7.105 | 0.009605 |
| 0.9 | constraint_combined_risk | 0.008171 | 5 | 90 | 5 | 0.4778 | 1 | 0 | 0.9667 | 0.05556 | 0.2228 | 11.6 | 0.009605 |
| 0.9 | full_audit | nan | 5 | 90 | 5 | 1 | 1 | 0 | 0.9667 | 0.05556 | 5.581 | 0.4074 | 0.009605 |
| 1 | student_score_margin | -0.5826 | 5 | 90 | 5 | 0.6778 | 1 | 0 | 0.9667 | 0.05556 | 5.167 | 0.4492 | 0.009605 |
| 1 | constraint_failure_probability | 0.005476 | 5 | 90 | 5 | 0.8 | 1 | 0 | 0.9667 | 0.05556 | 5.458 | 0.4227 | 0.009605 |
| 1 | constraint_max_group_probability | 0.01692 | 5 | 90 | 5 | 0.1778 | 1 | 0 | 0.9667 | 0.05556 | 0.1478 | 14.79 | 0.009605 |
| 1 | constraint_predicted_gap | 0.0009546 | 5 | 90 | 5 | 0.5 | 1 | 0 | 0.9667 | 0.05556 | 2.142 | 7.105 | 0.009605 |
| 1 | constraint_combined_risk | 0.008171 | 5 | 90 | 5 | 0.4778 | 1 | 0 | 0.9667 | 0.05556 | 0.2228 | 11.6 | 0.009605 |
| 1 | full_audit | nan | 5 | 90 | 5 | 1 | 1 | 0 | 0.9667 | 0.05556 | 5.581 | 0.4074 | 0.009605 |

## Held-Out Routing

| target_validation_failure_recall | metric | risk_threshold | validation_audit_rate | validation_failure_recall | test_n_rows | test_n_student_failures | test_audit_rate | test_failure_recall | test_undetected_failures | test_accepted_feasible_rate | test_fallback_rate | test_median_selective_pipeline_time_sec | test_median_selective_speedup_vs_teacher | test_max_accepted_normalized_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.9 | constraint_max_group_probability | 0.01692 | 0.1778 | 1 | 90 | 9 | 0.1444 | 0.3333 | 6 | 0.9111 | 0.03333 | 0.2349 | 23.23 | 0.009415 |
| 1 | constraint_max_group_probability | 0.01692 | 0.1778 | 1 | 90 | 9 | 0.1444 | 0.3333 | 6 | 0.9111 | 0.03333 | 0.2349 | 23.23 | 0.009415 |

## Prespecified Go/No-Go

| status | raw_test_joint_pass_count | required_test_joint_pass_count | raw_joint_pass_gate | undetected_test_failures | max_undetected_test_failures | routing_safety_gate | median_selective_speedup | min_accepted_pipeline_speedup | runtime_gate | full_audit_median_speedup | topology_holdout_gate | secondary_method_gate | paper_position |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NO-GO | 81 | 70 | True | 6 | 1 | False | 23.23 | 1 | True | 0.4281 | NOT-RUN: prespecified early stop after scale/routing gate | False | uncertified ablation; explicit Green/RD operator remains primary |

The topology-holdout expansion is not launched after an earlier prespecified gate fails.
