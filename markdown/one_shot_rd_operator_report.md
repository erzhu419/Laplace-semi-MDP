# One-Shot RD Green Operator

## Question

The original idea was not to run a costly combinatorial boundary search at
deployment time. Search should serve as a teacher/reference for deriving a
fixed, Laplacian-like graph filter. The runtime path should:

1. start from mandatory boundary `B0`;
2. build one truncated sparse Green response;
3. compute all state scores in one frozen multichannel pass;
4. select a thresholded local-max/top set once;
5. build graph kernels only for the final boundary once;
6. perform no candidate insertion, beam expansion, or score recomputation.

`experiments/one_shot_rd_operator.py` now implements exactly this path.

## What Is And Is Not The Operator

The exact frozen finite-difference RD score remains the mathematical reference
objective. Exact RD and iterative surrogate selection are teacher/oracle
algorithms. The deployed one-shot transform is a Green-derived heuristic
operator, closer in role to a fixed graph/CNN filter:

```text
B0 -> sparse truncated Green/occupancy response
   -> Green, policy, topology, entropy, and flow channels
   -> fixed normalization + threshold + local maxima
   -> B
   -> one final graph-kernel construction
```

The Lean layer proves response-to-score error propagation, threshold stability,
and local-maximum stability under a margin. It does not claim that thresholding
globally minimizes the combinatorial RD set objective.

## Results

### Classic paired search comparison

Across 12 corridor/open-room/four-room/maze map-slip cases, threshold `0.15`
gave:

| Metric | One-shot result |
| --- | ---: |
| Median selection time | 0.01095 s |
| Selection speedup vs iterative surrogate | 40.06x |
| Selection speedup vs exact RD search | 157.2x |
| Full graph-pipeline speedup vs iterative surrogate | 7.77x |
| Full graph-pipeline speedup vs exact RD search | 22.86x |
| Median boundary Jaccard vs iterative | 0.667 |
| Maximum normalized value gap | 0.009628 |
| Median occupancy hidden distortion | numerical zero |

The graph is usually a little denser than the search result. Corridor and most
maze boundaries match exactly; open-room and four-room graphs can differ while
retaining similar task value.

### Held-out random mazes

The held-out table has 108 size-seed-slip contexts for each fixed threshold:

| Threshold | Median boundary | State compression | Max normalized value gap | Median D_occ |
| --- | ---: | ---: | ---: | ---: |
| 0.15 | 18 | 6.30x | 1.46e-7 | 9.87e-7 |
| 0.75 | 10 | 9.70x | 1.06e-7 | 7.0 |

This is a genuine rate-distortion frontier. The higher threshold compresses
more and still solves the active task, but hides substantially more audit
structure. Value alone is therefore not enough to choose the threshold.

On a paired 20-context held-out subset (sizes 11 and 15, five seeds, slips
0.05 and 0.1), one-shot and iterative surrogate boundaries had median Jaccard
agreement `0.920`. One-shot selection was `369.5x` faster, and the complete
graph pipeline remained `12.94x` faster. Their maximum normalized value gaps
were `1.20e-7` and `1.08e-7`, respectively.

### XL scaling

Across 27 XL map-slip cases, threshold `0.15` gave median `192x` state
compression, maximum normalized start gap `0.00784`, and maximum normalized
boundary-value gap `0.00910`.

The median one-shot extraction time was `0.0797 s`, a `947x` paired-by-context
speedup over the legacy iterative selector. Including the one final graph
kernel, the graph pipeline was `15.1x` faster than the iterative pipeline.
However, it was still only `0.00386x` as fast as one sparse full-state VI solve.
The reason is now unambiguous: median final-kernel time was `2.05 s`, versus
`0.0797 s` for the operator. Search is no longer the dominant cost; exact edge
kernel construction is.

### Can the truncation horizon be learned?

`run_learned_green_horizon.py` tests a graph-conditioned horizon proposal before
adding a neural encoder. A NumPy ridge model sees graph size/density, degree and
cycle statistics, endpoint distances, slip, and discount horizon. A held-out
split-conformal residual shifts its prediction upward; any failed proposal is
then enlarged and checked again against the same frontier certificate.

The 105/15/60 train/calibration/test pilot obtained a `93.3%` first-pass
certificate rate over all 60 held-out rows (`92.6%` over the 54 nontrivial
rows), and `100%` after fallback. Both the first proposal and corrected result
had minimum boundary Jaccard `1.0` against the adaptive reference on this suite.
So `K` is learnable well enough to serve as a batched execution hint.

It is not a useful single-environment acceleration here. Median learned total
time was `0.0397 s`, versus `0.0335 s` for a deliberately fixed 256-step prefix
and `0.0265 s` for the existing per-step adaptive stop. Median learned speedups
were therefore only `0.906x` and `0.747x`. The current recurrence already stops
early, while graph-feature extraction and four underprediction retries add
cost. A YOLO-like extension should consequently predict the vertex heatmap
itself (and optionally per-response horizons for batching), not merely replace
adaptive stopping with a learned scalar.

## Failure Boundary

The current hard group audit is not solved by the frozen one-shot transform.
It failed all three open-room/four-room/maze diagnostic rows. Increasing the
fixed split cap did not monotonically restore feasibility because changing the
boundary also changes the available option library and active edges.

A stricter one-shot ablation computes the exact frozen multi-probe
finite-difference order once, then audits fixed prefixes without rescoring. In
the completed three-node artifact, open-room is feasible only at tested prefix
`k=2` and fails again at `k=3`; four-rooms is feasible at tested prefixes
`k=3,4,5,6,8,10` but not `k=12`; maze has no feasible prefix through `k=24`.
Thus the frozen score can hit feasible graphs, but feasibility is neither
monotone in prefix length nor guaranteed by a universal scalar `k`.

The honest method hierarchy is therefore:

```text
one-shot operator (primary fast proposal/task path)
    -> value and grouped audit
    -> accept if certified
    -> otherwise invoke separately timed group-constrained adaptive fallback
```

This supports the original operator idea, but only as a fast graph proposal
whose returned abstraction is audited. It does not establish task-independent
MDP equivalence, and the fallback cost must remain visible.

## Artifacts

- `experiments/output/one_shot_rd_operator/`: classic one-shot/search pairing.
- `experiments/output/one_shot_rd_operator_random/`: 216 held-out random-maze rows.
- `experiments/output/one_shot_rd_operator_random_reference/`: paired held-out one-shot/iterative rows.
- `experiments/output/one_shot_rd_operator_xl/`: operator-only XL timing.
- `experiments/output/one_shot_rd_operator_xl_end_to_end/`: full XL graph pipeline.
- `experiments/output/one_shot_group_fd_frontier/`: frozen group-FD prefix audit.
- `experiments/output/learned_green_horizon/`: train/calibration/test horizon proposal and certified execution audit.
- `proof/OneShotRDOperator.lean`: one-shot error and selection-stability proofs.
