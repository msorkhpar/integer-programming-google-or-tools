# 13.1.5 Trust: Determinism Harness, Hypothesis Properties, Golden Test, Warm Start

A regulator reviewing GridCap's rate case asks the question every optimization tool must answer
sooner or later: "If we run your tool on the same inputs next month, do we get the same plan, and
how do you know the plan obeys your own rules?" Four pieces of section 10 and section 12 answer it,
and this milestone fits them to CIPT Lite: a run manifest and a harness that reruns it in fresh
processes (lessons 10.2.4 and 10.2.5), properties checked on hundreds of generated portfolios
(lesson 12.3.2), golden records that catch a regression (lesson 12.3.3), and a warm start from last
cycle's plan that must not cost any of the above (lesson 11.2.1). Nothing here changes the model of
lesson 13.1.2; it changes what can be claimed about it. GridCap is a fictional utility's portfolio.

## A Run Is Its Manifest, and the Harness Compares Ten of Them Byte for Byte

A **run manifest** records what went into a run and what came out, in canonical bytes, and nothing
that names the clock, the machine or a person (lesson 10.2.4). CIPT Lite's has four sections: the
inputs (the snapshot digest of lesson 13.1.1, the scenario, the objective, and the digest of any
hint), the solver and its settings, the versions of Python and OR-Tools, and the result with its
plan and its work counts. `cipt_trust.py` prints one, for GridCap small at a zero gap:

```text
inputs.hint_digest             null
inputs.objective               "npv"
inputs.scenario                {"name":"base"}
inputs.snapshot                "29d5349c5b5ab600ecfb86b6d3c1fbe3cd0adaa21f7abfec385b4d3387a195e7"
result.bound                   17463.0
result.nodes                   1
result.objective               17463.0
```

The work counts (nodes, simplex iterations) are there on purpose. Two runs that return the same
plan by different searches are not the same run, and the counts are what shows it, where the
objective alone would hide it.

The **harness** runs one config in ten fresh processes, each with its own `PYTHONHASHSEED`, so a
set's iteration order, a per-process thread setting or a library's hidden state cannot hide behind
one process's luck (lesson 10.2.5). It compares the manifests' bytes:

```python
def harness(config: dict, runs: int = 10) -> tuple[dict, str]:
    """Raise NotDeterministic unless `runs` fresh processes give byte-identical manifests."""
    manifests = [child(config, seed) for seed in range(1, runs + 1)]
    for k, m in enumerate(manifests[1:], start=2):
        if canonical(m) != canonical(manifests[0]):
            raise NotDeterministic(f"run {k} of {runs} differs at: {', '.join(diff(manifests[0], m))}")
    return manifests[0], sha(manifests[0])
```

`trust_medium.py` puts the run setting of lesson 13.1.2 through it on GridCap medium, and then a
config built to fail, the zero-gap model stopped by a two-second clock limit:

```text
1. determinism
   PASS medium, gap 0.1%, 1 thread: 10 identical manifests, sha256 a4285d29b28c1712, OPTIMAL 219,054, 791 nodes
   FAIL medium, zero gap, 2 s clock limit: NotDeterministic
```

Ten processes, one manifest: the same 209 starts, the same bound and the same 791 nodes each time.
That is what one HiGHS thread and a stopping rule that counts the search (a gap) rather than the
clock buy (lesson 10.2.2). The clock-limited config fails, as it must: a clock stops the search
wherever the machine happens to be, and the harness's error names the fields that changed between
runs. A harness that never fails proves nothing, so this known-bad config stays in the module's
program beside the good one (lesson 12.3.4).

The PASS holds for this machine, this OR-Tools (9.15) and this Python; the manifest records all
three, so a later run on other versions is compared knowing they changed.

<!-- practice 1 -->

## Properties Must Hold on Every Drawn Portfolio

The harness shows the model repeats itself; it does not show the model is right. Lesson 12.3.2's
property tests do that on inputs nobody chose by hand: a Hypothesis strategy draws small portfolios,
each **feasible by construction** around a witness plan drawn first, with every rule CIPT Lite has
(must-dos, parents with lags, alternatives, yearly, regional and crew limits, floors). Each limit
is drawn either tight (a little above the witness's use) or loose, so that every rule gets cases
where it binds and cases where it leaves the plan free. Then one function checks every property
from the data:

```python
def holds(case: Case, builder=build) -> None:
    """Every property of one drawn case; an AssertionError names the one that failed."""
    pf = case.portfolio
    b = builder(pf)
    result = solve(b.model, params(gap=0.0))
```

The plan must break no rule (by `check`, which never sees the model), its reported value must be
the plan's value recomputed from the data, it must be no worse than the witness, and $10k more in
every year's budget must never lower the value. The settings are lesson 12.3.2's for repeatable
runs: 200 examples, `derandomize=True`, no example database, no deadline. `properties_200.py` runs
the correct model, and then two builders with a bug planted, each a slip a refactor can make:

```text
correct model: every property held on 200 drawn portfolios (1 to 8 projects)
lags read as 0: a property failed: plan {'P1': 2027, 'P3': 2027} breaks ['after_P3_2027']
crews charged to the start year: a property failed: plan {'P1': 2027} breaks ['crews_transmission_2028']
```

Both bugs are caught, and Hypothesis **shrinks** each failure to a small case that still fails
(lesson 12.3.2): a child started in its parent's year when the lag is one year, and a two-year
project whose second year's crews were never counted. Each counterexample names the broken row, so
it reads as a bug report.

The witness carries most of the weight here. Without it, many drawn portfolios would have no plan,
and a property test that skips them tests less than it seems; with it, every one of the 200 cases
tests the solver's plan against a plan known to be valid.

<!-- practice 2 -->

## A Golden Record Catches a Regression, Not a Rule Error

Properties check rules; they do not check that this month's answer is last month's. A **golden
record** stores a reviewed result: the snapshot it came from, the status, the objective and the
plan's digest (lesson 12.3.3). CIPT Lite keeps three, in `golden/cipt_golden.json`, chosen so that
different rules bind: GridCap small as exported, small with its 2028 budget cut to $6,000k, and
medium with the run setting. The comparison speaks in business terms and separates a changed input
and a tie from a regression:

```python
def golden_compare(expected: dict, manifest: dict) -> list[str]:
    """One line per difference between a reviewed record and a run, in business terms."""
    out = []
    if expected["snapshot"] != manifest["inputs"]["snapshot"]:
        return [f"input changed: snapshot {expected['snapshot'][:12]} -> {manifest['inputs']['snapshot'][:12]}"]
```

The objective is compared within $10 (0.01 in $k), far above HiGHS's noise in the last digits and
far below the smallest project. Fresh runs, then a run in which someone loosened the gap to 1%:

```text
2. golden records
   small-base      same as reviewed
   small-2028-cut  same as reviewed
   medium-base     same as reviewed
   medium, gap 1%  objective 219,054.00 -> 218,470.00; plan 396fad1978e3 -> 91b31caa632b
   the gap-1% plan breaks no rule; harness: 10 identical manifests, sha256 9fa4e29d4bcd753c
```

The loosened gap returned a plan $584k worse, and nothing else in the suite would have said so: the
plan breaks no rule, so a check of it finds nothing, and it repeats ten times out of ten, so the
harness passes. Only a
record of the reviewed answer catches it. The reverse holds too: a rule written too strictly from
the start would be in the golden record, approved, and the golden test would guard it. That is why
the three pieces are kept together, and why a golden file is rewritten only on purpose
(`python3 trust_medium.py --write-golden`) with its diff reviewed.

## A Warm Start Is Last Cycle's Plan, Repaired and Handed Over as a Hint

Next cycle finance cuts 2028 to $40,000k, and the planners want the new plan to stay close to the
old one where it can, and to arrive quickly. Lesson 11.2.1's recipe: map last cycle's plan onto this
cycle's variables, repair it until it breaks no rule, and hand the whole of it to the solver as a
**solution hint** in `ModelSolveParameters(solution_hints=...)` (lesson 4.3.3).

```python
def warm_start(b, last: dict[str, int]) -> tuple[mathopt.ModelSolveParameters, dict[str, int]]:
    """A complete hint (every start variable 0 or 1) from last cycle's plan, repaired first."""
    carried = {i: t for i, t in last.items() if (i, t) in b.x}
    start = repair(b.portfolio, b.scenario, carried)
    hint = mathopt.SolutionHint(variable_values={v: 1.0 if start.get(pid) == t else 0.0
                                                 for (pid, t), v in b.x.items()})
    return mathopt.ModelSolveParameters(solution_hints=[hint]), start
```

`repair` drops optional projects from the years whose limits the plan breaks, least NPV per $k
first, each with its children, and never a must-do. The hint sets every start variable, 0 or 1,
so the solver receives a complete plan to check rather than a partial one to finish (MathOpt's
documentation says solvers may accept partial and even infeasible hints, and repair them with a
sub-MIP of their own).

```text
3. warm start after a 2028 cut to $40,000k
   last cycle's plan: 209 projects, breaks ['budget_2028']
   repaired start: 202 projects, breaks nothing
   no hint  OPTIMAL, NPV 217,759, 337 nodes
   hinted   OPTIMAL, NPV 217,796, 29 nodes
   PASS hinted run: 10 identical manifests, sha256 5e10fe65af8e158d
```

Last cycle's plan broke only the cut year; dropping seven projects repaired it. With the hint, HiGHS
proved its plan within the gap in 29 nodes instead of 337, and the plan it stopped on is $37k
better, since each search stops at the first plan proved within 0.1%. One scenario is not a
measurement (lesson 11.2.1 measured over seeds and cycles); what this run does show is the last
line: the hint is an input, recorded in the manifest by its digest, and the hinted run is as
repeatable as the cold one.

<!-- practice 3 -->

## Summary

- **A run is its manifest, and the harness compares ten of them byte for byte.** Inputs, solver,
  versions and result with work counts, no clock; ten fresh processes gave one manifest for the run
  setting, and a clock-limited config failed as it must.
- **Properties must hold on every drawn portfolio.** Drawn feasible around a witness, limits tight
  or loose: every property held on 200 portfolios, and two planted bugs came back as one-line
  counterexamples.
- **A golden record catches a regression, not a rule error.** Three reviewed records; a gap loosened
  to 1% cost $584k, broke no rule and repeated, and only the golden test said so.
- **A warm start is last cycle's plan, repaired and handed over as a hint.** Complete, rule-abiding,
  recorded by digest; 29 nodes instead of 337 here, and still deterministic.

## Reference

| Piece | Function | Lesson |
| --- | --- | --- |
| manifest | `run(config)`: inputs, solver, versions, result | 10.2.4 |
| harness | `harness(config, runs)`, `NotDeterministic`, `diff` | 10.2.5, 12.3.4 |
| properties | `portfolios()` strategy, `holds(case, builder)`, settings `CI` | 12.3.2 |
| golden | `golden_compare(expected, manifest)`, `golden/cipt_golden.json` | 12.3.3 |
| warm start | `repair`, `warm_start(built, last)` | 4.3.3, 11.2.1 |

| Config key | Meaning |
| --- | --- |
| `size` | GridCap size |
| `gap` | HiGHS's relative gap |
| `scenario` | name and budget locks |
| `time_limit` | a clock limit, seconds (known-bad) |
| `hint_from` | last cycle's plan, {project: year} |

**Further reading:** [Hypothesis settings](https://hypothesis.readthedocs.io/en/latest/reference/api.html) (`max_examples`, `derandomize`, `database`, `deadline`); [OR-Tools `model_parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py) (`ModelSolveParameters` and `SolutionHint`, whose values may be partial); [HiGHS options](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`threads`, `random_seed`).

## Challenges

1. Add the table digests of lesson 13.1.3 to the manifest's inputs. Which runs' manifests change,
   and which golden records would have to be rewritten?
2. The clock-limited config failed in three runs. Could it have passed? What would a pass prove?
3. Draw every limit tight, never loose, and predict which of the two planted bugs the 200 cases are
   less likely to find. Then run it and see.

## Design Note: Four Tests, Four Questions

Each piece answers one question and is blind to the others': the harness asks "the same run?", the
properties "a valid plan?", the golden record "the reviewed answer?", and the warm start's own
harness run "still the same run once we add a hint?". A tool that has only one of them will one day
pass it with a wrong answer; this lesson's 1% gap passed two of the four. Keeping all four is
cheaper than finding out which one was missing.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**cipt_trust.py.** The trust library; run on its own it prints GridCap small's manifest, and run
with a config it prints one manifest's canonical bytes, which is how the harness calls it (*A Run Is
Its Manifest*). *Try:* Run it twice and compare the two outputs line by line.

- Program: [cipt_trust.py](src/cipt_trust.py)

**trust_medium.py.** Ten-run harness on GridCap medium, a known-bad config, golden records and a
regression, and the warm start after a 2028 cut (every section but *Properties*). *Try:* Give the
known-bad config a node limit instead of a clock limit. Predict PASS or FAIL.

- Program: [trust_medium.py](src/trust_medium.py)

**properties_200.py.** The properties on 200 drawn portfolios, for the correct model and two planted
bugs (*Properties Must Hold*). *Try:* Plant a third bug: drop the floor rows. Predict which property
names it.

- Program: [properties_200.py](src/properties_200.py)

The strategy and the properties are in `cipt_properties.py`.

- Library: [cipt_properties.py](src/cipt_properties.py)
