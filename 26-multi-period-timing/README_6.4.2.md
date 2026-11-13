# 6.4.2 Cash-Flow Spreading Across Years

GridCap finance reviews last year's plan and finds that 2031 overran its budget by $3.47M. The
model said the plan fit. It did fit the model: whoever built it charged each project's whole cost
to the year it starts. A three-year tower set repair does not spend its money in year one. This
lesson spreads each project's cost over the years it is worked on, in three rules.

## A Project's Cost Lands in the Years It Is Worked On

P022, a tower set repair in the small portfolio, takes three years. Its cost profile is what it
spends in each year of work, and the start year shifts the profile along the calendar:

```text
P022 cost profile (360, 720, 1470)
  start 2027: spends {2027: 360, 2028: 720, 2029: 1470}
  start 2028: spends {2028: 360, 2029: 720, 2030: 1470}
  start 2029: spends {2029: 360, 2030: 720, 2031: 1470}
```

So the money P022 spends in calendar year $`y`$ depends on which start variable is 1:

```math
\text{spend}_{P022,\,2029} = 1470\, x_{P022,2027} + 720\, x_{P022,2028} + 360\, x_{P022,2029}
```

In general, with $`c_{i,k}`$ the cost of project $`i`$ in its $`k`$-th year of work (counting
from 0):

```math
\text{spend}_y = \sum_i \sum_{t \le y} c_{i,\,y-t}\; x_{i,t}
```

Each start variable appears in the spend of every year its project is worked on, with the
coefficient for that year of work. At most one $`x_{i,t}`$ per project is 1, so in each year at
most one term per project survives: the one for its actual start, if it is being worked on then.

## Build Spend as an Expression Once, and Every Budget Rule Reuses It

The sum above is a linear expression in the $`x`$. Build it once per year and keep it:

```python
def spend_by_year(portfolio: Portfolio, x: dict) -> dict[int, mathopt.LinearExpression]:
    """What the plan spends in each calendar year, with each project's cost spread over its life."""
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    return spend
```

The yearly budget is then one row per year, $`\text{spend}_y \le B_y`$. The same expressions serve
every other rule about money: a carry-over (lesson 6.4.4), a regional cap (lesson 6.5.5), a report
of planned spend by year (section 9). Writing the triple loop again in each place is how two parts
of one model end up disagreeing about what a project costs in 2030. Nothing fails when the copies
drift apart: the model still solves, and no solver merges or rejects two rows because they disagree.
Each rule simply uses its own idea of spend.

`+=` on a `LinearExpression` does not grow it in place. MathOpt's expressions are immutable (the
OR-Tools source says so in their docstrings), so `spend[year] += ...` builds a new, deferred sum (a
`LinearSum`) and stores it under the same key. The program's last lines show the difference:

```python
total = mathopt.LinearExpression()
alias = total
total += 360 * x
```

```text
after +=: total is a LinearSum, alias is still a LinearExpression, same object: False; alias holds 0 terms, total 1
```

The dictionary entry gets the new sum, which is all `spend_by_year` needs. A second name bound to
the old expression keeps the old, empty one, so build the expressions first and hand them out
afterwards. A plain `sum(...)` over a generator works as well, and for the large portfolio section
11 compares both against building from DataFrames.

A rule a planner states with an absolute value or a "between" is still linear rows on these
expressions: "within 500 of last year" is two rows, one bounding the rise and one bounding the
fall, because a solver row compares one linear expression with a number and cannot take $`|\cdot|`$.

<!-- practice 1 -->

## Charging Everything to the Start Year Breaks the Budget the Plan Claims to Respect

Here is the shortcut finance caught, and the spread model, both solved on the small portfolio.
Each plan is then checked against the budgets using what it really spends each year:

```python
for cash_flow in ("lump", "spread"):
    tm = build(small, cash_flow=cash_flow)
    result = mathopt.solve(tm.model, mathopt.SolverType.HIGHS, params=params)
    spend = real_spend(schedule(tm, result))
    over = {y: spend[y] - small.budget[y] for y in small.years if spend[y] > small.budget[y]}
```

```text
lump   model: NPV $24,916k, real spend over budget in {2030: 1500, 2031: 3470}
spread model: NPV $24,260k, real spend over budget in no year
```

The lump model reports $656k more NPV, and that number is the cost of the shortcut being wrong:
it buys more work than the budget allows, by $1.5M in 2030 and $3.47M in 2031. The overrun lands at
the end of the plan because that is where long projects started in earlier years keep spending.
The lump model thinks that money was paid in the start year, so it fills those later years with
new starts as well. Nothing about value or discounting causes it: the overrun is spending the model
never counted. The budgets
do not cause it either: the spread model meets the very same budgets in every year.

Stepping back: a model is only as truthful as its accounting. The solver respected every
constraint it was given; the constraint described a world in which projects pay up front.

<!-- practice 2 -->

## The Model

The model of lesson 6.4.1, whole, with this lesson's budget row marked: the spend of year $`y`$ sums
each start variable times the slice of its project's cost that lands in $`y`$.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use (its window, cut so the work ends inside $`Y`$); $`M \subseteq P`$ the must-do projects;
$`\mathcal{G}`$ the alternative groups, each a set of projects; $`C \subseteq P`$ the child
projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$. No other variable exists, so no other start is possible.

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
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow \text{this lesson}
\end{aligned}
```

## Summary

- **A project's cost lands in the years it is worked on.** The spend in year $`y`$ is a sum over
  start years $`t \le y`$ of $`c_{i,y-t}\, x_{i,t}`$.
- **Build spend as an expression once, and every budget rule reuses it.** One definition keeps
  every rule about money consistent.
- **Charging everything to the start year breaks the budget the plan claims to respect.** On
  GridCap small it overstates NPV by $656k and overspends 2031 by $3.47M.

## Reference

| Symbol | Meaning |
| --- | --- |
| $`c_{i,k}`$ | cost of project $`i`$ in its $`k`$-th year of work ($`k = 0`$ is the start year) |
| $`\text{spend}_y`$ | $`\sum_i \sum_{t \le y} c_{i,y-t}\, x_{i,t}`$ |
| yearly budget | $`\text{spend}_y \le B_y`$ for every year $`y`$ |
| `Project.spend(t)` | GridCap's calendar spend, `{year: amount}`, for a start in `t` |
| `e += term` | a new expression bound to `e`; the old object is unchanged |

**Further reading:** [MathOpt expressions, `variables.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/variables.py) (`LinearExpression` and `LinearSum` are immutable, and `sum(iterable)` builds a nest of deferred sums); [MathOpt sample facility_location.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/facility_location.py) (an objective grown term by term from an empty `mathopt.LinearExpression()` with `+=`, the pattern of `spend_by_year`); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: cash-flow rows, one per period, whose coefficient for an investment is its net cash flow in that period, the $`c_{i,y-t}`$ of this lesson).

## Challenges

1. Projects in the medium portfolio last up to three years. How many nonzero coefficients does the
   2031 budget row have in the small and in the medium model?
2. Some utilities pay a contractor 10% on award and the rest on completion. Write the cost profile.
3. Should spend be escalated for inflation before or after spreading? Section 7.2 has the answer;
   guess first.

## Design Note: Spend Is Data Times Decisions, Not a Decision

You could add a continuous variable $`s_y`$ for each year's spend and a constraint
$`s_y = \sum \ldots`$. It reads well in a solver log, and it gives every report one named number.
It also adds a variable and a row per year for nothing the expression does not already say. This
course keeps spend as an expression and adds a variable only where the model must choose an amount,
as the carry-over in lesson 6.4.4 does.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**spreading.py.** Shows one project's cost profile, then solves with lump-sum and with spread spending and checks both against the real spend (*Charging Everything to the Start Year*). *Try:* Pick a project with a three-year profile instead of P022 and print its spend by start year. Which start years reach past the plan?

- Program: [spreading.py](src/spreading.py)

**timing_model.py.** The model builder, where `spend_by_year` builds each year's spend once for every rule to reuse.

- Library: [timing_model.py](src/timing_model.py)
