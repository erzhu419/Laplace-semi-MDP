# Greedy Split On Bypass

Generated: 2026-07-04T19:45:22
option_set = targeted, critical_kind = bottleneck, critical_top_fraction = 0.15
gamma = 0.97, slips = [0.0, 0.05], max_splits = 12, bypass_threshold = 1e-06
split_strategy = weighted_objective, policy_cost_mode = mean, candidate_limit = 50
objective = 100.0*start_gap + 10.0*value_gap + 100.0*bypass + 1.0*policy + 1.0*graph + 1.0*option + 0.1*nonlocal

## Final Rows

| map | slip | step | n_boundary | start_gap | bypass_cost_total | split_objective | objective_delta | description_length_proxy | policy_tv_total | candidate_split_coord | selected_split_state | selected_split_coord | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.0e+00 | 6.9 | 0.0e+00 | 8.3 | 4 | None | None | None | bypass_threshold |
| corridor | 0.05 | 0 | 2 | 1.2e-11 | 0.0e+00 | 7.867 | 0.0e+00 | 9.26 | 3.933 | None | None | None | bypass_threshold |
| four_rooms | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.0e+00 | 29.22 | 0.0e+00 | 82.8 | 234 | None | None | None | bypass_threshold |
| four_rooms | 0.05 | 4 | 6 | 0.1152 | 0.01746 | 52.18 | -6.056 | 89.06 | 220.2 | (2, 7) | None | None | no_objective_improvement |
| maze | 0.0e+00 | 2 | 4 | 0.0e+00 | 1.449 | 196.1 | -272.9 | 141.6 | 268 | (7, 15) | None | None | no_objective_improvement |
| maze | 0.05 | 2 | 4 | 2.8e-11 | 1.423 | 196.6 | -263.1 | 142.1 | 250.9 | (7, 15) | None | None | no_objective_improvement |
| open_room | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.2875 | 38.5 | -17.4 | 14.29 | 30 | (1, 4) | None | None | no_objective_improvement |
| open_room | 0.05 | 0 | 2 | 0.0788 | 0.2881 | 48.05 | -18.69 | 14.95 | 28.4 | (1, 4) | None | None | no_objective_improvement |

## Split Trace

| map | slip | step | n_boundary | start_gap | bypass_cost_total | split_objective | objective_delta | candidate_split_coord | selected_split_state | selected_split_coord | selected_split_score | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.0e+00 | 6.9 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| corridor | 0.05 | 0 | 2 | 1.2e-11 | 0.0e+00 | 7.867 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| open_room | 0.0e+00 | 0 | 2 | 0.0e+00 | 0.2875 | 38.5 | -17.4 | (1, 4) | None | None | 0.0e+00 | no_objective_improvement |
| open_room | 0.05 | 0 | 2 | 0.0788 | 0.2881 | 48.05 | -18.69 | (1, 4) | None | None | 0.0e+00 | no_objective_improvement |
| four_rooms | 0.0e+00 | 0 | 2 | 0.0e+00 | 5.094 | 525 | 89.27 | (3, 5) | 24 | (3, 5) | 2.469 | continue |
| four_rooms | 0.0e+00 | 1 | 3 | 1.8e-15 | 4.174 | 435.8 | 393.8 | (3, 7) | 26 | (3, 7) | 3.981 | continue |
| four_rooms | 0.0e+00 | 2 | 4 | 1.8e-15 | 0.1995 | 41.93 | 6.37 | (2, 5) | 14 | (2, 5) | 0.09975 | continue |
| four_rooms | 0.0e+00 | 3 | 5 | 1.8e-15 | 0.09975 | 35.56 | 6.338 | (4, 7) | 36 | (4, 7) | 0.09975 | continue |
| four_rooms | 0.0e+00 | 4 | 6 | 0.0e+00 | 0.0e+00 | 29.22 | 0.0e+00 | None | None | None | 0.0e+00 | bypass_threshold |
| four_rooms | 0.05 | 0 | 2 | 0.1152 | 5.046 | 533.5 | 85.8 | (3, 5) | 24 | (3, 5) | 2.444 | continue |
| four_rooms | 0.05 | 1 | 3 | 0.1152 | 4.151 | 447.7 | 388.6 | (3, 7) | 26 | (3, 7) | 3.95 | continue |
| four_rooms | 0.05 | 2 | 4 | 0.1152 | 0.2134 | 59.06 | 3.332 | (2, 5) | 14 | (2, 5) | 0.1015 | continue |
| four_rooms | 0.05 | 3 | 5 | 0.1152 | 0.1172 | 55.72 | 3.545 | (4, 7) | 36 | (4, 7) | 0.1032 | continue |
| four_rooms | 0.05 | 4 | 6 | 0.1152 | 0.01746 | 52.18 | -6.056 | (2, 7) | None | None | 0.0e+00 | no_objective_improvement |
| maze | 0.0e+00 | 0 | 2 | 3.6e-15 | 1.905 | 230.8 | 7.634 | (5, 19) | 57 | (5, 19) | 0.2376 | continue |
| maze | 0.0e+00 | 1 | 3 | 0.0e+00 | 1.774 | 223.2 | 27.06 | (5, 17) | 55 | (5, 17) | 0.3251 | continue |
| maze | 0.0e+00 | 2 | 4 | 0.0e+00 | 1.449 | 196.1 | -272.9 | (7, 15) | None | None | 0.0e+00 | no_objective_improvement |
| maze | 0.05 | 0 | 2 | 2.8e-11 | 1.879 | 228.2 | 6.358 | (5, 19) | 57 | (5, 19) | 0.2381 | continue |
| maze | 0.05 | 1 | 3 | 2.9e-11 | 1.743 | 221.8 | 25.15 | (5, 17) | 55 | (5, 17) | 0.3196 | continue |
| maze | 0.05 | 2 | 4 | 2.8e-11 | 1.423 | 196.6 | -263.1 | (7, 15) | None | None | 0.0e+00 | no_objective_improvement |
