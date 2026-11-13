A city transit agency chooses which bus orders to place this year. A colleague built the model in
`fleet.py` from three sources: order values in dollars from the finance system, the budget and the
overdraft in $M from the board pack, and a switch row with $`M = 10^9`$. It gives the right plan,
but its matrix spans more than nine powers of ten, which lesson 10.1.2 showed is outside the safe
range.

The colleague's model, `build_raw()`, with $`J`$ the orders, $`p_j`$ and $`v_j`$ an order's price
and value in dollars, $`B`$ the budget, $`L`$ the overdraft limit and $`F`$ the arrangement fee, all
in dollars:

```math
\begin{aligned}
\max \;& \sum_{j \in J} v_j\, b_j - F a \\
\text{s.t. }& \sum_{j \in J} \frac{p_j}{10^6}\, b_j \le \frac{B}{10^6} + d && \text{(budget)} \\
& d \le \frac{L}{10^6} && \text{(limit)} \\
& d \le 10^9\, a && \text{(switch)} \\
& b_j \in \{0, 1\} \;\; \forall j \in J, \quad a \in \{0, 1\}, \quad d \ge 0 \text{ (the overdraft, in \$M)}
\end{aligned}
```

Write the rescaled model first, in this notation: every amount (the objective, the rows and the
overdraft variable $`d`$) in $k, and the switch row's $`M`$ replaced by the smallest value the data
make valid. Then write `build_scaled()` to build it, returning a `Fleet` with the same fields as
`build_raw()`, the overdraft now in $k.

The tests fix a plan (which orders, the overdraft in $k, whether it is arranged), ask the solver
whether it is allowed, and read its objective; they also check that the matrix span (largest
absolute coefficient over smallest) is below 10,000. About eight lines.
