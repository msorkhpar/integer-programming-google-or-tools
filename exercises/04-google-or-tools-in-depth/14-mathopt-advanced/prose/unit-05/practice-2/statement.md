A crew-scheduling service lets each customer choose how close to optimal a schedule must be before
the solve stops. Write `stop_at(target)`, which returns a callback for `Event.MIP_SOLUTION` that asks
the solver to stop once the relative gap is at most `target`:

```math
\text{gap} = \frac{|\,\text{dual bound} - \text{primal bound}\,|}{|\,\text{primal bound}\,|}
```

Both bounds are in the callback data's `mip_stats` (`primal_bound`, the incumbent's value, and
`dual_bound`, the best bound). The callback returns `mathopt.CallbackResult(terminate=True)` to
stop, and `terminate=False` to go on. In a maximization the bound is above the incumbent; in a
minimization it is below, which is why the formula takes absolute values. The tests build
`CallbackData` by hand, with bounds you can read in each test. About five lines.

The formula has no value when the primal bound is 0 (a division by zero) or $`\pm\infty`$ (no
plan's value to measure against). In those cases return `terminate=False` and let the solve go on:
the reference does exactly that, testing `stats.primal_bound == 0` and `math.isfinite`. The tests
do not try those cases. (The lesson's `good_enough` does the same in its own way: for a maximization with
positive values it treats a primal bound that is not above 0 as a gap of 100%.)
