# RD Boundary Green Operator Checks

- recipe: `learned_rd_surrogate_joint_occ2_audit2`
- lambda_struct: 8.0
- edge_weight: `occupancy_or_uniform`
- with_actual_recompute: False
- elapsed_sec: 6.362

## Step Summary

- maze_13 step 0: top_fd=13 (3, 1) score=303.8, grad_match=False, actual_match=None, mean_grad_error=9.02e+10
- maze_13 step 1: top_fd=17 (3, 5) score=4.369, grad_match=True, actual_match=None, mean_grad_error=4.39e-09
- maze_13 step 2: top_fd=3 (1, 5) score=-6.896, grad_match=True, actual_match=None, mean_grad_error=0
- maze_13 step 3: top_fd=5 (1, 7) score=-6.866, grad_match=True, actual_match=None, mean_grad_error=0
- four_rooms_13 step 0: top_fd=61 (6, 1) score=55.01, grad_match=True, actual_match=None, mean_grad_error=25.6
- four_rooms_13 step 1: top_fd=142 (13, 8) score=24.67, grad_match=True, actual_match=None, mean_grad_error=1.67
- four_rooms_13 step 2: top_fd=80 (8, 6) score=-7.993, grad_match=True, actual_match=None, mean_grad_error=4.97e-08
- four_rooms_13 step 3: top_fd=67 (6, 8) score=-7.975, grad_match=True, actual_match=None, mean_grad_error=3.05e-08
- open_room_9 step 0: top_fd=72 (9, 1) score=17.11, grad_match=True, actual_match=None, mean_grad_error=3.73
- open_room_9 step 1: top_fd=8 (1, 9) score=-7.37, grad_match=True, actual_match=None, mean_grad_error=0
- open_room_9 step 2: top_fd=None None score=0, grad_match=False, actual_match=None, mean_grad_error=0

## Truncation Summary

- four_rooms_13 K=4: top1_match_rate=0.25, mean_abs_error=0.0223
- four_rooms_13 K=8: top1_match_rate=0.25, mean_abs_error=0.0197
- four_rooms_13 K=16: top1_match_rate=1, mean_abs_error=0.00443
- maze_13 K=4: top1_match_rate=0.75, mean_abs_error=0.00131
- maze_13 K=8: top1_match_rate=0.75, mean_abs_error=5.42e-06
- maze_13 K=16: top1_match_rate=0.75, mean_abs_error=8.55e-11
- open_room_9 K=4: top1_match_rate=0.667, mean_abs_error=0.147
- open_room_9 K=8: top1_match_rate=1, mean_abs_error=0.0194
- open_room_9 K=16: top1_match_rate=1, mean_abs_error=9.55e-07
