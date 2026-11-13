# 5.2.2 Reading PuLP Code You Inherit

A contractor left GridCap a PuLP script: lesson 1.1.1's one-period selection (fund projects within
one capital budget, with must-do, parent and alternative-group rules), written in the style of
PuLP code from before version 3.3. Planners have since added their own rules to copies of it, and
some of those copies give answers nobody can explain. GridCap now wants three things: read the
script, find the lines that do not do what they say, and move it to MathOpt, the API the rest of
GridCap's planning code uses. GridCap is a fictional utility's portfolio.

PuLP is easy to write and easy to misread. Most of its traps share one cause: PuLP gives no error,
and the model quietly becomes a different model. Five rules, one per heading. They run on PuLP
`3.3.2`, the course's pinned version (lesson 5.2.1).

## Older PuLP Code Makes Variables Apart From the Problem and Reads Answers Off Them

Here is the inherited script, `legacy_selection.py`, whole:

```python
from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpStatus, LpVariable, lpSum, value


def solve_legacy(portfolio, gap=None):
    """Return (status text, value, funded project ids, problem)."""
    ids = [p.project_id for p in portfolio.projects]
    x = LpVariable.dicts("x", ids, cat="Binary")

    prob = LpProblem("selection", LpMaximize)
    prob += lpSum(p.value * x[p.project_id] for p in portfolio.projects)

    prob += lpSum(p.capex * x[p.project_id] for p in portfolio.projects) <= portfolio.capital_budget, "budget"
    for p in portfolio.projects:
        if p.must_do:
            prob += x[p.project_id] == 1, "must_" + p.project_id
        if p.parent:
            prob += x[p.project_id] <= x[p.parent], "parent_" + p.project_id

    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g in groups:
        prob += lpSum(groups[g]) <= 1, "alt_" + g

    prob.solve(PULP_CBC_CMD(msg=0, gapRel=gap))
    status = LpStatus[prob.status]
    funded = [i for i in ids if value(x[i]) > 0.5]
    return status, value(prob.objective), funded, prob
```

Read it line by line against lesson 5.2.1's version:

- **`LpVariable.dicts("x", ids, cat="Binary")`** makes one variable per key, before any problem
  exists, and names each one by the prefix, an underscore and the key: `x_P001`. A variable
  joins the problem only when a row or the objective uses it.
- **`prob += lpSum(...)` with no name** sets the objective. PuLP names it `OBJ`.
- **`prob += ... <= ..., "budget"`** adds a named row, as in lesson 5.2.1.
- **`prob.solve(PULP_CBC_CMD(msg=0, gapRel=gap))`** runs the bundled CBC quietly. The script
  ignores what `solve` returns and reads `prob.status` through `LpStatus` instead.
- **`value(x[i])`** reads a value. It is the same number as `x[i].varValue`.

On GridCap small it finds the value lesson 4.7.1 found with pywraplp, and you can look inside what
it built:

```text
Optimal: value $25,336k, 20 of 40 funded
variables 40, rows 9, objective named 'OBJ'
a variable: x_P001 Integer 0 1 value 0.0
rows: budget, must_P003, must_P010, parent_P016 ... alt_G030
budget row: sense -1, rhs 38,390, slack 0
DeprecationWarnings raised by the script:
  LpVariable.dicts is deprecated
  PULP_CBC_CMD is deprecated and will be removed in PuLP 4.0. Install CBC with `pip install pulp[cbc]` and use COIN_CMD instead.
```

A binary is stored as an integer with bounds 0 and 1, which is why `x_P001` prints `Integer 0 1`.
A row's `sense` is a number: -1 for `<=` (`pulp.LpConstraintLE`), 1 for `>=`, 0 for `==`.

The idioms map to the forms of lesson 5.2.1, which PuLP 4 keeps:

| Older idiom | What it does | Form that PuLP 4 keeps |
| --- | --- | --- |
| `LpVariable.dicts("x", ids, cat="Binary")` | one variable per key, named `x_<key>` | `prob.add_variable_dicts("x", ids, cat=pulp.LpBinary)` |
| `LpVariable("k", 0, 3, cat="Integer")` | one variable | `prob.add_variable("k", 0, 3, cat=pulp.LpInteger)` |
| `prob.constraints["budget"]` | a row by name, from a dict | `prob.get_constraint_by_name("budget")` |
| `PULP_CBC_CMD(msg=0)` | the CBC bundled in PuLP 3 | `COIN_CMD(msg=False)` |
| `LpStatus[prob.status]` | the status as text | `stats.status_str` on what `solve()` returns |

Python hides a `DeprecationWarning` raised inside a library unless warnings are switched on
(`python -W default`), so nobody saw that PuLP 3.3 warns about two of the script's lines, printed
above. PuLP 4 removed both, and `LpStatus` as well, so the script will not run on PuLP 4 as it
stands.

## `+=` Adds a Row Only When It Is Handed a Constraint

`+=` decides what to do from the type of what it is given. A comparison of PuLP expressions is an
`LpConstraint`, and `+=` adds it as a row. A PuLP expression with no comparison becomes the
objective, replacing the old one. And a plain Python `True` is accepted and dropped, because PuLP
lets `prob += True` pass on purpose (a comparison between two numbers is always `True` or `False`).
`False` raises a `TypeError`. That is how PuLP 3.3's `LpProblem.__iadd__` is written.

Three planner rules were added to copies of the script, each in a way that looks right. Each is run
on GridCap small next to the line it meant:

```python
row = last_plan["P005"] == 1
print("the lock row as written is a", type(row).__name__, "=", row)
prob += row, "lock_P005"
report("lock written on data", prob, x)
prob, x = base()
prob += x["P005"] == 1, "lock_P005"
report("lock written on x", prob, x)
```

```python
row = 9000 <= ridge(x) <= 12000
print("the chained row as written is:", row)
prob += row, "ridge_band"
report("band chained", prob, x)
prob, x = base()
prob += ridge(x) >= 9000, "ridge_min"
prob += ridge(x) <= 12000, "ridge_max"
```

```python
prob += crew(x), "crew"
report("crew row, no <=", prob, x)
prob, x = base()
prob += crew(x) <= 90, "crew"
```

```text
no extra rule          rows  9  Optimal  objective  25,336  value $25,336k  P005 out  Ridge $7,360k  crew 100
the lock row as written is a bool = True
lock written on data   rows  9  Optimal  objective  25,336  value $25,336k  P005 out  Ridge $7,360k  crew 100
lock written on x      rows 10  Optimal  objective  25,072  value $25,072k  P005 in  Ridge $7,360k  crew 101
the chained row as written is: 2860*x_P007 + 390*x_P008 + 1010*x_P009 + 1720*x_P019 + 230*x_P020 + 1700*x_P024 + 5060*x_P028 + 580*x_P035 + 2120*x_P037 <= 12000.0
band chained           rows 10  Optimal  objective  25,336  value $25,336k  P005 out  Ridge $7,360k  crew 100
band as two rows       rows 11  Optimal  objective  24,897  value $24,897k  P005 out  Ridge $9,060k  crew 100
crew row, no <=        rows  9  Optimal  objective     111  value $20,347k  P005 out  Ridge $9,120k  crew 111
                       PuLP warned: UserWarning: Overwriting previously set objective.
crew row with <= 90    rows 10  Optimal  objective  24,250  value $24,250k  P005 out  Ridge $6,780k  crew 90
a guard that refuses anything but a constraint: False False True
```

What each line did:

- **The lock written on data.** `last_plan` holds last year's answers, read from a file: numbers,
  not variables. `last_plan["P005"] == 1` is Python comparing `1.0` with `1`, which is `True`, so
  `+=` dropped it. The row count stays at 9 and P005 stays out. Written on the variable, the lock
  is a tenth row, P005 is in, and the plan is worth $264k less, the price of the planners' rule.
- **The chained band.** Python reads `a <= b <= c` as `(a <= b) and (b <= c)`. A PuLP constraint
  counts as true in an `and`, so the expression's value is its right half alone: the printed row
  has only `<= 12000`. Ridge stayed at $7,360k, below the $9,000k floor. As two rows, Ridge gets
  $9,060k.
- **The crew row with no `<=`.** It is an expression, so it became the objective. CBC maximized
  crew-months (111), and the plan's value fell to $20,347k. PuLP did warn, with a `UserWarning` on
  standard error, which a nightly job's log is unlikely to show anyone.

None of the three is an error, and none changes the status: each run says Optimal. Two defenses
catch them. **Count the rows:** a rule that adds no row, or one row where two were meant, shows up in
`prob.numConstraints()` and in the LP file. **Refuse anything but a constraint** before adding it:
`isinstance(row, pulp.LpConstraint)` is `False` for the lock written on data and for the bare crew
expression, and `True` for a real row, as the last line printed. A chained comparison does pass
that check, since its right half is a real constraint, so the rule there is simpler: never chain.
Write a band as two rows, each with its own name.

## Row and Variable Names Must Stay Unique After PuLP Rewrites Them

Names identify rows in the LP file, in a solver's log and in `get_constraint_by_name`. PuLP enforces
them, and also rewrites them. `names.py` shows how two names become one. `attempt(label, action)`
runs `action` and prints its result, or the error it raised cut to its first line; `add` adds one
named row; `lp_rows` writes the problem as an LP file and returns its row lines:

```python
prob = pulp.LpProblem("names", pulp.LpMaximize)
y = pulp.LpVariable.dicts("y", ["P001", "P002", "P003"], cat="Binary")
prob += pulp.lpSum(y.values()), "value"

# 1. The same name twice: refused when the second row is added.
prob += y["P001"] + y["P002"] <= 1, "alt_G1"
attempt("same name twice", lambda: add(prob, y["P002"] + y["P003"] <= 1, "alt_G1"))

# 2. Names PuLP rewrites: '-', '+', '[', ']', ' ', '>' and '/' are not allowed in an LP file.
prob += y["P001"] <= 1, "cap Ridge"
print("'cap Ridge' is stored as", [row.name for row in prob.constraints()][-1])
prob += y["P002"] <= 1, "budget-2027"
attempt("'budget-2027' then 'budget_2027'", lambda: add(prob, y["P003"] <= 1, "budget_2027"))

# 3. Rows with no name get one from a counter, so the same row has another name in another run.
for extra_first in (False, True):
    auto = pulp.LpProblem("auto", pulp.LpMaximize)
    z = pulp.LpVariable("z", 0, 10)
    auto += z
    if extra_first:
        auto += z >= 1
    auto += z <= 8
    auto += z <= 9
    print(f"unnamed rows{' with one more in front' if extra_first else ''}: name in constraints() "
          f"{[row.name for row in auto.constraints()]}, in the LP file {lp_rows(auto)}")

# 4. Variable names: two keys that differ only in a rewritten character give one name.
x = pulp.LpVariable.dicts("x", ["P-017", "P_017"], cat="Binary")
print("variable names:", {key: var.name for key, var in x.items()})
twice = pulp.LpProblem("twice", pulp.LpMaximize)
twice += x["P-017"] + 2 * x["P_017"], "value"
twice += x["P-017"] + x["P_017"] <= 1, "one"
attempt("solve with a repeated variable name", lambda: twice.solve(pulp.PULP_CBC_CMD(msg=0)))
attempt("checkDuplicateVars()", lambda: twice.checkDuplicateVars() or "no repeats")
```

```text
same name twice: PulpError: overlapping constraint names: alt_G1
'cap Ridge' is stored as cap_Ridge
'budget-2027' then 'budget_2027': PulpError: overlapping constraint names: budget_2027
unnamed rows: name in constraints() [None, None], in the LP file ['_C1: z <= 8', '_C2: z <= 9']
unnamed rows with one more in front: name in constraints() [None, None, None], in the LP file ['_C1: z >= 1', '_C2: z <= 8', '_C3: z <= 9']
variable names: {'P-017': 'x_P_017', 'P_017': 'x_P_017'}
solve with a repeated variable name: PulpSolverError: Pulp: Error while executing .../cbc
checkDuplicateVars(): PulpError: Repeated variable names: {('x_P_017', 2)}
```

Read it as four rules:

1. **A repeated row name is refused** with `PulpError` when the second row is added. That one is
   loud. It usually means a loop built names from too little: `alt_` plus a region where the
   groups are per region and program, say.
2. **PuLP rewrites characters an LP file cannot hold**, such as a space or a `-`, to `_`. So
   `budget-2027` and `budget_2027` are the same name, and the second is refused. Build names from
   ids that are already plain: letters, digits and `_`.
3. **A row with no name gets one from a counter**, `_C1`, `_C2`, ... in the order rows were added.
   One more row in front, and every later row's name moves: `z <= 8` was `_C1`, then `_C2`. Two
   runs' LP files can then no longer be compared row by row, so name every row.
4. **Two variables with one name are not refused when they are made**, because `LpVariable.dicts`
   makes them apart from the problem. Keys `P-017` and `P_017`, from two systems that spell ids
   differently, both became `x_P_017`, and the solve failed with a message that says only that CBC
   could not run. `prob.checkDuplicateVars()` says what is wrong; call it before solving a model
   whose variable names come from data.

## Read `status` and `sol_status` Before Any Value, and Expect None

Lesson 5.2.1 showed that `status` 1 with `sol_status` 2 is a plan nobody proved best. The inherited
script has worse problems: it reads values whatever the status, and older code often guards the
solve with `if prob.solve(...):`. `status_traps.py` runs both on a budget too small for the must-do
projects, so no plan exists:

```python
status, total, funded, prob = solve_legacy(tight)
code = prob.status
print(f"must-do capex ${must:,}k, budget ${tight.capital_budget:,}k")
print(f"solve() returned {code} ({pulp.LpStatus[code]}); `if prob.solve():` takes the branch: {bool(code)}")
```

```text
must-do capex $7,630k, budget $6,630k
solve() returned -1 (Infeasible); `if prob.solve():` takes the branch: True
the legacy script still reports: value $1,687.29k, funded ['P003', 'P010', 'P017', 'P039']
  binary variables left holding a value that is not 0 or 1: {'x_P034': -0.469}
```

The status code for Infeasible is -1, and Python treats every number but 0 as true, so
`if prob.solve():` runs its "we have a plan" branch exactly when there is none. The values left in
the variables are whatever CBC had when it gave up: four must-do projects at 1, and `x_P034`, a
binary, at -0.469. The script prints them as a plan worth $1,687.29k. A value read after a run with
no plan is not a plan.

The other trap is `None`. A variable that never entered the problem has no value, and neither does
an objective that was never set:

```python
on_hold = {"P003"}                                    # left out of every row and of the objective
```

```python
try:
    print([pid for pid in x if pulp.value(x[pid]) > 0.5])
except TypeError as error:
    print("value(x) > 0.5 raised TypeError:", error)
```

```text
after the solve: {'P001': 0.0, 'P002': 1.0, 'P003': None}
value(x) > 0.5 raised TypeError: '>' not supported between instances of 'NoneType' and 'float'
objective: None | status Optimal
value(prob.objective) raised AttributeError: 'NoneType' object has no attribute 'value'
```

`LpVariable.dicts` made `x["P003"]`, but no row or objective used it, so CBC never saw it, and its
`varValue` is still `None`. `pulp.value(x)` passes that `None` through, and the comparison fails.
A feasibility check with no objective has `prob.objective` set to `None`, and `pulp.value(None)`
fails too. In inherited code, these errors usually mean a variable the code made and then forgot
to use, which is worth knowing before you fix the crash.

So read a result in this order, as `read_plan` does:

```python
def read_plan(prob, x, proved=True):
    """Funded ids, only from a solve that ended with a solution (proved optimal, unless proved=False)."""
    wanted = {pulp.LpSolutionOptimal} if proved else {pulp.LpSolutionOptimal, pulp.LpSolutionIntegerFeasible}
    if prob.status != pulp.LpStatusOptimal or prob.sol_status not in wanted:
        raise NoPlan(f"status {pulp.LpStatus[prob.status]}, {pulp.LpSolution[prob.sol_status]}")
    missing = [key for key, var in x.items() if var.varValue is None]
    if missing:
        raise NoPlan(f"no value for {missing}: not in the problem")
    return [key for key, var in x.items() if var.varValue > 0.5]
```

```text
read_plan, infeasible budget: refused (status Infeasible, No Solution Exists)
read_plan, project on hold: refused (no value for ['P003']: not in the problem)
```

<!-- practice 1 -->

## Migrating to MathOpt Maps Each PuLP Call, and a Test Proves the Port

Lesson 4.7.2 moved a pywraplp script to MathOpt; moving a PuLP script works the same
way. Map each call, port the script with the same names, then prove the port with a test.

| PuLP 3.3 | MathOpt | Note |
| --- | --- | --- |
| `LpProblem("selection", LpMaximize)` | `mathopt.Model(name="selection")`, then `model.maximize(...)` | the sense goes with the objective |
| `LpVariable.dicts("x", ids, cat="Binary")` | `{i: model.add_binary_variable(name="x_" + i) for i in ids}` | keep the names |
| `LpVariable("k", 0, 3, cat="Integer")` | `model.add_integer_variable(lb=0, ub=3, name="k")` | a bound left out is infinite in both |
| `LpVariable("s", 0)` | `model.add_variable(lb=0, name="s")` | continuous |
| `prob += expr, "obj"` | `model.maximize(expr)` | |
| `prob += expr <= b, "name"` | `model.add_linear_constraint(expr <= b, name="name")` | |
| `lo <= expr <= hi` (two rows in PuLP) | `model.add_linear_constraint(lb=lo, expr=expr, ub=hi, name=...)` | one ranged row; MathOpt has no chaining trap |
| `lpSum(terms)` | `sum(terms)` | start an empty sum from `mathopt.LinearExpression()` |
| `prob.solve(PULP_CBC_CMD(msg=0, gapRel=0))` | `mathopt.solve(model, SolverType.GSCIP, params=SolveParameters(relative_gap_tolerance=0.0))` | the solver is named at solve time |
| `prob.status`, `prob.sol_status` | `result.termination.reason` | `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, ... |
| `x.varValue`, `value(prob.objective)` | `result.variable_values(x)`, `result.objective_value()` | |

The port, `mathopt_selection.py`, keeps every row name of the script:

```python
    model = mathopt.Model(name="selection")
    x = {p.project_id: model.add_binary_variable(name="x_" + p.project_id) for p in portfolio.projects}
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))

    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")
```

```python
    result = mathopt.solve(model, solver, params=mathopt.SolveParameters(relative_gap_tolerance=gap))
    reason = result.termination.reason
    if reason not in (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE):
        return reason.name, None, [], model
```

Two kinds of trap from this lesson cannot happen in the port. MathOpt keeps no answer inside the
model: it returns a result, and the port reads a value only after checking the termination reason.
And a MathOpt row is made by `add_linear_constraint`, a call that only takes a comparison, never
the objective. The end of `compare_ports.py` hands it the three lines of the second section:

```python
for label, row in (("lock on data", lambda: last_plan["P005"] == 1),
                   ("chained band", lambda: 1 <= x["P005"] + x["P007"] <= 2),
                   ("no comparison", lambda: x["P005"] + x["P007"])):
```

```text
MathOpt, lock on data: TypeError: Unsupported type for bounded_expr argument: bool
MathOpt, chained band: TypeError: __bool__ is unsupported for LowerBoundedExpression
MathOpt, no comparison: TypeError: bounded_expr has bad type: 'LinearSum'.
```

Each one fails loudly where PuLP went on in silence. The chained band fails while Python evaluates
it, because a MathOpt comparison refuses to be read as true or false; a band is written as one
ranged row instead, as the map says.

The proof is the test of lesson 4.7.2: the same value with both solvers at a gap of 0, the same plan
where the optimum is unique, each plan kept by the other's rules, and the same rows by name. Run
it on more than one size. `compare_ports.py` adds the infeasible case:

```python
for size in ("tiny", "small", "medium"):
    portfolio = generate(size)
    status, old_value, old_plan, prob = solve_legacy(portfolio, gap=0)
    reason, new_value, new_plan, model = solve_ported(portfolio, mathopt.SolverType.GSCIP, gap=0.0)
```

```text
tiny   PuLP+CBC Optimal $3,627k | MathOpt+SCIP OPTIMAL $3,627k | same value: True, same plan: True, each plan allowed: True, same rows: True
small  PuLP+CBC Optimal $25,336k | MathOpt+SCIP OPTIMAL $25,336k | same value: True, same plan: True, each plan allowed: True, same rows: True
medium PuLP+CBC Optimal $229,745k | MathOpt+SCIP OPTIMAL $229,745k | same value: True, same plan: True, each plan allowed: True, same rows: True
infeasible budget: ('Infeasible', 1687.28638089, ['P003', 'P010', 'P017', 'P039']) | ('INFEASIBLE', None, [])
```

The port agrees on all three sizes, and on the infeasible budget it does what the script should
have done: no value and no plan. The port runs SCIP here, not HiGHS, because this program has
imported PuLP: lesson 5.2.1 showed that MathOpt's HiGHS then crashes the process on a MIP. Once
the port is proved, PuLP leaves the code, and with it the reason to avoid HiGHS. Until then, keep
the two in separate processes or solve the port with SCIP. The module's test,
`test_the_mathopt_port_reaches_the_legacy_value_plan_and_rows_at_zero_gap`, runs the same checks
on all three sizes.

<!-- practice 2 -->

## The Model

The inherited script and its port build the same model, lesson 1.1.1's selection, with the same
names.

**Sets.** $`P`$, the projects; $`M \subseteq P`$, the must-do projects; $`C \subseteq P`$, the child
projects, each with a parent $`p(c)`$; $`\mathcal{G}`$, the alternative groups.

**Parameters.** $`v_i`$, the value of project $`i`$ ($k); $`c_i`$, its capital cost ($k); $`B`$, the
capital budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for $`i \in P`$ (`LpVariable.dicts(..., cat="Binary")`, ported
to `add_binary_variable`).

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

The rows are named `budget`, `must_<id>`, `parent_<child id>` and `alt_<group id>` in both versions.
The three planner rules of the second section, written correctly, would add

```math
\begin{aligned}
x_{P005} &= 1 && && \text{(lock\_P005)} \\
9000 \le \sum_{i \in R} c_i\, x_i &\le 12000 && R = \text{Ridge's projects} && \text{(ridge\_min, ridge\_max)} \\
\sum_{i \in P} w_i\, x_i &\le 90 && w_i = \text{crew-months of } i && \text{(crew)}
\end{aligned}
```

## Summary

- **Older PuLP code makes variables apart from the problem and reads answers off them.**
  `LpVariable.dicts` names variables `x_<key>`; the answer is read from `varValue`, `value()` and
  `LpStatus[prob.status]`.
- **`+=` adds a row only when it is handed a constraint.** `True` is dropped, a chained band keeps
  only its right half, and an expression replaces the objective. All three runs said Optimal.
- **Row and variable names must stay unique after PuLP rewrites them.** `-` and space become `_`;
  unnamed rows get counter names that shift; repeated variable names fail inside CBC, and
  `checkDuplicateVars()` names them.
- **Read `status` and `sol_status` before any value, and expect None.** `if prob.solve():` is true
  for Infeasible (-1), and an infeasible run left a binary at -0.469.
- **Migrating to MathOpt maps each PuLP call, and a test proves the port.** The port matched the
  script on tiny, small and medium at gap 0, and reported no plan where the script reported one.

## Reference

| You see | It means | Do instead |
| --- | --- | --- |
| `prob += data[i] == 1` | a `bool`; `True` is dropped, `False` raises | write the row on the variable |
| `prob += lo <= expr <= hi` | only `expr <= hi` | two named rows |
| `prob += expr` after the objective | a new objective, with a `UserWarning` | add the comparison |
| a row with no name | `_C1`, `_C2`, ... in order of adding | name every row |
| ids with `-` or spaces in names | rewritten to `_`, and may collide | plain ids; `checkDuplicateVars()` |
| `if prob.solve(...):` | true for every status but Not Solved | compare with `pulp.LpStatusOptimal` |
| values read after a run with no plan | leftovers, even out of bounds | check both codes first |
| `varValue` is `None` | the variable is in no row and not in the objective | find why it was left out |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the
API the port moves to, and the solvers it can call) and the
[MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py)
(the shape of a MathOpt MIP program: model, rows, objective, solve, termination check);
[Optimization with PuLP](https://coin-or.github.io/pulp/) (the PuLP 4.3 documentation);
[A Blending Problem, PuLP 3.3.2 source](https://github.com/coin-or/pulp/blob/3.3.2/doc/source/CaseStudies/a_blending_problem.rst)
(the documentation's model in the style inherited code uses: `+=` with names, `LpStatus`,
`varValue`, `value`); [How to migrate from PuLP 3.x to 4.0](https://www.coin-or.org/pulp/guides/how_to_migrate_to_v4.html)
(what replaced `LpVariable.dicts`, the constraints dict, `PULP_CBC_CMD` and `LpStatus`);
[How to debug most errors during solving](https://www.coin-or.org/pulp/guides/how_to_debug.html)
(reading the LP file, and finding which rows make a model infeasible);
[How to configure a solver in PuLP, 3.3.2](https://github.com/coin-or/pulp/blob/3.3.2/doc/source/guides/how_to_configure_solvers.rst)
(`PULP_CBC_CMD` deprecated in 3.3).

## Challenges

1. Add a `lock_P006` row written on `last_plan` to `silent_rows.py`. `last_plan["P006"]` is 0.0.
   Predict what PuLP does with that line, then run it.
2. Write `add_row(prob, row, name)` that refuses anything but an `LpConstraint` and any name PuLP
   would rewrite. Run the three planner rules through it.
3. Port `silent_rows.py`'s Ridge band to the MathOpt port as one ranged row, and check that the
   port then reaches $24,897k on small.

## Design Note: Fix the Legacy Code Before You Port It, and Say Which You Did

A port proves that the new code gives the same answers as the old. If the old code has a dropped
lock row, a port that is "the same" faithfully keeps the bug, and a port that quietly fixes it fails
the test for a good reason. So do it in two steps. First fix the PuLP script, with a test for each
fix (a row count, a value), and record the new answers. Then port, and prove the port against the
fixed script. Each step then has one reason to change the numbers, and a reviewer can see which
step changed which number.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**run_legacy.py and legacy_selection.py.** The inherited script on GridCap small, what it
built (variables, rows, the objective's name, the budget row) and the warnings it raised (*Older PuLP Code Makes Variables
Apart From the Problem*). *Try:* Print `prob.constraints()[0]`. Predict which row comes first.

- Program: [run_legacy.py](src/run_legacy.py)
- Library: [legacy_selection.py](src/legacy_selection.py)

**silent_rows.py.** The three planner rules written wrong and right (*`+=` Adds a Row Only When It
Is Handed a Constraint*). *Try:* Change the Ridge band to 9000 to 9500. Predict which of the two
versions is infeasible.

- Program: [silent_rows.py](src/silent_rows.py)

**names.py.** Repeated, rewritten and counter-made names (*Row and Variable Names Must Stay
Unique*). *Try:* Name a row `cap+Ridge`. Predict the name PuLP stores.

- Program: [names.py](src/names.py)

**status_traps.py.** An infeasible run read the legacy way, values that are `None`, and a reader
that refuses both (*Read `status` and `sol_status` Before Any Value*). *Try:* Call `read_plan`
on the infeasible problem with `proved=False`. Predict whether it still refuses.

- Program: [status_traps.py](src/status_traps.py)

**compare_ports.py and mathopt_selection.py.** The script and its MathOpt port on three sizes and
an infeasible budget, and MathOpt refusing the three silent rows (*Migrating to MathOpt*). *Try:* Leave the `alt_` rows out of the port.
Predict which of the four checks fails first, and on which size.

- Program: [compare_ports.py](src/compare_ports.py)
- Library: [mathopt_selection.py](src/mathopt_selection.py)
