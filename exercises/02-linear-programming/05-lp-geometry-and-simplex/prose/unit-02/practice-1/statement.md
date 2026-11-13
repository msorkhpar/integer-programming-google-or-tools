A small simplex is being written for a water utility's pump-scheduling LP, and its first job is to
decide each step: which variable enters the basis, and which row's basic variable leaves.

Write `choose_pivot(T)` in `pivots.py`. `T` is a tableau for $`\max c \cdot x`$ subject to
$`Ax \le b`$, $`x \ge 0`$: one list per constraint row, each ending with its right-hand side, then a
last row for the objective (its entries are the reduced costs, its last number the current value).
Return the pivot as `(r, k)`:

- **Entering column** $`k`$: the column, among all but the last, with the most negative entry in
  the objective row (the lowest column index on a tie). If no entry is below $`-10^{-9}`$
  (`-EPS`), the tableau is optimal: return `None`.
- **Leaving row** $`r`$, by the ratio test over the constraint rows:

```math
r = \arg\min_{i} \left\{ \frac{T_{i,\text{rhs}}}{T_{i,k}} \;:\; T_{i,k} > 10^{-9} \right\}
```

  with the lowest row index on a tie.

You may assume that, whenever a column enters, at least one constraint row has a positive entry in
it (lesson 2.2.3 handles the case where none does).
