# 11.2.1 MIP Starts From Last Cycle's Plan

GridCap re-plans its capital portfolio every January. Last January the Ridge region's ten-year
plan was solved to optimality and approved. Now 2027 is over: the twelve projects the plan started
in 2027 are under way, finance has revised the budgets, the engineers have re-costed some
projects, and five new candidates have been added. The planners solve again, and the obvious
question is the one lesson 4.3.3 raised: can the solver start from last year's plan instead of
from nothing? Lesson 4.3.3 showed *how* to hand MathOpt a hint. This lesson is about *what* to hand
it and *whether it helps*: how last cycle's plan becomes a start for this cycle's model, why it
usually needs repair first, how each solver reports what it did with it, and how to measure the
effect without fooling yourself. GridCap is a fictional utility; its numbers are teaching data.

A **MIP start** (Gurobi's name; MathOpt calls it a solution hint, CP-SAT a hint) is a complete or
partial assignment of values to a model's integer variables, given to the solver before it begins.
If the solver accepts it as a feasible plan, that plan is its first **incumbent**, the best plan
found so far (lesson 3.3.3). A start never changes which plans are allowed or which one is optimal.

## The Model

The multi-period timing model of lesson 6.4.1, for one region. One region of a GridCap medium
portfolio, about 80 to 110 projects, is small enough to solve to optimality hundreds of times, which
is what a benchmark over many runs needs. `plan_model.region_portfolio` keeps one
region's projects (a child only if its parent is in the region) and scales each year's budget to
the region's share of the portfolio's spend, raised where needed so that every must-do project fits
at its earliest start.

**Sets.** $`P`$ the region's projects; $`Y`$ the plan's years, ten of them; $`T_i \subseteq Y`$ the
years project $`i`$ may start in; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the
alternative groups; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k); $`B_y`$, the region's
budget in year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The code names each row by its label: `once_P017`, `must_P002`, `alt_G006`, `after_P023_2030`,
`budget_2029`. The same rows are built three times in `plan_model.py` and `grb_runs.py`, for
MathOpt, CP-SAT and gurobipy, because the solvers below are reached through those three APIs.

**Without a Gurobi license.** The Gurobi lines and the Gurobi tables below come from
`start_logs.py` and `start_effect_gurobi.py`, and every gurobipy program needs a Gurobi license to
start (lesson 5.3.4 explains the kinds of license and how to give the runner yours). Without one,
you can read that output but not reproduce it. `start_logs.py` opens its Gurobi environment before
it prints anything, so without a license its HiGHS and SCIP lines do not appear either (lesson 5.3.4
shows the error such a program stops with). Everything else in the lesson runs without a license: `roll_forward.py` and
`start_effect.py` on HiGHS, `start_effect_scip.py` on SCIP, and all of the lesson's practices.

**This cycle's model** has the same rows over new data: $`Y`$ is the next ten years, $`P`$ loses
the projects already committed or whose windows have passed and gains new candidates, each $`T_i`$
loses the year that is over, and $`B_y`$ and some $`c_{i,k}`$ are revised. A **start** is a value
$`\hat x_{i,t} \in \{0, 1\}`$ for some or all of this cycle's variables. It is advice to the
solver, not a row: nothing above changes when a start is given.

## A Plan Rolls Forward One Year, and Its First Year Becomes Fixed

A multi-period model is normally used in a rolling format: solve it, carry out the first period's
decisions, and a period later slide the model forward one period with better data and solve again.
LINDO's text on multi-period planning (chapter 9) describes exactly this, and the risk that comes
with it: the new optimum can differ sharply from the last one, which the people carrying it out
find unsettling. `cycles.next_cycle` builds next year's model from this year's portfolio and the
approved plan:

```python
    first = pf.years[0]
    years = pf.years[1:] + (pf.years[-1] + 1,)
    committed = {i for i, t in plan.items() if t == first}
```

```python
    for i in committed:
        for y, amount in pf.project(i).spend(first).items():
            if y in budget:
                budget[y] -= amount
```

The projects the plan started in the year that is over are **committed**: they are being built,
so they are no longer decisions, and what they will still spend comes off the later budgets. The
horizon loses 2027 and gains 2037. Then the new data arrives, drawn from a seeded random generator
so that every run of the course sees the same next cycle: each budget revised by $-3\%$ to $+3\%$,
one project in eight re-costed 20% higher (its NPV drops by the extra cost), and five new
candidates. A project whose window has passed without a start drops out, and so does a child whose
parent can no longer start. A child of a committed parent keeps its lag as an earliest start year:

```python
        if parent in committed:                 # the parent started in `first`: the lag is now a date
            earliest, parent, lag = max(earliest, first + p.parent_lag), None, 0
```

For the Ridge region:

```text
Ridge-2027, cycle 2027-2036: approved plan NPV 50,538, 59 starts, 12 of them in 2027
next cycle 2028-2037: 12 projects committed, 1 dropped, 14 costs revised up 20%, 5 new projects
budgets  2028 2029 2030 2031 2032 ...
  before 7362 7137 7614 9044 12048    (last cycle's, less the committed spend)
  now    7280 6990 7680 8810 12070
model: 90 projects, 192 start variables
```

Two of the first five budgets went up and three went down, by a few percent. That is a quiet year.
It is still enough to make last year's plan illegal, as the next sections show.

## Last Cycle's Plan Must Be Mapped Onto This Cycle's Variables

A start is given per variable, and this cycle's variables are not last cycle's. A decision of the
old plan, "P031 starts in 2030", carries over only if this cycle's model still has the variable
$`x_{P031,2030}`$. Three things can happen to each old decision and each new variable:

- **kept**: the project is still a decision and its old start year is still in its window, so the
  start gives that variable 1;
- **no variable**: the project is committed (its start year is over) or dropped, so the old decision
  has nowhere to go;
- **new**: a project with no old decision. A complete start gives each of its variables 0, which
  means "not funded" until the solver finds otherwise.

```python
    allowed = {p.project_id: set(p.starts()) for p in pf.projects}
    carried = {i: t for i, t in old.items() if t in allowed.get(i, ())}
```

```text
carry forward: kept 47, no variable 12, new 5
```

Of the plan's 59 starts, 47 still have their variable, and the 12 without one are exactly the 12
committed projects. The new candidates are numbered `N001` to `N005` by `next_cycle`, which is how
`carry_forward` tells them apart. The carried plan is still a plan in the data sense, a dict from
project to year, and turning it into a **complete** start is one more line: 1 for each variable the
plan uses, 0 for every other variable of the model.

```python
def hint_values(keys, plan: dict[str, int]) -> dict:
    """1 for each (project, year) the plan starts, 0 for every other key: a complete start."""
    return {(i, t): 1.0 if plan.get(i) == t else 0.0 for i, t in keys}
```

Why complete? A **partial** start (values for only some variables, typically only the 1s) leaves
the solver to fill in the rest by solving a small MIP of its own, which lesson 4.3.3's HiGHS log
showed and which costs work. Gurobi's documentation says the same of its partial MIP starts: completing
them means solving subproblems, which can be expensive, and its `StartNodeLimit` parameter caps the
nodes spent on it. HiGHS has the same kind of cap, the option `mip_max_start_nodes` (500 nodes by
default, per its option list).

<!-- practice 1 -->

## Check the Start Against This Cycle's Rows Before Any Solver Sees It

Last year's plan was optimal for last year's data, which means it used nearly every dollar of every
budget. This year three of the first five budgets are lower and fourteen projects cost more. Before
handing the carried plan to any solver, check it against this cycle's rows. `plan_model.broken`
evaluates a plan, as data, against every row of the model and returns the names of the rows it
breaks:

```python
    for y in pf.years:
        if sum(by_id[i].spend(t).get(y, 0) for i, t in plan.items()) > pf.budget[y]:
            out.append(f"budget_{y}")
```

```text
carried      NPV  40,005   47 starts  breaks budget_2028, budget_2029, budget_2030, budget_2031, budget_2033, budget_2034, budget_2035, budget_2036
repaired     NPV  36,251   39 starts  breaks nothing
filled       NPV  37,809   55 starts  breaks nothing
greedy       NPV  33,512   58 starts  breaks nothing
optimum      NPV  40,136   47 starts  breaks nothing
```

The carried plan breaks eight of the ten budget rows. It is not a plan of this cycle's model, and
its NPV, 40,005, means nothing. Two steps turn it into one:

1. **Repair**: while a budget row is broken, drop the optional project with the least NPV per $k
   among those spending in a broken year, and its children with it. Must-do projects are never
   dropped. Eight projects go, and the plan fits: 36,251.
2. **Fill**: the repair freed money, and new candidates have none of it yet. Add the projects the
   plan leaves out, best NPV per $k first, each at its earliest start year that keeps every row
   (the greedy fill of lesson 3.3.3, now over start years). Sixteen projects come in: 37,809.

```python
    while rows := broken(pf, plan):
        years = {int(r.split("_")[1]) for r in rows if r.startswith("budget_")}
        optional = [i for i in plan if not by_id[i].must_do
                    and any(by_id[i].spend(plan[i]).get(y, 0) for y in years)]
        if not optional:
            break
        drop = min(optional, key=lambda i: (by_id[i].npv[plan[i]] / max(by_id[i].capex, 1), i))
        for i in [drop] + [c.project_id for c in pf.projects if c.parent == drop]:
            plan.pop(i, None)
```

The **greedy** row is the same fill run from nothing but the must-do projects: a start that needs no
last cycle at all. It is worth 33,512, 16.5% below this cycle's optimum of 40,136; the repaired and
filled plan is 5.8% below. Over all eight regions, rolled forward the same way:

```text
cycle        rows the carried plan breaks  filled gap  greedy gap
Ridge-2027                              8       5.80%      16.50%
Valley-2027                             7       3.55%       4.80%
Coast-2027                              9       4.63%      15.96%
Plains-2027                             4       3.79%       6.28%
Ridge-1                                 6       6.69%       9.46%
Valley-1                                7       3.14%      11.26%
Coast-1                                 6       3.38%       1.18%
Plains-1                                7       2.72%       4.32%
```

Every carried plan breaks between four and nine budget rows. The repaired and filled plan is within
2.7% to 6.7% of the optimum, and it beats the greedy plan on seven of the eight cycles; on Coast-1
the greedy plan is closer. (Names ending in `-2027` and `-1` are the medium portfolios drawn with
seeds 2027 and 1.) So the rule: **a plan carried from last cycle is a draft, never a start. Check
it against this cycle's rows, repair it, and fill it before any solver sees it.** The next section
shows what happens when you skip that.

<!-- practice 2 -->

## Each Solver Says in Its Own Words Whether It Took the Start

`start_logs.py` hands four starts to HiGHS and SCIP through MathOpt (lesson 4.3.3's
`ModelSolveParameters(solution_hints=[...])`) and to Gurobi through its own API, where a MIP start
is the `Start` attribute of each variable:

```python
    for k, v in (start or {}).items():
        if k in x:
            x[k].Start = v
```

and keeps only the log lines about the start. The four starts are the carried plan and the
repaired-and-filled plan, each given complete (every variable, zeros included) and as its 1s only:

```text
carried, complete: 47 starts given, 192 of 192 variables
  HiGHS   ['User-supplied values of discrete variables cannot yield feasible solution']
  SCIP    nothing about it
  Gurobi  ['User MIP start did not produce a new incumbent solution', 'User MIP start violates constraint budget_2028 by 120.000000000', 'Another try with MIP start']
carried, ones only: 47 starts given, 47 of 192 variables
  HiGHS   ['Attempting to find feasible solution by solving MIP for user-supplied values of 47 / 192 discrete variables']
  SCIP    nothing about it
  Gurobi  ['User MIP start did not produce a new incumbent solution', 'User MIP start violates constraint budget_2028 by 120.000000000']
repaired, complete: 55 starts given, 192 of 192 variables
  HiGHS   ['MIP start solution is feasible, objective value is 37809']
  SCIP    ['1/1 feasible solution given by solution candidate storage, new primal bound 3.780900e+04']
  Gurobi  ['Loaded user MIP start with objective 37809']
repaired, ones only: 55 starts given, 55 of 192 variables
  HiGHS   ['Attempting to find feasible solution by solving MIP for user-supplied values of 55 / 192 discrete variables', 'MIP start solution is feasible, objective value is 37809']
  SCIP    nothing about it
  Gurobi  ['User MIP start produced solution with objective 37809 (<t>s)', 'Loaded user MIP start with objective 37809']
```

(`<t>` masks a time, which changes on every run.) Read it start by start:

- **The carried plan, complete.** HiGHS rejects it in one line. Gurobi names the first row it breaks
  (`budget_2028`, overspent by $120k), tries once more to repair it, and gives up. SCIP says nothing:
  its log does not show the start at all. None of the three gets a plan out of it, and for HiGHS and
  SCIP the program checks that the whole run was the one they make with no start at all:

```text
HiGHS with the carried start, seed 1: the same run as with no start: True
SCIP with the carried start, seed 1: the same run as with no start: True
```

- **The carried plan, 1s only.** HiGHS and Gurobi both try to complete it and fail: fixing 47 starts
  that already overspend 2028 leaves nothing feasible to complete. Leaving out the zeros does not
  make an infeasible start feasible.
- **The repaired plan, complete.** All three accept it as their first incumbent, worth 37,809. This
  is the only case where every solver's log confirms the start.
- **The repaired plan, 1s only.** HiGHS and Gurobi complete it (HiGHS solves a MIP over the 137
  variables left free) into the same plan. SCIP's log is silent again.

Gurobi's documentation lists these messages: "Loaded user MIP start" for a start accepted as it is,
"User MIP start produced solution" for one it repaired or completed, and "did not produce a new
incumbent" for one it discarded. It also separates the MIP start from a **variable hint**
(`VarHintVal`, with a confidence `VarHintPri`): a start asks the solver to build one feasible plan
from the values, while hints steer heuristics and branching through the whole solve and need not be
feasible. MathOpt's `SolutionHint` and CP-SAT's `add_hint` are, despite the name, starts in this
sense; lesson 4.6.2 showed CP-SAT trying to repair an infeasible one.

The rule: **only the log, read with and without the start, tells you whether a solver used it** (the
MathOpt `SolutionHint` docstring says so too). A silent log, as SCIP's is for three of the four,
means you do not know.

## A Start Is Measured by the Work to a Good Plan, Over Seeds and Cycles

Does an accepted start make the solve faster? "It found the optimum, and the start was in the log"
proves nothing; lesson 5.4.2 showed that one run, or one seed, can show a speed-up that is not there.
So the measurement follows lesson 5.4.2's rules:

- **A fixed instance set, chosen first**: the eight next-cycle models above.
- **Several seeds**: 1, 2 and 3, each (cycle, seed) one paired observation, 24 in all.
- **Deterministic work, not seconds**: HiGHS and SCIP count LP iterations; Gurobi counts work units
  (its documentation: very roughly a second, depending on the machine and the model), read here in
  thousandths. Every run uses one thread.
- **Ratios of shifted geometric means**, with the count of observations where the start needed less
  and more work (W/L).

And one thing lesson 5.4.2 did not need: the work at which each plan was found. A MIP solver reports
every new incumbent as it finds it; `runs.py` records each as a pair (work, NPV). SCIP calls a MathOpt
callback on `Event.MIP_SOLUTION`, whose `mip_stats` carry the LP iterations so far. (The `callback.py`
docstring lists Gurobi and CP-SAT for this event; SCIP calls it too here, and prints two `ERROR`
lines on standard error when a callback is registered, while solving normally.) HiGHS
ignores MathOpt callbacks (lesson 4.3.5), so its plans are read from its log's progress table, where
each row that shows a better `BestSol` is a new plan at `LpIters`. Gurobi's callback reads
`GRB.Callback.WORK` at each `MIPSOL`.

```python
    def on_solution(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        found = sum(npv[v] * value for v, value in data.solution.items())    # the new plan's NPV
        if not events or found > events[-1][1] + 1e-6:
            events.append((float(data.mip_stats.simplex_iterations), found))
        return mathopt.CallbackResult()
```

From the events, three measures. The **time to first incumbent** is the work at the first event,
and "its gap" is how far that plan is below the cycle's optimum. The **work to 1%** is the work at
the first plan within 1% of the optimum. The **work to proof** is the whole run's work, with the gap
tolerance at 0:

```python
    def within(self, best: float, share: float) -> float:
        """Work until a plan within `share` of `best` (a maximization) was found."""
        for work, objective in self.events:
            if objective >= best - share * abs(best):
                return work
        return math.inf
```

```text
HiGHS
start     to first plan  its gap   to 1%  vs none    W/L  to proof  vs none    W/L
none                  0    80.2%     601     1.00  0/0      15,644     1.00  0/0
repaired              0     4.2%     584     0.97  9/11     15,625     1.00 14/10
greedy                0     8.7%     537     0.89  7/5      15,282     0.98  8/8
(24 paired observations: 8 cycles x 3 seeds; work in LP iterations;
 shifted geometric means, shift 100; W/L: runs with less/more work than with no start)
```

```text
SCIP
start     to first plan  its gap   to 1%  vs none    W/L  to proof  vs none    W/L
none                  0    24.1%     590     1.00  0/0       8,997     1.00  0/0
repaired              0     4.2%     715     1.21  8/12      7,959     0.88 18/6
```

```text
Gurobi
start     to first plan  its gap   to 1%  vs none    W/L  to proof  vs none    W/L
none                  0    29.4%       9     1.00  0/0         104     1.00  0/0
carried               0    29.4%       8     0.96 12/10         98     0.94 12/12
repaired              0     4.2%       7     0.84  9/13         98     0.95 11/10
greedy                0     8.7%       7     0.78 12/3         104     1.00 10/6
```

What the three tables say:

- **Every solver finds a first plan with almost no work, start or no start.** The time to first
  incumbent rounds to 0 in every row: before the first LP iteration, the solvers' own trivial
  heuristics have something. What the start changes is that first plan's quality: 4.2% below the
  optimum against 80.2% (HiGHS), 24.1% (SCIP) and 29.4% (Gurobi). Measured alone, "time to first
  incumbent" would call the start useless; measured with the plan's gap, it is the start's whole
  effect.
- **The work to a plan within 1% hardly moves, and can get worse.** HiGHS 0.97 with 9 wins and 11
  losses; SCIP 1.21, worse, losing 12 of 20; Gurobi 0.84 but losing 13 of 22. The solvers' own
  heuristics find plans within 1% within a few hundred LP iterations anyway, and a start changes
  the search's path, which can delay them.
- **The work to proof is about the same.** SCIP's 0.88 (18 wins, 6 losses) is the one consistent
  gain; HiGHS's 1.00 and Gurobi's 0.95 are noise-sized. Proving optimality means pushing the bound
  down to the optimum (lesson 3.4.1), and a start does nothing for the bound.
- **The carried, infeasible start changed Gurobi's path** (its rows differ from "none") without ever
  becoming a plan; HiGHS and SCIP dropped it, so it is not in their tables (`start_logs.py` shows
  why).

So the common advice is right that a good start gives the solver an incumbent at once,
and so a bound to prune with; on these models that did not translate into a faster proof, except a
12% saving for SCIP. Measure it on your own models before promising it.

<!-- practice 3 -->

## A Start Is Insurance for a Solve That Is Stopped Early

If the start barely speeds up the proof, why give one? Because real solves are stopped: by a time or
work limit, by a gap target, by the night ending. A stopped solve returns the best plan it has. The
second half of each program asks what that plan is worth after a fixed amount of work: the mean
gap, over the 24 observations, of the best plan found within that much work.

```text
mean gap of the best plan in hand, by work done (LP iterations):
start             0        50       200      1000
none         46.89%    24.43%    15.10%     0.55%
repaired      4.18%     4.18%     4.18%     0.46%
greedy        7.75%     6.94%     6.76%     0.51%
repaired start, seed 1, solved again: every run repeated: True
```

```text
mean gap of the best plan in hand, by work done (LP iterations):
start             0        50       200      1000
none         22.64%    15.24%     3.28%     0.35%
repaired      4.21%     4.21%     3.40%     0.50%
repaired start, seed 1, solved again: every run repeated: True
```

```text
mean gap of the best plan in hand, by work done (thousandths of a work unit):
start             0         1         5        20
none        no plan    29.30%     1.19%     0.46%
carried     no plan    29.30%     1.34%     0.45%
repaired      4.21%     4.17%     1.50%     0.38%
greedy        8.72%     8.68%     1.09%     0.41%
repaired start, seed 1, solved again: every run repeated: True
```

The tables are HiGHS, SCIP and Gurobi, in that order. At zero work the plan in hand can be better
than the first plan of the tables above, because a solver may find several plans before its first
LP iteration and keeps the best. Stopped after 50 LP iterations, HiGHS without
a start hands back a plan 24% below the optimum on average; with the repaired start, 4.2%. Gurobi
stopped at zero work has no plan at all without a start. By 1,000 LP iterations (or 20 thousandths
of a Gurobi work unit) every row is within about half a percent, and the start's advantage is gone;
SCIP's and Gurobi's repaired rows are even slightly behind there. The last line of each program
solves the eight repaired-start runs of seed 1 again and checks that every number repeated, so
these tables can be quoted.

That is what a start buys: **a floor under the plan a stopped solve returns, at no cost to the
answer of a solve that finishes.** It is worth most when solves are stopped early, which is the normal case for large models such as
the 10,000-project portfolio of lesson 11.1.3, and inside the heuristics of lesson 11.3.5. And because the greedy plan, which needs no last cycle, gives most of the same
floor, a new model with no history can still start from something.

## Summary

- **A plan rolls forward one year, and its first year becomes fixed.** Committed projects leave the
  decisions and their remaining spend leaves the budgets; the horizon slides one year.
- **Last cycle's plan must be mapped onto this cycle's variables.** Keep a decision where its
  variable still exists, drop it where it does not, give new projects 0, and hand over a complete
  start.
- **Check the start against this cycle's rows before any solver sees it.** Every carried plan broke
  four to nine budget rows; repaired and filled, it came within 2.7% to 6.7% of the optimum.
- **Each solver says in its own words whether it took the start.** HiGHS, SCIP and Gurobi all
  logged the repaired complete start; the carried one was rejected or silently dropped; SCIP's log
  was silent on three of the four starts.
- **A start is measured by the work to a good plan, over seeds and cycles.** On 24 paired runs the
  start cut the first plan's gap from 24% to 80% down to 4.2%, barely changed the work to 1%, and
  saved 12% of the proof only for SCIP.
- **A start is insurance for a solve that is stopped early.** After 50 HiGHS LP iterations the plan
  in hand was 4.2% from optimal with the start and 24% without; by 1,000 the difference was gone.

## Reference

| Solver | How to give a start | Partial start completed by | Log line when accepted |
| --- | --- | --- | --- |
| HiGHS (MathOpt) | `ModelSolveParameters(solution_hints=[SolutionHint(variable_values=...)])` | a sub-MIP, at most `mip_max_start_nodes` nodes | `MIP start solution is feasible, objective value is ...` |
| SCIP (MathOpt) | the same | (nothing in the log) | `... feasible solution given by solution candidate storage ...` |
| Gurobi | `var.Start = value`; several starts with `NumStart` and `StartNumber` | sub-MIP, at most `StartNodeLimit` nodes | `Loaded user MIP start with objective ...` |
| CP-SAT | `model.add_hint(var, value)` (lesson 4.6.2) | its own search (lesson 4.6.2) | `The solution hint is complete and is feasible.` |

| Measure | From the run's events $`(w_k, z_k)`$ | Answers |
| --- | --- | --- |
| time to first incumbent | $`w_1`$, with the gap of $`z_1`$ | how soon some plan exists, and how good it is |
| work to within 1% | first $`w_k`$ with $`z_k \ge z^* - 0.01\,\lvert z^*\rvert`$ | how soon a plan good enough to show exists |
| work to proof | the run's total work at gap 0 | how long the whole solve takes |
| plan in hand after $`W`$ | best $`z_k`$ with $`w_k \le W`$ | what a solve stopped at $`W`$ returns |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (warm
starts by solution or by basis among MathOpt's features); the `SolutionHint` and
`ModelSolveParameters` docstrings in
[`model_parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py)
(partial and infeasible hints completed by a sub-MIP, the first hint used by a solver that takes
one, and reading the log with and without the hint); the `Event.MIP_SOLUTION` and `CallbackData`
docstrings in
[`callback.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/callback.py)
(an event per new incumbent, `mip_stats` filled on it); Gurobi,
[Warm Start Options](https://docs.gurobi.com/projects/optimizer/en/13.0/features/warmstart.html)
(the `Start` attribute, partial and infeasible starts, `StartNodeLimit`, `NumStart` and
`StartNumber`, variable hints against MIP starts, and the log messages above); HiGHS,
[option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/)
(`mip_max_start_nodes`, the node limit for completing a partial start);
[LINDO, Multi-period Planning Problems, chapter 9](https://www.lindo.com/downloads/LINGO_text/Chapter9.pdf)
(section 9.1: multi-period models used in a rolling format, and the "nervousness" of plans that
change sharply between periods).

## Challenges

1. Raise the budget revision in `next_cycle` to $`\pm 10\%`$. Predict whether the carried plan
   breaks more rows, and whether the repaired start's gap grows.
2. Hand Gurobi two starts, the carried plan as start 0 and the repaired plan as start 1
   (`NumStart = 2`, then `StartNumber` before each set of `Start` values). Predict which log lines
   appear.
3. A planner wants this year's plan to change as little as possible from last year's. Is a start
   the tool for that? (Look at what a start promises about the final plan.)
4. Stop every solve at 200 LP iterations instead of running to proof. Which column of the tables
   would you report to the planners, and why?

## Design Note: A Start Is Data You Can Test

`start_effect.py` never hands a solver a start it has not first checked with `broken`, and
`starts.py` works only on plans as dicts. That keeps the expensive question ("does it help?")
separate from the cheap one ("is it a plan?"). The cheap one runs in microseconds, needs no solver,
and catches the mistake that cost every carried start here its value. Write the repair and the check
as plain functions with tests, as the practices do, and the solver only ever sees starts that are
plans.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. The Gurobi programs need a Gurobi license (lesson
5.3.4); the free size-limited one is enough.

**roll_forward.py.** Rolls the Ridge region's approved plan forward one cycle, carries it into the
new model, checks, repairs and fills it, and compares it with a greedy plan and the optimum on all
eight regions (*A Plan Rolls Forward*, *Last Cycle's Plan Must Be Mapped*, *Check the Start*).
*Try:* Change the seed of `next_cycle` from 7 to 8 and predict whether the carried plan still breaks
most budget rows.

**start_logs.py.** Four starts, each handed to HiGHS, SCIP and Gurobi, with the log lines about the
start (*Each Solver Says in Its Own Words*). *Try:* Give only the starts in 2028 and predict HiGHS's
"k / n" numbers.

**start_effect.py, start_effect_scip.py, start_effect_gurobi.py.** Every cycle, seed and kind of
start, compared pairwise with no start, then the plan in hand after fixed amounts of work (*A Start
Is Measured*, *A Start Is Insurance*). *Try:* Add 0.5% to the measures by changing `within(..., 0.01)`
to `0.005` in `start_bench.py`, and predict whether the start helps more at the tighter target.

- Program: [roll_forward.py](src/roll_forward.py)
- Program: [start_logs.py](src/start_logs.py)
- Program: [start_effect.py](src/start_effect.py)
- Program: [start_effect_scip.py](src/start_effect_scip.py)
- Program: [start_effect_gurobi.py](src/start_effect_gurobi.py)
- Library: [plan_model.py](src/plan_model.py)
- Library: [cycles.py](src/cycles.py)
- Library: [starts.py](src/starts.py)
- Library: [runs.py](src/runs.py)
- Library: [grb_runs.py](src/grb_runs.py)
- Library: [start_bench.py](src/start_bench.py)
- Library: [quiet.py](src/quiet.py)
