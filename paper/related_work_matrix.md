# Related Work Matrix

This matrix uses the local `reference/` folder as the citation source. It is a drafting guide, not a final BibTeX file.

| Topic | Representative local references | What they give us | Gap this paper targets |
|---|---|---|---|
| Options and SMDPs | `options_framework_1999...pdf`, `option_critic_architecture_2016...pdf` | Options induce SMDP models with termination and cumulative discounted rewards. | They do not decide which primitive states must become graph vertices under a compression-distortion objective. |
| Laplacian/eigenoption discovery | `laplacian_option_discovery_2017...pdf`, `laplacian_eigenmaps_2001...pdf`, `diffusion_maps_coarse_graining_2006...pdf` | Spectral geometry can propose directions, landmarks, and diffusion coordinates. | Standard Laplacians are not Bellman/reward-aware enough to certify boundary graph compression. |
| Graph neural spectral foundations | `chebnet_2016...pdf`, `gcn_2017...pdf` | Laplacian spectral filtering motivates explicit operators and approximation theory. | These operators act on observed graph signals, not first-hit option reductions of MDP regions. |
| Kron/Schur graph reduction | `kron_reduction_graphs_2013...pdf` | Schur complements explain why eliminating interior nodes can preserve boundary behavior. | Classical Kron reduction does not include option rewards, discounting, or MDP distortion constraints. |
| State abstraction and bisimulation | `smdp_homomorphisms_2003...pdf`, `bisimulation_metrics_continuous_mdp_2011...pdf`, `markov_state_abstractions_2021...pdf`, `value_preserving_state_action_abstractions_2020...pdf` | Abstraction must preserve reward and transition behavior, often with value-preserving guarantees. | These works focus on equivalence/aggregation; our focus is selecting a sparse boundary graph with auditable hidden structure. |
| Rate-distortion and information-theoretic abstraction | `rate_distortion_learning_2021...pdf`, `state_abstraction_compression_2019...pdf`, `mdl_principle_coding_modeling_1998...pdf` | Compression should be traded against task distortion and description length. | They do not provide a first-hit Green operator for where to split an MDP region into graph vertices. |
| Replay-buffer/world graph planning | `world_graphs_hrl_2019...pdf`, `world_model_as_graph_2021...pdf`, `sptm_2018...pdf`, `sorb_2019...pdf`, `planning_goal_conditioned_policies_2019...pdf` | Graphs over states or observations support planning and goal-conditioned control. | These graph edges are usually learned reachability links, not certified first-boundary kernels with explicit hidden-boundary audits. |
| Bellman residual caution | `bellman_residual_bad_proxy_2017...pdf`, `why_trust_bellman_2022...pdf` | Bellman residuals and value errors require careful interpretation. | This motivates reporting residual-to-value-gap certificates and not overclaiming scalar residual improvements. |

## Drafting Rule

Each related-work paragraph should end with a technical distinction:

1. Spectral methods propose geometry; RD Boundary Green scores Bellman-relevant boundary compression.
2. Option discovery proposes temporally extended actions; our method asks which states must remain graph vertices.
3. State abstraction preserves MDP behavior under equivalence or approximate metrics; our method builds a sparse graph-SMDP under explicit rate and audit constraints.
4. Graph-world planning builds useful planning graphs; our contribution is a proof-backed first-hit kernel and distortion certificate for the graph construction.
