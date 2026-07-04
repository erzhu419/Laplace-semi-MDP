# Bellman-Kron 第一轮 ablation

Generated: 2026-07-04T18:48:06
gamma = 0.97, slips = [0.0, 0.05], edge_threshold = 1e-05

## 读数方式

`bellman_error_max` 检查固定 boundary/option 后，Schur complement 是否精确保留 Bellman backup；它应该接近数值零。`start_gap` 和 `value_gap_max` 才是抽象图加 option set 能不能表达原始最优控制的指标。

## 总体 sanity

- 最大 Bellman preservation error: `1.421e-14`。
- 最小 start planning gap: `0.000e+00`。
- `targeted` option set 允许每个 boundary 有一个到目标 boundary 的反馈策略；它能测试“很粗的图 + 很强的 option model”上限，但会把复杂性藏进 option policy。
- `directional` option set 更接近原始 primitive control；如果它在压缩后有 gap，通常说明 option set 不够表达高层最优控制，而不是 reduction 公式错了。

## 每个地图/噪声下的最佳配置

| map | slip | selector | option_set | n_states | n_boundary | n_options | compression_ratio | start_gap | value_gap_max | bellman_error_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 11 | 2 | 2 | 0.1818 | 0.0e+00 | 0.0e+00 | 1.8e-15 |
| corridor | 0.05 | all | directional | 11 | 11 | 4 | 1 | 7.1e-15 | 7.1e-15 | 0.0e+00 |
| four_rooms | 0.0e+00 | endpoints | targeted | 51 | 2 | 2 | 0.03922 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.05 | all | directional | 51 | 51 | 4 | 1 | 3.6e-15 | 7.1e-15 | 0.0e+00 |
| maze | 0.0e+00 | all | directional | 81 | 81 | 4 | 1 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| maze | 0.05 | all | directional | 81 | 81 | 4 | 1 | 1.8e-14 | 2.8e-14 | 0.0e+00 |
| open_room | 0.0e+00 | endpoints | targeted | 35 | 2 | 2 | 0.05714 | 0.0e+00 | 0.0e+00 | 3.6e-15 |
| open_room | 0.05 | all | directional | 35 | 35 | 4 | 1 | 0.0e+00 | 3.6e-15 | 0.0e+00 |

## 压缩配置里的前沿样例

| map | slip | selector | option_set | n_states | n_boundary | n_options | n_edges_valid | start_gap | value_gap_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor | 0.0e+00 | endpoints | targeted | 11 | 2 | 2 | 2 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | junction | targeted | 11 | 2 | 2 | 2 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | decision | targeted | 11 | 2 | 2 | 2 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | endpoints | targeted | 35 | 2 | 2 | 2 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | endpoints | targeted | 51 | 2 | 2 | 2 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | endpoints | directional | 11 | 2 | 4 | 8 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | junction | directional | 11 | 2 | 4 | 8 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | decision | directional | 11 | 2 | 4 | 8 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | junction | directional | 35 | 33 | 4 | 128 | 0.0e+00 | 0.0e+00 |
| open_room | 0.0e+00 | junction | targeted | 35 | 33 | 33 | 1056 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | junction | directional | 51 | 44 | 4 | 164 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | junction | targeted | 51 | 44 | 44 | 1892 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | decision | directional | 51 | 50 | 4 | 200 | 0.0e+00 | 0.0e+00 |
| four_rooms | 0.0e+00 | decision | targeted | 51 | 50 | 50 | 2450 | 0.0e+00 | 0.0e+00 |
| corridor | 0.0e+00 | spectral_25 | directional | 11 | 5 | 4 | 20 | 0.0e+00 | 8.9e-16 |
| corridor | 0.0e+00 | spectral_25 | targeted | 11 | 5 | 5 | 20 | 0.0e+00 | 8.9e-16 |

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
3. 下一步不该只问“graph 更小吗”，而要问“graph 小了多少、option policy/model 花了多少复杂度、held-out rollout residual 是否仍然小”。
