Two messages arrived the same week. From finance, after trying a budget cut:

> We cut 2030 and 2031 to $4M each and the planner just said "infeasible". Infeasible why? Which of
> our numbers is the problem?

And from a regional manager:

> P030 is our biggest Valley project and it's not funded. Why not? What would it take?

You start from the planner of the lesson before, whose rows all carry names. When a request has no
plan, name exactly the rules that clash, in the planners' words, so that dropping or changing any
one of them gives a plan; a rule that plays no part in the clash is not named. When a project is
left out, say what funding it would cost (the NPV given up and the projects dropped) or, when no
plan can fund it, which rules block it. The command line explains an infeasible request, and
`--why PROJECT` explains a project the plan leaves out.

`--why` for a project the plan funds prints nothing after the report; for an infeasible request
the command line prints the conflict, does not answer `--why`, and returns 1.

Run's report gains a section: `main.py` now asks why P003 was left out of the demo plan, as
`--why P003` does. After the report it prints `P003 cannot be funded. ` and the conflict message on
the same line; the message's first line is
`No plan meets these <n> rules together; drop or change any one of them:` and each next line is
`  <row>: <description>` (two spaces first), one per row of the conflict in name order. The
frontier section of the lesson before follows, unchanged.

`cipt/scenario.py` and `cipt/store.py` are the next lesson's stubs, as the reference has them; no
code of this step imports them, so leave them as they are. Submit runs every test in `tests/`, the
earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `deletion_filter` in `cipt/diagnose.py`

```python
def deletion_filter(built: Built, keep: tuple[str, ...] = ()) -> list[str]
```

- **Contract.** Returns, sorted, the names of an irreducible set of rows that cannot all hold: relax each row in name order, keep it relaxed while the model stays infeasible, restore it when relaxing it makes the model feasible. Rows named in keep are never relaxed.
- **Modeling idea.** The deletion filter: the rows you cannot relax without the clash disappearing form a conflict, and dropping any one of them gives a plan.
- **Taught in** [9.1.3 IIS With MathOpt, gurobipy and Pyomo](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-03/9.1.3-iis-with-mathopt-gurobipy-and-pyomo.unit.html).

#### `feasible` in `cipt/diagnose.py`

```python
def feasible(built: Built) -> bool
```

- **Contract.** True unless HiGHS reports the model infeasible: only the termination INFEASIBLE counts as no plan, and INFEASIBLE_OR_UNBOUNDED counts as feasible (every variable is binary, so the model is never unbounded).
- **Modeling idea.** The filter only asks one question of each solve: does a plan exist?
- **Taught in** [9.1.1 Infeasible, Unbounded, or the Solver Can't Tell](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-01/9.1.1-infeasible-unbounded-or-the-solver-cant-tell.unit.html).

#### `describe` in `cipt/diagnose.py`

```python
def describe(request: Request, name: str) -> str
```

- **Contract.** Returns one row in the planners' words, read from its name: `spend in <y> within $<b>k`, `<id> is a must-do`, `<id> is forced in`, `at most one of <ids>` (the group's members in id order, joined by a comma and a space), `<a> and <b> are funded together or not at all`, `<child> started by <t> needs <parent> started by <t - lag>`, `remove at least $<floor>k of risk` (one decimal, thousands commas) for the risk floor; the name itself for any other row. The kind is the part of the name before its first underscore.
- **Modeling idea.** A conflict is only useful in the names people can change.
- **Taught in** [9.1.6 Turning an IIS Into a Planner Message](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-06/9.1.6-turning-an-iis-into-a-planner-message.unit.html).

#### `explain` in `cipt/diagnose.py`

```python
def explain(request: Request, rows: list[str]) -> Conflict
```

- **Contract.** Returns a Conflict with the rows and a message: `No plan meets these <n> rules together; drop or change any one of them:` then one line `  <row>: <description>` per row.
- **Modeling idea.** Turn the IIS into a message that says what to change.
- **Taught in** [9.1.6 Turning an IIS Into a Planner Message](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-06/9.1.6-turning-an-iis-into-a-planner-message.unit.html).

#### `why_infeasible` in `cipt/diagnose.py`

```python
def why_infeasible(request: Request) -> Conflict | None
```

- **Contract.** None when the request has a plan; otherwise the Conflict of the rows that clash.
- **Modeling idea.** Run the filter only when the model is infeasible.
- **Taught in** [9.1.3 IIS With MathOpt, gurobipy and Pyomo](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-03/9.1.3-iis-with-mathopt-gurobipy-and-pyomo.unit.html).

#### `why_deferred` in `cipt/diagnose.py`

```python
def why_deferred(request: Request, plan, project_id: str) -> Deferral
```

- **Contract.** Forces the project in with a row `force_<id>`. When that is feasible, returns the NPV the plan gives up and the funded projects it drops; when it is not, the Conflict of the rows that block it, the force row kept.
- **Modeling idea.** Forcing a decision in and re-solving prices it; when no plan exists, the conflict says why.
- **Taught in** [9.3.2 Why Selected, Why Deferred: Forcing In and Out](../../../../09-diagnostics-and-explainability/39-explaining-decisions/units/unit-02/9.3.2-why-selected-why-deferred-forcing-in-and-out.unit.html).

#### `main` in `cipt/__main__.py`

```python
def main(argv: list[str] | None = None) -> int
```

- **Contract.** Prints the report; for an infeasible request also prints the conflict message and returns 1. With --why PROJECT for a project the plan leaves out, prints `<id> cannot be funded. <message>` or `Funding <id> costs $<cost>k of NPV and drops <ids or nothing>.` (cost in whole $k, ids joined by a comma and a space); for a project the plan funds, nothing more.
- **Modeling idea.** The command line is where the planners read the diagnostics.
- **Taught in** [14.2.6 Why It Failed, Why It Was Deferred: A Diagnostics Layer](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-06/14.2.6-why-it-failed-why-it-was-deferred-a-diagnostics-layer.unit.html).
