A water authority renews its pipes district by district, and any number of kilometres can be
renewed, fractions included. Its analysts are moving the model from one solver to another and want
a check that runs in their test suite: the same model on GLOP, HiGHS and PDLP, and a verdict on
whether the three answers agree.

Each `District` has a value and a cost per kilometre (both in $k), crew hours per kilometre, a most
it may renew and a least a regulator has ordered (`min_km`, 0 when there is no order). With $`D`$ the
districts, $`B`$ the budget and $`H`$ the crew hours:

```math
\begin{aligned}
\max \;& \sum_{d \in D} \text{value}_d\, k_d \\
\text{s.t. }& \sum_{d \in D} \text{cost}_d\, k_d \le B && && \text{(budget)} \\
& \sum_{d \in D} \text{hours}_d\, k_d \le H && && \text{(crews)} \\
& \text{min}_d \le k_d \le \text{max}_d && \forall d \in D
\end{aligned}
```

Write three functions in `renewal.py`:

- `solve_on(districts, budget, hours, solver)` builds this model, solves it with the given
  `mathopt.SolverType`, and returns the objective value when the status is `OPTIMAL`, otherwise
  `None`.
- `relative_gap(a, b)` returns $`|a - b| / \max(1, |a|, |b|)`$.
- `all_agree(values, tol=1e-6)` takes a dict from solver name to value (or `None`) and returns
  `True` only when every solver returned a value and every pair has a relative gap of at most `tol`.

Exact equality is the wrong test: PDLP stops as soon as its answer is within its tolerance, so its
objective may differ from a simplex solver's in the seventh significant digit.
