# Proof Notes

`RDOperator.lean` is the Std-only finite/scaled proof core for the RD Boundary
Green operator. `RDOperatorReal.lean` is the Mathlib-backed real-valued proof
layer.

Run:

```bash
lean proof/RDOperator.lean
lean proof/AdaptiveTopK.lean
cd proof && lake env lean RDOperatorReal.lean
```

What is formalized now:

- frozen finite-difference identity;
- adaptive recomputation drift decomposition;
- margin stability, matching the diagnostic `m > 2 * epsilon_adapt`;
- exact finite-difference identity for a frozen multi-probe robust RD objective
  with an arbitrary finite-vector risk aggregator;
- first-hit certificate existence for the Green-kernel layer;
- finite absorbing-chain Green-kernel obligations: the first-hit kernel equals
  the matrix expression `e_b^T (I - P_II)^-1 P_IC`, entries are nonnegative,
  row mass is bounded, and every entry is bounded by that row mass;
- truncated Green convergence/error obligations:
  `sum_{t=0}^K P_II^t P_IC` plus a nonnegative tail equals the Green kernel,
  so any tail bound gives the epsilon approximation bound, including an
  epsilon-style convergence theorem when the tail-bound certificate vanishes;
- scaled bits-distortion finite-difference/Taylor obligations for
  `phi(h) = -log_2(1 - h + eps)`;
- discounted Bellman residual to value-gap bound in scaled rational form,
  matching `||V - Vhat||_∞ <= ||T V - That V||_∞ / (1 - gamma)`;
- a real-valued primitive-to-graph end-to-end certificate that keeps option
  restriction, boundary/interface abstraction, graph-kernel approximation, and
  planning residual as four explicit additive terms, with uniform finite-state
  hypotheses yielding the paper's sup-norm form;
- group-constraint feasibility from zero group violations;
- finite-option graph-SMDP Bellman sup-norm contraction and non-expansion,
  including stability of repeated Bellman iterates;
- Mathlib real finite-matrix layer:
  `(I - P_II)^-1 P_IC` solves the absorbing-chain linear system,
  nonnegative finite sums imply Green nonnegativity and row bounds,
  Neumann prefixes converge under a real tail-bound certificate,
  `phi(h) = -log_2(1 - h + eps)` has the expected real derivative, finite
  option max Bellman backups contract, and real residuals imply value-gap
  bounds.
- row-substochastic Neumann tail layer:
  if `P_II >= 0`, row mass is at most `q < 1`, and boundary-exit row mass is
  bounded, then each term `P_II^n P_IC` is geometrically bounded and every
  finite tail window is bounded by `exitBound * q^(K+1)/(1-q)`;
- weighted spectral-radius certificate layer:
  if there is a nonnegative weight vector `w` with `P_II w <= q w` and
  `q < 1`, then `P_II^n P_IC` and finite Neumann tails get the sharper weighted
  geometric bounds.  This is the Collatz-Wielandt style certificate behind the
  spectral-radius claim;
- signed weighted spectral tail layer:
  the same `P_II w <= q w` certificate also bounds arbitrary signed downstream
  feature/reward blocks in weighted sup-norm, so this is not limited to
  nonnegative hit probabilities;
- weighted downstream score layer:
  for any fixed nonnegative edge/objective weights, entrywise Green-tail bounds
  imply a weighted score interval, and separated approximate score intervals
  formally certify that the approximate top choice is also the exact top choice;
- top-set exact fallback layer:
  if interval bounds cannot separate top-1, exact evaluation on an ambiguous
  top set certifies a global optimum whenever the exact best in that set beats
  all outside interval upper bounds;
- tie-aware / epsilon-optimal certificate layer:
  interval bounds can certify that a selected split is within `eps` of the
  exact optimum, and any representative of an exact top tie set is globally
  optimal when all outside states are no better;
- conditioned/rational weighted certificate audit:
  `experiments/run_conditioned_weighted_certificate.py` searches for Collatz
  certificates under explicit condition-number caps and verifies rounded
  `(P,w,q)` inequalities with exact Python `Fraction` arithmetic.  The Lean
  layer remains the conditional real theorem applied after such inequalities
  are audited.
- adaptive feasible top-k wrapper:
  `AdaptiveTopK.lean` proves that, for a fixed candidate order, feasibility
  oracle, and cap `K`, adaptive feasible stopping has the same feasible envelope
  as fixed top-`K`, refines at most `K` candidates, and requires an interval
  dominance certificate before it can claim score-optimal rather than merely
  feasible stopping.
- bits-curvature layer:
  the derivative of `bitsPhiDeriv` is `bitsPhiSecond`, a positive margin
  `delta <= 1 - h + eps` bounds `|bitsPhiSecond|`, and Mathlib Taylor gives the
  first-order remainder bound from that curvature bound;
- automatic `iteratedDerivWithin` glue for `bitsPhiSecond`, so the final
  bits-Taylor theorem no longer needs a user-supplied curvature-identity
  hypothesis on nondegenerate closed intervals.

What still needs a stronger Mathlib-backed development before paper submission:

- optional eigenvalue/spectrum API version showing that a Mathlib
  `spectrum`/spectral-radius assumption implies the weighted certificate above;
- an infinite-tail theorem phrased with `HasSum`/`tsum`, beyond the current
  finite-tail geometric bound used by experiments.
