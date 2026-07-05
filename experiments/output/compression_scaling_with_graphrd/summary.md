# Compression Scaling

Generated: 2026-07-05T09:50:07
map_specs = ['corridor:64', 'open_room:10', 'maze:13']
methods = ['endpoints', 'betweenness_sqrt', 'graph_rd_joint', 'turn_articulation']
gamma = 0.97, slip = 0.05

Exact first-boundary kernels are built once, then graph/SMDP planning propagates value over compressed boundary vertices and option edges.

| map | method_spec | method | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | construction_time_sec | kernel_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | endpoints | 64 | 2 | 32 | 380 | 0.1045 | 7.925e-06 | 0.009166 | 0.0001352 | 773 | 11.23 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 64 | 8 | 8 | 8.837 | 0.1053 | 0.004141 | 0.08756 | 0.01969 | 5.348 | 0.9455 | 8.515 | 1.829647544582258e-11 | 0.0 | 0.0 |
| corridor_64 | graph_rd_joint | graph_rd_joint | 64 | 2 | 32 | 380 | 0.1056 | 0.237 | 0.008945 | 9.039e-05 | 1169 | 0.4293 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| corridor_64 | turn_articulation | turn_articulation | 64 | 2 | 32 | 380 | 0.1047 | 0.0004795 | 0.008734 | 8.403e-05 | 1245 | 11.26 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| open_room_10 | endpoints | endpoints | 100 | 2 | 50 | 792 | 0.07591 | 1.427e-05 | 0.02057 | 8.709e-05 | 871.6 | 3.671 | 4300 | 0.07026 | 0.8664 | 0.8664 |
| open_room_10 | betweenness_sqrt | betweenness_10 | 100 | 10 | 10 | 2.636 | 0.0761 | 0.01244 | 0.3428 | 0.01785 | 4.263 | 0.204 | 6.59 | 0.07026 | 0.8664 | 0.3467 |
| open_room_10 | graph_rd_joint | graph_rd_joint | 100 | 2 | 50 | 792 | 0.07601 | 0.6061 | 0.0199 | 9.08e-05 | 837.1 | 0.1214 | 4300 | 0.07026 | 0.8664 | 0.8664 |
| open_room_10 | turn_articulation | turn_articulation | 100 | 4 | 25 | 79.2 | 0.07775 | 0.0009443 | 0.04769 | 0.0003951 | 196.8 | 1.586 | 358.3 | 0.07026 | 0.0 | 0.0 |
| maze_13 | endpoints | endpoints | 71 | 2 | 35.5 | 422 | 0.06686 | 1.217e-05 | 0.01947 | 8.967e-05 | 745.6 | 3.416 | 3763 | 1.6697754290362354e-13 | 6 | 6 |
| maze_13 | betweenness_sqrt | betweenness_9 | 71 | 9 | 7.889 | 6.975 | 0.06653 | 0.005229 | 0.3836 | 0.009256 | 7.187 | 0.1671 | 11 | 4.192202140984591e-13 | 5 | 5 |
| maze_13 | graph_rd_joint | graph_rd_joint | 71 | 8 | 8.875 | 9.174 | 0.06634 | 21.53 | 0.238 | 0.006835 | 9.706 | 0.003046 | 14.93 | 1.1475265182525618e-12 | 9.473e-08 | 9.473e-08 |
| maze_13 | turn_articulation | turn_articulation | 71 | 18 | 3.944 | 1.546 | 0.06705 | 0.000589 | 0.4313 | 0.03673 | 1.825 | 0.1431 | 2.733 | 1.1475265182525618e-12 | 0.0 | 0.0 |
