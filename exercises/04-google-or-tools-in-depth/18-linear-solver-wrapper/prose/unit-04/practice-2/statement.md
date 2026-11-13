A tree-trimming contractor sells one crew's season to a utility. Each job has a value in whole $k
and a length in crew-months, given to two decimal places (2.3 months, 7.71 months); the season
is a number of months, also to two decimals. Which jobs make the most valuable season?

Write `best_season(values, months, season)` in `season.py` with `KnapsackSolver`. Return the best
total value and the sorted indices of the chosen jobs. The model:

```math
\max\; \sum_i v_i\, x_i \quad \text{s.t.} \quad \sum_i m_i\, x_i \le S \;\; \text{(season)}, \qquad x_i \in \{0, 1\}
```

`KnapsackSolver` takes only whole numbers, so turn the months and the season into whole hundredths
first. Mind how Python turns a float into an int: `2.3 * 100` is `229.99999999999997`, so
`int(2.3 * 100)` is 229, while `round(2.3 * 100)` is 230. Use `round` for every month and for the
season, as the reference does. One row means `weights` is a list holding one list.

Any solver type that handles one row works, since each test has only a few jobs; the reference
uses `KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER`, which the lesson's table showed handles any
number of rows. About eight lines.
