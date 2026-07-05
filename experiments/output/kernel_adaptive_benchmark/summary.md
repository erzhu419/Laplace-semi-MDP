# Kernel Approximation Benchmark

Generated: 2026-07-05T14:49:19
map_specs = ['corridor:128', 'open_room:12', 'maze:13']
methods = ['endpoints']
k_values = [64, 128]
adaptive_tail_tols = [0.001, 1e-06]
adaptive_max_steps = 512

This isolates the current upfront bottleneck by comparing exact first-hit Green solves against fixed-K and adaptive Neumann-prefix kernels.

- best approximate kernel-time speedup vs exact: `140.5x`
- best approximate total-time speedup vs exact: `139.9x`
- worst start-value difference vs exact: `4.071`

| map | method_spec | kernel_label | first_hit_used_steps_max | first_hit_tail_bound_max | n_states | n_boundary | kernel_time_sec | compressed_total_time_sec | kernel_time_speedup_vs_exact | total_time_speedup_vs_exact | start_value_abs_diff_vs_exact | start_gap_vs_full | value_gap_max_vs_full | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | exact | 0 | 0.0 | 128 | 2 | 2.781 | 2.781 | 1 | 1 | 0.0 | 3.725375563590205e-11 | 3.725375563590205e-11 | 1566 | 0.1036 |  |
| corridor_128 | endpoints | truncated_K64 | 64 | 4.603 | 128 | 2 | 0.02522 | 0.02533 | 110.3 | 109.8 | 4.071 | 4.071 | 4.071 | 4255 | 14.38 |  |
| corridor_128 | endpoints | truncated_K128 | 128 | 0.9758 | 128 | 2 | 0.0296 | 0.02971 | 93.95 | 93.63 | 0.1233 | 0.1233 | 0.1233 | 4302 | 13.06 |  |
| corridor_128 | endpoints | adaptive_eps0.001 | 150 | 0.0005939 | 128 | 2 | 0.03146 | 0.03157 | 88.4 | 88.09 | 1.249e-05 | 1.249e-05 | 1.249e-05 | 3755 | 11.65 |  |
| corridor_128 | endpoints | adaptive_eps1e-06 | 160 | 7.468e-07 | 128 | 2 | 0.03206 | 0.03218 | 86.74 | 86.43 | 1.028e-08 | 1.024e-08 | 1.024e-08 | 3538 | 11.67 |  |
| open_room_12 | endpoints | exact | 0 | 0.0 | 144 | 2 | 3.687 | 3.687 | 1 | 1 | 0.0 | 0.07851 | 0.07851 | 599.8 | 0.02584 |  |
| open_room_12 | endpoints | truncated_K64 | 64 | 1.5554812487983104e-17 | 144 | 2 | 0.03862 | 0.03874 | 95.47 | 95.18 | 3.552713678800501e-15 | 0.07851 | 0.07851 | 1439 | 3.744 |  |
| open_room_12 | endpoints | truncated_K128 | 128 | 8.85607404182199e-47 | 144 | 2 | 0.03494 | 0.03505 | 105.5 | 105.2 | 3.552713678800501e-15 | 0.07851 | 0.07851 | 1211 | 3.409 |  |
| open_room_12 | endpoints | adaptive_eps0.001 | 33 | 0.0009628 | 144 | 2 | 0.02624 | 0.02636 | 140.5 | 139.9 | 4.766e-05 | 0.07846 | 0.07846 | 1098 | 4.51 |  |
| open_room_12 | endpoints | adaptive_eps1e-06 | 41 | 3.737e-07 | 144 | 2 | 0.02767 | 0.02777 | 133.3 | 132.8 | 1.773e-08 | 0.07851 | 0.07851 | 1374 | 4.318 |  |
| maze_13 | endpoints | exact | 0 | 0.0 | 71 | 2 | 0.008605 | 0.008697 | 1 | 1 | 0.0 | 1.6697754290362354e-13 | 1.6697754290362354e-13 | 639.3 | 6.088 |  |
| maze_13 | endpoints | truncated_K64 | 64 | 3.527793986978237e-18 | 71 | 2 | 0.01196 | 0.01206 | 0.7195 | 0.7213 | 7.105427357601002e-15 | 1.5987211554602254e-13 | 1.5987211554602254e-13 | 733.4 | 5.379 |  |
| maze_13 | endpoints | truncated_K128 | 128 | 4.941463492309961e-52 | 71 | 2 | 0.01532 | 0.01542 | 0.5616 | 0.5641 | 7.105427357601002e-15 | 1.5987211554602254e-13 | 1.5987211554602254e-13 | 784 | 4.259 |  |
| maze_13 | endpoints | adaptive_eps0.001 | 35 | 0.0007283 | 71 | 2 | 0.009552 | 0.009644 | 0.9009 | 0.9018 | 2.969e-05 | 2.969e-05 | 2.969e-05 | 756 | 6.596 |  |
| maze_13 | endpoints | adaptive_eps1e-06 | 42 | 4.298e-07 | 71 | 2 | 0.009933 | 0.01003 | 0.8663 | 0.8673 | 1.548e-08 | 1.548e-08 | 1.548e-08 | 765.8 | 6.475 |  |
