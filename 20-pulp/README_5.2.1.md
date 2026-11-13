# 5.2.1 A PuLP Model End to End With CBC

GridCap's regional planning office keeps its tools in PuLP, an open-source Python modeling library
from the COIN-OR project, and solves with CBC, COIN-OR's open-source MILP solver. The office has
asked for lesson 6.4.1's five-year plan (40 projects on GridCap small, a start year for each, a
budget for each year from 2027 to 2031) in a form it can run. The central team builds the same
model in MathOpt. Before the office plans with the PuLP version, it has to show the same optimum
the MathOpt version found: **$24,260k**. GridCap is a fictional utility's portfolio.

This lesson writes that model in PuLP, looks at the file PuLP hands to CBC, solves it, reads the
result, and proves the port with a test. Five rules, one per heading. Everything here runs on the
course's pinned PuLP `3.3.2`, which bundles a CBC executable. PuLP 4, released in 2026, changed parts
of the API; the lesson points out each call it changed.

The model comes from lesson 6.4.1, in section 6, which the course reaches later. You do not need to
have read it: *The Model*, near the end of this lesson, restates it in full with the names the PuLP
code gives its rows. When this lesson compares with "lesson 6.4.1's MathOpt output", it means the
lines that lesson recorded from its MathOpt model, solved with HiGHS on GridCap small:

<!-- unverified -->
```text
OPTIMAL NPV $24,260k
started 27 of 40; 9 later than their earliest year
  P008 window 2029-2031 starts 2031  NPV 264 -> 182
  P010 window 2030-2031 starts 2031  NPV 26 -> 19
  P011 window 2029-2031 starts 2031  NPV 240 -> 140
  P012 window 2030-2031 starts 2031  NPV 201 -> 168
  P021 window 2028-2030 starts 2029  NPV 1,241 -> 1,012
  P025 window 2027-2029 starts 2028  NPV 1,009 -> 880
  P029 window 2030-2031 starts 2031  NPV 302 -> 233
  P031 window 2027-2028 starts 2028  NPV 1,000 -> 809
  P039 window 2027-2029 starts 2028  NPV 546 -> 386
starts per year: {2027: 4, 2028: 7, 2029: 4, 2030: 5, 2031: 7}
```

Each indented line is a project the plan starts later than the first year its window allows: P008 may start from
2029 to 2031, starts in 2031, and its NPV falls from 264 to 182. The port test at the end of the
lesson solves the MathOpt model again itself, so the comparison does not rest on this copy.

## A PuLP Model Is a Problem, Its Variables, and Rows Added With `+=`

PuLP has three building blocks:

- **`pulp.LpProblem(name, sense)`** holds the whole model: its objective, its rows and, through
  them, its variables. `sense` is `pulp.LpMaximize` or `pulp.LpMinimize`.
- **Variables.** `prob.add_variable(name, lowBound, upBound, cat=...)` creates one and ties it to
  the problem. `cat` is `pulp.LpContinuous` (the default), `pulp.LpInteger` or `pulp.LpBinary`.
  Older code creates variables on their own with `pulp.LpVariable(...)`; lesson 5.2.2 reads that
  style, which PuLP 4 removed.
- **`prob += ...`** adds to the problem. Handed a linear expression, it sets the **objective**.
  Handed a comparison (`<=`, `>=`, `==`) of expressions, it adds a **row**. A second item after a
  comma is the name: `prob += expr <= 5, "cap"`.

`pulp.lpSum(...)` adds up a sequence of terms into one linear expression, the way Python's `sum`
does. Here is the start of lesson 6.4.1's model, from `pulp_timing.py`:

```python
prob = pulp.LpProblem("gridcap_timing", pulp.LpMaximize)
x = {(p.project_id, t): prob.add_variable(f"x_{p.project_id}_{t}", 0, 1, cat=pulp.LpBinary)
     for p in portfolio.projects for t in p.starts()}
```

One binary $`x_{i,t}`$ per project $`i`$ and allowed start year $`t`$, named `x_P001_2028` and so
on. As in lesson 6.4.1, a start year outside the project's window has no variable at all. The
names matter: they are what the solver sees, what an LP file shows, and how you find a variable
again.

Most rows talk about $`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$, so the builder has a helper
for it. With `by` set, it sums only the start years up to `by`, which the precedence rows need:

```python
def started(pid: str, by: int | None = None) -> pulp.LpAffineExpression:
    return pulp.lpSum(x[pid, t] for t in by_id[pid].starts() if by is None or t <= by)
```

Then the objective, the once and must-do rows, and the yearly budgets, each with the name the
model block below gives it:

```python
prob += pulp.lpSum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()), "npv"

for p in portfolio.projects:
    if p.must_do:
        prob += started(p.project_id) == 1, f"must_{p.project_id}"
    else:
        prob += started(p.project_id) <= 1, f"once_{p.project_id}"
```

```python
for year in portfolio.years:
    spend = pulp.lpSum(amount * x[p.project_id, t]
                       for p in portfolio.projects for t in p.starts()
                       for y, amount in p.spend(t).items() if y == year)
    prob += spend <= portfolio.budget[year], f"budget_{year}"
```

The alternative-group rows (`alt_G006`) and the precedence rows (`after_P004_2028`) follow the same
pattern; the full builder is in `pulp_timing.py`.

Read `+=` with care. The same operator sets the objective or adds a row, depending only on what
stands to its right, so a row that lost its `<=` quietly becomes the new objective. Lesson 5.2.2
shows that bug and three others.

## Write the LP File and Read It Before You Solve

A model built in a loop is hard to check by reading the loop. PuLP can write the model in the
**LP format**, a plain-text file that lists the objective, then every row by name, then the
variables' bounds and types, the way a solver will see them. `prob.writeLP(path)` writes it.
Here it is for the tiny portfolio:

```python
print(f"{pt.prob.name}: {pt.prob.numVariables()} variables, {pt.prob.numConstraints()} rows,",
      "maximize" if pt.prob.sense == pulp.LpMaximize else "minimize", pt.prob.objective.name)
print("row names:", ", ".join(row.name for row in pt.prob.constraints()))
```

```python
    pt.prob.writeLP(str(path))
```

```text
gridcap_timing: 13 variables, 13 rows, maximize npv
row names: once_P001, must_P002, once_P003, once_P004, once_P005, once_P006, once_P007, once_P008, alt_G006, after_P004_2028, budget_2027, budget_2028, budget_2029
--- gridcap_tiny.lp (39 lines), up to the first budget row:
\* gridcap_timing *\
Maximize
npv: 1386 x_P001_2028 + 1077 x_P001_2029 + 871 x_P002_2028 + 636 x_P002_2029
 + 576 x_P003_2027 + 2120 x_P004_2028 + 123 x_P005_2027 + 1247 x_P006_2028
 + 265 x_P007_2027 + 220 x_P007_2028 + 137 x_P008_2027 + 92 x_P008_2028
 + 55 x_P008_2029
Subject To
after_P004_2028: - x_P003_2027 + x_P004_2028 <= 0
alt_G006: x_P006_2028 + x_P007_2027 + x_P007_2028 <= 1
budget_2027: 980 x_P003_2027 + 250 x_P005_2027 + 290 x_P007_2027
 + 580 x_P008_2027 <= 2300
...
rows in the file, in order: npv, after_P004_2028, alt_G006, budget_2027, budget_2028, budget_2029, must_P002, once_P001, once_P003, once_P004, once_P005, once_P006, once_P007, once_P008
```

Three things to read in it:

- **Every term moved to the left.** The precedence row was written as
  $`\text{started}(P004, \le 2028) \le \text{started}(P003, \le 2027)`$; the file shows it as
  `- x_P003_2027 + x_P004_2028 <= 0`. That is the same row. PuLP keeps variables on the left and
  one number on the right.
- **The rows come sorted by name**, not in the order the code added them (`prob.constraints()`
  keeps that order). Name rows so that sorting groups them: every budget row starts `budget_`.
- **The 2027 budget row has four projects, not eight.** Only projects that can be spending in 2027
  appear in it, which is the spreading of lesson 6.4.2 made visible.

When a model gives a strange answer, this file is the first thing to read. The PuLP debugging guide
gives the same advice for infeasible models: write the LP file and check each row in an editor.

<!-- practice 1 -->

## CBC Runs as a Separate Program, Set Up Through a Solver Object

`prob.solve(solver)` hands the model to a solver. In PuLP 3.3, `pulp.PULP_CBC_CMD(...)` is the CBC
executable that ships inside the PuLP package. As the `_CMD` in its name says, it is a
command-line integration: PuLP writes the model to a file, runs `cbc` on it as a separate program,
and reads the solution file back. Its options are arguments of the constructor. The module's
helper keeps CBC quiet unless asked:

```python
def cbc(**options) -> pulp.LpSolver:
    """PuLP 3.3's bundled CBC, quiet unless asked: `msg`, `timeLimit`, `gapRel`, `threads`, ..."""
    return pulp.PULP_CBC_CMD(**{"msg": False, **options})
```

| Option | Meaning |
| --- | --- |
| `msg=False` | Don't print CBC's log. The default, `True`, prints it. |
| `timeLimit=60` | Stop after 60 seconds. |
| `gapRel=0` | The relative MIP gap at which CBC may stop, as in lesson 3.4.1. `0` asks for a proved optimum. |
| `maxNodes=1` | Stop after that many branch-and-bound nodes. |
| `threads=4` | Threads CBC may use. |

Solve GridCap small with a gap of 0 and read the plan:

```python
pt = build(small)
status = pt.prob.solve(cbc(gapRel=0))
print("status", status, pulp.LpStatus[status], "| sol_status", pt.prob.sol_status,
      pulp.LpSolution[pt.prob.sol_status])
print(f"NPV ${pulp.value(pt.prob.objective):,.0f}k")
plan = schedule(pt)
```

```text
status 1 Optimal | sol_status 1 Optimal Solution Found
NPV $24,260k
started 27 of 40; 9 later than their earliest year
  P008 window 2029-2031 starts 2031  NPV 264 -> 182
  P010 window 2030-2031 starts 2031  NPV 26 -> 19
  P011 window 2029-2031 starts 2031  NPV 240 -> 140
  P012 window 2030-2031 starts 2031  NPV 201 -> 168
  P021 window 2028-2030 starts 2029  NPV 1,241 -> 1,012
  P025 window 2027-2029 starts 2028  NPV 1,009 -> 880
  P029 window 2030-2031 starts 2031  NPV 302 -> 233
  P031 window 2027-2028 starts 2028  NPV 1,000 -> 809
  P039 window 2027-2029 starts 2028  NPV 546 -> 386
spend / budget: 2027 8,750/8,890, 2028 7,970/8,120, 2029 8,630/8,760, 2030 8,560/8,610, 2031 7,720/7,850
budget_2027 slack 140.0 | P008 starts: {2029: 0.0, 2030: 0.0, 2031: 1.0}
```

$24,260k, 27 projects started, and the same nine deferrals lesson 6.4.1 printed from MathOpt and
HiGHS. After the solve, the answer is stored **in the model's own objects**:

- `var.varValue` is a variable's value, and `pulp.value(expr)` evaluates any expression,
  `prob.objective` included.
- `prob.get_constraint_by_name("budget_2027")` finds a row by name, and its `slack` is how far the
  row is from its bound: right side minus left side for a `<=` row. $140k of 2027's budget is
  unspent.
- `schedule` reads the start years the way lesson 6.4.1 does, with `> 0.5` rather than `== 1`,
  because a MILP solver only promises values within a small tolerance of whole numbers:

```python
def schedule(pt: PulpTiming) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in pt.x.items() if v.varValue > 0.5}
```

**This part of the API changed in PuLP 4.** PuLP 3.3 already marks `PULP_CBC_CMD` as deprecated,
and PuLP 4 removed it. CBC no longer ships inside PuLP: it comes from the `pulp[cbc]` extra or a
`cbc` on the path, and the solver class is `pulp.COIN_CMD`. The runner's PuLP `3.3.2` has no
separate CBC, so the course uses `PULP_CBC_CMD`. A different PuLP or CBC may also find another of
several equally good plans; the value is the thing to compare, as the last section does.

## The Status Says How CBC Stopped; `sol_status` Says Whether the Plan Is Proved

In PuLP 3.3, `prob.solve()` returns a **status code**, an `int` also kept in `prob.status`. The
dict `pulp.LpStatus` turns it into words. A second code, `prob.sol_status`, describes the solution
itself, and `pulp.LpSolution` turns that one into words. Here are both dicts, then GridCap small
solved in full and stopped by `maxNodes=1` (after the first node of the search), GridCap medium
stopped by a two-second time limit, and GridCap small with a row added that no plan can meet:

```python
print("LpStatus:  ", pulp.LpStatus)
print("LpSolution:", pulp.LpSolution)
```

```python
for label, options in (("no limit", {}), ("maxNodes=1", {"maxNodes": 1})):
    pt = build(small)
    status = pt.prob.solve(cbc(**options))
```

```text
LpStatus:   {0: 'Not Solved', 1: 'Optimal', -1: 'Infeasible', -2: 'Unbounded', -3: 'Undefined'}
LpSolution: {0: 'No Solution Found', 1: 'Optimal Solution Found', 2: 'Solution Found', -1: 'No Solution Exists', -2: 'Solution is Unbounded'}
no limit    status 1 Optimal  sol_status 1 Optimal Solution Found NPV $24,260k
maxNodes=1  status 1 Optimal  sol_status 2 Solution Found         NPV $23,944k
medium, timeLimit=2: status 1 Optimal, sol_status 2 Solution Found
forced     status -1 Infeasible sol_status -1 No Solution Exists
```

Read the middle line twice. CBC stopped after one node with a plan worth $23,944k, $316k short of
the optimum, and `status` still says **Optimal**. The time limit on medium gives the same pair.
In both runs the search stopped early with a plan in hand, and PuLP 3.3's CBC interface reported
status 1. Only `sol_status` tells a finished search from a stopped one: 1 is a proved optimum, and
2 is a solution with no proof.

So the rule for PuLP 3.3:

- `status == pulp.LpStatusOptimal` and `sol_status == pulp.LpSolutionOptimal`: a proved optimum.
- `status == pulp.LpStatusOptimal` and `sol_status == pulp.LpSolutionIntegerFeasible`: a plan
  that keeps every row, but the search stopped before proving it best. Report it as such.
- Any other status: there is no plan to read, whatever the variables hold (lesson 5.2.2 shows
  what they hold).

PuLP 4 replaced both codes. There `solve()` returns an `LpSolveStats` object, `LpStatus` and the
`LpSolution` constants are gone, a run stopped by a limit reports the limit (`TimeLimit`,
`NodeLimit`, ...) instead of `Optimal`, and `stats.has_solution` says whether a plan exists.

<!-- practice 2 -->

## A Port Is Proved by a Test: Same Optimum, Same Rows, Each Plan Allowed

"The same answer" means three checks, the ones lesson 4.7.2 uses to prove a port:

1. **The same optimal value, with both solvers at a gap of 0.** At the default gap, a solver may
   stop at a plan within its tolerance of the best, and two correct models can then disagree.
2. **Each plan keeps the other model's rules.** Two optimal plans can differ when several tie, so
   plans are not compared directly. Instead, `plan_rules.broken_rules` checks a plan against the
   rules from the data, with no solver. A port that dropped a row could reach a higher value with
   a plan the original forbids; this check catches it.
3. **The same rows by name.** A dropped or doubled rule shows up before any solve.

`same_optimum.py` runs all three on tiny and small:

```python
    pt = pulp_timing.build(portfolio)
    status = pt.prob.solve(pulp_timing.cbc(gapRel=0))
    cbc_value, cbc_plan = pulp.value(pt.prob.objective), pulp_timing.schedule(pt)

    model, x = mathopt_timing.build(portfolio)
    result = mathopt.solve(model, mathopt.SolverType.GSCIP, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
```

```text
tiny   CBC Optimal $2,473k | SCIP OPTIMAL $2,473k | same value: True, same plan: True, rules broken: [] / []
       rows 13 / 13, same names: True; variables 13 / 13
small  CBC Optimal $24,260k | SCIP OPTIMAL $24,260k | same value: True, same plan: True, rules broken: [] / []
       rows 49 / 49, same names: True; variables 80 / 80
```

Why SCIP here and not HiGHS, the course's default? Because in the runner, a Python process that has
imported `pulp` is killed when MathOpt then solves a MIP with HiGHS. `highs_after_pulp.py` runs each
case in a fresh child process, since the crash takes down the process it happens in:

```text
(no pulp)    then MathOpt HIGHS : exit 0, objective 2.0
import pulp  then MathOpt HIGHS : killed by SIGSEGV; the native stack passes through OR-Tools' HighsSolver: True, and highspy: True
import pulp  then MathOpt GSCIP : exit 0, objective 2.0
import pulp  then MathOpt CP_SAT: exit 0, objective 2.0
```

SIGSEGV is a segmentation fault: native code read memory it should not, and the operating system
ended the process. No Python exception is raised and no `try` can catch it. The program asks Python's
`faulthandler` for the native stack of the crash: it runs through OR-Tools' HiGHS solver and the
`highspy` library, the HiGHS that PuLP's own HiGHS interface loads. Until that is fixed, keep PuLP and MathOpt-with-HiGHS in **separate processes**, or use another
MathOpt solver in a process that needs both.

The module's test keeps them apart. It solves the PuLP port with CBC. Then, in a child process, it runs lesson 6.4.1's own builder with HiGHS,
the model and solver that lesson used. It checks the same value, that both plans keep every rule,
and the same row names. It passes on tiny and small, so the regional office's PuLP model answers
$24,260k, as the MathOpt model does.

## The Model

The PuLP port builds lesson 6.4.1's model with no change, so the model is that lesson's. Here it is
whole, with the names `pulp_timing.py` gives its rows.

**Sets.** $`P`$, the projects; $`Y`$, the plan's years; $`T_i \subseteq Y`$, the start years
project $`i`$ may use (its window, cut so the work ends inside $`Y`$); $`M \subseteq P`$, the
must-do projects; $`\mathcal{G}`$, the alternative groups, each a set of projects;
$`C \subseteq P`$, the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$
(`prob.add_variable(..., 0, 1, cat=pulp.LpBinary)`): project $`i`$ starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \qquad \text{(npv)}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

| Label | Row name in `pulp_timing.py` and `mathopt_timing.py` |
| --- | --- |
| npv | the objective, named `npv` |
| once$`_i`$, must$`_i`$ | `once_P001`, `must_P002` |
| alt$`_g`$ | `alt_G006` |
| after$`_{c,t}`$ | `after_P004_2028` |
| budget$`_y`$ | `budget_2027` |

## Summary

- **A PuLP model is a problem, its variables and rows added with `+=`.** `+=` with an expression
  sets the objective; with a comparison and a name, it adds a named row.
- **Write the LP file and read it before you solve.** It shows every row as the solver sees it,
  sorted by name.
- **CBC runs as a separate program, set up through a solver object.** In PuLP 3.3 that object is
  `PULP_CBC_CMD(msg=False, gapRel=0, ...)`; PuLP 4 renamed it `COIN_CMD`. Values are read from
  `varValue` and `pulp.value(...)`.
- **The status says how CBC stopped; `sol_status` says whether the plan is proved.** After one
  node, CBC reported `Optimal` with `sol_status` 2 and $23,944k, against $24,260k proved.
- **A port is proved by a test.** Same value at gap 0, each plan keeping every rule, and the same
  rows by name: the PuLP port matched MathOpt on tiny ($2,473k) and small ($24,260k). In the runner,
  keep PuLP and MathOpt's HiGHS in separate processes.

## Reference

| PuLP 3.3 | What it does | In PuLP 4 |
| --- | --- | --- |
| `pulp.LpProblem(name, pulp.LpMaximize)` | the model and its sense | same |
| `prob.add_variable(name, lo, up, cat=pulp.LpBinary)` | a variable tied to the problem | same |
| `prob += expr, "name"` | sets the objective | same |
| `prob += expr <= rhs, "name"` | adds a named row | same |
| `pulp.lpSum(terms)` | a linear sum | same |
| `prob.writeLP(path)` | the model as an LP file | same |
| `prob.solve(pulp.PULP_CBC_CMD(msg=False, gapRel=0))` | solve with the bundled CBC; returns the status code | `COIN_CMD`; returns `LpSolveStats` |
| `prob.status`, `pulp.LpStatus[...]` | how the run ended | `stats.status`, an `LpSolveStatus` |
| `prob.sol_status`, `pulp.LpSolution[...]` | proved, unproved or no solution | `stats.has_solution` |
| `var.varValue`, `pulp.value(expr)` | a value after the solve | same |
| `prob.get_constraint_by_name(n).slack` | a row's slack | same |

| `status` | `sol_status` | Read it as |
| --- | --- | --- |
| 1 Optimal | 1 Optimal Solution Found | a proved optimum |
| 1 Optimal | 2 Solution Found | a plan, not proved best (a limit stopped the search) |
| -1 Infeasible | -1 No Solution Exists | no plan keeps every row |
| 0, -2, -3 | | no plan to read |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the
MathOpt side of the port and the solvers it can call) and the
[MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py)
(a MathOpt MIP that reads the termination reason before any value);
[Optimization with PuLP](https://coin-or.github.io/pulp/) (the documentation, now for PuLP 4.3);
[A Blending Problem, PuLP 3.3.2 source](https://github.com/coin-or/pulp/blob/3.3.2/doc/source/CaseStudies/a_blending_problem.rst)
(the documentation's worked model: problem, `+=` with names, `writeLP`, `solve`, `LpStatus`,
`varValue`, `value`); [How to configure a solver in PuLP, 3.3.2](https://github.com/coin-or/pulp/blob/3.3.2/doc/source/guides/how_to_configure_solvers.rst)
(`getSolver`, `listSolvers`, and `PULP_CBC_CMD` deprecated in favor of `COIN_CMD`);
[pulp.constants (PuLP 4)](https://www.coin-or.org/pulp/technical/constants.html) (the senses,
categories and the `LpSolveStatus` that replaced `LpStatus`);
[How to migrate from PuLP 3.x to 4.0](https://www.coin-or.org/pulp/guides/how_to_migrate_to_v4.html)
(every call this lesson marks as changed, and why a limit no longer reports `Optimal`);
[How to debug most errors during solving](https://www.coin-or.org/pulp/guides/how_to_debug.html)
(`msg=True`, `writeLP` and `writeMPS` to see what the solver got).

## Challenges

1. Solve GridCap small with `cbc(timeLimit=1)`. Print `status` and `sol_status` and decide from
   them alone whether you may call the answer optimal.
2. Delete the `alt_` rows from `pulp_timing.build`. Which of the three checks in the port test
   fails first on tiny, and which on small?
3. Write GridCap small's model with `writeLP` and count the variables in `budget_2031`. Explain the
   count from the projects' windows and cost profiles.

## Design Note: Write PuLP 3.3 Code That PuLP 4 Still Reads

The pinned PuLP `3.3.2` already accepts most of PuLP 4's forms: `prob.add_variable` instead of
`LpVariable`, `prob.constraints()` as a list, `get_constraint_by_name`. Use them, and keep the
version-specific parts in one place. In this module, that is the `cbc()` helper, the only line that
names a solver class, and the status checks. Moving to PuLP 4 is then a change to two functions,
not to every model. The test of the last section is what tells you the move worked.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**lp_file.py.** Builds lesson 6.4.1's model on GridCap tiny and prints the LP file PuLP writes for
it (*Write the LP File and Read It Before You Solve*). *Try:* Print the `budget_2029` row of the
file. Predict which projects it lists before you run it.

- Program: [lp_file.py](src/lp_file.py)

**cbc_small.py.** Solves GridCap small with CBC and reads the status, the value, the schedule and
a row's slack (*CBC Runs as a Separate Program, Set Up Through a Solver Object*). *Try:* Run it with
`cbc(msg=True)` and find the line in CBC's log that gives the objective.

- Program: [cbc_small.py](src/cbc_small.py)

**status_codes.py.** Prints PuLP 3.3's two status dicts, and the pair of codes for a full solve, a
one-node solve, a medium solve stopped by a time limit, and an infeasible model (*The Status Says How CBC Stopped*). *Try:* Change `maxNodes`
to 10. Predict whether `sol_status` changes.

- Program: [status_codes.py](src/status_codes.py)

**same_optimum.py and highs_after_pulp.py.** The port's three checks on tiny and small, and the
crash that keeps MathOpt's HiGHS out of a process that imported PuLP (*A Port Is Proved by a
Test*). *Try:* Change a budget in the PuLP builder only, for instance `portfolio.budget[year] + 100`.
Predict which checks still pass.

- Program: [same_optimum.py](src/same_optimum.py)
- Program: [highs_after_pulp.py](src/highs_after_pulp.py)

**pulp_timing.py, mathopt_timing.py and plan_rules.py.** The PuLP builder, the same model in
MathOpt (a copy of the timing builder of lessons 6.4.1 to 6.4.4, cut to lesson 6.4.1's rows), and the rule check that needs no
solver. They print nothing themselves.

- Library: [pulp_timing.py](src/pulp_timing.py)
- Library: [mathopt_timing.py](src/mathopt_timing.py)
- Library: [plan_rules.py](src/plan_rules.py)
