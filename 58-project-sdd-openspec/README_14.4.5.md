# 14.4.5 Retiring the Yearly Start Cap: A REMOVED Requirement

The last lesson found that the yearly start cap, not the budget, limits the plan. The planners asked
where the cap came from, and the answer came back from engineering:

> **Request 5.** The cap of three starts a year was the design-review board's capacity: it met once a
> quarter and could not review more. Reviews are now done as each design is ready. Retire the cap.
> And make sure nobody who still sends it gets a different plan without being told.

The code before this lesson is snapshot `steps/04`; after it, `steps/05`. GridCap and its review
board are fictional.

## A Rule That Goes Away Is Removed From the Spec, With Its Reason

Deleting the rows is the easy part. The living spec still says "Yearly start cap: the planner SHALL
start no more projects in a year than the request's start cap, which is 3 when the request does not
set one", and as long as it says so, the spec and the code disagree. OpenSpec's delta for behaviour
going away is `## REMOVED Requirements`. It names the requirement, and archive deletes it from the
living spec. A REMOVED entry needs no scenario; OpenSpec's guide asks for a line on why, and its own
specs give a **Reason** and a **Migration** for each removal:

<!-- snapshot: steps/05/openspec/changes/archive/2026-11-06-retire-yearly-start-cap/specs/capital-plan/spec.md -->
```markdown
## REMOVED Requirements

### Requirement: Yearly start cap
**Reason**: The cap stood for the design-review board's capacity, which no longer limits starts.

**Migration**: Remove max_starts from requests. A request that still sets it is refused with a
message naming this change.
```

The archived change keeps that text forever, under `changes/archive/`, so the reason outlives the
requirement: a year from now, someone asking "didn't we have a start cap?" finds when it went and why.

## What Replaces It: Two Requirements, Because Removal Is a Behaviour Change

The second half of the request is the hard one. A caller that sets `max_starts=3` today gets a plan
with at most three starts a year. If the planner silently ignored the field after the change, that
caller would get a different plan, with no error and no warning. And a caller that never set it gets
a different plan too, since the default of 3 goes. So the same delta adds two requirements:

<!-- snapshot: steps/05/openspec/changes/archive/2026-11-06-retire-yearly-start-cap/specs/capital-plan/spec.md -->
```markdown
### Requirement: Retired start cap is refused
The planner SHALL refuse, before solving, a request that sets the retired yearly start cap, with a
message naming the change that retired it.

#### Scenario: A request that sets the retired cap is refused
- **WHEN** a request sets a start cap of 3
- **THEN** the planner refuses it with a message naming retire-yearly-start-cap
- **AND** a request that sets no cap is accepted

#### Scenario: A retired cap of zero is refused too
- **WHEN** a request sets a start cap of 0
- **THEN** the planner refuses it with the same message
```

The second, **Starts per year are not capped**, has one scenario: four $10k projects may all start
in 2027. That is the new behaviour, stated positively, so that a test can check it. A REMOVED entry
alone has no scenario, and nothing could fail if the cap came back.

"A retired cap of zero" is a scenario of its own for the same reason as the reason of three spaces
in the must-do change: a
check written as `if request.max_starts:` lets 0 through, because 0 is false in Python, and a request
with a cap of 0 would then plan as if it had none.

The proposal marks the change as breaking for callers, and its Impact names who must act: "any
request that sets max_starts must drop it".

## The Model

The planner's model without the cap. Changes from the last lesson are marked.

**Sets.** $`P`$, $`Y`$, $`T_i`$, $`R`$, $`P_r`$, $`S`$ and $`M`$ as before.

**Parameters.** $`c_i`$, $`v_i`$, $`B`$, $`s_r`$, $`C`$ and $`\bar r`$ as before. $`K`$ is gone
$`\leftarrow`$.

**Variables.** $`x_{i,t} \in \{0,1\}`$ for $`i \in P`$, $`t \in T_i`$; $`r_y \in \{0, 1, \dots,
\bar r\}`$ for $`y \in Y \setminus \{y_n\}`$.

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

The family $`\text{starts}_y`$, $`\sum_{i} x_{i,y} \le K`$, is removed $`\leftarrow`$. The refusal of
a request that sets the cap is not a row: it happens before any model is built.

## Tests First, and the Removed Scenario's Test Goes With It

The test of the removed scenario, `test_more_starts_than_the_cap_are_refused`, cannot stay: on the new
code it fails, because four starts in a year are now allowed. `retire_cap.py` runs the tests of
`steps/04` on the code of `steps/05` to show it:

```text
== the tests of steps/04 on the code of steps/05
  FAILED test_capital_plan.py::test_more_starts_than_the_cap_are_refused (AssertionError)
         assert not True
```

So the tasks delete it first, with its scenario, and then add one test per new scenario. On the code
of `steps/04`, the three new tests fail:

```text
step 05 tests on the code of step 04 (before): 29 passed, 3 failed
  FAILED test_capital_plan.py::test_four_starts_in_one_year_are_allowed (AssertionError)
         assert False
  FAILED test_capital_plan.py::test_a_request_that_sets_the_retired_cap_is_refused (AssertionError)
         assert None is not None
  FAILED test_capital_plan.py::test_a_retired_cap_of_zero_is_refused_too (AssertionError)
         assert None is not None
step 05 tests on the code of step 05 (after): 32 passed, 0 failed
tests step 05 adds or changes: 3; removes: 1
```

The first fails on the old default, the cap of 3; the other two because the old code reads the cap
instead of refusing it.

## The Change, File by File

**`model.py`: the `starts_<year>` rows are deleted.** Three lines go, and nothing replaces them:

```diff
--- 04/capplan/model.py
+++ 05/capplan/model.py
@@
         model.add(spend(projects, x, y) + carry.get(y, 0) <= request.budget + carry.get(y - 1, 0)
                   ).with_name(f"budget_{y}")
-        if request.max_starts is not None:
-            starts = sum(var for (_, year), var in x.items() if year == y)
-            model.add(starts <= request.max_starts).with_name(f"starts_{y}")
     for region, pct in request.shares.items():
         if pct == 0:
```

**`request.py`: the field stays, defaults to `None`, and any other value is refused.** The field is
kept, not deleted, so that a caller that still passes it gets the refusal and its message rather than
a `TypeError` about an unexpected argument. Only the default changes in the field's line:

```diff
--- 04/capplan/request.py
+++ 05/capplan/request.py
@@
     budget: int                   # $k for each plan year
     years: int = 5                # plan years, counted from FIRST_YEAR
-    max_starts: int | None = 3    # most projects that may start in one year; None: no cap
+    max_starts: int | None = None  # retired by the change retire-yearly-start-cap: must stay None
     shares: dict[str, int] = field(default_factory=dict)    # region -> least % of each year's spend
     must_do: dict[str, str] = field(default_factory=dict)   # project id -> the recorded reason
```

The refusal itself goes first in `check`, before the checks of shares and overrides, and its code is
the practice's to write. It refuses every value but `None`, 0 included, which a check written
`if request.max_starts:` would let through. Its message is fixed, because the step's report prints it:
`max_starts was retired by the change retire-yearly-start-cap; remove it from the request`. The
message names the change, which is the folder a reader opens under `changes/archive/` to learn why.

## What Retiring the Cap Does to the Plan

The 40 invented projects, with the Plains share, P039 must-do and 20% carry-over, under the default
request of each snapshot:

```text
steps/04, default request    12 started, value $12,839k (OPTIMAL); starts by year 0 3 3 3 3
steps/05, default request    26 started, value $19,897k (OPTIMAL); starts by year 0 7 6 6 7
max_starts=3: refused, max_starts was retired by the change retire-yearly-start-cap; remove it from the request
max_starts=0: refused, max_starts was retired by the change retire-yearly-start-cap; remove it from the request
```

Twenty-six projects instead of twelve, and $7,058k more value, from the same budget. The $19,897k is
the "no cap, 20%" plan of the last lesson, as it should be: that run set `max_starts=None` by hand,
and now the default is no cap.

## Validate and Archive: the Requirement Leaves the Living Spec

```text
== validate --strict, the change proposed
valid   spec capital-plan
valid   spec spec-checks
valid   change retire-yearly-start-cap
strict: 0 item(s) failed
```

Archive applies REMOVED before MODIFIED and ADDED, as it applies every delta. The requirement and its
scenario are gone from the living spec; the archived change keeps them, with the reason:

```text
== archive
specs/capital-plan/spec.md: updated
moved to changes/archive/2026-11-06-retire-yearly-start-cap
specs/capital-plan/spec.md after archive: the same as steps/05
specs/spec-checks/spec.md after archive: the same as steps/05
'Yearly start cap' in the living spec after archive: False
```

The real `openspec archive retire-yearly-start-cap --yes`, run by `openspec_cli.py` on another copy
of the proposed change, counts the two ADDED requirements and the one REMOVED, and writes the same
living specs; its archive folder is dated with the day it runs (`<today>`), where `specs_check.py`
takes `--date`:

```text
$ openspec archive retire-yearly-start-cap --yes
Task status: ✓ Complete
Specs to update:
  capital-plan: update
Applying changes to openspec/specs/capital-plan/spec.md:
  + 2 added
  - 1 removed
Totals: + 2, ~ 0, - 1, → 0
Specs updated successfully.
Change 'retire-yearly-start-cap' archived as '<today>-retire-yearly-start-cap'.
(exit 0)
specs/capital-plan/spec.md after openspec archive: the same as steps/05
specs/spec-checks/spec.md after openspec archive: the same as steps/05
archive folder: <today>-retire-yearly-start-cap
every file under openspec/, the archive's date set to steps/05's: the same as steps/05
```

One case this change does not meet: removing the last requirement of a capability. OpenSpec then
deletes the capability's whole spec file, and asks for that to be declared in the change's
`.openspec.yaml` as `retire_capabilities: true`, or archive stops. `specs_check.py` does not mirror
it, since this project never removes a whole capability.

## What the Step Did to the Code

```text
05              150            316     32            18         33  request.check (10)
```

The planner is one line shorter: three rows' lines went, two lines of check came. `build` is no
longer the most branching function; `request.check` is, at 10, holding three kinds of rule (the
retired cap, shares, overrides). The checker's 7 new lines are the stub of the next lesson's trace.

**Practice.** This lesson's project practice starts from the code of `steps/04`, with the specs and
tests of `steps/05`. It is graded by those tests and by a check that `main.py` prints
`steps/05/expected/report.txt`.

<!-- practice 1 -->

## Summary

- **Behaviour that goes away is REMOVED from the spec, with a Reason and a Migration.** Archive deletes
  the requirement and keeps the change, and the reason, in the archive.
- **A removal is a behaviour change, so it gets scenarios too:** what the planner now allows, and what
  it does with a caller that still sends the old setting.
- **Refuse a retired setting; do not ignore it.** Ignoring it would change a caller's plan without
  telling them.
- **The removed scenario's test is deleted with it;** on the new code it fails.
- **Retiring the cap more than doubled the plan:** 26 projects instead of 12, $7,058k more value.

## Reference

| Delta section | Holds | Archive does |
| --- | --- | --- |
| `## REMOVED Requirements` | `### Requirement: <name>`, with **Reason** and **Migration**; no scenario needed | deletes the requirement from the living spec |
| removing a capability's last requirement | `retire_capabilities: true` in the change's `.openspec.yaml` | deletes the spec file |

| Rule | Where | Code |
| --- | --- | --- |
| the cap is retired | before solving | `max_starts is not None` refused, naming `retire-yearly-start-cap` |

**Further reading:** [CP-SAT Solver (OR-Tools docs)](https://developers.google.com/optimization/cp/cp_solver) (the model is still integer linear rows, now without the starts family); [Writing good specs (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/writing-specs.md) (REMOVED for behaviour going away, with a line on why, and `retire_capabilities` for a capability's last requirement); [Concepts (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/concepts.md) (REMOVED requirements are deleted from the main spec on archive); [the openspec-conventions delta of `adopt-delta-based-changes` (OpenSpec's own archive, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/openspec/changes/archive/2025-08-19-adopt-delta-based-changes/specs/openspec-conventions/spec.md) (a removal gives its reason and its migration path, and the FROM/TO form of a rename); [CLI reference (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/cli.md) (`archive` and the retirement marker). Lessons 6.1.3 (at-most-k rows, as the cap was) and 12.3.3 (regression tests) are the course's background for this step.

## Challenges

1. Engineering says the board will be back for one year, 2029, with room for five reviews. Is that a
   new ADDED requirement or the old one restored? Write its text and one scenario.
2. Instead of refusing `max_starts`, a colleague proposes to log a warning and plan without the cap.
   Write the scenario that would describe that, and say what a caller who never reads logs sees.
3. Only the cap's test of `steps/04` fails on the new code. Explain why
   `test_the_plan_has_the_greatest_value_within_the_rules` still passes, although its brute force
   never applied a cap.

## Design Note: Keep the Field, Refuse Its Value

`Request.max_starts` could have been deleted from the dataclass. A caller that passed it would then
get Python's `TypeError: unexpected keyword argument`, which says nothing about why. Keeping the field
for one more cycle, with a default of `None` and a refusal that names the change, turns the removal
into a message a caller can act on. When no request has set it for a while, a later change can
delete the field, with a delta of its own if the refusal requirement goes with it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**retire_cap.py.** Plans the 40 invented projects under the default request of `steps/04` and
`steps/05`, shows the two refusals and the old test that the new code fails, validates and archives
the change, and runs the step's tests before and after (*every section*). *Try:* Halve the budget
to $1,500k. Predict whether retiring the cap still adds projects, then run it.

**openspec_cli.py.** Runs the real OpenSpec CLI on a temporary copy of every snapshot and every
proposed change (lesson 14.4.1 describes it); this lesson quotes its archive of
`retire-yearly-start-cap` (*Archive*). *Try:* Predict the `openspec list --specs` line for
capital-plan on `steps/04` and on `steps/05`, then find both in the program's output.

- Program: [retire_cap.py](src/retire_cap.py)
- Program: [openspec_cli.py](src/openspec_cli.py)
- Program: [growth.py](src/growth.py)
- Library: [changes.py](src/changes.py)
- Library: [steps.py](src/steps.py)
