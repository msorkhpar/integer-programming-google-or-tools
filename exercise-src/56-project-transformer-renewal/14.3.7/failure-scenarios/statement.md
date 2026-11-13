The asset-health team saw the plans and sent the seventh request:

> **Request 7.** The Weibull curves were fitted to few failures; the scales could be 15% off either
> way, and the shape too. Show us what the plan looks like if the curves are wrong, which units are
> in it whatever the curves, and give us one plan we can defend under all of them.

You start from the stronger model. A scenario is a version of the curves: every kind's Weibull scale
and shape times its factors. Value a replacement under a scenario, value a finished plan under one,
and let the request plan over several: by default for their weighted mean, with each scenario's
weight over the total, and with `objective="worst"` for the worst of them, the most risk removed in
the scenario where the plan removes least.

`renewal/cli.py` and `renewal/finance.py` are the next step's stubs, as the reference has them.
Nothing in this step imports them, so leave them as they are.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56, with the last step's request:

```python
Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
        crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})
```

over four equally weighted versions of the curves:

```python
SCENARIOS = (Scenario("base"), Scenario("younger", eta=0.85), Scenario("older", eta=1.15),
             Scenario("steeper", beta=1.25))
```

It plans twice, `expected` with the request's `scenarios=SCENARIOS` and `worst case` with
`scenarios=SCENARIOS, objective="worst"`, and prints each plan, then a table of what each plan
removes under each version (`evaluate` with the plain request):

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k a year
expected:
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, <outages> outages, $<spend>k
worst case:
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, <outages> outages, $<spend>k
risk removed ($k) by each plan if the fleet fails as in each version:
                  base   younger     older   steeper
  expected  <base><younger><older><steeper>
  worst case<base><younger><older><steeper>
```

The plan blocks are the last step's. The table's header is 12 spaces, then each version's name
right-aligned in 10 characters (`f"{s.name:>10}"`); each row is two spaces, the plan's name
left-aligned in 10 characters (`f"{name:10}"`), then each value right-aligned in 10 characters
with a comma between thousands and no decimals (`f"{v:10,.0f}"`). `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.
