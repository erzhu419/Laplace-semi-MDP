# GPT Answer 16 Implementation Report

## What Changed

- Added `experiments/run_edge_reward_kernel_multitask.py`.
- Kept the decision boundary graph `B` fixed across tasks.
- Added additive reward relabeling through exact edge discounted occupancy kernels.
- Added terminal-goal relabeling through query-time first-hit event kernels plus continuation kernels.
- Added T9 to `paper/theorem_stack.md`: edge reward/event kernel relabeling and value-gap bounds.
- Added Lean real-layer hooks in `proof/RDOperatorReal.lean`:
  - `reward_kernel_error_le_l1`
  - `reward_kernel_value_gap_real`
  - `reward_kernel_value_gap_from_l1_budget`
  - `primitive_to_reward_kernel_gap_decomposition`

## References Added Locally

- Dayan 1993 successor representation PDF:
  `reference/papers/successor_representation_1993__improving-generalisation-for-temporal-difference-learning.pdf`
- Barreto et al. 2018 successor features + GPI PDF/page:
  `reference/papers/successor_features_gpi_2018__transfer-in-deep-reinforcement-learning-using-successor-features-and-gpi.pdf`
  and `reference/pages/successor_features_gpi_2018.html`
- Barreto et al. 2017 successor features transfer PDF/page:
  `reference/papers/successor_features_transfer_2017__successor-features-for-transfer-in-reinforcement-learning.pdf`
  and `reference/pages/successor_features_transfer_2017.html`
- Independent related repo:
  `reference/repos/mike-gimelfarb__deep-successor-features-for-transfer`

## Experiment Result

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

Promote-goal negative-control smoke run:

```bash
python3 experiments/run_edge_reward_kernel_multitask.py \
  --map-specs corridor:32 open_room:6 \
  --methods endpoints turn_articulation \
  --task-counts 1 3 5 \
  --max-tasks 5 \
  --include-promote-baseline \
  --out-dir experiments/output/edge_reward_kernel_multitask_promote_smoke
```

Current interpretation:

- Additive reward kernels validate the compression story: `B` stays small, reward support no longer becomes topology, and planning-only speedup is large when the graph remains compact. In the current table, sparse and dense additive rewards both have median total speedup around `3x` and median planning-only speedup above `100x`.
- The promote-goal smoke run is the intended negative control: it gets tiny terminal gaps, but it grows `B` with the number of goals and loses total-time compression even on small maps.
- Terminal first-hit event kernels also keep `B` fixed, but their value gap exposes option/boundary restriction bias in open rooms and under sparse boundaries.
- The right paper claim is now cleaner: boundary vertices encode decision structure, while edge reward/event kernels encode task variation.

## Next Question For GPT

The next useful critique is not whether reward states should be promoted; that is now clearly a negative control. The sharper question is:

> For terminal interior goals with large event-kernel value gaps, should the paper treat the gap mainly as option/boundary restriction bias, or should we add a goal-conditioned local option/event family that preserves fixed `B` while reducing this bias?
