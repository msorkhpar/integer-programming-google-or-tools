A school district picks which bus routes to renew. Its main score is a whole number per route
(`primary`, positive integers), and to break ties it adds a small bonus per route (`secondary`,
non-negative numbers), so the solver maximizes

```math
\sum_{r} p_r\, x_r \;+\; \varepsilon \sum_{r} s_r\, x_r, \qquad x_r \in \{0, 1\}
```

The bonus must never change which of two plans has the higher main score. So the largest bonus any
plan can collect, times ε, has to stay below the smallest positive difference between two plans'
main scores. You don't need that exact difference, only a safe lower bound for it: the greatest
common divisor of the main scores, as the lesson shows (it can be smaller than the true smallest
difference, which only makes ε smaller and still safe).

Write `max_epsilon(primary, secondary)`, both dicts keyed by route. Take $`g`$ as the greatest common
divisor of the `primary` values and $`S`$ as the largest bonus a plan can collect, and return
$`g / (S + 1)`$.

About five lines.
