# 4.2.2 Reading `SolveResult`: Termination, Primal and Dual Solutions, Statistics

GridCap's nightly planning job solves the selection model and writes the plan to a report. One
night the budgets arrive truncated to $100k a year, and the job crashes with a `ValueError` from
`objective_value()`. Another night a time limit stops the solve early, and the job reports the plan
as optimal when it was not. Both bugs are the same bug: the job read the result without first asking
what kind of result it was.

`mathopt.solve` returns a `SolveResult`, and what it holds depends on how the solve ended. This
lesson reads every part of it, in the order a program should: the termination, then the plan and its
bounds, then the dual information an LP adds, then the statistics. Its programs solve the GridCap
selection model with HiGHS (and GLOP for the LPs) through MathOpt in OR-Tools 9.15. GridCap is a
fictional portfolio.

## The Model

Every program here solves GridCap small's project-selection model from lesson 4.2.1, either as the
MILP or as its LP relaxation (each $`x_i`$ allowed anywhere in $`[0, 1]`$).

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years; $`M \subseteq P`$ the must-do
projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$ the child projects, with parent
$`p(c)`$.

**Parameters.** $`v_i`$, the NPV of project $`i`$ at its earliest start ($k); $`c_{i,y}`$, what it
spends in year $`y`$ ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$ (MILP), or $`0 \le x_i \le 1`$ (LP relaxation).

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

## Read the Termination First: Its Reason Says What the Rest Holds

A `SolveResult` has five main parts: `termination` (how the solve ended), `solutions` (the plans
found, best first), `primal_rays` and `dual_rays` (certificates for unbounded and infeasible models),
and `solve_stats` (what the search did). SCIP, PDLP and OSQP also attach output of their own. The OR-Tools samples all read `termination` before anything
else, and so does every program here:

```python
small = generate("small")
sel = build(small)
result = solve(sel.model, mathopt.SolverType.HIGHS)

# 1. Termination: how the solve ended, and what the solver claims about the problem.
term = result.termination
print("reason        :", term.reason.name)
print("limit         :", term.limit)
print("detail        :", repr(term.detail))
print("problem_status:", term.problem_status.primal_status.name, "/", term.problem_status.dual_status.name)
print("bounds        :", term.objective_bounds.primal_bound, "/", term.objective_bounds.dual_bound)
```

```text
reason        : OPTIMAL
limit         : None
detail        : 'HighsModelStatus is kOptimal'
problem_status: FEASIBLE / FEASIBLE
bounds        : 22532.0 / 22532.0
```

`termination` is a small record with five fields:

- **`reason`** is a `TerminationReason`, the one field every program must check. The table below lists
  all nine.
- **`limit`** says which limit stopped the solve. It is set only when `reason` is `FEASIBLE` or
  `NO_SOLUTION_FOUND` (both mean "a limit stopped me"), and `None` otherwise.
- **`detail`** is free text from the solver: here HiGHS's own status name. It is for logs, not for
  code: each solver words it differently.
- **`problem_status`** is the solver's *claim* about the model itself, separate from what it found: is
  the primal problem (your model) feasible, and is the dual problem feasible? Each is a
  `FeasibilityStatus`: `FEASIBLE`, `INFEASIBLE` or `UNDETERMINED`. Both `FEASIBLE`, as here, means the
  model has plans and a finite best value.
- **`objective_bounds`** holds the two numbers of lesson 3.4.1: the **primal bound**, the value of the
  best plan found, and the **dual bound**, a value no plan can beat. Equal bounds, as here, are a proof
  of optimality.

The nine reasons, from MathOpt's `TerminationReason` docstring, grouped by what they leave you:

| `reason` | Meaning | A plan to read? |
| --- | --- | --- |
| `OPTIMAL` | a plan proven best, within the solver's tolerances (including a gap tolerance, lesson 3.4.2) | always |
| `FEASIBLE` | a limit stopped the solve after it found a plan; `limit` says which | always |
| `NO_SOLUTION_FOUND` | a limit stopped the solve before it found any plan | never |
| `INFEASIBLE` | proven: no plan satisfies every row | never |
| `UNBOUNDED` | proven: plans exist whose objective is as good as you like | sometimes (see below) |
| `INFEASIBLE_OR_UNBOUNDED` | one of the two, and the solver cannot say which | never |
| `IMPRECISE` | solved, but some tolerance was missed | maybe, slightly off |
| `NUMERICAL_ERROR` | the solver hit an unrecoverable numerical problem | never |
| `OTHER_ERROR` | some other error stopped the solver | never |

The `limit` values, from the `Limit` docstring: `ITERATION`, `TIME`, `NODE`, `SOLUTION`, `MEMORY`,
`OBJECTIVE`, `NORM`, `INTERRUPTED`, `SLOW_PROGRESS`, `OTHER`, and `UNDETERMINED` when the solver
does not say which limit it reached.

## The Plan Is the First Solution, and objective_value Raises When There Is None

The plan the solver found is the **primal solution**: a value for every variable. Read it through
`objective_value()` and `variable_values()`:

```python
# 2. The primal solution: the plan and its value.
print("has_primal_feasible_solution:", result.has_primal_feasible_solution())
print("objective_value:", result.objective_value(), "| best_objective_bound:", result.best_objective_bound())
x = sel.x
print("one variable   :", result.variable_values(x["P001"]))
print("a list         :", result.variable_values([x["P001"], x["P002"], x["P003"]]))
print("all, as a dict :", len(result.variable_values()), "entries")
```

```text
has_primal_feasible_solution: True
objective_value: 22532.0 | best_objective_bound: 22532.0
one variable   : 1.0
a list         : [1.0, 0.0, 1.0]
all, as a dict : 40 entries
```

`variable_values` takes one variable (and returns a float), a list of variables (a list), or nothing
(a dict from every variable to its value). `best_objective_bound()` is the dual bound under another
name. Both `objective_value()` and `variable_values()` read `result.solutions[0]`, the best plan, and
both raise `ValueError` when there is no feasible plan to read. `has_primal_feasible_solution()` says
in advance whether they will. The `SolveResult` docstring promises it is `True` whenever the reason is
`OPTIMAL` or `FEASIBLE`.

So what does each ending leave? The program solves six variants, from the GridCap model with its
budgets cut to $100k a year to an LP whose variable `x` has no upper bound, and prints the same
fields for each:

```python
for label, model, solver, params in cases:
    result = solve(model, solver, params)
    term = result.termination
    status = term.problem_status
    try:
        value = f"{result.objective_value():,.1f}"
    except ValueError:
        value = "ValueError"
    limit = term.limit.name if term.limit else "-"
    print(f"{label}")
    print(f"  {term.reason.name:<23} limit {limit:<9} primal/dual status {status.primal_status.name}/{status.dual_status.name}")
    print(f"  has plan {result.has_primal_feasible_solution()!s:<5}  objective_value {value:<10}"
          f"  primal_bound {result.primal_bound():,.1f}  dual_bound {result.dual_bound():,.1f}")
```

```text
GridCap small, HiGHS
  OPTIMAL                 limit -         primal/dual status FEASIBLE/FEASIBLE
  has plan True   objective_value 22,532.0    primal_bound 22,532.0  dual_bound 22,532.0
solution_limit=1, HiGHS
  FEASIBLE                limit SOLUTION  primal/dual status FEASIBLE/FEASIBLE
  has plan True   objective_value 20,594.0    primal_bound 20,594.0  dual_bound 23,669.0
iteration_limit=1, LP, HiGHS
  NO_SOLUTION_FOUND       limit ITERATION primal/dual status UNDETERMINED/UNDETERMINED
  has plan False  objective_value ValueError  primal_bound -inf  dual_bound inf
budgets of $100k, HiGHS
  INFEASIBLE              limit -         primal/dual status INFEASIBLE/FEASIBLE
  has plan False  objective_value ValueError  primal_bound -inf  dual_bound -inf
x unbounded, HiGHS
  UNBOUNDED               limit -         primal/dual status FEASIBLE/INFEASIBLE
  has plan True   objective_value 0.0         primal_bound inf  dual_bound inf
x unbounded, GLOP
  INFEASIBLE_OR_UNBOUNDED limit -         primal/dual status UNDETERMINED/UNDETERMINED
  has plan False  objective_value ValueError  primal_bound -inf  dual_bound inf
```

Read it row by row:

- **`FEASIBLE`** came with a plan worth $20,594k and the limit that stopped the search, `SOLUTION`
  (stop at the first plan found). The dual bound, $23,669k, says the best plan might be worth up to
  $3,075k more. Report this plan with its gap (lesson 3.4.1), never as "the optimum".
- **`NO_SOLUTION_FOUND`** stopped after one simplex iteration with nothing to show: no plan, and
  `objective_value()` raises. The limit field still says why, so the job can raise the limit and retry.
- **`INFEASIBLE`** is a proof, not a failure: the must-do projects cost more than $100k in some year.
  There is nothing to read, and the fix is in the data or the rules (section 9 finds which rows clash).
- **`UNBOUNDED`** from HiGHS came with a feasible point whose value is 0.0, while the primal bound is
  $`+\infty`$. That plan is only a witness that plans exist; it is not a "best" anything. So a program
  must not treat "has a plan" as "has a useful plan": the reason decides.
- **`INFEASIBLE_OR_UNBOUNDED`** is the same model on GLOP, which proved there is no finite optimum but
  not which of the two causes it is. As in lesson 4.2.1, the usual cause is a missing bound.

The bounds follow one convention, for a maximization: the primal bound is the value of the best plan
found, so $`-\infty`$ when there is none; the dual bound is the best value any plan could have, so
$`+\infty`$ when nothing is proven, and $`-\infty`$ when the model is proven infeasible (no plan can
have any value). For a minimization every sign flips. `primal_bound()` and `dual_bound()` never raise,
which makes them the safe numbers to log for every ending.

## A Handler Turns the Reason Into What the Caller Should Do

Put together, a program's first lines after a solve are a decision on `termination.reason`, and the
three answers a caller needs are: is there a plan, can it be called optimal, and if not, why not.

| `reason` | Plan? | What the caller does |
| --- | --- | --- |
| `OPTIMAL` | yes | use it |
| `FEASIBLE` | yes | use it, report the gap and the `limit` |
| `NO_SOLUTION_FOUND` | no | report the `limit`; raise it or retry |
| `INFEASIBLE` | no | report a data or rule conflict |
| `UNBOUNDED`, `INFEASIBLE_OR_UNBOUNDED` | no usable plan | report a modeling error (a missing bound) |
| `IMPRECISE`, `NUMERICAL_ERROR`, `OTHER_ERROR` | no | report a solver failure, with `detail` |

Write it as one function with one branch per row, and never as `if reason == OPTIMAL: ... else:
crash`: the `else` is where the nightly job's two bugs lived.

<!-- practice 1 -->

## Dual Values, Reduced Costs and a Basis Come Only From an LP Solve

The read above asked for one more thing, and got an error:

```python
# 3. The dual solution: a MILP has none.
print("has_dual_feasible_solution:", result.has_dual_feasible_solution())
try:
    result.dual_values(sel.budget[2027])
except ValueError as error:
    print("dual_values raised ValueError:", error)
```

```text
has_dual_feasible_solution: False
dual_values raised ValueError: Best solution does not have an associated dual feasible solution.
```

A **dual solution** prices the rows: the dual value of a row is how much the objective would improve
per unit of extra right-hand side (lesson 2.3.1). It exists for LPs, because an LP is convex; a MILP's
best value jumps when the budget crosses a project's cost, so it has no such prices, and MathOpt
returns none. The `SolveResult` docstring states the rule: dual solutions are given only for convex
problems such as LPs, not for integer programs.

An LP solve with a simplex solver returns three extras. The program below adapts the OR-Tools sample
`advanced_linear_programming.py`, which reads all three:

```python
model = mathopt.Model(name="advanced_linear_programming")
x = [model.add_variable(lb=0.0, name=f"x{j}") for j in range(3)]
constraints = [
    model.add_linear_constraint(10 * x[0] + 4 * x[1] + 5 * x[2] <= 600, name="c1"),
    model.add_linear_constraint(2 * x[0] + 2 * x[1] + 6 * x[2] <= 300, name="c2"),
    model.add_linear_constraint(mathopt.fast_sum(x) <= 100, name="c3"),
]
model.maximize(10 * x[0] + 6 * x[1] + 4 * x[2])

result = mathopt.solve(model, mathopt.SolverType.GLOP)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"model failed to solve to optimality: {result.termination}")
print("objective  :", round(result.objective_value(), 4))
print("values     :", [round(v, 4) for v in result.variable_values(x)])
if not result.has_dual_feasible_solution():
    raise RuntimeError("no dual solution was returned on optimal")
print("duals      :", [round(d, 4) + 0.0 for d in result.dual_values(constraints)])   # + 0.0 turns -0.0 into 0.0
print("reduced    :", [round(r, 4) for r in result.reduced_costs(x)])
if not result.has_basis():
    raise RuntimeError("no basis was returned on optimal")
print("row status :", [s.name for s in result.constraint_status(constraints)])
print("var status :", [s.name for s in result.variable_status(x)])
```

```text
objective  : 733.3333
values     : [33.3333, 66.6667, 0.0]
duals      : [0.6667, 0.0, 3.3333]
reduced    : [0.0, 0.0, -2.6667]
row status : ['AT_UPPER_BOUND', 'BASIC', 'AT_UPPER_BOUND']
var status : ['BASIC', 'BASIC', 'AT_LOWER_BOUND']
```

- **`dual_values(rows)`**: one more unit of `c1`'s right-hand side (601 instead of 600) is worth about
  0.6667 of objective, and `c3`'s about 3.3333. `c2` has slack, so its price is 0.
- **`reduced_costs(variables)`**: `x2` is at its bound 0, and its reduced cost, $`-2.6667`$, is how much
  each unit of `x2` forced into the plan would cost the objective (lesson 2.3.3).
- **`constraint_status` and `variable_status`** give the simplex **basis**: which rows are tight
  (`AT_UPPER_BOUND`) and which variables are `BASIC` (strictly between their bounds) or sit at a bound.
  Only simplex solvers return one, and it is what lets a solver restart quickly after a small change.

The sample checks `has_dual_feasible_solution()` and `has_basis()` before reading, because MathOpt
does not require a solver to return either one even on `OPTIMAL`. Do the same. The same reading on
GridCap small's LP relaxation prices each year's budget:

```python
sel = build(generate("small"), integer=False)
relaxed = solve(sel.model, mathopt.SolverType.GLOP)
print("LP relaxation:", relaxed.termination.reason.name, round(relaxed.objective_value(), 1))
for year, row in sel.budget.items():
    dual = round(relaxed.dual_values(row), 4) + 0.0
    print(f"  {row.name}: dual {dual:.4f}  status {relaxed.constraint_status(row).name}")
```

```text
LP relaxation: OPTIMAL 23669.5
  budget_2027: dual 0.6475  status AT_UPPER_BOUND
  budget_2028: dual 0.5765  status AT_UPPER_BOUND
  budget_2029: dual 0.0000  status BASIC
  budget_2030: dual 1.3817  status AT_UPPER_BOUND
  budget_2031: dual 0.0000  status BASIC
```

In the relaxation, one more $k of 2030 budget is worth about $1.38k of NPV, and 2029 and 2031 have
money to spare. Those are LP prices: they describe the relaxed model, not the yes/no plan (lesson
2.3.3 says what they do and do not mean for a MILP). Lesson 4.2.3 shows which solvers return duals at
all.

<!-- practice 2 -->

## Statistics Describe the Search, and the Solution List Can Hold More Than One Plan

The last part of the result says how much work the solve took:

```python
# 4. Statistics: what the search did.
stats = result.solve_stats
print("nodes:", stats.node_count, "| simplex iterations:", stats.simplex_iterations,
      "| solve_time is a", type(stats.solve_time).__name__)
```

```text
nodes: 1 | simplex iterations: 29 | solve_time is a timedelta
```

`solve_stats` has `node_count` (branch-and-bound nodes, lesson 3.2.1), `simplex_iterations`,
`barrier_iterations`, `first_order_iterations` (PDLP's steps) and `solve_time`, a `timedelta`
measured around the solver call (not counting the model build). HiGHS solved GridCap small at the
root node. Use these numbers to compare runs and to watch a job's health over time, but never
assert on them in a test: `solve_time` changes on every run, and the counts describe one search,
which a different solver, solver version or setting changes. Test the plan and its value instead.

`result.solutions` is a list, best first. Every solve so far read one plan from it, but a solver
that keeps a **solution pool** can return several, when asked with the common parameter
`solution_pool_size`:

```python
sel = build(generate("small"))
for solver in (mathopt.SolverType.GSCIP, mathopt.SolverType.HIGHS):
    result = solve(sel.model, solver, mathopt.SolveParameters(solution_pool_size=5)
                   if solver == mathopt.SolverType.GSCIP else None)
    values = [round(s.primal_solution.objective_value) for s in result.solutions]
    print(f"{solver.name}: len(result.solutions) = {len(result.solutions)}, objective values {values}")

best = result.solutions[0].primal_solution
print("solutions[0] is what objective_value() reads:", best.objective_value == result.objective_value())
```

```text
GSCIP: len(result.solutions) = 5, objective values [22532, 22481, 22461, 22302, 22182]
HIGHS: len(result.solutions) = 1, objective values [22532]
solutions[0] is what objective_value() reads: True
```

SCIP returned the optimum and four runners-up it met during the search. They are not "the five best
plans", only five plans it kept, but they answer a planner's favourite follow-up question ("what else
was close?") at no extra cost. HiGHS was not asked: lesson 4.2.4 shows it refuses
`solution_pool_size`. Each entry of `solutions` has a `primal_solution` (with `variable_values`,
`objective_value` and a `feasibility_status`), and for an LP a `dual_solution` and a `basis`.

## Summary

- **Read the termination first.** `reason` says what the rest of the result holds; `limit` says which
  limit stopped a `FEASIBLE` or `NO_SOLUTION_FOUND` solve; `detail` is the solver's own text.
- **The plan is `solutions[0]`.** `objective_value()` and `variable_values()` raise `ValueError` when
  there is none; `has_primal_feasible_solution()` says whether there is. An `UNBOUNDED` result may
  carry a plan that means nothing.
- **The bounds are always there.** `primal_bound()` and `dual_bound()` never raise; infinite values
  encode "nothing found" and "nothing proven".
- **A handler maps each reason to what the caller does,** with no catch-all branch.
- **Dual values, reduced costs and a basis come only from an LP solve**, and a program checks
  `has_dual_feasible_solution()` and `has_basis()` before reading them.
- **Statistics describe the search;** time and some solvers' counts change between runs, so log them
  and never assert on them.

## Reference

| Read | How | Raises when |
| --- | --- | --- |
| why it stopped | `result.termination.reason`, `.limit`, `.detail` | never |
| feasibility claims | `result.termination.problem_status.primal_status`, `.dual_status` | never |
| bounds | `result.primal_bound()`, `result.dual_bound()` (= `best_objective_bound()`) | never |
| the plan | `result.objective_value()`, `result.variable_values(v)` | no primal feasible solution |
| is there a plan | `result.has_primal_feasible_solution()` | never |
| LP prices | `result.dual_values(rows)`, `result.reduced_costs(vars)` | no dual feasible solution |
| simplex basis | `result.constraint_status(rows)`, `result.variable_status(vars)` | no basis |
| all plans | `result.solutions`, each with `.primal_solution`, `.dual_solution`, `.basis` | never |
| work done | `result.solve_stats.node_count`, `.simplex_iterations`, `.solve_time`, ... | never |

**Further reading:** [MathOpt `result.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (the docstrings of `TerminationReason`, `Limit`, `ProblemStatus`, `ObjectiveBounds` and `SolveResult`, including which fields each ending fills); [MathOpt `result.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/result.proto) (the same contract at the protocol level, where every `limit` value is defined); [MathOpt sample advanced_linear_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py) (the LP whose duals, reduced costs and basis this lesson reads); [MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (accepting `OPTIMAL` or `FEASIBLE` before reading a MIP's values); [MathOpt basic example (OR-Tools)](https://developers.google.com/optimization/math_opt/basic_example) (checking the termination reason before reading the solution).

## Challenges

1. Solve GridCap small with `solution_limit=2` on HiGHS. Is the gap smaller than with 1?
2. What are the two bounds of a *minimization* that is proven infeasible? Build one and check.
3. Write a function that logs one line per solve with `reason`, `limit`, both bounds and the node
   count, and call it after every solve in this lesson's programs.

## Design Note: A Result Is a Claim, Not a Proof You Have Checked

Every field of `SolveResult` is what the solver *claims*. MathOpt's own docstrings say so: the
termination reasons are as reported by the solver, which is not required to return a certificate,
and `OPTIMAL` means optimal within the solver's tolerances. For a planning job that means a cheap
check after the solve is worth having: recompute each year's spend from the plan with plain Python
(or `evaluate_expression`) and compare it with the budget. A plan that breaks a row by more than the
tolerance is a bug to report, whatever the status said. Section 10 returns to tolerances, and section
12 turns such checks into tests.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**read_result.py.** Every part of a `SolveResult`, read from one HiGHS solve of the GridCap small MILP (*Read the Termination First*, *The Plan Is the First Solution*, *Dual Values*, *Statistics*). *Try:* Solve the LP relaxation instead (`build(small, integer=False)`). Predict which lines change.

- Program: [read_result.py](src/read_result.py)

**endings.py.** Six variants of the model, each ending with a different reason, and what each result carries (*The Plan Is the First Solution*). *Try:* Give the infeasible case budgets of $3,000k a year. Predict the reason first.

- Program: [endings.py](src/endings.py)

**lp_result.py.** Adapted from the OR-Tools sample `advanced_linear_programming.py`: duals, reduced costs and the basis of an LP, then the budget prices of GridCap small's LP relaxation (*Dual Values, Reduced Costs and a Basis*). *Try:* Raise `c1`'s right-hand side from 600 to 601 and solve again. Predict the new objective from the dual value.

- Program: [lp_result.py](src/lp_result.py)

**solution_pool.py.** SCIP's solution pool and HiGHS's single plan (*Statistics Describe the Search*). *Try:* Ask SCIP for a pool of 10. Predict whether all ten values are different.

- Program: [solution_pool.py](src/solution_pool.py)
