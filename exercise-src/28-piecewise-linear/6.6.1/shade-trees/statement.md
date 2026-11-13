A city's forestry office has `stock` young trees to plant along its streets this autumn. For each
street, the arborist has measured how much summer shade benefit (in points of the city's heat index)
the street gains from a number of trees, as breakpoints `xs` (trees) and `ys` (benefit), with
straight lines in between. The first trees on a bare street matter most:

| Trees on Elm St | 0 | 10 | 25 | 40 |
| --- | --- | --- | --- | --- |
| Benefit | 0 | 30 | 51 | 57 |

A street cannot take more trees than its last breakpoint (the curb runs out). Trees may be split
across streets in any amounts, fractions included (the plan is rounded later).

The model in `street_trees.py` has a continuous variable `trees[name] >= 0` per street, with no
upper bound, and a row keeping the total within `stock`. Write
`add_benefit(model, trees, xs, ys)`: add the variables and rows you need for one street and return
an expression equal to the street's benefit at the plan's number of trees. The model maximizes the
sum of these expressions.

With $`S`$ the streets and $`(X_{s,k}, F_{s,k})`$ street $`s`$'s breakpoints, the model so far is

```math
\begin{aligned}
\max \;& \sum_{s \in S} \text{?}_s && && \text{(benefit of street } s\text{)} \\
& \sum_{s \in S} t_s \le \text{stock} && && \text{(stock)} \\
& t_s \ge 0 && \forall s \in S && \text{(trees on street } s\text{)}
\end{aligned}
```

Look at the slopes of a benefit curve and at which way the objective pushes the benefit before you
choose the rows. The tests use other curves of the same kind.

The tests ask for the best planting, and fix one street's trees to read its benefit, so any correct
formulation passes. About six lines.
