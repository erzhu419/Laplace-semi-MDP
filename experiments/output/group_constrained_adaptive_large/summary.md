# Larger Group-Constrained Adaptive Table

Generated: 2026-07-05T19:11:18
map_specs = ['open_room:12', 'four_rooms:11', 'maze:13']
slips = [0.0, 0.05]
methods = ['endpoints', 'group_constrained', 'group_constrained_incremental']
budget_frac = 0.25
first_hit_mode = adaptive, first_hit_tail_tol = 1e-06
elapsed_sec = 79.318

This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.

- feasible rows: `12/18`
- best planning speedup: `1391x`
- best total speedup: `4.251x`

## Method Summary

| method | n_rows | feasible_rows | feasible_rate | median_n_boundary | median_selection_time_sec | median_probe_green_kernel_time_sec | median_active_weight_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate | best_planning_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 6 | 0 | 0.0 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1391 | 4.251 | 1 | 233.2 |
| group_constrained | 6 | 6 | 1 | 4 | 5.41 | 1.99 | 0.0 | 0.002285 | 0.0 | 163.2 | 0.01666 | 112 | 0.0 |
| group_constrained_incremental | 6 | 6 | 1 | 3 | 1.583 | 0.02776 | 0.3463 | 0.001041 | 0.0 | 216.4 | 0.04434 | 35.5 | 0.0 |

## Rows

| map | slip | method | n_states | n_basis | n_boundary | state_compression_ratio | group_all_feasible | n_groups_feasible | group_total_violation | group_max_violation | trace_group_total_violation | group_test_bits_cvar | selection_time_sec | delta_backend | probe_green_kernel_time_sec | probe_operator_delta_time_sec | active_weight_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_used_steps_max | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | 72 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02448 | 8.938e-05 | 582.5 | 2.119 | 1 | 3.552713678800501e-15 | 21 | 0.0 |  |  |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 | 0.0 |  | 3.451 | operator | 1.309 | 0.9658 | 0.0 | 0.0009428 | 0.0 | 0.02937 | 0.001071 | 50.18 | 0.01544 | 67 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.0 | group_constrained_incremental | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.856 | insertion_score | 0.03719 | 0.01085 | 0.4026 | 0.0008951 | 0.0 | 0.02941 | 0.0004992 | 105.6 | 0.02794 | 37 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | 72 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02517 | 7.718e-05 | 1391 | 4.251 | 1 | 0.07851 | 41 | 3.737e-07 |  |  |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 | 0.0 |  | 14.57 | operator | 5.32 | 4.24 | 0.0 | 0.00243 | 0.0 | 0.04563 | 0.002707 | 40.55 | 0.00751 | 137 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| open_room_12 | 0.05 | group_constrained_incremental | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 | 0.0 | 3.7977806475397086e-10 | 5.93 | insertion_score | 0.1132 | 0.03792 | 1.325 | 0.001983 | 0.0 | 0.04621 | 0.002855 | 38.33 | 0.0183 | 57 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | 52 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01975 | 8.948e-05 | 390.2 | 1.76 | 1 | 5.329070518200751e-15 | 19 | 0.0 |  |  |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 | 0.0 |  | 2.102 | operator | 0.7479 | 0.6113 | 0.0 | 0.0009813 | 0.0 | 0.02893 | 0.0002176 | 163.2 | 0.01666 | 61 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.0 | group_constrained_incremental | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.186 | insertion_score | 0.01833 | 0.01263 | 0.258 | 0.001023 | 0.0 | 0.02943 | 0.0001687 | 216.4 | 0.03004 | 34 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | 52 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.026 | 8.466e-05 | 917.5 | 2.978 | 1 | 0.05768 | 39 | 7.41e-07 |  |  |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | 26 | True | 3 | 0.0 | 0.0 | 0.0 |  | 9.717 | operator | 3.509 | 2.846 | 0.0 | 0.002713 | 0.0 | 0.06871 | 0.0006575 | 117.8 | 0.007915 | 128 | 0.05768 | 39 | 9.381e-07 | feasible |  |
| four_rooms_11 | 0.05 | group_constrained_incremental | 104 | 29 | 5 | 20.8 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 5.924 | insertion_score | 0.1107 | 0.09558 | 1.353 | 0.003179 | 0.0 | 0.1145 | 0.003946 | 19.66 | 0.01284 | 83 | 0.05768 | 39 | 9.265e-07 | feasible |  |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | 35.5 | False | 1 | 155.5 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01453 | 7.786e-05 | 422.7 | 2.253 | 1 | 7.105427357601002e-15 | 23 | 0.0 |  |  |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | 14.2 | True | 3 | 0.0 | 0.0 | 0.0 |  | 5.362 | operator | 2.098 | 1.507 | 0.0 | 0.003127 | 0.0 | 0.04022 | 0.001711 | 19.35 | 0.006126 | 173 | 3.552713678800501e-15 | 15 | 0.0 | feasible |  |
| maze_13 | 0.0 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8799 | insertion_score | 0.01018 | 0.01008 | 0.2064 | 0.001045 | 0.0 | 0.02215 | 0.001246 | 26.33 | 0.03632 | 29 | 7.105427357601002e-15 | 22 | 0.0 | feasible |  |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | 35.5 | False | 0 | 233.2 | 77.73 |  | 0.0 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01877 | 8.128e-05 | 742.8 | 3.203 | 1 | 1.548e-08 | 42 | 4.298e-07 |  |  |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | 17.75 | True | 3 | 0.0 | 0.0 | 0.0 |  | 5.457 | operator | 1.882 | 1.612 | 0.0 | 0.002139 | 0.0 | 0.05208 | 0.002247 | 26.72 | 0.01089 | 96 | 4.297e-07 | 32 | 9.672e-07 | feasible |  |
| maze_13 | 0.05 | group_constrained_incremental | 71 | 33 | 3 | 23.67 | True | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 1.309 | insertion_score | 0.00925 | 0.0106 | 0.29 | 0.001037 | 0.0 | 0.0314 | 0.001682 | 35.37 | 0.04434 | 24 | 2.733e-07 | 41 | 7.73e-07 | feasible |  |
