After a storm the generator firm of the previous practice ships real units, and now each route has
a cost per generator as well as a capacity. The yards may hold more generators than the towns need;
the rest stay where they are. A plan that leaves some town short is no plan: the dispatcher must
hear that the needs cannot be met.

Write `ship(stock, needs, routes)` in `shipping.py`, using `SimpleMinCostFlow`. `routes` maps
`(from, to)` to `(cost per unit, capacity)`. Return `(total cost, {(from, to): units})`, listing
only routes that carry at least one generator, or `None` when the towns' needs cannot all be met.

The problem, with $`x_{ij}`$ the generators sent along route $`(i, j)`$:

```math
\begin{aligned}
\min\;& \sum_{(i,j)} c_{ij}\, x_{ij} \\
\text{s.t. }& \text{out of } y - \text{into } y \le \text{stock}_y && \text{for every yard } y \\
& \text{into } w - \text{out of } w = \text{need}_w && \text{for every town } w \\
& \text{into } n - \text{out of } n = 0 && \text{for every other place } n \\
& 0 \le x_{ij} \le u_{ij}, \ \text{integer}
\end{aligned}
```

The yard rows are "at most", while `solve()` needs every supply met exactly: pick the call, or the
extra node, that handles stock left behind, and check the result before you trust it. About fifteen
lines.
