#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from run_first_boundary_targeted import markdown_table
from run_option_algorithm_comparison import json_default, write_csv_all_fields


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finite_float(value: object, default: float = float("nan")) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def symbol_status(proof_root: Path, symbols: Sequence[str]) -> str:
    text = ""
    for path in sorted(proof_root.glob("*.lean")):
        if path.exists():
            text += path.read_text(encoding="utf-8")
    missing = [symbol for symbol in symbols if symbol not in text]
    if not missing:
        return "proved_symbol_present"
    return "missing_symbols:" + ",".join(missing)


def metric_status(name: str, rows: Sequence[Mapping[str, str]]) -> str:
    if not rows:
        return "artifact_missing"
    if name == "adaptive_certification":
        final = sum(1 for row in rows if str(row.get("final_certified", "")).lower() == "true")
        tie_final = sum(1 for row in rows if str(row.get("tie_aware_final_certified", "")).lower() == "true")
        return f"rows={len(rows)}, final={final}, tie_aware_final={tie_final}"
    if name == "group_adaptive":
        feasible = sum(1 for row in rows if str(row.get("group_all_feasible", "")).lower() == "true")
        return f"rows={len(rows)}, feasible={feasible}"
    if name == "core_benchmark":
        graph_rows = [row for row in rows if str(row.get("method_spec", "")) != "full_vi"]
        max_gap = max((finite_float(row.get("start_gap"), 0.0) for row in graph_rows), default=0.0)
        return f"rows={len(rows)}, graph_rows={len(graph_rows)}, max_start_gap={max_gap:.4g}"
    if name == "end_to_end":
        converged = [row for row in rows if row.get("config_label") == "converged_k256_i256"]
        certified = sum(
            1
            for row in converged
            if str(row.get("certificate_holds", "")).lower() == "true"
        )
        normalized = sorted(
            finite_float(row.get("normalized_primitive_to_solved_gap"))
            for row in converged
            if math.isfinite(finite_float(row.get("normalized_primitive_to_solved_gap")))
        )
        normalized_bounds = [
            finite_float(row.get("normalized_certified_total_bound"))
            for row in converged
            if math.isfinite(finite_float(row.get("normalized_certified_total_bound")))
        ]
        median_gap = statistics.median(normalized) if normalized else float("nan")
        p95_gap = normalized[int(0.95 * (len(normalized) - 1))] if normalized else float("nan")
        max_bound = max(normalized_bounds, default=float("nan"))
        return (
            f"rows={len(rows)}, converged={len(converged)}, certified={certified}, "
            f"median_norm_gap={median_gap:.4g}, p95_norm_gap={p95_gap:.4g}, "
            f"max_norm_bound={max_bound:.4g}"
        )
    if name == "operator_checks":
        stable = sum(1 for row in rows if str(row.get("margin_stability_correct", "")).lower() == "true")
        condition = sum(1 for row in rows if str(row.get("margin_stability_condition", "")).lower() == "true")
        return f"rows={len(rows)}, margin_condition={condition}, stable_when_checked={stable}"
    if name == "incremental_green":
        max_score_error = max((finite_float(row.get("max_score_error_vs_exact"), 0.0) for row in rows), default=0.0)
        match = sum(1 for row in rows if str(row.get("selected_state_match", "")).lower() == "true")
        return f"rows={len(rows)}, selected_match={match}, max_score_error={max_score_error:.4g}"
    if name == "random_maze":
        feasible = sum(1 for row in rows if str(row.get("group_all_feasible", "")).lower() == "true")
        return f"rows={len(rows)}, feasible={feasible}"
    if name == "budget_recovery":
        recovered = sum(1 for row in rows if str(row.get("recovered", "")).lower() == "true")
        plateau = sum(1 for row in rows if row.get("failure_class") == "fixed_family_or_probe_plateau")
        max_splits = max((finite_float(row.get("max_splits_tested"), 0.0) for row in rows), default=0.0)
        max_boundary = max((finite_float(row.get("largest_n_boundary"), 0.0) for row in rows), default=0.0)
        return (
            f"contexts={len(rows)}, recovered={recovered}, fixed_family_plateau={plateau}, "
            f"max_splits={max_splits:.0f}, max_boundary={max_boundary:.0f}"
        )
    if name == "edge_reward_multitask":
        additive = [row for row in rows if str(row.get("variant")) == "fixed_B_edge_reward_kernel"]
        event = [row for row in rows if str(row.get("variant")) == "fixed_B_event_hit_kernel"]
        goal_conditioned = [
            row for row in rows if str(row.get("variant")) == "fixed_B_goal_conditioned_event_options"
        ]
        max_event_gap = max((finite_float(row.get("start_gap_max"), 0.0) for row in event), default=0.0)
        max_gc_gap = max((finite_float(row.get("start_gap_max"), 0.0) for row in goal_conditioned), default=0.0)
        value_scale = 1.0 / (1.0 - 0.97)
        return (
            f"rows={len(rows)}, additive={len(additive)}, "
            f"event_norm_gap={max_event_gap / value_scale:.4g}, "
            f"goal_conditioned_norm_gap={max_gc_gap / value_scale:.4g}"
        )
    if name == "adaptive_topk":
        matches = sum(1 for row in rows if str(row.get("feasible_match", "")).lower() == "true")
        max_regret = max((finite_float(row.get("lexicographic_regret_vs_fixed"), 0.0) for row in rows), default=0.0)
        speedups = [finite_float(row.get("selection_speedup_fixed_over_adaptive")) for row in rows]
        speedups = [value for value in speedups if value == value]
        median_speedup = sorted(speedups)[len(speedups) // 2] if speedups else float("nan")
        return f"rows={len(rows)}, feasible_match={matches}, max_regret={max_regret:.4g}, median_speedup={median_speedup:.4g}"
    return f"rows={len(rows)}"


def bridge_rows(args: argparse.Namespace) -> List[Dict[str, object]]:
    adaptive_rows = read_csv_rows(args.adaptive_cert_csv)
    group_rows = read_csv_rows(args.group_adaptive_csv)
    core_rows = read_csv_rows(args.core_csv)
    operator_rows = read_csv_rows(args.operator_checks_csv)
    incremental_rows = read_csv_rows(args.incremental_green_csv)
    random_rows = read_csv_rows(args.random_maze_csv)
    budget_recovery_rows = read_csv_rows(args.budget_recovery_csv)
    edge_reward_rows = read_csv_rows(args.edge_reward_csv)
    adaptive_topk_rows = read_csv_rows(args.adaptive_topk_paired_csv)
    return [
        {
            "paper_claim": "The frozen split score is an exact finite difference of a fixed local RD objective.",
            "math_object": "S_FD(x|B)=L_theta(B)-L_theta(B union {x})",
            "proof_symbols": "FrozenObjective.fd_exact; MultiProbeObjective.fd_exact",
            "proof_status": symbol_status(args.proof_root, ["theorem fd_exact", "MultiProbeObjective"]),
            "experiment_artifact": args.operator_checks_csv,
            "experiment_status": metric_status("operator_checks", operator_rows),
            "manuscript_location": "Method theorem, not adaptive solver guarantee",
            "remaining_gap": "State frozen candidate universe/options/weights explicitly.",
        },
        {
            "paper_claim": "First-hit Green kernels define legal compressed edge models on finite absorbing interiors.",
            "math_object": "K=e_b^T (I-P_II)^(-1) P_IC",
            "proof_symbols": "green_formula_solves_linear_system; green_formula_entry_nonnegative; green_entry_le_rowBound",
            "proof_status": symbol_status(
                args.proof_root,
                ["green_formula_solves_linear_system", "green_formula_entry_nonnegative", "green_entry_le_rowBound"],
            ),
            "experiment_artifact": args.core_csv,
            "experiment_status": metric_status("core_benchmark", core_rows),
            "manuscript_location": "Graph-SMDP construction",
            "remaining_gap": "Use exact Green as reference operator; adaptive/truncated variants are certified implementations.",
        },
        {
            "paper_claim": "Truncated/adaptive Green scores are certified by Neumann tail bounds.",
            "math_object": "sum_{t<=K} P_II^t P_IC with tail <= epsilon",
            "proof_symbols": "finite_neumann_tail_entry_le_geometric; error_le_tailBound; spectral_certificate_signed_finite_neumann_tail_entry_abs_le",
            "proof_status": symbol_status(
                args.proof_root,
                [
                    "finite_neumann_tail_entry_le_geometric",
                    "error_le_tailBound",
                    "spectral_certificate_signed_finite_neumann_tail_entry_abs_le",
                ],
            ),
            "experiment_artifact": args.adaptive_cert_csv,
            "experiment_status": metric_status("adaptive_certification", adaptive_rows),
            "manuscript_location": "Implementation theorem and appendix certificate",
            "remaining_gap": "Report when tie/top-set exact fallback is used rather than hiding it as speed.",
        },
        {
            "paper_claim": "Bits distortion admits a controlled finite-difference/Taylor approximation.",
            "math_object": "phi(h)=-log2(1-h+eps)",
            "proof_symbols": "bitsPhi_iteratedDerivWithin_two_eq; bitsPhi_taylor_remainder_bound_from_delta_auto; finite_difference_taylor_error",
            "proof_status": symbol_status(
                args.proof_root,
                [
                    "bitsPhi_iteratedDerivWithin_two_eq",
                    "bitsPhi_taylor_remainder_bound_from_delta_auto",
                    "finite_difference_taylor_error",
                ],
            ),
            "experiment_artifact": args.operator_checks_csv,
            "experiment_status": metric_status("operator_checks", operator_rows),
            "manuscript_location": "Operator approximation and ablation",
            "remaining_gap": "Keep finite-difference score as the main theorem; gradient score is an approximation.",
        },
        {
            "paper_claim": "The graph-SMDP Bellman backup is a sup-norm contraction under finite options and gamma<1.",
            "math_object": "||T V - T W||_infty <= gamma ||V-W||_infty",
            "proof_symbols": "optionQ_lipschitz; bellmanMax_lipschitz; residual_to_value_gap_real_budget",
            "proof_status": symbol_status(
                args.proof_root,
                ["optionQ_lipschitz", "bellmanMax_lipschitz", "residual_to_value_gap_real_budget"],
            ),
            "experiment_artifact": args.core_csv,
            "experiment_status": metric_status("core_benchmark", core_rows),
            "manuscript_location": "Planning correctness lemma",
            "remaining_gap": "Tie value-gap reporting to residual diagnostics in each benchmark table.",
        },
        {
            "paper_claim": "The primitive optimal-value gap decomposes into option restriction, boundary abstraction, kernel approximation, and planning residual terms.",
            "math_object": "eps_option + eps_boundary + (eps_R + Vmax eps_Gamma + eps_plan)/(1-beta)",
            "proof_symbols": "primitive_to_graph_end_to_end_gap_real; primitive_to_graph_end_to_end_sup_bound",
            "proof_status": symbol_status(
                args.proof_root,
                [
                    "primitive_to_graph_end_to_end_gap_real",
                    "primitive_to_graph_end_to_end_sup_bound",
                ],
            ),
            "experiment_artifact": args.end_to_end_csv,
            "experiment_status": metric_status("end_to_end", read_csv_rows(args.end_to_end_csv)),
            "manuscript_location": "Main preservation theorem and value-gap accounting",
            "remaining_gap": "Keep the deliberately under-solved truncation/planning ablation separate from the converged certificate table.",
        },
        {
            "paper_claim": "Margin and top-set certificates separate stable operator decisions from ambiguous ties.",
            "math_object": "m>2 epsilon_adapt implies stable top choice",
            "proof_symbols": "margin_stability; interval_certified_top_choice; top_set_exact_fallback_global_optimal",
            "proof_status": symbol_status(
                args.proof_root,
                ["margin_stability", "interval_certified_top_choice", "top_set_exact_fallback_global_optimal"],
            ),
            "experiment_artifact": args.adaptive_cert_csv,
            "experiment_status": metric_status("adaptive_certification", adaptive_rows),
            "manuscript_location": "Certificate table",
            "remaining_gap": "Use tie-aware timing as the conservative runtime accounting.",
        },
        {
            "paper_claim": "Adaptive feasible top-k has the same feasible envelope as fixed top-K under a shared candidate order and feasibility oracle.",
            "math_object": "AdaptiveFeasibleTopK succeeds iff exists j<K with F(x_j)",
            "proof_symbols": "adaptive_feasible_envelope_equivalence; adaptive_refinement_work_bound; score_interval_dominance_certifies_best_feasible",
            "proof_status": symbol_status(
                args.proof_root,
                [
                    "adaptive_feasible_envelope_equivalence",
                    "adaptive_refinement_work_bound",
                    "score_interval_dominance_certifies_best_feasible",
                    "feasible_only_counterexample",
                ],
            ),
            "experiment_artifact": args.adaptive_topk_paired_csv,
            "experiment_status": metric_status("adaptive_topk", adaptive_topk_rows),
            "manuscript_location": "Main discovery backend and fixed-topK ablation",
            "remaining_gap": "Claim feasible discovery and refinement work savings; do not claim score-optimal split selection without interval dominance.",
        },
        {
            "paper_claim": "Group-constrained RD makes robustness constraints explicit instead of hiding them in a scalar risk.",
            "math_object": "forall group, risk_g(B) <= budget_g",
            "proof_symbols": "GroupConstraints; feasible_of_zero_violations",
            "proof_status": symbol_status(args.proof_root, ["GroupConstraints", "feasible_of_zero_violations"]),
            "experiment_artifact": args.group_adaptive_csv,
            "experiment_status": metric_status("group_adaptive", group_rows),
            "manuscript_location": "Robust objective and main ablation",
            "remaining_gap": "Use random-maze and held-out probes to show robustness is not hand-tuned to one map.",
        },
        {
            "paper_claim": "Incremental insertion scoring is an implementation optimization, not a new theorem yet.",
            "math_object": "parent-to-child boundary insertion update",
            "proof_symbols": "none",
            "proof_status": "lean_pending",
            "experiment_artifact": args.incremental_green_csv,
            "experiment_status": metric_status("incremental_green", incremental_rows),
            "manuscript_location": "Runtime ablation, not core correctness theorem",
            "remaining_gap": "Formalize the insertion algebra only if it becomes a central claim.",
        },
        {
            "paper_claim": "Fixed-boundary reward relabeling keeps task reward support out of the graph topology.",
            "math_object": "R_r^o(b)=<M_B^o(b,.),r>",
            "proof_symbols": "reward_kernel_error_le_l1; reward_kernel_value_gap_real; primitive_to_reward_kernel_gap_decomposition",
            "proof_status": symbol_status(
                args.proof_root,
                [
                    "reward_kernel_error_le_l1",
                    "reward_kernel_value_gap_real",
                    "primitive_to_reward_kernel_gap_decomposition",
                ],
            ),
            "experiment_artifact": args.edge_reward_csv,
            "experiment_status": metric_status("edge_reward_multitask", edge_reward_rows),
            "manuscript_location": "Multi-task compression and reward relabeling",
            "remaining_gap": "Label the legacy dense-VI denominator and report normalized option/boundary restriction gaps.",
        },
        {
            "paper_claim": "Goal-conditioned event options reduce terminal-goal restriction bias without adding the goal to B.",
            "math_object": "epsilon_opt(g)/(1-beta_g) plus event-kernel residuals",
            "proof_symbols": "goal_event_kernel_value_gap_real; goal_event_option_bias_value_gap_real; goal_event_total_value_gap_real",
            "proof_status": symbol_status(
                args.proof_root,
                [
                    "goal_event_kernel_value_gap_real",
                    "goal_event_option_bias_value_gap_real",
                    "goal_event_total_value_gap_real",
                ],
            ),
            "experiment_artifact": args.edge_reward_csv,
            "experiment_status": metric_status("edge_reward_multitask", edge_reward_rows),
            "manuscript_location": "Secondary terminal-goal extension",
            "remaining_gap": "Treat this as a costed secondary repair; the current table does not show a median win over even the legacy denominator.",
        },
        {
            "paper_claim": "The extracted graph should generalize across maze instances, not only fixed toy layouts.",
            "math_object": "same objective on held-out DFS maze family",
            "proof_symbols": "not_a_theorem",
            "proof_status": "empirical_stress_test",
            "experiment_artifact": f"{args.random_maze_csv}; {args.budget_recovery_csv}",
            "experiment_status": (
                f"{metric_status('random_maze', random_rows)}; "
                f"{metric_status('budget_recovery', budget_recovery_rows)}"
            ),
            "manuscript_location": "Generalization/stress-test section",
            "remaining_gap": (
                "State the sole max-splits-16 topology/value plateau as fixed option/probe-family bias, "
                "not as an unresolved boundary-budget failure."
            ),
        },
    ]


def write_report(rows: Sequence[Mapping[str, object]], out_path: Path) -> None:
    columns = [
        "paper_claim",
        "math_object",
        "proof_status",
        "experiment_status",
        "manuscript_location",
        "remaining_gap",
    ]
    covered = sum(
        1
        for row in rows
        if str(row.get("proof_status", "")).startswith("proved")
        and "artifact_missing" not in str(row.get("experiment_status", ""))
    )
    lines = [
        "# Theorem-to-Experiment Bridge",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This report turns each theoretical claim into a proof artifact, an experiment artifact, and an explicit manuscript placement. It is meant to prevent theorem claims from drifting beyond what the code and Lean layer actually support.",
        "",
        f"- proof-plus-experiment covered claims: `{covered}/{len(rows)}`",
        "",
        markdown_table([{col: row.get(col, "") for col in columns} for row in rows], columns),
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a theorem/proof/experiment bridge table.")
    parser.add_argument("--proof-root", type=Path, default=Path("proof"))
    parser.add_argument("--core-csv", type=Path, default=Path("experiments/output/core_benchmark/core_benchmark.csv"))
    parser.add_argument(
        "--end-to-end-csv",
        type=Path,
        default=Path("experiments/output/end_to_end_gap_decomposition/end_to_end_gap_decomposition.csv"),
    )
    parser.add_argument(
        "--operator-checks-csv",
        type=Path,
        default=Path("experiments/output/rd_operator_theorem_checks_actual_small/summary.csv"),
    )
    parser.add_argument(
        "--adaptive-cert-csv",
        type=Path,
        default=Path("experiments/output/adaptive_green_certification/certification_summary.csv"),
    )
    parser.add_argument(
        "--group-adaptive-csv",
        type=Path,
        default=Path("experiments/output/group_constrained_adaptive_large/group_constrained_adaptive_large.csv"),
    )
    parser.add_argument(
        "--incremental-green-csv",
        type=Path,
        default=Path("experiments/output/incremental_green_update/incremental_green_update.csv"),
    )
    parser.add_argument(
        "--random-maze-csv",
        type=Path,
        default=Path("experiments/output/random_maze_generalization/random_maze_generalization.csv"),
    )
    parser.add_argument(
        "--budget-recovery-csv",
        type=Path,
        default=Path(
            "experiments/output/random_maze_budget_recovery/"
            "random_maze_budget_recovery_summary.csv"
        ),
    )
    parser.add_argument(
        "--edge-reward-csv",
        type=Path,
        default=Path("experiments/output/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv"),
    )
    parser.add_argument(
        "--adaptive-topk-paired-csv",
        type=Path,
        default=Path("experiments/output/adaptive_topk_diagnostics/paired_equivalence.csv"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/theorem_experiment_bridge"))
    args = parser.parse_args()

    rows = [
        {key: str(value) if isinstance(value, Path) else value for key, value in row.items()}
        for row in bridge_rows(args)
    ]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "theorem_experiment_bridge.csv", rows)
    (args.out_dir / "theorem_experiment_bridge.json").write_text(
        json.dumps(rows, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    write_report(rows, args.out_dir / "summary.md")


if __name__ == "__main__":
    main()
