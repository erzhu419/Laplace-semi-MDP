# Figure Plan

## Main Figures

1. Pipeline figure: primitive MDP -> candidate boundary universe -> RD Boundary Green score -> selected boundary graph -> graph-SMDP planning.
2. Operator figure: one boundary edge, its first-hit Green mass over candidate states, and the finite-difference score for inserting one candidate.
3. Compression scaling: state count and backup count versus boundary count across corridor/open-room/four-room/maze families.
4. Fair budget frontier: rate budget on the x-axis, start-value gap or hidden audit on the y-axis, colored by method family.
5. Boundary overlay panels: selected vertices on open-room, four-room, and maze maps for endpoints, group-constrained operator, and incremental selector.
6. Certificate panel: adaptive Green tail bound, top-set fallback frequency, and exact fallback/tie-aware timing.
7. Adaptive top-k backend panel: fixed top-`K` versus adaptive cap-`K` feasible rate, median selection time, refined-candidate count, and k-used histogram.
8. General finite-MDP smoke panel or appendix table: ToyText and discretized PointMaze value-gap/compression rows, with Taxi highlighted as a task-variable abstraction failure.
9. Failure modes: corridor tie fallback, adaptive top-k cap-hit/no-feasible cases, Taxi passenger/destination compression failure, and random-maze cases where held-out probes disagree with the training residual lens.

## Generated Figure Artifacts

The current plot script writes:

```text
experiments/output/graph_abstraction_figures/boundary_selection_panel.png
experiments/output/graph_abstraction_figures/*_boundaries.png
```

Existing reward-propagation figures:

```text
experiments/output/reward_propagation_tradeoff_plots/
```

Adaptive top-k diagnostic artifacts:

```text
experiments/output/adaptive_topk_diagnostics/
experiments/output/submission_main_table/adaptive_topk_summary.csv
```

General finite-MDP smoke artifacts:

```text
experiments/output/general_env_benchmark/general_env_benchmark.csv
experiments/output/general_env_benchmark/summary.md
```

## Caption Discipline

Every figure caption should state:

1. map family and slip setting,
2. boundary/option budget,
3. whether the result uses exact Green, adaptive Green, or fallback,
4. the metric direction,
5. whether adaptive top-k is being evaluated as feasible discovery or score-certified selection,
6. one explicit limitation if the panel is diagnostic rather than a main win.
