# 12.1.1 Scenarios as Data: Create, Copy, Optimize

GridCap's planners have been answering what-if questions from a notebook. They load the small
portfolio, change a budget in a dictionary, rerun the model, and paste the NPV into a spreadsheet.
Finance asks what happens if 2030 gets $860k less, $7,750k instead of $8,610k. Someone edits the
dictionary, reruns, and a week later nobody can say which pasted NPV belongs to which budget, or
whether the base plan on the projector was solved before or after the edit.

Lesson 7.1.3 described the cure in words: a scenario is a copy with its own snapshot, never an edit
of another scenario. This lesson writes it as code a service can rely on. A scenario becomes a plain
record of inputs. A copy shares nothing that can change with its parent. The record survives a trip
through JSON, so it can be stored and sent over a network. And optimizing a scenario is a function
that builds the model from the record and stamps the result with the inputs it used.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real. The
people in the examples (`planner-a`, `planner-b`, ...) are placeholders.

## The Model

Every scenario in this module builds the same model from its own data; only the parameters and the
bounds differ. It is the multi-period model of lessons 6.4.1 to 6.4.3 with the must-do, alternative
and parent rules of lessons 6.5.1 to 6.5.3, built by `plan_model.build`.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use (its window); $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative
groups, each a set of projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag
$`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k), **taken from the scenario**; $`l_{i,t}, u_{i,t}`$, the
bounds of each start variable, $`0`$ and $`1`$ unless an override changes them (lesson 12.1.2).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$, with
$`l_{i,t} \le x_{i,t} \le u_{i,t}`$: project $`i`$ starts in year $`t`$. We write
$`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ and
$`\text{by}(i, t) = \sum_{s \in T_i,\, s \le t} x_{i,s}`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\text{by}(c, t) &\le \text{by}(p(c),\, t - L_c) && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

| Label | Row name in `plan_model.py` |
| --- | --- |
| once$`_i`$, must$`_i`$ | `once_P001`, `must_P017` |
| alt$`_g`$ | `alt_G030` |
| after$`_{c,t}`$ | `after_P023_2029` |
| budget$`_y`$ | `budget_2030` |

The finance question changes one parameter, $`B_{2030}`$, from 8,610 to 7,750. Nothing in the
formulation changes, which is the point of this lesson: a scenario is data poured into a fixed model.

## A Scenario Is a Record of Inputs, Kept Apart From the Model

A **scenario** is one named set of planning inputs (lesson 7.1.3). In code it is a plain record, a
Python dataclass with no solver object inside it. `scenario_record.py` creates GridCap's base
scenario and prints what the record holds:

```text
record keys: ['budget', 'created_at', 'created_by', 'data', 'name', 'overrides', 'parent_id', 'scenario_id', 'settings']
inputs keys: ['budget', 'data', 'overrides', 'settings']
budget: {'2027': 8890, '2028': 8120, '2029': 8760, '2030': 8610, '2031': 7850}
```

The record has two kinds of field, and the difference matters for everything that follows:

- **Inputs** are what the model is built from: `data` (which portfolio), `budget`, `overrides`
  (empty until lesson 12.1.2) and `settings` (the solver and its gap tolerance).
- **Metadata** says who made the scenario, when, under what name, and which scenario it was copied
  from: `scenario_id`, `name`, `created_by`, `created_at`, `parent_id`.

The portfolio itself is not copied into the record. `data` names it by size and seed, which is
enough to regenerate it, and stores its content hash (GridCap's `Portfolio.content_hash()`, the
sha256 of its canonical JSON) as proof of which data was meant. Forty projects with their cost
profiles and NPVs would make every scenario large, and every copy would duplicate them. Lesson 12.2.3
turns this reference into versioned snapshots of the input data.

Why keep the model out of the record? A MathOpt model is built for one solve: it holds solver-ready
variables and rows, it cannot be written to JSON, and it is not something two planners can share.
The OR-Tools MathOpt overview stresses that a MathOpt model is defined independently of any
solver; this lesson goes one step further and keeps the model out of the stored data altogether.
The record is small, readable and storable; the model is rebuilt from it on every run.

## The Snapshot Covers the Inputs, and Nothing About Who or When

Lesson 7.1.3 introduced the **snapshot**, the sha256 hash of a scenario's inputs written in one
canonical form. Here it is computed from `inputs()` only:

```python
    def inputs(self) -> dict:
        """Everything the model is built from, and nothing else, in a JSON-ready form."""
        return {"data": {"size": self.data.size, "seed": self.data.seed, "hash": self.data.content_hash},
                "budget": {str(y): v for y, v in sorted(self.budget.items())},
                "overrides": [[o.project, o.kind, o.year] for _, o in sorted(self.overrides.items())],
                "settings": dict(sorted(self.settings.items()))}

    def snapshot(self) -> str:
        """sha256 of the canonical inputs (lesson 7.1.3): equal inputs, equal id."""
        text = json.dumps(self.inputs(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

`sort_keys=True` and the compact separators `(",", ":")` make one text for one set of inputs,
whatever order the dictionaries were filled in; Python's `json` documentation names those
separators as the most compact form. The program renames the scenario, then changes one budget by
$1k:

```text
snapshot: b752239b45c2
renamed, same snapshot: True
budget 2030 less $1k, same snapshot: False
```

Renaming the scenario and changing who made it leave the snapshot alone, because neither changes
the model. A $1k change to one budget gives another snapshot, because it changes a row. That split
is what lets a service answer "were these two runs solved on the same inputs?" by comparing two
strings, and answer it correctly even when the two scenarios have different names or owners.

The data reference is checked too. A scenario whose data no longer matches its hash is refused
before any model is built:

```python
def load_portfolio(ref: DataRef) -> Portfolio:
    """Regenerate the portfolio a scenario names, and refuse it if it is not the same data."""
    portfolio = generate(ref.size, ref.seed)
    if portfolio.content_hash() != ref.content_hash:
        raise ValueError(f"portfolio {ref.size}/{ref.seed} does not match the hash the scenario recorded")
    return portfolio
```

```text
refused: portfolio small/2028 does not match the hash the scenario recorded
```

The program asked for seed 2028 while the recorded hash belongs to the default seed, 2027, so the
regenerated portfolio is different data. Building a model from it would silently plan a different
utility under the old scenario's name.

<!-- practice 1 -->

## A Copy Shares Nothing Mutable With Its Parent

Finance's question needs a second scenario that starts from the base's inputs. The tempting copy is
`copy.copy`. It is a **shallow copy**: a new object whose fields point at the *same* inner objects
as the original, as Python's `copy` documentation puts it. `copy_pitfall.py` makes one and cuts the
2030 budget:

```python
shallow = copy.copy(base)
shallow.scenario_id, shallow.name = "S-002", "cut-2030"
shallow.budget[2030] = 7750
```

```text
shallow copy: base budget 2030 is now 7750 | base snapshot changed: True
  same dict object: True
```

The copy and the base share one budget dictionary, so the edit to the copy changed the base. Its
snapshot moved with it, and any result solved earlier from the base no longer matches the base's
inputs. Nothing raised an error. This is the notebook's bug from the opening, moved into code.

A copy must give the new scenario its own containers. `copy_scenario` builds a new record with a new
dictionary for every field that can change, and a link back to the parent:

```python
def copy_scenario(s: Scenario, scenario_id: str, name: str, by: str, at: str) -> Scenario:
    """A new scenario with the same inputs as `s`, its own containers, and a link back to `s`."""
    return Scenario(scenario_id, name, s.data, budget=dict(s.budget), settings=dict(s.settings),
                    overrides=dict(s.overrides), parent_id=s.scenario_id, created_by=by, created_at=at)
```

```text
copy_scenario: parent S-001 | same snapshot as base: True
  after the edit: base budget 2030 8610 | cut 7750 | base snapshot changed: False
```

Three things to read in that output. The copy starts with the base's snapshot, because its inputs
are equal. Editing the copy leaves the base's budget and snapshot untouched. And `parent_id`
records where the copy came from, so a reviewer can always trace a scenario back to the one it was
made from.

`dict(s.budget)` copies one level, which is enough here because the values inside are integers and
`Override` records (lesson 12.1.2) are frozen dataclasses, which nobody can change in place. `data`
is shared on purpose: `DataRef` is frozen too, and both scenarios mean the same portfolio. A record
with nested mutable values would need `copy.deepcopy`, which copies every level.

<!-- practice 2 -->

## A Scenario Survives a Round Trip Through JSON

A scenario that only lives in one Python process cannot be stored in a database (lesson 12.1.4) or
sent to an API (lesson 12.4.1). `to_json` writes the whole record, inputs and metadata, as canonical JSON,
and `from_json` reads it back. JSON has one trap for this record. Its object keys are always strings
(Python's `json` documentation says every key is converted to a string), so the years come back as
`'2027'`, not `2027`:

```text
json.loads keys: ['2027', '2028']  2030 in it: False
round trip equal: True  same snapshot: True
```

A model builder that looked up `budget[2030]` in the raw JSON would raise `KeyError`, or worse, find
nothing and use a default. `from_json` turns the keys back into integers and the override lists back
into `Override` records, and the test that matters is the last line: the record read back equals the
record written, and so does its snapshot. If a field were lost or retyped on the way, one of the two
would be `False`.

## Optimize Builds the Model From the Scenario and Stamps the Result With Its Snapshot

`optimize` takes a scenario and returns a `Result`. It regenerates and checks the portfolio, turns
the overrides into bounds, builds the model, solves it with HiGHS through MathOpt, and reads the
plan only when the solve is optimal, as the OR-Tools MathOpt samples check the termination reason
before reading a solution:

```python
def optimize(s: Scenario) -> Result:
    """Build the scenario's model from its data alone, solve it, and stamp the result with the snapshot."""
    portfolio = load_portfolio(s.data)
    bounds = {}
    for o in s.overrides.values():
        bounds.update(bounds_of(o, portfolio.project(o.project)))
    built = build(portfolio, s.budget, bounds)
    result = solve_highs(built.model, s.settings["relative_gap_tolerance"])
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return Result(s.scenario_id, s.snapshot(), status, None, {})
    starts = {pid: t for (pid, t), v in built.x.items() if result.variable_values(v) > 0.5}
    return Result(s.scenario_id, s.snapshot(), status, round(result.objective_value()), dict(sorted(starts.items())))
```

The function reads nothing but its argument: no global budget, no model left over from an earlier
run. That is what makes a rerun meaningful. `optimize_scenarios.py` runs the base and the copy, then
the base again:

```text
S-001 OPTIMAL NPV $24,260k funded 27 snapshot b752239b45c2
S-002 OPTIMAL NPV $23,887k funded 27 snapshot 7c5ffb94a1c8
base -> cut-2030: {'selected': ['P006'], 'deferred': ['P016'], 'shifted': ['P018 2030->2031']}
base again: same plan True | same NPV True
```

The answer to finance: the $860k cut costs $373k of NPV ($24,260k less $23,887k). The plan drops the
Coast line job P016, which spends $310k and $950k in its two years of work, funds the small Valley
trim P006 instead, and moves P018 a year later. The diff line uses the three lists of lesson 9.3.3:
projects the new plan selects, defers, or shifts to
another year. The rerun of the base gave the same plan, on this machine and these versions; lessons
10.2.1 and 10.2.2 say when reruns repeat and when they need more than equal inputs.

Each `Result` carries the snapshot of the inputs it was solved on. That stamp is how a service
knows whether a result still describes its scenario:

```python
def current(r, s) -> bool:
    """A result describes the scenario only while the scenario still has the inputs it was solved with."""
    return r.snapshot == s.snapshot()


cut.budget[2031] = 7000
print("cut-2030 edited after its run; result current:", current(runs["S-002"], cut))
```

```text
cut-2030 edited after its run; result current: False
```

Someone changed the copy's 2031 budget after its run. The stored result still says $23,887k, but it
answers a question nobody is asking any more. A service that compares the two snapshots shows the
result as stale and asks for a rerun; one that does not compare them puts an old NPV beside new
budgets, which is the projector mix-up from the opening. Lesson 12.1.3 turns this check into a rule
the planning cycle enforces.

## Summary

- **A scenario is a record of inputs, kept apart from the model.** Inputs (data, budgets,
  overrides, settings) build the model; metadata (id, name, who, when, parent) does not.
- **The snapshot covers the inputs, and nothing about who or when.** Equal inputs give equal
  snapshots whatever the name; a $1k change gives another one. The data is named by its hash and
  refused if it no longer matches.
- **A copy shares nothing mutable with its parent.** A shallow copy shares the budget dictionary,
  so editing the copy edits the base; `copy_scenario` gives the copy its own containers and a
  `parent_id`.
- **A scenario survives a round trip through JSON.** JSON keys are strings, so the years must be
  turned back into integers; the record read back equals the record written.
- **Optimize builds the model from the scenario and stamps the result with its snapshot.** A
  result is current only while its snapshot equals its scenario's.

## Reference

| Field | Kind | In the snapshot |
| --- | --- | --- |
| `data` (size, seed, content hash) | input | yes |
| `budget` | input | yes |
| `overrides` | input | yes (project, kind, year) |
| `settings` | input | yes |
| `scenario_id`, `name`, `parent_id` | metadata | no |
| `created_by`, `created_at` | metadata | no |

| Function | Does |
| --- | --- |
| `create(portfolio, size, id, name, by, at)` | a scenario on GridCap's own budgets, no overrides |
| `copy_scenario(s, id, name, by, at)` | equal inputs, own containers, `parent_id = s.scenario_id` |
| `Scenario.to_json()` / `from_json(text)` | the whole record as canonical JSON, and back |
| `load_portfolio(ref)` | regenerate the data and refuse it if the hash differs |
| `optimize(s)` | build, solve, and return a `Result` stamped with `s.snapshot()` |
| `current(r, s)` | `r.snapshot == s.snapshot()` |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt)
(models are defined independently of any solver, which is what lets a scenario rebuild its model on
every run); the OR-Tools MathOpt sample
[`time_indexed_scheduling.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py)
(checks the termination reason before reading a solution, as `optimize` does); Python's
[`copy` module](https://docs.python.org/3/library/copy.html) (shallow and deep copies); Python's
[`json` module](https://docs.python.org/3/library/json.html) (keys always become strings;
`sort_keys` and the compact separators).

## Challenges

1. Add a `description` field to `Scenario`. Should it go into `inputs()`? Predict what a planner
   would see if it did.
2. Copy the cut scenario and set 2030 back to $8,610k. Predict its snapshot before you print it,
   and say why it is or is not the base's.
3. `optimize` rounds the objective to whole $k. What would `current` do if the snapshot were taken
   after the solve instead of before?

## Design Note: Ids and Clocks Come From Outside

Every function here takes the scenario id and the time as arguments instead of calling `uuid4()`
or `datetime.now()` itself. The programs pass fixed values (`S-001`, a `Clock` that steps five
minutes), so they print the same output on every run and their tests can check it. In a service the
id comes from the database (lesson 12.1.4) and the time from the server's clock in UTC, but the
functions do not change: whoever calls them decides where ids and times come from.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**scenario_record.py.** Creates the base scenario, prints its record and snapshot, shows which
changes move the snapshot, refuses a portfolio that does not match its hash, and makes the JSON
round trip (*A Scenario Is a Record of Inputs*, *The Snapshot Covers the Inputs*, *A Scenario
Survives a Round Trip*). *Try:* change the scenario's `settings` gap tolerance to 0.01 and predict
whether the snapshot changes.

- Program: [scenario_record.py](src/scenario_record.py)

**copy_pitfall.py.** The shallow copy that edits its parent, then `copy_scenario` (*A Copy Shares
Nothing Mutable*). *Try:* replace `copy.copy` with `copy.deepcopy` and predict both output lines.

- Program: [copy_pitfall.py](src/copy_pitfall.py)

**optimize_scenarios.py.** Optimizes the base and the 2030 cut, diffs them, reruns the base, and
detects a stale result (*Optimize Builds the Model From the Scenario*). *Try:* cut 2031 instead of
2030 by the same $860k and predict whether the cost in NPV is larger or smaller.

- Program: [optimize_scenarios.py](src/optimize_scenarios.py)

**scenario.py.** The `Scenario` record, its snapshot, `create`, `copy_scenario`, `optimize` and
`diff_plans`. It prints nothing itself.

- Library: [scenario.py](src/scenario.py)

**plan_model.py.** The model of *The Model* above, and the HiGHS solve.

- Library: [plan_model.py](src/plan_model.py)
