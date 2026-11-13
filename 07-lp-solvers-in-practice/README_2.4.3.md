# 2.4.3 Re-Solving After the Data Changes

Finance has news for GridCap's planners: the 2030 budget may be cut by 10%. Before the meeting
that decides it, the planners want the funding LP of lesson 2.4.1 answered under the cut, and
under a dozen other what-ifs: a revised NPV here, a new candidate project there, a cap on how much
money may be carried. Each what-if changes a few numbers of a model that is otherwise the same.
This lesson shows how to make those changes in the model you already have, how a solver can start
from its previous answer instead of from nothing, which changes that helps with, and when the dual
value of a row answers the question without solving at all. GridCap is a fictional utility; its
numbers are teaching data.

## The Model

The funding LP of lesson 2.4.1, whole, with the data this lesson changes marked. The changes are
data, not new kinds of rows, except a new project and a new rule in the section on other changes,
which are marked too.

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years, the first being $`y_0`$;
$`M \subseteq P`$ the must-do projects.

**Parameters.** $`c_{i,y}`$, what project $`i`$ spends in year $`y`$ if it starts at its earliest
start ($k, 0 in a year it is not worked); $`v_i`$, its NPV at its earliest start ($k), **revised
for one project in this lesson**; $`B_y`$, the budget of year $`y`$ ($k), **cut for 2030 in this
lesson**.

**Variables.** $`0 \le f_i \le 1`$ for every $`i \in P`$, the share of project $`i`$ funded;
$`r_y \ge 0`$ for every $`y \in Y`$, the money carried out of year $`y`$, with $`r_{y_0 - 1} = 0`$.

**Objective and constraints.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} v_i\, f_i && && \leftarrow v_i \text{ revised} \\
\text{s.t. }& \sum_{i \in P} c_{i,y}\, f_i + r_y \le B_y + r_{y-1} && \forall y \in Y && \text{(cash}_y) \quad \leftarrow B_{2030} \text{ cut} \\
& f_i = 1 && \forall i \in M && \text{(must}_i) \\
& \sum_{y \in Y} r_y \le 5{,}000 && && \text{(carry\_total)} \quad \leftarrow \text{a new rule, added later}
\end{aligned}
```

The new project, added in the same section, adds one variable $`0 \le f_{\text{NEW}} \le 1`$,
with spend 500 in 2028 and 700 in 2029 in rows (cash$`_{2028}`$) and (cash$`_{2029}`$), and NPV 900
in the objective.

## Change the Data in the Model, Not the Model Code

The obvious way to answer a what-if is to change the input data and call `build` again. That works,
and for one question it is fine. For many questions there is a better way: MathOpt's model is an
object you can edit. Each row's bounds are attributes, so the 2030 cut is one assignment:

```python
budget_2030 = lp.cash[2030].upper_bound
lp.cash[2030].upper_bound = 0.9 * budget_2030          # the data change: one number in one row
```

This is why `build` in lesson 2.4.1 returns the rows in a dict keyed by year: a what-if needs to
find the row it changes. The other kinds of change have their own calls:

| Change | Call |
| --- | --- |
| a row's limit (a budget) | `row.upper_bound = ...` or `row.lower_bound = ...` |
| a coefficient in a row (a project's spend) | `row.set_coefficient(variable, value)` |
| a coefficient in the objective (an NPV) | `model.objective.set_linear_coefficient(variable, value)` |
| a variable's bounds | `variable.lower_bound = ...`, `variable.upper_bound = ...` |
| a new variable or row | `model.add_variable(...)`, `model.add_linear_constraint(...)` |

The edit changes the model for every solve that follows. So a program that asks independent
what-ifs puts each change back before the next one, or every scenario after the first is answered
on the wrong data.

## An Incremental Solver Starts From the Last Basis

`mathopt.solve` builds a fresh solver for every call, hands it the model, and throws it away
afterwards. `mathopt.IncrementalSolver` keeps one solver alive across calls. Between calls it
sends the solver only the edits made to the model, and a solver that supports it starts from where
the last solve ended:

```python
lp = build(generate("medium"))
solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
```

```python
lp.cash[2030].upper_bound = 0.9 * budget_2030          # the data change: one number in one row
warm = solver.solve()                                  # same solver object: starts from the last basis
cold = mathopt.solve(lp.model, mathopt.SolverType.GLOP)  # a fresh solve of the same edited model
```

```text
base        objective 234898.1206  simplex iterations 191
cut, warm   objective 233003.9574  simplex iterations 6
cut, cold   objective 233003.9574  simplex iterations 196
restored    objective 234898.1206  simplex iterations 10
```

Both solves of the cut model give the same objective. The warm one needed 6 pivots, the cold
one 196. That is a **warm start**: the solver keeps the **basis** of its last answer, the
variables it solved for at its vertex (lesson 2.2.2; every variable strictly between its bounds is
one of them, lesson 2.4.1), and pivots from there.

Why so few pivots? A budget is the right-hand side of a row. Changing it moves where the row's
wall is, but not which moves would improve the objective, so the old basis still satisfies the
optimality conditions; only the plan it gives now breaks a row. GLOP runs primal simplex unless
asked otherwise, so it repaired the broken row first and then improved the objective again. Putting
the budget back took 10 pivots the same way.

Repairing broken rows while keeping optimality is exactly what dual simplex does (lesson 2.4.1),
and the OR-Tools guide to LP solving recommends dual simplex for a sequence of LPs where only the
bounds change. The program repeats the cut and the restore on two fresh solvers, the second asking
GLOP for dual simplex, and keeps the cut's log to see which phases ran:

```python
DUAL = mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX)
for label, params in (("primal simplex", mathopt.SolveParameters()), ("dual simplex", DUAL)):
    lp = build(generate("medium"))
    solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
    base = solver.solve(params=params)
    lp.cash[2030].upper_bound = 0.9 * budget_2030
    log: list[str] = []
    cut = solver.solve(params=params, msg_cb=log.extend)  # keep the cut's log to see which phases ran
    lp.cash[2030].upper_bound = budget_2030
    back = solver.solve(params=params)
```

```text
primal simplex  pivots: base 191, cut  6, restore 10; cut objective 233003.9574
                phases of the cut: Primal feasibility phase, Primal optimization phase
dual simplex    pivots: base  14, cut  1, restore  1; cut objective 233003.9574
                phases of the cut: Dual feasibility phase, Dual optimization phase
```

The default run's log shows the two steps: a primal feasibility phase that repairs the broken row,
then a primal optimization phase. Asked for dual simplex, GLOP needs 1 pivot for the cut and 1 for
the restore, against 6 and 10. For a series of budget what-ifs on GLOP, ask for dual simplex.

`solver.close()` at the end releases the solver; a program that answers many what-ifs creates one
`IncrementalSolver`, solves after each edit, and closes it when done.

<!-- practice 1 -->

## A Warm Start Survives Some Changes Better Than Others

The same solver, three more edits, each solved warm and then cold for comparison:

```python
lp.model.objective.set_linear_coefficient(lp.f["P004"], 3 * p004.value)
```

```python
new = lp.model.add_variable(lb=0, ub=1, name="f_NEW")
lp.cash[2028].set_coefficient(new, 500)
lp.cash[2029].set_coefficient(new, 700)
lp.model.objective.set_linear_coefficient(new, 900)
```

```python
lp.model.add_linear_constraint(sum(lp.carry.values()) <= 5000, name="carry_total")
```

```text
base               objective 234898.1206  P004 share 0.00  total carried 50,886
P004 NPV x3        objective 234976.7263  iterations warm   1  cold 189
new project        objective 235295.7904  iterations warm   4  cold 192
carry_total row    objective 230497.9928  iterations warm 116  cold 189
```

The edits are cumulative here (each keeps the one before), and the numbers line up with what each
edit does to the old vertex:

- **A new objective coefficient** leaves every row as it was, so the old vertex is still allowed;
  only optimality may be lost, which primal simplex repairs (lesson 2.4.1). P004 was unfunded;
  at three times its NPV it is worth funding, and one pivot brings it in.
- **A new variable** leaves the old vertex allowed too, with the new share at 0. Four pivots
  fit the new project in.
- **A new row** can cut the old vertex off. The plan was carrying $50,886k in total, ten times
  the new cap of $5,000k, so a large part of the plan has to change. The warm start still saved
  something, 116 pivots against 189, but far less than for the other edits.

The rule of thumb: edits that move a bound or a coefficient by a little are cheap to re-solve
warm; edits that make the old answer badly wrong are not much cheaper than a fresh solve. The
counts are what to trust, so measure on your own model.

## Not Every Solver Warm-Starts Through MathOpt

The same cut, on the large portfolio, with each of the three LP solvers:

```python
for solver_type in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP):
    lp = build(large)
    solver = mathopt.IncrementalSolver(lp.model, solver_type)
    base = solver.solve()
    lp.cash[2030].upper_bound *= 0.9
    warm = solver.solve()
    cold = mathopt.solve(lp.model, solver_type)
    solver.close()
```

```text
GLOP  iterations: base  4589  after the cut, warm   216  cold  4660
HIGHS iterations: base    21  after the cut, warm    22  cold    22
PDLP  iterations: base   320  after the cut, warm   384  cold   384
```

GLOP's re-solve took 216 pivots against 4,660 from scratch. HiGHS and PDLP did exactly the work of
a cold solve: through MathOpt in OR-Tools 9.15, their incremental re-solves start over.
`IncrementalSolver` accepts every solver; whether the next solve starts from the last one is up to
the solver. HiGHS's cold solve is short anyway on this LP, because its presolve leaves it little to
do (lesson 2.4.2), so for this model the difference does not matter. For many what-ifs of a model
where cold solves are slow, the counts above are the reason to run them on GLOP.

## A Dual Value Predicts a Small Change; Re-Solve to Know a Large One

Sometimes no solve is needed at all. The **dual value** of a row (lesson 2.3.1) is the rate at which
the optimal objective changes as the row's limit changes: here, how much NPV one more $k in the 2030
budget buys. So the effect of a cut can be predicted from the base solve alone:

```math
z_{\text{after}} \approx z - y_{2030} \cdot \text{cut}
```

with $`z`$ the base objective and $`y_{2030}`$ the dual value of (cash$`_{2030}`$). The program
compares that prediction with a re-solve, for cuts from $100k to 30% of the budget:

```python
for cut in (100, 1000, round(0.1 * budget_2030), round(0.3 * budget_2030)):
    lp.cash[2030].upper_bound = budget_2030 - cut
    result = solver.solve()
    predicted = base.objective_value() - price * cut
```

```text
dual value of cash_2030: 0.4808 of objective per $k; 2030 budget 38,430
cut    100: predicted  234850.0377  re-solved  234850.0377  error   0.0000  iterations 0
cut  1,000: predicted  234417.2916  re-solved  234415.3665  error   1.9251  iterations 4
cut  3,843: predicted  233050.2947  re-solved  233003.9574  error  46.3373  iterations 4
cut 11,529: predicted  229354.6429  re-solved  228937.5398  error 417.1031  iterations 22
```

The $100k cut is predicted exactly, and the re-solve confirms it with 0 pivots: the basis did not
change, so the objective moved along a straight line at the dual value's rate. From $1,000k on, the
basis changes (4 pivots and more), and the prediction drifts further from the truth with every
size of cut. The range of cuts over which the basis stays the same is the row's **ranging**
interval, which lesson 2.3.3 reads from a solver.

The error has a sign that never changes. In a maximizing LP, the optimal objective as a function of
a budget is **concave**: piecewise linear, with each further $k worth no more than the one
before. Cutting money therefore removes the least valuable use first, and every later $k cut
costs at least as much as the one before. So for a cut, $`z - y \cdot \text{cut}`$ is an **upper
bound** on the new optimum: the real loss can only be larger. That is what the table shows, a
prediction above the re-solve every time. For a budget meeting this gives a safe sentence before
any re-solve: "a cut of $11.5M costs at least $5.5M of NPV"; the re-solve then says it costs
$5.96M.

<!-- practice 2 -->

## Summary

- **Change the data in the model, not the model code.** Bounds, coefficients and new rows are edits
  of the existing model; undo a what-if's edits before the next one.
- **An incremental solver starts from the last basis.** GLOP re-solved a 10% budget cut in 6
  pivots against 196 from scratch, and in 1 pivot when asked for dual simplex.
- **A warm start survives some changes better than others.** A changed coefficient or a new
  variable costs a few pivots; a new row that cuts the old answer off costs many.
- **Not every solver warm-starts through MathOpt.** In OR-Tools 9.15, HiGHS and PDLP re-solves did
  the work of a cold solve.
- **A dual value predicts a small change; re-solve to know a large one.** For a cut in a
  maximizing LP, the prediction is an upper bound on the new optimum.

## Reference

| Edit | Old vertex after the edit | Warm re-solve (GLOP, medium) |
| --- | --- | --- |
| row limit, small change | same basis, maybe broken rows | 0 to 6 pivots (1 with dual simplex) |
| objective coefficient | still allowed | 1 pivot |
| new variable | still allowed (new variable at 0) | 4 pivots |
| new row the old answer breaks badly | cut off | 116 pivots (cold: 189) |

| Call | Effect |
| --- | --- |
| `mathopt.IncrementalSolver(model, solver_type)` | one solver kept across solves |
| `solver.solve()` | solve the model as edited since the last solve |
| `solver.close()` | release the solver |
| `result.dual_values(row)` | the row's dual value: objective change per unit of its limit |
| `solver.solve(params=mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX))` | a warm re-solve with dual simplex, the variant for changed bounds |

**Further reading:** [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (primal simplex suits a sequence of LPs whose objective changes, dual simplex one whose bounds change, and GLOP's default is primal simplex); [MathOpt `solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py) (`IncrementalSolver`: one solver kept across solves, with the model modified between them, and released by `close()` or a `with` statement); [MathOpt `linear_constraints.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/linear_constraints.py) (the row attributes a what-if edits: `lower_bound`, `upper_bound`, `set_coefficient`).

## Challenges

1. A what-if raises the 2030 budget by $100k instead of cutting it. Predict the new objective
   from the dual value, and say whether the prediction is an upper bound, a lower bound or exact.
2. A colleague answers 20 what-ifs on one `IncrementalSolver` and forgets to undo each edit. The
   20th answer is still a correct optimum. Of which model?
3. The cold HiGHS solve of the large LP takes 21 iterations. Is that a reason to prefer it to
   GLOP's warm start for 300 what-ifs? What would you measure to decide?

## Design Note: Build Once, Edit Many Times

Keeping the rows in a dict by their labels costs nothing when the model is built and is what makes
every what-if a one-line edit. A model built as an anonymous heap of rows can only be rebuilt.
Section 4 builds on this with MathOpt's other incremental features (lesson 4.3.4).

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**budget_cut.py.** The 10% cut on GLOP, warm and cold, and the restore, then the same cut with
GLOP's default primal simplex and with dual simplex (*Change the Data*, *An Incremental Solver*). *Try:* Cut 2030 by 50% instead. Predict whether the warm count stays far
below the cold one.

- Program: [budget_cut.py](src/budget_cut.py)

**other_changes.py.** A revised NPV, a new project and a new row on one incremental GLOP solver
(*A Warm Start Survives Some Changes Better Than Others*). *Try:* Raise the `carry_total` cap to
60,000. Predict the warm pivot count.

- Program: [other_changes.py](src/other_changes.py)

**warm_by_solver.py.** The cut on the large portfolio with GLOP, HiGHS and PDLP (*Not Every Solver
Warm-Starts*). *Try:* Cut 2030 by 1% instead of 10%. Predict GLOP's warm count first.

- Program: [warm_by_solver.py](src/warm_by_solver.py)

**dual_prediction.py.** The dual value's prediction against a re-solve, for four sizes of cut (*A
Dual Value Predicts a Small Change*). *Try:* Use 2036's row instead of 2030's. Predict whether the
$100k cut is still predicted exactly.

- Program: [dual_prediction.py](src/dual_prediction.py)
