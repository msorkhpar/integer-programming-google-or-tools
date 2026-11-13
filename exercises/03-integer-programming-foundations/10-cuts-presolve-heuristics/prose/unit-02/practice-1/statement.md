A pole-inspection model has many rows of the form

```math
\sum_{j} a_j\, x_j \le b, \qquad x_j \in \{0, 1\}, \quad lo_j \le x_j \le hi_j
```

where earlier reductions may already have fixed some variables ($`lo_j = hi_j`$). Write the presolve
step for one row.

Write `reduce_row(coefs, rhs, lo, hi)` in `reduce.py`. `coefs` maps each variable to $`a_j`$ (any
sign, never 0), and `lo` and `hi` map it to its bounds, 0 or 1. With

```math
\underline{L} = \sum_{a_j > 0} a_j\, lo_j + \sum_{a_j < 0} a_j\, hi_j, \qquad
\overline{L} = \sum_{a_j > 0} a_j\, hi_j + \sum_{a_j < 0} a_j\, lo_j
```

return a pair `(verdict, fixings)`:

- `("infeasible", {})` if $`\underline{L} > b`$;
- otherwise `("redundant", {})` if $`\overline{L} \le b`$;
- otherwise `("keep", fixings)`, where `fixings` maps each variable with $`lo_j < hi_j`$ that the row
  forces to a value: $`x_j = 0`$ if $`a_j > 0`$ and $`\underline{L} + a_j > b`$, and $`x_j = 1`$ if
  $`a_j < 0`$ and $`\underline{L} - a_j > b`$. Compute $`\underline{L}`$ once, from the bounds as
  given.

Compare as the lesson's presolve code does, with the tolerance $`\varepsilon = 10^{-9}`$ always
in favour of keeping a row and leaving a variable free. Written out, the reference solution's tests
are:

```math
\begin{aligned}
&\text{infeasible} && \text{if } \underline{L} > b + \varepsilon \\
&\text{redundant} && \text{if } \overline{L} \le b \quad \text{(no tolerance: a row whose } \overline{L} \text{ is above } b \text{ by any amount is kept)} \\
&x_j = 0 && \text{if } a_j > 0 \text{ and } \underline{L} + a_j > b + \varepsilon \\
&x_j = 1 && \text{if } a_j < 0 \text{ and } \underline{L} - a_j > b + \varepsilon
\end{aligned}
```

So a row whose most activity is $`0.1 + 0.2`$ against $`b = 0.3`$ is kept: in floating point that sum
is a hair above 0.3, and deleting a row on a rounding error is the mistake the tolerance guards
against.
