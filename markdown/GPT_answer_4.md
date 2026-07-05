# 我：
如果 value-impact residual 会把长 option 的结构隐藏问题稀释掉，那 raw structural residual 应该怎么归一化，才能不靠 magic number，同时又不被 duration normalization 洗掉。

# GPT：
结论：**raw structural residual 不应该按 duration 归一化，也不应该乘 (\gamma^\tau)。**
它应该被定义成一个**undiscounted first-hit event risk**，然后用**reference / null calibration** 或 **MDL split criterion** 来归一化。这样既没有魔法阈值，也不会因为 option 很长而被洗掉。

我能从公开 `main` 看到的是：现在 ablation 已经有 `bypass_cost_total`、`nonlocal_cost`、`policy_tv_total`、`policy_regions_total`，并且 `description_length_proxy` 已经把 graph cost、option-pair cost、policy TV/regions、bypass 和 nonlocal reachability 放进同一个复杂度代理里；report 也明确写了 targeted option 会测试“很粗 graph + 很强 option model”的上限，但可能把复杂性藏进 option policy。([GitHub][1])

---

## 1. 不要把 structural residual 当成 value residual

value-impact residual 是：

[
|\Delta R|
+
V_{\text{scale}}|\Delta \Gamma|_1
]

这里 (\Gamma) 本身是：

[
\Gamma_{bb'}^o
==============

\mathbb E[\gamma^\tau \mathbf 1{S_\tau=b'}]
]

所以长 option 天然会被 (\gamma^\tau) 压小。这个对**value error**是合理的，但对**结构隐藏**不合理。

结构隐藏关心的是：

> 这个 option 是否跨过了一个本该暴露给 abstract planner 的 diagnostic boundary？

这件事不应该因为它发生在 40 步以后就被折扣掉。
所以 structural residual 应该使用：

[
\gamma_{\text{struct}} = 1
]

而不是 task discount (\gamma)。

---

## 2. 主定义：undiscounted first-hidden-boundary probability

给当前 graph boundary：

[
B
]

给 residual diagnostic boundary：

[
B_{\text{res}}
]

隐藏诊断边界是：

[
H = B_{\text{res}}\setminus B
]

对一个 edge / option row：

[
e=(b,o)
]

定义 first diagnostic hit time：

[
\tau_{\text{res}}
=================

\inf
{t\ge 1:
S_t\in (B\setminus{b})\cup H
}
]

注意这里排除了 source (b)，否则 slip / self-loop 会导致 (t=0) 或 (t=1) 在原地误判终止。

raw structural residual 定义为：

[
\boxed{
\rho_{\text{struct}}(b,o)
=========================

\Pr[
S_{\tau_{\text{res}}}\in H
\mid
S_0=b,o
]
}
]

这就是最核心的量。

它有几个好处：

1. 取值天然在 ([0,1])，不依赖 reward scale；
2. 不使用 (\gamma^\tau)，所以不会被 long option 稀释；
3. 不除以 duration，所以不会变成 per-step hazard；
4. deterministic case 下非常清楚：跨过 hidden boundary 就是 1，不跨就是 0；
5. stochastic case 下它表示“这个 option 有多少概率先撞到 hidden residual boundary”。

这不是 duration-normalized hazard：

[
\frac{\Pr[\text{hidden hit}]}{\mathbb E[\tau]}
]

而是 cumulative incidence：

[
\Pr[\text{hidden hit before explicit boundary}]
]

这点很关键。**hazard 会洗掉长 option；cumulative incidence 不会。**

---

## 3. 用 Schur complement 算它，但用 (\gamma=1)

设：

[
A_e=(B\setminus{b})\cup H
]

[
I_e=S\setminus A_e
]

source (b) 被放在 transient set (I_e) 里，而不是 absorbing set 里。

在 option policy (o) 诱导的 primitive transition matrix (P^o) 下：

[
P^o=
\begin{pmatrix}
P_{II}^o & P_{IA}^o\
P_{AI}^o & P_{AA}^o
\end{pmatrix}
]

first-hit distribution 到 (A_e) 是：

[
\boxed{
F^o_{I\to A}
============

(I-P_{II}^o)^{-1}P_{IA}^o
}
]

然后取 source row：

[
f_{b,o}(a)
==========

F^o_{b,a}
]

于是：

[
\boxed{
\rho_{\text{struct}}(b,o)
=========================

\sum_{h\in H}
f_{b,o}(h)
}
]

这就是一个 **undiscounted structural Schur complement**。它和 Bellman-Kron 的形式一致，但不是 Bellman value kernel；它是 first-hit structural kernel。

如果有 finite-horizon rollout 或有不终止概率，可以同时记录：

[
p_{\text{hit}}(b,o)
===================

\sum_{a\in A_e} f_{b,o}(a)
]

[
p_{\text{nohit}}(b,o)=1-p_{\text{hit}}(b,o)
]

然后 structural hidden ratio 可以报：

[
\rho_{\text{hidden}\mid\text{hit}}
==================================

\frac{
\sum_{h\in H}f_{b,o}(h)
}{
p_{\text{hit}}+\epsilon
}
]

但 validity 里不要让 no-hit 被吞掉。最好分开：

[
\rho_{\text{struct}}
====================

p_{\text{hidden}}
]

[
\rho_{\text{nonterm}}
=====================

p_{\text{nohit}}
]

hidden-cross 和 nontermination 是两种不同失败。

---

## 4. 归一化不要除 duration，而要做 reference calibration

(\rho_{\text{struct}}) 本身已经是 dimensionless probability。真正的问题不是“量纲”，而是“什么值算大”。

不要手写：

[
\rho_{\text{struct}}>0.1
]

这种 magic number。

更好的做法是给每个 map / slip / (B_{\text{res}})-family 构造一个 reference distribution：

[
\mathcal R_{\text{ref}}
=======================

{
\rho_{\text{struct}}(e):
e\in E_{\text{known-local}}
}
]

其中 (E_{\text{known-local}}) 可以来自：

* all-boundary directional options；
* first-boundary local targeted options；
* (B=B_{\text{res}}) 时的 legal local edges；
* random matched local edges；
* human-free topology local edges，例如相邻 junction-to-junction edge。

然后定义 reference upper leakage：

[
\rho_0
======

Q_{1-\alpha}
(
\mathcal R_{\text{ref}}
)
]

例如取 95% 或 99% 分位。这里 (\alpha) 是统计置信水平，不是 task-scale magic number。

归一化 structural residual：

[
\boxed{
\tilde\rho_{\text{struct}}(b,o)
===============================

\left[
\frac{
\rho_{\text{struct}}(b,o)-\rho_0
}{
1-\rho_0
}
\right]_+
}
]

解释：

* (\tilde\rho=0)：不比合法 local reference 更坏；
* (\tilde\rho=1)：几乎必然先撞 hidden boundary；
* deterministic exact model 里，通常 (\rho_0=0)，所以 (\tilde\rho=\rho)。

如果是 sample-based rollout，进一步用置信区间：

[
\text{invalid}
\iff
\operatorname{LCB}
(\rho_{\text{struct}})

>

\operatorname{UCB}
(\rho_0)
]

这样 threshold 来自数据不确定性，而不是手调常数。

---

## 5. 更强的归一化：用 structural bits / surprisal

如果你不想做 hard threshold，可以把 structural hiding 变成 MDL cost：

[
\boxed{
C_{\text{struct-bits}}(b,o)
===========================

-\log_2
\left(
1-\tilde\rho_{\text{struct}}(b,o)+\epsilon
\right)
}
]

直觉：

* 没有 hidden-cross：(\rho=0)，cost = 0；
* hidden-cross 概率 0.5，cost = 1 bit；
* hidden-cross 概率 0.9，cost (\approx 3.32) bits；
* deterministic hidden-cross：(\rho=1)，cost 近似无穷，等价 hard invalid。

这个比 raw penalty 更自然，因为它可以和“新增一个 graph node 的编码成本”比较。

新增一个 boundary node 的描述长度可以粗略写成：

[
C_{\text{add-node}}
===================

\log_2 |S|
+
C_{\text{incident-edges}}
]

然后 split rule 可以是：

[
\boxed{
\sum_{e}
d(e)
C_{\text{struct-bits}}(e;h)

>

C_{\text{add-node}}(h)
}
]

其中 (d(e)) 可以是 abstract policy occupancy，也可以是 uniform library weight。

这就把问题变成：

> 继续隐藏这个 residual boundary 的编码代价，是否已经超过显式加入它的编码代价？

这比“hidden_mass > 0.05 就 split”更干净。

---

## 6. 如果想区分“跨过一个 hidden point”和“跨过很多 hidden points”

first-hit probability 会饱和。比如跨过 1 个 hidden boundary 和跨过 10 个 hidden boundaries，在 deterministic case 下：

[
\rho_{\text{struct}}=1
]

都一样。

所以建议同时加一个 **distinct hidden boundary exposure**，但仍然不要按 duration 归一化。

对每个 hidden candidate (h\in H)，定义：

[
p_h(b,o)
========

\Pr[
T_h<T_{B\setminus{b}}
\mid
S_0=b,o
]
]

然后：

[
\boxed{
N_{\text{hidden}}(b,o)
======================

\sum_{h\in H}
p_h(b,o)
}
]

这个量表示“期望暴露了多少个不同 hidden residual boundaries”。

它不是：

[
\mathbb E\left[\sum_{t<\tau}\mathbf 1{S_t\in H}\right]
]

后者会被停留时间、循环、duration 放大。

更好的 severity cost 是：

[
\boxed{
C_{\text{hidden-distinct}}(b,o)
===============================

\sum_{h\in H}
-\log_2(1-p_h(b,o)+\epsilon)
}
]

这个量会区分：

* 只擦到一个 hidden boundary；
* 穿过一串 hidden decision points；
* global targeted option 一路穿过整个 maze。

但它仍然不是 duration-normalized。

---

## 7. soft (B_{\text{res}}) 的情况：用 saturated hit，不用累计时间

如果 (B_{\text{res}}) 不是 binary set，而是 saliency map：

[
c_{\text{res}}(s)\in[0,1]
]

不要用：

[
\mathbb E
\left[
\sum_{t<\tau} c_{\text{res}}(S_t)
\right]
]

作为主 structural residual。这个会混入 duration。

更稳的是 saturated hit probability：

[
\boxed{
\rho_{\text{soft}}(b,o)
=======================

\mathbb E
\left[
1-
\prod_{t<\tau_B}
(1-c_{\text{res}}(S_t))
\right]
}
]

binary 情况下它退化为：

[
\Pr[\text{hit hidden residual boundary before explicit boundary}]
]

soft 情况下它表示：

> 这条 option trajectory 是否遇到过任何高 residual saliency 区域？

它不会因为在同一个区域停留 20 步就线性变大，也不会除以 duration 被洗掉。

实现上可以更简单：把 (c_{\text{res}}) 取 top-(q) quantile 变成若干 (B_{\text{res}}^{(q)})，然后对多个 (q) 报 (B_{\text{res}})-sensitivity curve。

---

## 8. 推荐最终指标组合

我建议你把 structural residual 分成 4 个字段：

[
\texttt{struct_hidden_prob}
===========================

\rho_{\text{struct}}
]

[
\texttt{struct_hidden_norm}
===========================

\tilde\rho_{\text{struct}}
]

[
\texttt{struct_hidden_bits}
===========================

-\log_2(1-\tilde\rho_{\text{struct}}+\epsilon)
]

[
\texttt{struct_hidden_distinct}
===============================

\sum_{h\in H}p_h
]

再加两个诊断字段：

[
\texttt{struct_nohit_prob}
==========================

p_{\text{nohit}}
]

[
\texttt{bres_family}
\in
{
\text{topo},
\text{spectral},
\text{residual},
\text{random-matched},
\text{all}
}
]

主 hard validity rule：

[
\boxed{
\text{edge valid}
\iff
\tilde\rho_{\text{struct}}\approx 0
\quad\text{and}\quad
p_{\text{nohit}}\approx 0
\quad\text{and}\quad
\tilde\delta_{\text{value}}\le \epsilon_{\text{value}}
}
]

如果是 exact deterministic tabular model：

[
\tilde\rho_{\text{struct}}>0
\Rightarrow
\text{invalid}
]

如果是 stochastic / sampled model：

[
\operatorname{LCB}
(\rho_{\text{struct}})

>

\operatorname{UCB}
(\rho_0)
\Rightarrow
\text{invalid}
]

---

## 9. 和 value-impact residual 的分工

最终不要试图把两者合成一个 residual。

应该是双通道：

[
\boxed{
\text{value-impact residual}
}
]

回答：

> 这个 reduced edge 的 reward / discounted terminal kernel 误差会不会影响 value？

[
\boxed{
\text{raw structural residual}
}
]

回答：

> 这个 option 有没有跳过本该显式出现在 graph 上的 diagnostic boundary？

因此：

* value residual 可以按 (\gamma)、(V_{\text{scale}})、(\beta=\mathbb E[\gamma^\tau]) 归一化；
* structural residual 不应该按 (\gamma) 或 duration 归一化；
* structural residual 只做 first-hit probability、reference calibration、MDL bits。

这也避免 Bellman residual 自己当唯一质量指标。Bellman residual 和 value / policy quality 的关系在近似场景下并不总是可靠，相关工作也专门讨论过 Bellman residual 是否是好 proxy 的问题。([NeurIPS Papers][2])

---

## 10. 最简洁的实现版本

可以先实现这个版本：

```python
def first_hit_structural_residual(P_policy, src, B, B_res, eps=1e-12):
    """
    Undiscounted first-hit structural residual.
    Source src is NOT absorbing.
    Terminal diagnostic set is (B - {src}) union (B_res - B).
    """
    n = P_policy.shape[0]
    B = set(B)
    B_res = set(B_res)
    H = sorted(B_res - B)
    A = sorted((B - {src}) | set(H))

    if not A:
        return {
            "struct_hidden_prob": 0.0,
            "struct_nohit_prob": 1.0,
            "first_hit_dist": {},
        }

    I = sorted(set(range(n)) - set(A))
    i_pos = {s: k for k, s in enumerate(I)}
    a_pos = {s: k for k, s in enumerate(A)}

    P_II = P_policy[np.ix_(I, I)]
    P_IA = P_policy[np.ix_(I, A)]

    N = np.linalg.solve(np.eye(len(I)) - P_II, P_IA)
    f = N[i_pos[src], :]  # first-hit distribution over A

    hidden_prob = sum(float(f[a_pos[h]]) for h in H if h in a_pos)
    hit_prob = float(np.sum(f))
    nohit_prob = max(0.0, 1.0 - hit_prob)

    return {
        "struct_hidden_prob": hidden_prob,
        "struct_nohit_prob": nohit_prob,
        "first_hit_dist": {a: float(f[a_pos[a]]) for a in A},
    }
```

然后 calibration：

```python
def normalize_structural_prob(p_hidden, p_ref_upper):
    if p_ref_upper >= 1.0:
        return 0.0
    return max(0.0, (p_hidden - p_ref_upper) / (1.0 - p_ref_upper))
```

MDL bits：

```python
def structural_bits(p_norm, eps=1e-12):
    return -np.log2(max(eps, 1.0 - p_norm))
```

---

## 11. 一句话总结

**raw structural residual 的正确归一化不是除以 duration，而是：**

[
\boxed{
\text{undiscounted first-hidden-boundary probability}
\rightarrow
\text{reference-calibrated excess probability}
\rightarrow
\text{MDL bits / split cost}
}
]

也就是：

[
\boxed{
\rho_{\text{struct}}
====================

\Pr[
\text{first }B_{\text{res}}\cup B\text{ hit is in }B_{\text{res}}\setminus B
]
}
]

[
\boxed{
\tilde\rho_{\text{struct}}
==========================

\left[
\frac{\rho_{\text{struct}}-\rho_0}{1-\rho_0}
\right]_+
}
]

[
\boxed{
C_{\text{struct}}
=================

-\log_2(1-\tilde\rho_{\text{struct}}+\epsilon)
}
]

这样它不靠 task reward scale，不靠 (\gamma)，不靠 option duration，也不会让 global targeted option 因为“每步平均看起来还好”而逃掉。

[1]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/run_ablation.py "raw.githubusercontent.com"
[2]: https://papers.neurips.cc/paper_files/paper/2017/file/e0ab531ec312161511493b002f9be2ee-Paper.pdf?utm_source=chatgpt.com "Is the Bellman residual a bad proxy?"
