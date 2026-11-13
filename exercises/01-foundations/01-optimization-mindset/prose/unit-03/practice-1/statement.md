A harbor authority keeps its quay repairs in a list of `Project` records: a cost, a value (both in
$k) and a `must_do` flag for repairs an inspector has ordered. Its analysts want one function that
builds the selection model, solves it and hands back an answer they can trust, including the day
the budget cannot even cover the ordered repairs.

Write `solve_plan(projects, budget)` in `solve.py`. It builds and solves this model with HiGHS,
with $`P`$ the projects, $`M \subseteq P`$ the must-do ones and $`B`$ the budget:

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{value}_i\, x_i \\
\text{s.t. }& \sum_{i \in P} \text{cost}_i\, x_i \le B && && \text{(budget)} \\
& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& x_i \in \{0, 1\} && \forall i \in P
\end{aligned}
```

It returns a tuple `(status, value, plan)`. `status` is the name of the solve's termination reason
(`"OPTIMAL"`, `"INFEASIBLE"`, ...). When the status is `OPTIMAL`, `value` is the objective value and
`plan` the frozenset of funded project ids; otherwise both are `None`, because a solve that found
no plan has no value to report.

About fifteen lines: the five parts of the lesson's program, in order.
