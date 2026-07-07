#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_HOST="${REMOTE_HOST:-zhengliang01@202.197.46.16}"
PROXY_JUMP="${PROXY_JUMP:-jtl110gpu2}"
REMOTE_ROOT="${REMOTE_ROOT:-/home/zhengliang01/scheduleurm_work/Laplace-semi-MDP}"
REMOTE_PYTHON="${REMOTE_PYTHON:-/home/zhengliang01/scheduleurm_work/conda_envs/freqduet-cpu-py310/bin/python}"

SSH_OPTS=(
  -o ConnectTimeout=30
  -o ServerAliveInterval=10
  -o ServerAliveCountMax=6
  -o BatchMode=yes
  -J "$PROXY_JUMP"
)
SSH=(ssh "${SSH_OPTS[@]}" "$REMOTE_HOST")
RSYNC_RSH="ssh -o ConnectTimeout=30 -o ServerAliveInterval=10 -o ServerAliveCountMax=6 -o BatchMode=yes -J $PROXY_JUMP"

echo "Staging Laplace-semi-MDP to $REMOTE_HOST:$REMOTE_ROOT"
"${SSH[@]}" "mkdir -p '$REMOTE_ROOT'"

rsync -az --delete -e "$RSYNC_RSH" \
  --exclude='.git/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='.mypy_cache/' \
  --exclude='.ruff_cache/' \
  --exclude='.venv/' \
  --exclude='.venv-laplace/' \
  --exclude='venv/' \
  --exclude='reference/' \
  --exclude='proof/.lake/' \
  --exclude='node_logs/' \
  --exclude='experiments/output/' \
  "$ROOT"/ "$REMOTE_HOST:$REMOTE_ROOT"/

"${SSH[@]}" "cd '$REMOTE_ROOT' && bash -n scripts/setup_node_env.sh scripts/run_node_large_paper.sh && '$REMOTE_PYTHON' -m py_compile scripts/submit_laplace_scheduler.py experiments/run_node_large_summary.py experiments/run_large_scale_compression.py experiments/run_random_maze_generalization.py experiments/run_option_baseline_frontier.py experiments/run_fair_budget_frontier.py experiments/run_submission_main_table.py experiments/run_amortized_multitask.py experiments/run_edge_reward_kernel_multitask.py experiments/run_hybrid_surrogate_refine.py experiments/aggregate_amortized_shards.py experiments/aggregate_scheduler_shards.py"

if [ "${LAPLACE_STAGE_SETUP:-1}" = "1" ]; then
  "${SSH[@]}" "cd '$REMOTE_ROOT' && PYTHON_BIN='$REMOTE_PYTHON' LAPLACE_USE_SYSTEM_PYTHON=1 bash scripts/setup_node_env.sh"
fi

echo "Remote staged at $REMOTE_ROOT"
