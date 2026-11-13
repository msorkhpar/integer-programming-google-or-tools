# 14.3.1 The First Request: Replace the Worst Transformers, and Why Ranking Is Not Enough

GridCap's asset team keeps a spreadsheet of its substation transformers. Every autumn an engineer
sorts it by condition score, walks down the list and stops when the year's money runs out. This
year the engineer has been asked to turn that habit into code, and writes the request down:

> **Request 1.** We have $10,000k for transformer replacements in 2027. Replace the worst
> transformers we can afford. The list must be repeatable, so put it in code, with tests.

This module grows that request into a real planning model, one requirement per lesson. The project
lives in complete snapshots: `steps/00` is the code before this lesson, `steps/01` the code after it.
The fleet is invented, made by a seeded generator in the project (GridCap is fictional), and the
first lesson starts where the engineer did: with the ranking.

## The Starting Code Ranks by One Number and Stops at the First Unit That Does Not Fit

The skeleton has four modules. `fleet.py` holds one record per transformer and the generator;
`rank.py` holds the asset team's rule; `report.py` adds up what a list costs and removes; and
`__main__.py` prints this year's list. A transformer carries what the asset team knows about it:

| Field | Meaning |
| --- | --- |
| `tid`, `substation`, `region` | identity and where it is |
| `kind` | `small`, `medium` or `large`, which sets its cost range and failure curve |
| `age` | years in 2027 |
| `cost` | $k to replace it |
| `cof` | consequence of failure: $k that one failure costs (lesson 7.3.3) |
| `condition` | the inspection score, 0 to 100, higher is worse |
| `pof` | the asset-health team's probability that it fails in 2027 (lesson 7.3.1) |

The ranking sorts by `condition` and takes units until the next one would break the budget:

```diff
--- /dev/null
+++ 00/renewal/rank.py
@@
+def worst_first(fleet: list[Transformer], budget: int) -> list[str]:
+    """Walk down the condition ranking and take units until the next one does not fit the budget."""
+    chosen, spent = [], 0
+    for t in sorted(fleet, key=lambda t: (-t.condition, t.tid)):
+        if spent + t.cost > budget:
+            break
+        chosen.append(t.tid)
+        spent += t.cost
+    return chosen
```

The program `first_request.py` runs it on a 500-unit fleet. The measure of a list is the **risk** it
removes: a unit's expected failure cost this year, $`\text{pof}_i \times \text{cof}_i`$ in $k
(lesson 7.3.3), summed over the units replaced:

```text
fleet: 500 units in 59 substations; 302 small, 144 medium, 54 large; risk this year $62,092k
worst first     :  9 units, $9,780k of $10,000k, risk removed $3,255k
```

Nine units. The list is short because the worst-scored units are not cheap, and the walk stops at
the tenth, which does not fit, although cheaper units further down would.

## A Condition Score Is Not Risk, and the Ranking Cannot See Cost

Three things are wrong with the ranking, and only the last is about code:

1. **It ranks by condition, and condition is not risk.** Condition says how worn a unit looks. Risk
   also needs what a failure costs: a worn unit feeding few customers can matter less than a
   fair one feeding a hospital.
2. **It ignores what a unit costs.** Two $400k units can remove more risk than one $1,090k unit.
3. **It stops at the first unit that does not fit**, and leaves money on the table.

The top of the worst-first list shows the first two:

```text
the worst-first list, top five:
  T00033 small  age 67  condition 100  PoF 0.087  CoF $1,390k  risk $121k  cost $380k  in model: no
  T00076 small  age 65  condition 100  PoF 0.082  CoF $7,050k  risk $577k  cost $400k  in model: yes
  T00106 medium age 54  condition 100  PoF 0.046  CoF $3,970k  risk $181k  cost $740k  in model: no
  T00181 small  age 67  condition 100  PoF 0.087  CoF $3,760k  risk $328k  cost $450k  in model: no
  T00182 medium age 65  condition 100  PoF 0.073  CoF $5,330k  risk $387k  cost $1,090k  in model: no
units on both lists: 2 of 9
```

All five score 100, so the sort cannot tell them apart and falls back on the id. T00033 and T00076
are the same kind at about the same age, with almost the same PoF; T00076's failure costs five times
as much. The "in model" column is the plan of the next section: it keeps 2 of the 9 ranked units.

A better ranking fixes the first two faults: sort by risk removed per $k, and skip a unit that does
not fit instead of stopping. It is a common next step, and the program tries it too:

```python
def best_ratio_first(fleet, budget):
    """A better ranking: risk removed per $k, skipping any unit that no longer fits."""
    chosen, spent = [], 0
    for t in sorted(fleet, key=lambda t: (-risk(t) / t.cost, t.tid)):
        if spent + t.cost <= budget:
            chosen.append(t.tid)
            spent += t.cost
    return chosen
```

```text
worst first     :  9 units, $9,780k of $10,000k, risk removed $3,255k
risk per $ first: 30 units, $9,840k of $10,000k, risk removed $11,424k
model           : 30 units, $9,990k of $10,000k, risk removed $11,533k
model status OPTIMAL, bound $11,533k
```

The ratio ranking removes 3.5 times what worst-first removes. On one budget it comes close to the
model, but not all the way:

```text
risk per $ first leaves $160k unspent; the model removes $109k more
```

The ratio ranking is a greedy rule for a **knapsack**: choose items, each with a value and a weight,
to get the most value within a capacity (lesson 6.3.1). Greedy by value per weight is good on one
knapsack and still not optimal, because the last few choices depend on what exactly fits. More to
the point for this project, a ranking cannot carry a second rule. The requests that follow add ten
years of budgets, outages shared by a substation, crews per region and spare units. A ranking has
nowhere to put any of them. A model does: each rule is one more row.

## The Design Decision: State the Choice as a 0-1 Model, Keep the Ranking as a Baseline

The engineer has three options:

| Option | For | Against |
| --- | --- | --- |
| keep worst-first | the asset team knows it | removes 28% of what the best list removes here |
| ratio ranking | simple, close on one budget | no bound to say how close; cannot hold a second rule |
| 0-1 model, solved by HiGHS | best list, with a bound; each rule is a row | a solver dependency and a model to test |

The project takes the model, and keeps `rank.py` as a baseline to compare against: a plan that is
worse than the asset team's list is a bug, and the comparison is the first thing a reviewer asks
for. The model is written with MathOpt, the OR-Tools modeling layer (lesson 4.2.1), and solved with
HiGHS. A solve also returns the **bound** (lesson 3.4.1): no list can remove more than it. Here the
bound equals the plan's value, so the plan is proved best, which no ranking can say about itself.

## The Model

The first model is a 0-1 knapsack with one row.

**Sets.** $`I`$, the transformers in the fleet.

**Parameters.** $`r_i = \text{pof}_i \cdot \text{cof}_i`$, the risk removed by replacing unit $`i`$
in 2027 ($k), since a new unit's chance of failing in its first year is negligible next to an old
one's; $`c_i`$, its replacement cost ($k); $`B`$, the 2027 budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in I`$: 1 if unit $`i`$ is replaced in 2027.

**Objective.**

```math
\max \; \sum_{i \in I} r_i \, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in I} c_i \, x_i &\le B && && \text{(budget)}
\end{aligned}
```

Before this lesson there was no model: the "plan" was the ranking's output. The row's code name is
`budget`, and the variables are named `x_T00042`.

## The Change, File by File

Six files change or arrive; one of them, `risk.py`, is only a stub for the next lesson. Each diff
below is lifted from the two snapshots it names.

**`model.py` (new): the formulation as code.** `Built` keeps the handles the rest of the code needs:
the model, the variables by transformer id, and the budget row. `build` writes the model above line
for line, and its variables and its row are yours to write in the practice:

```diff
--- /dev/null
+++ 01/renewal/model.py
@@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from ortools.math_opt.python import mathopt
+
+from .fleet import Transformer, risk
+from .request import Request
+
+
+@dataclass
+class Built:
+    model: mathopt.Model
+    x: dict[str, mathopt.Variable]          # x[i] = 1: replace transformer i this year
+    budget: mathopt.LinearConstraint
+
+
+def build(fleet: list[Transformer], request: Request) -> Built:
+    model = mathopt.Model(name="renewal")
```

- **The variables.** One binary $`x_i`$ per transformer of the fleet, made with
  `model.add_binary_variable(name=...)` and named `x_<tid>` (`x_T00042`), in a dict keyed by the
  transformer's id.
- **The row (budget).** The sum of `t.cost` times $`x_i`$ over the fleet at most `request.budget`,
  added with `model.add_linear_constraint(..., name="budget")`, whose return value is the row
  handle `Built` keeps.
- **The objective.** It is the one line of the body the page shows; the risk $`r_i`$ is `fleet.risk(t)`:

```diff
--- /dev/null
+++ 01/renewal/model.py
@@
+    model.maximize(sum(risk(t) * x[t.tid] for t in fleet))
+    return Built(model, x, budget)
```

**`solve.py` (new): solving and reading the answer.** Four names, all new:

- `FOUND` is the pair of termination reasons that come with a plan, `OPTIMAL` and `FEASIBLE`
  (lesson 4.2.2); every other reason means no plan to read.
- `solve_quietly` calls HiGHS with the process's output pointed away for the solve, so a stray
  line from the bundled HiGHS never reaches the report (the course's runs do the same). Two lines
  do the work. `os.dup2(sink, 1)` points file descriptor 1, the process's standard output, at
  `/dev/null`, which silences C code that never goes through Python's `sys.stdout`; the saved copy
  puts it back afterwards. `ctypes.CDLL(None).fflush(None)` calls the C library's `fflush` on every
  C stream before that, so output HiGHS left in C's buffer is written to `/dev/null` now, not to the
  report later.
- `is_feasible` asks whether the result's termination reason is in `FOUND`.
- `read_plan` turns a result into a `Plan`: the ids whose variable is above 0.5 (a binary comes back
  as a float within the solver's integrality tolerance, lesson 10.1.1), the objective, the bound and
  the termination reason (lesson 4.2.2).

```diff
--- /dev/null
+++ 01/renewal/solve.py
@@
+from __future__ import annotations
+
+import ctypes
+import os
+import sys
+
+from ortools.math_opt.python import mathopt
+
+from .fleet import FIRST_YEAR
+from .request import Plan
+
+FOUND = (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE)
+
+
+def solve_quietly(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
+    """Solve with HiGHS, with the process's standard output pointed at /dev/null for the solve.
+
+    The HiGHS bundled in OR-Tools 9.15 can print a stray debug line on a MIP solve with no log asked
+    for; it is buffered C output, so it is flushed before the output is restored.
+    """
+    sys.stdout.flush()
+    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
+    os.dup2(sink, 1)
+    try:
+        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
+    finally:
+        ctypes.CDLL(None).fflush(None)
+        os.dup2(saved, 1)
+        os.close(saved)
+        os.close(sink)
+
+
+def is_feasible(result: mathopt.SolveResult) -> bool:
+    return result.termination.reason in FOUND
+
+
+def read_plan(built, result: mathopt.SolveResult) -> Plan:
+    if not is_feasible(result):
+        return Plan({}, 0.0, 0.0, result.termination.reason.name)
+    replace = {tid: FIRST_YEAR for tid, var in built.x.items() if result.variable_values(var) > 0.5}
+    return Plan(replace, result.objective_value(), result.termination.objective_bounds.dual_bound,
+                result.termination.reason.name)
```

**`risk.py` (new): a stub for the next lesson.** Nothing in this step calls it; it holds the names
the next lesson fills in, each returning 0:

```diff
--- /dev/null
+++ 01/renewal/risk.py
@@
+from __future__ import annotations
+
+from .fleet import Transformer
+from .request import Request
+
+
+def pof_next(age: float, kind: str) -> float:
+    """The probability that a unit of this kind, working at `age`, fails within the year."""
+    return 0.0
+
+
+def risk_removed(t: Transformer, start: int, request: Request) -> float:
+    """The coefficient of x[i, start]: failure cost avoided over the risk window, discounted, $k."""
+    return 0.0
```

**`plan.py`: the entry point stops ranking.** In the skeleton, `plan` was a stub that returned the
ranking and `feasible` a stub that allowed everything, so that this lesson's tests could import
them and fail on their assertions. Now `plan` builds and solves, and `feasible` answers the question
every rule test asks: does the model allow *exactly* this list? It fixes every variable to the list
(lower and upper bound equal) and asks the solver whether any solution remains.

```diff
--- 00/renewal/plan.py
+++ 01/renewal/plan.py
@@
 def plan(fleet: list[Transformer], request: Request) -> Plan:
     """The replacements that remove the most risk within the request's rules."""
-    chosen = worst_first(fleet, request.budget)
-    by_id = {t.tid: t for t in fleet}
-    return Plan({tid: FIRST_YEAR for tid in chosen}, sum(risk(by_id[tid]) for tid in chosen), 0.0, "NOT_SOLVED")
+    built = build(fleet, request)
+    return read_plan(built, solve_quietly(built.model))
 
 
 def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool:
     """Does the model allow exactly these replacements? Every other unit is held at 'keep'."""
-    return True
+    built = build(fleet, request)
+    for tid, var in built.x.items():
+        var.lower_bound = var.upper_bound = 1 if tid in replace else 0
+    return is_feasible(solve_quietly(built.model))
```

**`request.py`: one field now, five stubs for the next lesson.** `Request` is what the planner
asks for and `Plan` what comes back. The `Plan` records a year per unit already (always 2027 here),
so the next lesson's ten-year plan needs no new type. The stub fields at the end are the next
lesson's; this model ignores them.

```diff
--- 00/renewal/request.py
+++ 01/renewal/request.py
@@
 @dataclass(frozen=True)
 class Request:
     budget: int                 # $k for the year
+    # Stubs: the next lesson gives these fields their meaning; this model ignores them.
+    years: int = 1
+    window: int | None = None
+    rate: float = 0.07
+    min_age: int = 0
+    gap: float = 0.0
```

**`__main__.py`: print both lists.** The ranking stays as the baseline:

```diff
--- 00/renewal/__main__.py
+++ 01/renewal/__main__.py
@@
 if __name__ == "__main__":
     fleet = generate_fleet(500)
-    s = summarize(fleet, worst_first(fleet, BUDGET))
-    print(f"worst first: {s.units} units, ${s.spend:,}k of ${BUDGET:,}k, risk removed ${s.risk_removed:,.0f}k")
+    for name, chosen in (("worst first", worst_first(fleet, BUDGET)),
+                         ("model", list(plan(fleet, Request(BUDGET)).replace))):
+        s = summarize(fleet, chosen)
+        print(f"{name:11}: {s.units} units, ${s.spend:,}k of ${BUDGET:,}k, risk removed ${s.risk_removed:,.0f}k")
```

## The Tests Pin the Mistakes a Ranking Makes, on Fleets Small Enough to Check by Hand

The tests never use the 500-unit fleet. Each builds a fleet of three to eight units where the right
answer is known, the style of the section 12 lesson *Unit-Testing One Constraint at a Time*:

- **the riskiest, not the worst-scored:** unit A scores 95 but its failure costs $1,000k; B and C
  score lower and cost $3,000k and $2,500k. The plan must be {B, C}.
- **money a ranking leaves:** A, B and C cost $500k, $700k and $400k under a $1,000k budget. The
  ranking takes A, cannot fit B, and stops. The plan must be {A, C}.
- **the best subset:** eight random units; the plan's value must equal the best of all 256 subsets,
  found by brute force. A model too small to get wrong by inspection is checked by enumeration.
- **the budget row, at its edge:** a list that spends exactly $1,000k is allowed, and the same list
  plus a $10k unit is refused. An allowed plan and a refused one sit in the same test, so a model
  with no budget row fails it.

```diff
--- /dev/null
+++ 01/tests/test_plan.py
@@
+def test_the_budget_allows_a_plan_at_the_limit_and_refuses_one_above_it():
+    fleet = [unit("A", 500, 0.05, 2000), unit("B", 500, 0.05, 2000), unit("C", 10, 0.05, 2000)]
+    assert feasible(fleet, Request(budget=1000), {"A": 2027, "B": 2027})
+    assert not feasible(fleet, Request(budget=1000), {"A": 2027, "B": 2027, "C": 2027})
```

The new tests, run on the skeleton's code and then on this lesson's:

```text
step 01 tests on the code of step 00 (before): 4 passed, 4 failed
  FAILED test_plan.py::test_the_plan_takes_the_riskiest_units_not_the_worst_scored (AssertionError)
         assert {'A'} == {'B', 'C'}
  FAILED test_plan.py::test_the_plan_uses_money_a_ranking_leaves_on_the_table (AssertionError)
         assert ['A'] == ['A', 'C']
  FAILED test_plan.py::test_the_plan_is_the_best_subset_within_the_budget (AssertionError)
         assert 1080.6624615305157 < 1e-06
  FAILED test_plan.py::test_the_budget_allows_a_plan_at_the_limit_and_refuses_one_above_it (AssertionError)
         assert not True
step 01 tests on the code of step 01 (after): 8 passed, 0 failed
tests step 01 adds or changes: 4
```

Before the change, every new test fails on an assertion that names the ranking's mistake: it picks
{A} where {B, C} is right, stops at [A], misses the best subset by $1,081k, and allows a list over
budget. The skeleton's four tests (the generator and the ranking) pass both times. This is the
shape of every lesson's practice in this module: the starter is the code before the change, and
these tests grade it.

## What the Step Did to the Code

The program `growth.py` counts each snapshot: code lines (no blanks, comments or docstrings),
functions, tests, and the branching of the most branching function (1 plus one per `if`, loop,
condition and boolean operator, a McCabe-style count):

```text
step  files  lines  functions  tests  test lines  most branching function
00        7    104          7      4          25  rank.worst_first (3)
01       10    167         13      8          55  solve.read_plan (3)
```

The code grew by 63 lines, most of them `solve.py`'s plumbing, and stayed flat: no function
branches more than three ways. The logic moved out of a loop and into a model. `worst_first` had
one rule hard-wired into its loop; `build` has none in its control flow, only a row. That is the
style the rest of the module keeps: rules are rows, and adding one does not touch the others.

**Practice.** This lesson's project practice starts from the code before this step, the whole
package (snapshot `steps/00`). It is graded by the tests in the practice's `tests/` folder and by a
check that `main.py` prints the practice's `expected/report.txt`; the practice's statement gives the
request `main.py` makes and the format of every line it prints. This step's `main.py` plans a tiny
fleet of 25 units, drawn from seed 56, by the ranking and by the model.

<!-- practice 1 -->

## Summary

- **A ranking sorts by one number and stops at the first unit that does not fit.** Worst-first
  removed $3,255k of risk where the best list removes $11,533k.
- **A condition score is not risk, and a ranking cannot see cost.** Risk is PoF times CoF, and the
  choice under a budget is a knapsack.
- **A better ranking comes close on one budget but proves nothing and holds no second rule.** The
  0-1 model gives the best list and a bound, and every later rule is a row.
- **The tests pin each mistake on a fleet small enough to check by hand**, and pair an allowed and a
  refused list at the budget's edge.

## Reference

| Piece | Where |
| --- | --- |
| risk of unit $`i`$ this year | $`r_i = \text{pof}_i \cdot \text{cof}_i`$, `fleet.risk` |
| the model | `model.build`: $`\max \sum r_i x_i`$ s.t. $`\sum c_i x_i \le B`$ |
| solve, read the plan and its bound | `solve.solve_quietly`, `solve.read_plan` |
| does the model allow this list? | `plan.feasible`: fix every variable, solve, read the status |
| the baseline | `rank.worst_first` |

**Further reading:** [MathOpt `model.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/model.py) (`add_binary_variable`, `add_linear_constraint` and `maximize`, as `build` uses them); [MathOpt `result.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/result.py) (`termination.objective_bounds.dual_bound`, the bound `read_plan` keeps, and the termination reasons). Both were read from the copy installed in the course's runner image. Lessons 6.3.1 (the knapsack), 7.3.3 (risk as PoF times CoF) and 3.4.1 (bounds and gaps) are the course's own background for this step.

## Challenges

1. Add a tie-break to `worst_first` that prefers the cheaper of two units with the same score.
   Predict whether it closes much of the gap to the model on the 500-unit fleet, then run it.
2. Write a test in which the ratio ranking, too, misses the best list. What is the smallest fleet
   that does it?
3. Finance asks for "the 30 riskiest units". Which row would you add, and does it keep the budget row?

## Design Note: Keep the Baseline in the Code

`rank.py` is not deleted. The asset team trusts it, and a reviewer's first question about a model is
"how does it compare with what we do now?". Keeping the baseline in the package, and printing both
lists, answers that on every run and catches a class of bug no unit test sees: a model that is
"optimal" for the wrong objective and does worse than the old habit.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**first_request.py.** Runs the worst-first list, the risk-per-dollar ranking and the model on the
fictional 500-unit fleet, shows the top of the ranking, and runs the step's tests on the code before
and after the change (*every section*). *Try:* Lower the budget to $3,000k. Predict whether the
ratio ranking gets closer to the model or further from it.

**growth.py.** Counts files, code lines, functions, tests and branching in every snapshot (*What
the Step Did to the Code*). *Try:* Predict which function will branch the most once the module is
done, then look at the last row.

- Program: [first_request.py](src/first_request.py)
- Program: [growth.py](src/growth.py)
- Library: [steps.py](src/steps.py)
