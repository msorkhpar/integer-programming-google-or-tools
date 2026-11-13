The ten-year plan reached the system operator, who sent the third request:

> **Request 3.** A transformer can only be swapped with its substation out of service. Each outage
> costs about $300k (switching, a mobile substation, overtime), whether we swap one unit or five, so
> units at one substation should be done together. And the system operator allows each region at
> most two planned substation outages a year. The plan must pay for its outages from the same
> budget and stay within the operator's limit.

You start from the ten-year model. An outage is a cost shared by every replacement at a substation in
one year, so it is not any one unit's coefficient. Give each substation and year an outage decision,
allow a replacement there only in a year its outage is taken, charge each outage to that year's
budget, and keep each region's outages a year within the limit when the request sets one. A request
with an outage cost or an outage limit has outages. The report adds each year's outages to its spend.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56. Its request is the last step's with the two outage fields
added:

```python
Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1)
```

that is five years at $2,000k a year, a ten-year risk window, units 40 and older, a 2% gap, $300k an
outage and one outage per region a year. It prints each year's units, outages and spend:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k a year
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, <outages> outages, $<spend>k
```

with one indented line per year that has replacements, in year order, two spaces before the year.
`<outages>` counts that year's entries of `report.outages`, `<spend>` is that year's entry of
`report.spend_by_year` with the request's outage cost, `<value>` is the `Plan`'s value with no
decimals, money has a comma between thousands, and "units" and "outages" stay plural for one.

`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the earlier
steps' included, and compares Run's report with the expected one.
