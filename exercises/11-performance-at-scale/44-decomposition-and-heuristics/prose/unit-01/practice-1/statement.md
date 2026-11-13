A telecom's fiber program plans which ring builds to start in which year. Each build has a value
for every year it may start in, and needs splicing-crew hours in each of its years of work: started
in year $`t`$, build $`i`$ uses $`h_{i,0}`$ hours in $`t`$, $`h_{i,1}`$ in $`t+1`$, and so on. Each year
has $`H_y`$ crew hours. Some builds are must-dos. The full model, with $`x_{i,t} \in \{0,1\}`$:

```math
\begin{aligned}
\max \;& \sum_{i} \sum_{t \in T_i} v_{i,t}\, x_{i,t} \\
& \sum_{t \in T_i} x_{i,t} \le 1 \;\; \forall i \text{ optional}, \qquad \sum_{t \in T_i} x_{i,t} = 1 \;\; \forall i \text{ must-do} && \text{(once}_i) \\
& \sum_{i} \sum_{t \in T_i,\, t \le y} h_{i,\,y-t}\, x_{i,t} \le H_y \quad \forall y && \text{(crews}_y)
\end{aligned}
```

The crew rows are the only rows that tie builds together. The planners want a quick upper bound on
the best plan's value, for any set of nonnegative prices $`\mu_y`$ per crew hour.

Write the Lagrangian relaxation of the crew rows first: the bound $`L(\mu)`$ as a formula, and what
each build chooses on its own once those rows are priced. Then write
`crew_bound(builds, hours, prices)` to return `(bound, plan)`: the value $`L(\mu)`$ and the
relaxed plan that reaches it, as a dict from build name to start year (builds not started are left
out). `builds[name]` holds `"value"` (start year to value), `"hours"` (hours by year of work, a
list) and `"must"` (a bool); `hours` and `prices` are dicts by year, with a price for every year a
build can be worked in. When two choices of a build are worth exactly the same, either may be
returned.

No solver is needed: about ten lines of plain Python.
