# 4.2.1 Model, Variables, Constraints, Objective

GridCap's planning team has written its selection model three times already: once to try GLOP, once
for HiGHS and once for a colleague who wanted SCIP. Each copy drifted from the others. The team now
wants one model, written once from the formulation, that any solver can take. That is what MathOpt is
for: it is OR-Tools' solver-independent modeling layer. You describe the model in Python, and only at
solve time do you name the solver that should work on it.

Sections 1 to 3 used MathOpt without stopping to look at it (lesson 1.1.3 showed the five parts of a
program). This lesson goes through each building block in turn: what a model holds, what a variable
is, how an expression and a constraint are stored, and how the objective is set. At the end you build
GridCap's selection model from its formulation and read it back. GridCap is a fictional utility's
portfolio, invented for this course.

## A MathOpt Program Builds a Model, Then Hands It to a Solver

The OR-Tools documentation opens MathOpt with a two-variable LP. Adapted from that example (its
"basic example" page and the sample `basic_example.py`), here is the problem:

```math
\begin{aligned}
\max \;& x + 2y \\
\text{s.t. }& x + y \le 1.5 && \text{(c)} \\
& -1 \le x \le 1.5, \quad 0 \le y \le 1
\end{aligned}
```

And here is the whole program, in five steps:

```python
from ortools.math_opt.python import mathopt

# 1. A model: an empty, named container. Nothing about any solver yet.
model = mathopt.Model(name="getting_started_lp")

# 2. Variables, each with its bounds (its domain).
x = model.add_variable(lb=-1.0, ub=1.5, name="x")
y = model.add_variable(lb=0.0, ub=1.0, name="y")

# 3. Constraints, each one linear comparison.
model.add_linear_constraint(x + y <= 1.5, name="c")

# 4. The objective, with its sense.
model.maximize(x + 2 * y)

# 5. Solve with a named solver, and check how the solve ended before reading anything.
result = mathopt.solve(model, mathopt.SolverType.GLOP)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"model failed to solve: {result.termination}")
print("termination:", result.termination.reason.name)
print("objective:", result.objective_value())
print("x =", result.variable_values(x), " y =", result.variable_values(y))

# The same model, untouched, on a second solver: only the SolverType changes.
again = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("HiGHS:", again.termination.reason.name, again.objective_value())
```

```text
termination: OPTIMAL
objective: 2.5
x = 0.5  y = 1.0
HiGHS: OPTIMAL 2.5
```

Everything you import comes from one module, `ortools.math_opt.python.mathopt`. Read the steps as
two halves:

- **Steps 1 to 4 build a model.** `mathopt.Model` is a container for variables, constraints and one
  objective. It is plain data: building it runs no solver, and nothing in it names one. That is
  why the last two lines can hand the same object to HiGHS without changing it.
- **Step 5 solves it.** `mathopt.solve(model, solver_type)` copies the model into the solver you name,
  runs it, and returns a `SolveResult`. The solver is the second argument and nothing else. Lesson
  4.2.3 is about choosing it.

The `if` after the solve is the habit the OR-Tools samples all share: check the **termination
reason** (why the solver stopped) before reading values, because a solve that ended without a plan
has no values to read. Lesson 4.2.2 reads every part of the result.

The rest of this lesson takes steps 2, 3 and 4 one at a time.

## The Model

The model this lesson builds is GridCap's **project-selection MILP**, the one sections 1 to 3 solved:
one yes/no decision per project, each funded project starting at its earliest start year. A MILP
(mixed-integer linear program, lesson 1.1.3) is a linear model in which some variables may only take
whole-number values.

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years; $`M \subseteq P`$ the must-do
projects; $`\mathcal{G}`$ the alternative groups, each a set of projects of which at most one may be
funded; $`C \subseteq P`$ the child projects, each with a parent project $`p(c)`$.

**Parameters.** $`v_i`$, the NPV of project $`i`$ if it starts at its earliest start ($k);
$`c_{i,y}`$, what project $`i`$ spends in year $`y`$ when it starts then ($k, 0 in a year it is not
worked); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is funded.

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

| Label | Row name in `selection.py` |
| --- | --- |
| must$`_i`$ | `must_P002` |
| alt$`_g`$ | `alt_G006` |
| needs$`_c`$ | `needs_P004` |
| budget$`_y`$ | `budget_2027` |

Each line of the formulation becomes one MathOpt call: a set becomes a Python loop, a variable with
its domain becomes `add_variable`, a labelled row becomes `add_linear_constraint` with that label as
its `name`, and the objective becomes `maximize`. The next four sections show each call.

## A Variable Is Its Bounds and an Integer Flag, and Its Default Bounds Are Infinite

A MathOpt variable has exactly four properties: a lower bound, an upper bound, an integer flag and a
name. Its **domain**, the set of values it may take, follows from them. There are three ways to make
one, and they differ only in their defaults:

```python
spend = model.add_variable(lb=0, ub=2500, name="spend")                 # 0 <= spend <= 2500, continuous
crews = model.add_variable(lb=0, ub=6, is_integer=True, name="crews")   # crews in {0, 1, ..., 6}
fund = model.add_binary_variable(name="fund")                           # fund in {0, 1}
poles = model.add_integer_variable(lb=0, ub=40, name="poles")           # poles in {0, 1, ..., 40}

for v in model.variables():
    print(f"{v.name:6} id={v.id}  lb={v.lower_bound:g}  ub={v.upper_bound:g}  integer={v.integer}")
```

```text
spend  id=0  lb=0  ub=2500  integer=False
crews  id=1  lb=0  ub=6  integer=True
fund   id=2  lb=0  ub=1  integer=True
poles  id=3  lb=0  ub=40  integer=True
```

`add_binary_variable` is `add_variable(lb=0, ub=1, is_integer=True)` and nothing more; MathOpt has no
separate binary type. `add_integer_variable` sets the flag and leaves the bounds to you. Each
variable gets an `id`, its position in creation order, which is how the solver refers to it. The
`name` is for people: it shows up in logs and error messages, so give every variable one built from
its index (`x_P001`), as the formulation's subscripts are.

The value `add_variable` returns is a handle into the model, not a number. Its bounds can be read and
changed after it is created, which is the simplest way to fix a decision:

```python
fund.lower_bound = 1                       # now fund = 1: the decision is fixed
print("fund fixed:", fund.lower_bound, "<= fund <=", fund.upper_bound)
```

```text
fund fixed: 1.0 <= fund <= 1.0
```

Now the trap. With no bounds given, `add_variable` makes a variable that may take **any** real value,
$`-\infty < \text{level} < +\infty`$. Forget the bounds on a quantity that should be non-negative,
and the model allows negative spend, negative crews, or, as here, a value that grows without limit:

```python
free = mathopt.Model(name="forgot-the-bounds")
level = free.add_variable(name="level")
print("default bounds:", level.lower_bound, level.upper_bound, "integer:", level.integer)
free.maximize(level)
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS):
    print(f"{solver.name}: {mathopt.solve(free, solver).termination.reason.name}")
```

```text
default bounds: -inf inf integer: False
GLOP: INFEASIBLE_OR_UNBOUNDED
HIGHS: UNBOUNDED
```

A model is **unbounded** when its objective can be made as good as you like; a real plan never is,
so this status always means a missing bound or row. GLOP could only tell that the model was
infeasible *or* unbounded; HiGHS said which. Lesson 4.2.2 lists every status. The cure is in the
formulation: every variable is written with its domain ($`0 \le s_y \le \bar s`$), and the code
passes that domain as `lb` and `ub`, every time.

## An Expression Is Built With + and *, and Read Back by Flattening It

A **linear expression** is a sum of number × variable terms plus a constant, such as
$`3x + 3y + 5`$. In MathOpt you write it with Python's own `+` and `*`, and the result is an
object, not a number:

```python
expr = 2 * x + 3 * y + x + 5
print(type(expr).__name__, "->", expr)

flat = mathopt.as_flat_linear_expression(expr)
print(type(flat).__name__, "offset", flat.offset, {v.name: c for v, c in flat.terms.items()})

print("value at x=1, y=0.5:", mathopt.evaluate_expression(expr, {x: 1, y: 0.5}))
```

```text
LinearSum -> 5.0 + 3.0 * x + 3.0 * y
LinearExpression offset 5.0 {'x': 3.0, 'y': 3.0}
value at x=1, y=0.5: 9.5
```

Three things happened:

- **`+` and `*` build a tree.** `2 * x + 3 * y + x + 5` is stored as a `LinearSum` of its pieces, not
  added up. MathOpt's source explains why: adding as you go would copy the growing expression at every
  `+`, so it defers the work until the expression is used.
- **Flattening adds it up.** `as_flat_linear_expression` returns a `LinearExpression`: one
  coefficient per variable (the two `x` terms merged into $`3x`$) and a constant `offset`. You rarely
  call it yourself; `add_linear_constraint` and `maximize` do it for you.
- **`evaluate_expression` computes the value** for given variable values, without a solver: here
  $`3 \cdot 1 + 3 \cdot 0.5 + 5 = 9.5`$. It is how a test checks what a plan costs under the model's own
  expressions.

For sums over a set, Python's `sum` works, and MathOpt also offers `mathopt.fast_sum`:

```python
total = sum([x, y, z])                  # Python's sum: a nested LinearSum per addition, starting at 0
quick = mathopt.fast_sum([x, y, z])     # one flat LinearSum over the whole iterable
print("sum:", total, "| fast_sum:", quick)
```

```text
sum: 0.0 + 1.0 * x + 1.0 * y + 1.0 * z | fast_sum: 0.0 + 1.0 * x + 1.0 * y + 1.0 * z
```

Both give the same expression. The difference is the tree behind it: `sum` adds one item at a time,
so a sum over 10,000 projects nests 10,000 `LinearSum` objects, while `fast_sum` stores the items in
one. The `LinearSum` docstring recommends the flat form for large sums, several OR-Tools samples
(`facility_location.py`, `writing_seminar.py`) use `fast_sum` for their sums over sets, and this
module's `selection.py` does too.

## A Constraint Is One Comparison, Stored as lb ≤ expression ≤ ub

`add_linear_constraint` takes one comparison of linear expressions. Whatever form you write, MathOpt
moves every variable to the left, every constant to the right, and stores the row as

```math
\text{lb} \;\le\; \sum_j a_j\, x_j \;\le\; \text{ub}
```

with $`\text{lb} = -\infty`$ or $`\text{ub} = +\infty`$ for a one-sided row. The program builds one row
of each form and prints what was stored:

```python
def show(row: mathopt.LinearConstraint) -> None:
    terms = ", ".join(f"{t.coefficient:g}*{t.variable.name}" for t in row.terms())
    print(f"{row.name:8} lb={row.lower_bound:<5g} ub={row.upper_bound:<5g} terms: {terms}")


show(model.add_linear_constraint(x + y <= 1.5, name="upper"))
show(model.add_linear_constraint(x + z >= 1, name="lower"))
show(model.add_linear_constraint(y == 2 * x, name="equal"))
show(model.add_linear_constraint((1 <= y + z) <= 3, name="ranged"))
show(model.add_linear_constraint(2 * x + 5 <= y + 7, name="moved"))
show(model.add_linear_constraint(lb=1, ub=3, expr=x + z, name="keyword"))
```

```text
upper    lb=-inf  ub=1.5   terms: 1*x, 1*y
lower    lb=1     ub=inf   terms: 1*x, 1*z
equal    lb=0     ub=0     terms: 1*y, -2*x
ranged   lb=1     ub=3     terms: 1*y, 1*z
moved    lb=-inf  ub=2     terms: 2*x, -1*y
keyword  lb=1     ub=3     terms: 1*x, 1*z
```

Row by row:

- **`<=` and `>=`** give a row with one infinite bound.
- **`==`** gives a row with $`\text{lb} = \text{ub}`$. $`y = 2x`$ became $`y - 2x = 0`$: the variables
  moved left, so the bounds are both 0.
- **A ranged row**, $`1 \le y + z \le 3`$, is one row with both bounds finite, not two rows. Write it
  with parentheses, `(1 <= y + z) <= 3`, for the reason below.
- **Constants on both sides** are moved: $`2x + 5 \le y + 7`$ was stored as $`2x - y \le 2`$.
- **The keyword form** `add_linear_constraint(lb=..., ub=..., expr=...)` states the bounds directly. It
  is handy when the bounds come from data.

Two comparisons are refused, each with a `TypeError` at the line that writes them:

```python
try:
    model.add_linear_constraint(1 <= y + z <= 3)
except TypeError as error:
    for line in str(error).splitlines():
        print("TypeError:", line)
try:
    model.add_linear_constraint(x + y != 1)
except TypeError as error:
    print("TypeError:", error)
```

```text
TypeError: __bool__ is unsupported for LowerBoundedExpression
TypeError: If you were trying to create a two-sided or ranged linear inequality of the form `lb <= expr <= ub`, try `(lb <= expr) <= ub` instead
TypeError: != constraints are not supported
```

Python evaluates `a <= b <= c` as `(a <= b) and (b <= c)`, and the `and` asks the first half whether it
is true. A MathOpt comparison is a row, not a truth value, so it refuses; without that refusal the
first half would be silently dropped. Hence the parentheses. And `!=` is not a linear row at all:
"$`x + y \ne 1`$" cuts the feasible region in two, which no single $`\text{lb} \le \cdot \le
\text{ub}`$ can describe. Section 6 shows how a binary variable states such an either-or rule.

The `show` function above read the row back through the handle `add_linear_constraint` returned: its
`name`, `lower_bound`, `upper_bound` and `terms()`, each term a `variable` and a `coefficient`. Those
are also the bounds and coefficients you can change later (lesson 4.3.4 re-solves after such edits).

## The Objective Is Set by maximize or minimize, and a Second Call Replaces the First

A model has one objective, `model.objective`. `maximize(expr)` and `minimize(expr)` set its expression
and its sense in one call, and calling either again replaces both:

```python
model.maximize(2 * x + y)
print("first :", model.objective.is_maximize, dict(sorted((t.variable.name, t.coefficient) for t in model.objective.linear_terms())))
model.minimize(x - y + 10)
print("second:", model.objective.is_maximize, dict(sorted((t.variable.name, t.coefficient) for t in model.objective.linear_terms())),
      "offset", model.objective.offset)

result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print(result.termination.reason.name, "objective", result.objective_value(),
      "x =", result.variable_values(x), "y =", result.variable_values(y))
```

```text
first : True {'x': 2.0, 'y': 1.0}
second: False {'x': 1.0, 'y': -1.0} offset 10.0
OPTIMAL objective 8.5 x = 0.0 y = 1.5
```

The second call did not add to the first; the model now minimizes $`x - y + 10`$ and the first
objective is gone. The constant 10 is kept as the objective's **offset**, and the reported objective
value includes it: $`0 - 1.5 + 10 = 8.5`$. A constant cannot change which plan is best, but it makes
the reported number mean something, such as a fixed cost every plan pays.

Two consequences for real code. Build the objective as one expression (with `fast_sum` over the set)
and set it once; an objective assembled by several `maximize` calls keeps only the last. And check
the sense: maximizing a cost or minimizing a value is a model that solves happily and answers the
wrong question. Lesson 4.3.2 adds *auxiliary* objectives for ranked goals; the main objective still
works as shown here.

<!-- practice 1 -->

## Build From the Formulation One Labelled Row at a Time, and Read the Model Back

`selection.py` turns the formulation of The Model into code, one block per line of it. The variables
first, one per project, with their domain:

```python
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
```

Then each family of rows, under its quantifier, named after its label:

```python
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(mathopt.fast_sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    for p in portfolio.projects:
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"needs_{p.project_id}")
    budget = {}
    for y in portfolio.years:
        spend = mathopt.fast_sum(p.spend(p.earliest_start).get(y, 0) * x[p.project_id]
                                 for p in portfolio.projects)
        budget[y] = model.add_linear_constraint(spend <= portfolio.budget[y], name=f"budget_{y}")
    model.maximize(mathopt.fast_sum(p.value * x[p.project_id] for p in portfolio.projects))
```

The `x` dict, keyed by project id, is the formulation's subscript: $`x_i`$ is `x["P001"]`. The
budget rows are kept in a dict by year too, because later lessons read their dual values. The
`integer` argument is the only difference between the MILP and its LP relaxation.

After building, read the model back to check it says what the formulation says. Counting rows by
label and reading one row's terms catches most building mistakes before any solve:

```python
rows = list(model.linear_constraints())
kinds = {}
for row in rows:
    label = row.name.split("_")[0]
    kinds[label] = kinds.get(label, 0) + 1
print(f"{model.name}: {model.get_num_variables()} variables, {model.get_num_linear_constraints()} rows {kinds}")
x = sel.x["P001"]
print(f"{x.name}: lb={x.lower_bound:g} ub={x.upper_bound:g} integer={x.integer}")

row = sel.budget[2027]
terms = sorted(((t.variable.name, t.coefficient) for t in row.terms()), key=lambda t: -t[1])
print(f"{row.name}: {len(terms)} terms, ub={row.upper_bound:,.0f}; largest: {terms[:3]}")

objective = model.objective
print("maximize:", objective.is_maximize, "| terms:", len(list(objective.linear_terms())),
      "| offset:", objective.offset)
```

```text
GridCap small-selection: 40 variables, 13 rows {'must': 4, 'alt': 2, 'needs': 2, 'budget': 5}
x_P001: lb=0 ub=1 integer=True
budget_2027: 10 terms, ub=8,890; largest: [('x_P032', 5680.0), ('x_P034', 2130.0), ('x_P036', 1870.0)]
maximize: True | terms: 40 | offset: 0.0
OPTIMAL NPV 22,532k, 25 projects funded
```

Forty projects give 40 binaries; 4 must-dos, 2 alternative groups, 2 child projects and 5 years give
13 rows. The 2027 budget row has 10 terms, not 40: a project that spends nothing in 2027 gets a
coefficient of 0, and MathOpt stores no zero coefficients. The last line is the solve, with HiGHS, of
the model as built.

Names are for people, but MathOpt does check them, and not when you would expect. Two variables with
the same name are accepted when you create them and refused when you solve:

```python
model = mathopt.Model(name="duplicate-names")
first = model.add_binary_variable(name="x_P001")
second = model.add_binary_variable(name="x_P001")      # accepted here: nothing is checked yet
model.maximize(first + second)
print("built:", model.get_num_variables(), "variables, both named", first.name)
try:
    mathopt.solve(model, mathopt.SolverType.HIGHS)
except Exception as error:                              # OR-Tools 9.15 raises an AttributeError here
    print("raised:", type(error).__name__)
    print("reason:", error.__context__)                # the real message (lesson 4.2.4)
```

```text
built: 2 variables, both named x_P001
raised: AttributeError
reason: duplicate name inserted: x_P001; ModelProto.variables are invalid [INVALID_ARGUMENT]
```

The docstring of `add_variable` says it: names are for debugging, "but nonempty names must be
distinct". The check runs when `solve` exports the model, so a loop that builds a name from the wrong
index (two projects named `x_2027`) fails there, far from the line that caused it. The exception is
also not the one MathOpt meant to raise: in OR-Tools 9.15 the reason is hidden behind an
`AttributeError`, and lesson 4.2.4 shows how to read it.

<!-- practice 2 -->

## Summary

- **A MathOpt program builds a model, then hands it to a solver.** The model names no solver;
  `mathopt.solve(model, solver_type)` does, and its termination reason is checked before anything is
  read.
- **A variable is its bounds and an integer flag.** `add_binary_variable` is bounds 0 and 1 with the
  flag; `add_variable` with no bounds is free in both directions, so always pass the formulation's
  domain.
- **An expression is built with `+` and `*`** and kept as a tree; `as_flat_linear_expression` adds it
  up, `evaluate_expression` computes its value, and `fast_sum` keeps a large sum flat.
- **A constraint is one comparison, stored as lb ≤ expression ≤ ub.** A ranged row needs parentheses;
  `!=` is refused.
- **The objective is set by `maximize` or `minimize`,** and a second call replaces the first; a
  constant becomes its offset.
- **Build from the formulation one labelled row at a time, and read the model back.** Duplicate names
  are refused at solve time.

## Reference

| Call | What it makes |
| --- | --- |
| `mathopt.Model(name=...)` | an empty model |
| `model.add_variable(lb=, ub=, is_integer=, name=)` | a variable; defaults $`-\infty`$, $`+\infty`$, continuous |
| `model.add_binary_variable(name=)` | $`\{0, 1\}`$ |
| `model.add_integer_variable(lb=, ub=, name=)` | integer, bounds as given (default infinite) |
| `model.add_linear_constraint(expr <= b, name=)` | one row; also `>=`, `==`, `(a <= expr) <= b` |
| `model.add_linear_constraint(lb=, ub=, expr=, name=)` | one row from explicit bounds |
| `model.maximize(expr)`, `model.minimize(expr)` | the objective; replaces any earlier one |
| `mathopt.fast_sum(items)` | a flat sum of expressions |
| `mathopt.evaluate_expression(expr, {var: value})` | the expression's value, no solver |

| Read back | How |
| --- | --- |
| variables, rows | `model.variables()`, `model.linear_constraints()`, `get_num_variables()`, `get_num_linear_constraints()` |
| a variable | `v.name`, `v.id`, `v.lower_bound`, `v.upper_bound`, `v.integer` (all but `id` and `name` writable) |
| a row | `c.name`, `c.lower_bound`, `c.upper_bound`, `c.terms()` (`.variable`, `.coefficient`) |
| the objective | `model.objective.is_maximize`, `.offset`, `.linear_terms()` |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (what a MathOpt model may contain and which solvers it can be handed to); [MathOpt basic example (OR-Tools)](https://developers.google.com/optimization/math_opt/basic_example) (the two-variable LP this lesson's first program adapts, built and solved step by step); [MathOpt sample basic_example.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/basic_example.py) (the same steps with a binary variable and an objective built term by term); [MathOpt `model.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (the docstrings of `add_variable`, `add_linear_constraint` and the objective methods, including the two-sided form and the distinct-names rule); [MathOpt `variables.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/variables.py) (why expressions are kept as `LinearSum` trees, and why a flat sum is cheaper for large sets).

## Challenges

1. Write the GridCap budget row with the keyword form, `add_linear_constraint(lb=..., ub=...,
   expr=...)`. What value do you give `lb`?
2. Add a variable for unspent money in each year, $`u_y \ge 0`$, and change each budget row to an
   equation. Read one row back: what are its bounds now?
3. Build the selection model with `sum` instead of `fast_sum` on the large portfolio and time both
   builds. Is the difference worth a line of code?

## Design Note: Keep the Model Builder Free of Solver Choices

`selection.build` returns a model and the handles to its variables and rows; it never solves, never
sets a parameter and never names a solver. That separation is what MathOpt is designed around, and
it pays off in three ways. Tests can build the model and inspect it without a solver (the read-back
above). The same builder serves the LP relaxation and the MILP. And the solver can change, in a
config file or a command-line flag, without touching the model, which is how several OR-Tools
samples take their solver: as a flag whose value is a `SolverType`. Lesson 4.2.3 does exactly that.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**first_model.py.** Adapted from the OR-Tools MathOpt basic example: the two-variable LP built in five steps and solved with GLOP, then with HiGHS (*A MathOpt Program Builds a Model, Then Hands It to a Solver*). *Try:* Change the objective to `x + y`. Predict whether the optimum is still unique before you run it.

- Program: [first_model.py](src/first_model.py)

**variables.py.** The three ways to create a variable, a bound changed after creation, and a variable left with its default bounds (*A Variable Is Its Bounds and an Integer Flag*). *Try:* Give `level` a lower bound of 0 and an upper bound of 100. Predict the status on both solvers.

- Program: [variables.py](src/variables.py)

**expressions.py.** An expression as a tree, flattened and evaluated, and `sum` beside `fast_sum` (*An Expression Is Built With + and \**). *Try:* Evaluate `expr` at `x = 0, y = 2.5`. Predict the value first.

- Program: [expressions.py](src/expressions.py)

**constraints.py.** One row of every accepted form, read back as bounds and terms, and the two refused comparisons (*A Constraint Is One Comparison*). *Try:* Add `3 * z >= x + 2` and predict its stored bounds and terms.

- Program: [constraints.py](src/constraints.py)

**objective.py.** An objective set, replaced, and solved with an offset (*The Objective Is Set by maximize or minimize*). *Try:* Delete the `minimize` line. Predict the objective value HiGHS reports.

- Program: [objective.py](src/objective.py)

**build_selection.py.** GridCap small's selection model built from its formulation, read back row by row, and solved (*Build From the Formulation*). *Try:* Print the `budget_2030` row instead. Predict how many terms it has.

- Program: [build_selection.py](src/build_selection.py)

**duplicate_names.py.** Two variables with one name, accepted at build time and refused at solve time (*Build From the Formulation*). *Try:* Rename the second variable `x_P002`. Predict the objective value.

- Program: [duplicate_names.py](src/duplicate_names.py)

**selection.py.** The module's model builder: the selection MILP (or its LP relaxation), the plan read from a result, and a solve that keeps the bundled HiGHS's stray output off the screen. It runs nothing itself.

- Library: [selection.py](src/selection.py)
