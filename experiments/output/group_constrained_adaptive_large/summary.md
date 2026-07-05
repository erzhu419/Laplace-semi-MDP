# Larger Group-Constrained Adaptive Table

Generated: 2026-07-05T17:00:34
map_specs = ['open_room:12', 'four_rooms:11', 'maze:13']
slips = [0.0, 0.05]
methods = ['endpoints', 'group_constrained']
budget_frac = 0.25
first_hit_mode = adaptive, first_hit_tail_tol = 1e-06
elapsed_sec = 205.182

This table evaluates larger group-constrained boundaries with adaptive first-hit Green kernels on the compressed graph-SMDP.

- feasible rows: `6/12`
- best planning speedup: `1255x`
- best total speedup: `4.278x`

## Method Summary

| method | n_rows | feasible_rows | feasible_rate | median_n_boundary | median_selection_time_sec | median_probe_green_kernel_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate | best_planning_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 6 | 0 | 0.0 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 1255 | 4.278 | 1 | 233.2 |
| group_constrained | 6 | 6 | 1 | 4 | 11.29 | 3.528 | 0.003336 | 0.0 | 218 | 0.008131 | 167.5 | 0.0 |

## Rows

| map | slip | method | n_states | n_basis | n_boundary | state_compression_ratio | group_all_feasible | n_groups_feasible | group_total_violation | group_max_violation | group_test_bits_cvar | selection_time_sec | probe_green_kernel_time_sec | probe_operator_delta_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_used_steps_max | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | 72 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02484 | 0.0001572 | 380.5 | 2.393 | 1 | 3.552713678800501e-15 | 21 | 0.0 |  |  |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | 48 | True | 3 | 0.0 | 0.0 |  | 36.52 | 31.97 | 2.72 | 0.001267 | 0.0 | 0.03217 | 0.001235 | 46.36 | 0.001566 | 653 | 3.552713678800501e-15 | 21 | 0.0 | feasible |  |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | 72 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02863 | 9.794e-05 | 1255 | 4.278 | 1 | 0.07851 | 41 | 3.737e-07 |  |  |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | 36 | True | 3 | 0.0 | 0.0 |  | 103.1 | 88.54 | 7.868 | 0.003326 | 0.0 | 0.05134 | 0.003279 | 37.97 | 0.001207 | 851 | 0.07851 | 40 | 9.787e-07 | feasible |  |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | 52 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02053 | 8.693e-05 | 433.1 | 1.826 | 1 | 5.329070518200751e-15 | 19 | 0.0 |  |  |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | 34.67 | True | 3 | 0.0 | 0.0 |  | 5.825 | 3.277 | 1.316 | 0.001465 | 0.0 | 0.03126 | 0.0001961 | 218 | 0.007298 | 138 | 5.329070518200751e-15 | 19 | 0.0 | feasible |  |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | 52 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02753 | 8.881e-05 | 937.8 | 3.016 | 1 | 0.05768 | 39 | 7.41e-07 |  |  |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | 26 | True | 3 | 0.0 | 0.0 |  | 13.12 | 3.779 | 4.587 | 0.00368 | 0.0 | 0.07736 | 0.0007685 | 108.4 | 0.006311 | 160 | 0.05768 | 39 | 9.381e-07 | feasible |  |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | 35.5 | False | 1 | 155.5 | 77.73 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01539 | 9.035e-05 | 394.5 | 2.302 | 1 | 7.105427357601002e-15 | 23 | 0.0 |  |  |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | 14.2 | True | 3 | 0.0 | 0.0 |  | 9.461 | 2.641 | 3.978 | 0.004614 | 0.0 | 0.04369 | 0.001806 | 31.13 | 0.005914 | 175 | 3.552713678800501e-15 | 15 | 0.0 | feasible |  |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | 35.5 | False | 0 | 233.2 | 77.73 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02101 | 0.0001012 | 633.8 | 3.04 | 1 | 1.548e-08 | 42 | 4.298e-07 |  |  |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | 17.75 | True | 3 | 0.0 | 0.0 |  | 8.19 | 2.053 | 3.158 | 0.003346 | 0.0 | 0.05922 | 0.002737 | 24.52 | 0.008131 | 129 | 4.297e-07 | 32 | 9.672e-07 | feasible |  |
