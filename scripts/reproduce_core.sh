#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

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

python3 experiments/run_submission_main_table.py
