# One-Shot RD Green Operator

Generated: 2026-07-10T21:51:09

The one-shot methods freeze the mandatory boundary and probe basis, run one truncated sparse Green pass, apply all RD channels once, and threshold once. They never insert a candidate or recompute the operator. In operator-only mode the benchmark stops there; otherwise it constructs final graph kernels exactly once.

operator_only = True, thresholds = [0.15], probe_count = None, operator_steps = 256, max_splits = 18

## Method Aggregate

| method | n_rows | median_n_boundary | median_state_compression | median_selection_time_sec | median_final_kernel_time_sec | median_total_speedup_vs_sparse_vi | median_selection_speedup_vs_iterative | median_total_speedup_vs_iterative | max_normalized_start_gap | max_normalized_value_gap | median_D_occ | median_D_audit_cvar95 | median_boundary_jaccard_vs_iterative |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| one_shot_rd_t0p15 | 27 | 3 | 192 | 0.04342 | nan | nan | 1610 | nan | nan | nan | nan | nan | nan |

## Rows

| map | slip | method | n_states | n_boundary | state_compression_ratio | selection_time_sec | final_kernel_time_sec | graph_solve_time_sec | total_speedup_vs_sparse_vi | selection_speedup_vs_iterative | normalized_start_gap | normalized_value_gap_max | D_occ | D_audit_cvar95 | boundary_jaccard_vs_iterative |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_256 | 0.0 | one_shot_rd_t0p15 | 256 | 2 | 128 | 0.002617 | nan | nan | nan | 1346 | nan | nan | nan | nan |  |
| corridor_256 | 0.05 | one_shot_rd_t0p15 | 256 | 2 | 128 | 0.002695 | nan | nan | nan | 1610 | nan | nan | nan | nan |  |
| corridor_256 | 0.1 | one_shot_rd_t0p15 | 256 | 2 | 128 | 0.00266 | nan | nan | nan | 1763 | nan | nan | nan | nan |  |
| corridor_512 | 0.0 | one_shot_rd_t0p15 | 512 | 2 | 256 | 0.004976 | nan | nan | nan | 2836 | nan | nan | nan | nan |  |
| corridor_512 | 0.05 | one_shot_rd_t0p15 | 512 | 2 | 256 | 0.005539 | nan | nan | nan | 2790 | nan | nan | nan | nan |  |
| corridor_512 | 0.1 | one_shot_rd_t0p15 | 512 | 2 | 256 | 0.005369 | nan | nan | nan | 3071 | nan | nan | nan | nan |  |
| corridor_1024 | 0.0 | one_shot_rd_t0p15 | 1024 | 2 | 512 | 0.009379 | nan | nan | nan | 3179 | nan | nan | nan | nan |  |
| corridor_1024 | 0.05 | one_shot_rd_t0p15 | 1024 | 2 | 512 | 0.01141 | nan | nan | nan | 2600 | nan | nan | nan | nan |  |
| corridor_1024 | 0.1 | one_shot_rd_t0p15 | 1024 | 2 | 512 | 0.01106 | nan | nan | nan | 2731 | nan | nan | nan | nan |  |
| open_room_24 | 0.0 | one_shot_rd_t0p15 | 576 | 3 | 192 | 0.05845 | nan | nan | nan | 49.16 | nan | nan | nan | nan |  |
| open_room_24 | 0.05 | one_shot_rd_t0p15 | 576 | 3 | 192 | 0.06368 | nan | nan | nan | 56.31 | nan | nan | nan | nan |  |
| open_room_24 | 0.1 | one_shot_rd_t0p15 | 576 | 3 | 192 | 0.06453 | nan | nan | nan | 66.87 | nan | nan | nan | nan |  |
| open_room_32 | 0.0 | one_shot_rd_t0p15 | 1024 | 3 | 341.3 | 0.0989 | nan | nan | nan | 81.16 | nan | nan | nan | nan |  |
| open_room_32 | 0.05 | one_shot_rd_t0p15 | 1024 | 3 | 341.3 | 0.1105 | nan | nan | nan | 96.23 | nan | nan | nan | nan |  |
| open_room_32 | 0.1 | one_shot_rd_t0p15 | 1024 | 3 | 341.3 | 0.11 | nan | nan | nan | 108.3 | nan | nan | nan | nan |  |
| four_rooms_21 | 0.0 | one_shot_rd_t0p15 | 404 | 4 | 101 | 0.05778 | nan | nan | nan | 31.08 | nan | nan | nan | nan |  |
| four_rooms_21 | 0.05 | one_shot_rd_t0p15 | 404 | 4 | 101 | 0.0434 | nan | nan | nan | 57.85 | nan | nan | nan | nan |  |
| four_rooms_21 | 0.1 | one_shot_rd_t0p15 | 404 | 4 | 101 | 0.04342 | nan | nan | nan | 72.86 | nan | nan | nan | nan |  |
| four_rooms_31 | 0.0 | one_shot_rd_t0p15 | 904 | 4 | 226 | 0.08433 | nan | nan | nan | 91.12 | nan | nan | nan | nan |  |
| four_rooms_31 | 0.05 | one_shot_rd_t0p15 | 904 | 4 | 226 | 0.09531 | nan | nan | nan | 103.4 | nan | nan | nan | nan |  |
| four_rooms_31 | 0.1 | one_shot_rd_t0p15 | 904 | 4 | 226 | 0.09705 | nan | nan | nan | 109.1 | nan | nan | nan | nan |  |
| maze_21 | 0.0 | one_shot_rd_t0p15 | 199 | 20 | 9.95 | 0.02129 | nan | nan | nan | 1.563e+04 | nan | nan | nan | nan |  |
| maze_21 | 0.05 | one_shot_rd_t0p15 | 199 | 20 | 9.95 | 0.0233 | nan | nan | nan | 1.462e+04 | nan | nan | nan | nan |  |
| maze_21 | 0.1 | one_shot_rd_t0p15 | 199 | 20 | 9.95 | 0.02433 | nan | nan | nan | 1.423e+04 | nan | nan | nan | nan |  |
| maze_31 | 0.0 | one_shot_rd_t0p15 | 449 | 20 | 22.45 | 0.04701 | nan | nan | nan | 9.605e+04 | nan | nan | nan | nan |  |
| maze_31 | 0.05 | one_shot_rd_t0p15 | 449 | 20 | 22.45 | 0.05111 | nan | nan | nan | 7.154e+04 | nan | nan | nan | nan |  |
| maze_31 | 0.1 | one_shot_rd_t0p15 | 449 | 20 | 22.45 | 0.05174 | nan | nan | nan | 1.238e+05 | nan | nan | nan | nan |  |
