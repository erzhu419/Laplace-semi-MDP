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

## 12. first-candidate-boundary targeted 结果

根据 `GPT_answer_2.md` 的建议，我实现了 pair-specific first-boundary option：

```text
experiments/run_first_boundary_targeted.py
```

语义是：

```text
给定 current boundary B 和 candidate boundary B0
对每个 pair (b -> g):
  policy 仍然朝 g 走
  但 termination 是 first hit of B0 \ {b}

如果 first terminal 在 B0 \ B:
  当前 edge invalid
  hidden terminal 作为 split_candidate
```

每条 edge 都输出：

```text
hidden_mass
hidden_gamma_mass
hidden_argmax_state / hidden_argmax_coord
edge_valid
split_candidate
```

输出目录：

```text
experiments/output/first_boundary_targeted_bottleneck/
experiments/output/first_boundary_targeted_turn_articulation/
experiments/output/first_boundary_targeted_turn_articulation_maze35/
```

### 12.1 bottleneck as hard B0

如果直接把上一轮 `bottleneck` saliency 当 hard `B0`，结果是：

```text
corridor:
  B = 2

open_room:
  B = 7

four_rooms:
  B = 6 deterministic, B = 10 with slip

maze:
  B = 13
```

这个和 pure bypass 很接近，说明：

```text
把 betweenness/bottleneck saliency 直接升级成 hard constraint 会让 open_room 过拆。
```

这验证了 GPT 的 hard/soft 分层建议：`bottleneck` 里有一部分应该是 soft saliency，
不能全部当 hard boundary。

### 12.2 turn_articulation as hard B0

我又加了一个更硬的 candidate selector：

```text
turn_articulation:
  endpoints
  + articulation points that are not straight corridor states
  + degree-2 turns
```

第一轮结果：

```text
corridor:
  B = 2

open_room:
  B = 4
  start_gap deterministic = 0
  start_gap slip=0.05 ~= 0.0788

four_rooms:
  B = 6 deterministic
  B = 10 slip=0.05

maze:
  max_splits=20 时还没清零 hidden crossing
```

然后我单独把 maze 跑到 `max_splits=35`：

```text
maze deterministic:
  B = 26, hidden_mass_max = 0, start_gap ~= 0

maze slip=0.05:
  B = 30, hidden_mass_max = 0, start_gap ~= 0
```

这一步的解释：

```text
first-boundary targeted 成功把 hidden-cross 从 soft cost 变成 hard legality；
只要某个 edge 会先撞到 B0 \ B，它就不能被当前 graph 当作合法 edge。
```

它也让退化解更清楚：

```text
endpoints + global_targeted:
  低 gap，但 edge 会穿过 hidden B0，因此 infeasible。

first-boundary targeted:
  初始 endpoints graph 通常 infeasible；
  必须逐步 split 到没有 hidden-cross，才得到合法 SMDP graph。
```

现在比较清楚的下一步是：

```text
保留 B0_hard = turn_articulation
保留 B0_soft = bottleneck/value_gradient/transition_entropy

edge validity:
  hidden_cross over B0_hard -> invalid
  hidden_cross / occupancy over B0_soft -> penalty + split priority
```

这样 open_room 不会因为 soft betweenness 过度拆，
maze/four_rooms 又能通过 hard first-boundary 约束杀掉 “one option solves the whole maze”。

## 13. hard/soft hybrid 结果

我把 `run_first_boundary_targeted.py` 扩展成 hybrid 模式：

```text
B0_hard:
  candidate_kind = turn_articulation

B0_soft:
  soft_kind = combined
  combined = bottleneck/value_gradient/transition_entropy

split:
  hard hidden-cross -> split
  soft saliency -> penalty/report only
```

运行命令：

```text
python3 experiments/run_first_boundary_targeted.py \
  --candidate-kind turn_articulation \
  --soft-kind combined \
  --soft-split-policy never \
  --slips 0.0 0.05 \
  --max-splits 30 \
  --out-dir experiments/output/first_boundary_hybrid_turn_soft_combined
```

输出：

```text
experiments/output/first_boundary_hybrid_turn_soft_combined/
```

最终行：

```text
corridor:
  B = 2
  hidden_mass_max = 0

open_room:
  B = 4
  hidden_mass_max = 0
  soft_cost_valid_total ~= 7.37 deterministic, 8.26 slip=0.05

four_rooms:
  B = 6 deterministic
  B = 10 slip=0.05
  hidden_mass_max = 0

maze:
  B = 26 deterministic
  B = 30 slip=0.05
  hidden_mass_max = 0
  soft_cost_valid_total ~= 158 deterministic, 293 slip=0.05
```

这轮正好得到我们想要的区分：

```text
hard B0 决定合法性：
  option 不能穿过 turn/articulation 后仍声称是当前 graph 的 direct edge。

soft B0 决定代价和诊断：
  value-gradient / transition-entropy / betweenness 不再强迫 open_room 继续 split。
```

我还修正了 first-boundary targeted 的 MDL 计费：

```text
pair-specific model / edge interface:
  按 n_pair_options 计费

internal policy library:
  按 target-policy library 计费
```

原因是 pair-specific reduction 的 terminal set 依赖 source-target pair，
但内部 shortest-path policy 是按 target 共享的；如果把 policy complexity 也按 pair 重复加总，
会严重高估 first-boundary option 的描述长度。

当前剩下的关键问题：

```text
maze 的 hard-feasible graph 仍然偏大：
  deterministic B=26
  slip B=30
```

这说明 `turn_articulation` 作为 hard B0 可能还是过细，尤其在 maze 里把很多普通转角都变成了必须显式暴露的 graph node。
下一步应该比较几种 hard B0：

```text
articulation_only:
  只把真正割点/门作为 hard boundary

turn_articulation:
  割点 + 转角

learned_hard:
  只把会造成 high hidden-cross + high planning gap 的 candidate 升级成 hard
```

我的判断是，最终版本应该是：

```text
hard:
  terminal / reward / reset / true bottleneck / high rollout residual

soft:
  turn / betweenness / value-gradient / transition-entropy
```

也就是说，turn 不应该天然 hard；它应该先是 soft，只有在 rollout residual 或 SMDP inconsistency 证明它必须被暴露时才升级。

## 14. hard B0 对比与 learned_hard 初版

我继续把 hard candidate selector 加成了：

```text
articulation_only:
  endpoints
  + articulation points that are not straight corridor states

turn_articulation:
  endpoints
  + articulation points that are not straight corridor states
  + degree-2 turns
```

并把 `learned_hard` 先实现成一个可跑的近似：

```text
initial hard B0 = articulation_only
soft saliency = combined
if max per-edge soft_cost > threshold:
  promote soft_argmax to boundary
  from then on it becomes an effective first-boundary terminal
```

对应输出：

```text
experiments/output/first_boundary_hybrid_articulation_soft_combined/
experiments/output/first_boundary_learned_hard_soft2/
experiments/output/first_boundary_learned_hard_soft3/
experiments/output/first_boundary_learned_hard_soft4/
experiments/output/first_boundary_hybrid_turn_soft_combined/
```

最终比较：

```text
articulation_only:
  open_room: B=2
  four_rooms: B=4
  maze: B=2

learned_hard, soft_threshold=2:
  open_room: B=2 deterministic, B=5 slip=0.05
  four_rooms: B=4
  maze: B=7 deterministic, B=9 slip=0.05

learned_hard, soft_threshold=3:
  open_room: B=2 deterministic, B=3 slip=0.05
  four_rooms: B=4
  maze: B=4 deterministic, B=7 slip=0.05

learned_hard, soft_threshold=4:
  open_room: B=2
  four_rooms: B=4
  maze: B=3 deterministic, B=2 slip=0.05

turn_articulation:
  open_room: B=4
  four_rooms: B=6 deterministic, B=10 slip=0.05
  maze: B=26 deterministic, B=30 slip=0.05
```

这组结果很有信息量：

1. `turn_articulation` 作为 hard B0 明显过细，尤其在 maze 里把几乎所有转角都强制暴露。
2. `articulation_only` 作为 hard B0 又太宽，maze 退回 `B=2`，说明它没有杀掉 global targeted 的隐藏规划。
3. `learned_hard` 介于二者之间，尤其 `soft_threshold=3` 当前看起来最合理：

```text
open_room:
  deterministic 不拆，slip=0.05 只加一个 soft point

four_rooms:
  只保留两个门点，B=4

maze:
  deterministic B=4
  slip=0.05 B=7
```

`learned_hard soft3` 选出的新增点：

```text
open_room slip=0.05:
  (5,3)

four_rooms:
  (3,7), (3,5)

maze deterministic:
  (6,19), (5,19)

maze slip=0.05:
  (5,7), (7,18), (7,17), (7,9), (7,16)
```

注意一个读数细节：

```text
soft split 是按 per-edge soft_cost_max 触发；
soft_cost_valid_total 可能在 split 后上升。
```

原因是加 boundary 会增加 pair-specific edges，因此 total soft exposure 不是单调量。
这和之前 pure bypass 的非单调现象一致。选择 split 时更应该看：

```text
per-edge violation
occupancy-weighted violation
feasible Pareto front
held-out residual
```

而不是要求 total soft cost 每步下降。

当前最清楚的下一步：

```text
把 learned_hard 的触发条件从 raw soft_cost_max
替换成:

  hinge(max_edge_soft_cost - epsilon_soft)
  + rollout/model residual
  + SMDP consistency residual

并报告 feasible Pareto front：
  hard hidden-cross = 0
  max soft violation <= threshold
  planning gap <= epsilon
  minimal MDL
```

如果暂时还没有 sample-based rollout residual，下一步可以先做一个 deterministic oracle residual：

```text
比较 pair-specific first-boundary edge model
和 global targeted edge model
在同一 source-target 上的 terminal distribution / reward 差异。
```

这个 residual 会直接量化“global option 到底隐藏了多少 first-boundary 结构”。

## 15. Edge-model residual: 用模型差异替代 raw soft cost

我把上面的 deterministic oracle residual 做进了
`experiments/run_first_boundary_targeted.py`。现在每条 pair-specific edge
都会同时算两个模型：

```text
global targeted edge:
  policy = shortest path to target
  absorbing = target only
  reduce onto current boundary B

first-boundary diagnostic edge:
  policy = same shortest path to target
  absorbing = residual candidate boundary B_res
  project first-hit terminal distribution back onto current B
```

然后比较两者在同一个 `(source, target)` 上的 terminal model：

```text
model_residual =
  ||Gamma_global(source, :) - Gamma_first_boundary_to_B(source, :)||_1
  + 0.05 * |R_global(source) - R_first_boundary(source)|
```

一开始只用 discounted terminal distribution 的 L1 residual，但是 maze
里的长路径被 `gamma^tau` 压得太厉害，反而没有稳定区分出来。因此加了一个
小权重的 reward residual。这个 reward residual 在当前 gridworld 里近似记录
global option 比 first-boundary model 多隐藏了多少步。

新增参数：

```text
--residual-kind
--residual-top-fraction
--residual-threshold
--residual-reward-weight
--residual-hit-weight
--residual-split-policy {never,threshold}
```

当前最有信息量的三组输出：

```text
diagnostic only:
  experiments/output/edge_model_residual_turn_diagnostic/

residual threshold = 1.0:
  experiments/output/edge_model_residual_learned_threshold1/

residual threshold = 1.2:
  experiments/output/edge_model_residual_learned_threshold12/

residual threshold = 1.1 / 1.3:
  experiments/output/edge_model_residual_learned_threshold11/
  experiments/output/edge_model_residual_learned_threshold13/

raw soft3 with residual diagnostics:
  experiments/output/first_boundary_learned_hard_soft3_with_residual/
```

关键对比：

```text
raw soft3:
  open_room slip=0.00  B=2
  open_room slip=0.05  B=3
  four_rooms           B=4
  maze slip=0.00       B=4, residual_max=1.345
  maze slip=0.05       B=7, residual_max=1.313

residual threshold = 1.2:
  open_room            B=2
  four_rooms           B=4
  maze                 B=14, residual_max<1.2

residual threshold = 1.3:
  open_room            B=2
  four_rooms           B=4
  maze slip=0.00       B=10, residual_max=1.284
  maze slip=0.05       B=6,  residual_max=1.299

residual threshold = 1.1:
  open_room            B=2
  four_rooms           B=4
  maze slip=0.00       B=21, residual_max=1.077
  maze slip=0.05       B=18, residual_max=1.096
```

这个结果比 raw soft 更符合现在的目标。raw soft3 看起来 compact，但是 residual
诊断显示 maze 里仍有 `model_residual_max > 1.3` 的 global option；也就是说
它还在隐藏 first-boundary 结构。另一方面，`turn_articulation` 作为 hard B0
会把 open/four_rooms/maze 都拆得太细。`residual_threshold=1.2` 目前正好介于
二者之间：不拆 open room，不把 four_rooms 拆过头，但会继续拆 maze 里的长隐藏
边界。

补充 sweep 后可以更准确地说：当前 knee 在 `epsilon_residual=1.2~1.3`。
`1.1` 已经明显过细；`1.3` 更 compact，但 deterministic maze 仍要拆到 `B=10`，
说明 residual 确实在惩罚 raw soft3 没看到的隐藏边界。接下来应该把 `1.2` 和
`1.3` 都保留为 Pareto candidates，而不是过早固定一个阈值。

需要注意：

```text
model_residual_valid_total 不是单调优化目标。
```

因为加 boundary 会增加 pair-specific edges，总 residual 可能上升。当前更适合
把 residual 当作 per-edge constraint：

```text
hidden_mass_max = 0
model_residual_max <= epsilon_residual
planning gap <= epsilon_value
在满足这些约束后最小化 MDL / graph size
```

下一步不应该再问“total residual 是否每一步下降”，而应该做 Pareto sweep：

```text
epsilon_residual in [0.9, 1.0, 1.1, 1.2, 1.3]
compare:
  B size
  model_residual_max
  start/value gap
  held-out target residual
  graph readability
```

这一步已经足够拿给 GPT 反驳/质询：为什么这个 residual 不是在重新发明 heuristic
bottleneck，而是真的在逼近“global option 隐藏的 first-boundary model error”。
我会优先让它攻击两个点：

```text
1. first-boundary diagnostic boundary B_res 是否本身带入了 heuristic bias？
2. residual threshold 是否应该按 task/discount/option duration 归一化？
```

## 16. GPT_answer_3 后续：value-impact normalization 与 sensitivity

`GPT_answer_3.md` 的主要反驳是：

```text
1. B_res 不是真实边界，而是一族 diagnostic lens。
2. raw residual threshold 不能跨 task / gamma / option duration 共用。
3. 应该报告 value-impact normalized residual、hidden-cross、planning gap、option complexity。
```

我先把新增参考处理完：

```text
reference/papers/why_trust_bellman_2022__why-should-i-trust-you-bellman-the-bellman-error-is-a-poor-replacement-for-value-error.pdf
reference/pages/why_trust_bellman_2022.html
reference/repos/sfujim__TD3/
reference/gpt_answer_3_download_report.md
```

然后在 `experiments/run_first_boundary_targeted.py` 里加了这些字段：

```text
residual_backup_raw
residual_backup_value
residual_backup_value_norm
residual_reward_per_discounted_step
residual_gamma_relative
residual_tau_relative
value_scale_task
beta_row
beta_global
l_gamma_row
expected_tau_global
expected_tau_residual
```

主 normalized residual 按 GPT 建议实现成：

```text
delta_value = |Delta R| + V_scale * ||Delta Gamma||_1
delta_value_norm = delta_value / ((1 - beta_row) * V_scale)

beta_row = sum_b' Gamma_global(b, b')
L_gamma = (1 - beta_row) / (1 - gamma)
```

CLI 新增：

```text
--residual-threshold-mode {raw,value_norm}
```

这使得同一份代码可以同时测试：

```text
raw structural residual split
value-impact normalized residual split
```

### 16.1 重要反例：value_norm 不能单独做 structural split

先跑 diagnostic：

```text
experiments/output/value_norm_residual_turn_diagnostic/
```

在 `B={start, goal}` 或 articulation-only hard 后，turn-articulation lens 下的
per-edge max 是：

```text
open_room:
  raw_max ~= 0.98 / 0.91
  value_norm_max ~= 4.95 / 4.45

four_rooms:
  raw_max ~= 1.01 / 0.98
  value_norm_max ~= 6.85 / 6.39

maze:
  raw_max ~= 1.35 / 1.33
  value_norm_max ~= 1.87 / 1.83
```

也就是说，value-impact normalization 把 maze 的长 option residual 压低了。
这在 value/planning error 语义上是合理的，因为长 option 的 SMDP contraction
更强；但在“不能把 boundary 结构藏进 global option”这个目标上，它会拆反。

我用 `--residual-threshold-mode value_norm --residual-threshold 4.0` 验证了这个
失败模式：

```text
experiments/output/value_norm_residual_threshold4/

open_room:
  B=4

four_rooms:
  B=6

maze:
  B=2
```

这正好和我们要的行为相反。它说明：

```text
value-impact residual 应该作为 planning/value diagnostic；
raw structural residual / hidden-cross 才应该负责 graph structure split。
```

这也和 GPT 自己的第 8 点一致：hidden-cross / bypass 不应该完全按 duration 归一化，
否则长 global option 会被稀释。

### 16.2 保留 raw residual 1.2，但补充 value fields

我用新字段重跑了 raw residual threshold 1.2：

```text
experiments/output/edge_model_residual_learned_threshold12_value_fields/
```

最终结果：

```text
open_room:
  B=2
  raw_max ~= 0.98 / 0.91
  value_norm_max ~= 4.95 / 4.45

four_rooms:
  B=4
  raw_max ~= 1.01 / 0.98
  value_norm_max ~= 6.85 / 6.39

maze:
  B=14
  raw_max ~= 1.17 / 1.19
  value_norm_max ~= 2.32 / 2.48
```

这个再次说明 raw residual 1.2 在当前 toy suite 上更像 structural graph splitter：
它保留 open_room / four_rooms 的 compact graph，同时强迫 maze 暴露中间结构。

### 16.3 B_res sensitivity script

按 GPT 建议，我加了：

```text
experiments/run_residual_sensitivity.py
```

它把同一个 learned graph 放到多个 residual probe lens 下评估：

```text
junction
decision
turn_articulation
bottleneck
combined
```

本轮输出：

```text
experiments/output/residual_probe_sensitivity/
```

比较的 recipe：

```text
soft3
raw_residual12
value_norm4
```

最关键的构造结果：

```text
soft3:
  open_room slip=0.00  B=2
  open_room slip=0.05  B=3
  four_rooms           B=4
  maze slip=0.00       B=4
  maze slip=0.05       B=7

raw_residual12:
  open_room            B=2
  four_rooms           B=4
  maze                 B=14

value_norm4:
  open_room            B=4
  four_rooms           B=6
  maze                 B=2
```

所以现在的结论更清楚：

```text
raw structural residual: good candidate for split pressure
value-impact normalized residual: good diagnostic / acceptance report
hidden-cross mass: separate structural validity channel
planning gap: necessary but insufficient
```

下一步应该把最终 acceptance rule 写成多通道，而不是单通道：

```text
valid if:
  hard hidden-cross <= epsilon_hidden
  raw structural residual <= epsilon_struct
  value-impact residual <= epsilon_value
  tau/duration residual <= epsilon_tau

select graph by:
  minimal graph / option description length among valid candidates
```

现在可以拿给 GPT 继续反驳的问题变成：

```text
如果 value-impact residual 单独会拆反，那么 structural residual 的 raw threshold
应该如何归一化，才能既不被 duration 稀释，又不变成 task-specific magic number？
```

## 17. GPT_answer_4 后续：undiscounted structural residual

`GPT_answer_4.md` 的核心建议是：

```text
structural residual 不应该用 gamma^tau，也不应该除以 duration。
它应该是 undiscounted first-hidden-boundary probability：

rho_struct(b,o) =
  Pr[first hit of (B_res union B) is in B_res \\ B]
```

我先补了新增 reference：

```text
reference/papers/bellman_residual_bad_proxy_2017__is-the-bellman-residual-a-bad-proxy.pdf
reference/pages/bellman_residual_bad_proxy_2017.html
reference/gpt_answer_4_download_report.md
```

这篇没有找到可靠的官方代码仓库。

### 17.1 实现

其实我们前面算的 `residual_hidden_mass` 已经接近这个定义：`first_hit_reduce`
里的 `hit_probability` 是 undiscounted first-hit distribution，不是
`gamma_terminal`。这轮我把它显式命名并加到 CSV：

```text
struct_hidden_prob
struct_hit_prob
struct_nohit_prob
struct_reference_prob
struct_hidden_norm
struct_hidden_bits
struct_hidden_distinct
struct_hidden_distinct_bits
```

新增 residual threshold mode：

```text
--residual-threshold-mode struct_prob
--residual-threshold-mode struct_bits
--residual-threshold-mode struct_distinct
```

其中：

```text
struct_hidden_norm =
  max(0, (struct_hidden_prob - struct_reference_prob) / (1 - struct_reference_prob))

struct_hidden_bits =
  -log2(1 - struct_hidden_norm + eps)
```

`struct_hidden_distinct` 默认不算，因为它要对每个 hidden candidate 单独做一次
first-hit solve；需要时用：

```text
--compute-struct-distinct
```

### 17.2 第一发现：struct_prob 不会被 duration 洗掉，但会饱和

输出：

```text
experiments/output/struct_first_hit_turn_diagnostic_v2/
```

turn-articulation lens 下：

```text
open_room:
  struct_hidden_prob_max ~= 1.00 / 0.936

four_rooms:
  struct_hidden_prob_max ~= 1.00 / 0.966

maze:
  struct_hidden_prob_max ~= 1.00 / 1.00
```

这验证了 GPT 的主要点：它不会像 value-normalized residual 那样把长 maze option
洗掉。但是它也暴露了一个新问题：

```text
first-hit probability 是 cumulative incidence，会饱和。
跨过一个 turn 和穿过整条 maze，在 deterministic case 都是 1。
```

所以 `struct_prob` 单独不能区分 open_room 里“擦到一个诊断点”和 maze 里“穿过一串
诊断点”。

### 17.3 第二发现：distinct hidden exposure 才能区分 open_room 和 maze

输出：

```text
experiments/output/struct_first_hit_turn_distinct_diagnostic/
```

结果：

```text
open_room:
  struct_hidden_distinct_valid_total ~= 2.0 / 1.9

four_rooms:
  struct_hidden_distinct_valid_total ~= 2.0 / 1.9

maze:
  struct_hidden_distinct_valid_total ~= 24.0 / 24.0
```

这非常关键。`struct_prob` 解决了 duration dilution，但 `struct_distinct` 解决了
first-hit saturation。它也更贴合 GPT 说的：

```text
跨过一个 hidden point 和跨过很多 hidden points 需要分开。
```

### 17.4 struct_bits threshold=1 的失败模式

输出：

```text
experiments/output/struct_first_hit_bits_threshold1_det/
```

deterministic 子集：

```text
open_room:
  B=4

four_rooms:
  B=6

maze:
  B=14 at max_splits=12
```

这说明直接把 `struct_hidden_bits > 1` 当 split rule 仍然太硬。它会把 open_room
和 four_rooms 也拆到 turn-articulation。也就是说：

```text
struct_prob / struct_bits 是合法性警报；
但如果 B_res lens 本身太宽，它仍然会把 diagnostic lens 误当成 ontology。
```

### 17.5 struct_distinct threshold=4 的更好行为

输出：

```text
experiments/output/struct_distinct_threshold4/
```

结果：

```text
open_room:
  B=2

four_rooms:
  B=4

maze:
  B=14
```

这和我们想要的行为一致：不动 open_room，不把 four_rooms 过拆，但会拆 maze。
它和 raw residual 1.2 的结果相近，不过解释更清楚：

```text
raw residual 1.2:
  empirically useful, but threshold 仍像 magic number

struct_distinct:
  直接量化 global option 暴露了多少个不同 hidden diagnostic boundaries
```

不过还要注意：`struct_distinct threshold=4` 现在仍然是一个阈值。它比 raw residual
好解释，但还不是最终形式。下一步更好的做法是把它变成 MDL criterion：

```text
split if:
  hidden structural bits / distinct exposure saved by adding h
  >
  cost(add boundary node h + incident option edges)
```

### 17.6 当前结论

现在我们有了四个通道，分工比之前清楚：

```text
value_norm residual:
  value/planning diagnostic，不能单独做 structural split

struct_prob:
  是否碰到任何 hidden diagnostic boundary；不被 duration 稀释，但会饱和

struct_distinct:
  穿过多少个不同 hidden diagnostic boundaries；能区分 open_room 和 maze

raw model residual:
  当前仍是强 baseline，但需要被 structural_distinct/MDL 解释或替代
```

下一步应该做的不是继续调单个 threshold，而是：

```text
实现 split-benefit MDL:
  benefit(h) = reduction in struct_distinct_bits or hidden-exposure cost
  cost(h) = log2 |S| + added edge/model complexity

选择 benefit(h) > cost(h) 的 split。
```

这个问题值得再拿给 GPT 反驳：

```text
struct_distinct 已经能区分 open_room/four_rooms 和 maze。
如何把它变成不靠 threshold 的 MDL split criterion？
```

## 18. MDL structural split：从 threshold 到 cost-benefit

我实现了第一版 `struct_distinct` MDL split。新增策略：

```text
--residual-split-policy mdl
```

核心思想：

```text
candidate benefit(h)
  ~= sum_edges struct_hidden_distinct(edge) * Pr(edge hits h before B)

candidate cost(h)
  = node_cost_weight * log2(|S|)
    + edge_cost_weight * 2|B|

split if:
  benefit(h) - cost(h) > min_gain
```

这里的关键修正是：一开始我只把 `Pr(hit h)` 当 benefit，结果 maze 里每个 candidate
的收益都不够大，完全不 split。后来改成：

```text
Pr(hit h) * total hidden distinct exposure of that edge
```

这更接近“加 h 会截断这条 edge，从而省掉 downstream hidden exposure”的含义。

新增参数：

```text
--struct-mdl-node-cost-weight
--struct-mdl-edge-cost-weight
--struct-mdl-exposure-bit-weight
--struct-mdl-min-gain
```

并且当 `--residual-split-policy mdl` 时，代码会自动启用：

```text
--compute-struct-distinct
```

### 18.1 默认 edge cost 太低，会过拆

默认 `edge_cost_weight=0.1` 时，maze 会继续拆到大约：

```text
maze:
  B ~= 22
```

这说明仅有 `log2(|S|)` 和很低的 added-edge cost 还不足以形成合适的 MDL knee。
pair-specific option set 里新增一个 boundary 会引入 `2|B|` 条新的 pair edges，
这个复杂度必须认真计入。

### 18.2 edge_cost_weight=1.0：更 conservative

输出：

```text
experiments/output/struct_distinct_mdl_edge1/
```

结果：

```text
open_room:
  B=2

four_rooms:
  B=4

maze:
  slip=0.00 -> B=8
  slip=0.05 -> B=13
```

这版不会拆 open_room，也不会过拆 four_rooms；maze 会被拆，但 deterministic maze
可能偏 compact。

### 18.3 edge_cost_weight=0.5：当前更像 knee

输出：

```text
experiments/output/struct_distinct_mdl_edge05/
```

结果：

```text
open_room:
  B=2

four_rooms:
  B=4

maze:
  slip=0.00 -> B=11
  slip=0.05 -> B=14
```

和上一轮的 `struct_distinct threshold=4` 对比：

```text
threshold=4:
  maze -> B=14 / B=14

MDL edge_cost=0.5:
  maze -> B=11 / B=14
```

MDL 的优势是停机理由更清楚。最终行里：

```text
open_room:
  benefit ~= 1, cost ~= 7.1, gain < 0

four_rooms:
  benefit ~= 1, cost ~= 9.7, gain < 0

maze edge_cost=0.5:
  deterministic final benefit ~= 11, cost ~= 17.3, gain < 0
  slip=0.05 final benefit ~= 14, cost ~= 20.3, gain < 0
```

所以它不是“低于手调 threshold 就停”，而是：

```text
继续 split 能省下的 hidden-exposure coding cost
已经小于新增 node + pair-edge coding cost。
```

### 18.4 当前判断

`struct_distinct MDL` 比 `struct_distinct threshold` 更接近我们想要的形式：

```text
不拆 open_room
不把 four_rooms 过拆
maze 会拆到一个中等规模 graph
```

但它还有两个明显待改进点：

```text
1. benefit 现在是局部 proxy，没有真正 recompute split 后的 total MDL decrease。
2. edge_cost_weight 仍然是一个模型复杂度系数，需要从 option library encoding 或 validation curve 里确定。
```

下一步更严谨的版本应该做 greedy one-step lookahead：

```text
for candidate h:
  temporarily add h
  recompute row metrics
  delta_MDL = MDL(B) - MDL(B union {h})

choose h if max(delta_MDL) > 0
```

这会更慢，但可以把现在的 local proxy 变成真正的 description-length decrease。

## 19. 统一 graph baseline comparison

现在可以开始和 option-discovery / landmark-discovery 算法做第一层对比了。新增脚本：

```text
experiments/run_graph_baseline_comparison.py
```

它把所有方法都先当成 boundary proposer：

```text
algorithm -> proposed boundary B
B -> canonical first-boundary targeted edge model
B -> same residual / hidden-cross / policy-complexity diagnostics
```

这样先隔离一个问题：

```text
这个算法找到的 graph node 本身好不好？
```

而不是一开始就把不同论文里各自的 option policy、termination、training loss 全混在一起。

### 19.1 当前 core comparison

命令：

```text
python3 experiments/run_graph_baseline_comparison.py \
  --fixed-methods fixed_endpoints fixed_bottleneck15 fixed_spectral25 fixed_turn_articulation \
  --learned-methods learned_soft3 learned_raw_residual12 learned_struct_mdl_e05 \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --max-splits 20 \
  --out-dir experiments/output/graph_baseline_comparison_core
```

输出：

```text
experiments/output/graph_baseline_comparison_core/
```

核心结果：

```text
open_room:
  endpoints / raw residual / MDL -> B=2
  soft3 with slip=0.05 -> B=3
  fixed turn_articulation -> B=4 but residual nearly zero only because it exposes turns

four_rooms:
  learned methods -> B=4
  fixed bottleneck15 / turn_articulation -> B=10
  fixed spectral25 -> B=15

maze:
  endpoints -> B=2, cheap but hides many boundary structures
  learned_soft3 -> B=4 / 7, still hides many structures
  learned_raw_residual12 -> B=14 / 14, lower residual but higher complexity
  learned_struct_mdl_e05 -> B=11 / 14, lower description-length than raw residual
  fixed_turn_articulation -> B=30, residual diagnostic almost zero but graph is too large
```

在 maze 上最有信息量的行：

```text
slip=0.00:
  endpoints:              B=2,  DL=73.5,  hiddenDistinct=24.0
  raw_residual12:         B=14, DL=743.6, hiddenDistinct=132.0
  struct_mdl_e05:         B=11, DL=545.5, hiddenDistinct=55.0
  turn_articulation:      B=30, DL=2045.8, hiddenDistinct=0.0

slip=0.05:
  endpoints:              B=2,  DL=71.7,  hiddenDistinct=24.0
  raw_residual12:         B=14, DL=750.1, hiddenDistinct=138.3
  struct_mdl_e05:         B=14, DL=687.7, hiddenDistinct=25.0
  turn_articulation:      B=30, DL=2242.5, hiddenDistinct=0.0
```

当前解释：

```text
fixed_turn_articulation 是 diagnostic upper bound：
  它把所有 turn/articulation 都暴露出来，所以 residual 很低，但图过大。

endpoints 是 degenerate compact lower bound：
  图很小，但 hidden-cross / residual 说明它把结构藏进 option。

struct_mdl_e05 目前最像中间解：
  不拆 open_room，不过拆 four_rooms，在 maze 拿到中等规模 graph。
```

### 19.2 外部 option 算法怎么接进来

`run_graph_baseline_comparison.py` 现在支持外部 boundary 文件：

```text
--boundary-files method_name=path/to/boundary.json
```

JSON 可以是 state id list：

```json
[0, 13, 27]
```

也可以是 coordinate list：

```json
[[1, 1], [3, 7], [5, 19]]
```

如果一个外部 option-discovery 算法输出 option terminal states / landmarks，就先把它们导出成这个格式，然后在同一套 diagnostic 下比较。

这一步回答的是：

```text
外部算法发现的 landmarks 作为 abstract graph nodes 是否更好？
```

下一层才比较：

```text
外部算法实际学到的 options 是否比 canonical first-boundary options 更好？
```

那需要再写一个 adapter，把 external option policy/termination 转成同一套 SMDP kernels 后再评估。

## 20. Option-discovery style boundary baselines

为了先和经典 option-discovery 思路对齐，我把两类额外 baseline 加进
`run_graph_baseline_comparison.py`：

```text
fixed_eigen_extrema{k}:
  Laplacian / eigenoption proxy。
  取 normalized graph Laplacian 的低频 eigenvectors，把每个 eigenpurpose 的 extrema
  当作 option terminal / landmark proposal。

fixed_coverage{k}:
  SPTM / SoRB / topological-memory proxy。
  用 shortest-path metric 做 farthest-point landmarks，模拟 replay graph 上的 coverage
  landmark selection。
```

这不是在复现外部 repo 的训练过程，而是在 tabular oracle setting 下比较它们隐含的
landmark/boundary hypothesis：

```text
Laplacian extrema / coverage landmarks 是否能给出好的 abstract graph nodes？
```

### 20.1 命令

```text
python3 experiments/run_graph_baseline_comparison.py \
  --fixed-methods fixed_endpoints fixed_bottleneck15 fixed_spectral25 \
                  fixed_eigen_extrema4 fixed_eigen_extrema8 fixed_eigen_extrema12 \
                  fixed_coverage8 fixed_coverage12 \
  --learned-methods learned_raw_residual12 learned_struct_mdl_e05 \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --max-splits 20 \
  --out-dir experiments/output/option_discovery_boundary_comparison
```

输出：

```text
experiments/output/option_discovery_boundary_comparison/
```

这轮也加了 normalized diagnostic：

```text
struct_hidden_distinct_per_edge =
  struct_hidden_distinct_valid_total / n_edges_valid
```

原因是 total hidden distinct 会随着 graph 边数量增长，不适合直接跨不同 `|B|`
比较；per-edge 更像“平均每条 abstract edge 还隐藏多少 boundary 结构”。

### 20.2 结果摘要

open_room：

```text
learned_struct_mdl_e05 / raw_residual12 / endpoints:
  B=2, 不拆

eigen_extrema / coverage:
  会按给定 k 继续放 landmark；
  hidden/edge 会下降，但 DL 明显上升。
```

这说明 Laplacian/coverage 类方法如果只看几何覆盖，会在 open room 产生非必要节点。

four_rooms：

```text
learned_struct_mdl_e05:
  B=4,  DL~=68/66, hidden/edge~=0.167/0.162

bottleneck15:
  B=10, DL~=240/237, hidden/edge~=0.067/0.070

eigen_extrema4:
  B=4,  DL~=91/88, hidden/edge~=1.67/1.63
```

这里 eigen-extrema 的 4 个点没有对准门/边界结构；同样 `B=4` 时，
learned hard/MDL 明显更好。bottleneck 可以进一步降低 hidden/edge，但复杂度高很多。

maze：

```text
slip=0.00:
  endpoints:            B=2,  DL=73.5,  hidden/edge=12.0
  eigen_extrema4:       B=4,  DL=182.3, hidden/edge=6.42
  eigen_extrema8:       B=8,  DL=425.7, hidden/edge=2.55
  struct_mdl_e05:       B=11, DL=545.5, hidden/edge=0.50
  bottleneck15:         B=13, DL=674.6, hidden/edge=0.52
  raw_residual12:       B=14, DL=743.6, hidden/edge=0.73

slip=0.05:
  endpoints:            B=2,  DL=71.7,  hidden/edge=12.02
  eigen_extrema8:       B=8,  DL=419.6, hidden/edge=2.56
  struct_mdl_e05:       B=14, DL=687.7, hidden/edge=0.138
  bottleneck15:         B=13, DL=702.5, hidden/edge=0.523
  raw_residual12:       B=14, DL=750.1, hidden/edge=0.760
```

当前读法：

```text
eigenoptions-style extrema 是有用 baseline：
  它确实沿 Pareto 方向改善 maze，从 endpoints 的 hidden/edge ~=12 降到 ~=2.5。

但它不像最终答案：
  同样 complexity 附近，struct_mdl_e05 的 hidden/edge 明显更低。

coverage landmarks 更像空间覆盖：
  在 open_room 降 hidden/edge，但这不是我们想要的 structural abstraction；
  在 maze 也不如 eigen_extrema 或 MDL。
```

### 20.3 暂时结论

第一层 comparison 已经给出一个很有用的反驳点：

```text
Laplacian/eigenoption 不是错。
它能找到大尺度方向，能改善长 maze 的粗 graph。
但它没有直接优化“abstract edge 是否隐藏 SMDP boundary structure”，
所以会：
  1. 在 open room / coverage setting 过放 landmarks；
  2. 在 maze 中比 structural-MDL 更慢地降低 hidden-cross residual。
```

这正好支持我们的主线：

```text
Laplacian 可以作为 proposal / prior，
但最终 split objective 应该是 SMDP edge residual + structural hidden exposure + model complexity。
```

下一步可以做两个方向：

```text
1. hybrid proposal:
   candidate pool = articulation / residual_argmax / eigen_extrema / coverage landmarks
   objective = same structural-MDL gain

2. real option adapter:
   读取外部 option algorithm 的 learned termination / policy，
   转成 canonical SMDP kernels，再比较 option policy 本身。
```

我建议先做方向 1，因为它能直接回答：

```text
Laplacian 作为 proposal 能不能帮助 structural-MDL 找到更好 graph？
```

如果 hybrid 仍然赢不了当前 residual_argmax，那再去接真正外部 option policy 会更有信息量。

### 20.4 hard-eigen hybrid 的负结果

我又做了一个更激进的 hybrid：

```text
learned_struct_mdl_hard_eigen12:
  B0_hard = articulation_only union eigen_extrema12
  split = hard first-boundary hidden first, then structural-MDL
```

命令：

```text
python3 experiments/run_graph_baseline_comparison.py \
  --fixed-methods fixed_endpoints fixed_eigen_extrema12 \
  --learned-methods learned_struct_mdl_e05 learned_struct_mdl_hard_eigen12 \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --max-splits 20 \
  --out-dir experiments/output/hybrid_eigen_proposal_comparison
```

结果：

```text
open_room:
  struct_mdl_e05:             B=2
  hard_eigen12:               B=12

four_rooms:
  struct_mdl_e05:             B=4
  hard_eigen12:               B=8 / 13

maze:
  struct_mdl_e05:             B=11 / 14
  hard_eigen12:               B=22 / 22
```

具体指标：

```text
maze slip=0.00:
  struct_mdl_e05:             DL=545.5,  hidden/edge=0.500
  hard_eigen12:               DL=1558.7, hidden/edge=0.494

maze slip=0.05:
  struct_mdl_e05:             DL=687.7,  hidden/edge=0.138
  hard_eigen12:               DL=1522.7, hidden/edge=0.483
```

这说明把 eigen extrema 升级成 hard B0 是错的：

```text
它在 open_room 必然过拆；
在 maze 中复杂度暴涨，hidden/edge 没有相应收益；
slip=0.05 甚至比当前 structural-MDL 更差。
```

因此更合理的下一步不是 `hard eigen B0`，而是：

```text
proposal-only eigen:
  eigen extrema 可以作为 candidate split proposals，
  但不应该作为 hidden-boundary diagnostic，也不应该强制 first-boundary termination。

objective 仍然只看：
  turn/articulation structural hidden exposure
  + residual/value diagnostic
  + graph/option complexity
```

这一步需要把当前代码里的 `candidate_boundary` 拆成两份：

```text
B_hard:
  真正会让 option first-boundary stop 的 hard diagnostic set

B_proposal:
  只用于 choose split candidate，不改变 option termination / residual lens
```

这个设计比直接接外部 option policy 更重要，因为它能清楚地区分：

```text
Laplacian as ontology  -> 不行，过拆
Laplacian as proposal  -> 还没测试，值得测试
```

### 20.5 proposal-only eigen / coverage

我把 `candidate_boundary` 拆出了一个 `proposal_boundary`：

```text
B_hard:
  仍然只用于 first-boundary option termination / hard hidden split。

B_proposal:
  只给 structural-MDL choose split candidate 用。
  不改变 option termination，也不改变 residual diagnostic lens。
```

新增 recipe：

```text
learned_struct_mdl_proposal_eigen12
learned_struct_mdl_proposal_coverage12
```

命令：

```text
python3 experiments/run_graph_baseline_comparison.py \
  --fixed-methods fixed_endpoints fixed_eigen_extrema12 fixed_coverage12 \
  --learned-methods learned_struct_mdl_e05 \
                    learned_struct_mdl_proposal_eigen12 \
                    learned_struct_mdl_proposal_coverage12 \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --max-splits 20 \
  --out-dir experiments/output/proposal_only_option_comparison
```

结果：

```text
open_room:
  struct_mdl_e05:             B=2
  proposal_eigen12:           B=2
  proposal_coverage12:        B=2

four_rooms:
  struct_mdl_e05:             B=4
  proposal_eigen12:           B=4
  proposal_coverage12:        B=4

maze slip=0.00:
  struct_mdl_e05:             B=11, DL=545.5, hidden/edge=0.500
  proposal_eigen12:           B=13, DL=674.9, hidden/edge=0.404
  proposal_coverage12:        B=14, DL=740.7, hidden/edge=0.368

maze slip=0.05:
  struct_mdl_e05:             B=14, DL=687.7, hidden/edge=0.138
  proposal_eigen12:           B=16, DL=824.7, hidden/edge=0.113
  proposal_coverage12:        B=17, DL=893.5, hidden/edge=0.103
```

这比 hard-eigen 结果健康很多：

```text
proposal-only 不再拆 open_room；
不再过拆 four_rooms；
只在 maze 里多加节点。
```

但它是否更好取决于 tradeoff：

```text
proposal_eigen/coverage 可以进一步降低 hidden/edge，
但代价是更高 graph + option library complexity。
```

当前判断：

```text
如果目标是极低 hidden/edge：
  proposal-only eigen/coverage 有帮助。

如果目标是最小 DL 下足够低 residual：
  原始 struct_mdl_e05 仍是更强默认点。
```

这给了下一轮很明确的问题：

```text
MDL cost 现在可能低估了 residual/hidden improvement 的收益，
或高估了 added pair edges 的成本。

需要做一条 lambda sweep：
  lambda_hidden / edge_cost_weight / node_cost_weight
看 proposal_eigen12 是否在某个合理权重下进入 Pareto frontier。
```

## 21. GPT_answer_5 后续：exact ΔMDL 与 occupancy exposure

`GPT_answer_5.md` 的核心反驳是：

```text
proposal-only eigen/coverage 降低 hidden/edge 不等于应该被 MDL 接受。
MDL 应该比较完整 code length：
  graph/boundary/edge/option cost + total 或 occupancy-weighted structural exposure。

per-edge hidden 只能是 diagnostic。
```

本轮补了新增 reference：

```text
reference/papers/mdl_principle_coding_modeling_1998__minimum-description-length-principle-in-coding-and-modeling.pdf
reference/gpt_answer_5_download_report.md
```

`GPT_answer_5.md` 里的其他 GitHub 链接都指回本仓库，没有新 repo。

### 21.1 实现

新增 exact MDL split mode：

```text
--residual-split-policy exact_mdl
```

它不再用：

```text
benefit(h) ~= edge_exposure * score - fixed split cost
```

而是对 top-k candidate 直接重算：

```text
L0 = mdl_bits(B)
Lh = mdl_bits(B union {h}) + log2(|proposal candidates|)
gain = L0 - Lh

accept if max_h gain(h) > 0
```

当前 `mdl_bits` 包括：

```text
boundary_bits:
  log2 C(|S|-|B_fixed|, |B|-|B_fixed|)

edge_bits:
  optional log2 C(|B|(|B|-1), n_edges_valid)

option/policy/model terms:
  option_pair_bit_cost * n_pair_options
  policy_tv_bit_cost * target_policy_tv_total
  policy_region_bit_cost * target_policy_regions_total
  model_residual_bit_cost * model_residual_valid_total

structural term:
  total distinct / total bits / occupancy distinct / occupancy bits
```

同时新增了 occupancy-weighted structural diagnostics：

```text
occupancy_struct_hidden_distinct
occupancy_struct_hidden_distinct_bits
occupancy_model_residual
occupancy_soft_cost
```

这个是按当前 abstract policy 实际使用的 edge 加权，而不是把 unused option
library 全算进 data cost。

### 21.2 strict exact MDL：会拒绝 maze split

命令：

```text
python3 experiments/run_first_boundary_targeted.py \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --candidate-kind articulation_only \
  --residual-kind turn_articulation \
  --residual-split-policy exact_mdl \
  --proposal-kind candidate \
  --exact-mdl-option-pair-bit-cost 0.25 \
  --exact-mdl-policy-tv-bit-cost 0.2 \
  --exact-mdl-policy-region-bit-cost 0.5 \
  --exact-mdl-model-residual-bit-cost 1.0 \
  --exact-mdl-struct-kind occupancy_distinct \
  --exact-mdl-top-k 8 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 20 \
  --out-dir experiments/output/exact_mdl_strict_pair025
```

结果：

```text
open_room:
  B=2

four_rooms:
  B=4

maze:
  B=2
```

maze step 0：

```text
strict pair025:
  occupancy_struct ~= 11.0 / 11.07
  exact gain ~= -31.1 / -40.2
```

也就是说，只要把 option-library / policy / model cost 也算进 code length，
当前 exact MDL 会认为 maze split 不划算。

这不是实现 bug，而是一个重要结论：

```text
如果没有 hard hidden constraint 或 task-distribution calibration，
strict MDL 会偏向 endpoints + strong option。
```

### 21.3 occupancy-struct-only exact MDL：只接受很少 split

为了隔离 structural term，我又跑了一个只看 occupancy structural exposure 的版本：

```text
python3 experiments/run_first_boundary_targeted.py \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --candidate-kind articulation_only \
  --residual-kind turn_articulation \
  --residual-split-policy exact_mdl \
  --proposal-kind candidate \
  --exact-mdl-option-pair-bit-cost 0.0 \
  --exact-mdl-policy-tv-bit-cost 0.0 \
  --exact-mdl-policy-region-bit-cost 0.0 \
  --exact-mdl-model-residual-bit-cost 0.0 \
  --exact-mdl-struct-kind occupancy_distinct \
  --exact-mdl-top-k 8 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 12 \
  --out-dir experiments/output/exact_mdl_occupancy_struct_only
```

结果：

```text
open_room:
  B=2

four_rooms:
  B=4

maze:
  slip=0.00 -> B=3
  slip=0.05 -> B=2
```

deterministic maze step 0：

```text
base_bits ~= 12.0
candidate_bits ~= 10.3
gain ~= 1.70
accepted split: (1, 5)
```

但下一步 gain 变负：

```text
B=3:
  occupancy_struct ~= 0
  gain ~= -8.87
```

所以 exact occupancy MDL 的行为比 proxy MDL 保守得多。

### 21.4 当前解释

这轮把问题暴露得更准确了：

```text
proxy MDL:
  能产生实用 graph，但 benefit 是局部 proxy。

strict exact MDL:
  理论上更干净，但如果 option cost 进入主 objective，
  会重新偏向 endpoints + strong option。

occupancy-struct-only exact MDL:
  说明 exact recomputation 可以工作，
  但单任务 occupancy 会让 split 很快停止。
```

因此下一步不应该再调 `edge_cost_weight`，而应该明确约束形式：

```text
主优化：
  minimize graph/option code length

hard constraints:
  occupancy_struct_hidden <= epsilon_hidden
  residual/value-impact <= epsilon_residual
  planning gap <= epsilon_plan

或：
  用 break-even lambda 报告每个 candidate split：
    lambda* = added_code / structural_exposure_reduction
```

这正好回答 GPT 的反驳：

```text
只靠 unconstrained MDL 会拒绝 maze split；
所以我们的目标不是普通 MDL，而是 constrained MDL / rate-distortion：
  在 hidden-cross/residual 约束下找最短 graph-option code。
```

## 22. GPT_answer_6 后的 constrained rate-distortion 构造器

GPT_answer_6 把目标重新定成：

```text
hard admissibility constraints
+ rate-distortion distortion terms
```

这次我把它落到 `run_first_boundary_targeted.py` 里：

```text
rate R:
  boundary code
  optional edge code
  option-pair code
  target-policy TV / region code

distortion D_struct:
  occupancy_struct_hidden_distinct
  或 distinct / bits 版本

constructor:
  如果 D_struct, D_model, D_value, start_gap 超预算：
    选 violation reduction 最大的 split
  如果没超预算：
    选 R + lambda_s D_struct + ... 下降的 split

diagnostic:
  lambda_s* = added_rate_bits / structural_distortion_reduction
```

新增参数：

```text
--residual-split-policy rd
--rd-struct-kind occupancy_distinct
--rd-struct-budget <epsilon_s>
--rd-lambda-struct <lambda_s>
--rd-model-budget / --rd-value-budget / --rd-start-gap-budget
```

同时在 baseline comparison 里新增：

```text
learned_rd_struct_budget1
learned_rd_struct_budget2
learned_rd_struct_budget6
```

这些 recipe 用：

```text
B_hard proposal source:
  candidate_kind = articulation_only

B_probe / distortion lens:
  residual_kind = turn_articulation
  proposal_kind = residual
```

也就是 hard/probe 被真正拆开了。

### 22.1 Budget constructor 结果

命令：

```bash
python3 experiments/run_first_boundary_targeted.py \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --candidate-kind articulation_only \
  --proposal-kind residual \
  --residual-kind turn_articulation \
  --residual-split-policy rd \
  --rd-struct-budget 2.0 \
  --rd-top-k 8 \
  --exact-mdl-option-pair-bit-cost 0.25 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 16 \
  --out-dir experiments/output/rate_distortion_struct_budget2_probe
```

核心结果：

```text
open_room:
  B=2, D_occ ~= 1.00 / 0.94
  under budget, no split

four_rooms:
  B=4
  hard articulation split handles admissibility

maze deterministic:
  B=3
  D_occ: 11 -> 0
  accepted split: residual_rate_distortion

maze slip=0.05:
  B=3
  D_occ: 11.07 -> 10.84
  still violates budget, but one-step split has no further D_occ gain
```

这比 strict MDL 更符合我们要的语义：

```text
open room 不因为 probe saliency 被过拆；
four_rooms 的 hard bottleneck 仍然必须拆；
deterministic maze 的 topology split 能被接受。
```

但 stochastic maze 暴露了新问题：

```text
occupancy aggregation + one-step split 会出现 distortion plateau。
```

也就是说，单个 split 在 stochastic slip 下只是把 hidden-cross 从第一段 option 转移到后续 option，
总 occupancy hidden distortion 没明显下降。

### 22.2 Lagrangian / break-even lambda

命令：

```bash
python3 experiments/run_first_boundary_targeted.py \
  --maps open_room four_rooms maze \
  --slips 0.0 0.05 \
  --candidate-kind articulation_only \
  --proposal-kind residual \
  --residual-kind turn_articulation \
  --residual-split-policy rd \
  --rd-lambda-struct 5.0 \
  --rd-top-k 8 \
  --exact-mdl-option-pair-bit-cost 0.25 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 16 \
  --out-dir experiments/output/rate_distortion_struct_lambda5
```

结果：

```text
open_room deterministic:
  lambda_s* ~= 10.84
  lambda_s=5 rejects split

open_room slip=0.05:
  lambda_s* ~= 12.36
  lambda_s=5 rejects split

maze deterministic:
  lambda_s* ~= 3.59
  lambda_s=5 accepts split

maze slip=0.05:
  lambda_s* ~= 172.5
  lambda_s=5 rejects split
```

这给了一个很干净的解释：

```text
lambda_s 是“愿意为降低 1 单位 occupancy structural distortion 支付多少 rate bits”。

deterministic maze 的 topology split 很便宜；
open room 的 split 不值；
stochastic maze 当前这个单步 split 在 occupancy 指标下极贵。
```

### 22.3 和固定图的比较

输出：

```text
experiments/output/rate_distortion_graph_comparison/summary.md
```

几个代表点：

```text
open_room:
  endpoints / learned_rd: B=2, DL ~= 18
  turn_articulation: B=4, DL ~= 44-46
  eigen/coverage12: B=12, DL ~= 264-279

four_rooms:
  endpoints: B=2, D_occ ~= 3
  learned_rd: B=4, D_occ ~= 0, DL ~= 66-68
  turn_articulation: B=10, DL ~= 229

maze deterministic:
  endpoints: B=2, D_occ ~= 11, DL ~= 73
  learned_rd: B=3, D_occ ~= 0, DL ~= 118
  turn_articulation: B=30, DL ~= 2046
```

所以 current best story 是：

```text
learned_rd sits between endpoints and dense option-discovery graphs:
  more topology-exposing than endpoints,
  much smaller than fixed turn/eigen/coverage graphs.
```

### 22.4 下一步

现在不急着再问 GPT。先把 stochastic maze 的 plateau 查清楚：

```text
假设 A:
  occupancy_distortion 太依赖当前 shortest-path abstract policy，
  split 后 hidden mass 被转移到下一段 option。

假设 B:
  one-step greedy 不够，需要 multi-split lookahead 或 batch split。

假设 C:
  stochastic setting 应该用 audit / CVaR / max distortion 作辅助 budget，
  不能只用 single-task occupancy distortion。
```

下一步实验应该加：

```text
1. RD candidate diagnostics:
   对每个 candidate 输出 rate_delta, D_delta, lambda*

2. batch-k RD split:
   一次加入 top-k candidate，检查 stochastic maze 的 D_occ 是否真正下降

3. audit budget:
   用 struct_hidden_distinct_max 或 CVaR 防止 occupancy plateau 掩盖 hidden boundary
```

## 23. Stochastic maze plateau 诊断

这一步把三个东西接进代码：

```text
1. rd_candidates.csv / rd_candidates.json
   每个 RD candidate 都输出：
     base_struct, candidate_struct, struct_delta
     base_violation, candidate_violation, violation_gain
     rate_delta, lambda*

2. --rd-batch-k
   在 single candidate 后，额外评估 top-k prefix batch split。

3. audit / CVaR distortion
   新增 rd_struct_kind:
     audit_prob_max / audit_prob_cvar95
     audit_distinct_max / audit_distinct_cvar95
     audit_distinct_bits_max / audit_distinct_bits_cvar95
```

### 23.1 Occupancy RD + batch-k

命令：

```bash
python3 experiments/run_first_boundary_targeted.py \
  --maps maze \
  --slips 0.05 \
  --candidate-kind articulation_only \
  --proposal-kind residual \
  --residual-kind turn_articulation \
  --residual-split-policy rd \
  --rd-struct-budget 2.0 \
  --rd-batch-k 4 \
  --rd-top-k 8 \
  --exact-mdl-option-pair-bit-cost 0.25 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 16 \
  --out-dir experiments/output/rate_distortion_batch4_budget2_maze_slip005
```

结果：

```text
step 0:
  B=2
  D_occ = 11.0687
  best single split: (1,5)
  D_occ -> 10.8446
  lambda* ~= 172.5

step 1:
  B=3
  top single candidates:
    D_occ delta = 0
  top batch candidates:
    D_occ delta = 0
  stop
```

所以 stochastic maze plateau 不是简单的 one-step greedy 问题。

```text
batch-k on the current occupancy distortion still cannot reduce D_occ.
```

这说明当前 abstract optimal policy 的 occupancy 把剩余 hidden structure 放到了“不被当前策略实际使用”的边里。

### 23.2 Audit/CVaR RD

命令：

```bash
python3 experiments/run_first_boundary_targeted.py \
  --maps maze \
  --slips 0.05 \
  --candidate-kind articulation_only \
  --proposal-kind residual \
  --residual-kind turn_articulation \
  --residual-split-policy rd \
  --rd-struct-kind audit_distinct_cvar95 \
  --rd-struct-budget 2.0 \
  --rd-batch-k 4 \
  --rd-top-k 8 \
  --exact-mdl-option-pair-bit-cost 0.25 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 16 \
  --out-dir experiments/output/rate_distortion_audit_cvar2_batch4_maze_slip005
```

结果：

```text
step 0:
  B=2
  audit CVaR = 12.97
  batch split 4 states -> audit CVaR = 7.93

step 1:
  B=6
  batch split 4 states -> audit CVaR = 4.60

step 2:
  B=10
  batch split 3 states -> audit CVaR = 2.23

step 3:
  B=13
  single split -> audit CVaR = 1.98

final:
  B=14
  audit CVaR ~= 1.98
  D_occ still ~= 10.84
```

这个结果非常关键：

```text
occupancy distortion:
  认为 B=3 之后没有继续收益

audit/CVaR distortion:
  继续发现隐藏边界，直到 B=14
```

所以 plateau 的原因更像是 aggregation choice，而不是 residual candidate 不够或 greedy 搜索太弱。

### 23.3 Plateau comparison

输出：

```text
experiments/output/rate_distortion_plateau_comparison_maze_slip005/summary.md
```

核心表：

```text
fixed_endpoints:
  B=2
  D_occ=11.07
  D_cvar=12.97
  DL=71.66

learned_rd_struct_budget2:
  B=3
  D_occ=10.84
  D_cvar=12.00
  DL=113.11

learned_rd_batch4_budget2:
  B=3
  D_occ=10.84
  D_cvar=12.00
  DL=113.11

learned_rd_audit_cvar2:
  B=14
  D_occ=10.84
  D_cvar=1.98
  DL=686.84

fixed_turn_articulation:
  B=30
  D_occ=0
  D_cvar=0
  DL=2242.51
```

解释：

```text
RD-occupancy:
  找到当前 task policy 实际用到的 topology split，但对 stochastic hidden library risk 不敏感。

RD-audit:
  能压低 hidden library risk，但会显著增加 graph/option rate。

fixed turn_articulation:
  是上界式 dense solution，几乎完全暴露结构，但代价太大。
```

### 23.4 当前结论

现在我们应该把 structural distortion 明确分成两层：

```text
D_occ:
  当前任务实际使用的 abstract policy 隐藏了多少结构。

D_audit:
  option library 里最坏尾部边隐藏了多少结构。
```

主优化不应该只用其中一个：

```text
minimize R
subject to:
  D_occ <= epsilon_occ
  CVaR_0.95(D_edge) <= epsilon_audit
```

这比单纯问 “hidden-cross 是 hard 还是 soft” 更准确：

```text
hard:
  B_hard hidden-cross

soft occupancy:
  当前任务策略实际用到的 hidden-cross

soft audit:
  library tail-risk hidden-cross
```

下一步应该做 Pareto frontier：

```text
x-axis:
  rate / DL

y-axis:
  D_occ and D_audit

points:
  endpoints
  learned_occ_RD
  learned_audit_RD
  learned_joint_RD
  fixed_turn_articulation
```

如果要问 GPT，最值得问的是：

```text
在 stochastic maze 中，D_occ 不降但 D_audit 能降，
主论文 claim 应该把 D_audit 放成第二个 budget，
还是把 task distribution 从 single start-goal 扩成 uniform task-pair occupancy？
```

但我建议先实现 joint budget / Pareto table，再问 GPT，信息会更实。

## 24. Joint budget 与 Pareto frontier

这一步把 RD 构造器从单一 structural distortion 扩成 joint budget。

新增参数：

```text
--rd-struct-kind / --rd-struct-budget
--rd-audit-kind / --rd-audit-budget
--rd-lambda-struct / --rd-lambda-audit
```

典型用法：

```text
primary struct:
  occupancy_distinct

audit struct:
  audit_distinct_cvar95
```

也就是：

```text
minimize R
subject to:
  D_occ <= epsilon_occ
  D_audit <= epsilon_audit
```

同时新增：

```text
experiments/run_rd_pareto_frontier.py
```

它从 graph baseline comparison 里抽 non-dominated frontier，默认目标是：

```text
description_length_proxy
occupancy_struct_hidden_distinct
struct_hidden_distinct_cvar95
```

### 24.1 Joint budget on stochastic maze

命令：

```bash
python3 experiments/run_first_boundary_targeted.py \
  --maps maze \
  --slips 0.05 \
  --candidate-kind articulation_only \
  --proposal-kind residual \
  --residual-kind turn_articulation \
  --residual-split-policy rd \
  --rd-struct-kind occupancy_distinct \
  --rd-struct-budget 2.0 \
  --rd-audit-kind audit_distinct_cvar95 \
  --rd-audit-budget 2.0 \
  --rd-batch-k 4 \
  --rd-top-k 8 \
  --exact-mdl-option-pair-bit-cost 0.25 \
  --soft-kind combined \
  --soft-split-policy never \
  --max-splits 16 \
  --out-dir experiments/output/rate_distortion_joint_occ2_audit2_maze_slip005
```

结果：

```text
final:
  B=18
  D_occ ~= 0.017
  D_audit ~= 1.02
  DL ~= 1182
```

trace 解释：

```text
step 0:
  B=2
  D_occ=11.07
  D_audit=12.97
  batch split 4 states

step 1:
  B=6
  D_occ=10.86
  D_audit=7.93
  batch split 4 states

step 2:
  B=10
  D_occ=10.86
  D_audit=4.60
  batch split 4 states
  important:
    this batch finally collapses D_occ to ~0.017

step 3:
  B=14
  D_occ=0.017
  D_audit=4.53
  batch split 4 states

step 4:
  B=18
  D_occ=0.017
  D_audit=1.02
  both budgets satisfied
```

这修正了上一轮的结论：

```text
single D_occ:
  greedy/batch 看起来 plateau

single D_audit:
  能降低 audit，但不主动解决 D_occ

joint D_occ + D_audit:
  audit-driven splits 能打开后续结构，
  然后 D_occ 也会大幅下降。
```

所以 stochastic maze 不是“D_occ 永远不可降”，而是：

```text
D_occ 的短视 greedy signal 不足；
D_audit 提供了必要的 exploration / library-risk pressure。
```

### 24.2 Pareto comparison

命令：

```bash
python3 experiments/run_graph_baseline_comparison.py \
  --maps maze \
  --slips 0.05 \
  --fixed-methods fixed_endpoints fixed_turn_articulation \
  --learned-methods \
    learned_rd_struct_budget2 \
    learned_rd_audit_cvar2 \
    learned_rd_joint_occ2_audit2 \
  --out-dir experiments/output/rate_distortion_joint_comparison_maze_slip005

python3 experiments/run_rd_pareto_frontier.py \
  --input experiments/output/rate_distortion_joint_comparison_maze_slip005/comparison.csv \
  --out-dir experiments/output/rate_distortion_joint_pareto_maze_slip005
```

结果：

```text
fixed_endpoints:
  B=2
  D_occ=11.07
  D_audit=12.97
  DL=71.66

learned_rd_struct_budget2:
  B=3
  D_occ=10.84
  D_audit=12.00
  DL=113.11

learned_rd_audit_cvar2:
  B=14
  D_occ=10.84
  D_audit=1.98
  DL=686.84

learned_rd_joint_occ2_audit2:
  B=18
  D_occ=0.017
  D_audit=1.02
  DL=1181.91

fixed_turn_articulation:
  B=30
  D_occ=0
  D_audit=0
  DL=2242.51
```

Pareto frontier 上全部保留，因为它们代表不同 trade-off：

```text
endpoints:
  cheapest, high distortion

occupancy-only RD:
  tiny graph improvement, still high library risk

audit-only RD:
  reduces library risk, not task occupancy

joint RD:
  satisfies both budgets at about half dense-turn DL

dense turn:
  zero distortion upper bound, very expensive
```

当前最强 claim 变成：

```text
我们不是用 Laplacian 找一个保持 MDP 不变的最小 graph；
我们是在 graph-option abstraction 空间里做 constrained rate-distortion。

D_occ 负责当前任务策略实际隐藏的结构；
D_audit 负责 option library 的尾部 hidden-cross risk。

二者联合约束时，stochastic maze 能得到比 dense turn 小很多、
但同时满足任务和结构风险预算的 graph。
```

### 24.3 下一步

下一步可以开始做正式 Pareto sweep：

```text
epsilon_occ in {0, 1, 2, 6, 12}
epsilon_audit in {0, 1, 2, 4, 8, 13}
```

并输出：

```text
frontier over:
  R
  D_occ
  D_audit
  value_gap
```

这时就值得 push，然后问 GPT：

```text
joint D_occ + D_audit 的解释是否足够稳？
D_audit 应该是 CVaR library risk，还是 uniform task-pair occupancy 的替代品？
```

## 25. Option Algorithm Baseline Adapter

这一步开始把“和 option 算法比较”落到同一个实验表里。

新增脚本：

```text
experiments/run_option_algorithm_comparison.py
```

它先做最便宜的 tabular baseline：

```text
Laplacian eigenoptions:
  用低频 Laplacian/PVF extrema 选 option termination/subgoal

betweenness bottleneck options:
  用 graph betweenness 选 bottleneck termination/subgoal

random landmarks:
  随机 landmark termination/subgoal

coverage landmarks:
  shortest-path farthest-point topological landmarks

ours:
  graph_rd_joint，也就是 joint D_occ / D_audit 约束下学出的 graph
```

为了公平地放到同一个 SMDP 评估框架里，所有 baseline 都先用同一种 adapter：

```text
termination/subgoal set B
  -> shortest-path-to-subgoal primitive option policy
  -> first-boundary termination on B
  -> exact first-hit SMDP kernel
  -> SMDP value iteration
  -> original-env rollout evaluation
```

所以现在比较的是：

```text
baseline option algorithm 在原始环境中构造 option policy/termination；
再转成 rollout/evaluation 可执行的 SMDP graph options；
最后和我们的 extracted graph + first-boundary options 同表比较。
```

### 25.1 重要修正

顺手修了一个会影响 D_occ 的实现问题：

```text
policy_boundary_occupancy 之前把 smdp_value_iteration 返回的 dict
当 sequence enumerate，导致 occupancy 主要只压在 start edge 上。

现在它按 boundary position 正确读取 policy_smdp[pos]。
```

因此从这一节开始，`occupancy_struct_hidden_distinct` 更接近真正的 closed-loop graph-policy occupancy。
旧的 joint RD 数值需要按新代码重跑后再作为正式结果引用。

另一个工程修正：

```text
GridWorld.index_maps 加 lru_cache
```

这把 option baseline 和 RD candidate evaluation 的运行时间明显降下来。

### 25.2 Maze slip=0.05 初始结果

命令：

```bash
python3 experiments/run_option_algorithm_comparison.py \
  --maps maze \
  --slips 0.05 \
  --methods endpoints eigenoptions_12 betweenness_12 random_landmarks_12 coverage_12 graph_rd_joint turn_articulation \
  --max-splits 18 \
  --n-rollouts 100 \
  --out-dir experiments/output/option_algorithm_comparison_maze_slip005
```

关键结果：

```text
endpoints:
  B=2, D_occ=11.07, D_audit_CVaR=12.97, rollout hidden=11.11, DL=71.66

eigenoptions_12:
  B=12, D_occ=10.07, D_audit_CVaR=6.00, rollout hidden=10.05, DL=693.06

betweenness_12:
  B=12, D_occ=7.14, D_audit_CVaR=6.13, rollout hidden=7.22, DL=611.41

random_landmarks_12:
  B=12, D_occ=10.05, D_audit_CVaR=6.93, rollout hidden=10.09, DL=676.87

coverage_12:
  B=12, D_occ=11.04, D_audit_CVaR=4.02, rollout hidden=11.07, DL=731.68

graph_rd_joint:
  B=24, D_occ=2.00, D_audit_CVaR=1.31, rollout hidden=2.04, DL=1585.23

turn_articulation:
  B=30, D_occ=0, D_audit_CVaR=0, rollout hidden=0, DL=2242.51
```

所有方法在这个 shortest-path control task 上 rollout success rate 都是 1，
primitive step mean 也都约 38.3 到 38.9，所以 value/success 指标暂时分不开。
真正拉开差异的是 hidden boundary structure：

```text
Laplacian eigenoptions / random landmarks / coverage landmarks
  大多能降低 tail risk，但 closed-loop D_occ 仍接近 endpoints。

betweenness bottleneck
  比 Laplacian/coverage 更像 bottleneck baseline，D_occ 降到 7.14。

graph_rd_joint
  在 B=24 时把 D_occ 和 rollout hidden crossing 压到约 2，
  更接近 dense turn_articulation，但 description length 仍明显低于 dense graph。
```

### 25.3 当前还缺的比较

现在还不是完整 Option-Critic 对比，只是 tabular option-discovery baseline adapter。

还缺：

```text
1. sample-efficiency curve:
   现在 training_samples = 0，因为这些 baseline 都是 oracle/tabular 构造。
   真正训练型 baseline 需要 Option-Critic 或 subgoal-option learning loop。

2. kernel estimation noise:
   现在 SMDP kernel 用 exact first-hit reduction。
   下一步可以加 rollout-estimated kernel，并比较 kernel_rollouts 增加时 planning gap 如何下降。

3. budget sweep:
   graph_rd_joint 现在只跑了一个预算点。
   需要和 eigenoptions_k / betweenness_k / random_k / coverage_k 在 k={4,8,12,16,24} 上画 frontier。
```

## 26. Option Baseline Frontier + Kernel Estimation Noise

这一轮把上一节的两个缺口补上：

```text
1. k={4,8,12,16,24} 的 option baseline frontier
2. rollout-estimated SMDP kernel noise curve
```

新增脚本：

```text
experiments/run_option_baseline_frontier.py
experiments/run_smdp_kernel_noise_curve.py
```

### 26.1 k-sweep frontier

命令：

```bash
python3 experiments/run_option_baseline_frontier.py \
  --maps maze \
  --slips 0.05 \
  --k-values 4 8 12 16 24 \
  --n-rollouts 100 \
  --max-splits 18 \
  --out-dir experiments/output/option_baseline_frontier_maze_slip005
```

输出：

```text
experiments/output/option_baseline_frontier_maze_slip005/frontier_all.csv
experiments/output/option_baseline_frontier_maze_slip005/frontier_pareto.csv
experiments/output/option_baseline_frontier_maze_slip005/summary.md
```

主要 frontier：

```text
endpoints:
  B=2,  DL=71.66,   D_occ=11.07, CVaR=12.97, rollout hidden=11.11

betweenness_8:
  B=8,  DL=377.22,  D_occ=9.10,  CVaR=8.30, rollout hidden=9.12

betweenness_12:
  B=12, DL=611.41,  D_occ=7.14,  CVaR=6.13, rollout hidden=7.22

betweenness_24:
  B=24, DL=1480.96, D_occ=5.17,  CVaR=3.85, rollout hidden=5.10

graph_rd_joint:
  B=24, DL=1585.23, D_occ=2.00,  CVaR=1.31, rollout hidden=2.04

turn_articulation:
  B=30, DL=2242.51, D_occ=0,     CVaR=0,    rollout hidden=0
```

对 baseline 的判断：

```text
betweenness 是目前最强的传统 option-subgoal baseline。
Laplacian eigenoptions 主要降低 tail CVaR，不太降低 closed-loop D_occ。
coverage 也更像 tail-risk baseline，对当前任务 occupancy hiding 帮助有限。
random landmarks 偶尔会撞到有用位置，但不稳定且不可解释。
```

最重要的比较：

```text
betweenness_24:
  DL=1480.96, D_occ=5.17, CVaR=3.85

graph_rd_joint:
  DL=1585.23, D_occ=2.00, CVaR=1.31
```

也就是说，在相同 B=24 下，joint RD graph 只比 betweenness 多一点 rate，
但把 closed-loop hidden structure 和 tail audit risk 都压低很多。
这比只和 dense turn graph 比更有说服力。

### 26.2 rollout-estimated SMDP kernel noise

命令：

```bash
python3 experiments/run_smdp_kernel_noise_curve.py \
  --maps maze \
  --slips 0.05 \
  --methods betweenness_12 graph_rd_joint \
  --sample-sizes 1 2 5 10 20 50 \
  --replicates 3 \
  --n-eval-rollouts 100 \
  --max-splits 18 \
  --out-dir experiments/output/smdp_kernel_noise_maze_slip005
```

输出：

```text
experiments/output/smdp_kernel_noise_maze_slip005/kernel_noise_raw.csv
experiments/output/smdp_kernel_noise_maze_slip005/kernel_noise_aggregate.csv
experiments/output/smdp_kernel_noise_maze_slip005/summary.md
```

这个实验流程是：

```text
固定 graph B 和 primitive option policies
  -> 每条 option edge 用 N 次 original-env rollout 估计 SMDP kernel
  -> 在 estimated kernel 上做 SMDP planning
  -> 把得到的 abstract policy 放回 exact SMDP 和 original env rollout 评估
```

关键结果：

```text
betweenness_12:
  N=1:  policy loss=2.71, model start error=0.59, kernel gamma L1=0.0466
  N=50: policy loss=0.011, model start error=0.26, kernel gamma L1=0.0158
  rollout hidden 大约一直在 7.0

graph_rd_joint:
  N=1:  policy loss=0.031, model start error=0.81, kernel gamma L1=0.0107
  N=50: policy loss=0.038, model start error=0.44, kernel gamma L1=0.0031
  rollout hidden 从约 2.0 降到接近 0
```

解释：

```text
kernel error 随 N 增加稳定下降；
estimated model 的 value 本身仍有偏差，但 policy loss 很小。

所以这个任务上，更应该汇报：
  exact-model value of learned abstract policy
而不是只汇报：
  value predicted by noisy estimated kernel
```

`policy_disagreement` 在 graph_rd_joint 上反而很高，不一定是坏事：

```text
graph_rd_joint 的 B 比较密，很多局部 option 近似等价；
estimated kernel 的 tie-breaking 会变，但 exact policy value loss 仍小。
```

### 26.3 更新后的主张

现在可以更明确地区分三件事：

```text
1. Option discovery baseline frontier:
   Laplacian/coverage/betweenness/random 是否自然找到足够好的 graph。

2. Our graph objective:
   joint D_occ + D_audit 是否能在相似 rate 下得到更低 hidden structure risk。

3. Kernel estimation robustness:
   这个 graph-SMDP 方法是否只能依赖 exact oracle kernel。
```

当前证据支持：

```text
joint RD graph 不是简单复现 Laplacian eigenoptions 或 betweenness bottleneck；
它优化的是 graph-option abstraction 的 hidden-structure distortion，
因此在相同 landmark budget 附近明显降低 D_occ 和 D_audit。

即使用 rollout-estimated kernels，
规划得到的 abstract policy 在 exact SMDP 下仍保持很小 policy loss。
```

## 27. Computational Compression Experiments

这一轮把主线从“option baseline 性能比较”切回真正的动机：

```text
full MDP:
  reward/value information 通过 local Bellman backup 从 reward state 逐格广播到所有 states

compressed graph SMDP:
  非关键区域被积分成 edge kernel
  value 只需要在关键 vertex / boundary state 上传播
```

新增三个脚本：

```text
experiments/compression_experiment_utils.py
experiments/run_compression_scaling.py
experiments/run_reward_propagation_curve.py
experiments/run_amortized_multitask.py
```

### 27.1 Compression scaling

命令：

```bash
python3 experiments/run_compression_scaling.py \
  --map-specs corridor:16,32,64 open_room:6,10 four_rooms:7,11 maze:9,13 \
  --methods endpoints betweenness_sqrt eigenoptions_sqrt turn_articulation \
  --out-dir experiments/output/compression_scaling
```

输出：

```text
experiments/output/compression_scaling/compression_scaling.csv
experiments/output/compression_scaling/summary.md
```

关键现象：

```text
corridor_64 endpoints / turn_articulation:
  |S|=64, |B|=2
  state compression=32x
  memory compression=380x
  full VI backups=24320
  SMDP edge backups=4
  planning speedup >1000x
  start gap ~0

maze_13 endpoints:
  |S|=71, |B|=2
  state compression=35.5x
  planning speedup ~487x
  start gap ~0
  but D_occ=6

maze_13 turn_articulation:
  |S|=71, |B|=18
  state compression=3.94x
  planning speedup ~1.77x
  D_occ=0
```

这正好说明：

```text
endpoints graph 可以极端压缩且保持 task value，
但它把结构藏进 option edge；

dense turn graph 不隐藏结构，
但压缩率下降；

我们的 RD objective 应该站在二者中间：
  在 value gap 受控时，最小化 rate；
  同时约束 D_occ / D_audit，避免 one-edge solution。
```

需要注意的 caveat：

```text
single-task exact kernel construction can dominate total wall time
```

比如 four_rooms_11 / maze_13 上，kernel_time 往往比 full VI 更贵。
所以论文里不能只报 single-task total wall time；
必须把它拆成：

```text
upfront graph/kernel cost
planning-only propagation cost
amortized multi-task cost
```

### 27.2 Reward propagation curve

命令：

```bash
python3 experiments/run_reward_propagation_curve.py \
  --map-specs corridor:64 maze:13 \
  --methods endpoints betweenness_sqrt turn_articulation \
  --record-points 1 2 3 5 8 13 21 34 55 89 144 233 \
  --out-dir experiments/output/reward_propagation_curve
```

输出：

```text
experiments/output/reward_propagation_curve/reward_propagation_curve.csv
experiments/output/reward_propagation_curve/summary.md
```

最终点：

```text
corridor_64:
  full VI:
    95 iterations, 24320 local backups

  endpoints graph:
    2 iterations, 4 edge backups

  betweenness_8 graph:
    51 iterations, 2856 edge backups

maze_13:
  full VI:
    53 iterations, 15052 local backups

  endpoints graph:
    2 iterations, 4 edge backups, D_occ=6

  betweenness_9 graph:
    19 iterations, 1368 edge backups, D_occ=5

  turn_articulation graph:
    18 iterations, 5508 edge backups, D_occ=0
```

这条实验直接支持“reward propagation compression”：

```text
full VI 的传播半径依赖 primitive transition graph；
compressed SMDP 的传播半径依赖 abstract graph edge。
```

但是也暴露了核心 trade-off：

```text
最少 edge backups 不等于最合理 abstraction。
endpoints 用 4 个 edge backups 就完成传播，
但 maze 中 D_occ=6，说明结构被藏进 option。
```

所以后续图应该画两种曲线：

```text
x-axis = planning backup count
y-axis = start value error
marker/color = D_occ or D_audit
```

否则 endpoints 会“看起来完胜”，但其实是退化压缩。

### 27.3 Amortized multi-task

命令：

```bash
python3 experiments/run_amortized_multitask.py \
  --map-specs corridor:64 maze:13 \
  --methods endpoints betweenness_sqrt turn_articulation \
  --task-counts 1 5 10 25 50 \
  --max-tasks 50 \
  --goal-source boundary \
  --out-dir experiments/output/amortized_multitask
```

输出：

```text
experiments/output/amortized_multitask/amortized_multitask.csv
experiments/output/amortized_multitask/summary.md
```

这里 `goal_source=boundary` 很重要：

```text
测试的是同一个 abstract graph 上的多 terminal/reward task；
如果 reward state 任意落在非边界 interior，
就必须把 reward state 加入 B，或者定义 edge-level reward projection。
```

结果：

```text
corridor_64 endpoints:
  task_count=1 就 amortized speedup=8.5x
  因为 B=2，kernel 很便宜

corridor_64 betweenness_8:
  task_count=1 speedup <1
  task_count=5 speedup=2.64x
  task_count=7 speedup=3.22x
  break-even estimate ~1.4 tasks

maze_13 betweenness_9:
  task_count=1 speedup <1
  task_count=5 speedup=1.88x
  task_count=8 speedup=2.51x
  break-even estimate ~2.2 tasks

maze_13 turn_articulation:
  task_count=10 speedup=0.93x
  task_count=17 speedup=1.12x
  break-even estimate ~12 tasks
```

这个结果很适合论文叙事：

```text
exact graph kernels have an upfront cost；
planning over the graph is much cheaper；
the method is most compelling when the abstraction is reused across tasks.
```

同时也给了审稿人想看的诚实边界：

```text
如果只做 single-task exact construction，未必比 full VI 快；
如果 tasks 的 rewards/goals 不落在 B 上，必须付额外 rate 把它们加入 B。
```

### 27.4 当前主张改写

现在应该把 paper 的 central claim 改成：

```text
We learn a rate-distortion graph abstraction for Bellman propagation.

The abstraction compresses non-critical state regions into SMDP edge kernels,
so planning propagates value over boundary vertices rather than primitive states.

The compression is constrained by value error and hidden-structure distortion,
preventing degenerate one-edge options that preserve task return while hiding
the Markov structure needed for reusable control.
```

中文直觉：

```text
这不是在找“更强的 option policy”；
而是在找“Bellman 信息传播的最小充分图”。
```

## 28. Graph RD in Compression Tables + Tradeoff Plot

这一轮把 `graph_rd_joint` 正式接进三组计算压缩实验，
并生成 `backup_count vs value_error` 的可视化。

新增脚本：

```text
experiments/plot_reward_propagation_tradeoff.py
```

新增输出：

```text
experiments/output/compression_scaling_with_graphrd/
experiments/output/reward_propagation_curve_with_graphrd/
experiments/output/amortized_multitask_with_graphrd/
experiments/output/reward_propagation_tradeoff_plots/
```

### 28.1 Compression scaling with graph RD

命令：

```bash
python3 experiments/run_compression_scaling.py \
  --map-specs corridor:64 open_room:10 maze:13 \
  --methods endpoints betweenness_sqrt graph_rd_joint turn_articulation \
  --max-splits 18 \
  --out-dir experiments/output/compression_scaling_with_graphrd
```

关键结果：

```text
maze_13:
  full VI backups = 15052

  endpoints:
    B=2,  planning backups=4,    D_occ=6

  betweenness_9:
    B=9,  planning backups=1368, D_occ=5

  graph_rd_joint:
    B=8,  planning backups=1008, D_occ≈0

  turn_articulation:
    B=18, planning backups=5508, D_occ=0
```

这个结果非常好：在 `maze_13` 上，
`graph_rd_joint` 比 betweenness 少一点 B、少一点 planning backups，
同时把 D_occ 从 5 降到约 0；
又比 dense turn graph 少很多 B 和 edge backups。

但它也暴露一个必须诚实报告的问题：

```text
graph_rd_joint construction_time on maze_13 ≈ 21.5s
```

这是当前 brute-force exact RD candidate evaluation 的 upfront cost，
不是 graph SMDP planning 本身的成本。论文里要把它写成：

```text
unoptimized exact-discovery cost
```

并且单独和 amortized reuse 区分。

### 28.2 Reward propagation tradeoff plot

命令：

```bash
python3 experiments/run_reward_propagation_curve.py \
  --map-specs corridor:64 maze:13 \
  --methods endpoints betweenness_sqrt graph_rd_joint turn_articulation \
  --record-points 1 2 3 5 8 13 21 34 55 89 144 233 \
  --max-splits 18 \
  --out-dir experiments/output/reward_propagation_curve_with_graphrd

python3 experiments/plot_reward_propagation_tradeoff.py \
  --input-csv experiments/output/reward_propagation_curve_with_graphrd/reward_propagation_curve.csv \
  --out-dir experiments/output/reward_propagation_tradeoff_plots
```

生成：

```text
backup_vs_value_error_colored_by_docc.png
backup_vs_value_error_colored_by_audit_cvar.png
```

图的解释方式：

```text
x-axis:
  planning backup count

y-axis:
  start value error

color:
  D_occ 或 audit CVaR
```

在 `maze_13` 上，endpoint 的点最左下，
说明它用极少 edge backups 保持 task value；
但颜色显示 D_occ=6，是退化压缩。

`graph_rd_joint` 也很快到低 value error，
但颜色接近 0，说明它没有把关键结构藏进 option edge。

这张图正好表达论文主张：

```text
不是所有 compression 都可接受；
我们要的是 value-preserving 且 structure-preserving 的 compression。
```

### 28.3 Amortized multitask with graph RD

命令：

```bash
python3 experiments/run_amortized_multitask.py \
  --map-specs corridor:64 maze:13 \
  --methods endpoints betweenness_sqrt graph_rd_joint turn_articulation \
  --task-counts 1 5 10 25 50 \
  --max-tasks 50 \
  --goal-source boundary \
  --max-splits 18 \
  --out-dir experiments/output/amortized_multitask_with_graphrd
```

`maze_13` 结果：

```text
betweenness_9:
  upfront≈0.12s
  task_count=5 speedup≈1.97x
  break-even≈2.1 tasks

turn_articulation:
  upfront≈0.38s
  task_count=17 speedup≈1.15x
  break-even≈11 tasks

graph_rd_joint:
  upfront≈21.4s
  task_count=7 speedup≈0.026x
  break-even≈300 tasks
```

这不是坏结果，而是清楚地分出了两个问题：

```text
1. Once the graph is built:
   graph_rd_joint has excellent compressed planning behavior.

2. Building the graph with current exact brute-force RD:
   too expensive unless reused many times or optimized.
```

所以现在下一步的工程/论文方向很明确：

```text
make RD discovery cheaper
```

可能路径：

```text
candidate pruning:
  只评估 high residual / bottleneck / value-gradient states

incremental kernel update:
  split 一个 state 后，不要重建所有 first-boundary kernels

learned surrogate:
  用 cheap local features 预测 RD gain，再只 exact-evaluate top candidates

parallel candidate evaluation:
  当前每个 split candidate 是 embarrassingly parallel
```

### 28.4 更新后的 claim

现在可以把主张写得更锋利：

```text
The learned RD graph is not primarily a faster discovery algorithm yet.

It is evidence that the right object is a compressed Bellman-propagation graph:
few vertices and edge backups, low value error, and low hidden-structure distortion.

The remaining systems problem is to reduce the upfront discovery/kernel cost.
```

## 29. Cheap RD Surrogate as an Explicit Operator Prototype

这一轮开始做“从 working exact RD 反推显式算子”的第一步。

动机：

```text
exact RD split:
  对 top-k candidate state 逐个加入 B
  每个 candidate 都重建 first-boundary kernels + SMDP planning
  成本很高

surrogate/operator split:
  不重跑 candidate evaluation
  只看当前 graph 下每条 edge 暴露出的 hidden-boundary score
  直接给每个 candidate state 一个显式分数
```

新增 residual split policy：

```text
--residual-split-policy rd_surrogate
```

新增 recipe：

```text
learned_rd_surrogate_joint_occ2_audit2
```

并且压缩实验现在可以用：

```text
graph_rd_surrogate_joint
```

### 29.1 Surrogate operator 形式

当前 surrogate 的核心是：

```text
score(x)
  = occupancy-weighted hidden structure resolved by making x a vertex
  + audit-tail hidden structure resolved by making x a vertex
  - approximate rate cost
```

更具体地，对当前 graph 中每条 valid edge `e`，已有：

```text
policy occupancy:
  rho(e)

candidate distinct first-hit score:
  h_e(x)

edge audit exposure:
  a(e)
```

于是候选点 `x` 的两个主要分量是：

```text
D_occ surrogate:
  sum_e rho(e) h_e(x)

D_audit surrogate:
  sum_{e in tail} h_e(x)
```

其中 `tail` 是当前 edge hidden-distinct exposure 的 top 5% tail。

这就是一个很像 graph operator 的东西：

```text
它不是先试每个 split 再看结果；
它直接从当前 reduced graph 的 residual exposure field
给每个 state 生成一个 saliency / split score。
```

这可以作为之后推导“RD-Laplacian-like operator”的雏形。

### 29.2 Exact RD vs surrogate RD

命令：

```bash
python3 experiments/run_compression_scaling.py \
  --map-specs corridor:64 maze:13 \
  --methods endpoints betweenness_sqrt graph_rd_joint graph_rd_surrogate_joint turn_articulation \
  --max-splits 18 \
  --out-dir experiments/output/rd_surrogate_compression_comparison
```

结果：

```text
maze_13 exact graph_rd_joint:
  B=8
  planning backups=1008
  D_occ≈9.47e-08
  audit CVaR≈9.47e-08
  construction_time≈21.33s

maze_13 graph_rd_surrogate_joint:
  B=8
  planning backups=1008
  D_occ≈9.47e-08
  audit CVaR≈9.47e-08
  construction_time≈1.54s
```

也就是说，在这个代表性 maze 上：

```text
surrogate 找到了和 exact RD 一样的 graph quality，
但 discovery cost 降低约 14x。
```

这非常重要，因为它说明 exact RD 的 split decision 里，
至少有一大部分可以被当前 residual exposure field 直接解释。

### 29.3 Amortized effect

命令：

```bash
python3 experiments/run_amortized_multitask.py \
  --map-specs maze:13 \
  --methods graph_rd_joint graph_rd_surrogate_joint betweenness_sqrt turn_articulation \
  --task-counts 1 5 10 25 50 \
  --max-tasks 50 \
  --goal-source boundary \
  --max-splits 18 \
  --out-dir experiments/output/rd_surrogate_amortized_comparison
```

结果：

```text
exact graph_rd_joint:
  upfront≈21.73s
  break-even≈300-470 tasks

graph_rd_surrogate_joint:
  upfront≈1.65s
  break-even≈20-28 tasks

betweenness_9:
  upfront≈0.12s
  break-even≈2.1 tasks

turn_articulation:
  upfront≈0.39s
  break-even≈11 tasks
```

surrogate 还没有比 handcrafted betweenness 便宜，
但它已经把 exact RD 的最大弱点从“几百个 task 才摊平”
降到“二十几个 task 量级”。

更重要的是，surrogate 仍保留了 RD graph 的结构质量：

```text
betweenness_9:
  D_occ≈5

graph_rd_surrogate_joint:
  D_occ≈0
```

### 29.4 下一步数学化目标

现在可以把“像 Laplacian operator 一样的表达式”具体化为：

```text
给定当前 boundary graph B 和 option-induced first-hit kernels，
定义一个 residual exposure operator L_RD 或 S_RD：

S_RD(x)
  = alpha * sum_e rho_pi(e) h_e(x)
  + beta  * CVaR_tail_e h_e(x)
  - lambda * RateDelta(x)

选择 top eigen/saliency/extrema state 作为下一批 boundary vertices。
```

这里：

```text
rho_pi(e):
  当前 abstract policy 在 boundary edge 上的 occupancy

h_e(x):
  option e 在到达 visible boundary 前 first-hit x 的概率/信息量

CVaR_tail:
  用来惩罚 option library 中隐藏结构风险最高的边

RateDelta(x):
  加一个 vertex 后的编码成本近似
```

这还不是最后的可证明 operator，
但已经是一个明确的数学对象，而不是纯启发式 search。

接下来最值得做：

```text
1. 记录 exact RD selected state 和 surrogate top state 的 rank agreement；
2. 在更多 maps/sizes 上比较 exact vs surrogate 的 graph quality；
3. 推导 S_RD(x) 是 constrained rate-distortion objective 的一阶贪心近似；
4. 问 GPT 反驳这个 operator 形式是否有理论漏洞。
```

如果要问 GPT，先 push 当前状态。

### 29.5 Agreement with exact RD

又补了一个直接验证 surrogate 是否真的在模仿 exact RD 的实验：

```text
experiments/run_rd_surrogate_agreement.py
```

命令：

```bash
python3 experiments/run_rd_surrogate_agreement.py \
  --map-specs maze:13 \
  --max-splits 18 \
  --out-dir experiments/output/rd_surrogate_agreement
```

结果：

```text
maze_13:
  exact_time≈19.83s
  surrogate_time≈1.50s
  speedup≈13.2x

  exact_steps=6
  surrogate_steps=6
  first_match_rate=1.0
  mean exact-selected rank in surrogate list=3.75
  max exact-selected rank in surrogate list=6
```

逐步看：

```text
step 0: exact selects 57, surrogate selects 57
step 1: exact selects 13, surrogate selects 13
step 2: exact selects 17, surrogate selects 17
step 3: exact selects 53, surrogate selects 53
step 4: exact selects 3,  surrogate selects 3
step 5: exact selects 5,  surrogate selects 5
```

这非常支持当前方向：

```text
exact RD split 不是黑箱 magic；
在这个 maze 上，它选的 state 可以由显式 residual exposure operator 复现。
```

因此现在可以把下一轮理论问题问得很具体：

```text
Can S_RD(x) be derived as the first-order greedy approximation
to a constrained rate-distortion objective over boundary sets?

What assumptions are needed for h_e(x), rho_pi(e), and CVaR_tail terms
to behave like an operator rather than a heuristic score?
```

## 30. GPT_answer_9 后续：fixed basis + multi-probe RD

`GPT_answer_9.md` 的核心反驳是：held-out residual probe 的失败不是 frozen
operator exactness 的失败，而是 probe overfitting。

新增参考：

```text
reference/papers/gdro_2024__efficient-algorithms-for-empirical-group-distributionally-robust-optimization-and-beyond.pdf
reference/pages/gdro_2024.html
reference/gpt_answer_9_download_report.md
```

`State Abstraction as Compression in Apprenticeship Learning` 和
`david-abel/rl_info_theory` 之前已经在 `reference/` 缓存。

实现：

```text
experiments/run_rd_multiprobe_basis.py
```

这个实验把 GPT 的建议拆成两层：

```text
fixed basis:
  C0 = topology + spectral + coverage + deterministic random anchors

residual_train basis:
  C_train = train residual probes induced candidate universe

multi-probe risk:
  single / mean / mean_cvar / max
```

主 score 是：

```text
S_rho(x|B) =
  lambda * [rho(D(B)) - rho(D(B) - Delta(x))] - c_x
```

其中 `Delta_l(x)` 由每个 probe 的 first-hit Green finite difference 给出。

对应 Lean 证明也补了：

```text
proof/RDOperator.lean:
  MultiProbeObjective.fd_exact
```

这说明只要 `C0/O0`、probe family、edge weights、rate cost 在 greedy step 内固定，
任意有限向量 risk aggregator `rho` 都有 exact finite-difference theorem。

第一组实验输出：

```text
experiments/output/rd_multiprobe_basis/summary.md
```

当前结果的关键信息不是“multi-probe 已经赢了”，而是一个更有用的反例：

```text
train probes = junction + bottleneck
test probes  = turn_articulation + combined + value_gradient
```

在 maze 上，mean/mean_cvar/max 能把 train probe bits 压到接近 0，
但 held-out test bits 仍然很高。这说明：

```text
固定 basis 只是解决 hypothesis leakage；
probe set 本身还必须覆盖 held-out lens 的结构类型。
```

下一步应该做 probe-count / leave-one-lens-out scaling：

```text
m = 1, 2, 3, 4, ...
plot:
  train_bits_mean
  test_bits_mean
  test_bits_cvar
  test-train gap
```

如果随着 train probe family 变丰富，held-out gap 下降，就能和
Hoeffding + finite hypothesis class bound 对上。

### 30.1 Probe-count scaling

我又补了 probe 数量变化实验：

```text
experiments/run_rd_probe_count_scaling.py
experiments/output/rd_probe_count_scaling/summary.md
```

默认 probe pool：

```text
junction, bottleneck, turn_articulation, combined, value_gradient, transition_entropy
```

这个实验还比较粗糙，但已经暴露出一个重要点：

```text
只增加 probe 数量并不自动改善 held-out；
probe 的顺序/族覆盖和 risk aggregator 会强烈影响结果。
```

例如在 maze/four_rooms 上，某些 `mean` / `mean_cvar` 前缀训练会把 train bits
压低但 held-out 仍高；而 `max` 在部分前缀上表现出完全不同的 boundary 选择。
这说明下一步不只是“多加 probes”，而是要做：

```text
leave-one-lens-out
stratified probe sampling
balanced CVaR group weighting
```

也就是把 `P_train` 从任意 prefix 改成覆盖 topology / stochastic / value-gradient
三类 lens 的分层集合。

### 30.2 Leave-one-lens-out 与 stratified validation

继续补了正式的 lens validation：

```text
experiments/run_rd_lens_validation.py
experiments/output/rd_lens_validation/summary.md
```

默认 lens group：

```text
topology:
  junction, bottleneck, turn_articulation, betweenness

value:
  value_gradient

stochastic:
  transition_entropy

extra held-out:
  combined
```

实验有两个 protocol：

```text
leave_one_lens_out:
  每次 hold out 一个 lens，其余全部训练

stratified_one_per_group:
  每次从 topology/value/stochastic 中各取一个训练，其余 lens 测试
```

第一轮结果：

```text
LOO mean test bits:
  mean_cvar ≈ 165.7
  max       ≈ 69.4

stratified mean test bits:
  mean_cvar ≈ 129.6
  max       ≈ 103.9
```

所以现在更明确了：

```text
1. mean_cvar 不是自动稳健；它仍会被 train probe composition 影响。
2. max/minimax 在 leave-one-lens-out 上明显降低平均 held-out risk，
   但也会在 open_room/junction 这类 lens 上出现个别 worst-case failure。
3. topology 组内部不是可互换的：junction / bottleneck / turn / betweenness
   各自诱导的 held-out risk 不一样。
```

下一步更像是：

```text
group-balanced robust risk:
  rho(D) = mean_groups CVaR_lenses_in_group(D)
  或 max_groups CVaR_lenses_in_group(D)

而不是简单 mean_cvar over all probes。
```

这能防止某一类 lens 数量多而淹没其他类，也能比 pure max 少一点过度悲观。

### 30.3 Group-balanced robust risk

继续把上面的 group-balanced risk 也接进了 operator：

```text
experiments/run_rd_multiprobe_basis.py:
  group_mean_cvar
  group_max_cvar
```

`run_rd_lens_validation.py` 现在默认同时跑：

```text
mean_cvar
max
group_mean_cvar
group_max_cvar
```

第一轮结果有点反直觉，但很有价值：

```text
leave-one-lens-out mean test bits:
  mean_cvar       ≈ 165.7
  group_mean_cvar ≈ 165.7
  max             ≈ 69.4
  group_max_cvar  ≈ 69.4

stratified mean test bits:
  mean_cvar       ≈ 129.6
  group_mean_cvar ≈ 129.6
  max             ≈ 103.9
  group_max_cvar  ≈ 103.9
```

也就是说，在当前 tiny probe family 和 `B=5` budget 下，
group-balanced risk 没有改变 greedy 选择；它和普通 mean/max 落到同一个 boundary。
这不是坏事，它说明失败不是单纯“某一组 lens 数量太多导致加权失衡”，
而更像是：

```text
1. topology 组内部 lens 不是互相替代的；
2. 当前 split budget 太小，某些 held-out lens 需要不同 vertex；
3. pure max 在平均 held-out 上更稳，但仍会牺牲个别 open-room/junction case。
```

下一步如果继续推进，应该改成 constrained multi-objective：

```text
min R(B)
subject to:
  CVaR_topology(B) <= eps_topology
  CVaR_value(B) <= eps_value
  CVaR_stochastic(B) <= eps_stochastic
```

而不是把所有 group 塞进单个 scalar risk。

### 30.4 Group-constrained RD + beam search

现在把真正的 group-constrained 版本也补上了：

```text
experiments/run_rd_group_constrained.py
experiments/output/rd_group_constrained/summary.md
```

目标不再是另一个 scalar risk，而是：

```text
min R(B)
subject to:
  CVaR_topology(B)   <= eps_topology
  CVaR_value(B)      <= eps_value
  CVaR_stochastic(B) <= eps_stochastic
```

实现上先用 endpoint boundary 估计每个 group 的初始 risk，
再用 `budget_frac` 设定：

```text
eps_g = budget_frac * initial_CVaR_g
```

然后贪心/beam 搜索选择 boundary，使 group violation：

```text
sum_g max(0, risk_g(B) - eps_g)
```

下降。

一个重要实现细节：普通 one-step greedy 会在 maze 里选到局部最优但死路的 split。
所以脚本加入了：

```text
--beam-width
--beam-expand
```

当前正式结果用：

```text
beam_width = 4
beam_expand = 6
max_splits = 5
budget_fracs = 0.25, 0.5
```

结果很强：

```text
maze_9:
  group_constrained:
    B=3, feasible=True, test_cvar=0
  scalar_mean_cvar:
    B=7, feasible=False, test_cvar≈255.7
  scalar_max:
    B=7, feasible=True, test_cvar=0

four_rooms_9:
  group_constrained:
    B=5, feasible=True, test_cvar=0
  scalar_mean_cvar:
    B=7, feasible=False, test_cvar≈355.6
  scalar_max:
    B=7, feasible=True, test_cvar=0

open_room_7:
  group_constrained:
    B=7, feasible=True
  scalar_mean_cvar:
    B=7, feasible=True
  scalar_max:
    B=7, feasible=True
```

这基本支持 GPT 的方向，但也补了一条关键修正：

```text
group constraints 本身还不够；
因为 first-hit/kernel 重构是非子模的，必须配 beam/lookahead，
否则 one-step greedy 可能选到 violation reduction 最大但后续不可继续的 split。
```

现在的论文故事可以更稳地写成：

```text
1. frozen multi-probe RD operator: exact theorem
2. robust abstraction objective: group-constrained RD
3. optimization algorithm: small-width beam greedy, because adaptive graph construction is non-submodular
4. empirical result: constraints reach feasibility with fewer vertices than scalar max,
   while scalar mean/CVaR can badly violate held-out group constraints
```

## 31. GPT answer 10: two-layer contribution, core benchmark, proof obligations

`GPT_answer_10.md` resolves the packaging problem:

```text
Frozen RD Green Operator 是 theorem；
Adaptive Group-Constrained Beam Search 是 solver。
```

This is the right way to avoid overclaiming. The exactness guarantee belongs to
the frozen local marginal:

```text
S_rho(x | B)
  = lambda [rho(D(B)) - rho(D(B) - Delta(x))] - c_x
  = J_theta^frozen(B) - J_theta^frozen(B union {x})
```

When the algorithm recomputes options, edges, occupancy, or group probes after a
split, the objective changes. That adaptive step is not exact; it is a
drift-aware constrained search driven by an exact local oracle.

### 31.1 Unified core benchmark

Added:

```text
experiments/run_core_benchmark.py
experiments/output/core_benchmark/
```

It produces one table for:

```text
full_vi
graph_rd_joint
graph_rd_surrogate_joint
group_constrained_rd
eigenoptions_sqrt
betweenness_sqrt
random_landmarks_sqrt
coverage_sqrt
```

across classic grid families:

```text
corridor
open_room
four_rooms
maze
```

and multiple slip settings.

The compact run used:

```text
map_specs = corridor:16,32, open_room:7, four_rooms:7, maze:9
slips = 0.0, 0.05
n_rollouts = 20
```

Main readout:

```text
best planning-only speedup over full VI: about 295x
worst graph start-value gap: about 0.0497

mean planning-only speedup:
  graph_rd_joint           ≈ 109x
  graph_rd_surrogate_joint ≈ 109x
  group_constrained_rd     ≈ 58x
  betweenness_sqrt         ≈ 3.9x
  eigenoptions_sqrt        ≈ 3.4x
  coverage_sqrt            ≈ 9.3x
```

But this table also makes the limitation clear:

```text
planning propagation is compressed;
single-task total runtime is still dominated by boundary discovery / group-constrained construction.
```

That matches the paper story better than claiming immediate single-task wall-time
dominance. The stronger speed claim should be multi-task amortized compression.

One caution from this compact run:

```text
group_constrained_rd used beam_width=2, beam_expand=4 for speed.
The stochastic open_room_7 row is not feasible under that tight beam.
```

So the core table is a runtime/generalization benchmark, not the final
group-constrained feasibility table. The earlier `rd_group_constrained` run with
`beam_width=4, beam_expand=6` is still the stronger feasibility result.

### 31.2 Proof layer update

`proof/RDOperator.lean` now formalizes more of the theorem stack:

```text
1. frozen finite-difference exactness
2. adaptive drift decomposition
3. margin stability
4. multi-probe robust finite-difference exactness
5. first-hit certificate existence
6. finite absorbing-chain Green formula / nonnegativity / row bound
7. truncated Green convergence and epsilon tail-error bound
8. bits-distortion finite-difference / Taylor bound certificate
9. discounted residual -> value-gap bound
10. zero group violations -> group feasibility
11. finite-option graph-SMDP Bellman contraction/non-expansion
```

The new proof pieces are finite/scaled but Lean-checked. They define what the
paper must instantiate over real-valued finite MDPs:

```text
first-hit Green kernel existence:
  finite absorbing Markov chain -> first-hit witness / harmonic measure
  K = e_b^T (I - P_II)^-1 P_IC
  K >= 0 and row mass <= scale

truncated Green:
  exact kernel = truncated prefix + tail
  tail <= eps -> score error <= eps
  tailBound -> 0 -> truncated kernel converges in epsilon form

bits distortion:
  phi_before - phi_after = first_order + Taylor remainder
  |remainder| <= curvature budget

model residual -> value gap:
  (1 - gamma) * valueGap <= residual -> valueGap <= residual / (1 - gamma)

group constraints:
  zero per-group violation indicators -> feasible boundary set

graph-SMDP Bellman:
  finite option backup contracts in sup norm
  repeated graph Bellman iterates are non-expansive
```

The Mathlib real layer has now started in `proof/RDOperatorReal.lean`:

```text
GreenFormula:
  (I - P_II)^-1 P_IC solves (I - P_II) K = P_IC when det(I - P_II) is a unit
  nonnegative inverse/block entries imply K >= 0
  finite row-mass bounds imply entry bounds

NeumannPrefix:
  sum_{t=0}^K P_II^t P_IC
  converges entrywise under an explicit tail-bound certificate
  row-substochastic P_II with row mass <= q < 1 gives
    term bound: P_II^n P_IC <= q^n * exitBound
    finite tail bound: exitBound * q^(K+1)/(1-q)
  weighted spectral certificate P_II w <= q w gives
    weighted term bound: P_II^n P_IC <= q^n * exitBound * w_i
    weighted tail bound: exitBound * w_i * q^(K+1)/(1-q)

bitsPhi:
  phi(h) = -log(1 - h + eps) / log 2
  derivative proved by Mathlib Real.hasDerivAt_log
  bitsPhiDeriv differentiates to bitsPhiSecond
  delta <= 1 - h + eps bounds |bitsPhiSecond|
  Mathlib Taylor converts this curvature bound to first-order remainder bound
  iteratedDerivWithin glue is automatic on nondegenerate closed intervals

graph-SMDP Bellman:
  each option Q backup is gamma-Lipschitz
  finite max over a nonempty option set is gamma-Lipschitz
  real residual -> value gap is proved in division and budget forms
```

Remaining proof work is now narrower:

```text
1. optional: connect Mathlib spectrum/eigenvalue API directly to the weighted
   P_II w <= q w certificate
2. optional: add an infinite-tail HasSum/tsum theorem beside the finite-tail
   geometric bound
```

### 31.3 Current next experiments suggested by answer 10

The next experiments should be:

```text
beam width ablation:
  W = 1,2,4,8, exhaustive-small

group constraints ablation:
  none / hard-only / hard+diversity / hard+multi-probe-CVaR / full beam

small exhaustive oracle:
  enumerate all B with |B| <= k on tiny maps
```

These are the most direct way to answer the reviewer objection that beam search
and group constraints are heuristic. The theorem says the frozen oracle is
exact; these ablations should show when the adaptive solver needs beam/lookahead
and whether it approaches the exhaustive small-map optimum.

### 31.4 Top-conference evidence pass

I added two more experiment entry points for the current submission-risk list:

```text
experiments/run_large_scale_compression.py
experiments/run_solver_validity.py
```

and ran:

```text
experiments/output/large_scale_compression/summary.md
experiments/output/amortized_multitask_large_allstates/summary.md
experiments/output/solver_validity/summary.md
```

The large-scale compression run removes dense policy iteration from the timing
loop and measures only the relevant comparison:

```text
full-state VI propagation
vs.
graph construction + exact first-boundary kernels + graph-SMDP VI
```

The compact large-scale pass reached 144 states:

```text
best planning-only speedup: 2471x
best total wall-time speedup: 10.6x
worst start-value gap: 0.0785
```

The interpretation is now sharper. Planning propagation is strongly compressed,
but exact first-hit kernel construction is the bottleneck. On `corridor_64`,
the compressed method wins end-to-end. On `open_room_12` and `corridor_128`,
the dense Green solve dominates and total wall time is worse even though SMDP
planning itself is three orders of magnitude cheaper. This is exactly the
place where the truncated Green / cached Green / incremental kernel update
work should enter the paper.

The all-state multi-task amortization run is a useful negative control. If we
force 25 arbitrary task goals into the boundary once, the graph remains exact
for those tasks but compression drops sharply:

```text
corridor_64: |B| = 26, best amortized speedup at 25 tasks ≈ 0.32x
maze_13:     |B| = 26-36, best amortized speedup at 25 tasks ≈ 0.29x
```

So the current strong amortization claim should not be stated as “arbitrary
state-goal multitask planning is already faster.” The honest claim is:

```text
The graph compresses propagation for tasks whose rewards/goals live on the
abstract boundary. Arbitrary interior goals require either adding those goals as
vertices, or learning reward-feature kernels; otherwise the current exact
graph-SMDP model is not the right object.
```

The solver-validity run compares three things on small maps:

```text
1. exhaustive oracle over every subset up to the split budget
2. operator-only greedy/beam group RD
3. exact-refined beam: use the frozen operator to propose top candidates,
   then rank those candidates by actual group-RD evaluation
```

The result is also clarifying:

```text
exact boundary matches:        14 / 18 rows
zero total-violation gap:      14 / 18 rows
feasible/infeasible matches:   15 / 18 rows
oracle subsets evaluated:      66
```

Narrow operator-only search still fails on `open_room_5` and `maze_9`, but
beam width 4 or exact-refined beam recovers the exhaustive oracle in those
cases. On `four_rooms_7`, the oracle itself is infeasible under the two-split
budget, and exact-refined beam matches that infeasible optimum.

This changes the paper framing again:

```text
Frozen RD Green Operator:
  theorem / scoring primitive

Operator-only beam:
  fast heuristic, useful but not always reliable

Exact-refined operator beam:
  submission-facing solver; the operator prunes the candidate universe and
  actual group RD evaluation chooses among the short list
```

The remaining top-conference blockers are therefore narrower:

```text
1. replace exact dense first-hit solves with truncated/cached/incremental Green kernels
2. add reward-feature kernels if we want arbitrary interior-goal multitask claims
3. run the same evidence on larger procedural maps after the kernel bottleneck is fixed
```

### 31.5 First pass on the Green-kernel bottleneck

I added executable truncated Green kernels to the experiment code:

```text
bellman_kron_reduce_truncated
first_hit_reduce_truncated
first_hit_interior_occupancy_truncated
```

and exposed them through:

```text
build_first_boundary_reductions(..., first_hit_mode="truncated", first_hit_truncation_steps=K)
experiments/run_large_scale_compression.py --first-hit-mode truncated --first-hit-truncation-steps K
experiments/run_kernel_approximation_benchmark.py
```

There is also a small cache-style cleanup: first-hit calls now reuse the
target-policy free transition matrix `P_free` instead of rebuilding a different
absorbing transition matrix for every terminal set. This is valid because
first-hit reduction only uses the interior-to-terminal block; terminal rows are
excluded from the Green solve.

The kernel approximation benchmark is:

```text
experiments/output/kernel_approximation_large/summary.md
```

On `corridor_128` and `open_room_12` with endpoint graphs:

```text
truncated K=32:
  kernel speedup up to 146x, but corridor value error is large

truncated K=64:
  still >100x kernel speedup on large maps, but corridor error remains visible

truncated K=128:
  112-119x kernel speedup
  open_room_12 matches exact start value to numerical precision
  corridor_128 start-value difference drops to about 0.123
```

The large-scale compression comparison is now:

```text
exact:
  experiments/output/large_scale_compression_exact_updated/summary.md

truncated K=128:
  experiments/output/large_scale_compression_truncated_k128/summary.md
```

The best end-to-end speedup in the truncated run is now `31.9x`, with planning
speedup up to `5075x`. The tradeoff is that a finite horizon can bias long
corridor values unless K is large enough. This gives the next mathematical and
algorithmic target:

```text
adaptive K per edge:
  stop when discounted tail bound <= value tolerance

or weighted/spectral tail certificate:
  use the Lean theorem's q^K/(1-q) bound to choose K automatically

or cached exact solve:
  use exact Green for long low-branching corridors where K would be too large,
  and truncated Green for open-room/stochastic local kernels
```

### 31.6 Adaptive per-edge K

I added `first_hit_mode="adaptive"` as the next step after fixed-K truncation.
The adaptive mode still uses the Neumann-prefix implementation, but each
first-hit edge stops independently once a frontier tail certificate is below
the requested tolerance:

```text
tail_bound = min(
  max(remaining_hit_mass, discounted_reward_tail),
  q^(K+1) / (1-q)          when q < 1
)

stop when tail_bound <= epsilon
```

This uses the same mathematical shape as the Lean tail theorem, but with a
frontier-dependent bound so corridor edges are allowed to run longer while
open-room edges stop early.

The benchmark entry point now includes adaptive kernels:

```text
experiments/run_kernel_approximation_benchmark.py
  --adaptive-tail-tols 1e-3 1e-6
  --adaptive-max-steps 512
```

Current output:

```text
experiments/output/kernel_adaptive_benchmark/summary.md
experiments/output/large_scale_compression_adaptive/summary.md
```

The key result is exactly the desired behavior:

```text
corridor_128 / endpoints:
  fixed K=128: start-value diff ≈ 0.123
  adaptive eps=1e-6: used K up to 160, start-value diff ≈ 1e-8
  kernel speedup vs exact ≈ 45x

open_room_12 / endpoints:
  adaptive eps=1e-6: used K up to 41, start-value diff ≈ 1.8e-8
  kernel speedup vs exact ≈ 164x

maze_13 / endpoints:
  adaptive eps=1e-6: used K up to 42, start-value diff ≈ 1.5e-8
```

So the method story is now much cleaner:

```text
Exact Green:
  theorem/reference kernel

Fixed-K truncated Green:
  fast ablation; can undercut long corridors if K is too small

Adaptive Green:
  practical solver; same operator family, automatic K, tiny value error in the
  current suite, and tens-to-hundreds-x kernel speedup on larger maps
```

This is probably ready to ask GPT for critique after the next push. The best
question is not “is adaptive K good?” but:

```text
Does the frontier-tail certificate plus Lean Neumann theorem justify presenting
adaptive Green as the main implementation, with exact Green as the reference
operator and fixed-K as an ablation?
```

### 31.7 Adaptive Green score certification

GPT's answer says the submission claim does not need a fully weighted spectral
certificate if we phrase the implementation as:

```text
Exact Green:
  reference operator / oracle

Adaptive Green:
  tail-certified Neumann-prefix implementation

Fixed-K Green:
  ablation
```

The missing practical layer was not another global spectral norm. It was a
downstream score interval:

```text
K_e(x) in [Khat_e(x), Khat_e(x) + T_e(x)]

accept adaptive top-1 iff
  Shat_top - B_top > Shat_runner + B_runner
```

I added this check in:

```text
experiments/run_adaptive_green_certification.py
```

The script evaluates every non-boundary state in the candidate universe, builds
finite-difference bits-RD score intervals from the adaptive first-hit tail
certificate, and marks each row as either:

```text
accept
needs_refinement_or_exact_fallback
```

Current output:

```text
experiments/output/adaptive_green_certification/summary.md
```

On the current endpoint suite:

```text
exact top-1 matches:        8 / 8
interval-certified top-1:   4 / 8
```

The accepted rows are the clean cases:

```text
open_room_12:
  eps=1e-3 and eps=1e-6 both certify the same top split as exact
  speedup vs exact in this score-cert run is about 19x to 27x

four_rooms_11:
  eps=1e-3 and eps=1e-6 both certify the same top split as exact
  speedup vs exact is about 12x to 15x
```

The uncertified rows are informative rather than failures:

```text
corridor_128:
  adaptive and exact agree, but the top margin is zero because the best split
  is tied by symmetry, so no interval method can certify a strict top-1

maze_13:
  adaptive and exact agree, but the bits distortion is near the high-curvature
  regime, so the conservative interval stays too wide; the anytime algorithm
  should refine or exact-fallback on the ambiguous top set
```

This gives a safer main-paper implementation claim:

```text
Adaptive Green is decision-certified whenever the score intervals separate.
When they do not separate, the solver refines the tolerance/horizon or falls
back to exact Green on the ambiguous top set.
```

So the proof/experiment hierarchy is now:

```text
Lean Neumann theorem:
  justifies the tail decomposition and epsilon certificate

adaptive Green benchmark:
  shows fixed-K failure is solved with large kernel speedups

score certification table:
  shows when the adaptive implementation preserves the exact-Green RD decision
```

### 31.8 First attempt at the fully weighted spectral certificate

Even though GPT said it is not a blocker, I tried the fully weighted route
because it is the stronger mathematical object.

The Lean layer now has three extra real theorems in:

```text
proof/RDOperatorReal.lean
```

They cover:

```text
1. signed weighted spectral tail:
   if P_II w <= q w and q < 1, then signed Neumann tails are bounded in
   weighted sup-norm, not only nonnegative hit-probability tails

2. weighted downstream score interval:
   for fixed nonnegative edge/objective weights a_e,
   |S(K) - S(Khat)| <= sum_e a_e T_e

3. interval-certified top choice:
   if approximate score intervals separate top-1 from runner-up, the top
   choice is also exact under the weighted score
```

I also added a diagnostic:

```text
experiments/run_weighted_spectral_certificate.py
experiments/output/weighted_spectral_certificate/summary.md
```

This computes a Collatz-style positive-vector certificate:

```text
P_II w <= q w, q < 1
tail <= c * w_start * q^(K+1)/(1-q)
```

The result is mixed in an informative way:

```text
row q < 1:
  0 / 16 edge-basis rows

weighted q < 1:
  16 / 16 edge-basis rows
```

So the spectral route does prove what the raw row-substochastic certificate
cannot: even when some rows have mass exactly 1, the interior block can still
have a valid weighted contraction certificate.

But the optimized floating-point certificates are badly conditioned:

```text
weight_dynamic_range can reach 1e12 - 1e20
```

and the resulting corridor tail bound is still very conservative:

```text
corridor_128 K=128:
  certified weighted row tail <= about 125
  actual row tail             <= about 0.976
```

For open rooms / four rooms / maze the optimized spectral bound becomes tiny,
but the giant weight dynamic range means we should not make this the default
runtime certificate yet. The right interpretation is:

```text
formal claim:
  weighted spectral certificate exists and can certify signed weighted tails

implementation claim:
  frontier-tail / score-interval certificate is still the practical default

next proof/engineering target:
  conditioned weighted certificate or interval/rational verification of w
```

This is useful for the paper: the fully weighted certificate is no longer just
future work in principle. We have a Lean-backed theorem and a diagnostic showing
exactly why it is stronger but numerically delicate.

### 31.9 Certified Adaptive Green with top-set exact fallback

GPT answer 12 made the submission-facing algorithm more precise:

```text
do not use pure adaptive Green as an unconditional main solver
use Certified Adaptive Green with top-set exact fallback
```

I implemented this directly inside:

```text
experiments/run_adaptive_green_certification.py
```

The algorithm is now:

```text
1. score every candidate with adaptive Green intervals
2. if the top interval separates, accept adaptive top-1
3. otherwise form the ambiguous set A = {x : U_x >= max_z L_z}
4. evaluate exact Green scores on A
5. accept the exact best in A if it beats all outside interval upper bounds
6. if exact scores tie, return a certified top-set with canonical tie-break
```

I also added the corresponding Lean theorem:

```text
top_set_exact_fallback_global_optimal
top_set_exact_fallback_beats_outside
```

These formalize the key fallback claim: exact evaluation on the ambiguous set
is globally valid if the exact winner beats every outside upper bound.

Current output:

```text
experiments/output/adaptive_green_certification/summary.md
```

The updated main table now reports:

```text
exact top-1 matches:          8 / 8
interval-certified top-1:     4 / 8
top-set fallback rows:        4 / 8
final certified decisions:    8 / 8
```

The behavior matches GPT's recommended story:

```text
open_room_12 and four_rooms_11:
  accepted by interval certificate, no fallback

corridor_128:
  tie_uncertified; exact top set has 126 tied candidates, so the solver returns
  a certified top-set with canonical tie-break

maze_13:
  curvature_uncertified_full_set; the interval is too wide, so the solver
  exact-fallbacks on the ambiguous set and returns a certified exact top-set
```

This gives a much stronger submission claim:

```text
Exact Green defines the reference operator.
Adaptive Green is the default tail-certified approximation.
When score intervals separate, the adaptive decision is certified.
When they do not, exact Green is used only on the ambiguous top set.
Fixed-K remains an ablation.
```

The only caveat is timing: the current `fallback_exact_time_proxy_sec` scales
the exact reference time by the ambiguous-set fraction because the diagnostic
still computes exact reference rows for the table. The CSV/JSON also report the
conservative full-exact fallback time. For final submission, if needed, this can
be replaced by a true candidate-subset exact kernel evaluator.

### 31.10 Conditioned and rational weighted certificates

GPT answer 13 says conditioned/rational weighted certificates are not a
submission blocker, but they are a useful strengthening. I implemented them as
an experiment-side audit rather than changing the main runtime certificate.

New entry point:

```text
experiments/run_conditioned_weighted_certificate.py
```

Current output:

```text
experiments/output/conditioned_weighted_certificate/summary.md
```

The script does two extra things beyond the earlier weighted spectral table:

```text
conditioned Collatz search:
  search P_II w <= q w subject to cond(w) <= C

rational audit:
  round P, w, q to rationals and verify P_II w <= q w exactly using Fraction
```

The useful result is:

```text
all found certificates rational-verified:
  92 / 92
```

Conditioning gives a clear tradeoff:

```text
corridor_128:
  cond cap 100: no certificate found
  cond cap 1e4: q <= 0.9635, tail K=128 <= 810.7
  cond cap 1e6: q <= 0.9274, tail K=128 <= 275.4
  unconditioned: q <= 0.8276, tail K=128 <= 124.5
  actual tail K=128 <= 0.976

open_room_12:
  cond cap 100 already works and rational-verifies
  boundary tail K=128 <= 3.58e-4

four_rooms_11:
  cond cap 100 already works and rational-verifies
  boundary tail K=128 <= 1.76e-5

maze_13:
  residual basis works even at cond cap 100 with tiny tail
  boundary basis at cond cap 100 is valid but loose; larger caps tighten it
```

So the status is better than before:

```text
weighted spectral certificate:
  theoretically stronger than row q<1

conditioned weighted certificate:
  exposes the q-vs-conditioning Pareto tradeoff

rational audit:
  turns the floating Collatz candidate into a reproducible exact inequality
  check for the reported rows
```

But it still should not replace the main implementation:

```text
frontier-tail + top-set exact fallback remains the main solver
conditioned/rational weighted spectral certificate is an appendix/theorem audit
```

The reason is visible in corridor: even a rational-verified conditioned
certificate can be very conservative compared with the actual tail. Its value
is not tight selection; its value is a stronger sufficient convergence/safety
certificate when raw row-substochasticity fails.

## 32. GPT Advice 1 Paper-Facing Alignment

GPT advice 1 was mostly right: the next bottleneck was not another theorem, but
artifact alignment.

Implemented:

```text
top-level README
requirements.txt
scripts/reproduce_proofs.sh
scripts/reproduce_certificates.sh
scripts/reproduce_core.sh
experiments/run_submission_main_table.py
experiments/output/submission_main_table/summary.md
```

The main table now states the intended paper hierarchy explicitly:

```text
exact Green:
  reference operator

certified adaptive Green + top-set exact fallback:
  main implementation

fixed-K Green:
  ablation

weighted spectral / conditioned rational certificates:
  theorem and reproducibility appendix
```

The current certification summary is:

```text
exact top-1 matches: 20 / 20
interval-certified top-1 decisions: 4 / 20
top-set exact fallback rows: 16 / 20
final certified decisions: 20 / 20
```

The submission table also makes the uncomfortable but useful fact visible:
fallback can dominate single-task corridor timing because all corridor
candidates are exact ties. That is not a contradiction; it clarifies the story.
The core evidence becomes:

```text
planning compression:
  thousands-x backup/time reduction on long corridors

certified decision:
  final top choice certified by interval separation or top-set exact fallback

amortized value:
  exact fallback/kernel costs need multi-task reuse or tighter tie handling
```

Solver-validity output is now paper-readable as an aggregate table. On the
compact oracle suite:

```text
actual_refine beam:
  boundary_match_rate = 1.0 for beam widths 1, 2, 4

operator-only beam:
  boundary_match_rate improves 0.0 -> 0.6667 -> 1.0
```

No new external references/repos were introduced by GPT advice 1; reference
manifests were recorded under the ignored `reference/` directory.

## 33. GPT Answer 14 Tie-Aware Certificate

GPT answer 14 made the right distinction:

```text
corridor slowdown:
  tie / uniqueness-certification overhead

maze endpoint slowdown:
  real curvature / interval uncertainty fallback
```

I implemented tie-aware certification before running a larger group-constrained
adaptive table.

Code/output changes:

```text
experiments/run_adaptive_green_certification.py
experiments/run_submission_main_table.py
experiments/output/adaptive_green_certification/summary.md
experiments/output/submission_main_table/summary.md
proof/RDOperatorReal.lean
```

The certification summary now separates:

```text
unique interval top-1
epsilon-optimal interval certificate
exact tie-set canonical certificate
curvature exact fallback
```

Current counts:

```text
exact top-1 matches: 20 / 20
interval-certified unique top-1: 4 / 20
unique-top fallback rows: 16 / 20
tie-aware final certified decisions: 20 / 20
tie fallback rows under unique-top certification: 14 / 20
curvature fallback rows after tie-aware certification: 2 / 20
```

The submission table now reports both runtime stories:

```text
total_speedup_unique_top_fallback
total_speedup_tie_aware
unique_top_break_even_tasks
amortization_break_even_tasks
```

Key result:

```text
best unique-top total speedup = 3.698x
best tie-aware total speedup = 10.68x
```

Interpretation for the paper:

```text
Do not claim:
  certified adaptive Green always wins one-shot total runtime

Claim:
  it compresses planning strongly; tie-heavy uniqueness failures can be
  certified as epsilon/top-set decisions; true curvature fallback remains
  explicit and amortized by repeated planning queries.
```

Lean now includes two simple order theorems:

```text
epsilon_interval_certified_optimality
exact_tie_set_representative_optimal
```

These sit beside the existing interval top-choice and top-set exact fallback
theorems.

## 34. Larger Group-Constrained Adaptive Table

GPT answer 14 said this was P1 rather than the immediate blocker, but it is now
implemented too.

New script/output:

```text
experiments/run_group_constrained_adaptive_table.py
experiments/output/group_constrained_adaptive_large/summary.md
```

Suite:

```text
maps:
  open_room_12
  four_rooms_11
  maze_13

slips:
  0.0
  0.05

methods:
  endpoints
  group_constrained

first-hit kernels:
  adaptive Green, tail_tol = 1e-6
```

Current result:

```text
endpoint boundaries:
  feasible rows = 0 / 6
  best total speedup = 4.281x

group-constrained boundaries:
  feasible rows = 6 / 6
  best planning speedup = 232.2x
  best total speedup = 0.009028x
```

So this table supports a different claim from the speed table:

```text
group constraints buy feasibility / hidden-boundary control,
not cheap one-shot discovery.
```

The discovery cost is still the bottleneck.  This strengthens the paper story
because it separates three axes:

```text
planning compression:
  adaptive graph kernels are fast once B is fixed

certification:
  tie-aware certificates remove artificial uniqueness fallback overhead

group-constrained discovery:
  gives robust feasible boundaries, but currently has expensive upfront search
```

## 35. Discovery Profile, Cache, and Vectorized Frozen Scoring

I added the first profiling pass for the expensive part of discovery:

```text
experiments/run_discovery_profile_cache.py
experiments/output/discovery_profile_cache/summary.md
experiments/run_rd_group_constrained.py
experiments/run_rd_operator_theorem_checks.py
```

What is now instrumented:

```text
probe/context build
Green-kernel evaluation
frozen finite-difference operator scoring
group candidate scoring
beam expansion
probe cache hits/misses
full adaptive candidate recompute
```

Two implementation changes matter:

```text
1. ProbeDeltaCache:
   key = (map, slip, boundary, basis, probe, recipe, edge_weight, lambda, top_fraction)
   value = frozen bits-before and candidate bits-deltas

2. Vectorized scoring:
   operator_marginal_rows now builds an edge-by-candidate probability matrix and
   computes linear / finite-difference bits / gradient scores with NumPy ops.
   score_candidates also evaluates group risks in a matrix pass.
```

Current one-step profile:

```text
current frozen operator vs full adaptive candidate recompute:
  median speedup ≈ 5.3x

cached repeat of the same boundary/probe:
  speedup ≈ 3.3e3x to 7.5e3x

group candidate scoring:
  about 2e-4 to 6e-4 seconds in the one-step profile
```

The larger group-constrained table now includes profile columns. Its main
diagnostic is blunt:

```text
group_constrained median selection time ≈ 11.3s
median Green-kernel time ≈ 3.53s
median operator-delta time ≈ 3.57s
median group candidate-score time ≈ 0.0033s
cache hit rate = 0 in the default beam run
```

So the problem is not the outer scalar/group scoring loop. The expensive part is
repeated Green/operator probe evaluation for new boundary states. The cache is
valuable for repeated boundary/probe queries and multitask reuse, but the default
beam mostly visits fresh boundaries; this means true incremental Green updates
or a learned/symbolic surrogate operator are still the right next cost target.

Answer to the direct-cost question:

```text
Directly using the operator is cheap only after the boundary/probe kernel is
available. During discovery, every new candidate boundary still forces new
first-hit Green evaluations, so "operator" does not automatically mean "free".
The paper should distinguish:

  frozen score application: cheap/vectorized
  kernel/probe construction: still expensive
  fixed-B planning: very cheap
```

## 36. Incremental Green Boundary-Insertion Pass

GPT answer 15 recommended making the next main contribution a true
parent-to-child Green update rather than a learned surrogate. I implemented the
first exact check.

New code/output:

```text
experiments/bellman_kron.py
experiments/run_incremental_green_update_check.py
experiments/output/incremental_green_update/summary.md
experiments/output/submission_main_table/incremental_green_update_aggregate.csv
```

Core implementation:

```text
first_hit_green_state(P, terminals)
insert_first_hit_terminal(parent_state, x)
```

The matrix-level update uses:

```text
N' = N_JJ - N_Jx N_xJ / N_xx
H'(i, x) = N(i, x) / N(x, x)
H'(i, c) = H(i, c) - H'(i, x) H(x, c)
```

For scoring we also use the cheaper exact scalar form:

```text
h_{B union x}(i)
  = h_B(i) - Pr_i[tau_x < tau_C] * h_B(x)
```

where `h_B(x)` is the old hidden mass from the newly inserted state to the old
hidden terminals. This is the useful runtime path: it gives the exact score
without materializing a full child Green matrix for every candidate.

Current check on `open_room_7`, `four_rooms_7`, `maze_9`, slip `0` and `0.05`:

```text
boundary_insertion_score_update:
  selected_state_match_rate = 1.0
  max hidden error vs direct child recompute ≈ 8.9e-16
  median speedup vs full child recompute ≈ 6.1x
  max speedup ≈ 7.4x
  median parent_update_rate = 1.0

boundary_insertion_update full matrix:
  kernel error ≈ 1e-15
  slower in Python because it materializes every child matrix

current_frozen_operator:
  selected_state_match_rate = 0.333
```

This is an important correction to the previous profile:

```text
memo cache:
  only helps repeated identical boundary/probe queries

incremental insertion:
  helps fresh child boundaries because every child is updated from its parent
```

The next implementation step is to thread `boundary_insertion_score_update`
through the group-constrained beam, replacing child probe recomputation where
the fixed-policy/fixed-residual semantics match the theorem assumptions. The
frontier-pruning layer should come after that, because now pruning can reduce
the number of parent-to-child updates rather than just cheap candidate rows.

## 37. Incremental Green Wired into Group-Constrained Beam

The diagnostic-only score update is now connected to the actual
group-constrained boundary selector.

New controls:

```text
experiments/run_rd_group_constrained.py --delta-backend {operator,insertion_score}
experiments/run_group_constrained_adaptive_table.py methods:
  group_constrained              # robust operator backend
  group_constrained_incremental  # insertion_score backend
```

The larger adaptive table now includes both backends:

```text
experiments/output/group_constrained_adaptive_large/summary.md
experiments/output/submission_main_table/summary.md
```

Current larger-table summary:

```text
group_constrained / operator:
  feasible rows = 6 / 6
  median selection time ≈ 10.4s
  best total speedup ≈ 0.0082x

group_constrained_incremental / insertion_score:
  feasible rows = 6 / 6
  median selection time ≈ 5.75s
  best total speedup ≈ 0.0275x
  median probe Green time is now comparable to operator because it also
  computes production occupancy weights; candidate score time remains tiny.
```

Interpretation:

```text
The incremental backend is now a real solver path, not just a diagnostic.
The deterministic open_room_12 miss was a semantics mismatch, not a graph
quality failure: the insertion trace used edge-uniform accounting after a
split, while the production operator used occupancy-or-uniform active-edge
weights. The backend now honors those weights when evaluating beam nodes.
```

The semantic diff artifact is:

```text
experiments/run_group_incremental_semantic_diff.py
experiments/output/group_incremental_semantic_diff/summary.md
```

It shows:

```text
operator top-1 at step 0: state 1, exact feasible after graph rewiring
insertion_score top-1 at step 0: state 72, exact feasible after graph rewiring

For boundary [0, 72, 143]:
  weighted topology bits ≈ 9.716
  uniform topology bits ≈ 116.6
```

So active-edge validity and terminal universe were not the main bug. The key
semantic mismatch was occupancy weighting versus uniform fallback. The remaining
scientific issue is whether to make the occupancy-weighted insertion backend the
main runtime path, or keep it as an ablation until a larger scale suite confirms
the added occupancy-weight computation amortizes well.
