A pole-replacement model has whole-number decisions $`x_1, \dots, x_n \ge 0`$ and rows
$`A x \le b`$ with integer $`A`$ and $`b`$. Its simplex code adds slack $`s_i = b_i - A_i x`$ to
row $`i`$. One row of the optimal tableau, over the columns $`(x_1, \dots, x_n, s_1, \dots, s_m)`$
and the right-hand side, is

```math
\sum_{j=1}^{n} r_j\, x_j + \sum_{i=1}^{m} r_{n+i}\, s_i = r_0
```

with $`r_0`$ fractional. Write the Gomory cut of this row in the model's own variables, so a planner
can read it.

Write `gomory_in_x(row, A, b)` in `gomory.py`. `row` is a list of `Fraction`:
$`[r_1, \dots, r_{n+m}, r_0]`$. Let $`f(v) = v - \lfloor v \rfloor`$. The Gomory cut is
$`\sum_{k=1}^{n+m} f(r_k)\, w_k \ge f(r_0)`$, where $`w`$ is $`x`$ followed by $`s`$. Substitute
$`s_i = b_i - \sum_j A_{ij} x_j`$ and return `(g, h)`, two `Fraction` values or lists of them, with

```math
g_j = -f(r_j) + \sum_{i=1}^{m} f(r_{n+i})\, A_{ij} \quad (j = 1, \dots, n), \qquad
h = \sum_{i=1}^{m} f(r_{n+i})\, b_i - f(r_0)
```

so the cut reads $`\sum_j g_j x_j \le h`$. Return exact fractions; don't scale them.
