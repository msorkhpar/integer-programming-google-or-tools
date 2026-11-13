# 7.4.4 Building the CIPT Value Function

The GridCap board has signed off on four measures (lesson 7.4.1), their references (lesson 7.4.2)
and their swing weights (lesson 7.4.3). Now the optimization team needs something it can put in a
model: the objective of the multi-period selection model of lessons 6.4.1 to 6.4.4, the one that sections 8
(*Multi-objective optimization*) and 14 (the capstone) solve. A model's objective coefficients have to
be exact: one number per decision variable, with a definition that two people would compute the same
way. "Weighted reliability, safety, environment and NPV" is not yet that.

This lesson writes the CIPT value function down precisely: its sets, parameters, units, the
coefficient of every start variable, and the full model it is the objective of. It builds the
coefficients for GridCap small, turns them back into dollars for planners, puts them into a MathOpt
expression, and tests that the result does not depend on the units the data arrived in. Solving the
model, and what weighted objectives can and cannot find, is the subject of lessons 8.1.1 and 8.1.2 (*Weighted sums*).

GridCap is a fictional utility generated for this course; its consequence table, references and
ratings are invented. Every project ID in this lesson is the small portfolio's: small's P006 is a
Valley corridor widening, not the tiny transformer replacement of lesson 7.4.1.

## The Value Function Is One Coefficient per Project and Start Year

The selection model of lessons 6.4.1 to 6.4.4 decides **when** each project starts: $`x_{i,t} = 1`$ if project
$`i`$ starts in year $`t`$, for each $`t`$ in its window $`T_i`$ (lesson 6.4.1). Every benefit in
lesson 7.4.1 depends on the start year: NPV through discounting, the other measures because the asset
ages while it waits and fewer years of the evaluation window are left. So the value function gives one
coefficient to each start variable:

```math
v_{i,t} = \sum_{k \in K} w_k\, \frac{m_{i,t,k}}{R_k}
```

with $`K`$ = {reliability, safety, environmental, financial}, $`m_{i,t,k}`$ the benefit of starting
$`i`$ in $`t`$ in measure $`k`$'s unit, $`R_k`$ the fixed reference in the same unit, and $`w_k`$ the
swing weights. $`v_{i,t}`$ has no unit; call it **value points**. A plan's value is the sum of the
coefficients of the starts it makes.

```python
def value_table(portfolio: Portfolio, reference=REFERENCE, weights=WEIGHTS) -> dict[tuple[str, int], float]:
    """v[(project, start year)] for every start each project may use."""
    return {(p.project_id, t): value(raw(measures(portfolio, p, t)), reference, weights)
            for p in portfolio.projects for t in p.starts()}
```

```python
small = generate("small")
v = value_table(small)
```

```text
80 coefficients for 40 projects
P030 start 2029: rel 0.0709 saf 0.0079 env 0.0004 fin 0.2019 | v 0.2810 = $6,089k NPV-equivalent
P030 start 2030: rel 0.0660 saf 0.0073 env 0.0004 fin 0.1652 | v 0.2389 = $5,176k NPV-equivalent
P006 start 2030: rel 0.4152 saf 0.1424 env 0.0356 fin 0.0028 | v 0.5960 = $12,912k NPV-equivalent
P006 start 2031: rel 0.3714 saf 0.1273 env 0.0318 fin 0.0016 | v 0.5321 = $11,529k NPV-equivalent
P019 start 2028: rel 0.0229 saf 0.0381 env 0.0002 fin 0.0588 | v 0.1200 = $2,600k NPV-equivalent
P035 start 2027: rel 0.0185 saf 0.0064 env 0.0016 fin 0.0198 | v 0.0463 = $1,003k NPV-equivalent
P035 start 2028: rel 0.0201 saf 0.0069 env 0.0017 fin 0.0168 | v 0.0454 = $984k NPV-equivalent
P035 start 2029: rel 0.0208 saf 0.0071 env 0.0018 fin 0.0141 | v 0.0438 = $949k NPV-equivalent
P035 start 2030: rel 0.0208 saf 0.0071 env 0.0018 fin 0.0117 | v 0.0415 = $899k NPV-equivalent
```

Each row splits a coefficient into its four weighted scores, $`w_k\, m_{i,t,k} / R_k`$, which add up
to $`v`$. Read P030's 2029 financial part by hand: its NPV is $4,374k, a score of 4,374 / 5,000 =
0.8748, times the financial weight 0.2308 gives 0.2019. Small has 40 projects and 80 start variables,
so the table has 80 coefficients.

## Delay Changes Every Measure, Not Only NPV

Read the rows of one project from top to bottom. P030 and P006 lose value in every measure when they
start a year later: the NPV is discounted further and decays (lessons 7.2.1 to 7.2.4, *Financial evaluation*), and
the asset spends one more year of the window unrenewed, so fewer failures are avoided.

P035, a vegetation corridor widening, is the exception worth understanding. Its reliability, safety
and environmental parts *grow* with delay, from 0.0185 to 0.0208 on reliability. A widening has depth
0.8 (lesson 7.4.1): it makes the corridor 80% younger than it is *when the work is done*. An older
corridor gives the work more years to take away, and for this asset that outweighs the shorter window.
Its NPV falls faster, so its total still falls, from 0.0463 to 0.0415. Nothing is wrong: the
coefficients say exactly what the measures say, and that is why each start year needs its own.

A value function that gives a project one number, computed at its earliest start, would miss both
effects. The model would see no reason to start P030 early and no cost in putting it off.

## Value Points Restate as NPV-Equivalent Dollars

Value points mean nothing to a planner. Dollars do. The financial measure gives a conversion: one $k
of NPV earns $`w_{\text{fin}} / R_{\text{fin}}`$ points, so $`v`$ points are worth

```math
v^{\$}_{i,t} = v_{i,t}\, \frac{R_{\text{fin}}}{w_{\text{fin}}} \quad \text{\$k of NPV}
```

```python
def npv_equivalent(points: float, reference=REFERENCE, weights=WEIGHTS) -> float:
    """Value points restated as the $k of NPV that would earn the same points."""
    return points * reference["financial"] / weights["financial"]
```

That is the last column above: P030 started in 2029 is worth $6,089k NPV-equivalent, its $4,374k of
NPV plus what its reliability, safety and emissions benefits are worth at the board's prices. P006 is
worth $12,912k, though its own NPV is small:

```text
P006 start 2030: NPV $60k, 3,238,782 customer-minutes avoided
```

At $2.78 a customer-minute (lesson 7.4.3), 3,238,782 customer-minutes alone are worth about $9.0M.
The conversion multiplies every coefficient by the same positive number,
$`R_{\text{fin}} / w_{\text{fin}} = 5{,}000 / 0.2308`$, so it never reorders projects or plans. It is
only a better unit for the report: a plan's value stated as "so many $M of NPV-equivalent, of which so
many are NPV" is a sentence a finance partner can check, where "0.997 value points" is not.

## The Plan's Value Is a Linear Expression in the Start Variables

The objective of the selection model is the sum of the coefficients of the chosen starts:

```math
V(x) = \sum_{i \in P} \sum_{t \in T_i} v_{i,t}\, x_{i,t}
```

It is linear in $`x`$ because every coefficient is a fixed number computed before the model is built:
the normalization, the weights and the failure model all live outside the solver. That is a design
choice worth keeping. Anything computed per start before the model is built stays linear in $`x`$,
however complicated the computation. But a rule about the plan as a whole does not: a cap on the
plan's total score in one measure ("count reliability only up to the reference"), the plan's weakest
measure, or a reference computed from the chosen plan would each make $`V`$ nonlinear in $`x`$, and
would need extra variables and rows (section 8 and lessons 6.6.1 to 6.6.4 show how). A cap is not a smaller
weight: below the cap each unit counts in full and above it not at all, which no single coefficient
per start can say. In MathOpt the objective is one linear expression,
built with `fast_sum` (which, unlike Python's `sum`, is also safe on an empty list) and passed to
`model.maximize`, the way the OR-Tools MathOpt samples set an objective:

```python
def value_expression(x: dict, v: dict) -> mathopt.LinearExpression:
    """The plan's value, sum of v[i, t] x[i, t], as one MathOpt expression."""
    return mathopt.fast_sum(v[key] * x[key] for key in x)
```

```python
model = mathopt.Model(name="cipt_value")
x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
     for p in small.projects for t in p.starts()}
plan_value = value_expression(x, v)
model.maximize(plan_value)              # section 8 adds the rules and solves; here we only read it

plan = {"P030": 2029, "P006": 2030, "P019": 2028}
values = {var: 1.0 if plan.get(pid) == t else 0.0 for (pid, t), var in x.items()}
```

`mathopt.evaluate_expression` computes an expression's value for given variable values, so the
objective can be read for a hand-built plan without solving anything:

```text
plan {'P030': 2029, 'P006': 2030, 'P019': 2028}: value 0.9970 (sum of its coefficients 0.9970)
```

0.2810 + 0.5960 + 0.1200 = 0.9970: the expression and the table agree. A test that compares the two
on a few fixed plans catches a coefficient attached to the wrong variable, the kind of bug that solves
without complaint and picks the wrong plan.

<!-- practice 1 -->

## The Model

The multi-period selection model of lesson 6.4.2, whole, with this lesson's objective marked. The
rows are unchanged; only the objective coefficients change, from $`\text{npv}_{i,t}`$ to $`v_{i,t}`$.
Like lessons 7.2.4 and 7.3.4, it leaves out the region floors $`\text{floor}_r`$ of lesson 7.1.3.
There the NPV plan and the risk plan each funded at least $3,710k more than every region's floor, so
the floors did not bind and leaving them out changed nothing. This lesson solves nothing, so it
cannot say the same of the value plan: a plan solved with $`v_{i,t}`$ has to be checked against the
floors the same way, or the floor row of lesson 7.1.3 added back unchanged.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years;
$`K`$ = {reliability, safety, environmental, financial}, the measures.

**Parameters.**

| Parameter | Meaning | Unit |
| --- | --- | --- |
| $`m_{i,t,\text{rel}}`$ | customer-minutes of interruption avoided by starting $`i`$ in $`t`$, over the 10-year window | customer-minutes |
| $`m_{i,t,\text{saf}}`$ | expected safety incidents avoided | incidents |
| $`m_{i,t,\text{env}}`$ | emissions avoided | tCO2e |
| $`m_{i,t,\text{fin}} = \text{npv}_{i,t}`$ | net present value | $k |
| $`R_k > 0`$ | reference swing, same unit as $`m_{\cdot,\cdot,k}`$: 3,000,000; 1; 200; 5,000 | measure $`k`$'s unit |
| $`r_k \ge 0`$ | board's swing rating: 100; 80; 20; 60 | none |
| $`w_k = r_k / \sum_j r_j`$ | swing weight: 0.3846; 0.3077; 0.0769; 0.2308 | none |
| $`v_{i,t} = \sum_{k \in K} w_k\, m_{i,t,k} / R_k`$ | value coefficient | value points |
| $`c_{i,k}`$, $`B_y`$ | cost of $`i`$ in its $`k`$-th year of work; budget of year $`y`$ | $k |

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$ starts
in year $`t`$.

**Objective.**

```math
\max \; V(x) = \sum_{i \in P} \sum_{t \in T_i} v_{i,t}\, x_{i,t} \qquad \leftarrow \text{this lesson}
```

**Constraints** (lessons 6.4.1 and 6.4.2, unchanged).

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

**Rules on the value function itself**, checked when the coefficients are built, not by the solver:

```math
\begin{aligned}
& w_k \ge 0 \;\; \forall k \in K, \qquad \sum_{k \in K} w_k = 1 && \text{(weights)} \\
& m_{i,t,k} = 0 \;\Rightarrow\; \text{no contribution from } k && \text{(zero means no benefit)} \\
& R_k \text{ fixed for the planning cycle, in the unit of } m_{\cdot,\cdot,k} && \text{(references)}
\end{aligned}
```

In code the coefficients are `value_table(portfolio)`, keyed `(project_id, start)` like the start
variables `x_P030_2029`, and the objective is `value_expression(x, v)`.

## A Test Restates Every Unit and Expects the Same Values

Lesson 7.4.2 proved that the units cancel; a test checks that the code actually lets them. It
restates every measure in another unit (SAIDI minutes, incidents per 100, kilograms of CO2e, $M), with
the references restated the same way, rebuilds all 80 coefficients and compares. Then it does the
same with one mistake planted: the reliability reference left in customer-minutes.

```python
units = {"reliability": 1 / CUSTOMERS_SERVED, "safety": 100.0, "environmental": 1_000.0, "financial": 1 / 1_000}
reference = {k: REFERENCE[k] * units[k] for k in REFERENCE}
```

```text
new units: SAIDI minutes, incidents per 100, kg CO2e, $M
largest change in any coefficient: 5.6e-17
same order of all 80 coefficients: True
reliability reference left in customer-minutes: same order: False | top three [('P030', 2029), ('P028', 2030), ('P006', 2030)] instead of [('P006', 2030), ('P006', 2031), ('P030', 2029)]
```

Done right, no coefficient moves by more than rounding error and all 80 keep their order. With the
one stale reference, reliability shrinks 600,000-fold, P006 (mostly reliability) drops from first to
third, and P030 (mostly NPV) takes the lead. Every number in the broken table still looks plausible,
which is why the check has to be a test that runs on every change, not a review.

Two more properties are worth a test of their own: multiplying every weight by the same positive
number (say, ratings that total 100 instead of 260, without dividing) multiplies every coefficient by
that number, and a project with no benefit in any measure gets a coefficient of exactly 0.

<!-- practice 2 -->

## Summary

- **The value function is one coefficient per project and start year.** $`v_{i,t} = \sum_k w_k\,
  m_{i,t,k}/R_k`$: 80 coefficients for GridCap small's 80 start variables.
- **Delay changes every measure, not only NPV.** P030 loses value in all four; P035's partial-depth
  widening gains reliability with delay, while its NPV falls faster.
- **Value points restate as NPV-equivalent dollars.** Multiply by $`R_{\text{fin}}/w_{\text{fin}}`$:
  P030 in 2029 is $6,089k, P006 in 2030 $12,912k with $60k of NPV.
- **The plan's value is a linear expression in the start variables.** All the nonlinear work happens
  before the model; MathOpt gets `fast_sum` of $`v_{i,t} x_{i,t}`$, and `evaluate_expression` reads it
  for a fixed plan.
- **A test restates every unit and expects the same values.** Correctly restated, the largest change
  is $`5.6 \times 10^{-17}`$; one stale reference reorders the top three.

## Reference

| Item | Value |
| --- | --- |
| measures and units | customer-minutes, incidents, tCO2e, $k NPV |
| references $`R_k`$ | 3,000,000; 1; 200; 5,000 |
| ratings $`r_k`$ | 100; 80; 20; 60 (reliability, safety, environmental, financial) |
| weights $`w_k`$ | 0.3846; 0.3077; 0.0769; 0.2308 |
| coefficient | $`v_{i,t} = \sum_k w_k m_{i,t,k}/R_k`$ (value points) |
| NPV-equivalent | $`v \cdot R_{\text{fin}}/w_{\text{fin}}`$ ($k) |
| code | `value_table(portfolio)`, `npv_equivalent(points)`, `value_expression(x, v)` |

**Further reading:** OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt) (the
modeling interface and its linear objectives); [the MathOpt `basic_example.py`
sample](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/basic_example.py)
(an objective built as an expression and passed to `model.maximize`);
[`ortools/math_opt/python/expressions.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/expressions.py)
(`fast_sum` and `evaluate_expression`); UK Department for Communities and Local Government,
[Multi-criteria analysis: a manual](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/7612/1132618.pdf)
(2009), section 6.2.12 on the weighted sum and the conditions it needs.

## Challenges

1. A project's benefits are all zero except NPV of $5,000k. What is its coefficient, and its
   NPV-equivalent value?
2. The board decides benefits should count over 15 years instead of 10. Which parts of the model
   change: the coefficients, the variables, or the rows?
3. Someone proposes $`\max \min_k \text{score}_k`$ ("the plan's weakest measure") as the objective.
   Is it linear in $`x`$? What would section 8's weighted sums need to model it?

## Design Note: Build the Coefficients Outside the Model, and Keep Them

The value function is a few hundred lines of data handling and a dozen of arithmetic, and none of it
belongs in the solver. Build the table once from the snapshot, store it with the run (keyed by project
and start year, with the references, ratings and the code version that made it), and give the model
only the numbers. A planner who asks "why is P006 funded before P028?" can then be answered from the
stored table, measure by measure, without rerunning anything. And the capstone (section 13,
*Capstone*), in its milestone *Value: NPV by start year, risk reduction from PoF/RUL, weighted
value*, grades exactly this table against a reference.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**cipt_value.py.** Builds the value table for GridCap small, prints a few projects' coefficients by
start year with their NPV-equivalents, and evaluates the MathOpt objective on a hand-built plan (*The
Value Function Is One Coefficient*, *Delay Changes Every Measure*, *Value Points Restate*, *The Plan's
Value Is a Linear Expression*). *Try:* Add P001 and P002, a replace and a repair of the same line, to
the printed projects. Predict which one's reliability grows with delay.

- Program: [cipt_value.py](src/cipt_value.py)

**rescaling_check.py.** Restates every measure in new units, with and without restating one reference
(*A Test Restates Every Unit*). *Try:* Leave the financial reference in $k instead. Predict which
project comes first.

- Program: [rescaling_check.py](src/rescaling_check.py)
