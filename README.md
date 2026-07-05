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

## Current Artifact Status

- Certified adaptive Green plus tie-aware epsilon/top-set certificates reaches final certified decisions on the current certification suite.
- The large-scale adaptive table currently shows planning-only speedups in the thousands on long corridors. The submission table reports both conservative unique-top fallback and tie-aware timing; tie-aware certification separates corridor tie overhead from true curvature fallback.
- The compact benchmark compares full VI, exact RD graph variants, group-constrained RD, eigenoptions, betweenness bottlenecks, random landmarks, and coverage landmarks under the same map/slip suite.
- Solver-validity diagnostics compare operator-only and exact-refined beam search against small exhaustive oracles.
- The larger group-constrained adaptive table evaluates `open_room_12`, `four_rooms_11`, and `maze_13` at slip `0` and `0.05`; group-constrained boundaries are feasible on the current suite, while endpoint-only boundaries are not.
- Discovery profiling is now separated from planning: `experiments/output/discovery_profile_cache/summary.md` decomposes probe construction, Green kernels, vectorized frozen scoring, full candidate recompute, and cache-hit reuse.
- Incremental Green diagnostics now check parent-to-child boundary insertion, and `group_constrained_incremental` wires the score-level update into beam selection as an ablation. The semantic diff identified the open-room issue as edge-uniform versus occupancy-weighted accounting; the insertion backend now honors and caches the production active-edge weights and is feasible on the larger group suite.
- Weighted spectral certificates are reported as sufficient appendix certificates; conditioned/rational audits expose the conditioning-vs-tightness tradeoff.

Use `experiments/output/submission_main_table/summary.md` as the first reviewer-facing artifact rather than reading every historical output directory.
