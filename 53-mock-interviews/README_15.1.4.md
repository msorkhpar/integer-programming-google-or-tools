# 15.1.4 Mock 4: Diagnostics, Sensitivity and Explanations

Planners do not ask "what is the optimum"; they ask "why did it fail?" and "why is my project not
in?". This round tests whether you can answer them with something better than a shrug: statuses you
can trust, conflicts you can name, prices you can qualify, and re-solves that give a decision its
cost. The interviewer's portfolio is fictional, like GridCap; the questions are the ones a planning
team asks every cycle.

| Part | Minutes |
| --- | --- |
| Round 1: when the model fails, three questions | 6 |
| Code practice: a deletion filter | 5 |
| Round 2: prices and reasons, three questions | 5 |
| Trap questions | 4 |
| Whiteboard and its code practice | 10 |

## Round 1: A Failed Scenario Gets a Status, a Conflict and a Repair

**Q1. The solver says `INFEASIBLE_OR_UNBOUNDED`. What do you do?**

<details>
<summary>Model answer</summary>

Read it as "the solver could not tell", not as "infeasible". `INFEASIBLE` means no plan exists;
`UNBOUNDED` means plans exist and improve forever, almost always a modeling bug (a missing bound or
a sign error). To settle it, solve a copy with a zero objective: a plan means the original was
unbounded, no plan means infeasible. Turning presolve off settled it for GLOP and for HiGHS, not for
every solver; Gurobi answers `INF_OR_UNBD` until `DualReductions=0`. To find what runs away, cap every
free variable at a large bound and see which ones reach it. And a limit that ends with no plan means
"unknown", never "infeasible".

*Follow-ups.* "Before the solve?" Validate the inputs: each check reads one project, group or region
against one limit and names the numbers. A check must never refuse a scenario that has a plan, and
passing every check does not prove a plan exists.

*Taught in:* lesson 9.1.1; lesson 9.1.2; lesson 2.2.3.

</details>

**Q2. What is an IIS, and how do you find one without Gurobi?**

<details>
<summary>Model answer</summary>

An irreducible infeasible subsystem is a set of rows (and bounds) that cannot hold together, where
dropping any one of them leaves a feasible set. It is one conflict: irreducible, but neither unique
nor the smallest, and a scenario can have several. A deletion filter finds one with any solver: drop
each row in turn and keep it out if the rest is still infeasible, one solve per row. Its order picks
which conflict survives: it keeps the conflict it tests last, so put the rows you want named last.
An additive filter builds a conflict up from nothing instead. To list every conflict, find one,
switch off one of its rows and look again. gurobipy's `computeIIS` also counts variable bounds as
members unless you force them in.

*Follow-ups.* "Pyomo has an IIS tool, doesn't it?" Its MIS tool works on the LP relaxation, so it
missed a conflict that only integrality causes and declared that scenario feasible; `write_iis` asks
Gurobi.

*Taught in:* lesson 9.1.3; lesson 4.3.5; lesson 5.1.4.

</details>

**Q3. The planners want a plan anyway. How do you tell them what to change?**

<details>
<summary>Model answer</summary>

Make the rows elastic: give each row that may bend a nonnegative variable, $`a^\top x - o \le u`$,
and minimize the bends at a price. The elastic model always has a plan, and the original is feasible
exactly when the least violation is 0. Price every bend in one currency: when every unit costs 1,
dollars, crews and projects mix, and the flat repair broke a board override because one project cost
the same as $1k. With prices in money, the course's repair was $40k more in 2028 plus seven
crew-months, and the best plan with that repair was worth $17,060k. Then write it for the planners:
the rules and projects by name (never row names), who set each number, the arithmetic of the closest
miss, and the changes that end each conflict, checked by a solve.

*Taught in:* lesson 9.1.4; lesson 9.1.6.

</details>

A conflict you report is only as good as the filter that produced it. The first code practice writes
the deletion filter against an oracle, so the order rule of Q2 is something you have seen happen.

<!-- practice 1 -->

## Round 2: A MILP Has No Prices, So Reasons Come From Re-Solves

**Q4. Finance asks for the shadow price of the 2029 budget in the capital plan. What do you say?**

<details>
<summary>Model answer</summary>

A MILP has no duals: the solver reports none (MathOpt's `has_dual_feasible_solution()` is `False`
and `dual_values` raises `ValueError`), because the value of the budget is a step function and a
price is a line that touches it from above, which a step function almost never has. The LP
relaxation has prices, but they price a plan nobody can fund. The fixed-integer re-solve (fix every
integer at its value, make it continuous, re-solve) prices only what stayed free, holds only with
that plan fixed and only inside its range, and in an all-binary model there is nothing free for the
budget to price. Tell finance the steps: where the next step in the budget-value curve is, how high,
and what a round amount buys.

*Follow-ups.* "How do you find the steps?" Two solves per step: the cheapest plan worth more, then
the best value at that cost; GridCap small has 1,090 steps.

*Taught in:* lesson 9.2.1; lesson 9.2.2; lesson 9.2.3; lesson 9.2.4.

</details>

**Q5. "Why was P24 not funded?"**

<details>
<summary>Model answer</summary>

Force the opposite and re-solve: $`\text{started}(i) = 1`$, and the cost of the decision is what the
best plan loses (GridCap's P024 costs $273k to force in; P032 costs $112k to lose, against its own
NPV of $3,678k). Then say why in the rules: the rows that refuse the project as the plan stands, the
projects that give way, then the cost. A forcing the rules cannot satisfy (a must-do forced out) is
answered by the conflicting rules, never a number. Small costs are near ties, not reasons, and a
cost of 0 would mean another optimum.

*Follow-ups.* "And between two scenarios?" A diff by project id in three lists (selected, deferred,
shifted), with the input diff and the money beside it, changing one input at a time so each change
can be charged to its cause.

*Taught in:* lesson 9.3.2; lesson 9.3.3.

</details>

**Q6. What goes into a binding-constraints report for a MILP?**

<details>
<summary>Model answer</summary>

For each row, its slack measured from the plan and the data, with no help from the solver, so it
works on any model; a row binds when the slack is zero. On a MILP, the rows that bind are often the
once, must and alternative rows, which record what was chosen. A row with slack can still be the row
that blocks, because whole projects cannot use the last few dollars, so list for each budget row the
single additions it refuses (on GridCap small the 2030 budget refused 15 of 25 starts). Prices, where
there are any, go in their own column. Different readers then get different reports from one record
of the run: projects and rules for planners, money by year and the gap for finance, inputs, settings
and checks for auditors.

*Taught in:* lesson 9.3.1; lesson 9.3.4.

</details>

## Trap Questions: Prices and Conflicts That Promise Too Much

**T1. "A constraint is binding when its slack is zero and its shadow price is nonzero." Right?**

<details>
<summary>What is wrong</summary>

Binding means zero slack. A binding row can have a zero price when the LP is degenerate, more rows
tight at the vertex than it needs. `diagnostic_traps.py` solves $`\max x + y`$ with $`x \le 1`$,
$`y \le 1`$ and $`x + y \le 2`$ with GLOP:

```text
degenerate LP: OPTIMAL, objective 2
  cap_x  slack 0  price 1
  cap_y  slack 0  price 1
  total  slack 0  price 0
```

All three rows bind; GLOP put the price on two of them. Lesson 9.2.2 saw `must_P003` bind with price
0, and lesson 9.3.1 found 11 binding GridCap rows at price 0 in the LP relaxation. Test slack and
price separately and report both.

*Taught in:* lesson 2.3.2; lesson 9.2.2; lesson 9.3.1.

</details>

**T2. "Fix the integers, re-solve, and the budget price of 1.25 means each extra $1,000 adds
$1,250." Fair?**

<details>
<summary>What is wrong</summary>

It is a local, conditional statement. The price holds only with the selection fixed and only inside
its range; inside, it is a floor on the MILP's gain, and outside it says nothing. The MILP's value of
the next dollar is a step function: with GridCap's costs in multiples of $10k, the next $1k buys
nothing at most budgets and a whole step at a few. In an all-binary model the fixed LP has nothing
continuous left for the budget to price:

```text
MILP: OPTIMAL, objective 110, plan {'P1': 1, 'P2': 1, 'P3': 0}
  has_dual_feasible_solution(): False
  dual_values(budget) raises ValueError: Best solution does not have an associated dual feasible solution.

fixed-integer LP: OPTIMAL, objective 110
  budget price 0; reduced costs P1 60, P2 50, P3 40
```

The budget row binds (cost 50 of 50) and its price is 0; the fixed bounds carry the prices instead,
and a fixed binary's reduced cost is its value against that, not a reason it was funded.

*Taught in:* lesson 9.2.2; lesson 9.2.4; lesson 5.3.2.

</details>

**T3. "Pyomo's dual suffix gives MILP duals, and its IIS tool explains any infeasible model." True?**

<details>
<summary>What is wrong</summary>

Neither. The dual suffix raises on a MILP; it does not run the fixed-integer re-solve for you. Fixing
the integers, relaxing integrality and re-solving is your job, after checking the plan. Pyomo's MIS
tool works on the LP relaxation, so a conflict that only integrality causes is invisible to it: it
declared GridCap's integer conflict feasible.

*Taught in:* lesson 9.2.2; lesson 9.1.3; lesson 5.1.2.

</details>

**T4. "The solve hit its time limit with no plan, so tell the planners the scenario is
infeasible." OK?**

<details>
<summary>What is wrong</summary>

A limit without a plan means "unknown". `NO_SOLUTION_FOUND` with a limit says the search stopped,
not that no plan exists; only `INFEASIBLE` is a proof. Report it as its own status (the course's
API returns `time_limit` with or without a plan, and `infeasible` only when proven).

*Taught in:* lesson 9.1.1; lesson 3.4.2; lesson 12.4.2.

</details>

## Whiteboard: The Cheapest Repair of an Over-Committed Scenario

"Our must-do projects no longer fit the yearly budgets. Finance will lend money in some years more
cheaply than in others. Find the cheapest overspend, year by year, that makes the plan possible, and
tell us what any given plan would cost in overspend."

<details>
<summary>Model formulation</summary>

**Sets.** $`P`$ the projects; $`Y`$ the years; $`M \subseteq P`$ the must-dos; $`P_y`$ the projects
that spend in year $`y`$.

**Parameters.** $`c_i`$, project $`i`$'s cost in its year ($k); $`B_y`$, the budget of year $`y`$
($k); $`\pi_y`$, the price of one $k of overspend in year $`y`$.

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$; $`o_y \ge 0`$ for every $`y \in Y`$, the
overspend allowed in year $`y`$ ($k).

**Objective.**

```math
\min \; \sum_{y \in Y} \pi_y\, o_y
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P_y} c_i\, x_i - o_y &\le B_y && \forall y \in Y && \text{(budget}_y) \\
x_i &= 1 && \forall i \in M && \text{(must}_i)
\end{aligned}
```

The must-do rows stay hard: the question is what the money must do, not which mandate to drop.
Follow-ups: "Why $`o_y \ge 0`$?" Without it an underspent year earns a credit that pays for another
year's overspend, which no lender offers. "And then the best plan?" Fix the least repair as a cap on
the overspend and maximize value in a second pass (lesson 9.1.4).

</details>

<!-- practice 2 -->

## Summary

- **Statuses.** `INFEASIBLE` is a proof; `INFEASIBLE_OR_UNBOUNDED` is settled by a zero-objective
  copy; a limit without a plan is unknown, never infeasible.
- **Conflicts.** An IIS is one conflict, irreducible but not unique; a deletion filter finds one with
  any solver and keeps the conflict it tests last. Pyomo's MIS tool sees only the LP relaxation.
- **Repairs.** Elastic rows priced in one currency give a repair planners can price.
- **Prices.** A MILP has no duals. A fixed-integer price holds only with the plan fixed and inside
  its range; the next dollar's value is a step function. Binding means zero slack, and a binding row
  can have a zero price.
- **Reasons.** Force a decision the other way and re-solve; report the rules, the projects that give
  way and the cost, and read small costs as near ties.

## Reference

| Question | Lessons |
| --- | --- |
| Q1, T4 statuses | 9.1.1; 9.1.2; 2.2.3; 3.4.2 |
| Q2, T3 conflicts | 9.1.3; 4.3.5; 5.1.4 |
| Q3 repairs and messages | 9.1.4; 9.1.6 |
| Q4, T2 prices | 9.2.1; 9.2.2; 9.2.3; 9.2.4; 5.3.2 |
| Q5, Q6, T1 reasons | 9.3.1; 9.3.2; 9.3.3; 9.3.4; 2.3.2 |
| Whiteboard | 9.1.4; the capstone's *Diagnostics: pre-solve checks, IIS message, why-deferred report*; project lesson *Why it failed, why it was deferred: a diagnostics layer* |

**Further reading:** [MathOpt `result.py` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (`has_dual_feasible_solution`, which is not promised even at `OPTIMAL`, and `dual_values`, which raises when the best solution has no dual solution); [MathOpt `solve.py` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py) (`compute_infeasible_subsystem` and the solvers its docstring says support it).

## Challenges

1. In `diagnostic_traps.py`, raise the budget to 60 and predict the MILP's plan and the fixed LP's
   budget price.
2. Extend the whiteboard with crews: a second elastic row per year priced per crew-month. How do you
   make $k and crew-months comparable?
3. A deletion filter needs one solve per row. How many solves does it need when the rows are grouped
   into seven families first (lesson 9.1.5)?

## Design Note: Say What a Number Is Conditional On

Every diagnostic number on this page holds under a condition: a price with the plan fixed and inside
a range, a forced-in cost against the current rules, a conflict for one filter order. Interviewers
probe exactly that condition. Say it before they ask.

## The Full Programs

**diagnostic_traps.py.** A degenerate LP where every row binds and one has a zero price, a three-project
MILP that has no duals, and its fixed-integer re-solve (*Trap Questions: Prices and Conflicts That
Promise Too Much*). *Try:* Change the third row to $`x + y \le 3`$ and predict each row's slack and
price.

- Program: [diagnostic_traps.py](src/diagnostic_traps.py)
