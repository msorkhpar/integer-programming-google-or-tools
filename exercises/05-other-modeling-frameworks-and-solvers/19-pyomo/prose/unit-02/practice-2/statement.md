An island grid commits its units each hour: a unit is on or off, and a unit that is on runs
between its minimum and maximum output. The market operator publishes the **price of one more
megawatt** for each hour, and it wants the price of the plan it actually runs, with the on/off
decisions as they are, not of some blend of half-started units.

`commit(units, demand)` in `prices.py` already builds the model:

```math
\begin{aligned}
\min \;& \sum_{u \in U} (\text{fixed}_u\, \text{on}_u + \text{marginal}_u\, \text{mw}_u) \\
& \text{low}_u\, \text{on}_u \le \text{mw}_u \le \text{high}_u\, \text{on}_u && \forall u \in U && \text{(low}_u, \text{high}_u) \\
& \sum_{u \in U} \text{mw}_u = D && && \text{(demand)} \\
& \text{on}_u \in \{0, 1\}, \quad 0 \le \text{mw}_u \le \text{high}_u && \forall u \in U
\end{aligned}
```

Write `price(units, demand)`: return the optimal hourly cost, and the dual value of the `demand`
row for the committed plan. A MILP solve gives no duals, so get them from the LP that is left when
every `on` is fixed at its optimal value: fix them, relax integrality, declare a `dual` Suffix, and
solve again. Use `appsi_highs` with a zero `mip_gap`. About twelve lines.
