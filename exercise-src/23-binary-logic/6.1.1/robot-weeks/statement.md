A water utility is choosing which trunk mains to inspect this season with a pipe-crawling robot. It
rents the robot from a specialist firm, and the rental terms decide which inspection plans are
affordable:

- The robot is rented in **whole weeks** at `weekly_rate` ($k) per week, and in one week it can
  inspect up to `km_per_week` kilometres of pipe, in any mix of pipes.
- The firm can lend the robot for at most `max_weeks` weeks this season.
- The season's **budget** must cover the inspections' own costs (crews, traffic control, access
  pits) *and* the rental.

The model in `inspection.py` has a binary `x[pid]` for each candidate main (1 if it is inspected).
Write `add_inspection_rules(model, x, pipes, km_per_week, weekly_rate, max_weeks, budget)` so that
the model allows exactly the plans the rental terms make affordable. Add whatever variables you
need; the starter has no budget row, so the budget is yours to write.

With $`P`$ the candidate mains, $`\ell_p`$ the length of main $`p`$ (km) and $`c_p`$ its inspection
cost ($k), the model so far is only

```math
x_p \in \{0, 1\} \quad \forall p \in P \qquad \text{(inspect main } p\text{)}
```

Write the rest of the formulation first: each new variable with its domain and bounds, then each
row with a label. Then code it.

The tests fix which mains are inspected and ask the solver whether some rental makes the plan
affordable, so any correct formulation passes. About five lines.
