# Experiment Matrix

This file maps reviewer questions to concrete scripts and output folders.

| Reviewer question | Required evidence | Current artifact | Status |
|---|---|---|---|
| Does the boundary graph preserve planning behavior at useful compression? | full VI/PI vs graph-SMDP value gaps, backup counts, memory, rollout success | `experiments/run_core_benchmark.py`, `experiments/output/core_benchmark/` | implemented |
| Is the contribution compression rather than only control performance? | compression scaling and amortized multi-task cost | `experiments/run_large_scale_compression.py`, `experiments/run_amortized_multitask.py`, `experiments/aggregate_scheduler_shards.py` | implemented; XL shard runner now supports multi-slip large maps |
| Is the solver close to an oracle? | exhaustive small-map optimum and beam-width ablation | `experiments/run_solver_validity.py`, `experiments/output/solver_validity/` | implemented |
| Does the operator generalize beyond one residual lens? | held-out residual probes and alternate goals | `experiments/run_rd_operator_generalization.py`, `experiments/output/rd_operator_generalization/` | implemented |
| Does it generalize beyond fixed hand-made maps? | random DFS maze family | `experiments/run_random_maze_generalization.py`, `experiments/output/random_maze_generalization/` | XL sharded multi-size/multi-seed/multi-slip run supported |
| Is comparison to options fair? | same rate/boundary budget frontier, value gap, hidden audit, success | `experiments/run_option_algorithm_comparison.py`, `experiments/run_option_baseline_frontier.py`, `experiments/run_fair_budget_frontier.py` | scaled option frontier + large/random inputs supported |
| Do multi-task rewards preserve graph compression? | fixed-`B` edge reward relabeling, terminal event kernels, shared/batched goal-conditioned option extension | `experiments/run_edge_reward_kernel_multitask.py`, `experiments/output/edge_reward_kernel_multitask/` | implemented |
| Does the runtime implementation match the theorem? | adaptive Green certificate, top-set fallback, weighted/conditioned certificates | `experiments/run_adaptive_green_certification.py`, `experiments/run_weighted_spectral_certificate.py`, `experiments/run_conditioned_weighted_certificate.py` | implemented |
| Where does runtime go? | profile discovery, kernel, scoring, beam, active weights | `experiments/run_discovery_profile_cache.py`, `experiments/output/discovery_profile_cache/` | implemented |
| Are figures interpretable? | overlay selected boundary vertices on maps | `experiments/plot_graph_abstraction_figures.py`, `experiments/output/graph_abstraction_figures/` | new |
| Are theorem claims aligned with experiments? | theorem/proof/experiment bridge table | `experiments/run_theorem_experiment_bridge.py`, `experiments/output/theorem_experiment_bridge/` | new |

## Final Paper Experiments Still Needed On CPU Nodes

1. Run the XL scheduler suite on node001-node006 and publish the aggregate.
2. Check the failure-mode table for open-room group feasibility, corridor tie fallback, and terminal interior goals.
3. Ask GPT/reviewer to attack the updated `submission_main_table` after the XL results are merged.
