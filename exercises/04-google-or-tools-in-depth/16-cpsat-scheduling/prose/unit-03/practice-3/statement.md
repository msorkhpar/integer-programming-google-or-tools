A security company rosters guards over a few nights. Each night every guard is at exactly one
**place**: a site, or home (off duty). Places are numbered `0, 1, ..., n - 1`, and the last one,
`n - 1`, is home. `need[d]` maps a site to the number of guards it needs on night `d`; a site
missing from `need[d]` needs none that night, and home takes any number. Moving a guard from place
`p` on one night to place `q` the next costs `cost[p][q]` (and `cost[p][p] = 0`), and some moves are
not allowed at all: a guard coming off a night at the port cannot be at the airport the next
night, for example.

Write `plan_nights(guards, need, cost, forbidden)` in `guards.py`. `forbidden` lists the
not-allowed `(p, q)` moves. Return `(total, at)`, where `at[(guard, d)]` is the guard's place on
night `d`, chosen so that the total cost of all moves is as small as possible. Every instance in the
tests has a plan.

The model, with $`G`$ the guards, nights $`d = 0, \dots, N - 1`$, places $`0, \dots, n-1`$, demand
$`m_{d,p}`$ for each site $`p < n - 1`$, the cost table $`T`$ flattened row by row
($`\tau_{n p + q} = T_{p,q}`$) and the forbidden moves $`F`$:

```math
\begin{aligned}
& y_{g,d,p} \in \{0, 1\},\quad a_{g,d} \in \{0, \dots, n - 1\},\quad v_{g,d} \in \{0, \dots, \max \tau\} \\
& \min \; \textstyle\sum_{g} \sum_{d < N - 1} v_{g,d} \\
& \textstyle\sum_p y_{g,d,p} = 1, \quad a_{g,d} = \textstyle\sum_p p\, y_{g,d,p} && \forall g, d && \text{(one place)} \\
& \textstyle\sum_g y_{g,d,p} = m_{d,p} && \forall d,\ p < n - 1 && \text{(need)} \\
& (a_{g,d}, a_{g,d+1}) \notin F && \forall g,\ d < N - 1 && \text{(forbidden)} \\
& v_{g,d} = \tau[\, n\, a_{g,d} + a_{g,d+1} \,] && \forall g,\ d < N - 1 && \text{(move cost)}
\end{aligned}
```

The (move cost) rows are element constraints, the (forbidden) rows forbidden-assignment
constraints. Read the flattening carefully: which index is the row? The tests check the roster you
return and its total, so any optimal roster passes. Some tests pass an empty `forbidden` list,
which forbids nothing; the reference adds the forbidden-assignment rows only when the list is not
empty, and you may do the same. Return the total as an `int`, with
`round(solver.objective_value)`. About twenty-five lines.
