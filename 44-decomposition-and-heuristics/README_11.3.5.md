# 11.3.5 Rolling Horizon and LNS Heuristics

GridCap's medium portfolio, 400 projects over ten years with lesson 4.6.1's crew limits, is the
model the planners rerun in every scenario meeting. HiGHS proves its optimum, but only after a long
search: 21,794 branch-and-bound nodes in this lesson's run. In a meeting the planners need a good
plan from a fraction of that work, and an honest statement of how good it is. This lesson builds the
two heuristics most used for multi-period plans: a **rolling horizon**, which plans a few years at a
time, and **large neighborhood search** (LNS) around the MIP solver, which re-plans one part of a
plan at a time. Both are measured the same way, against the best bound known, and then against the
proven optimum, and one of them loses to the plain solver. That result is part of the lesson.

Lesson 4.6.1 showed CP-SAT's own LNS and a region-based LNS on the same portfolio with CP-SAT. This
lesson runs LNS around a MIP solver (HiGHS through MathOpt), adds neighborhoods by years, and
compares them. GridCap is a fictional utility's portfolio.

## The Model

Lesson 11.3.1's plan model with lesson 4.6.1's crew rows, `capital.build(medium, crews=True)`.

**Sets.** $`P`$ the projects; $`Y = \{2027, \dots, 2036\}`$; $`T_i`$, $`M`$, $`\mathcal{G}`$, $`C`$
as in lesson 11.3.1; $`G`$ the programs; $`P_g`$ the projects of program $`g`$.

**Parameters.** $`\text{npv}_{i,t}`$, $`c_{i,k}`$, $`B_y`$ as in lesson 11.3.1; $`m_i`$, the
crew-months project $`i`$ needs in each year of work; $`d_i`$ its years of work; $`K_{g,y}`$ the
crew-months of program $`g`$ in year $`y`$.

**Variables.** $`x_{i,t} \in \{0,1\}`$ for every $`i \in P`$, $`t \in T_i`$ (887 variables).

**Objective.** $`z^* = \max \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}`$.

**Constraints.** The once, must, alt, after and budget rows of lesson 11.3.1, and

```math
\sum_{i \in P_g} \ \sum_{t \in T_i,\ t \le y < t + d_i} m_i\, x_{i,t} \;\le\; K_{g,y} \qquad \forall g \in G,\ y \in Y \qquad \text{(crews}_{g,y})
```

## Every Heuristic Plan Is Reported Against the Best Bound Known

A heuristic returns a plan, never a proof. Its quality is the gap between its value and the best
**upper bound** known for the optimum (lesson 3.4.1's gap, with the heuristic's plan as the
incumbent). Bounds come from relaxations: the LP relaxation, a Lagrangian bound (lesson 11.3.1), or
a MIP search stopped early, whose best bound is the tightest of the three here. `rolling_lns.py`
first collects them, stopping the monolithic HiGHS search after a fixed number of nodes. A node
limit, not a time limit, so every run of the program prints the same numbers:

```python
for nodes in (200, 2000, 8000):
    params = mathopt.SolveParameters(node_limit=nodes, relative_gap_tolerance=0.0)
    cap = build(medium, crews=True)
    r = solve_highs(cap.model, params)
    early = early or schedule(cap, r)                     # the plan after 200 nodes
    bound = min(bound, r.termination.objective_bounds.dual_bound)
```

```text
LP relaxation bound 220,238.3
monolithic MILP stopped after a node budget:
    200 nodes  plan   219,411  bound   219,730.0  gap 0.15%
   2000 nodes  plan   219,451  bound   219,723.0  gap 0.12%
   8000 nodes  plan   219,482  bound   219,722.0  gap 0.11%
```

The best bound known is 219,722: no plan is worth more. The solver itself already has a plan within
0.15% of it after 200 nodes. Any heuristic below has to be judged against both numbers: the bound,
which says how far a plan could be from the best, and the solver's own plan for comparable work,
which says whether the heuristic was worth writing.

## A Rolling Horizon Plans a Few Years at a Time and Keeps Only the First Ones

A rolling horizon solves the plan in **windows** of $`W`$ years. In each window it decides the
starts in the window's years, keeps the first $`S`$ years of those decisions, and moves the window
forward $`S`$ years. Chapter 9 of LINDO's text describes multi-period models used this way, in a
rolling format: solve, implement the first period, slide forward.

For GridCap, window $`[a, b]`$ means, for each start variable:

- decided in an earlier window: fixed to that decision;
- a start after $`b`$: held at 0 for now (a later window decides it);
- a start in $`[a, b]`$: free.

A must-do project whose latest start lies beyond $`b`$ may wait for a later window, so its
`must_` row is relaxed to $`\le 1`$ until the window that contains its last chance. Budget and crew
rows stay in for every year, so money and crews a project will use after the window are counted
when it starts:

```python
for (pid, t), var in cap.x.items():
    if (pid, t) in decided:
        fix(var, decided[pid, t])
    elif t > last:
        fix(var, 0)
    else:
        var.lower_bound, var.upper_bound = 0, 1
```

```python
for pid, p in must.items():
    # A must-do may wait for a later window while its latest start lies beyond this one.
    rows[f"must_{pid}"].lower_bound = 1 if p.latest_start <= last else 0
```

```python
keep = years[i:i + step] if last != years[-1] else years[i:]
for (pid, t), var in cap.x.items():
    if t in keep:
        decided[pid, t] = round(result.variable_values(var))
```

Every window is solved to optimality, so the program's nodes count all the search it did:

```text
rolling horizon (window, years kept per window):
  window 3, keep 1:  plan   211,431  8 MIP solves,   441 nodes  gap to best bound 3.92%  breaks nothing
  window 4, keep 2:  plan   216,672  4 MIP solves,  5909 nodes  gap to best bound 1.41%  breaks nothing
  window 5, keep 2:  plan   217,929  4 MIP solves,  6592 nodes  gap to best bound 0.82%  breaks nothing
```

Every plan breaks no rule (`capital.violations` checks each one in plain Python). Longer windows
give better plans: 3.92% from the bound with 3-year windows, 0.82% with 5. The loss has a name,
the **end effect** (LINDO's section 9.8): a window that ends in year $`b`$ sees nothing beyond it,
so it spends money and crews on projects that start inside it, even when the same money would earn
more on a project whose best start comes later. Keeping only the first years of each window, and
re-deciding the rest, softens it; a longer window softens it more, at the price of a larger MIP.

And here is the honest part. The window-4 plan, after 5,909 nodes of search spread over four
windows, is worth 216,672; the monolithic solver had 219,411 after 200 nodes. On this model a
rolling horizon is the wrong tool for speed. Each window is not much smaller than the whole model
(every project that may start in the window is in it, with budget and crew rows for all ten years),
and GridCap's LP bound is tight (220,238.3, 0.28% above the optimum found below), so the monolithic
search finds good plans early. A rolling horizon earns its place when the whole horizon cannot be
built or solved at all, for example a twenty-year horizon of monthly periods, and as a source of a
first plan for something else.

<!-- practice 1 -->

## LNS Frees One Neighborhood of a Plan, Keeps the Rest, and Re-Solves

LNS takes a plan and improves it a part at a time (lesson 4.6.1 introduced it for CP-SAT). Each
step chooses a **neighborhood** $`F \subseteq P`$ of projects, fixes every other project to the
current plan, and solves the MIP that is left, here to optimality:

```math
x_{i,t} = \bar x_{i,t} \qquad \forall i \in P \setminus F,\ t \in T_i \qquad \text{(keep}_{i,t})
```

where $`\bar x`$ is the current plan. If the re-solved plan is worth more, it becomes the current
plan. The step can never make the plan worse, because the current plan is one of the plans the step
considers.

```python
for (pid, t), var in cap.x.items():
    if pid in free:
        var.lower_bound, var.upper_bound = 0, 1
    else:
        fix(var, 1 if current.get(pid) == t else 0)       # outside the neighborhood: keep the plan
result = solve_highs(cap.model, EXACT)
found = schedule(cap, result)
```

## A Neighborhood Must Free Projects That Compete for the Same Money and Crews

Two kinds of neighborhood, eight steps each, both starting from the window-4 plan:

- **by region:** all projects of one region (about 100), regions in turn, as lesson 4.6.1 did;
- **by years:** every project that starts, or could start, in a run of three years (about 140),
  moving two years each step.

```python
first = portfolio.years[(2 * index) % (len(portfolio.years) - 2)]
span = range(first, first + 3)
free = {p.project_id for p in portfolio.projects
        if (p.project_id in plan and plan[p.project_id] in span)
        or (p.project_id not in plan and any(t in span for t in p.starts()))}
```

```text
LNS from the window-4 plan, neighborhoods by region:
  step  1 free Ridge     (102 projects)  plan 216,672
  step  2 free Valley    (104 projects)  plan 216,672
  step  3 free Coast     ( 97 projects)  plan 216,672
  step  4 free Plains    ( 97 projects)  plan 216,709
  step  5 free Ridge     (102 projects)  plan 216,709
  step  6 free Valley    (104 projects)  plan 216,709
  step  7 free Coast     ( 97 projects)  plan 216,709
  step  8 free Plains    ( 97 projects)  plan 216,709
  final plan 216,709  54 nodes  gap to best bound 1.39%  breaks nothing
LNS from the window-4 plan, neighborhoods by years:
  step  1 free 2027-2029 (134 projects)  plan 216,976
  step  2 free 2029-2031 (135 projects)  plan 217,319
  step  3 free 2031-2033 (149 projects)  plan 217,995
  step  4 free 2033-2035 (134 projects)  plan 218,004
  step  5 free 2027-2029 (134 projects)  plan 218,138
  step  6 free 2029-2031 (136 projects)  plan 218,359
  step  7 free 2031-2033 (158 projects)  plan 218,491
  step  8 free 2033-2035 (134 projects)  plan 218,491
  final plan 218,491  2047 nodes  gap to best bound 0.56%  breaks nothing
```

Regions found $37k in eight steps; years found $1,819k. The reason is in the model. GridCap's
budget and crew rows are by year and program, not by region. Freeing one region while the other
three keep their plans leaves that region only the money and crews the others left over, which the
window plan had already used up: there is almost nothing to rearrange. Freeing three years frees
every project competing for those years' budgets and crews at once, including the end-effect
mistakes the rolling horizon made, so moving one project's start can make room for another's. This
is the CP-SAT Primer's point about LNS, seen on GridCap: a neighborhood should hold the variables
that interact.

<!-- practice 2 -->

## LNS Polishes the Solver's Own Early Plan Better Than a Rolling Horizon's

The rolling-horizon start was the weak link. The third run starts LNS from the monolithic solver's
plan after 200 nodes:

```text
LNS from the 200-node plan, neighborhoods by years:
  step  1 free 2027-2029 (136 projects)  plan 219,432
  step  2 free 2029-2031 (141 projects)  plan 219,459
  step  3 free 2031-2033 (155 projects)  plan 219,483
  step  4 free 2033-2035 (136 projects)  plan 219,541
  step  5 free 2027-2029 (136 projects)  plan 219,560
  step  6 free 2029-2031 (141 projects)  plan 219,560
  step  7 free 2031-2033 (153 projects)  plan 219,560
  step  8 free 2033-2035 (136 projects)  plan 219,560
  final plan 219,560  128 nodes  gap to best bound 0.07%  breaks nothing
```

200 nodes of monolithic search plus 128 nodes of LNS give 219,560, more than the monolithic search
reached in 8,000 nodes (219,482), and 0.07% from the best bound. Node counts are only a rough
measure of work here. An LNS node belongs to a smaller MIP, one with most variables fixed, and is
cheaper than a node of the whole model. If anything, then, the count overstates the work LNS did.

Then the proof. `medium_proof.py` runs the monolithic MILP to the end:

```text
OPTIMAL: plan 219,619, bound 219,619, 21,794 nodes, breaks nothing
```

With the optimum known, every number above can be checked. The LNS plan is $59k (0.027%) below the
optimum; its reported gap of 0.07% was honest and, as gaps against a bound are, pessimistic, because
the bound 219,722 was itself $103k above the optimum. The window-4 rolling-horizon plan is 1.34%
below. A planner who had stopped at "the heuristic's plan" without a bound would have had no way to
tell these two apart.

## The Model

One LNS step, whole: the plan model with the neighborhood rows added.

**Sets, parameters, variables, objective.** As in the model above, plus $`F \subseteq P`$, the
projects the step frees, and $`\bar x`$, the current plan ($`\bar x_{i,t} \in \{0,1\}`$, a
parameter).

**Constraints.** The once, must, alt, after, budget and crew rows, and

```math
x_{i,t} = \bar x_{i,t} \qquad \forall i \in P \setminus F,\ t \in T_i \qquad \text{(keep}_{i,t}) \quad \leftarrow \text{this lesson}
```

written in code as bounds: both bounds of $`x_{i,t}`$ set to $`\bar x_{i,t}`$.

One rolling-horizon window $`[a, b]`$, whole: the same model with, for every $`i, t`$,
$`x_{i,t} = \hat x_{i,t}`$ if $`t < a`$ (decided by earlier windows), $`x_{i,t} = 0`$ if $`t > b`$,
and $`\text{must}_i`$ relaxed to $`\sum_t x_{i,t} \le 1`$ for must-do projects with latest start
after $`b`$. It keeps the decisions for years $`a, \dots, a + S - 1`$ (all remaining years in the
last window).

## Summary

- **Every heuristic plan is reported against the best bound known.** On GridCap medium with crews:
  bound 219,722 from 8,000 nodes, LP 220,238.3.
- **A rolling horizon plans a few years at a time and keeps only the first ones.** Longer windows
  gave better plans (3.92% to 0.82% from the bound), but here the monolithic solver beat all of them
  with 200 nodes: the windows were nearly as big as the model and its LP bound is tight.
- **LNS frees one neighborhood of a plan, keeps the rest, and re-solves.** It cannot make a plan
  worse.
- **A neighborhood must free projects that compete for the same money and crews.** Region
  neighborhoods gained $37k, three-year neighborhoods $1,819k, because GridCap's limits are by year.
- **LNS polishes the solver's own early plan better than a rolling horizon's.** 200 + 128 nodes gave
  219,560, 0.027% from the proven optimum 219,619, which took 21,794 nodes.

## Reference

| Heuristic | Fixes | Frees | Strength | Weakness |
| --- | --- | --- | --- | --- |
| rolling horizon | earlier windows' decisions; starts after the window at 0 | starts inside the window | each window's model is smaller in time; works when the whole horizon cannot be built | end effects; on a tight model, worse than the solver |
| LNS | the current plan outside the neighborhood | the neighborhood | never worse than its start; uses problem structure | needs a good start and the right neighborhoods |

| Number to report | Where it comes from |
| --- | --- |
| plan value | the heuristic, checked against every rule in plain Python |
| best bound known | the tightest of the LP, a Lagrangian bound, a stopped MIP search |
| gap | $`(\text{bound} - \text{plan}) / \text{plan}`$; an upper estimate of the true loss |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the `node_limit` and gap settings used for the stopped searches, and changing variable bounds between solves); [The CP-SAT Primer (Krupke), Large Neighborhood Search](https://d-krupke.github.io/cpsat-primer/lns.html) (the destroy-and-repair loop, why a problem-specific neighborhood can beat the solver's own, choosing neighborhoods that interact, and adapting their size); [LINDO Systems, *Optimization Modeling with LINGO*, Chapter 9: Multi-period Planning Problems](https://www.lindo.com/downloads/LINGO_text/Chapter9.pdf) (section 9.1, multi-period models used in a rolling or sliding format, and nervousness when plans change between runs; section 9.8, end effects and ways to soften them: truncation, end-of-horizon limits, salvage values).

## Challenges

1. Give the rolling horizon a salvage value: in each window, credit a project that starts in its
   last year with part of its NPV. Predict whether the window-3 plan improves.
2. Run LNS with neighborhoods of two years instead of three. Predict both the plan after eight steps
   and the nodes it took.
3. LINDO's text warns about *nervousness*: a plan that changes a lot between runs. Which of this
   lesson's heuristics changes the published plan least between two scenario meetings, and how
   would you measure that?
4. Use the LNS plan as a solution hint for the monolithic solve (lesson 11.2.1). Predict whether the
   proof needs fewer than 21,794 nodes.

## Design Note: A Heuristic Ships With Its Bound

Every function in this lesson returns a plan, and every line of output pairs it with a gap. A
heuristic plan alone invites the question "how good is it?", and the only honest answers are a
bound or "we do not know". Put the bound in the same report, from the same run, and say where it came
from; when the optimum becomes known later, the report can be checked against it, as this lesson's
last output did.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**rolling.py.** The rolling horizon: windows, fixing and keeping (*A Rolling Horizon Plans a Few Years at a Time*). It prints nothing.

**lns.py.** LNS around HiGHS, with neighborhoods by region and by years (*the two LNS sections*). It prints nothing.

**rolling_lns.py.** The bounds, the rolling horizon runs and the three LNS runs (*every section but the last proof*). *Try:* Add a window of 6 years keeping 3. Predict its gap to the best bound, and whether it beats the 200-node plan.

**medium_proof.py.** The monolithic MILP solved to a proven optimum (*LNS Polishes the Solver's Own Early Plan*). It runs for a while. *Try:* Set `relative_gap_tolerance` to 0.001. Predict whether the node count drops below 8,000.

- Library: [rolling.py](src/rolling.py)
- Library: [lns.py](src/lns.py)
- Program: [rolling_lns.py](src/rolling_lns.py)
- Program: [medium_proof.py](src/medium_proof.py)
