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
- `experiments/run_general_env_benchmark.py`

The general-environment benchmark should be framed as finite-MDP interface portability. Gymnasium ToyText and discretized PointMaze strengthen the claim that the implementation is not hardwired to one hand-authored grid class, while Taxi should be reported as a structured failure/repair mode. Boundary-targeted options and task-variable landmark states reduce the Taxi gap, but the remaining gap and larger interface show that passenger/destination identity needs an explicit factored abstraction story rather than a purely spatial boundary selector.

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

The project now has a complete submission draft, direct state-abstraction and
strong planning baselines, complete-universe solver oracles, a five-seed
external-environment audit, an end-to-end error decomposition, and paper-facing
figures. The evidence supports an abstraction/compression paper, but not a
universal runtime or control-performance claim. Sparse-vectorized VI wins every
matched single-task timing case once discovery is charged; external environments
also expose substantial option-family bias. The defensible contribution is the
auditable rate/distortion graph representation, its formal certificates, and
the explicit decomposition of where compression fails.

Remaining submission work is editorial rather than another horizontal method
extension: move the draft into the target conference template, select the main
versus appendix tables, preserve the legacy-denominator labels, and obtain one
final reviewer-style attack on the exact pushed artifact.
