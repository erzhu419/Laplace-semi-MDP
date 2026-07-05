# Larger Group-Constrained Adaptive Table

Generated: 2026-07-05T16:43:26
map_specs = ['open_room:12', 'four_rooms:11', 'maze:13']
slips = [0.0, 0.05]
methods = ['endpoints', 'group_constrained']
budget_frac = 0.25
first_hit_mode = adaptive, first_hit_tail_tol = 1e-06
elapsed_sec = 224.375

This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.

- feasible rows: `6/12`
- best planning speedup: `896.5x`
- best total speedup: `4.281x`

## Method Summary

| method | n_rows | feasible_rows | feasible_rate | median_n_boundary | best_planning_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 6 | 0 | 0.0 | 2 | 896.5 | 4.281 | 1 | 233.2 |
| group_constrained | 6 | 6 | 1 | 4 | 232.2 | 0.009028 | 207 | 0.0 |

## Rows

| map | slip | method | n_states | n_basis | n_boundary | state_compression_ratio | group_all_feasible | n_groups_feasible | group_total_violation | group_max_violation | group_test_bits_cvar | selection_time_sec | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_used_steps_max | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | 72 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 | 0.02574 | 9.427e-05 | 609.3 | 2.224 | 1 | 3.552713678800501e-15 | 21 | 0.0 |  |  |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 |  | 46.35 | 0.03248 | 0.001132 | 50.45 | 0.001231 | 829 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | 72 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 | 0.033 | 0.0001743 | 814.8 | 4.281 | 1 | 0.07851 | 41 | 3.737e-07 |  |  |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 |  | 106.1 | 0.04974 | 0.002978 | 39.69 | 0.001114 | 922 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | 52 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 | 0.0215 | 8.948e-05 | 449.4 | 1.863 | 1 | 5.329070518200751e-15 | 19 | 0.0 |  |  |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 |  | 4.959 | 0.03197 | 0.0001941 | 232.2 | 0.009028 | 112 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | 52 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 | 0.0284 | 9.346e-05 | 896.5 | 2.941 | 1 | 0.05768 | 39 | 7.41e-07 |  |  |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | 26 | True | 3 | 0.0 | 0.0 |  | 14.49 | 0.075 | 0.0007895 | 105 | 0.00569 | 178 | 0.05768 | 39 | 9.381e-07 | feasible |  |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | 35.5 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 | 0.0202 | 8.807e-05 | 412.9 | 1.793 | 1 | 7.105427357601002e-15 | 23 | 0.0 |  |  |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | 14.2 | True | 3 | 0.0 | 0.0 |  | 11.03 | 0.05935 | 0.001989 | 24.65 | 0.004419 | 236 | 3.552713678800501e-15 | 15 | 0.0 | feasible |  |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | 35.5 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 | 0.02127 | 8.96e-05 | 735.2 | 3.085 | 1 | 1.548e-08 | 42 | 4.298e-07 |  |  |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | 17.75 | True | 3 | 0.0 | 0.0 |  | 9.986 | 0.06452 | 0.002901 | 23.17 | 0.006685 | 157 | 4.297e-07 | 32 | 9.672e-07 | feasible |  |
