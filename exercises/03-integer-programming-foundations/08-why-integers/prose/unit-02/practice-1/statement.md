A retail chain picks which shop refits to fund from one budget. Some refits are ordered by a
safety inspector (`must_do`). Before running a solver, its analyst wants the ceiling on what any
plan can be worth, computed without one.

Write `fractional_bound(projects, budget)` in `bound.py`. It returns the optimal value of this LP
relaxation, with $`P`$ the projects and $`M`$ the must-do ones:

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{value}_i\, x_i \\
\text{s.t. }& \sum_{i \in P} \text{cost}_i\, x_i \le B && && \text{(budget)} \\
& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& 0 \le x_i \le 1 && \forall i \in P
\end{aligned}
```

Compute it by hand, with no solver: pay for every must-do project in full; then go through the
other projects in decreasing order of $`\text{value}_i / \text{cost}_i`$, funding each one whole
while it fits; the first that does not fit gets the share $`\text{room} / \text{cost}_i`$ that the
remaining room buys, and you stop. The tests' must-do projects always fit the budget, and their
ratios are all different.

About ten lines.
