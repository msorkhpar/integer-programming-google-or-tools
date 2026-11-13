A rural telecom carrier is choosing which tower and backhaul upgrades to build this year. Two
contract terms change what a plan really costs:

- **Permits.** Some upgrades need a permit, for example to cross the river. Each permit in
  `permits` maps a name to `(fee, projects)`: the fee is paid **once** if *any* of its projects is
  funded, however many of them are, and not at all if none is.
- **Bundle discounts.** Each `(tower, backhaul, discount)` in `bundles` takes `discount` ($k) off
  the plan's spend when *both* the tower and its backhaul link are funded.

The plan's spend (project costs, plus permit fees, minus bundle discounts) must not exceed
`budget`. The model in `towers.py` has a binary `x[pid]` for each upgrade (1 if funded) and no
budget row yet. Write `add_fee_rules(model, x, projects, permits, bundles, budget)` so that the
model allows exactly the plans whose real spend fits the budget. Add whatever variables you need.

With $`P`$ the upgrades and $`c_p`$ the cost of upgrade $`p`$ ($k), the model so far is only

```math
x_p \in \{0, 1\} \quad \forall p \in P \qquad \text{(build upgrade } p\text{)}
```

Write the rest first: each new variable with its domain, the rows that tie it to the $`x_p`$, and
the budget row, each labelled. For each new variable, decide which way the solver would like to move
it, and make sure your rows stop it.

The tests fix which upgrades are built and ask the solver whether the model accepts the plan, so any
correct formulation passes. About twelve lines.
