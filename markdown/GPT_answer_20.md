# 我：
我又更新了repo，遇到的新问题是：adaptive top-k feasible-only certificate 在 XL 表里达到 fixed top-4 同等 feasible rate，但中位 discovery time 约减半。论文里能否把它作为 main discovery backend，把 fixed top-k 作为 ablation？还需要补什么 theorem/experiment 来支撑这个 adaptive stopping rule？”

# GPT：
可以把 **adaptive top-k feasible-only certificate** 升级为 **main discovery backend**，并把 fixed top-4 放成 ablation。
但论文里必须把它的保证说清楚：

[
\boxed{
\text{它是 feasible-discovery backend，不是 full RD-optimal split oracle。}
}
]

你现在的数据已经足够支持这个定位：在 `discovery_acceleration_table.csv` 里，`adaptive_topk_certified_refine` 和 fixed `surrogate_topk_certified_refine, top_k=4` 的 feasible rate 都是 `0.7222`，但 median selection time 从 fixed top-4 的约 `47.18s` 降到 adaptive top-k 的约 `23.58s`；median upfront time 也从约 `47.39s` 降到约 `23.76s`。同时 adaptive top-k 的 median used-k 是 `1.0`、max used-k 是 `4.0`，说明它多数时候不需要真的扫满 fixed top-4。([GitHub][1])

所以最稳的主线是：

[
\boxed{
\text{Reference objective: exact/frozen RD Green}
}
]

[
\boxed{
\text{Main discovery backend: adaptive feasible top-k refine}
}
]

[
\boxed{
\text{Ablation: fixed top-k refine}
}
]

[
\boxed{
\text{Optional stronger mode: score-certified adaptive top-k}
}
]

---

## 1. 能不能作为 main discovery backend？

**可以。** 但它的名字和 claim 要避免过强。

不要写：

> adaptive top-k finds the same best RD split as fixed top-4.

除非你有 score-optimality certificate。

应该写：

> adaptive top-k matches the fixed top-(K_{\max}) feasible discovery envelope while avoiding unnecessary refinements. It stops once a feasible certified split is found, and falls back to at most (K_{\max}) refinements.

这句话和数据一致：adaptive top-k 和 fixed top-4 feasible rate 一样是 `13/18` 左右，但 median selection time 大约减半；它的 total refined candidates 是 `95`，而 fixed top-4 certified refine 是 `174`。([GitHub][1])

更重要的是，你的 README 当前已经把 exact Green 放成 reference operator，把 certified adaptive Green/tie-set/epsilon certificates 放成 runtime implementation，把 fixed-K 和 weighted spectral 放成 ablation/appendix，这个 hierarchy 已经和“adaptive backend 主用、fixed top-k 消融”一致。([GitHub][2])

---

## 2. 需要补的核心 theorem：Adaptive top-k feasible equivalence theorem

这个 theorem 很简单，但非常关键。它能把 adaptive top-k 从“工程剪枝”变成“有明确语义的 solver wrapper”。

设候选序列由 proposal/operator 排序：

[
x_1,x_2,\dots,x_n.
]

设 hard/group feasibility predicate 为：

[
F(x)\in{0,1},
]

并且每个 (F(x)) 是通过 exact/certified refinement 得到的。

固定 top-(K) baseline 的 feasible success 定义为：

[
\exists j\le K: F(x_j)=1.
]

adaptive feasible top-k 算法从 (j=1) 开始依次 refine，直到遇到第一个 feasible candidate 或达到 (K_{\max})。

### Theorem A: Feasible envelope equivalence

若 adaptive top-k 与 fixed top-(K_{\max}) 使用同一个候选顺序、同一个 feasibility oracle、同一个 (K_{\max})，则：

[
\boxed{
\text{Adaptive succeeds}
\iff
\text{Fixed top-}K_{\max}\text{ contains at least one feasible candidate.}
}
]

并且 adaptive 的 refine 数为：

[
\boxed{
N_{\rm refine}
==============

\min{j\le K_{\max}:F(x_j)=1}
}
]

若不存在 feasible candidate，则：

[
N_{\rm refine}=K_{\max}.
]

所以：

[
\boxed{
N_{\rm refine}^{\rm adaptive}\le K_{\max}
=========================================

N_{\rm refine}^{\rm fixed}.
}
]

这个 theorem 正好解释你当前结果：adaptive top-k feasible rate 和 fixed top-4 一样，但 refine/selection time 更低。([GitHub][1])

---

## 3. 需要补的第二个 theorem：feasible-only 不等于 score-optimal

这个要主动写出来，防止审稿人攻击。

### Proposition B: Feasible-only stopping does not certify best feasible RD score

如果 adaptive 在第一个 feasible candidate (x_j) 处停止，它只保证：

[
F(x_j)=1.
]

它**不保证**：

[
x_j=\arg\max_{i\le K_{\max},F(x_i)=1} S_{\rm RD}(x_i).
]

除非额外满足 score stopping condition：

[
L(x_j)\ge \max_{i>j, i\le K_{\max}} U(x_i),
]

其中 (L,U) 是 certified score interval。

所以论文要区分两个模式：

[
\boxed{
\text{adaptive feasible mode}
}
]

和：

[
\boxed{
\text{adaptive score-certified mode}
}
]

前者追求“找到可行 split”；后者追求“在 top-(K) envelope 内找到 score-certified best split”。

你现在问的是 “feasible-only certificate”，所以主 claim 应该围绕 feasible discovery，不要把它包装成 RD-optimal selection。

---

## 4. 推荐的算法表述

主算法可以写成：

```text
AdaptiveFeasibleTopK(B, candidates, Kmax):
    sort candidates by proposal / RD surrogate / frozen operator score
    for j = 1..Kmax:
        x = candidates[j]
        refine x with certified/exact feasibility oracle
        if x satisfies group/hard constraints:
            return x, certified_feasible=True, k_used=j
    return failure, certified_feasible=False, k_used=Kmax
```

然后 fixed top-(K) ablation 是：

```text
FixedTopK(B, candidates, K):
    refine all candidates[1:K]
    return best feasible among them, if any
```

这两个算法的关系非常清楚：

* fixed top-(K) 是 exhaustive refinement over a prefix；
* adaptive top-k 是 early stopping over the same prefix；
* feasible rate 一样；
* adaptive runtime 更低，当 feasible rank 通常小于 (K)。

---

## 5. 还需要补什么实验？

### A. Paired feasibility equivalence table

现在 aggregate 已经显示 adaptive top-k 和 fixed top-4 feasible rate 同为 `0.7222`。但建议补一个 row-level paired table：

```text
map
slip
seed / task
fixed_top4_feasible
adaptive_topk_feasible
match
adaptive_k_used
fixed_k
selected_candidate_rank
```

目标是显示：

[
\boxed{
\text{feasible match}=18/18
}
]

或者至少说明 mismatch 全部来自候选顺序/feasibility oracle差异，而不是 stopping rule 本身。

如果 theorem 的条件满足，应该是 100% match。

### B. k-used histogram

现在 aggregate 只有 median used-k `1.0`、max used-k `4.0`。([GitHub][1])
建议加 histogram：

```text
k_used=1: ...
k_used=2: ...
k_used=3: ...
k_used=4: ...
cap_hit_without_feasible: ...
```

这张图会非常直观地解释为什么 median time 减半：大多数 feasible split 在前 1–2 个 candidate 就出现了。

### C. Fixed-K sweep vs adaptive cap

你已经有 fixed top-k ablation：top-k (1,2,4,8,16)。结果显示 certified refine 在 top-4 和 top-8 都是 `0.7222` feasible rate，top-16 反而是 `0.6667`；fixed top-4 selection time 约 `47.18s`，top-8 约 `73.07s`，top-16 约 `132.20s`。([GitHub][1])

建议论文里只放简化版：

| Method         | K/cap | feasible rate | median selection time | refined candidates |
| -------------- | ----: | ------------: | --------------------: | -----------------: |
| fixed top-1    |     1 |           ... |                   ... |                ... |
| fixed top-2    |     2 |           ... |                   ... |                ... |
| fixed top-4    |     4 |         0.722 |                47.18s |                174 |
| adaptive top-k | cap 4 |         0.722 |                23.58s |                 95 |

这能证明 adaptive stopping 不是靠降低 feasible rate 换时间。

### D. Feasible-only vs score-certified mode

建议补一个小 ablation：

```text
adaptive_feasible_stop
adaptive_score_certified_stop
fixed_top4_best_feasible
fixed_top4_best_score_certified
```

报告：

```text
feasible_rate
score_regret_vs_fixed_top4_best_feasible
selection_time
group_violation
start_gap
```

如果 adaptive feasible stop 的 score regret 很小，那你可以更放心地把它作为 main backend。
如果 regret 有时大，就写清楚：

> main backend optimizes feasible discovery; score-optimality is available through score-certified mode at higher cost.

### E. Failure-mode table

当前 adaptive top-k feasible rate 只有 `0.7222`，不是 1。([GitHub][1])
所以要解释剩下 `5/18` 失败是：

1. cap 内没有 feasible candidate；
2. proposal ordering missed feasible candidate；
3. candidate universe insufficient；
4. group constraints too strict；
5. feasibility oracle failed due to approximation.

这张表能防止审稿人问：“为什么不是 100% feasible？”

---

## 6. 和 group-constrained adaptive table 的关系

你现在 larger group-constrained adaptive table显示 `group_constrained_incremental` 在 open_room/four_rooms/maze 的 slip 0 和 0.05 上都是 feasible，而且相比普通 `group_constrained` selection time 明显降低：比如 maze_13 slip 0 从 `5.23s` 降到 `0.676s`，open_room_12 slip 0 从 `3.39s` 降到 `1.49s`，four_rooms_11 slip 0 从 `2.04s` 降到 `0.908s`。([GitHub][3])

这张表和 adaptive top-k 的关系是：

* `group_constrained_incremental` 证明 incremental backend 在 larger group suite 可行；
* adaptive top-k 证明 discovery refinement 可以 early-stop，减少 candidate refinement；
* 两者可以合成最终 practical backend：

[
\boxed{
\text{incremental score update}
+
\text{adaptive feasible top-k refine}
}
]

所以论文里可以把 adaptive top-k 作为 main discovery backend，并把普通 group_constrained、fixed top-k、exact group RD 都放进消融。

---

## 7. 论文里的准确 claim

建议这样写：

> We use adaptive feasible top-k refinement as the main discovery backend. It scans candidates ordered by the frozen RD/surrogate proposal score and refines them until a hard/group-feasible split is certified, up to a fixed cap (K_{\max}). This has the same feasible envelope as fixed top-(K_{\max}) refinement but can stop earlier. In our XL discovery table, adaptive top-k matches fixed top-4 feasible rate while roughly halving median discovery time.

这句话完全符合当前数据。([GitHub][1])

不要写：

> adaptive top-k recovers the same best split as fixed top-4.

除非你补了 score-certified theorem和实验。

---

## 8. 最小 theorem set

你需要补三个小 theorem / proposition 就够：

### Theorem 1: Feasible-envelope equivalence

[
\text{AdaptiveFeasibleTopK succeeds}
\iff
\exists j\le K_{\max}:F(x_j)=1.
]

### Theorem 2: Refinement work bound

[
N_{\rm refine}^{\rm adaptive}
=============================

\min(\operatorname{rank}*{\rm first feasible},K*{\max})
\le K_{\max}
============

N_{\rm refine}^{\rm fixed}.
]

因此，如果 candidate refinement dominates runtime，adaptive expected time is:

[
\mathbb E[T_{\rm adaptive}]
\le
\mathbb E[N_{\rm refine}],t_{\rm refine}
+
T_{\rm proposal}.
]

### Proposition 3: Score-optimality requires interval dominance

If you want best feasible score inside the cap, adaptive can stop only when:

[
L(x_{\rm best})\ge \max_{y\in \text{unrefined cap}}U(y).
]

Otherwise it is feasible-only, not score-optimal.

这三个定理足够支撑 adaptive stopping rule。

---

## 9. 最终判断

[
\boxed{
\text{可以把 adaptive top-k feasible-only certificate 作为 main discovery backend。}
}
]

[
\boxed{
\text{fixed top-4 应该作为 ablation。}
}
]

但要明确：

[
\boxed{
\text{main guarantee = same feasible envelope as fixed cap + fewer refinements}
}
]

而不是：

[
\text{same RD-optimal selected split}.
]

最需要补的不是大实验，而是：

1. paired fixed-top4 vs adaptive-topk row-level equivalence；
2. k-used histogram；
3. score-regret vs fixed top-4 best-feasible；
4. failure-mode breakdown；
5. 三个简单 theorem：feasible equivalence、work bound、score-optimal stopping condition。

做完这些，adaptive top-k 就不是“启发式 early stop”，而是一个有明确定义、有定理、有配对实验的 main discovery backend。

[1]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/submission_main_table/discovery_acceleration_table.csv "raw.githubusercontent.com"
[2]: https://github.com/erzhu419/Laplace-semi-MDP "GitHub - erzhu419/Laplace-semi-MDP · GitHub"
[3]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/submission_main_table/group_constrained_adaptive_table.csv "raw.githubusercontent.com"
