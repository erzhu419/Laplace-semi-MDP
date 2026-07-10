from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from calibrate_boundary_heatmap_selective_audit import (  # noqa: E402
    calibrate_threshold,
    evaluate_rule,
    passes_constraints,
)


class BoundaryHeatmapSelectiveAuditTests(unittest.TestCase):
    def test_joint_constraint_includes_value_gap(self) -> None:
        row = {
            "student_group_all_feasible": "True",
            "student_normalized_start_gap": "0.02",
        }
        self.assertFalse(passes_constraints(row, "student", 0.01))

    def test_missing_uncertainty_does_not_hide_joint_failures(self) -> None:
        rows = [
            {
                "student_group_all_feasible": "True",
                "student_normalized_start_gap": "0.0",
                "teacher_group_all_feasible": "True",
                "teacher_normalized_start_gap": "0.0",
                "student_score_margin": "0.8",
            },
            {
                "student_group_all_feasible": "False",
                "student_normalized_start_gap": "0.0",
                "teacher_group_all_feasible": "True",
                "teacher_normalized_start_gap": "0.0",
                "student_score_margin": "0.1",
            },
            {
                "student_group_all_feasible": "True",
                "student_normalized_start_gap": "0.02",
                "teacher_group_all_feasible": "True",
                "teacher_normalized_start_gap": "0.0",
                "student_score_margin": "0.2",
            },
        ]
        threshold, n_failures = calibrate_threshold(
            rows,
            field="student_score_margin",
            transform=lambda value: -value,
            target_recall=1.0,
            max_normalized_gap=0.01,
        )
        self.assertEqual(n_failures, 2)
        result = evaluate_rule(
            rows,
            field="student_score_margin",
            transform=lambda value: -value,
            threshold=threshold,
            max_normalized_gap=0.01,
        )
        self.assertEqual(result["undetected_failures"], 0)
        self.assertEqual(result["failure_recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
