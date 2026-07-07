# Adaptive Top-K Diagnostics

Generated: 2026-07-07T15:31:51

This report checks the feasible-envelope claim for adaptive top-k refinement against the fixed top-4 ablation. It treats adaptive top-k as a feasible-discovery backend, not as a proof of score-optimal split selection.

- paired feasible matches: `36/36`
- certified median fixed/adaptive selection speedup: `1.913x`

## Paired Feasibility

| mode | map | slip | fixed_top4_feasible | adaptive_topk_feasible | feasible_match | adaptive_k_used_mean | selection_speedup_fixed_over_adaptive | lexicographic_regret_vs_fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| certified | four_rooms_11 | 0.0 | True | True | True | 1 | 1.981 | 0.0 |
| certified | four_rooms_11 | 0.05 | True | True | True | 3 | 1.292 | 0.0 |
| certified | four_rooms_11 | 0.1 | False | False | True | 4 | 1.023 | 0.0 |
| certified | four_rooms_15 | 0.0 | True | True | True | 1 | 2.052 | 0.0 |
| certified | four_rooms_15 | 0.05 | False | False | True | 4 | 1.04 | 0.0 |
| certified | four_rooms_15 | 0.1 | True | True | True | 4 | 1.03 | 0.0 |
| certified | maze_13 | 0.0 | True | True | True | 1 | 1.917 | 0.0 |
| certified | maze_13 | 0.05 | True | True | True | 1 | 1.974 | 0.0 |
| certified | maze_13 | 0.1 | True | True | True | 1 | 1.924 | 0.0 |
| certified | maze_17 | 0.0 | True | True | True | 1 | 2.047 | 0.0 |
| certified | maze_17 | 0.05 | True | True | True | 1 | 2.002 | 0.0 |
| certified | maze_17 | 0.1 | True | True | True | 1 | 1.91 | 0.0 |
| certified | open_room_12 | 0.0 | True | True | True | 1 | 2.175 | 0.0 |
| certified | open_room_12 | 0.05 | True | True | True | 4 | 1.062 | 0.0 |
| certified | open_room_12 | 0.1 | False | False | True | 4 | 1.003 | 0.0 |
| certified | open_room_16 | 0.0 | True | True | True | 1 | 2.084 | 0.0 |
| certified | open_room_16 | 0.05 | False | False | True | 4 | 1.044 | 0.0 |
| certified | open_room_16 | 0.1 | False | False | True | 4 | 1.015 | 0.0 |
| exact | four_rooms_11 | 0.0 | True | True | True | 1 | 2.066 | 0.0 |
| exact | four_rooms_11 | 0.05 | True | True | True | 3 | 1.376 | 0.0 |
| exact | four_rooms_11 | 0.1 | False | False | True | 4 | 1.03 | 0.0 |
| exact | four_rooms_15 | 0.0 | True | True | True | 1 | 1.985 | 0.0 |
| exact | four_rooms_15 | 0.05 | False | False | True | 4 | 1.082 | 0.0 |
| exact | four_rooms_15 | 0.1 | True | True | True | 4 | 1.068 | 0.0 |
| exact | maze_13 | 0.0 | True | True | True | 1 | 1.901 | 0.0 |
| exact | maze_13 | 0.05 | True | True | True | 1 | 2.052 | 0.0 |
| exact | maze_13 | 0.1 | True | True | True | 1 | 2.013 | 0.0 |
| exact | maze_17 | 0.0 | True | True | True | 1 | 1.927 | 0.0 |
| exact | maze_17 | 0.05 | True | True | True | 1 | 2.111 | 0.0 |
| exact | maze_17 | 0.1 | True | True | True | 1 | 2.064 | 0.0 |
| exact | open_room_12 | 0.0 | True | True | True | 1 | 2.05 | 0.0 |
| exact | open_room_12 | 0.05 | True | True | True | 4 | 1.085 | 0.0 |
| exact | open_room_12 | 0.1 | False | False | True | 4 | 1.046 | 0.0 |
| exact | open_room_16 | 0.0 | True | True | True | 1 | 1.961 | 0.0 |
| exact | open_room_16 | 0.05 | False | False | True | 4 | 1.098 | 0.0 |
| exact | open_room_16 | 0.1 | False | False | True | 4 | 1.084 | 0.0 |

## K-Used Histogram

| method | top_k_cap | k_used | n_steps | n_feasible_stop | n_cap_hit | n_cap_without_selected_feasible |
| --- | --- | --- | --- | --- | --- | --- |
| adaptive_topk_certified_refine | 4 | 1 | 11 | 11 | 0 | 0 |
| adaptive_topk_certified_refine | 4 | 4 | 21 | 0 | 19 | 19 |
| adaptive_topk_exact_refine | 4 | 1 | 11 | 11 | 0 | 0 |
| adaptive_topk_exact_refine | 4 | 4 | 21 | 0 | 19 | 19 |

## Fixed-K Vs Adaptive Cap

| source | method | top_k_or_cap | n_rows | feasible_rate | median_selection_time_sec | total_exact_refine_calls | total_refined_candidates | median_adaptive_topk_used_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_topk_ablation | surrogate_topk_certified_refine | 1 | 18 | 0.6111 | 25.63 | 82 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 2 | 18 | 0.6111 | 32.84 | 117 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 4 | 18 | 0.7222 | 47.18 | 174 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 8 | 18 | 0.7222 | 73.07 | 274 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_certified_refine | 16 | 18 | 0.6667 | 132.2 | 454 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 1 | 18 | 0.6111 | 25.26 | 82 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 2 | 18 | 0.6111 | 32.18 | 117 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 4 | 18 | 0.7222 | 48.69 | 174 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 8 | 18 | 0.7222 | 73.76 | 274 | 0 | nan |
| fixed_topk_ablation | surrogate_topk_exact_refine | 16 | 18 | 0.6667 | 131.3 | 454 | 0 | nan |
| adaptive_topk | adaptive_topk_certified_refine | 4 | 18 | 0.7222 | 23.58 | 141 | 95 | 1 |
| adaptive_topk | adaptive_topk_exact_refine | 4 | 18 | 0.7222 | 24.23 | 141 | 95 | 1 |

## Score-Regret Proxy

| mode | map | slip | both_feasible | feasible_match | boundary_match | lexicographic_regret_vs_fixed | group_total_violation_delta | start_gap_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| certified | four_rooms_11 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | four_rooms_11 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | four_rooms_11 | 0.1 | False | True | True | 0.0 | 0.0 | 0.0 |
| certified | four_rooms_15 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | four_rooms_15 | 0.05 | False | True | True | 0.0 | 0.0 | 0.0 |
| certified | four_rooms_15 | 0.1 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | maze_13 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | maze_13 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | maze_13 | 0.1 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | maze_17 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | maze_17 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | maze_17 | 0.1 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | open_room_12 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | open_room_12 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | open_room_12 | 0.1 | False | True | True | 0.0 | 0.0 | 0.0 |
| certified | open_room_16 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| certified | open_room_16 | 0.05 | False | True | True | 0.0 | 0.0 | 0.0 |
| certified | open_room_16 | 0.1 | False | True | True | 0.0 | 0.0 | 0.0 |
| exact | four_rooms_11 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | four_rooms_11 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | four_rooms_11 | 0.1 | False | True | True | 0.0 | 0.0 | 0.0 |
| exact | four_rooms_15 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | four_rooms_15 | 0.05 | False | True | True | 0.0 | 0.0 | 0.0 |
| exact | four_rooms_15 | 0.1 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | maze_13 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | maze_13 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | maze_13 | 0.1 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | maze_17 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | maze_17 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | maze_17 | 0.1 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | open_room_12 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | open_room_12 | 0.05 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | open_room_12 | 0.1 | False | True | True | 0.0 | 0.0 | 0.0 |
| exact | open_room_16 | 0.0 | True | True | True | 0.0 | 0.0 | 0.0 |
| exact | open_room_16 | 0.05 | False | True | True | 0.0 | 0.0 | 0.0 |
| exact | open_room_16 | 0.1 | False | True | True | 0.0 | 0.0 | 0.0 |

## Failure Summary

| mode | failure_class | n_rows | max_adaptive_group_total_violation | maps | slips |
| --- | --- | --- | --- | --- | --- |
| certified | cap_envelope_or_boundary_budget_not_met | 1 | 128.2 | four_rooms_11 | 0.1 |
| certified | cap_exhausted_no_positive_feasible_gain | 4 | 116.6 | four_rooms_15;open_room_12;open_room_16 | 0.05;0.1 |
| exact | cap_envelope_or_boundary_budget_not_met | 1 | 128.2 | four_rooms_11 | 0.1 |
| exact | cap_exhausted_no_positive_feasible_gain | 4 | 116.6 | four_rooms_15;open_room_12;open_room_16 | 0.05;0.1 |
