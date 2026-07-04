# First-Boundary Targeted Split

Generated: 2026-07-04T22:41:44
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = never
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = threshold
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 3.0, residual_threshold = 0.5, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | None | None | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | 0.2803 | 0.1402 | None | None | True | 1.2212453270876722e-11 | 9.985 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | 2.026 | 1.013 | (1, 5) | None | True | 1.7763568394002505e-15 | 67.95 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | (5, 7) | None | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 6.712 | 2.579 | 5.155 | 1.345 | (1, 5) | None | True | 0.0 | 150.1 | None | none | hybrid_threshold |
| maze | 0.05 | 5 | 7 | 7 | 42 | 0 | 0.0 | 20.69 | 2.862 | 25.15 | 1.313 | (3, 1) | None | True | 1.7255530337934033e-11 | 313.7 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | (1, 7) | None | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 1 | 3 | 3 | 6 | 0 | 0.0 | 6.001 | 2.983 | 2.95 | 0.9134 | (5, 1) | None | True | 0.0788 | 33.85 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | 0.2803 | 0.1402 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | True | 0.0788 | (5, 3) | soft_threshold | 0.8797 | continue |
| open_room | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 6.001 | 2.983 | 2.95 | 0.9134 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | True | 0.0 | (6, 19) | soft_threshold | 0.97 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 6.886 | 3.443 | 3.978 | 1.387 | True | 0.0 | (5, 19) | soft_threshold | 0.9409 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 6.712 | 2.579 | 5.155 | 1.345 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | True | 2.921041186709772e-11 | (5, 7) | soft_threshold | 0.5747 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 13.62 | 5.634 | 7.103 | 1.33 | True | 2.921041186709772e-11 | (7, 18) | soft_threshold | 1.034 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 21.04 | 4.656 | 10.82 | 1.313 | True | 2.921041186709772e-11 | (7, 17) | soft_threshold | 1.968 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 21.9 | 3.793 | 13.65 | 1.313 | True | 2.319922032256727e-11 | (7, 9) | soft_threshold | 2.513 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 22.72 | 3.385 | 21.35 | 1.313 | True | 2.3302249019252486e-11 | (7, 16) | soft_threshold | 2.858 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 20.69 | 2.862 | 25.15 | 1.313 | True | 1.7255530337934033e-11 | None | none | 0.0 | hybrid_threshold |
