#!/usr/bin/env python3
"""Submit reviewer-P0 audit experiments without modifying the main scheduler wrapper."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Dict, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEDULER = Path.home() / ".claude/skills/scheduler/scheduler.py"
DEFAULT_REMOTE_ROOT = Path("/home/zhengliang01/scheduleurm_work/Laplace-semi-MDP")
DEFAULT_REMOTE_PYTHON = Path("/home/zhengliang01/scheduleurm_work/conda_envs/freqduet-cpu-py310/bin/python")
DEFAULT_SNAPSHOT_BASE = ROOT.parent / ".laplace_p0_snapshots"
DEFAULT_REMOTE_SNAPSHOT_BASE = DEFAULT_REMOTE_ROOT.parent / ".laplace_p0_snapshots"
DEFAULT_NODES = ["node001", "node002", "node003", "node004", "node005", "node006"]
DEFAULT_SUITES = ["planner", "abstraction", "solver_oracle", "general_env", "end_to_end", "budget_recovery"]
STAGE_EXCLUDES = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    ".venv-laplace",
    "venv",
    "reference",
    "proof/.lake",
    "node_logs",
    "experiments/output",
]


SuiteSpec = Tuple[str, int, int, int, str]

SUITE_ENTRYPOINTS = {
    "planner": "experiments/run_planner_baseline_comparison.py",
    "planner_paired": "experiments/run_planner_baseline_comparison.py",
    "abstraction": "experiments/run_abstraction_baseline_comparison.py",
    "solver_oracle": "experiments/run_solver_validity.py",
    "solver_oracle_four_rooms": "experiments/run_solver_validity.py",
    "general_env": "experiments/run_general_env_benchmark.py",
    "general_env_taxi": "experiments/run_general_env_benchmark.py",
    "end_to_end": "experiments/run_end_to_end_gap_decomposition.py",
    "end_to_end_converged": "experiments/run_end_to_end_gap_decomposition.py",
    "budget_recovery": "experiments/run_random_maze_budget_recovery.py",
    "budget_recovery_actual": "experiments/run_random_maze_budget_recovery.py",
    "budget_recovery_actual_extended": "experiments/run_random_maze_budget_recovery.py",
    "one_shot_random": "experiments/run_one_shot_rd_operator.py",
    "one_shot_random_reference": "experiments/run_one_shot_rd_operator.py",
    "one_shot_group_frontier": "experiments/run_one_shot_group_fd_frontier.py",
    "one_shot_xl": "experiments/run_one_shot_rd_operator.py",
    "boundary_heatmap_teacher": "experiments/run_boundary_heatmap_teacher.py",
    "boundary_heatmap_multifamily_teacher": "experiments/run_boundary_heatmap_teacher.py",
    "boundary_heatmap_downstream": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_heatmap_multifamily_downstream": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_heatmap_multifamily_validation": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_heatmap_multifamily_train": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_heatmap_graphonly_baselines": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_constraint_train": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_constraint_validation": "experiments/run_boundary_heatmap_downstream.py",
    "boundary_constraint_test": "experiments/run_boundary_heatmap_downstream.py",
}


def suite_specs(remote_python: Path) -> Dict[str, SuiteSpec]:
    python = shlex.quote(str(remote_python))
    return {
        "planner": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_planner_baseline_comparison.py "
            "--map-specs corridor:256,512,1024 open_room:24,32 four_rooms:21,31 maze:21,31 "
            "--slips 0 0.05 0.1 --methods sparse_vectorized_vi gauss_seidel_vi prioritized_sweeping "
            "--repeats 5 --warmups 1 --shard-index {index} --num-shards {count} --resume "
            "--continue-on-error --out-dir {out}/planner_baseline_comparison"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 108, 2, 4096, "planner"),
        "planner_paired": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_planner_baseline_comparison.py "
            "--map-specs corridor:256,512,1024 open_room:24,32 four_rooms:21,31 maze:21,31 "
            "--slips 0 0.05 0.1 --methods sparse_vectorized_vi gauss_seidel_vi prioritized_sweeping "
            "--repeats 5 --warmups 1 --shard-unit case_repeat "
            "--shard-index {index} --num-shards {count} --resume --continue-on-error "
            "--out-dir {out}/planner_baseline_comparison"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 135, 2, 2048, "planner_paired"),
        "abstraction": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_abstraction_baseline_comparison.py "
            "--map-specs corridor:32,64 open_room:9,12 four_rooms:9,11 maze:9,11 "
            "--slips 0 0.05 0.1 --budget-fracs 0.05 0.1 0.2 0.35 --repeats 5 "
            "--shard-index {index} --num-shards {count} --resume "
            "--out-dir {out}/abstraction_baseline_comparison"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 72, 2, 8192, "abstraction"),
        "solver_oracle": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_solver_validity.py "
            "--map-specs open_room:5 four_rooms:7 maze:7 --random-maze-sizes 5 "
            "--random-maze-seeds 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 "
            "--slips 0 0.05 0.1 --budget-fracs 0.1 0.25 0.5 "
            "--fixed-basis-kinds turn_articulation coverage_sqrt --fixed-random-count 0 "
            "--oracle-pool-mode all --max-oracle-candidates 12 --max-extra-splits 2 "
            "--solvers operator actual_refine --beam-widths 1 2 4 8 --beam-expand 6 "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/solver_validity"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 108, 2, 4096, "solver_oracle"),
        "solver_oracle_four_rooms": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_solver_validity.py "
            "--map-specs four_rooms:7 --slips 0 0.05 0.1 --budget-fracs 0.1 0.25 0.5 "
            "--fixed-basis-kinds turn_articulation coverage_sqrt --fixed-random-count 0 "
            "--oracle-pool-mode all --max-oracle-candidates 17 --max-extra-splits 2 "
            "--solvers operator actual_refine --beam-widths 1 2 4 8 --beam-expand 6 "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/solver_validity"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 9, 2, 4096, "solver_oracle_four_rooms"),
        "general_env": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_general_env_benchmark.py "
            "--env-specs toytext:FrozenLake8x8-v1 toytext:CliffWalking-v1 "
            "minigrid:MiniGrid-FourRooms-v0 minigrid:MiniGrid-DoorKey-5x5-v0 "
            "minigrid:MiniGrid-MultiRoom-N2-S4-v0 pointmaze:umaze:3 toytext:Taxi-v4 "
            "--seeds 0 1 2 3 4 --methods endpoints green_group_rd "
            "--option-modes primitive boundary_targeted --target-counts 8 16 32 "
            "--shard-index {index} --num-shards {count} --resume "
            "--out-dir {out}/general_env_benchmark"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 35, 4, 8192, "general_env"),
        "general_env_taxi": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_general_env_benchmark.py "
            "--env-specs toytext:Taxi-v4 --seeds 0 1 2 3 4 "
            "--methods endpoints green_group_rd --option-modes primitive boundary_targeted "
            "--target-counts 8 16 32 --shard-index {index} --num-shards {count} --resume "
            "--out-dir {out}/general_env_benchmark"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 5, 4, 8192, "general_env_taxi"),
        "end_to_end": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_end_to_end_gap_decomposition.py "
            "--map-specs corridor:16,32,64 open_room:7,9 four_rooms:7,9 maze:9,11 "
            "--slips 0 0.05 0.1 --methods endpoints turn_articulation graph_rd_surrogate_joint "
            "--truncation-steps 32 --planning-iterations 8 --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/end_to_end_gap_decomposition"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 36, 2, 4096, "end_to_end"),
        "end_to_end_converged": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_end_to_end_gap_decomposition.py "
            "--map-specs corridor:16,32,64 open_room:7,9 four_rooms:7,9 maze:9,11 "
            "--slips 0 0.05 0.1 --methods endpoints turn_articulation graph_rd_surrogate_joint "
            "--truncation-steps 256 --planning-iterations 256 --config-label converged_k256_i256 "
            "--shard-index {index} --num-shards {count} --resume --continue-on-error "
            "--out-dir {out}/end_to_end_gap_decomposition"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 36, 2, 2048, "end_to_end_converged"),
        "budget_recovery": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_random_maze_budget_recovery.py "
            "--contexts 15:0:0.05:3 15:4:0.05:2 15:8:0.05:3 15:0:0.1:3 "
            "15:4:0.1:3 19:3:0.05:3 19:3:0.1:3 "
            "--max-splits-values 5 8 12 16 --budget-fracs 0.25 "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/random_maze_budget_recovery"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 7, 2, 4096, "budget_recovery"),
        "budget_recovery_actual": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_random_maze_budget_recovery.py "
            "--contexts 15:0:0.05:3 15:4:0.05:2 15:8:0.05:3 15:0:0.1:3 "
            "15:4:0.1:3 19:3:0.05:3 19:3:0.1:3 "
            "--methods actual_refine --max-splits-values 5 --budget-fracs 0.25 "
            "--beam-width 4 --beam-expand 6 --shard-index {index} --num-shards {count} "
            "--continue-on-error --out-dir {out}/random_maze_budget_recovery"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 7, 2, 2048, "budget_recovery_actual"),
        "budget_recovery_actual_extended": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_random_maze_budget_recovery.py "
            "--contexts 15:4:0.1:3 --methods actual_refine --max-splits-values 8 12 16 "
            "--budget-fracs 0.25 --beam-width 4 --beam-expand 6 --shard-unit job "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/random_maze_budget_recovery"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 3, 2, 2048, "budget_recovery_actual_extended"),
        "one_shot_random": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_one_shot_rd_operator.py "
            "--map-specs --random-maze-sizes 11 15 19 "
            "--maze-seeds 0 1 2 3 4 5 6 7 8 9 10 11 --slips 0 0.05 0.1 "
            "--thresholds 0.15 0.75 --baselines --operator-truncation-steps 256 "
            "--final-first-hit-steps 512 --planner-repeats 1 "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/one_shot_rd_operator_random"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 108, 2, 4096, "one_shot_random"),
        "one_shot_random_reference": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_one_shot_rd_operator.py "
            "--map-specs --random-maze-sizes 11 15 --maze-seeds 0 1 2 3 4 "
            "--slips 0.05 0.1 --thresholds 0.15 --baselines graph_rd_surrogate_joint "
            "--operator-truncation-steps 256 --final-first-hit-steps 512 "
            "--local-horizon 1e9 --planner-repeats 1 "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/one_shot_rd_operator_random_reference"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 20, 2, 4096, "one_shot_random_reference"),
        "one_shot_group_frontier": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_one_shot_group_fd_frontier.py "
            "--map-specs open_room:12 four_rooms:11 maze:13 --slips 0.05 "
            "--top-m-values 0 1 2 3 4 5 6 8 10 12 16 20 24 "
            "--shard-index {index} --num-shards {count} "
            "--out-dir {out}/one_shot_group_fd_frontier"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 3, 2, 4096, "one_shot_group_frontier"),
        "one_shot_xl": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_one_shot_rd_operator.py "
            "--map-specs corridor:256 corridor:512 corridor:1024 open_room:24 open_room:32 "
            "four_rooms:21 four_rooms:31 maze:21 maze:31 --slips 0 0.05 0.1 "
            "--thresholds 0.15 --baselines --operator-truncation-steps 256 "
            "--final-first-hit-steps 2048 --local-horizon 1e9 --planner-repeats 1 "
            "--shard-index {index} --num-shards {count} --continue-on-error "
            "--out-dir {out}/one_shot_rd_operator_xl_end_to_end"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 27, 2, 8192, "one_shot_xl"),
        "boundary_heatmap_teacher": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_teacher.py "
            "--sizes 11 13 15 17 19 --maze-seeds 0 1 2 3 4 5 6 7 8 9 10 11 "
            "--slips 0 0.05 0.1 --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/boundary_heatmap_teacher"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 18, 2, 4096, "boundary_heatmap_teacher"),
        "boundary_heatmap_multifamily_teacher": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_teacher.py "
            "--map-specs corridor:16,32,64,128 open_room:7,9,11,13 "
            "four_rooms:7,9,11,13 maze:9,11,13,15 braid_maze:9,11,13,15 "
            "--topology-seeds 0 1 2 3 4 5 --goal-variants 2 --slips 0 0.05 0.1 "
            "--fixed-random-count 0 --full-teacher --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/boundary_heatmap_teacher"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 180, 2, 4096, "boundary_heatmap_multifamily_teacher"),
        "boundary_heatmap_downstream": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--shard-index {index} --num-shards {count} --resume --continue-on-error "
            "--out-dir {out}/boundary_heatmap_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 60, 2, 4096, "boundary_heatmap_downstream"),
        "boundary_heatmap_multifamily_downstream": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_test_predictions.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_test_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} --resume --continue-on-error "
            "--out-dir {out}/boundary_heatmap_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 90, 2, 4096, "boundary_heatmap_multifamily_downstream"),
        "boundary_heatmap_multifamily_validation": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_validation_predictions.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_validation_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} --resume --continue-on-error "
            "--out-dir {out}/boundary_heatmap_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 90, 2, 4096, "boundary_heatmap_multifamily_validation"),
        "boundary_heatmap_multifamily_train": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_train_predictions.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_train_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} --resume --continue-on-error "
            "--out-dir {out}/boundary_heatmap_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 180, 2, 4096, "boundary_heatmap_multifamily_train"),
        "boundary_heatmap_graphonly_baselines": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_heatmap_gnn_graphonly/test_baseline_predictions.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_test_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/boundary_heatmap_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 180, 2, 4096, "boundary_heatmap_graphonly_baselines"),
        "boundary_constraint_train": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_constraint_candidates/constraint_candidates_train.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_train_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/boundary_constraint_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 180, 2, 2048, "boundary_constraint_train"),
        "boundary_constraint_validation": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_constraint_candidates/constraint_candidates_validation.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_validation_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/boundary_constraint_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 90, 2, 2048, "boundary_constraint_validation"),
        "boundary_constraint_test": ((
            "LAPLACE_NUM_THREADS=1 {python} experiments/run_boundary_heatmap_downstream.py "
            "--predictions-csv experiments/models/boundary_constraint_candidates/constraint_candidates_test.csv "
            "--teacher-csv experiments/models/boundary_heatmap_gnn_graphonly/selected_test_teacher.csv "
            "--fixed-random-count 0 --shard-index {index} --num-shards {count} "
            "--resume --continue-on-error --out-dir {out}/boundary_constraint_downstream"
        ).format(python=python, index="{index}", count="{count}", out="{out}"), 90, 2, 2048, "boundary_constraint_test"),
    }


def parse_csv(text: str) -> List[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def run_with_input(cmd: Sequence[object], payload: str, dry_run: bool) -> str:
    print("+", " ".join(shlex.quote(str(part)) for part in cmd), f"< {len(payload.splitlines())} tasks", flush=True)
    if dry_run:
        print(payload, end="")
        return ""
    return subprocess.check_output([str(part) for part in cmd], input=payload, text=True, cwd=ROOT)


def workspace_fingerprint() -> str:
    digest = hashlib.sha256()
    excluded = [Path(item) for item in STAGE_EXCLUDES]
    listed = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
    )
    for raw_relative in sorted(item for item in listed.split(b"\0") if item):
        relative = Path(raw_relative.decode("utf-8"))
        if any(relative == item or item in relative.parents for item in excluded):
            continue
        path = ROOT / relative
        if not path.is_file():
            continue
        digest.update(str(relative).encode("utf-8"))
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def create_snapshot(snapshot_root: Path, fingerprint: str, run_id: str) -> None:
    snapshot_root.mkdir(parents=True, exist_ok=True)
    command = ["rsync", "-a", "--delete", "--delete-excluded"]
    for pattern in STAGE_EXCLUDES:
        command.extend(["--exclude", f"/{pattern.rstrip('/')}/"])
    command.extend([f"{ROOT}/", f"{snapshot_root}/"])
    subprocess.run(command, check=True)
    (snapshot_root / ".scheduleurm_snapshot.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "source": str(ROOT),
                "fingerprint": fingerprint,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def strict_shell_command(
    *,
    inner: str,
    remote_project: Path,
    remote_out: Path,
    entrypoint: str,
    run_id: str,
    suite: str,
    label: str,
    fingerprint: str,
) -> str:
    success = remote_out / "_SUCCESS.json"
    failed = remote_out / "_FAILED.exitcode"
    payload = json.dumps(
        {
            "run_id": run_id,
            "suite": suite,
            "label": label,
            "fingerprint": fingerprint,
        },
        sort_keys=True,
    )
    body = " ".join(
        [
            "set -euo pipefail;",
            "export LC_ALL=C; export LANG=C;",
            f"cd {shlex.quote(str(remote_project))};",
            f"test -f {shlex.quote(entrypoint)};",
            "test -f .scheduleurm_snapshot.json;",
            f"mkdir -p {shlex.quote(str(remote_out))};",
            f"rm -f {shlex.quote(str(success))} {shlex.quote(str(failed))};",
            f"trap 'rc=$?; printf \"%s\\n\" \"$rc\" > {shlex.quote(str(failed))}; exit \"$rc\"' EXIT;",
            inner + ";",
            "trap - EXIT;",
            f"printf '%s\\n' {shlex.quote(payload)} > {shlex.quote(str(success))};",
        ]
    )
    return "bash -lc " + shlex.quote(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheduler", type=Path, default=DEFAULT_SCHEDULER)
    parser.add_argument("--remote-root", type=Path, default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--snapshot-base", type=Path, default=DEFAULT_SNAPSHOT_BASE)
    parser.add_argument("--remote-snapshot-base", type=Path, default=DEFAULT_REMOTE_SNAPSHOT_BASE)
    parser.add_argument("--no-immutable-snapshot", action="store_true")
    parser.add_argument("--reuse-existing-snapshot", action="store_true")
    parser.add_argument("--remote-python", type=Path, default=DEFAULT_REMOTE_PYTHON)
    parser.add_argument("--run-id", default="")
    parser.add_argument(
        "--suites",
        nargs="+",
        choices=["all", "planner", "planner_paired", "abstraction", "solver_oracle", "solver_oracle_four_rooms", "general_env", "general_env_taxi", "end_to_end", "end_to_end_converged", "budget_recovery", "budget_recovery_actual", "budget_recovery_actual_extended", "one_shot_random", "one_shot_random_reference", "one_shot_group_frontier", "one_shot_xl", "boundary_heatmap_teacher", "boundary_heatmap_multifamily_teacher", "boundary_heatmap_downstream", "boundary_heatmap_multifamily_downstream", "boundary_heatmap_multifamily_validation", "boundary_heatmap_multifamily_train", "boundary_heatmap_graphonly_baselines", "boundary_constraint_train", "boundary_constraint_validation", "boundary_constraint_test"],
        default=["all"],
    )
    parser.add_argument("--nodes", default=",".join(DEFAULT_NODES))
    parser.add_argument("--dispatch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--shard-limit", type=int, default=0, help="Submit only the first N shards per suite (smoke testing).")
    parser.add_argument("--shard-indices", default="", help="Comma-separated shard indices to submit from each selected suite.")
    parser.add_argument("--intent-ttl", type=int, default=900)
    args = parser.parse_args()

    run_id = args.run_id or f"p0_audits_{time.strftime('%Y%m%d_%H%M%S')}"
    nodes = parse_csv(args.nodes)
    if not nodes:
        raise ValueError("At least one node is required.")
    if args.no_immutable_snapshot and args.reuse_existing_snapshot:
        raise ValueError("--no-immutable-snapshot and --reuse-existing-snapshot are mutually exclusive.")
    specs_by_suite = suite_specs(args.remote_python)
    suites = list(DEFAULT_SUITES) if args.suites == ["all"] else args.suites
    fingerprint = workspace_fingerprint()
    local_projects: Dict[str, Path] = {}
    remote_projects: Dict[str, Path] = {}
    reused_fingerprints: set[str] = set()
    for node in nodes:
        if args.no_immutable_snapshot:
            local_projects[node] = ROOT
            remote_projects[node] = args.remote_root
            continue
        local_project = args.snapshot_base / run_id / node / ROOT.name
        remote_project = args.remote_snapshot_base / run_id / node / ROOT.name
        if args.reuse_existing_snapshot:
            manifest_path = local_project / ".scheduleurm_snapshot.json"
            if not manifest_path.exists():
                raise FileNotFoundError(f"Missing reusable snapshot manifest: {manifest_path}")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            reused_fingerprints.add(str(manifest["fingerprint"]))
        elif not args.dry_run:
            create_snapshot(local_project, fingerprint, run_id)
        local_projects[node] = local_project
        remote_projects[node] = remote_project
    if reused_fingerprints:
        if len(reused_fingerprints) != 1:
            raise RuntimeError(f"Reusable node snapshots have mixed fingerprints: {reused_fingerprints}")
        fingerprint = reused_fingerprints.pop()

    tasks: List[dict] = []
    task_index = 0
    requested_shards = {int(item) for item in parse_csv(args.shard_indices)}
    for suite in suites:
        command_template, shard_count, cpu, ram_mb, label_prefix = specs_by_suite[suite]
        width = max(2, len(str(shard_count - 1)))
        if requested_shards:
            invalid = sorted(index for index in requested_shards if not 0 <= index < shard_count)
            if invalid:
                raise ValueError(f"Shard indices out of range for {suite}: {invalid}")
            selected_shards = sorted(requested_shards)
        else:
            selected_shards = range(shard_count if args.shard_limit <= 0 else min(shard_count, args.shard_limit))
        for shard_index in selected_shards:
            label = f"{label_prefix}_shard_{shard_index:0{width}d}_of_{shard_count:0{width}d}"
            node = nodes[task_index % len(nodes)]
            remote_project = remote_projects[node]
            remote_out = remote_project / "experiments/output/scheduler_p0_audits" / run_id / label
            local_out = ROOT / "experiments/output/scheduler_p0_audits" / run_id / label
            inner = command_template.format(index=shard_index, count=shard_count, out=shlex.quote(str(remote_out)))
            cmd = strict_shell_command(
                inner=inner,
                remote_project=remote_project,
                remote_out=remote_out,
                entrypoint=SUITE_ENTRYPOINTS[suite],
                run_id=run_id,
                suite=suite,
                label=label,
                fingerprint=fingerprint,
            )
            tasks.append(
                {
                    "description": f"Laplace reviewer P0 {label} {run_id}",
                    "cmd": cmd,
                    "cwd": str(local_projects[node]),
                    "signature": f"Laplace-semi-MDP/p0/{run_id}/{label}",
                    "project": "Laplace-SMDP",
                    "vram": 0,
                    "cpu": cpu,
                    "ram_mb": ram_mb,
                    "require_node": node,
                    "result_dir": str(remote_out),
                    "local_result_dir": str(local_out),
                    "allow_no_resume": True,
                    "allow_no_ckpt": True,
                    "allow_remote_large_data": True,
                    # Some audit suite labels contain "train" because they
                    # consume the training split.  They only evaluate frozen
                    # boundaries and intentionally run on CPU nodes.
                    "allow_cpu_training": True,
                    "cpu_training_justification": "Frozen downstream audit; no model training is performed.",
                    "allow_duplicate": True,
                    "stage_excludes": STAGE_EXCLUDES,
                }
            )
            task_index += 1

    payload = "".join(json.dumps(task, ensure_ascii=False) + "\n" for task in tasks)
    output = run_with_input(
        [
            sys.executable,
            str(args.scheduler),
            "submit-jsonl",
            "--stdin",
            "--trusted",
            "--json",
            "--intent-label",
            f"laplace-{run_id}",
            "--intent-ttl",
            str(args.intent_ttl),
        ],
        payload,
        args.dry_run,
    )
    if output:
        print(output, end="" if output.endswith("\n") else "\n")
    if args.dispatch:
        command = [sys.executable, str(args.scheduler), "dispatch", "--lock-timeout", "60"]
        subprocess.run(command, cwd=ROOT, check=True)
    print(f"run_id={run_id} tasks={len(tasks)} fingerprint={fingerprint[:16]}")


if __name__ == "__main__":
    main()
