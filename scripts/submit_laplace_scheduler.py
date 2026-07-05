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
    "thread_random": "thread,random,summary",
    "large_scale": "large_scale,summary",
    "amortized": "amortized,summary",
    "operator": "operator,summary",
    "full": "thread,random,operator,large_scale,amortized,summary",
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
        return ["thread_random", "large_scale", "amortized", "operator"]
    return args.suites


def default_amortized_shards(profile: str) -> int:
    if profile == "smoke":
        return 1
    return 32


def task_specs(args: argparse.Namespace) -> List[Tuple[str, str, Dict[str, object]]]:
    specs: List[Tuple[str, str, Dict[str, object]]] = []
    for suite in planned_suites(args):
        if suite == "amortized":
            shard_count = args.amortized_shards or default_amortized_shards(args.profile)
            if shard_count > 1:
                width = max(2, len(str(shard_count - 1)))
                for shard_index in range(shard_count):
                    label = f"amortized_shard_{shard_index:0{width}d}_of_{shard_count:0{width}d}"
                    specs.append(
                        (
                            label,
                            "amortized",
                            {
                                "LAPLACE_AMORTIZED_SHARD_INDEX": shard_index,
                                "LAPLACE_AMORTIZED_NUM_SHARDS": shard_count,
                            },
                        )
                    )
            else:
                specs.append((suite, suite, {}))
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
                args.threads,
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
            str(args.cpu),
            "--ram-mb",
            str(args.ram_mb),
            "--require-node",
            node,
            "--result-dir",
            str(remote_result_dir),
            "--local-result-dir",
            str(local_result_dir),
            "--allow-no-ckpt",
            "--allow-no-resume",
            "--allow-remote-large-data",
            "--allow-duplicate",
        ] + stage_args()
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
        choices=["all", "thread_random", "large_scale", "amortized", "operator", "full"],
    )
    parser.add_argument("--nodes", default=",".join(CPU_NODES))
    parser.add_argument("--threads", type=int, default=192)
    parser.add_argument("--cpu", type=int, default=128)
    parser.add_argument("--ram-mb", type=int, default=65536)
    parser.add_argument(
        "--amortized-shards",
        type=int,
        default=0,
        help="Number of amortized map/method shards; 0 chooses a profile default.",
    )
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
