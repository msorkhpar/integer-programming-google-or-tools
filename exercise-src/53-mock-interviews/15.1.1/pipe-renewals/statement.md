This is the whiteboard question of the mock, coded. A water utility's model in `renewals.py` already
has a start variable `x[(rid, year)]` for each renewal and each year in its window, the row that
each renewal starts at most once, and an objective. Three of the interviewer's rules are missing:

- **Budgets.** A renewal spends `cost[0]` in its start year, `cost[1]` the next year, and so on. In
  every year of `budgets`, the renewals' spend in that year is at most the budget.
- **Predecessors.** A renewal with a `parent` may start in year $`t`$ only if the parent was funded
  and started in a year $`s \le t - \text{lag}`$.
- **Alternatives.** Renewals that share a `group` are alternatives for one main: at most one of them
  is funded, whatever years they would start in.

Write `add_rules(model, x, renewals, budgets)` so the model allows exactly the plans that keep all
three. Write your formulation first, in the notation of the mock's whiteboard (sets, parameters,
variables with domains, each row with its quantifier and a label), then code it. A year in which
nothing can be spent has an empty sum: in Python that is the number 0, not a row, so write no row
for it.

The tests fix a plan through the variables' bounds and ask HiGHS whether the model allows it, so
any correct formulation passes. About twenty lines.
