A depot's ordering tool collects rules from several planners. Some write "at most", some "at
least", some "exactly". The checker from the previous practice only understands one form, rows of
$`Ax \le b`$, so every rule has to be brought to it first.

Write `to_leq(rules, n)` in `leq.py`. Each rule is a triple `(coeffs, sense, limit)`:

- `coeffs` maps a variable's index (0 to `n - 1`) to its coefficient; a variable not in `coeffs` has
  coefficient 0;
- `sense` is `"<="`, `">="` or `"=="`;
- `limit` is the right-hand side.

Return `(A, b)` as NumPy arrays, `A` with shape `(rows, n)`, where each row means
$`a^\top x \le b`$:

| rule | rows it becomes, in this order |
| --- | --- |
| $`a^\top x \le \beta`$ | $`a^\top x \le \beta`$ |
| $`a^\top x \ge \beta`$ | $`-a^\top x \le -\beta`$ |
| $`a^\top x = \beta`$ | $`a^\top x \le \beta`$, then $`-a^\top x \le -\beta`$ |

Rows follow the order of `rules`.

About twelve lines.
