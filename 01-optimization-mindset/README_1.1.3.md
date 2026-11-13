# 1.1.3 The Problem Zoo: LP, MILP, CP, NLP and How to Pick

A colleague has written the tiny GridCap selection model and asks which solver to use. The
OR-Tools documentation offers GLOP, PDLP, HiGHS, SCIP, CP-SAT and a routing library. Picking from
that list by name is guesswork. The choice follows from two questions about the model: are the
variables continuous or whole numbers, and are the objective and the constraints straight lines?
This lesson solves one GridCap question four ways, one per problem class, in four rules.

## A Linear Program Allows Fractions, and Solves Fast Because It Does

A **linear program** (LP) has continuous variables, a linear objective and linear constraints:
every term is a number times one variable. Here is the tiny selection model with each $`x_i`$
allowed anywhere between 0 and 1, solved with GLOP, OR-Tools' LP solver:

```python
x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
     for p in tiny.projects}
model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in tiny.projects) <= tiny.capital_budget,
                            name="budget")
```

```text
LP   GLOP  OPTIMAL value 3,770.1
       {'P001': 1.0, 'P002': 1.0, 'P003': 0.099, 'P004': 0.099, 'P006': 1.0}
```

The answer funds 9.9% of the tower set and 9.9% of the breaker bay. The utility cannot build a
tenth of a tower set. For allocating money across programs, or flows on a network, fractions are
fine and the LP is the right model. For yes/no decisions the LP answer is not a plan. It is still
useful: no plan can be worth more than $3,770.1k, because the LP had every plan available and more
besides. A number that no plan can beat is called a **bound** (an *upper* bound when you
maximize). The same model with its whole-number requirement dropped is the model's **LP
relaxation**, and its value is always such a bound. A bound says nothing about which plan is best:
until a solver proves otherwise, the best plan may be worth anything between the best plan found
so far and the bound. Section 3 builds on that bound.

Allowing fractions is also what makes an LP fast. The best point can be reached by moving steadily
toward better values along the rules' boundary, and section 2 shows how. A model with yes/no
variables has no such path between plans, so its solver has to search, which is the next rule.

## A Mixed-Integer Program Adds Whole-Number Variables, and the Search That Comes With Them

Mark the variables as integer (`is_integer=True`), and the same model is a **mixed-integer linear
program** (MILP). Solved with HiGHS:

```text
MILP HIGHS OPTIMAL value 3,627.0
       {'P001': 1.0, 'P002': 1.0, 'P005': 1.0, 'P006': 1.0}
```

That is the plan brute force found in lesson 1.1.1, and $3,627k is below the LP's $3,770.1k, as it
must be. The gap between the two numbers is what section 3 is about: a MILP solver solves many
LPs, branching on fractional variables until the fractions are gone.

Why not solve the LP and round its fractions? Because the best whole-number plan need not be near
the LP's answer. The OR-Tools documentation shows this with a two-variable model (its MathOpt
sample `integer_programming.py`), adapted here to solve it both ways:

```math
\begin{aligned}
\max \;& x + 10y \\
\text{s.t. }& x + 7y \le 17.5 && \text{(c1)} \\
& 0 \le x \le 3.5, \quad y \ge 0 \\
& x, y \in \mathbb{Z} \quad \text{(MILP only)}
\end{aligned}
```

```python
def build(integer: bool) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="mip-example")
    x = model.add_variable(lb=0, ub=3.5, is_integer=integer, name="x")
    y = model.add_variable(lb=0, is_integer=integer, name="y")
    model.add_linear_constraint(x + 7 * y <= 17.5, name="c1")
    model.maximize(x + 10 * y)
    return model, x, y
```

```text
LP   GLOP  OPTIMAL value 25.0  x = 0.0, y = 2.5
MILP HIGHS OPTIMAL value 23.0  x = 3.0, y = 2.0
rounded (0, 2): allowed, value 20
rounded (0, 3): breaks c1
```

The LP puts everything into $`y`$ and stops at $`y = 2.5`$. Rounding $`y`$ up breaks (c1);
rounding it down gives an allowed point worth 20. The best whole-number point is worth 23, and it
sits at $`x = 3`$, where the LP had $`x = 0`$. Rounding gave a worse plan or a broken rule; finding the
best whole-number plan takes the MILP solver's search. (The sample writes $`x \le 3.5`$ as a second
row and solves with SCIP; here it is a bound on the variable, and HiGHS solves the MILP. Both give
23 at $`(3, 2)`$.)

"Mixed" means some variables may stay continuous. A capital plan with binary *fund* decisions and
continuous *spend per year* amounts is a MILP, and it is the main model class of this course and
of the job it prepares you for.

## Every MathOpt Program Has the Same Five Parts

The LP and the MILP above are one Python function, and every MathOpt model in this course has its
shape. Read it once, part by part:

```python
def build(integer: bool) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="tiny-selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in tiny.projects}
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in tiny.projects) <= tiny.capital_budget,
                                name="budget")
    for p in tiny.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
    model.add_linear_constraint(x["P006"] + x["P007"] <= 1, name="alt_G006")
    model.maximize(sum(p.value * x[p.project_id] for p in tiny.projects))
    return model, x
```

1. **A model.** `mathopt.Model(name=...)` is an empty container. Nothing is solved yet.
2. **Variables, with their domains.** `add_variable(lb=0, ub=1, is_integer=...)` is $`0 \le x_i \le 1`$,
   and `is_integer=True` makes it $`x_i \in \{0, 1\}`$. `add_binary_variable(name=...)` is a
   shorter way to write that binary. Keep each variable in a dict by its project id, because the
   rows and the answer are read through it.
3. **Constraints.** `add_linear_constraint(...)` takes one comparison of linear expressions:
   `<=`, `>=` or `==`. Sums of number × variable are written with Python's `sum` and `*`. The
   `name` is the row's label in the formulation (`budget`, `must_P002`), and it is what you will
   search for when a model misbehaves.
4. **An objective.** `model.maximize(...)` or `model.minimize(...)`, once.
5. **A solve, and a status before anything else.** The rest of the program:

```python
for integer, solver in ((False, mathopt.SolverType.GLOP), (True, mathopt.SolverType.HIGHS)):
    model, x = build(integer)
    result = mathopt.solve(model, solver)
    chosen = {pid: round(result.variable_values(v), 3) for pid, v in x.items() if result.variable_values(v) > 1e-9}
    kind = "MILP" if integer else "LP  "
    print(f"{kind} {solver.name:5} {result.termination.reason.name} value {result.objective_value():,.1f}")
    print("      ", chosen)
```

`mathopt.solve(model, solver)` returns a result. `result.termination.reason` says how the solve
ended: `OPTIMAL` means the plan it returns is proven best. `result.objective_value()` is the plan's
value, and `result.variable_values(v)` is one variable's value in it. Read the status first,
because when no plan satisfies every rule there is no value to read. Give the tiny portfolio a
budget of $2,000k, less than the must-do P002 costs, and the same kind of model answers:

```text
budget 7,390: OPTIMAL, value 3,627.0, x_P006 = 1.0
budget 2,000: INFEASIBLE
every status: OPTIMAL, INFEASIBLE, UNBOUNDED, INFEASIBLE_OR_UNBOUNDED, IMPRECISE, FEASIBLE, NO_SOLUTION_FOUND, NUMERICAL_ERROR, OTHER_ERROR
```

`INFEASIBLE` is a proof that the rules contradict each other, not a failure of the solver. Section
9 shows how to find which rows are responsible. The last line is every way a solve can end. Only
`OPTIMAL` comes with a proven best plan; `FEASIBLE` means a plan was found but not proven best
(a time limit stopped the search, section 3), and every other status means there is no plan to
read. So a program checks for `OPTIMAL` (or accepts `FEASIBLE` knowingly) before it asks for a
value.

<!-- practice 1 -->

## Constraint Programming Searches Over Logic and Integers Directly

CP-SAT, OR-Tools' constraint programming solver, works on integer and Boolean variables and lets
you state some rules as logic rather than arithmetic:

```python
model.add_implication(x[p.project_id], x[p.parent])      # child => parent
```

```text
CP-SAT OPTIMAL value 3627
        ['P001', 'P002', 'P005', 'P006']
```

Same answer. The difference is in what each solver is good at. CP-SAT has no continuous variables,
so a cost of $2,150.5k has to be scaled to integers, and it shines on scheduling, sequencing and
dense logic (lesson 4.4.4 measures when). A MILP solver handles continuous quantities directly and
proves optimality through LP bounds. For GridCap's selection both work; for a crew schedule with
no-overlap rules, CP-SAT is usually the better tool.

## A Nonlinear Program Has Curves, and Curves Cost You Guarantees

Some relationships are not straight lines. Suppose each program's value shows diminishing
returns, $`v_k(s) = a_k \sqrt{s}`$: the thousandth dollar of vegetation work buys less than the
first. Splitting the budget to maximize total value is a **nonlinear program** (NLP):

```math
\max \sum_k a_k \sqrt{s_k} \quad \text{s.t.} \quad \sum_k s_k = 7{,}390, \; s_k \ge 0
```

```python
result = minimize(lambda s: -total_value(s), x0=[BUDGET / 3] * 3, method="SLSQP",
                  bounds=[(0, BUDGET)] * 3, constraints=[{"type": "eq", "fun": lambda s: sum(s) - BUDGET}])
```

```text
SLSQP success value 6,228.8
  transmission  $2,252k
  distribution  $4,258k
  vegetation    $880k
```

A curve is **concave** when it bends downward, like $`\sqrt{s}`$: each extra dollar buys less, and
a straight line between two points of the curve lies below it. It is **convex** when it bends
upward, like $`s^2`$. When you maximize a sum of concave curves (or minimize a sum of convex ones)
under linear rules, any point that no small step improves is the best point overall. This one is
easy because the curve is concave. Without that shape, a local NLP method can stop at a point that is only the best in its neighborhood, and
it will not tell you. It still respects the budget and every other constraint; the risk is which
optimum it stops at, not whether the point is allowed. The usual move in capital planning is to approximate the curve with straight
pieces and stay in MILP, where the solver proves optimality (section 6.6).

<!-- practice 2 -->

## The Model

The LP and the MILP of this lesson are one model with one difference, the domain of $`x_i`$. With
the sets and parameters of lesson 1.1.1:

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{npv}_i\, x_i \\
\text{s.t. }& \text{(budget), (must}_i\text{), (parent}_c\text{), (alt}_g\text{) as in lesson 1.1.1} \\
& 0 \le x_i \le 1 \quad \forall i \in P && \text{(LP: GLOP, value 3,770.1)} \\
& x_i \in \{0, 1\} \quad \forall i \in P && \text{(MILP: HiGHS, value 3,627.0)}
\end{aligned}
```

The CP-SAT model states the same rows over Boolean variables, with (parent$`_c`$) written as the
implication $`x_c \Rightarrow x_{p(c)}`$ and (alt$`_g`$) as "at most one". The NLP of the last
section is a different model: one continuous variable $`s_k`$ per program, the objective
$`\max \sum_k a_k \sqrt{s_k}`$, the row $`\sum_k s_k = 7{,}390`$ and the bounds $`s_k \ge 0`$.

## Summary

- **An LP allows fractions and solves fast because it does.** Use it for amounts; for yes/no
  decisions, use its value as an upper bound, not as a plan.
- **A MILP adds whole-number variables and a search.** It is the default model for capital
  planning, and its answer is never better than its LP relaxation.
- **CP searches over logic and integers directly.** It suits scheduling and dense logic, and needs
  integer data.
- **Every MathOpt program has the same five parts.** A model, variables with their domains, named
  rows, one objective, and a solve whose status you read before its values.
- **An NLP has curves and loses guarantees unless they bend the right way:** concave when you
  maximize, convex when you minimize. Approximating a curve with linear pieces keeps you in MILP.

## Reference

| Class | Variables | Objective and constraints | OR-Tools solvers | Typical GridCap use |
| --- | --- | --- | --- | --- |
| LP | continuous | linear | GLOP, PDLP, HiGHS (via MathOpt) | budget split, bounds |
| MILP | some integer | linear | HiGHS, SCIP (`SolverType.GSCIP`), Gurobi, all via MathOpt | project selection and timing |
| CP | integer, Boolean | linear plus logical and global constraints | CP-SAT | crew scheduling, rule-heavy selection |
| NLP | continuous | at least one nonlinear term | no general NLP solver (MathOpt takes quadratic objectives on some solvers); SciPy for small ones | diminishing-returns curves, before linearizing |

| If your model has… | Pick |
| --- | --- |
| only amounts, all linear | LP |
| yes/no or count decisions, linear rules | MILP |
| intervals, no-overlap, many logical rules, all-integer data | CP-SAT |
| a curve you cannot avoid | piecewise-linear MILP first; NLP only if that fails |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt can call and the model features it accepts, quadratic objectives included); [Mixed-Integer Programming (OR-Tools)](https://developers.google.com/optimization/mip) (when to reach for a MIP solver and when for CP-SAT); [Solving a MIP Problem (OR-Tools)](https://developers.google.com/optimization/mip/mip_example) (the two-variable example of this lesson, with its LP relaxation); [MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (the same example as a MathOpt program that reads its status first); [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver) (CP-SAT works over integers only, and scales fractional data); [MO-book, Chapter 3: Mixed-integer linear optimization](https://mobook.github.io/MO-book/notebooks/03/03.00.html) (why some rules need integer variables, with worked models).

## Challenges

1. The LP funded 9.9% of P003 and P004. Explain why those two get the same fraction.
2. Name one GridCap rule that is awkward in a MILP and natural in CP-SAT, and one the other way.
3. If vegetation's value curve were $`a\, s^2`$ instead of $`a \sqrt{s}`$, what would go wrong with
   SLSQP?

## Design Note: One Model, Several Solvers

MathOpt lets the same model run on GLOP, HiGHS, SCIP or Gurobi by changing one argument, which is
how this lesson switched between LP and MILP. The cost is that you can use only what every chosen
solver understands; a feature one solver lacks is refused when you solve (lesson 4.2.4). Section 4
treats that trade in detail.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**zoo_lp_milp.py.** The tiny selection model as an LP with GLOP and as a MILP with HiGHS, from the section on the five parts of a MathOpt program. *Try:* Delete the `alt_G006` row and run it. Predict which of the two values moves.

- Program: [zoo_lp_milp.py](src/zoo_lp_milp.py)

**mip_example.py.** Adapted from the OR-Tools MathOpt sample `integer_programming.py`: the two-variable model solved as an LP with GLOP and as a MILP with HiGHS, and the LP answer rounded both ways (*A Mixed-Integer Program Adds Whole-Number Variables*). *Try:* Change the right-hand side of `c1` from 17.5 to 21. Predict the LP's value and whether rounding now finds the MILP's plan.

- Program: [mip_example.py](src/mip_example.py)

**mathopt_status.py.** Reads a solve's status before its values, and lists every status a solve can end with. *Try:* Call `solve_too_small` with 2,730, exactly P002's cost. Predict the status first.

- Program: [mathopt_status.py](src/mathopt_status.py)

**zoo_cp.py.** The same selection in CP-SAT, with the parent rule as an implication (*Constraint Programming*). *Try:* Replace `add_implication` with a linear row of the same meaning. Does the answer change?

- Program: [zoo_cp.py](src/zoo_cp.py)

**zoo_nlp.py.** Splits the budget across three programs whose value is a square-root curve (*A Nonlinear Program Has Curves*). *Try:* Change the curve to `A[k] * s ** 2` (convex) and run it. Is the split it returns the best one? How would you check?

- Program: [zoo_nlp.py](src/zoo_nlp.py)
