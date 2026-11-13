# 6.4.1 Start-Time Variables x[i,t] and Timing Windows

The one-period selection model (lessons 1.1.1 and 1.1.3) answers *whether* to fund each project. GridCap's planners now
work on a five-year plan for the small portfolio: 40 projects, a budget for each of 2027 to 2031,
and for each project a window of years it may start in. A project that starts late loses value
(the risk it would have removed is carried for longer), so the question becomes *whether and
when*. Four rules, one per heading, turn "when" into variables a MILP can handle.

## One Binary per Project and Start Year Turns "When" Into "Whether"

Give each project $`i`$ one binary for each year $`t`$ it may start in:

```math
x_{i,t} = \begin{cases} 1 & \text{project } i \text{ starts in year } t \\ 0 & \text{otherwise} \end{cases}
```

```python
def start_variables(model: mathopt.Model, portfolio: Portfolio, integer: bool = True) -> dict:
    """One variable per project and allowed start year. Years outside the window get none."""
    return {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
            for p in portfolio.projects for t in p.starts()}
```

For the tiny portfolio that gives 13 variables:

```text
tiny start variables: x[P001,2028], x[P001,2029], x[P002,2028], x[P002,2029], x[P003,2027], x[P004,2028], x[P005,2027], x[P006,2028], x[P007,2027], x[P007,2028], x[P008,2027], x[P008,2028], x[P008,2029]
```

Why not one integer variable "start year" per project, taking values 2027 to 2031? Because every
quantity that depends on the start year (the NPV, the spend in each year, the crews needed) would
then be a nonlinear function of that integer. With one binary per year, each of them is a plain
sum: the NPV of project $`i`$ is $`\sum_t \text{npv}_{i,t}\, x_{i,t}`$, linear in the $`x`$. That
trade (more variables, every expression linear) is the point of the time-indexed formulation.

## A Project Starts at Most Once, and a Must-Do Starts Exactly Once

Nothing so far stops the model from starting a project in 2027 *and* in 2029, and collecting its
NPV twice. One constraint per project closes that:

```math
\sum_{t} x_{i,t} \le 1 \quad \text{(discretionary)}, \qquad \sum_{t} x_{i,t} = 1 \quad \text{(must-do)}
```

```python
for p in portfolio.projects:
    if p.must_do:
        model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
    else:
        model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
```

`started(i)` is the sum over the project's start years, and it is worth naming, because almost
every later rule speaks about it: "P004 needs P003" becomes $`\text{started}(P004) \le
\text{started}(P003)`$, and an alternative group becomes a sum of `started` terms. The sum is
1 if the project is funded at all and 0 if it is not, so it plays the role the single $`x_i`$
played in the one-period model.

Forget the "at most once" row and the failure is quiet: the model returns a plan worth more than
any real one, with a project listed twice. A test that checks every project starts at most once
catches it in a line (lesson 12.3.1).

## A Timing Window Is Enforced by the Variables You Never Create

P001 may start in 2028 or 2029, so `x[P001,2027]` does not exist. You could create it and add
$`x_{P001,2027} = 0`$; leaving it out is simpler and shrinks the model before the solver sees it:

```text
tiny        8 projects   3 years  windowed     13  whole horizon     21
small      40 projects   5 years  windowed     80  whole horizon    183
medium    400 projects  10 years  windowed    887  whole horizon   3752
large   10000 projects  10 years  windowed  21843  whole horizon  93689
```

On the large portfolio the windows cut the variables by a factor of four, and every variable you
do not create is one the model never has to build, store or send to the solver. Section 11
measures what that saves.

The trap is the other end of the window. A project with a three-year cost profile that starts in
2030 would still be spending in 2032, outside the plan. GridCap's windows already stop every
project in time; with your own data, check that $`t + \text{duration} - 1`$ is inside the horizon
for every variable you create, or the model will fund work it never pays for.

Rows can run the other way too. The once and must-do rows sum one project's variables over its
years; a rule about a *year* sums over projects instead: $`\sum_{i \in P,\ t \in T_i} x_{i,t}`$
for one fixed $`t`$ counts the projects that start in year $`t`$, and a project with no variable
for that year simply has no term in the sum. A year in which no project may start has an empty sum:
there is nothing to bound, so write no row for it. Every per-year budget of the next lesson is a sum of
that shape.

In code, the empty sum needs care. Python's `sum` over no terms is the plain number 0, not a MathOpt
expression, so a row built from it is a comparison of two numbers, and MathOpt refuses it.
`empty_sum.py` caps GridCap tiny at one start per region and year; Coast's only project, P003, may
start only in 2027, so Coast's 2028 and 2029 sums are empty:

```python
coast_2029 = sum(x[p.project_id, t] for p in tiny.projects for t in p.starts()
                 if p.region == "Coast" and t == 2029)
print("Coast starts in 2029:", repr(coast_2029), "of type", type(coast_2029).__name__)
print("the row built from it:", repr(coast_2029 <= 1))
try:
    model.add_linear_constraint(coast_2029 <= 1, name="cap_Coast_2029")
except TypeError as error:
    print("add_linear_constraint refuses it:", type(error).__name__)
```

```text
Coast starts in 2029: 0 of type int
the row built from it: True
add_linear_constraint refuses it: TypeError
```

`0 <= 1` is the Python value `True`, and `add_linear_constraint` raises a `TypeError` on a `bool`.
There are two ways out. Skip the row when its set is empty, as above: it bounds nothing. Or start
the sum from an empty expression, `mathopt.LinearExpression()`, so that the result is an expression
even with no terms; Python's `sum` takes it as its `start`:

```python
starts = sum((x[p.project_id, t] for p in tiny.projects for t in p.starts()
              if p.region == g and t == y), start=mathopt.LinearExpression())
model.add_linear_constraint(starts <= 1, name=f"cap_{g}_{y}")
```

```text
skip empty sets: 10 rows of 12
start from LinearExpression(): 12 rows of 12
rows with no variable: cap_Coast_2028, cap_Coast_2029
HiGHS: OPTIMAL
wrapped after the sum: LinearExpression
an empty sum >= 1: INFEASIBLE
```

The second way writes the two empty rows, $`0 \le 1`$, which every plan satisfies, and HiGHS solves
the model as usual. Wrapping a finished sum, `mathopt.LinearExpression(sum(...))`, also turns the 0
into an expression. An empty row is harmless only when it is true: the last line puts a floor of 1
on an empty sum, $`0 \ge 1`$, and HiGHS reports the model `INFEASIBLE`. That is right if the rule
really demands a start where none is possible, and a bug to look for if it does not.

The MathOpt sample `time_indexed_scheduling.py` in the OR-Tools repository is this formulation
outside GridCap. Jobs run one at a time on a single machine; job $`i`$ takes $`p_i`$ periods and may
not start before its **release time** $`r_i`$, and the goal is the smallest sum of completion
times. It has one binary per job and start time, a "starts once" row per job, and one row per time
$`t`$ that sums, over every job, the start variables that would have it running at $`t`$: the
per-year shape just described. The sample handles a release time the other way from this lesson:
it creates every $`x_{i,t}`$ and sets the upper bound of the early ones to 0. `time_indexed.py`
builds it both ways:

```python
if windows == "create" and t < r[i]:
    continue                                    # never created
x[i, t] = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}_{t}")
if t < r[i]:
    x[i, t].upper_bound = 0                     # created, then forbidden
```

```text
release times as bounds or as variables never created (lesson 6.4.1):
  the example's test data  bounds variables    51  sum of completion times 26  order [1, 2, 0]
  the example's test data  create variables    50  sum of completion times 26  order [1, 2, 0]
  8 random jobs, seed 3    bounds variables  1424  sum of completion times 530  order [1, 6, 3, 5, 7, 4, 0, 2]
  8 random jobs, seed 3    create variables  1062  sum of completion times 530  order [1, 6, 3, 5, 7, 4, 0, 2]
```

Both give the same schedule; the variables differ. On the sample's own three-job test data one
variable is saved, and on eight jobs with release times drawn from 1 to 79 a quarter of them, 362 of 1,424.
A bound of 0 is the easy way to forbid a start in a model that already exists (lesson 6.5.6 uses
it for manual overrides); leaving the variable out is the better way when you build the model.
The machine rows also meet the empty-sum case: at a time before any job may start, no variable
exists to sum, so the program writes no row there.

<!-- practice 1 -->

## The Schedule Is Read Off the Variables That Are 1

Build the whole model (lesson 6.4.2 is about the budget rows), solve it, and read the start
year of every funded project:

```python
def schedule(tm: TimingModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in tm.x.items() if result.variable_values(v) > 0.5}
```

```text
OPTIMAL NPV $24,260k
started 27 of 40; 9 later than their earliest year
  P008 window 2029-2031 starts 2031  NPV 264 -> 182
  P010 window 2030-2031 starts 2031  NPV 26 -> 19
  P011 window 2029-2031 starts 2031  NPV 240 -> 140
  P012 window 2030-2031 starts 2031  NPV 201 -> 168
  P021 window 2028-2030 starts 2029  NPV 1,241 -> 1,012
  P025 window 2027-2029 starts 2028  NPV 1,009 -> 880
  P029 window 2030-2031 starts 2031  NPV 302 -> 233
  P031 window 2027-2028 starts 2028  NPV 1,000 -> 809
  P039 window 2027-2029 starts 2028  NPV 546 -> 386
starts per year: {2027: 4, 2028: 7, 2029: 4, 2030: 5, 2031: 7}
```

Nine projects start later than they could, each giving up some NPV. Why would the optimizer choose
to lose value? Because each year's budget is full, and pushing P031 from 2027 to 2028 frees
2027 money for work worth more. A one-period model cannot see this trade; it can only fund or
drop. Reading the schedule with the earliest year beside it is how you explain a deferral to a
planner, and section 9 turns that into a report.

`> 0.5` rather than `== 1` is deliberate: a MILP solver only promises values within a small
tolerance of whole numbers (section 10).

<!-- practice 2 -->

## The Model

The whole multi-period model `timing_model.build` solves, in one place. This lesson added the start
variables and the once and must rows; the budget rows come from lesson 6.4.2 and
the precedence rows from lesson 6.4.3.

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
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \quad \leftarrow \text{this lesson} \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \quad \leftarrow \text{this lesson} \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

| Label | Row name in `timing_model.py` |
| --- | --- |
| once$`_i`$, must$`_i`$ | `once_P017`, `must_P002` |
| alt$`_g`$ | `alt_G006` |
| after$`_{c,t}`$ | `after_P023_2029` |
| budget$`_y`$ | `budget_2029` |

## Summary

- **One binary per project and start year turns "when" into "whether".** Every quantity that
  depends on the start year becomes a linear sum.
- **A project starts at most once, and a must-do exactly once.** `started(i)` replaces the
  one-period $`x_i`$ in every rule that follows.
- **A timing window is enforced by the variables you never create.** Check that every created
  start year finishes inside the horizon.
- **The schedule is read off the variables that are 1.** Compare each start with the earliest
  allowed year to find and explain deferrals.

## Reference

| Symbol | Meaning |
| --- | --- |
| $`x_{i,t}`$ | 1 if project $`i`$ starts in year $`t`$, for $`t`$ in its window |
| $`\text{started}(i) = \sum_t x_{i,t}`$ | 1 if project $`i`$ is funded at all |
| $`\text{npv}_{i,t}`$ | NPV of project $`i`$ if it starts in year $`t`$ |
| objective | $`\max \sum_i \sum_t \text{npv}_{i,t}\, x_{i,t}`$ |

| Rule | Constraint |
| --- | --- |
| starts at most once | $`\text{started}(i) \le 1`$ |
| must-do | $`\text{started}(i) = 1`$ |
| child needs parent | $`\text{started}(c) \le \text{started}(p)`$ (timing: lesson 6.4.3) |
| window $`[e_i, l_i]`$ | create $`x_{i,t}`$ only for $`e_i \le t \le l_i`$ |

**Further reading:** [MathOpt sample time_indexed_scheduling.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (the example of `time_indexed.py`: one binary per job and start time, a once row per job, one row per time over the starts that would be running then, and release times as upper bounds of 0); [The Job Shop Problem (OR-Tools)](https://developers.google.com/optimization/scheduling/job_shop) (the other way to model time, one start variable per task with an integer value, which needs either-or rows for a shared machine; lesson 6.2.4 compares them); [Scheduling Overview (OR-Tools)](https://developers.google.com/optimization/scheduling) (scheduling as assigning people and resources to tasks at specific times, and the two kinds OR-Tools works through: shifts and machines); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: capital budgeting as go/no-go investments with a cash-flow row per period, and scheduling problems as inherently 0-1 decisions per item and period).

## Challenges

1. A planner asks for "P021 no later than 2029". Which variables do you delete, and what does that
   do to the model's size?
2. Measure the build time of the windowed and the whole-horizon model on the large portfolio.
3. Two projects share a crew and cannot start in the same year. Write the constraint.

## Design Note: Start Variables or Step Variables

An equivalent model uses $`z_{i,t} = 1`$ if project $`i`$ has started *by* year $`t`$, with
$`z_{i,t} \ge z_{i,t-1}`$. The two are linked by $`x_{i,t} = z_{i,t} - z_{i,t-1}`$, so their LP
relaxations are the same. Start variables make NPV and spend easy to write; step variables make
"has started by" rules easy. Lesson 6.4.3 writes precedence in the "by year $`t`$" style using
sums of start variables, which gives you the step variable's strength without a second set.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**windows.py.** Counts the start variables each GridCap portfolio needs with and without timing windows (*A Timing Window Is Enforced by the Variables You Never Create*). *Try:* Print the variables of one small-portfolio project with a long window. How many years could it start in?

- Program: [windows.py](src/windows.py)

**first_schedule.py.** Solves the multi-period model on GridCap small and reads the schedule off the variables (*The Schedule Is Read Off the Variables That Are 1*). *Try:* Print every funded project's start year, not only the late ones. How many start in the first year?

- Program: [first_schedule.py](src/first_schedule.py)

**time_indexed.py.** OR-Tools' time-indexed scheduling sample with release times as bounds and as
variables never created (*A Timing Window Is Enforced by the Variables You Never Create*), and its
LP bound against a start-time model (lesson 6.4.3). *Try:* Use `random_jobs(12, 3)`. Predict
whether the share of variables saved grows or shrinks.

- Program: [time_indexed.py](src/time_indexed.py)

**empty_sum.py.** Caps GridCap tiny at one start per region and year, where two of the sums have no
terms, and builds the rows by skipping the empty sets and by starting each sum from
`mathopt.LinearExpression()` (*A Timing Window Is Enforced by the Variables You Never Create*).
*Try:* Remove the `start=` argument in the second way. Predict which
line fails, and for which region and year.

- Program: [empty_sum.py](src/empty_sum.py)

**timing_model.py.** The model builder the module's programs import: start variables, once and must-do rows, spend, budgets and precedence. It runs nothing itself; read it to see the whole model in one place.

- Library: [timing_model.py](src/timing_model.py)
