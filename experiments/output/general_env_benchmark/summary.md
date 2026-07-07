# General Environment Benchmark

This smoke benchmark tests the finite-MDP adapter on non-handwritten-grid environments.
The PointMaze rows are discretized empirical MDPs; theoretical claims apply to the discretized model.

- rows: 112
- errors: 1

## Best Rows By Env

| env                | method              | options           | target | B  | compression | start_gap   | max_gap   | construct_s |
| ------------------ | ------------------- | ----------------- | ------ | -- | ----------- | ----------- | --------- | ----------- |
| CliffWalking-v1    | betweenness         | primitive         | 32     | 32 | 1.50        | 0           | 0         | 0.0030      |
| FrozenLake8x8-v1   | coverage            | boundary_targeted | 32     | 32 | 2.00        | 0.0243608   | 0.0967297 | 0.0054      |
| PointMaze-umaze-b3 | betweenness         | primitive         | 32     | 32 | 1.97        | 5.92119e-16 | 2.09304   | 0.0051      |
| Taxi-v3            | taxi_landmark_modes | boundary_targeted | 8      | 84 | 5.95        | 10.7284     | 50.1813   | 0.0001      |

## Skipped Or Failed Specs

| env_spec        | method   | options           | target | error                               |
| --------------- | -------- | ----------------- | ------ | ----------------------------------- |
| toytext:Taxi-v3 | spectral | boundary_targeted | 32     | LinAlgError('SVD did not converge') |

