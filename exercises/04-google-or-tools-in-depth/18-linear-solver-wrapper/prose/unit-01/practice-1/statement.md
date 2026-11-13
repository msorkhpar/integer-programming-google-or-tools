A water utility's planning script keeps its rows as data, so that planners can edit them in a
spreadsheet. Each row is a tuple `(name, lower, coefficients, upper)`: `coefficients` maps a
variable's name to its coefficient, and `lower` or `upper` is `None` when the row has no bound on
that side. A variable missing from `coefficients` has coefficient 0 in that row.

Write `add_rows(solver, x, rows)` in `rows.py`, which adds every row to a pywraplp solver in the
coefficient style: one `RowConstraint` per row, filled with `SetCoefficient`. `x` maps variable
names to the solver's variables. Each row is

```math
\ell_r \;\le\; \sum_{j} a_{r,j}\, x_j \;\le\; u_r \qquad \text{(name}_r\text{)}
```

with $`\ell_r = -\infty`$ when `lower` is `None` and $`u_r = +\infty`$ when `upper` is `None`.

`best(rows, objective)` is given: it makes integer variables `x0` and `x1` between 0 and 10, calls
your function, maximizes the objective, and returns the optimal value, or `None` if the solve is not
optimal. The tests compare that value with what the rows allow. About six lines.
