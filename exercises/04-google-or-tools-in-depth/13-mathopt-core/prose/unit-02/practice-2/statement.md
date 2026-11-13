A dairy cooperative plans its weekly milk allocation with an LP: how many thousand litres go to
cheese, butter and bottled milk, under limits on milk supply, plant hours and churn capacity, and a
minimum for the bottled-milk contract. Its finance team asks one question after every run: which limits hold the
plan back, and what would one more unit of each be worth?

Write `binding_prices(result, rows, tol=1e-6)` in `prices.py`. `rows` is a list of the model's
`mathopt.LinearConstraint`s.

- When `result` has no dual feasible solution (a MILP, or a solve that failed), return `None`.
- Otherwise return a dict from row name to the row's dual value, for every **binding** row in `rows`,
  and no other.

A row is binding when its **activity**, $`\sum_j a_j x_j`$ at the result's variable values, is within
`tol` of one of its finite bounds: its upper bound, its lower bound, or the single value of an
equality row. Compute the activity from the row's `terms()` and `result.variable_values()`. Do not
use the basis (`constraint_status`): a first-order solver such as PDLP returns dual values without
one.
