# Large-Scale Compression

Generated: 2026-07-05T14:48:47
map_specs = ['corridor:64,128', 'open_room:12', 'maze:13']
methods = ['endpoints', 'turn_articulation']
first_hit_mode = adaptive, first_hit_truncation_steps = 512
gamma = 0.97, slip = 0.05

This run intentionally omits policy iteration so larger tabular maps do not pay the dense linear-solve cost. It measures the core claim: full-state Bellman propagation versus first-boundary graph-SMDP planning after graph/kernel construction.

- max states evaluated: `144`
- best total wall-time speedup over full VI: `10.68x`
- best planning-only speedup over full VI: `4097x`
- worst graph start-value gap: `0.07851`
- failed rows: `0`

## Method Summary

| method_spec | n_rows | max_n_states | median_total_speedup | best_total_speedup | median_planning_speedup | best_planning_speedup | max_start_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 4 | 144 | 6.822 | 9.327 | 978.1 | 2804 | 0.07851 |
| turn_articulation | 4 | 144 | 5.11 | 10.68 | 676 | 4097 | 0.07851 |

## Rows

| map | method_spec | first_hit_mode | first_hit_truncation_steps | first_hit_used_steps_max | first_hit_tail_bound_max | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | adaptive | 512 | 87 | 5.982e-07 | 64 | 2 | 32 | 380 | 0.08168 | 0.01215 | 9.527e-05 | 857.3 | 6.668 | 6080 | 2.946e-08 | 0.0 | 0.0 |  |
| corridor_64 | turn_articulation | adaptive | 512 | 87 | 5.982e-07 | 64 | 2 | 32 | 380 | 0.1006 | 0.01251 | 8.714e-05 | 1154 | 7.981 | 6080 | 2.946e-08 | 0.0 | 0.0 |  |
| corridor_128 | endpoints | adaptive | 512 | 160 | 7.468e-07 | 128 | 2 | 64 | 764 | 0.2938 | 0.03139 | 0.0001048 | 2804 | 9.327 | 2.15e+04 | 1.024e-08 | 0.0 | 0.0 |  |
| corridor_128 | turn_articulation | adaptive | 512 | 160 | 7.468e-07 | 128 | 2 | 64 | 764 | 0.3624 | 0.03386 | 8.845e-05 | 4097 | 10.68 | 2.15e+04 | 1.024e-08 | 0.0 | 0.0 |  |
| open_room_12 | endpoints | adaptive | 512 | 41 | 3.737e-07 | 144 | 2 | 72 | 1144 | 0.09671 | 0.02606 | 8.801e-05 | 1099 | 3.698 | 6912 | 0.07851 | 0.0 | 0.0 |  |
| open_room_12 | turn_articulation | adaptive | 512 | 38 | 8.604e-07 | 144 | 4 | 36 | 143 | 0.1401 | 0.06182 | 0.0007079 | 197.9 | 2.24 | 576 | 0.07851 | 0.0 | 0.0 |  |
| maze_13 | endpoints | adaptive | 512 | 42 | 4.298e-07 | 71 | 2 | 35.5 | 422 | 0.0677 | 0.009614 | 8.903e-05 | 760.4 | 6.977 | 3763 | 1.548e-08 | 0.0 | 0.0 |  |
| maze_13 | turn_articulation | adaptive | 512 | 24 | 9.741e-07 | 71 | 18 | 3.944 | 1.546 | 0.06422 | 0.2002 | 0.03605 | 1.781 | 0.2719 | 2.733 | 7.147e-07 | 0.0 | 0.0 |  |
