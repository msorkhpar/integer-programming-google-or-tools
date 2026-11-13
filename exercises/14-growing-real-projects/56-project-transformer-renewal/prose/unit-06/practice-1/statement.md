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

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `renewal/model.py`

```python
def build(fleet: list[Transformer], request: Request) -> Built
```

- **Contract.** As before, except the outage rows: with request.link == "aggregated" the row `outage_<s>_<year>` of the step before; otherwise ("per-unit", now Request's default) a row `outage_<tid>_<year>` per candidate and year, x[tid, year] <= out[s, year].
- **Modeling idea.** Each aggregated row is the sum of the per-unit rows, so the per-unit form allows less in the LP relaxation and gives a tighter bound with the same integer plans.
- **Taught in** [6.7.1 Comparing Formulations by Their LP Bound](../../../../06-formulation-craft/29-strong-formulations/units/unit-01/6.7.1-comparing-formulations-by-their-lp-bound.unit.html).

#### `relax` in `renewal/model.py`

```python
def relax(built: Built) -> Built
```

- **Contract.** The LP relaxation, in place: every variable of the model made continuous within its bounds; returns the same Built.
- **Modeling idea.** Relaxing integrality gives the bound a branch-and-bound search starts from.
- **Taught in** [6.7.1 Comparing Formulations by Their LP Bound](../../../../06-formulation-craft/29-strong-formulations/units/unit-01/6.7.1-comparing-formulations-by-their-lp-bound.unit.html).

#### `lp_bound` in `renewal/plan.py`

```python
def lp_bound(fleet: list[Transformer], request: Request) -> float
```

- **Contract.** Builds the model, relaxes it, solves it, and returns the objective value: an upper bound on the risk any plan removes.
- **Modeling idea.** Compare two formulations of one problem by their LP bounds: the lower the bound of a maximization, the stronger the form.
- **Taught in** [6.7.1 Comparing Formulations by Their LP Bound](../../../../06-formulation-craft/29-strong-formulations/units/unit-01/6.7.1-comparing-formulations-by-their-lp-bound.unit.html).

#### `violations` in `renewal/check.py`

```python
def violations(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> list[str]
```

- **Contract.** One line per broken rule, each starting with its rule's name and the offending key, in this order. First, per replaced unit in id order: `<tid>: <year> is outside the plan` when the year is not a plan year, and `<tid>: younger than <min_age>, not a candidate` when the unit is under the age screen. Then, per year in year order: `budget <year>: <spend> > <budget>`, with the spend of report.spend_by_year including the outage cost. Then, when request.outages is set, sorted by region and then year: `outages <region> <year>: <count> > <outages>`, where <count> is the number of the region's substations with an outage that year (report.outages). Then, when request.crew_weeks is set, sorted by region and then year: `crews <region> <year>: <weeks> > <crew_weeks>`, where <weeks> is the summed crew-weeks of the region's replacements that year. Last, when request.lead_times is set, per kind in KINDS order: `spares <kind>: <early> > <stock>`, a kind with no spares listed having a stock of 0. Every number is printed as a plain integer. An empty list when the plan keeps every rule.
- **Modeling idea.** A checker that shares no code with the model catches a row the model lost.
- **Taught in** [12.3.1 Unit-Testing One Constraint at a Time](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-01/12.3.1-unit-testing-one-constraint-at-a-time.unit.html).

#### `rolling` in `renewal/rolling.py`

```python
def rolling(fleet: list[Transformer], request: Request, window: int = 3, keep: int = 1) -> Plan
```

- **Contract.** Builds the model once; from the first plan year, solves the years [a, a + window) with earlier years' replacement and outage variables fixed to their kept values and later years' fixed to 0, keeps the first `keep` years (every year of the last window), and moves on by `keep` years. Returns the last solve's Plan, or the first failed solve's.
- **Modeling idea.** A rolling horizon trades the bound for speed: each window is a small model, and every row still counts what earlier windows decided.
- **Taught in** [11.3.5 Rolling Horizon and LNS Heuristics](../../../../11-performance-at-scale/44-decomposition-and-heuristics/units/unit-05/11.3.5-rolling-horizon-and-lns-heuristics.unit.html).
