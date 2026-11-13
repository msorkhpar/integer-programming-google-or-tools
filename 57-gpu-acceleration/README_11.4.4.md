# 11.4.4 Determinism on a GPU: What Repeats, What Doesn't, and What the Manifest Records

GridCap's regulator can ask, months later, for the exact run behind an approved plan. Section 10
built the answer for the CPU: pinned solvers, one thread or a deterministic work limit, and a
**run manifest** that records what went in and what came out, so a rerun can be compared with it
(lessons 10.2.2 and 10.2.4). Now part of the nightly work runs on a GPU. This lesson measures what
repeats there and what does not, and changes the manifest so that it records the device, the
method and the tolerance, and so that its comparison asks for equal bits only where they were
promised. GridCap is a fictional utility; its numbers are teaching data.

Two words used throughout. Two runs are **bit for bit** the same when the objective and every
value of the plan are equal as stored numbers, byte for byte; a 16-hex-digit **digest** (the start
of a SHA-256 hash of those bytes) stands for them, and equal digests mean equal bits. Two runs
**agree within tolerance** when their objectives differ by at most a stated relative amount and
both plans keep the rows (lesson 11.4.2).

## The Model

The two LPs of lesson 11.4.2, unchanged. GridCap small's LP relaxation, with
$`0 \le x_{i,t} \le 1`$ for each project $`i \in P`$ and start year $`t \in T_i`$:

```math
\begin{aligned}
\max \;& \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \\
\text{s.t. }& \sum_{t \in T_i} x_{i,t} \le 1 \;\; \forall i \in P \setminus M \;\; \text{(once}_i),
\qquad \sum_{t \in T_i} x_{i,t} = 1 \;\; \forall i \in M \;\; \text{(must}_i), \\
& \sum_{i \in g} \sum_{t \in T_i} x_{i,t} \le 1 \;\; \forall g \in \mathcal{G} \;\; \text{(alt}_g),
\qquad \sum_{i \in P} \sum_{t \in T_i} s_{i,t,y}\, x_{i,t} \le B_y \;\; \forall y \in Y \;\; \text{(budget}_y)
\end{aligned}
```

and the $`n \times n`$ transportation LP, with $`x_{i,j} \ge 0`$ for each source $`i \in S`$ and
destination $`j \in D`$:

```math
\begin{aligned}
\min \;& \sum_{i \in S} \sum_{j \in D} k_{i,j}\, x_{i,j} \\
\text{s.t. }& \sum_{j \in D} x_{i,j} \le a_i \;\; \forall i \in S \;\; \text{(supply}_i),
\qquad \sum_{i \in S} x_{i,j} \ge d_j \;\; \forall j \in D \;\; \text{(demand}_j)
\end{aligned}
```

Sets and parameters are as defined in lessons 11.4.1 and 11.4.2. Lesson 11.4.5 adds the MILP.

## On the CPU, a Fixed Solver, Method and Thread Count Repeat Bit for Bit

`repeat.py` runs each solver twice in one process on each LP and compares the digests:

```python
cpu_runs = {
    "HiGHS simplex, 1 thread": lambda m: highs(m, "simplex"),
    "HiGHS interior point, 1 thread": lambda m: highs(m, "ipm"),
    "OR-Tools PDLP, 1 thread": lambda m: ortools_pdlp(m, 1e-6),
    "OR-Tools PDLP, 4 threads": lambda m: ortools_pdlp(m, 1e-6, threads=4),
}
```

```text
CPU, two runs in one process:
  GridCap small LP   HiGHS simplex, 1 thread         same bits: True
  GridCap small LP   HiGHS interior point, 1 thread  same bits: True
  GridCap small LP   OR-Tools PDLP, 1 thread         same bits: True
  GridCap small LP   OR-Tools PDLP, 4 threads        same bits: True
  transport 100x100  HiGHS simplex, 1 thread         same bits: True
  transport 100x100  HiGHS interior point, 1 thread  same bits: True
  transport 100x100  OR-Tools PDLP, 1 thread         same bits: True
  transport 100x100  OR-Tools PDLP, 4 threads        same bits: True
OR-Tools PDLP, 1 thread against 4 threads on transport 100x100: same bits False, iterations 1472 and 1536
```

Every configuration repeated itself, including PDLP on four threads. But the four-thread run is not
the one-thread run: it took 1,536 iterations instead of 1,472 and ended on different bits. The
comment on `num_shards` in OR-Tools' `solvers.proto` gives the reason: PDLP splits its vectors into
shards for the threads, the roundoff depends on the number of shards, and reproducible results
need the same number. So the thread count is part of what a run promises, as lesson 10.2.2 found
for the MIP solvers.

The same programs printed the same digests in the CPU image and in the GPU image on the build
machine:

```text
the answers' digests (equal digests mean equal bits; compare them across machines and images):
  transport 100x100  HiGHS simplex, 1 thread         objective 227777.0             x f700beb08eb9746e
  transport 100x100  HiGHS interior point, 1 thread  objective 227777.0             x f8ab14295015d7ed
  transport 100x100  OR-Tools PDLP, 1 thread         objective 227776.9885284009    x e557e1be6038794b
```

The GPU image's `highspy` is a different build of HiGHS `1.14.0` (compiled with CUDA, yet reporting the same version),
and its CPU methods still gave the same bits as the CPU image's wheel on this machine. That is a
measurement, not a promise: a different processor or a different build can round differently, and
only a rerun on that machine shows it.

## On the GPU, PDLP Repeated Bit for Bit, Run After Run

The GPU half of `repeat.py`, on the build machine (an 8 GB laptop NVIDIA GPU, one run of the program;
each cuOpt solve in a process of its own):

<!-- unverified -->
```text
device: GPU [an 8 GB laptop NVIDIA GPU] (compute capability 12.0), driver CUDA 13.2, runtime CUDA 13.3.29
GPU, two runs (cuOpt: each in a process of its own):
  GridCap small LP   HiGHS PDLP                      same bits: True
  GridCap small LP   cuOpt PDLP                      same bits: True
  transport 100x100  HiGHS PDLP                      same bits: True
  transport 100x100  cuOpt PDLP                      same bits: True
```

Both GPU PDLP implementations repeated themselves exactly, and the toolchain's probes found the same
for the 90,000- and million-variable transportation LPs, in one process and in new containers. A
GPU is not random by nature: a computation whose order of operations is fixed gives the same bits
every time. What breaks repeatability is an order that changes from run to run, as the next two
sections show.

Repeating itself does not make a GPU run equal to a CPU run. HiGHS's GPU PDLP and OR-Tools' CPU
PDLP are different code on different hardware, and their answers to the same LP differ in the last
digits; the manifest below compares them within a tolerance.

## cuOpt's Concurrent Default Is a Race: Record Which Method Won

cuOpt's default LP `method` is **concurrent**: it starts PDLP, barrier (interior point) and dual
simplex at once and returns the answer of whichever finishes first. Which one finishes first can
change from run to run, and the three stop at different accuracies. The toolchain's probe saw it
happen on the 300 × 300 transportation LP: one run returned 1,000,007.04 (PDLP won,
$`3.1 \times 10^{-5}`$ from the optimum, within its $`10^{-4}`$ tolerance) and the next 1,000,038.0
(another method won). Three more runs of `repeat.py`:

<!-- unverified -->
```text
cuOpt's default method (concurrent) on transport 300x300, three runs:
  run 1: solved by dual simplex, objective 1,000,038.0000, digest a7918ec1a3bf1cf5
  run 2: solved by dual simplex, objective 1,000,038.0000, digest a7918ec1a3bf1cf5
  run 3: solved by dual simplex, objective 1,000,038.0000, digest a7918ec1a3bf1cf5
```

Dual simplex won all three this time, so all three agree. That does not make concurrent mode
repeatable; it means this race had the same winner three times on an idle machine. A busier GPU or
CPU can change the winner, and the answer with it. Two rules follow:

- **When a result must repeat, set the method.** This module's `cuopt(m, "pdlp")` sets `method` to
  PDLP, which repeated in every run measured.
- **When the method is concurrent, record the winner.** cuOpt's `get_solved_by()` returns it
  (`repeat.py` prints it); a manifest that records it can at least say which algorithm produced
  each answer, and a comparison of two concurrent runs with different winners is a comparison
  within tolerance, never of bits.

## cuOpt's MILP Did Not Repeat, Even in Its Determinism Mode

cuOpt's MILP solver runs heuristics and branch and bound in parallel on the CPU and the GPU
(lesson 11.4.5), and their timing decides which plans are found first. The toolchain's probe solved
a 300-binary GridCap-like MILP twice with the defaults: 14.6 s and 30.0 s, both to the
default gap, with objectives equal to about $`10^{-16}`$ and different plans. Lesson 11.4.5's run on
GridCap medium found the same: two runs, two different plans.

cuOpt has a setting for this, `mip_determinism_mode`. On the probe's MILP it was far slower (4,600
nodes in 300 s, against 820,000 in 18 s by default) and, stopped by its time limit, still did not
repeat. `milp_gpu.py` tried it on GridCap medium with a 20-second limit:

<!-- unverified -->
```text
cuOpt determinism mode, run 1: FeasibleFound, objective 204,983, gap 1.1e-01, 127 nodes, 20.1 s
cuOpt determinism mode, run 2: FeasibleFound, objective 204,849, gap 1.1e-01, 127 nodes, 20.1 s
  the two runs same bits: False
```

Both runs explored exactly 127 nodes, which suggests the search itself followed the same path; but
both were stopped by the clock, and a clock stops a run at a different point each time (lesson
10.2.1), so the plans differ. The probe also found that `work_limit`, the setting that would stop
it at a fixed amount of work instead, did not stop it. On cuOpt `26.10.0`, then, no setting the
course found makes a MILP result repeat, and the course never quotes a cuOpt MILP plan as
reproducible. HiGHS on one thread does repeat (lesson 11.4.5), and it stays the solver of the plan
of record.

<!-- practice 1 -->

## The Manifest Records the Device, the Method and the Tolerance

Lesson 10.2.4's manifest recorded the inputs, the solver with its parameters, the versions and the
result, and left out the clock and anything that names the machine. For runs that may happen on a
GPU it needs three more facts, because each one changes the bits:

- **the device**, and for a GPU its model and CUDA versions, never its UUID. `highspy` reports
  `1.14.0` in both images, the CUDA build included, so the version alone does not say which build ran;
- **the method**, which for cuOpt's concurrent mode is the winner, not the request;
- **the tolerance**, because a run at $`10^{-4}`$ and a run at $`10^{-8}`$ are different promises,
  and **the threads**, as the CPU section showed.

`gpu_manifest.manifest` builds it:

```python
def manifest(m: dict, run: dict, method: str, tolerance: float, threads: int, device: str,
             requested: str | None = None) -> dict:
    """What went in and what came out; `device` is where this solver ran, not what the machine has.
    For a race, `method` is the winner and `requested` is "concurrent"."""
    where = {"device": "cpu"}
    if device == "gpu":
        report = device_report()
        where = {"device": "gpu", "device_name": report["name"], "driver_cuda": report["driver_cuda"],
                 "cuda_runtime": report["cuda_runtime"]}
    if requested is not None:
        where["requested"] = requested
    return {
        "inputs": {"model": digest(m["c"] + m["values"] + m["row_lb"] + m["row_ub"]),
                   "kind": "milp" if any(m["integer"]) else "lp"},
```

The device is where *this solve* ran: a CPU solve on a machine that has a GPU records `"cpu"`, so
its manifest matches the same solve on a machine without one. A concurrent run records the winner
as its `method` and `"concurrent"` as `requested`, and the inputs record whether the model is an LP
or a MILP.

The comparison asks for equal bits only where the reference table at the end of this lesson
promises them: from a **repeat**, a run whose solver block (name, method, requested, tolerance,
threads, device) and versions are all the same, and only if that configuration repeats. Two runs
of cuOpt's concurrent mode are never held to bits, even with the same winner, and neither are two
cuOpt MILP runs. Everything else is compared within the tolerance:

```python
def bits_promised(a: dict, b: dict) -> bool:
    """Equal bits are owed only by a repeat (the same solver block and versions) of a run that repeats."""
    if a["solver"] != b["solver"] or a["versions"] != b["versions"]:
        return False
    if a["solver"].get("requested") == "concurrent":                   # a race: the winner can change
        return False
    if a["solver"]["name"] == "cuopt" and a["inputs"]["kind"] == "milp":   # no setting made these repeat
        return False
    return True


def compare(a: dict, b: dict, tol: float = TOLERANCE) -> str:
    """'identical', 'within tolerance', 'different', or 'not comparable' (other inputs)."""
    if a["inputs"] != b["inputs"]:
        return "not comparable"
    if bits_promised(a, b):                                            # a repeat that repeats: every bit
        return "identical" if a["result"] == b["result"] else "different"
    close = relative_difference(a["result"]["objective"], b["result"]["objective"]) <= tol
    return "within tolerance" if close else "different"
```

The program compares real CPU runs, and then two pairs of made-up records that show the two
exceptions: the OR-Tools record relabelled as two concurrent cuOpt runs whose plans differ, and
again as two cuOpt MILP runs whose plans differ. No cuOpt solve runs for those two lines; they test
the rule, not the solver.

```text
{"name": "ortools", "method": "pdlp", "tolerance": 1e-06, "threads": 1, "device": "cpu"}
{"status": "TERMINATION_REASON_OPTIMAL", "objective": 227776.9885284009, "x": "e557e1be6038794b", "iterations": 1472}
OR-Tools PDLP, run again:             identical
OR-Tools PDLP, 4 threads against 1:   within tolerance
HiGHS interior point against PDLP:    within tolerance
a repeat whose plan changed:          different
two concurrent runs, plans differ:    within tolerance
two cuOpt MILP runs, plans differ:    within tolerance
```

A repeat with the same configuration must be identical, and one whose plan changed is `different`,
which is the alarm lesson 10.2.5's harness raises. The four-thread run and the interior point run
are other configurations, so they are held to the tolerance, which they meet. The two made-up cuOpt
pairs have equal solver blocks, but neither configuration promised bits, so a changed plan is not
an alarm: their objectives are compared within the tolerance, and a cuOpt MILP plan is also checked
as a plan (lesson 11.4.5).

On the GPU image the same program adds a GPU run (one run of the program as shown above, on the
build machine's 8 GB laptop NVIDIA GPU):

<!-- unverified -->
```text
{"name": "highs", "method": "pdlp", "tolerance": 1e-07, "threads": 1, "device": "gpu", "device_name": "[an 8 GB laptop NVIDIA GPU]", "driver_cuda": "13.2", "cuda_runtime": "13.3.29"}
HiGHS PDLP on the GPU against OR-Tools PDLP on the CPU: within tolerance, objective rel. diff 5e-08
```

So across devices, results are compared within tolerance, never bit for bit; on one device with
one configuration, a solver that repeats is held to every bit. A cuOpt MILP run, which does not
repeat even with every setting the same, is a third case: it is checked as a plan (feasible, and
within the gap of the best bound), which is lesson 11.4.5's subject.

<!-- practice 2 -->

## Summary

- **On the CPU, a fixed solver, method and thread count repeat bit for bit.** OR-Tools' PDLP on 4
  threads repeated itself but differed from 1 thread (1,536 against 1,472 iterations); the same
  CPU solves gave the same digests in both images on the build machine.
- **On the GPU, PDLP repeated bit for bit, run after run.** HiGHS's and cuOpt's PDLP both did; a GPU
  is not random, an order of operations that changes is.
- **cuOpt's concurrent default is a race: record which method won.** Set `method` when a result
  must repeat; record `get_solved_by()` when it is concurrent.
- **cuOpt's MILP did not repeat, even in its determinism mode.** Different plans at the same gap;
  determinism mode stopped by the clock differed too.
- **The manifest records the device, the method and the tolerance.** Equal bits are asked only of a
  repeat; across devices, configurations or methods, results agree within tolerance.

## Reference

| Run | Repeated bit for bit here? | Compare a rerun by |
| --- | --- | --- |
| HiGHS simplex or interior point, 1 thread (CPU) | yes | bits |
| OR-Tools PDLP, fixed threads (CPU) | yes | bits; a different thread count, tolerance |
| HiGHS PDLP (GPU) | yes | bits on the same device; tolerance against the CPU |
| cuOpt PDLP, `method` set (GPU) | yes | bits on the same device; tolerance against the CPU |
| cuOpt concurrent (GPU) | not promised: the winner can change | tolerance, with `get_solved_by()` recorded |
| cuOpt MILP, any setting tried (GPU) | no: different plans at the same gap | as a plan: feasible and within the gap |

| Manifest field | Why |
| --- | --- |
| `solver.device`, `device_name`, `driver_cuda`, `cuda_runtime` | where the solve ran; the build's version string does not say |
| `solver.method` | the algorithm that answered (the winner, for a race) |
| `solver.tolerance` | what "optimal" promised |
| `solver.threads` | changes PDLP's bits on the CPU |

**Further reading:** the parameter comments in OR-Tools'
[`solvers.proto`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/solvers.proto)
(`num_threads`, and `num_shards`: the roundoff depends on the shard count, so reproducible results
need the same one); NVIDIA cuOpt,
[LP and MILP settings](https://docs.nvidia.com/cuopt/user-guide/latest/lp-milp-settings.html)
(the concurrent method racing PDLP, dual simplex and barrier, and the MILP split between GPU and
CPU work); the toolchain's GPU measurements (the CUDA build's version string, the concurrent race
on the 300 × 300 LP, and the two default and determinism-mode MILP runs).

## Challenges

1. Add OR-Tools PDLP with `num_threads=4` and `num_shards=16` to `repeat.py`, twice with each. Predict
   which pairs give the same bits.
2. Change `compare` so that two concurrent cuOpt runs with the same `solved_by` are held to bits.
   Is that safe? What would you need to measure first?
3. Your auditor asks why last month's GPU run cannot be reproduced bit for bit on the new
   workstation's different card. Write the two sentences you would send, using the manifest's
   fields.

## Design Note: A Manifest States Its Own Promise

`compare` reads from the manifests themselves whether bits were promised: same solver block and
versions, and a configuration that repeats, bits; anything else, tolerance. No caller decides it case by case. Recording the device
and method in the solver block is what makes that possible, and leaving out the card's UUID and the
machine's name is what keeps two identical machines' manifests identical.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Without a GPU, the GPU parts are skipped.

**repeat.py.** Each CPU solver twice on each LP, the digests of three of them, and on a GPU each GPU
solver twice and cuOpt's concurrent mode three times (*On the CPU*, *On the GPU*, *cuOpt's
Concurrent Default*). *Try:* Change the concurrent runs to the 100 × 100 LP and predict the winner.

**gpu_manifest.py.** The manifest with the device, method and tolerance, and the comparison that
asks for bits only from a repeat (*The Manifest Records*). *Try:* Give the second OR-Tools run a
tolerance of `1e-5` in its manifest only, and predict the verdict.

The determinism-mode runs come from `milp_gpu.py`, the program of lesson 11.4.5.

- Program: [repeat.py](src/repeat.py)
- Program: [gpu_manifest.py](src/gpu_manifest.py)
- Library: [lps.py](src/lps.py)
