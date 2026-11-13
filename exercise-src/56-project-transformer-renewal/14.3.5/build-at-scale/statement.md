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
