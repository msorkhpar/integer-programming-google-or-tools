# 14.3.5 From 500 to 5,000 Transformers: Building the Model at Scale

The 500 units so far were one district, the one the asset team piloted. The pilot worked, and the
next request is the whole fleet:

> **Request 5.** Run it for all of GridCap's substation transformers, about 5,000 units in ten
> districts. Budgets, crews and outage limits are ten times the pilot's, spares too. We need the
> plan in the same morning we ask for it.

The code before this lesson is snapshot `steps/04`; after it, `steps/05`. The fleets of 500 to 5,000
units come from the project's seeded generator and are invented (GridCap is fictional).

## Before Changing Anything, Measure Where the Time Goes

The temptation at this point is to rewrite the builder. The last two lessons left three loops that
scan every candidate inside another loop, and the coefficient is a 20-term sum in plain Python per
unit and year. Each of those grows faster than the fleet. But whether any of them matters at 5,000
units is a question for a clock, not for a code review (lesson 11.1.1): a run has phases, and each
phase gets its own measurement before anyone optimizes one.

The request also hides a change that is not about speed at all: the request's limits are numbers
for 500 units. At 5,000 units a budget of $10,000k a year would spread the pilot's money over ten
times the fleet, and the plan would be correct and useless. So the step has two parts: make
the request scale with the fleet, then measure and fix what the measurement names.

## A Request Scales With Its Fleet, in One Place

The ten-district request is the pilot's with every limit multiplied by ten. The alternative, a
second hand-written `Request` for 5,000 units, is how the two drift apart: someone raises the pilot's
crew-weeks and forgets the other. So `Request` gets a method that says which fields are limits that
grow with the fleet, and which (years, window, rate, outage cost, the age screen) do not:

```diff
--- 04/renewal/request.py
+++ 05/renewal/request.py
@@
     def scaled(self, factor: int) -> Request:
-        """Stub: the next lesson grows every limit with the fleet. Until then, the request unchanged."""
-        return self
+        """The same request for a fleet `factor` times larger: every limit grows with it."""
+        return replace(self, budget=self.budget * factor,
+                       outages=None if self.outages is None else self.outages * factor,
+                       crew_weeks=None if self.crew_weeks is None else self.crew_weeks * factor,
+                       spares={kind: n * factor for kind, n in self.spares.items()})
```

`scale.py` prints the result for 5,000 units:

```text
request for 5,000 units: budget $100,000k a year, 20 outages and 120 crew-weeks per region-year, spares {'medium': 20, 'large': 10}
```

Scaling a limit linearly is a modeling decision, and the lesson states it rather than hides it: ten
districts' crews are ten times one district's only if crews are spread like units are. A planner
who knows otherwise passes a different `Request`; `scaled` is the default, not a law.

## The Model Grows Linearly With the Fleet

The generator makes fleets of any size with the same proportions (lesson 11.1.3), so the model's size
can be counted exactly at four sizes:

```text
size of the model (exact):
    500 units:   211 candidates,   2650 variables,   843 rows,   10197 nonzeros
   1000 units:   438 candidates,   5520 variables,  1670 rows,   21218 nonzeros
   2000 units:   885 candidates,  11050 variables,  3177 rows,   42523 nonzeros
   5000 units:  2196 candidates,  27650 variables,  7978 rows,  106187 nonzeros
```

Ten times the fleet, about ten times everything: 2,196 candidates with ten years each are 21,960
replacement variables, plus 569 substations with candidates times ten outage variables, 27,650 in
all. Nothing in the formulation multiplies two sets that both grow with the fleet. The model is
not the problem; the question is whether the code that writes it, and the solver that solves it,
grow the same way.

## The Builder's Scans Grew Faster Than the Fleet, but the Solve Is What Takes the Time

The measurements come from one run of `scale.py` in the course's runner, on a laptop CPU shared
with other jobs at the time, so they are machine-dependent. Each build time is the median of three
runs (lesson 11.1.1). Your machine will give different numbers, and so would the next run here; read
the ratios, not the seconds:

<!-- unverified -->
```text
build time, median of 3 (s):
    500 units: reference   0.08  fast   0.06
   1000 units: reference   0.24  fast   0.11
   2000 units: reference   0.43  fast   0.18
   5000 units: reference   1.22  fast   0.65
coefficients at 5,000 units (s): one call per unit and year 0.21, one array computation 0.001
phases at 5,000 units, one run (s):
  generate 0.02  build 0.80  solve 17.66
  1520 units replaced, gap 0.82%, OPTIMAL
```

"Reference" is the builder of the last lesson, kept unchanged; "fast" is this lesson's. Three
findings, in order of importance:

1. **The solve is 95% of the run.** At 5,000 units HiGHS needs about 18 seconds to reach the 2% gap,
   and everything before it about one second. The morning the request asks for is not at risk from
   the build.
2. **The old builder grew about 15-fold for a 10-fold fleet** (0.08 s to 1.22 s), the signature of the
   scans; the new one about 11-fold. At 5,000 units the difference is half a second, and at 50,000
   it would be the difference between seconds and minutes.
3. **The coefficients cost 0.21 s in plain Python and 0.001 s as one array computation.** Small here,
   and the cheapest of the fixes to make.

The honest conclusion is that this step's speed-ups are hygiene, not rescue: worth making because
they are cheap, checked and remove the code that grows fastest, not because 5,000 units needed them.
What 5,000 units does need is in the solve, and the next lesson takes it up.

## The Design Decision: Index Once, Compute Coefficients as Arrays, Keep the Slow Builder

Three ways to build faster were open:

| Option | Gain | Cost |
| --- | --- | --- |
| index each group once (`group`), and use `fast_sum` | removes the scans that grow fastest | a few lines; same model |
| coefficients as one array computation (`risk_table`) | 0.21 s to 0.001 s here | a second implementation of the formula, to be tested against the first |
| build the whole matrix as arrays and hand MathOpt a model proto (lesson 11.1.2) | the most at very large sizes | a rewrite, and the rows' names and order must be rebuilt by hand |

The project takes the first two and not the third: the measurement shows the build is not where the
time goes, so the rewrite would buy nothing a planner sees. And it keeps the old builder, renamed
`build_reference`, as the definition of the model: the fast builder is correct only if it makes
exactly the same model (lesson 11.1.2), and a test checks that on every run.

## The Model

Unchanged. Every set, parameter, variable, objective term and row is the last lesson's; only the code
that writes them changed. Whole, for reference:

```math
\begin{aligned}
\max\; & \sum_{i \in I} \sum_{t \in Y} \text{rr}_{i,t}\, x_{i,t} \\
\text{s.t.}\; & \sum_{t \in Y} x_{i,t} \le 1 && \forall i \in I && \text{(once}_i) \\
& \sum_{i \in I_s} x_{i,t} \le n_s\, o_{s,t} && \forall s \in S,\ t \in Y && \text{(outage}_{s,t}) \\
& \sum_{s \in S_g} o_{s,t} \le O && \forall g \in G,\ t \in Y && \text{(coord}_{g,t}) \\
& \sum_{i \in I_g} w_{k(i)}\, x_{i,t} \le C && \forall g \in G,\ t \in Y && \text{(crews}_{g,t}) \\
& \sum_{i \in I_k} \sum_{t \in E_k} x_{i,t} \le \sigma_k && \forall k \in K,\ E_k \ne \varnothing && \text{(spares}_k) \\
& \sum_{i \in I} c_i\, x_{i,t} + F \sum_{s \in S} o_{s,t} \le B && \forall t \in Y && \text{(budget}_t) \\
& x_{i,t} \in \{0,1\},\ o_{s,t} \in \{0,1\}
\end{aligned}
```

The sets and parameters are those of the crews lesson; at 5,000 units $`B`$, $`O`$, $`C`$ and
$`\sigma_k`$ are ten times the pilot's.

## The Change, File by File

**`model.py`: index once.** A new helper groups units by any key in one pass:

```diff
--- 04/renewal/model.py
+++ 05/renewal/model.py
@@
+def group(units: list[Transformer], key: Callable[[Transformer], str]) -> dict[str, list[Transformer]]:
+    """Units by a key, in one pass, with the keys sorted."""
+    found: dict[str, list[Transformer]] = {}
+    for t in units:
+        found.setdefault(key(t), []).append(t)
+    return dict(sorted(found.items()))
```

and each scan becomes a lookup. The outage block is the clearest case: `members` was rebuilt by
scanning every candidate once per substation and year, and now comes from `by_substation`:

```diff
--- 04/renewal/model.py
+++ 05/renewal/model.py
@@
     if request.has_outages():
-        substations = sorted({t.substation for t in units})
-        out = {(s, y): model.add_binary_variable(name=f"out_{s}_{y}") for s in substations for y in years}
-        for s in substations:
+        out = {(s, y): model.add_binary_variable(name=f"out_{s}_{y}") for s in by_substation for y in years}
+        for s, members in by_substation.items():
             for y in years:
-                members = [t for t in units if t.substation == s]
                 # One row per substation and year: any replacement there needs the outage.
-                model.add_linear_constraint(sum(x[t.tid, y] for t in members) <= len(members) * out[s, y],
-                                            name=f"outage_{s}_{y}")
+                model.add_linear_constraint(mathopt.fast_sum(x[t.tid, y] for t in members)
+                                            <= len(members) * out[s, y], name=f"outage_{s}_{y}")
```

The crews block does the same with `by_region`. Its loop still runs over `REGIONS`, in that order,
and skips a region with no candidates, so the crews rows come out in the reference builder's order;
`by_region` only replaces the scan:

```diff
--- 04/renewal/model.py
+++ 05/renewal/model.py
@@
     if request.crew_weeks is not None:
         for r in REGIONS:
             for y in years:
-                in_region = [t for t in units if t.region == r]
-                if in_region:
+                if r in by_region:
                     model.add_linear_constraint(
-                        sum(KINDS[t.kind].crew_weeks * x[t.tid, y] for t in in_region) <= request.crew_weeks,
-                        name=f"crews_{r}_{y}")
+                        mathopt.fast_sum(KINDS[t.kind].crew_weeks * x[t.tid, y] for t in by_region[r])
+                        <= request.crew_weeks, name=f"crews_{r}_{y}")
```

The spares block does the same with `by_kind`, still looping over `KINDS`, and the budget row stops
scanning every outage variable for each year:

```diff
--- 04/renewal/model.py
+++ 05/renewal/model.py
@@
-        spend = sum(t.cost * x[t.tid, y] for t in units)
-        spend += request.outage_cost * sum(v for (s, year), v in out.items() if year == y)
+        spend = mathopt.fast_sum(t.cost * x[t.tid, y] for t in units)
+        if out:
+            spend += request.outage_cost * mathopt.fast_sum(out[s, y] for s in by_substation)
         budget[y] = model.add_linear_constraint(spend <= request.budget, name=f"budget_{y}")
-    model.maximize(sum(risk_removed(t, y, request) * x[t.tid, y] for t in units for y in years))
+    rr = risk_table(units, request)
+    model.maximize(mathopt.fast_sum(rr[i, j] * x[t.tid, y]
+                                    for i, t in enumerate(units) for j, y in enumerate(years)))
```

Every Python `sum` of model terms becomes `mathopt.fast_sum`. Its documentation in the OR-Tools
source says two things: it is faster than `sum` on expressions, and it returns a linear expression
even for an empty list, where a row built from `sum` of an empty list is the number 0 and fails. The
`if in_region` guards of earlier lessons were written for exactly that case.

**`risk.py`: the coefficients as one array computation.** `risk_table(units, request)` returns a
NumPy array with a row per unit and a column per plan year, entry `[i, j]` equal to
`risk_removed(units[i], year, request)` for the `j`-th plan year `year`: $`\text{rr}_{i,t}`$ of the
model above. Its body is yours to write in the practice. Count the risk years from 2027 as
$`k = 0, 1, \dots`$ and the plan years as $`j = 0, 1, \dots`$; risk year $`k`$ is discounted by
$`(1 + r)^{-k}`$, with $`r`$ the request's `rate`. For each kind, the old unit's PoF at every age it
will reach in the window is one array, `old[i, k]`, its PoF at its 2027 age plus $`k`$; a new unit's
PoF depends only on the kind and years since the start, `new[j, k]`, its PoF at age $`k - j`$ for
$`k \ge j`$ and 0 before the start, the same for every unit of the kind; and `after[j, k]` says whether risk year $`k`$ comes on or
after start year $`j`$. The sum of the formula then becomes two array products, one kind's rows at a
time:

```math
\text{rr}_{i,j} = \text{cof}_i \Big( \sum_k \text{old}_{i,k}\,(1+r)^{-k}\,\text{after}_{j,k}
\; - \; \sum_k \text{new}_{j,k}\,(1+r)^{-k} \Big)
```

The first sum is a matrix product of the discounted `old` with the transpose of `after`; the second
is a row sum of the discounted `new`, the same for every unit of the kind. A kind with no units
leaves no rows to fill. The one helper the body needs evaluates the Weibull curve on whole arrays:

```diff
--- 04/renewal/risk.py
+++ 05/renewal/risk.py
@@
+def _pof(age: np.ndarray, beta: float, eta: float) -> np.ndarray:
+    return 1 - np.exp((age / eta) ** beta - ((age + 1) / eta) ** beta)
```

`_pof` is the Weibull formula of `fleet.weibull_pof` written with `np.exp`, so it takes a whole
array of ages and returns the PoF of each; `weibull_pof` uses `math.exp`, which takes one number.

`risk_removed` stays, unchanged: it is the readable definition, and the test compares the table with
it entry by entry.

**`reference.py`: the last lesson's builder, kept.** The skeleton's stub becomes a copy of the
builder before this lesson, renamed `build_reference`. It is not used by `plan`; it exists so a test
can say "the fast builder makes this model".

## The Tests Hold the Fast Code to the Slow Code

- **the fast builder makes the reference model:** on an 80-unit fleet with every rule on, the two
  models have the same variables in the same order, the same rows with the same bounds and the same
  coefficient on every variable, and objective coefficients equal within $`10^{-9}`$ (the array
  formula adds in a different order than the loop, so the last bits can differ, lesson 10.1.1).
- **the risk table matches the coefficient function** for every candidate and plan year of a
  60-unit fleet.
- **a scaled request grows every limit**, budget, outages, crew-weeks and spares, and leaves the
  years, window and outage cost alone.

```text
step 05 tests on the code of step 04 (before): 22 passed, 3 failed
  FAILED test_scale.py::test_the_fast_builder_makes_the_reference_model (AssertionError)
         assert ['x_T00001_20...09_2028', ...] == []
  FAILED test_scale.py::test_the_risk_table_matches_the_coefficient_function (AssertionError)
         assert False
  FAILED test_scale.py::test_a_scaled_request_grows_every_limit_with_the_fleet (AssertionError)
         assert (3000, 2, 10) == (30000, 20, 100)
step 05 tests on the code of step 05 (after): 25 passed, 0 failed
tests step 05 adds or changes: 3
```

On the last lesson's code the stub `build_reference` returns an empty model, the stub `risk_table`
an array of zeros, and the stub `scaled` the request unchanged; each test fails on the comparison.
No test checks a time. A speed claim in a test would fail on a busy machine for reasons unrelated to
the code; the test checks what the speed-up must not change, and the timing stays in a program.

## What the Step Did to the Code

```text
04       11    251         22     22         143  model.build (23)
05       13    337         27     25         177  reference.build_reference (23)
```

86 code lines more, most of them the reference builder, which is the last lesson's `build` moved to
its own file. The code has two implementations of two things now, the builder and the
coefficients, and that is the price of this step: each pair needs its test, and a change to the model
has to be made in both builders. The project accepts that while the reference is the cheapest proof
that the fast code is right.

**Practice.** This lesson's project practice starts from the code before this step, the whole
package (snapshot `steps/04`). It is graded by the tests in the practice's `tests/` folder and by a
check that `main.py` prints the practice's `expected/report.txt`; the practice's statement gives the
request `main.py` makes and the format of every line it prints. This step's `main.py` plans a tiny
fleet of 25 units, drawn from seed 56, checks the fast builder's model against the reference
builder's, and prints the request scaled for a fleet twice the size.

<!-- practice 1 -->

## Summary

- **Measure before rebuilding.** At 5,000 units the build took under a second and the solve about 18;
  the build's fixes are worth having, and they are not what the fleet needed.
- **A request scales with its fleet in one place**, by a method that names which fields are limits.
- **Index each group once and use `fast_sum`**: the scans that grow fastest go, and empty sums stop
  being a special case.
- **A fast builder is correct only if it makes the reference model**, and a test compares the two on
  every run; the timing stays out of the tests.

## Reference

| Piece | Where |
| --- | --- |
| the request for a larger fleet | `Request.scaled(factor)` |
| groups built once | `model.group(units, key)` |
| a sum that is safe when empty | `mathopt.fast_sum` |
| coefficients as arrays | `risk.risk_table`, checked against `risk.risk_removed` |
| the definition of the model | `reference.build_reference` |

**Further reading:** [MathOpt `expressions.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/expressions.py) (`fast_sum`: faster than `sum` on expressions, and safe on an empty list where `sum` fails in a row); [MathOpt `model.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/model.py) (`linear_constraint_matrix_entries`, which the reference-model test reads, and `export_model`). Both were read from the copy installed in the course's runner image. Lessons 11.1.1 (phases and medians), 11.1.2 (a fast builder checked against a slow one) and 11.1.3 (a generator for large portfolios) are the course's background for this step.

## Challenges

1. Run `scale.py` with a 20,000-unit fleet added to `SIZES`. Predict the reference builder's time from
   the four rows above, then compare.
2. A district has twice the crews of the others. Is `scaled` still the right tool, and what would you
   pass instead?
3. Break the fast builder on purpose: swap two rows' order. Which test fails, and what does its
   message show?

## Design Note: A Second Implementation Is Only as Good as Its Comparison

The fast builder and the array coefficients are each a second implementation of something the
project already had. The rule this module follows: a second implementation goes in only together with
a test that compares it with the first on real-looking input, and the first stays in the code as long
as that test runs. Without the comparison, "faster" is a claim about code that may be computing
something else.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change. The timings you get are your machine's.

**scale.py.** Scales the request, counts the model at four fleet sizes, times both builders and both
coefficient methods, times the phases of a 5,000-unit run, and runs the step's tests before and after
the change (*every section*). *Try:* Set the gap to 1% for the 5,000-unit solve. Predict how the solve
time and the build time change.

- Program: [scale.py](src/scale.py)
- Program: [growth.py](src/growth.py)
- Library: [steps.py](src/steps.py)
