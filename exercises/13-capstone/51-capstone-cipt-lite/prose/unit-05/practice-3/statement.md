Finance cut every year of this cycle to $300k. Last cycle's approved plan no longer fits, but most
of it is still good, and the planners want the solver to start from it rather than from nothing. Your
milestone turns last cycle's plan into a **warm start**: a complete, rule-abiding plan handed to HiGHS
as a solution hint. The data is a fictional utility's practice portfolio.

`warm_start.py` gives you milestone 2's model with a reduced rule set (must-do, at-most-once,
alternative, precedence-with-lag and yearly budget rows) as `build(snapshot)`, which returns
`(model, x)` with `x[(project, year)]` the start variables, plus `solve(model, model_params)`,
`plan_of`, `spend` and the rule checker `check(snapshot, plan)`.

Write:

| function | contract | lesson |
| --- | --- | --- |
| `carry(last, snapshot)` | last cycle's starts that this cycle's model has a variable for: the project still exists and the year is in its window. A child whose parent is not carried is not carried either (repeat until none is left) | 11.2.1 |
| `repair(snapshot, plan)` | while `check` reports a broken `budget_<year>` row, drop one optional project among those that spend in a broken year: the one with the least NPV (at its planned start) per $k of total cost, ties to the smaller id. A dropped project's children, and theirs, go with it. Never drop a must-do, nor a project with a must-do among its children or their children in the plan (dropping it would take the must-do with it); if only such projects are left, stop and return the plan | 11.2.1 |
| `hint(x, plan)` | `mathopt.ModelSolveParameters(solution_hints=[mathopt.SolutionHint(variable_values=...)])` with a value for every start variable: 1.0 for the plan's starts, 0.0 for all others | 4.3.3, 11.2.1 |

A hint changes where the search starts, never the answer: the tests check that the hinted solve
reaches the same optimum as the plain one, and that the start you hand over breaks no rule. About
twenty-five lines.
