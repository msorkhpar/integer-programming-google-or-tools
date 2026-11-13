A transmission operator (not GridCap) plans its substation jobs for next season. Several limited
resources are shared: the mobile crane's days, the outage hours the grid operator grants, the budget.
Each is a knapsack row,

```math
\sum_{j \in J} u_{\ell,j}\, x_j \le U_\ell \qquad \forall \ell \in L \qquad \text{(limit}_\ell)
```

with $`x_j \in \{0, 1\}`$ (do job $`j`$), $`u_{\ell,j}`$ the whole amount of resource $`\ell`$ that job
$`j`$ uses and $`U_\ell`$ what is available. `build` in `jobs.py` already writes these rows and
the objective.

The planners noticed that some jobs are so big that no two of them fit under the same limit, and
that the LP relaxation ignores this: it happily takes one big job and part of another. Write
`add_big_item_rows(model, x, limits)`, which adds rows that

- every whole plan that fits all the limits still satisfies (so no plan the limits allow is lost),
  and
- stop the LP from combining big jobs: for each limit, the jobs no two of which fit together under
  it may be funded at most one at a time, and a job that does not fit under a limit even on its own
  is never funded, not even in part.

Each such row comes from a cover of one limit's row, a cover of two jobs or of one. Decide on paper
which jobs belong to a limit's row, why "no two of them fit" is a simple test on each job's own use,
and write the rows with their labels before coding. When a limit has only one big job, the
reference writes no "at most one" row for it: that row would read $`x_j \le 1`$, which the
variable's bound already says (a job too big even on its own still gets its "never" row).

The tests try every whole plan of five jobs against the limits, and compare the LP bound with the
value the right rows give, so any correct set of valid rows passes. About seven lines.
