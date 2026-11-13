The crew supervisor booked the month plan and came back within a day:

> Month 1 says C12, 7 crew-weeks, out of 8. That means both my crews on C12 for three and a half
> weeks each. I don't split a circuit between crews: the crew that starts a circuit finishes it, one
> week after another, and it hands nothing over. And C12 takes one crew seven weeks, so it can't sit
> inside one month anyway. Give me a crew and a start week for every trim.

You start from the month planner of the lesson before. Plan in weeks with CP-SAT instead: each
trimmed circuit gets one crew and a run of consecutive weeks as long as the circuit's crew-weeks,
inside the season, and no crew works two circuits in the same week. The budget still holds and the
plan still removes the most risk. A trim may run across a month's end, and a circuit too long for
the season is left out, never shared between crews. The report draws one line per crew, a character
per week.

**The report.** The first line ends `, crews <crews>, weeks <weeks>` in place of the months, the
weeks being the months times 4. The month lines go. After the status line comes one line per crew,
K1 first: two spaces, the crew id, one space, the week chart, two spaces, and the crew's trims in
order of first week, each as `<cid>:<first>-<last>` with both weeks included, one space apart. The
chart has one character per week of the season: `.` while the crew is free, and the last character
of the circuit id while it trims. The two spaces after the chart are printed even for a crew with
no trims, so an idle crew's line ends in two spaces, here and in every later step.

**Which order.** The objective counts the risk removed whatever the order of the work, so the tiny
season has several equally good plans, and the one CP-SAT returns depends on how the model is built
and on how many workers search (the lesson shows the same model, built from the circuits in reverse
order, giving another plan). `expected/report.txt` comes from one worker and this build order: for
each circuit in the season's order that fits, and for each crew from K1 on, the presence literal,
the start and the optional interval, then that circuit's at-most-one; after every circuit, one
no-overlap per crew from K1 on, the budget row, and the objective. Keep `TIME_LIMIT = 10.0` and
`WORKERS = 4` in `planner.py`, and have `main.py` set `planner.WORKERS = 1` (after
`from vegcrew import planner`) before it plans, as the lesson's `main.py` does. The tests accept any
order.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `crew_ids` in `vegcrew/planner.py`

```python
def crew_ids(season: Season) -> list[str]
```

- **Contract.** Returns the season's crew ids, K1 to `K<crews>`.
- **Modeling idea.** A crew is a resource with its own timeline, so it needs a name.
- **Taught in** [14.1.3 A Trim Takes Weeks on One Crew: From MILP to CP-SAT Intervals](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-03/14.1.3-a-trim-takes-weeks-on-one-crew-from-milp-to-cp-sat-intervals.unit.html).

#### `horizon` in `vegcrew/planner.py`

```python
def horizon(season: Season) -> int
```

- **Contract.** Returns the season's length in weeks, months times WEEKS_PER_MONTH.
- **Modeling idea.** Weeks, not months, are the unit of time once a trim is a run of weeks.
- **Taught in** [14.1.3 A Trim Takes Weeks on One Crew: From MILP to CP-SAT Intervals](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-03/14.1.3-a-trim-takes-weeks-on-one-crew-from-milp-to-cp-sat-intervals.unit.html).

#### `trimmed` in `vegcrew/planner.py`

```python
def trimmed(self, cid: str) -> cp_model.LinearExprT
```

- **Contract.** A method of TrimModel, a mutable dataclass (`@dataclass`, not frozen) that holds the model and its variables: `model: cp_model.CpModel`, then three dicts keyed by (circuit id, crew id), each `field(default_factory=dict)`: `present` (the presence literals), `start` (the start weeks) and `work` (the optional intervals). `trimmed(cid)` returns the sum of the circuit's presence literals over the crews: 1 when the circuit is trimmed, 0 when it is not.
- **Modeling idea.** The sum of a circuit's presence literals plays the part the month model's sum of x over months played.
- **Taught in** [14.1.3 A Trim Takes Weeks on One Crew: From MILP to CP-SAT Intervals](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-03/14.1.3-a-trim-takes-weeks-on-one-crew-from-milp-to-cp-sat-intervals.unit.html).

#### `build` in `vegcrew/planner.py`

```python
def build(season: Season) -> TrimModel
```

- **Contract.** Takes a Season. Returns a TrimModel of a CP-SAT model: for each circuit that fits in the season and each crew, a presence literal, a start week from 0 to horizon minus the circuit's weeks, and an optional interval of the circuit's weeks; at most one crew per circuit; no two intervals of one crew overlapping; the trimmed circuits' cost within the budget; and their summed risk as the objective to maximize. A circuit longer than the season gets no interval. The expected report comes from this build order: for each circuit in the season's order that fits, and for each crew from K1 on, the presence literal `p_<cid>_<crew>`, the start `s_<cid>_<crew>` and the interval `w_<cid>_<crew>`, then that circuit's at-most-one; after every circuit, one no-overlap per crew from K1 on, the budget row, and the objective. The objective does not name the order of the work, so another build order can give another plan that is just as good; the tests accept it, the report check does not.
- **Modeling idea.** A trim is an optional interval on each crew, and a crew's intervals never overlap.
- **Taught in** [4.5.1 Interval Variables and `NoOverlap`](../../../../04-google-or-tools-in-depth/16-cpsat-scheduling/units/unit-01/4.5.1-interval-variables-and-nooverlap.unit.html).

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season) -> Plan
```

- **Contract.** Solves the model with CP-SAT, with max_time_in_seconds set to TIME_LIMIT and num_workers to WORKERS (module constants of planner.py: TIME_LIMIT = 10.0 seconds, WORKERS = 4), and returns a Plan with one Trim(cid, crew, start, end) per present interval, end being start plus the circuit's weeks, and the summed cost and risk removed. Any status but OPTIMAL or FEASIBLE is a Plan with the status alone. main.py sets planner.WORKERS = 1 before it plans, so that Run's search is the same every time: four workers race, and may return another of the tiny season's equally good plans.
- **Modeling idea.** Read the crew from the presence literal that is true and the weeks from that crew's start.
- **Taught in** [4.5.4 Scheduling Vegetation Crews Across Circuits](../../../../04-google-or-tools-in-depth/16-cpsat-scheduling/units/unit-04/4.5.4-scheduling-vegetation-crews-across-circuits.unit.html).

#### `format_plan` in `vegcrew/report.py`

```python
def format_plan(season: Season, plan: Plan) -> str
```

- **Contract.** The first line ends `, crews <crews>, weeks <horizon>` in place of the months. After the status line comes one line per crew from K1 on, in place of the month lines: two spaces, the crew id, one space, the week chart, two spaces, and the crew's trims in order of start, each as `<cid>:<first>-<last>` with both weeks included, separated by single spaces. The chart has one character per week of the season: `.` when the crew is free and the last character of the circuit id while it trims. The two spaces after the chart are printed even when the crew has no trims, so an idle crew's line ends in two spaces.
- **Modeling idea.** One letter per week shows at a glance that no crew works two circuits at once.
- **Taught in** [14.1.3 A Trim Takes Weeks on One Crew: From MILP to CP-SAT Intervals](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-03/14.1.3-a-trim-takes-weeks-on-one-crew-from-milp-to-cp-sat-intervals.unit.html).
