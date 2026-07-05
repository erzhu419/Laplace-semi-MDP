# RD Boundary Green Operator Checks

- recipe: `learned_rd_surrogate_joint_occ2_audit2`
- lambda_struct: 8.0
- edge_weight: `occupancy_or_uniform`
- with_actual_recompute: True
- elapsed_sec: 0.433

## Step Summary

- maze_9 step 0: top_fd=2 (1, 3) score=305, grad_match=True, actual_match=False, mean_grad_error=2.4e+11
- maze_9 step 1: top_fd=17 (5, 3) score=5.649, grad_match=True, actual_match=False, mean_grad_error=1.32e-08

## Truncation Summary

- maze_9 K=4: top1_match_rate=1, mean_abs_error=0.00786
- maze_9 K=8: top1_match_rate=1, mean_abs_error=3.25e-05
