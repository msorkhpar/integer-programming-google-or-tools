Engineering sent the fifth request:

> **Request 5.** The cap of three starts a year was the design-review board's capacity. Reviews are
> now done as each design is ready. Retire the cap. And make sure nobody who still sends it gets a
> different plan without being told.

The change is proposed and archived in `openspec/`: it removes the Yearly start cap requirement, with
its reason and migration, and adds two requirements for what replaces it. The specs, the tests (one
per scenario, named after it; the removed scenario's test is gone) and the expected report are given
and read-only.

You start from the planner with carry-over. Take the yearly start cap out of the model, so any number
of projects may start in a year. Keep the request's field, with no cap as its default, and refuse,
before solving, any request that still sets it, with a message that names the change that retired it.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, a 25% share for
Plains, one must-do and 20% carry-over, prints the plan, then what happens to the same request with a
start cap of 3, and the line about the specs; `expected/report.txt` is the report it should print.
Submit runs every test in `tests/`, the earlier steps' included, and compares Run's report with the
expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `capplan/model.py`

```python
def build(projects: list[Project], request: Request) -> Built
```

- **Contract.** As before, without the `starts_<year>` rows: any number of projects may start in a year.
- **Modeling idea.** A removed rule takes its rows with it.
- **Taught in** [14.4.5 Retiring the Yearly Start Cap: A REMOVED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-05/14.4.5-retiring-the-yearly-start-cap-a-removed-requirement.unit.html).

#### `check` in `capplan/request.py`

```python
def check(projects: list[Project], request: Request) -> None
```

- **Contract.** As before, and first raises ValueError with the message `max_starts was retired by the change retire-yearly-start-cap; remove it from the request` when request.max_starts is anything but None, 0 included. Request.max_starts now defaults to None.
- **Modeling idea.** A retired setting is refused with a message, so no caller gets a different plan without being told.
- **Taught in** [14.4.5 Retiring the Yearly Start Cap: A REMOVED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-05/14.4.5-retiring-the-yearly-start-cap-a-removed-requirement.unit.html).

#### `main` in `main.py`

```python
def main() -> None
```

- **Contract.** As before, and after the yearly lines one line for the same request with max_starts=3: 'a request that sets max_starts=3: refused, <message>' or 'a request that sets max_starts=3: accepted'.
- **Modeling idea.** The report shows what a caller who still sends the cap gets.
- **Taught in** [14.4.5 Retiring the Yearly Start Cap: A REMOVED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-05/14.4.5-retiring-the-yearly-start-cap-a-removed-requirement.unit.html).
