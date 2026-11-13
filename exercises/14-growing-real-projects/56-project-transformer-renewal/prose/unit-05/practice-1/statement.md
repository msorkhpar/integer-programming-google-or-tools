The pilot worked on 500 units, and the fifth request asked for the whole fleet:

> **Request 5.** Run it for all of GridCap's substation transformers, about 5,000 units in ten
> districts. Budgets, crews and outage limits are ten times the pilot's, spares too. We need the
> plan in the same morning we ask for it.

You start from the model with crews and spares, whose builder scans the whole fleet inside its loops
over substations and regions. Keep that builder as the reference, under a new name, and make `build`
fast: group the units once, sum with `mathopt.fast_sum`, and compute every objective coefficient in
one array computation. The fast builder must make exactly the reference's model. And give a request
for a fleet `factor` times larger: every limit grows with the fleet, every rate and price stays.

"The same model" is checked by name: the same variables in the same order, and the same rows, each
with the same bounds and coefficients, in any order. The reference's crews block takes the regions in
`REGIONS` order and skips a region with no candidates, and so does its region-limit block; the
spares block takes the kinds in `KINDS` order. The lesson's fast builder keeps those loops and only
replaces the scans inside them with lookups in units grouped once (its `group` returns the groups
with their keys sorted), so its rows come out in the same order too.

`renewal/check.py` and `renewal/rolling.py` are the next step's stubs, as the reference has them.
Nothing in this step imports them, so leave them as they are.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56, with the last step's request:

```python
Request(budget=2_000, years=5, window=10, min_age=40, gap=0.02, outage_cost=300, outages=1,
        crew_weeks=4, lead_times=True, spares={"medium": 1, "large": 0})
```

It checks that the fast builder makes the reference builder's model with these two helpers, which
compare two MathOpt models by name (row bounds and coefficients exactly, objective coefficients to
`1e-9`):

```python
def rows(m: mathopt.Model) -> dict:
    """Each row's bounds by name, and each coefficient by row and variable name."""
    found: dict = {c.name: (c.lower_bound, c.upper_bound) for c in m.linear_constraints()}
    for e in m.linear_constraint_matrix_entries():
        found[e.linear_constraint.name, e.variable.name] = e.coefficient
    return found


def same_model(a: mathopt.Model, b: mathopt.Model) -> bool:
    """The same variables, rows and coefficients, by name; objective coefficients to 1e-9."""
    oa = {t.variable.name: t.coefficient for t in a.objective.linear_terms()}
    ob = {t.variable.name: t.coefficient for t in b.objective.linear_terms()}
    return ([v.name for v in a.variables()] == [v.name for v in b.variables()] and rows(a) == rows(b)
            and oa.keys() == ob.keys()
            and all(math.isclose(oa[k], ob[k], rel_tol=1e-9, abs_tol=1e-9) for k in oa))
```

Its report is the last step's with two new lines, the second line and the last:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k a year
fast builder: <variables> variables, <rows> rows; the reference builder's model: <verdict>
<n> units replaced, risk removed $<value>k (<status>)
  <year>: <units> units, <outages> outages, $<spend>k
for 50 units: budget $<budget>k, outages <outages>, crew-weeks <crew_weeks>, spares <spares>
```

`<variables>` and `<rows>` count the fast model's variables and linear constraints, `<verdict>` is
`the same` when `same_model` holds and `different` otherwise, the per-year lines are the last
step's, and the last line reads the fields of `REQUEST.scaled(2)`, with `<spares>` printed as the
dict itself. `expected/report.txt` is the report it should print. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `renewal/model.py`

```python
def build(fleet: list[Transformer], request: Request) -> Built
```

- **Contract.** Makes the reference builder's model, with the same variables in the same order, the same row names, bounds and coefficients, and the same objective coefficients to 1e-9, in time that grows with the fleet: group the candidates by substation, region and kind once, build each sum with mathopt.fast_sum, and take the objective's coefficients from risk_table.
- **Modeling idea.** Index once and never scan the fleet inside a loop over groups; build sums in one call.
- **Taught in** [11.1.2 Vectorized Model Building From DataFrames](../../../../11-performance-at-scale/42-model-building-at-scale/units/unit-02/11.1.2-vectorized-model-building-from-dataframes.unit.html).

#### `risk_table` in `renewal/risk.py`

```python
def risk_table(units: list[Transformer], request: Request) -> np.ndarray
```

- **Contract.** An array with a row per unit and a column per plan year, entry [i, j] equal to risk_removed(units[i], the j-th plan year, request), computed with numpy arrays one kind at a time.
- **Modeling idea.** A coefficient that is a sum over years is a matrix product over arrays of ages and years.
- **Taught in** [11.1.2 Vectorized Model Building From DataFrames](../../../../11-performance-at-scale/42-model-building-at-scale/units/unit-02/11.1.2-vectorized-model-building-from-dataframes.unit.html).

#### `build_reference` in `renewal/reference.py`

```python
def build_reference(fleet: list[Transformer], request: Request) -> Built
```

- **Contract.** The builder of the step before, unchanged: one plain loop per row family, and risk_removed for each coefficient.
- **Modeling idea.** A faster builder is right only if it makes the same model as a slow one you trust, so keep the slow one and compare.
- **Taught in** [14.3.5 From 500 to 5,000 Transformers: Building the Model at Scale](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-05/14.3.5-from-500-to-5-000-transformers-building-the-model-at-scale.unit.html).

#### `scaled` in `renewal/request.py`

```python
def scaled(self, factor: int) -> Request
```

- **Contract.** The same request for a fleet factor times larger: budget, outages, crew_weeks and each kind's spares times factor (a limit that is None stays None); everything else, the outage cost included, unchanged.
- **Modeling idea.** A limit is a quantity of the fleet's resources and grows with it; a price or a rate does not.
- **Taught in** [14.3.5 From 500 to 5,000 Transformers: Building the Model at Scale](../../../../14-growing-real-projects/56-project-transformer-renewal/units/unit-05/14.3.5-from-500-to-5-000-transformers-building-the-model-at-scale.unit.html).
