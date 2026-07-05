# Option Algorithm Comparison

Generated: 2026-07-05T09:07:43
methods = ['endpoints', 'eigenoptions_12', 'betweenness_12', 'random_landmarks_12', 'coverage_12', 'graph_rd_joint', 'turn_articulation']
maps = ['maze'], slips = [0.05], gamma = 0.97
Tabular first pass: option terminations are selected in the original environment, option policies are shortest-path-to-subgoal, kernels are exact first-boundary reductions, and rollout metrics simulate the SMDP policy back in the original environment.
audit_lens = turn_articulation, n_rollouts = 100

## Comparison

| method | method_family | map | slip | n_boundary | feasible | success_rate | primitive_steps_mean | option_steps_mean | start_gap | value_gap_max | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 | hidden_audit_distinct_mean | target_policy_tv_total | description_length_proxy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| endpoints | diagnostic:small_graph | maze | 0.05 | 2 | True | 1 | 38.26 | 1 | 2.921041186709772e-11 | 2.921041186709772e-11 | 11.07 | 12.97 | 11.11 | 125.5 | 71.66 |
| eigenoptions_12 | option_algorithm:laplacian_eigenoptions | maze | 0.05 | 12 | True | 1 | 38.76 | 6.96 | 2.921751729445532e-11 | 2.921751729445532e-11 | 10.07 | 5.999 | 10.05 | 773.5 | 693.1 |
| betweenness_12 | option_algorithm:bottleneck_betweenness | maze | 0.05 | 12 | True | 1 | 38.79 | 10.98 | 2.0179413695586845e-11 | 2.0179413695586845e-11 | 7.138 | 6.131 | 7.22 | 762.3 | 611.4 |
| random_landmarks_12 | option_algorithm:random_landmarks | maze | 0.05 | 12 | True | 1 | 38.88 | 3.12 | 2.2602364424528787e-11 | 2.2602364424528787e-11 | 10.05 | 6.926 | 10.09 | 767.7 | 676.9 |
| coverage_12 | option_algorithm:topological_coverage | maze | 0.05 | 12 | True | 1 | 38.59 | 4.1 | 2.921041186709772e-11 | 2.921041186709772e-11 | 11.04 | 4.018 | 11.07 | 766 | 731.7 |
| graph_rd_joint | ours:rd_graph | maze | 0.05 | 24 | True | 1 | 38.5 | 10 | 2.9022118042121292e-11 | 2.9022118042121292e-11 | 2 | 1.31 | 2.04 | 1502 | 1585 |
| turn_articulation | diagnostic:dense_graph | maze | 0.05 | 30 | True | 1 | 38.58 | 12.1 | 2.901501261476369e-11 | 2.901501261476369e-11 | 0.0 | 0.0 | 0.0 | 1884 | 2243 |

## Notes

- `training_samples = 0` means these are constructed tabular baselines, not trained Option-Critic-style agents.
- `model_queries_proxy` is a rough graph/model-access proxy for construction cost, not a true sample-efficiency curve.
- `hidden_audit_distinct_mean` is measured from original-environment rollouts against the audit lens.
