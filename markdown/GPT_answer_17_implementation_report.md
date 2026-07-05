# GPT Answer 17 Implementation Report

## What Changed

- Extended `experiments/run_edge_reward_kernel_multitask.py` with
  `fixed_B_goal_conditioned_event_options`.
- The new variant keeps the boundary graph `B` fixed.
- For each query terminal goal `g`, it appends local goal-conditioned options
  from each boundary state to `g`, terminating at `g` or the first other
  boundary.
- The experiment now reports:
  - `goal_option_interface_size`
  - `goal_conditioned_options`
  - `boundary_gap_max`
  - `epsilon_opt_empirical`
- Added T10 to `paper/theorem_stack.md`: goal-event kernels and
  option-restriction bias.
- Added Lean real-layer hooks:
  - `goal_event_kernel_value_gap_real`
  - `goal_event_option_bias_value_gap_real`
  - `goal_event_total_value_gap_real`

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

- `fixed_B_event_hit_kernel`: max start gap `27.52`, median total speedup `0.3782x`.
- `fixed_B_goal_conditioned_event_options`: max start gap `0.3494`, median total speedup `0.1995x`.
- The proof-of-concept confirms GPT's diagnosis: terminal-goal gaps were mostly option-family insufficiency, not event-kernel approximation or graph-topology failure.
- The extra accuracy is not free: the interface grows with `|B| * n_goal_queries` and the current exact per-query event-kernel solve is slower, so this is an ablation/diagnostic rather than the main runtime path.

## Paper Positioning

The safest claim remains:

> Additive reward kernels are the main positive multi-task result; terminal event kernels diagnose option/boundary restriction bias. Goal-conditioned local event options show the gap can be reduced without adding the goal to `B`, but their option interface and per-query kernel cost must be counted.

## Next Question For GPT

The useful next critique is now:

> Given that goal-conditioned event options reduce terminal gaps from about `27.5` to below `0.35` while slowing total runtime, should the paper keep this as a proof-of-concept limitation ablation, or optimize it into a secondary method via cached/shared goal-conditioned policies and batched event-kernel solves?
