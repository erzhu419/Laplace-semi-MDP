# First-Boundary Targeted Split

Generated: 2026-07-04T22:02:55
candidate_kind = turn_articulation, candidate_top_fraction = 0.15
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | feasible | start_gap | description_length_proxy | split_candidate_coord | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | True | 0.0 | 7.9 | None | hidden_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | True | 1.2212453270876722e-11 | 7.887 | None | hidden_threshold |
| four_rooms | 0.0 | 4 | 6 | 10 | 30 | 0 | 0.0 | True | 1.7763568394002505e-15 | 343.5 | None | hidden_threshold |
| four_rooms | 0.05 | 8 | 10 | 10 | 90 | 0 | 0.0 | True | 0.1152 | 954.5 | None | hidden_threshold |
| maze | 0.0 | 20 | 22 | 30 | 446 | 16 | 1 | True | 0.0 | 1.424e+04 | (7, 1) | max_splits |
| maze | 0.05 | 20 | 22 | 30 | 445 | 17 | 0.9997 | True | 0.01151 | 1.379e+04 | (7, 5) | max_splits |
| open_room | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | True | 0.0 | 70.6 | None | hidden_threshold |
| open_room | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | True | 0.0788 | 68.68 | None | hidden_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | feasible | start_gap | split_candidate_coord | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | True | 0.0 | None | 0.0 | hidden_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | True | 1.2212453270876722e-11 | None | 0.0 | hidden_threshold |
| open_room | 0.0 | 0 | 2 | 0 | 1 | 2 | False | inf | (1, 7) | 1 | continue |
| open_room | 0.0 | 1 | 3 | 5 | 1 | 1 | True | 0.0 | (5, 1) | 1 | continue |
| open_room | 0.0 | 2 | 4 | 12 | 0.0 | 0 | True | 0.0 | None | 0.0 | hidden_threshold |
| open_room | 0.05 | 0 | 2 | 0 | 0.9358 | 2 | False | inf | (1, 7) | 0.9358 | continue |
| open_room | 0.05 | 1 | 3 | 5 | 0.9358 | 1 | True | 0.183 | (5, 1) | 0.9358 | continue |
| open_room | 0.05 | 2 | 4 | 12 | 0.0 | 0 | True | 0.0788 | None | 0.0 | hidden_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | False | inf | (3, 7) | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 2 | 1 | 4 | False | inf | (3, 5) | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 10 | 1 | 2 | True | 21.76 | (1, 5) | 1 | continue |
| four_rooms | 0.0 | 3 | 5 | 19 | 1 | 1 | True | 21.76 | (5, 7) | 1 | continue |
| four_rooms | 0.0 | 4 | 6 | 30 | 0.0 | 0 | True | 1.7763568394002505e-15 | None | 0.0 | hidden_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | False | inf | (3, 7) | 0.9997 | continue |
| four_rooms | 0.05 | 1 | 3 | 0 | 1 | 6 | False | inf | (3, 5) | 2.999 | continue |
| four_rooms | 0.05 | 2 | 4 | 0 | 0.9664 | 12 | False | inf | (5, 7) | 0.9667 | continue |
| four_rooms | 0.05 | 3 | 5 | 5 | 0.9664 | 15 | False | inf | (1, 5) | 0.9661 | continue |
| four_rooms | 0.05 | 4 | 6 | 12 | 0.0003136 | 18 | False | inf | (5, 5) | 0.001503 | continue |
| four_rooms | 0.05 | 5 | 7 | 24 | 0.9358 | 18 | False | inf | (5, 1) | 0.9371 | continue |
| four_rooms | 0.05 | 6 | 8 | 43 | 0.0003136 | 13 | False | inf | (1, 7) | 0.002108 | continue |
| four_rooms | 0.05 | 7 | 9 | 63 | 0.9358 | 9 | True | 0.1152 | (1, 11) | 0.9377 | continue |
| four_rooms | 0.05 | 8 | 10 | 90 | 0.0 | 0 | True | 0.1152 | None | 0.0 | hidden_threshold |
| maze | 0.0 | 0 | 2 | 0 | 1 | 2 | False | inf | (5, 19) | 1 | continue |
| maze | 0.0 | 1 | 3 | 3 | 1 | 3 | False | inf | (5, 17) | 1 | continue |
| maze | 0.0 | 2 | 4 | 8 | 1 | 4 | False | inf | (1, 5) | 2 | continue |
| maze | 0.0 | 3 | 5 | 14 | 1 | 6 | True | 11.13 | (3, 5) | 3 | continue |
| maze | 0.0 | 4 | 6 | 23 | 1 | 7 | True | 11.13 | (3, 17) | 3 | continue |
| maze | 0.0 | 5 | 7 | 34 | 1 | 8 | True | 11.13 | (3, 7) | 4 | continue |
| maze | 0.0 | 6 | 8 | 47 | 1 | 9 | True | 11.13 | (3, 19) | 4 | continue |
| maze | 0.0 | 7 | 9 | 62 | 1 | 10 | True | 11.13 | (1, 7) | 5 | continue |
| maze | 0.0 | 8 | 10 | 79 | 1 | 11 | True | 11.13 | (1, 19) | 5 | continue |
| maze | 0.0 | 9 | 11 | 98 | 1 | 12 | True | 11.13 | (1, 13) | 6 | continue |
| maze | 0.0 | 10 | 12 | 119 | 1 | 13 | True | 11.13 | (1, 15) | 6 | continue |
| maze | 0.0 | 11 | 13 | 142 | 1 | 14 | True | 11.13 | (3, 13) | 7 | continue |
| maze | 0.0 | 12 | 14 | 167 | 1 | 15 | True | 11.13 | (3, 15) | 14 | continue |
| maze | 0.0 | 13 | 15 | 209 | 1 | 1 | True | 0.0 | (3, 1) | 1 | continue |
| maze | 0.0 | 14 | 16 | 238 | 1 | 2 | True | 0.0 | (7, 15) | 1 | continue |
| maze | 0.0 | 15 | 17 | 267 | 1 | 5 | True | 0.0 | (5, 15) | 3 | continue |
| maze | 0.0 | 16 | 18 | 300 | 1 | 6 | True | 0.0 | (7, 13) | 3 | continue |
| maze | 0.0 | 17 | 19 | 333 | 1 | 9 | True | 0.0 | (7, 7) | 5 | continue |
| maze | 0.0 | 18 | 20 | 368 | 1 | 12 | True | 0.0 | (5, 5) | 7 | continue |
| maze | 0.0 | 19 | 21 | 405 | 1 | 15 | True | 0.0 | (7, 5) | 9 | continue |
| maze | 0.0 | 20 | 22 | 446 | 1 | 16 | True | 0.0 | (7, 1) | 9 | max_splits |
| maze | 0.05 | 0 | 2 | 0 | 1 | 2 | False | inf | (5, 19) | 0.9828 | continue |
| maze | 0.05 | 1 | 3 | 1 | 1 | 5 | False | inf | (5, 17) | 1 | continue |
| maze | 0.05 | 2 | 4 | 5 | 1 | 7 | False | inf | (1, 5) | 1.999 | continue |
| maze | 0.05 | 3 | 5 | 7 | 1 | 13 | False | inf | (3, 5) | 3 | continue |
| maze | 0.05 | 4 | 6 | 14 | 0.9997 | 16 | False | inf | (3, 17) | 3 | continue |
| maze | 0.05 | 5 | 7 | 23 | 0.9997 | 19 | False | inf | (3, 7) | 3.999 | continue |
| maze | 0.05 | 6 | 8 | 34 | 0.9997 | 22 | False | inf | (3, 19) | 4 | continue |
| maze | 0.05 | 7 | 9 | 47 | 0.9997 | 25 | False | inf | (1, 7) | 4.999 | continue |
| maze | 0.05 | 8 | 10 | 66 | 0.9997 | 24 | False | inf | (1, 19) | 5 | continue |
| maze | 0.05 | 9 | 11 | 88 | 0.9997 | 22 | False | inf | (1, 13) | 5.998 | continue |
| maze | 0.05 | 10 | 12 | 103 | 1 | 29 | False | inf | (3, 13) | 6.002 | continue |
| maze | 0.05 | 11 | 13 | 124 | 0.9997 | 32 | False | inf | (1, 15) | 6.998 | continue |
| maze | 0.05 | 12 | 14 | 142 | 1 | 40 | False | inf | (3, 15) | 14 | continue |
| maze | 0.05 | 13 | 15 | 195 | 0.9828 | 15 | False | inf | (3, 1) | 0.9868 | continue |
| maze | 0.05 | 14 | 16 | 223 | 0.9997 | 17 | False | inf | (3, 3) | 1.021 | continue |
| maze | 0.05 | 15 | 17 | 253 | 0.9997 | 19 | False | inf | (5, 3) | 2.986 | continue |
| maze | 0.05 | 16 | 18 | 285 | 0.9997 | 21 | False | inf | (5, 1) | 3.02 | continue |
| maze | 0.05 | 17 | 19 | 319 | 0.9997 | 23 | False | inf | (7, 1) | 4.986 | continue |
| maze | 0.05 | 18 | 20 | 368 | 0.9997 | 12 | True | 0.01151 | (7, 15) | 5.016 | continue |
| maze | 0.05 | 19 | 21 | 393 | 1 | 27 | False | inf | (5, 15) | 6.987 | continue |
| maze | 0.05 | 20 | 22 | 445 | 0.9997 | 17 | True | 0.01151 | (7, 5) | 7.015 | max_splits |
