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
