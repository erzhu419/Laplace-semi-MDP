# First-Boundary Targeted Split

Generated: 2026-07-05T05:26:02
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = mdl
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 0.5, residual_threshold_mode = raw, compute_struct_distinct = True, struct_mdl_node_cost_weight = 1.0, struct_mdl_edge_cost_weight = 1.0, struct_mdl_exposure_bit_weight = 1.0, struct_mdl_min_gain = 0.0, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | struct_mdl_split_benefit | struct_mdl_split_cost | struct_mdl_split_gain | struct_mdl_split_candidate_coord | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 2 | 1 | 13.67 | -12.67 | None | (1, 5) | (4, 11) | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 1.938 | 0.9342 | 13.67 | -12.74 | None | (5, 7) | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 6 | 8 | 8 | 56 | 0 | 0.0 | 36.53 | 4.31 | 33.48 | 1.345 | 33.48 | 1.345 | 8.446 | 1 | 1315 | 67 | 16 | 22.34 | -6.34 | None | (3, 19) | (6, 19) | True | 0.0 | 376.5 | None | none | hybrid_threshold |
| maze | 0.05 | 11 | 13 | 13 | 156 | 0 | 0.0 | 29.59 | 3.317 | 32.06 | 1.313 | 32.06 | 1.313 | 3.938 | 0.9997 | 157.5 | 37.03 | 25.98 | 32.34 | -6.356 | None | (1, 13) | (6, 19) | True | 2.917133201663091e-11 | 623.5 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 2 | 1 | 9.129 | -8.129 | None | (1, 7) | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 1.872 | 0.8758 | 9.129 | -8.253 | None | (5, 1) | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | struct_mdl_split_benefit | struct_mdl_split_cost | struct_mdl_split_gain | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 2 | 1 | 9.129 | -8.129 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 1.872 | 0.8758 | 9.129 | -8.253 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 0.9531 | 3.375 | 1 | 0.0 | 0.0 | 0.0 | 9.672 | 0.0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 1.013 | 1.046 | 6.848 | 1 | 39.86 | 1 | 1 | 11.67 | -10.67 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 2 | 1 | 13.67 | -12.67 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 0.9354 | 3.186 | 1 | 0.0 | 0.0 | 0.0 | 9.672 | 0.0 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 0.2029 | 1.038 | 6.386 | 1 | 0.0009352 | 0.0006481 | 1.966e-07 | 11.67 | -11.67 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 1.938 | 0.9342 | 13.67 | -12.74 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 2.691 | 1.345 | 1.87 | 1 | 79.73 | 24 | 13 | 10.34 | 2.66 | True | 0.0 | (1, 5) | residual_mdl | 2.66 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 12.63 | 4.31 | 5.295 | 1.345 | 5.295 | 1.345 | 1.965 | 1 | 159.5 | 47 | 36 | 12.34 | 23.66 | True | 0.0 | (1, 7) | residual_mdl | 23.66 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 17.33 | 4.31 | 10.28 | 1.345 | 10.28 | 1.345 | 5.957 | 1 | 358.8 | 55 | 36 | 14.34 | 21.66 | True | 3.552713678800501e-15 | (1, 13) | residual_mdl | 21.66 | continue |
| maze | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 22.11 | 4.31 | 12.44 | 1.345 | 12.44 | 1.345 | 5.957 | 1 | 438.5 | 61 | 40 | 16.34 | 23.66 | True | 0.0 | (1, 15) | residual_mdl | 23.66 | continue |
| maze | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 26.98 | 4.31 | 20.2 | 1.345 | 20.2 | 1.345 | 5.957 | 1 | 757.4 | 65 | 30 | 18.34 | 11.66 | True | 0.0 | (1, 19) | residual_mdl | 11.66 | continue |
| maze | 0.0 | 5 | 7 | 42 | 0.0 | 0 | 31.73 | 4.31 | 23.06 | 1.345 | 23.06 | 1.345 | 5.957 | 1 | 877 | 67 | 28 | 20.34 | 7.66 | True | 0.0 | (3, 17) | residual_mdl | 7.66 | continue |
| maze | 0.0 | 6 | 8 | 56 | 0.0 | 0 | 36.53 | 4.31 | 33.48 | 1.345 | 33.48 | 1.345 | 8.446 | 1 | 1315 | 67 | 16 | 22.34 | -6.34 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 2.666 | 1.333 | 1.832 | 1 | 79.73 | 24.03 | 12.93 | 10.34 | 2.594 | True | 2.921041186709772e-11 | (5, 19) | residual_mdl | 2.594 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 7.821 | 3.323 | 4.226 | 1.333 | 4.226 | 1.333 | 2.176 | 1 | 91.42 | 35.24 | 24.18 | 12.34 | 11.84 | True | 2.921041186709772e-11 | (5, 17) | residual_mdl | 11.84 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 11.39 | 3.317 | 6.044 | 1.332 | 6.044 | 1.332 | 2.176 | 1 | 131.3 | 44.22 | 33.18 | 14.34 | 18.84 | True | 2.8975932764296886e-11 | (3, 17) | residual_mdl | 18.84 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 13.41 | 3.317 | 8.088 | 1.332 | 8.088 | 1.332 | 2.176 | 1 | 171.1 | 51.21 | 40.18 | 16.34 | 23.84 | True | 2.921041186709772e-11 | (3, 19) | residual_mdl | 23.84 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 15.43 | 3.317 | 10.36 | 1.332 | 10.36 | 1.332 | 2.176 | 1 | 211 | 56.19 | 45.19 | 18.34 | 26.85 | True | 2.919975372606132e-11 | (1, 19) | residual_mdl | 26.85 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 17.46 | 3.317 | 12.75 | 1.332 | 12.75 | 1.332 | 2.176 | 1 | 250.9 | 59.17 | 48.19 | 20.34 | 27.85 | True | 2.9192648298703716e-11 | (1, 5) | residual_mdl | 27.85 | continue |
| maze | 0.05 | 6 | 8 | 56 | 0.0 | 0 | 19.48 | 3.317 | 16.9 | 1.313 | 16.9 | 1.313 | 2.345 | 1 | 169.2 | 67.03 | 55.99 | 22.34 | 33.65 | True | 2.9196201012382517e-11 | (3, 5) | residual_mdl | 33.65 | continue |
| maze | 0.05 | 7 | 9 | 72 | 0.0 | 0 | 21.5 | 3.317 | 19.77 | 1.313 | 19.77 | 1.313 | 2.475 | 0.9997 | 110.9 | 65.02 | 53.97 | 24.34 | 29.63 | True | 2.8968827336939285e-11 | (3, 7) | residual_mdl | 29.63 | continue |
| maze | 0.05 | 8 | 10 | 90 | 0.0 | 0 | 23.52 | 3.317 | 22.84 | 1.313 | 22.84 | 1.313 | 2.635 | 0.9997 | 122.5 | 61.02 | 49.97 | 26.34 | 23.63 | True | 2.920330643974012e-11 | (1, 7) | residual_mdl | 23.63 | continue |
| maze | 0.05 | 9 | 11 | 110 | 0.0 | 0 | 25.54 | 3.317 | 24.96 | 1.313 | 24.96 | 1.313 | 2.612 | 0.9997 | 134.2 | 55.02 | 43.97 | 28.34 | 15.63 | True | 2.917133201663091e-11 | (1, 15) | residual_mdl | 15.63 | continue |
| maze | 0.05 | 10 | 12 | 132 | 0.0 | 0 | 27.57 | 3.317 | 28.54 | 1.313 | 28.54 | 1.313 | 3.447 | 1 | 204.2 | 47.03 | 35.99 | 30.34 | 5.647 | True | 2.917133201663091e-11 | (3, 15) | residual_mdl | 5.647 | continue |
| maze | 0.05 | 11 | 13 | 156 | 0.0 | 0 | 29.59 | 3.317 | 32.06 | 1.313 | 32.06 | 1.313 | 3.938 | 0.9997 | 157.5 | 37.03 | 25.98 | 32.34 | -6.356 | True | 2.917133201663091e-11 | None | none | 0.0 | hybrid_threshold |
