A port authority plans which ships use its berths. Each berth has a load limit that may be exceeded
**only if** a tug is assigned to it, and the planning model writes every such rule as a big-M row,
switched by the tug's binary. The authority's operations team does not trust a solver status: after
every solve, it wants a list of the berth rules that the returned values break while their tug counts
as not assigned.

Write `leaks(values, rows, tol)` in `audit.py`. `values` maps each variable's name to the value the
solver returned. Each row is a dict: its `name`, its `terms` (variable name to coefficient), its
`limit`, and the name of its `switch` variable. Read the rule each row states, "the sum of the terms
stays within the limit unless the switch is on", the way a planner would: decide whether the switch
is on as a planner reads a binary, and allow the sum to exceed the limit by at most `tol`, since the
values come from floating-point arithmetic. Return the names of the broken rows, in the order the
rows are given.

In symbols, for a row $`r`$ with terms $`a_{r,v}`$, limit $`b_r`$ and switch $`z_r`$, and the solver's
values $`\hat x`$:

```math
r \text{ is reported} \iff \text{?}
```

Write the condition first, then code it. Which value of the switch should count as "on" when the
solver returned 0.4?

The tests pass hand-made values and rows and check the list returned. About eight lines.
