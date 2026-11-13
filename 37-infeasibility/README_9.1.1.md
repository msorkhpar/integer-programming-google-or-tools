# 9.1.1 Infeasible, Unbounded, or the Solver Can't Tell

It is Budget Lock week at GridCap (lesson 7.1.3): one scenario is about to become the plan of record.
Finance has locked the 2028 budget at $6,000k, a contractor change leaves transmission 12
crew-months in each of 2030 and 2031, and the board wants P032 started in 2028 and P023 in the plan.
The run comes back with no plan. In the same week a developer adds interest on carried-over money
to another model, and that run also comes back with no plan. HiGHS gives the two runs different
answers, and one of those answers is "infeasible or unbounded". Before anyone looks for the rule to
blame, someone has to work out which of the two problems each model has.
This lesson reads what a solver says when a model has no optimal plan, measures what five solvers
say on the same small models, and settles the ambiguous answer.
Section 9 uses this Budget Lock scenario throughout. GridCap is a fictional utility; none of its
numbers are real.

## The Model

The model is the timing model of lesson 6.4.1 with crew rows (lesson 6.2.1, held hard as in lesson 6.7.2) and the rule families
planners touch at Budget Lock. `lock_model.build(portfolio, scenario)` builds it in MathOpt and
gives every row a name. The names are the labels below, and the rest of the section talks about
rows only by these names.

**Sets.** $`P`$ the projects; $`Y = \{2027, \dots, 2031\}`$ the years; $`T_i \subseteq Y`$ the
start years project $`i`$ may use (its window); $`M \subseteq P`$ the must-do projects;
$`\mathcal{G}`$ the alternative groups, each a set of projects; $`C \subseteq P`$ the child
projects, with parent $`p(c)`$ and lag $`L_c`$ years; $`Q`$ the programs (transmission,
distribution, vegetation), with $`q(i)`$ the program of project $`i`$; $`R`$ the regions, with
$`r(i)`$ the region of project $`i`$; $`F \subseteq P`$ the projects the scenario forces in, and
$`F_1 \subseteq F`$ those forced into one year $`f_i`$; $`D \subseteq P`$ the projects it forces
out.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what it spends in its $`k`$-th year of work, $`k = 0, \dots, d_i - 1`$, where
$`d_i`$ is its number of years of work ($k; $`c_{i,k} = 0`$ for any other $`k`$);
$`\text{capex}_i = \sum_k c_{i,k}`$; $`B_y`$, the budget of year $`y`$ ($k);
$`m_i`$, the crew-months project $`i`$ needs in each year of work; $`K_{q,y}`$, the crew-months
program $`q`$ has in year $`y`$; $`\text{floor}_r`$, the least region $`r`$ must receive over
the plan ($k).

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
\sum_{i \in P} \sum_{t \in T_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{i:\, q(i) = q} \ \sum_{t \in T_i,\ t \le y < t + d_i} m_i\, x_{i,t} &\le K_{q,y} && \forall q \in Q,\ y \in Y && \text{(crews}_{q,y}) \\
\sum_{i:\, r(i) = r} \ \sum_{t \in T_i} \text{capex}_i\, x_{i,t} &\ge \text{floor}_r && \forall r \in R && \text{(floor}_r) \\
\sum_{t \in T_i} x_{i,t} &\ge 1 && \forall i \in F \setminus F_1 && \text{(force}_i) \\
x_{i,f_i} &\ge 1 && \forall i \in F_1 && \text{(force}_{i,f_i}) \\
\sum_{t \in T_i} x_{i,t} &\le 0 && \forall i \in D && \text{(drop}_i)
\end{aligned}
```

| Label | Row name in the code |
| --- | --- |
| once$`_i`$, must$`_i`$, alt$`_g`$ | `once_P001`, `must_P017`, `alt_G001` |
| after$`_{c,t}`$ | `after_P023_2029` |
| budget$`_y`$, crews$`_{q,y}`$, floor$`_r`$ | `budget_2028`, `crews_transmission_2030`, `floor_Coast` |
| force$`_i`$, force$`_{i,f_i}`$, drop$`_i`$ | `force_P023`, `force_P032_2028`, `drop_P040` |

A crew row exists only for a program and year that has crew-months in the data, and only when some
project could use them. The Budget Lock scenario (`lock_model.LOCK`) changes data only: $`B_{2028} =
6{,}000`$, $`K_{\text{transmission},2030} = K_{\text{transmission},2031} = 12`$, $`F = \{\text{P023},
\text{P032}\}`$ with $`F_1 = \{\text{P032}\}`$ and $`f_{\text{P032}} = 2028`$, and $`D = \emptyset`$. On
GridCap small, without the scenario, the best plan is worth $22,741k. With it, the model has 80
variables and 70 rows:

```text
base scenario: OPTIMAL, NPV $22,741k; budget lock: 80 variables, 70 rows
```

## A Termination Reason Is a Claim About the Model, Not About Your Plan

Lesson 4.2.2 read `result.termination`: a **reason** (how the solve ended), a **limit** (which
limit stopped it, if one did), and a `problem_status` with the solver's claims about the
**primal** problem (your model) and the **dual** problem (lesson 2.3.1; for a MIP, the dual of its
LP relaxation). When there is no optimal plan, the reason is one of four:

| `TerminationReason` | What the solver claims |
| --- | --- |
| `INFEASIBLE` | no plan meets every row and bound: the primal problem has no feasible point |
| `UNBOUNDED` | there are plans, and the objective can be made as good as you like (a **ray**: a direction you can move in forever, staying feasible and improving) |
| `INFEASIBLE_OR_UNBOUNDED` | one of the two, and the solver does not know which |
| `NO_SOLUTION_FOUND` | a limit stopped the search before any plan was found: nothing proven either way |

`problem_status` says the same thing in pieces. `primal_status` and `dual_status` are each
`FEASIBLE`, `INFEASIBLE` or `UNDETERMINED`, and `primal_or_dual_infeasible` is `True` when the
solver knows that one of the two is infeasible but not which. Lesson 2.2.3 showed the geometry: an
infeasible LP has an empty region, and an unbounded LP has a region that stretches forever in an
improving direction.

The two answers ask for different work. `INFEASIBLE` is about the data and the rules: some set of
them cannot hold together, and the rest of this module finds which. `UNBOUNDED` is almost always a
modeling bug, because no real plan is worth infinite money. Usually a bound or a row is missing.
Treat `INFEASIBLE_OR_UNBOUNDED` as an unanswered question, not as either of the two.

## Five Solvers Give Three Answers for the Same Unbounded Model

`status_zoo.py` builds three two-variable models, maximizing $`x + y`$ over $`x, y \ge 0`$.
"infeasible" has rows $`x + y \le 4`$ and $`x + y \ge 6`$. "unbounded" has the single row
$`x - y \le 2`$, so $`x = y = t`$ is feasible for every $`t`$. "both" has $`x - y \ge 1`$ and
$`x - y \le -1`$, so the primal is infeasible, and so is its dual. Each model is solved as an LP and
as a MIP, by every solver that takes it, with **presolve** (the pass that simplifies a model before
the main algorithm, lesson 3.3.2) on and off:

```python
def tiny(kind: str, integer: bool) -> mathopt.Model:
    """max x + y over x, y >= 0 with the rows of one kind of model."""
    m = mathopt.Model(name=kind)
    x = m.add_variable(lb=0, is_integer=integer, name="x")
    y = m.add_variable(lb=0, is_integer=integer, name="y")
```

```python
    params = mathopt.SolveParameters() if presolve else mathopt.SolveParameters(presolve=mathopt.Emphasis.OFF)
```

```text
model      type solver  presolve on               presolve off
infeasible LP   GLOP    INFEASIBLE                INFEASIBLE
infeasible LP   PDLP    INFEASIBLE                error: parameter presolve not supported for PDLP [INVALID_ARGUMENT]
infeasible LP   HIGHS   INFEASIBLE                INFEASIBLE
infeasible LP   GSCIP   INFEASIBLE                INFEASIBLE
infeasible LP   CP_SAT  INFEASIBLE                INFEASIBLE
infeasible MIP  HIGHS   INFEASIBLE                INFEASIBLE
infeasible MIP  GSCIP   INFEASIBLE                INFEASIBLE
infeasible MIP  CP_SAT  INFEASIBLE                INFEASIBLE
unbounded  LP   GLOP    INFEASIBLE_OR_UNBOUNDED   UNBOUNDED
unbounded  LP   PDLP    INFEASIBLE_OR_UNBOUNDED   error: parameter presolve not supported for PDLP [INVALID_ARGUMENT]
unbounded  LP   HIGHS   UNBOUNDED                 UNBOUNDED
unbounded  LP   GSCIP   UNBOUNDED                 error: Expected no NaN or inf but found value: inf ...
unbounded  LP   CP_SAT  INFEASIBLE_OR_UNBOUNDED   INFEASIBLE_OR_UNBOUNDED
unbounded  MIP  HIGHS   INFEASIBLE_OR_UNBOUNDED   UNBOUNDED
unbounded  MIP  GSCIP   UNBOUNDED                 error: Expected no NaN or inf but found value: inf ...
unbounded  MIP  CP_SAT  INFEASIBLE_OR_UNBOUNDED   INFEASIBLE_OR_UNBOUNDED
both       LP   GLOP    INFEASIBLE_OR_UNBOUNDED   INFEASIBLE
both       LP   PDLP    INFEASIBLE                error: parameter presolve not supported for PDLP [INVALID_ARGUMENT]
both       LP   HIGHS   INFEASIBLE                INFEASIBLE
both       LP   GSCIP   INFEASIBLE                INFEASIBLE
both       LP   CP_SAT  INFEASIBLE                INFEASIBLE
both       MIP  HIGHS   INFEASIBLE                INFEASIBLE
both       MIP  GSCIP   INFEASIBLE                INFEASIBLE
both       MIP  CP_SAT  INFEASIBLE                INFEASIBLE
```

An error is shown up to the end of its first clause; "..." marks a message that goes on. Read it by rows:

- **Every solver called the infeasible model `INFEASIBLE`**, as an LP and as a MIP, with
  presolve on or off. On these models that answer was never wrong, and never hedged.
- **The unbounded model got three different answers.** HiGHS and SCIP said `UNBOUNDED` for the LP.
  GLOP and PDLP said `INFEASIBLE_OR_UNBOUNDED`, and so did CP-SAT, which also gives no definite
  answer with presolve off. HiGHS said `UNBOUNDED` for the LP but `INFEASIBLE_OR_UNBOUNDED` for
  the same model with integer variables.
- **Switching presolve off settled it for GLOP and for HiGHS's MIP**, both of which then said
  `UNBOUNDED`. The other columns show that "presolve off" is no general cure. PDLP refuses the
  parameter. SCIP with presolve off fails in OR-Tools while reading SCIP's answer, because the
  objective value of an unbounded solve is infinite. OR-Tools 9.15 raises that as an
  `AttributeError`, and the solver's own message, the one the table prints, is on the error's
  `__context__` (lesson 4.2.4). CP-SAT's answer does not change.
- **"both" shows why a solver may have to hedge.** Its primal and its dual are both infeasible. A
  solver that learns only "primal or dual is infeasible" cannot say which. GLOP with presolve said
  `INFEASIBLE_OR_UNBOUNDED`, and without presolve it said `INFEASIBLE`.

Why does presolve cause this? Some presolve steps use the objective: they fix a variable, or drop
a row, because no optimal plan could need it. Such a step is safe only when an optimal plan exists.
When the reduced model then turns out to have no plan, or to be unbounded, the solver cannot be
sure the original model was the same. Switching presolve off, or only those steps, removes the
doubt at the cost of a slower solve.

## Gurobi Says INF_OR_UNBD Until Dual Reductions Are Off

Gurobi has a status for this case, `INF_OR_UNBD` (status 4), and a parameter that switches off
exactly the presolve steps that use the objective in this way: **dual reductions**. Gurobi's
parameter reference says to set `DualReductions` to 0 to get a definite answer after
`INF_OR_UNBD`. `gurobi_status.py` solves the same three models in gurobipy, on the size-limited
license mounted in the runner, with the default settings and then with dual reductions off:

```python
        strict.Params.DualReductions = 0                     # presolve may not use dual arguments
        strict.optimize()
```

```text
model      type default      DualReductions=0
infeasible LP   INF_OR_UNBD  INFEASIBLE
infeasible MIP  INF_OR_UNBD  INFEASIBLE
unbounded  LP   INF_OR_UNBD  UNBOUNDED
unbounded  MIP  UNBOUNDED    OPTIMAL   objective inf, x = 1e+30
both       LP   INF_OR_UNBD  INFEASIBLE
both       MIP  INF_OR_UNBD  INFEASIBLE
```

With default settings, Gurobi hedged on five of the six models, the plainly infeasible ones too.
With `DualReductions=0` it gave a definite answer for every LP and for both infeasible MIPs. The
unbounded MIP is a warning of its own: with dual reductions off, Gurobi 13 reported `OPTIMAL` with
an objective of `inf` and `x = 1e+30`, which is Gurobi's "infinity". An `OPTIMAL` status does not by
itself mean the plan is usable. Check that the objective is finite before you read the plan.

The two tables say the same thing about the method. A hedged answer comes from presolve. Asking
again with the doubtful steps switched off settles it for most solvers and models, but not for all.
The next section's method works on every solver that can say `INFEASIBLE`.

## A Zero-Objective Copy Settles INFEASIBLE_OR_UNBOUNDED

A model with no objective cannot be unbounded: every plan scores 0, so every plan is optimal.
Solve a copy of the model with its objective cleared. If the copy has a plan, the original has
plans too, and since the solver hedged it must be unbounded. If the copy has none, the original
is infeasible. `diagnose.separate` does this, and never edits the caller's model:

```python
def separate(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS) -> str:
    """Solve; if the answer is 'infeasible or unbounded', ask a zero-objective copy which it is."""
    first = verdict(solve(model, solver))
    if first != "infeasible or unbounded":
        return first
    feasibility = copy(model)
    feasibility.objective.clear()                       # minimize 0: every plan is optimal, none unbounded
    second = verdict(solve(feasibility, solver))
    return {"optimal": "unbounded", "infeasible": "infeasible"}.get(second, "unknown")
```

`copy` is `mathopt.Model.from_model_proto(model.export_model())`, the copy lesson 4.3.2 used, and
`verdict` maps the termination reason to a word (the next sections show the cases where no word
fits). Now the two broken models of this week. The second one is the developer's: finance pays 3%
interest on money carried into the next year, so each year gets a carry variable $`r_y \ge 0`$
(continuous, with no upper bound) and the objective gains $`0.03 \sum_y r_y`$. Lesson 6.4.4's cash
row is $`\text{spend}_y + r_y \le B_y + r_{y-1}`$. The developer wrote it without the
$`+ r_y`$ on the left:

```math
\text{spend}_y \le B_y + r_{y-1} \quad \forall y \in Y \qquad \text{(cash}_y\text{, the bug: } r_y \text{ never leaves year } y)
```

```python
    # The bug: + carry[y] is missing on the left, so money carried out of y never leaves y.
    bug.model.add_linear_constraint(bug.spend[y] <= small.budget[y] + incoming, name=f"cash_{y}")
bug.model.maximize(bug.npv + 0.03 * mathopt.fast_sum(carry.values()))
```

```python
for name, model in (("budget lock", lock.model), ("carry bug", bug.model)):
    result = solve(model)
    print(f"{name:<12} HiGHS: {result.termination.reason.name:<24} separate(): {separate(model)}")
```

```text
budget lock  HiGHS: INFEASIBLE               separate(): infeasible
carry bug    HiGHS: INFEASIBLE_OR_UNBOUNDED  separate(): unbounded
```

HiGHS answered the Budget Lock scenario with `INFEASIBLE`, so `separate` needed no second solve.
For the carry bug it hedged, as it did on the small unbounded MIP above, and the zero-objective
copy found a plan, so the model is unbounded. The two models need different work: the lock needs
the rest of this module, and the carry bug needs one missing term.

The copy answers only "is there any plan?". When it comes back `INFEASIBLE`, that is a full answer
about the original model, because the rows and bounds are the same. When it hits a limit, the
answer is "unknown", and `separate` says so rather than guess.

## Capping Every Free Variable Names the Ones That Run Away

"Unbounded" says some direction improves forever, not which variables move along it. A solver can
return that direction as a ray (`result.has_ray()`, `ray_variable_values()`). On the carry bug's
LP relaxation (every $`x`$ continuous in $`[0, 1]`$), none of HiGHS, GLOP or SCIP returned one
through MathOpt in OR-Tools 9.15, even when it answered `UNBOUNDED`:

```text
LP relaxation, HIGHS presolve on : UNBOUNDED                ray returned: False
LP relaxation, GLOP  presolve on : INFEASIBLE_OR_UNBOUNDED  ray returned: False
LP relaxation, GLOP  presolve off: UNBOUNDED                ray returned: False
LP relaxation, GSCIP presolve on : INFEASIBLE_OR_UNBOUNDED  ray returned: False
```

A method that needs no ray: give every variable
that has no upper bound a large one on a copy, solve, and list the variables that end at the cap.
The capped model cannot be unbounded, and the variables at the cap are the ones the objective was
pushing without limit:

```python
    capped = copy(model)
    free = [v for v in capped.variables() if math.isinf(v.upper_bound)]
    for v in free:
        v.upper_bound = cap
    result = solve(capped, solver)
    values = result.variable_values()
    return sorted(v.name for v in free if values[v] >= cap - 1e-6)
```

```text
variables that run away: ['carry_2027', 'carry_2028', 'carry_2029', 'carry_2030', 'carry_2031']
```

Every carry variable runs away, which points straight at the cash rows: nothing ever takes carried
money out of the year it leaves. Adding $`+ r_y`$ to the left side of each cash row fixes it. The
cap ($`10^7`$ by default) has to be far above any real value of the variables. Pick it below the
point where the solver's tolerances start to matter (section 10). Here $`10^7`$ against
amounts in thousands of dollars is safe.

This is a diagnosis, not a repair: the right fix is the missing term, never a cap left in the
model. A cap would turn "unbounded" into an "optimal" plan that carries $10 billion.

<!-- practice 1 -->

## A Limit Without a Plan Means "Unknown", Never "Infeasible"

The fourth way to end without a plan is to run out of time. GridCap medium (400 projects) with a
time limit of one millisecond:

```python
rushed = solve(build(medium).model, params=mathopt.SolveParameters(time_limit=datetime.timedelta(milliseconds=1)))
print(f"medium, 1 ms: {rushed.termination.reason.name}, limit {rushed.termination.limit.name},"
      f" primal status {rushed.termination.problem_status.primal_status.name} -> {verdict(rushed)}")
```

```text
medium, 1 ms: NO_SOLUTION_FOUND, limit TIME, primal status UNDETERMINED -> unknown
```

`NO_SOLUTION_FOUND` with limit `TIME` and primal status `UNDETERMINED`: the solver claims nothing
about the model. The base model has plans (it is lesson 6.4.1's model plus crews and floors), so
reporting this run as "infeasible" would be false, and a planner would go hunting for a conflict
that does not exist. `verdict` keeps the cases apart:

```python
def verdict(result: mathopt.SolveResult) -> str:
    """'optimal', 'feasible' (a plan, not proven best), 'infeasible', 'unbounded', or 'unknown'."""
    reason = result.termination.reason
    if reason == R.OPTIMAL:
        return "optimal"
    if reason == R.INFEASIBLE:
        return "infeasible"
    if reason == R.UNBOUNDED:
        return "unbounded"
    if reason == R.INFEASIBLE_OR_UNBOUNDED:
        return "infeasible or unbounded"
    if result.has_primal_feasible_solution():
        return "feasible"
    return "unknown"                                    # a limit stopped the solve before any plan
```

A service that turns solves into planner messages (section 12) needs exactly these five outcomes,
and each one leads somewhere different: publish the plan; publish it with its gap (lesson 3.4.1);
explain the conflict (lessons 9.1.3 to 9.1.6); fix the model; or run again with more time.

<!-- practice 2 -->

## Summary

- **A termination reason is a claim about the model, not about your plan.** `INFEASIBLE` means no
  plan exists. `UNBOUNDED` means plans exist and improve forever, almost always a modeling bug.
  `INFEASIBLE_OR_UNBOUNDED` means the solver could not tell which.
- **Five solvers give three answers for the same unbounded model.** Every solver called the
  infeasible models `INFEASIBLE`. GLOP, PDLP, CP-SAT and HiGHS (on the MIP) hedged on the
  unbounded one. Presolve off settled it for GLOP and for HiGHS, and not for the others.
- **Gurobi says `INF_OR_UNBD` until dual reductions are off.** `DualReductions=0` gave definite
  answers, except an unbounded MIP reported `OPTIMAL` with an infinite objective.
- **A zero-objective copy settles `INFEASIBLE_OR_UNBOUNDED`** on any solver: a plan means
  unbounded, none means infeasible.
- **Capping every free variable names the ones that run away**, without needing a ray from the
  solver.
- **A limit without a plan means "unknown", never "infeasible".**

## Reference

| Termination reason | Meaning | Next step |
| --- | --- | --- |
| `OPTIMAL` | best plan found and proven | publish (check the objective is finite) |
| `FEASIBLE` | a plan, stopped by a limit | publish with its gap, or run longer |
| `INFEASIBLE` | no plan meets every rule | find the conflict (9.1.2 to 9.1.6) |
| `UNBOUNDED` | plans improve forever | find the missing bound or term |
| `INFEASIBLE_OR_UNBOUNDED` | one of the two | zero-objective copy, presolve off, or `DualReductions=0` |
| `NO_SOLUTION_FOUND` | a limit stopped the search with no plan | more time; never report it as infeasible |

| Solver (OR-Tools 9.15, gurobipy 13) | Unbounded LP | Unbounded MIP | Presolve off |
| --- | --- | --- | --- |
| GLOP | `INFEASIBLE_OR_UNBOUNDED` | n/a | settles it |
| PDLP | `INFEASIBLE_OR_UNBOUNDED` | n/a | refused |
| HiGHS | `UNBOUNDED` | `INFEASIBLE_OR_UNBOUNDED` | settles it |
| SCIP | `UNBOUNDED` | `UNBOUNDED` | fails reading the result |
| CP-SAT | `INFEASIBLE_OR_UNBOUNDED` | `INFEASIBLE_OR_UNBOUNDED` | no change |
| Gurobi | `INF_OR_UNBD` | `UNBOUNDED` | `DualReductions=0` settles the LP |

| Term | Meaning |
| --- | --- |
| ray | a direction along which a plan stays feasible and improves without end |
| presolve | the pass that simplifies a model before the main algorithm |
| dual reductions | presolve steps that use the objective; valid only if an optimal plan exists |
| zero-objective copy | the model with its objective cleared: it can be infeasible, never unbounded |

**Further reading:** OR-Tools,
[MathOpt](https://developers.google.com/optimization/math_opt), and in its Python sources
[`result.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py)
(`TerminationReason`, `FeasibilityStatus`, `ProblemStatus` and its `primal_or_dual_infeasible`,
`has_ray`). Gurobi,
[Parameters reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
(`DualReductions` and the `INF_OR_UNBD` advice) and the
[infeasibility example tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html).
The [CP-SAT troubleshooting page](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md)
lists other ways to narrow down a model that has no plan.

## Challenges

1. Add the missing $`+ r_y`$ to the carry bug's cash rows. Predict what `separate` returns, and
   whether the NPV is above or below the $22,741k of the base model.
2. Run `status_zoo.py`'s unbounded MIP on HiGHS with presolve off, then add a time limit of one
   millisecond. Which of the five verdicts do you expect?
3. A colleague proposes to treat every `INFEASIBLE_OR_UNBOUNDED` as infeasible, "because our
   models are bounded". Name the bug from this lesson that this rule would have hidden.

## Design Note: Ask Again Rather Than Guess

`separate` could have read `primal_status` and `dual_status` and inferred an answer. When the
solver hedges, though, there is nothing to infer from. HiGHS's hedged answer on the carry bug
claims nothing about either problem:

```text
MIP, HiGHS: primal UNDETERMINED, dual UNDETERMINED, primal_or_dual_infeasible True
```

A second, simpler question (a zero-objective copy) costs one more solve and gives an answer you can
defend. The same habit runs through this module. The pre-solve checks, the filters, the elastic
model and the assumptions each change the question until the solver's answer means one thing.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**status_zoo.py.** The three two-variable models, solved as LPs and MIPs by GLOP, PDLP, HiGHS,
SCIP and CP-SAT, with presolve on and off (*Five Solvers Give Three Answers*). *Try:* Change the
"unbounded" row to $`x - y \le 2`$ plus $`x \le 10`$. Predict whether any solver still hedges.

- Program: [status_zoo.py](src/status_zoo.py)

**gurobi_status.py.** The same models in gurobipy, with default settings and with
`DualReductions=0` (*Gurobi Says INF_OR_UNBD*). It needs the license the runner mounts. *Try:* Set
`Presolve = 0` instead of `DualReductions = 0`. Predict which rows change.

- Program: [gurobi_status.py](src/gurobi_status.py)

**separate_lock.py.** The Budget Lock scenario and the carry bug, told apart by `separate`, the
variables that run away, and the 1 ms solve on GridCap medium (*A Zero-Objective Copy*, *Capping
Every Free Variable*, *A Limit Without a Plan*). *Try:* Give the medium model a 10-second limit.
Predict the verdict.

- Program: [separate_lock.py](src/separate_lock.py)

**diagnose_rays.py.** Asks HiGHS, GLOP and SCIP for a ray on the carry bug's LP relaxation
(*Capping Every Free Variable*). *Try:* Ask on the two-variable unbounded LP instead. Predict
whether a ray comes back.

- Program: [diagnose_rays.py](src/diagnose_rays.py)

The model itself is in `lock_model.py`, and the verdicts in `diagnose.py`.

- Library: [lock_model.py](src/lock_model.py)
- Library: [diagnose.py](src/diagnose.py)
