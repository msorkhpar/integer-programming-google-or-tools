A water utility's meter readers walk one loop a day from their depot. The route planner gets its
distances from a mapping service in kilometers, with decimals, and it has to price a loop with the
OR-Tools routing library. Two functions in `tour.py` are unfinished:

- `build(cost, depot)` makes a one-vehicle routing model from an integer cost matrix, with
  `cost[a][b]` the cost of going from node `a` to node `b` (the matrix need not be symmetric:
  some streets are one-way). The index manager is already there; the arc cost is missing.
- `scaled(km, scale)` turns the kilometers into the integer costs the model needs: each distance
  times `scale`, as an integer.

In the lesson's notation, with $`\text{node}(i)`$ the node of solver index $`i`$, the model must
minimize

```math
\sum_{i} c_{\text{node}(i),\, \text{node}(\text{next}_i)}, \qquad c_{ab} = \operatorname{round}(\text{scale} \cdot d_{ab})
```

where $`d_{ab}`$ is the distance in kilometers and $`\operatorname{round}`$ goes to the nearest
integer. The reference uses Python's built-in `round(scale * d)`, which sends an exact half to the
even neighbour (`round(2.5)` is 2, `round(3.5)` is 4), and returns an `int`; `int(...)` would instead
cut every fraction off, so 12.97 would become 12. Say in your own words which of the two indices the callback receives is the arc's start,
and why it must be converted before it reads the matrix.

The tests price hand-built loops with `ReadAssignmentFromRoutes`, so any correct callback passes.
About six lines in total.
