# Compression Scaling

Generated: 2026-07-05T09:41:34
map_specs = ['corridor:16,32,64', 'open_room:6,10', 'four_rooms:7,11', 'maze:9,13']
methods = ['endpoints', 'betweenness_sqrt', 'eigenoptions_sqrt', 'turn_articulation']
gamma = 0.97, slip = 0.05

Exact first-boundary kernels are built once, then graph/SMDP planning propagates value over compressed boundary vertices and option edges.

| map | method_spec | method | n_states | n_boundary | state_compression_ratio | memory_compression_ratio | full_vi_time_sec | construction_time_sec | kernel_time_sec | smdp_solve_time_sec | planning_time_speedup_vs_full_vi | total_time_speedup_vs_full_vi | backup_compression_ratio | start_gap | occupancy_struct_hidden_distinct | struct_hidden_distinct_cvar95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_16 | endpoints | endpoints | 16 | 2 | 8 | 92 | 0.01004 | 5.404e-06 | 0.002297 | 8.583e-05 | 117 | 4.205 | 576 | 3.809041970725957e-11 | 0.0 | 0.0 |
| corridor_16 | betweenness_sqrt | betweenness_4 | 16 | 4 | 4 | 13.14 | 0.009158 | 0.0004718 | 0.006968 | 0.001852 | 4.946 | 0.9856 | 9.6 | 2.4725110847612086e-11 | 0.0 | 0.0 |
| corridor_16 | eigenoptions_sqrt | eigenoptions_4 | 16 | 4 | 4 | 11.5 | 0.009196 | 0.0002425 | 0.006869 | 0.002395 | 3.839 | 0.9673 | 7.385 | 2.332356530132529e-11 | 0.0 | 0.0 |
| corridor_16 | turn_articulation | turn_articulation | 16 | 2 | 8 | 92 | 0.009144 | 0.0001932 | 0.002114 | 8.322e-05 | 109.9 | 3.825 | 576 | 3.809041970725957e-11 | 0.0 | 0.0 |
| corridor_32 | endpoints | endpoints | 32 | 2 | 16 | 188 | 0.02956 | 6.664e-06 | 0.00412 | 9.253e-05 | 319.5 | 7.005 | 1824 | 2.091127271341975e-11 | 0.0 | 0.0 |
| corridor_32 | betweenness_sqrt | betweenness_6 | 32 | 6 | 5.333 | 8.952 | 0.02975 | 0.001261 | 0.02466 | 0.006939 | 4.287 | 0.9053 | 7.37 | 1.4097167877480388e-11 | 0.0 | 0.0 |
| corridor_32 | eigenoptions_sqrt | eigenoptions_6 | 32 | 6 | 5.333 | 8.952 | 0.02965 | 0.0002465 | 0.02457 | 0.008742 | 3.391 | 0.8835 | 5.656 | 1.8953727476400672e-11 | 0.0 | 0.0 |
| corridor_32 | turn_articulation | turn_articulation | 32 | 2 | 16 | 188 | 0.02955 | 0.0002681 | 0.003883 | 9.049e-05 | 326.5 | 6.967 | 1824 | 2.091127271341975e-11 | 0.0 | 0.0 |
| corridor_64 | endpoints | endpoints | 64 | 2 | 32 | 380 | 0.1005 | 8.857e-06 | 0.008929 | 8.485e-05 | 1184 | 11.14 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| corridor_64 | betweenness_sqrt | betweenness_8 | 64 | 8 | 8 | 8.837 | 0.1034 | 0.004239 | 0.08974 | 0.01941 | 5.328 | 0.9119 | 8.515 | 1.829647544582258e-11 | 0.0 | 0.0 |
| corridor_64 | eigenoptions_sqrt | eigenoptions_8 | 64 | 8 | 8 | 10.27 | 0.1019 | 0.0006557 | 0.08633 | 0.02759 | 3.694 | 0.8895 | 5.869 | 2.952660338451096e-11 | 0.0 | 0.0 |
| corridor_64 | turn_articulation | turn_articulation | 64 | 2 | 32 | 380 | 0.1017 | 0.0004846 | 0.008824 | 9.496e-05 | 1071 | 10.82 | 6080 | 3.375077994860476e-11 | 0.0 | 0.0 |
| open_room_6 | endpoints | endpoints | 36 | 2 | 18 | 280 | 0.01931 | 7.366e-06 | 0.004813 | 8.397e-05 | 230 | 3.938 | 1152 | 0.04011 | 0.921 | 0.921 |
| open_room_6 | betweenness_sqrt | betweenness_6 | 36 | 6 | 6 | 3.733 | 0.01954 | 0.001866 | 0.03393 | 0.004416 | 4.425 | 0.486 | 7.314 | 0.04009 | 0.921 | 0.921 |
| open_room_6 | eigenoptions_sqrt | eigenoptions_6 | 36 | 6 | 6 | 3.889 | 0.01915 | 0.0003405 | 0.03428 | 0.002157 | 8.878 | 0.5208 | 15.36 | 0.04011 | 0.9216 | 0.9167 |
| open_room_6 | turn_articulation | turn_articulation | 36 | 4 | 9 | 15.56 | 0.01914 | 0.0004083 | 0.01346 | 0.000539 | 35.52 | 1.329 | 76.8 | 0.04011 | 0.0 | 0.0 |
| open_room_10 | endpoints | endpoints | 100 | 2 | 50 | 792 | 0.07291 | 1.295e-05 | 0.02042 | 8.941e-05 | 815.4 | 3.553 | 4300 | 0.07026 | 0.8664 | 0.8664 |
| open_room_10 | betweenness_sqrt | betweenness_10 | 100 | 10 | 10 | 2.636 | 0.07311 | 0.01273 | 0.3369 | 0.01734 | 4.217 | 0.1992 | 6.59 | 0.07026 | 0.8664 | 0.3467 |
| open_room_10 | eigenoptions_sqrt | eigenoptions_10 | 100 | 10 | 10 | 2.789 | 0.07372 | 0.05088 | 0.338 | 0.01765 | 4.176 | 0.1814 | 6.59 | 0.07026 | 0.867 | 0.7302 |
| open_room_10 | turn_articulation | turn_articulation | 100 | 4 | 25 | 79.2 | 0.07309 | 0.000875 | 0.04736 | 0.0003997 | 182.8 | 1.503 | 358.3 | 0.07026 | 0.0 | 0.0 |
| four_rooms_7 | endpoints | endpoints | 40 | 2 | 20 | 280 | 0.02365 | 7.87e-06 | 0.008057 | 8.674e-05 | 272.6 | 2.901 | 1400 | 0.02441 | 2.057 | 2.057 |
| four_rooms_7 | betweenness_sqrt | betweenness_7 | 40 | 7 | 5.714 | 5.185 | 0.02365 | 0.002142 | 0.09876 | 0.003805 | 6.215 | 0.2259 | 10.26 | 0.02427 | 1.173 | 1.054 |
| four_rooms_7 | eigenoptions_sqrt | eigenoptions_7 | 40 | 7 | 5.714 | 2.593 | 0.02382 | 0.0003563 | 0.1002 | 0.003267 | 7.29 | 0.2293 | 12.12 | 0.02441 | 2.058 | 1.055 |
| four_rooms_7 | turn_articulation | turn_articulation | 40 | 16 | 2.5 | 0.1702 | 0.02357 | 0.000398 | 0.1778 | 0.02051 | 1.149 | 0.1186 | 1.795 | 0.02441 | 0.0 | 0.0 |
| four_rooms_11 | endpoints | endpoints | 104 | 2 | 52 | 792 | 0.08164 | 1.264e-05 | 1.518 | 0.0002263 | 360.7 | 0.05376 | 4784 | 0.05768 | 1.904 | 1.904 |
| four_rooms_11 | betweenness_sqrt | betweenness_11 | 104 | 11 | 9.455 | 6.092 | 0.08037 | 0.01806 | 1.1 | 0.01915 | 4.196 | 0.0707 | 6.443 | 0.05768 | 1.905 | 0.9667 |
| four_rooms_11 | eigenoptions_sqrt | eigenoptions_11 | 104 | 11 | 9.455 | 2.411 | 0.08163 | 0.04205 | 1.104 | 0.01433 | 5.696 | 0.07035 | 8.698 | 0.05768 | 1.904 | 1.281 |
| four_rooms_11 | turn_articulation | turn_articulation | 104 | 16 | 6.5 | 0.6465 | 0.08046 | 0.0008636 | 0.6048 | 0.01403 | 5.735 | 0.1298 | 8.859 | 0.05768 | 0.0 | 0.0 |
| maze_9 | endpoints | endpoints | 31 | 2 | 15.5 | 182 | 0.01728 | 7.981e-06 | 0.004858 | 8.501e-05 | 203.2 | 3.49 | 1023 | 1.98667748918524e-11 | 3 | 3 |
| maze_9 | betweenness_sqrt | betweenness_6 | 31 | 6 | 5.167 | 7.913 | 0.01697 | 0.00118 | 0.03619 | 0.003592 | 4.723 | 0.4143 | 8.024 | 7.052136652418994e-12 | 2 | 2 |
| maze_9 | eigenoptions_sqrt | eigenoptions_6 | 31 | 6 | 5.167 | 8.089 | 0.01691 | 0.000273 | 0.03853 | 0.004799 | 3.523 | 0.3877 | 5.93 | 3.5864644587491057e-12 | 3 | 4.999 |
| maze_9 | turn_articulation | turn_articulation | 31 | 8 | 3.875 | 3.714 | 0.01685 | 0.000269 | 0.0407 | 0.004642 | 3.629 | 0.3694 | 6.089 | 1.9126034089822497e-11 | 0.0 | 0.0 |
| maze_13 | endpoints | endpoints | 71 | 2 | 35.5 | 422 | 0.06351 | 9.983e-06 | 0.01925 | 0.0001305 | 486.7 | 3.276 | 3763 | 1.6697754290362354e-13 | 6 | 6 |
| maze_13 | betweenness_sqrt | betweenness_9 | 71 | 9 | 7.889 | 6.975 | 0.06328 | 0.005227 | 0.3706 | 0.008998 | 7.032 | 0.1644 | 11 | 4.192202140984591e-13 | 5 | 5 |
| maze_13 | eigenoptions_sqrt | eigenoptions_9 | 71 | 9 | 7.889 | 7.673 | 0.06553 | 0.05479 | 0.3722 | 0.01697 | 3.86 | 0.1476 | 5.807 | 1.978861519091879e-12 | 5.001 | 7 |
| maze_13 | turn_articulation | turn_articulation | 71 | 18 | 3.944 | 1.546 | 0.06337 | 0.0005101 | 0.4133 | 0.03571 | 1.774 | 0.141 | 2.733 | 1.1475265182525618e-12 | 0.0 | 0.0 |
