# Edge Reward Kernel Multi-Task

Generated: 2026-07-05T23:33:52
map_specs = ['corridor:128', 'open_room:16', 'four_rooms:15', 'maze:17']
methods = ['endpoints', 'turn_articulation']
task_counts = [1, 5, 10], max_tasks = 10
additive_reward_kinds = ['sparse', 'dense']

This experiment keeps the decision boundary graph fixed and moves task variation into edge reward or event kernels.
Additive rewards use exact discounted occupancy relabeling; terminal goals use exact query-time first-hit event kernels.

## Summary

| variant | task_type | n_rows | median_n_boundary | median_total_speedup | best_total_speedup | median_planning_speedup | max_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_B_edge_reward_kernel | additive_dense | 24 | 2 | 2.999 | 27.72 | 97.72 | 14.25 |
| fixed_B_edge_reward_kernel | additive_sparse | 24 | 2 | 3.083 | 28.32 | 99.39 | 28.8 |
| fixed_B_event_hit_kernel | terminal_goal | 24 | 2 | 0.3945 | 1.717 | 0.538 | 27.52 |

## Rows

| map | method_spec | variant | task_type | task_count | n_states | n_boundary | state_compression_ratio | full_total_time_sec | graph_total_time_sec | amortized_speedup_vs_full_vi | planning_only_speedup_vs_full_vi | start_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 128 | 2 | 64 | 0.01659 | 0.005147 | 3.224 | 171 | 3.322 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 128 | 2 | 64 | 0.01608 | 0.005127 | 3.137 | 209.1 | 1.485 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 128 | 2 | 64 | 0.003672 | 0.007125 | 0.5154 | 1.77 | 3.413447302591521e-11 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 128 | 2 | 64 | 0.08245 | 0.005472 | 15.07 | 195.5 | 15.37 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 128 | 2 | 64 | 0.08042 | 0.005475 | 14.69 | 189.2 | 8.288 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 128 | 2 | 64 | 0.02069 | 0.01539 | 1.344 | 2.001 | 3.413447302591521e-11 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 128 | 2 | 64 | 0.1665 | 0.005897 | 28.24 | 196.6 | 16.41 |
| corridor_128 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 128 | 2 | 64 | 0.1621 | 0.005912 | 27.41 | 188 | 8.315 |
| corridor_128 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 128 | 2 | 64 | 0.04102 | 0.02572 | 1.595 | 1.984 | 4.735767333841068e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 128 | 2 | 64 | 0.01695 | 0.005762 | 2.943 | 183.6 | 3.322 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 128 | 2 | 64 | 0.01644 | 0.005747 | 2.861 | 211.4 | 1.485 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 128 | 2 | 64 | 0.004049 | 0.007757 | 0.5221 | 1.94 | 3.413447302591521e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 128 | 2 | 64 | 0.08449 | 0.006091 | 13.87 | 200.2 | 15.37 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 128 | 2 | 64 | 0.08253 | 0.006084 | 13.57 | 198.8 | 8.288 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 128 | 2 | 64 | 0.02279 | 0.01602 | 1.422 | 2.202 | 3.413447302591521e-11 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 128 | 2 | 64 | 0.1696 | 0.006497 | 26.1 | 204.9 | 16.41 |
| corridor_128 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 128 | 2 | 64 | 0.1652 | 0.006485 | 25.47 | 202.5 | 8.315 |
| corridor_128 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 128 | 2 | 64 | 0.04508 | 0.02625 | 1.717 | 2.19 | 4.735767333841068e-11 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 256 | 2 | 128 | 0.03666 | 0.02365 | 1.55 | 118.5 | 13.9 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 256 | 2 | 128 | 0.03624 | 0.02362 | 1.534 | 126.3 | 6.536 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 256 | 2 | 128 | 0.00683 | 0.03668 | 0.1862 | 0.5118 | 4.912 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 256 | 2 | 128 | 0.1862 | 0.0247 | 7.538 | 136.6 | 13.9 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 256 | 2 | 128 | 0.1822 | 0.0246 | 7.408 | 144 | 6.578 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 256 | 2 | 128 | 0.03321 | 0.09026 | 0.3679 | 0.4962 | 23.37 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 256 | 2 | 128 | 0.3728 | 0.02602 | 14.33 | 139.1 | 17.22 |
| open_room_16 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 256 | 2 | 128 | 0.3648 | 0.02604 | 14.01 | 135 | 9.1 |
| open_room_16 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 256 | 2 | 128 | 0.06701 | 0.1572 | 0.4264 | 0.5007 | 25.74 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 256 | 4 | 64 | 0.03652 | 0.1234 | 0.296 | 36.49 | 6.49 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 256 | 4 | 64 | 0.03646 | 0.1234 | 0.2955 | 36.31 | 3.368 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 256 | 4 | 64 | 0.007779 | 0.1986 | 0.03917 | 0.1021 | 9.667 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 256 | 4 | 64 | 0.1908 | 0.1278 | 1.493 | 35.62 | 11.41 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 256 | 4 | 64 | 0.1842 | 0.1274 | 1.446 | 36.76 | 6.411 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 256 | 4 | 64 | 0.03777 | 0.5086 | 0.07428 | 0.09782 | 23.37 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 256 | 4 | 64 | 0.3812 | 0.1328 | 2.87 | 36.5 | 13.48 |
| open_room_16 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 256 | 4 | 64 | 0.3706 | 0.1324 | 2.798 | 36.94 | 6.411 |
| open_room_16 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 256 | 4 | 64 | 0.07613 | 0.8972 | 0.08485 | 0.09826 | 26.32 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 200 | 2 | 100 | 0.02639 | 0.01288 | 2.049 | 103.5 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 200 | 2 | 100 | 0.02538 | 0.01288 | 1.97 | 99.44 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 200 | 2 | 100 | 0.004313 | 0.01962 | 0.2198 | 0.6163 | 0.8064 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 200 | 2 | 100 | 0.1365 | 0.01394 | 9.796 | 104.2 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 200 | 2 | 100 | 0.1285 | 0.01391 | 9.233 | 99.87 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 200 | 2 | 100 | 0.02078 | 0.04935 | 0.4211 | 0.5659 | 21.98 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 200 | 2 | 100 | 0.2733 | 0.01522 | 17.96 | 105.4 | 28.8 |
| four_rooms_15 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 200 | 2 | 100 | 0.2556 | 0.01523 | 16.78 | 98.02 | 14.25 |
| four_rooms_15 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 200 | 2 | 100 | 0.04127 | 0.08579 | 0.4811 | 0.5641 | 23.99 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 200 | 16 | 12.5 | 0.02701 | 0.8586 | 0.03146 | 1.521 | 9.575 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 200 | 16 | 12.5 | 0.02624 | 0.8686 | 0.03021 | 0.947 | 5.148 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 200 | 16 | 12.5 | 0.004779 | 1.406 | 0.003399 | 0.008456 | 0.8051 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 200 | 16 | 12.5 | 0.1357 | 0.9561 | 0.1419 | 1.177 | 23.87 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 200 | 16 | 12.5 | 0.1323 | 0.9713 | 0.1362 | 1.015 | 11.61 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 200 | 16 | 12.5 | 0.02415 | 3.657 | 0.006605 | 0.008577 | 9.141 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 200 | 16 | 12.5 | 0.2704 | 1.076 | 0.2512 | 1.148 | 23.87 |
| four_rooms_15 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 200 | 16 | 12.5 | 0.265 | 1.098 | 0.2414 | 1.031 | 11.61 |
| four_rooms_15 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 200 | 16 | 12.5 | 0.04814 | 6.542 | 0.007359 | 0.008444 | 27.52 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 1 | 127 | 2 | 63.5 | 0.0172 | 0.004556 | 3.776 | 86.14 | 4.314 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 1 | 127 | 2 | 63.5 | 0.01688 | 0.004582 | 3.684 | 74.68 | 2.14 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 1 | 127 | 2 | 63.5 | 0.003723 | 0.006632 | 0.5614 | 1.636 | 4.419 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 5 | 127 | 2 | 63.5 | 0.08766 | 0.005276 | 16.61 | 95.3 | 17.94 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 5 | 127 | 2 | 63.5 | 0.08462 | 0.005242 | 16.14 | 95.49 | 9.451 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 5 | 127 | 2 | 63.5 | 0.01853 | 0.01538 | 1.204 | 1.68 | 7.445 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_sparse | 10 | 127 | 2 | 63.5 | 0.1757 | 0.006204 | 28.32 | 95.06 | 17.94 |
| maze_17 | endpoints | fixed_B_edge_reward_kernel | additive_dense | 10 | 127 | 2 | 63.5 | 0.1688 | 0.006089 | 27.72 | 97.42 | 9.451 |
| maze_17 | endpoints | fixed_B_event_hit_kernel | terminal_goal | 10 | 127 | 2 | 63.5 | 0.03746 | 0.02692 | 1.392 | 1.661 | 7.445 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 1 | 127 | 38 | 3.342 | 0.01794 | 1.561 | 0.01149 | 0.03699 | 8.472 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 1 | 127 | 38 | 3.342 | 0.01726 | 1.549 | 0.01114 | 0.03648 | 4.278 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 1 | 127 | 38 | 3.342 | 0.004288 | 1.852 | 0.002316 | 0.00553 | 5.329070518200751e-15 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 5 | 127 | 38 | 3.342 | 0.08826 | 3.045 | 0.02899 | 0.04484 | 8.472 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 5 | 127 | 38 | 3.342 | 0.0867 | 3.168 | 0.02737 | 0.04145 | 4.278 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 5 | 127 | 38 | 3.342 | 0.02122 | 4.943 | 0.004293 | 0.005488 | 4.504840944719035e-11 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_sparse | 10 | 127 | 38 | 3.342 | 0.1775 | 4.544 | 0.03906 | 0.05119 | 21.38 |
| maze_17 | turn_articulation | fixed_B_edge_reward_kernel | additive_dense | 10 | 127 | 38 | 3.342 | 0.1748 | 5.134 | 0.03405 | 0.04308 | 10.34 |
| maze_17 | turn_articulation | fixed_B_event_hit_kernel | terminal_goal | 10 | 127 | 38 | 3.342 | 0.04696 | 9.34 | 0.005028 | 0.005683 | 5.022 |
