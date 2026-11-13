A substation team picks spare transformers to stock: each candidate has a value (avoided outage
cost) and a price, and one budget covers them all. Their branch-and-bound needs the LP bound at a
node without calling an LP solver.

Write `bound(items, budget, fixed)` in `bound.py`. `items` is a list of `(name, value, cost)`
tuples with every cost above 0, in any order. `fixed` maps some names to 0 or 1. The node's LP is

```math
\max \Big\{ \sum_i v_i x_i \;:\; \sum_i c_i x_i \le \text{budget},\ 0 \le x_i \le 1,\
x_i = \text{fixed}_i \text{ for every fixed } i \Big\}
```

Compute it with Dantzig's fill: pay for the items fixed at 1; skip the items fixed at 0; then go
through the free items by ratio $`v_i / c_i`$, highest first (ties by name), taking each one whole
while it fits, and taking the fraction of the first one that does not fit that uses up what is
left. Stop there.

Return `(value, split)`: the LP value, and the name of the item taken in part, or `None` when no
item is taken in part. Return `None` instead of a pair when the items fixed at 1 cost more than the
budget.

A budget used up exactly is not a split. When the whole items leave exactly 0 of the budget, the
next item would be taken to the fraction 0, which is not taking it at all, so the reference returns
`(value, None)`. Fixings that cost exactly the budget are allowed too: they leave 0, not less, so
the node is feasible and its bound is the fixed items' value.
