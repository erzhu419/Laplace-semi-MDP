# Edge Reward Kernel Multi-Task

Generated: 2026-07-05T23:56:51
map_specs = ['corridor:128', 'open_room:16', 'four_rooms:15', 'maze:17']
methods = ['endpoints', 'turn_articulation']
task_counts = [1, 5, 10], max_tasks = 10
additive_reward_kinds = ['sparse', 'dense']

This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.
Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.
The goal-conditioned variant appends query-time local options to the event model while keeping `B` fixed, and counts their interface size separately.

## Summary

| variant | task_type | n_rows | median_n_boundary | median_total_speedup | best_total_speedup | median_planning_speedup | max_start_gap | max_boundary_gap | median_goal_interface |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_B_edge_reward_kernel | additive_dense | 24 | 2 | 2.902 | 28.24 | 103 | 14.25 | 15.52 | 0.0 |
| fixed_B_edge_reward_kernel | additive_sparse | 24 | 2 | 3 | 28.27 | 103.6 | 28.8 | 30.49 | 0.0 |
| fixed_B_event_hit_kernel | terminal_goal | 24 | 2 | 0.3782 | 1.678 | 0.5553 | 27.52 | 31.22 | 0.0 |
| fixed_B_goal_conditioned_event_options | terminal_goal | 24 | 2 | 0.1995 | 0.8208 | 0.2542 | 0.3494 | 0.3925 | 18 |

## Rows

| map | method_spec | variant | task_type | task_count | n_states | n_boundary | state_compression_ratio | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | planning_only_speedup_vs_full_vi | goal_option_interface_size | start_gap_max | boundary_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 128 | 2 | 64 | 0.01695 | 0.005502 | 3.08 | 178.3 | 0 | 3.322 | 4.755 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 128 | 2 | 64 | 0.01621 | 0.005479 | 2.959 | 224.5 | 0 | 1.485 | 2.141 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 128 | 2 | 64 | 0.003744 | 0.007531 | 0.4971 | 1.763 | 0 | 3.413447302591521e-11 | 3.413447302591521e-11 |
| corridor_128 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 128 | 2 | 64 | 0.003744 | 0.01034 | 0.3622 | 0.7595 | 2 | 3.413447302591521e-11 | 3.413447302591521e-11 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 128 | 2 | 64 | 0.08485 | 0.005862 | 14.48 | 186.7 | 0 | 15.37 | 15.37 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 128 | 2 | 64 | 0.08236 | 0.0059 | 13.96 | 167.1 | 0 | 8.288 | 8.288 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 128 | 2 | 64 | 0.02177 | 0.0162 | 1.344 | 2.017 | 0 | 3.413447302591521e-11 | 6.24496010459552e-11 |
| corridor_128 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 128 | 2 | 64 | 0.02177 | 0.03019 | 0.7211 | 0.8784 | 10 | 3.413447302591521e-11 | 6.24496010459552e-11 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 128 | 2 | 64 | 0.1693 | 0.00629 | 26.91 | 191.8 | 0 | 16.41 | 16.41 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 128 | 2 | 64 | 0.1645 | 0.006375 | 25.8 | 170 | 0 | 8.315 | 8.315 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 128 | 2 | 64 | 0.04271 | 0.02721 | 1.57 | 1.959 | 0 | 4.735767333841068e-11 | 6.24496010459552e-11 |
| corridor_128 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 128 | 2 | 64 | 0.04271 | 0.05492 | 0.7777 | 0.8627 | 20 | 4.735767333841068e-11 | 6.24496010459552e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 128 | 2 | 64 | 0.01742 | 0.005965 | 2.92 | 184.8 | 0 | 3.322 | 4.755 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 128 | 2 | 64 | 0.01694 | 0.005957 | 2.845 | 197.3 | 0 | 1.485 | 2.141 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 128 | 2 | 64 | 0.00436 | 0.007997 | 0.5453 | 2.051 | 0 | 3.413447302591521e-11 | 3.413447302591521e-11 |
| corridor_128 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 128 | 2 | 64 | 0.00436 | 0.01084 | 0.4023 | 0.8779 | 2 | 3.413447302591521e-11 | 3.413447302591521e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 128 | 2 | 64 | 0.08821 | 0.00633 | 13.94 | 192.1 | 0 | 15.37 | 15.37 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 128 | 2 | 64 | 0.08565 | 0.006301 | 13.59 | 199.1 | 0 | 8.288 | 8.288 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 128 | 2 | 64 | 0.0236 | 0.01695 | 1.392 | 2.13 | 0 | 3.413447302591521e-11 | 6.24496010459552e-11 |
| corridor_128 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 128 | 2 | 64 | 0.0236 | 0.03144 | 0.7506 | 0.9229 | 10 | 3.413447302591521e-11 | 6.24496010459552e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 128 | 2 | 64 | 0.1756 | 0.006744 | 26.04 | 201 | 0 | 16.41 | 16.41 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 128 | 2 | 64 | 0.1716 | 0.006735 | 25.48 | 198.6 | 0 | 8.315 | 8.315 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 128 | 2 | 64 | 0.0464 | 0.02766 | 1.678 | 2.13 | 0 | 4.735767333841068e-11 | 6.24496010459552e-11 |
| corridor_128 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 128 | 2 | 64 | 0.0464 | 0.05653 | 0.8208 | 0.9159 | 20 | 4.735767333841068e-11 | 6.24496010459552e-11 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 256 | 2 | 128 | 0.03733 | 0.02479 | 1.506 | 137.7 | 0 | 13.9 | 26.14 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 256 | 2 | 128 | 0.03629 | 0.02484 | 1.461 | 112.7 | 0 | 6.536 | 11.73 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 256 | 2 | 128 | 0.006949 | 0.03833 | 0.1813 | 0.5032 | 0 | 4.912 | 4.912 |
| open_room_16 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 256 | 2 | 128 | 0.006949 | 0.05551 | 0.1252 | 0.2242 | 2 | 0.2593 | 0.2593 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 256 | 2 | 128 | 0.1884 | 0.02575 | 7.316 | 153.1 | 0 | 13.9 | 26.14 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 256 | 2 | 128 | 0.1815 | 0.02584 | 7.026 | 137.4 | 0 | 6.578 | 11.73 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 256 | 2 | 128 | 0.03167 | 0.09202 | 0.3442 | 0.4692 | 0 | 23.37 | 25.75 |
| open_room_16 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 256 | 2 | 128 | 0.03167 | 0.1689 | 0.1875 | 0.2193 | 10 | 0.2593 | 0.2813 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 256 | 2 | 128 | 0.3784 | 0.02701 | 14.01 | 152.2 | 0 | 17.22 | 26.14 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 256 | 2 | 128 | 0.3652 | 0.02704 | 13.5 | 144.7 | 0 | 9.1 | 11.73 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 256 | 2 | 128 | 0.06549 | 0.1588 | 0.4123 | 0.4875 | 0 | 25.74 | 26.42 |
| open_room_16 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 256 | 2 | 128 | 0.06549 | 0.3095 | 0.2116 | 0.2298 | 20 | 0.2593 | 0.2813 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 256 | 4 | 64 | 0.03776 | 0.1302 | 0.29 | 37.64 | 0 | 6.49 | 15.2 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 256 | 4 | 64 | 0.03768 | 0.1302 | 0.2894 | 36.6 | 0 | 3.368 | 7.197 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 256 | 4 | 64 | 0.00847 | 0.2092 | 0.04048 | 0.1058 | 0 | 9.667 | 26.49 |
| open_room_16 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 256 | 4 | 64 | 0.00847 | 0.2372 | 0.03571 | 0.07843 | 4 | 0.1784 | 0.3925 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 256 | 4 | 64 | 0.1928 | 0.1342 | 1.436 | 38.26 | 0 | 11.41 | 28.83 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 256 | 4 | 64 | 0.1883 | 0.1342 | 1.403 | 37.36 | 0 | 6.411 | 15.52 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 256 | 4 | 64 | 0.03742 | 0.5182 | 0.07221 | 0.09619 | 0 | 23.37 | 26.92 |
| open_room_16 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 256 | 4 | 64 | 0.03742 | 0.655 | 0.05712 | 0.07116 | 20 | 0.2759 | 0.3925 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 256 | 4 | 64 | 0.385 | 0.1393 | 2.763 | 37.97 | 0 | 13.48 | 28.83 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 256 | 4 | 64 | 0.3753 | 0.1391 | 2.698 | 37.83 | 0 | 6.411 | 15.52 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 256 | 4 | 64 | 0.0743 | 0.9038 | 0.0822 | 0.09592 | 0 | 26.32 | 28.31 |
| open_room_16 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 256 | 4 | 64 | 0.0743 | 1.174 | 0.06329 | 0.07112 | 40 | 0.3494 | 0.3925 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 200 | 2 | 100 | 0.02703 | 0.01296 | 2.085 | 107.4 | 0 | 28.8 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 200 | 2 | 100 | 0.02644 | 0.01297 | 2.039 | 102.5 | 0 | 14.25 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 200 | 2 | 100 | 0.004421 | 0.01997 | 0.2213 | 0.609 | 0 | 0.8064 | 2.161 |
| four_rooms_15 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 200 | 2 | 100 | 0.004421 | 0.02858 | 0.1547 | 0.2785 | 2 | 0.000575 | 0.1561 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 200 | 2 | 100 | 0.1376 | 0.01397 | 9.847 | 109.2 | 0 | 28.8 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 200 | 2 | 100 | 0.1314 | 0.01398 | 9.398 | 103.8 | 0 | 14.25 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 200 | 2 | 100 | 0.02163 | 0.04749 | 0.4555 | 0.622 | 0 | 21.98 | 21.98 |
| four_rooms_15 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 200 | 2 | 100 | 0.02163 | 0.08898 | 0.2431 | 0.2837 | 10 | 0.2199 | 0.2199 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 200 | 2 | 100 | 0.2768 | 0.01518 | 18.24 | 112.4 | 0 | 28.8 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 200 | 2 | 100 | 0.2636 | 0.01529 | 17.25 | 102.4 | 0 | 14.25 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 200 | 2 | 100 | 0.04305 | 0.08358 | 0.5151 | 0.6075 | 0 | 23.99 | 23.99 |
| four_rooms_15 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 200 | 2 | 100 | 0.04305 | 0.1663 | 0.2588 | 0.2802 | 20 | 0.2203 | 0.2203 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 200 | 16 | 12.5 | 0.02776 | 0.879 | 0.03159 | 1.562 | 0 | 9.575 | 12.83 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 200 | 16 | 12.5 | 0.02697 | 0.8897 | 0.03031 | 0.9446 | 0 | 5.148 | 6.806 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 200 | 16 | 12.5 | 0.004986 | 1.442 | 0.003457 | 0.008579 | 0 | 0.8051 | 10.45 |
| four_rooms_15 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 200 | 16 | 12.5 | 0.004986 | 1.479 | 0.003373 | 0.008078 | 16 | 0.01205 | 0.1768 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 200 | 16 | 12.5 | 0.1388 | 0.9746 | 0.1424 | 1.224 | 0 | 23.87 | 25.82 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 200 | 16 | 12.5 | 0.1352 | 0.9938 | 0.136 | 1.019 | 0 | 11.61 | 14.19 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 200 | 16 | 12.5 | 0.02542 | 3.745 | 0.006787 | 0.008814 | 0 | 9.141 | 10.95 |
| four_rooms_15 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 200 | 16 | 12.5 | 0.02542 | 3.936 | 0.006458 | 0.008267 | 80 | 0.1588 | 0.2194 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 200 | 16 | 12.5 | 0.2787 | 1.093 | 0.2549 | 1.2 | 0 | 23.87 | 25.83 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 200 | 16 | 12.5 | 0.2686 | 1.118 | 0.2401 | 1.044 | 0 | 11.61 | 14.19 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 200 | 16 | 12.5 | 0.05045 | 6.687 | 0.007544 | 0.00866 | 0 | 27.52 | 27.52 |
| four_rooms_15 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 200 | 16 | 12.5 | 0.05045 | 7.01 | 0.007197 | 0.008205 | 160 | 0.1588 | 0.2194 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 127 | 2 | 63.5 | 0.01728 | 0.004594 | 3.762 | 84.64 | 0 | 4.314 | 13.93 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 127 | 2 | 63.5 | 0.01745 | 0.004558 | 3.828 | 103.5 | 0 | 2.14 | 6.816 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 127 | 2 | 63.5 | 0.003834 | 0.00673 | 0.5697 | 1.638 | 0 | 4.419 | 14.27 |
| maze_17 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 127 | 2 | 63.5 | 0.003834 | 0.009355 | 0.4098 | 0.7722 | 2 | 3.823430461125099e-11 | 3.823430461125099e-11 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 127 | 2 | 63.5 | 0.08645 | 0.005263 | 16.43 | 99 | 0 | 17.94 | 30.49 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 127 | 2 | 63.5 | 0.08491 | 0.00524 | 16.2 | 99.89 | 0 | 9.451 | 14.96 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 127 | 2 | 63.5 | 0.01902 | 0.01566 | 1.215 | 1.688 | 0 | 7.445 | 31.22 |
| maze_17 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 127 | 2 | 63.5 | 0.01902 | 0.02885 | 0.6592 | 0.7775 | 10 | 3.823430461125099e-11 | 3.823430461125099e-11 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 127 | 2 | 63.5 | 0.1732 | 0.006127 | 28.27 | 99.71 | 0 | 17.94 | 30.49 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 127 | 2 | 63.5 | 0.1693 | 0.005997 | 28.24 | 105.4 | 0 | 9.451 | 14.96 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 127 | 2 | 63.5 | 0.03793 | 0.02699 | 1.405 | 1.679 | 0 | 7.445 | 31.22 |
| maze_17 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 127 | 2 | 63.5 | 0.03793 | 0.05326 | 0.7122 | 0.7762 | 20 | 5.326583618625591e-11 | 5.326583618625591e-11 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 127 | 38 | 3.342 | 0.0179 | 1.554 | 0.01152 | 0.03808 | 0 | 8.472 | 15.22 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 127 | 38 | 3.342 | 0.0172 | 1.542 | 0.01115 | 0.03749 | 0 | 4.278 | 7.686 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 127 | 38 | 3.342 | 0.004282 | 1.865 | 0.002296 | 0.005478 | 0 | 5.329070518200751e-15 | 1.3482548411047901e-11 |
| maze_17 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 127 | 38 | 3.342 | 0.004282 | 1.887 | 0.002269 | 0.005327 | 38 | 5.329070518200751e-15 | 1.3482548411047901e-11 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 127 | 38 | 3.342 | 0.08842 | 2.98 | 0.02968 | 0.04664 | 0 | 8.472 | 23.27 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 127 | 38 | 3.342 | 0.08526 | 3.108 | 0.02743 | 0.04212 | 0 | 4.278 | 10.39 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 127 | 38 | 3.342 | 0.02112 | 4.96 | 0.004258 | 0.005449 | 0 | 4.504840944719035e-11 | 4.504840944719035e-11 |
| maze_17 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 127 | 38 | 3.342 | 0.02112 | 5.073 | 0.004163 | 0.005294 | 190 | 4.504840944719035e-11 | 4.504840944719035e-11 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 127 | 38 | 3.342 | 0.1775 | 4.438 | 0.03999 | 0.0529 | 0 | 21.38 | 30.47 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 127 | 38 | 3.342 | 0.1727 | 4.867 | 0.03548 | 0.04564 | 0 | 10.34 | 13.87 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 127 | 38 | 3.342 | 0.04352 | 9.39 | 0.004635 | 0.00524 | 0 | 5.022 | 31.14 |
| maze_17 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 127 | 38 | 3.342 | 0.04352 | 9.177 | 0.004742 | 0.005377 | 380 | 4.504840944719035e-11 | 4.504840944719035e-11 |
