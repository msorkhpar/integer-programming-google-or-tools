The capstone's practice utility (a fictional one) has a finance team that forecasts benefits
differently from GridCap. Instead of one benefit in the start year, each project earns a **stream**:
one amount per year of service, starting in the year **after its last year of work**, and every
amount is smaller by a factor $`(1 - \delta_i)`$ for each year the project starts later than its own
earliest start. Your milestone-3 job is the coefficient table the model will use: the NPV of every
project for every start year in its window.

For project $`i`$ with cost profile $`c_{i,0}, \dots, c_{i,d_i-1}`$ ($k, $`d_i`$ years of work),
earliest start $`e_i`$, benefit stream $`b_{i,0}, b_{i,1}, \dots`$ and decay $`\delta_i`$, started in
year $`t`$, with the plan's first year $`y_0`$ and rate $`r`$:

```math
\text{npv}_{i,t} = -\sum_{k=0}^{d_i-1} \frac{c_{i,k}}{(1+r)^{\,t+k-y_0}}
  + \sum_{k \ge 0} \frac{b_{i,k}\,(1-\delta_i)^{\,t-e_i}}{(1+r)^{\,t+d_i+k-y_0}}
```

Write, in `npv.py`:

- `npv(project, forecast, start, years, rate)`: the formula above, as a float. `years` is the
  snapshot's list of plan years; `years[0]` is $`y_0`$. `discount` is given.
- `npv_table(snapshot, forecast)`: `{(project id, t): whole $k}` for every $`t`$ from `earliest` to
  `latest`, each value rounded to the nearest whole $k (`math.floor(v + 0.5)`).

The ideas come from lesson 7.2.4 (shift the cash flow to the start, discount every start to one
date, count benefits to the end of the asset's life and not to the end of the plan) and lesson 7.2.1
(present value). The tests use their own small portfolio; `snapshot["projects"][i]` has `cost`,
`earliest` and `latest`, and `forecast[i]` has `benefits` (a list) and `decay`.
