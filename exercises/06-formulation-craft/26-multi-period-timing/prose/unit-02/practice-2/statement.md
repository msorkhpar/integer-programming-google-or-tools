A water utility relines its old mains with one contractor, who has asked for a steady workload: the
crews and the lining plant cost money to stand up and stand down. The contract says that from one
year of the plan to the next, the utility's total relining spend may rise or fall by at most
`max_step`. The model in `steady.py` already has the start variables, a row saying each project
starts at most once, and `yearly_spend`, which builds each year's spend as an expression.

Write `add_steady_spend(model, spend, years, max_step)`, adding the rows that keep this rule.
`spend[y]` is year `y`'s expression and `years` are the plan's years in order. Spend before the
first year or after the last is not part of the rule.

The model so far, with $`P`$ the projects, $`T_i`$ the years project $`i`$ may start in, $`Y`$ the
plan's years, $`c_{i,k}`$ what project $`i`$ spends in its $`k`$-th year of work and $`S`$ the step:

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(start } i \text{ in year } t\text{)} \\
& \sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P && \text{(once}_i\text{, given)} \\
& \text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\ t \le y} c_{i,\,y-t}\, x_{i,t} && \forall y \in Y && \text{(an expression, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Write your rows in this notation first, each with its quantifier and a label, then code them. A
solver row is linear: it cannot take an absolute value, so think about what "rise or fall by at most
$`S`$" says as plain inequalities.

The tests fix a schedule by setting the variables' bounds and ask the solver whether it is allowed,
so any correct formulation passes. About four lines.
