# Node Large Run 20260705 Report

Generated after syncing and aggregating scheduler run `20260705_202131`.

## Artifacts

- Aggregated amortized table: `/home/erzhu419/mine_code/Laplace-semi-MDP/experiments/output/scheduler_large_runs/20260705_202131/amortized_aggregate/amortized_multitask.csv`
- Aggregated amortized summary: `/home/erzhu419/mine_code/Laplace-semi-MDP/experiments/output/scheduler_large_runs/20260705_202131/amortized_aggregate/summary.md`
- Large-scale compression summary: `/home/erzhu419/mine_code/Laplace-semi-MDP/experiments/output/scheduler_large_runs/20260705_202131/large_scale/large_scale_compression/summary.md`
- Random-maze robustness summary: `/home/erzhu419/mine_code/Laplace-semi-MDP/experiments/output/scheduler_large_runs/20260705_202131/thread_random/random_maze_generalization/summary.md`
- Thread-scaling summary: `/home/erzhu419/mine_code/Laplace-semi-MDP/experiments/output/scheduler_large_runs/20260705_202131/thread_random/linear_solver_thread_scaling/summary.md`

All 32 amortized shards finished and were synced manually because scheduler result sync had only pulled the first 3 shard folders. The aggregate now contains 192 rows from all 32 shard CSVs.

## Main Results

The large-scale compression table supports the core planning-compression story in structured maps, but not yet the full robust-discovery story.

| method | median total speedup | best total speedup | median planning speedup | max hidden structure | max start gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| endpoints | 1.918x | 7.587x | 2726x | 19.0 | 0.0980 |
| turn_articulation | 1.373x | 9.972x | 366x | 0.0 | 0.0980 |
| graph_rd_surrogate_joint | 0.274x | 0.458x | 3158x | 1.858 | 0.0980 |
| betweenness_sqrt | 0.100x | 0.938x | 3.109x | 16.0 | 0.0980 |
| coverage_sqrt | 0.129x | 1.149x | 14.85x | 19.05 | 0.0980 |

Interpretation:

- `turn_articulation` is the cleanest current method for validity: hidden boundary mass is 0 in this table, and it wins strongly on corridors/open rooms. It becomes too dense in mazes, so total speed falls below full VI there.
- `endpoints` gives the sharpest compression and total speedup, but it hides boundary structure badly in open/four-room/maze tasks. It is a useful lower-bound compression baseline, not a valid abstraction baseline.
- `graph_rd_surrogate_joint` often chooses compact graphs and planning is fast, but upfront discovery is still too expensive, especially maze rows, so total speed is not competitive yet.

The random-maze robustness table confirms the validity/runtime tradeoff:

| method | feasible rate | median total speedup | median planning speedup | median selection time | median break-even tasks |
| --- | ---: | ---: | ---: | ---: | ---: |
| endpoints | 0.0 | 2.679x | 549x | 0.0s | 1 |
| group_constrained_incremental | 0.969 | 0.047x | 18.57x | 1.294s | 23 |

So the group-constrained selector is doing the right structural job, but discovery cost still dominates.

The linear solver thread benchmark says not to blindly use all 192 CPU cores for the current matrix sizes. Best observed thread counts were 32 for size 192, 1 for size 384, and 16 for size 768; speedups were only about 1.1x at best, and 64/128/192 threads often made solves slower.

## Important Issue Found

The amortized multi-task result is currently not measuring the intended compressed-reward story.

For `--goal-source all_states`, `run_amortized_multitask.py` rebuilds the graph by adding all task goal states into the boundary set:

```text
boundary = base_boundary union {start} union goals
```

With `max_tasks=100`, the graph therefore gets about 100 boundary vertices even for endpoint/turn methods. The result is a dense all-goal boundary graph:

- median `n_boundary` at 100 tasks: about 101 to 115
- median amortized speedup: only 0.039x to 0.044x
- median planning-only speedup: only 0.039x to 0.046x
- no finite break-even task count

This is not evidence that the compression idea fails. It shows that the current all-state multi-task implementation destroys compression by promoting every reward state to a vertex. For the paper story, arbitrary interior rewards must be represented by edge-level reward/occupancy kernels, not by inserting every reward state into `B`.

## Next Step

The next implementation target should be an interior-reward compressed SMDP:

1. Keep `B` fixed after discovery.
2. For each compressed edge/option, estimate an edge reward kernel such as expected discounted occupancy or first-hit reward contribution for interior states.
3. Solve each new goal/reward task on the same graph without adding the goal state to `B`.
4. Compare three amortized variants:
   - boundary-goal only, where goals must already be in `B`
   - current naive all-state goal insertion, as a negative control
   - new interior-reward compressed kernel, which is the real hypothesis

This is also the right conceptual question for GPT:

> The large-scale compression result supports planning-speed compression when B stays small, but our all-state amortized experiment destroys compression because it inserts every goal into B. Should the paper formulate multi-task rewards through edge-level discounted occupancy / first-hit reward kernels, so arbitrary interior rewards can be evaluated without promoting reward states to graph vertices? What theorem should connect this reward-kernel approximation to value-gap bounds in the graph SMDP?
