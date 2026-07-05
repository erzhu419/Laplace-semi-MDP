# Fair Budget Frontier

Generated: 2026-07-05T19:42:59

This table normalizes full-MDP, graph-RD, group-constrained RD, and option-discovery rows into the same rate/distortion frontier vocabulary. It is an aggregation layer; it does not rerun heavy experiments.

- total normalized rows: `121`
- Pareto non-dominated rows: `59`

## Method-Group Summary

| method_group | n_rows | pareto_rows | median_rate_budget_boundary_frac | median_state_compression_ratio | median_start_gap | median_hidden_audit | mean_group_feasible_rate | median_total_speedup | median_success_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline:dense_turn | 1 | 1 | 0.3704 | 2.7 | 2.901501261476369e-11 | 0.0 | 1 | nan | 1 |
| baseline:endpoints | 7 | 7 | 0.01923 | 52 | 2.921041186709772e-11 | 155.5 | 0.1429 | 2.759 | 1 |
| full_mdp | 10 | 5 | 1 | 1 | 0.0 | 0.0 | nan | 1 | 1 |
| option_baseline:bottleneck | 15 | 8 | 0.1875 | 5.333 | 1.4097167877480388e-11 | 2 | 1 | 0.3402 | 1 |
| option_baseline:coverage | 15 | 1 | 0.1875 | 5.333 | 2.9125146738806507e-11 | 2 | 1 | 0.4021 | 1 |
| option_baseline:eigen | 15 | 3 | 0.1875 | 5.333 | 2.332356530132529e-11 | 2.1 | 1 | 0.3368 | 1 |
| option_baseline:random | 15 | 1 | 0.1875 | 5.333 | 2.1433521624203422e-11 | 2 | 1 | 0.3465 | 1 |
| ours:group_rd | 22 | 14 | 0.05221 | 19.27 | 1.7967849430533533e-12 | 0.0 | 0.9545 | 0.01516 | 1 |
| ours:rd_graph | 21 | 19 | 0.125 | 8 | 1.9127810446661897e-11 | 0.0 | 1 | 0.1836 | 1 |

## Pareto Rows

| source | map | slip | method | method_group | n_states | n_boundary | rate_budget_boundary_frac | state_compression_ratio | start_gap | hidden_audit | success_rate | group_feasible | total_speedup | pareto_nondominated | pareto_dominated_by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_benchmark | corridor_16 | 0.0 | graph_rd_joint | ours:rd_graph | 16 | 2 | 0.125 | 8 | 1.7763568394002505e-15 | 0.0 | 1 | None | 0.2175 | True |  |
| core_benchmark | corridor_16 | 0.0 | graph_rd_surrogate_joint | ours:rd_graph | 16 | 2 | 0.125 | 8 | 1.7763568394002505e-15 | 0.0 | 1 | None | 0.2347 | True |  |
| core_benchmark | corridor_16 | 0.05 | full_vi | full_mdp | 16 | 16 | 1 | 1 | 0.0 | 0.0 | 1 | None | 1 | True |  |
| core_benchmark | corridor_16 | 0.05 | graph_rd_joint | ours:rd_graph | 16 | 2 | 0.125 | 8 | 3.809041970725957e-11 | 0.0 | 1 | None | 0.2973 | True |  |
| core_benchmark | corridor_16 | 0.05 | graph_rd_surrogate_joint | ours:rd_graph | 16 | 2 | 0.125 | 8 | 3.809041970725957e-11 | 0.0 | 1 | None | 0.2995 | True |  |
| core_benchmark | corridor_16 | 0.05 | eigenoptions_sqrt | option_baseline:eigen | 16 | 4 | 0.25 | 4 | 2.332356530132529e-11 | 0.0 | 1 | None | 0.8093 | True |  |
| core_benchmark | corridor_32 | 0.0 | graph_rd_joint | ours:rd_graph | 32 | 2 | 0.0625 | 16 | 0.0 | 0.0 | 1 | None | 0.2846 | True |  |
| core_benchmark | corridor_32 | 0.0 | graph_rd_surrogate_joint | ours:rd_graph | 32 | 2 | 0.0625 | 16 | 0.0 | 0.0 | 1 | None | 0.2722 | True |  |
| core_benchmark | corridor_32 | 0.05 | full_vi | full_mdp | 32 | 32 | 1 | 1 | 0.0 | 0.0 | 1 | None | 1 | True |  |
| core_benchmark | corridor_32 | 0.05 | graph_rd_joint | ours:rd_graph | 32 | 2 | 0.0625 | 16 | 2.091127271341975e-11 | 0.0 | 1 | None | 0.3238 | True |  |
| core_benchmark | corridor_32 | 0.05 | graph_rd_surrogate_joint | ours:rd_graph | 32 | 2 | 0.0625 | 16 | 2.091127271341975e-11 | 0.0 | 1 | None | 0.2872 | True |  |
| core_benchmark | corridor_32 | 0.05 | betweenness_sqrt | option_baseline:bottleneck | 32 | 6 | 0.1875 | 5.333 | 1.4097167877480388e-11 | 0.0 | 1 | None | 0.7568 | True |  |
| core_benchmark | open_room_7 | 0.0 | graph_rd_joint | ours:rd_graph | 49 | 2 | 0.04082 | 24.5 | 1.7763568394002505e-15 | 1 | 1 | None | 0.05947 | True |  |
| core_benchmark | open_room_7 | 0.0 | graph_rd_surrogate_joint | ours:rd_graph | 49 | 2 | 0.04082 | 24.5 | 1.7763568394002505e-15 | 1 | 1 | None | 0.1933 | True |  |
| core_benchmark | open_room_7 | 0.0 | group_constrained_rd | ours:group_rd | 49 | 3 | 0.06122 | 16.33 | 1.7763568394002505e-15 | 0.0 | 1 | True | 0.007836 | True |  |
| core_benchmark | open_room_7 | 0.05 | full_vi | full_mdp | 49 | 49 | 1 | 1 | 0.0 | 0.0 | 1 | None | 1 | True |  |
| core_benchmark | open_room_7 | 0.05 | graph_rd_surrogate_joint | ours:rd_graph | 49 | 2 | 0.04082 | 24.5 | 0.04973 | 0.8 | 1 | None | 0.2868 | True |  |
| core_benchmark | open_room_7 | 0.05 | eigenoptions_sqrt | option_baseline:eigen | 49 | 7 | 0.1429 | 7 | 0.04973 | 0.85 | 1 | None | 0.3432 | True |  |
| core_benchmark | open_room_7 | 0.05 | betweenness_sqrt | option_baseline:bottleneck | 49 | 7 | 0.1429 | 7 | 0.04973 | 0.9 | 1 | None | 0.3281 | True |  |
| core_benchmark | open_room_7 | 0.05 | coverage_sqrt | option_baseline:coverage | 49 | 7 | 0.1429 | 7 | 0.04973 | 0.0 | 1 | None | 0.4345 | True |  |
| core_benchmark | four_rooms_7 | 0.0 | graph_rd_joint | ours:rd_graph | 40 | 2 | 0.05 | 20 | 1.7763568394002505e-15 | 2 | 1 | None | 0.01433 | True |  |
| core_benchmark | four_rooms_7 | 0.0 | graph_rd_surrogate_joint | ours:rd_graph | 40 | 2 | 0.05 | 20 | 1.7763568394002505e-15 | 2 | 1 | None | 0.174 | True |  |
| core_benchmark | four_rooms_7 | 0.0 | eigenoptions_sqrt | option_baseline:eigen | 40 | 7 | 0.175 | 5.714 | 1.7763568394002505e-15 | 0.0 | 1 | None | 0.07351 | True |  |
| core_benchmark | four_rooms_7 | 0.0 | random_landmarks_sqrt | option_baseline:random | 40 | 7 | 0.175 | 5.714 | 1.7763568394002505e-15 | 0.0 | 1 | None | 0.07986 | True |  |
| core_benchmark | four_rooms_7 | 0.05 | full_vi | full_mdp | 40 | 40 | 1 | 1 | 0.0 | 0.0 | 1 | None | 1 | True |  |
| core_benchmark | four_rooms_7 | 0.05 | graph_rd_joint | ours:rd_graph | 40 | 6 | 0.15 | 6.667 | 0.02441 | 0.0 | 1 | None | 0.007696 | True |  |
| core_benchmark | four_rooms_7 | 0.05 | group_constrained_rd | ours:group_rd | 40 | 5 | 0.125 | 8 | 0.002126 | 1 | 1 | True | 0.004379 | True |  |
| core_benchmark | maze_9 | 0.0 | graph_rd_joint | ours:rd_graph | 31 | 5 | 0.1613 | 6.2 | 1.7763568394002505e-15 | 0.0 | 1 | None | 0.0045 | True |  |
| core_benchmark | maze_9 | 0.0 | graph_rd_surrogate_joint | ours:rd_graph | 31 | 5 | 0.1613 | 6.2 | 1.7763568394002505e-15 | 0.0 | 1 | None | 0.03686 | True |  |
| core_benchmark | maze_9 | 0.0 | group_constrained_rd | ours:group_rd | 31 | 3 | 0.09677 | 10.33 | 1.7763568394002505e-15 | 3 | 1 | True | 0.01022 | True |  |
| core_benchmark | maze_9 | 0.05 | full_vi | full_mdp | 31 | 31 | 1 | 1 | 0.0 | 0.0 | 1 | None | 1 | True |  |
| core_benchmark | maze_9 | 0.05 | graph_rd_joint | ours:rd_graph | 31 | 5 | 0.1613 | 6.2 | 1.9127810446661897e-11 | 0.0 | 1 | None | 0.01015 | True |  |
| core_benchmark | maze_9 | 0.05 | graph_rd_surrogate_joint | ours:rd_graph | 31 | 5 | 0.1613 | 6.2 | 1.9127810446661897e-11 | 0.0 | 1 | None | 0.06558 | True |  |
| core_benchmark | maze_9 | 0.05 | group_constrained_rd | ours:group_rd | 31 | 3 | 0.09677 | 10.33 | 3.5864644587491057e-12 | 3 | 1 | True | 0.01795 | True |  |
| core_benchmark | maze_9 | 0.05 | betweenness_sqrt | option_baseline:bottleneck | 31 | 6 | 0.1935 | 5.167 | 7.052136652418994e-12 | 2 | 1 | None | 0.3524 | True |  |
| group_constrained_adaptive | open_room_12 | 0.0 | endpoints | baseline:endpoints | 144 | 2 | 0.01389 | 72 | 3.552713678800501e-15 | 155.5 | nan | False | 2.343 | True |  |
| group_constrained_adaptive | open_room_12 | 0.0 | group_constrained | ours:group_rd | 144 | 3 | 0.02083 | 48 | 3.552713678800501e-15 | 0.0 | nan | True | 0.01595 | True |  |
| group_constrained_adaptive | open_room_12 | 0.0 | group_constrained_incremental | ours:group_rd | 144 | 3 | 0.02083 | 48 | 3.552713678800501e-15 | 0.0 | nan | True | 0.04026 | True |  |
| group_constrained_adaptive | open_room_12 | 0.05 | endpoints | baseline:endpoints | 144 | 2 | 0.01389 | 72 | 0.07851 | 233.2 | nan | False | 4.457 | True |  |
| group_constrained_adaptive | open_room_12 | 0.05 | group_constrained | ours:group_rd | 144 | 4 | 0.02778 | 36 | 0.07851 | 0.0 | nan | True | 0.007959 | True |  |
| group_constrained_adaptive | open_room_12 | 0.05 | group_constrained_incremental | ours:group_rd | 144 | 4 | 0.02778 | 36 | 0.07851 | 0.0 | nan | True | 0.02364 | True |  |
| group_constrained_adaptive | four_rooms_11 | 0.0 | endpoints | baseline:endpoints | 104 | 2 | 0.01923 | 52 | 5.329070518200751e-15 | 155.5 | nan | False | 1.882 | True |  |
| group_constrained_adaptive | four_rooms_11 | 0.0 | group_constrained | ours:group_rd | 104 | 3 | 0.02885 | 34.67 | 5.329070518200751e-15 | 0.0 | nan | True | 0.01743 | True |  |
| group_constrained_adaptive | four_rooms_11 | 0.0 | group_constrained_incremental | ours:group_rd | 104 | 3 | 0.02885 | 34.67 | 5.329070518200751e-15 | 0.0 | nan | True | 0.03831 | True |  |
| group_constrained_adaptive | four_rooms_11 | 0.05 | endpoints | baseline:endpoints | 104 | 2 | 0.01923 | 52 | 0.05768 | 233.2 | nan | False | 3.134 | True |  |
| group_constrained_adaptive | four_rooms_11 | 0.05 | group_constrained | ours:group_rd | 104 | 4 | 0.03846 | 26 | 0.05768 | 0.0 | nan | True | 0.008062 | True |  |
| group_constrained_adaptive | four_rooms_11 | 0.05 | group_constrained_incremental | ours:group_rd | 104 | 5 | 0.04808 | 20.8 | 0.05768 | 0.0 | nan | True | 0.01779 | True |  |
| group_constrained_adaptive | maze_13 | 0.0 | endpoints | baseline:endpoints | 71 | 2 | 0.02817 | 35.5 | 7.105427357601002e-15 | 155.5 | nan | False | 2.384 | True |  |
| group_constrained_adaptive | maze_13 | 0.0 | group_constrained_incremental | ours:group_rd | 71 | 3 | 0.04225 | 23.67 | 7.105427357601002e-15 | 0.0 | nan | True | 0.04848 | True |  |
| group_constrained_adaptive | maze_13 | 0.05 | endpoints | baseline:endpoints | 71 | 2 | 0.02817 | 35.5 | 1.548e-08 | 233.2 | nan | False | 3.348 | True |  |
| group_constrained_adaptive | maze_13 | 0.05 | group_constrained_incremental | ours:group_rd | 71 | 3 | 0.04225 | 23.67 | 2.733e-07 | 0.0 | nan | True | 0.05848 | True |  |
| option_baseline_frontier | maze | 0.05 | betweenness_4 | option_baseline:bottleneck | 81 | 4 | 0.04938 | 20.25 | 2.921041186709772e-11 | 11 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | betweenness_8 | option_baseline:bottleneck | 81 | 8 | 0.09877 | 10.12 | 2.5359270239277976e-11 | 9.12 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | betweenness_12 | option_baseline:bottleneck | 81 | 12 | 0.1481 | 6.75 | 2.0179413695586845e-11 | 7.22 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | betweenness_16 | option_baseline:bottleneck | 81 | 16 | 0.1975 | 5.062 | 1.9397816686250735e-11 | 7.02 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | betweenness_24 | option_baseline:bottleneck | 81 | 24 | 0.2963 | 3.375 | 1.2143175354140112e-11 | 5.1 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | endpoints | baseline:endpoints | 81 | 2 | 0.02469 | 40.5 | 2.921041186709772e-11 | 11.11 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | graph_rd_joint | ours:rd_graph | 81 | 24 | 0.2963 | 3.375 | 2.9022118042121292e-11 | 2.04 | 1 | True | nan | True |  |
| option_baseline_frontier | maze | 0.05 | turn_articulation | baseline:dense_turn | 81 | 30 | 0.3704 | 2.7 | 2.901501261476369e-11 | 0.0 | 1 | True | nan | True |  |

## Source Artifacts

- core benchmark: `experiments/output/core_benchmark/core_benchmark.csv`
- group-constrained adaptive: `experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv`
- option baseline frontier: `experiments/output/option_baseline_frontier_maze_slip005/frontier_all.csv`
