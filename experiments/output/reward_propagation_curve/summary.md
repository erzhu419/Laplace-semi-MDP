# Reward Propagation Curve

Generated: 2026-07-05T09:42:37
map_specs = ['corridor:64', 'maze:13']
methods = ['endpoints', 'betweenness_sqrt', 'turn_articulation']
record_points = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]

Rows in the CSV contain the full curve. The table below shows each planner's final recorded point.

| map | planner | method_spec | method | n_states | n_boundary | state_compression_ratio | iteration | planning_backup_count | planning_time_sec | start_value_error | final_start_gap_floor | occupancy_struct_hidden_distinct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | full_vi | full_mdp | full_mdp | 64 | 64 | 1 | 95 | 24320 | 0.08068 | 0.0 | 0.0 | 0.0 |
| corridor_64 | graph_smdp | endpoints | endpoints | 64 | 2 | 32 | 2 | 4 | 8.728e-05 | 3.375077994860476e-11 | 3.375077994860476e-11 | 0.0 |
| corridor_64 | graph_smdp | betweenness_sqrt | betweenness_8 | 64 | 8 | 8 | 51 | 2856 | 0.01901 | 1.829647544582258e-11 | 1.829647544582258e-11 | 0.0 |
| corridor_64 | graph_smdp | turn_articulation | turn_articulation | 64 | 2 | 32 | 2 | 4 | 8.305e-05 | 3.375077994860476e-11 | 3.375077994860476e-11 | 0.0 |
| maze_13 | full_vi | full_mdp | full_mdp | 71 | 71 | 1 | 53 | 15052 | 0.05088 | 0.0 | 0.0 | 0.0 |
| maze_13 | graph_smdp | endpoints | endpoints | 71 | 2 | 35.5 | 2 | 4 | 9.034e-05 | 1.6697754290362354e-13 | 1.6697754290362354e-13 | 6 |
| maze_13 | graph_smdp | betweenness_sqrt | betweenness_9 | 71 | 9 | 7.889 | 19 | 1368 | 0.00927 | 4.192202140984591e-13 | 4.192202140984591e-13 | 5 |
| maze_13 | graph_smdp | turn_articulation | turn_articulation | 71 | 18 | 3.944 | 18 | 5508 | 0.03638 | 1.1475265182525618e-12 | 1.1475265182525618e-12 | 0.0 |
