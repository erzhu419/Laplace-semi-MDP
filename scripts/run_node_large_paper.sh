#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PROFILE="${1:-large}"
STAMP="${LAPLACE_RUN_STAMP:-$(date +%Y%m%d_%H%M%S)}"
THREADS="${LAPLACE_NUM_THREADS:-$(nproc)}"
OUT_ROOT="${LAPLACE_NODE_OUT_ROOT:-experiments/output/node_large_runs/$STAMP}"
VENV="${LAPLACE_VENV:-$PWD/.venv-laplace}"

export LAPLACE_NUM_THREADS="$THREADS"
export OMP_NUM_THREADS="$THREADS"
export OPENBLAS_NUM_THREADS="$THREADS"
export MKL_NUM_THREADS="$THREADS"
export NUMEXPR_NUM_THREADS="$THREADS"
export VECLIB_MAXIMUM_THREADS="$THREADS"
export BLIS_NUM_THREADS="$THREADS"

if [ "${LAPLACE_SETUP:-1}" = "1" ]; then
  bash scripts/setup_node_env.sh
fi

PYTHON_CMD="${PYTHON_BIN:-python3}"
if [ "${LAPLACE_USE_SYSTEM_PYTHON:-0}" != "1" ] && [ -d "$VENV" ]; then
  source "$VENV/bin/activate"
  PYTHON_CMD="python"
fi

mkdir -p "$OUT_ROOT"
RUN_PARTS="${LAPLACE_RUN_PARTS:-thread,random,operator,large_scale,amortized,edge_reward,option_frontier,summary}"

has_part() {
  case ",$RUN_PARTS," in
    *",$1,"*) return 0 ;;
    *) return 1 ;;
  esac
}

case "$PROFILE" in
  smoke)
    THREAD_GRID=(1 2 4)
    THREAD_SIZES=(96)
    RANDOM_SIZES=(9)
    RANDOM_SEEDS=(0)
    RANDOM_SLIPS=(0.05)
    RANDOM_METHODS=(endpoints group_constrained_incremental)
    LARGE_MAP_SPECS=(corridor:64 open_room:12 maze:13)
    LARGE_SLIPS=(0.05)
    LARGE_METHODS=(endpoints graph_rd_surrogate_joint betweenness_sqrt)
    AMORTIZED_MAP_SPECS=(corridor:64 open_room:10 maze:13)
    AMORTIZED_COUNTS=(1 5 10)
    AMORTIZED_MAX_TASKS=10
    EDGE_REWARD_MAP_SPECS=(corridor:64 open_room:10 maze:13)
    EDGE_REWARD_METHODS=(endpoints turn_articulation)
    EDGE_REWARD_COUNTS=(1 5 10)
    EDGE_REWARD_MAX_TASKS=10
    OPTION_MAP_SPECS=(maze:9)
    OPTION_SLIPS=(0.05)
    OPTION_K_VALUES=(4 8)
    HYBRID_MAP_SPECS=(open_room:7)
    HYBRID_SLIPS=(0.0)
    HYBRID_TOP_K=(2)
    HYBRID_METHODS=(endpoints incremental_group_rd surrogate_topk_certified_refine)
    HYBRID_TOPK_MAP_SPECS=(open_room:7)
    HYBRID_TOPK_SLIPS=(0.0)
    HYBRID_TOPK_VALUES=(1 2)
    HYBRID_TOPK_METHODS=(surrogate_topk_certified_refine)
    ;;
  large)
    THREAD_GRID=(1 8 16 32 64 96 128 192)
    THREAD_SIZES=(192 384 768)
    RANDOM_SIZES=(9 11 13 15)
    RANDOM_SEEDS=(0 1 2 3 4 5 6 7)
    RANDOM_SLIPS=(0.0 0.05)
    RANDOM_METHODS=(endpoints group_constrained_incremental)
    LARGE_MAP_SPECS=(corridor:128,256,512 open_room:16,24 four_rooms:15,21 maze:17,21)
    LARGE_SLIPS=(0.05)
    LARGE_METHODS=(endpoints turn_articulation graph_rd_surrogate_joint betweenness_sqrt coverage_sqrt)
    AMORTIZED_MAP_SPECS=(corridor:128,256 open_room:16,24 four_rooms:15,21 maze:17,21)
    AMORTIZED_COUNTS=(1 5 10 25 50 100)
    AMORTIZED_MAX_TASKS=100
    EDGE_REWARD_MAP_SPECS=(corridor:128,256 open_room:16,24 four_rooms:15,21 maze:17,21)
    EDGE_REWARD_METHODS=(endpoints turn_articulation)
    EDGE_REWARD_COUNTS=(1 5 10 25 50 100)
    EDGE_REWARD_MAX_TASKS=100
    OPTION_MAP_SPECS=(corridor:128 open_room:16 four_rooms:15 maze:17)
    OPTION_SLIPS=(0.0 0.05)
    OPTION_K_VALUES=(4 8 12 16 24)
    HYBRID_MAP_SPECS=(open_room:12 four_rooms:11 maze:13)
    HYBRID_SLIPS=(0.0 0.05)
    HYBRID_TOP_K=(4)
    HYBRID_METHODS=(endpoints exact_group_rd incremental_group_rd surrogate_topk_exact_refine surrogate_topk_certified_refine heuristic_topk_exact_refine)
    HYBRID_TOPK_MAP_SPECS=(open_room:12 four_rooms:11 maze:13)
    HYBRID_TOPK_SLIPS=(0.0 0.05)
    HYBRID_TOPK_VALUES=(1 2 4 8 16)
    HYBRID_TOPK_METHODS=(surrogate_topk_exact_refine surrogate_topk_certified_refine)
    ;;
  xl)
    THREAD_GRID=(1 16 32 64 96 128 192)
    THREAD_SIZES=(384 768 1024)
    RANDOM_SIZES=(11 13 15 17 19)
    RANDOM_SEEDS=(0 1 2 3 4 5 6 7 8 9 10 11)
    RANDOM_SLIPS=(0.0 0.05 0.1)
    RANDOM_METHODS=(endpoints group_constrained_incremental)
    LARGE_MAP_SPECS=(corridor:256,512,1024 open_room:24,32 four_rooms:21,31 maze:21,31)
    LARGE_SLIPS=(0.0 0.05 0.1)
    LARGE_METHODS=(endpoints turn_articulation graph_rd_surrogate_joint betweenness_sqrt coverage_sqrt)
    AMORTIZED_MAP_SPECS=(corridor:256,512 open_room:24,32 four_rooms:21,31 maze:21,31)
    AMORTIZED_COUNTS=(1 5 10 25 50 100)
    AMORTIZED_MAX_TASKS=100
    EDGE_REWARD_MAP_SPECS=(corridor:256,512 open_room:24,32 four_rooms:21,31 maze:21,31)
    EDGE_REWARD_METHODS=(endpoints turn_articulation)
    EDGE_REWARD_COUNTS=(1 5 10 25 50 100)
    EDGE_REWARD_MAX_TASKS=100
    OPTION_MAP_SPECS=(corridor:256,512 open_room:24,32 four_rooms:21,31 maze:21,31)
    OPTION_SLIPS=(0.0 0.05 0.1)
    OPTION_K_VALUES=(4 8 12 16 24 32)
    HYBRID_MAP_SPECS=(open_room:12,16 four_rooms:11,15 maze:13,17)
    HYBRID_SLIPS=(0.0 0.05 0.1)
    HYBRID_TOP_K=(4)
    HYBRID_METHODS=(endpoints exact_group_rd incremental_group_rd surrogate_topk_exact_refine surrogate_topk_certified_refine heuristic_topk_exact_refine)
    HYBRID_TOPK_MAP_SPECS=(open_room:12,16 four_rooms:11,15 maze:13,17)
    HYBRID_TOPK_SLIPS=(0.0 0.05 0.1)
    HYBRID_TOPK_VALUES=(1 2 4 8 16)
    HYBRID_TOPK_METHODS=(surrogate_topk_exact_refine surrogate_topk_certified_refine)
    ;;
  *)
    echo "Unknown profile: $PROFILE" >&2
    exit 2
    ;;
esac

if has_part thread && [ "${LAPLACE_SKIP_THREAD_SCALING:-0}" != "1" ]; then
  "$PYTHON_CMD" experiments/run_linear_solver_thread_scaling.py \
    --threads "${THREAD_GRID[@]}" \
    --sizes "${THREAD_SIZES[@]}" \
    --rhs 8 \
    --reps "${LAPLACE_THREAD_REPS:-3}" \
    --out-dir "$OUT_ROOT/linear_solver_thread_scaling"
fi

if has_part random; then
  "$PYTHON_CMD" experiments/run_random_maze_generalization.py \
    --sizes "${RANDOM_SIZES[@]}" \
    --maze-seeds "${RANDOM_SEEDS[@]}" \
    --slips "${RANDOM_SLIPS[@]}" \
    --methods "${RANDOM_METHODS[@]}" \
    --shard-index "${LAPLACE_RANDOM_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_RANDOM_NUM_SHARDS:-1}" \
    --resume \
    --continue-on-error \
    --out-dir "$OUT_ROOT/random_maze_generalization"
fi

if has_part operator && [ "${LAPLACE_INCLUDE_OPERATOR_SUBSET:-1}" = "1" ]; then
  "$PYTHON_CMD" experiments/run_random_maze_generalization.py \
    --sizes 9 11 \
    --maze-seeds 0 1 \
    --slips 0.05 \
    --methods group_constrained_operator \
    --continue-on-error \
    --out-dir "$OUT_ROOT/random_maze_operator_subset"
fi

if has_part large_scale; then
  "$PYTHON_CMD" experiments/run_large_scale_compression.py \
    --map-specs "${LARGE_MAP_SPECS[@]}" \
    --methods "${LARGE_METHODS[@]}" \
    --slips "${LARGE_SLIPS[@]}" \
    --first-hit-mode adaptive \
    --first-hit-truncation-steps 1024 \
    --first-hit-tail-tol 1e-6 \
    --local-horizon 1000000000 \
    --shard-index "${LAPLACE_LARGE_SCALE_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_LARGE_SCALE_NUM_SHARDS:-1}" \
    --resume \
    --continue-on-error \
    --out-dir "$OUT_ROOT/large_scale_compression"
fi

if has_part amortized; then
  "$PYTHON_CMD" experiments/run_amortized_multitask.py \
    --map-specs "${AMORTIZED_MAP_SPECS[@]}" \
    --methods endpoints betweenness_sqrt graph_rd_surrogate_joint turn_articulation \
    --task-counts "${AMORTIZED_COUNTS[@]}" \
    --max-tasks "$AMORTIZED_MAX_TASKS" \
    --goal-source all_states \
    --shard-index "${LAPLACE_AMORTIZED_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_AMORTIZED_NUM_SHARDS:-1}" \
    --resume \
    --continue-on-error \
    --out-dir "$OUT_ROOT/amortized_multitask"
fi

if has_part edge_reward; then
  "$PYTHON_CMD" experiments/run_edge_reward_kernel_multitask.py \
    --map-specs "${EDGE_REWARD_MAP_SPECS[@]}" \
    --methods "${EDGE_REWARD_METHODS[@]}" \
    --task-counts "${EDGE_REWARD_COUNTS[@]}" \
    --max-tasks "$EDGE_REWARD_MAX_TASKS" \
    --shard-index "${LAPLACE_EDGE_REWARD_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_EDGE_REWARD_NUM_SHARDS:-1}" \
    --continue-on-error \
    --out-dir "$OUT_ROOT/edge_reward_kernel_multitask"
fi

if has_part option_frontier; then
  "$PYTHON_CMD" experiments/run_option_baseline_frontier.py \
    --map-specs "${OPTION_MAP_SPECS[@]}" \
    --slips "${OPTION_SLIPS[@]}" \
    --k-values "${OPTION_K_VALUES[@]}" \
    --families eigenoptions betweenness random_landmarks coverage \
    --include-endpoints \
    --include-graph-rd \
    --include-dense \
    --shard-index "${LAPLACE_OPTION_FRONTIER_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_OPTION_FRONTIER_NUM_SHARDS:-1}" \
    --resume \
    --continue-on-error \
    --out-dir "$OUT_ROOT/option_baseline_frontier"
fi

if has_part hybrid_refine; then
  "$PYTHON_CMD" experiments/run_hybrid_surrogate_refine.py \
    --map-specs "${HYBRID_MAP_SPECS[@]}" \
    --slips "${HYBRID_SLIPS[@]}" \
    --methods "${HYBRID_METHODS[@]}" \
    --top-k "${HYBRID_TOP_K[@]}" \
    --max-splits "${LAPLACE_HYBRID_MAX_SPLITS:-4}" \
    --shard-index "${LAPLACE_HYBRID_REFINE_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_HYBRID_REFINE_NUM_SHARDS:-1}" \
    --resume \
    --out-dir "$OUT_ROOT/hybrid_surrogate_refine"
fi

if has_part hybrid_topk; then
  "$PYTHON_CMD" experiments/run_hybrid_surrogate_refine.py \
    --map-specs "${HYBRID_TOPK_MAP_SPECS[@]}" \
    --slips "${HYBRID_TOPK_SLIPS[@]}" \
    --methods "${HYBRID_TOPK_METHODS[@]}" \
    --top-k "${HYBRID_TOPK_VALUES[@]}" \
    --max-splits "${LAPLACE_HYBRID_MAX_SPLITS:-4}" \
    --shard-index "${LAPLACE_HYBRID_TOPK_SHARD_INDEX:-0}" \
    --num-shards "${LAPLACE_HYBRID_TOPK_NUM_SHARDS:-1}" \
    --resume \
    --out-dir "$OUT_ROOT/hybrid_topk_ablation"
fi

if has_part fair_frontier; then
  "$PYTHON_CMD" experiments/run_fair_budget_frontier.py \
    --large-scale-csv "$OUT_ROOT/large_scale_compression/large_scale_compression.csv" \
    --random-maze-csv "$OUT_ROOT/random_maze_generalization/random_maze_generalization.csv" \
    --option-frontier-csv "$OUT_ROOT/option_baseline_frontier/frontier_all.csv" \
    --out-dir "$OUT_ROOT/fair_budget_frontier"
fi

if has_part submission_table; then
  "$PYTHON_CMD" experiments/run_submission_main_table.py \
    --large-scale-csv "$OUT_ROOT/large_scale_compression/large_scale_compression.csv" \
    --random-maze-csv "$OUT_ROOT/random_maze_generalization/random_maze_generalization.csv" \
    --fair-frontier-csv "$OUT_ROOT/fair_budget_frontier/fair_budget_frontier_summary.csv" \
    --amortized-csv "$OUT_ROOT/amortized_multitask/amortized_multitask.csv" \
    --edge-reward-csv "$OUT_ROOT/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv" \
    --hybrid-refine-csv "$OUT_ROOT/hybrid_surrogate_refine/hybrid_surrogate_refine.csv" "$OUT_ROOT/hybrid_topk_ablation/hybrid_surrogate_refine.csv" \
    --out-dir "$OUT_ROOT/submission_main_table"
fi

if has_part summary; then
  "$PYTHON_CMD" experiments/run_node_large_summary.py \
    --large-scale-csv "$OUT_ROOT/large_scale_compression/large_scale_compression.csv" \
    --amortized-csv "$OUT_ROOT/amortized_multitask/amortized_multitask.csv" \
    --edge-reward-csv "$OUT_ROOT/edge_reward_kernel_multitask/edge_reward_kernel_multitask.csv" \
    --random-maze-csv "$OUT_ROOT/random_maze_generalization/random_maze_generalization.csv" \
    --option-frontier-csv "$OUT_ROOT/option_baseline_frontier/frontier_all.csv" \
    --thread-scaling-csv "$OUT_ROOT/linear_solver_thread_scaling/linear_solver_thread_scaling.csv" \
    --out-dir "$OUT_ROOT/summary"
fi

echo "Node large paper run complete: $OUT_ROOT"
echo "DONE"
