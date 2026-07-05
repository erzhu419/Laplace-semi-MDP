# Weighted Spectral Certificate

Generated: 2026-07-05T15:21:13
map_specs = ['corridor:128', 'open_room:12', 'maze:13', 'four_rooms:11']
boundary_methods = ['endpoints']
terminal_basis = ['boundary', 'residual']
k_values = [32, 64, 128]

This checks a Collatz-style positive-vector certificate for first-hit Green tails:

```text
P_II w <= q w, q < 1
tail <= c * w_start * q^(K+1) / (1-q)
```

It is a sufficient weighted spectral certificate; it is not used as the default runtime path yet.
Large dynamic ranges mean the certificate can be mathematically valid but numerically awkward.

| map | terminal_basis | n_edges | row_q_lt_1 | weighted_q_lt_1 | spectral_radius_max | row_q_max | weighted_q_max | weight_max_max | weight_dynamic_range_max | weighted_row_tail_K128_max | actual_tail_row_K128_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corridor_128 | boundary | 2 | 0 | 2 | 0.7439 | 1 | 0.8244 | 5.231e+12 | 3.912e+12 | 124.7 | 0.9758 |
| corridor_128 | residual | 2 | 0 | 2 | 0.7439 | 1 | 0.8244 | 5.231e+12 | 3.912e+12 | 124.7 | 0.9758 |
| four_rooms_11 | boundary | 2 | 0 | 2 | 0.3717 | 1 | 0.3755 | 3.637e+12 | 6.996e+11 | 1.4276718392151313e-43 | 1.2212453270876722e-15 |
| four_rooms_11 | residual | 2 | 0 | 2 | 0.3666 | 1 | 0.3705 | 2.502e+10 | 4.827e+09 | 4.294569448223811e-47 | 2.2219369740622287e-16 |
| maze_13 | boundary | 2 | 0 | 2 | 0.4645 | 1 | 0.4645 | 2.6e+20 | 8.839e+19 | 2.8673490386209093e-34 | 1.3322676295501878e-15 |
| maze_13 | residual | 2 | 0 | 2 | 0.2764 | 1 | 0.278 | 3.619e+10 | 8.662e+09 | 1.145362741482262e-70 | 0.0 |
| open_room_12 | boundary | 2 | 0 | 2 | 0.3573 | 1 | 0.3595 | 1.45e+14 | 1.373e+13 | 9.688698765692715e-45 | 2.3314683517128287e-15 |
| open_room_12 | residual | 2 | 0 | 2 | 0.3554 | 1 | 0.3569 | 3.817e+13 | 2.446e+12 | 4.810531195422247e-46 | 1.2490009027033011e-15 |
