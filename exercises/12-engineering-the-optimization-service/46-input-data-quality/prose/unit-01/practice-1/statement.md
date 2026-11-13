A city transit agency plans which buses to replace in which year, and its planning tool sends the
optimization service a snapshot as JSON. The service's model is small:

**Sets.** $`H`$ the horizon's years; $`D`$ the depots; $`V`$ the buses, each kept at a depot
$`d(b) \in D`$; $`T_b = \{e_b, \dots, l_b\}`$ the years bus $`b`$ may be replaced in.

**Parameters.** $`c_b`$, the cost of replacing bus $`b`$ ($k); $`A_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{b,y} \in \{0, 1\}`$ for $`b \in V`$, $`y \in T_b`$: bus $`b`$ is replaced in year $`y`$.

**Constraints.**

```math
\begin{aligned}
\sum_{y \in T_b} x_{b,y} &= 1 && \forall b \in V && \text{(replace}_b) \\
\sum_{b \in V:\, y \in T_b} c_b\, x_{b,y} &\le A_y && \forall y \in H && \text{(budget}_y)
\end{aligned}
```

In `fleet.py`, finish the schema so that a snapshot is accepted exactly when this model can be built
from it and its parameters make sense: one variable family per bus (no bus listed twice), every bus
at a listed depot, one budget row for every year of the horizon (not zero, not two), a window that
holds at least one year, a cost above zero, and a budget of zero or more. Rules across records go in
`FleetSnapshot.references_resolve`; when several fail, one `ValueError` must name every bus and year
involved. The tests validate JSON text with `FleetSnapshot.model_validate_json` and look for the
ids and years in the error's messages. About fifteen lines.
