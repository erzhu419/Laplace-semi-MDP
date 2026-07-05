# Proof Notes

`RDOperator.lean` is the first formal proof core for the RD Boundary Green
operator.

Run:

```bash
lean proof/RDOperator.lean
```

What is formalized now:

- frozen finite-difference identity;
- adaptive recomputation drift decomposition;
- margin stability, matching the diagnostic `m > 2 * epsilon_adapt`;
- exact finite-difference identity for a frozen multi-probe robust RD objective
  with an arbitrary finite-vector risk aggregator;
- an abstract Bellman contraction/non-expansion obligation for the graph-SMDP
  planning layer.

What still needs a stronger Mathlib-backed development before paper submission:

- real-valued first-hit Green kernel existence and row-sum bounds;
- Taylor/gradient error bound for the bits distortion;
- truncated Green convergence rate;
- sup-norm Bellman contraction over real value functions with max over finite
  actions.
