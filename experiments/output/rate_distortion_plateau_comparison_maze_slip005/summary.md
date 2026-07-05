# Graph Baseline Comparison

Generated: 2026-07-05T08:21:52
fixed_methods = ['fixed_endpoints', 'fixed_turn_articulation']
learned_methods = ['learned_rd_struct_budget2', 'learned_rd_batch4_budget2', 'learned_rd_audit_cvar2']
external_boundary_files = []
maps = ['maze'], slips = [0.05], gamma = 0.97
eval_residual_lens = turn_articulation, eval_soft_kind = combined

## Results

| method | method_family | map | slip | n_boundary | n_edges_valid | start_gap | value_gap_max | model_residual_max | residual_backup_value_norm_max | struct_hidden_prob_max | struct_hidden_distinct_valid_total | struct_hidden_distinct_cvar95 | struct_hidden_distinct_per_edge | occupancy_struct_hidden_distinct | soft_cost_valid_total | target_policy_tv_total | description_length_proxy | constructor_stop | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 2 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.333 | 1.832 | 1 | 24.03 | 12.97 | 12.02 | 11.07 | 6.304 | 125.5 | 71.66 | fixed | fixed |
| fixed_turn_articulation | fixed | maze | 0.05 | 30 | 870 | 2.901501261476369e-11 | 2.901501261476369e-11 | 0.1348 | 2.176 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 293.1 | 1884 | 2243 | fixed | fixed |
| learned_rd_struct_budget2 | learned | maze | 0.05 | 3 | 6 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.313 | 1.948 | 1 | 46.83 | 12 | 7.805 | 10.84 | 10.38 | 187.3 | 113.1 | hybrid_threshold | residual_rate_distortion |
| learned_rd_batch4_budget2 | learned | maze | 0.05 | 3 | 6 | 2.921041186709772e-11 | 2.921041186709772e-11 | 1.313 | 1.948 | 1 | 46.83 | 12 | 7.805 | 10.84 | 10.38 | 187.3 | 113.1 | hybrid_threshold | residual_rate_distortion |
| learned_rd_audit_cvar2 | learned | maze | 0.05 | 14 | 182 | 2.917133201663091e-11 | 2.917133201663091e-11 | 1.313 | 8.39 | 1 | 25.04 | 1.984 | 0.1376 | 10.84 | 31.61 | 872.7 | 686.8 | hybrid_threshold | residual_rate_distortion |
