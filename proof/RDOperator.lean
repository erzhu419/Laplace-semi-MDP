import Std

/-!
# RD Boundary Green Operator: finite proof core

This file keeps the formal core deliberately finite and tabular.  The
experiment-side operator uses real-valued probabilities, but the theorems below
state the algebraic invariants that must survive any implementation:

1. a frozen RD marginal score is exactly a finite difference of a frozen
   objective;
2. adaptive recomputation differs from that identity only by an explicit drift
   term;
3. a top split is stable when the frozen margin is larger than twice the
   approximation/adaptation error;
4. the first-hit Green kernel layer has explicit finite absorbing-chain
   certificates for the matrix formula, non-negativity, row bounds, and
   truncated-tail error;
5. bits distortion finite differences have a separate Taylor-error certificate;
6. graph-SMDP Bellman updates are contractions once the finite option backup
   supplies the usual discounted sup-norm inequality;
7. Bellman model residuals imply value-gap bounds in scaled rational form.

`weightedDistortion*` means the Lagrange multiplier has already been applied,
so it corresponds to `lambda * D` in the paper notation.  This avoids importing
Mathlib just for ring-normalization over integers.
-/

namespace RDBoundaryGreen

variable {State : Type}

/-- Frozen local objective for one greedy split.

The frozen data contains the candidate universe, option policies, edge weights,
and local rate increment from the current boundary `B`.  Adding a candidate
state is evaluated without rebuilding those objects.
-/
structure FrozenObjective (State : Type) where
  rateBase : Int
  weightedDistortionBefore : Int
  weightedDistortionDrop : State -> Int
  rateCost : State -> Int

namespace FrozenObjective

/-- Frozen weighted distortion after adding one candidate. -/
def weightedDistortionAfter (theta : FrozenObjective State) (x : State) : Int :=
  theta.weightedDistortionBefore - theta.weightedDistortionDrop x

/-- Frozen objective before the split: `R(B) + lambda * D(B)`. -/
def objectiveBefore (theta : FrozenObjective State) : Int :=
  theta.rateBase + theta.weightedDistortionBefore

/-- Frozen objective after the split: `R(B) + c_x + lambda * D(B union {x})`. -/
def objectiveAfter (theta : FrozenObjective State) (x : State) : Int :=
  theta.rateBase + theta.rateCost x + theta.weightedDistortionAfter x

/-- RD finite-difference operator score: distortion drop minus rate cost. -/
def fdOperator (theta : FrozenObjective State) (x : State) : Int :=
  theta.weightedDistortionDrop x - theta.rateCost x

/-- Main identity: the operator is exactly the frozen objective drop. -/
theorem fd_exact (theta : FrozenObjective State) (x : State) :
    theta.fdOperator x = theta.objectiveBefore - theta.objectiveAfter x := by
  simp [fdOperator, objectiveBefore, objectiveAfter, weightedDistortionAfter]
  omega

/-- Score produced by a fully adaptive recomputation after adding `x`. -/
def adaptiveScore (theta : FrozenObjective State) (adaptiveObjectiveAfter : Int) : Int :=
  theta.objectiveBefore - adaptiveObjectiveAfter

/-- Adaptive drift relative to the frozen finite-difference operator. -/
def adaptiveDrift (theta : FrozenObjective State) (x : State) (adaptiveObjectiveAfter : Int) : Int :=
  theta.adaptiveScore adaptiveObjectiveAfter - theta.fdOperator x

/-- Adaptive recomputation decomposes into frozen score plus drift. -/
theorem adaptive_decomposition
    (theta : FrozenObjective State) (x : State) (adaptiveObjectiveAfter : Int) :
    theta.adaptiveScore adaptiveObjectiveAfter =
      theta.fdOperator x + theta.adaptiveDrift x adaptiveObjectiveAfter := by
  simp [adaptiveDrift]
  omega

end FrozenObjective

/-- Margin-stability theorem.

If `xBest` has frozen score margin greater than `2 * eps` over the second-best
upper envelope, and every adaptive/approximate score differs from the frozen
score by at most `eps` in the needed one-sided sense, then every other candidate
still scores strictly below `xBest`.
-/
theorem margin_stability
    {score adaptive : State -> Int} {xBest xSecond y : State} {eps : Int}
    (hSecond : ∀ z, z ≠ xBest -> score z ≤ score xSecond)
    (hMargin : score xSecond + 2 * eps < score xBest)
    (hUpper : ∀ z, adaptive z ≤ score z + eps)
    (hLowerBest : score xBest - eps ≤ adaptive xBest)
    (hy : y ≠ xBest) :
    adaptive y < adaptive xBest := by
  have hySecond : score y ≤ score xSecond := hSecond y hy
  have hyUpper : adaptive y ≤ score y + eps := hUpper y
  omega

/-- Same stability theorem, named for Green-kernel approximations.

Use this for finite-difference vs gradient, truncated Green, or any learned
operator surrogate once a uniform score error bound is available.
-/
theorem approximation_top_stability
    {exact approx : State -> Int} {xBest xSecond y : State} {eps : Int}
    (hSecond : ∀ z, z ≠ xBest -> exact z ≤ exact xSecond)
    (hMargin : exact xSecond + 2 * eps < exact xBest)
    (hApproxUpper : ∀ z, approx z ≤ exact z + eps)
    (hApproxLowerBest : exact xBest - eps ≤ approx xBest)
    (hy : y ≠ xBest) :
    approx y < approx xBest :=
  margin_stability hSecond hMargin hApproxUpper hApproxLowerBest hy

/-- Frozen vector-valued objective for multi-probe/group RD.

`Probe -> Int` is the finite distortion vector, and `risk` is any finite-vector
aggregator: mean, max, CVaR, smoothmax approximation, or a paper-specific
robust risk.  The theorem below only needs that `risk` is fixed during the
greedy step.
-/
structure MultiProbeObjective (State Probe : Type) where
  rateBase : Int
  risk : (Probe -> Int) -> Int
  distortionBefore : Probe -> Int
  distortionDrop : State -> Probe -> Int
  rateCost : State -> Int

namespace MultiProbeObjective

/-- Probe-wise distortion vector after adding candidate `x`. -/
def distortionAfter (theta : MultiProbeObjective State Probe) (x : State) : Probe -> Int :=
  fun probe => theta.distortionBefore probe - theta.distortionDrop x probe

/-- Frozen robust objective before the split. -/
def objectiveBefore (theta : MultiProbeObjective State Probe) : Int :=
  theta.rateBase + theta.risk theta.distortionBefore

/-- Frozen robust objective after the split. -/
def objectiveAfter (theta : MultiProbeObjective State Probe) (x : State) : Int :=
  theta.rateBase + theta.rateCost x + theta.risk (theta.distortionAfter x)

/-- Multi-probe RD finite-difference operator. -/
def fdOperator (theta : MultiProbeObjective State Probe) (x : State) : Int :=
  theta.risk theta.distortionBefore - theta.risk (theta.distortionAfter x) - theta.rateCost x

/-- Multi-probe exactness: the robust operator is the frozen objective drop. -/
theorem fd_exact (theta : MultiProbeObjective State Probe) (x : State) :
    theta.fdOperator x = theta.objectiveBefore - theta.objectiveAfter x := by
  simp [fdOperator, objectiveBefore, objectiveAfter]
  omega

end MultiProbeObjective

/-!
## First-hit and Green approximation obligations

The probabilistic paper proof will instantiate these pathwise certificates with
finite absorbing Markov chains.  Here we prove the finite/scaled theorem layer:
if a path eventually hits a boundary set, then a first hitting time exists; if
an exact Green score decomposes as truncated score plus a tail, a tail bound is
an error bound.
-/

/-- `t` is the first time that `path` reaches the boundary predicate. -/
def FirstHitAt (isBoundary : State -> Prop) (path : Nat -> State) (t : Nat) : Prop :=
  isBoundary (path t) ∧ ∀ k, k < t -> ¬ isBoundary (path k)

/-- A finite first-hit certificate for one path. -/
structure FirstHitCertificate (State : Type) where
  isBoundary : State -> Prop
  path : Nat -> State
  firstHitTime : Nat
  firstHitValid : FirstHitAt isBoundary path firstHitTime

/-- A first-hit certificate gives the existence statement needed by the kernel. -/
theorem first_hit_exists_from_certificate
    (cert : FirstHitCertificate State) :
    ∃ t, FirstHitAt cert.isBoundary cert.path t :=
  ⟨cert.firstHitTime, cert.firstHitValid⟩

/-!
## Finite absorbing-chain Green kernel obligations

The paper notation writes the first-hit kernel as

`K = e_b^T (I - P_II)^{-1} P_IC`.

Without importing Mathlib matrices/reals, the formal core keeps the finite
absorbing-chain computation as a certificate.  `greenFormula` is the value
computed by the matrix expression above, and `kernel` is the first-hit kernel
used by the RD operator.  The theorems prove exactly which facts downstream
arguments may use: formula equality, non-negativity, bounded row mass, and a
tail decomposition for truncated Neumann/Green approximations.
-/

/-- Finite first-hit Green kernel certificate for a frozen graph-option model. -/
structure FirstHitGreenKernel (Edge Candidate : Type) where
  /-- First-hit kernel used by the operator. -/
  kernel : Edge -> Candidate -> Nat
  /-- Matrix expression `e_b^T (I - P_II)^{-1} P_IC`, scaled to naturals. -/
  greenFormula : Edge -> Candidate -> Nat
  /-- Truncated Green approximation, corresponding to `sum_{t=0}^K P_II^t P_IC`. -/
  truncated : Nat -> Edge -> Candidate -> Nat
  /-- Nonnegative tail left after the truncation horizon. -/
  tail : Nat -> Edge -> Candidate -> Nat
  /-- Scaled row mass of `kernel e ·`. -/
  rowSum : Edge -> Nat
  /-- Uniform row-mass budget; for probabilities this is normally the scale `1`. -/
  rowMassBound : Nat
  /-- First-hit kernel equals the finite absorbing-chain Green formula. -/
  formula : ∀ e c, kernel e c = greenFormula e c
  /-- Exact kernel decomposes into truncated prefix plus nonnegative tail. -/
  decompose : ∀ K e c, kernel e c = truncated K e c + tail K e c
  /-- Each entry is bounded by its row mass. -/
  entry_le_rowSum : ∀ e c, kernel e c ≤ rowSum e
  /-- Row mass is uniformly bounded. -/
  rowSum_le_bound : ∀ e, rowSum e ≤ rowMassBound

namespace FirstHitGreenKernel

/-- The matrix Green formula is legal for the operator: it equals first-hit mass. -/
theorem formula_eq_kernel
    (G : FirstHitGreenKernel Edge Candidate) (e : Edge) (c : Candidate) :
    G.greenFormula e c = G.kernel e c := by
  rw [G.formula e c]

/-- First-hit Green entries are nonnegative in the scaled finite model. -/
theorem entry_nonnegative
    (G : FirstHitGreenKernel Edge Candidate) (e : Edge) (c : Candidate) :
    0 ≤ G.kernel e c :=
  Nat.zero_le _

/-- First-hit Green rows satisfy the supplied absorbing-chain row bound. -/
theorem row_sum_bounded
    (G : FirstHitGreenKernel Edge Candidate) (e : Edge) :
    G.rowSum e ≤ G.rowMassBound :=
  G.rowSum_le_bound e

/-- Each kernel entry is bounded by the global row-mass bound. -/
theorem entry_le_rowMassBound
    (G : FirstHitGreenKernel Edge Candidate) (e : Edge) (c : Candidate) :
    G.kernel e c ≤ G.rowMassBound :=
  Nat.le_trans (G.entry_le_rowSum e c) (G.rowSum_le_bound e)

/-- Truncation error is exactly the remaining Green tail entry. -/
theorem truncated_error_decomposition
    (G : FirstHitGreenKernel Edge Candidate) (K : Nat) (e : Edge) (c : Candidate) :
    G.kernel e c = G.truncated K e c + G.tail K e c :=
  G.decompose K e c

/-- A uniform tail bound gives a uniform truncated-Green approximation bound. -/
theorem truncated_error_le_tail_bound
    (G : FirstHitGreenKernel Edge Candidate) (tailBound : Nat -> Nat)
    (hTail : ∀ K e c, G.tail K e c ≤ tailBound K)
    (K : Nat) (e : Edge) (c : Candidate) :
    G.kernel e c ≤ G.truncated K e c + tailBound K := by
  rw [G.decompose K e c]
  exact Nat.add_le_add_left (hTail K e c) (G.truncated K e c)

/-- Epsilon-form convergence statement for truncated Green prefixes. -/
theorem truncated_eventual_epsilon_bound
    (G : FirstHitGreenKernel Edge Candidate) (tailBound : Nat -> Nat)
    (hTail : ∀ K e c, G.tail K e c ≤ tailBound K)
    {K eps : Nat} (hEps : tailBound K ≤ eps)
    (e : Edge) (c : Candidate) :
    G.kernel e c ≤ G.truncated K e c + eps := by
  have hTailEps : G.tail K e c ≤ eps := Nat.le_trans (hTail K e c) hEps
  rw [G.decompose K e c]
  exact Nat.add_le_add_left hTailEps (G.truncated K e c)

/-- If the Green tail vanishes at horizon `K`, the truncated kernel is exact. -/
theorem truncated_exact_of_zero_tail
    (G : FirstHitGreenKernel Edge Candidate) {K : Nat}
    (hTailZero : ∀ e c, G.tail K e c = 0)
    (e : Edge) (c : Candidate) :
    G.kernel e c = G.truncated K e c := by
  rw [G.decompose K e c, hTailZero e c, Nat.add_zero]

end FirstHitGreenKernel

/-- A finite absorbing Markov-chain certificate exposes its first-hit Green kernel. -/
structure FiniteAbsorbingChain (Edge Candidate : Type) where
  /-- The chain-induced Green kernel, usually computed by the finite inverse formula. -/
  green : FirstHitGreenKernel Edge Candidate

namespace FiniteAbsorbingChain

/-- Finite absorption gives an existing legal first-hit Green kernel. -/
theorem first_hit_green_kernel_exists
    (M : FiniteAbsorbingChain Edge Candidate) :
    ∃ G : FirstHitGreenKernel Edge Candidate,
      (∀ e c, G.greenFormula e c = G.kernel e c) ∧
      (∀ e c, 0 ≤ G.kernel e c) ∧
      (∀ e, G.rowSum e ≤ G.rowMassBound) := by
  refine ⟨M.green, ?_, ?_, ?_⟩
  · intro e c
    exact FirstHitGreenKernel.formula_eq_kernel M.green e c
  · intro e c
    exact FirstHitGreenKernel.entry_nonnegative M.green e c
  · intro e
    exact FirstHitGreenKernel.row_sum_bounded M.green e

end FiniteAbsorbingChain

/-- Epsilon-convergence certificate for truncated Green prefixes. -/
structure TruncatedGreenConvergence (Edge Candidate : Type) where
  green : FirstHitGreenKernel Edge Candidate
  tailBound : Nat -> Nat
  tail_le_bound : ∀ K e c, green.tail K e c ≤ tailBound K
  eventually_below : ∀ eps, ∃ K, tailBound K ≤ eps

namespace TruncatedGreenConvergence

/-- Truncated Green prefixes converge to the certified Green kernel in epsilon form. -/
theorem converges_to_green
    (C : TruncatedGreenConvergence Edge Candidate) :
    ∀ eps e c, ∃ K,
      C.green.kernel e c ≤ C.green.truncated K e c + eps := by
  intro eps e c
  rcases C.eventually_below eps with ⟨K, hK⟩
  refine ⟨K, ?_⟩
  exact FirstHitGreenKernel.truncated_eventual_epsilon_bound
    C.green C.tailBound C.tail_le_bound hK e c

end TruncatedGreenConvergence

/-- Truncated Green score certificate: exact score is truncated score plus tail. -/
structure TruncatedGreen (Candidate : Type) where
  exact : Candidate -> Nat
  truncated : Candidate -> Nat
  tail : Candidate -> Nat
  decompose : ∀ x, exact x = truncated x + tail x

namespace TruncatedGreen

/-- A uniform tail bound controls the exact-vs-truncated score gap. -/
theorem error_le_tail_bound
    (G : TruncatedGreen Candidate) {eps : Nat}
    (hTail : ∀ x, G.tail x ≤ eps) (x : Candidate) :
    G.exact x ≤ G.truncated x + eps := by
  rw [G.decompose x]
  exact Nat.add_le_add_left (hTail x) (G.truncated x)

end TruncatedGreen

/-!
## Bits-distortion finite difference and Taylor obligations

For the paper's bits distortion

`phi(h) = -log_2 (1 - h + eps)`,

the implementation uses real arithmetic.  The proof core isolates the part the
operator proof needs: a finite-difference identity plus a Taylor/linearization
error bound.  A Mathlib-real instantiation can later prove `taylor_error_bound`
from derivatives of `log`; downstream RD theorems only depend on this
certificate.
-/

/-- Scaled bits-distortion Taylor certificate for one frozen candidate universe. -/
structure BitsDistortionTaylor (Candidate : Type) where
  /-- `phi(h_before)`, scaled. -/
  phiBefore : Candidate -> Int
  /-- `phi(h_after)`, scaled. -/
  phiAfter : Candidate -> Int
  /-- First-order/Taylor approximation to the finite difference. -/
  firstOrder : Candidate -> Int
  /-- Signed Taylor remainder. -/
  remainder : Candidate -> Int
  /-- Candidate-specific absolute error budget for the Taylor remainder. -/
  errorBudget : Candidate -> Nat
  /-- Exact finite-difference decomposition. -/
  fd_decompose : ∀ x, phiBefore x - phiAfter x = firstOrder x + remainder x
  /-- Taylor/curvature bound, e.g. from the log second derivative. -/
  remainder_bound : ∀ x, (remainder x).natAbs ≤ errorBudget x

namespace BitsDistortionTaylor

/-- Exact finite difference of the bits distortion. -/
def finiteDifference (Phi : BitsDistortionTaylor Candidate) (x : Candidate) : Int :=
  Phi.phiBefore x - Phi.phiAfter x

/-- The finite difference equals first order term plus Taylor remainder. -/
theorem finite_difference_decomposition
    (Phi : BitsDistortionTaylor Candidate) (x : Candidate) :
    Phi.finiteDifference x = Phi.firstOrder x + Phi.remainder x := by
  exact Phi.fd_decompose x

/-- Taylor bound in the form used by gradient/truncated-Green score proofs. -/
theorem taylor_error_bound
    (Phi : BitsDistortionTaylor Candidate) (x : Candidate) :
    (Phi.finiteDifference x - Phi.firstOrder x).natAbs ≤ Phi.errorBudget x := by
  have h : Phi.finiteDifference x - Phi.firstOrder x = Phi.remainder x := by
    unfold finiteDifference
    have hDecomp := Phi.fd_decompose x
    omega
  rw [h]
  exact Phi.remainder_bound x

/-- Uniform Taylor bound when all candidate-specific budgets are below `eps`. -/
theorem uniform_taylor_error_bound
    (Phi : BitsDistortionTaylor Candidate) {eps : Nat}
    (hBudget : ∀ x, Phi.errorBudget x ≤ eps) (x : Candidate) :
    (Phi.finiteDifference x - Phi.firstOrder x).natAbs ≤ eps :=
  Nat.le_trans (Phi.taylor_error_bound x) (hBudget x)

end BitsDistortionTaylor

/-!
## Residual and group-feasibility obligations

The residual theorem is the usual Bellman-residual-to-value-gap shape, written
in scaled natural numbers: if a contraction proof gives
`oneMinusGamma * valueGap <= residual` and the residual is under the allowed
budget after the same scaling, then the value gap is under budget.
-/

/-- A scaled residual bound implies a scaled value-gap bound. -/
theorem residual_to_value_gap_bound
    {residual valueGap budget oneMinusGamma : Nat}
    (hGap : oneMinusGamma * valueGap ≤ residual)
    (hResidual : residual ≤ oneMinusGamma * budget)
    (hPositive : 0 < oneMinusGamma) :
    valueGap ≤ budget := by
  have hScaled : oneMinusGamma * valueGap ≤ oneMinusGamma * budget := Nat.le_trans hGap hResidual
  exact Nat.le_of_mul_le_mul_left hScaled hPositive

/-- Discounted residual-to-value-gap bound in scaled rational form.

This is the Lean version of

`||V - Vhat||_∞ <= ||T V - That V||_∞ / (1 - gamma)`.

With `gamma = gammaNum / gammaDen`, division is avoided by cross-multiplying:
`(gammaDen - gammaNum) * valueGap <= gammaDen * residual`.
-/
theorem residual_to_value_gap_bound_discounted
    {gammaNum gammaDen residual valueGap budget : Nat}
    (hGamma : gammaNum < gammaDen)
    (hGap : (gammaDen - gammaNum) * valueGap ≤ gammaDen * residual)
    (hResidualBudget : gammaDen * residual ≤ (gammaDen - gammaNum) * budget) :
    valueGap ≤ budget := by
  have hPositive : 0 < gammaDen - gammaNum := Nat.sub_pos_of_lt hGamma
  have hScaled : (gammaDen - gammaNum) * valueGap ≤
      (gammaDen - gammaNum) * budget :=
    Nat.le_trans hGap hResidualBudget
  exact Nat.le_of_mul_le_mul_left hScaled hPositive

/-- Group-risk feasibility certificate. -/
structure GroupConstraints (Boundary Group : Type) where
  risk : Boundary -> Group -> Int
  budget : Group -> Int

namespace GroupConstraints

/-- A 0/1 violation indicator for a group budget. -/
def violation (problem : GroupConstraints Boundary Group) (B : Boundary) (g : Group) : Nat :=
  if problem.risk B g ≤ problem.budget g then 0 else 1

/-- A boundary is feasible when every group risk is within its budget. -/
def feasible (problem : GroupConstraints Boundary Group) (B : Boundary) : Prop :=
  ∀ g, problem.risk B g ≤ problem.budget g

/-- Zero group violations imply group-constrained feasibility. -/
theorem feasible_of_zero_violations
    (problem : GroupConstraints Boundary Group) (B : Boundary)
    (hZero : ∀ g, problem.violation B g = 0) :
    problem.feasible B := by
  intro g
  unfold violation at hZero
  by_cases hBudget : problem.risk B g ≤ problem.budget g
  · exact hBudget
  · have hContradiction := hZero g
    simp [hBudget] at hContradiction

end GroupConstraints

variable {α : Type}

/-- Iterate an abstract planning/update operator. -/
def iterate (T : α -> α) : Nat -> α -> α
  | 0, x => x
  | Nat.succ n, x => iterate T n (T x)

/-- If a Bellman-like update is non-expansive in a metric, all iterates are. -/
theorem nonexpansive_iterate
    {d : α -> α -> Nat} {T : α -> α}
    (hStep : ∀ x y, d (T x) (T y) ≤ d x y) :
    ∀ n x y, d (iterate T n x) (iterate T n y) ≤ d x y := by
  intro n
  induction n with
  | zero =>
      intro x y
      simp [iterate]
  | succ n ih =>
      intro x y
      calc
        d (iterate T (Nat.succ n) x) (iterate T (Nat.succ n) y)
            = d (iterate T n (T x)) (iterate T n (T y)) := by simp [iterate]
        _ ≤ d (T x) (T y) := ih (T x) (T y)
        _ ≤ d x y := hStep x y

/-- Abstract discounted contraction obligation for a graph-SMDP Bellman map.

The paper proof should instantiate this with the sup norm and the graph-option
discount factor.  The field `step_contracts` is the standard RL contraction
inequality in cross-multiplied rational form.
-/
structure DiscountContraction (α : Type) where
  distance : α -> α -> Nat
  T : α -> α
  gammaNum : Nat
  gammaDen : Nat
  step_contracts : ∀ x y,
    gammaDen * distance (T x) (T y) ≤ gammaNum * distance x y

/-- One Bellman step satisfies the supplied contraction inequality. -/
theorem contraction_one_step (C : DiscountContraction α) (x y : α) :
    C.gammaDen * C.distance (C.T x) (C.T y) ≤
      C.gammaNum * C.distance x y :=
  C.step_contracts x y

/-!
## Graph-SMDP Bellman contraction over finite option actions

`GraphSMDPBellman` names the exact obligation for the planning layer.  The
finite option set is part of the data, and `T` is the Bellman backup induced by
maximizing over that set.  The proof does not need to inspect the max directly;
it needs the standard discounted sup-norm inequality for that finite backup.
The theorem below packages that into the contraction statement used by value
iteration, policy evaluation, and residual-to-gap arguments.
-/

/-- Finite-option graph-SMDP Bellman backup with a scaled sup-norm metric. -/
structure GraphSMDPBellman (Value Opt : Type) where
  /-- Frozen finite option/action library used by the abstract graph. -/
  options : List Opt
  /-- Scaled sup norm on finite graph-boundary value functions. -/
  supDistance : Value -> Value -> Nat
  /-- Bellman optimality/evaluation backup over `options`. -/
  T : Value -> Value
  gammaNum : Nat
  gammaDen : Nat
  gammaLtOne : gammaNum < gammaDen
  /-- Sup-norm contraction for the finite-option Bellman backup. -/
  bellman_contracts : ∀ V W,
    gammaDen * supDistance (T V) (T W) ≤ gammaNum * supDistance V W

namespace GraphSMDPBellman

/-- One graph-SMDP Bellman step is a gamma-contraction in sup norm. -/
theorem supnorm_contraction_one_step
    (B : GraphSMDPBellman Value Opt) (V W : Value) :
    B.gammaDen * B.supDistance (B.T V) (B.T W) ≤
      B.gammaNum * B.supDistance V W :=
  B.bellman_contracts V W

/-- The graph-SMDP Bellman map is non-expansive because `gamma < 1`. -/
theorem supnorm_nonexpansive_one_step
    (B : GraphSMDPBellman Value Opt) (V W : Value) :
    B.supDistance (B.T V) (B.T W) ≤ B.supDistance V W := by
  have hNumLeDen : B.gammaNum ≤ B.gammaDen := Nat.le_of_lt B.gammaLtOne
  have hRight : B.gammaNum * B.supDistance V W ≤
      B.gammaDen * B.supDistance V W :=
    Nat.mul_le_mul_right (B.supDistance V W) hNumLeDen
  have hScaled : B.gammaDen * B.supDistance (B.T V) (B.T W) ≤
      B.gammaDen * B.supDistance V W :=
    Nat.le_trans (B.bellman_contracts V W) hRight
  have hDenPos : 0 < B.gammaDen :=
    Nat.lt_of_le_of_lt (Nat.zero_le B.gammaNum) B.gammaLtOne
  exact Nat.le_of_mul_le_mul_left hScaled hDenPos

/-- Repeated graph-SMDP Bellman planning remains non-expansive in sup norm. -/
theorem supnorm_nonexpansive_iterate
    (B : GraphSMDPBellman Value Opt) :
    ∀ n V W,
      B.supDistance (iterate B.T n V) (iterate B.T n W) ≤ B.supDistance V W :=
  nonexpansive_iterate (B.supnorm_nonexpansive_one_step)

end GraphSMDPBellman

end RDBoundaryGreen
