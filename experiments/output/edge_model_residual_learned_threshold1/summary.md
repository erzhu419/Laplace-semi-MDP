# First-Boundary Targeted Split

Generated: 2026-07-04T22:39:42
candidate_kind = articulation_only, candidate_top_fraction = 0.15
residual_kind = turn_articulation, residual_top_fraction = 0.15, residual_split_policy = threshold
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, residual_threshold = 1.0, residual_reward_weight = 0.05, residual_hit_weight = 0.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | residual_split_candidate_coord | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | None | (1, 10) | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | 0.2803 | 0.1402 | None | (1, 10) | True | 1.2212453270876722e-11 | 9.985 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 4 | 6 | 6 | 30 | 0 | 0.0 | 7.36 | 1.233 | 4.4408920985006264e-17 | 2.2204460492503132e-17 | None | (4, 11) | True | 1.7763568394002505e-15 | 110.1 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | 3.066 | 0.9752 | None | (4, 11) | True | 0.1152 | 66.24 | None | none | hybrid_threshold |
| maze | 0.0 | 12 | 14 | 14 | 182 | 0 | 0.0 | 75.45 | 2.741 | 19.47 | 1.317 | (3, 17) | (6, 19) | True | 3.552713678800501e-15 | 729.9 | (3, 17) | model_residual | max_splits |
| maze | 0.05 | 12 | 14 | 14 | 182 | 0 | 0.0 | 31.61 | 3.317 | 35.74 | 1.313 | (1, 13) | (6, 19) | True | 2.917133201663091e-11 | 687.7 | (1, 13) | model_residual | max_splits |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | 1.968 | 0.9839 | None | (4, 7) | True | 0.0 | 18.06 | None | none | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 3.355 | 3.337 | 1.827 | 0.9134 | None | (5, 3) | True | 0.0788 | 18.46 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | model_residual_valid_total | model_residual_max | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | 3.108624468950438e-16 | 1.9984014443252818e-16 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | 0.2803 | 0.1402 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | 1.968 | 0.9839 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | 1.827 | 0.9134 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | 0.0 | 0.9531 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | 1.013 | 1.046 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | 2.026 | 1.013 | True | 1.7763568394002505e-15 | (1, 5) | model_residual | 1.013 | continue |
| four_rooms | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 6.057 | 1.233 | 1.013 | 1.013 | True | 1.7763568394002505e-15 | (5, 7) | model_residual | 1.013 | continue |
| four_rooms | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 7.36 | 1.233 | 4.4408920985006264e-17 | 2.2204460492503132e-17 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | 0.0 | 0.9354 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | 0.2029 | 1.038 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | 3.066 | 0.9752 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | 2.691 | 1.345 | True | 0.0 | (3, 1) | model_residual | 1.345 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 11.53 | 5.025 | 3.916 | 1.345 | True | 0.0 | (5, 19) | model_residual | 1.345 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 14.71 | 5.025 | 5.141 | 1.331 | True | 0.0 | (3, 3) | model_residual | 1.331 | continue |
| maze | 0.0 | 3 | 5 | 20 | 0.0 | 0 | 23.18 | 5.025 | 7.651 | 1.331 | True | 0.0 | (5, 3) | model_residual | 2.633 | continue |
| maze | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 29.47 | 5.025 | 8.796 | 1.331 | True | 0.0 | (7, 15) | model_residual | 3.624 | continue |
| maze | 0.0 | 5 | 7 | 42 | 0.0 | 0 | 35.99 | 2.741 | 11.43 | 1.331 | True | 0.0 | (5, 15) | model_residual | 5.065 | continue |
| maze | 0.0 | 6 | 8 | 56 | 0.0 | 0 | 37.43 | 2.741 | 12.18 | 1.331 | True | 3.552713678800501e-15 | (5, 1) | model_residual | 4.989 | continue |
| maze | 0.0 | 7 | 9 | 72 | 0.0 | 0 | 42 | 2.741 | 13.15 | 1.331 | True | 0.0 | (7, 13) | model_residual | 5.672 | continue |
| maze | 0.0 | 8 | 10 | 90 | 0.0 | 0 | 46.57 | 2.741 | 13.5 | 1.331 | True | 0.0 | (7, 1) | model_residual | 5.914 | continue |
| maze | 0.0 | 9 | 11 | 110 | 0.0 | 0 | 51.14 | 2.741 | 13.77 | 1.331 | True | 3.552713678800501e-15 | (7, 5) | model_residual | 5.33 | continue |
| maze | 0.0 | 10 | 12 | 132 | 0.0 | 0 | 55.71 | 2.741 | 14.58 | 1.331 | True | 3.552713678800501e-15 | (5, 5) | model_residual | 5.528 | continue |
| maze | 0.0 | 11 | 13 | 156 | 0.0 | 0 | 60.28 | 2.741 | 14.66 | 1.331 | True | 3.552713678800501e-15 | (5, 17) | model_residual | 1.331 | continue |
| maze | 0.0 | 12 | 14 | 182 | 0.0 | 0 | 75.45 | 2.741 | 19.47 | 1.317 | True | 3.552713678800501e-15 | (3, 17) | model_residual | 3.95 | max_splits |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | 2.666 | 1.333 | True | 2.921041186709772e-11 | (5, 19) | model_residual | 1.31 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 7.821 | 3.323 | 4.226 | 1.333 | True | 2.921041186709772e-11 | (5, 17) | model_residual | 1.312 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 11.39 | 3.317 | 6.044 | 1.332 | True | 2.8975932764296886e-11 | (1, 5) | model_residual | 2.4 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 13.41 | 3.317 | 9.453 | 1.313 | True | 2.920685915341892e-11 | (3, 5) | model_residual | 3.805 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 15.43 | 3.317 | 11.79 | 1.313 | True | 2.8972380050618085e-11 | (3, 17) | model_residual | 3.753 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 17.46 | 3.317 | 14.33 | 1.313 | True | 2.8972380050618085e-11 | (3, 7) | model_residual | 4.932 | continue |
| maze | 0.05 | 6 | 8 | 56 | 0.0 | 0 | 19.48 | 3.317 | 17.09 | 1.313 | True | 2.920330643974012e-11 | (3, 19) | model_residual | 4.855 | continue |
| maze | 0.05 | 7 | 9 | 72 | 0.0 | 0 | 21.5 | 3.317 | 20.06 | 1.313 | True | 2.919975372606132e-11 | (1, 7) | model_residual | 5.966 | continue |
| maze | 0.05 | 8 | 10 | 90 | 0.0 | 0 | 23.52 | 3.317 | 22.28 | 1.313 | True | 2.917133201663091e-11 | (1, 19) | model_residual | 5.856 | continue |
| maze | 0.05 | 9 | 11 | 110 | 0.0 | 0 | 25.54 | 3.317 | 24.96 | 1.313 | True | 2.917133201663091e-11 | (1, 15) | model_residual | 5.247 | continue |
| maze | 0.05 | 10 | 12 | 132 | 0.0 | 0 | 27.57 | 3.317 | 28.54 | 1.313 | True | 2.917133201663091e-11 | (3, 15) | model_residual | 5.484 | continue |
| maze | 0.05 | 11 | 13 | 156 | 0.0 | 0 | 29.59 | 3.317 | 32.06 | 1.313 | True | 2.917133201663091e-11 | (3, 13) | model_residual | 5.34 | continue |
| maze | 0.05 | 12 | 14 | 182 | 0.0 | 0 | 31.61 | 3.317 | 35.74 | 1.313 | True | 2.917133201663091e-11 | (1, 13) | model_residual | 5.188 | max_splits |
