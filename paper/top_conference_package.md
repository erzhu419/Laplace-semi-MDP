# Top-Conference Package

This document is the current answer to "what is still missing besides runtime?"

## 1. Tight Main Claim

Use the compression/abstraction claim, not a raw performance claim. The method learns a proof-backed boundary graph so that uniform noncritical regions become option edges and Bellman-critical states remain vertices.

Artifact: `paper/claim_and_contributions.md`.

## 2. Related Work

Organize by mechanism: options/SMDP, spectral graph/eigenoptions, Kron reduction, state abstraction/bisimulation, rate-distortion/MDL, world-graph planning, and Bellman-residual caution.

Artifact: `paper/related_work_matrix.md`.

## 3. Paper-Readable Theorem Stack

State the proof layer as a sequence: frozen finite difference, first-hit Green legality, Neumann/adaptive tail certification, bits curvature, graph-SMDP contraction, top-set fallback, adaptive feasible top-k envelope, group-constraint feasibility, and reward/event-kernel relabeling.

Artifact: `paper/theorem_stack.md`.

## 4. Non-Runtime Experiments

Add random-maze topology stress tests, theorem margin checks, held-out residual probes, solver oracle validity, ablations, and failure modes.

Artifacts:

- `experiments/run_random_maze_generalization.py`
- `experiments/run_rd_operator_generalization.py`
- `experiments/run_solver_validity.py`

## 5. Fair Baselines And Budget Frontier

Compare methods at a shared rate/distortion vocabulary: boundary fraction, value gap, hidden audit, success, and feasibility. Do not rely only on fastest or best-looking rows.

Artifact: `experiments/run_fair_budget_frontier.py`.

## 6. Adaptive Backend Claim Discipline

Use adaptive feasible top-k as the main discovery backend, fixed top-k as the ablation envelope, and interval dominance as the only route to a score-optimal split claim. The paper should say the backend preserves the fixed-prefix feasible envelope while reducing refinements; it should not say it globally optimizes the adaptive RD objective.

Artifacts:

- `proof/AdaptiveTopK.lean`
- `experiments/run_adaptive_topk_diagnostics.py`
- `experiments/output/adaptive_topk_diagnostics/summary.md`

## 7. Figures And Interpretability

Make the graph visible. Reviewers should see which states become vertices and where the abstraction hides structure.

Artifact: `experiments/plot_graph_abstraction_figures.py`.

## 8. Theorem-To-Experiment Bridge

Every theorem-level statement must have a Lean symbol and an experiment output. Every implementation heuristic must be labeled as such.

Artifact: `experiments/run_theorem_experiment_bridge.py`.

## Current Verdict

The project now has the shape of a paper contribution. Large-scale node runs, adaptive top-k diagnostics, proof bridges, and fixed-`B` reward relabeling are in place; the remaining risk is manuscript discipline. The method story is defensible if we keep the theorem claims frozen/local, present adaptive top-k as feasible discovery rather than RD-optimal split selection, label incremental selection as an optimization/ablation, and show amortized compression wins without hiding upfront cost.
