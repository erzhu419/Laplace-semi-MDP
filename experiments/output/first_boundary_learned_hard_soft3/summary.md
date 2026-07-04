# First-Boundary Targeted Split

Generated: 2026-07-04T22:29:12
candidate_kind = articulation_only, candidate_top_fraction = 0.15
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = threshold
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 3.0, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | None | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | None | True | 1.2212453270876722e-11 | 9.705 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 4.824 | 1.233 | None | True | 1.7763568394002505e-15 | 65.92 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 3.834 | 1.83 | None | True | 0.1152 | 63.17 | None | none | hybrid_threshold |
| maze | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 6.712 | 2.579 | None | True | 0.0 | 144.9 | None | none | hybrid_threshold |
| maze | 0.05 | 5 | 7 | 7 | 42 | 0 | 0.0 | 20.69 | 2.862 | None | True | 1.7255530337934033e-11 | 288.6 | None | none | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 2.49 | 1.52 | None | True | 0.0 | 16.09 | None | none | hybrid_threshold |
| open_room | 0.05 | 1 | 3 | 3 | 6 | 0 | 0.0 | 6.001 | 2.983 | None | True | 0.0788 | 30.9 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 2.49 | 1.52 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 3.355 | 3.337 | True | 0.0788 | (5, 3) | soft_threshold | 0.8797 | continue |
| open_room | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 6.001 | 2.983 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 3 | 1 | 3 | 3.591 | 1.233 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 4.824 | 1.233 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | False | inf | (3, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.05 | 1 | 3 | 2 | 1 | 4 | 0.0003653 | 0.6677 | False | inf | (3, 7) | hard_hidden | 3 | continue |
| four_rooms | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 3.834 | 1.83 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 6.376 | 4.31 | True | 0.0 | (6, 19) | soft_threshold | 0.97 | continue |
| maze | 0.0 | 1 | 3 | 6 | 0.0 | 0 | 6.886 | 3.443 | True | 0.0 | (5, 19) | soft_threshold | 0.9409 | continue |
| maze | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 6.712 | 2.579 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 6.304 | 3.335 | True | 2.921041186709772e-11 | (5, 7) | soft_threshold | 0.5747 | continue |
| maze | 0.05 | 1 | 3 | 6 | 0.0 | 0 | 13.62 | 5.634 | True | 2.921041186709772e-11 | (7, 18) | soft_threshold | 1.034 | continue |
| maze | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 21.04 | 4.656 | True | 2.921041186709772e-11 | (7, 17) | soft_threshold | 1.968 | continue |
| maze | 0.05 | 3 | 5 | 20 | 0.0 | 0 | 21.9 | 3.793 | True | 2.319922032256727e-11 | (7, 9) | soft_threshold | 2.513 | continue |
| maze | 0.05 | 4 | 6 | 30 | 0.0 | 0 | 22.72 | 3.385 | True | 2.3302249019252486e-11 | (7, 16) | soft_threshold | 2.858 | continue |
| maze | 0.05 | 5 | 7 | 42 | 0.0 | 0 | 20.69 | 2.862 | True | 1.7255530337934033e-11 | None | none | 0.0 | hybrid_threshold |
