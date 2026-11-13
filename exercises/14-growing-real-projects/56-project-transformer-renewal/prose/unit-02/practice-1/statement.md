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

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `risk_removed` in `renewal/risk.py`

```python
def risk_removed(t: Transformer, start: int, request: Request) -> float
```

- **Contract.** The coefficient of x[i, start], $k: for each year y of the risk window (request.risk_years(), the window's years from FIRST_YEAR, or the plan's years when window is None) with y >= start, the old unit's PoF at its age in year y minus a new unit's PoF at age y - start, times the unit's CoF, divided by (1 + request.rate) to the power y - FIRST_YEAR. Years before start remove nothing.
- **Modeling idea.** A replacement's value is the failure cost it avoids each year after it, discounted to today, so a later replacement is worth less.
- **Taught in** [7.3.4 Risk Reduction From an Intervention, Year by Year](../../../../07-the-capital-planning-domain/32-asset-risk/units/unit-04/7.3.4-risk-reduction-from-an-intervention-year-by-year.unit.html).

#### `pof_next` in `renewal/risk.py`

```python
def pof_next(age: float, kind: str) -> float
```

- **Contract.** The probability that a unit of this kind, working at `age`, fails within the year: 1 - exp((age / eta)^beta - ((age + 1) / eta)^beta), with beta and eta from KINDS[kind]. It reproduces the fleet's pof column.
- **Modeling idea.** A Weibull curve gives the PoF at any age, so a plan can value a unit in years it has not reached.
- **Taught in** [7.3.1 Probability of Failure and Hazard Curves (Weibull)](../../../../07-the-capital-planning-domain/32-asset-risk/units/unit-01/7.3.1-probability-of-failure-and-hazard-curves-weibull.unit.html).

#### `build` in `renewal/model.py`

```python
def build(fleet: list[Transformer], request: Request) -> Built
```

- **Contract.** Candidates are the units at least request.min_age old. One binary x[tid, year] per candidate and plan year (request.plan_years(), `years` years from FIRST_YEAR), named `x_<tid>_<year>`; a row `once_<tid>` letting each candidate be replaced at most once; a row `budget_<year>` per plan year keeping that year's replacement cost within request.budget; and the summed risk_removed coefficients as the objective to maximize. Built.x is keyed by (tid, year), Built.budget by year.
- **Modeling idea.** A start-year variable per unit and year, with a row allowing one start, turns when into a choice the solver makes.
- **Taught in** [6.4.1 Start-Time Variables x[i,t] and Timing Windows](../../../../06-formulation-craft/26-multi-period-timing/units/unit-01/6.4.1-start-time-variables-x-i-t-and-timing-windows.unit.html).

#### `feasible` in `renewal/plan.py`

```python
def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool
```

- **Contract.** Fixes x[tid, year] to 1 for each listed unit and its year and every other variable to 0, solves, and answers whether the solver found a plan.
- **Modeling idea.** A pinned plan now names a year for each unit, so the pin is on the pair.
- **Taught in** [12.3.1 Unit-Testing One Constraint at a Time](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-01/12.3.1-unit-testing-one-constraint-at-a-time.unit.html).

#### `plan` in `renewal/plan.py`

```python
def plan(fleet: list[Transformer], request: Request) -> Plan
```

- **Contract.** As before, with request.gap as the solver's relative gap tolerance; the Plan maps each replaced unit to the year of its variable that is 1.
- **Modeling idea.** A gap tolerance lets the solver stop once its plan is provably close to the best.
- **Taught in** [14.3.2 A Ten-Year Budget and Weibull Failure Risk](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-02/14.3.2-a-ten-year-budget-and-weibull-failure-risk.unit.html).

#### `spend_by_year` in `renewal/report.py`

```python
def spend_by_year(fleet: list[Transformer], replace: dict[str, int], outage_cost: int = 0) -> dict[int, int]
```

- **Contract.** What the replacements cost in each year, $k: for each year that appears in `replace` (transformer id -> year), the summed cost of the units replaced that year, as a dict sorted by year. Years with no replacement are left out. `outage_cost` is a stub for the next lesson, which charges each outage to its year; this step ignores it.
- **Modeling idea.** A plan is a map from unit to year, so the report groups it by year and adds up costs; the solver's own rows are not read back.
- **Taught in** [14.3.2 A Ten-Year Budget and Weibull Failure Risk](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-02/14.3.2-a-ten-year-budget-and-weibull-failure-risk.unit.html).
