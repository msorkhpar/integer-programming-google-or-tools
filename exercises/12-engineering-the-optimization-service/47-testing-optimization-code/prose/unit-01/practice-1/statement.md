A hospital plans its equipment renewals with a small model, and its engineers want unit tests of
the form "this plan must be allowed, that one refused". They need one helper first:
`verdicts(model, x, plans)`, which says, for each plan in a list, whether the model accepts it.

The model the tests build, for projects $`i`$ with start windows $`T_i`$ and a cost $`c_i`$ paid in
the start year:

```math
\begin{aligned}
& x_{i,t} \in \{0,1\} \ \ \forall i,\ t \in T_i, \qquad 0 \le o_t \le 30 \ \ \forall t \in \{2027, 2028\} \\
& \sum_{t \in T_i} x_{i,t} \le 1 && \forall i && \text{(once}_i) \\
& x_{\text{boiler},2027} = 1 && && \text{(must\_boiler)} \\
& \sum_{i:\, t \in T_i} c_i\, x_{i,t} \le 80 + o_t && \forall t && \text{(budget}_t)
\end{aligned}
```

$`o_t`$ is overtime spending, which the hospital may use when a year runs over. It has no objective;
any plan that meets the rows is acceptable.

Write `verdicts(model, x, plans)`. `x` maps each `(project, year)` to its start variable, and each
plan maps each started project to its start year; every project not in a plan is not started.
Return one answer per plan, in order: `True` when the model accepts exactly that plan, `False` when
it refuses it. A plan that starts a project in a year the project has no variable for is refused.
Solve with HiGHS through MathOpt.

The engineers share one model between many questions, and a planner may already have fixed a start
by its bounds (an override). While a plan is being asked, the plan alone decides every start: fix
each start variable to 1 or 0 as the plan says, replacing whatever bounds it had, an override's
included. When `verdicts` returns, put the bounds back, so every start variable has the bounds it
had when the function was called. About twelve lines.
