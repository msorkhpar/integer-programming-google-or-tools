# 6.5.5 Jurisdictional and Portfolio Minimum/Maximum Spend

GridCap's rate case comes back from the regulator with a set of spending rules for the small
portfolio's five-year plan. Each year's capital budget is a ceiling, as before. But the utility also
promised to *use* its budget: a plan that leaves money unspent will be read as a sign the budget was
too high. Each of the four regions (the **jurisdictions**: areas with their own regulator,
municipality or rate base) was promised a minimum over the plan. And the board wants vegetation work
to be at least a fixed share of the plan, and transmission at most half of it. Every one of these
is a bound on money spent, from above or from below, on the whole **portfolio** or on a slice of it.
This lesson writes them as rows on the spend expressions the model already has, shows what floors do
to a plan, and checks them before the solve, in four rules.

GridCap is a fictional utility's portfolio, generated for this course. Its regional floors
(`region_floor`) are part of the data; the yearly floors, the raised Plains floor and the shares
below are invented for the lesson.

## A Spend Limit Is a Row on a Spend Expression, From Above or From Below

Lesson 6.4.2 built the plan's spend in year $`y`$ as a linear expression of the start variables,
with each project's cost spread over the years it is worked on:

```math
\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}
```

The budget row is a ceiling on it, $`\text{spend}_y \le B_y`$. A **floor** is the same expression
bounded from below. Two are common: a yearly floor, at least a share $`\alpha`$ of each year's budget,
and a floor on the plan as a whole, which lets the plan spend less in one year if it spends more in
another:

```math
\text{spend}_y \ge \alpha B_y \quad \forall y \in Y \quad \text{(floor}_y), \qquad
\sum_{y \in Y} \text{spend}_y \ge \alpha \sum_{y \in Y} B_y \quad \text{(floor\_plan)}
```

```python
def yearly_floor(share):
    def rows(plan):               # spend at least `share` of each year's budget
        for y in small.years:
            plan.model.add_linear_constraint(plan.spend[y] >= share * small.budget[y], name=f"floor_{y}")
    return rows


def plan_floor(share):
    def rows(plan):               # spend at least `share` of the five budgets together
        total = sum(small.budget.values())
        plan.model.add_linear_constraint(sum(plan.spend.values()) >= share * total, name="floor_plan")
    return rows
```

`portfolio_spend.py` solves GridCap small with each floor and prints the NPV, the plan's total spend
and the share of each year's budget it uses:

```text
budgets {2027: 8890, 2028: 8120, 2029: 8760, 2030: 8610, 2031: 7850}, total $42,230k
budget rows only       NPV $24,260k  spend $41,630k  2027 98.4%  2028 98.2%  2029 98.5%  2030 99.4%  2031 98.3%
yearly floor 99%       NPV $24,086k  spend $42,020k  2027 99.3%  2028 99.5%  2029 99.5%  2030 99.8%  2031 99.4%
plan floor 99.5%       NPV $24,086k  spend $42,020k  2027 99.3%  2028 99.5%  2029 99.5%  2030 99.8%  2031 99.4%
yearly floor 99.5%     NPV $23,850k  spend $42,160k  2027 99.8%  2028 99.8%  2029 100.0%  2030 99.9%  2031 99.7%
yearly floor 100%      NPV $19,032k  spend $42,230k  2027 100.0%  2028 100.0%  2029 100.0%  2030 100.0%  2031 100.0%
```

Without a floor the plan already spends 98% or more of every year's budget: projects are lumpy, and
the last few hundred thousand dollars of a year rarely buy a whole project. Each floor closes part
of that gap and costs NPV, and the cost grows fast. A 99% floor in every year costs $174k. Spending
every last dollar ($`\alpha = 1`$, which turns each budget row into an equality) costs $5,228k, more
than a fifth of the plan's value, because the solver must fill each year exactly with whatever
projects make the sums come out, valuable or not.

That is the general lesson about floors: a ceiling only ever removes plans, while a floor makes the
model *fund work for its spend*, not its value. Set floors where the business really needs them,
and report their cost.

## A Jurisdiction's Spend Is the Same Sum Over Its Own Projects

A jurisdiction $`r`$ owns the projects $`P_r \subseteq P`$. Its spend in year $`y`$ is the year's
spend expression summed over $`P_r`$ only, and its spend over the whole plan is simpler still: every
GridCap project finishes inside the plan, so a funded project spends its whole capex there.

```math
\sum_{i \in P_r} \text{capex}_i\, \text{started}(i) \;\ge\; F_r \qquad \forall r \in R \qquad \text{(floor}_r)
```

A **jurisdictional maximum** is the same row the other way round, $`\le U_r`$ over the plan, or a
yearly one on the regional spend of each year,
$`\sum_{i \in P_r} \sum_{t \le y} c_{i,y-t}\, x_{i,t} \le U_{r,y}`$. A minimum and a maximum on the
same expression make a **band**. This lesson's GridCap runs use the regional floors; the maximum is
the same row with the inequality reversed, and the first practice writes both.

```python
def region_spend(plan, region):
    return sum(p.capex * plan.started(p.project_id) for p in small.projects if p.region == region)


def add_floors(plan, floor):
    for r in REGIONS:
        plan.model.add_linear_constraint(region_spend(plan, r) >= floor[r], name=f"floor_{r}")
```

`region_floors.py` prints each region's floor and the most it could ever receive, then solves with
no floors, with GridCap's floors, and with the Plains floor raised to $8,000k, printing what each
region receives:

```text
floors             Ridge 3,130  Valley 4,300  Coast 4,110  Plains 2,410
most               Ridge 15,670  Valley 20,510  Coast 20,550  Plains 11,600
no floor           NPV $24,260k  Ridge 8,990  Valley 12,730  Coast 13,790  Plains 6,120
floors             NPV $24,260k  Ridge 8,990  Valley 12,730  Coast 13,790  Plains 6,120
Plains floor 8,000 NPV $23,837k  Ridge 7,270  Valley 7,050  Coast 19,420  Plains 8,150
```

GridCap's own floors cost nothing: every region already receives between two and a half and three and a half times its floor. The
raised Plains floor costs $423k, and look at where the money comes from. Plains gains $2,030k, but
Valley loses $5,680k, Ridge loses $1,720k and Coast gains $5,630k. A floor in one jurisdiction moves money between all the
others, through the budgets they share, in ways no one would guess from the rule. Report every
region's change when a floor moves, not only the region it names.

<!-- practice 1 -->

## A Share of the Plan Is Linear Once You Multiply Out the Total

"Vegetation is at least 8% of the plan's spend" looks like a ratio, and a ratio of two variable
expressions is not linear:

```math
\frac{\text{spend}_{\text{veg}}}{\text{spend}_{\text{all}}} \ge 0.08
```

But both sides can be multiplied by $`\text{spend}_{\text{all}}`$, which is never negative, so the
inequality keeps its direction and becomes linear:

```math
\text{spend}_{\text{veg}} \ge 0.08\, \text{spend}_{\text{all}} \qquad \text{(min\_share\_vegetation)}
```

The one case to think about is a plan that spends nothing: the ratio is undefined, and the linear
row reads $`0 \ge 0`$, which allows it. That is almost always what the business means (an empty plan
breaks no share rule), and here the must-dos make an empty plan impossible anyway.

Keep the share's own spend on the left. The reversed row, $`\text{spend}_{\text{all}} \ge 0.08\,
\text{spend}_{\text{veg}}`$, says the total is at least 8% of the vegetation spend, which every plan
meets, so it states no rule at all.

```python
def at_least_share(plan, program, share):    # program spend >= share x total spend
    plan.model.add_linear_constraint(spend_of(plan, program) >= share * spend_of(plan), name=f"min_share_{program}")


def at_most_share(plan, program, share):     # program spend <= share x total spend
    plan.model.add_linear_constraint(spend_of(plan, program) <= share * spend_of(plan), name=f"max_share_{program}")
```

```text
no share rule                  NPV $24,260k  spend $41,630k  transmission 64.2%  distribution 28.3%  vegetation 7.5%
vegetation at least 8%         NPV $24,146k  spend $41,860k  transmission 60.8%  distribution 30.6%  vegetation 8.6%
transmission at most 50%       NPV $23,328k  spend $40,980k  transmission 48.3%  distribution 44.1%  vegetation 7.6%
both                           NPV $23,135k  spend $40,570k  transmission 48.8%  distribution 43.0%  vegetation 8.2%
```

The vegetation rule costs $114k; the transmission cap costs $932k, because transmission holds the
largest projects, and the plan cuts more than it has to (48.3%) since projects come whole. A share
row is on the plan's *actual* spend, so it moves with the plan: under the transmission cap the plan
spends $650k less in total than without it. A rule written as a share of the *budget* instead,
$`\text{spend}_{\text{veg}} \ge 0.08 \sum_y B_y`$, is a different rule (a fixed floor), and it is a
common mistake when the business says "share".

<!-- practice 2 -->

## Floors Can Make the Model Infeasible: Check Them First, Knowing the Checks Are Not Enough

A ceiling alone never makes the model infeasible, since a plan that funds less always spends less;
it takes a must-do or another row that forces spending. A floor can do it on its own: a
jurisdiction cannot receive more than all of its projects cost. Two checks on the data catch the
plain cases:

- **Each floor against the most its jurisdiction can receive**: every project in it, but only the
  dearest option of each alternative group, since a plan funds at most one.
- **The floors together against the budgets together.**

```python
def most_spendable(portfolio, region) -> int:
    """The most a region can receive: every project, but only the dearest option of each group."""
    alone = sum(p.capex for p in portfolio.projects if p.region == region and not p.alt_group)
    groups = [max(portfolio.project(i).capex for i in members)
              for members in groups_of(portfolio).values() if portfolio.project(members[0]).region == region]
    return alone + sum(groups)


def precheck(portfolio, floor) -> list[str]:
    problems = [f"{r}: floor {money(floor[r])} above the most it can receive, {money(most_spendable(portfolio, r))}"
                for r in REGIONS if floor[r] > most_spendable(portfolio, r)]
    if sum(floor.values()) > sum(portfolio.budget.values()):
        problems.append(f"floors total {money(sum(floor.values()))}, budgets {money(sum(portfolio.budget.values()))}")
    return problems
```

Valley's most, $20,510k, is less than all of its projects' capex ($21,530k), because of the
alternative group G030. Now triple every floor:

```text
floors x3 total $41,850k; precheck: no problem found
floors x3          INFEASIBLE
```

Both checks pass: each tripled floor is far below what its region could receive, and the floors
total $41,850k against $42,230k of budgets. The model is still infeasible, because the floors must
be met with whole projects, in the years their windows allow, under each year's own budget, with the
must-dos and dependencies on top, and the last $380k of slack cannot absorb all of that. As in
lesson 6.5.1, the checks are necessary, not sufficient. When they pass and the solver still says
`INFEASIBLE`, lesson 9.1.4 relaxes the floors with penalized slack to find how far short the plan
falls, which is often the number a regulator needs.

## The Model

The planning model with this lesson's rows marked. Each program adds one family at a time.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$
the child projects, with parent $`p(c)`$ and lag $`L_c`$; $`R`$ the regions (jurisdictions), with
$`P_r \subseteq P`$ the projects of region $`r`$; $`P_g \subseteq P`$ the projects of program $`g`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year
of work, and $`\text{capex}_i = \sum_k c_{i,k}`$ ($k); $`B_y`$, the budget of year $`y`$ ($k);
$`\alpha \in [0, 1]`$, the floor's share of the budget; $`F_r`$ and $`U_r`$, region $`r`$'s floor
and cap over the plan ($k); $`\underline{s}_g`$ and $`\bar{s}_g`$, program $`g`$'s least and most
share of the plan's spend.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$; we write
$`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$, $`\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\,
t \le y} c_{i,\,y-t}\, x_{i,t}`$, and $`S(Q) = \sum_{i \in Q} \text{capex}_i\, \text{started}(i)`$ for
the plan's spend on a set of projects $`Q`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\textstyle\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \textstyle\sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\text{spend}_y &\ge \alpha B_y && \forall y \in Y && \text{(floor}_y) \quad \leftarrow \text{this lesson} \\
\textstyle\sum_{y \in Y} \text{spend}_y &\ge \alpha \textstyle\sum_{y \in Y} B_y && && \text{(floor\_plan)} \quad \leftarrow \text{this lesson} \\
S(P_r) &\ge F_r && \forall r \in R && \text{(floor}_r) \quad \leftarrow \text{this lesson} \\
S(P_r) &\le U_r && \forall r \in R && \text{(cap}_r) \quad \leftarrow \text{this lesson, the practice} \\
S(P_g) &\ge \underline{s}_g\, S(P) && \forall g && \text{(min\_share}_g) \quad \leftarrow \text{this lesson} \\
S(P_g) &\le \bar{s}_g\, S(P) && \forall g && \text{(max\_share}_g) \quad \leftarrow \text{this lesson}
\end{aligned}
```

`portfolio_spend.py` uses either the floor$`_y`$ rows or the floor\_plan row; `region_floors.py`
the floor$`_r`$ rows; `program_share.py` the share rows for vegetation (at least 8%) and
transmission (at most 50%).

| Label | Row name in the code |
| --- | --- |
| floor$`_y`$, floor\_plan | `floor_2029`, `floor_plan` |
| floor$`_r`$ | `floor_Plains` |
| min\_share$`_g`$, max\_share$`_g`$ | `min_share_vegetation`, `max_share_transmission` |

## Summary

- **A spend limit is a row on a spend expression, from above or from below.** A floor makes the
  model fund work for its spend; spending every dollar cost $5,228k of NPV here.
- **A jurisdiction's spend is the same sum over its own projects.** A floor in one region moved
  money between all the others; report every region's change.
- **A share of the plan is linear once you multiply out the total.** Write it on the plan's actual
  spend, not on the budget.
- **Floors can make the model infeasible: check them first, knowing the checks are not enough.**
  Each floor against its most, and all floors against all budgets; tripled floors passed both and
  were still infeasible.

## Reference

| Rule in words | Row |
| --- | --- |
| spend at most the budget in year $`y`$ | $`\text{spend}_y \le B_y`$ |
| spend at least $`\alpha`$ of each year's budget | $`\text{spend}_y \ge \alpha B_y`$ |
| spend at least $`\alpha`$ of the plan's budgets | $`\sum_y \text{spend}_y \ge \alpha \sum_y B_y`$ |
| jurisdiction $`r`$ gets at least $`F_r`$ / at most $`U_r`$ over the plan | $`S(P_r) \ge F_r`$ / $`S(P_r) \le U_r`$ |
| jurisdiction $`r`$ gets at most $`U_{r,y}`$ in year $`y`$ | $`\sum_{i \in P_r} \sum_{t \le y} c_{i,y-t}\, x_{i,t} \le U_{r,y}`$ |
| program $`g`$ is at least / at most a share $`s`$ of the plan | $`S(P_g) \ge s\, S(P)`$ / $`S(P_g) \le s\, S(P)`$ |

| Precheck | Fails when |
| --- | --- |
| a floor | it is above every project of its jurisdiction, one option per alternative group |
| all floors | they total more than all budgets |
| a cap | the must-dos inside it already spend more |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (models are built once and solved by any supported solver; this module uses HiGHS); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: capital budgeting with a resource row per period, and cash-flow rows whose right side is the funds available in that period).

## Challenges

1. Write the yearly floor as "at least 99% of each year's budget, or at least 99.5% of the plan's".
   Which variable do you need, and what does the solve cost?
2. In `region_floors.py`, find the largest Plains floor the plan can meet. Predict it before you
   search.
3. Rewrite "vegetation at least 8%" as a share of the budget, and compare the plan and its cost with
   the share of actual spend.

## Design Note: Floors Come With Their Price

A floor is usually a promise someone made outside the model: a rate case, a municipal agreement, a
board target. The model cannot judge it, but it can price it, by solving with and without the row
(lesson 6.5.1) and by showing which jurisdictions paid for it. Ship every floor with that report.
When a floor cannot be met, the right output is not a plan that quietly misses it, but the shortfall
and its cause, which section 9 builds.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**portfolio_spend.py.** Adds yearly and plan-wide spend floors to GridCap small (*A Spend Limit Is
a Row on a Spend Expression*). *Try:* Put the floor on 2030 alone, at 100%. Predict the cost.

- Program: [portfolio_spend.py](src/portfolio_spend.py)

**region_floors.py.** Holds each region above its floor, raises the Plains floor, checks tripled
floors before the solve (*A Jurisdiction's Spend Is the Same Sum* and *Floors Can Make the Model
Infeasible*). *Try:* Double the floors instead of tripling them. Predict whether the plan changes.

- Program: [region_floors.py](src/region_floors.py)

**program_share.py.** Bounds the vegetation and transmission shares of the plan's spend (*A Share
of the Plan Is Linear Once You Multiply Out the Total*). *Try:* Require distribution to be at least
40%. Predict which program gives way.

- Program: [program_share.py](src/program_share.py)

**planning_model.py.** The model builder the programs import; `spend_by_year` builds the spend
expressions.

- Library: [planning_model.py](src/planning_model.py)
