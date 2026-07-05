# Large-Scale Compression

Generated: 2026-07-05T14:22:30
map_specs = ['corridor:64,128', 'open_room:12', 'maze:13']
methods = ['endpoints', 'turn_articulation', 'graph_rd_surrogate_joint']
gamma = 0.97, slip = 0.05

This run intentionally omits policy iteration so larger tabular maps do not pay the dense linear-solve cost. It measures the core claim: full-state Bellman propagation versus first-boundary graph-SMDP planning after graph/kernel construction.

- max states evaluated: `144`
- best total wall-time speedup over full VI: `10.6x`
- best planning-only speedup over full VI: `2471x`
- worst graph start-value gap: `0.07851`
- failed rows: `0`

## Method Summary

| method_spec | n_rows | max_n_states | median_total_speedup | best_total_speedup | median_planning_speedup | best_planning_speedup | max_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 4 | 144 | 2.893 | 8.995 | 826 | 2333 | 0.07851 |
| graph_rd_surrogate_joint | 4 | 144 | 0.05239 | 0.4399 | 859.6 | 2471 | 0.07851 |
| turn_articulation | 4 | 144 | 0.1386 | 10.6 | 683.8 | 2316 | 0.07851 |

## Rows

| map | method_spec | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | 64 | 2 | 32 | 380 | 0.08151 | 0.00897 | 9.169e-05 | 888.9 | 8.995 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |  |
| corridor_64 | turn_articulation | 64 | 2 | 32 | 380 | 0.1019 | 0.009527 | 8.622e-05 | 1182 | 10.6 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |  |
| corridor_64 | graph_rd_surrogate_joint | 64 | 2 | 32 | 380 | 0.1027 | 0.2335 | 9.023e-05 | 1139 | 0.4399 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |  |
| corridor_128 | endpoints | 128 | 2 | 64 | 764 | 0.3149 | 2.501 | 0.000135 | 2333 | 0.1259 | 2.15e+04 | 3.725375563590205e-11 | 0.0 | 0.0 |  |
| corridor_128 | turn_articulation | 128 | 2 | 64 | 764 | 0.3622 | 2.48 | 0.0001564 | 2316 | 0.146 | 2.15e+04 | 3.725375563590205e-11 | 0.0 | 0.0 |  |
| corridor_128 | graph_rd_surrogate_joint | 128 | 2 | 64 | 764 | 0.3613 | 5.507 | 0.0001462 | 2471 | 0.06561 | 2.15e+04 | 3.725375563590205e-11 | 0.0 | 0.0 |  |
| open_room_12 | endpoints | 144 | 2 | 72 | 1144 | 0.1204 | 5.183 | 0.0001578 | 763 | 0.02323 | 6912 | 0.07851 | 0.0 | 0.0 |  |
| open_room_12 | turn_articulation | 144 | 4 | 36 | 143 | 0.1195 | 17.26 | 0.000645 | 185.3 | 0.006923 | 576 | 0.07851 | 0.0 | 0.0 |  |
| open_room_12 | graph_rd_surrogate_joint | 144 | 2 | 72 | 1144 | 0.1205 | 11.9 | 0.0002074 | 580.7 | 0.01012 | 6912 | 0.07851 | 0.0 | 0.0 |  |
| maze_13 | endpoints | 71 | 2 | 35.5 | 422 | 0.06029 | 0.01056 | 8.935e-05 | 674.8 | 5.661 | 3763 | 1.6697754290362354e-13 | 0.0 | 0.0 |  |
| maze_13 | turn_articulation | 71 | 18 | 3.944 | 1.546 | 0.06527 | 0.4593 | 0.03831 | 1.704 | 0.1312 | 2.733 | 1.1475265182525618e-12 | 0.0 | 0.0 |  |
| maze_13 | graph_rd_surrogate_joint | 71 | 8 | 8.875 | 9.174 | 0.06494 | 1.651 | 0.00686 | 9.467 | 0.03916 | 14.93 | 1.1475265182525618e-12 | 0.0 | 0.0 |  |
