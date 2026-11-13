# 14.4.4 Carry-Over: A MODIFIED Budget Rule and a RENAMED Requirement

The first three changes added requirements. This one changes one that is already there, the rule
every plan has kept since the baseline. Finance sends it:

> **Request 4.** From the next cycle, money a year leaves unspent is not lost: it moves into the next
> year, up to a fifth of one year's budget. It moves forward only. No year may spend next year's
> money.

The code before this lesson is snapshot `steps/03`; after it, `steps/04`. GridCap and its finance
team are fictional.

## The Budget Requirement Is Wrong Now, So the Change Modifies It

The living capital-plan spec says, in its first requirement, "Yearly budget": the planner SHALL keep
what the plan spends in each plan year within the yearly budget. After finance's request that is no
longer true: a year may spend more than its budget when the year before left money unspent.
Adding a requirement next to it would leave two requirements that contradict each other. OpenSpec's
guide to deltas is plain about it: behaviour that already exists and is changing goes under
`## MODIFIED Requirements`, with the full new version of the requirement. If the requirement were
added instead, the spec would hold two competing rules; if new behaviour were marked as modified,
there would be nothing to replace.

The old name no longer fits either: the rule is not one budget per year any more. A rename has its
own delta section, `## RENAMED Requirements`, with a `FROM:` line and a `TO:` line. The delta of this
change uses three sections:

<!-- snapshot: steps/04/openspec/changes/archive/2026-11-05-add-budget-carry-over/specs/capital-plan/spec.md -->
```markdown
## RENAMED Requirements
- FROM: `### Requirement: Yearly budget`
- TO: `### Requirement: Yearly budget with carry-over`

## MODIFIED Requirements

### Requirement: Yearly budget with carry-over
The planner SHALL keep what the plan spends in each plan year within the yearly budget plus the
money carried into that year, counting each project's whole cost in the year it starts. Money a
year leaves unspent SHALL carry into the next year, up to the request's carry-over percent of one
yearly budget, and no year SHALL spend money of a later year.

#### Scenario: Spending up to the budget is allowed
- **GIVEN** a budget of $1,000k a year and no carry-over
- **WHEN** a plan starts a $600k project and a $400k project in 2027
- **THEN** the plan is allowed

#### Scenario: Spending over the budget is refused
- **GIVEN** a budget of $1,000k a year and no carry-over
- **WHEN** a plan starts a $600k project and a $410k project in 2027
- **THEN** the plan is refused

#### Scenario: Unspent money carries into the next year
- **GIVEN** a budget of $1,000k a year and a carry-over of 20%
- **WHEN** a plan spends $800k in 2027 and $1,200k in 2028
- **THEN** the plan is allowed
- **AND** the same plan with $10k more in 2028 is refused

#### Scenario: Carry-over above its cap is refused
- **GIVEN** a budget of $1,000k a year and a carry-over of 20%
- **WHEN** a plan spends $500k in 2027 and $1,250k in 2028
- **THEN** the plan is refused, since only $200k of the $500k left may carry
- **AND** the plan that spends $1,200k in 2028 is allowed

#### Scenario: Money cannot be borrowed from a later year
- **GIVEN** a budget of $1,000k a year and a carry-over of 20%
- **WHEN** a plan spends $1,100k in 2027 and $900k in 2028
- **THEN** the plan is refused
- **AND** the plan that spends $900k in 2027 and $1,100k in 2028 is allowed
```

A third section, `## ADDED Requirements`, adds **Carry-over is checked before solving**: a carry-over
outside 0 to 100 percent is refused.

## A MODIFIED Block Replaces the Whole Requirement, Scenarios Included

On archive, a MODIFIED block does not patch the old requirement; it replaces it, text and scenarios
together. So the block above repeats the two scenarios the old requirement had, "Spending up to the
budget is allowed" and "Spending over the budget is refused", with "and no carry-over" added to their
GIVEN steps: with no carry-over, the old rule still holds word for word, and the old tests still
pass unchanged. A MODIFIED block that left a scenario out would delete it from the living spec without
anyone deciding to. OpenSpec `2.0.0` refuses that, in `validate` and again in `archive`, and so does
`specs_check.py`. It also applies the sections in a fixed order on archive, RENAMED first, then
REMOVED, then MODIFIED, then ADDED, so a MODIFIED block must use the new name. `carry_over.py` plants
both mistakes in a copy of the delta:

```text
== the delta as written
issues: 0
== a MODIFIED block that drops a scenario
ERROR   capital-plan: MODIFIED "Yearly budget with carry-over" drops scenario(s) the living spec has: "Spending over the budget is refused"
== a MODIFIED block under the old name
ERROR   capital-plan: MODIFIED uses the old name of a RENAMED requirement: "Yearly budget"
```

These are errors, not warnings: plain validation fails too. They are the two ways a MODIFIED delta
loses behaviour silently, and that is why they block.

## The Design: a Bounded Carry Variable and a Budget Row That Balances

The change's design records the formulation. Each plan year but the last gets a variable for what it
passes on, and its two bounds state two of finance's rules:

<!-- snapshot: steps/04/openspec/changes/archive/2026-11-05-add-budget-carry-over/design.md -->
```markdown
### Decision: one bounded integer variable per year that passes money on
carry_y, in $k, is what year y passes to year y + 1, for every plan year but the last. Its bounds
state two rules at once: the lower bound 0 forbids borrowing from a later year, and the upper bound,
the carry-over percent of one yearly budget rounded down, is the cap.

### Decision: the budget row becomes a balance
spend_y + carry_y <= budget + carry_(y-1), with carry of the year before the plan and carry of the
last year both 0. A year may pass on only what it was given and did not spend.
```

The design also records an alternative it rejected: one pooled budget for the whole plan, which would
let one year spend every other year's money, which finance did not allow. Lesson 6.4.4 builds
carry-over budgets the same way; lesson 2.1.3 shows the pattern in a first LP.

## The Model

The planner's model with carry-over. Changes from the last lesson are marked.

**Sets.** $`P`$, $`Y = \{y_1, \dots, y_n\}`$, $`T_i`$, $`R`$, $`P_r`$, $`S`$ and $`M`$ as before.

**Parameters.** $`c_i`$, $`v_i`$, $`B`$, $`K`$ and $`s_r`$ as before; $`C \in \{0, 1, \dots,
100\}`$, the carry-over percent $`\leftarrow`$; $`\bar r = \lfloor C B / 100 \rfloor`$, the most a
year may pass on ($k) $`\leftarrow`$.

**Variables.** $`x_{i,t} \in \{0,1\}`$ for $`i \in P`$, $`t \in T_i`$; $`r_y \in \{0, 1, \dots,
\bar r\}`$ for $`y \in Y \setminus \{y_n\}`$, the $k year $`y`$ passes to the next $`\leftarrow`$.
Write $`r_{y_0} = r_{y_n} = 0`$ for the year before the plan and the last year.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_i \, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\text{spend}_y + r_y &\le B + r_{y-1} && \forall y \in Y && \text{(budget}_y) \quad \leftarrow \text{changed} \\
\sum_{i \in P :\, y \in T_i} x_{i,y} &\le K && \forall y \in Y && \text{(starts}_y) \\
100\, \text{spend}_{r,y} &\ge s_r \, \text{spend}_y && \forall r \in S \text{ with } s_r > 0,\ y \in Y && \text{(share}_{r,y})
\end{aligned}
```

The row is an inequality, not a balance with $`=`$: money neither spent nor passed on lapses, as it
did before. With $`C = 0`$, $`\bar r = 0`$, every $`r_y`$ is 0 and the row is the old one, which is
why the two old scenarios still hold. The variables are named `carry_2027` to `carry_2030` in a
five-year plan, and the rows keep their names, `budget_2027` and on.

## Tests First

Four new tests, one per new scenario; the two budget tests stay as they were, untouched. On the code
of `steps/03`, where `Request.carry` is a stub field the model ignores:

```text
step 04 tests on the code of step 03 (before): 26 passed, 4 failed
  FAILED test_capital_plan.py::test_unspent_money_carries_into_the_next_year (AssertionError)
         assert False
  FAILED test_capital_plan.py::test_carry_over_above_its_cap_is_refused (AssertionError)
         assert False
  FAILED test_capital_plan.py::test_money_cannot_be_borrowed_from_a_later_year (AssertionError)
         assert False
  FAILED test_capital_plan.py::test_a_carry_over_outside_0_to_100_percent_is_refused (AssertionError)
         assert None is not None
```

Each `assert False` is the allowed half of a pair: the old code refuses every year that spends more
than $1,000k. The borrowing test is the one a wrong lower bound would pass halfway:

<!-- snapshot: steps/04/tests/test_capital_plan.py -->
```python
def test_money_cannot_be_borrowed_from_a_later_year():
    projects = [project("A", 900), project("B", 1100), project("C", 1100), project("D", 900)]
    request = Request(budget=1000, years=2, carry=20)
    assert allows(projects, request, {("A", 2027), ("B", 2028)})        # 100 carried forward
    assert not allows(projects, request, {("C", 2027), ("D", 2028)})    # 2027 would borrow 100 from 2028
```

A carry variable with a lower bound of $`-\bar r`$ passes the first assertion and fails the second:
2027 could spend $1,100k by passing minus $100k into 2028.

## The Change, File by File

**`model.py`: the carry variables and the budget row as a balance.** `Built` gains `carry`, so a
caller can read the variables. The bounds are the rules: 0 below, the cap above.

```diff
--- 03/capplan/model.py
+++ 04/capplan/model.py
@@
         else:
             model.add(starts <= 1).with_name(f"once_{p.pid}")
-    for y in request.plan_years():
-        model.add(spend(projects, x, y) <= request.budget).with_name(f"budget_{y}")
+    years = request.plan_years()
+    cap = request.budget * request.carry // 100
+    carry = {y: model.new_int_var(0, cap, f"carry_{y}") for y in years[:-1]}   # 0: nothing is borrowed
+    for y in years:
+        # The year's spend, plus what it passes on, within its budget plus what it was passed.
+        model.add(spend(projects, x, y) + carry.get(y, 0) <= request.budget + carry.get(y - 1, 0)
+                  ).with_name(f"budget_{y}")
         if request.max_starts is not None:
             starts = sum(var for (_, year), var in x.items() if year == y)
```

`carry.get(y, 0)` is 0 for the last year and `carry.get(y - 1, 0)` for the first, the $`r_{y_n}`$ and
$`r_{y_0}`$ of the model.

**`request.py`: the field becomes real and is checked.** A percent outside 0 to 100 is refused
before solving, as the ADDED requirement says.

**`report.py`: `carry_by_year`, counted from the starts.** The carry variables are free wherever
money is left over: the solver may set $`r_y`$ to anything that fits, so their values say what is
allowed, not what happened. The report computes what each year passes on from the plan's spend
alone, every unspent $k up to the cap, as the design's Risks section says:

```diff
--- 03/capplan/report.py
+++ 04/capplan/report.py
@@
     """Each must-do override with its recorded reason, by project id."""
     return [f"{pid}: {reason.strip()}" for pid, reason in sorted(request.must_do.items())]
+
+
+def carry_by_year(projects: list[Project], starts: dict[str, int], request: Request) -> dict[int, int]:
+    """What each year passes to the next: its unspent money, up to the cap. The last year passes nothing."""
+    cap = request.budget * request.carry // 100
+    spend = spend_by_year(projects, starts)
+    carried, inflow = {}, 0
+    for year in request.plan_years()[:-1]:
+        inflow = min(cap, request.budget + inflow - spend.get(year, 0))
+        carried[year] = inflow
+    return carried
```

After the change all 30 tests pass:

```text
step 04 tests on the code of step 04 (after): 30 passed, 0 failed
tests step 04 adds or changes: 4; removes: 0
```

## What Carry-Over Buys: Nothing While the Start Cap Binds

`carry_over.py` plans the 40 invented projects, with the Plains share and P039 must-do, under the old
code and the new, with and without a start cap (the request can still set `max_starts=None` for no
cap):

```text
                                        value  spend by year, 2027 to 2031    carried out of each year
steps/03, start cap 3                $ 12,839k      0 1,970 2,320 1,870 2,130
steps/04, start cap 3, carry 0%      $ 12,839k      0 1,970 2,320 1,870 2,130        0     0     0     0     0
steps/04, start cap 3, carry 20%     $ 12,839k      0 1,970 2,260 1,890 2,170      600   600   600   600     0
steps/04, start cap none, carry 0%   $ 18,923k      0 3,000 2,960 2,990 2,980        0     0     0     0     0
steps/04, start cap none, carry 20%  $ 19,897k      0 3,520 2,430 3,320 3,280      600    80   600   280     0
```

With a carry-over of 0, `steps/04` gives the plan of `steps/03`, as the two old scenarios promise.
With 20% it gives the same value, $12,839k: the plan starts three projects a year, the cap, and never
spends more than $2,320k of a $3,000k budget, so money was never what held it back. Without the cap
the budget binds, and carry-over is worth $974k: 2027 spends nothing (the Plains share again), passes
$600k on, and 2028 spends $3,520k. The finding for the planners is that the yearly start cap, not
the budget, is what limits this portfolio. It is the next request.

## Validate and Archive

```text
== validate --strict, the change proposed
valid   spec capital-plan
valid   spec spec-checks
valid   change add-budget-carry-over
strict: 0 item(s) failed
```

On archive the rename is applied first, so the MODIFIED block finds the requirement under its new
name and replaces it; the ADDED requirement is appended:

```text
== archive
specs/capital-plan/spec.md: updated
moved to changes/archive/2026-11-05-add-budget-carry-over
specs/capital-plan/spec.md after archive: the same as steps/04
specs/spec-checks/spec.md after archive: the same as steps/04
```

The living spec's first requirement is now **Yearly budget with carry-over**, in place, with five
scenarios. The real `openspec archive add-budget-carry-over --yes`, run by `openspec_cli.py` on
another copy of the proposed change, counts one requirement of each kind and writes the same living
specs; its archive folder is dated with the day it runs (`<today>`), where `specs_check.py` takes
`--date`:

```text
$ openspec archive add-budget-carry-over --yes
Task status: ✓ Complete
Specs to update:
  capital-plan: update
Applying changes to openspec/specs/capital-plan/spec.md:
  + 1 added
  ~ 1 modified
  → 1 renamed
Totals: + 1, ~ 1, - 0, → 1
Specs updated successfully.
Change 'add-budget-carry-over' archived as '<today>-add-budget-carry-over'.
(exit 0)
specs/capital-plan/spec.md after openspec archive: the same as steps/04
specs/spec-checks/spec.md after openspec archive: the same as steps/04
archive folder: <today>-add-budget-carry-over
every file under openspec/, the archive's date set to steps/04's: the same as steps/04
```

## What the Step Did to the Code

```text
04              151            309     30            17         31  model.build (10)
```

Fifteen planner lines: five for the variables and the row, eight for the report, two for the check.
`build`'s branching did not change, because the carry row replaced the budget row instead of adding a
family next to it. The spec grew by one requirement, the check, since the budget rule was modified
in place, and by four scenarios.

**Practice.** This lesson's project practice starts from the code of `steps/03`, with the specs and
tests of `steps/04`. It is graded by those tests and by a check that `main.py` prints
`steps/04/expected/report.txt`.

<!-- practice 1 -->

## Summary

- **A rule that changes is MODIFIED, not ADDED.** Adding it would leave two requirements that
  contradict each other.
- **A MODIFIED block replaces the whole requirement**, so it repeats every scenario it keeps;
  dropping one is an error in validate and archive.
- **RENAMED is applied before MODIFIED**, so the MODIFIED block uses the new name.
- **Carry-over is a bounded integer variable per year:** $`0 \le r_y \le \bar r`$. The lower bound
  forbids borrowing, the upper bound is the cap, and the budget row becomes
  $`\text{spend}_y + r_y \le B + r_{y-1}`$.
- **Measure before you celebrate:** with the start cap binding, carry-over changed nothing.

## Reference

| Delta section | Holds | Archive does |
| --- | --- | --- |
| `## RENAMED Requirements` | `` - FROM: `### Requirement: old` `` then `` - TO: `### Requirement: new` `` | renames the requirement in place, first |
| `## MODIFIED Requirements` | the whole new requirement, every kept scenario included | replaces the requirement |
| `## ADDED Requirements` | new requirements | appends them, last |

| Rule | Row or bound | Code name |
| --- | --- | --- |
| no borrowing; carry cap | $`0 \le r_y \le \lfloor C B / 100 \rfloor`$ | `carry_<year>` |
| budget with carry-over | $`\text{spend}_y + r_y \le B + r_{y-1}`$ | `budget_<year>` |

**Further reading:** [CP-SAT Solver (OR-Tools docs)](https://developers.google.com/optimization/cp/cp_solver) (integer variables with bounds, as the carry variables are); [Writing good specs (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/writing-specs.md) (pick the right kind of delta: MODIFIED for behaviour that exists and is changing, with the full new version); [Concepts (OpenSpec docs, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/docs/concepts.md) (MODIFIED replaces the existing requirement on archive); [`specs-apply.ts` (OpenSpec source, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/src/core/specs-apply.ts) (archive applies RENAMED, REMOVED, MODIFIED, then ADDED, and refuses a MODIFIED block that drops a scenario); [`validator.ts` (OpenSpec source, `v2.0.0`)](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/src/core/validation/validator.ts) (the same scenario check at validate time, and MODIFIED under a renamed requirement's old name). Lessons 2.1.3 (multi-period carry-over in an LP) and 6.4.4 (carry-over budgets and multi-year caps) are the course's background for this step.

## Challenges

1. Finance adds: carried money expires after one year; it cannot be passed on twice. Which rows or
   variables change, and is the requirement MODIFIED again or is a new one ADDED?
2. Write the MODIFIED block you would get if the change also renamed "Spending over the budget is
   refused". What does OpenSpec's scenario check say about it?
3. In the table above, with no start cap and 20% carry-over, 2028 passes on only $80k although the
   cap is $600k. Explain it from the budget row of 2028.

## Design Note: The Old Scenarios Are Kept by Their Words, and Their Tests by Their Code

The two old budget scenarios gained "and no carry-over" in their GIVEN steps, and their tests did
not change at all: the default request has no carry-over. That is deliberate. A MODIFIED requirement
that keeps its old scenarios true, under the conditions they state, keeps every old test as a
regression test of the new rule. Had the change made the old scenarios false, their tests would have
had to change too, and a reviewer would have had to check that the new tests still test something.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**carry_over.py.** Plans the 40 invented projects before and after carry-over, with and without the
start cap, plants two MODIFIED mistakes in the delta, validates and archives the change, and runs the
step's tests before and after (*every section*). *Try:* Set the carry-over to 50% with no start cap.
Predict whether the value rises above $19,897k, then run it.

**openspec_cli.py.** Runs the real OpenSpec CLI on a temporary copy of every snapshot and every
proposed change (lesson 14.4.1 describes it); this lesson quotes its archive of
`add-budget-carry-over` (*Validate and Archive*). *Try:* In the copy, put the MODIFIED block under
the old name, Yearly budget. Predict whether `openspec validate --all --strict` still passes, then run
it.

- Program: [carry_over.py](src/carry_over.py)
- Program: [openspec_cli.py](src/openspec_cli.py)
- Program: [growth.py](src/growth.py)
- Library: [changes.py](src/changes.py)
- Library: [steps.py](src/steps.py)
