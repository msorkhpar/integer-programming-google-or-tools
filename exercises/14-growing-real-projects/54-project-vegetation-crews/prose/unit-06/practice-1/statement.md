With calendars in place, GridCap's vegetation planner started using the plan every week, and wrote:

> Sometimes I know something the model doesn't. A crew is already on site near C17, so start it there
> in week 0. The county closes the road to C17 until October, so leave it. A landowner complained, so
> trim C02 first. I need to tell the planner these things and have it plan *around* them.
> And when it can't, "INFEASIBLE" is not an answer. Last week I forced in five circuits after a storm
> and got an empty plan and that one word. Tell me *which* of my decisions clash, in my words, so I
> know what to give up.

You start from the calendar scheduler of the lesson before. Take the planner's overrides: pin a
trim to a crew and a first week, skip a circuit, or force one in, each with a reason. Refuse an
override that names nothing before any model is built. When a season has no plan, name a smallest
set of the planner's rules that clash (the musts, the budget and the overrides, never the physics of
crews and weeks) in the planner's words, and print them in the report. Split the model out of
`planner.py` into `model.py`, and the explanation into `explain.py`.

**The explanation.** Name the rules in the order they are made: each must as its circuit comes in
the season, then the budget, then the overrides in the order given. The tests compare the
explanation with an exact tuple in that order.

**The report.** After the crew lines, a plan with an explanation prints
`these rules cannot all hold; change one of them:` and one line per rule, two spaces, `- ` and the
rule's words. An INFEASIBLE plan has no trims: its status line reads
`status INFEASIBLE: 0 trims, cost $0k, risk carried $0k`, and each crew's line shows only its weeks
off.

**`main.py`.** After the tiny season's report it prints two more sections, each after an empty line.
First the title `skip C03:` and the report of the tiny season with one override,
`Override("skip", "C03", reason="road closed")`. Then the title
`pin C01 and C05 a week apart on K1:` and the report with two,
`Override("pin", "C01", crew="K1", start=12, reason="crew is nearby")` and
`Override("pin", "C05", crew="K1", start=13, reason="landowner asked")`, which cannot both hold.
Keep the line that sets `planner.WORKERS = 1`.

Run's report gains the two sections above, as `expected/report.txt` shows. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `vegcrew/model.py`

```python
def build(season: Season, overrides: tuple[Override, ...] = ()) -> TrimModel
```

- **Contract.** The model of the lesson before, moved to model.py with crew_ids, horizon and start_domain, and built with the overrides. Every rule a planner can change sits behind a named literal, with its words: `must_<cid>` (`<cid> is overdue and must be trimmed this season`), budget (`the season's budget is $<budget>k`, the budget written with a thousands comma, as f"{budget:,}" writes it: `$962k`, `$1,000k`) and `override_<i>` (`override <i>: ` followed by the override's own words, as Override.says gives them: `trim <cid> on <crew> from week <start> (<reason>)` for a pin, `leave <cid> for next season (<reason>)`, `trim <cid> this season (<reason>)`, with `no reason given` when the reason is empty). A skip leaves its circuit untrimmed; a pin or force trims it; a pin also fixes the crew and the first week it names. The rules are made in this order: each must as its circuit comes in the season's order, then the budget, then the overrides in the order given.
- **Modeling idea.** A rule behind a literal holds only when its literal is true, so the search can be asked which literals cannot all be true.
- **Taught in** [4.4.2 Native Logic: `AddBoolOr`, `AddImplication`, `OnlyEnforceIf`](../../../../04-google-or-tools-in-depth/15-cpsat-core/units/unit-02/4.4.2-native-logic-addboolor-addimplication-onlyenforceif.unit.html).

#### `holds` in `vegcrew/explain.py`

```python
def holds(tm: TrimModel, names: list[str]) -> bool
```

- **Contract.** Answers whether the named rules can all hold at once: clears the model's assumptions, adds the named rules' literals as assumptions, and solves with num_workers = 1 and stop_after_first_solution = True; True unless the status is INFEASIBLE.
- **Modeling idea.** Only yes or no matters, so the first plan found is enough.
- **Taught in** [4.6.2 Hints, Assumptions and `SufficientAssumptionsForInfeasibility`](../../../../04-google-or-tools-in-depth/17-cpsat-tuning-and-diagnostics/units/unit-02/4.6.2-hints-assumptions-and-sufficientassumptionsforinfeasibility.unit.html).

#### `conflict` in `vegcrew/explain.py`

```python
def conflict(tm: TrimModel) -> list[str]
```

- **Contract.** Returns a minimal list of rule names that cannot all hold, or [] when every rule can: the rules the solver names as sufficient for infeasibility (assumptions need one worker), then each dropped in turn and left out when the rest still cannot hold. The names come back in the order the rules were made, whatever order the solver named them in.
- **Modeling idea.** Assumptions name a set of rules that is enough for the proof; a deletion filter makes it minimal.
- **Taught in** [9.1.5 CP-SAT Assumptions as a Conflict Finder](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-05/9.1.5-cp-sat-assumptions-as-a-conflict-finder.unit.html).

#### `why_infeasible` in `vegcrew/explain.py`

```python
def why_infeasible(season: Season, overrides: tuple[Override, ...] = ()) -> list[str]
```

- **Contract.** Builds the model of the season and its overrides and returns the words (TrimModel.says) of the rules in its conflict, in the conflict's order. The tests compare the explanation with an exact tuple in that order: musts, then the budget, then the overrides.
- **Modeling idea.** A conflict is only useful in the words of the people who can change it.
- **Taught in** [9.1.6 Turning an IIS Into a Planner Message](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-06/9.1.6-turning-an-iis-into-a-planner-message.unit.html).

#### `check_overrides` in `vegcrew/planner.py`

```python
def check_overrides(season: Season, overrides: tuple[Override, ...]) -> list[str]
```

- **Contract.** Returns what is wrong with the overrides as data, in order: `override <i>: unknown kind <kind repr>` unless the kind is pin, skip or force; `override <i>: no circuit <cid>`; `override <i>: no crew <crew>`; `override <i>: week <start> is outside the season`. Empty when nothing is.
- **Modeling idea.** An override that names nothing is refused before any model is built.
- **Taught in** [12.1.2 Manual Overrides as Bounds, With an Audit Trail](../../../../12-engineering-the-optimization-service/45-scenario-workflow/units/unit-02/12.1.2-manual-overrides-as-bounds-with-an-audit-trail.unit.html).

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season, overrides: tuple[Override, ...] = ()) -> Plan
```

- **Contract.** Raises ValueError with the problems joined by `; ` when check_overrides finds any; otherwise solves with every rule's literal true, and when the season is INFEASIBLE returns a Plan whose explanation is why_infeasible's words.
- **Modeling idea.** A failed plan says which of the planner's rules clash, not just that it failed.
- **Taught in** [14.1.6 Planner Overrides and Why a Plan Failed](../../../../14-growing-real-projects/54-project-vegetation-crews/units/unit-06/14.1.6-planner-overrides-and-why-a-plan-failed.unit.html).

#### `format_plan` in `vegcrew/report.py`

```python
def format_plan(season: Season, plan: Plan) -> str
```

- **Contract.** After the crews, when the plan has an explanation, the line `these rules cannot all hold; change one of them:` and one line `  - <words>` per rule, in the explanation's order. An INFEASIBLE plan has no trims, so its status line reads `0 trims, cost $0k, risk carried $0k` and each crew's line shows only its weeks off, ending in two spaces.
- **Modeling idea.** The explanation is part of the answer, so the report prints it.
- **Taught in** [9.1.6 Turning an IIS Into a Planner Message](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-06/9.1.6-turning-an-iis-into-a-planner-message.unit.html).
