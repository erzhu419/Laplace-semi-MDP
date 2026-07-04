# First-Boundary Targeted Split

Generated: 2026-07-04T21:59:25
candidate_kind = bottleneck, candidate_top_fraction = 0.15
gamma = 0.97, slips = [0.0, 0.05], hidden_threshold = 1e-06, local_horizon = 999.0

## Final Rows

| map | slip | step | n_boundary | n_candidate_boundary | n_edges_valid | invalid_hidden_count | hidden_mass_max | feasible | start_gap | description_length_proxy | split_candidate_coord | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 2 | 0 | 0.0 | True | 0.0 | 7.9 | None | hidden_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 2 | 0 | 0.0 | True | 1.2212453270876722e-11 | 7.887 | None | hidden_threshold |
| four_rooms | 0.0 | 4 | 6 | 10 | 30 | 0 | 0.0 | True | 1.7763568394002505e-15 | 364 | None | hidden_threshold |
| four_rooms | 0.05 | 8 | 10 | 10 | 90 | 0 | 0.0 | True | 0.1152 | 1041 | None | hidden_threshold |
| maze | 0.0 | 11 | 13 | 13 | 156 | 0 | 0.0 | True | 0.0 | 4830 | None | hidden_threshold |
| maze | 0.05 | 11 | 13 | 13 | 156 | 0 | 0.0 | True | 2.914291030720051e-11 | 4697 | None | hidden_threshold |
| open_room | 0.0 | 5 | 7 | 7 | 42 | 0 | 0.0 | True | 0.0 | 265.3 | None | hidden_threshold |
| open_room | 0.05 | 5 | 7 | 7 | 42 | 0 | 0.0 | True | 0.0788 | 258.3 | None | hidden_threshold |

## Split Trace

| map | slip | step | n_boundary | n_edges_valid | hidden_mass_max | invalid_hidden_count | feasible | start_gap | split_candidate_coord | split_candidate_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0 | 0 | 2 | 2 | 0.0 | 0 | True | 0.0 | None | 0.0 | hidden_threshold |
| corridor | 0.05 | 0 | 2 | 2 | 0.0 | 0 | True | 1.2212453270876722e-11 | None | 0.0 | hidden_threshold |
| open_room | 0.0 | 0 | 2 | 0 | 1 | 2 | False | inf | (1, 4) | 1 | continue |
| open_room | 0.0 | 1 | 3 | 2 | 1 | 4 | False | inf | (1, 3) | 2 | continue |
| open_room | 0.0 | 2 | 4 | 9 | 1 | 3 | True | 24.58 | (5, 3) | 2 | continue |
| open_room | 0.0 | 3 | 5 | 16 | 1 | 4 | True | 24.58 | (5, 4) | 3 | continue |
| open_room | 0.0 | 4 | 6 | 27 | 1 | 3 | True | 24.58 | (5, 5) | 3 | continue |
| open_room | 0.0 | 5 | 7 | 42 | 0.0 | 0 | True | 0.0 | None | 0.0 | hidden_threshold |
| open_room | 0.05 | 0 | 2 | 0 | 1 | 2 | False | inf | (1, 4) | 0.9997 | continue |
| open_room | 0.05 | 1 | 3 | 0 | 1 | 6 | False | inf | (1, 3) | 2 | continue |
| open_room | 0.05 | 2 | 4 | 6 | 0.9997 | 6 | True | 24.14 | (5, 3) | 1.936 | continue |
| open_room | 0.05 | 3 | 5 | 6 | 1 | 14 | False | inf | (5, 4) | 2.889 | continue |
| open_room | 0.05 | 4 | 6 | 6 | 1 | 24 | False | inf | (5, 5) | 3.243 | continue |
| open_room | 0.05 | 5 | 7 | 42 | 0.0 | 0 | True | 0.0788 | None | 0.0 | hidden_threshold |
| four_rooms | 0.0 | 0 | 2 | 0 | 1 | 2 | False | inf | (3, 7) | 1 | continue |
| four_rooms | 0.0 | 1 | 3 | 2 | 1 | 4 | False | inf | (3, 5) | 3 | continue |
| four_rooms | 0.0 | 2 | 4 | 10 | 1 | 2 | True | 21.76 | (2, 5) | 1 | continue |
| four_rooms | 0.0 | 3 | 5 | 19 | 1 | 1 | True | 21.76 | (4, 7) | 1 | continue |
| four_rooms | 0.0 | 4 | 6 | 30 | 0.0 | 0 | True | 1.7763568394002505e-15 | None | 0.0 | hidden_threshold |
| four_rooms | 0.05 | 0 | 2 | 0 | 1 | 2 | False | inf | (3, 5) | 0.9991 | continue |
| four_rooms | 0.05 | 1 | 3 | 0 | 1 | 6 | False | inf | (3, 7) | 2.964 | continue |
| four_rooms | 0.05 | 2 | 4 | 0 | 0.9833 | 12 | False | inf | (2, 5) | 1.001 | continue |
| four_rooms | 0.05 | 3 | 5 | 1 | 0.9833 | 19 | False | inf | (4, 7) | 1.018 | continue |
| four_rooms | 0.05 | 4 | 6 | 2 | 0.01724 | 28 | False | inf | (2, 7) | 0.08565 | continue |
| four_rooms | 0.05 | 5 | 7 | 11 | 0.01813 | 31 | False | inf | (4, 5) | 0.1029 | continue |
| four_rooms | 0.05 | 6 | 8 | 24 | 0.01813 | 32 | False | inf | (1, 9) | 0.01987 | continue |
| four_rooms | 0.05 | 7 | 9 | 54 | 0.01813 | 18 | False | inf | (5, 3) | 0.0202 | continue |
| four_rooms | 0.05 | 8 | 10 | 90 | 0.0 | 0 | True | 0.1152 | None | 0.0 | hidden_threshold |
| maze | 0.0 | 0 | 2 | 0 | 1 | 2 | False | inf | (5, 19) | 1 | continue |
| maze | 0.0 | 1 | 3 | 3 | 1 | 3 | False | inf | (5, 17) | 2 | continue |
| maze | 0.0 | 2 | 4 | 11 | 1 | 1 | True | 0.0 | (5, 3) | 1 | continue |
| maze | 0.0 | 3 | 5 | 16 | 1 | 4 | True | 0.0 | (5, 1) | 3 | continue |
| maze | 0.0 | 4 | 6 | 25 | 1 | 5 | True | 0.0 | (7, 1) | 3 | continue |
| maze | 0.0 | 5 | 7 | 36 | 1 | 6 | True | 0.0 | (7, 15) | 3 | continue |
| maze | 0.0 | 6 | 8 | 48 | 1 | 8 | True | 0.0 | (5, 15) | 4 | continue |
| maze | 0.0 | 7 | 9 | 63 | 1 | 9 | True | 0.0 | (7, 5) | 5 | continue |
| maze | 0.0 | 8 | 10 | 80 | 1 | 10 | True | 0.0 | (5, 13) | 5 | continue |
| maze | 0.0 | 9 | 11 | 99 | 1 | 11 | True | 0.0 | (5, 5) | 6 | continue |
| maze | 0.0 | 10 | 12 | 120 | 1 | 12 | True | 0.0 | (5, 7) | 12 | continue |
| maze | 0.0 | 11 | 13 | 156 | 0.0 | 0 | True | 0.0 | None | 0.0 | hidden_threshold |
| maze | 0.05 | 0 | 2 | 0 | 1 | 2 | False | inf | (5, 19) | 0.9828 | continue |
| maze | 0.05 | 1 | 3 | 1 | 1 | 5 | False | inf | (5, 17) | 2 | continue |
| maze | 0.05 | 2 | 4 | 9 | 0.9828 | 3 | True | 0.01151 | (5, 3) | 0.9828 | continue |
| maze | 0.05 | 3 | 5 | 14 | 1 | 6 | False | inf | (5, 1) | 3 | continue |
| maze | 0.05 | 4 | 6 | 22 | 0.9997 | 8 | False | inf | (7, 1) | 3 | continue |
| maze | 0.05 | 5 | 7 | 35 | 0.9997 | 7 | True | 0.01151 | (7, 15) | 3.016 | continue |
| maze | 0.05 | 6 | 8 | 45 | 1 | 11 | False | inf | (5, 15) | 4.001 | continue |
| maze | 0.05 | 7 | 9 | 59 | 0.9997 | 13 | False | inf | (7, 5) | 4.998 | continue |
| maze | 0.05 | 8 | 10 | 72 | 1 | 18 | False | inf | (5, 5) | 5.001 | continue |
| maze | 0.05 | 9 | 11 | 90 | 0.9997 | 20 | False | inf | (5, 13) | 5.999 | continue |
| maze | 0.05 | 10 | 12 | 115 | 0.9997 | 17 | False | inf | (5, 7) | 12 | continue |
| maze | 0.05 | 11 | 13 | 156 | 0.0 | 0 | True | 2.914291030720051e-11 | None | 0.0 | hidden_threshold |
