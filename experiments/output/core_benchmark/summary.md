# Core Benchmark

Generated: 2026-07-05T12:45:28
map_specs = ['corridor:16,32', 'open_room:7', 'four_rooms:7', 'maze:9']
slips = [0.0, 0.05]
methods = ['full_vi', 'graph_rd_joint', 'graph_rd_surrogate_joint', 'group_constrained_rd', 'eigenoptions_sqrt', 'betweenness_sqrt', 'random_landmarks_sqrt', 'coverage_sqrt']
gamma = 0.97, n_rollouts = 20

This table evaluates full MDP value iteration and graph-SMDP planning under the same map/slip suite. Graph rows include boundary construction, exact first-boundary kernels, SMDP solve cost, value gap, and hidden-boundary audit metrics.

- best planning-only speedup over full VI in this run: `295.4x`
- worst graph start-value gap in this run: `0.04973`

| map | slip | method_spec | method | n_states | n_boundary | state_compression_ratio | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | value_gap_max | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | success_rate | primitive_steps_mean | hidden_audit_distinct_mean | group_all_feasible | group_test_bits_cvar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_16 | 0.0 | full_vi | full_vi | 16 | 16 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| corridor_16 | 0.0 | graph_rd_joint | graph_rd_joint | 16 | 2 | 8 | 42.03 | 0.2175 | 256 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 15 | 0.0 |  |  |
| corridor_16 | 0.0 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 16 | 2 | 8 | 44.38 | 0.2347 | 256 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 15 | 0.0 |  |  |
| corridor_16 | 0.0 | group_constrained_rd | group_constrained_rd | 16 | 3 | 5.333 | 18.36 | 0.01437 | 56.89 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 15 | 0.0 | True | 0.0 |
| corridor_16 | 0.0 | eigenoptions_sqrt | eigenoptions_4 | 16 | 4 | 4 | 2.434 | 0.417 | 5.333 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 15 | 0.0 |  |  |
| corridor_16 | 0.0 | betweenness_sqrt | betweenness_4 | 16 | 4 | 4 | 3.947 | 0.4363 | 8.533 | 0.0 | 8.881784197001252e-16 | 0.0 | 0.0 | 1 | 15 | 0.0 |  |  |
| corridor_16 | 0.0 | random_landmarks_sqrt | random_landmarks_4 | 16 | 4 | 4 | 3.201 | 0.4448 | 7.758 | 0.0 | 0.0 | 0.0 | 0.0 | 1 | 15 | 0.0 |  |  |
| corridor_16 | 0.0 | coverage_sqrt | coverage_4 | 16 | 4 | 4 | 9.37 | 0.468 | 21.33 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 15 | 0.0 |  |  |
| corridor_16 | 0.05 | full_vi | full_vi | 16 | 16 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| corridor_16 | 0.05 | graph_rd_joint | graph_rd_joint | 16 | 2 | 8 | 100.3 | 0.2973 | 576 | 3.809041970725957e-11 | 3.809041970725957e-11 | 0.0 | 0.0 | 1 | 16.15 | 0.0 |  |  |
| corridor_16 | 0.05 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 16 | 2 | 8 | 100.2 | 0.2995 | 576 | 3.809041970725957e-11 | 3.809041970725957e-11 | 0.0 | 0.0 | 1 | 15.8 | 0.0 |  |  |
| corridor_16 | 0.05 | group_constrained_rd | group_constrained_rd | 16 | 3 | 5.333 | 41.27 | 0.01742 | 128 | 3.808686699358077e-11 | 3.808686699358077e-11 | 0.0 | 0.0 | 1 | 16.2 | 0.0 | True | 0.0 |
| corridor_16 | 0.05 | eigenoptions_sqrt | eigenoptions_4 | 16 | 4 | 4 | 3.26 | 0.8093 | 7.385 | 2.332356530132529e-11 | 2.332356530132529e-11 | 0.0 | 0.0 | 1 | 16.35 | 0.0 |  |  |
| corridor_16 | 0.05 | betweenness_sqrt | betweenness_4 | 16 | 4 | 4 | 4.226 | 0.8069 | 9.6 | 2.4725110847612086e-11 | 2.4725110847612086e-11 | 0.0 | 0.0 | 1 | 15.55 | 0.0 |  |  |
| corridor_16 | 0.05 | random_landmarks_sqrt | random_landmarks_4 | 16 | 4 | 4 | 5.647 | 0.9387 | 12.8 | 3.803357628839876e-11 | 3.803357628839876e-11 | 0.0 | 0.0 | 1 | 15.9 | 0.0 |  |  |
| corridor_16 | 0.05 | coverage_sqrt | coverage_4 | 16 | 4 | 4 | 11.43 | 0.9808 | 32 | 3.807265613886557e-11 | 3.807265613886557e-11 | 0.0 | 0.0 | 1 | 16.1 | 0.0 |  |  |
| corridor_32 | 0.0 | full_vi | full_vi | 32 | 32 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| corridor_32 | 0.0 | graph_rd_joint | graph_rd_joint | 32 | 2 | 16 | 147.7 | 0.2846 | 1024 | 0.0 | 0.0 | 0.0 | 0.0 | 1 | 31 | 0.0 |  |  |
| corridor_32 | 0.0 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 32 | 2 | 16 | 157.2 | 0.2722 | 1024 | 0.0 | 0.0 | 0.0 | 0.0 | 1 | 31 | 0.0 |  |  |
| corridor_32 | 0.0 | group_constrained_rd | group_constrained_rd | 32 | 3 | 10.67 | 76.56 | 0.01095 | 227.6 | 0.0 | 0.0 | 0.0 | 0.0 | 1 | 31 | 0.0 | True | 0.0 |
| corridor_32 | 0.0 | eigenoptions_sqrt | eigenoptions_6 | 32 | 6 | 5.333 | 2.048 | 0.4351 | 4.267 | 0.0 | 3.552713678800501e-15 | 0.0 | 0.0 | 1 | 31 | 0.0 |  |  |
| corridor_32 | 0.0 | betweenness_sqrt | betweenness_6 | 32 | 6 | 5.333 | 3.413 | 0.4433 | 7.186 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 31 | 0.0 |  |  |
| corridor_32 | 0.0 | random_landmarks_sqrt | random_landmarks_6 | 32 | 6 | 5.333 | 2.101 | 0.441 | 4.267 | 0.0 | 3.552713678800501e-15 | 0.0 | 0.0 | 1 | 31 | 0.0 |  |  |
| corridor_32 | 0.0 | coverage_sqrt | coverage_6 | 32 | 6 | 5.333 | 7.885 | 0.498 | 17.07 | 3.552713678800501e-15 | 7.105427357601002e-15 | 0.0 | 0.0 | 1 | 31 | 0.0 |  |  |
| corridor_32 | 0.05 | full_vi | full_vi | 32 | 32 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| corridor_32 | 0.05 | graph_rd_joint | graph_rd_joint | 32 | 2 | 16 | 295.4 | 0.3238 | 1824 | 2.091127271341975e-11 | 2.091127271341975e-11 | 0.0 | 0.0 | 1 | 33 | 0.0 |  |  |
| corridor_32 | 0.05 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 32 | 2 | 16 | 294.6 | 0.2872 | 1824 | 2.091127271341975e-11 | 2.091127271341975e-11 | 0.0 | 0.0 | 1 | 33.75 | 0.0 |  |  |
| corridor_32 | 0.05 | group_constrained_rd | group_constrained_rd | 32 | 3 | 10.67 | 135 | 0.01854 | 405.3 | 2.091127271341975e-11 | 2.091127271341975e-11 | 0.0 | 0.0 | 1 | 32.9 | 0.0 | True | 0.02509 |
| corridor_32 | 0.05 | eigenoptions_sqrt | eigenoptions_6 | 32 | 6 | 5.333 | 2.775 | 0.6969 | 5.656 | 1.8953727476400672e-11 | 1.8953727476400672e-11 | 0.0 | 0.0 | 1 | 33.1 | 0.0 |  |  |
| corridor_32 | 0.05 | betweenness_sqrt | betweenness_6 | 32 | 6 | 5.333 | 3.667 | 0.7568 | 7.37 | 1.4097167877480388e-11 | 1.4097167877480388e-11 | 0.0 | 0.0 | 1 | 34.55 | 0.0 |  |  |
| corridor_32 | 0.05 | random_landmarks_sqrt | random_landmarks_6 | 32 | 6 | 5.333 | 13.05 | 0.9301 | 27.02 | 2.091127271341975e-11 | 2.091127271341975e-11 | 0.0 | 0.0 | 1 | 33.1 | 0.0 |  |  |
| corridor_32 | 0.05 | coverage_sqrt | coverage_6 | 32 | 6 | 5.333 | 11.79 | 0.9013 | 24.32 | 2.0875745576631743e-11 | 2.0875745576631743e-11 | 0.0 | 0.0 | 1 | 32.95 | 0.0 |  |  |
| open_room_7 | 0.0 | full_vi | full_vi | 49 | 49 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| open_room_7 | 0.0 | graph_rd_joint | graph_rd_joint | 49 | 2 | 24.5 | 107.2 | 0.05947 | 637 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1 | 1 | 1 | 12 | 1 |  |  |
| open_room_7 | 0.0 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 49 | 2 | 24.5 | 104.9 | 0.1933 | 637 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1 | 1 | 1 | 12 | 1 |  |  |
| open_room_7 | 0.0 | group_constrained_rd | group_constrained_rd | 49 | 3 | 16.33 | 31.81 | 0.007836 | 84.93 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 1 | 1 | 12 | 0.0 | True | 0.0 |
| open_room_7 | 0.0 | eigenoptions_sqrt | eigenoptions_7 | 49 | 7 | 7 | 3.387 | 0.1365 | 6.741 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 1 | 1 | 12 | 0.0 |  |  |
| open_room_7 | 0.0 | betweenness_sqrt | betweenness_7 | 49 | 7 | 7 | 3.459 | 0.1209 | 6.741 | 0.0 | 8.881784197001252e-16 | 0.0 | 0.6667 | 1 | 12 | 0.0 |  |  |
| open_room_7 | 0.0 | random_landmarks_sqrt | random_landmarks_7 | 49 | 7 | 7 | 5.72 | 0.1535 | 12.13 | 0.0 | 8.881784197001252e-16 | 0.0 | 0.6667 | 1 | 12 | 0.0 |  |  |
| open_room_7 | 0.0 | coverage_sqrt | coverage_7 | 49 | 7 | 7 | 6.02 | 0.1654 | 12.13 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 12 | 0.0 |  |  |
| open_room_7 | 0.05 | full_vi | full_vi | 49 | 49 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| open_room_7 | 0.05 | graph_rd_joint | graph_rd_joint | 49 | 2 | 24.5 | 289.9 | 0.09814 | 1715 | 0.04973 | 0.04973 | 0.9067 | 0.9067 | 1 | 12.35 | 0.9 |  |  |
| open_room_7 | 0.05 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 49 | 2 | 24.5 | 277.8 | 0.2868 | 1715 | 0.04973 | 0.04973 | 0.9067 | 0.9067 | 1 | 12.6 | 0.8 |  |  |
| open_room_7 | 0.05 | group_constrained_rd | group_constrained_rd | 49 | 2 | 24.5 | 231.6 | 0.003189 | 1715 | 0.04973 | 0.04973 | 0.9067 | 0.9067 | 1 | 13.65 | 0.95 | False | 77.73 |
| open_room_7 | 0.05 | eigenoptions_sqrt | eigenoptions_7 | 49 | 7 | 7 | 4.446 | 0.3432 | 9.074 | 0.04973 | 0.05947 | 0.9229 | 0.9014 | 1 | 12.95 | 0.85 |  |  |
| open_room_7 | 0.05 | betweenness_sqrt | betweenness_7 | 49 | 7 | 7 | 3.363 | 0.3281 | 7.101 | 0.04973 | 0.04973 | 0.9067 | 0.6054 | 1 | 12.6 | 0.9 |  |  |
| open_room_7 | 0.05 | random_landmarks_sqrt | random_landmarks_7 | 49 | 7 | 7 | 4.672 | 0.3534 | 9.074 | 0.04973 | 0.05559 | 0.9067 | 0.9561 | 1 | 12.65 | 1 |  |  |
| open_room_7 | 0.05 | coverage_sqrt | coverage_7 | 49 | 7 | 7 | 10.11 | 0.4345 | 20.42 | 0.04973 | 0.05497 | 0.0 | 0.0 | 1 | 12.75 | 0.0 |  |  |
| four_rooms_7 | 0.0 | full_vi | full_vi | 40 | 40 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| four_rooms_7 | 0.0 | graph_rd_joint | graph_rd_joint | 40 | 2 | 20 | 82.99 | 0.01433 | 520 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 2 | 2 | 1 | 12 | 2 |  |  |
| four_rooms_7 | 0.0 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 40 | 2 | 20 | 85 | 0.174 | 520 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 2 | 2 | 1 | 12 | 2 |  |  |
| four_rooms_7 | 0.0 | group_constrained_rd | group_constrained_rd | 40 | 3 | 13.33 | 15.41 | 0.01137 | 49.52 | 0.0 | 1.7763568394002505e-15 | 2 | 2 | 1 | 12 | 2 | True | 0.0 |
| four_rooms_7 | 0.0 | eigenoptions_sqrt | eigenoptions_7 | 40 | 7 | 5.714 | 3.709 | 0.07351 | 7.075 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 1 | 1 | 12 | 0.0 |  |  |
| four_rooms_7 | 0.0 | betweenness_sqrt | betweenness_7 | 40 | 7 | 5.714 | 3.503 | 0.06992 | 7.075 | 0.0 | 8.881784197001252e-16 | 2 | 1 | 1 | 12 | 2 |  |  |
| four_rooms_7 | 0.0 | random_landmarks_sqrt | random_landmarks_7 | 40 | 7 | 5.714 | 3.536 | 0.07986 | 7.075 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 1 | 1 | 12 | 0.0 |  |  |
| four_rooms_7 | 0.0 | coverage_sqrt | coverage_7 | 40 | 7 | 5.714 | 5.964 | 0.0779 | 12.38 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1 | 1 | 1 | 12 | 1 |  |  |
| four_rooms_7 | 0.05 | full_vi | full_vi | 40 | 40 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| four_rooms_7 | 0.05 | graph_rd_joint | graph_rd_joint | 40 | 6 | 6.667 | 7.804 | 0.007696 | 15.56 | 0.02441 | 0.02543 | 0.0723 | 1.537 | 1 | 12.5 | 0.0 |  |  |
| four_rooms_7 | 0.05 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 40 | 6 | 6.667 | 7.495 | 0.08115 | 15.56 | 0.02441 | 0.02543 | 0.07206 | 1.493 | 1 | 12.65 | 0.05 |  |  |
| four_rooms_7 | 0.05 | group_constrained_rd | group_constrained_rd | 40 | 5 | 8 | 6.316 | 0.004379 | 13.33 | 0.002126 | 0.02499 | 1.137 | 1.999 | 1 | 13 | 1 | True | 0.0 |
| four_rooms_7 | 0.05 | eigenoptions_sqrt | eigenoptions_7 | 40 | 7 | 5.714 | 5.993 | 0.1873 | 12.12 | 0.02441 | 0.025 | 2.058 | 1.055 | 1 | 12.8 | 2.1 |  |  |
| four_rooms_7 | 0.05 | betweenness_sqrt | betweenness_7 | 40 | 7 | 5.714 | 5.102 | 0.1828 | 10.26 | 0.02427 | 0.02852 | 1.173 | 1.054 | 1 | 12.9 | 1.25 |  |  |
| four_rooms_7 | 0.05 | random_landmarks_sqrt | random_landmarks_7 | 40 | 7 | 5.714 | 5.115 | 0.2031 | 10.26 | 0.02441 | 0.0276 | 2.056 | 1.071 | 1 | 12.85 | 2.1 |  |  |
| four_rooms_7 | 0.05 | coverage_sqrt | coverage_7 | 40 | 7 | 5.714 | 9.513 | 0.2036 | 19.05 | 0.02441 | 0.05439 | 2.056 | 1.071 | 1 | 12.55 | 2 |  |  |
| maze_9 | 0.0 | full_vi | full_vi | 31 | 31 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| maze_9 | 0.0 | graph_rd_joint | graph_rd_joint | 31 | 5 | 6.2 | 5.861 | 0.0045 | 11.51 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 12 | 0.0 |  |  |
| maze_9 | 0.0 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 31 | 5 | 6.2 | 5.794 | 0.03686 | 11.51 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.0 | 0.0 | 1 | 12 | 0.0 |  |  |
| maze_9 | 0.0 | group_constrained_rd | group_constrained_rd | 31 | 3 | 10.33 | 8.633 | 0.01022 | 20.67 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 3 | 3 | 1 | 12 | 3 | True | 0.0 |
| maze_9 | 0.0 | eigenoptions_sqrt | eigenoptions_6 | 31 | 6 | 5.167 | 2.123 | 0.1395 | 4.133 | 1.7763568394002505e-15 | 2.6645352591003757e-15 | 3 | 5 | 1 | 12 | 3 |  |  |
| maze_9 | 0.0 | betweenness_sqrt | betweenness_6 | 31 | 6 | 5.167 | 4.998 | 0.1492 | 10.75 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 2 | 2 | 1 | 12 | 2 |  |  |
| maze_9 | 0.0 | random_landmarks_sqrt | random_landmarks_6 | 31 | 6 | 5.167 | 6.777 | 0.1482 | 13.43 | 0.0 | 8.881784197001252e-16 | 2 | 2 | 1 | 12 | 2 |  |  |
| maze_9 | 0.0 | coverage_sqrt | coverage_6 | 31 | 6 | 5.167 | 8.846 | 0.1465 | 17.91 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 2 | 2 | 1 | 12 | 2 |  |  |
| maze_9 | 0.05 | full_vi | full_vi | 31 | 31 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1 |  | 0.0 |  |  |
| maze_9 | 0.05 | graph_rd_joint | graph_rd_joint | 31 | 5 | 6.2 | 7.969 | 0.01015 | 17.05 | 1.9127810446661897e-11 | 1.9127810446661897e-11 | 9.473e-08 | 9.473e-08 | 1 | 12.9 | 0.0 |  |  |
| maze_9 | 0.05 | graph_rd_surrogate_joint | graph_rd_surrogate_joint | 31 | 5 | 6.2 | 8.1 | 0.06558 | 17.05 | 1.9127810446661897e-11 | 1.9127810446661897e-11 | 9.473e-08 | 9.473e-08 | 1 | 13.05 | 0.0 |  |  |
| maze_9 | 0.05 | group_constrained_rd | group_constrained_rd | 31 | 3 | 10.33 | 12.38 | 0.01795 | 29.65 | 3.5864644587491057e-12 | 3.6362024502523127e-12 | 3 | 3 | 1 | 12.95 | 3 | True | 0.0 |
| maze_9 | 0.05 | eigenoptions_sqrt | eigenoptions_6 | 31 | 6 | 5.167 | 3.069 | 0.3304 | 5.93 | 3.5864644587491057e-12 | 3.6362024502523127e-12 | 3 | 4.999 | 1 | 12.6 | 3 |  |  |
| maze_9 | 0.05 | betweenness_sqrt | betweenness_6 | 31 | 6 | 5.167 | 4.219 | 0.3524 | 8.024 | 7.052136652418994e-12 | 7.052136652418994e-12 | 2 | 2 | 1 | 13.05 | 2 |  |  |
| maze_9 | 0.05 | random_landmarks_sqrt | random_landmarks_6 | 31 | 6 | 5.167 | 3.511 | 0.3397 | 6.82 | 4.8832049515112885e-12 | 4.8832049515112885e-12 | 3.001 | 1.018 | 1 | 12.65 | 3 |  |  |
| maze_9 | 0.05 | coverage_sqrt | coverage_6 | 31 | 6 | 5.167 | 12.54 | 0.3698 | 27.28 | 1.98632221781736e-11 | 1.98632221781736e-11 | 2 | 2 | 1 | 12.7 | 2 |  |  |
