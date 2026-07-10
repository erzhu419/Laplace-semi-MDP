# Transition-Graph GNN Boundary Heatmap

Generated: 2026-07-11T00:49:53

The group-constrained RD selector is the offline teacher. The student receives only the finite transition graph, candidate mask, start/goal/reward/transition features, and global slip/discount values. It emits one node heatmap and one graph-level extra-vertex count. Mandatory endpoints are inserted exactly, and no teacher score, candidate insertion, beam expansion, or Green recomputation is available to the student.

split mode = `teacher`. Splits are assigned at the base-topology level, never by individual slip row. Teacher mode uses complete larger-scale holdouts; hybrid mode holds out maze topology seeds and retains deterministic-family scale holdouts.

training device = `cuda`, inference device = `cpu`, selected validation mode = `gnn_seed_2`

## Prediction Summary

| split | method | n_rows | n_feasible_teacher_rows | mean_boundary_jaccard | mean_extra_jaccard | mean_extra_recall | exact_boundary_rate | count_accuracy | top_set_hit_rate | mean_top_set_regret | mean_teacher_top_set_size | teacher_tie_rate | match_nearest_start_rate | feasible_teacher_mean_boundary_jaccard | median_student_selection_time_sec | median_selection_speedup_vs_teacher |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | baseline_midpoint | 90 | 71 | 0.4717 | 0.0 | 0.0 | 0.0 | 0.7778 | 0.01111 | 0.8604 | 1.844 | 0.5444 | 0.0 | 0.4834 | 0.00466 | 878.1 |
| test | baseline_nearest_start | 90 | 71 | 0.6789 | 0.4059 | 0.4059 | 0.3889 | 0.7778 | 0.5778 | 0.4222 | 1.844 | 0.5444 | 1 | 0.7435 | 0.00466 | 877.9 |
| test | baseline_random | 90 | 71 | 0.4717 | 0.0 | 0.0 | 0.0 | 0.7778 | 0.01111 | 0.9087 | 1.844 | 0.5444 | 0.0 | 0.4834 | 0.004658 | 878.1 |
| test | baseline_topology | 90 | 71 | 0.5237 | 0.09148 | 0.09148 | 0.06667 | 0.7778 | 0.1222 | 0.6332 | 1.844 | 0.5444 | 0.06667 | 0.5202 | 0.004657 | 879 |
| test | gnn_ensemble | 90 | 71 | 0.6567 | 0.3806 | 0.3833 | 0.3667 | 0.7667 | 0.5333 | 0.4347 | 1.844 | 0.5444 | 0.7111 | 0.7256 | 0.008987 | 453.2 |
| test | gnn_ensemble_top1 | 90 | 71 | 0.6628 | 0.3778 | 0.3778 | 0.3667 | 0.7778 | 0.5333 | 0.4667 | 1.844 | 0.5444 | 0.7111 | 0.7256 | 0.008987 | 453.2 |
| test | gnn_ensemble_top2 | 90 | 71 | 0.5654 | 0.262 | 0.517 | 0.0 | 0.1333 | 0.6556 | 0.337 | 1.844 | 0.5444 | 0.0 | 0.6211 | 0.008987 | 453.2 |
| test | gnn_ensemble_top3 | 90 | 71 | 0.4866 | 0.2084 | 0.6115 | 0.0 | 0.02222 | 0.7444 | 0.2067 | 1.844 | 0.5444 | 0.0 | 0.5291 | 0.008987 | 453.2 |
| test | gnn_seed_0 | 90 | 71 | 0.6684 | 0.3889 | 0.3889 | 0.3778 | 0.7778 | 0.5444 | 0.4387 | 1.844 | 0.5444 | 0.7111 | 0.7327 | 0.005433 | 759.7 |
| test | gnn_seed_1 | 90 | 71 | 0.6628 | 0.3778 | 0.3778 | 0.3667 | 0.7778 | 0.5333 | 0.4667 | 1.844 | 0.5444 | 0.6778 | 0.7256 | 0.005786 | 706.8 |
| test | gnn_seed_2 | 90 | 71 | 0.6508 | 0.3806 | 0.3833 | 0.3667 | 0.7556 | 0.5444 | 0.4284 | 1.844 | 0.5444 | 0.7444 | 0.7209 | 0.005415 | 769.8 |
| test | gnn_seed_3 | 90 | 71 | 0.6529 | 0.3738 | 0.38 | 0.3556 | 0.7778 | 0.5111 | 0.47 | 1.844 | 0.5444 | 0.4778 | 0.7186 | 0.005339 | 769.3 |
| test | gnn_seed_4 | 90 | 71 | 0.6546 | 0.3806 | 0.3833 | 0.3667 | 0.7778 | 0.5222 | 0.4458 | 1.844 | 0.5444 | 0.6444 | 0.7256 | 0.005709 | 747.4 |
| train | baseline_midpoint | 180 | 172 | 0.4953 | 0.0 | 0.0 | 0.0 | 0.8944 | 0.0 | 0.808 | 2.161 | 0.8 | 0.0 | 0.4895 | 0.001789 | 434.7 |
| train | baseline_nearest_start | 180 | 172 | 0.8846 | 0.7741 | 0.7741 | 0.7667 | 0.8944 | 0.8056 | 0.1944 | 2.161 | 0.8 | 1 | 0.8969 | 0.001787 | 435.6 |
| train | baseline_random | 180 | 172 | 0.5008 | 0.01111 | 0.01111 | 0.01111 | 0.8944 | 0.06667 | 0.8367 | 2.161 | 0.8 | 0.01667 | 0.4953 | 0.001789 | 431.9 |
| train | baseline_topology | 180 | 172 | 0.5918 | 0.1814 | 0.1814 | 0.1611 | 0.8944 | 0.3056 | 0.4917 | 2.161 | 0.8 | 0.1333 | 0.5893 | 0.001785 | 436.2 |
| train | gnn_ensemble | 180 | 172 | 0.8784 | 0.77 | 0.7722 | 0.7667 | 0.9111 | 0.8 | 0.1945 | 2.161 | 0.8 | 0.8222 | 0.8924 | 0.005455 | 147.6 |
| train | gnn_ensemble_top1 | 180 | 172 | 0.8786 | 0.7667 | 0.7667 | 0.7667 | 0.8944 | 0.7833 | 0.2167 | 2.161 | 0.8 | 0.8222 | 0.8907 | 0.005455 | 147.6 |
| train | gnn_ensemble_top2 | 180 | 172 | 0.6994 | 0.4315 | 0.8574 | 0.0 | 0.01667 | 0.8667 | 0.1333 | 2.161 | 0.8 | 0.0 | 0.7102 | 0.005455 | 147.6 |
| train | gnn_ensemble_top3 | 180 | 172 | 0.5727 | 0.3023 | 0.888 | 0.0 | 0.03333 | 0.9056 | 0.07611 | 2.161 | 0.8 | 0.0 | 0.5818 | 0.005455 | 147.6 |
| train | gnn_seed_0 | 180 | 172 | 0.862 | 0.7333 | 0.7333 | 0.7333 | 0.8944 | 0.7611 | 0.2389 | 2.161 | 0.8 | 0.7389 | 0.8733 | 0.00262 | 320.6 |
| train | gnn_seed_1 | 180 | 172 | 0.8761 | 0.7644 | 0.7685 | 0.7556 | 0.9278 | 0.8056 | 0.1869 | 2.161 | 0.8 | 0.8333 | 0.8899 | 0.002625 | 305.1 |
| train | gnn_seed_2 | 180 | 172 | 0.8801 | 0.7748 | 0.7792 | 0.7667 | 0.9222 | 0.8167 | 0.1722 | 2.161 | 0.8 | 0.8222 | 0.8949 | 0.002606 | 313.3 |
| train | gnn_seed_3 | 180 | 172 | 0.8742 | 0.7678 | 0.7722 | 0.7611 | 0.9278 | 0.8167 | 0.1778 | 2.161 | 0.8 | 0.8278 | 0.8911 | 0.002386 | 326.6 |
| train | gnn_seed_4 | 180 | 172 | 0.8816 | 0.7748 | 0.7792 | 0.7667 | 0.9222 | 0.8 | 0.184 | 2.161 | 0.8 | 0.8 | 0.8949 | 0.002396 | 323.2 |
| validation | baseline_midpoint | 90 | 84 | 0.4901 | 0.0 | 0.0 | 0.0 | 0.8667 | 0.0 | 0.881 | 2.144 | 0.6889 | 0.0 | 0.4858 | 0.003376 | 659.6 |
| validation | baseline_nearest_start | 90 | 84 | 0.8567 | 0.7222 | 0.7222 | 0.7 | 0.8667 | 0.7778 | 0.2222 | 2.144 | 0.6889 | 1 | 0.8745 | 0.003378 | 659.6 |
| validation | baseline_random | 90 | 84 | 0.4956 | 0.01111 | 0.01111 | 0.01111 | 0.8667 | 0.03333 | 0.93 | 2.144 | 0.6889 | 0.01111 | 0.4917 | 0.003378 | 661.5 |
| validation | baseline_topology | 90 | 84 | 0.5656 | 0.1444 | 0.1444 | 0.1333 | 0.8667 | 0.1333 | 0.6584 | 2.144 | 0.6889 | 0.1333 | 0.5667 | 0.003379 | 661.8 |
| validation | gnn_ensemble | 90 | 84 | 0.8713 | 0.7491 | 0.7583 | 0.7111 | 0.9 | 0.8111 | 0.1889 | 2.144 | 0.6889 | 0.7333 | 0.8853 | 0.007524 | 288.5 |
| validation | gnn_ensemble_top1 | 90 | 84 | 0.8558 | 0.725 | 0.725 | 0.7111 | 0.8667 | 0.7667 | 0.2333 | 2.144 | 0.6889 | 0.7333 | 0.8734 | 0.007524 | 288.5 |
| validation | gnn_ensemble_top2 | 90 | 84 | 0.6674 | 0.3883 | 0.7639 | 0.0 | 0.03333 | 0.8111 | 0.1889 | 2.144 | 0.6889 | 0.0 | 0.6781 | 0.007524 | 288.5 |
| validation | gnn_ensemble_top3 | 90 | 84 | 0.5609 | 0.2906 | 0.8111 | 0.0 | 0.04444 | 0.8444 | 0.1556 | 2.144 | 0.6889 | 0.0 | 0.5636 | 0.007524 | 288.5 |
| validation | gnn_seed_0 | 90 | 84 | 0.8613 | 0.7361 | 0.7361 | 0.7222 | 0.8667 | 0.7889 | 0.2111 | 2.144 | 0.6889 | 0.7333 | 0.8794 | 0.004441 | 490 |
| validation | gnn_seed_1 | 90 | 84 | 0.8643 | 0.7389 | 0.7454 | 0.7111 | 0.8889 | 0.8 | 0.2 | 2.144 | 0.6889 | 0.7333 | 0.8814 | 0.004132 | 533.8 |
| validation | gnn_seed_2 | 90 | 84 | 0.8742 | 0.7748 | 0.7889 | 0.7333 | 0.8778 | 0.8333 | 0.1667 | 2.144 | 0.6889 | 0.7333 | 0.8941 | 0.004061 | 539.7 |
| validation | gnn_seed_3 | 90 | 84 | 0.8622 | 0.7511 | 0.7639 | 0.7222 | 0.9 | 0.7889 | 0.1889 | 2.144 | 0.6889 | 0.7222 | 0.8813 | 0.004102 | 539.4 |
| validation | gnn_seed_4 | 90 | 84 | 0.8667 | 0.7526 | 0.7667 | 0.7111 | 0.9 | 0.8111 | 0.1889 | 2.144 | 0.6889 | 0.7111 | 0.8862 | 0.004192 | 525.4 |

## Training Runs

| training_seed | best_epoch | best_validation_score | epochs_run | training_time_sec |
| --- | --- | --- | --- | --- |
| 0 | 8 | 1.39 | 33 | 11.9 |
| 1 | 10 | 1.392 | 35 | 12.27 |
| 2 | 12 | 1.427 | 37 | 13.15 |
| 3 | 11 | 1.393 | 36 | 14.5 |
| 4 | 14 | 1.403 | 39 | 14.04 |

The selection speedup charges graph encoding, candidate-mask construction, and GNN forward time, but not the subsequent group audit or final graph-kernel construction. Those are evaluated separately by the downstream audit.

Teacher source: `experiments/output/boundary_heatmap_teacher_graphonly/boundary_heatmap_contexts.csv`
