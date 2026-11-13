A transit agency's fleet-renewal MILP chooses which depots to rebuild, and maximizes the value of
the plan. The board wants to know about one depot in particular: must it be in the plan? The analyst
runs the model twice, once with that depot's variable fixed to 1 (forced in) and once fixed to 0
(forced out). Each run returns its incumbent and its best bound, or nothing at all when the run
proved that no plan exists with the depot fixed that way.

Write `fund_or_skip(forced_in, forced_out)` in `fund_or_skip.py`. Each argument is a pair
`(incumbent, bound)` for a maximization, or `None` for a run that proved no plan exists. Return:

- `"fund"` when every plan without the depot is worse than a plan with it: the forced-in incumbent
  is strictly greater than the forced-out bound, or the forced-out run has no plan.
- `"skip"` when every plan with the depot is worse than a plan without it: the forced-out incumbent
  is strictly greater than the forced-in bound, or the forced-in run has no plan.
- `"undecided"` otherwise: the two brackets overlap or touch, and only tighter runs can tell.

The two runs never both return `None`.
