A hospital network buys major equipment through a yearly capital plan that its optimizer proposes.
Its internal auditor does not want to trust the optimizer's model to say the plan is valid: if a
rule had been coded wrongly, the model would agree with its own mistake. The auditor wants a check
written from the purchase data alone.

`items` maps each purchase to its data: `"years"`, the years it may be bought in; `"cost"`, $k, all
spent in the year it is bought; and `"mandatory"`. `budget` maps each year to its limit, and `groups`
maps each exclusive group (at most one of its members may be bought, ever) to its members. A plan maps
each purchase it makes to its year.

In `hospital_audit.py`, write `audit_failures(plan, items, budget, groups)`, returning a sorted list
with one entry per failure: `"window <item>"`, `"mandatory <item>"`, `"exclusive <group>"` or
`"budget <year>"`. An empty list means the plan keeps every rule.

Write the four rules first, as conditions on the plan, with $`y_i`$ the year purchase $`i`$ is bought
in, $`W_i`$ its allowed years, $`c_i`$ its cost, $`B_t`$ the budget of year $`t`$ and $`S`$ the
purchases the plan makes: one condition for windows, one for mandatory purchases, one per group and
one per year. Then code each as a check. The tests use their own hospital; no solver is involved.
