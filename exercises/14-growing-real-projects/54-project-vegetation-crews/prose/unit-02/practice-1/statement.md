The program manager sent the list to the crew supervisor, who answered:

> Your list needs 45 crew-weeks of trimming. I have two crews from April to September, and I plan
> them a month at a time: each crew gives me four weeks a month. Tell me which circuits to trim *and
> in which month*, without ever booking more work in a month than my crews can do.

You start from the knapsack of the lesson before. Read each circuit's crew-weeks and the season's
crews and months, and have the generator draw them. Let the model choose the month of each trimmed
circuit, trim a circuit in one month at most, and keep each month's booked crew-weeks within what
its crews can do, as well as the season within its budget. Keep anything HiGHS prints out of the
report. The report shows each month's booked crew-weeks against its capacity. A season of one month
is a season too: its crews may stop a trim the budget allows.

**The report.** The first line gains `, crews <crews>, months <months>`. After the status line comes
one line per month, from month 1 to the last, an empty month included: two spaces, `month <m>: `, the
crew-weeks booked that month right-aligned in two characters, `/`, the month's capacity and
` crew-weeks`; then, only when the month has trims, two spaces and the trims sorted by circuit id,
each as `<cid>(<weeks>)`, one space apart. An empty month's line ends at `crew-weeks`, so no line ends
in a space.

**Which months.** The objective counts the risk removed whatever the month, so the tiny season has
several equally good plans, and the months HiGHS returns depend on the order the model is built in
(the lesson shows the same model built in two orders giving two plans). `expected/report.txt` comes
from this order: the variables circuit by circuit in the season's order, months 1 to the last within
each circuit; then the once rows in circuit order, the crew rows in month order, the budget row, and
the objective, solved with HiGHS at a relative gap of zero. Build yours in that order for the report
check; the tests accept any order.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `vegcrew/planner.py`

```python
def build(season: Season) -> tuple[mathopt.Model, dict[tuple[str, int], mathopt.Variable]]
```

- **Contract.** Takes a Season. Returns a MathOpt model and one binary x[(cid, m)] per circuit and month m from 1 to season.months (named `x_<cid>_<m>`): a row `once_<cid>` per circuit (trimmed in at most one month), a row `crews_<m>` per month (the crew-weeks of the circuits trimmed that month within crews times WEEKS_PER_MONTH), a row budget, and the summed risk of the trimmed circuits as the objective to maximize. The expected report comes from this build order: the variables circuit by circuit in the season's order, months 1 to season.months within each circuit; then the once rows in circuit order, the crews rows in month order, the budget row, and the objective. The objective does not name the month, so another order can give other months that are just as good; the tests accept them, the report check does not.
- **Modeling idea.** A start-month binary per circuit and month carries the when; each month's crews are one more capacity row, and the once row keeps a circuit from being counted twice.
- **Taught in** [6.4.1 Start-Time Variables x[i,t] and Timing Windows](../../../../06-formulation-craft/26-multi-period-timing/units/unit-01/6.4.1-start-time-variables-x-i-t-and-timing-windows.unit.html).

#### `solve_quietly` in `vegcrew/planner.py`

```python
def solve_quietly(model: mathopt.Model) -> mathopt.SolveResult
```

- **Contract.** Solves the model with HiGHS at a relative gap of zero and returns the SolveResult, with nothing HiGHS writes at the C level reaching the program's standard output.
- **Modeling idea.** The HiGHS bundled with OR-Tools can print a stray debug line on some MIP solves; the report a manager reads must not carry it.
- **Taught in** [14.1.2 Crews and Months: Capacity Over Time](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-02/14.1.2-crews-and-months-capacity-over-time.unit.html).

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season) -> Plan
```

- **Contract.** Builds and quietly solves the model, and returns a Plan with one Trim(cid, month) per variable above 0.5, and the trimmed circuits' summed cost and risk removed.
- **Modeling idea.** The schedule is read off the variables that are 1; the key of each variable says the month.
- **Taught in** [6.4.1 Start-Time Variables x[i,t] and Timing Windows](../../../../06-formulation-craft/26-multi-period-timing/units/unit-01/6.4.1-start-time-variables-x-i-t-and-timing-windows.unit.html).

#### `season_from_dict` in `vegcrew/data.py`

```python
def season_from_dict(raw: dict) -> Season
```

- **Contract.** Also reads each circuit's weeks (crew-weeks to trim it) and the season's crews and months; columns the planner does not use are still ignored.
- **Modeling idea.** Read the columns the model needs now, and only those.
- **Taught in** [14.1.2 Crews and Months: Capacity Over Time](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-02/14.1.2-crews-and-months-capacity-over-time.unit.html).

#### `scenario` in `vegcrew/generate.py`

```python
def scenario(size: str = "small", seed: int = 54) -> dict
```

- **Contract.** Also gives each circuit its weeks, ceil(miles / u) with u drawn by uniform(4.0, 7.0) from its own stream named 'weeks', one draw per circuit in order after every circuit is drawn, and the season crews (CREWS by size: tiny 1, small 2, medium 6) and months (6).
- **Modeling idea.** A column drawn from its own stream leaves the values of every earlier column as they were.
- **Taught in** [14.1.2 Crews and Months: Capacity Over Time](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-02/14.1.2-crews-and-months-capacity-over-time.unit.html).

#### `format_plan` in `vegcrew/report.py`

```python
def format_plan(season: Season, plan: Plan) -> str
```

- **Contract.** The first line gains `, crews <crews>, months <months>`. After the status line comes one line per month m from 1 to season.months, an empty month included: two spaces, `month <m>: `, the crew-weeks booked that month right-aligned in two characters, `/<capacity> crew-weeks`, and then, only when the month has trims, two spaces and its trims sorted by circuit id, each as `<cid>(<weeks>)`, separated by single spaces. An empty month's line ends at `crew-weeks`; no line ends in a space.
- **Modeling idea.** A capacity is only trusted when the report shows each month's use against it.
- **Taught in** [14.1.2 Crews and Months: Capacity Over Time](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-02/14.1.2-crews-and-months-capacity-over-time.unit.html).
