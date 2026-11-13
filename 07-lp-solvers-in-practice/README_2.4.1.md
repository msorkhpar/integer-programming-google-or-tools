# 2.4.1 Simplex, Interior Point and PDLP: GLOP, HiGHS, PDLP

GridCap's planning team has a funding LP: what share of each candidate project to fund, year by
year, with unspent money carried forward. It runs on the medium portfolio (400 projects) every
week, and the team wants to run it on the large one (10,000 projects) for scenario work. A
colleague asks which LP solver to use. OR-Tools offers three through MathOpt: GLOP, HiGHS and
PDLP. They are three different algorithms, not three brands of one. This lesson solves the same LP
with each one, reads what each returns, and states the rules for choosing between them and for
checking that they agree. GridCap is a fictional utility; its numbers are teaching data, not any
real utility's.

The words used below: a **solver** is a program that solves models (GLOP, HiGHS, PDLP); an
**algorithm** is the method it uses inside (simplex, interior point, first order). HiGHS has
several algorithms; GLOP and PDLP have one family each. An **iteration** is one step of an
algorithm, and every solver counts them.

## The Model

The funding LP, stated in full before any code. Every project starts as early as it may; the LP
chooses how much of each to fund and how much money to carry from one year into the next.

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years, the first being $`y_0`$;
$`M \subseteq P`$ the must-do projects.

**Parameters.** $`c_{i,y}`$, what project $`i`$ spends in year $`y`$ if it starts at its earliest
start ($k; 0 in a year it is not worked, and spend after the last plan year is outside the plan);
$`v_i`$, the project's NPV at its earliest start ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`0 \le f_i \le 1`$ for every $`i \in P`$: the share of project $`i`$ funded, a
continuous amount (0.4 means 40% of its scope, cost and value). $`r_y \ge 0`$ for every
$`y \in Y`$: the money carried out of year $`y`$ into the next, with $`r_{y_0 - 1} = 0`$.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, f_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_{i,y}\, f_i + r_y &\le B_y + r_{y-1} && \forall y \in Y && \text{(cash}_y) \\
f_i &= 1 && \forall i \in M && \text{(must}_i)
\end{aligned}
```

Row (cash$`_y`$) says a year's spending plus what it carries out is at most its budget plus what
came in. Row (must$`_i`$) funds a must-do project in full. Every variable is continuous and every
term is a number times one variable, so this is a linear program (lesson 1.1.3). It is also the LP
relaxation (lesson 1.1.3) of a yes/no selection that starts each project as early as it may: with
$`f_i \in \{0, 1\}`$ instead, it would choose whole projects.

The code builds it in MathOpt, one row per labelled constraint and the row's label as its name:

```python
def build(portfolio: Portfolio) -> FundingLP:
    model = mathopt.Model(name="funding-lp")
    f = {p.project_id: model.add_variable(lb=0, ub=1, name=f"f_{p.project_id}") for p in portfolio.projects}
    carry = {y: model.add_variable(lb=0, name=f"carry_{y}") for y in portfolio.years}
    cash = {}
    for k, y in enumerate(portfolio.years):
        spend = sum(spend_in(p, y) * f[p.project_id] for p in portfolio.projects if spend_in(p, y))
        carried_in = carry[portfolio.years[k - 1]] if k else 0
        cash[y] = model.add_linear_constraint(spend + carry[y] - carried_in <= portfolio.budget[y], name=f"cash_{y}")
    must = {p.project_id: model.add_linear_constraint(f[p.project_id] == 1, name=f"must_{p.project_id}")
            for p in portfolio.projects if p.must_do}
    model.maximize(sum(p.value * f[p.project_id] for p in portfolio.projects))
    return FundingLP(model, f, carry, cash, must)
```

On the medium portfolio (10 years, 39 must-do projects) it has 400 share variables plus 10 carry
variables, and 10 cash rows plus 39 must rows:

```text
funding LP: 410 variables, 49 rows
```

The rest of the lesson solves this one model five ways. Here is the program's loop and what it
printed; the next three sections explain each line.

```python
RUNS = [
    ("GLOP  primal simplex", mathopt.SolverType.GLOP, mathopt.LPAlgorithm.PRIMAL_SIMPLEX),
    ("GLOP  dual simplex", mathopt.SolverType.GLOP, mathopt.LPAlgorithm.DUAL_SIMPLEX),
    ("HiGHS dual simplex", mathopt.SolverType.HIGHS, mathopt.LPAlgorithm.DUAL_SIMPLEX),
    ("HiGHS barrier", mathopt.SolverType.HIGHS, mathopt.LPAlgorithm.BARRIER),
    ("PDLP  first order", mathopt.SolverType.PDLP, mathopt.LPAlgorithm.FIRST_ORDER),
]

for label, solver, algorithm in RUNS:
    result = mathopt.solve(lp.model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
    stats = result.solve_stats
    print(f"{label:21} {result.termination.reason.name}  objective {result.objective_value():.4f}  "
          f"iterations: simplex {stats.simplex_iterations:3}, barrier {stats.barrier_iterations:2}, "
          f"first-order {stats.first_order_iterations:3}  in-between {in_between(lp, result)}")
```

```text
GLOP  primal simplex  OPTIMAL  objective 234898.1206  iterations: simplex 191, barrier  0, first-order   0  in-between 10
GLOP  dual simplex    OPTIMAL  objective 234898.1206  iterations: simplex  14, barrier  0, first-order   0  in-between 10
HiGHS dual simplex    OPTIMAL  objective 234898.1206  iterations: simplex  14, barrier  0, first-order   0  in-between 10
HiGHS barrier         OPTIMAL  objective 234898.1206  iterations: simplex   0, barrier 10, first-order   0  in-between 10
PDLP  first order     OPTIMAL  objective 234898.1297  iterations: simplex   0, barrier  0, first-order 256  in-between 10
GLOP's vertex: 4 projects partly funded, 6 years carrying money
```

`SolveParameters(lp_algorithm=...)` asks the solver for one algorithm; leave it out and the solver
picks its default. `result.solve_stats` counts the iterations of each kind; a solve fills only the
count of the algorithm it ran. The last column, **in-between**, counts the variables that sit
strictly between their bounds: shares above 0 and below 1, and carries above 0. It is computed by
`in_between` in `funding_lp.py`, and it is the key to the first rule.

## Simplex Walks From Vertex to Vertex and Ends on One

The allowed points of an LP form a polyhedron, and its corners are its **vertices** (lesson 1.2.3
calls them extreme points). If an LP has a best point, one of its vertices is best. The **simplex
method** uses that fact: it starts at a vertex and moves along an edge of the polyhedron to a
neighbouring vertex whose objective is at least as good, one move per iteration, until no
neighbour is better (lesson 2.2.2 builds a small simplex and walks it by hand). Each move is called
a **pivot**.

It comes in two forms:

- **Primal simplex** keeps every row satisfied at every step and improves the objective until no
  move helps. GLOP's primal simplex took 191 pivots here.
- **Dual simplex** keeps the optimality conditions satisfied at every step (no single move could
  improve the objective) and repairs broken rows one at a time, until none is broken. It reached the
  same vertex in 14 pivots on this LP, in both GLOP and HiGHS. Dual simplex is HiGHS's default for
  LPs; its documentation calls it likely faster and more robust than primal simplex.

The two solvers' defaults differ. GLOP's default is **primal simplex**: its parameter
`use_dual_simplex` is `false` unless you set it (lesson 2.4.3 relies on this). The end of the
program solves the LP once more on each solver with no `lp_algorithm`, and the pivot counts show
which form ran: GLOP's 191 is its primal simplex count, HiGHS's 14 its dual simplex count.

```python
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS):
    default = mathopt.solve(lp.model, solver)
    print(f"{solver.name} default: {default.termination.reason.name}, "
          f"simplex iterations {default.solve_stats.simplex_iterations}")
```

```text
GLOP default: OPTIMAL, simplex iterations 191
HIGHS default: OPTIMAL, simplex iterations 14
```

Neither form is faster on every LP; the counts above are for this LP. What both forms share is
where they stop: on a vertex. At a vertex every variable but a few sits on one of its bounds, and
the few that do not are all **basic** variables (lesson 2.2.2), of which there is one per row; so
at most one variable per row sits in between. Here the 39 must rows
only pin $`f_i = 1`$, so the 10 cash rows decide the vertex, and at most 10 variables can sit in
between. Every simplex run above has exactly 10; the program's last line splits GLOP's into 4 projects
partly funded and 6 years carrying money. That is why simplex answers are easy to read: most projects are funded fully or not at all.

## Interior Point Crosses the Inside in a Few Expensive Steps

An **interior point method**, also called **barrier**, does not walk the edges. It keeps every
variable strictly inside its bounds, never exactly on one, and moves through the inside toward an
optimum. The rows may be broken at first (the log below measures by how much); they are repaired
on the way.

**What it follows.** Complementary slackness (lesson 2.3.2) says that at an optimum, for every
variable, its distance from its bound times its reduced cost is 0, and for every row, its slack
times its price is 0. An interior point method relaxes each of those products from 0 to the same
small positive number $`\mu`$. For each $`\mu > 0`$ there is one point (a plan and its prices) where
the rows hold, the prices cover the objective, and every product equals $`\mu`$; since no product
is 0, no variable sits on a bound and no slack is 0, so the point is inside. These points form a
curve through the interior, the **central path**, and as $`\mu`$ shrinks toward 0 the path runs into
an optimum. The name "barrier" comes from an equivalent view: add $`\mu`$ times the logarithm of
each variable's distance to its bound to the objective. The logarithm falls to $`-\infty`$ at a
wall, so it is a barrier that keeps the point inside, and its weight $`\mu`$ is lowered step by
step.

**What each iteration solves.** One iteration takes one Newton step toward the path's point for a
smaller $`\mu`$: it writes the conditions "rows hold, prices cover, every product equals
$`\mu`$" to first order around the current point, which gives one system of linear equations in
all the variables and prices at once, and solves it. The system is built from the whole
constraint matrix, with weights that change at every iteration, so it is solved anew each time.
That is why one iteration costs far more than a pivot. The step then goes as far along that
direction as it can while staying inside, and $`\mu`$ is lowered.

HiGHS's log of its barrier run on the medium LP (its interior point code is called IPX) shows one
row per iteration:

```python
barrier = mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.BARRIER)
result, log = solve_with_log(lp.model, mathopt.SolverType.HIGHS, barrier)
```

```text
HiGHS log, interior point iterations:
 Iter       primal obj         dual obj       pinf       dinf       gap     time
   0   -1.95801682e+05  -6.53953148e+05   1.35e-01   3.85e-01  1.08e+00       <t>s
   1   -1.82776489e+05  -5.99319378e+05   3.65e-03   1.42e-02  1.07e+00       <t>s
   2   -2.04154489e+05  -3.90019063e+05   2.44e-04   4.16e-03  6.26e-01       <t>s
   3   -2.21235365e+05  -2.62264901e+05   2.19e-05   7.52e-04  1.70e-01       <t>s
   4   -2.31567381e+05  -2.39483123e+05   2.75e-06   1.32e-04  3.36e-02       <t>s
   5   -2.34229442e+05  -2.35889560e+05   4.22e-07   2.59e-05  7.06e-03       <t>s
   6   -2.34761249e+05  -2.35122482e+05   7.33e-08   5.45e-06  1.54e-03       <t>s
   7   -2.34860578e+05  -2.34968529e+05   1.15e-08   1.36e-06  4.60e-04       <t>s
   8   -2.34896862e+05  -2.34908308e+05   1.66e-10   1.88e-07  4.87e-05       <t>s
   9   -2.34898053e+05  -2.34898168e+05   3.17e-12   1.88e-13  4.86e-07       <t>s
 Constructing starting basis...
  10*  -2.34898121e+05  -2.34898121e+05   7.30e-16   1.35e-16  3.58e-12       <t>s
```

The objectives are negative because HiGHS minimizes $`-\sum_i v_i f_i`$ (lesson 2.4.2 reads the
same sign in the simplex log). `pinf` and `dinf` measure how far the rows and the price conditions
are still broken, and `gap` is the relative difference between the primal and dual objectives.
On the path that difference is the sum of the products, so it falls with $`\mu`$: from 1.08 to
$`3.58 \times 10^{-12}`$ in ten iterations, each iteration from the third on cutting it by a factor
of 3 or more. The starred row comes after IPX builds a starting basis
for itself; it is still an interior point iteration, the tenth, the count `barrier_iterations`
reported above.

**Why it ends near a vertex, not on one.** Every product equals $`\mu > 0`$ on the path, so the
method stops with variables that belong on a bound sitting a tiny distance off it, and its
objective a tiny bit short of the optimum. Solvers then run **crossover**, a clean-up that starts
from the barrier's point, moves the nearly-at-bound variables onto their bounds and finds the basis
of an optimal vertex. HiGHS runs crossover by default. The program solves the LP twice through
HiGHS's own Python API, `highspy` (as lesson 2.3.3 does), with HiGHS's option `run_crossover` off
and then on. It also sets `presolve` off, so that every variable goes through the interior point
method; with presolve, the fixed must-do shares would be removed first and put back at exactly 1.
For each run it counts the variables that sit strictly inside their bounds by more than a
threshold:

```python
    room = [min(x[c.index] - var.lower_bound, var.upper_bound - x[c.index]) for var, c in column.items()]
    counts = [sum(1 for r in room if r > tol) for tol in (0, 1e-12, 1e-9, 1e-6)]
```

```text
crossover status          objective   variables strictly inside their bounds, by more than
                                          0  1e-12  1e-9  1e-6
off       Optimal     234898.119606     410    410   369    21   of 410
on        Optimal     234898.120611      10     10    10    10   of 410
```

Without crossover, all 410 variables are strictly inside their bounds, none exactly on one, and
21 of them by more than $`10^{-6}`$, more than the 10 a vertex can have; the objective is 0.001
below the simplex value, because the point is allowed but not yet at the optimum. With crossover,
exactly 10 variables are inside and every other one is exactly on a bound: a vertex, with the
simplex objective. HiGHS's documentation warns that crossover can occasionally be very expensive,
and it can be switched off when an optimal point is enough and a vertex is not needed.

Barrier has to solve a large system at every iteration, and when it does so by factoring a
matrix, the factor can hold many more nonzeros than the constraint matrix, depending on how the
rows share variables. On very large LPs that factorization is what runs out first.

## PDLP Takes Many Cheap Steps and Stops Within a Tolerance

**PDLP** is a **first-order method**. It starts from duality (lesson 2.3.1). For an LP
$`\max c^\top x`$ subject to $`Ax \le b`$ and bounds on $`x`$, with prices $`y \ge 0`$ on the rows,
take the **Lagrangian**

```math
L(x, y) = c^\top x + y^\top (b - A x)
```

the objective plus each row's slack valued at its price. The best plan and the best prices form a
**saddle point** of $`L`$: the plan makes $`L`$ as large as it can, the prices make it as small as
they can, and neither can gain by moving alone. "First order" means that each step uses only the
**gradient** of $`L`$, its first derivatives, the direction in which $`L`$ changes fastest; it never
solves a system of equations. Both gradients are quantities you have met:

- the gradient in $`x`$ is $`c - A^\top y`$: each variable's reduced cost at prices $`y`$ (lesson
  2.3.3);
- the gradient in $`y`$ is $`b - A x`$: each row's slack at plan $`x`$ (lesson 2.1.2).

PDLP is built on the **primal-dual hybrid gradient** method (PDHG). One iteration takes two steps:

1. **Primal step.** Move $`x`$ a step of size $`\tau`$ up its gradient, then clip each variable
   back into its bounds: a variable whose value is more than the prices of what it uses grows, one
   worth less shrinks.
2. **Dual step.** Move $`y`$ a step of size $`\sigma`$ down its gradient, at the point
   $`2x_\text{new} - x_\text{old}`$ (a look ahead; without it the pair can circle the saddle point
   instead of closing in on it), then clip
   each price at 0: a broken row ($`Ax > b`$) gets a higher price, a row with room a lower one.

A bare version of that step, in plain Python, on a 2-variable LP whose optimum is 11 at
$`(3, 1)`$ with prices $`(2, 0, 1)`$:

```python
    x_new = [max(0.0, xj + TAU * (cj - aj)) for xj, cj, aj in zip(x, c, ATy)]
    Ax_bar = times(A, [2 * n - o for n, o in zip(x_new, x)])
    y = [max(0.0, yi - SIGMA * (bi - ai)) for yi, bi, ai in zip(y, b, Ax_bar)]
```

```text
 iter       x1       x2       y1       y2       y3  broken rows  uncovered        gap
    0   0.0000   0.0000   0.0000   0.0000   0.0000     0.00e+00   3.00e+00   0.00e+00
    1   0.7500   0.5000   0.0000   0.0000   0.0000     0.00e+00   3.00e+00   3.25e+00
    2   1.5000   1.0000   0.0000   0.0000   0.0000     0.00e+00   3.00e+00   6.50e+00
    5   3.2109   1.3281   0.6758   0.7852   0.2461     5.39e-01   1.29e+00   3.35e+00
   10   4.1049   0.7940   1.7480   0.0269   1.6085     1.10e+00   1.71e-01   1.90e+00
   20   2.5333   1.2581   1.4098   0.0000   1.3541     0.00e+00   5.90e-01   4.15e-01
   50   3.1144   0.8360   2.0124   0.0000   1.0389     1.14e-01   0.00e+00   1.51e-01
  100   3.0065   0.9888   1.9425   0.0000   1.0927     6.52e-03   5.75e-02   5.11e-02
  200   2.9947   1.0086   2.0169   0.0000   0.9726     3.27e-03   1.05e-02   1.57e-02
  957   3.0000   1.0000   2.0000   0.0000   1.0000     8.72e-07   9.33e-07   4.64e-07
```

Plan and prices find each other together. At iteration 10 the plan overshoots: $`x_1 = 4.1`$
breaks the row $`x_1 \le 3`$ by 1.1, and that row's price $`y_3`$ has risen from 0.25 at iteration
5 to 1.61. By iteration 20 the plan has pulled back to $`x_1 = 2.53`$, nothing is broken, and the
prices have fallen below covering the objective again (uncovered 0.59). The swings shrink until all
three measures are below $`10^{-6}`$, at iteration 957. Each iteration
did one product with $`A^\top`$ and one with $`A`$, and nothing else expensive.

That is the whole cost of an iteration in PDLP too: a pass over the constraint matrix and its
transpose, and no factorization, so it needs no more memory than the matrix itself and can take on
LPs too big to factor. The bare step needed 957 iterations even on 2 variables; PDLP adds to it a
rescaling of rows and columns, presolve, step sizes that adapt as it goes, and restarts from an
average of recent points (the paper behind PDLP describes each); with all of them it took 256
iterations on the 410-variable funding LP.
The price is still many iterations and a looser answer: PDLP stops as soon as three measures are
below its tolerance ($`10^{-6}`$ relative by default): how much the rows are broken, how far the
prices are from covering the objective, and the gap between the primal and dual objectives.

In one sentence, for an interview: PDLP treats the LP and its dual as one saddle-point problem and
alternates cheap gradient steps on the plan and on the prices, each a matrix-vector product
followed by a clip to the bounds, until both are feasible and their objectives agree within a
tolerance.

That is what the table shows: PDLP's objective, 234898.1297, differs from the simplex value
234898.1206 by 0.009, about 4 parts in 100 million. Both are `OPTIMAL`; each is optimal within its
solver's tolerance. PDLP's value is even *above* the true maximum, which no allowed point can be:
its point breaks some rows by a sliver, within tolerance. On the large portfolio below its value
lands below the maximum instead. Which side PDLP lands on is not fixed. PDLP also has no crossover, so its point need not be a vertex. On the large
portfolio below it ends with 14 variables in between, more than a vertex can have.

The OR-Tools guide to LP solving puts the trade this way: first-order methods scale to larger
problems with less memory, but are more sensitive to numbers and can struggle to reach high
accuracy. The HiGHS documentation adds that on a CPU its own PDLP implementations are unlikely to
compete with its simplex or interior point solvers; they are built for GPUs. So the order of choice
for a model GridCap's size is: simplex first, barrier when simplex is slow, PDLP when the LP is
too large for either.

## Each Solver Accepts Only Its Own Algorithms

`lp_algorithm` is a request, and a solver that lacks the algorithm refuses the solve. The full
grid, on the small portfolio:

```python
def try_algorithm(solver: mathopt.SolverType, algorithm: mathopt.LPAlgorithm) -> str:
    try:
        result = mathopt.solve(lp.model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
    except Exception as error:          # OR-Tools 9.15 reports the refusal as this AttributeError
        return f"refused ({type(error).__name__})"
    return result.termination.reason.name
```

```text
                GLOP                      HIGHS                     PDLP
PRIMAL_SIMPLEX  OPTIMAL                   OPTIMAL                   refused (AttributeError)
DUAL_SIMPLEX    OPTIMAL                   OPTIMAL                   refused (AttributeError)
BARRIER         refused (AttributeError)  OPTIMAL                   refused (AttributeError)
FIRST_ORDER     refused (AttributeError)  refused (AttributeError)  OPTIMAL
GLOP with BARRIER: AttributeError: 'StatusNotOk' object has no attribute 'canonical_code'
```

GLOP is simplex only, PDLP is first order only, and HiGHS (as OR-Tools 9.15 drives it) offers
both simplex forms and barrier. The refusal arrives as an exception, never as a status. Its message
is not the solver's reason: in OR-Tools 9.15 the Python wrapper fails while building the real error
and raises this `AttributeError` instead. So a program that tries an algorithm catches the
exception around the solve call, and records the refusal rather than retrying with the default,
which would label a simplex result "barrier".

<!-- practice 1 -->

## Same Model, Three Solvers: Compare Objectives With a Relative Tolerance

Switching solver is one argument in MathOpt, so the cheapest test of a model, or of a solver
upgrade, is to solve it on several and compare. On the large portfolio, each with its default
algorithm:

```python
def relative_gap(a: float, b: float) -> float:
    """|a - b| measured against the larger magnitude, never against less than 1."""
    return abs(a - b) / max(1.0, abs(a), abs(b))


for a, b in (("GLOP", "HIGHS"), ("GLOP", "PDLP")):
    gap = relative_gap(objective[a], objective[b])
    print(f"{a} vs {b}: equal? {objective[a] == objective[b]}  difference {abs(objective[a] - objective[b]):.6f}"
          f"  relative {gap:.1e}  within 1e-6? {gap <= 1e-6}")
```

```text
funding LP on large: 10000 projects, 871 must-do, 10 years
GLOP  objective 6,052,813.4253  in-between 10
HIGHS objective 6,052,813.4253  in-between 10
PDLP  objective 6,052,811.5985  in-between 14
GLOP vs HIGHS: equal? True  difference 0.000000  relative 0.0e+00  within 1e-6? True
GLOP vs PDLP: equal? False  difference 1.826815  relative 3.0e-07  within 1e-6? True
```

Three things to read from it.

- **`==` is the wrong test.** PDLP's objective is $1.8k below the simplex value, and both are
  correct answers within their tolerances. A test that asserts equality fails on a correct model.
  The two simplex solvers happen to agree to the last digit here; that is not something to rely on
  either, since two exact methods may stop on different optimal vertices and add their numbers in
  a different order.
- **The tolerance is relative.** A difference of 1.8 on six million is $`3 \times 10^{-7}`$; the
  same 1.8 on an objective of 50 would be a real disagreement. So the gap is divided by the size
  of the values. Dividing by at least 1 keeps two objectives near zero (say 0 and $`10^{-9}`$) from
  producing a huge "relative" gap out of noise. $`10^{-6}`$ is a common choice because LP solvers'
  default tolerances are around $`10^{-6}`$ to $`10^{-8}`$.
- **Rounding is not a fix.** 6,052,813.4 and 6,052,811.6 round to different whole numbers, and
  any two values on either side of a rounding boundary differ after rounding, however close they
  are.

A comparison also starts from the status: a solver that ended without `OPTIMAL` has no objective
to compare, and that is a disagreement, not a value to skip.

<!-- practice 2 -->

## Summary

- **Simplex walks from vertex to vertex and ends on one.** Primal simplex keeps the rows satisfied,
  dual simplex keeps optimality; both stop on a vertex, with at most one in-between variable per row.
- **Interior point crosses the inside in a few expensive steps.** It follows the central path, where
  every complementary slackness product equals $`\mu`$, with one Newton system per iteration while
  $`\mu`$ falls; it stops just off the bounds, and crossover then moves its answer to a vertex.
- **PDLP takes many cheap steps and stops within a tolerance.** Gradient steps on the Lagrangian,
  up for the plan and down for the prices, each a matrix-vector product and a clip; so it fits LPs
  too large to factor, and its answer is less exact and need not be a vertex.
- **GLOP's default is primal simplex; HiGHS's is dual simplex.**
- **Each solver accepts only its own algorithms.** GLOP: simplex; HiGHS: simplex and barrier; PDLP:
  first order. A refusal is an exception.
- **Compare objectives with a relative tolerance.** Never with `==`, and never by rounding.

## Reference

| Algorithm | Moves | Iteration cost | Iterations here (medium) | Ends on a vertex | In OR-Tools (MathOpt) |
| --- | --- | --- | --- | --- | --- |
| primal simplex | vertex to vertex, rows kept satisfied | small (one pivot) | 191 (GLOP) | yes | GLOP (its default), HiGHS |
| dual simplex | vertex to vertex, optimality kept | small (one pivot) | 14 (GLOP, HiGHS) | yes | GLOP, HiGHS (its default) |
| barrier (interior point) | along the central path, inside | large (one Newton system) | 10 (HiGHS) | after crossover | HiGHS |
| first order (PDLP) | gradient steps on plan and prices together | matrix-vector products | 256 (PDLP) | no | PDLP |

| Call | Meaning |
| --- | --- |
| `mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX)` | ask for one algorithm |
| `result.solve_stats.simplex_iterations` / `barrier_iterations` / `first_order_iterations` | the work each kind did |
| `abs(a - b) / max(1, abs(a), abs(b)) <= 1e-6` | two objectives agree |

**Further reading:** [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (the three families of LP algorithm, vertices and crossover, tolerances, and a guide to choosing: GLOP first, barrier next, PDLP for the largest problems); [PDLP (OR-Tools)](https://developers.google.com/optimization/lp/pdlp_math) (the mathematics behind PDLP: a primal-dual hybrid gradient method with diagonal rescaling, and the residuals it reports); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt drives, GLOP, PDLP and HiGHS among them); [Solving an LP Problem (OR-Tools)](https://developers.google.com/optimization/lp/lp_example) (switching an LP from GLOP to PDLP is a change of solver name); [GLOP `parameters.proto`](https://github.com/google/or-tools/blob/stable/ortools/glop/parameters.proto) (`use_dual_simplex`, false by default: GLOP runs primal simplex unless asked); [PDLP `solvers.proto`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/solvers.proto) (PDLP's parameters: the default tolerance of $`10^{-6}`$ on primal residual, dual residual and gap, restarts, adaptive step sizes, rescaling); [Applegate et al., Practical Large-Scale Linear Programming using Primal-Dual Hybrid Gradient](https://arxiv.org/abs/2106.04756) (the paper behind PDLP: PDHG on the saddle-point form of an LP, with preconditioning, presolve, adaptive step sizes and restarts); [HiGHS, Solvers](https://ergo-code.github.io/HiGHS/dev/solvers/) (dual simplex as its default, its interior point solvers, crossover after interior point and when it can be switched off, and its PDLP, built for GPUs); [Interior-point method (Wikipedia)](https://en.wikipedia.org/wiki/Interior-point_method) (the logarithmic barrier, the central path and the Newton step of a primal-dual method).

## Challenges

1. The large LP has 10 cash rows and 871 must rows. Before running anything, what is the most
   variables a simplex answer can have in between? Check it against the output above.
2. GLOP's primal simplex took 191 pivots and its dual simplex 14 on the medium LP. Would you expect
   the same ratio on another LP? What would you run to find out?
3. A colleague proposes asserting `round(glop, 2) == round(pdlp, 2)` in CI. Give two objective
   values that are within $`10^{-9}`$ relative and still fail it.

## Design Note: Keep the Solver an Argument

Every program here builds the model once and passes the solver as an argument. That costs nothing
and buys the cheapest test there is: solve on two solvers and compare. A model that only one solver
can run has no second opinion.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**funding_lp.py.** The funding LP of *The Model*, and the `in_between` count. It prints nothing; the
other programs import it.

- Library: [funding_lp.py](src/funding_lp.py)

**three_algorithms.py.** The medium LP solved five ways, with each run's iterations and in-between
count (*Simplex*, *Interior Point*, *PDLP*). *Try:* Add a run of HiGHS with `PRIMAL_SIMPLEX`.
Predict its objective and in-between count before you run it.

- Program: [three_algorithms.py](src/three_algorithms.py)

**barrier_crossover.py.** HiGHS's interior point log on the medium LP, then the same LP solved by
interior point with crossover off and on, counting the variables strictly inside their bounds
(*Interior Point*). *Try:* Turn `presolve` back on in `solve_ipm`. Predict whether the
crossover-off count above 0 stays at 410.

- Program: [barrier_crossover.py](src/barrier_crossover.py)

**pdhg_sketch.py.** The bare primal-dual hybrid gradient step that PDLP builds on, on a 2-variable
LP (*PDLP*). *Try:* Halve `TAU` and `SIGMA`. Predict whether it needs more or fewer iterations
than 957.

- Program: [pdhg_sketch.py](src/pdhg_sketch.py)

**refused_algorithms.py.** Every solver against every algorithm, and the exception a refusal raises
(*Each Solver Accepts Only Its Own Algorithms*). *Try:* Print `type(error).__mro__` for the
refusal. Which classes would an `except` clause have to name?

- Program: [refused_algorithms.py](src/refused_algorithms.py)

**compare_objectives.py.** The large LP on GLOP, HiGHS and PDLP, compared with a relative gap
(*Same Model, Three Solvers*). *Try:* Pass `mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.BARRIER)`
to the HiGHS solve. Predict whether it still matches GLOP within $`10^{-6}`$.

- Program: [compare_objectives.py](src/compare_objectives.py)
