# 4.7.1 Reading pywraplp Code

GridCap's planning team inherits a script from a contractor. It chooses which projects to fund
under the capital budget, and it has worked for years, but nobody on the team has read it closely.
It does not use MathOpt, the API this course has used since section 1. It imports
`ortools.linear_solver.pywraplp`, OR-Tools' older **linear solver wrapper**. The OR-Tools
documentation calls it MPSolver, and its pages on LP, MIP, assignment and bin packing are written
with it. A lot of existing code is too, so you have to be able to read it before you can trust it,
fix it or port it (lesson 4.7.2 does the port).

This lesson teaches the wrapper the way the OR-Tools pages "Solving an LP Problem" and "Solving a
MIP Problem" do: create a solver, add variables, add rows, set the objective, solve, and read the
status before the values. It ends by reading the inherited script line by line against its model.
GridCap is a fictional utility's portfolio, and the script was written for this course. There are
four rules, one per heading.

## A pywraplp Program Picks Its Back End by Name, and the Solver Holds the Model

Every pywraplp program starts the same way:

```python
solver = pywraplp.Solver.CreateSolver(backend)        # the solver object also holds the model
```

`CreateSolver` takes the name of a **back end**: the engine that will do the actual solving. GLOP
is Google's LP solver and SCIP is an open-source MIP solver. If the name is unknown, or that back
end was not built into this copy of OR-Tools, or it needs a licence that is missing,
`CreateSolver` returns `None` and raises no error. So the OR-Tools samples follow it with
`if not solver: return`. This program asks for each name in the course's runner image:

```python
for name in ("GLOP", "PDLP", "CLP", "SCIP", "CBC", "SAT", "HIGHS", "GUROBI", "XPRESS", "CPLEX", "GLPK"):
    solver = pywraplp.Solver.CreateSolver(name)
    if solver is None:
        print(f"{name:7} None (not available here)")
    else:
        kind = "MIP" if solver.IsMip() else "LP "
        print(f"{name:7} {kind}  {solver.SolverVersion()}")
```

```text
GLOP    LP   Glop solver v9.15.6755
PDLP    LP   PDLP Solver
CLP     LP   Clp 1.17.10
SCIP    MIP  SCIP 10.0.0 [LP solver: SoPlex 8.0.0]
CBC     MIP  Cbc 2.10.12
SAT     MIP  CP-SAT solver v9.15.6755
HIGHS   MIP  PDLP Solver
GUROBI  None (not available here)
XPRESS  None (not available here)
CPLEX   None (not available here)
GLPK    None (not available here)
```

Three things to read in it:

- **The name decides LP or MIP.** `IsMip()` says whether the back end handles integer variables.
  GLOP, PDLP and CLP are LP solvers. SCIP, CBC, SAT (CP-SAT) and HIGHS solve MIPs. The next
  section shows what happens to a script that creates `"GLOP"` and then adds integer variables.
- **Commercial back ends are names too.** Gurobi, Xpress and CPLEX are reachable through the same
  call when their libraries and licences are installed. Here they are not, so the call returns
  `None`, and OR-Tools logs a warning about the missing library on standard error.
- **`SolverVersion()` is a label, and it can be wrong.** For `"HIGHS"`, OR-Tools 9.15 prints
  "PDLP Solver", the label of a different back end, and the two rows disagree on `IsMip()`: PDLP is
  an LP solver, while the `"HIGHS"` solver says it handles integers. If you need to know which back
  end ran, look at the name you passed in.

The deeper point is in the comment on the first line: **in pywraplp, the solver object is the
model.** Variables and rows are created by methods of `solver`, and they belong to it. To try the
same model on another back end, you build it again in a new solver object. Lesson 4.7.2 shows
that MathOpt splits these two jobs: a `Model` holds the variables and rows, and the solver is named
only when you call `solve`.

## Variables, Rows and the Objective Come From the Solver, in Two Styles

Lesson 1.1.3 solved this small model with MathOpt (it is the model of the OR-Tools page "Solving a
MIP Problem"):

```math
\max\; x + 10y \quad \text{s.t.}\quad x + 7y \le 17.5,\quad x \le 3.5,\quad x, y \ge 0
```

Here it is in pywraplp, adapted from the OR-Tools samples `simple_lp_program.py` and
`simple_mip_program.py`. It is built three times: with continuous variables solved by GLOP, with
integer variables solved by SCIP, and with integer variables handed to GLOP:

```python
    infinity = solver.infinity()
    if integer:
        x = solver.IntVar(0.0, infinity, "x")             # integer, 0 <= x
        y = solver.IntVar(0.0, infinity, "y")
    else:
        x = solver.NumVar(0.0, infinity, "x")             # continuous, 0 <= x
        y = solver.NumVar(0.0, infinity, "y")
    solver.Add(x + 7 * y <= 17.5, "cap")
    solver.Add(x <= 3.5, "x_max")
    solver.Maximize(x + 10 * y)
```

```text
GLOP, continuous x and y: 2 variables, 2 constraints, status 0, IsMip() False
  objective = 25.00, x = 0.00, y = 2.50
SCIP, integer x and y: 2 variables, 2 constraints, status 0, IsMip() True
  objective = 23.00, x = 3.00, y = 2.00
  best bound = 23.00
GLOP, integer x and y: 2 variables, 2 constraints, status 0, IsMip() False
  objective = 25.00, x = 0.00, y = 2.50
  best bound = -inf
```

The first two are the answers lesson 1.1.3 found: 25 for the LP and 23 for the MIP. The third is
the trap the back-end table warned about. `IntVar` asked for whole numbers, GLOP returned
$`y = 2.5`$ with status OPTIMAL, and nothing complained. An LP solver solves the LP relaxation,
whatever the variables were declared as. (Its "best bound" of $`-\infty`$ is simply not a MIP
bound: GLOP never computes one.) When you read a script, check that the back end's name matches
the variables.

The calls map one to one onto the parts of a model:

| Part of the model | pywraplp call |
| --- | --- |
| continuous variable, $`l \le x \le u`$ | `solver.NumVar(l, u, name)` |
| integer variable | `solver.IntVar(l, u, name)` |
| binary variable, $`x \in \{0, 1\}`$ | `solver.BoolVar(name)`, the same as `IntVar(0, 1, name)` |
| no bound | `solver.infinity()`, or `-solver.infinity()` below |
| a row written as an expression | `solver.Add(expr <= b, name)`; `>=` and `==` work too |
| objective written as an expression | `solver.Maximize(expr)` or `solver.Minimize(expr)` |

**Every variable is created with its bounds**, so a reader finds the domain at the creation line:
`NumVar(0.0, infinity, "x")` is $`x \ge 0`$, continuous. Names are optional, but they cost
nothing and are what you search for in an exported model, so give every row one.

Older scripts, and the OR-Tools sample `mip_var_array.py`, use a second style, which builds rows
**coefficient by coefficient**. That suits data held in a matrix, and you will meet it often:

```python
for i, row in enumerate(COEFFS):
    constraint = solver.RowConstraint(0, BOUNDS[i], f"row{i}")     # 0 <= ... <= BOUNDS[i]
    for j, a in enumerate(row):
        constraint.SetCoefficient(x[j], a)

objective = solver.Objective()
for j, c in enumerate(OBJ):
    objective.SetCoefficient(x[j], c)
objective.SetMaximization()
```

`RowConstraint(lb, ub, name)` creates an empty row with a lower and an upper bound,
$`lb \le \sum_j a_j x_j \le ub`$, and `SetCoefficient` fills in one $`a_j`$ at a time. A
coefficient that is never set is 0. The objective works the same way: `solver.Objective()` returns
it, `SetCoefficient` fills it, and `SetMaximization()` (or `SetMinimization()`) sets its sense.

Notice the 0 in `RowConstraint(0, BOUNDS[i], ...)`. Every row of this model is **ranged**: it has a
lower bound as well as an upper one. Reading the code fast, you would write the model as four
"$`\le`$" rows, but the solver received eight inequalities. The quickest way to see what a solver
really holds is to ask it for the model as text. `ExportModelAsLpFormat(False)` writes it in **LP
format**, a plain-text format for models that most solvers can read. The program prints it before
solving:

```python
print(solver.ExportModelAsLpFormat(False))
```

```text
Maximize
 Obj: +7 x0 +8 x1 +2 x2 +9 x3 +6 x4 
Subject to
 row0_rhs: +5 x0 +7 x1 +9 x2 +2 x3 +1 x4  <= 250
 row0_lhs: +5 x0 +7 x1 +9 x2 +2 x3 +1 x4  >= 0
 row1_rhs: +18 x0 +4 x1 -9 x2 +10 x3 +12 x4  <= 285
 row1_lhs: +18 x0 +4 x1 -9 x2 +10 x3 +12 x4  >= 0
 row2_rhs: +4 x0 +7 x1 +3 x2 +8 x3 +5 x4  <= 211
 row2_lhs: +4 x0 +7 x1 +3 x2 +8 x3 +5 x4  >= 0
 row3_rhs: +5 x0 +13 x1 +16 x2 +3 x3 -7 x4  <= 315
 row3_lhs: +5 x0 +13 x1 +16 x2 +3 x3 -7 x4  >= 0
```

That is the export's objective and its eight inequalities, two per row for `row0` to `row3`; the
export also prints a header, the variables' bounds and the list of integer variables, left out
here. The exporter writes each ranged row as two lines, `_rhs` for the upper bound and `_lhs` for the
lower one. In the answer below no lower bound is binding: at the optimum every row's activity (its
left-hand side, evaluated at the solution) is well above 0. `row1` has a $`-9`$,
though, so some other plan could push its activity below 0, and the hidden lower bound would then
cut that plan off. When you port or rewrite a coefficient-style script, carry both bounds of every
`RowConstraint`. A row with no lower bound is written `RowConstraint(-solver.infinity(), ub, name)`.

```text
objective = 260
  x0 = 8, x1 = 21, x2 = 0, x3 = 2, x4 = 3
  row0: 0 <= 194 <= 250
  row1: 0 <= 284 <= 285
  row2: 0 <= 210 <= 211
  row3: 0 <= 298 <= 315
```

The program printed these activities by reading the model back. `solver.constraints()` lists the
rows, and each row answers `name()`, `lb()`, `ub()` and `GetCoefficient(var)`. That is how to
inspect a pywraplp model you did not write.

<!-- practice 1 -->

## Solve Returns an Integer Status, and Values Exist Only When It Says So

`solver.Solve()` returns a **status**, and in pywraplp the status is a plain integer. The class
gives the integers names:

```text
status codes: 0 OPTIMAL, 1 FEASIBLE, 2 INFEASIBLE, 3 UNBOUNDED, 4 ABNORMAL, 5 MODEL_INVALID, 6 NOT_SOLVED
```

- **OPTIMAL (0):** a solution was found and proved best, within the MIP gap tolerance (lesson
  3.4.1 defines the gap; lesson 4.7.2 shows why the tolerance matters).
- **FEASIBLE (1):** a solution was found, but a limit, such as the time limit, stopped the search
  before it was proved best.
- **INFEASIBLE (2)** and **UNBOUNDED (3):** no plan satisfies the rows, or the objective can improve
  without end.
- **ABNORMAL (4), MODEL_INVALID (5), NOT_SOLVED (6):** the back end failed, the model is malformed
  or `Solve` has not run.

That is why the samples print `status 0` and compare the result with a name:
`if status == pywraplp.Solver.OPTIMAL:`. A script that prints the raw status prints a number, and
`2` tells nobody anything.

Now the trap. Here is a model that no values can satisfy, $`x + y \ge 20`$ with $`x \le 3`$ and
$`y \le 10`$, and what the solver says when it is asked for values anyway:

```python
solver = pywraplp.Solver.CreateSolver("SCIP")
x = solver.IntVar(0, 3, "x")
y = solver.IntVar(0, 10, "y")
solver.Add(x + y >= 20, "need")
solver.Minimize(x + y)
status = solver.Solve()
print(f"Solve() returned {status!r} ({NAMES[status]})")
print(f"x.solution_value() = {x.solution_value()}, y.solution_value() = {y.solution_value()}, "
      f"Objective().Value() = {solver.Objective().Value()}")
```

```text
Solve() returned 2 (INFEASIBLE)
x.solution_value() = 0.0, y.solution_value() = 0.0, Objective().Value() = 0.0
```

**No exception.** The model is infeasible, yet `solution_value()` answers 0.0 for each variable and
the objective reads 0.0. A script that only reads values carries on, and a report built from them
says "fund nothing, value $0". An all-zero
plan is often a believable answer, so nobody notices. MathOpt raises a `ValueError` in the same
situation (lesson 4.7.2). In pywraplp, **read the status first, and read values only after OPTIMAL
or FEASIBLE.**

The other numbers a solved pywraplp model reports:

| Question | pywraplp call |
| --- | --- |
| objective value of the solution | `solver.Objective().Value()` |
| best bound (MIP) | `solver.Objective().BestBound()` |
| a variable's value | `var.solution_value()` |
| an LP row's dual value, a variable's reduced cost | `row.dual_value()`, `var.reduced_cost()` (lesson 2.3.3 defines them) |
| work done | `solver.wall_time()` (milliseconds), `solver.iterations()`, `solver.nodes()` (MIP) |
| time limit | `solver.SetTimeLimit(ms)` (milliseconds), before `Solve` |

The best bound printed above, 23.00, equals the objective. That is what "proved optimal" means
for a MIP: no plan can beat the bound, and the plan found reaches it.

<!-- practice 2 -->

## A Legacy Script Reads Line by Line Against Its Model

Here is the inherited script. Read it the way you would in a code review: for each block, say
which part of the model it builds.

```python
    solver = pywraplp.Solver.CreateSolver(backend)
    solver.SetTimeLimit(time_limit_ms)                    # milliseconds

    x = {}
    for p in portfolio.projects:
        x[p.project_id] = solver.BoolVar("x_" + p.project_id)

    budget = solver.RowConstraint(-solver.infinity(), portfolio.capital_budget, "budget")
    for p in portfolio.projects:
        budget.SetCoefficient(x[p.project_id], p.capex)

    for p in portfolio.projects:
        if p.must_do:
            x[p.project_id].SetBounds(1, 1)               # must-do: fixed at 1
        if p.parent:
            solver.Add(x[p.project_id] <= x[p.parent], "parent_" + p.project_id)

    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g, members in groups.items():
        solver.Add(solver.Sum(members) <= 1, "alt_" + g)

    objective = solver.Objective()
    for p in portfolio.projects:
        objective.SetCoefficient(x[p.project_id], p.value)
    objective.SetMaximization()
```

Block by block:

1. `SetTimeLimit(60_000)` is in **milliseconds**: a minute, not 16 hours. MathOpt takes a
   `timedelta`, and a port that passes the number straight through as seconds changes the limit a
   thousandfold.
2. `BoolVar` makes one binary per project: $`x_i \in \{0, 1\}`$, fund project $`i`$ or not.
3. The budget row is built coefficient by coefficient, with $`-\infty`$ as its lower bound:
   $`\sum_i c_i x_i \le B`$.
4. A **must-do** project is not a row. `SetBounds(1, 1)` fixes the variable's bounds to $`[1, 1]`$.
   That is the same rule as the row $`x_i = 1`$, but it does not appear in `solver.constraints()`,
   so a reader who lists the rows to understand the model misses it.
5. A child project needs its parent: $`x_c \le x_{p(c)}`$, one named row per child.
6. Alternatives: at most one project per group, $`\sum_{i \in g} x_i \le 1`$. `solver.Sum(list)`
   adds up a list of variables, like Python's `sum`.
7. The objective: maximize total value, coefficient by coefficient.

The script then solves, keeps the plan only when the status is OPTIMAL or FEASIBLE, and returns
the funded projects:

```python
    status, value, funded, solver = solve_legacy(portfolio)
```

```text
tiny: OPTIMAL, 8 variables, 3 rows, value $3,627k, 4 funded
  funded: P001 P002 P005 P006
  rows: budget parent_P004 alt_G006
small: OPTIMAL, 40 variables, 5 rows, value $25,336k, 20 funded
```

The rows the solver lists for tiny are the budget, one parent row and one alternative row. P002, a
must-do project, has no row of its own, exactly as block 4 predicts. The small portfolio's $25,336k
is the plan to check any port against: same data, same model, same value. (Lesson 6.3.2, later in
the course, starts its multiple-knapsack model from this same selection.) Now the script has a model you can write down, and
lesson 4.7.2 can port it with something to check the port against.

## The Model

The selection model the inherited script builds (lesson 1.1.1's model), with each part's pywraplp
call.

**Sets.** $`P`$, the projects; $`M \subseteq P`$, the must-do projects; $`C \subseteq P`$, the child
projects, each with a parent $`p(c)`$; $`\mathcal{G}`$, the alternative groups, each a set of
projects.

**Parameters.** $`v_i`$, the value (NPV) of project $`i`$ ($k); $`c_i`$, its capital cost ($k);
$`B`$, the capital budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for $`i \in P`$: project $`i`$ is funded. In code,
`BoolVar("x_" + id)`; for $`i \in M`$, `SetBounds(1, 1)` narrows the domain to $`\{1\}`$.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must-do: a variable bound, not a row)} \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

| Label | Name in the solver | Built with |
| --- | --- | --- |
| budget | `budget` | `RowConstraint(-infinity, B)` + `SetCoefficient` |
| must-do | none | `SetBounds(1, 1)` on the variable |
| parent$`_c`$ | `parent_<child id>` | `solver.Add(x[c] <= x[parent])` |
| alt$`_g`$ | `alt_<group id>` | `solver.Add(solver.Sum(members) <= 1)` |

## Summary

- **A pywraplp program picks its back end by name, and the solver holds the model.**
  `CreateSolver(name)` returns `None` for a back end that is missing, and the name decides LP or
  MIP. Variables and rows belong to that solver object.
- **Variables, rows and the objective come from the solver, in two styles.** `NumVar`, `IntVar`
  and `BoolVar` take their bounds; rows come from `Add(expr)` or from `RowConstraint(lb, ub)` plus
  `SetCoefficient`. A `RowConstraint` with a finite lower bound is a ranged row, and
  `ExportModelAsLpFormat` shows what the solver really holds.
- **Solve returns an integer status, and values exist only when it says so.** After INFEASIBLE,
  `solution_value()` still answers 0.0, with no exception.
- **A legacy script reads line by line against its model.** Map each block to a set, a variable, a
  row or the objective, and look for rules hidden in variable bounds.

## Reference

| pywraplp | Meaning |
| --- | --- |
| `pywraplp.Solver.CreateSolver("SCIP")` | a solver, with its own empty model, or `None` |
| `NumVar(l, u, n)` / `IntVar(l, u, n)` / `BoolVar(n)` | continuous / integer / binary variable |
| `var.SetBounds(l, u)`, `var.lb()`, `var.ub()` | change or read a variable's bounds |
| `Add(expr, name)` | a row from an expression |
| `RowConstraint(lb, ub, name)`, `row.SetCoefficient(v, a)` | a row from coefficients; $`lb \le \cdot \le ub`$ |
| `Objective().SetCoefficient(v, c)`, `SetMaximization()` | objective from coefficients |
| `Maximize(expr)`, `Minimize(expr)` | objective from an expression |
| `Solve()` | an `int` status: 0 OPTIMAL, 1 FEASIBLE, 2 INFEASIBLE, 3 UNBOUNDED, 4 ABNORMAL, 5 MODEL_INVALID, 6 NOT_SOLVED |
| `var.solution_value()`, `Objective().Value()`, `Objective().BestBound()` | the answer; meaningless unless the status is 0 or 1 |
| `constraints()`, `row.name()`, `row.lb()`, `row.ub()`, `row.GetCoefficient(v)` | read a model back |
| `ExportModelAsLpFormat(False)` | the model as LP-format text |
| `SetTimeLimit(ms)` | a time limit, in milliseconds |

**Further reading:** [Solving an LP Problem (OR-Tools)](https://developers.google.com/optimization/lp/lp_example) (the pywraplp workflow, step by step, on a two-variable LP solved by GLOP, with the wall time and iterations it reports); [Solving a MIP Problem (OR-Tools)](https://developers.google.com/optimization/mip/mip_example) (the model of this lesson's second section, with integer variables, its LP relaxation and the node count); [MPSolver (OR-Tools)](https://developers.google.com/optimization/lp/mpsolver) (the linear solver wrapper's page: GLOP for LPs, SCIP for MIPs, and `set_time_limit`); [OR-Tools sample simple_lp_program.py](https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/simple_lp_program.py) and [simple_mip_program.py](https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/simple_mip_program.py) (the programs adapted above; the MIP sample asks for the `"SAT"` back end); [OR-Tools sample mip_var_array.py](https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/mip_var_array.py) (the coefficient style, `RowConstraint` and `SetCoefficient`, with the expression style in comments).

## Challenges

1. Change the third run of `first_wrapper.py` to `"CBC"`. Predict the objective and `IsMip()`, then
   run it.
2. In `coefficient_style.py`, change one coefficient so that a plan with a negative row activity
   becomes the best one if the lower bound is dropped. Does the ranged row stop it?
3. The legacy script fixes must-do projects with `SetBounds`. Rewrite that block as a named row.
   What changes in `solver.constraints()`, and what stays the same in the answer?

## Design Note: A Status Check Belongs Next to Every Read

pywraplp returns values whatever the status, so the check cannot be left to the caller's memory.
Keep one small function that turns a solved solver into an answer, or into nothing: it reads the
status first and returns no plan unless the status is OPTIMAL or FEASIBLE. Every report then goes
through it. The legacy script does this already: its early `return status, None, [], solver` is
the most valuable line in it. Practice 2 builds that function.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**solver_names.py.** Asks `CreateSolver` for each back-end name and prints what it got (*A pywraplp
Program Picks Its Back End by Name*). *Try:* Add `"CP-SAT"` and `"BOP"` to the list. Predict which
of them come back as MIP solvers.

- Program: [solver_names.py](src/solver_names.py)

**first_wrapper.py.** The OR-Tools first LP and MIP examples in pywraplp, with GLOP and SCIP, and
integer variables handed to GLOP (*Variables, Rows and the Objective Come From the Solver*). *Try:* Change `17.5` to `21` and predict
both objectives before you run it.

- Program: [first_wrapper.py](src/first_wrapper.py)

**coefficient_style.py.** The `mip_var_array.py` example: rows from `RowConstraint` and
`SetCoefficient`, the LP-format export, and the rows read back (*Variables, Rows and the Objective
Come From the Solver*). *Try:* Change `RowConstraint(0, ...)` to `RowConstraint(-solver.infinity(), ...)`.
Predict what changes in the export and in the answer.

- Program: [coefficient_style.py](src/coefficient_style.py)

**status_codes.py.** The status names, and an infeasible model whose values still read 0.0
(*Solve Returns an Integer Status*). *Try:* Raise `y`'s upper bound to 17. Predict the status and
the values.

- Program: [status_codes.py](src/status_codes.py)

**run_legacy.py and legacy_selection.py.** The inherited GridCap selection script, run on tiny and
small (*A Legacy Script Reads Line by Line Against Its Model*). *Try:* Pass `backend="CBC"` in
`run_legacy.py`. Predict whether the values change.

- Program: [run_legacy.py](src/run_legacy.py)
- Library: [legacy_selection.py](src/legacy_selection.py)
