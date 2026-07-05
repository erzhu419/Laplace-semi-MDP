# Submission Main Table

Generated: 2026-07-05T19:22:30

This report is the paper-facing aggregation layer. It does not rerun heavy experiments; it reads the current public CSV artifacts and aligns the main runtime result, compact baselines, exhaustive-oracle solver validity, and certificate appendices.

- best certified adaptive total speedup with unique-top fallback: `3.698x`
- best certified adaptive total speedup with tie-aware certificate: `10.68x`
- worst certified adaptive start-value gap in that table: `0.07851`
- adaptive final certified decisions under unique-top fallback: `20/20`
- adaptive final certified decisions under tie-aware reporting: `20/20`
- larger group-constrained adaptive feasible rows: `6/6`
- exact Green is the reference operator; certified adaptive Green plus tie-aware top-set/epsilon certificates are the runtime implementation; fixed-K and weighted spectral certificates are ablations/appendix diagnostics.

## Main Runtime Table

| map | boundary_selector | method | n_states | n_boundary | state_compression_ratio | first_hit_used_steps_max | tail_bound_max | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | total_time_unique_top_fallback_sec | total_time_with_tie_certificate_sec | planning_speedup | total_speedup_unique_top_fallback | total_speedup_tie_aware | unique_top_break_even_tasks | amortization_break_even_tasks | start_gap | tie_mode | epsilon_optimal_certified | tie_set_certified | tie_aware_fallback_used | curvature_fallback_used | interval_certified | fallback_used | ambiguous_set_size | tie_aware_final_certified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | certified_adaptive_green_rd | 64 | 2 | 32 | 87 | 5.982e-07 | 0.08168 | 0.01215 | 9.527e-05 | 0.1421 | 0.01225 | 857.3 | 0.5749 | 6.668 | 2 | 1 | 2.946e-08 | epsilon_optimal_interval | True | True | False | False | False | True | 62 | True |
| corridor_64 | turn_articulation | certified_adaptive_green_rd | 64 | 2 | 32 | 87 | 5.982e-07 | 0.1006 | 0.01251 | 8.714e-05 | 0.1423 | 0.0126 | 1154 | 0.7066 | 7.981 | 2 | 1 | 2.946e-08 | epsilon_optimal_interval | True | True | False | False | False | True | 62 | True |
| corridor_128 | endpoints | certified_adaptive_green_rd | 128 | 2 | 64 | 160 | 7.468e-07 | 0.2938 | 0.03139 | 0.0001048 | 1.903 | 0.0315 | 2804 | 0.1544 | 9.327 | 7 | 1 | 1.024e-08 | epsilon_optimal_interval | True | True | False | False | False | True | 126 | True |
| corridor_128 | turn_articulation | certified_adaptive_green_rd | 128 | 2 | 64 | 160 | 7.468e-07 | 0.3624 | 0.03386 | 8.845e-05 | 5.223 | 0.03395 | 4097 | 0.06939 | 10.68 | 15 | 1 | 1.024e-08 | epsilon_optimal_interval | True | True | False | False | False | True | 126 | True |
| open_room_12 | endpoints | certified_adaptive_green_rd | 144 | 2 | 72 | 41 | 3.737e-07 | 0.09671 | 0.02606 | 8.801e-05 | 0.02615 | 0.02615 | 1099 | 3.698 | 3.698 | 1 | 1 | 0.07851 | unique_interval_top1 | True | False | False | False | True | False | 0 | True |
| open_room_12 | turn_articulation | certified_adaptive_green_rd | 144 | 4 | 36 | 38 | 8.604e-07 | 0.1401 | 0.06182 | 0.0007079 | 23.72 | 0.06253 | 197.9 | 0.005905 | 2.24 | 171 | 1 | 0.07851 | epsilon_optimal_interval | True | True | False | False | False | True | 140 | True |
| maze_13 | endpoints | certified_adaptive_green_rd | 71 | 2 | 35.5 | 42 | 4.298e-07 | 0.0677 | 0.009614 | 8.903e-05 | 0.09614 | 0.09614 | 760.4 | 0.7041 | 0.7041 | 2 | 2 | 1.548e-08 | curvature_exact_fallback | False | False | True | True | False | True | 69 | True |
| maze_13 | turn_articulation | certified_adaptive_green_rd | 71 | 18 | 3.944 | 24 | 9.741e-07 | 0.06422 | 0.2002 | 0.03605 | 0.9096 | 0.2362 | 1.781 | 0.07061 | 0.2719 | 32 | 8 | 7.147e-07 | epsilon_optimal_interval | True | True | False | False | False | True | 53 | True |

## Compact Baseline Aggregate

| method_spec | n_rows | median_state_compression | median_planning_speedup | median_total_speedup | max_start_gap | mean_success_rate | max_hidden_audit_distinct | group_feasible_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| betweenness_sqrt | 10 | 5.333 | 3.807 | 0.3402 | 0.04973 | 1 | 2 | nan |
| coverage_sqrt | 10 | 5.333 | 9.442 | 0.4021 | 0.04973 | 1 | 2 | nan |
| eigenoptions_sqrt | 10 | 5.333 | 3.165 | 0.3368 | 0.04973 | 1 | 3 | nan |
| full_vi | 10 | 1 | 1 | 1 | 0.0 | 1 | 0.0 | nan |
| graph_rd_joint | 10 | 12 | 91.62 | 0.07881 | 0.04973 | 1 | 2 | nan |
| graph_rd_surrogate_joint | 10 | 12 | 92.59 | 0.214 | 0.04973 | 1 | 2 | nan |
| group_constrained_rd | 10 | 10.5 | 25.09 | 0.01116 | 0.04973 | 1 | 3 | 0.9 |
| random_landmarks_sqrt | 10 | 5.333 | 4.893 | 0.3465 | 0.04973 | 1 | 3 | nan |

## Larger Group-Constrained Adaptive

| map | slip | method | n_states | n_basis | n_boundary | group_all_feasible | n_groups_feasible | group_total_violation | selection_time_sec | delta_backend | probe_green_kernel_time_sec | probe_operator_delta_time_sec | active_weight_time_sec | candidate_score_time_sec | probe_cache_hit_rate | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_tail_bound_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | False | 1 | 155.5 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02287 | 8.451e-05 | 636.4 | 2.343 | 1 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | True | 3 | 0.0 | 3.393 | operator | 1.287 | 0.9454 | 0.0 | 0.0008942 | 0.0 | 0.02966 | 0.001155 | 47.28 | 0.01595 | 65 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.0 | group_constrained_incremental | 144 | 24 | 3 | True | 3 | 0.0 | 1.493 | insertion_score | 0.03907 | 0.01097 | 0.04918 | 0.0008691 | 0.0 | 0.02899 | 0.0002627 | 233.3 | 0.04026 | 25 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | False | 0 | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02588 | 8.025e-05 | 1442 | 4.457 | 1 | 0.07851 | 3.737e-07 |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | True | 3 | 0.0 | 14.47 | operator | 5.257 | 4.158 | 0.0 | 0.002624 | 0.0 | 0.04639 | 0.002847 | 40.57 | 0.007959 | 129 | 0.07851 | 9.787e-07 |
| open_room_12 | 0.05 | group_constrained_incremental | 144 | 24 | 4 | True | 3 | 0.0 | 4.696 | insertion_score | 0.1122 | 0.03775 | 0.1023 | 0.001892 | 0.0 | 0.04455 | 0.002772 | 40.45 | 0.02364 | 44 | 0.07851 | 9.787e-07 |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | False | 1 | 155.5 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01908 | 8.066e-05 | 447.1 | 1.882 | 1 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | True | 3 | 0.0 | 2.043 | operator | 0.7261 | 0.5929 | 0.0 | 0.0009157 | 0.0 | 0.02844 | 0.000173 | 208.7 | 0.01743 | 58 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.0 | group_constrained_incremental | 104 | 29 | 3 | True | 3 | 0.0 | 0.9076 | insertion_score | 0.01755 | 0.01223 | 0.02391 | 0.000961 | 0.0 | 0.02837 | 0.000175 | 205 | 0.03831 | 27 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | False | 0 | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.02535 | 8.645e-05 | 922 | 3.134 | 1 | 0.05768 | 7.41e-07 |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | True | 3 | 0.0 | 9.718 | operator | 3.442 | 2.849 | 0.0 | 0.002826 | 0.0 | 0.06866 | 0.0007576 | 104.2 | 0.008062 | 126 | 0.05768 | 9.381e-07 |
| four_rooms_11 | 0.05 | group_constrained_incremental | 104 | 29 | 5 | True | 3 | 0.0 | 4.821 | insertion_score | 0.1158 | 0.09825 | 0.09189 | 0.003391 | 0.0 | 0.1352 | 0.004883 | 18.07 | 0.01779 | 60 | 0.05768 | 9.265e-07 |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | False | 1 | 155.5 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.01426 | 8.592e-05 | 398.1 | 2.384 | 1 | 7.105427357601002e-15 | 0.0 |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | True | 3 | 0.0 | 5.226 | operator | 2.064 | 1.429 | 0.0 | 0.003246 | 0.0 | 0.03877 | 0.001711 | 19.58 | 0.00636 | 166 | 3.552713678800501e-15 | 0.0 |
| maze_13 | 0.0 | group_constrained_incremental | 71 | 33 | 3 | True | 3 | 0.0 | 0.6764 | insertion_score | 0.009523 | 0.009816 | 0.03206 | 0.001024 | 0.0 | 0.02155 | 0.001261 | 26.89 | 0.04848 | 22 | 7.105427357601002e-15 | 0.0 |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | False | 0 | 233.2 | 0.0 |  | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0188 | 0.0001151 | 550 | 3.348 | 1 | 1.548e-08 | 4.298e-07 |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | True | 3 | 0.0 | 5.532 | operator | 1.962 | 1.623 | 0.0 | 0.002267 | 0.0 | 0.05175 | 0.002363 | 26.55 | 0.01123 | 93 | 4.297e-07 | 9.672e-07 |
| maze_13 | 0.05 | group_constrained_incremental | 71 | 33 | 3 | True | 3 | 0.0 | 1.054 | insertion_score | 0.009619 | 0.01091 | 0.01226 | 0.001102 | 0.0 | 0.03094 | 0.001674 | 37.97 | 0.05848 | 18 | 2.733e-07 | 7.73e-07 |

## Solver Validity Aggregate

| solver | beam_width | n_rows | boundary_match_rate | zero_total_violation_gap_rate | feasible_decision_match_rate | median_selection_time_sec | median_oracle_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| actual_refine | 1 | 3 | 1 | 1 | 1 | 3.668 | 10.95 |
| actual_refine | 2 | 3 | 1 | 1 | 1 | 4.063 | 10.95 |
| actual_refine | 4 | 3 | 1 | 1 | 1 | 4.054 | 10.95 |
| operator | 1 | 3 | 0.0 | 0.0 | 0.3333 | 0.9427 | 10.95 |
| operator | 2 | 3 | 0.6667 | 0.6667 | 0.6667 | 1.651 | 10.95 |
| operator | 4 | 3 | 1 | 1 | 1 | 1.6 | 10.95 |

## Discovery Profile Aggregate

| mode | n_rows | median_wall_time_sec | median_speedup_vs_full_recompute | max_speedup_vs_full_recompute | median_probe_green_kernel_time_sec | median_probe_operator_delta_time_sec | median_full_recompute_time_sec | median_candidate_score_time_sec | median_probe_cache_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cached_incremental_first | 6 | 0.3617 | 4.74 | 5.603 | 0.1236 | 0.108 | nan | 0.0003442 | 0.0 |
| cached_incremental_hit | 6 | 0.0003545 | 4776 | 7519 | 0.0 | 0.0 | nan | 0.0002474 | 1 |
| current_frozen_operator | 6 | 0.3614 | 4.736 | 5.608 | 0.1233 | 0.108 | nan | 0.0003723 | 0.0 |
| full_recompute | 6 | 1.691 | 1 | 1 | 0.125 | 0.1118 | 1.325 | 0.0003575 | 0.0 |

## Incremental Green Update Aggregate

| mode | n_rows | selected_state_match_rate | median_wall_time_sec | median_speedup_vs_full_recompute | max_speedup_vs_full_recompute | max_score_error_vs_exact | max_kernel_error_vs_exact | max_hidden_error_vs_exact | median_n_green_solves | median_n_green_updates | median_parent_update_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| boundary_insertion_score_update | 6 | 1.0 | 0.002205105673056096 | 6.1138616484194666 | 7.376957229810812 | 5.312703969195809e-06 | nan | 8.881784197001252e-16 | 12.0 | 139.0 | 1.0 |
| boundary_insertion_update | 6 | 1.0 | 0.01595097832614556 | 0.7525642597665083 | 0.8342300991313754 | 5.312703969195809e-06 | 1.3322676295501878e-15 | 8.881784197001252e-16 | 12.0 | 139.0 | 1.0 |
| current_frozen_operator | 6 | 0.3333333333333333 | 0.0058261186932213604 | 2.0784256763687954 | 2.286541564313952 | 233.17891857711604 | nan | 1.0 | 12.0 | 0.0 | 0.0 |
| full_recompute | 6 | 1.0 | 0.012428781890776008 | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 151.0 | 0.0 | 0.0 |
| static_basis_reuse | 6 | 1.0 | 0.005115150706842542 | 2.344762869362868 | 2.515053120630627 | 233.17891857711604 | nan | 1.0 | 12.0 | 0.0 | 0.0 |

## Certificate Appendix Summary

| certificate | rows | interval_certified | fallback_used | tie_fallback_used | curvature_fallback_used | tie_set_certified | epsilon_optimal_certified | final_certified | tie_aware_final_certified | row_q_lt_1_edges | weighted_q_lt_1_edges | certificates_found | rational_verified | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adaptive_frontier_tail_plus_top_set_fallback | 20 | 4 | 16 | 14 | 2 | 14 | 11 | 20 | 20 |  |  |  |  | runtime_decision_procedure |
| weighted_spectral_sufficient | 8 |  |  |  |  |  |  |  |  | 0 | 16 |  |  | appendix_sufficient_certificate |
| conditioned_rational_weighted_audit | 48 |  |  |  |  |  |  |  |  |  |  | 92 | 92 | appendix_reproducibility_audit |

## Source Artifacts

- large-scale adaptive: `experiments/output/large_scale_compression_adaptive/large_scale_compression.csv`
- core benchmark: `experiments/output/core_benchmark/core_benchmark.csv`
- adaptive certification: `experiments/output/adaptive_green_certification/certification_summary.csv`
- larger group-constrained adaptive: `experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv`
- solver validity: `experiments/output/solver_validity/solver_validity.csv`
- discovery profile/cache: `experiments/output/discovery_profile_cache/discovery_profile_cache.csv`
- incremental Green update: `experiments/output/incremental_green_update/incremental_green_update_aggregate.csv`
- incremental group semantic diff: `experiments/output/group_incremental_semantic_diff/summary.md`
- linear solver thread scaling: `experiments/output/linear_solver_thread_scaling/summary.md`
- weighted spectral certificate: `experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv`
- conditioned rational certificate: `experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv`
