# Graph Baseline Comparison

Generated: 2026-07-05T06:18:16
fixed_methods = ['fixed_endpoints', 'fixed_bottleneck15', 'fixed_spectral25', 'fixed_eigen_extrema4', 'fixed_eigen_extrema8', 'fixed_eigen_extrema12', 'fixed_coverage8', 'fixed_coverage12']
learned_methods = ['learned_raw_residual12', 'learned_struct_mdl_e05']
external_boundary_files = []
maps = ['open_room', 'four_rooms', 'maze'], slips = [0.0, 0.05], gamma = 0.97
eval_residual_lens = turn_articulation, eval_soft_kind = combined

## Results

| method | method_family | map | slip | n_boundary | n_edges_valid | start_gap | value_gap_max | model_residual_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_distinct_valid_total | struct_hidden_distinct_per_edge | soft_cost_valid_total | target_policy_tv_total | description_length_proxy | constructor_stop | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | fixed | fixed |
| fixed_bottleneck15 | fixed | open_room | 0.0 | 7 | 42 | 0.0 | 8.881784197001252e-16 | 0.9368 | 6.18 | 1 | 7 | 0.1667 | 6.79 | 116 | 105.1 | fixed | fixed |
| fixed_spectral25 | fixed | open_room | 0.0 | 11 | 110 | 0.0 | 8.881784197001252e-16 | 0.903 | 6.795 | 1 | 7 | 0.06364 | 12.09 | 234 | 220.7 | fixed | fixed |
| fixed_eigen_extrema4 | fixed | open_room | 0.0 | 4 | 12 | 0.0 | 8.881784197001252e-16 | 1.046 | 6.392 | 1 | 2 | 0.1667 | 5.496 | 86 | 49.89 | fixed | fixed |
| fixed_eigen_extrema8 | fixed | open_room | 0.0 | 8 | 56 | 0.0 | 8.881784197001252e-16 | 0.9957 | 11.68 | 1 | 6 | 0.1071 | 17.94 | 154 | 140.9 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9957 | 11.68 | 1 | 6 | 0.04545 | 28.32 | 274 | 271.1 | fixed | fixed |
| fixed_coverage8 | fixed | open_room | 0.0 | 8 | 56 | 0.0 | 1.7763568394002505e-15 | 0.903 | 6.795 | 1 | 3 | 0.05357 | 20.7 | 168 | 143.8 | fixed | fixed |
| fixed_coverage12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9894 | 17.8 | 1 | 3 | 0.02273 | 27.76 | 284 | 269.1 | fixed | fixed |
| learned_raw_residual12 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_struct_mdl_e05 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| fixed_endpoints | fixed | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | fixed | fixed |
| fixed_bottleneck15 | fixed | open_room | 0.05 | 7 | 42 | 0.0788 | 0.08313 | 0.8688 | 5.614 | 0.9358 | 6.578 | 0.1566 | 4.197 | 110.2 | 103.7 | fixed | fixed |
| fixed_spectral25 | fixed | open_room | 0.05 | 11 | 110 | 0.07837 | 0.08271 | 0.8391 | 6.419 | 0.9322 | 7.276 | 0.06615 | 15.64 | 221.9 | 226.7 | fixed | fixed |
| fixed_eigen_extrema4 | fixed | open_room | 0.05 | 4 | 12 | 0.0788 | 0.0788 | 1.008 | 5.943 | 0.9664 | 1.936 | 0.1614 | 3.756 | 81.27 | 48.17 | fixed | fixed |
| fixed_eigen_extrema8 | fixed | open_room | 0.05 | 8 | 56 | 0.0788 | 0.0788 | 0.9586 | 11.06 | 0.9664 | 5.971 | 0.1066 | 6.687 | 145.9 | 132.3 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.05 | 12 | 132 | 0.0788 | 0.0788 | 0.959 | 11.06 | 0.9658 | 6.139 | 0.04651 | 14.67 | 259.5 | 264.3 | fixed | fixed |
| fixed_coverage8 | fixed | open_room | 0.05 | 8 | 56 | 0.07778 | 0.07778 | 0.8357 | 6.192 | 0.9347 | 2.961 | 0.05287 | 24.91 | 159.2 | 150.5 | fixed | fixed |
| fixed_coverage12 | fixed | open_room | 0.05 | 12 | 132 | 0.07609 | 0.07609 | 0.9702 | 17.18 | 0.9828 | 3.277 | 0.02483 | 30.31 | 268.9 | 279.5 | fixed | fixed |
| learned_raw_residual12 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_struct_mdl_e05 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| fixed_endpoints | fixed | four_rooms | 0.0 | 2 | 2 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.9531 | 3.375 | 1 | 6 | 3 | 5.348 | 66 | 31.05 | fixed | fixed |
| fixed_bottleneck15 | fixed | four_rooms | 0.0 | 10 | 90 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.044 | 12.34 | 1 | 6 | 0.06667 | 13.38 | 388 | 240.4 | fixed | fixed |
| fixed_spectral25 | fixed | four_rooms | 0.0 | 15 | 210 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.046 | 17.34 | 1 | 26 | 0.1238 | 30.92 | 570 | 463.5 | fixed | fixed |
| fixed_eigen_extrema4 | fixed | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 4.431 | 1 | 20 | 1.667 | 20.05 | 154 | 90.7 | fixed | fixed |
| fixed_eigen_extrema8 | fixed | four_rooms | 0.0 | 8 | 56 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.046 | 9.114 | 1 | 19 | 0.3393 | 23.08 | 306 | 199.3 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.013 | 9.114 | 1 | 38 | 0.2879 | 38.18 | 448 | 357.4 | fixed | fixed |
| fixed_coverage8 | fixed | four_rooms | 0.0 | 8 | 56 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.03 | 9.114 | 1 | 60 | 1.071 | 65.49 | 274 | 248 | fixed | fixed |
| fixed_coverage12 | fixed | four_rooms | 0.0 | 12 | 132 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.061 | 12.34 | 1 | 76 | 0.5758 | 90.41 | 438 | 445.3 | fixed | fixed |
| learned_raw_residual12 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_e05 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | four_rooms | 0.05 | 2 | 2 | 0.1152 | 0.1152 | 0.9354 | 3.186 | 1 | 5.936 | 2.968 | 5.436 | 62 | 30.31 | fixed | fixed |
| fixed_bottleneck15 | fixed | four_rooms | 0.05 | 10 | 90 | 0.1152 | 0.1152 | 1.012 | 11.76 | 0.9667 | 6.337 | 0.07041 | 9.898 | 365.1 | 237.3 | fixed | fixed |
| fixed_spectral25 | fixed | four_rooms | 0.05 | 15 | 210 | 0.05866 | 0.0928 | 1.011 | 16.69 | 1 | 26.85 | 0.1278 | 24.21 | 536.5 | 459.4 | fixed | fixed |
| fixed_eigen_extrema4 | fixed | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 1.002 | 4.137 | 1 | 19.61 | 1.634 | 19.17 | 144.9 | 88.1 | fixed | fixed |
| fixed_eigen_extrema8 | fixed | four_rooms | 0.05 | 8 | 56 | 0.0916 | 0.0916 | 1.038 | 8.602 | 1 | 18.84 | 0.3365 | 21.08 | 288.1 | 196.4 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.0916 | 0.0916 | 1.006 | 8.602 | 1 | 37.52 | 0.2842 | 41.35 | 421.7 | 363 | fixed | fixed |
| fixed_coverage8 | fixed | four_rooms | 0.05 | 8 | 56 | 0.1152 | 0.1152 | 1.023 | 8.567 | 1 | 59.74 | 1.067 | 64.2 | 257.6 | 245.4 | fixed | fixed |
| fixed_coverage12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.09225 | 0.09525 | 1.06 | 12.08 | 1 | 76.12 | 0.5767 | 85.73 | 411.9 | 439.6 | fixed | fixed |
| learned_raw_residual12 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_e05 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | maze | 0.0 | 2 | 2 | 0.0 | 0.0 | 1.345 | 1.87 | 1 | 24 | 12 | 6.376 | 134 | 73.47 | fixed | fixed |
| fixed_bottleneck15 | fixed | maze | 0.0 | 13 | 156 | 0.0 | 3.552713678800501e-15 | 1.317 | 5.957 | 1 | 81 | 0.5192 | 70.07 | 874 | 674.6 | fixed | fixed |
| fixed_spectral25 | fixed | maze | 0.0 | 22 | 462 | 0.0 | 7.105427357601002e-15 | 1.078 | 5.957 | 1 | 325 | 0.7035 | 103.7 | 1514 | 1440 | fixed | fixed |
| fixed_eigen_extrema4 | fixed | maze | 0.0 | 4 | 12 | 0.0 | 7.105427357601002e-15 | 1.284 | 4.715 | 1 | 77 | 6.417 | 28.46 | 272 | 182.3 | fixed | fixed |
| fixed_eigen_extrema8 | fixed | maze | 0.0 | 8 | 56 | 0.0 | 7.105427357601002e-15 | 1.194 | 8.446 | 1 | 143 | 2.554 | 60.52 | 544 | 425.7 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.0 | 12 | 132 | 0.0 | 7.105427357601002e-15 | 1.171 | 8.446 | 1 | 220 | 1.667 | 88.9 | 826 | 717 | fixed | fixed |
| fixed_coverage8 | fixed | maze | 0.0 | 8 | 56 | 0.0 | 3.552713678800501e-15 | 1.183 | 4.484 | 1 | 181 | 3.232 | 68.9 | 542 | 443.2 | fixed | fixed |
| fixed_coverage12 | fixed | maze | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.11 | 8.827 | 1 | 257 | 1.947 | 106.1 | 818 | 753.4 | fixed | fixed |
| learned_raw_residual12 | learned | maze | 0.0 | 14 | 182 | 0.0 | 7.105427357601002e-15 | 1.174 | 2.316 | 1 | 132 | 0.7253 | 84.19 | 938 | 743.6 | hybrid_threshold | residual_raw |
| learned_struct_mdl_e05 | learned | maze | 0.0 | 11 | 110 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.345 | 8.446 | 1 | 55 | 0.5 | 41.66 | 730 | 545.5 | hybrid_threshold | residual_mdl |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 2 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.333 | 1.832 | 1 | 24.03 | 12.02 | 6.304 | 125.5 | 71.66 | fixed | fixed |
| fixed_bottleneck15 | fixed | maze | 0.05 | 13 | 156 | 2.914291030720051e-11 | 2.914291030720051e-11 | 1.299 | 5.914 | 1 | 81.61 | 0.5231 | 92.58 | 818.5 | 702.5 | fixed | fixed |
| fixed_spectral25 | fixed | maze | 0.05 | 22 | 462 | 2.7569058147491887e-11 | 2.7569058147491887e-11 | 1.074 | 5.913 | 1 | 322.1 | 0.6971 | 127.6 | 1417 | 1469 | fixed | fixed |
| fixed_eigen_extrema4 | fixed | maze | 0.05 | 4 | 12 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.276 | 4.665 | 1 | 76.9 | 6.408 | 24 | 254.8 | 174.3 | fixed | fixed |
| fixed_eigen_extrema8 | fixed | maze | 0.05 | 8 | 56 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.188 | 8.391 | 1 | 143.3 | 2.56 | 60.78 | 509.4 | 419.6 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.05 | 12 | 132 | 2.921751729445532e-11 | 2.921751729445532e-11 | 1.16 | 8.391 | 1 | 220.2 | 1.669 | 72.47 | 773.5 | 693.1 | fixed | fixed |
| fixed_coverage8 | fixed | maze | 0.05 | 8 | 56 | 2.921396458077652e-11 | 2.921396458077652e-11 | 1.177 | 4.462 | 1 | 181.1 | 3.233 | 59.55 | 507.6 | 426.6 | fixed | fixed |
| fixed_coverage12 | fixed | maze | 0.05 | 12 | 132 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.109 | 8.796 | 1 | 257.5 | 1.95 | 94.2 | 766 | 731.7 | fixed | fixed |
| learned_raw_residual12 | learned | maze | 0.05 | 14 | 182 | 2.901856532844249e-11 | 2.901856532844249e-11 | 1.194 | 2.475 | 0.9997 | 138.3 | 0.76 | 80.69 | 880.1 | 750.1 | hybrid_threshold | residual_raw |
| learned_struct_mdl_e05 | learned | maze | 0.05 | 14 | 182 | 2.917133201663091e-11 | 2.917133201663091e-11 | 1.313 | 4.677 | 0.9997 | 25.04 | 0.1376 | 31.61 | 876.4 | 687.7 | hybrid_threshold | residual_mdl |
