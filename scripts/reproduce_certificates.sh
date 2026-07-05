#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export LAPLACE_NUM_THREADS="${LAPLACE_NUM_THREADS:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-$LAPLACE_NUM_THREADS}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-$LAPLACE_NUM_THREADS}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-$LAPLACE_NUM_THREADS}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-$LAPLACE_NUM_THREADS}"

python3 experiments/run_adaptive_green_certification.py \
  --map-specs corridor:64,128 open_room:12 maze:13 four_rooms:11 \
  --boundary-methods endpoints turn_articulation \
  --adaptive-tail-tols 1e-3 1e-6 \
  --out-dir experiments/output/adaptive_green_certification

python3 experiments/run_weighted_spectral_certificate.py \
  --map-specs corridor:128 open_room:12 maze:13 four_rooms:11 \
  --boundary-methods endpoints \
  --out-dir experiments/output/weighted_spectral_certificate

python3 experiments/run_conditioned_weighted_certificate.py \
  --map-specs corridor:128 open_room:12 maze:13 four_rooms:11 \
  --boundary-methods endpoints \
  --out-dir experiments/output/conditioned_weighted_certificate

python3 experiments/run_submission_main_table.py
