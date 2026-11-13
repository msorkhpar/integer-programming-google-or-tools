A bakery plans how many oven hours go to each of two products, under rules written as rows of
$`Ax \le b`$, and wants the plan with the highest objective $`c^\top x`$. The region is a polygon,
and the best plan can be found at one of its corners.

Write `best_corner(A, b, c, tol=1e-9)` in `corner.py`, for two variables. Try every pair of rows
$`i < k`$:

1. If the two rows are parallel ($`|\det| < 10^{-12}`$ for the 2-by-2 matrix of the pair), skip
   the pair.
2. Otherwise solve $`a_i^\top x = b_i`$, $`a_k^\top x = b_k`$ with `np.linalg.solve`.
3. Keep the crossing only if it is feasible: every row has $`a_r^\top x \le b_r + \text{tol}`$.

Return `(value, (x0, x1))` for the kept crossing with the largest $`c^\top x`$, as Python floats.
Return `None` if no crossing is kept. You may assume the region has at least one corner and that
the objective does not grow without limit on it.

About twelve lines.
