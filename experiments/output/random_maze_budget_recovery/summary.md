# Random-Maze Boundary-Budget Recovery

Generated: 2026-07-10T18:47:20
max_splits = [5, 8, 12, 16], budget_fracs = [0.25]

This ablation reruns only failed XL random-maze contexts and asks whether a modestly larger boundary budget restores group feasibility.
Summary diagnostics prefer exact-refine rows when available. `fixed_family_or_probe_plateau` means that increasing the split cap beyond five did not reduce total group violation, so the failure should not be described as a boundary-rate shortage.

- failed contexts tested: `7`
- recovered contexts: `6`

| map | slip | budget_frac | recovered | recovery_method | minimal_max_splits | minimal_n_boundary | added_vertices_over_failed | max_splits_tested | largest_n_boundary | violation_reduction | best_total_violation | failure_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_maze_15_seed0 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_15_seed0 | 0.1 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_15_seed4 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 2 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_15_seed4 | 0.1 | 0.25 | False |  |  |  |  | 16 | 17 | 2.885656158468919e-10 | 38.86 | fixed_family_or_probe_plateau |
| random_maze_15_seed8 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_19_seed3 | 0.05 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
| random_maze_19_seed3 | 0.1 | 0.25 | True | actual_refine | 5 | 4 | 1 | 5 | 4 | 0.0 | 0.0 | budget_recovered |
