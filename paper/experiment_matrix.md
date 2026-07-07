# Experiment Matrix

This file maps reviewer questions to concrete scripts and output folders.

| Reviewer question | Required evidence | Current artifact | Status |
|---|---|---|---|
| Does the boundary graph preserve planning behavior at useful compression? | full VI/PI vs graph-SMDP value gaps, backup counts, memory, rollout success | `experiments/run_core_benchmark.py`, `experiments/output/core_benchmark/` | implemented |
| Is the contribution compression rather than only control performance? | compression scaling and amortized multi-task cost | `experiments/run_large_scale_compression.py`, `experiments/run_amortized_multitask.py`, `experiments/aggregate_scheduler_shards.py` | XL aggregate published (`paper_xl_20260706_0659`) |
| Is the solver close to an oracle? | exhaustive small-map optimum and beam-width ablation | `experiments/run_solver_validity.py`, `experiments/output/solver_validity/` | implemented |
| Does the operator generalize beyond one residual lens? | held-out residual probes and alternate goals | `experiments/run_rd_operator_generalization.py`, `experiments/output/rd_operator_generalization/` | implemented |
| Does it generalize beyond fixed hand-made maps? | random DFS maze family | `experiments/run_random_maze_generalization.py`, `experiments/output/random_maze_generalization/` | XL aggregate published: 360 random-maze rows |
| Does the code path generalize beyond the custom GridWorld class? | generic finite-MDP adapter, Gymnasium ToyText, discretized PointMaze, optional MiniGrid symbolic BFS, Taxi task-variable repair ablation | `experiments/finite_mdp_adapter.py`, `experiments/run_general_env_benchmark.py`, `experiments/output/general_env_benchmark/` | smoke implemented: 112 rows |
| Is comparison to options fair? | same rate/boundary budget frontier, value gap, hidden audit, success | `experiments/run_option_algorithm_comparison.py`, `experiments/run_option_baseline_frontier.py`, `experiments/run_fair_budget_frontier.py` | XL option frontier published: 648 rows |
| Do multi-task rewards preserve graph compression? | fixed-`B` edge reward relabeling, terminal event kernels, shared/batched goal-conditioned option extension | `experiments/run_edge_reward_kernel_multitask.py`, `experiments/output/edge_reward_kernel_multitask/` | implemented |
| Does the runtime implementation match the theorem? | adaptive Green certificate, top-set fallback, weighted/conditioned certificates | `experiments/run_adaptive_green_certification.py`, `experiments/run_weighted_spectral_certificate.py`, `experiments/run_conditioned_weighted_certificate.py` | implemented |
| Can adaptive top-k be the main discovery backend without overclaiming? | paired fixed-top-4/adaptive feasibility equivalence, k-used histogram, fixed-K sweep, score-regret proxy, failure-mode breakdown | `experiments/run_adaptive_topk_diagnostics.py`, `experiments/output/adaptive_topk_diagnostics/` | implemented |
| Where does runtime go? | profile discovery, kernel, scoring, beam, active weights | `experiments/run_discovery_profile_cache.py`, `experiments/output/discovery_profile_cache/` | implemented |
| Are figures interpretable? | overlay selected boundary vertices on maps | `experiments/plot_graph_abstraction_figures.py`, `experiments/output/graph_abstraction_figures/` | new |
| Are theorem claims aligned with experiments? | theorem/proof/experiment bridge table | `experiments/run_theorem_experiment_bridge.py`, `experiments/output/theorem_experiment_bridge/` | new |

## Final Paper Experiment Status

1. XL scheduler suite `paper_xl_20260706_0659` finished on node001-node006 and is published into tracked output folders.
2. Aggregated coverage: large-scale compression 135 rows, random maze 360 rows, option frontier 648 rows, amortized multitask 192 rows, edge reward 384 rows.
3. The corridor-1024 horizon artifact was fixed by using an effectively unbounded local horizon; the published large-scale table now has zero error rows.
4. Adaptive top-k diagnostics now support the paper hierarchy: exact/frozen RD Green is the reference objective, adaptive feasible top-k is the main feasible-discovery backend, fixed top-k is the ablation envelope, and score optimality requires interval dominance.
5. General finite-MDP smoke tests now separate interface portability from the main finite-grid compression claim. Taxi is an informative failure/repair mode: spatial boundary compression alone gives large gaps; task-variable landmark boundaries plus boundary-targeted options reduce the start gap from about `37.04` to `10.73`, but at lower compression and higher option-interface cost.
6. Next: ask GPT/reviewer to attack the updated `submission_main_table` and decide whether the negative amortized-all-state result should be shown only as a failure-mode/limitation beside the fixed-`B` edge reward result.
