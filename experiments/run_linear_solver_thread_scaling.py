#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Sequence


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        return
    fields: List[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    if not rows:
        return "_No rows._"

    def fmt(value: object) -> str:
        if isinstance(value, float):
            if not math.isfinite(value):
                return ""
            return f"{value:.4g}"
        return str(value)

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def worker(args: argparse.Namespace) -> None:
    import thread_limits  # noqa: F401
    import numpy as np

    rng = np.random.default_rng(args.seed)
    n = int(args.size)
    reps = int(args.reps)
    warmups = int(args.warmups)
    a = rng.standard_normal((n, n))
    a = a.T @ a + float(n) * np.eye(n)
    b = rng.standard_normal((n, max(1, int(args.rhs))))
    for _ in range(max(0, warmups)):
        np.linalg.solve(a, b)
    started = time.perf_counter()
    checksum = 0.0
    for _ in range(max(1, reps)):
        x = np.linalg.solve(a, b)
        checksum += float(x[0, 0])
    elapsed = time.perf_counter() - started
    print(
        json.dumps(
            {
                "threads": int(os.environ.get("LAPLACE_NUM_THREADS", "0") or 0),
                "size": n,
                "rhs": int(args.rhs),
                "reps": reps,
                "elapsed_sec": elapsed,
                "solve_per_sec": reps / max(1e-12, elapsed),
                "sec_per_solve": elapsed / max(1, reps),
                "checksum": checksum,
            },
            sort_keys=True,
        )
    )


def run_child(threads: int, size: int, rhs: int, reps: int, warmups: int, seed: int) -> Dict[str, object]:
    env = os.environ.copy()
    for key in [
        "LAPLACE_NUM_THREADS",
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "BLIS_NUM_THREADS",
    ]:
        env[key] = str(int(threads))
    cmd = [
        sys.executable,
        __file__,
        "--worker",
        "--size",
        str(int(size)),
        "--rhs",
        str(int(rhs)),
        "--reps",
        str(int(reps)),
        "--warmups",
        str(int(warmups)),
        "--seed",
        str(int(seed)),
    ]
    started = time.perf_counter()
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    row = json.loads(result.stdout.strip().splitlines()[-1])
    row["wall_sec"] = time.perf_counter() - started
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark OpenBLAS/NumPy dense solve versus thread count.")
    parser.add_argument("--threads", nargs="+", type=int, default=[1, 2, 4, 8, 16, 32])
    parser.add_argument("--sizes", nargs="+", type=int, default=[96, 192, 384])
    parser.add_argument("--rhs", type=int, default=8)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--size", type=int, default=128)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/output/linear_solver_thread_scaling"))
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return

    rows: List[Dict[str, object]] = []
    for size in args.sizes:
        baseline_sec = None
        for threads in args.threads:
            row = run_child(
                threads=threads,
                size=size,
                rhs=args.rhs,
                reps=args.reps,
                warmups=args.warmups,
                seed=args.seed,
            )
            if baseline_sec is None and int(threads) == 1:
                baseline_sec = float(row["sec_per_solve"])
            row["speedup_vs_1_thread"] = (
                baseline_sec / max(1e-12, float(row["sec_per_solve"]))
                if baseline_sec is not None
                else float("nan")
            )
            rows.append(row)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "linear_solver_thread_scaling.csv", rows)
    (args.out_dir / "linear_solver_thread_scaling.json").write_text(
        json.dumps(rows, indent=2) + "\n",
        encoding="utf-8",
    )
    columns = [
        "size",
        "rhs",
        "threads",
        "sec_per_solve",
        "solve_per_sec",
        "speedup_vs_1_thread",
        "wall_sec",
    ]
    lines = [
        "# Linear Solver Thread Scaling",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This benchmark isolates NumPy/OpenBLAS dense linear solves. It is CPU linear algebra, not CUDA training.",
        "",
        markdown_table(rows, columns),
        "",
        "Use this on CPU nodes to pick `LAPLACE_NUM_THREADS`; small matrices often prefer fewer threads, while large dense solves may benefit from more.",
    ]
    (args.out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out_dir}")


if __name__ == "__main__":
    main()
