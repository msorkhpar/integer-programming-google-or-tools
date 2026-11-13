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

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `renewal/model.py`

```python
def build(fleet: list[Transformer], request: Request) -> Built
```

- **Contract.** As before, and when the request has outages (an outage_cost above 0 or an outages limit; Request.has_outages() answers it): one binary out[s, year] per candidate substation and plan year, named `out_<s>_<year>`; a row `outage_<s>_<year>` allowing replacements at s in that year only when out[s, year] is 1 (the sum of its candidates' x at most their count times out); when request.outages is set, a row `coord_<region>_<year>` for each region with candidate substations, keeping the region's outages within it; and request.outage_cost times each year's outages in that year's budget row. Built.out holds the outage variables, keyed by (substation, year), and is empty without outages.
- **Modeling idea.** A cost shared by several decisions gets its own binary, linked to the decisions that need it, and is paid from the budget row rather than scored in the objective.
- **Taught in** [14.3.3 Substation Bundles and Outage Coordination](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-03/14.3.3-substation-bundles-and-outage-coordination.unit.html).

#### `outages` in `renewal/report.py`

```python
def outages(fleet: list[Transformer], replace: dict[str, int]) -> set[tuple[str, int]]
```

- **Contract.** The (substation, year) pairs a plan's replacements need: one per substation and year with at least one replacement.
- **Modeling idea.** An outage serves every replacement at its substation that year.
- **Taught in** [14.3.3 Substation Bundles and Outage Coordination](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-03/14.3.3-substation-bundles-and-outage-coordination.unit.html).

#### `spend_by_year` in `renewal/report.py`

```python
def spend_by_year(fleet: list[Transformer], replace: dict[str, int], outage_cost: int = 0) -> dict[int, int]
```

- **Contract.** Each year's replacement cost plus outage_cost for each outage that year, $k, by year in order.
- **Modeling idea.** The report counts money the way the budget row does, each outage once.
- **Taught in** [14.3.3 Substation Bundles and Outage Coordination](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-03/14.3.3-substation-bundles-and-outage-coordination.unit.html).
