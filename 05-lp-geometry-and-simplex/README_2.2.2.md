# 2.2.2 Simplex as Walking Between Vertices (a Tiny Tableau Implementation)

Lesson 2.2.1 solved GridCap's budget split by listing every vertex of its region and keeping the
best. That took ten pairs of lines for two variables; for a model with 100 variables and 200 rows
the same count is about $`4 \times 10^{81}`$. GridCap's capital models are far bigger than that,
and GLOP and HiGHS still solve their LPs. They do not list vertices. They start at one vertex and
walk along the region's edges to a better neighbour, again and again, until no neighbour is
better. That walk is the **simplex method** (George Dantzig, 1947), and it is the "S" in many
solver logs.

This lesson builds the walk in about 60 lines of plain Python, runs it on the budget split, and
watches it go A → B → C on the picture from lesson 2.2.1. It takes five rules.

## The Model, With One Slack per Row

The budget split of lesson 2.2.1, unchanged: $`d`$ and $`t`$ are the money for distribution and
transmission in $100k.

```math
\begin{aligned}
\max \;& 5d + 4t \\
\text{s.t. }& d + t \le 30 && \text{(budget)} \\
& 3d + 2t \le 72 && \text{(crews)} \\
& t \le 20 && \text{(ready\_t)} \\
& d,\ t \ge 0
\end{aligned}
```

Simplex works with equations, not inequalities, so each $`\le`$ row gets a **slack variable**: a new
variable that holds the row's unused amount (lesson 2.1.2
covers this conversion for every kind of row). The slack of budget, $`s_\text{budget}`$, is the money
left unspent; $`s_\text{crews}`$ the crew-weeks left idle; $`s_\text{ready\_t}`$ the ready
transmission work left undone. A slack can never be negative, since a negative slack would mean the
row is broken:

```math
\begin{aligned}
\max \;& 5d + 4t \\
\text{s.t. }& d + t + s_\text{budget} = 30 && \text{(budget)} \\
& 3d + 2t + s_\text{crews} = 72 && \text{(crews)} \\
& t + s_\text{ready\_t} = 20 && \text{(ready\_t)} \\
& d,\ t,\ s_\text{budget},\ s_\text{crews},\ s_\text{ready\_t} \ge 0
\end{aligned}
```

The two models have the same plans: a plan $`(d, t)`$ satisfies the first exactly when the slacks
it defines are all $`\ge 0`$ in the second. Now there are $`n = 2`$ original variables, $`m = 3`$
equations, and $`n + m = 5`$ variables in all.

## A Vertex Is a Basis: Set n Variables to Zero and Solve for the Rest

Three equations can pin down three unknowns. So pick any 2 of the 5 variables, set them to 0, and
solve the three equations for the other 3. The 3 you solve for are the **basic** variables, and the
set of them is the **basis**; the 2 you set to zero are **nonbasic**. The point you get is a
**basic solution**.

A slack at 0 means its row is tight, and $`d = 0`$ or $`t = 0`$ means a bound is tight. So setting
2 variables to zero is choosing 2 tight rows, which is exactly how lesson 2.2.1 found the crossing
points. Three bases, solved:

| Nonbasic (set to 0) | Basic, solved | Point $`(d, t)`$ | Vertex? |
| --- | --- | --- | --- |
| $`d, t`$ | $`s_\text{budget} = 30,\ s_\text{crews} = 72,\ s_\text{ready\_t} = 20`$ | (0, 0) | A |
| $`t, s_\text{crews}`$ | $`d = 24,\ s_\text{budget} = 6,\ s_\text{ready\_t} = 20`$ | (24, 0) | B |
| $`s_\text{budget}, s_\text{crews}`$ | $`d = 12,\ t = 18,\ s_\text{ready\_t} = 2`$ | (12, 18) | C |

A basic solution whose values are all $`\ge 0`$ is a **basic feasible solution**, and the basic
feasible solutions are exactly the vertices. A basic solution with a negative value is one of the
crossings outside the region. Making $`s_\text{budget}`$ and $`d`$ nonbasic, for example, gives
$`t = 30`$, $`s_\text{crews} = 72 - 60 = 12`$ and $`s_\text{ready\_t} = 20 - 30 = -10`$: the
crossing at $`(0, 30)`$ that lesson 2.2.1 found breaks ready_t.

Two vertices are **neighbours**, joined by an edge of the region, when their bases differ in one
variable: A and B share the basic variables $`s_\text{budget}`$ and $`s_\text{ready\_t}`$, and
differ only in whether $`s_\text{crews}`$ or $`d`$ is the third. One step of simplex swaps one
variable into the basis and one out: the **entering** variable rises from 0, and the **leaving**
variable falls to 0.

## The Tableau Holds the Equations, and Its Last Row Says Which Variable Improves the Objective

A **tableau** is the equations written as a table of numbers: one row per equation, one column per
variable, and a last column for the right-hand sides. Below them sits one more row for the
objective. Write the objective's value as $`z`$, so $`z = 5d + 4t`$, and move every variable to the
left: $`z - 5d - 4t = 0`$. The objective row stores the coefficients $`-5, -4, 0, 0, 0`$ and the
current value of $`z`$ on the right.

```python
def tableau(A: list[list[float]], b: list[float], c: list[float]) -> list[list[float]]:
    m = len(A)
    rows = [list(map(float, A[i])) + [1.0 if j == i else 0.0 for j in range(m)] + [float(b[i])]
            for i in range(m)]
    return rows + [[-float(cj) for cj in c] + [0.0] * m + [0.0]]
```

Row $`i`$ is the row $`i`$ of $`A`$, then a 1 in the column of slack $`i`$ and 0 for the other
slacks, then $`b_i`$. The last row is $`-c`$, zeros under the slacks, and 0 for $`z`$. Built for the
budget split and printed:

```python
A = [list(a) for a, _ in ROWS.values()]
b = [rhs for _, rhs in ROWS.values()]
names = list(NAMES) + [f"s_{label}" for label in ROWS]
T = tableau(A, b, VALUE)
basis = list(range(len(NAMES), len(names)))
show(T, names, basis)
```

```text
    basis         d         t  s_budget   s_crews s_ready_t       rhs
 s_budget         1         1         1         0         0        30
  s_crews         3         2         0         1         0        72
s_ready_t         0         1         0         0         1        20
objective        -5        -4         0         0         0         0
```

Each basic variable's column is a **unit column**: a 1 in its own row and 0 everywhere else,
including the objective row. That is what makes a tableau easy to read. Set the nonbasic variables
to 0 and each row says "this basic variable equals the right-hand side". So the tableau is at
vertex A: $`d = t = 0`$, the slacks hold 30, 72 and 20, and $`z = 0`$.

The objective row reads the same way. Written out, it says $`z - 5d - 4t = 0`$, that is
$`z = 0 + 5d + 4t`$: raising nonbasic $`d`$ from 0 adds 5 to $`z`$ per unit, and raising $`t`$
adds 4. In general, the objective row always says

```math
z = \text{(rhs of the objective row)} - \sum_{j \text{ nonbasic}} (\text{entry}_j)\, x_j
```

so **a negative entry marks a variable that improves the objective if it enters**. These entries are
the **reduced costs** of the nonbasic variables (lesson 2.3.3 reads them from a solver). Which
negative entry to pick is a choice; the classic rule, **Dantzig's rule**, takes the most negative:

```python
def entering(T: list[list[float]]) -> int | None:
    """The column with the most negative entry in the objective row; None when none improves."""
    z = T[-1][:-1]
    k = min(range(len(z)), key=lambda j: z[j])
    return k if z[k] < -EPS else None
```

`EPS` is $`10^{-9}`$: an entry like $`-10^{-15}`$ is float noise, not a real improvement. Here the
most negative entry is $`-5`$, so $`d`$ enters.

## The Ratio Test Picks the Row That Leaves: the First Basic Variable to Reach Zero

$`d`$ rises from 0 while $`t`$ stays 0. Each equation then says how a basic variable must change to
keep the equation true:

```math
s_\text{budget} = 30 - 1 \cdot d, \qquad s_\text{crews} = 72 - 3d, \qquad s_\text{ready\_t} = 20 - 0 \cdot d
```

Every basic variable must stay $`\ge 0`$. $`s_\text{budget}`$ reaches 0 at $`d = 30`$,
$`s_\text{crews}`$ at $`d = 72/3 = 24`$, and $`s_\text{ready\_t}`$ never does. So $`d`$ can rise to
24 and no further: one unit more and $`s_\text{crews}`$ would be negative, which means the plan
would need more crew-weeks than exist. $`s_\text{crews}`$ is the leaving variable.

That is the **ratio test**: for every row whose entry in the entering column is positive, divide the
right-hand side by that entry, and pick the row with the smallest ratio. A row whose entry is zero
or negative sets no limit, because raising the entering variable leaves its basic variable
unchanged or makes it larger. Ties go to the lowest row here; any tied row is a correct choice.

```python
def leaving(T: list[list[float]], k: int) -> int | None:
    """The ratio test: the row whose b_i / a_ik is smallest over a_ik > 0; None when no row limits k."""
    ratios = [(T[i][-1] / T[i][k], i) for i in range(len(T) - 1) if T[i][k] > EPS]
    return min(ratios)[1] if ratios else None
```

The smallest ratio is the step length: how far the entering variable rises. When no row has a
positive entry, nothing stops the rise; lesson 2.2.3 shows what that means. The walk program
prints its test:

```text
entering d: its objective-row entry is -5
  ratio test, row s_budget: 30 divided by 1 is 30
  ratio test, row s_crews: 72 divided by 3 is 24
  ratio test, row s_ready_t: entry 0, sets no limit
leaving s_crews
```

Taking the smallest ratio is what keeps the walk inside the region. Picking budget's 30 instead
would push $`d`$ to 30, and the plan $`(30, 0)`$ needs 90 crew-weeks: it is the crossing that lesson
2.2.1 found "outside: breaks crews".

<!-- practice 1 -->

## A Pivot Rewrites the Tableau So the Entering Variable Is Basic

The tableau must now describe vertex B, with $`d`$ basic in the row $`s_\text{crews}`$ held. That
means turning $`d`$'s column into a unit column with its 1 in that row. The operation is a
**pivot**, on the **pivot element** where the leaving row meets the entering column (here the 3).
It uses the two row operations that never change what a system of equations means:

1. Divide the pivot row by the pivot element, so the pivot element becomes 1.
2. From every other row, objective row included, subtract the new pivot row times that row's entry
   in the pivot column, so the entry becomes 0.

```python
def pivot(T: list[list[float]], r: int, k: int) -> list[list[float]]:
    """Make column k a unit column with its 1 in row r: one step to a neighbouring vertex."""
    row = [v / T[r][k] for v in T[r]]
    return [row if i == r else [v - T[i][k] * w for v, w in zip(T[i], row)] for i in range(len(T))]
```

`pivot` returns a new tableau and leaves the old one as it was. After the pivot:

```text
    basis         d         t  s_budget   s_crews s_ready_t       rhs
 s_budget         0       1/3         1      -1/3         0         6
        d         1       2/3         0       1/3         0        24
s_ready_t         0         1         0         0         1        20
objective         0      -2/3         0       5/3         0       120
```

Read it as before. $`d = 24`$, $`s_\text{budget} = 6`$ (that is $600k unspent),
$`s_\text{ready\_t} = 20`$, and the nonbasic $`t`$ and $`s_\text{crews}`$ are 0. That is vertex
B, worth 120, and the right-hand side of the objective row says so. The step moved along one edge of
the region, from A to B, along the bottom edge $`t = 0`$.

<!-- practice 2 -->

## When No Objective-Row Entry Is Negative, the Vertex Is Optimal

The objective row at B reads $`z = 120 + \tfrac{2}{3} t - \tfrac{5}{3} s_\text{crews}`$. Raising
$`t`$ still pays $`\tfrac{2}{3}`$ per unit. That is less than the 4 that $`t`$ earned at A, because
at B raising $`t`$ must lower $`d`$ to free crew-weeks: each unit of $`t`$ uses 2 crew-weeks, which
costs $`\tfrac{2}{3}`$ of a unit of $`d`$, worth $`\tfrac{10}{3}`$, so the net is
$`4 - \tfrac{10}{3} = \tfrac{2}{3}`$. The reduced cost counts that trade automatically. So $`t`$
enters, and the walk continues:

```text
entering t: its objective-row entry is -2/3
  ratio test, row s_budget: 6 divided by 1/3 is 18
  ratio test, row d: 24 divided by 2/3 is 36
  ratio test, row s_ready_t: 20 divided by 1 is 20
leaving s_budget
    basis         d         t  s_budget   s_crews s_ready_t       rhs
        t         0         1         3        -1         0        18
        d         1         0        -2         1         0        12
s_ready_t         0         0        -3         1         1         2
objective         0         0         2         1         0       132
```

The budget runs out first, at $`t = 18`$. The tableau is now at vertex C: $`d = 12`$, $`t = 18`$,
$`s_\text{ready\_t} = 2`$, value 132. Its objective row has no negative entry, and it says

```math
z = 132 - 2\, s_\text{budget} - 1\, s_\text{crews}
```

That one line is a proof that C is optimal. It is an equation that every feasible plan satisfies,
since the tableau is the original equations rearranged. Every feasible plan has
$`s_\text{budget} \ge 0`$ and $`s_\text{crews} \ge 0`$, so every feasible plan has $`z \le 132`$,
and C reaches 132. This is the **optimality test**: when no entry of the objective row is negative,
no neighbour is better, and by the argument just given no plan anywhere is. Because the region is
convex, a vertex that beats its neighbours is the best overall: an LP has no "local best" that is
not the global best.

The two numbers in the slack columns also have a meaning the planner cares about. Leaving one unit
($100k) of budget unspent costs 2 risk points; leaving one crew-week idle costs 1. Lessons 2.3.1 and
2.3.3 call them **dual values** (or shadow prices) and show what they say about buying more budget
or crews.

Put together, the walk is a loop: find an entering column, run the ratio test, pivot, repeat until
the optimality test passes.

```python
def solve(A, b, c, names: list[str], max_steps: int = 50) -> Result:
    n, m = len(c), len(A)
    T, basis, steps = tableau(A, b, c), list(range(n, n + m)), []

    def point(T):
        x = [0.0] * (n + m)
        for i, j in enumerate(basis):
            x[j] = T[i][-1]
        return x

    for _ in range(max_steps):
        k = entering(T)
        if k is None:
            return Result("OPTIMAL", point(T)[:n], T[-1][-1], steps)
        r = leaving(T, k)
        if r is None:
            direction = [0.0] * (n + m)
            direction[k] = 1.0
            for i, j in enumerate(basis):
                direction[j] = -T[i][k]
            return Result("UNBOUNDED", point(T)[:n], T[-1][-1], steps, direction[:n])
        step = T[r][-1] / T[r][k]
        T, left = pivot(T, r, k), names[basis[r]]
        basis[r] = k
        steps.append((names[k], left, step, point(T)[:n], T[-1][-1]))
    return Result("STEP_LIMIT", point(T)[:n], T[-1][-1], steps)
```

`basis[i]` is the column of the variable basic in row `i`, and `point` reads every basic
variable's value off the right-hand side. The `UNBOUNDED` branch and `max_steps` are for lesson
2.2.3. Run on the budget split:

```text
d enters, s_crews leaves, step 24: vertex (24, 0), value 120
t enters, s_budget leaves, step 18: vertex (12, 18), value 132
OPTIMAL: d = 12, t = 18, value 132
```

Two pivots, A → B → C, the same answer as the picture and as GLOP in lesson 2.2.1. On the map of
lesson 2.2.1, the walk ran along the bottom edge and then up the crews line. It never looked at D
or E.

Nothing in `solve` is about two variables. OR-Tools' MathOpt sample `linear_programming.py` (lesson
2.1.1 read its answer) has three, so its region is a solid, no longer a polygon on paper:

```math
\begin{aligned}
\max \;& 10x_0 + 6x_1 + 4x_2 \\
\text{s.t. }& 10x_0 + 4x_1 + 5x_2 \le 600 && \text{(c1)} \\
& 2x_0 + 2x_1 + 6x_2 \le 300 && \text{(c2)} \\
& x_0 + x_1 + x_2 \le 100 && \text{(c3)} \\
& x_0,\ x_1,\ x_2 \ge 0
\end{aligned}
```

Its rows go into the tableau as they are, and GLOP solves the same LP for comparison:

```python
A = [[10, 4, 5],    # c1
     [2, 2, 6],     # c2
     [1, 1, 1]]     # c3
b = [600, 300, 100]
c = [10, 6, 4]
```

```python
result = solve(A, b, c, NAMES + ["s_c1", "s_c2", "s_c3"])
```

```text
x0 enters, s_c1 leaves, step 60: vertex (60, 0, 0), value 600
x1 enters, s_c3 leaves, step 200/3: vertex (100/3, 200/3, 0), value 2200/3
tableau OPTIMAL: x = (100/3, 200/3, 0), value 2200/3
GLOP    OPTIMAL: x = (33.3333, 66.6667, 0.0000), value 733.3333
```

Two pivots again, to the vertex GLOP returns. The first ratio test compared c1's
$`600 / 10 = 60`$, c2's $`300 / 2 = 150`$ and c3's $`100 / 1 = 100`$, so c1 left the basis first.
At the end, $`x_0`$, $`x_1`$ and the slack of c2 are basic, one per row, and c1 and c3 are the tight
rows that lesson 2.1.1 found full.

This tableau needs every $`b_i \ge 0`$, so that the slack basis at the origin is feasible. GridCap's
real rows include $`\ge`$ commitments, for which the origin is not feasible; lesson 2.2.3 shows how a
solver finds its first vertex then.

## Summary

- **A vertex is a basis.** Add a slack to every row; set $`n`$ of the $`n + m`$ variables to zero
  and solve for the rest. If every value is $`\ge 0`$, the point is a vertex.
- **The tableau's last row says which variable improves the objective.** A negative entry
  (reduced cost) marks a nonbasic variable whose increase raises $`z`$; Dantzig's rule picks the
  most negative.
- **The ratio test picks the row that leaves:** the smallest $`b_i / a_{ik}`$ over rows with
  $`a_{ik} > 0`$, the first basic variable to reach zero. It keeps the walk inside the region.
- **A pivot rewrites the tableau so the entering variable is basic**, with two row operations, and
  moves to a neighbouring vertex.
- **When no objective-row entry is negative, the vertex is optimal.** The objective row is then a
  proof: $`z`$ equals the current value minus nonnegative terms.

## Reference

| Term | Meaning |
| --- | --- |
| slack $`s_i`$ | unused amount of row $`i`$: $`s_i = b_i - a_i \cdot x \ge 0`$ |
| basis | the $`m`$ variables solved for; the other $`n`$ (nonbasic) are 0 |
| basic feasible solution | a basic solution with every value $`\ge 0`$; the same thing as a vertex |
| tableau | $`[A \mid I \mid b]`$ over $`[-c \mid 0 \mid z]`$ for $`\max c \cdot x`$, $`Ax \le b`$, $`x \ge 0`$, $`b \ge 0`$ |
| reduced cost | a nonbasic column's objective-row entry; negative means entering improves $`z`$ |
| entering variable | Dantzig's rule: the most negative objective-row entry |
| ratio test | leaving row $`r = \arg\min \{ b_i / a_{ik} : a_{ik} > 0 \}`$ |
| pivot on $`(r, k)`$ | divide row $`r`$ by $`a_{rk}`$; subtract $`a_{ik}`$ times it from every other row $`i`$ |
| optimality test | no negative entry in the objective row |

**Further reading:** [MathOpt sample linear_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/linear_programming.py) (the three-variable LP walked above); [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (primal simplex steps along vertices of the plan's region, dual simplex along those of the prices', and GLOP is Google's implementation of both); [Vanderbei, *Linear Programming: Foundations and Extensions*](https://vanderbei.princeton.edu/LPbook/) (the textbook's page, with its [Simple Pivot Tool](https://vanderbei.princeton.edu/JAVA/pivot/simple.html): pivot a random LP by hand in the book's dictionary form, with every primal and dual infeasible entry highlighted until the dictionary is optimal).

## Challenges

1. Use the other entering rule: let $`t`$ enter first at A (its entry is negative too). Which
   vertices does the walk visit, and is it longer or shorter?
2. In the final tableau, the row of $`s_\text{ready\_t}`$ says $`s_\text{ready\_t} - 3 s_\text{budget}
   + s_\text{crews} = 2`$. Use it to say how much more ready transmission work would be left undone if
   $100k of the budget were left unspent and the crews stayed fully used.
3. Why can simplex never visit the same vertex twice when every step length is positive? (Lesson
   2.2.3 shows the case where a step length is zero.)

## Design Note: Why Real Solvers Do Not Store a Tableau

This tableau is dense: every pivot rewrites all $`(m + 1)(n + m + 1)`$ numbers, most of which are
zeros in a real model (lesson 1.2.2).
Production simplex codes keep the original sparse matrix and a factorization of the current basis
instead, and compute only the one column and one row a pivot needs. That variant is called the **revised
simplex method**. The walk is the same: same bases, same ratio test, same optimality test, and the
60 lines here are a faithful small model of it. GLOP, OR-Tools' simplex code, implements both
the primal simplex of this lesson and the dual simplex that lesson 2.4.1 describes. Lesson 2.4.1
also compares simplex with methods that do not walk between vertices: interior point methods,
which cross the inside of the region, and first-order methods such as PDLP, which take many small
steps on the plan and the prices together.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**simplex_walk.py.** Builds the budget split's tableau, prints the ratio test and the tableau at
every pivot, then runs `solve` and lists the vertices it visited (every section of this lesson).
*Try:* Change `VALUE` in `split_lp.py` to `(5, 6)`. Predict the first entering variable and the
number of pivots, then run it.

- Program: [simplex_walk.py](src/simplex_walk.py)

**simplex_sample.py.** Adapted from the OR-Tools MathOpt sample `linear_programming.py`: the
tableau simplex walks its three-variable LP, and GLOP solves it for comparison (*When No
Objective-Row Entry Is Negative*). *Try:* Change c to `[10, 6, 9]`. Predict which variable enters
first and whether $`x_2`$ stays at 0.

- Program: [simplex_sample.py](src/simplex_sample.py)

**simplex.py.** The tableau simplex itself: `tableau`, `entering`, `leaving`, `pivot` and `solve`,
plus `show` and `fmt` to print a tableau with fractions.

- Library: [simplex.py](src/simplex.py)
