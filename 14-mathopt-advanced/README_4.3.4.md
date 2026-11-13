# 4.3.4 Incremental Solving: Edit the Model, Re-Solve

Finance is preparing for a budget meeting and wants GridCap's planners ready for any outcome: what
does the plan lose if 2029 is cut by 5%, by 10%, by 20%? And what if the board rules out P032, a
$5,680k transmission project? Each question changes one or two numbers of a model that is
otherwise the same. This lesson answers them all with one model and one solver: edit the model,
re-solve, put the edit back. It also shows which edits a solver applies in place and which make
MathOpt quietly start the solver over, and the two mistakes that make scenario code give wrong
answers. GridCap is a fictional utility.

Lesson 2.4.3 introduced `mathopt.IncrementalSolver` on an LP and measured its warm start in simplex
iterations. This lesson is about MIPs, where the solvers differ more, and about scenario code that
stays correct.

## The Model

The multi-period timing model of lesson 4.3.1, with the data each scenario changes marked. Its
decisions are start-time variables: $`x_{i,t}= 1`$ if project $`i`$ starts in year $`t`$ of its
window $`T_i`$; a project starts at most once and spends its cost profile from its start year on.
(Lesson 6.4.1, in section 6, builds this model step by step.)

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the
child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, project $`i`$'s spend in its $`k`$-th year
of work ($k); $`B_y`$, the budget of year $`y`$ ($k), **with $`B_{2029}`$ cut by a share
$`s \in \{5\%, 10\%, 20\%\}`$ in the cut scenarios**.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$, **with
$`x_{\text{P032},t} \le 0`$ for every $`t`$ in the "without P032" scenario** (an upper bound of 0,
so the project cannot start).

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints**, with $`\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}`$:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow (1 - s)\, B_{2029} \text{ for } y = 2029
\end{aligned}
```

## Keep a Handle on What a Scenario Changes, and Put It Back

A scenario is an edit of the model, and an edit needs a handle on the thing it changes. That is why
`plan_model.build` returns a `PlanModel` holding the start variables `x[pid, t]` and the budget rows
`budget[y]` by key, not just the model. With handles, every kind of change is one call:

| Change | Call | Lesson |
| --- | --- | --- |
| a row's limit | `row.upper_bound = ...`, `row.lower_bound = ...` | 2.4.3 |
| a coefficient in a row or in the objective | `row.set_coefficient(v, a)`, `model.objective.set_linear_coefficient(v, c)` | 2.4.3 |
| a variable's bounds | `v.lower_bound = ...`, `v.upper_bound = ...` | this one |
| a variable's type | `v.integer = False` (or `True`) | 4.3.3 |
| a new row or variable | `model.add_linear_constraint(...)`, `model.add_variable(...)` | 2.4.3 |
| remove a row or variable | `model.delete_linear_constraint(row)`, `model.delete_variable(v)` | this one |
| an indicator constraint's row | delete it and add it again; it cannot be edited | 4.3.1 |

An edit stays in the model for every solve that follows, so a scenario must put back what it
changed before the next one runs. `budget_cut.py` does that with a small **context manager**, a
function used in a `with` block that runs code on the way in and, thanks to `finally`, on the way
out, even if the block raises an error:

```python
@contextlib.contextmanager
def edited(obj, attr: str, value: float):
    """Set obj.attr for the length of a `with` block, then put the old value back, even on errors."""
    old = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield
    finally:
        setattr(obj, attr, old)
```

`edited(row, "upper_bound", 7_000)` sets the bound for the block and restores the old one after it.
It works for any attribute with a setter: a row's bounds, a variable's bounds, `integer`.

<!-- practice 1 -->

## One IncrementalSolver Answers Every Scenario

`mathopt.IncrementalSolver(model, solver_type)` keeps one solver alive across solves. Each call to
its `solve()` sends the solver only what changed in the model since the last call. Used as a
context manager, it frees the solver when the block ends (its docstring recommends it; `close()`
does the same by hand). The budget scenarios, all on one model built once:

```python
with quiet(), mathopt.IncrementalSolver(pm.model, mathopt.SolverType.GSCIP) as solver:
    base = solver.solve(params=EXACT)
    base_plan = plan(pm, base.variable_values())
```

```python
for share in (0.05, 0.10, 0.20):
    row = pm.budget[2029]
    with edited(row, "upper_bound", (1 - share) * small.budget[2029]):
        result = solver.solve(params=EXACT)
        cut_plan = plan(pm, result.variable_values())
        dropped = sorted(set(base_plan) - set(cut_plan))
        moved = sorted(p for p in cut_plan if p in base_plan and cut_plan[p] != base_plan[p])
```

```text
base           NPV 24,260
2029 cut   5%  NPV 24,070  dropped ['P005']  moved ['P008', 'P011', 'P018', 'P020']
2029 cut  10%  NPV 24,053  dropped ['P005', 'P016']  moved ['P008', 'P011', 'P012']
2029 cut  20%  NPV 23,645  dropped ['P005']  moved ['P010', 'P015', 'P020']
2029 bound after the loop: 8,760
```

Each cut is taken from the original budget, 8,760, because `edited` put the bound back after the
scenario before. The last line checks it. The NPV falls with every deeper cut: $190k at 5%, $207k
at 10%, $615k at 20%. The lists say how the plan absorbs it: a few projects dropped, more **moved**
to another start year. They are one optimal plan per scenario, not the only one: where two plans
tie on NPV, another solver, or another version, may return the other. That is also why the 20%
plan can keep P016 while the 10% plan drops it.

Ruling out a project is a scenario too. Its start variables get an upper bound of 0 for the length
of the block; `contextlib.ExitStack` enters several `edited` blocks at once and leaves them all:

```python
with contextlib.ExitStack() as stack:
    for t in small.project("P032").starts():
        stack.enter_context(edited(pm.x["P032", t], "upper_bound", 0.0))
    result = solver.solve(params=EXACT)
    rows.append(f"without P032   NPV {result.objective_value():,.0f}")
again = solver.solve(params=EXACT)
rows.append(f"all restored   NPV {again.objective_value():,.0f}")
```

```text
without P032   NPV 24,148
all restored   NPV 24,260
```

P032 is worth $112k of NPV to the plan, and once its bounds are back the model solves to the base
NPV again: the edits left no trace.

<!-- practice 2 -->

## Whether the Solver Updates in Place Depends on the Solver and the Edit

What does `IncrementalSolver.solve()` do with the changes? Its source in `solve.py` answers: it
asks the solver it holds to apply them. If the solver says it cannot, MathOpt throws that solver
away and builds a new one from the whole model, without telling you. Either way the result is right;
what differs is whether the solver kept its copy of the model, and with it any state it could reuse.

`update_or_rebuild.py` makes six edits in a row, solving after each, and checks whether the object
the `IncrementalSolver` holds is still the same one. It reads a private attribute,
`_proto_solver`, so treat it as a diagnostic for learning, not as code to ship:

```python
held = solver._proto_solver                       # private: diagnostic only
apply()
result = solver.solve()
report.append(f"{name}: {'in place' if solver._proto_solver is held else 'REBUILT'}")
```

```text
GSCIP  final NPV 27,514 | budget bound: in place, objective coef: in place, new row: in place, delete row: in place, new variable: in place, integer -> continuous: REBUILT
HIGHS  final NPV 27,514 | budget bound: REBUILT, objective coef: REBUILT, new row: REBUILT, delete row: REBUILT, new variable: REBUILT, integer -> continuous: REBUILT
CP_SAT final NPV 27,514 | budget bound: REBUILT, objective coef: REBUILT, new row: REBUILT, delete row: REBUILT, new variable: REBUILT, integer -> continuous: REBUILT
```

- **SCIP** applied five of the six edits in place, and rebuilt only when a variable stopped being
  integer.
- **HiGHS and CP-SAT** rebuilt after every edit. Through MathOpt in OR-Tools 9.15, an
  `IncrementalSolver` on either is a fresh solve each time, the same finding lesson 2.4.3 made for
  HiGHS on an LP.
- **All three end at the same NPV**, 27,514 (high, because the edits included deleting the 2031
  budget row). A rebuild costs time, never correctness.

"In place" means the solver kept its model; it does not by itself mean the MIP search starts from
where the last one ended. This program measures no speed, and for a MIP the gain depends on the
solver and the edit. What the table does settle is the choice of tool: for many scenarios of one
model, an `IncrementalSolver` is never worse than a fresh `mathopt.solve`, and on SCIP it avoids
rebuilding the solver's model; on HiGHS and CP-SAT it gives nothing, and editing the model in place
is still worth it, because it saves rebuilding *your* model.

## Undo Every Edit, and Never Delete What a Scenario Only Switches Off

Two mistakes make scenario code quietly wrong. The first is a relative edit that is never undone:

```python
for scenario in ("5% cut", "another 5% cut"):
    pm.budget[2029].upper_bound *= 0.95
```

```text
5% cut          2029 bound 8,322.00  (budget 8,760, cut 5.00%)
another 5% cut  2029 bound 7,905.90  (budget 8,760, cut 9.75%)
```

The second scenario was meant to be "a 5% cut" and ran as a 9.75% one, and nothing failed. Either
compute each scenario from the original data, as the loop with `edited` does with
`(1 - share) * small.budget[2029]`, or restore after each scenario, and best both.

The second mistake is deleting what a scenario only needs to switch off. Deletion cannot be put
back with an assignment, and every reference to a deleted variable stops working:

```python
spare = pm.x["P040", 2028]
pm.model.delete_variable(spare)
try:
    spare.upper_bound = 1.0
except Exception as error:
    print("using a deleted variable:", type(error).__name__, "|", error)
```

```text
using a deleted variable: ValueError | no element with id 79 for element type variable
```

The `Variable` object still exists in Python, but the model no longer has the element it points to
(id 79, the last of the 80 start variables). Deleting a variable also removes it from every row and
the objective, so adding it back would mean rebuilding all of those. To take a project out of one
scenario, bound its variables to 0, as the "without P032" scenario did; delete only what is gone
for good. The upper bound is the one that matters: a lower bound of 1 would do the opposite and
force the project in. Setting its NPV to 0 in the objective is not the same thing: the project could still
start and spend budget for no value, which is a different scenario from "without". Indicator constraints are the one exception, because they cannot be edited at all
(lesson 4.3.1): to change one, delete it and add a new one, and replace your handle.

<!-- practice 3 -->

## Summary

- **Keep a handle on what a scenario changes, and put it back.** A builder that returns rows and
  variables by key makes each scenario one edit; a context manager restores it even on errors.
- **One IncrementalSolver answers every scenario.** Three 2029 cuts and a ruled-out project, on one
  model built once; the cuts cost $190k, $207k and $615k of NPV.
- **Whether the solver updates in place depends on the solver and the edit.** In OR-Tools 9.15,
  SCIP applied bound, coefficient, row and variable edits in place; HiGHS and CP-SAT rebuilt after
  every edit, silently and correctly.
- **Undo every edit, and never delete what a scenario only switches off.** Relative edits pile up;
  a deleted variable's references raise `ValueError`.

## Reference

| Task | Code |
| --- | --- |
| one solver for many solves | `with mathopt.IncrementalSolver(model, solver_type) as solver: solver.solve(params=...)` |
| a temporary edit | `with edited(row, "upper_bound", value): ...` (`budget_cut.py`) |
| several temporary edits | `contextlib.ExitStack()` and `stack.enter_context(edited(...))` |
| rule a project out | `v.upper_bound = 0` for its start variables, then restore |
| relax integrality in place | `v.integer = False` |

| Solver (OR-Tools 9.15) | Edits applied in place by `IncrementalSolver` |
| --- | --- |
| SCIP | bounds, objective coefficients, new and deleted rows, new variables; rebuilt on an integrality change |
| HiGHS, CP-SAT | none: rebuilt on every edit |
| GLOP (LP, lesson 2.4.3) | warm-starts from the last basis |

**Further reading.** OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt):
incremental solving among MathOpt's features. `IncrementalSolver` in
[`solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py): its
docstring (the `with` form, `close`, thread safety) and its `solve` method, which rebuilds the solver
when an update is refused. The samples
[`facility_lp_benders.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/facility_lp_benders.py),
which keeps two incremental solvers through a Benders loop and edits bounds and adds rows between
solves, and
[`cutting_stock.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/cutting_stock.py),
which re-solves a growing LP with an incremental GLOP solver.

## Challenges

1. Add a fourth scenario: 2029 cut by 10% *and* P032 ruled out. Is its NPV loss the sum of the two
   losses alone? Predict, then run.
2. In `update_or_rebuild.py`, add an edit that adds an indicator constraint, and run it on SCIP.
   Does SCIP keep its solver?
3. A colleague writes `pm.budget[2029].upper_bound -= 438` for a 5% cut and `+= 438` to undo it. When
   could that leave the bound different from where it started?

## Design Note: Scenarios Are Data, Edits Are Code

`budget_cut.py` lists its scenarios as numbers (`0.05, 0.10, 0.20`) and has one piece of code that
turns a number into an edit and back. Adding a scenario is adding a number. The same split scales to
the scenario tables planners ask for: a list of scenarios, each a set of (handle, attribute, value)
edits, and one loop that applies, solves, records and restores. Section 12 builds that loop into
a service.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**budget_cut.py.** The 2029 cut scenarios and the "without P032" scenario on one `IncrementalSolver`,
then the two mistakes: piled-up relative edits and a deleted variable (*Keep a Handle*, *One
IncrementalSolver Answers Every Scenario*, *Undo Every Edit*). *Try:* Replace the SCIP solver with
HiGHS and predict whether any number in the table changes.

- Program: [budget_cut.py](src/budget_cut.py)

**update_or_rebuild.py.** Six edits on SCIP, HiGHS and CP-SAT, and whether each was applied in place
(*Whether the Solver Updates in Place*). *Try:* Move the integrality edit to the front and predict
what SCIP reports for the edits after it.

- Program: [update_or_rebuild.py](src/update_or_rebuild.py)
