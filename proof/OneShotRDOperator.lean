import Mathlib

/-!
# One-shot RD Green operator certificates

The production one-shot backend freezes its candidate universe, probe policies,
Green responses, channel weights, and threshold. It then applies one finite
linear response and selects local maxima without candidate insertion or
recomputation. This file records the proof obligations specific to that path:

* entrywise Green-response error controls every frozen linear channel;
* a threshold decision is stable outside its certified error interval;
* a strict local maximum is stable when its margin exceeds twice the score
  error.

These are certificates for a returned one-shot graph, not a claim that the
heuristic threshold globally optimizes the combinatorial RD objective.
-/

open BigOperators

noncomputable section

namespace RDBoundaryGreen.OneShot

/-- A frozen channel is one finite linear response of the Green feature bank. -/
def linearScore {Probe Candidate : Type} [Fintype Probe]
    (response : Candidate -> Probe -> ℝ) (weight : Probe -> ℝ)
    (x : Candidate) : ℝ :=
  ∑ probe : Probe, weight probe * response x probe

/-- Entrywise response intervals induce an absolute interval for a frozen channel. -/
theorem linearScore_error_le
    {Probe Candidate : Type} [Fintype Probe]
    (exact approx : Candidate -> Probe -> ℝ) (weight epsilon : Probe -> ℝ)
    (x : Candidate)
    (hEntry : ∀ probe, |approx x probe - exact x probe| ≤ epsilon probe) :
    |linearScore approx weight x - linearScore exact weight x| ≤
      ∑ probe : Probe, |weight probe| * epsilon probe := by
  unfold linearScore
  rw [← Finset.sum_sub_distrib]
  calc
    |∑ probe : Probe,
        (weight probe * approx x probe - weight probe * exact x probe)|
        ≤ ∑ probe : Probe,
            |weight probe * approx x probe - weight probe * exact x probe| :=
      Finset.abs_sum_le_sum_abs _ _
    _ = ∑ probe : Probe,
          |weight probe| * |approx x probe - exact x probe| := by
      apply Finset.sum_congr rfl
      intro probe _hprobe
      rw [← mul_sub, abs_mul]
    _ ≤ ∑ probe : Probe, |weight probe| * epsilon probe := by
      apply Finset.sum_le_sum
      intro probe _hprobe
      exact mul_le_mul_of_nonneg_left (hEntry probe) (abs_nonneg (weight probe))

/-- A score certified above `threshold + epsilon` remains selected after approximation. -/
theorem above_threshold_stable
    {exact approx threshold epsilon : ℝ}
    (hError : |approx - exact| ≤ epsilon)
    (hMargin : threshold + epsilon < exact) :
    threshold < approx := by
  have hLower : -epsilon ≤ approx - exact := (abs_le.mp hError).1
  linarith

/-- A score certified below `threshold - epsilon` remains rejected after approximation. -/
theorem below_threshold_stable
    {exact approx threshold epsilon : ℝ}
    (hError : |approx - exact| ≤ epsilon)
    (hMargin : exact < threshold - epsilon) :
    approx < threshold := by
  have hUpper : approx - exact ≤ epsilon := (abs_le.mp hError).2
  linarith

/-- A local-maximum margin larger than `2 epsilon` survives uniform score error. -/
theorem local_maximum_stable
    {exactX exactY approxX approxY epsilon : ℝ}
    (hErrorX : |approxX - exactX| ≤ epsilon)
    (hErrorY : |approxY - exactY| ≤ epsilon)
    (hMargin : exactY + 2 * epsilon < exactX) :
    approxY < approxX := by
  have hXLower : -epsilon ≤ approxX - exactX := (abs_le.mp hErrorX).1
  have hYUpper : approxY - exactY ≤ epsilon := (abs_le.mp hErrorY).2
  linarith

/-- Frozen threshold-plus-local-maximum selector used by the theorem layer. -/
def selected
    {Candidate : Type}
    (eligible : Candidate -> Prop)
    (adjacent : Candidate -> Candidate -> Prop)
    (score : Candidate -> ℝ) (threshold : ℝ)
    (x : Candidate) : Prop :=
  eligible x ∧ threshold ≤ score x ∧
    ∀ y, eligible y -> adjacent x y -> score y ≤ score x

/-- The one-shot selector performs one frozen predicate evaluation by definition. -/
theorem selected_iff_frozen_predicate
    {Candidate : Type}
    (eligible : Candidate -> Prop)
    (adjacent : Candidate -> Candidate -> Prop)
    (score : Candidate -> ℝ) (threshold : ℝ)
    (x : Candidate) :
    selected eligible adjacent score threshold x ↔
      eligible x ∧ threshold ≤ score x ∧
        ∀ y, eligible y -> adjacent x y -> score y ≤ score x :=
  Iff.rfl

end RDBoundaryGreen.OneShot
