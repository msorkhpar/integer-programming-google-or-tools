A city's parks department picks which playground renovations to fund this year. The candidates sit
in a pandas DataFrame with the columns `project_id`, `cost` and `value` (both in $k) and `must_do`
(a bool: safety work that must be funded). The department wants one function it can run on HiGHS,
SCIP or CP-SAT and get the same answer.

The model, with $`P`$ the rows of the DataFrame and $`B`$ the budget:

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{value}_i\, x_i \\
\text{s.t. }& \sum_{i \in P} \text{cost}_i\, x_i \le B && && \text{(budget)} \\
& x_i = 1 && \forall i \in P \text{ with must\_do}_i && \text{(must}_i) \\
& x_i \in \{0, 1\} && \forall i \in P
\end{aligned}
```

Write `solve_selection(df, budget, solver)` in `selection.py`. It returns a pair: the objective value
of the plan, and the sorted list of the `project_id`s it funds (those whose $`x_i`$ is above 0.5).

- `solver` is a `mathopt.SolverType`. If it is one of `LP_ONLY` (GLOP and PDLP, which refuse integer
  variables), raise `ValueError` with the solver's name in the message, before building or solving
  anything, so the caller never meets OR-Tools' own refusal.
- If the solve ends with any reason other than `OPTIMAL`, raise `RuntimeError` with the reason's name
  in the message.
