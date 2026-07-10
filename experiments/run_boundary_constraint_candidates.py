#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch

from boundary_heatmap_gnn import (
    NODE_FEATURE_NAMES,
    BoundaryHeatmapGNN,
    boundary_metrics,
    load_state_dict_npz,
    select_boundary,
)
from boundary_constraint_student import PROPOSAL_KINDS, merge_duplicate_proposals
from run_boundary_heatmap_gnn import (
    build_sample,
    load_heatmap_rows,
    load_teacher_rows,
    model_outputs,
)
from run_option_algorithm_comparison import write_csv_all_fields


def proposal_row(
    sample,
    proposal_kind: str,
    prediction: Dict[str, object],
    forward_time_sec: float,
) -> Dict[str, object]:
    boundary = tuple(int(state) for state in prediction["boundary"])
    metrics = boundary_metrics(sample, boundary)
    return {
        "split": sample.split,
        "method": f"constraint_candidate_{proposal_kind}",
        "proposal_kind": proposal_kind,
        "proposal_aliases": json.dumps([proposal_kind]),
        "map_family": sample.map_family,
        "map_size": sample.map_size,
        "map": sample.name,
        "maze_seed": sample.maze_seed,
        "topology_seed": sample.teacher_row.get("topology_seed", sample.maze_seed),
        "goal_variant": sample.teacher_row.get("goal_variant", 0),
        "map_rows": sample.teacher_row.get("map_rows", ""),
        "slip": sample.slip,
        "n_states": sample.n_states,
        "teacher_feasible": sample.teacher_feasible,
        "teacher_boundary": json.dumps(sample.teacher_boundary),
        "predicted_boundary": json.dumps(boundary),
        "selected_states": json.dumps(prediction["selected_states"]),
        "predicted_extra_count": prediction["predicted_extra_count"],
        "score_margin": prediction["score_margin"],
        **metrics,
        "graph_encoding_time_sec": sample.graph_encoding_time_sec,
        "gnn_forward_time_sec": forward_time_sec,
        "student_selection_time_sec": sample.graph_encoding_time_sec + forward_time_sec,
        "teacher_selection_time_sec": sample.teacher_selection_time_sec,
        "selection_speedup_vs_teacher": sample.teacher_selection_time_sec
        / max(1e-12, sample.graph_encoding_time_sec + forward_time_sec),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a fixed cheap proposal family for constraint-aware reranking."
    )
    parser.add_argument(
        "--teacher-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_teacher_graphonly/"
            "boundary_heatmap_contexts.csv"
        ),
    )
    parser.add_argument(
        "--heatmap-teacher-csv",
        type=Path,
        default=Path(
            "experiments/output/boundary_heatmap_teacher_graphonly/"
            "boundary_heatmap_targets.csv"
        ),
    )
    parser.add_argument("--teacher-method", default="group_constrained_incremental")
    parser.add_argument(
        "--base-model-dir",
        type=Path,
        default=Path("experiments/models/boundary_heatmap_gnn_graphonly"),
    )
    parser.add_argument("--gamma", type=float, default=0.97)
    parser.add_argument("--probe-top-fraction", type=float, default=0.35)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/models/boundary_constraint_candidates"),
    )
    args = parser.parse_args()

    protocol = json.loads((args.base_model_dir / "protocol.json").read_text())
    selected_method = str(protocol["selected_student_method"])
    if not selected_method.startswith("gnn_seed_"):
        raise ValueError("Constraint candidates require a validation-selected single GNN.")
    selected_seed = int(selected_method.rsplit("_", 1)[1])
    weight_name = f"boundary_heatmap_seed{selected_seed}.npz"
    model = BoundaryHeatmapGNN(**protocol["model_config"])
    load_state_dict_npz(
        model,
        args.base_model_dir / weight_name,
        protocol["weight_key_maps"][weight_name],
    )
    device = torch.device("cpu")
    model.to(device)

    sample_args = argparse.Namespace(
        candidate_universe="all",
        fixed_basis_kinds=protocol["fixed_basis_kinds"],
        gamma=args.gamma,
        probe_top_fraction=args.probe_top_fraction,
        fixed_random_count=0,
        split_mode=str(protocol["split_mode"]),
        max_extra=int(protocol["model_config"]["max_extra"]),
    )
    teacher_rows = load_teacher_rows(args.teacher_csv, args.teacher_method)
    heatmaps = load_heatmap_rows(args.heatmap_teacher_csv)
    samples = [build_sample(row, sample_args, heatmaps) for row in teacher_rows]
    center = np.asarray(protocol["feature_center"], dtype=np.float32)
    scale = np.asarray(protocol["feature_scale"], dtype=np.float32)
    node_rows, count_rows, elapsed_rows = model_outputs(
        model,
        samples,
        center,
        scale,
        device=device,
        max_extra=sample_args.max_extra,
        measure_per_graph_latency=True,
    )

    feature_index = {name: index for index, name in enumerate(NODE_FEATURE_NAMES)}
    rows: List[Dict[str, object]] = []
    duplicate_contexts = 0
    dropped_duplicates = 0
    for sample, node_logits, count_logits, elapsed in zip(
        samples, node_rows, count_rows, elapsed_rows
    ):
        proposals = {
            "learned_count": select_boundary(sample, node_logits, count_logits),
            "top1": select_boundary(sample, node_logits, count_logits, forced_count=1),
            "top2": select_boundary(sample, node_logits, count_logits, forced_count=2),
            "top3": select_boundary(sample, node_logits, count_logits, forced_count=3),
        }
        nearest_scores = -sample.node_features[
            :, feature_index["distance_from_start"]
        ]
        proposals["nearest_start"] = select_boundary(
            sample, nearest_scores, count_logits, forced_count=1
        )
        raw_context_rows = [
            proposal_row(
                sample,
                proposal_kind,
                proposals[proposal_kind],
                forward_time_sec=elapsed,
            )
            for proposal_kind in PROPOSAL_KINDS
        ]
        context_rows, context_dropped = merge_duplicate_proposals(raw_context_rows)
        dropped_duplicates += context_dropped
        if context_dropped:
            duplicate_contexts += 1
        rows.extend(context_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_all_fields(args.out_dir / "constraint_candidates.csv", rows)
    for split in ("train", "validation", "test"):
        write_csv_all_fields(
            args.out_dir / f"constraint_candidates_{split}.csv",
            [row for row in rows if row["split"] == split],
        )
    summary = {
        "selected_base_method": selected_method,
        "n_contexts": len(samples),
        "n_proposals": len(rows),
        "proposal_kinds": list(PROPOSAL_KINDS),
        "duplicate_boundary_contexts": duplicate_contexts,
        "dropped_duplicate_proposals": dropped_duplicates,
        "split_rows": {
            split: sum(row["split"] == split for row in rows)
            for split in ("train", "validation", "test")
        },
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
