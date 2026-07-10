# Boundary Heatmap Student Audit

Generated: 2026-07-11T00:51:04

selected method = `gnn_seed_2`, prediction rows = 4680, downstream rows = 90

## Explicit-Rule Identity

| split | n_rows | match_nearest_start_rate | top_set_hit_rate | teacher_tie_rate | count_accuracy | mean_boundary_jaccard |
| --- | --- | --- | --- | --- | --- | --- |
| test | 90 | 0.7444 | 0.5444 | 0.5444 | 0.7556 | 0.6508 |
| train | 180 | 0.8222 | 0.8167 | 0.8 | 0.9222 | 0.8801 |
| validation | 90 | 0.7333 | 0.8333 | 0.6889 | 0.8778 | 0.8742 |

## Downstream Feasibility

| student_method | n_rows | student_feasible_rate | teacher_feasible_rate | fallback_rate | median_compression | median_selection_speedup | median_audited_speedup | max_normalized_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gnn_seed_2 | 90 | 0.7778 | 0.7889 | 0.2222 | 33.8 | 769.8 | 0.438 | 0.02225 |

## Family Holdout

| map_family | n_rows | student_feasible_rate | teacher_feasible_rate | mean_boundary_jaccard | median_compression | max_normalized_start_gap |
| --- | --- | --- | --- | --- | --- | --- |
| braid_maze | 36 | 0.8333 | 0.8333 | 0.6404 | 36 | 0.003156 |
| corridor | 6 | 0.6667 | 1 | 0.8167 | 42.67 | 1.351e-08 |
| four_rooms | 6 | 1 | 0.3333 | 0.3226 | 29.6 | 0.007458 |
| maze | 36 | 0.6667 | 0.8611 | 0.7361 | 32.33 | 1.485e-08 |
| open_room | 6 | 1 | 0.3333 | 0.3643 | 33.8 | 0.02225 |

## Selective-Audit Diagnostics

| metric | failure_detection_auc | pass_median | failure_median | n_finite |
| --- | --- | --- | --- | --- |
| score_margin | 0.5707 | 0.7667 | 0.6064 | 90 |
| ensemble_top_state_agreement | nan | nan | nan | 0 |
| ensemble_max_node_logit_std | nan | nan | nan | 0 |
| ensemble_selected_logit_std | nan | nan | nan | 0 |

Fixed top-k recovered feasibility in 0/0 contexts and lost it in 0/0 contexts. The latter count is direct evidence that hard-group feasibility is not monotone in the number of frozen heatmap vertices.
