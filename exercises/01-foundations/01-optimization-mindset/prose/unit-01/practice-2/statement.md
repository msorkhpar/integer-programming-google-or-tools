The checks of the previous practice are the first half of this one: paste your `evaluate_plan`
into `best.py` (the starter leaves it empty), or write the checks again. The director wants the plan itself: of every allowed plan, the most valuable one.
Portfolios in this tool have at most 15 projects, so checking every subset is fast enough.

Write `best_plan(projects, budget)` in `best.py`. It returns `(value, plan)`, where `plan` is a
`frozenset` of project ids, for the allowed plan with the highest total value. When two allowed
plans have the same value, return the one that costs less. When no plan is allowed at all, return
`None`.

About ten lines.
