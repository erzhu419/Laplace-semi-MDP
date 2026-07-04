# Bellman-Kron 第一轮 ablation

Generated: 2026-07-04T19:35:50
gamma = 0.97, slips = [0.0, 0.05], edge_threshold = 1e-05
local_horizon = 8.0, good_gap_threshold = 0.2
critical_kind = transition_entropy, critical_top_fraction = 0.15

## 读数方式

`bellman_error_max` 检查固定 boundary/option 后，Schur complement 是否精确保留 Bellman backup；它应该接近数值零。`start_gap` 和 `value_gap_max` 才是抽象图加 option set 能不能表达原始最优控制的指标。
`bypass_cost_*` 用 decision boundary 作为 hidden critical set，惩罚 option 穿过本该暴露给高层 planner 的状态；`policy_tv_total` 和 `policy_regions_total` 粗略惩罚 option 内部策略表的复杂度。
`description_length_proxy` 只是当前工作假设：`|B| + edges/|B| + |O| + 0.05*pairs + 0.20*policy_tv + 0.50*regions + bypass + 0.10*nonlocal`。

## 总体 sanity

- 最大 Bellman preservation error: `1.421e-14`。
- 最小 start planning gap: `0.000e+00`。
- `targeted` option set 允许每个 boundary 有一个到目标 boundary 的反馈策略；它能测试“很粗的图 + 很强的 option model”上限，但会把复杂性藏进 option policy。
- `local_targeted` 只允许 primitive distance 不超过 `local_horizon` 的 target option；不满足局部连通性的配置会被跳过。
- `directional` option set 更接近原始 primitive control；如果它在压缩后有 gap，通常说明 option set 不够表达高层最优控制，而不是 reduction 公式错了。

## 每个地图/噪声下的最佳配置

| map | slip | selector | option_set | n_states | n_boundary | n_options | compression_ratio | start_gap | value_gap_max | description_length_proxy | bellman_error_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 11 | 2 | 2 | 0.1818 | 0.0e+00 | 0.0e+00 | 8.3 | 1.8e-15 |
| corridor | 0.05 | all | directional | 11 | 11 | 4 | 1 | 7.1e-15 | 7.1e-15 | 30.47 | 0.0e+00 |
| four_rooms | 0.0e+00 | endpoints | targeted | 51 | 2 | 2 | 0.03922 | 0.0e+00 | 0.0e+00 | 25 | 0.0e+00 |
| four_rooms | 0.05 | all | directional | 51 | 51 | 4 | 1 | 3.6e-15 | 7.1e-15 | 82.49 | 0.0e+00 |
| maze | 0.0e+00 | all | directional | 81 | 81 | 4 | 1 | 0.0e+00 | 0.0e+00 | 107.2 | 0.0e+00 |
| maze | 0.05 | all | directional | 81 | 81 | 4 | 1 | 1.8e-14 | 2.8e-14 | 115.3 | 0.0e+00 |
| open_room | 0.0e+00 | endpoints | targeted | 35 | 2 | 2 | 0.05714 | 0.0e+00 | 0.0e+00 | 14 | 3.6e-15 |
| open_room | 0.05 | all | directional | 35 | 35 | 4 | 1 | 0.0e+00 | 3.6e-15 | 63.54 | 0.0e+00 |

## 压缩配置里的前沿样例

| map | slip | selector | option_set | n_states | n_boundary | n_options | n_edges_valid | critical_nonzero | start_gap | value_gap_max | bypass_cost_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 11 | 2 | 2 | 2 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | junction | targeted | 11 | 2 | 2 | 2 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | decision | targeted | 11 | 2 | 2 | 2 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | endpoints | targeted | 35 | 2 | 2 | 2 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | endpoints | targeted | 51 | 2 | 2 | 2 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | endpoints | directional | 11 | 2 | 4 | 8 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | junction | directional | 11 | 2 | 4 | 8 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | decision | directional | 11 | 2 | 4 | 8 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | junction | directional | 35 | 33 | 4 | 128 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | junction | targeted | 35 | 33 | 33 | 1056 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | junction | directional | 51 | 44 | 4 | 164 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | junction | targeted | 51 | 44 | 44 | 1892 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | decision | directional | 51 | 50 | 4 | 200 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | decision | targeted | 51 | 50 | 50 | 2450 | 0 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | spectral_25 | directional | 11 | 5 | 4 | 20 | 0 | 0.0e+00 | 8.9e-16 | 0.0e+00 |
| corridor | 0.0e+00 | spectral_25 | targeted | 11 | 5 | 5 | 20 | 0 | 0.0e+00 | 8.9e-16 | 0.0e+00 |

## 低复杂度配置

| map | slip | selector | option_set | n_boundary | n_options | option_pair_count | start_gap | description_length_proxy | bypass_cost_total | policy_tv_total | policy_regions_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 2 | 2 | 2 | 0.0e+00 | 8.3 | 0.0e+00 | 4 | 4 |
| corridor | 0.0e+00 | junction | targeted | 2 | 2 | 2 | 0.0e+00 | 8.3 | 0.0e+00 | 4 | 4 |
| corridor | 0.0e+00 | decision | targeted | 2 | 2 | 2 | 0.0e+00 | 8.3 | 0.0e+00 | 4 | 4 |
| maze | 0.0e+00 | endpoints | directional | 2 | 4 | 8 | 11.13 | 10.4 | 0.0e+00 | 0.0e+00 | 4 |
| four_rooms | 0.0e+00 | endpoints | directional | 2 | 4 | 8 | 21.76 | 10.4 | 0.0e+00 | 0.0e+00 | 4 |
| open_room | 0.0e+00 | endpoints | directional | 2 | 4 | 8 | 24.58 | 10.4 | 0.0e+00 | 0.0e+00 | 4 |
| maze | 0.0e+00 | junction | directional | 4 | 4 | 16 | 11.13 | 12.3 | 0.0e+00 | 0.0e+00 | 4 |
| corridor | 0.05 | endpoints | targeted | 2 | 2 | 2 | 1.2e-11 | 12.67 | 3.409 | 3.933 | 4 |
| corridor | 0.05 | junction | targeted | 2 | 2 | 2 | 1.2e-11 | 12.67 | 3.409 | 3.933 | 4 |
| corridor | 0.05 | decision | targeted | 2 | 2 | 2 | 1.2e-11 | 12.67 | 3.409 | 3.933 | 4 |
| corridor | 0.0e+00 | endpoints | directional | 2 | 4 | 8 | 0.0e+00 | 12.8 | 0.0e+00 | 0.0e+00 | 4 |
| corridor | 0.0e+00 | junction | directional | 2 | 4 | 8 | 0.0e+00 | 12.8 | 0.0e+00 | 0.0e+00 | 4 |
| corridor | 0.0e+00 | decision | directional | 2 | 4 | 8 | 0.0e+00 | 12.8 | 0.0e+00 | 0.0e+00 | 4 |
| open_room | 0.0e+00 | endpoints | targeted | 2 | 2 | 2 | 0.0e+00 | 14 | 0.0e+00 | 30 | 5 |
| corridor | 0.0e+00 | spectral_25 | directional | 5 | 4 | 20 | 0.0e+00 | 16 | 0.0e+00 | 0.0e+00 | 4 |
| open_room | 0.05 | endpoints | targeted | 2 | 2 | 2 | 0.0788 | 18.81 | 4.146 | 28.4 | 5 |

## start gap <= 0.2 的低复杂度候选

| map | slip | selector | option_set | n_boundary | n_options | start_gap | description_length_proxy | bypass_cost_total | policy_tv_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 2 | 2 | 0.0e+00 | 8.3 | 0.0e+00 | 4 |
| corridor | 0.0e+00 | junction | targeted | 2 | 2 | 0.0e+00 | 8.3 | 0.0e+00 | 4 |
| corridor | 0.0e+00 | decision | targeted | 2 | 2 | 0.0e+00 | 8.3 | 0.0e+00 | 4 |
| corridor | 0.05 | endpoints | targeted | 2 | 2 | 1.2e-11 | 12.67 | 3.409 | 3.933 |
| corridor | 0.05 | junction | targeted | 2 | 2 | 1.2e-11 | 12.67 | 3.409 | 3.933 |
| corridor | 0.05 | decision | targeted | 2 | 2 | 1.2e-11 | 12.67 | 3.409 | 3.933 |
| corridor | 0.0e+00 | endpoints | directional | 2 | 4 | 0.0e+00 | 12.8 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | junction | directional | 2 | 4 | 0.0e+00 | 12.8 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | decision | directional | 2 | 4 | 0.0e+00 | 12.8 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | endpoints | targeted | 2 | 2 | 0.0e+00 | 14 | 0.0e+00 | 30 |
| corridor | 0.0e+00 | spectral_25 | directional | 5 | 4 | 0.0e+00 | 16 | 0.0e+00 | 0.0e+00 |
| open_room | 0.05 | endpoints | targeted | 2 | 2 | 0.0788 | 18.81 | 4.146 | 28.4 |
| corridor | 0.05 | endpoints | directional | 2 | 4 | 5.4e-12 | 19.92 | 4.142 | 0.0e+00 |
| corridor | 0.05 | junction | directional | 2 | 4 | 5.4e-12 | 19.92 | 4.142 | 0.0e+00 |
| corridor | 0.05 | decision | directional | 2 | 4 | 5.4e-12 | 19.92 | 4.142 | 0.0e+00 |
| open_room | 0.0e+00 | spectral_25 | directional | 11 | 4 | 0.0e+00 | 22.38 | 0.0e+00 | 0.0e+00 |

## 非 corridor 且 start gap <= 0.2 的候选

| map | slip | selector | option_set | n_boundary | n_options | start_gap | description_length_proxy | bypass_cost_total | policy_tv_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room | 0.0e+00 | endpoints | targeted | 2 | 2 | 0.0e+00 | 14 | 0.0e+00 | 30 |
| open_room | 0.05 | endpoints | targeted | 2 | 2 | 0.0788 | 18.81 | 4.146 | 28.4 |
| open_room | 0.0e+00 | spectral_25 | directional | 11 | 4 | 0.0e+00 | 22.38 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | endpoints | targeted | 2 | 2 | 0.0e+00 | 25 | 0.0e+00 | 66 |
| four_rooms | 0.05 | endpoints | targeted | 2 | 2 | 0.1152 | 28.18 | 3.042 | 62 |
| maze | 0.0e+00 | decision | directional | 32 | 4 | 3.6e-15 | 48.4 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | junction | directional | 33 | 4 | 0.0e+00 | 49.48 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | all | directional | 35 | 4 | 0.0e+00 | 52 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | decision | directional | 35 | 4 | 0.0e+00 | 52 | 0.0e+00 | 0.0e+00 |
| open_room | 0.05 | junction | directional | 33 | 4 | 2.1e-12 | 61.36 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | junction | directional | 44 | 4 | 0.0e+00 | 62.53 | 0.0e+00 | 0.0e+00 |
| open_room | 0.05 | all | directional | 35 | 4 | 0.0e+00 | 63.54 | 0.0e+00 | 0.0e+00 |
| open_room | 0.05 | decision | directional | 35 | 4 | 0.0e+00 | 63.54 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | decision | directional | 50 | 4 | 0.0e+00 | 70 | 0.0e+00 | 0.0e+00 |
| maze | 0.0e+00 | endpoints | targeted | 2 | 2 | 3.6e-15 | 70 | 0.0e+00 | 134 |
| four_rooms | 0.0e+00 | all | directional | 51 | 4 | 0.0e+00 | 71.2 | 0.0e+00 | 0.0e+00 |

## endpoints + targeted 退化解探针

| map | slip | start_gap | description_length_proxy | bypass_cost_total | policy_tv_total | policy_regions_total |
| --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 0.0e+00 | 8.3 | 0.0e+00 | 4 | 4 |
| corridor | 0.05 | 1.2e-11 | 12.67 | 3.409 | 3.933 | 4 |
| four_rooms | 0.0e+00 | 0.0e+00 | 25 | 0.0e+00 | 66 | 11 |
| four_rooms | 0.05 | 0.1152 | 28.18 | 3.042 | 62 | 11 |
| maze | 0.0e+00 | 3.6e-15 | 70 | 0.0e+00 | 134 | 65 |
| maze | 0.05 | 2.8e-11 | 73.87 | 4.863 | 125.5 | 65 |
| open_room | 0.0e+00 | 0.0e+00 | 14 | 0.0e+00 | 30 | 5 |
| open_room | 0.05 | 0.0788 | 18.81 | 4.146 | 28.4 | 5 |

## 全配置 Pareto front 近似

| map | slip | selector | option_set | n_boundary | n_options | start_gap | description_length_proxy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 2 | 2 | 0.0e+00 | 8.3 |

## all-boundary primitive sanity baseline

| map | slip | n_states | n_boundary | n_options | start_gap | value_gap_max | bellman_error_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | 11 | 11 | 4 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| corridor | 0.05 | 11 | 11 | 4 | 7.1e-15 | 7.1e-15 | 0.0e+00 |
| four_rooms | 0.0e+00 | 51 | 51 | 4 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.05 | 51 | 51 | 4 | 3.6e-15 | 7.1e-15 | 0.0e+00 |
| maze | 0.0e+00 | 81 | 81 | 4 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| maze | 0.05 | 81 | 81 | 4 | 1.8e-14 | 2.8e-14 | 0.0e+00 |
| open_room | 0.0e+00 | 35 | 35 | 4 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| open_room | 0.05 | 35 | 35 | 4 | 0.0e+00 | 3.6e-15 | 0.0e+00 |

## 初步解释

1. Bellman-Kron 本身在所有设置下都是代数精确的；如果 planning gap 出现，优先怀疑 boundary/option 选择，而不是 Schur complement。
2. `endpoints + targeted` 往往会非常强，因为一个 option 可以携带完整的闭环路径策略；这证明 compact graph 可行，但也暴露了必须正则化 option 复杂度。
3. complexity-aware 指标会把“图很小但 option 跨过大量 decision states”的方案显式标出来；这一步不是最终 objective，而是防止退化解的第一根尺子。
4. 下一步不该只问“graph 更小吗”，而要问“graph 小了多少、option policy/model 花了多少复杂度、held-out rollout residual 是否仍然小”。
