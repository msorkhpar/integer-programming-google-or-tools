The practice utility's asset-health team sends one predicted **remaining useful life** (RUL) per
asset, together with a fleet shape $`\beta`$, the asset's age $`a`$ and its consequence of failure
$`\text{cof}`$ ($k). The maker's catalog also lists a scale `eta`, fitted to new assets. Milestone 3
needs the second coefficient table: the risk each project removes, for each start year.

**The curve.** Use the scale that makes the RUL the median remaining life at today's age
(lesson 7.3.2), not the catalog's:

```math
\eta = \left(\frac{(a + \text{RUL})^{\beta} - a^{\beta}}{\ln 2}\right)^{1/\beta}
```

**One year's risk.** With failures repaired as they come, the expected failures between ages $`u`$
and $`u+1`$ are $`(\tfrac{u+1}{\eta})^{\beta} - (\tfrac{u}{\eta})^{\beta}`$, and the year's risk is
$`\text{cof}`$ times that (lesson 7.3.3).

**Risk removed.** Work of $`d`$ years started in $`t`$ ends in $`t+d`$. Without it, the asset's age in
year $`y`$ is $`a + (y - y_0)`$. With it, the age is the same until $`t+d`$; from then on it is
`keep` times the age reached at $`t+d`$, plus $`y - (t+d)`$. The coefficient sums, over a fixed
window of $`W`$ years from the plan's first year $`y_0`$ (even past the plan's last year), the
yearly risk without the work less the yearly risk with it, discounted to $`y_0`$ at the snapshot's
rate (lesson 7.3.4).

Write, in `risk.py`, `scale_from_rul(age, rul, beta)`, `risk_removed(asset, start, duration, years,
window, rate)` (`years` is the plan's list of years, `years[0]` is $`y_0`$) and
`risk_table(snapshot, assets, window)`, which returns `{(project id, t): risk removed}` for every start
in each window, rounded to 3 decimals. `expected_failures` and `age_in` are given; `age_in` with
`start=None` is the age without the work. A project's duration is the length of its `cost` list.
