A water utility has a pump-failure model for each of its stations and a list of projects: replace
a station's pump, or repair it for less. The board wants the plan that removes the most failure
cost per year, within the budget and the rules. The rules are already written in `allowed`: stay
within the budget, fund every must-do project, and fund at most one project per station.

Write two functions in `pumps.py`. `pof_next(age, beta, eta)` (next year's probability of failure
for a pump working today) is written for you.

**First,** `risk_avoided(project, assets)`, the coefficient $`a_i`$ of project $`i`$ on station $`k`$:

```math
a_i = \text{CoF}_k \Big( \text{PoF}_{\text{next}}(\text{age}_k) - \text{PoF}_{\text{next}}(\rho_i\, \text{age}_k) \Big)
```

where $`\rho_i`$ is `AGE_AFTER[project.work]`: 0 for a replacement, 0.5 for a repair.

**Second,** `most_risk_removed(projects, assets, budget)`, which solves, by checking every plan:

```math
\max \; \sum_{i \in P} a_i\, x_i \quad \text{over plans } x \in \{0, 1\}^{|P|} \text{ that } \texttt{allowed} \text{ accepts}
```

It returns `(total, plan)`, with `plan` a frozenset of project ids.

About twelve lines in all.
