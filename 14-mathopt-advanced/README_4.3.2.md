# 4.3.2 Prioritized Objectives with `add_auxiliary_objective`

GridCap's plan maximizes NPV, and finance asks a second question: among the plans with the best
NPV, which one spends the least money? Then a sharper one: if we gave up at most 1% of NPV, how much
less could we spend? Neither question has one objective. Each has two, in a strict order: NPV
matters first, and spend only breaks ties, or near-ties, between plans that are equally good on
NPV. This is a **lexicographic** (or **hierarchical**) objective, ordered the way a dictionary
orders words: the first letter decides, and the second only matters when the first ties.

MathOpt can store such an objective in the model with `add_auxiliary_objective`. This lesson shows
the API, which solvers in OR-Tools 9.15 accept it (in the runner, none), how to read the refusal,
and how to get the same answer anyway by solving one objective at a time. Section 8 (lessons
8.2.1–8.2.2) treats lexicographic planning in depth; this lesson is about the MathOpt API. GridCap
is a fictional utility.

## The Model

The multi-period timing model of lesson 4.3.1, with its objective replaced by two prioritized ones.
Its decisions are start-time variables: $`x_{i,t}= 1`$ if project $`i`$ starts in year $`t`$ of its
window $`T_i`$; a project starts at most once and spends its cost profile from its start year on.
(Lesson 6.4.1, in section 6, builds this model step by step.)

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the
child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, project $`i`$'s spend in its $`k`$-th year
of work ($k); $`B_y`$, the budget ($k); $`\varepsilon \ge 0`$, the share of the best NPV the plan
may give up (0 or 1% in this lesson).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$.

With $`\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}`$:

**Objectives, in priority order.** $`\leftarrow`$ this lesson

```math
\begin{aligned}
&\text{priority 0:} && \max \; f_0(x) = \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \\
&\text{priority 1:} && \min \; f_1(x) = \sum_{y \in Y} \text{spend}_y \quad \text{over the plans with } f_0(x) \ge (1 - \varepsilon)\, f_0^*
\end{aligned}
```

where $`f_0^*`$ is the best NPV any plan reaches.

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## Each Objective Has a Priority, and the Lowest Number Goes First

A MathOpt model always has one **primary objective**, `model.objective`, set by `model.maximize`
or `model.minimize`. Any number of **auxiliary objectives** can be added next to it, each with an
expression, a sense (maximize or minimize) and an integer **priority**:

| Call | Adds |
| --- | --- |
| `model.add_auxiliary_objective(priority=p, expr=e, is_maximize=False, name="")` | an objective, minimized unless `is_maximize=True` |
| `model.add_maximization_objective(e, priority=p, name="")` | the same, maximized |
| `model.add_minimization_objective(e, priority=p, name="")` | the same, minimized |

The objectives are optimized from the **lowest** priority number to the highest. The primary
objective has priority 0 unless you change it with `model.objective.priority = ...`, so an
auxiliary objective with priority 1 comes second. The number is an order, not a weight: priority 1
does not mean "one unit of importance", and priorities 1 and 100 rank the same way. The `Objective`
docstring adds that a model with one objective ignores its priority, and that an auxiliary
objective must be linear.

OR-Tools' own example of the API, `hierarchical_objectives.py`, adapted here, is a model with many
optimal solutions and a second objective that picks one:

```python
model = mathopt.Model(name="hierarchical")
x = model.add_variable(lb=0, ub=1, name="x")
y = model.add_variable(lb=0, ub=1, name="y")
z = model.add_binary_variable(name="z")
model.add_linear_constraint(x + y + z <= 1.5, name="c")
model.maximize(x + y + 2 * z)                                   # the primary objective, priority 0
aux = model.add_maximization_objective(y, priority=1, name="more_y")
```

```text
primary: priority 0, maximize True
more_y: priority 1, maximize True, id 0
auxiliary objectives in the model: 1
```

With $`z = 1`$ the row leaves $`x + y \le 0.5`$, and every split of that 0.5 between $`x`$ and
$`y`$ gives the primary objective its best value, 2.5. The auxiliary objective says which split to
return: as much $`y`$ as possible. Like constraints, an `AuxiliaryObjective` has an `id`, numbered
from 0 in creation order, and its `priority`, `is_maximize` and `name` read back. Unlike indicator
constraints, an objective can be edited: `priority` and `is_maximize` have setters, and
`model.delete_auxiliary_objective(aux)` removes one.

## In OR-Tools 9.15, Add a Second Auxiliary Objective Term by Term

The sample has one auxiliary objective. A model with two, written the obvious way, loses the first
one's terms when the second is added:

```python
first = model.add_minimization_objective(1.5 * overtime, priority=1, name="overtime_cost")
print("after adding the first: ", {first.name: terms(first)})
second = model.add_minimization_objective(2 * idle, priority=2, name="idle_cost")
```

```text
after adding the first:  {'overtime_cost': {'overtime': 1.5}}
after adding the second: {'overtime_cost': {}, 'idle_cost': {'idle': 2.0}}
in the exported model:   {'overtime_cost': {}, 'idle_cost': {1: 2.0}}
```

After the second call, `overtime_cost` has no terms at all, and the model a solver would receive
(`export_model()`, read back by variable id) has lost them too. Nothing raised. The cause is in
OR-Tools' `objectives.py`: `add_auxiliary_objective(expr=...)` first calls the new objective's
`clear()`, and in 9.15 `AuxiliaryObjective.clear()` clears the coefficients of *every* auxiliary
objective, not only its own. The primary objective is not affected.

The way around it is to create each auxiliary objective without an expression, which skips
`clear()`, and set its terms one at a time with `set_linear_coefficient`, which touches only that
objective. `in_order.add_auxiliary` does that:

```python
obj = model.add_auxiliary_objective(priority=priority, is_maximize=is_maximize, name=name)
flat = mathopt.LinearExpression(expr)
obj.offset = flat.offset
for var, coefficient in flat.terms.items():
    obj.set_linear_coefficient(var, coefficient)
```

```text
term by term:            {'overtime_cost': {'overtime': 1.5}, 'idle_cost': {'idle': 2.0}}
```

`mathopt.LinearExpression(expr)` flattens any linear expression into a dict of terms (`terms`) and a
constant (`offset`). With one auxiliary objective, as in the rest of this lesson, the shortcut
methods are safe; with two or more, add them term by term, and read them back to check.

<!-- practice 1 -->

## A Tolerance Lets a Later Objective Buy Something From an Earlier One

With no tolerance, the second objective only breaks exact ties in the first. In a MIP like
GridCap's, exact ties on NPV are rare, so the second objective would rarely change anything. The
1% question needs a **degradation tolerance**: how far the first objective may fall from its best
value to make room for the second.

MathOpt sets it per objective, in `ModelSolveParameters`, the model-specific half of a solve's
settings (lesson 4.3.3 covers its other fields). The `ObjectiveParameters` docstring in
`model_parameters.py` defines it. A hierarchical solver takes the objectives in priority order; for
each one $`f^k`$ it finds the best value $`\Gamma^k`$ subject to every constraint, and from then on
treats a plan as acceptable for $`f^k`$ only if $`f^k(x)`$ is within tolerance of $`\Gamma^k`$:

```math
|f^k(x) - \Gamma^k| \;\le\; \text{absolute tolerance} \qquad\text{or}\qquad |f^k(x) - \Gamma^k| \;\le\; \text{relative tolerance} \cdot |\Gamma^k|
```

When both tolerances are set, meeting either one is enough, so the allowed loss is the larger of
the two. With neither set, the loss allowed is 0. The program asks for 1% on NPV:

```python
params = mathopt.ModelSolveParameters()
if npv_tolerance is not None:
    params.objective_parameters[pm.model.objective] = mathopt.ObjectiveParameters(
        objective_degradation_relative_tolerance=npv_tolerance)
```

`objective_parameters` is a dict keyed by the objective objects themselves, `model.objective` for
the primary one and an `AuxiliaryObjective` for the others. `ObjectiveParameters` also takes
`objective_degradation_absolute_tolerance` and a per-objective `time_limit`.

## No Solver in the Runner Takes Auxiliary Objectives

The same sample model, sent to each MIP solver in the runner:

```python
for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT,
               mathopt.SolverType.GUROBI):
    try:
        solve(model, solver)
    except Exception as error:
        print(f"{solver.name:6} {type(error).__name__:14} reason: {refusal(error)}")
```

```text
HIGHS  AttributeError reason: Highs does not support multiple objectives [INVALID_ARGUMENT]
GSCIP  AttributeError reason: SCIP does not support multiple objectives [INVALID_ARGUMENT]
CP_SAT AttributeError reason: CP-SAT does not support multiple objectives [INVALID_ARGUMENT]
GUROBI RuntimeError   reason: bad_function_call
```

HiGHS, SCIP and CP-SAT refuse the model, each with a clear reason once it is read from
`__context__` (lesson 4.3.1). The OR-Tools sample itself solves with Gurobi, a commercial solver
that needs a license, and the Gurobi line is different: a `RuntimeError` with nothing on
`__context__`, so `refusal` falls back to the error's own text. "bad_function_call" is a C++ error
saying a function was called through an empty pointer: MathOpt reached for the Gurobi library and
found none it could use. Section 5 covers Gurobi and its licenses; until then, no lesson needs it.

So in this course's runner, a model with an auxiliary objective cannot be solved by any solver as
it stands. The API is still worth knowing: the model stores the priorities in one place, and on a
machine with a supported Gurobi the same model solves unchanged. The sample reads the second
objective's value with `result.solutions[0].primal_solution.auxiliary_objective_values[aux]`.

## Solve in Order: One Objective at a Time, Each Kept Within Its Tolerance

The docstring's definition is also a recipe any MIP solver can follow. For each objective in
priority order: optimize it; read the best value $`\Gamma`$; add a row keeping that objective
within its allowed loss of $`\Gamma`$; go on to the next. For a maximized objective the row is
$`f(x) \ge \Gamma - \text{loss}`$, for a minimized one $`f(x) \le \Gamma + \text{loss}`$.
`in_order.py` does exactly that, on a copy of the model so the caller's model is not changed:

```python
def objectives_in_order(model: mathopt.Model) -> list:
    """The primary objective and every auxiliary one, lowest priority number first."""
    return sorted([model.objective, *model.auxiliary_objectives()], key=lambda obj: obj.priority)
```

```python
def allowed_loss(best: float, params: mathopt.ObjectiveParameters | None) -> float:
    """How far an objective may move from its optimum: the larger of the two tolerances, or 0."""
    if params is None:
        return 0.0
    absolute = params.objective_degradation_absolute_tolerance or 0.0
    relative = (params.objective_degradation_relative_tolerance or 0.0) * abs(best)
    return max(absolute, relative)
```

```python
work = mathopt.Model.from_model_proto(model.export_model())     # a copy; the model stays as it is
for aux in list(work.auxiliary_objectives()):
    work.delete_auxiliary_objective(aux)
reached = {}
for obj in objectives_in_order(model):
    expr = obj.offset + mathopt.fast_sum(t.coefficient * work.get_variable(t.variable.id)
                                         for t in obj.linear_terms())
    work.set_linear_objective(expr, is_maximize=obj.is_maximize)
```

```python
best = result.objective_value()
reached[obj.name or "primary"] = best
loss = allowed_loss(best, tolerances.get(obj))
if obj.is_maximize:                                          # keep it within its tolerance
    work.add_linear_constraint(expr >= best - loss, name=f"keep_{obj.name or 'primary'}")
else:
    work.add_linear_constraint(expr <= best + loss, name=f"keep_{obj.name or 'primary'}")
```

Three details carry the method:

- **The copy.** MathOpt models have no `clone` method in OR-Tools 9.15. `export_model()` writes the
  model as a protocol buffer (MathOpt's serialized form of a model), and `Model.from_model_proto`
  reads it back as a new model whose variables keep the same ids, so `work.get_variable(t.variable.id)`
  finds each original variable's twin.
- **The auxiliary objectives are deleted from the copy**, or the solver would refuse it as above.
  Each objective is rebuilt as the copy's single objective from its `linear_terms()` and `offset`.
- **The sign of the kept row follows the sense**: a maximized objective may fall by the loss, a
  minimized one may rise by it, and `abs(best)` keeps a relative tolerance right when the best value
  is negative.

On the sample, with the tie broken both ways:

```text
primary only:  objective 2.5  x 0.0  y 0.5  z 1.0
in order:      objectives {'primary': 2.5, 'more_y': 0.5}  x 0.0  y 0.5  z 1.0
in order:      objectives {'primary': 2.5, 'less_y': 0.0}  x 0.5  y 0.0  z 1.0
```

HiGHS alone happened to return the split with all of the 0.5 on $`y`$. That was its choice among
equally good answers, and nothing in the model asked for it. Solved in order, the auxiliary
objective decides: maximize $`y`$ and it is 0.5, minimize it and it is 0, while the primary value
stays 2.5 both times. Those are the values the OR-Tools sample states for Gurobi's solve: primary
2.5, secondary 0.5.

On GridCap, with NPV first and total spend second:

```python
pm.model.objective.priority = npv_priority                      # max NPV is the primary objective
total_spend = mathopt.fast_sum(pm.spend.values())
pm.model.add_minimization_objective(total_spend, priority=spend_priority, name="spend")
```

```text
NPV, then spend, exact       NPV    24,260  spend    41,630  projects 27
NPV within 1%, then spend    NPV    24,031  spend    40,440  projects 26
spend first, then NPV        NPV     2,684  spend     7,630  projects 4
```

Read the three rows in turn:

- **Exact.** The plan has the best NPV, 24,260, and of all plans with that NPV it spends the least,
  41,630.
- **1% tolerance.** NPV may fall to $`24{,}260 \times 0.99 = 24{,}017.4`$. The plan found gives up
  $229k of NPV (0.94%) and spends $1,190k less, with one project fewer. That trade is the answer to
  finance's sharper question, and a planner can now decide whether it is worth taking.
- **Swapped priorities.** With the NPV objective's priority set to 2, spend comes first. The least
  spend is the must-do projects alone, 4 projects and 7,630, and NPV only picks among plans that
  spend exactly that. Priorities are not weights: whatever comes first wins outright.

<!-- practice 2 -->

## Summary

- **Each objective has a priority, and the lowest number goes first.** The primary objective has
  priority 0; `add_maximization_objective(expr, priority=1)` adds a second one.
- **In OR-Tools 9.15, add a second auxiliary objective term by term.** Adding one with an
  expression erases the terms of every auxiliary objective already in the model.
- **A tolerance lets a later objective buy something from an earlier one.**
  `ModelSolveParameters(objective_parameters={obj: ObjectiveParameters(...)})`; with both
  tolerances set, the larger allowed loss applies.
- **No solver in the runner takes auxiliary objectives.** HiGHS, SCIP and CP-SAT refuse them, with
  the reason on `__context__`; Gurobi cannot be loaded in the runner.
- **Solve in order: one objective at a time, each kept within its tolerance.** On GridCap a 1% NPV
  tolerance bought $1,190k less spend for $229k of NPV.

## Reference

| Task | Code |
| --- | --- |
| a second objective | `model.add_minimization_objective(expr, priority=1, name="spend")` |
| two or more auxiliary objectives (9.15) | `add_auxiliary_objective(priority=..., is_maximize=...)`, then `set_linear_coefficient` per term |
| the primary objective's priority | `model.objective.priority` (0 by default) |
| list, count, delete | `model.auxiliary_objectives()`, `model.num_auxiliary_objectives()`, `model.delete_auxiliary_objective(aux)` |
| a 1% tolerance on an objective | `ModelSolveParameters(objective_parameters={obj: ObjectiveParameters(objective_degradation_relative_tolerance=0.01)})` |
| copy a model | `mathopt.Model.from_model_proto(model.export_model())` |
| an auxiliary objective's value (supporting solvers) | `result.solutions[0].primal_solution.auxiliary_objective_values[aux]` |

| Term | Meaning |
| --- | --- |
| lexicographic (hierarchical) objective | objectives in a strict order; a later one only chooses among plans the earlier ones accept |
| primary, auxiliary objective | `model.objective`; the others added with a priority |
| degradation tolerance | how far an objective may fall from its best value to make room for later ones |

**Further reading.** OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt):
multiple hierarchical objectives in the feature list. The sample
[`hierarchical_objectives.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/hierarchical_objectives.py),
adapted above. In OR-Tools' Python sources,
[`model.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py)
(`add_auxiliary_objective` and its two shortcuts),
[`objectives.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/objectives.py)
(priorities, the rule that auxiliary objectives are linear, and `AuxiliaryObjective.clear`) and
[`model_parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py)
(`ObjectiveParameters` and its definition of the tolerances).

## Challenges

1. Give the spend objective an absolute tolerance of 500 and add a third objective, priority 2,
   that maximizes the number of projects started. Which rows does `solve_in_order` add, and in
   which order?
2. Set both tolerances on NPV: relative 1% and absolute 100. Which one decides the allowed loss on
   the small portfolio, and why?
3. The swapped run sets the NPV priority to 2 and spend to 1. Would priorities 7 and 3 give a
   different plan?

## Design Note: Store the Priorities in the Model, Solve Them Where You Can

`npv_then_spend.py` builds one model that says everything about the question, objectives and
tolerances included, and leaves *how* to solve it to one function. On a solver that takes auxiliary
objectives, that function is one `mathopt.solve` call; in the runner it is `solve_in_order`. The
model code does not change between the two. Keep the question in the model and the workaround in
the solve, and the workaround can be deleted the day it is no longer needed.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**hierarchical_sample.py.** OR-Tools' hierarchical-objectives example: the API read back, the
refusals of every runner solver, and the solve in order with the tie broken both ways (*Each
Objective Has a Priority*, *No Solver in the Runner Takes Auxiliary Objectives*, *Solve in Order*).
*Try:* Change the row to `x + y + z <= 1.8` and predict the in-order values of $`x`$ and $`y`$.

- Program: [hierarchical_sample.py](src/hierarchical_sample.py)

**npv_then_spend.py.** GridCap with NPV first and spend second, exact, with a 1% tolerance, and with
the priorities swapped (*A Tolerance Lets a Later Objective Buy Something*, *Solve in Order*).
*Try:* Raise the tolerance to 3% and predict whether the project count keeps falling.

- Program: [npv_then_spend.py](src/npv_then_spend.py)

**aux_terms.py.** Two auxiliary objectives added the obvious way, the first one's lost terms, and
the term-by-term way that keeps both (*In OR-Tools 9.15, Add a Second Auxiliary Objective Term by
Term*). *Try:* Add the second objective with no `expr` and predict what the first one reads back.

- Program: [aux_terms.py](src/aux_terms.py)

**in_order.py.** `add_auxiliary`, and the solve in priority order, with each objective kept within
its tolerance.

- Library: [in_order.py](src/in_order.py)
