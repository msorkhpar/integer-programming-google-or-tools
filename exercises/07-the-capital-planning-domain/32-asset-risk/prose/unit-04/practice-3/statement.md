A regulator agrees a rate case with a utility on one condition: in every year of the plan, the
expected failure cost left in the network, after the plan's projects, must not exceed that year's
`cap[y]` ($k). The utility's model already chooses start years; it does not yet know about the
condition.

What the model has, in the lesson's notation: the plan's years $`Y`$; the start variables
$`x_{i,t} \in \{0, 1\}`$, given to you as `x[(i, t)]`; at most one start per project, already
written; the network's risk with no project at all in year $`y`$, `base[y]` ($k); and, for each
start variable, `cut[(i, t)][y]`: the risk project $`i`$ removes in year $`y`$ if it starts in
$`t`$ (0 in the years before it takes effect).

Write the formulation first, in that notation: each new row with its quantifier and its label.
Then write `add_risk_caps(model, x, base, cut, cap)` in `cap.py` to add it, and return your rows in
a dict keyed by year.

The tests fix a plan and ask the solver whether it is allowed, so any correct formulation passes.
About five lines.
