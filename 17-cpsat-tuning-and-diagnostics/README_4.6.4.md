# 4.6.4 Reading the CP-SAT Log

A GridCap planner reports that "the solver got stuck" on the medium portfolio: it ran out its limit
and the gap stayed above 4%. Stuck where? Finding plans, or proving that no better plan exists?
The status and the objective cannot say; the **log** can. CP-SAT can write a running account of
everything it does: the model it received, what presolve did to it, every new plan and every better
bound as they happen, and a final summary. This lesson turns the log on, captures it, and reads it
section by section, on GridCap small (where the search finishes) and GridCap medium (where it does
not).

GridCap is a fictional utility's portfolio; none of its numbers are real. The model is lesson
4.6.1's, unchanged (`cpsat_plan.build`). Every run here uses one worker, so the log's content repeats
from run to run (lesson 4.6.3); the times in it do not, so the programs replace every measured time
with `<time>`.

## log_search_progress Writes the Log, and log_callback Catches It

Logging is off by default. `solver.parameters.log_search_progress = True` turns it on; the
parameters proto calls it the main logging switch. By default the log goes to standard output.
In a service or a test you want it as data instead, and two more settings do that:
`log_to_stdout = False` keeps it off the screen, and `solver.log_callback` is a function CP-SAT calls
with each piece of the log:

```python
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.parameters.log_search_progress = True     # write the log ...
solver.parameters.log_to_stdout = False          # ... but not to the screen:
log: list[str] = []
solver.log_callback = log.append                 # every line comes here instead
status = solver.solve(plan.model)
```

A list's `append` is a perfectly good callback: after the solve, `log` holds the whole log. The
program then masks the times with two regular expressions, one for numbers followed by `s`, `ms`,
`us` or `ns` and one for `walltime:`, `usertime:` and `time:` fields:

```python
def mask(line: str) -> str:
    """The log line with every wall-clock measurement replaced by <time>."""
    return CLOCK.sub(r"\1: <time>", TIME.sub("<time>", line))
```

The log is long (about 300 lines for this 80-variable model), so the program prints it a section at
a time. The rest of the lesson reads those sections in order.

## The Header and Model Statistics Say What the Solver Was Given

```text
==== header
Starting CP-SAT solver v9.15.6755
Parameters: log_search_progress: true log_to_stdout: false num_workers: 1
```

The first line is the OR-Tools version, the first thing to check when two machines disagree (lesson
4.6.3). The second lists every parameter that is not at its default. If a setting you thought you
made is missing from this line, it never reached the solver.

```text
==== model as written
Initial optimization model '': (model_fingerprint: 0xd5bead22fc8fe2d0)
#Variables: 80 (#bools: 80 in objective) (80 primary variables)
  - 80 Booleans in [0,1]
#kLinear1: 15
#kLinear2: 18
#kLinear3: 14
#kLinearN: 21 (#terms: 240)
```

This is the model exactly as your code built it, before CP-SAT changed anything:

- The **fingerprint** is a hash of the model. Two runs with the same fingerprint solved the same
  model; a changed fingerprint means the model changed, even if nobody meant to change it.
- **80 variables, all Booleans in [0,1], all in the objective**: the 80 start variables of GridCap
  small (one per project and allowed start year), each worth its NPV. Lesson 6.4.1, later in the
  course, builds such start-year variables in depth. A count you did not expect is a
  modeling bug found before any solving.
- **The constraint counts** are grouped by kind. `kLinear1`, `kLinear2` and `kLinear3` are linear
  constraints with one, two and three terms; `kLinearN` are the longer ones (21 of them, 240 terms
  in all). They add up to 68 rows: 40 once rows, 4 must-do, 2 alternative groups, 2 precedence,
  5 budgets and 15 crew rows (lesson 4.6.1's model). The long ones include the budget and crew
  rows, which sum over many projects; a one-term row is, for example, the once row of a project
  with a single start year.

Then comes presolve, many lines long, each line one presolve step with its time and its effect.
At its end is the **presolve summary**, one line per rule that fired and how often. Three of them
are about variables:

```text
==== presolve summary, the lines about variables
  - 1 affine relations were detected.
  - rule 'linear: remapped using affine relations' was applied 2 times.
  - rule 'presolve: 13 unused variables removed.' was applied 1 time.
```

An **affine relation** is a variable that presolve found to be a fixed linear function of another
($`a = 1 - b`$, for example), so one of the two can go. The 13 **unused variables** are ones
presolve could take out of the search entirely; their values are filled back in after the solve.
The model after presolve shows the result:

```text
==== model after presolve
Presolved optimization model '': (model_fingerprint: 0x8d7b36b0f6d51c74)
#Variables: 66 (#bools: 65 in objective) (65 primary variables)
  - 66 Booleans in [0,1]
#kAtMostOne: 13 (#literals: 44)
#kBoolAnd: 20 (#enforced: 20) (#literals: 40)
#kBoolOr: 3 (#literals: 11)
#kExactlyOne: 1 (#literals: 3)
#kLinearN: 14 (#enforced: 1) (#terms: 184)
```

80 variables became 66, and the 68 linear rows became 51 constraints of new kinds. Presolve
recognized that many small linear rows over Booleans are really logic: an **at-most-one**
(no more than one of these literals is true, which is what a once row or an alternative group
says), a **bool_and** with an enforcement literal (if this is true, those are all true), a
**bool_or** (at least one is true), an **exactly-one**. These are clauses that CP-SAT's Boolean
(SAT) engine handles directly. What is left as `kLinearN` are 14 rows that remain true sums.

Comparing the two blocks is the quickest test of a model's shape. A presolve that removes most of
a model means much of it was decided by the data; a presolve that removes nothing on a model full
of logic means the logic was written in a form presolve could not read.

<!-- practice 1 -->

## Each Progress Line Is an Event: a New Plan or a Better Bound

After presolve, the search. Each line starting with `#` reports one event, with the same layout:
the event, the time, `best:` the value of the best plan so far, `next:[low,high]` the range of
objective values still in play, and the worker that caused it.

```text
==== search
Preloading model.
#Bound   <time> best:-inf  next:[1827,64284] initial_domain
Starting search at <time> with 1 workers.
1 full problem subsolver: [main]
#Bound   <time> best:-inf  next:[1827,27576] main (initial_propagation)
#1       <time> best:20625 next:[20626,27576] main
#Bound   <time> best:20625 next:[20626,27038] main
#2       <time> best:20646 next:[20647,27038] main
#Bound   <time> best:20646 next:[20647,26316] main
#3       <time> best:20822 next:[20823,26316] main
#Bound   <time> best:20822 next:[20823,26215] main
#Bound   <time> best:20822 next:[20823,26177] main
#4       <time> best:20880 next:[20881,26177] main
#5       <time> best:21383 next:[21384,26177] main
#6       <time> best:21444 next:[21445,26177] main
#Bound   <time> best:21444 next:[21445,26171] main
#7       <time> best:21494 next:[21495,26171] main
#Bound   <time> best:21494 next:[21495,26152] main
#Bound   <time> best:21494 next:[21495,26147] main
#8       <time> best:21749 next:[21750,26147] main
#9       <time> best:21862 next:[21863,26147] main
#10      <time> best:22485 next:[22486,26147] main
#11      <time> best:22571 next:[22572,26147] main
#12      <time> best:22637 next:[22638,26147] main
#Bound   <time> best:22637 next:[22638,25592] main
#13      <time> best:22713 next:[22714,25592] main
#Bound   <time> best:22713 next:[22714,25528] main
#14      <time> best:22720 next:[22721,25528] main
#Bound   <time> best:22720 next:[22721,25448] main
#Bound   <time> best:22720 next:[22721,25422] main
#15      <time> best:22741 next:[22742,25422] main
#Bound   <time> best:22741 next:[22742,25418] main
#Done    <time> main
```

The four kinds of line:

- **`#1`, `#2`, ...** a new, better plan. `best:` jumps to its value, and the low end of `next:`
  moves to one more than it: for a maximization with an integer objective, the next plan worth
  finding must be worth at least best + 1.
- **`#Bound`** a better bound. The high end of `next:` falls: no plan is worth more than this.
  The first one, from `initial_domain`, is the bound from the variables' domains alone ($64,284k);
  the next, after `initial_propagation`, is already less than half of it.
- **`#Done`** the search finished: it proved that no plan in the remaining range exists, so the
  best plan is optimal. The last `#Bound` line still says 25,418; the proof that closed the range
  came as the search ended, which is why the summary below reports a bound of 22,741.
- **`#Model`** (not in this run) reports that the model shrank during the search, for example as
  variables became fixed.

The last word on each line is the subsolver that caused the event. With one worker it is always
`main`; with several, it is one of the names in lesson 4.6.1's lists, which tells you which part of
the portfolio found each plan and each bound (the CP-SAT Primer reads this column the same way).

Now the medium run that "got stuck", one worker and 3 units of deterministic time. Its log is
hundreds of lines, so the program reads its progress lines as data and summarizes them:

```python
EVENT = re.compile(r"^#(\d+|Bound|Done|Model)\s+(\S+)\s*(.*)$")
RANGE = re.compile(r"best:(\S+)\s+next:\[(\S+),(\S+)\]\s*(\S*)")
```

```text
17 solution lines, 23 bound lines, last event: solution
plans: first 208873, last 215024
bound: from the domains 570140, at the first plan 225336, at the end 224292
response: objective 215,024, best_bound 224,292
```

Three readings answer the planner:

1. **No `#Done` line**: the last event is a plan, so the limit stopped the search, not a proof.
2. **The plan side moved**: from $208,873k to $215,024k across 17 plans, $6,151k in all.
3. **The bound side barely moved**: after the first plan it fell only from $225,336k to $224,292k,
   $1,044k.

So the search was not stuck finding plans; it was stuck *proving*. Where the bound starts says nothing about presolve: presolve's work is
read in its own summary lines before the search, not in the first `#Bound`. The CP-SAT Primer reads the log
the same way: improving plans with a flat bound point to a weak bound, while a flat plan with a
moving bound means the solver is busy with the proof. Lesson 4.6.1 gave the remedy for this case:
more workers bring subsolvers such as `max_lp` and `core` that raise the bound, and the 8-worker run
closed the gap below 1%.

<!-- practice 2 -->

## The Response Summary Is the Run's Final Word

Between the search and the summary, the log prints tables of statistics per subsolver: timing,
search counts, clauses, LP sizes and cuts. The CP-SAT Primer notes that they are mainly for CP-SAT's
developers. The last block is for you:

```text
==== response
CpSolverResponse summary:
status: OPTIMAL
objective: 22741
best_bound: 22741
integers: 68
booleans: 66
conflicts: 102
branches: 3731
propagations: 8941
integer_propagations: 14273
restarts: 1
lp_iterations: 3053
walltime: <time>
usertime: <time>
deterministic_time: 0.0546806
gap_integral: 0
solution_fingerprint: 0xc4a7abf151f083c
```

| Field | Meaning |
| --- | --- |
| `status` | `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `MODEL_INVALID` or `UNKNOWN` |
| `objective`, `best_bound` | the best plan's value and the proven bound; equal here, so the gap is 0 |
| `booleans`, `integers` | the variables the search worked with (after presolve: 66 Booleans) |
| `conflicts`, `branches` | how many times the search hit a contradiction, and how many decisions it made |
| `propagations`, `integer_propagations` | how many deductions propagation made |
| `restarts`, `lp_iterations` | search restarts, and simplex iterations of the LP relaxation |
| `walltime`, `usertime` | seconds on the clock (masked here, since they never repeat) |
| `deterministic_time` | the work done, in the unit of lesson 4.6.3 |
| `gap_integral` | the gap integrated over time: smaller means the gap closed sooner |
| `solution_fingerprint` | a hash of the plan: equal fingerprints mean the same plan; two different plans can tie on the objective and still have different fingerprints |

Why 68 integers next to 66 Booleans, in a model whose variables are all Booleans? The proto
(`cp_model.proto`, `CpSolverResponse`) lists `num_integers` and `num_booleans` without saying how
they are counted, so `variable_counts.py` measures it on five Booleans, with presolve off so that
the counts are the model's own:

```python
model.add_bool_or(x)
if row:
    model.add(sum((i + 2) * v for i, v in enumerate(x)) <= 9)
if objective:
    model.maximize(sum((i + 3) * v for i, v in enumerate(x)))
```

```text
5 Booleans, one clause             booleans 5  integers 0
+ a weighted linear row            booleans 5  integers 5
+ a weighted objective             booleans 5  integers 6
```

The two counts are not disjoint. A Boolean that only appears in clauses is counted once, as a
Boolean. A Boolean that appears in a weighted linear row is also given an integer form for that row,
so it is counted in both; and a weighted objective adds one more integer variable, its value. So
`integers` is not a count of the integer variables you created: in the GridCap run the Booleans
sit in budget and crew rows, so they are counted again as integers, and the solver's extra integer
variables (of the kind the objective adds above) bring the count above 66.

Every field is also on the solver object, so code never has to parse this text:

```text
==== the same numbers from the solver object
status OPTIMAL, objective 22,741, bound 22,741, branches 3,731, conflicts 102
solver.response_stats() starts with: CpSolverResponse summary:
```

`solver.status_name(status)`, `solver.objective_value`, `solver.best_objective_bound`,
`solver.num_branches`, `solver.num_conflicts`, `solver.wall_time` and `solver.deterministic_time`
give the numbers, and `solver.response_stats()` returns the summary block as a string, which is
the thing to write to a service's own log after every solve. When the full log is too much to
keep, keep this block and the version line: together they say what ran and what came out.

<!-- practice 3 -->

## Summary

- **`log_search_progress` writes the log, and `log_callback` catches it.** Set `log_to_stdout =
  False` and collect the lines; mask the times before comparing logs.
- **The header and model statistics say what the solver was given.** Check the version, the
  parameters line, the fingerprint and the variable counts; compare the model before and after
  presolve.
- **Each progress line is an event: a new plan or a better bound.** A missing `#Done` means a limit
  stopped the run; which side moved tells you whether the search lacked plans or a proof.
- **The response summary is the run's final word.** Keep `response_stats()` with every solve.

## Reference

| Log section | Starts with | Read it for |
| --- | --- | --- |
| header | `Starting CP-SAT solver` | version and non-default parameters |
| model as written | `Initial optimization model` | variable and constraint counts, fingerprint |
| presolve | `Starting presolve`, `Presolve summary:` | which simplifications fired |
| model after presolve | `Presolved optimization model` | what the search actually works on |
| search | `Starting search`, `#1`, `#Bound`, `#Done` | plans and bounds over time, and who found them |
| statistics | `Task timing`, `Search stats`, ... | per-subsolver detail (mostly for developers) |
| summary | `CpSolverResponse summary:` | the final status and numbers |

| Setting or call | What it does |
| --- | --- |
| `solver.parameters.log_search_progress = True` | write the log |
| `solver.parameters.log_to_stdout = False` | keep it off standard output |
| `solver.log_callback = f` | call `f` with each part of the log |
| `solver.parameters.log_subsolver_statistics = True` | per-subsolver statistics, with several workers |
| `solver.response_stats()` | the summary block as a string |

**Further reading:** [CP-SAT troubleshooting: logging](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md),
[CP-SAT model proto, `cp_model.proto`](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto)
(`CpSolverResponse` statistics),
[CP-SAT parameters proto](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`log_search_progress`, `log_to_stdout`, `log_subsolver_statistics`),
[CP-SAT solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver) (statuses), and
[The CP-SAT Primer: Understanding the Log](https://d-krupke.github.io/cpsat-primer/understanding_the_log.html).

## Challenges

1. Run `read_log.py` with `cp_model_presolve = False`. What does the log print where the presolve
   summary was, and how many variables does the search work with?
2. Change `log_events.py` to count, for GridCap medium with 8 workers, how many plans each
   subsolver found. Run it twice. Do the counts repeat?
3. Write a function that returns `True` when a log's last plan came more than half the work
   budget before the end. What would it tell a planner?

## Design Note: Logs Are for People, Fields Are for Code

The log is the best tool for understanding one run and a poor interface for programs: its layout is
not part of any API, and a new OR-Tools version may change it. Code that decides things (stop,
alert, retry) should read the fields on the solver object, and the log should be stored for the
person who will investigate. The practices of this lesson parse log text because archived logs are
often all that is left of an old run; for new runs, prefer `solver.objective_value` and its
siblings.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**read_log.py.** Captures the log of the GridCap small solve, masks its times and prints it section
by section (*log_search_progress Writes the Log, and log_callback Catches It* to *The Response
Summary Is the Run's Final Word*). *Try:* Print the `Search stats` table too. Which of its numbers
also appear in the summary?

- Program: [read_log.py](src/read_log.py)

**log_events.py.** Reads the progress lines of a stopped GridCap medium solve as events and
summarizes them (*Each Progress Line Is an Event: a New Plan or a Better Bound*). *Try:* Raise the
limit to 6 units. Predict which of the three summary lines changes most.

- Program: [log_events.py](src/log_events.py)

**variable_counts.py.** Five Booleans in a clause, then in a weighted row, then with a weighted
objective, printing the response's `booleans` and `integers` (*The Response Summary Is the Run's
Final Word*). *Try:* Make the row's coefficients all 1. Predict whether `integers` changes.

- Program: [variable_counts.py](src/variable_counts.py)
