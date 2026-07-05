# RD Pareto Frontier

Generated: 2026-07-05T08:41:28
input = experiments/output/rate_distortion_joint_comparison_maze_slip005/comparison.csv
group_columns = ['map', 'slip']
objectives = ['description_length_proxy', 'occupancy_struct_hidden_distinct', 'struct_hidden_distinct_cvar95']

## maze / 0.05

| method | method_family | map | slip | n_boundary | description_length_proxy | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | struct_hidden_distinct_valid_total | start_gap | constructor_last_split_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_endpoints | fixed | maze | 0.05 | 2 | 71.66338350038197 | 11.06868903087758 | 12.966122478284957 | 24.034811509162537 | 2.921041186709772e-11 | fixed |
| learned_rd_struct_budget2 | learned | maze | 0.05 | 3 | 113.1097607875922 | 10.844551080525244 | 11.999999911802908 | 46.82852947664694 | 2.921041186709772e-11 | residual_rate_distortion |
| learned_rd_audit_cvar2 | learned | maze | 0.05 | 14 | 686.8386627773741 | 10.844551080525246 | 1.9843935032984052 | 25.04003774193515 | 2.917133201663091e-11 | residual_rate_distortion |
| learned_rd_joint_occ2_audit2 | learned | maze | 0.05 | 18 | 1181.9100686214633 | 0.017236165709101903 | 1.0198087214115037 | 131.76639363967422 | 2.8407498575688805e-11 | residual_rate_distortion |
| fixed_turn_articulation | fixed | maze | 0.05 | 30 | 2242.510049505177 | 0.0 | 0.0 | 0.0 | 2.901501261476369e-11 | fixed |
