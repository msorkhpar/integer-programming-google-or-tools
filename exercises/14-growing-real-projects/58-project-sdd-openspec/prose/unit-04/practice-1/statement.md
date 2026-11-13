Finance sent the fourth request:

> **Request 4.** From the next cycle, money a year leaves unspent is not lost: it moves into the next
> year, up to a fifth of one year's budget. It moves forward only. No year may spend next year's
> money.

The change is proposed and archived in `openspec/`: it renames the yearly budget requirement, modifies
it, keeping its two old scenarios, and adds a check of the percent. The specs, the tests (one per
scenario, named after it) and the expected report are given and read-only.

You start from the planner with must-do overrides, where `Request.carry` is a stub field. Let each
plan year but the last pass unspent money to the next, up to the carry-over percent of one year's
budget, never less than nothing, and make each year's budget row a balance of what it spends, passes
on and was passed. A request with no carry-over must plan exactly as before. Refuse a percent
outside 0 to 100, and let the report count what each year passes on from the plan's spend.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, a 25% share for
Plains, one must-do and 20% carry-over, and prints a line for every plan year with what it carries;
`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the earlier
steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `capplan/model.py`

```python
def build(projects: list[Project], request: Request) -> Built
```

- **Contract.** As before, except the budget rows. For every plan year but the last, an integer variable `carry_<year>` between 0 and request.budget * request.carry // 100: what the year passes to the next. Each year's row `budget_<year>` keeps the year's spend plus what it passes on within the budget plus what the year before passed to it (0 for the first year, and the last year passes nothing). Built gains `carry`, the variables by year.
- **Modeling idea.** Carry-over is a bounded variable per year: its lower bound forbids borrowing, its upper bound is the cap, and the budget row becomes a balance between years.
- **Taught in** [14.4.4 Carry-Over: A MODIFIED Budget Rule and a RENAMED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-04/14.4.4-carry-over-a-modified-budget-rule-and-a-renamed-requirement.unit.html).

#### `check` in `capplan/request.py`

```python
def check(projects: list[Project], request: Request) -> None
```

- **Contract.** As before, and raises ValueError with the message `the carry-over is <carry>%, outside 0 to 100` for a carry-over percent below 0 or above 100; 0 and 100 are accepted.
- **Modeling idea.** A request no plan could mean is refused before solving.
- **Taught in** [14.4.4 Carry-Over: A MODIFIED Budget Rule and a RENAMED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-04/14.4.4-carry-over-a-modified-budget-rule-and-a-renamed-requirement.unit.html).

#### `carry_by_year` in `capplan/report.py`

```python
def carry_by_year(projects: list[Project], starts: dict[str, int], request: Request) -> dict[int, int]
```

- **Contract.** For every plan year but the last, what it passes to the next, counted from the starts: its budget plus what it was passed, less its spend, at most the cap.
- **Modeling idea.** The carry variables are free where money is left over, so the report counts the carry from the plan's spend.
- **Taught in** [14.4.4 Carry-Over: A MODIFIED Budget Rule and a RENAMED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-04/14.4.4-carry-over-a-modified-budget-rule-and-a-renamed-requirement.unit.html).

#### `main` in `main.py`

```python
def main() -> None
```

- **Contract.** As before, with REQUEST also setting a 20% carry-over, and one line for every plan year, a year with no spend included: '  <year>: <n> starts, $<spend>k, plains <pct>%, carries $<carried>k  <ids>', with trailing spaces stripped and <pct> rounded as before (`:.0f`). A year with no spend prints `0 starts, $0k, plains 0%`, and the last plan year, which passes nothing on, prints `carries $0k`.
- **Modeling idea.** The report shows what each year passes on.
- **Taught in** [14.4.4 Carry-Over: A MODIFIED Budget Rule and a RENAMED Requirement](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-04/14.4.4-carry-over-a-modified-budget-rule-and-a-renamed-requirement.unit.html).
