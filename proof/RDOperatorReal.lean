import Mathlib

/-!
# RD Boundary Green Operator: Mathlib real layer

This file instantiates the paper-facing proof obligations over real-valued
finite matrices and finite option sets.  `RDOperator.lean` keeps a lightweight
Std-only finite/scaled core; this file is the heavier Mathlib layer that uses
`Real`, `Matrix`, finite sums, derivatives of `Real.log`, and finite-action
max backups.
-/

set_option linter.unusedSectionVars false

open BigOperators Matrix

noncomputable section

namespace RDBoundaryGreen.RealProof

/-!
## First-hit Green kernel as a real finite-matrix formula

For an interior transition block `Pii` and an interior-to-boundary block `Pic`,
the Green/harmonic first-hit kernel is represented by

`(I - Pii)^{-1} Pic`.

The theorem `green_formula_solves_linear_system` proves that this matrix is the
solution of the absorbing-chain linear system whenever `I - Pii` has nonzero
determinant.  Non-negativity and row-mass bounds are then stated and proved as
ordinary real finite-sum consequences.
-/

/-- Real first-hit Green matrix `K = (I - Pii)^{-1} Pic`. -/
def GreenFormula {I C : Type} [Fintype I] [DecidableEq I]
    (Pii : Matrix I I ℝ) (Pic : Matrix I C ℝ) : Matrix I C ℝ :=
  (1 - Pii)⁻¹ * Pic

/-- Neumann/truncated Green prefix `sum_{t=0}^K Pii^t Pic`. -/
def NeumannPrefix {I C : Type} [Fintype I] [DecidableEq I]
    (Pii : Matrix I I ℝ) (Pic : Matrix I C ℝ) (K : Nat) : Matrix I C ℝ :=
  ∑ t ∈ Finset.range (K + 1), (Pii ^ t) * Pic

/-- Row mass of a finite boundary-kernel row. -/
def rowMass {I C : Type} [Fintype C] (K : Matrix I C ℝ) (i : I) : ℝ :=
  ∑ c : C, K i c

/-- Weighted row mass for a positive-vector/spectral-radius certificate. -/
def weightedRowMass {I J : Type} [Fintype J]
    (K : Matrix I J ℝ) (w : J -> ℝ) (i : I) : ℝ :=
  ∑ j : J, K i j * w j

/-- Finite Neumann tail window `sum_{t=K+1}^{N-1} Pii^t Pic`. -/
def NeumannTailIco {I C : Type} [Fintype I] [DecidableEq I]
    (Pii : Matrix I I ℝ) (Pic : Matrix I C ℝ) (K N : Nat) : Matrix I C ℝ :=
  ∑ t ∈ Finset.Ico (K + 1) N, (Pii ^ t) * Pic

/-- The Green formula solves `(I - Pii) K = Pic` when the inverse is legal. -/
theorem green_formula_solves_linear_system
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I]
    (Pii : Matrix I I ℝ) (Pic : Matrix I C ℝ)
    (hDet : IsUnit ((1 - Pii).det)) :
    (1 - Pii) * GreenFormula Pii Pic = Pic := by
  unfold GreenFormula
  rw [← Matrix.mul_assoc]
  rw [Matrix.mul_nonsing_inv (1 - Pii) hDet]
  simp

/-- Nonnegative inverse and boundary block imply nonnegative Green entries. -/
theorem green_formula_entry_nonnegative
    {I C : Type} [Fintype I] [DecidableEq I]
    (Pii : Matrix I I ℝ) (Pic : Matrix I C ℝ)
    (hInvNonneg : ∀ i j, 0 ≤ ((1 - Pii)⁻¹) i j)
    (hPicNonneg : ∀ i c, 0 ≤ Pic i c)
    (i : I) (c : C) :
    0 ≤ GreenFormula Pii Pic i c := by
  unfold GreenFormula
  rw [Matrix.mul_apply]
  exact Finset.sum_nonneg (by
    intro j _hj
    exact mul_nonneg (hInvNonneg i j) (hPicNonneg j c))

/-- A nonnegative entry is bounded by its finite row mass. -/
theorem green_entry_le_rowMass
    {I C : Type} [Fintype C] [DecidableEq C]
    (K : Matrix I C ℝ) (i : I)
    (hNonneg : ∀ c, 0 ≤ K i c) (c : C) :
    K i c ≤ rowMass K i := by
  unfold rowMass
  exact Finset.single_le_sum (by
    intro b _hb
    exact hNonneg b) (Finset.mem_univ c)

/-- Row-mass bound gives the usual `<= 1` absorbing-kernel row guarantee. -/
theorem green_entry_le_rowBound
    {I C : Type} [Fintype C] [DecidableEq C]
    (K : Matrix I C ℝ) (rowBound : ℝ) (i : I)
    (hNonneg : ∀ c, 0 ≤ K i c)
    (hRowBound : rowMass K i ≤ rowBound) (c : C) :
    K i c ≤ rowBound :=
  (green_entry_le_rowMass K i hNonneg c).trans hRowBound

/-- The identity matrix has row mass one. -/
theorem rowMass_one
    {I : Type} [Fintype I] [DecidableEq I] (i : I) :
    rowMass (1 : Matrix I I ℝ) i = 1 := by
  rw [rowMass]
  rw [Finset.sum_eq_single i]
  · simp
  · intro b _hb hbi
    simp [hbi.symm]
  · intro hi
    exact False.elim (hi (Finset.mem_univ i))

/-- Nonnegative square matrices have nonnegative powers. -/
theorem matrix_power_nonnegative
    {I : Type} [Fintype I] [DecidableEq I]
    (P : Matrix I I ℝ) (hPnonneg : ∀ i j, 0 ≤ P i j) :
    ∀ n i j, 0 ≤ (P ^ n) i j := by
  intro n
  induction n with
  | zero =>
      intro i j
      by_cases hij : i = j <;> simp [hij]
  | succ n ih =>
      intro i j
      rw [pow_succ]
      rw [Matrix.mul_apply]
      exact Finset.sum_nonneg (by
        intro k _hk
        exact mul_nonneg (ih i k) (hPnonneg k j))

/-- Rectangular row-mass multiplication bound. -/
theorem rowMass_mul_rect_le
    {I C : Type} [Fintype I] [Fintype C]
    (A : Matrix I I ℝ) (B : Matrix I C ℝ) (q : ℝ) (i : I)
    (hA : ∀ i k, 0 ≤ A i k)
    (hBrow : ∀ k, rowMass B k ≤ q) :
    rowMass (A * B) i ≤ rowMass A i * q := by
  unfold rowMass
  rw [show (∑ c : C, (A * B) i c) = ∑ k : I, A i k * ∑ c : C, B k c by
    simp [Matrix.mul_apply, Finset.mul_sum]
    rw [Finset.sum_comm]]
  calc
    (∑ k : I, A i k * ∑ c : C, B k c) ≤ ∑ k : I, A i k * q := by
      apply Finset.sum_le_sum
      intro k _hk
      exact mul_le_mul_of_nonneg_left (hBrow k) (hA i k)
    _ = (∑ k : I, A i k) * q := by
      rw [Finset.sum_mul]

/-- Square row-mass multiplication bound. -/
theorem rowMass_mul_square_le
    {I : Type} [Fintype I]
    (A B : Matrix I I ℝ) (q : ℝ) (i : I)
    (hA : ∀ i k, 0 ≤ A i k)
    (hBrow : ∀ k, rowMass B k ≤ q) :
    rowMass (A * B) i ≤ rowMass A i * q :=
  rowMass_mul_rect_le A B q i hA hBrow

/-- If every row of `P` has mass at most `q`, then row mass of `P^n` is at most `q^n`. -/
theorem substochastic_power_rowMass_bound
    {I : Type} [Fintype I] [DecidableEq I]
    (P : Matrix I I ℝ) (q : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hRow : ∀ i, rowMass P i ≤ q)
    (hqNonneg : 0 ≤ q) :
    ∀ n i, rowMass (P ^ n) i ≤ q ^ n := by
  intro n
  induction n with
  | zero =>
      intro i
      rw [pow_zero, rowMass_one]
      norm_num
  | succ n ih =>
      intro i
      calc
        rowMass (P ^ Nat.succ n) i = rowMass ((P ^ n) * P) i := by
          rw [pow_succ]
        _ ≤ rowMass (P ^ n) i * q := by
          exact rowMass_mul_square_le (P ^ n) P q i
            (matrix_power_nonnegative P hPnonneg n) hRow
        _ ≤ q ^ n * q := by
          exact mul_le_mul_of_nonneg_right (ih i) hqNonneg
        _ = q ^ Nat.succ n := by
          rw [pow_succ]

/-- Each Neumann term is geometrically bounded under a row-substochastic condition. -/
theorem neumann_term_entry_le_geometric
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I] [DecidableEq C]
    (P : Matrix I I ℝ) (Pic : Matrix I C ℝ) (q exitBound : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hProw : ∀ i, rowMass P i ≤ q)
    (hqNonneg : 0 ≤ q)
    (hPicNonneg : ∀ i c, 0 ≤ Pic i c)
    (hPicRow : ∀ i, rowMass Pic i ≤ exitBound)
    (hexitNonneg : 0 ≤ exitBound)
    (n : Nat) (i : I) (c : C) :
    ((P ^ n) * Pic) i c ≤ q ^ n * exitBound := by
  have hPowNonneg := matrix_power_nonnegative P hPnonneg n
  have hProductNonneg : ∀ c, 0 ≤ ((P ^ n) * Pic) i c := by
    intro c
    rw [Matrix.mul_apply]
    exact Finset.sum_nonneg (by
      intro k _hk
      exact mul_nonneg (hPowNonneg i k) (hPicNonneg k c))
  calc
    ((P ^ n) * Pic) i c ≤ rowMass ((P ^ n) * Pic) i := by
      unfold rowMass
      exact Finset.single_le_sum (by
        intro b _hb
        exact hProductNonneg b) (Finset.mem_univ c)
    _ ≤ rowMass (P ^ n) i * exitBound := by
      exact rowMass_mul_rect_le (P ^ n) Pic exitBound i hPowNonneg hPicRow
    _ ≤ q ^ n * exitBound := by
      exact mul_le_mul_of_nonneg_right
        (substochastic_power_rowMass_bound P q hPnonneg hProw hqNonneg n i)
        hexitNonneg

/-- Finite Neumann tails are bounded by the geometric tail `exitBound * q^(K+1)/(1-q)`. -/
theorem finite_neumann_tail_entry_le_geometric
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I] [DecidableEq C]
    (P : Matrix I I ℝ) (Pic : Matrix I C ℝ) (q exitBound : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hProw : ∀ i, rowMass P i ≤ q)
    (hqNonneg : 0 ≤ q)
    (hqLt : q < 1)
    (hPicNonneg : ∀ i c, 0 ≤ Pic i c)
    (hPicRow : ∀ i, rowMass Pic i ≤ exitBound)
    (hexitNonneg : 0 ≤ exitBound)
    (K N : Nat) (i : I) (c : C) :
    (NeumannTailIco P Pic K N) i c ≤
      exitBound * (q ^ (K + 1) / (1 - q)) := by
  unfold NeumannTailIco
  simp only [Matrix.sum_apply]
  calc
    (∑ x ∈ Finset.Ico (K + 1) N, ((P ^ x) * Pic) i c)
        ≤ ∑ x ∈ Finset.Ico (K + 1) N, q ^ x * exitBound := by
      apply Finset.sum_le_sum
      intro t _ht
      exact neumann_term_entry_le_geometric P Pic q exitBound hPnonneg hProw
        hqNonneg hPicNonneg hPicRow hexitNonneg t i c
    _ = (∑ x ∈ Finset.Ico (K + 1) N, q ^ x) * exitBound := by
      rw [Finset.sum_mul]
    _ ≤ (q ^ (K + 1) / (1 - q)) * exitBound := by
      exact mul_le_mul_of_nonneg_right
        (geom_sum_Ico_le_of_lt_one hqNonneg hqLt) hexitNonneg
    _ = exitBound * (q ^ (K + 1) / (1 - q)) := by
      ring

/-!
### Weighted spectral-radius certificate

The row-substochastic theorem above is the special case `w = 1`.  The next
block uses a positive weighted sup-norm / Collatz-Wielandt certificate

`P w <= q w`, with `q < 1`.

For nonnegative matrices this is a standard sufficient certificate for
spectral radius `< 1`, and is often less conservative than raw row sums.
-/

/-- Weighted row mass of the identity matrix is the source weight. -/
theorem weightedRowMass_one
    {I : Type} [Fintype I] [DecidableEq I] (w : I -> ℝ) (i : I) :
    weightedRowMass (1 : Matrix I I ℝ) w i = w i := by
  rw [weightedRowMass]
  rw [Finset.sum_eq_single i]
  · simp
  · intro b _hb hbi
    simp [hbi.symm]
  · intro hi
    exact False.elim (hi (Finset.mem_univ i))

/-- Weighted row-mass multiplication bound. -/
theorem weightedRowMass_mul_le
    {I C : Type} [Fintype I] [Fintype C]
    (A : Matrix I I ℝ) (B : Matrix I C ℝ)
    (wI : I -> ℝ) (wC : C -> ℝ) (q : ℝ) (i : I)
    (hA : ∀ i k, 0 ≤ A i k)
    (hB : ∀ k, weightedRowMass B wC k ≤ q * wI k) :
    weightedRowMass (A * B) wC i ≤ q * weightedRowMass A wI i := by
  unfold weightedRowMass
  rw [show (∑ c : C, (A * B) i c * wC c) =
      ∑ k : I, A i k * ∑ c : C, B k c * wC c by
    simp [Matrix.mul_apply, Finset.sum_mul, Finset.mul_sum, mul_assoc]
    rw [Finset.sum_comm]]
  calc
    (∑ k : I, A i k * ∑ c : C, B k c * wC c)
        ≤ ∑ k : I, A i k * (q * wI k) := by
      apply Finset.sum_le_sum
      intro k _hk
      exact mul_le_mul_of_nonneg_left (hB k) (hA i k)
    _ = q * (∑ k : I, A i k * wI k) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro k _hk
      ring

/-- A weighted spectral certificate `P w <= q w` propagates to `P^n w <= q^n w`. -/
theorem weighted_power_rowMass_bound
    {I : Type} [Fintype I] [DecidableEq I]
    (P : Matrix I I ℝ) (w : I -> ℝ) (q : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hWeightedRow : ∀ i, weightedRowMass P w i ≤ q * w i)
    (hqNonneg : 0 ≤ q) :
    ∀ n i, weightedRowMass (P ^ n) w i ≤ q ^ n * w i := by
  intro n
  induction n with
  | zero =>
      intro i
      rw [pow_zero, weightedRowMass_one]
      simp
  | succ n ih =>
      intro i
      calc
        weightedRowMass (P ^ Nat.succ n) w i =
            weightedRowMass ((P ^ n) * P) w i := by
          rw [pow_succ]
        _ ≤ q * weightedRowMass (P ^ n) w i := by
          exact weightedRowMass_mul_le (P ^ n) P w w q i
            (matrix_power_nonnegative P hPnonneg n) hWeightedRow
        _ ≤ q * (q ^ n * w i) := by
          exact mul_le_mul_of_nonneg_left (ih i) hqNonneg
        _ = q ^ Nat.succ n * w i := by
          rw [pow_succ]
          ring

/-- Weighted spectral certificate bounds each Neumann term. -/
theorem spectral_certificate_neumann_term_entry_le
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I]
    (P : Matrix I I ℝ) (Pic : Matrix I C ℝ) (w : I -> ℝ) (q exitBound : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hWeightedRow : ∀ i, weightedRowMass P w i ≤ q * w i)
    (hqNonneg : 0 ≤ q)
    (hPicEntry : ∀ i c, Pic i c ≤ exitBound * w i)
    (hexitNonneg : 0 ≤ exitBound)
    (n : Nat) (i : I) (c : C) :
    ((P ^ n) * Pic) i c ≤ q ^ n * (exitBound * w i) := by
  have hPowNonneg := matrix_power_nonnegative P hPnonneg n
  rw [Matrix.mul_apply]
  calc
    (∑ k : I, (P ^ n) i k * Pic k c)
        ≤ ∑ k : I, (P ^ n) i k * (exitBound * w k) := by
      apply Finset.sum_le_sum
      intro k _hk
      exact mul_le_mul_of_nonneg_left (hPicEntry k c) (hPowNonneg i k)
    _ = exitBound * weightedRowMass (P ^ n) w i := by
      unfold weightedRowMass
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro k _hk
      ring
    _ ≤ exitBound * (q ^ n * w i) := by
      exact mul_le_mul_of_nonneg_left
        (weighted_power_rowMass_bound P w q hPnonneg hWeightedRow hqNonneg n i)
        hexitNonneg
    _ = q ^ n * (exitBound * w i) := by
      ring

/-- Weighted spectral certificate gives a geometric finite-tail bound. -/
theorem spectral_certificate_finite_neumann_tail_entry_le
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I]
    (P : Matrix I I ℝ) (Pic : Matrix I C ℝ) (w : I -> ℝ) (q exitBound : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hWeightedRow : ∀ i, weightedRowMass P w i ≤ q * w i)
    (hqNonneg : 0 ≤ q)
    (hqLt : q < 1)
    (hPicEntry : ∀ i c, Pic i c ≤ exitBound * w i)
    (hexitNonneg : 0 ≤ exitBound)
    (hWNonneg : ∀ i, 0 ≤ w i)
    (K N : Nat) (i : I) (c : C) :
    (NeumannTailIco P Pic K N) i c ≤
      exitBound * w i * (q ^ (K + 1) / (1 - q)) := by
  unfold NeumannTailIco
  simp only [Matrix.sum_apply]
  have hScaleNonneg : 0 ≤ exitBound * w i := mul_nonneg hexitNonneg (hWNonneg i)
  calc
    (∑ x ∈ Finset.Ico (K + 1) N, ((P ^ x) * Pic) i c)
        ≤ ∑ x ∈ Finset.Ico (K + 1) N, q ^ x * (exitBound * w i) := by
      apply Finset.sum_le_sum
      intro t _ht
      exact spectral_certificate_neumann_term_entry_le P Pic w q exitBound
        hPnonneg hWeightedRow hqNonneg hPicEntry hexitNonneg t i c
    _ = (∑ x ∈ Finset.Ico (K + 1) N, q ^ x) * (exitBound * w i) := by
      rw [Finset.sum_mul]
    _ ≤ (q ^ (K + 1) / (1 - q)) * (exitBound * w i) := by
      exact mul_le_mul_of_nonneg_right
        (geom_sum_Ico_le_of_lt_one hqNonneg hqLt) hScaleNonneg
    _ = exitBound * w i * (q ^ (K + 1) / (1 - q)) := by
      ring

/-!
The preceding theorem handles nonnegative boundary blocks.  For a genuinely
weighted operator-norm certificate we also need the signed version: arbitrary
real downstream rewards/features may be propagated through the same
nonnegative transition kernel, and the weighted sup-norm controls the absolute
tail.
-/

/-- A signed Neumann term is bounded in weighted sup-norm form. -/
theorem spectral_certificate_signed_neumann_term_entry_abs_le
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I]
    (P : Matrix I I ℝ) (B : Matrix I C ℝ) (w : I -> ℝ) (q coeffBound : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hWeightedRow : ∀ i, weightedRowMass P w i ≤ q * w i)
    (hqNonneg : 0 ≤ q)
    (hBEntry : ∀ i c, |B i c| ≤ coeffBound * w i)
    (hCoeffNonneg : 0 ≤ coeffBound)
    (n : Nat) (i : I) (c : C) :
    |((P ^ n) * B) i c| ≤ q ^ n * (coeffBound * w i) := by
  have hPowNonneg := matrix_power_nonnegative P hPnonneg n
  rw [Matrix.mul_apply]
  calc
    |∑ k : I, (P ^ n) i k * B k c|
        ≤ ∑ k : I, |(P ^ n) i k * B k c| := by
          exact Finset.abs_sum_le_sum_abs _ _
    _ = ∑ k : I, (P ^ n) i k * |B k c| := by
          apply Finset.sum_congr rfl
          intro k _hk
          rw [abs_mul, abs_of_nonneg (hPowNonneg i k)]
    _ ≤ ∑ k : I, (P ^ n) i k * (coeffBound * w k) := by
          apply Finset.sum_le_sum
          intro k _hk
          exact mul_le_mul_of_nonneg_left (hBEntry k c) (hPowNonneg i k)
    _ = coeffBound * weightedRowMass (P ^ n) w i := by
          unfold weightedRowMass
          rw [Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro k _hk
          ring
    _ ≤ coeffBound * (q ^ n * w i) := by
          exact mul_le_mul_of_nonneg_left
            (weighted_power_rowMass_bound P w q hPnonneg hWeightedRow hqNonneg n i)
            hCoeffNonneg
    _ = q ^ n * (coeffBound * w i) := by
          ring

/-- Weighted spectral certificate gives an absolute finite-tail bound for signed blocks. -/
theorem spectral_certificate_signed_finite_neumann_tail_entry_abs_le
    {I C : Type} [Fintype I] [Fintype C] [DecidableEq I]
    (P : Matrix I I ℝ) (B : Matrix I C ℝ) (w : I -> ℝ) (q coeffBound : ℝ)
    (hPnonneg : ∀ i j, 0 ≤ P i j)
    (hWeightedRow : ∀ i, weightedRowMass P w i ≤ q * w i)
    (hqNonneg : 0 ≤ q)
    (hqLt : q < 1)
    (hBEntry : ∀ i c, |B i c| ≤ coeffBound * w i)
    (hCoeffNonneg : 0 ≤ coeffBound)
    (hWNonneg : ∀ i, 0 ≤ w i)
    (K N : Nat) (i : I) (c : C) :
    |(NeumannTailIco P B K N) i c| ≤
      coeffBound * w i * (q ^ (K + 1) / (1 - q)) := by
  unfold NeumannTailIco
  simp only [Matrix.sum_apply]
  have hScaleNonneg : 0 ≤ coeffBound * w i := mul_nonneg hCoeffNonneg (hWNonneg i)
  calc
    |∑ x ∈ Finset.Ico (K + 1) N, ((P ^ x) * B) i c|
        ≤ ∑ x ∈ Finset.Ico (K + 1) N, |((P ^ x) * B) i c| := by
          exact Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ x ∈ Finset.Ico (K + 1) N, q ^ x * (coeffBound * w i) := by
          apply Finset.sum_le_sum
          intro t _ht
          exact spectral_certificate_signed_neumann_term_entry_abs_le P B w q coeffBound
            hPnonneg hWeightedRow hqNonneg hBEntry hCoeffNonneg t i c
    _ = (∑ x ∈ Finset.Ico (K + 1) N, q ^ x) * (coeffBound * w i) := by
          rw [Finset.sum_mul]
    _ ≤ (q ^ (K + 1) / (1 - q)) * (coeffBound * w i) := by
          exact mul_le_mul_of_nonneg_right
            (geom_sum_Ico_le_of_lt_one hqNonneg hqLt) hScaleNonneg
    _ = coeffBound * w i * (q ^ (K + 1) / (1 - q)) := by
          ring

/-!
## Weighted downstream score certificates

These lemmas connect kernel approximation errors to RD scores.  They are the
formal version of the paper sentence: for any fixed nonnegative downstream
weights, an entrywise/spectral Green-tail certificate induces a finite score
interval, and separated intervals certify that the adaptive implementation
preserves the exact top choice.
-/

/-- A fixed weighted downstream score over edge/features. -/
def WeightedScore {E X : Type} [Fintype E]
    (a : E -> ℝ) (K : E -> X -> ℝ) (x : X) : ℝ :=
  ∑ e : E, a e * K e x

/-- Weighted sum of per-entry kernel error bounds. -/
def WeightedErrorBound {E X : Type} [Fintype E]
    (a : E -> ℝ) (T : E -> X -> ℝ) (x : X) : ℝ :=
  ∑ e : E, a e * T e x

/-- Entrywise Green-tail bounds imply a weighted downstream score interval. -/
theorem weightedScore_error_le
    {E X : Type} [Fintype E]
    (a : E -> ℝ) (K Khat T : E -> X -> ℝ) (x : X)
    (hWeightNonneg : ∀ e, 0 ≤ a e)
    (hEntry : ∀ e, |K e x - Khat e x| ≤ T e x) :
    |WeightedScore a K x - WeightedScore a Khat x| ≤
      WeightedErrorBound a T x := by
  unfold WeightedScore WeightedErrorBound
  have hdiff :
      (∑ e : E, a e * K e x) - (∑ e : E, a e * Khat e x) =
        ∑ e : E, a e * (K e x - Khat e x) := by
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro e _he
    ring
  rw [hdiff]
  calc
    |∑ e : E, a e * (K e x - Khat e x)|
        ≤ ∑ e : E, |a e * (K e x - Khat e x)| := by
          exact Finset.abs_sum_le_sum_abs _ _
    _ = ∑ e : E, a e * |K e x - Khat e x| := by
          apply Finset.sum_congr rfl
          intro e _he
          rw [abs_mul, abs_of_nonneg (hWeightNonneg e)]
    _ ≤ ∑ e : E, a e * T e x := by
          apply Finset.sum_le_sum
          intro e _he
          exact mul_le_mul_of_nonneg_left (hEntry e) (hWeightNonneg e)

/-- Separated score intervals certify that the approximate top choice is exact. -/
theorem interval_certified_top_choice
    {X : Type} {exact approx err : X -> ℝ} {xBest xRunner y : X}
    (hRunner :
      ∀ z, z ≠ xBest -> approx z + err z ≤ approx xRunner + err xRunner)
    (hSeparated : approx xRunner + err xRunner < approx xBest - err xBest)
    (hErr : ∀ z, |exact z - approx z| ≤ err z)
    (hy : y ≠ xBest) :
    exact y < exact xBest := by
  have hyUpper : exact y ≤ approx y + err y := by
    have h := (abs_sub_le_iff.mp (hErr y)).1
    linarith
  have hbestLower : approx xBest - err xBest ≤ exact xBest := by
    have h := (abs_sub_le_iff.mp (hErr xBest)).2
    linarith
  have hyRunner := hRunner y hy
  linarith

/-- If interval bounds show that no candidate can beat `x` by more than `eps`, `x` is
epsilon-optimal for the exact score. -/
theorem epsilon_interval_certified_optimality
    {X : Type} {exact lower upper : X -> ℝ} {x y : X} {eps : ℝ}
    (hxLower : lower x ≤ exact x)
    (hyUpper : exact y ≤ upper y)
    (hGap : upper y - lower x ≤ eps) :
    exact y - exact x ≤ eps := by
  linarith

/-- Any representative of an exact top tie set is globally optimal if all states in
the set tie with it and all outside states are no better. -/
theorem exact_tie_set_representative_optimal
    {X : Type} {exact : X -> ℝ} {inTie : X -> Prop} {x y : X}
    (hTie : ∀ z, inTie z -> exact z = exact x)
    (hOutside : ∀ z, ¬ inTie z -> exact z ≤ exact x) :
    exact y ≤ exact x := by
  by_cases hy : inTie y
  · exact le_of_eq (hTie y hy)
  · exact hOutside y hy

/-- Exact evaluation on an ambiguous top set certifies global optimality if it beats all outside upper bounds. -/
theorem top_set_exact_fallback_global_optimal
    {X : Type} {exact upper : X -> ℝ} {inAmbiguous : X -> Prop} {xBest y : X}
    (hBestAmbiguous : ∀ z, inAmbiguous z -> exact z ≤ exact xBest)
    (hOutsideUpper : ∀ z, ¬ inAmbiguous z -> exact z ≤ upper z)
    (hBeatsOutside : ∀ z, ¬ inAmbiguous z -> upper z < exact xBest) :
    exact y ≤ exact xBest := by
  by_cases hy : inAmbiguous y
  · exact hBestAmbiguous y hy
  · exact le_of_lt ((hOutsideUpper y hy).trans_lt (hBeatsOutside y hy))

/-- Outside the ambiguous set, the exact fallback winner is strictly better. -/
theorem top_set_exact_fallback_beats_outside
    {X : Type} {exact upper : X -> ℝ} {inAmbiguous : X -> Prop} {xBest y : X}
    (hOutsideUpper : ∀ z, ¬ inAmbiguous z -> exact z ≤ upper z)
    (hBeatsOutside : ∀ z, ¬ inAmbiguous z -> upper z < exact xBest)
    (hy : ¬ inAmbiguous y) :
    exact y < exact xBest :=
  (hOutsideUpper y hy).trans_lt (hBeatsOutside y hy)

/-!
## Truncated Green / Neumann convergence

The exact analytic fact needed by the paper is: if the Neumann tail is bounded
by a quantity that goes to zero, then the finite prefix converges to the Green
kernel entrywise.  The spectral-radius/substochastic proof can instantiate the
`tailBound` field below.
-/

/-- Real truncated-Green convergence certificate. -/
structure RealTruncatedGreen {I C : Type} [Fintype I] [DecidableEq I] where
  Pii : Matrix I I ℝ
  Pic : Matrix I C ℝ
  exact : Matrix I C ℝ
  truncated : Nat -> Matrix I C ℝ
  tail : Nat -> Matrix I C ℝ
  tailBound : Nat -> ℝ
  exact_eq_green : exact = GreenFormula Pii Pic
  truncated_eq_neumann : ∀ K, truncated K = NeumannPrefix Pii Pic K
  decompose : ∀ K i c, exact i c = truncated K i c + tail K i c
  tail_abs_le : ∀ K i c, |tail K i c| ≤ tailBound K
  eventually_below : ∀ eps, 0 < eps -> ∃ K, tailBound K ≤ eps

namespace RealTruncatedGreen

/-- Entrywise truncated-Green error is bounded by the supplied tail bound. -/
theorem error_le_tailBound
    {I C : Type} [Fintype I] [DecidableEq I]
    (G : RealTruncatedGreen (I := I) (C := C))
    (K : Nat) (i : I) (c : C) :
    |G.exact i c - G.truncated K i c| ≤ G.tailBound K := by
  have hdiff : G.exact i c - G.truncated K i c = G.tail K i c := by
    rw [G.decompose K i c]
    ring
  rw [hdiff]
  exact G.tail_abs_le K i c

/-- If the Neumann tail bound eventually falls below every epsilon, prefixes converge. -/
theorem neumann_prefix_converges_epsilon
    {I C : Type} [Fintype I] [DecidableEq I]
    (G : RealTruncatedGreen (I := I) (C := C)) :
    ∀ eps, 0 < eps -> ∀ i c, ∃ K,
      |G.exact i c - G.truncated K i c| ≤ eps := by
  intro eps heps i c
  rcases G.eventually_below eps heps with ⟨K, hK⟩
  refine ⟨K, ?_⟩
  exact (G.error_le_tailBound K i c).trans hK

end RealTruncatedGreen

/-!
## Bits distortion over real numbers

The paper uses

`phi(h) = -log_2(1 - h + eps)`.

We write it as a natural-log expression divided by `log 2`, then prove the real
derivative by Mathlib's `Real.hasDerivAt_log`.  A Taylor certificate records the
finite-difference remainder bound used by the operator approximation.
-/

/-- Bits distortion, written with natural logarithms. -/
def bitsPhi (eps h : ℝ) : ℝ :=
  - Real.log (1 - h + eps) / Real.log 2

/-- First derivative of `bitsPhi`. -/
def bitsPhiDeriv (eps h : ℝ) : ℝ :=
  (1 - h + eps)⁻¹ / Real.log 2

/-- Second derivative / curvature of `bitsPhi`. -/
def bitsPhiSecond (eps h : ℝ) : ℝ :=
  ((1 - h + eps)⁻¹ * (1 - h + eps)⁻¹) / Real.log 2

/-- Real derivative of `phi(h) = -log_2(1 - h + eps)`. -/
theorem bitsPhi_hasDerivAt
    (eps h : ℝ) (hNonzero : 1 - h + eps ≠ 0) :
    HasDerivAt (fun x => bitsPhi eps x)
      (bitsPhiDeriv eps h) h := by
  unfold bitsPhi
  have hinner : HasDerivAt (fun x : ℝ => 1 - x + eps) (-1) h := by
    simpa using (((hasDerivAt_id h).const_sub 1).add_const eps)
  have hlog0 :
      HasDerivAt (fun x : ℝ => Real.log (1 - x + eps))
        ((1 - h + eps)⁻¹ * (-1)) h := by
    exact (Real.hasDerivAt_log hNonzero).comp h hinner
  have hlog :
      HasDerivAt (fun x : ℝ => Real.log (1 - x + eps))
        (-(1 - h + eps)⁻¹) h := by
    convert hlog0 using 1
    ring
  have hneg0 := hlog.neg
  have hfun :
      (fun x : ℝ => - Real.log (1 - x + eps)) =
        (- fun x : ℝ => Real.log (1 - x + eps)) := by
    rfl
  have hderiv : (1 - h + eps)⁻¹ = - (-(1 - h + eps)⁻¹) := by
    ring
  have hneg :
      HasDerivAt (fun x : ℝ => - Real.log (1 - x + eps))
        ((1 - h + eps)⁻¹) h := by
    rw [hfun, hderiv]
    exact hneg0
  simpa [bitsPhiDeriv] using hneg.div_const (Real.log 2)

/-- Real derivative of the first derivative of `bitsPhi`. -/
theorem bitsPhiDeriv_hasDerivAt
    (eps h : ℝ) (hNonzero : 1 - h + eps ≠ 0) :
    HasDerivAt (fun x => bitsPhiDeriv eps x)
      (bitsPhiSecond eps h) h := by
  unfold bitsPhiDeriv bitsPhiSecond
  have hinner : HasDerivAt (fun x : ℝ => 1 - x + eps) (-1) h := by
    simpa using (((hasDerivAt_id h).const_sub 1).add_const eps)
  have hinv0 :
      HasDerivAt (fun x : ℝ => (1 - x + eps)⁻¹)
        (-(-1) / (1 - h + eps) ^ 2) h := by
    exact hinner.inv hNonzero
  have hinv :
      HasDerivAt (fun x : ℝ => (1 - x + eps)⁻¹)
        ((1 - h + eps)⁻¹ * (1 - h + eps)⁻¹) h := by
    convert hinv0 using 1
    field_simp [hNonzero]
  simpa using hinv.div_const (Real.log 2)

/-- `bitsPhi` is locally twice continuously differentiable away from its singularity. -/
theorem bitsPhi_contDiffAt
    (eps y : ℝ) (hyNonzero : 1 - y + eps ≠ 0) :
    ContDiffAt ℝ 2 (fun x => bitsPhi eps x) y := by
  unfold bitsPhi
  fun_prop (disch := exact hyNonzero)

/-- Near a nonsingular point, the derivative of `bitsPhi` equals `bitsPhiDeriv`. -/
theorem bitsPhi_deriv_eq_eventually
    (eps y : ℝ) (hyNonzero : 1 - y + eps ≠ 0) :
    (deriv (fun z => bitsPhi eps z)) =ᶠ[nhds y]
      (fun z => bitsPhiDeriv eps z) := by
  have hcont : ContinuousAt (fun z : ℝ => 1 - z + eps) y := by
    fun_prop
  have hEv : ∀ᶠ z in nhds y, 1 - z + eps ≠ 0 :=
    hcont.eventually_ne hyNonzero
  filter_upwards [hEv] with z hz
  exact (bitsPhi_hasDerivAt eps z hz).deriv

/-- Global second iterated derivative at a nonsingular point. -/
theorem bitsPhi_iteratedDeriv_two_eq
    (eps y : ℝ) (hyNonzero : 1 - y + eps ≠ 0) :
    iteratedDeriv 2 (fun z => bitsPhi eps z) y = bitsPhiSecond eps y := by
  rw [show (2 : Nat) = 1 + 1 by norm_num, iteratedDeriv_succ, iteratedDeriv_one]
  have hEv := bitsPhi_deriv_eq_eventually eps y hyNonzero
  rw [hEv.deriv_eq]
  exact (bitsPhiDeriv_hasDerivAt eps y hyNonzero).deriv

/-- Closed-interval `iteratedDerivWithin` glue for the bits curvature. -/
theorem bitsPhi_iteratedDerivWithin_two_eq
    (eps a b y : ℝ) (hab : a < b)
    (hy : y ∈ Set.Icc a b) (hyNonzero : 1 - y + eps ≠ 0) :
    iteratedDerivWithin 2 (fun z => bitsPhi eps z) (Set.Icc a b) y =
      bitsPhiSecond eps y := by
  rw [iteratedDerivWithin_eq_iteratedDeriv (uniqueDiffOn_Icc hab)
    (bitsPhi_contDiffAt eps y hyNonzero) hy]
  exact bitsPhi_iteratedDeriv_two_eq eps y hyNonzero

/-- Lower-bounding `1 - h + eps` bounds the bits-distortion curvature. -/
theorem bitsPhiSecond_abs_le
    (eps h delta : ℝ) (hDelta : 0 < delta)
    (hLower : delta ≤ 1 - h + eps) :
    |bitsPhiSecond eps h| ≤ (delta⁻¹ * delta⁻¹) / Real.log 2 := by
  unfold bitsPhiSecond
  have hInnerPos : 0 < 1 - h + eps := lt_of_lt_of_le hDelta hLower
  have hlogPos : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have hInvLe : (1 - h + eps)⁻¹ ≤ delta⁻¹ := inv_anti₀ hDelta hLower
  have hInvNonneg : 0 ≤ (1 - h + eps)⁻¹ := inv_nonneg.mpr hInnerPos.le
  have hDeltaInvNonneg : 0 ≤ delta⁻¹ := inv_nonneg.mpr hDelta.le
  have hSqLe :
      (1 - h + eps)⁻¹ * (1 - h + eps)⁻¹ ≤ delta⁻¹ * delta⁻¹ := by
    exact mul_le_mul hInvLe hInvLe hInvNonneg hDeltaInvNonneg
  have hNumNonneg :
      0 ≤ (1 - h + eps)⁻¹ * (1 - h + eps)⁻¹ :=
    mul_nonneg hInvNonneg hInvNonneg
  rw [abs_of_nonneg (div_nonneg hNumNonneg hlogPos.le)]
  exact div_le_div_of_nonneg_right hSqLe hlogPos.le

/-- `bitsPhi` is twice continuously differentiable on intervals away from the singularity. -/
theorem bitsPhi_contDiffOn_of_lower_bound
    (eps a b delta : ℝ) (hDelta : 0 < delta)
    (hLower : ∀ y ∈ Set.Icc a b, delta ≤ 1 - y + eps) :
    ContDiffOn ℝ 2 (fun x => bitsPhi eps x) (Set.Icc a b) := by
  unfold bitsPhi
  fun_prop (disch := intro x hx; exact ne_of_gt (lt_of_lt_of_le hDelta (hLower x hx)))

/-- Generic first-order Taylor remainder bound from a second-derivative curvature bound. -/
theorem first_order_taylor_remainder_bound_from_curvature
    {f : ℝ -> ℝ} {a b C x : ℝ}
    (hab : a ≤ b)
    (hf : ContDiffOn ℝ 2 f (Set.Icc a b))
    (hx : x ∈ Set.Icc a b)
    (hC : ∀ y ∈ Set.Icc a b,
      ‖iteratedDerivWithin 2 f (Set.Icc a b) y‖ ≤ C) :
    ‖f x - taylorWithinEval f 1 (Set.Icc a b) a x‖ ≤
      C * (x - a) ^ 2 := by
  have h := taylor_mean_remainder_bound
    (f := f) (a := a) (b := b) (C := C) (x := x) (n := 1)
    hab hf hx hC
  simpa using h

/-- Bits-distortion Taylor bound from a curvature identity and a positive margin. -/
theorem bitsPhi_taylor_remainder_bound_from_delta
    (eps a b delta x : ℝ)
    (hab : a ≤ b)
    (hDelta : 0 < delta)
    (hLower : ∀ y ∈ Set.Icc a b, delta ≤ 1 - y + eps)
    (hx : x ∈ Set.Icc a b)
    (hCurvEq : ∀ y ∈ Set.Icc a b,
      iteratedDerivWithin 2 (fun z => bitsPhi eps z) (Set.Icc a b) y =
        bitsPhiSecond eps y) :
    ‖bitsPhi eps x -
      taylorWithinEval (fun z => bitsPhi eps z) 1 (Set.Icc a b) a x‖ ≤
      ((delta⁻¹ * delta⁻¹) / Real.log 2) * (x - a) ^ 2 := by
  refine first_order_taylor_remainder_bound_from_curvature
    (f := fun z => bitsPhi eps z) hab
    (bitsPhi_contDiffOn_of_lower_bound eps a b delta hDelta hLower)
    hx ?_
  intro y hy
  rw [hCurvEq y hy]
  simpa [Real.norm_eq_abs] using bitsPhiSecond_abs_le eps y delta hDelta (hLower y hy)

/-- Bits-distortion Taylor bound with the curvature identity discharged automatically. -/
theorem bitsPhi_taylor_remainder_bound_from_delta_auto
    (eps a b delta x : ℝ)
    (hab : a < b)
    (hDelta : 0 < delta)
    (hLower : ∀ y ∈ Set.Icc a b, delta ≤ 1 - y + eps)
    (hx : x ∈ Set.Icc a b) :
    ‖bitsPhi eps x -
      taylorWithinEval (fun z => bitsPhi eps z) 1 (Set.Icc a b) a x‖ ≤
      ((delta⁻¹ * delta⁻¹) / Real.log 2) * (x - a) ^ 2 := by
  refine bitsPhi_taylor_remainder_bound_from_delta eps a b delta x
    hab.le hDelta hLower hx ?_
  intro y hy
  exact bitsPhi_iteratedDerivWithin_two_eq eps a b y hab hy
    (ne_of_gt (lt_of_lt_of_le hDelta (hLower y hy)))

/-- Real Taylor finite-difference certificate for the bits distortion. -/
structure RealBitsTaylor where
  eps : ℝ
  hBefore : ℝ
  hAfter : ℝ
  firstOrder : ℝ
  remainder : ℝ
  errorBound : ℝ
  fd_decompose :
    bitsPhi eps hBefore - bitsPhi eps hAfter = firstOrder + remainder
  remainder_bound : |remainder| ≤ errorBound

namespace RealBitsTaylor

/-- Finite-difference/Taylor error bound in real absolute value. -/
theorem finite_difference_taylor_error
    (T : RealBitsTaylor) :
    |(bitsPhi T.eps T.hBefore - bitsPhi T.eps T.hAfter) - T.firstOrder|
      ≤ T.errorBound := by
  have hdiff :
      (bitsPhi T.eps T.hBefore - bitsPhi T.eps T.hAfter) - T.firstOrder =
        T.remainder := by
    rw [T.fd_decompose]
    ring
  rw [hdiff]
  exact T.remainder_bound

end RealBitsTaylor

/-!
## Real graph-SMDP Bellman contraction over finite option sets

The next lemmas instantiate the familiar RL contraction argument directly over
finite option actions.  First each option's expected backup is Lipschitz in the
value function.  Then `finset_sup_abs_diff_le` lifts the result through the
finite `max` over options.
-/

/-- One option-action Q backup on the abstract graph. -/
def OptionQ {S O : Type} [Fintype S]
    (P : S -> O -> S -> ℝ) (R : S -> O -> ℝ) (γ : ℝ)
    (V : S -> ℝ) (s : S) (o : O) : ℝ :=
  R s o + γ * ∑ sp : S, P s o sp * V sp

/-- Finite max Bellman backup over a nonempty option set. -/
def BellmanMax {S O : Type} [Fintype S]
    (options : Finset O) (hOptions : options.Nonempty)
    (P : S -> O -> S -> ℝ) (R : S -> O -> ℝ) (γ : ℝ)
    (V : S -> ℝ) (s : S) : ℝ :=
  options.sup' hOptions (fun o => OptionQ P R γ V s o)

/-- If two finite families are uniformly close, their finite maxima are close. -/
theorem finset_sup_abs_diff_le
    {O : Type} (options : Finset O) (hOptions : options.Nonempty)
    (q r : O -> ℝ) {δ : ℝ}
    (h : ∀ o ∈ options, |q o - r o| ≤ δ) :
    |options.sup' hOptions q - options.sup' hOptions r| ≤ δ := by
  have hmax1 : options.sup' hOptions q ≤ options.sup' hOptions r + δ := by
    apply Finset.sup'_le
    intro o ho
    have hoBound := h o ho
    have hq : q o ≤ r o + δ := by
      have := (abs_sub_le_iff.mp hoBound).1
      linarith
    have hrmax : r o ≤ options.sup' hOptions r := Finset.le_sup' r ho
    linarith
  have hmax2 : options.sup' hOptions r ≤ options.sup' hOptions q + δ := by
    apply Finset.sup'_le
    intro o ho
    have hoBound := h o ho
    have hr : r o ≤ q o + δ := by
      have := (abs_sub_le_iff.mp hoBound).2
      linarith
    have hqmax : q o ≤ options.sup' hOptions q := Finset.le_sup' q ho
    linarith
  rw [abs_sub_le_iff]
  constructor <;> linarith

/-- One fixed option backup is Lipschitz with factor `gamma`. -/
theorem optionQ_lipschitz
    {S O : Type} [Fintype S]
    (P : S -> O -> S -> ℝ) (R : S -> O -> ℝ) (γ eps : ℝ)
    (V W : S -> ℝ) (s : S) (o : O)
    (hγ : 0 ≤ γ)
    (hPnonneg : ∀ sp, 0 ≤ P s o sp)
    (hRowsum : (∑ sp : S, P s o sp) = 1)
    (hVW : ∀ sp, |V sp - W sp| ≤ eps) :
    |OptionQ P R γ V s o - OptionQ P R γ W s o| ≤ γ * eps := by
  unfold OptionQ
  have hdiff :
      R s o + γ * (∑ sp : S, P s o sp * V sp) -
        (R s o + γ * (∑ sp : S, P s o sp * W sp)) =
      γ * (∑ sp : S, P s o sp * (V sp - W sp)) := by
    simp only [add_sub_add_left_eq_sub]
    rw [← mul_sub]
    congr 1
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro sp _hsp
    ring
  rw [hdiff]
  calc
    |γ * (∑ sp : S, P s o sp * (V sp - W sp))|
        = γ * |∑ sp : S, P s o sp * (V sp - W sp)| := by
          rw [abs_mul, abs_of_nonneg hγ]
    _ ≤ γ * (∑ sp : S, |P s o sp * (V sp - W sp)|) := by
          exact mul_le_mul_of_nonneg_left (Finset.abs_sum_le_sum_abs _ _) hγ
    _ = γ * (∑ sp : S, P s o sp * |V sp - W sp|) := by
          congr 1
          apply Finset.sum_congr rfl
          intro sp _hsp
          rw [abs_mul, abs_of_nonneg (hPnonneg sp)]
    _ ≤ γ * (∑ sp : S, P s o sp * eps) := by
          apply mul_le_mul_of_nonneg_left _ hγ
          apply Finset.sum_le_sum
          intro sp _hsp
          exact mul_le_mul_of_nonneg_left (hVW sp) (hPnonneg sp)
    _ = γ * eps := by
          rw [← Finset.sum_mul]
          rw [hRowsum]
          ring

/-- Finite-option Bellman optimality backup is a sup-norm gamma-contraction. -/
theorem bellmanMax_lipschitz
    {S O : Type} [Fintype S]
    (options : Finset O) (hOptions : options.Nonempty)
    (P : S -> O -> S -> ℝ) (R : S -> O -> ℝ) (γ eps : ℝ)
    (V W : S -> ℝ) (s : S)
    (hγ : 0 ≤ γ)
    (hPnonneg : ∀ o ∈ options, ∀ sp, 0 ≤ P s o sp)
    (hRowsum : ∀ o ∈ options, (∑ sp : S, P s o sp) = 1)
    (hVW : ∀ sp, |V sp - W sp| ≤ eps) :
    |BellmanMax options hOptions P R γ V s -
      BellmanMax options hOptions P R γ W s| ≤ γ * eps := by
  unfold BellmanMax
  apply finset_sup_abs_diff_le
  intro o ho
  exact optionQ_lipschitz P R γ eps V W s o hγ
    (hPnonneg o ho) (hRowsum o ho) hVW

/-!
## Real Bellman residual to value-gap bound
-/

/-- Direct real version of `valueGap <= residual / (1 - gamma)`. -/
theorem residual_to_value_gap_real_div
    {γ residual valueGap : ℝ}
    (hγ : γ < 1)
    (hGap : (1 - γ) * valueGap ≤ residual) :
    valueGap ≤ residual / (1 - γ) := by
  have hpos : 0 < 1 - γ := sub_pos.mpr hγ
  rw [le_div_iff₀ hpos]
  rwa [mul_comm]

/-- Budgeted real residual-to-value-gap theorem. -/
theorem residual_to_value_gap_real_budget
    {γ residual valueGap budget : ℝ}
    (hγ : γ < 1)
    (hGap : (1 - γ) * valueGap ≤ residual)
    (hResidual : residual ≤ (1 - γ) * budget) :
    valueGap ≤ budget := by
  have hpos : 0 < 1 - γ := sub_pos.mpr hγ
  have hScaled : (1 - γ) * valueGap ≤ (1 - γ) * budget :=
    hGap.trans hResidual
  exact le_of_mul_le_mul_left hScaled hpos

/-!
## Edge reward-kernel relabeling bounds

The multi-task paper claim keeps the boundary graph fixed and relabels rewards
through an edge occupancy kernel.  These real lemmas instantiate the only new
analytic burden: kernel/reward residuals plug directly into the same Bellman
residual-to-value-gap theorem, and an `l1` occupancy-kernel error controls the
reward residual for bounded rewards.
-/

/-- `l1` edge-occupancy error times reward sup-norm bounds reward residual. -/
theorem reward_kernel_error_le_l1
    {S : Type} [Fintype S]
    (delta r : S -> ℝ) {rMax epsM : ℝ}
    (hr : ∀ s, |r s| ≤ rMax)
    (hdelta : (∑ s : S, |delta s|) ≤ epsM)
    (hrMaxNonneg : 0 ≤ rMax) :
    |∑ s : S, delta s * r s| ≤ rMax * epsM := by
  calc
    |∑ s : S, delta s * r s|
        ≤ ∑ s : S, |delta s * r s| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ s : S, |delta s| * |r s| := by
          apply Finset.sum_congr rfl
          intro s _hs
          rw [abs_mul]
    _ ≤ ∑ s : S, |delta s| * rMax := by
          apply Finset.sum_le_sum
          intro s _hs
          exact mul_le_mul_of_nonneg_left (hr s) (abs_nonneg (delta s))
    _ = (∑ s : S, |delta s|) * rMax := by
          rw [Finset.sum_mul]
    _ ≤ epsM * rMax := by
          exact mul_le_mul_of_nonneg_right hdelta hrMaxNonneg
    _ = rMax * epsM := by
          ring

/-- Reward/continuation kernel residual budget gives the graph-SMDP value gap. -/
theorem reward_kernel_value_gap_real
    {beta epsilonR epsilonGamma Vmax valueGap : ℝ}
    (hbeta : beta < 1)
    (hGap : (1 - beta) * valueGap ≤ epsilonR + Vmax * epsilonGamma) :
    valueGap ≤ (epsilonR + Vmax * epsilonGamma) / (1 - beta) := by
  exact residual_to_value_gap_real_div hbeta hGap

/-- Bounded rewards convert an `l1` occupancy-kernel budget into value gap. -/
theorem reward_kernel_value_gap_from_l1_budget
    {beta epsilonR rMax epsM epsilonGamma Vmax valueGap : ℝ}
    (hbeta : beta < 1)
    (hGap : (1 - beta) * valueGap ≤ epsilonR + Vmax * epsilonGamma)
    (hRewardResidual : epsilonR ≤ rMax * epsM) :
    valueGap ≤ (rMax * epsM + Vmax * epsilonGamma) / (1 - beta) := by
  have hScaled : (1 - beta) * valueGap ≤ rMax * epsM + Vmax * epsilonGamma := by
    linarith
  exact residual_to_value_gap_real_div hbeta hScaled

/--
Triangle-inequality decomposition used in the paper text:
full primitive value vs. approximate reward-kernel graph value is bounded by
option/boundary restriction bias, exact reduction error, and kernel error.
-/
theorem primitive_to_reward_kernel_gap_decomposition
    {vStar vRestricted vExact vApprox : ℝ} :
    |vStar - vApprox| ≤
      |vStar - vRestricted| + |vRestricted - vExact| + |vExact - vApprox| := by
  have hDecomp :
      vStar - vApprox =
        (vStar - vRestricted) + (vRestricted - vExact) + (vExact - vApprox) := by
    ring
  rw [hDecomp]
  calc
    |(vStar - vRestricted) + (vRestricted - vExact) + (vExact - vApprox)|
        ≤ |(vStar - vRestricted) + (vRestricted - vExact)| + |vExact - vApprox| := by
          simpa [add_assoc] using
            abs_add_le ((vStar - vRestricted) + (vRestricted - vExact)) (vExact - vApprox)
    _ ≤ (|vStar - vRestricted| + |vRestricted - vExact|) + |vExact - vApprox| := by
          have h := abs_add_le (vStar - vRestricted) (vRestricted - vExact)
          linarith
    _ = |vStar - vRestricted| + |vRestricted - vExact| + |vExact - vApprox| := by
          ring

end RDBoundaryGreen.RealProof
