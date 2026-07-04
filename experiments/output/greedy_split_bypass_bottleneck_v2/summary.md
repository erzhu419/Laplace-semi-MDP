# Greedy Split On Bypass

Generated: 2026-07-04T19:45:35
option_set = targeted, critical_kind = bottleneck, critical_top_fraction = 0.15
gamma = 0.97, slips = [0.0, 0.05], max_splits = 12, bypass_threshold = 1e-06
split_strategy = bypass_attribution, policy_cost_mode = total, candidate_limit = 50
objective = 100.0*start_gap + 10.0*value_gap + 100.0*bypass + 0.2*policy + 1.0*graph + 1.0*option + 0.1*nonlocal

## Final Rows

| map | slip | step | n_boundary | start_gap | bypass_cost_total | split_objective | objective_delta | description_length_proxy | policy_tv_total | candidate_split_coord | selected_split_state | selected_split_coord | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.0e+00 | 6.06 | 0.0e+00 | 8.3 | 4 | None | None | None | bypass_threshold |
| corridor | 0.05 | 0 | 2 | 1.2e-11 | 0.0e+00 | 7.031 | 0.0e+00 | 9.26 | 3.933 | None | None | None | bypass_threshold |
| four_rooms | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.0e+00 | 31.36 | 0.0e+00 | 82.8 | 234 | None | None | None | bypass_threshold |
| four_rooms | 0.05 | 8 | 10 | 0.1152 | 0.0e+00 | 91.38 | 0.0e+00 | 161.1 | 365.1 | None | None | None | bypass_threshold |
| maze | 0.0e+00 | 11 | 13 | 0.0e+00 | 0.0e+00 | 133 | 0.0e+00 | 442.4 | 874 | None | None | None | bypass_threshold |
| maze | 0.05 | 11 | 13 | 2.6e-11 | 0.0e+00 | 149.1 | 0.0e+00 | 449.7 | 818.5 | None | None | None | bypass_threshold |
| open_room | 0.0e+00 | 5 | 7 | 0.0e+00 | 0.0e+00 | 29.04 | 0.0e+00 | 56.8 | 116 | None | None | None | bypass_threshold |
| open_room | 0.05 | 5 | 7 | 0.0788 | 0.0e+00 | 55.38 | 0.0e+00 | 73.49 | 110.2 | None | None | None | bypass_threshold |

## Split Trace

| map | slip | step | n_boundary | start_gap | bypass_cost_total | split_objective | objective_delta | candidate_split_coord | selected_split_state | selected_split_coord | selected_split_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.0e+00 | 6.06 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| corridor | 0.05 | 0 | 2 | 1.2e-11 | 0.0e+00 | 7.031 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| open_room | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.2875 | 35.95 | 0.0e+00 | (1, 4) | 3 | (1, 4) | 0.06112 | continue |
| open_room | 0.0e+00 | 1 | 3 | 0.0e+00 | 0.43 | 54.14 | 0.0e+00 | (1, 3) | 2 | (1, 3) | 0.1315 | continue |
| open_room | 0.0e+00 | 2 | 4 | 0.0e+00 | 0.4817 | 63.55 | 0.0e+00 | (5, 4) | 31 | (5, 4) | 0.193 | continue |
| open_room | 0.0e+00 | 3 | 5 | 0.0e+00 | 0.3681 | 56.51 | 0.0e+00 | (5, 3) | 30 | (5, 3) | 0.2365 | continue |
| open_room | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.1963 | 43.95 | 0.0e+00 | (5, 5) | 32 | (5, 5) | 0.1963 | continue |
| open_room | 0.0e+00 | 5 | 7 | 0.0e+00 | 0.0e+00 | 29.04 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| open_room | 0.05 | 0 | 2 | 0.0788 | 0.2881 | 45.6 | 0.0e+00 | (5, 4) | 31 | (5, 4) | 0.06129 | continue |
| open_room | 0.05 | 1 | 3 | 0.0788 | 0.4867 | 70.55 | 0.0e+00 | (5, 5) | 32 | (5, 5) | 0.1311 | continue |
| open_room | 0.05 | 2 | 4 | 0.0788 | 0.534 | 82.16 | 0.0e+00 | (1, 4) | 3 | (1, 4) | 0.1897 | continue |
| open_room | 0.05 | 3 | 5 | 0.0788 | 0.3269 | 68.87 | 0.0e+00 | (5, 3) | 30 | (5, 3) | 0.1859 | continue |
| open_room | 0.05 | 4 | 6 | 0.0788 | 0.2515 | 69.62 | 0.0e+00 | (1, 3) | 2 | (1, 3) | 0.2515 | continue |
| open_room | 0.05 | 5 | 7 | 0.0788 | 0.0e+00 | 55.38 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| four_rooms | 0.0e+00 | 0 | 2 | 0.0e+00 | 5.094 | 519.4 | 0.0e+00 | (3, 5) | 24 | (3, 5) | 2.469 | continue |
| four_rooms | 0.0e+00 | 1 | 3 | 1.8e-15 | 4.174 | 431.7 | 0.0e+00 | (3, 7) | 26 | (3, 7) | 3.981 | continue |
| four_rooms | 0.0e+00 | 2 | 4 | 1.8e-15 | 0.1995 | 39.85 | 0.0e+00 | (2, 5) | 14 | (2, 5) | 0.09975 | continue |
| four_rooms | 0.0e+00 | 3 | 5 | 1.8e-15 | 0.09975 | 35.56 | 0.0e+00 | (4, 7) | 36 | (4, 7) | 0.09975 | continue |
| four_rooms | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.0e+00 | 31.36 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| four_rooms | 0.05 | 0 | 2 | 0.1152 | 5.046 | 528.1 | 0.0e+00 | (3, 5) | 24 | (3, 5) | 2.444 | continue |
| four_rooms | 0.05 | 1 | 3 | 0.1152 | 4.151 | 443.8 | 0.0e+00 | (3, 7) | 26 | (3, 7) | 3.95 | continue |
| four_rooms | 0.05 | 2 | 4 | 0.1152 | 0.2134 | 57.07 | 0.0e+00 | (2, 5) | 14 | (2, 5) | 0.1015 | continue |
| four_rooms | 0.05 | 3 | 5 | 0.1152 | 0.1172 | 55.72 | 0.0e+00 | (4, 7) | 36 | (4, 7) | 0.1032 | continue |
| four_rooms | 0.05 | 4 | 6 | 0.1152 | 0.01746 | 54.23 | 0.0e+00 | (2, 7) | 15 | (2, 7) | 0.00869 | continue |
| four_rooms | 0.05 | 5 | 7 | 0.1152 | 0.0111 | 62.37 | 0.0e+00 | (4, 5) | 35 | (4, 5) | 0.01043 | continue |
| four_rooms | 0.05 | 6 | 8 | 0.1152 | 0.001248 | 70.27 | 0.0e+00 | (1, 9) | 7 | (1, 9) | 0.0006239 | continue |
| four_rooms | 0.05 | 7 | 9 | 0.1152 | 0.0006345 | 80.67 | 0.0e+00 | (5, 3) | 43 | (5, 3) | 0.0006345 | continue |
| four_rooms | 0.05 | 8 | 10 | 0.1152 | 0.0e+00 | 91.38 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| maze | 0.0e+00 | 0 | 2 | 3.6e-15 | 1.905 | 213 | 0.0e+00 | (5, 19) | 57 | (5, 19) | 0.2376 | continue |
| maze | 0.0e+00 | 1 | 3 | 0.0e+00 | 1.774 | 211.4 | 0.0e+00 | (5, 17) | 55 | (5, 17) | 0.3251 | continue |
| maze | 0.0e+00 | 2 | 4 | 0.0e+00 | 1.449 | 190.2 | 0.0e+00 | (5, 3) | 44 | (5, 3) | 0.2054 | continue |
| maze | 0.0e+00 | 3 | 5 | 0.0e+00 | 5.862 | 646.9 | 0.0e+00 | (5, 1) | 42 | (5, 1) | 0.8204 | continue |
| maze | 0.0e+00 | 4 | 6 | 0.0e+00 | 6.554 | 726.7 | 0.0e+00 | (5, 7) | 47 | (5, 7) | 0.9932 | continue |
| maze | 0.0e+00 | 5 | 7 | 0.0e+00 | 8.701 | 948.4 | 0.0e+00 | (5, 5) | 45 | (5, 5) | 1.645 | continue |
| maze | 0.0e+00 | 6 | 8 | 0.0e+00 | 8.308 | 918.3 | 0.0e+00 | (7, 5) | 68 | (7, 5) | 1.888 | continue |
| maze | 0.0e+00 | 7 | 9 | 7.1e-15 | 7.404 | 838.6 | 0.0e+00 | (7, 1) | 64 | (7, 1) | 2.145 | continue |
| maze | 0.0e+00 | 8 | 10 | 7.1e-15 | 5.959 | 705.1 | 0.0e+00 | (5, 13) | 52 | (5, 13) | 2.039 | continue |
| maze | 0.0e+00 | 9 | 11 | 0.0e+00 | 4.782 | 590.6 | 0.0e+00 | (7, 15) | 76 | (7, 15) | 2.393 | continue |
| maze | 0.0e+00 | 10 | 12 | 0.0e+00 | 3.118 | 434.5 | 0.0e+00 | (5, 15) | 54 | (5, 15) | 3.118 | continue |
| maze | 0.0e+00 | 11 | 13 | 0.0e+00 | 0.0e+00 | 133 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| maze | 0.05 | 0 | 2 | 2.8e-11 | 1.879 | 210.9 | 0.0e+00 | (5, 19) | 57 | (5, 19) | 0.2381 | continue |
| maze | 0.05 | 1 | 3 | 2.9e-11 | 1.743 | 210.3 | 0.0e+00 | (5, 17) | 55 | (5, 17) | 0.3196 | continue |
| maze | 0.05 | 2 | 4 | 2.8e-11 | 1.423 | 190.9 | 0.0e+00 | (5, 3) | 44 | (5, 3) | 0.2045 | continue |
| maze | 0.05 | 3 | 5 | 2.6e-11 | 5.724 | 636.9 | 0.0e+00 | (5, 1) | 42 | (5, 1) | 0.813 | continue |
| maze | 0.05 | 4 | 6 | 2.6e-11 | 6.395 | 716 | 0.0e+00 | (5, 7) | 47 | (5, 7) | 0.959 | continue |
| maze | 0.05 | 5 | 7 | 2.6e-11 | 8.611 | 945.8 | 0.0e+00 | (5, 5) | 45 | (5, 5) | 1.627 | continue |
| maze | 0.05 | 6 | 8 | 2.6e-11 | 8.224 | 917.9 | 0.0e+00 | (7, 5) | 68 | (7, 5) | 1.871 | continue |
| maze | 0.05 | 7 | 9 | 2.6e-11 | 7.326 | 840.6 | 0.0e+00 | (7, 1) | 64 | (7, 1) | 2.133 | continue |
| maze | 0.05 | 8 | 10 | 2.6e-11 | 5.881 | 708.6 | 0.0e+00 | (5, 13) | 52 | (5, 13) | 1.994 | continue |
| maze | 0.05 | 9 | 11 | 2.6e-11 | 4.747 | 599.7 | 0.0e+00 | (7, 15) | 76 | (7, 15) | 2.376 | continue |
| maze | 0.05 | 10 | 12 | 2.6e-11 | 3.105 | 446.8 | 0.0e+00 | (5, 15) | 54 | (5, 15) | 3.105 | continue |
| maze | 0.05 | 11 | 13 | 2.6e-11 | 0.0e+00 | 149.1 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
