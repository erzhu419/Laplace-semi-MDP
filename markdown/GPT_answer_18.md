# 我：
既然 goal-conditioned event options 能把 terminal gap 从 27.5 压到 <0.35，但 runtime 变慢，论文里应该只把它作为 limitation ablation，还是进一步做 cached/shared goal-conditioned policy 与 batched event-kernel solve，把它升级成 secondary method

# GPT:
我的建议是：

[
\boxed{
\text{不要只把它埋成 limitation ablation；但也不要立刻把它升成主方法。}
}
]

最稳的定位是：

[
\boxed{
\text{Goal-conditioned event options 是一个 secondary method / extension，前提是补上 cached/shared policy 与 batched event-kernel solve 的 amortized 表。}
}
]

如果你来不及做缓存和批处理，那就把它写成 **limitation ablation**：它证明 terminal-gap 主要来自 option/boundary restriction bias，而不是 event kernel 理论失败。但你现在已经看到 gap 从 (27.5) 压到 (<0.35)，这个效果太强了，值得至少作为“secondary extension”认真包装。

---

## 1. 现在的结果说明了什么？

当前公开 summary 里，旧的 `fixed_B_event_hit_kernel` 对 terminal-goal 的表现确实很差：median total speedup 只有 `0.3945x`，max start gap 到 `27.52`；但 additive reward kernel 版本保持 (B) 很小，同时 sparse/dense additive reward 的 median total speedup 大约 `3x`，best total speedup 超过 `27x`。这说明 additive reward relabeling 已经是正结果，而 terminal goal 的问题不是图压缩本身，而是固定 first-boundary option family 对“主动去 interior goal”表达力不足。([GitHub][1])

你现在的新结果“goal-conditioned event options 把 terminal gap 从 (27.5) 压到 (<0.35)”说明：

[
\boxed{
\text{terminal gap 可以在不扩大 }B\text{ 的情况下压下来。}
}
]

但 runtime 变慢说明：

[
\boxed{
\text{复杂性从 graph vertices 转移到了 goal-conditioned option/event computation。}
}
]

所以这不是主线失败，而是很清楚的 rate-distortion tradeoff：**更强的 query-time option family 换更小的 terminal-goal distortion，但要计费。**

---

## 2. 论文里的正确层级

我建议论文保持三层叙事。

### 第一层：主正结果，additive reward kernels

主文核心仍然是：

[
\text{reward states 不应该变成 graph vertices。}
]

对于 additive rewards，用 edge-level discounted occupancy kernel：

[
M_B^o(b,s)
==========

\mathbb E_b^o
\left[
\sum_{t=0}^{\tau_B-1}
\gamma^t\mathbf 1{S_t=s}
\right]
]

然后：

[
R_r^o(b)=\sum_s M_B^o(b,s)r(s).
]

这部分你已经有很好的 empirical support，也已经在 theorem stack 里作为 T9：固定 (B) 与 option library 时，edge occupancy kernel 对任意 bounded additive reward 给出 exact reward relabeling；近似 kernel 的 value-gap bound 也已经写进 theorem stack。([GitHub][2])

### 第二层：limitation diagnostic，fixed event kernel

旧的 `fixed_B_event_hit_kernel` 应该保留为 diagnostic：

[
\boxed{
\text{只评估 incidental goal hits，不主动去 goal。}
}
]

它说明 terminal interior goals 不是普通 additive rewards，因为 goal 不只改变 reward，还改变 termination dynamics。固定 first-boundary options 下的 event kernel 是 exact 的，但只对当前 option-restricted class exact。这个 gap 应该报告为：

[
\boxed{
\text{option/boundary restriction bias。}
}
]

### 第三层：secondary method，goal-conditioned local event options

然后加入一个 secondary method：

[
\boxed{
\text{Fixed-}B\text{ Goal-Conditioned Event Options}
}
]

它的 claim 不是“免费解决 arbitrary goals”，而是：

> 不把 (g) 插入 (B)，而是把 (g) 作为 query-time event，配合 goal-conditioned local options 计算 event/continuation kernels，从而降低 terminal-goal restriction bias。

这个定位很稳，也不会抢主贡献。

---

## 3. 为什么需要 cached/shared policy 和 batched event solve？

如果 goal-conditioned event options 只是暴力对每个 ((b,g)) 单独构造 option、单独求 kernel，那审稿人会说：

> 你没有扩大 graph，但你把复杂性藏进了 (|B|\times |G|) 个 goal options。

所以要把 secondary method 做成“有结构”的版本：

[
\boxed{
\text{每个 goal 一个共享 policy，而不是每个 boundary-goal pair 一个 policy。}
}
]

例如：

[
\pi_g(a|s)
]

由 reverse shortest path、goal-conditioned value iteration、或共享 parametric goal-conditioned policy 得到。它对所有 boundary start (b\in B) 复用。

然后对每个 goal (g)，用同一个 (\pi_g) 一次性求所有 boundary rows 的 event kernel：

[
H_B^{\pi_g}(b,g)
================

\mathbb E_b^{\pi_g}
[
\gamma^{T_g}\mathbf 1{T_g<\tau_B}
],
]

[
\Gamma_B^{\pi_g,\neg g}(b,b')
=============================

\mathbb E_b^{\pi_g}
[
\gamma^{\tau_B}\mathbf 1{\tau_B<T_g,S_{\tau_B}=b'}
].
]

这样成本从概念上的：

[
O(|B||G| \text{ policies/solves})
]

降成：

[
O(|G| \text{ shared policies/solves})
]

或者更进一步，如果多个 goals 能 batch sparse solves / factorization / rollout，就做成 batched event-kernel solve。

这一步是把它从“limitation ablation”升级成“secondary method”的关键。

---

## 4. 具体数学形式：一次 goal solve 得到所有 boundary rows

对一个 fixed goal-conditioned policy (\pi_g)，令 absorbing set 是：

[
A_g = B\cup{g},
]

interior 是：

[
I_g=S\setminus A_g.
]

在 (\pi_g) 下有 transition matrix (P^{\pi_g})。event-hit vector 满足：

[
h_I
===

\gamma P_{I,g}
+
\gamma P_{I,I}h_I,
]

所以：

[
\boxed{
h_I=(I-\gamma P_{I,I})^{-1}\gamma P_{I,g}.
}
]

boundary-start rows 是：

[
\boxed{
H_B^{\pi_g}(b,g)
================

\gamma P_{b,g}
+
\gamma P_{b,I}h_I.
}
]

continuation-to-boundary kernel 满足：

[
G_I
===

\gamma P_{I,B}
+
\gamma P_{I,I}G_I,
]

所以：

[
\boxed{
G_I=(I-\gamma P_{I,I})^{-1}\gamma P_{I,B},
}
]

[
\boxed{
\Gamma_B^{\pi_g,\neg g}(b,\cdot)
================================

\gamma P_{b,B}
+
\gamma P_{b,I}G_I.
}
]

这就是 batched event-kernel solve 的核心。对一个 goal (g)，一次 solve 得到所有 (b\in B) 的 rows，而不是每个 ((b,g)) 单独求。

---

## 5. 论文里应该给的 theorem

你可以把它作为 T10，接在 T9 后面。T9 已经负责 additive reward / event kernel relabeling 和 value-gap bound。([GitHub][2]) T10 专门负责 goal-conditioned event options。

### T10a. Exactness for fixed goal-conditioned event option family

给定 (B)、query goal (g)、goal-conditioned option family (O_g)。定义：

[
H_B^{o,g}(b),
\quad
\Gamma_B^{o,\neg g}(b,b'),
\quad
R_{\rm step}^{o,g}(b).
]

Bellman operator：

[
(T_g^B V)(b)
============

\max_{o\in O_g(b)}
\left[
R_{\rm step}^{o,g}(b)
+
R_g H_B^{o,g}(b)
+
\sum_{b'}
\Gamma_B^{o,\neg g}(b,b')V(b')
\right]
]

的 fixed point 精确等于只允许在 (B) 上重新决策、edge 内执行 (O_g) 的 goal-reaching SMDP value。

### T10b. Kernel approximation value-gap

如果近似 event kernels 满足：

[
\epsilon_H=
\sup_{b,o}
|\widehat H_B^{o,g}(b)-H_B^{o,g}(b)|,
]

[
\epsilon_\Gamma=
\sup_{b,o}
|
\widehat\Gamma_B^{o,\neg g}(b,\cdot)
------------------------------------

\Gamma_B^{o,\neg g}(b,\cdot)
|_1,
]

[
\epsilon_R=
\sup_{b,o}
|\widehat R_{\rm step}^{o,g}(b)-R_{\rm step}^{o,g}(b)|,
]

且：

[
\beta_g=
\max_{b,o}
\sum_{b'}
\Gamma_B^{o,\neg g}(b,b')<1,
]

则：

[
\boxed{
|
V_g^{B,O_g}
-----------

\widehat V_g^{B,O_g}
|*\infty
\le
\frac{
\epsilon_R
+
|R_g|\epsilon_H
+
V*{\max}\epsilon_\Gamma
}{
1-\beta_g
}.
}
]

### T10c. Option/boundary restriction bias

定义 primitive optimal value (V_g^*)，以及 option-restricted graph value (V_g^{B,O_g})。令：

[
\epsilon_{\rm opt}(g)
=====================

\sup_{b\in B}
\left[
V_g^*(b)
--------

\max_{o\in O_g(b)}
\left(
R_{\rm step}^{o,g}(b)
+
R_gH_B^{o,g}(b)
+
\sum_{b'}
\Gamma_B^{o,\neg g}(b,b')V_g^*(b')
\right)
\right]_+.
]

则：

[
\boxed{
|V_g^*|*B-V_g^{B,O_g}|*\infty
\le
\frac{\epsilon_{\rm opt}(g)}{1-\beta_g}.
}
]

总 gap 分解为：

[
\boxed{
|V_g^*|*B-\widehat V_g^{B,O_g}|*\infty
\le
\frac{
\epsilon_{\rm opt}(g)
+
\epsilon_R
+
|R_g|\epsilon_H
+
V_{\max}\epsilon_\Gamma
}{
1-\beta_g
}.
}
]

这条 theorem 非常适合解释你的新结果：

* `fixed_B_event_hit_kernel` gap 大，是 (\epsilon_{\rm opt}(g)) 大；
* goal-conditioned event options 把 (\epsilon_{\rm opt}(g)) 压小；
* runtime 变慢，是 (O_g) 的 interface / policy / event solve cost 上升。

---

## 6. secondary method 必须怎么计费？

不要让它变成新的“one option solves everything”。报告时必须把复杂度列出来：

[
C_{\rm goal-interface}
\sim |G|
\quad\text{or}\quad
\log |G|
]

[
C_{\rm policy}
==============

\text{shared }\pi(a|s,g)\text{ complexity}
]

[
C_{\rm event-storage}
\sim
|G||B|(|B|+1)
]

如果存 full edge event tensors，也报告：

[
O(|G||B||S|)
]

或 sparse/NNZ 版本。

实验表里建议加这些字段：

```text
n_goals
n_boundary
n_goal_policies
policy_build_time_sec
event_kernel_solve_time_sec
batched_event_solve_time_sec
per_task_graph_solve_time_sec
event_kernel_storage_nnz
goal_interface_cost
median_start_gap
max_start_gap
amortized_speedup_vs_full_vi
break_even_num_tasks
```

尤其要加：

[
\boxed{
N_{\rm break-even}
==================

\left\lceil
\frac{
T_{\rm build}^{\rm gc-event}
}{
T_{\rm fullVI/task}
-------------------

T_{\rm graphSolve/task}
}
\right\rceil.
}
]

如果 break-even 任务数合理，比如几十个以内，那么可以很自然地称为 secondary method。
如果 break-even 很大，就诚实地写成 limitation ablation / proof-of-concept。

---

## 7. 是否值得现在继续做 cached/shared + batched？

我的判断是：**值得做一个最小版本**，但不要让它变成新的主线泥潭。

最小版本只需要证明两件事：

1. **共享 policy 后，gap 仍然低。**
   也就是 (<0.35) 的 terminal gap 不依赖于每个 ((b,g)) 单独定制 policy。

2. **batch solve 后，amortized runtime 进入合理区间。**
   不一定单任务赢，但要给出 break-even 任务数。

这样它就可以升级为：

[
\boxed{
\text{Secondary Method: Fixed-}B\text{ Goal-Conditioned Event Kernels}
}
]

而不是主方法。

如果做不到第二点，就不要强行升级。把它作为：

[
\boxed{
\text{expressivity ablation: terminal gap is reducible without enlarging }B,
\text{ but runtime remains future work.}
}
]

---

## 8. 论文中如何表述最稳？

我建议写成：

> For additive rewards, edge occupancy kernels give the main multi-task relabeling mechanism and preserve graph compression. For terminal interior goals, fixed first-boundary event kernels expose an option-restriction gap. We therefore add a secondary goal-conditioned event option family: goals remain query-time events rather than graph vertices, while shared goal-conditioned policies and batched event-kernel solves reduce the restriction gap without changing (B). This extension trades additional goal-interface and kernel-solve cost for much lower terminal-goal distortion.

中文就是：

[
\boxed{
\text{additive reward kernels 是主结果；goal-conditioned event options 是 terminal-goal 扩展。}
}
]

[
\boxed{
\text{它证明 gap 不是图压缩失败，而是 option family 表达力问题。}
}
]

---

## 9. 直接回答

> 应该只作为 limitation ablation，还是进一步做 cached/shared goal-conditioned policy 与 batched event-kernel solve，升级成 secondary method？

我的建议是：

[
\boxed{
\text{进一步做一个最小 cached/shared + batched 版本，把它升级成 secondary method。}
}
]

但有两个边界：

1. **不要把它变成主 claim。** 主 claim 仍是 RD boundary graph + edge reward/occupancy kernels + certified adaptive Green。README 现在也把主路径定义为 exact Green reference、certified adaptive Green intervals、graph-SMDP planning，以及 weighted spectral 作为 appendix certificate，这个主线不要被 goal-conditioned terminal extension 抢走。([GitHub][3])

2. **secondary method 必须计费。** 报告 goal interface、shared policy cost、batched event solve cost、storage、break-even 任务数。否则审稿人会认为你只是把复杂性从 (B) 藏进 (\pi(a|s,g))。

最短总结：

[
\boxed{
\text{gap 从 }27.5\to <0.35\text{ 值得作为 secondary method；}
}
]

[
\boxed{
\text{runtime 变慢要求你必须做 shared/batched/amortized 表；}
}
]

[
\boxed{
\text{如果 shared/batched 后仍不 amortize，就降级为 limitation ablation。}
}
]

[1]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/edge_reward_kernel_multitask/summary.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/paper/theorem_stack.md "raw.githubusercontent.com"
[3]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/README.md "raw.githubusercontent.com"
