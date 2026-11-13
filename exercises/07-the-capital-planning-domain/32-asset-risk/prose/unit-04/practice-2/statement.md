A gas utility's planners fix the end-of-horizon effect differently from lesson 7.3.4. Instead of
one window from the plan's first year, they credit every start with the same **service period**:
the risk removed in the `service_years` years that follow the end of its work, whenever that is.
Each year's reduction is discounted at `rate` back to the plan's first year `first_year`.

`yearly_cut(main, years, start, duration, keep)` is written for you: the lesson's yearly risk
reduction, for any list of calendar years that begins at `first_year`. Write
`coefficients(main, starts, first_year, duration, keep, service_years, rate)` in `coefficients.py`:
a dict from each start year in `starts` to its coefficient, $k.

In the lesson's notation, write $`\text{rr}_{s}`$ as a sum: over which years $`y`$, of what
$`\delta_{s,y}`$, divided by what. Remember that the reduction is 0 while the work goes on, so you
may include those years or not. The tests compute the yearly reductions with
`scipy.stats.weibull_min.logsf`. About six lines.
