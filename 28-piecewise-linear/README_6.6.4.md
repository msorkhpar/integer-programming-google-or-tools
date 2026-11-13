# 6.6.4 Lifecycle Value Curves for Asset Renewal

GridCap's asset team has a renewal fund of $3,000k for the small portfolio's ten assets that have a
replacement project. Until now a replacement was all or nothing. The field crews point out that most
of these assets can be renewed in part: replace a third of a line's spans, half of a pole set, the
worst breakers of a bay. A partial renewal costs part of the replacement and buys part of its value.
But not in proportion: renewing the first quarter of a worn-out line removes far more failures than
the last quarter, and for some assets it is the other way round. The value of a renewal as a
function of how much is renewed is a **lifecycle value curve**. This lesson builds one per asset from
GridCap's failure model, puts all ten into one model with the cheapest exact formulation for each,
and checks the result with two other tools, in six rules.

GridCap is a fictional utility's portfolio, generated for this course; the renewal fund and partial
renewals are invented for this lesson.

## A Lifecycle Value Curve Comes From the Asset's Failure Model

Every GridCap asset has a Weibull failure model with shape $`\beta`$ and scale $`\eta`$ (years), an
age $`a`$ and a consequence of failure $`\text{cof}`$, the cost of one failure in $k (lesson 1.1.2).
Assume that a failed asset is repaired just enough to run again, so that a failure does not make it
any younger. Under that assumption the expected number of failures between ages $`a`$ and $`a + h`$ is
the growth of the **cumulative hazard** $`\Lambda(t) = (t/\eta)^\beta`$ over those years:

```math
N(a) = \Lambda(a + h) - \Lambda(a) = \Big(\frac{a + h}{\eta}\Big)^{\beta} - \Big(\frac{a}{\eta}\Big)^{\beta}
```

with $`h = 5`$, the plan's five years. Now define a renewal of **depth** $`d \in [0, 1]`$: $`d = 0`$ is
nothing, $`d = 1`$ a full replacement, and in between the asset becomes as old as $`(1 - d)\,a`$, the
same convention as lesson 1.1.2's repairs, which took an asset back to half its age. It costs
$`d \times \text{capex}`$ of the asset's replacement project. Its value is the failure cost it avoids
over the plan:

```math
V(d) = \text{cof} \cdot \Big( N(a) - N\big((1 - d)\,a\big) \Big)
```

```python
def expected_failures(age: float, beta: float, eta: float, years: float = HORIZON) -> float:
    return ((age + years) / eta) ** beta - (age / eta) ** beta


def risk_avoided(asset, depth: float) -> float:
    """$k of expected failure cost avoided over the plan by a renewal of this depth."""
    before = expected_failures(asset.age, asset.weibull_beta, asset.weibull_eta)
    after = expected_failures((1 - depth) * asset.age, asset.weibull_beta, asset.weibull_eta)
    return asset.cof * (before - after)
```

$`V`$ is not piecewise linear; it is a smooth curve. To put it in a MILP, sample it at five depths,
$`0, 0.25, 0.5, 0.75, 1`$, and join the samples by straight lines: a piecewise-linear curve with five
breakpoints, which lessons 6.6.1 to 6.6.3 know how to write.

```python
def value_curve(asset, depths=DEPTHS) -> Curve:
    return Curve(tuple(depths), tuple(risk_avoided(asset, d) for d in depths))
```

```text
project asset        age  beta | value at depth  0.0  0.25   0.5  0.75   1.0 | shape   | capex | worst gap
P001    line         45  3.91 |                  0   326   506   583   599 | concave |  2640 |  20.8
P013    pole         27  1.77 |                  0    12    24    38    55 | convex  |  1010 |   0.7
P016    breaker       5  1.61 |                  0    16    34    54    79 | convex  |  1260 |   0.9
P019    pole         28  2.76 |                  0   837  1503  1982  2245 | concave |  1720 |  30.3
P021    breaker      25  1.59 |                  0    14    30    50    78 | convex  |  2020 |   2.1
P023    pole         46  1.81 |                  0   176   363   568   816 | convex  |  1500 |  10.3
P026    transformer  13  3.41 |                  0   177   300   373   407 | concave |  1350 |   7.3
P028    breaker      31  2.62 |                  0   259   474   637   734 | concave |  5060 |   9.8
P030    line         16  3.94 |                  0   197   313   369   387 | concave |  5840 |  11.4
P040    pole         36   1.8 |                  0    50   104   162   233 | convex  |  2440 |   2.9
```

P019, a 28-year-old pole set, avoids $837k of failures if a quarter of it is renewed and $2,245k if
all of it is, for a full price of $1,720k. P013 avoids $55k for $1,010k. The last column is the next
rules' business.

## Wearing-Out Assets Have Concave Curves, the Others Convex

Five curves are concave and five convex, and the column that sorts them is $`\beta`$: every asset with
$`\beta > 2`$ has a concave curve, every one with $`\beta < 2`$ a convex one. That is not a
coincidence of this portfolio; it follows from the formula.

The value is $`\text{cof}\,(N(a) - N(u))`$ with $`u = (1 - d)\,a`$, so it is concave in $`d`$ exactly
when $`N(u)`$ is convex in $`u`$ ($`u`$ falls in a straight line as $`d`$ grows). Here
$`N(u) = \Lambda(u + 5) - \Lambda(u)`$, and its second derivative is
$`\Lambda''(u + 5) - \Lambda''(u)`$, with $`\Lambda''(t) = \beta(\beta - 1)\,t^{\beta - 2} / \eta^{\beta}`$.
For $`\beta > 2`$, $`t^{\beta - 2}`$ grows with $`t`$, so $`\Lambda''(u + 5) > \Lambda''(u)`$ and
$`N`$ is convex: the value is concave. For $`1 < \beta < 2`$, $`t^{\beta - 2}`$ shrinks, and the
value is convex.

In words: a **wearing-out** asset ($`\beta > 2`$, failures speeding up with age) loses most of its
risk in the first part of a renewal, because that part takes away the oldest, steepest years; each
further quarter buys less. An asset whose failure rate grows only slowly ($`\beta < 2`$) gains little
from a shallow renewal, and the value comes in a rush at the end, when the renewal reaches the
youngest years, where its failure rate changes fastest.

The shape decides the formulation (lesson 6.6.1): the model maximizes value, so it pushes each curve
up. A concave curve pushed up is exact with segment variables and no binaries. A convex curve pushed
up is not; it needs the exact forms of lessons 6.6.2 and 6.6.3.

## Five Breakpoints Are an Approximation You Can Measure

The curve the model sees is the five-point one, not $`V`$. The last column of the table is the
**worst gap**: the largest difference between $`V`$ and the five-point curve, over 400 depths
between 0 and 1.

```python
def worst_gap(asset, curve, steps: int = 400) -> float:
    """The largest |true value - curve value| over a fine grid of depths, in $k."""
    return max(abs(risk_avoided(asset, k / steps) - curve(k / steps)) for k in range(steps + 1))
```

The straight line between two breakpoints lies *below* a concave curve and *above* a convex one. So
the five-point curve underrates every concave asset a little between its breakpoints, and overrates
every convex one. The gaps here are small next to the values (P019: $30.3k on a curve that reaches
$2,245k), and they shrink with more breakpoints. For A019, P019's pole set:

```text
A019 with 9 breakpoints: worst gap 8.3 (5 breakpoints: 30.3)
```

Twice the segments, about a quarter of the gap: for a smooth curve, the gap of a straight chord
grows with the square of the segment's width. More breakpoints cost more variables (and, for a convex
curve, more binaries or bits), so choose the number from a tolerance, not by habit: the smallest
count whose worst gap is below what the decision can feel.

<!-- practice 1 -->

## Each Curve Gets the Cheapest Exact Form

The model: one depth per candidate, a value on its curve, all within the fund.

```math
\max \sum_{i} V_i(d_i) \quad \text{subject to} \quad \sum_i \text{capex}_i\, d_i \le 3{,}000, \quad 0 \le d_i \le 1
```

with each $`V_i`$ the five-point curve of asset $`i`$. The library builds it with any rule for choosing
a formulation per curve:

```python
for p, asset in candidates(portfolio):
    curve = value_curve(asset, depths)
    piece = choose(curve)(model, curve, p.project_id)
    depth[p.project_id], value[p.project_id] = piece.x, piece.y
    binaries += len(piece.binaries)
model.add_linear_constraint(sum(p.capex * depth[p.project_id] for p, _ in candidates(portfolio)) <= fund,
                            name="fund")
model.maximize(sum(value.values()))
```

and the rule this lesson argues for picks by shape:

```python
def by_shape(curve: Curve):
    """Segments where the value curve is concave (the solver pushes value up), the incremental form elsewhere."""
    return add_segments if curve.concave() else add_incremental
```

The program solves it four ways and, for each plan, computes the **true** value of the depths it
chose with $`V`$ itself:

```text
renewal fund $3,000k, 10 candidates
segments for every curve  :  0 binaries, claims $2,971.0k, true value $2,887.5k
    depths: {'P019': 1.0, 'P023': 0.628, 'P026': 0.25}
incremental for every curve: 30 binaries, claims $2,926.5k, true value $2,956.7k
    depths: {'P019': 0.872, 'P023': 1.0}
chosen by each curve's shape: 15 binaries, claims $2,926.5k, true value $2,956.7k
    depths: {'P019': 0.872, 'P023': 1.0}
by shape, 9 breakpoints    : 35 binaries, claims $2,956.2k, true value $2,955.5k
    depths: {'P019': 0.875, 'P023': 0.997}
```

- **Segments for every curve** is the mistake lesson 6.6.1 warned of. P023's curve is convex
  ($`\beta = 1.81`$), and the segment rows let the solver take its steepest last quarter first: the
  model claims $2,971.0k, and the depths it chose are really worth $2,887.5k.
- **The incremental form for every curve** is exact on the five-point curves, with 3 binaries per
  curve, 30 in all. It renews P023 fully and 87.2% of P019.
- **Chosen by shape** finds the same plan with 15 binaries: the five concave curves need none.
- Its claim, $2,926.5k, is below the true value of its plan, $2,956.7k, because the five-point
  curves underrate the concave P019 between breakpoints. **With nine breakpoints** the claim moves to
  within $1k of the truth and the depths barely change; the plan's true value is $1.2k lower than
  the five-point plan's, a reminder that a finer curve is a better *estimate*, and the decision was
  already right.

The exact plan beats the segment-only one by $69.2k of true value ($2,956.7k against $2,887.5k), and
the segment-only model reported $2,971.0k: $83.5k more than its own plan delivers, and $14.3k more
than even the exact plan does.

## CP-SAT Reads a Curve as a Table When the Decision Is Integer

OR-Tools' CP-SAT solver works on integers and has no SOS2 or piecewise-linear constraint (lesson
6.6.2's program found no SOS method on its `CpModel`). It does have the **element** constraint,
`add_element(index, expressions, target)`, which says `target == expressions[index]` for an integer
variable `index`. If renewals are only sold in quarters (a depth of 0, 1, 2, 3 or 4 quarters), the
curve is just its five breakpoint values, a table to look up:

```python
quarters[p.project_id] = model.new_int_var(0, 4, f"q_{p.project_id}")
worth[p.project_id] = model.new_int_var(0, max(table(a)), f"v_{p.project_id}")
model.add_element(quarters[p.project_id], table(a), worth[p.project_id])
```

The program rounds the values to whole $k (CP-SAT needs integers) and solves the quarter-step
problem in CP-SAT and, for comparison, in MathOpt with the incremental form and the depth tied to an
integer number of quarters:

```text
CP-SAT, add_element : OPTIMAL, $2,813k, quarters {'P019': 4, 'P023': 3}
MathOpt, incremental: OPTIMAL, $2,813k, quarters {'P019': 4, 'P023': 3}
```

Both find the same plan. The table form is exact for any shape, because there is nothing between
the breakpoints to get wrong; the price is that the decision may only take the table's values. When
the business decides in steps (crews, spans, units), that is a feature; when the depth is truly
continuous, the forms of lessons 6.6.1 to 6.6.3 keep it continuous.

## A Second Tool Checks the Formulation

The formulations of this module are a few dozen lines of code, and a wrong row in them gives a model
that solves, reports "optimal", and is wrong. An independent check is cheap: build the same model in
another modeling tool that writes the formulation itself, and compare the optimum. Pyomo, which
section 5 covers (lesson 5.1.4 is about its piecewise functions), has a `Piecewise` component: given
a variable $`x`$, a variable $`y`$, the breakpoints and the values, it adds the rows for $`y = f(x)`$.
Its `pw_repn` argument names the formulation: `"CC"` is the lambda form with segment binaries,
`"INC"` the incremental form, `"LOG"` the logarithmic one, and the default `"SOS2"` hands an SOS2
constraint to the solver; `pw_constr_type="EQ"` asks for $`y = f(x)`$ rather than one side.

```python
m = pyo.ConcreteModel()
m.P = pyo.Set(initialize=[p.project_id for p, _ in cands])
m.depth = pyo.Var(m.P, bounds=(0, 1))
m.value = pyo.Var(m.P)
m.curve = pyo.Piecewise(
    m.P, m.value, m.depth,
    pw_pts={p.project_id: list(DEPTHS) for p, _ in cands},
    f_rule={p.project_id: list(value_curve(a).ys) for p, a in cands},
    pw_constr_type="EQ", pw_repn=repn)
m.fund = pyo.Constraint(expr=sum(p.capex * m.depth[p.project_id] for p, _ in cands) <= fund)
m.obj = pyo.Objective(expr=sum(m.value[i] for i in m.P), sense=pyo.maximize)
```

The program solves it with HiGHS through Pyomo's `appsi_highs` interface, once per formulation, next
to the MathOpt model with the incremental form on every curve:

```text
MathOpt, incremental form : $2,926.5k
Pyomo Piecewise, INC     : $2,926.5k, depths {P019: 0.872, P023: 1.000}
Pyomo Piecewise, CC      : $2,926.5k, depths {P019: 0.872, P023: 1.000}
Pyomo Piecewise, LOG     : $2,926.5k, depths {P019: 0.872, P023: 1.000}
Pyomo Piecewise, SOS2    : NotImplementedError: Highs interface does not support SOS constraints
```

Three formulations written by another tool's authors agree with this module's code, to the $0.1k
and on the depths. The fourth shows the point of lesson 6.6.2 from the other side: Pyomo's default
SOS2 representation needs a solver interface that accepts SOS constraints, and its HiGHS interface
refuses it. A check like this belongs in the model's tests, on a small instance, where it catches a
broken formulation the day it is broken.

<!-- practice 2 -->

## The Model

The renewal model on GridCap small's ten replacement candidates, with each curve written by its
shape. This model is new in this lesson; everything in it is marked.

**Sets.** $`R`$ the candidates: the projects with a replacement intervention, each with its asset
(10 on small); $`R_A \subseteq R`$ those whose value curve is concave, $`R_B = R \setminus R_A`$
the others (convex); $`j = 0, \dots, 4`$ the breakpoints and $`k = 1, \dots, 4`$ the segments.

**Parameters.** $`\text{capex}_i`$, the replacement project's cost ($k); $`D_j = j/4`$, the depths of
the breakpoints; $`V_{i,j} = V_i(D_j)`$, asset $`i`$'s value at depth $`D_j`$ ($k, from its Weibull
$`\beta_i`$, $`\eta_i`$, age $`a_i`$ and $`\text{cof}_i`$); $`s_{i,k} = (V_{i,k} - V_{i,k-1}) / (D_k -
D_{k-1})`$, the slopes; $`F = 3{,}000`$, the fund ($k).

**Variables.**

```math
\begin{aligned}
& 0 \le \delta_{i,k} \le D_k - D_{k-1} && \forall i \in R_A,\; k = 1, \dots, 4 && \text{(depth renewed in segment } k\text{)} \\
& 0 \le \phi_{i,k} \le 1 && \forall i \in R_B,\; k = 1, \dots, 4 && \text{(share of segment } k \text{ used)} \\
& w_{i,k} \in \{0, 1\} && \forall i \in R_B,\; k = 1, 2, 3 && \text{(1 if segment } k \text{ is full)}
\end{aligned}
```

The depth and value of each candidate are expressions of these:

```math
d_i = \sum_{k} \delta_{i,k},\;\; v_i = \sum_k s_{i,k}\,\delta_{i,k} \;\; (i \in R_A); \qquad
d_i = \sum_{k} (D_k - D_{k-1})\,\phi_{i,k},\;\; v_i = \sum_k (V_{i,k} - V_{i,k-1})\,\phi_{i,k} \;\; (i \in R_B)
```

**Objective.**

```math
\max \; \sum_{i \in R} v_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in R} \text{capex}_i\, d_i &\le F && && \text{(fund)} \\
\phi_{i,k+1} &\le w_{i,k} && \forall i \in R_B,\; k = 1, 2, 3 && (i\text{\_next}_k) \\
w_{i,k} &\le \phi_{i,k} && \forall i \in R_B,\; k = 1, 2, 3 && (i\text{\_full}_k)
\end{aligned}
```

The concave curves need no row of their own: the objective pushes their value up, and their slopes
fall. In the code each candidate's variables are named after its project (`P023_fill0`,
`P023_full0`, `P019_d0`, ...).

## Summary

- **A lifecycle value curve comes from the asset's failure model.** With minimal repair, a renewal
  of depth $`d`$ avoids $`\text{cof}\,(N(a) - N((1-d)a))`$ over the plan; sample it at five depths.
- **Wearing-out assets have concave curves, the others convex.** $`\beta > 2`$ gives concave,
  $`\beta < 2`$ convex, from the sign of $`\Lambda''(u + 5) - \Lambda''(u)`$.
- **Five breakpoints are an approximation you can measure.** Chords lie below a concave curve and
  above a convex one; doubling the segments cut P019's worst gap from $30.3k to $8.3k.
- **Each curve gets the cheapest exact form.** Segments for the concave, incremental for the convex:
  the exact plan with 15 binaries instead of 30, worth $69.2k more than the all-segments plan.
- **CP-SAT reads a curve as a table when the decision is integer.** With depths in quarters,
  `add_element` looks the value up, and CP-SAT and MathOpt find the same $2,813k plan.
- **A second tool checks the formulation.** Pyomo's `Piecewise` (INC, CC, LOG) agrees with MathOpt
  to the $0.1k; its default SOS2 is refused by its HiGHS interface.

## Reference

| Asset | Curve shape | Pushed | Formulation |
| --- | --- | --- | --- |
| $`\beta > 2`$ (wearing out) | concave | up (value maximized) | segments, no binaries |
| $`\beta < 2`$ | convex | up | incremental, lambda or log |
| any, depth in steps | table | either | CP-SAT `add_element`, or an integer step count |

| Tool | How it writes $`y = f(x)`$ |
| --- | --- |
| MathOpt | your own rows (this module's `piecewise.py`); no SOS or piecewise method in OR-Tools 9.15 |
| Pyomo | `Piecewise(..., pw_pts=..., f_rule=..., pw_constr_type="EQ", pw_repn="INC")` |
| CP-SAT | `add_element(index, values, target)` for an integer index |

**Further reading:** [CP-SAT `cp_model` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/sat/python/cp_model.py) (`add_element`, which sets a target to the entry of a list chosen by an index, and `add_linear_expression_in_domain`); [CP-SAT sample step_function_sample_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/step_function_sample_sat.py) (a step function written with enforced domain constraints, another way to tabulate a function in CP-SAT); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt calls, none of which is given an SOS2 by this course); [Pyomo `Piecewise`](https://pyomo.readthedocs.io/en/stable/api/pyomo.core.base.piecewise.Piecewise.html) (`pw_repn`, `pw_constr_type` and the breakpoints, with SOS2 as the default representation); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2, "Approximation of Nonlinear Functions": a curve replaced by line segments between breakpoints); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (sections 8 and 9: the incremental and logarithmic formulations of a piecewise-linear function).

## Challenges

1. Change `HORIZON` to 10 years. Predict whether any asset's curve changes shape, then run
   `value_curves.py`.
2. Find the smallest number of equally spaced breakpoints that brings P019's worst gap under $5k.
3. Give each partial renewal a fixed mobilization cost of $100k (nothing if $`d = 0`$). Which
   lesson of this section writes that, and does the concave case still need no binaries?

## Design Note: Keep the True Curve Next to the Approximation

The model optimizes the five-point curves; the planners care about $`V`$. `renewal_plan.py` keeps
both: it solves on the approximation and reports the plan's value on the true curve. That one extra
line is what exposed the segment-only model ($2,971.0k claimed, $2,887.5k real) and what shows that
nine breakpoints change the estimate more than the decision. A model whose input is an approximated
curve should always report both numbers, and a review should ask for the gap between them.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**value_curves.py.** Prints each candidate's five-point value curve, its shape and its worst gap
(*A Lifecycle Value Curve*, *Wearing-Out Assets*, *Five Breakpoints Are an Approximation*). *Try:*
Change `DEPTHS` in `lifecycle.py` to three breakpoints (0, 0.5, 1). Predict P019's worst gap.

- Program: [value_curves.py](src/value_curves.py)

**renewal_plan.py.** Solves the renewal fund with segments everywhere, incremental everywhere, by
shape, and by shape with nine breakpoints (*Each Curve Gets the Cheapest Exact Form*). *Try:* Raise
`FUND` to 6,000. Predict whether the all-segments model's claim moves further from the truth.

- Program: [renewal_plan.py](src/renewal_plan.py)

**pyomo_check.py.** Builds the renewal model in Pyomo with `Piecewise` and four representations
(*A Second Tool Checks the Formulation*). *Try:* Add `"BIGM_BIN"` to the list. Predict whether it
agrees.

- Program: [pyomo_check.py](src/pyomo_check.py)

**cpsat_element.py.** The quarter-step renewal in CP-SAT with `add_element` and in MathOpt (*CP-SAT
Reads a Curve as a Table*). *Try:* Allow eighths instead of quarters (a table of nine values). Predict
whether the two solvers still agree.

- Program: [cpsat_element.py](src/cpsat_element.py)

**lifecycle.py.** The failure model, the value curves and the renewal model builder.

- Library: [lifecycle.py](src/lifecycle.py)

**piecewise.py.** The curve and the formulations of lessons 6.6.1 to 6.6.3.

- Library: [piecewise.py](src/piecewise.py)
