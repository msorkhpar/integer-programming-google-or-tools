# 14.4.2 A Regional Spend Share: The First Change From Proposal to Archive

The living specs of the last lesson describe the planner as it is. The first real change arrives
from the rate-case settlement for the Plains region:

> **Request 2.** Plains should get its fair share of the work: at least a quarter of the capital
> spend, every year. The settlement is signed; the plan for the next cycle must keep it.

It reads like ten minutes of code, one row a year. Spec-driven development makes it a change first:
a folder, `openspec/changes/add-regional-share/`, with a proposal, a spec delta, a design and tasks,
reviewed before any code. This lesson takes the change through the whole loop. The code before it is
snapshot `steps/01`; after it, `steps/02`. GridCap and its settlement are fictional.

## The Planner Has No Share Rule, and Plains Gets Nothing in Four Years of Five

`regional_share.py` plans the 40 invented projects with the code of `steps/01`, and reports the
Plains share of each year's spend:

```text
Plains has 10 of the 40 projects; the Plains projects that may start in each year: 0 4 4 6 2
steps/01, no share      : value $18,616k, Plains share by year   0%   0%   0%   0%  41%
```

Plains projects are worth less per $k than the others in this portfolio, so a planner that only
maximizes value leaves them for last. No living requirement says otherwise: the capital-plan spec
has a budget, a start window, a cap and the most valuable plan, and nothing about regions.

## Two Questions Go Back to the Planners Before the Proposal

"A quarter of the capital spend, every year" leaves two choices open, and each is a different rule:

- **A share of what?** Of the yearly budget, or of what the plan actually spends that year? With the
  budget, a year that spends little must still give Plains a quarter of the whole budget.
- **When?** The note says every year; a share over the whole plan would let Plains catch up later.

The modeler does not choose. The questions go back to the planners, who own the rule, and their
answers go into the change: the share is of what the plan spends, and it holds in every plan year.
The design records both answers under its Context, so a reviewer can see what was asked and decided.

## The Change Folder: Proposal, Delta, Design and Tasks

The **proposal** says why and what, in the planners' words:

<!-- snapshot: steps/02/openspec/changes/archive/2026-11-03-add-regional-share/proposal.md -->
```markdown
## Why
The rate-case settlement for the Plains region commits GridCap to spend at least a quarter of each
year's capital spend on Plains projects. Plains projects are worth less per $k than the others, so
the planner, which keeps no such rule, leaves Plains short in most years.

## What Changes
- A request may name regions with a least share, in whole percent, of what the plan spends in every
  plan year, and the planner keeps every share in every year.
- Shares no plan could keep are refused before the planner solves.
```

Under **Capabilities**, it lists `capital-plan` as modified: this change adds requirements to an
existing living spec. The **spec delta**, `specs/capital-plan/spec.md`, has one section,
`## ADDED Requirements`, with two requirements. The first states the rule:

<!-- snapshot: steps/02/openspec/changes/archive/2026-11-03-add-regional-share/specs/capital-plan/spec.md -->
```markdown
## ADDED Requirements

### Requirement: Regional spend share
The planner SHALL give each region the request names at least its share, in whole percent, of what
the plan spends in every plan year.

#### Scenario: A share is kept at its boundary
- **GIVEN** a share of 25% for Plains
- **WHEN** a plan spends $1,000k in 2027, $250k of it on Plains
- **THEN** the plan is allowed
- **AND** the same plan with a $10k North project added in 2027 is refused

#### Scenario: A year with no spend keeps the share
- **GIVEN** a share of 25% for Plains
- **WHEN** a plan spends nothing in 2028
- **THEN** 2028 keeps the share
- **AND** a plan whose only 2028 start is a North project is refused

#### Scenario: The plan keeps every share
- **GIVEN** three projects whose most valuable plan, with no share, starts no Plains project
- **WHEN** the planner plans with a share of 25% for Plains
- **THEN** every year of the plan gives Plains at least 25% of its spend
```

Each scenario pins the rule where a careless reading breaks it. The first sits on the boundary:
$250k of $1,000k is exactly 25%, and $250k of $1,010k is under it, so a rule that is a little off in
either direction fails it. The second is the year with no spend, where the share, a ratio, is not
defined. The third checks the plan, not only a fixed list. The second requirement, **Shares are
checked before solving**, has three scenarios: a share outside 0 to 100, shares adding up to more
than 100, and a share for a region with no project are refused with a message.

The **design**, `design.md`, is where the formulation goes. OpenSpec keeps the how out of the spec
and in the design; for a model, the how is the rows. Its decisions, in short:

<!-- snapshot: steps/02/openspec/changes/archive/2026-11-03-add-regional-share/design.md -->
```markdown
### Decision: the share as a linear row
A share is a ratio of two spends, which is not linear. Multiplying both sides by the year's spend,
which is never negative, and by 100 gives one linear row per named region and year:
100 times the region's spend is at least the share times the year's spend. Every coefficient is an
integer, so a plan exactly at the share is allowed and one $k under it is refused. No new variable.
```

Integer coefficients matter twice here. They make the boundary exact, $`100 \times 250 = 25 \times
1{,}000`$ with nothing to round, and CP-SAT asks for them: its documentation says every constraint
must be stated with integers, scaled up if need be. The **tasks** then order the work, tests first:

<!-- snapshot: steps/02/openspec/changes/archive/2026-11-03-add-regional-share/tasks.md -->
```markdown
## 1. Tests from the scenarios
- [x] 1.1 Add Request.shares as a stub that the model ignores
- [x] 1.2 Write one test per scenario in tests/test_capital_plan.py
- [x] 1.3 Run them on the code before the change and see each fail on an assertion
```

## Review the Proposal, Then the Deltas, Then the Tasks; Validate the Format

OpenSpec's guide to reviewing a change reads the files in the order that lets a reviewer stop
earliest: the proposal first (is this the right problem?), then the spec deltas (is "done" defined
correctly, and what is missing?), the design for a bigger change, and the tasks last. Here the review
is the planners' and the modeler's. The planners check the scenarios against the settlement; the
modeler checks that every scenario can be a test. Then the format, with the change still active:

```text
== validate --strict, the change proposed
valid   spec capital-plan
valid   spec spec-checks
valid   change add-regional-share
strict: 0 item(s) failed
```

`specs_check.py` mirrors the CLI's validator and is not the CLI. The real CLI, which the course
image now runs, checks the same proposed change with `openspec validate --all --strict`
(`openspec_cli.py`):

```text
== add-regional-share, proposed on steps/01
$ openspec validate --all --strict
✓ change/add-regional-share
✓ spec/capital-plan
✓ spec/spec-checks
Totals: 3 passed, 0 failed (3 items)
(exit 0)
```

The same three items pass. The CLI writes them as `change/...` and `spec/...` and lists the change
first; `specs_check.py` lists the living specs first.

## The Model

The planner's model with the share. Changes from the last lesson are marked.

**Sets.** $`P`$, the projects; $`Y`$, the plan years; $`T_i \subseteq Y`$, the years project
$`i`$ may start; $`R`$, the regions, and $`P_r \subseteq P`$ the projects of region $`r`$
$`\leftarrow`$; $`S \subseteq R`$, the regions the request names $`\leftarrow`$.

**Parameters.** $`c_i`$, cost ($k); $`v_i`$, value ($k); $`B`$, the yearly budget ($k); $`K`$, the
start cap; $`s_r \in \{0, 1, \dots, 100\}`$, the least share of region $`r \in S`$, in whole
percent, with $`\sum_{r \in S} s_r \le 100`$ $`\leftarrow`$.

**Variables.** $`x_{i,t} \in \{0,1\}`$ for $`i \in P`$, $`t \in T_i`$. The share adds none.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_i \, x_{i,t}
```

**Constraints.** With $`\text{spend}_y = \sum_{i \in P :\, y \in T_i} c_i \, x_{i,y}`$ and
$`\text{spend}_{r,y}`$ the same sum over $`P_r`$ only:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P && \text{(once}_i) \\
\text{spend}_y &\le B && \forall y \in Y && \text{(budget}_y) \\
\sum_{i \in P :\, y \in T_i} x_{i,y} &\le K && \forall y \in Y && \text{(starts}_y) \\
100\, \text{spend}_{r,y} &\ge s_r \, \text{spend}_y && \forall r \in S \text{ with } s_r > 0,\ y \in Y && \text{(share}_{r,y}) \quad \leftarrow \text{this lesson}
\end{aligned}
```

In a year with no spend the share row reads $`0 \ge 0`$ and holds, which is the second scenario. A
share of 0 sets no minimum and gets no row. The rows are named `share_plains_2027` to
`share_plains_2031`. Lesson 6.5.5 writes a plan-wide program share the same way.

## Tests First: Six Scenarios, Six Tests, Six Failures on the Old Code

Each scenario becomes a test in `tests/test_capital_plan.py`, named after it. A test of a rule pairs
a plan the rule allows with one it refuses, so that a model with no rule at all cannot pass it:

<!-- snapshot: steps/02/tests/test_capital_plan.py -->
```python
def test_a_share_is_kept_at_its_boundary():
    projects = [project("P", 250, region="plains"), project("N", 750), project("M", 10)]
    request = Request(budget=5000, years=3, shares={"plains": 25})
    assert allows(projects, request, {("P", 2027), ("N", 2027)})                    # 250 of 1,000
    assert not allows(projects, request, {("P", 2027), ("N", 2027), ("M", 2027)})   # 250 of 1,010
```

The budget of $5,000k is one no test plan comes near, so only the share can refuse. The three tests
of the second requirement use a helper, `refusal`, that returns the message of the `ValueError` a call
raises, or `None` when it raises none. Run on the code of `steps/01`, where `Request.shares` is a stub
the model ignores, every new test fails on its assertion:

```text
step 02 tests on the code of step 01 (before): 14 passed, 6 failed
  FAILED test_capital_plan.py::test_a_share_is_kept_at_its_boundary (AssertionError)
         assert not True
  FAILED test_capital_plan.py::test_a_year_with_no_spend_keeps_the_share (AssertionError)
         assert not True
  FAILED test_capital_plan.py::test_the_plan_keeps_every_share (AssertionError)
         assert {'N1': 2027, 'N2': 2027} == {'N1': 2027, 'P1': 2027}
  FAILED test_capital_plan.py::test_a_share_outside_0_to_100_is_refused (AssertionError)
         assert None is not None
  FAILED test_capital_plan.py::test_shares_adding_up_to_more_than_100_are_refused (AssertionError)
         assert None is not None
  FAILED test_capital_plan.py::test_a_share_for_a_region_with_no_project_is_refused (AssertionError)
         assert None is not None
```

Read where each failed. In the two boundary tests the allowed plan passed and the refused one was let
through (`assert not True`): a model with no share allows everything. So a test with only the
allowed plan is too weak, even one sitting exactly on the boundary: it passes on code with no share
at all. The plan test got the two North projects, the old optimum. The three checks raised nothing.

## The Change, File by File

**`request.py`: the field becomes real, and a check refuses impossible shares.** `check` runs before
any model is built. Shares that add up to more than 100, or a share for a region with no project,
leave only plans that spend nothing; the model would return such a plan with no word about why, so
the check refuses the request with a message instead:

```diff
--- 01/capplan/request.py
+++ 02/capplan/request.py
@@
     years: int = 5                # plan years, counted from FIRST_YEAR
     max_starts: int | None = 3    # most projects that may start in one year; None: no cap
+    shares: dict[str, int] = field(default_factory=dict)    # region -> least % of each year's spend
     # Stub: the next lesson gives this field its meaning; this model ignores it.
-    shares: dict[str, int] = field(default_factory=dict)
+    must_do: dict[str, str] = field(default_factory=dict)
 
     def plan_years(self) -> list[int]:
         return list(range(FIRST_YEAR, FIRST_YEAR + self.years))
+
+
+def check(projects: list[Project], request: Request) -> None:
+    """Refuse, before any model is built, a request that no plan could keep."""
+    regions = {p.region for p in projects}
+    for region, pct in request.shares.items():
+        if region not in regions:
+            raise ValueError(f"a share for {region!r}, which has no project in the portfolio")
+        if not 0 <= pct <= 100:
+            raise ValueError(f"the share of {region} is {pct}%, outside 0 to 100")
+    if sum(request.shares.values()) > 100:
+        raise ValueError(f"the shares add up to {sum(request.shares.values())}%, more than 100")
```

**`model.py`: one row family, as the design wrote it.** `spend` is the same helper the budget row
uses, so the two rules cannot disagree about what a year spends:

```diff
--- 01/capplan/model.py
+++ 02/capplan/model.py
@@
             starts = sum(var for (_, year), var in x.items() if year == y)
             model.add(starts <= request.max_starts).with_name(f"starts_{y}")
+    for region, pct in request.shares.items():
+        if pct == 0:
+            continue                             # a share of 0 sets no minimum
+        members = [p for p in projects if p.region == region]
+        for y in request.plan_years():
+            # 100 * (the region's spend) >= pct * (the year's spend): the share as a linear row.
+            model.add(100 * spend(members, x, y) >= pct * spend(projects, x, y)).with_name(f"share_{region}_{y}")
     model.maximize(sum(p.value * x[p.pid, y] for p in projects for y in window(p, request)))
     return Built(model, x)
```

**`plan.py`: both entry points check first.** `plan` and `allows` call `check` before `build`.
**`report.py`: `share_by_year`** counts each region's percent from the starts, apart from the model,
so a test can compare the two. It replaces last lesson's stub, and `overrides` becomes the stub for
the next lesson.

After the change all 20 tests pass:

```text
step 02 tests on the code of step 02 (after): 20 passed, 0 failed
tests step 02 adds or changes: 6; removes: 0
```

## What the Share Costs, and What the Planners Should See

The same 40 projects, with the code of `steps/02` and a 25% share for Plains:

```text
steps/02, Plains at 25% : value $13,236k, Plains share by year   -   28%  33%  29%  41%
the share costs $5,380k of value (OPTIMAL)
share rows: 5, share_plains_2027 to share_plains_2031
shares {'plains': 60, 'coast': 50}: refused, the shares add up to 110%, more than 100
shares {'south': 10}: refused, a share for 'south', which has no project in the portfolio
```

Every year with spend gives Plains at least 25%. And 2027 spends nothing at all: no Plains project
may start in 2027, so the only 2027 that keeps the share is an empty one. That is exactly what the
second scenario says, and it costs a whole year of work. The scenarios made it visible on paper; the
run shows its price, $5,380k of value. It goes back to the planners as a finding, not a bug: if the
settlement meant "in every year with Plains work available", that is a new change, with its own
delta.

In the share line, `-` marks a year that spends nothing, where a share is not defined. The project's
own report, `main.py`, prints a line only for the years the plan spends anything at this step, with
the share rounded to a whole percent (`f"{pct:.0f}"`). Two lessons on, in *Carry-Over: A MODIFIED
Budget Rule and a RENAMED Requirement*, the report prints every plan year, and a year with no spend
shows `plains 0%`.

## Archive: the Requirements Join the Living Spec

```text
== archive
specs/capital-plan/spec.md: updated
moved to changes/archive/2026-11-03-add-regional-share
specs/capital-plan/spec.md after archive: the same as steps/02
specs/spec-checks/spec.md after archive: the same as steps/02
```

The real `openspec archive`, on another copy of the proposed change, counts the two ADDED
requirements and writes the same living specs; only its archive folder is dated with the day it runs
(`<today>`), where `specs_check.py` takes `--date`:

```text
$ openspec archive add-regional-share --yes
Task status: ✓ Complete
Specs to update:
  capital-plan: update
Applying changes to openspec/specs/capital-plan/spec.md:
  + 2 added
Totals: + 2, ~ 0, - 0, → 0
Specs updated successfully.
Change 'add-regional-share' archived as '<today>-add-regional-share'.
(exit 0)
specs/capital-plan/spec.md after openspec archive: the same as steps/02
specs/spec-checks/spec.md after openspec archive: the same as steps/02
archive folder: <today>-add-regional-share
every file under openspec/, the archive's date set to steps/02's: the same as steps/02
```

The ADDED requirements are appended to the living capital-plan spec, which now has 7 requirements,
and the change folder moves to `changes/archive/2026-11-03-add-regional-share/`, proposal, design and
tasks included. The next change starts from a spec that already has the share.

## What the Step Did to the Code

```text
02              125            309     20            12         20  model.build (9)
```

The planner grew from 101 to 125 lines, and `build` from 5 to 9 on the branching count: a loop over
the named regions, the skip of a zero share, a comprehension that filters a region, and a loop over
the years. The specs grew by 2 requirements and 6 scenarios, and the tests by 6, one per scenario.

**Practice.** This lesson's project practice starts from the code of `steps/01`, with the specs and
tests of `steps/02`. It is graded by those tests and by a check that `main.py` prints
`steps/02/expected/report.txt`.

<!-- practice 1 -->

## Summary

- **A request becomes a change folder before it becomes code:** a proposal (why, what, which
  capabilities), a spec delta, a design for the formulation, and tasks with tests first.
- **Open questions go back to the rule's owners.** Share of the spend or the budget, each year or
  over the plan: the planners answer, and the design records it.
- **A share is a ratio, and the row is linear:** $`100\, \text{spend}_{r,y} \ge s_r \, \text{spend}_y`$,
  with integer coefficients, which CP-SAT requires and which make the boundary exact.
- **Each scenario is a test that pairs an allowed and a refused plan**, and each fails on the old code
  before the code changes.
- **Archive appends the ADDED requirements to the living spec** and keeps the change for its history.

## Reference

| Delta section | Archive does |
| --- | --- |
| `## ADDED Requirements` | appends each requirement to the living spec |
| `## Purpose` | seeds the Purpose of a capability the change creates; ignored for an existing one |

| Rule | Row | Code name |
| --- | --- | --- |
| regional share | $`100\, \text{spend}_{r,y} \ge s_r \, \text{spend}_y`$ | `share_<region>_<year>` |

**Further reading:** [CP-SAT Solver (OR-Tools docs)](https://developers.google.com/optimization/cp/cp_solver) (all CP-SAT constraints are over integers, which is why the share is a whole percent); [Concepts (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/concepts.md) (changes as folders, the proposal, design and tasks artifacts, ADDED deltas and what archive does with them); [Reviewing a change (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/reviewing-changes.md) (read the proposal, then the deltas, then the tasks, and look for what is missing); [Writing good specs (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/writing-specs.md) (one behaviour per requirement, scenarios for the edge cases, the right kind of delta); [proposal template (OpenSpec source, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/schemas/spec-driven/templates/proposal.md) and [design template](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/schemas/spec-driven/templates/design.md) (Why, What Changes, Capabilities, Impact; Context, Goals, Decisions, Risks). Lessons 6.5.5 (minimum and maximum spend) and 12.3.1 (testing one constraint at a time) are the course's background for this step.

## Challenges

1. The planners come back: the share should hold only in years where at least one project of the
   region may start. Write the new requirement text and the scenario for 2027, and say which delta
   section it goes in.
2. A colleague writes the share row as `4 * spend(members) >= spend(projects)` for 25%. Which shares
   can that form state, and which can it not?
3. Write a scenario for a share of exactly 100%, and predict what the plan of the 40 projects does
   with it.

## Design Note: The Formulation Lives in the Design, Not the Spec

The spec says "at least its share, in whole percent, of what the plan spends in every plan year". The
row, $`100\, \text{spend}_{r,y} \ge s_r \, \text{spend}_y`$, is in `design.md`. Had the spec held the
row, the planners would have been asked to sign a piece of algebra, and the choice it encodes (spend,
not budget; every year, not the plan) would have been made by whoever wrote the row, before the
planners could see that there was a choice. OpenSpec's own test for what belongs in a spec fits: if
the implementation can change without changing what anyone can observe, it is not spec. The row could
be written another way; the share could not.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**regional_share.py.** Plans 40 invented projects with and without the share, prints the Plains share
of each year, the share rows and two refusals, validates the proposed change, runs the step's tests
before and after, and archives the change (*every section*). *Try:* Lower the share to 10%. Predict
whether 2027 still spends nothing, then run it.

**openspec_cli.py.** Runs the real OpenSpec CLI on a temporary copy of every snapshot and every
proposed change (lesson 14.4.1 describes it); this lesson quotes its validation and archive of
`add-regional-share` (*Review the proposal; Archive*). *Try:* Delete the `--yes` from the archive
command. Predict what the CLI does with no terminal to confirm in, then run it.

- Program: [regional_share.py](src/regional_share.py)
- Program: [openspec_cli.py](src/openspec_cli.py)
- Program: [growth.py](src/growth.py)
- Library: [changes.py](src/changes.py)
- Library: [steps.py](src/steps.py)
