A town's utility must carry a peak load through its substation transformers this winter. Each
transformer is either **repaired** (cheaper, and it then carries a lower rating) or **replaced**
(dearer, with a higher rating). Find the cheapest choice per transformer that carries the load.

In `replace.py`, write `build(assets, demand)` and `plan(assets, demand)`. `assets` maps a name to
`Asset(repair, replace, repaired, new)`: the two costs ($k) and the two ratings (MVA). The model,
with one disjunction per transformer:

```math
\begin{aligned}
\min \;& \sum_{i \in A} \text{cost}_i \\
& \begin{bmatrix} \text{cost}_i \ge \text{repair}_i \\ \text{rating}_i \le \text{repaired}_i \end{bmatrix}
  \vee
  \begin{bmatrix} \text{cost}_i \ge \text{replace}_i \\ \text{rating}_i \le \text{new}_i \end{bmatrix} && \forall i \in A && \text{(choice}_i) \\
& \sum_{i \in A} \text{rating}_i \ge D && && \text{(carry)} \\
& 0 \le \text{cost}_i \le \max(\text{repair}_i, \text{replace}_i), \quad 0 \le \text{rating}_i \le \max(\text{repaired}_i, \text{new}_i) && \forall i \in A
\end{aligned}
```

Write the disjunction with `pyomo.gdp.Disjunction` (repair as its first disjunct, replace as its
second) and name the objective `m.total`. In `plan`, turn it into a MILP with `gdp.bigm`, solve
with `appsi_highs` at a zero `mip_gap`, and return the total cost and a dict from each transformer
to `"repair"` or `"replace"`, read from the disjuncts' `indicator_var`. The fleets in the tests
range from a few hundred $k to a few thousand. About twenty-five lines.
