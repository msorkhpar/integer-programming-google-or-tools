The rate-case settlement for the Plains region sent the second request:

> **Request 2.** Plains should get its fair share of the work: at least a quarter of the capital
> spend, every year. The settlement is signed; the plan for the next cycle must keep it.

The planners answered the two open questions: the share is of what the plan spends, not of the
budget, and it holds in every plan year. The change is proposed and archived in `openspec/`: its
proposal, its delta with the regional share and the checks of shares, its design and its tasks, and
the living capital-plan spec now states both requirements. The specs, the tests (one per scenario,
named after it) and the expected report are given and read-only.

You start from the planner of the last lesson, where `Request.shares` is a stub the model ignores.
Make the plan give each named region at least its share, in whole percent, of what the plan spends in
every plan year, with integer coefficients, since CP-SAT takes integers only. Refuse, before solving,
shares that no plan with any spend could keep. Count each region's share in the report apart from
the model.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year and a 25% share for
Plains, and prints each year's starts, spend and Plains share, then the line about the specs;
`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the earlier
steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `check` in `capplan/request.py`

```python
def check(projects: list[Project], request: Request) -> None
```

- **Contract.** A new function. Raises ValueError, with a message, before any model is built, when request.shares names a region with no project in the portfolio, sets a share outside 0 to 100, or sets shares that add up to more than 100. Returns None otherwise.
- **Modeling idea.** Shares that no plan with any spend could keep are refused with a message, not left to an empty plan.
- **Taught in** [14.4.2 A Regional Spend Share: The First Change From Proposal to Archive](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-02/14.4.2-a-regional-spend-share-the-first-change-from-proposal-to-archive.unit.html).

#### `plan` in `capplan/plan.py`

```python
def plan(projects: list[Project], request: Request) -> Plan
```

- **Contract.** As before, after calling request.check first.
- **Modeling idea.** Every entry point checks the request before solving.
- **Taught in** [14.4.2 A Regional Spend Share: The First Change From Proposal to Archive](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-02/14.4.2-a-regional-spend-share-the-first-change-from-proposal-to-archive.unit.html).

#### `allows` in `capplan/plan.py`

```python
def allows(projects: list[Project], request: Request, starts: set[tuple[str, int]]) -> bool
```

- **Contract.** As before, after calling request.check first.
- **Modeling idea.** Every entry point checks the request before solving.
- **Taught in** [14.4.2 A Regional Spend Share: The First Change From Proposal to Archive](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-02/14.4.2-a-regional-spend-share-the-first-change-from-proposal-to-archive.unit.html).

#### `build` in `capplan/model.py`

```python
def build(projects: list[Project], request: Request) -> Built
```

- **Contract.** As before, and for each region in request.shares with a share above 0, and each plan year, a row `share_<region>_<year>`: 100 times the year's spend on the region's projects is at least the share times the year's whole spend, both counted with `spend`.
- **Modeling idea.** A share is a ratio of two spends; multiplied out by the year's spend and by 100 it is one linear row with integer coefficients, and a year with no spend reads 0 >= 0.
- **Taught in** [14.4.2 A Regional Spend Share: The First Change From Proposal to Archive](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-02/14.4.2-a-regional-spend-share-the-first-change-from-proposal-to-archive.unit.html).

#### `share_by_year` in `capplan/report.py`

```python
def share_by_year(projects: list[Project], starts: dict[str, int], region: str) -> dict[int, float]
```

- **Contract.** The region's percent of each year's spend, for the years the plan spends anything, counted from the starts.
- **Modeling idea.** The report counts the share apart from the model, so a test can compare the two.
- **Taught in** [14.4.2 A Regional Spend Share: The First Change From Proposal to Archive](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-02/14.4.2-a-regional-spend-share-the-first-change-from-proposal-to-archive.unit.html).

#### `main` in `main.py`

```python
def main() -> None
```

- **Contract.** As before, with REQUEST setting a 25% share for plains, and one line for each year the plan spends anything (a year with no spend gets no line at this step): '  <year>: <n> starts, $<spend>k, plains <pct>%  <ids>', where <pct> is the year's share_by_year percent rounded to a whole number, as `f"{pct:.0f}"` rounds it.
- **Modeling idea.** The report shows the rule the plan keeps.
- **Taught in** [14.4.2 A Regional Spend Share: The First Change From Proposal to Archive](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-02/14.4.2-a-regional-spend-share-the-first-change-from-proposal-to-archive.unit.html).
