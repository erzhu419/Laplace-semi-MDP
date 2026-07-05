# 我：
我又push了下。目前的问题是：如何把“frozen RD operator exactness + adaptive group-constrained beam search”包装成一个严谨贡献，而不是被审稿人说成启发式堆料
# GPT：
我会把它包装成一个**“可证明 operator + 有约束 adaptive solver”**的两层贡献，而不是把二者混在一起说成“整个算法都有 exactness”。

最稳的主张是：

[
\boxed{
\text{Frozen RD Green Operator 是定理；Adaptive Group-Constrained Beam Search 是求解器。}
}
]

换句话说，**理论贡献不是 beam search 本身 exact，而是你给 beam search 提供了一个可证明的 local marginal oracle**。beam search 只是用这个 oracle 在 hard constraints、multi-probe groups、adaptive recompute drift 存在时做有限宽度搜索。

---

## 1. 先把审稿人最可能的攻击点拆掉

审稿人会说“这不就是一堆 heuristic：RD score、group constraints、beam search、held-out probes、adaptive recompute？”

你的回应应该是：

> 不是。我们的方法有两个层级。第一层是一个数学对象：给定 frozen graph-option model，(S_{\rm RD}) 是 constrained RD objective 的精确一步有限差分。第二层是一个求解器：当每次加入 boundary 后重新估计 options、edges、occupancy 和 hard feasibility 时，目标函数发生漂移，因此我们用 group-constrained beam search 作为 adaptive coordinate-search solver，并显式测量 drift、margin stability 和 held-out generalization。

也就是说，不能把 adaptive beam search 说成“继承 exactness”。它不继承。它使用 exact operator 作为 proposal / local oracle。

这个 distinction 很重要，因为你现在的代码已经在做这种区分：`run_rd_operator_theorem_checks.py` 里有 `--with-frozen-recompute`、`--with-actual-recompute`、`--with-recompute-modes` 三种诊断开关，说明你已经把 frozen exactness、actual recompute、recompute drift 拆成了不同实验对象；summary 里也记录了 `with_frozen_recompute: True`、`with_actual_recompute: False`、`with_recompute_modes: False` 的配置。([GitHub][1])

---

## 2. 论文里的贡献应该这样分层

我建议贡献写成四条。

### Contribution 1：Graph-SMDP boundary learning 的 constrained multi-probe RD formulation

你要先把问题从“找一些边界点”变成一个明确优化问题。

令：

[
C_0
]

是固定的 multi-task candidate universe，例如 topology、coverage、spectral、hard semantic boundary 的并集。

当前显式 graph boundary 是：

[
B\subseteq C_0
]

定义 rate：

[
R(B)
====

C_{\rm graph}(B)
+
C_{\rm option}(B)
+
C_{\rm edge}(B)
+
C_{\rm policy}(B)
]

定义多组 probe distortion：

[
D(B)
====

\left(
D_1(B),D_2(B),\dots,D_m(B)
\right)
]

其中每个 (D_g) 可以对应一个 group：task group、probe lens group、map group、slip group、occupancy group、audit-tail group。

然后主目标写成：

[
\boxed{
\min_{B\in\mathcal F}
\quad
J(B)
====

R(B)
+
\lambda
\rho
\left(
D_1(B),\dots,D_m(B)
\right)
}
]

其中：

[
\mathcal F
]

是 hard feasible family，例如：

[
B_{\rm hard}\subseteq B
]

[
|B\cap G_j|\le k_j
]

[
p_{\rm fatal-hidden}(B)=0
]

[
D_{\rm SMDP-hard}(B)\le \epsilon_{\rm hard}
]

(\rho) 可以是 mean、mean+CVaR、smoothmax 或 max。这样 group constraints 就不是后处理，而是 objective/feasibility 的一部分。

这一步非常重要，因为它把“堆料”变成：

[
\boxed{
\text{一个 constrained rate-distortion set optimization problem}
}
]

---

### Contribution 2：Frozen RD Boundary Green Operator 的 exact finite-difference theorem

给定当前 boundary (B)，固定：

[
\theta_B
========

(C_0,O_B,E_B,w_B,R_B)
]

其中 (O_B) 是当前 option policies，(E_B) 是当前 active edge set，(w_B) 是 occupancy / audit weights，(R_B) 是 local rate model。

对每个 edge：

[
e=(b,o)
]

定义 first-hit Green kernel：

[
K_e(x)
======

\Pr_o
\left[
S_{\tau_{C_0}}=x
\mid S_0=b
\right]
]

其中：

[
\tau_{C_0}
==========

\inf{t\ge 1:S_t\in C_0\setminus{b}}
]

线性代数形式是：

[
\boxed{
K_e
===

e_b^\top
(I-P^o_{II})^{-1}P^o_{IC}
}
]

这就是你的 Green operator / harmonic-measure object。

对某个 probe group (g)，定义 hidden mass：

[
h_{g,e}(B)
==========

\sum_{y\in C_g\setminus B}
K_{g,e}(y)
]

bits distortion：

[
D_g(B)
======

\sum_e
w_{g,e}
\phi(h_{g,e}(B))
]

其中：

[
\phi(p)=-\log_2(1-p+\epsilon)
]

加入 candidate (x) 后，group (g) 的 finite-difference gain 是：

[
\Delta_g(x\mid B)
=================

\sum_e
w_{g,e}
\left[
\phi(h_{g,e})
-------------

\phi(h_{g,e}-K_{g,e}(x))
\right]
]

于是 multi-group RD operator 是：

[
\boxed{
S_{\rho}(x\mid B)
=================

\lambda
\left[
\rho(D(B))
----------

\rho(D(B)-\Delta(x))
\right]
-------

c_B(x)
}
]

其中：

[
c_B(x)=R_B(B\cup{x})-R_B(B)
]

然后定理写成：

[
\boxed{
S_{\rho}(x\mid B)
=================

## J_{\theta_B}^{\rm frozen}(B)

J_{\theta_B}^{\rm frozen}(B\cup{x})
}
]

这就是 exactness。

你现在的实验已经支持这个 claim：summary 里多张地图、多步的 `max_fd_minus_frozen` 基本在 (10^{-15}\sim 10^{-12}) 的数值误差范围内，例如 maze、four-rooms、open-room 的 frozen check 都接近 machine precision；这应该成为核心图，而不是附录。([GitHub][2])

---

### Contribution 3：Adaptive recompute drift 和 margin stability

加入 (x) 后，如果你重新构图、重算 option model、重算 SMDP policy、重算 occupancy，那么对象变了：

[
\theta_{B\cup{x}}\ne \theta_B
]

所以 actual adaptive score 是：

[
S_{\rm ad}(x\mid B)
===================

## J_{\theta_B}^{\rm frozen}(B)

J_{\theta_{B\cup{x}}}^{\rm adaptive}(B\cup{x})
]

而 frozen score 是：

[
S_{\rm fr}(x\mid B)
===================

## J_{\theta_B}^{\rm frozen}(B)

J_{\theta_B}^{\rm frozen}(B\cup{x})
]

定义 recompute drift：

[
A(x\mid B)
==========

## S_{\rm ad}(x\mid B)

S_{\rm fr}(x\mid B)
]

再定义：

[
\epsilon_{\rm adapt}
====================

\max_x |A(x\mid B)|
]

如果 frozen top-1 candidate 是 (x_1)，第二名是 (x_2)，并且 margin：

[
m_{\rm fr}
==========

S_{\rm fr}(x_1)-S_{\rm fr}(x_2)
]

满足：

[
\boxed{
m_{\rm fr}>2\epsilon_{\rm adapt}
}
]

则：

[
x_1
]

也是 adaptive score 下的 top-1。

这就是一个干净的 stability theorem。你的代码里已经在计算 `fd_margin`、`epsilon_adapt` 和 `stability_condition = fd_margin > 2.0 * epsilon_adapt`，这正好可以对应这个定理。([GitHub][1])

这条 theorem 的作用不是证明 adaptive beam search 总是最优，而是证明：

> 当 recompute drift 小于 frozen margin 时，frozen RD operator 的选择在 adaptive recompute 下稳定。

这非常重要，因为它把 mismatch 从“反例”变成了“可测量的 drift”。

---

### Contribution 4：Adaptive Group-Constrained Beam Search as a solver, not as the theorem

这里要非常小心。

beam search 本身不要包装成“理论核心”。它应该被包装成：

[
\boxed{
\text{a constrained adaptive search procedure driven by an exact frozen marginal oracle}
}
]

也就是：

1. 当前 beam 里每个 partial boundary set (B_t) 先重新估计 graph-option model；
2. 在 frozen (\theta_{B_t}) 下用 (S_{\rm RD}) 给所有 candidate 打分；
3. 只扩展满足 group constraints / hard constraints 的 candidates；
4. 对扩展后的 (B_t\cup{x}) 做 actual recompute；
5. 按 adaptive objective、held-out probe、hard feasibility 或 robust group score 剪枝；
6. 保留 top-(W) beams。

这不是“启发式堆料”，而是一个标准模式：

[
\boxed{
\text{local exact oracle}
+
\text{adaptive relinearization}
+
\text{constrained finite-width search}
}
]

你可以把它类比为 constrained decoding：Grid Beam Search 的贡献不是让基础模型本身满足约束，而是在 beam search 过程中把约束状态纳入搜索；Hokamp 和 Liu 的 GBS 也是把 beam search 扩展到必须包含预设词法约束的序列生成场景，而不需要改模型参数。([ACL Anthology][3])

你的版本类似，但对象不是 token sequence，而是 boundary-set sequence：

[
B_0\rightarrow B_1\rightarrow \cdots \rightarrow B_T
]

constraints 不是 lexical constraints，而是 group feasibility / hard SMDP admissibility / probe budgets。

---

## 3. 关键：不要说“beam search 有 exact guarantee”，而说“三种 guarantee”

我建议在论文里明确分三种 guarantee。

### Guarantee A：Frozen exactness

这是最强、最核心的：

[
S_{\rm RD}
==========

-\Delta J_{\theta_B}^{\rm frozen}
]

这个是 theorem。

### Guarantee B：Margin stability under bounded adaptive drift

这是第二强：

[
m_{\rm fr}>2\epsilon_{\rm adapt}
\Rightarrow
\text{top-1 stable under adaptive recompute}
]

这个也是 theorem。

### Guarantee C：Beam search coverage condition

这个可以写成条件性 proposition：

令 adaptive optimal path 的每一步选择为：

[
x_t^*
]

如果在每一步，(x_t^*) 的 frozen score rank 不超过 beam expansion budget (q)，并且对应 prefix 没有被 group constraints 剪掉，那么宽度 (W\ge q) 的 beam 会保留该 optimal prefix。

或者更严格：

如果对每个 depth (t)：

[
S_{\rm fr}(x_t^*)\ge S_{\rm fr}^{(q)}
]

其中 (S_{\rm fr}^{(q)}) 是第 (q) 名 frozen score，并且 adaptive pruning score 的 drift 小于 beam margin，那么 beam 保留 optimal prefix。

这类 statement 是有限搜索树的 coverage guarantee。它不会很惊艳，但很严谨。你不要试图把它说成全局最优 guarantee。

---

## 4. group constraints 怎么避免“人为调参”的质疑？

group constraints 应该不是“为了结果好临时加的过滤器”，而是来自 problem definition：

[
\mathcal F
==========

\left{
B\subseteq C_0:
B_{\rm hard}\subseteq B,;
|B\cap G_j|\le k_j,;
D_j(B)\le \epsilon_j
\right}
]

你需要把 group 分成三类：

**Hard admissibility groups**：比如 terminal、goal、reward discontinuity、fatal hidden-cross。违反就 invalid。

**Probe robustness groups**：比如 junction、turn-articulation、bottleneck、spectral、coverage、held-out residual lens。它们进入 (D_g) 或 CVaR，不直接 invalid。

**Budget / diversity groups**：比如每个 room、每个 topological region、每个 candidate family 至多/至少选多少。这些约束防止 beam 一直选同一类点。

这样 group constraints 是在定义 feasible hypothesis class，而不是后验筛选。

如果你希望更有理论味道，可以说：当 group budgets 是 partition matroid / cardinality constraints，并且 distortion reduction 是 monotone submodular 时，greedy-style algorithms 可以连接到经典 submodular maximization 理论；Nemhauser、Wolsey、Fisher 的经典结果就是这条线的基础。([ResearchGate][4])

但要注意：如果你用 max/CVaR、actual recompute、dynamic option retraining，严格 submodularity 不一定保留。那时就不要硬 claim approximation ratio；只 claim constrained adaptive solver + diagnostic guarantees。

---

## 5. 论文主线可以这样写

### 章节 1：Problem

“我们不是在学一个最小图，而是在学一个 graph-option abstraction，使它在多组 probes / tasks 下达到 low distortion，同时控制 graph-option rate。”

公式：

[
\min_{B\in\mathcal F}
R(B)
+
\lambda
\rho(D_1(B),\dots,D_m(B))
]

### 章节 2：Frozen RD Green Operator

先固定 (\theta_B)，推导：

[
K_e=e_b^\top(I-P^o_{II})^{-1}P^o_{IC}
]

[
S_\rho(x)=\lambda[\rho(D)-\rho(D-\Delta(x))]-c_x
]

定理：

[
S_\rho(x)=J_{\theta_B}(B)-J_{\theta_B}(B\cup{x})
]

### 章节 3：Adaptive drift

定义：

[
A(x)=S_{\rm ad}(x)-S_{\rm fr}(x)
]

定理：

[
m_{\rm fr}>2|A|_\infty
\Rightarrow
\text{top choice stable}
]

并解释：actual recompute mismatch 不是 theorem failure，而是 drift 超过 margin。

### 章节 4：Adaptive Group-Constrained Beam Search

给 algorithm box：

```
Input: initial B0, candidate universe C0, option library O0,
       group constraints F, probe groups G, beam width W.

Beam = {B0}

for t = 1..T:
    NewBeam = {}
    for B in Beam:
        Recompute graph-option model theta_B
        Compute frozen RD Green scores S_theta_B(x)
        for x in TopCandidates(B, S_theta_B):
            if B ∪ {x} satisfies group/hard constraints:
                B' = B ∪ {x}
                Recompute adaptive objective J_ad(B')
                Add B' to NewBeam
    Beam = top-W feasible elements of NewBeam
return best feasible B
```

然后明确写：

> The beam search is not claimed to be exact. Its role is to search the adaptive objective using a provably exact local oracle and explicit feasibility constraints.

---

## 6. 你现在已有的证据应该怎么放

你已经有几类非常有价值的证据，不要埋没。

### A. Frozen exactness

summary 里 `max_fd_minus_frozen` 基本是 (10^{-15}) 到 (10^{-12})，这应该是主表第一行。([GitHub][2])

图：scatter plot

[
x=S_{\rm FD},\quad y=S_{\rm frozen-recompute}
]

应该完全在 (y=x) 线上。

### B. Gradient 是近似，不是主方法

summary 里 maze step 0 的 `mean_grad_error` 很大，但 finite-difference 仍然 exact；这说明你应该主推 FD operator，而不是 gradient operator。([GitHub][2])

图：hidden mass vs gradient error。
结论：gradient 适合 amortized / differentiable / large-scale approximation；FD 是理论主算子。

### C. Truncated Green convergence

summary 里 truncation 随 (K) 增加明显收敛：例如 four_rooms 到 (K=16/32) top1 match 到 1，open_room 到 (K=8/16/32) top1 match 到 1，maze 的 mean absolute error 到 (K=16/32) 已经接近零。([GitHub][2])

这张图非常重要，因为它证明 (S_{\rm RD}) 不是 arbitrary score，而是可以由有限步 propagation 逼近的 Green operator。

### D. Baseline ranking

代码里已经比较 raw hidden、random、spectral、betweenness、value-gradient、degree 等 baseline score；summary 里也输出了这些 baseline 是否 match FD top choice。([GitHub][1])

这可以回答“是不是随便一个 heuristic 都行？”
你应该报告：

[
\operatorname{KendallTau}(S_{\rm baseline},S_{\rm FD})
]

[
\text{top-1 match}
]

[
\text{adaptive regret}
]

### E. Runtime

summary 里已经有 base eval、FD/gradient operator score 的 runtime，以及 truncated Green runtime。([GitHub][2])

要补一张：

[
\text{full adaptive recompute over all candidates}
\quad\text{vs}\quad
S_{\rm FD}
\quad\text{vs}\quad
S_{\rm truncated}^{(K)}
]

这能支撑“operator 减少成本”的 claim。

---

## 7. 还缺的关键实验

为了不被说成启发式堆料，我建议补 5 个实验。

### 1. Beam width ablation

比较：

[
W=1,2,4,8,\text{exhaustive small}
]

指标：

[
J_{\rm adaptive}(B)
]

[
D_{\rm heldout}
]

[
R(B)
]

[
\text{constraint violations}
]

如果 (W=1) 是 greedy，(W>1) 明显减少 adaptive regret，而且小图上接近 exhaustive，这就能说明 beam search 的作用不是任意调参，而是在处理 adaptive recompute nonlocality。

### 2. Group constraints ablation

比较：

* no group constraints；
* hard-only；
* hard + diversity；
* hard + multi-probe CVaR；
* hard + multi-probe CVaR + beam。

报告：

[
D_{\rm train}
,\quad
D_{\rm heldout}
,\quad
D_{\rm worst-group}
,\quad
R
]

如果 group constraints 真的有用，它应该降低 worst-group / held-out probe residual，而不是只降低 train objective。

### 3. Actual recompute drift decomposition

你代码已经有 `rate_only_score`、`occupancy_only_score`、`edge_only_score`、`edge_option_uniform_score`、`actual_recompute_score` 的 recompute mode 设计。([GitHub][1])

用它做一张 decomposition 图：

[
A=A_{\rm rate}+A_{\rm occupancy}+A_{\rm edge}+A_{\rm option}+A_{\rm residual}
]

这会非常有说服力，因为你能说清楚 mismatch 来自哪里。

### 4. Held-out probe generalization

train probe groups 和 held-out probe groups 分开：

[
\mathcal G_{\rm train}\cap\mathcal G_{\rm test}=\varnothing
]

比较 single-probe RD、multi-probe mean、multi-probe CVaR、minimax。

这可以证明 group-constrained beam search 不是只服务当前 residual lens。

### 5. Exhaustive small-map oracle

在很小的 grid 上枚举所有：

[
|B|\le k
]

得到 true best adaptive set。然后比较：

* FD greedy；
* group-constrained beam；
* raw hidden；
* spectral；
* random；
* exhaustive optimum。

这张表最能堵住“heuristic 堆料”的批评。

---

## 8. 最危险的 overclaim

避免这些表述：

> Our adaptive beam search is exact.

不要说。

> The RD operator always predicts the best recomputed split.

不要说。

> Group constraints are theoretically optimal.

不要说。

> The full algorithm has submodular approximation guarantees.

除非你严格限制为 frozen、mean/sum distortion、fixed options、modular rate、cardinality/partition matroid，否则不要说。

更稳的表述是：

> The exactness theorem applies to the frozen RD objective. Adaptive recomputation introduces objective drift. We therefore use the operator as a local oracle inside a constrained adaptive beam search, and we explicitly measure drift, margin stability, beam regret, and held-out group generalization.

---

## 9. 可以放在摘要里的版本

我会这样写：

> We formulate graph-option abstraction as a constrained multi-probe rate-distortion problem over boundary sets. For a fixed graph-option model, we derive an RD Boundary Green Operator whose score is exactly the one-step finite difference of the frozen RD objective. The operator is computed by an option-induced first-hit Green kernel, avoiding exhaustive candidate recomputation. Since adding a boundary can change the option model, edge set, and occupancy weights, we introduce adaptive recomputation drift and a margin-stability criterion. We then use the operator as a local oracle inside an adaptive group-constrained beam search, which enforces hard admissibility and robust probe constraints while re-estimating the SMDP after each split.

中文就是：

> 我们先证明 frozen local operator 是精确的，再把 adaptive beam search 定义成一个使用该 operator 的 constrained solver，并把它的非精确性通过 drift / margin / held-out diagnostics 显式暴露出来。

---

## 10. 最终包装成一句话

你的贡献不是“一个复杂启发式算法”。

更准确的包装是：

[
\boxed{
\text{A provably exact frozen RD marginal oracle}
+
\text{a drift-aware group-constrained adaptive search procedure}
}
]

其中：

[
\boxed{
S_{\rm RD}
\text{ 是数学贡献}
}
]

[
\boxed{
\text{adaptive group-constrained beam search 是系统求解器}
}
]

[
\boxed{
\text{drift、margin、held-out probes 是防止 overclaim 的审计层}
}
]

只要你按这个结构写，审稿人最多会说 adaptive solver 没有全局最优保证，但很难说它只是 heuristic 堆料，因为核心 operator 有 exact finite-difference theorem，adaptive mismatch 有 drift decomposition，beam search 有约束化搜索语义，实验有 frozen identity、truncation convergence、baseline ranking、beam-width ablation 和 held-out group generalization。

[1]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/run_rd_operator_theorem_checks.py?plain=1 "Laplace-semi-MDP/experiments/run_rd_operator_theorem_checks.py at main · erzhu419/Laplace-semi-MDP · GitHub"
[2]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/output/rd_operator_theorem_checks/summary.md?plain=1 "Laplace-semi-MDP/experiments/output/rd_operator_theorem_checks/summary.md at main · erzhu419/Laplace-semi-MDP · GitHub"
[3]: https://aclanthology.org/P17-1141/?utm_source=chatgpt.com "Lexically Constrained Decoding for Sequence Generation ..."
[4]: https://www.researchgate.net/publication/242914003_An_Analysis_of_Approximations_for_Maximizing_Submodular_Set_Functions-I?utm_source=chatgpt.com "An Analysis of Approximations for Maximizing Submodular ..."
