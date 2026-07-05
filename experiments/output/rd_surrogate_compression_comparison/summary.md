# Compression Scaling

Generated: 2026-07-05T10:03:43
map_specs = ['corridor:64', 'maze:13']
methods = ['endpoints', 'betweenness_sqrt', 'graph_rd_joint', 'graph_rd_surrogate_joint', 'turn_articulation']
gamma = 0.97, slip = 0.05

Exact first-boundary kernels are built once, then graph/SMDP planning propagates value over compressed boundary vertices and option edges.

| map | method_spec | method | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | construction_time_sec | kernel_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | endpoints | 64 | 2 | 32 | 380 | 0.1032 | 8.483e-06 | 0.009129 | 9.98e-05 | 1035 | 11.18 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 64 | 8 | 8 | 8.837 | 0.1007 | 0.004111 | 0.08618 | 0.01943 | 5.183 | 0.9179 | 8.515 | 1.829647544582258e-11 | 0.0 | 0.0 |
| corridor_64 | graph_rd_joint | graph_rd_joint | 64 | 2 | 32 | 380 | 0.1017 | 0.2228 | 0.008825 | 8.872e-05 | 1147 | 0.439 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| corridor_64 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 64 | 2 | 32 | 380 | 0.101 | 0.2251 | 0.008902 | 8.713e-05 | 1160 | 0.4316 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| corridor_64 | turn_articulation | turn_articulation | 64 | 2 | 32 | 380 | 0.1013 | 0.0004947 | 0.008851 | 8.476e-05 | 1196 | 10.75 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| maze_13 | endpoints | endpoints | 71 | 2 | 35.5 | 422 | 0.06522 | 9.02e-06 | 0.01952 | 8.781e-05 | 742.7 | 3.325 | 3763 | 1.6697754290362354e-13 | 6 | 6 |
| maze_13 | betweenness_sqrt | betweenness_9 | 71 | 9 | 7.889 | 6.975 | 0.06513 | 0.005148 | 0.3801 | 0.009306 | 6.999 | 0.1651 | 11 | 4.192202140984591e-13 | 5 | 5 |
| maze_13 | graph_rd_joint | graph_rd_joint | 71 | 8 | 8.875 | 9.174 | 0.06593 | 21.33 | 0.2381 | 0.006804 | 9.691 | 0.003056 | 14.93 | 1.1475265182525618e-12 | 9.473e-08 | 9.473e-08 |
| maze_13 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 71 | 8 | 8.875 | 9.174 | 0.06899 | 1.536 | 0.2391 | 0.006766 | 10.2 | 0.03873 | 14.93 | 1.1475265182525618e-12 | 9.473e-08 | 9.473e-08 |
| maze_13 | turn_articulation | turn_articulation | 71 | 18 | 3.944 | 1.546 | 0.06549 | 0.0005332 | 0.4257 | 0.03565 | 1.837 | 0.1418 | 2.733 | 1.1475265182525618e-12 | 0.0 | 0.0 |
