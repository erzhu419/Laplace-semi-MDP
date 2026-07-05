我看完最新公开 main 后，整体判断是：**理论和诊断已经很强，离“可投稿版本”差的不是再加一个大 theorem，而是把主线、实现、输出和可复现实验对齐。** 现在最容易被审稿人抓住的地方是：**文档叙事比公开脚本/summary 走得更快**。

## 现在最缺的 5 件事，按优先级排

### P0-1：把 top-set exact fallback 真正落到主输出里

你最新 notes 里已经写得很清楚：主实现应该是 “Certified Adaptive Green with top-set exact fallback”，并且声称 fallback rows 是 `4/8`、final certified decisions 是 `8/8`。但公开的 `adaptive_green_certification/summary.md` 仍然只显示：

[
\text{exact top-1 matches}=8/8,\quad
\text{interval-certified top-1}=4/8
]

并且 uncertified rows 仍标记为 `needs_refinement_or_exact_fallback`，没有 `fallback_used`、`ambiguous_set_size`、`final_certified`、`total_time_with_fallback` 这些字段。([GitHub][1])

更关键的是，notes 说 `run_adaptive_green_certification.py` 已实现 top-set fallback，但我在公开 raw 脚本里没有看到 `fallback` 相关逻辑；`find("fallback")` 对该脚本也没有匹配。([GitHub][2]) 这会让审稿人觉得你“论文说主算法有 fallback，但 artifact 表还停在 pure adaptive 诊断阶段”。

这里应该立刻补一个最终主表版本：

```text
adaptive_top
exact_top
interval_certified
fallback_used
ambiguous_set_size
fallback_exact_time_sec
total_time_with_fallback_sec
final_top
final_certified
final_decision
speedup_vs_full_exact_with_fallback
```

然后把主表改成：

[
\boxed{
\text{Certified Adaptive Green + top-set exact fallback}
}
]

而不是现在 summary 里隐含的 pure adaptive Green。

---

### P0-2：Lean proof claim 和 notes claim 需要同步

`RDOperatorReal.lean` 里我能直接看到的是 `weightedScore_error_le` 和 `interval_certified_top_choice`，它证明的是“分离的 score intervals 能 certify approximate top choice equals exact top choice”。([GitHub][3]) 但 notes 里进一步写了 proof layer now includes：

```text
top_set_exact_fallback_global_optimal
top_set_exact_fallback_beats_outside
```

并说 fallback step 不只是 implementation convention。([GitHub][4])

如果这些 theorem 已经本地存在但没 push，要 push；如果只是 notes 先写了，必须补到 `RDOperatorReal.lean` 或把 notes 改成 “planned theorem / order argument”。否则审稿人会看到一个 mismatch：

[
\text{paper/notes claim: top-set fallback theorem}
]

但 artifact 里可见 theorem 只有：

[
\texttt{interval_certified_top_choice}
]

我建议把 fallback theorem 写成非常朴素的 order theorem，不需要复杂数学：

[
A={x: U_x \ge \max_z L_z}
]

若 (x^*=\arg\max_{x\in A}S_{\rm exact}(x))，且

[
S_{\rm exact}(x^*) > \max_{y\notin A} U_y,
]

则 (x^*) 是全局 exact top-1。这个 theorem 很容易 Lean 化，也会让主算法更可信。

---

### P0-3：顶层 README / paper-facing entry point 还缺

repo 顶层没有可用的 `README.md`，raw README 访问是 404；GitHub root 也显示 “No description”。 ([GitHub][5])

现在 proof 子目录有 README、lakefile、lean-toolchain，并且已经写了 Lean 的运行方式。([GitHub][6]) 但顶层还需要一个“审稿人 5 分钟能跑通”的入口：

```text
README.md
requirements.txt / pyproject.toml
scripts/reproduce_core.sh
scripts/reproduce_proofs.sh
scripts/reproduce_certificates.sh
```

README 里建议只写四条主线：

1. **Theory check**: frozen FD exactness, Lean proof.
2. **Main algorithm**: certified adaptive Green + top-set exact fallback.
3. **Main benchmark**: core / large-scale compression.
4. **Appendix diagnostics**: weighted spectral, conditioned rational certificate, lens validation.

现在目录里实验脚本很多，output 也很多，审稿人容易迷路。需要一个“读这个，不要读旧 ablation”的导航。

---

### P0-4：主实验表需要统一成 submission-facing 版本

你现在有很多很好的输出，但它们分散：

* `core_benchmark` 仍然是 exact first-boundary kernels，并报告 best planning-only speedup 295.4x、worst graph start-value gap 0.04973。([GitHub][7])
* `large_scale_compression_adaptive` 已经是 adaptive Green，并显示 max states 144、best total speedup 10.68x、best planning-only speedup 4097x、worst start-value gap 0.07851。([GitHub][8])
* `adaptive_green_certification` 是 score interval 检查，但还没有 fallback 主表。([GitHub][1])
* `weighted_spectral_certificate` 和 `conditioned_weighted_certificate` 是 proof/certificate appendix。([GitHub][9])

现在缺一个真正的 **Main Table**：

```text
method:
  full_vi
  exact_green_rd
  certified_adaptive_green_rd
  fixed_K_green_rd
  eigenoptions
  betweenness
  coverage
  random

columns:
  map/slip
  |S|, |B|, compression
  construction_time
  kernel_time
  smdp_solve_time
  total_time
  planning_speedup
  total_speedup
  start_gap
  success_rate
  hidden_audit_cvar
  interval_certified
  fallback_used
  final_certified
```

主结论应该围绕这张表说：

[
\boxed{
\text{Exact Green 是 reference；Certified Adaptive Green 是主实现；fixed-K 是 ablation；weighted spectral 是 sufficient certificate appendix。}
}
]

这会比现在几十个输出目录更像一篇论文。

---

### P0-5：把“weighted spectral certificate”的地位写低一点，但保留为强附录

你现在 weighted spectral 层很漂亮：row (q<1) 在 summary 里是 0/16，但 weighted (q<1) 是 16/16，这证明它确实比 raw row certificate 更强。([GitHub][9]) 你又进一步做了 conditioned/rational audit，summary 写明它用 `Fraction` 验证 rounded inequality (P_{II}w \le q w)，且 corridor / open-room / maze / four-rooms 都有 condition-cap frontier。([GitHub][10])

但它仍然不应该当主 runtime certificate。原因也被你的结果清楚展示了：corridor K=128 下 conditioned/unconditioned weighted tail bound 仍然远大于 actual tail；例如 cap (10^{12}) 时 corridor bound 约 124.5，而 actual tail 约 0.9758。([GitHub][10])

所以论文表述应固定为：

[
\boxed{
\text{weighted spectral certificate = sufficient theorem / reproducibility audit}
}
]

[
\boxed{
\text{frontier-tail score interval + exact fallback = runtime decision procedure}
}
]

不要让审稿人以为你主算法依赖 ill-conditioned Collatz weights。

---

## P1：强烈建议补，但不是 blocker

### 1. Solver-validity 输出需要变成公开主表

notes 里说 `run_solver_validity.py` 已比较 exhaustive oracle、operator-only greedy/beam、exact-refined beam，并给出 compact run：

[
14/18 \text{ exact boundary matches},\quad
14/18 \text{ zero violation-gap rows},\quad
15/18 \text{ feasibility matches}.
]

这正是“adaptive solver 不是启发式堆料”的关键证据。([GitHub][4]) 但我打开 `experiments/output/solver_validity/summary.md` 时没有看到可读的完整表。([GitHub][11])

建议把 solver-validity 作为论文主实验之一：

```text
small-map exhaustive oracle
operator-only beam
exact-refined beam
group-constrained beam
```

并报告：

```text
oracle_match
feasibility_match
violation_gap
adaptive_regret
beam_width
expanded_candidates
```

这比单纯说 “we use beam search” 强很多。

---

### 2. Group-constrained RD 的结果很好，但还需要一版 larger / adaptive-Green 主表

`rd_group_constrained` 结果显示 group-constrained beam 在 maze_9 和 four_rooms_9 上能用更少 vertices 达到 feasibility，而 scalar mean/CVaR 会违反全部 groups；scalar max 也可行但通常边界更多。([GitHub][12])

这已经能支撑：

[
\boxed{
\text{group constraints are not cosmetic; they change the feasible solution.}
}
]

但当前表主要是小图。建议再跑一版：

```text
maze_13
four_rooms_11
open_room_12
slip 0 / 0.05
certified adaptive Green + fallback
```

哪怕只跑一张精简表，也能让 “adaptive group-constrained beam search” 更像主算法，而不是 diagnostic。

---

### 3. Held-out probe / multi-probe 结果要“诚实收敛”

`rd_multiprobe_basis` 结果很有用，但也很危险：它显示 fixed basis + single 有时 test=0，而 mean / mean_cvar / max 反而会在 maze_9 上出现 test_mean 178.8 / test_cvar 357.6；residual_train basis 也有明显 held-out gap。([GitHub][13])

`rd_lens_validation` 也显示 leave-one-lens-out 下有些 lenses 对 mean_cvar 很难，max/group_max 更稳但不是全局完美。([GitHub][14])

这部分不要包装成“robust objective 已解决泛化”。更稳的结论是：

[
\boxed{
\text{single-probe RD exactness does not imply cross-probe generalization;}
}
]

[
\boxed{
\text{group constraints and minimax-like risks are necessary diagnostics, but probe design remains a limitation.}
}
]

这其实会增加论文可信度。

---

### 4. 文档里的 “remaining proof work” 要更新成最新状态

proof README 现在已经列出 weighted spectral-radius certificate、bits-curvature layer、real finite-matrix layer等内容，并把 optional work 写成 Mathlib spectrum API 和 `HasSum`/`tsum` infinite-tail formulation。([GitHub][6])

但 `rd_boundary_green_operator_notes.md` 里还有一些历史段落，比如 “A Mathlib-real instantiation remains the next formalization step”，后面又说 Real layer 已经完成很多。([GitHub][4]) 建议把 notes 分成：

```text
Current paper claims
Historical diagnostics
Future work
```

否则审稿人读到前后不一致，会怀疑 artifact 状态。

---

## P2：可以放进 appendix / future work

### 1. conditioned rational certificate 不必继续加强

你已经做到 `Fraction` audit，summary 也说明它验证 rounded inequality (P_{II}w \le q w)，并显示 rational max violation 是 0。([GitHub][10]) 这已经足够作为 appendix strengthening。

不要再为了 tightness 继续陷在 weighted certificate。corridor 证明了：rational verification 证明的是“证书成立”，不是“证书紧”。主算法应该仍靠 frontier-tail + fallback。

### 2. arbitrary-goal multitask 暂时不要主 claim

notes 里已经诚实写了 all-state goal variant 是 negative control，25 sampled goals 时 graph 变太 dense，corridor_64 / maze_13 的 speedup 小于 1。([GitHub][4])

因此主 claim 应该是：

[
\boxed{
\text{boundary / reward-family amortization}
}
]

而不是：

[
\text{arbitrary interior-goal multitask speedup}
]

---

## 我建议最终投稿前的最小 action list

1. **实现或公开同步 top-set exact fallback**：`run_adaptive_green_certification.py` 里实际加入 ambiguous top-set exact scoring，summary 输出 `final_certified=8/8`。现在公开 summary 仍是 `4/8` interval-certified 且需要 fallback。([GitHub][1])

2. **Lean proof 同步 fallback theorem**：如果 notes 里说有 `top_set_exact_fallback_*`，那 proof 文件里也要有；否则删掉该 claim。当前可见 Real proof明确有 interval-certified top-choice theorem。([GitHub][3])

3. **生成一张 submission-facing Main Table**：用 certified adaptive Green + fallback 做主实现，fixed-K / exact / baselines 作为 columns 或 rows。

4. **把 solver-validity 输出变成正式表**：尤其是 exact-refined beam vs exhaustive oracle 的 14/18、15/18 这组结果，应该在 artifact 中可直接打开。([GitHub][4])

5. **加顶层 README**：说明运行环境、核心命令、主要输出、哪些表是论文主表、哪些是历史 ablation。现在顶层 README 不存在/不可访问。

6. **统一 claim hierarchy**：

[
\boxed{
\text{Theorem: frozen RD Green exact finite difference}
}
]

[
\boxed{
\text{Solver: adaptive group-constrained beam / exact-refined beam}
}
]

[
\boxed{
\text{Implementation: certified adaptive Green + fallback}
}
]

[
\boxed{
\text{Appendix certificate: weighted / conditioned spectral certificate}
}
]

---

## 当前最强的论文故事

你现在已经可以讲一个很强、很严谨的故事：

> We formulate graph-option abstraction as a constrained multi-probe rate-distortion boundary problem. For a frozen graph-option model, the RD Boundary Green Operator is exactly the finite-difference marginal of the frozen RD objective. Adaptive construction changes the objective, so we use the operator as a certified local proposal inside a group-constrained exact-refined beam solver. Exact Green is the reference operator; adaptive Green is the main tail-certified implementation; unseparated score intervals trigger top-set exact fallback. Weighted spectral certificates provide an additional sufficient proof layer, but the runtime decision certificate is frontier-tail score intervals plus fallback.

中文压缩版：

[
\boxed{
\text{定理是 frozen operator；算法是 drift-aware constrained solver；实现是 certified adaptive Green + fallback。}
}
]

现在缺的不是“再发明一块理论”，而是**把这个故事在代码、输出、README、主表、Lean theorem 名称上完全对齐**。这一步做完，就很像一个可投的 artifact 了。

[1]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/adaptive_green_certification/summary.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/run_adaptive_green_certification.py "raw.githubusercontent.com"
[3]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/proof/RDOperatorReal.lean "raw.githubusercontent.com"
[4]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/markdown/rd_boundary_green_operator_notes.md "raw.githubusercontent.com"
[5]: https://github.com/erzhu419/Laplace-semi-MDP "GitHub - erzhu419/Laplace-semi-MDP · GitHub"
[6]: https://github.com/erzhu419/Laplace-semi-MDP/tree/main/proof "Laplace-semi-MDP/proof at main · erzhu419/Laplace-semi-MDP · GitHub"
[7]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/core_benchmark/summary.md "raw.githubusercontent.com"
[8]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/large_scale_compression_adaptive/summary.md "raw.githubusercontent.com"
[9]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/weighted_spectral_certificate/summary.md "raw.githubusercontent.com"
[10]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/conditioned_weighted_certificate/summary.md "raw.githubusercontent.com"
[11]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/solver_validity/summary.md "raw.githubusercontent.com"
[12]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/rd_group_constrained/summary.md "raw.githubusercontent.com"
[13]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/rd_multiprobe_basis/summary.md "raw.githubusercontent.com"
[14]: https://raw.githubusercontent.com/erzhu419/Laplace-semi-MDP/main/experiments/output/rd_lens_validation/summary.md "raw.githubusercontent.com"
