Finance read the first plan and sent it back:

> Your plan spends $13.14M in 2027. We have $8.89M that year. The $38.39M was five yearly budgets
> added up, and they are not interchangeable: money not spent in a year does not roll over. Plan
> by year. A project may start in any year of its window, and its cost lands in the years it is
> worked on, not all at the start. And no plan may run past 2031.

You start from the one-envelope planner of the lesson before. Change it to plan by year. Read each
project's cost profile and latest start and each year's budget from the export, and let the model
choose the year each funded project starts, inside its window. A project's cost is spent over its
years of work, and each year's spend stays within that year's budget. No project may be funded with
work that runs past the plan's last year. The plan says the year each funded project starts, and
the report shows each year's spend against its budget.

`Request.starts` is a stub in `cipt/data.py` that returns the earliest year alone; `Project` needs
the arithmetic of its profile too: how many years its work lasts, and what it spends in each
calendar year for a given start. The report keeps its status line and its project lines and
changes in two ways, every amount in whole $k with thousands commas:

- the funded line's budget is the total of all yearly budgets:
  `funded <n> of <all> projects, capex $<capex>k of $<sum of yearly budgets>k, value $<value>k`,
  where value is still the funded projects' earliest-start value;
- after it, before the project lines, one line per plan year in year order:
  `  <year>  spend $<spend>k of $<budget>k` (two spaces before the year and two after it), with
  0 for a year nothing spends in.

Run executes `main.py`, which plans the demo export and prints the report; `expected/report.txt` is
the report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `cipt/model.py`

```python
def build(request: Request) -> Built
```

- **Contract.** Takes a Request. Returns a Built with one binary x[(id, t)] per project and allowed start year t, a row `once_<id>` per project (it starts at most once), a row `budget_<y>` per plan year (that year's spread spend within that year's budget), and the summed value of the starts as the objective to maximize.
- **Modeling idea.** A start-year variable per project and year carries the when, and the window is the set of variables that exist: a start outside it has no variable at all.
- **Taught in** [6.4.1 Start-Time Variables x[i,t] and Timing Windows](../../../../06-formulation-craft/26-multi-period-timing/units/unit-01/6.4.1-start-time-variables-x-i-t-and-timing-windows.unit.html).

#### `starts` in `cipt/data.py`

```python
def starts(self, project: Project) -> range
```

- **Contract.** Returns the start years a project may use: from the later of its earliest start and the plan's first year, to the earlier of its latest start and the last year that lets all its work end inside the plan. An empty range when no start fits.
- **Modeling idea.** Cutting the window in the data keeps the model free of rows that only forbid impossible starts.
- **Taught in** [6.4.1 Start-Time Variables x[i,t] and Timing Windows](../../../../06-formulation-craft/26-multi-period-timing/units/unit-01/6.4.1-start-time-variables-x-i-t-and-timing-windows.unit.html).

#### `spend_by_year` in `cipt/model.py`

```python
def spend_by_year(request: Request, x: dict) -> dict[int, mathopt.LinearSum]
```

- **Contract.** Returns one linear expression per plan year, with an entry for every plan year (an empty sum when no start can spend in it): for every project and allowed start, each year's amount of its cost profile times that start's variable, summed into the calendar year it is spent in.
- **Modeling idea.** A start in year t spends profile[k] in year t + k, so a yearly budget row sums over starts, not over projects.
- **Taught in** [6.4.2 Cash-Flow Spreading Across Years](../../../../06-formulation-craft/26-multi-period-timing/units/unit-02/6.4.2-cash-flow-spreading-across-years.unit.html).

#### `read_plan` in `cipt/solve.py`

```python
def read_plan(built: Built, result: mathopt.SolveResult) -> Plan
```

- **Contract.** Turns a SolveResult into a Plan whose starts map each funded project to the year its variable is 1.
- **Modeling idea.** The schedule is read off the variables that are 1; the key of each variable says the year.
- **Taught in** [6.4.1 Start-Time Variables x[i,t] and Timing Windows](../../../../06-formulation-craft/26-multi-period-timing/units/unit-01/6.4.1-start-time-variables-x-i-t-and-timing-windows.unit.html).

#### `spend_by_year` in `cipt/report.py`

```python
def spend_by_year(request: Request, plan: Plan) -> dict[int, int]
```

- **Contract.** Returns what a Plan spends in each plan year, in whole $k, from the funded projects' starts and cost profiles, with 0 for a year nothing spends in.
- **Modeling idea.** Compute the report's numbers from the plan and the data, not from the model, so the report checks the model instead of repeating it.
- **Taught in** [14.2.2 Many Years: Start Years, Windows and Cash-Flow Spreading](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-02/14.2.2-many-years-start-years-windows-and-cash-flow-spreading.unit.html).

#### `render` in `cipt/report.py`

```python
def render(request: Request, plan: Plan) -> str
```

- **Contract.** Returns the report: the status line, the funded line with the total of all yearly budgets, one line per plan year reading `  <year>  spend $<spend>k of $<budget>k`, then one line per funded project.
- **Modeling idea.** A yearly budget is only trusted when the report shows each year against its own limit.
- **Taught in** [14.2.2 Many Years: Start Years, Windows and Cash-Flow Spreading](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-02/14.2.2-many-years-start-years-windows-and-cash-flow-spreading.unit.html).

#### `load_request` in `cipt/data.py`

```python
def load_request(raw: dict) -> Request
```

- **Contract.** Builds a Request from the export's dictionary: each project's cost profile, NPV for its earliest start, earliest and latest start; the plan's years; and the budget of each year, keyed by an int year. Refuses duplicate project ids.
- **Modeling idea.** Read the columns the model needs now, and only those.
- **Taught in** [14.2.2 Many Years: Start Years, Windows and Cash-Flow Spreading](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-02/14.2.2-many-years-start-years-windows-and-cash-flow-spreading.unit.html).
