# First-Boundary Targeted Split

Generated: 2026-07-04T23:44:50
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = threshold
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 4.0, residual_threshold_mode = struct_distinct, compute_struct_distinct = True, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | 2 | 1 | 6.848 | 1 | 79.73 | 2 | None | (4, 11) | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | 1.938 | 0.9667 | 6.385 | 0.9664 | 9.799 | 1.938 | None | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 12 | 14 | 14 | 182 | 0 | 0.0 | 82.36 | 2.741 | 21.65 | 1.284 | 104 | 8 | 2.647 | 1 | 797.3 | 104 | (7, 13) | (6, 19) | True | 3.552713678800501e-15 | 736.3 | (7, 13) | model_residual | max_splits |
| maze | 0.05 | 12 | 14 | 14 | 182 | 0 | 0.0 | 57.34 | 6.226 | 42.26 | 1.284 | 104.5 | 8.032 | 2.612 | 0.9997 | 233.4 | 104.5 | (5, 1) | (6, 19) | True | 2.8396840434652404e-11 | 720 | (5, 1) | model_residual | max_splits |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | 2 | 1 | 4.953 | 1 | 79.73 | 2 | None | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.872 | 0.9358 | 4.449 | 0.9358 | 7.924 | 1.872 | None | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 2 | 1 | 4.953 | 1 | 79.73 | 2 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.872 | 0.9358 | 4.449 | 0.9358 | 7.924 | 1.872 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 3 | 3.375 | 1 | 0.0 | 0.0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 1 | 2 | 6.848 | 1 | 39.86 | 1 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 2 | 1 | 6.848 | 1 | 79.73 | 2 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 2.968 | 3.186 | 1 | 0.0 | 0.0 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 0.0006481 | 1.968 | 6.386 | 1 | 0.0009352 | 0.0006481 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 1.938 | 0.9667 | 6.385 | 0.9664 | 9.799 | 1.938 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 24 | 13 | 1.87 | 1 | 79.73 | 24 | True | 0.0 | (5, 19) | model_residual | 13 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 8.589 | 2.579 | 3.916 | 1.345 | 35 | 12 | 1.914 | 1 | 119.6 | 35 | True | 0.0 | (5, 17) | model_residual | 12 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 11.14 | 2.066 | 5.11 | 1.345 | 44 | 11 | 1.965 | 1 | 159.5 | 44 | True | 0.0 | (1, 5) | model_residual | 22 | continue |
| maze | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 14.36 | 2.066 | 7.766 | 1.345 | 61 | 11 | 2.09 | 1 | 239.2 | 61 | True | 0.0 | (3, 5) | model_residual | 30 | continue |
| maze | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 17.18 | 2.066 | 8.943 | 1.345 | 65 | 11 | 2.167 | 1 | 279 | 65 | True | 3.552713678800501e-15 | (3, 17) | model_residual | 27 | continue |
| maze | 0.0 | 5 | 7 | 42 | 0.0 | 0 | 21.26 | 2.066 | 10.08 | 1.345 | 67 | 11 | 2.259 | 1 | 318.9 | 67 | True | 3.552713678800501e-15 | (3, 7) | model_residual | 32 | continue |
| maze | 0.0 | 6 | 8 | 56 | 0.0 | 0 | 24 | 2.066 | 11.16 | 1.345 | 67 | 11 | 2.368 | 1 | 358.8 | 67 | True | 0.0 | (3, 19) | model_residual | 28 | continue |
| maze | 0.0 | 7 | 9 | 72 | 0.0 | 0 | 26.74 | 2.066 | 12.2 | 1.345 | 65 | 11 | 2.499 | 1 | 398.6 | 65 | True | 3.552713678800501e-15 | (1, 7) | model_residual | 30 | continue |
| maze | 0.0 | 8 | 10 | 90 | 0.0 | 0 | 29.48 | 2.066 | 12.27 | 1.345 | 61 | 11 | 2.661 | 1 | 438.5 | 61 | True | 3.552713678800501e-15 | (1, 19) | model_residual | 25 | continue |
| maze | 0.0 | 9 | 11 | 110 | 0.0 | 0 | 32.22 | 2.066 | 12.55 | 1.345 | 55 | 11 | 2.647 | 1 | 478.4 | 55 | True | 3.552713678800501e-15 | (3, 1) | model_residual | 11 | continue |
| maze | 0.0 | 10 | 12 | 132 | 0.0 | 0 | 39.21 | 5.025 | 14.84 | 1.331 | 68 | 10 | 2.647 | 1 | 558.1 | 68 | True | 3.552713678800501e-15 | (7, 15) | model_residual | 10 | continue |
| maze | 0.0 | 11 | 13 | 156 | 0.0 | 0 | 71.31 | 2.741 | 19.75 | 1.301 | 97 | 9 | 2.647 | 1 | 717.5 | 97 | True | 3.552713678800501e-15 | (5, 15) | model_residual | 27 | continue |
| maze | 0.0 | 12 | 14 | 182 | 0.0 | 0 | 82.36 | 2.741 | 21.65 | 1.284 | 104 | 8 | 2.647 | 1 | 797.3 | 104 | True | 3.552713678800501e-15 | (7, 13) | model_residual | 24 | max_splits |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 24.03 | 12.97 | 1.832 | 1 | 79.73 | 24.03 | True | 2.921041186709772e-11 | (5, 19) | model_residual | 12.74 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 7.821 | 3.323 | 4.226 | 1.333 | 35.24 | 12 | 2.176 | 1 | 91.42 | 35.24 | True | 2.921041186709772e-11 | (1, 5) | model_residual | 12 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 10.27 | 3.317 | 7.342 | 1.313 | 55.03 | 11 | 2.176 | 1 | 75.88 | 55.03 | True | 2.921041186709772e-11 | (3, 5) | model_residual | 22 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 12.34 | 3.317 | 9.454 | 1.313 | 61.02 | 10.84 | 2.176 | 0.9997 | 64.22 | 61.02 | True | 2.8968827336939285e-11 | (5, 17) | model_residual | 29.98 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 15.43 | 3.317 | 11.79 | 1.313 | 65.02 | 10.84 | 2.176 | 0.9997 | 75.88 | 65.02 | True | 2.8972380050618085e-11 | (3, 17) | model_residual | 26.98 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 17.46 | 3.317 | 14.33 | 1.313 | 67.02 | 10.84 | 2.237 | 0.9997 | 87.55 | 67.02 | True | 2.8972380050618085e-11 | (3, 7) | model_residual | 31.98 | continue |
| maze | 0.05 | 6 | 8 | 56 | 0.0 | 0 | 19.48 | 3.317 | 17.09 | 1.313 | 67.02 | 10.84 | 2.345 | 0.9997 | 99.22 | 67.02 | True | 2.920330643974012e-11 | (3, 19) | model_residual | 27.98 | continue |
| maze | 0.05 | 7 | 9 | 72 | 0.0 | 0 | 21.5 | 3.317 | 20.06 | 1.313 | 65.02 | 10.84 | 2.475 | 0.9997 | 110.9 | 65.02 | True | 2.919975372606132e-11 | (1, 7) | model_residual | 29.98 | continue |
| maze | 0.05 | 8 | 10 | 90 | 0.0 | 0 | 23.52 | 3.317 | 22.28 | 1.313 | 61.02 | 10.84 | 2.635 | 0.9997 | 122.5 | 61.02 | True | 2.917133201663091e-11 | (1, 19) | model_residual | 24.98 | continue |
| maze | 0.05 | 9 | 11 | 110 | 0.0 | 0 | 25.54 | 3.317 | 24.96 | 1.313 | 55.02 | 10.84 | 2.612 | 0.9997 | 134.2 | 55.02 | True | 2.917133201663091e-11 | (3, 1) | model_residual | 10.66 | continue |
| maze | 0.05 | 10 | 12 | 132 | 0.0 | 0 | 33.15 | 6.226 | 29.73 | 1.313 | 68.4 | 10.03 | 2.612 | 0.9997 | 163.4 | 68.4 | True | 2.8965274623260484e-11 | (3, 3) | model_residual | 10.03 | continue |
| maze | 0.05 | 11 | 13 | 156 | 0.0 | 0 | 48.22 | 6.226 | 37.08 | 1.299 | 97.15 | 9.032 | 2.612 | 0.9997 | 204.2 | 97.15 | True | 2.892974748647248e-11 | (5, 3) | model_residual | 26.78 | continue |
| maze | 0.05 | 12 | 14 | 182 | 0.0 | 0 | 57.34 | 6.226 | 42.26 | 1.284 | 104.5 | 8.032 | 2.612 | 0.9997 | 233.4 | 104.5 | True | 2.8396840434652404e-11 | (5, 1) | model_residual | 24.09 | max_splits |
