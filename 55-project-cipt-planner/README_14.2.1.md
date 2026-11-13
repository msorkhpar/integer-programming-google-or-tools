# 14.2.1 The First Request: Fund Projects Within One Budget

This module grows one program, the CIPT planner (Capital Investment Planning Tool), from a first
small request into the system a capital-planning team runs every cycle. Each lesson takes one new
request from the planners and changes the code to meet it. The project lives in complete snapshots:
`steps/00` is the starting skeleton, and `steps/NN` is the project after lesson 14.2.NN. Every
snapshot runs on its own and passes its own tests. The data is GridCap, the course's fictional
utility; no number in it describes a real company.

The capstone (lessons 13.1.1 to 13.1.6) built a similar system milestone by milestone, from finished parts. Here
the code starts small and grows, and the subject is how a design changes when requirements arrive
one at a time.

The first request, as the planning lead wrote it:

> We have $38.39M of capital for the next five years and 40 candidate projects on GridCap small.
> Tell us which to fund to get the most value. Use the NPV finance quoted for each project.
> We'll worry about years later.

## The Skeleton Reads the Export and Prints a Plan, but Decides Nothing

`steps/00` is what the team had before anyone wrote a model. It has a package `cipt` with five
files, a test folder, a demo export, an entry point and the report it prints:

| File | What it does in `steps/00` |
| --- | --- |
| `cipt/data.py` | reads the planning export (JSON) into `Project` and `Request` records |
| `cipt/plan.py` | `Plan`: a status, the funded projects with their start years, an objective |
| `cipt/model.py` | `build(request)`: a stub that returns an empty model |
| `cipt/solve.py` | `solve(request)`: a stub that returns "not solved"; `run_highs` and `read_plan`, stubs this lesson writes |
| `cipt/report.py`, `cipt/__main__.py` | the report and the command line `python -m cipt EXPORT.json` |
| `main.py`, `expected/report.txt` | plans `data/demo.json`, found from the file's own folder, and prints the report; the report it prints |

The **export** is the file the planning system hands over. It already carries every column the
planners keep: each project's cost profile, its start window, its rules, its NPV for each start
year and its asset's health. The skeleton's loader reads only what it uses. From
`steps/00/cipt/data.py`:

<!-- snapshot: steps/00/cipt/data.py -->
```python
def load_request(raw: dict) -> Request:
    """Build a Request from the export's dictionary form, refusing duplicate project ids."""
    projects = tuple(
        Project(
            project_id=row["id"],
            name=row["name"],
            capex=sum(row["cost_profile"]),
            value=row["npv"][str(row["earliest_start"])],
            earliest_start=row["earliest_start"],
        )
        for row in raw["projects"]
    )
```

`capex` is the project's whole cost in $k (thousands of dollars), the sum of its cost profile. `value`
is the NPV (net present value, lesson 7.2.1) finance quotes for a start in the project's earliest
year. Every later lesson reads more columns of the same export; none changes the file.

The command line already works. It just has nothing to say:

```text
$ python -m cipt data/demo.json    # steps/00
GridCap tiny: not solved
funded 0 of 8 projects, capex $0k of $7,390k, value $0k
```

The stub in `steps/00/cipt/solve.py` returns a plan that funds nothing:

<!-- snapshot: steps/00/cipt/solve.py -->
```python
def solve(request: Request) -> Plan:
    """Stub: lesson 14.2.1 solves the model. Until then, nothing is funded."""
    return Plan(status="not solved")
```

A stub returns a wrong answer instead of raising, so the tests of this lesson fail on what the
planner answers, not on a crash. That is also the shape of this lesson's practice: you start from
`steps/00` and the tests of `steps/01` grade you.

## One Envelope and Yes-or-No Choices Make a Knapsack

The request has one budget and one decision per project: fund it or not. That is the 0-1 knapsack of
lesson 6.3.1. Nothing about years enters yet; the planners said so.

## The Model

**Sets.** $`P`$, the candidate projects.

**Parameters.** $`c_i`$, the capex of project $`i`$ ($k); $`v_i`$, its value, the NPV of a start in
its earliest year ($k); $`B`$, the envelope ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is funded.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_i\, x_i &\le B && && \text{(budget)}
\end{aligned}
```

The row's label is the name the code gives it, `budget`. Every later lesson keeps that habit:
a row's name in the code is its label in the formulation.

## A Sort by Value per Dollar Is Not the Best Fill

Before writing a model, the team asked whether a spreadsheet would do: sort the projects by value
per $k and take each one that still fits. `first_plan.py` compares that **greedy** fill with the
model's answer for envelopes from $10M to the real $38.39M:

```python
for envelope in (10_000, 15_000, 20_000, 25_000, 30_000, 38_390):
    sized = cipt.data.Request(request.name, envelope, request.projects)
    best = cipt.solve.solve(sized).objective
    quick = sum(p.value for p in greedy(request.projects, envelope))
```

```text
envelope ($k)   model value   greedy value   greedy short by
       10,000         8,898          8,893                 5
       15,000        12,503         12,295               208
       20,000        16,225         16,166                59
       25,000        19,466         19,416                50
       30,000        22,659         22,551               108
       38,390        27,384         27,384                 0
```

At the real envelope the greedy fill happens to match the model, and at $15M it is $208k short.
Greedy fails when the last good projects do not fit the money left and a different mix would
have used it. Nothing in the data warns you when that happens, so the planner uses the model. At
$38.39M the model funds 24 projects:

```text
model: 40 binary variables, 1 row (budget)
GridCap small: optimal
funded 24 of 40 projects, capex $38,390k of $38,390k, value $27,384k
```

## The Model Lives in One File and the Solver in Another

The design decision of this step is where the formulation and the solver go. Three choices were on
the table:

| Choice | For | Against |
| --- | --- | --- |
| model and solve in one function | shortest code today | every later rule and every solver setting edits the same function |
| `model.py` builds, `solve.py` solves and reads back (chosen) | a rule changes one file, a solver setting another; tests call `solve` and check behaviour | two files for twelve lines today |
| CP-SAT instead of MathOpt and HiGHS | the knapsack has integer data | CP-SAT works in integers, so the fractional risk values of the lesson *Value: NPV by start year and risk reduction* would have to be scaled (lesson 4.4.3) |

The planner uses MathOpt with HiGHS (lesson 4.2.1) from the start, so the solver does not change
when the objective does.

## The Change, File by File

**`cipt/model.py`.** Before: `build` returned an empty model. After, it is the model block above
turned into MathOpt calls, and the page leaves its code to the practice. `build(request)` makes a
`mathopt.Model` named after the request and returns `Built(request, model, x, rows)`, the record
`steps/00` already defines:

- `x` maps each project id to its binary variable $`x_i`$, named `x_<id>`, so reading the answer
  back needs no search.
- `rows` maps the row's label to the row. It holds one row today, (budget): the capex $`c_i`$ of
  each project times its $`x_i`$, summed, at most the envelope `capital_budget`, under the name
  `budget`. The diagnostics of the lesson *Why it failed, why it was deferred: a diagnostics layer*
  find rows by these names.
- The objective is the model block's: maximize the sum of each project's `value` $`v_i`$ times
  its $`x_i`$.
- `mathopt.fast_sum` instead of `sum`: its docstring in the OR-Tools source says a row built from
  an empty list with `fast_sum` is safe, while `sum` of an empty list is the number 0 and the row
  becomes a Python `bool` that MathOpt refuses. An export with no projects then still builds.

**`cipt/solve.py`.** Before: three stubs, `solve` above, `run_highs` returning `None` and
`read_plan` returning "not solved". After, in `steps/01/cipt/solve.py`, three parts. First the
imports, the solver settings and the quiet solve:

<!-- snapshot: steps/01/cipt/solve.py -->
```python
import ctypes
import os
import sys

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from .data import Request
from .model import Built, build
from .plan import Plan

#: One thread, set in HiGHS's own options; the first HiGHS solve of a process fixes the count.
PARAMS = mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(int_options={"threads": 1}))


def run_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with stdout pointed at /dev/null, so HiGHS's stray C output stays out of reports."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=PARAMS)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
```

- `highs_pb2` is the module of HiGHS's own options as MathOpt passes them on;
  `HighsOptionsProto` is its record, with one dictionary per option type (`int_options`,
  `bool_options`, ...). `solve.py` now imports `Built` and `build` from `model.py`.
- `PARAMS` fixes HiGHS at one thread through its own options, because MathOpt's common `threads`
  parameter is refused by HiGHS (lesson 4.2.4). One thread also makes runs repeat, which
  the lesson *Trust at scale: determinism harness, golden tests, warm starts* relies on.
- `run_highs` points the process's standard output at `/dev/null` during the solve, because the
  HiGHS bundled with OR-Tools can print a stray debug line on some MIP solves (lesson 4.2.1). A report that
  planners read must not carry it. Line by line:
  - `sys.stdout.flush()` writes out what Python has buffered so far, so no line of the report is
    lost into `/dev/null`.
  - `os.dup(1)` keeps a copy of the real standard output, file descriptor 1, and `os.dup2(sink, 1)`
    points descriptor 1 at `/dev/null`. Redirecting the descriptor, not `sys.stdout`, is what
    silences HiGHS: it is C++ code and writes to descriptor 1 without passing through Python.
  - `ctypes.CDLL(None).fflush(None)` flushes the C library's own output buffers. `CDLL(None)`
    opens the running process itself, whose symbols include the C library's `fflush`, and
    `fflush(NULL)` flushes every C stream. It runs while descriptor 1 still points at
    `/dev/null`, so text HiGHS left in a C buffer goes there, not into the report once the
    descriptor is restored.
  - `finally` restores descriptor 1 and closes the two spare descriptors, even when the solve
    raises.

<!-- snapshot: steps/01/cipt/solve.py -->
```python
def read_plan(built: Built, result: mathopt.SolveResult) -> Plan:
    """Turn a solver result into a Plan; a funded project starts in its earliest year."""
    status = result.termination.reason.name.lower()
    if not result.has_primal_feasible_solution():
        return Plan(status=status)
    values = result.variable_values()
    starts = {pid: built.request.project(pid).earliest_start
              for pid, var in built.x.items() if values[var] > 0.5}
    return Plan(status=status, starts=starts, objective=result.objective_value())
```

- `status` is MathOpt's termination reason in lower case: "optimal", "infeasible", and so on.
- `values[var] > 0.5` reads a binary that the solver returns as a float such as 0.9999999.
- A funded project "starts in its earliest year". The model has no years; the plan records the
  year the planners assumed, so `Plan` keeps one shape from this step to the last.

**`cipt/plan.py`, `report.py`, `__main__.py`.** Unchanged. **`cipt/data.py`** gains one stub for
the next lesson, `Request.starts(project)`, which returns the earliest year alone; nothing calls it
yet. The report that printed "not solved" now prints a plan:

```text
$ python -m cipt data/demo.json    # steps/01
GridCap tiny: optimal
funded 4 of 8 projects, capex $7,370k of $7,390k, value $4,876k
  P001  start 2028  capex  2,150  value  1,386  Ridge substation transformer replace (A001)
  P004  start 2028  capex  3,000  value  2,120  Plains breaker bay replace (A004)
  P005  start 2027  capex    250  value    123  Ridge circuit trim (A005)
  P006  start 2028  capex  1,970  value  1,247  Valley substation transformer replace (A006)
```

## Each Test Checks What the Planners Asked, on Data Small Enough to Solve by Hand

The tests build their own exports with two helpers in `steps/01/tests/conftest.py`, `row` and
`export`, which fill every column of the export with a default. They never use GridCap: a test's
expected answer must be one a reader can check with a pencil. From `steps/01/tests/test_select.py`:

<!-- snapshot: steps/01/tests/test_select.py -->
```python
def test_best_combination_beats_best_ratio():
    # A has the best value per $k, but taking it leaves no room for B and C together.
    request = load_request(export([row("A", (60,), 70), row("B", (50,), 50), row("C", (50,), 50)],
                                  capital_budget=100))
    plan = solve(request)
    assert plan.funded == ("B", "C")
    assert plan.objective == 100
```

`ledger.py` runs each step's new tests twice: against the code before the step (`steps/00` with
the tests of `steps/01`, the practice's starting point) and against the code after it:

```text
14.2.1: 5 tests added; on step 00, 5 fail on an assertion; on step 01, 9 of 9 pass
  test_plan_respects_the_budget
    before: assert 'not solved' == 'optimal'
    after:  passed
  test_best_combination_beats_best_ratio
    before: assert () == ('B', 'C')
    after:  passed
  test_funds_everything_when_the_budget_allows
    before: assert () == ('A', 'B')
    after:  passed
  test_report_names_the_funded_projects
    before: assert 'funded 2 of 3 projects, capex $100k of $100k, value $100k' in 'test: not solved\
    after:  passed
  test_command_line_prints_the_report
    before: assert 'test: not solved' == 'test: optimal'
    after:  passed
```

The first test checks two things at once on purpose: an empty plan respects any budget, so a test
that checked only the budget would pass on the stub. A test that cannot fail on the old code
tests nothing about the change.

## The Step Added a Solver Layer and Nothing Else

`code_size.py` measures each snapshot: lines of the package (non-blank, not comments), functions,
test functions, and the function with the most branches (1 plus its decision points: McCabe's
cyclomatic number):

```text
14.2.1: steps/00 -> steps/01
  package lines 125 -> 154, functions 10 -> 11, tests 4 -> 9
  most branches: report.render (5) -> report.render (5)
  data.py        47 ->   51
  model.py       15 ->   20
  solve.py       15 ->   35
```

Twenty-nine lines: twenty in `solve.py`, most of them the quiet, one-thread solve, four in
`data.py` for the next lesson's stub, and five in the model itself. That ratio is typical of the first step: the formulation is small,
and the plumbing around a solver call is what takes code.

**Practice.** This lesson's project practice starts from `steps/00`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds.

<!-- practice 1 -->

## Summary

- **The skeleton reads the export and prints a plan, but decides nothing.** The export carries
  every column from the start; each version reads the ones it uses.
- **One envelope and yes-or-no choices make a knapsack.** One binary per project, one row.
- **A sort by value per dollar is not the best fill.** On GridCap small it came up $208k short at a
  $15M envelope, and matched the model at $38.39M.
- **The model lives in one file and the solver in another.** `build` names every row; `solve` runs
  HiGHS quietly on one thread and reads a `Plan` back.
- **Each test checks what the planners asked, on data small enough to solve by hand**, and fails on
  the code before the step.

## Reference

| Name | Meaning |
| --- | --- |
| `steps/NN` | the project after lesson 14.2.NN; `steps/00` is the skeleton |
| export | the planning system's file, every column from the start (JSON) |
| `Built` | the model, its variables `x` and its rows by name |
| `Plan` | status, `starts` (project to start year), `objective` |
| `ledger.py` | each step's new tests on the code before and after the step |
| `code_size.py` | lines, functions, tests and the most-branched function per snapshot |

**Further reading:** [MathOpt `expressions.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/expressions.py) (`fast_sum`, and why it is safe on an empty list where `sum` is not); [MathOpt `parameters.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py) (`SolveParameters` and the solver-specific `highs` options); [MathOpt `result.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (`TerminationReason`, the source of the plan's status).

## Challenges

1. Find an envelope between $10M and $15M where greedy is short by more than $208k. What makes
   those envelopes bad for greedy?
2. The export has a project with an NPV of zero at its earliest start. Does the model fund it when
   the money is there? Should it?
3. Write a test that fails if `read_plan` used `values[var] == 1.0` instead of `> 0.5`. Can you,
   with HiGHS on these models?

## Design Note: Read Only the Columns You Use

The loader could have refused an export with columns it does not know, or mapped every column into
the records at once. It does neither. Reading only what the code uses keeps the first version
small, and the planners never have to make a special export for it. The cost is that a column the
planner should use but ignores goes unnoticed: in this version the must-do flag is in the export
and nothing reads it. The tests of the lesson *Business rules: must-dos, bundles, parents and alternatives* are what catch that, not the loader.

## The Full Programs

Each output above was printed by one of these programs. Open one to read it whole, change it, and
run it again.

**first_plan.py.** Runs `steps/01` on GridCap small and compares the model with a greedy fill by
value per $k for six envelopes (*A Sort by Value per Dollar Is Not the Best Fill*). *Try:* sort
the greedy fill by value alone instead of value per $k. Predict whether it does better or worse at
$15M before you run it.

- Program: [first_plan.py](src/first_plan.py)

**cli_demo.py.** Runs `python -m cipt data/demo.json` in several snapshots, the skeleton's and
step 01's among them. *Try:* add `(5, [])` to its list of runs and predict the first line.

- Program: [cli_demo.py](src/cli_demo.py)

**ledger.py.** Runs each step's new tests against the code before and after the step
(*Each Test Checks What the Planners Asked*). *Try:* run `python3 ledger.py 1` alone.

- Program: [ledger.py](src/ledger.py)

**code_size.py.** Measures every snapshot (*The Step Added a Solver Layer and Nothing Else*).
*Try:* change the branch count to leave out boolean operators and see which function leads.

- Program: [code_size.py](src/code_size.py)

**export.py and steps.py.** `export.py` writes GridCap as the planning export; `steps.py` loads
one snapshot's package for a program.

- Library: [export.py](src/export.py)
- Library: [steps.py](src/steps.py)
