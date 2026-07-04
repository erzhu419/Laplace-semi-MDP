# First-Boundary Targeted Split

Generated: 2026-07-04T23:42:40
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = threshold
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 1.2, residual_threshold_mode = raw, compute_struct_distinct = False, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 1.195752858752444e-15 | 0.0 | 0.0 | 0.0 | None | (1, 10) | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | 0.2803 | 0.1402 | 0.2803 | 0.1402 | 0.6721 | 0.0 | 0.0 | 0.0 | None | (1, 10) | True | 1.2212453270876722e-11 | 9.985 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 0.0 | None | (4, 11) | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 0.0 | None | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 12 | 14 | 14 | 182 | 0 | 0.0 | 84.19 | 2.741 | 26.2 | 1.174 | 26.2 | 1.174 | 2.316 | 1 | 916.9 | 0.0 | None | (6, 19) | True | 0.0 | 743.6 | None | none | hybrid_threshold |
| maze | 0.05 | 12 | 14 | 14 | 182 | 0 | 0.0 | 80.69 | 6.226 | 47.31 | 1.194 | 47.31 | 1.194 | 2.475 | 0.9997 | 262.5 | 0.0 | None | (6, 19) | True | 2.901856532844249e-11 | 750.1 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 0.0 | None | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 0.0 | None | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 1.195752858752444e-15 | 0.0 | 0.0 | 0.0 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | 0.2803 | 0.1402 | 0.2803 | 0.1402 | 0.6721 | 0.0 | 0.0 | 0.0 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 0.0 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 0.0 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 0.9531 | 3.375 | 1 | 0.0 | 0.0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 1.013 | 1.046 | 6.848 | 1 | 39.86 | 0.0 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 0.0 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 0.9354 | 3.186 | 1 | 0.0 | 0.0 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 0.2029 | 1.038 | 6.386 | 1 | 0.0009352 | 0.0 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 0.0 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 2.691 | 1.345 | 1.87 | 1 | 79.73 | 0.0 | True | 0.0 | (3, 1) | model_residual | 1.345 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 11.53 | 5.025 | 3.916 | 1.345 | 3.916 | 1.345 | 1.914 | 1 | 119.6 | 0.0 | True | 0.0 | (5, 19) | model_residual | 1.345 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 14.71 | 5.025 | 5.141 | 1.331 | 5.141 | 1.331 | 1.914 | 1 | 159.5 | 0.0 | True | 0.0 | (3, 3) | model_residual | 1.331 | continue |
| maze | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 23.18 | 5.025 | 7.651 | 1.331 | 7.651 | 1.331 | 1.965 | 1 | 239.2 | 0.0 | True | 0.0 | (5, 3) | model_residual | 2.633 | continue |
| maze | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 29.47 | 5.025 | 8.796 | 1.331 | 8.796 | 1.331 | 2.023 | 1 | 279 | 0.0 | True | 0.0 | (7, 15) | model_residual | 3.624 | continue |
| maze | 0.0 | 5 | 7 | 42 | 0.0 | 0 | 35.99 | 2.741 | 11.43 | 1.331 | 11.43 | 1.331 | 2.167 | 1 | 358.8 | 0.0 | True | 0.0 | (5, 15) | model_residual | 5.065 | continue |
| maze | 0.0 | 6 | 8 | 56 | 0.0 | 0 | 37.43 | 2.741 | 12.18 | 1.331 | 12.18 | 1.331 | 2.259 | 1 | 398.6 | 0.0 | True | 3.552713678800501e-15 | (5, 1) | model_residual | 4.989 | continue |
| maze | 0.0 | 7 | 9 | 72 | 0.0 | 0 | 42 | 2.741 | 13.15 | 1.331 | 13.15 | 1.331 | 2.368 | 1 | 438.5 | 0.0 | True | 0.0 | (7, 1) | model_residual | 4.908 | continue |
| maze | 0.0 | 8 | 10 | 90 | 0.0 | 0 | 46.57 | 2.741 | 13.7 | 1.331 | 13.7 | 1.331 | 2.316 | 1 | 478.4 | 0.0 | True | 0.0 | (5, 17) | model_residual | 1.331 | continue |
| maze | 0.0 | 9 | 11 | 110 | 0.0 | 0 | 59 | 2.741 | 18.64 | 1.317 | 18.64 | 1.317 | 2.316 | 1 | 637.8 | 0.0 | True | 0.0 | (3, 17) | model_residual | 3.95 | continue |
| maze | 0.0 | 10 | 12 | 132 | 0.0 | 0 | 71.52 | 2.741 | 20.88 | 1.301 | 20.88 | 1.301 | 2.316 | 1 | 717.5 | 0.0 | True | 0.0 | (3, 19) | model_residual | 3.902 | continue |
| maze | 0.0 | 11 | 13 | 156 | 0.0 | 0 | 77.86 | 2.741 | 25.65 | 1.284 | 25.65 | 1.284 | 2.316 | 1 | 877 | 0.0 | True | 0.0 | (1, 19) | model_residual | 6.42 | continue |
| maze | 0.0 | 12 | 14 | 182 | 0.0 | 0 | 84.19 | 2.741 | 26.2 | 1.174 | 26.2 | 1.174 | 2.316 | 1 | 916.9 | 0.0 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 2.666 | 1.333 | 1.832 | 1 | 79.73 | 0.0 | True | 2.921041186709772e-11 | (5, 19) | model_residual | 1.31 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 7.821 | 3.323 | 4.226 | 1.333 | 4.226 | 1.333 | 2.176 | 1 | 91.42 | 0.0 | True | 2.921041186709772e-11 | (5, 17) | model_residual | 1.312 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 11.39 | 3.317 | 6.044 | 1.332 | 6.044 | 1.332 | 2.176 | 1 | 131.3 | 0.0 | True | 2.8975932764296886e-11 | (1, 5) | model_residual | 2.4 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 13.41 | 3.317 | 9.453 | 1.313 | 9.453 | 1.313 | 2.176 | 1 | 99.21 | 0.0 | True | 2.920685915341892e-11 | (3, 5) | model_residual | 3.805 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 15.43 | 3.317 | 11.79 | 1.313 | 11.79 | 1.313 | 2.176 | 0.9997 | 75.88 | 0.0 | True | 2.8972380050618085e-11 | (3, 17) | model_residual | 3.753 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 17.46 | 3.317 | 14.33 | 1.313 | 14.33 | 1.313 | 2.237 | 0.9997 | 87.55 | 0.0 | True | 2.8972380050618085e-11 | (3, 7) | model_residual | 4.932 | continue |
| maze | 0.05 | 6 | 8 | 56 | 0.0 | 0 | 19.48 | 3.317 | 17.09 | 1.313 | 17.09 | 1.313 | 2.345 | 0.9997 | 99.22 | 0.0 | True | 2.920330643974012e-11 | (3, 19) | model_residual | 4.855 | continue |
| maze | 0.05 | 7 | 9 | 72 | 0.0 | 0 | 21.5 | 3.317 | 20.06 | 1.313 | 20.06 | 1.313 | 2.475 | 0.9997 | 110.9 | 0.0 | True | 2.919975372606132e-11 | (3, 1) | model_residual | 1.29 | continue |
| maze | 0.05 | 8 | 10 | 90 | 0.0 | 0 | 29.1 | 6.226 | 24.45 | 1.313 | 24.45 | 1.313 | 2.475 | 0.9997 | 140.1 | 0.0 | True | 2.8972380050618085e-11 | (3, 3) | model_residual | 1.312 | continue |
| maze | 0.05 | 9 | 11 | 110 | 0.0 | 0 | 44.18 | 6.226 | 31.43 | 1.299 | 31.43 | 1.299 | 2.475 | 0.9997 | 180.9 | 0.0 | True | 2.892619477279368e-11 | (5, 3) | model_residual | 3.861 | continue |
| maze | 0.05 | 10 | 12 | 132 | 0.0 | 0 | 53.3 | 6.226 | 36.24 | 1.284 | 36.24 | 1.284 | 2.475 | 0.9997 | 210 | 0.0 | True | 2.8400393148331204e-11 | (5, 1) | model_residual | 3.851 | continue |
| maze | 0.05 | 11 | 13 | 156 | 0.0 | 0 | 70.94 | 6.226 | 43.59 | 1.268 | 43.59 | 1.268 | 2.475 | 0.9997 | 245.1 | 0.0 | True | 2.9103830456733704e-11 | (7, 1) | model_residual | 6.305 | continue |
| maze | 0.05 | 12 | 14 | 182 | 0.0 | 0 | 80.69 | 6.226 | 47.31 | 1.194 | 47.31 | 1.194 | 2.475 | 0.9997 | 262.5 | 0.0 | True | 2.901856532844249e-11 | None | none | 0.0 | hybrid_threshold |
