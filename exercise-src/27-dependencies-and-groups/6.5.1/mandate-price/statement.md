A city parks department picks this year's projects under one budget. Each project has a cost and
a value (both in $k), and some are **mandated**: a court order or a safety inspection requires
them. The council asks the question every planner hears: what do the mandates cost us?

Write two functions in `parks.py`:

- `best_value(projects, budget, enforced)`: the value of the best selection that fits the budget,
  in which every project in `enforced` is funded. A mandated project that is not in `enforced` is
  treated like any other project: the selection may fund it or not.
- `mandate_costs(projects, budget)`: a dict with one entry per mandated project, its cost, and one
  entry `"all"`, the cost of every mandate together. A mandate's cost is how much more the best
  selection is worth when that mandate (or, for `"all"`, every mandate) is lifted.

Every instance in the tests can fund all its mandates within the budget.

Write the model of `best_value` first, with $`P`$ the projects, $`E \subseteq P`$ the enforced
ones, $`c_i`$ and $`v_i`$ the cost and value, and $`B`$ the budget: the variables with their
domains, the objective, and each row with its label. Then decide, for each entry of
`mandate_costs`, which `enforced` sets it compares. Before you code `"all"`, ask whether the
single costs can tell you its value.

The tests compare your numbers with values worked out by hand on small instances. About fifteen
lines.
