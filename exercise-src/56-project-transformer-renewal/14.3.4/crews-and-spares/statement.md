The bundled plan went to the field, and the regions answered with the fourth request:

> **Request 4.** Each region has 12 crew-weeks a year for transformer work. A small unit takes 2
> crew-weeks to swap, a medium one 4, a large one 8. And new units are not on a shelf: a medium unit
> takes a year from order to delivery and a large one three, so nothing ordered now arrives before
> 2028 or 2030. Until then, a replacement must come from the spares we hold: two medium units and
> one large. Small units are stocked by the supplier and arrive within the year.

You start from the model with outages. When the request gives crew-weeks, keep each region's crew
work in each year within them. When it asks for lead times, a replacement of a kind before its first
delivery year (2027 plus the kind's lead time in years) uses a spare, so those replacements of each
kind must not outnumber the spares held of it, and a kind the request lists no spares for has none.

`renewal/reference.py` is the next step's stub, as the reference has it. Nothing in this step
imports it, so leave it as it is.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56. Its request is the last step's with crews, lead times and
spares added:

```python
Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
        crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})
```

that is 4 crew-weeks a region a year, lead times on, and one medium spare and no large one. It
prints each year's units, outages and spend in the last step's format:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k a year
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, <outages> outages, $<spend>k
```

with one indented line per year that has replacements, in year order, two spaces before the year.
`<outages>` counts that year's entries of `report.outages`, `<spend>` is that year's entry of
`report.spend_by_year` with the request's outage cost, `<value>` is the `Plan`'s value with no
decimals, money has a comma between thousands, and "units" and "outages" stay plural for one.

`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the
earlier steps' included, and compares Run's report with the expected one.
