# 4.2.4 Common vs. Solver-Specific Parameters, and What Each Solver Rejects

GridCap's planning service now takes its solver from configuration, as lesson 4.2.3 advised. The
first night it runs on SCIP instead of HiGHS, it works. The first night someone sets `threads: 4` for
a faster run, the HiGHS deployment crashes with `AttributeError: 'StatusNotOk' object has no
attribute 'canonical_code'`, a message that says nothing about threads, HiGHS or what to change.

MathOpt's `SolveParameters` holds two kinds of setting. **Common parameters** (`time_limit`,
`threads`, `relative_gap_tolerance`, ...) have one name for every solver, and MathOpt translates them.
**Solver-specific parameters** are each solver's own options, passed through untouched. A solver that
cannot honour a common parameter refuses the whole solve. This lesson measures which solver refuses
what in OR-Tools 9.15, teaches you to read the refusal (which this version hides), and shows when to
reach past the common names to a solver's own options. GridCap is a fictional portfolio.

## The Model

Every program here solves GridCap small's project-selection model of lesson 4.2.1, as the MILP or as
its LP relaxation, and one program uses the medium portfolio (400 projects) for a search long enough
to stop early.

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years; $`M \subseteq P`$ the must-do
projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$ the child projects, with parent
$`p(c)`$.

**Parameters.** $`v_i`$, the NPV of project $`i`$ at its earliest start ($k); $`c_{i,y}`$, what it
spends in year $`y`$ ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** MILP: $`x_i \in \{0, 1\}`$ for every $`i \in P`$. LP relaxation: $`0 \le x_i \le 1`$.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(needs}_c) \\
\sum_{i \in P} c_{i,y}\, x_i &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The rows are named `must_P002`, `alt_G006`, `needs_P004` and `budget_2027` in `selection.py`.

## Common Parameters Have One Name for Every Solver, and Each Solver Accepts Only Some

`mathopt.SolveParameters` is a dataclass; you pass the fields you want and leave the rest `None`,
which means "the solver's own default". Its docstring describes each common field; grouped by
purpose, they are:

| Group | Fields |
| --- | --- |
| Stopping | `time_limit` (a `timedelta`), `iteration_limit`, `node_limit`, `solution_limit`, `cutoff_limit`, `objective_limit`, `best_bound_limit` |
| Optimality | `relative_gap_tolerance`, `absolute_gap_tolerance` (lesson 3.4.1) |
| Machine | `threads`, `random_seed` |
| Output | `enable_output` (print the solver's log), `solution_pool_size` (lesson 4.2.2) |
| Algorithm | `lp_algorithm` (lesson 2.4.1), and four efforts: `presolve`, `cuts`, `heuristics`, `scaling` |

The four efforts take an `Emphasis`: `OFF`, `LOW`, `MEDIUM`, `HIGH` or `VERY_HIGH`. The `Emphasis`
docstring sets the rule: a solver without the feature accepts only `None` (some also accept `OFF`),
and a solver that cannot turn the feature off refuses `OFF`.

"Common" means the *name* is shared, not that every solver honours it. The program asks each solver
for each parameter, one solve per cell, and records whether `mathopt.solve` ran or raised:

```python
def accepted(solver: mathopt.SolverType, model: mathopt.Model, params: mathopt.SolveParameters) -> bool:
    try:
        solve(model, solver, params)
        return True
    except Exception:                    # the refusal; read_refusal.py shows how to read why
        return False


print(f"{'parameter':<23}" + "".join(f"{name:>9}" for name, _, _ in columns))
for label, params in asks.items():
    cells = ["ok" if accepted(solver, model, params) else "--" for _, solver, model in columns]
    print(f"{label:<23}" + "".join(f"{cell:>9}" for cell in cells))
```

```text
parameter                   GLOP     PDLP HiGHS-LP  SCIP-LP    HiGHS     SCIP   CP-SAT
time_limit                    ok       ok       ok       ok       ok       ok       ok
iteration_limit               ok       ok       ok       --       --       --       --
node_limit                    --       --       ok       ok       ok       ok       --
solution_limit=1              --       --       ok       ok       ok       ok       ok
cutoff_limit                  --       --       --       ok       --       ok       ok
objective_limit               ok       --       --       --       --       --       --
best_bound_limit              ok       --       ok       --       --       --       --
relative_gap_tolerance        ok       ok       ok       ok       ok       ok       ok
absolute_gap_tolerance        ok       ok       ok       ok       ok       ok       ok
threads=1                     ok       ok       --       ok       --       ok       ok
random_seed                   ok       --       ok       ok       ok       ok       ok
solution_pool_size            ok       ok       --       ok       --       ok       ok
lp_algorithm                  ok       --       ok       ok       --       ok       --
presolve=OFF                  ok       --       ok       ok       ok       ok       ok
cuts=OFF                      --       --       --       ok       --       ok       ok
heuristics=OFF                --       --       ok       ok       ok       ok       --
scaling=OFF                   ok       --       ok       ok       ok       ok       --
```

The first four columns solve the LP relaxation, the last three the MILP. What to take from it:

- **Only three parameters work everywhere:** `time_limit` and the two gap tolerances. The MathOpt
  docstring says `time_limit` is always passed to the solver; a job that must run on any solver can
  rely on those three and nothing else.
- **HiGHS refuses `threads`**, even `threads=1`, and `solution_pool_size`, `cuts`, and two stopping
  values, `cutoff_limit` and `objective_limit`; on a MILP it also refuses a third stopping value,
  `best_bound_limit`, and `iteration_limit` and `lp_algorithm`. It is the course's default solver, so these are the refusals
  you will meet first.
- **CP-SAT refuses the LP-flavoured settings** (`iteration_limit`, `lp_algorithm`, `scaling`), and
  `node_limit`, `heuristics` and the objective and bound limits: it is not an LP-based
  branch-and-bound solver.
- **PDLP refuses most of the list.** It takes the gaps, a time or iteration limit, `threads` and
  `solution_pool_size`.
- **SCIP accepts the most on a MILP,** and refuses only three of the stopping values:
  `iteration_limit`, `objective_limit` and `best_bound_limit`.
- **A refusal is about the pair (solver, model).** HiGHS takes `lp_algorithm` and `iteration_limit` on
  the LP and refuses them on the MILP.

Values are checked too, by MathOpt itself, for every solver: `threads=0`, a negative `time_limit` or a
negative gap is refused before any solver sees it (the next section shows the messages).

<!-- practice 1 -->

## A Refusal Is Raised as an AttributeError in OR-Tools 9.15, and Its Reason Is on __context__

A refused solve raises an exception from `mathopt.solve`; it never returns a result. MathOpt meant
that exception to be a standard Python one: its `solve.py` catches the C++ error (a `StatusNotOk`,
which carries an absl status code and a message; absl, short for Abseil, is Google's open-source C++ library
that OR-Tools' C++ code uses, and a status code is its number for the kind of error) and converts it, by the table in its `errors.py`:

| C++ status code | Python exception MathOpt raises |
| --- | --- |
| `INVALID_ARGUMENT` (3) | `ValueError` |
| `FAILED_PRECONDITION` (9) | `AssertionError` |
| `UNIMPLEMENTED` (12) | `NotImplementedError` |
| `INTERNAL` (13) and anything else | `mathopt.InternalMathOptError` (a `RuntimeError`) |

In OR-Tools 9.15 the conversion itself fails. It reads an attribute, `canonical_code`, that the
`StatusNotOk` class in the installed `pybind11_abseil` does not have, and the `AttributeError` from
that line is what reaches you. Python keeps the exception that was being handled when a new one is
raised as the new one's `__context__`, so the real error is still there:

```python
try:
    solve(milp, mathopt.SolverType.HIGHS, too_many)
except Exception as error:
    print("caught    :", type(error).__name__, "-", error)
    hidden = error.__context__
    print("__context__:", type(hidden).__name__)
    print("  .code   :", hidden.code)
    print("  .message:", hidden.message)
    print("__cause__  :", error.__cause__)
```

```text
caught    : AttributeError - 'StatusNotOk' object has no attribute 'canonical_code'
__context__: StatusNotOk
  .code   : 3
  .message: threads not supported for HiGHS solver, this must be set using globals, see HiGHS documentation
__cause__  : None
```

`too_many` is `SolveParameters(threads=2)`. The hidden `StatusNotOk` has a `code` (3, which is
`INVALID_ARGUMENT`) and a `message`, the solver's own reason. Look for it on `__context__`, not on
`__cause__`: nothing raised the `AttributeError` *from* the real error, so `__cause__` is empty. (Earlier lessons printed
`str(error.__context__)`, which is the message with the code's name appended in brackets.) The same
bug hides every refusal of this module: GLOP's "does not support integer variables" in lesson 4.2.3,
the duplicate names of lesson 4.2.1, and each `--` in the grid above: every one of them raises the
same `AttributeError`, with the reason only on `__context__`.

You do not have to live with the `AttributeError`. A small wrapper does the conversion MathOpt meant
to do, with MathOpt's own table (`mathopt.status_proto_to_exception`), and leaves any other
`AttributeError` alone:

```python
def solve_or_explain(model: mathopt.Model, solver: mathopt.SolverType,
                     params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve, and turn OR-Tools 9.15's AttributeError back into the exception MathOpt meant to raise."""
    try:
        return solve(model, solver, params)
    except AttributeError as error:
        hidden = error.__context__
        if hidden is None or not hasattr(hidden, "code"):
            raise                                       # a genuine AttributeError: leave it alone
        meant = mathopt.status_proto_to_exception(rpc_pb2.StatusProto(code=hidden.code, message=hidden.message))
        raise meant from None
```

With it, every refusal reads as what it is:

```python
for label, solver, params in tries:
    try:
        solve_or_explain(milp, solver, params)
        print(f"{label}: solved")
    except (ValueError, NotImplementedError, AssertionError, mathopt.InternalMathOptError) as error:
        print(f"{label}: {type(error).__name__}: {error}")
```

```text
HiGHS, threads=2: ValueError: threads not supported for HiGHS solver, this must be set using globals, see HiGHS documentation (was C++ INVALID_ARGUMENT)
SCIP, threads=0: ValueError: SolveParameters.threads = 0 <= 0; invalid parameters (was C++ INVALID_ARGUMENT)
HiGHS, time_limit=-1s: ValueError: SolveParameters.time_limit = -1s < 0; invalid parameters (was C++ INVALID_ARGUMENT)
CP-SAT, node_limit=10: ValueError: The node_limit parameter is not supported for CP-SAT. (was C++ INVALID_ARGUMENT)
GLOP, an integer model: ValueError: Glop does not support integer variables (was C++ INVALID_ARGUMENT)
```

Every refusal here is `INVALID_ARGUMENT`, so a `ValueError`: the request was wrong, and retrying it
unchanged will fail again. That is the distinction a service needs. A `ValueError` from `solve` is a
configuration or modeling error, to report and fix; an `InternalMathOptError` is a solver failure,
which may be worth one retry; and a `TerminationReason` (lesson 4.2.2) is an answer, not an error. The
wrapper is written so it keeps working when a later OR-Tools fixes the bug: then the `except
AttributeError` never fires and MathOpt raises the right exception itself.

Read a message for what it says, too. "Not supported for HiGHS" means the parameter is wrong for that
solver; "invalid parameters" with a `SolveParameters.` prefix means the value is wrong for every
solver; "does not support integer variables" means the model is wrong for that solver.

<!-- practice 2 -->

## Solver-Specific Parameters Are Each Solver's Own Options, and They Win Over Common Ones

Each solver has far more settings than the common list. `SolveParameters` has one field per solver
for them, each in that solver's own message type:

| Field | Type | How a setting is written |
| --- | --- | --- |
| `highs` | `highs_pb2.HighsOptionsProto` | by HiGHS option name, in `int_options`, `double_options`, `bool_options` or `string_options` |
| `gscip` | `gscip_pb2.GScipParameters` | by SCIP parameter name, in `int_params`, `long_params`, `real_params`, `bool_params`, ... |
| `cp_sat` | `sat_parameters_pb2.SatParameters` | as fields (`num_workers`, `random_seed`, ...) |
| `glop` | `parameters_pb2.GlopParameters` (in `ortools.glop`) | as fields (`use_dual_simplex`, ...) |
| `pdlp` | `PrimalDualHybridGradientParams` | as fields |
| `gurobi` | `mathopt.GurobiParameters` | `param_values={"Name": "value"}` |

The `SolveParameters` docstring states two rules this section checks: a value set both as a common
and as a solver-specific parameter takes the solver-specific one, and the specific parameters of
solvers other than the one in use are ignored. The program runs one option per solver, then each rule, on GridCap medium where a node limit
has something to stop:

```python
run("HiGHS   highs.int_options mip_max_nodes=1", medium, S.HIGHS,
    P(highs=highs_pb2.HighsOptionsProto(int_options={"mip_max_nodes": 1})))
run("HiGHS   common node_limit=1", medium, S.HIGHS, P(node_limit=1))
run("SCIP    gscip.long_params limits/nodes=1", medium, S.GSCIP,
    P(gscip=gscip_pb2.GScipParameters(long_params={"limits/nodes": 1})))
run("CP-SAT  cp_sat stop_after_first_solution", milp, S.CP_SAT,
    P(cp_sat=sat_parameters_pb2.SatParameters(stop_after_first_solution=True, num_workers=1)))
run("GLOP    glop use_dual_simplex", lp, S.GLOP, P(glop=glop_parameters_pb2.GlopParameters(use_dual_simplex=True)))

# Set in both places, the solver-specific value wins.
run("HiGHS   node_limit=1 and mip_max_nodes=50", medium, S.HIGHS,
    P(node_limit=1, highs=highs_pb2.HighsOptionsProto(int_options={"mip_max_nodes": 50})))

# Another solver's options are ignored, even a nonsense value.
run("HiGHS   with cp_sat num_workers=99", milp, S.HIGHS, P(cp_sat=sat_parameters_pb2.SatParameters(num_workers=99)))
run("HiGHS   with gurobi Threads=2", milp, S.HIGHS, P(gurobi=mathopt.GurobiParameters(param_values={"Threads": "2"})))

# A misspelled option of the solver in use is refused.
run("HiGHS   highs.int_options mip_max_node=1", milp, S.HIGHS,
    P(highs=highs_pb2.HighsOptionsProto(int_options={"mip_max_node": 1})))
```

```text
HiGHS   highs.int_options mip_max_nodes=1    FEASIBLE limit UNDETERMINED 224,315  nodes 1
HiGHS   common node_limit=1                  FEASIBLE limit NODE         224,315  nodes 1
SCIP    gscip.long_params limits/nodes=1     FEASIBLE limit NODE         224,266
CP-SAT  cp_sat stop_after_first_solution     FEASIBLE limit UNDETERMINED 22,481
GLOP    glop use_dual_simplex                OPTIMAL  limit -            23,669
HiGHS   node_limit=1 and mip_max_nodes=50    FEASIBLE limit NODE         224,315  nodes 51
HiGHS   with cp_sat num_workers=99           OPTIMAL  limit -            22,532  nodes 1
HiGHS   with gurobi Threads=2                OPTIMAL  limit -            22,532  nodes 1
HiGHS   highs.int_options mip_max_node=1     refused: option name was unknown; error setting int option name: mip_max_node to value:1
```

(`run` solves and prints the reason, the limit, the objective and, for HiGHS, the node count.) Line by
line:

- **The first two lines stop at the same place** and find the same plan: HiGHS's own `mip_max_nodes`
  is what the common `node_limit` becomes. But the result's `limit` differs. Set through the common
  name, MathOpt knows why HiGHS stopped (`NODE`); set as a HiGHS option, it does not
  (`UNDETERMINED`). A handler that reports the limit (lesson 4.2.2) loses information when a limit is
  set the specific way, so prefer the common name when one exists. SCIP's adapter reports `NODE` either
  way.
- **CP-SAT and GLOP** take their options as fields: `stop_after_first_solution` stopped CP-SAT at its
  first plan, and `use_dual_simplex` switched GLOP to the dual simplex method.
- **Both set, the specific one wins:** with `node_limit=1` and `mip_max_nodes=50`, HiGHS searched
  51 nodes, not 1, and still reported the limit as `NODE`.
- **Other solvers' options are ignored**, silently, however wrong their values. That is what lets one
  `SolveParameters` carry settings for several solvers, and also why a Gurobi setting does nothing on
  HiGHS.
- **A misspelled option of the solver in use is refused**, with the solver's message. The common names
  are checked by MathOpt; the specific names are checked only by the solver, and only when it runs.

Where the specific option names come from: HiGHS's option list in its own documentation, SCIP's
parameter list (names like `limits/nodes`, `limits/gap`), and the `.proto` files in OR-Tools for
CP-SAT, GLOP and PDLP. They change between solver versions, so pin the solver version with the
code that sets them.

## HiGHS Fixes Its Thread Count at the First HiGHS Solve of a Process

HiGHS's refusal of `threads` says the setting "must be set using globals". HiGHS also has an option
named `threads` of its own, and its behaviour explains the message:

```python
asks = [("common threads=1", mathopt.SolveParameters(threads=1)),
        ("highs threads=1 (first HiGHS solve)", highs_threads(1)),
        ("highs threads=1 again", highs_threads(1)),
        ("highs threads=2", highs_threads(2)),
        ("no thread option", highs_threads(None))]
for label, params in asks:
    try:
        result = solve(milp, mathopt.SolverType.HIGHS, params)
        print(f"{label:<36} {result.termination.reason.name}")
    except Exception as error:
        print(f"{label:<36} refused: {error.__context__}")
```

```text
common threads=1                     refused: threads not supported for HiGHS solver, this must be set using globals, see HiGHS documentation [INVALID_ARGUMENT]
highs threads=1 (first HiGHS solve)  OPTIMAL
highs threads=1 again                OPTIMAL
highs threads=2                      refused: HighsStatus: kError [INTERNAL]
no thread option                     OPTIMAL
```

The first HiGHS solve in the process set the thread count to 1, and a later request for 2 was refused
with an `INTERNAL` error, which `solve_or_explain` would raise as `InternalMathOptError`. The
refusal's "globals" and this behaviour point the same way: HiGHS's thread count is a setting of the
whole process, fixed by its first solve, not of one solve. For a service that means: decide HiGHS's thread count once, at start-up, and pass the same value
on every solve or none at all. For reproducible runs, which need a fixed thread count (section 10),
this is the setting to pin.

## A Cutoff Stop Is Reported by the Solver and Unreadable in the 9.15 Wrapper

One more wrapper bug sits in the result, not the request. `cutoff_limit` asks the solver to give up
once it proves no plan can reach that value (lesson 3.4.2). The `SolveParameters` docstring says such
a stop ends `NO_SOLUTION_FOUND` with the limit `CUTOFF`. SCIP and CP-SAT accept the parameter, so the
program sets a cutoff below and above GridCap small's optimum of $22,532k:

```python
for cutoff in (20_000.0, 30_000.0):
    for solver in (mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT):
        params = mathopt.SolveParameters(cutoff_limit=cutoff)
        try:
            result = solve(milp, solver, params)
            print(f"cutoff {cutoff:,.0f} {solver.name:<6}: {result.termination.reason.name}"
                  f" {result.objective_value():,.0f}")
        except ValueError as error:
            print(f"cutoff {cutoff:,.0f} {solver.name:<6}: ValueError: {error}")
print("Limit members:", [limit.name for limit in mathopt.Limit])
```

```text
cutoff 20,000 GSCIP : OPTIMAL 22,532
cutoff 20,000 CP_SAT: OPTIMAL 22,532
cutoff 30,000 GSCIP : ValueError: 12 is not a valid Limit
cutoff 30,000 CP_SAT: ValueError: 12 is not a valid Limit
Limit members: ['UNDETERMINED', 'ITERATION', 'TIME', 'NODE', 'SOLUTION', 'MEMORY', 'OBJECTIVE', 'NORM', 'INTERRUPTED', 'SLOW_PROGRESS', 'OTHER']
```

A cutoff the optimum beats changes nothing. A cutoff above the optimum makes both solvers stop as
documented, and the result never reaches you: MathOpt's result protocol numbers the cutoff limit 12
(`LIMIT_CUTOFF` in `result.proto`), the Python `Limit` enum has no member for it, and parsing the
result raises `ValueError`. Unlike the parameter refusals, this one has no `__context__` to read; the
solve ran and its answer is lost. In OR-Tools 9.15, treat a `ValueError` naming "not a valid Limit"
from a solve with a cutoff as "no plan reaches the cutoff", or leave `cutoff_limit` unset.

## Summary

- **Common parameters have one name for every solver,** and each solver accepts only some. Only
  `time_limit` and the two gap tolerances worked on every solver here.
- **HiGHS refuses `threads`, `solution_pool_size`, `cuts`, `cutoff_limit` and `objective_limit`**
  (and on a MILP `best_bound_limit`, `iteration_limit` and `lp_algorithm`); CP-SAT refuses
  `node_limit` and the LP settings; PDLP refuses most of the list. Refusals depend on the model too.
- **A refusal raises an exception before solving.** In OR-Tools 9.15 it is an `AttributeError`; the
  real error is on `__context__`, with `.code` and `.message`, and `mathopt.status_proto_to_exception`
  turns it into the `ValueError` MathOpt meant.
- **Solver-specific parameters are each solver's own options.** They win over common ones, other
  solvers' options are ignored, a misspelled name is refused, and a limit set this way can come back
  as `UNDETERMINED`.
- **HiGHS fixes its thread count at the first solve** of a process; later solves must ask for the same
  count or none.
- **A cutoff stop raises `ValueError: 12 is not a valid Limit`** in OR-Tools 9.15.

## Reference

| Want | Common parameter | Refused by (OR-Tools 9.15) |
| --- | --- | --- |
| stop after a time | `time_limit=timedelta(...)` | none |
| stop at a gap | `relative_gap_tolerance`, `absolute_gap_tolerance` | none |
| stop after nodes | `node_limit` | GLOP, PDLP, CP-SAT |
| stop at the first plan | `solution_limit=1` | GLOP, PDLP |
| threads | `threads` | HiGHS (use `highs` `threads`, fixed per process) |
| a seed | `random_seed` | PDLP |
| several plans | `solution_pool_size` | HiGHS |
| turn cuts off | `cuts=Emphasis.OFF` | GLOP, PDLP, HiGHS |
| turn heuristics off | `heuristics=Emphasis.OFF` | GLOP, PDLP, CP-SAT |

| Exception from `solve` | Meaning | What to do |
| --- | --- | --- |
| `AttributeError ... canonical_code` (9.15) | a refusal; read `__context__.code` and `.message` | convert, then as below |
| `ValueError` (`INVALID_ARGUMENT`) | wrong parameter, value or model for this solver | fix the request |
| `NotImplementedError` (`UNIMPLEMENTED`) | a model feature this solver lacks | change solver or model |
| `InternalMathOptError` (`INTERNAL`) | a solver failure | report; maybe retry once |
| `ValueError: 12 is not a valid Limit` (9.15) | the solve stopped on `cutoff_limit` | no plan reaches the cutoff |

**Further reading:** [MathOpt `parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py) (the `SolveParameters` docstring: every common field, the `Emphasis` rules, and the precedence of solver-specific settings); [MathOpt `parameters.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/parameters.proto) (the same fields at the protocol level, with which solvers support `solution_limit`); [MathOpt `solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py) (where a C++ status becomes a Python exception, and the `canonical_code` read that fails in 9.15); [MathOpt `errors.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/errors.py) (the status-code to exception table); [MathOpt `result.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/result.proto) (`LIMIT_CUTOFF = 12`, the value the Python `Limit` enum lacks); [MathOpt sample facility_lp_benders.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/facility_lp_benders.py) (a function that builds different `SolveParameters` for Gurobi, GLOP, GLPK and PDLP, with solver-specific settings for Gurobi and GLPK).

## Challenges

1. Extend the grid with `enable_output=True`. Where does each solver print its log, and does any refuse
   it?
2. Write `params_for` for SCIP with a 60-second limit, a 0.1% gap and 4 threads, and the same for
   HiGHS. Which line has to differ?
3. Find the HiGHS option that sets the MIP gap, set it with the common `relative_gap_tolerance` also
   set to another value, and check which one HiGHS used.

## Design Note: Build Parameters Per Solver, in One Place

The OR-Tools sample `facility_lp_benders.py` has a function that returns a different `SolveParameters`
for each solver it supports, and raises for any other. That is the shape to copy. A planning service
keeps one function, `params_for(solver, settings)`, that turns its own settings (a time budget, a gap,
a thread count) into what each solver accepts, skips what a solver refuses, and is tested by one solve
per solver. Everything else in the service passes the solver and the settings through without
looking at them. When a new OR-Tools release changes what a solver accepts, the grid program above
finds it and this one function changes.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**common_params.py.** Every common parameter on every solver, as an LP and as a MILP, accepted or refused (*Common Parameters Have One Name for Every Solver*). *Try:* Add `presolve=Emphasis.HIGH`. Predict which cells change from the `OFF` row.

- Program: [common_params.py](src/common_params.py)

**read_refusal.py.** The `AttributeError`, the real error on `__context__`, and `solve_or_explain`, which raises the exception MathOpt meant (*A Refusal Is Raised as an AttributeError*). *Try:* Add PDLP with an integer model to `tries`. Predict the message.

- Program: [read_refusal.py](src/read_refusal.py)

**specific_params.py.** One option per solver, a common and a specific setting together, other solvers' options, and a misspelled option (*Solver-Specific Parameters*). *Try:* Set SCIP's `limits/nodes` to 50 with the common `node_limit=1`. Predict which one SCIP obeys, then check the result.

- Program: [specific_params.py](src/specific_params.py)

**highs_threads.py.** HiGHS's thread count, refused as a common parameter and fixed by the first HiGHS solve (*HiGHS Fixes Its Thread Count*). *Try:* Move the "no thread option" line to the top. Predict which lines change.

- Program: [highs_threads.py](src/highs_threads.py)

**cutoff_crash.py.** A cutoff below and above the optimum on SCIP and CP-SAT, and the `Limit` enum (*A Cutoff Stop Is Reported by the Solver*). *Try:* Set the cutoff to exactly 22,532. Predict the outcome.

- Program: [cutoff_crash.py](src/cutoff_crash.py)
