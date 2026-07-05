# Kernel Approximation Benchmark

Generated: 2026-07-05T14:41:58
map_specs = ['corridor:128', 'open_room:12']
methods = ['endpoints']
k_values = [32, 64, 128]

This isolates the current upfront bottleneck by comparing exact first-hit Green solves against truncated Neumann-prefix kernels.

- best truncated kernel-time speedup vs exact: `146.1x`
- best truncated total-time speedup vs exact: `145.3x`
- worst start-value difference vs exact: `11.67`

| map | method_spec | kernel_label | n_states | n_boundary | kernel_time_sec | compressed_total_time_sec | kernel_time_speedup_vs_exact | total_time_speedup_vs_exact | start_value_abs_diff_vs_exact | start_gap_vs_full | value_gap_max_vs_full | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | exact | 128 | 2 | 2.968 | 2.968 | 1 | 1 | 0.0 | 3.725375563590205e-11 | 3.725375563590205e-11 | 2050 | 0.0987 |  |
| corridor_128 | endpoints | truncated_K32 | 128 | 2 | 0.02031 | 0.02043 | 146.1 | 145.3 | 11.67 | 11.67 | 11.67 | 3940 | 18.47 |  |
| corridor_128 | endpoints | truncated_K64 | 128 | 2 | 0.02195 | 0.02205 | 135.2 | 134.6 | 4.071 | 4.071 | 4.071 | 4488 | 17.82 |  |
| corridor_128 | endpoints | truncated_K128 | 128 | 2 | 0.02494 | 0.02504 | 119 | 118.5 | 0.1233 | 0.1233 | 0.1233 | 4103 | 15.01 |  |
| open_room_12 | endpoints | exact | 144 | 2 | 3.3 | 3.3 | 1 | 1 | 0.0 | 0.07851 | 0.07851 | 609.5 | 0.02903 |  |
| open_room_12 | endpoints | truncated_K32 | 144 | 2 | 0.02499 | 0.02511 | 132.1 | 131.4 | 0.0001262 | 0.07838 | 0.07838 | 1224 | 4.904 |  |
| open_room_12 | endpoints | truncated_K64 | 144 | 2 | 0.02641 | 0.02652 | 124.9 | 124.5 | 3.552713678800501e-15 | 0.07851 | 0.07851 | 1381 | 4.591 |  |
| open_room_12 | endpoints | truncated_K128 | 144 | 2 | 0.02939 | 0.02952 | 112.3 | 111.8 | 3.552713678800501e-15 | 0.07851 | 0.07851 | 1122 | 4.263 |  |
