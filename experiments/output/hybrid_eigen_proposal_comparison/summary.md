# Graph Baseline Comparison

Generated: 2026-07-05T06:36:33
fixed_methods = ['fixed_endpoints', 'fixed_eigen_extrema12']
learned_methods = ['learned_struct_mdl_e05', 'learned_struct_mdl_hard_eigen12']
external_boundary_files = []
maps = ['open_room', 'four_rooms', 'maze'], slips = [0.0, 0.05], gamma = 0.97
eval_residual_lens = turn_articulation, eval_soft_kind = combined

## Results

| method | method_family | map | slip | n_boundary | n_edges_valid | start_gap | value_gap_max | model_residual_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_distinct_valid_total | struct_hidden_distinct_per_edge | soft_cost_valid_total | target_policy_tv_total | description_length_proxy | constructor_stop | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9957 | 11.68 | 1 | 6 | 0.04545 | 28.32 | 274 | 271.1 | fixed | fixed |
| learned_struct_mdl_e05 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_struct_mdl_hard_eigen12 | learned | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9957 | 11.68 | 1 | 6 | 0.04545 | 28.32 | 274 | 271.1 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.05 | 12 | 132 | 0.0788 | 0.0788 | 0.959 | 11.06 | 0.9658 | 6.139 | 0.04651 | 14.67 | 259.5 | 264.3 | fixed | fixed |
| learned_struct_mdl_e05 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_struct_mdl_hard_eigen12 | learned | open_room | 0.05 | 12 | 132 | 0.0788 | 0.0788 | 0.959 | 11.06 | 0.9658 | 6.139 | 0.04651 | 14.67 | 259.5 | 264.3 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | four_rooms | 0.0 | 2 | 2 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.9531 | 3.375 | 1 | 6 | 3 | 5.348 | 66 | 31.05 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.013 | 9.114 | 1 | 38 | 0.2879 | 38.18 | 448 | 357.4 | fixed | fixed |
| learned_struct_mdl_e05 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_hard_eigen12 | learned | four_rooms | 0.0 | 8 | 56 | 3.552713678800501e-15 | 3.552713678800501e-15 | 0.978 | 9.114 | 1 | 4 | 0.07143 | 6.352 | 300 | 167.1 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | four_rooms | 0.05 | 2 | 2 | 0.1152 | 0.1152 | 0.9354 | 3.186 | 1 | 5.936 | 2.968 | 5.436 | 62 | 30.31 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.0916 | 0.0916 | 1.006 | 8.602 | 1 | 37.52 | 0.2842 | 41.35 | 421.7 | 363 | fixed | fixed |
| learned_struct_mdl_e05 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_hard_eigen12 | learned | four_rooms | 0.05 | 13 | 156 | 0.0916 | 0.0916 | 0.9411 | 8.602 | 0.9664 | 7.848 | 0.05031 | 14.12 | 461.3 | 354.9 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | maze | 0.0 | 2 | 2 | 0.0 | 0.0 | 1.345 | 1.87 | 1 | 24 | 12 | 6.376 | 134 | 73.47 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.0 | 12 | 132 | 0.0 | 7.105427357601002e-15 | 1.171 | 8.446 | 1 | 220 | 1.667 | 88.9 | 826 | 717 | fixed | fixed |
| learned_struct_mdl_e05 | learned | maze | 0.0 | 11 | 110 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.345 | 8.446 | 1 | 55 | 0.5 | 41.66 | 730 | 545.5 | hybrid_threshold | residual_mdl |
| learned_struct_mdl_hard_eigen12 | learned | maze | 0.0 | 22 | 462 | 3.552713678800501e-15 | 7.105427357601002e-15 | 1.008 | 11.44 | 1 | 228 | 0.4935 | 150.1 | 1486 | 1559 | hybrid_threshold | residual_mdl |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 2 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.333 | 1.832 | 1 | 24.03 | 12.02 | 6.304 | 125.5 | 71.66 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.05 | 12 | 132 | 2.921751729445532e-11 | 2.921751729445532e-11 | 1.16 | 8.391 | 1 | 220.2 | 1.669 | 72.47 | 773.5 | 693.1 | fixed | fixed |
| learned_struct_mdl_e05 | learned | maze | 0.05 | 14 | 182 | 2.917133201663091e-11 | 2.917133201663091e-11 | 1.313 | 4.677 | 0.9997 | 25.04 | 0.1376 | 31.61 | 876.4 | 687.7 | hybrid_threshold | residual_mdl |
| learned_struct_mdl_hard_eigen12 | learned | maze | 0.05 | 22 | 462 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.038 | 8.39 | 1 | 223.2 | 0.483 | 138.2 | 1403 | 1523 | max_splits | residual_mdl |
