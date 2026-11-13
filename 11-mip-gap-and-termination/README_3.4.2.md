# 3.4.2 Stopping on Gap, Time, Nodes or Solution Count

GridCap's planning job is moving to a nightly schedule. Run to the end, the medium selection MILP
took HiGHS 13,930 nodes (lesson 3.4.1), and the large portfolio will take longer. The planners need a
plan on their desks at 6 a.m., and they have said what "good enough" means to them: a plan within
0.1% of the best, or within $100k of it, whichever comes first. The job needs rules that stop the
solver, and it needs to know afterwards which rule stopped it, because a plan proved within 0.1% and
a plan that merely ran out of time are not the same thing to hand a planner. GridCap is a fictional
utility, and its numbers are teaching data.

This lesson sets each kind of stopping rule on the same model, reads how each run ended, shows which
rules give the same answer every run, and checks which solvers accept which rules.

## The Model

The project-selection MILP of lesson 3.4.1, unchanged. Only the rules for stopping its solve change
in this lesson.

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years; $`M \subseteq P`$ the must-do
projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$ the child projects, each with a
parent $`p(c)`$.

**Parameters.** $`v_i`$, the NPV of project $`i`$ at its earliest start ($k); $`c_{i,y}`$, what
project $`i`$ spends in year $`y`$ ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is in the plan.

**Objective and constraints.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} v_i\, x_i \\
\text{s.t. }& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& \sum_{i \in g} x_i \le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
& x_c \le x_{p(c)} && \forall c \in C && \text{(needs}_c) \\
& \sum_{i \in P} c_{i,y}\, x_i \le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

On GridCap medium: 400 binary variables and 85 rows. Every run below is HiGHS through MathOpt in
OR-Tools 9.15 unless it says otherwise, and every number is what a program printed. Another solver,
version or machine can print different ones.

## A Solve Stops at the First Limit It Reaches

MathOpt's `SolveParameters` holds the stopping rules common to every solver. MathOpt passes each one
to the solver only if you set it:

| Parameter | Stops when | Type |
| --- | --- | --- |
| `relative_gap_tolerance` | the relative gap (lesson 3.4.1) is at most this | a fraction: `0.001` is 0.1% |
| `absolute_gap_tolerance` | the absolute gap is at most this | the objective's units ($k here) |
| `time_limit` | this much wall-clock time has passed | a `datetime.timedelta` |
| `node_limit` | this many branch-and-bound nodes are done | a whole number |
| `solution_limit` | this many plans have been found | a whole number, at least 1 |

Set several, and the solve stops at whichever is reached first. Left unset, a limit is off, and a gap
tolerance falls back to the solver's own default. So with none set, each solver still stops
somewhere: at the end of the search, or at a tolerance of its own. HiGHS's are documented as
options, `mip_rel_gap` $`= 10^{-4}`$ (0.01%) and `mip_abs_gap` $`= 10^{-6}`$; lesson 3.4.3 shows the
first at work.

`stopping.py` solves the model five times, each time with one rule:

```python
limits = {
    "relative gap 1%": mathopt.SolveParameters(relative_gap_tolerance=0.01),
    "relative gap 0.1%": mathopt.SolveParameters(relative_gap_tolerance=0.001),
    "absolute gap 100": mathopt.SolveParameters(absolute_gap_tolerance=100, relative_gap_tolerance=0.0),
    "100 nodes": mathopt.SolveParameters(node_limit=100, relative_gap_tolerance=0.0),
    "1 solution": mathopt.SolveParameters(solution_limit=1, relative_gap_tolerance=0.0),
}
```

The last three also set `relative_gap_tolerance=0.0`. Without it, HiGHS's own relative tolerance
would still be in force and could stop the run before the rule being shown; 0.0 switches it off by
asking for a gap of zero. For each run the program prints how it ended, the bracket and the nodes:

```text
limit              reason    limit hit incumbent     bound    gap  rel gap nodes
relative gap 1%    OPTIMAL   -           224,191   224,611    420   0.187%     1
relative gap 0.1%  OPTIMAL   -           224,315   224,538    223   0.099%     1
absolute gap 100   OPTIMAL   -           224,315   224,414     99   0.044%   471
100 nodes          FEASIBLE  NODE        224,315   224,552    237   0.106%   100
1 solution         FEASIBLE  SOLUTION    219,607   224,870  5,263   2.397%     0
```

`rel gap` is the absolute gap divided by the incumbent, as HiGHS divides.

## A Gap Stop Ends OPTIMAL; Every Other Limit Ends FEASIBLE or NO_SOLUTION_FOUND

The two columns `reason` and `limit hit` come from `result.termination`: `reason` is
`termination.reason`, and `limit hit` is `termination.limit`, printed as `-` when it is `None`.

Look at the first three rows. Each run stopped with a gap above zero, $420k, $223k and $99k, and each
says `OPTIMAL`. That is not a bug. MathOpt's documentation of both gap tolerances says the solver may
stop once the gap is within the tolerance *and return OPTIMAL*. So **`OPTIMAL` means "optimal within
the gap tolerances in force"**, not "the bound met the incumbent". The plan is proved to be within
the tolerance of the best, which is exactly what the planners asked for.

Every other stopping rule is a **limit**, and a limit stop ends with one of two reasons:

| `termination.reason` | Means | `termination.limit` |
| --- | --- | --- |
| `OPTIMAL` | the bracket is within the gap tolerances; the plan is proved good enough | `None` |
| `FEASIBLE` | a limit stopped the run, and it holds a plan, not proved within the tolerances | which limit: `TIME`, `NODE`, `SOLUTION`, ... |
| `NO_SOLUTION_FOUND` | a limit stopped the run before any plan was found | which limit |
| `INFEASIBLE` | the solver proved that no plan obeys every row | `None` |

The rows above show the first two: 100 nodes ends `FEASIBLE` with limit `NODE`, and one solution ends
`FEASIBLE` with limit `SOLUTION`. The full list of reasons is in lesson 1.1.3. The full list of
limits in OR-Tools 9.15 also has `ITERATION`, `MEMORY`, `OBJECTIVE`, `INTERRUPTED` and a few more,
and one value that says nothing:

```text
CP-SAT, 1 solution: FEASIBLE, limit UNDETERMINED
```

**`UNDETERMINED`** means the solver does not say which limit it hit; MathOpt's documentation warns
that some solvers cannot fill the field in. Here CP-SAT, OR-Tools' constraint solver (section 4),
stopped on its solution limit and reported it this way. So code that branches on
`termination.limit` must handle `UNDETERMINED`, and never assume that a `FEASIBLE` run ran out of
time.

The rule for reading a run, then, has two questions, in this order:

1. **Is there a plan?** `OPTIMAL` and `FEASIBLE` hold one; `NO_SOLUTION_FOUND` and `INFEASIBLE` do
   not. `result.has_primal_feasible_solution()` answers it directly.
2. **Is the answer settled?** `OPTIMAL` is settled (within the tolerances), and so is `INFEASIBLE`
   (a proof that no plan exists). `FEASIBLE` and `NO_SOLUTION_FOUND` are not: more time, nodes or
   solutions could change them. A dashboard that prints `FEASIBLE` next to a plan should also print
   the gap (lesson 3.4.1) and the limit that stopped it.

<!-- practice 1 -->

## Each Limit Answers a Different Question

Read the table again as five ways of saying "enough":

- **A relative gap** says "enough when no plan is better by more than this share". At 1% the run
  stopped after a single node, with a plan $193k below the optimum of $224,384k (lesson 3.4.1). At
  0.1% it also stopped at the first node, with a better plan and a gap of 0.099%. One tolerance
  serves every model size, which is why it is the rule most jobs set.
- **An absolute gap** says "enough when no plan is better by more than this amount", in money. A
  tolerance of $100k took 471 nodes and stopped at a gap of $99k. It is the rule to use when the
  planners think in money, and when the objective can be near zero, where a ratio means little.
- **A node limit** says "enough work". It bounds the effort, not the quality: after 100 nodes the
  gap is whatever it happens to be, here $237k. It is the rule for repeatable runs (next section).
- **A solution limit** says "any plan, fast". With a limit of one, HiGHS stopped before branching,
  with a plan $5,263k (2.4%) below its bound. Which plans a solver counts is its own choice: this run
  returned the 219,607 plan, the one on the `R` row of lesson 3.4.1's log, not the 41,050 plan on
  the first row of that log. MathOpt's documentation warns that a solution limit promises nothing
  about the objective value of the plans returned. Use it to check that a model has any plan at all,
  or to get a starting point quickly; never hand its plan over as an answer without its gap.
- **A time limit** says "enough waiting". How good the plan is when it fires depends on how far the
  search got in that time, which depends on the machine.

The program's last HiGHS run had a one-second time limit:

```text
1 second: FEASIBLE, limit TIME, has a plan: True
```

After one second, HiGHS was stopped holding a plan.

How far off a first plan can be depends on the model. The OR-Tools MathOpt sample
`time_indexed_scheduling.py` schedules jobs on one machine, each job taking one start time on a grid
of whole time steps, and minimizes the sum of the jobs' completion times. Adapted here with HiGHS:

**Sets.** $`I`$ the jobs; $`T = \{0, \dots, H - 1\}`$ the time steps, with $`H`$ the latest release
plus the total processing time. **Parameters.** $`p_i`$ the processing time and $`r_i`$ the release
time of job $`i`$. **Variables.** $`x_{i,t} \in \{0, 1\}`$: job $`i`$ starts at $`t`$, fixed at 0 for
$`t < r_i`$.

```math
\begin{aligned}
\min \;& \sum_{i \in I} \sum_{t \in T} (t + p_i)\, x_{i,t} \\
\text{s.t. }& \sum_{t \in T} x_{i,t} = 1 && \forall i \in I && \text{(start}_i) \\
& \sum_{i \in I} \sum_{s = t - p_i + 1}^{t} x_{i,s} \le 1 && \forall t \in T && \text{(machine}_t)
\end{aligned}
```

The machine row for time $`t`$ counts every job that would be running at $`t`$: one started in the
last $`p_i`$ steps (from $`s = \max(0, t - p_i + 1)`$). The program solves the sample's own
three-job test instance, then 15 random jobs, once to the end and once stopped at the first plan:

```python
report("to the end", solve_highs(model))
report("first plan only", solve_highs(model, mathopt.SolveParameters(solution_limit=1, relative_gap_tolerance=0.0)))
```

```text
the example's own test instance (3 jobs):
  to the end       OPTIMAL  limit -        plan    26  bound    26.0  gap     0 (0.0%)  nodes 1
15 random jobs, 4,410 binaries, minimize the sum of completion times:
  to the end       OPTIMAL  limit -        plan 1,117  bound 1,117.0  gap     0 (0.0%)  nodes 1
  first plan only  FEASIBLE limit SOLUTION plan 2,273  bound 1,109.0  gap 1,164 (51.2%)  nodes 0
```

The test instance gives 26, the value the sample's comments state. On the random jobs, the first
plan costs 2,273 against an optimum of 1,117, more than twice as much, and its gap says so: 1,164,
51.2% of the plan's value. For a minimization the bracket is the other way round, bound below and
plan above. The full solve needed only one node, and the first plan is one no planner should get.

The gap rules are the ones that say something about the plan; the limits only say how the run ended.
A nightly job usually sets one of each kind: a gap tolerance that the planners agreed to, and a time
limit as a safety net, so that a hard night still ends with whatever plan was found. When the safety
net fires, the result says `FEASIBLE` and `TIME`, and the job reports the gap with the plan.

<!-- practice 2 -->

## Time Limits Are Not Repeatable; Node and Solution Limits Are

A time limit stops the search wherever it has got to after so many seconds. The same model on a
faster machine, on a busier one, or next to another job gets further or less far in those seconds,
so a time-limited run cannot promise the same plan twice. MathOpt's documentation adds that the time
limit is not a hard limit: a solve may run slightly past it.

A node limit counts work, not seconds. `repeatable.py` runs the same 200-node solve twice:

```python
params = mathopt.SolveParameters(node_limit=200, relative_gap_tolerance=0.0)
first = solve_highs(sel.model, params)
second = solve_highs(sel.model, params)
```

```text
first:  NODE, incumbent 224,315, bound 224,552, nodes 200
second:  NODE, incumbent 224,315, bound 224,552, nodes 200
same plan: True
same solve_time: False
```

The two runs did the same work and stopped in the same place, with the same plan, though their clocks
read differently. MathOpt's documentation of `node_limit` says that for many solvers it can limit the
computation deterministically, sometimes only with further settings such as a single thread. HiGHS
here needed none. When another solver's node-limited runs differ, a single thread is the first
setting to try; lesson 4.2.4 covers what each solver accepts, and lesson 4.6.3 reproducible CP-SAT
runs.

Repeatability matters in three places: a test that checks a solve's output (this module's tests use
node limits and gap tolerances, never time limits), an audit that must reproduce last
quarter's plan from last quarter's data, and a bug report that someone else must be able to run.

## Solvers Accept Different Limits

MathOpt passes each parameter to the solver, and a solver that cannot honour one refuses the whole
solve. `support.py` asks each MILP solver for each stopping rule on the small portfolio and reports
whether the solve was accepted:

```text
relative_gap_tolerance
  HIGHS  accepted
  GSCIP  accepted
  CP_SAT accepted
absolute_gap_tolerance
  HIGHS  accepted
  GSCIP  accepted
  CP_SAT accepted
time_limit
  HIGHS  accepted
  GSCIP  accepted
  CP_SAT accepted
node_limit
  HIGHS  accepted
  GSCIP  accepted
  CP_SAT refused: The node_limit parameter is not supported for CP-SAT.
solution_limit=1
  HIGHS  accepted
  GSCIP  accepted
  CP_SAT accepted
solution_limit=3
  HIGHS  accepted
  GSCIP  accepted
  CP_SAT refused: The CP-SAT solver only supports value 1 for solution_limit, found: 3
objective_limit
  HIGHS  refused: objective_limit not supported for HiGHS solver on integer problems.
  GSCIP  refused: parameter objective_limit not supported for gSCIP.
  CP_SAT refused: The objective_limit parameter is not supported for CP-SAT.
best_bound_limit
  HIGHS  refused: best_bound_limit not supported for HiGHS solver on integer problems.
  GSCIP  refused: parameter best_bound_limit not supported for gSCIP.
  CP_SAT refused: The best_bound_limit parameter is not supported for CP-SAT.
cutoff_limit
  HIGHS  refused: cutoff_limit not supported for HiGHS
  GSCIP  accepted
  CP_SAT accepted
```

The five rules of this lesson work on HiGHS and SCIP. CP-SAT refuses a node limit, and its solution
limit can only be 1. The last three
rows are rules this lesson has not used, and they are rarely what a nightly job needs:
`objective_limit` stops as soon as a plan reaches a target value, `best_bound_limit` as soon as the
bound proves a value, and `cutoff_limit` gives up once no plan can reach a value. None of the three
solvers accepts the first two on a MILP in this version.

A refusal is an exception raised by `mathopt.solve`, not a result. In OR-Tools 9.15 that exception
hides its own message: a bug in the Python wrapper turns it into an `AttributeError` about a missing
`canonical_code`, and the solver's reason is only on the exception's `__context__`, as the HiGHS
refusal in lesson 3.3.1 printed. That is why
`support.py` reads it there:

```python
    except Exception as error:  # OR-Tools 9.15 raises AttributeError; the reason is on __context__
        reason = str(error.__context__ or error)
        return "refused: " + reason.split(" [")[0]
```

So stopping rules belong to a solver, not to a model. A job that can switch solvers builds its
`SolveParameters` per solver, and its tests solve once with each set.

## Summary

- **A solve stops at the first limit it reaches.** Gap tolerances, a time limit, a node limit and a
  solution limit can be combined.
- **A gap stop ends `OPTIMAL`.** `OPTIMAL` means within the tolerances in force, even with a gap
  above zero.
- **Every other limit ends `FEASIBLE` (a plan) or `NO_SOLUTION_FOUND` (none)**, with
  `termination.limit` saying which limit, or `UNDETERMINED` when the solver does not say.
- **Each limit answers a different question.** Gaps say how good the plan is; node, solution and
  time limits only say how much was done.
- **Time limits are not repeatable; node limits are**, on HiGHS here, and on many solvers with one
  thread.
- **Solvers accept different limits.** CP-SAT refuses a node limit and any solution limit but 1;
  none of the three takes `objective_limit` on a MILP.

## Reference

| `SolveParameters` | Example | Ends the run with |
| --- | --- | --- |
| `relative_gap_tolerance` | `0.001` (0.1%) | `OPTIMAL` |
| `absolute_gap_tolerance` | `100` (objective units) | `OPTIMAL` |
| `time_limit` | `datetime.timedelta(minutes=20)` | `FEASIBLE` or `NO_SOLUTION_FOUND`, limit `TIME` |
| `node_limit` | `10_000` | `FEASIBLE` or `NO_SOLUTION_FOUND`, limit `NODE` |
| `solution_limit` | `1` | `FEASIBLE`, limit `SOLUTION` |

| Reason | Plan? | Settled? |
| --- | --- | --- |
| `OPTIMAL` | yes | yes, within the gap tolerances |
| `FEASIBLE` | yes | no |
| `NO_SOLUTION_FOUND` | no | no |
| `INFEASIBLE` | no | yes: no plan exists |

| Solver (OR-Tools 9.15) | Refuses on a MILP |
| --- | --- |
| HiGHS | `objective_limit`, `best_bound_limit`, `cutoff_limit` |
| SCIP (`GSCIP`) | `objective_limit`, `best_bound_limit` |
| CP-SAT | `node_limit`, `solution_limit` above 1, `objective_limit`, `best_bound_limit` |

MathOpt's docstring for `solution_limit` names Gurobi and SCIP, and CP-SAT only with the value 1; the
HiGHS of OR-Tools 9.15 accepted it too, as `support.py` printed.

**Further reading:** [MathOpt `SolveParameters` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py) (every common stopping rule: `time_limit` is not a hard limit, `node_limit` can make a solve deterministic, `solution_limit` promises nothing about the plan's value, and the gap tolerances may end a solve `OPTIMAL`); [MathOpt `SolveResult`, `Termination` and `ObjectiveBounds` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (`TerminationReason` and `Limit`, including `UNDETERMINED` for a solver that cannot say which limit it hit); [MathOpt sample time_indexed_scheduling.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (the scheduling model of this lesson, which checks for `OPTIMAL` before reading its schedule); [MathOpt sample writing_seminar.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/writing_seminar.py) (a solve with a time limit that accepts `OPTIMAL` or `FEASIBLE` and then checks the values are whole); [MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (a plan is always present on `OPTIMAL` and `FEASIBLE`, and may be suboptimal on the second); [MathOpt parameter and result reference (OR-Tools)](https://developers.google.com/optimization/service/reference/rpc/google.research.optimization.v1/mathopt) (the termination reasons and limits, `CUTOFF` among them); [HiGHS option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`mip_rel_gap`, `mip_abs_gap`, `mip_max_nodes`, `time_limit` and `mip_max_improving_sols` on the HiGHS side).

## Challenges

1. A job sets `relative_gap_tolerance=0.001` and `time_limit` of 20 minutes. One night it reports
   `FEASIBLE`, limit `TIME`, gap 0.4%. What can you tell the planners about that night's plan, and
   what should the job do the next night?
2. Why does the "absolute gap 100" run take 471 nodes while the "relative gap 0.1%" run takes one,
   although 0.1% of $224,315k is $224k? Answer from the table before you check with a calculator.
3. A test asserts a solve's objective with a 10-second time limit and passes on your laptop. Name two
   ways it can fail on the build server, and the change that makes it repeatable.

## Design Note: Store the Stopping Rule With the Plan

A plan's value means little without the rules that stopped its run. Save the `SolveParameters` you
passed (tolerances and limits), `termination.reason`, `termination.limit` and both bounds next to
every plan the job produces. When someone asks why Tuesday's plan differs from Monday's, the first
question is whether both were settled, and that record answers it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**stopping.py.** The model solved once per stopping rule, then once with a one-second time limit and
once on CP-SAT with a solution limit (*A Solve Stops at the First Limit It Reaches*, *A Gap Stop Ends
OPTIMAL*, *Each Limit Answers a Different Question*). *Try:* Combine `relative_gap_tolerance=0.001`
and `absolute_gap_tolerance=100` in one run. Predict which rule stops it, from the table, before
running.

- Program: [stopping.py](src/stopping.py)

**repeatable.py.** The same node-limited run twice (*Time Limits Are Not Repeatable*). *Try:* Replace
the node limit with `time_limit=datetime.timedelta(seconds=2)` (and import `datetime`). Predict
whether "same plan" stays `True`, then run it a few times.

- Program: [repeatable.py](src/repeatable.py)

**support.py.** Each stopping rule offered to HiGHS, SCIP and CP-SAT (*Solvers Accept Different
Limits*). *Try:* Add `iteration_limit=1000` to the dictionary. Predict which solvers accept it.

- Program: [support.py](src/support.py)

**scheduling.py.** Adapted from the OR-Tools MathOpt sample `time_indexed_scheduling.py`: the
sample's test instance, then 15 random jobs solved to the end and stopped at the first plan (*Each
Limit Answers a Different Question*). *Try:* Use 20 jobs. Predict whether the first plan's gap is
above or below 51.2%.

- Program: [scheduling.py](src/scheduling.py)

**selection.py.** The model builder and the quiet HiGHS solve the programs share. It prints nothing.

- Library: [selection.py](src/selection.py)
