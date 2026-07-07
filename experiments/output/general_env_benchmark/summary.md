# General Environment Benchmark

This smoke benchmark tests the finite-MDP adapter on non-handwritten-grid environments.
The PointMaze rows are discretized empirical MDPs; theoretical claims apply to the discretized model.

- rows: 56
- errors: 0

## Best Rows By Env

| env                | method      | target | B  | compression | start_gap   | max_gap   | construct_s |
| ------------------ | ----------- | ------ | -- | ----------- | ----------- | --------- | ----------- |
| CliffWalking-v1    | betweenness | 32     | 32 | 1.50        | 0           | 0         | 0.0027      |
| FrozenLake8x8-v1   | coverage    | 32     | 32 | 2.00        | 0.024623    | 0.0982883 | 0.0055      |
| PointMaze-umaze-b3 | betweenness | 32     | 32 | 1.97        | 5.92119e-16 | 2.09304   | 0.0049      |
| Taxi-v3            | coverage    | 32     | 32 | 15.62       | 37.0419     | 51.7333   | 0.0578      |

