# 10.1.3 Spotting Numerical Trouble in a Log

GridCap's capital plan runs every night, and the job keeps each solve's log next to its result
(lesson 3.3.4's design note). Most nights nobody reads it. This lesson is about the nights someone
should: what in a log says that a plan rests on bad numbers, before a planner finds out from a
budget that does not add up. Lessons 2.4.2 and 3.3.4 read an LP log and a MIP log from top to bottom.
This one reads only the lines that carry numerical warnings, on the models of lessons 10.1.1 and
10.1.2, and ends with the check no log line replaces: solve again a different way and compare.
GridCap is a fictional utility; its numbers are teaching data.

## The Model

The bridge-loan model of lessons 10.1.1 and 10.1.2, restated whole. $`o`$ and $`r`$ are the units of
the objective and of the money rows per $k, and $`\bar M_y`$ is the switch row's big-M.

**Sets.** $`P`$ the projects; $`Y = \{2027, \dots, 2031\}`$; $`M \subseteq P`$ the must-do
projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$.

**Parameters.** $`v_i`$ the NPV of project $`i`$ ($k); $`c_{i,y}`$ its spend in year $`y`$ ($k);
$`B_y`$ the budget ($k); $`L_y = B_y/10`$ the credit line ($k); $`F = 300`$ the fee ($k);
$`\rho = 0.05`$ the interest per $k borrowed; $`o`$, $`r`$ and $`\bar M_y`$ as above.

**Variables.** $`x_i \in \{0, 1\}`$ for $`i \in P`$; $`h_y \in \{0, 1\}`$ and
$`\ell'_y \ge 0`$ (the loan, in the rows' unit) for $`y \in Y`$.

```math
\begin{aligned}
\max \;& \sum_{i \in P} o\, v_i\, x_i - \sum_{y \in Y} \Bigl( o F\, h_y + \frac{o\,\rho}{r}\, \ell'_y \Bigr) \\
\text{s.t. }& \sum_{i \in P} r\, c_{i,y}\, x_i \le r B_y + \ell'_y && \forall y \in Y && \text{(budget}_y) \\
& \ell'_y \le r L_y && \forall y \in Y && \text{(credit}_y) \\
& \ell'_y \le \bar M_y\, h_y && \forall y \in Y && \text{(switch}_y) \\
& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& x_c \le x_{p(c)} && \forall c \in C && \text{(after}_c)
\end{aligned}
```

The three variants: `TIGHT` ($k, $`\bar M_y = L_y`$), `HUGE_M` ($k, $`\bar M_y = 10^9`$) and
`MIXED` (objective in dollars, rows in $M, $`\bar M_y = 10^9`$). All three allow the same plans,
and the best of them is worth $23,161.5k.

## HiGHS Warns About Large Costs and Bounds, but Not About the Matrix, So Read the Ranges Yourself

A HiGHS log opens with the model's size and its four coefficient ranges (lesson 10.1.2), then any
`WARNING` lines about them, then presolve. Which numbers draw a warning? `warnings_grid.py` builds
one tiny model per test, with all numbers 1 except one, and keeps the warnings:

```math
\max \; c\, x + y \quad \text{s.t.} \quad a\, x + y \le b \;\; \text{(row)}, \qquad 0 \le x \le u, \quad y \in \{0, 1\}
```

```python
for kind in ("Matrix", "Cost", "RHS", "Bound"):
    for value in (1e-7, 1e5, 1e6, 1e7, 1e11):
        _, log = solve(one_number(kind, value))
        warnings = [line.replace("WARNING: ", "").strip() for line in log if line.startswith("WARNING")]
```

```text
Matrix 1e-07: no warning
Matrix 1e+05: no warning
Matrix 1e+06: no warning
Matrix 1e+07: no warning
Matrix 1e+11: no warning
Cost   1e-07: Problem has some excessively small costs
Cost   1e+05: no warning
Cost   1e+06: no warning
Cost   1e+07: Problem has some excessively large costs / Consider scaling the objective by 1e-1, or setting the user_objective_scale option to -4
Cost   1e+11: Problem has some excessively large costs / Consider scaling the objective by 1e-5, or setting the user_objective_scale option to -17
RHS    1e-07: Problem has some excessively small row bounds
RHS    1e+05: no warning
RHS    1e+06: no warning
RHS    1e+07: Problem has some excessively large row bounds / Consider scaling the    bounds by 1e-1, or setting the user_bound_scale option to -4
RHS    1e+11: Problem has some excessively large row bounds / Consider scaling the    bounds by 1e-5, or setting the user_bound_scale option to -17
Bound  1e-07: Problem has some excessively small column bounds
Bound  1e+05: no warning
Bound  1e+06: no warning
Bound  1e+07: Problem has some excessively large column bounds / Consider scaling the    bounds by 1e-1, or setting the user_bound_scale option to -4
Bound  1e+11: Problem has some excessively large column bounds / Consider scaling the    bounds by 1e-5, or setting the user_bound_scale option to -17
```

The HiGHS in OR-Tools 9.15 warned about costs, right-hand sides and bounds at $`10^7`$ and above and
at $`10^{-7}`$, and not at $`10^5`$ or $`10^6`$. It printed no warning for any matrix coefficient, not even
$`10^{11}`$, though the matrix is where a big-M lives. That is why lesson 10.1.2's model with the
objective in $k and $`10^9`$ in its matrix ran without a single warning.

So the first lines to read are the ranges, not the warnings. Read the `Matrix` line as a span: a
largest value more than $`10^9`$ times the smallest is past the limit Gurobi's numerical guidelines
give, and anything above $`10^6`$ is worth a look. Then read each extreme as a question: which data gave a coefficient
this large, and is it in the unit you meant?

## A Nonzero Count Lower Than You Built Means a Coefficient Was Dropped

The first line of the log describes the model as HiGHS received it, before presolve (lesson 3.3.4),
and counts its nonzeros. HiGHS's option `small_matrix_value`, default
$`10^{-9}`$, is documented as a lower limit: matrix entries at or below it are treated as zero.
`dropped.py` builds the same one-row model with $`a = 10^{-8}`$ and $`a = 10^{-9}`$, and compares
the nonzeros it built with the count in HiGHS's first line:

```math
\max \; x + y \quad \text{s.t.} \quad a\, x + y \le 1 \;\; \text{(row)}, \qquad 0 \le x \le 1000, \quad y \in \{0, 1\}
```

```text
a = 1e-08: built 2 nonzeros; HiGHS: MIP tiny has 1 row; 2 cols; 2 nonzeros; 1 integer variables (1 binary)
  OPTIMAL  x = 1000  y = 0  row broken by 0.0e+00
a = 1e-09: built 2 nonzeros; HiGHS: MIP tiny has 1 row; 2 cols; 1 nonzero; 1 integer variable (1 binary)
  OPTIMAL  x = 1000  y = 1  row broken by 1.0e-06
```

With $`a = 10^{-8}`$, $`x = 1000`$ uses $`10^{-5}`$ of the row, so $`y`$ cannot be 1 as well, and
HiGHS sets it to 0. With $`a = 10^{-9}`$ HiGHS counts one nonzero, not two: the coefficient never
reached the solver, there was no warning, and the plan breaks the row as written by $`10^{-6}`$. A
coefficient this small usually means a unit gone wrong (a cost per dollar in a row of billions,
say), and the only trace in the log is a count one lower than the model you built. Compare it with
`sum(len(list(model.row_nonzeros(r))) for r in model.linear_constraints())`, as `dropped.py` does.
Large coefficients are not dropped the same way: the $`10^9`$ of lesson 10.1.2's models reached
HiGHS, and its `Matrix` line printed it.

## The Report's Violation Lines Are the Solver's Audit of Its Own Plan

At the end of a MIP log, HiGHS's solving report checks the plan it returns against the model it
solved, and prints the largest violation of three kinds: of a variable's bounds, of integrality, and
of a row. `report.py` prints that block for lesson 10.1.1's two runs, the tight model with defaults
and the huge $`M`$ with presolve off:

```text
HiGHS, tight M, defaults:
  Solution status   feasible
                    23161.5 (objective)
                    0 (bound viol.)
                    0 (int. viol.)
                    0 (row viol.)
HiGHS, M = 1e9, presolve off:
  Solution status   feasible
                    23565.8992314 (objective)
                    0 (bound viol.)
                    8.89e-07 (int. viol.)
                    0 (row viol.)
```

Both say `feasible`, and both are, within HiGHS's tolerances: $`8.89 \times 10^{-7}`$ is below its
integrality tolerance of $`10^{-6}`$. The difference is in the numbers. A model whose binaries
multiply ordinary numbers lands its binaries on 0 and 1, and reports zeros. A nonzero integrality
violation says a binary was left between whole numbers, and lesson 10.1.1 showed that this one is a
$`8.9 \times 10^{-7}`$ switch worth an $889k loan. The violation line does not say that it matters;
it says where to look: find the binaries that are not whole, and the coefficients they meet.

A useful rule for a nightly job is to flag any nonzero violation on a model with switched rows,
and any violation near the tolerance on any model, and to keep the flag with the plan. Rerunning
with a tighter tolerance is not the fix: lesson 10.1.1 uses it only to diagnose, and the fix is to
make the model's numbers fit the tolerance.

<!-- practice 1 -->

## SCIP Says When Its Best Solution Breaks a Row of Your Model

SCIP works on a transformed copy of the model, the result of its presolve, and translates its best
solution back at the end. When the translated solution breaks a row of the original model, it says
so after its report. `report.py` solves the `HUGE_M` model with SCIP's defaults:

```python
result, log = solve(build(small, HUGE_M).model, mathopt.SolverType.GSCIP, EXACT)
```

```text
SCIP, M = 1e9, defaults: OPTIMAL, objective 23,161.5
SCIP Status        : problem is solved [optimal solution found]
Solving Time (sec) : <t>
Solving Nodes      : 1
Primal Bound       : +2.31615000000000e+04 (33 solutions)
Dual Bound         : +2.31615000000000e+04
Gap                : 0.00 %
  [linear] <switch_2027>: <loan_2027>[C] (-1.13686838e-12) -1e+09<take_2027>[B] (-1.27881707e-15) <= 0;
;
violation: right hand side is violated by 1.27881593536577e-06
best solution is not feasible in original problem
```

The last four lines are the warning. They print the row (`switch_2027`, written as
$`\ell_{2027} - 10^9 h_{2027} \le 0`$), each variable's value in brackets, and the size of the
violation. The values are rounding noise: a loan of $`-1.1 \times 10^{-12}`$ and a switch of
$`-1.3 \times 10^{-15}`$, both zero in any sense that matters. But the switch is multiplied by
$`10^9`$, and $`-10^9 \times -1.28 \times 10^{-15} = 1.28 \times 10^{-6}`$ is above SCIP's tolerance
for a row whose right-hand side is 0. Lesson 10.1.1 measured that noise at about $`10^{-16}`$ of a
number; $`10^9`$ brought it up to the tolerance.

The plan itself is right: $23,161.5k, the true optimum. What the warning says is that the model
cannot be checked reliably, because any value near zero on that binary is magnified a billion
times. And MathOpt's result carries none of it: the status is `OPTIMAL` and the objective is right.
Only the log has the warning, which is one more reason to keep and scan it.

<!-- practice 2 -->

## Two Settings That Should Agree and Do Not Are a Numerical Symptom

The warnings above are the solver's. The strongest test is your own: solve the same model in ways
that must give the same optimum, and compare. Presolve on or off, HiGHS or SCIP: none of these
changes which plans the model allows, so with a gap tolerance of 0 every run must report the same
best value. Gurobi's numerical guidelines give the same test: re-solve with another setting, and
treat a changed objective or status as a strong sign of numerical trouble. `cross_check.py` runs
all three variants four ways:

```python
for units in (TIGHT, HUGE_M, MIXED):
    answers = []
    for _, solver, params in WAYS:
        lm = build(small, units)
        result, _ = solve(lm.model, solver, params)
        answers.append(lm.in_k(result.objective_value()))
    flag = "agree" if max(answers) - min(answers) < 0.01 else "DISAGREE"
```

```text
objective in $k                                     HiGHS  HiGHS no presolve               SCIP   SCIP no presolve
tight ($k, M = credit line)                      23,161.5           23,161.5           23,161.5           23,161.5  agree
huge M ($k, M = 1e9)                             23,161.5           23,565.9           23,161.5           23,161.5  DISAGREE
mixed ($ objective, $M rows, M = 1e9)            23,161.5           23,161.5           23,161.5           23,668.9  DISAGREE
```

The tight model gives one answer four times. Each model with $`M = 10^9`$ gives a wrong one in one
of the four ways: HiGHS without presolve on `HUGE_M` (the free loans of lesson 10.1.1), and SCIP
without presolve on `MIXED`, $507.4k too high. Both wrong runs ended `OPTIMAL`, with nothing in
MathOpt's result to set them apart. With the defaults alone, all three models gave the right value, so a
team that only ever ran the defaults would never have seen it. The trouble was in the models all
along; the second run is what showed it.

Which settings to vary is a choice: presolve and the solver are cheap to change. Lesson 10.2.2
adds seeds and thread counts to the settings a run can vary. Run the comparison when a model changes, not every night: it doubles
the solve time, and a model that passed it keeps passing until its numbers change.

## Summary

- **HiGHS warns about large costs and bounds, but not about the matrix, so read the ranges
  yourself.** A $`10^{11}`$ matrix coefficient drew no warning.
- **A nonzero count lower than you built means a coefficient was dropped.** HiGHS treats entries
  at or below $`10^{-9}`$ as zero, silently.
- **The report's violation lines are the solver's audit of its own plan.** A nonzero integrality
  violation, even below the tolerance, points at a binary between whole numbers.
- **SCIP says when its best solution breaks a row of your model.** "best solution is not feasible
  in original problem" appeared in the log while MathOpt reported `OPTIMAL`.
- **Two settings that should agree and do not are a numerical symptom.** The tight model agreed
  four ways; each model with $`M = 10^9`$ disagreed once.

## Reference

| Where | Line | What it says |
| --- | --- | --- |
| HiGHS header | `Coefficient ranges:` then `Matrix`, `Cost`, `Bound`, `RHS` | the spans to check; no warning covers the matrix |
| HiGHS header | `WARNING: Problem has some excessively large costs` (or `row bounds`, `column bounds`; or `small`) | a cost, right-hand side or bound of $`10^7`$ or $`10^{11}`$ (none at $`10^5`$ or $`10^6`$), or of $`10^{-7}`$ |
| HiGHS header | `Consider scaling the objective by ..., or setting the user_objective_scale option to ...` | the power-of-two fix of lesson 10.1.2 |
| HiGHS first line | `... N nonzeros ...` | fewer than built: a coefficient at or below `small_matrix_value` ($`10^{-9}`$) was dropped |
| HiGHS report | `x (bound viol.)`, `x (int. viol.)`, `x (row viol.)` | the returned plan's largest violations; 0 on a well-scaled model |
| SCIP, after the report | `violation: ... is violated by ...` / `best solution is not feasible in original problem` | the translated solution breaks a row of the model you built |
| your own runs | different optima with presolve on and off, or with two solvers | the model's numbers are not trustworthy |

**Further reading:** [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (solvers check tolerances on a presolved model, which explains statuses such as GLOP's `IMPRECISE`, and GLOP's `solution_feasibility_tolerance`, checked after the solve to flag numerical trouble); [Gurobi: Does my Model have Numerical Issues?](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/modelissues.html) (the signs to look for: coefficient statistics, warnings in the log, the maximum violations after a solve, and results that change with a solver setting); [Gurobi: Numerical Issues guidelines](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide.html) (where numerical trouble comes from, and why reformulating beats changing parameters); [HiGHS options](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`small_matrix_value`, `mip_feasibility_tolerance`); [SCIP parameters](https://www.scipopt.org/doc/html/PARAMETERS.php) (`numerics/feastol`, and `display/allviols`, which lists every violation of the best solution).

## Challenges

1. A log shows `Matrix [1e-03, 1e+04]` and no warnings. Is the matrix span a concern by the
   guidelines in this lesson? What would you check next?
2. `dropped.py`'s $`10^{-9}`$ coefficient came from an emissions row written in tonnes per dollar.
   Which unit change brings it back above `small_matrix_value`, and what does it do to the row's
   other numbers?
3. Run `cross_check.py` with the `TIGHT` model's $`\bar M_y`$ doubled. Predict whether the four
   runs still agree.

## Design Note: Scan the Log Like a Test Report

A log is output nobody reads until something breaks. Treat its numerical lines the way a build
treats test failures: a short function that reads the lines kept with each solve and returns a list
of findings (warnings, a matrix span above a limit, nonzero violations, SCIP's
not-feasible-in-original line), stored with the plan and shown to whoever approves it. The function
is cheap; the night it finds something, it is the difference between a planner trusting a plan and
a planner finding a $980k overspend.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**warnings_grid.py.** One tiny model per number kind and magnitude, and the warnings HiGHS printed
for each (*HiGHS Warns About Large Costs and Bounds*). *Try:* Add $`5 \times 10^6`$ to the magnitudes.
Predict which kinds warn.

- Program: [warnings_grid.py](src/warnings_grid.py)

**dropped.py.** A one-row model with a coefficient of $`10^{-8}`$ and of $`10^{-9}`$, HiGHS's
nonzero count and the row as written (*A Nonzero Count Lower Than You Built*). *Try:* Set $`a`$ to
$`2 \times 10^{-9}`$. Predict the nonzero count and $`y`$.

- Program: [dropped.py](src/dropped.py)

**report.py.** HiGHS's solving report for a sound run and a leaky one, and SCIP's warning on the
`HUGE_M` model (*The Report's Violation Lines*, *SCIP Says When Its Best Solution Breaks a Row*).
*Try:* Solve the `TIGHT` model with SCIP instead. Predict whether the warning appears.

- Program: [report.py](src/report.py)

**cross_check.py.** Each variant solved by HiGHS and SCIP, with presolve on and off, and whether
the optima agree (*Two Settings That Should Agree and Do Not*). *Try:* Add a fifth way: HiGHS with
`relative_gap_tolerance` left at its default. Predict which rows still agree.

- Program: [cross_check.py](src/cross_check.py)

**loan_model.py.** The model builder and the helpers, shared with lessons 10.1.1 and 10.1.2.

- Library: [loan_model.py](src/loan_model.py)
