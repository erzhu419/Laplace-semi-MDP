# Edge Reward Kernel Multi-Task

Generated: 2026-07-06T00:13:32
map_specs = ['corridor:128', 'open_room:16', 'four_rooms:15', 'maze:17']
methods = ['endpoints', 'turn_articulation']
task_counts = [1, 5, 10], max_tasks = 10
additive_reward_kinds = ['sparse', 'dense']

This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.
Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.
The goal-conditioned variant appends query-time local options to the event model while keeping `B` fixed, and counts their interface size separately.
Its shared/batched backend builds one goal-conditioned policy per queried goal and solves all boundary-start event rows together.

## Summary

| variant | task_type | n_rows | median_n_boundary | median_total_speedup | best_total_speedup | median_planning_speedup | max_start_gap | max_boundary_gap | median_goal_interface | median_goal_policies | median_break_even_tasks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_B_edge_reward_kernel | additive_dense | 24 | 2 | 2.996 | 28.93 | 108.6 | 14.25 | 15.52 | 0.0 | 0.0 | 1 |
| fixed_B_edge_reward_kernel | additive_sparse | 24 | 2 | 3.09 | 28.79 | 110 | 28.8 | 30.49 | 0.0 | 0.0 | 1 |
| fixed_B_event_hit_kernel | terminal_goal | 24 | 2 | 0.3858 | 1.793 | 0.5782 | 27.52 | 31.22 | 0.0 | 0.0 | 3 |
| fixed_B_goal_conditioned_event_options | terminal_goal | 24 | 2 | 0.3167 | 1.18 | 0.4408 | 0.3494 | 0.3925 | 18 | 5 | 10 |

## Rows

| map | method_spec | variant | task_type | task_count | n_states | n_boundary | state_compression_ratio | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | planning_only_speedup_vs_full_vi | break_even_num_tasks | goal_option_interface_size | n_goal_policies | policy_build_time_sec | batched_event_solve_time_sec | start_gap_max | boundary_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 128 | 2 | 64 | 0.01711 | 0.005433 | 3.15 | 166.6 | 1 | 0 | 0 | 0.0 | 0.0 | 3.322 | 4.755 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 128 | 2 | 64 | 0.01651 | 0.005415 | 3.049 | 193.8 | 1 | 0 | 0 | 0.0 | 0.0 | 1.485 | 2.141 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 128 | 2 | 64 | 0.003739 | 0.007495 | 0.4989 | 1.727 | 4 | 0 | 0 | 0.0 | 0.0 | 3.413447302591521e-11 | 3.413447302591521e-11 |
| corridor_128 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 128 | 2 | 64 | 0.003739 | 0.008675 | 0.431 | 1.118 | 3 | 2 | 1 | 0.0006601 | 0.0004345 | 3.1885605267234496e-11 | 3.1885605267234496e-11 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 128 | 2 | 64 | 0.08524 | 0.005799 | 14.7 | 181.6 | 1 | 0 | 0 | 0.0 | 0.0 | 15.37 | 15.37 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 128 | 2 | 64 | 0.08246 | 0.005764 | 14.31 | 190 | 1 | 0 | 0 | 0.0 | 0.0 | 8.288 | 8.288 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 128 | 2 | 64 | 0.0214 | 0.01596 | 1.341 | 2.013 | 3 | 0 | 0 | 0.0 | 0.0 | 3.413447302591521e-11 | 6.24496010459552e-11 |
| corridor_128 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 128 | 2 | 64 | 0.0214 | 0.02206 | 0.9705 | 1.28 | 6 | 10 | 5 | 0.003406 | 0.002173 | 3.1885605267234496e-11 | 6.005862474012247e-11 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 128 | 2 | 64 | 0.1703 | 0.006215 | 27.41 | 192.6 | 1 | 0 | 0 | 0.0 | 0.0 | 16.41 | 16.41 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 128 | 2 | 64 | 0.1654 | 0.006213 | 26.62 | 187.3 | 1 | 0 | 0 | 0.0 | 0.0 | 8.315 | 8.315 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 128 | 2 | 64 | 0.04211 | 0.02646 | 1.592 | 1.993 | 3 | 0 | 0 | 0.0 | 0.0 | 4.735767333841068e-11 | 6.24496010459552e-11 |
| corridor_128 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 128 | 2 | 64 | 0.04211 | 0.0385 | 1.094 | 1.27 | 10 | 20 | 10 | 0.006773 | 0.004299 | 4.5147885430196766e-11 | 6.005862474012247e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 128 | 2 | 64 | 0.01728 | 0.005702 | 3.03 | 214.1 | 1 | 0 | 0 | 0.0 | 0.0 | 3.322 | 4.755 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 128 | 2 | 64 | 0.01675 | 0.005691 | 2.943 | 242.2 | 1 | 0 | 0 | 0.0 | 0.0 | 1.485 | 2.141 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 128 | 2 | 64 | 0.004202 | 0.007747 | 0.5424 | 1.977 | 3 | 0 | 0 | 0.0 | 0.0 | 3.413447302591521e-11 | 3.413447302591521e-11 |
| corridor_128 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 128 | 2 | 64 | 0.004202 | 0.009072 | 0.4632 | 1.218 | 3 | 2 | 1 | 0.0008045 | 0.0004293 | 3.1885605267234496e-11 | 3.1885605267234496e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 128 | 2 | 64 | 0.08733 | 0.006053 | 14.43 | 202.7 | 1 | 0 | 0 | 0.0 | 0.0 | 15.37 | 15.37 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 128 | 2 | 64 | 0.08514 | 0.005988 | 14.22 | 232.4 | 1 | 0 | 0 | 0.0 | 0.0 | 8.288 | 8.288 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 128 | 2 | 64 | 0.02351 | 0.01582 | 1.486 | 2.304 | 3 | 0 | 0 | 0.0 | 0.0 | 3.413447302591521e-11 | 6.24496010459552e-11 |
| corridor_128 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 128 | 2 | 64 | 0.02351 | 0.02248 | 1.046 | 1.395 | 5 | 10 | 5 | 0.004011 | 0.002177 | 3.1885605267234496e-11 | 6.005862474012247e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 128 | 2 | 64 | 0.1745 | 0.006434 | 27.13 | 214.9 | 1 | 0 | 0 | 0.0 | 0.0 | 16.41 | 16.41 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 128 | 2 | 64 | 0.1697 | 0.006374 | 26.62 | 225.5 | 1 | 0 | 0 | 0.0 | 0.0 | 8.315 | 8.315 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 128 | 2 | 64 | 0.04643 | 0.0259 | 1.793 | 2.289 | 3 | 0 | 0 | 0.0 | 0.0 | 4.735767333841068e-11 | 6.24496010459552e-11 |
| corridor_128 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 128 | 2 | 64 | 0.04643 | 0.03934 | 1.18 | 1.377 | 9 | 20 | 10 | 0.008103 | 0.004374 | 4.5147885430196766e-11 | 6.005862474012247e-11 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 256 | 2 | 128 | 0.03775 | 0.02369 | 1.593 | 133.1 | 1 | 0 | 0 | 0.0 | 0.0 | 13.9 | 26.14 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 256 | 2 | 128 | 0.03731 | 0.02364 | 1.578 | 158.5 | 1 | 0 | 0 | 0.0 | 0.0 | 6.536 | 11.73 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 256 | 2 | 128 | 0.007346 | 0.03692 | 0.1989 | 0.5436 | inf | 0 | 0 | 0.0 | 0.0 | 4.912 | 4.912 |
| open_room_16 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 256 | 2 | 128 | 0.007346 | 0.04081 | 0.18 | 0.4221 | 6 | 2 | 1 | 0.001808 | 0.002109 | 0.2593 | 0.2593 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 256 | 2 | 128 | 0.1854 | 0.02463 | 7.53 | 152.1 | 1 | 0 | 0 | 0.0 | 0.0 | 13.9 | 26.14 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 256 | 2 | 128 | 0.1819 | 0.02467 | 7.373 | 144.3 | 1 | 0 | 0 | 0.0 | 0.0 | 6.578 | 11.73 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 256 | 2 | 128 | 0.03197 | 0.08937 | 0.3577 | 0.4847 | inf | 0 | 0 | 0.0 | 0.0 | 23.37 | 25.75 |
| open_room_16 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 256 | 2 | 128 | 0.03197 | 0.1074 | 0.2977 | 0.3806 | 18 | 10 | 5 | 0.008059 | 0.01051 | 0.2593 | 0.2813 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 256 | 2 | 128 | 0.3728 | 0.02589 | 14.4 | 150.3 | 1 | 0 | 0 | 0.0 | 0.0 | 17.22 | 26.14 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 256 | 2 | 128 | 0.3633 | 0.02595 | 14 | 142.9 | 1 | 0 | 0 | 0.0 | 0.0 | 9.1 | 11.73 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 256 | 2 | 128 | 0.0645 | 0.1558 | 0.4139 | 0.4871 | inf | 0 | 0 | 0.0 | 0.0 | 25.74 | 26.42 |
| open_room_16 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 256 | 2 | 128 | 0.0645 | 0.1921 | 0.3358 | 0.3824 | 31 | 20 | 10 | 0.01623 | 0.02109 | 0.2593 | 0.2813 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 256 | 4 | 64 | 0.03693 | 0.1245 | 0.2967 | 36.28 | 4 | 0 | 0 | 0.0 | 0.0 | 6.49 | 15.2 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 256 | 4 | 64 | 0.03683 | 0.1245 | 0.296 | 37.21 | 4 | 0 | 0 | 0.0 | 0.0 | 3.368 | 7.197 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 256 | 4 | 64 | 0.008348 | 0.1996 | 0.04182 | 0.1096 | inf | 0 | 0 | 0.0 | 0.0 | 9.667 | 26.49 |
| open_room_16 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 256 | 4 | 64 | 0.008348 | 0.2029 | 0.04113 | 0.105 | 26 | 4 | 1 | 0.001963 | 0.002103 | 0.1784 | 0.3925 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 256 | 4 | 64 | 0.188 | 0.1285 | 1.463 | 37.16 | 4 | 0 | 0 | 0.0 | 0.0 | 11.41 | 28.83 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 256 | 4 | 64 | 0.1866 | 0.1283 | 1.454 | 38.3 | 4 | 0 | 0 | 0.0 | 0.0 | 6.411 | 15.52 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 256 | 4 | 64 | 0.03748 | 0.5015 | 0.07474 | 0.09915 | inf | 0 | 0 | 0.0 | 0.0 | 23.37 | 26.92 |
| open_room_16 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 256 | 4 | 64 | 0.03748 | 0.5179 | 0.07236 | 0.09501 | 72 | 20 | 5 | 0.009214 | 0.01045 | 0.2759 | 0.3925 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 256 | 4 | 64 | 0.377 | 0.1334 | 2.826 | 37.91 | 4 | 0 | 0 | 0.0 | 0.0 | 13.48 | 28.83 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 256 | 4 | 64 | 0.3712 | 0.1333 | 2.785 | 37.88 | 4 | 0 | 0 | 0.0 | 0.0 | 6.411 | 15.52 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 256 | 4 | 64 | 0.07464 | 0.8838 | 0.08446 | 0.09818 | inf | 0 | 0 | 0.0 | 0.0 | 26.32 | 28.31 |
| open_room_16 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 256 | 4 | 64 | 0.07464 | 0.9151 | 0.08157 | 0.09429 | 128 | 40 | 10 | 0.01891 | 0.02096 | 0.3494 | 0.3925 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 200 | 2 | 100 | 0.0268 | 0.01318 | 2.034 | 109.9 | 1 | 0 | 0 | 0.0 | 0.0 | 28.8 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 200 | 2 | 100 | 0.02624 | 0.01317 | 1.992 | 109.3 | 1 | 0 | 0 | 0.0 | 0.0 | 14.25 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 200 | 2 | 100 | 0.004342 | 0.01986 | 0.2186 | 0.6262 | inf | 0 | 0 | 0.0 | 0.0 | 0.8064 | 2.161 |
| four_rooms_15 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 200 | 2 | 100 | 0.004342 | 0.02238 | 0.194 | 0.4595 | 6 | 2 | 1 | 0.001302 | 0.001229 | 0.000575 | 0.1561 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 200 | 2 | 100 | 0.1359 | 0.01413 | 9.618 | 113.2 | 1 | 0 | 0 | 0.0 | 0.0 | 28.8 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 200 | 2 | 100 | 0.1322 | 0.01416 | 9.338 | 107.8 | 1 | 0 | 0 | 0.0 | 0.0 | 14.25 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 200 | 2 | 100 | 0.02082 | 0.04615 | 0.4511 | 0.6267 | inf | 0 | 0 | 0.0 | 0.0 | 21.98 | 21.98 |
| four_rooms_15 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 200 | 2 | 100 | 0.02082 | 0.05755 | 0.3617 | 0.4666 | 15 | 10 | 5 | 0.005875 | 0.005654 | 0.2199 | 0.2199 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 200 | 2 | 100 | 0.2772 | 0.01541 | 17.99 | 111.8 | 1 | 0 | 0 | 0.0 | 0.0 | 28.8 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 200 | 2 | 100 | 0.2654 | 0.01534 | 17.31 | 110.4 | 1 | 0 | 0 | 0.0 | 0.0 | 14.25 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 200 | 2 | 100 | 0.0418 | 0.08112 | 0.5152 | 0.6129 | inf | 0 | 0 | 0.0 | 0.0 | 23.99 | 23.99 |
| four_rooms_15 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 200 | 2 | 100 | 0.0418 | 0.1037 | 0.4031 | 0.4605 | 26 | 20 | 10 | 0.01178 | 0.01151 | 0.2203 | 0.2203 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 200 | 16 | 12.5 | 0.02735 | 0.8643 | 0.03164 | 1.575 | 85 | 0 | 0 | 0.0 | 0.0 | 9.575 | 12.83 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 200 | 16 | 12.5 | 0.02667 | 0.8743 | 0.03051 | 0.9751 | inf | 0 | 0 | 0.0 | 0.0 | 5.148 | 6.806 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 200 | 16 | 12.5 | 0.004997 | 1.413 | 0.003536 | 0.008828 | inf | 0 | 0 | 0.0 | 0.0 | 0.8051 | 10.45 |
| four_rooms_15 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 200 | 16 | 12.5 | 0.004997 | 1.413 | 0.003537 | 0.008835 | 768 | 16 | 1 | 0.001248 | 0.0009173 | 0.01205 | 0.1768 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 200 | 16 | 12.5 | 0.1368 | 0.9583 | 0.1428 | 1.23 | 166 | 0 | 0 | 0.0 | 0.0 | 23.87 | 25.82 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 200 | 16 | 12.5 | 0.1327 | 0.9746 | 0.1362 | 1.04 | 837 | 0 | 0 | 0.0 | 0.0 | 11.61 | 14.19 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 200 | 16 | 12.5 | 0.02494 | 3.672 | 0.006792 | 0.008828 | inf | 0 | 0 | 0.0 | 0.0 | 9.141 | 10.95 |
| four_rooms_15 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 200 | 16 | 12.5 | 0.02494 | 3.682 | 0.006772 | 0.008795 | 2318 | 80 | 5 | 0.006235 | 0.004571 | 0.1588 | 0.2194 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 200 | 16 | 12.5 | 0.2729 | 1.076 | 0.2536 | 1.192 | 193 | 0 | 0 | 0.0 | 0.0 | 23.87 | 25.83 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 200 | 16 | 12.5 | 0.2653 | 1.098 | 0.2415 | 1.056 | 602 | 0 | 0 | 0.0 | 0.0 | 11.61 | 14.19 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 200 | 16 | 12.5 | 0.04974 | 6.561 | 0.00758 | 0.008704 | inf | 0 | 0 | 0.0 | 0.0 | 27.52 | 27.52 |
| four_rooms_15 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 200 | 16 | 12.5 | 0.04974 | 6.525 | 0.007622 | 0.008759 | 4456 | 160 | 10 | 0.01285 | 0.009586 | 0.1588 | 0.2194 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 127 | 2 | 63.5 | 0.01718 | 0.004422 | 3.885 | 110.1 | 1 | 0 | 0 | 0.0 | 0.0 | 4.314 | 13.93 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 127 | 2 | 63.5 | 0.01665 | 0.004423 | 3.764 | 106.3 | 1 | 0 | 0 | 0.0 | 0.0 | 2.14 | 6.816 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 127 | 2 | 63.5 | 0.003681 | 0.006405 | 0.5746 | 1.721 | 3 | 0 | 0 | 0.0 | 0.0 | 4.419 | 14.27 |
| maze_17 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 127 | 2 | 63.5 | 0.003681 | 0.007452 | 0.4939 | 1.155 | 3 | 2 | 1 | 0.0006924 | 0.0004093 | 3.4077629607054405e-11 | 3.4077629607054405e-11 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 127 | 2 | 63.5 | 0.08668 | 0.005179 | 16.74 | 94.99 | 1 | 0 | 0 | 0.0 | 0.0 | 17.94 | 30.49 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 127 | 2 | 63.5 | 0.08396 | 0.005057 | 16.6 | 106.2 | 1 | 0 | 0 | 0.0 | 0.0 | 9.451 | 14.96 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 127 | 2 | 63.5 | 0.01863 | 0.01524 | 1.223 | 1.698 | 3 | 0 | 0 | 0.0 | 0.0 | 7.445 | 31.22 |
| maze_17 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 127 | 2 | 63.5 | 0.01863 | 0.02061 | 0.9038 | 1.14 | 6 | 10 | 5 | 0.003411 | 0.002113 | 3.4077629607054405e-11 | 3.4077629607054405e-11 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 127 | 2 | 63.5 | 0.1729 | 0.006007 | 28.79 | 99.33 | 1 | 0 | 0 | 0.0 | 0.0 | 17.94 | 30.49 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 127 | 2 | 63.5 | 0.1678 | 0.005801 | 28.93 | 109.3 | 1 | 0 | 0 | 0.0 | 0.0 | 9.451 | 14.96 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 127 | 2 | 63.5 | 0.03723 | 0.02624 | 1.419 | 1.694 | 3 | 0 | 0 | 0.0 | 0.0 | 7.445 | 31.22 |
| maze_17 | endpoints | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 127 | 2 | 63.5 | 0.03723 | 0.03687 | 1.01 | 1.142 | 10 | 20 | 10 | 0.006777 | 0.004153 | 4.879296966464608e-11 | 4.879296966464608e-11 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 127 | 38 | 3.342 | 0.01818 | 1.567 | 0.01161 | 0.0377 | inf | 0 | 0 | 0.0 | 0.0 | 8.472 | 15.22 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 127 | 38 | 3.342 | 0.01711 | 1.55 | 0.01104 | 0.03673 | inf | 0 | 0 | 0.0 | 0.0 | 4.278 | 7.686 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 127 | 38 | 3.342 | 0.004214 | 1.864 | 0.002261 | 0.005406 | inf | 0 | 0 | 0.0 | 0.0 | 5.329070518200751e-15 | 1.3482548411047901e-11 |
| maze_17 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 1 | 127 | 38 | 3.342 | 0.004214 | 1.874 | 0.002248 | 0.005333 | inf | 38 | 1 | 0.0008599 | 0.0004099 | 3.552713678800501e-15 | 4.479971948967432e-12 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 127 | 38 | 3.342 | 0.08926 | 3.013 | 0.02962 | 0.04627 | inf | 0 | 0 | 0.0 | 0.0 | 8.472 | 23.27 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 127 | 38 | 3.342 | 0.0857 | 3.128 | 0.0274 | 0.04194 | inf | 0 | 0 | 0.0 | 0.0 | 4.278 | 10.39 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 127 | 38 | 3.342 | 0.02084 | 4.964 | 0.004197 | 0.00537 | inf | 0 | 0 | 0.0 | 0.0 | 4.504840944719035e-11 | 4.504840944719035e-11 |
| maze_17 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 5 | 127 | 38 | 3.342 | 0.02084 | 5.012 | 0.004157 | 0.005304 | inf | 190 | 5 | 0.0042 | 0.001926 | 3.936051484743075e-11 | 3.936051484743075e-11 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 127 | 38 | 3.342 | 0.1783 | 4.467 | 0.03992 | 0.05272 | inf | 0 | 0 | 0.0 | 0.0 | 21.38 | 30.47 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 127 | 38 | 3.342 | 0.1722 | 4.886 | 0.03524 | 0.0453 | inf | 0 | 0 | 0.0 | 0.0 | 10.34 | 13.87 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 127 | 38 | 3.342 | 0.04313 | 9.303 | 0.004636 | 0.005247 | inf | 0 | 0 | 0.0 | 0.0 | 5.022 | 31.14 |
| maze_17 | turn_articulation | fixed_B_goal_conditioned_event_options | terminal_goal | 10 | 127 | 38 | 3.342 | 0.04313 | 8.966 | 0.00481 | 0.005472 | inf | 380 | 10 | 0.008493 | 0.004012 | 3.936051484743075e-11 | 3.936051484743075e-11 |
