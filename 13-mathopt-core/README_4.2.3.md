# 4.2.3 Switching Solvers: HiGHS, SCIP, CP-SAT, GLOP, Gurobi

GridCap's planning service runs the selection model on HiGHS. A colleague asks for a second opinion
from SCIP before a board meeting, finance wants the LP budget prices from GLOP, and the vendor
evaluation needs a Gurobi run. With MathOpt that is the same model handed to four solvers, and the
code change is one argument. What changes with the solver is everything around that argument: which
models it accepts, what it returns, and how much of its answer you can trust.

This lesson hands one GridCap model to every solver OR-Tools 9.15 ships, as an LP and as a MILP, and
reads what comes back. The solver names follow MathOpt's `SolverType`: `GLOP` (Google's simplex LP
solver), `PDLP` (Google's first-order LP solver, lesson 2.4.1), `HIGHS` (the open-source LP and MIP
solver this course uses by default), `GSCIP` (SCIP, an open-source MIP solver, through Google's
wrapper) and `CP_SAT` (Google's constraint-programming solver over integers, taught from lesson 4.4.1). GridCap is a
fictional portfolio.

## The Model

Both models are GridCap small's project-selection model of lesson 4.2.1.

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years; $`M \subseteq P`$ the must-do
projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$ the child projects, with parent
$`p(c)`$.

**Parameters.** $`v_i`$, the NPV of project $`i`$ at its earliest start ($k, an integer);
$`c_{i,y}`$, what it spends in year $`y`$ ($k, an integer); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** MILP: $`x_i \in \{0, 1\}`$ for every $`i \in P`$. LP relaxation: $`0 \le x_i \le 1`$.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(needs}_c) \\
\sum_{i \in P} c_{i,y}\, x_i &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The rows are named `must_P002`, `alt_G006`, `needs_P004` and `budget_2027` in `selection.py`.

## The Solver Is an Argument to solve, Never Part of the Model

`selection.build` returns a model that names no solver. The program builds both versions once and
hands each to all five solvers, catching the solves that are refused:

```python
small = generate("small")
models = {"LP": build(small, integer=False), "MILP": build(small)}


def attempt(kind: str, solver: mathopt.SolverType) -> str:
    sel = models[kind]
    try:
        result = solve(sel.model, solver)
    except Exception as error:          # a refusal; lesson 4.2.4 reads its message properly
        return "refused: " + str(error.__context__ or error).split(" [")[0]
    funded = plan(sel, result)
    extras = [name for name, has in (("duals", result.has_dual_feasible_solution()),
                                      ("basis", result.has_basis())) if has]
    count = f"  funded {len(funded)}" if kind == "MILP" else ""
    return (f"{result.termination.reason.name} {result.objective_value():,.1f}"
            f"{count}  {' + '.join(extras) or 'no duals'}")


for kind in models:
    print(kind)
    for solver in (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT):
        print(f"  {solver.name:<7} {attempt(kind, solver)}")
```

```text
LP
  GLOP    OPTIMAL 23,669.5  duals + basis
  PDLP    OPTIMAL 23,669.5  duals
  HIGHS   OPTIMAL 23,669.5  duals + basis
  GSCIP   OPTIMAL 23,669.5  no duals
  CP_SAT  OPTIMAL 22,532.0  no duals
MILP
  GLOP    refused: Glop does not support integer variables
  PDLP    refused: PDLP does not support integer variables
  HIGHS   OPTIMAL 22,532.0  funded 25  no duals
  GSCIP   OPTIMAL 22,532.0  funded 25  no duals
  CP_SAT  OPTIMAL 22,532.0  funded 25  no duals
the three MILP solvers fund the same projects: True
```

The `solve` here is `selection.solve`, which calls `mathopt.solve` and keeps the bundled HiGHS's
stray output off the screen (lesson 4.2.1). The solver went in as a value, `S.GLOP` through `S.CP_SAT`,
and nothing else in the program changed. Several OR-Tools samples (`time_indexed_scheduling.py`,
`facility_location.py`, `writing_seminar.py`) do the same at the command line: their solver is a flag
whose type is `SolverType`, so a run can switch solvers without an edit. That is the pattern to
copy: the model builder knows nothing of solvers, and the solver is configuration.

The grid answers four questions about the solvers, one per section below: which model types each
accepts, what each returns, where CP-SAT's answer goes wrong, and which solvers you can use at all.

## Each Solver Accepts Only the Model Types It Can Solve, and Says So Before Solving

The MILP column shows the first rule: **GLOP and PDLP solve LPs only**, and refuse a model with an
integer variable. The refusal is an exception from `mathopt.solve`, raised before any work, never a
status; in OR-Tools 9.15 its message is hidden on the exception's `__context__` (lesson 4.2.4). It is
a good refusal: it stops you from getting an LP answer to a yes/no question.

The LP column shows the second: **only some solvers return dual values.** GLOP and HiGHS return duals
and a basis (both use simplex); PDLP returns duals but no basis (it does not use simplex); SCIP
solves the LP and returns no duals at all. The `SolverType` docstring says it plainly for SCIP: no
dual data for LPs, prefer GLOP. So "read the budget's shadow price" (lesson 4.2.2) is a job for GLOP or
HiGHS, and a program that switches solver must check `has_dual_feasible_solution()` rather than assume.

The three MILP solvers agree: the same value, $22,532k, and the same 25 projects. Agreement on a
small model is a cheap and strong test of a model; when a solver change moves the objective, the first
suspects are a tolerance (lesson 2.4.1) and a model feature one solver reads differently, which is
what CP-SAT does in the LP column.

What each solver takes, from the `SolverType` docstrings and the runs above:

| Solver | LP | MILP | Duals on an LP | Notes |
| --- | --- | --- | --- | --- |
| GLOP | yes | refused | yes, with basis | primal and dual simplex |
| PDLP | yes | refused | yes, no basis | first-order; large LPs, lower accuracy |
| HiGHS | yes | yes | yes, with basis | the course default |
| SCIP (`GSCIP`) | yes | yes | no | also nonconvex integer quadratics |
| CP-SAT | see next section | yes, all variables integer and bounded | no | lesson 4.4.1 |

## CP-SAT Needs Integers, and Rounds a Continuous Model Without Warning

The LP column's last line is wrong. CP-SAT reported `OPTIMAL 22,532.0` for the LP relaxation, whose
optimum the other four agree is $23,669.5k. It solved a different model. CP-SAT works over integers
only; the CP-SAT page of the OR-Tools documentation says to scale any non-integer terms to integers
before using it, and MathOpt's `SolverType` docstring calls its handling of continuous variables
experimental support to "rescale and discretize". The program shows what that did here:

```python
lp = build(generate("small"), integer=False)          # every x[i] continuous in [0, 1]
for solver in (S.GLOP, S.HIGHS, S.CP_SAT):
    result = solve(lp.model, solver)
    fractional = sum(1 for v in lp.x.values() if 1e-6 < result.variable_values(v) < 1 - 1e-6)
    print(f"{solver.name:<6} {result.termination.reason.name} {result.objective_value():,.1f}"
          f"  fractional x: {fractional}")
```

```text
GLOP   OPTIMAL 23,669.5  fractional x: 4
HIGHS  OPTIMAL 23,669.5  fractional x: 4
CP_SAT OPTIMAL 22,532.0  fractional x: 0
```

The LP's optimum funds four projects in part. CP-SAT returned no fractions at all: every $`x_i`$ came
back 0 or 1, so it answered the MILP, and called that the optimum of the LP. A model with one
continuous variable shows the same thing on a smaller scale:

```python
model = mathopt.Model(name="one-continuous")
a = model.add_variable(lb=0, ub=10, name="a")              # continuous
b = model.add_integer_variable(lb=0, ub=10, name="b")
model.add_linear_constraint(0.37 * a + 1.13 * b <= 7.71, name="cap")
model.maximize(1.01 * a + 2.9 * b)
for solver in (S.HIGHS, S.CP_SAT):
    result = solve(model, solver)
    print(f"{solver.name:<6} {result.termination.reason.name} {result.objective_value():.4f}"
          f"  a = {result.variable_values(a):.4f}  b = {result.variable_values(b):g}")
```

```text
HIGHS  OPTIMAL 20.3078  a = 8.6216  b = 4
CP_SAT OPTIMAL 19.6800  a = 8.0000  b = 4
```

HiGHS sets the continuous `a` to 8.6216, where the `cap` row is tight. CP-SAT stopped at `a = 8`, a
whole number, and still said `OPTIMAL`. Its value is a feasible plan, so nothing breaks; it is just not
the optimum of the model you wrote, and no field of the result says so. The rule that follows: **hand
CP-SAT only models whose variables are all integer**, with integer data where you can (GridCap's
money is in whole $k for that reason), and send anything with a continuous variable to HiGHS or SCIP.
Lessons 4.4.1 to 4.4.4 teach CP-SAT in its own API, where integers are the only kind of variable.

<!-- practice 1 -->

## Five Solvers Are Built Into the pip Package, and Gurobi Needs Its Own Library and License

`SolverType` lists more solvers than the OR-Tools wheel contains. Asking for each one shows which are
there:

```python
print("compiled into this OR-Tools:")
for solver in S:
    if solver in (S.GUROBI,):
        continue
    try:
        mathopt.solve(mathopt.Model(), solver)
        print(f"  {solver.name:<9} yes")
    except Exception as error:
        print(f"  {solver.name:<9} no: {str(error.__context__ or error).split(',')[0]}")
```

```text
compiled into this OR-Tools:
  GSCIP     yes
  GLOP      yes
  CP_SAT    yes
  PDLP      yes
  GLPK      no: solver type SOLVER_TYPE_GLPK is not registered
  OSQP      no: solver type SOLVER_TYPE_OSQP is not registered
  ECOS      no: solver type SOLVER_TYPE_ECOS is not registered
  SCS       no: solver type SOLVER_TYPE_SCS is not registered
  HIGHS     yes
  SANTORINI no: solver type SOLVER_TYPE_SANTORINI is not registered
```

SCIP, GLOP, CP-SAT, PDLP and HiGHS are compiled in. GLPK, OSQP, ECOS, SCS and Santorini have a
`SolverType` but no code behind it in this build: the full message adds that support for the solver
has not been compiled, so naming one is refused at once.

Gurobi is the fifth kind: a commercial solver whose code is not in OR-Tools at all. MathOpt loads
Gurobi's own shared library at run time, and Gurobi then needs a license. Here is what the course
runner does with `SolverType.GUROBI`:

```python
model = mathopt.Model(name="tiny")
x = model.add_binary_variable(name="x")
model.maximize(x)
try:
    result = mathopt.solve(model, mathopt.SolverType.GUROBI)
    print("GUROBI:", result.termination.reason.name)
except Exception as error:
    print("GUROBI raised", type(error).__name__ + ":", error)
    print("hidden reason:", error.__context__)
```

```text
GUROBI raised RuntimeError: bad_function_call
hidden reason: None
```

**Gurobi through MathOpt does not run in the course runner, so this page shows no Gurobi results.**
The call fails with a C++ `bad_function_call`, which names no cause. The runner does have the
`gurobipy` package (section 5 uses it directly), and that wheel ships a Gurobi library, so the program
then points OR-Tools at it, in a child process because a failure there stops the process:

```python
library = sorted((pathlib.Path(gurobipy.__file__).parent / ".libs").glob("libgurobi*.so"))[0]
probe = ("from ortools.init.python import init; "
         f"print('loaded', init.CppBridge.load_gurobi_shared_library({str(library)!r}))")
child = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
print("gurobipy", ".".join(map(str, gurobipy.gurobi.version())), "ships", library.name)
print("loading it: exit code", child.returncode)
for line in child.stderr.splitlines():
    if "could not find function" in line:
        print("  ", line.split("] ", 1)[1].replace(str(library), library.name))
```

```text
gurobipy 13.0.3 ships libgurobi130.so
loading it: exit code -6
   Check failed: function_address Error: could not find function GRBcopyparams in libgurobi130.so
```

OR-Tools 9.15 expects a function, `GRBcopyparams`, that the Gurobi 13 library does not have, and the
child process aborted (exit code $`-6`$ is the abort signal). So in this course's pinned versions,
Gurobi is used through `gurobipy` itself (section 5, from lesson 5.3.1). On a machine with a Gurobi version and license
that OR-Tools supports, the same `mathopt.solve(model, mathopt.SolverType.GUROBI)` call is all it
takes; the model does not change. Never put a license file in a repository or an image; mount it at
run time (lesson 5.3.4, in section 5).

<!-- practice 2 -->

## Summary

- **The solver is an argument to `solve`, never part of the model.** Build once, solve with any
  `SolverType`, and make the solver configuration.
- **Each solver accepts only the model types it can solve.** GLOP and PDLP refuse integer variables,
  with an exception raised before solving.
- **Only GLOP, HiGHS and PDLP return LP duals**; SCIP and CP-SAT do not, and no solver returns duals for
  a MILP.
- **CP-SAT needs integers.** Handed a continuous variable, it rounds it and still reports `OPTIMAL`;
  give it all-integer models only.
- **Five solvers are compiled into the pip package:** GLOP, PDLP, HiGHS, SCIP, CP-SAT. Gurobi needs its
  own library and license, and does not run through MathOpt in the course runner.

## Reference

| `SolverType` | Kind | Takes | In the pip wheel |
| --- | --- | --- | --- |
| `GLOP` | simplex LP | LP | yes |
| `PDLP` | first-order LP | LP | yes |
| `HIGHS` | simplex, barrier, branch and bound | LP, MILP | yes |
| `GSCIP` | branch and cut (SCIP) | LP (no duals), MILP | yes |
| `CP_SAT` | constraint programming over integers | all-integer MILP | yes |
| `GUROBI` | commercial | LP, MILP | library and license needed |
| `GLPK`, `OSQP`, `ECOS`, `SCS`, `SANTORINI` | various | various | no (not compiled) |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt can drive, and the note that Gurobi and Xpress need licenses); [MathOpt `parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py) (the `SolverType` docstrings: what each solver supports, SCIP's missing LP duals, CP-SAT's experimental discretizing); [MathOpt `parameters.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/parameters.proto) (the same list at the protocol level, which already names Xpress); [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver) (CP-SAT works over integers only, and non-integer terms must be scaled first); [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (GLOP's primal and dual simplex, and when to try PDLP or a commercial solver); [MathOpt sample time_indexed_scheduling.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (a solver taken as a `SolverType` flag, with SCIP as its default).

## Challenges

1. Scale the one-continuous model so CP-SAT gets it right: replace `a` by an integer number of
   hundredths. What changes in the coefficients?
2. Solve GridCap medium with HiGHS, SCIP and CP-SAT. Do they fund the same projects? If not, are the
   objective values still equal?
3. Write the shortest program that tells a colleague whether MathOpt can use Gurobi on their machine,
   without printing anything that identifies the machine.

## Design Note: Test a Model on Two Solvers

Switching solver costs one argument, so use it in tests. A test that solves a small instance with
HiGHS and with SCIP and asserts the objective values agree (within a tolerance, lesson 2.4.1) catches
two kinds of bug at once: a model that a solver reads differently than you intended (the CP-SAT case
above) and a solver bug in a new release. It does not catch a model that is wrong in the same way for
every solver; that needs hand-built feasible and infeasible plans, as the course's modeling practices
use. Section 12 builds both kinds of test into the planning service.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**solver_grid.py.** GridCap small as an LP and as a MILP on GLOP, PDLP, HiGHS, SCIP and CP-SAT, and the list of solvers compiled into the wheel (*The Solver Is an Argument*, *Each Solver Accepts Only*, *Five Solvers Are Built Into the pip Package*). *Try:* Add the tiny portfolio as a third model. Predict which cells change.

- Program: [solver_grid.py](src/solver_grid.py)

**cpsat_continuous.py.** CP-SAT on a continuous model: the LP relaxation and a model with one continuous variable (*CP-SAT Needs Integers*). *Try:* Make `a` an integer variable. Predict both solvers' answers.

- Program: [cpsat_continuous.py](src/cpsat_continuous.py)

**gurobi_attempt.py.** What `SolverType.GUROBI` does in the course runner, and what happens when OR-Tools is pointed at the library inside `gurobipy` (*Gurobi Needs Its Own Library and License*). *Try:* Run it on a machine with Gurobi installed. Predict the termination reason.

- Program: [gurobi_attempt.py](src/gurobi_attempt.py)
