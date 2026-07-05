# Edge Reward Kernel Multi-Task

Generated: 2026-07-05T23:34:45
map_specs = ['corridor:32', 'open_room:6']
methods = ['endpoints', 'turn_articulation']
task_counts = [1, 3, 5], max_tasks = 5
additive_reward_kinds = ['sparse', 'dense']

This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.
Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.

## Summary

| variant | task_type | n_rows | median_n_boundary | median_total_speedup | best_total_speedup | median_planning_speedup | max_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_B_edge_reward_kernel | additive_dense | 12 | 2 | 9.795 | 22.96 | 31.79 | 13.25 |
| fixed_B_edge_reward_kernel | additive_sparse | 12 | 2 | 10.22 | 23.33 | 31.76 | 28.22 |
| fixed_B_event_hit_kernel | terminal_goal | 12 | 2 | 0.8372 | 1.905 | 2.626 | 29.53 |
| promote_goals_to_B | terminal_goal | 12 | 5 | 0.2082 | 0.3471 | 2.255 | 0.1348 |

## Rows

| map | method_spec | variant | task_type | task_count | n_states | n_boundary | state_compression_ratio | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | planning_only_speedup_vs_full_vi | start_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 32 | 2 | 16 | 0.01115 | 0.001403 | 7.948 | 44.84 | 23.14 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 32 | 2 | 16 | 0.01074 | 0.00138 | 7.782 | 47.57 | 11.31 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 32 | 2 | 16 | 0.001164 | 0.001528 | 0.7615 | 3.112 | 0.0 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 1 | 32 | 3 | 10.67 | 0.001164 | 0.004747 | 0.2452 | 9.927 | 0.0 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 3 | 32 | 2 | 16 | 0.03308 | 0.001865 | 17.73 | 46.52 | 28.22 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 3 | 32 | 2 | 16 | 0.03185 | 0.001838 | 17.32 | 46.55 | 12.89 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 3 | 32 | 2 | 16 | 0.003471 | 0.00228 | 1.523 | 3.085 | 1.5717205315013416e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 3 | 32 | 5 | 6.4 | 0.003471 | 0.01054 | 0.3295 | 2.3 | 3.568700890355103e-12 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 32 | 2 | 16 | 0.05472 | 0.002345 | 23.33 | 45.96 | 28.22 |
| corridor_32 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 32 | 2 | 16 | 0.0528 | 0.002299 | 22.96 | 46.12 | 12.89 |
| corridor_32 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 32 | 2 | 16 | 0.005594 | 0.002937 | 1.905 | 3.138 | 3.667821601993637e-11 |
| corridor_32 | endpoints | promote_goals_to_B | terminal_goal | 5 | 32 | 7 | 4.571 | 0.005594 | 0.02746 | 0.2037 | 0.4539 | 3.667288694941817e-11 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 32 | 2 | 16 | 0.01086 | 0.001641 | 6.619 | 47.99 | 23.14 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 32 | 2 | 16 | 0.01057 | 0.001638 | 6.451 | 47.27 | 11.31 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 32 | 2 | 16 | 0.001198 | 0.001742 | 0.6875 | 3.655 | 0.0 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 1 | 32 | 3 | 10.67 | 0.001198 | 0.004266 | 0.2807 | 12.85 | 0.0 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 3 | 32 | 2 | 16 | 0.03283 | 0.00209 | 15.71 | 48.61 | 28.22 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 3 | 32 | 2 | 16 | 0.03192 | 0.00209 | 15.27 | 47.26 | 12.89 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 3 | 32 | 2 | 16 | 0.00361 | 0.00246 | 1.467 | 3.452 | 1.5717205315013416e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 3 | 32 | 5 | 6.4 | 0.00361 | 0.0104 | 0.3471 | 2.254 | 3.568700890355103e-12 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 32 | 2 | 16 | 0.05482 | 0.002575 | 21.29 | 47.22 | 28.22 |
| corridor_32 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 32 | 2 | 16 | 0.05314 | 0.002522 | 21.07 | 47.99 | 12.89 |
| corridor_32 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 32 | 2 | 16 | 0.005958 | 0.003131 | 1.903 | 3.47 | 3.667821601993637e-11 |
| corridor_32 | turn_articulation | promote_goals_to_B | terminal_goal | 5 | 32 | 7 | 4.571 | 0.005958 | 0.02802 | 0.2126 | 0.472 | 3.667288694941817e-11 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 36 | 2 | 18 | 0.01115 | 0.001542 | 7.234 | 16.85 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 36 | 2 | 18 | 0.01076 | 0.001567 | 6.862 | 15.64 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 36 | 2 | 18 | 0.0009027 | 0.001296 | 0.6964 | 2.168 | 0.629 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 1 | 36 | 3 | 12 | 0.0009027 | 0.004997 | 0.1807 | 6.638 | 0.0008212 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 3 | 36 | 2 | 18 | 0.0332 | 0.002658 | 12.49 | 18.67 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 3 | 36 | 2 | 18 | 0.03209 | 0.002717 | 11.81 | 17.46 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 3 | 36 | 2 | 18 | 0.002809 | 0.003077 | 0.9129 | 1.278 | 25.6 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 3 | 36 | 5 | 7.2 | 0.002809 | 0.01089 | 0.2581 | 2.256 | 0.1348 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 36 | 2 | 18 | 0.05525 | 0.003836 | 14.4 | 18.69 | 27.05 |
| open_room_6 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 36 | 2 | 18 | 0.05385 | 0.003968 | 13.57 | 17.44 | 13.25 |
| open_room_6 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 36 | 2 | 18 | 0.004717 | 0.004444 | 1.061 | 1.323 | 29.53 |
| open_room_6 | endpoints | promote_goals_to_B | terminal_goal | 5 | 36 | 7 | 5.143 | 0.004717 | 0.02587 | 0.1824 | 0.4961 | 0.1348 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 36 | 4 | 9 | 0.01101 | 0.005651 | 1.948 | 4.505 | 13.21 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 36 | 4 | 9 | 0.01099 | 0.005734 | 1.916 | 4.348 | 7.395 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 36 | 4 | 9 | 0.001115 | 0.006914 | 0.1612 | 0.3007 | 20.17 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 1 | 36 | 5 | 7.2 | 0.001115 | 0.009846 | 0.1132 | 3.031 | 0.1049 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 3 | 36 | 4 | 9 | 0.03343 | 0.01108 | 3.018 | 4.247 | 13.82 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 3 | 36 | 4 | 9 | 0.03297 | 0.0114 | 2.891 | 4.022 | 7.446 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 3 | 36 | 4 | 9 | 0.003146 | 0.01584 | 0.1986 | 0.249 | 27.92 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 3 | 36 | 7 | 5.143 | 0.003146 | 0.01956 | 0.1608 | 0.9652 | 0.1049 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 36 | 4 | 9 | 0.05612 | 0.01721 | 3.261 | 4.008 | 19.48 |
| open_room_6 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 36 | 4 | 9 | 0.05479 | 0.01735 | 3.158 | 3.874 | 9.521 |
| open_room_6 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 36 | 4 | 9 | 0.005287 | 0.01856 | 0.2848 | 0.3443 | 27.92 |
| open_room_6 | turn_articulation | promote_goals_to_B | terminal_goal | 5 | 36 | 9 | 4 | 0.005287 | 0.03903 | 0.1355 | 0.3877 | 0.1049 |
