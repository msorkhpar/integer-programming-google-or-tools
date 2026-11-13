A courier firm re-plans its weekly delivery routes with a MIP: a binary $`y_r`$ per candidate route
$`r`$, 1 if the route runs this week. Most weeks look like the last one, so the planners want to
start the solver from last week's plan.

Write `hint_params(y, chosen, complete)`, which returns a `mathopt.ModelSolveParameters` holding one
`SolutionHint` built from last week's plan. `y` is a dict from route name to its binary variable;
`chosen` is the set of route names that ran last week.

- `complete=True`: every route gets a value, $`y_r = 1`$ for $`r`$ in `chosen` and $`y_r = 0`$
  otherwise.
- `complete=False`: only the chosen routes get a value, $`y_r = 1`$; the solver fills in the rest.

One test solves with your parameters and reads HiGHS's log, as lesson 4.3.3 did; the others read
the hint back. About five lines.
