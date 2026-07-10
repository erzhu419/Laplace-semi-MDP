# Empirical Selective Audit

Generated: 2026-07-11T00:51:04

Thresholds and the choice of uncertainty statistic use validation rows only. Failure means either a hard-group violation or normalized start gap above 0.01. The untouched scale-holdout table reports the resulting audit rate, failure recall, accepted joint-constraint rate, runtime, and value gap. This is an empirical routing policy, not a formal certificate; the production certificate remains the full group and value audit.

## Calibration Frontier

| target_validation_failure_recall | metric | risk_threshold | n_calibration_failures | validation_n_rows | validation_n_student_failures | validation_audit_rate | validation_failure_recall | validation_undetected_failures | validation_accepted_feasible_rate | validation_fallback_rate | validation_median_selective_pipeline_time_sec | validation_median_selective_speedup_vs_teacher | validation_max_accepted_normalized_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.9 | student_score_margin | -0.3623 | 10 | 90 | 10 | 0.3556 | 0.9 | 1 | 0.9444 | 0.1 | 0.08889 | 26.02 | 0.009605 |
| 0.9 | full_audit | nan | 10 | 90 | 10 | 1 | 1 | 0 | 0.9556 | 0.1111 | 5.44 | 0.423 | 0.009605 |
| 1 | student_score_margin | -0.5826 | 10 | 90 | 10 | 0.4444 | 1 | 0 | 0.9556 | 0.1111 | 0.09384 | 24.78 | 0.009605 |
| 1 | full_audit | nan | 10 | 90 | 10 | 1 | 1 | 0 | 0.9556 | 0.1111 | 5.44 | 0.423 | 0.009605 |

## Held-Out Routing

| target_validation_failure_recall | metric | risk_threshold | validation_audit_rate | validation_failure_recall | test_n_rows | test_n_student_failures | test_audit_rate | test_failure_recall | test_undetected_failures | test_accepted_feasible_rate | test_fallback_rate | test_median_selective_pipeline_time_sec | test_median_selective_speedup_vs_teacher | test_max_accepted_normalized_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.9 | student_score_margin | -0.3623 | 0.3556 | 0.9 | 90 | 22 | 0.3667 | 0.4545 | 12 | 0.8111 | 0.1111 | 0.1342 | 26.32 | 0.009415 |
| 1 | student_score_margin | -0.5826 | 0.4444 | 1 | 90 | 22 | 0.4 | 0.5 | 11 | 0.8222 | 0.1222 | 0.1359 | 25.69 | 0.009415 |
