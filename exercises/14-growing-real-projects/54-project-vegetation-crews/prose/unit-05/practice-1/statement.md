The risk-ordered schedule went to the field, and three answers came back the same day:

> **Crew supervisor:** The River circuits run through bottom land. Until the ground dries, around week
> 8, we can't get bucket trucks in. And K1 is at training in weeks 10 and 11; K2 is held back for storm
> duty in weeks 14 to 17.
>
> **Environmental lead:** About half of the Hills circuits cross nesting habitat. No work there from
> week 6 to week 13.
>
> **Compliance:** C05 and C16 are overdue on their trim cycle. They are not optional this year.

The supervisor speaks of the small season's two crews. The generator gives K1 the training weeks
10 and 11 in every season and, when a season has more than one crew, gives its last crew the storm
duty in weeks 14 to 17: K2 in the small season, K6 in the medium; the tiny season's one crew has
only the training weeks.

You start from the risk-ordered scheduler of the lesson before. Read three calendars, and have the
generator draw them: each circuit's access windows, each crew's weeks off, and the circuits that
must be trimmed this season. A trim lies wholly inside one window of its circuit, never across the
closed weeks between two; a circuit whose windows are all too short for its trim waits for next
season; no crew works in its weeks off; every must circuit is trimmed, and a season whose musts
cannot all be trimmed is infeasible. The report marks each crew's weeks off.

**The report.** Each crew's week chart marks the crew's weeks off with `x` (a trim never covers
one); the rest of every line is as before.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `spans` in `vegcrew/data.py`

```python
def spans(raw: list) -> Weeks
```

- **Contract.** Turns a list of [first, last] pairs into a tuple of (first, last) int pairs, both weeks included.
- **Modeling idea.** A calendar is data: spans of weeks, read once and kept immutable.
- **Taught in** [14.1.5 Weather and Access Windows: Calendars and Optional Work](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-05/14.1.5-weather-and-access-windows-calendars-and-optional-work.unit.html).

#### `season_from_dict` in `vegcrew/data.py`

```python
def season_from_dict(raw: dict) -> Season
```

- **Contract.** Also reads each circuit's windows (none: the whole season) and must flag (none: optional), and the season's crew_off, crew id to spans of weeks off (none: every crew works every week). Circuit gains `windows` and `must`, after `growth`; Season gains `crew_off: dict[str, Weeks]` between `months` and `circuits`, so a Season is built as Season(name, budget, crews, months, crew_off, circuits). Weeks is tuple[tuple[int, int], ...], a module-level alias in data.py.
- **Modeling idea.** A missing calendar column means no calendar, so older exports still load.
- **Taught in** [14.1.5 Weather and Access Windows: Calendars and Optional Work](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-05/14.1.5-weather-and-access-windows-calendars-and-optional-work.unit.html).

#### `scenario` in `vegcrew/generate.py`

```python
def scenario(size: str = "small", seed: int = 54) -> dict
```

- **Contract.** Also, from its own stream named 'access', one circuit at a time in order: must when a draw of random() is below 0.15; then a River circuit has the window [8, last week], a Hills circuit has the windows [0, 5] and [14, last week] when a second draw is below 0.5, and every other circuit no windows. The season's crew_off gives K1 the weeks [10, 11] and, with more than one crew, the last crew (K2 in the small season, K6 in the medium) the weeks [14, 17]. The season's dict holds `crew_off` between `months` and `circuits`.
- **Modeling idea.** A column drawn from its own stream leaves the values of every earlier column as they were.
- **Taught in** [14.1.5 Weather and Access Windows: Calendars and Optional Work](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-05/14.1.5-weather-and-access-windows-calendars-and-optional-work.unit.html).

#### `start_domain` in `vegcrew/planner.py`

```python
def start_domain(c: Circuit, h: int) -> cp_model.Domain
```

- **Contract.** Returns every first week that keeps a trim of the circuit's weeks inside one of its windows (the whole season when it has none) and inside the season: one interval per window long enough, and an empty domain when none is.
- **Modeling idea.** An access window is a domain on the start, one interval per window, so a trim never runs across a closed week.
- **Taught in** [4.5.2 Cumulative Resources: Crews and Outage Windows](../../../../04-google-or-tools-in-depth/16-cpsat-scheduling/units/unit-02/4.5.2-cumulative-resources-crews-and-outage-windows.unit.html).

#### `build` in `vegcrew/planner.py`

```python
def build(season: Season) -> TrimModel
```

- **Contract.** As before, with each start taking its values from start_domain, no crew options for a circuit whose domain is empty, each crew's weeks off as fixed intervals in that crew's no-overlap, and every must circuit trimmed.
- **Modeling idea.** A crew's weeks off are fixed intervals its trims may not overlap.
- **Taught in** [4.5.1 Interval Variables and `NoOverlap`](../../../../04-google-or-tools-in-depth/16-cpsat-scheduling/units/unit-01/4.5.1-interval-variables-and-nooverlap.unit.html).

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season) -> Plan
```

- **Contract.** As before, keeping every calendar; when the must circuits cannot all be trimmed, a Plan with the status INFEASIBLE and no trims. (The reference also takes an `overrides` argument that it ignores, typed with a stub Override dataclass in data.py, ready for the next lesson; this step's tests do not use it.)
- **Modeling idea.** A must is a hard rule, so a season that cannot keep it has no plan.
- **Taught in** [14.1.5 Weather and Access Windows: Calendars and Optional Work](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-05/14.1.5-weather-and-access-windows-calendars-and-optional-work.unit.html).

#### `format_plan` in `vegcrew/report.py`

```python
def format_plan(season: Season, plan: Plan) -> str
```

- **Contract.** Each crew's week chart also shows its weeks off, as 'x'; a trim never covers one, and the rest of the line is as before.
- **Modeling idea.** The report shows the calendar the plan was made to keep.
- **Taught in** [14.1.5 Weather and Access Windows: Calendars and Optional Work](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-05/14.1.5-weather-and-access-windows-calendars-and-optional-work.unit.html).
