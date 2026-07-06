# Submission Main Table

Generated: 2026-07-07T07:13:51

This report is the paper-facing aggregation layer. It does not rerun heavy experiments; it reads the current public CSV artifacts and aligns the main runtime result, compact baselines, exhaustive-oracle solver validity, and certificate appendices.

- best certified adaptive total speedup with unique-top fallback: `10.49x`
- best certified adaptive total speedup with tie-aware certificate: `10.49x`
- best multi-task amortized speedup in the current table: `108.4x`
- best fixed-B edge reward relabeling speedup: `108.4x`
- worst certified adaptive start-value gap in that table: `0.1962`
- adaptive final certified decisions under unique-top fallback: `20/20`
- adaptive final certified decisions under tie-aware reporting: `20/20`
- larger group-constrained adaptive feasible rows: `6/6`
- exact Green is the reference operator; certified adaptive Green plus tie-aware top-set/epsilon certificates are the runtime implementation; fixed-K and weighted spectral certificates are ablations/appendix diagnostics.

## Main Runtime Table

| map | slip | boundary_selector | method | n_states | n_boundary | state_compression_ratio | first_hit_used_steps_max | tail_bound_max | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | total_time_unique_top_fallback_sec | total_time_with_tie_certificate_sec | planning_speedup | total_speedup_unique_top_fallback | total_speedup_tie_aware | unique_top_break_even_tasks | amortization_break_even_tasks | start_gap | tie_mode | epsilon_optimal_certified | tie_set_certified | tie_aware_fallback_used | curvature_fallback_used | interval_certified | fallback_used | ambiguous_set_size | tie_aware_final_certified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_256 | 0.0 | endpoints | certified_adaptive_green_rd | 256 | 2.0 | 128 | 254.0 | 0.0 | 1.271 | 0.2432 | 0.0001686 | 0.2434 | 0.2434 | 7536 | 5.22 | 5.22 | 1 | 1 | 0.0 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 51.0 | 8.603e-07 | 5.754 | 8.459 | 0.206 | 8.665 | 8.665 | 27.94 | 0.6641 | 0.6641 | 2 | 2 | 1.155e-06 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 45.0 | 0.0 | 0.5664 | 8.045 | 0.1944 | 8.239 | 8.239 | 2.913 | 0.06875 | 0.06875 | 22 | 22 | 0.0 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 104.0 | 6.65e-07 | 2.474 | 13.6 | 0.0002484 | 13.6 | 13.6 | 9959 | 0.1819 | 0.1819 | 6 | 6 | 0.1408 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | turn_articulation | certified_adaptive_green_rd | 904 | 16.0 | 56.5 | 82.0 | 9.517e-07 | 1.853 | 8.667 | 0.01881 | 8.685 | 8.685 | 98.49 | 0.2133 | 0.2133 | 5 | 5 | 0.09094 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | endpoints | certified_adaptive_green_rd | 449 | 2.0 | 224.5 | 151.0 | 0.0 | 1.456 | 1.823 | 0.0001808 | 1.823 | 1.823 | 8053 | 0.7988 | 0.7988 | 2 | 2 | 2.131628207280301e-14 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | turn_articulation | certified_adaptive_green_rd | 256 | 2.0 | 128 | 254.0 | 0.0 | 1.257 | 0.2677 | 0.0001731 | 0.2679 | 0.2679 | 7261 | 4.692 | 4.692 | 1 | 1 | 0.0 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | endpoints | certified_adaptive_green_rd | 512 | 2.0 | 256 | 654.0 | 8.055e-07 | 6.285 | 0.599 | 0.0001758 | 0.5992 | 0.5992 | 3.574e+04 | 10.49 | 10.49 | 1 | 1 | 3.5352343275008025e-10 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 30.0 | 0.0 | 0.5564 | 5.97 | 0.06181 | 6.032 | 6.032 | 9.002 | 0.09224 | 0.09224 | 13 | 13 | 3.552713678800501e-15 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 104.0 | 9.982e-07 | 2.487 | 43.24 | 0.8317 | 44.07 | 44.07 | 2.99 | 0.05642 | 0.05642 | 27 | 27 | 0.1408 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 904 | 2.0 | 452 | 87.0 | 8.822e-07 | 1.787 | 11.32 | 0.0001809 | 11.32 | 11.32 | 9875 | 0.1579 | 0.1579 | 7 | 7 | 0.09094 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | turn_articulation | certified_adaptive_green_rd | 449 | 128.0 | 3.508 | 11.0 | 0.0 | 1.407 | 71.05 | 18.22 | 89.27 | 89.27 | 0.07722 | 0.01576 | 0.01576 |  |  | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 256 | 2.0 | 128 | 254.0 | 0.0 | 1.228 | 3.673 | 0.0001676 | 3.674 | 3.674 | 7330 | 0.3344 | 0.3344 | 3 | 3 | 0.0 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | turn_articulation | certified_adaptive_green_rd | 512 | 2.0 | 256 | 654.0 | 8.055e-07 | 6.101 | 0.6211 | 0.0002011 | 0.6213 | 0.6213 | 3.033e+04 | 9.82 | 9.82 | 1 | 1 | 3.5352343275008025e-10 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | endpoints | certified_adaptive_green_rd | 576 | 2.0 | 288 | 70.0 | 4.601e-07 | 0.9371 | 0.5285 | 0.0001691 | 0.5287 | 0.5287 | 5541 | 1.773 | 1.773 | 1 | 1 | 0.08633 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 95.0 | 9.997e-07 | 2.416 | 36.9 | 0.1361 | 37.04 | 37.04 | 17.76 | 0.06523 | 0.06523 | 17 | 17 | 0.1408 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 42.0 | 9.892e-07 | 1.823 | 111.2 | 0.6259 | 111.8 | 111.8 | 2.912 | 0.0163 | 0.0163 | 93 | 93 | 0.09094 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 449 | 20.0 | 22.45 | 95.0 | 0.0 | 1.393 | 4605 | 0.3585 | 4606 | 4606 | 3.886 | 0.0003025 | 0.0003025 | 4452 | 4452 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 120.0 | 0.0 | 1.229 | 1.342 | 0.3975 | 1.74 | 1.74 | 3.091 | 0.7063 | 0.7063 | 2 | 2 | 2.131628207280301e-14 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 512 | 2.0 | 256 | 654.0 | 8.055e-07 | 6.086 | 17.12 | 0.0001973 | 17.12 | 17.12 | 3.084e+04 | 0.3556 | 0.3556 | 3 | 3 | 3.5352343275008025e-10 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | turn_articulation | certified_adaptive_green_rd | 576 | 4.0 | 144 | 68.0 | 6.483e-07 | 0.914 | 0.6825 | 0.0007953 | 0.6833 | 0.6833 | 1149 | 1.338 | 1.338 | 1 | 1 | 0.08633 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | endpoints | certified_adaptive_green_rd | 404 | 2.0 | 202 | 39.0 | 0.0 | 0.332 | 0.3235 | 0.0001979 | 0.3237 | 0.3237 | 1678 | 1.026 | 1.026 | 1 | 1 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 46.0 | 9.97e-07 | 1.763 | 25.34 | 0.1162 | 25.45 | 25.45 | 15.17 | 0.06925 | 0.06925 | 16 | 16 | 0.09094 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 117.0 | 0.0 | 1.39 | 115 | 0.08606 | 115 | 115 | 16.15 | 0.01208 | 0.01208 | 89 | 89 | 2.131628207280301e-14 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 30.0 | 0.0 | 1.15 | 1.145 | 0.0457 | 1.191 | 1.191 | 25.16 | 0.9655 | 0.9655 | 2 | 2 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 331.0 | 9.816e-07 | 5.77 | 8.241 | 1.712 | 9.953 | 9.953 | 3.371 | 0.5797 | 0.5797 | 3 | 3 | 1.605e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 576 | 2.0 | 288 | 70.0 | 4.601e-07 | 0.8478 | 4.068 | 0.000164 | 4.068 | 4.068 | 5169 | 0.2084 | 0.2084 | 5 | 5 | 0.08633 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | turn_articulation | certified_adaptive_green_rd | 404 | 16.0 | 25.25 | 21.0 | 0.0 | 0.3168 | 1.461 | 0.01783 | 1.479 | 1.479 | 17.77 | 0.2142 | 0.2142 | 5 | 5 | 0.0 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | endpoints | certified_adaptive_green_rd | 904 | 2.0 | 452 | 104.0 | 6.176e-07 | 1.977 | 1.642 | 0.0001928 | 1.642 | 1.642 | 1.025e+04 | 1.204 | 1.204 | 1 | 1 | 0.1752 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 85.0 | 0.0 | 1.334 | 256 | 0.04674 | 256.1 | 256.1 | 28.55 | 0.005211 | 0.005211 | 199 | 199 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | endpoints | certified_adaptive_green_rd | 256 | 2.0 | 128 | 305.0 | 7.438e-07 | 1.387 | 0.2354 | 0.0001423 | 0.2355 | 0.2355 | 9744 | 5.889 | 5.889 | 1 | 1 | 6.662048690486698e-11 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 61.0 | 8.117e-07 | 5.857 | 8.785 | 0.2017 | 8.986 | 8.986 | 29.04 | 0.6517 | 0.6517 | 2 | 2 | 1.251e-06 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 70.0 | 9.894e-07 | 0.8533 | 9.837 | 0.2994 | 10.14 | 10.14 | 2.85 | 0.08418 | 0.08418 | 18 | 18 | 0.08633 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 404 | 2.0 | 202 | 39.0 | 0.0 | 0.3084 | 2.09 | 0.0001509 | 2.09 | 2.09 | 2044 | 0.1475 | 0.1475 | 7 | 7 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | turn_articulation | certified_adaptive_green_rd | 904 | 16.0 | 56.5 | 98.0 | 9.938e-07 | 1.949 | 8.054 | 0.01744 | 8.072 | 8.072 | 111.8 | 0.2414 | 0.2414 | 5 | 5 | 0.1749 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | endpoints | certified_adaptive_green_rd | 449 | 2.0 | 224.5 | 189.0 | 7.004e-07 | 1.667 | 2.083 | 0.0001791 | 2.083 | 2.083 | 9304 | 0.8001 | 0.8001 | 2 | 2 | 4.095e-09 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | turn_articulation | certified_adaptive_green_rd | 256 | 2.0 | 128 | 305.0 | 7.438e-07 | 1.542 | 0.2869 | 0.0002314 | 0.2871 | 0.2871 | 6662 | 5.369 | 5.369 | 1 | 1 | 6.662048690486698e-11 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1022.0 | 0.0 | 10.74 | 2.367 | 0.0001493 | 2.367 | 2.367 | 7.194e+04 | 4.537 | 4.537 | 1 | 1 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 62.0 | 9.955e-07 | 0.9087 | 10.01 | 0.06878 | 10.08 | 10.08 | 13.21 | 0.09012 | 0.09012 | 12 | 12 | 0.08633 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 13.0 | 0.0 | 0.3491 | 12.2 | 0.1485 | 12.34 | 12.34 | 2.351 | 0.02828 | 0.02828 | 61 | 61 | 3.552713678800501e-15 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 904 | 2.0 | 452 | 104.0 | 6.176e-07 | 2.088 | 12.14 | 0.0001753 | 12.14 | 12.14 | 1.191e+04 | 0.172 | 0.172 | 6 | 6 | 0.1752 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | turn_articulation | certified_adaptive_green_rd | 449 | 128.0 | 3.508 | 27.0 | 9.741e-07 | 1.83 | 109.8 | 20.73 | 130.5 | 130.5 | 0.0883 | 0.01402 | 0.01402 |  |  | 5.497e-06 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 256 | 2.0 | 128 | 305.0 | 7.438e-07 | 1.544 | 4.538 | 0.0002243 | 4.538 | 4.538 | 6885 | 0.3403 | 0.3403 | 3 | 3 | 6.662048690486698e-11 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | turn_articulation | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1022.0 | 0.0 | 13.09 | 2.288 | 0.0001401 | 2.289 | 2.289 | 9.343e+04 | 5.719 | 5.719 | 1 | 1 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | endpoints | certified_adaptive_green_rd | 576 | 2.0 | 288 | 83.0 | 7.417e-07 | 1.124 | 0.5355 | 0.0001726 | 0.5357 | 0.5357 | 6516 | 2.099 | 2.099 | 1 | 1 | 0.1762 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 25.0 | 0.0 | 0.3471 | 5.518 | 0.03836 | 5.556 | 5.556 | 9.048 | 0.06248 | 0.06248 | 18 | 18 | 0.0 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 53.0 | 9.997e-07 | 2.18 | 124.1 | 0.6787 | 124.8 | 124.8 | 3.213 | 0.01748 | 0.01748 | 83 | 83 | 0.1752 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 449 | 20.0 | 22.45 | 125.0 | 7.976e-07 | 1.984 | 3809 | 0.4739 | 3810 | 3810 | 4.188 | 0.0005209 | 0.0005209 | 2522 | 2522 | 3.711e-06 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 153.0 | 8.159e-07 | 1.526 | 1.637 | 0.4475 | 2.085 | 2.085 | 3.409 | 0.7318 | 0.7318 | 2 | 2 | 2.668e-07 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1022.0 | 0.0 | 13.19 | 32.1 | 0.0001397 | 32.1 | 32.1 | 9.442e+04 | 0.411 | 0.411 | 3 | 3 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | turn_articulation | certified_adaptive_green_rd | 576 | 4.0 | 144 | 81.0 | 7.442e-07 | 1.11 | 0.6795 | 0.0008027 | 0.6803 | 0.6803 | 1383 | 1.632 | 1.632 | 1 | 1 | 0.1762 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | endpoints | certified_adaptive_green_rd | 404 | 2.0 | 202 | 64.0 | 5.183e-07 | 0.5966 | 0.3504 | 0.0001538 | 0.3506 | 0.3506 | 3879 | 1.702 | 1.702 | 1 | 1 | 0.09804 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 56.0 | 9.992e-07 | 2.148 | 24.25 | 0.1257 | 24.38 | 24.38 | 17.09 | 0.08813 | 0.08813 | 12 | 12 | 0.1748 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 150.0 | 9.012e-07 | 1.859 | 154.7 | 0.1896 | 154.9 | 154.9 | 9.802 | 0.012 | 0.012 | 93 | 93 | 1.539e-07 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 50.0 | 8.603e-07 | 1.535 | 1.746 | 0.04821 | 1.794 | 1.794 | 31.84 | 0.8556 | 0.8556 | 2 | 2 | 1.15e-06 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 496.0 | 0.0 | 15.66 | 36.88 | 6.491 | 43.37 | 43.37 | 2.412 | 0.361 | 0.361 | 5 | 5 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 576 | 2.0 | 288 | 83.0 | 7.417e-07 | 1.113 | 4.861 | 0.0002084 | 4.861 | 4.861 | 5341 | 0.2289 | 0.2289 | 5 | 5 | 0.1762 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | turn_articulation | certified_adaptive_green_rd | 404 | 16.0 | 25.25 | 58.0 | 9.795e-07 | 0.5992 | 2.42 | 0.02135 | 2.441 | 2.441 | 28.06 | 0.2454 | 0.2454 | 5 | 5 | 0.09804 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | endpoints | certified_adaptive_green_rd | 199 | 2.0 | 99.5 | 75.0 | 0.0 | 0.3191 | 0.2875 | 0.0001819 | 0.2877 | 0.2877 | 1754 | 1.109 | 1.109 | 1 | 1 | 1.7763568394002505e-14 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 114.0 | 9.937e-07 | 1.896 | 378.2 | 0.0462 | 378.3 | 378.3 | 41.04 | 0.005012 | 0.005012 | 205 | 205 | 7.615e-07 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | endpoints | certified_adaptive_green_rd | 256 | 2.0 | 128 | 342.0 | 7.245e-07 | 1.695 | 0.2386 | 0.0001884 | 0.2388 | 0.2388 | 8995 | 7.098 | 7.098 | 1 | 1 | 8.284217756227008e-11 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 62.0 | 0.0 | 15.87 | 30.79 | 0.3359 | 31.13 | 31.13 | 47.24 | 0.5097 | 0.5097 | 2 | 2 | 3.211e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 83.0 | 9.791e-07 | 1.085 | 10.66 | 0.3795 | 11.04 | 11.04 | 2.86 | 0.09827 | 0.09827 | 16 | 16 | 0.1762 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 404 | 2.0 | 202 | 64.0 | 5.183e-07 | 0.5982 | 2.849 | 0.0001618 | 2.85 | 2.85 | 3696 | 0.2099 | 0.2099 | 5 | 5 | 0.09804 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | turn_articulation | certified_adaptive_green_rd | 199 | 52.0 | 3.827 | 13.0 | 0.0 | 0.3162 | 4.033 | 1.144 | 5.178 | 5.178 | 0.2763 | 0.06107 | 0.06107 |  |  | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | endpoints | certified_adaptive_green_rd | 449 | 2.0 | 224.5 | 214.0 | 9.201e-07 | 2.006 | 2.468 | 0.0002325 | 2.468 | 2.468 | 8625 | 0.8128 | 0.8128 | 2 | 2 | 3.121e-09 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | turn_articulation | certified_adaptive_green_rd | 256 | 2.0 | 128 | 342.0 | 7.245e-07 | 1.539 | 0.2669 | 0.0001426 | 0.2671 | 0.2671 | 1.079e+04 | 5.761 | 5.761 | 1 | 1 | 8.284217756227008e-11 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.43 | 2.34 | 0.0001335 | 2.34 | 2.34 | 1.006e+05 | 5.74 | 5.74 | 1 | 1 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 76.0 | 9.982e-07 | 0.9996 | 10.01 | 0.06658 | 10.08 | 10.08 | 15.01 | 0.09921 | 0.09921 | 11 | 11 | 0.1762 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 31.0 | 9.862e-07 | 0.5441 | 18.58 | 0.2116 | 18.8 | 18.8 | 2.571 | 0.02895 | 0.02895 | 56 | 56 | 0.09804 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 199 | 20.0 | 9.95 | 13.0 | 0.0 | 0.284 | 338.5 | 0.1489 | 338.7 | 338.7 | 1.907 | 0.0008386 | 0.0008386 | 2506 | 2506 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | turn_articulation | certified_adaptive_green_rd | 449 | 128.0 | 3.508 | 34.0 | 9.94e-07 | 1.918 | 110.4 | 20.16 | 130.6 | 130.6 | 0.09515 | 0.01469 | 0.01469 |  |  | 5.015e-06 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 256 | 2.0 | 128 | 342.0 | 7.245e-07 | 1.664 | 4.887 | 0.0002245 | 4.887 | 4.887 | 7410 | 0.3404 | 0.3404 | 3 | 3 | 8.284217756227008e-11 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | turn_articulation | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.09 | 2.301 | 0.0001715 | 2.301 | 2.301 | 7.632e+04 | 5.687 | 5.687 | 1 | 1 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 61.0 | 0.0 | 1.354 | 1.692 | 0.0002118 | 1.693 | 1.693 | 6392 | 0.7998 | 0.7998 | 2 | 2 | 1.7763568394002505e-14 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 58.0 | 9.941e-07 | 0.5961 | 10.12 | 0.04387 | 10.17 | 10.17 | 13.59 | 0.05863 | 0.05863 | 19 | 19 | 0.09804 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 60.0 | 0.0 | 0.3192 | 5.664 | 0.04411 | 5.708 | 5.708 | 7.237 | 0.05592 | 0.05592 | 21 | 21 | 2.131628207280301e-14 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 449 | 20.0 | 22.45 | 143.0 | 8.941e-07 | 2.002 | 6587 | 0.411 | 6587 | 6587 | 4.871 | 0.0003039 | 0.0003039 | 4141 | 4141 | 3.334e-06 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 175.0 | 9.578e-07 | 1.676 | 1.783 | 0.4797 | 2.263 | 2.263 | 3.494 | 0.7407 | 0.7407 | 2 | 2 | 1.306e-07 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.5 | 31.98 | 0.0001541 | 31.98 | 31.98 | 8.76e+04 | 0.4222 | 0.4222 | 3 | 3 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | turn_articulation | certified_adaptive_green_rd | 1024 | 4.0 | 256 | 30.0 | 0.0 | 1.397 | 1.85 | 0.0006389 | 1.851 | 1.851 | 2187 | 0.7551 | 0.7551 | 2 | 2 | 1.7763568394002505e-14 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | endpoints | certified_adaptive_green_rd | 404 | 2.0 | 202 | 77.0 | 8.318e-07 | 0.7101 | 0.3879 | 0.0001719 | 0.3881 | 0.3881 | 4132 | 1.83 | 1.83 | 1 | 1 | 0.1962 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 29.0 | 0.0 | 0.3116 | 10.04 | 0.02698 | 10.07 | 10.07 | 11.55 | 0.03096 | 0.03096 | 36 | 36 | 1.0658141036401504e-14 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 171.0 | 9.297e-07 | 2.079 | 176.8 | 0.2389 | 177.1 | 177.1 | 8.7 | 0.01174 | 0.01174 | 97 | 97 | 1.027e-07 |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 60.0 | 9.079e-07 | 1.666 | 1.854 | 0.0489 | 1.903 | 1.903 | 34.07 | 0.8754 | 0.8754 | 2 | 2 | 1.249e-06 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 575.0 | 6.776e-07 | 15.37 | 35.64 | 8.71 | 44.35 | 44.35 | 1.764 | 0.3464 | 0.3464 | 6 | 6 | 3.227e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 61.0 | 0.0 | 1.363 | 9.54 | 0.0001615 | 9.54 | 9.54 | 8440 | 0.1429 | 0.1429 | 8 | 8 | 1.7763568394002505e-14 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | turn_articulation | certified_adaptive_green_rd | 404 | 16.0 | 25.25 | 71.0 | 9.793e-07 | 0.7046 | 2.415 | 0.02084 | 2.436 | 2.436 | 33.82 | 0.2892 | 0.2892 | 4 | 4 | 0.1962 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | endpoints | certified_adaptive_green_rd | 199 | 2.0 | 99.5 | 102.0 | 6.311e-07 | 0.4433 | 0.3234 | 0.0001486 | 0.3236 | 0.3236 | 2983 | 1.37 | 1.37 | 1 | 1 | 2.974e-08 |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 131.0 | 9.941e-07 | 2.077 | 407 | 0.04715 | 407.1 | 407.1 | 44.06 | 0.005102 | 0.005102 | 201 | 201 | 1.235e-06 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | endpoints | certified_adaptive_green_rd | 512 | 2.0 | 256 | 510.0 | 0.0 | 5.118 | 0.7676 | 0.0001926 | 0.7678 | 0.7678 | 2.657e+04 | 6.666 | 6.666 | 1 | 1 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 87.0 | 6.58e-07 | 15.8 | 41.66 | 0.4234 | 42.09 | 42.09 | 37.32 | 0.3754 | 0.3754 | 3 | 3 | 7.082e-07 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 61.0 | 0.0 | 1.404 | 42.73 | 0.4934 | 43.22 | 43.22 | 2.845 | 0.03248 | 0.03248 | 47 | 47 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 404 | 2.0 | 202 | 77.0 | 8.318e-07 | 0.7538 | 3.587 | 0.0002333 | 3.588 | 3.588 | 3231 | 0.2101 | 0.2101 | 5 | 5 | 0.1962 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | turn_articulation | certified_adaptive_green_rd | 199 | 52.0 | 3.827 | 29.0 | 9.741e-07 | 0.4758 | 8.102 | 1.448 | 9.55 | 9.55 | 0.3286 | 0.04982 | 0.04982 |  |  | 3.039e-06 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | turn_articulation | certified_adaptive_green_rd | 512 | 2.0 | 256 | 510.0 | 0.0 | 4.759 | 0.6325 | 0.0001662 | 0.6327 | 0.6327 | 2.864e+04 | 7.522 | 7.522 | 1 | 1 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 12.89 | 2.286 | 0.000146 | 2.286 | 2.286 | 8.83e+04 | 5.639 | 5.639 | 1 | 1 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 46.0 | 0.0 | 1.298 | 24.14 | 0.1254 | 24.27 | 24.27 | 10.35 | 0.05348 | 0.05348 | 21 | 21 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 41.0 | 9.895e-07 | 0.6599 | 21.08 | 0.2384 | 21.32 | 21.32 | 2.768 | 0.03095 | 0.03095 | 51 | 51 | 0.1962 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 199 | 20.0 | 9.95 | 29.0 | 9.741e-07 | 0.4189 | 351 | 0.1853 | 351.1 | 351.1 | 2.261 | 0.001193 | 0.001193 | 1503 | 1503 | 2.965e-06 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 512 | 2.0 | 256 | 510.0 | 0.0 | 5.129 | 14.66 | 0.0001711 | 14.66 | 14.66 | 2.998e+04 | 0.3499 | 0.3499 | 3 | 3 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | turn_articulation | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.04 | 2.326 | 0.000147 | 2.326 | 2.326 | 8.871e+04 | 5.608 | 5.608 | 1 | 1 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 88.0 | 8.332e-07 | 2.09 | 1.599 | 0.0001676 | 1.599 | 1.599 | 1.247e+04 | 1.307 | 1.307 | 1 | 1 | 0.07115 |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 70.0 | 9.936e-07 | 0.7007 | 10.09 | 0.04124 | 10.14 | 10.14 | 16.99 | 0.06913 | 0.06913 | 16 | 16 | 0.1962 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 85.0 | 7.011e-07 | 0.4365 | 6.974 | 0.08669 | 7.061 | 7.061 | 5.036 | 0.06183 | 0.06183 | 20 | 20 | 2.62e-07 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 245.0 | 0.0 | 5.075 | 7.769 | 1.728 | 9.497 | 9.497 | 2.937 | 0.5344 | 0.5344 | 3 | 3 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.07 | 32.51 | 0.0001316 | 32.51 | 32.51 | 9.931e+04 | 0.4019 | 0.4019 | 3 | 3 | 3.228e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | turn_articulation | certified_adaptive_green_rd | 1024 | 4.0 | 256 | 86.0 | 9.793e-07 | 2.12 | 2.195 | 0.0009235 | 2.196 | 2.196 | 2295 | 0.9654 | 0.9654 | 2 | 2 | 0.07115 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | endpoints | certified_adaptive_green_rd | 904 | 2.0 | 452 | 59.0 | 0.0 | 1.18 | 1.513 | 0.0002462 | 1.514 | 1.514 | 4792 | 0.7795 | 0.7795 | 2 | 2 | 1.7763568394002505e-14 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 49.0 | 9.494e-07 | 0.4443 | 15.27 | 0.02317 | 15.29 | 15.29 | 19.18 | 0.02906 | 0.02906 | 37 | 37 | 1.032e-06 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 31.0 | 0.0 | 5.126 | 6.597 | 0.2172 | 6.815 | 6.815 | 23.6 | 0.7523 | 0.7523 | 2 | 2 | 1.4210854715202004e-14 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 637.0 | 8.22e-07 | 15.71 | 46.89 | 9.382 | 56.28 | 56.28 | 1.674 | 0.2791 | 0.2791 | 8 | 8 | 3.229e-09 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 88.0 | 8.332e-07 | 2.152 | 12.32 | 0.0002155 | 12.32 | 12.32 | 9988 | 0.1746 | 0.1746 | 6 | 6 | 0.07115 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | turn_articulation | certified_adaptive_green_rd | 904 | 16.0 | 56.5 | 31.0 | 0.0 | 1.177 | 6.32 | 0.02007 | 6.34 | 6.34 | 58.63 | 0.1856 | 0.1856 | 6 | 6 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | endpoints | certified_adaptive_green_rd | 199 | 2.0 | 99.5 | 117.0 | 9.364e-07 | 0.5337 | 0.3673 | 0.0001621 | 0.3674 | 0.3674 | 3292 | 1.452 | 1.452 | 1 | 1 | 5.012e-08 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | endpoints | certified_adaptive_green_rd | 512 | 2.0 | 256 | 590.0 | 8.619e-07 | 5.733 | 0.6556 | 0.0001806 | 0.6558 | 0.6558 | 3.175e+04 | 8.741 | 8.741 | 1 | 1 | 2.169358026549162e-10 |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 101.0 | 6.132e-07 | 15.78 | 38.36 | 0.3103 | 38.67 | 38.67 | 50.85 | 0.408 | 0.408 | 3 | 3 | 6.403e-07 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 88.0 | 9.929e-07 | 2.112 | 38.83 | 0.716 | 39.55 | 39.55 | 2.95 | 0.05342 | 0.05342 | 28 | 28 | 0.07115 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 904 | 2.0 | 452 | 59.0 | 0.0 | 1.2 | 9.089 | 0.0002172 | 9.089 | 9.089 | 5526 | 0.132 | 0.132 | 8 | 8 | 1.7763568394002505e-14 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | turn_articulation | certified_adaptive_green_rd | 199 | 52.0 | 3.827 | 36.0 | 8.822e-07 | 0.5439 | 7.273 | 1.35 | 8.623 | 8.623 | 0.4028 | 0.06307 | 0.06307 |  |  | 2.828e-06 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | turn_articulation | certified_adaptive_green_rd | 512 | 2.0 | 256 | 590.0 | 8.619e-07 | 5.787 | 0.7832 | 0.0001917 | 0.7834 | 0.7834 | 3.018e+04 | 7.387 | 7.387 | 1 | 1 | 2.169358026549162e-10 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | endpoints | certified_adaptive_green_rd | 576 | 2.0 | 288 | 45.0 | 0.0 | 0.6086 | 0.5435 | 0.0002096 | 0.5438 | 0.5438 | 2904 | 1.119 | 1.119 | 1 | 1 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 80.0 | 9.993e-07 | 2.164 | 42.91 | 0.1548 | 43.07 | 43.07 | 13.98 | 0.05025 | 0.05025 | 22 | 22 | 0.07115 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 20.0 | 0.0 | 1.217 | 90.4 | 0.5093 | 90.9 | 90.9 | 2.39 | 0.01339 | 0.01339 | 128 | 128 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 199 | 20.0 | 9.95 | 36.0 | 8.778e-07 | 0.529 | 360.1 | 0.1984 | 360.3 | 360.3 | 2.666 | 0.001468 | 0.001468 | 1090 | 1090 | 2.667e-06 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 512 | 2.0 | 256 | 590.0 | 8.619e-07 | 5.674 | 16.04 | 0.000174 | 16.04 | 16.04 | 3.261e+04 | 0.3538 | 0.3538 | 3 | 3 | 2.169358026549162e-10 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | turn_articulation | certified_adaptive_green_rd | 576 | 4.0 | 144 | 22.0 | 0.0 | 0.5541 | 0.617 | 0.000657 | 0.6177 | 0.6177 | 843.3 | 0.8971 | 0.8971 | 2 | 2 | 0.0 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 104.0 | 6.65e-07 | 2.396 | 1.672 | 0.0001915 | 1.672 | 1.672 | 1.251e+04 | 1.433 | 1.433 | 1 | 1 | 0.1408 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 21.0 | 0.0 | 1.168 | 18.43 | 0.1472 | 18.58 | 18.58 | 7.939 | 0.06288 | 0.06288 | 19 | 19 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 98.0 | 8.549e-07 | 0.5205 | 8.062 | 0.1019 | 8.164 | 8.164 | 5.107 | 0.06375 | 0.06375 | 20 | 20 | 4.736e-07 |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 295.0 | 6.938e-07 | 5.637 | 8.045 | 1.8 | 9.845 | 9.845 | 3.132 | 0.5726 | 0.5726 | 3 | 3 | 2.883e-09 |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 576 | 2.0 | 288 | 45.0 | 0.0 | 0.5626 | 3.381 | 0.0001666 | 3.382 | 3.382 | 3377 | 0.1664 | 0.1664 | 7 | 7 | 7.105427357601002e-15 |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | turn_articulation | certified_adaptive_green_rd | 1024 | 4.0 | 256 | 102.0 | 8.868e-07 | 2.297 | 1.972 | 0.0007778 | 1.973 | 1.973 | 2953 | 1.164 | 1.164 | 1 | 1 | 0.1408 |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | endpoints | certified_adaptive_green_rd | 904 | 2.0 | 452 | 87.0 | 8.822e-07 | 1.667 | 1.416 | 0.0001746 | 1.416 | 1.416 | 9548 | 1.177 | 1.177 | 1 | 1 | 0.09094 |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 58.0 | 9.903e-07 | 0.4793 | 15.61 | 0.01994 | 15.63 | 15.63 | 24.03 | 0.03067 | 0.03067 | 34 | 34 | 1.228e-06 |  |  |  |  |  |  |  |  |  |

## Compact Baseline Aggregate

| method_spec | n_rows | median_state_compression | median_planning_speedup | median_total_speedup | max_start_gap | mean_success_rate | max_hidden_audit_distinct | group_feasible_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| betweenness_sqrt | 10 | 5.333 | 3.807 | 0.3402 | 0.04973 | 1 | 2 | nan |
| coverage_sqrt | 10 | 5.333 | 9.442 | 0.4021 | 0.04973 | 1 | 2 | nan |
| eigenoptions_sqrt | 10 | 5.333 | 3.165 | 0.3368 | 0.04973 | 1 | 3 | nan |
| full_vi | 10 | 1 | 1 | 1 | 0.0 | 1 | 0.0 | nan |
| graph_rd_joint | 10 | 12 | 91.62 | 0.07881 | 0.04973 | 1 | 2 | nan |
| graph_rd_surrogate_joint | 10 | 12 | 92.59 | 0.214 | 0.04973 | 1 | 2 | nan |
| group_constrained_rd | 10 | 10.5 | 25.09 | 0.01116 | 0.04973 | 1 | 3 | 0.9 |
| random_landmarks_sqrt | 10 | 5.333 | 4.893 | 0.3465 | 0.04973 | 1 | 3 | nan |

## Larger Group-Constrained Adaptive

| map | slip | method | n_states | n_basis | n_boundary | group_all_feasible | n_groups_feasible | group_total_violation | selection_time_sec | delta_backend | probe_green_kernel_time_sec | probe_operator_delta_time_sec | active_weight_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_tail_bound_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | False | 1 | 155.5 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02287 | 8.451e-05 | 636.4 | 2.343 | 1 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | True | 3 | 0.0 | 3.393 | operator | 1.287 | 0.9454 | 0.0 | 0.0008942 | 0.0 | 0.02966 | 0.001155 | 47.28 | 0.01595 | 65 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.0 | group_constrained_incremental | 144 | 24 | 3 | True | 3 | 0.0 | 1.493 | insertion_score | 0.03907 | 0.01097 | 0.04918 | 0.0008691 | 0.0 | 0.02899 | 0.0002627 | 233.3 | 0.04026 | 25 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | False | 0 | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02588 | 8.025e-05 | 1442 | 4.457 | 1 | 0.07851 | 3.737e-07 |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | True | 3 | 0.0 | 14.47 | operator | 5.257 | 4.158 | 0.0 | 0.002624 | 0.0 | 0.04639 | 0.002847 | 40.57 | 0.007959 | 129 | 0.07851 | 9.787e-07 |
| open_room_12 | 0.05 | group_constrained_incremental | 144 | 24 | 4 | True | 3 | 0.0 | 4.696 | insertion_score | 0.1122 | 0.03775 | 0.1023 | 0.001892 | 0.0 | 0.04455 | 0.002772 | 40.45 | 0.02364 | 44 | 0.07851 | 9.787e-07 |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | False | 1 | 155.5 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01908 | 8.066e-05 | 447.1 | 1.882 | 1 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | True | 3 | 0.0 | 2.043 | operator | 0.7261 | 0.5929 | 0.0 | 0.0009157 | 0.0 | 0.02844 | 0.000173 | 208.7 | 0.01743 | 58 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.0 | group_constrained_incremental | 104 | 29 | 3 | True | 3 | 0.0 | 0.9076 | insertion_score | 0.01755 | 0.01223 | 0.02391 | 0.000961 | 0.0 | 0.02837 | 0.000175 | 205 | 0.03831 | 27 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | False | 0 | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02535 | 8.645e-05 | 922 | 3.134 | 1 | 0.05768 | 7.41e-07 |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | True | 3 | 0.0 | 9.718 | operator | 3.442 | 2.849 | 0.0 | 0.002826 | 0.0 | 0.06866 | 0.0007576 | 104.2 | 0.008062 | 126 | 0.05768 | 9.381e-07 |
| four_rooms_11 | 0.05 | group_constrained_incremental | 104 | 29 | 5 | True | 3 | 0.0 | 4.821 | insertion_score | 0.1158 | 0.09825 | 0.09189 | 0.003391 | 0.0 | 0.1352 | 0.004883 | 18.07 | 0.01779 | 60 | 0.05768 | 9.265e-07 |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | False | 1 | 155.5 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01426 | 8.592e-05 | 398.1 | 2.384 | 1 | 7.105427357601002e-15 | 0.0 |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | True | 3 | 0.0 | 5.226 | operator | 2.064 | 1.429 | 0.0 | 0.003246 | 0.0 | 0.03877 | 0.001711 | 19.58 | 0.00636 | 166 | 3.552713678800501e-15 | 0.0 |
| maze_13 | 0.0 | group_constrained_incremental | 71 | 33 | 3 | True | 3 | 0.0 | 0.6764 | insertion_score | 0.009523 | 0.009816 | 0.03206 | 0.001024 | 0.0 | 0.02155 | 0.001261 | 26.89 | 0.04848 | 22 | 7.105427357601002e-15 | 0.0 |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | False | 0 | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0188 | 0.0001151 | 550 | 3.348 | 1 | 1.548e-08 | 4.298e-07 |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | True | 3 | 0.0 | 5.532 | operator | 1.962 | 1.623 | 0.0 | 0.002267 | 0.0 | 0.05175 | 0.002363 | 26.55 | 0.01123 | 93 | 4.297e-07 | 9.672e-07 |
| maze_13 | 0.05 | group_constrained_incremental | 71 | 33 | 3 | True | 3 | 0.0 | 1.054 | insertion_score | 0.009619 | 0.01091 | 0.01226 | 0.001102 | 0.0 | 0.03094 | 0.001674 | 37.97 | 0.05848 | 18 | 2.733e-07 | 7.73e-07 |

## Random Maze Generalization

| method | n_rows | feasible_rate | median_n_boundary | median_state_compression | median_selection_time_sec | median_total_speedup | max_start_gap | max_group_total_violation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | 180 | 0.0 | 2 | 48.5 | 0.0 | 2.383 | 5.848e-08 | 233.2 |
| group_constrained_incremental | 180 | 0.9611 | 3 | 32.33 | 3.865 | 0.05321 | 1.221e-06 | 174.9 |

## Fair Budget Frontier

| method_group | n_rows | pareto_rows | median_rate_budget_boundary_frac | median_state_compression_ratio | median_start_gap | median_hidden_audit | mean_group_feasible_rate | median_total_speedup | median_success_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline:dense_turn | 51 | 33 | 0.007812 | 128 | 2.170708057747106e-10 | 0.0 | 1 | 0.8971 | 1 |
| baseline:endpoints | 237 | 226 | 0.01575 | 63.5 | 2.557e-08 | 233.2 | 0.1143 | 2.324 | 1 |
| full_mdp | 10 | 5 | 1 | 1 | 0.0 | 0.0 | nan | 1 | 1 |
| option_baseline:bottleneck | 181 | 32 | 0.03429 | 29.16 | 1.355289214188815e-10 | 0.72 | 1 | 0.09827 | 1 |
| option_baseline:coverage | 181 | 17 | 0.03429 | 29.16 | 1.355289214188815e-10 | 0.0 | 1 | 0.09921 | 1 |
| option_baseline:eigen | 154 | 21 | 0.03125 | 32 | 7.285194669748307e-11 | 0.625 | 1 | 0.3368 | 1 |
| option_baseline:random | 154 | 16 | 0.03125 | 32 | 7.456613104750431e-11 | 0.72 | 1 | 0.3465 | 1 |
| ours:group_rd | 202 | 194 | 0.03093 | 32.33 | 2.371e-07 | 0.0 | 0.9604 | 0.05223 | 1 |
| ours:rd_graph | 71 | 57 | 0.007812 | 128 | 7.38040739634016e-11 | 0.7 | 1 | 0.1819 | 1 |

## Multi-Task And Edge Reward Compression

| source | method_or_variant | task_count | n_rows | median_amortized_speedup | best_amortized_speedup | median_planning_only_speedup | median_break_even_tasks | max_start_gap | median_state_compression | median_goal_interface | median_goal_policies |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| amortized_multitask | betweenness_sqrt | 1 | 8 | 0.004569 | 0.01453 | 0.05651 | nan | 0.0 | 4.107 |  |  |
| amortized_multitask | betweenness_sqrt | 10 | 8 | 0.02487 | 0.04607 | 0.06099 | nan | 0.0 | 4.107 |  |  |
| amortized_multitask | betweenness_sqrt | 100 | 8 | 0.04586 | 0.06165 | 0.0618 | nan | 0.0 | 4.107 |  |  |
| amortized_multitask | betweenness_sqrt | 25 | 8 | 0.03362 | 0.0545 | 0.06209 | nan | 0.0 | 4.107 |  |  |
| amortized_multitask | betweenness_sqrt | 5 | 8 | 0.01844 | 0.0368 | 0.06061 | nan | 0.0 | 4.107 |  |  |
| amortized_multitask | betweenness_sqrt | 50 | 8 | 0.03988 | 0.05769 | 0.0637 | nan | 0.0 | 4.107 |  |  |
| amortized_multitask | endpoints | 1 | 8 | 0.006091 | 0.01745 | 0.07745 | nan | 0.0 | 4.757 |  |  |
| amortized_multitask | endpoints | 10 | 8 | 0.03262 | 0.05419 | 0.08644 | nan | 0.0 | 4.757 |  |  |
| amortized_multitask | endpoints | 100 | 8 | 0.07647 | 0.08873 | 0.08712 | nan | 0.0 | 4.757 |  |  |
| amortized_multitask | endpoints | 25 | 8 | 0.04367 | 0.06798 | 0.08855 | nan | 0.0 | 4.757 |  |  |
| amortized_multitask | endpoints | 5 | 8 | 0.02507 | 0.04264 | 0.089 | nan | 0.0 | 4.757 |  |  |
| amortized_multitask | endpoints | 50 | 8 | 0.05675 | 0.075 | 0.08876 | nan | 0.0 | 4.757 |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 1 | 8 | 0.002292 | 0.01934 | 0.07254 | nan | 0.0 | 4.539 |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 10 | 8 | 0.01955 | 0.07091 | 0.08575 | nan | 0.0 | 4.539 |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 100 | 8 | 0.07412 | 0.09775 | 0.09113 | nan | 0.0 | 4.539 |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 25 | 8 | 0.03915 | 0.08417 | 0.08911 | nan | 0.0 | 4.539 |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 5 | 8 | 0.01075 | 0.0574 | 0.08141 | nan | 0.0 | 4.539 |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 50 | 8 | 0.05813 | 0.08834 | 0.09289 | nan | 0.0 | 4.539 |  |  |
| amortized_multitask | turn_articulation | 1 | 8 | 0.003293 | 0.0223 | 0.06958 | nan | 0.0 | 4.354 |  |  |
| amortized_multitask | turn_articulation | 10 | 8 | 0.02051 | 0.06919 | 0.08252 | nan | 0.0 | 4.354 |  |  |
| amortized_multitask | turn_articulation | 100 | 8 | 0.05555 | 0.08427 | 0.07977 | nan | 0.0 | 4.354 |  |  |
| amortized_multitask | turn_articulation | 25 | 8 | 0.03171 | 0.08073 | 0.08072 | nan | 0.0 | 4.354 |  |  |
| amortized_multitask | turn_articulation | 5 | 8 | 0.0142 | 0.05856 | 0.08259 | nan | 0.0 | 4.354 |  |  |
| amortized_multitask | turn_articulation | 50 | 8 | 0.04114 | 0.08447 | 0.08071 | nan | 0.0 | 4.354 |  |  |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 1 | 32 | 0.3835 | 1.486 | 286.1 | 3 | 13.38 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 10 | 32 | 4.218 | 13.45 | 348.7 | 2 | 30.88 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 100 | 32 | 35.39 | 108.4 | 305.2 | 3 | 30.88 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 25 | 32 | 9.849 | 33.77 | 315.7 | 3 | 30.88 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 5 | 32 | 1.914 | 6.684 | 292 | 2.5 | 30.88 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 50 | 32 | 19.57 | 60.35 | 307.8 | 3 | 30.88 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 1 | 16 | 0.09172 | 0.4865 | 0.3755 | 7 | 27.44 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 10 | 16 | 0.2882 | 1.743 | 0.387 | 6.5 | 30.09 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 100 | 16 | 0.3815 | 2.78 | 0.3957 | 5.5 | 30.2 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 25 | 16 | 0.3356 | 2.18 | 0.3847 | 6.5 | 30.09 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 5 | 16 | 0.225 | 1.281 | 0.3793 | 6.5 | 30.09 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 50 | 16 | 0.37 | 2.562 | 0.3975 | 6.5 | 30.09 |  | 0.0 | 0.0 |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 1 | 16 | 0.0841 | 0.4573 | 0.2742 | 9 | 0.2569 |  | 2 | 1 |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 10 | 16 | 0.2196 | 1.363 | 0.2719 | 30 | 0.5018 |  | 20 | 10 |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 100 | 16 | 0.273 | 1.823 | 0.2801 | 229 | 0.5018 |  | 200 | 100 |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 25 | 16 | 0.2475 | 1.589 | 0.2734 | 63.5 | 0.5018 |  | 50 | 25 |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 5 | 16 | 0.1841 | 1.068 | 0.2741 | 19 | 0.3618 |  | 10 | 5 |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 50 | 16 | 0.2672 | 1.716 | 0.2811 | 118 | 0.5018 |  | 100 | 50 |

## Failure Modes

| failure_mode | evidence | n_rows | endpoint_feasible_rate | robust_feasible_rate | max_endpoint_violation | max_robust_violation | max_ambiguous_set_size | tie_set_certified_rate | max_tie_aware_total_speedup | event_kernel_max_gap | goal_conditioned_max_gap | goal_conditioned_median_break_even | goal_conditioned_best_speedup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_soft_over_split_or_hidden_boundary | group constraints expose endpoint infeasibility while incremental/group RD removes group violation | 6 | 0.0 | 1 | 233.2 | 0.0 |  |  |  |  |  |  |  |
| corridor_top_set_tie | long corridors create large epsilon/tie sets; tie-aware certificate reports cheap top-set exact fallback separately | 45 |  |  |  |  | 0.0 | nan | 10.49 |  |  |  |  |
| terminal_interior_goal_event_gap | fixed-B event kernels expose option/boundary restriction bias; goal-conditioned event options reduce gap but add query-time interface cost | 192 |  |  |  |  |  |  |  | 30.2 | 0.5018 | 58.5 | 1.823 |

## Solver Validity Aggregate

| solver | beam_width | n_rows | boundary_match_rate | zero_total_violation_gap_rate | feasible_decision_match_rate | median_selection_time_sec | median_oracle_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| actual_refine | 1 | 3 | 1 | 1 | 1 | 3.668 | 10.95 |
| actual_refine | 2 | 3 | 1 | 1 | 1 | 4.063 | 10.95 |
| actual_refine | 4 | 3 | 1 | 1 | 1 | 4.054 | 10.95 |
| operator | 1 | 3 | 0.0 | 0.0 | 0.3333 | 0.9427 | 10.95 |
| operator | 2 | 3 | 0.6667 | 0.6667 | 0.6667 | 1.651 | 10.95 |
| operator | 4 | 3 | 1 | 1 | 1 | 1.6 | 10.95 |

## Discovery Profile Aggregate

| mode | n_rows | median_wall_time_sec | median_speedup_vs_full_recompute | max_speedup_vs_full_recompute | median_probe_green_kernel_time_sec | median_probe_operator_delta_time_sec | median_full_recompute_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cached_incremental_first | 6 | 0.3617 | 4.74 | 5.603 | 0.1236 | 0.108 | nan | 0.0003442 | 0.0 |
| cached_incremental_hit | 6 | 0.0003545 | 4776 | 7519 | 0.0 | 0.0 | nan | 0.0002474 | 1 |
| current_frozen_operator | 6 | 0.3614 | 4.736 | 5.608 | 0.1233 | 0.108 | nan | 0.0003723 | 0.0 |
| full_recompute | 6 | 1.691 | 1 | 1 | 0.125 | 0.1118 | 1.325 | 0.0003575 | 0.0 |

## Incremental Green Update Aggregate

| mode | n_rows | selected_state_match_rate | median_wall_time_sec | median_speedup_vs_full_recompute | max_speedup_vs_full_recompute | max_score_error_vs_exact | max_kernel_error_vs_exact | max_hidden_error_vs_exact | median_n_green_solves | median_n_green_updates | median_parent_update_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| boundary_insertion_score_update | 6 | 1.0 | 0.002205105673056096 | 6.1138616484194666 | 7.376957229810812 | 5.312703969195809e-06 | nan | 8.881784197001252e-16 | 12.0 | 139.0 | 1.0 |
| boundary_insertion_update | 6 | 1.0 | 0.01595097832614556 | 0.7525642597665083 | 0.8342300991313754 | 5.312703969195809e-06 | 1.3322676295501878e-15 | 8.881784197001252e-16 | 12.0 | 139.0 | 1.0 |
| current_frozen_operator | 6 | 0.3333333333333333 | 0.0058261186932213604 | 2.0784256763687954 | 2.286541564313952 | 233.17891857711604 | nan | 1.0 | 12.0 | 0.0 | 0.0 |
| full_recompute | 6 | 1.0 | 0.012428781890776008 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 151.0 | 0.0 | 0.0 |
| static_basis_reuse | 6 | 1.0 | 0.005115150706842542 | 2.344762869362868 | 2.515053120630627 | 233.17891857711604 | nan | 1.0 | 12.0 | 0.0 | 0.0 |

## Theorem-To-Experiment Bridge

| paper_claim | proof_status | experiment_status | manuscript_location | remaining_gap |
| --- | --- | --- | --- | --- |
| The frozen split score is an exact finite difference of a fixed local RD objective. | proved_symbol_present | rows=9, margin_condition=1, stable_when_checked=1 | Method theorem, not adaptive solver guarantee | State frozen candidate universe/options/weights explicitly. |
| First-hit Green kernels define legal compressed edge models on finite absorbing interiors. | proved_symbol_present | rows=80, graph_rows=70, max_start_gap=0.04973 | Graph-SMDP construction | Use exact Green as reference operator; adaptive/truncated variants are certified implementations. |
| Truncated/adaptive Green scores are certified by Neumann tail bounds. | proved_symbol_present | rows=20, final=20, tie_aware_final=20 | Implementation theorem and appendix certificate | Report when tie/top-set exact fallback is used rather than hiding it as speed. |
| Bits distortion admits a controlled finite-difference/Taylor approximation. | proved_symbol_present | rows=9, margin_condition=1, stable_when_checked=1 | Operator approximation and ablation | Keep finite-difference score as the main theorem; gradient score is an approximation. |
| The graph-SMDP Bellman backup is a sup-norm contraction under finite options and gamma<1. | proved_symbol_present | rows=80, graph_rows=70, max_start_gap=0.04973 | Planning correctness lemma | Tie value-gap reporting to residual diagnostics in each benchmark table. |
| Margin and top-set certificates separate stable operator decisions from ambiguous ties. | proved_symbol_present | rows=20, final=20, tie_aware_final=20 | Certificate table | Use tie-aware timing as the conservative runtime accounting. |
| Group-constrained RD makes robustness constraints explicit instead of hiding them in a scalar risk. | proved_symbol_present | rows=18, feasible=12 | Robust objective and main ablation | Use random-maze and held-out probes to show robustness is not hand-tuned to one map. |
| Incremental insertion scoring is an implementation optimization, not a new theorem yet. | lean_pending | rows=30, selected_match=26, max_score_error=233.2 | Runtime ablation, not core correctness theorem | Formalize the insertion algebra only if it becomes a central claim. |
| Fixed-boundary reward relabeling keeps task reward support out of the graph topology. | proved_symbol_present | rows=384, additive=192, event_gap=30.2, goal_conditioned_gap=0.4631 | Multi-task compression and reward relabeling | Present terminal-goal event gaps as option/boundary restriction bias unless goal-conditioned options are counted. |
| Goal-conditioned event options reduce terminal-goal restriction bias without adding the goal to B. | proved_symbol_present | rows=384, additive=192, event_gap=30.2, goal_conditioned_gap=0.4631 | Secondary terminal-goal extension | The gap is much smaller and the backend is shared/batched, but larger multitask runs must show amortized speedup beyond the current break-even table. |
| The extracted graph should generalize across maze instances, not only fixed toy layouts. | empirical_stress_test | rows=6, feasible=3 | Generalization/stress-test section | Scale to larger random maps on node001-node006 for final paper numbers. |

## Certificate Appendix Summary

| certificate | rows | interval_certified | fallback_used | tie_fallback_used | curvature_fallback_used | tie_set_certified | epsilon_optimal_certified | final_certified | tie_aware_final_certified | row_q_lt_1_edges | weighted_q_lt_1_edges | certificates_found | rational_verified | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adaptive_frontier_tail_plus_top_set_fallback | 20 | 4 | 16 | 14 | 2 | 14 | 11 | 20 | 20 |  |  |  |  | runtime_decision_procedure |
| weighted_spectral_sufficient | 8 |  |  |  |  |  |  |  |  | 0 | 16 |  |  | appendix_sufficient_certificate |
| conditioned_rational_weighted_audit | 48 |  |  |  |  |  |  |  |  |  |  | 92 | 92 | appendix_reproducibility_audit |

## Source Artifacts

- large-scale adaptive: `experiments/output/large_scale_compression_adaptive/large_scale_compression.csv`
- core benchmark: `experiments/output/core_benchmark/core_benchmark.csv`
- adaptive certification: `experiments/output/adaptive_green_certification/certification_summary.csv`
- larger group-constrained adaptive: `experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv`
- random maze generalization: `experiments/output/random_maze_generalization/random_maze_generalization.csv`
- fair budget frontier: `experiments/output/fair_budget_frontier/fair_budget_frontier_summary.csv`
- amortized multitask: `experiments/output/amortized_multitask/amortized_multitask.csv`
- edge reward multitask: `experiments/output/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv`
- solver validity: `experiments/output/solver_validity/solver_validity.csv`
- discovery profile/cache: `experiments/output/discovery_profile_cache/discovery_profile_cache.csv`
- incremental Green update: `experiments/output/incremental_green_update/incremental_green_update_aggregate.csv`
- incremental group semantic diff: `experiments/output/group_incremental_semantic_diff/summary.md`
- graph abstraction figures: `experiments/output/graph_abstraction_figures/summary.md`
- theorem/experiment bridge: `experiments/output/theorem_experiment_bridge/theorem_experiment_bridge.csv`
- linear solver thread scaling: `experiments/output/linear_solver_thread_scaling/summary.md`
- weighted spectral certificate: `experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv`
- conditioned rational certificate: `experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv`
