# Laplace Semi-MDP

This repository is an experimental artifact for a rate-distortion graph abstraction of finite semi-MDP planning. The core idea is not to discover options for their own sake: it is to compress noncritical state regions into first-boundary edges while keeping the MDP/SMDP planning distortion auditable.

## Main Claim

The current paper-facing path is:

1. **Reference operator:** exact first-hit Green kernels define the frozen RD split score.
2. **Runtime implementation:** certified adaptive Green intervals are used first; uniqueness failures are separated into epsilon-optimal/tie-set certificates versus true curvature fallback.
3. **Planner:** the selected boundary states become graph vertices, first-boundary options become graph-SMDP actions, and value iteration/planning runs on that compressed graph.
4. **Appendix certificates:** weighted spectral and conditioned rational Collatz certificates justify convergence/safety as sufficient certificates, but they are not the main runtime decision rule.

The most useful entry-point table is generated at:

```text
experiments/output/submission_main_table/summary.md
```

It aligns the large-scale certified adaptive result, compact baselines, exhaustive-oracle solver validity, and certificate appendices into one submission-facing report.

## Repository Map

- `experiments/`: executable benchmark and diagnostic scripts.
- `experiments/output/`: checked-in CSV/JSON/Markdown experiment artifacts.
- `proof/`: Lean 4 proof layer for the frozen RD operator, Green/Neumann certificates, Bellman contraction/value-gap statements, top-set fallback, and bits-curvature bounds.
- `paper/`: paper-facing claim, terminology, related-work, theorem, experiment, figure, and reviewer-risk planning docs.
- `markdown/`: working research notes and GPT critique/advice logs.
- `reference/`: ignored local papers and cloned repositories.

## Quick Start

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the proof layer:

```bash
bash scripts/reproduce_proofs.sh
```

Rebuild the certificate artifacts:

```bash
bash scripts/reproduce_certificates.sh
```

Rebuild the core paper-facing experiments:

```bash
bash scripts/reproduce_core.sh
```

By default, experiment scripts cap BLAS/OpenMP to one CPU thread so local WSL
runs do not monopolize all cores. These experiments are NumPy/OpenBLAS linear
algebra jobs, not CUDA/GPU training. On CPU nodes, override the cap explicitly,
for example:

```bash
LAPLACE_NUM_THREADS=64 bash scripts/reproduce_core.sh
```

To choose a thread count on a CPU node, run:

```bash
python3 experiments/run_linear_solver_thread_scaling.py --threads 1 2 4 8 16 32 64
```

For large CPU-node paper runs, use the existing scheduler wrapper. First stage
the repo through the configured jump host to the shared scheduler workdir:

```bash
bash scripts/stage_laplace_scheduler.sh
```

Then submit scheduler tasks pinned to `node001`-`node006`; result directories
are synced back under `experiments/output/scheduler_large_runs/`:

```bash
python3 scripts/submit_laplace_scheduler.py --profile large --dispatch
```

The scheduler wrapper defaults to full-node BLAS/OpenMP threading
(`--threads 192`) while reserving a slightly lower scheduler CPU estimate
(`--cpu 128`) so transient load-average accounting does not keep otherwise
idle `node001`-`node006` jobs queued. The `--threads` value is exported as
`LAPLACE_NUM_THREADS`, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
`MKL_NUM_THREADS`, and `NUMEXPR_NUM_THREADS`. Large/xl amortized runs are split
into map/method shards by default (`--amortized-shards 32`) and use smaller
per-shard reservations (`--amortized-threads 16`, `--amortized-cpu 16`) because
that workload did not saturate a whole 192-core node. Each shard writes
application-level checkpoints (`progress.jsonl` plus an incrementally refreshed
CSV/summary) after every map/method job; `--scheduler-ckpt-dir` can also declare
those dirs to scheduler, but it is slower because submit scans remote paths.
The paper-grade suites can be submitted separately as scheduler shards:
`random_maze`, `large_scale`, `amortized`, `edge_reward`, and
`option_frontier`.  The XL profile defaults to multi-slip random/topology
stress tests, scaled compression maps, fixed-`B` edge reward relabeling, and a
matched option-baseline frontier.  To aggregate finished shard outputs:

```bash
python3 experiments/aggregate_scheduler_shards.py \
  --run-root experiments/output/scheduler_large_runs/<run_id> \
  --publish
```

For a cheap scheduler preflight:

```bash
python3 scripts/submit_laplace_scheduler.py --profile smoke --suites full --nodes node001 --dispatch
```

The underlying node runner is `scripts/run_node_large_paper.sh`; it runs
random-maze robustness, large-scale compression, multi-task amortization, thread
scaling, and a node summary under `experiments/output/scheduler_large_runs/`.

## Current Artifact Status

- Certified adaptive Green plus tie-aware epsilon/top-set certificates reaches final certified decisions on the current certification suite.
- The XL scheduler run `paper_xl_20260706_0659` has been published into the tracked paper-facing outputs: large-scale compression 135 rows, random maze 360 rows, option frontier 648 rows, amortized multitask 192 rows, and fixed-`B` edge reward 384 rows.
- The large-scale adaptive table currently shows planning-only speedups up to roughly `1e5x` on long corridors and single-task total speedups up to roughly `10.5x`. The submission table reports both planning-only and total-time accounting.
- The compact benchmark compares full VI, exact RD graph variants, group-constrained RD, eigenoptions, betweenness bottlenecks, random landmarks, and coverage landmarks under the same map/slip suite.
- Solver-validity diagnostics compare operator-only and exact-refined beam search against small exhaustive oracles.
- The larger group-constrained adaptive table evaluates `open_room_12`, `four_rooms_11`, and `maze_13` at slip `0` and `0.05`; group-constrained boundaries are feasible on the current suite, while endpoint-only boundaries are not.
- Discovery profiling is now separated from planning: `experiments/output/discovery_profile_cache/summary.md` decomposes probe construction, Green kernels, vectorized frozen scoring, full candidate recompute, and cache-hit reuse.
- Incremental Green diagnostics now check parent-to-child boundary insertion, and `group_constrained_incremental` wires the score-level update into beam selection as an ablation. The semantic diff identified the open-room issue as edge-uniform versus occupancy-weighted accounting; the insertion backend now honors and caches the production active-edge weights and is feasible on the larger group suite.
- Weighted spectral certificates are reported as sufficient appendix certificates; conditioned/rational audits expose the conditioning-vs-tightness tradeoff.
- Fixed-boundary multi-task relabeling is now separated from graph topology:
  `experiments/output/edge_reward_kernel_multitask/summary.md` compares full VI
  against exact edge discounted-occupancy reward kernels and query-time
  first-hit event kernels. Additive reward relabeling preserves compression;
  terminal-goal event kernels keep `B` fixed but expose the remaining
  option/boundary restriction gap. The goal-conditioned event-option extension
  keeps `B` fixed and reduces terminal-goal gaps using one shared policy and
  one batched event solve per queried goal, while reporting the extra
  goal-interface cost and break-even task count separately.
- Paper-facing scaffolding now lives under `paper/`, including the main claim, related-work matrix, theorem stack, experiment matrix, and figure plan.
- `experiments/run_random_maze_generalization.py`, `experiments/run_fair_budget_frontier.py`, `experiments/plot_graph_abstraction_figures.py`, and `experiments/run_theorem_experiment_bridge.py` add random-topology stress tests, shared budget-frontier aggregation, interpretability figures, and theorem/proof/experiment alignment.

Use `experiments/output/submission_main_table/summary.md` as the first reviewer-facing artifact rather than reading every historical output directory.
