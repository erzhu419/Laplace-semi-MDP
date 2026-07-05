# RD Boundary Green Operator Checks

- recipe: `learned_rd_surrogate_joint_occ2_audit2`
- lambda_struct: 8.0
- edge_weight: `occupancy_or_uniform`
- with_frozen_recompute: True
- with_actual_recompute: True
- with_recompute_modes: True
- elapsed_sec: 4.412

## Step Summary

- maze_9 step 0: top_fd=2 (1, 3) score=305, margin=3.3639935281826183e-10, eps_adapt=1252.020899077906, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=False, mean_grad_error=2.4e+11, max_fd_minus_frozen=5.684341886080802e-14, max_adaptive_drift=1252.020899077906, actual_regret_fd=11.541317057384276
- maze_9 step 1: top_fd=17 (5, 3) score=5.649, margin=11.541560819493098, eps_adapt=19.941560806117188, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=False, mean_grad_error=1.32e-08, max_fd_minus_frozen=3.552713678800501e-15, max_adaptive_drift=19.941560806117188, actual_regret_fd=13.287982617669698
- maze_9 step 2: top_fd=21 (5, 7) score=5.957, margin=11.541560806151802, eps_adapt=7.5469115218154315, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=False, mean_grad_error=1.69e-08, max_fd_minus_frozen=3.552713678800501e-15, max_adaptive_drift=7.5469115218154315, actual_regret_fd=0.8933322397013796
- four_rooms_9 step 0: top_fd=25 (4, 1) score=67.43, margin=35.114647817820305, eps_adapt=56.330882055461416, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=False, mean_grad_error=78.5, max_fd_minus_frozen=7.105427357601002e-15, max_adaptive_drift=56.330882055461416, actual_regret_fd=5.969504279199384
- four_rooms_9 step 1: top_fd=64 (9, 6) score=30.85, margin=29.788482083904924, eps_adapt=18.113339037104694, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=True, mean_grad_error=3.02, max_fd_minus_frozen=1.5987211554602254e-14, max_adaptive_drift=18.113339037104694, actual_regret_fd=0.0
- four_rooms_9 step 2: top_fd=38 (6, 4) score=-6.419, margin=0.19643791482632178, eps_adapt=18.11333573375542, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=False, mean_grad_error=0.000112, max_fd_minus_frozen=8.954614827416663e-12, max_adaptive_drift=18.11333573375542, actual_regret_fd=0.842192996853484
- open_room_7 step 0: top_fd=42 (7, 1) score=20.82, margin=27.376403193008652, eps_adapt=4.526666666685177, stable_if_margin=True, stable_ok=True, grad_match=True, frozen_match=True, actual_match=True, mean_grad_error=5.3, max_fd_minus_frozen=6.217248937900877e-15, max_adaptive_drift=4.526666666685177, actual_regret_fd=0.0
- open_room_7 step 1: top_fd=6 (1, 7) score=-6.609, margin=None, eps_adapt=3.6533333333333324, stable_if_margin=False, stable_ok=None, grad_match=True, frozen_match=True, actual_match=True, mean_grad_error=2.22e-16, max_fd_minus_frozen=8.881784197001252e-16, max_adaptive_drift=3.6533333333333324, actual_regret_fd=0.0
- open_room_7 step 2: top_fd=None None score=0, margin=None, eps_adapt=None, stable_if_margin=False, stable_ok=None, grad_match=False, frozen_match=None, actual_match=None, mean_grad_error=0, max_fd_minus_frozen=None, max_adaptive_drift=None, actual_regret_fd=None

## Baseline Ranking Summary

- maze_9 step 0: raw=2 match=True regret=11.541317057384276, spectral=21 match=False regret=0.02000218671798848, betweenness=21 match=False regret=0.02000218671798848, value_grad=21 match=False regret=0.02000218671798848, random=5 match=False regret=1864.558015283549
- maze_9 step 1: raw=17 match=True regret=13.287982617669698, spectral=21 match=False regret=12.434649297712276, betweenness=21 match=False regret=12.434649297712276, value_grad=21 match=False regret=12.434649297712276, random=21 match=False regret=12.434649297712276
- maze_9 step 2: raw=21 match=True regret=0.8933322397013796, spectral=21 match=True regret=0.8933322397013796, betweenness=21 match=True regret=0.8933322397013796, value_grad=21 match=True regret=0.8933322397013796, random=5 match=False regret=0.0
- four_rooms_9 step 0: raw=25 match=True regret=5.969504279199384, spectral=39 match=False regret=35.41540614280561, betweenness=28 match=False regret=36.226081990870654, value_grad=42 match=False regret=40.47648767372581, random=35 match=False regret=40.37400700775788
- four_rooms_9 step 1: raw=64 match=True regret=0.0, spectral=39 match=False regret=34.24573307883976, betweenness=28 match=False regret=35.07324992245246, value_grad=42 match=False regret=39.07729810040891, random=63 match=False regret=37.86401395107606
- four_rooms_9 step 2: raw=38 match=True regret=0.842192996853484, spectral=39 match=False regret=1.0462711113037244, betweenness=28 match=False regret=2.518138210457863, value_grad=42 match=False regret=1.9931475831463104, random=3 match=False regret=0.00010900937620306195
- open_room_7 step 0: raw=42 match=True regret=0.0, spectral=42 match=True regret=0.0, betweenness=6 match=False regret=26.503069859656808, value_grad=6 match=False regret=26.503069859656808, random=6 match=False regret=26.503069859656808
- open_room_7 step 1: raw=6 match=True regret=0.0, spectral=6 match=True regret=0.0, betweenness=6 match=True regret=0.0, value_grad=6 match=True regret=0.0, random=6 match=True regret=0.0
- open_room_7 step 2: raw=None match=None regret=None, spectral=None match=None regret=None, betweenness=None match=None regret=None, value_grad=None match=None regret=None, random=None match=None regret=None

## Runtime Summary

- maze_9 step 0: base_eval=0.01941s, fd_grad_score=0.01783s, actual_recompute=0.1546s, recompute_over_operator=8.670526039635849
- maze_9 step 1: base_eval=0.03517s, fd_grad_score=0.01711s, actual_recompute=0.2002s, recompute_over_operator=11.698800715811657
- maze_9 step 2: base_eval=0.04431s, fd_grad_score=0.01807s, actual_recompute=0.1746s, recompute_over_operator=9.662729836289282
- four_rooms_9 step 0: base_eval=0.05176s, fd_grad_score=0.051s, actual_recompute=0.7551s, recompute_over_operator=14.807454151490345
- four_rooms_9 step 1: base_eval=0.06273s, fd_grad_score=0.05215s, actual_recompute=0.9483s, recompute_over_operator=18.183924635695355
- four_rooms_9 step 2: base_eval=0.07962s, fd_grad_score=0.05625s, actual_recompute=1.185s, recompute_over_operator=21.06483889012767
- open_room_7 step 0: base_eval=0.033s, fd_grad_score=0.02918s, actual_recompute=0.08114s, recompute_over_operator=2.7811178624863095
- open_room_7 step 1: base_eval=0.04042s, fd_grad_score=0.02954s, actual_recompute=0.05211s, recompute_over_operator=1.7639235079084858
- open_room_7 step 2: base_eval=0s, fd_grad_score=0s, actual_recompute=0s, recompute_over_operator=nan

## Recompute Mode Summary

- maze_9 step 0: rate_match=True, occ_match=True, edge_match=True, edge_option_match=False, tau_actual=0.5
- maze_9 step 1: rate_match=True, occ_match=True, edge_match=True, edge_option_match=False, tau_actual=-1.0
- maze_9 step 2: rate_match=True, occ_match=True, edge_match=True, edge_option_match=False, tau_actual=-0.3333333333333333
- four_rooms_9 step 0: rate_match=True, occ_match=True, edge_match=True, edge_option_match=True, tau_actual=0.6060606060606061
- four_rooms_9 step 1: rate_match=True, occ_match=True, edge_match=True, edge_option_match=False, tau_actual=0.5454545454545454
- four_rooms_9 step 2: rate_match=False, occ_match=True, edge_match=True, edge_option_match=True, tau_actual=-0.12121212121212122
- open_room_7 step 0: rate_match=True, occ_match=True, edge_match=True, edge_option_match=True, tau_actual=1.0
- open_room_7 step 1: rate_match=True, occ_match=True, edge_match=True, edge_option_match=True, tau_actual=None
- open_room_7 step 2: rate_match=None, occ_match=None, edge_match=None, edge_option_match=None, tau_actual=None

## Truncation Summary

- four_rooms_9 K=4: top1_match_rate=0.333, mean_abs_error=0.0264, mean_time=0.0008007s
- four_rooms_9 K=8: top1_match_rate=0.667, mean_abs_error=0.0246, mean_time=0.0007852s
- four_rooms_9 K=16: top1_match_rate=1, mean_abs_error=4.84e-05, mean_time=0.0009052s
- four_rooms_9 K=32: top1_match_rate=1, mean_abs_error=2.69e-12, mean_time=0.0009282s
- maze_9 K=4: top1_match_rate=1, mean_abs_error=0.0116, mean_time=0.0004728s
- maze_9 K=8: top1_match_rate=1, mean_abs_error=5.23e-05, mean_time=0.0004631s
- maze_9 K=16: top1_match_rate=1, mean_abs_error=1.08e-09, mean_time=0.0005086s
- maze_9 K=32: top1_match_rate=1, mean_abs_error=9.31e-17, mean_time=0.0006457s
- open_room_7 K=4: top1_match_rate=0.667, mean_abs_error=0.151, mean_time=0.0006216s
- open_room_7 K=8: top1_match_rate=1, mean_abs_error=0.00107, mean_time=0.0006724s
- open_room_7 K=16: top1_match_rate=1, mean_abs_error=2.42e-08, mean_time=0.0006506s
- open_room_7 K=32: top1_match_rate=1, mean_abs_error=1.48e-16, mean_time=0.000719s
