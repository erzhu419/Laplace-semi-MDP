# Theorem Stack

The paper should package the proof layer in the same order a reviewer needs it.

Scope note: the Lean statements are finite-kernel statements. The new generic
finite-MDP adapter for Gymnasium ToyText, symbolic MiniGrid, and discretized
PointMaze is covered only after the environment has been converted to an
explicit finite transition kernel. For sampled/discretized continuous domains,
the theorem applies to that empirical finite MDP, not directly to the original
continuous simulator.

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

## T7: Adaptive Feasible Top-K Envelope

Claim: adaptive feasible top-k is a solver wrapper with a precise feasible-discovery guarantee. Given a shared candidate order, feasibility oracle, and cap `K`, adaptive refinement succeeds if and only if the corresponding fixed top-`K` prefix contains at least one feasible candidate. It refines at most `K` candidates and usually fewer when the first feasible candidate appears early.

Boundary: this theorem certifies the feasible envelope, not RD-optimal split selection. Score optimality inside the prefix requires a separate score-interval dominance certificate: the selected candidate's lower score bound must exceed every competing upper score bound. Without this dominance condition, feasible-only early stopping can return a feasible candidate that is not the best-scoring feasible candidate.

Lean hooks:

- `proof/AdaptiveTopK.lean`: `adaptive_feasible_envelope_equivalence`
- `proof/AdaptiveTopK.lean`: `adaptive_refinement_work_bound`
- `proof/AdaptiveTopK.lean`: `score_interval_dominance_certifies_best_feasible`
- `proof/AdaptiveTopK.lean`: `feasible_only_counterexample`

Experiment hooks:

- `experiments/run_adaptive_topk_diagnostics.py`
- `experiments/output/adaptive_topk_diagnostics/summary.md`

## T8: Group Constraint Feasibility

Claim: group-wise risk constraints turn robustness into explicit feasibility conditions.

Lean hooks:

- `proof/RDOperator.lean`: `GroupConstraints`
- `proof/RDOperator.lean`: `feasible_of_zero_violations`

Experiment hooks:

- `experiments/run_group_constrained_adaptive_table.py`
- `experiments/run_random_maze_generalization.py`

## T9: Incremental Insertion Update

Current status: executable diagnostic only. Keep it as a runtime optimization unless the paper makes it a theorem-level contribution.

Experiment hooks:

- `experiments/run_incremental_green_update_check.py`
- `experiments/run_group_incremental_semantic_diff.py`

## T10: Edge Reward/Event Kernel Relabeling

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

## T11: Goal-Event Kernels and Option-Restriction Bias

Claim: terminal interior goals are exact only relative to the option family used
to query them.  For a fixed boundary graph `B`, query goal `g`, and
goal-conditioned local option family `O_g`, define

```text
tau_{B,g} = min(tau_B, T_g)
H_B^{o,g}(b) = E_b^o[gamma^{T_g} 1{T_g < tau_B}]
Gamma_B^{o,not g}(b,b') = E_b^o[gamma^{tau_B} 1{tau_B < T_g, S_tau=b'}].
```

Then the goal-event Bellman backup

```text
T_g^B V(b) =
  max_{o in O_g(b)} [
    R_step^{o,g}(b) + R_g H_B^{o,g}(b)
    + sum_{b'} Gamma_B^{o,not g}(b,b') V(b')
  ]
```

is a contraction with modulus

```text
beta_g = max_{b,o} sum_{b'} Gamma_B^{o,not g}(b,b') < 1,
```

and its fixed point is exact for the option-restricted goal SMDP.  This is not
a free equality to the primitive optimal value.

Kernel approximation bound:

```text
||V_g^{B,O_g} - Vhat_g^{B,O_g}||_inf
  <= (epsilon_R + |R_g| epsilon_H + Vmax epsilon_Gamma) / (1 - beta_g).
```

Option sufficiency bound: if the one-step option-completeness residual is
`epsilon_opt(g)`, then

```text
||V_g^*|_B - V_g^{B,O_g}||_inf <= epsilon_opt(g) / (1 - beta_g).
```

Thus the terminal-goal gap decomposes into option-family insufficiency plus
kernel approximation error.  The new goal-conditioned option ablation is a
proof of concept that this bias can be reduced without promoting `g` into `B`,
but its interface size and event-kernel cost must be reported separately.

Batched implementation hook: for a shared goal-conditioned policy `pi_g`,
absorbing set `A_g = B union {g}`, and interior `I_g = S \ A_g`, the event rows
can be obtained for all boundary starts with one matrix solve:

```text
h_I = (I - gamma P_II)^(-1) gamma P_Ig
G_I = (I - gamma P_II)^(-1) gamma P_IB
H_B(b,g) = gamma P_bg + gamma P_bI h_I
Gamma_B^{not g}(b,.) = gamma P_bB + gamma P_bI G_I.
```

This turns the extension from per-boundary option solves into one shared policy
and one batched event solve per queried goal.  The experiment reports
`n_goal_policies`, `policy_build_time_sec`, `batched_event_solve_time_sec`, and
`break_even_num_tasks` so the extension is not a hidden complexity sink.

Lean hooks:

- `proof/RDOperatorReal.lean`: `goal_event_kernel_value_gap_real`
- `proof/RDOperatorReal.lean`: `goal_event_option_bias_value_gap_real`
- `proof/RDOperatorReal.lean`: `goal_event_total_value_gap_real`

Experiment hooks:

- `experiments/run_edge_reward_kernel_multitask.py`
- `experiments/output/edge_reward_kernel_multitask/summary.md`

## T12: Primitive-To-Graph End-To-End Gap

Claim: graph-SMDP contraction alone does not imply preservation of the original
primitive optimum. For the chain

```text
V* -> V^{O} -> V^{B,O} -> Vhat^{B,O} -> Vsolve^{B,O},
```

the final gap is bounded by

```text
option restriction bias
+ boundary/interface abstraction bias
+ (reward-kernel residual + Vmax * continuation-kernel residual) / (1 - beta)
+ planning residual / (1 - beta).
```

This certificate applies to the returned graph, regardless of whether boundary
discovery is globally optimal. It therefore separates reduction validity from
option-family sufficiency and from solver optimality.

Lean hooks:

- `proof/RDOperatorReal.lean`: `primitive_to_graph_end_to_end_gap_real`
- `proof/RDOperatorReal.lean`: `primitive_to_graph_end_to_end_sup_bound`

Experiment hooks:

- `experiments/run_core_benchmark.py`
- `experiments/run_end_to_end_gap_decomposition.py`
