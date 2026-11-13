# 4.4.3 Objectives, Integer Scaling and Solution Callbacks

Two requests reach GridCap's planning team in the same week. The asset-health group wants a plan that
avoids the most expected equipment failures over the next five years, and its numbers are
probabilities such as 0.1701 and 0.0493, not whole $k. The steering committee wants something else:
it scores each project in points of $500k of NPV, rounded, because it does not trust NPV estimates to
better than that, and it asks for *every* plan with the best score so it can choose among them itself.

Both requests run into CP-SAT's integer world. Fractional data has to become whole numbers without
changing the answer, and "every best plan" needs a way to watch the solver's solutions as it finds
them. This lesson covers the objective, the scaling, and the **solution callback**, a piece of your
code that the solver calls each time it finds a solution.

GridCap is a fictional utility's portfolio, generated for this course; the failure probabilities come
from its invented asset data, and the scoring rule is invented for the lesson.

## The Model

Both requests use lesson 4.4.2's model (the selection with crew rows and native logic for the parent
and alternative rules) with the credit line closed, $`k = 0`$, and a new objective.

**New parameters.** $`q_i \in [0, 1]`$, the probability that the asset project $`i`$ works on fails in
the next five years, given that it is working now, from its Weibull curve (lesson 1.1.2):
$`q_i = \dfrac{F(a_i + 5) - F(a_i)}{1 - F(a_i)}`$ with $`F`$ the curve and $`a_i`$ the asset's age.
$`s_i = \operatorname{round}(v_i / 500)`$, the committee's score of project $`i`$, in points.

**Objective of the asset-health model** (the expected number of failures the plan avoids, if a funded
project removes its asset's risk):

```math
\max \; \sum_{i \in P} q_i\, x_i
```

**Objective of the committee's model:**

```math
\max \; \sum_{i \in P} s_i\, x_i
```

**Constraints.** Those of lesson 4.4.2 (budget, crews$`_g`$, must$`_i`$, parent$`_c`$, alt$`_a`$),
and

```math
k = 0 \qquad \text{(no borrowing)}
```

The second step of the committee's question adds one more row once the best score $`S^*`$ is known:

```math
\sum_{i \in P} s_i\, x_i = S^* \qquad \text{(at\_best)}
```

## One Linear Objective, and OPTIMAL Means Within the Gap Limit

A CP-SAT model has at most one objective, set with `model.maximize(expr)` or `model.minimize(expr)`,
where `expr` is a linear expression. A second call replaces the first; `model.clear_objective()`
removes it, and `model.has_objective()` says whether there is one. After a solve,
`solver.objective_value` is the plan's value and `solver.best_objective_bound` the best value no plan
can beat: for a maximization, an upper bound, as in lesson 3.4.1.

How close the two must be before CP-SAT stops is a parameter, `relative_gap_limit` (default 0) or
`absolute_gap_limit` (default $`10^{-4}`$, so for a whole-number objective, an exact proof). The gap
is

```math
\text{gap} = \frac{|O - B|}{\max(1, |O|)}
```

for objective $`O`$ and bound $`B`$. Lesson 4.4.1's model on GridCap medium, solved with three gap
limits (`one_worker()`, from lesson 4.4.1, is a `CpSolver` with
`solver.parameters.num_workers = 1`, so each run repeats):

```python
for gap in (0.0, 0.001, 0.01):
    solver = one_worker()
    solver.parameters.relative_gap_limit = gap
    status = solver.solve(sel.model)
    objective, bound = solver.objective_value, solver.best_objective_bound
```

```text
has objective: True
relative_gap_limit 0.0    OPTIMAL  objective 229,745  bound 229,745  gap 0.000%
relative_gap_limit 0.001  OPTIMAL  objective 229,726  bound 229,927  gap 0.087%
relative_gap_limit 0.01   OPTIMAL  objective 228,765  bound 230,577  gap 0.792%
after minimize(): OPTIMAL  objective 39  (must-do projects: 39)
```

With a gap limit of 1%, CP-SAT stops at a plan $980k below the true optimum and still says `OPTIMAL`.
The status means "optimal within the gap limit you set", the same convention lesson 3.4.3 described
for MILP solvers. A program that sets a gap limit compares `objective_value` with
`best_objective_bound` to know how far from proven it is.

The last line replaces the objective with `minimize(sum of x)`, the fewest projects that keep every
rule. The answer, 39, is the number of must-do projects on GridCap medium: the rules force those and
nothing else.

## Scale a Row Exactly, With a Whole-Number Multiplier

Lesson 4.4.1 showed that `model.add` refuses a fractional coefficient. The fix is the one the OR-Tools
guide *Solving an Optimization Problem* uses: multiply the whole row by a number that clears the
fractions. Its first constraint is $`x + 3.5y + 1.5z \le 25`$; times 2, it is
$`2x + 7y + 3z \le 50`$, which allows exactly the same whole-number points. The example, adapted:

```python
model.add(2 * x + 7 * y + 3 * z <= 50)          # x + 3.5 y + 1.5 z <= 25, times 2
model.add(3 * x - 5 * y + 7 * z <= 45)
model.add(5 * x + 2 * y - 6 * z <= 37)
model.maximize(2 * x + 2 * y + 3 * z)
```

```text
OPTIMAL: objective 35, x = 7, y = 3, z = 5
```

For any row with decimal data the multiplier is the **least common multiple** (LCM) of the
coefficients' denominators: write each coefficient as a fraction in lowest terms ($`1.5 = 3/2`$,
$`0.75 = 3/4`$), and take the smallest number every denominator divides. Multiplying by it makes every
coefficient whole. The right-hand side may still be fractional, and then there is one more step,
which is safe because the left side is now a whole number for every plan: a whole number is at most
$`30.4`$ exactly when it is at most $`30`$, so a $`\le`$ row rounds its bound **down**, and a $`\ge`$
row rounds it **up**.

```python
def scale_row(coefficients: list[str], rhs: str) -> tuple[int, list[int], int]:
    """sum c_j x_j <= rhs with decimal data -> (multiplier, whole coefficients, whole rhs), same 0/1 plans."""
    exact = [Fraction(c) for c in coefficients]
    multiplier = math.lcm(*(f.denominator for f in exact))
    whole = [int(f * multiplier) for f in exact]
    return multiplier, whole, math.floor(Fraction(rhs) * multiplier)  # whole left side: round the bound down
```

`Fraction("0.75")` reads the decimal text exactly as $`3/4`$. (Reading the float `0.75` would work
here too, but a float such as `0.1` is not exactly one tenth, and `Fraction(0.1)` has a denominator of
$`2^{55}`$; start from the text, or from data already in whole units.) A crew row on five yes/no jobs:

```text
row  1.5 x0 + 2.5 x1 + 0.75 x2 + 3.5 x3 + 2.5 x4 <= 7.6
x4  6 x0 + 10 x1 + 3 x2 + 14 x3 + 10 x4 <= 30
same 0/1 plans: True
rounded coefficients ['2', '2', '1', '4', '2']: same 0/1 plans: False
```

The denominators are 2, 2, 4, 2 and 2, so the multiplier is 4, and $`7.6 \times 4 = 30.4`$ rounds down
to 30. The program checks all 32 plans: the scaled row allows exactly the plans the original does.
Rounding each coefficient instead (Python's `round` sends 2.5 to 2, to the even neighbour) gives a
different row that allows different plans, and a model built on it answers a different question.

<!-- practice 1 -->

## Scale an Objective Enough to Keep Its Order

An objective is more forgiving than a row, and CP-SAT treats it differently. `model.maximize` accepts
float coefficients: `cp_model.proto` says the solver scales such a **floating-point objective** to
integers itself before it searches. A row has to be exact, because a plan either keeps it or does
not; an objective only has to rank the plans in the right order. The asset-health model shows both
ways, and what too little scaling does:

```python
for scale in (None, 1, 10, 100, 1000):
    sel = selection(small, native=True)
    sel.model.add(sel.k == 0)                                 # no borrowing in this comparison
    if scale is None:
        sel.model.maximize(sum(avoided[i] * v for i, v in sel.x.items()))
    else:
        sel.model.maximize(sum(round(scale * avoided[i]) * v for i, v in sel.x.items()))
```

```text
five-year failure probabilities: P001 0.1701, P002 0.1701, P003 0.0493, P004 0.2789 ...
HiGHS, float objective: 6.3036 failures avoided
CP-SAT floats as given  OPTIMAL  objective     6.3036  true value 6.3036  short by 0.0000
CP-SAT x1, rounded      OPTIMAL  objective     1.0000  true value 1.2351  short by 5.0684
CP-SAT x10, rounded     OPTIMAL  objective    64.0000  true value 6.2451  short by 0.0585
CP-SAT x100, rounded    OPTIMAL  objective   632.0000  true value 6.3036  short by 0.0000
CP-SAT x1000, rounded   OPTIMAL  objective 6,303.0000  true value 6.3036  short by 0.0000
```

- **Floats as given.** CP-SAT finds the plan HiGHS finds, 6.3036 expected failures avoided.
- **Times 1, rounded.** Every probability below 0.5 rounds to 0, so the objective cares about one
  project only and ignores the rest. The solver proves an optimum of the rounded model (status
  `OPTIMAL`), and that plan avoids 1.2351 failures, five fewer than the best. The status is about the
  model it was given; the model was wrong.
- **Times 10.** Each probability keeps one decimal. The plan is close, 0.0585 failures short.
- **Times 100 and 1000.** Two decimals already rank the plans as the floats do, on this data.

How much is enough depends on how close the plans' values are, so there is no universal factor. Two
checks work on any model: compute the true objective of the plan the scaled model returns (as the
program does) and compare it with a finer scaling, or with the float objective. The scale also has a
cost. Larger coefficients mean larger sums, and every sum must stay inside CP-SAT's 64-bit range
(lesson 4.4.1); the CP-SAT Primer also warns that finer resolution can make the solve much slower, so
use the coarsest scale that keeps the plan's true value, and test it.

## A Solution Callback Sees Every Improving Plan

When CP-SAT optimizes, it finds a first plan and then better and better ones until it proves the last
one best. A **solution callback** lets your code see each of them: subclass
`cp_model.CpSolverSolutionCallback`, write `on_solution_callback`, and pass an instance to
`solver.solve(model, callback)`. Inside it, `self.value(v)`, `self.boolean_value(v)`,
`self.objective_value` and `self.best_objective_bound` read the solution just found. The printer below
is adapted from the OR-Tools example that prints intermediate solutions; it records each solution's
objective, the bound at that moment and the number of projects:

```python
class ObjectivePrinter(cp_model.CpSolverSolutionCallback):
    """Record the objective and bound of each solution the search finds."""

    def __init__(self, x: dict):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.x = x
        self.seen = []

    def on_solution_callback(self) -> None:
        count = sum(self.boolean_value(v) for v in self.x.values())
        self.seen.append((self.objective_value, self.best_objective_bound, count))
```

```text
OPTIMAL: 21 improving solutions; the first five and the last:
  objective   228,285  bound   230,577  projects 215
  objective   228,765  bound   230,577  projects 213
  objective   229,538  bound   230,576  projects 214
  objective   229,573  bound   230,576  projects 208
  objective   229,600  bound   230,575  projects 209
  objective   229,745  bound   229,924  projects 212
second run, same sequence: True
```

On GridCap medium the search reports 21 solutions, each better than the last. The first is already
only about 1% below the bound; the last is the optimum, found while the bound was still $179k above it. The
proof came after the last solution, which is why the callback never sees the bound reach the
objective. The run uses one search worker, and the second run produced exactly the same sequence;
with several workers the solutions arrive in an order that can change from run to run (lesson 4.6.3).

The callback can also end the search. `self.stop_search()` asks the solver to stop; the solve then
returns the best plan so far, with status `FEASIBLE`:

```python
class StopWithinGap(cp_model.CpSolverSolutionCallback):
    """Stop the search at the first solution within `gap` of the bound (relative)."""

    def __init__(self, gap: float):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.gap = gap
        self.solution_count = 0

    def on_solution_callback(self) -> None:
        self.solution_count += 1
        if self.best_objective_bound - self.objective_value <= self.gap * abs(self.objective_value):
            self.stop_search()
```

```text
stopped within 0.5%: FEASIBLE after 3 solutions, objective 229,538, bound 230,576
```

Compare it with the gap limit of the first section: the parameter stops with `OPTIMAL`, the callback
with `FEASIBLE`. The callback is the tool when the stopping rule is your own (a target value, a
deadline from a business calendar, a plan that passes a check the model cannot state). Keep its work
small: the solver waits for your Python code at every solution, and the Primer notes that a slow
callback slows the solve.

<!-- practice 2 -->

## Every Optimal Plan: Optimize, Fix the Objective, Enumerate

`solver.parameters.enumerate_all_solutions = True` makes CP-SAT report *every* solution of a model to
the callback, not just improving ones. The OR-Tools guide's example lists all 18 assignments of
$`x, y, z \in \{0, 1, 2\}`$ with $`x \ne y`$ this way. The parameter's documentation in
`sat_parameters.proto` has two conditions that matter here:

- it enumerates the solutions of a problem **without an objective**;
- presolve can remove feasible solutions, so when this parameter is on and
  `keep_all_feasible_solutions_in_presolve` is unset, CP-SAT sets it to true for you.

So "every optimal plan" takes two solves. The first finds the best score $`S^*`$. The second adds the
row $`\sum_i s_i x_i = S^*`$ (at_best in the model), removes the objective, and enumerates; every
solution of that model is an optimal plan of the first. The collector is adapted from the OR-Tools
example `search_for_all_solutions_sample_sat.py`:

```python
class PlanCollector(cp_model.CpSolverSolutionCallback):
    """Keep the set of funded projects of every solution the solver reports."""

    def __init__(self, x: dict):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.x = x
        self.plans = []

    def on_solution_callback(self) -> None:
        self.plans.append(tuple(i for i, v in self.x.items() if self.boolean_value(v)))
```

```python
    solver = one_worker()                                      # solve 1: the best score
    if solver.solve(sel.model) != cp_model.OPTIMAL:
        raise RuntimeError("no proven optimum to enumerate at")
    best = round(solver.objective_value)

    sel.model.add(score == best)                               # solve 2: every plan with that score
    sel.model.clear_objective()
    collector = PlanCollector(sel.x)
    solver = one_worker()
    solver.parameters.enumerate_all_solutions = True
    status = solver.solve(sel.model, collector)
```

```text
enumeration OPTIMAL, 9 solutions reported
GridCap small: best score 52 points, 9 optimal plans; all share 13 projects
  + P002 P009 P015 P018 P023 P029 P035 NPV $24,757k  capex $38,280k
  + P002 P009 P018 P020 P023 P029 P035 NPV $24,724k  capex $38,360k
  + P002 P009 P018 P023 P029 P035  NPV $24,645k  capex $38,130k
  + P002 P009 P018 P029 P035 P038  NPV $25,000k  capex $38,360k
  + P002 P018 P023 P027 P029 P035  NPV $24,676k  capex $38,250k
  + P002 P018 P023 P029 P038       NPV $25,063k  capex $38,270k
  + P002 P018 P023 P035 P038       NPV $25,190k  capex $38,330k
  + P002 P023 P029 P035 P038       NPV $25,134k  capex $38,320k
  + P018 P023 P029 P035 P038       NPV $25,106k  capex $38,390k
GridCap tiny: 5 optimal plans; checking all 256 subsets finds 5, same: True
objective left on: OPTIMAL, 2 solutions reported
```

Nine plans score the best 52 points. They share 13 projects and differ in the rest, and their NPVs
range from $24,645k to $25,190k: the committee's rounding hides a $545k difference, which is exactly
the information it needs to choose. On GridCap tiny the program also checks the method against brute
force: of all $`2^8 = 256`$ subsets of the 8 projects, the ones that keep every rule and reach the best
score are the same 5 plans.

Three details make the method sound:

1. **Prove the optimum first.** If the first solve stops at `FEASIBLE`, $`S^*`$ may not be the best
   score, and the "optimal plans" are only the plans with that score. The program refuses to go on
   without `OPTIMAL` (and with a gap limit, `OPTIMAL` is not a proof; leave it at 0 here).
2. **Remove the objective.** The last line of the output is the same enumeration with the objective
   left on: the solver reported 2 solutions, the improving ones, and the 9 tied plans never appeared.
3. **Count plans, not solutions.** A solution assigns *every* variable. If the model has variables
   outside the plan (here the tranche count $`k`$, fixed at 0), two solutions can carry the same plan,
   so the program keeps the set of distinct plans. The parameter's documentation adds that with
   several workers the same solution may be reported more than once; one worker avoids that, and the
   set would absorb it anyway.

If the tied plans are too many to list, add a tie-break to the model instead, for example
"best score, then highest NPV" as a second solve with the score fixed (lesson 4.3.2 does this in
MathOpt), or stop the enumeration after a number of plans with `stop_search`.

<!-- practice 3 -->

## Summary

- **One linear objective, and OPTIMAL means within the gap limit.** `maximize` or `minimize` (a second
  call replaces the first); with `relative_gap_limit` set, `OPTIMAL` can stop short of the optimum.
- **Scale a row exactly, with a whole-number multiplier.** The LCM of the denominators, and the bound
  rounded down for $`\le`$ (up for $`\ge`$); rounding the coefficients changes the plans a row allows.
- **Scale an objective enough to keep its order.** CP-SAT accepts float objective coefficients; if you
  scale by hand, check the true value of the plan you get.
- **A solution callback sees every improving plan.** `on_solution_callback`, `self.value`,
  `self.objective_value`; `stop_search()` ends the search with `FEASIBLE`.
- **Every optimal plan: optimize, fix the objective, enumerate.** `enumerate_all_solutions` works on a
  model without an objective; collect distinct plans.

## Reference

| Call or parameter | What it does |
| --- | --- |
| `model.maximize(expr)`, `model.minimize(expr)` | set (or replace) the objective |
| `model.clear_objective()`, `model.has_objective()` | remove it; ask whether there is one |
| `solver.objective_value`, `solver.best_objective_bound` | the plan's value and the proven bound |
| `solver.parameters.relative_gap_limit` | stop when the relative gap, defined above, is below it (default 0) |
| `solver.parameters.absolute_gap_limit` | stop when the absolute gap, the distance from $`O`$ to $`B`$, is below it (default $`10^{-4}`$) |
| `class C(cp_model.CpSolverSolutionCallback)` with `on_solution_callback(self)` | your code at each solution |
| `self.value(v)`, `self.boolean_value(v)`, `self.objective_value`, `self.best_objective_bound` | read the solution just found |
| `self.stop_search()` | stop; the solve returns `FEASIBLE` with the best plan so far |
| `solver.solve(model, callback)` | solve, calling the callback |
| `solver.parameters.enumerate_all_solutions = True` | report every solution of a model with no objective |

| Data | Do |
| --- | --- |
| decimal coefficients in a row | multiply the row by the LCM of the denominators; round a $`\le`$ bound down, a $`\ge`$ bound up |
| float coefficients in the objective | pass them as they are, or scale by $`10^d`$ and check the plan's true value |
| money already in whole $k | nothing to do |

**Further reading:** [Solving an Optimization Problem (OR-Tools)](https://developers.google.com/optimization/cp/cp_example)
(the row multiplied by 2 to clear its fractions, adapted above); [Integer Optimization with CP-SAT (OR-Tools)](https://developers.google.com/optimization/cp/integer_opt_cp)
(the same example and why scaling the row does not change its solutions); [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver)
(the solution printer and `enumerate_all_solutions` on the $`x \ne y`$ model); [Setting Solver Limits (OR-Tools)](https://developers.google.com/optimization/cp/cp_tasks)
(a time limit, and a callback that stops after a number of solutions);
[The N-queens Problem (OR-Tools)](https://developers.google.com/optimization/cp/queens) and
[Cryptarithmetic (OR-Tools)](https://developers.google.com/optimization/cp/cryptarithmetic) (two
complete programs that enumerate every solution with a callback: 92 boards, 72 digit assignments);
[CP-SAT samples: `search_for_all_solutions_sample_sat.py` and `solve_and_print_intermediate_solutions_sample_sat.py` (OR-Tools on GitHub)](https://github.com/google/or-tools/tree/stable/ortools/sat/samples)
(the callbacks adapted above); [`sat_parameters.proto` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`enumerate_all_solutions` is for models without an objective and turns on
`keep_all_feasible_solutions_in_presolve`; the gap limits and their defaults);
[`cp_model.proto` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto)
(a floating-point objective is scaled to integers by the solver); [The CP-SAT Primer, Parameters (Krupke)](https://d-krupke.github.io/cpsat-primer/parameters.html)
(gap limits, solution callbacks, `stop_search` and the cost of a slow callback).

## Challenges

1. Score in points of $250k instead of $500k. Predict whether there are more or fewer optimal plans,
   then run it.
2. Find the smallest power of ten that scales the failure probabilities without losing value. Is it
   the same on GridCap medium?
3. Write a callback that stops at the first plan within 0.1% of the bound or at the fifth solution,
   whichever comes first. Which of the two stops the search on GridCap medium?

## Design Note: A Callback Observes; It Does Not Model

CP-SAT's callbacks read solutions and can stop the search; they cannot add a constraint while the
solver runs (the Primer says so explicitly: no lazy constraints). Keep it that way in your own code.
A rule that matters to the plan belongs in the model, where the solver can reason with it and prove
the optimum under it; a callback that throws away solutions it dislikes leaves the solver proving
optimality of a model that is not the one you meant. Use the callback for what only it can do:
watching, recording, and deciding when to stop.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**objectives.py.** The objective and bound under three gap limits on GridCap medium, and a replaced
objective (*One Linear Objective, and OPTIMAL Means Within the Gap Limit*). *Try:* Set
`absolute_gap_limit` to 500 instead. Predict the status and the gap.

- Program: [objectives.py](src/objectives.py)

**scaled_row.py.** The OR-Tools example whose fractional row is multiplied by 2, adapted from
`cp_sat_example.py` (*Scale a Row Exactly, With a Whole-Number Multiplier*). *Try:* Use the row
$`2x + 7y + 3z \le 51`$. Predict whether the optimum moves.

- Program: [scaled_row.py](src/scaled_row.py)

**scaling.py.** A decimal crew row scaled exactly and rounded wrongly, then the failure-probability
objective as floats and at four scales (*Scale a Row Exactly, With a Whole-Number Multiplier*, *Scale
an Objective Enough to Keep Its Order*). *Try:* Scale by 20 instead of 10. Predict the shortfall.

- Program: [scaling.py](src/scaling.py)

**callbacks.py.** A callback that records every improving solution on GridCap medium, and one that
stops within 0.5% of the bound (*A Solution Callback Sees Every Improving Plan*). *Try:* Stop
within 0.1%. Predict how many solutions the search reports before it stops.

- Program: [callbacks.py](src/callbacks.py)

**all_optima.py.** Every optimal plan of the committee's score on GridCap small, checked by brute force
on GridCap tiny, and the same enumeration with the objective left on (*Every Optimal Plan: Optimize,
Fix the Objective, Enumerate*). *Try:* Print the NPV-best of the nine plans as the tie-break. Which is
it?

- Program: [all_optima.py](src/all_optima.py)
