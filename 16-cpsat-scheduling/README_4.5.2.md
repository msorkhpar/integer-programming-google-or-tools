# 4.5.2 Cumulative Resources: Crews and Outage Windows

Lesson 4.5.1 gave each crew its own calendar. GridCap's vegetation manager does not think that way:
she has a **pool** of three crews for the season and twelve jobs, and some jobs need two crews at
once. A corridor widening (P006, P012, P020, P035) runs a mower and a climbing crew side by side,
so it takes two of the three crews for its whole length; a circuit job takes one. Her questions
are about the pool: "in any week, do the jobs under way need more crews than I have?", "what if one
crew is held back for storm duty in the stormy weeks?", "can my circuit clears fit into the weeks
the grid operators will switch those circuits off?". (GridCap is fictional; so is this season, see
`season.py` in lesson 4.5.1.)

Each question is a resource with a capacity, and CP-SAT states each in one constraint. The twelve
jobs come from `season.py`:

```text
P003 Valley circuit  clear weeks 2  crews 1  due 20  weight 10
P004 Plains circuit  trim  weeks 6  crews 1  due  6  weight 30
P006 Valley corridor widen weeks 4  crews 2  due  6  weight  6
P008 Ridge  circuit  clear weeks 6  crews 1  due  6  weight 13
P010 Valley circuit  clear weeks 4  crews 1  due 12  weight 28
P011 Coast  circuit  trim  weeks 4  crews 1  due  6  weight 11
P012 Coast  corridor widen weeks 6  crews 2  due  6  weight 22
P014 Coast  circuit  trim  weeks 2  crews 1  due 20  weight 38
P015 Coast  circuit  clear weeks 2  crews 1  due 12  weight 31
P018 Valley circuit  clear weeks 6  crews 1  due 20  weight 30
P020 Ridge  corridor widen weeks 2  crews 2  due 20  weight 15
P035 Ridge  corridor widen weeks 6  crews 2  due 20  weight 13
```

`crews` is the job's **demand**: how many of the pool's crews it holds in every week it runs. The
due weeks and weights are for lesson 4.5.4; this lesson minimizes the makespan, the week the last
job ends, as lesson 4.5.1 did.

## Cumulative Caps the Crews at Work in Every Week

`NoOverlap` says "at most one at a time". The pool needs "at most three crews' worth at a time",
where each job counts its demand. That is the **cumulative** constraint. Given intervals
$`[s_j, s_j + d_j)`$, demands $`c_j`$ and a capacity $`K`$, it requires that in every week $`w`$
the demands of the jobs running in that week add up to at most $`K`$:

```math
\sum_{j \in J \,:\, s_j \le w < s_j + d_j} c_j \;\le\; K \qquad \forall w
```

The set under the sum depends on the starts, which are variables, so this is not a linear row you
could hand to a MIP solver as written. CP-SAT takes it as one constraint, `add_cumulative(intervals,
demands, capacity)`, and reasons about it directly. `season_model.build` creates one fixed-size
interval per job on a start variable and adds the pool:

```python
s.start[j.jid] = model.new_int_var(0, horizon - j.weeks, f"start_{j.jid}")
s.task[j.jid] = model.new_fixed_size_interval_var(s.start[j.jid], j.weeks, f"work_{j.jid}")
intervals = [s.task[j.jid] for j in jobs]
demands = [j.crews for j in jobs]
model.add_cumulative(intervals, demands, crews)
```

The start's upper bound is `horizon - j.weeks`, so every job ends inside the 30-week season. The
makespan objective is the one of lesson 4.5.1, written with the interval's end expression:

```python
def minimize_makespan(s: Season, horizon: int = HORIZON) -> None:
    s.makespan = s.model.new_int_var(0, horizon, "makespan")
    s.model.add_max_equality(s.makespan, [s.end(j.jid) for j in s.jobs])
    s.model.minimize(s.makespan)
```

`crew_pool.py` first works out a bound by hand. The twelve jobs need 68 crew-weeks (weeks times
demand, summed), and three crews supply 3 crew-weeks per week, so no schedule can end before week
$`\lceil 68 / 3 \rceil = 23`$:

```text
12 jobs, 68 crew-weeks of work, 3 crews: no schedule ends before week 23
OPTIMAL: makespan 24 weeks
  P004 Plains trim  crews 1  weeks  0- 5  due  6
  P012 Coast  widen crews 2  weeks  0- 5  due  6
  P008 Ridge  clear crews 1  weeks  6-11  due  6  late 6 x 13
  P035 Ridge  widen crews 2  weeks  6-11  due 20
  P010 Valley clear crews 1  weeks 12-15  due 12  late 4 x 28
  P011 Coast  trim  crews 1  weeks 12-15  due  6  late 10 x 11
  P018 Valley clear crews 1  weeks 12-17  due 20
  P006 Valley widen crews 2  weeks 16-19  due  6  late 14 x 6
  P003 Valley clear crews 1  weeks 18-19  due 20
  P014 Coast  trim  crews 1  weeks 20-21  due 20  late 2 x 38
  P015 Coast  clear crews 1  weeks 20-21  due 12  late 10 x 31
  P020 Ridge  widen crews 2  weeks 22-23  due 20  late 4 x 15
crews at work by week: 333333333333333333332222000000
```

The last line is the **load profile**: the crews at work in each of the 30 weeks, one digit per
week. It never exceeds 3, which is the cumulative constraint at work, and it is full for the first
20 weeks. The optimum is 24, one week above the hand bound, and `OPTIMAL` means CP-SAT proved that
23 is impossible. The hand bound only counts crew-weeks; it knows nothing about which jobs can
share a week, so a real schedule can need more.

The `late` notes show what the makespan does not care about: P006 is due at week 6 and finishes at
week 20. Lesson 4.5.4 changes the objective.

## NoOverlap Is Cumulative With Capacity 1

A single crew is a pool of size 1 in which every job has demand 1, so `add_cumulative(intervals,
[1] * n, 1)` must say exactly what `add_no_overlap(intervals)` says. `nooverlap_is_cumulative.py`
solves the one-crew schedule of lesson 4.5.1 (five jobs, the training week and the storm standby)
both ways:

```python
if resource == "no_overlap":
    model.add_no_overlap(intervals)
else:
    model.add_cumulative(intervals, [1] * len(intervals), 1)
```

```text
add_no_overlap:                 makespan 18
add_cumulative, capacity 1:     makespan 18
```

The same 18 weeks. Use `add_no_overlap` when the capacity really is 1: it says what you mean, and
CP-SAT has reasoning made for that case. Use `add_cumulative` when a resource holds more than one
job, or when jobs take different amounts of it.

<!-- practice 1 -->

## A Capacity That Drops Is a Fixed Interval Holding the Missing Crews

From week 12 to week 15 the regional operations center holds one crew back for storm duty, so the
pool has 2 crews in those 4 weeks and 3 the rest of the season. `add_cumulative` takes one
capacity. How do you make it change over time?

Add a fixed interval for the period, with the demand of the crews that are away. It occupies part
of the capacity just as a job would, and the jobs share what is left:

```python
for first, (weeks, away) in (standby or {}).items():
    intervals.append(model.new_fixed_size_interval_var(first, weeks, f"standby_{first}"))
    demands.append(away)
model.add_cumulative(intervals, demands, crews)
```

Here `standby = {12: (4, 1)}` (`STANDBY` in `season_model.py`): from week 12, for 4 weeks, 1 crew
away. The capacity stays at 3 (the most crews the season ever has), and a fixed interval of demand
$`3 - a_w`$ is added wherever only $`a_w`$ crews are available. The OR-Tools sample
`cumulative_variable_profile_sample_sat.py` builds a whole day's capacity profile this way, with one
fixed interval per period, each as high as the gap between that period's capacity and the peak.

```text
OPTIMAL: makespan 24 weeks
  P008 Ridge  clear crews 1  weeks  0- 5  due  6
  P012 Coast  widen crews 2  weeks  0- 5  due  6
  P018 Valley clear crews 1  weeks  6-11  due 20
  P035 Ridge  widen crews 2  weeks  6-11  due 20
  P004 Plains trim  crews 1  weeks 12-17  due  6  late 12 x 30
  P011 Coast  trim  crews 1  weeks 12-15  due  6  late 10 x 11
  P006 Valley widen crews 2  weeks 16-19  due  6  late 14 x 6
  P010 Valley clear crews 1  weeks 18-21  due 12  late 10 x 28
  P020 Ridge  widen crews 2  weeks 20-21  due 20  late 2 x 15
  P003 Valley clear crews 1  weeks 22-23  due 20  late 4 x 10
  P014 Coast  trim  crews 1  weeks 22-23  due 20  late 4 x 38
  P015 Coast  clear crews 1  weeks 22-23  due 12  late 12 x 31
crews at work by week: 333333333333222233333333000000
crews available:       333333333333222233333333333333
```

Weeks 12 to 15 now have 2 crews at work, and the profile never goes above the second line. The
makespan is still 24. Count the crew-weeks: 24 weeks of 3 crews are 72, the work takes 68 and the
standby 4, so this schedule leaves no crew idle before week 24, where the first one had 4 idle
crew-weeks (weeks 20 to 23 at 2 crews). The schedule is a different one, and its late jobs differ:
a rule that does not move the objective can still move the plan.

A capacity that *rises* over time works the same way: set the capacity to the highest level and
hold the difference with fixed intervals in the weeks before it rises.

<!-- practice 2 -->

## An Outage Window Is a Domain on the Start

A circuit **clear** (P003, P008, P010, P015, P018) removes trees close to energized conductors, so
the circuit must be switched off (an **outage**) while the crew works. The grid operators allow
outages only in certain weeks of each region, `OUTAGE_WINDOWS` in `season.py`: the Valley, for
example, can be switched in weeks $`[2, 12)`$ and $`[18, 28)`$. A clear must lie entirely inside one
window.

For a job of $`d`$ weeks and a window $`[a, b)`$, the starts that keep the job inside are
$`a, a+1, \dots, b - d`$. The job's allowed starts are the union of those ranges over its region's
windows: a set of integers with holes. CP-SAT lets a variable take its values from exactly such a
set, a **domain**, built with `cp_model.Domain.from_intervals` and used through
`new_int_var_from_domain`:

```python
def start_domain(j: Job, horizon: int) -> cp_model.Domain:
    """Every start that keeps the job inside one of its region's outage windows."""
    return cp_model.Domain.from_intervals(
        [[a, b - j.weeks] for a, b in OUTAGE_WINDOWS[j.region] if b - j.weeks >= a and a < horizon])
```

```python
if outages and j.needs_outage:
    s.start[j.jid] = model.new_int_var_from_domain(start_domain(j, horizon), f"start_{j.jid}")
```

`Domain.from_intervals` takes closed ranges, both ends included, so $`[a, b - d]`$ here is the
list `[a, b - j.weeks]`. A window shorter than the job is skipped (`b - j.weeks >= a`). The five
clears get these domains:

```text
P003 Valley 2 weeks  windows ((2, 12), (18, 28))  start in [2,10][18,26]
P008 Ridge  6 weeks  windows ((0, 8), (14, 24))  start in [0,2][14,18]
P010 Valley 4 weeks  windows ((2, 12), (18, 28))  start in [2,8][18,24]
P015 Coast  2 weeks  windows ((0, 10), (16, 30))  start in [0,8][16,28]
P018 Valley 6 weeks  windows ((2, 12), (18, 28))  start in [2,6][18,22]
```

P008 may start in weeks 0 to 2 or 14 to 18: a six-week clear starting at week 2 occupies
$`[2, 8)`$, weeks 2 to 7, and its end, 8, equals the end of the first Ridge window $`[0, 8)`$, whose
last week is 7. One starting at week 3 would also work week 8, which lies outside the window, when
the circuit is back on.

No constraint was added: the windows live in the variable's domain, and a start in a hole is not
a value the solver can even try. The OR-Tools sample `scheduling_with_calendar_sample_sat.py` does
the same for a task that cannot start during a lunch break, with
`Domain.from_intervals([(8, 12), (14, 15)])`.

## One Outage per Region Is a NoOverlap Over That Region's Clears

The operators add one more rule: a region switches off one circuit at a time, so two clears in the
same region must not overlap. That is a second resource, of capacity 1, over a subset of the same
intervals:

```python
if one_outage_per_region:
    for region in OUTAGE_WINDOWS:
        clears = [s.task[j.jid] for j in jobs if j.region == region and j.needs_outage]
        if len(clears) > 1:
            model.add_no_overlap(clears)
```

An interval can sit in as many scheduling constraints as you like: each clear is in the crew pool's
cumulative *and* in its region's NoOverlap, and the schedule must satisfy both. (A region with one
clear needs no NoOverlap, hence `len(clears) > 1`.) `outages.py` solves the season with the
standby and the windows, first without and then with the one-outage rule, and prints the clears:

```text
windows only: OPTIMAL, makespan 24 weeks
  P008 Ridge  clear crews 1  weeks  0- 5  due  6
  P010 Valley clear crews 1  weeks  2- 5  due 12
  P018 Valley clear crews 1  weeks  2- 7  due 20
  P015 Coast  clear crews 1  weeks  6- 7  due 12
  P003 Valley clear crews 1  weeks 22-23  due 20  late 4 x 10
windows, one outage per region: OPTIMAL, makespan 24 weeks
  P008 Ridge  clear crews 1  weeks  0- 5  due  6
  P018 Valley clear crews 1  weeks  4- 9  due 20
  P003 Valley clear crews 1  weeks 10-11  due 20
  P015 Coast  clear crews 1  weeks 16-17  due 12  late 6 x 31
  P010 Valley clear crews 1  weeks 18-21  due 12  late 10 x 28
```

Every clear sits inside a window of its region in both runs. With windows only, P010 and P018 both
switch Valley circuits off in weeks 2 to 5; with the rule, the Valley's three clears run one after
another. They need 2 + 4 + 6 = 12 weeks and the first Valley window is 10 weeks long, so one of them
has to wait for the second window, $`[18, 28)`$: P010 does. The makespan is 24 in all four runs of
this lesson. The rules cost no time at the end of the season, but they move jobs, and a moved job
can be a late one; lesson 4.5.4 prices that.

Why a domain for the windows and not optional intervals, one per window with exactly one present,
as lesson 4.5.1 chose crews? Both are correct. The domain is smaller (one variable, no Booleans).
Optional intervals are worth their size when the choice of window must appear in other rules or in
the objective: a different crew rate in the late window, for example.

<!-- practice 3 -->

## The Model

The season model `season_model.build` writes with every option on, and the makespan objective of
this lesson. This lesson added the pool, the standby and the outage rules.

**Sets.** $`J`$ the jobs; $`O \subseteq J`$ the circuit clears, which need an outage; $`R`$ the
regions, with $`r(j)`$ the region of job $`j`$; $`\mathcal{W}_r`$ the outage windows of region $`r`$,
each a span $`[a, b)`$ of weeks.

**Parameters.** $`d_j`$, the weeks of job $`j`$; $`c_j`$, the crews it holds while it runs;
$`K = 3`$, the crews in the pool; $`H = 30`$, the season's weeks; the standby, $`n = 1`$ crew away
for the 4 weeks $`[12, 16)`$.

**Variables.**

```math
\begin{aligned}
& s_j \in \{0, \dots, H - d_j\} && \forall j \in J \setminus O && \text{(start week)} \\
& s_j \in \textstyle\bigcup_{[a,b) \in \mathcal{W}_{r(j)},\ b - d_j \ge a} \{a, \dots, b - d_j\} && \forall j \in O && \text{(start inside a window)} \\
& C \in \{0, \dots, H\} && && \text{(makespan)}
\end{aligned}
```

**Objective.**

```math
\min \; C
```

**Constraints.** Each job's interval is $`[s_j, s_j + d_j)`$, a fixed-size interval on $`s_j`$.

```math
\begin{aligned}
& \textstyle\sum_{j \in J \,:\, s_j \le w < s_j + d_j} c_j \;+\; n\,[12 \le w < 16] \;\le\; K && \forall w \in \{0, \dots, H-1\} && \text{(crews)} \\
& \text{NoOverlap}\big(\{[s_j, s_j + d_j) : j \in O,\ r(j) = r\}\big) && \forall r \in R && \text{(outage}_r) \\
& C = \max_{j \in J} (s_j + d_j) && && \text{(makespan)}
\end{aligned}
```

$`[12 \le w < 16]`$ is 1 in the standby weeks and 0 otherwise: the standby's fixed interval.

| Label | In `season_model.py` |
| --- | --- |
| start inside a window | `new_int_var_from_domain(start_domain(j, horizon), ...)` |
| crews | `add_cumulative(intervals, demands, crews)`, with the standby interval appended |
| outage$`_r`$ | `add_no_overlap(clears)`, for each region with two or more clears |
| makespan | `minimize_makespan` |

## Summary

- **Cumulative caps the crews at work in every week.** `add_cumulative(intervals, demands,
  capacity)`: in every unit of time, the demands of the running intervals add up to at most the
  capacity.
- **NoOverlap is cumulative with capacity 1** and every demand 1; use NoOverlap when that is what
  you mean.
- **A capacity that drops is a fixed interval holding the missing crews.** Set the capacity to the
  peak and add a fixed interval with demand peak − available in each period below it.
- **An outage window is a domain on the start.** `Domain.from_intervals` with closed ranges
  $`[a, b - d]`$, one per window, and `new_int_var_from_domain`.
- **One outage per region is a NoOverlap over that region's clears.** One interval can belong to
  several resource constraints, and the schedule meets them all.

## Reference

| Call | What it does |
| --- | --- |
| `add_cumulative(intervals, demands, capacity)` | sum of the demands of the intervals running at any time ≤ capacity |
| `cp_model.Domain.from_intervals([[a1, b1], [a2, b2]])` | the integers in $`[a_1, b_1] \cup [a_2, b_2]`$, ends included |
| `cp_model.Domain.from_values([v1, v2, ...])` | exactly the listed integers |
| `new_int_var_from_domain(domain, name)` | an integer variable whose values are the domain |
| `interval.end_expr()` | the interval's end, as an expression |

| Resource | Constraint |
| --- | --- |
| one crew, machine or circuit at a time | `add_no_overlap` |
| a pool of $`K`$ identical units, jobs taking $`c_j`$ each | `add_cumulative(..., demands, K)` |
| a pool whose size changes over time | `add_cumulative` at the peak, plus fixed intervals for the gaps |
| allowed time windows | a domain on the start (or optional intervals, one per window) |

**Further reading:** the CP-SAT samples
[`cumulative_variable_profile_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/cumulative_variable_profile_sample_sat.py)
(a capacity profile held by fixed intervals) and
[`scheduling_with_calendar_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/scheduling_with_calendar_sample_sat.py)
(a start domain with a hole); OR-Tools,
[The Job Shop Problem](https://developers.google.com/optimization/scheduling/job_shop), for the
NoOverlap-per-resource pattern this lesson extends; the CP-SAT Primer,
[Advanced Modeling](https://d-krupke.github.io/cpsat-primer/advanced_modelling.html), on
`add_cumulative` (demands and capacity may also be variables) and
[Basic Modeling](https://d-krupke.github.io/cpsat-primer/modelling.html), on custom domains and
their costs.

## Challenges

1. Raise the pool to four crews in `crew_pool.py`. Work out the hand bound first, then run it.
2. Make the standby two crews instead of one. Predict whether the makespan moves, and check the
   load profile.
3. Give the Coast a single outage window, $`[0, 10)`$. Which clear can no longer be placed late,
   and what does the solver report if the Coast's clears cannot all fit?

## Design Note: Domains Are Data, So Check Them as Data

An outage window that is one week too short, or a domain built with $`b`$ where $`b - d`$ was meant,
does not make the model fail loudly. It makes some starts impossible, and the solver answers with a
worse schedule or, if no start is left, `INFEASIBLE` with no hint of why. Print each domain next to
its windows, as `outages.py` does, and test `start_domain` on a job whose length equals its window
(exactly one start) and on one longer than every window (an empty domain). Lesson 4.6.2 shows how
CP-SAT can name the rule that made a model infeasible.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**crew_pool.py.** The twelve jobs on a pool of three crews with one cumulative constraint, the
hand bound, and the load profile (*Cumulative Caps the Crews at Work in Every Week*). *Try:* Make
every corridor need 3 crews. Predict whether any two corridors can then run in the same week.

- Program: [crew_pool.py](src/crew_pool.py)

**nooverlap_is_cumulative.py.** The one-crew schedule of lesson 4.5.1 with NoOverlap and with a
capacity-1 cumulative (*NoOverlap Is Cumulative With Capacity 1*). *Try:* Give the training week a
demand of 1 and the capacity 2 in the cumulative version. Predict the makespan.

- Program: [nooverlap_is_cumulative.py](src/nooverlap_is_cumulative.py)

**crew_standby.py.** The pool with one crew held back in weeks 12 to 15 (*A Capacity That Drops Is
a Fixed Interval Holding the Missing Crews*). *Try:* Move the standby to weeks 0 to 3. Predict
whether the first two jobs change.

- Program: [crew_standby.py](src/crew_standby.py)

**outages.py.** The clears' start domains, then the season with outage windows, without and with
one outage per region (*An Outage Window Is a Domain on the Start*, *One Outage per Region Is a
NoOverlap Over That Region's Clears*). *Try:* Shorten the Valley's first window to $`[2, 8)`$.
Predict which Valley clears can still go in it.

- Program: [outages.py](src/outages.py)

**season_model.py.** The model builder this lesson and lesson 4.5.4 use: one interval per job, the
pool, the standby, the outage rules, and the two objectives. It runs nothing itself.

- Library: [season_model.py](src/season_model.py)
