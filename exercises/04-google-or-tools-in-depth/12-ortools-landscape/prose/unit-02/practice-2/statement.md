A wholesaler (not GridCap) ships whole pallets from warehouses to stores along lanes, each lane with
a capacity (pallets) and a cost per pallet. Its dashboard shows a cost for every plan, and last month
it showed $0 for a plan that could not be shipped at all: the code read the cost without reading the
solver's status first.

Write `ship(lanes, supply)` in `shipping.py` with `min_cost_flow.SimpleMinCostFlow`. `lanes` is a
list of `(from_node, to_node, capacity, cost_per_pallet)` with whole numbers; `supply[n]` is what
node `n` sends (positive) or receives (negative). Return:

- the least total cost, an `int`, when the status `solve()` returns equals the solver's own
  `OPTIMAL` (`status == flow.OPTIMAL`, with `flow` your `SimpleMinCostFlow`);
- otherwise the status's name, a `str` such as `"INFEASIBLE"` or `"UNBALANCED"` (`status.name`).

The model the solver takes, with $`x_a`$ the pallets on lane $`a`$:

```math
\begin{aligned}
\min \;& \sum_{a \in A} k_a\, x_a \\
\text{s.t. } & \sum_{a \text{ leaves } n} x_a - \sum_{a \text{ enters } n} x_a = s_n && \forall n && \text{(balance}_n) \\
& 0 \le x_a \le u_a,\; x_a \in \mathbb{Z} && \forall a \in A && \text{(capacity}_a)
\end{aligned}
```

Use `add_arc_with_capacity_and_unit_cost`, `set_node_supply`, `solve()` and `optimal_cost()`. The
flow solvers raise nothing for an impossible plan: the status is the only place it shows. About ten
lines.
