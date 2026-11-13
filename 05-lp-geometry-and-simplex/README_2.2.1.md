# 2.2.1 Solving a 2-Variable LP by Picture

GridCap's maintenance planner has $3.0M left for next year and two programs that want it:
distribution work (transformers, poles, breakers) and transmission work (lines and towers). Each
$100k of distribution work removes 5 points from GridCap's risk score; each $100k of transmission
work removes 4. Distribution is the better buy per dollar, so the obvious answer is "all of it to
distribution". That answer is wrong, because two more rules apply: crews are limited, and only so
much transmission work is designed and ready to start. (GridCap is the course's fictional utility;
these numbers describe no real company.)

With only two decisions, the whole problem fits on one sheet of graph paper. This lesson solves it
by drawing, in four rules. The picture is worth the trouble: every LP solver in this course,
including GLOP and HiGHS (the two that lesson 1.1.3 introduced), is doing a higher-dimensional version of what you will do here by eye.

## The Model

The planner's question, written as a linear program (LP: continuous variables, a linear objective,
linear constraints; lesson 1.1.3 introduced the term). Money is counted in units of $100k, so 30
means $3.0M.

**Sets.** The two programs, $`K = \{\text{distribution}, \text{transmission}\}`$. With only two, the
model names each variable directly instead of indexing by $`K`$.

**Parameters.**

| Symbol | Value | Meaning |
| --- | --- | --- |
| $`v_d, v_t`$ | 5, 4 | risk points removed per $100k of distribution, of transmission |
| $`B`$ | 30 | money available, in $100k |
| $`g_d, g_t`$ | 3, 2 | crew-weeks needed per $100k of distribution, of transmission |
| $`C`$ | 72 | crew-weeks available |
| $`R`$ | 20 | transmission work designed and ready, in $100k |

**Variables.** $`d \ge 0`$, the money given to distribution, and $`t \ge 0`$, the money given to
transmission, both in $100k and both continuous: $1,234,500 of distribution work is a fine answer.

**Objective.**

```math
\max \; 5d + 4t \qquad \text{(risk points removed)}
```

**Constraints.**

```math
\begin{aligned}
d + t &\le 30 && \text{(budget)} \\
3d + 2t &\le 72 && \text{(crews)} \\
t &\le 20 && \text{(ready\_t)} \\
d,\ t &\ge 0 && \text{(d\_nonneg, t\_nonneg)}
\end{aligned}
```

In code, every row is stored the same way, as two coefficients and a right-hand side that read
$`a_d\, d + a_t\, t \le b`$. A bound such as $`d \ge 0`$ is turned around to fit that shape:
$`-d \le 0`$.

```python
ROWS = {
    "budget": ((1, 1), 30),     # $3.0M in all
    "crews": ((3, 2), 72),      # 72 crew-weeks; $100k of distribution takes 3, of transmission 2
    "ready_t": ((0, 1), 20),    # only $2.0M of transmission work is designed and ready
}
BOUNDS = {
    "d_nonneg": ((-1, 0), 0),   # d >= 0, written as -d <= 0
    "t_nonneg": ((0, -1), 0),   # t >= 0
}
VALUE = (5, 4)                  # risk points removed per $100k of d and of t
```

The same rows become a MathOpt model (MathOpt is OR-Tools' modeling layer, met in lesson 1.1.3) with
one loop. A solver will confirm the answer at the end of
the lesson; until then, the picture does the work.

```python
def build(rows=ROWS, value=VALUE) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="budget-split")
    x = {name: model.add_variable(lb=0, name=name) for name in NAMES}
    for label, ((a_d, a_t), b) in rows.items():
        model.add_linear_constraint(a_d * x["d"] + a_t * x["t"] <= b, name=label)
    model.maximize(value[0] * x["d"] + value[1] * x["t"])
    return model, x
```

`add_variable(lb=0)` gives a continuous variable with lower bound 0 and no upper bound, which is
$`d \ge 0`$. So the two bounds are not added as rows here; the solver keeps them as variable bounds.

## Each Constraint Keeps One Side of a Line, and the Feasible Region Is Where All Sides Overlap

A **plan** is one choice of the two numbers $`(d, t)`$, so it is a point on a sheet of paper with
$`d`$ across and $`t`$ up. A plan is **feasible** when it satisfies every constraint.

Take one constraint, crews: $`3d + 2t \le 72`$. The points where $`3d + 2t = 72`$ exactly form a
straight line, through $`(24, 0)`$ and $`(0, 36)`$. That line splits the sheet in two. On one side,
$`3d + 2t`$ is less than 72 (the origin is there: $`3 \cdot 0 + 2 \cdot 0 = 0`$); on the other side
it is more. The constraint keeps the first side and the line itself. A set of that shape, a line and
everything on one side of it, is called a **half-plane**. Every linear inequality in two variables
is one.

To test a plan against a row, put its numbers into the left side and compare with the right:

```python
def broken(d: float, t: float, rows=ALL) -> list[str]:
    """The labels of the rows a plan (d, t) breaks; an empty list means the plan is feasible."""
    return [label for label, ((a_d, a_t), b) in rows.items() if a_d * d + a_t * t > b + 1e-9]
```

The `1e-9` is a tolerance: a plan that meets a row exactly, but whose float arithmetic lands a hair
above $`b`$, still counts as meeting it. Five plans, tested:

```text
plan d=10, t=10: feasible
plan d=20, t=10: breaks crews
plan d= 5, t=25: breaks ready_t
plan d=16, t=16: breaks budget, crews
plan d=12, t=18: feasible
```

Spending $2.0M on distribution and $1.0M on transmission fits the budget exactly, but needs
$`3 \cdot 20 + 2 \cdot 10 = 80`$ crew-weeks, eight more than GridCap has.

The **feasible region** is the set of all feasible plans: the points that lie in every half-plane
at once. Testing every point of a grid and printing `#` for feasible and `.` for not draws it. Each
character is one grid point: $`d`$ goes up by 1 ($100k) per column, $`t`$ by 2 per row. The letters
mark the five corners, which the next section finds exactly:

```text
t=22 ...............................
t=20 E#########D....................
t=18 ############C..................
t=16 ##############.................
t=14 ###############................
t=12 #################..............
t=10 ##################.............
t= 8 ###################............
t= 6 #####################..........
t= 4 ######################.........
t= 2 #######################........
t= 0 A#######################B......
     d=0       d=10      d=20      d=30
```

Read the boundary from the top left. Along the top, from E to D, the region stops at $`t = 20`$:
that is ready_t. From D to C the edge is the budget line $`d + t = 30`$, and from C down to B it is
the steeper crews line $`3d + 2t = 72`$. The left edge is $`d = 0`$ and the bottom edge $`t = 0`$.
The program `draw_region.py` draws the same region with matplotlib, with each boundary line labelled.

Two facts about this region hold for every LP, in any number of variables:

- **It has straight edges.** Each edge is part of one constraint's line. In three variables the
  lines become flat planes and the region is a solid with flat faces; in $`n`$ variables it is
  called a **polyhedron**, and a polyhedron that does not run off to infinity is a **polytope**.
- **It is convex.** A set is **convex** when the straight segment between any two of its points
  stays inside it. Each half-plane is convex, and points that lie in every one of several convex
  sets form a convex set too, so the region has no dents or holes. Lesson 1.2.3 treats convexity in general; here it is all you need.

## A Vertex Is Where Two Boundary Lines Cross Inside the Region

A **vertex** (a corner) of the region is a feasible point where two boundary lines cross. Lesson
1.2.3 calls the same points **extreme points**: points of the region that are not in the middle of
any segment between two other points of it. In two variables a corner needs two lines because one
line fixes only one direction; the second pins the point down.

Two lines $`a_1 d + b_1 t = r_1`$ and $`a_2 d + b_2 t = r_2`$ meet at one point unless they are
parallel. Solving the pair by hand (eliminate one variable, then the other) gives **Cramer's rule**:

```math
\Delta = a_1 b_2 - a_2 b_1, \qquad d = \frac{r_1 b_2 - r_2 b_1}{\Delta}, \qquad t = \frac{a_1 r_2 - a_2 r_1}{\Delta}
```

When $`\Delta = 0`$ the lines have the same slope: they never meet, or they are the same line.
In code:

```python
def crossing(row1, row2):
    """Where the lines a.x = b of two rows meet (Cramer's rule), or None when they are parallel."""
    (a1, b1), r1 = row1
    (a2, b2), r2 = row2
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        return None
    return ((r1 * b2 - r2 * b1) / det, (a1 * r2 - a2 * r1) / det)
```

For budget and crews: $`\Delta = 1 \cdot 2 - 3 \cdot 1 = -1`$,
$`d = (30 \cdot 2 - 72 \cdot 1)/(-1) = 12`$ and $`t = (1 \cdot 72 - 3 \cdot 30)/(-1) = 18`$.

A crossing is a vertex only if it is feasible: two lines can cross somewhere every plan is
forbidden. The model has five rows (three constraints and two bounds), so there are ten pairs. Every
pair, checked:

```text
  budget x crews    (12, 18) VERTEX
  budget x ready_t  (10, 20) VERTEX
  budget x d_nonneg (0, 30) outside: breaks ready_t
  budget x t_nonneg (30, 0) outside: breaks crews
   crews x ready_t  (10.6667, 20) outside: breaks budget
   crews x d_nonneg (0, 36) outside: breaks budget, ready_t
   crews x t_nonneg (24, 0) VERTEX
 ready_t x d_nonneg (0, 20) VERTEX
 ready_t x t_nonneg parallel, never meet
d_nonneg x t_nonneg (0, 0) VERTEX
5 vertices: (12, 18), (10, 20), (24, 0), (0, 20), (0, 0)
```

Five of the ten crossings are corners of the region: A $`(0, 0)`$, B $`(24, 0)`$, C $`(12, 18)`$,
D $`(10, 20)`$ and E $`(0, 20)`$, the letters on the map. Four crossings fall outside: the budget
line meets $`d = 0`$ at $`t = 30`$, but only 20 of transmission is ready. One pair, $`t = 20`$ and
$`t = 0`$, is parallel. The function that keeps only the feasible crossings, and records which rows
are tight at each, is:

```python
def vertices(rows=ALL) -> dict[tuple[float, float], list[str]]:
    """Every feasible crossing point, with the rows tight there."""
    found = {}
    for (l1, row1), (l2, row2) in combinations(rows.items(), 2):
        point = crossing(row1, row2)
        if point is not None and not broken(*point, rows):
            point = (round(point[0], 9) + 0.0, round(point[1], 9) + 0.0)
            found.setdefault(point, [])
            found[point] += [label for label in (l1, l2) if label not in found[point]]
    return found
```

A row is **tight** (or **active**) at a plan when the plan meets it with equality: at C, the
budget is spent to the last dollar and every crew-week is used. A row that is not tight has
**slack**, an unused amount: at C, ready transmission work has $`20 - 18 = 2`$ ($200k) left over.
Rounding to 9 decimals merges the same corner reached through different pairs of lines (lesson
2.2.3 meets a corner where three lines cross), and `+ 0.0` turns a `-0.0` into `0.0`.

<!-- practice 1 -->

## The Objective's Level Lines Are Parallel, and the Best Plan Is the Last Point the Line Touches

The objective $`5d + 4t`$ gives every plan a value. The plans with one particular value, say 100,
satisfy $`5d + 4t = 100`$: that is again a straight line, called a **level line** (or iso-value
line) of the objective. Different values give parallel lines, because only the right-hand side
changes, never the slope. Raising the value slides the line away from the origin, in the direction
$`(5, 4)`$: the direction in which the objective grows fastest, made of its coefficients.

So the picture method is: draw one level line through the region, then slide it in the direction
$`(5, 4)`$, keeping it parallel, until one more nudge would leave the region. The last feasible
points it touches are the best plans.

The value at each vertex tells you where that happens:

```python
def touches(level: float, c=VALUE) -> str:
    """Whether the line c.x = level meets the region: it does when level lies between the vertices' values."""
    values = [value(p, c) for p in vertices()]
    if level > max(values) + 1e-9 or level < min(values) - 1e-9:
        return "misses the region"
    on = ", ".join(LETTER[p] for p in vertices() if abs(value(p, c) - level) < 1e-9)
    if abs(level - max(values)) < 1e-9:
        return f"touches the region only at {on}" if "," not in on else f"touches the region along {on}"
    return "crosses the region" + (f", through vertex {on}" if on else "")
```

Why the vertices settle whether a level line meets the region: the region is convex and has these
five corners, so a line misses it exactly when all five corners lie strictly on one side of the
line. The values, and five level lines:

```text
A (0, 0): 5d + 4t = 0
E (0, 20): 5d + 4t = 80
B (24, 0): 5d + 4t = 120
D (10, 20): 5d + 4t = 130
C (12, 18): 5d + 4t = 132
level 60: crosses the region
level 100: crosses the region
level 130: crosses the region, through vertex D
level 132: touches the region only at C
level 140: misses the region
```

At level 130 the line still cuts through the region: it passes through D, but plans beyond it, near
C, are worth more. At 132 the only feasible point left on the line is C. At 140 no plan reaches the
line at all. So the best plan is C: $1.2M to distribution and $1.8M to transmission, removing 132
risk points.

That settles the opening puzzle. "All to distribution" is vertex B, $`(24, 0)`$, and it is
stopped by crews before it spends the money: distribution needs 3 crew-weeks per $100k against
transmission's 2, so B spends only $2.4M and is worth 120. Moving from B toward C trades
distribution for transmission along the crews line. Each step gives up $100k of distribution and
buys $150k of transmission with the same crew-weeks, for a net gain of
$`-5 + 1.5 \cdot 4 = 1`$ point, until the budget runs out at C.

## If an LP Has a Best Plan, Some Vertex Is a Best Plan

The sliding line always comes to rest on a corner or along an edge between two corners; it cannot
come to rest on a point in the middle of the region, because from there it could slide further.
Stated as a rule: **if an LP has an optimal plan, then at least one vertex of its region is an
optimal plan.** (Its region needs at least one vertex for this; every region in this module has
one, and so does every nonempty region whose variables are all bounded below by 0.)

Why it is true in general, in any number of variables: every point of a bounded region is a
weighted average of its vertices, with nonnegative weights that add up to 1. A linear objective's
value at a weighted average is the same weighted average of the vertices' values, and an average
can never exceed the largest thing being averaged. So no point beats the best vertex.

Sometimes the best plan is not unique. Change the objective to $`4d + 4t`$, as if both programs
removed 4 points per $100k:

```text
objective 4d + 4t: best 120 at ['C', 'D']
level 120 of 4d + 4t: touches the region along C, D
```

Now the level lines are parallel to the budget line $`d + t = 30`$, and the line comes to rest along
the whole edge from D to C. Every plan on that edge, such as $`(11, 19)`$, is optimal with value 120.
The rule still holds: C and D are vertices, and both are optimal. An LP solver returns one optimal
plan; when there are several, which one it returns is up to the solver.

A solver agrees with the picture. GLOP, OR-Tools' LP solver, on the model built above:

```text
GLOP: OPTIMAL, d = 12, t = 18, value 132
```

The rule suggests an algorithm: list every vertex, compute its value, keep the best. That is what
this lesson did, and it works for two variables. It does not scale. With $`n`$ variables, a vertex
is a point where $`n`$ boundary rows are tight, so a model with $`n`$ variables and $`m`$
constraints (plus its $`n`$ bounds) has up to $`\binom{n+m}{n}`$ candidate crossings to solve and
test:

```text
2 variables, 3 rows: 10 ways to pick 2 tight rows
10 variables, 20 rows: 3e+07 ways to pick 10 tight rows
50 variables, 100 rows: 2.01e+40 ways to pick 50 tight rows
100 variables, 200 rows: 4.16e+81 ways to pick 100 tight rows
```

The first line is this lesson's ten pairs. GridCap's real models have thousands of variables. The
simplex method, in lesson 2.2.2, keeps the idea that the answer is a vertex but visits only a short
path of them, each one better than the last.

<!-- practice 2 -->

## Summary

- **Each constraint keeps one side of a line, and the feasible region is where all sides
  overlap.** The region of an LP is convex and has straight edges: a polygon in two variables, a
  polyhedron in general.
- **A vertex is where two boundary lines cross inside the region.** Solve the two rows as
  equations (Cramer's rule), then keep the crossing only if it breaks no row.
- **The objective's level lines are parallel, and the best plan is the last point the line
  touches** as it slides in the direction of the objective's coefficients.
- **If an LP has a best plan, some vertex is a best plan.** Several vertices can tie, and then the
  whole edge or face between them is optimal. Listing all vertices works for two variables and
  explodes beyond that.

## Reference

| Term | Meaning |
| --- | --- |
| feasible plan | a point that satisfies every constraint |
| feasible region | the set of all feasible plans; convex, with flat sides |
| half-plane | a line and everything on one side of it: the points of one inequality in two variables |
| vertex (extreme point) | a feasible point where $`n`$ boundary rows meet ($`n = 2`$ here) |
| tight (active) row | a row the plan meets with equality |
| slack | the unused amount of a row, $`b - a \cdot x \ge 0`$ |
| level line | the plans with one value of the objective, $`c \cdot x = \text{const}`$ |

| Vertex | $`(d, t)`$ | Tight rows | $`5d + 4t`$ |
| --- | --- | --- | --- |
| A | (0, 0) | d_nonneg, t_nonneg | 0 |
| B | (24, 0) | crews, t_nonneg | 120 |
| C | (12, 18) | budget, crews | 132 (optimal) |
| D | (10, 20) | budget, ready_t | 130 |
| E | (0, 20) | ready_t, d_nonneg | 80 |

**Further reading:** [Solving an LP Problem (OR-Tools)](https://developers.google.com/optimization/lp/lp_example) (a second two-variable LP solved by picture: the feasible region drawn, and the objective line slid to the corner where it last touches it); [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (why simplex solvers such as GLOP always return a vertex, and why that answer tends to be sparse); [MO-book 2.1, BIM production planning](https://mobook.github.io/MO-book/notebooks/02/01-bim.html) (a two-product LP whose optimum sits where two resource rows are tight, the shape of vertex C).

## Challenges

1. GridCap finds 4 more crew-weeks (76 instead of 72). Where do the crews line and vertex C move?
   Recompute C with Cramer's rule, then check with `vertices.py`.
2. For which values of distribution's coefficient $`v_d`$ (with $`v_t = 4`$) is B the best vertex?
   Hint: compare the slope of the level lines with the slope of the crews line.
3. Add the rule "at least $0.5M to distribution". Which vertices disappear, and which appear?

## Design Note: The Picture Is for Understanding, Not for Solving

No one solves a production LP by listing vertices: the table of crossings shows why. The picture
earns its place because it makes the vocabulary concrete. *Feasible region*, *vertex*, *tight row*
and *slack* are the words a solver's log, its dual values (lesson 2.3.1) and its infeasibility
reports (section 9) use, and each one is something you can now point at on a drawing. When a
large model misbehaves, shrinking it to two variables and drawing it is still one of the fastest
ways to see why.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**split_lp.py.** The model's rows and a `build` function that turns them into a MathOpt model; run
on its own, it solves the model with GLOP (*The Model*). *Try:* Change `VALUE` to `(4, 4)`.
Predict which of C and D GLOP returns, then run it.

- Program: [split_lp.py](src/split_lp.py)

**half_planes.py.** Tests five plans against the rows and prints the character map of the region
(*Each Constraint Keeps One Side of a Line*). *Try:* Raise the budget in `split_lp.py` from 30
to 34. Predict which edge of the map moves before you run it.

- Program: [half_planes.py](src/half_planes.py)

**vertices.py.** Crosses every pair of boundary lines and keeps the feasible crossings (*A Vertex
Is Where Two Boundary Lines Cross*). *Try:* Add `"floor_d": ((-1, 0), -5)` to `BOUNDS` in `split_lp.py`
(at least $0.5M to distribution) and predict how many vertices the region has.

- Program: [vertices.py](src/vertices.py)

**level_lines.py.** Values every vertex, slides the level line, shows the tie along an edge, asks
GLOP, and counts the crossings a larger model would have (*The Objective's Level Lines* and *If an
LP Has a Best Plan*). *Try:* Set the tie objective to `(6, 4)` and predict which vertex wins.

- Program: [level_lines.py](src/level_lines.py)

**draw_region.py.** Draws the region, its three constraint lines, three level lines and the best
vertex with matplotlib, and saves the figure as `feasible_region.png` in the temp folder. *Try:*
Add the level line for 120 and check that it passes through B.

- Program: [draw_region.py](src/draw_region.py)
