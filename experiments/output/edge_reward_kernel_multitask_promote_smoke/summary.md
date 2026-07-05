# Edge Reward Kernel Multi-Task

Generated: 2026-07-06T00:12:52
map_specs = ['corridor:32', 'open_room:6']
methods = ['endpoints', 'turn_articulation']
task_counts = [1, 3, 5], max_tasks = 5
additive_reward_kinds = ['sparse', 'dense']

This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.
Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.
The goal-conditioned variant appends query-time local options to the event model while keeping `B` fixed, and counts their interface size separately.
Its shared/batched backend builds one goal-conditioned policy per queried goal and solves all boundary-start event rows together.

## Summary

| variant | task_type | n_rows | median_n_boundary | median_total_speedup | best_total_speedup | median_planning_speedup | max_start_gap | max_boundary_gap | median_goal_interface | median_goal_policies | median_break_even_tasks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_B_edge_reward_kernel | additive_dense | 12 | 2 | 10.18 | 24.23 | 30.3 | 13.25 | 14.41 | 0.0 | 0.0 | 1 |
| fixed_B_edge_reward_kernel | additive_sparse | 12 | 2 | 10.51 | 25.27 | 32.68 | 28.22 | 28.84 | 0.0 | 0.0 | 1 |
| fixed_B_event_hit_kernel | terminal_goal | 12 | 2 | 0.8205 | 2.166 | 2.61 | 29.53 | 29.53 | 0.0 | 0.0 | 2 |
| fixed_B_goal_conditioned_event_options | terminal_goal | 12 | 2 | 0.7154 | 1.227 | 1.335 | 0.1397 | 0.1589 | 6 | 3 | 4 |
| promote_goals_to_B | terminal_goal | 12 | 5 | 0.205 | 0.3418 | 2.194 | 0.1348 | nan | 3 | 0.0 | 17 |

## Rows

| map | method_spec | variant | task_type | task_count | n_states | n_boundary | state_compression_ratio | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | planning_only_speedup_vs_full_vi | break_even_num_tasks | goal_option_interface_size | n_goal_policies | policy_build_time_sec | batched_event_solve_time_sec | start_gap_max | boundary_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 32 | 2 | 16 | 0.01127 | 0.001284 | 8.771 | 47.41 | 1 | 0 | 0 | 0.0 | 0.0 | 23.14 | 23.14 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 32 | 2 | 16 | 0.01085 | 0.001266 | 8.57 | 49.42 | 1 | 0 | 0 | 0.0 | 0.0 | 11.31 | 11.31 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 32 | 2 | 16 | 0.001128 | 0.001358 | 0.8309 | 3.63 | 2 | 0 | 0 | 0.0 | 0.0 | 0.0 | 1.3706369372812333e-11 |
| corridor_32 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 32 | 2 | 16 | 0.001128 | 0.001764 | 0.6396 | 1.574 | 2 | 2 | 1 | 0.0001823 | 0.0001413 | 6.394884621840902e-13 | 1.2420287021086551e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 1 | 32 | 3 | 10.67 | 0.001128 | 0.004506 | 0.2503 | 8.001 | 6 | 1 | 0 | 0.0 | 0.0 | 0.0 | nan |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 3 | 32 | 2 | 16 | 0.03334 | 0.001751 | 19.04 | 47.34 | 1 | 0 | 0 | 0.0 | 0.0 | 28.22 | 28.22 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 3 | 32 | 2 | 16 | 0.03196 | 0.001758 | 18.18 | 44.94 | 1 | 0 | 0 | 0.0 | 0.0 | 12.89 | 12.89 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 3 | 32 | 2 | 16 | 0.003389 | 0.001902 | 1.782 | 3.965 | 2 | 0 | 0 | 0.0 | 0.0 | 1.5717205315013416e-11 | 2.8130386908742366e-11 |
| corridor_32 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 32 | 2 | 16 | 0.003389 | 0.003095 | 1.095 | 1.655 | 3 | 6 | 3 | 0.000555 | 0.0003612 | 1.4555467942045652e-11 | 2.6624036308930954e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 3 | 32 | 5 | 6.4 | 0.003389 | 0.01021 | 0.332 | 2.294 | 20 | 3 | 0 | 0.0 | 0.0 | 3.568700890355103e-12 | nan |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 32 | 2 | 16 | 0.05523 | 0.002186 | 25.27 | 48.49 | 1 | 0 | 0 | 0.0 | 0.0 | 28.22 | 28.22 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 32 | 2 | 16 | 0.05299 | 0.002186 | 24.23 | 46.5 | 1 | 0 | 0 | 0.0 | 0.0 | 12.89 | 12.89 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 32 | 2 | 16 | 0.005479 | 0.00253 | 2.166 | 3.695 | 2 | 0 | 0 | 0.0 | 0.0 | 3.667821601993637e-11 | 3.667821601993637e-11 |
| corridor_32 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 32 | 2 | 16 | 0.005479 | 0.004466 | 1.227 | 1.603 | 4 | 10 | 5 | 0.0009128 | 0.0005667 | 3.5564440281632415e-11 | 3.5564440281632415e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 5 | 32 | 7 | 4.571 | 0.005479 | 0.02808 | 0.1951 | 0.4274 | inf | 5 | 0 | 0.0 | 0.0 | 3.667288694941817e-11 | nan |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 32 | 2 | 16 | 0.01105 | 0.001612 | 6.851 | 50.26 | 1 | 0 | 0 | 0.0 | 0.0 | 23.14 | 23.14 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 32 | 2 | 16 | 0.01081 | 0.001644 | 6.573 | 42.98 | 1 | 0 | 0 | 0.0 | 0.0 | 11.31 | 11.31 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 32 | 2 | 16 | 0.001252 | 0.00167 | 0.7492 | 4.505 | 2 | 0 | 0 | 0.0 | 0.0 | 0.0 | 1.3706369372812333e-11 |
| corridor_32 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 32 | 2 | 16 | 0.001252 | 0.002076 | 0.6027 | 1.83 | 2 | 2 | 1 | 0.0002013 | 0.0001005 | 6.394884621840902e-13 | 1.2420287021086551e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 1 | 32 | 3 | 10.67 | 0.001252 | 0.004252 | 0.2944 | 13.7 | 5 | 1 | 0 | 0.0 | 0.0 | 0.0 | nan |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 3 | 32 | 2 | 16 | 0.03299 | 0.002045 | 16.13 | 50.54 | 1 | 0 | 0 | 0.0 | 0.0 | 28.22 | 28.22 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 3 | 32 | 2 | 16 | 0.03219 | 0.002105 | 15.29 | 45.17 | 1 | 0 | 0 | 0.0 | 0.0 | 12.89 | 12.89 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 3 | 32 | 2 | 16 | 0.003605 | 0.002382 | 1.513 | 3.643 | 2 | 0 | 0 | 0.0 | 0.0 | 1.5717205315013416e-11 | 2.8130386908742366e-11 |
| corridor_32 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 32 | 2 | 16 | 0.003605 | 0.003615 | 0.997 | 1.622 | 4 | 6 | 3 | 0.0006097 | 0.0003019 | 1.4555467942045652e-11 | 2.6624036308930954e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 3 | 32 | 5 | 6.4 | 0.003605 | 0.01055 | 0.3418 | 2.342 | 19 | 3 | 0 | 0.0 | 0.0 | 3.568700890355103e-12 | nan |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 32 | 2 | 16 | 0.05499 | 0.00252 | 21.82 | 48.78 | 1 | 0 | 0 | 0.0 | 0.0 | 28.22 | 28.22 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 32 | 2 | 16 | 0.05344 | 0.002514 | 21.26 | 47.66 | 1 | 0 | 0 | 0.0 | 0.0 | 12.89 | 12.89 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 32 | 2 | 16 | 0.006028 | 0.002986 | 2.019 | 3.783 | 2 | 0 | 0 | 0.0 | 0.0 | 3.667821601993637e-11 | 3.667821601993637e-11 |
| corridor_32 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 32 | 2 | 16 | 0.006028 | 0.00509 | 1.184 | 1.63 | 5 | 10 | 5 | 0.001039 | 0.0005231 | 3.5564440281632415e-11 | 3.5564440281632415e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 5 | 32 | 7 | 4.571 | 0.006028 | 0.02805 | 0.2149 | 0.4699 | inf | 5 | 0 | 0.0 | 0.0 | 3.667288694941817e-11 | nan |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 36 | 2 | 18 | 0.01131 | 0.00154 | 7.341 | 17.08 | 1 | 0 | 0 | 0.0 | 0.0 | 27.05 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 36 | 2 | 18 | 0.01089 | 0.001567 | 6.948 | 15.8 | 1 | 0 | 0 | 0.0 | 0.0 | 13.25 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 36 | 2 | 18 | 0.0009478 | 0.001474 | 0.643 | 1.59 | 3 | 0 | 0 | 0.0 | 0.0 | 0.629 | 5.239 |
| open_room_6 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 36 | 2 | 18 | 0.0009478 | 0.001832 | 0.5174 | 0.9937 | 3 | 2 | 1 | 0.0002377 | 0.0001352 | 0.0008212 | 0.1589 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 1 | 36 | 3 | 12 | 0.0009478 | 0.00496 | 0.1911 | 7.48 | 8 | 1 | 0 | 0.0 | 0.0 | 0.0008212 | nan |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 3 | 36 | 2 | 18 | 0.03356 | 0.002741 | 12.24 | 18.01 | 1 | 0 | 0 | 0.0 | 0.0 | 27.05 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 3 | 36 | 2 | 18 | 0.03245 | 0.002751 | 11.79 | 17.32 | 1 | 0 | 0 | 0.0 | 0.0 | 13.25 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 3 | 36 | 2 | 18 | 0.002824 | 0.003485 | 0.8102 | 1.083 | 13 | 0 | 0 | 0.0 | 0.0 | 25.6 | 29.53 |
| open_room_6 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 36 | 2 | 18 | 0.002824 | 0.003568 | 0.7913 | 1.05 | 4 | 6 | 3 | 0.0007388 | 0.0003981 | 0.1348 | 0.1589 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 3 | 36 | 5 | 7.2 | 0.002824 | 0.01132 | 0.2494 | 2.094 | 27 | 3 | 0 | 0.0 | 0.0 | 0.1348 | nan |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 36 | 2 | 18 | 0.05591 | 0.004073 | 13.73 | 17.5 | 1 | 0 | 0 | 0.0 | 0.0 | 27.05 | 28.84 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 36 | 2 | 18 | 0.05455 | 0.003974 | 13.73 | 17.62 | 1 | 0 | 0 | 0.0 | 0.0 | 13.25 | 14.41 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 36 | 2 | 18 | 0.004685 | 0.004879 | 0.9603 | 1.171 | 7 | 0 | 0 | 0.0 | 0.0 | 29.53 | 29.53 |
| open_room_6 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 36 | 2 | 18 | 0.004685 | 0.005148 | 0.9101 | 1.097 | 6 | 10 | 5 | 0.00115 | 0.0007097 | 0.1348 | 0.1589 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 5 | 36 | 7 | 5.143 | 0.004685 | 0.02694 | 0.1739 | 0.4648 | inf | 5 | 0 | 0.0 | 0.0 | 0.1348 | nan |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 36 | 4 | 9 | 0.01101 | 0.005983 | 1.841 | 4.353 | 1 | 0 | 0 | 0.0 | 0.0 | 13.21 | 14.53 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 36 | 4 | 9 | 0.01084 | 0.006076 | 1.785 | 4.135 | 1 | 0 | 0 | 0.0 | 0.0 | 7.395 | 7.859 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 36 | 4 | 9 | 0.001008 | 0.007336 | 0.1375 | 0.2597 | inf | 0 | 0 | 0.0 | 0.0 | 20.17 | 21.67 |
| open_room_6 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 36 | 4 | 9 | 0.001008 | 0.005416 | 0.1862 | 0.5136 | 7 | 4 | 1 | 0.0002339 | 0.0001214 | 0.1049 | 0.1049 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 1 | 36 | 5 | 7.2 | 0.001008 | 0.009986 | 0.101 | 2.738 | 17 | 1 | 0 | 0.0 | 0.0 | 0.1049 | nan |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 3 | 36 | 4 | 9 | 0.03351 | 0.01145 | 2.927 | 4.19 | 1 | 0 | 0 | 0.0 | 0.0 | 13.82 | 14.53 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 3 | 36 | 4 | 9 | 0.03299 | 0.01181 | 2.794 | 3.949 | 1 | 0 | 0 | 0.0 | 0.0 | 7.446 | 7.859 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 3 | 36 | 4 | 9 | 0.003036 | 0.01655 | 0.1835 | 0.2318 | inf | 0 | 0 | 0.0 | 0.0 | 27.92 | 28.86 |
| open_room_6 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 36 | 4 | 9 | 0.003036 | 0.009315 | 0.3259 | 0.5179 | 12 | 12 | 3 | 0.0007276 | 0.0003777 | 0.1049 | 0.1049 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 3 | 36 | 7 | 5.143 | 0.003036 | 0.02005 | 0.1514 | 0.8577 | inf | 3 | 0 | 0.0 | 0.0 | 0.1049 | nan |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 36 | 4 | 9 | 0.05616 | 0.01781 | 3.154 | 3.913 | 1 | 0 | 0 | 0.0 | 0.0 | 19.48 | 24.45 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 36 | 4 | 9 | 0.05514 | 0.0178 | 3.098 | 3.844 | 1 | 0 | 0 | 0.0 | 0.0 | 9.521 | 11.8 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 36 | 4 | 9 | 0.005158 | 0.01941 | 0.2657 | 0.3232 | inf | 0 | 0 | 0.0 | 0.0 | 27.92 | 28.86 |
| open_room_6 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 36 | 4 | 9 | 0.005158 | 0.01325 | 0.3892 | 0.5263 | 17 | 20 | 5 | 0.00122 | 0.0006186 | 0.1397 | 0.1453 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 5 | 36 | 9 | 4 | 0.005158 | 0.0399 | 0.1293 | 0.3641 | inf | 5 | 0 | 0.0 | 0.0 | 0.1049 | nan |
