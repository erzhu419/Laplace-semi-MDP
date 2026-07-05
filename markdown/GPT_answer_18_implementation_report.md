# GPT Answer 18 Implementation Report

## What Changed

- Upgraded the goal-conditioned terminal extension from per-boundary exact
  solves to a shared/batched backend.
- For each queried goal `g`, the experiment now builds one shared
  shortest-path goal-conditioned policy `pi_g`.
- For that policy it solves all boundary-start event rows together:
  - goal-hit vector `H_B(b,g)`
  - continuation matrix `Gamma_B^{not g}(b,.)`
  - step reward rows
- Added accounting fields:
  - `n_goal_policies`
  - `policy_build_time_sec`
  - `batched_event_solve_time_sec`
  - `break_even_num_tasks`

## Main Result

Main run:

```bash
python3 experiments/run_edge_reward_kernel_multitask.py \
  --map-specs corridor:128 open_room:16 four_rooms:15 maze:17 \
  --methods endpoints turn_articulation \
  --task-counts 1 5 10 \
  --max-tasks 10 \
  --continue-on-error \
  --out-dir experiments/output/edge_reward_kernel_multitask
```

Current summary:

- Additive reward kernels remain the main positive result:
  - sparse median total speedup `3.09x`
  - dense median total speedup `2.996x`
- Fixed event kernel remains the diagnostic:
  - max terminal start gap `27.52`
  - median total speedup `0.3858x`
- Shared/batched goal-conditioned event options are now a credible secondary
  extension:
  - max terminal start gap `0.3494`
  - median total speedup `0.3167x`
  - best total speedup `1.18x`
  - median break-even `10` tasks

## Interpretation

The upgrade confirms GPT's suggested positioning.  Goal-conditioned event
options should not replace the main RD boundary graph claim, but they are more
than a limitation note: they are a secondary method for terminal interior goals.
The important caveat is that the extension must always report goal-interface
and event-solve cost, because the complexity moves from graph vertices into the
query-time goal-conditioned interface.

## Next Question For GPT

The next useful critique is:

> With shared/batched goal-conditioned event options now reaching max terminal
> gap below `0.35`, best speedup above `1x`, and median break-even around `10`
> tasks, should we present the extension in the main experiments as a secondary
> method, or keep it in an appendix unless larger node-scale runs show better
> amortized speedup?
