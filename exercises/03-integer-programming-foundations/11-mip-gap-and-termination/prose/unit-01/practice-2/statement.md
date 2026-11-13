A hospital's nurse-rostering MILP runs every Sunday night with a time limit. The service that
starts it stores a short report of each run, built from the `SolveResult` that `mathopt.solve`
returned. Some weeks the run ends with a plan, some weeks it stops before finding one, and once a
year the rules contradict each other.

Write `read_gap(result)` in `gap.py`. Read the two numbers from
`result.termination.objective_bounds`: `primal_bound` (the incumbent's value) and `dual_bound` (the
best bound). Return a dict with four keys:

- `"incumbent"`: the primal bound as a float, or `None` when it is infinite (no plan).
- `"bound"`: the dual bound as a float, or `None` when it is infinite.
- `"absolute"`: $`|\text{bound} - \text{incumbent}|`$, which is positive for a maximization and a
  minimization alike, or `math.inf` when either number is missing.
- `"relative"`: the absolute gap divided by $`|\text{incumbent}|`$, the way HiGHS divides. It is `0.0`
  when the absolute gap is 0, `math.inf` when the incumbent is 0 and the absolute gap is not, and
  `math.inf` when either number is missing.

The result does not say whether the model was a maximization or a minimization, and your function
does not need to know. `math.isinf(x)` tells you whether a float is infinite.
