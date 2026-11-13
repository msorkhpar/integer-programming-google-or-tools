# 8.2.2 Three Implementations: Auxiliary Objectives in MathOpt, `setObjectiveN` in gurobipy, and a Manual Two-Pass Solve

The board has approved the plan of lesson 8.2.1: NPV within 1% of its best, then the most risk
removed. Two requests come with the approval. Finance adds a third level: if two plans tie on NPV
and risk, fund the one that spends less. And the audit team wants to know that the plan does not
depend on the tool, because GridCap's production service runs on HiGHS while one analyst checks
plans in Gurobi.

There are three ways to write the same hierarchy, and this lesson builds all three on the small
portfolio:

- **MathOpt's prioritized objectives**: the hierarchy stored in the model (lesson 4.3.2 taught the
  API);
- **gurobipy's `setObjectiveN`**: Gurobi's native multi-objective solve;
- **a manual two-pass solve**: one ordinary solve per objective, with a kept row between them.

They should return the same plan. They do, as long as you know where they differ: which priority
goes first, how a minimized objective is written, what a tolerance defaults to, and what a MIP gap
left in an early pass does. GridCap is a fictional utility.

## The Model

The model of lesson 8.2.1 with a third objective. New: the parameters $`s_{i,t}`$, and the
objective $`f_3`$ with its pass and row, marked.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of
project $`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$ and $`\text{rr}_{i,t}`$, the NPV and discounted risk removed
of project $`i`$ started in year $`t`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`s_{i,t} = \sum_{k:\, t+k \in Y} c_{i,k}`$, what it spends inside the plan's
years ($k) $`\leftarrow`$ new; $`B_y`$, the budget of year $`y`$ ($k); $`a_k, r_k \ge 0`$, the
absolute and relative tolerances of objective $`k`$ (here $`r_1 = 0.01`$, every other one 0).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$.

**Objectives, in priority order.**

```math
\begin{aligned}
f_1(x) &= \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} && \text{maximize, first} \\
f_2(x) &= \sum_{i \in P} \sum_{t \in T_i} \text{rr}_{i,t}\, x_{i,t} && \text{maximize, second} \\
f_3(x) &= \sum_{i \in P} \sum_{t \in T_i} s_{i,t}\, x_{i,t} && \text{minimize, third} \quad \leftarrow \text{new}
\end{aligned}
```

**Constraints.** $`X`$, the plans that satisfy every rule of lesson 6.4.2:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

**The passes**, with $`\delta_k = \max(a_k, r_k |\Gamma_k|)`$:

```math
\begin{aligned}
&\text{pass 1:} && \Gamma_1 = \max_{x \in X} f_1(x) \\
&\text{pass 2:} && \Gamma_2 = \max_{x \in X} f_2(x) \;\text{ s.t. }\; f_1(x) \ge \Gamma_1 - \delta_1 && \text{(keep\_npv)} \\
&\text{pass 3:} && \min_{x \in X} f_3(x) \;\text{ s.t. }\; f_1(x) \ge \Gamma_1 - \delta_1,\;\; f_2(x) \ge \Gamma_2 - \delta_2 && \text{(keep\_risk)} \quad \leftarrow \text{new}
\end{aligned}
```

A minimized objective would get the mirror row, $`f_k(x) \le \Gamma_k + \delta_k`$, if a fourth
pass followed it.

## MathOpt Stores the Hierarchy in the Model, and Every Runner Solver Refuses It

In MathOpt the whole question lives in the model: NPV is the primary objective (priority 0), and
risk and spend are auxiliary objectives with priorities 1 and 2. The lowest number goes first. The
1% is a per-objective solve parameter, keyed by the objective object (lesson 4.3.2):

```python
model.maximize(sm.objective("npv"))                                    # primary objective, priority 0
risk = add_auxiliary(model, sm.objective("risk"), priority=1, is_maximize=True, name="risk")
spend = add_auxiliary(model, sm.objective("spend"), priority=2, is_maximize=False, name="spend")
params = mathopt.ModelSolveParameters(objective_parameters={
    model.objective: mathopt.ObjectiveParameters(objective_degradation_relative_tolerance=0.01)})
```

```text
primary  priority 0  max  terms 80
risk     priority 1  max  terms 80
spend    priority 2  min  terms 80
```

Two auxiliary objectives, so they are added with `add_auxiliary`, which sets each term one at a time.
In OR-Tools 9.15, `add_auxiliary_objective(expr=...)` erases the terms of every auxiliary objective
already in the model, and nothing raises (lesson 4.3.2 shows it). Read the objectives back, as above:
each has its 80 terms, one per start variable.

The model is complete and correct. No solver in the runner will solve it:

```python
try:
    with quiet():
        mathopt.solve(model, mathopt.SolverType.HIGHS, model_params=params)
except Exception as error:                     # OR-Tools 9.15 hides the solver's reason on __context__
    print(f"HiGHS refuses: {error.__context__ or error}")
```

```text
HiGHS refuses: Highs does not support multiple objectives [INVALID_ARGUMENT]
```

As lesson 4.2.4 shows, in OR-Tools 9.15 a solver's refusal reaches Python as an `AttributeError`
raised by MathOpt's own error handling, and the solver's message is on the exception's
`__context__`; the program prints it from there.

Lesson 4.3.2 showed that SCIP and CP-SAT refuse it the same way. MathOpt can pass auxiliary
objectives to Gurobi, but in OR-Tools 9.15 MathOpt cannot load the runner's Gurobi 13 library
(lesson 4.3.2), so this course shows no result from MathOpt with Gurobi.

What does run is lesson 4.3.2's `solve_in_order`, copied into this module as `in_order.py`. It reads
the objectives and tolerances from the model and the parameters, and solves them one at a time on a
copy of the model:

```python
reached, values = solve_in_order(model, params)
```

```text
in order: {'primary': 24260.0, 'risk': 12750.5, 'spend': 41780.0}
plan: NPV $24,019k  risk removed $12,750.5k  spend $41,780k  projects 27
```

The values are each pass's best, $`\Gamma_1, \Gamma_2, \Gamma_3`$: NPV $24,260k in pass 1, then
risk $12,750.5k, then spend $41,780k. The plan is lesson 8.2.1's 1% plan; the spend pass did not
change it. The model keeps the question in one place, and the day a solver that accepts auxiliary
objectives is available, the same model and parameters go to `mathopt.solve` unchanged.

## gurobipy Solves the Hierarchy Natively, and Its Priorities Run the Other Way

Gurobi takes several objectives in one model with `Model.setObjectiveN(expr, index, priority,
weight, abstol, reltol, name)`. The same three levels:

```python
m.ModelSense = GRB.MAXIMIZE                                     # one sense for every objective
m.setObjectiveN(gm.objective["npv"], index=0, priority=2, weight=1, reltol=0.01, name="npv")
m.setObjectiveN(gm.objective["risk"], index=1, priority=1, weight=1, name="risk")
m.setObjectiveN(gm.objective["spend"], index=2, priority=0, weight=-1, name="spend")  # -1: minimize
m.Params.MIPGap = 0.0
m.optimize()
```

Three things are different from MathOpt, and each one is a way to port a model wrong:

- **The highest priority goes first.** Gurobi's documentation: one pass per distinct priority, in
  decreasing order. NPV has priority 2 here, spend 0. MathOpt's numbers run the other way, lowest
  first. Copy MathOpt's priorities 0, 1, 2 into `setObjectiveN` and spend is optimized first.
- **One sense for the whole model.** `ModelSense` applies to every objective, so a minimized
  objective in a maximized model gets `weight=-1`: minimizing spend is maximizing −spend. In MathOpt
  each objective has its own `is_maximize`.
- **A small default absolute tolerance.** `abstol` defaults to 1e-6 and `reltol` to 0. MathOpt's
  default for both is "not set", which allows no loss.

The first one is the costly one. The same program, with MathOpt's numbers copied unchanged (NPV 0,
risk 1, spend 2):

```text
priorities copied from MathOpt: npv 2,684  risk 956.8  spend 7,630  projects 4
```

Spend went first, so the plan is the must-do projects alone, the least money that can be spent:
the same four projects lesson 4.3.2 found when it put spend first on purpose. Nothing warns: the
model is valid, it simply asks the other question.

The tolerances themselves mean the same: Gurobi's documentation says the looser of the two applies
when both are set, as in MathOpt. The values are read per objective, by pointing the `ObjNumber`
parameter at one and reading its `ObjN...` attributes:

```python
for k in range(m.NumObj):
    m.Params.ObjNumber = k                       # which objective the ObjN* attributes read
    print(f"  {m.ObjNName:6} priority {m.ObjNPriority}  weight {m.ObjNWeight:+.0f}  reltol {m.ObjNRelTol:g}"
          f"  abstol {m.ObjNAbsTol:g}  value {m.ObjNVal:,.1f}")
```

```text
status 2 (2 is OPTIMAL), objectives 3
  npv    priority 2  weight +1  reltol 0.01  abstol 1e-06  value 24,019.0
  risk   priority 1  weight +1  reltol 0  abstol 1e-06  value 12,750.5
  spend  priority 0  weight -1  reltol 0  abstol 1e-06  value 41,780.0
projects 27
```

`ObjNVal` is each objective's value in the plan Gurobi returns, so NPV reads $24,019k here, where
`solve_in_order` reported pass 1's best, $24,260k. The plan's three values are the same as MathOpt's.

The program runs on the size-limited Gurobi license mounted read-only in the course's runner; the
model has 80 variables and 49 rows, well inside the limit. Section 5 covers gurobipy, licenses and
the limit. `quiet_env` sets `OutputFlag=0` before the environment starts, so no license banner or log
reaches the output; without a license, the program stops with Gurobi's message, with user and host
names masked.

**`reltol` applies to MIPs only.** The `setObjectiveN` reference says the relative tolerance is
ignored for LP models, where Gurobi degrades an objective a different way (by fixing variables from
their reduced costs, with `abstol` as the allowed violation). The same levels on the LP relaxation
(every $`x_{i,t}`$ continuous in $`[0, 1]`$), with three relative tolerances:

```python
for reltol in (0.0, 0.01, 0.20):                  # the same objectives on the LP relaxation
    lp = build(env, small)
    lp.model.update()                               # the variables exist before their type changes
    for var in lp.model.getVars():
        var.VType = GRB.CONTINUOUS                  # 0 <= x <= 1, no longer binary
```

```text
LP relaxation, npv reltol  0.0: npv 26,587.4  risk 9,698.8
LP relaxation, npv reltol 0.01: npv 26,587.4  risk 9,698.8
LP relaxation, npv reltol  0.2: npv 26,587.4  risk 9,698.8
```

Even 20% changes nothing. A relative tolerance on a pure LP needs another implementation, such as the
manual passes below, where the kept row works the same for an LP as for a MIP.

<!-- practice 1 -->

## A Manual Two-Pass Solve Is a Loop of Solve, Read, Keep

The third way needs no multi-objective support at all: any MIP solver, HiGHS here, solves each pass
as an ordinary model. `lexicographic.py` is the whole method:

```python
def allowed_loss(best: float, level: Level) -> float:
    """The larger of the two tolerances: meeting either one is enough."""
    return max(level.abs_tol, level.rel_tol * abs(best))
```

```python
kept, outcome = [], Outcome(plan={})
for level in levels:
    expr = sm.objective(level.name)
    sm.model.set_linear_objective(expr, is_maximize=level.maximize)
    result = solve(sm.model, gap)                                   # pass k
    best = result.objective_value()
    loss = allowed_loss(best, level)
    if level.maximize:
        row, bound = expr >= best - loss - TOL, best - loss
    else:
        row, bound = expr <= best + loss + TOL, best + loss
    kept.append(sm.model.add_linear_constraint(row, name=f"keep_{level.name}"))
    outcome.best[level.name], outcome.floor[level.name] = best, bound
outcome.plan = plan_of(sm, result)
for row in kept:                                                    # give the model back as it was
    sm.model.delete_linear_constraint(row)
```

Each line is a piece of the pass formulation:

- **Solve.** `set_linear_objective` replaces the model's objective with this level's, and `solve`
  runs HiGHS to a relative gap of 0, so `best` is the proven optimum $`\Gamma_k`$.
- **Read.** `allowed_loss` is $`\delta_k = \max(a_k, r_k |\Gamma_k|)`$; `abs` keeps the loss
  positive when $`\Gamma_k`$ is negative.
- **Keep.** The row's direction follows the sense: a maximized objective may fall by the loss, a
  minimized one may rise by it. The row is loosened by one more term, `TOL` $`= 10^{-6}`$, explained
  next.
- **Give the model back.** The kept rows are deleted at the end. The same `StartModel` then serves
  the next question; without the deletes, a later run would still carry an earlier run's floors.

**Why the kept row needs a numerical slack.** With no tolerance, $`\delta_k = 0`$ and the row reads
$`f_k(x) \ge \Gamma_k`$, where $`\Gamma_k`$ is the value the solver reported. Pass $`k`$'s own plan
should meet that row with equality, but in floating point the reported value and the value of the
returned plan can differ in the last digits. `kept_row.py` solves the risk pass on GridCap small and
compares the two:

```python
best = result.objective_value()
own = mathopt.evaluate_expression(risk, result.variable_values())
```

```text
pass 1 reports best risk removed 16086.118894732655
pass 1's own plan removes        16086.118894732652
the plan sits 3.6e-12 below best, so the row risk >= best excludes it by that much
pass 2 with the exact row: OPTIMAL
```

The plan that proved the optimum violates the exact row by $`3.6 \times 10^{-12}`$. HiGHS still
solved pass 2 here, but that rests on how strictly the solver checks a row, which is not the
model's business. `solve_levels` therefore subtracts `TOL` from a floor (adds it to a ceiling), so
the plan pass $`k`$ returned always meets the row with room to spare. $`10^{-6}`$ $k is a thousandth
of a dollar, far below any tolerance a planner sets; `outcome.floor` records the bound without it.
Lesson 8.3.2's `best_of` adds the same `TOL` for the same reason.

Where `solve_in_order` copies the model through `export_model()`, this version edits the caller's
model and undoes the edits. Both are sound; the copy is safer when other code holds the model, the
in-place edit is cheaper for a sweep of many tolerances on one model.

Now the three implementations on four questions, each compared with Gurobi's plan:

```python
plans = {"MathOpt in order": mathopt_in_order(*tol), "gurobipy setObjectiveN": gurobi_native(*tol),
         "manual two-pass": manual(*tol)}
```

```text
question            implementation        NPV      risk  same plan
NPV exact, risk     MathOpt in order       24,260  10,576.6  yes
NPV exact, risk     gurobipy setObjectiveN 24,260  10,576.6  yes
NPV exact, risk     manual two-pass        24,260  10,576.6  yes
NPV 1%, risk        MathOpt in order       24,019  12,750.5  yes
NPV 1%, risk        gurobipy setObjectiveN 24,019  12,750.5  yes
NPV 1%, risk        manual two-pass        24,019  12,750.5  yes
NPV $100k, risk     MathOpt in order       24,162  11,049.4  yes
NPV $100k, risk     gurobipy setObjectiveN 24,162  11,049.4  yes
NPV $100k, risk     manual two-pass        24,162  11,049.4  yes
NPV 5%, risk        MathOpt in order       23,104  14,837.1  yes
NPV 5%, risk        gurobipy setObjectiveN 23,104  14,837.1  yes
NPV 5%, risk        manual two-pass        23,104  14,837.1  yes
```

All three return the same plan for every question, project for project, which answers the audit
team. "Same plan" compares the start years of every project, not only the objective values. It
could have failed even with correct code: when several plans tie on the last objective, two solvers
may return different ones. That did not happen here, but a test of an implementation should compare
objective values first and plans only when ties are ruled out.

## Solve Each Pass to a Zero Gap, or the Gap Becomes a Tolerance

Every implementation above solved each pass to a relative gap of 0. A MIP solver is often told to
stop earlier, once the best plan found is within a relative gap of the best bound (lesson 3.4.1
explains the gap), and Gurobi's default gap is not 0 either. In a lexicographic solve that matters, because the kept row is built
from what pass 1 returned. With no tolerance at all, the manual passes with pass 1 stopped at a 5%
gap:

```python
sm.model.set_linear_objective(npv, is_maximize=True)
first = solve(sm.model, gap)                                   # pass 1 stops within `gap`
best, bound = first.objective_value(), first.termination.objective_bounds.dual_bound
keep = sm.model.add_linear_constraint(npv >= best, name="keep_npv")
```

```text
manual two-pass, HiGHS, no tolerance on NPV
  pass-1 gap   0%: kept NPV >= 24,260 (bound 24,260) -> NPV 24,260  risk removed 10,576.6
  pass-1 gap   5%: kept NPV >= 24,071 (bound 24,652) -> NPV 24,098  risk removed 12,347.9
```

At a 5% gap, pass 1 stopped with a plan worth $24,071k, $189k below the optimum, and the row kept NPV
above that instead of above $24,260k. Pass 2 then gave up $162k of NPV for $1,771.3k more risk
removed, a trade nobody asked for. Pass 2 even found a plan with more NPV than pass 1 returned:
$24,098k. The gap acted as a tolerance of unknown size, set by when the solver happened to stop. The row
itself never makes pass 2 infeasible, because the plan pass 1 returned always meets it; the harm is
the opposite, a floor set too low. (In floating point, it is the `TOL` of the previous section that
guarantees "always meets it". This program's row has none, to show the gap alone, and pass 2 still
solved at both gaps.)

Gurobi does the same inside `setObjectiveN`. Its documentation says the value later passes must
respect is computed from the pass's best plan, its best bound and the MIP gaps, and only then relaxed
by `reltol` and `abstol`. So `MIPGap` loosens every pass:

```text
gurobipy setObjectiveN, no tolerance on NPV (reltol 0)
  (Gurobi's default MIPGap: 0.0001)
  MIPGap 0     : NPV 24,260  risk removed 10,576.6
  MIPGap 0.0001: NPV 24,260  risk removed 10,576.6
  MIPGap 0.01  : NPV 24,196  risk removed 10,919.1
  MIPGap 0.02  : NPV 24,127  risk removed 11,896.7
```

At the default gap the plan is the exact one; at 1% and 2% the NPV pass gives up $64k and $133k
with no tolerance set. The rule for all three implementations: **solve every pass but the last to a
gap of 0 or very close to it, and state the tolerance on purpose**. If a pass cannot reach a zero
gap in the time available, the row can be built from the pass's best bound instead of its plan. For a
maximized objective the bound is at least the optimum, so the floor never falls below the optimum
minus the tolerance you chose. The price: when the remaining gap is larger than the tolerance, the
floor can sit above every plan, and the next pass is infeasible. Neither choice is free, so the run's
record should say which one was made.

<!-- practice 2 -->

## Summary

- **MathOpt stores the hierarchy in the model, and every runner solver refuses it.** Add auxiliary
  objectives term by term (in OR-Tools 9.15, `add_auxiliary_objective(expr=...)` erases the terms of
  the auxiliary objectives already in the model), and solve them in order; no MathOpt-with-Gurobi
  result runs here.
- **gurobipy solves the hierarchy natively, and its priorities run the other way.** Highest priority
  first, one `ModelSense` with `weight=-1` for a minimized objective, `abstol` 1e-6 by default, and
  `reltol` ignored for LPs.
- **A manual two-pass solve is a loop of solve, read, keep.** It runs on any MIP solver and gave the
  same plan as `setObjectiveN` on every question tried. Loosen each kept row by a tiny `TOL`, because
  a solver can report its best a hair above its own plan's value.
- **Solve each pass to a zero gap, or the gap becomes a tolerance.** A 5% gap in HiGHS's pass 1, or
  a 1% `MIPGap` in Gurobi, gave up NPV that no tolerance allowed.

## Reference

| | MathOpt prioritized objectives | gurobipy `setObjectiveN` | manual passes |
| --- | --- | --- | --- |
| order | lowest `priority` first | highest `priority` first | the order of your loop |
| first objective | `model.maximize(expr)` (priority 0) | `setObjectiveN(expr, index=0, priority=...)` | pass 1's objective |
| a later objective | `add_auxiliary_objective(priority=..., is_maximize=...)`, terms one at a time (9.15) | `setObjectiveN(expr, index=k, priority=...)` | the next pass's objective |
| a minimized objective | `is_maximize=False` | `weight=-1` under `ModelSense = GRB.MAXIMIZE` | `is_maximize=False`, row $`\le \Gamma + \delta`$ |
| relative tolerance | `ObjectiveParameters(objective_degradation_relative_tolerance=r)` | `reltol=r` (MIPs only) | $`r \cdot \lvert\Gamma\rvert`$ |
| absolute tolerance | `objective_degradation_absolute_tolerance=a` (unset: 0) | `abstol=a` (default 1e-6) | $`a`$ |
| both set | the larger loss | the looser value | $`\max(a, r\lvert\Gamma\rvert)`$ |
| read a value | `primal_solution.auxiliary_objective_values[aux]` | `Params.ObjNumber = k`, then `ObjNVal` | each pass's `objective_value()` |
| runs in the runner | no (HiGHS, SCIP, CP-SAT refuse; MathOpt in OR-Tools 9.15 cannot load the runner's Gurobi 13 library) | yes, size-limited license | yes, any MIP solver |
| numerical slack on a kept row | none to set | none to set | `TOL` $`= 10^{-6}`$, so pass $`k`$'s own plan meets its row |

**Further reading.** OR-Tools,
[`hierarchical_objectives.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/hierarchical_objectives.py),
the sample lesson 4.3.2 adapts. OR-Tools,
[`objectives.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/objectives.py)
(priorities, `AuxiliaryObjective.clear`) and
[`model_parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py)
(`ObjectiveParameters`). OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt):
hierarchical objectives in the feature list. Gurobi,
[Multiple Objectives](https://docs.gurobi.com/projects/optimizer/en/current/features/multiobjective.html):
priorities in decreasing order, negative weights for a minimized objective, the MIP and LP rules for
degradation, and per-pass environments. Gurobi,
[Python `Model` reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html):
`setObjectiveN` and its defaults. Gurobi,
[Multi-objective attributes](https://docs.gurobi.com/projects/optimizer/en/13.0/reference/attributes/multiobjective.html):
`ObjNRelTol`, `ObjNAbsTol`, `ObjNVal` and `NumObj`.

## Challenges

1. Gurobi's default `abstol` is 1e-6, MathOpt's is no loss at all. On what kind of objective could
   that difference ever change the plan, and how would you make the manual passes match Gurobi?
2. Add a fourth level to the manual passes: the most projects started, after spend. Which row does
   pass 3 leave behind for pass 4, and in which direction?
3. Pass 1 must stop after ten seconds on GridCap large. Write the kept row from the best bound
   instead of the incumbent, and say what it guarantees and what it can cost.

## Design Note: Keep the Question in One Place, and Let the Solve Be Swappable

The three implementations share one question: an ordered list of objectives, each with a sense and
two tolerances. Write that list once, as data (`Level` here, the auxiliary objectives and
`ObjectiveParameters` in MathOpt), and let one function turn it into solves. Then the service can use
the manual passes on HiGHS, an analyst can check them with `setObjectiveN`, and a test can compare
the two on every scenario, as `three_ways.py` does. The test is cheap, and it is what catches a port
that copied MathOpt's priority numbers into Gurobi.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**mathopt_aux.py.** The three levels as MathOpt prioritized objectives, read back, refused by HiGHS,
and solved in order (*MathOpt Stores the Hierarchy in the Model*). *Try:* Add the spend objective
with `model.add_minimization_objective` instead of `add_auxiliary`, and predict what the risk
objective's term count reads.

- Program: [mathopt_aux.py](src/mathopt_aux.py)

**gurobi_multiobj.py.** The same levels with `setObjectiveN`, `reltol` on the LP relaxation, and
MathOpt's priority numbers copied unchanged (*gurobipy Solves the Hierarchy Natively*). *Try:* Swap the priorities of NPV and spend, and predict
the spend value.

- Program: [gurobi_multiobj.py](src/gurobi_multiobj.py)

**kept_row.py.** Solves the risk pass and compares the reported best with the value of the plan
the solver returned, then runs pass 2 with the exact row (*A Manual Two-Pass Solve*). *Try:* Do the
same for the NPV pass, and predict whether its two values differ.

- Program: [kept_row.py](src/kept_row.py)

**three_ways.py.** MathOpt in order, `setObjectiveN` and the manual passes on four questions (*A
Manual Two-Pass Solve*). *Try:* Add a question with both tolerances set, 1% and $300k, and predict
which one decides.

- Program: [three_ways.py](src/three_ways.py)

**gap_leak.py.** A gap left in pass 1, by hand on HiGHS and inside Gurobi (*Solve Each Pass to a Zero
Gap*). *Try:* Build the kept row from `bound` instead of `best` at a 5% gap, and predict the NPV.

- Program: [gap_leak.py](src/gap_leak.py)

**in_order.py** solves MathOpt's prioritized objectives one at a time (lesson 4.3.2); **gurobi_model.py**
is the model in gurobipy.

- Library: [in_order.py](src/in_order.py)
- Library: [gurobi_model.py](src/gurobi_model.py)
- Library: [lexicographic.py](src/lexicographic.py)
- Library: [lex_model.py](src/lex_model.py)
