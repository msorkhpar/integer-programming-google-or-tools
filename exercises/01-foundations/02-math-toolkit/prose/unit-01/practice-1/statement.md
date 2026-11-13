A field-operations team plans work orders against crew-hour limits. Each row of a matrix `A` is
one crew, each column one work order, and `b` holds each crew's hours. A plan `x` gives how many
times each work order is done. The team wants a checker that says whether a plan fits, and when it
does not, which crews it overloads.

Write two functions in `check.py`. `A`, `b` and `x` are NumPy arrays, and the data may be
fractional.

| function | returns |
| --- | --- |
| `broken_rows(A, b, x, tol=1e-9)` | the indices of the rows with $`a_r^\top x > b_r + \text{tol}`$, as a list of ints in increasing order |
| `is_feasible(A, b, x, tol=1e-9)` | `True` when every row satisfies $`a_r^\top x \le b_r + \text{tol}`$, else `False` (a Python `bool`) |

A row whose activity equals its limit holds. A row that misses its limit by no more than `tol`
holds too, because fractional sums can land a hair off.

About four lines in total, with no Python loop over the rows.
