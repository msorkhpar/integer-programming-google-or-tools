# 6.2.1 Deriving Big-M From Bounds

GridCap's crews are short. Each program (transmission, distribution, vegetation) has a fixed number
of crew-months in house for each year, and the five-year plan for the small portfolio asks for more
than that in some years. The planners have a way out: a program may hire an outside contractor for a
year, at a fee, and then use as many crew-months as its projects need. So the rule is "a program
uses at most its own crews in a year, **unless** it hires a contractor that year". A rule with an
"unless" in it is a constraint that a yes/no decision can switch off. The standard way to write
one in a linear model is a **big-M** constraint, and the one thing you must get right in it is the
number $`M`$. This lesson derives $`M`$ from the data, in four rules, from the cheapest safe value
to the smallest one that is still correct.

GridCap is fictional, and so is the contractor: its fee is this module's own parameter, $300k per
program and year.

## The Model

The model chooses which projects of GridCap small to fund and in which year each one starts. Its
project rows are a multi-period planning model that lessons 6.4.1 to 6.4.4 build step by step, later in this
section; this lesson adds two things to it: a crew row for every program and year, and a binary
that switches that row off. Everything about crews is new. The rest is stated here, with each piece
defined right below the constraints, enough to read the crew rows; lessons 6.4.1 and 6.4.3 give
the full treatment.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`P^{\text{must}} \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative
groups, each a set of projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag
$`L_c`$ years; $`G`$ the programs (transmission, distribution, vegetation) and $`P_g \subseteq P`$
the projects of program $`g`$. For a program $`g`$ and a year $`y`$, $`A_{g,y}`$ is the set of pairs
$`(i, t)`$ with $`i \in P_g`$ and $`t \in T_i`$ such that project $`i`$, started in year $`t`$, is
still being worked on in year $`y`$ ($`t \le y \le t + d_i - 1`$, with $`d_i`$ its years of work).

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k); $`B_y`$, the budget of
year $`y`$ ($k); $`\kappa_i`$, the crew-months project $`i`$ needs in each year it is worked on;
$`K_{g,y}`$, the crew-months program $`g`$ has in house in year $`y`$; $`F = 300`$, the
contractor's fee for one program and year ($k); $`M_{g,y} \ge 0`$, the big-M of crew row
$`(g, y)`$, in crew-months. This lesson is about how to choose it.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$. $`h_{g,y} \in \{0, 1\}`$ for every $`g \in G`$ and $`y \in Y`$: program $`g`$
hires a contractor in year $`y`$.

**Objective.** The NPV of the plan, less the contractor fees:

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \;-\; F \sum_{g \in G} \sum_{y \in Y} h_{g,y}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus P^{\text{must}} && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in P^{\text{must}} && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{(i,t) \in A_{g,y}} \kappa_i\, x_{i,t} &\le K_{g,y} + M_{g,y}\, h_{g,y} && \forall g \in G,\ y \in Y && \text{(crews}_{g,y}) \quad \leftarrow \text{new}
\end{aligned}
```

| Label | Row name in `crew_model.py` |
| --- | --- |
| once$`_i`$, must$`_i`$ | `once_P017`, `must_P003` |
| alt$`_g`$ | `alt_G030` |
| after$`_{c,t}`$ | `after_P023_2029` |
| budget$`_y`$ | `budget_2029` |
| crews$`_{g,y}`$ | `crews_transmission_2029` |

What each piece means, in short:

- **Start variables.** $`x_{i,t} = 1`$ says "project $`i`$ starts in year $`t`$". One binary per
  project and start year turns the question "when?" into a set of yes/no questions. A project
  started in $`t`$ runs for $`d_i`$ years and spends $`c_{i,0}`$ in year $`t`$, $`c_{i,1}`$ in year
  $`t + 1`$, and so on, which is why the budget row of year $`y`$ reads $`c_{i,\,y-t}`$.
- **Windows.** $`T_i`$ is project $`i`$'s **window**, the start years the planners allow for it. A
  year outside the window gets no variable at all, so the model cannot start the project then.
- **`started`.** The sum $`\sum_{t \in T_i} x_{i,t}`$ is 1 if project $`i`$ is funded (in some
  year) and 0 if not. The code names it `started(i)`, and the once, must and alt rows are written
  with it: started at most once, exactly once, at most one project of the group.
- **After rows.** A child project $`c`$ (P023, say) may start only $`L_c`$ or more years after its
  parent $`p(c)`$. Row after$`_{c,t}`$ reads "the child can have started by year $`t`$ only if the
  parent had started by year $`t - L_c`$": its left side counts the child's starts up to $`t`$, its
  right side the parent's starts up to $`t - L_c`$, and there is one such row for each $`t`$ in the
  child's window.
- **Active set.** $`A_{g,y}`$, defined above, lists the start choices of program $`g`$'s projects
  that keep a crew busy in year $`y`$. The crew row adds up $`\kappa_i`$ over the chosen ones.

Lesson 6.4.1 builds start variables, windows and `started` in full, and lesson 6.4.3 derives the
after rows and shows why they are written one per year.

The left side of a crew row is the program's **crew use** in that year. `crew_use` builds it: every
start year that keeps a project busy in year $`y`$ adds that project's crew-months.

```python
def active(project, t: int, year: int) -> bool:
    """Is a project that starts in year t being worked on in `year`?"""
    return t <= year < t + project.duration


def crew_use(portfolio: Portfolio, x: dict) -> dict[tuple[str, int], mathopt.LinearExpression]:
    """Crew-months each program uses in each year: every active project needs its crew_months."""
    use = {(g, y): mathopt.LinearExpression() for g in PROGRAMS for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for y in portfolio.years:
                if active(p, t, y):
                    use[p.program, y] += p.crew_months * x[p.project_id, t]
    return use
```

## A Switched Row Is Off Only When M Covers the Largest Value Its Left Side Can Take

Read the crew row for its two cases. When $`h_{g,y} = 0`$ (no contractor), the term
$`M_{g,y} h_{g,y}`$ is 0 and the row says crew use $`\le K_{g,y}`$: the in-house limit, as it
should. When $`h_{g,y} = 1`$, the row says crew use $`\le K_{g,y} + M_{g,y}`$. The rule wants the
limit **gone** in that case. A linear row cannot vanish, so instead it is made so loose that it can
never bind. That happens when $`K_{g,y} + M_{g,y}`$ is at least the largest crew use any allowed
plan can have.

Such a row, a constraint plus a binary times a constant that makes it harmless, is called a
**big-M constraint**, and the binary is its **switch**. The constant has two jobs, and they pull in
opposite directions:

- **Valid.** $`M`$ must be large enough. If it is too small, the row still binds when the switch is
  on, and it refuses plans that the business rule allows. The model then returns a worse plan than
  the best one, and nothing in the output says so.
- **Tight.** $`M`$ should be as small as validity allows. Lesson 6.2.2 shows what a needlessly
  large $`M`$ costs: a weaker LP bound (the LP relaxation, lesson 3.1.1, is the model with the
  whole-number rule dropped; its optimal value bounds every plan, lesson 3.1.2) and numerical trouble.

Put together, the smallest valid $`M`$ for a row "$`a^\top x \le b`$ unless $`h = 1`$" is

```math
M^{\ast} \;=\; \max\Big(0,\; \max_{x \text{ allowed by the other rows}} a^\top x \;-\; b\Big)
```

the most the left side can exceed the right side over every plan the rest of the model allows. If
the left side can never exceed $`b`$ at all, the row can never bind, the switch is pointless, and
$`M^{\ast} = 0`$.

Take one row of GridCap tiny by hand: distribution in 2029. Two start variables keep a distribution
project busy that year:

```text
crew use of distribution in 2029: {'x_P001_2029': 5, 'x_P006_2028': 4}, in-house 3
M from variable bounds: 6
M from once rows:       6
M by solving the MILP:  2
```

The row is $`5\,x_{P001,2029} + 4\,x_{P006,2028} \le 3 + M\,h_{\text{dist},2029}`$. The three
values of $`M`$ come from the three rules below; the last is $`M^{\ast}`$. P006 can never be funded
in GridCap tiny: it may only start in 2028, and must-do P002 has to start in 2028 too (its 2,730 does
not fit 2029's budget of 2,310), so together they would spend 2,730 + 840 = 3,570 in 2028, over the
3,280 budget. The most the row's left side can be in an allowed plan is 5 (P001 alone), so
$`M^{\ast} = 5 - 3 = 2`$. One less is too small, and the model refuses a plan the planners would
accept:

```text
plan {'P002': 2028, 'P001': 2029} with a contractor and M = 1: refused
plan {'P002': 2028, 'P001': 2029} with a contractor and M = 2: allowed
```

With $`M = 1`$ the contractor is hired and the row still says $`5 \le 3 + 1`$, which is false. A
model with that $`M`$ would never start P001 in 2029, whatever it is worth.

## Variable Bounds Give a Safe M With No Solve

Finding $`M^{\ast}`$ exactly means solving an optimization problem (the fourth rule). Usually you
want a value you can compute from the data in one pass, and accept that it may be larger than
$`M^{\ast}`$. Larger is safe; smaller is not.

The cheapest safe value uses nothing but each variable's own bounds. The left side
$`a^\top x = \sum_j a_j x_j`$ is largest when every term is largest on its own: a term with a
positive coefficient is largest at the variable's upper bound $`u_j`$, and a term with a negative
coefficient at its lower bound $`l_j`$. So

```math
\max a^\top x \;\le\; \sum_{j:\, a_j > 0} a_j\, u_j \;+\; \sum_{j:\, a_j < 0} a_j\, l_j,
\qquad
M \;=\; \max\Big(0,\; \sum_{j:\, a_j > 0} a_j\, u_j + \sum_{j:\, a_j < 0} a_j\, l_j - b\Big)
```

This is valid because no plan can beat the sum of each term's best case. It is not tight, because
it pretends every term can be at its best at once, which the other rows usually forbid.

A crew row has only positive coefficients on binaries ($`u_j = 1`$), so the bound is the sum of
the crew-months of every start that is busy that year:

```python
def m_from_variable_bounds(portfolio: Portfolio) -> dict[tuple[str, int], int]:
    """Every x at its upper bound 1: the largest the row's left side can be, less the crews in house."""
    m = {}
    for g in PROGRAMS:
        for y in portfolio.years:
            most = sum(p.crew_months for p in portfolio.projects if p.program == g
                       for t in p.starts() if active(p, t, y))
            m[g, y] = max(0, most - portfolio.crews[g, y])
    return m
```

The same reasoning works for a row in the other direction. A floor "$`a^\top x \ge b`$ unless
$`h = 1`$" is written $`a^\top x \ge b - M h`$, and with the switch on it must allow the
*smallest* value the left side can take. Its safe $`M`$ is $`b`$ minus the smallest left side,
which takes positive coefficients at their lower bounds and negative ones at their upper bounds:

```math
M \;=\; \max\Big(0,\; b - \sum_{j:\, a_j > 0} a_j\, l_j - \sum_{j:\, a_j < 0} a_j\, u_j\Big)
```

Two consequences matter in every model you write:

- **A switched variable needs a finite bound.** The most common big-M row is a **fixed charge**:
  a continuous amount $`s`$ may be positive only if a binary $`z`$ is 1, written $`s \le U z`$. By
  the rule above, the right $`U`$ is $`s`$'s upper bound. If $`s`$ has no upper bound, no valid
  $`M`$ exists, and you must find one in the data (a budget, a capacity, a demand) before you can
  write the row. Lesson 6.2.3 shows the alternative that needs no $`M`$.
- **Every row gets its own M.** The crew rows of different programs and years have different left
  sides, so one $`M`$ for all of them is either too small for the largest row or needlessly large
  for the rest. `m_from_variable_bounds` returns one value per row.

<!-- practice 1 -->

## Rows That Cap a Group Give a Smaller M

The bound rule treats every variable as free to be 1. But the model's once rows say a project
starts at most once, so of P036's start variables only one can be 1. Look at transmission in 2030 on
GridCap small: P036 has a two-year profile and may start in 2027 to 2030, so starting in 2029 or in
2030 keeps it busy in 2030. The bound rule counts its crew-months twice, once per start; no plan can
do that.

The general rule: **if at most one variable of a group can be 1, the group adds at most its largest
coefficient**, not the sum of its coefficients. For a crew row every start of one project has the
same coefficient (the project's crew-months), so a project adds its crew-months once if any of its
starts is busy in the year:

```python
def m_from_once_rows(portfolio: Portfolio) -> dict[tuple[str, int], int]:
    """A project starts at most once, so it adds its crew_months once, if any start reaches the year."""
    m = {}
    for g in PROGRAMS:
        for y in portfolio.years:
            most = sum(p.crew_months for p in portfolio.projects if p.program == g
                       and any(active(p, t, y) for t in p.starts()))
            m[g, y] = max(0, most - portfolio.crews[g, y])
    return m
```

Where a group's coefficients differ (in another model, say, a project whose crew need depends on
the year it starts), take the largest. The value is still safe: every allowed plan picks at most
one member of each group, and that member's coefficient is at most the group's largest.

The table at the end of the next section shows what this buys on GridCap small: transmission in
2030 drops from 98 to 52, because transmission projects there have long windows and multi-year
profiles. Vegetation projects in GridCap small last one year, so each start keeps a project busy only in
its own year and the two rules agree on every vegetation row.

<!-- practice 2 -->

## The Tightest M Is a Maximization Over the Rest of the Model

The two rules above ignore every row except the bounds and the once rows. The budgets also cap how
much work can run in a year, and a must-do project takes its share of the budget whatever happens.
The exact $`M^{\ast}`$ of the formula above takes all of that into account: build the model without
the crew rows, maximize one row's crew use, and subtract the in-house crews.

```python
def m_by_solving(portfolio: Portfolio, *, integer: bool) -> dict[tuple[str, int], int]:
    """The largest crew use the other rows allow, per row, found by maximizing it: an LP or the MILP."""
    m = {}
    for key, crews in portfolio.crews.items():
        cm = build(portfolio, 0, integer=integer, form="none")
        cm.model.maximize(cm.use[key])
        most = quiet_solve(cm.model, mathopt.SolverType.HIGHS if integer else mathopt.SolverType.GLOP,
                           params=mathopt.SolveParameters(relative_gap_tolerance=0.0) if integer else None)
        m[key] = max(0, math.floor(most.objective_value() + 1e-6) - crews)
    return m
```

Solving the MILP gives $`M^{\ast}`$ itself, at the price of one MILP per row (15 on GridCap small).
Solving only the LP relaxation (`integer=False`) is cheaper and still safe: every allowed plan is a
point of the relaxation, so the LP's maximum is at least the MILP's. Because crew use is a whole
number of crew-months in every real plan, the LP's maximum can also be rounded down to a whole
number without losing validity. The `+ 1e-6` keeps a value the LP returns as 38.9999999 from being
rounded down to 38: solvers compute in floating point.

All four values for every row of GridCap small:

```text
program       year  in-house   M: bounds  once rows  LP max  MILP max
transmission  2027        26          16         16      12        10
transmission  2028        19          54         34      19        18
transmission  2029        20          79         47      29        26
transmission  2030        34          98         52       8         5
transmission  2031        14          67         67      19        12
distribution  2027         9           5          5       5         5
distribution  2028        15          14          9       9         9
distribution  2029        11          22         11      11        11
distribution  2030         8          25         17      17        17
distribution  2031         4          15         15      15        15
vegetation    2027         2           1          1       1         1
vegetation    2028         3           4          4       4         4
vegetation    2029         4           5          5       5         5
vegetation    2030         7          13         13      13        13
vegetation    2031         2          15         15      15        15
sum of M over the 15 rows: 433 311 182 166
```

Every column is valid, and each is at most the one to its left: each rule uses more of the model
than the one before. Transmission 2030 shows the whole range: 98 from bounds, 52 once each project
counts once, and 8 and 5 once the budgets are counted. Transmission projects are the expensive
ones, and 2030's budget of $8,610k cannot pay for all the transmission work that could be busy that
year, so no allowed plan comes near the 52 extra crew-months the once rows still allow.

Which one should a model use? In production, the cheapest one you can defend. Bounds and once-row
values cost nothing and never go wrong when the data change, as long as you recompute them from the
data each run, never type them in. Solving for $`M`$ costs a solve per row, and is worth it when
lesson 6.2.2's measurements show the bound matters. Any of them beats a round number such as
$`10^6`$, which is valid only by luck of scale and is never tight.

## Summary

- **A switched row is off only when M covers the largest value its left side can take.** The
  smallest valid $`M`$ is the most the left side can exceed the right side over every plan the rest
  of the model allows; too small refuses real plans silently.
- **Variable bounds give a safe M with no solve.** Positive coefficients at upper bounds, negative
  at lower bounds; a switched continuous variable needs a finite bound, and every row gets its own M.
- **Rows that cap a group give a smaller M.** If at most one variable of a group can be 1, the group
  adds only its largest coefficient.
- **The tightest M is a maximization over the rest of the model.** The MILP gives it exactly; the
  LP gives a safe value in between, rounded down when the left side is whole.

## Reference

| Row | Written as | Smallest safe M from bounds |
| --- | --- | --- |
| $`a^\top x \le b`$ unless $`h = 1`$ | $`a^\top x \le b + M h`$ | $`\sum_{a_j>0} a_j u_j + \sum_{a_j<0} a_j l_j - b`$, at least 0 |
| $`a^\top x \ge b`$ unless $`h = 1`$ | $`a^\top x \ge b - M h`$ | $`b - \sum_{a_j>0} a_j l_j - \sum_{a_j<0} a_j u_j`$, at least 0 |
| $`s > 0`$ only if $`z = 1`$ (fixed charge) | $`s \le U z`$ | $`U`$ = the upper bound of $`s`$ |

| Way to get M | Uses | Cost | Valid |
| --- | --- | --- | --- |
| a round number ($`10^6`$) | nothing | none | only if it happens to be large enough |
| variable bounds | each variable's bounds | one pass over the row | always |
| group caps (once rows) | "at most one of these" rows | one pass | always |
| LP maximum | every row, fractions allowed | one LP per row | always (round down if the row is whole) |
| MILP maximum | every row | one MILP per row | always, and the smallest |

| Term | Meaning |
| --- | --- |
| big-M constraint | a row plus a binary times a constant $`M`$, so that the binary switches the row off |
| switch | the binary in a big-M row |
| valid M | one large enough that the switched-off row refuses no allowed plan |
| tight M | the smallest valid one |
| fixed charge | a continuous amount allowed only when a binary is on: $`s \le U z`$ |

**Further reading:** [The Bin Packing Problem (OR-Tools)](https://developers.google.com/optimization/pack/bin_packing) (a switched row in an OR-Tools example: a bin's load is at most its capacity times its "used" binary, so the capacity serves as $`M`$; lesson 6.2.2 measures it); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the model features MathOpt accepts, indicator constraints among them, the $`M`$-free form of lesson 6.2.3); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2, "Constraint Feasibility": a row switched off by a binary and a constant large enough for every choice of the variables, and the advice to take the smallest one, to avoid numerical difficulties; "Fixed Costs": $`x \le B y`$ with $`B`$ the capacity); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 6.1: the big-M constant of a row as the largest value of that row over what the other case allows, the $`M^\ast`$ of this lesson); [MO-book 3.4, Production model using disjunctions](https://mobook.github.io/MO-book/notebooks/03/04-simple-production-model-gdp.html) (Pyomo's big-M transformation needs bounds on the variables, for the reason given here).

## Challenges

1. Transmission 2028's $`M`$ drops from 54 (bounds) to 34 (once rows). Find, in the project
   table, a project the bound rule counts more than once in that row.
2. Write the crew row for "at most $`K`$ crew-months in house, plus at most 10 more if a contractor
   is hired". What is its $`M`$, and does it depend on the data any more?
3. On GridCap tiny, compute the once-row $`M`$ of every vegetation row by hand from the project
   table and check it against `m_from_once_rows`.

## Design Note: Compute M in Code, Next to the Row

`crew_model.py` never contains a number for $`M`$. Every value is computed from the portfolio by a
named function, and `build` takes the result as an argument. That keeps three promises: the value
moves when the data move (a new project, a longer window, a bigger crew), a reviewer can read why the
value is safe from the function's name and docstring, and a test can check validity directly, as
`tiny_row.py` does, by fixing a plan the rule allows and asking whether the model accepts it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**tiny_row.py.** One crew row of GridCap tiny, its $`M`$ three ways, and the plan a too-small $`M`$
refuses (*A Switched Row Is Off Only When M Covers the Largest Value Its Left Side Can Take*).
*Try:* Change the row to `("transmission", 2029)` and predict, from the project table, which of the
three values will be smallest.

- Program: [tiny_row.py](src/tiny_row.py)

**m_table.py.** Every crew row of GridCap small with its $`M`$ from bounds, once rows, the LP and
the MILP (*The Tightest M Is a Maximization Over the Rest of the Model*). *Try:* Halve every year's
budget before computing the table. Predict which columns move.

- Program: [m_table.py](src/m_table.py)

**crew_model.py.** The model builder the module's programs import: start variables, the
multi-period rows of lessons 6.4.1 to 6.4.4, crew use, the three ways to get $`M`$, and the crew rows as big-M or indicator constraints.

- Library: [crew_model.py](src/crew_model.py)
