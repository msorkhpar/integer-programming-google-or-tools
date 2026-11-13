A water utility wants to see how much value its pipe-renewal list delivers at several budgets
before the board picks one. Each renewal has a cost and a value ($k); a renewal is funded whole or
not at all. The analyst's old script built a fresh model for every budget, and on the real list
that rebuild is most of the run time.

In `sweep.py`, write:

- `build(projects, budget)`: a Pyomo model of the selection below, where `projects` maps a name
  to `(cost, value)`. The budget must be a **mutable** Param named `m.budget`, and the objective
  must be named `m.total`.
- `sweep(projects, budgets)`: call `build` **once**, then for each budget in the list set
  `m.budget`, solve with `appsi_highs` at a zero `mip_gap`, and record the value of `m.total`.
  Return the values in the order of `budgets`.

```math
\begin{aligned}
\max \;& \sum_{p \in P} \text{value}_p\, x_p \\
& \sum_{p \in P} \text{cost}_p\, x_p \le B && \text{(spend)} \\
& x_p \in \{0, 1\} && \forall p \in P
\end{aligned}
```

The tests check every value and count how many times `sweep` calls `build`. About twenty lines.
