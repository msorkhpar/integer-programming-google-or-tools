A bus operator overhauls its fleet at three depots. Its planners ask the same question many times
a day with one number changed: "what if the budget were 14?", "what if we had 12 staff?". The
depot LP is already written as `build()` in the starter; you write the loop that answers the
questions on one solver, so that each solve can start from the last one.

The given model, with $`h_A, h_B, h_C`$ the overhaul hours at each depot:

```math
\begin{aligned}
\max \;& 6 h_A + 5 h_B + 2 h_C \\
\text{s.t. }& 2 h_A + 2 h_B + h_C \le 20 && \text{(budget)} \\
& h_A + h_B + h_C \le 9 && \text{(staff)} \\
& h_A \ge 3 && \text{(service)} \\
& 0 \le h_A \le 4, \quad 0 \le h_B \le 5, \quad 0 \le h_C \le 10
\end{aligned}
```

Write `run_scenarios(model, rows, scenarios)` in `scenarios.py`. `rows` maps a row's name to its
`LinearConstraint`; each scenario is a dict from row names to new upper bounds (an empty dict is
the base data). For each scenario, in order:

1. set the named rows' `upper_bound`s;
2. solve with one `mathopt.IncrementalSolver(model, mathopt.SolverType.GLOP)`, created once
   before the loop;
3. record the objective value if the termination reason is `OPTIMAL`, otherwise `None`;
4. put the changed bounds back, so the next scenario starts from the base data.

Return the list of recorded values. When the function returns, every row has its base bound
again.
