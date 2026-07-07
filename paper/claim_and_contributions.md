# Claim And Contributions

## One-Sentence Argument

In finite tabular navigation tasks, we show that a boundary graph can be selected by a rate-distortion first-hit Green operator and then used for graph-SMDP planning, supported by exact Green-kernel proofs, certified adaptive approximations, adaptive feasible top-k discovery diagnostics, fair option-baseline comparisons, group-constrained robustness tests, and compression/amortization measurements, with the current boundary limited to finite known-model environments and CPU-scale experiments.

## Main Claim

The paper should not claim that the method is a universally faster option-discovery algorithm. The stronger and safer claim is:

> The RD Boundary Green Operator defines a proof-backed, reward-aware graph abstraction objective: it selects which primitive states must remain vertices so that noncritical regions can be represented as first-boundary SMDP edges under explicit rate, distortion, and audit constraints.

## Contributions

1. A Bellman-aware graph abstraction formulation that separates exact first-boundary SMDP reduction from the harder question of boundary selection.
2. The RD Boundary Green Operator: a frozen finite-difference split score built from first-hit Green kernels and a rate-distortion objective.
3. Certified runtime approximations: adaptive Green tail certificates, top-set/tie-aware exact fallback, and weighted spectral sufficient certificates.
4. An adaptive feasible top-k discovery backend that matches the fixed-prefix feasible envelope under a shared candidate order/oracle while avoiding unnecessary refinements; fixed top-k is the ablation envelope, and score-optimality is claimed only under interval dominance.
5. A group-constrained robust selector that keeps topology, value-gradient, and stochastic-transition distortions separate instead of collapsing them into one scalar risk.
6. A graph-SMDP evaluation suite comparing full VI/PI, exact/surrogate/group RD graphs, eigenoption-style spectral baselines, betweenness bottlenecks, random/coverage landmarks, and tabular option baselines.
7. A Lean 4 proof layer covering the frozen finite-difference identity, Green-kernel legality, truncated Neumann tails, bits-distortion Taylor bounds, Bellman contraction, residual-to-value-gap bounds, top-set certificates, and adaptive feasible top-k envelope guarantees.

## Non-Claims

- The frozen theorem does not prove the fully adaptive solver is globally optimal.
- Adaptive feasible top-k is a feasible-discovery backend, not an RD-optimal split oracle unless score-interval dominance is certified.
- The current implementation is not yet a sample-based deep RL algorithm.
- Single-task total wall time need not beat full VI when discovery/kernel upfront cost dominates.
- Weighted spectral certificates are sufficient certificates, not the main runtime decision rule.
- Incremental insertion scoring is currently a runtime ablation, not a central correctness theorem.

## Reviewer-Facing Thesis

The paper is strongest if framed as a compression and abstraction paper: full MDP planning broadcasts reward information through every primitive state, whereas the boundary graph stores uniform noncritical regions as option edges and reserves vertices for states that preserve Bellman-relevant structure.
