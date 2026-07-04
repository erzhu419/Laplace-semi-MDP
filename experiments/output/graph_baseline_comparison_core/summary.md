# Graph Baseline Comparison

Generated: 2026-07-05T06:04:40
fixed_methods = ['fixed_endpoints', 'fixed_bottleneck15', 'fixed_spectral25', 'fixed_turn_articulation']
learned_methods = ['learned_soft3', 'learned_raw_residual12', 'learned_struct_mdl_e05']
external_boundary_files = []
maps = ['open_room', 'four_rooms', 'maze'], slips = [0.0, 0.05], gamma = 0.97
eval_residual_lens = turn_articulation, eval_soft_kind = combined

## Results

| method | method_family | map | slip | n_boundary | n_edges_valid | start_gap | value_gap_max | model_residual_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_distinct_valid_total | soft_cost_valid_total | target_policy_tv_total | description_length_proxy | constructor_stop | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 2.49 | 30 | 18.06 | fixed | fixed |
| fixed_bottleneck15 | fixed | open_room | 0.0 | 7 | 42 | 0.0 | 8.881784197001252e-16 | 0.9368 | 6.18 | 1 | 7 | 6.79 | 116 | 105.1 | fixed | fixed |
| fixed_spectral25 | fixed | open_room | 0.0 | 11 | 110 | 0.0 | 8.881784197001252e-16 | 0.903 | 6.795 | 1 | 7 | 12.09 | 234 | 220.7 | fixed | fixed |
| fixed_turn_articulation | fixed | open_room | 0.0 | 4 | 12 | 0.0 | 8.881784197001252e-16 | 2.2204460492503132e-17 | 4.4232961430380427e-16 | 0.0 | 0.0 | 7.365 | 60 | 43.97 | fixed | fixed |
| learned_soft3 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_raw_residual12 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_struct_mdl_e05 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| fixed_endpoints | fixed | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 3.355 | 28.4 | 18.46 | fixed | fixed |
| fixed_bottleneck15 | fixed | open_room | 0.05 | 7 | 42 | 0.0788 | 0.08313 | 0.8688 | 5.614 | 0.9358 | 6.578 | 4.197 | 110.2 | 103.7 | fixed | fixed |
| fixed_spectral25 | fixed | open_room | 0.05 | 11 | 110 | 0.07837 | 0.08271 | 0.8391 | 6.419 | 0.9322 | 7.276 | 15.64 | 221.9 | 226.7 | fixed | fixed |
| fixed_turn_articulation | fixed | open_room | 0.05 | 4 | 12 | 0.0788 | 0.0788 | 0.1349 | 0.9484 | 0.0 | 0.0 | 8.263 | 56.8 | 45.56 | fixed | fixed |
| learned_soft3 | learned | open_room | 0.05 | 3 | 6 | 0.0788 | 0.0788 | 0.9134 | 5.612 | 0.9358 | 2.808 | 6.001 | 45.5 | 33.85 | hybrid_threshold | soft_threshold |
| learned_raw_residual12 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_struct_mdl_e05 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| fixed_endpoints | fixed | four_rooms | 0.0 | 2 | 2 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.9531 | 3.375 | 1 | 6 | 5.348 | 66 | 31.05 | fixed | fixed |
| fixed_bottleneck15 | fixed | four_rooms | 0.0 | 10 | 90 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.044 | 12.34 | 1 | 6 | 13.38 | 388 | 240.4 | fixed | fixed |
| fixed_spectral25 | fixed | four_rooms | 0.0 | 15 | 210 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.046 | 17.34 | 1 | 26 | 30.92 | 570 | 463.5 | fixed | fixed |
| fixed_turn_articulation | fixed | four_rooms | 0.0 | 10 | 90 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 2.2204460492503132e-17 | 3.345542092546036e-16 | 0.0 | 0.0 | 18.27 | 348 | 229.4 | fixed | fixed |
| learned_soft3 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_raw_residual12 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_e05 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | four_rooms | 0.05 | 2 | 2 | 0.1152 | 0.1152 | 0.9354 | 3.186 | 1 | 5.936 | 5.436 | 62 | 30.31 | fixed | fixed |
| fixed_bottleneck15 | fixed | four_rooms | 0.05 | 10 | 90 | 0.1152 | 0.1152 | 1.012 | 11.76 | 0.9667 | 6.337 | 9.898 | 365.1 | 237.3 | fixed | fixed |
| fixed_spectral25 | fixed | four_rooms | 0.05 | 15 | 210 | 0.05866 | 0.0928 | 1.011 | 16.69 | 1 | 26.85 | 24.21 | 536.5 | 459.4 | fixed | fixed |
| fixed_turn_articulation | fixed | four_rooms | 0.05 | 10 | 90 | 0.1152 | 0.1152 | 0.1325 | 2.17 | 0.0 | 0.0 | 12.4 | 327.2 | 228.8 | fixed | fixed |
| learned_soft3 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_raw_residual12 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_e05 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | maze | 0.0 | 2 | 2 | 0.0 | 0.0 | 1.345 | 1.87 | 1 | 24 | 6.376 | 134 | 73.47 | fixed | fixed |
| fixed_bottleneck15 | fixed | maze | 0.0 | 13 | 156 | 0.0 | 3.552713678800501e-15 | 1.317 | 5.957 | 1 | 81 | 70.07 | 874 | 674.6 | fixed | fixed |
| fixed_spectral25 | fixed | maze | 0.0 | 22 | 462 | 0.0 | 7.105427357601002e-15 | 1.078 | 5.957 | 1 | 325 | 103.7 | 1514 | 1440 | fixed | fixed |
| fixed_turn_articulation | fixed | maze | 0.0 | 30 | 870 | 3.552713678800501e-15 | 7.105427357601002e-15 | 2.2204460492503132e-17 | 1.743992625925969e-16 | 0.0 | 0.0 | 182.9 | 2012 | 2046 | fixed | fixed |
| learned_soft3 | learned | maze | 0.0 | 4 | 12 | 0.0 | 0.0 | 1.345 | 1.914 | 1 | 47 | 6.712 | 268 | 150.1 | hybrid_threshold | soft_threshold |
| learned_raw_residual12 | learned | maze | 0.0 | 14 | 182 | 0.0 | 7.105427357601002e-15 | 1.174 | 2.316 | 1 | 132 | 84.19 | 938 | 743.6 | hybrid_threshold | residual_raw |
| learned_struct_mdl_e05 | learned | maze | 0.0 | 11 | 110 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.345 | 8.446 | 1 | 55 | 41.66 | 730 | 545.5 | hybrid_threshold | residual_mdl |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 2 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.333 | 1.832 | 1 | 24.03 | 6.304 | 125.5 | 71.66 | fixed | fixed |
| fixed_bottleneck15 | fixed | maze | 0.05 | 13 | 156 | 2.914291030720051e-11 | 2.914291030720051e-11 | 1.299 | 5.914 | 1 | 81.61 | 92.58 | 818.5 | 702.5 | fixed | fixed |
| fixed_spectral25 | fixed | maze | 0.05 | 22 | 462 | 2.7569058147491887e-11 | 2.7569058147491887e-11 | 1.074 | 5.913 | 1 | 322.1 | 127.6 | 1417 | 1469 | fixed | fixed |
| fixed_turn_articulation | fixed | maze | 0.05 | 30 | 870 | 2.901501261476369e-11 | 2.901501261476369e-11 | 0.1348 | 2.176 | 0.0 | 0.0 | 293.1 | 1884 | 2243 | fixed | fixed |
| learned_soft3 | learned | maze | 0.05 | 7 | 42 | 1.7255530337934033e-11 | 1.7255530337934033e-11 | 1.313 | 8.39 | 1 | 90.23 | 20.69 | 458.8 | 313.7 | hybrid_threshold | soft_threshold |
| learned_raw_residual12 | learned | maze | 0.05 | 14 | 182 | 2.901856532844249e-11 | 2.901856532844249e-11 | 1.194 | 2.475 | 0.9997 | 138.3 | 80.69 | 880.1 | 750.1 | hybrid_threshold | residual_raw |
| learned_struct_mdl_e05 | learned | maze | 0.05 | 14 | 182 | 2.917133201663091e-11 | 2.917133201663091e-11 | 1.313 | 4.677 | 0.9997 | 25.04 | 31.61 | 876.4 | 687.7 | hybrid_threshold | residual_mdl |
