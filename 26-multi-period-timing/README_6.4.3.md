# 6.4.3 Aggregated vs. Cumulative (Disaggregated) Forms

A rate case freezes GridCap's 2027 and 2028 capital budgets. In the small portfolio, P023 (a
breaker bay) may only start a year after its parent P022 (the tower set it sits on). Two analysts
write that rule two ways. Both models return the same optimal plan, and one of them tells the
solver much less about where the optimum is. This lesson compares the two forms by the one number
that decides how hard a MILP is to solve, its LP bound, in four rules.

## The Same Rule Can Be Written as One Aggregated Row or as One Row per Year

"P023 starts at least $`L`$ years after P022, and only if P022 is funded." The first analyst works
with start years as numbers. $`\sum_t t\,x_{i,t}`$ is project $`i`$'s start year when it is funded,
so the rule becomes one funding row and one timing row, with a big-M term that switches the timing
row off when the child is not funded:

```math
\sum_t t\,x_{c,t} \;\ge\; \sum_s (s + L)\,x_{p,s} - M\Big(1 - \sum_t x_{c,t}\Big)
```

The second analyst writes, for every year $`t`$ in the child's window, "the child can have started
by $`t`$ only if the parent had started by $`t - L`$":

```math
\sum_{u \le t} x_{c,u} \;\le\; \sum_{s \le t - L} x_{p,s} \qquad \text{for each } t
```

```python
for t in child.starts():
    model.add_linear_constraint(
        sum(x[child.project_id, u] for u in child.starts() if u <= t)
        <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - lag),
        name=f"after_{child.project_id}_{t}")
```

The first is called **aggregated** because it folds every year into one row: it compares the two
projects' start years, $`\sum_t t\,x_{c,t}`$ against $`\sum_s (s+L)\,x_{p,s}`$, which for a funded
project is exactly its start year.
The second is **disaggregated**, or **cumulative**, because it checks the running totals year by
year. With binary $`x`$ the two allow exactly the same plans.

## Two Forms That Allow the Same Plans Can Have Different LP Bounds

Solve both, as MILPs and as LPs, on the frozen-budget scenario:

```text
P023 needs P022 with lag 1; P023 may start [2029], P022 may start [2027, 2028, 2029]
aggregated precedence rows 4  LP bound 14,472.2  MILP 12,511.0
           P022 {2027: 0.0, 2028: 0.0, 2029: 0.191}  P023 {2029: 0.191}
cumulative precedence rows 2  LP bound 14,449.0  MILP 12,511.0
           P022 {2027: 0.0, 2028: 0.0, 2029: 0.279}  P023 {2029: 0.0}
```

Same MILP optimum, $12,511k. Different LP bounds. Look at what the aggregated LP did: it starts 19.1%
of P022 in 2029 and 19.1% of P023 in 2029, the same year, although the lag is one year. In the
aggregated row the child is only 19.1% funded, so the big-M term $`M(1 - 0.191)`$ is large enough to
excuse any timing at all. The funding row holds (parent and child are both at 19.1%), and the
objective only explains why the LP wants the early start; the row that allows it is the big-M timing
row. The cumulative row for 2029 says $`x_{P023,2029} \le x_{P022,2027} +
x_{P022,2028}`$, both 0, so P023 gets nothing.

## A Tighter LP Bound Means a Smaller Search

Why care about the LP when the MILP answers agree? Section 3 shows that a MILP solver works by
solving LPs and branching on fractions. Every node of its search whose LP bound is below the best
plan found so far can be discarded. A bound of $14,449.0k is closer to the true $12,511k than
$14,472.2k is, so more nodes fall below the line sooner.

On one parent-child pair the difference is $23k, small next to the remaining gap. The size of the
effect grows with the number of precedence rules and with how tight the budgets are, which is why
section 6.7 compares whole formulations by their bounds on the medium portfolio. The direction is
what matters, and it holds well beyond this one scenario. Across 40 seeds of the small portfolio,
each with three budget freezes:

```text
96 feasible scenarios: cumulative tighter in 9, looser in 0
```

The reason is that the cumulative rows say more: they bound the child's running total in every year,
and the aggregated row only compares one weighted sum of the years, with a big-M discount on top. With
fractional values that sum is no longer a start year, so the row can be met by plans no schedule
matches. Where the
bounds are equal, the extra rows cost nothing; where they differ, they always help. The first practice asks you to write a different timing rule, a deadline,
year by year, and to check that its bound beats a colleague's single-row version; the second
applies the same idea to a parent with several children.

The same contrast, at a larger scale, is the reason the OR-Tools MathOpt sample
`time_indexed_scheduling.py` uses one binary per job and start time. The other way to schedule jobs
on one machine is the aggregated one: one start-time variable per job, and for every pair of jobs
two big-M rows, "this one first or that one first" (lesson 6.2.4). `time_indexed.py` solves the
LP relaxation of both on the sample's test data and on eight random jobs:

```text
LP bounds, time-indexed against start times with big-M (lesson 6.4.3):
  the example's test data  time-indexed    25.50  start-time big-M    17.00  MILP 26
  8 random jobs, seed 3    time-indexed   528.25  start-time big-M   462.00  MILP 530
```

The problem is a minimization, so a bound is below the optimum and a higher one is tighter. The
start-time LP returns 17 on the test data, which is every job finishing at its release time plus
its own length, as if the machine could run all three at once: the big-M rows excuse every overlap
once the order binaries are fractional. The time-indexed LP, whose machine rows count running jobs
period by period, gets within half a period of the optimum, 25.50 against 26. It pays for it in
size: 1,062 variables on eight jobs against 8 start times and 28 order binaries.

<!-- practice 1 -->

## Disaggregated Is Stronger, Not Always Bigger

The usual objection to disaggregation is size: one row per year instead of one row. Count them
here. The small portfolio has two children, P023 and P016 (which needs P015 with no lag), so the
aggregated form used 4 rows (two per child) and the cumulative form used 2, because each child has
a one-year window. In general the cumulative form has one row per year of
the child's window, so a ten-year window costs ten rows where the aggregated form needs two. On a
large portfolio that is real growth, and section 11 measures when it starts to cost build time.

Before choosing the smaller form, check what it costs in bound. A model that is a little bigger and
solves in a tenth of the nodes is the better model.

<!-- practice 2 -->

## The Model

The model with the precedence row in its aggregated form, marked, as the first analyst wrote it
($`M_c = \max T_{p(c)} + L_c`$, the parent's latest start plus the lag: the smallest value that never
refuses a plan in which the child is unfunded and the parent starts as late as it may). The cumulative form is the one in
the model of lesson 6.4.1; everything else is unchanged.

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
\sum_{t \in T_c} x_{c,t} &\le \sum_{s \in T_{p(c)}} x_{p(c),s} && \forall c \in C && \text{(needs}_c) \quad \leftarrow \text{this lesson} \\
\sum_{t \in T_c} t\, x_{c,t} &\ge \sum_{s \in T_{p(c)}} (s + L_c)\, x_{p(c),s} - M_c \Big(1 - \sum_{t \in T_c} x_{c,t}\Big) && \forall c \in C && \text{(after}_c) \quad \leftarrow \text{this lesson} \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## Summary

- **The same rule can be written as one aggregated row or as one row per year.** With binaries
  both allow exactly the same plans.
- **Two forms that allow the same plans can have different LP bounds.** The aggregated LP let a
  fractional child start in its parent's year, because the big-M term excused it.
- **A tighter LP bound means a smaller search.** In 96 GridCap scenarios the cumulative bound was
  never weaker, and tighter in 9.
- **Disaggregated is stronger, not always bigger.** Its size grows with window length; weigh that
  against the bound.

## Reference

| Form | Rows per child | Rule |
| --- | --- | --- |
| aggregated | 2 | $`\text{started}(c) \le \text{started}(p)`$ and $`\sum_t t\,x_{c,t} \ge \sum_s (s+L)\,x_{p,s} - M(1-\text{started}(c))`$ |
| cumulative | one per year $`t`$ of the child's window | $`\sum_{u \le t} x_{c,u} \le \sum_{s \le t-L} x_{p,s}`$ |

| Term | Meaning |
| --- | --- |
| LP bound | the optimal value of the LP relaxation; for a maximization, an upper bound on the MILP |
| stronger formulation | one whose LP relaxation allows fewer fractional points |
| big-M | a constant that switches a row off; lesson 6.2.1 derives the smallest valid one |

**Further reading:** [MathOpt sample time_indexed_scheduling.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (the time-indexed model of `time_indexed.py`, whose "no two jobs overlap" rows are one row per time over the starts that would be running then, the per-period form of this lesson); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2.2: formulations of the same set can have LP relaxations of different strength, and a larger one can be the better one; section 6.1: big-M formulations and why they can be weak); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2: a conditional row switched off by a binary and a large constant, the shape of the aggregated precedence row).

## Challenges

1. Show that the cumulative rows imply "the child is funded only if the parent is", so the separate
   funding row is not needed.
2. Find a GridCap scenario where the two LP bounds differ by more than 1%. What did you change?
3. $`M`$ here is a calendar year, about 2030, because $`t`$ is. Rewrite the aggregated row with
   years counted from the plan's first year ($`t - 2027`$) and its smallest valid $`M`$. Predict
   whether the LP bound moves, then measure it.

## Design Note: Why the Course Builds the Cumulative Form by Default

`build(..., precedence="cumulative")` is the default in `timing_model.py`. Its rows read as plain
English ("started by 2029 only if the parent started by 2028"), they need no big-M to derive or
defend, and they are never weaker. The price is a row per window year. The aggregated form stays in
the code because inherited models are full of it, and recognizing its weakness is the skill.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**precedence_forms.py.** Solves the frozen-budget scenario with both precedence forms, as LP and as MILP (*Two Forms That Allow the Same Plans Can Have Different LP Bounds*). *Try:* Freeze only the first year's budget instead of two. Predict whether the two LP bounds move apart or together.

- Program: [precedence_forms.py](src/precedence_forms.py)

**bound_survey.py.** Compares the two forms' LP bounds over 96 scenarios (*Two Forms That Allow the Same Plans*). *Try:* Add 0.25 to the budget cuts. Do you expect more scenarios where the cumulative form is tighter?

- Program: [bound_survey.py](src/bound_survey.py)

**time_indexed.py.** The LP bound of OR-Tools' time-indexed scheduling sample against a start-time
model with big-M order rows (*A Tighter LP Bound Means a Smaller Search*). *Try:* Halve the big-M
constant `horizon` in `start_time`. Predict whether the LP bound moves, and whether the model is
still correct.

- Program: [time_indexed.py](src/time_indexed.py)

**timing_model.py.** The model builder, where `add_precedence` writes both forms.

- Library: [timing_model.py](src/timing_model.py)
