# Large-Scale Compression

Generated: 2026-07-05T14:42:33
map_specs = ['corridor:64,128', 'open_room:12', 'maze:13']
methods = ['endpoints', 'turn_articulation']
first_hit_mode = exact, first_hit_truncation_steps = 32
gamma = 0.97, slip = 0.05

This run intentionally omits policy iteration so larger tabular maps do not pay the dense linear-solve cost. It measures the core claim: full-state Bellman propagation versus first-boundary graph-SMDP planning after graph/kernel construction.

- max states evaluated: `144`
- best total wall-time speedup over full VI: `12.77x`
- best planning-only speedup over full VI: `2384x`
- worst graph start-value gap: `0.07851`
- failed rows: `0`

## Method Summary

| method_spec | n_rows | max_n_states | median_total_speedup | best_total_speedup | median_planning_speedup | best_planning_speedup | max_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 4 | 144 | 3.52 | 10.86 | 775.7 | 1810 | 0.07851 |
| turn_articulation | 4 | 144 | 0.1896 | 12.77 | 717 | 2384 | 0.07851 |

## Rows

| map | method_spec | first_hit_mode | first_hit_truncation_steps | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | exact | 32 | 64 | 2 | 32 | 380 | 0.08449 | 0.007692 | 8.994e-05 | 939.4 | 10.86 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |  |
| corridor_64 | turn_articulation | exact | 32 | 64 | 2 | 32 | 380 | 0.1041 | 0.008066 | 8.574e-05 | 1214 | 12.77 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |  |
| corridor_128 | endpoints | exact | 32 | 128 | 2 | 64 | 764 | 0.3027 | 2.309 | 0.0001672 | 1810 | 0.1311 | 2.15e+04 | 3.725375563590205e-11 | 0.0 | 0.0 |  |
| corridor_128 | turn_articulation | exact | 32 | 128 | 2 | 64 | 764 | 0.4273 | 3.394 | 0.0001792 | 2384 | 0.1259 | 2.15e+04 | 3.725375563590205e-11 | 0.0 | 0.0 |  |
| open_room_12 | endpoints | exact | 32 | 144 | 2 | 72 | 1144 | 0.1002 | 2.854 | 0.000178 | 562.9 | 0.0351 | 6912 | 0.07851 | 0.0 | 0.0 |  |
| open_room_12 | turn_articulation | exact | 32 | 144 | 4 | 36 | 143 | 0.1225 | 11.87 | 0.0005578 | 219.6 | 0.01032 | 576 | 0.07851 | 0.0 | 0.0 |  |
| maze_13 | endpoints | exact | 32 | 71 | 2 | 35.5 | 422 | 0.06147 | 0.008798 | 0.0001004 | 612.1 | 6.908 | 3763 | 1.6697754290362354e-13 | 0.0 | 0.0 |  |
| maze_13 | turn_articulation | exact | 32 | 71 | 18 | 3.944 | 1.546 | 0.06758 | 0.2294 | 0.03742 | 1.806 | 0.2532 | 2.733 | 1.1475265182525618e-12 | 0.0 | 0.0 |  |
