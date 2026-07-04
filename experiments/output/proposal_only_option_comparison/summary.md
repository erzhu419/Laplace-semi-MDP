# Graph Baseline Comparison

Generated: 2026-07-05T06:44:32
fixed_methods = ['fixed_endpoints', 'fixed_eigen_extrema12', 'fixed_coverage12']
learned_methods = ['learned_struct_mdl_e05', 'learned_struct_mdl_proposal_eigen12', 'learned_struct_mdl_proposal_coverage12']
external_boundary_files = []
maps = ['open_room', 'four_rooms', 'maze'], slips = [0.0, 0.05], gamma = 0.97
eval_residual_lens = turn_articulation, eval_soft_kind = combined

## Results

| method | method_family | map | slip | n_boundary | n_edges_valid | start_gap | value_gap_max | model_residual_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_distinct_valid_total | struct_hidden_distinct_per_edge | soft_cost_valid_total | target_policy_tv_total | description_length_proxy | constructor_stop | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9957 | 11.68 | 1 | 6 | 0.04545 | 28.32 | 274 | 271.1 | fixed | fixed |
| fixed_coverage12 | fixed | open_room | 0.0 | 12 | 132 | 0.0 | 8.881784197001252e-16 | 0.9894 | 17.8 | 1 | 3 | 0.02273 | 27.76 | 284 | 269.1 | fixed | fixed |
| learned_struct_mdl_e05 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_struct_mdl_proposal_eigen12 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| learned_struct_mdl_proposal_coverage12 | learned | open_room | 0.0 | 2 | 2 | 0.0 | 0.0 | 0.9839 | 4.953 | 1 | 2 | 1 | 2.49 | 30 | 18.06 | hybrid_threshold | none |
| fixed_endpoints | fixed | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | open_room | 0.05 | 12 | 132 | 0.0788 | 0.0788 | 0.959 | 11.06 | 0.9658 | 6.139 | 0.04651 | 14.67 | 259.5 | 264.3 | fixed | fixed |
| fixed_coverage12 | fixed | open_room | 0.05 | 12 | 132 | 0.07609 | 0.07609 | 0.9702 | 17.18 | 0.9828 | 3.277 | 0.02483 | 30.31 | 268.9 | 279.5 | fixed | fixed |
| learned_struct_mdl_e05 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_struct_mdl_proposal_eigen12 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| learned_struct_mdl_proposal_coverage12 | learned | open_room | 0.05 | 2 | 2 | 0.0788 | 0.0788 | 0.9134 | 4.449 | 0.9358 | 1.872 | 0.9358 | 3.355 | 28.4 | 18.46 | hybrid_threshold | none |
| fixed_endpoints | fixed | four_rooms | 0.0 | 2 | 2 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 0.9531 | 3.375 | 1 | 6 | 3 | 5.348 | 66 | 31.05 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.013 | 9.114 | 1 | 38 | 0.2879 | 38.18 | 448 | 357.4 | fixed | fixed |
| fixed_coverage12 | fixed | four_rooms | 0.0 | 12 | 132 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.061 | 12.34 | 1 | 76 | 0.5758 | 90.41 | 438 | 445.3 | fixed | fixed |
| learned_struct_mdl_e05 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_proposal_eigen12 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_proposal_coverage12 | learned | four_rooms | 0.0 | 4 | 12 | 1.7763568394002505e-15 | 1.7763568394002505e-15 | 1.013 | 6.848 | 1 | 2 | 0.1667 | 4.824 | 150 | 67.95 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | four_rooms | 0.05 | 2 | 2 | 0.1152 | 0.1152 | 0.9354 | 3.186 | 1 | 5.936 | 2.968 | 5.436 | 62 | 30.31 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.0916 | 0.0916 | 1.006 | 8.602 | 1 | 37.52 | 0.2842 | 41.35 | 421.7 | 363 | fixed | fixed |
| fixed_coverage12 | fixed | four_rooms | 0.05 | 12 | 132 | 0.09225 | 0.09525 | 1.06 | 12.08 | 1 | 76.12 | 0.5767 | 85.73 | 411.9 | 439.6 | fixed | fixed |
| learned_struct_mdl_e05 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_proposal_eigen12 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| learned_struct_mdl_proposal_coverage12 | learned | four_rooms | 0.05 | 4 | 12 | 0.1152 | 0.1152 | 0.9752 | 6.385 | 0.9664 | 1.938 | 0.1615 | 3.834 | 141.2 | 66.24 | hybrid_threshold | hard_hidden |
| fixed_endpoints | fixed | maze | 0.0 | 2 | 2 | 0.0 | 0.0 | 1.345 | 1.87 | 1 | 24 | 12 | 6.376 | 134 | 73.47 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.0 | 12 | 132 | 0.0 | 7.105427357601002e-15 | 1.171 | 8.446 | 1 | 220 | 1.667 | 88.9 | 826 | 717 | fixed | fixed |
| fixed_coverage12 | fixed | maze | 0.0 | 12 | 132 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.11 | 8.827 | 1 | 257 | 1.947 | 106.1 | 818 | 753.4 | fixed | fixed |
| learned_struct_mdl_e05 | learned | maze | 0.0 | 11 | 110 | 3.552713678800501e-15 | 3.552713678800501e-15 | 1.345 | 8.446 | 1 | 55 | 0.5 | 41.66 | 730 | 545.5 | hybrid_threshold | residual_mdl |
| learned_struct_mdl_proposal_eigen12 | learned | maze | 0.0 | 13 | 156 | 3.552713678800501e-15 | 7.105427357601002e-15 | 1.345 | 8.446 | 1 | 63 | 0.4038 | 48.86 | 870 | 674.9 | hybrid_threshold | residual_mdl |
| learned_struct_mdl_proposal_coverage12 | learned | maze | 0.0 | 14 | 182 | 0.0 | 7.105427357601002e-15 | 1.345 | 11.44 | 1 | 67 | 0.3681 | 52.46 | 936 | 740.7 | hybrid_threshold | residual_mdl |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 2 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.333 | 1.832 | 1 | 24.03 | 12.02 | 6.304 | 125.5 | 71.66 | fixed | fixed |
| fixed_eigen_extrema12 | fixed | maze | 0.05 | 12 | 132 | 2.921751729445532e-11 | 2.921751729445532e-11 | 1.16 | 8.391 | 1 | 220.2 | 1.669 | 72.47 | 773.5 | 693.1 | fixed | fixed |
| fixed_coverage12 | fixed | maze | 0.05 | 12 | 132 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.109 | 8.796 | 1 | 257.5 | 1.95 | 94.2 | 766 | 731.7 | fixed | fixed |
| learned_struct_mdl_e05 | learned | maze | 0.05 | 14 | 182 | 2.917133201663091e-11 | 2.917133201663091e-11 | 1.313 | 4.677 | 0.9997 | 25.04 | 0.1376 | 31.61 | 876.4 | 687.7 | hybrid_threshold | residual_mdl |
| learned_struct_mdl_proposal_eigen12 | learned | maze | 0.05 | 16 | 240 | 2.920330643974012e-11 | 2.920330643974012e-11 | 1.313 | 5.913 | 0.9997 | 27.22 | 0.1134 | 35.73 | 1006 | 824.7 | hybrid_threshold | residual_mdl |
| learned_struct_mdl_proposal_coverage12 | learned | maze | 0.05 | 17 | 272 | 2.8880009494969272e-11 | 2.8880009494969272e-11 | 1.313 | 6.903 | 1 | 28.04 | 0.1031 | 37.68 | 1069 | 893.5 | hybrid_threshold | residual_mdl |
