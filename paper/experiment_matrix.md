# Experiment Matrix

This file maps reviewer questions to concrete scripts and output folders.

| Reviewer question | Required evidence | Current artifact | Status |
|---|---|---|---|
| Does the boundary graph preserve planning behavior at useful compression? | full VI/PI vs graph-SMDP value gaps, backup counts, memory, rollout success | `experiments/run_core_benchmark.py`, `experiments/output/core_benchmark/` | implemented |
| Is the contribution compression rather than only control performance? | compression scaling and amortized multi-task cost | `experiments/run_large_scale_compression.py`, `experiments/run_amortized_multitask.py`, `experiments/output/large_scale_compression_adaptive/` | implemented, needs larger node runs |
| Is the solver close to an oracle? | exhaustive small-map optimum and beam-width ablation | `experiments/run_solver_validity.py`, `experiments/output/solver_validity/` | implemented |
| Does the operator generalize beyond one residual lens? | held-out residual probes and alternate goals | `experiments/run_rd_operator_generalization.py`, `experiments/output/rd_operator_generalization/` | implemented |
| Does it generalize beyond fixed hand-made maps? | random DFS maze family | `experiments/run_random_maze_generalization.py`, `experiments/output/random_maze_generalization/` | new |
| Is comparison to options fair? | same rate/boundary budget frontier, value gap, hidden audit, success | `experiments/run_option_algorithm_comparison.py`, `experiments/run_option_baseline_frontier.py`, `experiments/run_fair_budget_frontier.py` | new aggregation |
| Do multi-task rewards preserve graph compression? | fixed-`B` edge reward relabeling, terminal event kernels, shared/batched goal-conditioned option extension | `experiments/run_edge_reward_kernel_multitask.py`, `experiments/output/edge_reward_kernel_multitask/` | implemented |
| Does the runtime implementation match the theorem? | adaptive Green certificate, top-set fallback, weighted/conditioned certificates | `experiments/run_adaptive_green_certification.py`, `experiments/run_weighted_spectral_certificate.py`, `experiments/run_conditioned_weighted_certificate.py` | implemented |
| Where does runtime go? | profile discovery, kernel, scoring, beam, active weights | `experiments/run_discovery_profile_cache.py`, `experiments/output/discovery_profile_cache/` | implemented |
| Are figures interpretable? | overlay selected boundary vertices on maps | `experiments/plot_graph_abstraction_figures.py`, `experiments/output/graph_abstraction_figures/` | new |
| Are theorem claims aligned with experiments? | theorem/proof/experiment bridge table | `experiments/run_theorem_experiment_bridge.py`, `experiments/output/theorem_experiment_bridge/` | new |

## Final Paper Experiments Still Needed On CPU Nodes

1. Larger random maze and four-room scale frontier with `LAPLACE_NUM_THREADS` tuned on node001-node006.
2. Multi-task amortization with 10/50/100 goals on large maps.
3. Fair-budget frontier at matched boundary counts for all option baselines.
4. Failure-mode table: open-room over-splitting, corridor tie fallback, stochastic slip drift.
