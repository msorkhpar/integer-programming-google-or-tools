A bus operator plans depot upgrades in PuLP and solves them with CBC every night. A reporting job
reads each run and writes one line for the operations manager: was a plan found, is it proved the
best, and what is it worth. Last month the job printed a plan worth "0 seats" after a run that had
no plan at all, and the manager approved it.

Write `report(prob)` in `verdict.py`. It is called after `prob.solve(...)` and returns:

- `("proved", value)` when CBC finished its search with an optimal plan;
- `("unproved", value)` when CBC stopped early, for instance at a time limit, with a plan it has
  not proved best;
- `("no plan", None)` in every other case.

`value` is the objective's value. Decide from the problem's two codes, `prob.status` and
`prob.sol_status`, never from the variables: after a run with no plan they can still hold numbers.
The constants you need are in `pulp`: `LpStatusOptimal`, `LpSolutionOptimal`,
`LpSolutionIntegerFeasible`. About four lines.
