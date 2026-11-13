# 1.2.1 Vectors, Matrices and Ax ≤ b in NumPy

GridCap's finance team liked the plan from lesson 1.1.1: fund P001, P002, P005 and P006. The plan
is worth $3,627k and costs $7,100k, which fits the $7,390k capital budget with $290k to spare. Then
they asked a question the one-number budget could not answer: *does it fit each year?* GridCap's budget is set year by year, $2,300k for 2027,
$3,280k for 2028 and $2,310k for 2029. A project spends its cost over the years it is worked on,
so checking the plan means one sum per year, and a real model has hundreds of rows. This lesson
writes a plan as a vector and the rules as a matrix, so that one line of NumPy checks every rule
at once. Five rules, one per heading.

A **vector** here is an ordered list of numbers, one per project; a **matrix** is a table of
numbers with rows and columns. NumPy (`import numpy as np`) stores both as arrays and does
arithmetic on whole arrays at once. GridCap is a fictional utility; none of its numbers describe a
real one.

## A Plan Is a Vector, and Its Value and Cost Are Dot Products

Lesson 1.1.1 wrote a plan as a 0/1 vector $`x`$, one entry per project. The data become vectors
the same way: `capex` holds each project's cost and `npv` its value, in the same project order.

```python
capex = np.array([p.capex for p in tiny.projects])
npv = np.array([p.value for p in tiny.projects])


def to_vector(plan: set[str]) -> np.ndarray:
    return np.array([1 if pid in plan else 0 for pid in ids])
```

```text
x     = [1 1 0 0 1 1 0 0]
capex = [2150 2730 2470 3000  250 1970  290  580]
npv   = [1386  871  576 2120  123 1247  265  137]
capex * x = [2150 2730    0    0  250 1970    0    0]
capex @ x = 7,100   npv @ x = 3,627
```

`capex * x` multiplies entry by entry: a funded project keeps its cost and an unfunded one
becomes 0. Adding those products up is the **dot product**, written $`c^\top x`$ in math and `capex @ x`
in NumPy:

```math
c^\top x = \sum_{j} c_j\, x_j = 2150 \cdot 1 + 2730 \cdot 1 + 2470 \cdot 0 + \dots + 580 \cdot 0 = 7100
```

The $`\top`$ (*transpose*) only says the vector $`c`$ is laid on its side as a row so that it can
multiply the column $`x`$. Both numbers from lesson 1.1.1 come back: the plan costs $7,100k and is
worth $3,627k. The objective of the model is $`\text{npv}^\top x`$ and the one-period budget row is
$`\text{capex}^\top x \le 7390`$.

## A Budget Matrix Has One Row per Constraint and One Column per Decision

One budget per year means one dot product per year, each with its own coefficients: what each
project spends *in that year*. Stack those coefficient vectors as the rows of a matrix $`A`$ and
the budgets into a vector $`b`$. The vector $`b`$ is called the **right-hand side**, because each
row's limit stands to the right of its $`\le`$. A project's **cost profile** is what it spends in
each year of its work, in order: P003's is $980k in its first year and $1,490k in its second. In
this lesson every funded project starts in its earliest start year, so its cost profile fixes the
year each part of its cost lands in. (Section 6 lets the start year move.)

```python
def spend_matrix(portfolio: Portfolio) -> tuple[np.ndarray, np.ndarray]:
    """A[r, j]: what project j spends in year r if it starts as early as it can. b[r]: that year's budget."""
    A = np.zeros((len(portfolio.years), len(portfolio.projects)), dtype=int)
    for j, p in enumerate(portfolio.projects):
        for year, amount in p.spend(p.earliest_start).items():
            A[portfolio.years.index(year), j] = amount
    b = np.array([portfolio.budget[y] for y in portfolio.years])
    return A, b
```

```text
        P001  P002  P003  P004  P005  P006  P007  P008 |      b
2027        0     0   980     0   250     0   290   580 |   2300
2028     2150  2730  1490  2000     0   840     0     0 |   3280
2029        0     0     0  1000     0  1130     0     0 |   2310
```

Read it by column and by row. Column P003 is the project's cost profile laid on the calendar:
$980k in 2027 and $1,490k in 2028, which add up to its $2,470k capex. Row 2028 is the 2028 budget
constraint: every project that spends money in 2028, with how much. The entry in row $`r`$ and
column $`j`$ is written $`a_{rj}`$, and row $`r`$ of the matrix as a vector is $`a_r`$.

The shape is the point. A model's constraint matrix always has one **row per constraint** and one
**column per decision variable**: here 3 rows by 8 columns. The variables' order is the columns'
order, and it must be the same in $`A`$, in $`x`$ and in the objective vector.

## Ax ≤ b Checks Every Row at Once

The product $`Ax`$ takes the dot product of every row with $`x`$, giving one number per row: the
row's **activity**, here what the plan spends in each year. The comparison $`Ax \le b`$ then holds
row by row:

```math
Ax \le b \quad\Longleftrightarrow\quad a_r^\top x \le b_r \quad \text{for every row } r
```

```python
print("A @ x      =", A @ x)
print("b          =", b)
print("A @ x <= b =", A @ x <= b)
print("slack b - A @ x =", b - A @ x)
print("feasible:", bool(np.all(A @ x <= b)))
broken = np.flatnonzero(A @ x > b)                # the positions where the mask is True
print("broken rows:", broken)
print("over budget in:", [tiny.years[r] for r in broken])
```

```text
A @ x      = [ 250 5720 1130]
b          = [2300 3280 2310]
A @ x <= b = [ True False  True]
slack b - A @ x = [ 2050 -2440  1180]
feasible: False
broken rows: [1]
over budget in: [2028]
```

The plan that fit the $7,390k total does not fit the year budgets. P001, P002 and P006 all start
in 2028 and would spend $2,150k + $2,730k + $840k = $5,720k that year, against $3,280k. The
**slack** $`b - Ax`$ says by how much each row is satisfied: positive means room to spare, zero
means the row is exactly met (it is *tight*), and negative means the row is broken, here by
$2,440k. `np.all` turns the row-by-row answers into one: a plan is feasible only if every row holds.

An array of `True` and `False`, like `A @ x > b`, is a **boolean mask**: one yes/no per row.
`np.flatnonzero(mask)` returns the positions of its `True` entries, here `[1]`, the second row
(NumPy counts from 0). Those positions index anything in row order, such as the list of years, so
the check can say *which* rows break and not only *that* some do.

GridCap's money is in whole $k, so these sums are exact. With fractions they are not, and the
check needs a **tolerance**: a small number by which a row may miss and still count as met.

```python
def is_feasible(A: np.ndarray, b: np.ndarray, x: np.ndarray, tol: float = 1e-9) -> bool:
    return bool(np.all(A @ x <= b + tol))
```

```text
A @ x       = 0.30000000000000004
A @ x <= b  = False
with tol    = True
```

Here $`A = [0.1 \;\; 0.1 \;\; 0.1]`$, $`x`$ is all ones and $`b = 0.3`$. On paper the row is met
exactly. In binary floating point 0.1 has no exact form, the sum lands a hair above 0.3, and the
check without a tolerance rejects a plan that is fine.

<!-- practice 1 -->

## Every Linear Rule Fits Ax ≤ b: Flip ≥ Rows, Split = Rows

A matrix check is only as good as the rows in it, and lesson 1.1.1 had three more rules. Each is
**linear**: a sum of numbers times variables, compared with a number. Every linear rule can be
written as one or two rows of the form $`a^\top x \le b`$:

- **A ≤ row** goes in as it is. The alternatives rule $`x_{P006} + x_{P007} \le 1`$ is the row
  $`(0,0,0,0,0,1,1,0)`$ with right-hand side 1.
- **A ≥ row is a ≤ row times −1.** Multiplying both sides by −1 flips the inequality, so
  $`a^\top x \ge \beta`$ becomes $`-a^\top x \le -\beta`$.
- **An = row is two rows**, one ≤ and one ≥: $`x_{P002} = 1`$ becomes $`x_{P002} \le 1`$ and
  $`-x_{P002} \le -1`$.
- **Variables move to the left.** The parent rule $`x_{P004} \le x_{P003}`$ becomes
  $`x_{P004} - x_{P003} \le 0`$, a row with a 1 and a −1.

```python
for p in tiny.projects:
    if p.must_do:                                    # x = 1 is x <= 1 and -x <= -1
        leq(f"must_{p.project_id}_le", {p.project_id: 1}, 1)
        leq(f"must_{p.project_id}_ge", {p.project_id: -1}, -1)
    if p.parent:                                     # x_child <= x_parent
        leq(f"parent_{p.project_id}", {p.project_id: 1, p.parent: -1}, 0)
leq("alt_G006", {"P006": 1, "P007": 1}, 1)           # at most one of the group
```

Stacked under the budget rows, the whole tiny model is one $`A`$ and one $`b`$:

```text
row           P001  P002  P003  P004  P005  P006  P007  P008 |     b
budget_2027      0     0   980     0   250     0   290   580 |  2300
budget_2028   2150  2730  1490  2000     0   840     0     0 |  3280
budget_2029      0     0     0  1000     0  1130     0     0 |  2310
must_P002_le     0     1     0     0     0     0     0     0 |     1
must_P002_ge     0    -1     0     0     0     0     0     0 |    -1
parent_P004      0     0    -1     1     0     0     0     0 |     0
alt_G006         0     0     0     0     0     1     1     0 |     1
plan P001 P003 P004 breaks: ['budget_2028', 'must_P002_ge']
```

The check names the broken rows: the plan overspends 2028, and its `must_P002_ge` row reads
$`-0 \le -1`$, which is false because P002 is missing. Naming every row, as lesson 1.1.1 named its
rules, is what turns "infeasible" into a reason a planner can act on.

Why insist on one form? Because then one function checks any linear model, and because it is the
form linear-algebra results are stated in. Solvers accept ≥ and = rows directly, so you never have
to flip rows for them; the flipping is for your own checks and proofs.

<!-- practice 2 -->

## Checking Many Plans Is One Matrix Product

Lesson 1.1.1 checked all $`2^8 = 256`$ plans in a Python loop. Put every plan in as a column of a
matrix $`X`$ instead, and $`AX`$ computes every row's activity for every plan in one product:

```python
X = np.array(list(itertools.product([0, 1], repeat=len(ids)))).T     # 8 rows, 256 columns
activity = A @ X                                                      # 7 rows, 256 columns
feasible = np.all(activity <= b[:, None], axis=0)                     # one True/False per plan
values = np.where(feasible, npv @ X, -1)
best = X[:, np.argmax(values)]
```

```text
X: (8, 256)  A @ X: (7, 256)
feasible plans: 8 of 256
best: ['P002', 'P005', 'P007', 'P008'] value $1,396k
spend by year: {2027: 1120, 2028: 2730, 2029: 0}
```

Three NumPy details carry this. `b[:, None]` turns $`b`$ into a single column so that it is
compared with every column of the activity matrix (NumPy calls this *broadcasting*). `axis=0`
makes `np.all` look down each column, giving one verdict per plan. `np.where` gives every
infeasible plan a value of −1, so `np.argmax` can only pick a feasible one.

The answer is worth reading. With yearly budgets and every project starting as early as it can,
only 8 of the 256 plans are allowed, and the best is worth $1,396k, against $3,627k with one total
budget. The must-do P002 alone spends $2,730k of 2028's $3,280k, so almost nothing else fits
in 2028. P001 and P002 could start in 2029 instead; a model where they may is what lesson 6.4.1 builds.

The product is not magic: it does the same multiplications as the loop. Its value is that the
model is now data, $`A`$ and $`b`$, and a check is one line that works for any model of this
form, with 7 rows or 7,000.

## The Model

The selection model of lesson 1.1.1 with the single budget replaced by yearly budgets, and every
rule written as rows of $`Ax \le b`$.

**Sets.** $`P`$ the projects; $`Y`$ the years (2027 to 2029 on GridCap tiny); $`M \subseteq P`$ the
must-do projects; $`C \subseteq P`$ the child projects, each with parent $`p(c)`$; $`\mathcal{G}`$
the alternative groups.

**Parameters.** $`\text{npv}_j`$, the value of project $`j`$ ($k); $`a_{yj}`$, what project $`j`$
spends in year $`y`$ if it starts in its earliest start year ($k); $`B_y`$, the budget of year
$`y`$ ($k).

**Variables.** $`x_j \in \{0, 1\}`$ for each $`j \in P`$: 1 if project $`j`$ is funded.

**Objective.**

```math
\max \; \sum_{j \in P} \text{npv}_j\, x_j
```

**Constraints.**

```math
\begin{aligned}
\sum_{j \in P} a_{yj}\, x_j &\le B_y && \forall y \in Y && \text{(budget}_y) \\
x_i &\le 1 && \forall i \in M && \text{(must}_i\text{\_le)} \\
-x_i &\le -1 && \forall i \in M && \text{(must}_i\text{\_ge)} \\
x_c - x_{p(c)} &\le 0 && \forall c \in C && \text{(parent}_c) \\
\sum_{j \in g} x_j &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

In matrix form, with $`n = |P|`$ columns and one row of $`A`$ per labelled constraint:

```math
\max \; \text{npv}^\top x \quad \text{subject to} \quad Ax \le b, \quad x \in \{0, 1\}^n
```

On GridCap tiny its optimum is P002, P005, P007 and P008, worth $1,396k.

## Summary

- **A plan is a vector, and its value and cost are dot products.** $`\text{npv}^\top x`$ is the
  objective; $`\text{capex}^\top x`$ is the plan's total cost.
- **A budget matrix has one row per constraint and one column per decision.** Column $`j`$ is
  project $`j`$ across every rule; row $`r`$ is one rule across every project.
- **Ax ≤ b checks every row at once.** The slack $`b - Ax`$ shows which rows hold, which are tight
  and which are broken, and with fractional data the check needs a tolerance.
- **Every linear rule fits Ax ≤ b.** Multiply a ≥ row by −1, split an = row into two, and move
  variables to the left.
- **Checking many plans is one matrix product.** Plans as the columns of $`X`$ give $`AX`$, every
  row for every plan.

## Reference

| Math | NumPy | Meaning |
| --- | --- | --- |
| $`c^\top x`$ | `c @ x` | dot product: $`\sum_j c_j x_j`$ |
| $`c_j x_j`$ for each $`j`$ | `c * x` | entry-by-entry product |
| $`Ax`$ | `A @ x` | one dot product per row of $`A`$: each row's activity |
| $`Ax \le b`$ | `np.all(A @ x <= b + tol)` | every row holds, within a tolerance |
| $`b - Ax`$ | `b - A @ x` | slack: room left in each row (negative if broken) |
| $`AX`$ | `A @ X` | every row's activity for every plan (plans as columns) |
| — | `b[:, None]` | $`b`$ as a column, compared with every column |
| — | `np.all(M, axis=0)` | one verdict per column of `M` |
| — | `np.flatnonzero(mask)` | positions of the `True` entries of a mask, e.g. the broken rows |

| Rule as written | As rows of $`Ax \le b`$ |
| --- | --- |
| $`a^\top x \le \beta`$ | $`a^\top x \le \beta`$ |
| $`a^\top x \ge \beta`$ | $`-a^\top x \le -\beta`$ |
| $`a^\top x = \beta`$ | $`a^\top x \le \beta`$ and $`-a^\top x \le -\beta`$ |
| $`x_c \le x_p`$ | $`x_c - x_p \le 0`$ |

**Further reading:** [MathOpt `model.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/model.proto) (how MathOpt stores each linear row with a lower and an upper bound, so ≥ and = rows need no flipping); [NumPy `matmul`](https://numpy.org/doc/stable/reference/generated/numpy.matmul.html) (what `@` does for vector-vector, matrix-vector and matrix-matrix products, and how it differs from `*`); [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) (the shape rule behind `b[:, None]`); [NumPy `flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html) (positions of the nonzero entries, as used for broken rows); [Python tutorial: floating-point arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html) (why 0.1 + 0.1 + 0.1 is not 0.3, and comparing with a tolerance).

## Challenges

1. Add a row that says P008 must start no earlier than 2029 when it is funded. Can it be written
   as a row of $`Ax \le b`$ with the variables of this lesson? What would it need?
2. A planner proposes "spend at least $1,000k in 2027". Write it as a row of $`Ax \le b`$ and
   predict whether the best plan above still satisfies it.
3. `all_plans.py` builds a 256-column `X`. How many columns would the small portfolio need, and
   how much memory would that take at one byte per entry?

## Design Note: Name Every Row

The matrix form throws names away: row 4 is just row 4. Keep a list of row names next to $`A`$,
in the same order, from the start. A broken row then reports itself as `must_P002_ge`, a solver
log can be matched to the rule it is about, and when section 9 asks *which* rules make a model
infeasible, the answer is a list of names a planner can read rather than a list of numbers.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**plan_vectors.py.** The plan, costs and values as vectors, and the dot products that give the plan's cost and value (*A Plan Is a Vector*). *Try:* Add P008 to the plan. Predict both dot products before you run it.

- Program: [plan_vectors.py](src/plan_vectors.py)

**budget_matrix.py.** Builds the yearly budget matrix and checks the lesson 1.1.1 plan against it (*A Budget Matrix Has One Row per Constraint* and *Ax ≤ b Checks Every Row at Once*). *Try:* Change the plan `x` to fund only P002, P005 and P008. Which rows are tight, and which have slack?

- Program: [budget_matrix.py](src/budget_matrix.py)

**tolerance.py.** A row that is met exactly on paper and missed by a hair in floating point (*Ax ≤ b Checks Every Row at Once*). *Try:* Set `tol` to `0`. Predict what `is_feasible` returns.

- Program: [tolerance.py](src/tolerance.py)

**rules_matrix.py.** Writes the must-do, parent and alternatives rules as rows and stacks them under the budget rows (*Every Linear Rule Fits Ax ≤ b*). *Try:* Change the alternatives row to "exactly one of P006 and P007". How many rows does it need?

- Program: [rules_matrix.py](src/rules_matrix.py)

**all_plans.py.** Checks all 256 plans with one matrix product and picks the best feasible one (*Checking Many Plans Is One Matrix Product*). *Try:* Raise the 2028 budget in `b` by 2,000 before the check. Predict whether the best plan changes.

- Program: [all_plans.py](src/all_plans.py)
