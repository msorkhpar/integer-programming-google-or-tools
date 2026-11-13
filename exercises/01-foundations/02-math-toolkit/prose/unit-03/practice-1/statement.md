A materials yard plans how many tonnes of each material to stock, under rules written as rows of
$`Ax \le b`$. Its optimizer reports a plan, and the yard's analyst wants to check that the plan is
a corner of the allowed region, as the optimum of a linear objective can always be chosen to be.

Write `is_extreme_point(A, b, x, tol=1e-9)` in `extreme.py`. `A` has one column per variable, so
there are $`n`$ = `A.shape[1]` variables. Return `True` when `x` is an extreme point of
$`\{x : Ax \le b\}`$:

1. `x` is feasible: every row has $`a_r^\top x \le b_r + \text{tol}`$;
2. among the **tight** rows, those with $`|a_r^\top x - b_r| \le \text{tol}`$, there are $`n`$
   linearly independent ones. `np.linalg.matrix_rank(M)` returns how many independent rows `M`
   has.

Otherwise return `False`. Return a Python `bool`. The function must work for any number of
variables, not only two.

About six lines.
