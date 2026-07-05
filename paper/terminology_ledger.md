# Terminology Ledger

This ledger fixes the paper-facing names used across notes, experiments, and proofs.

| Canonical term | First-use definition | Variants to avoid | Decision |
|---|---|---|---|
| RD Boundary Green Operator | Rate-distortion finite-difference split operator induced by first-hit Green kernels on a frozen boundary/options/edge-weight universe. | Laplacian operator, new Laplacian, graph Laplacian replacement | Use this as the method name; mention Laplacian only as motivation/baseline. |
| Boundary graph | Abstract graph whose vertices are selected boundary states and whose directed option-labeled edges are first-boundary SMDP options. | compressed graph, abstract graph, key graph | Use "boundary graph" in prose, "graph-SMDP" for the planning model. |
| First-hit Green kernel | Kernel K_e(x) giving the probability or discounted mass that option edge e first hits candidate x before the next boundary. | hitting matrix, Green-delta matrix | Use "first-hit Green kernel" for exact reference, "adaptive Green" for certified runtime implementation. |
| Frozen local objective | Local RD objective that keeps candidate universe, options, edge weights, and rate terms fixed while scoring one split. | frozen operator, local heuristic | Use "frozen local objective" in theorem statements. |
| Adaptive solver | Outer beam/greedy boundary selection that may recompute options, edges, weights, and constraints after a split. | full recompute, adaptive objective | Use "adaptive solver"; do not claim it is exactly optimized by the frozen theorem. |
| Group-constrained RD | Boundary selection that enforces separate topology/value/stochastic distortion budgets. | robust RD, multi-objective RD | Use "group-constrained RD" for the main robust selector. |
| Graph-SMDP planning | Value iteration or policy evaluation on the compressed option-labeled boundary graph. | graph RL, high-level RL | Use "graph-SMDP planning" unless rollout learning is actually used. |
