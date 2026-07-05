# 我：
Profile shows group candidate scoring is negligible, cache helps only repeated boundary/probe queries, but default beam has zero cache hit because it visits fresh boundaries. Should the next main contribution target true incremental first-hit Green updates, frontier-local pruning, or a symbolic/learned surrogate for the Green-delta matrix?
# GPT：
我会把下一步主贡献押在：

[
\boxed{
\text{true incremental first-hit Green boundary-insertion update}
}
]

而不是优先做 learned surrogate。**frontier-local pruning 可以作为配套 solver 优化，但不该是主理论贡献。**

原因很直接：现在 profile 已经说明 candidate scoring 基本不是瓶颈。`candidate_score_time_sec` 大约是 (3\times 10^{-4}) 秒量级，而 `probe_green_kernel_time_sec` 和 `probe_operator_delta_time_sec` 是 (10^{-1}) 秒量级；cache-hit 版当然极快，但 default beam 访问 fresh boundaries 时 cache hit rate 是 0，所以普通 memoization 不解决主路径。你现在的 discovery profile 里 `current_frozen_operator` 相比 `full_recompute` 约 4–5.6x 快，但 `cached_incremental_first` 和 current 基本一样，只有 `cached_incremental_hit` 才出现几千倍 speedup；这说明 cache 只复用重复 query，不复用 beam tree 的父子结构。([GitHub][1]) 主 submission table 也已经把 discovery profile 聚合出来：candidate scoring 近乎可忽略，缓存命中才极快，但 fresh-boundary hit rate 为 0。([GitHub][2])

---

## 1. 三条路线的优先级

### 第一优先级：true incremental first-hit Green update

这是最值得做成下一块主贡献的方向，因为它正好击中当前瓶颈：

[
\text{fresh boundary}
\Rightarrow
\text{cache miss}
\Rightarrow
\text{重新 Green / delta}
]

而 incremental update 要做的是：

[
B
\rightarrow
B\cup{x}
]

时，不重新解一次 first-hit Green，而是从父节点的 Green object 精确更新子节点。

这不是 heuristic，而是可以证明的线性代数恒等式，和你当前的“frozen RD operator exactness”非常契合。

### 第二优先级：frontier-local pruning

这个应该做，但更像 solver 工程和 ablation。它能减少 beam 扩展、减少 exact fallback ambiguous set、减少无意义 candidate，但**如果它没有减少 Green kernel / delta 构造次数，就不会解决当前主耗时**。

所以 frontier pruning 的定位应该是：

[
\boxed{
\text{incremental Green 的配套加速层}
}
]

而不是新的核心理论主线。

### 第三优先级：symbolic / learned surrogate

我不建议现在把 learned surrogate 作为下一主贡献。它会立刻把论文从“可证明 operator + certified solver”拉回“启发式近似器”的审稿风险区。

如果要做 learned surrogate，最好只作为：

[
\boxed{
\text{proposal generator}
}
]

也就是它只负责提出候选 subset，最终 decision 仍由 certified Green / exact fallback 验证。不要让 surrogate 直接决定 split。

---

## 2. 你真正想要的不是 cache，而是 parent-to-child Green update

现在 cache 的 key 大概是：

[
(\text{boundary},\text{probe})
]

beam search 默认访问的是 fresh boundary：

[
B_0,\quad B_0\cup{x_1},\quad B_0\cup{x_2},\quad \ldots
]

这些 query 不重复，所以 hit rate 为 0 是正常的。

真正有用的复用结构不是：

[
\text{same }B\text{ again}
]

而是：

[
B'
==

B\cup{x}
]

是 (B) 的 child。

所以需要把数据结构从 memoization 改成：

[
\boxed{
\text{persistent Green state on the beam tree}
}
]

每个 beam node 保存或引用：

[
N_B=(I-P_{II})^{-1}
]

或 first-hit kernel：

[
H_B=N_B P_{IC}
]

子节点通过 boundary insertion formula 从父节点更新。

---

## 3. 关键公式：boundary insertion Green identity

设在某个 fixed option policy (o) 下，当前 terminal / boundary set 是：

[
C
]

transient set 是：

[
I=S\setminus C
]

转移矩阵分块：

[
P^o=
\begin{pmatrix}
P_{II} & P_{IC}\
P_{CI} & P_{CC}
\end{pmatrix}
]

first-hit Green / fundamental matrix 是：

[
N_C=(I-P_{II})^{-1}
]

first-hit kernel 是：

[
H_C=N_C P_{IC}
]

现在把一个 transient candidate (x\in I) 加入 boundary：

[
C' = C\cup{x}
]

令：

[
J=I\setminus{x}
]

那么有两个非常有用的 exact identities。

### Identity A：inverse deletion / Schur complement update

如果把 (N_C) 按 (x,J) 分块：

[
N_C=
\begin{pmatrix}
N_{xx} & N_{xJ}\
N_{Jx} & N_{JJ}
\end{pmatrix}
]

则新 transient inverse 是：

[
\boxed{
N_{C'}
======

## N_{JJ}

\frac{N_{Jx}N_{xJ}}{N_{xx}}
}
]

这把一次矩阵求逆变成 rank-one downdate。

### Identity B：first-hit kernel update

定义：

[
p_x(i)
======

# \Pr_i[\tau_x<\tau_C]

\frac{N_C(i,x)}{N_C(x,x)}
]

也就是从 (i) 出发，在 hit 当前 boundary (C) 之前先 hit 新 boundary (x) 的概率。

那么新 first-hit kernel 满足：

[
\boxed{
H_{C'}(i,x)=p_x(i)
}
]

并且对旧 boundary (c\in C)：

[
\boxed{
H_{C'}(i,c)
=

## H_C(i,c)

p_x(i)H_C(x,c)
}
]

直觉非常清楚：

> 原来从 (i) 到旧 boundary (c) 的 hitting probability 里，有一部分路径先经过 (x)，再从 (x) 去 (c)。现在 (x) 变成 terminal，这部分要从旧 (c) 的概率里扣掉，并转移到新 boundary (x)。

这正是你需要的 incremental first-hit Green update。

---

## 4. 这可以变成一个新 theorem，而且很干净

我建议把下一块理论写成：

### Theorem: Exact Green boundary-insertion update

给定 fixed option policy (o)、terminal set (C)、transient set (I)，假设：

[
I-P_{II}
]

可逆。令：

[
N_C=(I-P_{II})^{-1}
]

和：

[
H_C=N_C P_{IC}
]

对于任何 (x\in I)，令 (C'=C\cup{x})。则：

[
N_{C'}
======

## N_{JJ}

\frac{N_{Jx}N_{xJ}}{N_{xx}}
]

且：

[
H_{C'}(i,x)
=

\frac{N_C(i,x)}{N_C(x,x)}
]

[
H_{C'}(i,c)
=

## H_C(i,c)

\frac{N_C(i,x)}{N_C(x,x)}
H_C(x,c)
]

这个 theorem 和你现在的 frozen exactness / Green certificate 完全兼容。它不是替代 (S_{\rm RD})，而是让 (S_{\rm RD}) 在 beam tree 上增量计算。

---

## 5. 先做一个 sanity check：是否其实可以固定 (C_0) 后完全不用更新？

在实现 incremental update 前，先检查一个更简单的可能性。

如果你的 candidate universe / probe universe 是固定的：

[
C_0
]

并且 first-hit kernel 始终是：

[
K^{C_0}
=

(I-P_{II}^{C_0})^{-1}P_{IC_0}
]

那么 boundary (B\subseteq C_0) 改变时，其实 Green kernel 不需要变；变化的只是 hidden mask：

[
m_B(x)=\mathbf 1[x\in C_0\setminus B]
]

hidden mass 是：

[
h_e(B)
======

\sum_{x\in C_0\setminus B}K_e(x)
]

加入 (x) 时：

[
h_e(B\cup{x})
=

h_e(B)-K_e(x)
]

这时你甚至不需要 boundary-insertion inverse update，只需要一次全局 (C_0) Green tensor，然后后续都是 mask / vector update。

所以我建议你把 incremental 做成两层：

### Level 0：fixed-universe tensor reuse

如果 (C_0) 固定，先实现：

[
K_{e,x}
\text{ precompute once}
]

然后所有 (B) 的 delta 都用 mask 更新。

这是最便宜、最稳的精确复用。

### Level 1：true boundary-insertion update

如果 terminal set 本身随 (B) 变化，例如 first-hit terminal 就是当前 (B\cup B_{\rm res})，再用上面的 Schur / hitting update。

这两层可以一起写成：

[
\boxed{
\text{Static basis reuse when }C_0\text{ is fixed; exact insertion update when }C\text{ grows.}
}
]

---

## 6. frontier-local pruning 应该怎么接在后面？

等 incremental Green update 有了之后，frontier pruning 才会更有意义。

推荐做成 **certified active frontier**：

对每个 candidate (x)，先给一个便宜 upper bound：

[
U(x)
\ge
S_{\rm RD}(x)
]

如果：

[
U(x)<L(x_{\rm best})
]

就不展开它。

或者对 group-constrained beam：

[
U_g(x)
]

在所有 group risk 上都不可能改善 violation，就 prune。

这可以写成：

[
\boxed{
\text{safe pruning by upper bounds}
}
]

而不是 learned heuristic。

但注意：由于你当前 candidate scoring 本身已经几乎不要时间，frontier pruning 只有在它减少下面这些东西时才有价值：

[
\text{number of Green updates}
]

[
\text{number of beam children}
]

[
\text{number of exact fallback candidates}
]

[
\text{number of probe contexts}
]

如果只是减少 `score_candidates` 的行数，那收益会很小。

---

## 7. learned / symbolic surrogate 的正确位置

symbolic / learned surrogate 可以做，但最好等到 exact incremental 和 frontier pruning之后。

原因有三个：

第一，它会稀释你的主贡献。你现在最强的叙事是：

[
\boxed{
\text{provable Green operator}
+
\text{certified adaptive solver}
}
]

learned surrogate 会让审稿人回到：

[
\text{是不是又是一个 learned heuristic?}
]

第二，它需要 held-out map / probe / task 泛化实验，否则很容易被认为 overfit。

第三，它不能替代 certificate。即使 surrogate 给出 candidate rank，最终也必须：

[
\text{exact / certified Green validates decision}
]

所以 learned surrogate 的合适定位是：

[
\boxed{
\text{proposal-only acceleration}
}
]

而不是主算法。

可以以后写成：

[
\text{Surrogate proposes top }M\text{ candidates;}
\quad
\text{Green operator certifies among them.}
]

---

## 8. 下一轮实验该怎么设计

我建议新增一个 `run_incremental_green_update_check.py` 或类似脚本，输出四组 mode：

```text
full_recompute
current_frozen_operator
static_basis_reuse
boundary_insertion_update
boundary_insertion_update + frontier_prune
```

关键字段：

```text
max_kernel_error_vs_exact
max_score_error_vs_exact
selected_state_match
wall_time_sec
green_update_time_sec
operator_delta_time_sec
n_green_solves
n_green_updates
n_pruned_candidates
beam_width
beam_depth
parent_update_rate
cache_hit_rate
```

注意新增的核心指标不是 `cache_hit_rate`，而是：

```text
parent_update_rate
```

因为你要证明的是：

[
\text{fresh child boundary can be updated from parent}
]

不是：

[
\text{same query appeared again}
]

主图可以画：

[
\text{beam depth}
\quad\text{vs}\quad
\text{wall time}
]

比较：

[
\text{recompute}
]

[
\text{memo cache}
]

[
\text{incremental insertion}
]

如果 incremental update 是对的，它应该在 default beam 的 fresh-boundary setting 下也获得收益，而 memo cache 不会。

---

## 9. 审稿人视角下，三条路线的风险

| 路线                            | 优点                                  | 风险                                                      | 我建议的定位                          |
| ----------------------------- | ----------------------------------- | ------------------------------------------------------- | ------------------------------- |
| True incremental Green update | 精确、可证明、直击 fresh-boundary cache miss | 实现复杂；只在 fixed-policy / fixed-terminal semantics 下 exact | **下一主贡献**                       |
| Frontier-local pruning        | 工程收益；能减少 beam/fallback              | 如果只减少 scoring 行数，收益小；可能引入 heuristic                     | P1 solver layer                 |
| Symbolic/learned surrogate    | 长期可扩展；可能大图有用                        | 容易被说成 heuristic；需要泛化实验；破坏清晰理论线                          | Future / proposal-only ablation |

---

## 10. 最推荐的下一步 claim

不要写：

> We add a learned surrogate to predict good boundaries.

也不要先写：

> We prune the frontier heuristically.

建议写：

> We derive an exact boundary-insertion update for first-hit Green kernels. This converts beam expansion from repeated Green solves on fresh boundary sets into parent-to-child Green updates. The update is a Schur-complement identity, preserves the frozen RD marginal exactly under fixed option policies, and composes with the existing top-set/fallback certificates.

中文就是：

[
\boxed{
\text{下一主贡献：把 Green operator 从“每个 boundary 重新算”升级成“beam tree 上精确增量更新”。}
}
]

然后 frontier pruning 接在后面：

[
\boxed{
\text{有了 incremental Green state 后，再做 safe frontier pruning，减少需要生成的 child states。}
}
]

learned surrogate 放后面：

[
\boxed{
\text{只作为 proposal-only future work。}
}
]

---

## 11. 最短答案

是的，下一主贡献应该优先做 **true incremental first-hit Green updates**。

原因是：

[
\text{candidate scoring negligible}
]

[
\text{ordinary cache misses on fresh beam nodes}
]

[
\text{dominant cost is Green / delta construction}
]

而 incremental Green boundary insertion 正好把：

[
B\rightarrow B\cup{x}
]

从“新 query”变成“父节点精确 update”。

frontier-local pruning 是第二步，用来减少 child expansion 和 fallback set；learned / symbolic surrogate 先不要主推，除非它只作为 proposal 并由 Green certificate 验证。

[1]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/discovery_profile_cache/summary.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/submission_main_table/summary.md "raw.githubusercontent.com"
