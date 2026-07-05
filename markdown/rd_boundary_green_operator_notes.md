# RD Boundary Green Operator Notes

This note distills the direction from `GPT_answer_7.md` into the current code vocabulary.

## Core Claim

The split score should not be described as a standard graph Laplacian. The cleaner claim is:

\[
S_{\rm RD}(x \mid B)
=
-\Delta_x\left[R(B)+\lambda D(B)\right]
=
\lambda\left[D(B)-D(B\cup\{x\})\right]
-\left[R(B\cup\{x\})-R(B)\right].
\]

For a fixed boundary universe \(C\), fixed option policies, and frozen edge weights, the first-hit kernel for an abstract edge \(e=(b,o)\) is

\[
K_e(x)=\Pr_o[S_{\tau_C}=x\mid S_0=b],
\qquad
\tau_C=\inf\{t\ge 1:S_t\in C\setminus\{b\}\}.
\]

In matrix form:

\[
K_e=e_b^\top (I-P_{II}^{o})^{-1}P_{IC}^{o}.
\]

So the linear structural operator is

\[
S_{\rm RD}(x\mid B)=\lambda\sum_e w_e K_e(x)-c_x,
\]

or, stacked over candidate states,

\[
\mathcal S_{\rm RD}^{B,\lambda}=\lambda K_B^\top w_B-c_B.
\]

This is better named an **RD Boundary Green Operator** or **Rate-Distortion Harmonic Boundary Operator**: it is the adjoint marginal score of a controlled first-hit Green kernel.

## Bits Distortion

For the bits-style distortion used by the experiments,

\[
\phi(h)=-\log_2(1-h+\epsilon),
\qquad
h_e(B)=\sum_{y\in C\setminus B} K_e(y).
\]

The finite-difference score is

\[
S_{\rm RD}^{\rm FD}(x\mid B)
=
\lambda
\sum_e w_e
\left[\phi(h_e)-\phi(h_e-K_e(x))\right]
-c_x.
\]

The gradient approximation is

\[
S_{\rm RD}^{\rm grad}(x\mid B)
=
\lambda\sum_e w_e\phi'(h_e)K_e(x)-c_x.
\]

The current experiments suggest the finite-difference version should be the theory-facing main formula. The gradient version can become numerically extreme when \(h_e\approx 1\), which is exactly the early hard-boundary case.

## Assumptions To State Explicitly

1. Finite tabular MDP.
2. First-hit Green kernel exists: \(\rho(P_{II}^o)<1\), or use the discounted inverse for value reduction.
3. Candidate universe \(C\) is fixed during one greedy step.
4. Option policies are frozen during the marginal calculation.
5. Edge weights \(w_e\) are frozen or treated as a first-order local approximation.
6. Rate cost is modular or locally approximated by \(c_x(B)\).
7. Fatal hard constraints are handled outside the soft RD Lagrangian.

## Implementation Hooks

- `experiments/run_first_boundary_targeted.py` now exports `residual_hidden_probs`, the empirical \(K_e(x)\) row for each option edge.
- `experiments/run_rd_operator_theorem_checks.py` computes:
  - finite-difference operator scores,
  - gradient operator scores,
  - gradient approximation error and its local Taylor bound,
  - truncated Green approximations \(\sum_{t=0}^K P_{II}^tP_{IC}\).

## Current Diagnostic Takeaway

On the first hard split in mazes, \(h_e\) is often nearly one. That makes \(S_{\rm RD}^{\rm grad}\) unstable, while \(S_{\rm RD}^{\rm FD}\) stays interpretable. This supports presenting the finite-difference operator as the theorem, with the GNN-like gradient/truncated operator as an efficient approximation under an additional \(h_e\le 1-\delta\) assumption.
