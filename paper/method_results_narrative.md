# Method And Results Narrative Draft

This file is a paper-facing prose scaffold. It can be expanded into the Methods,
Results, and Discussion sections without changing the technical claim hierarchy.

## One-Sentence Argument

In finite tabular navigation tasks, we show that a boundary graph can compress
noncritical regions into first-boundary SMDP edges while keeping Bellman-relevant
state distinctions auditable, using a proof-backed rate-distortion Green
operator and a practical adaptive feasible top-k discovery backend, supported by
paired fixed-top-k diagnostics, compression scaling, fair option baselines,
multi-task reward relabeling, and Lean-checked operator certificates.

## Terminology Ledger For This Section

| Canonical term | First-use definition | Boundary |
|---|---|---|
| RD Boundary Green Operator | Frozen rate-distortion finite-difference score induced by first-hit Green kernels. | It scores candidate insertions under a fixed candidate universe, option family, and edge-weight model. |
| Boundary graph | Compressed graph whose vertices are selected boundary states and whose directed edges are first-boundary SMDP options. | It is not claimed to preserve the primitive MDP under arbitrary option families. |
| Adaptive feasible top-k refinement | Main discovery backend that scans candidates ordered by the frozen/surrogate score and stops when a group-feasible split is certified, up to cap `K`. | It certifies feasible discovery, not RD-optimal split selection. |
| Fixed top-k refinement | Ablation that refines every candidate in the same top-`K` prefix. | It defines the feasible envelope used to audit adaptive top-k. |
| Score-interval dominance | Optional stronger certificate in which the selected candidate's lower score bound beats every other candidate's upper bound. | Needed only for score-optimality claims. |

## Methods Draft

### Problem formulation

We study finite discounted MDPs in which local transitions are known and planning
over all primitive states can be unnecessarily expensive. The objective is not
to discover options as an end in itself, but to identify a small set of boundary
states `B` that should remain explicit graph vertices. The remaining states are
represented through option-labeled first-boundary edges: starting from a
boundary state, an option traverses the primitive environment until it reaches
the next boundary state, at which point the graph-SMDP planner applies a
Bellman backup on `B`. This separates two questions that are often conflated:
the first-boundary SMDP reduction can be exact for a fixed boundary and option
family, while the choice of `B` determines how much task-relevant structure the
graph has retained.

### RD Boundary Green Operator

For a fixed boundary graph, candidate set, option library, local rate cost, and
edge-weight model, the RD Boundary Green Operator scores a candidate state by a
frozen finite difference of a local rate-distortion objective. The distortion
term is computed from first-hit Green kernels: for each active boundary edge,
the kernel records the probability or discounted mass with which that edge
would first hit a candidate state before reaching the next boundary. Inserting a
candidate into `B` splits the affected first-boundary edge and reduces hidden
mass or audit distortion, but it also increases the graph rate by adding a new
vertex and incident option edges. The frozen score is therefore a local
trade-off between rate increase and distortion reduction.

This operator is the mathematical reference object of the paper. The proof
layer shows that the frozen score is exactly the finite difference of the fixed
local objective; that the first-hit Green kernel is a legal finite absorbing
chain object; that truncated/adaptive Green approximations are controlled by
Neumann-tail certificates; and that the resulting graph-SMDP Bellman operator is
a contraction under finite option actions and discount less than one. These
claims are deliberately local: they do not assert that a fully adaptive solver,
which may rebuild options, edge weights, or active-edge occupancies after each
split, globally optimizes the same frozen objective.

### Group-constrained boundary selection

A scalar distortion can hide failures in one diagnostic lens by averaging them
against success in another. We therefore use group-constrained RD as the robust
boundary-selection objective. Topological, value-gradient, and stochastic
transition distortions are tracked as separate groups, and a boundary graph is
accepted only when each group satisfies its budget. This design makes failures
auditable: if the method fails in an open room or stochastic maze, the output
identifies which group constraint remains violated instead of reporting a single
opaque scalar risk.

### Adaptive feasible top-k refinement

The main discovery backend is adaptive feasible top-k refinement. At each
boundary-selection step, candidates are ordered by the frozen RD/surrogate
proposal score. Rather than refining all candidates in a fixed top-`K` prefix,
the adaptive backend refines candidates sequentially and stops once an exact or
certified group-feasible split is found, with fallback to the full cap `K` if no
feasible candidate is certified earlier. The fixed top-`K` refinement baseline
uses the same candidate order, feasibility oracle, and cap, but evaluates the
entire prefix before selecting.

This distinction is important for the claim. Adaptive feasible top-k has the
same feasible envelope as fixed top-`K` under a shared candidate order and
feasibility oracle: it succeeds if and only if some candidate in that prefix is
feasible, and it never refines more than `K` candidates. It is therefore a
feasible-discovery backend, not a proof that the first feasible candidate is the
highest-scoring feasible candidate. Score-optimality inside the prefix requires
a stronger interval-dominance certificate, where the selected candidate's lower
score bound exceeds the upper score bound of every remaining candidate. We
report this distinction explicitly and treat fixed top-`K` as the ablation that
defines the envelope.

## Results Draft

### Boundary graphs preserved planning behavior while compressing the state space

The large-scale compression experiments compared full-state value iteration with
graph-SMDP planning on boundary graphs across corridors, open rooms, four rooms,
and maze maps under deterministic and stochastic transitions. The results
separate planning-only speedup from total wall-clock cost. Planning on the graph
was substantially cheaper when the boundary set stayed small, with the strongest
planning compression in long corridors where the graph represents an entire
corridor segment as one first-boundary edge. Total single-task speedups were
more conservative because graph discovery and Green-kernel construction are
upfront costs; the paper therefore reports break-even task counts and
multi-task amortized speedups rather than hiding the discovery cost.

### Adaptive feasible top-k matched the fixed top-4 feasible envelope with fewer refinements

The adaptive top-k diagnostics directly tested the solver-wrapper claim. Across
the paired XL discovery suite, adaptive top-k and fixed top-4 agreed on
feasibility for all paired rows (`36/36`). In the certified mode, adaptive top-k
matched fixed top-4's feasible rate (`0.7222`) while reducing median selection
time from `47.18 s` to `23.58 s`. The same table showed zero proxy regret
against the fixed top-4 final graph on the reported objective tuple and a
median fixed-over-adaptive selection speedup of `1.913x`. The k-used histogram
explained the speedup: many successful steps stopped at `k=1`, while difficult
stochastic cases exhausted the cap and therefore paid the same cost as fixed
top-4.

These diagnostics support using adaptive feasible top-k as the main discovery
backend. They also bound the claim. The result says that adaptive top-k matches
the fixed-prefix feasible envelope under the tested candidate order and oracle;
it does not say that early feasible stopping is a general score-optimal split
oracle. The score-optimal version is available only when interval dominance is
certified, and should be reported separately if used.

### Group constraints exposed failures instead of hiding them

The larger group-constrained adaptive table showed that endpoint-only boundary
sets can leave substantial hidden distortion even when the graph is extremely
small. Group-constrained and incremental variants reduced these violations on
the open-room, four-room, and maze settings used in the larger adaptive table.
The adaptive top-k failure-mode table further localized the remaining failures:
one class reached the cap or boundary budget without satisfying every group, and
another exhausted positive feasible gains in stochastic open-room or four-room
cases. These are useful negative results because they distinguish insufficient
candidate/envelope coverage from a failure of the first-boundary reduction
itself.

### Fixed-B reward relabeling preserved multi-task compression

The multi-task experiments were designed to avoid a misleading all-goals
protocol that promotes every interior reward state into the boundary set and
therefore destroys compression by construction. Instead, fixed-`B` reward
relabeling stores edge discounted-occupancy kernels and reuses the same boundary
graph across many additive rewards. This preserves graph topology while changing
only edge rewards, and it is the correct setting for the compression claim.
Terminal interior goals were handled separately with event-hit kernels and a
goal-conditioned local option extension. The event-kernel gap is reported as
option/boundary restriction bias rather than hidden inside the main compression
metric; the goal-conditioned extension reduces this gap without adding the goal
to `B`, but pays a query-time policy and batched event-solve cost.

### Fair-budget baselines clarify what the method is, and is not, optimizing

The fair-budget frontier compares full MDP planning, RD boundary graphs,
group-constrained RD, eigenoption-style spectral baselines, betweenness
bottlenecks, random landmarks, coverage landmarks, and tabular option baselines
under a shared map/slip/rate vocabulary. This prevents a misleading comparison
in which one method is allowed many more graph vertices or option endpoints than
another. The role of these baselines is not to show that the RD graph dominates
every option method on every performance metric. The stronger claim is that it
offers an auditable compression objective: rate, occupancy/value/audit
distortions, hidden boundary crossing, and planning gap are all measured in the
same table.

## Discussion Draft

The central contribution is a proof-backed graph abstraction objective for
finite SMDP planning. Classical option discovery asks which temporally extended
actions might improve control, whereas the present method asks which primitive
states must remain explicit vertices so that the rest of the state space can be
compressed into first-boundary edges. This reframing makes compression, value
distortion, hidden boundary structure, and upfront discovery cost measurable in
one pipeline.

The strongest runtime lesson is that exact recomputation is not the right
implementation story. Exact Green kernels and fixed top-`K` refinement are
reference and ablation objects. The practical backend combines certified
adaptive Green approximations, group-wise feasibility checks, incremental or
surrogate proposal scoring, and adaptive feasible top-k refinement. The
adaptive top-k theorem and paired diagnostics give this backend a precise
meaning: it preserves the fixed-prefix feasible envelope while avoiding
unnecessary refinements, but it does not certify score optimality unless the
stronger interval dominance condition is met.

The current boundary of the claim is finite known-model environments. The method
does not yet solve sample-based deep RL, and single-task wall-clock speed can be
unfavorable when discovery cost dominates planning. The evidence is strongest
for planning compression and multi-task amortization, especially when fixed-`B`
reward relabeling avoids adding every reward state as a graph vertex. The main
open technical path is to make the proposal/operator layer cheaper and more
predictive at larger scales while preserving the auditability that distinguishes
the method from a black-box option discovery heuristic.

## Claim-Evidence Map

| Claim | Evidence | Status |
|---|---|---|
| Adaptive feasible top-k can be the main discovery backend. | Paired diagnostics: feasible match `36/36`, certified feasible rate `0.7222`, median selection time `23.58 s` vs fixed top-4 `47.18 s`. | supported |
| Adaptive feasible top-k is not an RD-optimal split oracle. | Lean `AdaptiveTopK.lean` includes interval-dominance theorem and feasible-only counterexample. | supported as boundary |
| The RD Boundary Green Operator is the reference mathematical object. | Lean finite-difference, Green legality, Neumann tail, Bellman contraction, and value-gap theorems. | supported |
| Compression is the main story, not universal single-task speed. | Submission table separates planning-only speedup, total speedup, break-even tasks, and multi-task amortization. | supported |
| Fixed-`B` reward relabeling preserves multi-task compression. | Edge reward multitask table and theorem stack T10/T11. | supported |

## Writing Notes

- The main story is compression-oriented graph abstraction, not universal dominance over option discovery.
- Adaptive top-k can be the main backend, but the guarantee is feasible-envelope preservation rather than RD-optimal split selection.
- Fixed top-4 is the ablation/reference envelope; score optimality requires interval dominance.
- The results narrative should always separate planning-only speedup, single-task total speedup, and multi-task amortized speedup.
