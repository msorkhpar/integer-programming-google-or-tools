A water utility's operations team solves a pumping LP every night, and the morning report must say,
for every row, how much room was left, and which rows were binding. Their models are MathOpt models,
so every row is stored as $`\text{lb} \le a \cdot x \le \text{ub}`$, with $`\pm\infty`$ for a
missing side. With $`a \cdot x`$ the row's activity at the solution, a row's **room** is:

| Row, as stored | Room |
| --- | --- |
| only `ub` finite ($`a \cdot x \le \text{ub}`$) | the slack, $`\text{ub} - a \cdot x`$ |
| only `lb` finite ($`a \cdot x \ge \text{lb}`$) | the surplus, $`a \cdot x - \text{lb}`$ |
| both finite (a range, or an equation when they are equal) | $`\min(\text{ub} - a \cdot x,\ a \cdot x - \text{lb})`$ |
| neither finite (a free row, $`-\infty \le a \cdot x \le +\infty`$) | `math.inf`: nothing limits the row, so it never binds |

Write two functions in `report.py`:

- `room(model, result)` returns a dict from each row's name to its room, for every linear
  constraint of the model, using the solution in `result`;
- `binding(model, result, tol=1e-6)` returns the names of the rows whose room is at most `tol`, in
  the order `model.linear_constraints()` gives them.

`row.terms()`, `row.lower_bound`, `row.upper_bound` and `result.variable_values()` give everything
you need; `math.isfinite` tells a bound from $`\pm\infty`$. About fifteen lines.
