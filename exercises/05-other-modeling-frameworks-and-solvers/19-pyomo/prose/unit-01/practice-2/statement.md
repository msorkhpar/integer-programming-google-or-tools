A distribution company trims trees along its feeder lines in spring. Each line needs a number of
crew hours, removes some risk once it is trimmed, and may only be trimmed in certain months (a
nesting season or a road permit closes the others). The crews have a fixed number of hours in each
month. Some lines have no allowed month this year, and some months have no line allowed in them.

Write `trim_plan(circuits, crew_hours)` in `trim.py` with Pyomo. `circuits` maps a line's name to a
`Circuit(hours, risk, months)`; `crew_hours` maps each month to the crew hours it has. Return the
most risk the plan removes and a dict from each trimmed line to its month.

`crew_hours` lists every month the crews work. A line may name a month that `crew_hours` leaves
out: that month has no crew hours, so the line cannot be trimmed in it.

The formulation, with $`C`$ the lines, $`M`$ the months of `crew_hours` and
$`A = \{(c, k) : k \in M \text{ is an allowed month of } c\}`$:

```math
\begin{aligned}
\max \;& \sum_{(c,k) \in A} \text{risk}_c\, x_{c,k} \\
& \sum_{k : (c,k) \in A} x_{c,k} \le 1 && \forall c \in C && \text{(once}_c) \\
& \sum_{c : (c,k) \in A} \text{hours}_c\, x_{c,k} \le \text{cap}_k && \forall k \in M && \text{(crews}_k) \\
& x_{c,k} \in \{0, 1\} && \forall (c,k) \in A
\end{aligned}
```

Declare $`C`$, $`M`$ and $`A`$ as Pyomo Sets, the data as Params, $`x`$ over $`A`$ only, and each
family of rows as an indexed Constraint with a rule. Solve with `appsi_highs` and a zero
`mip_gap`. About twenty-five lines.
