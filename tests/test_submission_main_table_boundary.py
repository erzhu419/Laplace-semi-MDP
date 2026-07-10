from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from run_submission_main_table import build_boundary_student_rows  # noqa: E402


class SubmissionBoundaryTableTests(unittest.TestCase):
    def test_reranker_row_keeps_quality_and_safety_metrics_together(self) -> None:
        constraint = {
            "student_method": "constraint_aware_gnn",
            "n_rows": "90",
            "student_feasible_rate": str(83 / 90),
            "student_joint_constraint_rate": str(81 / 90),
            "teacher_feasible_rate": str(71 / 90),
            "teacher_joint_constraint_rate": str(71 / 90),
            "median_selection_speedup_vs_teacher": "656.0",
            "median_accepted_speedup_vs_teacher_pipeline": "0.428",
        }
        gate = {
            "split": "test",
            "n_contexts": "90",
            "joint_pass_count": "81",
            "oracle_union_pass_count": "85",
        }
        routing = {
            "target_validation_failure_recall": "1.0",
            "test_n_student_failures": "9",
            "test_audit_rate": str(13 / 90),
            "test_failure_recall": str(3 / 9),
            "test_undetected_failures": "6",
        }
        full_audit = {"median_selective_speedup_vs_teacher": "0.428"}

        rows = build_boundary_student_rows(
            [], [], [], [constraint], [gate], [routing], [full_audit]
        )
        reranker = next(
            row
            for row in rows
            if row["proposal"] == "Constraint-aware fixed-family reranker"
        )
        self.assertEqual(reranker["raw_joint_pass"], "81/90")
        self.assertEqual(reranker["candidate_oracle_joint_pass"], "85/90")
        self.assertEqual(reranker["adaptive_reference_joint_pass"], "71/90")
        self.assertEqual(reranker["undetected_failures"], "6/9")
        self.assertEqual(reranker["full_audit_speedup"], "0.428")
        self.assertEqual(reranker["certified"], "no")

        proposals = {row["proposal"] for row in rows}
        self.assertIn("Adaptive RD reference proposal", proposals)
        self.assertIn("Candidate-family oracle", proposals)


if __name__ == "__main__":
    unittest.main()
