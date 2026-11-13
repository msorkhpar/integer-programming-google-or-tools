The planners sent the third request:

> **Request 3.** Some projects have to be done whatever the model thinks they are worth: a
> regulator's order, storm damage, a safety finding. Give us a must-do switch. And every must-do
> needs a written reason, or the auditors will ask us who forced what, and why.

The change is proposed and archived in `openspec/`, and the living capital-plan spec states its
requirements. The specs, the tests (one per scenario, named after it) and the expected report are
given and read-only. One scenario of the change has no test yet; it is not part of this step.

You start from the planner with the regional share, where `Request.must_do` is a stub field and
`report.overrides` a stub. Make every must-do project start in some year of its window, chosen by the
model, without touching its value. Refuse, before solving, an override for a project not in the
portfolio, or with no reason. List each override with its reason in the report.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, a 25% share for
Plains and one must-do project, and prints the plan, its overrides, each year's line and the line
about the specs; `expected/report.txt` is the report it should print. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `capplan/model.py`

```python
def build(projects: list[Project], request: Request) -> Built
```

- **Contract.** As before, except that a project in request.must_do gets a row `must_<pid>`, its starts over its window summing to exactly 1, in place of `once_<pid>`.
- **Modeling idea.** A must-do is a rule about the plan, so it is a row; the model still chooses the year.
- **Taught in** [14.4.3 A Must-Do Override That Needs a Recorded Reason](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-03/14.4.3-a-must-do-override-that-needs-a-recorded-reason.unit.html).

#### `check` in `capplan/request.py`

```python
def check(projects: list[Project], request: Request) -> None
```

- **Contract.** As before, and raises ValueError for a must-do override that names a project not in the portfolio, or whose reason is empty or only white space.
- **Modeling idea.** The reason is data the model never reads, so it is checked before solving.
- **Taught in** [14.4.3 A Must-Do Override That Needs a Recorded Reason](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-03/14.4.3-a-must-do-override-that-needs-a-recorded-reason.unit.html).

#### `overrides` in `capplan/report.py`

```python
def overrides(request: Request) -> list[str]
```

- **Contract.** Each must-do override as '<pid>: <reason>', the reason stripped, sorted by project id.
- **Modeling idea.** The report says who was forced, and why, next to the plan.
- **Taught in** [14.4.3 A Must-Do Override That Needs a Recorded Reason](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-03/14.4.3-a-must-do-override-that-needs-a-recorded-reason.unit.html).

#### `main` in `main.py`

```python
def main() -> None
```

- **Contract.** As before, with REQUEST marking P010 must-do with the reason 'Storm damage on the Ridge line, inspection report IR-31', and a line '  must-do <override>' for each override, after the plan's summary line.
- **Modeling idea.** The report lists the overrides with the plan.
- **Taught in** [14.4.3 A Must-Do Override That Needs a Recorded Reason](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-03/14.4.3-a-must-do-override-that-needs-a-recorded-reason.unit.html).
