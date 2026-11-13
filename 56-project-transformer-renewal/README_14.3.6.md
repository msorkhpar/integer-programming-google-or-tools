# 14.3.6 Too Slow: a Stronger Formulation and a Rolling Horizon

The whole-fleet plan reached finance, and finance found the tolerance before anyone else did:

> **Request 6.** Your plan is "within 2%" of the best. On 5,000 units that is about $100,000k of
> risk, more than the differences between the scenarios we want to compare next. We need plans
> within 0.1% of the bound, and the analysts need each one within fifteen minutes.

The code before this lesson is snapshot `steps/05`; after it, `steps/06`. The 5,000-unit fleet is
invented (GridCap is fictional).

## At 0.1% the Model Stops Being Fast, and the Gap Says Why

At 2%, the last lesson's 5,000-unit run finished in about 18 seconds. At 0.1% it is
another model to solve. The run below (one run, on the machine described in the last lesson; your
times will differ) gave HiGHS fifteen minutes:

<!-- unverified -->
```text
aggregated gap 0.1%, limit 900 s:  900.6 s, FEASIBLE, plan $5,220,725k, bound $5,226,747k, gap 0.115%, nodes 1513
```

After fifteen minutes the search stopped on its time limit (status `FEASIBLE`: a plan, not a proof
of the target) at a gap of 0.115%, a little short of 0.1%. Nothing is wrong with the model's
correctness; the question is why the solver needs so long to *prove* a plan good, and the first
place to look is the LP relaxation, the bound the search starts from (lesson 6.7.1). `stronger.py`
solves it for both fleet sizes:

```text
500 units:
  aggregated:   2650 variables,    843 rows, LP bound $496,456k
```

```text
5000 units:
  aggregated:  27650 variables,   7978 rows, LP bound $5,518,227k
```

The best plan the fifteen-minute search found removes $5,220,725k, and the search itself proved no
plan removes more than $5,226,747k. The LP bound claims up to $5,518,227k is possible, 5.7% above
that plan. Every point of that 5.7% is space the search must close
by branching and cuts before it can stop at 0.1%.

## The Aggregated Outage Row Lets the LP Buy a Fraction of an Outage

The outage lesson chose the aggregated link, one row per substation and year, and left a note: the
per-unit form allows the same 0-1 plans and may have a tighter LP relaxation. Here is why it does.
Take a substation with $`n_s = 10`$ candidates and replace one of them. The aggregated row reads

```math
x_{1,t} + \dots + x_{10,t} \;\le\; 10\, o_{s,t}
```

and with $`x_{1,t} = 1`$ and the rest 0 the LP is satisfied by $`o_{s,t} = 0.1`$, and by nothing
less: one tenth of an outage, at one tenth of its $300k. The LP relaxation can replace one unit at a substation and pay
$30k for the outage. The per-unit form writes one row for each unit,

```math
x_{i,t} \;\le\; o_{s,t} \qquad \forall i \in I_s
```

and with $`x_{1,t} = 1`$ the LP must set $`o_{s,t} = 1`$ and pay the whole $300k. Each aggregated
row is the sum of the ten per-unit rows, so every LP point the per-unit rows allow, the aggregated
row allows too: the per-unit relaxation is contained in the aggregated one, and its bound can only be
lower or equal (lesson 6.7.1). In integers they agree, because $`o_{s,t}`$ is 0 or 1 either way. The
same comparison is in the big-M lessons: $`n_s`$ is the aggregated row's $`M`$, and the per-unit
row is the same link with $`M = 1`$, the smallest $`M`$ a 0-1 variable allows (lesson 6.2.2).

```text
500 units:
  aggregated:   2650 variables,    843 rows, LP bound $496,456k
  per-unit  :   2650 variables,   2413 rows, LP bound $470,794k
  the per-unit LP bound is 5.17% lower
5000 units:
  aggregated:  27650 variables,   7978 rows, LP bound $5,518,227k
  per-unit  :  27650 variables,  24248 rows, LP bound $5,226,769k
  the per-unit LP bound is 5.28% lower
```

Three times as many rows, the same variables, and an LP bound 5.3% lower at 5,000 units. The
per-unit LP bound, $5,226,769k, is $22k above the bound of $5,226,747k that the aggregated search
proved after fifteen minutes: the per-unit LP starts where the aggregated search ended.

## The Design Decision: Strengthen the Formulation First, Then Decompose If Still Needed

Three levers were on the table, cheapest first:

| Lever | What it changes | Risk |
| --- | --- | --- |
| per-unit outage rows | the formulation: a tighter LP bound, same 0-1 plans | three times the rows |
| a rolling horizon (lesson 11.3.5) | the method: solve a few years at a time, keep the first | a plan with no proof; end effects |
| more solver time or settings | nothing in the model | hides the cause |

A stronger formulation is the cheapest and safest lever: it changes no plan, only how fast the
solver can prove one. The project makes it the default (`link="per-unit"`) and keeps the aggregated
form as an option, because the reference builder and the tests of the scale lesson are written in it.
The rolling horizon is built too, as the fallback if the strong form is still too slow, and measured
against the same bound.

## The Model

The model of the scale lesson with the outage link replaced; everything else is unchanged.

**Sets.** $`I`$ the candidates; $`Y`$ the plan years; $`W`$ the risk window; $`S`$ the substations
with candidates, and $`I_s`$ their candidates; $`G`$ the regions, with $`S_g`$ and $`I_g`$; $`K`$
the kinds, with $`I_k`$ and $`E_k`$.

**Parameters.** $`\text{rr}_{i,t}`$, $`c_i`$, $`B`$, $`F`$, $`O`$, $`w_k`$, $`C`$, $`\sigma_k`$, as
in the crews lesson, scaled with the fleet.

**Variables.** $`x_{i,t} \in \{0,1\}`$ for $`i \in I`$, $`t \in Y`$; $`o_{s,t} \in \{0,1\}`$ for
$`s \in S`$, $`t \in Y`$.

**Objective.**

```math
\max \; \sum_{i \in I} \sum_{t \in Y} \text{rr}_{i,t} \, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in Y} x_{i,t} &\le 1 && \forall i \in I && \text{(once}_i) \\
x_{i,t} &\le o_{s,t} && \forall s \in S,\ i \in I_s,\ t \in Y && \text{(outage}_{i,t}) \quad \leftarrow \text{this lesson} \\
\sum_{s \in S_g} o_{s,t} &\le O && \forall g \in G,\ t \in Y && \text{(coord}_{g,t}) \\
\sum_{i \in I_g} w_{k(i)} \, x_{i,t} &\le C && \forall g \in G,\ t \in Y && \text{(crews}_{g,t}) \\
\sum_{i \in I_k} \sum_{t \in E_k} x_{i,t} &\le \sigma_k && \forall k \in K,\ E_k \ne \varnothing && \text{(spares}_k) \\
\sum_{i \in I} c_i \, x_{i,t} + F \sum_{s \in S} o_{s,t} &\le B && \forall t \in Y && \text{(budget}_t)
\end{aligned}
```

The row $`\text{outage}_{i,t}`$ replaces $`\text{outage}_{s,t}`$; in the code it is named
`outage_T00042_2029`, by unit, where the aggregated row was `outage_S0007_2029`, by substation.

## The Change, File by File

**`model.py`: the link chooses its form.** `relax` turns every variable continuous, for the LP bound:

```diff
--- 05/renewal/model.py
+++ 06/renewal/model.py
@@
+def relax(built: Built) -> Built:
+    """The LP relaxation, in place: every variable continuous within its bounds."""
+    for v in built.model.variables():
+        v.integer = False
+    return built
```

and the outage block writes either form, chosen by the request's `link`. That block is yours to
write in the practice. It stays inside the loops over `by_substation` and the plan years, and the
outage variables, the region limit and the budget row are untouched:

- **`link == "aggregated"`:** the row of the scale lesson, $`\text{outage}_{s,t}`$ with $`n_s`$, named
  `outage_<s>_<year>`, unchanged, so the old model can still be built and measured.
- **Otherwise, the default `"per-unit"`:** the row $`\text{outage}_{i,t}`$ of the model above, one per
  candidate of the substation and plan year, $`x_{i,t} \le o_{s,t}`$, named `outage_<tid>_<year>`.

Each aggregated row is the sum of the per-unit rows of its substation and year (lesson 6.7.1), so
the two allow the same 0-1 plans, and the per-unit rows allow less in the LP relaxation.

**`request.py`: the default becomes the strong form.** The stub field of the last snapshot becomes
real, with the new default; two stubs belong to the next lesson.

```diff
--- 05/renewal/request.py
+++ 06/renewal/request.py
@@
-    link: str = "aggregated"    # Stub: the next lesson adds the per-unit form; this model ignores it.
+    link: str = "per-unit"      # outage rows: "per-unit" (x[i,t] <= out[s,t]) or "aggregated" (one per s, t)
```

**`plan.py`: the LP bound as a function.** Tests and programs ask for it by name:

```diff
--- 05/renewal/plan.py
+++ 06/renewal/plan.py
@@
 def lp_bound(fleet: list[Transformer], request: Request) -> float:
-    """Stub: the next lesson solves the LP relaxation here. Until then, 0."""
-    return 0.0
+    """The LP relaxation's optimum: an upper bound on every plan's risk removed (lesson 6.7.1)."""
+    built = relax(build(fleet, request))
+    return solve_quietly(built.model).objective_value()
```

**`rolling.py`: a rolling horizon.** It follows lesson 11.3.5, and its body is yours to write in the
practice. `rolling(fleet, request, window=3, keep=1)` builds the whole model once, then walks the
plan years from the first, `keep` years at a time:

- **Each window** covers the years $`[a, a + \text{window})`$, cut at the last plan year. Before its
  solve, set the bounds of every replacement and outage variable (both are keyed by a pair whose
  second item is the year): a variable an earlier window decided is fixed to its kept value, one
  after the window's last year is fixed to 0, and the rest are free between 0 and 1.
- **Solve** with the request's gap, as `plan` does. If the solve finds no plan, return that
  result's `Plan` at once.
- **Keep** the values of the first `keep` years of the window, rounded to 0 or 1, as decided. The
  window that reaches the last plan year keeps all its years and ends the walk, and its `Plan` is
  what `rolling` returns.

Budget, crew and spares rows stay in for every year, so what a window decides is counted against
all of them.

A rolling plan's value is exact, but the bound it returns is only the last window's, which says
nothing about the whole plan. It is judged against the best bound known from a full solve.

**`check.py`: every rule, checked apart from the model.** A heuristic plan is not proved by a
solver, so it gets checked by code that does not share the model's rows: `violations` recomputes
budgets, outages, crews and spares from the plan in plain Python and returns one line per broken
rule (the section 12 lesson *Property-Based Tests With Hypothesis* checks plans the same way).

## Measured: the Strong Form Meets the Target; the Rolling Horizon Is Fast and Misses It

`stronger_timing.py --full` ran each method once on the 5,000-unit fleet, with a 0.1% gap, a
fifteen-minute limit for the full solves, and a 0.1% gap in each rolling window. The times are from
one run on the machine of the last lesson and change from run to run; the plan values and bounds are
the solver's:

<!-- unverified -->
```text
aggregated gap 0.1%, limit 900 s:  900.6 s, FEASIBLE, plan $5,220,725k, bound $5,226,747k, gap 0.115%, nodes 1513
per-unit   gap 0.1%, limit 900 s:  537.8 s, OPTIMAL, plan $5,222,473k, bound $5,226,747k, gap 0.082%, nodes 1029
rolling window 3 keep 1:   25.4 s, plan $5,192,922k, 0.647% below the best bound, rules broken 0
rolling window 5 keep 2:   33.2 s, plan $5,208,140k, 0.356% below the best bound, rules broken 0
best bound known $5,226,747k
```

The per-unit form reaches the 0.1% target, status `OPTIMAL` at a gap of 0.082%, in about nine
minutes, inside finance's fifteen; the aggregated form had not reached it when its fifteen minutes
ran out. Both runs end at the same best bound, $5,226,747k: the per-unit LP relaxation starts there,
the aggregated search has to work its way down to it. The plans differ by $1,748k, less than the gap
of either, so the two forms' plans are equally good as far as these runs can tell; what differs is
that one of them is proved within the target.

The rolling horizons are another kind of answer. They finish in 25 and 33 seconds, about 16 to 21
times faster, every plan keeps every rule (`violations` found none), and they land 0.65% and 0.36%
below the best bound. Longer windows do better, as lesson 11.3.5 found: each window ends its view of
the future at its last year, and a longer window sees more. Neither meets finance's 0.1%, so for
this request the rolling horizon is not the answer. It stays in the project as the tool for what it
is good at: a first plan in half a minute while the full solve runs, or a horizon too long to solve
at once.

## The Tests Pin the Bound, the Same Optimum, and the Rolling Plan's Rules

- **per-unit outage rows tighten the LP bound and keep the optimum:** on four units at two
  substations, the per-unit LP bound is lower than the aggregated one, and both forms' exact plans
  have the same value.
- **a rolling plan keeps every rule and most of the value:** on a 30-unit fleet with every rule, a
  rolling plan with two-year windows breaks no rule according to `violations`, and keeps at least
  90% of the full model's value.
- **one window over the whole plan is the full model:** with a window as long as the plan, the
  rolling horizon solves once and its value equals the full model's.
- **the checker names each broken rule and passes a good plan:** a hand-made plan over budget in
  2027, over the north's crews in 2028 and using a large spare that does not exist gets exactly those
  three lines; a good plan gets none.

```text
step 06 tests on the code of step 05 (before): 25 passed, 4 failed
  FAILED test_check.py::test_the_checker_names_each_broken_rule_and_passes_a_good_plan (AssertionError)
         assert [] == ['budget 2027...spares large']
  FAILED test_rolling.py::test_a_rolling_plan_keeps_every_rule_and_most_of_the_value (AssertionError)
         assert ({})
  FAILED test_rolling.py::test_one_window_over_the_whole_plan_is_the_full_model (AssertionError)
         assert 21186.291737181327 < 1e-06
  FAILED test_strong.py::test_per_unit_outage_rows_tighten_the_lp_bound_and_keep_the_optimum (AssertionError)
         assert 0.0 < (0.0 - 1)
step 06 tests on the code of step 06 (after): 29 passed, 0 failed
tests step 06 adds or changes: 4
```

The scale lesson's reference-model test still passes: its request pins `link="aggregated"`, the form
the reference builder writes, so the default's change does not touch it.

## What the Step Did to the Code

```text
05       13    337         27     25         177  reference.build_reference (23)
06       13    415         29     29         216  reference.build_reference (23)
```

78 code lines, most of them `check.py` and `rolling.py`, and one `if` in `build`. The formulation
change itself is four lines; its effect is the largest of any step in the module. That ratio is
typical of formulation work, and it is why the project measured the LP bound before writing a
heuristic.

**Practice.** This lesson's project practice starts from the code before this step, the whole
package (snapshot `steps/05`). It is graded by the tests in the practice's `tests/` folder and by a
check that `main.py` prints the practice's `expected/report.txt`; the practice's statement gives the
request `main.py` makes and the format of every line it prints. This step's `main.py` plans a tiny
fleet of 25 units, drawn from seed 56, and also prints the LP bound under both outage forms, the
checker's verdict on the plan, and a rolling-horizon plan.

<!-- practice 1 -->

## Summary

- **A solve that is slow to prove is first a question about the LP bound.** The aggregated outage
  row let the LP buy a tenth of an outage, and its bound sat more than 5% above every plan.
- **The per-unit link allows the same 0-1 plans and a smaller LP region**, so its bound is lower; at
  5,000 units it starts where the aggregated search ended after fifteen minutes.
- **A rolling horizon is a fallback with no proof.** Judge it against the best bound known, and check
  its plan with code that does not share the model's rows.

## Reference

| Piece | Where |
| --- | --- |
| aggregated link | $`\sum_{i \in I_s} x_{i,t} \le n_s o_{s,t}`$, `link="aggregated"` |
| per-unit link (default) | $`x_{i,t} \le o_{s,t}`$, `link="per-unit"` |
| LP bound | `plan.lp_bound`, via `model.relax` (`Variable.integer = False`) |
| rolling horizon | `rolling.rolling(fleet, request, window, keep)` |
| rules checked apart from the model | `check.violations` |

**Further reading:** [MathOpt `variables.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/variables.py) (the `integer` property with its setter, which `relax` uses, and variable bounds set between solves, as the rolling horizon does); [MathOpt `result.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/result.py) (`dual_bound`: for a MIP solver, a bound from some relaxation of the search, which a time-limited run still reports). Both were read from the copy installed in the course's runner image. Lessons 6.7.1 (comparing formulations by their LP bound), 6.2.2 (what a loose M does to the LP bound) and 11.3.5 (rolling horizons) are the course's background for this step.

## Challenges

1. Between the two forms sits a third: the aggregated row plus the per-unit rows only for the three
   costliest units of each substation. Predict its LP bound against the two above.
2. Write the property test that would have caught a rolling horizon that forgot to fix earlier
   windows' outage variables.
3. Finance relaxes the target to 0.5%. Which of the two forms would you expect to finish first, and
   what would you measure to be sure?

## Design Note: Strengthen Before You Decompose

A decomposition or heuristic changes what the answer means: a plan without a proof, judged against a
bound from elsewhere. A stronger formulation changes nothing about the answer and only makes the
proof cheaper. So the order is fixed: measure the LP bound against the best plan, strengthen the rows
that leave the gap, and decompose only if the strong model is still too slow. Here the first step was
enough, and the rolling horizon stays in the code, tested, for the next request that needs it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**stronger.py.** Builds both outage forms at 500 and 5,000 units and solves their LP relaxations, and
runs the step's tests before and after the change (*The Aggregated Outage Row Lets the LP Buy a
Fraction of an Outage*, *The Tests Pin the Bound, the Same Optimum, and the Rolling Plan's Rules*).
*Try:* Raise the outage cost to $600k. Predict whether the gap between the two LP bounds grows.

**stronger_timing.py.** Solves the 5,000-unit fleet to 0.1% with each form and with two rolling
horizons, and checks the rolling plans' rules (*At 0.1% the Model Stops Being Fast*, *Measured*). It
runs only with `--full`, because it takes about half an hour. *Try:* A window of 10 years and keep 10
is the full model. Predict its time against the per-unit line.

- Program: [stronger.py](src/stronger.py)
- Program: [stronger_timing.py](src/stronger_timing.py)
- Program: [growth.py](src/growth.py)
- Library: [steps.py](src/steps.py)
