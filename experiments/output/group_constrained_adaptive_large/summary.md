# Larger Group-Constrained Adaptive Table

Generated: 2026-07-05T19:21:37
map_specs = ['open_room:12', 'four_rooms:11', 'maze:13']
slips = [0.0, 0.05]
methods = ['endpoints', 'group_constrained', 'group_constrained_incremental']
budget_frac = 0.25
first_hit_mode = adaptive, first_hit_tail_tol = 1e-06
elapsed_sec = 75.667

This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.

- feasible rows: `12/18`
- best planning speedup: `1442x`
- best total speedup: `4.457x`

## Method Summary

| method | n_rows | feasible_rows | feasible_rate | median_n_boundary | median_selection_time_sec | median_probe_green_kernel_time_sec | median_active_weight_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate | best_planning_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 6 | 0 | 0.0 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1442 | 4.457 | 1 | 233.2 |
| group_constrained | 6 | 6 | 1 | 4 | 5.379 | 2.013 | 0.0 | 0.002445 | 0.0 | 208.7 | 0.01743 | 109.5 | 0.0 |
| group_constrained_incremental | 6 | 6 | 1 | 3 | 1.274 | 0.02831 | 0.04062 | 0.001063 | 0.0 | 233.3 | 0.05848 | 26 | 0.0 |

## Rows

| map | slip | method | n_states | n_basis | n_boundary | state_compression_ratio | group_all_feasible | n_groups_feasible | group_total_violation | group_max_violation | trace_group_total_violation | group_test_bits_cvar | selection_time_sec | delta_backend | probe_green_kernel_time_sec | probe_operator_delta_time_sec | active_weight_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_used_steps_max | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | 72 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02287 | 8.451e-05 | 636.4 | 2.343 | 1 | 3.552713678800501e-15 | 21 | 0.0 |  |  |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 | 0.0 |  | 3.393 | operator | 1.287 | 0.9454 | 0.0 | 0.0008942 | 0.0 | 0.02966 | 0.001155 | 47.28 | 0.01595 | 65 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.0 | group_constrained_incremental | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.493 | insertion_score | 0.03907 | 0.01097 | 0.04918 | 0.0008691 | 0.0 | 0.02899 | 0.0002627 | 233.3 | 0.04026 | 25 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | 72 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02588 | 8.025e-05 | 1442 | 4.457 | 1 | 0.07851 | 41 | 3.737e-07 |  |  |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 | 0.0 |  | 14.47 | operator | 5.257 | 4.158 | 0.0 | 0.002624 | 0.0 | 0.04639 | 0.002847 | 40.57 | 0.007959 | 129 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| open_room_12 | 0.05 | group_constrained_incremental | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 | 0.0 | 3.7977806475397086e-10 | 4.696 | insertion_score | 0.1122 | 0.03775 | 0.1023 | 0.001892 | 0.0 | 0.04455 | 0.002772 | 40.45 | 0.02364 | 44 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | 52 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01908 | 8.066e-05 | 447.1 | 1.882 | 1 | 5.329070518200751e-15 | 19 | 0.0 |  |  |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 | 0.0 |  | 2.043 | operator | 0.7261 | 0.5929 | 0.0 | 0.0009157 | 0.0 | 0.02844 | 0.000173 | 208.7 | 0.01743 | 58 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.0 | group_constrained_incremental | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9076 | insertion_score | 0.01755 | 0.01223 | 0.02391 | 0.000961 | 0.0 | 0.02837 | 0.000175 | 205 | 0.03831 | 27 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | 52 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02535 | 8.645e-05 | 922 | 3.134 | 1 | 0.05768 | 39 | 7.41e-07 |  |  |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | 26 | True | 3 | 0.0 | 0.0 | 0.0 |  | 9.718 | operator | 3.442 | 2.849 | 0.0 | 0.002826 | 0.0 | 0.06866 | 0.0007576 | 104.2 | 0.008062 | 126 | 0.05768 | 39 | 9.381e-07 | feasible |  |
| four_rooms_11 | 0.05 | group_constrained_incremental | 104 | 29 | 5 | 20.8 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 4.821 | insertion_score | 0.1158 | 0.09825 | 0.09189 | 0.003391 | 0.0 | 0.1352 | 0.004883 | 18.07 | 0.01779 | 60 | 0.05768 | 39 | 9.265e-07 | feasible |  |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | 35.5 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01426 | 8.592e-05 | 398.1 | 2.384 | 1 | 7.105427357601002e-15 | 23 | 0.0 |  |  |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | 14.2 | True | 3 | 0.0 | 0.0 | 0.0 |  | 5.226 | operator | 2.064 | 1.429 | 0.0 | 0.003246 | 0.0 | 0.03877 | 0.001711 | 19.58 | 0.00636 | 166 | 3.552713678800501e-15 | 15 | 0.0 | feasible |  |
| maze_13 | 0.0 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6764 | insertion_score | 0.009523 | 0.009816 | 0.03206 | 0.001024 | 0.0 | 0.02155 | 0.001261 | 26.89 | 0.04848 | 22 | 7.105427357601002e-15 | 22 | 0.0 | feasible |  |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | 35.5 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0188 | 0.0001151 | 550 | 3.348 | 1 | 1.548e-08 | 42 | 4.298e-07 |  |  |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | 17.75 | True | 3 | 0.0 | 0.0 | 0.0 |  | 5.532 | operator | 1.962 | 1.623 | 0.0 | 0.002267 | 0.0 | 0.05175 | 0.002363 | 26.55 | 0.01123 | 93 | 4.297e-07 | 32 | 9.672e-07 | feasible |  |
| maze_13 | 0.05 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.054 | insertion_score | 0.009619 | 0.01091 | 0.01226 | 0.001102 | 0.0 | 0.03094 | 0.001674 | 37.97 | 0.05848 | 18 | 2.733e-07 | 41 | 7.73e-07 | feasible |  |
