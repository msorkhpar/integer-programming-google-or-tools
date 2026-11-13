The planners checked the step-02 plan against their own lists and wrote back:

> Three must-do projects are missing: P010, P017 and P039 are regulatory commitments, so they go in
> whatever they're worth. P030 and P031 are two ways to fix the same Valley line, and you funded
> both. Also, P023 can only start a year after P022 has started, P016 needs P015, and P011 and P012
> are one Coast crew visit: both or neither. The export has all of this in its columns.

You start from the yearly planner of the lesson before. Make it keep the rules the export already
holds: a must-do project is funded, at most one project of an alternative group is funded, a bundle
is funded whole or not at all, and a child starts no earlier than its parent's start plus the lag.
Give each rule its own function in a new file, `cipt/rules.py`, that adds its rows under names the
planners can read, and let the model run the rules in turn. An export in which a project names a
parent the export does not have is refused when it is read.

`cipt/rules.py` starts as the reference has it, with the five rule functions of the blueprint
stubbed. Its imports are there (`Built` is imported inside `if TYPE_CHECKING:`, because `model.py`
imports `RULES` from `rules.py` and a plain import back would be circular), and so is `RULES`, the
tuple of rule functions `build` runs in order. `cipt/value.py` is the next lesson's stub, as the
reference has it; no code of this step imports it, so leave it as it is.

The expected report is one of several tied best plans. To print that one, create the start
variables project by project in export order, each project's start years in ascending order, and
run the rules in the order `once_or_must`, `alternatives`, `bundles`, `parents`, `budgets`. The
report's format is the one of the lesson before, unchanged.

Run executes `main.py`, which plans the demo export and prints the report; `expected/report.txt` is
the report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `once_or_must` in `cipt/rules.py`

```python
def once_or_must(built: Built) -> None
```

- **Contract.** Adds a row `once_<id>` (the project starts at most once) for each discretionary project, and a row `must_<id>` (it starts exactly once) for each must-do project.
- **Modeling idea.** A must-do is the at-most-once row turned into an equality: the same sum of start variables, fixed to 1.
- **Taught in** [6.5.1 Must-Do vs. Discretionary Planning Groups](../../../../06-formulation-craft/27-dependencies-and-groups/units/unit-01/6.5.1-must-do-vs-discretionary-planning-groups.unit.html).

#### `alternatives` in `cipt/rules.py`

```python
def alternatives(built: Built) -> None
```

- **Contract.** Adds a row `alt_<group>` per alternative group: the projects of the group start at most once between them.
- **Modeling idea.** Mutually exclusive choices are one at-most-one row over their start variables.
- **Taught in** [6.5.3 Mutually Exclusive Alternatives (Repair vs. Replace)](../../../../06-formulation-craft/27-dependencies-and-groups/units/unit-03/6.5.3-mutually-exclusive-alternatives-repair-vs-replace.unit.html).

#### `bundles` in `cipt/rules.py`

```python
def bundles(built: Built) -> None
```

- **Contract.** Adds a row `bundle_<first>_<other>` for each further member of a bundle: that member is funded exactly when the bundle's first member, in id order, is.
- **Modeling idea.** All-or-nothing is an equality between the funded indicators, chained to one member.
- **Taught in** [6.5.2 Parent-Child Bundles and All-or-Nothing](../../../../06-formulation-craft/27-dependencies-and-groups/units/unit-02/6.5.2-parent-child-bundles-and-all-or-nothing.unit.html).

#### `parents` in `cipt/rules.py`

```python
def parents(built: Built) -> None
```

- **Contract.** Adds a row `after_<child>_<t>` for each start year t of a child: the child started by t needs its parent started by t minus the lag.
- **Modeling idea.** Precedence with a lag compares cumulative starts: started by t on the child, started by t - lag on the parent.
- **Taught in** [6.5.4 Precedence with Lags](../../../../06-formulation-craft/27-dependencies-and-groups/units/unit-04/6.5.4-precedence-with-lags.unit.html).

#### `budgets` in `cipt/rules.py`

```python
def budgets(built: Built) -> None
```

- **Contract.** Adds a row `budget_<y>` per plan year: that year's spend, costs spread over the years of work, within that year's budget.
- **Modeling idea.** The yearly budget of the lesson before is one more rule, written the way the others are.
- **Taught in** [6.4.2 Cash-Flow Spreading Across Years](../../../../06-formulation-craft/26-multi-period-timing/units/unit-02/6.4.2-cash-flow-spreading-across-years.unit.html).

#### `build` in `cipt/model.py`

```python
def build(request: Request) -> Built
```

- **Contract.** Creates the start variables, keeps the Built that owns them and the named rows, runs every rule of rules.RULES on it in order, and sets the objective. Every row has the name its rule gave it.
- **Modeling idea.** Each rule is a function that adds rows with the names it owns, so a new rule never changes build.
- **Taught in** [14.2.3 Business Rules: Must-Dos, Bundles, Parents and Alternatives](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-03/14.2.3-business-rules-must-dos-bundles-parents-and-alternatives.unit.html).

#### `load_request` in `cipt/data.py`

```python
def load_request(raw: dict) -> Request
```

- **Contract.** Also reads must_do, parent, parent_lag, alt_group and bundle for each project, and refuses an export in which a project names a parent the export does not have (ValueError, 'unknown parent').
- **Modeling idea.** Validate the input before the solve: a rule that points at nothing is an error in the data, not a constraint.
- **Taught in** [9.1.2 Validating Inputs Before the Solve](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-02/9.1.2-validating-inputs-before-the-solve.unit.html).
