# Theorem-to-Experiment Bridge

Generated: 2026-07-05T19:41:30

This report turns each theoretical claim into a proof artifact, an experiment artifact, and an explicit manuscript placement. It is meant to prevent theorem claims from drifting beyond what the code and Lean layer actually support.

- proof-plus-experiment covered claims: `7/9`

| paper_claim | math_object | proof_status | experiment_status | manuscript_location | remaining_gap |
| --- | --- | --- | --- | --- | --- |
| The frozen split score is an exact finite difference of a fixed local RD objective. | S_FD(x|B)=L_theta(B)-L_theta(B union {x}) | proved_symbol_present | rows=9, margin_condition=1, stable_when_checked=1 | Method theorem, not adaptive solver guarantee | State frozen candidate universe/options/weights explicitly. |
| First-hit Green kernels define legal compressed edge models on finite absorbing interiors. | K=e_b^T (I-P_II)^(-1) P_IC | proved_symbol_present | rows=80, graph_rows=70, max_start_gap=0.04973 | Graph-SMDP construction | Use exact Green as reference operator; adaptive/truncated variants are certified implementations. |
| Truncated/adaptive Green scores are certified by Neumann tail bounds. | sum_{t<=K} P_II^t P_IC with tail <= epsilon | proved_symbol_present | rows=20, final=20, tie_aware_final=20 | Implementation theorem and appendix certificate | Report when tie/top-set exact fallback is used rather than hiding it as speed. |
| Bits distortion admits a controlled finite-difference/Taylor approximation. | phi(h)=-log2(1-h+eps) | proved_symbol_present | rows=9, margin_condition=1, stable_when_checked=1 | Operator approximation and ablation | Keep finite-difference score as the main theorem; gradient score is an approximation. |
| The graph-SMDP Bellman backup is a sup-norm contraction under finite options and gamma<1. | ||T V - T W||_infty <= gamma ||V-W||_infty | proved_symbol_present | rows=80, graph_rows=70, max_start_gap=0.04973 | Planning correctness lemma | Tie value-gap reporting to residual diagnostics in each benchmark table. |
| Margin and top-set certificates separate stable operator decisions from ambiguous ties. | m>2 epsilon_adapt implies stable top choice | proved_symbol_present | rows=20, final=20, tie_aware_final=20 | Certificate table | Use tie-aware timing as the conservative runtime accounting. |
| Group-constrained RD makes robustness constraints explicit instead of hiding them in a scalar risk. | forall group, risk_g(B) <= budget_g | proved_symbol_present | rows=18, feasible=12 | Robust objective and main ablation | Use random-maze and held-out probes to show robustness is not hand-tuned to one map. |
| Incremental insertion scoring is an implementation optimization, not a new theorem yet. | parent-to-child boundary insertion update | lean_pending | rows=30, selected_match=26, max_score_error=233.2 | Runtime ablation, not core correctness theorem | Formalize the insertion algebra only if it becomes a central claim. |
| The extracted graph should generalize across maze instances, not only fixed toy layouts. | same objective on held-out DFS maze family | empirical_stress_test | rows=6, feasible=3 | Generalization/stress-test section | Scale to larger random maps on node001-node006 for final paper numbers. |
