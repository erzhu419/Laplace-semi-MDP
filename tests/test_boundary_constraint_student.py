from __future__ import annotations

from pathlib import Path
import sys
import unittest

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from boundary_constraint_student import (  # noqa: E402
    asymmetric_regression_loss,
    choose_candidate_indices,
    merge_duplicate_proposals,
    topology_holdout_maps,
)


class BoundaryConstraintStudentTests(unittest.TestCase):
    def test_candidate_dedup_keeps_aliases(self) -> None:
        rows = [
            {
                "proposal_kind": "learned_count",
                "proposal_aliases": '["learned_count"]',
                "predicted_boundary": "[3, 1]",
            },
            {
                "proposal_kind": "top1",
                "proposal_aliases": '["top1"]',
                "predicted_boundary": "[1, 3]",
            },
        ]
        merged, dropped = merge_duplicate_proposals(rows)
        self.assertEqual(dropped, 1)
        self.assertEqual(len(merged), 1)
        self.assertIn("learned_count", str(merged[0]["proposal_aliases"]))
        self.assertIn("top1", str(merged[0]["proposal_aliases"]))

    def test_underestimation_costs_more_than_equal_overestimation(self) -> None:
        underestimated = asymmetric_regression_loss(
            torch.tensor([0.0]), torch.tensor([1.0]), underestimation_weight=4.0
        )
        overestimated = asymmetric_regression_loss(
            torch.tensor([1.0]), torch.tensor([0.0]), underestimation_weight=4.0
        )
        self.assertGreater(float(underestimated), float(overestimated))

    def test_topology_split_keeps_all_slips_on_one_side(self) -> None:
        rows = []
        for map_index in range(12):
            for slip in (0.0, 0.05, 0.1):
                rows.append(
                    {
                        "map": f"maze_{map_index}",
                        "slip": slip,
                        "joint_failure": map_index % 3 == 0,
                    }
                )
        training, holdout = topology_holdout_maps(rows, holdout_fraction=0.25, seed=7)
        self.assertTrue(training)
        self.assertTrue(holdout)
        self.assertFalse(set(training).intersection(holdout))
        self.assertEqual(set(training).union(holdout), {f"maze_{index}" for index in range(12)})

    def test_reranking_ties_are_deterministic_and_prefer_smaller_graph(self) -> None:
        chosen = choose_candidate_indices(
            [("map_a", "0"), ("map_a", "0"), ("map_b", "0")],
            [0.2, 0.2, 0.1],
            [5, 3, 4],
            ["z", "a", "b"],
        )
        self.assertEqual(chosen, [1, 2])


if __name__ == "__main__":
    unittest.main()
