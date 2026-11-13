The substation team now wants the stocking plan itself. Some spares *must* be stocked (a regulator
requires them); the rest compete for what is left of the budget. `bound` and `by_ratio` are written
for you in `search.py`; you write the search.

The model, with $`S`$ the spares, $`M \subseteq S`$ the must-stock ones and $`D = S \setminus M`$:

```math
\begin{aligned}
\max \;& \sum_{i \in M} v_i + \sum_{i \in D} v_i\, x_i \\
\text{s.t. }& \sum_{i \in D} c_i\, x_i \le \text{budget} - \sum_{i \in M} c_i && \text{(budget)} \\
& x_i \in \{0, 1\} \quad \forall i \in D
\end{aligned}
```

Write `best_plan(items, budget, must)`. `items` is a list of `(name, value, cost)` with whole values
and costs above 0, and `must` a set of names. Return `(value, names)`: the best plan's total value,
must-stock items included, and the sorted list of every stocked name. Return `None` when the
must-stock items alone cost more than the budget.

Use the given pieces as lesson 3.2.4's search does: sort the free items once with `by_ratio`, keep
a stack of fixings (dicts from name to 0 or 1, starting with `{}`), and at each node call
`bound(order, budget_left, fixed)`, which returns `None` for an infeasible node or
`(value, split, taken)`. Prune infeasible nodes, prune a node when
$`\lfloor \text{value} \rfloor`$ is not above the incumbent, take `taken` as the new plan when
`split` is `None`, and otherwise push the children `split = 0` and `split = 1`.
