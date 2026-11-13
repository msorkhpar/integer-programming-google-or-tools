# 4.3.5 Callbacks and `compute_infeasible_subsystem`

Two requests reach GridCap's modeling team in the same week. Operations wants to watch a long
solve as it runs: every better plan the solver finds, and a way to stop as soon as one is good
enough. And finance has sent a scenario the model calls **INFEASIBLE**, with no plan at all; they
want to know which of their numbers to blame. Both needs reach inside the solve. The first uses
**callbacks**, functions of yours that the solver calls while it works. The second uses an
**irreducible infeasible subsystem** (IIS), a smallest set of rules that cannot all hold at once.
This lesson shows MathOpt's API for both, which solvers in OR-Tools 9.15 support which parts, and
how to get an IIS when the solver will not compute one. GridCap is a fictional utility.

## The Model

The multi-period timing model of lesson 4.3.1, with two additions used in this lesson, each marked.
Its decisions are start-time variables: $`x_{i,t}= 1`$ if project $`i`$ starts in year $`t`$ of its
window $`T_i`$; a project starts at most once and spends its cost profile from its start year on.
(Lesson 6.4.1, in section 6, builds this model step by step.)

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the
child projects, with parent $`p(c)`$ and lag $`L_c`$; $`R \subseteq P`$ the transmission projects.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, project $`i`$'s spend in its $`k`$-th year
of work ($k); $`B_y`$, the budget ($k); $`K = 2`$, the transmission projects one year's crews can
start.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints**, with $`\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}`$:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{i \in R,\ y \in T_i} x_{i,y} &\le K && \forall y \in Y && \text{(crews}_y) \quad \leftarrow \text{lazy, in its section}
\end{aligned}
```

The infeasible scenario changes data only: $`x_{\text{P032},2027} \ge 1`$ (the board's promise) and
$`B_{2030} = B_{2031} = 5{,}000`$ (finance's caps). The crew rows are used only in the lazy
constraints section, and the scenario only in the IIS sections.

## A Message Callback Hands You the Solver's Log, Line by Line

The simplest callback is the one lesson 4.3.3 used to read hints: `msg_cb`, a function that
receives the solver's log as a list of lines, each time the solver writes some. HiGHS, SCIP and
CP-SAT all call it (lesson 4.3.3 read all three logs this way). MathOpt ships three ready-made ones in `message_callback.py`:
`list_message_callback(sink)` appends the lines to a list, `printer_message_callback(prefix=...)`
prints them, and `log_messages` sends them to Python's `logging`. A message callback is plain
Python, so it can also filter. The program below uses two of them. First HiGHS solves the small
portfolio with its log kept in a list; nothing reaches the terminal during the solve, and the
program afterwards prints four lines it picks from the list. Then SCIP solves the tiny portfolio
with a printer that shows only the lines a filter lets through:

```python
log: list[str] = []
result = solve(pm.model, mathopt.SolverType.HIGHS, msg_cb=mathopt.list_message_callback(log))
print(f"{result.termination.reason.name}: {len(log)} log lines kept, none printed")
for line in log:
    if line.strip().startswith(("Status", "Primal bound", "Dual bound", "Gap")):
        print("  ", line.strip())
```

```python
printer = mathopt.printer_message_callback(prefix="SCIP> ")     # prints each line as it arrives
keep = ("SCIP Status", "Primal Bound", "Dual Bound", "Gap")
# mathopt.solve, not plan_model.solve: that one silences standard output, the printer's too.
result = mathopt.solve(pm.model, mathopt.SolverType.GSCIP,
                       msg_cb=lambda lines: printer([line for line in lines if line.startswith(keep)]))
```

```text
OPTIMAL: 58 log lines kept, none printed
   Status            Optimal
   Primal bound      24260
   Dual bound        24260
   Gap               0%
SCIP> SCIP Status        : problem is solved [optimal solution found]
SCIP> Primal Bound       : +2.47300000000000e+03 (1 solutions)
SCIP> Dual Bound         : +2.47300000000000e+03
SCIP> Gap                : 0.00 %
```

The four indented lines come from the list: the program printed them from the HiGHS log it kept,
after the solve, and they are the end of HiGHS's log on the small portfolio. The `SCIP>` lines are the
printer's, written during SCIP's solve of the tiny portfolio (optimum 2,473). The printer comes from OR-Tools' `remote_solve.py` sample. Logging to
a list instead of the terminal is what a service does (section 12): the log is kept with the
result, and nothing is printed that nobody reads.

## A Solve Callback Runs at Events the Solver Supports

A **solve callback** is called by the solver at **events** during the search, receives data about
the search so far, and can answer. Three pieces make one:

- a `CallbackRegistration`: which events to call it at (`events={...}`), and whether it may add rows
  (`add_lazy_constraints`, `add_cuts`);
- the callback, a function from `CallbackData` to `CallbackResult`, passed to `solve` as `cb`;
- `CallbackData`, what the solver hands over: the `event`, a `solution` (a dict from variables to
  values, at events that have one), `mip_stats` (the best bound and incumbent so far, node counts),
  and the `runtime`.

The events for a MIP, as the `Event` docstring in `callback.py` describes them:

| Event | When | `solution` holds |
| --- | --- | --- |
| `MIP_SOLUTION` | the solver found a new feasible integer solution | that solution |
| `MIP` | periodically in the search loop | nothing |
| `MIP_NODE` | inside a node of the search tree | the node's LP relaxation, if any |

The callback below follows OR-Tools' `facility_location.py` sample: register `MIP_SOLUTION`, and in
the callback read the solution. Here it computes each solution's NPV and keeps a list:

```python
def watch(data: mathopt.CallbackData) -> mathopt.CallbackResult:
    npv = sum(small.project(p).npv[t] * data.solution[v] for (p, t), v in pm.x.items())
    seen.append(round(npv))
    return mathopt.CallbackResult()                  # nothing to ask of the solver
registration = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION})
result = solve(pm.model, solver, params=params, callback_reg=registration, cb=watch)
```

```text
GSCIP  OPTIMAL  NPV 24,260  callback calls 191  incumbents [19911, 16582, 21172, 23851, 20192, 20739, 20799, 18987] ...
CP_SAT OPTIMAL  NPV 24,260  callback calls 16  incumbents [20901, 22318, 23159, 23507, 23509, 23673, 23683, 23930] ...
HIGHS  OPTIMAL  NPV 24,260  callback calls 0  incumbents []
```

The same callback, three very different stories:

- **SCIP called it 191 times, and the values go down as well as up**: 19,911, then 16,582. SCIP
  reports every feasible solution its heuristics find, not only better ones. A callback that wants
  "the best plan so far" must keep the best itself.
- **CP-SAT called it 16 times, with values only rising.** It ran with `threads=1`: CP-SAT's default
  of several parallel workers finds solutions in an order that changes from run to run, and one
  worker makes the list repeatable.
- **HiGHS never called it**, and raised no error either. The next check shows that is not about this
  event.

Each solver's answer to each event, with the callback counting its calls:

```text
GSCIP  MIP_SOLUTION called; MIP refused (event CALLBACK_EVENT_MIP is not supported [INVALID_ARGUMENT]); MIP_NODE called
CP_SAT MIP_SOLUTION called; MIP called; MIP_NODE refused (event CALLBACK_EVENT_MIP_NODE is not supported [INVALID_ARGUMENT])
HIGHS  MIP_SOLUTION accepted, never called; MIP accepted, never called; MIP_NODE accepted, never called
```

SCIP and CP-SAT refuse what they cannot do, before the solve starts, with a reason on
`__context__`. HiGHS accepts every registration and calls none of them: through MathOpt in OR-Tools
9.15, a HiGHS solve runs as if no callback had been given. When SCIP runs with a callback it also
writes two `ERROR` lines to standard error about catching events (`SCIPcatchEvent does not support
variable or row change events`); the solve still ends `OPTIMAL` with the right plan, as the output
shows. The `Event` docstring lists further events (`PRESOLVE`, `SIMPLEX`, `BARRIER`) that only
Gurobi supports.

<!-- practice 1 -->

## A Callback Can Stop the Solve

A callback's answer is a `CallbackResult`. Setting `terminate=True` asks the solver to stop as soon
as it can. `mip_stats` gives the incumbent's value (`primal_bound`) and the best bound
(`dual_bound`), so a callback can stop at a gap of its own choosing (lesson 3.4.1 defines the gap):

```python
def good_enough(data: mathopt.CallbackData) -> mathopt.CallbackResult:
    stats = data.mip_stats
    gap = (stats.dual_bound - stats.primal_bound) / abs(stats.primal_bound) if stats.primal_bound > 0 else 1.0
    return mathopt.CallbackResult(terminate=gap <= 0.02)
```

```text
stopped early: FEASIBLE (INTERRUPTED), NPV 24,059, bound 24,510
```

SCIP stopped with a plan worth 24,059 and a proven bound of 24,510: the plan is within
$`(24{,}510 - 24{,}059) / 24{,}059 = 1.9\%`$ of the best possible. The termination is `FEASIBLE`,
not `OPTIMAL`, with limit `INTERRUPTED`, so a program reading the result knows why the search
stopped (lesson 4.2.2). Two details from the `CallbackResult` docstring: a solver may not stop at
once and may call the callback again, and once `terminate` has been returned, a later `False` does
not take it back. For a fixed gap, the `relative_gap_tolerance` parameter does the same job without
code (lesson 3.4.2); a callback earns its place when the rule is your own, such as "stop when a plan
funds every must-do region at 95%" or "stop when the user clicks Cancel".

<!-- practice 2 -->

## A Lazy Constraint Is Added Only When a Solution Breaks It

A callback at `MIP_SOLUTION` can also reply with rows the solution breaks. These are **lazy
constraints**: rules left out of the model, then added by the callback the first time a solution
breaks one. OR-Tools' `tsp.py` sample uses them for a rule with too many rows to write: it checks
each solution for subtours and adds only the cut rows that solution breaks. The pattern needs
`add_lazy_constraints=True` in the registration and `result.add_lazy_constraint(row)` in the
callback.

Here the rule is GridCap's crew limit: at most $`K = 2`$ transmission projects may start in one
year. It has only five rows, so writing it up front is the sensible choice, and the program does
that first as the reference answer. Then the same rule goes in lazily:

```python
def check(data: mathopt.CallbackData) -> mathopt.CallbackResult:
    result = mathopt.CallbackResult()
    for year, count in starts_per_year(plan(pm, data.solution)).items():
        if count > CREWS:
            result.add_lazy_constraint(crew_row(pm, year))
            added.append(year)
    return result
registration = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION}, add_lazy_constraints=True)
```

```text
without the rule: {2027: 2, 2028: 3, 2029: 1, 2030: 3}
rows up front  HIGHS   NPV 24,050  starts {2027: 2, 2028: 2, 2029: 1, 2030: 2}
lazy rows      GSCIP   NPV 24,050  starts {2027: 2, 2028: 2, 2029: 1, 2030: 2}  rows sent 4
lazy rows      HIGHS   NPV 24,260  starts {2027: 2, 2028: 3, 2029: 1, 2030: 3}  rows sent 0
lazy rows      CP_SAT  refused: CallbackRegistrationProto.add_lazy_constraints=true is not supported for CP-SAT. [INVALID_ARGUMENT]
```

The dict maps each year to the transmission projects started in it. Without the rule, 2028 and
2030 start three each. `rows sent` counts the rows the callback returned.

- **SCIP** added rows as solutions broke the rule and ended at 24,050, the same NPV as the model with
  every row written up front, with at most 2 starts in every year.
- **CP-SAT** refuses lazy constraints, with a clear reason.
- **HiGHS** accepted the registration, never called the callback, and returned a plan that breaks
  the rule: 3 starts in 2028 and in 2030, and an NPV of 24,260 that no allowed plan reaches. Nothing
  in the result says so.

That last line is the most dangerous output in this module: an `OPTIMAL` status on a plan that
breaks a business rule. The defence: check the plan against the rules after every solve, in plain
Python, as `starts_per_year` does here. (Lesson 6.2.2, in section 6, gives the same advice for
big-M rows, whose plans can break a rule through the solver's tolerance.) And never
send a callback-dependent model to a solver you have not seen call your callback.

## `compute_infeasible_subsystem` Names a Minimal Conflict, With Gurobi Only

Now finance's scenario: the board promises P032 for 2027, and the 2030 and 2031 budgets are capped at
5,000 each. The model has no plan:

```python
promised = pm.x["P032", 2027]
promised.lower_bound = 1.0
pm.budget[2030].upper_bound = 5000
pm.budget[2031].upper_bound = 5000
```

```text
solve: INFEASIBLE | (no detail)
```

"Infeasible" says no plan meets every rule, not which rules clash. An **irreducible infeasible
subsystem** (IIS) answers that: a set of the model's constraints (rows, variable bounds,
integrality) that cannot all hold together, and is **irreducible**: drop any one of them and the
rest can hold. It is one explanation of the conflict, small enough to read. A model can have
several, and an IIS is one of them, not necessarily the smallest.

MathOpt's call is `mathopt.compute_infeasible_subsystem(model, solver_type)`. Its docstring in
`solve.py` says the only supported solver is Gurobi, and the runner agrees:

```text
compute_infeasible_subsystem, HIGHS  AttributeError HiGHS does not provide a method to compute an infeasible subsystem [UNIMPLEMENTED]
compute_infeasible_subsystem, GSCIP  AttributeError SCIP does not provide a method to compute an infeasible subsystem [UNIMPLEMENTED]
compute_infeasible_subsystem, CP_SAT AttributeError CPSAT does not provide a method to compute an infeasible subsystem [UNIMPLEMENTED]
compute_infeasible_subsystem, GUROBI RuntimeError   bad_function_call
```

What the call returns is still worth knowing well, because the next section builds the same result
by hand. A `ComputeInfeasibleSubsystemResult` has three fields:

| Field | Meaning |
| --- | --- |
| `feasibility` | `INFEASIBLE` if a conflict was proven; `FEASIBLE` or `UNDETERMINED` otherwise, and then the rest is to be ignored |
| `infeasible_subsystem` | a `ModelSubset`: which constraints are in the conflict |
| `is_minimal` | `True` if the subset is irreducible; the docstring warns MathOpt's model changes can leave it not quite minimal |

A `ModelSubset` lists the conflict in three parts: `linear_constraints` and `variable_bounds`, dicts
from a row or a variable to a `ModelSubsetBounds(lower=..., upper=...)` saying which of its two
bounds take part, and `variable_integrality`, the set of variables whose integrality takes part.
The sides matter: a row $`\ell \le a^\top x \le u`$ is two rules, and an IIS often needs only one of
them. In OR-Tools 9.15 the Python reader of this result also raises `NotImplementedError` if the
subsystem contains indicator, SOS or quadratic constraints (`compute_infeasible_subsystem_result.py`),
so a model with indicators cannot get its IIS read back in Python.

## A Deletion Filter Finds One by Hand, in the Same Result Type

Without Gurobi, an IIS can be found with any solver that can say "infeasible", by the **deletion
filter** (Chinneck's method). Go through the model's bounds one at a time. Drop the bound, then
solve:

- still infeasible: the bound was not needed for the conflict, so leave it dropped;
- now feasible: the bound is part of the conflict, so put it back.

At the end, every bound left is needed, and the set is irreducible. Each test is a feasibility
question, so the objective is set to 0 first; the cost is one solve per bound, which is fine for a
few hundred rows and slow for a large model. `find_iis.deletion_filter` works on a copy (made as
in lesson 4.3.2), and returns the same `ComputeInfeasibleSubsystemResult` Gurobi's call would:

```python
for item, side in candidates:
    old = getattr(item, side)
    if math.isinf(old):
        continue                                                   # no bound on this side
    setattr(item, side, -math.inf if side == "lower_bound" else math.inf)
    if not is_infeasible(work, solver):
        setattr(item, side, old)                                   # needed: put it back
        kept.append((item, side))
```

```python
return mathopt.ComputeInfeasibleSubsystemResult(
    feasibility=mathopt.FeasibilityStatus.INFEASIBLE,
    infeasible_subsystem=mathopt.ModelSubset(variable_bounds=bounds, linear_constraints=rows),
    is_minimal=True)
```

The candidates are both sides of every row, and both sides of the variables the caller names: here
the promised start, whose lower bound of 1 was a scenario decision. The 0-and-1 bounds of the other
binaries are what makes them binaries, and are left alone. `report` reads the result as a planner
would:

```text
by hand: feasibility INFEASIBLE, minimal True, 3 rows, 0 variable bounds
   row budget_2030: upper bound 5,000
   row budget_2031: upper bound 5,000
   row must_P017: lower bound 1
P017: must start in [2030, 2031], cost profile (5310,)
```

Three rules clash: P017 is a must-do project that can start only in 2030 or 2031 and spends 5,310 in
its start year, and both of those years are capped at 5,000. Notice what is *not* in the
subsystem: the board's promise of P032. Finance's question was "which number do we blame?", and the
answer is the caps, not the promise. Raising either cap to 5,310, or moving P017's window, makes the
scenario feasible again. Only the lower side of `must_P017` (an equality, $`= 1`$) is in the
conflict: "at most once" is harmless; "at least once" is the problem.

Lesson 9.1.3 goes further with IIS tools (MathOpt with Gurobi, gurobipy, Pyomo) and lesson 9.1.6
turns an IIS into a message for planners.

<!-- practice 3 -->

## Summary

- **A message callback hands you the solver's log, line by line.** `msg_cb=list_message_callback(log)`
  works with HiGHS, SCIP and CP-SAT.
- **A solve callback runs at events the solver supports.** SCIP calls `MIP_SOLUTION` (for every
  solution found, not only improvements) and `MIP_NODE`; CP-SAT calls `MIP_SOLUTION` and `MIP`;
  HiGHS accepts every event and never calls the callback.
- **A callback can stop the solve.** `CallbackResult(terminate=True)` ended SCIP at 1.9% from the
  bound, `FEASIBLE` with limit `INTERRUPTED`.
- **A lazy constraint is added only when a solution breaks it.** SCIP matched the up-front model;
  CP-SAT refuses; HiGHS silently ignored the rule and returned a plan that breaks it.
- **`compute_infeasible_subsystem` names a minimal conflict, with Gurobi only.** HiGHS, SCIP and
  CP-SAT refuse it with `UNIMPLEMENTED`.
- **A deletion filter finds one by hand, in the same result type.** The scenario's conflict was
  P017's must-do row against both caps; the promise of P032 was not part of it.

## Reference

| Task | Code |
| --- | --- |
| keep the log | `msg_cb=mathopt.list_message_callback(log)` |
| a callback at each new solution | `callback_reg=mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION}), cb=f` |
| read the solution in it | `data.solution[v]`; bounds in `data.mip_stats.primal_bound`, `.dual_bound` |
| stop the solve | `return mathopt.CallbackResult(terminate=True)` |
| add a lazy row | registration with `add_lazy_constraints=True`; `result.add_lazy_constraint(row)` |
| an IIS (Gurobi) | `mathopt.compute_infeasible_subsystem(model, mathopt.SolverType.GUROBI)` |

| Solver (OR-Tools 9.15) | `MIP_SOLUTION` | `MIP` | `MIP_NODE` | lazy rows | IIS |
| --- | --- | --- | --- | --- | --- |
| SCIP | called | refused | called | added | refused |
| CP-SAT | called | called | refused | refused | refused |
| HiGHS | accepted, never called | accepted, never called | accepted, never called | ignored | refused |

| Term | Meaning |
| --- | --- |
| message callback | receives the solver's log lines |
| solve callback, event | your function called during the search; the moment it is called at |
| lazy constraint | a row added by a callback when a solution breaks it |
| IIS | a set of constraints that cannot all hold, each one needed for the conflict |
| deletion filter | find an IIS by dropping one bound at a time and keeping only those whose loss makes the model feasible |

**Further reading.** OR-Tools, [MathOpt](https://developers.google.com/optimization/math_opt):
callbacks among the advanced features, and infeasibility analysis (IIS) as Gurobi-only. In OR-Tools'
Python sources,
[`callback.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/callback.py)
(every event and which solvers support it, `CallbackData`, `CallbackRegistration`, `CallbackResult`),
[`message_callback.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/message_callback.py),
[`solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py)
(`compute_infeasible_subsystem`) and
[`compute_infeasible_subsystem_result.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/compute_infeasible_subsystem_result.py).
The samples
[`facility_location.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/facility_location.py)
(solutions in a callback),
[`tsp.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/tsp.py)
(lazy constraints) and
[`remote_solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/remote_solve.py)
(the printer callback). Pyomo,
[Infeasibility Diagnostics](https://pyomo.readthedocs.io/en/stable/explanation/analysis/iis.html):
the same idea in another framework, an IIS written by CPLEX, Gurobi or Xpress, and a finder for
minimal infeasible systems based on John Chinneck's algorithms.

## Challenges

1. Change `watch` so that it records only improving solutions. How many does SCIP's list keep?
2. Make the crew limit 1 per year and run the lazy version on SCIP. Is the callback ever called with
   a solution that already meets the rule?
3. Cap only 2030 at 5,000 in the infeasible scenario. Predict the deletion filter's answer before
   running it.

## Design Note: Return the Library's Type, Even From Your Own Code

`deletion_filter` could return a list of names. It returns a `ComputeInfeasibleSubsystemResult`
instead, the type Gurobi's call returns, built from MathOpt's own `ModelSubset` and
`ModelSubsetBounds`. Everything that reads an IIS, such as `report` here or a planner message in
lesson 9.1.6, is then written once against one type, and the day a supported solver is available,
the hand-made filter can be swapped for `compute_infeasible_subsystem` without changing a reader.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**log_lines.py.** HiGHS's log kept in a list, and SCIP's printed with a prefix and a filter (*A
Message Callback*). *Try:* Keep every line that contains "nodes" and predict whether SCIP or HiGHS
writes more of them.

- Program: [log_lines.py](src/log_lines.py)

**incumbents.py.** Every solution SCIP, CP-SAT and HiGHS report through `MIP_SOLUTION`, which events
each one accepts, and a callback that stops SCIP at a 2% gap (*A Solve Callback Runs at Events*, *A
Callback Can Stop the Solve*). *Try:* Stop at 5% instead and predict whether the NPV is lower.

- Program: [incumbents.py](src/incumbents.py)

**lazy_rows.py.** The crew limit written up front, then added lazily on SCIP, HiGHS and CP-SAT (*A
Lazy Constraint*). *Try:* Make the limit 3 and predict how many rows SCIP sends.

- Program: [lazy_rows.py](src/lazy_rows.py)

**iis.py.** The infeasible scenario, the refused `compute_infeasible_subsystem` calls, and the
deletion filter's answer read against the data (*`compute_infeasible_subsystem` Names a Minimal
Conflict*, *A Deletion Filter*). *Try:* Raise the 2031 cap to 5,310 and predict the solve's status.

- Program: [iis.py](src/iis.py)

**find_iis.py.** The deletion filter and the report.

- Library: [find_iis.py](src/find_iis.py)
