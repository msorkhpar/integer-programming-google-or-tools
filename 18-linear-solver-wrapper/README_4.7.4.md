# 4.7.4 Special-Purpose Solvers: LinearSumAssignment, KnapsackSolver and Bin Packing

Three requests reach GridCap's work planners in one week. Each of the eight crews must lead one of
the eight projects of the tiny portfolio this season: *which crew leads which project, at the least
cost?* A contract crew works one 12-month season: *which projects give it the most value?* And the
distribution and vegetation work must be hired out in whole seasons: *how few contract crews can do
it all?* These are an **assignment**, a **knapsack** and a **bin packing**, three model families
that a MIP can also state, as this lesson does to check each answer. Lessons 6.3.1 and 6.3.2, later
in the course, model the knapsack and assignment families as MIPs in depth.

OR-Tools has a dedicated solver for the first two, `SimpleLinearSumAssignment` and
`KnapsackSolver`. Each accepts only its own problem shape, works on whole numbers, and needs no
model at all. This lesson teaches both the way the OR-Tools pages do, checks each against a MIP on
GridCap, and shows where each one stops: the side rule that sends you back to a min-cost flow or a
MIP. Bin packing has no dedicated solver in OR-Tools, so it is a MIP, and a simple bound sometimes
makes the MIP unnecessary. GridCap, its crews, rates and seasons are fictional. Five rules, one per
heading.

## LinearSumAssignment Matches Each Worker to One Task at Least Cost

The **assignment problem**: $`n`$ workers, $`n`$ tasks, and a cost $`c_{w,t}`$ for worker $`w`$ to
do task $`t`$. Each worker does exactly one task, each task is done by exactly one worker, and the
total cost is as small as possible. As a MIP, with $`x_{w,t} = 1`$ when worker $`w`$ does task
$`t`$:

```math
\begin{aligned}
\min\;& \sum_{w} \sum_{t} c_{w,t}\, x_{w,t} \\
\text{s.t. }& \sum_{t} x_{w,t} = 1 \;\; \forall w && \text{(worker}_w) \qquad
\sum_{w} x_{w,t} = 1 \;\; \forall t \quad \text{(task}_t) \\
& x_{w,t} \in \{0, 1\}
\end{aligned}
```

`SimpleLinearSumAssignment`, in `ortools.graph.python.linear_sum_assignment`, solves exactly this
problem and nothing else. You give it one **arc** per allowed (worker, task) pair with its cost;
workers are the **left nodes** and tasks the **right nodes**, each numbered from 0. The OR-Tools
example, adapted from `assignment_linear_sum_assignment.py`:

```python
costs = np.array([
    [90, 76, 75, 70],
    [35, 85, 55, 65],
    [125, 95, 90, 105],
    [45, 110, 95, 115],
])
assignment = linear_sum_assignment.SimpleLinearSumAssignment()
# One arc per (worker, task) pair: three parallel arrays, as for the flow solvers.
end_nodes_unraveled, start_nodes_unraveled = np.meshgrid(np.arange(costs.shape[1]), np.arange(costs.shape[0]))
assignment.add_arcs_with_cost(start_nodes_unraveled.ravel(), end_nodes_unraveled.ravel(), costs.ravel())

status = assignment.solve()
if status == assignment.OPTIMAL:
    print(f"total cost = {assignment.optimal_cost()}")
    for worker in range(assignment.num_nodes()):
        print(f"  worker {worker} -> task {assignment.right_mate(worker)}, cost {assignment.assignment_cost(worker)}")
```

```text
total cost = 265
  worker 0 -> task 3, cost 70
  worker 1 -> task 2, cost 55
  worker 2 -> task 1, cost 95
  worker 3 -> task 0, cost 45
```

The `meshgrid` lines only turn the 4 × 4 table into three flat arrays (row number, column number,
cost), one entry per cell. `add_arc_with_cost(worker, task, cost)` adds one arc at a time, which is
what the GridCap program below does. After `solve()`:

- **the status** is `OPTIMAL`, `INFEASIBLE` (no way to give every worker a task through the arcs
  given), or `POSSIBLE_OVERFLOW` (costs so large that the integer arithmetic could overflow);
- **`optimal_cost()`** is the total;
- **`right_mate(w)`** is the task worker `w` got, and **`assignment_cost(w)`** what it costs;
- **`num_nodes()`** is the number of left nodes, the workers.

Costs are **integers**, as for the flow solvers in lesson 4.7.3. Scale cents or decimals to whole
units first:

```text
cost 1.5 -> TypeError: add_arc_with_cost(): incompatible function arguments. The following argument types are supported:
```

Now GridCap. Two crews are based in each region: a **line** crew, qualified for every program, at
$24k per crew-month, and a **field** crew, not qualified for transmission, at $18k. Leading a
project costs the crew's rate times the project's crew-months, plus travel when the project is in
another region. A field crew on a transmission project is not allowed, so **that pair gets no arc**,
the same rule a MIP follows by giving a pair that is not allowed no variable at all (lesson 6.3.2,
later in the course, uses that rule throughout):

```python
lsa = linear_sum_assignment.SimpleLinearSumAssignment()
for (c, s), k in cost.items():
    lsa.add_arc_with_cost(CREWS.index(c), sites.index(s), k)
status = lsa.solve()
```

```text
8 crews, 8 projects, 52 allowed pairs of 64
LinearSumAssignment: OPTIMAL, cost $752k
  Ridge line   -> P002 (transmission, Valley)  $150k
  Ridge field  -> P005 (vegetation, Ridge)  $54k
  Valley line  -> P007 (distribution, Valley)  $24k
  Valley field -> P006 (distribution, Valley)  $72k
  Coast line   -> P003 (transmission, Coast)  $144k
  Coast field  -> P001 (distribution, Ridge)  $104k
  Plains line  -> P004 (transmission, Plains)  $168k
  Plains field -> P008 (vegetation, Plains)  $36k
MIP (HiGHS): cost $752k, fractional variables: 0
LP relaxation (GLOP): cost $752k, fractional variables: 0
```

Three solvers, one answer: the dedicated solver, the MIP of the model above solved by HiGHS over
the 52 allowed pairs, and that MIP's LP relaxation, solved by GLOP with every $`x`$ between 0 and 1.
The relaxation came back whole with no branching. That is the property lesson 2.1.3 described: the assignment rows have the structure of a flow network (each variable in exactly one
worker row and one task row), so with whole-number data the LP has a whole optimal corner. It is
also why a solver built for this one problem exists. Checking it against the MIP, as here, is the
test to keep whenever you replace a MIP with a special-purpose solver.

Two crews travel, and the data says why. Coast has one project, P003, a transmission project that
no field crew may lead, so Coast's field crew has nothing at home and must work away. Valley has
three projects for its two crews, so one crew must come to Valley. The solver sent Ridge line to
P002 in Valley and Coast field to P001 in Ridge, the cheapest way to settle both moves for all
eight crews at once.

## The Table Must Be Square: Pad It With Dummy Tasks

The OR-Tools assignment example with a MIP (`assignment_mip.py`) has five workers and four tasks:
one worker stays idle. `SimpleLinearSumAssignment` needs every left node matched, and it has no
task for the fifth worker:

```text
5 workers x 4 tasks: INFEASIBLE
with a dummy task: OPTIMAL, cost 265
  worker 0 -> task 3
  worker 1 -> task 2
  worker 2 -> task 1
  worker 3 -> task 0
  worker 4 -> no task
MIP: cost 265
```

The fix is a **dummy task**, "no task", that every worker can take at cost 0. It squares the table
to 5 × 5, and whoever gets it is the idle worker:

```python
padded = [row + [0] for row in COSTS]                 # task 4 is "no task": cost 0 for everyone
```

The MIP of the OR-Tools page writes the same rule directly, with "at most one task" rows for
workers and "exactly one worker" rows for tasks, and agrees: 265. With more tasks than workers,
pad the other way: dummy workers, at cost 0 (when a task may stay undone) or at a large cost (when
leaving it undone should be a last resort).

<!-- practice 1 -->

## A Side Rule Moves Assignment to a Min-Cost Flow or a MIP

The OR-Tools page "Assignment with Teams of Workers" adds one rule: six workers in two teams, four
tasks, and **each team takes at most two tasks**. `SimpleLinearSumAssignment` has no place for
that rule. Without it, the cheapest assignment gives team B three tasks:

```text
no team rule: cost 235, workers [0, 1, 3, 5], team A takes 1
```

The rule fits a **min-cost flow** (lesson 4.7.3), as the OR-Tools sample `balance_min_flow.py`
builds it. A source sends one unit per task. It reaches the workers only through a **team node**
whose arc from the source has capacity 2, so no team can pass on more than two units. Each worker
passes at most one unit (arc of capacity 1), along a cost arc to a task, and each task passes one
unit to the sink:

```python
for team, members in TEAMS.items():
    smcf.add_arc_with_capacity_and_unit_cost(SOURCE, team_node[team], MAX_PER_TEAM, 0)  # the team rule
    for w in members:
        smcf.add_arc_with_capacity_and_unit_cost(team_node[team], worker_node[w], 1, 0)  # one task per worker
```

```text
min-cost flow: OPTIMAL, cost 250
  worker 0 (team A) -> task 2, cost 75
  worker 1 (team B) -> task 0, cost 35
  worker 4 (team A) -> task 3, cost 75
  worker 5 (team B) -> task 1, cost 65
MIP with team rows: cost 250
```

250, the cost the OR-Tools page reports, and the same as the MIP with one extra row per team,
$`\sum_{w \in \text{team}} \sum_t x_{w,t} \le 2`$. The rule cost $`250 - 235 = 15`$.

Where does each tool stop?

| Rule added to the assignment | Tool |
| --- | --- |
| none; square table (pad with dummies if not) | `SimpleLinearSumAssignment` |
| capacities on groups of workers or tasks (teams, regions) | `SimpleMinCostFlow` with a node per group |
| a worker takes several tasks whose **sizes** add up against its capacity | MIP: a generalized assignment (lesson 6.3.2, later) |
| pairs of workers that must work together, or logical rules | MIP or CP-SAT |

The sizes row is where the flow structure breaks. In a flow, every unit that passes a worker counts
the same against its capacity; a task of size 10 and a task of size 3 cannot weigh differently. With
sizes, the model is a **generalized assignment**: each task goes to exactly one worker, and the sizes
of a worker's tasks must fit its capacity. Its LP relaxation may split a task between workers: one
task of size 10 and two crews of capacity 6 have no whole assignment, yet the LP can put half of the
task on each crew (5 of 6 used on each). So the MIP needs branching. Lesson 6.3.2, later in the
course, treats the generalized assignment in depth. The OR-Tools sample `assignment_task_sizes_mip.py` solves the sizes variant as a
MIP, and the page "Assignment with Allowed Groups" solves the pairs variant with a MIP and with
CP-SAT.

## KnapsackSolver Picks Yes/No Items Under Capacity Rows, and Its Type Must Fit the Rows

Lesson 3.2.4 used `KnapsackSolver` as a cross-check on GridCap, and lesson 6.3.1, later in the
course, does so again. Here is its API in full.
The **0-1 knapsack**: items with values $`v_i`$ and weights $`w_{r,i}`$, each taken or not
($`x_i \in \{0, 1\}`$), maximizing total value under one or more capacity rows
$`\sum_i w_{r,i}\, x_i \le C_r`$. The OR-Tools example, adapted from `knapsack.py`, has 50 items and
one row:

```python
def solve(type_name: str, values, weights, capacities) -> tuple[int, list[int]]:
    solver = knapsack_solver.KnapsackSolver(getattr(knapsack_solver.SolverType, type_name), "example")
    solver.init(values, weights, capacities)
    best = solver.solve()
    return best, [i for i in range(len(values)) if solver.best_solution_contains(i)]
```

- `KnapsackSolver(solver_type, name)` picks the **algorithm** with a `SolverType` and gives the
  solver a name.
- `init(values, weights, capacities)` takes a list of values, a list of **weight lists, one per
  row**, and a list of capacities, one per row. With one row, `weights` is still a list holding one
  list: `[[7, 0, 30, ...]]`. All three must be **integers**; the page says so, and GridCap's capex and
  values are already whole $k.
- `solve()` returns the best total value, and `best_solution_contains(i)` says whether item `i` is
  in the best set.

```text
total value = 7534, total weight = 850, 32 items packed
```

7534, as the OR-Tools page reports. The program then runs the same data through every solver type,
once with the example's one row and once with a second row added ("at most 30 items"). Each run is
in a child process, for a reason the table makes plain:

```text
solver type                                      one row: weight <= 850           two rows: and at most 30 items
KNAPSACK_BRUTE_FORCE_SOLVER                      process stopped, exit code -6    process stopped, exit code -6
KNAPSACK_64ITEMS_SOLVER                          value 7534                       process stopped, exit code -6
KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER              value 7534                       process stopped, exit code -6
KNAPSACK_DIVIDE_AND_CONQUER_SOLVER               value 7534                       process stopped, exit code -6
KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER  value 7534                       value 7513
KNAPSACK_MULTIDIMENSION_CBC_MIP_SOLVER           value 7534                       value 7513
KNAPSACK_MULTIDIMENSION_SCIP_MIP_SOLVER          value 7534                       value 7513
KNAPSACK_MULTIDIMENSION_CP_SAT_SOLVER            value 7534                       value 7513
the solver's message for each stopped run:
  BRUTE_FORCE_SOLVER, 1 row: num_items_ <= kMaxNumberOfBruteForceItems (50 vs. 30) To use KnapsackBruteForceSolver the number of items should be less than 30. Current value: 50.
  BRUTE_FORCE_SOLVER, 2 rows: weights.size() == 1 (2 vs. 1) Brute force solver only works with one dimension.
  64ITEMS_SOLVER, 2 rows: weights.size() == 1 (2 vs. 1) Brute force solver only works with one dimension.
  DYNAMIC_PROGRAMMING_SOLVER, 2 rows: weights.size() == 1 (2 vs. 1) Current implementation of the dynamic programming solver only deals with one dimension.
  DIVIDE_AND_CONQUER_SOLVER, 2 rows: weights.size() == 1 (2 vs. 1) Current implementation of the divide and conquer solver only deals with one dimension.
```

Every type that ran agrees, with one row (7534) and with two (7513). But four types handle only
**one row**, and the brute-force type, in its message's words, "less than 30" items. Five runs
stopped, and each left one message. The 64-items type's message names the brute-force solver: the
two types report a second row with the same text, so read the run's label, not the message, to
know which type stopped. Given data they cannot handle, they do not
raise a Python exception: a failed internal check **stops the whole process** (exit code −6 is the
abort signal), and the messages above went to standard error. A `try`/`except` cannot catch that. So
pick the type from the data: a `MULTIDIMENSION` type whenever there may be more than one row, and
never the brute-force type for real data.

The GridCap question: which distribution and vegetation projects of the small portfolio give one
12-month crew season the most value? One row, crew-months as weights, NPV in $k as values:

```python
values = [p.value for p in work]                       # $k, whole numbers
weights = [[p.crew_months for p in work]]              # one row: a list holding one list
capacities = [SEASON]
```

```text
KnapsackSolver (dynamic programming): $4,267k from P019 P026 P034, 12 crew-months
MIP check (CP-SAT): $4,267k
```

The same as the MIP, solved by CP-SAT through MathOpt. But `KnapsackSolver` takes only values,
capacity rows and yes/no items, so it stops being enough the moment the plan needs a must-do, a
parent rule or a choice of start year: those are rows it has no way to state, and the plan is a MIP
again (lesson 6.3.1, later in the course, meets exactly this).

<!-- practice 2 -->

## Bin Packing Minimizes the Number of Bins, and a Lower Bound Can Prove a Heuristic Optimal

**Bin packing**: items of sizes $`s_i`$, bins of capacity $`C`$; put every item in some bin, using as
few bins as possible. OR-Tools has no dedicated bin-packing solver; its guide solves it as a MIP,
in pywraplp with SCIP. Here is that model ported to MathOpt (lesson 4.7.2), with $`x_{i,b} = 1`$
when item $`i`$ goes in bin $`b`$ and $`y_b = 1`$ when bin $`b`$ is used:

```python
    x = {(i, b): model.add_binary_variable(name=f"x_{i}_{b}") for i in items for b in bins}
    y = {b: model.add_binary_variable(name=f"y_{b}") for b in bins}
    for i in items:
        model.add_linear_constraint(sum(x[i, b] for b in bins) == 1, name=f"once_{i}")
    for b in bins:
        model.add_linear_constraint(sum(sizes[i] * x[i, b] for i in items) <= capacity * y[b], name=f"cap_{b}")
    for b in bins[1:]:
        model.add_linear_constraint(y[b] <= y[b - 1], name=f"order_{b}")     # use bin b only after bin b-1
    model.minimize(sum(y.values()))
```

Three rows to read:

- **`once`**: every item goes in exactly one bin.
- **`cap`** does two jobs. Its right side is $`C\, y_b`$: a used bin holds at most $`C`$, and an
  unused bin ($`y_b = 0`$) holds nothing. Without $`y_b`$ on the right, items could sit in bins the
  objective does not count.
- **`order`** is not in the OR-Tools guide's model. The bins are identical, so any packing can be
  relabelled in many ways: many packings that differ only in which identical bin got which label.
That is called **symmetry**, and lesson 6.7.3, later in the course, treats it in depth. "Use bin $`b`$
  only if bin $`b-1`$ is used" keeps one labelling of each choice of used bins, which removes some of
  the copies a search would otherwise explore. It changes no optimal count.

How many bins are offered? The guide offers one bin per item, always enough. The program does that
for the guide's data:

```text
11 items, total weight 370, bins of 100: at least 4 bins
MIP: OPTIMAL, 4 bins
  bin 0: items [0, 2, 10], weight 97
  bin 1: items [3, 4, 5], weight 99
  bin 2: items [1, 6, 9], weight 96
  bin 3: items [7, 8], weight 78
first fit decreasing: 4 bins
```

Four bins, as the guide reports, though its packing differs: several packings tie. Two other
numbers sit beside the MIP. The **lower bound** $`\lceil \sum_i s_i / C \rceil`$ is the total size
divided by one bin's capacity, rounded up: $`\lceil 370 / 100 \rceil = 4`$. No packing can use
fewer bins. **First fit decreasing** (FFD) is the classic heuristic: sort the items largest first,
and put each into the first bin with room, opening a new bin when none has room.

```python
    for i in sorted(range(len(sizes)), key=lambda i: -sizes[i]):
        for b in range(len(bins)):
            if sizes[i] <= room[b]:
                bins[b].append(i)
                room[b] -= sizes[i]
                break
        else:
            bins.append([i])
            room.append(capacity - sizes[i])
```

When the heuristic's count equals the lower bound, the heuristic is **proved optimal**, and no MIP
is needed. When they differ, either one may be off, and the MIP settles it. A small case where FFD
loses:

```text
sizes [3, 3, 2, 2, 2, 2], bins of 7: at least 2; first fit decreasing [[3, 3], [2, 2, 2], [2]]; MIP [[3, 2, 2], [3, 2, 2]]
```

FFD packs the two 3s together (6 of 7) and then has no room to place the 2s well. The MIP pairs each
3 with two 2s.

Now GridCap: 26 distribution and vegetation projects of the small portfolio, each a bundle of
crew-months one crew does whole, packed into 12-month contract seasons.

```text
26 projects, 74 crew-months, largest 6; seasons of 12: at least 7 crews
first fit decreasing: 7 crews, loads [12, 12, 12, 12, 12, 12, 2]
first fit decreasing meets the bound, so it is optimal: True
MIP, as a check: OPTIMAL, 7 crews
  crew 1: P005 P009 P012 P013 P027         12 crew-months
  crew 2: P003 P008 P014 P015 P029 P038    11 crew-months
  crew 3: P034                              5 crew-months
  crew 4: P023 P024 P037                   12 crew-months
  crew 5: P011 P035 P040                   11 crew-months
  crew 6: P006 P010 P026 P039              12 crew-months
  crew 7: P004 P018 P019 P020              11 crew-months
```

74 crew-months need at least $`\lceil 74 / 12 \rceil = 7`$ seasons, and FFD finds 7, so 7 contract
crews it is, proved by the bound alone. The MIP agrees, with a different packing: FFD fills six
seasons and leaves the seventh nearly empty, while the MIP's packing happens to spread the load.
Both count 7, which is all the objective asks. If planners also want the loads even, that is a new
objective, and only the MIP can take it.

<!-- practice 3 -->

## The Model

The three models of this lesson, in full.

**Assignment** (`SimpleLinearSumAssignment`; the MIP of `crew_to_site.py`). **Sets.** $`W`$, the
crews; $`T`$, the projects, with $`|W| = |T|`$; $`E \subseteq W \times T`$, the allowed pairs (a
field crew may not lead a transmission project). **Parameters.** $`c_{w,t}`$, the cost ($k) for crew
$`w`$ to lead project $`t`$: rate times crew-months, plus travel. **Variables.**
$`x_{w,t} \in \{0, 1\}`$ for $`(w, t) \in E`$.

```math
\begin{aligned}
\min\;& \sum_{(w,t) \in E} c_{w,t}\, x_{w,t} \\
\text{s.t. }& \sum_{t : (w,t) \in E} x_{w,t} = 1 && \forall w \in W && \text{(crew}_w) \\
& \sum_{w : (w,t) \in E} x_{w,t} = 1 && \forall t \in T && \text{(site}_t) \\
& x_{w,t} \in \{0, 1\} && \forall (w,t) \in E
\end{aligned}
```

With teams (`teams_flow.py`), add $`\sum_{w \in g} \sum_t x_{w,t} \le 2`$ for each team $`g`$
(team$`_g`$); with more workers than tasks, the worker rows become $`\le 1`$.

**Knapsack** (`KnapsackSolver`; `season_knapsack.py`). **Sets.** $`I`$, the distribution and
vegetation projects. **Parameters.** $`v_i`$, NPV ($k); $`m_i`$, crew-months; $`S = 12`$, the season.
**Variables.** $`x_i \in \{0, 1\}`$.

```math
\max\; \sum_{i \in I} v_i\, x_i \quad \text{s.t.} \quad \sum_{i \in I} m_i\, x_i \le S \;\; \text{(season)}, \qquad x_i \in \{0, 1\}
```

**Bin packing** (`bin_packing.py`). **Sets.** $`I`$, the items; $`B = \{0, \dots, K-1\}`$, the bins
offered. **Parameters.** $`s_i`$, item size; $`C`$, bin capacity. **Variables.**
$`x_{i,b} \in \{0, 1\}`$ (item $`i`$ in bin $`b`$); $`y_b \in \{0, 1\}`$ (bin $`b`$ used).

```math
\begin{aligned}
\min\;& \sum_{b \in B} y_b \\
\text{s.t. }& \sum_{b \in B} x_{i,b} = 1 && \forall i \in I && \text{(once}_i) \\
& \sum_{i \in I} s_i\, x_{i,b} \le C\, y_b && \forall b \in B && \text{(cap}_b) \\
& y_b \le y_{b-1} && \forall b \in B,\ b \ge 1 && \text{(order}_b) \\
& x_{i,b},\ y_b \in \{0, 1\}
\end{aligned}
```

## Summary

- **LinearSumAssignment matches each worker to one task at least cost.** Integer costs, one arc per
  allowed pair, `right_mate` for the answer. On GridCap's crews it matched the MIP and the LP
  relaxation: $752k.
- **The table must be square: pad it with dummy tasks.** Five workers and four tasks is
  INFEASIBLE until a cost-0 "no task" column is added; then 265, as the MIP finds.
- **A side rule moves assignment to a min-cost flow or a MIP.** Team caps fit a flow with a node per
  team (250); task sizes need a MIP, a generalized assignment.
- **KnapsackSolver picks yes/no items under capacity rows, and its type must fit the rows.**
  Integer data, weights as one list per row; one-row types stop the process on two rows.
- **Bin packing minimizes the number of bins, and a lower bound can prove a heuristic optimal.**
  $`\lceil \sum s_i / C \rceil`$ against first fit decreasing; GridCap's work needs 7 crews, proved
  by the bound.

## Reference

| Problem | OR-Tools tool | Input | Watch for |
| --- | --- | --- | --- |
| assignment, square | `SimpleLinearSumAssignment` | `add_arc_with_cost(w, t, c)` | integers; INFEASIBLE if not square or no perfect matching |
| assignment with group caps | `SimpleMinCostFlow` | source → group → worker → task → sink | supplies balance |
| assignment with sizes, pairs, logic | MathOpt MIP or CP-SAT | the model | |
| 0-1 knapsack, one row | `KnapsackSolver`, dynamic programming or branch and bound | `init(values, [weights], [capacity])` | integers |
| 0-1 knapsack, several rows | `KnapsackSolver`, a `MULTIDIMENSION_*` type | one weight list per row | a one-row type stops the process |
| bin packing | MathOpt MIP; check FFD against $`\lceil \sum s_i / C \rceil`$ first | the model | link bin use to capacity |

**Further reading:** [Solving an Assignment Problem (OR-Tools)](https://developers.google.com/optimization/assignment/assignment_example) (the assignment MIP with five workers and four tasks, "at most one" rows for workers); [Linear Sum Assignment (OR-Tools)](https://developers.google.com/optimization/assignment/linear_assignment) (the example adapted above; integer costs only, and why MIP and CP-SAT remain the usual choice for wider problems); [Assignment (OR-Tools)](https://developers.google.com/optimization/assignment) (the problem, and which OR-Tools solvers handle which variants); [Assignment with Teams of Workers (OR-Tools)](https://developers.google.com/optimization/assignment/assignment_teams) and [Assignment as a Minimum Cost Flow (OR-Tools)](https://developers.google.com/optimization/flow/assignment_min_cost_flow) (the team rule as a MIP, with CP-SAT, and as a flow with a node per team, cost 250); [Assignment with Allowed Groups (OR-Tools)](https://developers.google.com/optimization/assignment/assignment_groups) (a rule no flow can state: allowed pairs of workers, as a MIP and with CP-SAT); [The Knapsack Problem (OR-Tools)](https://developers.google.com/optimization/pack/knapsack) (the 50-item example, its integer-only data and weights given as a list of lists); [Solving a Multiple Knapsacks Problem (OR-Tools)](https://developers.google.com/optimization/pack/multiple_knapsack) (several knapsacks as a MIP and with CP-SAT); [Bin Packing (OR-Tools)](https://developers.google.com/optimization/pack/bin_packing) (the model ported above, with SCIP, and its 4-bin answer); [OR-Tools samples on GitHub](https://github.com/google/or-tools/tree/stable/ortools): `graph/samples/assignment_linear_sum_assignment.py`, `graph/samples/balance_min_flow.py`, `linear_solver/samples/assignment_task_sizes_mip.py`, `linear_solver/samples/bin_packing_mip.py`, `algorithms/samples/knapsack.py`.

## Challenges

1. In `crews.py`, let field crews lead transmission projects at their own rate. Predict whether
   the $752k falls, and which crews move.
2. Make one team in `teams_flow.py` allowed three tasks. Predict the cost before you run it.
3. In `crew_seasons.py`, make seasons 10 crew-months. Compute the lower bound by hand, then predict
   whether first fit decreasing still meets it.

## Design Note: Keep the MIP Next to the Special-Purpose Solver

A special-purpose solver is a promise about the problem's shape: square, integer, one row, no side
rules. Requirements change, and the shape changes with them. Keep the MIP of the same problem in the
code base with a test that compares the two on a few instances, as `crew_to_site.py` and
`season_knapsack.py` do. When a new rule arrives that the dedicated solver cannot state, the MIP is
already there, already trusted, and the switch is a one-line change at the call site.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**linear_sum_assignment_example.py.** The OR-Tools linear sum assignment example (*LinearSumAssignment
Matches Each Worker to One Task*). *Try:* Raise worker 3's cost for task 0 to 100. Predict the new
total.

- Program: [linear_sum_assignment_example.py](src/linear_sum_assignment_example.py)

**crew_to_site.py and crews.py.** GridCap's eight crews and eight tiny projects, solved by the
dedicated solver, the MIP and its LP relaxation (*LinearSumAssignment Matches Each Worker to One
Task*). *Try:* Halve every travel cost in `crews.py`. Predict whether the assignment changes.

- Program: [crew_to_site.py](src/crew_to_site.py)
- Library: [crews.py](src/crews.py)

**more_workers.py.** Five workers and four tasks: refused, padded with a dummy task, and checked by
a MIP (*The Table Must Be Square*), and a fractional cost refused (*LinearSumAssignment Matches Each
Worker to One Task*). *Try:* Give the dummy task a cost of 20 for worker 4 only.
Predict who stays idle.

- Program: [more_workers.py](src/more_workers.py)

**teams_flow.py.** The OR-Tools team assignment as a min-cost flow, beside the plain assignment and
the MIP (*A Side Rule Moves Assignment to a Min-Cost Flow or a MIP*). *Try:* Move worker 3 to team A.
Predict the cost.

- Program: [teams_flow.py](src/teams_flow.py)

**knapsack_types.py.** The OR-Tools 50-item knapsack with every solver type, on one row and on two
(*KnapsackSolver Picks Yes/No Items*). *Try:* Change the second row's limit from 30 to 32. Predict
which types change their value.

- Program: [knapsack_types.py](src/knapsack_types.py)

**season_knapsack.py.** One 12-month crew season filled from GridCap small, checked by CP-SAT
(*KnapsackSolver Picks Yes/No Items*). *Try:* Make the season 18 crew-months. Predict whether
P034 stays in.

- Program: [season_knapsack.py](src/season_knapsack.py)

**bin_packing_example.py, crew_seasons.py and bin_packing.py.** The OR-Tools bin-packing model in
MathOpt, first fit decreasing, the lower bound, and GridCap's crew seasons (*Bin Packing Minimizes
the Number of Bins*). *Try:* Remove the `order` rows in `bin_packing.py`. Predict whether any count
changes.

- Program: [bin_packing_example.py](src/bin_packing_example.py)
- Program: [crew_seasons.py](src/crew_seasons.py)
- Library: [bin_packing.py](src/bin_packing.py)
