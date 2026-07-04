# Greedy Split On Bypass

Generated: 2026-07-04T19:44:50
option_set = targeted, critical_kind = bottleneck, critical_top_fraction = 0.15
gamma = 0.97, slips = [0.0, 0.05], max_splits = 12, bypass_threshold = 1e-06
split_strategy = weighted_objective, policy_cost_mode = total, candidate_limit = 50
objective = 100.0*start_gap + 10.0*value_gap + 100.0*bypass + 0.2*policy + 1.0*graph + 1.0*option + 0.1*nonlocal

## Final Rows

| map | slip | step | n_boundary | start_gap | bypass_cost_total | split_objective | objective_delta | description_length_proxy | policy_tv_total | candidate_split_coord | selected_split_state | selected_split_coord | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.0e+00 | 6.06 | 0.0e+00 | 8.3 | 4 | None | None | None | bypass_threshold |
| corridor | 0.05 | 0 | 2 | 1.2e-11 | 0.0e+00 | 7.031 | 0.0e+00 | 9.26 | 3.933 | None | None | None | bypass_threshold |
| four_rooms | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.0e+00 | 31.36 | 0.0e+00 | 82.8 | 234 | None | None | None | bypass_threshold |
| four_rooms | 0.05 | 4 | 6 | 0.1152 | 0.01746 | 54.23 | -8.144 | 89.06 | 220.2 | (2, 7) | None | None | no_objective_improvement |
| maze | 0.0e+00 | 2 | 4 | 0.0e+00 | 1.449 | 190.2 | -278.8 | 141.6 | 268 | (7, 15) | None | None | no_objective_improvement |
| maze | 0.05 | 2 | 4 | 2.8e-11 | 1.423 | 190.9 | -268.9 | 142.1 | 250.9 | (7, 15) | None | None | no_objective_improvement |
| open_room | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.2875 | 35.95 | -18.19 | 14.29 | 30 | (1, 4) | None | None | no_objective_improvement |
| open_room | 0.05 | 0 | 2 | 0.0788 | 0.2881 | 45.6 | -19.45 | 14.95 | 28.4 | (1, 4) | None | None | no_objective_improvement |

## Split Trace

| map | slip | step | n_boundary | start_gap | bypass_cost_total | split_objective | objective_delta | candidate_split_coord | selected_split_state | selected_split_coord | selected_split_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.0e+00 | 6.06 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| corridor | 0.05 | 0 | 2 | 1.2e-11 | 0.0e+00 | 7.031 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| open_room | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.2875 | 35.95 | -18.19 | (1, 4) | None | None | 0.0e+00 | no_objective_improvement |
| open_room | 0.05 | 0 | 2 | 0.0788 | 0.2881 | 45.6 | -19.45 | (1, 4) | None | None | 0.0e+00 | no_objective_improvement |
| four_rooms | 0.0e+00 | 0 | 2 | 0.0e+00 | 5.094 | 519.4 | 87.67 | (3, 5) | 24 | (3, 5) | 2.469 | continue |
| four_rooms | 0.0e+00 | 1 | 3 | 1.8e-15 | 4.174 | 431.7 | 391.9 | (3, 7) | 26 | (3, 7) | 3.981 | continue |
| four_rooms | 0.0e+00 | 2 | 4 | 1.8e-15 | 0.1995 | 39.85 | 4.295 | (2, 5) | 14 | (2, 5) | 0.09975 | continue |
| four_rooms | 0.0e+00 | 3 | 5 | 1.8e-15 | 0.09975 | 35.56 | 4.195 | (4, 7) | 36 | (4, 7) | 0.09975 | continue |
| four_rooms | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.0e+00 | 31.36 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| four_rooms | 0.05 | 0 | 2 | 0.1152 | 5.046 | 528.1 | 84.28 | (3, 5) | 24 | (3, 5) | 2.444 | continue |
| four_rooms | 0.05 | 1 | 3 | 0.1152 | 4.151 | 443.8 | 386.8 | (3, 7) | 26 | (3, 7) | 3.95 | continue |
| four_rooms | 0.05 | 2 | 4 | 0.1152 | 0.2134 | 57.07 | 1.345 | (2, 5) | 14 | (2, 5) | 0.1015 | continue |
| four_rooms | 0.05 | 3 | 5 | 0.1152 | 0.1172 | 55.72 | 1.494 | (4, 7) | 36 | (4, 7) | 0.1032 | continue |
| four_rooms | 0.05 | 4 | 6 | 0.1152 | 0.01746 | 54.23 | -8.144 | (2, 7) | None | None | 0.0e+00 | no_objective_improvement |
| maze | 0.0e+00 | 0 | 2 | 3.6e-15 | 1.905 | 213 | 1.644 | (5, 19) | 57 | (5, 19) | 0.2376 | continue |
| maze | 0.0e+00 | 1 | 3 | 0.0e+00 | 1.774 | 211.4 | 21.19 | (5, 17) | 55 | (5, 17) | 0.3251 | continue |
| maze | 0.0e+00 | 2 | 4 | 0.0e+00 | 1.449 | 190.2 | -278.8 | (7, 15) | None | None | 0.0e+00 | no_objective_improvement |
| maze | 0.05 | 0 | 2 | 2.8e-11 | 1.879 | 210.9 | 0.5401 | (5, 19) | 57 | (5, 19) | 0.2381 | continue |
| maze | 0.05 | 1 | 3 | 2.9e-11 | 1.743 | 210.3 | 19.45 | (5, 17) | 55 | (5, 17) | 0.3196 | continue |
| maze | 0.05 | 2 | 4 | 2.8e-11 | 1.423 | 190.9 | -268.9 | (7, 15) | None | None | 0.0e+00 | no_objective_improvement |
