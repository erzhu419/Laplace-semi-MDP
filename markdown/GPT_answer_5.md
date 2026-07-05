# 我：
proposal-only eigen/coverage 能进一步降低 hidden/edge， 但 DL 更高。这个 improvement 应该被 MDL 接受吗？ MDL 里的 edge_cost_weight / hidden exposure weight 应该怎么校准， 才能不是人为偏向当前 struct_mdl_e05？

# GPT 直接结论：

**proposal-only eigen/coverage 不应该因为 hidden/edge 下降就自动被 MDL 接受。**
如果它只是通过增加 proposal nodes / valid edges 把分母变大，使 `struct_hidden_distinct_per_edge` 下降，但 **total structural exposure、option library size、edge/model cost、DL 都上升**，严格 MDL 应该拒绝。它可以作为 Pareto frontier 上的“更结构化但更贵”的点报告，而不是被主 MDL objective 选中。

我看到你现在的 `proposal_only_option_comparison` 里，maze 上就是这个现象：`learned_struct_mdl_e05` 在 deterministic maze 是 `n_boundary=11, n_edges_valid=110, struct_hidden_distinct_valid_total=55, per_edge=0.5, DL=545.5`；proposal-eigen 变成 `13,156,63,0.4038,674.9`；proposal-coverage 变成 `14,182,67,0.3681,740.7`。也就是说 **per-edge exposure 降了，但 total exposure 和 DL 都升了**。slip=0.05 的 maze 也类似：per-edge 从 `0.1376` 降到 `0.1134/0.1031`，但 total exposure 从 `25.04` 升到 `27.22/28.04`，DL 从 `687.7` 升到 `824.7/893.5`。([GitHub][1])

---

## 1. hidden/edge 只能做诊断，不能做 MDL 的主收益

`hidden/edge` 的问题是：

[
\text{hidden_per_edge}
======================

\frac{\text{total hidden exposure}}{#\text{valid edges}}
]

当 proposal eigen/coverage 增加 boundary 数量时，valid pair options 通常按 (O(|B|^2)) 增长。这样即使总 hidden exposure 没下降，甚至上升，per-edge 也会下降。

所以 MDL 里不应该用：

[
\Delta \left(\frac{H}{|E|}\right)
]

作为接受 split 的依据。

应该用：

[
\Delta H_{\text{total}}
]

或者更好：

[
\Delta H_{\text{occ}}
=====================

\sum_{b,o}
d_{\bar\pi}(b)\bar\pi(o|b)
C_{\text{struct}}(b,o)
]

其中 (d_{\bar\pi}) 是 abstract policy occupancy。
如果你在评估整个 option library 的复杂度，用 total；如果你在评估某个 task distribution 下的实际使用复杂度，用 occupancy-weighted。**per-edge 只保留为诊断列。**

---

## 2. MDL 接受条件应该是“总码长下降”，不是某个指标下降

MDL 的核心不是“某个 residual 变小就接受”，而是：

[
\boxed{
L(M,D)
======

L(M)
+
L(D\mid M)
}
]

模型更复杂可以被接受，但必须让数据描述长度下降得更多。MDL 文献本身就是把 model class / parameters / data-given-model 合起来比较；Barron、Rissanen、Yu 的综述把 MDL 解释为选择能给数据最短编码的模型，Grünwald 也把它表述为“regularities compress data”。([Massachusetts Institute of Technology][2])

所以对 proposal-eigen/coverage 的接受规则应该写成：

[
\Delta L
========

\Delta L_{\text{boundary}}
+
\Delta L_{\text{edge}}
+
\Delta L_{\text{option}}
+
\Delta L_{\text{params}}
+
\Delta L_{\text{struct}}
+
\Delta L_{\text{rollout}}
]

接受当且仅当：

[
\boxed{
\Delta L < 0
}
]

并且 hard constraints 满足：

[
\text{planning gap}\le \epsilon_{\text{plan}},
\quad
\text{held-out residual}\le \epsilon_{\text{res}},
\quad
\text{hard hidden-cross}\le \epsilon_{\text{hidden}}
]

在你现在的实验结果里，如果 proposal-only 只是降低 per-edge hidden，但增加 total exposure 和 DL，它不该被接受。它最多说明：**eigen/coverage proposal 可以让 graph 更密、更平均，但不是更短的解释。**

---

## 3. 当前 `edge_cost_weight=0.5` 的问题：它是 penalty，不是 code length

你现在的 `choose_mdl_struct_split` 是：

[
\text{benefit}(h)
=================

\sum_e
w_{\text{exposure}}
\cdot
\text{edge_exposure}(e)
\cdot
\text{score}_h(e)
]

[
\text{split_cost}
=================

w_{\text{node}}\log_2 |S|
+
w_{\text{edge}}\cdot 2|B|
]

代码里对应的是 `edge_exposure * score` 聚合 benefit，然后用 `log2(n_states) + edge_cost_weight * 2*n_boundary` 当 split cost。([GitHub][3]) 这作为启发式是可以的，但作为 MDL claim 不够，因为 `edge_cost_weight=0.5` 没有真实编码解释。你在 graph baseline recipes 里也确实是手设了 `learned_struct_mdl_e05` 的 `struct_mdl_edge_cost_weight=0.5`，另一个版本是 `e1=1.0`，proposal-eigen/coverage 也沿用了 `0.5`。([GitHub][4])

更干净的做法是把这些 weight 替换成真正的 bits。

---

## 4. node cost：用 enumerative code，而不是固定 (\log_2 |S|)

如果 start/goal 固定，设：

[
N'=|S|-|B_{\text{fixed}}|
]

[
k=|B|-|B_{\text{fixed}}|
]

那么 boundary set 的编码长度可以是：

[
\boxed{
L_B
===

\log_2 {N' \choose k}
+
L_{\mathbb N}(k)
}
]

加一个 node 的真实增量是：

[
\Delta L_B
==========

\log_2
\frac{
{N' \choose k+1}
}{
{N' \choose k}
}
=

\log_2
\frac{N'-k}{k+1}
]

这比固定 (\log_2 |S|) 更合理：当已经选了很多 boundary 时，再加一个 node 的 combinatorial cost 会变化。

如果使用 proposal set (P)，则可以写成：

[
L_B(P)
======

L(P)
+
\log_2 {|P|-|B_{\text{fixed}}| \choose k}
+
L_{\mathbb N}(k)
]

其中：

[
L(P)
====

\log_2 |\mathcal P|
]

如果你允许在 `candidate`, `residual`, `eigen_extrema_12`, `coverage_12` 等 proposal family 之间选择，就要支付 family index 的码长。你的代码里 `proposal_kind` 已经和 `candidate_kind` 分开，`proposal_kind` 可以是 `candidate`、`residual` 或其他 selector；同时 `candidate_boundary_states` 也支持 `eigen_extrema_*`、`coverage_*`、`articulation_eigen_extrema_*`、`turn_coverage_*` 等 family。([GitHub][3])

这能自然解决“proposal-only eigen/coverage 是不是作弊”：
如果 eigen/coverage 只是给出候选，不改变最终 graph，额外 cost 是常数或很小；如果它让你选择更多节点，就要为这些节点付码长；如果你是在多种 proposal family 里挑最好的，还要付 family-selection cost。

---

## 5. edge cost：不要手调，用 graph encoding 或 option-library encoding

你有两种语义，选一种，不要混用。

### 语义 A：edge 是显式存储的 abstract graph

设：

[
K=|B|,
\quad
M=K(K-1)
]

possible directed edges 有 (M) 条，实际 valid edges 有 (m) 条，则：

[
\boxed{
L_E
===

\log_2 {M \choose m}
}
]

加一个 node 后，重新算：

[
\Delta L_E
==========

L_E(B\cup{h})-L_E(B)
]

这会自然惩罚 proposal-only eigen/coverage 带来的 edge explosion。

### 语义 B：edge 不单独存，因为所有 pair options 都自动生成

你现在 first-boundary targeted 更像这个语义：每个 boundary pair 都会有 pair option 记录，metadata 里也有 `option_pair_count` 和 `n_edges_valid`，`description_length_proxy` 里已经把 `n_boundary`、`n_edges_valid/n_boundary`、`n_pair_options`、target policy complexity、soft cost、model residual 加在一起。([GitHub][3])

如果所有 pair options 是由 deterministic algorithm 自动生成，那么 edge identity 不一定需要编码；真正要编码的是：

[
L_{\text{option-interface}}
+
L_{\text{option-policy}}
+
L_{\text{edge-model-params}}
]

也就是说，`edge_cost_weight * 2|B|` 应该被替换成：

[
\Delta L_{\text{pair-options}}
==============================

## L_{\text{option}}(B\cup{h})

L_{\text{option}}(B)
]

在 tabular 实验里，可以近似成：

[
L_{\text{option}}
=================

c_{\text{target}}\cdot |B|
+
c_{\text{pair}}\cdot |B|(|B|-1)
+
c_{\pi}\cdot \text{policy_TV}
+
c_{\text{region}}\cdot \text{policy_regions}
]

但 (c_{\pi},c_{\text{region}}) 也最好最终变成真实 code，比如“policy table 变化点”的编码长度，而不是固定 0.2/0.5。你当前 DL proxy 里 `0.20 * target_policy_tv_total + 0.50 * target_policy_regions_total` 也是启发式权重。([GitHub][3])

---

## 6. hidden exposure weight：最好设成 1，因为它已经是 bits

你已经有：

[
\tilde p
========

\frac{p_{\text{hidden}}-p_{\text{ref}}}{1-p_{\text{ref}}}
]

[
C_{\text{struct}}
=================

-\log_2(1-\tilde p+\epsilon)
]

代码里 `normalize_structural_prob` 和 `structural_bits` 正是这个形式。([GitHub][3])

所以如果你把 structural exposure 当成 data codelength，那么：

[
\boxed{
\text{struct_mdl_exposure_bit_weight}=1
}
]

不需要再调。

真正要校准的是 (p_{\text{ref}})，不是 exposure weight。
目前我在公开代码片段里看到 `struct_reference_prob` 初始化为 0，并直接传给 `normalize_structural_prob`；没有看到它从 local reference distribution 中估出来。([GitHub][3]) 这意味着当前 `struct_hidden_bits` 基本等价于：

[
-\log_2(1-p_{\text{hidden}})
]

可以先这样用，但如果要避免 magic number，下一步应该让：

[
p_{\text{ref}}
==============

Q_{0.95}
\left(
p_{\text{hidden}}(e)
:
e\in E_{\text{legal-local-reference}}
\right)
]

也就是用合法 local reference edges 的 95% 分位作为 calibration upper bound。这样 `struct_hidden_bits=0` 的含义是：

> 这个 edge 的 hidden exposure 不比合法 local edge 更坏。

这比手设 `struct_mdl_e05` 更不偏。

---

## 7. 对 eigen/coverage 的接受，建议用 break-even analysis

对任意 proposal 方法 (M_1) 和 baseline (M_0)，计算：

[
\Delta C
========

L_{\text{boundary}}(M_1)
+
L_{\text{edge}}(M_1)
+
L_{\text{option}}(M_1)
----------------------

## L_{\text{boundary}}(M_0)

## L_{\text{edge}}(M_0)

L_{\text{option}}(M_0)
]

[
\Delta S
========

## L_{\text{struct}}(M_1)

L_{\text{struct}}(M_0)
]

如果 (M_1) 真降低 structural exposure，则：

[
\Delta S<0
]

接受条件是：

[
\Delta C+\Delta S<0
]

如果你仍然想保留一个 scalar hidden exposure multiplier (\lambda)，不要直接选 (\lambda=1) 或调到某个方法好看，而是报告 break-even：

[
\boxed{
\lambda^*
=========

\frac{\Delta C}{-\Delta S}
}
]

解释：

* (\lambda^*<1)：即使保守地计 structural bits，也值得接受；
* (\lambda^*\approx 1)：边界情况；
* (\lambda^*\gg 1)：只有极度重视 hidden exposure 时才接受，说明 proposal improvement 很贵；
* (\Delta S\ge 0)：structural exposure 总量没下降，直接拒绝。

对你现在 summary 里的 maze proposal-only，按 total exposure 看 (\Delta S) 甚至不是负的，所以不应该接受；per-edge 下降不算。

---

## 8. 更重要：把“best-of-many proposal”搜索成本计入 MDL

proposal eigen/coverage 还引入一个 subtle bias：**候选越多，越容易找到一个看似有 gain 的 split**。

你现在 `struct_distinct_scores` 会在 `residual_hidden_probs` 和 `proposal_boundary_set - boundary_set - {src}` 的 union 上打分；也就是说 proposal set 越大，搜索空间越大。([GitHub][3])

MDL 里要为“我从这么多候选里选了这个 state”付费：

[
L_{\text{choose-split}}
=======================

\log_2 |P\setminus B|
]

如果还有多种 proposal family：

[
L_{\text{proposal-family}}
==========================

\log_2 |\mathcal P|
]

如果你按这个写，eigen/coverage 不会被人为打压，也不会被免费奖励。它们只有在提供了**更短编码的候选集合**时才会赢。

---

## 9. 最推荐的替换：exact ΔMDL split，而不是 approximate benefit

当前 `choose_mdl_struct_split` 用：

[
\text{benefit}_h
================

\sum_e
\text{edge_exposure}*e
\cdot
\text{score}*{e,h}
]

这是一个 proxy。更稳的版本是对 top-k candidate 直接重算：

[
\Delta L(h)
===========

## L(B\cup{h})

L(B)
]

然后选：

[
h^*
===

\arg\min_h \Delta L(h)
]

接受当：

[
\Delta L(h^*)<0
]

小 gridworld 完全可以这么做，计算量不大。这样你不需要问 `edge_cost_weight` 到底设多少，因为每一项都拆成 bits 以后可以直接相加。

伪代码：

```python
def mdl_bits(row, edge_rows, code_cfg):
    return (
        boundary_bits(row, code_cfg)
        + edge_bits(row, code_cfg)
        + option_policy_bits(row, code_cfg)
        + option_interface_bits(row, code_cfg)
        + struct_exposure_bits(edge_rows, weighting="library")   # or occupancy
        + rollout_residual_bits(edge_rows, code_cfg)
        + proposal_family_bits(row, code_cfg)
    )

def choose_exact_mdl_split(B, proposal_states):
    base_row, base_edges = evaluate_boundary(B)
    L0 = mdl_bits(base_row, base_edges, code_cfg)

    best = None
    for h in proposal_states - set(B):
        row_h, edges_h = evaluate_boundary(sorted(set(B) | {h}))
        Lh = mdl_bits(row_h, edges_h, code_cfg)
        gain = L0 - Lh
        if best is None or gain > best.gain:
            best = Candidate(h=h, gain=gain, L=Lh)

    return best.h if best.gain > 0 else None
```

这会比现在的 `edge_exposure * score - split_cost` 更接近真正 MDL。

---

## 10. 最后给你的两个问题的明确答案

### Q1：proposal-only eigen/coverage 降低 hidden/edge，但 DL 更高，应不应该被 MDL 接受？

**不应该，除非它降低的是 total / occupancy-weighted structural bits，并且降幅超过新增 graph/edge/option cost。**

在你现在公开 summary 里，maze 上它主要降低的是 `struct_hidden_distinct_per_edge`，但 `struct_hidden_distinct_valid_total` 和 `description_length_proxy` 都上升，所以 strict MDL 应该拒绝。它应被报告为：

> proposal family improves average exposure density but is dominated in total code length.

### Q2：`edge_cost_weight` / hidden exposure weight 怎么校准，才能不是人为偏向 `struct_mdl_e05`？

最干净路线：

1. **删除 `edge_cost_weight`，改成 edge code length**：

[
L_E=\log_2 {K(K-1)\choose m}
]

或者如果 all-pair options 是自动生成的，就把 edge cost 并入：

[
L_{\text{option-interface}}+L_{\text{option-policy}}+L_{\text{edge-model-params}}
]

2. **hidden exposure weight 设成 1**，因为：

[
-\log_2(1-\tilde p)
]

已经是 bits。

3. **校准 (p_{\text{ref}})，而不是调 exposure weight**：

[
p_{\text{ref}}
==============

Q_{0.95}
(
\text{legal local reference hidden exposure}
)
]

4. **为 proposal family 付搜索成本**：

[
L(P)=\log_2 |\mathcal P|+\log_2 |P\setminus B|
]

5. **用 break-even λ 报告敏感性**，而不是调一个让 `e05` 好看的值：

[
\lambda^*
=========

\frac{\Delta C}{-\Delta S}
]

6. **最终主表用 feasible Pareto + exact ΔMDL**，per-edge hidden 只当诊断列。

一句话：**eigen/coverage 可以作为 proposal mechanism，但 MDL 接受的是“更短的完整 graph-option-code”，不是“更低的 hidden/edge ratio”。**

[1]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/output/proposal_only_option_comparison/summary.md "Laplace-semi-MDP/experiments/output/proposal_only_option_comparison/summary.md at main · erzhu419/Laplace-semi-MDP · GitHub"
[2]: https://web.mit.edu/6.433/www/handouts/minimumdescriptionlength.pdf "The Minimum Description Length Principle in Coding and Modeling - Information Theory, IEEE Transactions on"
[3]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/run_first_boundary_targeted.py "Laplace-semi-MDP/experiments/run_first_boundary_targeted.py at main · erzhu419/Laplace-semi-MDP · GitHub"
[4]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/run_graph_baseline_comparison.py "Laplace-semi-MDP/experiments/run_graph_baseline_comparison.py at main · erzhu419/Laplace-semi-MDP · GitHub"
