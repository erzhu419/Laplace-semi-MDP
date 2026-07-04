# First-Boundary Targeted Split

Generated: 2026-07-04T23:40:55
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = threshold
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 1.0, residual_threshold_mode = struct_bits, compute_struct_distinct = False, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| four_rooms | 0.0 | 4 | 6 | 6 | 30 | 0 | 0.0 | 7.36 | 1.233 | 4.4408920985006264e-17 | 2.2204460492503132e-17 | 0.0 | -0.0 | 3.345542092546036e-16 | 0.0 | 0.0 | 0.0 | None | (4, 11) | True | 1.7763568394002505e-15 | 110.1 | None | none | hybrid_threshold |
| maze | 0.0 | 12 | 14 | 14 | 182 | 0 | 0.0 | 40.45 | 2.066 | 15.04 | 1.345 | 597.9 | 39.86 | 8.446 | 1 | 597.9 | 0.0 | (3, 15) | (6, 19) | True | 3.552713678800501e-15 | 686 | (3, 15) | model_residual | max_splits |
| open_room | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 7.365 | 1.883 | 8.881784197001253e-17 | 2.2204460492503132e-17 | 0.0 | -0.0 | 4.4232961430380427e-16 | 0.0 | 0.0 | 0.0 | None | (4, 7) | True | 0.0 | 43.97 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_bits_valid_total | struct_hidden_distinct_valid_total | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 79.73 | 39.86 | 4.953 | 1 | 79.73 | 0.0 | True | 0.0 | (1, 7) | model_residual | 39.86 | continue |
| open_room | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 4.373 | 1.52 | 0.9839 | 0.9839 | 39.86 | 39.86 | 4.953 | 1 | 39.86 | 0.0 | True | 0.0 | (5, 1) | model_residual | 39.86 | continue |
| open_room | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 7.365 | 1.883 | 8.881784197001253e-17 | 2.2204460492503132e-17 | 0.0 | -0.0 | 4.4232961430380427e-16 | 0.0 | 0.0 | 0.0 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 39.86 | 3.375 | 1 | 0.0 | 0.0 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 39.86 | 39.86 | 6.848 | 1 | 39.86 | 0.0 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 79.73 | 39.86 | 6.848 | 1 | 79.73 | 0.0 | True | 1.7763568394002505e-15 | (1, 5) | model_residual | 39.86 | continue |
| four_rooms | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 6.057 | 1.233 | 1.013 | 1.013 | 39.86 | 39.86 | 6.848 | 1 | 39.86 | 0.0 | True | 1.7763568394002505e-15 | (5, 7) | model_residual | 39.86 | continue |
| four_rooms | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 7.36 | 1.233 | 4.4408920985006264e-17 | 2.2204460492503132e-17 | 0.0 | -0.0 | 3.345542092546036e-16 | 0.0 | 0.0 | 0.0 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 79.73 | 39.86 | 1.87 | 1 | 79.73 | 0.0 | True | 0.0 | (5, 19) | model_residual | 39.86 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 8.589 | 2.579 | 3.916 | 1.345 | 119.6 | 39.86 | 1.914 | 1 | 119.6 | 0.0 | True | 0.0 | (5, 17) | model_residual | 39.86 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 11.14 | 2.066 | 5.11 | 1.345 | 159.5 | 39.86 | 1.965 | 1 | 159.5 | 0.0 | True | 0.0 | (1, 5) | model_residual | 79.73 | continue |
| maze | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 14.36 | 2.066 | 7.766 | 1.345 | 239.2 | 39.86 | 2.09 | 1 | 239.2 | 0.0 | True | 0.0 | (3, 5) | model_residual | 119.6 | continue |
| maze | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 17.18 | 2.066 | 8.943 | 1.345 | 279 | 39.86 | 2.167 | 1 | 279 | 0.0 | True | 3.552713678800501e-15 | (3, 17) | model_residual | 119.6 | continue |
| maze | 0.0 | 5 | 7 | 42 | 0.0 | 0 | 21.26 | 2.066 | 10.08 | 1.345 | 318.9 | 39.86 | 2.259 | 1 | 318.9 | 0.0 | True | 3.552713678800501e-15 | (3, 7) | model_residual | 159.5 | continue |
| maze | 0.0 | 6 | 8 | 56 | 0.0 | 0 | 24 | 2.066 | 11.16 | 1.345 | 358.8 | 39.86 | 2.368 | 1 | 358.8 | 0.0 | True | 0.0 | (3, 19) | model_residual | 159.5 | continue |
| maze | 0.0 | 7 | 9 | 72 | 0.0 | 0 | 26.74 | 2.066 | 12.2 | 1.345 | 398.6 | 39.86 | 2.499 | 1 | 398.6 | 0.0 | True | 3.552713678800501e-15 | (1, 7) | model_residual | 199.3 | continue |
| maze | 0.0 | 8 | 10 | 90 | 0.0 | 0 | 29.48 | 2.066 | 12.27 | 1.345 | 438.5 | 39.86 | 2.661 | 1 | 438.5 | 0.0 | True | 3.552713678800501e-15 | (1, 19) | model_residual | 199.3 | continue |
| maze | 0.0 | 9 | 11 | 110 | 0.0 | 0 | 32.22 | 2.066 | 12.55 | 1.345 | 478.4 | 39.86 | 2.647 | 1 | 478.4 | 0.0 | True | 3.552713678800501e-15 | (1, 13) | model_residual | 239.2 | continue |
| maze | 0.0 | 10 | 12 | 132 | 0.0 | 0 | 34.96 | 2.066 | 13.71 | 1.345 | 518.2 | 39.86 | 3.972 | 1 | 518.2 | 0.0 | True | 3.552713678800501e-15 | (1, 15) | model_residual | 239.2 | continue |
| maze | 0.0 | 11 | 13 | 156 | 0.0 | 0 | 37.7 | 2.066 | 14.51 | 1.345 | 558.1 | 39.86 | 5.957 | 1 | 558.1 | 0.0 | True | 3.552713678800501e-15 | (3, 13) | model_residual | 279 | continue |
| maze | 0.0 | 12 | 14 | 182 | 0.0 | 0 | 40.45 | 2.066 | 15.04 | 1.345 | 597.9 | 39.86 | 8.446 | 1 | 597.9 | 0.0 | True | 3.552713678800501e-15 | (3, 15) | model_residual | 558.1 | max_splits |
