A water utility plans to swap an old pump for a unit of a newer design. The old pump has age
`age` in the plan's first year and a Weibull curve (`beta`, `eta`); the new design has its own
curve (`beta_new`, `eta_new`). The work starts in `start` and lasts `duration` years; the old pump
runs until the work ends, and the new unit is in service, at age 0, from the year after. Failed
pumps are repaired and kept, so a year's risk is `cof` times the expected failures in that year.

Write `yearly_cut(pump, years, start, duration)` in `refurb.py`: a dict from each year in `years`
(the first is the plan's first year) to the risk removed that year, $k.

In the lesson's notation, write $`\delta_y`$ as the risk of the old pump at its age $`a^0_y`$ minus
the risk with the work, which now comes from a different curve. `failures(age, beta, eta)` is
written for you. The tests compute expected failures from `scipy.stats.weibull_min.logsf`. About
ten lines.
