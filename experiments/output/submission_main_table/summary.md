# Submission Main Table

Generated: 2026-07-11T05:32:09

This report is the paper-facing aggregation layer. It keeps audit protocols separate, reports normalized gaps, and never treats the legacy Python VI denominator as the conservative runtime baseline when a matched strong planner measurement is available.

- best total speedup against the legacy Python VI implementation, unique-top fallback: `10.49x`
- best total speedup against the legacy Python VI implementation, tie-aware certificate: `10.49x`
- best tie-aware total speedup against the matched strongest full-state planner: `0.07493x`
- matched strong-planner coverage: `135/135` runtime rows
- best multi-task amortized speedup in the current table: `108.4x` (legacy dense NumPy VI denominator)
- best fixed-B edge reward relabeling speedup: `108.4x` (not a matched sparse-VI claim)
- worst start-value gap in that table: `0.1962`; normalized: `0.005887`
- adaptive final certified decisions under unique-top fallback: `20/20`
- adaptive final certified decisions under tie-aware reporting: `20/20`
- larger group-constrained adaptive feasible rows: `6/6`
- adaptive top-k paired feasible matches: `36/36`
- exact Green is the reference operator; certified adaptive Green plus tie-aware top-set/epsilon certificates are the runtime implementation; fixed-K and weighted spectral certificates are ablations/appendix diagnostics.

## Main Runtime Table

| map | slip | boundary_selector | method | n_states | n_boundary | state_compression_ratio | first_hit_used_steps_max | tail_bound_max | legacy_full_vi_time_sec | strong_full_planner_method | strong_full_planner_time_median_sec | strong_full_planner_time_bootstrap_ci_low_sec | strong_full_planner_time_bootstrap_ci_high_sec | upfront_time_sec | smdp_solve_time_sec | total_time_unique_top_fallback_sec | total_time_with_tie_certificate_sec | planning_speedup | planning_speedup_vs_strong_planner | total_speedup_unique_top_fallback | total_speedup_tie_aware | total_speedup_tie_vs_strong_planner | unique_top_break_even_tasks | amortization_break_even_tasks | strong_planner_tie_break_even_tasks | start_gap | normalized_start_gap | gap_normalization | tie_mode | epsilon_optimal_certified | tie_set_certified | tie_aware_fallback_used | curvature_fallback_used | interval_certified | fallback_used | ambiguous_set_size | tie_aware_final_certified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_256 | 0.0 | endpoints | certified_adaptive_green_rd | 256 | 2.0 | 128 | 254.0 | 0.0 | 1.271 | sparse_vectorized_vi | 0.01343 | 0.01326 | 0.01344 | 0.2432 | 0.0001686 | 0.2434 | 0.2434 | 7536 | 79.63 | 5.22 | 5.22 | 0.05516 | 1 | 1 | 19 | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 51.0 | 8.603e-07 | 5.754 | sparse_vectorized_vi | 0.03576 | 0.03276 | 0.03804 | 8.459 | 0.206 | 8.665 | 8.665 | 27.94 | 0.1736 | 0.6641 | 0.6641 | 0.004126 | 2 | 2 |  | 1.155e-06 | 3.464e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 45.0 | 0.0 | 0.5664 | sparse_vectorized_vi | 0.002972 | 0.002939 | 0.003274 | 8.045 | 0.1944 | 8.239 | 8.239 | 2.913 | 0.01528 | 0.06875 | 0.06875 | 0.0003606 | 22 | 22 |  | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 104.0 | 6.65e-07 | 2.474 | sparse_vectorized_vi | 0.008407 | 0.008135 | 0.008738 | 13.6 | 0.0002484 | 13.6 | 13.6 | 9959 | 33.85 | 0.1819 | 0.1819 | 0.0006182 | 6 | 6 | 1667 | 0.1408 | 0.004225 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | turn_articulation | certified_adaptive_green_rd | 904 | 16.0 | 56.5 | 82.0 | 9.517e-07 | 1.853 | sparse_vectorized_vi | 0.00694 | 0.006555 | 0.007172 | 8.667 | 0.01881 | 8.685 | 8.685 | 98.49 | 0.3689 | 0.2133 | 0.2133 | 0.000799 | 5 | 5 |  | 0.09094 | 0.002728 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | endpoints | certified_adaptive_green_rd | 449 | 2.0 | 224.5 | 151.0 | 0.0 | 1.456 | sparse_vectorized_vi | 0.009032 | 0.008754 | 0.009722 | 1.823 | 0.0001808 | 1.823 | 1.823 | 8053 | 49.94 | 0.7988 | 0.7988 | 0.004954 | 2 | 2 | 206 | 2.131628207280301e-14 | 6.394884621840907e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | turn_articulation | certified_adaptive_green_rd | 256 | 2.0 | 128 | 254.0 | 0.0 | 1.257 | sparse_vectorized_vi | 0.01343 | 0.01326 | 0.01344 | 0.2677 | 0.0001731 | 0.2679 | 0.2679 | 7261 | 77.57 | 4.692 | 4.692 | 0.05012 | 1 | 1 | 21 | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | endpoints | certified_adaptive_green_rd | 512 | 2.0 | 256 | 654.0 | 8.055e-07 | 6.285 | sparse_vectorized_vi | 0.03663 | 0.03547 | 0.03814 | 0.599 | 0.0001758 | 0.5992 | 0.5992 | 3.574e+04 | 208.3 | 10.49 | 10.49 | 0.06113 | 1 | 1 | 17 | 3.5352343275008025e-10 | 1.0605702982502416e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 30.0 | 0.0 | 0.5564 | sparse_vectorized_vi | 0.002972 | 0.002939 | 0.003274 | 5.97 | 0.06181 | 6.032 | 6.032 | 9.002 | 0.04807 | 0.09224 | 0.09224 | 0.0004926 | 13 | 13 |  | 3.552713678800501e-15 | 1.0658141036401511e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 104.0 | 9.982e-07 | 2.487 | sparse_vectorized_vi | 0.008407 | 0.008135 | 0.008738 | 43.24 | 0.8317 | 44.07 | 44.07 | 2.99 | 0.01011 | 0.05642 | 0.05642 | 0.0001908 | 27 | 27 |  | 0.1408 | 0.004225 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 904 | 2.0 | 452 | 87.0 | 8.822e-07 | 1.787 | sparse_vectorized_vi | 0.00694 | 0.006555 | 0.007172 | 11.32 | 0.0001809 | 11.32 | 11.32 | 9875 | 38.36 | 0.1579 | 0.1579 | 0.0006132 | 7 | 7 | 1675 | 0.09094 | 0.002728 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | turn_articulation | certified_adaptive_green_rd | 449 | 128.0 | 3.508 | 11.0 | 0.0 | 1.407 | sparse_vectorized_vi | 0.009032 | 0.008754 | 0.009722 | 71.05 | 18.22 | 89.27 | 89.27 | 0.07722 | 0.0004956 | 0.01576 | 0.01576 | 0.0001012 |  |  |  | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 256 | 2.0 | 128 | 254.0 | 0.0 | 1.228 | sparse_vectorized_vi | 0.01343 | 0.01326 | 0.01344 | 3.673 | 0.0001676 | 3.674 | 3.674 | 7330 | 80.11 | 0.3344 | 0.3344 | 0.003654 | 3 | 3 | 278 | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | turn_articulation | certified_adaptive_green_rd | 512 | 2.0 | 256 | 654.0 | 8.055e-07 | 6.101 | sparse_vectorized_vi | 0.03663 | 0.03547 | 0.03814 | 0.6211 | 0.0002011 | 0.6213 | 0.6213 | 3.033e+04 | 182.1 | 9.82 | 9.82 | 0.05895 | 1 | 1 | 18 | 3.5352343275008025e-10 | 1.0605702982502416e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | endpoints | certified_adaptive_green_rd | 576 | 2.0 | 288 | 70.0 | 4.601e-07 | 0.9371 | sparse_vectorized_vi | 0.004791 | 0.004718 | 0.005549 | 0.5285 | 0.0001691 | 0.5287 | 0.5287 | 5541 | 28.33 | 1.773 | 1.773 | 0.009062 | 1 | 1 | 115 | 0.08633 | 0.00259 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 95.0 | 9.997e-07 | 2.416 | sparse_vectorized_vi | 0.008407 | 0.008135 | 0.008738 | 36.9 | 0.1361 | 37.04 | 37.04 | 17.76 | 0.06179 | 0.06523 | 0.06523 | 0.000227 | 17 | 17 |  | 0.1408 | 0.004225 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 42.0 | 9.892e-07 | 1.823 | sparse_vectorized_vi | 0.00694 | 0.006555 | 0.007172 | 111.2 | 0.6259 | 111.8 | 111.8 | 2.912 | 0.01109 | 0.0163 | 0.0163 | 6.206e-05 | 93 | 93 |  | 0.09094 | 0.002728 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 449 | 20.0 | 22.45 | 95.0 | 0.0 | 1.393 | sparse_vectorized_vi | 0.009032 | 0.008754 | 0.009722 | 4605 | 0.3585 | 4606 | 4606 | 3.886 | 0.02519 | 0.0003025 | 0.0003025 | 1.961e-06 | 4452 | 4452 |  | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 120.0 | 0.0 | 1.229 | sparse_vectorized_vi | 0.01343 | 0.01326 | 0.01344 | 1.342 | 0.3975 | 1.74 | 1.74 | 3.091 | 0.03377 | 0.7063 | 0.7063 | 0.007717 | 2 | 2 |  | 2.131628207280301e-14 | 6.394884621840907e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 512 | 2.0 | 256 | 654.0 | 8.055e-07 | 6.086 | sparse_vectorized_vi | 0.03663 | 0.03547 | 0.03814 | 17.12 | 0.0001973 | 17.12 | 17.12 | 3.084e+04 | 185.6 | 0.3556 | 0.3556 | 0.00214 | 3 | 3 | 470 | 3.5352343275008025e-10 | 1.0605702982502416e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | turn_articulation | certified_adaptive_green_rd | 576 | 4.0 | 144 | 68.0 | 6.483e-07 | 0.914 | sparse_vectorized_vi | 0.004791 | 0.004718 | 0.005549 | 0.6825 | 0.0007953 | 0.6833 | 0.6833 | 1149 | 6.023 | 1.338 | 1.338 | 0.007011 | 1 | 1 | 171 | 0.08633 | 0.00259 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | endpoints | certified_adaptive_green_rd | 404 | 2.0 | 202 | 39.0 | 0.0 | 0.332 | sparse_vectorized_vi | 0.002415 | 0.002371 | 0.002604 | 0.3235 | 0.0001979 | 0.3237 | 0.3237 | 1678 | 12.21 | 1.026 | 1.026 | 0.007462 | 1 | 1 | 146 | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 46.0 | 9.97e-07 | 1.763 | sparse_vectorized_vi | 0.00694 | 0.006555 | 0.007172 | 25.34 | 0.1162 | 25.45 | 25.45 | 15.17 | 0.05974 | 0.06925 | 0.06925 | 0.0002726 | 16 | 16 |  | 0.09094 | 0.002728 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 117.0 | 0.0 | 1.39 | sparse_vectorized_vi | 0.009032 | 0.008754 | 0.009722 | 115 | 0.08606 | 115 | 115 | 16.15 | 0.1049 | 0.01208 | 0.01208 | 7.851e-05 | 89 | 89 |  | 2.131628207280301e-14 | 6.394884621840907e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 30.0 | 0.0 | 1.15 | sparse_vectorized_vi | 0.01343 | 0.01326 | 0.01344 | 1.145 | 0.0457 | 1.191 | 1.191 | 25.16 | 0.2938 | 0.9655 | 0.9655 | 0.01127 | 2 | 2 |  | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 331.0 | 9.816e-07 | 5.77 | sparse_vectorized_vi | 0.03663 | 0.03547 | 0.03814 | 8.241 | 1.712 | 9.953 | 9.953 | 3.371 | 0.0214 | 0.5797 | 0.5797 | 0.00368 | 3 | 3 |  | 1.605e-09 | 4.8136428176803776e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 576 | 2.0 | 288 | 70.0 | 4.601e-07 | 0.8478 | sparse_vectorized_vi | 0.004791 | 0.004718 | 0.005549 | 4.068 | 0.000164 | 4.068 | 4.068 | 5169 | 29.21 | 0.2084 | 0.2084 | 0.001177 | 5 | 5 | 880 | 0.08633 | 0.00259 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | turn_articulation | certified_adaptive_green_rd | 404 | 16.0 | 25.25 | 21.0 | 0.0 | 0.3168 | sparse_vectorized_vi | 0.002415 | 0.002371 | 0.002604 | 1.461 | 0.01783 | 1.479 | 1.479 | 17.77 | 0.1354 | 0.2142 | 0.2142 | 0.001633 | 5 | 5 |  | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | endpoints | certified_adaptive_green_rd | 904 | 2.0 | 452 | 104.0 | 6.176e-07 | 1.977 | sparse_vectorized_vi | 0.008167 | 0.007689 | 0.009419 | 1.642 | 0.0001928 | 1.642 | 1.642 | 1.025e+04 | 42.36 | 1.204 | 1.204 | 0.004975 | 1 | 1 | 206 | 0.1752 | 0.005257 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 85.0 | 0.0 | 1.334 | sparse_vectorized_vi | 0.009032 | 0.008754 | 0.009722 | 256 | 0.04674 | 256.1 | 256.1 | 28.55 | 0.1932 | 0.005211 | 0.005211 | 3.527e-05 | 199 | 199 |  | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | endpoints | certified_adaptive_green_rd | 256 | 2.0 | 128 | 305.0 | 7.438e-07 | 1.387 | sparse_vectorized_vi | 0.01601 | 0.0159 | 0.01695 | 0.2354 | 0.0001423 | 0.2355 | 0.2355 | 9744 | 112.5 | 5.889 | 5.889 | 0.06796 | 1 | 1 | 15 | 6.662048690486698e-11 | 1.998614607146011e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 61.0 | 8.117e-07 | 5.857 | sparse_vectorized_vi | 0.03663 | 0.03547 | 0.03814 | 8.785 | 0.2017 | 8.986 | 8.986 | 29.04 | 0.1816 | 0.6517 | 0.6517 | 0.004076 | 2 | 2 |  | 1.251e-06 | 3.752e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 70.0 | 9.894e-07 | 0.8533 | sparse_vectorized_vi | 0.004791 | 0.004718 | 0.005549 | 9.837 | 0.2994 | 10.14 | 10.14 | 2.85 | 0.016 | 0.08418 | 0.08418 | 0.0004726 | 18 | 18 |  | 0.08633 | 0.00259 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 404 | 2.0 | 202 | 39.0 | 0.0 | 0.3084 | sparse_vectorized_vi | 0.002415 | 0.002371 | 0.002604 | 2.09 | 0.0001509 | 2.09 | 2.09 | 2044 | 16.01 | 0.1475 | 0.1475 | 0.001155 | 7 | 7 | 924 | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | turn_articulation | certified_adaptive_green_rd | 904 | 16.0 | 56.5 | 98.0 | 9.938e-07 | 1.949 | sparse_vectorized_vi | 0.008167 | 0.007689 | 0.009419 | 8.054 | 0.01744 | 8.072 | 8.072 | 111.8 | 0.4684 | 0.2414 | 0.2414 | 0.001012 | 5 | 5 |  | 0.1749 | 0.005246 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | endpoints | certified_adaptive_green_rd | 449 | 2.0 | 224.5 | 189.0 | 7.004e-07 | 1.667 | sparse_vectorized_vi | 0.01175 | 0.01106 | 0.01212 | 2.083 | 0.0001791 | 2.083 | 2.083 | 9304 | 65.57 | 0.8001 | 0.8001 | 0.005639 | 2 | 2 | 181 | 4.095e-09 | 1.2284509409710164e-10 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | turn_articulation | certified_adaptive_green_rd | 256 | 2.0 | 128 | 305.0 | 7.438e-07 | 1.542 | sparse_vectorized_vi | 0.01601 | 0.0159 | 0.01695 | 0.2869 | 0.0002314 | 0.2871 | 0.2871 | 6662 | 69.17 | 5.369 | 5.369 | 0.05575 | 1 | 1 | 19 | 6.662048690486698e-11 | 1.998614607146011e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1022.0 | 0.0 | 10.74 | sparse_vectorized_vi | 0.05356 | 0.05092 | 0.05419 | 2.367 | 0.0001493 | 2.367 | 2.367 | 7.194e+04 | 358.8 | 4.537 | 4.537 | 0.02262 | 1 | 1 | 45 | 3.228e-09 | 9.684306689905504e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 62.0 | 9.955e-07 | 0.9087 | sparse_vectorized_vi | 0.004791 | 0.004718 | 0.005549 | 10.01 | 0.06878 | 10.08 | 10.08 | 13.21 | 0.06965 | 0.09012 | 0.09012 | 0.0004751 | 12 | 12 |  | 0.08633 | 0.00259 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 13.0 | 0.0 | 0.3491 | sparse_vectorized_vi | 0.002415 | 0.002371 | 0.002604 | 12.2 | 0.1485 | 12.34 | 12.34 | 2.351 | 0.01626 | 0.02828 | 0.02828 | 0.0001957 | 61 | 61 |  | 3.552713678800501e-15 | 1.0658141036401511e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 904 | 2.0 | 452 | 104.0 | 6.176e-07 | 2.088 | sparse_vectorized_vi | 0.008167 | 0.007689 | 0.009419 | 12.14 | 0.0001753 | 12.14 | 12.14 | 1.191e+04 | 46.59 | 0.172 | 0.172 | 0.0006728 | 6 | 6 | 1519 | 0.1752 | 0.005257 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | turn_articulation | certified_adaptive_green_rd | 449 | 128.0 | 3.508 | 27.0 | 9.741e-07 | 1.83 | sparse_vectorized_vi | 0.01175 | 0.01106 | 0.01212 | 109.8 | 20.73 | 130.5 | 130.5 | 0.0883 | 0.0005666 | 0.01402 | 0.01402 | 8.998e-05 |  |  |  | 5.497e-06 | 1.649e-07 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 256 | 2.0 | 128 | 305.0 | 7.438e-07 | 1.544 | sparse_vectorized_vi | 0.01601 | 0.0159 | 0.01695 | 4.538 | 0.0002243 | 4.538 | 4.538 | 6885 | 71.36 | 0.3403 | 0.3403 | 0.003527 | 3 | 3 | 288 | 6.662048690486698e-11 | 1.998614607146011e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | turn_articulation | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1022.0 | 0.0 | 13.09 | sparse_vectorized_vi | 0.05356 | 0.05092 | 0.05419 | 2.288 | 0.0001401 | 2.289 | 2.289 | 9.343e+04 | 382.3 | 5.719 | 5.719 | 0.0234 | 1 | 1 | 43 | 3.228e-09 | 9.684306689905504e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | endpoints | certified_adaptive_green_rd | 576 | 2.0 | 288 | 83.0 | 7.417e-07 | 1.124 | sparse_vectorized_vi | 0.006052 | 0.005695 | 0.006312 | 0.5355 | 0.0001726 | 0.5357 | 0.5357 | 6516 | 35.07 | 2.099 | 2.099 | 0.0113 | 1 | 1 | 92 | 0.1762 | 0.005285 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 25.0 | 0.0 | 0.3471 | sparse_vectorized_vi | 0.002415 | 0.002371 | 0.002604 | 5.518 | 0.03836 | 5.556 | 5.556 | 9.048 | 0.06295 | 0.06248 | 0.06248 | 0.0004347 | 18 | 18 |  | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 53.0 | 9.997e-07 | 2.18 | sparse_vectorized_vi | 0.008167 | 0.007689 | 0.009419 | 124.1 | 0.6787 | 124.8 | 124.8 | 3.213 | 0.01203 | 0.01748 | 0.01748 | 6.546e-05 | 83 | 83 |  | 0.1752 | 0.005257 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 449 | 20.0 | 22.45 | 125.0 | 7.976e-07 | 1.984 | sparse_vectorized_vi | 0.01175 | 0.01106 | 0.01212 | 3809 | 0.4739 | 3810 | 3810 | 4.188 | 0.02479 | 0.0005209 | 0.0005209 | 3.083e-06 | 2522 | 2522 |  | 3.711e-06 | 1.113e-07 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 153.0 | 8.159e-07 | 1.526 | sparse_vectorized_vi | 0.01601 | 0.0159 | 0.01695 | 1.637 | 0.4475 | 2.085 | 2.085 | 3.409 | 0.03576 | 0.7318 | 0.7318 | 0.007678 | 2 | 2 |  | 2.668e-07 | 8.004e-09 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1022.0 | 0.0 | 13.19 | sparse_vectorized_vi | 0.05356 | 0.05092 | 0.05419 | 32.1 | 0.0001397 | 32.1 | 32.1 | 9.442e+04 | 383.2 | 0.411 | 0.411 | 0.001668 | 3 | 3 | 601 | 3.228e-09 | 9.684306689905504e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | turn_articulation | certified_adaptive_green_rd | 576 | 4.0 | 144 | 81.0 | 7.442e-07 | 1.11 | sparse_vectorized_vi | 0.006052 | 0.005695 | 0.006312 | 0.6795 | 0.0008027 | 0.6803 | 0.6803 | 1383 | 7.54 | 1.632 | 1.632 | 0.008897 | 1 | 1 | 130 | 0.1762 | 0.005285 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | endpoints | certified_adaptive_green_rd | 404 | 2.0 | 202 | 64.0 | 5.183e-07 | 0.5966 | sparse_vectorized_vi | 0.004253 | 0.004132 | 0.004826 | 0.3504 | 0.0001538 | 0.3506 | 0.3506 | 3879 | 27.65 | 1.702 | 1.702 | 0.01213 | 1 | 1 | 86 | 0.09804 | 0.002941 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 56.0 | 9.992e-07 | 2.148 | sparse_vectorized_vi | 0.008167 | 0.007689 | 0.009419 | 24.25 | 0.1257 | 24.38 | 24.38 | 17.09 | 0.06499 | 0.08813 | 0.08813 | 0.000335 | 12 | 12 |  | 0.1748 | 0.005245 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 150.0 | 9.012e-07 | 1.859 | sparse_vectorized_vi | 0.01175 | 0.01106 | 0.01212 | 154.7 | 0.1896 | 154.9 | 154.9 | 9.802 | 0.06194 | 0.012 | 0.012 | 7.583e-05 | 93 | 93 |  | 1.539e-07 | 4.617e-09 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 50.0 | 8.603e-07 | 1.535 | sparse_vectorized_vi | 0.01601 | 0.0159 | 0.01695 | 1.746 | 0.04821 | 1.794 | 1.794 | 31.84 | 0.332 | 0.8556 | 0.8556 | 0.008921 | 2 | 2 |  | 1.15e-06 | 3.451e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 496.0 | 0.0 | 15.66 | sparse_vectorized_vi | 0.05356 | 0.05092 | 0.05419 | 36.88 | 6.491 | 43.37 | 43.37 | 2.412 | 0.008251 | 0.361 | 0.361 | 0.001235 | 5 | 5 |  | 3.228e-09 | 9.684306689905504e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 576 | 2.0 | 288 | 83.0 | 7.417e-07 | 1.113 | sparse_vectorized_vi | 0.006052 | 0.005695 | 0.006312 | 4.861 | 0.0002084 | 4.861 | 4.861 | 5341 | 29.05 | 0.2289 | 0.2289 | 0.001245 | 5 | 5 | 832 | 0.1762 | 0.005285 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | turn_articulation | certified_adaptive_green_rd | 404 | 16.0 | 25.25 | 58.0 | 9.795e-07 | 0.5992 | sparse_vectorized_vi | 0.004253 | 0.004132 | 0.004826 | 2.42 | 0.02135 | 2.441 | 2.441 | 28.06 | 0.1992 | 0.2454 | 0.2454 | 0.001742 | 5 | 5 |  | 0.09804 | 0.002941 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | endpoints | certified_adaptive_green_rd | 199 | 2.0 | 99.5 | 75.0 | 0.0 | 0.3191 | sparse_vectorized_vi | 0.004287 | 0.004042 | 0.004385 | 0.2875 | 0.0001819 | 0.2877 | 0.2877 | 1754 | 23.57 | 1.109 | 1.109 | 0.0149 | 1 | 1 | 71 | 1.7763568394002505e-14 | 5.329070518200755e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 114.0 | 9.937e-07 | 1.896 | sparse_vectorized_vi | 0.01175 | 0.01106 | 0.01212 | 378.2 | 0.0462 | 378.3 | 378.3 | 41.04 | 0.2543 | 0.005012 | 0.005012 | 3.105e-05 | 205 | 205 |  | 7.615e-07 | 2.284e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | endpoints | certified_adaptive_green_rd | 256 | 2.0 | 128 | 342.0 | 7.245e-07 | 1.695 | sparse_vectorized_vi | 0.01789 | 0.01764 | 0.035 | 0.2386 | 0.0001884 | 0.2388 | 0.2388 | 8995 | 94.96 | 7.098 | 7.098 | 0.07493 | 1 | 1 | 14 | 8.284217756227008e-11 | 2.4852653268681043e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 62.0 | 0.0 | 15.87 | sparse_vectorized_vi | 0.05356 | 0.05092 | 0.05419 | 30.79 | 0.3359 | 31.13 | 31.13 | 47.24 | 0.1595 | 0.5097 | 0.5097 | 0.001721 | 2 | 2 |  | 3.211e-09 | 9.632742603571393e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 83.0 | 9.791e-07 | 1.085 | sparse_vectorized_vi | 0.006052 | 0.005695 | 0.006312 | 10.66 | 0.3795 | 11.04 | 11.04 | 2.86 | 0.01595 | 0.09827 | 0.09827 | 0.000548 | 16 | 16 |  | 0.1762 | 0.005285 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 404 | 2.0 | 202 | 64.0 | 5.183e-07 | 0.5982 | sparse_vectorized_vi | 0.004253 | 0.004132 | 0.004826 | 2.849 | 0.0001618 | 2.85 | 2.85 | 3696 | 26.28 | 0.2099 | 0.2099 | 0.001492 | 5 | 5 | 697 | 0.09804 | 0.002941 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | turn_articulation | certified_adaptive_green_rd | 199 | 52.0 | 3.827 | 13.0 | 0.0 | 0.3162 | sparse_vectorized_vi | 0.004287 | 0.004042 | 0.004385 | 4.033 | 1.144 | 5.178 | 5.178 | 0.2763 | 0.003746 | 0.06107 | 0.06107 | 0.000828 |  |  |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | endpoints | certified_adaptive_green_rd | 449 | 2.0 | 224.5 | 214.0 | 9.201e-07 | 2.006 | sparse_vectorized_vi | 0.01323 | 0.01247 | 0.0133 | 2.468 | 0.0002325 | 2.468 | 2.468 | 8625 | 56.9 | 0.8128 | 0.8128 | 0.005362 | 2 | 2 | 190 | 3.121e-09 | 9.364264030864439e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | turn_articulation | certified_adaptive_green_rd | 256 | 2.0 | 128 | 342.0 | 7.245e-07 | 1.539 | sparse_vectorized_vi | 0.01789 | 0.01764 | 0.035 | 0.2669 | 0.0001426 | 0.2671 | 0.2671 | 1.079e+04 | 125.5 | 5.761 | 5.761 | 0.067 | 1 | 1 | 16 | 8.284217756227008e-11 | 2.4852653268681043e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.43 | sparse_vectorized_vi | 0.0532 | 0.05109 | 0.05473 | 2.34 | 0.0001335 | 2.34 | 2.34 | 1.006e+05 | 398.6 | 5.74 | 5.74 | 0.02273 | 1 | 1 | 45 | 3.228e-09 | 9.684285373623431e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 576 | 24.0 | 24 | 76.0 | 9.982e-07 | 0.9996 | sparse_vectorized_vi | 0.006052 | 0.005695 | 0.006312 | 10.01 | 0.06658 | 10.08 | 10.08 | 15.01 | 0.09091 | 0.09921 | 0.09921 | 0.0006007 | 11 | 11 |  | 0.1762 | 0.005285 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 31.0 | 9.862e-07 | 0.5441 | sparse_vectorized_vi | 0.004253 | 0.004132 | 0.004826 | 18.58 | 0.2116 | 18.8 | 18.8 | 2.571 | 0.02009 | 0.02895 | 0.02895 | 0.0002263 | 56 | 56 |  | 0.09804 | 0.002941 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 199 | 20.0 | 9.95 | 13.0 | 0.0 | 0.284 | sparse_vectorized_vi | 0.004287 | 0.004042 | 0.004385 | 338.5 | 0.1489 | 338.7 | 338.7 | 1.907 | 0.02879 | 0.0008386 | 0.0008386 | 1.266e-05 | 2506 | 2506 |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | turn_articulation | certified_adaptive_green_rd | 449 | 128.0 | 3.508 | 34.0 | 9.94e-07 | 1.918 | sparse_vectorized_vi | 0.01323 | 0.01247 | 0.0133 | 110.4 | 20.16 | 130.6 | 130.6 | 0.09515 | 0.0006563 | 0.01469 | 0.01469 | 0.0001013 |  |  |  | 5.015e-06 | 1.504e-07 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 256 | 2.0 | 128 | 342.0 | 7.245e-07 | 1.664 | sparse_vectorized_vi | 0.01789 | 0.01764 | 0.035 | 4.887 | 0.0002245 | 4.887 | 4.887 | 7410 | 79.7 | 0.3404 | 0.3404 | 0.003661 | 3 | 3 | 277 | 8.284217756227008e-11 | 2.4852653268681043e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | turn_articulation | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.09 | sparse_vectorized_vi | 0.0532 | 0.05109 | 0.05473 | 2.301 | 0.0001715 | 2.301 | 2.301 | 7.632e+04 | 310.2 | 5.687 | 5.687 | 0.02311 | 1 | 1 | 44 | 3.228e-09 | 9.684285373623431e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 61.0 | 0.0 | 1.354 | sparse_vectorized_vi | 0.004777 | 0.004596 | 0.005337 | 1.692 | 0.0002118 | 1.693 | 1.693 | 6392 | 22.55 | 0.7998 | 0.7998 | 0.002822 | 2 | 2 | 371 | 1.7763568394002505e-14 | 5.329070518200755e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 58.0 | 9.941e-07 | 0.5961 | sparse_vectorized_vi | 0.004253 | 0.004132 | 0.004826 | 10.12 | 0.04387 | 10.17 | 10.17 | 13.59 | 0.09694 | 0.05863 | 0.05863 | 0.0004183 | 19 | 19 |  | 0.09804 | 0.002941 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 60.0 | 0.0 | 0.3192 | sparse_vectorized_vi | 0.004287 | 0.004042 | 0.004385 | 5.664 | 0.04411 | 5.708 | 5.708 | 7.237 | 0.09719 | 0.05592 | 0.05592 | 0.0007511 | 21 | 21 |  | 2.131628207280301e-14 | 6.394884621840907e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 449 | 20.0 | 22.45 | 143.0 | 8.941e-07 | 2.002 | sparse_vectorized_vi | 0.01323 | 0.01247 | 0.0133 | 6587 | 0.411 | 6587 | 6587 | 4.871 | 0.0322 | 0.0003039 | 0.0003039 | 2.009e-06 | 4141 | 4141 |  | 3.334e-06 | 1e-07 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 175.0 | 9.578e-07 | 1.676 | sparse_vectorized_vi | 0.01789 | 0.01764 | 0.035 | 1.783 | 0.4797 | 2.263 | 2.263 | 3.494 | 0.0373 | 0.7407 | 0.7407 | 0.007907 | 2 | 2 |  | 1.306e-07 | 3.918e-09 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.5 | sparse_vectorized_vi | 0.0532 | 0.05109 | 0.05473 | 31.98 | 0.0001541 | 31.98 | 31.98 | 8.76e+04 | 345.1 | 0.4222 | 0.4222 | 0.001663 | 3 | 3 | 604 | 3.228e-09 | 9.684285373623431e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | turn_articulation | certified_adaptive_green_rd | 1024 | 4.0 | 256 | 30.0 | 0.0 | 1.397 | sparse_vectorized_vi | 0.004777 | 0.004596 | 0.005337 | 1.85 | 0.0006389 | 1.851 | 1.851 | 2187 | 7.477 | 0.7551 | 0.7551 | 0.002581 | 2 | 2 | 448 | 1.7763568394002505e-14 | 5.329070518200755e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | endpoints | certified_adaptive_green_rd | 404 | 2.0 | 202 | 77.0 | 8.318e-07 | 0.7101 | sparse_vectorized_vi | 0.005198 | 0.004851 | 0.005591 | 0.3879 | 0.0001719 | 0.3881 | 0.3881 | 4132 | 30.25 | 1.83 | 1.83 | 0.01339 | 1 | 1 | 78 | 0.1962 | 0.005887 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 29.0 | 0.0 | 0.3116 | sparse_vectorized_vi | 0.004287 | 0.004042 | 0.004385 | 10.04 | 0.02698 | 10.07 | 10.07 | 11.55 | 0.1589 | 0.03096 | 0.03096 | 0.000426 | 36 | 36 |  | 1.0658141036401504e-14 | 3.1974423109204537e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 171.0 | 9.297e-07 | 2.079 | sparse_vectorized_vi | 0.01323 | 0.01247 | 0.0133 | 176.8 | 0.2389 | 177.1 | 177.1 | 8.7 | 0.05539 | 0.01174 | 0.01174 | 7.473e-05 | 97 | 97 |  | 1.027e-07 | 3.082e-09 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_256 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 256 | 16.0 | 16 | 60.0 | 9.079e-07 | 1.666 | sparse_vectorized_vi | 0.01789 | 0.01764 | 0.035 | 1.854 | 0.0489 | 1.903 | 1.903 | 34.07 | 0.3659 | 0.8754 | 0.8754 | 0.009403 | 2 | 2 |  | 1.249e-06 | 3.746e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 575.0 | 6.776e-07 | 15.37 | sparse_vectorized_vi | 0.0532 | 0.05109 | 0.05473 | 35.64 | 8.71 | 44.35 | 44.35 | 1.764 | 0.006107 | 0.3464 | 0.3464 | 0.001199 | 6 | 6 |  | 3.227e-09 | 9.682302959390661e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 61.0 | 0.0 | 1.363 | sparse_vectorized_vi | 0.004777 | 0.004596 | 0.005337 | 9.54 | 0.0001615 | 9.54 | 9.54 | 8440 | 29.58 | 0.1429 | 0.1429 | 0.0005007 | 8 | 8 | 2067 | 1.7763568394002505e-14 | 5.329070518200755e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | turn_articulation | certified_adaptive_green_rd | 404 | 16.0 | 25.25 | 71.0 | 9.793e-07 | 0.7046 | sparse_vectorized_vi | 0.005198 | 0.004851 | 0.005591 | 2.415 | 0.02084 | 2.436 | 2.436 | 33.82 | 0.2495 | 0.2892 | 0.2892 | 0.002134 | 4 | 4 |  | 0.1962 | 0.005887 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | endpoints | certified_adaptive_green_rd | 199 | 2.0 | 99.5 | 102.0 | 6.311e-07 | 0.4433 | sparse_vectorized_vi | 0.005996 | 0.005743 | 0.007419 | 0.3234 | 0.0001486 | 0.3236 | 0.3236 | 2983 | 40.34 | 1.37 | 1.37 | 0.01853 | 1 | 1 | 56 | 2.974e-08 | 8.921006866557952e-10 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_31 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 449 | 22.0 | 20.41 | 131.0 | 9.941e-07 | 2.077 | sparse_vectorized_vi | 0.01323 | 0.01247 | 0.0133 | 407 | 0.04715 | 407.1 | 407.1 | 44.06 | 0.2807 | 0.005102 | 0.005102 | 3.251e-05 | 201 | 201 |  | 1.235e-06 | 3.704e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | endpoints | certified_adaptive_green_rd | 512 | 2.0 | 256 | 510.0 | 0.0 | 5.118 | sparse_vectorized_vi | 0.02994 | 0.02955 | 0.03191 | 0.7676 | 0.0001926 | 0.7678 | 0.7678 | 2.657e+04 | 155.5 | 6.666 | 6.666 | 0.039 | 1 | 1 | 26 | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 87.0 | 6.58e-07 | 15.8 | sparse_vectorized_vi | 0.0532 | 0.05109 | 0.05473 | 41.66 | 0.4234 | 42.09 | 42.09 | 37.32 | 0.1256 | 0.3754 | 0.3754 | 0.001264 | 3 | 3 |  | 7.082e-07 | 2.125e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 61.0 | 0.0 | 1.404 | sparse_vectorized_vi | 0.004777 | 0.004596 | 0.005337 | 42.73 | 0.4934 | 43.22 | 43.22 | 2.845 | 0.009683 | 0.03248 | 0.03248 | 0.0001105 | 47 | 47 |  | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 404 | 2.0 | 202 | 77.0 | 8.318e-07 | 0.7538 | sparse_vectorized_vi | 0.005198 | 0.004851 | 0.005591 | 3.587 | 0.0002333 | 3.588 | 3.588 | 3231 | 22.28 | 0.2101 | 0.2101 | 0.001449 | 5 | 5 | 723 | 0.1962 | 0.005887 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | turn_articulation | certified_adaptive_green_rd | 199 | 52.0 | 3.827 | 29.0 | 9.741e-07 | 0.4758 | sparse_vectorized_vi | 0.005996 | 0.005743 | 0.007419 | 8.102 | 1.448 | 9.55 | 9.55 | 0.3286 | 0.004141 | 0.04982 | 0.04982 | 0.0006278 |  |  |  | 3.039e-06 | 9.117e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | turn_articulation | certified_adaptive_green_rd | 512 | 2.0 | 256 | 510.0 | 0.0 | 4.759 | sparse_vectorized_vi | 0.02994 | 0.02955 | 0.03191 | 0.6325 | 0.0001662 | 0.6327 | 0.6327 | 2.864e+04 | 180.2 | 7.522 | 7.522 | 0.04733 | 1 | 1 | 22 | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 12.89 | sparse_vectorized_vi | 0.0516 | 0.05102 | 0.05465 | 2.286 | 0.000146 | 2.286 | 2.286 | 8.83e+04 | 353.4 | 5.639 | 5.639 | 0.02257 | 1 | 1 | 45 | 3.228e-09 | 9.684562485290377e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 46.0 | 0.0 | 1.298 | sparse_vectorized_vi | 0.004777 | 0.004596 | 0.005337 | 24.14 | 0.1254 | 24.27 | 24.27 | 10.35 | 0.03808 | 0.05348 | 0.05348 | 0.0001968 | 21 | 21 |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 41.0 | 9.895e-07 | 0.6599 | sparse_vectorized_vi | 0.005198 | 0.004851 | 0.005591 | 21.08 | 0.2384 | 21.32 | 21.32 | 2.768 | 0.02181 | 0.03095 | 0.03095 | 0.0002438 | 51 | 51 |  | 0.1962 | 0.005887 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 199 | 20.0 | 9.95 | 29.0 | 9.741e-07 | 0.4189 | sparse_vectorized_vi | 0.005996 | 0.005743 | 0.007419 | 351 | 0.1853 | 351.1 | 351.1 | 2.261 | 0.03236 | 0.001193 | 0.001193 | 1.708e-05 | 1503 | 1503 |  | 2.965e-06 | 8.896e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 512 | 2.0 | 256 | 510.0 | 0.0 | 5.129 | sparse_vectorized_vi | 0.02994 | 0.02955 | 0.03191 | 14.66 | 0.0001711 | 14.66 | 14.66 | 2.998e+04 | 175 | 0.3499 | 0.3499 | 0.002043 | 3 | 3 | 493 | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | turn_articulation | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.04 | sparse_vectorized_vi | 0.0516 | 0.05102 | 0.05465 | 2.326 | 0.000147 | 2.326 | 2.326 | 8.871e+04 | 350.9 | 5.608 | 5.608 | 0.02218 | 1 | 1 | 46 | 3.228e-09 | 9.684562485290377e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 88.0 | 8.332e-07 | 2.09 | sparse_vectorized_vi | 0.007284 | 0.006951 | 0.007585 | 1.599 | 0.0001676 | 1.599 | 1.599 | 1.247e+04 | 43.45 | 1.307 | 1.307 | 0.004556 | 1 | 1 | 225 | 0.07115 | 0.002135 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_21 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 404 | 21.0 | 19.24 | 70.0 | 9.936e-07 | 0.7007 | sparse_vectorized_vi | 0.005198 | 0.004851 | 0.005591 | 10.09 | 0.04124 | 10.14 | 10.14 | 16.99 | 0.126 | 0.06913 | 0.06913 | 0.0005129 | 16 | 16 |  | 0.1962 | 0.005887 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 85.0 | 7.011e-07 | 0.4365 | sparse_vectorized_vi | 0.005996 | 0.005743 | 0.007419 | 6.974 | 0.08669 | 7.061 | 7.061 | 5.036 | 0.06917 | 0.06183 | 0.06183 | 0.0008492 | 20 | 20 |  | 2.62e-07 | 7.859e-09 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 245.0 | 0.0 | 5.075 | sparse_vectorized_vi | 0.02994 | 0.02955 | 0.03191 | 7.769 | 1.728 | 9.497 | 9.497 | 2.937 | 0.01733 | 0.5344 | 0.5344 | 0.003153 | 3 | 3 |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 1024.0 | 1 | 13.07 | sparse_vectorized_vi | 0.0516 | 0.05102 | 0.05465 | 32.51 | 0.0001316 | 32.51 | 32.51 | 9.931e+04 | 392.1 | 0.4019 | 0.4019 | 0.001587 | 3 | 3 | 632 | 3.228e-09 | 9.684562485290377e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | turn_articulation | certified_adaptive_green_rd | 1024 | 4.0 | 256 | 86.0 | 9.793e-07 | 2.12 | sparse_vectorized_vi | 0.007284 | 0.006951 | 0.007585 | 2.195 | 0.0009235 | 2.196 | 2.196 | 2295 | 7.887 | 0.9654 | 0.9654 | 0.003317 | 2 | 2 | 346 | 0.07115 | 0.002135 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | endpoints | certified_adaptive_green_rd | 904 | 2.0 | 452 | 59.0 | 0.0 | 1.18 | sparse_vectorized_vi | 0.004575 | 0.004298 | 0.004722 | 1.513 | 0.0002462 | 1.514 | 1.514 | 4792 | 18.58 | 0.7795 | 0.7795 | 0.003022 | 2 | 2 | 350 | 1.7763568394002505e-14 | 5.329070518200755e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 49.0 | 9.494e-07 | 0.4443 | sparse_vectorized_vi | 0.005996 | 0.005743 | 0.007419 | 15.27 | 0.02317 | 15.29 | 15.29 | 19.18 | 0.2588 | 0.02906 | 0.02906 | 0.0003922 | 37 | 37 |  | 1.032e-06 | 3.095e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 31.0 | 0.0 | 5.126 | sparse_vectorized_vi | 0.02994 | 0.02955 | 0.03191 | 6.597 | 0.2172 | 6.815 | 6.815 | 23.6 | 0.1378 | 0.7523 | 0.7523 | 0.004394 | 2 | 2 |  | 1.4210854715202004e-14 | 4.2632564145606044e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 637.0 | 8.22e-07 | 15.71 | sparse_vectorized_vi | 0.0516 | 0.05102 | 0.05465 | 46.89 | 9.382 | 56.28 | 56.28 | 1.674 | 0.005499 | 0.2791 | 0.2791 | 0.0009168 | 8 | 8 |  | 3.229e-09 | 9.685777513368528e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 88.0 | 8.332e-07 | 2.152 | sparse_vectorized_vi | 0.007284 | 0.006951 | 0.007585 | 12.32 | 0.0002155 | 12.32 | 12.32 | 9988 | 33.81 | 0.1746 | 0.1746 | 0.0005911 | 6 | 6 | 1744 | 0.07115 | 0.002135 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | turn_articulation | certified_adaptive_green_rd | 904 | 16.0 | 56.5 | 31.0 | 0.0 | 1.177 | sparse_vectorized_vi | 0.004575 | 0.004298 | 0.004722 | 6.32 | 0.02007 | 6.34 | 6.34 | 58.63 | 0.2279 | 0.1856 | 0.1856 | 0.0007215 | 6 | 6 |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | endpoints | certified_adaptive_green_rd | 199 | 2.0 | 99.5 | 117.0 | 9.364e-07 | 0.5337 | sparse_vectorized_vi | 0.00677 | 0.006576 | 0.007153 | 0.3673 | 0.0001621 | 0.3674 | 0.3674 | 3292 | 41.77 | 1.452 | 1.452 | 0.01843 | 1 | 1 | 56 | 5.012e-08 | 1.504e-09 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | endpoints | certified_adaptive_green_rd | 512 | 2.0 | 256 | 590.0 | 8.619e-07 | 5.733 | sparse_vectorized_vi | 0.03576 | 0.03276 | 0.03804 | 0.6556 | 0.0001806 | 0.6558 | 0.6558 | 3.175e+04 | 198 | 8.741 | 8.741 | 0.05452 | 1 | 1 | 19 | 2.169358026549162e-10 | 6.508074079647491e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_1024 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 101.0 | 6.132e-07 | 15.78 | sparse_vectorized_vi | 0.0516 | 0.05102 | 0.05465 | 38.36 | 0.3103 | 38.67 | 38.67 | 50.85 | 0.1663 | 0.408 | 0.408 | 0.001334 | 3 | 3 |  | 6.403e-07 | 1.921e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 88.0 | 9.929e-07 | 2.112 | sparse_vectorized_vi | 0.007284 | 0.006951 | 0.007585 | 38.83 | 0.716 | 39.55 | 39.55 | 2.95 | 0.01017 | 0.05342 | 0.05342 | 0.0001842 | 28 | 28 |  | 0.07115 | 0.002135 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 904 | 2.0 | 452 | 59.0 | 0.0 | 1.2 | sparse_vectorized_vi | 0.004575 | 0.004298 | 0.004722 | 9.089 | 0.0002172 | 9.089 | 9.089 | 5526 | 21.07 | 0.132 | 0.132 | 0.0005033 | 8 | 8 | 2086 | 1.7763568394002505e-14 | 5.329070518200755e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | turn_articulation | certified_adaptive_green_rd | 199 | 52.0 | 3.827 | 36.0 | 8.822e-07 | 0.5439 | sparse_vectorized_vi | 0.00677 | 0.006576 | 0.007153 | 7.273 | 1.35 | 8.623 | 8.623 | 0.4028 | 0.005014 | 0.06307 | 0.06307 | 0.0007851 |  |  |  | 2.828e-06 | 8.483e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | turn_articulation | certified_adaptive_green_rd | 512 | 2.0 | 256 | 590.0 | 8.619e-07 | 5.787 | sparse_vectorized_vi | 0.03576 | 0.03276 | 0.03804 | 0.7832 | 0.0001917 | 0.7834 | 0.7834 | 3.018e+04 | 186.5 | 7.387 | 7.387 | 0.04564 | 1 | 1 | 23 | 2.169358026549162e-10 | 6.508074079647491e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | endpoints | certified_adaptive_green_rd | 576 | 2.0 | 288 | 45.0 | 0.0 | 0.6086 | sparse_vectorized_vi | 0.002972 | 0.002939 | 0.003274 | 0.5435 | 0.0002096 | 0.5438 | 0.5438 | 2904 | 14.18 | 1.119 | 1.119 | 0.005465 | 1 | 1 | 197 | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.05 | coverage_sqrt | certified_adaptive_green_rd | 1024 | 32.0 | 32 | 80.0 | 9.993e-07 | 2.164 | sparse_vectorized_vi | 0.007284 | 0.006951 | 0.007585 | 42.91 | 0.1548 | 43.07 | 43.07 | 13.98 | 0.04705 | 0.05025 | 0.05025 | 0.0001691 | 22 | 22 |  | 0.07115 | 0.002135 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | betweenness_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 20.0 | 0.0 | 1.217 | sparse_vectorized_vi | 0.004575 | 0.004298 | 0.004722 | 90.4 | 0.5093 | 90.9 | 90.9 | 2.39 | 0.008982 | 0.01339 | 0.01339 | 5.032e-05 | 128 | 128 |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 199 | 20.0 | 9.95 | 36.0 | 8.778e-07 | 0.529 | sparse_vectorized_vi | 0.00677 | 0.006576 | 0.007153 | 360.1 | 0.1984 | 360.3 | 360.3 | 2.666 | 0.03413 | 0.001468 | 0.001468 | 1.879e-05 | 1090 | 1090 |  | 2.667e-06 | 8.002e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 512 | 2.0 | 256 | 590.0 | 8.619e-07 | 5.674 | sparse_vectorized_vi | 0.03576 | 0.03276 | 0.03804 | 16.04 | 0.000174 | 16.04 | 16.04 | 3.261e+04 | 205.5 | 0.3538 | 0.3538 | 0.00223 | 3 | 3 | 451 | 2.169358026549162e-10 | 6.508074079647491e-12 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | turn_articulation | certified_adaptive_green_rd | 576 | 4.0 | 144 | 22.0 | 0.0 | 0.5541 | sparse_vectorized_vi | 0.002972 | 0.002939 | 0.003274 | 0.617 | 0.000657 | 0.6177 | 0.6177 | 843.3 | 4.523 | 0.8971 | 0.8971 | 0.004811 | 2 | 2 | 267 | 0.0 | 0.0 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | endpoints | certified_adaptive_green_rd | 1024 | 2.0 | 512 | 104.0 | 6.65e-07 | 2.396 | sparse_vectorized_vi | 0.008407 | 0.008135 | 0.008738 | 1.672 | 0.0001915 | 1.672 | 1.672 | 1.251e+04 | 43.89 | 1.433 | 1.433 | 0.005029 | 1 | 1 | 204 | 0.1408 | 0.004225 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.0 | coverage_sqrt | certified_adaptive_green_rd | 904 | 31.0 | 29.16 | 21.0 | 0.0 | 1.168 | sparse_vectorized_vi | 0.004575 | 0.004298 | 0.004722 | 18.43 | 0.1472 | 18.58 | 18.58 | 7.939 | 0.03109 | 0.06288 | 0.06288 | 0.0002462 | 19 | 19 |  | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | betweenness_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 98.0 | 8.549e-07 | 0.5205 | sparse_vectorized_vi | 0.00677 | 0.006576 | 0.007153 | 8.062 | 0.1019 | 8.164 | 8.164 | 5.107 | 0.06643 | 0.06375 | 0.06375 | 0.0008293 | 20 | 20 |  | 4.736e-07 | 1.421e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| corridor_512 | 0.05 | betweenness_sqrt | certified_adaptive_green_rd | 512 | 23.0 | 22.26 | 295.0 | 6.938e-07 | 5.637 | sparse_vectorized_vi | 0.03576 | 0.03276 | 0.03804 | 8.045 | 1.8 | 9.845 | 9.845 | 3.132 | 0.01986 | 0.5726 | 0.5726 | 0.003632 | 3 | 3 |  | 2.883e-09 | 8.648932237065317e-11 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_24 | 0.0 | graph_rd_surrogate_joint | certified_adaptive_green_rd | 576 | 2.0 | 288 | 45.0 | 0.0 | 0.5626 | sparse_vectorized_vi | 0.002972 | 0.002939 | 0.003274 | 3.381 | 0.0001666 | 3.382 | 3.382 | 3377 | 17.84 | 0.1664 | 0.1664 | 0.0008787 | 7 | 7 | 1206 | 7.105427357601002e-15 | 2.1316282072803022e-16 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| open_room_32 | 0.1 | turn_articulation | certified_adaptive_green_rd | 1024 | 4.0 | 256 | 102.0 | 8.868e-07 | 2.297 | sparse_vectorized_vi | 0.008407 | 0.008135 | 0.008738 | 1.972 | 0.0007778 | 1.973 | 1.973 | 2953 | 10.81 | 1.164 | 1.164 | 0.004261 | 1 | 1 | 259 | 0.1408 | 0.004225 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| four_rooms_31 | 0.05 | endpoints | certified_adaptive_green_rd | 904 | 2.0 | 452 | 87.0 | 8.822e-07 | 1.667 | sparse_vectorized_vi | 0.00694 | 0.006555 | 0.007172 | 1.416 | 0.0001746 | 1.416 | 1.416 | 9548 | 39.75 | 1.177 | 1.177 | 0.0049 | 1 | 1 | 210 | 0.09094 | 0.002728 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |
| maze_21 | 0.1 | coverage_sqrt | certified_adaptive_green_rd | 199 | 15.0 | 13.27 | 58.0 | 9.903e-07 | 0.4793 | sparse_vectorized_vi | 0.00677 | 0.006576 | 0.007153 | 15.61 | 0.01994 | 15.63 | 15.63 | 24.03 | 0.3395 | 0.03067 | 0.03067 | 0.0004333 | 34 | 34 |  | 1.228e-06 | 3.684e-08 | discounted_unit_reward_bound |  |  |  |  |  |  |  |  |  |

## One-Shot Operator Versus Search

The one-shot rows measure one frozen sparse Green response and one threshold pass; iterative/exact search appears only in the paired speedup columns. Final-kernel time is reported separately, so extraction speed is not confused with graph-model construction.

| source | method | n_rows | median_n_boundary | median_state_compression | median_selection_time_sec | median_final_kernel_time_sec | median_selection_speedup_vs_iterative | median_total_speedup_vs_iterative | median_selection_speedup_vs_exact_search | median_total_speedup_vs_exact_search | median_total_speedup_vs_sparse_vi | max_normalized_value_gap | median_D_occ | median_boundary_jaccard_vs_iterative |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| one_shot_rd_operator | one_shot_rd_t0p10 | 12 | 3.5 | 21 | 0.01143 | 0.02981 | 35.21 | 7.681 | 153.2 | 23.26 | 0.01721 | 0.009628 | 1.4470983993044236e-16 | 0.6667 |
| one_shot_rd_operator | one_shot_rd_t0p15 | 12 | 3.5 | 21 | 0.01095 | 0.02944 | 40.06 | 7.772 | 157.2 | 22.86 | 0.01715 | 0.009628 | 1.4470983993044236e-16 | 0.6667 |
| one_shot_rd_operator | one_shot_rd_t0p20 | 12 | 3.5 | 21 | 0.01086 | 0.03006 | 51.27 | 8.073 | 157.3 | 22.95 | 0.01707 | 0.009628 | 1.4470983993044236e-16 | 0.6667 |
| one_shot_rd_operator_random | one_shot_rd_t0p15 | 108 | 18 | 6.296 | 0.0247 | 0.8779 | nan | nan | nan | nan | 0.003538 | 1.457e-07 | 9.869e-07 | nan |
| one_shot_rd_operator_random | one_shot_rd_t0p75 | 108 | 10 | 9.7 | 0.02493 | 0.6243 | nan | nan | nan | nan | 0.005842 | 1.059e-07 | 7 | nan |
| one_shot_rd_operator_random_reference | one_shot_rd_t0p15 | 20 | 13 | 4.85 | 0.02333 | 0.5449 | 369.5 | 12.94 | nan | nan | 0.005735 | 1.195e-07 | 4.866e-08 | 0.9199 |
| one_shot_rd_operator_xl_end_to_end | one_shot_rd_t0p15 | 27 | 3 | 192 | 0.07967 | 2.049 | 947.1 | 15.13 | nan | nan | 0.003863 | 0.009098 | 2.3645527521133335e-53 | nan |

### Frozen Group-FD Prefix Audit

This diagnostic freezes one exact multi-probe candidate order, audits prefixes without rescoring, and exposes nonmonotone feasibility caused by the changing boundary/option library.

| map | slip | n_tested_prefixes | max_tested_k | any_feasible | feasible_prefixes | first_feasible_k | infeasible_after_first_feasible | best_feasible_state_compression | n_candidate_insertion_evaluations | n_beam_expansions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| four_rooms_11 | 0.05 | 13 | 24 | True | 3,4,5,6,8,10 | 3 | True | 20.8 | 0 | 0 |
| maze_13 | 0.05 | 13 | 24 | False |  |  | False | nan | 0 | 0 |
| open_room_12 | 0.05 | 12 | 20 | True | 2 | 2 | True | 36 | 0 | 0 |

### Learned Boundary Proposal Ablation

The transition-graph GNN is an uncertified ablation, not a second proposed method. Raw joint pass, the fixed candidate-family oracle, held-out routing misses, audit coverage, full-audit speed, and certification status are shown together to prevent proposal quality from being read as certified pipeline quality.

| source | proposal | n_rows | raw_joint_pass | candidate_oracle_joint_pass | adaptive_reference_joint_pass | mean_boundary_jaccard | group_feasible_rate | median_selection_speedup | audit_coverage | failure_recall | undetected_failures | full_audit_speedup | max_normalized_start_gap | certified | certification_status | gate_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| learned_ablation | Boundary-only transition-graph GNN | 90 | 68/90 |  | 71/90 | 0.6508465608465608 | 0.7777777777777778 | 769.8192740217598 | 0.4 | 0.5 | 11/22 | 0.4438337324121785 | 0.022249000484847407 | no | uncertified proposal ablation | ablation |
| fixed_baseline | Nearest-start fixed proposal | 90 | 62/90 |  | 71/90 | 0.6788888888888889 | 0.6888888888888889 | 877.8809547874098 |  |  |  | 0.4349989758681264 | 0.02224900781274634 | no | uncertified proposal ablation | ablation |
| fixed_baseline | Topology fixed proposal | 90 | 10/90 |  | 71/90 | 0.5236507936507936 | 0.1111111111111111 | 879.0496567025946 |  |  |  | 0.32348480523589856 | 0.02224900784850102 | no | uncertified proposal ablation | ablation |
| learned_ablation | Constraint-aware fixed-family reranker | 90 | 81/90 | 85/90 | 71/90 | 0.5683421516754853 | 0.9222222222222223 | 656.0300626356689 | 0.14444444444444443 | 0.3333333333333333 | 6/9 | 0.4281247548202982 | 0.022249000484847407 | no | raw proposal quality only; full audit required | NO-GO under predefined go/no-go protocol |
| explicit_reference | Adaptive RD reference proposal | 90 | 71/90 |  | 71/90 |  | 0.7888888888888889 | 1 | certificate/audit dependent |  |  | 1 |  | conditional | reference constructor; explicit certificates and production audit govern acceptance | reference/fallback, not a joint-pass oracle |
| oracle_envelope | Candidate-family oracle | 90 | 85/90 | 85/90 | 71/90 |  |  |  |  |  |  |  |  | not applicable | offline upper envelope; not deployable | diagnostic only |

#### Paired Descriptive Comparison

The constraint-aware fixed-family reranker and adaptive RD reference optimize different objectives and provide different guarantees. Their paired comparison is therefore descriptive. The bootstrap interval excludes zero, whereas the discrete exact McNemar test does not reject at the 5% level; neither result supports a learned-method superiority claim.

| n_pairs | both_pass | reranker_only | reference_only | both_fail | paired_pass_rate_difference | paired_bootstrap_ci_low | paired_bootstrap_ci_high | exact_mcnemar_pvalue | comparison_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 90 | 64 | 17 | 7 | 2 | 0.1111111111111111 | 0.011111111111111112 | 0.2111111111111111 | 0.06391465663909912 | descriptive_different_objectives_and_guarantees |

## Runtime By Boundary Selector

This aggregation prevents the fastest endpoint or topology selector from being reported as a typical RD-selector gain.

| boundary_selector | n_rows | n_strong_planner_rows | median_state_compression | median_normalized_start_gap | max_normalized_start_gap | legacy_median_total_speedup | strong_planner_median_planning_speedup | strong_planner_planning_speedup_ci95_low | strong_planner_planning_speedup_ci95_high | strong_planner_median_total_speedup | strong_planner_total_speedup_ci95_low | strong_planner_total_speedup_ci95_high | strong_planner_best_total_speedup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| betweenness_sqrt | 27 | 27 | 22.26 | 3.082e-09 | 0.005887 | 0.06183 | 0.01733 | 0.01203 | 0.03377 | 0.0004726 | 0.0001908 | 0.0009168 | 0.007907 |
| coverage_sqrt | 27 | 27 | 22.26 | 3.451e-08 | 0.005887 | 0.06925 | 0.1378 | 0.06965 | 0.1816 | 0.0004347 | 0.000335 | 0.001264 | 0.01127 |
| endpoints | 27 | 27 | 256 | 9.684285373623431e-11 | 0.005887 | 1.452 | 43.45 | 35.07 | 79.63 | 0.01213 | 0.005465 | 0.02257 | 0.07493 |
| graph_rd_surrogate_joint | 27 | 27 | 256 | 9.684306689905504e-11 | 0.005887 | 0.1819 | 29.58 | 21.07 | 71.36 | 0.001155 | 0.0005911 | 0.001587 | 0.003661 |
| turn_articulation | 27 | 27 | 128 | 9.684306689905504e-11 | 0.005887 | 0.8971 | 6.023 | 0.2279 | 69.17 | 0.003317 | 0.001012 | 0.02218 | 0.067 |

## Strong Full-State Planner Audit

| map | slip | strongest_method | strongest_time_q1_sec | strongest_time_median_sec | strongest_time_q3_sec | strongest_time_bootstrap_ci_low_sec | strongest_time_bootstrap_ci_high_sec | strongest_backup_median | max_value_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_1024 | 0.0 | sparse_vectorized_vi | 0.05144829803612083 | 0.053556247032247484 | 0.054049337981268764 | 0.050918371067382395 | 0.05418839096091688 | 3100672.0 | 3.1975915248949605e-09 |
| corridor_1024 | 0.05 | sparse_vectorized_vi | 0.051162007031962276 | 0.053195592015981674 | 0.05429827398620546 | 0.051085114013403654 | 0.05472545698285103 | 3100672.0 | 3.1975915248949605e-09 |
| corridor_1024 | 0.1 | sparse_vectorized_vi | 0.05119607294909656 | 0.05159760592505336 | 0.05248683306854218 | 0.05102044704835862 | 0.054653414990752935 | 3100672.0 | 3.1975773140402453e-09 |
| corridor_256 | 0.0 | sparse_vectorized_vi | 0.013337359065189958 | 0.013425156008452177 | 0.013428965001367033 | 0.01326356502249837 | 0.013437979039736092 | 262144.0 | 0.0 |
| corridor_256 | 0.05 | sparse_vectorized_vi | 0.015959182986989617 | 0.016005630022846162 | 0.016095826984383166 | 0.01589729404076934 | 0.016950838966295123 | 314368.0 | 7.477041208403534e-11 |
| corridor_256 | 0.1 | sparse_vectorized_vi | 0.01773657405283302 | 0.017892675008624792 | 0.020713304984383285 | 0.017639065976254642 | 0.03499655402265489 | 349184.0 | 1.3950796073913807e-10 |
| corridor_512 | 0.0 | sparse_vectorized_vi | 0.02956795901991427 | 0.02994245698209852 | 0.031676332000643015 | 0.02954983792733401 | 0.03190628404263407 | 1048576.0 | 0.0 |
| corridor_512 | 0.05 | sparse_vectorized_vi | 0.03380395798012614 | 0.03575596702285111 | 0.036002214066684246 | 0.03275873709935695 | 0.03803691396024078 | 1169408.0 | 2.1548629547396558e-10 |
| corridor_512 | 0.1 | sparse_vectorized_vi | 0.03575747297145426 | 0.036629739101044834 | 0.03774758707731962 | 0.03547177102882415 | 0.03814085805788636 | 1265664.0 | 3.5134917197865434e-10 |
| four_rooms_21 | 0.0 | sparse_vectorized_vi | 0.002381086931563914 | 0.002415077993646264 | 0.0025613970356062055 | 0.002371411072090268 | 0.0026036810595542192 | 66256.0 | 0.0 |
| four_rooms_21 | 0.05 | sparse_vectorized_vi | 0.004137141979299486 | 0.004252844024449587 | 0.004426253959536552 | 0.004131871974095702 | 0.004826132906600833 | 114736.0 | 2.7068125518781017e-11 |
| four_rooms_21 | 0.1 | sparse_vectorized_vi | 0.00515775999519974 | 0.005198272061534226 | 0.005210582981817424 | 0.004851473029702902 | 0.005590746062807739 | 137360.0 | 1.0221157253909041e-10 |
| four_rooms_31 | 0.0 | sparse_vectorized_vi | 0.004307730938307941 | 0.004574556020088494 | 0.004587774048559368 | 0.004297857987694442 | 0.004721722099930048 | 220576.0 | 0.0 |
| four_rooms_31 | 0.05 | sparse_vectorized_vi | 0.006777568021789193 | 0.006939683109521866 | 0.00704955798573792 | 0.006555426982231438 | 0.007172208046540618 | 339904.0 | 4.89173146434041e-11 |
| four_rooms_31 | 0.1 | sparse_vectorized_vi | 0.007729655015282333 | 0.008166893967427313 | 0.00845446006860584 | 0.00768882199190557 | 0.00941930792760104 | 401376.0 | 1.0395595495538146e-10 |
| maze_21 | 0.0 | sparse_vectorized_vi | 0.004228302976116538 | 0.004287393065169454 | 0.004299178021028638 | 0.0040418090065941215 | 0.004384647938422859 | 61292.0 | 0.0 |
| maze_21 | 0.05 | sparse_vectorized_vi | 0.0058757850201800466 | 0.00599578395485878 | 0.006308821029961109 | 0.0057434000773355365 | 0.007418813998810947 | 87560.0 | 4.8753889814179274e-11 |
| maze_21 | 0.1 | sparse_vectorized_vi | 0.006657997029833496 | 0.006770291016437113 | 0.007051877910271287 | 0.006576173007488251 | 0.007152648991905153 | 101888.0 | 7.363709642049798e-11 |
| maze_31 | 0.0 | sparse_vectorized_vi | 0.008916265098378062 | 0.00903156097047031 | 0.009186677983962 | 0.008753789938054979 | 0.009721923037432134 | 274788.0 | 0.0 |
| maze_31 | 0.05 | sparse_vectorized_vi | 0.011226595030166209 | 0.011745924013666809 | 0.01176072598900646 | 0.011058734962716699 | 0.012118864920921624 | 352016.0 | 4.462208380573429e-11 |
| maze_31 | 0.1 | sparse_vectorized_vi | 0.012716626049950719 | 0.013232946977950633 | 0.013264960958622396 | 0.012469556997530162 | 0.013302403036504984 | 396916.0 | 1.34683375563327e-10 |
| open_room_24 | 0.0 | sparse_vectorized_vi | 0.0029433449963107705 | 0.002971566980704665 | 0.0032338181044906378 | 0.0029392950236797333 | 0.003273959970101714 | 108288.0 | 0.0 |
| open_room_24 | 0.05 | sparse_vectorized_vi | 0.004786101984791458 | 0.004790529026649892 | 0.005068668979220092 | 0.004717624047771096 | 0.005549486028030515 | 177408.0 | 4.4003911625623005e-11 |
| open_room_24 | 0.1 | sparse_vectorized_vi | 0.00577874097507447 | 0.006052345037460327 | 0.006276522995904088 | 0.005695187021046877 | 0.006312241079285741 | 211968.0 | 7.751310704406933e-11 |
| open_room_32 | 0.0 | sparse_vectorized_vi | 0.004604557994753122 | 0.004777009948156774 | 0.004976834054104984 | 0.004595623933710158 | 0.005336954025551677 | 258048.0 | 0.0 |
| open_room_32 | 0.05 | sparse_vectorized_vi | 0.007050136919133365 | 0.00728441309183836 | 0.007445723982527852 | 0.006951201008632779 | 0.00758455996401608 | 393216.0 | 3.942091097997036e-11 |
| open_room_32 | 0.1 | sparse_vectorized_vi | 0.008174521033652127 | 0.008407191024161875 | 0.008667983929626644 | 0.008134630043059587 | 0.008738178992643952 | 462848.0 | 8.386891181544343e-11 |

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

## Direct State-Abstraction And Schur Baselines

Exact/epsilon homogeneous aggregation preserves a primitive-action abstract MDP; Q*-aggregation and policy-Kron are explicitly labeled oracles because they consume full optimal information.

| map | slip | method | target_count | n_abstract_states | state_compression_ratio | normalized_start_gap | normalized_policy_start_gap | homogeneity_error | time_median_sec | total_speedup_median | representation_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_32 | 0.0 | epsilon_homogeneous | 12 | 2 | 16 | 0.1989 | 0.0 | 1 | 2.681 | 0.0006693 | full_action_abstract_mdp |
| corridor_32 | 0.0 | epsilon_homogeneous | 2 | 2 | 16 | 0.1989 | 0.0 | 1 | 2.625 | 0.0006781 | full_action_abstract_mdp |
| corridor_32 | 0.0 | epsilon_homogeneous | 4 | 2 | 16 | 0.1989 | 0.0 | 1 | 2.661 | 0.0006768 | full_action_abstract_mdp |
| corridor_32 | 0.0 | epsilon_homogeneous | 7 | 2 | 16 | 0.1989 | 0.0 | 1 | 2.643 | 0.0006729 | full_action_abstract_mdp |
| corridor_32 | 0.0 | exact_model_minimization | 2 | 32 | 1 | 0.0 | 0.0 | 0.0 | 0.05733 | 0.03192 | full_action_abstract_mdp |
| corridor_32 | 0.0 | policy_kron_oracle | 12 | 12 | 2.667 | 0.0 | 0.0 | nan | 0.07679 | 0.02361 | fixed_optimal_policy_only |
| corridor_32 | 0.0 | policy_kron_oracle | 2 | 2 | 16 | 0.0 | 0.0 | nan | 0.08949 | 0.01997 | fixed_optimal_policy_only |
| corridor_32 | 0.0 | policy_kron_oracle | 4 | 4 | 8 | 0.0 | 0.0 | nan | 0.09824 | 0.01851 | fixed_optimal_policy_only |
| corridor_32 | 0.0 | policy_kron_oracle | 7 | 7 | 4.571 | 0.0 | 0.0 | nan | 0.08125 | 0.02447 | fixed_optimal_policy_only |
| corridor_32 | 0.0 | qstar_oracle_aggregation | 12 | 12 | 2.667 | 0.01969 | 0.0 | 1 | 0.005859 | 0.3061 | full_action_abstract_mdp |
| corridor_32 | 0.0 | qstar_oracle_aggregation | 2 | 2 | 16 | 0.1989 | 0.0 | 1 | 0.008321 | 0.216 | full_action_abstract_mdp |
| corridor_32 | 0.0 | qstar_oracle_aggregation | 4 | 4 | 8 | 0.07811 | 0.0 | 1 | 0.00651 | 0.2764 | full_action_abstract_mdp |
| corridor_32 | 0.0 | qstar_oracle_aggregation | 7 | 7 | 4.571 | 0.03985 | 0.0 | 1 | 0.006043 | 0.2977 | full_action_abstract_mdp |
| corridor_32 | 0.05 | epsilon_homogeneous | 12 | 2 | 16 | 0.2097 | 9.875230869868249e-13 | 0.95 | 2.729 | 0.002024 | full_action_abstract_mdp |
| corridor_32 | 0.05 | epsilon_homogeneous | 2 | 2 | 16 | 0.2097 | 9.875230869868249e-13 | 0.95 | 2.672 | 0.002386 | full_action_abstract_mdp |
| corridor_32 | 0.05 | epsilon_homogeneous | 4 | 2 | 16 | 0.2097 | 9.875230869868249e-13 | 0.95 | 2.701 | 0.002154 | full_action_abstract_mdp |
| corridor_32 | 0.05 | epsilon_homogeneous | 7 | 2 | 16 | 0.2097 | 9.875230869868249e-13 | 0.95 | 2.773 | 0.002019 | full_action_abstract_mdp |
| corridor_32 | 0.05 | exact_model_minimization | 2 | 32 | 1 | 0.0 | 9.875230869868249e-13 | 0.0 | 0.06062 | 0.04912 | full_action_abstract_mdp |
| corridor_32 | 0.05 | policy_kron_oracle | 12 | 12 | 2.667 | 9.868523292439233e-13 | 0.0 | nan | 0.007309 | 0.7076 | fixed_optimal_policy_only |
| corridor_32 | 0.05 | policy_kron_oracle | 2 | 2 | 16 | 9.873553975510994e-13 | 0.0 | nan | 0.006395 | 0.8604 | fixed_optimal_policy_only |
| corridor_32 | 0.05 | policy_kron_oracle | 4 | 4 | 8 | 9.871877081153741e-13 | 0.0 | nan | 0.007885 | 0.7341 | fixed_optimal_policy_only |
| corridor_32 | 0.05 | policy_kron_oracle | 7 | 7 | 4.571 | 9.870200186796486e-13 | 0.0 | nan | 0.007949 | 0.7303 | fixed_optimal_policy_only |
| corridor_32 | 0.05 | qstar_oracle_aggregation | 12 | 12 | 2.667 | 0.02076 | 9.875230869868249e-13 | 0.95 | 0.01031 | 0.4327 | full_action_abstract_mdp |
| corridor_32 | 0.05 | qstar_oracle_aggregation | 2 | 2 | 16 | 0.2097 | 9.875230869868249e-13 | 0.95 | 0.01263 | 0.4666 | full_action_abstract_mdp |
| corridor_32 | 0.05 | qstar_oracle_aggregation | 4 | 4 | 8 | 0.08344 | 9.875230869868249e-13 | 0.95 | 0.01161 | 0.5514 | full_action_abstract_mdp |
| corridor_32 | 0.05 | qstar_oracle_aggregation | 7 | 7 | 4.571 | 0.04064 | 9.875230869868249e-13 | 0.95 | 0.01046 | 0.5695 | full_action_abstract_mdp |
| corridor_32 | 0.1 | epsilon_homogeneous | 12 | 2 | 16 | 0.2207 | 3.309552744645334e-12 | 0.9 | 2.776 | 0.00133 | full_action_abstract_mdp |
| corridor_32 | 0.1 | epsilon_homogeneous | 2 | 2 | 16 | 0.2207 | 3.309552744645334e-12 | 0.9 | 2.748 | 0.002448 | full_action_abstract_mdp |
| corridor_32 | 0.1 | epsilon_homogeneous | 4 | 2 | 16 | 0.2207 | 3.309552744645334e-12 | 0.9 | 2.713 | 0.001312 | full_action_abstract_mdp |
| corridor_32 | 0.1 | epsilon_homogeneous | 7 | 2 | 16 | 0.2207 | 3.309552744645334e-12 | 0.9 | 2.766 | 0.00136 | full_action_abstract_mdp |
| corridor_32 | 0.1 | exact_model_minimization | 2 | 32 | 1 | 3.220662460729208e-16 | 3.309552744645334e-12 | 0.0 | 0.06108 | 0.06336 | full_action_abstract_mdp |
| corridor_32 | 0.1 | policy_kron_oracle | 12 | 12 | 2.667 | 3.308747579030152e-12 | 0.0 | nan | 0.005428 | 0.6424 | fixed_optimal_policy_only |
| corridor_32 | 0.1 | policy_kron_oracle | 2 | 2 | 16 | 3.3097137777683706e-12 | 0.0 | nan | 0.004304 | 0.8306 | fixed_optimal_policy_only |
| corridor_32 | 0.1 | policy_kron_oracle | 4 | 4 | 8 | 3.3097137777683706e-12 | 0.0 | nan | 0.005703 | 0.6614 | fixed_optimal_policy_only |
| corridor_32 | 0.1 | policy_kron_oracle | 7 | 7 | 4.571 | 3.3097137777683706e-12 | 0.0 | nan | 0.005355 | 0.6675 | fixed_optimal_policy_only |
| corridor_32 | 0.1 | qstar_oracle_aggregation | 12 | 12 | 2.667 | 0.02194 | 3.309552744645334e-12 | 0.9 | 0.007844 | 0.4492 | full_action_abstract_mdp |
| corridor_32 | 0.1 | qstar_oracle_aggregation | 2 | 2 | 16 | 0.2207 | 3.309552744645334e-12 | 0.9 | 0.0105 | 0.3457 | full_action_abstract_mdp |
| corridor_32 | 0.1 | qstar_oracle_aggregation | 4 | 4 | 8 | 0.08904 | 3.309552744645334e-12 | 0.9 | 0.009012 | 0.3961 | full_action_abstract_mdp |
| corridor_32 | 0.1 | qstar_oracle_aggregation | 7 | 7 | 4.571 | 0.0435 | 3.309552744645334e-12 | 0.9 | 0.008102 | 0.4379 | full_action_abstract_mdp |
| corridor_64 | 0.0 | epsilon_homogeneous | 13 | 2 | 32 | 0.2255 | 0.0 | 1 | 16.82 | 0.000206 | full_action_abstract_mdp |
| corridor_64 | 0.0 | epsilon_homogeneous | 23 | 2 | 32 | 0.2255 | 0.0 | 1 | 17.03 | 0.0002031 | full_action_abstract_mdp |
| corridor_64 | 0.0 | epsilon_homogeneous | 4 | 2 | 32 | 0.2255 | 0.0 | 1 | 17.06 | 0.0001939 | full_action_abstract_mdp |
| corridor_64 | 0.0 | epsilon_homogeneous | 7 | 2 | 32 | 0.2255 | 0.0 | 1 | 17.07 | 0.000203 | full_action_abstract_mdp |
| corridor_64 | 0.0 | exact_model_minimization | 4 | 64 | 1 | 0.0 | 0.0 | 0.0 | 0.387 | 0.00884 | full_action_abstract_mdp |
| corridor_64 | 0.0 | policy_kron_oracle | 13 | 13 | 4.923 | 3.747429732277204e-16 | 0.0 | nan | 0.008091 | 0.4104 | fixed_optimal_policy_only |
| corridor_64 | 0.0 | policy_kron_oracle | 23 | 23 | 2.783 | 3.747429732277204e-16 | 0.0 | nan | 0.0107 | 0.3113 | fixed_optimal_policy_only |
| corridor_64 | 0.0 | policy_kron_oracle | 4 | 4 | 16 | 3.747429732277204e-16 | 0.0 | nan | 0.007193 | 0.4603 | fixed_optimal_policy_only |
| corridor_64 | 0.0 | policy_kron_oracle | 7 | 7 | 9.143 | 2.498286488184803e-16 | 0.0 | nan | 0.007319 | 0.456 | fixed_optimal_policy_only |
| corridor_64 | 0.0 | qstar_oracle_aggregation | 13 | 13 | 4.923 | 0.02437 | 0.0 | 1 | 0.009635 | 0.3567 | full_action_abstract_mdp |
| corridor_64 | 0.0 | qstar_oracle_aggregation | 23 | 23 | 2.783 | 0.01358 | 0.0 | 1 | 0.0102 | 0.3273 | full_action_abstract_mdp |
| corridor_64 | 0.0 | qstar_oracle_aggregation | 4 | 4 | 16 | 0.09787 | 0.0 | 1 | 0.01109 | 0.3214 | full_action_abstract_mdp |
| corridor_64 | 0.0 | qstar_oracle_aggregation | 7 | 7 | 9.143 | 0.04803 | 0.0 | 1 | 0.01002 | 0.3342 | full_action_abstract_mdp |
| corridor_64 | 0.05 | epsilon_homogeneous | 13 | 2 | 32 | 0.2287 | 1.1618964075164356e-12 | 0.95 | 16.96 | 0.0002977 | full_action_abstract_mdp |
| corridor_64 | 0.05 | epsilon_homogeneous | 23 | 2 | 32 | 0.2287 | 1.1618964075164356e-12 | 0.95 | 17.07 | 0.000295 | full_action_abstract_mdp |
| corridor_64 | 0.05 | epsilon_homogeneous | 4 | 2 | 32 | 0.2287 | 1.1618964075164356e-12 | 0.95 | 17.04 | 0.0002868 | full_action_abstract_mdp |
| corridor_64 | 0.05 | epsilon_homogeneous | 7 | 2 | 32 | 0.2287 | 1.1618964075164356e-12 | 0.95 | 17.21 | 0.0002913 | full_action_abstract_mdp |
| corridor_64 | 0.05 | exact_model_minimization | 4 | 64 | 1 | 2.4458402431668995e-16 | 1.1618964075164356e-12 | 0.0 | 0.3842 | 0.01296 | full_action_abstract_mdp |
| corridor_64 | 0.05 | policy_kron_oracle | 13 | 13 | 4.923 | 1.1616518234921189e-12 | 0.0 | nan | 0.0099 | 0.4982 | fixed_optimal_policy_only |
| corridor_64 | 0.05 | policy_kron_oracle | 23 | 23 | 2.783 | 1.1610403634313273e-12 | 0.0 | nan | 0.01263 | 0.3865 | fixed_optimal_policy_only |
| corridor_64 | 0.05 | policy_kron_oracle | 4 | 4 | 16 | 1.162018699528594e-12 | 0.0 | nan | 0.009753 | 0.5012 | fixed_optimal_policy_only |
| corridor_64 | 0.05 | policy_kron_oracle | 7 | 7 | 9.143 | 1.1615295314799606e-12 | 0.0 | nan | 0.01015 | 0.4801 | fixed_optimal_policy_only |
| corridor_64 | 0.05 | qstar_oracle_aggregation | 13 | 13 | 4.923 | 0.02643 | 1.1618964075164356e-12 | 0.95 | 0.01212 | 0.4027 | full_action_abstract_mdp |
| corridor_64 | 0.05 | qstar_oracle_aggregation | 23 | 23 | 2.783 | 0.01439 | 1.1618964075164356e-12 | 0.95 | 0.01255 | 0.3929 | full_action_abstract_mdp |
| corridor_64 | 0.05 | qstar_oracle_aggregation | 4 | 4 | 16 | 0.1008 | 1.1618964075164356e-12 | 0.95 | 0.01288 | 0.3891 | full_action_abstract_mdp |
| corridor_64 | 0.05 | qstar_oracle_aggregation | 7 | 7 | 9.143 | 0.04965 | 1.1618964075164356e-12 | 0.95 | 0.01198 | 0.411 | full_action_abstract_mdp |
| corridor_64 | 0.1 | epsilon_homogeneous | 13 | 2 | 32 | 0.2312 | 2.207366878286206e-12 | 0.9 | 16.85 | 0.0003402 | full_action_abstract_mdp |
| corridor_64 | 0.1 | epsilon_homogeneous | 23 | 2 | 32 | 0.2312 | 2.207366878286206e-12 | 0.9 | 16.88 | 0.0003405 | full_action_abstract_mdp |
| corridor_64 | 0.1 | epsilon_homogeneous | 4 | 2 | 32 | 0.2312 | 2.207366878286206e-12 | 0.9 | 17.23 | 0.0003358 | full_action_abstract_mdp |
| corridor_64 | 0.1 | epsilon_homogeneous | 7 | 2 | 32 | 0.2312 | 2.207366878286206e-12 | 0.9 | 17.12 | 0.0003635 | full_action_abstract_mdp |
| corridor_64 | 0.1 | exact_model_minimization | 4 | 64 | 1 | 0.0 | 2.207366878286206e-12 | 0.0 | 0.3878 | 0.01468 | full_action_abstract_mdp |
| corridor_64 | 0.1 | policy_kron_oracle | 13 | 13 | 4.923 | 2.207366878286206e-12 | 0.0 | nan | 0.0119 | 0.5082 | fixed_optimal_policy_only |
| corridor_64 | 0.1 | policy_kron_oracle | 23 | 23 | 2.783 | 2.2061689801593887e-12 | 0.0 | nan | 0.01467 | 0.4175 | fixed_optimal_policy_only |
| corridor_64 | 0.1 | policy_kron_oracle | 4 | 4 | 16 | 2.2077262477242514e-12 | 0.0 | nan | 0.01084 | 0.5253 | fixed_optimal_policy_only |
| corridor_64 | 0.1 | policy_kron_oracle | 7 | 7 | 9.143 | 2.2079658273496146e-12 | 0.0 | nan | 0.009906 | 0.6002 | fixed_optimal_policy_only |
| corridor_64 | 0.1 | qstar_oracle_aggregation | 13 | 13 | 4.923 | 0.02535 | 2.207366878286206e-12 | 0.9 | 0.01277 | 0.452 | full_action_abstract_mdp |
| corridor_64 | 0.1 | qstar_oracle_aggregation | 23 | 23 | 2.783 | 0.01513 | 2.207366878286206e-12 | 0.9 | 0.01389 | 0.4009 | full_action_abstract_mdp |
| corridor_64 | 0.1 | qstar_oracle_aggregation | 4 | 4 | 16 | 0.1014 | 2.207366878286206e-12 | 0.9 | 0.01384 | 0.4164 | full_action_abstract_mdp |
| corridor_64 | 0.1 | qstar_oracle_aggregation | 7 | 7 | 9.143 | 0.05007 | 2.207366878286206e-12 | 0.9 | 0.01312 | 0.4341 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | epsilon_homogeneous | 11 | 2 | 52 | 0.6683 | 1.192 | 1 | 11.91 | 0.0001087 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | epsilon_homogeneous | 21 | 2 | 52 | 0.6683 | 1.192 | 1 | 11.71 | 0.0001122 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | epsilon_homogeneous | 37 | 2 | 52 | 0.6683 | 1.192 | 1 | 11.76 | 0.0001212 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | epsilon_homogeneous | 6 | 2 | 52 | 0.6683 | 1.192 | 1 | 11.97 | 9.988e-05 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | exact_model_minimization | 6 | 104 | 1 | 0.0 | 0.0 | 0.0 | 0.2774 | 0.004384 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | policy_kron_oracle | 11 | 11 | 9.455 | 0.0 | 0.0 | nan | 0.009267 | 0.147 | fixed_optimal_policy_only |
| four_rooms_11 | 0.0 | policy_kron_oracle | 21 | 21 | 4.952 | 1.1681289864726658e-16 | 0.0 | nan | 0.01425 | 0.08626 | fixed_optimal_policy_only |
| four_rooms_11 | 0.0 | policy_kron_oracle | 37 | 37 | 2.811 | 1.1681289864726658e-16 | 0.0 | nan | 0.0267 | 0.04509 | fixed_optimal_policy_only |
| four_rooms_11 | 0.0 | policy_kron_oracle | 6 | 6 | 17.33 | 0.0 | 0.0 | nan | 0.007721 | 0.145 | fixed_optimal_policy_only |
| four_rooms_11 | 0.0 | qstar_oracle_aggregation | 11 | 11 | 9.455 | 0.6497 | 1.192 | 1 | 0.008743 | 0.1463 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | qstar_oracle_aggregation | 21 | 21 | 4.952 | 0.2626 | 1.192 | 1 | 0.007515 | 0.1595 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | qstar_oracle_aggregation | 37 | 37 | 2.811 | 0.101 | 1.192 | 1 | 0.008697 | 0.1376 | full_action_abstract_mdp |
| four_rooms_11 | 0.0 | qstar_oracle_aggregation | 6 | 6 | 17.33 | 0.7125 | 1.192 | 1 | 0.009603 | 0.1385 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | epsilon_homogeneous | 11 | 2 | 52 | 0.6024 | 1.089 | 0.95 | 12.02 | 0.0002159 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | epsilon_homogeneous | 21 | 2 | 52 | 0.6024 | 1.089 | 0.95 | 11.92 | 0.0002167 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | epsilon_homogeneous | 37 | 2 | 52 | 0.6024 | 1.089 | 0.95 | 11.83 | 0.000219 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | epsilon_homogeneous | 6 | 2 | 52 | 0.6024 | 1.089 | 0.95 | 12.03 | 0.0002177 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | exact_model_minimization | 6 | 104 | 1 | 0.0 | 2.712336828250836e-12 | 0.0 | 0.2822 | 0.009478 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | policy_kron_oracle | 11 | 11 | 9.455 | 2.712336828250836e-12 | 0.0 | nan | 0.01159 | 0.2183 | fixed_optimal_policy_only |
| four_rooms_11 | 0.05 | policy_kron_oracle | 21 | 21 | 4.952 | 2.712225525496178e-12 | 0.0 | nan | 0.01611 | 0.1742 | fixed_optimal_policy_only |
| four_rooms_11 | 0.05 | policy_kron_oracle | 37 | 37 | 2.811 | 2.712225525496178e-12 | 0.0 | nan | 0.0287 | 0.09529 | fixed_optimal_policy_only |
| four_rooms_11 | 0.05 | policy_kron_oracle | 6 | 6 | 17.33 | 2.712336828250836e-12 | 0.0 | nan | 0.009966 | 0.2512 | fixed_optimal_policy_only |
| four_rooms_11 | 0.05 | qstar_oracle_aggregation | 11 | 11 | 9.455 | 0.6247 | 1.089 | 0.9833 | 0.01051 | 0.2505 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | qstar_oracle_aggregation | 21 | 21 | 4.952 | 0.2684 | 1.073 | 0.9833 | 0.008296 | 0.2983 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | qstar_oracle_aggregation | 37 | 37 | 2.811 | 0.1038 | 1.083 | 0.9833 | 0.01019 | 0.2445 | full_action_abstract_mdp |
| four_rooms_11 | 0.05 | qstar_oracle_aggregation | 6 | 6 | 17.33 | 0.7433 | 1.089 | 0.9667 | 0.01087 | 0.2358 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | epsilon_homogeneous | 11 | 2 | 52 | 0.5352 | 0.9849 | 0.9 | 11.91 | 0.000265 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | epsilon_homogeneous | 21 | 2 | 52 | 0.5352 | 0.9849 | 0.9 | 11.89 | 0.0002733 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | epsilon_homogeneous | 37 | 2 | 52 | 0.5352 | 0.9849 | 0.9 | 11.83 | 0.0002678 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | epsilon_homogeneous | 6 | 2 | 52 | 0.5352 | 0.9849 | 0.9 | 11.84 | 0.0002632 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | exact_model_minimization | 6 | 104 | 1 | 0.0 | 4.1327816553320315e-12 | 0.0 | 0.2852 | 0.01078 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | policy_kron_oracle | 11 | 11 | 9.455 | 4.132146981927066e-12 | 0.0 | nan | 0.01167 | 0.262 | fixed_optimal_policy_only |
| four_rooms_11 | 0.1 | policy_kron_oracle | 21 | 21 | 4.952 | 4.132146981927066e-12 | 0.0 | nan | 0.01688 | 0.1849 | fixed_optimal_policy_only |
| four_rooms_11 | 0.1 | policy_kron_oracle | 37 | 37 | 2.811 | 4.131935424125411e-12 | 0.0 | nan | 0.02868 | 0.1074 | fixed_optimal_policy_only |
| four_rooms_11 | 0.1 | policy_kron_oracle | 6 | 6 | 17.33 | 4.132358539728721e-12 | 0.0 | nan | 0.01085 | 0.2938 | fixed_optimal_policy_only |
| four_rooms_11 | 0.1 | qstar_oracle_aggregation | 11 | 11 | 9.455 | 0.5929 | 0.9655 | 0.9667 | 0.011 | 0.2653 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | qstar_oracle_aggregation | 21 | 21 | 4.952 | 0.2424 | 0.9825 | 0.9667 | 0.009878 | 0.3297 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | qstar_oracle_aggregation | 37 | 37 | 2.811 | 0.09717 | 0.9384 | 0.9667 | 0.01104 | 0.2801 | full_action_abstract_mdp |
| four_rooms_11 | 0.1 | qstar_oracle_aggregation | 6 | 6 | 17.33 | 0.6836 | 0.936 | 0.9333 | 0.01178 | 0.2736 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | epsilon_homogeneous | 14 | 2 | 34 | 0.7485 | 1.592 | 1 | 4.497 | 0.0002449 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | epsilon_homogeneous | 24 | 2 | 34 | 0.7485 | 1.592 | 1 | 4.474 | 0.0002459 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | epsilon_homogeneous | 4 | 2 | 34 | 0.7485 | 1.592 | 1 | 4.463 | 0.0002218 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | epsilon_homogeneous | 7 | 2 | 34 | 0.7485 | 1.592 | 1 | 4.473 | 0.0002409 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | exact_model_minimization | 4 | 68 | 1 | 0.0 | 0.0 | 0.0 | 0.1066 | 0.01082 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | policy_kron_oracle | 14 | 14 | 4.857 | 1.3814960442367423e-16 | 0.0 | nan | 0.00601 | 0.1647 | fixed_optimal_policy_only |
| four_rooms_9 | 0.0 | policy_kron_oracle | 24 | 24 | 2.833 | 0.0 | 0.0 | nan | 0.009112 | 0.1151 | fixed_optimal_policy_only |
| four_rooms_9 | 0.0 | policy_kron_oracle | 4 | 4 | 17 | 0.0 | 0.0 | nan | 0.004388 | 0.2424 | fixed_optimal_policy_only |
| four_rooms_9 | 0.0 | policy_kron_oracle | 7 | 7 | 9.714 | 0.0 | 0.0 | nan | 0.004678 | 0.2393 | fixed_optimal_policy_only |
| four_rooms_9 | 0.0 | qstar_oracle_aggregation | 14 | 14 | 4.857 | 0.2785 | 1.592 | 1 | 0.005274 | 0.1868 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | qstar_oracle_aggregation | 24 | 24 | 2.833 | 0.1406 | 1.592 | 1 | 0.006455 | 0.1558 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | qstar_oracle_aggregation | 4 | 4 | 17 | 0.9903 | 1.592 | 1 | 0.01078 | 0.1169 | full_action_abstract_mdp |
| four_rooms_9 | 0.0 | qstar_oracle_aggregation | 7 | 7 | 9.714 | 0.6574 | 1.592 | 1 | 0.007588 | 0.1437 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | epsilon_homogeneous | 14 | 2 | 34 | 0.6787 | 1.462 | 0.95 | 4.494 | 0.0005069 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | epsilon_homogeneous | 24 | 2 | 34 | 0.6787 | 1.462 | 0.95 | 4.447 | 0.0005192 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | epsilon_homogeneous | 4 | 2 | 34 | 0.6787 | 1.462 | 0.95 | 4.477 | 0.0005169 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | epsilon_homogeneous | 7 | 2 | 34 | 0.6787 | 1.462 | 0.95 | 4.45 | 0.0005083 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | exact_model_minimization | 4 | 68 | 1 | 0.0 | 1.924286338474306e-12 | 0.0 | 0.1062 | 0.02026 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | policy_kron_oracle | 14 | 14 | 4.857 | 1.9244175278892552e-12 | 0.0 | nan | 0.007618 | 0.2856 | fixed_optimal_policy_only |
| four_rooms_9 | 0.05 | policy_kron_oracle | 24 | 24 | 2.833 | 1.9244175278892552e-12 | 0.0 | nan | 0.01084 | 0.2027 | fixed_optimal_policy_only |
| four_rooms_9 | 0.05 | policy_kron_oracle | 4 | 4 | 17 | 1.9244175278892552e-12 | 0.0 | nan | 0.006032 | 0.3593 | fixed_optimal_policy_only |
| four_rooms_9 | 0.05 | policy_kron_oracle | 7 | 7 | 9.714 | 1.9248110961341027e-12 | 0.0 | nan | 0.006249 | 0.3529 | fixed_optimal_policy_only |
| four_rooms_9 | 0.05 | qstar_oracle_aggregation | 14 | 14 | 4.857 | 0.2458 | 1.461 | 0.9833 | 0.007811 | 0.3115 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | qstar_oracle_aggregation | 24 | 24 | 2.833 | 0.1146 | 1.409 | 0.9667 | 0.007134 | 0.3077 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | qstar_oracle_aggregation | 4 | 4 | 17 | 0.9186 | 1.462 | 0.9667 | 0.01107 | 0.21 | full_action_abstract_mdp |
| four_rooms_9 | 0.05 | qstar_oracle_aggregation | 7 | 7 | 9.714 | 0.6256 | 1.443 | 0.9667 | 0.009007 | 0.2432 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | epsilon_homogeneous | 14 | 2 | 34 | 0.6071 | 1.331 | 0.9 | 4.514 | 0.000644 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | epsilon_homogeneous | 24 | 2 | 34 | 0.6071 | 1.331 | 0.9 | 4.482 | 0.0006433 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | epsilon_homogeneous | 4 | 2 | 34 | 0.6071 | 1.331 | 0.9 | 4.467 | 0.0006066 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | epsilon_homogeneous | 7 | 2 | 34 | 0.6071 | 1.331 | 0.9 | 4.501 | 0.0006398 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | exact_model_minimization | 4 | 68 | 1 | 0.0 | 3.742875271673913e-12 | 0.0 | 0.1065 | 0.02547 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | policy_kron_oracle | 14 | 14 | 4.857 | 3.743123711836647e-12 | 0.0 | nan | 0.008248 | 0.3277 | fixed_optimal_policy_only |
| four_rooms_9 | 0.1 | policy_kron_oracle | 24 | 24 | 2.833 | 3.7425026114298114e-12 | 0.0 | nan | 0.01133 | 0.2389 | fixed_optimal_policy_only |
| four_rooms_9 | 0.1 | policy_kron_oracle | 4 | 4 | 17 | 3.742626831511179e-12 | 0.0 | nan | 0.006671 | 0.4253 | fixed_optimal_policy_only |
| four_rooms_9 | 0.1 | policy_kron_oracle | 7 | 7 | 9.714 | 3.74299949175528e-12 | 0.0 | nan | 0.006678 | 0.4115 | fixed_optimal_policy_only |
| four_rooms_9 | 0.1 | qstar_oracle_aggregation | 14 | 14 | 4.857 | 0.3008 | 1.303 | 0.9333 | 0.008215 | 0.3328 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | qstar_oracle_aggregation | 24 | 24 | 2.833 | 0.1477 | 0.8058 | 0.9667 | 0.008315 | 0.3212 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | qstar_oracle_aggregation | 4 | 4 | 17 | 0.8438 | 1.331 | 0.9333 | 0.01168 | 0.2424 | full_action_abstract_mdp |
| four_rooms_9 | 0.1 | qstar_oracle_aggregation | 7 | 7 | 9.714 | 0.6091 | 1.263 | 0.9333 | 0.009959 | 0.2779 | full_action_abstract_mdp |
| maze_11 | 0.0 | epsilon_homogeneous | 10 | 2 | 24.5 | 0.04044 | 0.6059 | 1 | 5.68 | 0.0003241 | full_action_abstract_mdp |
| maze_11 | 0.0 | epsilon_homogeneous | 18 | 2 | 24.5 | 0.04044 | 0.6059 | 1 | 5.755 | 0.0003155 | full_action_abstract_mdp |
| maze_11 | 0.0 | epsilon_homogeneous | 3 | 2 | 24.5 | 0.04044 | 0.6059 | 1 | 5.761 | 0.0003063 | full_action_abstract_mdp |
| maze_11 | 0.0 | epsilon_homogeneous | 5 | 2 | 24.5 | 0.04044 | 0.6059 | 1 | 5.798 | 0.0003048 | full_action_abstract_mdp |
| maze_11 | 0.0 | exact_model_minimization | 3 | 49 | 1 | 0.0 | 0.0 | 0.0 | 0.1271 | 0.01383 | full_action_abstract_mdp |
| maze_11 | 0.0 | policy_kron_oracle | 10 | 10 | 4.9 | 0.0 | 0.0 | nan | 0.004293 | 0.4114 | fixed_optimal_policy_only |
| maze_11 | 0.0 | policy_kron_oracle | 18 | 18 | 2.722 | 1.7116220133971358e-16 | 0.0 | nan | 0.005614 | 0.3046 | fixed_optimal_policy_only |
| maze_11 | 0.0 | policy_kron_oracle | 3 | 3 | 16.33 | 0.0 | 0.0 | nan | 0.003683 | 0.4747 | fixed_optimal_policy_only |
| maze_11 | 0.0 | policy_kron_oracle | 5 | 5 | 9.8 | 0.0 | 0.0 | nan | 0.003725 | 0.4607 | fixed_optimal_policy_only |
| maze_11 | 0.0 | qstar_oracle_aggregation | 10 | 10 | 4.9 | 0.2799 | 0.6059 | 1 | 0.008724 | 0.2026 | full_action_abstract_mdp |
| maze_11 | 0.0 | qstar_oracle_aggregation | 18 | 18 | 2.722 | 0.1409 | 0.6059 | 1 | 0.006915 | 0.2555 | full_action_abstract_mdp |
| maze_11 | 0.0 | qstar_oracle_aggregation | 3 | 3 | 16.33 | 0.07621 | 0.6059 | 1 | 0.008367 | 0.2127 | full_action_abstract_mdp |
| maze_11 | 0.0 | qstar_oracle_aggregation | 5 | 5 | 9.8 | 0.2406 | 0.6059 | 1 | 0.0102 | 0.1832 | full_action_abstract_mdp |
| maze_11 | 0.05 | epsilon_homogeneous | 10 | 2 | 24.5 | 0.05848 | 0.544 | 0.95 | 5.728 | 0.0005384 | full_action_abstract_mdp |
| maze_11 | 0.05 | epsilon_homogeneous | 18 | 2 | 24.5 | 0.05848 | 0.544 | 0.95 | 5.688 | 0.0005276 | full_action_abstract_mdp |
| maze_11 | 0.05 | epsilon_homogeneous | 3 | 2 | 24.5 | 0.05848 | 0.544 | 0.95 | 5.786 | 0.000513 | full_action_abstract_mdp |
| maze_11 | 0.05 | epsilon_homogeneous | 5 | 2 | 24.5 | 0.05848 | 0.544 | 0.95 | 5.892 | 0.0005244 | full_action_abstract_mdp |
| maze_11 | 0.05 | exact_model_minimization | 3 | 49 | 1 | 1.6456385767480226e-16 | 2.1914968926553417e-12 | 0.0 | 0.1301 | 0.02318 | full_action_abstract_mdp |
| maze_11 | 0.05 | policy_kron_oracle | 10 | 10 | 4.9 | 2.1916614565130166e-12 | 0.0 | nan | 0.0056 | 0.509 | fixed_optimal_policy_only |
| maze_11 | 0.05 | policy_kron_oracle | 18 | 18 | 2.722 | 2.191167764939992e-12 | 0.0 | nan | 0.006894 | 0.4148 | fixed_optimal_policy_only |
| maze_11 | 0.05 | policy_kron_oracle | 3 | 3 | 16.33 | 2.191332328797667e-12 | 0.0 | nan | 0.005298 | 0.5643 | fixed_optimal_policy_only |
| maze_11 | 0.05 | policy_kron_oracle | 5 | 5 | 9.8 | 2.191332328797667e-12 | 0.0 | nan | 0.005598 | 0.5495 | fixed_optimal_policy_only |
| maze_11 | 0.05 | qstar_oracle_aggregation | 10 | 10 | 4.9 | 0.2564 | 0.544 | 0.9667 | 0.01024 | 0.289 | full_action_abstract_mdp |
| maze_11 | 0.05 | qstar_oracle_aggregation | 18 | 18 | 2.722 | 0.1615 | 0.544 | 0.95 | 0.008534 | 0.3476 | full_action_abstract_mdp |
| maze_11 | 0.05 | qstar_oracle_aggregation | 3 | 3 | 16.33 | 0.07736 | 0.544 | 0.9667 | 0.0113 | 0.2607 | full_action_abstract_mdp |
| maze_11 | 0.05 | qstar_oracle_aggregation | 5 | 5 | 9.8 | 0.2134 | 0.544 | 0.95 | 0.01131 | 0.2611 | full_action_abstract_mdp |
| maze_11 | 0.1 | epsilon_homogeneous | 10 | 2 | 24.5 | 0.07676 | 0.483 | 0.9 | 5.782 | 0.000647 | full_action_abstract_mdp |
| maze_11 | 0.1 | epsilon_homogeneous | 18 | 2 | 24.5 | 0.07676 | 0.483 | 0.9 | 5.78 | 0.0006411 | full_action_abstract_mdp |
| maze_11 | 0.1 | epsilon_homogeneous | 3 | 2 | 24.5 | 0.07676 | 0.483 | 0.9 | 5.691 | 0.0006164 | full_action_abstract_mdp |
| maze_11 | 0.1 | epsilon_homogeneous | 5 | 2 | 24.5 | 0.07676 | 0.483 | 0.9 | 5.795 | 0.0006401 | full_action_abstract_mdp |
| maze_11 | 0.1 | exact_model_minimization | 3 | 49 | 1 | 3.1611210416992603e-16 | 1.7422518621325475e-12 | 0.0 | 0.129 | 0.02715 | full_action_abstract_mdp |
| maze_11 | 0.1 | policy_kron_oracle | 10 | 10 | 4.9 | 1.7420938060804624e-12 | 0.0 | nan | 0.006942 | 0.5647 | fixed_optimal_policy_only |
| maze_11 | 0.1 | policy_kron_oracle | 18 | 18 | 2.722 | 1.7411454697679527e-12 | 0.0 | nan | 0.007749 | 0.4642 | fixed_optimal_policy_only |
| maze_11 | 0.1 | policy_kron_oracle | 3 | 3 | 16.33 | 1.7424099181846323e-12 | 0.0 | nan | 0.006195 | 0.6096 | fixed_optimal_policy_only |
| maze_11 | 0.1 | policy_kron_oracle | 5 | 5 | 9.8 | 1.7424099181846323e-12 | 0.0 | nan | 0.00593 | 0.6108 | fixed_optimal_policy_only |
| maze_11 | 0.1 | qstar_oracle_aggregation | 10 | 10 | 4.9 | 0.1294 | 0.483 | 0.9333 | 0.009691 | 0.3804 | full_action_abstract_mdp |
| maze_11 | 0.1 | qstar_oracle_aggregation | 18 | 18 | 2.722 | 0.1602 | 0.4826 | 0.9 | 0.009212 | 0.389 | full_action_abstract_mdp |
| maze_11 | 0.1 | qstar_oracle_aggregation | 3 | 3 | 16.33 | 0.05268 | 0.483 | 0.9333 | 0.01225 | 0.2974 | full_action_abstract_mdp |
| maze_11 | 0.1 | qstar_oracle_aggregation | 5 | 5 | 9.8 | 0.1067 | 0.483 | 0.9333 | 0.01008 | 0.3461 | full_action_abstract_mdp |
| maze_9 | 0.0 | epsilon_homogeneous | 11 | 2 | 15.5 | 0.572 | 2.266 | 1 | 1.022 | 0.000853 | full_action_abstract_mdp |
| maze_9 | 0.0 | epsilon_homogeneous | 2 | 2 | 15.5 | 0.572 | 2.266 | 1 | 1.01 | 0.0007549 | full_action_abstract_mdp |
| maze_9 | 0.0 | epsilon_homogeneous | 4 | 2 | 15.5 | 0.572 | 2.266 | 1 | 1.018 | 0.0008159 | full_action_abstract_mdp |
| maze_9 | 0.0 | epsilon_homogeneous | 7 | 2 | 15.5 | 0.572 | 2.266 | 1 | 1.017 | 0.0008333 | full_action_abstract_mdp |
| maze_9 | 0.0 | exact_model_minimization | 2 | 31 | 1 | 0.0 | 0.0 | 0.0 | 0.0231 | 0.03285 | full_action_abstract_mdp |
| maze_9 | 0.0 | policy_kron_oracle | 11 | 11 | 2.818 | 0.0 | 0.0 | nan | 0.002294 | 0.3254 | fixed_optimal_policy_only |
| maze_9 | 0.0 | policy_kron_oracle | 2 | 2 | 15.5 | 0.0 | 0.0 | nan | 0.001306 | 0.5751 | fixed_optimal_policy_only |
| maze_9 | 0.0 | policy_kron_oracle | 4 | 4 | 7.75 | 0.0 | 0.0 | nan | 0.001943 | 0.3917 | fixed_optimal_policy_only |
| maze_9 | 0.0 | policy_kron_oracle | 7 | 7 | 4.429 | 1.7406296101340607e-16 | 0.0 | nan | 0.002014 | 0.3736 | fixed_optimal_policy_only |
| maze_9 | 0.0 | qstar_oracle_aggregation | 11 | 11 | 2.818 | 0.301 | 0.0 | 1 | 0.003779 | 0.2063 | full_action_abstract_mdp |
| maze_9 | 0.0 | qstar_oracle_aggregation | 2 | 2 | 15.5 | 0.572 | 2.266 | 1 | 0.006894 | 0.1158 | full_action_abstract_mdp |
| maze_9 | 0.0 | qstar_oracle_aggregation | 4 | 4 | 7.75 | 0.3947 | 2.266 | 1 | 0.004576 | 0.1691 | full_action_abstract_mdp |
| maze_9 | 0.0 | qstar_oracle_aggregation | 7 | 7 | 4.429 | 0.422 | 2.266 | 1 | 0.003964 | 0.1916 | full_action_abstract_mdp |
| maze_9 | 0.05 | epsilon_homogeneous | 11 | 2 | 15.5 | 0.5134 | 2.088 | 0.95 | 1.019 | 0.00171 | full_action_abstract_mdp |
| maze_9 | 0.05 | epsilon_homogeneous | 2 | 2 | 15.5 | 0.5134 | 2.088 | 0.95 | 1.045 | 0.001693 | full_action_abstract_mdp |
| maze_9 | 0.05 | epsilon_homogeneous | 4 | 2 | 15.5 | 0.5134 | 2.088 | 0.95 | 1.027 | 0.001659 | full_action_abstract_mdp |
| maze_9 | 0.05 | epsilon_homogeneous | 7 | 2 | 15.5 | 0.5134 | 2.088 | 0.95 | 1.031 | 0.001701 | full_action_abstract_mdp |
| maze_9 | 0.05 | exact_model_minimization | 2 | 31 | 1 | 0.0 | 1.8417671187447517e-12 | 0.0 | 0.02453 | 0.06884 | full_action_abstract_mdp |
| maze_9 | 0.05 | policy_kron_oracle | 11 | 11 | 2.818 | 1.841602439996652e-12 | 0.0 | nan | 0.003409 | 0.5002 | fixed_optimal_policy_only |
| maze_9 | 0.05 | policy_kron_oracle | 2 | 2 | 15.5 | 1.8417671187447517e-12 | 0.0 | nan | 0.002283 | 0.7442 | fixed_optimal_policy_only |
| maze_9 | 0.05 | policy_kron_oracle | 4 | 4 | 7.75 | 1.8414377612485527e-12 | 0.0 | nan | 0.003061 | 0.5641 | fixed_optimal_policy_only |
| maze_9 | 0.05 | policy_kron_oracle | 7 | 7 | 4.429 | 1.841931797492851e-12 | 0.0 | nan | 0.003172 | 0.5358 | fixed_optimal_policy_only |
| maze_9 | 0.05 | qstar_oracle_aggregation | 11 | 11 | 2.818 | 0.3223 | 0.0004031 | 0.95 | 0.005692 | 0.3539 | full_action_abstract_mdp |
| maze_9 | 0.05 | qstar_oracle_aggregation | 2 | 2 | 15.5 | 0.5134 | 2.088 | 0.95 | 0.008099 | 0.2115 | full_action_abstract_mdp |
| maze_9 | 0.05 | qstar_oracle_aggregation | 4 | 4 | 7.75 | 0.3688 | 2.082 | 0.95 | 0.006399 | 0.2961 | full_action_abstract_mdp |
| maze_9 | 0.05 | qstar_oracle_aggregation | 7 | 7 | 4.429 | 0.408 | 1.881 | 0.95 | 0.004883 | 0.3401 | full_action_abstract_mdp |
| maze_9 | 0.1 | epsilon_homogeneous | 11 | 2 | 15.5 | 0.453 | 1.898 | 0.9 | 1.021 | 0.002166 | full_action_abstract_mdp |
| maze_9 | 0.1 | epsilon_homogeneous | 2 | 2 | 15.5 | 0.453 | 1.898 | 0.9 | 1.018 | 0.002087 | full_action_abstract_mdp |
| maze_9 | 0.1 | epsilon_homogeneous | 4 | 2 | 15.5 | 0.453 | 1.898 | 0.9 | 0.9796 | 0.00219 | full_action_abstract_mdp |
| maze_9 | 0.1 | epsilon_homogeneous | 7 | 2 | 15.5 | 0.453 | 1.898 | 0.9 | 1.021 | 0.00218 | full_action_abstract_mdp |
| maze_9 | 0.1 | exact_model_minimization | 2 | 31 | 1 | 0.0 | 2.586746487722213e-12 | 0.0 | 0.02486 | 0.0859 | full_action_abstract_mdp |
| maze_9 | 0.1 | policy_kron_oracle | 11 | 11 | 2.818 | 2.58628051921836e-12 | 0.0 | nan | 0.003792 | 0.5597 | fixed_optimal_policy_only |
| maze_9 | 0.1 | policy_kron_oracle | 2 | 2 | 15.5 | 2.586746487722213e-12 | 0.0 | nan | 0.002578 | 0.8019 | fixed_optimal_policy_only |
| maze_9 | 0.1 | policy_kron_oracle | 4 | 4 | 7.75 | 2.586746487722213e-12 | 0.0 | nan | 0.003515 | 0.6045 | fixed_optimal_policy_only |
| maze_9 | 0.1 | policy_kron_oracle | 7 | 7 | 4.429 | 2.586746487722213e-12 | 0.0 | nan | 0.003763 | 0.5996 | fixed_optimal_policy_only |
| maze_9 | 0.1 | qstar_oracle_aggregation | 11 | 11 | 2.818 | 0.3107 | 0.001365 | 0.9 | 0.005434 | 0.3802 | full_action_abstract_mdp |
| maze_9 | 0.1 | qstar_oracle_aggregation | 2 | 2 | 15.5 | 0.453 | 1.898 | 0.9 | 0.008779 | 0.2539 | full_action_abstract_mdp |
| maze_9 | 0.1 | qstar_oracle_aggregation | 4 | 4 | 7.75 | 0.2913 | 1.798 | 0.9 | 0.00605 | 0.3549 | full_action_abstract_mdp |
| maze_9 | 0.1 | qstar_oracle_aggregation | 7 | 7 | 4.429 | 0.392 | 1.399 | 0.9 | 0.00582 | 0.3629 | full_action_abstract_mdp |
| open_room_12 | 0.0 | epsilon_homogeneous | 15 | 2 | 72 | 0.6701 | 1.048 | 1 | 25.28 | 6.176e-05 | full_action_abstract_mdp |
| open_room_12 | 0.0 | epsilon_homogeneous | 29 | 2 | 72 | 0.6701 | 1.048 | 1 | 25.37 | 6.419e-05 | full_action_abstract_mdp |
| open_room_12 | 0.0 | epsilon_homogeneous | 51 | 2 | 72 | 0.6701 | 1.048 | 1 | 25.46 | 6.711e-05 | full_action_abstract_mdp |
| open_room_12 | 0.0 | epsilon_homogeneous | 8 | 2 | 72 | 0.6701 | 1.048 | 1 | 25.32 | 5.764e-05 | full_action_abstract_mdp |
| open_room_12 | 0.0 | exact_model_minimization | 8 | 144 | 1 | 0.0 | 0.0 | 0.0 | 0.5923 | 0.002401 | full_action_abstract_mdp |
| open_room_12 | 0.0 | policy_kron_oracle | 15 | 15 | 9.6 | 0.0 | 0.0 | nan | 0.01784 | 0.08041 | fixed_optimal_policy_only |
| open_room_12 | 0.0 | policy_kron_oracle | 29 | 29 | 4.966 | 0.0 | 0.0 | nan | 0.03132 | 0.04701 | fixed_optimal_policy_only |
| open_room_12 | 0.0 | policy_kron_oracle | 51 | 51 | 2.824 | 2.1825072406138237e-16 | 0.0 | nan | 0.06753 | 0.024 | fixed_optimal_policy_only |
| open_room_12 | 0.0 | policy_kron_oracle | 8 | 8 | 18 | 0.0 | 0.0 | nan | 0.01507 | 0.099 | fixed_optimal_policy_only |
| open_room_12 | 0.0 | qstar_oracle_aggregation | 15 | 15 | 9.6 | 0.06074 | 1.048 | 1 | 0.006004 | 0.2657 | full_action_abstract_mdp |
| open_room_12 | 0.0 | qstar_oracle_aggregation | 29 | 29 | 4.966 | 0.00659 | 1.048 | 1 | 0.00698 | 0.213 | full_action_abstract_mdp |
| open_room_12 | 0.0 | qstar_oracle_aggregation | 51 | 51 | 2.824 | 0.0 | 0.0 | 1 | 0.009293 | 0.1493 | full_action_abstract_mdp |
| open_room_12 | 0.0 | qstar_oracle_aggregation | 8 | 8 | 18 | 0.1055 | 1.048 | 1 | 0.006148 | 0.2728 | full_action_abstract_mdp |
| open_room_12 | 0.05 | epsilon_homogeneous | 15 | 2 | 72 | 0.6124 | 0.9648 | 0.95 | 25.31 | 0.000117 | full_action_abstract_mdp |
| open_room_12 | 0.05 | epsilon_homogeneous | 29 | 2 | 72 | 0.6124 | 0.9648 | 0.95 | 25.2 | 0.0001168 | full_action_abstract_mdp |
| open_room_12 | 0.05 | epsilon_homogeneous | 51 | 2 | 72 | 0.6124 | 0.9648 | 0.95 | 25.2 | 0.0001201 | full_action_abstract_mdp |
| open_room_12 | 0.05 | epsilon_homogeneous | 8 | 2 | 72 | 0.6124 | 0.9648 | 0.95 | 25.31 | 0.0001196 | full_action_abstract_mdp |
| open_room_12 | 0.05 | exact_model_minimization | 8 | 144 | 1 | 0.0 | 1.2876796166290814e-12 | 0.0 | 0.6235 | 0.005071 | full_action_abstract_mdp |
| open_room_12 | 0.05 | policy_kron_oracle | 15 | 15 | 9.6 | 1.2872607909284378e-12 | 0.0 | nan | 0.02065 | 0.1366 | fixed_optimal_policy_only |
| open_room_12 | 0.05 | policy_kron_oracle | 29 | 29 | 4.966 | 1.2874702037787596e-12 | 0.0 | nan | 0.03345 | 0.08518 | fixed_optimal_policy_only |
| open_room_12 | 0.05 | policy_kron_oracle | 51 | 51 | 2.824 | 1.2870513780781158e-12 | 0.0 | nan | 0.06443 | 0.04387 | fixed_optimal_policy_only |
| open_room_12 | 0.05 | policy_kron_oracle | 8 | 8 | 18 | 1.2874702037787596e-12 | 0.0 | nan | 0.01673 | 0.1684 | fixed_optimal_policy_only |
| open_room_12 | 0.05 | qstar_oracle_aggregation | 15 | 15 | 9.6 | 0.07647 | 0.9648 | 0.9833 | 0.007548 | 0.3992 | full_action_abstract_mdp |
| open_room_12 | 0.05 | qstar_oracle_aggregation | 29 | 29 | 4.966 | 0.002832 | 0.08388 | 0.9833 | 0.009905 | 0.295 | full_action_abstract_mdp |
| open_room_12 | 0.05 | qstar_oracle_aggregation | 51 | 51 | 2.824 | 0.004714 | 0.006711 | 0.9667 | 0.01214 | 0.2381 | full_action_abstract_mdp |
| open_room_12 | 0.05 | qstar_oracle_aggregation | 8 | 8 | 18 | 0.1108 | 0.5809 | 0.9667 | 0.008104 | 0.3762 | full_action_abstract_mdp |
| open_room_12 | 0.1 | epsilon_homogeneous | 15 | 2 | 72 | 0.5529 | 0.8805 | 0.9 | 24.99 | 0.0001436 | full_action_abstract_mdp |
| open_room_12 | 0.1 | epsilon_homogeneous | 29 | 2 | 72 | 0.5529 | 0.8805 | 0.9 | 24.9 | 0.0001456 | full_action_abstract_mdp |
| open_room_12 | 0.1 | epsilon_homogeneous | 51 | 2 | 72 | 0.5529 | 0.8805 | 0.9 | 24.3 | 0.0001436 | full_action_abstract_mdp |
| open_room_12 | 0.1 | epsilon_homogeneous | 8 | 2 | 72 | 0.5529 | 0.8805 | 0.9 | 25.09 | 0.0001524 | full_action_abstract_mdp |
| open_room_12 | 0.1 | exact_model_minimization | 8 | 144 | 1 | 0.0 | 4.804665755373555e-12 | 0.0 | 0.6036 | 0.005698 | full_action_abstract_mdp |
| open_room_12 | 0.1 | policy_kron_oracle | 15 | 15 | 9.6 | 4.804064445571456e-12 | 0.0 | nan | 0.02158 | 0.1598 | fixed_optimal_policy_only |
| open_room_12 | 0.1 | policy_kron_oracle | 29 | 29 | 4.966 | 4.8042648821721555e-12 | 0.0 | nan | 0.03431 | 0.1028 | fixed_optimal_policy_only |
| open_room_12 | 0.1 | policy_kron_oracle | 51 | 51 | 2.824 | 4.804064445571456e-12 | 0.0 | nan | 0.06592 | 0.0517 | fixed_optimal_policy_only |
| open_room_12 | 0.1 | policy_kron_oracle | 8 | 8 | 18 | 4.804866191974255e-12 | 0.0 | nan | 0.01818 | 0.2072 | fixed_optimal_policy_only |
| open_room_12 | 0.1 | qstar_oracle_aggregation | 15 | 15 | 9.6 | 0.08176 | 0.8773 | 0.9333 | 0.008361 | 0.4169 | full_action_abstract_mdp |
| open_room_12 | 0.1 | qstar_oracle_aggregation | 29 | 29 | 4.966 | 0.04175 | 0.8743 | 0.9667 | 0.01059 | 0.3259 | full_action_abstract_mdp |
| open_room_12 | 0.1 | qstar_oracle_aggregation | 51 | 51 | 2.824 | 0.009219 | 0.01266 | 0.9333 | 0.01448 | 0.2428 | full_action_abstract_mdp |
| open_room_12 | 0.1 | qstar_oracle_aggregation | 8 | 8 | 18 | 0.1858 | 0.8775 | 0.9333 | 0.01003 | 0.3911 | full_action_abstract_mdp |
| open_room_9 | 0.0 | epsilon_homogeneous | 17 | 2 | 40.5 | 0.8462 | 1.592 | 1 | 6.543 | 0.0001764 | full_action_abstract_mdp |
| open_room_9 | 0.0 | epsilon_homogeneous | 29 | 2 | 40.5 | 0.8462 | 1.592 | 1 | 6.456 | 0.0001704 | full_action_abstract_mdp |
| open_room_9 | 0.0 | epsilon_homogeneous | 5 | 2 | 40.5 | 0.8462 | 1.592 | 1 | 6.582 | 0.0001667 | full_action_abstract_mdp |
| open_room_9 | 0.0 | epsilon_homogeneous | 9 | 2 | 40.5 | 0.8462 | 1.592 | 1 | 6.764 | 0.0001778 | full_action_abstract_mdp |
| open_room_9 | 0.0 | exact_model_minimization | 5 | 81 | 1 | 0.0 | 0.0 | 0.0 | 0.1524 | 0.006661 | full_action_abstract_mdp |
| open_room_9 | 0.0 | policy_kron_oracle | 17 | 17 | 4.765 | 0.0 | 0.0 | nan | 0.009078 | 0.1289 | fixed_optimal_policy_only |
| open_room_9 | 0.0 | policy_kron_oracle | 29 | 29 | 2.793 | 0.0 | 0.0 | nan | 0.01409 | 0.07506 | fixed_optimal_policy_only |
| open_room_9 | 0.0 | policy_kron_oracle | 5 | 5 | 16.2 | 0.0 | 0.0 | nan | 0.007814 | 0.1293 | fixed_optimal_policy_only |
| open_room_9 | 0.0 | policy_kron_oracle | 9 | 9 | 9 | 0.0 | 0.0 | nan | 0.007452 | 0.1452 | fixed_optimal_policy_only |
| open_room_9 | 0.0 | qstar_oracle_aggregation | 17 | 17 | 4.765 | 0.03742 | 1.592 | 1 | 0.004254 | 0.2345 | full_action_abstract_mdp |
| open_room_9 | 0.0 | qstar_oracle_aggregation | 29 | 29 | 2.793 | 0.007922 | 1.592 | 1 | 0.005707 | 0.1862 | full_action_abstract_mdp |
| open_room_9 | 0.0 | qstar_oracle_aggregation | 5 | 5 | 16.2 | 0.3782 | 1.592 | 1 | 0.007069 | 0.1608 | full_action_abstract_mdp |
| open_room_9 | 0.0 | qstar_oracle_aggregation | 9 | 9 | 9 | 0.1453 | 1.592 | 1 | 0.004333 | 0.239 | full_action_abstract_mdp |
| open_room_9 | 0.05 | epsilon_homogeneous | 17 | 2 | 40.5 | 0.781 | 1.477 | 0.95 | 6.614 | 0.0003529 | full_action_abstract_mdp |
| open_room_9 | 0.05 | epsilon_homogeneous | 29 | 2 | 40.5 | 0.781 | 1.477 | 0.95 | 6.532 | 0.000348 | full_action_abstract_mdp |
| open_room_9 | 0.05 | epsilon_homogeneous | 5 | 2 | 40.5 | 0.781 | 1.477 | 0.95 | 6.742 | 0.0003391 | full_action_abstract_mdp |
| open_room_9 | 0.05 | epsilon_homogeneous | 9 | 2 | 40.5 | 0.781 | 1.477 | 0.95 | 6.627 | 0.0003446 | full_action_abstract_mdp |
| open_room_9 | 0.05 | exact_model_minimization | 5 | 81 | 1 | 1.319902100718946e-16 | 2.0194502140999874e-12 | 0.0 | 0.1566 | 0.01519 | full_action_abstract_mdp |
| open_room_9 | 0.05 | policy_kron_oracle | 17 | 17 | 4.765 | 2.0193182238899156e-12 | 0.0 | nan | 0.01069 | 0.2068 | fixed_optimal_policy_only |
| open_room_9 | 0.05 | policy_kron_oracle | 29 | 29 | 2.793 | 2.0194502140999874e-12 | 0.0 | nan | 0.01659 | 0.1328 | fixed_optimal_policy_only |
| open_room_9 | 0.05 | policy_kron_oracle | 5 | 5 | 16.2 | 2.0193182238899156e-12 | 0.0 | nan | 0.008845 | 0.2447 | fixed_optimal_policy_only |
| open_room_9 | 0.05 | policy_kron_oracle | 9 | 9 | 9 | 2.0194502140999874e-12 | 0.0 | nan | 0.008375 | 0.2689 | fixed_optimal_policy_only |
| open_room_9 | 0.05 | qstar_oracle_aggregation | 17 | 17 | 4.765 | 0.04229 | 1.472 | 0.9667 | 0.006497 | 0.3397 | full_action_abstract_mdp |
| open_room_9 | 0.05 | qstar_oracle_aggregation | 29 | 29 | 2.793 | 0.004587 | 0.004194 | 0.9667 | 0.006803 | 0.3128 | full_action_abstract_mdp |
| open_room_9 | 0.05 | qstar_oracle_aggregation | 5 | 5 | 16.2 | 0.3665 | 1.477 | 0.9667 | 0.008427 | 0.2669 | full_action_abstract_mdp |
| open_room_9 | 0.05 | qstar_oracle_aggregation | 9 | 9 | 9 | 0.1506 | 0.3209 | 0.9833 | 0.00589 | 0.3661 | full_action_abstract_mdp |
| open_room_9 | 0.1 | epsilon_homogeneous | 17 | 2 | 40.5 | 0.7128 | 1.357 | 0.9 | 6.636 | 0.0004607 | full_action_abstract_mdp |
| open_room_9 | 0.1 | epsilon_homogeneous | 29 | 2 | 40.5 | 0.7128 | 1.357 | 0.9 | 6.588 | 0.0004213 | full_action_abstract_mdp |
| open_room_9 | 0.1 | epsilon_homogeneous | 5 | 2 | 40.5 | 0.7128 | 1.357 | 0.9 | 6.625 | 0.000405 | full_action_abstract_mdp |
| open_room_9 | 0.1 | epsilon_homogeneous | 9 | 2 | 40.5 | 0.7128 | 1.357 | 0.9 | 6.648 | 0.0004259 | full_action_abstract_mdp |
| open_room_9 | 0.1 | exact_model_minimization | 5 | 81 | 1 | 0.0 | 5.863346531092314e-12 | 0.0 | 0.1573 | 0.01703 | full_action_abstract_mdp |
| open_room_9 | 0.1 | policy_kron_oracle | 17 | 17 | 4.765 | 5.863346531092314e-12 | 0.0 | nan | 0.01173 | 0.2478 | fixed_optimal_policy_only |
| open_room_9 | 0.1 | policy_kron_oracle | 29 | 29 | 2.793 | 5.862969402332971e-12 | 0.0 | nan | 0.01685 | 0.172 | fixed_optimal_policy_only |
| open_room_9 | 0.1 | policy_kron_oracle | 5 | 5 | 16.2 | 5.8630951119194185e-12 | 0.0 | nan | 0.007829 | 0.3401 | fixed_optimal_policy_only |
| open_room_9 | 0.1 | policy_kron_oracle | 9 | 9 | 9 | 5.863472240678762e-12 | 0.0 | nan | 0.009105 | 0.2968 | fixed_optimal_policy_only |
| open_room_9 | 0.1 | qstar_oracle_aggregation | 17 | 17 | 4.765 | 0.06489 | 1.354 | 0.9333 | 0.006188 | 0.4261 | full_action_abstract_mdp |
| open_room_9 | 0.1 | qstar_oracle_aggregation | 29 | 29 | 2.793 | 0.01742 | 0.6598 | 0.9333 | 0.007625 | 0.3488 | full_action_abstract_mdp |
| open_room_9 | 0.1 | qstar_oracle_aggregation | 5 | 5 | 16.2 | 0.3513 | 1.334 | 0.9333 | 0.009312 | 0.3007 | full_action_abstract_mdp |
| open_room_9 | 0.1 | qstar_oracle_aggregation | 9 | 9 | 9 | 0.1323 | 1.288 | 0.9333 | 0.006748 | 0.3971 | full_action_abstract_mdp |

## Primitive-To-Graph Gap Decomposition

This table separates option-family restriction from boundary commitment, kernel approximation, and incomplete graph planning. The certified bound is expected to be conservative; the actual component gaps are retained to expose looseness.

| map | slip | config_label | method_spec | n_boundary | option_restriction_bias | boundary_abstraction_bias | kernel_actual_gap | kernel_gap_bound | planning_actual_gap | planning_gap_bound | primitive_to_solved_gap | certified_total_bound | certificate_holds | normalized_primitive_to_solved_gap | normalized_certified_total_bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_16 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.4530573407062472e-16 | 4.84352446902082e-15 |
| open_room_9 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| maze_11 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.4232440267942716e-16 | 1.1410813422647563e-14 |
| corridor_16 | 0.0 | fixed_k32_i8 | turn_articulation | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.4530573407062472e-16 | 4.84352446902082e-15 |
| open_room_9 | 0.0 | fixed_k32_i8 | turn_articulation | 4 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | True | 1.3814960442367423e-16 | 1.3814960442367423e-16 |
| maze_11 | 0.0 | fixed_k32_i8 | turn_articulation | 15 | 0.0 | 3.552713678800501e-15 | 0.0 | 0.0 | 7.898203422347608 | 40.33598991071635 | 7.898203422347612 | 40.33598991071635 | True | 0.3805186701266364 | 1.9433023459029992 |
| corridor_16 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.4530573407062472e-16 | 4.84352446902082e-15 |
| open_room_9 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| maze_11 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 12 | 0.0 | 3.552713678800501e-15 | 0.0 | 0.0 | 7.898203422347608 | 40.33598991071635 | 7.898203422347612 | 40.33598991071635 | True | 0.3805186701266364 | 1.9433023459029992 |
| corridor_16 | 0.05 | fixed_k32_i8 | endpoints | 2 | 3.552713678800501e-15 | 3.711164708875003e-11 | 2.737099435989876e-10 | 8.395367723854181e-08 | 3.6907987777112794e-09 | 1.1516506267147017e-07 | 3.927393521507838e-09 | 1.9915585510981442e-07 | True | 3.050402178006442e-10 | 1.5468413105607882e-08 |
| open_room_9 | 0.05 | fixed_k32_i8 | endpoints | 2 | 0.06464888018276582 | 3.888089850079268e-11 | 1.8386112188295556e-08 | 5.4144941198451525e-06 | 3.801350345611354e-10 | 1.2090832039272441e-08 | 0.0646488614553995 | 0.06465430680659862 | True | 0.004803661412584187 | 0.004804066023320468 |
| maze_11 | 0.05 | fixed_k32_i8 | endpoints | 2 | 7.105427357601002e-15 | 4.566658162730164e-11 | 0.28671984702030073 | 90.88452808630167 | 6.106500194391629e-09 | 1.9054292958268569e-07 | 0.28671985308112724 | 90.88452827689028 | True | 0.01328103792223229 | 4.2098266081631985 |
| corridor_16 | 0.05 | fixed_k32_i8 | turn_articulation | 2 | 3.552713678800501e-15 | 3.711164708875003e-11 | 2.737099435989876e-10 | 8.395367723854181e-08 | 3.6907987777112794e-09 | 1.1516506267147017e-07 | 3.927393521507838e-09 | 1.9915585510981442e-07 | True | 3.050402178006442e-10 | 1.5468413105607882e-08 |
| open_room_9 | 0.05 | fixed_k32_i8 | turn_articulation | 4 | 0.006004904414314893 | 0.05864397580684866 | 1.3177459123880908e-09 | 4.326523795389907e-06 | 7.787712164031291e-08 | 2.4264810605245636e-06 | 0.064648801026296 | 0.06465563322601947 | True | 0.004803656922467175 | 0.00480416458143341 |
| maze_11 | 0.05 | fixed_k32_i8 | turn_articulation | 15 | 1.7763568394002505e-14 | 4.447642254490347e-11 | 1.7763568394002505e-14 | 1.2947357576323633e-13 | 8.781378181012853 | 40.46643884411287 | 8.781378180968387 | 40.466438844157494 | True | 0.40675877647685993 | 1.874430051116419 |
| corridor_16 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 3.552713678800501e-15 | 3.711164708875003e-11 | 2.737099435989876e-10 | 8.395367723854181e-08 | 3.6907987777112794e-09 | 1.1516506267147017e-07 | 3.927393521507838e-09 | 1.9915585510981442e-07 | True | 3.050402178006442e-10 | 1.5468413105607882e-08 |
| open_room_9 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.06464888018276582 | 3.888089850079268e-11 | 1.8386112188295556e-08 | 5.4144941198451525e-06 | 3.801350345611354e-10 | 1.2090832039272441e-08 | 0.0646488614553995 | 0.06465430680659862 | True | 0.004803661412584187 | 0.004804066023320468 |
| maze_11 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 12 | 1.7763568394002505e-14 | 4.447642254490347e-11 | 1.7763568394002505e-14 | 1.590795230865738e-13 | 8.781378181012853 | 40.46643884411299 | 8.781378180968387 | 40.46643884415764 | True | 0.40675877647685993 | 1.8744300511164258 |
| corridor_16 | 0.1 | fixed_k32_i8 | endpoints | 2 | 5.329070518200751e-15 | 5.4647841807309305e-11 | 6.040006379492979e-07 | 0.00015043299524377017 | 9.932190661032791e-07 | 2.886239010753871e-05 | 1.5971650508816992e-06 | 0.00017929544000447976 | True | 1.1748083934969091e-07 | 1.3188229213800026e-05 |
| open_room_9 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.1372450496721065 | 6.767031379695254e-11 | 1.4826142940904674e-05 | 0.003509386576943706 | 1.0291689633845635e-07 | 3.101493106782979e-06 | 0.13723012067993956 | 0.1407575378098273 | True | 0.009711529427085043 | 0.009961158408600006 |
| maze_11 | 0.1 | fixed_k32_i8 | endpoints | 2 | 3.552713678800501e-15 | 3.186428898516169e-11 | 0.9665514285714529 | 177.90775209928555 | 1.5715311398878384e-06 | 4.566781524791467e-05 | 0.966553000070725 | 177.90779776713265 | True | 0.04300080590047302 | 7.914908628295909 |
| corridor_16 | 0.1 | fixed_k32_i8 | turn_articulation | 2 | 5.329070518200751e-15 | 5.4647841807309305e-11 | 6.040006379492979e-07 | 0.00015043299524377017 | 9.932190661032791e-07 | 2.886239010753871e-05 | 1.5971650508816992e-06 | 0.00017929544000447976 | True | 1.1748083934969091e-07 | 1.3188229213800026e-05 |
| open_room_9 | 0.1 | fixed_k32_i8 | turn_articulation | 4 | 0.025795264125143547 | 0.11207546250206946 | 1.899423535789424e-06 | 0.002644453067138948 | 8.99235084261818e-06 | 0.0002607956618660976 | 0.13723415796895644 | 0.14077597535621805 | True | 0.009711815138785206 | 0.009962463200678085 |
| maze_11 | 0.1 | fixed_k32_i8 | turn_articulation | 15 | 7.105427357601002e-15 | 2.4133584020091803e-11 | 1.8260948309034575e-12 | 8.811228507277601e-11 | 9.726650142482418 | 40.5328303514057 | 9.726650142459457 | 40.53283035151795 | True | 0.43272722220830384 | 1.8032579386902627 |
| corridor_16 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 5.329070518200751e-15 | 5.4647841807309305e-11 | 6.040006379492979e-07 | 0.00015043299524377017 | 9.932190661032791e-07 | 2.886239010753871e-05 | 1.5971650508816992e-06 | 0.00017929544000447976 | True | 1.1748083934969091e-07 | 1.3188229213800026e-05 |
| open_room_9 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.1372450496721065 | 6.767031379695254e-11 | 1.4826142940904674e-05 | 0.003509386576943706 | 1.0291689633845635e-07 | 3.101493106782979e-06 | 0.13723012067993956 | 0.1407575378098273 | True | 0.009711529427085043 | 0.009961158408600006 |
| maze_11 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 15 | 7.105427357601002e-15 | 2.4133584020091803e-11 | 1.8260948309034575e-12 | 8.811228507277601e-11 | 9.726650142482418 | 40.5328303514057 | 9.726650142459457 | 40.53283035151795 | True | 0.43272722220830384 | 1.8032579386902627 |
| corridor_32 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.488621061101381e-16 | 1.1628736870337928e-14 |
| four_rooms_7 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| corridor_32 | 0.0 | fixed_k32_i8 | turn_articulation | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.488621061101381e-16 | 1.1628736870337928e-14 |
| four_rooms_7 | 0.0 | fixed_k32_i8 | turn_articulation | 16 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | True | 1.7406296101340607e-16 | 1.7406296101340607e-16 |
| corridor_32 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.488621061101381e-16 | 1.1628736870337928e-14 |
| four_rooms_7 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| corridor_32 | 0.05 | fixed_k32_i8 | endpoints | 2 | 1.7763568394002505e-14 | 1.929478798956552e-11 | 0.14118829512667475 | 48.74521670206722 | 6.0328666506848094e-09 | 1.882452712228161e-07 | 0.14118830114022884 | 48.745216890331804 | True | 0.006664141467551395 | 2.300792761158089 |
| four_rooms_7 | 0.05 | fixed_k32_i8 | endpoints | 2 | 0.024212229488799863 | 0.000197274882335563 | 1.1185008474967617e-10 | 2.7575846227856156e-08 | 3.051390251584962e-10 | 9.7053032277472e-09 | 0.024409503954146317 | 0.024409541652284882 | True | 0.0022582336329549195 | 0.0022582371205802547 |
| corridor_32 | 0.05 | fixed_k32_i8 | turn_articulation | 2 | 1.7763568394002505e-14 | 1.929478798956552e-11 | 0.14118829512667475 | 48.74521670206722 | 6.0328666506848094e-09 | 1.882452712228161e-07 | 0.14118830114022884 | 48.745216890331804 | True | 0.006664141467551395 | 2.300792761158089 |
| four_rooms_7 | 0.05 | fixed_k32_i8 | turn_articulation | 16 | 0.000475461160198698 | 0.05393893994279786 | 1.0658141036401503e-14 | 9.986797343311034e-13 | 0.005829434955940016 | 0.17743571410093734 | 0.05437175501901326 | 0.23185011520493257 | True | 0.00503017702028576 | 0.021449502986369173 |
| corridor_32 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 1.7763568394002505e-14 | 1.929478798956552e-11 | 0.14118829512667475 | 48.74521670206722 | 6.0328666506848094e-09 | 1.882452712228161e-07 | 0.14118830114022884 | 48.745216890331804 | True | 0.006664141467551395 | 2.300792761158089 |
| four_rooms_7 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 6 | 0.0004913308229363977 | 0.025014054472062952 | 2.859934511434403e-13 | 5.006815309480543e-10 | 0.003695537272175642 | 0.11365493712235746 | 0.02530544697891024 | 0.13916032291803834 | True | 0.0023411213751857313 | 0.012874350997739157 |
| corridor_32 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.0 | 6.585665346392489e-11 | 0.6545417407741034 | 136.83603207049399 | 1.5639668013989194e-06 | 4.5447999852399294e-05 | 0.6545433046750482 | 136.83607751855968 | True | 0.02966834989922846 | 6.202340773578059 |
| four_rooms_7 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.050577184819584176 | 0.0008546880598370166 | 3.385094835550717e-07 | 6.89641608364196e-05 | 8.389037375877706e-08 | 2.52784276473979e-06 | 0.05143145047956388 | 0.05150336488302235 | True | 0.0044778964895976275 | 0.0044841577412597046 |
| corridor_32 | 0.1 | fixed_k32_i8 | turn_articulation | 2 | 0.0 | 6.585665346392489e-11 | 0.6545417407741034 | 136.83603207049399 | 1.5639668013989194e-06 | 4.5447999852399294e-05 | 0.6545433046750482 | 136.83607751855968 | True | 0.02966834989922846 | 6.202340773578059 |
| four_rooms_7 | 0.1 | fixed_k32_i8 | turn_articulation | 16 | 0.001118584567544545 | 0.1140430488006583 | 6.061462443085475e-11 | 5.695633375862434e-09 | 0.04805219445151998 | 1.3226747054249077 | 0.11454322763994895 | 1.4378363444887439 | True | 0.009972744540034188 | 0.12518570368067572 |
| corridor_32 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 6.585665346392489e-11 | 0.6545417407741034 | 136.83603207049399 | 1.5639668013989194e-06 | 4.5447999852399294e-05 | 0.6545433046750482 | 136.83607751855968 | True | 0.02966834989922846 | 6.202340773578059 |
| four_rooms_7 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 6 | 0.04913367734678609 | 0.04953969083749854 | 1.0924559035174752e-08 | 5.645981686923498e-06 | 0.03689064382833962 | 1.0415983944784075 | 0.05074751998253646 | 1.140277408644379 | True | 0.0044183498514372916 | 0.09927863510995115 |
| corridor_64 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 6.9414923168168166 | 336.56246127027794 | 0.0 | 0.0 | 6.9414923168168166 | 336.56246127027794 | True | 0.24406465072633127 | 11.833622484681129 |
| four_rooms_9 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| corridor_64 | 0.0 | fixed_k32_i8 | turn_articulation | 2 | 0.0 | 0.0 | 6.9414923168168166 | 336.56246127027794 | 0.0 | 0.0 | 6.9414923168168166 | 336.56246127027794 | True | 0.24406465072633127 | 11.833622484681129 |
| four_rooms_9 | 0.0 | fixed_k32_i8 | turn_articulation | 16 | 0.0 | 1.7763568394002505e-15 | 0.0 | 2.9605947323337485e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 3.1382304162737735e-14 | True | 1.3814960442367423e-16 | 2.4406430114849096e-15 |
| corridor_64 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 6.9414923168168166 | 336.56246127027794 | 0.0 | 0.0 | 6.9414923168168166 | 336.56246127027794 | True | 0.24406465072633127 | 11.833622484681129 |
| four_rooms_9 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| corridor_64 | 0.05 | fixed_k32_i8 | endpoints | 2 | 2.842170943040401e-14 | 3.1533886613033246e-11 | 7.519515505403707 | 320.86075735609114 | 6.1723213207187655e-09 | 1.9259675336040025e-07 | 7.519515511544466 | 320.86075754871945 | True | 0.25883782525169186 | 11.04471432567904 |
| four_rooms_9 | 0.05 | fixed_k32_i8 | endpoints | 2 | 0.04323329045202229 | 0.00035460921815477775 | 4.540342679604237e-08 | 1.307966834751156e-05 | 3.8187053519322944e-10 | 1.2146017525083141e-08 | 0.043587853884879735 | 0.0436009914845421 | True | 0.003219097043574632 | 0.0032200672957082765 |
| corridor_64 | 0.05 | fixed_k32_i8 | turn_articulation | 2 | 2.842170943040401e-14 | 3.1533886613033246e-11 | 7.519515505403707 | 320.86075735609114 | 6.1723213207187655e-09 | 1.9259675336040025e-07 | 7.519515511544466 | 320.86075754871945 | True | 0.25883782525169186 | 11.04471432567904 |
| four_rooms_9 | 0.05 | fixed_k32_i8 | turn_articulation | 16 | 0.014407652713009256 | 0.07406255079447277 | 4.153832833253546e-11 | 5.03402501573175e-09 | 0.0009336763662783909 | 0.02880087432709878 | 0.08695681268872058 | 0.11727108286860582 | True | 0.006422028012304506 | 0.008660830082530829 |
| corridor_64 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 2.842170943040401e-14 | 3.1533886613033246e-11 | 7.519515505403707 | 320.86075735609114 | 6.1723213207187655e-09 | 1.9259675336040025e-07 | 7.519515511544466 | 320.86075754871945 | True | 0.25883782525169186 | 11.04471432567904 |
| four_rooms_9 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.04323329045202229 | 0.00035460921815477775 | 4.540342679604237e-08 | 1.307966834751156e-05 | 3.8187053519322944e-10 | 1.2146017525083141e-08 | 0.043587853884879735 | 0.0436009914845421 | True | 0.003219097043574632 | 0.0032200672957082765 |
| corridor_64 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.0 | 5.5845106317065074e-11 | 8.088784219355347 | 304.16562137183723 | 1.5757762419355004e-06 | 4.579117553286471e-05 | 8.088785795075744 | 304.1656671630686 | True | 0.27273634264326485 | 10.255807697393365 |
| four_rooms_9 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.09107846271449205 | 0.0015890525894413088 | 3.126069351999661e-05 | 0.007237828028831662 | 1.0385461557405051e-07 | 3.129737239741338e-06 | 0.09263615075579779 | 0.09990847307000476 | True | 0.006478017214328927 | 0.0069865684522119696 |
| corridor_64 | 0.1 | fixed_k32_i8 | turn_articulation | 2 | 0.0 | 5.5845106317065074e-11 | 8.088784219355347 | 304.16562137183723 | 1.5757762419355004e-06 | 4.579117553286471e-05 | 8.088785795075744 | 304.1656671630686 | True | 0.27273634264326485 | 10.255807697393365 |
| four_rooms_9 | 0.1 | fixed_k32_i8 | turn_articulation | 16 | 0.03354517780304711 | 0.15637104105985777 | 1.2104990965156048e-07 | 1.0932993324281837e-05 | 0.011378106035188296 | 0.32171420952652807 | 0.18356784484847743 | 0.5116413613827573 | True | 0.012836842304258559 | 0.035778921291078694 |
| corridor_64 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 5.5845106317065074e-11 | 8.088784219355347 | 304.16562137183723 | 1.5757762419355004e-06 | 4.579117553286471e-05 | 8.088785795075744 | 304.1656671630686 | True | 0.27273634264326485 | 10.255807697393365 |
| four_rooms_9 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.09107846271449205 | 0.0015890525894413088 | 3.126069351999661e-05 | 0.007237828028831662 | 1.0385461557405051e-07 | 3.129737239741338e-06 | 0.09263615075579779 | 0.09990847307000476 | True | 0.006478017214328927 | 0.0069865684522119696 |
| open_room_7 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| maze_9 | 0.0 | fixed_k32_i8 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| open_room_7 | 0.0 | fixed_k32_i8 | turn_articulation | 4 | 0.0 | 1.7763568394002505e-15 | 0.0 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 6.098825148607522e-14 | True | 1.7406296101340607e-16 | 5.976161661460271e-15 |
| maze_9 | 0.0 | fixed_k32_i8 | turn_articulation | 8 | 0.0 | 1.7763568394002505e-15 | 0.0 | 394.4540828227036 | 2.996699948075271 | 26.124778647923172 | 2.9966999480752694 | 420.57886147062675 | True | 0.293642839468456 | 41.211990937553566 |
| open_room_7 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| maze_9 | 0.0 | fixed_k32_i8 | graph_rd_surrogate_joint | 5 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | True | 1.7406296101340607e-16 | 1.7406296101340607e-16 |
| open_room_7 | 0.05 | fixed_k32_i8 | endpoints | 2 | 0.04973231542109424 | 2.1886492618250486e-11 | 5.005951209113846e-11 | 1.2275069279597381e-08 | 3.0256153138452646e-10 | 9.623472389345495e-09 | 0.04973231509035969 | 0.0497323373415224 | True | 0.00464199891356802 | 0.004642000990484668 |
| maze_9 | 0.05 | fixed_k32_i8 | endpoints | 2 | 3.552713678800501e-15 | 1.9046098032049485e-11 | 3.270272941335861e-12 | 8.557760844064392e-10 | 3.092187839115468e-09 | 9.648643365759796e-08 | 3.0764084613110754e-09 | 9.736125939275013e-08 | True | 2.8520119539858376e-10 | 9.025962551309005e-09 |
| open_room_7 | 0.05 | fixed_k32_i8 | turn_articulation | 4 | 0.00382846108703383 | 0.04590385435547972 | 2.1280754936015e-12 | 8.631205094282902e-09 | 6.614359548962057e-08 | 2.0608283672155855e-06 | 0.04973224929678999 | 0.04973438490208586 | True | 0.0046419927724165675 | 0.0046421921091545654 |
| maze_9 | 0.05 | fixed_k32_i8 | turn_articulation | 8 | 3.552713678800501e-15 | 1.8765433651424246e-11 | 1.7816859099184512e-12 | 371.9546877172262 | 2.1939253003324932 | 29.848874139135827 | 2.193925300315506 | 401.8035618563808 | True | 0.20338980539616633 | 37.249558242344584 |
| open_room_7 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.04973231542109424 | 2.1886492618250486e-11 | 5.005951209113846e-11 | 1.2275069279597381e-08 | 3.0256153138452646e-10 | 9.623472389345495e-09 | 0.04973231509035969 | 0.0497323373415224 | True | 0.00464199891356802 | 0.004642000990484668 |
| maze_9 | 0.05 | fixed_k32_i8 | graph_rd_surrogate_joint | 5 | 3.552713678800501e-15 | 1.8838264281839656e-11 | 3.552713678800501e-15 | 7.451504583459935e-14 | 0.00674002654858441 | 0.2051498942945427 | 0.006740026529746146 | 0.20514989431345904 | True | 0.0006248401821397138 | 0.01901860426854918 |
| open_room_7 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.10689515935551341 | 4.545519516341301e-11 | 1.692785716045364e-07 | 3.411440558959749e-05 | 8.216968439000993e-08 | 2.4762572436998177e-06 | 0.10689490795271261 | 0.1069317500638019 | True | 0.009472562475412899 | 0.009475827263284494 |
| maze_9 | 0.1 | fixed_k32_i8 | endpoints | 2 | 0.0 | 2.5870861009025248e-11 | 2.0085044738493707e-08 | 4.3188924616103e-06 | 8.355206979615559e-07 | 2.4279763799484024e-05 | 8.555798718390406e-07 | 2.859868213195533e-05 | True | 7.48110334524378e-08 | 2.5006396668385473e-06 |
| open_room_7 | 0.1 | fixed_k32_i8 | turn_articulation | 4 | 0.01627865195821876 | 0.09061650744518168 | 1.3120500241825539e-08 | 2.2134478541913254e-05 | 7.850307111922916e-06 | 0.00022762438245393904 | 0.10688729597578828 | 0.10714491826439629 | True | 0.009471887935078301 | 0.009494717303386264 |
| maze_9 | 0.1 | fixed_k32_i8 | turn_articulation | 8 | 1.7763568394002505e-15 | 2.282618538629322e-11 | 3.511857471494295e-12 | 347.480009307301 | 2.2074497526986967 | 31.726873672678746 | 2.2074497526793824 | 379.20688298000255 | True | 0.1930171603234499 | 33.15746400979924 |
| open_room_7 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 2 | 0.10689515935551341 | 4.545519516341301e-11 | 1.692785716045364e-07 | 3.411440558959749e-05 | 8.216968439000993e-08 | 2.4762572436998177e-06 | 0.10689490795271261 | 0.1069317500638019 | True | 0.009472562475412899 | 0.009475827263284494 |
| maze_9 | 0.1 | fixed_k32_i8 | graph_rd_surrogate_joint | 7 | 1.7763568394002505e-15 | 1.3709922086491133e-11 | 3.552713678800501e-15 | 1.8196102594340113e-13 | 0.054632695005679466 | 1.5067686952071673 | 0.05463269499196599 | 1.5067686952210608 | True | 0.004777027262055209 | 0.1317503215929737 |
| corridor_16 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.4530573407062472e-16 | 4.84352446902082e-15 |
| open_room_9 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| maze_11 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.4232440267942716e-16 | 1.1410813422647563e-14 |
| corridor_16 | 0.0 | converged_k256_i256 | turn_articulation | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.4530573407062472e-16 | 4.84352446902082e-15 |
| open_room_9 | 0.0 | converged_k256_i256 | turn_articulation | 4 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | True | 1.3814960442367423e-16 | 1.3814960442367423e-16 |
| maze_11 | 0.0 | converged_k256_i256 | turn_articulation | 15 | 0.0 | 3.552713678800501e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 3.552713678800501e-15 | 3.552713678800501e-15 | True | 1.7116220133971358e-16 | 1.7116220133971358e-16 |
| corridor_16 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.4530573407062472e-16 | 4.84352446902082e-15 |
| open_room_9 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| maze_11 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 12 | 0.0 | 3.552713678800501e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 3.552713678800501e-15 | 3.552713678800501e-15 | True | 1.7116220133971358e-16 | 1.7116220133971358e-16 |
| corridor_16 | 0.05 | converged_k256_i256 | endpoints | 2 | 3.552713678800501e-15 | 3.711164708875003e-11 | 5.329070518200751e-15 | 4.635181649972511e-13 | 9.734435479913373e-13 | 0.0 | 3.808331427990197e-11 | 3.7578717967426084e-11 | True | 2.957926782455863e-12 | 2.9187348430140647e-12 |
| open_room_9 | 0.05 | converged_k256_i256 | endpoints | 2 | 0.06464888018276582 | 3.888089850079268e-11 | 5.329070518200751e-15 | 3.809425524146793e-13 | 8.775202786637237e-13 | 0.0 | 0.06464888022251891 | 0.06464888022202767 | True | 0.004803662807054025 | 0.004803662807017524 |
| maze_11 | 0.05 | converged_k256_i256 | endpoints | 2 | 7.105427357601002e-15 | 4.566658162730164e-11 | 1.0658141036401503e-14 | 6.748477788728623e-13 | 1.6342482922482304e-12 | 0.0 | 4.729727720587107e-11 | 4.63485348335321e-11 | True | 2.1908386372246426e-12 | 2.146892313696438e-12 |
| corridor_16 | 0.05 | converged_k256_i256 | turn_articulation | 2 | 3.552713678800501e-15 | 3.711164708875003e-11 | 5.329070518200751e-15 | 4.635181649972511e-13 | 9.734435479913373e-13 | 0.0 | 3.808331427990197e-11 | 3.7578717967426084e-11 | True | 2.957926782455863e-12 | 2.9187348430140647e-12 |
| open_room_9 | 0.05 | converged_k256_i256 | turn_articulation | 4 | 0.006004904414314893 | 0.05864397580684866 | 7.105427357601002e-15 | 5.688266979141084e-13 | 1.3677947663381929e-12 | 0.0 | 0.06464888022252424 | 0.06464888022173237 | True | 0.004803662807054422 | 0.0048036628069955825 |
| maze_11 | 0.05 | converged_k256_i256 | turn_articulation | 15 | 1.7763568394002505e-14 | 4.447642254490347e-11 | 1.7763568394002505e-14 | 1.2947357576323633e-13 | 2.8208546609675977e-12 | 0.0 | 4.728661906483467e-11 | 4.462365968906071e-11 | True | 2.190344945651618e-12 | 2.0669950482693434e-12 |
| corridor_16 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 3.552713678800501e-15 | 3.711164708875003e-11 | 5.329070518200751e-15 | 4.635181649972511e-13 | 9.734435479913373e-13 | 0.0 | 3.808331427990197e-11 | 3.7578717967426084e-11 | True | 2.957926782455863e-12 | 2.9187348430140647e-12 |
| open_room_9 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.06464888018276582 | 3.888089850079268e-11 | 5.329070518200751e-15 | 3.809425524146793e-13 | 8.775202786637237e-13 | 0.0 | 0.06464888022251891 | 0.06464888022202767 | True | 0.004803662807054025 | 0.004803662807017524 |
| maze_11 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 12 | 1.7763568394002505e-14 | 4.447642254490347e-11 | 1.7763568394002505e-14 | 1.590795230865738e-13 | 2.8208546609675977e-12 | 0.0 | 4.728661906483467e-11 | 4.465326563638405e-11 | True | 2.190344945651618e-12 | 2.0683664137499668e-12 |
| corridor_16 | 0.1 | converged_k256_i256 | endpoints | 2 | 5.329070518200751e-15 | 5.4647841807309305e-11 | 0.0 | 1.1320203937753431e-13 | 4.4142467459096224e-12 | 0.0 | 5.906741762373713e-11 | 5.476637291720504e-11 | True | 4.344754348853675e-12 | 4.0283873322294415e-12 |
| open_room_9 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.1372450496721065 | 6.767031379695254e-11 | 3.552713678800501e-15 | 2.3081767819233686e-13 | 8.741452006688633e-12 | 0.0 | 0.1372450497485218 | 0.13724504974000762 | True | 0.009712585930483401 | 0.009712585929880868 |
| maze_11 | 0.1 | converged_k256_i256 | endpoints | 2 | 3.552713678800501e-15 | 3.186428898516169e-11 | 7.105427357601002e-15 | 3.4082716035743313e-13 | 7.297273896256229e-12 | 0.0 | 3.915801016773912e-11 | 3.220866885919793e-11 | True | 1.7420938060804624e-12 | 1.432925786610394e-12 |
| corridor_16 | 0.1 | converged_k256_i256 | turn_articulation | 2 | 5.329070518200751e-15 | 5.4647841807309305e-11 | 0.0 | 1.1320203937753431e-13 | 4.4142467459096224e-12 | 0.0 | 5.906741762373713e-11 | 5.476637291720504e-11 | True | 4.344754348853675e-12 | 4.0283873322294415e-12 |
| open_room_9 | 0.1 | converged_k256_i256 | turn_articulation | 4 | 0.025795264125143547 | 0.11207546250206946 | 1.7763568394002505e-15 | 5.076468069308792e-13 | 5.183409257369931e-12 | 0.0 | 0.13724504974851648 | 0.13787072662772065 | True | 0.009712585930483025 | 0.009756863960656953 |
| maze_11 | 0.1 | converged_k256_i256 | turn_articulation | 15 | 7.105427357601002e-15 | 2.4133584020091803e-11 | 2.842170943040401e-14 | 2.999531772476525e-13 | 1.5003109865574515e-11 | 0.0 | 3.916866830877552e-11 | 2.4440642624697055e-11 | True | 1.7425679742367172e-12 | 1.0873354379020329e-12 |
| corridor_16 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 5.329070518200751e-15 | 5.4647841807309305e-11 | 0.0 | 1.1320203937753431e-13 | 4.4142467459096224e-12 | 0.0 | 5.906741762373713e-11 | 5.476637291720504e-11 | True | 4.344754348853675e-12 | 4.0283873322294415e-12 |
| open_room_9 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.1372450496721065 | 6.767031379695254e-11 | 3.552713678800501e-15 | 2.3081767819233686e-13 | 8.741452006688633e-12 | 0.0 | 0.1372450497485218 | 0.13724504974000762 | True | 0.009712585930483401 | 0.009712585929880868 |
| maze_11 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 15 | 7.105427357601002e-15 | 2.4133584020091803e-11 | 2.842170943040401e-14 | 2.999531772476525e-13 | 1.5003109865574515e-11 | 0.0 | 3.916866830877552e-11 | 2.4440642624697055e-11 | True | 1.7425679742367172e-12 | 1.0873354379020329e-12 |
| corridor_32 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.488621061101381e-16 | 1.1628736870337928e-14 |
| four_rooms_7 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| corridor_32 | 0.0 | converged_k256_i256 | turn_articulation | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.488621061101381e-16 | 1.1628736870337928e-14 |
| four_rooms_7 | 0.0 | converged_k256_i256 | turn_articulation | 16 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | True | 1.7406296101340607e-16 | 1.7406296101340607e-16 |
| corridor_32 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | 0.0 | 0.0 | 7.105427357601002e-15 | 2.368475785866999e-13 | True | 3.488621061101381e-16 | 1.1628736870337928e-14 |
| four_rooms_7 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| corridor_32 | 0.05 | converged_k256_i256 | endpoints | 2 | 1.7763568394002505e-14 | 1.929478798956552e-11 | 1.0658141036401503e-14 | 1.1001183889210727e-12 | 1.602273869139026e-12 | 0.0 | 2.0904167286062147e-11 | 2.0412669946880594e-11 | True | 9.866846398081979e-13 | 9.634857786222572e-13 |
| four_rooms_7 | 0.05 | converged_k256_i256 | endpoints | 2 | 0.024212229488799863 | 0.000197274882335563 | 5.329070518200751e-15 | 4.1818822049419276e-13 | 7.034373084024992e-13 | 0.0 | 0.024409504371833535 | 0.024409504371553616 | True | 0.0022582336715970537 | 0.0022582336715711573 |
| corridor_32 | 0.05 | converged_k256_i256 | turn_articulation | 2 | 1.7763568394002505e-14 | 1.929478798956552e-11 | 1.0658141036401503e-14 | 1.1001183889210727e-12 | 1.602273869139026e-12 | 0.0 | 2.0904167286062147e-11 | 2.0412669946880594e-11 | True | 9.866846398081979e-13 | 9.634857786222572e-13 |
| four_rooms_7 | 0.05 | converged_k256_i256 | turn_articulation | 16 | 0.000475461160198698 | 0.05393893994279786 | 3.552713678800501e-15 | 5.430539016706588e-13 | 9.379164112033322e-13 | 0.0 | 0.054385121827552396 | 0.05441440110353961 | True | 0.005031413644211631 | 0.005034122402484929 |
| corridor_32 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 1.7763568394002505e-14 | 1.929478798956552e-11 | 1.0658141036401503e-14 | 1.1001183889210727e-12 | 1.602273869139026e-12 | 0.0 | 2.0904167286062147e-11 | 2.0412669946880594e-11 | True | 9.866846398081979e-13 | 9.634857786222572e-13 |
| four_rooms_7 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 6 | 0.0004913308229363977 | 0.025014054472062952 | 5.329070518200751e-15 | 3.2139244397119534e-13 | 3.256062086620659e-12 | 0.0 | 0.025432055161099143 | 0.025505385295320742 | True | 0.0023528344708620445 | 0.002359618573305068 |
| corridor_32 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.0 | 6.585665346392489e-11 | 1.7763568394002505e-14 | 7.390440797669476e-13 | 7.16227077646181e-12 | 0.0 | 7.30366878087807e-11 | 6.659569754369183e-11 | True | 3.310518943383553e-12 | 3.018569500898536e-12 |
| four_rooms_7 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.050577184819584176 | 0.0008546880598370166 | 0.0 | 1.2808708807565672e-13 | 7.153388992264809e-12 | 0.0 | 0.05143187288657458 | 0.05143187287954928 | True | 0.004477933266605718 | 0.004477933265994058 |
| corridor_32 | 0.1 | converged_k256_i256 | turn_articulation | 2 | 0.0 | 6.585665346392489e-11 | 1.7763568394002505e-14 | 7.390440797669476e-13 | 7.16227077646181e-12 | 0.0 | 7.30366878087807e-11 | 6.659569754369183e-11 | True | 3.310518943383553e-12 | 3.018569500898536e-12 |
| four_rooms_7 | 0.1 | converged_k256_i256 | turn_articulation | 16 | 0.001118584567544545 | 0.1140430488006583 | 3.552713678800501e-15 | 4.231495085122219e-13 | 1.9547030660760356e-11 | 0.0 | 0.11508961296317821 | 0.11516163336862599 | True | 0.010020315761495813 | 0.01002658624225665 |
| corridor_32 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 6.585665346392489e-11 | 1.7763568394002505e-14 | 7.390440797669476e-13 | 7.16227077646181e-12 | 0.0 | 7.30366878087807e-11 | 6.659569754369183e-11 | True | 3.310518943383553e-12 | 3.018569500898536e-12 |
| four_rooms_7 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 6 | 0.04913367734678609 | 0.04953969083749854 | 3.552713678800501e-15 | 5.250435267570226e-13 | 3.3448799285906716e-12 | 0.0 | 0.053444808142931066 | 0.09867336818480966 | True | 0.004653190149975313 | 0.008591029902746001 |
| corridor_64 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-14 | 5.921189464667496e-13 | 0.0 | 0.0 | 1.7763568394002505e-14 | 5.921189464667496e-13 | True | 6.245716220462007e-16 | 2.081905406820667e-14 |
| four_rooms_9 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| corridor_64 | 0.0 | converged_k256_i256 | turn_articulation | 2 | 0.0 | 0.0 | 1.7763568394002505e-14 | 5.921189464667496e-13 | 0.0 | 0.0 | 1.7763568394002505e-14 | 5.921189464667496e-13 | True | 6.245716220462007e-16 | 2.081905406820667e-14 |
| four_rooms_9 | 0.0 | converged_k256_i256 | turn_articulation | 16 | 0.0 | 1.7763568394002505e-15 | 0.0 | 2.9605947323337485e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 3.1382304162737735e-14 | True | 1.3814960442367423e-16 | 2.4406430114849096e-15 |
| corridor_64 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-14 | 5.921189464667496e-13 | 0.0 | 0.0 | 1.7763568394002505e-14 | 5.921189464667496e-13 | True | 6.245716220462007e-16 | 2.081905406820667e-14 |
| four_rooms_9 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.3814960442367423e-16 | 4.604986814122471e-15 |
| corridor_64 | 0.05 | converged_k256_i256 | endpoints | 2 | 2.842170943040401e-14 | 3.1533886613033246e-11 | 3.552713678800501e-14 | 1.657122140600954e-12 | 2.19912976717751e-12 | 0.0 | 3.3725910952853155e-11 | 3.32194304630646e-11 | True | 1.1609180714191688e-12 | 1.1434839284470568e-12 |
| four_rooms_9 | 0.05 | converged_k256_i256 | endpoints | 2 | 0.04323329045202229 | 0.00035460921815477775 | 1.5987211554602254e-14 | 8.790038441409905e-13 | 8.828493491819245e-13 | 0.0 | 0.04358789967104393 | 0.04358789967105607 | True | 0.0032191004250236516 | 0.0032191004250245485 |
| corridor_64 | 0.05 | converged_k256_i256 | turn_articulation | 2 | 2.842170943040401e-14 | 3.1533886613033246e-11 | 3.552713678800501e-14 | 1.657122140600954e-12 | 2.19912976717751e-12 | 0.0 | 3.3725910952853155e-11 | 3.32194304630646e-11 | True | 1.1609180714191688e-12 | 1.1434839284470568e-12 |
| four_rooms_9 | 0.05 | converged_k256_i256 | turn_articulation | 16 | 0.014407652713009256 | 0.07406255079447277 | 8.881784197001252e-15 | 6.176165507366105e-13 | 5.613287612504791e-13 | 0.0 | 0.08695915168368451 | 0.08847020350809964 | True | 0.0064222007542750845 | 0.006533796578045388 |
| corridor_64 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 2.842170943040401e-14 | 3.1533886613033246e-11 | 3.552713678800501e-14 | 1.657122140600954e-12 | 2.19912976717751e-12 | 0.0 | 3.3725910952853155e-11 | 3.32194304630646e-11 | True | 1.1609180714191688e-12 | 1.1434839284470568e-12 |
| four_rooms_9 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.04323329045202229 | 0.00035460921815477775 | 1.5987211554602254e-14 | 8.790038441409905e-13 | 8.828493491819245e-13 | 0.0 | 0.04358789967104393 | 0.04358789967105607 | True | 0.0032191004250236516 | 0.0032191004250245485 |
| corridor_64 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.0 | 5.5845106317065074e-11 | 3.197442310920451e-14 | 1.015987976469374e-12 | 9.627854069549358e-12 | 0.0 | 6.550493480972364e-11 | 5.6861094293534446e-11 | True | 2.208684566225705e-12 | 1.917232980227187e-12 |
| four_rooms_9 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.09107846271449205 | 0.0015890525894413088 | 5.329070518200751e-15 | 3.374272573364657e-13 | 8.823164421301044e-12 | 0.0 | 0.09266751531275119 | 0.09266751530427078 | True | 0.006480210528042917 | 0.006480210527449884 |
| corridor_64 | 0.1 | converged_k256_i256 | turn_articulation | 2 | 0.0 | 5.5845106317065074e-11 | 3.197442310920451e-14 | 1.015987976469374e-12 | 9.627854069549358e-12 | 0.0 | 6.550493480972364e-11 | 5.6861094293534446e-11 | True | 2.208684566225705e-12 | 1.917232980227187e-12 |
| four_rooms_9 | 0.1 | converged_k256_i256 | turn_articulation | 16 | 0.03354517780304711 | 0.15637104105985777 | 3.552713678800501e-15 | 6.218864430376619e-13 | 5.680789172402001e-12 | 0.0 | 0.183703908243519 | 0.18991621886352678 | True | 0.01284635717516077 | 0.013280782124911288 |
| corridor_64 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 5.5845106317065074e-11 | 3.197442310920451e-14 | 1.015987976469374e-12 | 9.627854069549358e-12 | 0.0 | 6.550493480972364e-11 | 5.6861094293534446e-11 | True | 2.208684566225705e-12 | 1.917232980227187e-12 |
| four_rooms_9 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.09107846271449205 | 0.0015890525894413088 | 5.329070518200751e-15 | 3.374272573364657e-13 | 8.823164421301044e-12 | 0.0 | 0.09266751531275119 | 0.09266751530427078 | True | 0.006480210528042917 | 0.006480210527449884 |
| open_room_7 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| maze_9 | 0.0 | converged_k256_i256 | endpoints | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| open_room_7 | 0.0 | converged_k256_i256 | turn_articulation | 4 | 0.0 | 1.7763568394002505e-15 | 0.0 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 6.098825148607522e-14 | True | 1.7406296101340607e-16 | 5.976161661460271e-15 |
| maze_9 | 0.0 | converged_k256_i256 | turn_articulation | 8 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.42940285857753185 | 0.0 | 0.0 | 1.7763568394002505e-15 | 0.42940285857753363 | True | 1.7406296101340607e-16 | 0.04207664325871698 |
| open_room_7 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | 0.0 | 0.0 | 1.7763568394002505e-15 | 5.921189464667497e-14 | True | 1.7406296101340607e-16 | 5.802098700446865e-15 |
| maze_9 | 0.0 | converged_k256_i256 | graph_rd_surrogate_joint | 5 | 0.0 | 1.7763568394002505e-15 | 0.0 | 0.0 | 0.0 | 0.0 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | True | 1.7406296101340607e-16 | 1.7406296101340607e-16 |
| open_room_7 | 0.05 | converged_k256_i256 | endpoints | 2 | 0.04973231542109424 | 2.1886492618250486e-11 | 1.7763568394002505e-15 | 4.1770140830767027e-13 | 6.981082378842984e-13 | 0.0 | 0.049732315443677066 | 0.049732315443398435 | True | 0.004641998946546555 | 0.004641998946520547 |
| maze_9 | 0.05 | converged_k256_i256 | endpoints | 2 | 3.552713678800501e-15 | 1.9046098032049485e-11 | 5.329070518200751e-15 | 3.772315927236406e-13 | 8.171241461241152e-13 | 0.0 | 1.98614458213342e-11 | 1.9426882338451928e-11 | True | 1.841273082500453e-12 | 1.8009864865060522e-12 |
| open_room_7 | 0.05 | converged_k256_i256 | turn_articulation | 4 | 0.00382846108703383 | 0.04590385435547972 | 8.881784197001252e-16 | 4.370811353691183e-13 | 1.1617373729677638e-12 | 0.0 | 0.04973231544367529 | 0.049732315442950634 | True | 0.004641998946546389 | 0.00464199894647875 |
| maze_9 | 0.05 | converged_k256_i256 | turn_articulation | 8 | 3.552713678800501e-15 | 1.8765433651424246e-11 | 3.552713678800501e-15 | 0.402055662369396 | 1.0960121699099545e-12 | 0.0 | 1.98614458213342e-11 | 0.402055662388165 | True | 1.841273082500453e-12 | 0.03727292944741364 |
| open_room_7 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.04973231542109424 | 2.1886492618250486e-11 | 1.7763568394002505e-15 | 4.1770140830767027e-13 | 6.981082378842984e-13 | 0.0 | 0.049732315443677066 | 0.049732315443398435 | True | 0.004641998946546555 | 0.004641998946520547 |
| maze_9 | 0.05 | converged_k256_i256 | graph_rd_surrogate_joint | 5 | 3.552713678800501e-15 | 1.8838264281839656e-11 | 3.552713678800501e-15 | 7.451504583459935e-14 | 1.0231815394945443e-12 | 0.0 | 1.98614458213342e-11 | 1.8916332041353056e-11 | True | 1.841273082500453e-12 | 1.7536554650000048e-12 |
| open_room_7 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.10689515935551341 | 4.545519516341301e-11 | 0.0 | 8.431464949961714e-14 | 6.979306022003584e-12 | 0.0 | 0.10689515940794792 | 0.10689515940105293 | True | 0.009472584758283727 | 0.009472584757672724 |
| maze_9 | 0.1 | converged_k256_i256 | endpoints | 2 | 0.0 | 2.5870861009025248e-11 | 3.552713678800501e-15 | 2.982996188545192e-13 | 3.7125857943465235e-12 | 0.0 | 2.958699951705057e-11 | 2.6169160627879766e-11 | True | 2.5870571333914485e-12 | 2.2882047785280758e-12 |
| open_room_7 | 0.1 | converged_k256_i256 | turn_articulation | 4 | 0.01627865195821876 | 0.09061650744518168 | 8.881784197001252e-16 | 2.521774756896521e-13 | 4.547473508864641e-12 | 0.0 | 0.10689515940794792 | 0.10689515940365261 | True | 0.009472584758283727 | 0.009472584757903095 |
| maze_9 | 0.1 | converged_k256_i256 | turn_articulation | 8 | 1.7763568394002505e-15 | 2.282618538629322e-11 | 7.105427357601002e-15 | 0.3727480454960984 | 6.753708703399752e-12 | 0.0 | 2.958699951705057e-11 | 0.3727480455189264 | True | 2.5870571333914485e-12 | 0.032592709833984164 |
| open_room_7 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 2 | 0.10689515935551341 | 4.545519516341301e-11 | 0.0 | 8.431464949961714e-14 | 6.979306022003584e-12 | 0.0 | 0.10689515940794792 | 0.10689515940105293 | True | 0.009472584758283727 | 0.009472584757672724 |
| maze_9 | 0.1 | converged_k256_i256 | graph_rd_surrogate_joint | 7 | 1.7763568394002505e-15 | 1.3709922086491133e-11 | 3.552713678800501e-15 | 1.8196102594340113e-13 | 1.5873524716880638e-11 | 0.0 | 2.958699951705057e-11 | 1.3893659469273934e-11 | True | 2.5870571333914485e-12 | 1.2148474473791414e-12 |

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

## Random-Maze Boundary-Budget Recovery

| map | slip | budget_frac | recovered | recovery_method | minimal_max_splits | minimal_n_boundary | added_vertices_over_failed | max_splits_tested | largest_n_boundary | violation_reduction | best_total_violation | failure_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_maze_15_seed0 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_15_seed0 | 0.1 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_15_seed4 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 2 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_15_seed4 | 0.1 | 0.25 | False |  |  |  |  | 16 | 17 | 2.885656158468919e-10 | 38.863153095861364 | fixed_family_or_probe_plateau |
| random_maze_15_seed8 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_19_seed3 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_19_seed3 | 0.1 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |

## General Finite-MDP Portability Smoke

These rows are adapter/claim-boundary evidence, not a replacement for the main grid compression table. PointMaze is a discretized empirical MDP; Taxi highlights structured state variables that purely spatial boundary selection does not preserve.

| env | source | method | n_rows | best_option_mode | best_n_options | best_target_count | n_states | best_n_boundary | best_state_compression | best_start_gap | best_value_gap_max | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CliffWalking-v1 | gymnasium_toy_text | endpoints | 10 | boundary_targeted | 2 | 8 | 48 | 2 | 24.0 | 10.899096994480836 | 31.363333333333273 | finite-MDP portability smoke |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | 30 | boundary_targeted | 4 | 8 | 48 | 4 | 12.0 | 10.899096994480836 | 30.422433333333274 | finite-MDP portability smoke |
| FrozenLake8x8-v1 | gymnasium_toy_text | endpoints | 10 | primitive | 4 | 8 | 64 | 12 | 5.333333333333333 | 0.07444398742335054 | 0.10453031682674943 | finite-MDP portability smoke |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | 30 | primitive | 4 | 16 | 64 | 14 | 4.571428571428571 | 0.06656794225053705 | 0.10453031682674943 | finite-MDP portability smoke |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | endpoints | 10 | boundary_targeted | 11 | 8 | 270 | 11 | 24.545454545454547 | 0.0 | 0.931588 | finite-MDP portability smoke |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | 30 | boundary_targeted | 11 | 8 | 270 | 11 | 24.545454545454547 | 0.0 | 0.931588 | finite-MDP portability smoke |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | endpoints | 10 | boundary_targeted | 4 | 8 | 1039 | 4 | 259.75 | 0.0 | 0.9263499999999999 | finite-MDP portability smoke |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | 30 | boundary_targeted | 6 | 8 | 1039 | 6 | 173.16666666666666 | 0.0 | 0.8128599999999999 | finite-MDP portability smoke |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | endpoints | 10 | boundary_targeted | 2 | 8 | 37 | 2 | 18.5 | 0.0 | 0.817225 | finite-MDP portability smoke |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | 30 | boundary_targeted | 4 | 8 | 37 | 4 | 9.25 | 0.0 | 0.817225 | finite-MDP portability smoke |
| PointMaze-umaze-b3 | discretized_point_maze | endpoints | 10 | boundary_targeted | 18 | 8 | 63 | 18 | 3.5 | 10.830865993545386 | 12.003085793800107 | finite-MDP portability smoke |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | 30 | primitive | 8 | 32 | 63 | 25 | 2.52 | 3.636979786111949 | 5.47547750490347 | finite-MDP portability smoke |
| Taxi-v4 | gymnasium_toy_text | endpoints | 10 | boundary_targeted | 20 | 8 | 500 | 20 | 25.0 | 26.63745552465558 | 51.733333333333285 | structured task-variable failure |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | 30 | boundary_targeted | 32 | 32 | 500 | 32 | 15.625 | 24.433972176265822 | 51.733333333333285 | structured task-variable failure |

## External Environment Multi-Seed Aggregate

A low group-risk violation is not treated as a value guarantee: held-out normalized value gaps are reported next to group feasibility.

| env | source | method | option_mode | target_count | n_seeds | median_n_boundary | median_state_compression_ratio | median_normalized_start_gap | max_normalized_start_gap | median_normalized_value_gap_max | group_feasible_rate | median_construction_time_sec | median_smdp_eval_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CliffWalking-v1 | gymnasium_toy_text | endpoints | boundary_targeted | 8 | 5 | 2.0 | 24.0 | 1.0 | 1.0 | 2.877608424736037 | nan | 5.074706859886646e-05 | 0.008879981003701687 |
| CliffWalking-v1 | gymnasium_toy_text | endpoints | primitive | 8 | 5 | 2.0 | 24.0 | 2.0583573434554974 | 2.0583573434554974 | 2.877608424736037 | nan | 4.19949647039175e-05 | 0.10540934500750154 |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | boundary_targeted | 16 | 5 | 4.0 | 12.0 | 1.0 | 1.0 | 2.791280171993956 | 1.0 | 0.027684575994499028 | 0.013196958927437663 |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | boundary_targeted | 32 | 5 | 4.0 | 12.0 | 1.0 | 1.0 | 2.791280171993956 | 1.0 | 0.027421769103966653 | 0.013211334007792175 |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | boundary_targeted | 8 | 5 | 4.0 | 12.0 | 1.0 | 1.0 | 2.791280171993956 | 1.0 | 0.027664633002132177 | 0.013228351017460227 |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | primitive | 16 | 5 | 4.0 | 12.0 | 2.0583573434554974 | 2.0583573434554974 | 2.8776084245175624 | 1.0 | 0.027709992020390928 | 0.02477946109138429 |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | primitive | 32 | 5 | 4.0 | 12.0 | 2.0583573434554974 | 2.0583573434554974 | 2.8776084245175624 | 1.0 | 0.027487514074891806 | 0.024643660057336092 |
| CliffWalking-v1 | gymnasium_toy_text | green_group_rd | primitive | 8 | 5 | 4.0 | 12.0 | 2.0583573434554974 | 2.0583573434554974 | 2.8776084245175624 | 1.0 | 0.028203184949234128 | 0.0247957028914243 |
| FrozenLake8x8-v1 | gymnasium_toy_text | endpoints | boundary_targeted | 8 | 5 | 12.0 | 5.333333333333333 | 0.09729254539441845 | 0.09729254539441845 | 0.10453031682674943 | nan | 6.565498188138008e-05 | 0.052391548990271986 |
| FrozenLake8x8-v1 | gymnasium_toy_text | endpoints | primitive | 8 | 5 | 12.0 | 5.333333333333333 | 0.07444398742335054 | 0.07444398742335054 | 0.10453031682674943 | nan | 4.505098331719637e-05 | 0.08430217008572072 |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | boundary_targeted | 16 | 5 | 14.0 | 4.571428571428571 | 0.08263560851604991 | 0.08263560851604991 | 0.10453031682674943 | 1.0 | 0.08691059297416359 | 0.05981696303933859 |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | boundary_targeted | 32 | 5 | 14.0 | 4.571428571428571 | 0.08263560851604991 | 0.08263560851604991 | 0.10453031682674943 | 1.0 | 0.08668654598295689 | 0.05930814705789089 |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | boundary_targeted | 8 | 5 | 12.0 | 5.333333333333333 | 0.09729254539441845 | 0.09729254539441845 | 0.10453031682674943 | 0.0 | 0.06346794799901545 | 0.0495109420735389 |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | primitive | 16 | 5 | 14.0 | 4.571428571428571 | 0.06656794225053705 | 0.06656794225053705 | 0.10453031682674943 | 1.0 | 0.08627941098529845 | 0.009528514929115772 |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | primitive | 32 | 5 | 14.0 | 4.571428571428571 | 0.06656794225053705 | 0.06656794225053705 | 0.10453031682674943 | 1.0 | 0.08666974201332778 | 0.009571961010806262 |
| FrozenLake8x8-v1 | gymnasium_toy_text | green_group_rd | primitive | 8 | 5 | 12.0 | 5.333333333333333 | 0.07444398742335054 | 0.07444398742335054 | 0.10453031682674943 | 0.0 | 0.06311196705792099 | 0.00906582793686539 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | endpoints | boundary_targeted | 8 | 5 | 11.0 | 24.545454545454547 | 0.0 | 0.0 | 0.931588 | nan | 6.359897088259459e-05 | 0.5298988410504535 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | endpoints | primitive | 8 | 5 | 11.0 | 24.545454545454547 | 0.7082221314698889 | 0.811981110404789 | 0.931588 | nan | 6.627500988543034e-05 | 0.09488356101792306 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 16 | 5 | 13.0 | 20.76923076923077 | 0.0 | 0.0 | 0.931588 | 1.0 | 0.1685796930687502 | 0.6486557429889217 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 32 | 5 | 13.0 | 20.76923076923077 | 0.0 | 0.0 | 0.931588 | 1.0 | 0.17268406390212476 | 0.6121030349750072 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 8 | 5 | 11.0 | 24.545454545454547 | 0.0 | 0.0 | 0.931588 | 0.0 | 0.1535543849458918 | 0.5232129009673372 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 16 | 5 | 13.0 | 20.76923076923077 | 0.7082221314698889 | 0.811981110404789 | 0.931588 | 1.0 | 0.17194953106809407 | 0.02453858300577849 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 32 | 5 | 13.0 | 20.76923076923077 | 0.7082221314698889 | 0.811981110404789 | 0.931588 | 1.0 | 0.16896460391581059 | 0.02484096889384091 |
| MiniGrid-DoorKey-5x5-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 8 | 5 | 11.0 | 24.545454545454547 | 0.7082221314698889 | 0.811981110404789 | 0.931588 | 0.0 | 0.14678379299584776 | 0.02518814499489963 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | endpoints | boundary_targeted | 8 | 5 | 4.0 | 259.75 | 0.0 | 0.0 | 0.85651 | nan | 7.643201388418674e-05 | 2.847515505971387 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | endpoints | primitive | 8 | 5 | 4.0 | 259.75 | 0.6126628047589716 | 0.9525399999999999 | 0.85651 | nan | 8.382904343307018e-05 | 0.2744178690481931 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 16 | 5 | 7.0 | 148.42857142857142 | 0.0 | 0.0 | 0.85651 | 1.0 | 0.5459457989782095 | 4.69235029106494 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 32 | 5 | 7.0 | 148.42857142857142 | 0.0 | 0.0 | 0.85651 | 1.0 | 0.5894884510198608 | 4.576733905007131 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 8 | 5 | 7.0 | 148.42857142857142 | 0.0 | 0.0 | 0.85651 | 0.8 | 0.5408857929287478 | 4.610688449000008 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 16 | 5 | 7.0 | 148.42857142857142 | 0.5647033800034252 | 0.8454546335499998 | 0.85651 | 1.0 | 0.6097538589965552 | 0.1730381160741672 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 32 | 5 | 7.0 | 148.42857142857142 | 0.5647033800034252 | 0.8454546335499998 | 0.85651 | 1.0 | 0.561460305005312 | 0.1675814390182495 |
| MiniGrid-FourRooms-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 8 | 5 | 7.0 | 148.42857142857142 | 0.5647033800034252 | 0.8454546335499998 | 0.85651 | 0.8 | 0.5558886720100418 | 0.1770183949265629 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | endpoints | boundary_targeted | 8 | 5 | 5.0 | 12.8 | 0.0 | 0.0 | 0.817225 | nan | 5.294999573379755e-05 | 0.03052137792110443 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | endpoints | primitive | 8 | 5 | 5.0 | 12.8 | 0.7017789141526823 | 0.7428049322304998 | 0.817225 | nan | 4.8977090045809746e-05 | 0.08089721703436226 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 16 | 5 | 7.0 | 9.142857142857142 | 0.0 | 0.0 | 0.817225 | 1.0 | 0.03238864603918046 | 0.037980976048856974 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 32 | 5 | 7.0 | 9.142857142857142 | 0.0 | 0.0 | 0.817225 | 1.0 | 0.031725988956168294 | 0.03786594793200493 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | boundary_targeted | 8 | 5 | 7.0 | 9.142857142857142 | 0.0 | 0.0 | 0.817225 | 1.0 | 0.038369519053958356 | 0.03812813700642437 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 16 | 5 | 7.0 | 9.142857142857142 | 0.7017789141526823 | 0.7428049322304998 | 0.817225 | 1.0 | 0.03259147109929472 | 0.013236240018159151 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 32 | 5 | 7.0 | 9.142857142857142 | 0.7017789141526823 | 0.7428049322304998 | 0.817225 | 1.0 | 0.031650900025852025 | 0.012998013058677316 |
| MiniGrid-MultiRoom-N2-S4-v0 | minigrid_symbolic_bfs | green_group_rd | primitive | 8 | 5 | 7.0 | 9.142857142857142 | 0.7017789141526823 | 0.7428049322304998 | 0.817225 | 1.0 | 0.039442311972379684 | 0.013400578987784684 |
| PointMaze-umaze-b3 | discretized_point_maze | endpoints | boundary_targeted | 8 | 5 | 18.0 | 3.5 | 0.9916111794931917 | 0.9988366333413018 | 1.0960836406882126 | nan | 5.713605787605047e-05 | 0.11059487599413842 |
| PointMaze-umaze-b3 | discretized_point_maze | endpoints | primitive | 8 | 5 | 18.0 | 3.5 | 1.8993322176259009 | 2.0457367856369038 | 2.1965306316450066 | nan | 4.988396540284157e-05 | 0.1383222019067034 |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | boundary_targeted | 16 | 5 | 18.0 | 3.5 | 0.9916111794931917 | 0.9988366333413018 | 1.0960836406882126 | 0.0 | 0.05379154998809099 | 0.10474116797558963 |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | boundary_targeted | 32 | 5 | 25.0 | 2.52 | 0.9916111794931917 | 0.9988366333413018 | 1.0960836406882126 | 1.0 | 0.14746399805881083 | 0.149270505993627 |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | boundary_targeted | 8 | 5 | 18.0 | 3.5 | 0.9916111794931917 | 0.9988366333413018 | 1.0960836406882126 | 0.0 | 0.05497801105957478 | 0.10363372694700956 |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | primitive | 16 | 5 | 18.0 | 3.5 | 1.8993322176259009 | 2.0457367856369038 | 2.1965306316450066 | 0.0 | 0.05333955294918269 | 0.041828243993222713 |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | primitive | 32 | 5 | 25.0 | 2.52 | 0.3223000215255633 | 0.3597612324959681 | 0.41052689045578694 | 1.0 | 0.14556052500847727 | 0.01707182195968926 |
| PointMaze-umaze-b3 | discretized_point_maze | green_group_rd | primitive | 8 | 5 | 18.0 | 3.5 | 1.8993322176259009 | 2.0457367856369038 | 2.1965306316450066 | 0.0 | 0.05574551899917424 | 0.04203174391295761 |
| Taxi-v4 | gymnasium_toy_text | endpoints | boundary_targeted | 8 | 5 | 20.0 | 25.0 | 1.7361806324795588 | 1.7361806324795588 | 3.371884048902744 | nan | 8.003297261893749e-05 | 2.661186524084769 |
| Taxi-v4 | gymnasium_toy_text | endpoints | primitive | 8 | 5 | 20.0 | 25.0 | 2.414325972098052 | 2.414325972098052 | 3.371884048902744 | nan | 7.268402259796858e-05 | 0.1329685339005664 |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | boundary_targeted | 16 | 5 | 20.0 | 25.0 | 1.7361806324795588 | 1.7361806324795588 | 3.371884048902744 | 0.0 | 0.21548287209589034 | 2.5713148430222645 |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | boundary_targeted | 32 | 5 | 32.0 | 15.625 | 1.592561617895959 | 1.592561617895959 | 3.371884048902744 | 0.0 | 0.539189375936985 | 4.082966216956265 |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | boundary_targeted | 8 | 5 | 20.0 | 25.0 | 1.7361806324795588 | 1.7361806324795588 | 3.371884048902744 | 0.0 | 0.22713032399769872 | 2.560850227950141 |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | primitive | 16 | 5 | 20.0 | 25.0 | 2.414325972098052 | 2.414325972098052 | 3.371884048902744 | 0.0 | 0.21628349495586008 | 0.059662982006557286 |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | primitive | 32 | 5 | 32.0 | 15.625 | 2.4143259720862766 | 2.4143259720862766 | 3.371884048902744 | 0.0 | 0.5452023379039019 | 0.06693917594384402 |
| Taxi-v4 | gymnasium_toy_text | green_group_rd | primitive | 8 | 5 | 20.0 | 25.0 | 2.414325972098052 | 2.414325972098052 | 3.371884048902744 | 0.0 | 0.22799497202504426 | 0.06478620099369437 |

## Fair Budget Frontier

| comparison_protocol | method_group | n_rows | pareto_rows | median_rate_budget_boundary_frac | median_state_compression_ratio | median_start_gap | median_normalized_start_gap | median_hidden_audit | median_normalized_hidden_audit | mean_group_feasible_rate | median_total_speedup | median_success_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abstraction_baseline_comparison | abstraction:model_minimization | 120 | 80 | 0.03603 | 28.25 | nan | 0.7432 | nan | nan | nan | 0.000518 | nan |
| abstraction_baseline_comparison | abstraction:qstar_oracle | 96 | 2 | 0.1652 | 6.358 | nan | 0.8401 | nan | nan | nan | 0.298 | nan |
| abstraction_baseline_comparison | reduction:policy_kron_oracle | 96 | 23 | 0.1652 | 6.358 | nan | 0.0 | nan | nan | nan | 0.3183 | nan |
| core_benchmark | full_mdp | 10 | 3 | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | nan | 1 | 1 |
| core_benchmark | option_baseline:bottleneck | 10 | 1 | 0.1875 | 5.333 | 3.5269565046291973e-12 | 1.05808695138876e-13 | 0.4533 | 0.009252 | nan | 0.3402 | 1 |
| core_benchmark | option_baseline:coverage | 10 | 1 | 0.1875 | 5.333 | 9.9333874459262e-12 | 2.9800162337778625e-13 | 0.0 | 0.0 | nan | 0.4021 | 1 |
| core_benchmark | option_baseline:eigen | 10 | 1 | 0.1875 | 5.333 | 1.794120407794253e-12 | 5.3823612233827635e-14 | 0.0 | 0.0 | nan | 0.3368 | 1 |
| core_benchmark | option_baseline:random | 10 | 1 | 0.1875 | 5.333 | 2.4424906541753444e-12 | 7.32747196252604e-14 | 0.0 | 0.0 | nan | 0.3465 | 1 |
| core_benchmark | ours:group_rd | 10 | 5 | 0.09526 | 10.5 | 1.794120407794253e-12 | 5.3823612233827635e-14 | 0.4534 | 0.009252 | 0.9 | 0.01116 | 1 |
| core_benchmark | ours:rd_graph | 20 | 19 | 0.09375 | 12 | 9.564793401750649e-12 | 2.8694380205251965e-13 | 4.737e-08 | 1.528e-09 | nan | 0.1836 | 1 |
| group_constrained_adaptive | baseline:endpoints | 6 | 6 | 0.01923 | 52 | 7.741e-09 | 2.3223636347324845e-10 | 194.3 | 194.3 | 0.0 | 2.759 | nan |
| group_constrained_adaptive | ours:group_rd | 12 | 10 | 0.03365 | 30.33 | 1.366e-07 | 4.099e-09 | 0.0 | 0.0 | 1 | 0.01761 | nan |
| large_scale_compression | baseline:dense_turn | 27 | 27 | 0.007812 | 128 | 3.228e-09 | 9.684306689905504e-11 | 0.0 | 0.0 | nan | 0.8971 | nan |
| large_scale_compression | baseline:endpoints | 27 | 27 | 0.003906 | 256 | 3.228e-09 | 9.684285373623431e-11 | 1 | 0.001251 | nan | 1.452 | nan |
| large_scale_compression | option_baseline:bottleneck | 27 | 8 | 0.04492 | 22.26 | 1.027e-07 | 3.082e-09 | 0.5677 | 0.0006445 | nan | 0.06183 | nan |
| large_scale_compression | option_baseline:coverage | 27 | 7 | 0.04492 | 22.26 | 1.15e-06 | 3.451e-08 | 0.0 | 0.0 | nan | 0.06925 | nan |
| large_scale_compression | ours:rd_graph | 27 | 27 | 0.003906 | 256 | 3.228e-09 | 9.684306689905504e-11 | 1 | 0.001251 | nan | 0.1819 | nan |
| option_baseline_frontier | baseline:dense_turn | 24 | 22 | 0.01276 | 92.25 | 1.0536993499954406e-10 | 3.227693031267288e-12 | 0.0 | 0.0 | 1 | nan | 1 |
| option_baseline_frontier | baseline:endpoints | 24 | 24 | 0.00418 | 240.2 | 1.0555112339716288e-10 | 3.2395713581639985e-12 | 1.239 | 0.001685 | 1 | nan | 1 |
| option_baseline_frontier | option_baseline:bottleneck | 144 | 21 | 0.02874 | 34.83 | 1.0521006288399803e-10 | 3.1664945926805514e-12 | 0.7206 | 0.001106 | 1 | nan | 1 |
| option_baseline_frontier | option_baseline:coverage | 144 | 14 | 0.02874 | 34.83 | 1.0555467611084168e-10 | 3.2394717298270782e-12 | 0.0 | 0.0 | 1 | nan | 1 |
| option_baseline_frontier | option_baseline:eigen | 144 | 4 | 0.02874 | 34.83 | 1.000017846308765e-10 | 3.009625736390688e-12 | 0.6604 | 0.0009883 | 1 | nan | 1 |
| option_baseline_frontier | option_baseline:random | 144 | 14 | 0.02874 | 34.83 | 9.975664738703927e-11 | 3.0648393050418303e-12 | 0.7206 | 0.001179 | 1 | nan | 1 |
| option_baseline_frontier | ours:rd_graph | 24 | 24 | 0.004428 | 229 | 1.0537348771322286e-10 | 3.227685558292771e-12 | 1 | 0.001685 | 1 | nan | 1 |
| random_maze_generalization | baseline:endpoints | 180 | 179 | 0.02062 | 48.5 | 2.915e-08 | 8.743918655795831e-10 | 233.2 | 233.2 | 0.0 | 2.383 | nan |
| random_maze_generalization | ours:group_rd | 180 | 180 | 0.03093 | 32.33 | 2.469e-07 | 7.407e-09 | 0.0 | 0.0 | 0.9611 | 0.05321 | nan |

## Epsilon-Constrained Frontier

Canonical slice: normalized value gap <= `0.01` and normalized audit <= `0.001`. Coverage is reported before compression or speedup.

| comparison_protocol | method_group | value_epsilon | audit_epsilon | n_cases_available | n_cases_feasible | constraint_coverage_rate | paired_case_count | median_rate_budget_boundary_frac | median_state_compression_ratio | state_compression_ci95_low | state_compression_ci95_high | median_total_speedup | total_speedup_ci95_low | total_speedup_ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abstraction_baseline_comparison | abstraction:model_minimization | 0.01 | 0.001 | 24 | 0 | 0.0 | 0 | nan | nan | nan | nan | nan | nan | nan |
| abstraction_baseline_comparison | abstraction:qstar_oracle | 0.01 | 0.001 | 24 | 0 | 0.0 | 0 | nan | nan | nan | nan | nan | nan | nan |
| abstraction_baseline_comparison | reduction:policy_kron_oracle | 0.01 | 0.001 | 24 | 0 | 0.0 | 0 | nan | nan | nan | nan | nan | nan | nan |
| core_benchmark | full_mdp | 0.01 | 0.001 | 10 | 10 | 1.0 | 4 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| core_benchmark | option_baseline:bottleneck | 0.01 | 0.001 | 10 | 5 | 0.5 | 4 | 0.1875 | 5.333333333333333 | 4.0 | 7.0 | 0.4432684691573722 | 0.1209212379644871 | 0.8068607489133391 |
| core_benchmark | option_baseline:coverage | 0.01 | 0.001 | 10 | 6 | 0.6 | 4 | 0.1875 | 5.333333333333333 | 4.0 | 7.0 | 0.48297684945559666 | 0.2999852255162242 | 0.9410277068326185 |
| core_benchmark | option_baseline:eigen | 0.01 | 0.001 | 10 | 6 | 0.6 | 4 | 0.1875 | 5.333333333333333 | 4.0 | 6.357142857142858 | 0.42606623282529543 | 0.10498495929872148 | 0.7530947693393724 |
| core_benchmark | option_baseline:random | 0.01 | 0.001 | 10 | 6 | 0.6 | 4 | 0.1875 | 5.333333333333333 | 4.0 | 6.357142857142858 | 0.4428784787101792 | 0.11669254313303093 | 0.9344360123350957 |
| core_benchmark | ours:group_rd | 0.01 | 0.001 | 10 | 5 | 0.5 | 4 | 0.09375 | 10.666666666666666 | 5.333333333333333 | 16.333333333333332 | 0.014372218194298394 | 0.007836302824100175 | 0.018535375510118014 |
| core_benchmark | ours:rd_graph | 0.01 | 0.001 | 10 | 6 | 0.6 | 4 | 0.125 | 8.0 | 6.2 | 16.0 | 0.2596212793403313 | 0.05122000631819744 | 0.3116607329741538 |
| group_constrained_adaptive | baseline:endpoints | 0.01 | 0.001 | 6 | 0 | 0.0 | 0 | nan | nan | nan | nan | nan | nan | nan |
| group_constrained_adaptive | ours:group_rd | 0.01 | 0.001 | 6 | 6 | 1.0 | 0 | 0.03365384615384616 | 30.333333333333332 | 23.666666666666668 | 42.0 | 0.0392852839884518 | 0.015849520638755603 | 0.05347956680833867 |
| large_scale_compression | baseline:dense_turn | 0.01 | 0.001 | 27 | 27 | 1.0 | 13 | 0.0078125 | 128.0 | 25.25 | 256.0 | 0.8970534465197718 | 0.2142066125878501 | 4.6916178629329615 |
| large_scale_compression | baseline:endpoints | 0.01 | 0.001 | 27 | 13 | 0.48148148148148145 | 13 | 0.003472222222222222 | 288.0 | 256.0 | 512.0 | 5.639278259352069 | 2.098814450959034 | 6.665842752047791 |
| large_scale_compression | option_baseline:bottleneck | 0.01 | 0.001 | 27 | 15 | 0.5555555555555556 | 13 | 0.041666666666666664 | 24.0 | 22.26086956521739 | 32.0 | 0.3464398101247238 | 0.0564238039129172 | 0.5796768533874868 |
| large_scale_compression | option_baseline:coverage | 0.01 | 0.001 | 27 | 21 | 0.7777777777777778 | 13 | 0.041666666666666664 | 24.0 | 22.26086956521739 | 29.161290322580644 | 0.0922426642241242 | 0.0691332400335737 | 0.5096832064584026 |
| large_scale_compression | ours:rd_graph | 0.01 | 0.001 | 27 | 13 | 0.48148148148148145 | 13 | 0.003472222222222222 | 288.0 | 256.0 | 512.0 | 0.3404145664099412 | 0.2289360792891061 | 0.3555614097285011 |
| option_baseline_frontier | baseline:dense_turn | 0.01 | 0.001 | 24 | 24 | 1.0 | 10 | 0.012755807522123894 | 92.25 | 25.25 | 144.0 | nan | nan | nan |
| option_baseline_frontier | baseline:endpoints | 0.01 | 0.001 | 24 | 10 | 0.4166666666666667 | 10 | 0.00390625 | 256.0 | 128.0 | 512.0 | nan | nan | nan |
| option_baseline_frontier | option_baseline:bottleneck | 0.01 | 0.001 | 24 | 13 | 0.5416666666666666 | 10 | 0.0078125 | 128.0 | 64.0 | 144.0 | nan | nan | nan |
| option_baseline_frontier | option_baseline:coverage | 0.01 | 0.001 | 24 | 18 | 0.75 | 10 | 0.011061946902654867 | 94.16666666666666 | 64.0 | 136.0 | nan | nan | nan |
| option_baseline_frontier | option_baseline:eigen | 0.01 | 0.001 | 24 | 13 | 0.5416666666666666 | 10 | 0.0078125 | 128.0 | 64.0 | 226.0 | nan | nan | nan |
| option_baseline_frontier | option_baseline:random | 0.01 | 0.001 | 24 | 13 | 0.5416666666666666 | 10 | 0.0078125 | 128.0 | 64.0 | 144.0 | nan | nan | nan |
| option_baseline_frontier | ours:rd_graph | 0.01 | 0.001 | 24 | 10 | 0.4166666666666667 | 10 | 0.00390625 | 256.0 | 128.0 | 512.0 | nan | nan | nan |
| random_maze_generalization | baseline:endpoints | 0.01 | 0.001 | 180 | 0 | 0.0 | 0 | nan | nan | nan | nan | nan | nan | nan |
| random_maze_generalization | ours:group_rd | 0.01 | 0.001 | 180 | 173 | 0.9611111111111111 | 0 | 0.030927835051546393 | 32.333333333333336 | 24.25 | 32.333333333333336 | 0.05342590790975046 | 0.05224407074496018 | 0.05441328163289956 |

## Multi-Task And Edge Reward Compression

Edge-reward speedups in this legacy artifact use dense NumPy full-state VI. They support amortization and representation compression, but are not reported as wins over the matched sparse-vectorized planner. Gaps use the discounted unit-reward bound when the original shard did not record a task-specific value scale.

| source | method_or_variant | task_count | n_rows | median_amortized_speedup | best_amortized_speedup | median_planning_only_speedup | median_break_even_tasks | max_start_gap | max_normalized_start_gap | max_normalized_boundary_gap | median_state_compression | median_goal_interface | median_goal_policies | runtime_denominator |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| amortized_multitask | betweenness_sqrt | 1 | 8 | 0.004569 | 0.01453 | 0.05651 | nan | 0.0 |  |  | 4.107 |  |  |  |
| amortized_multitask | betweenness_sqrt | 10 | 8 | 0.02487 | 0.04607 | 0.06099 | nan | 0.0 |  |  | 4.107 |  |  |  |
| amortized_multitask | betweenness_sqrt | 100 | 8 | 0.04586 | 0.06165 | 0.0618 | nan | 0.0 |  |  | 4.107 |  |  |  |
| amortized_multitask | betweenness_sqrt | 25 | 8 | 0.03362 | 0.0545 | 0.06209 | nan | 0.0 |  |  | 4.107 |  |  |  |
| amortized_multitask | betweenness_sqrt | 5 | 8 | 0.01844 | 0.0368 | 0.06061 | nan | 0.0 |  |  | 4.107 |  |  |  |
| amortized_multitask | betweenness_sqrt | 50 | 8 | 0.03988 | 0.05769 | 0.0637 | nan | 0.0 |  |  | 4.107 |  |  |  |
| amortized_multitask | endpoints | 1 | 8 | 0.006091 | 0.01745 | 0.07745 | nan | 0.0 |  |  | 4.757 |  |  |  |
| amortized_multitask | endpoints | 10 | 8 | 0.03262 | 0.05419 | 0.08644 | nan | 0.0 |  |  | 4.757 |  |  |  |
| amortized_multitask | endpoints | 100 | 8 | 0.07647 | 0.08873 | 0.08712 | nan | 0.0 |  |  | 4.757 |  |  |  |
| amortized_multitask | endpoints | 25 | 8 | 0.04367 | 0.06798 | 0.08855 | nan | 0.0 |  |  | 4.757 |  |  |  |
| amortized_multitask | endpoints | 5 | 8 | 0.02507 | 0.04264 | 0.089 | nan | 0.0 |  |  | 4.757 |  |  |  |
| amortized_multitask | endpoints | 50 | 8 | 0.05675 | 0.075 | 0.08876 | nan | 0.0 |  |  | 4.757 |  |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 1 | 8 | 0.002292 | 0.01934 | 0.07254 | nan | 0.0 |  |  | 4.539 |  |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 10 | 8 | 0.01955 | 0.07091 | 0.08575 | nan | 0.0 |  |  | 4.539 |  |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 100 | 8 | 0.07412 | 0.09775 | 0.09113 | nan | 0.0 |  |  | 4.539 |  |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 25 | 8 | 0.03915 | 0.08417 | 0.08911 | nan | 0.0 |  |  | 4.539 |  |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 5 | 8 | 0.01075 | 0.0574 | 0.08141 | nan | 0.0 |  |  | 4.539 |  |  |  |
| amortized_multitask | graph_rd_surrogate_joint | 50 | 8 | 0.05813 | 0.08834 | 0.09289 | nan | 0.0 |  |  | 4.539 |  |  |  |
| amortized_multitask | turn_articulation | 1 | 8 | 0.003293 | 0.0223 | 0.06958 | nan | 0.0 |  |  | 4.354 |  |  |  |
| amortized_multitask | turn_articulation | 10 | 8 | 0.02051 | 0.06919 | 0.08252 | nan | 0.0 |  |  | 4.354 |  |  |  |
| amortized_multitask | turn_articulation | 100 | 8 | 0.05555 | 0.08427 | 0.07977 | nan | 0.0 |  |  | 4.354 |  |  |  |
| amortized_multitask | turn_articulation | 25 | 8 | 0.03171 | 0.08073 | 0.08072 | nan | 0.0 |  |  | 4.354 |  |  |  |
| amortized_multitask | turn_articulation | 5 | 8 | 0.0142 | 0.05856 | 0.08259 | nan | 0.0 |  |  | 4.354 |  |  |  |
| amortized_multitask | turn_articulation | 50 | 8 | 0.04114 | 0.08447 | 0.08071 | nan | 0.0 |  |  | 4.354 |  |  |  |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 1 | 32 | 0.3835 | 1.486 | 286.1 | 3 | 13.38 | 0.4015 | 0.94 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 10 | 32 | 4.218 | 13.45 | 348.7 | 2 | 30.88 | 0.9264 | 0.94 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 100 | 32 | 35.39 | 108.4 | 305.2 | 3 | 30.88 | 0.9264 | 0.9425 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 25 | 32 | 9.849 | 33.77 | 315.7 | 3 | 30.88 | 0.9264 | 0.94 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 5 | 32 | 1.914 | 6.684 | 292 | 2.5 | 30.88 | 0.9264 | 0.94 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_edge_reward_kernel | 50 | 32 | 19.57 | 60.35 | 307.8 | 3 | 30.88 | 0.9264 | 0.9408 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 1 | 16 | 0.09172 | 0.4865 | 0.3755 | 7 | 27.44 | 0.8233 | 0.8506 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 10 | 16 | 0.2882 | 1.743 | 0.387 | 6.5 | 30.09 | 0.9026 | 0.9351 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 100 | 16 | 0.3815 | 2.78 | 0.3957 | 5.5 | 30.2 | 0.906 | 0.9366 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 25 | 16 | 0.3356 | 2.18 | 0.3847 | 6.5 | 30.09 | 0.9026 | 0.9357 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 5 | 16 | 0.225 | 1.281 | 0.3793 | 6.5 | 30.09 | 0.9026 | 0.9351 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_event_hit_kernel | 50 | 16 | 0.37 | 2.562 | 0.3975 | 6.5 | 30.09 | 0.9026 | 0.9357 | 173 | 0.0 | 0.0 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 1 | 16 | 0.0841 | 0.4573 | 0.2742 | 9 | 0.2569 | 0.007707 | 0.01323 | 173 | 2 | 1 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 10 | 16 | 0.2196 | 1.363 | 0.2719 | 30 | 0.5018 | 0.01505 | 0.01505 | 173 | 20 | 10 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 100 | 16 | 0.273 | 1.823 | 0.2801 | 229 | 0.5018 | 0.01505 | 0.01514 | 173 | 200 | 100 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 25 | 16 | 0.2475 | 1.589 | 0.2734 | 63.5 | 0.5018 | 0.01505 | 0.01513 | 173 | 50 | 25 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 5 | 16 | 0.1841 | 1.068 | 0.2741 | 19 | 0.3618 | 0.01085 | 0.0143 | 173 | 10 | 5 | legacy_dense_numpy_full_vi |
| edge_reward_kernel_multitask | fixed_B_goal_conditioned_event_options | 50 | 16 | 0.2672 | 1.716 | 0.2811 | 118 | 0.5018 | 0.01505 | 0.01513 | 173 | 100 | 50 | legacy_dense_numpy_full_vi |

## Failure Modes

| failure_mode | evidence | n_rows | endpoint_feasible_rate | robust_feasible_rate | max_endpoint_violation | max_robust_violation | max_ambiguous_set_size | tie_set_certified_rate | max_tie_aware_total_speedup | event_kernel_max_gap | event_kernel_max_normalized_gap | goal_conditioned_max_gap | goal_conditioned_max_normalized_gap | goal_conditioned_median_break_even | goal_conditioned_best_speedup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_soft_over_split_or_hidden_boundary | group constraints expose endpoint infeasibility while incremental/group RD removes group violation | 6 | 0.0 | 1 | 233.2 | 0.0 |  |  |  |  |  |  |  |  |  |
| corridor_top_set_tie | long corridors create large epsilon/tie sets; tie-aware certificate reports cheap top-set exact fallback separately | 45 |  |  |  |  | 0.0 | nan | 10.49 |  |  |  |  |  |  |
| terminal_interior_goal_event_gap | fixed-B event kernels expose option/boundary restriction bias; goal-conditioned event options reduce gap but add query-time interface cost | 192 |  |  |  |  |  |  |  | 30.2 | 0.906 | 0.5018 | 0.01505 | 58.5 | 1.823 |

## Solver Validity Aggregate

| solver | beam_width | oracle_pool_mode | oracle_complete_candidate_universe | n_rows | boundary_match_rate | zero_total_violation_gap_rate | feasible_decision_match_rate | median_selection_time_sec | median_oracle_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actual_refine | 1 | all | True | 315 | 0.9841 | 0.9841 | 0.9841 | 0.4794 | 0.5534 |
| actual_refine | 2 | all | True | 315 | 0.9873 | 0.9873 | 0.9873 | 0.5247 | 0.5534 |
| actual_refine | 4 | all | True | 315 | 1 | 1 | 1 | 0.5222 | 0.5534 |
| actual_refine | 8 | all | True | 315 | 1 | 1 | 1 | 0.5183 | 0.5534 |
| operator | 1 | all | True | 315 | 0.01905 | 0.01905 | 0.2 | 0.09513 | 0.5534 |
| operator | 2 | all | True | 315 | 0.8286 | 0.981 | 0.981 | 0.2293 | 0.5534 |
| operator | 4 | all | True | 315 | 0.8317 | 0.9841 | 0.9841 | 0.2285 | 0.5534 |
| operator | 8 | all | True | 315 | 0.8476 | 1 | 1 | 0.2286 | 0.5534 |

## Discovery Profile Aggregate

| mode | n_rows | median_wall_time_sec | median_speedup_vs_full_recompute | max_speedup_vs_full_recompute | median_probe_green_kernel_time_sec | median_probe_operator_delta_time_sec | median_full_recompute_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cached_incremental_first | 6 | 0.3617 | 4.74 | 5.603 | 0.1236 | 0.108 | nan | 0.0003442 | 0.0 |
| cached_incremental_hit | 6 | 0.0003545 | 4776 | 7519 | 0.0 | 0.0 | nan | 0.0002474 | 1 |
| current_frozen_operator | 6 | 0.3614 | 4.736 | 5.608 | 0.1233 | 0.108 | nan | 0.0003723 | 0.0 |
| full_recompute | 6 | 1.691 | 1 | 1 | 0.125 | 0.1118 | 1.325 | 0.0003575 | 0.0 |

## Hybrid Discovery Acceleration

| source | method | top_k | n_rows | feasible_rate | median_n_boundary | median_selection_time_sec | median_proposal_time_sec | median_refine_time_sec | median_kernel_time_sec | median_upfront_time_sec | median_total_speedup | best_total_speedup | median_break_even_tasks | max_group_total_violation | max_start_gap | mean_surrogate_topk_recall | total_exact_refine_calls | median_adaptive_topk_used_mean | max_adaptive_topk_used | total_adaptive_topk_cap_hits | total_refined_candidates | median_probe_green_kernel_time_sec | median_active_weight_time_sec | median_candidate_score_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid_adaptive_topk_refine | adaptive_topk_certified_refine | 4 | 18 | 0.7222 | 3 | 23.58 | 2.628 | 20.95 | 0.1461 | 23.76 | 0.007529 | 0.01212 | 136 | 128.2 | 0.1888 |  | 141 | 1 | 4 | 19 | 95 | 0.0 | 0.0 | 0.0 |
| hybrid_adaptive_topk_refine | adaptive_topk_exact_refine | 4 | 18 | 0.7222 | 3 | 24.23 | 2.674 | 21.56 | 0.2637 | 24.51 | 0.007407 | 0.01219 | 139 | 128.2 | 0.1888 |  | 141 | 1 | 4 | 19 | 95 | 0.0 | 0.0 | 0.0 |
| hybrid_surrogate_refine | endpoints |  | 18 | 0.0 | 2 | 4.727 | 0.0 | 4.727 | 0.06631 | 4.789 | 0.03787 | 0.04259 | 27 | 174.9 | 0.1888 |  | 18 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_surrogate_refine | exact_group_rd |  | 18 | 0.1111 | 3 | 17.63 | 12.92 | 5.151 | 0.1241 | 17.79 | 0.01217 | 0.02024 | 83 | 1.094e+08 | 0.1888 |  | 18 | nan | 0.0 | 0 | 0 | 4.537 | 0.0 | 0.002032 |
| hybrid_surrogate_refine | heuristic_topk_exact_refine | 4 | 18 | 0.05556 | 6 | 122.4 | 0.7386 | 121.6 | 0.3773 | 123.1 | 0.001594 | 0.00484 | 651.5 | 2288 | 0.1888 |  | 356 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_surrogate_refine | incremental_group_rd |  | 18 | 0.6111 | 3 | 11.09 | 4.909 | 5.357 | 0.1305 | 11.23 | 0.01624 | 0.02367 | 62.5 | 308.7 | 0.1888 |  | 18 | nan | 0.0 | 0 | 0 | 0.07444 | 0.1128 | 0.002796 |
| hybrid_surrogate_refine | surrogate_topk_certified_refine | 4 | 18 | 0.6667 | 3 | 47.75 | 2.833 | 44.92 | 0.1289 | 47.92 | 0.004265 | 0.006585 | 236 | 126.1 | 0.1888 |  | 178 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_surrogate_refine | surrogate_topk_exact_refine | 4 | 18 | 0.6667 | 3 | 48.48 | 2.888 | 45.59 | 0.2112 | 48.71 | 0.004223 | 0.006599 | 239 | 126.1 | 0.1888 |  | 178 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_certified_refine | 1 | 18 | 0.6111 | 3 | 25.63 | 2.883 | 22.74 | 0.1569 | 25.86 | 0.007654 | 0.01218 | 136.5 | 346.5 | 0.1888 |  | 82 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_certified_refine | 2 | 18 | 0.6111 | 3 | 32.84 | 2.853 | 29.98 | 0.1674 | 33.04 | 0.005914 | 0.009495 | 173.5 | 128.2 | 0.1888 |  | 117 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_certified_refine | 4 | 18 | 0.7222 | 3 | 47.18 | 2.773 | 44.41 | 0.1482 | 47.39 | 0.004016 | 0.00641 | 253 | 128.2 | 0.1888 |  | 174 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_certified_refine | 8 | 18 | 0.7222 | 3 | 73.07 | 2.519 | 70.55 | 0.1303 | 73.25 | 0.002565 | 0.003948 | 399.5 | 116.6 | 0.1888 |  | 274 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_certified_refine | 16 | 18 | 0.6667 | 3 | 132.2 | 2.51 | 129.7 | 0.1265 | 132.4 | 0.001422 | 0.00225 | 720.5 | 116.6 | 0.1888 |  | 454 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_exact_refine | 1 | 18 | 0.6111 | 3 | 25.26 | 2.862 | 22.4 | 0.235 | 25.49 | 0.007785 | 0.01212 | 132.5 | 346.5 | 0.1888 |  | 82 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_exact_refine | 2 | 18 | 0.6111 | 3 | 32.18 | 2.776 | 29.4 | 0.2432 | 32.41 | 0.005678 | 0.009438 | 181 | 128.2 | 0.1888 |  | 117 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_exact_refine | 4 | 18 | 0.7222 | 3 | 48.69 | 2.856 | 45.83 | 0.2351 | 48.93 | 0.00407 | 0.006495 | 251.5 | 128.2 | 0.1888 |  | 174 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_exact_refine | 8 | 18 | 0.7222 | 3 | 73.76 | 2.546 | 71.22 | 0.1875 | 73.95 | 0.002465 | 0.003961 | 410 | 116.6 | 0.1888 |  | 274 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| hybrid_topk_ablation | surrogate_topk_exact_refine | 16 | 18 | 0.6667 | 3 | 131.3 | 2.498 | 128.8 | 0.1958 | 131.6 | 0.001444 | 0.002269 | 711.5 | 116.6 | 0.1888 |  | 454 | nan | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 |

## Adaptive Top-K Diagnostics

### Paired Feasibility

| mode | map | slip | fixed_top4_feasible | adaptive_topk_feasible | feasible_match | adaptive_k_used_mean | selection_speedup_fixed_over_adaptive | lexicographic_regret_vs_fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| certified | four_rooms_11 | 0.0 | True | True | True | 1.0 | 1.9809225334844147 | 0.0 |
| certified | four_rooms_11 | 0.05 | True | True | True | 3.0 | 1.2917481258906074 | 0.0 |
| certified | four_rooms_11 | 0.1 | False | False | True | 4.0 | 1.0227274851121877 | 0.0 |
| certified | four_rooms_15 | 0.0 | True | True | True | 1.0 | 2.0523569986524732 | 0.0 |
| certified | four_rooms_15 | 0.05 | False | False | True | 4.0 | 1.0403975952874398 | 0.0 |
| certified | four_rooms_15 | 0.1 | True | True | True | 4.0 | 1.0299159157143836 | 0.0 |
| certified | maze_13 | 0.0 | True | True | True | 1.0 | 1.9165760216062036 | 0.0 |
| certified | maze_13 | 0.05 | True | True | True | 1.0 | 1.973676558692511 | 0.0 |
| certified | maze_13 | 0.1 | True | True | True | 1.0 | 1.9235773906230542 | 0.0 |
| certified | maze_17 | 0.0 | True | True | True | 1.0 | 2.0474250560069427 | 0.0 |
| certified | maze_17 | 0.05 | True | True | True | 1.0 | 2.0020909968516047 | 0.0 |
| certified | maze_17 | 0.1 | True | True | True | 1.0 | 1.9104051991839082 | 0.0 |
| certified | open_room_12 | 0.0 | True | True | True | 1.0 | 2.1754896581686687 | 0.0 |
| certified | open_room_12 | 0.05 | True | True | True | 4.0 | 1.0624194221579948 | 0.0 |
| certified | open_room_12 | 0.1 | False | False | True | 4.0 | 1.002695982235208 | 0.0 |
| certified | open_room_16 | 0.0 | True | True | True | 1.0 | 2.084450691696202 | 0.0 |
| certified | open_room_16 | 0.05 | False | False | True | 4.0 | 1.0441562449015103 | 0.0 |
| certified | open_room_16 | 0.1 | False | False | True | 4.0 | 1.0150720860857465 | 0.0 |
| exact | four_rooms_11 | 0.0 | True | True | True | 1.0 | 2.0662672918212177 | 0.0 |
| exact | four_rooms_11 | 0.05 | True | True | True | 3.0 | 1.3761496533051576 | 0.0 |
| exact | four_rooms_11 | 0.1 | False | False | True | 4.0 | 1.0300934750236677 | 0.0 |
| exact | four_rooms_15 | 0.0 | True | True | True | 1.0 | 1.9849137738493123 | 0.0 |
| exact | four_rooms_15 | 0.05 | False | False | True | 4.0 | 1.0818399085493329 | 0.0 |
| exact | four_rooms_15 | 0.1 | True | True | True | 4.0 | 1.0681286183607728 | 0.0 |
| exact | maze_13 | 0.0 | True | True | True | 1.0 | 1.9011631147919805 | 0.0 |
| exact | maze_13 | 0.05 | True | True | True | 1.0 | 2.0524515196815964 | 0.0 |
| exact | maze_13 | 0.1 | True | True | True | 1.0 | 2.01296293445069 | 0.0 |
| exact | maze_17 | 0.0 | True | True | True | 1.0 | 1.926947748753271 | 0.0 |
| exact | maze_17 | 0.05 | True | True | True | 1.0 | 2.1106502995653744 | 0.0 |
| exact | maze_17 | 0.1 | True | True | True | 1.0 | 2.0644665478377617 | 0.0 |
| exact | open_room_12 | 0.0 | True | True | True | 1.0 | 2.0497941691617214 | 0.0 |
| exact | open_room_12 | 0.05 | True | True | True | 4.0 | 1.0850715008844412 | 0.0 |
| exact | open_room_12 | 0.1 | False | False | True | 4.0 | 1.046393704718393 | 0.0 |
| exact | open_room_16 | 0.0 | True | True | True | 1.0 | 1.9608309188476378 | 0.0 |
| exact | open_room_16 | 0.05 | False | False | True | 4.0 | 1.0975796195938656 | 0.0 |
| exact | open_room_16 | 0.1 | False | False | True | 4.0 | 1.0843370106887176 | 0.0 |

### K-Used Histogram

| method | top_k_cap | k_used | n_steps | n_feasible_stop | n_cap_hit | n_cap_without_selected_feasible |
| --- | --- | --- | --- | --- | --- | --- |
| adaptive_topk_certified_refine | 4 | 1 | 11 | 11 | 0 | 0 |
| adaptive_topk_certified_refine | 4 | 4 | 21 | 0 | 19 | 19 |
| adaptive_topk_exact_refine | 4 | 1 | 11 | 11 | 0 | 0 |
| adaptive_topk_exact_refine | 4 | 4 | 21 | 0 | 19 | 19 |

### Fixed-K Vs Adaptive Cap

| source | method | top_k_or_cap | n_rows | feasible_rate | median_selection_time_sec | total_exact_refine_calls | total_refined_candidates | median_adaptive_topk_used_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_topk_ablation | surrogate_topk_certified_refine | 1 | 18 | 0.6111111111111112 | 25.627451439999277 | 82 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 2 | 18 | 0.6111111111111112 | 32.837170812505065 | 117 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 4 | 18 | 0.7222222222222222 | 47.18378464298439 | 174 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 8 | 18 | 0.7222222222222222 | 73.07360589801101 | 274 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 16 | 18 | 0.6666666666666666 | 132.19928522451664 | 454 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 1 | 18 | 0.6111111111111112 | 25.25970465550199 | 82 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 2 | 18 | 0.6111111111111112 | 32.18061363900779 | 117 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 4 | 18 | 0.7222222222222222 | 48.68884417702793 | 174 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 8 | 18 | 0.7222222222222222 | 73.76086592450156 | 274 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 16 | 18 | 0.6666666666666666 | 131.33958206299576 | 454 | 0 | nan |
| adaptive_topk | adaptive_topk_certified_refine | 4 | 18 | 0.7222222222222222 | 23.579303502454422 | 141 | 95 | 1.0 |
| adaptive_topk | adaptive_topk_exact_refine | 4 | 18 | 0.7222222222222222 | 24.231489408470225 | 141 | 95 | 1.0 |

### Adaptive Failure Summary

| mode | failure_class | n_rows | max_adaptive_group_total_violation | maps | slips |
| --- | --- | --- | --- | --- | --- |
| certified | cap_envelope_or_boundary_budget_not_met | 1 | 128.17685001041116 | four_rooms_11 | 0.1 |
| certified | cap_exhausted_no_positive_feasible_gain | 4 | 116.58945928855368 | four_rooms_15;open_room_12;open_room_16 | 0.05;0.1 |
| exact | cap_envelope_or_boundary_budget_not_met | 1 | 128.17685001041116 | four_rooms_11 | 0.1 |
| exact | cap_exhausted_no_positive_feasible_gain | 4 | 116.58945928855368 | four_rooms_15;open_room_12;open_room_16 | 0.05;0.1 |

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
| A no-recompute Green response gives a fast explicit boundary proposal whose threshold and local maxima are stable outside certified score-error margins. | proved_symbol_present | rows=299, median_selection=0.02365s, median_speedup_vs_iterative=137.8, max_normalized_value_gap=0.009628 | One-shot implementation and operator-vs-search result | This certifies response/selection stability, not global RD optimality; failed group audits use the separately reported adaptive fallback. |
| First-hit Green kernels define legal compressed edge models on finite absorbing interiors. | proved_symbol_present | rows=80, graph_rows=70, max_start_gap=0.04973 | Graph-SMDP construction | Use exact Green as reference operator; adaptive/truncated variants are certified implementations. |
| Truncated/adaptive Green scores are certified by Neumann tail bounds. | proved_symbol_present | rows=20, final=20, tie_aware_final=20 | Implementation theorem and appendix certificate | Report when tie/top-set exact fallback is used rather than hiding it as speed. |
| Bits distortion admits a controlled finite-difference/Taylor approximation. | proved_symbol_present | rows=9, margin_condition=1, stable_when_checked=1 | Operator approximation and ablation | Keep finite-difference score as the main theorem; gradient score is an approximation. |
| The graph-SMDP Bellman backup is a sup-norm contraction under finite options and gamma<1. | proved_symbol_present | rows=80, graph_rows=70, max_start_gap=0.04973 | Planning correctness lemma | Tie value-gap reporting to residual diagnostics in each benchmark table. |
| The primitive optimal-value gap decomposes into option restriction, boundary abstraction, kernel approximation, and planning residual terms. | proved_symbol_present | rows=162, converged=81, certified=81, median_norm_gap=2.19e-12, p95_norm_gap=0.009713, max_norm_bound=0.04208 | Main preservation theorem and value-gap accounting | Keep the deliberately under-solved truncation/planning ablation separate from the converged certificate table. |
| Margin and top-set certificates separate stable operator decisions from ambiguous ties. | proved_symbol_present | rows=20, final=20, tie_aware_final=20 | Certificate table | Use tie-aware timing as the conservative runtime accounting. |
| Adaptive feasible top-k has the same feasible envelope as fixed top-K under a shared candidate order and feasibility oracle. | proved_symbol_present | rows=36, feasible_match=36, max_regret=0, median_speedup=1.917 | Main discovery backend and fixed-topK ablation | Claim feasible discovery and refinement work savings; do not claim score-optimal split selection without interval dominance. |
| Group-constrained RD makes robustness constraints explicit instead of hiding them in a scalar risk. | proved_symbol_present | rows=18, feasible=12 | Robust objective and main ablation | Use random-maze and held-out probes to show robustness is not hand-tuned to one map. |
| Incremental insertion scoring is an implementation optimization, not a new theorem yet. | lean_pending | rows=30, selected_match=26, max_score_error=233.2 | Runtime ablation, not core correctness theorem | Formalize the insertion algebra only if it becomes a central claim. |
| Fixed-boundary reward relabeling keeps task reward support out of the graph topology. | proved_symbol_present | rows=384, additive=192, event_norm_gap=0.906, goal_conditioned_norm_gap=0.01505 | Multi-task compression and reward relabeling | Label the legacy dense-VI denominator and report normalized option/boundary restriction gaps. |
| Goal-conditioned event options reduce terminal-goal restriction bias without adding the goal to B. | proved_symbol_present | rows=384, additive=192, event_norm_gap=0.906, goal_conditioned_norm_gap=0.01505 | Secondary terminal-goal extension | Treat this as a costed secondary repair; the current table does not show a median win over even the legacy denominator. |
| The extracted graph should generalize across maze instances, not only fixed toy layouts. | empirical_stress_test | rows=360, feasible=173; contexts=7, recovered=6, fixed_family_plateau=1, max_splits=16, max_boundary=17 | Generalization/stress-test section | State the sole max-splits-16 topology/value plateau as fixed option/probe-family bias, not as an unresolved boundary-budget failure. |

## Certificate Appendix Summary

| certificate | rows | interval_certified | fallback_used | tie_fallback_used | curvature_fallback_used | tie_set_certified | epsilon_optimal_certified | final_certified | tie_aware_final_certified | row_q_lt_1_edges | weighted_q_lt_1_edges | certificates_found | rational_verified | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adaptive_frontier_tail_plus_top_set_fallback | 20 | 4 | 16 | 14 | 2 | 14 | 11 | 20 | 20 |  |  |  |  | runtime_decision_procedure |
| weighted_spectral_sufficient | 8 |  |  |  |  |  |  |  |  | 0 | 16 |  |  | appendix_sufficient_certificate |
| conditioned_rational_weighted_audit | 48 |  |  |  |  |  |  |  |  |  |  | 92 | 92 | appendix_reproducibility_audit |

## Source Artifacts

- large-scale adaptive: `experiments/output/large_scale_compression_adaptive/large_scale_compression.csv`
- one-shot operator suites: `experiments/output/one_shot_rd_operator/one_shot_rd_operator.csv, experiments/output/one_shot_rd_operator_random/one_shot_rd_operator.csv, experiments/output/one_shot_rd_operator_random_reference/one_shot_rd_operator.csv, experiments/output/one_shot_rd_operator_xl_end_to_end/one_shot_rd_operator.csv`
- frozen one-shot group-prefix audit: `experiments/output/one_shot_group_fd_frontier/one_shot_group_fd_frontier.csv`
- learned boundary proposal: `experiments/output/boundary_heatmap_downstream_graphonly_test/summary.csv`
- explicit boundary-proposal baselines: `experiments/output/boundary_heatmap_downstream_graphonly_baselines/summary.csv`
- empirical selective audit: `experiments/output/boundary_heatmap_selective_audit_graphonly/heldout_selective_audit.csv`
- constraint-aware reranker audit: `experiments/output/boundary_constraint_student_test/summary.csv`
- constraint-aware reranker gate summary: `experiments/output/boundary_constraint_student/summary.csv`
- constraint-aware selective audit: `experiments/output/boundary_constraint_selective_audit/heldout_selective_audit.csv`
- constraint-aware full audit: `experiments/output/boundary_constraint_selective_audit/heldout_full_audit.csv`
- paired reranker/reference analysis: `experiments/output/boundary_constraint_pairing/paired_summary.csv`
- strong full-state planners: `experiments/output/planner_baseline_comparison/strongest_planner_by_case.csv`
- core benchmark: `experiments/output/core_benchmark/core_benchmark.csv`
- direct state-abstraction baselines: `experiments/output/abstraction_baseline_comparison/abstraction_baseline_aggregate.csv`
- primitive-to-graph gap decomposition: `experiments/output/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv`
- adaptive certification: `experiments/output/adaptive_green_certification/certification_summary.csv`
- larger group-constrained adaptive: `experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv`
- random maze generalization: `experiments/output/random_maze_generalization/random_maze_generalization.csv`
- random-maze boundary-budget recovery: `experiments/output/random_maze_budget_recovery/random_maze_budget_recovery_summary.csv`
- general finite-MDP smoke: `experiments/output/general_env_benchmark/general_env_benchmark.csv`
- general finite-MDP multi-seed aggregate: `experiments/output/general_env_benchmark/general_env_aggregate.csv`
- fair budget frontier: `experiments/output/fair_budget_frontier/fair_budget_frontier_summary.csv`
- epsilon-constrained frontier: `experiments/output/fair_budget_frontier/epsilon_constrained_frontier.csv`
- amortized multitask: `experiments/output/amortized_multitask/amortized_multitask.csv`
- edge reward multitask: `experiments/output/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv`
- solver validity: `experiments/output/solver_validity/solver_validity.csv`
- discovery profile/cache: `experiments/output/discovery_profile_cache/discovery_profile_cache.csv`
- hybrid surrogate/refine: `experiments/output/hybrid_surrogate_refine/hybrid_surrogate_refine.csv, experiments/output/hybrid_topk_ablation/hybrid_surrogate_refine.csv, experiments/output/hybrid_adaptive_topk_refine/hybrid_surrogate_refine.csv`
- adaptive top-k diagnostics: `experiments/output/adaptive_topk_diagnostics`
- incremental Green update: `experiments/output/incremental_green_update/incremental_green_update_aggregate.csv`
- incremental group semantic diff: `experiments/output/group_incremental_semantic_diff/summary.md`
- graph abstraction figures: `experiments/output/graph_abstraction_figures/summary.md`
- theorem/experiment bridge: `experiments/output/theorem_experiment_bridge/theorem_experiment_bridge.csv`
- linear solver thread scaling: `experiments/output/linear_solver_thread_scaling/summary.md`
- weighted spectral certificate: `experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv`
- conditioned rational certificate: `experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv`
