# Submission Main Table

Generated: 2026-07-05T15:59:12

This report is the paper-facing aggregation layer. It does not rerun heavy experiments; it reads the current public CSV artifacts and aligns the main runtime result, compact baselines, exhaustive-oracle solver validity, and certificate appendices.

- best certified adaptive total speedup in the large-scale table: `3.698x`
- worst certified adaptive start-value gap in that table: `0.07851`
- adaptive final certified decisions: `20/20`
- exact Green is the reference operator; certified adaptive Green plus top-set exact fallback is the runtime implementation; fixed-K and weighted spectral certificates are ablations/appendix diagnostics.

## Main Runtime Table

| map | boundary_selector | method | n_states | n_boundary | state_compression_ratio | first_hit_used_steps_max | tail_bound_max | full_vi_time_sec | upfront_time_sec | smdp_solve_time_sec | total_time_with_fallback_proxy_sec | planning_speedup | total_speedup | start_gap | interval_certified | fallback_used | ambiguous_set_size | final_certified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_64 | endpoints | certified_adaptive_green_rd | 64 | 2 | 32 | 87 | 5.982e-07 | 0.08168 | 0.01215 | 9.527e-05 | 0.1322 | 857.3 | 0.6178 | 2.946e-08 | False | True | 62 | True |
| corridor_64 | turn_articulation | certified_adaptive_green_rd | 64 | 2 | 32 | 87 | 5.982e-07 | 0.1006 | 0.01251 | 8.714e-05 | 0.1413 | 1154 | 0.7116 | 2.946e-08 | False | True | 62 | True |
| corridor_128 | endpoints | certified_adaptive_green_rd | 128 | 2 | 64 | 160 | 7.468e-07 | 0.2938 | 0.03139 | 0.0001048 | 5.32 | 2804 | 0.05522 | 1.024e-08 | False | True | 126 | True |
| corridor_128 | turn_articulation | certified_adaptive_green_rd | 128 | 2 | 64 | 160 | 7.468e-07 | 0.3624 | 0.03386 | 8.845e-05 | 1.864 | 4097 | 0.1944 | 1.024e-08 | False | True | 126 | True |
| open_room_12 | endpoints | certified_adaptive_green_rd | 144 | 2 | 72 | 41 | 3.737e-07 | 0.09671 | 0.02606 | 8.801e-05 | 0.02615 | 1099 | 3.698 | 0.07851 | True | False | 0 | True |
| open_room_12 | turn_articulation | certified_adaptive_green_rd | 144 | 4 | 36 | 38 | 8.604e-07 | 0.1401 | 0.06182 | 0.0007079 | 9.394 | 197.9 | 0.01491 | 0.07851 | False | True | 140 | True |
| maze_13 | endpoints | certified_adaptive_green_rd | 71 | 2 | 35.5 | 42 | 4.298e-07 | 0.0677 | 0.009614 | 8.903e-05 | 0.08879 | 760.4 | 0.7624 | 1.548e-08 | False | True | 69 | True |
| maze_13 | turn_articulation | certified_adaptive_green_rd | 71 | 18 | 3.944 | 24 | 9.741e-07 | 0.06422 | 0.2002 | 0.03605 | 0.8148 | 1.781 | 0.07882 | 7.147e-07 | False | True | 53 | True |

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

| certificate | rows | interval_certified | fallback_used | final_certified | row_q_lt_1_edges | weighted_q_lt_1_edges | certificates_found | rational_verified | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adaptive_frontier_tail_plus_top_set_fallback | 20 | 4 | 16 | 20 |  |  |  |  | runtime_decision_procedure |
| weighted_spectral_sufficient | 8 |  |  |  | 0 | 16 |  |  | appendix_sufficient_certificate |
| conditioned_rational_weighted_audit | 48 |  |  |  |  |  | 92 | 92 | appendix_reproducibility_audit |

## Source Artifacts

- large-scale adaptive: `experiments/output/large_scale_compression_adaptive/large_scale_compression.csv`
- core benchmark: `experiments/output/core_benchmark/core_benchmark.csv`
- adaptive certification: `experiments/output/adaptive_green_certification/certification_summary.csv`
- solver validity: `experiments/output/solver_validity/solver_validity.csv`
- weighted spectral certificate: `experiments/output/weighted_spectral_certificate/spectral_certificate_summary.csv`
- conditioned rational certificate: `experiments/output/conditioned_weighted_certificate/conditioned_certificate_summary.csv`
