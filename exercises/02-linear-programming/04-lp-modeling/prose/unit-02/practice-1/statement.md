A water utility's analysts keep their LPs as plain data: a list of variable names, an objective
(coefficients by name, and `"max"` or `"min"`) and a list of rows. Each row is a tuple
`(coefficients, op, rhs)`: the coefficients by variable name (a variable missing from the dict has
coefficient 0), `op` one of `"<="`, `">="` or `"=="`, and the right-hand side. Every variable is
$`\ge 0`$. Their in-house LP code accepts only one shape, the standard form:

```math
\max \; c^\top x \quad \text{s.t.} \quad A x \le b, \quad x \ge 0
```

Write `standard_form(variables, objective, sense, rows)` in `standard_form.py`. It returns
`(c, A, b)` as plain lists: `c` has one entry per variable, in the order of `variables`; `A` is a
list of rows, each a list with one entry per variable in that order; `b` has one entry per row of
`A`. Rewrite with these moves:

| Given | Becomes |
| --- | --- |
| $`a \cdot x \le r`$ | the row $`a`$, right-hand side $`r`$ |
| $`a \cdot x \ge r`$ | the row $`-a`$, right-hand side $`-r`$ |
| $`a \cdot x = r`$ | two rows, in this order: $`a`$ with $`r`$, then $`-a`$ with $`-r`$ |
| $`\min\, c^\top x`$ | $`\max\, (-c)^\top x`$ |

Rows keep the order they were given in. About twelve lines; no solver needed.
