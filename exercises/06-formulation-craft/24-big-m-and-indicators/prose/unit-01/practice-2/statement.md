A warehouse ships orders to a utility's storeroom. Each order ships this week by at most one of its
options (a small truck, a big truck, rail, ...), and each option unloads a known number of pallets at
dock D, or none if it goes to another dock. Dock D takes at most `capacity` pallets a week,
**unless** the overflow yard is opened, a binary decision.

`choice_variables` (given) creates a binary $`c_{o,k}`$ for each order $`o`$ and option $`k`$, and
the row "at most one option per order". Write two functions in `dock.py`:

- `dock_m(orders, capacity)`: the smallest $`M`$ for dock D's row that the "at most one option per
  order" rows justify (no solve). `orders[o][k]` is the pallets option $`k`$ of order $`o`$ unloads at
  dock D.
- `add_dock_row(model, choose, orders, capacity, overflow)`: dock D's row, switched by `overflow`,
  using `dock_m`.

The model so far, with $`p_{o,k}`$ the pallets, $`K`$ the capacity and $`v`$ the overflow binary:

```math
\begin{aligned}
& c_{o,k} \in \{0, 1\}, \quad v \in \{0, 1\} && \forall o,\ k \\
& \textstyle\sum_{k} c_{o,k} \le 1 && \forall o \quad \text{(one}_o) \\
& \text{?} && \text{(dock\_D)}
\end{aligned}
```

Write the row and the formula for $`M`$ in this notation first, then code them. Check $`M`$ by hand
on a two-order example before running the tests, and decide what $`M`$ must be when the dock can
never be over capacity.

The tests fix a plan by its variables' bounds and ask the solver whether it is allowed, so any
correct row passes; two more tests check the value `dock_m` returns. About four lines.
