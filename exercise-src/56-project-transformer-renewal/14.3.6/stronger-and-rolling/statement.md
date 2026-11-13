The 5,000-unit plan came back "within 2%", and the analysts sent the sixth request:

> **Request 6.** Your plan is "within 2%" of the best. On 5,000 units that is about $100,000k of
> risk, more than the differences between the scenarios we want to compare next. We need plans
> within 0.1% of the bound, and the analysts need each one within fifteen minutes.

You start from the model built for scale. Its outage row per substation and year lets the LP
relaxation buy a fraction of an outage. Add the per-unit form, a row per unit and year allowing its
replacement only with its substation's outage, choose between the two with the request's `link`
(per-unit by default), and give the LP relaxation's optimum, the bound the forms are compared by.
Then write a checker that tests every rule of a finished plan in plain Python, apart from the model,
and a rolling horizon that solves a few years at a time and keeps the first of them.

Run executes `main.py`, which takes a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56, and the last step's request, whose `link` is left at its
default, per-unit:

```python
Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
        crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})
```

It prints the LP bound under both outage forms (the request with `link="aggregated"`, then the
request itself), plans the five years, checks the plan with `violations`, and plans it again with
`rolling(fleet, REQUEST, window=2, keep=1)`:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k a year
LP bound: aggregated outage rows $<aggregated>k, per-unit rows $<per_unit>k
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, <outages> outages, $<spend>k
rules broken: <count>
rolling, window 2 keep 1: <n> units, risk removed $<value>k, rules broken <count>
```

The per-year lines are the last step's. `<count>` is the number of lines `violations` returns for
that plan, and money has a comma between thousands and no decimals. `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.
