# 4.3.3 Solution Hints and `ModelSolveParameters`

Every month GridCap's planners re-solve the five-year plan after small changes: a revised cost
here, a little more budget there. Last month's approved plan is sitting in a file, and it is
usually close to this month's answer. Can the solver start from it instead of from nothing? This
lesson shows how to hand a MIP solver a starting plan, a **solution hint**, through MathOpt; how to
tell from the solver's log whether it used the hint (the result alone cannot tell you); and the
other fields of `ModelSolveParameters`, the object that carries everything about a solve that is
tied to this particular model. GridCap is a fictional utility.

## The Model

The multi-period timing model of lesson 4.3.1, with this month's one change marked. Its decisions
are start-time variables: $`x_{i,t}= 1`$ if project $`i`$ starts in year $`t`$ of its window
$`T_i`$; a project starts at most once and spends its cost profile from its start year on.
(Lesson 6.4.1, in section 6, builds this model step by step.) A hint changes nothing in
the model: it is advice to the solver about where to look, not a rule about which plans are allowed.

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the
child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, project $`i`$'s spend in its $`k`$-th year
of work ($k); $`B_y`$, the budget of year $`y`$ ($k), **with $`B_{2031}`$ raised by 200 this
month**.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$.

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
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow B_{2031} + 200
\end{aligned}
```

Raising a budget only adds plans, so last month's plan still satisfies every row. That makes it a
**feasible** hint, the best kind.

## A Hint Is a Starting Plan, Passed in `ModelSolveParameters`

MathOpt splits a solve's settings in two:

- `SolveParameters` (lesson 4.2.4) holds settings that make sense for any model: time limit, gap,
  threads, log output.
- `ModelSolveParameters` holds settings that name this model's variables or rows, so they cannot be
  written before the model exists: hints, filters, a starting basis, per-objective tolerances
  (lesson 4.3.2).

A hint is a `SolutionHint`: a dict from variables to values (`variable_values`), plus, for LP
solvers, a dict from rows to dual values (`dual_values`). It goes into
`ModelSolveParameters(solution_hints=[...])`, a list, and the parameters go to `solve` as
`model_params`:

```python
approved = {v: round(last.variable_values(v)) for v in pm.x.values()}
```

```python
complete = mathopt.SolutionHint(variable_values=approved)                         # every x, 0 or 1
partial = mathopt.SolutionHint(variable_values={v: 1.0 for v, a in approved.items() if a == 1})
wrong = mathopt.SolutionHint(variable_values={v: 1.0 for v in pm.x.values()})      # every start at once
```

```python
result = solve(pm.model, solver, model_params=mathopt.ModelSolveParameters(solution_hints=[hint]),
               msg_cb=mathopt.list_message_callback(log))
```

```text
last month    NPV 24,260, 27 projects started
hint sizes: complete 80, partial 27, wrong 80 of 80 variables
```

`round` turns each value of last month's result into an exact 0 or 1: a solver returns values like
0.9999999 for a binary, and a hint should say what the plan is, not repeat the round-off. Three
hints of three kinds:

- **complete**: a value for every one of the 80 variables, and the plan they describe is allowed;
- **partial**: values for only some variables, here the 27 starts that were 1; the solver has to
  fill in the rest;
- **wrong**: values for every variable that break the rules (every project started in every year).

The `SolutionHint` docstring says what a solver may do with each: many MIP solvers accept partial
or infeasible hints and solve a small sub-MIP (a MIP over the unhinted or conflicting variables) to
complete or repair them. A solver that accepts only one hint uses the first one in the list. Two
facts about the API are easy to get wrong: MathOpt has no `model.add_solution_hint()`, the hint
goes only through `ModelSolveParameters`; and CP-SAT's own API (lesson 4.6.2 teaches it) uses a
different call, `model.add_hint`, for the same idea.

<!-- practice 1 -->

## Only the Log Says Whether a Hint Was Used

The docstring is frank about the rest: how a hint is used, if at all, depends on the solver, and the
reliable way to know is to read the solver's log with and without it. MathOpt passes each log line
to a **message callback**, `msg_cb`, during the solve; `mathopt.list_message_callback(log)` makes
one that appends the lines to a list. The program solves with each hint on each MIP solver and keeps
only the log lines about hints:

```python
WORDS = {mathopt.SolverType.HIGHS: ("MIP start", "User-supplied", "user-supplied"),
         mathopt.SolverType.GSCIP: ("solution candidate storage",),
         mathopt.SolverType.CP_SAT: ("The solution hint",)}
```

```text
HIGHS  complete NPV 24,298  log: ['MIP start solution is feasible, objective value is 24260']
HIGHS  partial  NPV 24,298  log: ['Attempting to find feasible solution by solving MIP for user-supplied values of 27 / 80 discrete variables', 'MIP start solution is feasible, objective value is 24260']
HIGHS  wrong    NPV 24,298  log: ['User-supplied values of discrete variables cannot yield feasible solution']
GSCIP  complete NPV 24,298  log: ['1/1 feasible solution given by solution candidate storage, new primal bound 2.426000e+04']
GSCIP  partial  NPV 24,298  log: nothing about it
GSCIP  wrong    NPV 24,298  log: nothing about it
CP_SAT complete NPV 24,298  log: ['The solution hint is complete and is feasible.']
CP_SAT partial  NPV 24,298  log: ['The solution hint is incomplete: 25 out of 76 non fixed variables hinted.', 'The solution hint is incomplete: 26 out of 79 non fixed variables hinted.']
CP_SAT wrong    NPV 24,298  log: ['The solution hint is complete, but it is infeasible! we will try to repair it.']
```

Read it solver by solver.

- **HiGHS** calls a hint a "MIP start". The complete hint was checked and accepted as a first
  incumbent worth 24,260, last month's NPV. For the partial hint, HiGHS solved a sub-MIP with the 27
  hinted values fixed and completed it into the same plan. The wrong hint was rejected outright.
- **SCIP** stores a hint as a "solution candidate". The complete one became its first incumbent
  ("new primal bound 2.426000e+04", that is, 24,260). For the partial and the wrong hints its log has
  no line at all: from the log, you cannot tell that SCIP did anything with them.
- **CP-SAT** checks the hint before searching: complete and feasible; incomplete (it reports how
  many of the variables still free after presolve were hinted, twice, as its presolve runs in
  stages); or complete but infeasible, which it then tries to repair.

And in every row the answer is the same: NPV 24,298, this month's optimum, $38k above last month
thanks to the extra $200k. A hint never changes the answer of a solve that runs to optimality. It
can change how fast a good plan is found, which matters when a time limit stops the solve early
(lesson 3.4.2), and the log is where to see whether it had the chance.

<!-- practice 2 -->

## Filters Choose Which Values Come Back

A large model's result holds a value for every variable, most of them 0 in a selection model.
`ModelSolveParameters` can ask for less. `variable_values_filter` takes a `VariableFilter`:
`skip_zero_values=True` drops the zeros, `filtered_items=[...]` keeps only the variables listed.
(`dual_values_filter` and `reduced_costs_filter` do the same for an LP's duals and reduced costs.)

```python
nonzero = mathopt.ModelSolveParameters(variable_values_filter=mathopt.VariableFilter(skip_zero_values=True))
```

```python
watch = [pm.x["P032", t] for t in small.project("P032").starts()]
only = mathopt.ModelSolveParameters(variable_values_filter=mathopt.VariableFilter(filtered_items=watch))
```

The program prints how many values each solver returned, and every returned value that is not
exactly 1:

```text
HIGHS skip_zero_values: 28 values back, not 1: {'x_P018_2031': -2.220446049250313e-15}
GSCIP skip_zero_values: 27 values back, not 1: {}
filtered_items: {'x_P032_2027': 1.0, 'x_P032_2028': 0.0, 'x_P032_2029': 0.0}
```

The plan starts 27 projects. SCIP returned exactly their 27 values. HiGHS returned 28: one variable
came back as $`-2.2 \times 10^{-15}`$, a binary that is 0 up to floating-point round-off, and
"skip zero values" skips only values that are exactly zero. So a filter shortens the result; it
does not clean it. Read a binary as chosen when its value is above 0.5, never when it is "not
zero". `filtered_items` returns its variables whatever their values, zeros included.

## An LP Starts From a Basis, Not a Hint

For an LP solved by simplex, the useful starting point is not a plan but a **basis**: the record of
which variables and rows were at their bounds at the last vertex (lesson 2.4.1). The `SolutionHint`
docstring says simplex solvers prefer a basis to a hint. Lesson 2.4.3 kept one solver alive across
solves to reuse its basis; `ModelSolveParameters(initial_basis=...)` hands a basis saved from one
result to a new, separate solve:

```python
for v in lp.x.values():
    v.integer = False                                    # the LP relaxation, in place
first = solve(lp.model, mathopt.SolverType.GLOP)
basis = first.solutions[0].basis
lp.budget[2030].upper_bound *= 0.9
cold = solve(lp.model, mathopt.SolverType.GLOP)
warm = solve(lp.model, mathopt.SolverType.GLOP, model_params=mathopt.ModelSolveParameters(initial_basis=basis))
```

```text
GLOP after a 2030 cut: cold 338 iterations, from the old basis 32; objectives 225,053.56 and 225,053.56
```

The medium portfolio's LP relaxation (each `x` made continuous by setting `integer = False`), with
the 2030 budget cut by 10%: from scratch, GLOP needed 338 simplex iterations; from the basis of the
solve before the cut, 32, to the same objective. A basis can be stored with the result and used by
any later process; a kept-alive solver cannot.

## Some Fields Are Requests a Solver May Ignore

Two more fields describe how the solver should work rather than what it returns:

- `branching_priorities={variable: int}`: branch on higher-priority variables first (lesson 3.2.1
  explains branching);
- `lazy_linear_constraints={row, ...}`: rows the solver may hold back and add only when a solution
  breaks them. The docstring says this changes no plan's feasibility and that solvers without
  support ignore it.

```python
extras = mathopt.ModelSolveParameters(branching_priorities={pm.x["P032", 2027]: 10},
                                      lazy_linear_constraints={pm.budget[2027]})
```

```text
HIGHS  priorities + lazy rows: OPTIMAL, NPV 24,260
GSCIP  priorities + lazy rows: OPTIMAL, NPV 24,260
CP_SAT priorities + lazy rows: OPTIMAL, NPV 24,260
```

All three solvers accept both fields and return the optimum. Whether any of them acted on them, the
output cannot say, and this lesson does not claim it. Treat such fields like a hint: advice whose
effect you measure, in the log or in the time to a good plan, on your own model.

`ModelSolveParameters`, field by field:

| Field | What it carries | Checked here |
| --- | --- | --- |
| `solution_hints` | starting plans for a MIP (first one used if the solver takes one) | HiGHS, SCIP, CP-SAT log it |
| `initial_basis` | a simplex basis from an earlier result | GLOP: 32 iterations against 338 |
| `variable_values_filter`, `dual_values_filter`, `reduced_costs_filter` | which values to return | exact zeros only |
| `objective_parameters` | per-objective tolerances and time limits (lesson 4.3.2) | refused with the objectives |
| `branching_priorities` | branching order | accepted; effect not measured |
| `lazy_linear_constraints` | rows the solver may add on demand | accepted; effect not measured |

## Summary

- **A hint is a starting plan, passed in `ModelSolveParameters`.**
  `ModelSolveParameters(solution_hints=[SolutionHint(variable_values={...})])`, given to `solve` as
  `model_params`; it may be complete or partial.
- **Only the log says whether a hint was used.** HiGHS, SCIP and CP-SAT each log a complete
  feasible hint; HiGHS completes a partial one and rejects a wrong one; SCIP's log is silent on both.
  The optimum is the same with any hint.
- **Filters choose which values come back.** `skip_zero_values` drops exact zeros only: HiGHS
  returned a $`-2.2 \times 10^{-15}`$.
- **An LP starts from a basis, not a hint.** `initial_basis` cut GLOP's re-solve from 338 iterations
  to 32.
- **Some fields are requests a solver may ignore.** Branching priorities and lazy rows were accepted
  by every MIP solver here; their effect is for you to measure.

## Reference

| Task | Code |
| --- | --- |
| hint a plan | `mathopt.ModelSolveParameters(solution_hints=[mathopt.SolutionHint(variable_values={x: 1.0, ...})])` |
| pass it | `mathopt.solve(model, solver, model_params=params)` |
| keep the log | `log = []`, then `msg_cb=mathopt.list_message_callback(log)` |
| fewer values back | `variable_values_filter=mathopt.VariableFilter(skip_zero_values=True)` or `(filtered_items=[...])` |
| reuse a simplex basis | `initial_basis=result.solutions[0].basis` |

| Log line | Solver | Means |
| --- | --- | --- |
| `MIP start solution is feasible, objective value is ...` | HiGHS | hint accepted as an incumbent |
| `Attempting to find feasible solution by solving MIP for user-supplied values of k / n ...` | HiGHS | partial hint being completed |
| `User-supplied values of discrete variables cannot yield feasible solution` | HiGHS | hint rejected |
| `... feasible solution given by solution candidate storage ...` | SCIP | hint accepted as an incumbent |
| `The solution hint is complete and is feasible.` | CP-SAT | hint accepted |
| `The solution hint is incomplete: ...` / `... complete, but it is infeasible! ...` | CP-SAT | partial hint; infeasible hint to repair |

**Further reading.** OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt): warm
starts by solution or by basis among MathOpt's features. The `SolutionHint` and
`ModelSolveParameters` docstrings in
[`model_parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py):
partial and infeasible hints, reading the log to see a hint's effect, and every field in the table
above. The `solve` docstring in
[`solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py)
(`model_params`, `msg_cb`), and
[`remote_solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/remote_solve.py),
the one MathOpt sample that passes a message callback.

## Challenges

1. Hint last month's plan after a 10% cut to the 2029 budget, so that it no longer fits. Predict
   which of the three solvers' log lines you will see, then run it.
2. Pass two hints in the list, the wrong one first. Which one does HiGHS report?
3. A colleague says "the hint made no difference: the objective is the same". What would you ask
   them to look at instead?

## Design Note: Keep Last Month's Plan as Values, Not as a Result

`hints.py` turns last month's result into a plain dict of rounded values before it builds any
hint. A `SolveResult` belongs to the model and the run that made it; a dict of 0s and 1s keyed by
project and year can be saved, compared with this month's plan, and turned into a hint for any
model that has the same decisions. Keep plans as data, and hints, comparisons and reports all start
from the same place.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**hints.py.** Last month's plan as a complete, a partial and a wrong hint, on HiGHS, SCIP and CP-SAT,
with the log lines about each (*A Hint Is a Starting Plan*, *Only the Log Says Whether a Hint Was
Used*). *Try:* Hint only the projects started in 2027 and predict HiGHS's "k / n" numbers.

- Program: [hints.py](src/hints.py)

**model_params.py.** Value filters on HiGHS and SCIP, a starting basis for GLOP, and branching
priorities and lazy rows on every MIP solver (*Filters*, *An LP Starts From a Basis*, *Some Fields Are
Requests*). *Try:* Cut the 2030 budget by 30% instead of 10% and predict whether the old basis still
saves most of the iterations.

- Program: [model_params.py](src/model_params.py)
