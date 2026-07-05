# Incremental Group Beam Semantic Diff

Generated: 2026-07-05T19:11:33
map = `open_room_12`, slip = `0.0`
initial_boundary = `[0, 143]`, n_basis = `24`
budgets = `{"stochastic": 0.0, "topology": 19.43157654809228, "value": 19.43157654809228}`
elapsed_sec = `9.655`

This diagnostic separates the open-room discrepancy into score estimate, edge-weight semantics, and exact post-split group feasibility.

## Backend Step-0 Summary

| backend | step_time_sec | top_candidate | top_estimated_violation_after | top_estimated_violation_reduction | current_total_violation |
| --- | --- | --- | --- | --- | --- |
| operator | 1.592 | 1 | 116.6 | 0.0 | 116.6 |
| insertion_score | 0.9003 | 72 | 77.73 | 38.86 | 116.6 |

## Top Candidate Exact Checks

| backend | rank | candidate_state | estimated_violation_after | exact_total_violation_after | estimate_minus_exact_violation | estimated_violation_reduction | exact_all_groups_feasible |
| --- | --- | --- | --- | --- | --- | --- | --- |
| operator | 1 | 1 | 116.6 | 0.0 | 116.6 | 0.0 | True |
| insertion_score | 1 | 72 | 77.73 | 0.0 | 77.73 | 38.86 | True |

## Edge Weight Semantics

| boundary | probe | n_valid_edges | n_active_edges_weighted | valid_policy_occupancy_total | weighted_hidden_bits | uniform_hidden_bits | uniform_minus_weighted_bits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [0, 143] | bottleneck | 0 | 2 | 0 | 77.73 | 77.73 | 0.0 |
| [0, 143] | junction | 0 | 2 | 0 | 77.73 | 77.73 | 0.0 |
| [0, 143] | value_gradient | 0 | 2 | 0 | 77.73 | 77.73 | 0.0 |
| [0, 1, 143] | bottleneck | 2 | 1 | 0.25 | -3.6070582432937927e-13 | -2.885646594635035e-12 | -2.524940770305656e-12 |
| [0, 1, 143] | junction | 2 | 1 | 0.25 | -3.6070582432937927e-13 | -2.885646594635035e-12 | -2.524940770305656e-12 |
| [0, 1, 143] | value_gradient | 2 | 1 | 0.25 | -3.6070582432937927e-13 | -2.885646594635035e-12 | -2.524940770305656e-12 |
| [0, 72, 143] | bottleneck | 3 | 1 | 0.25 | 9.716 | 116.6 | 106.9 |
| [0, 72, 143] | junction | 3 | 1 | 0.25 | 9.716 | 116.6 | 106.9 |
| [0, 72, 143] | value_gradient | 3 | 1 | 0.25 | -3.6070582432937927e-13 | -4.328469891952552e-12 | -3.967764067623173e-12 |

## Interpretation

- The original discrepancy comes from edge weighting, not from terminal-universe or active-edge validity: edge-uniform bits remain large while occupancy-weighted bits are already below budget.
- The insertion-score backend now honors the same occupancy-or-uniform active-edge semantics as the production operator when it evaluates a beam node.
- The step-0 score is still a conservative frozen-edge estimate; the exact post-split check shows that both top choices are feasible after the graph is rewired.
