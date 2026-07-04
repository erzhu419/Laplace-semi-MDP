# First-Boundary Targeted Split

Generated: 2026-07-04T22:15:54
candidate_kind = turn_articulation, candidate_top_fraction = 0.15
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | (1, 10) | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | (1, 10) | True | 1.2212453270876722e-11 | 9.705 | None | none | hybrid_threshold |
| open_room | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 7.365 | 1.883 | (4, 7) | True | 0.0 | 77.97 | None | none | hybrid_threshold |
| open_room | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 8.263 | 3.935 | (5, 6) | True | 0.0788 | 76.94 | None | none | hybrid_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | soft_cost_valid_total | soft_cost_max | feasible | start_gap | split_candidate_coord | split_candidate_source | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | 1.73 | 0.97 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | 1.818 | 1.034 | True | 1.2212453270876722e-11 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.97 | False | inf | (1, 7) | hard_hidden | 1 | continue |
| open_room | 0.0 | 1 | 3 | 5 | 1 | 1 | 2.853 | 0.97 | True | 0.0 | (5, 1) | hard_hidden | 1 | continue |
| open_room | 0.0 | 2 | 4 | 12 | 0.0 | 0 | 7.365 | 1.883 | True | 0.0 | None | none | 0.0 | hybrid_threshold |
| open_room | 0.05 | 0 | 2 | 0 | 0.9358 | 2 | 0.0 | 0.2145 | False | inf | (1, 7) | hard_hidden | 0.9358 | continue |
| open_room | 0.05 | 1 | 3 | 5 | 0.9358 | 1 | 0.09808 | 0.2145 | True | 0.183 | (5, 1) | hard_hidden | 0.9358 | continue |
| open_room | 0.05 | 2 | 4 | 12 | 0.0 | 0 | 8.263 | 3.935 | True | 0.0788 | None | none | 0.0 | hybrid_threshold |
