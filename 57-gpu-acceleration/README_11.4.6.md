# 11.4.6 One Run Policy for Threads, Workers and the GPU

By now GridCap's planning service has settings in many places: one thread for HiGHS so plans repeat
(lesson 10.2.2), workers for CP-SAT, a GPU when there is one (lesson 11.4.2), PDLP's tolerance, a
gap for the MILP, a method for cuOpt (lesson 11.4.4). Each was decided for a good reason, and each
lives next to the call that uses it. The result is a service whose behaviour no one can state in
one place, and whose manifest records what the code happened to pass, not what was intended. This
lesson gathers every one of those decisions into a single **run policy**: one object, made by one
function from the job and the machine, that decides the device, solver, method, threads and
tolerance, falls back to the CPU, is written into the manifest, and says how a GPU result may be
used for a capital plan. GridCap is a fictional utility; its numbers are teaching data.

## The Model

The policy decides how to run the models of this module; it builds none. They are, in brief:

**The capital plan** (lesson 11.4.5), GridCap medium: projects $`i \in P`$, start years
$`t \in T_i`$, must-do projects $`M`$, alternative groups $`\mathcal{G}`$, budgets $`B_y`$,
spend $`s_{i,t,y}`$ and NPV $`\text{npv}_{i,t}`$ in $k, and $`x_{i,t} \in \{0, 1\}`$:

```math
\begin{aligned}
\max \;& \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \\
\text{s.t. }& \sum_{t \in T_i} x_{i,t} \le 1 \;\; \forall i \in P \setminus M \;\; \text{(once}_i),
\qquad \sum_{t \in T_i} x_{i,t} = 1 \;\; \forall i \in M \;\; \text{(must}_i), \\
& \sum_{i \in g} \sum_{t \in T_i} x_{i,t} \le 1 \;\; \forall g \in \mathcal{G} \;\; \text{(alt}_g),
\qquad \sum_{i \in P} \sum_{t \in T_i} s_{i,t,y}\, x_{i,t} \le B_y \;\; \forall y \in Y \;\; \text{(budget}_y)
\end{aligned}
```

**Its LP relaxation** (lesson 11.4.1): the same rows with $`0 \le x_{i,t} \le 1`$, here for GridCap
small. **The transportation LP** (lesson 11.4.3): $`x_{i,j} \ge 0`$, minimise
$`\sum k_{i,j} x_{i,j}`$ subject to $`\text{supply}_i`$ and $`\text{demand}_j`$, here with
$`n = 300`$ (90,000 variables, 180,000 nonzeros), standing in for a large LP.

## One Object Decides the Device, Solver, Method, Threads and Tolerance

A **job** says what is being solved and what the answer is for. A **run policy** says how to solve
it. Both are frozen dataclasses, so a policy cannot be changed after it is made:

```python
@dataclass(frozen=True)
class Job:
    name: str
    kind: str                   # "lp" or "milp"
    nonzeros: int
    use: str                    # "plan" (the plan of record), "bound" (an LP bound), or "start" (a starting plan)


@dataclass(frozen=True)
class RunPolicy:
    device: str
    solver: str
    method: str
    threads: int
    tolerance: float            # LP optimality tolerance, or the MILP relative gap
    verify_on_cpu: bool         # a GPU answer is checked on the CPU before anything uses it
    why: str
```

One function makes the policy, from the job and one fact about the machine:

```python
def decide(job: Job, gpu: bool) -> RunPolicy:
    """The whole policy in one place. Every branch without a GPU is a CPU branch."""
    if job.kind == "milp" and job.use == "plan":
        return RunPolicy("cpu", "highs", "branch-and-bound", 1, 1e-4, False, "the plan of record repeats bit for bit")
    if job.kind == "milp":
        if gpu:
            return RunPolicy("gpu", "cuopt", "milp", 0, 1e-3, True, "a starting plan; 0 threads: cuOpt chooses")
        return RunPolicy("cpu", "highs", "branch-and-bound", 1, 1e-3, False, "no GPU: the CPU solver")
    if job.use == "plan":
        return RunPolicy("cpu", "highs", "simplex", 1, 1e-7, False, "a vertex, repeatable, for the plan of record")
    if gpu and job.nonzeros >= GPU_MIN_NONZEROS:
        return RunPolicy("gpu", "highs", "pdlp", 1, 1e-7, True, "large LP: GPU PDLP, CPU fallback if not Optimal")
    if job.nonzeros >= GPU_MIN_NONZEROS:
        return RunPolicy("cpu", "highs", "ipm", 1, 1e-8, False, "large LP, no GPU: interior point")
    return RunPolicy("cpu", "highs", "simplex", 1, 1e-7, False, "small LP: the CPU is faster")
```

Each branch carries a reason from this module:

- **The plan of record never goes to the GPU.** It must repeat bit for bit for the auditor, and
  HiGHS on one thread does (lessons 10.2.2 and 11.4.5); cuOpt's MILP does not (lesson 11.4.4). A
  continuous plan of record goes to simplex for the same reason, and because simplex ends on a
  vertex (lesson 11.4.1).
- **A starting plan may come from cuOpt**, with a looser gap, because it will be checked and only
  handed to the CPU solver as a start. `threads` 0 means cuOpt picks its own CPU workers; HiGHS gets
  exactly 1.
- **A large LP goes to the GPU's PDLP**, a small one stays on the CPU. `GPU_MIN_NONZEROS` is
  100,000: on the build machine the GPU first matched the CPU at the 300 × 300 transportation LP
  (180,000 nonzeros) and lost clearly at 100 × 100 (20,000), lesson 11.4.3.
- **Every tolerance is explicit**, so the manifest can record what "optimal" promised.

`decide` is a pure function, so its whole behaviour can be printed for both answers to "is there a
GPU?", on any machine:

```text
job                              GPU?  device solver method           thr    tol  verify
final capital plan               False cpu    highs  branch-and-bound   1  1e-04  False
final capital plan               True  cpu    highs  branch-and-bound   1  1e-04  False
starting plan for tonight's run  False cpu    highs  branch-and-bound   1  1e-03  False
starting plan for tonight's run  True  gpu    cuopt  milp               0  1e-03  True
LP relaxation, GridCap small     False cpu    highs  simplex            1  1e-07  False
LP relaxation, GridCap small     True  cpu    highs  simplex            1  1e-07  False
large LP, 300x300 transport      False cpu    highs  ipm                1  1e-08  False
large LP, 300x300 transport      True  gpu    highs  pdlp               1  1e-07  True
continuous budget split          False cpu    highs  simplex            1  1e-07  False
continuous budget split          True  cpu    highs  simplex            1  1e-07  False
```

Two jobs of five change device when a GPU appears; three never do. Every `GPU? False` row is a CPU
row, so the service works the same on a machine with no GPU, only without the two GPU branches.

<!-- practice 1 -->

## The Policy Falls Back to the CPU and Is Recorded in the Manifest

`run` solves a job under the live policy, `decide(job, gpu_available())`, and handles the two
fallback triggers of lesson 11.4.2 with the policy itself: if the GPU's PDLP does not answer
`Optimal`, it asks `decide` again with `gpu=False` and solves under that CPU policy, so the
manifest records the policy that actually ran, not the one first chosen:

```python
    policy = decide(job, gpu_available())
    if policy.device == "gpu" and policy.solver == "highs":
        result = highs(m, "pdlp", tolerance=policy.tolerance)
        if result["status"] != "Optimal":                       # the fallback: same job, the CPU branch
            policy = decide(job, gpu=False)
            result = highs(m, policy.method, tolerance=policy.tolerance)
```

```python
    record = {"policy": asdict(policy), "result": {"solver": result["solver"], "status": result["status"],
                                                   "objective": round(result["objective"], 6)}}
```

The returned record goes into the manifest beside lesson 11.4.4's fields: the policy is the
`solver` block, with the reason, and it is the same on every machine that made the same decision.
The GridCap small LP relaxation, on any machine:

```text
{"device": "cpu", "solver": "highs", "method": "simplex", "threads": 1, "tolerance": 1e-07, "verify_on_cpu": false, "why": "small LP: the CPU is faster"}
{"solver": "highs-simplex", "status": "Optimal", "objective": 26587.44151}
```

On the build machine's GPU image (an 8 GB laptop NVIDIA GPU, one run), the two GPU branches ran:

<!-- unverified -->
```text
device: GPU [an 8 GB laptop NVIDIA GPU] (compute capability 12.0), driver CUDA 13.2, runtime CUDA 13.3.29
{"device": "gpu", "solver": "highs", "method": "pdlp", "threads": 1, "tolerance": 1e-07, "verify_on_cpu": true, "why": "large LP: GPU PDLP, CPU fallback if not Optimal"}
{"solver": "highs-pdlp", "status": "Optimal", "objective": 1000038.002168} verified on the CPU: True
{"device": "gpu", "solver": "cuopt", "method": "milp", "threads": 0, "tolerance": 0.001, "verify_on_cpu": true, "why": "a starting plan; 0 threads: cuOpt chooses"}
{"solver": "cuopt-milp", "status": "FeasibleFound", "objective": 226807.0} verified on the CPU: True
```

## A GPU Result Serves a Capital Plan Only as a Bound or a Start, Verified on the CPU

Every GPU branch in the policy has `verify_on_cpu` set, and `run` acts on it before anything uses
the answer:

```python
    if policy.verify_on_cpu and job.kind == "lp":              # a CPU interior point solve, held to 1e-6
        cpu = highs(m, "ipm")
        record["verified_on_cpu"] = relative_difference(result["objective"], cpu["objective"]) <= 1e-6
    elif policy.verify_on_cpu:                                 # a MILP plan: rows, integrality, and the gap
        cpu = highs(m, threads=1, gap=policy.tolerance)        # to the best bound any solver proved (lesson 11.4.5)
        best = min(result["bound"], cpu["bound"])              # a maximisation: the smallest bound is the tightest
        record["verified_on_cpu"] = check(m, result, best, policy.tolerance)[0]
```

A MILP plan is judged as lesson 11.4.5 judges one: against the tightest bound any solver proved,
not against the bound of the solver that found it. So `run` also solves the job with HiGHS on one
CPU thread to the same gap, and passes the smaller of the two bounds (the model is a maximisation)
to `check`. A cuOpt plan that only met cuOpt's own bound, when HiGHS had proved a tighter one, is
refused. cuOpt's plans change from run to run (lesson 11.4.4), so the objective above is one run's.

Why each use is acceptable, and the one that is not:

- **An LP bound or relaxation.** The relaxation's optimum caps every plan's worth (lesson 3.1.1);
  analysts use it to say how far a plan is from the best possible. A GPU's PDLP gives it within its
  tolerance, $`2 \times 10^{-9}`$ here, which is far finer than any budget decision. The CPU
  interior point confirms it, and the manifest says it was confirmed.
- **A starting or heuristic plan.** A cuOpt plan that passes lesson 11.4.5's check (rows kept,
  integral, within its gap) can be handed to HiGHS as a start (lesson 11.2.1). HiGHS then proves,
  or improves, the plan on the CPU, and the plan of record is HiGHS's. A start that fails the check
  is dropped and the CPU solve runs without it.
- **The plan of record: never from the GPU.** It must repeat bit for bit and carry a full proof
  from one solver, and no GPU path in this module repeats a MILP plan. The policy has no branch
  that sends it there, whatever the machine has.

The rule in one line: **the GPU may make the night shorter, never the plan different.** Everything
it produces is either a number the CPU confirms or a start the CPU solver improves on, and every
answer a planner signs comes from a run the auditor can repeat.

<!-- practice 2 -->

## HiGHS Stays at the Centre of the Policy

This course runs HiGHS as its default solver (the course README says so, and lesson 2.4.1 set it
beside GLOP and PDLP). The policy keeps it at the centre on every device: HiGHS's simplex and interior point on the
CPU, HiGHS's own GPU PDLP (cuPDLP-C) for a large LP, and HiGHS on one thread for the plan of
record. A team that standardises on HiGHS therefore gets the GPU path from the same library, with
the same model format, the same status codes and the same version pin, and the CPU fallback is
HiGHS too. cuOpt enters only where it is the better tool: a GPU heuristic plan, checked.

## Summary

- **One object decides the device, solver, method, threads and tolerance.** `decide(job, gpu)` is
  pure and frozen; every `gpu=False` branch is a CPU branch.
- **The policy falls back to the CPU and is recorded in the manifest.** A refused GPU answer makes
  `run` ask the policy again without a GPU, and the record holds the policy that ran.
- **A GPU result serves a capital plan only as a bound or a start, verified on the CPU.** The LP
  bound is confirmed by an interior point solve; a cuOpt plan is checked and then improved by
  HiGHS; the plan of record never comes from the GPU.
- **HiGHS stays at the centre of the policy.** CPU simplex and interior point, GPU PDLP, and the
  one-thread plan of record all come from HiGHS.

## Reference

| Use of the answer | Device | Solver and method | Threads | Tolerance | Verified on the CPU |
| --- | --- | --- | --- | --- | --- |
| MILP plan of record | CPU | HiGHS branch and bound | 1 | gap $`10^{-4}`$ | it is the CPU run |
| MILP starting plan | GPU if present | cuOpt MILP, else HiGHS | cuOpt's own, else 1 | gap $`10^{-3}`$ | the plan check of lesson 11.4.5 |
| large LP bound | GPU if present | HiGHS PDLP, else HiGHS interior point | 1 | $`10^{-7}`$, else $`10^{-8}`$ | interior point, within $`10^{-6}`$ |
| small LP, or a continuous plan of record | CPU | HiGHS simplex | 1 | $`10^{-7}`$ | it is the CPU run |

**Further reading:** HiGHS,
[GPU acceleration](https://ergo-code.github.io/HiGHS/dev/guide/gpu/) (one library, its PDLP on
the GPU with the same `solver` option, and the tolerances to raise for it); NVIDIA cuOpt,
[LP and MILP settings](https://docs.nvidia.com/cuopt/user-guide/latest/lp-milp-settings.html)
(`num_cpu_threads` chosen from the core count by default, `method`, and the MILP gap); the parameter
comments in OR-Tools'
[`solvers.proto`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/solvers.proto)
(`num_threads` and the shard count that reproducible PDLP runs must keep).

## Challenges

1. Add a job "what-if for a board meeting, answer in a minute", a MILP whose answer is shown but
   never signed. Write its branch in `decide` and say what `verify_on_cpu` should be.
2. Your workstation's GPU is replaced by a larger one. Which line of the policy should change, and
   what would you run first to change it? (Lesson 11.4.3.)
3. A teammate wants `decide` to read `gpu_available()` itself instead of taking `gpu` as an
   argument. What does the module lose?

## Design Note: A Policy Is Data, So It Can Be Diffed

Because a policy is a frozen dataclass printed into the manifest, a change of policy shows up as a
change of data: two manifests that differ only in `policy.device` tell the auditor exactly why
their bits may differ, and a review of `decide` is a review of one function with one table of
outputs. The alternative, settings scattered beside each call, has no single place to review and
nothing to record.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Without a GPU, the GPU branches are shown in
the table but not run.

**run_policy.py.** The jobs, the policy for each with and without a GPU, a live run of the GridCap
small LP relaxation, and on a GPU the large LP and the starting plan, each verified on the CPU (*One
Object Decides*, *The Policy Falls Back*, *A GPU Result Serves a Capital Plan*). *Try:* Lower
`GPU_MIN_NONZEROS` to 100 and predict which rows of the table change and what the live GridCap run
does on a GPU.

- Program: [run_policy.py](src/run_policy.py)
- Library: [lps.py](src/lps.py)
