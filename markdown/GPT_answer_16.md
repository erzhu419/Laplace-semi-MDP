# 我：
Large-scale compression supports planning-speed compression when B stays small, but our all-state amortized experiment destroys compression because it inserts every goal into B. Should the paper formulate multi-task rewards through edge-level discounted occupancy / first-hit reward kernels, so arbitrary interior rewards can be evaluated without promoting reward states to graph vertices? What theorem should connect this reward-kernel approximation to value-gap bounds in the graph SMDP?

# GPT：
是的，**下一步应该把 multi-task rewards 从“把 reward/goal state 升格成 boundary vertex”改成“edge-level discounted occupancy / first-hit reward kernels”**。否则 all-state multitask 会天然破坏你的核心 compression claim。

你现在的证据已经非常清楚：large-scale compression 在 (B) 小时成立，`corridor_128 endpoints` 用 (128) 个原状态压到 (2) 个 boundary，planning-only speedup 达到 `2804x`，`turn_articulation` 甚至达到 `4097x`；但 all-state amortized 实验把 25 个 sampled goals 直接插进 (B)，导致 corridor 的 (n_B=26)、maze 的 (n_B=26/30/36)，state compression 只有约 (2\sim3) 倍，并且 25-task speedup 仍小于 1。也就是说，失败不是 SMDP graph 不工作，而是 **task parameter 被错误地编码进 graph topology**。([GitHub][1])

---

## 1. 先分清两类 multitask reward

这里必须把 “arbitrary interior reward” 和 “arbitrary terminal goal” 分开。

### A. 普通 additive reward

如果任务只是改变：

[
r:S\rightarrow \mathbb R
]

例如某些 interior states 有奖励、代价、风险、密度 reward，那么**不应该把这些 reward states 加进 (B)**。正确做法是：保持同一个 boundary graph (B)，对每条 option edge 存一个 discounted occupancy kernel。

这和 successor representation / successor features 的思想一致：Dayan 的 successor representation 本来就是用未来状态占用来支持 reward relabeling；successor features 进一步把“动态结构”和“reward weights”分离，使 reward 改变时可以快速复用。([Gatsby][2])

### B. Terminal goal / absorbing goal

如果任务是“到达 interior state (g) 就终止”，那它不仅改变 reward，还改变了 termination dynamics。此时只用 occupancy reward kernel 不够；你还需要 **first-hit event kernel**：

[
\Pr[T_g < \tau_B]
]

或者 discounted version：

[
\mathbb E[\gamma^{T_g}\mathbf 1{T_g<\tau_B}]
]

但仍然不需要把每个 (g) 永久加入 (B)。你可以把 (g) 当成 query-time absorbing event，通过 edge event kernel 修正 Bellman backup。

所以建议论文里写成：

[
\boxed{
\text{reward relabeling uses occupancy kernels;}
\quad
\text{terminal-goal relabeling uses first-hit event kernels.}
}
]

---

## 2. Edge-level discounted occupancy kernel

给定当前 boundary set：

[
B\subset S
]

给定 option (o)，从 boundary (b\in B) 出发，令：

[
\tau_B=\inf{t\ge 1:S_t\in B}
]

定义 edge-level discounted occupancy kernel：

[
\boxed{
M^o_B(b,s)
==========

\mathbb E_b^o
\left[
\sum_{t=0}^{\tau_B-1}
\gamma^t
\mathbf 1{S_t=s}
\right]
}
]

这表示：从 (b) 执行 option (o)，直到第一次撞到下一个 boundary 之前，对每个原始状态 (s) 的 discounted occupancy。

同时已有的 SMDP terminal kernel 是：

[
\boxed{
\Gamma^o_B(b,b')
================

\mathbb E_b^o
\left[
\gamma^{\tau_B}
\mathbf 1{S_{\tau_B}=b'}
\right]
}
]

于是任意 additive reward (r:S\rightarrow\mathbb R) 的 edge reward 不再需要重新构图，只需要内积：

[
\boxed{
R^o_r(b)
========

\sum_{s\in S}
M^o_B(b,s)r(s)
==============

\langle M^o_B(b,\cdot),r\rangle
}
]

然后 graph SMDP Bellman backup 是：

[
\boxed{
(T^B_r V)(b)
============

\max_{o\in O(b)}
\left[
R^o_r(b)
+
\sum_{b'\in B}
\Gamma^o_B(b,b')V(b')
\right]
}
]

这个公式的重点是：

[
\boxed{
B,\Gamma,M \text{ 固定；任务只改变 } r \text{ 和 } R_r=M r。
}
]

这就是你 all-state amortized 现在缺的东西。

---

## 3. Matrix form：它和 Bellman-Kron 是同一套 Green kernel

如果把状态分成 boundary (B) 和 interior (I=S\setminus B)，对固定 option (o) 有：

[
P^o=
\begin{pmatrix}
P^o_{BB} & P^o_{BI}\
P^o_{IB} & P^o_{II}
\end{pmatrix}
]

那么 discounted interior occupancy 是：

[
\boxed{
M^o_{B,I}
=========

\gamma P^o_{BI}(I-\gamma P^o_{II})^{-1}
}
]

如果 edge reward 包含起点 boundary reward，则加上：

[
r_B
]

得到：

[
\boxed{
R^o_r
=====

r_B
+
\gamma P^o_{BI}
(I-\gamma P^o_{II})^{-1}
r_I
}
]

这和你现有 Bellman-Kron reduced reward 公式完全同构。你目前 theorem stack 里已经有 graph-SMDP Bellman contraction 和 residual-to-value-gap 这一层，所以 reward-kernel theorem 可以直接接在现有 T5 后面，而不是另起一套理论。([GitHub][3])

---

## 4. 核心定理 1：Exact Edge Reward-Kernel Theorem

可以把第一个 theorem 写成这样。

**Theorem: Exact option-restricted reward relabeling.**

给定有限 MDP、discount (\gamma<1)、boundary set (B)、固定 option set (O)。对每个 ((b,o)) 精确计算：

[
\Gamma^o_B(b,b')
================

\mathbb E_b^o[
\gamma^{\tau_B}\mathbf 1{S_{\tau_B}=b'}
]
]

和：

[
M^o_B(b,s)
==========

\mathbb E_b^o
\left[
\sum_{t=0}^{\tau_B-1}\gamma^t\mathbf 1{S_t=s}
\right].
]

则对任意 bounded additive reward (r:S\to\mathbb R)，由：

[
R^o_r(b)=M^o_B(b,\cdot)^\top r
]

和 (\Gamma^o_B) 定义的 graph SMDP Bellman operator：

[
(T^B_rV)(b)
===========

\max_o
\left[
R^o_r(b)+\Gamma^o_B(b,\cdot)V
\right]
]

的 fixed point (V^B_r) 精确等于原始 MDP 中**只允许在 boundary 决策并在 edge 内执行固定 options**的最优价值。

也就是说：

[
\boxed{
V^B_r(b)
========

\sup_{\pi\in\Pi(B,O)}
\mathbb E^\pi_b
\left[
\sum_{t=0}^\infty\gamma^t r(S_t)
\right].
}
]

这里的 equality 是对 option-restricted policy class 的精确等价，不是对 full primitive MDP optimal value 的免费等价。Options 理论本来就说明 fixed options over an MDP induces an SMDP；你的 reward kernel 只是把 reward relabeling 加进同一个 SMDP reduction。([自主学习实验室][4])

---

## 5. 核心定理 2：Reward-kernel approximation value-gap bound

实际实现会近似 (M) 和 (\Gamma)，所以需要第二个 theorem。

设 exact graph-SMDP operator 是：

[
T_r
]

近似 operator 是：

[
\widehat T_r
]

它们分别由：

[
(M,\Gamma)
\quad\text{和}\quad
(\widehat M,\widehat\Gamma)
]

定义。

令：

[
\epsilon_R(r)
=============

\sup_{b,o}
\left|
(\widehat M^o_B(b,\cdot)-M^o_B(b,\cdot))^\top r
\right|
]

[
\epsilon_\Gamma
===============

\sup_{b,o}
\left|
\widehat\Gamma^o_B(b,\cdot)
---------------------------

\Gamma^o_B(b,\cdot)
\right|_1
]

并令：

[
\beta
=====

\max_{b,o}
\sum_{b'}\Gamma^o_B(b,b')
=========================

\max_{b,o}
\mathbb E_b^o[\gamma^{\tau_B}]
<1.
]

若 (\widehat\Gamma) 也有 row sum 不超过 (\beta)，且所有 value 都有上界：

[
|V|*\infty\le V*{\max},
]

则 exact graph value (V^B_r) 与近似 graph value (\widehat V^B_r) 满足：

[
\boxed{
|V^B_r-\widehat V^B_r|*\infty
\le
\frac{
\epsilon_R(r)+V*{\max}\epsilon_\Gamma
}{
1-\beta
}.
}
]

如果只关心 reward-kernel 误差、(\Gamma) 精确，则：

[
\boxed{
|V^B_r-\widehat V^B_r|_\infty
\le
\frac{\epsilon_R(r)}{1-\beta}.
}
]

如果 reward bounded：

[
|r|*\infty\le R*{\max},
]

并且：

[
\sup_{b,o}
|\widehat M^o_B(b,\cdot)-M^o_B(b,\cdot)|_1
\le \epsilon_M,
]

则：

[
\epsilon_R(r)\le R_{\max}\epsilon_M
]

所以：

[
\boxed{
|V^B_r-\widehat V^B_r|*\infty
\le
\frac{
R*{\max}\epsilon_M+V_{\max}\epsilon_\Gamma
}{
1-\beta
}.
}
]

这个就是你要的 value-gap theorem。它把 reward-kernel approximation 误差和 graph SMDP value gap 直接连起来。

---

## 6. 和 full MDP value gap 的分解

必须诚实地写：graph reward kernel 解决的是**任务 relabeling 不破坏 graph compression**，但不自动消除 option abstraction bias。

对于 full primitive optimal value：

[
V^*_r
]

和 graph value：

[
\widehat V^B_r
]

应该写成三项分解：

[
\boxed{
|V^*_r-\widehat V^B_r|
\le
\underbrace{
|V^**r-V^{B,O}*r|
}*{\text{option / boundary restriction bias}}
+
\underbrace{
|V^{B,O}*r-V^B_r|
}*{\text{exact reduction error, ideally }0}
+
\underbrace{
|V^B_r-\widehat V^B_r|
}*{\text{kernel approximation error}}.
}
]

其中：

* 第一项是 graph abstraction 本身的表达力问题；
* 第二项在 exact ((M,\Gamma)) 下为 0；
* 第三项由上面的 reward-kernel approximation theorem 控制。

这会避免审稿人攻击你说：

> 你只是换 reward kernel，怎么保证等于 full MDP optimal value？

正确回答是：

[
\boxed{
\text{它等于 option-restricted SMDP optimal value；到 full MDP 的差距单独作为 abstraction bias 报告。}
}
]

---

## 7. 如果 reward 是 feature family，成本会更低

如果 multitask rewards 满足：

[
r_\theta(s)=\phi(s)^\top\theta
]

则不用存 full (M(b,o,s))。只需存 edge successor feature：

[
\boxed{
\Psi^o_B(b)
===========

\mathbb E_b^o
\left[
\sum_{t=0}^{\tau_B-1}
\gamma^t
\phi(S_t)
\right]
}
]

于是：

[
R^o_\theta(b)
=============

\Psi^o_B(b)^\top\theta.
]

这就是 successor features 的 edge-level SMDP 版本。Successor features / GPI 这条线的基本设定就是环境 dynamics 可复用、任务 reward 变化时通过 successor features 快速迁移；你的区别是 successor features 不是对 primitive state-action policy 存，而是对 **graph-SMDP edge / option segment** 存。([Proceedings of Machine Learning Research][5])

如果任意 reward 不在 feature span 中，设：

[
r=\Phi\theta+\eta,
\quad
|\eta|_\infty\le\delta,
]

那么 edge reward 误差多一项：

[
\epsilon_{\rm proj}
\le
\frac{\delta}{1-\gamma}
]

更精细地，如果 edge expected duration 较短，可以用 edge occupancy mass：

[
\epsilon_{\rm proj}(b,o)
\le
\delta
\sum_s M^o_B(b,s).
]

然后代入 value-gap bound：

[
\boxed{
|V^B_r-\widehat V^B_r|*\infty
\le
\frac{
\epsilon*{\rm kernel}
+
\epsilon_{\rm proj}
}{
1-\beta
}.
}
]

---

## 8. Terminal interior goals：需要 first-hit event kernel

如果 all-state multitask 的语义是：

> 每个 interior state (g) 都可以成为 absorbing goal。

那不要把 (g) 放进 (B)，但也不能只用 additive occupancy reward。应该定义：

[
T_g=\inf{t\ge 0:S_t=g}
]

和 edge-level goal hit kernel：

[
\boxed{
H^o_B(b,g)
==========

\mathbb E_b^o
\left[
\gamma^{T_g}
\mathbf 1{T_g<\tau_B}
\right]
}
]

以及“未命中 goal 而先到 boundary”的 continuation kernel：

[
\boxed{
\Gamma^{o,\neg g}_B(b,b')
=========================

\mathbb E_b^o
\left[
\gamma^{\tau_B}
\mathbf 1{\tau_B<T_g,\ S_{\tau_B}=b'}
\right].
}
]

如果 goal reward 是 (R_g)，则 graph Bellman backup 变成：

[
\boxed{
(T_gV)(b)
=========

\max_o
\left[
R_g H^o_B(b,g)
+
R_{\rm step}^o(b)
+
\sum_{b'}
\Gamma^{o,\neg g}_B(b,b')V(b')
\right].
}
]

这样 (g) 是 query-time absorbing event，不是 permanent graph vertex。

这可以作为 all-state terminal-goal 的正确替代实验：

```text
baseline: promote all sampled goals into B
new: keep B fixed, evaluate goals through H_B^o(b,g) and Γ_B^{o,¬g}
```

如果 (H) 对所有 (g\in S) 都存，内存是：

[
O(|B||O||S|)
]

这仍然比把每个 goal 加入 (B) 后导致 graph edges / options 膨胀要更符合 compression 逻辑，尤其当 (|B|\ll |S|)。

---

## 9. 论文 claim 应该怎么改

我建议把 multitask claim 改成：

[
\boxed{
\text{Graph compression is over decision boundaries, not over reward supports.}
}
]

更正式地：

> We do not promote every task-specific reward state into the graph. Instead, we keep the boundary graph fixed and amortize reward relabeling through edge-level discounted occupancy and first-hit event kernels.

中文就是：

> 图节点表示高层决策点，不表示所有可能的 reward 位置。reward 变化应该通过 edge reward kernel 查询，而不是改变 graph topology。

这正好解释你现在的 negative control：all-state goal variant 把 sampled goals 插进 boundary，导致 graph 变 dense，speedup 低于 1；这不是主方法失败，而是错误地把任务参数编码进状态抽象。([GitHub][6])

---

## 10. 建议新增的 theorem stack

在你现有 theorem stack 后面加一个 T9：

### T9: Edge Reward-Kernel Relabeling and Value Gap

**T9a. Exact reward relabeling.**

[
R^o_r(b)=M^o_B(b,\cdot)^\top r
]

gives the exact option-restricted SMDP Bellman backup for any bounded additive reward (r).

**T9b. Feature reward relabeling.**

If (r_\theta=\Phi\theta), then:

[
R^o_\theta(b)=\Psi^o_B(b)^\top\theta
]

with:

[
\Psi^o_B(b)=M^o_B(b,\cdot)\Phi.
]

**T9c. Approximation value-gap.**

If:

[
\epsilon_R(r)=
\sup_{b,o}|(\widehat M-M)r|,
\quad
\epsilon_\Gamma=
\sup_{b,o}|\widehat\Gamma-\Gamma|_1,
]

then:

[
|V^B_r-\widehat V^B_r|*\infty
\le
\frac{
\epsilon_R(r)+V*{\max}\epsilon_\Gamma
}{
1-\beta
}.
]

**T9d. Terminal event kernel.**

For absorbing goal (g), use:

[
H^o_B(b,g)
==========

\mathbb E[
\gamma^{T_g}
\mathbf 1{T_g<\tau_B}
]
]

and:

[
\Gamma^{o,\neg g}_B
]

to evaluate goal tasks without promoting (g) into (B).

This theorem can reuse your existing T5 Bellman contraction/value-gap machinery; you only need to instantiate the residual term with reward-kernel error. Your current proof stack already has a Bellman contraction and residual-to-value-gap layer, so this is a natural extension rather than a new proof burden.([GitHub][3])

---

## 11. 实验上怎么证明这个方向是对的

建议新增一个实验：

```text
experiments/run_edge_reward_kernel_multitask.py
```

比较三种方法：

```text
full_vi_per_task
promote_goals_to_B
fixed_B_edge_reward_kernel
fixed_B_event_hit_kernel
```

任务分三类：

```text
dense_random_rewards
sparse_interior_additive_rewards
absorbing_terminal_goals
```

输出：

```text
n_states
n_boundary
state_compression_ratio
edge_reward_kernel_memory
event_kernel_memory
upfront_kernel_time
per_task_reward_relabel_time
per_task_smdp_solve_time
total_amortized_speedup
value_gap_mean
value_gap_max
certified_kernel_error_bound
```

关键图：

[
x=\text{number of tasks}
]

[
y=\text{total time speedup}
]

并且把 all-state promotion 作为 negative control。

预期结论：

[
\boxed{
\text{promote-goals destroys compression;}
\quad
\text{edge reward/event kernels preserve small }B.
}
]

---

## 12. 最直接回答

> Should the paper formulate multi-task rewards through edge-level discounted occupancy / first-hit reward kernels?

**是。** 这是正确方向，而且应该成为 multitask/amortization claim 的核心。
但要分两类：

[
\boxed{
\text{additive rewards}
\Rightarrow
\text{discounted edge occupancy kernel }M
}
]

[
\boxed{
\text{terminal goals}
\Rightarrow
\text{first-hit event kernel }H\text{ plus continuation kernel }\Gamma^{\neg g}
}
]

> What theorem should connect this reward-kernel approximation to value-gap bounds?

主 theorem 就是：

[
\boxed{
|V^B_r-\widehat V^B_r|*\infty
\le
\frac{
\epsilon_R(r)+V*{\max}\epsilon_\Gamma
}{
1-\beta
}
}
]

其中：

[
\epsilon_R(r)
=============

\sup_{b,o}
|(\widehat M-M)r|
]

或 feature version：

[
\epsilon_R(\theta)
==================

\sup_{b,o}
|(\widehat\Psi-\Psi)^\top\theta|.
]

这条定理把 reward-kernel approximation 直接接到 graph-SMDP value gap 上；再加上 option-restriction bias 分解，就能把 claim 写得严谨且不夸大。

一句话总结：

[
\boxed{
\text{Reward support should not determine graph vertices.}
}
]

[
\boxed{
\text{Boundary vertices encode decision structure; edge reward/event kernels encode task variation.}
}
]

[1]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/large_scale_compression_adaptive/summary.md "raw.githubusercontent.com"
[2]: https://www.gatsby.ucl.ac.uk/~dayan/papers/d93b.pdf?utm_source=chatgpt.com "Improving Generalisation for Temporal Difference Learning"
[3]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/paper/theorem_stack.md "raw.githubusercontent.com"
[4]: https://www-anw.cs.umass.edu/~barto/courses/cs687/Sutton-Precup-Singh-AIJ99.pdf?utm_source=chatgpt.com "A framework for temporal abstraction in reinforcement ..."
[5]: https://proceedings.mlr.press/v80/barreto18a/barreto18a.pdf?utm_source=chatgpt.com "Transfer in Deep Reinforcement Learning Using Successor ..."
[6]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/amortized_multitask_large_allstates/summary.md "raw.githubusercontent.com"
