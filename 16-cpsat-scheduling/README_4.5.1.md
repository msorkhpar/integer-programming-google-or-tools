# 4.5.1 Interval Variables and `NoOverlap`

GridCap's vegetation program keeps trees away from power lines. A capital plan decides *which year*
each vegetation project is funded; this module takes that year as given and decides *which week*
each project is worked, and by which crew. Nothing here needs the year plan itself: lesson 6.4.1,
later in the course, builds it in depth. The question changes shape. A year plan asks "how much money does each year need?"; a
season plan asks "is this crew already busy that week?". Two jobs that each fit the season can
still collide, because one crew cannot be in two places at once.

This lesson starts with one crew and five circuit jobs from GridCap small, all in the Valley and
Coast regions. (GridCap is a fictional utility; the season data are invented on top of it, see
`season.py` below.) A circuit trim or clear takes this crew 2 to 4 weeks. In what order should the
crew do them, and when does the season's work end? CP-SAT, the constraint solver of OR-Tools that
lessons 4.4.1 to 4.4.4 introduce, has a variable made for exactly this: the **interval**.

The season's jobs, as `season.py` derives them from the portfolio. The module uses all twelve; this
lesson uses the five Valley and Coast circuits P003, P010, P011, P014 and P015:

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

The `weeks` column is the work's length: two weeks per crew-month GridCap gives the project.
`crews`, `due` and `weight` matter from lesson 4.5.2 on.

## An Interval Variable Ties a Start, a Size and an End Together

A schedule is made of time spans: "P014 is worked from week 3 to week 4". Weeks are numbered from
0, the season's first week. A span is written as the half-open range $`[s, e)`$: it starts at the
beginning of week $`s`$ and ends at the beginning of week $`e`$, so it covers weeks
$`s, s+1, \dots, e-1`$, and its **size** is $`e - s`$. A two-week job that starts at week 3 is
$`[3, 5)`$: it occupies weeks 3 and 4, and the next job on the same crew can start at week 5.

In CP-SAT you build a span from two integer variables, its start and its end, and one size, and
then tie them together into an **interval variable**:

```python
model = cp_model.CpModel()
start = model.new_int_var(0, HORIZON, "start_P014")
end = model.new_int_var(0, HORIZON, "end_P014")
trim = model.new_interval_var(start, 2, end, "trim_P014")
print(repr(trim))
```

`HORIZON` is the season's length, 30 weeks: the latest week any job may end. Every start and end
needs such a bound, because an integer variable in CP-SAT always has a finite domain (lesson 4.4.1);
a job that ends after the horizon is simply not a value the variable can take.

`new_interval_var(start, size, end, name)` does two things. It creates the interval, the object the
scheduling constraints below take as input, and it **adds the constraint**
$`\text{end} = \text{start} + \text{size}`$ to the model. The size here is the constant 2; it could
also be an integer variable when a job's length is a decision (lesson 4.5.3 does that).

When the size is a constant there is a shorter form that needs no end variable, and a fixed span
(a holiday, say) is the same call with a constant start:

```python
same = model.new_fixed_size_interval_var(start, 2, "trim_P014_fixed")
print(repr(same))
holiday = model.new_fixed_size_interval_var(25, 1, "holiday")
print(repr(holiday))
```

The three intervals print as:

```text
trim_P014(start = start_P014, size = 2, end = end_P014)
trim_P014_fixed(start = start_P014, size = 2, end = start_P014 + 2)
holiday(start = 25, size = 1, end = 26)
```

The second one has no end variable: its end is the expression `start_P014 + 2`, and
`interval.end_expr()` returns it whenever you need the end in a constraint. The third is fixed
entirely, weeks $`[25, 26)`$.

To see that the interval really is a constraint, solve a model that asks the job to start at week
3 or later and to end as early as possible, once with the interval and once with the same two
variables but no interval:

```python
model.add(start >= 3)
model.minimize(end)
solver, status = solve(model)
print(f"with the interval:    {status}  start {solver.value(start)}  end {solver.value(end)}")
```

```text
with the interval:    OPTIMAL  start 3  end 5
without the interval: OPTIMAL  start 3  end 0
```

Without the interval nothing links `end` to `start`, so the solver sets `end` to its lower
bound, 0. With it, the end follows the start by exactly two weeks. `solve` is the module's small helper
(`cpsat_run.py`): it creates a `cp_model.CpSolver`, sets one search worker so that a printed
schedule repeats from run to run (when two schedules are equally good, several parallel workers can
return either; lesson 4.6.3 covers reproducible runs), and returns the solver with the status name.
`OPTIMAL` means CP-SAT found a solution and proved that none is better.

The OR-Tools samples `interval_sample_sat.py` and `optional_interval_sample_sat.py` build the same
kinds of intervals; this lesson's `interval_basics.py` follows them.

## NoOverlap Lets One Crew Do One Job at a Time

An interval alone says nothing about other jobs. The rule "one crew does one job at a time" is a
statement about a whole set of intervals: no two of them may share a week. CP-SAT states it in one
call, `add_no_overlap(intervals)`. For two intervals $`[s_a, e_a)`$ and $`[s_b, e_b)`$ it means

```math
e_a \le s_b \quad \text{or} \quad e_b \le s_a
```

(one of them ends before the other starts), and it means that for every pair in the list.

The crew's five jobs, as one model. Each job $`j`$ has a start $`s_j`$, an end $`e_j`$ and an
interval of $`d_j`$ weeks; the **makespan** $`C`$ is the week the last job ends, and the objective is
to make it as small as possible:

```math
\begin{aligned}
& s_j, e_j \in \{0, \dots, H\},\ e_j = s_j + d_j && \forall j \in J && \text{(work}_j) \\
& C \in \{0, \dots, H\} \\
& \min \; C \\
& \text{NoOverlap}\big(\{[s_j, e_j) : j \in J\}\big) && && \text{(one crew)} \\
& C = \max_{j \in J} e_j && && \text{(makespan)}
\end{aligned}
```

$`J`$ is the set of the five jobs, $`d_j`$ their weeks, and $`H = 30`$ the horizon. In code:

```python
model = cp_model.CpModel()
start, end, task = {}, {}, {}
for j in WORK:
    start[j] = model.new_int_var(0, HORIZON, f"start_{j}")
    end[j] = model.new_int_var(0, HORIZON, f"end_{j}")
    task[j] = model.new_interval_var(start[j], job[j].weeks, end[j], f"work_{j}")
fixed = [model.new_fixed_size_interval_var(first, weeks, name) for name, (first, weeks) in blocked.items()]
model.add_no_overlap(list(task.values()) + fixed)

makespan = model.new_int_var(0, HORIZON, "makespan")
model.add_max_equality(makespan, [end[j] for j in WORK])
model.minimize(makespan)
```

`add_max_equality(target, expressions)` sets the target equal to the largest of the expressions; it
is how the job shop example on the OR-Tools site writes the makespan, and it is exact, not a bound.
(`fixed` is empty for now; the next section fills it.) With nothing blocked, the crew works without
a break:

```text
no blocked weeks
OPTIMAL: makespan 14 weeks, 14 weeks of work
  weeks  0- 3  P010
  weeks  4- 7  P011
  weeks  8- 9  P015
  weeks 10-11  P003
  weeks 12-13  P014
```

Each line gives the first and last week a job occupies. Five jobs that add up to 14 weeks end at
week 14: no idle week, which is the best one crew can do. Any order of the five jobs would also end
at week 14; the makespan does not prefer one order over another, and that is a point lesson 4.5.4
comes back to.

What does `add_no_overlap` save you? Write the same rule by hand: for every pair of jobs, one
Boolean variable says which comes first, and two **enforced** rows (lesson 4.4.2: a row with
`only_enforce_if(b)` holds only when the literal `b` is true) keep them apart:

```python
a_first = model.new_bool_var(f"{a}_before_{b}")
model.add(end[a] <= start[b]).only_enforce_if(a_first)
model.add(end[b] <= start[a]).only_enforce_if(~a_first)
```

`pairwise_order.py` writes that for every pair of the five jobs and the blocked weeks of the next
section, and gets the same answer:

```text
OPTIMAL: makespan 18 weeks with 20 order Booleans
```

Twenty Booleans for five jobs and two blocked periods (seven intervals make 21 pairs, and the
pair of two fixed periods needs none); the count grows with the square of the number of jobs. A MIP solver needs the same pairs, but it has no
`only_enforce_if`, so it writes each pair as two **big-M** rows with a Boolean $`y_{ab}`$ (1 when
$`a`$ comes first): $`e_a \le s_b + M(1 - y_{ab})`$ and $`e_b \le s_a + M y_{ab}`$. $`M`$ is a
constant at least as large as the horizon, so the row whose Boolean term is $`M`$ holds whatever
the starts are. Their LP relaxation is weak: with each Boolean at 1/2, both rows of a pair are
nearly free. Lesson 6.2.1, later in the course, derives such constants in depth.
`add_no_overlap` is one constraint over the whole set, and CP-SAT reasons about the set at once (for
example, that five jobs adding up to 14 weeks cannot all end before week 14) instead of pair by
pair. That set-level reasoning is why scheduling models are usually written with intervals in
CP-SAT.

## Fixed Intervals Block Weeks the Crew Cannot Work

The crew is not free all season. It has a training week at week 8 and is held for storm standby in
weeks 12 and 13. A blocked period is an interval too, a fixed one, and it goes into the same
`NoOverlap` as the jobs: then no job can share a week with it. In the code above, `blocked` maps a
name to (first week, number of weeks), and each entry becomes
`model.new_fixed_size_interval_var(first, weeks, name)`. The OR-Tools sample
`no_overlap_sample_sat.py` does the same with weekends, and `jobshop_with_maintenance_sat.py` with a
machine's maintenance window.

```text
training in week 8, storm standby in weeks 12-13
OPTIMAL: makespan 18 weeks, 14 weeks of work
  weeks  0- 3  P010
  weeks  4- 7  P011
  weeks  8- 8  training
  weeks  9-10  P014
  weeks 12-13  storm standby
  weeks 14-15  P015
  weeks 16-17  P003
```

The work still takes 14 weeks, but now it ends at week 18. Three weeks are blocked, and week 11
is idle: between the training and the standby there are three free weeks (9, 10 and 11), and every
job is 2 or 4 weeks long, so no set of jobs fills exactly three. Count it: 14 weeks of work, 3
blocked and 1 idle make 18. The solver did not need to be told that a job cannot be split around a block: an
interval is one unbroken span, so a two-week job either fits in a gap or goes after it.

Mind the conversion from a planner's calendar to an interval. A planner says "standby in weeks 12
to 13"; the interval is $`[12, 14)`$, size 2. Writing size $`13 - 12 = 1`$ blocks week 12 only and
lets a job run in week 13. Whenever a period is given by its first and last unit, the size is
$`\text{last} - \text{first} + 1`$.

<!-- practice 1 -->

## The Job Shop Is One NoOverlap per Machine and One Precedence Row per Step

The OR-Tools guide *The Job Shop Problem* is the standard first scheduling model. Several jobs each
pass through machines in a fixed order of **steps**; a machine works on one step at a time; a step,
once started, runs to its end. The guide's data are three jobs on three machines, each step a
pair (machine, processing time):

```python
jobshop({"job0": [("machine0", 3), ("machine1", 2), ("machine2", 2)],
         "job1": [("machine0", 2), ("machine2", 1), ("machine1", 4)],
         "job2": [("machine1", 4), ("machine2", 3)]})
```

The model has two kinds of rule, and each is one line in the loop:

- every machine gets a `NoOverlap` over the intervals of the steps that use it;
- every job's steps run in order: step $`k+1`$ starts no earlier than step $`k`$ ends, a
  **precedence** row $`s_{b,k+1} \ge e_{b,k}`$.

```python
horizon = sum(d for steps in jobs.values() for _, d in steps)
model = cp_model.CpModel()
start, end, on_machine = {}, {}, {}
for name, steps in jobs.items():
    for k, (machine, duration) in enumerate(steps):
        start[name, k] = model.new_int_var(0, horizon, f"start_{name}_{k}")
        end[name, k] = model.new_int_var(0, horizon, f"end_{name}_{k}")
        interval = model.new_interval_var(start[name, k], duration, end[name, k], f"{name}_{k}")
        on_machine.setdefault(machine, []).append(interval)
for intervals in on_machine.values():
    model.add_no_overlap(intervals)                               # one step at a time per machine
for name, steps in jobs.items():
    for k in range(len(steps) - 1):
        model.add(start[name, k + 1] >= end[name, k])            # a job's steps in order
```

The horizon is the sum of every step's time, as in the guide: if all steps ran one after another,
the schedule would end there, so no optimal schedule ends later. The makespan is the largest end of
each job's *last* step, through `add_max_equality` as before:

```text
OPTIMAL: makespan 11 (horizon 21)
  machine0   job1#0[0,2]  job0#0[2,5]
  machine1   job2#0[0,4]  job0#1[5,7]  job1#2[7,11]
  machine2   job1#1[2,3]  job2#1[4,7]  job0#2[7,9]
```

`job1#2[7,11]` is job 1's step 2 (counting from 0), in the span $`[7, 11)`$. The guide's optimal
length is 11 too. Read machine 1: job 2 uses it first, then job 0 waits for its own step 0 on
machine 0 to end at 5, then job 1's last step ends the schedule at 11.

Now move it onto GridCap, in working days. Vegetation work on a Valley circuit passes through three
crews: a climbing crew cuts, a chipper crew clears the brush, an inspector signs the circuit off.
The corridor widening P006 starts with the chipper crew's mower and then needs climbers for the
edge trees. Each crew is a machine, each project a job:

```python
jobshop({"P003": [("climbers", 3), ("chipper", 2), ("inspector", 1)],
         "P010": [("climbers", 5), ("chipper", 3), ("inspector", 1)],
         "P018": [("climbers", 6), ("chipper", 4), ("inspector", 2)],
         "P006": [("chipper", 4), ("climbers", 3), ("inspector", 1)]})
```

```text
OPTIMAL: makespan 18 (horizon 35)
  chipper    P006#0[0,4]  P018#1[6,10]  P010#1[11,14]  P003#1[14,16]
  climbers   P018#0[0,6]  P010#0[6,11]  P003#0[11,14]  P006#1[14,17]
  inspector  P018#2[10,12]  P010#2[14,15]  P003#2[16,17]  P006#2[17,18]
```

The climbers are the bottleneck: they have 3 + 5 + 6 + 3 = 17 days of work, and whichever job
they do last still needs at least one inspector day after it, so no schedule ends before day 18.
This one does. In it the chipper's mower starts P006 on day 0 (P006 is the only job whose first
step is not with the climbers) while the climbers start P018.

Only the data changed between the two runs; `jobshop` is the same function. That is the point of
the pattern: one NoOverlap per resource, one precedence row per consecutive pair of steps.

<!-- practice 2 -->

## Optional Intervals Let a Job Choose Its Crew

Back to weeks. Now there are two crews, A and B, and each job can go to either. Crew A has its
training week at week 8; crew B is still finishing last season's work in weeks 0 to 3. Which
crew does which job, and when?

A fixed interval cannot express "this job is on crew A's calendar or on crew B's". An **optional
interval** can: it has a **presence literal**, a Boolean, and when the literal is false the interval
is absent and every scheduling constraint ignores it. So give each job one optional interval per
crew, all on the job's one start and end, with presence $`x_{j,c}`$ ("crew $`c`$ does job $`j`$"),
and require exactly one presence per job:

```python
for j in WORK:
    start[j] = model.new_int_var(0, HORIZON, f"start_{j}")
    end[j] = model.new_int_var(0, HORIZON, f"end_{j}")
    for c in CREW_NAMES:
        does[j, c] = model.new_bool_var(f"{c}_does_{j}")
        on_crew[c].append(model.new_optional_interval_var(start[j], job[j].weeks, end[j], does[j, c], f"{j}_by_{c}"))
    model.add_exactly_one(does[j, c] for c in CREW_NAMES)
for c in CREW_NAMES:
    for first, weeks, name in BLOCKED[c]:
        on_crew[c].append(model.new_fixed_size_interval_var(first, weeks, f"{c}_{name}"))
    model.add_no_overlap(on_crew[c])
```

Each crew's `NoOverlap` gets that crew's optional intervals and its own blocked weeks. A job done by
crew A is present in crew A's list and absent from crew B's, so it uses crew A's weeks and none of
crew B's. The CP-SAT Primer builds meeting rooms the same way (one optional interval per room,
exactly one present), and warns against the shortcut of sharing one interval between rooms: an
interval in two NoOverlap lists is present in both, so it would occupy both crews.

```text
OPTIMAL: makespan 10 weeks
  crew A: P015 0-1, P014 2-3, P011 4-7, training 8-8
  crew B: finishing last season 0-3, P003 4-5, P010 6-9
```

Two crews end the work at week 10 instead of 14. Crew A takes 8 weeks of work before its training
week; crew B, free from week 4, takes 6. Nothing could end sooner. For the work to end by week 9,
crew A could use only weeks 0 to 7 (a job cannot run through its training week, and nothing fits
after it), 8 weeks, and crew B only weeks 4 to 8, 5 weeks: 13 weeks of room for 14 weeks of work.

`two_crews.py` also builds the shortcut the Primer warns about: one ordinary interval per job, placed
in both crews' lists.
CP-SAT accepts the model and proves its optimum, but the optimum is a different schedule: every
job occupies both crews at once, so each job must also avoid both crews' blocked weeks.

```text
one interval in both crews' lists: OPTIMAL, makespan 19 weeks
```

Nineteen weeks: worse than the 18 one crew needed in the previous section, because the jobs now
have to dodge crew B's weeks 0 to 3 as well as crew A's training week. A wrong model is still a
valid model; only the schedule tells you.

A presence literal is an ordinary Boolean: it can appear in other constraints and in the objective.
Lesson 4.5.3 ties one to a choice of contractor, and the job with no present interval at all, work
that is simply not done this season, is the same idea with "exactly one" relaxed to "at most one".

<!-- practice 3 -->

## The Model

The two-crew model of the last section, in one place. The one-crew model of the first sections is
the same with one crew, $`x_{j,A} = 1`$ for every job.

**Sets.** $`J`$ the jobs (P003, P010, P011, P014, P015); $`K`$ the crews (A, B); $`F_c`$ the blocked
periods of crew $`c`$.

**Parameters.** $`d_j`$, the weeks of work of job $`j`$; $`(f_b, n_b)`$, the first week and the
number of weeks of blocked period $`b`$; $`H = 30`$, the horizon in weeks.

**Variables.**

```math
\begin{aligned}
& s_j, e_j \in \{0, \dots, H\} && \forall j \in J && \text{(start and end week)} \\
& x_{j,c} \in \{0, 1\} && \forall j \in J,\ c \in K && \text{(crew } c \text{ does job } j\text{)} \\
& C \in \{0, \dots, H\} && && \text{(makespan)}
\end{aligned}
```

**Objective.**

```math
\min \; C
```

**Constraints.**

```math
\begin{aligned}
& e_j = s_j + d_j && \forall j \in J && \text{(work}_j\text{, by the interval)} \\
& \textstyle\sum_{c \in K} x_{j,c} = 1 && \forall j \in J && \text{(one crew}_j) \\
& \text{NoOverlap}\big(\{[s_j, e_j) \text{ if } x_{j,c} = 1 : j \in J\} \cup \{[f_b, f_b + n_b) : b \in F_c\}\big) && \forall c \in K && \text{(crew}_c) \\
& C = \max_{j \in J} e_j && && \text{(makespan)}
\end{aligned}
```

| Label | In `two_crews.py` |
| --- | --- |
| work$`_j`$ | `new_optional_interval_var(start[j], job[j].weeks, end[j], does[j, c], ...)`, one per crew |
| one crew$`_j`$ | `add_exactly_one(does[j, c] for c in CREW_NAMES)` |
| crew$`_c`$ | `add_no_overlap(on_crew[c])` |
| makespan | `add_max_equality(makespan, [end[j] for j in WORK])` |

The job shop adds one set of rows: $`s_{b,k+1} \ge e_{b,k}`$ for consecutive steps of each job
(order$`_{b,k}`$), with one NoOverlap per machine in place of one per crew.

## Summary

- **An interval variable ties a start, a size and an end together.** `new_interval_var` adds
  $`e = s + d`$; `new_fixed_size_interval_var` needs no end variable; a fixed span is the same call
  with a constant start. Every start and end has a finite horizon.
- **NoOverlap lets one crew do one job at a time.** It is one constraint over a set of intervals,
  in place of a Boolean and two enforced rows for every pair.
- **Fixed intervals block weeks the crew cannot work.** They go into the same NoOverlap; a period
  given by its first and last unit has size last − first + 1.
- **The job shop is one NoOverlap per machine and one precedence row per step.** The makespan is
  the largest end of each job's last step, written with `add_max_equality`.
- **Optional intervals let a job choose its crew.** One optional interval per crew on the job's
  start, a presence literal each, exactly one present, and one NoOverlap per crew.

## Reference

| Call | What it does |
| --- | --- |
| `new_interval_var(start, size, end, name)` | interval, and the constraint end = start + size |
| `new_fixed_size_interval_var(start, size, name)` | interval with a constant size; end is `start + size` |
| `new_optional_interval_var(start, size, end, is_present, name)` | interval that counts only when `is_present` is true |
| `new_optional_fixed_size_interval_var(start, size, is_present, name)` | the same with a constant size |
| `add_no_overlap(intervals)` | no two present intervals share a unit of time |
| `add_max_equality(target, exprs)` | target = the largest of the expressions |
| `interval.end_expr()`, `start_expr()`, `size_expr()` | the interval's parts, as expressions |

| Term | Meaning |
| --- | --- |
| horizon $`H`$ | the latest time any start or end may take |
| $`[s, e)`$ | the span from the start of unit $`s`$ to the start of unit $`e`$; it covers $`e - s`$ units |
| makespan | the time the last job ends |
| presence literal | the Boolean that says whether an optional interval exists |
| precedence row | $`s_{\text{next}} \ge e_{\text{previous}}`$ |

**Further reading:** OR-Tools, [The Job Shop Problem](https://developers.google.com/optimization/scheduling/job_shop),
the model and data `jobshop.py` adapts; the CP-SAT samples
[`interval_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/interval_sample_sat.py),
[`optional_interval_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/optional_interval_sample_sat.py)
and [`no_overlap_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/no_overlap_sample_sat.py)
(tasks around fixed weekends); the examples
[`jobshop_ft06_sat.py`](https://github.com/google/or-tools/blob/stable/examples/python/jobshop_ft06_sat.py)
and [`jobshop_with_maintenance_sat.py`](https://github.com/google/or-tools/blob/stable/examples/python/jobshop_with_maintenance_sat.py)
(a maintenance window as a fixed interval); the CP-SAT Primer,
[Advanced Modeling: scheduling and packing with intervals](https://d-krupke.github.io/cpsat-primer/advanced_modelling.html),
for the four kinds of interval and the multiple-rooms pattern;
[the CP-SAT solver page](https://developers.google.com/optimization/cp/cp_solver) for the statuses.

## Challenges

1. In `one_crew.py`, move the training week to week 4. Predict the makespan, then run it.
2. In `jobshop_crews.py`, give the climbers a second crew (a fourth machine, "climbers2") and let
   P018 use it. What happens to the makespan, and which crew becomes the bottleneck?
3. In `two_crews.py`, let some jobs be skipped: replace "exactly one" with "at most one" and
   maximize the weeks of work done by week 8. Which jobs are left out?

## Design Note: Intervals or Week-by-Week Booleans

There is another way to write a season: one Boolean per job and week, "job $`j`$ is worked in week
$`w`$", with rows that make each job's weeks consecutive and a crew's Booleans sum to at most one
per week. The CP-SAT Primer warns against reaching for intervals by reflex: when time comes in a
few fixed slots (shifts, days of a short roster), slot Booleans are often the better model, and
lesson 4.5.3 builds a roster that way. Intervals pay off when time is long or fine-grained: the
size of an interval model does not grow with the number of weeks, while the slot model needs a
variable for every job and week.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**season.py.** Derives the season's twelve vegetation jobs from GridCap small and prints them
(the table at the top of this lesson shows five of its lines). It is also the library every
program of the module imports. *Try:* Change the due-week rule so that every job with an RUL of 2
years or less is due at week 4. Predict how many jobs change.

- Program: [season.py](src/season.py)

**interval_basics.py.** Builds the three kinds of interval and shows that an interval is a
constraint (*An Interval Variable Ties a Start, a Size and an End Together*). *Try:* Make the size
of `trim_P014` 3 and the start bound `start >= 28`. Predict the status.

- Program: [interval_basics.py](src/interval_basics.py)

**one_crew.py.** One crew, five jobs, NoOverlap and the makespan, without and with blocked weeks
(*NoOverlap Lets One Crew Do One Job at a Time*, *Fixed Intervals Block Weeks the Crew Cannot
Work*). *Try:* Make the storm standby three weeks long. Predict the makespan.

- Program: [one_crew.py](src/one_crew.py)

**pairwise_order.py.** The same schedule with one order Boolean per pair instead of NoOverlap
(*NoOverlap Lets One Crew Do One Job at a Time*). *Try:* Add P018 to `WORK` in `one_crew.py`
first. Predict how many order Booleans the pairwise model then needs.

- Program: [pairwise_order.py](src/pairwise_order.py)

**jobshop.py.** The OR-Tools job shop, rewritten as a function, on the guide's data (*The Job Shop
Is One NoOverlap per Machine and One Precedence Row per Step*). *Try:* Swap job 2's two steps.
Predict whether the makespan rises.

- Program: [jobshop.py](src/jobshop.py)

**jobshop_crews.py.** The same function on four Valley vegetation jobs in working days. *Try:*
Shorten P018's climbing step to 3 days. Predict the new makespan before you run it.

- Program: [jobshop_crews.py](src/jobshop_crews.py)

**two_crews.py.** Two crews, optional intervals and exactly one crew per job (*Optional Intervals
Let a Job Choose Its Crew*). *Try:* Remove crew B's blocked weeks. Predict the makespan.

- Program: [two_crews.py](src/two_crews.py)

**cpsat_run.py.** The solve helper every program uses: one worker, and the status name. It runs
nothing itself.

- Library: [cpsat_run.py](src/cpsat_run.py)
