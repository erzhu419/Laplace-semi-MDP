# Kernel Approximation Benchmark

Generated: 2026-07-05T14:39:35
map_specs = ['corridor:32', 'open_room:7', 'maze:9']
methods = ['endpoints', 'turn_articulation']
k_values = [16, 32, 64]

This isolates the current upfront bottleneck by comparing exact first-hit Green solves against truncated Neumann-prefix kernels.

- best truncated kernel-time speedup vs exact: `1.113x`
- best truncated total-time speedup vs exact: `1.105x`
- worst start-value difference vs exact: `7.714`

| map | method_spec | kernel_label | n_states | n_boundary | kernel_time_sec | compressed_total_time_sec | kernel_time_speedup_vs_exact | total_time_speedup_vs_exact | start_value_abs_diff_vs_exact | start_gap_vs_full | value_gap_max_vs_full | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_32 | endpoints | exact | 32 | 2 | 0.003888 | 0.003989 | 1 | 1 | 0.0 | 2.091127271341975e-11 | 2.091127271341975e-11 | 253.4 | 6.063 |  |
| corridor_32 | endpoints | truncated_K16 | 32 | 2 | 0.003987 | 0.004078 | 0.9751 | 0.9782 | 7.714 | 7.714 | 7.714 | 357.9 | 7.347 |  |
| corridor_32 | endpoints | truncated_K32 | 32 | 2 | 0.004446 | 0.004535 | 0.8745 | 0.8797 | 0.2896 | 0.2896 | 0.2896 | 380.6 | 6.893 |  |
| corridor_32 | endpoints | truncated_K64 | 32 | 2 | 0.005761 | 0.005854 | 0.6748 | 0.6814 | 1.7763568394002505e-14 | 2.0893509145025746e-11 | 2.0893509145025746e-11 | 353.2 | 5.154 |  |
| corridor_32 | turn_articulation | exact | 32 | 2 | 0.003917 | 0.004274 | 1 | 1 | 0.0 | 2.091127271341975e-11 | 2.091127271341975e-11 | 363.8 | 7.149 |  |
| corridor_32 | turn_articulation | truncated_K16 | 32 | 2 | 0.003872 | 0.004229 | 1.012 | 1.011 | 7.714 | 7.714 | 7.714 | 343.1 | 7.061 |  |
| corridor_32 | turn_articulation | truncated_K32 | 32 | 2 | 0.004546 | 0.004901 | 0.8616 | 0.8719 | 0.2896 | 0.2896 | 0.2896 | 368.5 | 6.182 |  |
| corridor_32 | turn_articulation | truncated_K64 | 32 | 2 | 0.005688 | 0.006064 | 0.6887 | 0.7047 | 1.7763568394002505e-14 | 2.0893509145025746e-11 | 2.0893509145025746e-11 | 364.3 | 5.03 |  |
| open_room_7 | endpoints | exact | 49 | 2 | 0.006037 | 0.006142 | 1 | 1 | 0.0 | 0.04973 | 0.04973 | 241.9 | 3.814 |  |
| open_room_7 | endpoints | truncated_K16 | 49 | 2 | 0.00609 | 0.006186 | 0.9913 | 0.9929 | 0.006355 | 0.04338 | 0.04338 | 330.3 | 4.679 |  |
| open_room_7 | endpoints | truncated_K32 | 49 | 2 | 0.006625 | 0.006722 | 0.9113 | 0.9137 | 2.035758228657869e-10 | 0.04973 | 0.04973 | 325.5 | 4.318 |  |
| open_room_7 | endpoints | truncated_K64 | 49 | 2 | 0.007721 | 0.007838 | 0.7819 | 0.7836 | 0.0 | 0.04973 | 0.04973 | 267.9 | 3.685 |  |
| open_room_7 | turn_articulation | exact | 49 | 4 | 0.01906 | 0.01994 | 1 | 1 | 0.0 | 0.04973 | 0.04973 | 72.96 | 1.447 |  |
| open_room_7 | turn_articulation | truncated_K16 | 49 | 4 | 0.01712 | 0.01804 | 1.113 | 1.105 | 0.0004726 | 0.04926 | 0.04926 | 64.68 | 1.611 |  |
| open_room_7 | turn_articulation | truncated_K32 | 49 | 4 | 0.02431 | 0.02518 | 0.7841 | 0.7916 | 9.43067846037593e-12 | 0.04973 | 0.04973 | 76.94 | 1.218 |  |
| open_room_7 | turn_articulation | truncated_K64 | 49 | 4 | 0.02473 | 0.02565 | 0.7708 | 0.7774 | 0.0 | 0.04973 | 0.04973 | 66.52 | 1.161 |  |
| maze_9 | endpoints | exact | 31 | 2 | 0.003562 | 0.00365 | 1 | 1 | 0.0 | 1.98667748918524e-11 | 1.98667748918524e-11 | 170.3 | 3.822 |  |
| maze_9 | endpoints | truncated_K16 | 31 | 2 | 0.003824 | 0.003918 | 0.9313 | 0.9317 | 0.004435 | 0.004435 | 0.004435 | 200.3 | 4.451 |  |
| maze_9 | endpoints | truncated_K32 | 31 | 2 | 0.004413 | 0.004515 | 0.8071 | 0.8085 | 1.98614458213342e-11 | 5.329070518200751e-15 | 5.329070518200751e-15 | 192.2 | 4.063 |  |
| maze_9 | endpoints | truncated_K64 | 31 | 2 | 0.005411 | 0.005543 | 0.6582 | 0.6586 | 1.7763568394002505e-15 | 1.98685512486918e-11 | 1.98685512486918e-11 | 142.9 | 3.14 |  |
| maze_9 | turn_articulation | exact | 31 | 8 | 0.04176 | 0.04662 | 1 | 1 | 0.0 | 1.9126034089822497e-11 | 1.9126034089822497e-11 | 3.813 | 0.3746 |  |
| maze_9 | turn_articulation | truncated_K16 | 31 | 8 | 0.04306 | 0.04784 | 0.9699 | 0.9744 | 3.471e-08 | 3.469e-08 | 3.554e-07 | 3.877 | 0.3629 |  |
| maze_9 | turn_articulation | truncated_K32 | 31 | 8 | 0.05287 | 0.0578 | 0.7899 | 0.8065 | 3.552713678800501e-15 | 1.9122481376143696e-11 | 1.9122481376143696e-11 | 3.756 | 0.3022 |  |
| maze_9 | turn_articulation | truncated_K64 | 31 | 8 | 0.07291 | 0.07774 | 0.5728 | 0.5997 | 3.552713678800501e-15 | 1.9122481376143696e-11 | 1.9122481376143696e-11 | 3.861 | 0.2257 |  |
