# 6.6.1 Convex Piecewise Costs Without Binaries

GridCap's treasury offers the small portfolio's planners a credit line. The plan may spend past
its $38,390k capital budget by drawing on it, and each $k drawn costs money: the first $1,500k at
0.10 per $k (the present value of the interest and fees), the next $1,500k at 0.25, and the last
$2,000k at 0.45. Nothing above $5,000k may be drawn. Is it worth drawing, and how much? The cost of
the loan is not one line through the origin: it bends at $1,500k and again at $3,000k. This lesson
writes that bent cost into the selection model with no new binary variables, and shows exactly when
that is allowed, in four rules.

GridCap is a fictional utility's portfolio, generated for this course; the credit line is invented
for this lesson.

## A Piecewise-Linear Function Is Its Breakpoints

Add up the tiers to get the total cost $`f(b)`$ of drawing $`b`$ thousand dollars:

| Drawn $`b`$ ($k) | 0 | 1,500 | 3,000 | 5,000 |
| --- | --- | --- | --- | --- |
| Total cost $`f(b)`$ ($k) | 0 | 150 | 525 | 1,425 |

Between two neighbouring columns the cost grows at the tier's rate, so $`f`$ is made of straight
pieces joined at the columns. Such a function is **piecewise linear**. The columns are its
**breakpoints** $`(X_0, F_0), (X_1, F_1), \dots, (X_K, F_K)`$ with $`X_0 < X_1 < \dots < X_K`$, and the
$`K`$ straight pieces between them are its **segments**. The slope of segment $`k`$ (numbered from 1) is

```math
s_k = \frac{F_k - F_{k-1}}{X_k - X_{k-1}}
```

here 0.10, 0.25 and 0.45, the three rates. Between $`X_{k-1}`$ and $`X_k`$ the function is
$`f(b) = F_{k-1} + s_k\,(b - X_{k-1})`$. So the list of breakpoints says everything about $`f`$, and
the programs of this module store a curve as exactly that: two tuples, `xs` and `ys`.

A MILP cannot contain $`f(b)`$ itself: "if $`b \le 1500`$ use this line, otherwise that one" is not a
linear expression in $`b`$. The question of this module is how to say $`y = f(b)`$ with linear rows,
and this lesson's answer is that for some curves it costs nothing at all.

A function is **convex** when its slopes never decrease from left to right: each segment is at least
as steep as the one before. The credit line is convex (0.10, then 0.25, then 0.45), as is every cost
that gets dearer per unit the more you buy; MIT's *Applied Mathematical Programming* (chapter 9)
calls this case diseconomies of scale. A function whose slopes never increase is **concave**: each
unit is cheaper, or worth less, than the one before. A straight line is both.

## A Convex Cost Can Be Split Into Segments the Solver Fills in Order

Give each tier its own continuous variable: $`\delta_k`$, the amount drawn from tier $`k`$, between 0
and the tier's width $`X_k - X_{k-1}`$. Then

```math
b = X_0 + \sum_{k=1}^{K} \delta_k, \qquad \text{cost} = F_0 + \sum_{k=1}^{K} s_k\, \delta_k, \qquad 0 \le \delta_k \le X_k - X_{k-1}
```

This is a linear model. It describes the credit line correctly only if the tiers are used in order:
tier 2 only once tier 1 is full. Nothing in the rows says so. A plan with $`\delta_1 = 0`$ and
$`\delta_2 = 1{,}000`$ is allowed by the rows and charged at 0.25 per $k, which no tier of the real
line does for the first $1,000k drawn.

The order holds anyway, because of where the cost sits. The objective subtracts the cost, so the
solver wants it as small as possible for whatever it draws. To draw $`b`$, it takes the cheapest
$k first: all of tier 1 at 0.10 before any of tier 2 at 0.25. Filling in order is exactly what the
real line charges, so the cheapest way the rows allow is the true cost.

The module's library writes these rows for any curve:

```python
s = curve.slopes()
delta = [model.add_variable(lb=0, ub=curve.xs[k + 1] - curve.xs[k], name=f"{name}_d{k}")
         for k in range(len(s))]
x = curve.xs[0] + sum(delta)
y = curve.ys[0] + sum(s[k] * delta[k] for k in range(len(s)))
```

(Python numbers the segments from 0, so `delta[k]` is $`\delta_{k+1}`$.) The selection model of lesson
1.1.1, built in MathOpt (OR-Tools' modeling layer, introduced in lesson 1.1.3), takes the curve in two
places: the budget row gains the amount drawn, and the objective loses its cost.

```python
loan = form(model, curve, "loan")
model.delete_linear_constraint(sel.budget)
spend = sum(p.capex * sel.x[p.project_id] for p in portfolio.projects)
model.add_linear_constraint(spend <= portfolio.capital_budget + loan.x, name="budget")
model.maximize(sum(p.value * sel.x[p.project_id] for p in portfolio.projects) - loan.y)
```

HiGHS solves it without the credit line, then with it:

```text
no credit line: objective $25,336k, 20 projects
rising tiers, slopes [0.1, 0.25, 0.45]
rising, as segments: objective $26,686k, 24 projects, drawn $3,600k
    tiers used ($k): [1500, 1500, 600]
    cost charged by the model $795k, real cost $795k, plan really worth $26,686k
    40 integer variables, 3 continuous
```

The plan draws $3,600k, funds 4 more projects and is worth $1,350k more after the loan's cost. The
tiers are used in order (1,500, then 1,500, then 600 of the last tier's 2,000), and the cost the
model charged, $795k, is the real one: $`0.10 \times 1500 + 0.25 \times 1500 + 0.45 \times 600`$.
The model still has its 40 project binaries and nothing more: the curve added three continuous
variables and no integer one, so the branch-and-bound search of section 3 still branches only on
the project binaries.

## The Same Cost Is the Largest of Its Lines

There is a second way to write a convex cost, with one variable instead of one per tier. Extend each
segment into a whole straight line: line $`k`$ is $`F_{k-1} + s_k\,(b - X_{k-1})`$. For a convex
function, every line lies on or below the curve, and at each $`b`$ the line of the segment that
contains $`b`$ touches it. So the curve is the **largest** of its lines:

```math
f(b) = \max_{k = 1, \dots, K} \big( F_{k-1} + s_k\,(b - X_{k-1}) \big) \qquad \text{for convex } f
```

A maximum of linear terms is easy to bound from below: "$`y`$ is at least the largest line" is the
same as "$`y`$ is at least every line", one row per segment.

```math
y \ge F_{k-1} + s_k\,(b - X_{k-1}) \qquad k = 1, \dots, K
```

These rows allow every $`y \ge f(b)`$. As before, the objective decides the rest: it subtracts $`y`$,
so the solver lowers $`y`$ until a row stops it, and the row that stops it is the largest line,
$`f(b)`$. The region above a function's graph is called its **epigraph**, so this is the epigraph form:

```python
x = model.add_variable(lb=curve.xs[0], ub=curve.xs[-1], name=f"{name}_x")
y = model.add_variable(lb=-math.inf, name=f"{name}_y")
for k, slope in enumerate(curve.slopes()):
    model.add_linear_constraint(y >= curve.ys[k] + slope * (x - curve.xs[k]), name=f"{name}_line{k}")
```

The bounds on $`x`$ carry the domain: nothing below $`X_0`$, nothing above $`X_K = 5{,}000`$. Without
the upper bound the last line would happily price a $9,000k draw that the treasury never offered.
Solved:

```text
rising, as lines   : objective $26,686k, 24 projects, drawn $3,600k
    cost charged by the model $795k, real cost $795k, plan really worth $26,686k
    40 integer variables, 2 continuous
```

The same plan and the same $795k, with two continuous variables and three rows. The segment form
uses one variable per segment and no extra rows (the widths are bounds); the epigraph form uses
two variables and one row per segment. Both are exact for a convex cost the solver wants small, and
neither needs a binary.

The cost does not have to sit in the objective. In a row such as
$`\text{spend} + y \le B`$, a larger $`y`$ only makes the row harder to meet, so any plan the rows
allow with some $`y \ge f(b)`$ is also allowed with $`y = f(b)`$: the row sees the true cost. What
matters is the direction in which the rest of the model presses on $`y`$, which is the next rule.

<!-- practice 1 -->

## Without Binaries, the Push Must Match the Shape

Now the treasury proposes the opposite schedule: the first $1,500k at 0.45 per $k, the next $1,500k
at 0.25 and the last $2,000k at 0.10, as a lender does that charges a large arrangement fee and then
little. The slopes fall, so this cost is concave. Solved with the same segment rows:

```text
falling tiers, slopes [0.45, 0.25, 0.1]
falling, as segments: objective $26,861k, 24 projects, drawn $3,600k
    tiers used ($k): [100, 1500, 2000]
    cost charged by the model $620k, real cost $1,110k, plan really worth $26,371k
    40 integer variables, 3 continuous
```

The solver drew $2,000k from the last tier and $1,500k from the middle one, and only $100k from the
first, the dear one. The real line would have charged the first $1,500k at 0.45, so the plan's true
cost is $1,110k, and the model charged $620k. It claims $26,861k for a plan really worth $26,371k.
The cheapest way the rows allow is no longer the true cost, because filling the cheap tiers first
now breaks the order.

Whether the rows are exact depends on two things together: the curve's shape, and which way the
model pushes $`y`$. The program fixes $`b`$ at four values, lets the solver move $`y`$ down (as a cost
in a maximization, or in a $`\le`$ row, does) or up (as a value in a maximization does), and compares
the result with $`f(b)`$:

```text
curve    shape    y is pushed | x =  1000   2000   3500   4500 | exact?
rising   convex   f(x)        |        100    275    750   1200
                  down        |        100    275    750   1200 | yes
                  up          |        450    900   1275   1375 | no
falling  concave  f(x)        |        450    800   1100   1200
                  down        |        100    200    575   1025 | no
                  up          |        450    800   1100   1200 | yes
```

- **A convex curve pushed down is exact**: the cheap segments come first, so filling them first is
  the true order. This is a convex cost being minimized, or kept within a budget.
- **A concave curve pushed up is exact** for the mirror reason: the most valuable segments come
  first. This is a concave value being maximized, such as a benefit with diminishing returns.
- **The other two are wrong.** A concave cost pushed down (economies of scale) and a convex value
  pushed up (increasing returns) both reward skipping to a later segment, and the rows cannot stop it.

For the epigraph form, the mirror of a convex cost is a concave value written as the smallest of its
lines: $`y \le`$ every line, which is exact when $`y`$ is pushed up.

So before writing a curve without binaries, check two things: the slopes (rising or falling) and the
push (is the solver trying to make $`y`$ smaller or larger?). When they match, the curve is free. When
they do not, the solver must be told which segment it is on, and that takes binaries: lesson 6.6.2.

Two warnings about the push. First, it must be the same everywhere $`y`$ appears: a cost that is
subtracted in the objective and also limited in a budget row is pushed down in both places, which is
fine, but a quantity that is a cost in one row and a reward in another is pushed both ways and
needs the exact forms of lesson 6.6.2. Second, an equality row ($`y = \dots`$ pinned to something else)
pushes both ways too.

<!-- practice 2 -->

## The Model

The selection model of lesson 1.1.1 on GridCap small with the credit line in segment form, marked.
`credit_line.py` solves it with the rising tiers (exact) and with the falling tiers (not exact, as
the last rule showed).

**Sets.** $`P`$ the candidate projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$ the child
projects, with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups, each a set of projects;
$`k = 1, \dots, K`$ the credit line's tiers ($`K = 3`$). ← this lesson

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$, project $`i`$'s cost and value ($k);
$`B = 38{,}390`$, the capital budget ($k); $`X_0 = 0 < X_1 < \dots < X_K`$, the credit line's
breakpoints ($k drawn: 0, 1,500, 3,000, 5,000); $`s_k`$, tier $`k`$'s cost per $k drawn (0.10, 0.25,
0.45). ← this lesson

**Variables.**

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(1 if project } i \text{ is funded)} \\
& 0 \le \delta_k \le X_k - X_{k-1} && \forall k = 1, \dots, K && \text{(\$k drawn from tier } k\text{)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i - \sum_{k=1}^{K} s_k\, \delta_k
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B + \sum_{k=1}^{K} \delta_k && && \text{(budget)} \quad \leftarrow \text{this lesson} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

The model is exact because $`s_1 \le s_2 \le s_3`$ and the objective subtracts the cost. The epigraph
version replaces the $`\delta_k`$ by $`0 \le b \le X_K`$ and a cost variable $`y`$, with rows
$`y \ge F_{k-1} + s_k(b - X_{k-1})`$ for each $`k`$ (`loan_line0` to `loan_line2` in the code), the
budget row reading $`\le B + b`$ and the objective subtracting $`y`$.

## Summary

- **A piecewise-linear function is its breakpoints.** Between neighbouring breakpoints it is a
  straight segment; a convex function's slopes never decrease, a concave function's never increase.
- **A convex cost can be split into segments the solver fills in order.** One bounded variable per
  segment; the solver takes the cheap segments first, which is the true order. On GridCap small the
  credit line added $1,350k of value with no new binary.
- **The same cost is the largest of its lines.** One row per segment, $`y \ge`$ each line, and $`y`$
  pushed down lands on the curve.
- **Without binaries, the push must match the shape.** Convex pushed down and concave pushed up are
  exact; the other two let the solver skip segments, as the falling tiers did ($620k charged, $1,110k
  real).

## Reference

| Curve | Pushed | Without binaries | Rows |
| --- | --- | --- | --- |
| convex (slopes rise) | down: a cost minimized or kept within a $`\le`$ row | exact | segments $`0 \le \delta_k \le X_k - X_{k-1}`$, or $`y \ge`$ each line |
| concave (slopes fall) | up: a value maximized, or kept above a $`\ge`$ row | exact | segments, or $`y \le`$ each line |
| convex | up | wrong: skips to the steep segment | binaries (lesson 6.6.2) |
| concave | down | wrong: skips to the cheap segment | binaries (lesson 6.6.2) |
| any | both ways (equality, or used as cost and reward) | wrong | binaries (lesson 6.6.2) |

| Term | Meaning |
| --- | --- |
| breakpoint | a point $`(X_k, F_k)`$ where the function may change slope |
| segment | the straight piece between two neighbouring breakpoints, slope $`s_k`$ |
| convex / concave | slopes never decrease / never increase from left to right |
| epigraph | the region on or above a function's graph; for a convex $`f`$, the points with $`y \ge`$ every line |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the modeling layer used here, which takes linear and quadratic objectives); [MathOpt `Model` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`add_variable`, `add_linear_constraint` and `delete_linear_constraint`); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2, "Representing Nonlinear Functions": piecewise-linear costs as segment variables, and diseconomies of scale, which need no integer variables in a minimization).

## Challenges

1. Add a fourth tier, $1,000k at 0.30 per $k, after the $0.45 tier. Is the curve still convex? Predict
   what the segment model draws from it, then run it.
2. Write the credit line's cost as $`y \ge`$ each line, but forget the upper bound of 5,000 on $`b`$.
   What does the model allow that the treasury does not?
3. A benefit grows by 30 per unit for the first 10 units, then 20, then 5. In which objective sense and
   which kind of row can it be written without binaries?

## Design Note: Check the Shape in Code, Not by Eye

A curve that arrives as data (a tariff, a contract, a fitted curve) can change shape when someone
edits one breakpoint. The library's `Curve` has `convex()` and `concave()`; a model builder that
writes the cheap form should assert the shape it relies on, and fall back to the forms of lesson
6.6.2 (or refuse) when the check fails, rather than return a plan that claims value it does not
have. The falling-tier run above passed every solver check: optimal, feasible, no warning. Only the
shape check catches it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**credit_line.py.** Solves GridCap small with no credit line, with the rising tiers as segments and as
lines, and with the falling tiers as segments (*A Convex Cost Can Be Split Into Segments*, *The Same
Cost Is the Largest of Its Lines*, *Without Binaries, the Push Must Match the Shape*). *Try:* Raise
the first tier's rate from 0.10 to 0.30. Predict how much the plan draws.

- Program: [credit_line.py](src/credit_line.py)

**direction_table.py.** Fixes the amount drawn and lets the solver push the cost down or up, for both
schedules (*Without Binaries, the Push Must Match the Shape*). *Try:* Add the point 0 to `POINTS`.
Predict whether any row of the table changes there.

- Program: [direction_table.py](src/direction_table.py)

**piecewise.py.** The curve and every formulation of this module (`add_segments`, `add_epigraph` here).

- Library: [piecewise.py](src/piecewise.py)

**selection.py.** The one-period selection model of lesson 1.1.1 and the HiGHS helper.

- Library: [selection.py](src/selection.py)
