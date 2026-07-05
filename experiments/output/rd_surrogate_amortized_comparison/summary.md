# Amortized Multi-Task Compression

Generated: 2026-07-05T10:04:24
map_specs = ['maze:13']
methods = ['graph_rd_joint', 'graph_rd_surrogate_joint', 'betweenness_sqrt', 'turn_articulation']
task_counts = [1, 5, 10, 25, 50], max_tasks = 50
goal_source = boundary

A boundary set and first-boundary kernels are built once, then reused across many terminal-goal tasks.

| map | method_spec | method | task_count | n_states | n_boundary | state_compression_ratio | upfront_time_sec | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | break_even_task_count_estimate | backup_compression_ratio | start_gap_mean | start_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| maze_13 | graph_rd_joint | graph_rd_joint | 1 | 71 | 8 | 8.875 | 21.73 | 0.053 | 21.74 | 0.002438 | 469.5 | 14.93 | 1.1475265182525618e-12 | 1.1475265182525618e-12 |
| maze_13 | graph_rd_joint | graph_rd_joint | 5 | 71 | 8 | 8.875 | 21.73 | 0.3513 | 21.76 | 0.01615 | 335.9 | 24.38 | 2.3154811401582264e-13 | 1.1475265182525618e-12 |
| maze_13 | graph_rd_joint | graph_rd_joint | 7 | 71 | 8 | 8.875 | 21.73 | 0.4682 | 21.77 | 0.0215 | 355.3 | 22.6 | 5.107660326432649e-13 | 1.2221335055073723e-12 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 1 | 71 | 8 | 8.875 | 1.645 | 0.06513 | 1.652 | 0.03942 | 28.29 | 14.93 | 1.1475265182525618e-12 | 1.1475265182525618e-12 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 5 | 71 | 8 | 8.875 | 1.645 | 0.4288 | 1.673 | 0.2562 | 20.54 | 24.38 | 2.3154811401582264e-13 | 1.1475265182525618e-12 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 7 | 71 | 8 | 8.875 | 1.645 | 0.5711 | 1.686 | 0.3388 | 21.7 | 22.6 | 5.107660326432649e-13 | 1.2221335055073723e-12 |
| maze_13 | betweenness_sqrt | betweenness_9 | 1 | 71 | 9 | 7.889 | 0.1191 | 0.06505 | 0.1283 | 0.507 | 2.132 | 11 | 4.192202140984591e-13 | 4.192202140984591e-13 |
| maze_13 | betweenness_sqrt | betweenness_9 | 5 | 71 | 9 | 7.889 | 0.1191 | 0.3378 | 0.1711 | 1.975 | 2.084 | 10.01 | 1.2924772363476223e-12 | 6.036060540282051e-12 |
| maze_13 | betweenness_sqrt | betweenness_9 | 8 | 71 | 9 | 7.889 | 0.1191 | 0.5289 | 0.2015 | 2.625 | 2.134 | 9.896 | 3.771649659256582e-12 | 1.0690115459510707e-11 |
| maze_13 | turn_articulation | turn_articulation | 1 | 71 | 18 | 3.944 | 0.3906 | 0.06586 | 0.426 | 0.1546 | 12.84 | 2.733 | 1.1475265182525618e-12 | 1.1475265182525618e-12 |
| maze_13 | turn_articulation | turn_articulation | 5 | 71 | 18 | 3.944 | 0.3906 | 0.4301 | 0.642 | 0.6699 | 10.93 | 2.536 | 2.3439028495886303e-13 | 1.1475265182525618e-12 |
| maze_13 | turn_articulation | turn_articulation | 10 | 71 | 18 | 3.944 | 0.3906 | 0.8544 | 0.8944 | 0.9552 | 11.14 | 2.507 | 6.1694205300000246e-12 | 3.3427483003833913e-11 |
| maze_13 | turn_articulation | turn_articulation | 17 | 71 | 18 | 3.944 | 0.3906 | 1.413 | 1.224 | 1.154 | 11.47 | 2.509 | 8.201517896195047e-12 | 3.3427483003833913e-11 |
