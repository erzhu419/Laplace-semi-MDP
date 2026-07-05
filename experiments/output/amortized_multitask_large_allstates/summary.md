# Amortized Multi-Task Compression

Generated: 2026-07-05T14:24:06
map_specs = ['corridor:64', 'maze:13']
methods = ['endpoints', 'graph_rd_surrogate_joint', 'turn_articulation']
task_counts = [1, 5, 10, 25], max_tasks = 25
goal_source = all_states

A boundary set and first-boundary kernels are built once, then reused across many terminal-goal tasks.

| map | method_spec | method | task_count | n_states | n_boundary | state_compression_ratio | upfront_time_sec | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | break_even_task_count_estimate | backup_compression_ratio | start_gap_mean | start_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | endpoints | 1 | 64 | 26 | 2.462 | 0.862 | 0.1396 | 1.428 | 0.09773 | inf | 0.5056 | 2.901501261476369e-11 | 2.901501261476369e-11 |
| corridor_64 | endpoints | endpoints | 5 | 64 | 26 | 2.462 | 0.862 | 0.6269 | 3.295 | 0.1902 | inf | 0.508 | 5.8040683370563785e-12 | 2.901501261476369e-11 |
| corridor_64 | endpoints | endpoints | 10 | 64 | 26 | 2.462 | 0.862 | 0.9523 | 4.552 | 0.2092 | inf | 0.5088 | 2.9052316108391096e-12 | 2.901501261476369e-11 |
| corridor_64 | endpoints | endpoints | 25 | 64 | 26 | 2.462 | 0.862 | 1.923 | 8.496 | 0.2263 | inf | 0.5096 | 1.6203856034735507e-11 | 4.866507197220926e-11 |
| corridor_64 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 1 | 64 | 26 | 2.462 | 0.8772 | 0.1148 | 1.198 | 0.09581 | inf | 0.5056 | 2.901501261476369e-11 | 2.901501261476369e-11 |
| corridor_64 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 5 | 64 | 26 | 2.462 | 0.8772 | 0.5519 | 2.413 | 0.2288 | inf | 0.508 | 5.8040683370563785e-12 | 2.901501261476369e-11 |
| corridor_64 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 10 | 64 | 26 | 2.462 | 0.8772 | 1.013 | 4.624 | 0.219 | inf | 0.5088 | 2.9052316108391096e-12 | 2.901501261476369e-11 |
| corridor_64 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 25 | 64 | 26 | 2.462 | 0.8772 | 2.353 | 8.361 | 0.2814 | inf | 0.5096 | 1.6203856034735507e-11 | 4.866507197220926e-11 |
| corridor_64 | turn_articulation | turn_articulation | 1 | 64 | 26 | 2.462 | 0.6563 | 0.1179 | 0.9994 | 0.1179 | inf | 0.5056 | 2.901501261476369e-11 | 2.901501261476369e-11 |
| corridor_64 | turn_articulation | turn_articulation | 5 | 64 | 26 | 2.462 | 0.6563 | 0.5591 | 2.233 | 0.2503 | inf | 0.508 | 5.8040683370563785e-12 | 2.901501261476369e-11 |
| corridor_64 | turn_articulation | turn_articulation | 10 | 64 | 26 | 2.462 | 0.6563 | 1.02 | 3.532 | 0.2889 | inf | 0.5088 | 2.9052316108391096e-12 | 2.901501261476369e-11 |
| corridor_64 | turn_articulation | turn_articulation | 25 | 64 | 26 | 2.462 | 0.6563 | 2.366 | 7.388 | 0.3202 | inf | 0.5096 | 1.6203856034735507e-11 | 4.866507197220926e-11 |
| maze_13 | endpoints | endpoints | 1 | 71 | 26 | 2.731 | 0.76 | 0.06763 | 0.9564 | 0.07072 | inf | 0.5789 | 1.7408297026122455e-13 | 1.7408297026122455e-13 |
| maze_13 | endpoints | endpoints | 5 | 71 | 26 | 2.731 | 0.76 | 0.3926 | 2.011 | 0.1952 | inf | 0.5682 | 4.1744385725905886e-14 | 1.7408297026122455e-13 |
| maze_13 | endpoints | endpoints | 10 | 71 | 26 | 2.731 | 0.76 | 0.747 | 3.198 | 0.2336 | inf | 0.5691 | 3.278355364955132e-12 | 3.253219915677619e-11 |
| maze_13 | endpoints | endpoints | 25 | 71 | 26 | 2.731 | 0.76 | 1.885 | 6.594 | 0.2859 | inf | 0.5716 | 1.057824050576528e-11 | 4.674660658565699e-11 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 1 | 71 | 30 | 2.367 | 2.502 | 0.07543 | 2.736 | 0.02756 | inf | 0.4325 | 2.1671553440683056e-13 | 2.1671553440683056e-13 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 5 | 71 | 30 | 2.367 | 2.502 | 0.4983 | 4.417 | 0.1128 | inf | 0.4245 | 5.098144129078719e-14 | 2.1671553440683056e-13 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 10 | 71 | 30 | 2.367 | 2.502 | 0.9928 | 6.264 | 0.1585 | inf | 0.4236 | 2.3249846492490177e-12 | 2.2961188506087638e-11 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 25 | 71 | 30 | 2.367 | 2.502 | 2.357 | 10.74 | 0.2196 | inf | 0.4212 | 7.534062262948283e-12 | 3.82982534574694e-11 |
| maze_13 | turn_articulation | turn_articulation | 1 | 71 | 36 | 1.972 | 1.263 | 0.07466 | 1.671 | 0.04468 | inf | 0.2715 | 1.7053025658242404e-13 | 1.7053025658242404e-13 |
| maze_13 | turn_articulation | turn_articulation | 5 | 71 | 36 | 1.972 | 1.263 | 0.5015 | 3.871 | 0.1296 | inf | 0.2722 | 4.1744385725905886e-14 | 1.7053025658242404e-13 |
| maze_13 | turn_articulation | turn_articulation | 10 | 71 | 36 | 1.972 | 1.263 | 0.9968 | 6.365 | 0.1566 | inf | 0.2734 | 2.320366121466577e-12 | 2.2961188506087638e-11 |
| maze_13 | turn_articulation | turn_articulation | 25 | 71 | 36 | 1.972 | 1.263 | 2.372 | 13.44 | 0.1765 | inf | 0.2768 | 7.243166066928097e-12 | 3.82982534574694e-11 |
