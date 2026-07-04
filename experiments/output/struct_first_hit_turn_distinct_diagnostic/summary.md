# First-Boundary Targeted Split

Generated: 2026-07-04T23:43:15
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = never
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 0.5, residual_threshold_mode = struct_prob, compute_struct_distinct = True, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 0.0 | 0.0 | 1.195752858752444e-15 | 0.0 | 0.0 | 0.0 | None | (1, 10) | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | 0.2803 | 0.1402 | 0.0 | 0.0 | 0.6721 | 0.0 | 0.0 | 0.0 | None | (1, 10) | True | 1.2212453270876722e-11 | 9.985 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | 2 | 1 | 6.848 | 1 | 79.73 | 2 | (1, 5) | (4, 11) | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | 1.937 | 0.9664 | 6.385 | 0.9664 | 9.799 | 1.938 | (5, 7) | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 6.376 | 4.31 | 2.691 | 1.345 | 2 | 1 | 1.87 | 1 | 79.73 | 24 | (5, 19) | (6, 19) | True | 0.0 | 73.47 | None | none | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 6.304 | 3.335 | 2.666 | 1.333 | 2 | 1 | 1.832 | 1 | 79.73 | 24.03 | (5, 19) | (6, 19) | True | 2.921041186709772e-11 | 71.66 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | 2 | 1 | 4.953 | 1 | 79.73 | 2 | (1, 7) | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.872 | 0.9358 | 4.449 | 0.9358 | 7.924 | 1.872 | (1, 7) | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 0.0 | 0.0 | 1.195752858752444e-15 | 0.0 | 0.0 | 0.0 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | 0.2803 | 0.1402 | 0.0 | 0.0 | 0.6721 | 0.0 | 0.0 | 0.0 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 2 | 1 | 4.953 | 1 | 79.73 | 2 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.872 | 0.9358 | 4.449 | 0.9358 | 7.924 | 1.872 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 1 | 3.375 | 1 | 0.0 | 0.0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 1 | 1 | 6.848 | 1 | 39.86 | 1 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 2 | 1 | 6.848 | 1 | 79.73 | 2 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 1 | 3.186 | 1 | 0.0 | 0.0 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 0.0006481 | 1 | 6.386 | 1 | 0.0009352 | 0.0006481 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 1.937 | 0.9664 | 6.385 | 0.9664 | 9.799 | 1.938 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 2 | 1 | 1.87 | 1 | 79.73 | 24 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 2 | 1 | 1.832 | 1 | 79.73 | 24.03 | True | 2.921041186709772e-11 | None | none | 0.0 | hybrid_threshold |
