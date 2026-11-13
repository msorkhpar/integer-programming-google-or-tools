# 13.1.4 Diagnostics: Pre-Solve Checks, IIS Message, Why-Deferred Report

It is Budget Lock, the step of the planning cycle where finance fixes the numbers (lesson 7.1.3).
Finance locks the 2028 budget at $40,000k, and a contractor change leaves the transmission program
18 crew-months in each of 2029 and 2030, where GridCap's figures were 129 and 122. CIPT Lite runs the
scenario and HiGHS answers `INFEASIBLE`: there is no plan, and nothing in the result says why. The
planners need one message they can act on, and the asset team, looking at a plan that does exist,
needs to know why its favourite breaker replacement is not in it. This milestone builds both
answers from section 9: checks before the solve, a conflict found by a deletion filter and said in
the planners' words, and a why-deferred report. GridCap is a fictional utility's portfolio.

The scenario changes only data: the model is lesson 13.1.2's, with $`B_{2028} = 40{,}000`$ and
$`W_{\text{transmission},2029} = W_{\text{transmission},2030} = 18`$.

## Pre-Solve Checks Run First and Catch What One Limit Can Refuse

Most infeasible scenarios are one typo, and a typo deserves a one-line answer, not a search. Lesson
9.1.2's checks read one project, group or region against one limit, before any model is built. CIPT
Lite runs them on the **required** projects, the must-dos and every project a planner forced in or
fixed to a year (overrides count, lesson 6.5.6): each must have a start left; each must fit the
yearly budgets and its program's crews on its own in some start year; together, their least spend
in each year must fit that year's budget; no two may be alternatives; and each region's floor must
be reachable. The year check is the gate rule of lesson 13.1.1, now with the scenario's overrides
and locked numbers. That gate, `gate(pf)`, reads only the portfolio: it counts the export's must-dos
against the export's budgets, so it sees neither a scenario's overrides nor its locked numbers. The
year check reads the required projects and the scenario's limits:

```python
    for y in pf.years:
        least = sum(min(by_id[i].spend(t).get(y, 0) for t in ys) for i, ys in need.items())
        if least > limit[y]:
            found.append(Finding("required-over-budget", "error", str(y), f"${least:,}k required, ${limit[y]:,}k"))
```

Every check compares a least demand with a most supply, so it is sound: it never refuses a scenario
that has a plan. `budget_lock.py` also runs a second scenario, the same lock with the 2027 budget
typed as $428k instead of $42,810k:

```text
Scenario 'budget-lock-typo' has no plan.
Pre-solve checks failed:
  alone-over-budget: P392: no start fits the yearly budgets on its own
  required-over-budget: 2027: $2,310k required, $428k
```

Two lines and no solver: P392, a must-do that can only start in 2027, costs more than the whole
locked year, and the must-dos' 2027 spend alone is $2,310k. The real Budget Lock scenario passes
every check:

```text
solve: INFEASIBLE; pre-solve findings: 0
```

Passing the checks does not mean a plan exists (lesson 9.1.2): the clash is between several rules
at once, and finding it needs the solver.

<!-- practice 1 -->

## A Deletion Filter Names the Rules That Clash

An **irreducible infeasible subsystem** (IIS) is a set of rows that has no solution while every
proper subset of it has one (lesson 9.1.3). MathOpt's `compute_infeasible_subsystem` finds one with
Gurobi only (lesson 4.3.5), so CIPT Lite finds one by hand, with the **deletion filter**: switch a
candidate row off; if the model is still infeasible, the conflict does not need that row, so leave it
off; otherwise switch it back on. What survives is irreducible.

Two choices make it fast and its answer useful. The candidates are only the **limits**: must-do and
forced rows, and the budget, regional, crew and floor rows. The rows that describe the decisions
(once, alternatives, precedence) stay on, because "a project starts at most once" is not a number
anyone at Budget Lock can change. And the filter tries whole families first, then the rows inside
the families it kept (lesson 9.1.5):

```python
        for fam, names in families.items():
            _switch(b, names, False, saved)
            solves += 1
            if _feasible(b):
                _switch(b, names, True, saved)
                kept += names
        members = list(kept)
        for n in kept:
            _switch(b, [n], False, saved)
            solves += 1
            if _feasible(b):
                _switch(b, [n], True, saved)
            else:
                members.remove(n)
```

Switching a row off sets its bounds to $`\pm\infty`$, and the objective is cleared while the filter
runs, since each solve only asks whether any plan exists. On the Budget Lock scenario the budget,
regional and floor families can all go; the must and crew families cannot, so their 69 rows are
filtered one at a time: 5 family solves and 69 row solves, 74 in all. The run setting's gap plays
no part here, because with no objective each solve only has to find a plan or prove there is none.

## The Message States the Rules, the Arithmetic and One Checked Change

A row name is not a message. Lesson 9.1.6's rules for one: name rules and projects, never rows; say
who set each number; show the arithmetic; end with the change that ends the conflict, checked by a
solve. CIPT Lite's `message` does each in turn:

```text
Scenario 'budget-lock' has no plan.
Every pre-solve check passed: no project or limit is impossible on its own.
These 4 rules cannot all hold (74 solves to find them):
  1. Transmission crews have 18 crew-months in 2029 in this scenario (GridCap's figure: 129).
  2. Transmission crews have 18 crew-months in 2030 in this scenario (GridCap's figure: 122).
  3. P097 Valley breaker bay replace (A097) is must-do: it has to start in 2029.
  4. P370 Valley breaker bay replace (A370) is must-do: it has to start in 2029 or 2030.
Every way to start the required projects runs out:
  P097 in 2029, P370 in 2029: crews_transmission_2029 needs 19 crew-months, has 18.
  P097 in 2029, P370 in 2030: crews_transmission_2030 needs 19 crew-months, has 18.
Smallest change that gives the scenario a plan (checked by a solve): 19 transmission crew-months in 2029 instead of 18.
```

The conflict is small enough to read whole. P097 works two years, 2029 and 2030, with 8
crew-months in each; P370 needs 11 in the year it starts, and it can only start in one of those two
years; 8 + 11 = 19, one more than the 18 the contractor change left. The 2028 budget lock is not in
the conflict: whatever it costs, it is not why there is no plan.

The arithmetic lines are computed, not written: for every combination of start years the conflict
leaves the required projects, the program adds up their use of each limit in the conflict and
prints the first one that runs out. The proposed change is searched among the numbers the scenario
itself set (the locked crews and budgets), one step at a time, and each candidate is accepted only
when a full solve of the changed scenario finds a plan. A conflict can have several ways out: by the
same arithmetic, 19 crew-months in 2030 would end this conflict too, and so would relaxing a mandate, but a mandate is a regulator's
number, not finance's, so the message offers the change finance can make.

<!-- practice 2 -->

## Why Deferred: The Rows That Refuse It, and What Forcing It In Costs

With the base scenario there is a plan, and the asset team asks why P399, a Valley line rebuild worth
$3,506k, is not in it. Lesson 9.3.1 answers the first half with no solve: add the project to the
plan at each of its start years, and list the rows the result breaks. Lesson 9.3.2 answers the
second: force it in, solve again, and compare. `why_deferred_report.py` does both for the three
deferred projects with the highest NPV at their earliest start:

```text
base plan: 209 projects, NPV 219,054, bound 219,273
```

```text
P399 Valley 115 kV line rebuild (A399): NPV $3,506k at 2027, cost (2370, 3180)
  start 2027: refused by budget_2028, crews_transmission_2027, crews_transmission_2028
  start 2028: refused by budget_2028, budget_2029, crews_transmission_2028, crews_transmission_2029
  forcing it in costs between $272k and $709k of NPV
  what gives way: 27 changes, e.g. P020 dropped, P024 2033->2035, P047 dropped, P050 2033->2032
```

The cost is an interval, and the reason is the run setting. Both solves stop within 0.1% of their
bound, so neither value is known exactly: the base plan is worth between its plan value and its
bound, and so is the forced plan. Forcing a project in adds a row, so it can never raise the best
value, and `why_deferred` raises a low end below 0 to 0 (`max(0.0, ...)`). The cost of forcing
is at least the base plan's value less the forced bound, and at most the base bound less the forced
plan's value:

```python
    base_low, base_high = base.objective_value(), base.termination.objective_bounds.dual_bound
    forced_low, forced_high = forced.objective_value(), forced.termination.objective_bounds.dual_bound
```

For P399 that is between $272k and $709k: whatever the exact optimum, the plan is better without it.
The other two:

```text
P088 Valley breaker bay replace (A088): NPV $2,584k at 2033, cost (5520,)
  start 2033: refused by alt_G088, budget_2033
  start 2034: refused by alt_G088, budget_2034, crews_transmission_2034
  start 2035: refused by alt_G088, budget_2035, crews_transmission_2035
  forcing it in costs between $206k and $539k of NPV
```

P088 is the replacement in an alternative pair whose repair is in the plan, so every start is
refused by `alt_G088` before any budget is reached: the plan chose to repair A088 instead. P168's
interval is $36k to $430k, and an interval that starts this close to zero says the project is
nearly a tie with what replaced it. If the asset team must know whether it is a tie, both solves go
to a zero gap, at the price of lesson 13.1.2's 26,516 nodes each. The list of what gives way is long,
27 changes for one project, because a forced re-solve under a gap may return any plan within 0.1% of
its bound, not the base plan with the fewest edits; read it as one valid way to make room, not the
only one.

<!-- practice 3 -->

## Summary

- **Pre-solve checks run first and catch what one limit can refuse.** On the required projects,
  overrides included: a typed $428k budget is two lines and no solver. Passing them proves nothing.
- **A deletion filter names the rules that clash.** Limits only, decision rows kept on, families
  before rows: four rules in 74 feasibility solves.
- **The message states the rules, the arithmetic and one checked change.** Who set each number,
  every start-year combination and where it runs out, and the smallest change finance can make,
  confirmed by a solve: 19 crew-months.
- **Why deferred: the rows that refuse it, and what forcing it in costs.** Refusing rows from the
  data; the forcing cost as an interval, because both solves stop at the run setting's gap.

## Reference

| Step | Function | Lesson |
| --- | --- | --- |
| required projects | `required(pf, scenario)`: must-dos, forced, fixed | 6.5.1, 6.5.6 |
| pre-solve checks | `presolve_checks`: `no-start`, `alone-over-budget`, `alone-over-crews`, `required-over-budget`, `required-alternatives`, `floor-out-of-reach` | 9.1.2 |
| conflict | `conflict(built)`: deletion filter over `must`, `force`, `budget`, `region`, `crews`, `floor` | 9.1.3, 9.1.5 |
| message | `describe`, `arithmetic`, `repair`, `message` | 9.1.6 |
| why deferred | `why_deferred(built, base, pid)`: refusing rows, cost interval, what gives way | 9.3.1, 9.3.2 |

| Term | Meaning |
| --- | --- |
| IIS | rows with no solution, every proper subset of which has one |
| deletion filter | drop each candidate; keep it dropped if the rest stays infeasible |
| cost interval | [max(0, base plan − forced bound), base bound − forced plan] for a maximization |

**Further reading:** [OR-Tools: MathOpt](https://developers.google.com/optimization/math_opt) (infeasibility analysis is listed with Gurobi only, which is why the filter runs by hand); [HiGHS options](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`mip_rel_gap`, the gap that makes a forcing cost an interval).

## Challenges

1. Add a `force_in` of P384 to the Budget Lock scenario. Predict whether the conflict changes, and
   which pre-solve check you would expect to say something first.
2. The filter's answer depends on the order it tries rows. Put the crew rows last and the must
   rows first; which rows can then survive, and is it still the same conflict?
3. A planner reads "between $36k and $430k" for P168 and asks for one number. Write the reply, and
   the solve you would run to give it.

## Design Note: Diagnose What People Can Change

Every choice in this milestone points the answer at someone who can act: the filter only removes
limits, the message names who set each number, and the proposed change is to a number this
scenario set. A conflict made of once-rows and precedence rows would be true and useless at Budget
Lock. Choosing the candidate rows is choosing whom the diagnosis is for.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**budget_lock.py.** Solves the Budget Lock scenario, runs the checks, and prints the planner message
for it and for a scenario with a typed budget (*Pre-Solve Checks*, *A Deletion Filter*, *The
Message*). *Try:* Leave transmission crews at 18 in 2029 only. Predict whether the scenario has a
plan.

- Program: [budget_lock.py](src/budget_lock.py)

**why_deferred_report.py.** For GridCap medium's three best deferred projects: the refusing rows at
each start, the forcing cost interval, and what gives way (*Why Deferred*). *Try:* Pass `gap=0.0`
for P168 only. Predict where its cost falls inside the interval.

- Program: [why_deferred_report.py](src/why_deferred_report.py)

The milestone's library is `cipt_diagnose.py`.

- Library: [cipt_diagnose.py](src/cipt_diagnose.py)
