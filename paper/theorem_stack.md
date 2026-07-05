# Theorem Stack

The paper should package the proof layer in the same order a reviewer needs it.

## T1: Frozen Finite-Difference Identity

Claim: for a fixed candidate universe, options, edge weights, and local rate costs, the RD split score is exactly the finite difference of the frozen objective.

Lean hooks:

- `proof/RDOperator.lean`: `FrozenObjective.fd_exact`
- `proof/RDOperator.lean`: `MultiProbeObjective.fd_exact`

Experiment hooks:

- `experiments/run_rd_operator_theorem_checks.py`
- `experiments/output/rd_operator_theorem_checks_actual_small/summary.csv`

Boundary: this theorem does not claim the adaptive recompute solver is optimizing the same objective after the split.

## T2: First-Hit Green Kernel Legality

Claim: for a finite absorbing interior, the first-hit Green kernel

```text
K = e_b^T (I - P_II)^(-1) P_IC
```

is legal, nonnegative under the stated hypotheses, and row-mass bounded.

Lean hooks:

- `proof/RDOperatorReal.lean`: `green_formula_solves_linear_system`
- `proof/RDOperatorReal.lean`: `green_formula_entry_nonnegative`
- `proof/RDOperatorReal.lean`: `green_entry_le_rowBound`

Experiment hooks:

- `experiments/run_core_benchmark.py`
- `experiments/run_kernel_approximation_benchmark.py`

## T3: Truncated and Adaptive Green Certification

Claim: the truncated Neumann prefix converges to the Green kernel, and a tail certificate bounds score error.

Lean hooks:

- `proof/RDOperatorReal.lean`: `finite_neumann_tail_entry_le_geometric`
- `proof/RDOperatorReal.lean`: `error_le_tailBound`
- `proof/RDOperatorReal.lean`: `spectral_certificate_signed_finite_neumann_tail_entry_abs_le`

Experiment hooks:

- `experiments/run_adaptive_green_certification.py`
- `experiments/run_weighted_spectral_certificate.py`
- `experiments/run_conditioned_weighted_certificate.py`

## T4: Bits Distortion Curvature

Claim: `phi(h)=-log2(1-h+eps)` has a controlled second derivative on the safe interval, giving finite-difference/Taylor approximation bounds.

Lean hooks:

- `proof/RDOperatorReal.lean`: `bitsPhi_iteratedDerivWithin_two_eq`
- `proof/RDOperatorReal.lean`: `bitsPhi_taylor_remainder_bound_from_delta_auto`
- `proof/RDOperatorReal.lean`: `finite_difference_taylor_error`

Experiment hooks:

- `experiments/run_rd_operator_theorem_checks.py`

## T5: Graph-SMDP Bellman Contraction

Claim: with finite option actions and discount `gamma < 1`, the graph-SMDP Bellman operator is a sup-norm contraction; residual errors bound value gaps.

Lean hooks:

- `proof/RDOperatorReal.lean`: `optionQ_lipschitz`
- `proof/RDOperatorReal.lean`: `bellmanMax_lipschitz`
- `proof/RDOperatorReal.lean`: `residual_to_value_gap_real_budget`

Experiment hooks:

- `experiments/run_core_benchmark.py`
- `experiments/run_reward_propagation_curve.py`

## T6: Top-Set and Margin Stability

Claim: when the certified margin dominates approximation/adaptive error, the top split is stable; otherwise top-set exact fallback gives an honest epsilon/tie-aware certificate.

Lean hooks:

- `proof/RDOperator.lean`: `margin_stability`
- `proof/RDOperatorReal.lean`: `interval_certified_top_choice`
- `proof/RDOperatorReal.lean`: `top_set_exact_fallback_global_optimal`

Experiment hooks:

- `experiments/run_adaptive_green_certification.py`

## T7: Group Constraint Feasibility

Claim: group-wise risk constraints turn robustness into explicit feasibility conditions.

Lean hooks:

- `proof/RDOperator.lean`: `GroupConstraints`
- `proof/RDOperator.lean`: `feasible_of_zero_violations`

Experiment hooks:

- `experiments/run_group_constrained_adaptive_table.py`
- `experiments/run_random_maze_generalization.py`

## T8: Incremental Insertion Update

Current status: executable diagnostic only. Keep it as a runtime optimization unless the paper makes it a theorem-level contribution.

Experiment hooks:

- `experiments/run_incremental_green_update_check.py`
- `experiments/run_group_incremental_semantic_diff.py`

## T9: Edge Reward/Event Kernel Relabeling

Claim: multi-task rewards should not change the boundary graph topology.  For a
fixed boundary set `B` and option library, exact edge occupancy kernels

```text
M_B^o(b,s) = E_b^o[sum_{t=0}^{tau_B-1} gamma^t 1{S_t=s}]
```

give exact reward relabeling for every bounded additive reward:

```text
R_r^o(b) = <M_B^o(b,.), r>.
```

Together with the first-boundary continuation kernel `Gamma_B^o`, this is
exactly the Bellman operator for the option-restricted graph SMDP.  For feature
rewards `r_theta = Phi theta`, the same statement stores the edge successor
feature `Psi_B^o(b) = M_B^o(b,.) Phi` and relabels by
`R_theta^o(b) = <Psi_B^o(b), theta>`.

For absorbing interior goal queries, keep `B` fixed and add query-time first-hit
event kernels

```text
H_B^o(b,g) = E_b^o[gamma^{T_g} 1{T_g < tau_B}]
Gamma_B^{o,not g}(b,b') = E_b^o[gamma^{tau_B} 1{tau_B < T_g, S_tau=b'}].
```

Approximation bound: if `Mhat` and `Gammahat` induce operator `That`, the exact
graph operator is `T`, row mass is at most `beta < 1`, and

```text
epsilon_R(r) = sup_{b,o} |<(Mhat-M)_B^o(b,.), r>|
epsilon_Gamma = sup_{b,o} ||Gammahat_B^o(b,.) - Gamma_B^o(b,.)||_1,
```

then

```text
||V_r^B - Vhat_r^B||_inf
  <= (epsilon_R(r) + Vmax epsilon_Gamma) / (1 - beta).
```

The full primitive-MDP gap should be decomposed as option/boundary restriction
bias plus exact reduction error plus this kernel approximation error; the exact
reduction term is zero when the edge kernels are exact.

Lean hooks:

- `proof/RDOperatorReal.lean`: `reward_kernel_error_le_l1`
- `proof/RDOperatorReal.lean`: `reward_kernel_value_gap_real`
- `proof/RDOperatorReal.lean`: `reward_kernel_value_gap_from_l1_budget`
- `proof/RDOperatorReal.lean`: `primitive_to_reward_kernel_gap_decomposition`

Experiment hooks:

- `experiments/run_edge_reward_kernel_multitask.py`
- `experiments/output/edge_reward_kernel_multitask/summary.md`
