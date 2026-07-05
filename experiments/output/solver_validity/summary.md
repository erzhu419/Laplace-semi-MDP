# Solver Validity

Generated: 2026-07-05T14:29:37
map_specs = ['open_room:5', 'four_rooms:7', 'maze:9']
solvers = ['operator', 'actual_refine']
beam_widths = [1, 2, 4], beam_expand = 6
max_extra_splits = 2, max_oracle_candidates = 6

For small candidate universes this exhaustively enumerates every subset up to the split budget, then compares operator-only and exact-refined beam group-constrained RD against that oracle. The exact-refined solver uses the frozen operator only to propose a small expansion set, then ranks those expansions by actual group RD evaluation.

- exact boundary matches: `14/18`
- zero total-violation gap rows: `14/18`
- feasible/infeasible decision matches: `15/18`
- oracle subsets evaluated: `66`

| map | solver | beam_width | n_states | n_basis | n_oracle_pool | oracle_evaluated_subsets | same_boundary_as_oracle | extra_jaccard_with_oracle | operator_top_rank_in_oracle_extra | first_selected_in_oracle_extra | oracle_total_violation | chosen_total_violation | total_violation_gap | oracle_all_feasible | chosen_all_feasible | oracle_test_bits_cvar | chosen_test_bits_cvar | selection_time_sec | oracle_time_sec | chosen_stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_5 | operator | 1 | 25 | 10 | 6 | 22 | False | 0.0 | 4 | False | 0.0 | 183.1 | 183.1 | True | False | 7.651e-06 | 54.12 | 0.966 | 9.084 | budget_not_met |
| open_room_5 | operator | 2 | 25 | 10 | 6 | 22 | False | 0.0 | 4 | False | 0.0 | 174.9 | 174.9 | True | False | 7.651e-06 | 77.73 | 1.642 | 9.084 | budget_not_met |
| open_room_5 | operator | 4 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 1.543 | 9.084 | feasible |
| open_room_5 | actual_refine | 1 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 2.8 | 9.084 | actual_refine_feasible |
| open_room_5 | actual_refine | 2 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 2.786 | 9.084 | actual_refine_feasible |
| open_room_5 | actual_refine | 4 | 25 | 10 | 6 | 22 | True | 1 | 4 | True | 0.0 | 0.0 | 0.0 | True | True | 7.651e-06 | 7.651e-06 | 2.969 | 9.084 | actual_refine_feasible |
| four_rooms_7 | operator | 1 | 40 | 26 | 6 | 22 | False | 0.0 |  | False | 174.9 | 576.7 | 401.8 | False | False | 77.73 | 245 | 1.812 | 16.18 | budget_not_met |
| four_rooms_7 | operator | 2 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 3.145 | 16.18 | budget_not_met |
| four_rooms_7 | operator | 4 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 5.426 | 16.18 | budget_not_met |
| four_rooms_7 | actual_refine | 1 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 10.21 | 16.18 | actual_refine_budget_not_met |
| four_rooms_7 | actual_refine | 2 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 15.48 | 16.18 | actual_refine_budget_not_met |
| four_rooms_7 | actual_refine | 4 | 40 | 26 | 6 | 22 | True | 0.0 |  | False | 174.9 | 174.9 | 0.0 | False | False | 77.73 | 77.73 | 25 | 16.18 | actual_refine_budget_not_met |
| maze_9 | operator | 1 | 31 | 17 | 6 | 22 | False | 0.0 | 1 | False | 0.0 | 174.9 | 174.9 | True | False | 0.0 | 77.73 | 0.3968 | 12.2 | no_positive_violation_reduction |
| maze_9 | operator | 2 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 0.9543 | 12.2 | feasible |
| maze_9 | operator | 4 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 0.8665 | 12.2 | feasible |
| maze_9 | actual_refine | 1 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 3.835 | 12.2 | actual_refine_feasible |
| maze_9 | actual_refine | 2 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 3.903 | 12.2 | actual_refine_feasible |
| maze_9 | actual_refine | 4 | 31 | 17 | 6 | 22 | True | 1 | 1 | True | 0.0 | 0.0 | 0.0 | True | True | 0.0 | 0.0 | 3.782 | 12.2 | actual_refine_feasible |
