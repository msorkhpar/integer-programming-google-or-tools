# 6.2.4 Disjunctions: Big-M vs. Hull

Three projects in GridCap small's Coast region work on the same substation: P011 (vegetation
clearing around it), P016 and P021 (transmission work in it). Each one needs the substation out of
service while its crew works, and the operator allows only one outage at a time, so the three jobs
cannot overlap within the year. The planners want an order that gets the assets back in service
as early as possible. "Job A finishes before job B starts, **or** job B finishes before job A
starts" is not a single linear row: it is a choice between two groups of rows, a **disjunction**.
This lesson writes it two ways, as big-M rows and as the **hull** formulation, and compares them by
the measure lesson 6.2.2 used, the LP bound, in four rules. (Lesson 6.4.3, later in this section,
uses the same measure on precedence rows.)

As in lesson 6.2.1, GridCap's data is fictional, and one reading of it is this lesson's own: each
project's `crew_months` is taken as the months its single crew works with the outage on.

## The Model

**Sets.** $`J`$ the jobs (P011, P016, P021); $`\Pi = \{(i, j) \in J \times J : i \text{ before } j \text{ in the list}\}`$
the pairs that share the outage (every pair here).

**Parameters.** $`d_j`$, job $`j`$'s duration in months (2, 3 and 5); $`H = 12`$, the months in the
year.

**Variables.** $`s_j \in [0,\, H - d_j]`$, the month job $`j`$ starts (continuous, so a job may start
mid-month), for $`j \in J`$. $`y_{ij} \in \{0, 1\}`$ for $`(i, j) \in \Pi`$: 1 if $`i`$ goes first,
0 if $`j`$ does.

**Objective.** Every month a job is unfinished, its asset waits; minimize the sum of finish months:

```math
\min \; \sum_{j \in J} (s_j + d_j)
```

**Constraints, as a disjunction.** For every pair, one of two rows holds:

```math
\big[\; s_i + d_i \le s_j \;\big] \;\vee\; \big[\; s_j + d_j \le s_i \;\big] \qquad \forall (i, j) \in \Pi \qquad \text{(order}_{ij})
```

The symbol $`\vee`$ reads "or". A disjunction is not yet something a MILP solver accepts; the next
two rules turn it into linear rows with the binary $`y_{ij}`$ choosing the side. Each side of the
"or", here a single row, is called a **disjunct**; in general a disjunct can be a whole group of rows.

## A Disjunction Written as Big-M Switches Each Disjunct With Its Own Binary

The big-M form gives each disjunct a switch, and ties the switches together so exactly one disjunct
is on. With one binary per pair, $`y_{ij}`$ switches on the first disjunct and $`1 - y_{ij}`$ the
second:

```math
\begin{aligned}
s_i + d_i &\le s_j + M (1 - y_{ij}) && \forall (i, j) \in \Pi && (i\text{\_before\_}j) \\
s_j + d_j &\le s_i + M\, y_{ij} && \forall (i, j) \in \Pi && (j\text{\_before\_}i)
\end{aligned}
```

$`M`$ follows from lesson 6.2.1's bound rule. With the switch off, the first row must allow every
pair of starts the bounds allow, so $`M`$ must cover the largest value of $`s_i + d_i - s_j`$: $`s_i`$
at its upper bound $`H - d_i`$ and $`s_j`$ at its lower bound 0, which gives
$`(H - d_i) + d_i - 0 = H`$. The same holds for the second row, so $`M = H = 12`$ months is the
smallest valid value from bounds. (With these durations it is also the exact $`M^\ast`$: $`s_i = H - d_i`$ and
$`s_j = 0`$ is a schedule the other disjunct allows.)

```python
def add_big_m(model, start, d, horizon, i, j, y) -> None:
    """y = 1: i before j; y = 0: j before i. M = horizon: the most s_i + d_i - s_j can be."""
    big = horizon
    model.add_linear_constraint(start[i] + d[i] <= start[j] + big * (1 - y), name=f"{i}_before_{j}")
    model.add_linear_constraint(start[j] + d[j] <= start[i] + big * y, name=f"{j}_before_{i}")
```

Solved as a MILP and as its LP relaxation:

```text
months of work: {'P011': 2, 'P016': 3, 'P021': 5}  horizon 12
big_m  variables  6  rows  6  LP bound 10.00  MILP  17.0  starts {'P011': 0.0, 'P016': 2.0, 'P021': 5.0}
       LP: starts [0.0, 0.0, 0.0]  first [0.25, 0.42, 0.42]
```

The best order is shortest job first: P011 in months 0 to 2, P016 in 2 to 5, P021 in 5 to 10, so
the finish months add up to 2 + 5 + 10 = 17. The LP relaxation is useless here. It starts all three
jobs in month 0, all at once, and sets each $`y_{ij}`$ to a fraction that keeps both rows of the pair
loose: with $`y_{P011,P016} = 0.25`$, the first row has $`12 \times 0.75 = 9`$ months of room and the
second $`12 \times 0.25 = 3`$, enough for P011's 2 months and P016's 3. The LP bound, 10, is just
the sum of the durations: the bound of a model with no outage rule at all, as with $`M = 10^6`$ in
lesson 6.2.2, except that here even the tightest $`M`$ cannot do better.

<!-- practice 1 -->

## The Hull Gives Each Disjunct Its Own Copy of the Variables

The big-M rows are weak because both disjuncts talk about the same $`s_i`$ and $`s_j`$, and a
fractional switch only loosens each row; it never forces the starts to be a mix of two orders that
actually work. The **hull** formulation (also called the convex-hull or Balas formulation, after the
disjunctive programming it comes from) fixes that by giving each disjunct its own copy of every
variable it mentions:

- Split each start into one copy per disjunct: $`s_i = s_i^a + s_i^b`$, where $`a`$ is the
  disjunct "$`i`$ first" (switched by $`y_{ij}`$) and $`b`$ is "$`j`$ first" (switched by
  $`1 - y_{ij}`$).
- Scale each copy's bounds by its disjunct's switch: $`0 \le s_i^a \le (H - d_i)\, y_{ij}`$, and so
  on. When a disjunct is off, its copies are forced to 0.
- Write each disjunct's row on its own copies, with every constant also multiplied by the switch:
  $`s_i^a + d_i\, y_{ij} \le s_j^a`$.

For one pair:

```math
\begin{aligned}
s_i &= s_i^a + s_i^b, \quad s_j = s_j^a + s_j^b && && \text{(split)} \\
0 \le s_k^a &\le (H - d_k)\, y_{ij}, \quad 0 \le s_k^b \le (H - d_k)(1 - y_{ij}) && k \in \{i, j\} && \text{(cap)} \\
s_i^a + d_i\, y_{ij} &\le s_j^a && && (i\text{\_before\_}j) \\
s_j^b + d_j\, (1 - y_{ij}) &\le s_i^b && && (j\text{\_before\_}i)
\end{aligned}
```

Why does this work? When $`y_{ij} = 1`$, every $`b`$ copy is 0, so $`s_i = s_i^a`$ and $`s_j = s_j^a`$,
and the $`a`$ row is the real "$`i`$ first" row; the $`b`$ row reads $`0 \le 0`$. When $`y_{ij}`$ is a
fraction $`\lambda`$, the $`a`$ copies describe a valid "$`i`$ first" schedule scaled by
$`\lambda`$, the $`b`$ copies a valid "$`j`$ first" schedule scaled by $`1 - \lambda`$, and the
starts are their sum: a weighted average of two real schedules. That is exactly the **convex hull**
of the disjunction, the smallest set without holes that contains every point either disjunct allows.
No formulation of a single disjunction can have a tighter LP relaxation, because every point of the
convex hull is an average of allowed points, and an LP cannot rule out an average of allowed points.

```python
def add_hull(model, start, d, horizon, i, j, y) -> None:
    """Each order gets its own copy of the two starts, scaled by that order's binary."""
    copies = {}
    for side, on in (("a", y), ("b", 1 - y)):
        for k in (i, j):
            copies[side, k] = model.add_variable(lb=0, name=f"s_{k}_{side}_{i}{j}")
            model.add_linear_constraint(copies[side, k] <= (horizon - d[k]) * on, name=f"cap_{k}_{side}_{i}{j}")
    for k in (i, j):
        model.add_linear_constraint(start[k] == copies["a", k] + copies["b", k], name=f"split_{k}_{i}{j}")
    model.add_linear_constraint(copies["a", i] + d[i] * y <= copies["a", j], name=f"{i}_before_{j}")
    model.add_linear_constraint(copies["b", j] + d[j] * (1 - y) <= copies["b", i], name=f"{j}_before_{i}")
```

The same three jobs:

```text
hull   variables 18  rows 24  LP bound 13.98  MILP  17.0  starts {'P011': 0.0, 'P016': 2.0, 'P021': 5.0}
       LP: starts [0.25, 1.83, 1.9]  first [0.92, 0.95, 0.63]
```

The MILP is the same, 17, with the same order: both forms allow the same whole-number schedules.
The LP bound rose from 10.00 to 13.98, closing $`3.98 / 7 \approx 57\%`$ of the gap to 17. The LP's
starts now spread out (0.25, 1.83, 1.9) instead of sitting at month 0, because each pair's starts
must be an average of two schedules in which the jobs do not overlap.

Why is 13.98 still below 17? The hull is the convex hull of *each* disjunction on its own. The model
has three of them, and the hull of each one separately is not the hull of all three together.
Formulating the whole model as one hull would need a disjunct for every complete order of the
jobs, which grows too fast to write (lesson 3.1.3).

Note the hull needed bounds too: each copy's cap $`(H - d_k)\, y_{ij}`$ is the variable's upper
bound times the switch. A disjunction over unbounded variables has no hull formulation of this kind,
for the same reason it has no valid big-M.

<!-- practice 2 -->

## The Hull Is Tighter but Bigger, and for One Variable a Tight Big-M Already Is the Hull

The price is in the first two columns of the outputs: the hull model has 18 variables and 24 rows
against the big-M model's 6 and 6. Every disjunction adds a copy of each variable it mentions, per
disjunct, and a cap row for each copy. On a model with thousands of pairs, that is real size. A
bigger model with a tighter bound is often the better model, but measure it; lesson 6.4.3, later in
this section, makes the same point for precedence rows.

There is also a common case where the hull buys nothing: a disjunction over **one** variable's
intervals, such as a contract that is either small, 100 to 300 $k, or large, 600 to 900 $k. With
the tight Ms from lesson 6.2.1, the big-M rows are $`s \le 300 + 600\,\ell`$ and
$`s \ge 600 - 500\,(1 - \ell)`$, with $`\ell`$ the "large" binary. Solving the LP relaxation of each
form for four different objectives:

```text
objective              tight big-M     hull   big-M with M = 10,000
max s - 450 large           450.0    450.0       873.0
min s + 200 large           100.0    100.0       100.0
max 2 s - 1300 large        600.0    600.0      1722.0
min 3 s - 900 large         300.0    300.0      -555.0
```

The tight big-M and the hull agree on every objective: in the plane of $`(s, \ell)`$, the two
big-M rows are exactly the two slanted edges of the convex hull of the two intervals, so the forms
describe the same LP region. The loose big-M is far off on three of the four. So the rule for
choosing is:

- **One variable, intervals:** a tight big-M is already the hull. Use it; it is smaller.
- **Disjuncts that tie several variables together** (sequencing, two modes with different
  costs): the hull can be much tighter, as on the outage pairs. Try both and compare LP bounds.
- **Either way,** every variable needs a finite bound, and the big-M needs it to be tight.

Lesson 5.1.3 writes disjunctions in
Pyomo's GDP language, which can build either form from one statement of the disjunction.

The same disjunction is the heart of the OR-Tools guide *The Job Shop Problem*. Three jobs of two
or three tasks run on three machines; a job's tasks run in order, a machine runs one task at a
time, and the goal is the earliest time the last job finishes, the **makespan**. The guide states
the machine rule for one pair of tasks exactly as this lesson does: one task finishes before the
other starts, or the other way round. CP-SAT then takes it for a whole machine at once: each task
is an **interval variable** (a start, a duration and an end tied together), and
`add_no_overlap` forbids any two intervals of a machine to overlap. `job_shop.py` solves the guide's
example that way, and as a MILP with this lesson's `add_big_m` and `add_hull` on every pair of tasks
that share a machine:

```python
for intervals in on_machine.values():
    model.add_no_overlap(intervals)                 # the disjunctions, all at once
```

```python
for a, b in combinations(TASKS, 2):
    if TASKS[a][0] == TASKS[b][0]:                  # same machine: a before b, or b before a
        y = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"first_{a}_{b}")
        (add_big_m if form == "big_m" else add_hull)(model, start, d, HORIZON, a, b, y)
```

```text
8 tasks on 3 machines, horizon 21
CP-SAT, add_no_overlap: makespan 11
MathOpt, big_m  LP bound  7.00  MILP makespan 11
MathOpt, hull   LP bound  8.20  MILP makespan 11
work per machine: {0: 5, 1: 10, 2: 6}
```

All three find the makespan of 11 the guide reports. The $`M`$ is the horizon, 21, the sum of all
durations, which is also the bound the guide puts on every start and end. The LP bounds repeat the
outage result: 7 for big-M, which is only the longest job (each job's three or two tasks take 7 in
a row), and 8.20 for the hull. Both are below 10, the work machine 1 must do in any schedule. Each
hull describes one pair of tasks, and no pair sees a whole machine's load; `add_no_overlap` states
the rule for all of a machine's intervals in one constraint.

## Summary

- **A disjunction written as big-M switches each disjunct with its own binary.** For sequencing, the
  smallest $`M`$ from bounds is the horizon; even so the LP starts every job at month 0, and its bound
  is that of a model with no outage rule.
- **The hull gives each disjunct its own copy of the variables.** Copies scaled by the switch make the
  LP relaxation of each disjunction its convex hull; on three outage jobs the bound rose from 10 to
  13.98 against an optimum of 17.
- **The hull is tighter but bigger, and for one variable a tight big-M already is the hull.** 18
  variables and 24 rows against 6 and 6; on one variable's intervals the two LPs were identical.

## Reference

| Form | Variables added per disjunction | LP relaxation | Needs |
| --- | --- | --- | --- |
| big-M | one binary (two disjuncts) | can be very weak | a valid M per row, from bounds |
| hull | one binary, plus a copy of each variable per disjunct | the convex hull of that disjunction | finite bounds on every variable |

| Term | Meaning |
| --- | --- |
| disjunction | a choice that at least one (here exactly one) of several groups of rows holds |
| disjunct | one group of rows in a disjunction |
| convex hull | the smallest convex set containing every allowed point; its points are weighted averages of allowed points |
| hull formulation | a disjunction written with a copy of the variables per disjunct, scaled by its switch |

**Further reading:** [The Job Shop Problem (OR-Tools)](https://developers.google.com/optimization/scheduling/job_shop) (the example of `job_shop.py`: the no-overlap rule for two tasks on one machine as an either-or of two rows, stated in CP-SAT with interval variables and `add_no_overlap`, and the horizon as the sum of all durations); [CP-SAT sample minimal_jobshop_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/minimal_jobshop_sat.py) (the same model as a complete program); [MathOpt sample facility_location.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/facility_location.py) (a binary that switches a continuous variable, written as $`y_{ij} \le x_i`$, the fixed-charge row with $`U = 1`$); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 5 gives the formulation with a copy of the variables per disjunct and when it is as tight as possible; section 6.1 gives the big-M formulation with the smallest constants, and shows it can still be weaker); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2: alternative, "either-or", constraints with a binary and two constants, here both 100); [MO-book 3.5, Machine scheduling](https://mobook.github.io/MO-book/notebooks/03/05-machine-scheduling.html) (the same no-overlap disjunction in Pyomo, converted by its big-M transformation from the times' bounds of 0 to 100, and written by hand with $`M = 10{,}000`$; compare both with the $`M = H`$ derived here).

## Challenges

1. Add a fourth job of 4 months to `outage_order.py`. Predict the MILP value from the shortest-job-first
   rule before running, then compare the two LP bounds.
2. Give the jobs release months (P021 may not start before month 3). Which $`M`$ changes, and to what?
3. Write the hull of the contract example by hand in the plane of $`(s, \ell)`$ and check that its two
   slanted edges are the tight big-M rows.

## Design Note: Name the Disjunct, Then Choose Its Form

`outage_model.build(..., form=...)` takes the form as a parameter, like `crew_model.build` in lesson
6.2.3. The disjunction itself, "these two jobs do not overlap", is the business rule; big-M and
hull are two ways to hand it to a MILP solver. Keeping the rule in one place (the loop over pairs)
and the form in another (`add_big_m`, `add_hull`) lets you switch forms with one argument and
measure, which is how the two LP bounds above were obtained.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**outage_order.py.** The three Coast outage jobs ordered with big-M rows and with the hull, as LP
and as MILP (*A Disjunction Written as Big-M*, *The Hull Gives Each Disjunct Its Own Copy*).
*Try:* Make the horizon 24 months. Predict which LP bound moves and which stays.

- Program: [outage_order.py](src/outage_order.py)

**one_variable.py.** A one-variable disjunction where the tight big-M and the hull give the same LP
(*The Hull Is Tighter but Bigger*). *Try:* Make the large interval 250 to 900, so the two overlap.
Predict whether the big-M rows still need the binary.

- Program: [one_variable.py](src/one_variable.py)

**job_shop.py.** OR-Tools' job shop example in CP-SAT with `add_no_overlap`, and as a MILP with
big-M and hull disjunctions per pair of tasks on a machine (*The Hull Is Tighter but Bigger*).
*Try:* Add the row "makespan at least the work on each machine" to the MILP. Predict both LP bounds.

- Program: [job_shop.py](src/job_shop.py)

**outage_model.py.** The outage model builder, with `add_big_m` and `add_hull`.

- Library: [outage_model.py](src/outage_model.py)
