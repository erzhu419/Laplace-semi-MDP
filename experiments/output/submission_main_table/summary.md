# Submission Main Table

Generated: 2026-07-05T16:44:01

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

| map | slip | method | n_states | n_basis | n_boundary | group_all_feasible | n_groups_feasible | group_total_violation | selection_time_sec | kernel_time_sec | smdp_solve_time_sec | planning_speedup | total_speedup | break_even_tasks | start_gap | first_hit_tail_bound_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_12 | 0.0 | endpoints | 144 | 24 | 2 | False | 1 | 155.5 | 0.0 | 0.02574 | 9.427e-05 | 609.3 | 2.224 | 1 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.0 | group_constrained | 144 | 24 | 3 | True | 3 | 0.0 | 46.35 | 0.03248 | 0.001132 | 50.45 | 0.001231 | 829 | 3.552713678800501e-15 | 0.0 |
| open_room_12 | 0.05 | endpoints | 144 | 24 | 2 | False | 0 | 233.2 | 0.0 | 0.033 | 0.0001743 | 814.8 | 4.281 | 1 | 0.07851 | 3.737e-07 |
| open_room_12 | 0.05 | group_constrained | 144 | 24 | 4 | True | 3 | 0.0 | 106.1 | 0.04974 | 0.002978 | 39.69 | 0.001114 | 922 | 0.07851 | 9.787e-07 |
| four_rooms_11 | 0.0 | endpoints | 104 | 29 | 2 | False | 1 | 155.5 | 0.0 | 0.0215 | 8.948e-05 | 449.4 | 1.863 | 1 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.0 | group_constrained | 104 | 29 | 3 | True | 3 | 0.0 | 4.959 | 0.03197 | 0.0001941 | 232.2 | 0.009028 | 112 | 5.329070518200751e-15 | 0.0 |
| four_rooms_11 | 0.05 | endpoints | 104 | 29 | 2 | False | 0 | 233.2 | 0.0 | 0.0284 | 9.346e-05 | 896.5 | 2.941 | 1 | 0.05768 | 7.41e-07 |
| four_rooms_11 | 0.05 | group_constrained | 104 | 29 | 4 | True | 3 | 0.0 | 14.49 | 0.075 | 0.0007895 | 105 | 0.00569 | 178 | 0.05768 | 9.381e-07 |
| maze_13 | 0.0 | endpoints | 71 | 33 | 2 | False | 1 | 155.5 | 0.0 | 0.0202 | 8.807e-05 | 412.9 | 1.793 | 1 | 7.105427357601002e-15 | 0.0 |
| maze_13 | 0.0 | group_constrained | 71 | 33 | 5 | True | 3 | 0.0 | 11.03 | 0.05935 | 0.001989 | 24.65 | 0.004419 | 236 | 3.552713678800501e-15 | 0.0 |
| maze_13 | 0.05 | endpoints | 71 | 33 | 2 | False | 0 | 233.2 | 0.0 | 0.02127 | 8.96e-05 | 735.2 | 3.085 | 1 | 1.548e-08 | 4.298e-07 |
| maze_13 | 0.05 | group_constrained | 71 | 33 | 4 | True | 3 | 0.0 | 9.986 | 0.06452 | 0.002901 | 23.17 | 0.006685 | 157 | 4.297e-07 | 9.672e-07 |

## Solver Validity Aggregate

| solver | beam_width | n_rows | boundary_match_rate | zero_total_violation_gap_rate | feasible_decision_match_rate | median_selection_time_sec | median_oracle_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| actual_refine | 1 | 3 | 1 | 1 | 1 | 3.668 | 10.95 |
| actual_refine | 2 | 3 | 1 | 1 | 1 | 4.063 | 10.95 |
| actual_refine | 4 | 3 | 1 | 1 | 1 | 4.054 | 10.95 |
| operator | 1 | 3 | 0.0 | 0.0 | 0.3333 | 0.9427 | 10.95 |
| operator | 2 | 3 | 0.6667 | 0.6667 | 0.6667 | 1.651 | 10.95 |
| operator | 4 | 3 | 1 | 1 | 1 | 1.6 | 10.95 |

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
- weighted spectral certificate: `experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv`
- conditioned rational certificate: `experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv`
