# 2.1.2 Standard Form, Slack and Surplus

The program split of lesson 2.1.1 is in front of GridCap's finance team, and two questions come
back. A quantitative analyst wants to check it with her own LP code, which accepts only one shape
of problem: maximize, every row a $`\le`$, every variable $`\ge 0`$. The budget officer asks a
plainer question: "of each limit, how much is left?". The first question is about **standard
form**, the one shape every LP can be rewritten into. The second is about **slack** and
**surplus**, the room each row has left. Both turn out to be the same idea, and the next two
modules (05, the simplex method, and 06, duality) are written in their terms. Four rules, one per
heading.

GridCap is fictional; the numbers are the 2027 split of lesson 2.1.1, whose answer was:
transmission $4,329.9k, distribution $4,017.9k, vegetation $312.0k, NPV $4,611.5k.

## Every LP Can Be Rewritten Into One Standard Form

First, the notation. Put the variables in a list, $`x = (x_1, \dots, x_n)`$; here
$`x = (s_{\text{transmission}}, s_{\text{distribution}}, s_{\text{vegetation}})`$. A row
$`a_1 x_1 + \dots + a_n x_n \le b`$ is written $`a \cdot x \le b`$, where $`a \cdot x`$ (the *dot
product*) means "multiply entry by entry, then add". Stack the rows' coefficient lists $`a`$ as the
rows of a table $`A`$ (a **matrix**, one row per constraint and one column per variable) and their
right-hand sides as a list $`b`$, and the whole system of rows is $`A x \le b`$: row $`i`$ of
$`A x`$ is $`a_i \cdot x`$, and it must be at most $`b_i`$. The objective's coefficients form one
more list $`c`$, and the objective is $`c \cdot x`$, also written $`c^\top x`$.

The **standard form** this course uses is

```math
\max \; c^\top x \quad \text{s.t.} \quad A x \le b, \quad x \ge 0
```

Every LP can be rewritten into it, by five moves, each of which keeps exactly the same solutions:

| The model has | Rewrite it as | Why it is the same |
| --- | --- | --- |
| $`a \cdot x \ge b`$ | $`-a \cdot x \le -b`$ | multiplying by $`-1`$ flips the inequality |
| $`a \cdot x = b`$ | $`a \cdot x \le b`$ and $`-a \cdot x \le -b`$ | "equal" is "at most and at least" |
| $`\min\, c^\top x`$ | $`\max\, (-c)^\top x`$, then negate the value | the lowest cost is minus the highest negative cost |
| variables on both sides | move them to the left | ordinary algebra |
| $`x_j \le u_j`$ | one more row of $`A`$ | a bound is a row with one coefficient |

Two more moves handle variables whose domain is not $`x_j \ge 0`$: a variable with lower bound
$`\ell_j \ne 0`$ is replaced by $`x_j' = x_j - \ell_j \ge 0`$, and a **free** variable (any sign,
such as a change in spend that may be negative) is written as the difference of two non-negative
ones, $`x_j = x_j^+ - x_j^-`$.

Different books choose different standard forms: some minimize, some use $`Ax = b`$ (the equality form of
the next heading). The book *Hands-On Mathematical Optimization with Python* (MO-book) writes
$`\min c^\top x`$ s.t. $`Ax \ge b`$, $`x \ge 0`$; the HiGHS documentation writes
$`\min c^\top x`$ s.t. $`Ax = b`$, $`x \ge 0`$. The moves are the same, so check which form a text means before you use its
formulas.

The program below reads the split model's rows from MathOpt and applies the moves. Each row is
stored with a lower and an upper bound (the last heading of this lesson explains why), so a finite
upper bound gives a $`\le`$ row as it is, and a finite lower bound gives a row multiplied by
$`-1`$:

```python
for con in model.linear_constraints():
    a = {t.variable: t.coefficient for t in con.terms()}
    if math.isfinite(con.upper_bound):                       # a.x <= ub stays as it is
        add(a, con.upper_bound, con.name)
    if math.isfinite(con.lower_bound):                       # a.x >= lb  becomes  -a.x <= -lb
        add({v: -c for v, c in a.items()}, -con.lower_bound, f"{con.name} (x -1)")
for v in variables:
    if math.isfinite(v.upper_bound):                         # an upper bound is one more row
        add({v: 1.0}, v.upper_bound, f"{v.name} <= ub")
sign = 1.0 if model.objective.is_maximize else -1.0          # min f  is  max -f
```

An equality row has both bounds finite and equal, so it produces both rows of the second move. The
split model's matrix:

```text
row                          s_transmission   s_distribution     s_vegetation         b
budget                                    1                1                1   8,890.0
crew_transmission                   0.00246                0                0      26.0
crew_distribution                         0          0.00224                0       9.0
crew_vegetation                           0                0          0.00641       2.0
floor_vegetation (x -1)                   0                0               -1    -300.0
share_transmission                      0.5             -0.5             -0.5       0.0
share_distribution                     -0.5              0.5             -0.5       0.0
share_vegetation                       -0.5             -0.5              0.5       0.0
c (max)                               0.582            0.477            0.561
original model NPV 4,611.5   standard form NPV 4,611.5
```

Read it against the model. The floor $`s_V \ge 300`$ became $`-s_V \le -300`$. Each share row
$`s_k \le 0.5 (s_T + s_D + s_V)`$ became, with the variables moved left, $`0.5\, s_k - 0.5\,(\text{the
other two}) \le 0`$. The crew rows carry $`m_k / 1000`$. The last line solves a fresh model built
from nothing but $`c`$, $`A`$ and $`b`$, and gets the same NPV, which is the point: standard form
changes how the LP is written, never what it allows.

<!-- practice 1 -->

## Slack Is the Room Left in a ≤ Row, and Surplus Is the Excess Over a ≥ Row

The budget officer's question has a precise answer for each row:

- For a $`\le`$ row $`a \cdot x \le b`$, the **slack** is $`b - a \cdot x`$: how far the row's
  activity is below its limit. Unspent budget is the budget row's slack.
- For a $`\ge`$ row $`a \cdot x \ge b`$, the **surplus** is $`a \cdot x - b`$: how far the activity
  is above its minimum. Vegetation spend above the floor is the floor row's surplus.

Both are $`\ge 0`$ for any allowed solution, and both are $`0`$ exactly when the row is full. A row
whose slack or surplus is zero at the solution is called **binding** (also *active* or *tight*);
lesson 2.1.1 called these the full rows.

Slack is more than a number to report: it can be a variable. Add one new variable per row,
$`\text{slack}_i \ge 0`$, and every inequality becomes an equation:

```math
a \cdot x \le b \;\iff\; a \cdot x + \text{slack} = b,\ \text{slack} \ge 0
\qquad\qquad
a \cdot x \ge b \;\iff\; a \cdot x - \text{surplus} = b,\ \text{surplus} \ge 0
```

The whole LP becomes $`\max c^\top x`$ s.t. $`A x + \text{slack} = b`$, $`x, \text{slack} \ge 0`$:
the **equality form**, the shape the simplex method of lesson 2.2.2 works on. The program builds the
split in this form, one extra variable per row:

```python
def row(expr, sense: str, rhs: float, name: str) -> None:
    extra[name] = model.add_variable(lb=0, name=f"{'slack' if sense == '<=' else 'surplus'}_{name}")
    if sense == "<=":
        model.add_linear_constraint(expr + extra[name] == rhs, name=name)      # a.x + slack = b
    else:
        model.add_linear_constraint(expr - extra[name] == rhs, name=name)      # a.x - surplus = b
```

It then prints, for each row, the value GLOP chose for the extra variable, next to the room
computed from lesson 2.1.1's solution ($`b - a \cdot x`$ for a $`\le`$ row, $`a \cdot x - b`$ for
a $`\ge`$ row):

```text
equality form: OPTIMAL, NPV 4,611.5
row                  variable                       solver value       room
budget               slack_budget                          230.3      230.3
crew_transmission    slack_crew_transmission                15.3       15.3
crew_distribution    slack_crew_distribution                 0.0        0.0
crew_vegetation      slack_crew_vegetation                   0.0        0.0
floor_vegetation     surplus_floor_vegetation               12.0       12.0
share_transmission   slack_share_transmission                0.0        0.0
share_distribution   slack_share_distribution              312.0      312.0
share_vegetation     slack_share_vegetation              4,017.9    4,017.9
```

The same NPV, and each slack equals the room. Three rows are binding: `crew_distribution`,
`crew_vegetation` and `share_transmission`. Now read each number in the budget officer's units:

- `budget`: $230.3k unspent.
- `crew_transmission`: 15.3 crew-months of transmission crews idle (26 available, 10.7 used).
- `floor_vegetation`: vegetation got $12.0k more than the regulator's minimum.
- `share_distribution`: 312.0, in the row's own units. The row is $`0.5 s_D - 0.5 s_T - 0.5 s_V \le 0`$, so its slack is
  $`0.5 (s_T + s_V - s_D) = 0.5 (4{,}329.9 + 312.0 - 4{,}017.9) = 312.0`$: half of how far
  distribution is below the other two together. A slack is measured in
  the units of the row as written; multiply a row by 2 and its slack doubles. When you report a
  slack, say which row it belongs to and in what units.

A slack is never negative in an allowed solution. If your own computation gives
$`-0.0000001`$, that is floating-point noise, not a violated row; compare with a tolerance, as
lesson 2.1.1 did.

## A Row With Room Does Not Shape the Answer; Loosening It Changes Nothing

Slack tells the planner where extra resources pay. The program loosens one row at a time, by
more than nothing, and re-solves:

```python
print(f"{'as built':34}", npv(build(YEAR)))
print(f"{'budget +200 (room 230.3)':34}", npv(build(YEAR, budget=small.budget[YEAR] + 200)))
print(f"{'no vegetation floor (room 12.0)':34}", npv(build(YEAR, floor={})))
print(f"{'distribution crews +1 (room 0)':34}", npv(build(YEAR, crews={**crews, "distribution": 10})))
print(f"{'vegetation crews +1 (room 0)':34}", npv(build(YEAR, crews={**crews, "vegetation": 3})))
```

```text
as built                           NPV  4,611.5  {'transmission': 4329.9, 'distribution': 4017.9, 'vegetation': 312.0}
budget +200 (room 230.3)           NPV  4,611.5  {'transmission': 4329.9, 'distribution': 4017.9, 'vegetation': 312.0}
no vegetation floor (room 12.0)    NPV  4,611.5  {'transmission': 4329.9, 'distribution': 4017.9, 'vegetation': 312.0}
distribution crews +1 (room 0)     NPV  4,733.5  {'transmission': 4445.0, 'distribution': 4133.0, 'vegetation': 312.0}
vegetation crews +1 (room 0)       NPV  4,746.6  {'transmission': 4445.0, 'distribution': 3977.0, 'vegetation': 468.0}
```

Read the five lines against the slack table.

- **Rows with room.** The budget had $230.3k of slack; adding $200k leaves the answer exactly where
  it was. The floor had $12.0k of surplus; deleting the floor altogether changes nothing. A row with
  room was not pressing on the solution, so moving it, or removing it, leaves the best split
  allowed and still best.
- **Binding rows.** One more crew-month for distribution or for vegetation, and the NPV rises, by
  $`4{,}733.5 - 4{,}611.5 = 122.0`$ and $`4{,}746.6 - 4{,}611.5 = 135.1`$ $k.

Why must the rows with room not matter? Suppose the solution $`x^*`$ satisfies a row with room,
and you loosen that row. Every split allowed before is still allowed, so the best value can only
rise. If some new split $`y`$ beat $`x^*`$, then every point on the straight line from $`x^*`$
toward $`y`$ would beat $`x^*`$ too, because the objective is linear. Points close enough to
$`x^*`$ on that line still satisfy the loosened row's old limit (there was room) and every other
row (they are the same rows, and $`x^*`$ and $`y`$ both satisfy them, so every point between does).
Those points were allowed in the original model and beat $`x^*`$, which contradicts $`x^*`$ being
optimal. So the answer stays. This argument uses linearity twice: in the objective, and in "every
point between two allowed points is allowed" (the allowed region is *convex*, lesson 1.2.3). For a
MILP, where the points between two plans are fractional and not allowed, it fails, and section 3
shows what happens instead.

The distribution line has one more lesson in it. One crew-month bought the same NPV that three did
in lesson 2.1.1 (4,733.5 both times). With 10 crew-months, distribution's crews allow
$`10 \times 1000 / 2.24 = 4{,}464.3`$ $k, but distribution only grows to $4,133.0k, because a new
row binds first: the budget ($`4{,}445.0 + 4{,}133.0 + 312.0 = 8{,}890`$). So the value of an extra
unit of a binding row holds only until another row binds. How far it holds, and the price per unit,
are the *ranging* and *dual values* of lesson 2.3.3.

## MathOpt Stores Every Row as lb ≤ a·x ≤ ub, So You Write Rules as the Business States Them

If every LP must be in standard form, why did lesson 2.1.1 write $`\ge`$ rows, and variables on
both sides of a share row? Because MathOpt does the conversion for you. Every row is stored in one
shape, a lower bound, a linear expression and an upper bound, $`\text{lb} \le a \cdot x \le
\text{ub}`$, with $`\pm\infty`$ for a missing side:

```python
model.add_linear_constraint(t + d <= 8890, name="written_le")
model.add_linear_constraint(d >= 300, name="written_ge")
model.add_linear_constraint(t == 2 * d, name="written_eq")
model.add_linear_constraint(lb=1000, ub=5000, expr=t + d, name="written_range")
model.add_linear_constraint(t <= 0.5 * (t + d) + 100, name="written_both_sides")
```

```text
written_le             -inf <= +1*t +1*d    <= 8890.0
written_ge            300.0 <= +1*d         <= inf
written_eq              0.0 <= +1*t -2*d    <= 0.0
written_range        1000.0 <= +1*t +1*d    <= 5000.0
written_both_sides     -inf <= +0.5*t -0.5*d <= 100.0
variable t: 0.0 <= t <= inf
variable d: 0.0 <= d <= 4000.0
variable free: -inf <= free <= inf
```

- A $`\le`$ row has $`\text{lb} = -\infty`$; a $`\ge`$ row has $`\text{ub} = +\infty`$.
- An equation has $`\text{lb} = \text{ub}`$. `t == 2 * d` was stored as $`0 \le t - 2d \le 0`$:
  the variables moved left, the constant right.
- A **ranged row**, "between 1,000 and 5,000", is one row with two finite bounds, written with
  `lb=`, `ub=` and `expr=`. In standard form it would be two rows.
- `written_both_sides` had variables and a constant on both sides; MathOpt collected them into
  $`0.5t - 0.5d \le 100`$.
- Variables have bounds too. `free` was created with no `lb` and no `ub`, and it is
  $`-\infty \le \text{free} \le +\infty`$: the default is a free variable, which is why every money
  variable in this module says `lb=0`.

So in MathOpt, write each rule the way the business states it. The rewrite into a solver's own
internal form is the solver's job, and it does not change the answer, as the first heading showed.
You will still use standard form, and slack, in three places: when you read LP theory (lessons
2.2.2 and 2.3.1 assume one form), when you implement an algorithm yourself (the simplex tableau of
lesson 2.2.2), and when you explain to a budget officer what is left of each limit.

<!-- practice 2 -->

## The Model

The split model of lesson 2.1.1, unchanged, in the two forms of this lesson.

**Sets.** $`K`$, the programs. **Parameters.** $`v_k`$, $`m_k`$, $`C_k`$, $`B`$, $`f`$, $`\alpha`$ as in
lesson 2.1.1. **Variables.** $`s_k \ge 0`$, continuous, for $`k \in K`$.

**As written** (lesson 2.1.1):

```math
\begin{aligned}
\max \;& \sum_{k \in K} v_k\, s_k \\
\text{s.t. }& \sum_{k \in K} s_k \le B && && \text{(budget)} \\
& \frac{m_k}{1000}\, s_k \le C_k && \forall k \in K && \text{(crew}_k) \\
& s_{\text{vegetation}} \ge f && && \text{(floor\_vegetation)} \\
& s_k \le \alpha \sum_{j \in K} s_j && \forall k \in K && \text{(share}_k) \\
& s_k \ge 0 && \forall k \in K
\end{aligned}
```

**Standard form**, $`\max c^\top s`$ s.t. $`A s \le b`$, $`s \ge 0`$, with the changed rows marked:

```math
\begin{aligned}
\max \;& \sum_{k \in K} v_k\, s_k \\
\text{s.t. }& \sum_{k \in K} s_k \le B && && \text{(budget)} \\
& \frac{m_k}{1000}\, s_k \le C_k && \forall k \in K && \text{(crew}_k) \\
& -s_{\text{vegetation}} \le -f && && \text{(floor\_vegetation)} \quad \leftarrow \times (-1) \\
& (1 - \alpha)\, s_k - \alpha \sum_{j \ne k} s_j \le 0 && \forall k \in K && \text{(share}_k) \quad \leftarrow \text{moved left} \\
& s_k \ge 0 && \forall k \in K
\end{aligned}
```

**Equality form**: one more variable per row, all $`\ge 0`$, and every row an equation:

```math
\begin{aligned}
\max \;& \sum_{k \in K} v_k\, s_k \\
\text{s.t. }& \sum_{k \in K} s_k + \sigma_{\text{budget}} = B && && \text{(budget)} \\
& \frac{m_k}{1000}\, s_k + \sigma_{\text{crew},k} = C_k && \forall k \in K && \text{(crew}_k) \\
& s_{\text{vegetation}} - \sigma_{\text{floor}} = f && && \text{(floor\_vegetation)} \\
& s_k - \alpha \sum_{j \in K} s_j + \sigma_{\text{share},k} = 0 && \forall k \in K && \text{(share}_k) \\
& s_k \ge 0,\ \sigma \ge 0 && \forall k \in K
\end{aligned}
```

Here $`\sigma`$ (sigma) names each row's slack, or the floor's surplus; in the code they are the
variables `slack_budget`, `slack_crew_transmission`, ..., `surplus_floor_vegetation`.

## Summary

- **Every LP can be rewritten into one standard form**, $`\max c^\top x`$, $`Ax \le b`$,
  $`x \ge 0`$: negate $`\ge`$ rows and minimizations, split equations into two rows, move variables
  left, turn bounds into rows, and shift or split variables that are not $`\ge 0`$. The answer
  never changes.
- **Slack is the room left in a $`\le`$ row; surplus is the excess over a $`\ge`$ row.** Both are
  $`\ge 0`$, both are zero exactly on a binding row, and adding them as variables gives the
  equality form. A slack is in the units of the row as written.
- **A row with room does not shape the answer.** Loosen or delete it and the LP's answer stays; an
  extra unit of a binding row pays, until another row binds.
- **MathOpt stores every row as lb ≤ a·x ≤ ub**, so write rules as the business states them and let
  the solver convert. A variable with no bounds is free.

## Reference

| Original | Standard form ($`\max`$, $`\le`$, $`x \ge 0`$) | Equality form |
| --- | --- | --- |
| $`a \cdot x \le b`$ | $`a \cdot x \le b`$ | $`a \cdot x + \text{slack} = b`$ |
| $`a \cdot x \ge b`$ | $`-a \cdot x \le -b`$ | $`a \cdot x - \text{surplus} = b`$ |
| $`a \cdot x = b`$ | $`a \cdot x \le b`$, $`-a \cdot x \le -b`$ | $`a \cdot x = b`$ (no extra variable) |
| $`\ell \le a \cdot x \le u`$ | two rows | two rows, or one with a bounded slack |
| $`\min c^\top x`$ | $`\max (-c)^\top x`$ | same |
| $`x_j`$ free | $`x_j^+ - x_j^-`$, both $`\ge 0`$ | same |
| $`x_j \ge \ell_j`$ | $`x_j' = x_j - \ell_j \ge 0`$ | same |

| Term | Meaning |
| --- | --- |
| activity | $`a \cdot x`$ at the solution |
| slack | $`b - a \cdot x`$ on a $`\le`$ row |
| surplus | $`a \cdot x - b`$ on a $`\ge`$ row |
| binding (active, tight) | slack or surplus is zero |

**Further reading:** [MathOpt `linear_constraints.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/linear_constraints.py) (the docstring of `LinearConstraint`: every row is $`\text{lb} \le \sum_i a_i x_i \le \text{ub}`$, and $`\text{lb} = \text{ub}`$ is an equation); [MathOpt `model.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`add_variable` defaults to $`\text{lb} = -\infty`$, $`\text{ub} = +\infty`$, a free variable); [MO-book, Chapter 2: Linear optimization](https://mobook.github.io/MO-book/notebooks/02/02.00.html) (its standard form, $`\min c^\top x`$, $`Ax \ge b`$, $`x \ge 0`$, and the moves that bring any LP to it); [HiGHS, Feasibility and optimality](https://ergo-code.github.io/HiGHS/dev/guide/kkt/) (the equality form $`\min c^\top x`$, $`Ax = b`$, $`x \ge 0`$ that a solver's theory is written in).

## Challenges

1. A ranged row $`1{,}000 \le t + d \le 5{,}000`$ has two kinds of room. Write its slack and its
   surplus, and say which one is zero when $`t + d = 5{,}000`$.
2. The budget officer multiplies the crew rows by 1,000 so that their coefficients read as
   crew-months per $1,000k. What happens to their slacks, and to the answer?
3. An equation row is always binding. Explain why, using the definition of slack.

## Design Note: Why the Course Uses max and ≤

Textbooks disagree on standard form: many write $`\min c^\top x`$ s.t. $`Ax = b`$, $`x \ge 0`$,
which is the equality form with the objective flipped. This course uses $`\max`$ with $`\le`$ because
GridCap's questions are mostly "most value within limits", so the model as written is already
nearly in that shape, and the slack of each $`\le`$ row is the unused amount of a resource a planner
can name. Lesson 2.3.1's dual is written for the same form.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**standard_form.py.** Reads the split model's rows from MathOpt, rewrites them as $`A x \le b`$ with
$`x \ge 0`$, prints the matrix and solves the matrix form again (*Every LP Can Be Rewritten*).
*Try:* Turn the objective into a minimization of the negated values in `program_split.py` and
predict what the program prints for $`c`$.

- Program: [standard_form.py](src/standard_form.py)

**slack_surplus.py.** Builds the split in equality form, with a slack or surplus variable on every
row, and compares each with the room computed from the original model (*Slack Is the Room Left*).
*Try:* Raise the vegetation floor in `FLOOR` to 312. Predict which row's room changes, and to what.

- Program: [slack_surplus.py](src/slack_surplus.py)

**binding_rows.py.** Loosens rows with and without room, one at a time, and re-solves (*A Row With
Room Does Not Shape the Answer*). *Try:* Add $250k instead of $200k to the budget. Predict whether
the NPV moves.

- Program: [binding_rows.py](src/binding_rows.py)

**row_bounds.py.** Shows how MathOpt stores rows written five ways, and the default bounds of a
variable (*MathOpt Stores Every Row*). *Try:* Add a row `2 * t >= d`. Predict its stored bounds
before you run it.

- Program: [row_bounds.py](src/row_bounds.py)
