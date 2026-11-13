A rural electric cooperative is scheduling its feeder upgrades year by year, and the model in
`outages.py` already has a start variable `x[(pid, year)]` for each project and each year in its
window, a row saying each project starts at most once, and a row saying each must-do project
starts exactly once. Two rules from the operations team are missing:

- **Crews.** Each year only a few line crews can be mobilized: at most `max_starts[year]` projects
  may start in that year, must-do projects included. A year in which no project may start has
  nothing to cap, so it gets no row. In Python an empty `sum` is the number 0, and MathOpt refuses
  a row built from it (a `TypeError` about a `bool`): skip the row, or start the sum from
  `mathopt.LinearExpression()`, as the lesson shows.
- **Coordinated outages.** Some pairs of upgrades sit on the same feeder and need one shared
  outage. For each pair in `coordinated`, either neither project is funded, or both are and they
  start in the same year.

Write `add_outage_rules(model, x, projects, max_starts, coordinated)` so the model allows exactly
the schedules that keep both rules.

The model so far, with $`P`$ the projects, $`T_i`$ the years project $`i`$ may start in, $`M
\subseteq P`$ the must-do projects, $`Y`$ the years with a crew cap $`K_y`$, and $`D`$ the
coordinated pairs:

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(start } i \text{ in year } t\text{)} \\
& \sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P \setminus M && \text{(once}_i\text{, given)} \\
& \sum_{t \in T_i} x_{i,t} = 1 && \forall i \in M && \text{(must}_i\text{, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Write your rows in this notation first, each with its quantifier and a label, then code them. Mind
the pairs whose windows do not line up: there is no variable for a year outside a project's window.

The tests fix a schedule by setting the variables' bounds and ask the solver whether it is allowed,
so any correct formulation passes. About ten lines in total.
