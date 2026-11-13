A city's public works department schedules water-main replacements and street resurfacing for
2027 to 2033. The model in `streets.py` has a binary `x[pid, t]` for each project and each year `t`
in its `starts`; each project starts at most once (given). A water main takes `duration` years of
work: one started in 2028 with a duration of 2 is dug up through 2029.

`after` maps a resurfacing project to a pair `(main, settle)`. The rule: a street may be resurfaced
only after the water main under it is finished, and only once the trench has settled for `settle`
full years. With the main above and `settle = 1`, 2030 is the settling year, and the street may be
resurfaced in 2031 or later. A resurfacing project whose main is not funded may not be done at all.
A resurfacing project that is not in `after` has no such rule.

Write `add_after_rules(model, x, projects, after)` so that the model allows exactly the plans that
keep the rule.

The model so far, with $`P`$ the projects, $`T_i`$ project $`i`$'s start years and $`d_i`$ its
duration:

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(project } i \text{ starts in year } t\text{)} \\
& \textstyle\sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P && \text{(once}_i\text{, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

First turn the rule into a least number of years between the two *starts*, and check it on the
example above. Then write one row per resurfacing project and year, with its quantifier and a
label, before you code it.

The tests fix every `x[pid, t]` through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About eight lines.
