# 12.3.3 Golden Datasets and Regression Tests

GridCap's planning service will change every month: a faster model builder, a new rule, a solver
upgrade. Each change must leave last month's answers alone unless it was meant to change them. The
unit tests of lesson 12.3.1 and the properties of lesson 12.3.2 say whether the rules hold; they do
not say whether the plan for GridCap small is still the plan the planners reviewed. A **golden
dataset** does: a fixed set of scenarios with their reviewed results stored next to the code, and a
**regression test** that solves them again and compares, field by field, within stated tolerances,
with a diff that says what moved. GridCap is a fictional utility's portfolio.

## The Model Under Test

The model is lesson 12.3.1's, unchanged.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, each with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k); $`B_y`$, the budget of
year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$.

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
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## A Golden Record Stores the Input's Identity and the Reviewed Result

The golden scenarios are chosen like test cases, each for a reason: GridCap tiny and small as
generated, small with its 2028 budget cut by 20% so that a different year binds, and a two-project
instance with a tie (two equal projects and room for one), which exists to catch a change in how
ties are broken:

```python
def scenarios() -> dict[str, Portfolio]:
    """The golden scenarios: small enough to solve in a second, each with something that binds."""
    small = generate("small")
    cut = {y: (b * 8 // 10 if y == 2028 else b) for y, b in small.budget.items()}
    tie = portfolio(project("A", (50,), (2027, 2027), npv=30), project("B", (50,), (2027, 2027), npv=30),
                    budget={2027: 60}, name="tie")
    return {"tiny": generate("tiny"), "small": small,
            "small, 2028 budget cut 20%": replace(small, budget=cut),
            "two equal projects, room for one": tie}
```

A record holds what a reviewer approved, and one more thing, the input's identity:

```python
def result(portfolio: Portfolio, rules: dict | None = None) -> dict:
    """What a golden record holds: the input's identity and the solve's status, value, plan and spend."""
    status, npv, plan = optimize(portfolio, rules)
    return {"input_sha256": input_hash(portfolio), "status": status,
            "objective": round(npv, 3), "plan": plan,
            "spend": {str(y): v for y, v in spend_by_year(portfolio, plan).items()}}
```

- `input_sha256` is the first 16 hex digits of the SHA-256 of the portfolio's canonical JSON, with
  its projects sorted by id, so the same data read in another row order has the same hash (lesson
  12.2.3 covers content hashes of snapshots). It lets the test tell "the model changed" from "the
  data changed".
- `status`, `objective`, `plan` and `spend` are the result. The objective is rounded to 3 decimals
  before it is stored, so the file does not record the solver's noise digits. `spend` is recomputed
  from the data and the plan, in whole $k, so it is exact.

The records live in `src/golden/plan_results.json`, written with sorted keys and one field per line,
so that a change shows as a readable diff in code review:

```text
the golden record of one scenario, as stored:
{
 "two equal projects, room for one": {
  "input_sha256": "473f69beb9c87207",
  "objective": 30.0,
  "plan": {
   "A": 2027
  },
  "spend": {
   "2027": 50,
   "2028": 0,
   "2029": 0
  },
  "status": "OPTIMAL"
 }
}
```

## Compare Field by Field, Within Tolerances Stated in Business Units

Which fields must match exactly, and which within a tolerance, is a decision to write down, field
by field:

- **Status, plan and spend: exactly.** They are discrete: a project is in or out, in 2028 or 2029,
  and the spend is a sum of integers.
- **Objective: within a tolerance in the objective's own units.** The solver computes it in floating
  point, and HiGHS returns values with noise in the last digits. The
  tolerance here is 0.01 $k, $10, stated next to the reason for it:

```python
TOLERANCE = {"objective": 0.01}     # $10: far above solver noise (1e-5), far below one project
```

An absolute tolerance in dollars says what a planner would call "the same". A relative tolerance
would scale with the portfolio: 1e-6 of a $24,260k NPV is $24, and of a $2B portfolio (lesson 3.4.3)
it is $2k. Neither is wrong, but the unit must be stated. Exact float equality is wrong, and
`regressions.py` shows why on a real solve:

```text
solver noise: HiGHS returned 26646.00000000258 for a plan whose NPV is 26,646; equal as floats: False; within 0.01: True
```

`compare` checks the fields in order of how much they explain, and returns one line per difference:

```python
def compare(expected: dict, actual: dict, tolerance: dict = TOLERANCE) -> list[str]:
    """Every difference between a golden record and a new one, most fundamental first."""
    if expected["input_sha256"] != actual["input_sha256"]:
        return [f"input changed: sha256 {expected['input_sha256']} -> {actual['input_sha256']} "
                "(the data moved, not the model: regenerate this record on purpose)"]
    if expected["status"] != actual["status"]:
        return [f"status: {expected['status']} -> {actual['status']}"]
    lines = []
    delta = actual["objective"] - expected["objective"]
    if abs(delta) > tolerance["objective"]:
        lines.append(f"objective: {expected['objective']:,.3f} -> {actual['objective']:,.3f} "
                     f"({delta:+,.3f}, tolerance {tolerance['objective']})")
    was, now = expected["plan"], actual["plan"]
    for pid in sorted(set(was) | set(now)):
        if pid not in now:
            lines.append(f"plan: {pid} dropped (was {was[pid]})")
        elif pid not in was:
            lines.append(f"plan: {pid} added (starts {now[pid]})")
        elif was[pid] != now[pid]:
            lines.append(f"plan: {pid} moved {was[pid]} -> {now[pid]}")
    for year in expected["spend"]:
        if expected["spend"][year] != actual["spend"][year]:
            lines.append(f"spend {year}: {expected['spend'][year]:,} -> {actual['spend'][year]:,}")
    if lines and abs(delta) <= tolerance["objective"]:
        lines.append("same value, another plan: a tie picked differently")
    return lines
```

A changed input stops the comparison: when the data moved, every other difference is expected and
says nothing about the model. A changed status stops it too: an infeasible run has no plan to diff.
After that, the plan is compared over the union of both plans' projects, so an added project is
reported as well as a dropped one, and a project in both plans is checked for its year.

A list of lines, rather than `assert expected == actual`, is the point of the function. A plain
equality on two dictionaries of 27 projects fails with a wall of nested data; these lines say what
moved, in the planners' words. A test then asserts that the list is empty, and pytest prints the
list when it is not. On the current model, `golden.py` passes every scenario:

```text
PASS tiny: OPTIMAL, NPV 2,473.0, 5 projects
PASS small: OPTIMAL, NPV 24,260.0, 27 projects
PASS small, 2028 budget cut 20%: OPTIMAL, NPV 23,666.0, 28 projects
PASS two equal projects, room for one: OPTIMAL, NPV 30.0, 1 project
```

<!-- practice 1 -->

## A Golden Test Catches Regressions, Not Rule Errors

`regressions.py` makes four changes in memory and compares each with the golden file. The first two
are lesson 12.3.1's broken precedence rows:

```text
1. A model bug: precedence ignores the lag
  PASS tiny
  FAIL small
       objective: 24,260.000 -> 24,313.000 (+53.000, tolerance 0.01)
       plan: P001 dropped (was 2028)
       plan: P002 added (starts 2028)
       plan: P005 dropped (was 2029)
       ... 17 more
  PASS small, 2028 budget cut 20%
  PASS two equal projects, room for one
2. A model bug: precedence adds 1 to the lag
  PASS tiny
  PASS small
  PASS small, 2028 budget cut 20%
  PASS two equal projects, room for one
```

The first bug changes small's plan, and the diff says how much value it gained by breaking the rule,
$53k, and which projects moved. The second passes every scenario. A golden test asks one question,
"did the answer change?", and the too-strict row does not change any of these four answers. That is
the same blind spot as lesson 12.3.1's whole-model test, because a golden test *is* a whole-model
test, repeated on a few fixed points. It is excellent at catching an unintended change, and it says
nothing about whether the stored answer was right. The unit tests and properties answer that; the
golden test guards what they approved.

Note also which scenarios caught bug 1: only small. A golden set is worth what its scenarios lean on,
which is why each one should be chosen for something that binds.

## Tell a Data Change and a Tie From a Regression

The other two changes are not model bugs, and the comparison has to say so:

```text
3. The data moved: GridCap small's 2031 budget lowered by 500
  FAIL small
       input changed: sha256 29d5349c5b5ab600 -> b09ec6788cb9922c (the data moved, not the model: regenerate this record on purpose)
4. The same data, its rows read in another order
  FAIL two equal projects, room for one
       plan: A dropped (was 2027)
       plan: B added (starts 2027)
       same value, another plan: a tie picked differently
```

Change 3 lowers one budget, as a new data snapshot might. Without the input hash the test would
report a long plan diff and someone would hunt for a model bug that does not exist. With it, the
first and only line says the scenario's data are no longer the reviewed data. The fix is to decide
whether the scenario should follow the new data, then regenerate that record and review its diff.

Change 4 reads the same two projects in the opposite order. The input hash is unchanged (it sorts
the projects), the value is unchanged, and the plan funds B instead of A: the solver broke a **tie**,
two plans of equal value, the other way. Lesson 10.2.3 shows where ties come from and how a second
criterion picks one plan on purpose. Whether a tie flip is a failure depends on the contract: if
planners were promised a specific plan, it is; if they were promised the best value, it is not. The
golden test here fails on it, because a plan nobody reviewed should not ship silently, and the last
line tells the reviewer it is a tie rather than a worse plan.

<!-- practice 2 -->

## Update a Golden File on Purpose, and Review the Diff

A golden file goes stale whenever an answer is meant to change: a new rule, a corrected cost, a new
scenario. Updating it is part of the change, never a way to make a red test green. `golden.py` does
both jobs: run plainly, it compares; run with `--update`, it rewrites the file:

```python
def main() -> None:
    current = {name: result(p) for name, p in scenarios().items()}
    if "--update" in sys.argv:
        write(current)
        print(f"wrote {len(current)} records to {GOLDEN.name}; review the diff before committing")
        return
```

The rule that keeps the file honest: update it in its own commit, or in the same commit as the
change that explains it, and read the diff of the JSON in review as carefully as the code. Because
the file is written with sorted keys and one field per line, a moved project is one changed line
and a new objective is another. A reviewer who sees 20 plan lines change in a commit titled
"refactor the builder" has found a bug.

## Summary

- **A golden record stores the input's identity and the reviewed result.** Scenarios are chosen to
  make different rules bind; the input hash separates data changes from model changes.
- **Compare field by field, within tolerances stated in business units.** Status, plan and spend
  exactly; the objective within $10, never by float equality; one readable line per difference.
- **A golden test catches regressions, not rule errors.** It guards answers that the unit tests and
  properties approved; a too-strict rule that changes none of its answers passes it.
- **Tell a data change and a tie from a regression.** Check the input hash first; name a same-value
  plan change as a tie.
- **Update a golden file on purpose, and review the diff.** One field per line, sorted keys, and a
  commit that explains why the answers moved.

## Reference

| Field | Compared | Why |
| --- | --- | --- |
| `input_sha256` | exactly, first; stops the comparison | a data change explains every other difference |
| `status` | exactly; stops the comparison | an infeasible run has no plan |
| `objective` | within 0.01 $k | floating point; solver noise near 1e-5 |
| `plan` | exactly, over both plans' projects | discrete: dropped, added, moved |
| `spend` | exactly | integer $k recomputed from the data |

| Diff line | Means |
| --- | --- |
| `input changed` | the scenario's data are not the reviewed data |
| `objective` | the value moved by more than the tolerance |
| `plan: ... dropped / added / moved` | the plan changed; with no objective line, a tie |
| `same value, another plan` | a tie broken the other way (lesson 10.2.3) |

**Further reading:** [The basic example of MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt/basic_example) (reading the termination reason and objective value that each golden record stores); [pytest.approx (pytest API reference)](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx) (its default relative tolerance of 1e-6 and absolute 1e-12, and how passing `abs` alone switches the relative one off: the choice `TOLERANCE` makes explicit).

## Challenges

1. Add a golden scenario that would catch change 2, the too-strict lag. What must its best plan
   contain?
2. Give `compare` a per-year tolerance for spend and explain why this model does not need one.
3. Store the golden records in one file per scenario instead of one file. What does a reviewer gain,
   and what does an update lose?

## Design Note: Why the Golden File Stores Rounded Objectives

The stored objective is rounded to three decimals and compared within $10. Storing the raw float
would put the solver's noise digits into the file, so a solver upgrade that moved the noise would
show as a changed line in every record's diff, and reviewers would learn to skip those lines. The
rounding keeps the file stable; the tolerance, far larger than the rounding, keeps the test stable.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**golden.py.** The golden scenarios, the record, `compare`, and the check or `--update` run (*Compare
Field by Field*, *Update a Golden File on Purpose*). *Try:* Set the objective tolerance to 0. Predict
which scenarios still pass on the current model.

- Program: [golden.py](src/golden.py)

**regressions.py.** Four changes compared with the golden file, and the solver-noise line (*A Golden
Test Catches Regressions*, *Tell a Data Change and a Tie From a Regression*). *Try:* Lower the 2028
budget of `small` instead of 2031's. Predict whether the comparison reports anything beyond the input
change.

- Program: [regressions.py](src/regressions.py)
