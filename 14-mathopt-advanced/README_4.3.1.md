# 4.3.1 Indicator Constraints

GridCap's risk office has a new rule for large projects. A project costing $5M or more often
overruns in its first year, so in any year such a project starts, the plan must keep 10% of that
year's budget unspent as a reserve. In words the rule is an implication: *if* a large project
starts in year $`t`$, *then* spend in $`t`$ stays within 90% of $`B_t`$. GridCap is a fictional
utility, and its numbers are teaching data.

An indicator constraint writes such a rule directly: a linear row that must hold when a chosen
binary variable is 1 (or, if you ask, when it is 0), and that is switched off when the binary has
its other value. MathOpt stores one as it is, and leaves it to the solver to enforce. Lesson 6.2.3,
in section 6, sets indicator constraints against big-M rows (the linear way to write the same rule,
shown at the end of this lesson) in depth; this lesson needs only what it states here. It is about
the API itself: every way to write an indicator constraint, how to
read one back, why you cannot edit one, which solvers in OR-Tools 9.15 take them, and how to get
the real reason when a solver refuses. It is the first lesson of the module, and it relies on the
MathOpt basics of lessons 4.2.1–4.2.4 (model, variables, `SolveResult`, solver types): a
`mathopt.Model` holds variables and rows, and `mathopt.solve(model, solver_type)` hands it to one
solver.

## The Model

A multi-period timing model, whole, with one new family of rows. Its decisions are **start-time
variables**: $`x_{i,t} = 1`$ means project $`i`$ starts in year $`t`$, with one binary for each year
$`t`$ in the project's window $`T_i`$. Each project starts in at most one year of its window, and a
project started in year $`t`$ spends its cost profile from that year on: $`c_{i,0}`$ in year $`t`$,
$`c_{i,1}`$ in year $`t + 1`$, and so on. Every lesson of this module uses this model as it is stated
here; lesson 6.4.1, in section 6, builds it step by step.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups, each
a set of projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years;
$`L \subseteq P`$ the **large** projects, those with total cost of at least $5,000k.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k); $`\sigma = 0.9`$, the share of a year's budget a large
start allows.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

Write $`\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}`$, the
money the plan spends in year $`y`$ (an expression, not a variable).

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y) \\
x_{i,t} = 1 \;&\Longrightarrow\; \text{spend}_t \le \sigma B_t && \forall i \in L,\ t \in T_i && \text{(reserve}_{i,t}) \quad \leftarrow \text{this lesson}
\end{aligned}
```

The arrow reads "implies". When $`x_{i,t} = 1`$ the reserve row must hold; when $`x_{i,t} = 0`$ it
says nothing, and only the ordinary budget row limits that year.

## An Indicator Constraint Is a Binary, a Row and the Value That Switches It On

An **indicator constraint** has three parts:

- the **indicator variable**, a binary variable $`z`$;
- the **implied constraint**, a linear row $`\ell \le a^\top x \le u`$, where either bound may be
  missing (infinite);
- the **activating value**: the row must hold when $`z = 1`$ (the default), or when $`z = 0`$.

`Model.add_indicator_constraint` takes these as keyword arguments. Its docstring in OR-Tools'
`model.py` lists two ways to give the row. Either pass a bounded expression as
`implied_constraint`, the same thing you would pass to `add_linear_constraint`, or pass its parts
as `implied_expr`, `implied_lb` and `implied_ub`; you may not mix the two. The program below writes
the reserve rule for P032 starting in 2027 both ways, then a third constraint that switches on at
zero and has two bounds:

```python
a = pm.model.add_indicator_constraint(indicator=x, implied_constraint=spend <= cap, name="as_row")
b = pm.model.add_indicator_constraint(indicator=x, implied_expr=spend, implied_ub=cap, name="as_parts")
```

```python
c = pm.model.add_indicator_constraint(indicator=x, activate_on_zero=True,
                                      implied_constraint=(5000 <= spend) <= small.budget[2027], name="floor")
```

```text
as_row    lb -inf  ub 8001.0  on zero False
as_parts  lb -inf  ub 8001.0  on zero False
floor     lb 5000.0  ub 8890.0  on zero True
```

The first two are the same constraint: no lower bound, an upper bound of 8,001, which is 90% of the
2027 budget of 8,890, switched on by $`x = 1`$. The third reads "unless P032 starts in 2027, 2027
spend is between 5,000 and 8,890": `activate_on_zero=True` makes $`z = 0`$ the activating value, and
the parentheses around `(5000 <= spend) <= ...` are how MathOpt's Python API writes a row with two
bounds (without them, Python would silently keep only one comparison). An equality is a row whose
two bounds are equal, `implied_constraint=expr == b`.

MathOpt stores all of these, but a solver may take fewer. SCIP, the one solver in the runner that
solves indicator constraints at all (a later section shows the others refusing), takes only rows
with **one** side. The program sends the model with `floor` to SCIP, then replaces `floor` by its
lower side alone:

```python
try:
    solve(pm.model, mathopt.SolverType.GSCIP)
except Exception as error:
    print("SCIP, two-sided row:", refusal(error))
pm.model.delete_indicator_constraint(c)
c = pm.model.add_indicator_constraint(indicator=x, activate_on_zero=True,           # one side only
                                      implied_constraint=spend >= 5000, name="floor")
```

```text
SCIP, two-sided row: gSCIP does not support indicator constraints with ranged implied constraints; bounds are: 5000 <= ... <= 8890 [INVALID_ARGUMENT]
SCIP, one-sided row: OPTIMAL
```

An equality has two sides as well, so SCIP refuses "if off, then output $`= 0`$" the same way. When
the variable cannot go below 0 anyway, write the one side that matters:

```python
toy.add_indicator_constraint(indicator=on, activate_on_zero=True, implied_constraint=work == 0, name="off_means_0")
```

```text
SCIP, equality row: gSCIP does not support indicator constraints with ranged implied constraints; bounds are: 0 <= ... <= 0 [INVALID_ARGUMENT]
SCIP, work <= 0 instead: 9.0
```

With $`\text{work} \ge 0`$ as its bound, `work <= 0` says the same as `work == 0`. A rule that truly
needs both sides becomes two indicator constraints on the same binary, one per side. (`refusal`, which
reads a refusal's real reason, is explained in the section on solvers below.)

Every argument in the table, with its default:

| Argument | Meaning | Default |
| --- | --- | --- |
| `indicator` | the binary variable $`z`$ | `None`, which makes the model invalid at solve time |
| `activate_on_zero` | `True`: the row holds when $`z = 0`$; `False`: when $`z = 1`$ | `False` |
| `implied_constraint` | the row as a bounded expression, `expr <= u`, `expr >= l`, `(l <= expr) <= u`, `expr == b` | `None` |
| `implied_expr`, `implied_lb`, `implied_ub` | the row in parts, used only when `implied_constraint` is `None` | `0`, $`-\infty`$, $`+\infty`$ |
| `name` | a label for reading the model and its errors | `""` |

The indicator must be a **binary** variable when the model is solved: integer with bounds 0 and 1.
MathOpt checks this before the solver starts. A continuous variable with the same bounds is
refused:

```python
share = toy.add_variable(lb=0, ub=1, name="share")           # continuous, not binary
work = toy.add_variable(lb=0, ub=10, name="work")
toy.add_indicator_constraint(indicator=share, implied_constraint=work <= 3, name="needs_binary")
```

```text
continuous indicator: the following (indicator constraint ID, indicator variable ID) pairs are invalid as the indicator variable is not binary: (0, 0) [INVALID_ARGUMENT]
```

The message names constraints and variables by their **ids**, the integers MathOpt numbers them by
in creation order, not by their names. Here both are the first of their kind, so both ids are 0.
Each object's `.id` gives it, so a program can map the message back to a name.

<!-- practice 1 -->

## Any Binary in the Model Can Be the Indicator

An indicator can be a binary added only to switch a row (lesson 6.2.3, in section 6, adds one for
"hire a contractor"). Often no new variable is needed: the decision the rule depends on is already a binary of the model. Here the indicator of
each reserve row is the start variable $`x_{i,t}`$ itself, so the code adds rows and nothing else:

```python
reserve = {}
for p in small.projects:
    if p.capex < LARGE:
        continue
    for t in p.starts():
        reserve[p.project_id, t] = pm.model.add_indicator_constraint(
            indicator=pm.x[p.project_id, t],                     # an existing start variable
            implied_constraint=pm.spend[t] <= SHARE * small.budget[t],
            name=f"reserve_{p.project_id}_{t}")
```

`pm.spend[t]` is the year's spend expression the model builder already made for the budget row
(`plan_model.py`), so the reserve row costs one line. Five projects are large: P017, P028, P030,
P032 and P036, with 2, 1, 2, 3 and 4 allowed start years, which makes 12 rows. SCIP solves the
model:

```text
without the rule   NPV 24,260
indicator constraints: 12
```

```text
with the rule      NPV 23,039  (OPTIMAL, SCIP)
  P017 starts 2030: spend 7,720 of 8,610 (89.7%)
  P028 starts 2030: spend 7,720 of 8,610 (89.7%)
  P032 starts 2029: spend 7,800 of 8,760 (89.0%)
```

The reserve costs $1,221k of NPV. Every year in which a large project starts ends at or below 90%
of its budget, and the program checks that from the plan itself, by adding up each started project's
spend in that year, not from the solver's say-so. Two large projects share 2030, which is allowed:
the rule caps the year once, however many large projects start in it.

## An Indicator Constraint Reads Back, but Cannot Be Edited

`add_indicator_constraint` returns an `IndicatorConstraint` object. Its properties give back
everything that went in:

```python
ic = reserve["P032", 2027]
print(f"{ic.name}: indicator {ic.indicator_variable.name}, activate_on_zero {ic.activate_on_zero},"
      f" bounds [{ic.lower_bound}, {ic.upper_bound}], {len(list(ic.terms()))} terms")
```

```text
reserve_P032_2027: indicator x_P032_2027, activate_on_zero False, bounds [-inf, 8001.0], 10 terms
```

| Read | Gives |
| --- | --- |
| `ic.indicator_variable` | the binary $`z`$ (`None` if it was never set or was deleted) |
| `ic.activate_on_zero` | `True` if the row holds when $`z = 0`$ |
| `ic.lower_bound`, `ic.upper_bound` | the row's bounds, `-inf` or `inf` when missing |
| `ic.terms()` | the row's `(variable, coefficient)` pairs, as `LinearTerm` objects |
| `ic.get_coefficient(v)` | one coefficient, 0 if `v` is not in the row |
| `ic.get_implied_constraint()` | the whole row as a bounded expression |
| `model.get_num_indicator_constraints()`, `model.get_indicator_constraints()` | how many there are; each of them |

`get_implied_constraint()` prints the row the way MathOpt stores it: the expression with its
constant term 0.0 first, the variables, then the bounds.

```python
print("read back:", str(c.get_implied_constraint())[:58], "...")
```

```text
read back: 5000.0 <= 0.0 + 460.0 * x_P002_2027 + 360.0 * x_P022_2027  ...
```

What you cannot do is change one. The class docstring calls indicator constraints of "limited
mutability": you can delete one, or delete a variable it uses, but not update its bounds or
coefficients. The properties have no setters, so an assignment fails at once:

```python
try:
    ic.upper_bound = 0.95 * small.budget[2027]
except AttributeError as error:
    print("change a bound:", error)
pm.model.delete_indicator_constraint(ic)          # to change a rule: delete it and add it again
reserve["P032", 2027] = pm.model.add_indicator_constraint(
    indicator=pm.x["P032", 2027], implied_constraint=pm.spend[2027] <= 0.95 * small.budget[2027],
    name="reserve_P032_2027")
```

```text
change a bound: property 'upper_bound' of 'IndicatorConstraint' object has no setter
after delete and re-add: 12 indicator constraints, P032 2027 bound 8,445.5
```

This is different from a linear constraint, whose `upper_bound` you can assign (lesson 2.4.3). A
program that runs what-ifs on an indicator's limit must keep the pieces (indicator, expression,
bounds, activating value) to rebuild it, or read them back from the old constraint before deleting
it. A toy constraint shows the second way, with `terms()` turned back into an expression for
`implied_expr`:

```python
old = toy.add_indicator_constraint(indicator=z, implied_constraint=2 * v + 5 <= 9, name="rule")
print("stored:", old.get_implied_constraint())
parts = dict(indicator=old.indicator_variable, activate_on_zero=old.activate_on_zero, name=old.name,
             implied_expr=mathopt.fast_sum(t.coefficient * t.variable for t in old.terms()),
             implied_lb=old.lower_bound, implied_ub=old.upper_bound)
toy.delete_indicator_constraint(old)
new = toy.add_indicator_constraint(**parts)
print("rebuilt:", new.get_implied_constraint(), "| on zero", new.activate_on_zero, "| name", new.name)
```

```text
stored: -inf <= 0.0 + 2.0 * v <= 4.0
rebuilt: -inf <= 0.0 + 2.0 * v <= 4.0 | on zero False | name rule
```

The row was written with a constant, `2 * v + 5 <= 9`, and MathOpt stored it as `2 * v <= 4`: the
constant moved into the bound, and the stored expression's constant is 0.0. So the terms and the
two bounds are the whole row, and a rebuild has no offset to carry. To change a limit,
pass a new `implied_lb` or `implied_ub` in place of the old one. Either way the program must
replace its own reference, as the code does with
`reserve["P032", 2027]`: the old object now refers to a deleted constraint. Lesson 4.3.4 comes back
to this when it edits models between solves.

Do not reach for a plain row instead. A row `load <= 250` added beside an indicator constraint
"if `on`, then `load <= 250`" is a different rule: the plain row holds whatever the indicator's
value. A toy model shows it, maximizing `load + 100 * on` with `load` between 0 and 400:

```python
toy.add_indicator_constraint(indicator=on, implied_constraint=load <= 250, name="if_on")
toy.maximize(load + 100 * on)
result = solve(toy, mathopt.SolverType.GSCIP)
print(f"indicator only:          on {result.variable_values(on):.0f}, load {result.variable_values(load):.0f}")
toy.add_linear_constraint(load <= 250, name="always")              # a plain row, no indicator
```

```text
indicator only:          on 0, load 400
plus plain load <= 250:  on 1, load 250
```

With the indicator alone, the solver switches `on` off and takes the full 400. With the plain row
beside it, `load` stays at 250 even when `on` is 0, so the solver might as well switch `on` on: the
plain row has replaced the implication with an unconditional limit.

<!-- practice 2 -->

## The Solver Decides Whether It Accepts Indicators, and the Reason Is on `__context__`

MathOpt accepts an indicator constraint into any model. Whether it can be solved is up to the
solver behind it, and the program sends the same reserve model to three more:

```python
for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.CP_SAT, mathopt.SolverType.GLOP):
    try:
        solve(pm.model, solver)
    except Exception as error:                    # the real reason is on __context__
        print(f"{solver.name:6} {type(error).__name__} | reason: {refusal(error)}")
```

```text
HIGHS  AttributeError | reason: Highs does not support indicator constraints [INVALID_ARGUMENT]
CP_SAT AttributeError | reason: MathOpt does not currently support CP-SAT models with indicator constraints [UNIMPLEMENTED]
GLOP   AttributeError | reason: Glop does not support integer variables [INVALID_ARGUMENT]
```

Read the two columns separately. The exception each one raises is an `AttributeError`, which says
nothing about the model: in OR-Tools 9.15, MathOpt's Python wrapper fails while converting the
solver's error into a Python one (lesson 4.2.4 takes this bug apart). Python keeps the exception that was being
handled when a new one was raised in the new exception's `__context__` attribute, and there sits the
solver's own message. `plan_model.refusal` returns it:

```python
def refusal(error: BaseException) -> str:
    """The solver's own reason for an error: OR-Tools 9.15 raises an AttributeError whose
    `__context__` holds the real error, a StatusNotOk. Its text is the solver's message followed by
    the status code's name in brackets. Falls back to the error itself."""
    inner = error.__context__ or error.__cause__
    return str(inner if inner is not None else error)
```

The hidden error is a `StatusNotOk` object. `refusal` returns its text, `str(...)`, which is the
solver's message followed by the status code's name in brackets, as printed above. Lesson 4.2.4
reads the same object's `.message`, the message alone, and its `.code`, the code as a number. Both
carry the solver's own words; `refusal` keeps the text because a log line then has the code too.

The bracketed word at the end is the error's **status code**: `INVALID_ARGUMENT` means the solver
cannot take this model at all; `UNIMPLEMENTED` means MathOpt has no translation for it yet. That
CP-SAT line is worth reading twice. CP-SAT itself has enforcement literals, its native form of an
implication (lesson 4.4.2 teaches them), but MathOpt's bridge to CP-SAT does not translate indicator
constraints into them in 9.15. A model written directly in CP-SAT's own API (lesson 4.4.2) can state
the rule;
the same rule sent through MathOpt cannot.

The solvers of OR-Tools 9.15, as the runner has them:

| Solver | Indicator constraints |
| --- | --- |
| SCIP (`GSCIP`) | accepted and solved, when each implied row has one side only |
| HiGHS | refused: "Highs does not support indicator constraints" |
| CP-SAT | refused: MathOpt does not translate them for CP-SAT |
| GLOP, PDLP | refused, because they take no integer variables at all |
| Gurobi | documented as supported, but the runner has no Gurobi library that MathOpt can load (lesson 4.3.2 shows the error) |

<!-- practice 3 -->

## A Model for HiGHS States the Rule as a Linear Row

HiGHS is the course's default MILP solver, so a rule that only SCIP accepts is a rule worth
writing a second way. The linear way is a **big-M row**: the row's limit moves by a constant $`M`$
times the binary, so the row is tight when the binary is 1 and loose when it is 0. The rule for
$`M`$: it must be at least as large as the move needed when the row is switched off, which takes a
bound on the row's expression from the data, and no larger, because a larger $`M`$ only weakens the
model. Lesson 6.2.1, in section 6, derives such bounds in depth. Here the linear form needs no new
bound at all: the budget row already caps $`\text{spend}_t`$ at $`B_t`$, so lowering that cap by
$`(1 - \sigma) B_t`$ when $`x_{i,t} = 1`$ is exact, with $`M = (1 - \sigma) B_t`$:

```math
\text{spend}_t \;\le\; B_t - (1 - \sigma)\, B_t\, x_{i,t} \qquad \forall i \in L,\ t \in T_i
```

```python
pm.model.add_linear_constraint(
    pm.spend[t] <= small.budget[t] - (1 - SHARE) * small.budget[t] * pm.x[p.project_id, t])
```

```text
indicator rows, GSCIP  NPV 23,039
linear    rows, HIGHS  NPV 23,039
```

Same rule, same optimum, two solvers. Which form to keep comes down to the bound (lesson 6.2.3, in
section 6, compares the two forms in depth): when the data give a tight bound, as here, the linear row runs anywhere; when no finite bound exists, the
indicator is the only exact form, and it ties the model to a solver that accepts it.

## Summary

- **An indicator constraint is a binary, a row and the value that switches it on.**
  `add_indicator_constraint(indicator=z, implied_constraint=row)` or with `implied_expr`,
  `implied_lb`, `implied_ub`; `activate_on_zero=True` switches it on at $`z = 0`$; the indicator
  must be binary at solve time, and SCIP takes only one-sided implied rows (no ranges, no equalities).
- **Any binary in the model can be the indicator.** The reserve rule hangs on the start variables
  the model already has, with no new variable.
- **An indicator constraint reads back, but cannot be edited.** Its properties return every part;
  to change a bound, delete it and add it again, and replace your reference. A plain row
  `load <= 250` added beside it is a different rule: it holds whatever the indicator's value.
- **The solver decides whether it accepts indicators, and the reason is on `__context__`.** In
  OR-Tools 9.15 SCIP solves them; HiGHS, CP-SAT (through MathOpt), GLOP and PDLP refuse them.
- **A model for HiGHS states the rule as a linear row.** With a bound from the data, the linear
  form gives the same optimum.

## Reference

| Task | Code |
| --- | --- |
| row holds when $`z = 1`$ | `model.add_indicator_constraint(indicator=z, implied_constraint=expr <= u)` |
| row holds when $`z = 0`$ | `model.add_indicator_constraint(indicator=z, activate_on_zero=True, implied_constraint=...)` |
| row given in parts | `implied_expr=expr, implied_lb=l, implied_ub=u` |
| two-sided row (stored, but refused by SCIP: write one constraint per side) | `implied_constraint=(l <= expr) <= u` |
| count, list, delete | `get_num_indicator_constraints()`, `get_indicator_constraints()`, `delete_indicator_constraint(ic)` |
| the solver's reason for a refusal | `error.__context__` (OR-Tools 9.15) |

| Term | Meaning |
| --- | --- |
| indicator constraint | a binary variable, a linear row, and the value of the binary at which the row must hold |
| implied constraint | the row of an indicator constraint |
| limited mutability | an indicator constraint can be deleted, not edited |
| `INVALID_ARGUMENT`, `UNIMPLEMENTED` | status codes: the solver cannot take the model; MathOpt has no translation for it yet |

**Further reading.** OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt): the
solvers MathOpt can call, and indicator constraints among its specialized MIP constraints. The
`add_indicator_constraint` docstring in
[`ortools/math_opt/python/model.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py)
and the `IndicatorConstraint` class in
[`indicator_constraints.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/indicator_constraints.py):
the two ways to pass the row, the binary rule, and limited mutability. The
[MathOpt Python samples](https://github.com/google/or-tools/tree/stable/ortools/math_opt/samples/python),
none of which uses an indicator constraint; their models (`facility_location.py`,
`time_indexed_scheduling.py`) write their logic as linear rows.

## Challenges

1. Write the reserve rule with `activate_on_zero=True`. What variable would you need, and is it
   worth adding?
2. The risk office wants the reserve to be $1,000k, not 10%, in a year a large project starts.
   Write the indicator row and the linear row. Is the linear row still exact with
   $`M = 1{,}000`$?
3. A program deletes a start variable that is an indicator. What does the docstring say happens at
   the next solve, and how would you find which constraint is to blame from the error's ids?

## Design Note: Keep the Parts, Not Just the Constraint

`reserve_rule.py` keeps every reserve constraint in a dict keyed by project and year, and builds
each from `pm.spend[t]`, an expression the builder already keeps. Both habits pay off the first
time a rule changes: an indicator constraint cannot be edited, so changing it means building it
again from its parts. A model builder that returns its expressions and rows by key, rather than
only the model, is what lets every lesson in this module edit a model instead of rebuilding it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**reserve_rule.py.** The reserve rule as 12 indicator constraints on the start variables, read back,
solved by SCIP, refused by HiGHS, CP-SAT and GLOP, and changed by deleting and re-adding (*Any Binary
in the Model Can Be the Indicator*, *An Indicator Constraint Reads Back*, *The Solver Decides*).
*Try:* Lower `LARGE` to 2,500 and predict whether the NPV falls further before running.

- Program: [reserve_rule.py](src/reserve_rule.py)

**indicator_forms.py.** The same indicator written as a row and in parts, a two-sided one switched
on at zero, the refusal of a continuous indicator, and the linear form solved by HiGHS (*An
Indicator Constraint Is a Binary, a Row and the Value That Switches It On*, *A Model for HiGHS States
the Rule as a Linear Row*). *Try:* Make `SHARE` 0.8 and predict whether the two NPVs still agree.

- Program: [indicator_forms.py](src/indicator_forms.py)

**plan_model.py.** The model builder and the `refusal`, `quiet` and `solve` helpers every program
in this module uses.

- Library: [plan_model.py](src/plan_model.py)
