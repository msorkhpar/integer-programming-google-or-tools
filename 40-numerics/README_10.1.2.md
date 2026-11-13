# 10.1.2 Coefficient Ranges and Scaling

A colleague hands over a version of the bridge-loan model from lesson 10.1.1. The NPVs came from
the finance system in dollars, so the objective is in dollars. The budgets came from the board
pack in millions, so the budget rows and the loan are in $M. And the switch row got
$`M = 10^9`$, "big enough for anything". It solves, and HiGHS returns the right plan. It also
prints two warnings, and its log shows matrix coefficients from about 0.1 to $`10^9`$.

Lesson 10.1.1 showed why such numbers are risky: tolerances are absolute, and a huge coefficient on
a binary turns the integrality tolerance into room. This lesson shows how to measure a model's
numbers, what the solver's own warnings say about them, and how to rescale the model, one unit at a
time, until its numbers fit the tolerances, without changing the plan. GridCap is a fictional
utility; its numbers are teaching data.

## The Model

Lesson 10.1.1's loan model, restated whole, with two unit factors added and the big-M left open.
The factors change the numbers in the model, never its meaning.

**Sets.** $`P`$ the projects; $`Y = \{2027, \dots, 2031\}`$; $`M \subseteq P`$ the must-do
projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$.

**Parameters.** $`v_i`$, $`c_{i,y}`$, $`B_y`$, $`L_y = B_y/10`$ and $`F = 300`$ as in lesson
10.1.1, all in $k; $`\rho = 0.05`$ the interest per $k borrowed. New:
$`o > 0`$, the objective's units per $k (1,000 for dollars, 1 for $k);
$`r > 0`$, the rows' units per $k ($`10^{-3}`$ for $M, 1 for $k);
$`\bar M_y`$, the switch row's big-M, in the rows' unit. ← this lesson

**Variables.** $`x_i \in \{0, 1\}`$ for $`i \in P`$; $`h_y \in \{0, 1\}`$ for $`y \in Y`$;
$`\ell'_y \ge 0`$ for $`y \in Y`$, the loan in the rows' unit, so $`\ell'_y = r\,\ell_y`$ with
$`\ell_y`$ the loan in $k. ← this lesson

**Objective.**

```math
\max \; \sum_{i \in P} o\, v_i\, x_i \;-\; \sum_{y \in Y} \left( o F\, h_y + \frac{o\,\rho}{r}\, \ell'_y \right)
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} r\, c_{i,y}\, x_i &\le r B_y + \ell'_y && \forall y \in Y && \text{(budget}_y) \\
\ell'_y &\le r L_y && \forall y \in Y && \text{(credit}_y) \\
\ell'_y &\le \bar M_y\, h_y && \forall y \in Y && \text{(switch}_y) \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(after}_c)
\end{aligned}
```

The variants of `loan_model.py`, as `Units(objective, rows, big_m)`:

| Variant | $`o`$ | $`r`$ | $`\bar M_y`$ |
| --- | --- | --- | --- |
| `MIXED`, the colleague's model | 1,000 ($) | $`10^{-3}`$ ($M) | $`10^9`$ |
| `HUGE_M` | 1 ($k) | 1 ($k) | $`10^9`$ |
| `TIGHT` | 1 ($k) | 1 ($k) | $`r L_y`$, the credit line |

```python
o, r = units.objective, units.rows
model = mathopt.Model(name="loan")
x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in portfolio.projects}
loan = {y: model.add_variable(lb=0, name=f"loan_{y}") for y in portfolio.years}
take = {y: model.add_binary_variable(name=f"take_{y}") for y in portfolio.years}
# One unit of loan is 1/r $k, so its interest is RATE / r $k, or RATE * o / r objective units.
model.maximize(sum(p.value * o * x[p.project_id] for p in portfolio.projects)
               - sum(FEE * o * take[y] + RATE * o / r * loan[y] for y in portfolio.years))
```

```python
spend[y] = sum(spend_in(p, y) * r * x[p.project_id] for p in portfolio.projects if spend_in(p, y))
model.add_linear_constraint(spend[y] <= portfolio.budget[y] * r + loan[y], name=f"budget_{y}")
model.add_linear_constraint(loan[y] <= credit_line(portfolio, y) * r, name=f"credit_{y}")
big_m = credit_line(portfolio, y) * r if units.big_m is None else units.big_m
model.add_linear_constraint(loan[y] <= big_m * take[y], name=f"switch_{y}")
```

## Four Ranges Describe a Model's Numbers: Matrix, Cost, Bound and RHS

Lesson 2.4.2 read the four **coefficient ranges** at the top of a HiGHS log: for each kind of
number in the model, the smallest and the largest absolute value. The kinds are the **matrix** (the
coefficients in the rows), the **cost** (the objective's coefficients), the **bounds** (variables'
finite bounds) and the **RHS** (the rows' finite right-hand sides). Zeros and infinite values are
left out, and so are bounds of 0, so a binary's bounds $`[0, 1]`$ add only the 1.

The same numbers can be computed from a MathOpt model, which a test can then check:

```python
def coefficient_ranges(model: mathopt.Model) -> dict[str, tuple[float, float]]:
    """Smallest and largest absolute value of each kind of number, as HiGHS's log reports them.

    Zeros and infinite values are left out, and so are bounds of 0: a binary's bounds [0, 1]
    contribute 1.
    """
    def finite(values):
        return [abs(v) for v in values if v != 0 and math.isfinite(v)]

    kinds = {
        "Matrix": finite(c for row in model.linear_constraints()
                         for c in (row.get_coefficient(v) for v in model.row_nonzeros(row))),
        "Cost": finite(model.objective.get_linear_coefficient(v) for v in model.variables()),
        "Bound": finite(b for v in model.variables() for b in (v.lower_bound, v.upper_bound)),
        "RHS": finite(b for row in model.linear_constraints() for b in (row.lower_bound, row.upper_bound)),
    }
    return {kind: (min(values), max(values)) for kind, values in kinds.items() if values}
```

`model.row_nonzeros(row)` lists the variables with a nonzero coefficient in a row, and
`row.get_coefficient(v)` reads one. `ranges.py` prints the function's result for the `TIGHT` model
next to HiGHS's log:

```text
HiGHS's log:
  MIP loan has 21 rows; 50 cols; 85 nonzeros; 45 integer variables (45 binary)
  Coefficient ranges:
    Matrix  [1e+00, 6e+03]
    Cost    [5e-02, 4e+03]
    Bound   [1e+00, 1e+00]
    RHS     [1e+00, 9e+03]
coefficient_ranges(model):
  Matrix  [1e+00, 6e+03]   exact: 1 to 5,680   span 5,680
  Cost    [5e-02, 4e+03]   exact: 0.05 to 4,374   span 87,480
  Bound   [1e+00, 1e+00]   exact: 1 to 1   span 1
  RHS     [1e+00, 9e+03]   exact: 1 to 8,890   span 8,890
```

The two agree; HiGHS rounds each value to one significant digit. The **span** of a range is its
largest value divided by its smallest, the number of times the largest is bigger. Each number can
be traced to the model:

- **Matrix, 1 to 5,680:** the 1s are the loan's coefficient in a budget row, the switch's and
  credit's coefficients, and the must and after rows; 5,680 is the largest one-year spend of a
  project, in $k. With the tight $`M`$, the switch coefficients are the credit lines, at most 889.
- **Cost, 0.05 to 4,374:** 0.05 is the interest on one $k of loan; 4,374 is the largest NPV.
- **Bound, 1:** only the binaries have a finite nonzero bound. The loans have none above.
- **RHS, 1 to 8,890:** the must rows' 1s, and the budgets.

Every span is below $`10^5`$. The rows' numbers sit between 1 and $`10^4`$, where lesson 10.1.1's
tolerances are a tenth of a cent and floats keep twelve digits to spare.

<!-- practice 1 -->

## A Model Written in Mixed Units Spreads Its Numbers Over Many Powers of Ten

The colleague's `MIXED` model is the same model in other units. `rescale.py` prints its ranges and
every warning line in HiGHS's log:

```text
mixed ($ objective, $M rows, M = 1e9)
  Matrix [1e-01, 1e+09]  Cost [3e+04, 4e+06]  Bound [1e+00, 1e+00]  RHS [8e-01, 9e+00]
  WARNING: Problem has some excessively large costs
  WARNING:    Consider scaling the objective by 1e-1, or setting the user_objective_scale option to -3
  OPTIMAL, objective 23,161,500.0 = $23,161.5k, 27 projects, loans $k {2030: 750}
```

The plan is right: $23,161.5k, as lesson 10.1.1's tight model found, and one loan, $750k in 2030.
The numbers are not:

- **The matrix spans ten powers of ten**, from about 0.1 (a small project's spend in $M) to
  $`10^9`$ (the big-M). Gurobi's numerical guidelines say the ratio of the largest to the smallest
  matrix coefficient should ideally stay below $`10^6`$ and never exceed $`10^9`$; this one is
  above it.
- **The costs reach $`4 \times 10^6`$**, an NPV in dollars. The same guidelines ask for objective
  values of good plans below about $`10^6`$; this objective is $`2.3 \times 10^7`$.
- **The RHS is small**, 0.8 to 9: the rows are in $M, where a row's tolerance of $`10^{-6}`$ is
  worth $1 to HiGHS (lesson 10.1.1's table).

HiGHS warned about the costs, and suggested a fix. It said nothing about the $`10^9`$ in the
matrix. Lesson 10.1.3 measures which numbers HiGHS warns about; here the point is that the model is
badly scaled whether or not a warning appears.

## Rescaling Multiplies a Row, a Column or the Objective, and Leaves the Plan Unchanged

**Rescaling** changes the units in which a model's numbers are written. It comes in three kinds,
each of which leaves the set of allowed plans, and the best plan, exactly as they were:

- **A row times a positive number.** $`a^\top x \le b`$ and $`(s\,a)^\top x \le s\,b`$, with
  $`s > 0`$, allow the same $`x`$. Writing a budget row in $k instead of $M multiplies it by
  1,000.
- **A column times a positive number.** Replacing a variable $`\ell`$ by $`\ell = \ell'/r`$
  multiplies its coefficient in every row and in the objective by $`1/r`$, and its bounds by
  $`r`$. Measuring the loan in $k instead of $M is that substitution.
- **The objective times a positive number.** $`\max\, f(x)`$ and $`\max\, s f(x)`$, with
  $`s > 0`$, have the same best plans; only the reported value is $`s`$ times larger. Writing
  NPV in $k instead of dollars multiplies the objective by $`1/1000`$.

In the model above, $`o`$ is an objective scaling and $`r`$ scales every money row and the loan's
column together. `rescale.py` builds the model four times, changing one thing at a time, and
solves each with HiGHS's defaults:

```python
STEPS = (
    MIXED,
    Units(objective=1, rows=0.001, big_m=1e9, name="objective in $k"),
    HUGE_M,
    TIGHT,
)
```

```text
mixed ($ objective, $M rows, M = 1e9)
  Matrix [1e-01, 1e+09]  Cost [3e+04, 4e+06]  Bound [1e+00, 1e+00]  RHS [8e-01, 9e+00]
  WARNING: Problem has some excessively large costs
  WARNING:    Consider scaling the objective by 1e-1, or setting the user_objective_scale option to -3
  OPTIMAL, objective 23,161,500.0 = $23,161.5k, 27 projects, loans $k {2030: 750}
objective in $k
  Matrix [1e-01, 1e+09]  Cost [3e+01, 4e+03]  Bound [1e+00, 1e+00]  RHS [8e-01, 9e+00]
  OPTIMAL, objective 23,161.5 = $23,161.5k, 27 projects, loans $k {2030: 750}
huge M ($k, M = 1e9)
  Matrix [1e+00, 1e+09]  Cost [5e-02, 4e+03]  Bound [1e+00, 1e+00]  RHS [1e+00, 9e+03]
  OPTIMAL, objective 23,161.5 = $23,161.5k, 27 projects, loans $k {2030: 750}
tight ($k, M = credit line)
  Matrix [1e+00, 6e+03]  Cost [5e-02, 4e+03]  Bound [1e+00, 1e+00]  RHS [1e+00, 9e+03]
  OPTIMAL, objective 23,161.5 = $23,161.5k, 27 projects, loans $k {2030: 750}
same projects in every step: True
```

Step by step:

- **The objective in $k** divides every cost by 1,000: the cost range falls from
  $`[3 \times 10^4, 4 \times 10^6]`$ to $`[30, 4{,}000]`$, the reported objective falls from
  23,161,500 to 23,161.5, and the warnings stop. The interest coefficient is $`o\rho/r`$: with
  $`o = 1`$ and $`r = 10^{-3}`$ it is 50, the interest in $k on one $M of loan.
- **The rows in $k** multiply every money row and the loan's column by 1,000: the RHS moves from
  0.8–9 to 1–8,890, and the smallest matrix entry from 0.1 to 1. In $k a row's tolerance of
  $`10^{-6}`$ is a tenth of a cent instead of a dollar. The matrix still reaches $`10^9`$.
- **The tight M** replaces $`10^9`$ by the credit line. The matrix span drops from $`10^9`$ to
  5,680.

The plan never changed: the same 27 projects, the same $750k loan in 2030, and the same value once
converted to $k with `in_k`. That is what rescaling must do. A test of a rescaled model should
check both halves: the ranges shrank, and the plans allowed and refused are the same.

## A Valid M Is Part of Scaling: Replace 1e9 With the Bound the Data Give

Units cannot fix the last step. $`10^9`$ is not a unit problem: in $k, $M or dollars, it is far
larger than any loan the model allows. The data say how large a loan can be: the credit line,
$`L_y`$. Lesson 6.2.1 derived such an $`M`$ from bounds, and showed it is the smallest valid one:
the credit row already caps the loan at $`L_y`$, so the switch row needs no more.

The step table shows why it belongs to scaling. After the units were fixed, the $`10^9`$ alone kept
the matrix span at $`10^9`$; with the credit line it fell to 5,680. And lesson 10.1.1 showed what
that span costs: a switch of $`10^{-6}`$ times $`10^9`$ is room for $1,000k of loan, more than any
credit line, while $`10^{-6}`$ times 889 is less than a dollar.

The second line of the step table makes one more point. The model "objective in $k" still has
$`10^9`$ in its matrix and 0.1 at the other end, and HiGHS printed no warning about it. A model
without warnings is not a well-scaled model; the ranges are the measure.

<!-- practice 2 -->

## HiGHS Can Scale the Objective and Bounds for You, Not the Matrix

HiGHS's warning offered a second fix: "setting the user_objective_scale option to -3". HiGHS's
option list describes `user_objective_scale` and `user_bound_scale` as exponents of a power-of-two
scaling of the objective and of the bounds. `user_scale.py` solves the `MIXED` model with it:

```python
params = mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(int_options={"user_objective_scale": -3}))
result, log = solve(lm.model, params=params)
```

```text
MIP loan has 21 rows; 50 cols; 85 nonzeros; 45 integer variables (45 binary)
Assessing costs and bounds after applying user_objective_scale option value of -3
Coefficient ranges:
  Matrix  [1e-01, 1e+09]
  Cost    [3e+03, 5e+05]
  Bound   [1e+00, 1e+00]
  RHS     [8e-01, 9e+00]
Presolving model
...
After solving the user-scaled model, the unscaled solution has objective value 23161500
result.objective_value(): 23,161,500.0
```

HiGHS multiplied every cost by $`2^{-3} = 1/8`$, which brought them under its warning threshold,
solved, and reported the objective in the model's own units again: MathOpt returns 23,161,500, as
before. A power of two changes only a float's exponent, so this scaling adds no rounding error of
its own.

It is a convenience, not a substitute for choosing units. The matrix line still reads
$`[10^{-1}, 10^9]`$: no option rescales the colleague's big-M away. HiGHS also scales the matrix
internally while it solves (its option `simplex_scale_strategy` chooses how, with equilibration
the default), but that is the solver's working copy. The model you wrote, the tolerance that applies
to its rows, and the plan you round are still in your units, and only you know that the credit line
is the right $`M`$.

## Summary

- **Four ranges describe a model's numbers: matrix, cost, bound and RHS.** Compute them from the
  model, compare them with the log, and know which data each extreme comes from.
- **A model written in mixed units spreads its numbers over many powers of ten.** Dollars next to
  millions and an $`M`$ of $`10^9`$ spread the matrix over ten powers of ten and put the objective
  near $`10^7`$, outside the ranges the numerical guidelines recommend.
- **Rescaling multiplies a row, a column or the objective, and leaves the plan unchanged.** The same
  27 projects and the same loan came back at every step; only the numbers moved.
- **A valid M is part of scaling: replace 1e9 with the bound the data give.** The credit line cut
  the matrix span from $`10^9`$ to 5,680, which no change of units could do.
- **HiGHS can scale the objective and bounds for you, not the matrix.** `user_objective_scale`
  silenced the warning; the $`10^9`$ stayed.

## Reference

| Range | What it covers | Left out |
| --- | --- | --- |
| Matrix | coefficients in the rows | zeros |
| Cost | objective coefficients | zeros |
| Bound | variables' bounds | zeros and infinite bounds |
| RHS | rows' right-hand sides, both sides of a ranged row | zeros and infinite sides |

| Rescaling | What changes | What stays |
| --- | --- | --- |
| row $`i`$ times $`s > 0`$ | row $`i`$'s coefficients and right-hand side | allowed plans, optimum, objective value |
| column $`j`$: $`x_j = x'_j / s`$ | column $`j`$'s coefficients ($`\times 1/s`$) and bounds ($`\times s`$) | allowed plans (in the new unit), optimum |
| objective times $`s > 0`$ | every cost, and the reported objective | allowed plans, best plans |

| Guideline (Gurobi's numerical guidelines) | Value |
| --- | --- |
| matrix span, largest / smallest | ideally below $`10^6`$, never above $`10^9`$ |
| right-hand sides and bounds | about $`10^6`$ or less |
| objective of good plans | below about $`10^6`$ |

**Further reading:** [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (section *Scaling of problem data*: units too small or too large for the solver's tolerances, and the advice to check that the data's scale suits them); [MathOpt `Model` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`linear_constraints`, `row_nonzeros`, `variables` and the objective's coefficients, which `coefficient_ranges` reads); [Gurobi: Tolerances and User-Scaling](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/tolerances_scaling.html) (recommended ranges, and changing units, dollars to millions, to bring numbers into them); [Gurobi: Does my Model have Numerical Issues?](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/modelissues.html) (the coefficient span to aim for and the one never to exceed); [HiGHS options](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`user_objective_scale`, `user_bound_scale` and `simplex_scale_strategy`).

## Challenges

1. Write the colleague's model with the objective in $M as well as the rows. Predict its cost range
   and whether HiGHS warns.
2. A planner wants loans reported in dollars. Where does that conversion belong: in the model's
   units, or in the report? Give one reason from this lesson.
3. Run `rescale.py` with a fifth step: the `TIGHT` model with the rows in $M. Predict which ranges
   change from the last step.

## Design Note: Scale in the Data Layer, Once

Each rescaling step above changed two numbers in one place, `Units`, and the model builder applied
them everywhere. That is the shape to keep: the builder takes data in one unit and never mixes
units itself, and conversions for reports happen after the solve (`in_k`). A model whose rows are
written by different people from different systems, as the colleague's was, needs that rule more
than any other.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**ranges.py.** The `TIGHT` model's coefficient ranges from `coefficient_ranges` and from HiGHS's
log, with their exact values and spans (*Four Ranges Describe a Model's Numbers*). *Try:* Build the
`HUGE_M` model instead. Predict which of the four ranges changes.

- Program: [ranges.py](src/ranges.py)

**rescale.py.** The loan model in four units and M choices, with each one's ranges, HiGHS's
warnings and its plan (*A Model Written in Mixed Units*, *Rescaling Multiplies a Row*, *A Valid M
Is Part of Scaling*). *Try:* Add a step with the objective in $M (`objective=0.001`). Predict
whether HiGHS warns about small costs.

- Program: [rescale.py](src/rescale.py)

**user_scale.py.** The `MIXED` model solved with HiGHS's `user_objective_scale` set to $`-3`$
(*HiGHS Can Scale the Objective and Bounds for You*). *Try:* Set it to $`-10`$ instead. Predict the
cost range HiGHS prints.

- Program: [user_scale.py](src/user_scale.py)

**loan_model.py.** The model builder and the helpers, shared with lesson 10.1.1.

- Library: [loan_model.py](src/loan_model.py)
