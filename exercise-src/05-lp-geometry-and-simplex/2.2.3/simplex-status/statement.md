The pump-scheduling simplex can pivot. Now it must run on its own and say how it ended, including
on the two kinds of model that trip up a first implementation: one whose objective can grow
without limit, and one with a vertex where several rows are tight.

In `simplex.py`, `pivot` and `entering` (Dantzig's rule, `None` at an optimum) are given. Write:

- `ratio_row(T, k)`: the leaving row for entering column `k`,

  ```math
  r = \arg\min_{i} \left\{ \frac{T_{i,\text{rhs}}}{T_{i,k}} \;:\; T_{i,k} > 10^{-9} \right\}
  ```

  over the constraint rows (every row but the last), the lowest row index on a tie, and `None` when
  no constraint row has an entry above $`10^{-9}`$ in column `k`.
- `run_simplex(T, max_steps=100)`: repeat until done, at most `max_steps` pivots. Take the entering
  column; if there is none, return `("OPTIMAL", value)` with the value in the objective row's last
  entry. Take the ratio row; if there is none, the LP is unbounded: return `("UNBOUNDED", None)`.
  Otherwise pivot and continue. If the steps run out, return `("STEP_LIMIT", None)`. The optimum
  is recognized only at the start of a step, by finding no entering column, and that check costs
  no pivot. So if the `max_steps`-th pivot lands on the optimum, there is no step left to see it,
  and the status is `STEP_LIMIT`: with `max_steps=2`, an LP that needs exactly two pivots ends
  `STEP_LIMIT`, and with `max_steps=3` it ends `OPTIMAL`.

`T` is a tableau for $`\max c \cdot x`$, $`Ax \le b`$, $`x \ge 0`$ with $`b \ge 0`$: constraint
rows $`[A \mid I \mid b]`$, then the objective row $`[-c \mid 0 \mid 0]`$.
