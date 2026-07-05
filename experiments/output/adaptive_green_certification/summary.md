# Adaptive Green Certification

Generated: 2026-07-05T15:13:00
map_specs = ['corridor:128', 'open_room:12', 'maze:13', 'four_rooms:11']
boundary_methods = ['endpoints']
adaptive_tail_tols = [0.001, 1e-06]
candidate_universe = all

This table checks whether adaptive Green score intervals are narrow enough to certify the top RD split without falling back to exact Green.

- exact top-1 matches: `8/8`
- interval-certified top-1 decisions: `4/8`
- uncertified rows should refine the tolerance/horizon or use exact Green on the ambiguous top set.

| map | boundary_method | tail_tol | n_states | n_boundary | n_candidates | used_steps_max | tail_bound_max | speedup_vs_exact | score_interval_max_width | top_state_adaptive | top_state_exact | top1_match_exact | top1_certified | top1_margin | top1_certified_margin | top1_margin_over_bound | max_abs_score_error_vs_exact | value_diff_vs_exact | status | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | endpoints | 0.001 | 128 | 2 | 126 | 150 | 0.0005939 | 7.683 | 0.006856 | 1 | 1 | True | False | 0.0 | -0.006856 | 0.0 | 0.0 | 1.249e-05 | ok | needs_refinement_or_exact_fallback |
| corridor_128 | endpoints | 1e-06 | 128 | 2 | 126 | 160 | 7.468e-07 | 8.431 | 8.62e-06 | 1 | 1 | True | False | 0.0 | -8.62e-06 | 0.0 | 0.0 | 1.028e-08 | ok | needs_refinement_or_exact_fallback |
| open_room_12 | endpoints | 0.001 | 144 | 2 | 142 | 33 | 0.0009628 | 14.65 | 0.07038 | 132 | 132 | True | True | 21.27 | 21.2 | 151.1 | 5.014975101857999e-10 | 4.766e-05 | ok | accept |
| open_room_12 | endpoints | 1e-06 | 144 | 2 | 142 | 41 | 8.604e-07 | 17.53 | 6.27e-05 | 132 | 132 | True | True | 21.27 | 21.27 | 1.696e+05 | 1.3855583347321954e-13 | 1.773e-08 | ok | accept |
| maze_13 | endpoints | 0.001 | 71 | 2 | 69 | 7 | 0.0005685 | 1.024 | 446.3 | 13 | 13 | True | False | 3.415 | -405.2 | 0.00418 | 187 |  | ok | needs_refinement_or_exact_fallback |
| maze_13 | endpoints | 1e-06 | 71 | 2 | 69 | 12 | 5.594e-07 | 1.005 | 282.5 | 13 | 13 | True | False | 7.739 | -238.8 | 0.01572 | 108.8 |  | ok | needs_refinement_or_exact_fallback |
| four_rooms_11 | endpoints | 0.001 | 104 | 2 | 102 | 32 | 0.0006135 | 6.611 | 3.88 | 41 | 41 | True | True | 31 | 27.12 | 3.995 | 0.05433 | 2.943e-05 | ok | accept |
| four_rooms_11 | endpoints | 1e-06 | 104 | 2 | 102 | 39 | 7.41e-07 | 8.811 | 0.003979 | 41 | 41 | True | True | 31 | 31 | 3896 | 2.568e-05 | 3.622e-08 | ok | accept |
