The heating crew's whiteboard region now has its corners listed. The team lead wants the best plan
read off them for any objective: the most hours of value for a maximize, the least cost for a
minimize, and, when two corners are equally good, both of them, because then every plan on the
edge between them is equally good too.

Write `best_corners(corners, c, sense)` in `best.py`. `corners` is the list of corners of a
bounded two-variable region (as `vertices` returned them), `c = (c_x, c_y)` the objective, and
`sense` either `"max"` or `"min"`. The LP is

```math
\max \text{ (or } \min\text{)} \;\; c_x\, x + c_y\, y \quad \text{over the region whose corners are given}
```

and its optimum, if the region is not empty, is reached at a corner. Return a tuple
`(value, best)`: `value` is the best objective value over the corners, and `best` is the sorted
list of every corner whose value is within `TOL` ($`10^{-9}`$) of it. An empty list of corners
means the region is empty and the LP has no optimum: return `(None, [])`.
