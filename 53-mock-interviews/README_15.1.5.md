# 15.1.5 Mock 5: Production, Trust and Performance

A plan that regulators rely on must come out the same every time, run as a service, pass tests that
can fail, and finish inside the planners' window. This round is the engineering half of the job:
determinism, snapshots, tests, the API, the cloud, speed and the GPU. The interviewer's service is fictional,
like GridCap, and every number quoted below comes from a course program.

| Part | Minutes |
| --- | --- |
| Round 1: trust, three questions | 6 |
| Code practice: a snapshot digest | 5 |
| Round 2: service and speed, three questions | 5 |
| Round 3: the GPU, two questions | 4 |
| Trap questions | 6 |
| Whiteboard and its code practice | 10 |

## Round 1: A Run Repeats Only Relative to Everything It Read

**Q1. The same scenario gave two different plans on two runs. Where do you look?**

<details>
<summary>Model answer</summary>

A run repeats only relative to everything it read: the data, the model's build order, the solver and
its version, the parameters and the machine. Three causes cover most cases. Parallel workers race,
so their plan can change between runs (four CP-SAT workers under a deterministic limit did not give
one plan in five runs). A clock limit stops the search wherever the clock says; a node limit or a
deterministic-time limit repeats. Ties: when several plans are optimal, input order picks the winner,
and Python salts string hashes per process, so a model built in set order returned a different tied
plan in each process. Compare reruns in fresh processes, each with its own hash seed, and compare
whole manifests, not only the objective.

*Follow-ups.* "Settings per solver?" HiGHS: a seed, a thread count fixed per process, a node limit.
CP-SAT: one worker, a seed and a deterministic limit repeat every number but the clock. Gurobi:
deterministic for a fixed thread count. "And ties?" A second real criterion solved in a second pass,
or small weights that repeat in every process and cannot outweigh a real difference.

*Taught in:* lesson 10.2.1; lesson 10.2.2; lesson 10.2.3; lesson 4.6.3.

</details>

**Q2. An auditor asks you to prove which inputs produced last year's locked plan.**

<details>
<summary>Model answer</summary>

Name the inputs by a content hash: validate the snapshot, write it in one canonical form (sorted
keys, unordered lists sorted, fixed separators, money in whole units, ASCII, no NaN) and take a
`hashlib` digest of the bytes; equal content gives equal digests in every process. Store each
snapshot once under its digest and re-hash it on every read, so a file edited in place is refused.
Keep a run manifest beside it: inputs, solver and parameters, pinned versions (the OR-Tools wheel
carries its own HiGHS, 1.12.0 in 9.15), and the result with its work counts, leaving out the clock
and anything naming the machine or a person. A rerun that matches is evidence, not a guarantee.

*Taught in:* lesson 10.2.4; lesson 12.2.3; lesson 10.2.5; lesson 7.1.3.

</details>

**Q3. How do you test an optimization model?**

<details>
<summary>Model answer</summary>

In layers, each catching what the others miss. Unit-test one rule at a time on a hand-made instance
where it alone can bind: fix a plan through the variables' bounds and ask the solver "allowed or
refused?", pairing every refused plan with an allowed one at the boundary (a whole-model test passed
with three of five broken rules on GridCap tiny). Property tests with Hypothesis check every plan
against a checker that reads only the data, on instances built around a known feasible plan. Golden
records compare a reviewed result field by field (status, plan and spend exactly, the objective
within $10), after checking the input hash. A determinism test reruns fresh processes and compares
bytes, and it must be able to fail: keep a known-bad case and assert that it does.

*Taught in:* lesson 12.3.1; lesson 12.3.2; lesson 12.3.3; lesson 12.3.4.

</details>

Before any hash can name a snapshot, the snapshot needs one canonical form. The first code practice
writes it.

<!-- practice 1 -->

## Round 2: A Solve Is a Job, and Speed Is Measured

**Q4. A solve takes twenty minutes. Design the API.**

<details>
<summary>Model answer</summary>

A long solve must not hold the request open: submit answers 202 and a job id, poll answers a status,
fetch answers the result (or 409 before it exists). A job store keeps each job's state and an
executor runs the solves; run them in a process pool, because a solver crash in a thread killed the
whole API process, while in a `ProcessPoolExecutor` it failed one job. Every way a solve ends gets
its own status: `optimal`, `time_limit` (with or without a plan), `infeasible` (proven only),
`failed`. An infeasible scenario is an answer, returned with 200, not an HTTP error; 4xx is for a bad
request. A blocking solve belongs in a `def` path, never `async def` (three one-second calls took
3 s under `async def`, 1 s under `def`). No plan is `null` in the result, never infinity.

*Taught in:* lesson 12.4.1; lesson 12.4.2; lesson 12.4.3.

</details>

**Q5. Where does each part run on AWS?**

<details>
<summary>Model answer</summary>

The API answers requests; S3 keeps snapshots and results, each snapshot under its digest and every
write conditional; AWS Batch on Fargate runs the solver container, with the job's timeout above the
solver's own limit; Step Functions waits for the job and catches failures; Lambda, at most 900 s,
does short glue and never the solve. In the course, a local SQLite file indexes the runs and S3 holds
their content. One image serves both the API and the worker, pins the solver, runs as a non-root
user and holds no credentials, and the solver is told how many CPUs the container has. AWS code is
tested against moto with fake credentials, remembering that moto accepts things AWS refuses.

*Taught in:* lesson 12.5.1; lesson 12.5.2; lesson 12.5.3; lesson 12.5.4.

</details>

**Q6. The ten-year model on the large portfolio misses its run window. What do you try, in order?**

<details>
<summary>Model answer</summary>

Measure first: time the data, build, hand-off and solve phases separately (on GridCap large the
build was 15% of the run); a slow builder is fixed by vectorizing, 300 times faster there. If the
solve dominates, compare formulations by their LP and root bounds and tighten (cumulative rows,
bounds from the data, valid inequalities, symmetry handling), then measure the solver's work. A MIP
start from last cycle's plan, mapped and repaired, is insurance for a run stopped early. Tune one
parameter at a time on held-out instances and several seeds; defaults won on GridCap. Decomposition
(Lagrangian, Benders, rolling horizon, LNS) is reported against the best bound known; on GridCap
medium LNS polished the solver's early plan to 0.027% of the proven optimum.

*Taught in:* lesson 11.1.1; lesson 11.1.2; lesson 6.7.4; lesson 11.2.1; lesson 11.2.2;
lesson 11.2.3; lesson 11.3.5.

</details>

## Round 3: A GPU Speeds Up Large LPs, and the Run Says Which Device Answered

Module 57 measured GPU solvers on one laptop card, an 8 GB laptop NVIDIA GPU whose driver reports
CUDA `13.2`, with HiGHS `1.14.0` built with CUDA and NVIDIA cuOpt `26.10`. The times depend on the
machine: another card gives other times, but the reasoning below does not change with the card.

**Q7. Finance wants the ten-year plan overnight, on GPUs. What would you move to the GPU, and what
not?**

<details>
<summary>Model answer</summary>

Start from what a GPU does well. PDLP, the first-order LP method built on PDHG, needs only products
of the constraint matrix with vectors, which a GPU computes in parallel, and it stops when its
errors fall below a tolerance rather than at an exact vertex. So large LPs gain: on a transportation
LP with 1M variables, HiGHS's interior point method took 10.3 s on the CPU, HiGHS's GPU PDLP 1.63 s
and cuOpt's PDLP 0.93 s of solver time, while OR-Tools' PDLP on the CPU took 11.2 s. The gain grows
with size: at 90,000 variables the first three took 0.55 s, 0.40 s and 0.19 s. A small LP gains
nothing, and the first solve in a process pays about 0.2 s of CUDA start-up. The ten-year plan is a
MILP, and on a cuOpt MILP the GPU runs only the feasibility-jump heuristic and PDLP inside the
concurrent root LP; presolve, cuts and branch-and-bound stay on the CPU. So measure first (Q6), move
the large LPs to the GPU, and keep the search that proves the plan on the CPU; a cuOpt MILP plan is
one more candidate, checked for feasibility and objective on the CPU before anyone relies on it.
The GPU stays optional: every job has a CPU fallback that gives the same answer within tolerance.

*Follow-ups.* "Is the GPU's answer as good?" HiGHS's GPU PDLP landed within $`2 \times 10^{-9}`$
relative of the interior point optimum; cuOpt's PDLP about $`3 \times 10^{-5}`$ away at its default
tolerance, which on a $2B portfolio is $60k. State the tolerance with the result. "And if the
night's machine has no GPU?" The CPU fallback runs, and the manifest records the device, the method
and the tolerance, so the morning's reader knows which one answered.

*Taught in:* lesson 11.4.1; lesson 11.4.3; lesson 11.4.5; lesson 11.4.6; lesson 11.1.1.

</details>

**Q8. Two runs of the same plan on the GPU gave different plans. Is that a bug?**

<details>
<summary>Model answer</summary>

Not by itself. First find which solver and which method answered, then check the plan. cuOpt's
default LP method is concurrent: PDLP, barrier and dual simplex race, and the first to finish
answers. The same 90,000-variable LP came back at 1,000,007.04 on one run and at 1,000,038.0 on
another. The optimum is 1,000,038.0, the objective HiGHS's interior point method reports for that LP
(lesson 11.4.3); the 1,000,007.04 is PDLP winning the race and stopping at its default tolerance of
$`10^{-4}`$, $`3.1 \times 10^{-5}`$ from the optimum. `get_solved_by()` names the winner. Set the method to PDLP and state the tolerance: cuOpt's PDLP and
HiGHS's GPU PDLP each repeated bit for bit in every run measured. A cuOpt MILP does not repeat: two
default runs of a 300-binary GridCap-like model took 14.6 s and 30.0 s and ended at the same gap and
the same objective, 61,587.1, with different plans. Those are two plans within the gap, like the
plans of racing CP-SAT workers (Q1). It is a bug only if a plan breaks a rule or its objective lies
outside the gap, so check every GPU MILP plan for feasibility and objective on the CPU, compare it
with HiGHS on one thread, which repeats, and record the device, the method and the tolerance in the
manifest.

*Follow-ups.* "So what does a rerun prove?" On the GPU with the method fixed to PDLP, the same
bytes; across devices or with the CPU fallback, the same answer within the stated tolerance, never
byte for byte. "Can cuOpt be made to repeat?" Not in the runs measured (T6).

*Taught in:* lesson 11.4.4; lesson 11.4.5; lesson 11.4.6; lesson 10.2.1.

</details>

## Trap Questions: Settings That Do Not Do What They Promise

**T1. "Break ties with $`\varepsilon_i = 10^{-6} \cdot \text{hash}(\text{id}_i)`$." Deterministic?**

<details>
<summary>What is wrong</summary>

Python salts string hashes per process, so the weights change from run to run and the tie-break picks
a different plan in each process: the opposite of what it was for. `production_traps.py` computes
the tie-break ranks in two fresh processes:

```text
tie-break ranks (x % 100) for P017, P032, P101
  process                hash()       sha256
  PYTHONHASHSEED=1       87 45 92     98 71 15
  PYTHONHASHSEED=2       30 39 45     98 71 15
```

Use a stable digest (`hashlib`) or the sorted index, and keep the weights small enough that they can
never outweigh a real difference at the solver's tolerances, yet larger than its absolute gap (too
small an $`\varepsilon`$ was ignored in lesson 10.2.3). Lesson 10.2.3's `hash()` weights gave four
plans in four processes.

*Taught in:* lesson 10.2.3; lesson 12.2.3.

</details>

**T2. "Set Gurobi's `Method=2` for deterministic runs, and `num_workers = 8` (or
`num_search_workers`) with a seed for CP-SAT." Will they repeat?**

<details>
<summary>What is wrong</summary>

`Method=2` selects barrier for the LP; it is not a determinism setting. Gurobi is deterministic by
default for a fixed thread count, and every setting tried in lesson 10.2.2 repeated with or without
it. For CP-SAT, `num_search_workers` is the old name of `num_workers`, and several workers with a
seed still race: eight workers under a deterministic limit gave different plans, and only the
experimental `interleave_search`, or one worker with a seed and a deterministic limit, repeated.
And "replace the time limit with a node limit" does not work on CP-SAT, which refuses a node limit
(lesson 4.2.4 measured that refusal); use its deterministic time.

*Taught in:* lesson 10.2.2; lesson 4.6.3; lesson 3.4.2.

</details>

**T3. "Run Gurobi in containers on Fargate and the license problem goes away." Does it?**

<details>
<summary>What is wrong</summary>

A container still needs a license, and it gets one at run time, never in the image: a WLS key or a
token server reached over the network. Named-user academic and node-locked licenses do not work in
containers, and the free pip license stops at 2,000 variables or 2,000 rows (GridCap large does not
fit). Price that into the solver recommendation, beside the open-source default.

*Taught in:* lesson 5.3.4; lesson 5.4.3; lesson 5.4.4.

</details>

**T4. "A warm start sets a good incumbent at once, so it always speeds up the solve." Measured?**

<details>
<summary>What is wrong</summary>

On 24 paired runs, last cycle's repaired plan cut the first plan's gap from 24%–80% down to 4.2%,
barely changed the work to reach 1%, and saved 12% of the proof only for SCIP. The carried plan, not
repaired, broke four to nine budget rows and was rejected or silently dropped. A start is insurance
for a solve stopped early; check it against this cycle's rows first and read the log to see whether
it was used.

*Taught in:* lesson 11.2.1; lesson 4.3.3.

</details>

**T5. "A golden test asserts that the objective is within $`10^{-4}`$ of the stored one." Enough?**

<details>
<summary>What is wrong</summary>

The objective alone misses a tie (another plan with the same value) and work cut short by a clock. A
golden record holds the input's identity and the reviewed result, and the test compares status, plan
and spend exactly and the objective within a tolerance stated in business units, one readable line
per difference. It catches regressions, not rule errors: a too-strict rule that changes none of its
answers passes it, which is why unit tests and properties come first.

*Taught in:* lesson 12.3.3; lesson 10.2.5.

</details>

**T6. "Turn on cuOpt's `mip_determinism_mode=1`, and its MILP runs repeat like HiGHS on one thread."
Measured?**

<details>
<summary>What is wrong</summary>

Not in the runs measured. On the 300-binary model of Q8, the mode explored 4,600 nodes in 300 s,
against 820,000 nodes in 18 s for a default run; it stopped at its time limit with a 7% gap, and two
such runs still did not repeat. Setting `work_limit` did not stop it either. Treat a cuOpt MILP
result as a plan within the gap: check its feasibility and objective on the CPU before anyone relies
on it, and take repeatable runs from a solver that repeats, such as HiGHS on one thread.

*Taught in:* lesson 11.4.4; lesson 11.4.5; lesson 10.2.2.

</details>

## Whiteboard: Planner Overrides as Bounds

"Planners override the optimizer: 'start P1 in 2028', 'never fund P2', 'P3 not before 2029', 'fund P4
in any year'. How do you put those into the model so that one built model serves every what-if, and
the overrides can be undone?"

<details>
<summary>Model formulation</summary>

The model is the start-year model: $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$, with
$`\sum_t x_{i,t} \le 1`$ (once$`_i`$). Each override changes bounds, except one:

| Override | Change |
| --- | --- |
| start $`i`$ in year $`y`$ | lower bound of $`x_{i,y}`$ set to 1 (the once row zeroes the others) |
| never fund $`i`$ | upper bound of every $`x_{i,t}`$ set to 0 |
| $`i`$ not before year $`y`$ | upper bound of $`x_{i,t}`$ set to 0 for every $`t < y`$ |
| fund $`i`$ in any year | a row, $`\sum_{t \in T_i} x_{i,t} = 1`$ (fund$`_i`$) |

"Fund in any year" is a sum over years, so no single bound can say it. Overrides are data, kept as
records outside the model with who, when and why; restoring the bounds and deleting the row undoes
them, and each one is priced by solving with and without it. Check overrides against windows,
must-dos and each other before the solve: a start year outside the window turned "fund it" into
"drop it" with an `OPTIMAL` status in lesson 6.5.6.

</details>

<!-- practice 2 -->

## Summary

- **Determinism.** Threads race, clocks stop anywhere, and ties go to input order; pin seeds,
  threads and a work limit, rerun in fresh processes, and compare whole manifests.
- **Snapshots.** A `hashlib` digest of a canonical form names the inputs; `hash()` is salted per
  process and names nothing.
- **Tests.** One rule at a time with allowed and refused plans, properties against an independent
  checker, golden records field by field, determinism tests that can fail.
- **Service.** Submit, poll, fetch; solves in a process pool; infeasible is an answer; Batch on
  Fargate solves, Lambda glues, S3 and a SQLite index keep the runs.
- **The GPU.** PDLP's matrix-vector products make large LPs faster on a GPU; a small LP gains
  nothing, and a MILP's search stays on the CPU. The GPU is optional, with a CPU fallback; the
  manifest names the device, the method and the tolerance, and a GPU MILP plan is checked on the CPU.
- **Traps.** `Method=2` is barrier; several CP-SAT workers with a seed still race; containers still
  need a license; a warm start is insurance, not speed; an objective-only golden test misses ties;
  cuOpt's determinism mode was far slower and still did not repeat.

## Reference

| Question | Lessons |
| --- | --- |
| Q1, T1, T2 determinism | 10.2.1; 10.2.2; 10.2.3; 4.6.3; 3.4.2 |
| Q2 snapshots | 10.2.4; 12.2.3; 10.2.5; 7.1.3 |
| Q3, T5 tests | 12.3.1; 12.3.2; 12.3.3; 12.3.4 |
| Q4 API | 12.4.1; 12.4.2; 12.4.3 |
| Q5, T3 cloud and licenses | 12.5.1; 12.5.2; 12.5.3; 12.5.4; 5.3.4; 5.4.3; 5.4.4 |
| Q6, T4 speed | 11.1.1; 11.1.2; 6.7.4; 11.2.1; 11.2.2; 11.2.3; 11.3.5; 4.3.3 |
| Q7, Q8, T6 the GPU | 11.4.1; 11.4.3; 11.4.4; 11.4.5; 11.4.6 |
| Whiteboard | 6.5.6; 12.1.2; project lesson *Scenarios, overrides and snapshots* |

**Further reading:** [CPython `hashlib.py` (read in Python 3.14's standard library)](https://github.com/python/cpython/blob/3.14/Lib/hashlib.py) (the `sha256` constructor and `hexdigest`, a digest of bytes that does not depend on the process); [CP-SAT Python API `cp_model.py` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/sat/python/cp_model.py) (the solver's `parameters`, where `num_workers`, the seed and the deterministic limit are set).

## Challenges

1. In `production_traps.py`, add a third process with `PYTHONHASHSEED=0` and predict which column
   changes.
2. Add an override "P5 no later than 2028" to the whiteboard. Bound or row?
3. Write the record you would store for a whiteboard override so that replaying the records rebuilds
   the overrides in force.

## Design Note: Evidence, Not Assurance

Every answer in this round ends in something that can be rerun: a digest, a manifest, a test that
fails on a planted bug, a measurement over seeds. "We set the seed" is an assurance; "here is the
harness that reran it in five fresh processes" is evidence, and evidence is what auditors and
interviewers ask for.

## The Full Programs

**production_traps.py.** Computes tie-break ranks from `hash()` and from a SHA-256 digest in two fresh
processes with different string-hash seeds (*Trap Questions: Settings That Do Not Do What They
Promise*). *Try:* Replace the ids with integers and predict whether `hash()` still changes between
processes.

- Program: [production_traps.py](src/production_traps.py)
