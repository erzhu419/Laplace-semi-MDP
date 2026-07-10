# Constraint-Aware Reranker Pairing

| reranker_outcome | adaptive_reference_pass | adaptive_reference_fail |
| --- | --- | --- |
| pass | 64 | 17 |
| fail | 7 | 2 |

| n_pairs | reranker_joint_passes | adaptive_reference_joint_passes | both_pass | reranker_only | reference_only | both_fail | discordant_pairs | paired_pass_rate_difference | paired_bootstrap_confidence | paired_bootstrap_ci_low | paired_bootstrap_ci_high | paired_bootstrap_resamples | paired_bootstrap_seed | exact_mcnemar_pvalue | comparison_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 90 | 81 | 71 | 64 | 17 | 7 | 2 | 24 | 0.1111 | 0.95 | 0.01111 | 0.2111 | 100000 | 2027 | 0.06391 | descriptive_different_objectives_and_guarantees |

This comparison is descriptive because the adaptive RD reference and the reranker optimize different objectives and provide different acceptance guarantees. The paired bootstrap interval and exact McNemar test quantify sample uncertainty; neither is used to claim learned-method superiority.
