# 4.7.2 Migrating a pywraplp Model to MathOpt

The inherited selection script of lesson 4.7.1 now has to join GridCap's MathOpt code base. The
rest of the planning service builds MathOpt models and switches between HiGHS, SCIP and CP-SAT
with one argument; this script builds its model inside a SCIP solver object and cannot. The team
lead's condition for the port is simple: **prove it gives the same answer.**

A port is a rewrite in which nothing about the model may change. This lesson maps every pywraplp
call to its MathOpt counterpart, ports the script, and then proves the port with a test, which on
GridCap's medium portfolio turns up a difference that is not a bug. GridCap is a fictional
utility's portfolio. Three rules, one per heading.

## Every pywraplp Call Has a MathOpt Counterpart

Lesson 4.7.1's first example, written in both APIs. pywraplp first:

```python
solver = pywraplp.Solver.CreateSolver("SCIP")
x = solver.IntVar(0, solver.infinity(), "x")
y = solver.IntVar(0, solver.infinity(), "y")
cap = solver.Add(x + 7 * y <= 17.5, "cap")
solver.Add(x <= 3.5, "x_max")
solver.Maximize(x + 10 * y)
status = solver.Solve()
```

Then MathOpt, line for line:

```python
model = mathopt.Model(name="first")
mx = model.add_integer_variable(lb=0, name="x")
my = model.add_integer_variable(lb=0, name="y")
mcap = model.add_linear_constraint(mx + 7 * my <= 17.5, name="cap")
model.add_linear_constraint(mx <= 3.5, name="x_max")
model.maximize(mx + 10 * my)
result = mathopt.solve(model, mathopt.SolverType.GSCIP)
if result.termination.reason == mathopt.TerminationReason.OPTIMAL:
```

```text
pywraplp: objective 23.0, x 3.0, y 2.0
MathOpt:  objective 23.0, x 3.0, y 2.0
```

The shape is the same: variables with bounds, rows from expressions, an objective with a sense. Two
things moved. The model is created on its own (`mathopt.Model`) and the back end is named only in
`mathopt.solve`. And the answer comes back as a **result object**, not as state left inside the
solver. The full map:

| pywraplp | MathOpt | Note |
| --- | --- | --- |
| `pywraplp.Solver.CreateSolver("SCIP")` | `mathopt.Model(name=...)`, then `mathopt.SolverType.GSCIP` at solve time | SCIP's enum is `GSCIP`, not `SCIP` |
| `"GLOP"`, `"SAT"`, `"PDLP"`, `"HIGHS"` | `SolverType.GLOP`, `CP_SAT`, `PDLP`, `HIGHS` | |
| `NumVar(l, u, n)` | `add_variable(lb=l, ub=u, name=n)` | default bounds differ: see below |
| `IntVar(l, u, n)` | `add_integer_variable(lb=l, ub=u, name=n)` | |
| `BoolVar(n)` | `add_binary_variable(name=n)` | |
| `solver.infinity()` | `math.inf`, or leave the bound out | |
| `var.SetBounds(l, u)` | `var.lower_bound = l`, `var.upper_bound = u` | |
| `Add(expr, name)` | `add_linear_constraint(expr, name=name)` | |
| `RowConstraint(lb, ub, name)` + `SetCoefficient(v, a)` | `add_linear_constraint(lb=lb, ub=ub, expr=..., name=name)`, or `row.set_coefficient(v, a)` | keep both bounds |
| `Maximize(expr)`; `Objective().SetCoefficient` + `SetMaximization()` | `model.maximize(expr)`; `model.objective.set_linear_coefficient(v, c)`, `model.objective.is_maximize = True` | |
| `solver.Solve()` | `result = mathopt.solve(model, solver_type, params=...)` | |
| status `pywraplp.Solver.OPTIMAL` (an `int`) | `result.termination.reason == mathopt.TerminationReason.OPTIMAL` (an enum) | |
| `var.solution_value()` | `result.variable_values(var)` | raises with no solution |
| `Objective().Value()`, `Objective().BestBound()` | `result.objective_value()`, `result.dual_bound()` | |
| `row.dual_value()`, `var.reduced_cost()` | `result.dual_values(row)`, `result.reduced_costs(var)` | LP only |
| `SetTimeLimit(ms)` | `SolveParameters(time_limit=timedelta(milliseconds=ms))` | milliseconds vs `timedelta` |
| `MPSolverParameters` with `RELATIVE_MIP_GAP` | `SolveParameters(relative_gap_tolerance=...)` | |

Watch the defaults when you port a variable. `NumVar` and `IntVar` take both bounds every time.
MathOpt lets you leave them out, and a bound left out is infinite:

```text
MathOpt bounds left out: add_variable [-inf, inf], add_integer_variable [-inf, inf]
```

So a ported `NumVar(0, infinity, ...)` must keep its `lb=0`. Leave it out and the variable may go
negative.

Statuses map almost one to one. pywraplp's OPTIMAL, FEASIBLE, INFEASIBLE and UNBOUNDED have
reasons of the same names in `mathopt.TerminationReason`. MathOpt splits the rest more finely:
`INFEASIBLE_OR_UNBOUNDED`, `NO_SOLUTION_FOUND` (a limit stopped the search before any solution),
`IMPRECISE`, `NUMERICAL_ERROR` and `OTHER_ERROR`. Lesson 4.2.2 covers them.

The LP side ports just as directly. The LP relaxation, built in both APIs and solved by GLOP, gives
the same dual value on `cap` and the same reduced cost on `x`:

```text
pywraplp LP: objective 25.00, dual(cap) 1.4286, reduced cost(x) -0.4286
MathOpt LP:  objective 25.00, dual(cap) 1.4286, reduced cost(x) -0.4286
```

One behaviour does **not** carry over, and that is a good thing. Lesson 4.7.1 showed pywraplp
answering 0.0 for every value after an infeasible solve. MathOpt refuses:

```python
bad_result = mathopt.solve(bad_model, mathopt.SolverType.GSCIP)
try:
    bad_result.variable_values(m)
except ValueError as error:
```

```text
pywraplp infeasible: status 2, n.solution_value() = 0.0
MathOpt infeasible: INFEASIBLE, variable_values raised ValueError: No primal feasible solution available.
```

A ported script that forgot its status check used to print zeros. Now it stops with an error, so
the port can surface bugs the old script hid. Keep the status check anyway: an error in a nightly
job is better than a wrong report, but a clear message is better than both.

<!-- practice 1 -->

## MathOpt Keeps the Model Apart From the Solver

Here is the port of the inherited script, block by block against lesson 4.7.1's version:

```python
    model = mathopt.Model(name="selection")
    x = {}
    for p in portfolio.projects:
        x[p.project_id] = model.add_binary_variable(name="x_" + p.project_id)

    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")

    for p in portfolio.projects:
        if p.must_do:
            x[p.project_id].lower_bound = 1                       # must-do: fixed at 1
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name="parent_" + p.project_id)

    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g, members in groups.items():
        model.add_linear_constraint(sum(members) <= 1, name="alt_" + g)
```

- `BoolVar` became `add_binary_variable`, with the same names, so that a row or a variable can be
  found by the name it had before.
- The budget's `RowConstraint(-infinity, B)` plus a loop of `SetCoefficient` became one expression
  with `<=`. Its lower bound was $`-\infty`$, so nothing is lost. A ranged row would need
  `add_linear_constraint(lb=..., ub=..., expr=...)`.
- `SetBounds(1, 1)` on a binary became `lower_bound = 1`: a binary's upper bound is already 1.
- The parent and alternative rows keep their names, `parent_<id>` and `alt_<group>`.

The solve moved out of the model:

```python
    params = mathopt.SolveParameters(time_limit=datetime.timedelta(milliseconds=time_limit_ms),
                                     relative_gap_tolerance=relative_gap)
    result = quiet_solve(model, solver, params)
    reason = result.termination.reason
```

`quiet_solve` is `mathopt.solve` with standard output pointed at `/dev/null` for the call, the
course's way of keeping a stray line printed by the bundled HiGHS out of the output (it is in
`ported_selection.py`).

This split is the reason to port. A pywraplp model lives inside one solver object, so trying it on
SCIP, then CBC, then CP-SAT means three builds. A MathOpt model is built once and handed to each
solver in turn:

```python
model, x = build(small)
for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT):
    result = quiet_solve(model, solver, mathopt.SolveParameters(relative_gap_tolerance=0.0))
```

```text
HIGHS   OPTIMAL: value $25,336k, 20 funded
GSCIP   OPTIMAL: value $25,336k, 20 funded
CP_SAT  OPTIMAL: value $25,336k, 20 funded
```

The same $25,336k as the legacy script found on small in lesson 4.7.1, from three different
engines. MathOpt is also the API that lessons 4.2.1 to 4.3.5 build on, for incremental re-solves,
prioritized objectives and infeasibility analysis. Lesson 4.2.3 covers what changes between back
ends.

## A Port Is Proved by a Test: Same Value at Zero Gap, and Each Plan Allowed by the Other's Rules

What does "the same answer" mean? The obvious test compares the two optimal values. It needs two
refinements.

**First, two optimal plans can differ.** When several plans tie for best, two correct models, or
the same model on two solvers, may return different plans. So compare values, not plans. Then check
each plan against the *other* model's rules. A port that dropped a row can reach a higher value
with a plan the old model forbids, and this second check catches it even when a test instance
happens to give equal values. This program checks the rules directly from the data:

```python
def allowed(portfolio, funded) -> bool:
    """Does a plan keep every rule of the selection model? Checked by hand, not by a solver."""
    chosen = set(funded)
    if sum(portfolio.project(pid).capex for pid in chosen) > portfolio.capital_budget:
        return False
```

**Second, "optimal" has a tolerance.** Lesson 3.4.1 defined the relative MIP gap: a MIP solver
stops and reports OPTIMAL once its plan is within that fraction of the best bound. Here are the old
script and the port on three GridCap sizes, each first with its own default gap:

```python
for size, gap in (("tiny", None), ("small", None), ("medium", None), ("medium", 0.0)):
    portfolio = generate(size)
    status, old_value, old_plan, _ = solve_legacy(portfolio, relative_gap=gap)
    reason, new_value, new_plan, _ = solve_ported(portfolio, relative_gap=gap)
```

```text
pywraplp's default relative MIP gap: 0.0001
tiny   gap default: pywraplp OPTIMAL $3,627k | MathOpt OPTIMAL $3,627k | same value: True, same plan: True, each plan allowed: True
small  gap default: pywraplp OPTIMAL $25,336k | MathOpt OPTIMAL $25,336k | same value: True, same plan: True, each plan allowed: True
medium gap default: pywraplp OPTIMAL $229,740k | MathOpt OPTIMAL $229,745k | same value: False, same plan: False, each plan allowed: True
medium gap 0.0: pywraplp OPTIMAL $229,745k | MathOpt OPTIMAL $229,745k | same value: True, same plan: True, each plan allowed: True
```

On medium, both report OPTIMAL and the values differ by $5k. Is the port wrong? No. pywraplp
passes SCIP a relative gap of 0.0001 unless told otherwise, and $`5 / 229{,}745 \approx 0.00002`$ is
inside it: $229,740k is "optimal" by that standard. The MathOpt port left `relative_gap_tolerance`
at `None`. MathOpt's parameter documentation says the solver may stop at that gap only "when set",
so unset, SCIP keeps its own default, and SCIP's parameter list gives `limits/gap` a default of 0:
it stops only when the plan meets the bound. `default_gap.py` solves the port on medium with the
gap unset and with pywraplp's 0.0001, and prints the bound beside the plan:

```python
    result = quiet_solve(model, mathopt.SolverType.GSCIP,
                         mathopt.SolveParameters(relative_gap_tolerance=gap))
```

```text
relative_gap_tolerance None: OPTIMAL  plan $229,745k  bound $229,745k  gap 0.000000
relative_gap_tolerance 0.0001: OPTIMAL  plan $229,740k  bound $229,758k  gap 0.000077
```

Unset, SCIP ran until bound and plan met at $229,745k; given 0.0001 through MathOpt, it stopped at
pywraplp's $229,740k, with $18k still between plan and bound. So the $5k difference is the two
gaps, not the port. Both plans keep every rule. With the gap set to 0 in both, they agree on value
and plan.

So the test that proves a port, `test_the_port_reaches_the_legacy_value_and_plan_at_zero_gap` in
the module's tests, does three things:

1. **Fix the gap at 0 in both**, so that "optimal" means the same thing to both. Alternatively,
   compare the values within the larger of the two gaps.
2. **Compare values**, and compare plans only where the optimum is known to be unique.
3. **Check each plan against the other's rules.** The test also checks that both models have the
   same rows by name.

Run it on more than one instance. Tiny and small agree even at the default gap, so they would not
have shown the gap issue; it took the medium portfolio.

<!-- practice 2 -->

## The Model

The model is unchanged by the port: lesson 4.7.1's selection model, now with its MathOpt calls.

**Sets.** $`P`$, the projects; $`M \subseteq P`$, the must-do projects; $`C \subseteq P`$, the child
projects, each with a parent $`p(c)`$; $`\mathcal{G}`$, the alternative groups.

**Parameters.** $`v_i`$, the value of project $`i`$ ($k); $`c_i`$, its capital cost ($k); $`B`$, the
capital budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for $`i \in P`$ (`add_binary_variable`), with
$`x_i = 1`$ for $`i \in M`$ (`lower_bound = 1`).

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must-do, as a lower bound)} \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

The row names are the same in both versions: `budget`, `parent_<child id>`, `alt_<group id>`.

## Summary

- **Every pywraplp call has a MathOpt counterpart.** Variables, rows and the objective map one to
  one. SCIP is `SolverType.GSCIP`, time limits become a `timedelta`, and bounds left out of
  `add_variable` are infinite. MathOpt raises where pywraplp answered 0.0.
- **MathOpt keeps the model apart from the solver.** One model is built once and solved by HiGHS,
  SCIP and CP-SAT: all three found $25,336k on small.
- **A port is proved by a test.** Fix the gap at 0 in both, compare values, and check each plan
  against the other's rules. At default gaps the medium portfolio gave $229,740k and $229,745k,
  both OPTIMAL and both correct.

## Reference

| Check in a port test | Catches |
| --- | --- |
| same rows by name, same variable count | a dropped or duplicated rule |
| same optimal value at gap 0 | a changed coefficient, bound or sense |
| each plan allowed by the other's rules | a rule weakened or strengthened in a way the values hide |
| more than one instance, including a large one | differences that only show when the search is long |

| pywraplp default | MathOpt equivalent |
| --- | --- |
| relative MIP gap 0.0001 (`MPSolverParameters`) | `SolveParameters(relative_gap_tolerance=1e-4)` |
| `SetTimeLimit(60_000)` | `SolveParameters(time_limit=timedelta(seconds=60))` |
| `NumVar(0, infinity)` | `add_variable(lb=0)`; leaving `lb` out allows negatives |

**Further reading:** [Solving an LP Problem (OR-Tools)](https://developers.google.com/optimization/lp/lp_example) and [Solving a MIP Problem (OR-Tools)](https://developers.google.com/optimization/mip/mip_example) (the pywraplp side of the map, call by call); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt drives, among them GLOP, PDLP, CP-SAT, SCIP and HiGHS, and its incremental solving and multiple objectives); [MPSolver (OR-Tools)](https://developers.google.com/optimization/lp/mpsolver) (the wrapper's own page and its time limit in milliseconds); [OR-Tools sample simple_mip_program.py](https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/simple_mip_program.py) (the pywraplp program ported in the first section); [MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (the same model as a MathOpt program, the target shape of the port); [MathOpt parameters, `parameters.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/parameters.proto) (`relative_gap_tolerance`, applied only when set); [SCIP parameters](https://www.scipopt.org/doc/html/PARAMETERS.php) (`limits/gap`, default 0).

## Challenges

1. Port `coefficient_style.py` from lesson 4.7.1 to MathOpt, keeping its ranged rows. Check the
   objective against 260 and decide which `add_linear_constraint` form keeps both bounds.
2. In `compare_ports.py`, set the gap to 0.001 in both. Predict which sizes still agree on value,
   then run it.
3. Drop the `alt_` rows from the port. Which of the three checks in the port test fails first, on
   which size?

## Design Note: Keep the Old Code Until the Test Is Green, Then Delete It

Keep the legacy builder runnable next to the port until the agreement test passes on every
instance you care about, including the largest one you can afford. Then delete the legacy builder
and keep the test's *data*: the instances and the values both versions reached at gap 0. A later
change to the MathOpt model then has a fixed reference to meet, with no pywraplp left in the code.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**side_by_side.py.** The OR-Tools first example in pywraplp and in MathOpt, its LP relaxation's
duals in both, and an infeasible model read in both (*Every pywraplp Call Has a MathOpt
Counterpart*). *Try:* Leave out `lb=0` on `mx`. Predict whether the MathOpt answer changes.

- Program: [side_by_side.py](src/side_by_side.py)

**one_model_three_solvers.py and ported_selection.py.** The ported GridCap selection model, built
once and solved by HiGHS, SCIP and CP-SAT (*MathOpt Keeps the Model Apart From the Solver*).
*Try:* Add `mathopt.SolverType.GLOP` to the loop. Predict the value and whether it is a plan.

- Program: [one_model_three_solvers.py](src/one_model_three_solvers.py)
- Library: [ported_selection.py](src/ported_selection.py)

**compare_ports.py.** The legacy script and the port on tiny, small and medium, at default gaps
and at gap 0 (*A Port Is Proved by a Test*). *Try:* Change the port's budget row to `<=` the budget
plus 100. Predict which of the three checks reports it, and on which size.

- Program: [compare_ports.py](src/compare_ports.py)

**default_gap.py.** The port on medium with the gap unset and at 0.0001, printing plan, bound and
gap (*A Port Is Proved by a Test*). *Try:* Pass `relative_gap_tolerance=0.001`. Predict whether the
plan's value drops below $229,740k.

- Program: [default_gap.py](src/default_gap.py)
