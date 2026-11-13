A regulator requires a power utility to spend at least a floor $`F_y`$ on vegetation work in each
year $`y`$. The utility's plan maximizes value, and the floor rows are the rows that tie its
projects together:

```math
\max \; \sum_i \sum_t v_{i,t}\, x_{i,t} \qquad \text{subject to} \qquad
\text{veg}_y(x) \ge F_y \quad \forall y \quad \text{(floor}_y), \qquad \text{and rows on single projects}
```

To bound the best plan, the planners relax the floor rows with prices $`\mu_y \ge 0`$. Note the
direction: these rows are $`\ge`$, not $`\le`$ like the budget rows of the lesson.

Write it first: $`L(\mu)`$ with the floors priced so that every $`\mu \ge 0`$ gives an upper bound,
the subgradient of $`L`$ at $`\mu`$ in terms of the relaxed plan's vegetation spend, and the
projected update with Polyak's step
$`s = \theta\,(L(\mu) - \underline{z}) / \lVert g \rVert^2`$, where $`\underline{z}`$ is the best
plan's value so far.

Then write `next_prices(prices, floors, veg_spend, bound, best_value, theta)` to return the next
prices as a new dict by year. `veg_spend` is the relaxed plan's vegetation spend by year, `bound`
is $`L(\mu)`$ at `prices`. If the subgradient is zero, the relaxed plan meets every floor exactly
and the prices are returned unchanged.

About six lines.
