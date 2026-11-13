A city parks department plans its maintenance spending over several years. Each year has a budget,
an amount of work its crews can actually do, and a value per $k of work (later years are worth a
little less, as discounting makes them). Council lets a year roll unspent money into the next year,
but at most a share `max_carry` of the budget of the year the money leaves. Money a year neither
spends nor carries lapses at year end.

With $`Y`$ the years in order, $`y_0`$ the first (in order means sorted by year, smallest first,
whatever order the dict's keys come in: money carried out of a year goes into the next larger year
among the keys), $`B_y`$ the budget, $`w_y`$ the work available,
$`v_y`$ the value per $k and $`\gamma`$ the carry share:

```math
\begin{aligned}
\max \;& \sum_{y \in Y} v_y\, x_y \\
\text{s.t. }& x_y + r_y \le B_y + r_{y-1} && \forall y \in Y && \text{(cash}_y),\ r_{y_0 - 1} = 0 \\
& 0 \le x_y \le w_y && \forall y \in Y \\
& 0 \le r_y \le \gamma\, B_y && \forall y \in Y
\end{aligned}
```

$`x_y`$ is the $k spent in year $`y`$ and $`r_y`$ the $k carried out of it, both continuous. Write
`plan_spending(budgets, work, value, max_carry)` in `carry.py`; the three dicts are keyed by year.
It solves the model with GLOP and returns `(status, value, spend, carry)`: the name of the
termination reason; when it is `OPTIMAL`, the objective value and two dicts by year, the spend and
the carry (not rounded, every year included); otherwise `None, None, None`.

About fifteen lines.
