# 6.1.4 Linearizing Binary × Binary and Binary × Bounded Continuous

Two refinements reach GridCap's planners for the small portfolio. Field operations points out that
two distribution projects in the same region, funded together, share one crew mobilization, and
values that at $150k a pair; and that two transmission projects in the same region, funded
together, need their outages coordinated, at a cost of $400k a pair. Both say "for each pair funded
together", which is a product: $`x_a\,x_b`$ is 1 exactly when both are funded. And the vegetation
contract now lets GridCap choose one clearance width $`q`$, between 3 and 6 metres, for every funded
vegetation project; a project's cost and value depend on the width only if it is funded, which is
the product $`x_i\,q`$ of a binary and a continuous variable. A MILP allows neither product. This
lesson replaces each by a new variable and linear rows that give exactly the same plans, in four
rules.

GridCap is a fictional utility's portfolio, generated for this course; the savings, costs and the
clearance-width contract are invented for this lesson.

## A Product of Two Binaries Is Their AND, Written as Three Rows

Multiply two 0/1 numbers and you get 1 only when both are 1:

| $`x_a`$ | $`x_b`$ | $`x_a x_b`$ |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

That is the truth table of AND, so $`x_a x_b`$ is "$`a`$ and $`b`$", and lesson 6.1.2 already wrote
AND as a value: a new binary $`z_{ab}`$ with

```math
z_{ab} \le x_a, \qquad z_{ab} \le x_b, \qquad z_{ab} \ge x_a + x_b - 1
```

**Linearizing** a product means exactly this: replace the nonlinear term by a new variable, and add
linear rows that force the variable to equal the term at every 0/1 point. The model is then linear
again, and every plan it allows is a plan the product model allowed, with the same value.

Why not leave the product in? The objective $`\sum_i \text{npv}_i x_i + 150 \sum_{(a,b)} x_a x_b`$
is **quadratic** (it has products of two variables), and a MILP solver is not obliged to accept
that. The program writes the bonus exactly that way, then hands the model to HiGHS and to SCIP, the solver
MathOpt reaches as `GSCIP`:

```python
sel = build(small)
npv = sel.model.objective.as_linear_expression()
sel.model.maximize(npv + sum(BONUS * sel.x[a] * sel.x[b] for a, b in pairs))
try:
    solve_highs(sel.model, EXACT)
except Exception as error:                    # OR-Tools 9.15 hides the reason in __context__
    print("HiGHS, product in the objective:", error.__context__)
scip = mathopt.solve(sel.model, mathopt.SolverType.GSCIP, params=EXACT)
```

Then it replaces each product by its $`z`$ and solves the linear model with HiGHS:

```python
for a, b in pairs:
    z[a, b] = model.add_binary_variable(name=f"z_{a}_{b}")
    model.add_linear_constraint(z[a, b] <= x[a], name=f"z_le_{a}_{b}")
    model.add_linear_constraint(z[a, b] <= x[b], name=f"z_le_{b}_{a}")
    model.add_linear_constraint(z[a, b] >= x[a] + x[b] - 1, name=f"z_ge_{a}_{b}")
model.maximize(model.objective.as_linear_expression() + sum(BONUS * v for v in z.values()))
```

```text
22 pairs of same-region distribution projects
HiGHS, product in the objective: MathOpt does not currently support Highs models with quadratic objectives [UNIMPLEMENTED]
SCIP, product in the objective: OPTIMAL, $26,064k
HiGHS, product replaced by z: OPTIMAL, $26,064k, 12 pairs funded together
```

HiGHS, the course's default solver, refuses the quadratic objective through MathOpt. (OR-Tools
9.15 raises an `AttributeError` that hides the solver's message, as lesson 2.4.1 noted for other
refusals; the real reason is on the exception's `__context__`.) SCIP accepts it and finds
$26,064k. The linearized model gives HiGHS a plain MILP and reaches the same $26,064k, with 12 pairs
funded together. Linearizing is what makes the model portable: the result is a plain MILP, the
kind of model every MILP solver of section 5 is built for.

The cost is one variable and three rows per pair. 22 pairs is small; all pairs of 400 projects
would be about 80,000, so in practice the pairs come from data (the same region, the same feeder),
never from every combination.

## The Sign of the Product's Term Decides Which Rows It Needs

Lesson 6.1.2 showed that a variable pinned from one side may be enough, depending on which way the
solver wants to move it. Products are the most common place this matters. The program solves both
refinements three ways: with all three rows per pair, with only the two rows that push $`z`$ down
($`z \le x_a`$, $`z \le x_b`$), and with only the row that pushes it up
($`z \ge x_a + x_b - 1`$). For each, it compares what the solver *claims* (its objective, which
trusts $`z`$) with what the plan is really worth (NPV plus the bonus or cost of the pairs the plan
actually funds):

```text
bonus +$150k per distribution pair (22 pairs)
  rows down+up  claims $26,064k with 12 pairs; the plan has 12 pairs and is worth $26,064k
  rows down     claims $26,064k with 12 pairs; the plan has 12 pairs and is worth $26,064k
  rows up       claims $28,636k with 22 pairs; the plan has  2 pairs and is worth $25,636k
cost -$400k per transmission pair (23 pairs)
  rows down+up  claims $24,030k with  1 pair; the plan has  1 pair and is worth $24,030k
  rows down     claims $25,336k with  0 pairs; the plan has  7 pairs and is worth $22,536k
  rows up       claims $24,030k with  1 pair; the plan has  1 pair and is worth $24,030k
```

- **A reward on $`z`$ (a positive term in a maximization) makes the solver push $`z`$ up**, so the
  rows that push it down are the ones that hold it to the truth. With them alone the answer is
  exact. Without them, the solver sets all 22 $`z`$ to 1, claims $28,636k, and returns a plan that
  funds only 2 real pairs and is worth $25,636k, $428k less than the true optimum.
- **A cost on $`z`$ (a negative term in a maximization) makes the solver push $`z`$ down**, so the
  row that pushes it up is the one that matters. Without it, the solver sets every $`z`$ to 0,
  pays no coordination cost, and returns the plan that ignores it: 7 transmission pairs, really
  worth $22,536k, reported as $25,336k.

The same holds when the product sits in a row instead of the objective: a product in a $`\le`$ row
with a positive coefficient (a cost in a budget) is pushed down and needs the "up" row; a product
whose coefficient lowers the spend (a discount) is pushed up and needs the "down" rows. Writing all
three rows is always correct. Dropping a side is an optimization that is only safe while every use
of $`z`$ pushes the same way.

A product of more than two binaries is the AND of all of them: $`x_a x_b x_c`$ becomes $`z`$ with
$`z \le x_a`$, $`z \le x_b`$, $`z \le x_c`$ and $`z \ge x_a + x_b + x_c - 2`$, from the table in
lesson 6.1.2.

<!-- practice 1 -->

## A Binary Times a Bounded Continuous Variable Takes Four Rows

The clearance width $`q`$ is continuous: any value from 3 to 6 metres. Write the contract's terms
for one vegetation project $`i`$ with GridCap's figures at the standard 4-metre width,
$`\text{capex}_i`$ and $`\text{npv}_i`$: its cost is half fixed and half proportional to the width,
$`\text{capex}_i\,(\tfrac12 + \tfrac{q}{8})`$, and its value is proportional to the width,
$`\text{npv}_i\,\tfrac{q}{4}`$. Both equal GridCap's figures at $`q = 4`$. A funded project pays
and earns them; an unfunded one nothing. So its contribution to the budget row is

```math
\tfrac12\,\text{capex}_i\,x_i + \tfrac18\,\text{capex}_i\,x_i\,q
```

and $`x_i\,q`$ is a product of a binary and a continuous variable. Replace it by a new continuous
variable $`w_i`$, the width actually cleared on project $`i`$, which must be 0 when $`x_i = 0`$ and
$`q`$ when $`x_i = 1`$. With $`L = 3`$ and $`U = 6`$ the bounds of $`q`$, four rows do it:

```math
\begin{aligned}
w_i &\le U\,x_i && \text{(1)} \\
w_i &\le q - L\,(1 - x_i) && \text{(2)} \\
w_i &\ge L\,x_i && \text{(3)} \\
w_i &\ge q - U\,(1 - x_i) && \text{(4)}
\end{aligned}
```

Read them for each value of $`x_i`$:

- **$`x_i = 0`$.** Row (1) says $`w_i \le 0`$ and row (3) says $`w_i \ge 0`$, so $`w_i = 0`$. Rows
  (2) and (4) become $`w_i \le q - L`$ and $`w_i \ge q - U`$; since $`L \le q \le U`$, the first
  right side is at least 0 and the second at most 0, so both hold for $`w_i = 0`$ and cut nothing.
- **$`x_i = 1`$.** Rows (2) and (4) say $`w_i \le q`$ and $`w_i \ge q`$, so $`w_i = q`$. Rows (1)
  and (3) become $`w_i \le U`$ and $`w_i \ge L`$, which $`w_i = q`$ already satisfies.

In each case two rows do the pinning and two are switched off by the bounds, the same trick as the
switch rows of lesson 6.1.3. These four rows are known as the **McCormick** rows of the product;
for a binary $`x`$ they are exact. Rows (1) and (2) push $`w`$ down, rows (3) and (4) push it up:

```python
def product_rows(model, w, x, q, low=LOW, high=HIGH, which=("down", "up")):
    """The rows that make w = x * q when x is binary and low <= q <= high."""
    if "down" in which:
        model.add_linear_constraint(w <= high * x)
        model.add_linear_constraint(w <= q - low * (1 - x))
    if "up" in which:
        model.add_linear_constraint(w >= low * x)
        model.add_linear_constraint(w >= q - high * (1 - x))
```

The program fixes $`x`$ and $`q`$, then asks HiGHS for the smallest and the largest $`w`$ the rows
allow ($`w`$ is declared between 0 and 6):

```text
x  q   | x*q | four rows | 'down' rows only | 'up' rows only
0  3.0 | 0.0 | 0.0       | 0.0              | 0.0 to 6.0
0  4.5 | 0.0 | 0.0       | 0.0              | 0.0 to 6.0
0  6.0 | 0.0 | 0.0       | 0.0              | 0.0 to 6.0
1  3.0 | 3.0 | 3.0       | 0.0 to 3.0       | 3.0 to 6.0
1  4.5 | 4.5 | 4.5       | 0.0 to 4.5       | 4.5 to 6.0
1  6.0 | 6.0 | 6.0       | 0.0 to 6.0       | 6.0
```

With all four rows, $`w`$ has one value and it is $`x\,q`$. As with binaries, each side alone
leaves $`w`$ free in one direction, and the same reasoning picks the side to keep: here $`w_i`$
earns value in the objective and spends budget, so the solver would like it larger for one reason
and smaller for the other, and the model needs all four.

The GridCap model puts each funded vegetation project's cost and value on $`w_i`$:

```python
w = {i: model.add_variable(lb=0, ub=high_in_rows, name=f"w_{i}") for i in vegetation}
for i in vegetation:
    product_rows(model, w[i], x[i], q, high=high_in_rows)
    p = portfolio.project(i)
    sel.budget.set_coefficient(x[i], p.capex / 2)                 # fixed half of the cost
    sel.budget.set_coefficient(w[i], p.capex / 2 / STANDARD)      # cost per metre of width
```

and solves it with $`q`$ fixed at each whole width, then with $`q`$ left to the solver:

```text
GridCap small, one clearance width for every funded vegetation project
  q fixed at 3: q = 3.000, NPV $25,183.8k, 5 vegetation projects
  q fixed at 4: q = 4.000, NPV $25,336.0k, 7 vegetation projects
  q fixed at 5: q = 5.000, NPV $25,657.0k, 9 vegetation projects
  q fixed at 6: q = 6.000, NPV $25,847.5k, 8 vegetation projects
  q chosen   : q = 5.897, NPV $25,904.9k, 10 vegetation projects
```

At $`q = 4`$ every cost and value equals GridCap's own, and the model returns the familiar
$25,336k: a check that the rows change nothing when the width is the standard one. Left free, the
solver picks 5.897 metres, a width no one would have tried by hand, and funds 10 vegetation
projects at it, $568.9k more than the standard width.

When the continuous variable belongs to one project only (each project has its own amount $`q_i`$,
used nowhere else), there is nothing to multiply: define the amount as already switched off,
$`L\,x_i \le q_i \le U\,x_i`$, and use $`q_i`$ directly. The four rows are for a continuous variable
that exists whether or not the project is funded and is shared, like the one width of a contract.

CP-SAT, OR-Tools' constraint solver (lessons 4.4.1 to 4.4.4), writes both products of this lesson as logic
instead of rows. Two OR-Tools samples show how. `boolean_product_sample_sat.py` writes
$`p = x\,y`$ for Booleans as one clause and two implications: "$`x`$ and $`y`$ implies $`p`$" is the
clause "not $`x`$, or not $`y`$, or $`p`$", the row that pushes $`p`$ up, and "$`p`$ implies $`x`$",
"$`p`$ implies $`y`$" are the two rows that push it down. `bool_and_int_var_product_sample_sat.py`
writes $`p = b\,x`$ for a Boolean $`b`$ and an integer $`x`$ as two equalities, each enforced by
one value of $`b`$. `cpsat_products.py` builds both, with $`x`$ from 1 to 4 in the second, and lists
every solution:

```python
model.add_bool_or(~x, ~y, p)        # x and y implies p
model.add_implication(p, x)         # p implies x
model.add_implication(p, y)         # p implies y
```

```python
model.add(p == x).only_enforce_if(b)
model.add(p == 0).only_enforce_if(~b)
```

```text
p = x * y, all solutions (x, y, p): [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)]
p = b * x, 8 solutions (b, x, p): [(0, 1, 0), (0, 2, 0), (0, 3, 0), (0, 4, 0), (1, 1, 1), (1, 2, 2), (1, 3, 3), (1, 4, 4)]
```

The first list is the AND table, so $`p`$ is pinned on every line. The second has $`p = 0`$
whenever $`b = 0`$ and $`p = x`$ whenever $`b = 1`$: the product, with no $`L`$ or $`U`$ written in
any row. The bounds have not gone away, though. CP-SAT gives every variable a finite domain, and
$`p`$'s domain, 0 to 4, is $`x`$'s domain with 0 added, as the sample builds it. In a MILP solver
the same knowledge goes into the four rows; in CP-SAT it goes into the domains.

## The Bounds in the Rows Are Part of the Formulation

The four rows are exact only because $`q`$ has a lower bound $`L`$ and an upper bound $`U`$. With no
finite upper bound there is no number to write in row (1), and no linear form exists. The bound in
the rows does not have to be the tightest one to be *correct*: any $`U' \ge U`$ still gives
$`w = x\,q`$ at every 0/1 point. But the rows are also what the LP relaxation sees, and there the
number matters. The program solves the width model's LP relaxation (GLOP) and MILP (HiGHS) with
the true bound 6 written in the rows, with looser bounds, and with 5, a bound *below* the true one:

```text
bound in rows | LP bound     | MILP        | q in the MILP
            6 | $25,983.20k | $25,904.9k | 5.897
           60 | $26,043.95k | $25,904.9k | 5.897
          600 | $26,051.83k | $25,904.9k | 5.897
            5 | $25,712.13k | $25,657.0k | 5.000
bound 60, LP's fractional vegetation projects (x, w): {'P004': (0.053, 3.16), 'P008': (0.053, 3.16), 'P012': (0.053, 3.16), 'P018': (0.053, 3.16), 'P020': (0.053, 3.16)}
```

- **A looser bound keeps the MILP and weakens the LP.** With 60, the MILP is unchanged, but the LP
  relaxation funds 0.053 of five projects at a width of 3.16 metres each: row (1) allows
  $`w \le 60\,x`$, about 3.16 at $`x = 0.053`$, so a twentieth of a project is cleared at more than half the
  full width. The LP bound rises from $25,983.20k to $26,043.95k, further from the true $25,904.9k,
  and with 600 further still. Lesson 3.1.2 explained why a looser bound means a harder search.
- **A bound below the true one is wrong, not loose.** With 5, row (4) for a funded project reads
  $`w \ge q`$ while row (1) reads $`w \le 5`$, so $`q`$ can no longer exceed 5. The model silently
  loses every plan with a wider clearance, and the "optimum" drops to $25,657.0k, the value of the
  best plan at $`q = 5`$.

So take the bound from the data (here the contract's 6 metres), never a large round number "to be
safe", and never a guess that might be too small. Lessons 6.2.1 to 6.2.4 make choosing such numbers a
method of their own: lesson 6.2.1 derives them from bounds, and lesson 6.2.2 measures what a loose one costs.

<!-- practice 2 -->

## The Model

The selection model on GridCap small with this lesson's variables and rows marked. `pair_products.py`
solves it with the pair terms and without the width ($`q`$ fixed at 4, so $`w_i = 4x_i`$);
`clearance_width.py` with the width and without the pair terms.

**Sets.** $`P`$ the candidate projects; $`M`$, $`C`$ and $`\mathcal{G}`$ the must-do projects, the
child projects (parent $`p(c)`$) and the alternative groups; $`V \subseteq P`$ the vegetation
projects; $`E_D`$ the pairs of distribution projects in the same region (22); $`E_T`$ the pairs of
transmission projects in the same region (23).

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ at the standard width ($k); $`B = 38{,}390`$
($k); $`\beta = 150`$, the bonus per distribution pair ($k); $`\gamma = 400`$, the cost per
transmission pair ($k); $`L = 3`$ and $`U = 6`$, the clearance width's bounds (m); $`4`$, the
standard width (m).

**Variables.**

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(1 if project } i \text{ is funded)} \\
& z_{ab} \in \{0, 1\} && \forall (a, b) \in E_D \cup E_T && \text{(}= x_a x_b\text{)} \quad \leftarrow \text{this lesson} \\
& L \le q \le U && && \text{(clearance width, m)} \quad \leftarrow \text{this lesson} \\
& 0 \le w_i \le U && \forall i \in V && \text{(}= x_i\, q\text{)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P \setminus V} \text{npv}_i\, x_i + \sum_{i \in V} \frac{\text{npv}_i}{4}\, w_i
+ \beta \sum_{(a,b) \in E_D} z_{ab} - \gamma \sum_{(a,b) \in E_T} z_{ab}
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P \setminus V} \text{capex}_i\, x_i + \sum_{i \in V} \Big(\frac{\text{capex}_i}{2}\, x_i + \frac{\text{capex}_i}{8}\, w_i\Big) &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
z_{ab} &\le x_a,\quad z_{ab} \le x_b && \forall (a,b) \in E_D \cup E_T && \text{(z\_le)} \quad \leftarrow \text{this lesson} \\
z_{ab} &\ge x_a + x_b - 1 && \forall (a,b) \in E_D \cup E_T && \text{(z\_ge)} \quad \leftarrow \text{this lesson} \\
w_i &\le U\,x_i,\quad w_i \le q - L\,(1 - x_i) && \forall i \in V && \text{(rows 1, 2)} \quad \leftarrow \text{this lesson} \\
w_i &\ge L\,x_i,\quad w_i \ge q - U\,(1 - x_i) && \forall i \in V && \text{(rows 3, 4)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

## Summary

- **A product of two binaries is their AND, written as three rows.** Replace $`x_a x_b`$ by a
  binary $`z`$ with $`z \le x_a`$, $`z \le x_b`$, $`z \ge x_a + x_b - 1`$; HiGHS refuses the
  product itself.
- **The sign of the product's term decides which rows it needs.** A reward needs the rows that push
  $`z`$ down, a cost the row that pushes it up; without the right side the solver claims value the
  plan does not have.
- **A binary times a bounded continuous variable takes four rows.** With $`L \le q \le U`$,
  $`w = x\,q`$ is exact through the four McCormick rows; a per-project amount needs only
  $`L\,x \le q \le U\,x`$.
- **The bounds in the rows are part of the formulation.** A loose bound weakens the LP bound; a
  bound below the true one cuts off real plans.

## Reference

| Product | New variable | Rows |
| --- | --- | --- |
| $`x_a x_b`$ | $`z \in \{0,1\}`$ | $`z \le x_a`$, $`z \le x_b`$, $`z \ge x_a + x_b - 1`$ |
| $`x_1 x_2 \cdots x_n`$ | $`z \in \{0,1\}`$ | $`z \le x_k`$ for each $`k`$, $`z \ge \sum_k x_k - (n-1)`$ |
| $`x\,q`$, $`L \le q \le U`$ | $`w`$ continuous | $`w \le U x`$, $`w \le q - L(1-x)`$, $`w \ge L x`$, $`w \ge q - U(1-x)`$ |
| $`x\,q_i`$, $`q_i`$ used only by this project | none | $`L\,x \le q_i \le U\,x`$ |

| The product's term | Rows that matter |
| --- | --- |
| a reward, or a discount in a $`\le`$ row | those that push the new variable down |
| a cost, or a charge in a $`\le`$ row | those that push it up |
| both, or not sure | all of them |

| CP-SAT | Product |
| --- | --- |
| `add_bool_or(~x, ~y, p)`, `add_implication(p, x)`, `add_implication(p, y)` | $`p = x\,y`$, Booleans |
| `add(p == x).only_enforce_if(b)`, `add(p == 0).only_enforce_if(~b)` | $`p = b\,x`$, $`p`$'s domain $`x`$'s plus 0 |

**Further reading:** [CP-SAT sample boolean_product_sample_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/boolean_product_sample_sat.py) (the product of two Booleans as a clause and two implications, with every solution listed); [CP-SAT sample bool_and_int_var_product_sample_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/bool_and_int_var_product_sample_sat.py) (a Boolean times an integer variable through two enforced equalities, the product's domain built from the integer's); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (MathOpt models may hold quadratic objectives, and the solvers it calls decide whether they accept them, as HiGHS's refusal shows); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2: a fixed cost as a capacity row $`x \le B y`$ on a binary, the bound-times-binary idea behind rows (1) and (3)).

## Challenges

1. A third refinement: two vegetation projects in the same region funded together save $40k. Write
   the rows, and say which you can drop.
2. Product of a binary and an *integer* $`n \in \{0, \dots, 5\}`$: does the four-row form still
   work? Check the case $`x = 1`$, $`n = 3`$.
3. In `clearance_width.py`, allow widths from 2 to 8 metres. Predict whether the chosen width moves
   to a bound.

## Design Note: Linearize Where the Model Is Built, Not in the Data

A product could be avoided by precomputing: list every width the contract allows (3, 3.5, 4, …)
and give each project one binary per width. That trades a continuous decision for a grid and many
more binaries, and it misses 5.897 metres. The opposite mistake is to compute $`x_i q`$ after the
solve ("we'll multiply later"), which leaves the solver choosing $`q`$ without seeing what it
costs. Keep the products in the model, written as the rows of this lesson, in one helper such as
`product_rows`, so every use of a product gets the same exact rows and the same bounds, and a
reviewer has one place to check them.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**quadratic_refused.py.** Writes the distribution-pair bonus as products, shows HiGHS refusing it
and SCIP solving it, then linearizes it for HiGHS (*A Product of Two Binaries Is Their AND*).
*Try:* Raise `BONUS` to 600. Predict whether more pairs are funded together.

- Program: [quadratic_refused.py](src/quadratic_refused.py)

**pair_products.py.** Solves the pair bonus and the pair cost with all rows, the "down" rows only
and the "up" row only (*The Sign of the Product's Term Decides Which Rows It Needs*). *Try:* Change
the transmission cost to a bonus of $400k. Predict which variant claims too much.

- Program: [pair_products.py](src/pair_products.py)

**clearance_width.py.** Checks the four product rows at fixed points, then solves GridCap small with
one clearance width (*A Binary Times a Bounded Continuous Variable Takes Four Rows*). *Try:* Make
the cost fully proportional to the width (`p.capex / STANDARD` per metre, no fixed half). Predict
the chosen width.

- Program: [clearance_width.py](src/clearance_width.py)

**loose_bound.py.** Solves the width model's LP relaxation and MILP with the true, looser and too
small bounds in the rows (*The Bounds in the Rows Are Part of the Formulation*). *Try:* Use 6.5 as
the bound. Predict whether the MILP changes.

- Program: [loose_bound.py](src/loose_bound.py)

**cpsat_products.py.** The two products in CP-SAT, adapted from OR-Tools' Boolean-product and
Boolean-times-integer samples, with every solution listed (*A Binary Times a Bounded Continuous
Variable Takes Four Rows*). *Try:* Drop `model.add_implication(p, y)`. Predict which extra solution
appears, and which side of the AND it lost.

- Program: [cpsat_products.py](src/cpsat_products.py)
