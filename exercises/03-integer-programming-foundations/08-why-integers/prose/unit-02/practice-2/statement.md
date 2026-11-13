A rail operator's depot-upgrade team wants every plan it publishes to carry its integrality gap, so
readers can see how close the LP ceiling is to the best plan. Each candidate is a `Project` with a
cost and a value ($k) and an optional `parent`, the project it depends on.

Write two functions in `gap.py`. With $`P`$ the projects, $`C`$ those with a parent $`p(c)`$ and
$`B`$ the budget, the model is

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{value}_i\, x_i \\
\text{s.t. }& \sum_{i \in P} \text{cost}_i\, x_i \le B && && \text{(budget)} \\
& x_c \le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
& x_i \in \{0, 1\} && \forall i \in P && \text{(MILP)} \quad \text{or} \quad 0 \le x_i \le 1 \;\; \text{(LP relaxation)}
\end{aligned}
```

- `solve(projects, budget, integer)` builds this model in MathOpt and returns its optimal value:
  the MILP solved with HiGHS when `integer` is true, the LP relaxation solved with GLOP when it is
  false.
- `integrality_gap(projects, budget)` returns `(lp_bound, optimum, gap)`, where
  $`\text{gap} = (z_{LP} - z_{IP}) / |z_{IP}|`$.

The tests use budgets that some plan fits, so both solves end `OPTIMAL`. About fifteen lines.

Two pieces of the result come from the section 2 lesson *Your first LP: splitting a maintenance
budget across programs*, in its rule *GLOP Solves It: Read the Status, Then the Amounts, Then the Rows*:
`result = mathopt.solve(model, solver_type)` returns the result, `result.termination.reason` says
how the solve ended (compare it with `mathopt.TerminationReason.OPTIMAL`), and
`result.objective_value()` is the optimal value. The reference solution returns
`objective_value()` directly, since the tests' budgets always end `OPTIMAL`.
