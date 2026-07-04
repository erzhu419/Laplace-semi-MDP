我的建议可以压成三句话：

**bypass / residual：训练搜索时用 penalty，最终合法性判断用 hard constraint。**
**policy complexity：主指标用 total library MDL，辅以 optimal-occupancy weighted；mean per option 只做诊断。**
**first-candidate-boundary option：先把 (B_0\setminus B) 当 hidden terminal 检测；固定 (B) 评估时判 invalid；在线版本用 hidden terminal 触发 split。**

你现在代码方向已经很接近了：最新 `run_ablation.py` 里已经有 `local_targeted`，并用 `local_horizon` 限制 source-target pair；也已经把 `bypass_cost_total`、`policy_tv_total`、`policy_regions_total` 和 `nonlocal_cost` 放进 `description_length_proxy`。这说明现在的问题不是缺指标，而是要给这些指标确定**语义层级**：哪些是合法性约束，哪些是排序代价。([GitHub][1])

---

## 1. residual / bypass：不要二选一，应该是“搜索 penalty + 接受 hard constraint”

我会把它定义成一个 constrained objective：

[
\min_{B,O,\phi}
C_{\text{graph}}
+
C_{\text{option}}
+
C_{\text{duration}}
+
C_{\text{interface}}
]

subject to:

[
D_{\text{plan}}^{\text{test}}\le \epsilon_{\text{plan}}
]

[
D_{\text{rollout}}^{\text{test}}\le \epsilon_{\text{roll}}
]

[
D_{\text{SMDP}}\le \epsilon_{\text{markov}}
]

[
P_{\text{hidden-cross}}\le \epsilon_{\text{cross}}
]

[
C_{\text{bypass}}\le \epsilon_{\text{bypass}}
]

然后在搜索或 ablation 排序时，可以用 Lagrangian/hinge penalty：

[
J_\lambda
=========

C_{\text{MDL}}
+
\eta D_{\text{plan}}
+
\lambda_r [D_{\text{rollout}}-\epsilon_r]*+^2
+
\lambda_m [D*{\text{SMDP}}-\epsilon_m]*+^2
+
\lambda_b [C*{\text{bypass}}-\epsilon_b]*+^2
+
\lambda_h [P*{\text{hidden-cross}}-\epsilon_h]_+^2
]

也就是说：**优化时是 weighted penalty，论文/实验 claim 时必须过 hard constraint。**

原因是，如果只用 weighted penalty，`endpoints + targeted` 仍然可能通过调小 (\lambda_b) 成为“最优”。但如果只用 hard constraint，又会因为 (B_0) 里的 saliency 噪声而过度 split。所以我建议把 candidate boundary 拆成两层：

[
B_0^{\text{hard}}
=================

\text{degree/junction/turn/reward/terminal/reset/known bottleneck}
]

[
B_0^{\text{soft}}
=================

\text{value-gradient/betweenness/spectral/model-uncertainty/high residual}
]

对 (B_0^{\text{hard}})：cross 就 invalid。
对 (B_0^{\text{soft}})：先 penalty，超过阈值再 split。

你现在的 `critical_saliency` 已经支持 `decision`、`bottleneck`、`betweenness`、`value_gradient`、`transition_entropy`、`combined` 这些候选 critical set；这非常适合做这个 hard/soft 分层。([GitHub][2])

一个具体判据：

[
P_{\text{hidden-cross}}(b,o)
============================

\Pr
\left[
\exists t<\tau:
S_t\in B_0\setminus B
\mid S_0=b,o
\right]
]

[
C_{\text{bypass}}(b,o)
======================

\mathbb E
\left[
\sum_{t=1}^{\tau-1}
\gamma^t c_{\text{crit}}(S_t)
\mid S_0=b,o
\right]
]

固定图评估时：

[
\text{edge valid}
\iff
P_{\text{hidden-cross}}\le \epsilon_h
\quad\text{and}\quad
C_{\text{bypass}}\le \epsilon_b
\quad\text{and}\quad
D_{\text{rollout}}\le \epsilon_r
]

deterministic gridworld 里可以先用：

[
\epsilon_h=0
]

stochastic slip 里用：

[
\epsilon_h \in [0.01,0.05]
]

并且报告 hidden-cross mass，而不是把它吞进 value gap。

你现在 `expected_discounted_interior_cost` 的定义正好就是这个 bypass cost 的 Schur-complement 版本：它用和 reduced reward 同构的线性求解，计算 hitting 下一边界前累计的 interior cost，并明确说明这是为了惩罚 option bypass hidden critical states。([GitHub][2])

---

## 2. policy complexity：主目标用 total library，任务效率用 occupancy-weighted，mean 只做诊断

这三个指标回答的是不同问题。

### total option library complexity

这个回答：

> 这个 agent 为了拥有这些 options，总共存了多少策略复杂度？

它是最接近 MDL / description length 的指标，应该作为主 regularizer：

[
C_{\pi}^{\text{lib}}
====================

\sum_{o\in O}
\left[
c_0
+
C_{\text{TV}}(\pi_o)
+
C_{\text{regions}}(\pi_o)
+
C_\beta(o)
+
C_{\text{interface}}(o)
\right]
]

你当前代码里的：

[
\texttt{policy_tv_total}
]

[
\texttt{policy_regions_total}
]

就属于这个类别；`description_length_proxy` 里已经把 total TV、total regions、option pair count 都计进去了，这是对的。([GitHub][1])

这个指标可以防止：

[
\text{“我有很多很强的 options，但当前任务只用了一个，所以不算复杂”}
]

这种作弊。

### mean per option complexity

这个回答：

> 单个 option 平均有多复杂？

它适合做诊断，不适合作为 objective。因为它很容易被操纵：

* 加很多简单但没用的 options，可以稀释 mean；
* 一个巨大 targeted option library，mean 可能不夸张，但 total 非常大；
* 一个 shared goal-conditioned policy，mean 的定义也会变模糊。

所以 mean 只用来读数，不进入主排序。

### optimal abstract policy occupancy-weighted complexity

这个回答：

> 在当前任务或任务分布下，实际执行时用了多少 option 复杂度？

定义为：

[
C_{\pi}^{\text{occ}}
====================

\mathbb E_{\mathcal T}
\left[
\sum_z d_{\bar\pi^*_{\mathcal T}}(z)
\sum_o \bar\pi^**{\mathcal T}(o|z)
C*\pi(o)
\right]
]

其中 (d_{\bar\pi^*}) 是 reduced SMDP 上的 discounted boundary occupancy。

因为你的 (\bar\Gamma^o) 已经是 discounted terminal kernel，所以 occupancy 可以直接用：

[
d
=

\mu
+
\bar\Gamma_{\bar\pi}^{\top}d
]

即：

[
d
=

(I-\bar\Gamma_{\bar\pi}^{\top})^{-1}\mu
]

其中：

[
\bar\Gamma_{\bar\pi}(z,z')
==========================

\sum_o
\bar\pi(o|z)
\bar\Gamma^o(z,z')
]

这个 occupancy-weighted complexity 很有用，但不能单独用。原因是，如果只测当前 start-goal，`endpoints + targeted` 可能只用一个强 option，于是 unused library 不被计费。它必须和 total library cost 一起用。

我建议 objective 里写成：

[
\boxed{
C_{\pi}
=======

\alpha C_{\pi}^{\text{lib}}
+
\beta C_{\pi}^{\text{occ}}
+
\rho C_{\text{interface}}
}
]

实验报告中同时列：

[
C_{\pi}^{\text{lib}},
\quad
C_{\pi}^{\text{mean}},
\quad
C_{\pi}^{\text{occ}}
]

但 Pareto/selection 主要看：

[
C_{\pi}^{\text{lib}} + C_{\pi}^{\text{occ}}
]

这和 state abstraction as compression 的思想一致：好的 abstraction 不是“状态数少”，而是在压缩和性能损失之间取得合理 trade-off。Rate-distortion / information bottleneck 视角正是把 state abstraction 看作 compression-performance tradeoff。([AAAI出版][3])

---

## 3. first-candidate-boundary targeted option：语义应该是“先吸收到 hidden terminal，再 invalid/split”

这个问题最关键。我不建议直接只做：

[
\text{cross } B_0\setminus B
\Rightarrow
\text{invalid}
]

因为这样你丢掉了 split 信号：你知道这条边不好，但不知道应该把哪个 hidden candidate 加进 (B)。

也不建议直接把 hidden terminal 当成普通 terminal 留在模型里，因为那等于偷偷给 abstract planner 加了一个未计费节点。

所以正确流程是三阶段：

[
\boxed{
\text{detect hidden terminal}
\rightarrow
\text{fixed-}B\text{ evaluation marks invalid}
\rightarrow
\text{adaptive version triggers split}
}
]

### 定义

给定：

[
B \subseteq B_0
]

其中 (B) 是当前 compact graph 的 boundary，(B_0) 是 candidate boundary set。

对 source-target pair：

[
(b,g),\qquad b,g\in B
]

定义 targeted policy：

[
\pi_g(a|s)
]

例如当前的 shortest-path-to-target feedback policy。

但 termination 不再是“到达 (g) 才停”，而是：

[
\tau
====

\inf
{t\ge 1:
S_t\in B_0\setminus{b}
}
]

也就是：

> 从 (b) 出发，朝 (g) 走，但一旦撞到任何 candidate boundary，就立刻停。

这才配得上名字：

[
\text{first-candidate-boundary targeted option}
]

注意这里是 (t\ge 1)，否则 source (b\in B_0) 会在 (t=0) 立即终止。

终止结果有三种：

1. (S_\tau=g)：这是理想 direct edge。
2. (S_\tau=h\in B,\ h\neq g)：这是 valid stochastic outcome，表示“本来想去 (g)，但先到了另一个已显式建模的 boundary，planner 可以在那里重新决策”。
3. (S_\tau=h\in B_0\setminus B)：这是 hidden terminal，不能被当前 graph 表达。

于是：

[
p_{\text{hidden}}(b,g)
======================

\Pr
[
S_\tau \in B_0\setminus B
\mid S_0=b,\pi_g
]
]

固定 (B) 的评估规则：

[
p_{\text{hidden}}(b,g)>\epsilon_h
\Rightarrow
\text{edge invalid}
]

在线 split 规则：

[
h^*
===

\arg\max_{h\in B_0\setminus B}
\Pr[S_\tau=h]
]

如果这个 hidden mass 高，就把 (h^*) 加进 (B)，然后重新做 Bellman-Kron reduction。

所以回答你的第三个问题：

> **应该先吸收到 hidden terminal 用来观测；但在当前 abstract graph 上，这条 edge 仍然判 invalid；随后 hidden terminal 触发 split。**

---

## 4. 这个 first-boundary targeted 不能继续用“每个 target 一个全局 P”来完全实现

你现在 `targeted/local_targeted` 的实现是：对每个 target boundary 建一个 shortest-path policy，并用 target state 作为 absorbing state；`local_targeted` 再通过 `local_horizon` mask 掉太远的 source-target pair。([GitHub][1])

但 first-candidate-boundary targeted 的 termination set 依赖 source：

[
T_{b,g}=B_0\setminus{b}
]

所以它天然是 pair-specific option model：

[
o_{b\to g}
]

而不是纯 target-specific option model：

[
o_g
]

否则会出现一个问题：如果你把所有 (B_0) 都设成 absorbing，那么 source (b) 也 absorbing，option 会在 (t=0) 终止。

实现上有两个选择。

### 方案 A：pair-specific reduction，最清晰

对每个 valid pair ((b,g)) 单独构造一个 transition model：

[
P^{b,g}
]

其中：

* policy 是 (\pi_g)；
* absorbing set 是 (B_0\setminus{b})；
* source (b) 的 row 不吸收，照常按 (\pi_g) 走一步；
* 只使用 source row 的 reduced model。

然后用 (B_0) 做 reduction，得到 terminal distribution over all candidates：

[
\bar\Gamma^{b,g}_{B_0}
]

再投影到当前 (B)：

[
\bar\Gamma^{b,g}_{B}
====================

\bar\Gamma^{b,g}_{B_0}[:,B]
]

同时记录 hidden mass：

[
\bar\Gamma^{b,g}_{H}
====================

\bar\Gamma^{b,g}_{B_0}[:,B_0\setminus B]
]

如果 hidden mass 超阈值，edge invalid 并触发 split。

### 方案 B：augmented state，比较优雅但没必要现在做

给状态加一个 flag：

[
(s,\text{started})
]

让 source 在 (t=0) 不吸收，走出第一步以后再按 (B_0) 吸收。这个更像严格 SMDP option semantics，但实现成本高。现在 tabular gridworld 里方案 A 足够。

---

## 5. 推荐你下一版实验的合法性顺序

我建议每个 candidate edge 都走这个 pipeline：

### Step 1：candidate generation

先由 `local_horizon` 粗筛：

[
d_{\text{primitive}}(b,g)\le H
]

你现在已经有这个机制。([GitHub][1])

### Step 2：first-boundary rollout / reduction

构造 (o_{b\to g})，终止于 first candidate boundary：

[
\tau=\inf{t\ge1:S_t\in B_0\setminus{b}}
]

计算：

[
p_B(b,g)
========

\Pr[S_\tau\in B]
]

[
p_H(b,g)
========

\Pr[S_\tau\in B_0\setminus B]
]

[
R(b,g)
]

[
\Gamma_B(b,g,\cdot)
]

[
\tau_{\text{mean}},\tau_{\text{var}}
]

### Step 3：edge validity

[
\text{valid}(b,g)
=================

\mathbf 1
[
p_H(b,g)\le\epsilon_h
]
\cdot
\mathbf 1
[
D_{\text{rollout}}(b,g)\le\epsilon_r
]
\cdot
\mathbf 1
[
C_{\text{bypass}}(b,g)\le\epsilon_b
]
]

### Step 4：split proposal

如果 invalid because hidden:

[
h^*
===

\arg\max_{h\in B_0\setminus B}
\Pr[S_\tau=h]
]

add:

[
B \leftarrow B\cup {h^*}
]

如果 invalid because residual:

[
h^*
===

\arg\max_s
\text{rollout residual contribution along edge}
]

或者沿 rollout 中点 / high variance point split。

### Step 5：recompute Bellman-Kron

因为 Bellman-Kron 本身在给定 (B,O) 后是精确代数；你的实现路线和实验笔记也已经明确：真正未知的是 boundary selection、option definition、boundary fusion 和 sample estimation，reduction 本身应该作为 oracle 检验这些选择。([GitHub][4])

---

## 6. 对你三个问题的直接结论

### 1. residual bypass 是 hard constraint 还是 weighted penalty？

**最终评估：hard constraint。搜索/排序：weighted penalty。**

更具体：

[
D_{\text{rollout}},D_{\text{SMDP}},P_{\text{hidden-cross}}
]

属于“模型是否合法”的条件，不应该只当 soft cost。否则 one-option-solve-whole-task 仍可能通过调权重获胜。

但：

[
C_{\text{bypass}}
]

如果来自 noisy saliency，比如 value gradient / betweenness / spectral candidate，可以先做 penalty，再用 threshold 触发 split。

所以我会用：

[
B_0^{\text{hard}}:\quad \text{cross} \Rightarrow \text{invalid}
]

[
B_0^{\text{soft}}:\quad \text{cross} \Rightarrow \text{penalty + split priority}
]

### 2. policy complexity 按 total、mean，还是 optimal occupancy？

**objective 里用 total library + occupancy weighted；mean 只报告。**

推荐：

[
C_\pi
=====

\alpha C_\pi^{\text{lib}}
+
\beta C_\pi^{\text{occ}}
+
\rho C_{\text{interface}}
]

其中：

[
C_\pi^{\text{lib}}
==================

\sum_o C_\pi(o)
]

[
C_\pi^{\text{occ}}
==================

\mathbb E_{\text{held-out tasks}}
\left[
\sum_z d_{\bar\pi^*}(z)C_\pi(\bar\pi^*(z))
\right]
]

如果只做 single start-goal，occupancy 会偏袒 `endpoints + targeted`。所以 occupancy 必须在 held-out goal / held-out reward / multi-task distribution 上算。

### 3. first-candidate-boundary targeted option 怎么定义？

**定义上：terminate at first (B_0) candidate boundary。**

**评估上：如果 first terminal 在 (B_0\setminus B)，当前 edge invalid。**

**学习上：把这个 hidden terminal 作为 split proposal。**

也就是：

[
\text{hidden terminal 是诊断变量，不是免费 abstract node。}
]

不要 silent absorb；不要只 invalid 而不记录 hidden hit。正确做法是：

[
\text{absorb for measurement}
\rightarrow
\text{invalid for current graph}
\rightarrow
\text{split for next graph}
]

---

## 7. 我建议你把实验 claim 改成这个

不要说：

> `endpoints + targeted` 用极少节点得到低 gap。

而是说：

> Bellman-Kron 在给定 (B,O) 后精确保留 boundary backup；真正的学习问题是寻找一个满足 rollout residual、SMDP consistency、hidden-boundary crossing constraints 的最小描述长度 graph-option pair。

这个 claim 更稳。Options 理论本身就说明 MDP + fixed options 会诱导 SMDP；所以只要 option 足够强，粗 graph 低 gap 并不意外。 SMDP homomorphism 相关工作也提醒： reduced model 的 state set 变小，不等于问题描述真的变简单；参数/结构复杂度也必须计入。

你现在最应该加的不是更多 baselines，而是这两个表：

[
\text{Feasible Pareto front}
]

只包含满足 hard constraints 的配置。

[
\text{Infeasible-but-low-gap degeneracy table}
]

专门列出 `endpoints + targeted` 这种低 gap 但 high hidden-cross / high policy-complexity / high nonlocal 的配置。

这样实验会非常清楚地区分：

[
\text{compact graph}
]

和：

[
\text{compact-looking graph with hidden option planner}
]

我的最终建议是：下一步先实现 **pair-specific first-candidate-boundary targeted option**，并把 `hidden_mass`、`hidden_argmax`、`edge_valid`、`split_candidate` 写进每条 edge 的 CSV。这个会直接把你现在遇到的三个问题统一起来。

[1]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/run_ablation.py?plain=1 "Laplace-semi-MDP/experiments/run_ablation.py at main · erzhu419/Laplace-semi-MDP · GitHub"
[2]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/bellman_kron.py?plain=1 "Laplace-semi-MDP/experiments/bellman_kron.py at main · erzhu419/Laplace-semi-MDP · GitHub"
[3]: https://ojs.aaai.org/index.php/AAAI/article/view/4179 "
		State Abstraction as Compression in Apprenticeship Learning
							\| Proceedings of the AAAI Conference on Artificial Intelligence
			"
[4]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/SMDP_Fusion_implementation_plan.md "Laplace-semi-MDP/SMDP_Fusion_implementation_plan.md at main · erzhu419/Laplace-semi-MDP · GitHub"
