A transmission company builds substations and must test each new station's protection relays. The
model in `testing.py` has a binary `x[pid, t]` for each project and each year `t` in its `starts`;
the plan's years are `years`, and each project starts at most once (given). `testing` maps each
testing project to a pair `(station, k)`, and the regulator's rule is:

- Testing may not start before its station starts (the same year is fine).
- Testing has a deadline: if the station starts in year `s`, its testing must have started by year
  `s + k`. This holds whether or not the planners like it: building the station commits the
  testing.
- The plan only covers `years`. If a station's deadline `s + k` falls after the plan's last year,
  its testing is not required inside this plan (the next plan will take it up), though it may still
  be done.

Write `add_testing_rules(model, x, projects, years, testing)` so that the model allows exactly the
plans that keep the rules.

The model so far, with $`P`$ the projects, $`Y`$ the plan's years and $`T_i`$ project $`i`$'s
start years:

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(project } i \text{ starts in year } t\text{)} \\
& \textstyle\sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P && \text{(once}_i\text{, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Write your rows in "started by year $`t`$" terms, each with its quantifier and a label, before you
code them. Decide which years $`t`$ each kind of row needs, and check the third rule against the
years you chose.

A sum over no variables is the plain number 0 in Python, and MathOpt refuses a row with no variable
on either side (a `TypeError` about a `bool`). Such a row says nothing, so either skip it or wrap
each sum in `mathopt.LinearExpression(...)`, which MathOpt accepts even when it is empty.

The tests fix every `x[pid, t]` through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About ten lines.
