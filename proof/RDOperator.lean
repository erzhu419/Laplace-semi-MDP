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
4. a Bellman-style graph solver needs a contraction/non-expansion hypothesis to
   make repeated planning stable.

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

end RDBoundaryGreen
