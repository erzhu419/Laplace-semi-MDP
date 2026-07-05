# Discovery Profile Cache Benchmark

Generated: 2026-07-05T16:57:11
map_specs = ['open_room:7', 'four_rooms:7', 'maze:9']
slips = [0.0, 0.05]
max_candidates = 8

This isolates one boundary-selection step and decomposes probe construction, Green-kernel evaluation, frozen/operator scoring, full adaptive candidate recompute, and cache hits.

| map | slip | mode | n_states | n_basis | n_boundary | max_candidates | n_candidate_scores | selected_state | wall_time_sec | speedup_vs_full_recompute | probe_context_build_time_sec | probe_green_kernel_time_sec | probe_operator_delta_time_sec | full_recompute_time_sec | candidate_score_time_sec | probe_cache_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| open_room_7 | 0.0 | full_recompute | 49 | 14 | 2 | 8 | 48 | 3 | 1.745 | 1 | 0.117 | 0.1163 | 0.09902 | 1.412 | 0.0003467 | 0.0 |
| open_room_7 | 0.0 | current_frozen_operator | 49 | 14 | 2 | 8 | 10 | 43 | 0.3277 | 5.326 | 0.1164 | 0.1138 | 0.09663 |  | 0.0003236 | 0.0 |
| open_room_7 | 0.0 | cached_incremental_first | 49 | 14 | 2 | 8 | 10 | 43 | 0.3265 | 5.344 | 0.116 | 0.1134 | 0.09611 |  | 0.0003415 | 0.0 |
| open_room_7 | 0.0 | cached_incremental_hit | 49 | 14 | 2 | 8 | 10 | 43 | 0.0003485 | 5007 | 0.0 | 0.0 | 0.0 |  | 0.000243 | 1 |
| open_room_7 | 0.05 | full_recompute | 49 | 14 | 2 | 8 | 48 | 3 | 2.862 | 1 | 0.2517 | 0.2298 | 0.2167 | 2.163 | 0.0003684 | 0.0 |
| open_room_7 | 0.05 | current_frozen_operator | 49 | 14 | 2 | 8 | 11 | 43 | 0.6903 | 4.146 | 0.2498 | 0.2285 | 0.2113 |  | 0.0003508 | 0.0 |
| open_room_7 | 0.05 | cached_incremental_first | 49 | 14 | 2 | 8 | 11 | 43 | 0.692 | 4.137 | 0.253 | 0.2277 | 0.2102 |  | 0.000391 | 0.0 |
| open_room_7 | 0.05 | cached_incremental_hit | 49 | 14 | 2 | 8 | 11 | 43 | 0.0003807 | 7519 | 0.0 | 0.0 | 0.0 |  | 0.0002694 | 1 |
| four_rooms_7 | 0.0 | full_recompute | 40 | 26 | 2 | 8 | 48 | 2 | 1.509 | 1 | 0.09523 | 0.09604 | 0.08173 | 1.235 | 0.0003979 | 0.0 |
| four_rooms_7 | 0.0 | current_frozen_operator | 40 | 26 | 2 | 8 | 10 | 2 | 0.2806 | 5.375 | 0.09831 | 0.101 | 0.08053 |  | 0.0003939 | 0.0 |
| four_rooms_7 | 0.0 | cached_incremental_first | 40 | 26 | 2 | 8 | 10 | 2 | 0.2716 | 5.555 | 0.09647 | 0.09597 | 0.0781 |  | 0.0003122 | 0.0 |
| four_rooms_7 | 0.0 | cached_incremental_hit | 40 | 26 | 2 | 8 | 10 | 2 | 0.0003477 | 4339 | 0.0 | 0.0 | 0.0 |  | 0.0002375 | 1 |
| four_rooms_7 | 0.05 | full_recompute | 40 | 26 | 2 | 8 | 48 | 2 | 2.296 | 1 | 0.2031 | 0.1878 | 0.1747 | 1.729 | 0.0006301 | 0.0 |
| four_rooms_7 | 0.05 | current_frozen_operator | 40 | 26 | 2 | 8 | 16 | 6 | 0.5642 | 4.069 | 0.2049 | 0.1873 | 0.1712 |  | 0.0004076 | 0.0 |
| four_rooms_7 | 0.05 | cached_incremental_first | 40 | 26 | 2 | 8 | 16 | 6 | 0.5589 | 4.108 | 0.2008 | 0.1859 | 0.1711 |  | 0.000438 | 0.0 |
| four_rooms_7 | 0.05 | cached_incremental_hit | 40 | 26 | 2 | 8 | 16 | 6 | 0.0004546 | 5051 | 0.0 | 0.0 | 0.0 |  | 0.000335 | 1 |
| maze_9 | 0.0 | full_recompute | 31 | 17 | 2 | 8 | 48 | 1 | 1.073 | 1 | 0.06772 | 0.07023 | 0.05936 | 0.8747 | 0.0002771 | 0.0 |
| maze_9 | 0.0 | current_frozen_operator | 31 | 17 | 2 | 8 | 9 | 1 | 0.1913 | 5.608 | 0.06717 | 0.06878 | 0.05468 |  | 0.0002837 | 0.0 |
| maze_9 | 0.0 | cached_incremental_first | 31 | 17 | 2 | 8 | 9 | 1 | 0.1914 | 5.603 | 0.06702 | 0.06888 | 0.05469 |  | 0.0002836 | 0.0 |
| maze_9 | 0.0 | cached_incremental_hit | 31 | 17 | 2 | 8 | 9 | 1 | 0.0003273 | 3278 | 0.0 | 0.0 | 0.0 |  | 0.0002221 | 1 |
| maze_9 | 0.05 | full_recompute | 31 | 17 | 2 | 8 | 48 | 1 | 1.638 | 1 | 0.1415 | 0.1336 | 0.1246 | 1.237 | 0.0003119 | 0.0 |
| maze_9 | 0.05 | current_frozen_operator | 31 | 17 | 2 | 8 | 11 | 1 | 0.3952 | 4.145 | 0.1422 | 0.1328 | 0.1194 |  | 0.0004022 | 0.0 |
| maze_9 | 0.05 | cached_incremental_first | 31 | 17 | 2 | 8 | 11 | 1 | 0.3969 | 4.126 | 0.1423 | 0.1338 | 0.1198 |  | 0.000347 | 0.0 |
| maze_9 | 0.05 | cached_incremental_hit | 31 | 17 | 2 | 8 | 11 | 1 | 0.0003604 | 4544 | 0.0 | 0.0 | 0.0 |  | 0.0002518 | 1 |
