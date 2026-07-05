# Amortized Multi-Task Compression

Generated: 2026-07-05T09:41:54
map_specs = ['corridor:64', 'maze:13']
methods = ['endpoints', 'betweenness_sqrt', 'turn_articulation']
task_counts = [1, 5, 10, 25, 50], max_tasks = 50
goal_source = boundary

A boundary set and first-boundary kernels are built once, then reused across many terminal-goal tasks.

| map | method_spec | method | task_count | n_states | n_boundary | state_compression_ratio | upfront_time_sec | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | break_even_task_count_estimate | backup_compression_ratio | start_gap_mean | start_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | endpoints | 1 | 64 | 2 | 32 | 0.009264 | 0.08053 | 0.009438 | 8.533 | 0.1153 | 6080 | 3.375077994860476e-11 | 3.375077994860476e-11 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 1 | 64 | 8 | 8 | 0.08462 | 0.1003 | 0.1042 | 0.9623 | 1.049 | 8.515 | 1.829647544582258e-11 | 1.829647544582258e-11 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 5 | 64 | 8 | 8 | 0.08462 | 0.3498 | 0.1324 | 2.642 | 1.401 | 12.07 | 7.775469157422776e-12 | 1.829647544582258e-11 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 7 | 64 | 8 | 8 | 0.08462 | 0.4756 | 0.1476 | 3.223 | 1.436 | 12.44 | 1.3830206821044806e-11 | 3.057465391975711e-11 |
| corridor_64 | turn_articulation | turn_articulation | 1 | 64 | 2 | 32 | 0.009099 | 0.1 | 0.009254 | 10.81 | 0.0911 | 6080 | 3.375077994860476e-11 | 3.375077994860476e-11 |
| maze_13 | endpoints | endpoints | 1 | 71 | 2 | 35.5 | 0.01018 | 0.05092 | 0.01034 | 4.924 | 0.2006 | 3763 | 1.6697754290362354e-13 | 1.6697754290362354e-13 |
| maze_13 | betweenness_sqrt | betweenness_9 | 1 | 71 | 9 | 7.889 | 0.119 | 0.06307 | 0.1293 | 0.4877 | 2.256 | 11 | 4.192202140984591e-13 | 4.192202140984591e-13 |
| maze_13 | betweenness_sqrt | betweenness_9 | 5 | 71 | 9 | 7.889 | 0.119 | 0.3248 | 0.1725 | 1.884 | 2.193 | 10.01 | 1.2924772363476223e-12 | 6.036060540282051e-12 |
| maze_13 | betweenness_sqrt | betweenness_9 | 8 | 71 | 9 | 7.889 | 0.119 | 0.5096 | 0.2033 | 2.507 | 2.238 | 9.896 | 3.771649659256582e-12 | 1.0690115459510707e-11 |
| maze_13 | turn_articulation | turn_articulation | 1 | 71 | 18 | 3.944 | 0.3973 | 0.06777 | 0.4332 | 0.1564 | 12.49 | 2.733 | 1.1475265182525618e-12 | 1.1475265182525618e-12 |
| maze_13 | turn_articulation | turn_articulation | 5 | 71 | 18 | 3.944 | 0.3973 | 0.4226 | 0.6493 | 0.6509 | 11.64 | 2.536 | 2.3439028495886303e-13 | 1.1475265182525618e-12 |
| maze_13 | turn_articulation | turn_articulation | 10 | 71 | 18 | 3.944 | 0.3973 | 0.8436 | 0.9091 | 0.928 | 11.97 | 2.507 | 6.1694205300000246e-12 | 3.3427483003833913e-11 |
| maze_13 | turn_articulation | turn_articulation | 17 | 71 | 18 | 3.944 | 0.3973 | 1.394 | 1.243 | 1.121 | 12.33 | 2.509 | 8.201517896195047e-12 | 3.3427483003833913e-11 |
