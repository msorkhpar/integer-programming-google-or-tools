A water utility's pump-replacement model reports its objective as "total network value": the value
of the replacements it chooses **plus** a fixed amount $`K`$ for the network that already exists. The
solver's relative gap divides by that total, so its reports look better than the decisions deserve.
The analytics team wants every report to carry the gap on the part the decisions control.

Write `true_gap(incumbent, bound, constant)` in `true_gap.py`. `incumbent` and `bound` are the two
numbers the solver reported, both including `constant`. Return a dict:

- `"absolute"`: $`|\text{bound} - \text{incumbent}|`$. The constant cancels out of this difference.
- `"seen"`: the absolute gap divided by $`|\text{incumbent}|`$, which is what the solver saw.
- `"on_decisions"`: the absolute gap divided by $`|\text{incumbent} - \text{constant}|`$, the value
  of the decisions alone.

The model may be a maximization or a minimization, and the constant may be negative (a sunk cost
taken off every plan). Both ratios are `0.0` when the absolute gap is 0, and `math.inf` when their
denominator is 0 and the absolute gap is not.
