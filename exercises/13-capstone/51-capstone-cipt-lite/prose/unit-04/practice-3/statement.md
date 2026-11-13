The practice utility's planners (a fictional utility) read the best plan and ask about one project it
left out: why is it deferred, and what would funding it cost? Milestone 4 answers both, for any
project, with numbers a planner can check.

`why.py` gives you milestone 2's model and tools: `build(snapshot, scenario)` (a scenario's
`force_in` list becomes a row $`\sum_t x_{i,t} \ge 1`$), `solve(b)` (HiGHS to a zero gap),
`plan_of(b, result)` and `check(snapshot, scenario, plan)`, the rule checker that names every row a
plan breaks from the data alone.

Write:

- `refused_by(snapshot, scenario, plan, pid)`: for each start year $`t`$ of the deferred project, the
  rows that **the plan as it stands, with the project added at $`t`$**, breaks (lesson 9.3.1: on a
  MILP the row that blocks is the one a whole project cannot fit, slack or not). Return
  `{start year: [row names]}`, with each list exactly as `check` returns it: `must_` rows, then
  `alt_`, then `after_`, then for each year in order its `budget_`, `region_` and `crews_` rows,
  then `floor_` rows. Rows the plan already breaks without the project are not taken out: they are
  listed at every start.
- `forcing_cost(snapshot, scenario, pid)`: solve the scenario, then solve it again with `pid` forced
  in (lesson 9.3.2). Return `Forced(cost, gives_way)`, where `cost` is the base objective less the
  forced one, and `gives_way` lists, by project id, every project of the base plan that the forced
  plan drops (`"J3 dropped"`) or moves (`"J1 2028->2027"`). When the forced model has no plan,
  return `None`: a forcing the rules cannot satisfy is answered by a rule, not by a price.
- `cost_interval(base_primal, base_bound, forced_primal, forced_bound)`: on a large portfolio both
  solves stop at a relative gap, so each objective is only known between its plan's value (primal)
  and its proven bound. For a maximization, the true cost lies between

  ```math
  \max\bigl(0,\; z^{\text{base}}_{\text{plan}} - z^{\text{forced}}_{\text{bound}}\bigr)
  \quad\text{and}\quad
  z^{\text{base}}_{\text{bound}} - z^{\text{forced}}_{\text{plan}}
  ```

  Return the pair `(low, high)`. Forcing a project in can never raise the best value, which is why
  the low end is never below zero.
