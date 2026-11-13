# 7.2.4 Precomputing NPV Coefficients by Start Year

Lesson 6.4.1 gave every start variable $`x_{i,t}`$ an objective coefficient $`\text{npv}_{i,t}`$, read
from GridCap's data: P022 is worth $1,496k, $1,287k or $1,102k for a start in 2027, 2028 or 2029.
The model trusted those numbers, and the plan it found (NPV $24,260k on GridCap small) is only as
good as they are. This lesson opens the table. It builds each coefficient from the project's cash
flow with the tools of lessons 7.2.1–7.2.3, shows two mistakes that make a table quietly wrong,
rebuilds GridCap's whole table and finds it equal to the stored one, entry for entry, and then
solves lesson 6.4.2's model with the rebuilt table at three discount rates.

GridCap is a fictional utility's portfolio, generated for this course. The mains relining in the
third rule is invented for this lesson.

## A Start-Year Coefficient Is the Project's Cash Flow, Shifted to Start in That Year

A project's cash flow is written once, relative to its own start: it spends $`c_{i,k}`$ in its
$`k`$-th year of work ($`k = 0`$ is the start year) and receives benefits $`b_{i,k}(t)`$ in year
$`k`$ after starting, which may depend on the start $`t`$. Starting in year $`t`$ moves every amount to
calendar year $`t + k`$. The coefficient is the NPV of that moved cash flow, on the model's one
valuation date $`y_0`$:

```math
\text{npv}_{i,t} = \sum_{k} \frac{b_{i,k}(t) - c_{i,k}}{(1 + r)^{\,t + k - y_0}} \qquad \forall i \in P,\ t \in T_i
```

The shift is the same one lesson 6.4.2 used for the budget rows: the amount in calendar year $`y`$
is the profile entry $`c_{i,\,y - t}`$. In code, one function moves the cash flow and one sum values
it, for every allowed start:

```python
def start_year_flows(costs: tuple[float, ...], benefits: dict[int, float], start: int) -> dict[int, float]:
    """A project's net cash flow by calendar year if it starts in `start`.

    `costs[k]` is spent in year start + k; `benefits[k]` is received in year start + k.
    """
    flows: dict[int, float] = {}
    for k, cost in enumerate(costs):
        flows[start + k] = flows.get(start + k, 0.0) - cost
    for k, benefit in benefits.items():
        flows[start + k] = flows.get(start + k, 0.0) + benefit
    return flows


def npv_by_start_year(costs: tuple[float, ...], benefits_for, starts, rate: float,
                      valuation_year: int) -> dict[int, float]:
    """{start year: NPV on `valuation_year`}, one entry per allowed start.

    `benefits_for(start)` returns that start's benefits by year offset, so a benefit that shrinks
    with delay (as GridCap's does) is one function, not a special case.
    """
    return {t: present_value(start_year_flows(costs, benefits_for(t), t), rate, valuation_year)
            for t in starts}
```

GridCap's benefit model is simple, and it is worth stating exactly, because the table depends on
it. Each project $`i`$ delivers one benefit, counted in its start year:
$`B_i = \rho_i \cdot \text{capex}_i`$, where the **benefit ratio** $`\rho_i`$ (between 1.15 and 2.05)
says how much the work is worth per dollar of cost. Every year the project waits past its earliest
start $`e_i`$, the benefit shrinks by the **decay** $`\delta_i`$ (between 3% and 8%): the risk the
work would remove is carried a year longer. So $`b_{i,0}(t) = \rho_i\, \text{capex}_i\, (1 - \delta_i)^{t - e_i}`$
and $`b_{i,k}(t) = 0`$ for $`k > 0`$. Costs are the 2027-dollar profile, unescalated, and
$`r = 7\%`$, $`y_0 = 2027`$: by lesson 7.2.2, real dollars at a real rate.

```python
def gridcap_benefits(project: Project, ratio: float, decay: float):
    """GridCap's benefit model: one amount in the start year, smaller by `decay` per year of delay."""
    def benefits_for(start: int) -> dict[int, float]:
        return {0: project.capex * ratio * (1 - decay) ** (start - project.earliest_start)}
    return benefits_for
```

On P022, whose ratio and decay are 1.4953 and 0.0313:

```text
P022 costs (360, 720, 1470), starts [2027, 2028, 2029], benefit ratio 1.4953, decay 0.0313
start  benefit  PV benefit  PV cost   NPV      stored
2027   3813.0      3813.0   2316.9   1496.1    1496
2028   3693.6      3452.0   2165.3   1286.7    1287
2029   3578.1      3125.2   2023.6   1101.6    1102
cash flow if P022 starts in 2028: {2028: 3333.6, 2029: -720.0, 2030: -1470.0}
```

Rounded to a whole $k, the computed NPVs are the stored ones. Read the columns to see why a later
start is worth less. Two things happen to the benefit: it shrinks by the decay (3,813.0 to
3,693.6) and it is discounted one more year (to 3,452.0). The cost's present value falls too
(2,316.9 to 2,165.3), because the same payments move a year further away. Delay saves on the cost
side and loses on the benefit side; here the benefit's loss is bigger, so the NPV falls by about
$209k for the first year of delay.

## Discount Every Start to One Valuation Date

The most common mistake in a start-year table is to value each start from its own start year: "the
NPV of the project, if we start it in $`t`$", computed as if $`t`$ were today. Each entry then looks
reasonable, and the table is wrong as a set:

```text
start  to 2027   to own start
2027    1496.1        1496.1
2028    1286.7        1376.8
2029    1101.6        1261.2
cost alone, each to its own start: {2027: -2316.9, 2028: -2316.9, 2029: -2316.9}
```

Valued from its own start, P022's cost is $2,316.9k in every year, so waiting costs nothing on that
side, and the only loss left is the decay. A 2029 start then seems to give up $235k against a 2027
start; on one common date it gives up $395k. A project with no decay would have the same entry in
every year, and a model would defer it to the last allowed year for free, pushing work out of every
year's budget into the future at no cost. The fix is the design note of lesson 7.2.1: one valuation
date for the whole model, the same for every project and every start. In the formula above, that is
$`y_0`$ in the exponent, not $`t`$.

<!-- practice 1 -->

## Count Benefits to the End of the Asset's Life, Not the End of the Plan

GridCap books each benefit as one amount in the start year. Many real benefits are streams instead:
fewer breaks, outage minutes and repairs, year after year, for as long as the new asset lasts, which
is usually far longer than the plan. Take an invented mains relining: $600k in each of two years of
work, then $120k a year of avoided breaks for 25 years. The plan runs 2027–2031. If the benefits are
cut at the end of the plan, the table is ruined:

```python
for t in (2027, 2028, 2029, 2030):
    benefits = {k: 120 for k in range(len(costs), len(costs) + life)}
    full = start_year_flows(costs, benefits, t)
    cut = {y: a for y, a in full.items() if y <= plan_end}
```

```text
start  full life  cut at 2031  benefit years counted
2027      146.2       -866.4     3 of 25
2028      136.6       -895.3     2 of 25
2029      127.7       -922.3     1 of 25
2030      119.3       -947.5     0 of 25
```

Counted over the asset's life, the relining is worth about $146k and loses a little with each year
of delay (each entry is the one above divided by 1.07, because the whole cash flow moves a year).
Cut at 2031, it is worth nothing at any start, and later starts are punished most because they keep
the fewest benefit years: a 2030 start keeps none. A model with that table would never fund
long-lived work late in the plan, and it would favour quick-payback work everywhere. This is the
**end effect** of a finite horizon. Klevorick's 1966 paper on capital budgeting by mathematical
programming raises it explicitly: projects started inside the horizon keep paying after it ends,
and the paper adds, to the last period's return, the project's value at that point. Counting the
benefit stream over the asset's full life, as here, does the same job.

The plan's horizon limits *when the decisions are made* (which start variables exist). It does not
limit *which consequences count*. A coefficient should include every cash flow the decision causes,
whenever it falls.

<!-- practice 2 -->

## GridCap's Table Is This Calculation, Entry for Entry

GridCap's generator draws each project's benefit ratio and decay, computes the NPV of every allowed
start as above, rounds it to a whole $k and stores only the result (`Project.npv`). The ratio and the
decay are not in the data. In practice they are what finance hands you: a benefit forecast per
project, and a view of what delay costs. To check the table, the library `gridcap_assumptions.py`
replays the generator with the same seed and records the two numbers as they are drawn; it leaves
the portfolio unchanged (a module test checks its content hash). Then every entry is rebuilt from
the cash flow:

```python
def coefficient_table(portfolio: Portfolio, assumptions: dict, rate: float) -> dict[tuple[str, int], int]:
    """{(project id, start year): NPV in $k on the first plan year, rounded to a whole $k}."""
    table = {}
    for p in portfolio.projects:
        ratio, decay = assumptions[p.project_id]
        npv = npv_by_start_year(p.cost_profile, gridcap_benefits(p, ratio, decay), p.starts(), rate,
                                valuation_year=portfolio.years[0])
        for t, value in npv.items():
            table[p.project_id, t] = math.floor(value + 0.5)
    return table
```

The rebuilt table is compared with the stored one for three sizes. The cost side is also checked
independently with numpy-financial: each start's costs are laid on a calendar-year list from 2027
(zeros before the start) and discounted with `npf.npv`, whose first value is not discounted, the
same convention as `present_value` (lesson 7.2.1).

```text
tiny    entries   13  rebuilt   13  different 0  cost PV vs npf.npv: largest gap 4.5e-13
small   entries   80  rebuilt   80  different 0  cost PV vs npf.npv: largest gap 4.5e-13
medium  entries  887  rebuilt  887  different 0  cost PV vs npf.npv: largest gap 9.1e-13
```

All 980 entries match, and the cost present values agree with numpy-financial to within float
rounding. So the coefficients of lessons 6.4.1–6.4.4 are exactly NPVs of shifted cash flows on one
date, in real 2027 dollars at 7%, with a benefit that decays with delay. Rounding happens once, at
the end; rounding the benefit and the cost separately could move an entry by $1k.

Two simplifications of GridCap's model are worth knowing, because a real table would not make them.
Its benefit is one lump in the start year, before the work is finished; the previous rule's stream,
starting after the work, is the more faithful shape. And its costs are not escalated, which is
correct only if they rise with general inflation (lesson 7.2.2).

## The Model

The rebuilt table goes into lesson 6.4.2's model unchanged. Restated here in full, with the
coefficient written out. One family of rows is left out on purpose: the region floors
$`\text{floor}_r`$ of lesson 7.1.3. The section after this one shows that they do not bind on this
data, so the model without them finds the same plan as the floored base scenario of 7.1.3.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years, with first year $`y_0`$; $`T_i \subseteq Y`$ the
start years project $`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the
alternative groups; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`c_{i,k}`$, project $`i`$'s cost in its $`k`$-th year of work ($k, 2027 dollars);
$`\rho_i`$, its benefit ratio; $`\delta_i`$, its yearly decay; $`e_i`$, its earliest start; $`r`$, the
real discount rate; $`B_y`$, the budget of year $`y`$ ($k). From them, computed before the model is
built:

```math
\text{npv}_{i,t} = \frac{\rho_i \,\text{capex}_i\, (1 - \delta_i)^{t - e_i}}{(1 + r)^{t - y_0}}
- \sum_{k} \frac{c_{i,k}}{(1 + r)^{t + k - y_0}}, \qquad \text{capex}_i = \sum_k c_{i,k}
```

rounded to a whole $k.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$: project $`i`$ starts in year
$`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

| Label | Row name in `rate_in_model.py` |
| --- | --- |
| once$`_i`$, must$`_i`$ | `once_P017`, `must_P002` |
| alt$`_g`$ | `alt_G006` |
| after$`_{c,t}`$ | `after_P023_2029` |
| budget$`_y`$ | `budget_2029` |

The rate $`r`$ appears in no constraint and in no variable. It is inside the parameters
$`\text{npv}_{i,t}`$, and nowhere else.

## The Rate Reaches the Plan Only Through the Coefficients

`rate_in_model.py` builds that model in MathOpt as lesson 6.4.1 did, with binary start variables,
the rows above, and an objective whose coefficients are the table. The objective is one line:

```python
model.maximize(sum(npv[key] * var for key, var in x.items()))
```

Solved with HiGHS at a zero gap, with the table rebuilt at 3%, 7% and 12%:

```text
rate 3%: NPV $25,300k, started 27 of 40, 9 later than earliest
rate 7%: NPV $24,260k, started 27 of 40, 9 later than earliest
rate 12%: NPV $23,161k, started 25 of 40, 7 later than earliest
starts that differ from the 7% plan at 3%: 0
starts that differ from the 7% plan at 12%: 14
```

At 7% the rebuilt table gives exactly the plan lesson 6.4.1 found, which lesson 6.4.2's spread-cost
model finds again: NPV $24,260k, 27 projects started, 9 of them late. That closes the loop: the model
of section 6 and the finance of this module agree.

It is also the NPV of lesson 7.1.3's base scenario, although that scenario adds the region floors
this model leaves out. The program checks the 7% plan against them:

```text
7% plan, capex funded above each region floor ($k): Ridge 5,860, Valley 8,430, Coast 9,680, Plains 3,710; every floor met: True
```

Every region gets at least $3,710k more than its floor. Dropping rows can only let a plan do
better; this plan already keeps the dropped rows, so it is optimal with them too, and the floored
model has the same $24,260k. The floors do not bind on GridCap small. On data where one did, the row
$`\sum_{i \in P_r} \text{capex}_i \sum_{t \in T_i} x_{i,t} \ge F_r`$ of lesson 7.1.3 goes back in.

At 3% every coefficient changes, and the plan does not move at all. At 12%, 14 starts change and two
fewer projects are funded. A plan can be insensitive to the rate over a wide range and then change
in many places at once, because the solver compares whole combinations of projects, not one
project at a time. The program prints which projects moved; explaining *why* each one moved is the
job of the tools in section 9. A sensitivity run like this one, re-solving at the rates finance
might plausibly argue for, is cheap and tells planners whether the rate is a decision they need to
fight over.

One warning about the NPV column: $25,300k at 3% and $23,161k at 12% are not "more" and "less"
value for the same plan. They are measured with different yardsticks. Compare plans at one rate;
across rates, compare what the plans do.

## Summary

- **A start-year coefficient is the project's cash flow, shifted to start in that year.** Move
  every amount from year $`k`$ of the project to calendar year $`t + k`$, then take the NPV.
- **Discount every start to one valuation date.** Valuing each start from its own year makes delay
  look free (P022: $235k of loss shown instead of $395k).
- **Count benefits to the end of the asset's life, not the end of the plan.** Cutting at the
  horizon turned a $146k project into a loss at every start.
- **GridCap's table is this calculation, entry for entry.** 980 of 980 entries rebuilt; the cost
  side matches `npf.npv`.
- **The rate reaches the plan only through the coefficients.** GridCap small's plan is the same at
  3% and 7% and changes 14 starts at 12%.

## Reference

| Symbol | Meaning |
| --- | --- |
| $`c_{i,k}`$ | cost of project $`i`$ in its $`k`$-th year of work |
| $`b_{i,k}(t)`$ | benefit of project $`i`$ in year $`k`$ after a start in $`t`$ |
| $`y_0`$ | the valuation year, the same for every entry (GridCap: 2027) |
| $`\text{npv}_{i,t}`$ | $`\sum_k (b_{i,k}(t) - c_{i,k})(1 + r)^{-(t + k - y_0)}`$ |
| $`\rho_i`$, $`\delta_i`$ | GridCap's benefit ratio and decay per year of delay |

| Check a start-year table for | Test |
| --- | --- |
| one valuation date | a cost-only table falls with later starts |
| the shift | the cost of a start in $`t`$ lands in years $`t, t+1, \dots`$ |
| the end effect | benefits counted to the end of the asset's life |
| the arithmetic | each entry against `npf.npv` on a calendar-year list |
| the convention | `npf.npv` does not discount `values[0]` |

**Further reading:** [OR-Tools MathOpt basic example](https://developers.google.com/optimization/math_opt/basic_example)
(building and solving a MathOpt model, and reading its result); [OR-Tools MathOpt
`integer_programming.py` sample](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py)
(integer variables and named rows); [numpy-financial: `npv`](https://numpy.org/numpy-financial/latest/_api_stubs/numpy_financial.npv.html)
(the check used on the cost side); [Klevorick, *Mathematical Programming and Capital Budgeting Under
Risk*, 1966](https://www.princeton.edu/%7Eerp/ERParchives/archivepdfs/R14.pdf) (footnote 3: returns
after the planning horizon, and valuing them through the last period).

## Challenges

1. Escalate GridCap's costs at a real 1% a year from 2027 and rebuild the small table. How many
   entries change, and in which direction?
2. Replace GridCap's lump benefit with a stream: $`\rho_i\,\text{capex}_i / 20`$ a year for twenty
   years after the work ends. Does the 7% plan change?
3. Re-solve at 8%, 9%, 10% and 11%. Find the lowest rate at which the plan differs from the 7% one.

## Design Note: Precompute the Table, Do Not Model the Finance

The NPV of a start is a nonlinear function of the rate, and its benefit can depend on the start in
any way finance likes. None of that belongs in the solver. Precompute $`\text{npv}_{i,t}`$ for every
allowed start, check it against an independent library, store it with the data, and give the model a
linear objective. The model stays a MILP, the finance stays testable on its own, and a change of
rate or benefit forecast is a change of data, not of model code. It also means the table is a place
where errors hide, so each check in the reference table above belongs in the project's tests.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**start_year_table.py.** Builds P022's NPV for each start from its cash flow and prints it beside
the stored value (*A Start-Year Coefficient Is the Project's Cash Flow*). *Try:* Pick P036, which
has four allowed starts. Predict whether its NPV falls by the same amount each year.

- Program: [start_year_table.py](src/start_year_table.py)

**own_start.py.** Values P022's starts on a common date and on their own start years (*Discount
Every Start to One Valuation Date*). *Try:* Set the decay to 0 in the program. Predict the "to own
start" column.

- Program: [own_start.py](src/own_start.py)

**end_effect.py.** Values a relining over its full life and with benefits cut at the plan's end
(*Count Benefits to the End of the Asset's Life*). *Try:* Extend the plan to 2040. Predict which
starts now agree with the full-life column.

- Program: [end_effect.py](src/end_effect.py)

**reproduce_gridcap.py.** Rebuilds the tiny, small and medium tables and compares every entry, and
checks the cost side with numpy-financial (*GridCap's Table Is This Calculation*). *Try:* Change
the valuation year to 2028. Predict how many entries still match.

- Program: [reproduce_gridcap.py](src/reproduce_gridcap.py)

**rate_in_model.py.** Solves lesson 6.4.2's model with the rebuilt table at three rates and lists the
starts that move (*The Rate Reaches the Plan Only Through the Coefficients*). *Try:* Add 10% to the
rates. Predict whether its plan is the 7% plan.

- Program: [rate_in_model.py](src/rate_in_model.py)

**coefficients.py.** The GridCap benefit model and the table builder the programs import.

- Library: [coefficients.py](src/coefficients.py)

**gridcap_assumptions.py.** Replays GridCap's generator to record each project's benefit ratio and
decay, which the data does not store.

- Library: [gridcap_assumptions.py](src/gridcap_assumptions.py)
