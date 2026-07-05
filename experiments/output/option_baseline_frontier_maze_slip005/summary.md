# Option Baseline Frontier

Generated: 2026-07-05T09:22:31
k_values = [4, 8, 12, 16, 24]
families = ['eigenoptions', 'betweenness', 'random_landmarks', 'coverage']
objectives = ['description_length_proxy', 'occupancy_struct_hidden_distinct', 'struct_hidden_distinct_cvar95']
maps = ['maze'], slips = [0.05], gamma = 0.97

## Pareto Frontier

| method | map | slip | n_boundary | description_length_proxy | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | hidden_audit_distinct_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | maze | 0.05 | 2 | 71.66 | 11.07 | 12.97 | 11.11 |
| random_landmarks_4 | maze | 0.05 | 4 | 159.5 | 11.03 | 10.93 | 11.06 |
| coverage_4 | maze | 0.05 | 4 | 172.9 | 11.05 | 7.001 | 11.07 |
| betweenness_8 | maze | 0.05 | 8 | 377.2 | 9.104 | 8.305 | 9.12 |
| random_landmarks_8 | maze | 0.05 | 8 | 397.6 | 11.05 | 7 | 11.02 |
| eigenoptions_8 | maze | 0.05 | 8 | 419.6 | 10.05 | 6 | 10.02 |
| coverage_8 | maze | 0.05 | 8 | 426.6 | 11.07 | 4.018 | 11.1 |
| betweenness_12 | maze | 0.05 | 12 | 611.4 | 7.138 | 6.131 | 7.22 |
| eigenoptions_12 | maze | 0.05 | 12 | 693.1 | 10.07 | 5.999 | 10.05 |
| coverage_12 | maze | 0.05 | 12 | 731.7 | 11.04 | 4.018 | 11.07 |
| betweenness_16 | maze | 0.05 | 16 | 864.5 | 7.138 | 5.659 | 7.02 |
| eigenoptions_16 | maze | 0.05 | 16 | 1030 | 10.05 | 4 | 10.06 |
| coverage_16 | maze | 0.05 | 16 | 1107 | 10.05 | 3.01 | 10.02 |
| betweenness_24 | maze | 0.05 | 24 | 1481 | 5.172 | 3.853 | 5.1 |
| graph_rd_joint | maze | 0.05 | 24 | 1585 | 2 | 1.31 | 2.04 |
| turn_articulation | maze | 0.05 | 30 | 2243 | 0.0 | 0.0 | 0.0 |

## Best By Family

| method | map | slip | n_boundary | description_length_proxy | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | hidden_audit_distinct_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| betweenness_24 | maze | 0.05 | 24 | 1481 | 5.172 | 3.853 | 5.1 |
| coverage_24 | maze | 0.05 | 24 | 1896 | 8.088 | 2.018 | 8.08 |
| eigenoptions_24 | maze | 0.05 | 24 | 1788 | 9.967 | 2.745 | 9.97 |
| endpoints | maze | 0.05 | 2 | 71.66 | 11.07 | 12.97 | 11.11 |
| graph_rd_joint | maze | 0.05 | 24 | 1585 | 2 | 1.31 | 2.04 |
| random_landmarks_24 | maze | 0.05 | 24 | 1781 | 6.071 | 3.727 | 6.09 |
| turn_articulation | maze | 0.05 | 30 | 2243 | 0.0 | 0.0 | 0.0 |

## All Rows

| method | map | slip | n_boundary | pareto_frontier | success_rate | primitive_steps_mean | description_length_proxy | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | hidden_audit_distinct_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| betweenness_4 | maze | 0.05 | 4 | False | 1 | 38.75 | 170 | 11.07 | 12.81 | 11 |
| betweenness_8 | maze | 0.05 | 8 | True | 1 | 38.29 | 377.2 | 9.104 | 8.305 | 9.12 |
| betweenness_12 | maze | 0.05 | 12 | True | 1 | 38.79 | 611.4 | 7.138 | 6.131 | 7.22 |
| betweenness_16 | maze | 0.05 | 16 | True | 1 | 38.72 | 864.5 | 7.138 | 5.659 | 7.02 |
| betweenness_24 | maze | 0.05 | 24 | True | 1 | 38.91 | 1481 | 5.172 | 3.853 | 5.1 |
| coverage_4 | maze | 0.05 | 4 | True | 1 | 38.34 | 172.9 | 11.05 | 7.001 | 11.07 |
| coverage_8 | maze | 0.05 | 8 | True | 1 | 38.36 | 426.6 | 11.07 | 4.018 | 11.1 |
| coverage_12 | maze | 0.05 | 12 | True | 1 | 38.59 | 731.7 | 11.04 | 4.018 | 11.07 |
| coverage_16 | maze | 0.05 | 16 | True | 1 | 38.41 | 1107 | 10.05 | 3.01 | 10.02 |
| coverage_24 | maze | 0.05 | 24 | False | 1 | 38.25 | 1896 | 8.088 | 2.018 | 8.08 |
| eigenoptions_4 | maze | 0.05 | 4 | False | 1 | 38.73 | 174.3 | 11.07 | 9.035 | 11.02 |
| eigenoptions_8 | maze | 0.05 | 8 | True | 1 | 38.74 | 419.6 | 10.05 | 6 | 10.02 |
| eigenoptions_12 | maze | 0.05 | 12 | True | 1 | 38.76 | 693.1 | 10.07 | 5.999 | 10.05 |
| eigenoptions_16 | maze | 0.05 | 16 | True | 1 | 38.53 | 1030 | 10.05 | 4 | 10.06 |
| eigenoptions_24 | maze | 0.05 | 24 | False | 1 | 38.5 | 1788 | 9.967 | 2.745 | 9.97 |
| endpoints | maze | 0.05 | 2 | True | 1 | 38.26 | 71.66 | 11.07 | 12.97 | 11.11 |
| graph_rd_joint | maze | 0.05 | 24 | True | 1 | 38.5 | 1585 | 2 | 1.31 | 2.04 |
| random_landmarks_4 | maze | 0.05 | 4 | True | 1 | 38.14 | 159.5 | 11.03 | 10.93 | 11.06 |
| random_landmarks_8 | maze | 0.05 | 8 | True | 1 | 38.36 | 397.6 | 11.05 | 7 | 11.02 |
| random_landmarks_12 | maze | 0.05 | 12 | False | 1 | 38.88 | 676.9 | 10.05 | 6.926 | 10.09 |
| random_landmarks_16 | maze | 0.05 | 16 | False | 1 | 38.07 | 1060 | 10.05 | 4.644 | 10.03 |
| random_landmarks_24 | maze | 0.05 | 24 | False | 1 | 38.21 | 1781 | 6.071 | 3.727 | 6.09 |
| turn_articulation | maze | 0.05 | 30 | True | 1 | 38.58 | 2243 | 0.0 | 0.0 | 0.0 |
