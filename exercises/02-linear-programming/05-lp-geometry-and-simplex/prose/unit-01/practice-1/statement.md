A district heating crew plans two kinds of work for a month, $`x`$ and $`y`$ (in hundreds of
hours), under a handful of limits. Before anyone trusts a solver with it, the team lead wants the
corners of the allowed region printed, so the drawing on the whiteboard can be checked against
numbers.

Write `vertices(rows)` in `vertices.py`. Each row is a tuple `(a, b, r)` that reads
$`a\,x + b\,y \le r`$; bounds such as $`x \ge 0`$ arrive as rows too, `(-1, 0, 0)`. The region is

```math
\{(x, y) : a_i\, x + b_i\, y \le r_i \ \ \forall i\}
```

A corner is a point where the boundary lines $`a_i x + b_i y = r_i`$ of two rows cross and that
every row allows. For two rows, with $`\Delta = a_1 b_2 - a_2 b_1`$:

```math
x = \frac{r_1 b_2 - r_2 b_1}{\Delta}, \qquad y = \frac{a_1 r_2 - a_2 r_1}{\Delta}
```

and when $`|\Delta| < 10^{-12}`$ the lines are parallel and have no crossing.

Return the corners as a sorted list of `(x, y)` tuples, each rounded to 6 decimals (add `0.0` after
rounding so that `-0.0` becomes `0.0`), each corner listed once. Count a row as allowing a point
when $`a\,x + b\,y \le r + 10^{-9}`$ (the constant `TOL`), so a corner is not lost to float
arithmetic. A region with no corners gives `[]`.
