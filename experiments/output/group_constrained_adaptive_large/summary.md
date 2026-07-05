# Larger Group-Constrained Adaptive Table

Generated: 2026-07-05T18:58:23
map_specs = ['open_room:12', 'four_rooms:11', 'maze:13']
slips = [0.0, 0.05]
methods = ['endpoints', 'group_constrained', 'group_constrained_incremental']
budget_frac = 0.25
first_hit_mode = adaptive, first_hit_tail_tol = 1e-06
elapsed_sec = 284.770

This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.

- feasible rows: `12/18`
- best planning speedup: `1357x`
- best total speedup: `4.244x`

## Method Summary

| method | n_rows | feasible_rows | feasible_rate | median_n_boundary | median_selection_time_sec | median_probe_green_kernel_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate | best_planning_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 6 | 0 | 0.0 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 1357 | 4.244 | 1 | 233.2 |
| group_constrained | 6 | 6 | 1 | 4 | 10.42 | 3.062 | 0.003444 | 0.0 | 188.3 | 0.00821 | 182 | 0.0 |
| group_constrained_incremental | 6 | 6 | 1 | 3 | 5.751 | 3.109 | 0.001866 | 0.0 | 208.5 | 0.02752 | 98.5 | 0.0 |

## Rows

| map | slip | method | n_states | n_basis | n_boundary | state_compression_ratio | group_all_feasible | n_groups_feasible | group_total_violation | group_max_violation | trace_group_total_violation | group_test_bits_cvar | selection_time_sec | delta_backend | probe_green_kernel_time_sec | probe_operator_delta_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_used_steps_max | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | 72 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02357 | 8.308e-05 | 641.8 | 2.255 | 1 | 3.552713678800501e-15 | 21 | 0.0 |  |  |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 | 0.0 |  | 14.35 | operator | 10.89 | 1.895 | 0.001164 | 0.0 | 0.02961 | 0.00109 | 48.02 | 0.003639 | 281 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.0 | group_constrained_incremental | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 17 | insertion_score | 15.2 | 0.01701 | 0.00271 | 0.0 | 0.02912 | 0.0002589 | 208.5 | 0.003168 | 318 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | 72 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02601 | 8.159e-05 | 1357 | 4.244 | 1 | 0.07851 | 41 | 3.737e-07 |  |  |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 | 0.0 |  | 50.84 | operator | 38.58 | 6.238 | 0.005254 | 0.0 | 0.048 | 0.003029 | 37.35 | 0.002223 | 463 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| open_room_12 | 0.05 | group_constrained_incremental | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 | 0.0 | 3.7977806475397086e-10 | 58.53 | insertion_score | 53.22 | 0.05828 | 0.002583 | 0.0 | 0.04492 | 0.00281 | 41.56 | 0.001994 | 514 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | 52 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.01885 | 7.748e-05 | 450.4 | 1.844 | 1 | 5.329070518200751e-15 | 19 | 0.0 |  |  |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 | 0.0 |  | 5.13 | operator | 2.752 | 1.272 | 0.001342 | 0.0 | 0.02757 | 0.0002249 | 188.3 | 0.00821 | 123 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.0 | group_constrained_incremental | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 2.839 | insertion_score | 1.883 | 0.01378 | 0.0009636 | 0.0 | 0.028 | 0.0002163 | 174.7 | 0.01318 | 77 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | 52 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02498 | 0.0001217 | 644.8 | 3.127 | 1 | 0.05768 | 39 | 7.41e-07 |  |  |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | 26 | True | 3 | 0.0 | 0.0 | 0.0 |  | 11.87 | operator | 3.372 | 4.12 | 0.003636 | 0.0 | 0.06729 | 0.0007788 | 100.8 | 0.006573 | 154 | 0.05768 | 39 | 9.381e-07 | feasible |  |
| four_rooms_11 | 0.05 | group_constrained_incremental | 104 | 29 | 5 | 20.8 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 8.662 | insertion_score | 4.335 | 0.09484 | 0.002955 | 0.0 | 0.1133 | 0.00397 | 19.43 | 0.008786 | 120 | 0.05768 | 39 | 9.265e-07 | feasible |  |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | 35.5 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.01371 | 9.089e-05 | 362.3 | 2.386 | 1 | 7.105427357601002e-15 | 23 | 0.0 |  |  |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | 14.2 | True | 3 | 0.0 | 0.0 | 0.0 |  | 8.977 | operator | 2.43 | 3.802 | 0.004571 | 0.0 | 0.04028 | 0.001841 | 24.34 | 0.004968 | 210 | 3.552713678800501e-15 | 15 | 0.0 | feasible |  |
| maze_13 | 0.0 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.362 | insertion_score | 0.7139 | 0.01007 | 0.001005 | 0.0 | 0.02235 | 0.001116 | 30.07 | 0.02422 | 43 | 7.105427357601002e-15 | 22 | 0.0 | feasible |  |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | 35.5 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02031 | 8.963e-05 | 698.1 | 3.067 | 1 | 1.548e-08 | 42 | 4.298e-07 |  |  |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | 17.75 | True | 3 | 0.0 | 0.0 | 0.0 |  | 7.946 | operator | 1.914 | 3.203 | 0.003252 | 0.0 | 0.05081 | 0.002287 | 26.1 | 0.007464 | 140 | 4.297e-07 | 32 | 9.672e-07 | feasible |  |
| maze_13 | 0.05 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 2.198 | insertion_score | 1.032 | 0.01215 | 0.001149 | 0.0 | 0.03082 | 0.001568 | 39.13 | 0.02752 | 38 | 2.733e-07 | 41 | 7.73e-07 | feasible |  |
