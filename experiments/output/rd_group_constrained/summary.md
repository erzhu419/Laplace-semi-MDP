# Group-Constrained RD

- lens_groups: `topology:junction,bottleneck,turn_articulation,betweenness; value:value_gradient; stochastic:transition_entropy`
- group_risk_kind: `cvar`
- budget_fracs: `0.25, 0.5`
- score_mode: `reduction`
- beam_width: 4
- elapsed_sec: 135.705

## Summary

- maze_9 group_constrained eps=0.25: B=3/17, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=feasible
- maze_9 scalar_mean_cvar eps=0.25: B=7/17, feasible=False, groups_ok=0, total_violation=1598, max_violation=598.7, test_cvar=255.7, stop=fixed_splits
- maze_9 scalar_max eps=0.25: B=7/17, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=fixed_splits
- maze_9 group_constrained eps=0.5: B=3/17, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=feasible
- maze_9 scalar_mean_cvar eps=0.5: B=7/17, feasible=False, groups_ok=0, total_violation=1540, max_violation=579.3, test_cvar=255.7, stop=fixed_splits
- maze_9 scalar_max eps=0.5: B=7/17, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=fixed_splits
- four_rooms_9 group_constrained eps=0.25: B=5/28, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=feasible
- four_rooms_9 scalar_mean_cvar eps=0.25: B=7/28, feasible=False, groups_ok=0, total_violation=1291, max_violation=558.9, test_cvar=355.6, stop=fixed_splits
- four_rooms_9 scalar_max eps=0.25: B=7/28, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=fixed_splits
- four_rooms_9 group_constrained eps=0.5: B=5/28, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=feasible
- four_rooms_9 scalar_mean_cvar eps=0.5: B=7/28, feasible=False, groups_ok=0, total_violation=1233, max_violation=539.5, test_cvar=355.6, stop=fixed_splits
- four_rooms_9 scalar_max eps=0.5: B=7/28, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=0, stop=fixed_splits
- open_room_7 group_constrained eps=0.25: B=7/14, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=7.407e-06, stop=feasible
- open_room_7 scalar_mean_cvar eps=0.25: B=7/14, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=7.407e-06, stop=fixed_splits
- open_room_7 scalar_max eps=0.25: B=7/14, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=3.538e-10, stop=fixed_splits
- open_room_7 group_constrained eps=0.5: B=7/14, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=7.407e-06, stop=feasible
- open_room_7 scalar_mean_cvar eps=0.5: B=7/14, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=7.407e-06, stop=fixed_splits
- open_room_7 scalar_max eps=0.5: B=7/14, feasible=True, groups_ok=3, total_violation=0, max_violation=0, test_cvar=3.538e-10, stop=fixed_splits
