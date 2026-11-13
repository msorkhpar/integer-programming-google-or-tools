# 14.2.8 Trust at Scale: Determinism Harness, Golden Tests, Warm Starts

The planner is now used for the real portfolio, GridCap medium in this course: 400 projects over
ten years (fictional, like all GridCap data). Audit and the planning lead sent the last requests:

> Audit: if we run the same export twice we must get the same plan, and every run must say what it
> was planned from and with what. Prove it.
>
> Planning lead: the rule tests are good, but last month a change to the window code moved projects
> and no test noticed. And each run takes half a minute now; next cycle starts from this cycle's
> plan, so can the solver start from it too?

## A Plan Nobody Can Reproduce Cannot Be Audited

`steps/07` stores the snapshot hash with each run (the lesson *Scenarios, overrides and snapshots*), but it does not record the solver,
its version or its settings, and nothing checks that two runs of one snapshot agree. Its tests are
all about rules on small hand-built exports: a change that keeps every rule but moves a start year
on real data passes them all. And `solve` always starts from nothing.

Three tools from sections 10 to 12 answer the three requests:

| Request | Tool | Lesson |
| --- | --- | --- |
| same export, same plan, and proof of it | a run manifest and a determinism harness that compares plan digests | 10.2.4, 10.2.5 |
| catch a change that moves the plan | a golden plan for a fixed export, checked by a test | section 12, *Golden datasets and regression tests* |
| start from last cycle's plan | a solution hint mapped onto this cycle's variables | 11.2.1 |

The alternatives were weighed with each. For the harness, comparing objective values instead of
plans: two different plans can have the same NPV, so equal NPVs prove nothing (lesson 10.2.3).
For the golden check, storing the whole `Request` and model: it would fail on every harmless
refactor; the plan is what the planners use. For the warm start, a start repaired to fit this
cycle's rows (lesson 11.2.1) or none at all; the planner hands the old plan over as it is and
measures what that does.

## The Model

The planning model is the model of the lesson *Scenarios, overrides and snapshots*, unchanged; this step changes how it is run and
checked. Its sets, parameters, variables, objective and rows are those of the lesson *Scenarios, overrides and snapshots*. One input
is new to the solve, not to the model:

**The hint.** For last cycle's plan, which gives each funded project $`i`$ its start year $`s^{\text{prev}}_i`$ (absent
if $`i`$ was not funded), the hint gives every variable of this cycle's model a value:

```math
h_{i,t} = \begin{cases} 1 & \text{if } s^{\text{prev}}_i = t \\ 0 & \text{otherwise} \end{cases}
\qquad \forall i \in P,\ t \in T_i
```

A project whose old start is no longer in its window, or that left the export, gets no 1. The hint
is a suggestion: HiGHS may use it, repair it, or ignore it (the `SolutionHint` docstring in the
OR-Tools source says how a hint is used depends on the solver).

## The Change, File by File

**`cipt/trust.py`.** Before: the stub of the lesson *Scenarios, overrides and snapshots*. After, from `steps/08/cipt/trust.py`, the
identity of a plan and of a run:

<!-- snapshot: steps/08/cipt/trust.py -->
```python
def plan_digest(plan: Plan) -> str:
    body = canonical({"status": plan.status, "starts": plan.starts})
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def manifest(raw: dict, scenario: Scenario, plan: Plan) -> dict:
    return {
        "input": content_hash(raw),
        "scenario": scenario.to_dict(),
        "solver": {"name": "HIGHS", "ortools": ortools.__version__,
                   "threads": PARAMS.highs.int_options["threads"]},
        "plan": plan_digest(plan),
        "npv": round(plan.npv, 2),
    }
```

The digest covers the status and the starts, the decisions, and not the NPV: a float's last digit
can differ between machines while the plan is the same. The manifest reads the thread count from
the same `PARAMS` the solve uses, so it cannot disagree with the run.

A golden file is written once by `write_golden` and then checked in. From
`steps/08/cipt/trust.py`:

<!-- snapshot: steps/08/cipt/trust.py -->
```python
def write_golden(raw: dict, path: str | Path) -> None:
    plan = solve(load_request(raw))
    Path(path).write_text(json.dumps({"input": content_hash(raw), "status": plan.status, "npv": plan.npv,
                                      "starts": plan.starts}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
```

The file is one JSON object with four keys, in sorted order and indented by one space: `input`, the
hash of the export the plan was made from; `npv`, the plan's NPV; `starts`, each funded project's
start year by project id; and `status`. It ends with a newline, so a reviewer's diff shows only
lines that changed.

The golden check, `check_golden(raw, path)`, compares today's plan of the same export with that
file, start by start, and the page leaves its code to the practice. It returns a list of
differences, every one of them, not just "different", so a failing test names the projects that
moved. In this order:

- It reads the golden file first. If the export's content hash is not the file's `input`, it
  refuses to compare at all and returns the single line
  `input changed: golden <12 hex digits>, now <12 hex digits>`, the first 12 digits of each hash: a
  golden plan belongs to one input.
- Otherwise it plans the export from scratch. A status that differs gives the line
  `status <golden status> -> <status now>`.
- Then one line `<id>: start <golden start> -> <start now>` per project whose start differs, over
  the projects either plan funds, in id order, with `None` for a project one of the two plans does
  not fund.
- Last, `npv <golden> -> <now>` when the NPVs differ by more than 0.5, both in whole $k with
  thousands commas.

An empty list means the plan is the golden one.

**`cipt/solve.py`.** `solve` takes an optional `previous` plan, and `run_highs` passes a hint.
`hint_values(built, previous)` maps last cycle's plan onto this model's variables, and the page
leaves its code to the practice. It returns the hint $`h_{i,t}`$ of the model block above as a dict
with one entry per key of `built.x`, `(project_id, t)`: 1.0 where `previous.starts` gives that
project the start year `t`, else 0.0. Build it over this model's variables, not over the old plan,
so a start the window no longer allows, or a project that left the export, is dropped, and a stale
start can never produce a key that is not in `built.x`. Before (step 07) this function was a stub
returning an empty dict.

`solve` turns those values into a dictionary keyed by the variables themselves, and `run_highs`
hands it to MathOpt as a `SolutionHint`, the only entry of the `solution_hints` list of a
`ModelSolveParameters`. With no hint,
`model_params` stays `None` and the solve is the cold one of earlier steps. From
`steps/08/cipt/solve.py`:

<!-- snapshot: steps/08/cipt/solve.py -->
```python
def run_highs(model: mathopt.Model, hint: dict | None = None) -> mathopt.SolveResult:
    """Solve with stdout pointed at /dev/null, so HiGHS's stray C output stays out of reports.

    `hint` maps variables to values: a starting plan HiGHS may use (lesson 11.2.1).
    """
    model_params = mathopt.ModelSolveParameters(solution_hints=[mathopt.SolutionHint(variable_values=hint)]) \
        if hint else None
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=PARAMS, model_params=model_params)
```

<!-- snapshot: steps/08/cipt/solve.py -->
```python
def solve(request: Request, previous: Plan | None = None) -> Plan:
    """Plan a request; `previous`, last cycle's plan, is handed to HiGHS as a start when given."""
    built = build(request)
    hint = None if previous is None else {built.x[key]: v for key, v in hint_values(built, previous).items()}
    return read_plan(built, run_highs(built.model, hint))
```

**`tests/golden/demo_plan.json`.** The reviewed plan of the demo export, written once by
`write_golden` and checked in. A change that moves it fails `test_demo_plan_matches_its_golden`
until someone reviews the new plan and writes it as the new golden.

## A Run Is Repeatable When Its Plan Digest Repeats

`trust_medium.py` plans GridCap medium three times, once in its own process and twice in fresh
ones, so no state a process keeps can make the runs agree by accident:

```text
medium: 887 binary variables, base plan funds 222 projects, NPV $226,814k
harness: 3 runs, digests 3db2edf1335c, 3db2edf1335c, 3db2edf1335c, identical: True
manifest: {"input": "e1b838ee1664...", "npv": 226814.0, "plan": "3db2edf1335c...", "scenario": {"budget": {}, "fix_start": {}, "force_in": [], "force_out": [], "name": "base", "note": ""}, "solver": {"name": "HIGHS", "ortools": "9.15.6755", "threads": 1}}
```

The program shortens the two hashes to twelve digits for the page; the manifest itself holds them
whole. `scenario` is the whole scenario as `to_dict` writes it, here the base scenario with no
change, so the manifest says what was changed for a run, not only its name.

Three identical digests show that this export, with this OR-Tools version and one HiGHS thread,
gives the same plan. They do not show that the plan is the only best one, or that another solver
version gives the same plan; that is why the version is in the manifest. One thread is what the
planner has used since the lesson *The first request: fund projects within one budget*, and lesson 10.2.2 showed why threads change runs.

## A Golden Plan Catches a Regression the Rule Tests Miss

The program then checks the demo export against its golden plan, first with the code as shipped,
then with a planted regression: the window cut of the lesson *Many years: start years, windows and cash-flow spreading* ends one year early
(`years[-1] - duration` without the `+ 1`):

```text
golden check, code as shipped: no difference
golden check, window cut one year short: ['P001: start 2029 -> None', 'npv 2,473 -> 1,396']
```

P001 is a one-year project that started in the plan's last year, a start the bug no longer allows.
No rule is broken by the faulty code: its plans keep every row it builds. Only a comparison with a
known plan sees that P001 vanished and $1,077k of NPV with it, which is exactly the kind of change
the planning lead said no test noticed.

## A Warm Start Changed the Search, Not the Time, on These Runs

Next cycle the budget of 2031 changes. The program plans two changes, a 10% cut and a 10% rise,
each cold and warm-started from the base plan:

```text
2031 cut 10%: budget $33,822k; the base plan spends $37,560k in 2031
  cold: OPTIMAL, NPV $225,079.0k, bound $225,101.0k, 8,850 nodes, 370,025 simplex iterations
  warm: OPTIMAL, NPV $225,079.0k, bound $225,101.0k, 8,850 nodes, 370,025 simplex iterations
2031 raised 10%: budget $41,338k; the base plan spends $37,560k in 2031
  cold: OPTIMAL, NPV $228,348.0k, bound $228,370.0k, 2,591 nodes, 213,561 simplex iterations
  warm: OPTIMAL, NPV $228,349.0k, bound $228,371.0k, 2,755 nodes, 222,934 simplex iterations
```

After the cut, the base plan overspends 2031, so as a start it breaks a row of the new model. The
warm run did exactly the same work as the cold one, to the node: on this run the infeasible start
changed nothing. After the rise, the base plan fits, and the warm run took a different path, 164
more nodes, to a plan worth $1k more.

Each "OPTIMAL" sits $22k below its bound. That is HiGHS stopping at its default relative gap of
0.01% (lesson 3.4.3): both plans of the rise are optimal within it, and they differ. So a warm
start is not free for determinism either: a run with a hint and one without can return different
plans, and the manifest would have to record the hint. The planner keeps `previous` optional and
off by default, and the lead got a measured answer instead of a promise: on these two changes the
old plan did not make the solve faster. Lesson 11.2.1 measured starts over many seeds and cycles;
two runs are a measurement of two runs.

## The Trust Tests Pin What Audit Asked For

From `steps/08/tests/test_trust.py`:

<!-- snapshot: steps/08/tests/test_trust.py -->
```python
def test_hint_keeps_only_starts_this_model_has():
    built = build(load_request(base()))
    values = hint_values(built, Plan("optimal", {"A": 2026, "B": 2028, "Z": 2027}))
    assert {k for k, v in values.items() if v == 1} == {("B", 2028)}
```

A's 2026 start is outside its window and Z left the export; only B's start survives.

```text
14.2.8: 8 tests added; on step 07, 8 fail on an assertion; on step 08, 58 of 58 pass
  test_harness_finds_identical_runs
    before: assert (0, False) == (3, True)
    after:  passed
  test_plan_digest_changes_with_the_plan
    before: assert '' != ''
    after:  passed
  test_manifest_records_the_input_and_the_settings
    before: assert (None, None, None) == ('c4eb3d1286b...ae647', '', 1)
    after:  passed
  test_golden_check_reports_each_changed_start
    before: assert ['not checked'] == ['B: start No...2028 -> None']
    after:  passed
  test_golden_check_refuses_a_changed_input
    before: assert ['not checked'] == ['input chang...c4eb3d1286bd']
    after:  passed
  test_demo_plan_matches_its_golden
    before: assert ['not checked'] == []
    after:  passed
  test_hint_keeps_only_starts_this_model_has
    before: assert set() == {('B', 2028)}
    after:  passed
  test_warm_start_gives_the_cold_plan
    before: assert {} == {'A': 2027, 'B': 2028}
    after:  passed
```

These tests run on hand-built exports in a few seconds. The medium runs above take minutes and
stay in the lesson program: a test suite that takes minutes is a suite people stop running.

## Trust Added Checks Around the Planner, Not Inside It

```text
14.2.8: steps/07 -> steps/08
  package lines 616 -> 657, functions 63 -> 63, tests 50 -> 58
  most branches: diagnose.describe (11) -> diagnose.describe (11)
  solve.py       41 ->   51
  trust.py       29 ->   60
```

The last step added 41 lines, and none in the model or the rules. Over eight lessons the planner
grew from 125 lines to 657 and from 4 tests to 58, and `model.py` stopped changing after the lesson
*Two goals: risk against NPV*. Every later request was met by a new file that uses `Built`'s handles: the rows by name,
`started`, `npv` and `risk`. That is the main design lesson of the project: the early choices to
name every row and to keep both measures on `Built` were what made diagnostics, scenarios and
trust additions instead of rewrites.

**Practice.** This lesson's project practice starts from `steps/07`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds. This step's `main.py` also
plans the demo export three times and says whether the plans agree, after the scenario section: an
empty line, then `<runs> runs, same plan: <True or False>, plan digest <12 hex digits>`, where the
digits are the start of the first run's plan digest.

<!-- practice 1 -->

## Summary

- **A plan nobody can reproduce cannot be audited.** The manifest records the input's hash, the
  scenario, the solver, its version and threads, and the plan's digest.
- **A run is repeatable when its plan digest repeats**: three runs of GridCap medium gave one
  digest.
- **A golden plan catches a regression the rule tests miss**: a window cut one year short
  dropped P001 without breaking any row.
- **A warm start changed the search, not the time, on these runs**, and both plans of a run were
  optimal only within HiGHS's 0.01% gap.

## Reference

| Name | Meaning |
| --- | --- |
| `plan_digest(plan)` | sha256 of the canonical status and starts |
| `manifest(raw, scenario, plan)` | input hash, scenario, solver, version, threads, plan digest, NPV |
| `harness(raw, runs)` | the digests of `runs` fresh solves; `same` if all equal |
| `check_golden(raw, path)` | each start that differs from the golden plan; empty if none |
| `hint_values(built, previous)` | $`h_{i,t}`$ for every variable of this model |
| `solve(request, previous)` | solve with last cycle's plan as a hint |

**Further reading:** [MathOpt `model_parameters.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py) (`SolutionHint` and `ModelSolveParameters.solution_hints`, with the docstring on partial and infeasible hints and on reading the logs to see whether a hint was used); [MathOpt `result.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (`objective_bounds.dual_bound` and `solve_stats`, the bound, nodes and iterations printed above); [MathOpt `parameters.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py) (solver-specific HiGHS options, where the thread count is set).

## Challenges

1. Set `relative_gap_tolerance` to 0 in `PARAMS` and predict whether the two plans of the rise
   become one. How long does each solve take then?
2. Repair the base plan before handing it over after the cut: drop funded projects from the hint
   until 2031 fits. Does the warm run change?
3. Write a test that fails if `plan_digest` included the NPV. What would make it fail on another
   machine?

## Design Note: What Each Check Answers

The harness answers "does this code repeat itself?", the golden check "did this code change its
answer?", the rule tests "does each rule hold?", and the manifest "what was this run?". None of them
answers another's question: a repeatable plan can be wrong, a golden plan can encode an old bug,
and a rule test cannot see a project that silently vanished. The planner keeps all four, and each
failure message names what differs.

## The Full Programs

**trust_medium.py.** On GridCap medium with `steps/08`: three runs compared by digest, the manifest,
the golden check with and without a planted regression, and cold and warm solves after two budget
changes. It takes a few minutes. *Try:* plant a different regression, such as dropping the
`bundles` rule, and predict whether the demo's golden check notices.

- Program: [trust_medium.py](src/trust_medium.py)

**ledger.py, code_size.py.** The test ledger and the size table for step 08.

- Program: [ledger.py](src/ledger.py)
- Program: [code_size.py](src/code_size.py)
