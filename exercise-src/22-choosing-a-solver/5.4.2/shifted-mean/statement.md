A team compares two MILP solvers on its instance set and wants one number per solver, computed the
way Hans Mittelmann's benchmark pages define it. For nonnegative values $`v_1, \dots, v_n`$ (solve
times, or counts of work) and a shift $`s \ge 0`$:

```math
\text{SGM}_s(v) = \exp\!\Big(\frac{1}{n} \sum_{i=1}^{n} \ln \max(1,\; v_i + s)\Big) - s
```

Write `shifted_geometric_mean(values, shift)` in `sgm.py`, for a nonempty list. The `max(1, ...)`
matters: it keeps each logarithm nonnegative, so tiny values cannot pull the mean toward zero.

About three lines.
