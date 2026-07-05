# Amortized Multi-Task Compression

Generated: 2026-07-05T09:51:04
map_specs = ['corridor:64', 'maze:13']
methods = ['endpoints', 'betweenness_sqrt', 'graph_rd_joint', 'turn_articulation']
task_counts = [1, 5, 10, 25, 50], max_tasks = 50
goal_source = boundary

A boundary set and first-boundary kernels are built once, then reused across many terminal-goal tasks.

| map | method_spec | method | task_count | n_states | n_boundary | state_compression_ratio | upfront_time_sec | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | break_even_task_count_estimate | backup_compression_ratio | start_gap_mean | start_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | endpoints | 1 | 64 | 2 | 32 | 0.009113 | 0.0799 | 0.009282 | 8.609 | 0.1143 | 6080 | 3.375077994860476e-11 | 3.375077994860476e-11 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 1 | 64 | 8 | 8 | 0.08404 | 0.1012 | 0.1052 | 0.9614 | 1.051 | 8.515 | 1.829647544582258e-11 | 1.829647544582258e-11 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 5 | 64 | 8 | 8 | 0.08404 | 0.3466 | 0.1335 | 2.597 | 1.414 | 12.07 | 7.775469157422776e-12 | 1.829647544582258e-11 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 7 | 64 | 8 | 8 | 0.08404 | 0.471 | 0.1485 | 3.171 | 1.447 | 12.44 | 1.3830206821044806e-11 | 3.057465391975711e-11 |
| corridor_64 | graph_rd_joint | graph_rd_joint | 1 | 64 | 2 | 32 | 0.2319 | 0.1028 | 0.2321 | 0.4429 | 2.26 | 6080 | 3.375077994860476e-11 | 3.375077994860476e-11 |
| corridor_64 | turn_articulation | turn_articulation | 1 | 64 | 2 | 32 | 0.009027 | 0.1008 | 0.009192 | 10.97 | 0.08968 | 6080 | 3.375077994860476e-11 | 3.375077994860476e-11 |
| maze_13 | endpoints | endpoints | 1 | 71 | 2 | 35.5 | 0.01026 | 0.05132 | 0.01041 | 4.932 | 0.2004 | 3763 | 1.6697754290362354e-13 | 1.6697754290362354e-13 |
| maze_13 | betweenness_sqrt | betweenness_9 | 1 | 71 | 9 | 7.889 | 0.1197 | 0.06636 | 0.129 | 0.5144 | 2.098 | 11 | 4.192202140984591e-13 | 4.192202140984591e-13 |
| maze_13 | betweenness_sqrt | betweenness_9 | 5 | 71 | 9 | 7.889 | 0.1197 | 0.34 | 0.1723 | 1.973 | 2.083 | 10.01 | 1.2924772363476223e-12 | 6.036060540282051e-12 |
| maze_13 | betweenness_sqrt | betweenness_9 | 8 | 71 | 9 | 7.889 | 0.1197 | 0.5308 | 0.2028 | 2.617 | 2.139 | 9.896 | 3.771649659256582e-12 | 1.0690115459510707e-11 |
| maze_13 | graph_rd_joint | graph_rd_joint | 1 | 71 | 8 | 8.875 | 21.41 | 0.06348 | 21.42 | 0.002964 | 377.2 | 14.93 | 1.1475265182525618e-12 | 1.1475265182525618e-12 |
| maze_13 | graph_rd_joint | graph_rd_joint | 5 | 71 | 8 | 8.875 | 21.41 | 0.4152 | 21.44 | 0.01937 | 276.2 | 24.38 | 2.3154811401582264e-13 | 1.1475265182525618e-12 |
| maze_13 | graph_rd_joint | graph_rd_joint | 7 | 71 | 8 | 8.875 | 21.41 | 0.5522 | 21.45 | 0.02575 | 292.3 | 22.6 | 5.107660326432649e-13 | 1.2221335055073723e-12 |
| maze_13 | turn_articulation | turn_articulation | 1 | 71 | 18 | 3.944 | 0.3812 | 0.06369 | 0.4165 | 0.1529 | 13.4 | 2.733 | 1.1475265182525618e-12 | 1.1475265182525618e-12 |
| maze_13 | turn_articulation | turn_articulation | 5 | 71 | 18 | 3.944 | 0.3812 | 0.4189 | 0.6294 | 0.6656 | 11.16 | 2.536 | 2.3439028495886303e-13 | 1.1475265182525618e-12 |
| maze_13 | turn_articulation | turn_articulation | 10 | 71 | 18 | 3.944 | 0.3812 | 0.8466 | 0.8885 | 0.9528 | 11.23 | 2.507 | 6.1694205300000246e-12 | 3.3427483003833913e-11 |
| maze_13 | turn_articulation | turn_articulation | 17 | 71 | 18 | 3.944 | 0.3812 | 1.406 | 1.22 | 1.153 | 11.41 | 2.509 | 8.201517896195047e-12 | 3.3427483003833913e-11 |
