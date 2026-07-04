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

## 9. GPT_answer_1 后的推进

GPT 的反驳基本成立：只看 planning gap 和 Bellman preservation 会偏向把复杂性藏进 option。
所以目标应该从“最小 graph”改成“最小 graph-option 总描述长度，在 held-out planning/model/SMDP consistency 误差受控下”。

我先把最直接的三个建议落进实验：

```text
experiments/run_ablation.py
experiments/output/ablation_complexity/results.csv
experiments/output/ablation_complexity/results.json
experiments/output/ablation_complexity/summary.md
```

新增内容：

```text
option set:
  local_targeted

metrics:
  policy_tv_total
  policy_regions_total
  bypass_cost_mean / bypass_cost_total
  nonlocal_cost
  description_length_proxy
```

当前 proxy 是工作假设，不是最终理论：

```text
description_length_proxy =
  |B|
  + n_edges_valid / |B|
  + |O|
  + 0.05 * option_pair_count
  + 0.20 * policy_tv_total
  + 0.50 * policy_regions_total
  + bypass_cost_total
  + 0.10 * nonlocal_cost
```

第一轮结果：

```text
max Bellman preservation error ~= 1.42e-14
```

所以代数部分仍然是对的。新指标主要揭示 option 是否“过强”：

```text
maze, slip=0.05:
  endpoints + targeted:
    start_gap ~= 2.76e-11
    description_length_proxy ~= 85.26
    bypass_cost_total ~= 16.25
    policy_tv_total ~= 125.47

  all + directional:
    start_gap ~= 1.78e-14
    description_length_proxy ~= 115.30
    bypass_cost_total = 0
    policy_tv_total = 0

  decision + directional:
    start_gap ~= 1.20
    description_length_proxy ~= 56.27
    bypass_cost_total = 0
    policy_tv_total = 0

  decision + local_targeted:
    start_gap ~= 0.011
    description_length_proxy ~= 1018.51
    bypass_cost_total = 0
    policy_tv_total ~= 2011.40
```

解释：

1. `endpoints + targeted` 的确能在 maze 上保持低 gap，但它的 policy table 非常复杂，已经被 `policy_tv/regions`
   抓出来；它不是免费的 2-node graph。
2. `decision + directional` 很便宜，但 stochastic maze 下表达力不足，gap 仍有约 `1.20`。
3. `local_targeted` 能修掉一部分 directional 的表达力问题，但如果给每个 boundary 都配一个 shortest-path policy，
   policy complexity 会爆炸；这说明下一步不能简单加 all local goal-conditioned options。
4. open room 暴露了另一个问题：用 `decision_boundary_states` 当 hidden critical set 会把很多 2D 自由空间状态也当成
   “必须暴露的决策点”，这会高估 bypass cost。critical saliency 需要换成 bottleneck/value/model-uncertainty，
   而不能只靠 degree。

因此下一步不应该继续堆 option，而应该做两个更针对性的实验：

```text
Experiment F:
  用 bottleneck / value-gradient / transition-entropy 定义 c_crit(s)，
  替代现在粗糙的 degree-based decision critical set。

Experiment G:
  greedy split on bypass:
    从 endpoints 开始；
    找出当前 best option 轨迹里贡献最高的 hidden critical state；
    加入 B；
    直到 bypass 或 planning gap 降到阈值。
```

这会把 GPT 说的原则落成可检验机制：

```text
option 可以长，
但不应该免费跨过本该给高层 planner 决策的状态。
```

## 10. critical saliency 与 greedy split 结果

我把 `c_crit(s)` 做成了可选 saliency：

```text
critical_kind:
  decision
  bottleneck
  betweenness
  value_gradient
  transition_entropy
  combined
```

其中当前最有用的是 `bottleneck`。它不是简单用 degree 判断，而是：

```text
articulation / high-betweenness narrow states
```

并且会避免把整片 open room 都当成 hidden critical set。对比 `endpoints + targeted, slip=0.05`：

```text
critical = bottleneck:
  open_room bypass ~= 0.29
  four_rooms bypass ~= 5.05
  maze bypass ~= 1.88

critical = value_gradient:
  open_room bypass ~= 3.35
  four_rooms bypass ~= 3.91
  maze bypass ~= 6.29

critical = transition_entropy:
  open_room bypass ~= 4.15
  four_rooms bypass ~= 3.04
  maze bypass ~= 4.86
```

解释：

1. `bottleneck` 更像结构性抽象图的 saliency：open room 低、four rooms 和 maze 非零。
2. `value_gradient` 更 task-specific，会把 open room 中沿 goal 方向的路径也算进去。
3. `transition_entropy` 在 deterministic 时几乎没用，在 slip 下会惩罚受噪声/墙影响的位置，但不一定等于抽象图节点。

新增输出：

```text
experiments/output/ablation_bottleneck/
experiments/output/ablation_value_gradient/
experiments/output/ablation_transition_entropy/
```

我还实现了 greedy split：

```text
experiments/run_greedy_split.py
experiments/output/greedy_split_bottleneck/trace.csv
experiments/output/greedy_split_bottleneck/trace.json
experiments/output/greedy_split_bottleneck/summary.md
```

算法：

```text
初始化:
  B = {S, G}

循环:
  1. 构建 targeted option Bellman-Kron SMDP
  2. 对所有有效 (boundary, option) 聚合 discounted interior occupancy
  3. 找 occupancy * c_crit 最大的 hidden state
  4. 把它加入 B
  5. 直到 bypass_cost_total ~= 0 或达到 max_splits
```

`bottleneck` 下的 greedy split 结果：

```text
corridor:
  B = 2, 不拆，bypass = 0

open_room:
  B = 7, bypass -> 0
  但这说明当前 bottleneck 仍会选一些边界/中心通路点；open room 是否应该拆，取决于我们是否允许 global targeted policy。

four_rooms:
  B = 6 deterministic, B = 10 with slip
  split 主要集中在门/门附近，比如 (3,5), (3,7), (2,5), (4,7)

maze:
  B = 13
  split 主要集中在窄通道和高 betweenness 转折点，比如 (5,19), (5,17), (5,3), (5,1), (5,7), (5,5), (7,5), ...
```

一个重要观察：

```text
bypass_cost_total 不一定单调下降
```

因为每次加 boundary 后，targeted option 数量和有效 option pairs 都变多了，新的 source-target pair 会产生新的 bypass。
最终能清零，是因为所有被当前 saliency 标记的重要 hidden states 都被加入了 `B`。

这一步的结论不是“greedy split 已经找到最终算法”，而是：

```text
critical saliency + discounted occupancy attribution 可以作为 split 机制；
但还必须同时约束 option policy complexity，否则 targeted options 仍然可以让 policy_tv 爆炸。
```

下一步应该把 split 目标从单一 bypass 改成：

```text
choose split state that most improves:
  planning_gap
  + lambda_bypass * bypass_cost
  + lambda_policy * policy_complexity
  + lambda_graph * graph_size
```

并新增一个更公平的 option set：

```text
first_boundary_targeted:
  朝 target 走，
  但一旦 hit 任意 current boundary 就终止；
  如果跨过第三个 boundary，说明 B 不够细或 option 不合法。
```

这会比现在的 global `targeted` 更接近“local controller”，也更符合 SMDP graph fusion 的目标。

## 11. multi-objective split 结果

我把 `experiments/run_greedy_split.py` 扩展成两种 split 策略：

```text
split_strategy:
  bypass_attribution
  weighted_objective
```

`bypass_attribution` 是上一轮的 pure bypass greedy：每次直接加入
`discounted occupancy * c_crit` 最大的 hidden state。

`weighted_objective` 会先把候选 split state 逐个加入 `B`，重新构建 Bellman-Kron SMDP，
然后只接受能降低目标函数的 split：

```text
J =
  100 * start_gap
  + 10 * value_gap
  + 100 * bypass_cost
  + 0.2 * policy_cost_total
  + graph_cost
  + option_cost
  + 0.1 * nonlocal_cost
```

其中：

```text
graph_cost = |B| + n_edges_valid / |B|
option_cost = |O| + 0.05 * option_pair_count
policy_cost_total = 0.20 * policy_tv_total + 0.50 * policy_regions_total
```

新增输出：

```text
experiments/output/greedy_split_bypass_bottleneck_v2/
experiments/output/greedy_split_weighted_bottleneck/
experiments/output/greedy_split_weighted_mean_bottleneck/
```

和 pure bypass 相比，weighted objective 已经出现了有信息量的分歧：

```text
pure bypass:
  open_room slip=0.00: B=7,  bypass=0,      DL=56.80
  open_room slip=0.05: B=7,  bypass=0,      DL=73.49
  four_rooms slip=0.05: B=10, bypass=0,     DL=161.13
  maze slip=0.00: B=13, bypass=0,           DL=442.40
  maze slip=0.05: B=13, bypass=0,           DL=449.66

weighted objective:
  open_room slip=0.00: B=2, bypass=0.287,   DL=14.29
  open_room slip=0.05: B=2, bypass=0.288,   DL=14.95
  four_rooms slip=0.05: B=6, bypass=0.017,  DL=89.06
  maze slip=0.00: B=4, bypass=1.449,        DL=141.65
  maze slip=0.05: B=4, bypass=1.423,        DL=142.13
```

这说明 multi-objective split 已经能避免 pure bypass 的一个坏倾向：

```text
不要为了把 saliency 清零而在 open room 或 noisy four_rooms 里继续拆无意义节点。
```

但它也暴露了下一个核心问题：

```text
在 maze 里，weighted objective 停在 B=4，不愿继续拆到 B=13。
```

这不一定是错的。它可能说明：

1. 当前 `global targeted` option set 仍然把规划能力藏进 option policy；
2. `policy_cost_total` 和 `option_cost` 随 `|B|` 增长太快，压过了继续降低 bypass 的收益；
3. `bypass_cost` 可能不应该只是 soft regularizer，而应该对 local controller 设置 hard constraint。

现在已经到了值得让 GPT 反驳的一步。建议拿下面三个问题问它：

```text
1. residual bypass 应该是 hard constraint，还是 weighted penalty？
2. policy complexity 应该按 total option library、mean per option，
   还是按 optimal abstract policy occupancy 加权？
3. first-candidate-boundary targeted option 应该怎么定义：
   是把跨过 B0 \ B 的 edge 判 invalid，还是先吸收到 hidden terminal 再触发 split？
```

我自己的判断是：下一步不能只调 lambda。应该实现一个 `candidate_boundary_targeted`
或 `bypass_gated_targeted` option set，让 option 不能穿过 `B0` 中的第三个 candidate boundary。
否则 multi-objective 会一直在“强 global option 很省 graph node”和“local graph 应该暴露结构”之间摇摆。
