A port authority splits its maintenance budget across its terminals. Each terminal returns a value
per $k spent, its work needs dock-crew hours per $k, it has a number of crew hours available, and
some terminals have a floor the harbor board requires them to get. The authority wants the best
split and, just as much, an answer it can read: did the solve succeed, what does each terminal get,
and which limits decided it.

With $`T`$ the terminals, $`v_t`$ the value per $k, $`h_t`$ the crew hours per $k, $`H_t`$ the hours
available, $`f_t`$ the floor and $`B`$ the budget:

```math
\begin{aligned}
\max \;& \sum_{t \in T} v_t\, x_t \\
\text{s.t. }& \sum_{t \in T} x_t \le B && && \text{(budget)} \\
& h_t\, x_t \le H_t && \forall t \in T && \text{(labour}_t) \\
& x_t \ge f_t && \forall t \in T,\ f_t > 0 && \text{(floor}_t) \\
& x_t \ge 0 && \forall t \in T
\end{aligned}
```

$`x_t`$ is continuous, in $k. Write `split(terminals, budget)` in `split.py`. It builds this model
with the row names shown (`budget`, `labour_north`, `floor_east`, ...; a terminal with floor 0 gets
no floor row), solves it with GLOP and returns `(status, value, amounts, full)`:

- `status`: the name of the termination reason, such as `"OPTIMAL"` or `"INFEASIBLE"`;
- when the status is `OPTIMAL`: `value`, the objective value; `amounts`, a dict from terminal name
  to its amount, not rounded; and `full`, the set of names of the rows whose activity is within
  `TOL` ($`10^{-6}`$) of their lower or their upper bound;
- otherwise `None, None, None`, because a solve that found no split has nothing to report.

About twenty lines.
