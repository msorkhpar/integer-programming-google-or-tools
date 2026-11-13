The one-year list went to finance, and the second request came back:

> **Request 2.** Finance has set the transformer budget at $10,000k a year for 2027 to 2036. Give us
> a ten-year plan: which units to replace, and in which year. A unit we wait on keeps aging, so the
> plan should count the risk each year of waiting leaves in place. The asset team says units under
> 40 years old are not worth looking at this decade.

You start from the one-year model. A plan that waits needs a unit's probability of failure at every
age, so compute it from its kind's Weibull curve, and value a replacement in a given year by the risk
it removes over the request's risk window, discounted to 2027. Then let each candidate (a unit at
least the request's minimum age) be replaced in at most one year of the plan, and keep each year's
spend within that year's budget. The request's `gap` becomes the solver's relative gap, and a plan
maps each replaced unit to its year.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56. Its request sets every field the plan reads:

```python
Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02)
```

that is $2,000k a year for the five years 2027 to 2031, risk counted over the ten years 2027 to
2036, units 40 years and older as candidates, the default discount rate of 7%, and a relative gap
of 2%. It prints each year's units and spend, using `report.spend_by_year` for the spend:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k a year
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, $<spend>k
```

with one indented line per year that has replacements, in year order, two spaces before the year;
`<value>` is the `Plan`'s value with no decimals, money has a comma between thousands, and "units"
stays plural for one unit. `expected/report.txt` is the report it should print. Submit runs every
test in `tests/`, the earlier steps' included, and compares Run's report with the expected one.
