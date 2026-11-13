A school district picks which building repairs to fund this summer, with a binary $`x_j`$ per
repair, value $`v_j`$, cost $`c_j`$ and one budget row:

```math
\max \sum_j v_j x_j \quad \text{s.t.} \quad \sum_j c_j x_j \le B \;\; \text{(budget)}, \qquad x_j \in \{0, 1\}
```

The board wants the best value under several cuts of $`B`$: for each share $`s`$ in `cuts`, the
optimum with the budget row's limit at $`(1 - s) B`$, where $`B`$ is the limit the row has when the
function is called.

Write `cut_table(model, budget_row, cuts)`, which returns a list with the optimal objective value for
each share, in order. Use one `mathopt.IncrementalSolver` on HiGHS for all of them, and edit the
row's `upper_bound` rather than building anything new. When the function returns, the model must be
exactly as it was, limit included. About ten lines.
