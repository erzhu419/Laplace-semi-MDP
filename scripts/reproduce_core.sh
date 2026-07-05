#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export LAPLACE_NUM_THREADS="${LAPLACE_NUM_THREADS:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-$LAPLACE_NUM_THREADS}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-$LAPLACE_NUM_THREADS}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-$LAPLACE_NUM_THREADS}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-$LAPLACE_NUM_THREADS}"

python3 experiments/run_core_benchmark.py \
  --map-specs corridor:16,32 open_room:7 four_rooms:7 maze:9 \
  --slips 0.0 0.05 \
  --n-rollouts 20 \
  --out-dir experiments/output/core_benchmark

python3 experiments/run_large_scale_compression.py \
  --map-specs corridor:64,128 open_room:12 maze:13 \
  --methods endpoints turn_articulation \
  --slip 0.05 \
  --first-hit-mode adaptive \
  --first-hit-truncation-steps 512 \
  --first-hit-tail-tol 1e-6 \
  --out-dir experiments/output/large_scale_compression_adaptive

python3 experiments/run_solver_validity.py \
  --map-specs open_room:5 four_rooms:7 maze:9 \
  --beam-widths 1 2 4 \
  --max-extra-splits 2 \
  --max-oracle-candidates 6 \
  --out-dir experiments/output/solver_validity

python3 experiments/run_group_constrained_adaptive_table.py \
  --map-specs open_room:12 four_rooms:11 maze:13 \
  --slips 0.0 0.05 \
  --methods endpoints group_constrained group_constrained_incremental \
  --out-dir experiments/output/group_constrained_adaptive_large

python3 experiments/run_random_maze_generalization.py \
  --sizes 9 \
  --maze-seeds 0 1 \
  --slips 0.05 \
  --methods endpoints group_constrained_operator group_constrained_incremental \
  --out-dir experiments/output/random_maze_generalization

python3 experiments/run_group_incremental_semantic_diff.py \
  --out-dir experiments/output/group_incremental_semantic_diff

python3 experiments/run_discovery_profile_cache.py \
  --map-specs open_room:7 four_rooms:7 maze:9 \
  --slips 0.0 0.05 \
  --out-dir experiments/output/discovery_profile_cache

python3 experiments/run_incremental_green_update_check.py \
  --map-specs open_room:7 four_rooms:7 maze:9 \
  --slips 0.0 0.05 \
  --out-dir experiments/output/incremental_green_update

python3 experiments/run_fair_budget_frontier.py \
  --out-dir experiments/output/fair_budget_frontier

python3 experiments/run_edge_reward_kernel_multitask.py \
  --map-specs corridor:128 open_room:16 four_rooms:15 maze:17 \
  --methods endpoints turn_articulation \
  --task-counts 1 5 10 \
  --max-tasks 10 \
  --continue-on-error \
  --out-dir experiments/output/edge_reward_kernel_multitask

python3 experiments/plot_graph_abstraction_figures.py \
  --out-dir experiments/output/graph_abstraction_figures

python3 experiments/run_theorem_experiment_bridge.py \
  --out-dir experiments/output/theorem_experiment_bridge

python3 experiments/run_submission_main_table.py
