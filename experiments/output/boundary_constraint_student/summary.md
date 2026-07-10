# Constraint-Aware Boundary Student

Generated: 2026-07-11T05:06:43

The frozen transition-graph GNN emits a fixed five-proposal family. A multi-head risk student predicts the three group-violation channels, normalized value gap, and joint failure, using an asymmetric underestimation penalty. It reranks proposals but does not certify them and never performs candidate insertion, beam search, or Green recomputation.

Student proposes; Green operator certifies.

| split | n_candidates | n_contexts | joint_pass_count | joint_pass_rate | oracle_union_pass_count | oracle_union_pass_rate | candidate_failure_auc | median_selection_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 572 | 180 | 176 | 0.9778 | 176 | 0.9778 | 1 | 0.003299 |
| validation | 294 | 90 | 85 | 0.9444 | 86 | 0.9556 | 0.8425 | 0.004714 |
| test | 293 | 90 | 81 | 0.9 | 85 | 0.9444 | 0.7584 | 0.006351 |

## Prespecified Raw Gate

- test joint pass: 81/90 (required >=70)
- raw gate: PASS
- independent validation calibration, accepted-pipeline runtime, and topology-holdout gates are evaluated separately.
