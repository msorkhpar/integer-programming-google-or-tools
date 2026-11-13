# 6.7.2 Bound Tightening and Valid Inequalities

A contractor freeze reaches GridCap: next plan, every project on the small portfolio must be done by
in-house crews. Lesson 6.2.1 let a program hire a contractor when its own crews ran out; now each
program's crew-months per year are a hard limit, a row like any budget row. The planners rebuild the
model of lesson 6.4.1 with those crew rows and get a plan worth $22,741k, with an LP bound of
$25,262.67k above it.

Lesson 6.7.1 compared two formulations someone had already written. This lesson starts from one
formulation and makes it stronger without changing a single plan it allows, using only facts that
its own rows imply. There are two kinds of such facts. A **bound** fact says a variable can take
fewer values than its domain allows (here: a start year no plan can use, fixed at 0). A **valid
inequality** is a new row that every allowed plan already satisfies (lesson 6.3.3), here a row that
says "at most one of these starts". Lesson 3.3.2 showed how presolve derives facts of the first kind
from one row at a time, and lessons 6.1.3 and 6.3.3 wrote "at most one" rows and cover rows. This
lesson derives both kinds from the whole model, in four rules, and checks every fact it adds.

GridCap is a fictional utility's portfolio, generated for this course. Reading `crew_months` as the
crew-months a project needs in every year it is worked on is the reading of lessons 6.2.1 to 6.2.4.

## The Model

The multi-period model of lesson 6.4.1 on GridCap small, with crew rows added.

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i`$ the start years project $`i`$ may use;
$`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the child
projects, with parent $`p(c)`$ and lag $`L_c`$; $`G`$ the programs (transmission, distribution,
vegetation), $`P_g`$ the projects of program $`g`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`d_i`$, its years of work; $`B_y`$, the budget of year $`y`$ ($k);
$`m_i`$, the crew-months project $`i`$ needs in each year it is worked on; $`K_{g,y}`$, program
$`g`$'s in-house crew-months in year $`y`$.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$: project $`i`$ starts in year
$`t`$. With $`s_i = \sum_{t \in T_i} x_{i,t}`$, and "worked in $`y`$" meaning $`t \le y < t + d_i`$:

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
s_i &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
s_i &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} s_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\textstyle\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \textstyle\sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\textstyle\sum_{i \in P_g} \sum_{t \in T_i:\ t \le y < t + d_i} m_i\, x_{i,t} &\le K_{g,y} && \forall g \in G,\ y \in Y && \text{(crews}_{g,y}) \quad \leftarrow \text{this lesson}
\end{aligned}
```

This lesson adds two families to it, both derived below and both marked as derived, so a reader can
tell them from the business rules:

```math
\begin{aligned}
x_{i,t} &= 0 && \forall (i, t) \in Z && \text{(fixed: a bound)} \\
\textstyle\sum_{(i,t) \in Q} x_{i,t} &\le 1 && \forall Q \in \mathcal{Q} && \text{(clique}_Q\text{: a valid inequality)}
\end{aligned}
```

where $`Z`$ is the set of starts no plan can use and $`\mathcal{Q}`$ a set of cliques of starts, each
two of which no plan can use together. The code names the clique rows `cliques_0`, `cliques_1`, and
so on.

## A Row Leaves Each Variable Only What the Others Must Use

Take one capacity row, $`\sum_v a_v\, x_v \le b`$ with every $`a_v \ge 0`$, and one start $`x_u`$ in
it. If $`x_u = 1`$, the row must hold its $`a_u`$ plus whatever the other variables are *forced* to
use. Lesson 3.3.2 called that forced part the row's **least activity**, computed from the bounds. In
this model the bounds alone force nothing (every $`x`$ may be 0), but the must-do rows do: a must-do
project starts in one of its years, so it uses at least the smallest of its starts' uses of the row.
Call the total over the must-dos the row's **floor**, and $`b`$ minus the floor its **room**:

```python
    return row.capacity - sum(must_floor(portfolio, row, p.project_id, fixed)
                              for p in portfolio.projects if p.must_do)
```

If $`a_u`$ is more than the room, no allowed plan can set $`x_u = 1`$: the bound of $`x_u`$ tightens
from $`[0, 1]`$ to $`[0, 0]`$. For a must-do's own start, its floor is part of the room already, so
it is given back before the comparison:

```python
                if a > left + must_floor(portfolio, row, pid, fixed):
                    found[pid, t] = (rounds, row.name)
```

One fixing can lead to another. Fixing a must-do's start removes it from the must-do's choices, so
the must-do's smallest use of some other row can rise, that row's room falls, and more starts may
no longer fit. So the search runs in **rounds**, each using the fixings of the rounds before, until a
round finds nothing. This repeated use of bounds to tighten other bounds is called **bound
propagation**. On GridCap small, with budget and crew rows:

```text
8 of 80 starts can be fixed at 0:
  round 1: P006 starting 2031: needs 2 of crews_vegetation_2031 (2), and the must-dos leave 1
  round 1: P008 starting 2031: needs 3 of crews_vegetation_2031 (2), and the must-dos leave 1
  round 1: P010 (must-do) starting 2031: needs 2 of crews_vegetation_2031 (2), and the must-dos leave 1
  round 1: P011 starting 2031: needs 2 of crews_vegetation_2031 (2), and the must-dos leave 1
  round 1: P012 starting 2031: needs 3 of crews_vegetation_2031 (2), and the must-dos leave 1
  round 1: P018 starting 2031: needs 3 of crews_vegetation_2031 (2), and the must-dos leave 1
  round 1: P035 starting 2027: needs 3 of crews_vegetation_2027 (2), and the must-dos leave 2
  round 1: P037 starting 2031: needs 5 of crews_distribution_2031 (4), and the must-dos leave 4
as written    LP bound 25,262.67  MILP 22,741
starts fixed  LP bound 25,170.51  MILP 22,741
```

Vegetation has 2 crew-months in 2031, and the must-do P003, whose only start is 2031, takes 1 of
them. So any start that needs 2 or more vegetation crew-months in 2031 cannot be used, including the
must-do P010's: P010 must therefore start in 2030, its other year. P008, P012 and P018 would not fit
even with no must-do at all. One round found all eight here; a second round looked at the rows again
with P010 pinned to 2030 and found nothing new.

The MILP optimum does not move, as it cannot: only starts no plan could use were removed. The LP
bound falls by $92.16k, because the relaxation had been using fractions of those starts. Fixing a
variable is the strongest bound tightening there is, and it shrinks the model too.

<!-- practice 1 -->

## Two Starts That Cannot Both Be Used Are a Conflict, Whatever Row Says So

The same reasoning applies to pairs. Two starts $`u`$ and $`v`$ of different projects **conflict** if
together they need more of some row than its room: $`a_u + a_v > \text{room}`$ (with must-do floors
given back, as above). No allowed plan uses both, so $`x_u + x_v \le 1`$ is a valid inequality.
Conflicts also come straight from the model's other rows: two starts of the same project conflict
(the once row), and so do starts of two projects in one alternative group (the alt row).

```python
    for row in capacity_rows(portfolio, crews):
        left = room(portfolio, row, fixed)
        users = [s for s in row.use if s not in fixed]
        for u, v in itertools.combinations(users, 2):
            if u[0] == v[0]:
                continue
            extra = must_floor(portfolio, row, u[0], fixed) + must_floor(portfolio, row, v[0], fixed)
            if row.use[u] + row.use[v] > left + extra:
                reasons.setdefault(frozenset((u, v)), row.name)
```

Draw every start as a point and every conflict as a line between two points: that drawing is the
**conflict graph** of the model. On GridCap small there are 123 conflicting pairs, of which 70 are
not already stated by a once or alt row.

Each of those 70 could be added as a pair row. Lesson 6.1.3 showed why that is a weak way to say
"at most one": with a pair row for every two of six projects, its LP set five of them to 0.5, which
every pair row allows.

## A Clique of Conflicts Is One Valid Row, Stronger Than Its Pairs

A **clique** of the conflict graph is a set of starts that conflict two by two. For a clique $`Q`$,
any plan uses at most one of its starts, so

```math
\sum_{(i,t) \in Q} x_{i,t} \le 1 \qquad \text{(clique}_Q)
```

is valid. It implies every pair row inside $`Q`$ (drop the other terms, which are $`\ge 0`$), and the
pair rows do not imply it: the point with every start of a five-start clique at 0.5 satisfies all ten
pair rows and gives the clique row 2.5. So the clique row is stronger than its pairs, and it is one row
instead of $`|Q|(|Q| - 1)/2`$.

Lesson 6.1.3 had the clique handed to it by the business rule. Here the cliques must be found. Finding
the largest clique of a graph is itself a hard problem, so the program grows them greedily: each
conflict not yet covered starts a clique, which takes in, in a fixed order, every further start that
conflicts with all of its members:

```python
        clique = sorted(pair)
        for w in sorted(set.intersection(*(near[c] for c in clique))):
            if all(w in near[c] for c in clique):
                clique.append(w)
```

```text
conflicting pairs 123, of them not already in one once or alt row 70
cliques covering every conflict 39, of them new rows 19; sizes [5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 2, 2, 2]
the widest that repeats a project: x[P022,2027] + x[P022,2028] + x[P032,2028] + x[P036,2027] + x[P036,2028] <= 1
  x[P022,2027] and x[P022,2028]: once_P022
  x[P022,2027] and x[P032,2028]: crews_transmission_2028
  x[P022,2027] and x[P036,2027]: crews_transmission_2028
  x[P022,2027] and x[P036,2028]: crews_transmission_2028
  x[P022,2028] and x[P032,2028]: crews_transmission_2028
  x[P022,2028] and x[P036,2027]: crews_transmission_2028
  x[P022,2028] and x[P036,2028]: crews_transmission_2028
  x[P032,2028] and x[P036,2027]: budget_2028
  x[P032,2028] and x[P036,2028]: crews_transmission_2028
  x[P036,2027] and x[P036,2028]: once_P036
fixings + none     rows added   0  LP bound 25,170.51  HiGHS root bound 23,148  MILP 22,741
fixings + pairs    rows added  70  LP bound 24,719.96  HiGHS root bound 23,107  MILP 22,741
fixings + cliques  rows added  19  LP bound 24,580.01  HiGHS root bound 23,187  MILP 22,741
```

Of the 39 cliques that cover the conflicts, 20 lie inside one project's starts or one alternative group,
rows the model already has; 19 are new. The one printed shows why a clique can say more than any row
of the model. Its ten pairs conflict for three different reasons: two once rows, the transmission
crew row of 2028 (P022, P032 and P036 are all worked in 2028 from those starts, and any two of them
need more than 2028's 19 crew-months), and the 2028 budget row. No single row of the model says "at
most one of these five starts"; the clique row does.

The bounds line up as the argument says they must: 25,170.51 with fixings alone, 24,719.96 with the
70 pair rows, 24,580.01 with the 19 clique rows, fewer rows and a lower bound. The optimum is
$22,741k in all three.

HiGHS's root bound tells a different story: 23,148, 23,107 and 23,187, all within 0.4% of each other
and in no order the LP bounds would predict. Whatever HiGHS's presolve and root cuts did with each
model, they reached nearly the same bound from all three, so on this model the derived rows told the
solver little it did not work out itself. That is the measurement to make before adding derived rows
to a production model: they help most where the solver cannot derive them, for example from data
the model's rows do not contain, and in a model you solve only as an LP.

<!-- practice 2 -->

## A Derived Row Is Trusted Only After It Is Checked Against Whole Plans

A wrong bound or a wrong valid inequality does not raise an error. It removes plans the rules allow,
and the solver reports a worse optimum as if it were true (lesson 6.3.3's design note). So every
fact derived here is checked twice. On GridCap small, the MILP with all of them added must keep its
optimum, which the outputs above show. On GridCap tiny, where every 0/1 point can be listed, each
fixing and each clique row must hold for every allowed plan:

```text
13 start variables, 8192 0/1 points, 15 of them allowed plans
derived: 7 fixings, 3 clique rows; broken by an allowed plan: 0
planted row x[P002,2028] + x[P005,2027] <= 1 is broken by 6 allowed plans
```

The program lists all $`2^{13} = 8{,}192`$ points, keeps the 15 that satisfy every row, and finds no
allowed plan that breaks a derived fact. Then it plants a wrong row, a "conflict" between two starts
that some allowed plan uses together, and the same check catches it: 6 allowed plans break it. A
check that cannot fail proves nothing, so test the checker with a planted error as well.

Why is the brute force on tiny worth having when the small MILP already kept its optimum? The
optimum only tests the plans near the top. A wrong row that cuts off a plan worth less than the best
one would leave the optimum unchanged and still be wrong, and it would bite on next year's data.

## Summary

- **A row leaves each variable only what the others must use.** Capacity less the must-dos' floor is
  the room; a start that needs more is fixed at 0, and fixings propagate in rounds. Eight starts of
  GridCap small go, and the LP bound falls from 25,262.67 to 25,170.51.
- **Two starts that cannot both be used are a conflict, whatever row says so.** Once rows, alt rows
  and capacity rows all give conflicts; together they form the conflict graph.
- **A clique of conflicts is one valid row, stronger than its pairs.** 19 clique rows give a lower
  LP bound than 70 pair rows; HiGHS's root bound was within 0.4% across all three models.
- **A derived row is trusted only after it is checked against whole plans.** The MILP optimum must
  stay; on tiny, every allowed plan must satisfy every derived row, and a planted error must be caught.

## Reference

| Term | Meaning |
| --- | --- |
| floor of a row | the least the must-dos use of it, over their open starts |
| room | capacity less the floor |
| bound tightening | deriving a smaller range for a variable from the rows; a fixing is the extreme case |
| bound propagation | repeating it, each round using the bounds the last one found |
| conflict | two binaries no allowed plan sets to 1 together: $`x_u + x_v \le 1`$ is valid |
| conflict graph | starts as points, conflicts as lines |
| clique | a set of starts that conflict two by two: $`\sum_{Q} x \le 1`$ is valid and implies its pairs |

| GridCap small, crew rows hard | Rows added | LP bound | Optimum |
| --- | --- | --- | --- |
| as written | 0 | 25,262.67 | 22,741 |
| eight starts fixed | 0 | 25,170.51 | 22,741 |
| fixings and 70 pair rows | 70 | 24,719.96 | 22,741 |
| fixings and 19 clique rows | 19 | 24,580.01 | 22,741 |

**Further reading:** [MathOpt `SolveParameters`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py)
(OR-Tools source): `presolve` and `cuts`, the solver's own versions of this lesson's work ·
[Mixed-Integer Programming](https://developers.google.com/optimization/mip) (OR-Tools guide) ·
[Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf),
section 3.4: redundant rows, and the rows (facets) no strongest formulation can do without;
section 6.1: a big-M formulation is strongest when each constant is the largest value the row's
left side can take, a bound computed from the other rows, as in this lesson's first rule.

## Challenges

1. Halve every vegetation crew limit of GridCap small with `dataclasses.replace`. Predict whether a
   second round of fixings appears, then run `fixings.py`.
2. The greedy clique growth adds starts in sorted order. Add them in the reverse order instead.
   Predict whether the number of clique rows or the LP bound changes.
3. Two starts of the same project conflict. Do two starts of a parent and its child, with the child
   starting before the parent can, conflict too? Write the reason as a row of the model.

## Design Note: Keep Derived Rows Apart From Business Rules

`build` writes the business rules; `derived_rows.py` computes fixings and cliques from them, and the
programs add those afterwards, with their own names. Keeping them apart has two uses. A planner who
reads the model sees the rules as they were agreed, not a mix of rules and consequences. And when
the data change, the derived rows are recomputed from the new data and checked again, rather than
being carried over from a run where they were true.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**fixings.py.** Finds the starts of GridCap small that no plan can use, round by round, and solves
the model with and without them (*A Row Leaves Each Variable Only What the Others Must Use*).
*Try:* Leave the must-dos out of the room (use each row's capacity). Predict how many fixings
remain.

- Program: [fixings.py](src/fixings.py)

**clique_rows.py.** Builds the conflict graph, grows cliques, and compares pair rows with clique
rows (*Two Starts That Cannot Both Be Used Are a Conflict*, *A Clique of Conflicts Is One Valid
Row*). *Try:* Keep only the cliques of four or more starts. Predict where the LP bound lands.

- Program: [clique_rows.py](src/clique_rows.py)

**check_derived.py.** Lists every 0/1 point of GridCap tiny, keeps the allowed plans, and checks
every derived row on them, then a planted wrong one (*A Derived Row Is Trusted Only After It Is
Checked*). *Try:* Plant a wrong fixing instead of a wrong pair. Predict how many plans break it.

- Program: [check_derived.py](src/check_derived.py)

**derived_rows.py.** `capacity_rows`, `room`, `fixable`, `conflict_reasons` and `cliques`, shared by
the programs. It prints nothing.

- Library: [derived_rows.py](src/derived_rows.py)

**strong_model.py.** The model builder of lesson 6.7.1, with `crews=True` for the crew rows.

- Library: [strong_model.py](src/strong_model.py)
