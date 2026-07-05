# Edge Reward Kernel Multi-Task

Generated: 2026-07-05T23:56:12
map_specs = ['corridor:32', 'open_room:6']
methods = ['endpoints', 'turn_articulation']
task_counts = [1, 3, 5], max_tasks = 5
additive_reward_kinds = ['sparse', 'dense']

This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.
Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.
The goal-conditioned variant appends query-time local options to the event model while keeping `B` fixed, and counts their interface size separately.

## Summary

| variant | task_type | n_rows | median_n_boundary | median_total_speedup | best_total_speedup | median_planning_speedup | max_start_gap | max_boundary_gap | median_goal_interface |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_B_edge_reward_kernel | additive_dense | 12 | 2 | 10.21 | 23.62 | 31.01 | 13.25 | 14.41 | 0.0 |
| fixed_B_edge_reward_kernel | additive_sparse | 12 | 2 | 10.18 | 24.07 | 31.75 | 28.22 | 28.84 | 0.0 |
| fixed_B_event_hit_kernel | terminal_goal | 12 | 2 | 0.7966 | 1.948 | 2.559 | 29.53 | 29.53 | 0.0 |
| fixed_B_goal_conditioned_event_options | terminal_goal | 12 | 2 | 0.674 | 1.105 | 1.23 | 0.1397 | 0.1589 | 6 |
| promote_goals_to_B | terminal_goal | 12 | 5 | 0.2098 | 0.3713 | 2.204 | 0.1348 | nan | 3 |

## Rows

| map | method_spec | variant | task_type | task_count | n_states | n_boundary | state_compression_ratio | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | planning_only_speedup_vs_full_vi | goal_option_interface_size | start_gap_max | boundary_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 32 | 2 | 16 | 0.01085 | 0.001324 | 8.196 | 45.28 | 0 | 23.14 | 23.14 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 32 | 2 | 16 | 0.01036 | 0.001306 | 7.933 | 46.8 | 0 | 11.31 | 11.31 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 32 | 2 | 16 | 0.001099 | 0.001451 | 0.757 | 2.996 | 0 | 0.0 | 1.3706369372812333e-11 |
| corridor_32 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 32 | 2 | 16 | 0.001099 | 0.001867 | 0.5885 | 1.404 | 2 | 0.0 | 1.3706369372812333e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 1 | 32 | 3 | 10.67 | 0.001099 | 0.004677 | 0.2349 | 9.533 | 1 | 0.0 | nan |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 3 | 32 | 2 | 16 | 0.03272 | 0.001797 | 18.21 | 45.96 | 0 | 28.22 | 28.22 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 3 | 32 | 2 | 16 | 0.03122 | 0.00174 | 17.94 | 47.66 | 0 | 12.89 | 12.89 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 3 | 32 | 2 | 16 | 0.003297 | 0.002131 | 1.547 | 3.151 | 0 | 1.5717205315013416e-11 | 2.8130386908742366e-11 |
| corridor_32 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 32 | 2 | 16 | 0.003297 | 0.003375 | 0.977 | 1.44 | 6 | 1.5717205315013416e-11 | 2.8130386908742366e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 3 | 32 | 5 | 6.4 | 0.003297 | 0.01069 | 0.3084 | 2.211 | 3 | 3.568700890355103e-12 | nan |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 32 | 2 | 16 | 0.05402 | 0.002245 | 24.07 | 46.57 | 0 | 28.22 | 28.22 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 32 | 2 | 16 | 0.05181 | 0.002193 | 23.62 | 46.74 | 0 | 12.89 | 12.89 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 32 | 2 | 16 | 0.005445 | 0.002795 | 1.948 | 3.183 | 0 | 3.667821601993637e-11 | 3.667821601993637e-11 |
| corridor_32 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 32 | 2 | 16 | 0.005445 | 0.004928 | 1.105 | 1.417 | 10 | 3.667821601993637e-11 | 3.667821601993637e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 5 | 32 | 7 | 4.571 | 0.005445 | 0.02771 | 0.1965 | 0.4416 | 5 | 3.667288694941817e-11 | nan |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 32 | 2 | 16 | 0.01078 | 0.001746 | 6.175 | 48.59 | 0 | 23.14 | 23.14 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 32 | 2 | 16 | 0.01056 | 0.001742 | 6.064 | 48.59 | 0 | 11.31 | 11.31 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 32 | 2 | 16 | 0.001187 | 0.001827 | 0.6495 | 3.918 | 0 | 0.0 | 1.3706369372812333e-11 |
| corridor_32 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 32 | 2 | 16 | 0.001187 | 0.002313 | 0.5131 | 1.505 | 2 | 0.0 | 1.3706369372812333e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 1 | 32 | 3 | 10.67 | 0.001187 | 0.004404 | 0.2695 | 12.48 | 1 | 0.0 | nan |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 3 | 32 | 2 | 16 | 0.03226 | 0.002212 | 14.58 | 46.9 | 0 | 28.22 | 28.22 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 3 | 32 | 2 | 16 | 0.03148 | 0.002256 | 13.95 | 43 | 0 | 12.89 | 12.89 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 3 | 32 | 2 | 16 | 0.003665 | 0.002487 | 1.474 | 3.806 | 0 | 1.5717205315013416e-11 | 2.8130386908742366e-11 |
| corridor_32 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 32 | 2 | 16 | 0.003665 | 0.003919 | 0.9353 | 1.531 | 6 | 1.5717205315013416e-11 | 2.8130386908742366e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 3 | 32 | 5 | 6.4 | 0.003665 | 0.009871 | 0.3713 | 2.488 | 3 | 3.568700890355103e-12 | nan |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 32 | 2 | 16 | 0.05371 | 0.002646 | 20.3 | 47.9 | 0 | 28.22 | 28.22 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 32 | 2 | 16 | 0.05229 | 0.002678 | 19.52 | 45.32 | 0 | 12.89 | 12.89 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 32 | 2 | 16 | 0.006024 | 0.003178 | 1.895 | 3.643 | 0 | 3.667821601993637e-11 | 3.667821601993637e-11 |
| corridor_32 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 32 | 2 | 16 | 0.006024 | 0.005475 | 1.1 | 1.525 | 10 | 3.667821601993637e-11 | 3.667821601993637e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 5 | 32 | 7 | 4.571 | 0.006024 | 0.02701 | 0.223 | 0.4866 | 5 | 3.667288694941817e-11 | nan |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 36 | 2 | 18 | 0.01099 | 0.001482 | 7.42 | 18.09 | 0 | 27.05 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 36 | 2 | 18 | 0.01052 | 0.001464 | 7.187 | 17.84 | 0 | 13.25 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 36 | 2 | 18 | 0.0009089 | 0.001302 | 0.698 | 2.123 | 0 | 0.629 | 5.239 |
| open_room_6 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 36 | 2 | 18 | 0.0009089 | 0.001787 | 0.5086 | 0.9958 | 2 | 0.0008212 | 0.1589 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 1 | 36 | 3 | 12 | 0.0009089 | 0.004779 | 0.1902 | 6.825 | 1 | 0.0008212 | nan |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 3 | 36 | 2 | 18 | 0.03202 | 0.002631 | 12.17 | 18.22 | 0 | 27.05 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 3 | 36 | 2 | 18 | 0.03174 | 0.002542 | 12.49 | 19.03 | 0 | 13.25 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 3 | 36 | 2 | 18 | 0.002669 | 0.003192 | 0.8361 | 1.151 | 0 | 25.6 | 29.53 |
| open_room_6 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 36 | 2 | 18 | 0.002669 | 0.003514 | 0.7596 | 1.011 | 6 | 0.1348 | 0.1589 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 3 | 36 | 5 | 7.2 | 0.002669 | 0.0106 | 0.2518 | 2.198 | 3 | 0.1348 | nan |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 36 | 2 | 18 | 0.05374 | 0.003824 | 14.05 | 18.22 | 0 | 27.05 | 28.84 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 36 | 2 | 18 | 0.0528 | 0.003703 | 14.26 | 18.67 | 0 | 13.25 | 14.41 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 36 | 2 | 18 | 0.004488 | 0.0045 | 0.9974 | 1.238 | 0 | 29.53 | 29.53 |
| open_room_6 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 36 | 2 | 18 | 0.004488 | 0.005123 | 0.8761 | 1.056 | 10 | 0.1348 | 0.1589 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 5 | 36 | 7 | 5.143 | 0.004488 | 0.02557 | 0.1755 | 0.4723 | 5 | 0.1348 | nan |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 36 | 4 | 9 | 0.0107 | 0.005822 | 1.839 | 4.458 | 0 | 13.21 | 14.53 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 36 | 4 | 9 | 0.01067 | 0.005949 | 1.794 | 4.22 | 0 | 7.395 | 7.859 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 36 | 4 | 9 | 0.001014 | 0.007027 | 0.1442 | 0.281 | 0 | 20.17 | 21.67 |
| open_room_6 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 36 | 4 | 9 | 0.001014 | 0.005444 | 0.1862 | 0.5009 | 4 | 0.1049 | 0.1049 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 1 | 36 | 5 | 7.2 | 0.001014 | 0.01001 | 0.1012 | 2.808 | 1 | 0.1049 | nan |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 3 | 36 | 4 | 9 | 0.03274 | 0.01104 | 2.965 | 4.295 | 0 | 13.82 | 14.53 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 3 | 36 | 4 | 9 | 0.03212 | 0.01147 | 2.799 | 3.988 | 0 | 7.446 | 7.859 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 3 | 36 | 4 | 9 | 0.002966 | 0.01587 | 0.1869 | 0.2382 | 0 | 27.92 | 28.86 |
| open_room_6 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 3 | 36 | 4 | 9 | 0.002966 | 0.009881 | 0.3002 | 0.4591 | 12 | 0.1049 | 0.1049 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 3 | 36 | 7 | 5.143 | 0.002966 | 0.01906 | 0.1557 | 0.8995 | 3 | 0.1049 | nan |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 36 | 4 | 9 | 0.05483 | 0.01702 | 3.221 | 4.031 | 0 | 19.48 | 24.45 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 36 | 4 | 9 | 0.05369 | 0.01715 | 3.13 | 3.91 | 0 | 9.521 | 11.8 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 36 | 4 | 9 | 0.005095 | 0.01864 | 0.2733 | 0.3348 | 0 | 27.92 | 28.86 |
| open_room_6 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 36 | 4 | 9 | 0.005095 | 0.01401 | 0.3637 | 0.4812 | 20 | 0.1397 | 0.1453 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 5 | 36 | 9 | 4 | 0.005095 | 0.03773 | 0.135 | 0.3964 | 5 | 0.1049 | nan |
