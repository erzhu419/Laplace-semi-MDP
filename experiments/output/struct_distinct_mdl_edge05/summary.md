# First-Boundary Targeted Split

Generated: 2026-07-05T05:27:14
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = mdl
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 0.5, residual_threshold_mode = raw, compute_struct_distinct = True, struct_mdl_node_cost_weight = 1.0, struct_mdl_edge_cost_weight = 0.5, struct_mdl_exposure_bit_weight = 1.0, struct_mdl_min_gain = 0.0, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | struct_mdl_split_benefit | struct_mdl_split_cost | struct_mdl_split_gain | struct_mdl_split_candidate_coord | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 2 | 1 | 9.672 | -8.672 | None | (1, 5) | (4, 11) | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 1.938 | 0.9342 | 9.672 | -8.738 | None | (5, 7) | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 9 | 11 | 11 | 110 | 0 | 0.0 | 41.66 | 2.741 | 44.38 | 1.345 | 44.38 | 1.345 | 8.446 | 1 | 1794 | 55 | 11 | 17.34 | -6.34 | None | (3, 7) | (6, 19) | True | 3.552713678800501e-15 | 545.5 | None | none | hybrid_threshold |
| maze | 0.05 | 12 | 14 | 14 | 182 | 0 | 0.0 | 31.61 | 3.317 | 35.74 | 1.313 | 35.74 | 1.313 | 4.677 | 0.9997 | 169.2 | 25.04 | 13.99 | 20.34 | -6.348 | None | (1, 13) | (6, 19) | True | 2.917133201663091e-11 | 687.7 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 2 | 1 | 7.129 | -6.129 | None | (1, 7) | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 1.872 | 0.8758 | 7.129 | -6.253 | None | (5, 1) | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | struct_mdl_split_benefit | struct_mdl_split_cost | struct_mdl_split_gain | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 1.968 | 0.9839 | 4.953 | 1 | 79.73 | 2 | 1 | 7.129 | -6.129 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 1.827 | 0.9134 | 4.449 | 0.9358 | 7.924 | 1.872 | 0.8758 | 7.129 | -6.253 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 0.9531 | 3.375 | 1 | 0.0 | 0.0 | 0.0 | 7.672 | 0.0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 1.013 | 1.046 | 6.848 | 1 | 39.86 | 1 | 1 | 8.672 | -7.672 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 2.026 | 1.013 | 6.848 | 1 | 79.73 | 2 | 1 | 9.672 | -8.672 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 0.9354 | 3.186 | 1 | 0.0 | 0.0 | 0.0 | 7.672 | 0.0 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 0.2029 | 1.038 | 6.386 | 1 | 0.0009352 | 0.0006481 | 1.966e-07 | 8.672 | -8.672 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 3.066 | 0.9752 | 6.385 | 0.9664 | 9.799 | 1.938 | 0.9342 | 9.672 | -8.738 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 2.691 | 1.345 | 1.87 | 1 | 79.73 | 24 | 13 | 8.34 | 4.66 | True | 0.0 | (1, 5) | residual_mdl | 4.66 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 12.63 | 4.31 | 5.295 | 1.345 | 5.295 | 1.345 | 1.965 | 1 | 159.5 | 47 | 36 | 9.34 | 26.66 | True | 0.0 | (1, 7) | residual_mdl | 26.66 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 17.33 | 4.31 | 10.28 | 1.345 | 10.28 | 1.345 | 5.957 | 1 | 358.8 | 55 | 36 | 10.34 | 25.66 | True | 3.552713678800501e-15 | (1, 13) | residual_mdl | 25.66 | continue |
| maze | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 22.11 | 4.31 | 12.44 | 1.345 | 12.44 | 1.345 | 5.957 | 1 | 438.5 | 61 | 40 | 11.34 | 28.66 | True | 0.0 | (1, 15) | residual_mdl | 28.66 | continue |
| maze | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 26.98 | 4.31 | 20.2 | 1.345 | 20.2 | 1.345 | 5.957 | 1 | 757.4 | 65 | 30 | 12.34 | 17.66 | True | 0.0 | (1, 19) | residual_mdl | 17.66 | continue |
| maze | 0.0 | 5 | 7 | 42 | 0.0 | 0 | 31.73 | 4.31 | 23.06 | 1.345 | 23.06 | 1.345 | 5.957 | 1 | 877 | 67 | 28 | 13.34 | 14.66 | True | 0.0 | (3, 17) | residual_mdl | 14.66 | continue |
| maze | 0.0 | 6 | 8 | 56 | 0.0 | 0 | 36.53 | 4.31 | 33.48 | 1.345 | 33.48 | 1.345 | 8.446 | 1 | 1315 | 67 | 16 | 14.34 | 1.66 | True | 0.0 | (3, 5) | residual_mdl | 1.66 | continue |
| maze | 0.0 | 7 | 9 | 72 | 0.0 | 0 | 40.84 | 4.31 | 37.18 | 1.345 | 37.18 | 1.345 | 8.446 | 1 | 1475 | 65 | 18 | 15.34 | 2.66 | True | 3.552713678800501e-15 | (3, 13) | residual_mdl | 2.66 | continue |
| maze | 0.0 | 8 | 10 | 90 | 0.0 | 0 | 45.15 | 4.31 | 40.81 | 1.345 | 40.81 | 1.345 | 8.446 | 1 | 1634 | 61 | 20 | 16.34 | 3.66 | True | 3.552713678800501e-15 | (5, 17) | residual_mdl | 3.66 | continue |
| maze | 0.0 | 9 | 11 | 110 | 0.0 | 0 | 41.66 | 2.741 | 44.38 | 1.345 | 44.38 | 1.345 | 8.446 | 1 | 1794 | 55 | 11 | 17.34 | -6.34 | True | 3.552713678800501e-15 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 2.666 | 1.333 | 1.832 | 1 | 79.73 | 24.03 | 12.93 | 8.34 | 4.594 | True | 2.921041186709772e-11 | (5, 19) | residual_mdl | 4.594 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 7.821 | 3.323 | 4.226 | 1.333 | 4.226 | 1.333 | 2.176 | 1 | 91.42 | 35.24 | 24.18 | 9.34 | 14.84 | True | 2.921041186709772e-11 | (5, 17) | residual_mdl | 14.84 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 11.39 | 3.317 | 6.044 | 1.332 | 6.044 | 1.332 | 2.176 | 1 | 131.3 | 44.22 | 33.18 | 10.34 | 22.84 | True | 2.8975932764296886e-11 | (3, 17) | residual_mdl | 22.84 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 13.41 | 3.317 | 8.088 | 1.332 | 8.088 | 1.332 | 2.176 | 1 | 171.1 | 51.21 | 40.18 | 11.34 | 28.84 | True | 2.921041186709772e-11 | (3, 19) | residual_mdl | 28.84 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 15.43 | 3.317 | 10.36 | 1.332 | 10.36 | 1.332 | 2.176 | 1 | 211 | 56.19 | 45.19 | 12.34 | 32.85 | True | 2.919975372606132e-11 | (1, 19) | residual_mdl | 32.85 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 17.46 | 3.317 | 12.75 | 1.332 | 12.75 | 1.332 | 2.176 | 1 | 250.9 | 59.17 | 48.19 | 13.34 | 34.85 | True | 2.9192648298703716e-11 | (1, 5) | residual_mdl | 34.85 | continue |
| maze | 0.05 | 6 | 8 | 56 | 0.0 | 0 | 19.48 | 3.317 | 16.9 | 1.313 | 16.9 | 1.313 | 2.345 | 1 | 169.2 | 67.03 | 55.99 | 14.34 | 41.65 | True | 2.9196201012382517e-11 | (3, 5) | residual_mdl | 41.65 | continue |
| maze | 0.05 | 7 | 9 | 72 | 0.0 | 0 | 21.5 | 3.317 | 19.77 | 1.313 | 19.77 | 1.313 | 2.475 | 0.9997 | 110.9 | 65.02 | 53.97 | 15.34 | 38.63 | True | 2.8968827336939285e-11 | (3, 7) | residual_mdl | 38.63 | continue |
| maze | 0.05 | 8 | 10 | 90 | 0.0 | 0 | 23.52 | 3.317 | 22.84 | 1.313 | 22.84 | 1.313 | 2.635 | 0.9997 | 122.5 | 61.02 | 49.97 | 16.34 | 33.63 | True | 2.920330643974012e-11 | (1, 7) | residual_mdl | 33.63 | continue |
| maze | 0.05 | 9 | 11 | 110 | 0.0 | 0 | 25.54 | 3.317 | 24.96 | 1.313 | 24.96 | 1.313 | 2.612 | 0.9997 | 134.2 | 55.02 | 43.97 | 17.34 | 26.63 | True | 2.917133201663091e-11 | (1, 15) | residual_mdl | 26.63 | continue |
| maze | 0.05 | 10 | 12 | 132 | 0.0 | 0 | 27.57 | 3.317 | 28.54 | 1.313 | 28.54 | 1.313 | 3.447 | 1 | 204.2 | 47.03 | 35.99 | 18.34 | 17.65 | True | 2.917133201663091e-11 | (3, 15) | residual_mdl | 17.65 | continue |
| maze | 0.05 | 11 | 13 | 156 | 0.0 | 0 | 29.59 | 3.317 | 32.06 | 1.313 | 32.06 | 1.313 | 3.938 | 0.9997 | 157.5 | 37.03 | 25.98 | 19.34 | 6.644 | True | 2.917133201663091e-11 | (3, 13) | residual_mdl | 6.644 | continue |
| maze | 0.05 | 12 | 14 | 182 | 0.0 | 0 | 31.61 | 3.317 | 35.74 | 1.313 | 35.74 | 1.313 | 4.677 | 0.9997 | 169.2 | 25.04 | 13.99 | 20.34 | -6.348 | True | 2.917133201663091e-11 | None | none | 0.0 | hybrid_threshold |
