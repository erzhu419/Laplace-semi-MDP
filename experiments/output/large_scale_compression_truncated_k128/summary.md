# Large-Scale Compression

Generated: 2026-07-05T14:42:16
map_specs = ['corridor:64,128', 'open_room:12', 'maze:13']
methods = ['endpoints', 'turn_articulation']
first_hit_mode = truncated, first_hit_truncation_steps = 128
gamma = 0.97, slip = 0.05

This run intentionally omits policy iteration so larger tabular maps do not pay the dense linear-solve cost. It measures the core claim: full-state Bellman propagation versus first-boundary graph-SMDP planning after graph/kernel construction.

- max states evaluated: `144`
- best total wall-time speedup over full VI: `31.91x`
- best planning-only speedup over full VI: `5075x`
- worst graph start-value gap: `0.1233`
- failed rows: `0`

## Method Summary

| method_spec | n_rows | max_n_states | median_total_speedup | best_total_speedup | median_planning_speedup | best_planning_speedup | max_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 4 | 144 | 5.906 | 7.303 | 958.1 | 1865 | 0.1233 |
| turn_articulation | 4 | 144 | 5.352 | 31.91 | 735.4 | 5075 | 0.1233 |

## Rows

| map | method_spec | first_hit_mode | first_hit_truncation_steps | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | truncated | 128 | 64 | 2 | 32 | 380 | 0.08104 | 0.01119 | 9.576e-05 | 846.3 | 7.182 | 6080 | 3.3711700098137953e-11 | 0.0 | 0.0 |  |
| corridor_64 | turn_articulation | truncated | 128 | 64 | 2 | 32 | 380 | 0.09873 | 0.01143 | 8.525e-05 | 1158 | 8.577 | 6080 | 3.3711700098137953e-11 | 0.0 | 0.0 |  |
| corridor_128 | endpoints | truncated | 128 | 128 | 2 | 64 | 764 | 0.309 | 0.04215 | 0.0001657 | 1865 | 7.303 | 2.15e+04 | 0.1233 | 0.0 | 0.0 |  |
| corridor_128 | turn_articulation | truncated | 128 | 128 | 2 | 64 | 764 | 0.9177 | 0.02858 | 0.0001808 | 5075 | 31.91 | 2.15e+04 | 0.1233 | 0.0 | 0.0 |  |
| open_room_12 | endpoints | truncated | 128 | 144 | 2 | 72 | 1144 | 0.09718 | 0.02863 | 9.083e-05 | 1070 | 3.383 | 6912 | 0.07851 | 0.0 | 0.0 |  |
| open_room_12 | turn_articulation | truncated | 128 | 144 | 4 | 36 | 143 | 0.1359 | 0.06343 | 0.0004347 | 312.6 | 2.127 | 576 | 0.07851 | 0.0 | 0.0 |  |
| maze_13 | endpoints | truncated | 128 | 71 | 2 | 35.5 | 422 | 0.05552 | 0.01191 | 8.814e-05 | 629.9 | 4.629 | 3763 | 1.5987211554602254e-13 | 0.0 | 0.0 |  |
| maze_13 | turn_articulation | truncated | 128 | 71 | 18 | 3.944 | 1.546 | 0.08137 | 1.995 | 0.08542 | 0.9526 | 0.03911 | 2.733 | 1.1652900866465643e-12 | 0.0 | 0.0 |  |
