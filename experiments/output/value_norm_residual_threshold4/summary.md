# First-Boundary Targeted Split

Generated: 2026-07-04T23:04:17
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = threshold
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 4.0, residual_threshold_mode = value_norm, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 1.618572751340554e-15 | 1.195752858752444e-15 | 1.195752858752444e-15 | None | (1, 10) | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | 0.2803 | 0.1402 | 1.344 | 0.6721 | 0.6721 | None | (1, 10) | True | 1.2212453270876722e-11 | 9.985 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 4 | 6 | 6 | 30 | 0 | 0.0 | 7.36 | 1.233 | 4.4408920985006264e-17 | 2.2204460492503132e-17 | 6.691084185092072e-16 | 3.345542092546036e-16 | 3.345542092546036e-16 | None | (4, 11) | True | 1.7763568394002505e-15 | 110.1 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 4 | 6 | 6 | 30 | 0 | 0.0 | 6.72 | 1.965 | 3.256 | 0.1325 | 42.63 | 2.173 | 2.173 | None | (4, 11) | True | 0.1152 | 110.1 | None | none | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 6.376 | 4.31 | 2.691 | 1.345 | 3.74 | 1.87 | 1.87 | None | (6, 19) | True | 0.0 | 73.47 | None | none | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 6.304 | 3.335 | 2.666 | 1.333 | 3.664 | 1.832 | 1.832 | None | (6, 19) | True | 2.921041186709772e-11 | 71.66 | None | none | hybrid_threshold |
| open_room | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 7.365 | 1.883 | 8.881784197001253e-17 | 2.2204460492503132e-17 | 1.769318457215217e-15 | 4.4232961430380427e-16 | 4.4232961430380427e-16 | None | (4, 7) | True | 0.0 | 43.97 | None | none | hybrid_threshold |
| open_room | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 8.263 | 3.935 | 1.34 | 0.1349 | 11.16 | 0.9484 | 0.9484 | None | (5, 6) | True | 0.0788 | 45.56 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_threshold_metric_valid_total | residual_threshold_metric_max | residual_backup_value_norm_max | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | 1.618572751340554e-15 | 1.195752858752444e-15 | 1.195752858752444e-15 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | 0.2803 | 0.1402 | 1.344 | 0.6721 | 0.6721 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | 9.906 | 4.953 | 4.953 | True | 0.0 | (1, 7) | model_residual | 4.953 | continue |
| open_room | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 4.373 | 1.52 | 0.9839 | 0.9839 | 4.953 | 4.953 | 4.953 | True | 0.0 | (5, 1) | model_residual | 4.953 | continue |
| open_room | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 7.365 | 1.883 | 8.881784197001253e-17 | 2.2204460492503132e-17 | 1.769318457215217e-15 | 4.4232961430380427e-16 | 4.4232961430380427e-16 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | 8.897 | 4.449 | 4.449 | True | 0.0788 | (5, 1) | model_residual | 4.163 | continue |
| open_room | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 7.962 | 3.935 | 1.483 | 0.9134 | 9.122 | 4.449 | 4.449 | True | 0.0788 | (1, 7) | model_residual | 4.163 | continue |
| open_room | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 8.263 | 3.935 | 1.34 | 0.1349 | 11.16 | 0.9484 | 0.9484 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | 0.0 | 3.375 | 3.375 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | 6.848 | 6.848 | 6.848 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | 13.7 | 6.848 | 6.848 | True | 1.7763568394002505e-15 | (1, 5) | model_residual | 6.848 | continue |
| four_rooms | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 6.057 | 1.233 | 1.013 | 1.013 | 6.848 | 6.848 | 6.848 | True | 1.7763568394002505e-15 | (5, 7) | model_residual | 6.848 | continue |
| four_rooms | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 7.36 | 1.233 | 4.4408920985006264e-17 | 2.2204460492503132e-17 | 6.691084185092072e-16 | 3.345542092546036e-16 | 3.345542092546036e-16 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | 0.0 | 3.186 | 3.186 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | 1.296 | 6.386 | 6.386 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | 25.36 | 6.385 | 6.385 | True | 0.1152 | (1, 5) | model_residual | 6.169 | continue |
| four_rooms | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 4.502 | 1.83 | 3.064 | 0.9752 | 32.33 | 6.385 | 6.385 | True | 0.1152 | (5, 7) | model_residual | 6.169 | continue |
| four_rooms | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 6.72 | 1.965 | 3.256 | 0.1325 | 42.63 | 2.173 | 2.173 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | 3.74 | 1.87 | 1.87 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | 3.664 | 1.832 | 1.832 | True | 2.921041186709772e-11 | None | none | 0.0 | hybrid_threshold |
