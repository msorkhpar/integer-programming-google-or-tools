# 14.3.8 Handoff: Tests, Packaging and a Report for Finance

The plan is ready to leave the engineer's machine. Two teams will take it from here, and the last
request comes from both:

> **Request 8.** Finance wants the plan as a table they can read: money and risk by year, against
> each year's budget, with a line saying how good the plan is. The operations analysts will run it
> themselves, so it needs a command, a version, and tests that tell them when a change has moved the
> answer. Same input, same report, every time.

The code before this lesson is snapshot `steps/07`; after it, `steps/08`. The fleets are invented
(GridCap is fictional), and the report says so on its second line.

## The Code Prints for Its Author, Not for Finance

After seven lessons the project answers every planning question so far, but the only way to get an
answer is `python -m renewal`, which prints a few lines meant for the engineer: units replaced, the
objective, the bound, a line per year. It has no version, so nobody can say which code made a given
plan; it has no flags, so a different fleet size or budget means editing `__main__.py`; and nothing
checks that the next change leaves a reviewed plan alone. The tests of the earlier lessons check
rules, one at a time. None of them would notice if a refactoring kept every rule and moved forty
units to other years.

## The Design Decision: A Report Function, a Command, and a Golden File

Three pieces, each the smallest that does the job:

| Need | Choice | Alternatives considered |
| --- | --- | --- |
| a table finance reads | `finance.py`: lines per year, then Markdown | a spreadsheet file (a new dependency); an HTML page (more than asked) |
| a way to run it | `cli.py` with `argparse`, declared as the `renewal` command in `pyproject.toml` | keep `python -m` only (no version, no install) |
| notice when an answer moves | a golden report, reviewed once, compared on every test run (the section 12 lesson *Golden Datasets and Regression Tests*) | value tolerances only (miss moved units) |

The report's numbers come from one function, `finance_lines`, and the Markdown is only a rendering of
them. Tests check the numbers against the plan; the golden file checks the rendering and the plan
together.

## The Model Does Not Change

This lesson changes no row, variable or objective. The model is the last lesson's, solved on the
base curves by default. That is worth saying in a handoff: finance is told which model produced the
table, and a reader of the code sees that the step touched reporting and packaging only.

## The Change, File by File

**`finance.py` (new): the plan as finance reads it.** One `YearLine` per plan year, years with no
work included, so the table always has the plan's ten rows:

```diff
--- 07/renewal/finance.py
+++ 08/renewal/finance.py
@@
+@dataclass(frozen=True)
+class YearLine:
+    year: int
+    units: int              # transformers replaced
+    replacement: int        # $k for the units
+    outages: int            # substation outages
+    outage_cost: int        # $k for the outages
+    total: int              # $k, replacement + outage_cost
+    budget: int             # $k
+    risk_removed: float     # $k over the risk window, discounted to FIRST_YEAR, base curves
```

`finance_lines(fleet, request, plan)` fills one `YearLine` per year of `request.plan_years()`, in
order, and its body is yours to write in the practice. For each year: the units the plan replaces
that year and the sum of their costs; the number of that year's pairs in `report.outages` and that
number times `request.outage_cost`; as the total, that year's entry of `report.spend_by_year` with
the request's outage cost, 0 for a year with no work; `request.budget`; and the sum of
`risk_removed(t, year, request)` over the year's units, on the base curves.

The money comes from `report.spend_by_year` and `report.outages`, the same functions the tests of the
outage lesson pinned; the risk from `risk.risk_removed`, the model's own coefficient. Nothing is
computed twice in two ways. The last line of the report states the bound in finance's terms:

```diff
--- 07/renewal/finance.py
+++ 08/renewal/finance.py
@@
+    gap = (plan.bound - plan.value) / plan.bound if plan.bound else 0.0
+    out += ["", f"Solver status {plan.status}. No plan under these rules removes more than "
+                f"${plan.bound:,.0f}k; this one is within {gap:.2%} of that bound."]
+    return "\n".join(out) + "\n"
```

**`cli.py` (new): the command.** It holds the 500-unit request that `__main__.py` used to hold,
scales it for larger fleets, and lets an analyst set the fleet size, seed, budget and gap:

```diff
--- 07/renewal/cli.py
+++ 08/renewal/cli.py
@@
+    parser = argparse.ArgumentParser(prog="renewal", description=__doc__)
+    parser.add_argument("--units", type=int, default=500, help="fleet size (fictional fleet)")
+    parser.add_argument("--seed", type=int, default=2027, help="the fleet generator's seed")
+    parser.add_argument("--budget", type=int, help="$k per year (default: 10,000 per 500 units)")
+    parser.add_argument("--gap", type=float, help="stop within this share of the bound (default 0.02)")
+    parser.add_argument("--out", help="write the report here instead of printing it")
```

`main` returns 0 when a plan was found and 2 when not, so a script that runs it can tell the two
apart. A `Plan` carries its status as the termination reason's name, a string, so `solve.py` gains
`FOUND_NAMES`, the names of the reasons in `FOUND`, and `main` tests the status against it:

```diff
--- 07/renewal/solve.py
+++ 08/renewal/solve.py
@@
 FOUND = (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE)
+FOUND_NAMES = {reason.name for reason in FOUND}
```

```diff
--- 07/renewal/cli.py
+++ 08/renewal/cli.py
@@
+from .solve import FOUND_NAMES
@@
+    return 0 if got.status in FOUND_NAMES else 2
```

`main` takes `argv` as an argument, so tests call it directly instead of starting a process.

**`__main__.py`: one line.** `python -m renewal` now runs the same `main` as the installed command:

```diff
--- 07/renewal/__main__.py
+++ 08/renewal/__main__.py
@@
-"""python -m renewal [UNITS]: a ten-year replacement plan for a fictional fleet (500 units unless
-UNITS is given, a multiple of 500), with outages, crews and spares."""
+"""python -m renewal: the same as the `renewal` command."""
```

**`pyproject.toml` and `__init__.py`: a package with a version.** The stub file becomes a project
declaration: a name, a version, the pinned OR-Tools it was tested with, and the `renewal` command.
`__version__` repeats the version in the code, and a test keeps the two equal.

```diff
--- 07/pyproject.toml
+++ 08/pyproject.toml
@@
 [project]
 name = "renewal"
+version = "1.0.0"
+description = "Transformer fleet renewal planning with OR-Tools MathOpt and HiGHS"
+requires-python = ">=3.12"
+dependencies = ["ortools==9.15.6755", "numpy>=2"]
+
+[project.scripts]
+renewal = "renewal.cli:main"
```

One limit, stated plainly: the course's runner image has no `setuptools`, so `pip install .` cannot
build this package inside it, and the lesson does not claim it does. What the runner can do is pack
the package into one runnable file with the standard library's `zipapp`, which is how `handoff.py`
checks that the package runs from outside its folder.

## The Report for the 500-Unit Fleet

`handoff.py` runs the command on the 500-unit fleet with the default request (gap 2%, per-unit
outage rows, base curves):

```text
$ renewal --units 500
# Transformer renewal plan, 2027-2036

Fleet of 500 transformers (fictional data). All money in $k.

| Year | Units | Replacement | Outages | Outage cost | Total | Budget | Risk removed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2027 | 21 | 7,730 | 7 | 2,100 | 9,830 | 10,000 | 103,272 |
| 2028 | 18 | 7,750 | 7 | 2,100 | 9,850 | 10,000 | 79,625 |
| 2029 | 22 | 7,830 | 7 | 2,100 | 9,930 | 10,000 | 67,083 |
| 2030 | 14 | 8,120 | 6 | 1,800 | 9,920 | 10,000 | 51,499 |
| 2031 | 13 | 7,950 | 6 | 1,800 | 9,750 | 10,000 | 42,695 |
| 2032 | 12 | 8,150 | 4 | 1,200 | 9,350 | 10,000 | 35,430 |
| 2033 | 11 | 8,470 | 5 | 1,500 | 9,970 | 10,000 | 25,927 |
| 2034 | 12 | 7,660 | 7 | 2,100 | 9,760 | 10,000 | 23,245 |
| 2035 | 14 | 7,870 | 7 | 2,100 | 9,970 | 10,000 | 18,770 |
| 2036 | 6 | 8,300 | 5 | 1,500 | 9,800 | 10,000 | 13,540 |
| Total | 143 | 79,830 | 61 | 18,300 | 98,130 | 100,000 | 461,085 |

Solver status OPTIMAL. No plan under these rules removes more than $469,076k; this one is within 1.70% of that bound.
```

Finance can read three things off it without knowing what a model is. The plan spends $98,130k of
$100,000k, and $18,300k of that, almost a fifth, is outages, which is the cost of the substation
rule. The risk removed per year falls steadily, from $103,272k for the 2027 work to $13,540k for
2036's, because each later replacement is counted over fewer of the 20 risk years and the riskiest
units go first. And the last line says the plan is within 1.70% of the best any plan could do under
these rules, which is the honest form of "optimal" at a 2% tolerance.

Then the packed file, run on the small fleet the golden test uses:

```text
packed 15 modules into renewal.pyz
renewal.pyz exit 0; report equals the golden file: True
```

## The Tests Guard the Numbers, the Report, Repeatability and the Declaration

- **the finance lines add up to the plan:** on a 40-unit fleet, one line per year; units, totals
  and risk add up to the plan's own counts, `spend_by_year` and objective; and every year's total is
  its replacements plus its outages and within budget.
- **the report matches the reviewed golden file:** `main` on a 30-unit fleet, exact solve, writes a
  report equal to `tests/golden/plan_30.md`, character for character. The golden file was produced
  once by this code and read before it was kept; a change that moves the plan fails this test until
  someone reviews the new report and replaces the file on purpose.
- **two runs write the same report:** the same input gives the same bytes. HiGHS is run with its
  defaults here, and the test is what says that, on this fleet and image, its answer repeats (the
  determinism lessons, 10.2.1 to 10.2.5, list what would break it: threads, time limits, ties).
- **the package declares its version and command:** `pyproject.toml` names `renewal.cli:main` as
  the `renewal` command, and its version equals `renewal.__version__`.

Of the four, only the golden test notices a plan that moved. The other three would pass on it: the
finance lines add up to whatever plan the code found, two runs of the changed code still write the
same report as each other, and the declaration test reads `pyproject.toml` and `__version__`, never
a plan.

The golden fleet is small and solved exactly (`--gap 0`) on purpose. A golden test of a run stopped
at 2% would compare whichever plan the solver stopped at, and a harmless change in the search could
move it.

```text
step 08 tests on the code of step 07 (before): 32 passed, 4 failed
  FAILED test_handoff.py::test_the_finance_lines_add_up_to_the_plan (AssertionError)
         assert [] == [2027, 2028, 2029, 2030]
  FAILED test_handoff.py::test_the_report_matches_the_reviewed_golden_file (AssertionError)
         assert 1 == 0
  FAILED test_handoff.py::test_two_runs_write_the_same_report (AssertionError)
         assert 1 == 0
  FAILED test_handoff.py::test_the_package_declares_its_version_and_command (AssertionError)
         assert None == 'renewal.cli:main'
step 08 tests on the code of step 08 (after): 36 passed, 0 failed
tests step 08 adds or changes: 4
```

On the last lesson's code, the stub `finance_lines` returns no lines, the stub `main` returns 1, and
the stub `pyproject.toml` declares no command; each test fails on that assertion. The practice is
set up differently on one point: it gives `pyproject.toml` finished and read-only, with the command
and the version declared, so in the practice the declaration test passes its first assertion and
fails on its second, because the starting package has no `__version__`.

## What the Step Did to the Code, and to the Project Overall

```text
step  files  lines  functions  tests  test lines  most branching function
00        7    104          7      4          25  rank.worst_first (3)
01       10    167         13      8          55  solve.read_plan (3)
02       10    195         17     15          97  solve.read_plan (3)
03       10    225         19     19         121  model.build (13)
04       11    251         22     22         143  model.build (23)
05       13    337         27     25         177  reference.build_reference (23)
06       13    415         29     29         216  reference.build_reference (23)
07       15    439         34     32         245  model.build (24)
08       15    497         34     36         277  model.build (24)
```

This step added 58 code lines and no branching to the model: the report and command are straight
code. Over the whole module the package grew from 104 lines to 497 and the tests from 4 to 36, with
about one line of test for every two lines of code. The two numbers that deserve a reviewer's eye
are the branching ones. `model.build` reached 23 when crews and spares were added and 24 with the
scenario objectives, and its reference copy keeps the old 23 alongside it.
A next request should begin by splitting `build` into one function per constraint family, each
taking the shared variables: the rows are already written as separate blocks, so the split moves
code rather than changing it, and the reference-model test of the scale lesson says whether it was
moved correctly.

**Practice.** This lesson's project practice starts from the code before this step, the whole
package (snapshot `steps/07`). It is graded by the tests in the practice's `tests/` folder and by a
check that `main.py` prints the practice's `expected/report.txt`; the practice's statement gives the
request `main.py` makes and the format of every line it prints. This step's `main.py` runs the
`renewal` command's `main` on a tiny fleet of 25 units, drawn from seed 56, and prints the finance
report.

<!-- practice 1 -->

## Summary

- **A handoff adds no rules.** It adds a report function, a command, a version and tests that watch
  the answer, and leaves the model alone.
- **The report's numbers come from the code the tests already pinned**, and the Markdown is only
  their rendering; its last line states the bound and the gap in finance's terms.
- **A golden file catches a moved plan that every rule test misses.** Keep its run exact and small,
  and update it on purpose, after review.
- **Same input, same report** is a test, not an assumption.

## Reference

| Piece | Where |
| --- | --- |
| lines by year | `finance.finance_lines` → `YearLine` |
| the report | `finance.finance_report` (Markdown) |
| the command | `cli.main(argv)`; `renewal` in `pyproject.toml`; `python -m renewal` |
| the golden report | `tests/golden/plan_30.md`, checked by `test_the_report_matches_the_reviewed_golden_file` |
| one runnable file | `zipapp.create_archive(src, "renewal.pyz", main="renewal.cli:main")` |

**Further reading:** [Python `zipapp` (CPython source)](https://github.com/python/cpython/blob/3.14/Lib/zipapp.py) (`create_archive` and its `main` argument, the entry point written into the archive's `__main__.py`); [Python `tomllib` (CPython source)](https://github.com/python/cpython/tree/3.14/Lib/tomllib) (`loads`, which the declaration test uses to read `pyproject.toml`); [MathOpt `parameters.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/parameters.py) (`relative_gap_tolerance` and the solver-dependent gap, the number the report's last line restates). All three were read from the copies installed in the course's runner image. Lessons 10.2.1 to 10.2.5 (determinism) and the section 12 lesson *Golden Datasets and Regression Tests* are the course's background for this step.

## Challenges

1. Finance asks for a CSV next to the Markdown. Which function gives you every number already, and
   what test keeps the CSV and the Markdown in agreement?
2. A teammate changes the default gap from 2% to 1%. Which test fails, which does not, and why?
3. Split `model.build` into one function per constraint family. Which test tells you the split kept
   the model?

## Design Note: The Report States the Bound, Not "Optimal"

`OPTIMAL` from a solver stopped at a 2% gap means "within 2%". Finance reads "optimal" as "best".
So the report's last line says what the run proved, a bound no plan can beat and how close this one
is, and keeps the solver's word for the status only. A handoff document that overstates the answer
is a bug the tests cannot catch.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**handoff.py.** Runs the `renewal` command's `main` on the 500-unit fleet, packs the package into one
runnable file with `zipapp`, runs that file on the golden fleet and compares its report with the
golden file, and runs the step's tests before and after the change (*every section*). *Try:* Pass
`--seed 7` to the 500-unit run. Predict which lines of the report change.

**growth.py.** Counts every snapshot (*What the Step Did to the Code, and to the Project Overall*).

- Program: [handoff.py](src/handoff.py)
- Program: [growth.py](src/growth.py)
- Library: [steps.py](src/steps.py)
