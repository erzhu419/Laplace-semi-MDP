# First-Boundary Targeted Split

Generated: 2026-07-04T22:25:41
candidate_kind = turn_articulation, candidate_top_fraction = 0.15
soft_kind = combined, soft_top_fraction = 0.15, soft_split_policy = never
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0
soft_threshold = 1e-06, soft_cost_weight = 1.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | soft_cost_valid_total | soft_cost_max | soft_split_candidate_coord | feasible | start_gap | description_length_proxy | split_candidate_coord | split_candidate_source | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.73 | 0.97 | (1, 10) | True | 0.0 | 9.63 | None | none | hybrid_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | 1.818 | 1.034 | (1, 10) | True | 1.2212453270876722e-11 | 9.705 | None | none | hybrid_threshold |
| four_rooms | 0.0 | 4 | 6 | 10 | 30 | 0 | 0.0 | 7.36 | 1.233 | (4, 11) | True | 1.7763568394002505e-15 | 110.1 | None | none | hybrid_threshold |
| four_rooms | 0.05 | 8 | 10 | 10 | 90 | 0 | 0.0 | 12.4 | 1.965 | (4, 11) | True | 0.1152 | 219.3 | None | none | hybrid_threshold |
| maze | 0.0 | 24 | 26 | 30 | 650 | 0 | 0.0 | 157.5 | 2.741 | (6, 19) | True | 3.552713678800501e-15 | 1663 | None | none | hybrid_threshold |
| maze | 0.05 | 28 | 30 | 30 | 870 | 0 | 0.0 | 293.1 | 2.912 | (5, 7) | True | 2.901501261476369e-11 | 2130 | None | none | hybrid_threshold |
| open_room | 0.0 | 2 | 4 | 4 | 12 | 0 | 0.0 | 7.365 | 1.883 | (4, 7) | True | 0.0 | 43.97 | None | none | hybrid_threshold |
| open_room | 0.05 | 2 | 4 | 4 | 12 | 0 | 0.0 | 8.263 | 3.935 | (5, 6) | True | 0.0788 | 44.22 | None | none | hybrid_threshold |

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
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.233 | False | inf | (3, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 2 | 1 | 4 | 2.466 | 1.233 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 10 | 1 | 2 | 3.699 | 1.233 | True | 21.76 | (1, 5) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 3 | 5 | 19 | 1 | 1 | 4.932 | 1.233 | True | 21.76 | (5, 7) | hard_hidden | 1 | continue |
| four_rooms | 0.0 | 4 | 6 | 30 | 0.0 | 0 | 7.36 | 1.233 | True | 1.7763568394002505e-15 | None | none | 0.0 | hybrid_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.6677 | False | inf | (3, 7) | hard_hidden | 0.9997 | continue |
| four_rooms | 0.05 | 1 | 3 | 0 | 1 | 6 | 0.0 | 0.6677 | False | inf | (3, 5) | hard_hidden | 2.999 | continue |
| four_rooms | 0.05 | 2 | 4 | 0 | 0.9664 | 12 | 0.0 | 0.6677 | False | inf | (5, 7) | hard_hidden | 0.9667 | continue |
| four_rooms | 0.05 | 3 | 5 | 5 | 0.9664 | 15 | 3.954 | 1.965 | False | inf | (1, 5) | hard_hidden | 0.9661 | continue |
| four_rooms | 0.05 | 4 | 6 | 12 | 0.0003136 | 18 | 3.966 | 1.965 | False | inf | (5, 5) | hard_hidden | 0.001503 | continue |
| four_rooms | 0.05 | 5 | 7 | 24 | 0.9358 | 18 | 3.978 | 1.965 | False | inf | (5, 1) | hard_hidden | 0.9371 | continue |
| four_rooms | 0.05 | 6 | 8 | 43 | 0.0003136 | 13 | 5.472 | 1.965 | False | inf | (1, 7) | hard_hidden | 0.002108 | continue |
| four_rooms | 0.05 | 7 | 9 | 63 | 0.9358 | 9 | 5.641 | 1.965 | True | 0.1152 | (1, 11) | hard_hidden | 0.9377 | continue |
| four_rooms | 0.05 | 8 | 10 | 90 | 0.0 | 0 | 12.4 | 1.965 | True | 0.1152 | None | none | 0.0 | hybrid_threshold |
| maze | 0.0 | 0 | 2 | 0 | 1 | 2 | 0.0 | 0.97 | False | inf | (5, 19) | hard_hidden | 1 | continue |
| maze | 0.0 | 1 | 3 | 3 | 1 | 3 | 2.91 | 0.97 | False | inf | (5, 17) | hard_hidden | 1 | continue |
| maze | 0.0 | 2 | 4 | 8 | 1 | 4 | 7.531 | 0.97 | False | inf | (1, 5) | hard_hidden | 2 | continue |
| maze | 0.0 | 3 | 5 | 14 | 1 | 6 | 9.413 | 0.97 | True | 11.13 | (3, 5) | hard_hidden | 3 | continue |
| maze | 0.0 | 4 | 6 | 23 | 1 | 7 | 11.3 | 0.97 | True | 11.13 | (3, 17) | hard_hidden | 3 | continue |
| maze | 0.0 | 5 | 7 | 34 | 1 | 8 | 19.19 | 0.97 | True | 11.13 | (3, 7) | hard_hidden | 4 | continue |
| maze | 0.0 | 6 | 8 | 47 | 1 | 9 | 21.93 | 0.97 | True | 11.13 | (3, 19) | hard_hidden | 4 | continue |
| maze | 0.0 | 7 | 9 | 62 | 1 | 10 | 24.67 | 0.97 | True | 11.13 | (1, 7) | hard_hidden | 5 | continue |
| maze | 0.0 | 8 | 10 | 79 | 1 | 11 | 27.41 | 0.97 | True | 11.13 | (1, 19) | hard_hidden | 5 | continue |
| maze | 0.0 | 9 | 11 | 98 | 1 | 12 | 30.16 | 0.97 | True | 11.13 | (1, 13) | hard_hidden | 6 | continue |
| maze | 0.0 | 10 | 12 | 119 | 1 | 13 | 32.9 | 0.97 | True | 11.13 | (1, 15) | hard_hidden | 6 | continue |
| maze | 0.0 | 11 | 13 | 142 | 1 | 14 | 35.64 | 0.97 | True | 11.13 | (3, 13) | hard_hidden | 7 | continue |
| maze | 0.0 | 12 | 14 | 167 | 1 | 15 | 38.38 | 0.97 | True | 11.13 | (3, 15) | hard_hidden | 14 | continue |
| maze | 0.0 | 13 | 15 | 209 | 1 | 1 | 41.12 | 0.97 | True | 0.0 | (3, 1) | hard_hidden | 1 | continue |
| maze | 0.0 | 14 | 16 | 238 | 1 | 2 | 42.95 | 2.741 | True | 0.0 | (7, 15) | hard_hidden | 1 | continue |
| maze | 0.0 | 15 | 17 | 267 | 1 | 5 | 86.77 | 2.741 | True | 0.0 | (5, 15) | hard_hidden | 3 | continue |
| maze | 0.0 | 16 | 18 | 300 | 1 | 6 | 107.7 | 2.741 | True | 0.0 | (7, 13) | hard_hidden | 3 | continue |
| maze | 0.0 | 17 | 19 | 333 | 1 | 9 | 114 | 2.741 | True | 0.0 | (7, 7) | hard_hidden | 5 | continue |
| maze | 0.0 | 18 | 20 | 368 | 1 | 12 | 120.4 | 2.741 | True | 0.0 | (5, 5) | hard_hidden | 7 | continue |
| maze | 0.0 | 19 | 21 | 405 | 1 | 15 | 126.7 | 2.741 | True | 0.0 | (7, 5) | hard_hidden | 9 | continue |
| maze | 0.0 | 20 | 22 | 446 | 1 | 16 | 133.1 | 2.741 | True | 0.0 | (7, 1) | hard_hidden | 9 | continue |
| maze | 0.0 | 21 | 23 | 487 | 1 | 19 | 139.4 | 2.741 | True | 0.0 | (5, 1) | hard_hidden | 11 | continue |
| maze | 0.0 | 22 | 24 | 532 | 1 | 20 | 145.8 | 2.741 | True | 0.0 | (5, 3) | hard_hidden | 11 | continue |
| maze | 0.0 | 23 | 25 | 577 | 1 | 23 | 152.1 | 2.741 | True | 0.0 | (3, 3) | hard_hidden | 23 | continue |
| maze | 0.0 | 24 | 26 | 650 | 0.0 | 0 | 157.5 | 2.741 | True | 3.552713678800501e-15 | None | none | 0.0 | hybrid_threshold |
| maze | 0.05 | 0 | 2 | 0 | 1 | 2 | 0.0 | 1.05 | False | inf | (5, 19) | hard_hidden | 0.9828 | continue |
| maze | 0.05 | 1 | 3 | 1 | 1 | 5 | 1.035 | 1.05 | False | inf | (5, 17) | hard_hidden | 1 | continue |
| maze | 0.05 | 2 | 4 | 5 | 1 | 7 | 5.044 | 1.05 | False | inf | (1, 5) | hard_hidden | 1.999 | continue |
| maze | 0.05 | 3 | 5 | 7 | 1 | 13 | 7.049 | 1.05 | False | inf | (3, 5) | hard_hidden | 3 | continue |
| maze | 0.05 | 4 | 6 | 14 | 0.9997 | 16 | 9.054 | 1.05 | False | inf | (3, 17) | hard_hidden | 3 | continue |
| maze | 0.05 | 5 | 7 | 23 | 0.9997 | 19 | 13.03 | 1.05 | False | inf | (3, 7) | hard_hidden | 3.999 | continue |
| maze | 0.05 | 6 | 8 | 34 | 0.9997 | 22 | 15.05 | 1.05 | False | inf | (3, 19) | hard_hidden | 4 | continue |
| maze | 0.05 | 7 | 9 | 47 | 0.9997 | 25 | 17.08 | 1.05 | False | inf | (1, 7) | hard_hidden | 4.999 | continue |
| maze | 0.05 | 8 | 10 | 66 | 0.9997 | 24 | 19.1 | 1.05 | False | inf | (1, 19) | hard_hidden | 5 | continue |
| maze | 0.05 | 9 | 11 | 88 | 0.9997 | 22 | 21.12 | 1.05 | False | inf | (1, 13) | hard_hidden | 5.998 | continue |
| maze | 0.05 | 10 | 12 | 103 | 1 | 29 | 23.14 | 1.05 | False | inf | (3, 13) | hard_hidden | 6.002 | continue |
| maze | 0.05 | 11 | 13 | 124 | 0.9997 | 32 | 25.16 | 1.05 | False | inf | (1, 15) | hard_hidden | 6.998 | continue |
| maze | 0.05 | 12 | 14 | 142 | 1 | 40 | 27.19 | 1.05 | False | inf | (3, 15) | hard_hidden | 14 | continue |
| maze | 0.05 | 13 | 15 | 195 | 0.9828 | 15 | 29.21 | 1.05 | False | inf | (3, 1) | hard_hidden | 0.9868 | continue |
| maze | 0.05 | 14 | 16 | 223 | 0.9997 | 17 | 30.24 | 2.912 | False | inf | (3, 3) | hard_hidden | 1.021 | continue |
| maze | 0.05 | 15 | 17 | 253 | 0.9997 | 19 | 31.29 | 2.912 | False | inf | (5, 3) | hard_hidden | 2.986 | continue |
| maze | 0.05 | 16 | 18 | 285 | 0.9997 | 21 | 33.28 | 2.912 | False | inf | (5, 1) | hard_hidden | 3.02 | continue |
| maze | 0.05 | 17 | 19 | 319 | 0.9997 | 23 | 35.26 | 2.912 | False | inf | (7, 1) | hard_hidden | 4.986 | continue |
| maze | 0.05 | 18 | 20 | 368 | 0.9997 | 12 | 37.25 | 2.912 | True | 0.01151 | (7, 15) | hard_hidden | 5.016 | continue |
| maze | 0.05 | 19 | 21 | 393 | 1 | 27 | 57.75 | 2.912 | False | inf | (5, 15) | hard_hidden | 6.987 | continue |
| maze | 0.05 | 20 | 22 | 445 | 0.9997 | 17 | 100.4 | 2.912 | True | 0.01151 | (7, 5) | hard_hidden | 7.015 | continue |
| maze | 0.05 | 21 | 23 | 474 | 1 | 32 | 105.3 | 2.912 | False | inf | (5, 5) | hard_hidden | 8.987 | continue |
| maze | 0.05 | 22 | 24 | 530 | 0.9997 | 22 | 110.2 | 2.912 | True | 0.01151 | (7, 7) | hard_hidden | 8.859 | continue |
| maze | 0.05 | 23 | 25 | 552 | 1 | 48 | 115.1 | 2.912 | False | inf | (7, 13) | hard_hidden | 20.88 | continue |
| maze | 0.05 | 24 | 26 | 576 | 0.01724 | 74 | 125.3 | 2.912 | True | 0.01151 | (5, 11) | hard_hidden | 0.1601 | continue |
| maze | 0.05 | 25 | 27 | 637 | 0.9997 | 65 | 185.7 | 2.912 | False | inf | (3, 11) | hard_hidden | 12.97 | continue |
| maze | 0.05 | 26 | 28 | 688 | 0.9997 | 68 | 205.7 | 2.912 | False | inf | (3, 9) | hard_hidden | 13 | continue |
| maze | 0.05 | 27 | 29 | 741 | 0.9997 | 71 | 212.6 | 2.912 | False | inf | (5, 9) | hard_hidden | 19.14 | continue |
| maze | 0.05 | 28 | 30 | 870 | 0.0 | 0 | 293.1 | 2.912 | True | 2.901501261476369e-11 | None | none | 0.0 | hybrid_threshold |
