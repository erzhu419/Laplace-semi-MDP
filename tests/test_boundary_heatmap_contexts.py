from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from bellman_kron import GridWorld  # noqa: E402
from boundary_heatmap_contexts import (  # noqa: E402
    context_fields,
    expand_contexts,
    rows_from_record,
)
from compression_experiment_utils import braided_maze_rows, dfs_maze_rows  # noqa: E402


def cycle_rank(rows: tuple[str, ...]) -> int:
    grid = GridWorld(rows)
    edges = {
        tuple(sorted((state, grid.next_state(state, action))))
        for state in range(grid.n_states)
        for action in grid.legal_actions(state)
        if grid.next_state(state, action) != state
    }
    return len(edges) - grid.n_states + 1


class BoundaryHeatmapContextTests(unittest.TestCase):
    def test_braiding_adds_cycles_without_changing_endpoints(self) -> None:
        tree = dfs_maze_rows(11, seed=3)
        braided = braided_maze_rows(11, seed=3)
        self.assertEqual(cycle_rank(tree), 0)
        self.assertGreater(cycle_rank(braided), 0)
        self.assertEqual(sum(row.count("S") for row in braided), 1)
        self.assertEqual(sum(row.count("G") for row in braided), 1)

    def test_multifamily_contexts_hold_out_complete_sizes(self) -> None:
        contexts = expand_contexts(
            ["open_room:5,7,9", "maze:7,9,11"],
            topology_seeds=[0, 1],
            goal_variants=2,
        )
        self.assertEqual(len(contexts), 18)
        for context in contexts:
            if context.map_family == "open_room":
                expected = {5: "train", 7: "validation", 9: "test"}[context.map_size]
            else:
                expected = {7: "train", 9: "validation", 11: "test"}[context.map_size]
            self.assertEqual(context.split, expected)

    def test_serialized_rows_round_trip(self) -> None:
        context = expand_contexts(
            ["four_rooms:7,9,11"],
            topology_seeds=[0],
            goal_variants=2,
        )[1]
        fields = context_fields(context)
        self.assertEqual(rows_from_record(fields), context.rows)
        self.assertIsInstance(json.loads(str(fields["map_rows"])), list)


if __name__ == "__main__":
    unittest.main()
