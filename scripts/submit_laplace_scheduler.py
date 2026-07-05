#!/usr/bin/env python3
"""Submit Laplace-semi-MDP large CPU experiments through scheduler.py."""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE_ROOT = Path("/home/zhengliang01/scheduleurm_work/Laplace-semi-MDP")
DEFAULT_REMOTE_PYTHON = Path("/home/zhengliang01/scheduleurm_work/conda_envs/freqduet-cpu-py310/bin/python")
DEFAULT_SCHEDULER = Path.home() / ".claude/skills/scheduler/scheduler.py"
CPU_NODES = ["node001", "node002", "node003", "node004", "node005", "node006"]
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


SUITE_PARTS = {
    "thread_random": "thread,summary",
    "random_maze": "random,summary",
    "large_scale": "large_scale,summary",
    "amortized": "amortized,summary",
    "edge_reward": "edge_reward,summary",
    "option_frontier": "option_frontier,summary",
    "fair_frontier": "fair_frontier,summary",
    "submission_table": "submission_table,summary",
    "operator": "operator,summary",
    "full": "thread,random,operator,large_scale,amortized,edge_reward,option_frontier,summary",
}


def parse_csv(text: str) -> List[str]:
    return [item.strip() for item in str(text or "").split(",") if item.strip()]


def run_cmd(cmd: Sequence[object], dry_run: bool = False) -> str:
    printable = " ".join(shlex.quote(str(part)) for part in cmd)
    print("+", printable, flush=True)
    if dry_run:
        return ""
    return subprocess.check_output([str(part) for part in cmd], text=True, cwd=ROOT)


def stage_args() -> List[str]:
    out: List[str] = []
    for pattern in STAGE_EXCLUDES:
        out.extend(["--stage-exclude", pattern])
    return out


def shell_cmd(
    profile: str,
    suite: str,
    run_label: str,
    run_id: str,
    threads: int,
    remote_result_dir: Path,
    remote_python: Path,
    extra_env: Dict[str, object] | None = None,
) -> str:
    parts = SUITE_PARTS[suite]
    setup = [
        "set -e",
        "export LC_ALL=${LC_ALL:-C}",
        "export LANG=${LANG:-C}",
        f"export LAPLACE_NUM_THREADS={int(threads)}",
        f"export OMP_NUM_THREADS={int(threads)}",
        f"export OPENBLAS_NUM_THREADS={int(threads)}",
        f"export MKL_NUM_THREADS={int(threads)}",
        f"export NUMEXPR_NUM_THREADS={int(threads)}",
        f"export PYTHON_BIN={shlex.quote(str(remote_python))}",
        "export LAPLACE_USE_SYSTEM_PYTHON=1",
        f"export LAPLACE_RUN_PARTS={shlex.quote(parts)}",
        f"export LAPLACE_RUN_STAMP={shlex.quote(run_id + '_' + run_label)}",
        f"export LAPLACE_NODE_OUT_ROOT={shlex.quote(str(remote_result_dir))}",
    ]
    for key, value in (extra_env or {}).items():
        setup.append(f"export {key}={shlex.quote(str(value))}")
    setup.append(f"bash scripts/run_node_large_paper.sh {shlex.quote(profile)}")
    return "bash -lc " + shlex.quote("; ".join(setup))


def planned_suites(args: argparse.Namespace) -> List[str]:
    if args.suites == ["all"]:
        return ["thread_random", "random_maze", "large_scale", "amortized", "edge_reward", "option_frontier", "operator"]
    return args.suites


def default_large_scale_shards(profile: str) -> int:
    if profile == "smoke":
        return 1
    if profile == "xl":
        return 24
    return 12


def default_random_shards(profile: str) -> int:
    if profile == "smoke":
        return 1
    if profile == "xl":
        return 24
    return 16


def default_option_frontier_shards(profile: str) -> int:
    if profile == "smoke":
        return 1
    if profile == "xl":
        return 24
    return 12


def default_amortized_shards(profile: str) -> int:
    if profile == "smoke":
        return 1
    return 32


def default_edge_reward_shards(profile: str) -> int:
    if profile == "smoke":
        return 1
    return 16


def shard_range(start: int, stop: int, count: int) -> range:
    shard_start = max(0, start)
    shard_stop = count if stop < 0 else min(count, stop)
    return range(shard_start, max(shard_start, shard_stop))


def add_sharded_specs(
    specs: List[Tuple[str, str, Dict[str, object]]],
    suite: str,
    shard_count: int,
    shard_start: int,
    shard_stop: int,
    env_index: str,
    env_count: str,
) -> None:
    shards = shard_range(shard_start, shard_stop, shard_count)
    if not shards:
        return
    if shard_count > 1:
        width = max(2, len(str(shard_count - 1)))
        for shard_index in shards:
            label = f"{suite}_shard_{shard_index:0{width}d}_of_{shard_count:0{width}d}"
            specs.append((label, suite, {env_index: shard_index, env_count: shard_count}))
    else:
        specs.append((suite, suite, {}))


def task_specs(args: argparse.Namespace) -> List[Tuple[str, str, Dict[str, object]]]:
    specs: List[Tuple[str, str, Dict[str, object]]] = []
    for suite in planned_suites(args):
        if suite == "large_scale":
            add_sharded_specs(
                specs,
                suite,
                args.large_scale_shards or default_large_scale_shards(args.profile),
                args.large_scale_shard_start,
                args.large_scale_shard_stop,
                "LAPLACE_LARGE_SCALE_SHARD_INDEX",
                "LAPLACE_LARGE_SCALE_NUM_SHARDS",
            )
        elif suite == "random_maze":
            add_sharded_specs(
                specs,
                suite,
                args.random_shards or default_random_shards(args.profile),
                args.random_shard_start,
                args.random_shard_stop,
                "LAPLACE_RANDOM_SHARD_INDEX",
                "LAPLACE_RANDOM_NUM_SHARDS",
            )
        elif suite == "amortized":
            add_sharded_specs(
                specs,
                suite,
                args.amortized_shards or default_amortized_shards(args.profile),
                args.amortized_shard_start,
                args.amortized_shard_stop,
                "LAPLACE_AMORTIZED_SHARD_INDEX",
                "LAPLACE_AMORTIZED_NUM_SHARDS",
            )
        elif suite == "edge_reward":
            add_sharded_specs(
                specs,
                suite,
                args.edge_reward_shards or default_edge_reward_shards(args.profile),
                args.edge_reward_shard_start,
                args.edge_reward_shard_stop,
                "LAPLACE_EDGE_REWARD_SHARD_INDEX",
                "LAPLACE_EDGE_REWARD_NUM_SHARDS",
            )
        elif suite == "option_frontier":
            add_sharded_specs(
                specs,
                suite,
                args.option_frontier_shards or default_option_frontier_shards(args.profile),
                args.option_frontier_shard_start,
                args.option_frontier_shard_stop,
                "LAPLACE_OPTION_FRONTIER_SHARD_INDEX",
                "LAPLACE_OPTION_FRONTIER_NUM_SHARDS",
            )
        else:
            specs.append((suite, suite, {}))
    return specs


def submit(args: argparse.Namespace) -> List[str]:
    nodes = parse_csv(args.nodes)
    if not nodes:
        raise ValueError("At least one scheduler node is required.")
    specs = task_specs(args)
    run_id = args.run_id or time.strftime("%Y%m%d_%H%M%S")
    task_ids: List[str] = []

    for idx, (suite_label, suite_kind, extra_env) in enumerate(specs):
        if suite_kind not in SUITE_PARTS:
            known = ", ".join(sorted(SUITE_PARTS))
            raise ValueError(f"Unknown suite {suite_kind!r}. Known: all, {known}")
        node = nodes[idx % len(nodes)]
        remote_result_dir = (
            args.remote_root
            / "experiments"
            / "output"
            / "scheduler_large_runs"
            / run_id
            / suite_label
        )
        local_result_dir = ROOT / "experiments" / "output" / "scheduler_large_runs" / run_id / suite_label
        description = f"Laplace SMDP {args.profile} {suite_label} {run_id}"
        signature = f"Laplace-semi-MDP/{args.profile}/{run_id}/{suite_label}"
        if suite_kind == "amortized":
            task_threads = args.amortized_threads
            task_cpu = args.amortized_cpu
        elif suite_kind == "edge_reward":
            task_threads = args.edge_reward_threads
            task_cpu = args.edge_reward_cpu
        elif suite_kind == "large_scale":
            task_threads = args.large_scale_threads
            task_cpu = args.large_scale_cpu
        elif suite_kind == "random_maze":
            task_threads = args.random_threads
            task_cpu = args.random_cpu
        elif suite_kind == "option_frontier":
            task_threads = args.option_frontier_threads
            task_cpu = args.option_frontier_cpu
        else:
            task_threads = args.threads
            task_cpu = args.cpu
        cmd = [
            sys.executable,
            str(args.scheduler),
            "submit",
            "--description",
            description,
            "--cmd",
            shell_cmd(
                args.profile,
                suite_kind,
                suite_label,
                run_id,
                task_threads,
                remote_result_dir,
                args.remote_python,
                extra_env,
            ),
            "--cwd",
            str(ROOT),
            "--signature",
            signature,
            "--project",
            "Laplace-SMDP",
            "--vram",
            "0",
            "--cpu",
            str(task_cpu),
            "--ram-mb",
            str(args.ram_mb),
            "--require-node",
            node,
            "--result-dir",
            str(remote_result_dir),
            "--local-result-dir",
            str(local_result_dir),
            "--allow-no-resume",
            "--allow-remote-large-data",
            "--allow-duplicate",
        ]
        if suite_kind == "amortized" and args.scheduler_ckpt_dir:
            cmd.extend(["--ckpt-dir", str(remote_result_dir / "amortized_multitask")])
        else:
            cmd.append("--allow-no-ckpt")
        cmd += stage_args()
        out = run_cmd(cmd, dry_run=args.dry_run)
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
            parts = out.split()
            if len(parts) >= 2:
                task_ids.append(parts[1])

    if args.dispatch:
        run_cmd([sys.executable, str(args.scheduler), "dispatch"], dry_run=args.dry_run)
    return task_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheduler", type=Path, default=DEFAULT_SCHEDULER)
    parser.add_argument("--remote-root", type=Path, default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--remote-python", type=Path, default=DEFAULT_REMOTE_PYTHON)
    parser.add_argument("--profile", choices=["smoke", "large", "xl"], default="large")
    parser.add_argument("--run-id", default="")
    parser.add_argument(
        "--suites",
        nargs="+",
        default=["all"],
        choices=[
            "all",
            "thread_random",
            "random_maze",
            "large_scale",
            "amortized",
            "edge_reward",
            "option_frontier",
            "fair_frontier",
            "submission_table",
            "operator",
            "full",
        ],
    )
    parser.add_argument("--nodes", default=",".join(CPU_NODES))
    parser.add_argument("--threads", type=int, default=192)
    parser.add_argument("--cpu", type=int, default=128)
    parser.add_argument("--ram-mb", type=int, default=65536)
    parser.add_argument("--large-scale-threads", type=int, default=16)
    parser.add_argument("--large-scale-cpu", type=int, default=16)
    parser.add_argument("--random-threads", type=int, default=16)
    parser.add_argument("--random-cpu", type=int, default=16)
    parser.add_argument("--amortized-threads", type=int, default=16)
    parser.add_argument("--amortized-cpu", type=int, default=16)
    parser.add_argument("--edge-reward-threads", type=int, default=16)
    parser.add_argument("--edge-reward-cpu", type=int, default=16)
    parser.add_argument("--option-frontier-threads", type=int, default=16)
    parser.add_argument("--option-frontier-cpu", type=int, default=16)
    parser.add_argument(
        "--scheduler-ckpt-dir",
        action="store_true",
        help="Also declare amortized output dirs as scheduler ckpt dirs; slower because submit scans remote paths.",
    )
    parser.add_argument(
        "--large-scale-shards",
        type=int,
        default=0,
        help="Number of large-scale map/slip/method shards; 0 chooses a profile default.",
    )
    parser.add_argument("--large-scale-shard-start", type=int, default=0)
    parser.add_argument("--large-scale-shard-stop", type=int, default=-1)
    parser.add_argument(
        "--random-shards",
        type=int,
        default=0,
        help="Number of random-maze size/seed/slip/method shards; 0 chooses a profile default.",
    )
    parser.add_argument("--random-shard-start", type=int, default=0)
    parser.add_argument("--random-shard-stop", type=int, default=-1)
    parser.add_argument(
        "--amortized-shards",
        type=int,
        default=0,
        help="Number of amortized map/method shards; 0 chooses a profile default.",
    )
    parser.add_argument("--amortized-shard-start", type=int, default=0)
    parser.add_argument("--amortized-shard-stop", type=int, default=-1)
    parser.add_argument(
        "--edge-reward-shards",
        type=int,
        default=0,
        help="Number of edge reward/event kernel map/method shards; 0 chooses a profile default.",
    )
    parser.add_argument("--edge-reward-shard-start", type=int, default=0)
    parser.add_argument("--edge-reward-shard-stop", type=int, default=-1)
    parser.add_argument(
        "--option-frontier-shards",
        type=int,
        default=0,
        help="Number of option-frontier map/slip/method shards; 0 chooses a profile default.",
    )
    parser.add_argument("--option-frontier-shard-start", type=int, default=0)
    parser.add_argument("--option-frontier-shard-stop", type=int, default=-1)
    parser.add_argument("--dispatch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task_ids = submit(args)
    print({"task_ids": task_ids})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
