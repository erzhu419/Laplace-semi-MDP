# Adaptive Green Certification

Generated: 2026-07-05T15:29:08
map_specs = ['corridor:128', 'open_room:12', 'maze:13', 'four_rooms:11']
boundary_methods = ['endpoints']
adaptive_tail_tols = [0.001, 1e-06]
candidate_universe = all

This table runs Certified Adaptive Green: adaptive intervals are accepted when they separate, otherwise exact Green is invoked on the ambiguous top set.

- exact top-1 matches: `8/8`
- interval-certified top-1 decisions: `4/8`
- rows using top-set fallback: `4/8`
- final certified decisions/top-sets: `8/8`
- time columns with `proxy` scale the exact reference time by ambiguous-set fraction; full exact fallback time is also in the CSV/JSON.

| map | boundary_method | tail_tol | n_states | n_boundary | n_candidates | used_steps_max | tail_bound_max | speedup_vs_exact | score_interval_max_width | top_state_adaptive | top_state_exact | top1_match_exact | top1_certified | top1_margin | top1_certified_margin | top1_margin_over_bound | fallback_used | fallback_reason | ambiguous_set_size | ambiguous_fraction | fallback_top_state | final_top_state | final_certificate | final_certified | fallback_global_certified | exact_tie_count | exact_top_margin | fallback_exact_time_proxy_sec | total_time_with_fallback_proxy_sec | speedup_with_fallback_proxy_vs_full_exact | max_abs_score_error_vs_exact | value_diff_vs_exact | status | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | 0.001 | 128 | 2 | 126 | 150 | 0.0005939 | 10.1 | 0.006856 | 1 | 1 | True | False | 0.0 | -0.006856 | 0.0 | True | tie_uncertified | 126 | 1 | 1 | 1 | exact_top_set_canonical_tie_break | True | True | 126 | 0.0 | 4.9 | 5.386 | 0.9099 | 0.0 | 1.249e-05 | ok | top_set_exact_fallback |
| corridor_128 | endpoints | 1e-06 | 128 | 2 | 126 | 160 | 7.468e-07 | 11.94 | 8.62e-06 | 1 | 1 | True | False | 0.0 | -8.62e-06 | 0.0 | True | tie_uncertified | 126 | 1 | 1 | 1 | exact_top_set_canonical_tie_break | True | True | 126 | 0.0 | 4.9 | 5.311 | 0.9227 | 0.0 | 1.028e-08 | ok | top_set_exact_fallback |
| open_room_12 | endpoints | 0.001 | 144 | 2 | 142 | 33 | 0.0009628 | 13.17 | 0.07038 | 132 | 132 | True | True | 21.27 | 21.2 | 151.1 | False | interval_certified | 0 | 0.0 |  | 132 | adaptive_interval_top1 | True |  | 1 | 21.27 | 0.0 | 0.2854 | 13.17 | 5.014975101857999e-10 | 4.766e-05 | ok | accept |
| open_room_12 | endpoints | 1e-06 | 144 | 2 | 142 | 41 | 8.604e-07 | 23.33 | 6.27e-05 | 132 | 132 | True | True | 21.27 | 21.27 | 1.696e+05 | False | interval_certified | 0 | 0.0 |  | 132 | adaptive_interval_top1 | True |  | 1 | 21.27 | 0.0 | 0.1611 | 23.33 | 1.3855583347321954e-13 | 1.773e-08 | ok | accept |
| maze_13 | endpoints | 0.001 | 71 | 2 | 69 | 7 | 0.0005685 | 0.9894 | 446.3 | 13 | 13 | True | False | 3.415 | -405.2 | 0.00418 | True | curvature_uncertified_full_set | 69 | 1 | 13 | 13 | exact_top_set_canonical_tie_break | True | True | 2 | 0.0 | 0.07948 | 0.1598 | 0.4973 | 187 |  | ok | top_set_exact_fallback |
| maze_13 | endpoints | 1e-06 | 71 | 2 | 69 | 12 | 5.594e-07 | 0.9968 | 282.5 | 13 | 13 | True | False | 7.739 | -238.8 | 0.01572 | True | curvature_uncertified_full_set | 69 | 1 | 13 | 13 | exact_top_set_canonical_tie_break | True | True | 2 | 0.0 | 0.07948 | 0.1592 | 0.4992 | 108.8 |  | ok | top_set_exact_fallback |
| four_rooms_11 | endpoints | 0.001 | 104 | 2 | 102 | 32 | 0.0006135 | 8.163 | 3.88 | 41 | 41 | True | True | 31 | 27.12 | 3.995 | False | interval_certified | 0 | 0.0 |  | 41 | adaptive_interval_top1 | True |  | 1 | 31 | 0.0 | 0.149 | 8.163 | 0.05433 | 2.943e-05 | ok | accept |
| four_rooms_11 | endpoints | 1e-06 | 104 | 2 | 102 | 39 | 7.41e-07 | 11.3 | 0.003979 | 41 | 41 | True | True | 31 | 31 | 3896 | False | interval_certified | 0 | 0.0 |  | 41 | adaptive_interval_top1 | True |  | 1 | 31 | 0.0 | 0.1077 | 11.3 | 2.568e-05 | 3.622e-08 | ok | accept |
