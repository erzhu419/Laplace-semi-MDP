# Larger Group-Constrained Adaptive Table

Generated: 2026-07-05T17:30:58
map_specs = ['open_room:12', 'four_rooms:11', 'maze:13']
slips = [0.0, 0.05]
methods = ['endpoints', 'group_constrained', 'group_constrained_incremental']
budget_frac = 0.25
first_hit_mode = adaptive, first_hit_tail_tol = 1e-06
elapsed_sec = 230.601

This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.

- feasible rows: `11/18`
- best planning speedup: `1314x`
- best total speedup: `4.097x`

## Method Summary

| method | n_rows | feasible_rows | feasible_rate | median_n_boundary | median_selection_time_sec | median_probe_green_kernel_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate | best_planning_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 6 | 0 | 0.0 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 1314 | 4.097 | 1 | 233.2 |
| group_constrained | 6 | 6 | 1 | 4 | 10.7 | 3.126 | 0.003298 | 0.0 | 248.3 | 0.01197 | 159.5 | 0.0 |
| group_constrained_incremental | 6 | 5 | 0.8333 | 3 | 3.25 | 0.3545 | 0.001938 | 0.0 | 197 | 0.05543 | 55 | 97.16 |

## Rows

| map | slip | method | n_states | n_basis | n_boundary | state_compression_ratio | group_all_feasible | n_groups_feasible | group_total_violation | group_max_violation | group_test_bits_cvar | selection_time_sec | delta_backend | probe_green_kernel_time_sec | probe_operator_delta_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_used_steps_max | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | 72 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02543 | 9.164e-05 | 619.3 | 2.224 | 1 | 3.552713678800501e-15 | 21 | 0.0 |  |  |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 |  | 13.86 | operator | 10.04 | 2.098 | 0.001538 | 0.0 | 0.03241 | 0.001157 | 48.55 | 0.004045 | 253 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.0 | group_constrained_incremental | 144 | 24 | 3 | 48 | False | 2 | 97.16 | 97.16 |  | 89.48 | insertion_score | 77.39 | 0.5036 | 0.008679 | 0.0 | 0.03115 | 0.0002865 | 197 | 0.0006307 | 1594 | 3.552713678800501e-15 | 21 | 0.0 | budget_not_met |  |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | 72 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02852 | 8.923e-05 | 1314 | 4.097 | 1 | 0.07851 | 41 | 3.737e-07 |  |  |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 |  | 52.32 | operator | 39.2 | 6.703 | 0.003474 | 0.0 | 0.04994 | 0.003014 | 39.93 | 0.002297 | 447 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| open_room_12 | 0.05 | group_constrained_incremental | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 |  | 15.42 | insertion_score | 9.577 | 0.07434 | 0.002712 | 0.0 | 0.05041 | 0.002881 | 41.15 | 0.007661 | 134 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | 52 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02128 | 0.0002071 | 177.3 | 1.709 | 1 | 5.329070518200751e-15 | 19 | 0.0 |  |  |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 |  | 3.951 | operator | 1.545 | 1.195 | 0.001372 | 0.0 | 0.03157 | 0.0001921 | 248.3 | 0.01197 | 84 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.0 | group_constrained_incremental | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 |  | 1.606 | insertion_score | 0.5907 | 0.0162 | 0.001078 | 0.0 | 0.03073 | 0.0001935 | 194.5 | 0.023 | 44 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | 52 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02756 | 0.0001309 | 621.1 | 2.937 | 1 | 0.05768 | 39 | 7.41e-07 |  |  |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | 26 | True | 3 | 0.0 | 0.0 |  | 12.45 | operator | 3.628 | 4.031 | 0.003625 | 0.0 | 0.07691 | 0.0007959 | 104.4 | 0.00663 | 153 | 0.05768 | 39 | 9.381e-07 | feasible |  |
| four_rooms_11 | 0.05 | group_constrained_incremental | 104 | 29 | 5 | 20.8 | True | 3 | 0.0 | 0.0 |  | 4.893 | insertion_score | 0.1183 | 0.1037 | 0.00356 | 0.0 | 0.1256 | 0.004452 | 18.3 | 0.01622 | 66 | 0.05768 | 39 | 9.265e-07 | feasible |  |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | 35.5 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.01516 | 8.558e-05 | 405 | 2.273 | 1 | 7.105427357601002e-15 | 23 | 0.0 |  |  |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | 14.2 | True | 3 | 0.0 | 0.0 |  | 8.938 | operator | 2.624 | 3.315 | 0.009708 | 0.0 | 0.04463 | 0.001859 | 30.23 | 0.006254 | 166 | 3.552713678800501e-15 | 15 | 0.0 | feasible |  |
| maze_13 | 0.0 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 |  | 0.7091 | insertion_score | 0.01033 | 0.01077 | 0.001111 | 0.0 | 0.02362 | 0.001343 | 26.14 | 0.04783 | 22 | 7.105427357601002e-15 | 22 | 0.0 | feasible |  |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | 35.5 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.02037 | 8.574e-05 | 746.1 | 3.127 | 1 | 1.548e-08 | 42 | 4.298e-07 |  |  |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | 17.75 | True | 3 | 0.0 | 0.0 |  | 7.596 | operator | 2.049 | 2.572 | 0.003122 | 0.0 | 0.05591 | 0.00266 | 24.23 | 0.00842 | 124 | 4.297e-07 | 32 | 9.672e-07 | feasible |  |
| maze_13 | 0.05 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 |  | 1.129 | insertion_score | 0.01025 | 0.01183 | 0.001164 | 0.0 | 0.03529 | 0.001912 | 33.81 | 0.05543 | 19 | 2.733e-07 | 41 | 7.73e-07 | feasible |  |
