# Random Maze Generalization

Generated: 2026-07-05T19:41:09
sizes = [9]
seeds = [0, 1]
slips = [0.05]
methods = ['endpoints', 'group_constrained_operator', 'group_constrained_incremental']
elapsed_sec = 9.023

This is a topology-family stress test: each row uses a fresh DFS maze instance, then runs the same group-constrained boundary selector and compressed graph-SMDP evaluation.

- completed rows: `6/6`

## Method Summary

| method | n_rows | feasible_rate | median_n_boundary | median_state_compression_ratio | median_selection_time_sec | median_kernel_time_sec | median_total_speedup | median_break_even_tasks | max_group_total_violation | max_start_gap | max_tail_bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 2 | 0.0 | 2 | 15.5 | 0.0 | 0.006828 | 2.494 | 1 | 233.2 | 3.332e-08 | 7.862e-07 |
| group_constrained_incremental | 2 | 1 | 3 | 10.33 | 0.3035 | 0.01196 | 0.05424 | 20.5 | 0.0 | 2.167e-07 | 9.597e-07 |
| group_constrained_operator | 2 | 0.5 | 3 | 10.33 | 3.323 | 0.01206 | 0.008238 | 190.5 | 116.6 | 1.633e-07 | 8.511e-07 |

## Rows

| map | maze_seed | slip | method | n_states | n_boundary | state_compression_ratio | group_all_feasible | group_total_violation | selection_time_sec | delta_backend | probe_green_kernel_time_sec | active_weight_time_sec | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_tail_bound_max | stop_reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_maze_9_seed0 | 0 | 0.05 | endpoints | 31 | 2 | 15.5 | False | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.006002 | 8.451e-05 | 186.1 | 2.584 | 1 | 3.332e-08 | 7.862e-07 |  |  |
| random_maze_9_seed0 | 0 | 0.05 | group_constrained_operator | 31 | 3 | 10.33 | True | 0.0 | 1.157 | operator | 0.4051 | 0.0 | 0.01046 | 0.001009 | 15.16 | 0.01309 | 82 | 1.633e-07 | 8.065e-07 | feasible |  |
| random_maze_9_seed0 | 0 | 0.05 | group_constrained_incremental | 31 | 3 | 10.33 | True | 0.0 | 0.2808 | insertion_score | 0.004835 | 0.003751 | 0.01025 | 0.001062 | 14.65 | 0.05324 | 21 | 1.633e-07 | 8.065e-07 | feasible |  |
| random_maze_9_seed1 | 1 | 0.05 | endpoints | 31 | 2 | 15.5 | False | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.007655 | 8.552e-05 | 217.6 | 2.404 | 1 | 1.724e-08 | 4.029e-07 |  |  |
| random_maze_9_seed1 | 1 | 0.05 | group_constrained_operator | 31 | 3 | 10.33 | False | 116.6 | 5.489 | operator | 2.367 | 0.0 | 0.01367 | 0.0001681 | 110.8 | 0.003385 | 299 | 6.702e-08 | 8.511e-07 | budget_not_met |  |
| random_maze_9_seed1 | 1 | 0.05 | group_constrained_incremental | 31 | 3 | 10.33 | True | 0.0 | 0.3261 | insertion_score | 0.003953 | 0.003558 | 0.01367 | 0.001226 | 15.36 | 0.05523 | 20 | 2.167e-07 | 9.597e-07 | feasible |  |
