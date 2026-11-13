A maintenance team's nightly job solves a small pywraplp model and mails the result to the
supervisors. Last month the model was infeasible for a week, and the mail said "hire 0 crews, cost
0" every night, because the job read `solution_value()` without looking at the status.

Write `outcome(solver, status, x)` in `report.py`. `status` is what `solver.Solve()` returned and
`x` maps names to the solver's variables. Return a dict with three keys:

- `"status"`: the status's name, one of `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `UNBOUNDED`,
  `ABNORMAL`, `MODEL_INVALID`, `NOT_SOLVED` (the `NAMES` table is given);
- `"value"`: the objective value, or `None` when the solve has no solution to report;
- `"plan"`: `{name: value}` for every variable in `x`, or `None` in the same cases.

A solve has a solution to report when the solver found one, whether or not it proved it best.
`crews_model(need, most)` is a small model to try your function on:

```math
\begin{aligned}
\min\;& 5\,x_{\text{line}} + 3\,x_{\text{field}} \\
\text{s.t. }& 2\,x_{\text{line}} + x_{\text{field}} \ge \text{need} && \text{(cover)} \\
& x_{\text{line}}, x_{\text{field}} \in \{0, 1, \dots, \text{most}\}
\end{aligned}
```

About five lines.
