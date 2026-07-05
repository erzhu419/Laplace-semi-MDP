# Fixed Basis Multi-Probe RD

- recipe: `learned_rd_surrogate_joint_occ2_audit2`
- train_probes: `junction, bottleneck`
- test_probes: `turn_articulation, combined, value_gradient`
- risk_kinds: `single, mean, mean_cvar, max`
- elapsed_sec: 32.974

## Summary

- maze_9 fixed single: B=5/17, train_mean=0, test_mean=0, test_cvar=0, gap=0, start_gap_max=0
- maze_9 fixed mean: B=5/17, train_mean=2.733e-07, test_mean=178.8, test_cvar=357.6, gap=178.8, start_gap_max=0
- maze_9 fixed mean_cvar: B=5/17, train_mean=2.733e-07, test_mean=178.8, test_cvar=357.6, gap=178.8, start_gap_max=0
- maze_9 fixed max: B=5/17, train_mean=2.733e-07, test_mean=178.8, test_cvar=357.6, gap=178.8, start_gap_max=0
- maze_9 residual_train single: B=5/10, train_mean=2.05e-07, test_mean=129.5, test_cvar=194.3, gap=129.5, start_gap_max=0
- maze_9 residual_train mean: B=5/10, train_mean=2.051e-07, test_mean=197.9, test_cvar=415.8, gap=197.9, start_gap_max=0
- maze_9 residual_train mean_cvar: B=5/10, train_mean=2.051e-07, test_mean=197.9, test_cvar=415.8, gap=197.9, start_gap_max=0
- maze_9 residual_train max: B=5/10, train_mean=2.051e-07, test_mean=197.9, test_cvar=415.8, gap=197.9, start_gap_max=0
- four_rooms_9 fixed single: B=5/28, train_mean=0, test_mean=0, test_cvar=0, gap=0, start_gap_max=0
- four_rooms_9 fixed mean: B=5/28, train_mean=145.8, test_mean=126.2, test_cvar=171.1, gap=-19.62, start_gap_max=0
- four_rooms_9 fixed mean_cvar: B=5/28, train_mean=226.4, test_mean=147, test_cvar=198.3, gap=-79.42, start_gap_max=0
- four_rooms_9 fixed max: B=5/28, train_mean=0, test_mean=0, test_cvar=0, gap=0, start_gap_max=0
- four_rooms_9 residual_train single: B=5/54, train_mean=29.72, test_mean=28.25, test_cvar=29.61, gap=-1.472, start_gap_max=0
- four_rooms_9 residual_train mean: B=5/54, train_mean=145.9, test_mean=62.46, test_cvar=67.27, gap=-83.44, start_gap_max=0
- four_rooms_9 residual_train mean_cvar: B=5/54, train_mean=145.9, test_mean=62.46, test_cvar=67.27, gap=-83.44, start_gap_max=0
- four_rooms_9 residual_train max: B=5/54, train_mean=68.21, test_mean=65.09, test_cvar=68.25, gap=-3.127, start_gap_max=0
- open_room_7 fixed single: B=5/14, train_mean=4.932, test_mean=2.597e-06, test_cvar=7.655e-06, gap=-4.932, start_gap_max=0
- open_room_7 fixed mean: B=5/14, train_mean=4.932, test_mean=2.597e-06, test_cvar=7.655e-06, gap=-4.932, start_gap_max=0
- open_room_7 fixed mean_cvar: B=5/14, train_mean=4.932, test_mean=2.597e-06, test_cvar=7.655e-06, gap=-4.932, start_gap_max=0
- open_room_7 fixed max: B=5/14, train_mean=196.9, test_mean=119.9, test_cvar=173, gap=-77, start_gap_max=0
- open_room_7 residual_train single: B=5/47, train_mean=28.46, test_mean=22.1, test_cvar=29.61, gap=-6.361, start_gap_max=0
- open_room_7 residual_train mean: B=5/47, train_mean=40.64, test_mean=31.02, test_cvar=46.99, gap=-9.619, start_gap_max=0
- open_room_7 residual_train mean_cvar: B=5/47, train_mean=40.64, test_mean=31.02, test_cvar=46.99, gap=-9.619, start_gap_max=0
- open_room_7 residual_train max: B=5/47, train_mean=40.64, test_mean=31.02, test_cvar=46.99, gap=-9.619, start_gap_max=0
