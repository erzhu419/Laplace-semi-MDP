# Graph Baseline Comparison

Generated: 2026-07-05T07:59:24
fixed_methods = ['fixed_endpoints', 'fixed_turn_articulation', 'fixed_eigen_extrema12', 'fixed_coverage12']
learned_methods = ['learned_rd_struct_budget1', 'learned_rd_struct_budget2', 'learned_rd_struct_budget6']
external_boundary_files = []
maps = ['open_room', 'four_rooms', 'maze'], slips = [0.0, 0.05], gamma = 0.97
eval_residual_lens = turn_articulation, eval_soft_kind = combined

## Results

| method | method_family | map | slip | n_boundary | n_edges_valid | start_gap | value_gap_max | model_residual_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_distinct_valid_total | struct_hidden_distinct_per_edge | occupancy_struct_hidden_distinct | soft_cost_valid_total | target_policy_tv_total | description_length_proxy | constructor_stop | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 1 | 2.49 | 30 | 18.06 | fixed | fixed |
| fixed_turn_articulation | fixed | open_room | 0.0 | 4 | 12 | 0.0 | 8.881784197001252e-16 | 2.2204460492503132e-17 | 4.4232961430380427e-16 | 0.0 | 0.0 | 0.0 | 0.0 | 7.365 | 60 | 43.97 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9957 | 11.68 | 1 | 6 | 0.04545 | 0.0 | 28.32 | 274 | 271.1 | fixed | fixed |
| fixed_coverage12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9894 | 17.8 | 1 | 3 | 0.02273 | 0.0 | 27.76 | 284 | 269.1 | fixed | fixed |
| learned_rd_struct_budget1 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_rd_struct_budget2 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_rd_struct_budget6 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| fixed_endpoints | fixed | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 0.9358 | 3.355 | 28.4 | 18.46 | fixed | fixed |
| fixed_turn_articulation | fixed | open_room | 0.05 | 4 | 12 | 0.0788 | 0.0788 | 0.1349 | 0.9484 | 0.0 | 0.0 | 0.0 | 0.0 | 8.263 | 56.8 | 45.56 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.05 | 12 | 132 | 0.0788 | 0.0788 | 0.959 | 11.06 | 0.9658 | 6.139 | 0.04651 | 1.1976545186454249e-12 | 14.67 | 259.5 | 264.3 | fixed | fixed |
| fixed_coverage12 | fixed | open_room | 0.05 | 12 | 132 | 0.07609 | 0.07609 | 0.9702 | 17.18 | 0.9828 | 3.277 | 0.02483 | 0.0 | 30.31 | 268.9 | 279.5 | fixed | fixed |
| learned_rd_struct_budget1 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_rd_struct_budget2 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_rd_struct_budget6 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| fixed_endpoints | fixed | four_rooms | 0.0 | 2 | 2 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.9531 | 3.375 | 1 | 6 | 3 | 3 | 5.348 | 66 | 31.05 | fixed | fixed |
| fixed_turn_articulation | fixed | four_rooms | 0.0 | 10 | 90 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 2.2204460492503132e-17 | 3.345542092546036e-16 | 0.0 | 0.0 | 0.0 | 0.0 | 18.27 | 348 | 229.4 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.013 | 9.114 | 1 | 38 | 0.2879 | 0.0 | 38.18 | 448 | 357.4 | fixed | fixed |
| fixed_coverage12 | fixed | four_rooms | 0.0 | 12 | 132 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.061 | 12.34 | 1 | 76 | 0.5758 | 0.0 | 90.41 | 438 | 445.3 | fixed | fixed |
| learned_rd_struct_budget1 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 0.0 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_rd_struct_budget2 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 0.0 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_rd_struct_budget6 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 0.0 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | four_rooms | 0.05 | 2 | 2 | 0.1152 | 0.1152 | 0.9354 | 3.186 | 1 | 5.936 | 2.968 | 2.968 | 5.436 | 62 | 30.31 | fixed | fixed |
| fixed_turn_articulation | fixed | four_rooms | 0.05 | 10 | 90 | 0.1152 | 0.1152 | 0.1325 | 2.17 | 0.0 | 0.0 | 0.0 | 0.0 | 12.4 | 327.2 | 228.8 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.0916 | 0.0916 | 1.006 | 8.602 | 1 | 37.52 | 0.2842 | 0.0 | 41.35 | 421.7 | 363 | fixed | fixed |
| fixed_coverage12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.09225 | 0.09525 | 1.06 | 12.08 | 1 | 76.12 | 0.5767 | 9.977e-06 | 85.73 | 411.9 | 439.6 | fixed | fixed |
| learned_rd_struct_budget1 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 0.0003241 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_rd_struct_budget2 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 0.0003241 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_rd_struct_budget6 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 0.0003241 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | maze | 0.0 | 2 | 2 | 0.0 | 0.0 | 1.345 | 1.87 | 1 | 24 | 12 | 11 | 6.376 | 134 | 73.47 | fixed | fixed |
| fixed_turn_articulation | fixed | maze | 0.0 | 30 | 870 | 3.552713678800501e-15 | 7.105427357601002e-15 | 2.2204460492503132e-17 | 1.743992625925969e-16 | 0.0 | 0.0 | 0.0 | 0.0 | 182.9 | 2012 | 2046 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.0 | 12 | 132 | 0.0 | 7.105427357601002e-15 | 1.171 | 8.446 | 1 | 220 | 1.667 | 1 | 88.9 | 826 | 717 | fixed | fixed |
| fixed_coverage12 | fixed | maze | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.11 | 8.827 | 1 | 257 | 1.947 | 0.0 | 106.1 | 818 | 753.4 | fixed | fixed |
| learned_rd_struct_budget1 | learned | maze | 0.0 | 3 | 6 | 0.0 | 0.0 | 1.345 | 1.965 | 1 | 47 | 7.833 | 0.0 | 12.63 | 200 | 117.7 | hybrid_threshold | residual_rate_distortion |
| learned_rd_struct_budget2 | learned | maze | 0.0 | 3 | 6 | 0.0 | 0.0 | 1.345 | 1.965 | 1 | 47 | 7.833 | 0.0 | 12.63 | 200 | 117.7 | hybrid_threshold | residual_rate_distortion |
| learned_rd_struct_budget6 | learned | maze | 0.0 | 3 | 6 | 0.0 | 7.105427357601002e-15 | 1.345 | 3.972 | 1 | 44 | 7.333 | 3 | 13.02 | 198 | 118.9 | hybrid_threshold | residual_rate_distortion |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 2 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.333 | 1.832 | 1 | 24.03 | 12.02 | 11.07 | 6.304 | 125.5 | 71.66 | fixed | fixed |
| fixed_turn_articulation | fixed | maze | 0.05 | 30 | 870 | 2.901501261476369e-11 | 2.901501261476369e-11 | 0.1348 | 2.176 | 0.0 | 0.0 | 0.0 | 0.0 | 293.1 | 1884 | 2243 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.05 | 12 | 132 | 2.921751729445532e-11 | 2.921751729445532e-11 | 1.16 | 8.391 | 1 | 220.2 | 1.669 | 0.9825 | 72.47 | 773.5 | 693.1 | fixed | fixed |
| fixed_coverage12 | fixed | maze | 0.05 | 12 | 132 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.109 | 8.796 | 1 | 257.5 | 1.95 | 3.931 | 94.2 | 766 | 731.7 | fixed | fixed |
| learned_rd_struct_budget1 | learned | maze | 0.05 | 3 | 6 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.313 | 1.948 | 1 | 46.83 | 7.805 | 10.84 | 10.38 | 187.3 | 113.1 | hybrid_threshold | residual_rate_distortion |
| learned_rd_struct_budget2 | learned | maze | 0.05 | 3 | 6 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.313 | 1.948 | 1 | 46.83 | 7.805 | 10.84 | 10.38 | 187.3 | 113.1 | hybrid_threshold | residual_rate_distortion |
| learned_rd_struct_budget6 | learned | maze | 0.05 | 3 | 6 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.313 | 1.948 | 1 | 46.83 | 7.805 | 10.84 | 10.38 | 187.3 | 113.1 | hybrid_threshold | residual_rate_distortion |
