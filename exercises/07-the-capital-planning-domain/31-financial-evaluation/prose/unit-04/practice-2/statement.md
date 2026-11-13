A water utility (invented for this practice) relines old cast-iron mains. A relining job spends
`costs[k]` in its `k`-th year of work (`k = 0` is the start year). From the year after the work
ends, it avoids `annual_benefit` of break repairs every year, for `life` years. Every amount is
quoted in the prices of `valuation_year`, prices rise by `escalation` a year, and the utility's
nominal discount rate is `rate`. Amounts are paid at the start of their year. The planning model
needs one entry per allowed start year, all valued on the start of `valuation_year`.

Write `npv_by_start_year(costs, annual_benefit, life, starts, valuation_year, rate, escalation)`,
returning `{start year: NPV}`. The tests check each entry against numpy-financial's `npv` on the
job's year-by-year cash flow, so the conventions above matter.

Write the entry for a start $`t`$ as one formula first: the calendar year of each cost and each
benefit, its escalation exponent, and its discount exponent. About twelve lines.
