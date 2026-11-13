This is the modeling round's whiteboard, coded. A water authority's model in `cash.py` has a start
variable `x[(pid, year)]` per project and allowed start year, the row that each project starts at
most once, `spend(x, projects, year)` (what a set of projects spends in one year, as an expression),
and an objective. Write `add_cash_rules(model, x, projects, budgets, carry_share, floors)`:

- **Carry-over.** What a year does not spend may be carried into the next year and spent there.
  Money neither spent nor carried lapses. Nothing comes into the first year. The last year may
  carry money out too, under the same cap, but no year follows to spend it, so it lapses; giving
  the last year a carry variable or not changes no plan, and the tests allow both.
- **Carry cap.** A year carries out at most `carry_share` times its own budget.
- **Floors.** Each region in `floors` spends at least its floor in total over the plan's years
  (`budgets` lists them); spend after the last year does not count. A region in `floors` that can
  spend nothing in those years (no projects, or none that can spend inside the plan) still has its
  floor, so a positive floor there allows no plan. Its total is an empty sum, which in Python is the
  number 0, not an expression, so start the sum from `mathopt.LinearExpression()` to keep the
  floor a row.

Write the formulation first: the new variables with their domains, each row with its quantifier and
a label. The tests fix the start variables and leave your other variables free, so any correct
formulation passes. About twelve lines.
