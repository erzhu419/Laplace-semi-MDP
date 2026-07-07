import Std

/-!
# Adaptive feasible top-k wrapper

This file formalizes the small solver-wrapper theorem used by the adaptive
top-k discovery backend.  The theorem is deliberately finite and independent of
the Green-kernel layer:

* a fixed top-`K` feasible envelope succeeds iff some candidate in the shared
  prefix is feasible;
* an adaptive feasible top-k run with the same candidate order and feasibility
  oracle has the same feasible envelope;
* adaptive refinement work is bounded by `K`;
* feasible-only stopping does not imply score optimality unless a score
  interval dominance certificate is also supplied.
-/

namespace RDBoundaryGreen
namespace AdaptiveTopK

/-- Fixed top-`K` feasible envelope over an already ordered candidate prefix. -/
def FixedTopKFeasible (K : Nat) (F : Nat -> Prop) : Prop :=
  ∃ j, j < K ∧ F j

/--
Certificate emitted by an implementation of adaptive feasible top-k.

The implementation details live in Python; Lean records the semantic contract:
same prefix/order, same feasibility oracle, and a refinement counter that never
exceeds the cap.
-/
structure AdaptiveFeasibleTopKRun (K : Nat) (F : Nat -> Prop) where
  kUsed : Nat
  kUsed_le_cap : kUsed ≤ K
  success : Prop
  success_iff_fixed_envelope : success ↔ FixedTopKFeasible K F
  first_feasible_work :
    success -> ∃ j, j < K ∧ F j ∧ kUsed = j + 1 ∧ ∀ i, i < j -> ¬ F i
  cap_work_on_failure : ¬ success -> kUsed = K

/-- Adaptive feasible top-k and fixed top-`K` have the same feasible envelope. -/
theorem adaptive_feasible_envelope_equivalence
    {K : Nat} {F : Nat -> Prop} (run : AdaptiveFeasibleTopKRun K F) :
    run.success ↔ FixedTopKFeasible K F :=
  run.success_iff_fixed_envelope

/-- Adaptive top-k never refines more candidates than fixed top-`K`. -/
theorem adaptive_refinement_work_bound
    {K : Nat} {F : Nat -> Prop} (run : AdaptiveFeasibleTopKRun K F) :
    run.kUsed ≤ K :=
  run.kUsed_le_cap

/-- On success, the adaptive work count is the first feasible rank plus one. -/
theorem adaptive_refinement_count_at_first_feasible
    {K : Nat} {F : Nat -> Prop} (run : AdaptiveFeasibleTopKRun K F)
    (h : run.success) :
    ∃ j, j < K ∧ F j ∧ run.kUsed = j + 1 ∧ ∀ i, i < j -> ¬ F i :=
  run.first_feasible_work h

/-- On failure, adaptive top-k has exhausted its cap. -/
theorem adaptive_refinement_count_on_failure
    {K : Nat} {F : Nat -> Prop} (run : AdaptiveFeasibleTopKRun K F)
    (h : ¬ run.success) :
    run.kUsed = K :=
  run.cap_work_on_failure h

/-- Score interval for candidates inside a fixed top-`K` prefix. -/
structure ScoreInterval (X : Type) where
  lower : X -> Int
  upper : X -> Int

/--
Interval dominance certifies the best feasible score inside the considered
candidate prefix.  This is the theorem needed for a stronger score-certified
mode; feasible-only stopping does not supply `hDominates`.
-/
theorem score_interval_dominance_certifies_best_feasible
    {X : Type} {candidate feasible : X -> Prop} {score : X -> Int}
    (I : ScoreInterval X) (selected : X)
    (hLower : ∀ x, I.lower x ≤ score x)
    (hUpper : ∀ x, score x ≤ I.upper x)
    (hDominates :
      ∀ y, candidate y -> feasible y -> y ≠ selected -> I.upper y ≤ I.lower selected)
    {y : X} (hyCandidate : candidate y) (hyFeasible : feasible y) :
    score y ≤ score selected := by
  by_cases hSame : y = selected
  · subst hSame
    omega
  · have h1 : score y ≤ I.upper y := hUpper y
    have h2 : I.upper y ≤ I.lower selected := hDominates y hyCandidate hyFeasible hSame
    have h3 : I.lower selected ≤ score selected := hLower selected
    omega

/--
Concrete counterexample: feasibility of the stopped candidate alone does not
imply score optimality among feasible candidates.
-/
theorem feasible_only_counterexample :
    ∃ (F : Nat -> Prop) (score : Nat -> Int) (selected other : Nat),
      F selected ∧ F other ∧ score selected < score other := by
  refine ⟨(fun _ => True), (fun n => if n = 0 then (0 : Int) else 1), 0, 1, ?_⟩
  constructor
  · trivial
  constructor
  · trivial
  · simp

end AdaptiveTopK
end RDBoundaryGreen
