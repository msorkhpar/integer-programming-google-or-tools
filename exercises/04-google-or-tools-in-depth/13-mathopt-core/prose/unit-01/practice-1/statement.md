A water utility's storm desk stations repair crews at its depots before a storm. Each depot can be
opened or left closed; an open depot hosts up to its capacity in crews, each crew costs a day rate,
and opening a depot has a fixed cost. Across all depots, the desk wants at least `low` and at most
`high` crews on standby.

The model, with $`D`$ the depots:

**Parameters.** $`\text{cap}_d`$, the most crews depot $`d`$ can host; $`\text{rate}_d`$, the cost of
one crew at $`d`$ ($k); $`\text{fixed}_d`$, the cost of opening $`d`$ ($k); $`L`$ and $`U`$, the
lowest and highest total number of crews.

**Variables.** $`\text{open}_d \in \{0, 1\}`$ and $`\text{crews}_d \in \{0, 1, \dots,
\text{cap}_d\}`$ for every $`d \in D`$.

**Objective and constraints.**

```math
\begin{aligned}
\min \;& \sum_{d \in D} \left(\text{rate}_d\, \text{crews}_d + \text{fixed}_d\, \text{open}_d\right) \\
\text{s.t. }& \text{crews}_d \le \text{cap}_d\, \text{open}_d && \forall d \in D && \text{(link}_d) \\
& L \le \sum_{d \in D} \text{crews}_d \le U && && \text{(total)}
\end{aligned}
```

Write `build(depots, low, high)` in `crews.py`. It already creates one `open` and one `crews` variable
per depot, but with MathOpt's default bounds; give each its domain, then add the rows and the
objective. Return the model and the two dicts of variables, keyed by depot name.

The tests fix a plan by setting each variable's bounds to its value and ask HiGHS whether the model
accepts it, so any correct formulation passes. The `total` row can be one ranged row; both bounds
belong to it.
