A fiber builder plans its network for 2027 to 2029 under agreements with the counties it builds in.
The model in `counties.py` has a binary `x[pid, t]` for each project and each year `t` in its
`starts`; each project starts at most once (given). A project's `cost` is a tuple: what it spends in
its first year of work, its second, and so on, so a project with cost `(300, 200)` started in 2027
spends 300 in 2027 and 200 in 2028. All work ends by 2029. The agreements, in $k:

- **Minimum.** Each county in `floor` receives at least `floor[c]` over the whole plan.
- **Cap over the plan.** Each county in `cap` receives at most `cap[c]` over the whole plan.
- **Cap in a year.** For each `(c, y)` in `yearly_cap`, county `c` receives at most
  `yearly_cap[c, y]` in year `y`.

Write `add_county_rules(model, x, projects, years, floor, cap, yearly_cap)` so that the model allows
exactly the plans that keep the three agreements.

The model so far, with $`P`$ the projects, $`T_i`$ project $`i`$'s start years and $`c_{i,k}`$ what
it spends in its $`k`$-th year of work ($`k = 0, 1, \dots`$):

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(project } i \text{ starts in year } t\text{)} \\
& \textstyle\sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P && \text{(once}_i\text{, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the counties and the projects of each, and write two expressions first: a county's spend in
one year, and its spend over the plan. Then write each row with its quantifier and a label, and
only then code them.

A county may have no project that spends in some year. Its spend there is a sum over no terms, the
number 0 in Python, and MathOpt refuses a row with no variable on either side. Skip such a row, or
start the sum from `mathopt.LinearExpression()` (lesson 6.4.1).

The tests fix every `x[pid, t]` through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About twelve lines.
