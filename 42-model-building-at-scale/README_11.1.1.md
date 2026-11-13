# 11.1.1 Measuring Build Time vs. Solve Time

GridCap's planners have run the timing model on the medium portfolio (400 projects) for a year.
Next cycle they move to the large one: 10,000 projects over 10 years, about 22,000 binary
variables. The first trial run feels slow, and two fixes are proposed in the same meeting: buy a
faster solver, or rewrite the code that builds the model. Both cost weeks. Neither should start
before someone knows where the run's time goes. This lesson measures it, in four rules, and the
numbers it prints are a method more than a result: your machine will give different ones.

## The Model

Every program in this module builds and solves the same model: the timing model of lessons 6.4.1
and 6.4.2, with cash flow spread across the years of work and precedence in the
cumulative form of lesson 6.4.3. Nothing in it changes in this module; what changes is how fast and
how safely it is built.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use (its window, cut so the work ends inside $`Y`$); $`M \subseteq P`$ the must-do projects;
$`\mathcal{G}`$ the alternative groups, each a set of projects; $`C \subseteq P`$ the child projects,
with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

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

In code, variable $`x_{i,t}`$ is named `x_P00001_2029` on the large portfolio, and the rows are
named after their labels: `once_P00001`, `must_P00041`, `alt_G00015`, `after_P00027_2031`,
`budget_2031`. `loop_builder.py` is
lesson 6.4.2's builder, copied so this module runs on its own; its `build_loops(portfolio)` is the
reference every faster builder in this module must reproduce.

## A Run Has Phases, and Each Phase Gets Its Own Clock

A planning run does four things in order: it gets the data (here, `generate` the portfolio), builds
the model, hands the model to the solver, and solves it. Put a clock around each one, not one
clock around the whole run. `time.perf_counter()` is the clock to use: Python documents it as the
highest-resolution clock for short durations, and only the difference between two readings means
anything.

```python
def one_run(size: str) -> tuple[dict[str, float], mathopt.Model, mathopt.SolveResult]:
    """One planning run, the way a service does it, with a clock around each phase."""
    clock = {}
    start = time.perf_counter()
    portfolio = generate(size)
    clock["data"] = time.perf_counter() - start

    start = time.perf_counter()
    model = build_loops(portfolio)
    clock["build"] = time.perf_counter() - start

    start = time.perf_counter()
    result = solve_highs(model, PARAMS)
    wall = time.perf_counter() - start
    clock["solve"] = result.solve_stats.solve_time.total_seconds()    # what the solver reports
    clock["hand-off"] = wall - clock["solve"]                          # the rest of mathopt.solve
    return clock, model, result
```

The solve gets two clocks, because `mathopt.solve` does more than solve. Its source shows the
steps: it exports the model to a `ModelProto` (MathOpt's protocol-buffer form of a model, the one a
solver reads), passes the proto to the solver's C++ code, and parses the result back into Python.
`result.solve_stats.solve_time` is MathOpt's own measure of the middle step only, "roughly the time
inside" the solver by its documentation, and it leaves out building the model. The wall time around
`mathopt.solve` minus that reported time is the **hand-off**: export, set-up and parsing.

`PARAMS` stops HiGHS at a 1% relative gap (lesson 3.4.1), the tolerance a planning team would use
for a 10,000-project run. The program does three runs of each size. First the lines that repeat on
every run:

```text
medium: 887 variables, 469 rows, 2,550 nonzeros; OPTIMAL, NPV 226,340k
large : 21,843 variables, 11,467 rows, 63,048 nonzeros; OPTIMAL, NPV 6,028,673k
```

Then the timings, from one run of the program in the course's runner on the author's machine,
while other programs shared the machine. Yours will differ, and so will the next run here:

<!-- unverified -->
```text
measured (3 runs each; medians, then each phase's share of the median total):
medium: data 0.012s (1%)  build 0.044s (4%)  hand-off 0.004s (0%)  solve 0.967s (94%)
large : data 0.342s (4%)  build 1.177s (15%)  hand-off 0.058s (1%)  solve 6.130s (80%)
large LP relaxation: build median 0.751s (range 0.716-0.821, n=3); HiGHS solve median 0.365s (range 0.352-0.384, n=3)
```

Read the shares, not the seconds:

- **On medium, the solve is the run.** The build is 4% of it. A builder twice as fast would save
  2% of the run; a faster solve is the only lever that matters here.
- **On large, the build is no longer noise.** It is 15% of the run: roughly one second of building
  for every five or six seconds of solving to a 1% gap. Building grew about 27 times from medium
  to large, in step with the model's size (25 times as many variables, 25 times as many nonzeros).
- **When the solve is short, the build can be most of the run.** The last line solves the large
  model's LP relaxation (every $`x_{i,t}`$ allowed anywhere in $`[0, 1]`$), as a first bound or a
  quick what-if would. The build took twice as long as the solve.
- **The hand-off is small** (about 1%), but it is not free, and it grows with the model, since the
  whole model is exported on every call.

So the answer to "buy a solver or rewrite the builder?" depends on which run you do most. A team
that solves once a night to a tight gap should look at the solver. A team that rebuilds the model
for every scenario, every what-if and every LP bound pays for the build each time. Lessons 11.2.1
to 11.2.3 work on the solve; this module works on the build.

## One Timing Is an Anecdote: Warm Up, Repeat, and Report the Median and Range

A wall-clock time is a sample. The same build takes a different time on each run, because the
operating system schedules other work, the CPU changes its speed with load and heat, and the first
run of anything pays for caches and memory that later runs reuse. So a timing is reported the way
any noisy measurement is: several samples, a middle value, and their spread. `stopwatch.py` does
it in one function:

```python
def measure(work: Callable[[], object], repeats: int = 5, warmup: int = 1,
            clock: Callable[[], float] = time.perf_counter) -> Timing:
    """Run `work` `warmup` times untimed, then `repeats` times, timing each run on its own."""
    for _ in range(warmup):
        work()
    samples = []
    for _ in range(repeats):
        start = clock()
        work()
        samples.append(clock() - start)
    return Timing(tuple(samples))
```

`Timing` keeps every sample and reports their **median** (the middle sample, which one slow
outlier cannot move) and their range. The `clock` argument is there for tests: a test passes a fake
clock that returns numbers it chose, so it can check the arithmetic without timing anything.

The program times one cold build of the medium model, then seven more. Here are two runs of it,
one after the other, on the same machine:

<!-- unverified -->
```text
first build, cold: 0.031s
next 7 builds: 0.021 0.026 0.026 0.020 0.021 0.023 0.020
build_loops(medium): median 0.021s (range 0.020-0.026, n=7)
first build / median: 1.5x
```

<!-- unverified -->
```text
first build, cold: 0.044s
next 7 builds: 0.033 0.035 0.037 0.049 0.036 0.043 0.054
build_loops(medium): median 0.037s (range 0.033-0.054, n=7)
first build / median: 1.2x
```

The same code on the same data took a median of 0.021 s in one run and 0.037 s in the next, more
than the spread inside either run. Two things follow:

- **Warm up before you time.** The cold build was the slowest sample both times. `measure` runs the
  work once untimed (`warmup=1`) so that one-time costs do not land in the samples.
- **Compare like with like: same process, same machine, one right after the other.** Whatever made
  the second run slower made everything in it slower. A ratio of two builders measured side by
  side survives that; two absolute times measured at different moments do not. When the machine is
  busy, alternate the two builders round by round (old, new, old, new, ...) and take the ratio
  within each round, so a slow patch hits both. This module's speed-ups are always ratios of
  builders timed in one process.

A speed claim in a test would fail on a busy machine for reasons that have nothing to do with the
code. So this module never asserts a time in a test. Its tests check what the speed is *for*: that
a fast builder makes exactly the model the slow one makes (lesson 11.1.2). The timings are run and
read by a person, like the ones above.

<!-- practice 1 -->

## Time at Several Sizes to Learn How Build Time Grows

One size tells you how long a build takes. Two or more tell you how the time grows, which is what
decides whether next year's portfolio will still build. If the time is proportional to $`n^a`$ for
$`n`$ projects, then $`a`$ is the **growth exponent**: doubling $`n`$ multiplies the time by
$`2^a`$, so 2 for a linear builder ($`a = 1`$) and 4 for a quadratic one ($`a = 2`$). Taking
logarithms, $`\log t = a \log n + \text{const}`$, a straight line whose slope is $`a`$.
`growth.py` fits that slope by least squares over every size it measured:

```python
def exponent(sizes: tuple[int, ...], seconds: list[float]) -> float:
    """The slope of log(time) against log(n), fitted by least squares over every size."""
    xs, ys = [math.log(n) for n in sizes], [math.log(s) for s in seconds]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
```

It times three builders on the first 1,250, 2,500, 5,000 and 10,000 projects of GridCap large (a
child's parent is always the project just before it, so a prefix cuts no parent off):

- `build_loops`, lesson 6.4.2's builder, looping over GridCap's project objects;
- `build_slow`, the first builder a team typically writes when its data arrives as pandas
  DataFrames: it walks the tables with `iterrows` and finds each project's rows with a boolean
  mask, `starts[starts.project_id == pid]`, which compares every row of the table each time;
- `build_matrix`, the builder lesson 11.1.2 develops.

`build_slow` is the one to look at:

```python
    def starts_of(pid: str) -> list[int]:
        return [int(s) for s in t.starts[t.starts.project_id == pid]["start"]]    # scans every start row
```

A mask over a table of $`n`$ rows, done once per project, is $`n \times n`$ comparisons: quadratic
work hidden in one readable line. Before any clock, the program counts that work, because counts
repeat exactly:

```text
n= 1,250:  2,721 start rows,  2,052 cost rows; slow builder's masks compare 9,775,068 rows
n= 2,500:  5,415 start rows,  4,056 cost rows; slow builder's masks compare 38,802,340 rows (3.97x the size before)
n= 5,000: 10,890 start rows,  8,140 cost rows; slow builder's masks compare 155,999,100 rows (4.02x the size before)
n=10,000: 21,843 start rows, 16,311 cost rows; slow builder's masks compare 623,905,057 rows (4.00x the size before)
```

Every doubling of the portfolio quadruples the rows the masks compare. Then the clock, from one run
on the author's machine:

<!-- unverified -->
```text
measured (median seconds at n = 1,250, 2,500, 5,000, 10,000; fitted exponent):
slow     3.136    9.917   23.196   56.832   exponent 1.4
loops    0.127    0.233    0.734    1.018   exponent 1.1
matrix   0.048    0.051    0.139    0.137   exponent 0.6
```

The rows compared quadrupled at every doubling, yet the slow builder's time grew with an exponent
of 1.4, not 2. Both are true, and the gap between them is the lesson:

- **A count of work is not a time.** Comparing one row inside a mask is a tight loop in compiled
  code and costs almost nothing; what costs is everything around it, the hundreds of microseconds
  pandas spends setting up each operation and each `iterrows` row. That part grows linearly. The
  quadratic part is still small at 1,250 projects and grows four times per doubling, so the fitted
  exponent sits between 1 and 2 and climbs as $`n`$ grows. At the next portfolio size it would be
  the whole bill.
- **The loop builder is close to linear** (1.1): twice the projects, about twice the time.
- **The matrix builder hardly grows at all** (0.6) over this range, because most of its time is a
  fixed cost per pandas operation, paid once per build whatever the size.
- **The exponent is noisier than the counts.** An earlier run of the same program measured the slow
  builder at 3.97, 6.63, 19.42 and 42.96 seconds. Fit over several sizes, never two, and read the
  exponent to one digit.

The measured times disagree with a simple model of the code, and that is normal: measure the sizes
you will run, and use the counts to say why the times bend.

## A Profiler Names the Hot Spot, and Its Call Counts Repeat When Its Times Do Not

Knowing that a builder is slow does not say which line to fix. A **profiler** does: Python's
`cProfile` records every function call while it is switched on, and `pstats` reports, for each
function, how many times it was called (`ncalls`), the time spent in its own code (`tottime`) and
the time including everything it called (`cumtime`). `profile_build.py` profiles one slow build of
the first 2,500 projects:

```python
    profiler = cProfile.Profile()
    profiler.enable()
    build_slow(tables)
    profiler.disable()
    stats = pstats.Stats(profiler).stats        # (file, line, function) -> (calls, ..., cumulative time, ...)
```

A full report lists hundreds of pandas functions; the program picks out the ones that tell the
story. Their call counts come from the code and the data alone, so they are the same on every run:

```text
function                                      calls
the whole build                                   1
DataFrame.iterrows, one Series per row       33,049
row.column, reading a field by name         163,721
starts_of, a mask over every start row        3,040
column == value, computing each mask          8,606
df[mask], selecting each mask's rows          8,606
Model.add_linear_constraint                   2,924
Model.add_variable                            5,415
```

The times, from one run on the author's machine (cumulative, so a function's line includes the
functions it calls: `starts_of` contains some of the masks below it, and the shares do not add up
to 100%):

<!-- unverified -->
```text
measured (cumulative time, and its share of the whole build):
the whole build                             13.953s  100%
DataFrame.iterrows, one Series per row       3.272s   23%
row.column, reading a field by name          3.141s   23%
starts_of, a mask over every start row       2.384s   17%
column == value, computing each mask         3.188s   23%
df[mask], selecting each mask's rows         3.256s   23%
Model.add_linear_constraint                  0.394s    3%
Model.add_variable                           0.091s    1%
```

What the two tables say together:

- **The time is in pandas, not in MathOpt.** Adding 5,415 variables and 2,924 rows to the model
  costs a few percent. The rest is the builder reading its own data.
- **The counts name the cause.** 8,606 masks for 2,500 projects is more than three per project,
  each comparing a whole table. 33,049 `iterrows` rows each became a pandas `Series` (a one-row
  object pandas builds for every row it yields), and 163,721 field reads went through pandas'
  attribute lookup. pandas' own documentation says `iterrows` returns each row as a Series and
  points to `itertuples` as the faster way to walk a table.
- **The profiler inflates the times.** The same build of 2,500 projects took about 10 s without the
  profiler in the growth run above and about 14 s with it, because the profiler does extra work
  on every one of the millions of calls. Python's documentation of `cProfile` notes that this error
  accumulates in code that makes many calls. Read a profile for where time goes, as shares and
  counts, and measure speed without it.

The fix is not to make each mask faster. It is to stop asking the same question of a whole table
thousands of times: compute every coefficient for every row in a few operations on whole columns.
That is lesson 11.1.2.

<!-- practice 2 -->

## Summary

- **A run has phases, and each phase gets its own clock.** Data, build, hand-off and solve;
  `solve_stats.solve_time` is the solver's part, and the rest of `mathopt.solve` is the hand-off.
  On GridCap medium the solve was 94% of the run; on large the build was 15%, and twice the solve of
  the LP relaxation.
- **One timing is an anecdote: warm up, repeat, and report the median and range.** The same build
  measured 0.021 s and 0.037 s in two runs; ratios of builders timed side by side are what carry
  over. Tests check identical models, never times.
- **Time at several sizes to learn how build time grows.** The slope of $`\log t`$ against
  $`\log n`$ is the growth exponent; the slow builder's masks compare four times as many rows each
  time the portfolio doubles.
- **A profiler names the hot spot, and its call counts repeat when its times do not.** The slow
  builder spends its time in pandas lookups, not in MathOpt.

## Reference

| Measure | How | Repeats exactly? |
| --- | --- | --- |
| a phase's wall time | `time.perf_counter()` before and after | no |
| the solver's own time | `result.solve_stats.solve_time` (a `timedelta`) | no |
| hand-off | wall time of `mathopt.solve` minus `solve_time` | no |
| a timing you can report | `measure(work, repeats, warmup)`: median and range | no, but its ratios are steadier |
| growth exponent | slope of $`\log t`$ against $`\log n`$ over several sizes | roughly |
| work counts | `cProfile` `ncalls`; counting rows a loop touches | yes |
| model size | `get_num_variables()`, `get_num_linear_constraints()`, `linear_constraint_matrix_entries()` | yes |

| Speed-up of | If $`a`$ is | Doubling $`n`$ multiplies time by |
| --- | --- | --- |
| a linear builder | 1 | 2 |
| a quadratic builder | 2 | 4 |

**Further reading:** [MathOpt `solve.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/solve.py) (what `mathopt.solve` does: export the model to a proto, call the solver, parse the result); [MathOpt `result.proto` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/result.proto) (`SolveStatsProto.solve_time`: the solver's wall time, without the build); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (models are built apart from any solver and handed to one); [Python `time.perf_counter`](https://docs.python.org/3.14/library/time.html#time.perf_counter) (the clock, and why only differences of its readings mean anything); [The Python profilers, `cProfile` and `pstats`](https://docs.python.org/3.14/library/profile.html) (`enable`, `disable`, the `ncalls`, `tottime` and `cumtime` columns, and the timing error the profiler adds); [pandas `DataFrame.iterrows`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html) (each row comes back as a Series; `itertuples` is the faster alternative).

## Challenges

1. Run `phases.py` twice and compare the large build's share of the run. Which moves more between
   your two runs, the seconds or the share?
2. The large model at a 0.1% gap: predict whether the build's share grows or shrinks, then change
   `PARAMS` and measure.
3. `build_loops` writes each `once_i` row with Python's `sum`. Time it against a version that uses
   `mathopt.fast_sum` (lesson 4.2.1) on the large portfolio, five repeats each. Is the difference
   larger than the spread of either?

## Design Note: Report Times With Their Method, and Count What You Can

A time printed without its method is close to useless to the next reader: which machine, how many
repeats, warm or cold, median or best, what else was running. This module prints the method next to
every timing ("3 runs each; medians") and keeps timings in their own block, apart from the lines
that repeat. Where a quantity can be counted instead of timed (rows compared, functions called,
nonzeros built), the count goes in the test and the time goes in the report. Lesson 5.4.2 applies
the same rule to comparing solvers.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change. The timings you get are your machine's, and they will differ from the ones on this page.

**phases.py.** One planning run per size with a clock around each phase, then the large LP relaxation's build against its solve (*A Run Has Phases*). *Try:* Set the gap in `PARAMS` to 0.05. Before running, guess the build's share of the large run.

- Program: [phases.py](src/phases.py)

**stopwatch.py.** `measure` and `Timing`, and a cold build of the medium model against seven warm ones (*One Timing Is an Anecdote*). *Try:* Run it three times in a row and write down the three medians. How far apart are they, as a share of the smallest?

- Program: [stopwatch.py](src/stopwatch.py)

**growth.py.** Three builders on the first 1,250 to 10,000 projects of GridCap large: rows compared by the slow builder's masks, then median times and fitted exponents (*Time at Several Sizes*). *Try:* Add 625 to `SIZES`. Does the slow builder's exponent move toward 2 or away from it?

- Program: [growth.py](src/growth.py)

**profile_build.py.** `cProfile` around one slow build of 2,500 projects, with call counts apart from times (*A Profiler Names the Hot Spot*). *Try:* Add `("slow_builder.py", "<genexpr>")` to `WATCH` and predict its call count before running.

- Program: [profile_build.py](src/profile_build.py)

**loop_builder.py, slow_builder.py.** The reference builder from lesson 6.4.2, and the DataFrame builder this lesson profiles (lesson 11.1.2 explains the tables it reads).

- Library: [loop_builder.py](src/loop_builder.py)
- Library: [slow_builder.py](src/slow_builder.py)
