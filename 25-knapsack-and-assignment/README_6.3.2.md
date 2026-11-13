# 6.3.2 Multiple Knapsack and Generalized Assignment

GridCap small's best plan (lesson 1.1.1's selection model) funds 20 projects that need 100
crew-months of field work over the five-year plan. The work-planning team has four regional crews,
one per region, with 30, 30, 20 and 20 crew-months free, and a contractor who can take up to 20
crew-months more at a higher rate. Planning asked "which projects?"; work planning asks "which crew
does each one?" A crew that works outside its own region loses a crew-month to travel and set-up,
and only some crews are qualified for transmission work.

Each crew is a knapsack: it has a capacity, and the projects it takes must fit in it. With several
crews sharing one list of projects the model becomes a **multiple knapsack**, and when every
project must be placed and its size depends on the crew, a **generalized assignment problem**
(GAP). This lesson builds both, adds the qualification rule, and looks at what the LP relaxation
does with them.

GridCap is a fictional utility's portfolio, generated for this course. Its crews, their capacities,
rates and qualifications are invented for this lesson.

## Several Knapsacks Share the Items: One Binary per Item and Knapsack

In lesson 6.3.1 there was one bag. Now there are several, $`K`$ of them, each with its own capacity
$`b_k`$, and each item goes into **at most one** of them. A binary per item is no longer enough,
because the model must say *which* knapsack an item is in. So there is one binary per item and
knapsack:

```math
x_{i,k} = \begin{cases} 1 & \text{item } i \text{ goes into knapsack } k \\ 0 & \text{otherwise} \end{cases}
\qquad x_{i,k} \in \{0, 1\} \quad \forall i \in I,\ k \in K
```

Two families of rows complete the **multiple knapsack**: each item is used at most once, and each
knapsack holds no more than its capacity.

```math
\begin{aligned}
\max \;& \sum_{i \in I} \sum_{k \in K} v_i\, x_{i,k} \\
\text{s.t. }& \sum_{k \in K} x_{i,k} \le 1 && \forall i \in I && \text{(once}_i) \\
& \sum_{i \in I} w_i\, x_{i,k} \le b_k && \forall k \in K && \text{(bin}_k)
\end{aligned}
```

The OR-Tools guide *Solving a Multiple Knapsacks Problem* uses this model with 15 items and five
bins of capacity 100. The program below is that example's data and rows, written in MathOpt and
solved with HiGHS (the OR-Tools sample uses the older `pywraplp` wrapper, which lesson 4.7.2 maps to
MathOpt):

```python
x = {(i, b): model.add_binary_variable(name=f"x_{i}_{b}") for i in items for b in bins}
for i in items:
    model.add_linear_constraint(sum(x[i, b] for b in bins) <= 1, name=f"once_{i}")       # at most one bin
for b in bins:
    model.add_linear_constraint(sum(weights[i] * x[i, b] for i in items) <= capacities[b], name=f"bin_{b}")
model.maximize(sum(values[i] * x[i, b] for i in items for b in bins))
```

```text
five bins of 100: value 395, weight 438
  bin 0: items [7, 13], weight 78
  bin 1: items [5, 12], weight 90
  bin 2: items [2, 4], weight 78
  bin 3: items [3, 8, 9], weight 96
  bin 4: items [1, 10, 14], weight 96
```

Value 395 and weight 438, the numbers the OR-Tools guide reports. Now the tempting shortcut: five
bins of 100 hold 500 in all, so why not one binary per item and one row, "total weight at most
500"? The same program solves that too:

```text
one pooled row of 500: value 410, weight 480
```

The **pooled row** promises 410, and no packing into the five bins achieves it: the multiple
knapsack's optimum is 395. Pooling forgets that items are indivisible and bins are separate. A set
of items can fit in the total and still not split into five groups of at most 100 each. Every
packing into the bins obeys the pooled row (add the five bin rows up and you get it), so the pooled
model is a **relaxation** of the multiple knapsack: it allows every plan the bins allow, and more.
Its optimum is a bound, not a plan.

On GridCap the knapsacks are the crews. The selection model keeps its binary $`y_i`$ (fund project
$`i`$) and its rows, and one row per project ties the two: a funded project gets exactly one crew,
an unfunded one none.

```python
x = {(p.project_id, k): model.add_binary_variable(name=f"x_{p.project_id}_{k}")
     for p in small.projects for k in CREWS}
for p in small.projects:
    model.add_linear_constraint(sum(x[p.project_id, k] for k in CREWS) == y[p.project_id],
                                name=f"crew_of_{p.project_id}")
for k in CREWS:
    model.add_linear_constraint(sum(p.crew_months * x[p.project_id, k] for p in small.projects) <= CAPACITY[k],
                                name=f"capacity_{k}")
```

The row $`\sum_k x_{i,k} = y_i`$ is the "at most once" row with the selection decision on its right:
when $`y_i = 0`$ it forces every $`x_{i,k}`$ to 0, and when $`y_i = 1`$ exactly one of them is 1.
With every crew taking any project at its own crew-months:

```text
GridCap small with crews Ridge 30, Valley 30, Coast 20, Plains 20:
  20 projects, NPV $25,336k, 100 crew-months
  Ridge    30 of 30: P015 P018 P021 P028 P029 P035 P039
  Valley   30 of 30: P010 P014 P017 P030
  Coast    20 of 20: P003 P032 P034
  Plains   20 of 20: P002 P011 P019 P022 P025 P038
```

The plan is unchanged ($25,336k), and its 100 crew-months pack exactly into the four crews. Many
other packings would do as well (the crews could swap projects of equal size), so the lists above
are one optimal answer among several, not *the* answer. And this model ignores something the work
planners care about: here the Ridge crew does P030, a Valley project, at no extra cost.

<!-- practice 1 -->

## Every Item Goes to Exactly One Agent, at a Size That Depends on the Agent

Two things change when the plan is fixed and only the crews are left to choose. First, every
project of the plan **must** be done, so "at most one crew" becomes "exactly one". Second, a
project's size depends on who does it: a regional crew working away from home needs one more
crew-month for travel and set-up, and the contractor needs none. The labour cost depends on the
crew too, $20k per crew-month for a GridCap crew and $35k for the contractor.

That is the **generalized assignment problem** (GAP): **agents** $`k`$ (the crews), each with a
capacity $`b_k`$; **tasks** $`i`$ (the projects), each of which must go to exactly one agent; a
size $`a_{i,k}`$ and a cost $`c_{i,k}`$ that depend on the pair. "Generalized" because the classic
**assignment problem** is the special case where every agent takes exactly one task of size 1.

```math
\begin{aligned}
\min \;& \sum_{i \in I} \sum_{k \in K} c_{i,k}\, x_{i,k} \\
\text{s.t. }& \sum_{k \in K} x_{i,k} = 1 && \forall i \in I && \text{(assign}_i) \\
& \sum_{i \in I} a_{i,k}\, x_{i,k} \le b_k && \forall k \in K && \text{(capacity}_k) \\
& x_{i,k} \in \{0, 1\} && \forall i \in I,\ k \in K
\end{aligned}
```

Each capacity row is a knapsack row over the tasks, with sizes that belong to that agent alone. The
sizes and costs are two small functions of the data:

```python
def size(p: Project, crew: str) -> int:
    """Crew-months project p takes if `crew` does it: one more for a regional crew away from home."""
    away = crew != CONTRACTOR and crew != p.region
    return p.crew_months + (TRAVEL if away else 0)
```

and the model is the formulation, row for row:

```python
def assignment_model(plan: list[Project], *, only_eligible: bool = False, integer: bool = True):
    """Every project of the plan to exactly one crew, within each crew's capacity, at least labour cost."""
    model = mathopt.Model(name="crew assignment")
    crews = CREWS + (CONTRACTOR,)
    x = {(p.project_id, k): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{k}")
         for p in plan for k in crews if not only_eligible or eligible(p, k)}
    for p in plan:
        model.add_linear_constraint(
            sum(x[p.project_id, k] for k in crews if (p.project_id, k) in x) == 1, name=f"assign_{p.project_id}")
    for k in crews:
        model.add_linear_constraint(
            sum(size(p, k) * x[p.project_id, k] for p in plan if (p.project_id, k) in x) <= CAPACITY[k],
            name=f"capacity_{k}")
    model.minimize(sum(cost(p, k) * var for (i, k), var in x.items() for p in plan if p.project_id == i))
    return model, x
```

(The `only_eligible` switch is for the next rule; leave it off for now.) Before solving, look at
each region's own work against its own crew:

```text
the plan: 20 projects, 100 crew-months
each region's own work against its crew:
  Ridge    19 of 30
  Valley   42 of 30  over
  Coast    28 of 20  over
  Plains   11 of 20
```

"Everyone works at home" is not a plan: Valley and Coast have 20 crew-months more work than their
crews, and Ridge and Plains have 20 crew-months to spare. Moving the surplus costs a crew-month per
project moved, so the crews' 100 crew-months can no longer carry 100 crew-months of work, and the
contractor must take some. HiGHS finds the cheapest mix:

```text
cheapest assignment: labour $2,135k
  Ridge       30 of 30; away from home: P030(Valley)
  Valley      28 of 30; away from home: -
  Coast       20 of 20; away from home: -
  Plains      20 of 20; away from home: P019(Ridge) P021(Coast)
  Contractor   5 of 20; away from home: -; projects P002 P011 P014
```

Check the cost by hand. All 100 crew-months at the in-house rate would cost $2,000k. Three projects
are done away from home, three extra crew-months at $20k: $60k. The contractor does 5 crew-months at
$35k instead of $20k: $75k more. $2,000k + $60k + $75k = $2,135k. The model moved the *small*
projects to the contractor (3 projects, 5 crew-months) and the *big* Valley project P030 to Ridge,
where one travel month on a 14-month project costs less than paying contractor rates on it.

The OR-Tools guide *Assignment with Task Sizes* solves a GAP of this shape in which the size of a
task is the same for every worker; only the cost depends on the pair. Ten workers share eight
tasks, each task goes to exactly one worker, and the sizes of a worker's tasks may add up to at
most 15. `task_sizes.py` is the guide's example (`assignment_task_sizes_mip.py` in the OR-Tools
repository) in MathOpt, row for row the GAP above:

```python
for w in workers:                                    # capacity: a knapsack row per worker
    model.add_linear_constraint(sum(TASK_SIZES[t] * x[w, t] for t in tasks) <= TOTAL_SIZE_MAX, name=f"size_{w}")
for t in tasks:                                      # every task to exactly one worker
    model.add_linear_constraint(sum(x[w, t] for w in workers) == 1, name=f"task_{t}")
```

```text
MILP: minimum cost 326, (worker, task) [(0, 6), (1, 0), (1, 2), (2, 4), (5, 5), (5, 7), (6, 1), (8, 3)]
```

The minimum, 326, is the guide's. The assignment is not quite the guide's: HiGHS gives task 4 to
worker 2 and the guide's run gives it to worker 4, both at a cost of 59. Two optimal answers that
differ only in a tie are both correct, which is one more reason to compare costs, never assignment
lists, when you check a model against a reference.

## An Agent That May Not Take an Item Gets No Variable

Only the Ridge and Valley crews and the contractor hold transmission qualifications. The simplest
way to forbid a pair is to leave its variable out of the model: a variable that does not exist
cannot be 1, and the model is smaller too. A crew that may not do a project gets no $`x_{i,k}`$
for it, so no row can ever assign it (lesson 6.4.1, later in this section, uses the same idea to
enforce a project's timing window: it creates no start variable for a year outside the window):

```math
x_{i,k} \text{ exists only for } (i, k) \in E, \qquad E = \{(i,k) : i \notin P_{\text{trans}} \text{ or } k \in K_{\text{line}}\}
```

That is the `only_eligible` switch above: the dictionary comprehension skips the pairs that are not
in $`E`$, and every row sums only over the pairs that exist (`if (p.project_id, k) in x`). The
alternative, creating every variable and adding a row $`x_{i,k} = 0`$ for each forbidden pair, gives
the same plans with more variables and rows for the solver to read and presolve away. Note what the
switch does not touch: every crew keeps its capacity, because Coast and Plains may still do
distribution and vegetation work; only the forbidden pairs disappear.

Fewer pairs can make the model infeasible, and a GAP's infeasibility is expensive to discover by
solving. Two quick checks catch the obvious cases first: every task must have at least one eligible
agent with enough capacity for it, and the qualified agents together must have room for the
qualified work at its smallest size:

```python
for p in plan:
    if not any(eligible(p, k) and size(p, k) <= CAPACITY[k] for k in crews):
        print(f"{p.project_id}: no crew can take it")
line_work = sum(min(size(p, k) for k in LINE_CREWS) for p in plan if p.program == "transmission")
```

Both are necessary conditions, not sufficient ones: passing them does not prove a packing exists,
as the pooled row showed in the first rule. Here every project has a crew, and:

```text
transmission work needs at least 68 crew-months; line crews have 80
any crew for any project: 100 variables, labour $2,135k
  Ridge       30 of 30: P028t P030t P035v
  Valley      28 of 30: P003v P010v P018v P022t P025t P032t
  Coast       20 of 20: P015v P017t P029d P039d
  Plains      20 of 20: P019d P021t P034d P038d
  Contractor   5 of 20: P002t P011v P014v
line crews only for transmission: 84 variables, labour $2,290k
  Ridge       30 of 30: P017t P019d P028t
  Valley      30 of 30: P025t P030t P032t
  Coast       14 of 20: P011v P014v P015v P029d P035v P039d
  Plains      16 of 20: P010v P018v P034d P038d
  Contractor  14 of 20: P002t P003v P021t P022t
```

The letter after each project is its program (t, d or v). The unrestricted answer had the Coast crew
on P017 and the Plains crew on P021, two transmission projects they are not qualified for. With the
16 forbidden pairs gone (100 variables down to 84), the transmission work squeezes into the three
line crews: Ridge and Valley are full of it, the contractor takes 14 crew-months, and Coast and
Plains pick up the vegetation work the line crews had to drop. The qualification rule costs $155k.

<!-- practice 2 -->

## The LP Relaxation Splits Items Between Agents

Relax every $`x_{i,k}`$ to $`[0, 1]`$ and a project may be shared, three quarters done by one crew
and a quarter by another. The assignment rows still add each project's shares up to 1, and the
capacity rows still charge each share its crew's size:

```text
whole crews: $2,290k; LP relaxation: $2,258.75k (1.4% below)
2 of 20 projects split between crews:
  P017: Ridge 0.750, Contractor 0.250
  P030: Ridge 0.500, Valley 0.500
```

The LP bound is $2,258.75k, so no assignment can cost less, and the whole-crew answer, $2,290k, is
within 1.4% of it. Only 2 of 20 projects are split, and a counting argument like lesson 6.3.1's says
a vertex can never split many. Say $`s`$ projects are split. Their fractional variables, at least
two per split project, are not at a bound, so at a vertex they must be pinned down by rows that hold
with equality, and the only rows they appear in are the $`s`$ assignment rows of the split projects
and the $`|K|`$ capacity rows. A vertex needs at least as many such rows as fractional variables, so
$`2s \le s + |K|`$, that is $`s \le |K|`$: at most one split project per agent. With 5 agents that
is 5, whether the plan has 20 projects or 2,000.

The guide's task-size example shows the same bound at work. Its LP relaxation, solved by GLOP:

```text
LP relaxation: 310.80; tasks split between workers: [3, 4, 7] (a vertex may split up to 10, one per worker)
```

Three of eight tasks are split, against a limit of ten, and the LP bound, 310.80, is 4.7% below
the whole-number 326.

The split itself is what branch-and-bound works on: branching on $`x_{P017,\text{Ridge}}`$ sends
P017 wholly to Ridge in one child and away from Ridge in the other (lessons 3.2.1 to 3.2.3).

Why is a split cheaper? P017 is a 13-month Coast transmission project. The Coast crew may not do it,
so it costs 14 crew-months with Ridge or Valley, or 13 contractor months at $35k. The LP gives three
quarters of it to Ridge and the rest to the contractor, a mix no real crew can work.

The classic assignment problem, one task per agent and every size 1, is the exception: its LP
relaxation always has a whole optimal vertex, which is why it has fast special algorithms; lesson 4.7.4
covers OR-Tools' solver for it.

## The Model

The crew assignment of GridCap small's plan: a generalized assignment problem with an eligibility
set. The multiple knapsack of the first rule is the same shape with "at most one" rows, one size per
item, and a value to maximize.

**Sets.** $`I`$, the projects of the plan (20); $`I_{\text{trans}} \subseteq I`$, its transmission
projects; $`K`$, the agents: the four regional crews and the contractor; $`K_{\text{line}} \subseteq
K`$, the agents qualified for transmission (Ridge, Valley, contractor); $`E \subseteq I \times K`$,
the allowed pairs: $`(i, k) \in E`$ unless $`i \in I_{\text{trans}}`$ and $`k \notin K_{\text{line}}`$.

**Parameters.** $`m_i`$, the crew-months project $`i`$ needs at home; $`a_{i,k} = m_i + 1`$ for a
regional crew outside its region, else $`m_i`$ (crew-months); $`r_k`$, agent $`k`$'s rate ($20k per
crew-month for a regional crew, $35k for the contractor); $`c_{i,k} = r_k\, a_{i,k}`$ ($k);
$`b_k`$, agent $`k`$'s capacity (30, 30, 20, 20 and 20 crew-months).

**Variables.**

```math
x_{i,k} \in \{0, 1\} \quad \forall (i, k) \in E \qquad \text{(1 if agent } k \text{ does project } i\text{)}
```

**Objective.**

```math
\min \; \sum_{(i,k) \in E} c_{i,k}\, x_{i,k}
```

**Constraints.**

```math
\begin{aligned}
\sum_{k : (i,k) \in E} x_{i,k} &= 1 && \forall i \in I && \text{(assign}_i) \\
\sum_{i : (i,k) \in E} a_{i,k}\, x_{i,k} &\le b_k && \forall k \in K && \text{(capacity}_k)
\end{aligned}
```

The code names the rows `assign_<project>` and `capacity_<crew>`.

## Summary

- **Several knapsacks share the items: one binary per item and knapsack.** $`x_{i,k}`$, at most one
  knapsack per item, one capacity row per knapsack. One pooled row is a relaxation: on the OR-Tools
  example it promised 410 where the bins allow 395.
- **In a generalized assignment, every item goes to exactly one agent, at an agent-dependent size.**
  Equality assignment rows, capacity rows with sizes $`a_{i,k}`$, costs $`c_{i,k}`$; GridCap's crew
  plan costs $2,135k with travel and a contractor.
- **An agent that may not take an item gets no variable.** Build the variables over the allowed
  pairs only, and check before solving that every task has a capable agent; qualifications raised
  the cost to $2,290k.
- **The LP relaxation splits items between agents.** Its bound was $2,258.75k with 2 projects split;
  branching on a split variable sends the project wholly to one side.

## Reference

| Model | Item rows | Capacity rows | Objective |
| --- | --- | --- | --- |
| multiple knapsack | $`\sum_k x_{i,k} \le 1`$ | $`\sum_i w_i x_{i,k} \le b_k`$ | max value |
| selection with agents | $`\sum_k x_{i,k} = y_i`$ | $`\sum_i w_i x_{i,k} \le b_k`$ | max value of the $`y_i`$ |
| generalized assignment | $`\sum_k x_{i,k} = 1`$ | $`\sum_i a_{i,k} x_{i,k} \le b_k`$ | min $`\sum c_{i,k} x_{i,k}`$ |
| bin packing | $`\sum_k x_{i,k} = 1`$ | $`\sum_i w_i x_{i,k} \le b\, u_k`$ | min $`\sum_k u_k`$ (bins used) |

| Check before solving | Catches |
| --- | --- |
| every task has an eligible agent with room for it | a task no one can take |
| qualified capacity at least the qualified work at its smallest size | a whole class of work no one can carry |

**Further reading:** [Solving a Multiple Knapsacks Problem (OR-Tools)](https://developers.google.com/optimization/pack/multiple_knapsack) (the example of `multiple_knapsack.py`: one binary per item and bin, at most one bin per item, a capacity row per bin, value 395 and weight 438); [Assignment with Task Sizes (OR-Tools)](https://developers.google.com/optimization/assignment/assignment_cp) (the generalized assignment of `task_sizes.py`, with a capacity on the total task size per worker, solved with CP-SAT and with the MIP solver to a minimum of 326); [The Bin Packing Problem (OR-Tools)](https://developers.google.com/optimization/pack/bin_packing) (how bin packing differs from the multiple knapsack: every item packed, as few bins as possible, a used binary per bin); [Solving an Assignment Problem (OR-Tools)](https://developers.google.com/optimization/assignment/assignment_example) (the classic assignment, at most one task per worker and one worker per task, with the MIP solver and CP-SAT); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: capital budgeting with several resources, and assigning crews to routes in airline crew scheduling).

## Challenges

1. Give the contractor no capacity at all. Predict whether `crew_assignment.py` still finds an
   assignment, using the region totals it prints, then run it.
2. Make travel cost two crew-months instead of one. Predict which projects stop moving between
   regions.
3. Write the bin-packing model of the Reference table for the OR-Tools example's 15 items and bins
   of 100, and say what row ties $`u_k`$ to the items, and why $`u_k`$ must be binary.

## Design Note: Identical Agents Make Identical Plans Look Different

Two crews with the same capacity, the same home region and the same rate are interchangeable: swap
everything they do and the cost is the same, yet the $`x_{i,k}`$ are different. A model with
$`n`$ identical crews has up to $`n!`$ copies of every assignment, and branch-and-bound may explore
them all. Lesson 6.7.3, later in this section, treats this; the usual cure is a row that
orders the copies, for example "crew 1's load is at least crew 2's". GridCap's crews differ in
region and capacity, which is one reason this lesson's model needed no such row.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**multiple_knapsack.py.** The OR-Tools multiple knapsack example in MathOpt, adapted from
`ortools/linear_solver/samples/multiple_knapsack_mip.py`, and the same items under one pooled row
(*Several Knapsacks Share the Items*). *Try:* Change the five bins to one bin of 500. Predict the
value.

- Program: [multiple_knapsack.py](src/multiple_knapsack.py)

**crews_knapsack.py.** GridCap small's selection model with four regional crews as knapsacks
(*Several Knapsacks Share the Items*). *Try:* Cut the Valley crew to 20 crew-months. Predict whether
the plan's NPV falls.

- Program: [crews_knapsack.py](src/crews_knapsack.py)

**crew_assignment.py.** The generalized assignment of the plan's 20 projects to the crews and the
contractor (*Every Item Goes to Exactly One Agent*). *Try:* Lower the contractor's rate to $21k.
Predict how many projects move to it.

- Program: [crew_assignment.py](src/crew_assignment.py)

**line_crews.py.** The checks before solving, and the assignment with and without the transmission
qualification (*An Agent That May Not Take an Item Gets No Variable*). *Try:* Take the Valley crew
off `LINE_CREWS`. Predict what the checks print.

- Program: [line_crews.py](src/line_crews.py)

**split_projects.py.** The LP relaxation of the qualified assignment and the projects it splits
(*The LP Relaxation Splits Items Between Agents*). *Try:* Relax only the contractor's variables.
Predict whether the cost changes.

- Program: [split_projects.py](src/split_projects.py)

**task_sizes.py.** OR-Tools' assignment with task sizes in MathOpt, as a MILP and as its LP
relaxation (*Every Item Goes to Exactly One Agent*, *The LP Relaxation Splits Items Between
Agents*). *Try:* Lower `TOTAL_SIZE_MAX` to 12. Predict which task no worker can take any more, and
what HiGHS reports.

- Program: [task_sizes.py](src/task_sizes.py)
