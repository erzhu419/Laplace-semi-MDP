# RD Operator Generalization

- recipe: `learned_rd_surrogate_joint_occ2_audit2`
- methods: `rd_fd, raw_hidden, random, spectral, betweenness, value_gradient`
- residual_probes: `train_recipe, all, turn_articulation, value_gradient`
- heldout_goal_count: 1
- elapsed_sec: 21.137

## Summary

- four_rooms_9 betweenness: mean_bits=23.39, heldout_goal_bits=22.330880427963407, probe_bits=28.99576871072783, mean_start_gap=0.06601, max_start_gap=0.08843
- four_rooms_9 random: mean_bits=22.9, heldout_goal_bits=21.685541488630903, probe_bits=28.23103397922047, mean_start_gap=0.06601, max_start_gap=0.08843
- four_rooms_9 raw_hidden: mean_bits=47.37, heldout_goal_bits=38.30097498131736, probe_bits=63.130887743524035, mean_start_gap=0.06592, max_start_gap=0.08826
- four_rooms_9 rd_fd: mean_bits=47.37, heldout_goal_bits=38.30097498131736, probe_bits=63.130887743524035, mean_start_gap=0.06592, max_start_gap=0.08826
- four_rooms_9 spectral: mean_bits=23.41, heldout_goal_bits=22.32638492008916, probe_bits=29.006991297557487, mean_start_gap=0.06601, max_start_gap=0.08843
- four_rooms_9 value_gradient: mean_bits=31.07, heldout_goal_bits=21.99727561691777, probe_bits=39.94022832065945, mean_start_gap=0.06592, max_start_gap=0.08826
- maze_9 betweenness: mean_bits=109.9, heldout_goal_bits=64.27730816429248, probe_bits=146.48661365536952, mean_start_gap=0, max_start_gap=0
- maze_9 random: mean_bits=50.1, heldout_goal_bits=3.041256723237823, probe_bits=66.79942628753415, mean_start_gap=0, max_start_gap=0
- maze_9 raw_hidden: mean_bits=4.104e+08, heldout_goal_bits=410365844.55709124, probe_bits=547154458.9285668, mean_start_gap=22.92, max_start_gap=23.29
- maze_9 rd_fd: mean_bits=4.104e+08, heldout_goal_bits=410365844.55709124, probe_bits=547154458.9285668, mean_start_gap=22.92, max_start_gap=23.29
- maze_9 spectral: mean_bits=38.91, heldout_goal_bits=0.0999352657366371, probe_bits=51.88416092809302, mean_start_gap=0, max_start_gap=0
- maze_9 value_gradient: mean_bits=118.1, heldout_goal_bits=80.76756311693144, probe_bits=157.48011695792763, mean_start_gap=0, max_start_gap=0
- open_room_7 betweenness: mean_bits=28.4, heldout_goal_bits=19.75163105330913, probe_bits=37.86793842965705, mean_start_gap=0.09347, max_start_gap=0.1372
- open_room_7 random: mean_bits=28.4, heldout_goal_bits=19.75163105330913, probe_bits=37.86793842965705, mean_start_gap=0.09347, max_start_gap=0.1372
- open_room_7 raw_hidden: mean_bits=28.4, heldout_goal_bits=19.75163105330913, probe_bits=37.86793842965705, mean_start_gap=0.09347, max_start_gap=0.1372
- open_room_7 rd_fd: mean_bits=28.4, heldout_goal_bits=19.75163105330913, probe_bits=37.86793842965705, mean_start_gap=0.09347, max_start_gap=0.1372
- open_room_7 spectral: mean_bits=28.4, heldout_goal_bits=19.75163105330913, probe_bits=37.86793842965705, mean_start_gap=0.09347, max_start_gap=0.1372
- open_room_7 value_gradient: mean_bits=28.4, heldout_goal_bits=19.75163105330913, probe_bits=37.86793842965705, mean_start_gap=0.09347, max_start_gap=0.1372
