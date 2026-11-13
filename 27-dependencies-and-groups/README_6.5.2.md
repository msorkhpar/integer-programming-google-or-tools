# 6.5.2 Parent-Child Bundles and All-or-Nothing

GridCap's Ridge engineers send the planners three new rules for the small portfolio. The P028
tower-set replacement in 2030 takes a line out of service, and while it is out the load has to run
through a Ridge circuit that has already been put underground (P024 or P037): P028 *needs* one of
them. The three Plains feeder replacements P013, P026 and P040 are one program, approved as a
whole or not at all. And the three Ridge vegetation jobs P008, P020 and P035 share one crew
mobilization, so they must start in the same year. The first rule links a **child** project to its
**parents**; the other two make a **bundle**, a group that is funded, or scheduled, as one. This
lesson writes each as rows of the multi-period model, measures what each costs, and checks the
dependency graph before the solve, in four rules.

GridCap is a fictional utility's portfolio, generated for this course. Its data already has two
parent-child pairs (P016 needs P015, and P023 needs P022 with a one-year lag); the rules above are
invented for the lesson.

## A Child Needs Its Parent: Started by Year t Only if the Parent Had Started by Then

Section 9.1 of MIT's 15.053 text (see Further reading) writes a contingent investment, "j only if
i", as one row on two binaries, $`x_j \le x_i`$: if $`x_j = 1`$ then $`x_i`$ must be 1, and if
$`x_i = 0`$ then $`x_j`$ must be 0. The contingent project sits on the small side of the row. (The
text names its two projects the other way round, so its row reads $`x_j \ge x_i`$ for "i only if
j"; it is the same row.)
With start-year variables the rule also has a time: the parent must be under way when the child
starts. Lesson 6.4.3 wrote it one row per year of the child's window, with
$`\text{started\_by}(i, t) = \sum_{u \in T_i,\ u \le t} x_{i,u}`$, which is 1 if project $`i`$
has started in year $`t`$ or earlier:

```math
\text{started\_by}(c, t) \le \text{started\_by}(p, t - L) \qquad \forall t \in T_c \qquad \text{(needs}_{c,p,t})
```

with $`L`$ the lag in years (0 here: the parent may start in the same year as the child). In the
child's last year the row reads $`\text{started}(c) \le \text{started\_by}(p, \cdot)`$, so it also
says "no child without its parent". A child with two parents can mean two different things, and
the rows differ:

- **Needs all of them**: one such row per parent.
- **Needs any one of them**: one row per year whose right side sums the parents,
  $`\text{started\_by}(c, t) \le \sum_{p} \text{started\_by}(p, t - L)`$. The sum is at least 1 as
  soon as one parent has started, which is all the child needs.

```python
def needs_one(plan):              # P028 needs P024, started no later than P028 starts
    for t in small.project(CHILD).starts():
        plan.model.add_linear_constraint(plan.started_by(CHILD, t) <= plan.started_by("P024", t),
                                         name=f"needs_{CHILD}_P024_{t}")


def needs_all(plan):              # P028 needs both P024 and P037
    for parent in PARENTS:
        for t in small.project(CHILD).starts():
            plan.model.add_linear_constraint(plan.started_by(CHILD, t) <= plan.started_by(parent, t),
                                             name=f"needs_{CHILD}_{parent}_{t}")


def needs_any(plan):              # P028 needs at least one of P024 and P037
    for t in small.project(CHILD).starts():
        plan.model.add_linear_constraint(
            plan.started_by(CHILD, t) <= sum(plan.started_by(parent, t) for parent in PARENTS),
            name=f"needs_any_{CHILD}_{t}")
```

`needs_rows.py` solves the model with each version and prints the start years of the three
projects (`-` for not funded):

```text
P028 may start [2030]; P024 may start [2028, 2029, 2030]; P037 may start [2030, 2031]
no rule     NPV $24,260k  costs    $0k  {'P028': 2030, 'P024': '-', 'P037': '-'}
needs P024  NPV $23,987k  costs  $273k  {'P028': 2030, 'P024': 2029, 'P037': 2031}
needs all   NPV $23,390k  costs  $870k  {'P028': '-', 'P024': '-', 'P037': '-'}
needs any   NPV $23,987k  costs  $273k  {'P028': 2030, 'P024': 2029, 'P037': 2031}
```

- **No rule.** The best plan funds P028 (the most valuable project in the portfolio, $4,268k of
  NPV) and neither undergrounding job. That is exactly the plan the engineers say cannot be built.
- **Needs P024.** The plan keeps P028 and adds P024 in 2029, before P028's start, for $273k of NPV.
  It also funds P037 in 2031; the rule does not ask for that, it is just the best use of the money
  once P024 is in.
- **Needs all.** P037 cannot start before 2030, so P028's 2030 row needs both P024 and P037 started
  by 2030. That costs more than P028 is worth to the plan, which now drops all three: a loss of
  $870k against the plan without the rule.
- **Needs any.** The rule is met by P024 alone, so it costs the same $273k as "needs P024".

The difference between "all" and "any" here is $597k. Ask which one the engineers mean, every time
a child has more than one parent.

## All-or-Nothing Is an Equality Between Members

A **bundle** is a set of projects $`B`$ that is funded whole or not at all. Pick one member $`b_1`$
and tie each other member to it:

```math
\text{started}(j) = \text{started}(b_1) \qquad \forall j \in B \setminus \{b_1\} \qquad \text{(bundle}_{b_1,j})
```

If $`b_1`$ is funded, every member is; if it is not, none is. That is $`|B| - 1`$ rows. Two other
forms are common and allow the same plans: a new binary $`z_B`$ with $`\text{started}(j) = z_B`$
for every member (one more variable, $`|B|`$ rows), and the pair of parent rows
$`\text{started}(j) \le \text{started}(b_1)`$ and $`\text{started}(b_1) \le \text{started}(j)`$,
which says the same thing as the equality in twice the rows. A bundle is a parent-child rule that
runs both ways.

```python
def all_or_nothing(plan, members):
    first = members[0]
    for other in members[1:]:
        plan.model.add_linear_constraint(plan.started(other) == plan.started(first),
                                         name=f"bundle_{first}_{other}")
```

Only *whether* the members are funded is tied. Each member still chooses its own start year.

## A Bundle That Starts Together Is an Equality per Year

"One crew mobilization" asks for more: the members start *in the same year*. Tying the `started`
sums is not enough, because P008 could start in 2031 and P020 in 2030 with both sums equal to 1.
The year has to be tied, one row per year and member:

```math
x_{j,t} = x_{b_1,t} \qquad \forall j \in B \setminus \{b_1\},\ t \in T_B \qquad \text{(together}_{b_1,j,t})
```

where $`T_B = \bigcap_{i \in B} T_i`$ is the set of years in which *every* member may start. A
member's start variable for a year outside $`T_B`$ can never be 1 in such a plan, because the
others cannot join it there, so it is fixed to 0 (the "apart" rows below; lesson 6.5.6 shows that a
fixed variable is better written as a bound). If $`T_B`$ is empty, the bundle can never be funded.

```python
def same_year(plan, members):
    first = members[0]
    common = set.intersection(*(set(small.project(i).starts()) for i in members))
    for i in members:
        for t in small.project(i).starts():
            if t not in common:
                plan.model.add_linear_constraint(plan.x[i, t] == 0, name=f"apart_{i}_{t}")
    for other in members[1:]:
        for t in sorted(common):
            plan.model.add_linear_constraint(plan.x[other, t] == plan.x[first, t],
                                             name=f"together_{first}_{other}_{t}")
    return sorted(common)
```

The "together" rows imply the "all or nothing" rows: summing $`x_{j,t} = x_{b_1,t}`$ over the common
years gives $`\text{started}(j) = \text{started}(b_1)`$ once the other years are fixed to 0.
`bundles.py` solves each bundle three ways:

```text
Plains feeders: P013 1,010 may start [2028, 2029], P026 1,350 may start [2028], P040 2,440 may start [2028]
  no bundle       NPV $24,260k  costs   $0k  {'P013': '-', 'P026': 2028, 'P040': '-'}
  all or nothing  NPV $24,139k  costs $121k  {'P013': '-', 'P026': '-', 'P040': '-'}
  same year       NPV $24,139k  costs $121k  {'P013': '-', 'P026': '-', 'P040': '-'}  common years [2028]
Ridge vegetation: P008 390 may start [2029, 2030, 2031], P020 230 may start [2030, 2031], P035 580 may start [2027, 2028, 2029, 2030]
  no bundle       NPV $24,260k  costs   $0k  {'P008': 2031, 'P020': 2030, 'P035': 2027}
  all or nothing  NPV $24,260k  costs   $0k  {'P008': 2031, 'P020': 2030, 'P035': 2027}
  same year       NPV $23,966k  costs $294k  {'P008': '-', 'P020': '-', 'P035': '-'}  common years [2030]
```

Each cost is measured against that bundle's own "no bundle" line, which is the same $24,260k plan
both times.

- **Plains feeders.** The best plan funds only P026. All of the program costs more than it returns
  in the years it would run, so the bundle drops all three, and the plan loses P026's contribution
  net of what the freed money buys: $121k. "All or nothing" is a real choice between all and
  nothing, and here nothing wins.
- **Ridge vegetation, all or nothing.** The best plan already funds all three, in 2031, 2030 and
  2027, so the rule costs nothing.
- **Ridge vegetation, same year.** The only year all three may start is 2030. Starting all three
  then is worth less than dropping them, so the plan drops them, for $294k.

The two Ridge rows are the point of this section: the same three projects, the same "all of them",
and a $294k difference that comes only from the timing.

<!-- practice 1 -->

## Read the Dependency Graph Before You Solve

Parent links form a graph: an arrow from each child to each parent. Three facts about it can be
read before any model is built, and each one changes the plan in a way the solver will not explain:

- **A must-do child makes its parents must-dos.** If P023 must be funded and needs P022, P022 must
  be funded too, and so must P022's own parents. The model enforces this already; the check tells
  the planner, who may not know that marking one project mandatory mandated another.
- **A child whose window closes before its parent's opens can never be funded.** If the parent's
  earliest start plus the lag is after the child's latest start, the child's needs rows force it to
  0 in every year. The model drops it without a word.
- **Two projects that need each other are a bundle.** "A needs B" and "B needs A" together are the
  all-or-nothing rows, and with lag 0 both ways, the same-year rows. A cycle in parent links is
  usually a data error, and if it is meant, it should be written as a bundle.

```python
def ancestors(portfolio, pid: str) -> list[str]:
    """Every project `pid` needs, directly or through its parents, nearest first."""
    found, here = [], portfolio.project(pid).parent
    while here is not None and here not in found and here != pid:
        found.append(here)
        here = portfolio.project(here).parent
    return found
```

`dependency_check.py` runs the three checks on GridCap small as generated and after three edits a
planner might make, and solves each edited model:

```text
children: [('P016', 'P015', 0), ('P023', 'P022', 1)]
as generated: no problem found
P023 made a must-do: ['P023 is a must-do, so P022 is one too']
   solve OPTIMAL; {'P015': 2029, 'P016': 2030, 'P022': 2027, 'P023': 2029}
P016 lag raised to 2: ['P016 can never start: P015 starts 2029 at the earliest, lag 2, P016 starts 2030 at the latest']
   solve OPTIMAL; {'P015': 2030, 'P016': '-', 'P022': 2027, 'P023': 2029}
P015 made a child of P016: ['P015 and P016 need each other: a bundle, not a parent and child']
   solve OPTIMAL; {'P015': 2030, 'P016': 2030, 'P022': 2027, 'P023': 2029}
```

Every edited model solves to `OPTIMAL`. That is the reason for the checks: none of these problems
makes the model infeasible, so the solver has nothing to report. With the lag at 2, P016 silently
leaves the plan. With the cycle, P015 and P016 are forced into the same year, 2030, and P015 moves
from 2029 to get there. A planner reading only the plan would see two changes and no cause.

The `ancestors` walk follows one parent per project, as GridCap stores it. With several parents
per child (needs all), the walk becomes a search over every parent, and a project reached by two
paths is still one project, funded once.

<!-- practice 2 -->

## The Model

The planning model with this lesson's rows marked. Each program adds one rule to it at a time.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq
P`$ the child projects, each with a set of parents $`\text{Par}(c)`$ and a lag $`L_c`$ years (the
data has one parent per child; P028 gets two in this lesson); $`\mathcal{B}`$ the bundles, each a
set $`B \subseteq P`$ with a first member $`b_1`$; $`\mathcal{B}^{\text{yr}} \subseteq \mathcal{B}`$
the bundles that start together, with $`T_B = \bigcap_{i \in B} T_i`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$. We write $`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ and
$`\text{started\_by}(i, t) = \sum_{u \in T_i,\, u \le t} x_{i,u}`$.

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
\text{started\_by}(c, t) &\le \text{started\_by}(p, t - L_c) && \forall c \in C,\ p \in \text{Par}(c),\ t \in T_c && \text{(needs}_{c,p,t}) \quad \leftarrow \text{needs all} \\
\text{started\_by}(c, t) &\le \textstyle\sum_{p \in \text{Par}(c)} \text{started\_by}(p, t - L_c) && \forall c \in C,\ t \in T_c && \text{(needs\_any}_{c,t}) \quad \leftarrow \text{or needs any} \\
\text{started}(j) &= \text{started}(b_1) && \forall B \in \mathcal{B},\ j \in B \setminus \{b_1\} && \text{(bundle}_{b_1,j}) \quad \leftarrow \text{this lesson} \\
x_{j,t} &= x_{b_1,t} && \forall B \in \mathcal{B}^{\text{yr}},\ j \in B \setminus \{b_1\},\ t \in T_B && \text{(together}_{b_1,j,t}) \quad \leftarrow \text{this lesson} \\
x_{i,t} &= 0 && \forall B \in \mathcal{B}^{\text{yr}},\ i \in B,\ t \in T_i \setminus T_B && \text{(apart}_{i,t}) \quad \leftarrow \text{this lesson} \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

A child uses either the needs rows or the needs-any rows, as its rule says. GridCap's own children
use needs rows with one parent each; `planning_model.py` names them `after_P023_2029`, as lessons
6.4.1 to 6.4.4 did.

| Label | Row name in the code |
| --- | --- |
| needs$`_{c,p,t}`$ | `needs_P028_P024_2030`, `after_P016_2030` |
| needs\_any$`_{c,t}`$ | `needs_any_P028_2030` |
| bundle$`_{b_1,j}`$ | `bundle_P013_P026` |
| together$`_{b_1,j,t}`$, apart$`_{i,t}`$ | `together_P008_P020_2030`, `apart_P035_2027` |

## Summary

- **A child needs its parent: started by year t only if the parent had started by then.** Several
  parents mean "all" (a row per parent) or "any" (one row on their sum); here the difference was
  $597k.
- **All-or-nothing is an equality between members.** $`|B| - 1`$ rows tie whether each member is
  funded; each still picks its own year.
- **A bundle that starts together is an equality per year.** Tie the start variables in the common
  years and fix the others to 0; the same three Ridge jobs cost $0 as a bundle and $294k as a
  same-year bundle.
- **Read the dependency graph before you solve.** Must-do children, children that can never start,
  and cycles all solve to `OPTIMAL`; only a check names them.

## Reference

| Rule in words | Rows |
| --- | --- |
| $`c`$ needs $`p`$, at least $`L`$ years after | $`\text{started\_by}(c, t) \le \text{started\_by}(p, t - L)`$ for each $`t \in T_c`$ |
| $`c`$ needs all of its parents | the row above for each parent |
| $`c`$ needs any one of its parents | $`\text{started\_by}(c, t) \le \sum_p \text{started\_by}(p, t - L)`$ for each $`t \in T_c`$ |
| bundle $`B`$, all or nothing | $`\text{started}(j) = \text{started}(b_1)`$ for each $`j \ne b_1`$ |
| bundle $`B`$, same year | $`x_{j,t} = x_{b_1,t}`$ for $`t \in T_B`$; $`x_{i,t} = 0`$ for $`t \notin T_B`$ |

| Graph check | What it means for the plan |
| --- | --- |
| must-do child | every ancestor is a must-do too |
| parent's earliest start + lag > child's latest start | the child is never funded |
| a cycle of parent links | the projects form a bundle |

**Further reading:** [MathOpt sample time_indexed_scheduling.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (start-time binaries, one per job and time, the $`x_{i,t}`$ these bundle rows tie together); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: capital budgeting with contingent investments, where the contingent project's binary is never above its prerequisite's, $`x_j \le x_i`$ for "j only if i", and multiple-choice rows).

## Challenges

1. Write the bundle rows with a bundle variable $`z_B`$ instead of a first member. Predict whether
   the plan or the number of rows changes.
2. In `needs_rows.py`, give P028 a lag of 1 on P024. Which start years of P024 can still serve it?
3. Extend `ancestors` to a child with several parents, so that a project reached by two paths is
   listed once.

## Design Note: A Bundle Is Data, Not Code

The bundles in this lesson are lists in a program. In a planning tool they are records: a name, a
kind ("all or nothing", "same year") and the members, owned by the planners and checked like any
other input (lesson 12.2.2). One function turns every record into rows, and the dependency check
runs over the same records. Then "why was P026 dropped?" has an answer a planner can read: it is in
the Plains feeders bundle, and the bundle did not pay for itself.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**needs_rows.py.** Adds "P028 needs P024", "needs both" and "needs either" to the plan and compares
their costs (*A Child Needs Its Parent*). *Try:* Make P028 need only P037. Predict whether the
plan keeps P028.

- Program: [needs_rows.py](src/needs_rows.py)

**bundles.py.** Solves two bundles with no rule, as all-or-nothing, and as same-year bundles
(*All-or-Nothing Is an Equality Between Members* and *A Bundle That Starts Together*). *Try:* Drop
P035 from the Ridge bundle. Predict the common years and the cost.

- Program: [bundles.py](src/bundles.py)

**dependency_check.py.** Checks GridCap's parent links for must-do children, children that can
never start, and cycles, then solves each edited portfolio (*Read the Dependency Graph Before You
Solve*). *Try:* Make P022 a must-do instead of P023. Predict what the check reports.

- Program: [dependency_check.py](src/dependency_check.py)

**planning_model.py.** The model builder the programs import; `add_after` writes GridCap's own
parent rows.

- Library: [planning_model.py](src/planning_model.py)
