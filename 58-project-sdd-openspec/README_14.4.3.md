# 14.4.3 A Must-Do Override That Needs a Recorded Reason

The share is in the living spec. The next request comes from the planners themselves:

> **Request 3.** Some projects have to be done whatever the model thinks they are worth: a
> regulator's order, storm damage, a safety finding. Today we force them by raising their value in
> the input file until the model picks them, which nobody can see afterwards and which inflates the
> plan's value. Give us a must-do switch. And every must-do needs a written reason, or the auditors
> will ask us who forced what, and why, and we will not know.

The code before this lesson is snapshot `steps/02`; after it, `steps/03`. GridCap is fictional, and
so are its regulators.

## Inflating a Value Forces Nothing and Leaves No Record

The planner has one way to make a project more attractive, its value $`v_i`$, and raising it has
three faults. It does not force anything: a project with a large value can still lose to two
projects with more. It changes the plan's reported value by money that does not exist. And it leaves
no trace of who forced the project or why. A must-do is not a preference; it is a rule about the
plan, and a rule is a row.

`must_do.py` takes the plan of `steps/02` on the 40 invented projects, with the Plains share, and
picks the project a value-maximizing plan likes least, the one with the least value per $k among
those it leaves out, as the one a regulator orders:

```text
steps/02 plan: 12 started, value $13,236k; 28 left out
least value per $k among them: P039, plains, $560k for $381k, may start 2030-2031
```

## The Change: Four Requirements, One Row Family, One Check

The proposal names the problem and the change in the planners' words:

<!-- snapshot: steps/03/openspec/changes/archive/2026-11-04-add-must-do-override/proposal.md -->
```markdown
## What Changes
- A request may mark projects must-do, each with the reason it is forced; the plan starts every
  must-do project in a year of its window.
- An override with no reason, or for a project the planner cannot start, is refused before solving.
- The report lists each override with its reason.
```

The delta adds four requirements to `capital-plan`: **Must-do override** (the plan starts it),
**Recorded reason**, **Override target** and **Overrides are reported**. The two about refusing an
override are where the audit rule lives:

<!-- snapshot: steps/03/openspec/changes/archive/2026-11-04-add-must-do-override/specs/capital-plan/spec.md -->
```markdown
### Requirement: Recorded reason
The planner SHALL refuse, before solving, a must-do override whose reason is empty or only spaces.

#### Scenario: An override with an empty reason is refused
- **WHEN** a request marks a project must-do with an empty reason
- **THEN** the planner refuses it with a message
- **AND** the same override with a reason is accepted

#### Scenario: A reason of only spaces is refused
- **WHEN** a request marks a project must-do with a reason of three spaces
- **THEN** the planner refuses it with a message

### Requirement: Override target
The planner SHALL refuse, before solving, a must-do override for a project that is not in the
portfolio or that cannot start in any plan year.

#### Scenario: An override for an unknown project is refused
- **WHEN** a request marks project Z must-do and the portfolio has no Z
- **THEN** the planner refuses it with a message

#### Scenario: A must-do that cannot start in the plan is refused
- **GIVEN** a project that may start only in 2030, in a plan of 2027 to 2029
- **WHEN** a request marks it must-do
- **THEN** the planner refuses it with a message naming the project
```

"A reason of only spaces" is its own scenario on purpose. An empty string and three spaces are both
no reason, but a check written as `if not reason` refuses only the first: Python treats `"   "` as
true. Writing the case down as a scenario is what makes someone test it.

This change has no `design.md`. OpenSpec makes the design optional, for changes where the approach
needs agreeing; here it is one row family and a check, and the proposal's Impact names them. The
formulation is in the model block below.

## The Design Decision: an Equality Row, Not a Fixed Variable

Lesson 6.5.6 treats a manual override as a fixed bound on a variable, and lesson 12.1.2 keeps an
audit trail of them. A must-do here does not say which year, only that the project starts in one
year of its window, so no single variable can be fixed to 1. The options:

| Option | For | Against |
| --- | --- | --- |
| raise $`v_i`$ until the model picks it | no code | forces nothing; inflates the reported value; leaves no trace |
| fix $`x_{i,t} = 1`$ for one chosen year | one bound | the planners would have to choose the year, which the model does better |
| replace $`\sum_t x_{i,t} \le 1`$ by $`\sum_t x_{i,t} = 1`$ | the model chooses the year; the row has its own name | none here |

The project takes the equality. The reason is not part of the model at all: it is data the request
carries and the report prints, and the check refuses a request without it before any model exists.

## The Model

The planner's model with must-do overrides. Changes from the last lesson are marked.

**Sets.** $`P`$, $`Y`$, $`T_i`$, $`R`$, $`P_r`$ and $`S`$ as before; $`M \subseteq P`$, the
projects the request marks must-do $`\leftarrow`$.

**Parameters.** $`c_i`$, $`v_i`$, $`B`$, $`K`$ and $`s_r`$ as before. Each $`i \in M`$ carries a
reason, a non-empty text that the model does not read $`\leftarrow`$.

**Variables.** $`x_{i,t} \in \{0,1\}`$ for $`i \in P`$, $`t \in T_i`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_i \, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \quad \leftarrow \text{changed} \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \quad \leftarrow \text{this lesson} \\
\text{spend}_y &\le B && \forall y \in Y && \text{(budget}_y) \\
\sum_{i \in P :\, y \in T_i} x_{i,y} &\le K && \forall y \in Y && \text{(starts}_y) \\
100\, \text{spend}_{r,y} &\ge s_r \, \text{spend}_y && \forall r \in S \text{ with } s_r > 0,\ y \in Y && \text{(share}_{r,y})
\end{aligned}
```

A must-do project gets `must_P039` in place of `once_P039`. Its value stays $`v_i`$, so the plan's
value is what the projects are worth, and the price of the override is the drop in value.

## Tests First, and Two Tasks Left Open

The tasks list one test per scenario, then the code. Two boxes are not ticked:

<!-- snapshot: steps/03/openspec/changes/archive/2026-11-04-add-must-do-override/tasks.md -->
```markdown
- [ ] 1.6 Test: a must-do that cannot start in the plan is refused
- [x] 1.7 Test: the report lists each override with its reason
- [x] 1.8 Run the tests on the code before the change and see each fail on an assertion

## 2. Code
- [x] 2.1 model.build: the row must_<pid>, the project's starts summing to exactly 1, in place of once_<pid>
- [x] 2.2 request.check: refuse an unknown project, and a reason that is empty or only spaces
- [ ] 2.3 request.check: refuse a must-do whose window has no plan year
```

The team ran out of time on the last scenario and left it for later. The change still validates:
OpenSpec checks a change's format, not whether its tasks are done. The six tests that were written
fail on the code of `steps/02`, where `must_do` is a stub field and `overrides` a stub function:

```text
step 03 tests on the code of step 02 (before): 20 passed, 6 failed
  FAILED test_capital_plan.py::test_a_must_do_project_is_started (AssertionError)
         assert {'A': 2027, 'B': 2027} == {'A': 2027, 'L': 2027}
  FAILED test_capital_plan.py::test_a_plan_without_the_must_do_is_refused (AssertionError)
         assert not True
  FAILED test_capital_plan.py::test_an_override_with_an_empty_reason_is_refused (AssertionError)
         assert None is not None
  FAILED test_capital_plan.py::test_a_reason_of_only_spaces_is_refused (AssertionError)
         assert None is not None
  FAILED test_capital_plan.py::test_an_override_for_an_unknown_project_is_refused (AssertionError)
         assert None is not None
  FAILED test_capital_plan.py::test_the_report_lists_each_override_with_its_reason (AssertionError)
         assert [] == ['A: Storm da...r order RO-7']
```

The first two tests use three projects: A ($600k, worth $1,000k), B ($400k, worth $600k) and L ($300k,
worth $50k), with $1,000k for one year. The best plan without a must-do is A and B; with L must-do, it
is A and L, since B and L together are worth less. The old code returns A and B.

## The Change, File by File

**`model.py`: `must_<pid>` in place of `once_<pid>`.** This is the one model change, and the page
leaves its code to the practice: the rows $`\text{once}_i`$ and $`\text{must}_i`$ of the model above
share their left side, the sum of the project's start variables over its window, and differ only in
their sense, $`\le 1`$ or $`= 1`$, and their name. The row of a project the request does not mark
stays exactly as it was in `steps/02`.

**`request.py`: the reason is checked before solving.** `reason.strip()` is what makes three spaces
count as no reason:

```diff
--- 02/capplan/request.py
+++ 03/capplan/request.py
@@
     if sum(request.shares.values()) > 100:
         raise ValueError(f"the shares add up to {sum(request.shares.values())}%, more than 100")
+    pids = {p.pid for p in projects}
+    for pid, reason in request.must_do.items():
+        if pid not in pids:
+            raise ValueError(f"a must-do override names {pid!r}, which is not in the portfolio")
+        if not reason.strip():
+            raise ValueError(f"the must-do override of {pid} has no recorded reason")
```

`strip()` removes tabs and newlines as well as spaces, so a reason made of a tab and a space is no
reason either. Without it, a check written `if not reason` lets any such string through: a tab is an
ordinary character, `not` of a string is `False` whenever the string is not empty, and testing it
raises nothing, not even a `TypeError`:

```text
not '   ' is False; '   '.strip() is ''
not '\t ' is False; '\t '.strip() is ''
not '\t\n' is False; '\t\n'.strip() is ''
```

**`report.py`: `overrides` lists each override and its reason**, sorted by project id, so the
report says who was forced and why next to the plan:

```diff
--- 02/capplan/report.py
+++ 03/capplan/report.py
@@
 def overrides(request: Request) -> list[str]:
-    """Stub: the next lesson writes it."""
-    return []
+    """Each must-do override with its recorded reason, by project id."""
+    return [f"{pid}: {reason.strip()}" for pid, reason in sorted(request.must_do.items())]
```

All 26 tests pass after the change:

```text
step 03 tests on the code of step 03 (after): 26 passed, 0 failed
tests step 03 adds or changes: 6; removes: 0
```

## What the Override Costs, and What the Report Says

The 40 projects again, with the share and P039 must-do:

```text
steps/03 plan, P039 must-do: 12 started, value $12,839k (OPTIMAL); P039 starts in 2030
the override costs $397k of value
report: must-do P039: Regulator order RO-7, Plainsview feeder
must_do {'P039': ''}: refused, the must-do override of P039 has no recorded reason
must_do {'P039': '   '}: refused, the must-do override of P039 has no recorded reason
must_do {'P999': 'Regulator order RO-7, Plainsview feeder'}: refused, a must-do override names 'P999', which is not in the portfolio
```

The plan still starts 12 projects, now including P039, and is worth $397k less. That number is the
price of the regulator's order, and the planners can quote it, because the value was never inflated.

## Archive Warns About the Open Tasks, and Does Not Block

`specs_check.py list` shows the change with its tasks counted, as `openspec list` does:

```text
== list, the change proposed
Changes:
  add-must-do-override         12/14 tasks
Specs:
  capital-plan                 requirements 7
  spec-checks                  requirements 5
```

The real CLI, on a copy of the same proposed change, counts the same 12 of 14 tasks. It lists only
the change (`openspec list --specs` lists the specs) and adds how long ago the change last changed;
`specs_check.py list` on that copy prints the lines above:

```text
$ openspec list
Changes:
  add-must-do-override     12/14 tasks   just now
(exit 0)
-- specs_check.py list, the same folder, with the checker of steps/03
Changes:
  add-must-do-override         12/14 tasks
Specs:
  capital-plan                 requirements 7
  spec-checks                  requirements 5
```

OpenSpec's archive does not refuse a change with unchecked tasks: it warns, because a change can be
filed on purpose with work left. `specs_check.py` does the same:

```text
== archive
add-must-do-override: 2 task(s) not checked off in tasks.md (a warning, not a block)
specs/capital-plan/spec.md: updated
moved to changes/archive/2026-11-04-add-must-do-override
specs/capital-plan/spec.md after archive: the same as steps/03
specs/spec-checks/spec.md after archive: the same as steps/03
```

The real `openspec archive` gives the same warning, goes on because of `--yes`, and writes the same
living specs; its archive folder is dated with the day it runs (`<today>`):

```text
$ openspec archive add-must-do-override --yes
Task status: 12/14 tasks
Warning: 2 incomplete task(s) found. Continuing due to --yes flag.
Specs to update:
  capital-plan: update
Applying changes to openspec/specs/capital-plan/spec.md:
  + 4 added
Totals: + 4, ~ 0, - 0, → 0
Specs updated successfully.
Change 'add-must-do-override' archived as '<today>-add-must-do-override'.
(exit 0)
specs/capital-plan/spec.md after openspec archive: the same as steps/03
specs/spec-checks/spec.md after openspec archive: the same as steps/03
```

The living spec now states a scenario, "A must-do that cannot start in the plan is refused", that no
test checks and no code keeps. The warning scrolled past. The last lesson of this module comes
back to it.

## What the Step Did to the Code

```text
03              136            309     26            16         27  model.build (10)
```

Eleven planner lines, and `build` one branch more for the must-do test. `request.check` now holds two
kinds of rule, shares and overrides, in one function; it is still short, but the next check added to
it should make it two functions.

**Practice.** This lesson's project practice starts from the code of `steps/02`, with the specs and
tests of `steps/03`. It is graded by those tests and by a check that `main.py` prints
`steps/03/expected/report.txt`.

<!-- practice 1 -->

## Summary

- **A must-do is a rule about the plan, so it is a row:** $`\sum_t x_{i,t} = 1`$ in place of
  $`\le 1`$. The model still chooses the year.
- **Inflating a value forces nothing and hides the price.** With the equality, the drop in value is
  the override's price.
- **The reason is data the model never reads,** checked before solving and printed with the plan.
- **An edge case worth a scenario is worth a test:** three spaces are no reason, and `not "   "` is
  false in Python.
- **Archive warns about unchecked tasks and does not block.** A scenario can reach the living spec
  with no test behind it.

## Reference

| Rule | Row | Code name |
| --- | --- | --- |
| must-do | $`\sum_{t \in T_i} x_{i,t} = 1`$, for $`i \in M`$ | `must_<pid>` |
| once, for the others | $`\sum_{t \in T_i} x_{i,t} \le 1`$, for $`i \in P \setminus M`$ | `once_<pid>` |

| Situation | `openspec archive` |
| --- | --- |
| the change does not validate | refuses |
| unchecked tasks in `tasks.md` | warns, and archives |

**Further reading:** [CP-SAT Solver (OR-Tools docs)](https://developers.google.com/optimization/cp/cp_solver) (linear constraints over integer variables, as the must row is); [Concepts (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/concepts.md) (the design is optional, and tasks are checked off as the work is done); [Troubleshooting (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/troubleshooting.md) (archive warns about incomplete tasks and does not block); [CLI reference (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/cli.md) (`openspec list` and what `archive` does, step by step). Lessons 6.5.1 (must-do and discretionary groups), 6.5.6 (manual overrides as fixed bounds) and 12.1.2 (overrides with an audit trail) are the course's background for this step.

## Challenges

1. The auditors also want the name of who asked for each override. Write the requirement's new text,
   and say which delta section the change uses.
2. A must-do project's window is 2027 to 2028, and the Plains share leaves 2027 empty. Predict what
   the plan does, and which rule decides the year.
3. Write a scenario for two must-do projects that cannot both fit one year's budget but fit in two
   years, and the test that pairs an allowed and a refused plan.

## Design Note: Archiving With Open Tasks Is Allowed, and That Is the Risk

OpenSpec lets a change be archived with work left, and for good reason: a change can be filed in
part, on purpose, with the rest planned. The cost is that the living spec then states something the
code does not do, and nothing in the format says so. This project accepted the warning and moved on.
The fix is not to forbid open tasks; it is a check that compares the living specs with the tests, run
on every change, which is the last lesson of this module.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**must_do.py.** Picks the project the plan likes least, plans the 40 invented projects with it as a
must-do, prints the report's override line, three refusals and what `not` and `strip()` make of
white space, lists, validates and archives the change, and runs the step's tests before and after (*every section*). *Try:* Make the must-do a
project that may only start in 2027. Predict the plan's status with the Plains share on, then run it.

**openspec_cli.py.** Runs the real OpenSpec CLI on a temporary copy of every snapshot and every
proposed change (lesson 14.4.1 describes it); this lesson quotes its list and archive of
`add-must-do-override` (*Archive warns about the open tasks*). *Try:* Tick the two open tasks in the
copy's `tasks.md` before the archive. Predict the `Task status` line and the `openspec list` line,
then run it.

- Program: [must_do.py](src/must_do.py)
- Program: [openspec_cli.py](src/openspec_cli.py)
- Program: [growth.py](src/growth.py)
- Library: [changes.py](src/changes.py)
- Library: [steps.py](src/steps.py)
