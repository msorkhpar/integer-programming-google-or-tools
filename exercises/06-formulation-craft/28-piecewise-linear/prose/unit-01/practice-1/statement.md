A water utility plans next month's work for its contracted main-repair crew. Each job in `jobs`
needs a known number of crew hours. The contract prices the crew's hours in tiers, given in `tiers`
as `(hours up to, $ per hour)`, in order:

| Hours in the month | Rate |
| --- | --- |
| up to 160 | $60 per hour |
| from 160 up to 200 | $90 per hour |
| from 200 up to 240 | $120 per hour |

So a month of 170 hours costs 160 × 60 + 10 × 90. The contract allows no more hours than the last
tier's limit. The month's labor cost must not exceed `budget` dollars.

The model in `crew_month.py` has a binary `x[jid]` per job (1 if the job is done this month).
Write `add_labor_rules(model, x, jobs, tiers, budget)` so that the model allows exactly the months
(which jobs) whose real labor cost fits the budget and whose hours stay within the contract. Add
whatever variables you need. Work from `tiers`, not from the numbers in the table: the tests use
other tiers too.

With $`J`$ the jobs and $`h_j`$ the hours of job $`j`$, the model so far is

```math
\begin{aligned}
& x_j \in \{0, 1\} && \forall j \in J && \text{(do job } j \text{ this month)} \\
& \text{?} && && \text{(your variables and rows)}
\end{aligned}
```

Write the month's hours as an expression first. Then write its labor cost as a function of the
hours: what shape is it, and does the budget row press that cost up or down? That decides whether
you need anything more than continuous variables.

The tests fix which jobs are done and ask the solver whether the model accepts the month, so any
correct formulation passes. About eight lines.
