# First-Boundary Targeted Split

Generated: 2026-07-05T07:23:54
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = exact_mdl
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 0.5, residual_threshold_mode = raw, compute_struct_distinct = True, struct_mdl_node_cost_weight = 1.0, struct_mdl_edge_cost_weight = 0.1, struct_mdl_exposure_bit_weight = 1.0, struct_mdl_min_gain = 0.0, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | occupancy_struct_hidden_distinct | struct_mdl_split_benefit | struct_mdl_split_cost | struct_mdl_split_gain | struct_mdl_split_candidate_coord | exact_mdl_split_gain | exact_mdl_split_candidate_coord | exact_mdl_base_bits | exact_mdl_candidate_bits | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 2 | 0.0 | 1 | 6.472 | -5.472 | None | -6.97 | None | 11.78 | 18.75 | (1, 5) | (4, 11) | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 1.938 | 0.0003241 | 0.9342 | 6.472 | -5.538 | None | -6.969 | None | 11.78 | 18.75 | (5, 7) | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 1 | 3 | 3 | 6 | 0 | 0.0 | 12.63 | 4.31 | 5.295 | 1.345 | 5.295 | 1.345 | 1.965 | 1 | 159.5 | 47 | 0.0 | 36 | 6.94 | 29.06 | (1, 7) | -8.87 | None | 7.304 | 16.17 | (5, 19) | (6, 19) | True | 0.0 | 117.7 | None | none | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 6.304 | 3.335 | 2.666 | 1.333 | 2.666 | 1.333 | 1.832 | 1 | 79.73 | 24.03 | 11.07 | 12.93 | 6.74 | 6.194 | (5, 19) | -9.08 | None | 12.07 | 21.15 | (5, 19) | (6, 19) | True | 2.921041186709772e-11 | 71.66 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 2 | 1 | 1 | 5.529 | -4.529 | None | -5.044 | None | 2 | 7.044 | (1, 7) | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 1.872 | 0.9358 | 0.8758 | 5.529 | -4.653 | None | -5.109 | None | 1.936 | 7.044 | (5, 1) | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | occupancy_struct_hidden_distinct | struct_mdl_split_benefit | struct_mdl_split_cost | struct_mdl_split_gain | exact_mdl_split_gain | exact_mdl_base_bits | exact_mdl_candidate_bits | exact_mdl_candidates_evaluated | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 2 | 1 | 1 | 5.529 | -4.529 | -5.044 | 2 | 7.044 | 2 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 1.872 | 0.9358 | 0.8758 | 5.529 | -4.653 | -5.109 | 1.936 | 7.044 | 2 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 0.9531 | 3.375 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 6.072 | 0.0 | 0.0 | 1 | 0.0 | 0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 1.013 | 1.046 | 6.848 | 1 | 39.86 | 1 | 0.0 | 1 | 6.272 | -5.272 | -7.977 | 6.615 | 14.59 | 7 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 2 | 0.0 | 1 | 6.472 | -5.472 | -6.97 | 11.78 | 18.75 | 6 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 0.9354 | 3.186 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 6.072 | 0.0 | 0.0 | 1 | 0.0 | 0 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 0.2029 | 1.038 | 6.386 | 1 | 0.0009352 | 0.0006481 | 0.0 | 1.966e-07 | 6.272 | -6.272 | -7.977 | 6.615 | 14.59 | 7 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 1.938 | 0.0003241 | 0.9342 | 6.472 | -5.538 | -6.969 | 11.78 | 18.75 | 6 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 2.691 | 1.345 | 1.87 | 1 | 79.73 | 24 | 11 | 13 | 6.74 | 6.26 | 1.696 | 12 | 10.3 | 8 | True | 0.0 | (1, 5) | residual_exact_mdl | 1.696 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 12.63 | 4.31 | 5.295 | 1.345 | 5.295 | 1.345 | 1.965 | 1 | 159.5 | 47 | 0.0 | 36 | 6.94 | 29.06 | -8.87 | 7.304 | 16.17 | 8 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 2.666 | 1.333 | 1.832 | 1 | 79.73 | 24.03 | 11.07 | 12.93 | 6.74 | 6.194 | -9.08 | 12.07 | 21.15 | 8 | True | 2.921041186709772e-11 | None | none | 0.0 | hybrid_threshold |
