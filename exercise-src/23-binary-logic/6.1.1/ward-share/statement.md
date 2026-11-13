A city's public-works department is choosing which streetlight blocks to retrofit with LED fixtures
this year. The model in `retrofits.py` already has a binary `x[rid]` per candidate retrofit (1 if
it is funded) and a budget row. Two rules from the operations office are missing:

- **Yards.** The crews of each ward work out of one yard, and a yard can stage at most
  `yard_cap[ward]` retrofits. A ward that does not appear in `yard_cap` has no yard limit.
- **Fair share.** No ward may receive more than `max_share` (a fraction such as 0.4) of the
  retrofits the plan funds.

Write `add_ward_rules(model, x, retrofits, yard_cap, max_share)` so that the model allows exactly
the plans that keep both rules.

The model so far, with $`R`$ the candidate retrofits, $`c_r`$ the cost of retrofit $`r`$ and $`B`$
the budget:

```math
\begin{aligned}
& x_r \in \{0, 1\} && \forall r \in R && \text{(fund retrofit } r\text{)} \\
& \sum_{r \in R} c_r\, x_r \le B && && \text{(budget, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the sets and parameters you need (the wards, the retrofits of each ward, the caps, the share),
write your rows in this notation first, each with its quantifier and a label, then code them. A
share of a count is not linear as a fraction; find the form that is.

The tests fix a plan through the variables' bounds and ask the solver whether the model accepts it,
so any correct formulation passes. About six lines.
