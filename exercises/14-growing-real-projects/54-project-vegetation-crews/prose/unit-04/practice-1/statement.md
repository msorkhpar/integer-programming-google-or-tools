The crew schedule reached GridCap's reliability engineer:

> Your plan trims C13 in the first five weeks and leaves C12 for weeks 17 to 23. C12 is the one I
> worry about: its trees are growing into the lines, and every week we wait its risk goes up. A
> trim in September does not take out a year of risk; it takes out what is left of the year, and the
> circuit carried the rest. Order the work so that we carry the least risk over the season. And
> a circuit we skip waits half a year more for next season's crews; count that too.

You start from the crew scheduler of the lesson before. Read each circuit's weekly growth of risk,
and have the generator draw it. A circuit carries its weekly share of its yearly risk, plus its
growth for every week it has waited, until its trim ends; a circuit left for next season carries it
until 26 weeks past the season's end. Plan the least risk carried in total, within the budget and
the crews, and report it. A trim that fills the whole season still fits.

**The report.** Only the status line changes: it ends `risk carried $<risk carried>k`, with a
thousands comma, in place of `risk removed $<risk removed>k a year`. `main.py` still sets one worker.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `vegcrew/planner.py`

```python
def build(season: Season) -> TrimModel
```

- **Contract.** As before, and also: per circuit a literal `t_<cid>` (one crew or none) and an end week, from the circuit's weeks to the horizon when trimmed (start plus weeks on its crew) and horizon + DEFER_WEEKS when it waits for next season; the risk it carries is Circuit.carried(end), looked up in a table indexed by the end week; the objective is the summed risk carried, to minimize. Circuit.carried(end) is round(risk / 52 * end + growth * end * (end - 1) / 2). TrimModel loses its trimmed method and gains three dicts keyed by circuit id: `trimmed` (the literals t), `end` (the end weeks) and `carried` (the risk each carries), declared after `model`, `trimmed` first and `end` and `carried` after `work`. A circuit longer than the season gets no crew options; the reference still writes its end domain as Domain.from_intervals([[weeks, horizon], [horizon + DEFER_WEEKS, horizon + DEFER_WEEKS]]), and from_intervals drops the empty first piece, so the end can only be horizon + DEFER_WEEKS.
- **Modeling idea.** Risk carried is a table indexed by the week a trim ends, and an element constraint reads it.
- **Taught in** [4.5.3 Element, Table and Allowed-Assignment Constraints](../../../../04-google-or-tools-in-depth/16-cpsat-scheduling/units/unit-03/4.5.3-element-table-and-allowed-assignment-constraints.unit.html).

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season) -> Plan
```

- **Contract.** As before, and the Plan's risk_carried is the objective value, rounded.
- **Modeling idea.** Once order matters, the objective is a sum over time, and a better plan may take longer to prove.
- **Taught in** [4.5.4 Scheduling Vegetation Crews Across Circuits](../../../../04-google-or-tools-in-depth/16-cpsat-scheduling/units/unit-04/4.5.4-scheduling-vegetation-crews-across-circuits.unit.html).

#### `season_from_dict` in `vegcrew/data.py`

```python
def season_from_dict(raw: dict) -> Season
```

- **Contract.** Also reads each circuit's growth ($k a week by which its weekly risk grows).
- **Modeling idea.** Read the columns the model needs now, and only those.
- **Taught in** [14.1.4 Risk Grows While a Circuit Waits: The Objective Changes](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-04/14.1.4-risk-grows-while-a-circuit-waits-the-objective-changes.unit.html).

#### `scenario` in `vegcrew/generate.py`

```python
def scenario(size: str = "small", seed: int = 54) -> dict
```

- **Contract.** Also gives each circuit its growth, round(risk / 52 * u, 2) with u drawn by uniform(0.02, 0.10) from its own stream named 'growth', one draw per circuit in order after the weeks.
- **Modeling idea.** A column drawn from its own stream leaves the values of every earlier column as they were.
- **Taught in** [14.1.4 Risk Grows While a Circuit Waits: The Objective Changes](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-04/14.1.4-risk-grows-while-a-circuit-waits-the-objective-changes.unit.html).

#### `format_plan` in `vegcrew/report.py`

```python
def format_plan(season: Season, plan: Plan) -> str
```

- **Contract.** The status line ends `risk carried $<risk_carried>k` instead of the risk removed a year.
- **Modeling idea.** The report states the number the plan is chosen by.
- **Taught in** [14.1.4 Risk Grows While a Circuit Waits: The Objective Changes](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-04/14.1.4-risk-grows-while-a-circuit-waits-the-objective-changes.unit.html).
