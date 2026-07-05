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

The formal proof core is split across:

- `proof/RDOperator.lean`: Std-only finite/scaled theorem layer.
- `proof/RDOperatorReal.lean`: Mathlib-backed real-valued finite-matrix layer.

It currently proves:

- exact frozen finite-difference identity,
- adaptive drift decomposition,
- margin stability from \(m>2\epsilon\),
- exact finite-difference identity for arbitrary fixed finite-vector multi-probe risks,
- first-hit certificate existence for the Green-kernel layer,
- finite absorbing-chain Green-kernel obligations:
  \(K=e_b^\top(I-P_{II})^{-1}P_{IC}\) equals the first-hit kernel, entries are
  nonnegative, and row mass is bounded,
- truncated Green convergence/error obligations:
  \(\sum_{t=0}^K P_{II}^tP_{IC}\) plus a nonnegative tail equals the Green
  kernel, so a tail bound gives an epsilon approximation/convergence bound,
- bits-distortion finite-difference/Taylor obligations for
  \(\phi(h)=-\log_2(1-h+\epsilon)\),
- discounted Bellman residual-to-value-gap bound in scaled rational form,
- group-constraint feasibility from zero group violations,
- finite-option graph-SMDP Bellman sup-norm contraction/non-expansion and
  stability of repeated Bellman iterates,
- real finite-matrix Green facts:
  \((I-P_{II})^{-1}P_{IC}\) solves the absorbing-chain linear system,
  nonnegative finite sums imply Green nonnegativity, and row-mass bounds imply
  entry bounds,
- real Neumann/truncated Green convergence under a tail-bound certificate,
- Mathlib derivative of
  \(\phi(h)=-\log_2(1-h+\epsilon)\),
- real finite-option max Bellman contraction and real residual-to-value-gap
  bounds.
- row-substochastic Neumann tail bounds:
  \(P_{II}\ge 0\), row mass \(\le q<1\), and bounded exit mass imply
  \(P_{II}^nP_{IC}\) decays geometrically and finite tails are bounded by
  \(\mathrm{exitBound}\,q^{K+1}/(1-q)\),
- weighted spectral-radius / Collatz-Wielandt certificate:
  if \(P_{II}w\le q w\) for a nonnegative weight vector \(w\) and \(q<1\), then
  \(P_{II}^nP_{IC}\) and finite Neumann tails obey the sharper weighted
  geometric bound,
- bits-curvature/Taylor layer:
  `bitsPhiDeriv` differentiates to `bitsPhiSecond`, a positive margin
  \(\delta\le 1-h+\epsilon\) bounds curvature, and Mathlib Taylor converts that
  curvature bound into a first-order remainder bound,
- automatic `iteratedDerivWithin` glue:
  on nondegenerate closed intervals, the proof now derives the
  `bitsPhiSecond` curvature identity internally, so the final bits-Taylor bound
  does not need a supplied curvature equality.

This is now a Lean-checked finite/scaled layer plus a first Mathlib `Real`
instantiation. The remaining technical proof work is now optional polish:
connect Mathlib's `spectrum` API directly to the weighted certificate, and add a
`tsum`/infinite-tail formulation beside the finite-tail bound.

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

## GPT Answer 10 Follow-up: Unified Benchmark + Proof Layer

`GPT_answer_10.md` makes the paper framing explicit:

```text
Frozen RD Green Operator is the theorem.
Adaptive group-constrained beam search is the solver.
```

The code now has a single benchmark entry point:

```text
experiments/run_core_benchmark.py
experiments/output/core_benchmark/summary.md
```

The table compares:

```text
full_vi
graph_rd_joint
graph_rd_surrogate_joint
group_constrained_rd
eigenoptions_sqrt
betweenness_sqrt
random_landmarks_sqrt
coverage_sqrt
```

over `corridor`, `open_room`, `four_rooms`, and `maze` with deterministic and stochastic slip settings. Each row reports full VI cost, construction/kernel/SMDP solve cost, backup compression, start/value gap, rollout success, and hidden-boundary audit metrics.

The first compact run shows the intended pattern:

```text
planning-only speedup can be large:
  graph_rd_joint mean ≈ 109x
  graph_rd_surrogate_joint mean ≈ 109x
  group_constrained_rd mean ≈ 58x

but total single-task time is still dominated by construction:
  exact RD and group-constrained RD remain slower than full VI on tiny maps.
```

So the current evidence supports the careful claim:

```text
the operator compresses planning propagation;
the remaining bottleneck is discovery / adaptive construction;
multi-task amortization or better operator approximations are needed for end-to-end speed.
```

The compact core run deliberately used a small beam (`W=2`, expand `4`), so one
open-room stochastic group-constrained row remains infeasible. That should be
treated as a beam-budget diagnostic rather than as a failure of the frozen
operator. The earlier wider group-constrained run (`W=4`, expand `6`) reached
feasibility on `open_room_7`, `four_rooms_9`, and `maze_9`.

The proof file was also extended with the obligations GPT asked for:

```text
first-hit certificate existence
finite absorbing-chain Green kernel formula / nonnegativity / row bound
truncated Green convergence and epsilon tail error
bits-distortion finite-difference / Taylor error
finite-option graph-SMDP Bellman contraction
discounted residual-to-value-gap bound
group-constrained feasibility
```

These are Lean-checked as finite/scaled certificates. A Mathlib-real
instantiation remains the next formalization step, but the proof obligations
the paper needs are now named and mechanically checked.

## Submission Evidence Pass

The current top-conference risk list is now partially instrumented rather than
just discussed.

New scripts:

```text
experiments/run_large_scale_compression.py
experiments/run_solver_validity.py
```

New outputs:

```text
experiments/output/large_scale_compression/summary.md
experiments/output/amortized_multitask_large_allstates/summary.md
experiments/output/solver_validity/summary.md
```

### Large-scale compression

The large-scale script skips policy iteration and measures the core compression
story directly:

```text
full VI cost:
  sweeps * |S| * |A|

compressed graph cost:
  construction + first-boundary kernel time + graph SMDP sweeps * |B| * |O|
```

Current compact result:

```text
max states: 144
best graph planning-only speedup: 2471x
best end-to-end speedup: 10.6x
worst start-value gap: 0.0785
```

This is good evidence for compressed propagation, but not yet for universal
end-to-end speed. Exact dense first-hit Green solves dominate `open_room_12`
and `corridor_128`. This is now the main systems/method gap.

### Multi-task amortization

The all-state goal variant is a negative control. It includes 25 sampled goals
as graph vertices up front, then reuses the graph for all tasks. This is exact
for those goals, but the graph gets too dense on the current small maps:

```text
corridor_64 best speedup at 25 all-state tasks: about 0.32x
maze_13 best speedup at 25 all-state tasks: about 0.29x
```

So the paper should not claim arbitrary interior-goal multitask speedups yet.
The defensible claim is boundary/reward-family amortization. If we want a
stronger arbitrary-goal claim, the next method piece is an option-edge
reward-feature kernel or a cheap way to add task goals without rebuilding dense
first-hit kernels.

### Solver validity

`run_solver_validity.py` now compares:

```text
exhaustive oracle over small frozen candidate subsets
operator-only greedy/beam
exact-refined beam
```

The exact-refined beam uses the frozen operator as a proposal/pruning device,
then evaluates the top candidates with the actual group-constrained RD metric.
On the compact run:

```text
exact boundary matches:      14 / 18
zero violation-gap rows:     14 / 18
feasibility matches:         15 / 18
oracle subsets evaluated:    66
```

This resolves the most direct “adaptive solver is only a heuristic” objection
for small maps: operator-only search can fail with a narrow beam, but the
operator-proposed exact-refined solver tracks the exhaustive oracle whenever
the split budget/candidate pool can express the oracle solution. In the paper,
this should be the submission-facing solver, while the pure operator beam is a
fast ablation.

## Truncated Green Kernel Implementation

The proof layer's truncated Green object is now executable in the experiment
pipeline:

```text
bellman_kron_reduce_truncated
first_hit_reduce_truncated
first_hit_interior_occupancy_truncated
```

The implementation replaces dense inverse solves with finite Neumann prefixes:

```text
(I - gamma P_II)^-1      -> sum_{t=0}^K gamma^t P_II^t
(I - P_II)^-1            -> sum_{t=0}^K P_II^t
first-hit kernel K_BC    -> sum_{t=0}^K P_II^t P_IC
```

For the global boundary reducer, the implementation avoids forming full
`P_II^t` matrices. It propagates the boundary-to-interior frontier
`P_BI P_II^t`, which is cheaper when the graph boundary is small. First-hit
and soft-occupancy kernels use vector frontiers from the source state.

I also removed unnecessary absorbing-matrix rebuilds for first-hit kernels:
all first-hit calls for a target policy can reuse the policy's free transition
matrix because terminal rows do not enter the Green block.

Current benchmark:

```text
experiments/output/kernel_approximation_large/summary.md
```

Key result:

```text
corridor_128 / endpoints:
  exact kernel time ≈ 2.97s
  truncated K=128 kernel time ≈ 0.025s
  kernel speedup ≈ 119x
  start-value difference ≈ 0.123

open_room_12 / endpoints:
  exact kernel time ≈ 3.30s
  truncated K=64 kernel time ≈ 0.026s
  kernel speedup ≈ 125x
  start-value difference ≈ numerical zero
```

The practical lesson is not “always truncate at a fixed K.” Long corridors need
larger K because the first-hit time itself is long. Open rooms mix faster and
benefit immediately. The next principled version should choose K per edge by a
tail certificate:

\[
\frac{q^{K+1}}{1-q} \le \epsilon
\]

using either a row-substochastic bound or the weighted certificate already
formalized in the Mathlib layer.

## Adaptive Green Kernel

The code now has that next version:

```text
first_hit_mode = "adaptive"
first_hit_truncation_steps = max_K
first_hit_tail_tol = epsilon
```

For each first-hit edge, the solver runs the Neumann frontier until the
remaining mass certificate is small:

```text
remaining_hit_mass = ||frontier_K||_1
discounted_reward_tail <= gamma^(K+1) ||frontier_K||_1 / (1-gamma)
geometric_tail = q^(K+1)/(1-q) if q < 1

tail_bound = min(max(remaining_hit_mass, discounted_reward_tail), geometric_tail)
```

The global graph reducer uses the same idea row-wise with the
boundary-to-interior frontier `P_BI P_II^K`.

Current evidence:

```text
experiments/output/kernel_adaptive_benchmark/summary.md
experiments/output/large_scale_compression_adaptive/summary.md
```

Highlights:

```text
corridor_128:
  adaptive eps=1e-6 chooses K up to 160
  start-value diff vs exact ≈ 1e-8
  kernel speedup vs exact ≈ 45x

open_room_12:
  adaptive eps=1e-6 chooses K up to 41
  start-value diff vs exact ≈ 1.8e-8
  kernel speedup vs exact ≈ 164x

maze_13:
  adaptive eps=1e-6 chooses K up to 42
  start-value diff vs exact ≈ 1.5e-8
```

This resolves the fixed-K failure mode. Long corridors no longer need a
manually chosen global K, while fast-mixing maps keep the cheap short prefix.
For the paper, the clean hierarchy is:

```text
Exact Green kernel:
  reference operator and proof target

Adaptive Green kernel:
  main implementation with certified truncation tolerance

Fixed-K Green:
  ablation demonstrating why adaptive K matters
```

This is a good point to ask GPT for a theory/framing critique after pushing.
The question should focus on whether the current frontier-tail certificate is
strong enough for the main paper claim, or whether it should be replaced by the
fully weighted spectral certificate before submission.

## Adaptive Green Score Certificate

GPT's follow-up critique says the fully weighted spectral certificate is not a
submission blocker as long as the claim is score-certified rather than
arbitrary-weight spectral-certified. The right hierarchy is:

```text
Exact Green:
  reference operator and small-scale oracle

Adaptive Green:
  main tail-certified Neumann-prefix implementation

Fixed-K Green:
  ablation
```

The implementation now has the missing score-level certificate:

```text
experiments/run_adaptive_green_certification.py
```

For each candidate split \(x\), it turns adaptive first-hit tail bounds into a
finite-difference bits-RD score interval:

```text
S_exact(x) in [S_hat(x) - B_x, S_hat(x) + B_x]
```

using entrywise first-hit intervals and monotone interval arithmetic for:

\[
\phi(h)-\phi(h-K_x).
\]

The top-1 decision is accepted only when:

\[
\hat S_1 - B_1 > \hat S_2 + B_2.
\]

Otherwise the row is explicitly marked:

```text
needs_refinement_or_exact_fallback
```

Current table:

```text
experiments/output/adaptive_green_certification/summary.md
```

Summary:

```text
exact top-1 matches:        8 / 8
interval-certified top-1:   4 / 8
```

The accepted cases are `open_room_12` and `four_rooms_11` for both
\(\epsilon=10^{-3}\) and \(10^{-6}\). `corridor_128` agrees with exact but has a
zero strict margin due to symmetry. `maze_13` agrees with exact but remains
uncertified because the bits distortion interval is conservative near hidden
mass one.

This gives the intended anytime algorithm:

```text
1. run adaptive Green at an initial tail tolerance
2. accept if the score intervals separate top-1 from runner-up
3. otherwise lower epsilon / increase max horizon
4. if still ambiguous, exact-fallback only on the ambiguous top set
```

The resulting paper claim should be:

```text
adaptive Green is decision-certified whenever it commits without fallback
```

not:

```text
adaptive Green is spectrally certified for every possible downstream weighted
objective
```

## Fully Weighted Spectral Certificate Attempt

I also tried the stronger route rather than leaving it only as future work.
The real Lean layer now contains:

```text
spectral_certificate_signed_neumann_term_entry_abs_le
spectral_certificate_signed_finite_neumann_tail_entry_abs_le
weightedScore_error_le
interval_certified_top_choice
```

The important upgrade is that the weighted certificate is not restricted to
nonnegative hit-probability blocks. If:

\[
P_{II}w \le q w,\qquad q<1,
\]

then signed downstream feature/reward tails are bounded in weighted sup-norm.
For fixed nonnegative downstream weights \(a_e\), entrywise tail bounds imply:

\[
|S(K)-S(\hat K)| \le \sum_e a_e T_e.
\]

This is the formal bridge from a spectral/weighted Green tail to an RD score
interval.

The executable diagnostic is:

```text
experiments/run_weighted_spectral_certificate.py
experiments/output/weighted_spectral_certificate/summary.md
```

It checks a Collatz-style certificate on the current endpoint suite:

```text
P_II w <= q w, q < 1
tail <= c * w_start * q^(K+1)/(1-q)
```

Main observation:

```text
raw row q < 1:
  0 / 16 edge-basis rows

weighted q < 1:
  16 / 16 edge-basis rows
```

So the weighted spectral theorem really does certify cases that the plain
row-substochastic theorem cannot certify.

The catch is conditioning. The optimized floating-point weights can have
dynamic range from about \(10^{12}\) to \(10^{20}\). Corridor also remains very
conservative:

```text
corridor_128, K=128:
  weighted certified row tail <= about 125
  actual row tail             <= about 0.976
```

This means the fully weighted spectral certificate is now mathematically
plausible and Lean-backed, but not yet a good default numerical implementation.
For the paper, the careful wording is:

```text
We provide a weighted spectral sufficient certificate in the proof layer.
The scalable implementation uses frontier-tail / score-interval certification,
which is tighter and numerically better conditioned in the current experiments.
```

## Certified Adaptive Green With Top-Set Exact Fallback

GPT answer 12 says the main implementation should not be "pure adaptive Green"
without fallback. It should be:

```text
Certified Adaptive Green with top-set exact fallback
```

That is now implemented in:

```text
experiments/run_adaptive_green_certification.py
```

The decision rule is:

```text
if L_top > max_runner U:
  accept adaptive top-1
else:
  A = {x : U_x >= max_z L_z}
  exact-score candidates in A
  accept exact best in A if it beats all outside upper bounds
```

The proof layer now includes:

```text
top_set_exact_fallback_global_optimal
top_set_exact_fallback_beats_outside
```

so the fallback step is not just an implementation convention; it has the
corresponding real-valued order theorem.

Updated evidence:

```text
experiments/output/adaptive_green_certification/summary.md
```

Summary:

```text
exact top-1 matches:        8 / 8
interval-certified top-1:   4 / 8
fallback rows:              4 / 8
final certified decisions:  8 / 8
```

Interpretation:

```text
open_room_12 / four_rooms_11:
  adaptive interval decides directly

corridor_128:
  tie-uncertified, so the output is a certified top-set plus canonical tie-break

maze_13:
  curvature-uncertified full ambiguous set, so exact fallback preserves
  correctness while giving up speed on that regime
```

The submission-facing claim should now be:

```text
Exact Green is the reference RD operator.
Adaptive Green is the default tail-certified approximation.
Unseparated intervals trigger exact fallback on the ambiguous top set.
```

not:

```text
pure adaptive Green certifies every top-1 decision by itself
```
