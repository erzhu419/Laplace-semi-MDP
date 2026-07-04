# Bellman-Kron SMDP Fusion：实现与实验路线

这份笔记把 `GPT_roadmap.md` 最后那个回答落成一个可实验的路线。我的判断是：
应该先实现能严格检验的 Bellman-preserving 部分，再把它作为 oracle 去探索“如何学出正确的抽象图”。

## 1. 这个算子真正要保留什么

最后那个回答的方向是对的：这里最有用的不是普通图拉普拉斯 `L = D - W`，而是某个
option 诱导出的 Bellman 方程算子：

```text
L_gamma^o = I - gamma P^o
```

对一个 option `o`，把原始状态分成两类：

```text
B = 保留的边界/决策状态
I = 要消去的内部状态
```

对 `I` 做 Schur complement：

```text
L_bar_B^o = L_BB^o - L_BI^o (L_II^o)^-1 L_IB^o = I - Gamma_bar^o
```

其中：

```text
Gamma_bar^o =
    gamma P_BB^o
  + gamma^2 P_BI^o (I - gamma P_II^o)^-1 P_IB^o

R_bar_B^o =
    r_B^o
  + gamma P_BI^o (I - gamma P_II^o)^-1 r_I^o
```

于是高层 SMDP backup 是：

```text
Q(b, o) = R_bar^o(b) + sum_b' Gamma_bar^o[b,b'] V(b')
```

这里 `Gamma_bar^o[b,b']` 不是普通转移概率，而是折扣后的 hitting kernel：

```text
E[ gamma^tau 1{S_tau = b'} | S_0=b, o ]
```

当 `gamma = 1`，它退化成 hitting probability；对 `gamma` 求导可以得到 hitting time 的一阶矩。
所以这才是比较自然的“半马尔可夫拉普拉斯”。

## 2. 真正未知的部分

只要 `P^o`、`r^o` 和 `B` 已经给定，Bellman-Kron reduction 本身是精确代数。真正未知、
值得实验的是：

1. 如何选择保留节点 `B`。
2. 如何定义或学习 candidate options `o`。
3. 如何融合 boundary states，同时不破坏 Markov/SMDP consistency。
4. 如何从采样数据估计这些量，而不是依赖已知 tabular MDP。

所以实现上应该拆成两个算子：

```text
算子 A：根据 controllability / value / uncertainty / Markov test 选择与融合状态。
算子 B：用 Bellman-Kron 精确消去 interior states，得到 SMDP option edges。
```

算子 B 是确定的；算子 A 是研究问题。先把 B 做对，再用 B 检验 A。

## 3. 参考文献给出的约束

- Sutton, Precup, Singh：options 会诱导 SMDP；option model 存的是累计折扣奖励和
  `sum_k gamma^k p(s', k)`。
- Kron reduction：对 Laplacian 做 Schur complement 可以消去 interior nodes，并保留 boundary behavior。
- Laplacian Eigenmaps / Diffusion Maps：普通 Laplacian 适合做扩散几何和候选 landmark，但它本身不够做 Bellman-preserving fusion。
- Machado et al.：Laplacian eigenvectors 可以发现 eigenoptions；这适合发现 option direction，不等价于抽象图融合。
- Markov state abstraction / bisimulation：融合后的状态必须保留奖励和转移行为；这应该成为 split/merge 判据。
- SoRB / World Model as a Graph：replay-buffer graph 和 reachability metric 是后续从样本学习抽象图的自然路线。

## 4. 已经实现的最小实验

我加了一个 tabular gridworld 原型：

```text
experiments/bellman_kron.py
experiments/run_gridworld_bellman_kron.py
```

它做了这些事：

1. 构造一个迷宫式 gridworld。
2. 把起点、目标、死路、转弯、路口作为 boundary nodes。
3. 把长程方向动作 `N/S/W/E` 当作 candidate options。
4. 对每个 option 计算 `Gamma_bar`、`R_bar`、`I - Gamma_bar`、hitting probability、expected hitting time。
5. 在 reduced SMDP 上做 value iteration，并和原始 primitive MDP 的 value iteration 对比。
6. 导出抽象 boundary graph。

运行：

```bash
python3 experiments/run_gridworld_bellman_kron.py --gamma 0.97 --slip 0.0
python3 experiments/run_gridworld_bellman_kron.py --gamma 0.97 --slip 0.05 --out-dir experiments/output/gridworld_bellman_kron_slip005
```

当前 deterministic 结果：

```text
n_states = 81
n_boundary = 32
n_interior = 49
compression_ratio = 0.395
Bellman preservation error ~= 1e-15
SMDP vs primitive value gap ~= 7e-15
```

stochastic slip 的结果也很有意思：对每个固定 option，Bellman preservation 仍然接近 0；
但 reduced option graph 和 primitive MDP 的最优 value 出现 gap，因为“承诺沿一个方向走到下一个 boundary”
本身是受限控制器。这说明我们能把两个问题分开看：

```text
reduction 是否精确
option set 是否足够表达最优控制
```

输出文件：

```text
experiments/output/gridworld_bellman_kron/summary.json
experiments/output/gridworld_bellman_kron/edges.csv
experiments/output/gridworld_bellman_kron/boundary_values.csv
experiments/output/gridworld_bellman_kron/boundary_graph.png
```

## 5. 核心评价指标

实验应该一直盯着这些指标：

```text
Bellman preservation:
  max_B | Q_full(B, o; V_B) - (R_bar^o + Gamma_bar^o V_B) |

Monte Carlo SMDP model error:
  || rollout empirical estimates of (R_bar, Gamma_bar, tau) - reduced model ||

Planning gap:
  || V_full_primitive(B) - V_reduced_SMDP(B) ||

Compression:
  |B| / |S|, SMDP edges 数量, 平均 option duration

Merge consistency:
  sup_{z_i,z_j in cluster, o}
    |R_bar^o(z_i)-R_bar^o(z_j)|
    + ||Gamma_bar^o(z_i,.)-Gamma_bar^o(z_j,.)||_1
    + tau variance
```

第一项在已知模型的 tabular 实验里应该是 0；如果不是 0，就是实现错了。后面几项才说明抽象和 option set 是否真的有用。

## 6. 下一组实验

### Experiment A：tabular sanity checks

换多种地图：直走长廊、four rooms、带 loop 的 maze、stochastic slip。预期：
Bellman preservation 始终为数值零；compression 和 value gap 随 `B` 与 option set 改变。

### Experiment B：boundary selection ablation

比较不同 `B` 的选择方式：

```text
degree/turn heuristic
reward gradient
value gradient
transition entropy
betweenness/bottleneck score
Laplacian/diffusion landmark score
组合 score
```

好的 selector 不是“聚类图看起来漂亮”，而是在同样 compression ratio 下 planning gap 最小。

### Experiment C：option discovery ablation

比较 candidate options：

```text
directional options
shortest-path-to-nearest-boundary options
eigenoptions from graph Laplacian
goal-conditioned options from replay-buffer reachability
```

这个实验能回答 Laplacian 更适合用来找 option direction、boundary node，还是两者都找。

### Experiment D：sample-based estimation

停止使用真 `P`。用轨迹估计 `P_hat`、`r_hat`，再做 Bellman-Kron reduction，并用 held-out rollouts 检查误差。
高不确定性/高 rollout residual 的边应该被 split 或降权。

### Experiment E：online split/merge

从很粗的 `B` 开始。如果某条 reduced edge 的 rollout residual 或 duration variance 很高，
就在这条边中间加节点；只有 SMDP signature 足够接近时才 merge。

## 7. 最可能站得住的核心贡献

比较清楚的贡献表述是：

```text
Bellman-Kron SMDP Fusion:
  一个 discounted、reward-aware 的 Schur-complement 算子，
  能把 primitive-state MDP 区域折叠成 option-labeled SMDP graph edges，
  同时保留 boundary Bellman equations。
```

实验 claim 应该收窄成：

```text
给定 boundary selector 和 candidate options，Bellman-Kron 能给出 exact reduced SMDP model；
adaptive split/merge 再搜索一个 compact boundary set，使 planning error 低于阈值。
```

这样不会过度声称“Laplacian 自动找到了图”。更准确地说：

```text
Laplacian 是发现候选结构的工具；
Bellman preservation 才是判断抽象是否正确的不变量。
```

## 8. 第一轮 ablation 结果

我加入了一个更系统的 sweep：

```text
experiments/run_ablation.py
experiments/output/ablation/results.csv
experiments/output/ablation/results.json
experiments/output/ablation/summary.md
```

覆盖：

```text
maps:
  corridor, open_room, four_rooms, maze

slip:
  0.0, 0.05

boundary selectors:
  all, endpoints, junction, decision, spectral_25

option sets:
  directional
  targeted
```

主要结果：

```text
max Bellman preservation error across all conditions ~= 1.42e-14
```

这说明：给定 `B` 和 option model，Bellman-Kron reduction 的代数部分是对的。
planning gap 的变化来自 `B` 和 option set，而不是 reduction 公式。

几个有信息量的现象：

1. `all + directional` 在所有地图和 slip 下都等价于 primitive MDP，是 sanity baseline。
2. deterministic 地图里，如果 `B` 包含必要的转弯/路口，`decision + directional` 基本精确。
3. `endpoints + directional` 在 open room、four rooms、maze 上失败很明显，因为单个方向 option 不能表达需要转弯的路径。
4. stochastic slip 下，`decision + directional` 的 reduction 仍然精确，但不一定表达原始最优控制：
   maze 上 start gap 约 `1.20`，说明“承诺一个方向直到下个 boundary”比 primitive 每步纠偏更弱。
5. `targeted` feedback options 能把很多 gap 打到接近 0；但这也说明它可能把复杂性藏进 option policy。
   例如 `endpoints + targeted` 可以用 2 个 boundary 节点表示完整任务，这不能直接 claim 为“找到了好 graph”。

因此下一步目标要改成一个带复杂度约束的搜索问题：

```text
minimize:
  planning_gap(B, O)
  + lambda_graph * graph_complexity(B, edges)
  + lambda_option * option_complexity(O)
  + lambda_model * heldout_rollout_residual(B, O)
```

其中 `option_complexity` 至少应该惩罚：

```text
option 数量
option 平均 duration
option policy 是否是全局 goal-conditioned 闭环策略
option model 的有效 kernel entries
option 在 held-out rollout 上的 reward / hitting kernel residual
```

这里是一个需要外部 GPT 反驳/把关的问题：

```text
怎样定义一个公平的 option complexity regularizer，
避免 endpoints + one-goal-option 这种“把整个任务藏进 option”的退化解？
```

我的当前倾向是下一轮先做两件事：

1. 加一个 `local_targeted` option set：只允许去附近/相邻 boundary 的反馈 option，而不是 all-to-all target option。
2. 做 sample-based held-out residual：用 rollout 估计每条 reduced edge 的 reward、hitting kernel、duration，
   gap 高或 residual 高的边触发 split。
