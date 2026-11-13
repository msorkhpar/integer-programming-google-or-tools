A port authority finances its capital plan through a bond program, and the bond covenant now limits
how fast it may spend: any `k` consecutive years of the plan together may spend at most `cap`. The
model in `rolling.py` holds only the whole plan to one cap, so a plan can still crowd its spending
into a few years.

The model so far, with $`Y = (y_1, \dots, y_n)`$ the plan's years in order and
$`\text{spend}_y`$ the given linear expressions in the plan's 0/1 variables:

```math
\sum_{y \in Y} \text{spend}_y \le C \qquad \text{(plan\_cap)}
```

Write the covenant first in this notation: which sets of years it caps (say exactly which first
years a window may have), and one row per such set, with its quantifier and a label. Then write
`add_rolling_caps(model, spend, years, k, cap)` to add those rows and return them in a dict keyed
by each window's first year. If the plan has fewer than `k` years, no window fits and there is no
row. `add_plan_cap` shows the old row; the tests call your function alone.

The tests fix a plan and ask the solver whether it is allowed, so any correct formulation passes.
About five lines.
