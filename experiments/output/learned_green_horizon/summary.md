# Trainable Green Horizon Pilot

Generated: 2026-07-10T22:47:06

This pilot asks whether the truncation horizon can be amortized from one graph-level observation. A NumPy ridge model predicts K from transition-graph summaries; a split-conformal upper residual makes the proposal conservative. The proposal never replaces the frontier certificate: failed proposals grow geometrically and are re-audited.

target coverage = 0.95, learned upper residual = 36.2365, tail tolerance = 1e-06

## Prediction

| split | n_rows | n_nontrivial | median_required_k | median_proposed_k | base_mae | proposal_mae | proposal_coverage | median_excess_steps | p95_excess_steps | median_continuation_steps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 105 | 96 | 46.5 | 84 | 3.177 | 36.76 | 1 | 37 | 43 | 0.0 |
| calibration | 15 | 12 | 75 | 103 | 14.08 | 22 | 1 | 25 | 36 | 0.0 |
| test | 60 | 54 | 117 | 150.5 | 18.59 | 28.52 | 0.9259 | 26 | 68 | 0.0 |

## Execution

| n_test_rows | proposal_first_pass_rate | final_certificate_rate | median_fixed_time_sec | median_adaptive_time_sec | median_learned_time_sec | median_learned_speedup_vs_fixed | median_learned_speedup_vs_adaptive | min_proposal_boundary_jaccard | min_corrected_boundary_jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | 0.9333 | 1 | 0.03348 | 0.02647 | 0.03967 | 0.9063 | 0.7468 | 1 | 1 |

The fixed baseline deliberately executes every term through fixed K with no early stopping. The adaptive baseline is the current production behavior and checks the frontier every step. The learned implementation is a correctness-first prototype that restarts after an underprediction; a continuation implementation would remove that retry overhead.

## Held-Out Rows

| map | slip | required_k | proposed_k | learned_final_k | learned_attempts | learned_certified | learned_speedup_vs_fixed | learned_speedup_vs_adaptive | proposal_boundary_jaccard | corrected_boundary_jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_256 | 0.0 | 0 | 0 | 0 | 1 | True | 0.3866 | 0.2976 | 1 | 1 |
| corridor_256 | 0.05 | 0 | 0 | 0 | 1 | True | 0.3844 | 0.3625 | 1 | 1 |
| corridor_256 | 0.1 | 0 | 0 | 0 | 1 | True | 0.3895 | 0.3556 | 1 | 1 |
| corridor_512 | 0.0 | 0 | 0 | 0 | 1 | True | 0.3829 | 0.2953 | 1 | 1 |
| corridor_512 | 0.05 | 0 | 0 | 0 | 1 | True | 0.387 | 0.3595 | 1 | 1 |
| corridor_512 | 0.1 | 0 | 0 | 0 | 1 | True | 0.4036 | 0.368 | 1 | 1 |
| open_room_20 | 0.0 | 39 | 72 | 72 | 1 | True | 0.9199 | 0.6817 | 1 | 1 |
| open_room_20 | 0.05 | 57 | 86 | 86 | 1 | True | 0.9052 | 0.7462 | 1 | 1 |
| open_room_20 | 0.1 | 67 | 100 | 100 | 1 | True | 0.904 | 0.7668 | 1 | 1 |
| open_room_24 | 0.0 | 47 | 72 | 72 | 1 | True | 0.8838 | 0.6781 | 1 | 1 |
| open_room_24 | 0.05 | 67 | 87 | 87 | 1 | True | 0.877 | 0.753 | 1 | 1 |
| open_room_24 | 0.1 | 78 | 102 | 102 | 1 | True | 0.8587 | 0.7492 | 1 | 1 |
| open_room_32 | 0.0 | 63 | 63 | 63 | 1 | True | 0.8703 | 0.6384 | 1 | 1 |
| open_room_32 | 0.05 | 85 | 80 | 160 | 2 | True | 0.4329 | 0.3667 | 1 | 1 |
| open_room_32 | 0.1 | 98 | 98 | 98 | 1 | True | 0.8286 | 0.8049 | 1 | 1 |
| four_rooms_19 | 0.0 | 37 | 68 | 68 | 1 | True | 0.9154 | 0.6605 | 1 | 1 |
| four_rooms_19 | 0.05 | 56 | 82 | 82 | 1 | True | 0.9235 | 0.7355 | 1 | 1 |
| four_rooms_19 | 0.1 | 66 | 96 | 96 | 1 | True | 0.9197 | 0.7509 | 1 | 1 |
| four_rooms_21 | 0.0 | 41 | 67 | 67 | 1 | True | 0.9117 | 0.6808 | 1 | 1 |
| four_rooms_21 | 0.05 | 61 | 82 | 82 | 1 | True | 0.9043 | 0.7574 | 1 | 1 |
| four_rooms_21 | 0.1 | 71 | 96 | 96 | 1 | True | 0.9217 | 0.7639 | 1 | 1 |
| four_rooms_31 | 0.0 | 61 | 55 | 110 | 2 | True | 0.4668 | 0.3665 | 1 | 1 |
| four_rooms_31 | 0.05 | 84 | 72 | 144 | 2 | True | 0.4688 | 0.3999 | 1 | 1 |
| four_rooms_31 | 0.1 | 97 | 89 | 178 | 2 | True | 0.4636 | 0.3961 | 1 | 1 |
| maze_19_seed8 | 0.0 | 96 | 128 | 128 | 1 | True | 0.9994 | 0.728 | 1 | 1 |
| maze_19_seed8 | 0.05 | 120 | 150 | 150 | 1 | True | 1.038 | 0.7916 | 1 | 1 |
| maze_19_seed8 | 0.1 | 134 | 171 | 171 | 1 | True | 0.9376 | 0.7996 | 1 | 1 |
| maze_19_seed9 | 0.0 | 118 | 136 | 136 | 1 | True | 0.9033 | 0.669 | 1 | 1 |
| maze_19_seed9 | 0.05 | 144 | 155 | 155 | 1 | True | 0.9752 | 0.8234 | 1 | 1 |
| maze_19_seed9 | 0.1 | 160 | 175 | 175 | 1 | True | 0.954 | 0.8114 | 1 | 1 |
| maze_19_seed10 | 0.0 | 90 | 117 | 117 | 1 | True | 1.036 | 0.7473 | 1 | 1 |
| maze_19_seed10 | 0.05 | 113 | 134 | 134 | 1 | True | 0.9518 | 0.7795 | 1 | 1 |
| maze_19_seed10 | 0.1 | 127 | 151 | 151 | 1 | True | 0.9894 | 0.8251 | 1 | 1 |
| maze_19_seed11 | 0.0 | 117 | 153 | 153 | 1 | True | 0.9474 | 0.763 | 1 | 1 |
| maze_19_seed11 | 0.05 | 143 | 178 | 178 | 1 | True | 0.931 | 0.8464 | 1 | 1 |
| maze_19_seed11 | 0.1 | 159 | 204 | 204 | 1 | True | 0.9155 | 0.8564 | 1 | 1 |
| maze_21_seed8 | 0.0 | 69 | 137 | 137 | 1 | True | 1.002 | 0.7423 | 1 | 1 |
| maze_21_seed8 | 0.05 | 90 | 156 | 156 | 1 | True | 0.6729 | 0.4881 | 1 | 1 |
| maze_21_seed8 | 0.1 | 102 | 174 | 174 | 1 | True | 0.9227 | 0.773 | 1 | 1 |
| maze_21_seed9 | 0.0 | 117 | 171 | 171 | 1 | True | 0.941 | 0.7363 | 1 | 1 |
| maze_21_seed9 | 0.05 | 143 | 196 | 196 | 1 | True | 0.94 | 0.8048 | 1 | 1 |
| maze_21_seed9 | 0.1 | 159 | 222 | 222 | 1 | True | 0.9032 | 0.7991 | 1 | 1 |
| maze_21_seed10 | 0.0 | 128 | 138 | 138 | 1 | True | 0.9163 | 0.6785 | 1 | 1 |
| maze_21_seed10 | 0.05 | 154 | 157 | 157 | 1 | True | 0.8995 | 0.7509 | 1 | 1 |
| maze_21_seed10 | 0.1 | 171 | 177 | 177 | 1 | True | 0.8963 | 0.7441 | 1 | 1 |
| maze_21_seed11 | 0.0 | 128 | 164 | 164 | 1 | True | 0.9409 | 0.7351 | 1 | 1 |
| maze_21_seed11 | 0.05 | 155 | 189 | 189 | 1 | True | 0.9268 | 0.8085 | 1 | 1 |
| maze_21_seed11 | 0.1 | 172 | 215 | 215 | 1 | True | 0.9075 | 0.8186 | 1 | 1 |
| maze_25_seed8 | 0.0 | 176 | 183 | 183 | 1 | True | 0.8814 | 0.7104 | 1 | 1 |
| maze_25_seed8 | 0.05 | 205 | 212 | 212 | 1 | True | 0.908 | 0.7922 | 1 | 1 |
| maze_25_seed8 | 0.1 | 225 | 241 | 241 | 1 | True | 0.8695 | 0.8074 | 1 | 1 |
| maze_25_seed9 | 0.0 | 198 | 209 | 209 | 1 | True | 0.8576 | 0.7312 | 1 | 1 |
| maze_25_seed9 | 0.05 | 228 | 242 | 242 | 1 | True | 0.8595 | 0.8097 | 1 | 1 |
| maze_25_seed9 | 0.1 | 249 | 275 | 275 | 1 | True | 0.8338 | 0.8462 | 1 | 1 |
| maze_25_seed10 | 0.0 | 104 | 131 | 131 | 1 | True | 0.9745 | 0.7077 | 1 | 1 |
| maze_25_seed10 | 0.05 | 129 | 148 | 148 | 1 | True | 0.892 | 0.7437 | 1 | 1 |
| maze_25_seed10 | 0.1 | 144 | 165 | 165 | 1 | True | 0.9221 | 0.7794 | 1 | 1 |
| maze_25_seed11 | 0.0 | 97 | 161 | 161 | 1 | True | 0.9402 | 0.7251 | 1 | 1 |
| maze_25_seed11 | 0.05 | 121 | 184 | 184 | 1 | True | 0.9216 | 0.7849 | 1 | 1 |
| maze_25_seed11 | 0.1 | 135 | 207 | 207 | 1 | True | 0.8895 | 0.7945 | 1 | 1 |
