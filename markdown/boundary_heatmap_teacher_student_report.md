# Transition-Graph Boundary Student

## Question

Can one graph-conditioned forward pass replace iterative boundary insertion?
The adaptive group-constrained RD solver is used only as an offline teacher. At
deployment, the student sees the finite transition graph, reward, start and
goal indicators, slip, discount, and candidate mask. It emits a node heatmap
and the number of nonmandatory vertices. It does not insert candidates,
recompute Green kernels, expand a beam, or use teacher scores.

The experiment is an ablation of the explicit one-shot Green operator, not a
replacement for that operator in the main method.

## Protocol

The native PyTorch implementation uses a sparse residual GCN without
`torch_geometric`. Each node has 28 transition, reward, topology, coordinate,
and endpoint-distance features. Five models are trained independently. The
validation set chooses either one model or the five-model ensemble; it selects
the single `seed_2` model. The model has a node heatmap head and a graph-level
count head. Training uses CUDA, but a validation benchmark selects CPU
inference (`0.00068 s` median forward/collation versus `0.00184 s` on CUDA)
because the model is too small to amortize device transfer. Final latency is
measured one graph at a time rather than reporting batched throughput.

The final graph-only teacher suite contains 360 contexts:

- families: corridor, open room, four rooms, DFS maze, and braided maze;
- slips: 0, 0.05, and 0.1;
- 180 train, 90 validation, and 90 scale-holdout test contexts;
- 8,115 frozen candidate targets;
- no hashed random basis states (`fixed_random_count=0`).

Removing the two hidden hash-selected basis states was necessary because a
student that only observes the graph cannot reproduce labels that also depend
on `map_name`. It changed the exact adaptive boundary in 39/360 contexts, but
did not change the qualitative student result.

The adaptive teacher was group feasible in 327/360 contexts and 71/90 strict
scale-holdout contexts. Infeasible teacher rows were retained for evaluation
but excluded from student training.

## Results

### Degenerate tree-maze pilot

On the initial 180-context DFS-maze dataset, the GNN and nearest-start rule
returned exactly the same graph in 180/180 contexts. Both hit the frozen
first-step top set in every context. The GNN therefore learned no additional
structure on that dataset. Production auditing showed 52/60 feasible GNN
graphs versus 58/60 feasible adaptive-teacher graphs. Adding fixed top-2 or
top-3 vertices was not monotone: it recovered feasibility in 9/60 contexts and
lost feasibility in 14/60 contexts.

### Multifamily scale holdout

On validation contexts, the selected graph-only GNN had boundary Jaccard
0.8742 versus 0.8567 for nearest-start. This imitation gain did not
extrapolate to the held-out larger sizes. Test Jaccard was 0.6508 for the GNN
and 0.6789 for nearest-start. Test top-set hit rate was 0.5444 versus 0.5778.

| proposal | boundary Jaccard | group feasible | group feasible and gap <= 0.01 | selection speedup | accepted pipeline speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| transition-graph GNN | 0.6508 | 70/90 | 68/90 | 769.8x | 0.444x |
| nearest-start | 0.6789 | 62/90 | 62/90 | 877.9x | 0.435x |
| adaptive RD teacher | 1.0000 | 71/90 | 71/90 | 1.0x | 1.0x |

Under the joint group-feasibility and normalized-value-gap constraint, both
methods passed 60 contexts, the GNN alone passed eight, nearest-start alone
passed two, and both failed 20. Thus the GNN has a six-context net advantage,
but still fails 22/90 held-out contexts and trails the adaptive teacher by
three passes. Maximum normalized start gap was 0.02225. Median GNN compression
was 33.8x.

Graph encoding plus one selected-model CPU forward pass took a median 0.00541
seconds, which was 769.8x faster than iterative teacher selection. The full
production group audit took a median 7.75 seconds. With audit and fallback
charged, the accepted GNN pipeline was only 0.444x as fast as the adaptive
teacher pipeline.

### Uncertainty routing

Validation-calibrated score margin was the usable cheap failure indicator for
the selected single model. A threshold calibrated to catch 100% of validation
joint-constraint failures audited 40.0% of held-out contexts but caught only
50.0% of test failures. Eleven failed graphs were accepted without audit. The
resulting median 25.7x timing number is not a valid certified speedup because
the routing rule did not preserve feasibility. Ensemble variance remains an
ablation and is unavailable to the selected one-pass model.

### Topology holdout

A second split held out maze topology seeds while retaining deterministic-map
scale holdouts. Its selected GNN top-1 model obtained test Jaccard 0.8318,
exactly matching nearest-start; top-set hit was 0.7424 versus 0.7273. This is a
minor ranking difference, not evidence that the learned student dominates the
explicit rule.

## Interpretation

The experiment separates three claims:

1. A graph-conditioned forward pass learns some constraint-relevant structure
   and is hundreds of times faster than iterative selection.
2. Boundary imitation quality is not itself a group-feasibility or value
   certificate.
3. Current validation-calibrated confidence routing does not replace the
   production audit.

The current GNN is therefore an uncertified ablation. Its improvement over
nearest-start makes it more informative than a purely degenerate negative
result, but it should not be promoted to the paper's main method. The explicit
one-shot Green operator remains the primary search-free proposal because it
has an interpretable mathematical object, formal truncation and selection
certificates, and stronger paired evidence. Adaptive group-constrained RD
remains the reference and fallback when hard group feasibility is required.

## Artifacts

- `experiments/boundary_heatmap_gnn.py`: sparse GCN, batching, loss, and model serialization.
- `experiments/run_boundary_heatmap_teacher.py`: sharded frozen heatmaps and optional adaptive labels.
- `experiments/run_boundary_heatmap_gnn.py`: training, baselines, scale/topology splits, and deployment exports.
- `experiments/run_boundary_heatmap_downstream.py`: production group and value audit.
- `experiments/analyze_boundary_heatmap_student.py`: explicit-rule identity and failure analysis.
- `experiments/calibrate_boundary_heatmap_selective_audit.py`: validation-only uncertainty calibration.
- `experiments/output/boundary_heatmap_teacher_graphonly/`: compact graph-only teacher artifact.
- `experiments/output/boundary_heatmap_gnn_graphonly/`: prediction and training summaries.
- `experiments/output/boundary_heatmap_downstream_graphonly_test/`: strict scale-holdout audit.
- `experiments/output/boundary_heatmap_downstream_graphonly_baselines/`: nearest-start and topology audits.
- `experiments/output/boundary_heatmap_selective_audit_graphonly/`: selective-routing failure audit.

The neural dependency is intentionally optional and pinned in
`requirements-learning.txt`; the core operator and Lean artifact remain
PyTorch-free.
