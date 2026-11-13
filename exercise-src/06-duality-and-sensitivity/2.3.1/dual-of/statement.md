A facilities team plans a week of inspection, repair and painting hours. Some of its rules are
limits, some are minimums, and one is a contract that fixes an amount exactly. The team lead wants
the price of every rule, and the proof that the plan is the best one, from a single function that
writes the dual LP and solves it.

The team's LP, with $`A`$ the activities, $`R`$ the rows, $`v_j`$ the value per unit of activity
$`j`$, $`a_{ij}`$ its coefficient in row $`i`$ (0 if it does not appear), $`b_i`$ the row's
right-hand side, and each row a limit, a minimum or an equality:

```math
\max \sum_{j \in A} v_j\, x_j \quad \text{s.t.} \quad \sum_{j \in A} a_{ij}\, x_j \;\; (\le,\ \ge \text{ or } =) \;\; b_i \;\; \forall i \in R, \qquad x_j \ge 0 \;\; \forall j \in A
```

Its dual has one price $`y_i`$ per row and one cover row per activity:

```math
\min \sum_{i \in R} b_i\, y_i \quad \text{s.t.} \quad \sum_{i \in R} a_{ij}\, y_i \ge v_j \;\; \forall j \in A \quad \text{(cover}_j)
```

with $`y_i \ge 0`$ for a $`\le`$ row, $`y_i \le 0`$ for a $`\ge`$ row, and $`y_i`$ free for an
$`=`$ row.

Write `solve_dual(value, rows)` in `dual.py`. `value` maps each activity to $`v_j`$; `rows` maps
each row's name to `(coefficients, sense, rhs)`, with `sense` one of `"<="`, `">="`, `"=="` and
`coefficients` mapping the activities in that row to $`a_{ij}`$. Build the dual in MathOpt, solve
it with GLOP, and return `(value, prices)`: the dual's optimal value and a dict of each row's
price. If the solve does not end `OPTIMAL`, return `(None, {})`.

An activity may appear in no row (every $`a_{ij} = 0`$). Its cover row is then
$`0 \ge v_j`$: if $`v_j > 0`$ no prices satisfy it, so the dual is infeasible (the LP itself is
unbounded, since that activity can grow forever) and the function returns `(None, {})`; if
$`v_j \le 0`$ the row always holds, and the dual is solved as usual. Either way the function must
not raise. A Python `sum` over no terms is the number `0`, and `0 >= v_j` is a `bool`, which
`add_linear_constraint` refuses with a `TypeError`; start such a sum from `mathopt.LinearExpression()`,
or keep a zero term for each row, so the cover row is always a MathOpt expression.

A free variable is `add_variable(lb=-math.inf, ub=math.inf)`; MathOpt's default lower bound is
also $`-\infty`$, so write each bound you mean. About fifteen lines.
