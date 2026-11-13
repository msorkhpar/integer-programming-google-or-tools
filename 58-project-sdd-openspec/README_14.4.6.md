# 14.4.6 Living Specs: Every Scenario Traced to a Test, Every Test to a Scenario

Five changes are archived. The living specs describe the planner as it is, and GridCap's auditors,
who review the planning process once a year, have read them. Their request:

> **Request 6.** For every rule in these specs, show us the test that proves the planner keeps it. For
> every test, show us the rule it checks. If a rule has no test, we cannot rely on it; if a test checks
> no agreed rule, nobody agreed to what it enforces.

The code before this lesson is snapshot `steps/05`; after it, `steps/06`. GridCap and its auditors
are fictional.

## Nothing Links a Scenario to Its Test but a Habit

Since the first lesson, every scenario's test has been named after it: `test_` and the scenario's
name in lower case, each run of other characters an underscore, in the test file named after the
capability, `tests/test_capital_plan.py` for `capital-plan`. That is a convention, and nothing checks
it. The design decision of this change is how to make the link checkable:

| Option | For | Against |
| --- | --- | --- |
| a marker on each test naming its scenario | survives a test rename | every one of 32 tests must change |
| a table, scenario to test, kept in a file | explicit | a third thing to keep in step, and it rots |
| the naming convention the tests already follow | no test changes; the name says what it checks | renaming a scenario breaks the link |

The project takes the convention, and turns its weakness into a check: renaming a scenario without
renaming its test is exactly what a trace should report. The trace reads the **living specs** only,
`openspec/specs/`, because they are what the system is agreed to do; a scenario in a change not yet
archived is not agreed yet. Test files named after no capability are outside the trace, so helpers
and the course's own expected-output check do not count as tests without a scenario.

## The First Trace Finds the Gap the Must-Do Change Left

Run with the trace of `steps/06` on the project as it stands, `steps/05`:

```text
== trace, with the checker of steps/06
steps/05: 32 scenarios with their tests
  no test: capital-plan: A must-do that cannot start in the plan is refused
open tasks of 2026-11-04-add-must-do-override:
  - [ ] 1.6 Test: a must-do that cannot start in the plan is refused
  - [ ] 2.3 request.check: refuse a must-do whose window has no plan year
```

Thirty-two scenarios have their test; one has none. It is the scenario the must-do change left open,
and the archive warned about it and archived anyway. Since then the living spec has said the planner
refuses such a request with a message naming the project. What the planner of `steps/05` does
instead:

```text
steps/05, F must-do and may start only in 2030, plan 2027-2029: 0 started (INFEASIBLE)
```

No message, no plan, and no word about why. The reason is in the model. Project F has no year in the
plan, so $`T_F`$ is empty and its row $`\text{must}_F`$ is $`\sum_{t \in \emptyset} x_{F,t} = 1`$, that
is $`0 = 1`$. In Python the empty `sum` is the number 0, so `starts == 1` is the plain value `False`,
and CP-SAT's `CpModel.add` accepts a Boolean: for `False` it adds an empty clause, a constraint that
can never hold. The model is infeasible, which is true, and useless to a planner, who needs to know
which override to fix. The scenario said so in words; with no test, nobody saw the code did not.

## The Change: Traceability for the Checker, and the Open Tasks Done

The proposal:

<!-- snapshot: steps/06/openspec/changes/archive/2026-11-09-add-scenario-traceability/proposal.md -->
```markdown
## What Changes
- specs_check.py traces each scenario of the living specs to the test named after it, and reports
  every scenario with no test and every test that names no scenario.
- The open tasks of add-must-do-override are done: the test of "A must-do that cannot start in the
  plan is refused", and the check it needs. The capital-plan spec already states the scenario, so
  it does not change.
```

The delta adds one requirement to `spec-checks`, and the convention becomes part of it:

<!-- snapshot: steps/06/openspec/changes/archive/2026-11-09-add-scenario-traceability/specs/spec-checks/spec.md -->
```markdown
### Requirement: Scenario traceability
The checker SHALL trace each scenario of the living specs to its test, and SHALL report every
scenario with no test and every test of a capability's test file that traces to no scenario. A
scenario's test is named test_ and the scenario's name in lower case, each run of other characters
an underscore, in tests/test_ and the capability's name, with hyphens as underscores, and .py.

#### Scenario: A scenario with no test is reported
- **GIVEN** a spec with the scenarios Fits and Too big, and a test file with test_fits only
- **WHEN** the checker traces
- **THEN** it reports Too big as a scenario with no test
```

Its other three scenarios: a test with no scenario is reported; a test in the file of another
capability does not count for this one; and this project's living specs and tests trace both ways.
That last one makes the trace a test of the project, so from now on a scenario without a test fails
the suite, and an archive warning like the must-do change's can no longer scroll past.

The change modifies no capital-plan requirement. The must-do scenario is already in the living spec;
the code is catching up with it. A change does not need a delta for every file it touches, only for
the behaviour it changes in the spec.

## The Model

No row changes in this lesson. The full model, as `steps/05` and `steps/06` build it:

**Sets.** $`P`$, the projects; $`Y = \{y_1, \dots, y_n\}`$, the plan years; $`T_i \subseteq Y`$,
the years project $`i`$ may start; $`R`$, the regions, with $`P_r \subseteq P`$; $`S \subseteq R`$,
the regions with a share; $`M \subseteq P`$, the must-do projects.

**Parameters.** $`c_i`$, cost ($k); $`v_i`$, value ($k); $`B`$, the yearly budget ($k);
$`s_r \in \{0, \dots, 100\}`$, the least share of region $`r`$ (%); $`C \in \{0, \dots, 100\}`$,
the carry-over percent; $`\bar r = \lfloor C B / 100 \rfloor`$ ($k).

**Variables.** $`x_{i,t} \in \{0,1\}`$ for $`i \in P`$, $`t \in T_i`$; $`r_y \in \{0, 1, \dots,
\bar r\}`$ for $`y \in Y \setminus \{y_n\}`$, with $`r_{y_0} = r_{y_n} = 0`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_i \, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\text{spend}_y + r_y &\le B + r_{y-1} && \forall y \in Y && \text{(budget}_y) \\
100\, \text{spend}_{r,y} &\ge s_r \, \text{spend}_y && \forall r \in S \text{ with } s_r > 0,\ y \in Y && \text{(share}_{r,y})
\end{aligned}
```

What changes is the check before the model: a must-do $`i`$ with $`T_i = \emptyset`$ is refused, so
the row $`\text{must}_i`$ is never built with an empty sum $`\leftarrow`$.

## Tests First

Five new tests: four for the checker's new requirement, on small `openspec/` folders written in a
temporary directory, and the must-do test the earlier change never wrote. On the code of `steps/05`,
where `trace` is a stub that returns an empty trace:

```text
step 06 tests on the code of step 05 (before): 32 passed, 5 failed
  FAILED test_capital_plan.py::test_a_must_do_that_cannot_start_in_the_plan_is_refused (AssertionError)
         assert None is not None
  FAILED test_spec_checks.py::test_a_scenario_with_no_test_is_reported (AssertionError)
         assert (0, [], []) == (1, ['demo: Too big'], [])
  FAILED test_spec_checks.py::test_a_test_with_no_scenario_is_reported (AssertionError)
         assert (0, [], []) == (1, [], ['tes...st_old_rule'])
  FAILED test_spec_checks.py::test_a_test_in_the_file_of_another_capability_does_not_count (AssertionError)
         assert (0, [], []) == (1, ['demo: F...::test_fits'])
  FAILED test_spec_checks.py::test_these_specs_and_tests_trace_both_ways (AssertionError)
         assert 0 > 0
```

The third checker test is the one a shortcut would pass: matching scenarios to tests by the test's
name alone, in any file, finds `test_fits` in `other`'s file and calls `demo`'s scenario tested:

<!-- snapshot: steps/06/tests/test_spec_checks.py -->
```python
def test_a_test_in_the_file_of_another_capability_does_not_count(tmp_path):
    write(tmp_path, {"openspec/specs/demo/spec.md": demo_spec("Fits"),
                     "openspec/specs/other/spec.md": demo_spec("Other"),
                     "tests/test_other.py": "def test_other():\n    pass\n\n\ndef test_fits():\n    pass\n"})
    found = trace(tmp_path)
    assert (found.pairs, found.untested, found.untraced) == (1, ["demo: Fits"], ["tests/test_other.py::test_fits"])
```

## The Change, File by File

**`specs_check.py`: `test_name` and `trace`.** `test_name` is the naming convention, written once:

```diff
--- 05/specs_check.py
+++ 06/specs_check.py
@@
 
 
+def test_name(scenario: str) -> str:
+    """The test a scenario is traced to: its name in lower case, each run of other characters one '_'."""
+    return "test_" + re.sub(r"[^a-z0-9]+", "_", scenario.lower()).strip("_")
+
+
 def trace(root: Path) -> Trace:
-    """Stub: the next lesson writes it."""
-    return Trace()
```

`trace` replaces the stub, and its body is the practice's to write. It works in three passes over
two sets of pairs (test file, test name):

1. **What the specs want.** For each living spec `openspec/specs/<capability>/spec.md`, the test
   file is `test_` and the capability's name with `-` as `_`, plus `.py`, and each scenario of its
   requirements wants the pair (that file, `test_name(scenario)`), labelled
   `<capability>: <scenario>`.
2. **What the tests have.** For each of those files that exists under `tests/`, Python's `ast`
   module reads the file's module-level functions whose names start with `test_`, without importing
   or running the file. Other test files are never read.
3. **The comparison.** A pair in both sets is a scenario with its test; a wanted pair with no
   test is reported by its label; a found pair that no scenario wants is reported as
   `tests/<file>::<test>`. Both lists are sorted.

Keeping the file in the pair is what the third checker test above asks for: a set of test names
alone would let `test_fits` in `other`'s file count for `demo`'s scenario.

The snapshot's `specs_check.py` also gains a `trace` command beside `list`, `validate` and `archive`,
which prints the same counts and gaps and exits 1 on any gap. The practice does not ask for it: its
tests and its report call the `trace` function. OpenSpec has no trace command; this one is the
project's own, built on the same reading of requirements and scenarios as the validator.

**`request.py`: the check the must-do change left open.** A must-do whose window has no plan year is
refused before the model, with the project and its window in the message:

```diff
--- 05/capplan/request.py
+++ 06/capplan/request.py
@@
     if not 0 <= request.carry <= 100:
         raise ValueError(f"the carry-over is {request.carry}%, outside 0 to 100")
-    pids = {p.pid for p in projects}
+    by_id = {p.pid: p for p in projects}
     for pid, reason in request.must_do.items():
-        if pid not in pids:
+        if pid not in by_id:
             raise ValueError(f"a must-do override names {pid!r}, which is not in the portfolio")
         if not reason.strip():
             raise ValueError(f"the must-do override of {pid} has no recorded reason")
+        p = by_id[pid]
+        if not any(p.earliest <= y <= p.latest for y in request.plan_years()):
+            raise ValueError(f"must-do {pid} cannot start in any plan year (its window is {p.earliest} to {p.latest})")
```

```text
steps/06, the same request: refused, must-do F cannot start in any plan year (its window is 2030 to 2030)
```

## The Trace Passes Only After Archive

With the change proposed and the new tests written, the trace still reports four tests with no
scenario: the checker's new tests, whose scenarios are in the change and not yet in the living spec.
After archive, nothing:

```text
== trace, the change proposed and the tests of steps/06 written
before archive: 33 scenarios with their tests
  no scenario: tests/test_spec_checks.py::test_a_scenario_with_no_test_is_reported
  no scenario: tests/test_spec_checks.py::test_a_test_in_the_file_of_another_capability_does_not_count
  no scenario: tests/test_spec_checks.py::test_a_test_with_no_scenario_is_reported
  no scenario: tests/test_spec_checks.py::test_these_specs_and_tests_trace_both_ways
after archive: 37 scenarios with their tests
```

The real `openspec archive add-scenario-traceability --yes`, run by `openspec_cli.py` on another
copy of the proposed change, adds the one requirement to spec-checks and writes the same living
specs; its archive folder is dated with the day it runs (`<today>`), where `specs_check.py` takes
`--date`:

```text
$ openspec archive add-scenario-traceability --yes
Task status: ✓ Complete
Specs to update:
  spec-checks: update
Applying changes to openspec/specs/spec-checks/spec.md:
  + 1 added
Totals: + 1, ~ 0, - 0, → 0
Specs updated successfully.
Change 'add-scenario-traceability' archived as '<today>-add-scenario-traceability'.
(exit 0)
specs/capital-plan/spec.md after openspec archive: the same as steps/06
specs/spec-checks/spec.md after openspec archive: the same as steps/06
archive folder: <today>-add-scenario-traceability
every file under openspec/, the archive's date set to steps/06's: the same as steps/06
```

That is the trace saying what OpenSpec's workflow says: a change is done when it is archived. Until
then its scenarios are a proposal, and tests written for them check something not yet agreed. The
must-do scenario went the other way: it was archived, and so agreed, before its test existed. The
trace catches both. After the change all 37 tests pass:

```text
step 06 tests on the code of step 06 (after): 37 passed, 0 failed
tests step 06 adds or changes: 5; removes: 0
```

## The Living Specs Are the Project's Documentation

Six changes in six lessons, each kept whole under `changes/archive/`, and two living specs that say
what the planner does now:

```text
== the archive and the living specs of steps/06
  2026-11-02-add-baseline-specs                capital-plan, spec-checks
  2026-11-03-add-regional-share                capital-plan
  2026-11-04-add-must-do-override              capital-plan
  2026-11-05-add-budget-carry-over             capital-plan
  2026-11-06-retire-yearly-start-cap           capital-plan
  2026-11-09-add-scenario-traceability         spec-checks
Changes:
Specs:
  capital-plan                 requirements 13
  spec-checks                  requirements 6
```

The living specs answer "what does the planner do?"; the archive answers "since when, and why?". The
start cap is in the second and not the first. With the trace in the suite, the auditors' two
questions have an answer that is checked on every run, and the specs cannot drift from the tests
without a test failing. The real CLI, which the course image now runs, agrees on `steps/06`
(`openspec_cli.py`, on a copy):

```text
== steps/06
$ openspec validate --all --strict
✓ spec/capital-plan
✓ spec/spec-checks
Totals: 2 passed, 0 failed (2 items)
(exit 0)
$ openspec list --specs
Specs:
  capital-plan     requirements 13
  spec-checks      requirements 6
(exit 0)
$ openspec list
No active changes found.
(exit 0)
```

The same two specs, with 13 and 6 requirements, pass strict validation. `openspec list` says in words
that no change is active, where `specs_check.py list` prints an empty `Changes:`, and it lists the
specs only under `--specs`. `openspec show capital-plan --type spec`, which prints the spec itself,
stays read-along.

## What the Project Became

```text
step  planner lines  checker lines  tests  requirements  scenarios  most branching planner function
00               98            296      6             0          0  model.build (5)
01              101            309     14            10         14  model.build (5)
02              125            309     20            12         20  model.build (9)
03              136            309     26            16         27  model.build (10)
04              151            309     30            17         31  model.build (10)
05              150            316     32            18         33  request.check (10)
06              153            344     37            19         37  request.check (11)
```

The planner grew by 55 lines in six changes, and its specs from nothing to 19 requirements and 37
scenarios, each with exactly one test. The largest function is still small, but `request.check` now
holds four kinds of rule, and a seventh change should split it, behind the same tests. The style the
project kept is the point of the module: every change started as a folder of words that the planners
could read, every rule was a test before it was code, and every archived change left the specs true.

**Practice.** This lesson's project practice starts from the code of `steps/05`, with the specs and
tests of `steps/06`. It is graded by those tests and by a check that `main.py` prints
`steps/06/expected/report.txt`, which now ends with the trace.

<!-- practice 1 -->

## Summary

- **A trace links every scenario of the living specs to its test, and every test to its scenario.**
  Here the link is a naming convention, written into the checker's spec and checked on every run.
- **The first trace found a scenario archived without its test**, and behind it a planner that
  answered INFEASIBLE where the spec promised a message.
- **An empty sum is the number 0, and `0 == 1` is `False`;** CP-SAT accepts it as a constraint that
  never holds. The check before the model turns it into a message.
- **The trace reads living specs only, so it passes only after archive.** A change is done when it is
  archived.
- **Living specs say what the system does; the archive says since when and why.**

## Reference

| `specs_check.py` command | Does | OpenSpec |
| --- | --- | --- |
| `list` | active changes with tasks done, living specs with requirements | `openspec list`, `openspec list --specs` |
| `validate --strict` | every living spec and active change; fails on warnings | `openspec validate --all --strict` |
| `archive <id> --date <d>` | merges the deltas, moves the change | `openspec archive <id> --yes` |
| `trace` | scenarios with no test, tests with no scenario | none; the project's own |

| Convention | Form |
| --- | --- |
| a capability's test file | `tests/test_<capability with - as _>.py` |
| a scenario's test | `test_` and the scenario's name in lower case, each run of other characters `_` |

**Further reading:** [CP-SAT Solver (OR-Tools docs)](https://developers.google.com/optimization/cp/cp_solver) (the `INFEASIBLE` status the planner of `steps/05` returned); [`cp_model.py` (OR-Tools source, `v9.15`)](https://github.com/google/or-tools/blob/v9.15/ortools/sat/python/cp_model.py) (`CpModel.add` accepts a Boolean and adds an empty clause for `False`; read from the copy installed in the course's runner image); [Concepts (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/concepts.md) (specs as the source of truth, archive as the end of a change, and the archive as an audit trail); [CLI reference (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/cli.md) (`list --specs`, `show --type spec`, `validate --all --strict`); [Troubleshooting (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/troubleshooting.md) (archive warns about incomplete tasks). Lessons 12.3.1 (testing one constraint at a time) and 12.3.3 (regression tests) are the course's background for this step.

## Challenges

1. Rename the scenario "Four starts in one year are allowed" to "Many starts in one year are
   allowed" in the living spec only. Predict the trace's two lines, then say which file the fix
   belongs in.
2. A colleague adds a helper test, `test_generator_is_seeded`, to `tests/test_capital_plan.py`. What
   does the trace report, and what are the two ways to make it pass?
3. Write the scenario, and the test, for a must-do whose window starts in the plan's last year and
   ends after it. Should it be refused?

## Design Note: Why the Checker Got a Spec of Its Own

`specs_check.py` is tooling, and could have stayed outside the specs. It has one because its rules are
behaviour the project relies on as much as the planner's: if the keyword rule broke, specs without
SHALL would pass; if the trace broke, a scenario without a test would. Writing them as requirements
and scenarios put them under the same discipline: each rule has a test, the trace covers them, and a
change to a rule is a delta someone reviews. OpenSpec does the same with its own repository, whose
`openspec/` folder specifies the CLI itself.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**living_specs.py.** Traces `steps/05` with the new checker, shows the open tasks, the INFEASIBLE plan
and the refusal, validates the change, runs the step's tests before and after, traces before and
after archive, and lists the archive and the living specs (*every section*). *Try:* Delete
`test_four_starts_in_one_year_are_allowed` from a copy of `steps/06` and run the trace on it.
Predict its one line, then run it.

**growth.py.** Counts the planner's and the checker's lines, the tests, the requirements and the
scenarios of every snapshot (*What the Project Became*). *Try:* Predict which column would grow most
if a seventh change split `request.check` into three functions, then make the change in a copy and
run it.

**openspec_cli.py.** Runs the real OpenSpec CLI on a temporary copy of every snapshot and every
proposed change (lesson 14.4.1 describes it); this lesson quotes its archive of
`add-scenario-traceability` and its run on `steps/06` (*The Trace Passes Only After Archive; The
Living Specs Are the Project's Documentation*). *Try:* Predict what `openspec list` prints on a copy of `steps/06` with one archived
change moved back to `openspec/changes/`, then run it.

- Program: [living_specs.py](src/living_specs.py)
- Program: [openspec_cli.py](src/openspec_cli.py)
- Program: [growth.py](src/growth.py)
- Library: [changes.py](src/changes.py)
- Library: [steps.py](src/steps.py)
