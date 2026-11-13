# 5.4.2 Honest Benchmarking: Instance Sets, Seeds, Time-to-Gap, Shifted Geometric Mean

A GridCap engineer switches HiGHS's presolve off, solves the transmission slice of portfolio 1, and
posts in the team channel: "Presolve off cuts the work by 32%: 2,301 LP iterations down to 1,563.
Let's ship it." Both numbers are real, and the program below prints them. The conclusion is not: over
the whole instance set and three seeds, the same switch makes no difference at all. This lesson is
about the gap between those two statements. It builds the benchmark harness that lesson 5.4.4's
recommendation rests on, one rule at a time: what to solve, how often, what to measure, how to stop,
and how to average. GridCap is a fictional utility, and its numbers are teaching data.

A **benchmark** here is a set of solver runs designed to answer one comparison question ("which
solver?", "which setting?") in a way someone else could repeat and check. Each rule below exists
because breaking it has misled real benchmarks. The sources are the ones the optimization community
itself uses: Hans Mittelmann's benchmark pages, the MIPLIB 2017 test set, and a FICO article on how
MIP benchmarks get abused.

## The Model

The model is lesson 5.4.1's project-selection MILP on a program slice, unchanged: one binary
$`x_i`$ per project, maximize $`\sum_i v_i x_i`$, subject to the rows $`\text{must}_i`$,
$`\text{alt}_g`$, $`\text{needs}_c`$ and $`\text{budget}_y`$ with the slice's scaled budgets
$`b_y`$. What varies in this lesson is never the model. It is the instance (which slice), the seed,
the solver and its settings, and the stopping rule.

## A Benchmark Is an Instance Set, Not an Instance

The engineer's claim rests on one model. One model tells you about that model. A solver choice or a
setting will meet every model the service ever solves, so the benchmark needs a set of instances that
stands in for them: the same formulation, a range of sizes and difficulties, chosen *before* anyone
looks at the results.

GridCap's set has six instances: the transmission, distribution and vegetation slices of the medium
portfolios drawn with seeds 2027 and 1. The harness prints them:

```python
    for inst in instances:
        model, _ = build_mathopt(inst)
        print(f"  {inst.name:<18} {len(inst.projects):>4} binaries {len(list(model.linear_constraints())):>4} rows")
```

```text
6 instances x seeds (1, 2, 3) x 4 solvers, each cell run twice
  transmission-2027   130 binaries   34 rows
  distribution-2027   127 binaries   33 rows
  vegetation-2027     132 binaries   27 rows
  transmission-1      115 binaries   33 rows
  distribution-1      146 binaries   34 rows
  vegetation-1        125 binaries   25 rows
```

The sizes are alike; the difficulty is not. Lesson 5.4.1's runs and the tables below show the
vegetation slices solved at the root node with a hundred LP iterations or fewer, and the distribution
slices taking tens of thousands. A set with only easy instances would rank solvers by their start-up
cost; a set with only hard ones would hide what the service mostly solves. Keep both, and keep them
all.

This is also what the MIP community's standard practice asks. MIPLIB 2017's benchmark set of 240
instances is the standard test set for comparing MIP solvers, and FICO's article *MIP Benchmarking:
Don't Abuse the Standards* (O. Bastert, 2018) names the first abuse: picking a subset of a standard
set that favours your solver, then making claims that read as if they held for the whole set. If a
subset is reported at all, it is named, instance by instance, next to the full-set result. For a team
benchmark the same rule reads: **fix the instance set before the first run, and report on all of it.**

## Seeds Expose Performance Variability, So Each Instance Runs Under Several

A MILP solver makes many choices that have no right answer (which fractional variable to branch on
when two score the same, which of two equal cuts to add first), and it breaks such ties with a
pseudo-random number generator. Its **random seed** fixes that generator's sequence. MathOpt passes
`SolveParameters(random_seed=...)` to the solver, with a valid range that depends on the solver
(`parameters.py`); CP-SAT's `random_seed` reinitializes its generator at the start of each solve
(`sat_parameters.proto`); SCIP's `randomization/randomseedshift` shifts all its random seeds. A
different seed sends the search down a different path to the same optimum, and the work can differ
a lot. That is **performance variability**: a change in work that comes from the path, not from the
solver being better or worse.

The harness solves every instance with seeds 1, 2 and 3 and prints, per instance, the largest
over the smallest work across the three seeds, in each solver's own unit:

```text
seed spread, largest/smallest over seeds 1-3:
  HiGHS  transmission-2027 1.06  distribution-2027 1.23  vegetation-2027 1.02  transmission-1 1.05  distribution-1 1.21  vegetation-1 1.00
  SCIP   transmission-2027 1.39  distribution-2027 2.02  vegetation-2027 1.00  transmission-1 1.11  distribution-1 1.00  vegetation-1 1.00
  CP-SAT transmission-2027 4.11  distribution-2027 1.44  vegetation-2027 1.00  transmission-1 1.36  distribution-1 1.85  vegetation-1 1.00
```

CP-SAT's work on transmission-2027 varies by a factor of 4.11 between seeds; SCIP's on
distribution-2027 by 2.02. A comparison that ran each solver once could report a factor of 2 or 4
that is nothing but the seed. So each (solver, instance) pair runs under several seeds, and each
(instance, seed) pair counts as one observation. Mittelmann's MILP page adds variability another way:
it preprocesses each instance by randomly perturbing the order of its rows and columns with SCIP, so
no solver benefits from the order the file happened to be written in.

These ratios are unit-free, so unlike raw counts they *can* be set side by side across solvers:
"how much does this solver's work depend on luck" is a fair question to ask of each. Lesson 5.4.4
uses it.

## The Shifted Geometric Mean Summarizes Ratios, and Its Shift Keeps Easy Instances From Dominating

After the runs, each solver has one number per observation, and the comparison needs one number per
solver. Which average? `sgm.py` compares three on made-up times for two solvers, A and B, on the
same five instances. A is twice as fast on the four easy ones, B twice as fast on the one hard one:

```text
times (s)         A: [0.1, 0.2, 0.4, 0.8, 3600.0]
                  B: [0.2, 0.4, 0.8, 1.6, 1800.0]
arithmetic mean   A    720.30   B    360.60   B/A 0.501
geometric mean    A      1.87   B      2.84   B/A 1.516
shifted, sh=1     A      5.54   B      5.76   B/A 1.040
shifted, sh=10    A     23.43   B     19.94   B/A 0.851
shifted, sh=100   A    106.51   B     81.28   B/A 0.763
```

- **The arithmetic mean** says B takes half as long (0.501). It is decided entirely by the one hard
  instance; the four others could change tenfold and the ratio would barely move. Run times of MILP
  solvers spread over orders of magnitude, so the arithmetic mean is a report on the slowest
  instance.
- **The geometric mean**, the $`n`$-th root of the product, averages *ratios*: each instance counts
  the same however long it takes. It says B is 1.516 times slower, because B is twice as slow on four
  instances out of five. But those four are differences between a tenth of a second and two tenths,
  which no user would ever notice.
- **The shifted geometric mean** adds a shift $`s`$ to every value before taking the geometric mean,
  and subtracts it after. Values much smaller than $`s`$ all look alike; values much larger than
  $`s`$ keep their ratios. With $`s = 10`$, B comes out ahead (0.851): the hard instance, where the
  difference is half an hour, counts; the easy ones, where it is fractions of a second, do not.

The form Mittelmann's pages define, for nonnegative values $`v_1, \dots, v_n`$ and a shift
$`s \ge 0`$:

```math
\text{SGM}_s(v) = \exp\!\Big(\frac{1}{n} \sum_{i=1}^{n} \ln \max(1,\; v_i + s)\Big) - s
```

His benchmarks measure wall-clock seconds and use $`s = 10`$, then divide each solver's mean by the
smallest one, so the best solver scores 1 (the "scaled" row of lesson 5.4.1's table). The
$`\max(1, \cdot)`$ keeps every logarithm nonnegative, so a run of a few milliseconds cannot drag the
mean toward zero. That only works when the unit makes 1 small. Every $`v_i + s`$ below 1 counts as
exactly 1, so values that small all tie, whatever their ratios. In seconds with $`s = 10`$ no value
gets there. In a unit where typical values are fractions, such as 0.0001, most values fall under 1
and the mean measures the clamp instead of the solver. So pick a unit in which even the easiest
instance costs well above 1, and a shift $`s \ge 1`$. In code:

```python
def shifted_geometric_mean(values: list[float], shift: float) -> float:
    """exp(mean of ln(max(1, v + shift))) - shift, for nonnegative values and a nonnegative shift."""
    if not values:
        raise ValueError("no values")
    logs = [math.log(max(1.0, v + shift)) for v in values]
    return math.exp(sum(logs) / len(logs)) - shift
```

The second half of `sgm.py` isolates the shift's job. Solvers C and D tie on four hard instances
(100 s each); on four easy ones C takes 0.01 s and D 0.1 s:

```text
Four easy instances and four hard ones: C and D tie on the hard ones
geometric mean    C      1.00   D      3.16   D/C 3.162
shifted, sh=1     C      9.10   D      9.54   D/C 1.048
shifted, sh=10    C     23.18   D     23.33   D/C 1.006
```

The plain geometric mean calls D more than three times slower, over differences of nine hundredths
of a second. With a shift of 10 the two are within 1%, which is the truth a user would see.

Three rules follow, and the program's first table shows why each matters:

1. **The shift is a choice, and it can flip the ranking.** A beats B at shift 0 and shift 1 and loses
   at 10 and 100. Report the shift with every mean, and pick it before looking at the results.
2. **Choose the shift at the size of a difference nobody cares about.** Mittelmann's 10 seconds fits
   runs with a two-hour limit. GridCap's harness measures work, not seconds, so it uses a shift of
   100 LP iterations, or 100 millionths of a deterministic second for CP-SAT: about what the
   cheapest runs in the set cost (the harness prints them below). CP-SAT reports its deterministic
   time in seconds, and its cheapest run costs 0.0001 of one, so the harness counts that time in
   millionths (`micro_det_time`), where the same run costs 100. Counted in seconds with a shift of
   0.01, every run under about one deterministic second would hit the $`\max(1, \cdot)`$ and tie.
3. **A run that fails still counts.** Dropping it would reward a solver for failing on the hardest
   instances. Mittelmann counts every non-success as the time limit; the harness counts an unfinished
   run at a cap. The FICO article also warns against swapping in other scores: PAR10, which charges a
   failure ten times the limit, is a penalty score, so it cannot support "solver A is $`k`$ times
   faster than solver B".

<!-- practice 1 -->

## Fix the Gap Target Before You Time Anything, Then Measure Time-to-Gap

"How long to solve it" sounds like one question, but a MILP solver stops when its **relative gap**,
the distance between its best plan and its bound on all plans, divided by a reference value (lesson
3.4.1), falls below a target. Different targets are different questions. `time_to_gap.py` first
solves the hardest instance with no target set, each solver on its own default:

```text
with no gap target set (each solver's own default), through MathOpt:
  HiGHS   OPTIMAL  objective 56,119  bound 56,124.0  gap 0.0089%
  SCIP    OPTIMAL  objective 56,119  bound 56,119.0  gap 0.0000%
  CP-SAT  OPTIMAL  objective 56,119  bound 56,119.0  gap 0.0000%
```

All three say `OPTIMAL`, but HiGHS stopped with its bound $5k above its plan: its documented default
`mip_rel_gap` is $`10^{-4}`$, so a gap of 0.0089% counts as optimal for HiGHS. SCIP's documented
`limits/gap` default is 0, and it closed the gap. A benchmark run on defaults would time HiGHS to
"within 0.01%" and SCIP to "exactly", and call both "time to optimal". **Set one gap target for every
solver**: the harness passes a relative gap of 0 to each.

The gap's *formula* differs too: HiGHS divides by its primal bound, SCIP by the smaller of the two
values (its `limits/gap` documentation and lesson 3.4.1), and CP-SAT's parameters proto defines its
relative gap as $`|O - B| / \max(1, |O|)`$. So the harness never trusts a solver's own gap. It
computes one gap for every run, $`|\text{bound} - \text{objective}| / |\text{objective}|`$, from the
objective and bound each solver returns:

```python
    def gap(self) -> float:
        """|bound - objective| / |objective|: one definition for every solver, the course's relative gap."""
        return abs(self.bound - self.objective) / max(abs(self.objective), 1e-9)
```

Then the measure that matters to a service. GridCap's planners accept a plan within 1% of optimal
when the night is short. **Time-to-gap** is the work a solver needs to reach a given gap, and it can
rank solvers differently from time to optimal. The program stops each solver at targets of 5%, 1%,
0.1% and 0 on the same instance, with seed 1:

```python
    runs = [run(solver, inst, 1, gap=g) for g in TARGETS]
    full = runs[-1].work[unit]
    for g, r in zip(TARGETS, runs):
        print(f"{solver:<7} {g:>7.1%} {r.objective:>10,.0f} {r.bound:>10,.1f} {r.gap():>8.4%} "
              f"{r.work[unit]:>10g}  {r.work[unit] / full:>6.1%} of {full:g} {unit}")
```

```text
instance distribution-2027: 127 projects, seed 1, one thread
solver   target  objective      bound      gap       work  share of work to optimal
HiGHS      5.0%     55,669   56,504.0  1.4999%        643    2.7% of 23590 lp_iterations
HiGHS      1.0%     55,901   56,447.0  0.9767%       1428    6.1% of 23590 lp_iterations
HiGHS      0.1%     56,119   56,175.0  0.0998%      18761   79.5% of 23590 lp_iterations
HiGHS      0.0%     56,119   56,119.0  0.0000%      23590  100.0% of 23590 lp_iterations
SCIP       5.0%     55,094   56,872.7  3.2286%         22    0.1% of 23085 lp_iterations
SCIP       1.0%     55,827   56,349.4  0.9358%       2307   10.0% of 23085 lp_iterations
SCIP       0.1%     56,119   56,172.1  0.0947%      23030   99.8% of 23085 lp_iterations
SCIP       0.0%     56,119   56,119.0  0.0000%      23085  100.0% of 23085 lp_iterations
CP-SAT     5.0%     54,073   56,770.0  4.9877%     0.0005    0.0% of 2.0947 det_time
CP-SAT     1.0%     55,987   56,541.0  0.9895%     0.5915   28.2% of 2.0947 det_time
CP-SAT     0.1%     56,119   56,135.0  0.0285%     2.0928   99.9% of 2.0947 det_time
CP-SAT     0.0%     56,119   56,119.0  0.0000%     2.0947  100.0% of 2.0947 det_time
CBC        5.0%     55,840   56,899.2  1.8969%          0    0.0% of 52537 lp_iterations
CBC        1.0%     55,942   56,496.6  0.9914%      12394   23.6% of 52537 lp_iterations
CBC        0.1%     56,119   56,119.0  0.0000%      52537  100.0% of 52537 lp_iterations
CBC        0.0%     56,119   56,119.0  0.0000%      52537  100.0% of 52537 lp_iterations
```

What the table shows:

- **The last fraction of a percent costs most of the work.** HiGHS reaches 1% with 6.1% of the LP
  iterations it needs to prove optimality, SCIP with 10.0%, CBC with 23.6%. Each had the optimal plan,
  $56,119k, well before it could prove it: at 0.1%, HiGHS, SCIP and CP-SAT already hold it, and the
  rest of the run only lowers the bound.
- **The shares rank the solvers differently at each target.** At 1%, CP-SAT has spent 28.2% of its
  work to optimal and HiGHS 6.1%. A benchmark of time to optimality and a benchmark of time to 1% can
  recommend different solvers, so measure the one your service will run.
- **A solver checks its gap only at points of its own choosing**, so it overshoots the target: asked
  for 5%, HiGHS stopped at 1.4999%. Report the gap reached, not the target asked.
- **A count can leave work out.** CBC reports 0 LP iterations at the 5% stop, though it holds a
  bound of 56,899.2 that only an LP solve could give: its iteration count evidently does not include
  the root LP. One more reason a count compares runs of one solver only.

The same idea appears in public benchmarks. Mittelmann's MIPFEAS page ranks solvers by the **primal
integral**: the gap between the incumbent and the optimum, integrated over the run and divided by its
length, so a solver that finds good plans early scores well even if it proves nothing. Time-to-gap is
its simplest form: one point on that curve.

<!-- practice 2 -->

## Measure Deterministic Work Where You Can, and Mask Wall Time Where You Cannot

Wall-clock seconds are what users feel, and they are what Mittelmann's pages report, all measured on
one machine. They are also different on every run: the same solve takes longer when another process
is busy, when the CPU throttles, or when the machine is a different one. A course page has to print
output that repeats, and so does a benchmark report that someone else is meant to check. So the
harness follows one rule: **measure each solver in a deterministic unit when it offers one, and treat
wall time as a measurement whose method you publish but whose numbers you do not.**

Each cell (solver, instance, seed) runs twice, and a cell counts as repeated only if both runs agree on
the status, the objective and every work count. The summary for one solver:

```python
def counted(r: Run, measure: str) -> float:
    return r.work[measure] * UNIT[measure][1] if r.solved else CAP[measure]


def summary(cells: list[Cell], solver: str) -> dict:
    mine = [c for c in cells if c.first.solver == solver]
    measure = MEASURES[solver][0]
    return {
        "solver": solver,
        "unit": UNIT[measure][0],
        "shift": SHIFT[measure],
        "runs": len(mine),
        "solved": sum(c.first.solved for c in mine),
        "repeat": all(c.repeated for c in mine),
        "sgm": shifted_geometric_mean([counted(c.first, measure) for c in mine], SHIFT[measure]),
        "wall_sgm": shifted_geometric_mean([c.first.wall for c in mine], WALL_SHIFT),
    }
```

```text
every solved run found the same optimum on its instance: True

solver  unit            shift  runs  solved  repeats        SGM   wall SGM
HiGHS   lp_iterations     100    18      18      yes    3066.25   <masked>
SCIP    lp_iterations     100    18      18      yes    1432.04   <masked>
CP-SAT  micro_det_time    100    18      18      yes   56578.77   <masked>
CBC     lp_iterations     100     6       6      yes    3324.17   <masked>

cheapest run, in each solver's counted unit (each shift is set at about this size):
  HiGHS 93  SCIP 14  CP-SAT 100  CBC 111
```

How to read each column:

- **solved, repeats.** Every run of every solver proved its optimum, the optima agree, and every
  cell repeated exactly, SCIP included. Lesson 6.2.3 saw SCIP node counts change between
  runs on its indicator model; on this set, with one thread and a fixed seed, they did not.
  The harness does not assume either: it checks, cell by cell, and a `NO` would stop a count from
  being quoted.
- **SGM, in each solver's own unit.** These numbers repeat, so they can be quoted, tracked across
  versions, and put in a regression test. They are **not** a ranking: SCIP's 1,432 LP iterations
  against HiGHS's 3,066 do not mean SCIP does half the work (lesson 5.4.1 showed why units of different
  solvers do not compare). CBC has 6 runs because it takes no seed. CP-SAT's 56,578.77 is in
  millionths of a deterministic second, about 0.057 of one.
- **cheapest run.** The least any run cost, in the unit the mean counts. Every one is at least 14,
  so with a shift of 100 every $`v_i + s`$ is well above 1 and the $`\max(1, \cdot)`$ never decides
  a value.
- **wall SGM.** The program computes the shifted geometric mean of wall seconds (shift 1 s) for every
  solver, because across solvers that is the only common unit. It prints `<masked>`, because the
  numbers change on every run, and a page that printed them would be wrong the next time it ran. Run
  `harness.py` yourself and print `s['wall_sgm']` to see them on your machine; run it twice to see
  them move.

So across solvers, an honest report states the wall-clock *method* (same machine, one thread, same
instance set and seeds, same gap target, shift and cap) and gives its results with the date and
machine, as Mittelmann's pages do. Within one solver, deterministic units make a comparison you can
repeat exactly. The next section uses that.

<!-- practice 3 -->

## Compare Settings of One Solver Pairwise, Over Every Seed

Back to the engineer's claim. Within one solver a deterministic unit is a fair yardstick: HiGHS's LP
iterations with presolve on and off count the same steps. `ab_test.py` solves every instance with
every seed both ways, and each (instance, seed) pair is one paired observation:

```python
for inst in instance_set():
    for seed in SEEDS:
        a = run("HiGHS", inst, seed)
        b = run("HiGHS", inst, seed, presolve=mathopt.Emphasis.OFF)
        assert round(a.objective) == round(b.objective)
        on.append(a.work["lp_iterations"])
        off.append(b.work["lp_iterations"])
        rows.append((inst.name, seed, on[-1], off[-1]))
```

```text
instance           seed  presolve on      off  off/on
transmission-2027     1       14,289   14,672    1.03
transmission-2027     2       14,993   14,395    0.96
transmission-2027     3       15,185   40,348    2.66
distribution-2027     1       23,590   24,622    1.04
distribution-2027     2       25,215   23,848    0.95
distribution-2027     3       28,902   22,204    0.77
vegetation-2027       1           95      125    1.32
vegetation-2027       2           95      126    1.33
vegetation-2027       3           93      125    1.34
transmission-1        1        2,301    1,563    0.68
transmission-1        2        2,228    1,561    0.70
transmission-1        3        2,190    1,610    0.74
distribution-1        1       24,687   28,470    1.15
distribution-1        2       29,752   20,460    0.69
distribution-1        3       26,650   26,268    0.99
vegetation-1          1          112      115    1.03
vegetation-1          2          112      115    1.03
vegetation-1          3          112      116    1.04
```

The engineer's row is there: transmission-1, seed 1, 2,301 down to 1,563 (0.68). On that instance
the effect is real and steady across seeds. On transmission-2027, seed 3, the same switch multiplies
the work by 2.66; on the other two seeds it does nothing. Averaged:

```text
what one seed alone would conclude (SGM of off / SGM of on, shift 100):
  seed 1: 1.000
  seed 2: 0.895
  seed 3: 1.104
all 18 pairs:  0.996; presolve off used fewer LP iterations in 8, more in 10
```

Someone who benchmarked with seed 2 only would report "presolve off saves 10%"; with seed 3,
"presolve off costs 10%". Over all 18 pairs the ratio is 0.996, and presolve off wins 8 and loses 10:
no effect worth a configuration change. The rule: **compare settings pairwise on every instance and
seed, report the ratio of shifted geometric means and the win/loss count, and treat any single pair
as an anecdote.**

## Summary

- **A benchmark is an instance set, not an instance.** Fix the set before the first run, mix easy and
  hard, and report on all of it (FICO: no cherry-picked subsets).
- **Seeds expose performance variability.** On GridCap's set one seed against another changed the work
  by up to 4.11 times; run several seeds and treat each (instance, seed) as one observation.
- **The shifted geometric mean summarizes ratios, and its shift keeps easy instances from
  dominating.** $`\text{SGM}_s = \exp(\frac1n\sum \ln\max(1, v_i + s)) - s`$; Mittelmann uses
  $`s = 10`$ s and counts failures at the limit. The shift can flip a ranking, so report it.
- **Fix the gap target, then measure time-to-gap.** Defaults differ (HiGHS stops at $`10^{-4}`$),
  formulas differ, and the work to reach 1% can be a small share of the work to optimal.
- **Measure deterministic work where you can, and mask wall time where you cannot.** Counts repeat
  and compare runs of one solver; wall time is the only cross-solver unit and is reported by method,
  date and machine.
- **Compare settings of one solver pairwise, over every seed.** HiGHS presolve off: 0.996 over 18
  pairs, though single seeds said 0.895 and 1.104.

## Reference

| Rule | In the harness |
| --- | --- |
| fixed instance set | `instance_set()`: six program slices of GridCap medium, seeds 2027 and 1 |
| several seeds | `SEEDS = (1, 2, 3)`; CBC once (no seed through `pywraplp`) |
| one thread | HiGHS `int_options={"threads": 1}` (it refuses the common `threads`, lesson 4.2.4), SCIP `threads=1`, CP-SAT `num_workers = 1`, CBC `SetNumThreads(1)` |
| one gap target | relative gap 0 for every solver; the gap reported is the harness's own |
| repeat check | each cell twice; status, objective and all counts must agree |
| failures count | an unsolved run counts at `CAP` |
| summary | `shifted_geometric_mean` with `SHIFT` per unit (100 LP iterations; CP-SAT counted in millionths of a deterministic second, shift 100) |
| wall time | computed, shift 1 s, printed `<masked>` |

| Default stopping gap (documented) | Value |
| --- | --- |
| HiGHS `mip_rel_gap` | $`10^{-4}`$, of $`\lvert ub - lb \rvert / \lvert ub \rvert`$ |
| HiGHS `mip_abs_gap` | $`10^{-6}`$ |
| SCIP `limits/gap` | 0, of $`\lvert p - d \rvert / \min(\lvert p \rvert, \lvert d \rvert)`$ |

| Measure | What it rewards |
| --- | --- |
| arithmetic mean | the slowest instance, almost alone |
| geometric mean | ratios on every instance, the trivial ones included |
| shifted geometric mean | ratios on instances that cost more than about the shift |
| time-to-gap | reaching a good plan with a proof of its quality |
| primal integral (MIPFEAS) | finding good plans early |

**Further reading:** [MathOpt `SolveParameters` in parameters.py, v9.15](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/parameters.py)
(`random_seed` and its solver-dependent range, `relative_gap_tolerance`, `threads`);
[MathOpt `SolveStats` in result.py, v9.15](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/result.py)
(simplex iterations, node count, wall-clock solve time); [CP-SAT parameters, sat_parameters.proto, v9.15](https://github.com/google/or-tools/blob/v9.15/ortools/sat/sat_parameters.proto)
(`random_seed`, `max_deterministic_time`, the relative gap formula, `num_workers`);
[The shifted geometric mean](https://plato.asu.edu/ftp/shgeom.html) (H. Mittelmann; the formula with
$`\max(1, \cdot)`$ and $`s = 10`$); [Benchmarks for Optimization Software](https://plato.asu.edu/bench.html)
(why the shifted geometric mean rather than performance profiles); [MILP Benchmark, MIPLIB 2017](https://plato.asu.edu/ftp/milp.html)
(non-successes counted as the time limit, randomly perturbed instances); [MIPFEAS Benchmark](https://plato.asu.edu/ftp/mipfeas.html)
(the primal integral); [MIP Benchmarking: Don't Abuse the Standards](https://www.fico.com/blogs/mip-benchmarking-don-t-abuse-standards)
(FICO, O. Bastert, 2018: subsets, the shifted geometric mean as the standard, PAR10);
[MIPLIB 2017](https://miplib.zib.de/) (the benchmark set); [HiGHS options](https://ergo-code.github.io/HiGHS/dev/options/definitions/)
(`random_seed`, `mip_rel_gap`, `mip_abs_gap`, `threads`); [HiGHS parallelism](https://ergo-code.github.io/HiGHS/dev/parallel/)
(MIP branch and bound is multithreaded unless switched off; set `threads` before the first solve);
[SCIP parameters](https://www.scipopt.org/doc/html/PARAMETERS.php) (`randomization/randomseedshift`,
`limits/gap` and its formula).

## Challenges

1. In `sgm.py`, find the shift at which A and B tie exactly. What does that shift mean in seconds?
2. Add seed 4 and 5 to `ab_test.py`. Predict whether the 8 wins and 10 losses move toward a verdict.
3. Change the harness's `SHIFT` for LP iterations from 100 to 10,000. Predict which solver's SGM moves
   most, and whether a within-solver A/B ratio would move more or less.

## Design Note: A Benchmark Is a Program, Kept With the Code

Everything that decides a benchmark's outcome (instances, seeds, threads, gap target, shift, cap,
the solver versions) lives in `harness.py` and its pinned image, not in a slide. That makes the result
something a reviewer can rerun, and something the team reruns when OR-Tools is upgraded: the
deterministic SGMs then say exactly how much each solver's work changed, with no noise to argue
about. Keep the harness in the repository next to the model, and keep its instance set under version
control like test fixtures.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**sgm.py.** The shifted geometric mean, and three averages compared on made-up times (*The Shifted
Geometric Mean Summarizes Ratios*). *Try:* Make A's hard instance 7,200 s. Predict which of the five
ratios change most.

- Program: [sgm.py](src/sgm.py)

**time_to_gap.py.** Each solver stopped at four gap targets, and on its own default (*Fix the Gap
Target Before You Time Anything*). *Try:* Run it on `"transmission-1"`. Predict whether the last
fraction of a percent still costs most of the work.

- Program: [time_to_gap.py](src/time_to_gap.py)

**harness.py.** The benchmark: six instances, three seeds, four solvers, each cell twice, summarized
by shifted geometric means (*Measure Deterministic Work Where You Can*). *Try:* Set `SEEDS = (1,)`.
Predict which seed-spread lines disappear and which SGMs change.

- Program: [harness.py](src/harness.py)

**ab_test.py.** HiGHS with presolve on and off, paired over every instance and seed (*Compare
Settings of One Solver Pairwise*). *Try:* Compare SCIP with `cuts=mathopt.Emphasis.OFF` instead.
Predict the direction before you run it.

- Program: [ab_test.py](src/ab_test.py)
