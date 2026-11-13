A water utility's board approves a new rule for its capital fund. A year may spend some of the
next year's budget early, up to a share `max_advance` of that next year's budget, and whatever it
spends early is no longer there to spend in the year it came from. A year may do both in one plan:
lose part of its budget to the year before and spend early from the year after. The plan's last
year has no next year to draw on. Money a year neither spends nor sends anywhere still lapses at year end. The
model in `advance.py` still holds every year to its own budget, so it never uses the new rule.

The model so far, with $`Y`$ the plan's years in order, $`\text{spend}_y`$ the given linear
expressions in the plan's 0/1 variables, and $`B_y`$ the budgets:

```math
\text{spend}_y \le B_y \qquad \forall y \in Y \qquad \text{(budget}_y)
```

Your formulation replaces those rows. Write it first in this notation: each new variable with its
domain and bounds, and each row with its quantifier and label. Then write
`add_advances(model, spend, budgets, max_advance)` to add it, and return your new variables in a
dict keyed by the year that spends early (the last year, which cannot borrow, has no entry). `add_yearly_budgets` shows the old rows; your function replaces them (the tests call
yours alone).

The tests fix a plan and ask the solver whether it is allowed, so any correct formulation passes.
About eight lines in total.
