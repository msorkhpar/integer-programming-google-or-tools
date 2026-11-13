# 5.4.4 Writing a Solver Recommendation

The architecture review from lesson 5.4.1 is back on the calendar, and the reviewer's question has
not changed: "Why HiGHS? Shouldn't we just buy Gurobi?" This time the team has a survey of the field
(5.4.1), a benchmark harness whose numbers repeat (5.4.2), and the license and container facts with
their dates (5.4.3). What is missing is the document that turns those into a decision someone can
approve, challenge, or revisit in a year. This lesson writes it, as a program, `recommend.py`, so
that every number in it comes from a run and the whole memo can be regenerated when anything
changes. GridCap is a fictional utility.

A **solver recommendation** here is a short memo that answers one question ("which solver should
this service use?") for one service, in a fixed order: the requirements, the candidates checked
against them, the evidence, the decision with its fallback, and the conditions that would reopen it.
The order matters more than the prose. A reviewer who disagrees should be able to point at the line
they disagree with: a requirement, a fact, or a measurement.

## The Model

The model is lesson 5.4.1's project-selection MILP on GridCap's six program slices: one binary
$`x_i`$ per project, maximize $`\sum_i v_i x_i`$, subject to the rows $`\text{must}_i`$,
$`\text{alt}_g`$, $`\text{needs}_c`$ and $`\text{budget}_y`$. The service will also run the timing
model of lesson 6.4.4, which adds a continuous carry-over variable $`r_y \ge 0`$, the money a year
leaves unspent and passes to the next. Lesson 6.4.4 is in section 6, later in the course; all this
lesson needs from it is that $`r_y`$ is a continuous variable. That is why one requirement below is
about continuous variables, though the benchmark's model has none.

## Start From the Requirements, and Make Each One a Yes-or-No Test

A requirement is a property the service cannot do without. Written as a yes-or-no test, it rules a
candidate out by itself, before any number is compared. GridCap's service has three, and the program
keeps them next to the facts that answer them:

```python
FACTS = {
    "HiGHS":  {"in_mathopt": True, "exact_continuous": True, "offline_license": True, "license": "MIT"},
    "SCIP":   {"in_mathopt": True, "exact_continuous": True, "offline_license": True, "license": "Apache-2.0"},
    "CP-SAT": {"in_mathopt": True, "exact_continuous": False, "offline_license": True, "license": "Apache-2.0"},
    "CBC":    {"in_mathopt": False, "exact_continuous": True, "offline_license": True, "license": "EPL-2.0"},
    "Gurobi": {"in_mathopt": False, "exact_continuous": True, "offline_license": False, "license": "commercial"},
}
REQUIREMENTS = (
    ("in_mathopt", "one model code, solver chosen by SolverType (no second model to keep in step)"),
    ("exact_continuous", "continuous variables solved exactly (the timing model's carry-over r_y)"),
    ("offline_license", "runs in a batch container with no internet and no license server"),
)
```

Each fact has a source in this course, and the memo is only as good as that link:

| Fact | Where it was shown |
| --- | --- |
| HiGHS, SCIP and CP-SAT are MathOpt backends in the runner; CBC is only in `pywraplp` | lesson 4.1.2 (`backend_grid.py`) |
| Gurobi cannot be loaded through MathOpt in the runner | lesson 4.1.2 |
| CP-SAT rounds continuous variables and reports `OPTIMAL` | lesson 5.4.1 (`capabilities.py`), lesson 4.2.3 |
| the open-source solvers run with no network and no license server | lesson 5.4.3 (`footprint.py`, the offline runner) |
| a Gurobi license in a container needs internet (WLS) or a token server | lesson 5.4.3, Gurobi's container pages opened 2026-11-11 |

The program prints the requirements and checks every candidate against them:

```python
    passing = []
    for name, facts in FACTS.items():
        failed = [key for key, _ in REQUIREMENTS if not facts[key]]
        print(f"   {name:<7} {'passes' if not failed else 'out: fails ' + ', '.join(failed)}")
        if not failed:
            passing.append(name)
```

```text
RECOMMENDATION: MILP solver for the GridCap planning service

1. Requirements (hard; a candidate failing one is out)
   - one model code, solver chosen by SolverType (no second model to keep in step)
   - continuous variables solved exactly (the timing model's carry-over r_y)
   - runs in a batch container with no internet and no license server

2. Candidates against the requirements
   HiGHS   passes
   SCIP    passes
   CP-SAT  out: fails exact_continuous
   CBC     out: fails in_mathopt
   Gurobi  out: fails in_mathopt, offline_license
   not measured: CPLEX and Xpress (not in the runner). Commercial terms as of the pages opened
   2026-11-11: deployment prices by quote; CPLEX development from $320.00 USD per user per month.
```

Reading the "out" lines:

- **CP-SAT** is out for this service, not in general: it is the course's tool for scheduling and
  logic (section 4.4 on), and the plain selection model would suit it. The carry-over variable is
  what rules it out, because a solver that rounds a continuous variable and reports success produces
  a wrong plan with no error.
- **CBC** solves the model, but only through `pywraplp`, so the service would carry a second copy of
  the model in a second API, two definitions to keep in step (lesson 6.4.2 makes the same argument
  for one shared definition of spend).
- **Gurobi** fails two tests, and they are different in kind. `in_mathopt` fails *in this runner*,
  because of a library mismatch; on a machine with a supported Gurobi install it would pass, or
  the team could use `gurobipy` and accept a second model. `offline_license` fails because of the
  service's network, and no install fixes that: in a private network with no internet, Gurobi needs a
  token server the team would run (lesson 5.4.3). That is a cost and an architecture change, so the
  memo says so in the "revisit" section rather than pretending the option does not exist.
- **CPLEX and Xpress** were not measured, and the memo says that, with the dated terms instead of a
  silence a reader might take for a verdict.

Notice what the filter did *not* use: speed. Three of five candidates are out before a single
benchmark number is read.

## The Evidence Is What the Harness Can Repeat, and Wall Time Enters Only as a Masked Check

The program then runs lesson 5.4.2's harness (six instances, seeds 1 to 3, one thread, gap target 0,
every cell twice) and prints only what it can repeat:

```text
3. Evidence: 6 GridCap instances x seeds 1-3, one thread, gap target 0, each cell run twice
   every solver found the same optimum on every instance: True
   solver   solved  repeats  worst seed spread
   HiGHS    18/18       yes               1.23
   SCIP     18/18       yes               2.02
   CP-SAT   18/18       yes               4.11
   CBC       6/6        yes      n/a (no seed)
   wall-clock SGMs within a factor of 3 of each other: yes (values masked: they change every run)
```

The memo reports three kinds of evidence, chosen because each can be compared across solvers
honestly:

- **Correctness**: every solver found the same optimum on every instance. This is the cross-check of
  lesson 5.4.1, run over the whole set.
- **Reliability**: every run solved, and every cell repeated exactly. For a service whose plans are
  audited (lesson 4.6.3), a solver that does not repeat would be a finding on its own.
- **Seed spread**: on each instance, the largest work over the smallest across seeds, and here the
  worst instance. A ratio has no unit, so unlike raw counts it compares across solvers: it says how
  much a solver's effort on GridCap's models depends on luck. HiGHS's worst is 1.23, SCIP's 2.02,
  CP-SAT's 4.11.

And one thing it deliberately does not report: **which solver is fastest**. Across solvers the only
common unit is wall time, which changes from run to run and machine to machine (lesson 5.4.2). The
program computes each solver's shifted geometric mean of wall seconds and asks one coarse question:
are they all within a factor of 3 of one another? It prints the answer, not the values:

```python
    walls = [summary(cells, solver)["wall_sgm"] for solver in SOLVERS]
    close = max(walls) <= WALL_FACTOR * min(walls)
    print(f"   wall-clock SGMs within a factor of {WALL_FACTOR:g} of each other: "
          f"{'yes' if close else 'no'} (values masked: they change every run)")
```

On this set the answer is yes: speed does not separate the four, and a memo that ranked them by a
few hundredths of a second would be ranking noise. The factor is wide on purpose. A claim like "X is
faster" belongs in a recommendation only when it holds on every repetition of the benchmark, by a
margin larger than the run-to-run noise, with the machine and date stated, as Mittelmann's pages do.

<!-- practice 1 -->

## Name a Default, a Fallback, and What Would Change the Decision

Among the candidates that passed every requirement, solved every run and repeated, the program picks
the one whose work depends least on the seed, and keeps the others as fallbacks:

```python
    finalists = [s for s in passing if summary(cells, s)["solved"] == summary(cells, s)["runs"]
                 and summary(cells, s)["repeat"]]
    choice = min(finalists, key=lambda s: max(seed_spread(cells, s).values()))
    backup = [s for s in finalists if s != choice]
```

```text
4. Recommendation
   Use HiGHS (MIT) through MathOpt as the default solver.
   Reason: it meets every requirement, solved and repeated every run, and its work varied least
   across seeds; speed does not separate the candidates on this set.
   Keep SCIP (Apache-2.0) as the second solver: same model code, one enum away.
   It accepts quadratic objectives and indicator constraints, which HiGHS refuses (capabilities.py showed both).

5. Revisit when
   - a GridCap large solve misses its gap target inside the batch window;
   - the service may call out to a license service (then price a commercial solver);
   - OR-Tools is upgraded: rerun this harness on the new pin before switching.
```

Three parts, each with a job:

1. **The default, with its reason in one sentence**, each clause backed by a line above it. The reason
   is not "HiGHS is the best solver"; it is that HiGHS met the requirements and was the most
   predictable on these models. A reviewer can check every word.
2. **The fallback**, chosen so that switching costs nothing: SCIP is one `SolverType` away, and it
   covers the features HiGHS refuses. If the default ever fails in production, or the model grows an
   indicator constraint, the team already knows where to go and has measured it.
3. **The conditions that reopen the decision.** This is the real answer to "shouldn't we just buy
   Gurobi?": not now, and here is exactly when. GridCap large (10,000 projects) is beyond every
   free tier (lesson 5.4.3) and was not in this benchmark; if it misses its gap target in the nightly
   window, the team requests a commercial evaluation license, adds that solver to the harness, prices
   the token server or the internet route, and reruns this program. An OR-Tools upgrade reruns it too,
   because every solver in the runner is a bundled build.

Two habits keep the memo honest after it is approved. **Every figure that can change carries its
date**: the commercial terms say "as of the pages opened on 2026-11-11", and a reader in a year knows
to check. **The memo is regenerated, not edited**: `recommend.py` lives next to the harness, so the
next review starts from a fresh run instead of last year's numbers.

<!-- practice 2 -->

## Summary

- **Start from the requirements, and make each one a yes-or-no test** with a fact behind it; the
  filter ruled out CP-SAT, CBC and Gurobi before any benchmark number was read.
- **The evidence is what the harness can repeat**: correctness, reliability and the unit-free seed
  spread. Wall time enters only as a masked check, within a factor of 3 here, so speed separated
  nothing.
- **Name a default, a fallback, and what would change the decision.** HiGHS through MathOpt, SCIP one
  enum away, and a revisit when GridCap large misses its window, the network may reach a license
  service, or OR-Tools is upgraded.

## Reference

The memo's sections, in order:

| Section | Holds | Comes from |
| --- | --- | --- |
| 1. Requirements | yes-or-no tests the service cannot do without | the service's design |
| 2. Candidates | pass, or out with the failed tests; what was not measured; dated terms | lessons 4.1.2, 5.4.1, 5.4.3 |
| 3. Evidence | agreement of optima, solved and repeated runs, seed spread, masked wall check | `harness.py` (lesson 5.4.2) |
| 4. Recommendation | default, one-sentence reason, fallback | the rule applied to sections 2 and 3 |
| 5. Revisit when | the measurable conditions that reopen the decision | the gaps in the evidence |

| Claim in a memo | Allowed when |
| --- | --- |
| "X solves our models" | every run on the fixed instance set solved, at a stated gap target |
| "X's runs repeat" | every cell ran twice and agreed on status, objective and work |
| "X's effort depends less on luck than Y's" | the unit-free seed spread is lower, on the same instances and seeds |
| "X is faster than Y" | on every repetition, by a stated factor, with machine and date |
| "X costs ..." | quoted with the date of the vendor page or quote |

**Further reading:** [MathOpt](https://developers.google.com/optimization/math_opt) (one model, the
solver chosen by `SolverType`, and which solvers need a paid license); [Benchmarks for Optimization
Software](https://plato.asu.edu/bench.html) (benchmarks published with machine, date and logs, and the
end of commercial participation); [MIP Benchmarking: Don't Abuse the Standards](https://www.fico.com/blogs/mip-benchmarking-don-t-abuse-standards)
(FICO, 2018: claims that read as general when they were measured on a subset); [Gurobi pricing and
licensing](https://www.gurobi.com/pricing/) (quote-based subscriptions and license models);
[Gurobi docker-python](https://github.com/Gurobi/docker-python) (license routes in containers);
[IBM ILOG CPLEX Optimization Studio pricing](https://www.ibm.com/products/ilog-cplex-optimization-studio/pricing)
(the dated development price in the memo); [FICO Xpress license options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options)
(evaluation licenses for a trial in the harness).

## Challenges

1. Add a fourth requirement, "accepts indicator constraints", to `REQUIREMENTS` and the facts.
   Predict the memo's recommendation and fallback before you run it.
2. Make CP-SAT pass by dropping the carry-over requirement. Predict whether it becomes the default,
   and which line of the evidence decides.
3. Write the "Revisit when" line that would apply if GridCap's planners accepted plans within 1% of
   optimal. Which harness setting changes, and which lesson 5.4.2 table tells you the work could drop?

## Design Note: A Recommendation Is a Program, Not a Slide

A slide records a decision; a program records how it was reached. Kept as `recommend.py` next to the
harness, the recommendation can be rerun when the pin moves, challenged line by line, and diffed
against last year's output. The prose around it (who asked, what was decided in the meeting) goes in
the team's decision log, with a link to the commit of the program that produced it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**recommend.py.** The whole memo: requirements, candidates, the harness's evidence, the
recommendation and the revisit conditions (every section of this lesson). *Try:* Set `WALL_FACTOR` to
1.0. Predict which lines of the memo change, then explain why the program now refuses the claim it
made before.

- Program: [recommend.py](src/recommend.py)
