A city's roads department is choosing which streets to rebuild next summer. Rebuilding streets at
the same time causes extra traffic costs that a street-by-street price list misses:

- **Detours.** For each pair of adjacent streets in `detours` (a dict from `(a, b)` to a cost in
  $k), rebuilding *both* in the same summer needs a temporary detour route, which costs that amount.
  Rebuilding only one of them needs no detour.
- **Corridor fees.** Each `(streets, fee)` in `corridor_fees` is a corridor of several streets. If
  *every* street of the corridor is rebuilt, the police charge a corridor-wide traffic-management
  fee. If only some of them are, there is no fee. A corridor may have any number of streets.

The plan's spend (street costs plus detours plus corridor fees) must not exceed `budget`. The model
in `streets.py` has a binary `x[sid]` per street (1 if rebuilt) and no budget row yet. Write
`add_traffic_costs(model, x, streets, detours, corridor_fees, budget)` so that the model allows
exactly the plans whose real spend fits the budget. Add whatever variables you need.

With $`S`$ the streets and $`c_s`$ the cost of street $`s`$ ($k), the model so far is only

```math
x_s \in \{0, 1\} \quad \forall s \in S \qquad \text{(rebuild street } s\text{)}
```

The real spend has products of binaries in it. Write the spend with those products first, then
replace each by a new variable with its domain and the rows that make it equal to the product
wherever it matters. Decide for each new variable which way the solver would like to move it.

The tests fix which streets are rebuilt and ask the solver whether the model accepts the plan, so
any correct formulation passes. About ten lines.
