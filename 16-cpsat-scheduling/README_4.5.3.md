# 4.5.3 Element, Table and Allowed-Assignment Constraints

Lessons 4.5.1 and 4.5.2 scheduled jobs whose length was known. GridCap's vegetation planners have
more choices than that. A Coast circuit can be trimmed by hand (slow and cheap), with a mechanical
mower or saw (faster, dearer), or with an aerial saw slung under a helicopter (fastest, dearest), and
the choice sets both the job's weeks and its cost. Some combinations do not exist at all: GridCap's
own crews have no aerial saw; the contractor has no climbers. And between jobs the crews travel:
three crews move between four regions and the yard week by week, and a move from the Coast to the
Ridge in one week is too far to drive.

These are rules of the form "this quantity is read from a list by that choice", "only these
combinations exist" and "never this pair". CP-SAT has a constraint for each: **element**, **table**
(`add_allowed_assignments`) and its opposite (`add_forbidden_assignments`). The lesson starts where
the OR-Tools scheduling guide starts its employee example, with the nurse roster, and ends with a
roster of GridCap's crews. (GridCap is fictional; the method data, prices and travel costs below
are invented for the lesson.)

## A Roster Is One Boolean per Person, Day and Shift

The OR-Tools guide *Employee Scheduling* rosters 4 nurses over 3 days of 3 shifts. Its model has
no intervals at all: time comes in a few fixed slots, so it uses one Boolean per nurse, day and
shift, $`x_{n,d,s} = 1`$ if nurse $`n`$ works shift $`s`$ on day $`d`$, and three families of rows:

```math
\begin{aligned}
& \textstyle\sum_{n} x_{n,d,s} = 1 && \forall d, s && \text{(each shift has one nurse)} \\
& \textstyle\sum_{s} x_{n,d,s} \le 1 && \forall n, d && \text{(at most one shift a day)} \\
& 2 \le \textstyle\sum_{d,s} x_{n,d,s} \le 3 && \forall n && \text{(fair share of the 9 shifts)}
\end{aligned}
```

`nurses.py` builds it as the guide does, with `add_exactly_one` and `add_at_most_one` (lesson 4.4.2)
for the first two families, and counts every schedule with a solution callback (lesson 4.4.3) and
`enumerate_all_solutions`:

```python
for d in DAYS:
    for s in SHIFTS:
        model.add_exactly_one(shifts[n, d, s] for n in NURSES)
for n in NURSES:
    for d in DAYS:
        model.add_at_most_one(shifts[n, d, s] for s in SHIFTS)
low = len(SHIFTS) * len(DAYS) // len(NURSES)                 # 9 // 4 = 2
high = low + (len(SHIFTS) * len(DAYS) % len(NURSES) != 0)    # 3, since 9 is not a multiple of 4
```

```text
OPTIMAL: 5184 schedules; each nurse works 2 to 3 shifts
  day 0: shift 0 -> nurse 3  shift 1 -> nurse 2  shift 2 -> nurse 0
  day 1: shift 0 -> nurse 1  shift 1 -> nurse 3  shift 2 -> nurse 0
  day 2: shift 0 -> nurse 2  shift 1 -> nurse 3  shift 2 -> nurse 1
```

5,184 schedules, the number the guide reports. (A model with no objective that has been enumerated
completely ends with status `OPTIMAL`.) The last section of this lesson moves this roster onto
GridCap's crews. First, the constraints it will need.

## Element Reads a List at a Variable Index

Back to one crew and the four Coast jobs P011, P012, P014 and P015. Each job $`j`$ has three
methods, numbered 0 (manual), 1 (mechanical) and 2 (aerial), and for each a length in weeks
$`W_{j,m}`$ and a cost $`C_{j,m}`$ in $k:

```python
DATA = {"P011": ([4, 2, 1], [60, 75, 110]),
        "P012": ([6, 3, 2], [90, 105, 160]),
        "P014": ([2, 1, 1], [30, 40, 55]),
        "P015": ([2, 1, 1], [35, 45, 70])}
```

Let the method be an integer variable $`m_j \in \{0, 1, 2\}`$. Then the job's length is
$`W_{j,m_j}`$: a list read at a position the solver chooses. That is the **element** constraint:

```math
\text{target} = \text{array}[\text{index}], \qquad \text{index} \in \{0, \dots, n - 1\}
```

and in CP-SAT, `add_element(index, expressions, target)`. Here the array holds constants, the
lengths or the costs; since OR-Tools 9.12 it may also hold variables or linear expressions, and the
index must land on a position of the array. Each job gets a method, a length and a cost, tied by two
elements, and its interval takes the length as a *variable* size:

```python
method[j] = model.new_int_var(0, len(METHODS) - 1, f"method_{j}")
weeks[j] = model.new_int_var(min(w), max(w), f"weeks_{j}")
cost[j] = model.new_int_var(min(c), max(c), f"cost_{j}")
model.add_element(method[j], w, weeks[j])           # weeks_j = W_j[method_j]
model.add_element(method[j], c, cost[j])            # cost_j  = C_j[method_j]
start = model.new_int_var(0, deadline, f"start_{j}")
end[j] = model.new_int_var(0, deadline, f"end_{j}")
tasks.append(model.new_interval_var(start, weeks[j], end[j], f"work_{j}"))
```

`new_interval_var` with a variable size still adds end = start + size (lesson 4.5.1), so when the
solver picks a faster method the interval shrinks. The crew does the jobs one at a time
(`add_no_overlap(tasks)`), every end is at most the deadline, and the objective is the total cost.
`methods_element.py` solves it for three deadlines:

```text
deadline week 14: OPTIMAL, cost $215k
  P011 manual     weeks 4  $60k
  P012 manual     weeks 6  $90k
  P014 manual     weeks 2  $30k
  P015 manual     weeks 2  $35k
deadline week 8: OPTIMAL, cost $255k
  P011 mechanical weeks 2  $75k
  P012 mechanical weeks 3  $105k
  P014 manual     weeks 2  $30k
  P015 mechanical weeks 1  $45k
deadline week 5: OPTIMAL, cost $355k
  P011 aerial     weeks 1  $110k
  P012 aerial     weeks 2  $160k
  P014 mechanical weeks 1  $40k
  P015 mechanical weeks 1  $45k
```

With 14 weeks, hand work fits (4 + 6 + 2 + 2 = 14) and is cheapest. With 8, the crew must save 6
weeks, and the cheapest way is mechanical on three jobs (2 + 3 + 2 + 1 = 8) for $40k more. With 5,
the two long jobs go aerial (1 + 2 + 1 + 1 = 5). The deadline buys speed, and element is what lets
the price of speed be read from the data.

## One Boolean per Option Does the Same, and an Interval's Size Must Be Affine

The CP-SAT Primer advises against reaching for element when Booleans will do: one Boolean per job
and method, $`u_{j,m}`$, exactly one of them true, and the length and cost as weighted sums,

```math
\textstyle\sum_m u_{j,m} = 1, \qquad \text{weeks}_j = \sum_m W_{j,m}\, u_{j,m}, \qquad \text{cost}_j = \sum_m C_{j,m}\, u_{j,m}
```

Both forms say the same thing, and a Boolean form is often clearer: each $`u_{j,m}`$ can appear
directly in other rules ("at most two aerial jobs a season" is a sum of $`u_{j,2}`$).

There is one catch in CP-SAT. An interval's start, size and end must each be **affine**: one
variable times a constant, plus a constant, or a constant. A weighted sum of three Booleans is not.
`methods_booleans.py` tries it first:

```text
a sum as the size: cp_model.new_interval_var: size must be affine or constant.
```

The fix is to give the sum a name, an integer variable equal to it, and to use that variable as the
size:

```python
weeks = model.new_int_var(min(w), max(w), f"weeks_{j}")
model.add(weeks == sum(w[m] * use[j, m] for m in range(len(METHODS))))
costs.append(sum(c[m] * use[j, m] for m in range(len(METHODS))))
start = model.new_int_var(0, deadline, f"start_{j}")
end = model.new_int_var(0, deadline, f"end_{j}")
tasks.append(model.new_interval_var(start, weeks, end, f"work_{j}"))
```

The cost needs no such variable: the objective accepts any linear expression. The answers are the
element model's:

```text
deadline week 14: OPTIMAL, cost $215k
deadline week 8: OPTIMAL, cost $255k
deadline week 5: OPTIMAL, cost $355k
```

Which to use? Element when the index is itself meaningful (a method number, a position in a
sequence, a region, as in the last section), Booleans when the options appear in other rules.
Either way, check the result against the other form once, as this section did.

The programs here print the cost with `solver.objective_value`. That value is a Python `float`,
even when every coefficient is a whole number, and a function that returns a cost must turn it into
an `int` with care. `objective_float.py` prices a rental two ways, in $k per day (coefficients 0.1
and 0.7) and in $100 per day (coefficients 1 and 7):

```python
cost = prices[0] * chipper + prices[1] * lift
model.minimize(cost)
solver, status = solve(model)
value = solver.objective_value
```

```text
prices [0.1, 0.7] $k/day: OPTIMAL, objective_value 19.999999999999996 (float)
  int() 19   round() 20
prices [1, 7] $100/day: OPTIMAL, objective_value 200.0 (float)
  int() 200   round() 200
  solver.value(cost) 200 (int)
```

The true cost is $20k, but with float coefficients the value is computed in floating point and
lands just below 20; `int()` cuts off the fraction and returns 19. `round()` returns the nearest
whole number, 20, so use `round(solver.objective_value)` whenever the cost is a whole number. With
whole-number coefficients you can also read the objective expression itself: `solver.value(cost)`
returns an `int`.

<!-- practice 1 -->

## A Table Lists Every Combination That Is Allowed

Now add a second choice: who does the job, GridCap's own crew or a contractor. The two do not offer
the same things:

| Method | Own crew | Contractor |
| --- | --- | --- |
| manual | yes | no (no climbers) |
| mechanical | yes | yes, $15k dearer |
| aerial | no (no aerial saw) | yes |

A rule over several variables at once, "the tuple (method, who, weeks, cost) is one of these rows",
is a **table constraint**: `add_allowed_assignments(expressions, tuples)`. The assignment of the
listed variables must equal one of the tuples, exactly. For each job the table has four rows, one
per offer:

```python
def rows(w: list[int], c: list[int]) -> list[tuple[int, int, int, int]]:
    """Allowed (method, who, weeks, cost) for a job with weeks w and in-house costs c by method."""
    return [(MANUAL, OWN, w[MANUAL], c[MANUAL]),
            (MECHANICAL, OWN, w[MECHANICAL], c[MECHANICAL]),
            (MECHANICAL, CONTRACTOR, w[MECHANICAL], c[MECHANICAL] + 15),
            (AERIAL, CONTRACTOR, w[AERIAL], c[AERIAL])]
```

The table does two jobs at once. It forbids the combinations nobody offers (manual by the
contractor, aerial by the own crew), and it *defines* the length and the cost of the ones that
exist, including a cost that depends on both choices. Element reads one list by one index; a table
relates any number of variables.

Keep the table whole. Split it into two smaller tables, allowed (method, who) pairs and allowed
(method, cost) pairs, and each pair is still right on its own, but the link between who and cost is
gone: mechanical appears with the own crew and with the contractor, and with $75k and with $90k for
P011, so the split tables let the contractor do P011 mechanically at the own crew's $75k. Only a
row that names all the variables together says which price goes with which provider.

`who` is a Boolean, `hired[j]`, 1 when the contractor does the job, and a Boolean is an integer
variable with values 0 and 1, so it can sit in the table. It is also a presence literal: each job
has an optional interval on the own crew, present when `~hired[j]` (the negation, "not hired"), and
one on the contractor, present when `hired[j]`, as crews were chosen in lesson 4.5.1:

```python
model.add_allowed_assignments([method[j], hired[j], weeks[j], cost[j]], rows(w, c))
start = model.new_int_var(0, deadline, f"start_{j}")
end = model.new_int_var(0, deadline, f"end_{j}")
on[OWN].append(model.new_optional_interval_var(start, weeks[j], end, ~hired[j], f"{j}_own"))
on[CONTRACTOR].append(model.new_optional_interval_var(start, weeks[j], end, hired[j], f"{j}_hired"))
```

```text
deadline week 8: OPTIMAL, cost $245k
  P011 manual     own crew   weeks 4  $60k
  P012 mechanical contractor weeks 3  $120k
  P014 manual     own crew   weeks 2  $30k
  P015 manual     own crew   weeks 2  $35k
deadline week 4: OPTIMAL, cost $280k
  P011 mechanical own crew   weeks 2  $75k
  P012 mechanical contractor weeks 3  $120k
  P014 mechanical own crew   weeks 1  $40k
  P015 mechanical own crew   weeks 1  $45k
deadline week 3: OPTIMAL, cost $330k
  P011 aerial     contractor weeks 1  $110k
  P012 mechanical own crew   weeks 3  $105k
  P014 aerial     contractor weeks 1  $55k
  P015 mechanical contractor weeks 1  $60k
deadline week 2: INFEASIBLE
```

With two crews working in parallel, week 8 costs $245k against $255k for one crew: the contractor
takes P012 at the mechanical price plus $15k, and everything else is done by hand. Every chosen row
is one the table allows: no manual job goes to the contractor and no aerial job to the own crew.
At week 2 there is no plan. P012 takes at least 2 weeks (aerial, so the contractor), which fills the
contractor's two weeks; the own crew would then need the three other jobs in 2 weeks, and the
fastest it can do them is mechanical, 2 + 1 + 1 = 4 weeks.

A table is the right tool when the allowed combinations are a short, explicit list. The CP-SAT
Primer notes it pays off when the table's variables also appear in other constraints, as here,
where weeks feed the intervals and cost the objective.

<!-- practice 2 -->

## Forbidden Pairs and a Flattened Element Price a Crew's Moves

Now the nurse roster, moved onto GridCap. Three crews (A, B, C) work an eight-week stretch. Each
week a crew is in exactly one place: one of the four regions or the yard. The vegetation plan says
how many crews each region needs each week, and every crew must spend at least one week in the yard
for equipment service. Moving a crew costs money, from a 5 × 5 table of travel costs, and a move
between the Coast and the Ridge in a single week is not allowed (two days' drive each way).

The guide's Booleans carry over directly: $`y_{c,w,p} = 1`$ if crew $`c`$ is in place $`p`$ in week
$`w`$, with exactly one place per crew and week, and one row per region and week for the demand.
The travel rule is about *pairs of consecutive weeks*, and for that an integer is handier than five
Booleans: the crew's place $`a_{c,w} \in \{0, \dots, 4\}`$, which a linear row ties to the
Booleans,

```math
a_{c,w} = \textstyle\sum_{p=0}^{4} p \cdot y_{c,w,p}
```

(exactly one $`y_{c,w,p}`$ is 1, so the sum is that place's number). The forbidden moves are a
**forbidden-assignment** constraint on the pair: `add_forbidden_assignments([a[c,w], a[c,w+1]],
[(COAST, RIDGE), (RIDGE, COAST)])` says the pair may take any value except those two rows. The
shift-scheduling example in the OR-Tools repository (`shift_scheduling_sat.py`) forbids a night
shift followed by a morning shift with a clause on the two Booleans; the table form says the same
for integer places.

The travel cost of a move is $`T[a_{c,w}][a_{c,w+1}]`$, a two-dimensional table read at two
variable indices. Element takes one index, so flatten the table row by row into a list of 25
numbers, where entry $`5p + q`$ is $`T[p][q]`$ (row $`p`$, the place the crew leaves; column
$`q`$, the place it goes to), and index it with the linear expression $`5\,a_{c,w} + a_{c,w+1}`$.
With $`n`$ places the multiplier is $`n`$, the length of a row, so that each pair of places gets
its own entry; a plain sum $`a_{c,w} + a_{c,w+1}`$ would not, since Coast to Ridge and Valley to
Valley both add up to 2. The order matters:
$`5\,a_{c,w+1} + a_{c,w}`$ reads $`T[q][p]`$, the move the other way, which is the same number
only while the table is symmetric, as this one is; a climb up to the Ridge that costs more than
the drive down would break it. In code:

```python
FLAT = [TRAVEL[p][q] for p in range(5) for q in range(5)]
```

```python
for c in CREWS:
    for w in WEEKS[:-1]:
        if forbid_coast_ridge:
            model.add_forbidden_assignments([at[c, w], at[c, w + 1]], [(COAST, RIDGE), (RIDGE, COAST)])
        move = model.new_int_var(0, max(FLAT), f"travel_{c}_w{w}")
        model.add_element(5 * at[c, w] + at[c, w + 1], FLAT, move)
        moves.append(move)
model.minimize(sum(moves))
```

The index of `add_element` may be an affine expression, as here; the program ran it as written.
`crew_roster.py` solves the roster with every move allowed and then with the Coast–Ridge pair
forbidden:

```text
every move allowed: OPTIMAL, travel $26k
  crew A: Coast  Coast  Ridge  Ridge  yard   yard   Ridge  Ridge
  crew B: Coast  Coast  Coast  Valley Valley Valley yard   Coast
  crew C: Plains Plains Plains Ridge  Ridge  Valley Valley yard
Coast-Ridge forbidden: OPTIMAL, travel $28k
  crew A: Coast  Coast  Plains Ridge  Ridge  Valley Valley yard
  crew B: Coast  Coast  Coast  Valley Valley Valley yard   Coast
  crew C: Plains Plains Ridge  Ridge  yard   yard   Ridge  Ridge
```

Each week's places meet the plan (week 0: two crews on the Coast and one on the Plains, and so
on), and every crew has a yard week. With every move allowed, crew A goes straight from the Coast
to the Ridge in week 2, at $6k. Forbidding that move costs $2k: crew A now goes Coast → Plains →
Ridge ($4k + $4k), and crew C, which was already on the Plains, takes the Ridge job of week 2.

<!-- practice 3 -->

## The Model

The crew roster of the last section, in one place.

**Sets.** $`K`$ the crews (A, B, C); $`W = \{0, \dots, 7\}`$ the weeks; $`P = \{0, \dots, 4\}`$
the places, the regions Ridge, Valley, Coast, Plains (0 to 3) and the yard (4); $`F`$ the forbidden
moves, $`\{(\text{Coast}, \text{Ridge}), (\text{Ridge}, \text{Coast})\}`$.

**Parameters.** $`n_{w,p}`$, the crews region $`p`$ needs in week $`w`$ (`NEED`); $`T_{p,q}`$, the
cost in $k of moving a crew from place $`p`$ to place $`q`$ (`TRAVEL`), flattened as
$`\tau_{5p+q} = T_{p,q}`$.

**Variables.**

```math
\begin{aligned}
& y_{c,w,p} \in \{0, 1\} && \forall c \in K,\ w \in W,\ p \in P && \text{(crew } c \text{ is in } p \text{ in week } w\text{)} \\
& a_{c,w} \in \{0, \dots, 4\} && \forall c \in K,\ w \in W && \text{(crew } c\text{'s place in week } w\text{)} \\
& v_{c,w} \in \{0, \dots, \max \tau\} && \forall c \in K,\ w \in W \setminus \{7\} && \text{(travel cost of the move after week } w\text{)}
\end{aligned}
```

**Objective.**

```math
\min \; \sum_{c \in K} \sum_{w = 0}^{6} v_{c,w}
```

**Constraints.**

```math
\begin{aligned}
& \textstyle\sum_{p \in P} y_{c,w,p} = 1 && \forall c, w && \text{(one place)} \\
& a_{c,w} = \textstyle\sum_{p \in P} p \cdot y_{c,w,p} && \forall c, w && \text{(place number)} \\
& \textstyle\sum_{w \in W} y_{c,w,4} \ge 1 && \forall c && \text{(yard week)} \\
& \textstyle\sum_{c \in K} y_{c,w,p} = n_{w,p} && \forall w,\ p \in \{0, 1, 2, 3\} && \text{(demand)} \\
& (a_{c,w}, a_{c,w+1}) \notin F && \forall c,\ w \le 6 && \text{(no long move)} \\
& v_{c,w} = \tau[\,5 a_{c,w} + a_{c,w+1}\,] && \forall c,\ w \le 6 && \text{(travel, element)}
\end{aligned}
```

| Label | In `crew_roster.py` |
| --- | --- |
| one place | `add_exactly_one(there[c, w, p] for p in range(5))` |
| place number | `add(at[c, w] == sum(p * there[c, w, p] ...))` |
| yard week | `add(sum(there[c, w, YARD] for w in WEEKS) >= 1)` |
| demand | `add(sum(there[c, w, p] for c in CREWS) == NEED[w].get(p, 0))` |
| no long move | `add_forbidden_assignments([at[c, w], at[c, w + 1]], [(COAST, RIDGE), (RIDGE, COAST)])` |
| travel | `add_element(5 * at[c, w] + at[c, w + 1], FLAT, move)` |

The method models of the earlier sections are stated in their sections: element ties
$`(\text{weeks}_j, \text{cost}_j)`$ to $`m_j`$; the table ties
$`(m_j, h_j, \text{weeks}_j, \text{cost}_j)`$ to the offers, with $`h_j \in \{0, 1\}`$ the
contractor Boolean, and each crew's intervals go into its NoOverlap.

## Summary

- **A roster is one Boolean per person, day and shift.** Exactly-one and at-most-one rows, and a
  count range for fairness; the guide's nurse roster has 5,184 schedules.
- **Element reads a list at a variable index.** `add_element(index, expressions, target)`; the
  target may then be an interval's size, a cost or anything else.
- **One Boolean per option does the same, and an interval's size must be affine.** Name a weighted
  sum with an integer variable before using it as a size.
- **A table lists every combination that is allowed.** `add_allowed_assignments(vars, tuples)`
  forbids the missing combinations and defines values that depend on several choices at once.
- **Forbidden pairs and a flattened element price a crew's moves.**
  `add_forbidden_assignments` removes listed tuples; a 2-D cost table is a flat list read at
  $`n\,p + q`$.

## Reference

| Call | Meaning |
| --- | --- |
| `add_element(index, expressions, target)` | target = expressions[index] |
| `add_allowed_assignments(expressions, tuples)` | the expressions' values form one of the tuples |
| `add_forbidden_assignments(expressions, tuples)` | the expressions' values form none of the tuples |
| `add_exactly_one(literals)`, `add_at_most_one(literals)` | exactly / at most one literal is true |
| `~b` | the negation of Boolean `b`, usable as a presence literal |
| `solver.parameters.enumerate_all_solutions = True` | report every solution to the callback |

| Rule in words | Constraint |
| --- | --- |
| "the length depends on the method" | element, or one Boolean per method with weighted sums |
| "only these (method, provider) offers exist, at these prices" | table |
| "never this pair of consecutive values" | forbidden assignments on the pair |
| "cost of going from $`p`$ to $`q`$" | element on the flattened table at $`n\,p + q`$ |

**Further reading:** OR-Tools,
[Employee Scheduling](https://developers.google.com/optimization/scheduling/employee_scheduling),
the nurse roster `nurses.py` and `crew_roster.py` adapt, and the example
[`shift_scheduling_sat.py`](https://github.com/google/or-tools/blob/stable/examples/python/shift_scheduling_sat.py)
(forbidden and penalized shift transitions); the CP-SAT Primer,
[Basic Modeling](https://d-krupke.github.io/cpsat-primer/modelling.html), its sections on element
and on domains and combinations (table constraints), with the advice to prefer Booleans; the
[CP-SAT solver page](https://developers.google.com/optimization/cp/cp_solver) on enumerating all
solutions.

## Challenges

1. In `methods_element.py`, add a fourth method to every job with weeks 3 and cost 50. Predict the
   cost at the week-8 deadline.
2. In `methods_table.py`, let the contractor also offer manual work at $20k over the in-house
   price. Predict whether the week-8 plan changes.
3. In `crew_roster.py`, forbid two yard weeks in a row. Predict whether the roster stays feasible,
   then check it.

## Design Note: Enumerating Is a Test, Not a Report

`nurses.py` counts 5,184 schedules, a number you can also work out by hand (the guide does). A count
that matches a hand count is a strong test that the model says what you meant: one missing row and
the count jumps, one extra row and it drops. Keep enumeration for small instances where you know the
answer; on a real roster the count is astronomically large and the search for all of them never
ends.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**nurses.py.** The guide's first nurse roster, counted with a solution callback (*A Roster Is One
Boolean per Person, Day and Shift*). *Try:* Change the fair share to exactly 2 or 3 shifts with
four nurses and four days. Predict whether any schedule exists.

- Program: [nurses.py](src/nurses.py)

**methods_element.py.** Method choice by element: weeks and cost read from lists, the interval's
size a variable (*Element Reads a List at a Variable Index*). *Try:* Make the aerial saw cost $200k
on P012. Predict the cost at week 5.

- Program: [methods_element.py](src/methods_element.py)

**methods_booleans.py.** The same choice with one Boolean per method, after showing the affine-size
error (*One Boolean per Option Does the Same, and an Interval's Size Must Be Affine*). *Try:* Add
"at most one aerial job" as a sum of Booleans. Predict the cost at week 5.

- Program: [methods_booleans.py](src/methods_booleans.py)

**objective_float.py.** One small rental model priced with float and with whole-number
coefficients, printing `objective_value`, `int()` and `round()` (*One Boolean per Option Does the
Same, and an Interval's Size Must Be Affine*). *Try:* Change the lift's minimum to 7 days. Predict
what `int()` prints for the $k prices.

- Program: [objective_float.py](src/objective_float.py)

**methods_table.py.** Who does each job and how, from a table of offers, with optional intervals
on the own crew and the contractor (*A Table Lists Every Combination That Is Allowed*). *Try:* Drop
the contractor's mechanical row. Predict the week-4 plan.

- Program: [methods_table.py](src/methods_table.py)

**crew_roster.py.** The nurse roster moved onto three crews and four regions, with a forbidden pair
of moves and a flattened travel table (*Forbidden Pairs and a Flattened Element Price a Crew's
Moves*). *Try:* Also forbid Valley to Plains. Predict the travel cost.

- Program: [crew_roster.py](src/crew_roster.py)
