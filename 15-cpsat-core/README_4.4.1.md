# 4.4.1 Integer and Boolean Variables, Linear Constraints Over Integers

GridCap's planners have one more lever this year. The capital budget of the small portfolio is
$38,390k, and the treasury has arranged a credit line on top of it: four tranches of $500k each,
drawn whole, each costing $300k in interest and fees over the plan. Drawing a tranche pays only if
the projects it lets in are worth more than $300k. The planners also want each program's work kept
within the crew-months its own crews can give over the five years.

You could write this as a MILP in MathOpt, as lessons 1.1.1 and 3.1.1 did. This module writes it in
**CP-SAT**, OR-Tools' other integer solver, which lesson 1.1.3 used briefly. CP-SAT
stands for *constraint programming* with a *SAT* solver inside: it searches over variables that
take whole-number values, deducing from each constraint which values are still possible, and it
learns from every dead end (the CP-SAT Primer's chapter on its search describes the machinery; this
module needs only its consequences). Those consequences are the rules of this lesson: every variable
is an integer with a known finite range, every constraint has whole-number coefficients, and every
answer starts with a status that says what kind of answer it is.

GridCap is a fictional utility's portfolio, generated for this course. None of its numbers describe
a real company, and the credit line is invented for this lesson.

## The Model

The one-period selection of lesson 1.1.1, with a crew row per program and the credit line.

**Sets.** $`P`$, the projects (40 on GridCap small); $`G`$, the programs (transmission,
distribution, vegetation), with $`P_g \subseteq P`$ the projects of program $`g`$; $`M \subseteq P`$,
the must-do projects; $`C \subseteq P`$, the child projects, each with a parent $`p(c)`$; $`\mathcal{A}`$,
the alternative groups, each a set of projects of which at most one may be funded.

**Parameters.** $`v_i`$, the NPV of project $`i`$ if it starts as early as it can ($k);
$`\text{capex}_i`$, its total cost ($k); $`n_i`$, the crew-months it needs over its life (its
crew-months per year of work times its years of work); $`N_g`$, the crew-months program $`g`$'s own
crews give over the five years; $`B = 38{,}390`$, the capital budget ($k); a tranche is $500k and
costs $300k; there are 4 tranches.

**Variables.**

```math
x_i \in \{0, 1\} \quad \forall i \in P \qquad k \in \{0, 1, 2, 3, 4\}
```

$`x_i = 1`$ if project $`i`$ is funded; $`k`$ is the number of tranches drawn. $`k`$ is a
**general integer variable**: an integer that can take more values than 0 and 1.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i \;-\; 300\, k
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B + 500\, k && && \text{(budget)} \\
\sum_{i \in P_g} n_i\, x_i &\le N_g && \forall g \in G && \text{(crews}_g) \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in a} x_i &\le 1 && \forall a \in \mathcal{A} && \text{(alt}_a)
\end{aligned}
```

Every coefficient here is a whole number: GridCap keeps money in whole $k and crew-months as whole
months. That is what makes this model a CP-SAT model as it stands. The code names the rows `budget`,
`crews_transmission`, `must_P003`, `parent_P016` and `alt_G001`.

## A CP-SAT Program Is a Model, a Solver and a Status Check

Every CP-SAT program has the same four steps, and the OR-Tools guide *CP-SAT Solver* teaches them on
a model so small it has no data at all: three variables that each take a value 0, 1 or 2, and one
constraint, $`x \ne y`$. The program below is that example, adapted:

```python
model = cp_model.CpModel()

num_vals = 3
x = model.new_int_var(0, num_vals - 1, "x")
y = model.new_int_var(0, num_vals - 1, "y")
z = model.new_int_var(0, num_vals - 1, "z")

model.add(x != y)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"status {solver.status_name(status)}: x = {solver.value(x)}, y = {solver.value(y)}, z = {solver.value(z)}")
else:
    print("No solution found.")
```

```text
status OPTIMAL: x = 1, y = 0, z = 0
```

1. **The model.** `cp_model.CpModel()` is an empty container. It holds variables, constraints and
   at most one objective, and nothing is solved while you fill it.
2. **The variables.** `new_int_var(lb, ub, name)` makes an integer variable that may take any whole
   value from `lb` to `ub`, both included. The name is for printing and for the solver's log.
3. **The constraints.** `model.add(...)` takes a comparison between linear expressions, here
   `x != y`.
4. **The solver and the status.** `cp_model.CpSolver()` runs the search; `solve(model)` returns a
   **status**, a code that says what the solver found. Only after checking it does the program ask
   for values, with `solver.value(var)`.

The model has no objective, so any assignment that satisfies the constraint is as good as any other,
and the solver reports `OPTIMAL` for the first one it finds: with nothing to optimize, "a solution
was found" and "an optimal solution was found" are the same statement.

The method names are snake_case (`new_int_var`, `solve`, `status_name`). Older code and older
answers online use CamelCase (`NewIntVar`, `Solve`); OR-Tools 9.15 still accepts those names, and the
`cp_model.py` source marks them as deprecated aliases. This course writes snake_case, as the OR-Tools
guides now do.

## Every Variable Is an Integer With a Finite Domain

A variable's **domain** is the set of values it may take. CP-SAT has no other kind of variable: no
continuous variable, and no integer without bounds. There are three ways to make one:

```python
x = model.new_bool_var("x_P001")                          # a Boolean: the integers 0 and 1
k = model.new_int_var(0, 4, "tranches")                   # an integer from 0 to 4
draw = model.new_int_var_from_domain(                      # only these four values
    cp_model.Domain.from_values([0, 500, 1000, 2000]), "draw")
print(repr(x), "|", repr(k), "|", repr(draw))
print("not x:", ~x)
```

```text
x_P001(0..1) | tranches(0..4) | draw(0, 500, 1000, 2000)
not x: not(x_P001)
```

- **`new_bool_var(name)`** is the 0/1 variable, the binary of lesson 3.1.1. It is an integer
  variable with the domain 0..1, so it can appear in sums with a coefficient like any other.
  It is also a truth value: `~x` is "not x", which lesson 4.4.2 builds on.
- **`new_int_var(lb, ub, name)`** is a general integer, here the tranche count $`k`$ of the model.
- **`new_int_var_from_domain(domain, name)`** takes any finite set of integers, given as a
  `cp_model.Domain`. `Domain.from_values` lists the values; `Domain.from_intervals` takes ranges such
  as `[[0, 0], [500, 2000]]` ("nothing, or at least 500"). A MILP has no such variable: it would need
  one binary per allowed value, or a binary and two rows for the gap.

Asked for the smallest draw that covers a $700k shortfall, the solver can only answer with a value
of the domain:

```python
model.add(draw >= 700)
model.minimize(draw)
solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status), "draw =", solver.value(draw))
```

```text
OPTIMAL draw = 1000
```

**Why the bounds must be finite.** CP-SAT reasons about each variable as a range of whole numbers
and narrows the range as the search goes (this narrowing is called **propagation**). It also adds up
the largest and smallest values each constraint's left side can take, in 64-bit integers, and it
checks that no such sum can overflow before it starts. A variable with a huge range fails that
check, and the solver refuses the model rather than risk a wrong answer:

```python
big = cp_model.CpModel()
spend = big.new_int_var(0, 2**62, "spend")
print("validate:", big.validate())
print("status:", cp_model.CpSolver().status_name(cp_model.CpSolver().solve(big)))
```

```text
validate: var #0 domain do not fall in [-kint64max / 2, kint64max / 2]. name: "spend" domain: 0 domain: 4611686018427387904
status: MODEL_INVALID
```

`kint64max` is the largest 64-bit integer, $`2^{63} - 1`$, so a domain must lie within about
$`\pm 4.6 \times 10^{18}`$. `model.validate()` returns an empty string for a valid model and the
reason otherwise; call it when a solve says `MODEL_INVALID`. The practical rule is stronger than
"don't overflow": take each bound from the data. The tranche count is at most 4 because the credit
line has 4 tranches; a spend is at most the sum of the capex that could be in it. The CP-SAT Primer
recommends keeping every domain as tight as the data allows, because the solver's work on a variable
grows with the part of its range it has to reason about.

## A Linear Constraint Has Whole-Number Coefficients

`model.add` takes a comparison between two linear expressions: sums of variables times numbers, plus
a constant. `<=`, `>=` and `==` work as in MathOpt. Two more forms are CP-SAT's own:

```python
model.add(3 * a + 2 * b <= crews)                             # an inequality
model.add(a + b == 1)                                         # an equality
model.add_linear_constraint(2 * crews - a, 3, 7)              # a range: 3 <= 2 crews - a <= 7
model.add(crews != 3)                                         # "not equal" is allowed too
```

- **`add_linear_constraint(expr, lb, ub)`** states $`lb \le \text{expr} \le ub`$ in one constraint,
  a **ranged row** (a floor and a cap on the same sum).
- **`!=`** is not linear (the allowed values form two separate pieces, below 3 and above 3), and a
  MILP would need a binary and two big-M rows to state it. CP-SAT takes it directly. The Primer warns
  that many `!=` constraints can be slow, and offers `add_all_different` for "all of these differ".

What `model.add` refuses is a coefficient that is not a whole number:

```python
try:
    model.add(2.5 * a <= crews)
except TypeError as error:
    print("TypeError:", str(error).splitlines()[0])
```

```text
TypeError: Linear constraints only accept integer values and coefficients: FloatAffine(expr=a(0..1), coeff=2.5, offset=0) and crews(0..10)
OPTIMAL {'a': 1, 'b': 0, 'crews': 4}
```

The refusal happens in Python, when the row is built, before any solve. A right-hand side such as
`7.5` is refused the same way. The second line is the solve of the four valid rows with
`maximize(crews)`: $`a = 1`$ (so $`b = 0`$), and the range row allows $`2\,\text{crews} - 1 \le 7`$,
so crews is at most 4; 4 is not 3, so it is allowed.

This is the price of CP-SAT's exact integer arithmetic: there is no tolerance. A MILP solver accepts
a value within its integrality tolerance of a whole number as whole (lesson 6.2.2, in section 6, shows
what such a tolerance lets through); CP-SAT's values
are Python `int`s, and a row either holds exactly or it does not. Data with fractions has to be
multiplied out to whole numbers first, and lesson 4.4.3 shows how to do that without changing which
plans a row allows.

Now the whole model of this lesson, in code. The rows read as the formulation does; `with_name`
gives a constraint the name the formulation's label uses:

```python
model = cp_model.CpModel()
x = {p.project_id: model.new_bool_var(f"x_{p.project_id}") for p in portfolio.projects}
k = model.new_int_var(0, MAX_TRANCHES, "tranches")

model.add(sum(p.capex * x[p.project_id] for p in portfolio.projects)
          <= portfolio.capital_budget + TRANCHE * k).with_name("budget")
own = crew_capacity(portfolio)
for g in PROGRAMS:
    model.add(sum(crew_need(p) * x[p.project_id] for p in portfolio.projects if p.program == g)
              <= own[g]).with_name(f"crews_{g}")
for p in portfolio.projects:
    if p.must_do:
        model.add(x[p.project_id] == 1).with_name(f"must_{p.project_id}")
```

The builder has a switch, `native`, for lesson 4.4.2's way of writing the parent and alternative
rules. This lesson uses the linear rows, the `native=False` branch:

```python
    elif p.parent:
        model.add(x[p.project_id] <= x[p.parent]).with_name(f"parent_{p.project_id}")
for g, members in groups_of(portfolio).items():
```

```python
        model.add(sum(x[i] for i in members) <= 1).with_name(f"alt_{g}")

model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects) - TRANCHE_COST * k)
```

`maximize` sets the objective (lesson 4.4.3 covers it). Python's `sum` over CP-SAT variables builds a
linear expression, just as it does over MathOpt variables.

<!-- practice 1 -->

## Read the Status Before You Read a Value

`solver.solve(model)` returns one of five statuses. The program below provokes each of them on GridCap
small, using the lesson's model and some deliberately broken versions of it (one search worker
throughout, so every run repeats exactly; lesson 4.6.3 explains why that matters):

```text
full search                        OPTIMAL       objective    25,374  bound    25,374
stop after the first plan          FEASIBLE      objective    24,419  bound    25,852
no search allowed                  UNKNOWN       no plan to read
budget $5,530k (must-do $7,630k)   INFEASIBLE    no plan to read
a row that can overflow            MODEL_INVALID no plan to read
validate: Possible integer overflow in constraint: linear {
```

| Status | Meaning | Is there a plan to read? |
| --- | --- | --- |
| `OPTIMAL` | a solution was found and proved best (for a model with no objective: a solution was found) | yes |
| `FEASIBLE` | a solution was found, but the search stopped before proving it best | yes, with a gap |
| `INFEASIBLE` | proved that no assignment satisfies every constraint | no |
| `MODEL_INVALID` | the model breaks a rule of CP-SAT (overflow, an empty domain, ...); `model.validate()` says which | no |
| `UNKNOWN` | the search stopped (a limit) before it found a solution or proved there is none | no |

Each line of the output is one cause:

- **FEASIBLE.** `stop_after_first_solution = True` stops the search at the first plan, worth $24,419k.
  The **bound** ($25,852k) is the best value the solver can still not rule out; the true optimum lies
  between the two. A limit that stops the search with a plan in hand gives the same status; lesson 4.4.3
  shows it for a callback that stops the search.
- **UNKNOWN.** No conflicts allowed and no presolve: the solver stopped before it had any plan. The
  OR-Tools guide names the usual cause, a time or memory limit reached before the first plan.
- **INFEASIBLE.** With the capital budget cut to $5,530k, even the must-do projects ($7,630k) do not
  fit, with all four tranches ($2,000k) drawn. No plan exists, and CP-SAT proved it.
- **MODEL_INVALID.** A row with coefficients of $`2^{61}`$ on a variable that can reach 4 could
  overflow, so the model is refused before any search, and `validate()` names the row.

So a program tests the status first, as the OR-Tools example did, and reads values only for
`OPTIMAL` or `FEASIBLE` (and says which, because a `FEASIBLE` plan may not be the best). The lesson's
model, solved in full:

`one_worker()` is a helper of this module's `cpsat_models.py`, used by every lesson of the module:

```python
def one_worker() -> cp_model.CpSolver:
    """A CP-SAT solver on one search worker, so a run repeats exactly (lesson 4.6.3)."""
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    return solver
```

By default CP-SAT runs several search workers in parallel, and which one finds a plan first can
change from run to run. `solver.parameters` holds the solver's settings, and `num_workers = 1` keeps
the search on one worker, so the output below is the same on every run. Lesson 4.6.3 treats workers
and repeatable runs in depth.

```python
solver = one_worker()
status = solver.solve(sel.model)
print("status:", solver.status_name(status))
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    plan = funded(sel, solver)
    print(f"objective {solver.objective_value:,.0f}   bound {solver.best_objective_bound:,.0f}")
```

```text
status: OPTIMAL
objective 25,374   bound 25,374
funded 21 projects: P002 P003 P008 P010 P011 P015 P017 P018 P019 P021 P022 P025 P026 P028 P029 P030 P032 P034 P035 P038 P039
tranches drawn 3 -> $1,500k borrowed
capex 39,860 of 38,390 + 1,500
  crews_transmission uses 106 of 113 crew-months
  crews_distribution uses  30 of  47 crew-months
  crews_vegetation   uses  15 of  18 crew-months
types: int bool float
HiGHS OPTIMAL  objective 25,374  same plan: True
```

The planners draw three tranches, not four. The third $500k of credit lets in projects worth more than
its $300k cost; the fourth would not. Every crew row has room left, so on this data the budget, not the
crews, decides the plan. HiGHS, solving the same model through MathOpt, finds the same value and the
same plan.

Three ways to read a solution:

- **`solver.value(expr)`** returns the value of a variable *or of any linear expression*, as a Python
  `int`. The program asks for the capex of the plan with `solver.value(capex)`, where `capex` is the
  sum $`\sum_i \text{capex}_i x_i`$ built from the model's variables, so the check uses the same
  expression the row used.
- **`solver.boolean_value(literal)`** returns a Boolean as `True` or `False` (`funded()` uses it).
- **`solver.objective_value`** and **`solver.best_objective_bound`** are properties, not methods, and
  are floats, because an objective may have float coefficients (lesson 4.4.3).

<!-- practice 2 -->

## Summary

- **A CP-SAT program is a model, a solver and a status check.** `CpModel`, `new_*_var`, `add`,
  `CpSolver().solve(model)`, then the status, then `solver.value`.
- **Every variable is an integer with a finite domain.** `new_bool_var`, `new_int_var(lb, ub)` and
  `new_int_var_from_domain`; bounds from the data, and a domain beyond about $`\pm 4.6 \times 10^{18}`$
  makes the model invalid.
- **A linear constraint has whole-number coefficients.** `add` and `add_linear_constraint(expr, lb, ub)`;
  `!=` is allowed; a float coefficient is refused with a `TypeError` when the row is built.
- **Read the status before you read a value.** `OPTIMAL` and `FEASIBLE` carry a plan; `INFEASIBLE`,
  `MODEL_INVALID` and `UNKNOWN` do not.

## Reference

| Call | What it does |
| --- | --- |
| `cp_model.CpModel()` | an empty model |
| `model.new_bool_var(name)` | a 0/1 variable, also usable as a truth value |
| `model.new_int_var(lb, ub, name)` | an integer in $`[lb, ub]`$ |
| `model.new_int_var_from_domain(cp_model.Domain.from_values([...]), name)` | an integer in a listed set |
| `model.add(lhs <= rhs)`, `>=`, `==`, `!=` | a linear constraint with whole-number data |
| `model.add_linear_constraint(expr, lb, ub)` | $`lb \le \text{expr} \le ub`$ |
| `constraint.with_name(name)` | name a constraint |
| `model.validate()` | `""` if the model is valid, else the reason |
| `solver = cp_model.CpSolver()`; `status = solver.solve(model)` | solve; returns a status |
| `solver.status_name(status)` | the status as text |
| `solver.value(expr)`, `solver.boolean_value(lit)` | a solution's values (ints, bools) |
| `solver.objective_value`, `solver.best_objective_bound` | the plan's objective and the proven bound |

| MathOpt (lesson 4.2.1) | CP-SAT |
| --- | --- |
| `add_binary_variable(name=...)` | `new_bool_var(name)` |
| `add_integer_variable(lb=..., ub=...)` | `new_int_var(lb, ub, name)`; bounds are required |
| `add_variable(lb=..., ub=...)` (continuous) | none |
| `add_linear_constraint(row)` | `add(row)`, whole-number data only |
| `result.termination.reason` | the status returned by `solve` |
| `result.variable_values(x)` | `solver.value(x)` |

**Further reading:** [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver)
(the four steps of a CP-SAT program, the five statuses, and why the data must be integers; its
example is adapted above); [Solving an Optimization Problem (OR-Tools)](https://developers.google.com/optimization/cp/cp_example)
(the same steps with an objective and the solver's statistics); [`cp_model.py` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/python/cp_model.py)
(the docstrings of `new_int_var`, `add` and `add_linear_constraint`, and the deprecated CamelCase
aliases); [`cp_model.proto` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto)
(why a domain must be small enough to rule out integer overflow); [The CP-SAT Primer, Basic Modeling (Krupke)](https://d-krupke.github.io/cpsat-primer/modelling.html)
(variables, tight bounds, custom domains and linear constraints, with the warning about `!=`).

## Challenges

1. Change the credit line to six tranches of $250k at $150k each. Predict how much the planners draw,
   then run it.
2. Give the tranche count no upper bound you can justify, say $`10^{18}`$. Does `validate()` refuse
   the model? Does the solve change?
3. A planner wants "vegetation capex between $1,500k and $3,000k". Write it with
   `add_linear_constraint`, and as two `add` rows. Which do you prefer to read?

## Design Note: Keep a MathOpt Twin While You Learn

`cpsat_models.py` builds the lesson's model twice, once in CP-SAT and once in MathOpt, and
`first_selection.py` checks that HiGHS finds the same value. While a model is new, or when you port a
MILP to CP-SAT, a twin like this catches a row written wrongly in one of the two: two solvers agreeing
on a value is good evidence that both models say the same thing. Once the model is trusted, the twin
becomes a test (this module's tests keep it) rather than code that runs every time.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**simple_sat.py.** The smallest CP-SAT program, adapted from the OR-Tools example
`simple_sat_program.py` (*A CP-SAT Program Is a Model, a Solver and a Status Check*). *Try:* Add
`model.add(x == y)`. Predict the status before you run it.

- Program: [simple_sat.py](src/simple_sat.py)

**domains.py.** The three kinds of variable, a solve over a listed domain, and a domain too wide to
be valid (*Every Variable Is an Integer With a Finite Domain*). *Try:* Change the shortfall from 700
to 1,500. Predict the draw.

- Program: [domains.py](src/domains.py)

**integer_rows.py.** Inequality, equality, range and `!=` rows, and the `TypeError` a float
coefficient raises (*A Linear Constraint Has Whole-Number Coefficients*). *Try:* Remove `crews != 3`.
Predict whether the maximum changes.

- Program: [integer_rows.py](src/integer_rows.py)

**statuses.py.** The five statuses, each produced on GridCap small (*Read the Status Before You Read
a Value*). *Try:* Set the budget cut to $7,700k instead. Predict the status.

- Program: [statuses.py](src/statuses.py)

**first_selection.py.** The lesson's model solved by CP-SAT and by HiGHS, with the plan, the
tranches and the crew rows (*Read the Status Before You Read a Value*). *Try:* Make a tranche cost
$200k. Predict how many the planners draw.

- Program: [first_selection.py](src/first_selection.py)

**cpsat_models.py.** The lesson's model in CP-SAT and in MathOpt, the one-worker solver, the truth
table helper of lesson 4.4.2 and the quiet HiGHS solve that the module's programs share. It prints
nothing.

- Library: [cpsat_models.py](src/cpsat_models.py)
