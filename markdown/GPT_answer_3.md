我这边公开 `main` 暂时没有搜到 `B_res` 字段，所以按你描述的新实现语义来判断。结论是：

**1. (B_{\rm res}) 一定会带入偏置，但这不是致命问题；关键是把它从“ground truth boundary”降级成“diagnostic probe family”。**
**2. residual threshold 必须归一化；raw residual threshold 不应该跨 task、(\gamma)、option duration 共用。**
**3. 最推荐的主阈值不是 per-step residual，而是 value-impact normalized residual：它直接对应“这个局部模型误差最终能造成多大 planning/value error”。**

---

## 1. (B_{\rm res}) 是否带入 heuristic bias？

**会。只要你显式指定一个 residual diagnostic boundary set，它就编码了某种“什么地方应该被高层看见”的偏好。**

例如：

[
B_{\rm res}^{\rm topo}
======================

\text{junctions/turns/endpoints}
]

这会偏向 topological abstraction。

[
B_{\rm res}^{\rm value}
=======================

\text{high value-gradient states}
]

这会偏向当前 task/reward。

[
B_{\rm res}^{\rm residual}
==========================

\text{high rollout residual states}
]

这会偏向模型当前失败的地方。

[
B_{\rm res}^{\rm all}
=====================

S
]

这几乎会把所有 multi-step option 都打成 crossing，过于严格。

所以不能把某一个 (B_{\rm res}) 称为“真实边界”。更合理的说法是：

[
B_{\rm res}
\text{ defines a diagnostic lens, not the ontology of the environment.}
]

你的公开代码里已经有几种天然的候选 lens：`decision_boundary_states` 会保留 endpoints、junctions、turns 和符号状态；`junction_boundary_states` 保留 degree 非 2 的状态；`spectral_boundary_states` 则用图 Laplacian 的局部 spectral energy 选 landmark。它们本质上就是不同的 (B_{\rm res}) family，而不是唯一标准。([GitHub][1])

---

## 2. 怎么避免 (B_{\rm res}) 变成“人为偏置攻击器”？

我建议把 (B_{\rm res}) 分三层。

### A. Hard structural (B_{\rm res}^{\rm hard})

只包含非常低争议、任务无关的结构点：

[
B_{\rm res}^{\rm hard}
======================

\text{start/goal symbols}
\cup
\text{degree}\neq 2
\cup
\text{turns}
\cup
\text{walls/doors/bottlenecks if explicitly given}
]

这类点不是从 value 或 reward 推出来的，而是从 transition topology 推出来的。对它们可以用 hard constraint：

[
\Pr[
\text{option first hits } B_{\rm res}^{\rm hard}\setminus B
]

>

\epsilon
\Rightarrow
\text{edge invalid}
]

直觉：如果一个 option 从 A 到 C，中途必经一个真正路口 B，但当前 abstract graph 没有 B，那么这个 option 确实在隐藏决策点。

### B. Soft diagnostic (B_{\rm res}^{\rm soft})

包含 spectral、betweenness、model uncertainty、transition entropy、residual peak、value-gradient 等候选点。它们更像“可能应该 split 的地方”。

对它们不要直接 hard invalid，而是：

[
\text{crossing}
\Rightarrow
\text{penalty + split proposal}
]

也就是说：

[
h^*
===

\arg\max_{h\in B_{\rm res}^{\rm soft}\setminus B}
\Pr[S_{\tau}=h]
]

然后把 (h^*) 作为下一轮加入 (B) 的候选。

### C. Reference / oracle (B_{\rm res}^{\rm ref})

例如 all-states 或 full primitive grid。它只能作为上界压力测试，不能作为主合法性标准。否则任何长 option 都会被惩罚，等于否定 SMDP abstraction 本身。

---

## 3. 最重要的实验设计：不要报告单个 (B_{\rm res})，报告 (B_{\rm res})-sensitivity curve

我会把实验改成：

[
\mathcal F_{\rm res}
====================

{
B_{\rm topo},
B_{\rm spectral},
B_{\rm residual},
B_{\rm random},
B_{\rm all}
}
]

然后对每个 graph-option pair 报告：

[
D_{\rm res}^{\mathcal F}
========================

\left{
D_{\rm res}^{B_1},
D_{\rm res}^{B_2},
\dots
\right}
]

而不是只报一个 residual。

更强的是画曲线：

[
x = |B_{\rm res}|/|S|
]

[
y =
\text{hidden-cross mass}
\quad\text{or}\quad
\text{normalized rollout residual}
]

如果 `endpoints + targeted` 只是把复杂性藏进 option，它通常会表现为：

[
|B_{\rm res}|\text{ 稍微变大}
\Rightarrow
\text{hidden-cross mass 快速上升}
]

而真正 local graph-option abstraction 应该更平滑。

公开代码里的 report 已经明确指出 `targeted` option 是“很粗的图 + 很强的 option model”的上限测试，而且会把复杂性藏进 option policy；所以现在用 (B_{\rm res})-sensitivity 去攻击它，方向是对的。([GitHub][2])

---

## 4. 防止 (B_{\rm res}) circularity：必须做 split 数据集

如果 (B_{\rm res}) 是从 residual 选出来的，那么最危险的问题是 circular evaluation：

[
\text{用同一批 residual 选 }B_{\rm res}
\quad\text{又用它评估 residual}
]

这会天然放大失败。

我建议分成三份：

[
D_{\rm train}
\rightarrow
\text{learn } B,O,\phi
]

[
D_{\rm calib}
\rightarrow
\text{choose } B_{\rm res},\epsilon
]

[
D_{\rm test}
\rightarrow
\text{final residual / gap / hidden-cross evaluation}
]

如果数据少，可以 cross-fit：

[
\text{fold 1 selects } B_{\rm res}, \text{ fold 2 evaluates}
]

然后交换平均。

这样 (B_{\rm res}) 仍然有 inductive bias，但不再是“用答案攻击自己”。

---

## 5. residual threshold 是否应该按 task / discount / option duration 归一化？

**是，必须归一化。raw residual threshold 没有可比性。**

原因很简单：同样的 raw residual，在不同 (\gamma)、不同 reward scale、不同 option duration 下，对最终 planning gap 的影响完全不同。

你的 Bellman-Kron reduction 里核心对象是：

[
\bar R^o
]

和：

[
\bar\Gamma^o_{bb'}
==================

\mathbb E[
\gamma^\tau
\mathbf 1{S_\tau=b'}
]
]

公开代码里 `bellman_kron_reduce` 已经显式构造了 reduced kernel：

[
\Gamma
======

\gamma P_{BB}
+
\gamma^2P_{BI}
(I-\gamma P_{II})^{-1}P_{IB}
]

以及 reduced reward：

[
\bar R
======

r_B
+
\gamma P_{BI}
(I-\gamma P_{II})^{-1}r_I
]

同时也计算了 hit probability 和 expected tau。([GitHub][1])

所以 residual 应该直接定义在 SMDP backup 上：

[
\delta_{b,o}(v)
===============

\left|
\hat R(b,o)-\bar R(b,o)
+
\left(
\hat\Gamma(b,o,\cdot)
---------------------

\bar\Gamma(b,o,\cdot)
\right)v
\right|
]

这里 (\hat R,\hat\Gamma) 来自 held-out rollout，(\bar R,\bar\Gamma) 来自模型或 Schur complement，(v) 是 boundary value probe。

---

## 6. 主指标：value-impact normalized residual

给一个 task (\mathcal T)，定义 value scale：

[
V_{\rm scale}^{\mathcal T}
==========================

\max
\left(
1,
\frac{R_{\rm scale}^{\mathcal T}}{1-\gamma},
\operatorname{P95}*{s\in B}|V*{\rm primitive}^{\mathcal T}(s)|
\right)
]

如果是 gridworld shortest-path cost，简单一点也可以用：

[
V_{\rm scale}^{\mathcal T}
==========================

\max(1, |V_{\rm primitive}^{\mathcal T}(s_0)|)
]

然后定义 worst-case backup residual：

[
\delta_{b,o}^{\rm wc}
=====================

|\Delta R_{b,o}|
+
V_{\rm scale}^{\mathcal T}
|\Delta \Gamma_{b,o,\cdot}|_1
]

其中：

[
\Delta R=\hat R-\bar R
]

[
\Delta\Gamma=\hat\Gamma-\bar\Gamma
]

再定义 SMDP contraction：

[
\beta
=====

\max_{b,o}
\sum_{b'}
\bar\Gamma^o_{bb'}
]

因为：

[
\sum_{b'}\bar\Gamma^o_{bb'}
===========================

\mathbb E[\gamma^\tau]
]

所以长 option 通常有更小的 (\beta)，短 option 更接近 primitive (\gamma)。

最终主归一化残差：

[
\boxed{
\tilde\delta_{b,o}^{\rm value}
==============================

\frac{
\delta_{b,o}^{\rm wc}
}{
(1-\beta)V_{\rm scale}^{\mathcal T}
}
}
]

然后用统一阈值：

[
\tilde\delta_{b,o}^{\rm value}
\le
\epsilon_{\rm value}
]

这个阈值语义非常清楚：

> 这个 edge 的 held-out model error，在最坏情况下不会造成超过 (\epsilon_{\rm value}) 个 normalized value-scale 的全局 planning 误差。

这比 raw residual 稳得多。

---

## 7. duration 归一化：用于诊断，不要替代 value-impact threshold

option duration 会影响 reward residual 的自然尺度。长 option 累计 reward 更大，raw (|\Delta R|) 也自然更大。

你可以用 discounted option length：

[
L_\gamma(b,o)
=============

\mathbb E
\left[
\sum_{t=0}^{\tau-1}\gamma^t
\right]
=======

\frac{
1-\mathbb E[\gamma^\tau]
}{
1-\gamma
}
]

由于：

[
\mathbb E[\gamma^\tau]
======================

\sum_{b'}\bar\Gamma^o_{bb'}
]

所以可以直接从 `gamma_terminal` 的 row-sum 算：

[
\boxed{
L_\gamma(b,o)
=============

\frac{
1-\sum_{b'}\bar\Gamma^o_{bb'}
}{
1-\gamma
}
}
]

于是 reward residual 的 per-discounted-step 版本是：

[
\tilde\delta_R^{\rm step}
=========================

\frac{
|\Delta R_{b,o}|
}{
R_{\rm scale} L_\gamma(b,o)+\epsilon
}
]

transition/time kernel 的相对误差可以报：

[
\tilde\delta_\Gamma^{\rm rel}
=============================

\frac{
|\Delta\Gamma_{b,o,\cdot}|*1
}{
\sum*{b'}\bar\Gamma^o_{bb'}+\epsilon
}
]

expected duration 误差可以报：

[
\tilde\delta_\tau
=================

\frac{
|\hat{\mathbb E}\tau-\bar{\mathbb E}\tau|
}{
1+\bar{\mathbb E}\tau
}
]

但我不建议把 per-step duration-normalized residual 作为主 hard threshold。原因是：一个长 targeted option 如果穿过整个 maze，它的 per-step residual 可能很小，但它仍然在隐藏全局规划。duration-normalized residual 衡量“模型平均每步准不准”；value-impact residual 衡量“对规划伤害多大”；bypass/hidden-cross 衡量“是否隐藏决策复杂度”。三者不要混在一起。

---

## 8. hidden-cross / bypass 不应该完全按 duration 归一化

对于 (B_{\rm res}^{\rm hard})，我建议使用 raw hidden mass：

[
p_{\rm hidden}(b,o)
===================

\Pr[
S_{\tau_{B_{\rm res}}}
\in
B_{\rm res}^{\rm hard}\setminus B
]
]

或者 discounted hidden mass：

[
\Gamma_{\rm hidden}(b,o)
========================

\mathbb E[
\gamma^\tau
\mathbf 1
{
S_{\tau_{B_{\rm res}}}\in B_{\rm res}^{\rm hard}\setminus B
}
]
]

不要除以 duration。

因为 hard structural hidden-cross 的语义是：

> 你是否跨过了一个必须暴露给高层的决策点？

不是：

> 你每一步平均跨过多少决策点？

如果除以 duration，一个特别长的 global option 反而可能被稀释。

对于 (B_{\rm res}^{\rm soft})，可以同时报：

[
p_{\rm hidden}
]

和：

[
\frac{
\mathbb E[
\sum_{t<\tau}
\gamma^t
\mathbf 1{S_t\in B_{\rm res}^{\rm soft}\setminus B}
]
}{
L_\gamma(b,o)
}
]

前者用于 validity / split，后者用于诊断密度。

---

## 9. 推荐的最终 residual acceptance rule

我建议 edge validity 写成：

[
\text{valid}(b,o)
=================

\mathbf 1[
p_{\rm hidden}^{\rm hard}(b,o)
\le
\epsilon_{\rm hidden}
]
]

[
\cdot
\mathbf 1[
\tilde\delta_{b,o}^{\rm value}
\le
\epsilon_{\rm value}
]
]

[
\cdot
\mathbf 1[
\tilde\delta_{\tau}(b,o)
\le
\epsilon_{\tau}
]
]

其中：

[
\tilde\delta_{b,o}^{\rm value}
==============================

\frac{
|\Delta R_{b,o}|
+
V_{\rm scale}^{\mathcal T}|\Delta\Gamma_{b,o,\cdot}|*1
}{
(1-\beta)V*{\rm scale}^{\mathcal T}
}
]

这个 rule 的好处是：

* task reward scale 由 (V_{\rm scale}^{\mathcal T}) 处理；
* discount 由 ((1-\beta)) 处理；
* option duration 通过 (\bar\Gamma) 的 row-sum 和 (L_\gamma) 进入；
* hidden planner 问题由 (p_{\rm hidden}) 单独处理，不会被 duration normalization 洗掉；
* residual 不再跟 graph complexity / option complexity 混在一起。

---

## 10. 需要注意：Bellman residual 不应该是唯一评估指标

Bellman residual / Bellman error 本身可能和真实 value error 排序不一致。Fujimoto 等人的 “Why Should I Trust You, Bellman?” 明确指出 Bellman error 在实践中可能不是 value error 的可靠替代指标，尤其在有限数据和函数近似下会出现误导。([Proceedings of Machine Learning Research][3])

所以你的实验报告最好同时有：

[
\text{normalized held-out backup residual}
]

[
\text{normalized value/planning gap}
]

[
\text{hidden-cross mass}
]

[
\text{option complexity}
]

[
\text{duration / nonlocality}
]

不要只用 residual 判胜负。

---

## 11. 我会加的 CSV 字段

每条 edge / option source row 建议输出：

```text
bres_family
bres_size
hidden_mass_prob
hidden_mass_discounted
hidden_mass_soft_density

resid_R_raw
resid_Gamma_l1
resid_backup_raw
resid_backup_value_norm
resid_reward_per_discounted_step
resid_Gamma_relative
resid_tau_relative

V_scale_task
beta_row
beta_global
L_gamma_row
expected_tau
edge_valid
split_candidate_state
split_candidate_mass
```

其中：

[
\beta_{\rm row}(b,o)
====================

\sum_{b'}\bar\Gamma^o_{bb'}
]

[
\beta_{\rm global}
==================

\max_{b,o}\beta_{\rm row}(b,o)
]

[
L_\gamma(b,o)
=============

\frac{1-\beta_{\rm row}(b,o)}{1-\gamma}
]

---

## 12. 最终实验 claim 可以这样写

不要说：

> (B_{\rm res}) 发现了真实 boundary。

更稳的是：

> We evaluate graph-option abstractions under a family of residual probe boundaries. A compact abstraction is considered robust only if it maintains low held-out value-impact residual and low hidden-cross mass across structurally defined, spectral, residual-driven, and random matched probe families.

中文就是：

> (B_{\rm res}) 不是环境的真实边界，而是一族诊断镜头。一个 compact graph 只有在多种诊断镜头下都低 residual / 低 hidden-cross，才说明它不是把复杂性藏进 option policy。

这也更贴合你之前的目标：不是证明某个 heuristic boundary 是对的，而是证明 **graph-option pair 在压缩、可预测性、局部性、SMDP consistency 之间形成了稳定 Pareto tradeoff**。Rate-distortion / information bottleneck 视角也支持这种“压缩—失真 tradeoff”的表述；相关 state abstraction 工作就是把抽象看成 compression 和 performance distortion 之间的权衡。([ojs.aaai.org][4])

[1]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/bellman_kron.py "Laplace-semi-MDP/experiments/bellman_kron.py at main · erzhu419/Laplace-semi-MDP · GitHub"
[2]: https://github.com/erzhu419/Laplace-semi-MDP/blob/main/experiments/run_ablation.py "Laplace-semi-MDP/experiments/run_ablation.py at main · erzhu419/Laplace-semi-MDP · GitHub"
[3]: https://proceedings.mlr.press/v162/fujimoto22a/fujimoto22a.pdf?utm_source=chatgpt.com "Why Should I Trust You, Bellman? The Bellman Error is a Poor ..."
[4]: https://ojs.aaai.org/index.php/AAAI/article/view/4179?utm_source=chatgpt.com "State Abstraction as Compression in Apprenticeship ..."
