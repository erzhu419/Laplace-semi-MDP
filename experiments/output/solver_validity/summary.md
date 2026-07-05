# Solver Validity

Generated: 2026-07-05T15:59:10
map_specs = ['open_room:5', 'four_rooms:7', 'maze:9']
solvers = ['operator', 'actual_refine']
beam_widths = [1, 2, 4], beam_expand = 6
max_extra_splits = 2, max_oracle_candidates = 6

For small candidate universes this exhaustively enumerates every subset up to the split budget, then compares operator-only and exact-refined beam group-constrained RD against that oracle. The exact-refined solver uses the frozen operator only to propose a small expansion set, then ranks those expansions by actual group RD evaluation.

- exact boundary matches: `14/18`
- zero total-violation gap rows: `14/18`
- feasible/infeasible decision matches: `15/18`
- oracle subsets evaluated: `66`

## Aggregate

| solver | beam_width | n_rows | boundary_match_rate | zero_total_violation_gap_rate | feasible_decision_match_rate | mean_extra_jaccard | median_selection_time_sec | median_oracle_time_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actual_refine | 1 | 3 | 1 | 1 | 1 | 0.6667 | 3.668 | 10.95 |
| actual_refine | 2 | 3 | 1 | 1 | 1 | 0.6667 | 4.063 | 10.95 |
| actual_refine | 4 | 3 | 1 | 1 | 1 | 0.6667 | 4.054 | 10.95 |
| operator | 1 | 3 | 0.0 | 0.0 | 0.3333 | 0.0 | 0.9427 | 10.95 |
| operator | 2 | 3 | 0.6667 | 0.6667 | 0.6667 | 0.3333 | 1.651 | 10.95 |
| operator | 4 | 3 | 1 | 1 | 1 | 0.6667 | 1.6 | 10.95 |

## Rows

| map | solver | beam_width | n_states | n_basis | n_oracle_pool | oracle_evaluated_subsets | same_boundary_as_oracle | extra_jaccard_with_oracle | operator_top_rank_in_oracle_extra | first_selected_in_oracle_extra | oracle_total_violation | chosen_total_violation | total_violation_gap | oracle_all_feasible | chosen_all_feasible | oracle_test_bits_cvar | chosen_test_bits_cvar | selection_time_sec | oracle_time_sec | chosen_stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_5 | operator | 1 | 25 | 10 | 6 | 22 | False | 0.0 | 4 | False | 0.0 | 183.1 | 183.1 | True | False | 7.651e-06 | 54.12 | 0.9427 | 8.442 | budget_not_met |
| open_room_5 | operator | 2 | 25 | 10 | 6 | 22 | False | 0.0 | 4 | False | 0.0 | 174.9 | 174.9 | True | False | 7.651e-06 | 77.73 | 1.651 | 8.442 | budget_not_met |
| open_room_5 | operator | 4 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 1.6 | 8.442 | feasible |
| open_room_5 | actual_refine | 1 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 2.743 | 8.442 | actual_refine_feasible |
| open_room_5 | actual_refine | 2 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 2.918 | 8.442 | actual_refine_feasible |
| open_room_5 | actual_refine | 4 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 2.706 | 8.442 | actual_refine_feasible |
| four_rooms_7 | operator | 1 | 40 | 26 | 6 | 22 | False | 0.0 |  | False | 174.9 | 576.7 | 401.8 | False | False | 77.73 | 245 | 1.919 | 15.57 | budget_not_met |
| four_rooms_7 | operator | 2 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 2.924 | 15.57 | budget_not_met |
| four_rooms_7 | operator | 4 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 5.38 | 15.57 | budget_not_met |
| four_rooms_7 | actual_refine | 1 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 10.74 | 15.57 | actual_refine_budget_not_met |
| four_rooms_7 | actual_refine | 2 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 14.73 | 15.57 | actual_refine_budget_not_met |
| four_rooms_7 | actual_refine | 4 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 24.16 | 15.57 | actual_refine_budget_not_met |
| maze_9 | operator | 1 | 31 | 17 | 6 | 22 | False | 0.0 | 1 | False | 0.0 | 174.9 | 174.9 | True | False | 0.0 | 77.73 | 0.3907 | 10.95 | no_positive_violation_reduction |
| maze_9 | operator | 2 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 0.8098 | 10.95 | feasible |
| maze_9 | operator | 4 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 0.8099 | 10.95 | feasible |
| maze_9 | actual_refine | 1 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 3.668 | 10.95 | actual_refine_feasible |
| maze_9 | actual_refine | 2 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 4.063 | 10.95 | actual_refine_feasible |
| maze_9 | actual_refine | 4 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 4.054 | 10.95 | actual_refine_feasible |
