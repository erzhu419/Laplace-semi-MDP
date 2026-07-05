# Top-Conference Package

This document is the current answer to "what is still missing besides runtime?"

## 1. Tight Main Claim

Use the compression/abstraction claim, not a raw performance claim. The method learns a proof-backed boundary graph so that uniform noncritical regions become option edges and Bellman-critical states remain vertices.

Artifact: `paper/claim_and_contributions.md`.

## 2. Related Work

Organize by mechanism: options/SMDP, spectral graph/eigenoptions, Kron reduction, state abstraction/bisimulation, rate-distortion/MDL, world-graph planning, and Bellman-residual caution.

Artifact: `paper/related_work_matrix.md`.

## 3. Paper-Readable Theorem Stack

State the proof layer as a sequence: frozen finite difference, first-hit Green legality, Neumann/adaptive tail certification, bits curvature, graph-SMDP contraction, top-set fallback, and group-constraint feasibility.

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

## 6. Figures And Interpretability

Make the graph visible. Reviewers should see which states become vertices and where the abstraction hides structure.

Artifact: `experiments/plot_graph_abstraction_figures.py`.

## 7. Theorem-To-Experiment Bridge

Every theorem-level statement must have a Lean symbol and an experiment output. Every implementation heuristic must be labeled as such.

Artifact: `experiments/run_theorem_experiment_bridge.py`.

## Current Verdict

The project now has the shape of a paper contribution, but final top-conference readiness still depends on large-scale node runs and polished manuscript writing. The method story is defensible if we keep the theorem claims frozen/local, present adaptive/incremental selection as certified implementations or ablations, and show amortized compression wins at scale.
