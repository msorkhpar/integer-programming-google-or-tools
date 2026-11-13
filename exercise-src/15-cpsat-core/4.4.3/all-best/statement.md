A conference's programme committee (not GridCap) scores each submitted talk and fills a session
within its minutes, at most one talk per track. Scores are small whole numbers, so many programmes
tie, and the committee wants to see *all* the best ones before it chooses.

Write `all_best(model, x, objective)` in `best_plans.py`. `model` is a CP-SAT model with every rule
already in it and no objective; `x` maps each talk's name to its Boolean; `objective` is the linear
score to maximize. Return `(best, plans)`: the best score as an `int`, and every distinct plan that
reaches it, each plan a sorted tuple of the names whose Boolean is true, the list sorted. Return
`(None, [])` if no optimum is proven. In the lesson's terms, with $`S(x)`$ the score:

```math
S^* = \max_{x \text{ feasible}} S(x), \qquad \text{plans} = \{\, \{i : x_i = 1\} \;:\; x \text{ feasible},\ S(x) = S^* \,\}
```

`PlanCollector` is given: it records the plan of every solution reported to it. Some models have
variables that are not part of the plan. About fifteen lines.

The function may change the model it is given: each test builds a fresh model for each call, and the
reference adds its rows to `model` itself. If you would rather leave the caller's model as it was,
work on a copy: in OR-Tools 9.15, `copy = model.clone()` returns a new `CpModel` with the same
variables and constraints, and rows or an objective added to the copy leave the original unchanged.
The copy's variables have the same indices as the original's, so expressions built from `x` and
`objective` can be added to the copy and read with `solver.value` after solving it.
