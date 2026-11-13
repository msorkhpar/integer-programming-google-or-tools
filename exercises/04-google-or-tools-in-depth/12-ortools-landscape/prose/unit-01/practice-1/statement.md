A school district (not GridCap) funds building repairs from a yearly budget. Its finance office keeps
every cost in millions of dollars with two decimals (`1.15` is $1,150,000), and wants the pick made
in CP-SAT, because its other planning models already use it.

Write `pick(values, costs, budget)` in `pick.py`. It returns the indices of the repairs to fund, in
increasing order, for this model:

**Sets.** $`I = \{0, 1, \dots, n-1\}`$, the repairs.

**Parameters.** $`v_i`$, the value of repair $`i`$ (a score, with up to two decimals); $`c_i`$, its
cost ($M, two decimals); $`B`$, the budget ($M, two decimals).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in I`$.

```math
\begin{aligned}
\max \;& \sum_{i \in I} v_i\, x_i \\
\text{s.t. } & \sum_{i \in I} c_i\, x_i \le B && \text{(budget)}
\end{aligned}
```

CP-SAT accepts whole numbers only in a row, so state the budget row in hundredths of a million, where
every cost and the budget are whole. Turn each number into hundredths with care: a value such as
`1.15 * 100` is not exactly 115 in floating point. Use `cp_model.CpModel`, `new_bool_var`, `add`,
`maximize` and `cp_model.CpSolver`, as lesson 4.1.1 did. About ten lines.

Two facts from the lesson you will need. CP-SAT's objective accepts decimal coefficients, so the
values may stay as they are, or be scaled to hundredths like the costs; either gives the same pick.
And `solver.solve(model)` returns a status: read the plan only when it is `cp_model.OPTIMAL` or
`cp_model.FEASIBLE`. Funding nothing always fits the budget, so this model always has a plan.
