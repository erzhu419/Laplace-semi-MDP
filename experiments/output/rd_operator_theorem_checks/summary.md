# RD Boundary Green Operator Checks

- recipe: `learned_rd_surrogate_joint_occ2_audit2`
- lambda_struct: 8.0
- edge_weight: `occupancy_or_uniform`
- with_frozen_recompute: True
- with_actual_recompute: False
- with_recompute_modes: False
- elapsed_sec: 22.835

## Step Summary

- maze_13 step 0: top_fd=13 (3, 1) score=303.8, margin=0.0, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=False, frozen_match=True, actual_match=None, mean_grad_error=9.02e+10, max_fd_minus_frozen=7.993605777301127e-15, max_adaptive_drift=None, actual_regret_fd=None
- maze_13 step 1: top_fd=17 (3, 5) score=4.369, margin=11.541560819493098, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=4.39e-09, max_fd_minus_frozen=1.865174681370263e-14, max_adaptive_drift=None, actual_regret_fd=None
- maze_13 step 2: top_fd=3 (1, 5) score=-6.896, margin=0.0, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=0, max_fd_minus_frozen=3.552713678800501e-15, max_adaptive_drift=None, actual_regret_fd=None
- maze_13 step 3: top_fd=5 (1, 7) score=-6.866, margin=0.0, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=0, max_fd_minus_frozen=3.552713678800501e-15, max_adaptive_drift=None, actual_regret_fd=None
- maze_13 step 4: top_fd=8 (1, 11) score=-6.963, margin=0.0, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=False, actual_match=None, mean_grad_error=0, max_fd_minus_frozen=3.9399594697897555e-12, max_adaptive_drift=None, actual_regret_fd=None
- four_rooms_13 step 0: top_fd=61 (6, 1) score=55.01, margin=28.42103967174264, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=25.6, max_fd_minus_frozen=8.881784197001252e-15, max_adaptive_drift=None, actual_regret_fd=None
- four_rooms_13 step 1: top_fd=142 (13, 8) score=24.67, margin=32.79593479318004, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=1.67, max_fd_minus_frozen=5.3290705182007514e-14, max_adaptive_drift=None, actual_regret_fd=None
- four_rooms_13 step 2: top_fd=80 (8, 6) score=-7.993, margin=0.0006151347885197112, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=4.97e-08, max_fd_minus_frozen=5.509370737399877e-12, max_adaptive_drift=None, actual_regret_fd=None
- four_rooms_13 step 3: top_fd=67 (6, 8) score=-7.975, margin=0.00309038238178605, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=3.05e-08, max_fd_minus_frozen=1.092459456231154e-13, max_adaptive_drift=None, actual_regret_fd=None
- four_rooms_13 step 4: top_fd=66 (6, 6) score=-8.087, margin=6.212749347866975e-05, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=1.21e-08, max_fd_minus_frozen=9.414691248821327e-14, max_adaptive_drift=None, actual_regret_fd=None
- open_room_9 step 0: top_fd=72 (9, 1) score=17.11, margin=24.415139117346186, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=3.73, max_fd_minus_frozen=1.326050380612287e-12, max_adaptive_drift=None, actual_regret_fd=None
- open_room_9 step 1: top_fd=8 (1, 9) score=-7.37, margin=None, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=None, mean_grad_error=0, max_fd_minus_frozen=1.7141843500212417e-13, max_adaptive_drift=None, actual_regret_fd=None
- open_room_9 step 2: top_fd=None None score=0, margin=None, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=False, frozen_match=None, actual_match=None, mean_grad_error=0, max_fd_minus_frozen=None, max_adaptive_drift=None, actual_regret_fd=None

## Baseline Ranking Summary

- maze_13 step 0: raw=57 match=False regret=None, spectral=19 match=False regret=None, betweenness=57 match=False regret=None, value_grad=57 match=False regret=None, random=5 match=False regret=None
- maze_13 step 1: raw=17 match=True regret=None, spectral=19 match=False regret=None, betweenness=57 match=False regret=None, value_grad=57 match=False regret=None, random=3 match=False regret=None
- maze_13 step 2: raw=3 match=True regret=None, spectral=19 match=False regret=None, betweenness=57 match=False regret=None, value_grad=57 match=False regret=None, random=5 match=False regret=None
- maze_13 step 3: raw=5 match=True regret=None, spectral=19 match=False regret=None, betweenness=57 match=False regret=None, value_grad=57 match=False regret=None, random=8 match=False regret=None
- maze_13 step 4: raw=8 match=True regret=None, spectral=19 match=False regret=None, betweenness=57 match=False regret=None, value_grad=57 match=False regret=None, random=19 match=False regret=None
- four_rooms_13 step 0: raw=61 match=True regret=None, spectral=81 match=False regret=None, betweenness=66 match=False regret=None, value_grad=86 match=False regret=None, random=141 match=False regret=None
- four_rooms_13 step 1: raw=142 match=True regret=None, spectral=81 match=False regret=None, betweenness=66 match=False regret=None, value_grad=86 match=False regret=None, random=5 match=False regret=None
- four_rooms_13 step 2: raw=80 match=True regret=None, spectral=81 match=False regret=None, betweenness=66 match=False regret=None, value_grad=86 match=False regret=None, random=6 match=False regret=None
- four_rooms_13 step 3: raw=67 match=True regret=None, spectral=81 match=False regret=None, betweenness=66 match=False regret=None, value_grad=86 match=False regret=None, random=141 match=False regret=None
- four_rooms_13 step 4: raw=66 match=True regret=None, spectral=81 match=False regret=None, betweenness=66 match=True regret=None, value_grad=86 match=False regret=None, random=136 match=False regret=None
- open_room_9 step 0: raw=72 match=True regret=None, spectral=72 match=True regret=None, betweenness=8 match=False regret=None, value_grad=8 match=False regret=None, random=72 match=True regret=None
- open_room_9 step 1: raw=8 match=True regret=None, spectral=8 match=True regret=None, betweenness=8 match=True regret=None, value_grad=8 match=True regret=None, random=8 match=True regret=None
- open_room_9 step 2: raw=None match=None regret=None, spectral=None match=None regret=None, betweenness=None match=None regret=None, value_grad=None match=None regret=None, random=None match=None regret=None

## Runtime Summary

- maze_13 step 0: base_eval=0.06387s, fd_grad_score=0.103s, actual_recompute=0s, recompute_over_operator=nan
- maze_13 step 1: base_eval=0.1182s, fd_grad_score=0.08681s, actual_recompute=0s, recompute_over_operator=nan
- maze_13 step 2: base_eval=0.1322s, fd_grad_score=0.1161s, actual_recompute=0s, recompute_over_operator=nan
- maze_13 step 3: base_eval=0.1375s, fd_grad_score=0.1133s, actual_recompute=0s, recompute_over_operator=nan
- maze_13 step 4: base_eval=0.1804s, fd_grad_score=0.1157s, actual_recompute=0s, recompute_over_operator=nan
- four_rooms_13 step 0: base_eval=1.443s, fd_grad_score=0.2713s, actual_recompute=0s, recompute_over_operator=nan
- four_rooms_13 step 1: base_eval=0.9925s, fd_grad_score=0.1693s, actual_recompute=0s, recompute_over_operator=nan
- four_rooms_13 step 2: base_eval=4.666s, fd_grad_score=0.1625s, actual_recompute=0s, recompute_over_operator=nan
- four_rooms_13 step 3: base_eval=2.253s, fd_grad_score=0.1518s, actual_recompute=0s, recompute_over_operator=nan
- four_rooms_13 step 4: base_eval=10.24s, fd_grad_score=0.1852s, actual_recompute=0s, recompute_over_operator=nan
- open_room_9 step 0: base_eval=0.06149s, fd_grad_score=0.05723s, actual_recompute=0s, recompute_over_operator=nan
- open_room_9 step 1: base_eval=0.1128s, fd_grad_score=0.08874s, actual_recompute=0s, recompute_over_operator=nan
- open_room_9 step 2: base_eval=0s, fd_grad_score=0s, actual_recompute=0s, recompute_over_operator=nan

## Truncation Summary

- four_rooms_13 K=4: top1_match_rate=0.4, mean_abs_error=0.0179, mean_time=0.004219s
- four_rooms_13 K=8: top1_match_rate=0.4, mean_abs_error=0.0157, mean_time=0.004473s
- four_rooms_13 K=16: top1_match_rate=1, mean_abs_error=0.00355, mean_time=0.005303s
- four_rooms_13 K=32: top1_match_rate=1, mean_abs_error=1.9e-08, mean_time=0.004851s
- maze_13 K=4: top1_match_rate=0.6, mean_abs_error=0.00105, mean_time=0.002986s
- maze_13 K=8: top1_match_rate=0.8, mean_abs_error=4.34e-06, mean_time=0.004314s
- maze_13 K=16: top1_match_rate=0.8, mean_abs_error=6.84e-11, mean_time=0.003985s
- maze_13 K=32: top1_match_rate=0.8, mean_abs_error=8.6e-18, mean_time=0.003665s
- open_room_9 K=4: top1_match_rate=0.667, mean_abs_error=0.147, mean_time=0.001303s
- open_room_9 K=8: top1_match_rate=1, mean_abs_error=0.0194, mean_time=0.001256s
- open_room_9 K=16: top1_match_rate=1, mean_abs_error=9.55e-07, mean_time=0.0015s
- open_room_9 K=32: top1_match_rate=1, mean_abs_error=2.44e-15, mean_time=0.002704s
