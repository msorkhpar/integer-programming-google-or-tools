A print shop's scheduler is handed weekly plans by three sales offices, each sure its plan is the
most profitable. The shop has no solver licence on the scheduling machine, but it has NumPy. It
wants a function that either proves a plan optimal, by producing prices that certify it, or
refuses it.

The shop's LP, with $`A`$ the products, $`R`$ the rows (each a limit $`\le`$ or a minimum $`\ge`$),
$`v_j`$ the profit per run of product $`j`$, $`a_{ij}`$ its coefficient in row $`i`$ (0 if absent)
and $`b_i`$ the right-hand side:

```math
\max \sum_{j \in A} v_j\, x_j \quad \text{s.t.} \quad \sum_{j \in A} a_{ij}\, x_j \;(\le \text{ or } \ge)\; b_i \;\; \forall i \in R, \qquad x_j \ge 0
```

For a feasible plan $`x`$, complementary slackness fixes the prices it implies:

1. $`y_i = 0`$ for every row with slack ($`|\sum_j a_{ij} x_j - b_i| > `$ `tol`);
2. for every product with $`x_j > `$ `tol`, its reduced cost is zero:
   $`\sum_{i \text{ binding}} a_{ij}\, y_i = v_j`$, one linear equation per used product in the
   prices of the binding rows.

The plan is optimal exactly when those prices are dual feasible: $`y_i \ge 0`$ on every $`\le`$
row, $`y_i \le 0`$ on every $`\ge`$ row, and every product's reduced cost
$`v_j - \sum_{i \in R} a_{ij}\, y_i \le 0`$ (all three with tolerance `tol`).

Write `certify(value, rows, plan, tol=1e-6)` in `certify.py`. `value` maps each product to $`v_j`$;
`rows` maps each row's name to `(coefficients, sense, rhs)`; `plan` maps each product to $`x_j`$.
Return a dict of every row's price when the plan is optimal, and `None` when it is not. Every plan
the tests pass is feasible and has as many binding rows as used products, with a system that has
one solution, so `np.linalg.solve(matrix, rhs)` solves it.

About fifteen lines.
