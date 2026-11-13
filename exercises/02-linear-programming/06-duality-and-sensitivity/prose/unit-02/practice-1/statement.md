A bakery's planning tool solves its daily LP with one solver and stores the plan and the row prices.
The owner wants an independent check, run on every saved result, that the pair really is optimal: a
list of every place where it breaks complementary slackness, empty when the pair is fine.

The bakery's LP, with $`A`$ the products, $`R`$ the rows, $`v_j`$ the profit per tray of product
$`j`$, $`a_{ij}`$ its coefficient in row $`i`$ (0 if absent) and $`b_i`$ the right-hand side; each
row is a limit ($`\le`$) or a minimum ($`\ge`$):

```math
\max \sum_{j \in A} v_j\, x_j \quad \text{s.t.} \quad \sum_{j \in A} a_{ij}\, x_j \;(\le \text{ or } \ge)\; b_i \;\; \forall i \in R, \qquad x_j \ge 0
```

For a plan $`x`$ and prices $`y`$:

- the **slack** of a $`\le`$ row is $`b_i - \sum_j a_{ij} x_j`$, and of a $`\ge`$ row
  $`\sum_j a_{ij} x_j - b_i`$;
- the **reduced cost** of product $`j`$ is $`d_j = v_j - \sum_{i \in R} a_{ij}\, y_i`$;
- complementary slackness asks $`\text{slack}_i \cdot y_i = 0`$ for every row and
  $`x_j \cdot d_j = 0`$ for every product.

Write `cs_violations(value, rows, plan, prices, tol=1e-6)` in `cs.py`. `value` maps each product to
$`v_j`$; `rows` maps each row's name to `(coefficients, sense, rhs)`, `sense` being `"<="` or
`">="`; `plan` maps each product to $`x_j`$; `prices` maps each row to $`y_i`$. Return the sorted
list of the names of every row with slack and price both nonzero, and every product with value and
reduced cost both nonzero, where "nonzero" means larger than `tol` in absolute value (the stored
numbers come from a floating-point solver). The plans the tests pass satisfy every row.

About twelve lines.
