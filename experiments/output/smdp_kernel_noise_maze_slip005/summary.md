# Rollout-Estimated SMDP Kernel Noise Curve

Generated: 2026-07-05T09:24:42
methods = ['betweenness_12', 'graph_rd_joint']
sample_sizes = [1, 2, 5, 10, 20, 50], replicates = 3
maps = ['maze'], slips = [0.05], gamma = 0.97

Each row estimates first-boundary SMDP kernels from Monte Carlo option rollouts, solves planning on the estimated model, then evaluates that abstract policy on the exact SMDP model and by original-environment rollouts.

| method | map | slip | n_boundary | sample_rollouts_per_option | policy_value_loss_exact_mean | estimated_model_start_error_mean | policy_disagreement_mean | kernel_gamma_l1_mean_mean | kernel_reward_abs_mean_mean | success_rate_mean | hidden_audit_distinct_mean_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| betweenness_12 | maze | 0.05 | 12 | 1 | 2.706 | 0.5881 | 0.2424 | 0.0466 | 0.2478 | 0.9967 | 7.04 |
| betweenness_12 | maze | 0.05 | 12 | 2 | 0.01142 | 0.5864 | 0.2727 | 0.04584 | 0.1734 | 1 | 7.047 |
| betweenness_12 | maze | 0.05 | 12 | 5 | 0.007612 | 0.5234 | 0.2121 | 0.03542 | 0.1518 | 1 | 7.013 |
| betweenness_12 | maze | 0.05 | 12 | 10 | 0.01142 | 0.4689 | 0.5455 | 0.03431 | 0.09916 | 1 | 7.013 |
| betweenness_12 | maze | 0.05 | 12 | 20 | 0.007612 | 0.3478 | 0.5455 | 0.02921 | 0.07901 | 1 | 7.033 |
| betweenness_12 | maze | 0.05 | 12 | 50 | 0.01142 | 0.2623 | 0.6667 | 0.01577 | 0.04831 | 1 | 7.04 |
| graph_rd_joint | maze | 0.05 | 24 | 1 | 0.03131 | 0.8075 | 0.2609 | 0.01066 | 0.2754 | 1 | 2.03 |
| graph_rd_joint | maze | 0.05 | 24 | 2 | 0.04125 | 0.8075 | 0.2609 | 0.009654 | 0.2432 | 1 | 2.053 |
| graph_rd_joint | maze | 0.05 | 24 | 5 | 0.02466 | 0.8075 | 0.4203 | 0.007876 | 0.177 | 1 | 0.6867 |
| graph_rd_joint | maze | 0.05 | 24 | 10 | 0.01812 | 0.7852 | 0.5797 | 0.005929 | 0.1237 | 1 | 0.0 |
| graph_rd_joint | maze | 0.05 | 24 | 20 | 0.01462 | 0.664 | 0.8551 | 0.004445 | 0.08735 | 1 | 0.006667 |
| graph_rd_joint | maze | 0.05 | 24 | 50 | 0.03795 | 0.4373 | 0.8696 | 0.003078 | 0.05497 | 1 | 0.0 |
