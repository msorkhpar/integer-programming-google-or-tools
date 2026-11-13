A hospital courier runs two cars. Each blood sample is collected at a clinic and must reach its lab
in the same car, since nobody hands samples between cars, and the car must of course collect it
before it delivers it. `handoff.py` builds the routes with a "Distance" dimension, whose cumul is
the distance a car has driven on arrival. Write `add_handoffs(routing, manager, distance_dim,
pairs)`, with `pairs` a list of `(clinic, lab)` nodes.

In the lesson's notation, for every pair $`(p, d)`$ with indices $`\text{index}(p)`$ and
$`\text{index}(d)`$:

```math
\begin{aligned}
& \text{vehicle}_{\text{index}(p)} = \text{vehicle}_{\text{index}(d)} && \text{(same car)} \\
& \text{dist}_{\text{index}(p)} \le \text{dist}_{\text{index}(d)} && \text{(collect first)}
\end{aligned}
```

and the pair is declared to the search so its moves keep the two stops together. Before you code,
say why comparing the Distance cumuls means "earlier on the route", and which of the three calls
the lesson found a plan could not do without.

The tests ask the model whether hand-built plans are allowed, so any correct formulation passes.
About five lines.
