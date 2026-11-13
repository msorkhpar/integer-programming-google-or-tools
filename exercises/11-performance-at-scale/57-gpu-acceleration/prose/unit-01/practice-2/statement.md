A staffing team buys shifts: shift $`j`$ costs $`c_j`$ and covers $`A_{ij}`$ hours of need $`i`$,
and each need must be covered **at least** $`b_i`$ hours. Their LP, $`\min c^\top x`$ subject to
$`Ax \ge b`$ and $`x \ge 0`$, will be solved by a first-order method, and they need the rule that
says when to stop.

Before you code, write this LP's dual: one price $`y_i \ge 0`$ per row, the dual objective, and the
sign each reduced cost $`c_j - (A^\top y)_j`$ must have when $`x_j`$ has a lower bound of 0 and no
upper bound. Then write PDLP's three relative tests for this form, each with tolerance
$`\varepsilon`$: the gap between the primal and dual objectives, against
$`1 + \lvert\text{primal}\rvert + \lvert\text{dual}\rvert`$; the 2-norm of how far the plan leaves
rows short, against $`1 + \lVert b \rVert_2`$; and the 2-norm of the reduced costs of the wrong sign,
against $`1 + \lVert c \rVert_2`$.

Write `converged(A, b, c, x, y, eps)` in `stopping.py`: True when all three hold. The inputs are
NumPy arrays and `y` is already non-negative. About eight lines.
