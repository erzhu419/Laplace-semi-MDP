from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from analyze_boundary_constraint_pairing import (  # noqa: E402
    contingency_counts,
    exact_mcnemar_pvalue,
    paired_bootstrap_interval,
)


def row(student: bool, teacher: bool) -> dict[str, object]:
    return {
        "student_group_all_feasible": student,
        "student_normalized_start_gap": 0.0,
        "teacher_group_all_feasible": teacher,
        "teacher_normalized_start_gap": 0.0,
    }


class BoundaryConstraintPairingTests(unittest.TestCase):
    def test_contingency_uses_paired_joint_outcomes(self) -> None:
        rows = [row(True, True), row(True, False), row(False, True), row(False, False)]
        self.assertEqual(
            contingency_counts(rows, max_normalized_gap=0.01),
            {
                "both_pass": 1,
                "reranker_only": 1,
                "reference_only": 1,
                "both_fail": 1,
            },
        )

    def test_exact_mcnemar_is_symmetric(self) -> None:
        self.assertAlmostEqual(exact_mcnemar_pvalue(17, 7), 0.06391465663909912)
        self.assertEqual(exact_mcnemar_pvalue(7, 17), exact_mcnemar_pvalue(17, 7))
        self.assertEqual(exact_mcnemar_pvalue(0, 0), 1.0)

    def test_bootstrap_interval_is_reproducible(self) -> None:
        differences = np.asarray([1.0, 1.0, -1.0, 0.0, 0.0])
        first = paired_bootstrap_interval(differences, 0.95, 2_000, seed=5)
        second = paired_bootstrap_interval(differences, 0.95, 2_000, seed=5)
        self.assertEqual(first, second)
        self.assertLessEqual(first[0], float(np.mean(differences)))
        self.assertGreaterEqual(first[1], float(np.mean(differences)))


if __name__ == "__main__":
    unittest.main()
