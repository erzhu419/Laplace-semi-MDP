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

## Frozen Versus Adaptive Objective

The main theorem should be stated against a frozen local objective, not the fully recomputed adaptive algorithm.

Let

\[
\theta_B=(C_B,\Pi_B,E_B,w_B,c_B)
\]

collect the current candidate universe, option policies, active edge set, edge weights, and local rate cost. The frozen objective is

\[
\mathcal L_{\theta_B}^{\rm fr}(A)=R_{\theta_B}(A)+\lambda D_{\theta_B}(A),
\qquad A\supseteq B,
\]

where \(\theta_B\) is kept fixed even when evaluating \(A=B\cup\{x\}\). The adaptive objective is

\[
\mathcal L^{\rm ad}(A)=R_{\theta_A}(A)+\lambda D_{\theta_A}(A),
\]

where adding \(x\) can change the candidate universe, options, edges, occupancy weights, and rate terms.

Thus

\[
S_{\rm FD}(x\mid B)=
\mathcal L_{\theta_B}^{\rm fr}(B)
-
\mathcal L_{\theta_B}^{\rm fr}(B\cup\{x\})
\]

is an exact identity, while full recomputation measures

\[
S_{\rm ad}(x\mid B)=
\mathcal L_{\theta_B}^{\rm fr}(B)
-
\mathcal L_{\theta_{B\cup\{x\}}}^{\rm ad}(B\cup\{x\}).
\]

The difference

\[
A(x\mid B)=S_{\rm ad}(x\mid B)-S_{\rm FD}(x\mid B)
\]

is the adaptive recomputation drift. Actual-recompute mismatch is therefore not a refutation of the frozen theorem; it means the outer adaptive algorithm is no longer optimizing the same frozen local objective.

`experiments/run_rd_operator_theorem_checks.py` now supports `--with-frozen-recompute` to verify the exact identity and `--with-actual-recompute` to expose the drift. The expected pattern is:

\[
S_{\rm FD}=S_{\rm frozen}
\]

to numerical precision, while

\[
S_{\rm actual}\ne S_{\rm frozen}
\]

when recomputation drift is large.

The same script also supports `--with-recompute-modes`, which adds bridge diagnostics:

- `rate_only_score`: recompute only the rate term while keeping the frozen distortion.
- `occupancy_only_score`: use recomputed occupancy weights on the frozen first-hit kernels.
- `edge_only_score`: use recomputed first-hit kernels for the old edge keys with frozen weights.
- `edge_option_uniform_score`: recompute the edge/option library under a uniform audit objective.
- `actual_recompute_score`: full adaptive recompute.

On the current small diagnostic suite, rate-only, occupancy-only, and old-edge/kernel-only usually preserve the FD top split. The cases where full adaptive changes the top split are driven by larger edge/option-library drift, especially when the newly added boundary creates a substantially different graph-option library.

## Answer 8 Follow-up Diagnostics

The current experiment pass adds the requested theorem-facing diagnostics.

- Margin-stability: `summary.csv` now reports `fd_margin`, `epsilon_adapt_observed`, `margin_stability_condition`, and `margin_stability_correct`. The intended theorem check is exactly
  \[
  m>2\epsilon_{\rm adapt}\Rightarrow \arg\max S_{\rm FD}=\arg\max S_{\rm actual}.
  \]
  On `rd_operator_theorem_checks_actual_small`, the open-room case where the condition is true is stable; the maze/four-room mismatch cases fail the margin condition, which is what the theorem should predict.
- Baseline ranking: candidate rows and summaries now include `raw_hidden`, `random`, `spectral`, `betweenness`, `value_gradient`, and `degree` ranks, top-state matches, Kendall tau against \(S_{\rm FD}\), and actual-recompute regret where available.
- Runtime/amortization proxy: the same summary reports base graph evaluation time, cheap FD/gradient operator scoring time, full actual recomputation time, and truncated-Green timing per \(K\). In the small recompute suite, full recomputation is roughly \(2\text{x}\) to \(23\text{x}\) slower than the frozen operator score.
- Drift separation: `rate_only`, `occupancy_only`, `edge_only`, and `edge_option_uniform` modes separate rate drift, occupancy-weight drift, old-edge first-hit drift, and option/edge-library drift. Current evidence still says the most damaging mismatch comes from changing the option/edge library, not from the frozen finite-difference identity.
- Held-out probes/tasks: `experiments/run_rd_operator_generalization.py` evaluates the selected boundary under held-out residual probes and alternate goals. The first run shows a useful warning: the current \(S_{\rm FD}\) selection is good as a local frozen operator, but not yet robust as a task/probe-general abstraction objective. In maze with only two splits, spectral/random landmarks can look better under held-out probes because the RD local score overcommits to the training residual universe.

## Lean Proof Core

The formal proof core is in `proof/RDOperator.lean`.

It currently proves:

- exact frozen finite-difference identity,
- adaptive drift decomposition,
- margin stability from \(m>2\epsilon\),
- abstract graph-SMDP Bellman contraction/non-expansion obligations.

This is intentionally not yet a full real-analysis proof of first-hit Green kernels. The next proof layer should instantiate the abstract integers/reweighted terms with real-valued finite MDP quantities, preferably with Mathlib: stochastic matrix absorption, truncated Green convergence, Taylor error for the bits distortion, and sup-norm Bellman contraction over finite graph options.

## GPT Answer 9 Follow-up: Fixed Basis + Multi-Probe RD

`GPT_answer_9.md` sharpens the failure mode from the held-out diagnostics:

```text
exact frozen operator != cross-probe generalization
```

The right next algorithmic shape is two-layer:

```text
1. freeze a probe-independent multi-task basis C0 / O0
2. optimize a robust multi-probe RD objective on that fixed basis
```

I added `experiments/run_rd_multiprobe_basis.py` to test this directly. It builds two basis modes:

- `fixed`: topology + spectral + coverage + deterministic random anchors;
- `residual_train`: a deliberately leakier basis made from train residual probes.

Then it runs several frozen robust objectives over the same train probes:

- `single`: first train probe only;
- `mean`: average train distortion;
- `mean_cvar`: `(1 - eta) * mean + eta * CVaR_alpha`;
- `max`: minimax / worst-probe distortion.

The implemented multi-probe finite-difference score is:

\[
S_\rho(x\mid B)
=
\lambda
\left[
\rho(D(B))-\rho(D(B)-\Delta(x))
\right]
-c_x,
\]

where each component of \(\Delta(x)\) is the per-probe first-hit Green finite difference.

The Lean proof core now includes `MultiProbeObjective.fd_exact`, which proves this formula is exactly the frozen objective drop for any fixed finite-vector risk aggregator \(\rho\). This keeps the theory clean: mean, max, CVaR, and smoothmax all share the same exactness theorem.

`experiments/run_rd_probe_count_scaling.py` adds a first probe-count scaling table over a fixed basis. The first result is a warning rather than a victory lap: increasing the prefix length of an arbitrary probe pool does not monotonically reduce held-out distortion. The next version should use leave-one-lens-out or stratified probe sampling so each train family covers topology, stochasticity, and value-gradient lenses.

`experiments/run_rd_lens_validation.py` now runs that next validation. It has two protocols: leave-one-lens-out and stratified one-per-group. On the first `maze_9/four_rooms_9/open_room_7` pass, minimax is clearly more robust than `mean_cvar` in leave-one-lens-out average held-out distortion, but it still has individual lens failures. I also added `group_mean_cvar` and `group_max_cvar`; in this small suite they choose the same boundaries as the corresponding ungrouped risks, which suggests the next real fix is group-specific constraints/budgets rather than another scalarized robust risk.

`experiments/run_rd_group_constrained.py` implements that constrained version. It minimizes boundary rate implicitly by stopping once all group budgets are feasible:

\[
\operatorname{CVaR}_{\rm topology}(B)\le\epsilon_{\rm topology},\quad
\operatorname{CVaR}_{\rm value}(B)\le\epsilon_{\rm value},\quad
\operatorname{CVaR}_{\rm stochastic}(B)\le\epsilon_{\rm stochastic}.
\]

The first pass shows the constrained formulation is materially different from scalar mean/CVaR: on `maze_9` and `four_rooms_9`, group-constrained beam search reaches feasibility with fewer vertices than scalar max, while scalar mean/CVaR violates all groups. A one-step greedy variant can dead-end, so the current optimizer uses a small beam; this is evidence that adaptive graph construction is non-submodular even when the frozen per-step operator is exact.
