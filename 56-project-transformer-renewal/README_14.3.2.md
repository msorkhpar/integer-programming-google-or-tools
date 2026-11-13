# 14.3.2 A Ten-Year Budget and Weibull Failure Risk

The one-year list went to the planning meeting, and finance answered with a longer horizon:

> **Request 2.** Finance has set the transformer budget at $10,000k a year for 2027 to 2036. Give us
> a ten-year plan: which units to replace, and in which year. A unit we wait on keeps aging, so the
> plan should count the risk each year of waiting leaves in place. The asset team says units under
> 40 years old are not worth looking at this decade.

The code of the last lesson (snapshot `steps/01`) decides one year. This lesson's code is snapshot
`steps/02`. The fleet is still the invented 500-unit one.

## One Year's PoF Cannot Value a Plan That Waits

The model of the first lesson valued a replacement at $`\text{pof}_i \cdot \text{cof}_i`$: the
asset-health team's PoF for 2027 times the cost of a failure. That is one number per unit, and a ten-
year plan needs a number per unit *and* year, for two reasons:

- **A unit that waits ages.** Replacing T00076 in 2030 leaves three more years of the old unit in
  service, each with a higher PoF than the last.
- **A new unit is not risk-free forever.** It starts its own curve on the day it goes in.

So the model needs the PoF at any age, not one column of this year's values. That is what a failure
curve gives (lesson 7.3.1): for a Weibull curve with shape $`\beta`$ and scale $`\eta`$, a unit
working at age $`a`$ fails within the year with probability

```math
\text{PoF}(a) = 1 - \frac{R(a+1)}{R(a)} = 1 - \exp\!\left(\left(\frac{a}{\eta}\right)^{\beta} - \left(\frac{a+1}{\eta}\right)^{\beta}\right)
```

The generator already drew this year's `pof` column from one curve per kind (the curves live in
`KINDS`, next to costs). The asset team's numbers and the curves agree, which the program checks on
one unit:

```text
T00076: small, age 65, CoF $7,050k; PoF column 0.0819, curve 0.0819
  PoF by year if kept: 2027: 0.082, 2030: 0.090, 2033: 0.098, 2036: 0.107
```

| Kind | $`\beta`$ | $`\eta`$ (years) | Cost range ($k) |
| --- | ---: | ---: | --- |
| small | 3.2 | 55 | 250–450 |
| medium | 3.6 | 60 | 700–1,300 |
| large | 4.0 | 65 | 2,200–3,800 |

## A Replacement's Value Is the Risk It Removes Over a Window, Discounted

Replacing unit $`i`$ in year $`t`$ changes nothing before $`t`$. From $`t`$ on, the old unit's PoF at
its age is swapped for a new unit's PoF at age $`y - t`$. Summed over a window of years $`W`$ and
discounted at rate $`\rho`$ to 2027 (lesson 7.3.4), the coefficient of $`x_{i,t}`$ is

```math
\text{rr}_{i,t} = \sum_{y \in W,\; y \ge t} \frac{\big(\text{PoF}_{k(i)}(a_i + y - y_0) - \text{PoF}_{k(i)}(y - t)\big)\, \text{cof}_i}{(1 + \rho)^{\,y - y_0}}
```

where $`k(i)`$ is the unit's kind, $`a_i`$ its age in $`y_0 = 2027`$, and the plan uses $`\rho = 7\%`$.

**The design decision is the window.** If $`W`$ is the plan's own ten years, a replacement in 2036
counts one year of benefit and one in 2027 counts ten, so late replacements look nearly worthless.
That is the end-of-horizon effect of lesson 7.3.4. The alternatives are a window of plan years, a
fixed longer window, or a value for the unit's whole remaining life. The project takes a fixed
window of 20 years, $`W = \{2027, \dots, 2046\}`$: long enough that a 2036 replacement still
counts ten years of service, and simple to explain. `Request.window` holds it, and the coefficients
for T00076 show what it changes:

```text
rr[start] over 10 years: 2027: 4,897, 2030: 3,238, 2033: 1,745, 2036: 411
rr[start] over 20 years: 2027: 8,113, 2030: 6,487, 2033: 5,019, 2036: 3,701
```

With ten years, a 2036 replacement is worth 8% of a 2027 one; with twenty, 46%. Every coefficient
falls with a later start, because each year of waiting is a year of the old unit's risk.

The second decision is **who is a candidate**. The asset team's rule, 40 years and older, is a
domain restriction: younger units get no variable at all. It cuts the model to 211 of the 500
units.

## The Model

The first lesson's knapsack becomes a start-year model (lesson 6.4.1), one budget row per year.
Changes from the last lesson are marked.

**Sets.** $`I = \{ i : a_i \ge 40 \}`$, the candidate transformers $`\leftarrow`$; $`Y = \{2027,
\dots, 2036\}`$, the plan's years $`\leftarrow`$; $`W = \{2027, \dots, 2046\}`$, the risk window
$`\leftarrow`$.

**Parameters.** $`\text{rr}_{i,t}`$, the discounted risk removed over $`W`$ by replacing unit $`i`$
in year $`t`$ ($k, formula above) $`\leftarrow`$ (it replaces $`r_i = \text{pof}_i\,\text{cof}_i`$);
$`c_i`$, the replacement cost ($k); $`B`$, the budget of each year ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in I`$, $`t \in Y`$: 1 if unit $`i`$ is
replaced in year $`t`$ $`\leftarrow`$ (it replaces $`x_i`$).

**Objective.**

```math
\max \; \sum_{i \in I} \sum_{t \in Y} \text{rr}_{i,t} \, x_{i,t} \quad \leftarrow \text{this lesson}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in Y} x_{i,t} &\le 1 && \forall i \in I && \text{(once}_i) \quad \leftarrow \text{this lesson} \\
\sum_{i \in I} c_i \, x_{i,t} &\le B && \forall t \in Y && \text{(budget}_t) \quad \leftarrow \text{this lesson}
\end{aligned}
```

The code names the rows `once_T00076` and `budget_2029`, and the variables `x_T00076_2029`. The one
budget row of the last lesson is now ten.

## The Change, File by File

**`request.py`: the request gets a horizon.** The five stub fields of the last snapshot become real.
`years` and `window` are counts from 2027, so a request stays readable, and two methods turn them
into ranges. `window=None` means "the plan's own years". The defaults describe the first lesson's
one-year request, so its tests still state what they meant. Two new stubs belong to the next lesson.

```diff
--- 01/renewal/request.py
+++ 02/renewal/request.py
@@
 from dataclasses import dataclass

+from .fleet import FIRST_YEAR
+

 @dataclass(frozen=True)
 class Request:
-    budget: int                 # $k for the year
+    budget: int                 # $k per year
+    years: int = 1              # the plan's length, from FIRST_YEAR
+    window: int | None = None   # years over which removed risk is counted; None: the plan's years
+    rate: float = 0.07          # discount rate for risk removed in later years
+    min_age: int = 0            # units younger than this, in FIRST_YEAR, are not candidates
+    gap: float = 0.0            # stop when the plan is within this share of the bound
     # Stubs: the next lesson gives these fields their meaning; this model ignores them.
-    years: int = 1
-    window: int | None = None
-    rate: float = 0.07
-    min_age: int = 0
-    gap: float = 0.0
+    outage_cost: int = 0
+    outages: int | None = None
+
+    def plan_years(self) -> range:
+        return range(FIRST_YEAR, FIRST_YEAR + self.years)
+
+    def risk_years(self) -> range:
+        return range(FIRST_YEAR, FIRST_YEAR + (self.window or self.years))
```

**`risk.py`: the stubs become the curve and the coefficient.** `pof_next` reads a kind's curve;
`risk_removed` is the formula for $`\text{rr}_{i,t}`$, term by term.

```diff
--- 01/renewal/risk.py
+++ 02/renewal/risk.py
@@
-from .fleet import Transformer
+from .fleet import FIRST_YEAR, KINDS, Transformer, weibull_pof
 from .request import Request
@@
 def pof_next(age: float, kind: str) -> float:
     """The probability that a unit of this kind, working at `age`, fails within the year."""
-    return 0.0
+    return weibull_pof(age, KINDS[kind].beta, KINDS[kind].eta)
 
 
 def risk_removed(t: Transformer, start: int, request: Request) -> float:
-    """The coefficient of x[i, start]: failure cost avoided over the risk window, discounted, $k."""
-    return 0.0
+    """The coefficient of x[i, start]: failure cost avoided over the risk window, discounted, $k.
+
+    In each year from `start` on, the old unit's PoF at its age is replaced by a new unit's PoF at
+    its age, `y - start` (lesson 7.3.4). Years before `start` keep the old unit and remove nothing.
+    """
+    total = 0.0
+    for y in request.risk_years():
+        if y >= start:
+            old = pof_next(t.age + y - FIRST_YEAR, t.kind)
+            new = pof_next(y - start, t.kind)
+            total += (old - new) * t.cof / (1 + request.rate) ** (y - FIRST_YEAR)
+    return total
```

**`fleet.py`: the curve function goes public.** The generator's private `_pof` is renamed
`weibull_pof`, because `risk.py` now needs it too. One formula, two callers: the generator's PoF
column and the model's coefficients cannot drift apart.

```diff
--- 01/renewal/fleet.py
+++ 02/renewal/fleet.py
@@
-def _pof(age: float, beta: float, eta: float) -> float:
+def weibull_pof(age: float, beta: float, eta: float) -> float:
     """Weibull probability of failing within a year, given working at `age` (lesson 7.3.1)."""
     return 1 - math.exp((age / eta) ** beta - ((age + 1) / eta) ** beta)
```

**`model.py`: a variable per unit and year, a row per year.** `x` is now keyed by `(tid, year)`
and `budget` by year. `candidates` applies the age screen:

```diff
--- 01/renewal/model.py
+++ 02/renewal/model.py
@@
-from .fleet import Transformer, risk
+from .fleet import Transformer
 from .request import Request
+from .risk import risk_removed
@@
 @dataclass
 class Built:
     model: mathopt.Model
-    x: dict[str, mathopt.Variable]          # x[i] = 1: replace transformer i this year
-    budget: mathopt.LinearConstraint
+    x: dict[tuple[str, int], mathopt.Variable]      # x[i, t] = 1: replace transformer i in year t
+    budget: dict[int, mathopt.LinearConstraint]     # one row per year
+
+
+def candidates(fleet: list[Transformer], request: Request) -> list[Transformer]:
+    return [t for t in fleet if t.age >= request.min_age]
 
 
 def build(fleet: list[Transformer], request: Request) -> Built:
     model = mathopt.Model(name="renewal")
+    units, years = candidates(fleet, request), request.plan_years()
```

Each set in the formulation is one name in the code: $`I`$ is `units`, $`Y`$ is `years`. The rest of
`build`, the start-year model itself, is yours to write in the practice; the model above is its
specification:

- **The variables.** One binary $`x_{i,t}`$ for every candidate $`i`$ and plan year $`t`$, named
  `x_<tid>_<year>` and kept in `x` under the key `(tid, year)`.
- **$`\text{once}_i`$.** For each candidate, the sum of its variables over the plan years at most 1,
  named `once_<tid>`. This row is what turns *when* into a choice: without it the solver could
  replace one unit in every plan year and collect its coefficient each time.
- **$`\text{budget}_t`$.** For each plan year, the summed cost of that year's replacements at most
  `request.budget`, named `budget_<year>`; `Built.budget` maps each year to its row.
- **The objective.** Maximize the sum over candidates and years of `risk_removed(t, y, request)`
  times $`x_{i,t}`$, the coefficient $`\text{rr}_{i,t}`$ of the `risk.py` change above.

`build` still ends with `return Built(model, x, budget)`, so `plan` and `feasible` keep calling it the
same way.

**`plan.py` and `solve.py`: years in, years out.** `feasible` fixes `x[i, t]` to 1 only for the
year the list names; `read_plan` returns each unit's year instead of always 2027. And `plan` passes
the request's **gap**: HiGHS stops once its plan is within that share of the bound and reports
`OPTIMAL` (MathOpt's `relative_gap_tolerance`; lesson 3.4.2). The tests leave it at 0, an exact
solve; the 500-unit plan uses 2%.

```diff
--- 01/renewal/plan.py
+++ 02/renewal/plan.py
@@
 from __future__ import annotations

+from ortools.math_opt.python import mathopt
+
 from .fleet import Transformer
@@
 def plan(fleet: list[Transformer], request: Request) -> Plan:
     """The replacements that remove the most risk within the request's rules."""
     built = build(fleet, request)
-    return read_plan(built, solve_quietly(built.model))
+    params = mathopt.SolveParameters(relative_gap_tolerance=request.gap)
+    return read_plan(built, solve_quietly(built.model, params))
 
 
 def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool:
-    """Does the model allow exactly these replacements? Every other unit is held at 'keep'."""
+    """Does the model allow exactly these replacements (id -> year)? Every other choice is held at 0."""
     built = build(fleet, request)
-    for tid, var in built.x.items():
-        var.lower_bound = var.upper_bound = 1 if tid in replace else 0
+    for (tid, y), var in built.x.items():
+        var.lower_bound = var.upper_bound = 1 if replace.get(tid) == y else 0
     return is_feasible(solve_quietly(built.model))
```

```diff
--- 01/renewal/solve.py
+++ 02/renewal/solve.py
@@
 from ortools.math_opt.python import mathopt

-from .fleet import FIRST_YEAR
 from .request import Plan
@@
-    replace = {tid: FIRST_YEAR for tid, var in built.x.items() if result.variable_values(var) > 0.5}
+    replace = {tid: y for (tid, y), var in built.x.items() if result.variable_values(var) > 0.5}
```

**`report.py`: spend by year.** `spend_by_year` adds up what each year's replacements cost, for the
report: a dict from year to $k, sorted by year, with only the years that have work. Its
`outage_cost` argument is a stub that the next lesson uses to charge outages; here it is ignored.

```diff
--- 01/renewal/report.py
+++ 02/renewal/report.py
@@
+def spend_by_year(fleet: list[Transformer], replace: dict[str, int], outage_cost: int = 0) -> dict[int, int]:
+    """What the replacements cost in each year, $k. (Stub: the next lesson adds `outage_cost`.)"""
+    cost = {t.tid: t.cost for t in fleet}
+    spend: dict[int, int] = {}
+    for tid, y in replace.items():
+        spend[y] = spend.get(y, 0) + cost[tid]
+    return dict(sorted(spend.items()))
```

## The Ten-Year Plan Spends Every Year's Budget, and the Window Moves the Late Years

`ten_year_plan.py` solves the 500-unit fleet with the request finance sent:

```python
REQUEST = Request(budget=10_000, years=10, window=20, min_age=40, gap=0.02)
```

```text
candidates (age >= 40): 211 of 500
window 10: 161 units replaced, 25 of them in 2034-2036, risk removed $261,482k (bound $262,597k, OPTIMAL)
window 20: 161 units replaced, 27 of them in 2034-2036, risk removed $523,787k (bound $528,226k, OPTIMAL)
units placed differently by the two windows: 26
  2027: 30 units, $9,970k, mean age 59
  2028: 28 units, $9,980k, mean age 52
  2029: 18 units, $9,780k, mean age 53
  2030: 13 units, $9,890k, mean age 58
  2031: 16 units, $9,770k, mean age 54
  2032: 16 units, $9,740k, mean age 53
  2033: 13 units, $9,960k, mean age 54
  2034:  8 units, $10,000k, mean age 53
  2035: 10 units, $9,920k, mean age 48
  2036:  9 units, $9,950k, mean age 50
gap to the bound: 0.84%
```

Every year spends close to its $10,000k, so the budget binds each year: the plan is money-limited,
not candidate-limited. The first two years replace 30 and 28 units, the last three 8 to 10. The two
windows replace the same number of
units but place 26 of them differently: with ten years, late replacements count so little that the
plan shuffles which units wait. The two values are not comparable (they sum over different years);
only the plans are. The 2% gap is met at 0.84%: no ten-year plan under these rules removes more than
$528,226k.

## The Tests Pin the Curve, the Timing and Each Year's Row

The new tests, again on fleets of two to eight units:

- **the curve reproduces the PoF column** of 50 generated units, to the column's five decimals;
- **a later replacement removes less**, for an old unit, and more than nothing;
- **the coefficient by hand:** a three-year window, a 2029 start, the medium curve written out in
  the test with `math.exp`, discounted at 5%: equal to `risk_removed` within $`10^{-9}`$;
- **each year keeps its own budget:** two $600k units under $1,000k a year may go in 2027 and 2028,
  not both in 2027;
- **a tight budget spreads the work:** three units that fit one a year are replaced in 2027, 2028
  and 2029;
- **the riskier unit goes first**, and **a unit under the age screen is never chosen**, however
  costly its failure.

The best-subset test of the last lesson changes too: its brute force now values subsets with
`risk_removed`, so it checks the new objective, not the old one.

```text
step 02 tests on the code of step 01 (before): 7 passed, 8 failed
  FAILED test_plan.py::test_the_plan_is_the_best_subset_within_the_budget (AssertionError)
         assert 661.0 < 1e-06
  FAILED test_risk.py::test_the_curve_reproduces_the_fleet_pof_column (AssertionError)
         assert 0.03585 < 1e-05
  FAILED test_risk.py::test_a_later_replacement_removes_less_risk (AssertionError)
         assert 0.0 > 0.0
  FAILED test_risk.py::test_risk_removed_counts_the_years_after_the_replacement_discounted (AssertionError)
         assert 292.7158447930207 < 1e-09
  FAILED test_years.py::test_each_year_keeps_to_its_own_budget (AssertionError)
         assert False
  FAILED test_years.py::test_a_tight_budget_spreads_replacements_over_the_years (AssertionError)
         assert [] == [2027, 2028, 2029]
  FAILED test_years.py::test_the_riskier_unit_goes_first (AssertionError)
         assert {} == {'B': 2027, 'A': 2028}
  FAILED test_years.py::test_units_younger_than_the_screen_are_not_candidates (AssertionError)
         assert {} == {'B': 2027}
step 02 tests on the code of step 02 (after): 15 passed, 0 failed
tests step 02 adds or changes: 8
```

On the old code the stubbed curve returns 0, so the curve tests fail on their numbers. The year
tests fail because the one-year model has one variable per unit: asked for "A in 2027, B in 2028",
`feasible` fixes both to 1 in a model with one $1,000k row, and refuses a list it should allow; asked
to plan three years, it finds nothing with every coefficient at 0.

The other stubs take no part in that refusal. The old model ignores `min_age` and `gap`, as the
comment above them says, so it screens out no unit and stops no solve early. And `feasible` reads
no coefficient: it fixes the variables and asks only whether the rows can hold, so a curve that
returns 0 cannot make a list infeasible.

## What the Step Did to the Code

```text
01       10    167         13      8          55  solve.read_plan (3)
02       10    195         17     15          97  solve.read_plan (3)
```

28 code lines and 4 functions more, no new file, and no function branches more than before. The
model grew from one row to 211 + 10 = 221 rows and from 500 to 2,110 variables, but `build` is still
straight-line code. The cost moved into data: the request now has six fields, and the coefficient
is a 20-term sum per unit and year, computed in plain Python; a later lesson of this module measures
what that costs at 5,000 units.

**Practice.** This lesson's project practice starts from the code before this step, the whole
package (snapshot `steps/01`). It is graded by the tests in the practice's `tests/` folder and by a
check that `main.py` prints the practice's `expected/report.txt`; the practice's statement gives the
request `main.py` makes and the format of every line it prints. This step's `main.py` plans a tiny
fleet of 25 units, drawn from seed 56, over five years at $2,000k a year, with a ten-year risk
window, units 40 and older as candidates, and a 2% gap.

<!-- practice 1 -->

## Summary

- **One year's PoF cannot value a plan that waits.** A ten-year plan needs PoF at any age, so it
  needs a curve; the Weibull curve per kind reproduces the asset team's column.
- **A replacement's value is the risk it removes over a window, discounted.** A window of plan years
  undervalues late replacements; the project counts a fixed 20 years.
- **The model is a start-year model:** one variable per unit and year, `once` rows, and one budget
  row per year. The age screen is a domain restriction, not a row.
- **The tests pin the curve, the coefficient by hand, and each row on its own.**

## Reference

| Piece | Formula | Code |
| --- | --- | --- |
| PoF within the year at age $`a`$ | $`1 - e^{(a/\eta)^\beta - ((a+1)/\eta)^\beta}`$ | `fleet.weibull_pof`, `risk.pof_next` |
| risk removed, unit $`i`$, year $`t`$ | $`\text{rr}_{i,t}`$ above | `risk.risk_removed` |
| at most once | $`\sum_t x_{i,t} \le 1`$ | `once_{tid}` |
| each year's budget | $`\sum_i c_i x_{i,t} \le B`$ | `budget_{year}` |
| stop within a share of the bound | relative gap | `Request.gap`, `relative_gap_tolerance` |

**Further reading:** [MathOpt `parameters.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/parameters.py) (`relative_gap_tolerance`: the solver may stop and report `OPTIMAL` once the relative gap is at most the tolerance, and how the gap is normalized is solver-dependent); [MathOpt `model.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/model.py) (variable bounds set after the model is built, as `feasible` does). Both were read from the copy installed in the course's runner image. Lessons 7.3.1 (the Weibull PoF), 7.3.4 (the risk window and discounting) and 6.4.1 (start-year variables) are the course's background for this step.

## Challenges

1. Set `window=None`, so the window is the plan's ten years. Predict which years lose units, then
   compare with the "window 10" line above.
2. Finance offers $12,000k in 2027 and $8,000k in 2036 instead of a flat $10,000k. Which field of
   `Request` would you change into what, and which row reads it?
3. The asset team wants units over 65 replaced by 2030 at the latest. Is that a row or a domain
   change, and which test would you write first?

## Design Note: Defaults That Describe the Old Request

Every new field of `Request` has a default that means "as before": one year, the plan's own window,
no age screen, an exact solve. So the first lesson's tests still read as the first request, and a
caller who never heard of the horizon gets the one-year plan. The alternative, making the new fields
required, would have touched every caller and test to say what the defaults already say.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**ten_year_plan.py.** Checks the curve against the PoF column, prints one unit's coefficients for
two windows, solves the ten-year plan with each, prints the plan by year, and runs the step's tests
before and after the change (*every section*). *Try:* Change the discount rate to 0. Predict whether
the late years get more units.

- Program: [ten_year_plan.py](src/ten_year_plan.py)
- Program: [growth.py](src/growth.py)
- Library: [steps.py](src/steps.py)
