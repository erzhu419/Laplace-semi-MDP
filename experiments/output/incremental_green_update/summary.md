# Incremental Green Update Check

Generated: 2026-07-05T17:16:55
map_specs = ['open_room:7', 'four_rooms:7', 'maze:9']
slips = [0.0, 0.05]

This benchmark checks exact parent-to-child first-hit Green boundary insertion updates against direct child recomputation.

## Aggregate

| mode | n_rows | selected_state_match_rate | median_wall_time_sec | median_speedup_vs_full_recompute | max_speedup_vs_full_recompute | max_score_error_vs_exact | max_kernel_error_vs_exact | max_hidden_error_vs_exact | median_n_green_solves | median_n_green_updates | median_parent_update_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| boundary_insertion_score_update | 6 | 1 | 0.002205 | 6.114 | 7.377 | 5.313e-06 | nan | 8.881784197001252e-16 | 12 | 139 | 1 |
| boundary_insertion_update | 6 | 1 | 0.01595 | 0.7526 | 0.8342 | 5.313e-06 | 1.3322676295501878e-15 | 8.881784197001252e-16 | 12 | 139 | 1 |
| current_frozen_operator | 6 | 0.3333 | 0.005826 | 2.078 | 2.287 | 233.2 | nan | 1 | 12 | 0.0 | 0.0 |
| full_recompute | 6 | 1 | 0.01243 | 1 | 1 | 0.0 | 0.0 | 0.0 | 151 | 0.0 | 0.0 |
| static_basis_reuse | 6 | 1 | 0.005115 | 2.345 | 2.515 | 233.2 | nan | 1 | 12 | 0.0 | 0.0 |

## Rows

| map | slip | mode | n_states | n_candidates | selected_state | exact_selected_state | selected_state_match | max_score_error_vs_exact | max_kernel_error_vs_exact | max_hidden_error_vs_exact | wall_time_sec | speedup_vs_full_recompute | n_green_solves | n_green_updates | parent_update_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_7 | 0.0 | full_recompute | 49 | 12 | 7 | 7 | True | 0.0 | 0.0 | 0.0 | 0.01289 | 1 | 120 | 0 | 0.0 |
| open_room_7 | 0.0 | current_frozen_operator | 49 | 12 | 6 | 7 | False | 116.6 | nan | 1 | 0.005805 | 2.22 | 12 | 0 | 0.0 |
| open_room_7 | 0.0 | static_basis_reuse | 49 | 12 | 7 | 7 | True | 77.73 | nan | 1 | 0.005125 | 2.515 | 12 | 0 | 0.0 |
| open_room_7 | 0.0 | boundary_insertion_update | 49 | 12 | 7 | 7 | True | 0.0 | 0.0 | 0.0 | 0.01562 | 0.8252 | 12 | 108 | 1 |
| open_room_7 | 0.0 | boundary_insertion_score_update | 49 | 12 | 7 | 7 | True | 0.0 | nan | 0.0 | 0.002157 | 5.975 | 12 | 108 | 1 |
| open_room_7 | 0.05 | full_recompute | 49 | 12 | 7 | 7 | True | 0.0 | 0.0 | 0.0 | 0.01197 | 1 | 114 | 0 | 0.0 |
| open_room_7 | 0.05 | current_frozen_operator | 49 | 12 | 43 | 7 | False | 120.1 | nan | 0.9833 | 0.005847 | 2.047 | 12 | 0 | 0.0 |
| open_room_7 | 0.05 | static_basis_reuse | 49 | 12 | 7 | 7 | True | 62.16 | nan | 0.9998 | 0.005105 | 2.344 | 12 | 0 | 0.0 |
| open_room_7 | 0.05 | boundary_insertion_update | 49 | 12 | 7 | 7 | True | 7.898e-07 | 1.3322676295501878e-15 | 6.661338147750939e-16 | 0.01628 | 0.735 | 12 | 102 | 1 |
| open_room_7 | 0.05 | boundary_insertion_score_update | 49 | 12 | 7 | 7 | True | 7.898e-07 | nan | 6.661338147750939e-16 | 0.002253 | 5.312 | 12 | 102 | 1 |
| four_rooms_7 | 0.0 | full_recompute | 40 | 24 | 6 | 6 | True | 0.0 | 0.0 | 0.0 | 0.01974 | 1 | 218 | 0 | 0.0 |
| four_rooms_7 | 0.0 | current_frozen_operator | 40 | 24 | 6 | 6 | True | 116.6 | nan | 1 | 0.009417 | 2.096 | 12 | 0 | 0.0 |
| four_rooms_7 | 0.0 | static_basis_reuse | 40 | 24 | 6 | 6 | True | 116.6 | nan | 1 | 0.008749 | 2.256 | 12 | 0 | 0.0 |
| four_rooms_7 | 0.0 | boundary_insertion_update | 40 | 24 | 6 | 6 | True | 0.0 | 0.0 | 0.0 | 0.02666 | 0.7405 | 12 | 206 | 1 |
| four_rooms_7 | 0.0 | boundary_insertion_score_update | 40 | 24 | 6 | 6 | True | 0.0 | nan | 0.0 | 0.002676 | 7.377 | 12 | 206 | 1 |
| four_rooms_7 | 0.05 | full_recompute | 40 | 24 | 6 | 6 | True | 0.0 | 0.0 | 0.0 | 0.01866 | 1 | 208 | 0 | 0.0 |
| four_rooms_7 | 0.05 | current_frozen_operator | 40 | 24 | 6 | 6 | True | 88.65 | nan | 0.9833 | 0.009397 | 1.986 | 12 | 0 | 0.0 |
| four_rooms_7 | 0.05 | static_basis_reuse | 40 | 24 | 6 | 6 | True | 88.58 | nan | 0.9822 | 0.008647 | 2.158 | 12 | 0 | 0.0 |
| four_rooms_7 | 0.05 | boundary_insertion_update | 40 | 24 | 6 | 6 | True | 1.91e-09 | 6.661338147750939e-16 | 5.551115123125783e-16 | 0.0276 | 0.6761 | 12 | 196 | 1 |
| four_rooms_7 | 0.05 | boundary_insertion_score_update | 40 | 24 | 6 | 6 | True | 1.91e-09 | nan | 5.551115123125783e-16 | 0.002781 | 6.709 | 12 | 196 | 1 |
| maze_9 | 0.0 | full_recompute | 31 | 15 | 1 | 1 | True | 0.0 | 0.0 | 0.0 | 0.01145 | 1 | 154 | 0 | 0.0 |
| maze_9 | 0.0 | current_frozen_operator | 31 | 15 | 21 | 1 | False | 194.3 | nan | 1 | 0.005006 | 2.287 | 12 | 0 | 0.0 |
| maze_9 | 0.0 | static_basis_reuse | 31 | 15 | 1 | 1 | True | 194.3 | nan | 1 | 0.004595 | 2.491 | 12 | 0 | 0.0 |
| maze_9 | 0.0 | boundary_insertion_update | 31 | 15 | 1 | 1 | True | 0.0 | 0.0 | 0.0 | 0.01372 | 0.8342 | 12 | 142 | 1 |
| maze_9 | 0.0 | boundary_insertion_score_update | 31 | 15 | 1 | 1 | True | 0.0 | nan | 0.0 | 0.001831 | 6.253 | 12 | 142 | 1 |
| maze_9 | 0.05 | full_recompute | 31 | 15 | 1 | 1 | True | 0.0 | 0.0 | 0.0 | 0.01128 | 1 | 148 | 0 | 0.0 |
| maze_9 | 0.05 | current_frozen_operator | 31 | 15 | 21 | 1 | False | 233.2 | nan | 1 | 0.005474 | 2.061 | 12 | 0 | 0.0 |
| maze_9 | 0.05 | static_basis_reuse | 31 | 15 | 1 | 1 | True | 233.2 | nan | 1 | 0.00481 | 2.345 | 12 | 0 | 0.0 |
| maze_9 | 0.05 | boundary_insertion_update | 31 | 15 | 1 | 1 | True | 5.313e-06 | 1.1102230246251565e-15 | 8.881784197001252e-16 | 0.01475 | 0.7646 | 12 | 136 | 1 |
| maze_9 | 0.05 | boundary_insertion_score_update | 31 | 15 | 1 | 1 | True | 5.313e-06 | nan | 8.881784197001252e-16 | 0.002039 | 5.533 | 12 | 136 | 1 |
