# 4.6.3 Deterministic Time, Seeds and Reproducible Runs

An auditor at GridCap's regulator reruns last quarter's plan with the same data and the same code,
and gets a different plan. Nothing was wrong with either plan; both kept every rule. But "the model
gives a different answer each time you ask" is a finding no planning team wants, and it makes every
regression test flaky. This lesson finds out, by running each setting several times, exactly which
numbers repeat and which do not, and builds the settings that make a CP-SAT run repeat.

GridCap is a fictional utility's portfolio; none of its numbers are real. The model is lesson
4.6.1's, unchanged (`cpsat_plan.build`), solved on GridCap medium, where CP-SAT stops at a limit
before proving optimality. That is where reproducibility is hard: a run that proves the optimum ends
at the same objective whatever path it took, while a run stopped early ends wherever the limit
caught it.

## One Worker, a Fixed Seed and a Deterministic Limit Repeat Every Number but the Clock

Three settings decide whether a run can repeat:

- `num_workers`, the number of threads (lesson 4.6.1). With one, there is a single search, a
  single sequence of decisions.
- `random_seed`, the seed of the solver's random number generator. The parameters proto says it is
  reset at the start of each solve, so the same seed gives the same sequence of random choices.
  The default is 1.
- The limit. `max_deterministic_time` stops the search after a fixed amount of **deterministic
  time**: CP-SAT's own estimate of the work it has done, computed from what the search did rather
  than read from a clock. The proto says the unit is meant to be close to a second, but it is a
  measure of work, so the same search reaches the same count at the same point however busy the
  machine is.

The program solves the same model several times with each setting. For every quantity it prints
the value if all runs gave the same one, and `differs` if they did not:

```python
def report(label: str, params: dict, runs: int, keys: list[str]) -> None:
    results = [run(params) for _ in range(runs)]
    print(f"{label} ({runs} runs)")
    for key in keys:
        values = {r[key] for r in results}
        print(f"  {key:<19} {values.pop() if len(values) == 1 else 'differs'}")
```

The `plan` row is a fingerprint of the plan: the first 12 hex digits of a SHA-256 hash of the
sorted list of (project, start year) pairs, so two equal fingerprints mean the same plan.

```text
1 worker, seed 7, deterministic limit 3 (3 runs)
  status              FEASIBLE
  objective           214,973
  bound               224,290
  branches            73,294
  deterministic time  3.0001
  plan                bac9492e8b17
  wall time           differs
```

Everything the search produced repeats: the plan, its value, the bound, the number of branches
(decisions the search made), even the deterministic time to four decimals. Only the wall time, the
seconds on the clock, differs, as it must: the same work takes longer on a busy machine.

This is the recipe for an auditable run on one OR-Tools version:

```python
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.parameters.random_seed = seed
if work is not None:
    solver.parameters.max_deterministic_time = work
```

Everything here was measured on OR-Tools 9.15. Another version may presolve or search
differently, so record the version with the seed and the limit, and treat an upgrade as a change
that needs its own check.

<!-- practice 1 -->

## A Wall-Clock Limit Stops the Search at a Different Point Each Run

`max_time_in_seconds` stops the search when the clock says so. The same one-worker, seed-7 run with
a 2-second limit instead:

```text
1 worker, seed 7, time limit 2 s (3 runs)
  branches            differs
  deterministic time  differs
  wall time           differs
```

The search itself is the same sequence of decisions every time (one worker, same seed), but the
clock stops it after a different number of them, because how many decisions fit in 2 seconds
depends on what else the machine is doing. Any number taken at the moment of stopping (the plan,
its value, the bound) is then the number at a different point of the search. On some runs those
may happen to agree, since the plan does not change at every branch; nothing makes them agree.

A time limit is still the right tool when a planner is waiting: it bounds the wait. The two limits
answer different questions. "Give me the best plan you can find in 60 seconds" is a time limit;
"give me the same plan every time" is a work limit. A service can set both, and then must record
which one stopped the run.

<!-- practice 2 -->

## Parallel Workers Race, So Their Plan Can Change Between Runs

Eight workers with the same seed and the same deterministic limit:

```text
8 workers, seed 7, deterministic limit 3 (4 runs)
  objective           differs
  plan                differs
  wall time           differs
```

Each subsolver of the portfolio (lesson 4.6.1) is itself deterministic, but they run on separate
threads at speeds the operating system decides, and they share plans and bounds as they find them.
Which subsolver's plan arrives first, and so what the others build on, changes from run to run.
The deterministic limit does not help: whatever amount of work each worker is allowed, the plans
it received from the others along the way were different.

The parameters proto offers a way out, marked experimental: `interleave_search`. In this mode the
subsolvers do not race; their tasks run in batches, and the next batch starts only when the current
one has finished (`interleave_batch_size` sets the batch size). The proto describes the search as
deterministic whatever `num_workers` is:

```text
8 workers, interleaved, seed 7, deterministic limit 3 (3 runs)
  status              FEASIBLE
  objective           219,156
  bound               219,779
  branches            26,723
  deterministic time  8.0674
  plan                3799c27d21e2
  wall time           differs
```

Every number repeats again, and the plan ($219,156k, bound $219,779k) is far better than the
one-worker plan above ($214,973k, bound $224,290k): the portfolio's strength without the race. Note
the deterministic time: 8.0674 against a limit of 3. In this run the limit stopped the search well
after the 3 units, which fits the batch design (a batch runs to its end before the next one is
considered), so treat the limit in this mode as approximate and choose it by measuring.

Two cautions before relying on it. The proto calls the mode experimental, so check it again on each
new OR-Tools version. And the proto's promise is about the search; it says nothing about the log
(lesson 4.6.4), so compare results, not logs.

## A Seed Changes the Path, Never What Is Proven Optimal

Changing the seed changes the random choices, and so the path the search takes. What that does to
the answer depends on whether the search finishes:

```text
medium, deterministic limit 3
  seed 1: FEASIBLE plan $215,024k  branches 72,117  plan 21cd63c641a3
  seed 2: FEASIBLE plan $215,492k  branches 70,488  plan 0d37df1473d8
  seed 3: FEASIBLE plan $215,060k  branches 69,717  plan b2de677ca612
small, no limit
  seed 1: OPTIMAL  plan $22,741k  branches  3,731  plan 87e390ff0917
  seed 2: OPTIMAL  plan $22,741k  branches  4,625  plan 87e390ff0917
  seed 3: OPTIMAL  plan $22,741k  branches  3,245  plan 87e390ff0917
```

On GridCap medium, stopped by the limit, each seed ends at a different plan: three paths, each cut
off at the same amount of work at a different place. On GridCap small, where the search finishes,
the three seeds take paths of different lengths (3,731, 4,625 and 3,245 branches) and all prove the
same optimum, $22,741k. A proof of optimality does not depend on the path. Here all three also
returned the same plan; on a model with several optimal plans, different seeds may return
different ones, all with the optimal value.

So a seed is not a tuning knob to keep searching for a lucky number. It is a label that makes a
run repeatable. Two practical uses follow. Benchmark a setting over several seeds, not one, because
a single seed's result (here anywhere from $215,024k to $215,492k) is partly luck. And when a test
must pin a plan, pin the seed along with the worker count and the work limit.

## Summary

- **One worker, a fixed seed and a deterministic limit repeat every number but the clock.** Status,
  plan, objective, bound, branches and deterministic time all repeat on one OR-Tools version.
- **A wall-clock limit stops the search at a different point each run.** Use it to bound a
  planner's wait, not to reproduce a plan.
- **Parallel workers race, so their plan can change between runs.** `interleave_search` (experimental)
  made eight workers repeat in our runs, overshooting its deterministic limit.
- **A seed changes the path, never what is proven optimal.** Benchmark over several seeds; pin the
  seed to make a run repeatable.

## Reference

| Setting | Repeats run to run? (OR-Tools 9.15, our runs) |
| --- | --- |
| `num_workers = 1`, `random_seed`, `max_deterministic_time` | yes: every number except wall time |
| `num_workers = 1`, `random_seed`, `max_time_in_seconds` | no: branches and deterministic time differ |
| `num_workers = 8`, `random_seed`, `max_deterministic_time` | no: plan and objective differ |
| `num_workers = 8`, `interleave_search = True`, `random_seed`, `max_deterministic_time` | yes: every number except wall time |

| Quantity | Read it with |
| --- | --- |
| deterministic time used | `solver.deterministic_time` |
| wall time used | `solver.wall_time` |
| branches, conflicts | `solver.num_branches`, `solver.num_conflicts` |
| bound | `solver.best_objective_bound` |

**Further reading:** [CP-SAT parameters proto](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`random_seed`, `max_deterministic_time`, `max_time_in_seconds`, `num_workers`, `interleave_search`,
`interleave_batch_size`),
[Setting solver limits (OR-Tools)](https://developers.google.com/optimization/cp/cp_tasks) and the
sample [`solve_with_time_limit_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/solve_with_time_limit_sample_sat.py),
[CP-SAT solver docs](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/solver.md)
(changing parameters, time limits).

## Challenges

1. Add `"num_conflicts"` to the quantities `repeat_runs.py` compares. Predict for which settings it
   repeats.
2. Run the 8-worker interleaved setting with 4 workers. Does the plan repeat? Is it the same plan as
   with 8?
3. Find the smallest deterministic limit at which seed 2 on GridCap medium beats seed 1's plan at
   a limit of 3.

## Design Note: What to Store With a Plan

A plan that must be reproduced later is stored with everything its run depended on: the input
data (or its hash: `Portfolio.content_hash()` for GridCap), the code version, the OR-Tools version,
and the solver settings (`num_workers`, `random_seed`, the limit and its kind). Store the result's
repeatable fields too, so a rerun can be compared field by field: status, objective, bound, the
plan's fingerprint and the deterministic time. Never store the wall time as part of the result; it
is a fact about the machine, not about the plan.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**repeat_runs.py.** Solves GridCap medium several times under four settings and prints which
quantities repeated (*One Worker, a Fixed Seed and a Deterministic Limit Repeat Every Number but
the Clock*, *A Wall-Clock Limit Stops the Search at a Different Point Each Run* and *Parallel
Workers Race, So Their Plan Can Change Between Runs*). *Try:* Print every key for the time-limited
setting. Which ones repeated on your run, and would they repeat on a busier machine?

- Program: [repeat_runs.py](src/repeat_runs.py)

**seeds.py.** Three seeds on a model stopped by a limit and on one solved to the end (*A Seed
Changes the Path, Never What Is Proven Optimal*). *Try:* Add seeds 4 to 10 for GridCap medium.
How wide is the range of plans?

- Program: [seeds.py](src/seeds.py)
