A hospital laboratory (not GridCap) is choosing which new analyzers to buy this year. Each analyzer
$`a`$ adds $`v_a`$ tests per day, costs $`p_a`$ ($k), takes $`s_a`$ m² of floor and draws $`\ell_a`$ kW.
Three resources limit the choice:

- **Money.** The capital budget is `budget` ($k).
- **Floor.** The lab owns `floor` m² of free floor. It may also lease space in the adjoining unit,
  any amount from 0 up to `max_lease` m², at `lease_rate` $k per m². Leased space is paid from the
  same capital budget, and it is priced by the square metre, fractions included.
- **Power.** The lab's electrical supply can carry `power` kW of new load. No lease helps here.

The model in `lab.py` has a binary `x[aid]` per analyzer (1 if it is bought) and maximizes tests per
day. Write `add_lab_rules(model, x, analyzers, budget, floor, power, lease_rate, max_lease)` so that
the model allows exactly the purchases the three resources allow. Add whatever variables you need.

With $`A`$ the candidate analyzers, the model so far is only

```math
x_a \in \{0, 1\} \quad \forall a \in A \qquad \text{(buy analyzer } a\text{)}
```

Write the rest of the formulation first: each new variable with its domain and bounds, then one
labelled row per resource. Then code it.

The tests fix which analyzers are bought and ask the solver whether some lease makes the purchase
fit, so any correct formulation passes. About five lines.
