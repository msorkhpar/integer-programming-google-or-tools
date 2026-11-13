# 11.2.3 Automated Tuning, and How Not to Overfit It

Lesson 11.2.2 changed one knob at a time by hand. A GridCap engineer now proposes to let a program
do it: try every combination of a few Gurobi parameters on the Ridge region's model, keep the
fastest, and ship it. The program finds a setting that proves the Ridge plan with a fifth of the
default's work. On the other regions it is slower than the default. This lesson builds that tuner,
shows why its best result looked so good, and turns it into a procedure whose result can be trusted:
score on a set, hold out whole groups of instances the tuner never sees, and re-measure the winner
with other seeds. It ends with Gurobi's own tuning tool, which runs the same kind of search for you,
and what of its answer you can quote. GridCap is a fictional utility; its numbers are teaching data.

**Overfitting** is the name, borrowed from statistics, for a choice that fits the data it was chosen
on better than it fits the data it will meet. A tuned solver setting is such a choice.

**Without a Gurobi license.** Both of this lesson's programs, `overfit.py` and
`gurobi_tune.py`, run Gurobi, and every gurobipy program needs a Gurobi license to start (the
kinds of license, and how to give the runner yours, are in lesson 5.3.4). Without one, you can read
their output but not reproduce it. The procedure itself does not depend on the solver: the lesson's
practices run without a license, and the HiGHS and SCIP programs of lesson 11.2.2
(`settings_highs.py`, `settings_scip.py`) produce the kind of paired measurements this lesson tunes
on.

## The Model

The regional timing model of lessons 11.2.1 and 11.2.2, unchanged, built in gurobipy
(`grb_runs.build_gurobi`). The tuning set has sixteen regional plans: the four regions of the medium
portfolios drawn with seeds 2027, 1, 2 and 3 (`tuner.tuning_set`). Every plan stays under the
size-limited Gurobi license's 2,000 variables and rows.

**Sets.** $`P`$ the region's projects; $`Y`$ the ten plan years; $`T_i \subseteq Y`$ the start years
of project $`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, the spend of project $`i`$ in its $`k`$-th
year of work ($k); $`B_y`$, the region's budget in year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$.

**Objective and constraints.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \\
\text{s.t. }& \sum_{t \in T_i} x_{i,t} \le 1 \quad \forall i \in P \setminus M && \text{(once}_i) \\
& \sum_{t \in T_i} x_{i,t} = 1 \quad \forall i \in M && \text{(must}_i) \\
& \sum_{i \in g} \sum_{t \in T_i} x_{i,t} \le 1 \quad \forall g \in \mathcal{G} && \text{(alt}_g) \\
& \sum_{u \in T_c,\, u \le t} x_{c,u} \le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} \quad \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
& \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} \le B_y \quad \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## A Tuner Is a Search Over Settings, Scored on a Fixed Set

An automated tuner has three parts, and each is a choice you make before running it:

1. **The search space**: which parameters, and which values. `tuner.py` searches a grid: every
   combination of Gurobi's `MIPFocus` (0, 1, 2), `Cuts` (-1 automatic, 0 off, 1 conservative) and
   `Presolve` (-1 automatic, 1 conservative), eighteen configurations, the default among them.
2. **The score**: one number per configuration. Here it is lesson 5.4.2's shifted geometric mean of
   the work to prove optimality over the instances scored, in thousandths of a Gurobi work unit with
   a shift of 10. Deterministic work, so a score repeats exactly.
3. **The rule**: the configuration with the lowest score wins; on a tie, the earlier one, so the
   default wins any tie.

```python
GRID = {"MIPFocus": (0, 1, 2), "Cuts": (-1, 0, 1), "Presolve": (-1, 1)}
```

```python
def pick(table: dict, names: list[str], configs: list[dict], seed: int = 1) -> dict:
    """The configuration with the best score on `names`; ties go to the earlier one (the default first)."""
    return min(configs, key=lambda c: score(table, names, c, seed))
```

Each plan's model is built once and re-solved under each configuration. Gurobi keeps what it
learned from the last solve of a model object (basis, incumbent) and reuses it unless the model is
reset, as its Warm Start Options page says, so every solve begins with `reset()`, and every parameter of the grid is set explicitly:

```python
        m.reset()                                  # forget the last solve, so no run starts from another
        m.Params.Threads, m.Params.Seed, m.Params.MIPGap = 1, seed, 0.0
        for name, values in GRID.items():
            m.setParam(name, config.get(name, values[0]))
        m.optimize()
```

`overfit.py` solves all eighteen configurations on all sixteen plans with seed 1, then asks what a
tuner would have chosen from part of that table, and how the choice does on the rest.

## The Winner on the Training Set Looks Better Than It Is

Start with the engineer's tuner: tune on one plan. The **training set** is the instances a tuner
chooses on; the **test set** (or held-out set) is instances it never sees, kept to report on. Here
each of the four regions of portfolio 2027 in turn is the whole training set, and the twelve plans of
the other three portfolios are the test set:

```text
tuned on one training plan alone:
  Ridge-2027   Cuts=0 Presolve=1                    that plan 0.20   test 1.05
  Valley-2027  Cuts=1 Presolve=1                    that plan 0.91   test 1.01
  Coast-2027   default                              that plan 1.00   test 1.00
  Plains-2027  Cuts=1 Presolve=1                    that plan 0.77   test 1.01
```

Tuned on Ridge alone, the tuner found a configuration that proves Ridge with 0.20 of the default's
work: five times faster. On the twelve plans it never saw, the same configuration needs 5% *more*
work than the default. Valley's and Plains's winners, 9% and 23% faster on their own plans, are 1%
slower on the test set. Coast's winner is the default itself.

Why does the best score lie? Each of the eighteen scores on one plan is the true effect of the
configuration plus the luck of one search path: lesson 5.4.2 measured CP-SAT's work varying by up
to 4.11 times between seeds of one instance. Taking the minimum of eighteen such numbers picks
the configuration whose luck was best, so the winning score is biased low by construction. This is
sometimes called the **winner's curse**, and it grows with the number of configurations tried and
shrinks with the number of instances each score averages over. Ridge's 0.20 is mostly luck that
happened to that one model.

Now tune on all four plans of portfolio 2027 together:

```text
18 configurations x 16 regional plans; train on 4 (Ridge-2027, Valley-2027, Coast-2027, Plains-2027),
test on the other 12

best five on the training set (SGM of work to proof, as a ratio to the default):
  Cuts=1                               train 0.97   test 0.95
  Cuts=1 Presolve=1                    train 0.99   test 1.01
  default                              train 1.00   test 1.00
  MIPFocus=1                           train 1.09   test 1.14
  MIPFocus=1 Cuts=1                    train 1.09   test 1.14

the tuner's choice, Cuts=1: train 0.97, test 0.95, rank 1 of 18 on the test set
the best on the test set, in hindsight: Cuts=1, test 0.95
on the 12 test plans the choice needs less work than the default on 9, more on 3
```

Averaging over four plans, the winner's score is far more modest: 0.97, a 3% gain, not 80%. And this
time the choice held on the test set: 0.95, nine wins against three losses, and the best of the
eighteen there too. Only the third line of the ranking, the default, is guaranteed to score 1.00 on
both sets. The rule from this section: **score on a set of instances, never on one, and judge the
winner only by its score on instances it was not chosen on.**

<!-- practice 1 -->

## Hold Out Whole Groups the Tuner Never Sees

The test set above is not any twelve plans: it is every plan of three portfolios the training set
does not touch. That matters because instances come in related groups. The four regions of one
GridCap portfolio are drawn by one generator run with one seed; next year's cycle of a region shares
most of its projects with this year's (lesson 11.2.1); a depot's January and February routing models
share roads and customers. If one member of a group is in the training set and another in the test
set, the test **leaks**: the tuner has in effect seen part of it, and the test score inherits some of
the training score's luck.

So split by group: decide the groups first (here, the portfolio seed), then put whole groups on each
side. When there are too few instances to spare a test set, **cross-validation** reuses them: divide
the groups into $`k`$ folds, tune on all folds but one and test on the one left out, once per fold,
and report the test scores of all $`k`$ runs. Each instance is then tested exactly once, by a tuner
that never saw its group. The split, like the instance set, is fixed before the first run
(lesson 5.4.2's first rule).

For a service that re-plans every year, a second rule follows from lesson 11.2.1: the instances it
will meet are next year's cycles. Tune on past cycles and test on later ones, never the reverse.

<!-- practice 2 -->

## Re-Measure the Winner With Other Seeds

The test-set score is still one measurement per plan with one seed. Before shipping, the last step
re-solves the training plans with the winner and the default under other seeds:

```text
the choice re-measured on the training plans with other seeds:
  seed 1: train 0.97   (the seed it was tuned with)
  seed 2: train 1.03
  seed 3: train 0.98
(shift 10, work in thousandths of a Gurobi work unit; below 1 is less work than the default)
```

With seed 2, the winner is 3% *slower* than the default on the very plans it was chosen on. A 3% gain
that turns into a 3% loss when the seed changes is inside the seed noise. Lesson 11.2.2's practice
writes the rule down: a measure counts as better only if its ratio is below 1 by more than a margin
and the wins outnumber the losses. With a 5% margin, `Cuts=1` is no effect on the training set under
any of the three seeds, and its 0.95 on the test set is right at the margin.

So the honest summary of this tuning run is: **no configuration in this grid beats Gurobi's default
on these models by a margin larger than the noise.** `Cuts=1` may help a little (it ranked first on
the held-out plans, nine wins to three); confirming that would take more held-out plans and seeds,
not more configurations. That is not a failure of the tuner. It is the tuner answering the question
honestly, which the one-plan tuner of the previous section did not.

## Gurobi's Tuning Tool Runs the Same Search on the Clock

Gurobi ships its own tuner. `Model.tune()` tries parameter settings on the model and keeps the ones
that improve it; Gurobi's documentation describes it in these terms, which map onto this lesson's
three parts:

- **search space**: the tool chooses the parameters itself; the command-line version can restrict
  them (`TuneParams`), the API cannot;
- **score**: runtime first; for a MIP that does not reach its gap target within its time limit, a
  secondary criterion, the gap by default (`TuneCriterion` changes it); each setting is solved
  `TuneTrials` times with different seeds, combined by `TuneMetric` (average or worst case);
- **rule and result**: the tool keeps a small Pareto set of results (`TuneResults`), the best
  setting changing one parameter, the best changing two, and so on, dropping any that a setting
  with fewer changes matches.

`TuneTimeLimit` bounds the whole search. `gurobi_tune.py` runs it on the Ridge plan:

```python
model.Params.Threads = 1
model.Params.TuneTimeLimit = 10        # seconds on the clock for the whole search
model.Params.TuneTrials = 2            # each candidate setting is solved with two seeds
model.Params.TuneOutput = 0            # no tuning log
```

```python
        model.getTuneResult(k)             # copies parameter set k into the model
        path = os.path.join(folder, f"set{k}.prm")
        model.write(path)                  # a .prm file lists the parameters that differ from the defaults
```

```text
tuned Ridge-2027 for 10 s of wall-clock time, 2 trials per setting, one thread
parameter sets kept: <masked>; parameters they change: <masked>
every set kept changes Threads, which the program set itself: True
the grbtune command line, which tunes several models at once, is on this machine: False
```

The page masks what the tool found, because the tool times its trials on the clock: how many
settings it tries in ten seconds, and which ones win, change with the machine and its load. Run the
program twice and compare. What it shows reliably is the shape of the answer: each kept set is
written relative to the defaults, so the fixed `Threads` of the program appears in every one of them.

Three consequences for a planning service:

1. **The tool tunes the models you give it, and nothing else.** Through the Python API that is one
   model. The documentation's command-line tool, `grbtune`, takes several model files and scores
   across them, but it is not in the course runner (the last line above), so a set has to be tuned
   the way `tuner.py` does it, or with `grbtune` on a machine that has it.
2. **Its suggestion is a training-set result.** Everything in the previous sections applies: test it
   on held-out groups with your own deterministic measure before adopting it. Gurobi's documentation
   says as much: tuning results are noisy, small changes to a model or a seed can swing performance a
   lot, and the tool does not replace careful testing or good modeling.
3. **Its time limit is the budget of the search, not of a solve.** Ten seconds on a model that solves
   in hundredths of a second is many trials; on a model that takes a minute it is none. Set
   `TimeLimit` for each trial too, as the documentation recommends.

## Keep a Tuned Setting Only While It Keeps Winning Held-Out Tests

A tuned setting is a claim about one solver version, one formulation and one kind of data. Any of
those can change: a new OR-Tools or Gurobi release, a new rule in the model (lessons 11.3.1 to 11.3.4
add decomposition), a bigger portfolio. So the setting is stored like a plan's run manifest (lesson 10.2.4): the values, the solver version, the instance set
and split, the seeds, the score on held-out groups, and the date. Before each release of the
service, rerun the held-out comparison of the stored setting against the default; if it no longer
clears the margin, return to the default, which Gurobi's guidelines describe as generally working
well and which needs no evidence of its own to be the safe fallback.

## Summary

- **A tuner is a search over settings, scored on a fixed set.** Search space, score and rule are
  choices made before the first run; score in deterministic work, and let the default win ties.
- **The winner on the training set looks better than it is.** Tuned on Ridge alone, the winner
  proved Ridge with 0.20 of the default's work and needed 1.05 times the default's on the twelve
  held-out plans; tuned on four plans, its gain was 3%, and held at 0.95 on the test set.
- **Hold out whole groups the tuner never sees.** Related instances (one portfolio's regions, one
  depot's months, one region's cycles) stay on one side of a split; cross-validation folds keep
  groups whole.
- **Re-measure the winner with other seeds.** The 3% gain became a 3% loss with seed 2: inside the
  noise.
- **Gurobi's tuning tool runs the same search on the clock.** It tunes the models it is given, times
  trials on the clock, and its suggestion still needs a held-out test.
- **Keep a tuned setting only while it keeps winning held-out tests,** and store it with the evidence
  for it.

## Reference

| Step | Do | Avoid |
| --- | --- | --- |
| instance set | fixed before the first run, mixed difficulty | adding instances after seeing scores |
| split | whole groups (portfolio, depot, region's cycles) on one side; later cycles to test | random instances, so a group is on both sides |
| score | SGM of deterministic work with a stated shift | wall time; the best of one run |
| choose | lowest training score; ties to the default | one instance; peeking at the test set |
| report | test-set ratio to the default, wins and losses, re-measured with other seeds | the training-set ratio |

| Gurobi tuning parameter | What it sets |
| --- | --- |
| `TuneTimeLimit` | wall-clock budget of the whole search |
| `TuneTrials` | solves per setting, each with another seed |
| `TuneMetric` | how trials (and models) are combined: average or worst |
| `TuneCriterion` | the secondary measure for runs that miss their gap |
| `TuneResults` | how many improving sets to keep |
| `TuneOutput` | how much the tool logs (0 for nothing) |

**Further reading:** Gurobi,
[Parameter Tuning Tool](https://docs.gurobi.com/projects/optimizer/en/13.0/features/tuning.html)
(what `tune` measures, `TuneTimeLimit`, `TuneTrials`, `TuneMetric`, `TuneCriterion`, `TuneResults`,
`TuneOutput`, tuning several models with `grbtune`, and the warning that results are noisy and no
substitute for testing); Gurobi,
[Parameter Guidelines](https://docs.gurobi.com/projects/optimizer/en/13.0/concepts/parameters/guidelines.html)
(the parameters this lesson's grid searches); O. Bastert,
[MIP Benchmarking: Don't Abuse the Standards](https://www.fico.com/blogs/mip-benchmarking-don-t-abuse-standards)
(FICO, 2018: a subset of a benchmark set picked to support a claim misleads unless it is named
next to the full-set result, the same discipline a held-out set imposes on a tuner);
[MIPLIB 2017](https://miplib.zib.de/) (a benchmark set of 240 instances, chosen under solvability
and numerical-stability rules, separate from the larger collection: a fixed set chosen before the
results, the kind a tuner's test set should be);
[Hans Mittelmann's benchmarks](https://plato.asu.edu/bench.html) (results reported as shifted
geometric means over published instance sets); the
[CP-SAT Primer, parameters chapter](https://d-krupke.github.io/cpsat-primer/parameters.html)
(most parameters are best left at their defaults; do not trade hard-instance performance for speed on
easy ones).

## Challenges

1. Add `Heuristics` (0.05, 0.2) to `GRID`. Before running, predict whether the winner's training
   score falls, and whether its test score does.
2. Make the training set the twelve plans and the test set the four of portfolio 2027. Predict
   whether `Cuts=1` still wins.
3. Score by the work to a plan within 1% (lesson 11.2.2) instead of the work to proof. Which
   configuration would you expect to win, and why?
4. Run `gurobi_tune.py` twice and compare what you get. What would you need to store to explain the
   difference to a colleague?

## Design Note: Solve Once, Ask Many Questions

`overfit.py` fills one table, every configuration on every plan, and then answers every question
(one-plan tuning, set tuning, the test ranking) by looking up that table. The expensive part runs
once; the analysis is cheap and can be changed without solving again. It also makes cheating
visible: every number the tuner used and every number it was judged by sit in the same table, and
the split decides which is which.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Both programs need a Gurobi license (lesson
5.3.4); the free size-limited one is enough.

**overfit.py.** Fills the table of eighteen configurations on sixteen plans, then tunes on one plan,
on four plans, and re-measures the choice with other seeds (*The Winner on the Training Set* to
*Re-Measure the Winner*). *Try:* Change the training set to the four Valley and Coast plans of
portfolios 2027 and 1. Predict whether the choice changes.

**gurobi_tune.py.** Runs Gurobi's tuning tool on the Ridge plan for ten seconds and reads its kept
parameter sets (*Gurobi's Tuning Tool*). *Try:* Print the kept sets on your machine, then set
`TuneTimeLimit` to 2 and predict how many sets come back.

- Program: [overfit.py](src/overfit.py)
- Program: [gurobi_tune.py](src/gurobi_tune.py)
- Library: [tuner.py](src/tuner.py)
