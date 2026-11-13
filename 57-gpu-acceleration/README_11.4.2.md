# 11.4.2 Detecting a GPU, With a CPU Fallback That Gives the Same Answer

GridCap's planning service runs in three places: on the analysts' laptops, which have no NVIDIA
GPU; on the build server that runs the tests, which has none either; and on one workstation with a
GPU, where the large nightly LPs go. It is one code base. The code must find out where it is,
use the GPU when there is one and it answers, fall back to the CPU otherwise, and give the same
answer in all three places, where "the same" is a tolerance the team writes down. This lesson
builds that pattern on the course's GPU helper, `00-base/gpu.py`, and on the toolchain's optional
GPU image. GridCap is a fictional utility; its numbers are teaching data.

This course runs every program in a container image (`scripts/runner.py`). The default image is the
**CPU image**. The optional **GPU image** adds HiGHS built with CUDA (NVIDIA's GPU programming
platform), so that `highspy` can run PDLP on the card (HiGHS calls it cuPDLP-C), and NVIDIA's
**cuOpt** solver. The runner starts the GPU image only when it is present and Docker can reach a
GPU, and the CPU image otherwise, with no error.

## The Model

Two LPs, each solved on every device. The first is GridCap small's LP relaxation, exactly as in
lesson 11.4.1 (80 variables $`0 \le x_{i,t} \le 1`$, maximise NPV, rows $`\text{once}_i`$,
$`\text{must}_i`$, $`\text{alt}_g`$ and $`\text{budget}_y`$). The second is a **transportation
LP**, the model lesson 11.4.3 grows to a million variables:

**Sets.** $`S`$ the sources and $`D`$ the destinations, $`n`$ of each.

**Parameters.** $`a_i`$, the supply of source $`i`$; $`d_j`$, the demand of destination $`j`$, with
$`\sum_j d_j = \sum_i a_i`$; $`k_{i,j} \in \{1, \dots, 99\}`$, the cost of moving one unit from $`i`$
to $`j`$, drawn from a fixed-seed generator.

**Variables.** $`x_{i,j} \ge 0`$ for every $`i \in S`$, $`j \in D`$: the units moved.

**Objective.**

```math
\min \; \sum_{i \in S} \sum_{j \in D} k_{i,j}\, x_{i,j}
```

**Constraints.**

```math
\begin{aligned}
\sum_{j \in D} x_{i,j} &\le a_i && \forall i \in S && \text{(supply}_i) \\
\sum_{i \in S} x_{i,j} &\ge d_j && \forall j \in D && \text{(demand}_j)
\end{aligned}
```

`lps.transport(n)` builds it for $`n`$ sources and $`n`$ destinations; here $`n = 100`$, so 10,000
variables and 200 rows.

## Ask Once: Is There a GPU This Process Can Use?

`00-base/gpu.py` answers that question for every program, test and practice of the course:

- `gpu_available()` is True only when two things hold: the program runs in the GPU image (it
  carries a file, `/opt/gpu/variant.json`, that lists its CUDA, HiGHS and cuOpt versions), and the
  CUDA driver reports a device. The GPU image on a machine whose GPU did not reach the container
  is a CPU machine, and so is the CPU image on a machine with a GPU.
- It asks the driver in a **child process**, so the calling program never starts CUDA itself: a
  process forked from one that has started CUDA cannot use it.
- `describe()` returns one line that names the device, for every output that states one.
- `requires_gpu()` marks a pytest test that runs only where `gpu_available()`, and is skipped with
  the reason everywhere else.

On the CPU image, and on the build machine's GPU image, `describe()` printed (on these pages, the
card's model name in a GPU line is shown as its class, in square brackets):

<!-- unverified -->
```text
device: CPU (the CPU image)
device: GPU [an 8 GB laptop NVIDIA GPU] (compute capability 12.0), driver CUDA 13.2, runtime CUDA 13.3.29
```

The GPU line names the card's model, its compute capability (its CUDA generation), and two CUDA
versions: the driver's and the one the image was built with. It names no single card or machine:
two machines with the same card print the same line. Never print a card's UUID, the machine's host
name or a path under a home directory in an output that is shared; cuOpt's log does name the UUID
in its header, which is one reason the next sections keep that log off the console.

## Never Ask highspy for PDLP Without a GPU

HiGHS chooses its LP method with the option `solver`: `"simplex"`, `"ipm"` (interior point) or
`"pdlp"`. The HiGHS documentation says a GPU build without a GPU returns an error for its native
PDLP; the toolchain measured something worse for the CUDA build's PDLP, cuPDLP-C, which has no
CPU path at all: with no GPU, `solver="pdlp"` prints `cusparseCreate(): CUDA context cannot be initialized` and
**kills the process** with a segmentation fault. A `try`/`except` cannot catch that; the program is
gone. So the check comes first, in the one function that sets the option:

```python
    if solver == "pdlp" and not gpu_available():
        # The CUDA build's PDLP has no CPU path: without a GPU it kills the process.
        raise RuntimeError("highspy's PDLP runs here only on a GPU; check gpu_available() first")
```

The CPU image's `highspy` is the ordinary wheel, with a CPU PDLP of its own, but the course never
uses it: the same line of code must be safe in both images, and `highs(m, "pdlp")` either runs on
a GPU or raises an exception the program can catch. A module test checks that it raises when
`gpu_available()` is False.

## cuOpt Runs in a Process of Its Own

cuOpt cannot share the course's Python environment, because the toolchain found the two cannot
be installed together: its data library, cuDF, needs pandas and numpy versions older than the ones
the course pins. The GPU image gives cuOpt a
virtual environment of its own, and `gpu.run_cuopt(script, *args)` runs a script with that
environment's interpreter, in a new process. What is kept apart is the environment and the
process, not the hardware: cuOpt shares the machine, the GPU image and the card with HiGHS, and
lesson 11.4.3 runs both on the same GPU, one after the other. `lps.cuopt` writes the model and the
settings to a JSON file, runs `cuopt_worker.py` on it, and reads one JSON line back:

```python
    with tempfile.TemporaryDirectory() as folder:
        job = Path(folder) / "job.json"
        job.write_text(json.dumps({"model": m, "method": method, "settings": settings or {}, "want_x": want_x,
                                   "keep_log": list(keep_log)}), encoding="utf-8")
        done = run_cuopt(WORKER, job)
    if done.returncode != 0:
        raise RuntimeError(f"cuOpt worker failed: {done.stderr[-500:]}")
    return json.loads(done.stdout.strip().splitlines()[-1])
```

A separate process has two more uses. If cuOpt crashes, only the worker dies, and the caller gets
an exception it can handle. And cuOpt writes its log to the console by default, with the card's
UUID, the CPU model and the memory in use in its header; the worker sends the log to
a file instead and returns only the lines it was asked for, never one of those:

```python
    s.set_parameter("log_to_console", False)
```

`run_cuopt` itself refuses to start without a GPU, so `lps.cuopt` is only ever called behind a
`gpu_available()` check.

## Fall Back When the GPU Is Missing or Its Answer Is Not Optimal

`fallback.solve_lp` tries HiGHS's PDLP on the GPU when there is one, accepts its answer only if
HiGHS reports `Optimal`, and otherwise solves on the CPU with HiGHS's interior point method. It
returns the result and the list of what it tried:

```python
def solve_lp(m: dict, use_gpu: bool | None = None) -> tuple[dict, list[str]]:
    """GPU PDLP when there is a GPU and it reports Optimal; HiGHS interior point on the CPU otherwise."""
    if use_gpu is None:
        use_gpu = gpu_available()
    tried = []
    if use_gpu:                                    # never solver="pdlp" without a GPU: it kills the process
        result = highs(m, "pdlp")
        tried.append(f"{result['solver']} {result['status']}")
        if result["status"] == "Optimal":
            return result, tried
    result = highs(m, "ipm")
    tried.append(f"{result['solver']} {result['status']}")
    return result, tried
```

The CPU path, which runs on every machine, compared with HiGHS's simplex method as the reference:

```text
reference: HiGHS simplex on the CPU; tolerance 1e-06
CPU path (runs on every machine):
  GridCap small LP   tried highs-ipm Optimal      objective      26587.442  agrees: True
  transport 100x100  tried highs-ipm Optimal      objective     227777.000  agrees: True
```

On the build machine's GPU image, the GPU path printed (one run, on an 8 GB laptop NVIDIA GPU):

<!-- unverified -->
```text
device: GPU [an 8 GB laptop NVIDIA GPU] (compute capability 12.0), driver CUDA 13.2, runtime CUDA 13.3.29
GPU path:
  GridCap small LP   tried highs-pdlp Unknown, highs-ipm Optimal  objective      26587.442  rel. diff 0.0e+00  agrees: True
  transport 100x100  tried highs-pdlp Optimal                     objective     227776.999  rel. diff 3.3e-09  agrees: True
  the refused GPU answer: status Unknown, objective rel. diff 3.1e-08, max primal infeasibility 9.2e-08, max dual infeasibility 1.1e+03
```

The transportation LP went to the GPU and came back `Optimal`, 3.3 parts in a billion from the
simplex objective. GridCap's LP did not: the GPU's PDLP returned the status `Unknown`, and the
fallback solved it on the CPU. The last line shows why HiGHS refused the answer. Its objective was
within $`3.1 \times 10^{-8}`$ of the optimum and its plan kept every row to $`9.2 \times 10^{-8}`$,
but its prices broke the dual rows by up to 1,100. PDLP stops on relative measures (lesson
11.4.1), and the HiGHS documentation warns that HiGHS may then refuse an answer PDLP calls optimal,
and says to read the infeasibilities in its `HighsInfo`. A program that took the objective without
the status would have used a result HiGHS did not stand behind; this one never does.

So the fallback has two triggers, and both are needed: **no GPU** (do not even try) and **a GPU
answer the solver does not report as optimal** (try, then solve on the CPU).

<!-- practice 1 -->

## The Same Answer Means Within a Stated Tolerance

The GPU's answer to the transportation LP is not the simplex answer bit for bit: its objective is
227,776.999 against 227,777.000. Nor is the CPU interior point's, in general. Different algorithms,
and the same algorithm on different hardware, add numbers in different orders, and floating-point
addition is not associative (lesson 10.1.1). So "the same answer on every device" is a tolerance,
stated in the code:

```python
def agrees(result: dict, reference: dict, m: dict, tol: float = TOLERANCE) -> bool:
    """Same answer within tol: the objective, relatively, and every row and bound, scaled by the largest one."""
    scale = max([1.0] + [abs(v) for v in m["row_lb"] + m["row_ub"] if abs(v) != float("inf")])
    return (relative_difference(result["objective"], reference["objective"]) <= tol
            and violation(m, result["x"]) <= tol * scale)
```

Two tests, both needed:

- **The objective, relatively:** $`\lvert z - z_\text{ref} \rvert / \max(1, \lvert z_\text{ref}
  \rvert) \le 10^{-6}`$. An absolute test would be too strict for a portfolio worth $227 million
  and too loose for one worth $200k.
- **The plan keeps the rows**, to $`10^{-6}`$ times the largest row bound. An objective can match
  while the plan overspends a budget: a plan that breaks a row can be worth more than the optimum
  (lesson 2.4.1 saw PDLP land above the maximum).

The tolerance is checked against an answer from a different solver on the CPU, never against the
GPU's own report. A module test runs the same check on the GPU image with a GPU: HiGHS's GPU PDLP
on the 100 × 100 transportation LP agrees with the CPU interior point within $`10^{-6}`$, and
does not match it bit for bit. Lesson 11.4.4 asks which runs should match bit for bit.

<!-- practice 2 -->

## Summary

- **Ask once: is there a GPU this process can use?** `gpu_available()` needs the GPU image and a
  device the driver reports; `describe()` names the device without naming the machine.
- **Never ask highspy for PDLP without a GPU.** The CUDA build's PDLP kills the process with no GPU;
  check first, so the failure is an exception.
- **cuOpt runs in a process of its own.** Its environment cannot share the course's; a
  worker process also contains a crash and keeps the log, which names the card's UUID, off the
  console.
- **Fall back when the GPU is missing or its answer is not optimal.** On GridCap's LP the GPU PDLP
  said `Unknown`, with dual rows broken by 1,100, and the CPU answered.
- **The same answer means within a stated tolerance.** Relative objective and scaled row breach,
  against a CPU answer from another solver.

## Reference

| Call | Where | Does |
| --- | --- | --- |
| `gpu_available()` | `00-base/gpu.py` | True with the GPU image and a device the driver reports |
| `describe()` | `00-base/gpu.py` | one line naming the device and CUDA versions |
| `requires_gpu()` | `00-base/gpu.py` | a pytest mark: run only with a GPU, skip with the reason otherwise |
| `run_cuopt(script, *args)` | `00-base/gpu.py` | run a script under cuOpt's interpreter, in its own process |
| `lps.highs(m, "pdlp")` | this module | GPU PDLP, or `RuntimeError` without a GPU |
| `fallback.solve_lp(m)` | this module | GPU first if present and `Optimal`, else CPU interior point |

| What the toolchain measured | What it means for a program |
| --- | --- |
| cuOpt's data library needs older pandas and numpy than the course pins | cuOpt runs under its own interpreter, in a separate process |
| the CUDA build's PDLP kills the process when there is no GPU | no `solver="pdlp"` on the CUDA build of highspy without `gpu_available()` |
| cuPDLP-C prints its log on stdout | `output_flag` off |
| cuOpt's log header names the card's UUID, the CPU model and the memory | cuOpt's `log_to_console` off; never quote its log header |

**Further reading:** HiGHS,
[GPU acceleration](https://ergo-code.github.io/HiGHS/dev/guide/gpu/) (cuPDLP-C and HiPDLP, the
`CUPDLP_GPU` build option, the `solver` option, lower accuracy than simplex or interior point,
answers PDLP calls optimal that HiGHS may refuse, and the infeasibility data to read in
`HighsInfo`); NVIDIA cuOpt,
[LP and MILP settings](https://docs.nvidia.com/cuopt/user-guide/latest/lp-milp-settings.html)
(`log_to_console`, `log_file`, `method`, and the default tolerances); the course's
`00-base/gpu.py` and the toolchain's notes on its GPU variant (its measurements of cuOpt's separate
environment, of cuPDLP-C without a GPU and with `output_flag` on, and of cuOpt's log header).

## Challenges

1. Change `solve_lp` to try cuOpt's PDLP when HiGHS's GPU PDLP returns `Unknown`, before the CPU.
   What would you check about cuOpt's answer before accepting it? (Lesson 11.4.3 measures how far
   its answers are from the optimum.)
2. A teammate replaces `agrees` with `result["objective"] == reference["objective"]` "to be safe".
   Predict what happens to the transportation LP on the CPU path and on the GPU path.
3. Your service runs on a machine whose GPU is busy with another job and out of memory. Which of
   the two fallback triggers catches that, and what would you add?

## Design Note: The Device Is a Fact, the Fallback Is a Rule

`gpu_available()` reports a fact about the machine; `solve_lp` applies a rule to it. Keeping them
apart means the rule can be tested on any machine with `use_gpu=False` or `True` passed in, and the
fact is asked in one place, in a child process, once. The same split runs through the course's
tests: the CPU half of every test carries the grade, and `requires_gpu()` adds checks without
removing any.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. On a machine without the GPU image, the GPU
parts are skipped and the CPU parts print as shown.

**fallback.py.** The fallback and the agreement check on GridCap small's LP and the 100 × 100
transportation LP, the CPU path everywhere and the GPU path where there is one (*Fall Back*, *The
Same Answer*). *Try:* Lower `TOLERANCE` to `1e-10` and predict which lines say `agrees: False`.

**cuopt_worker.py.** The script cuOpt's interpreter runs: it reads a job file, solves, and prints
one JSON line (*cuOpt Runs in a Process of Its Own*). Run on its own, it says what it is.

- Program: [fallback.py](src/fallback.py)
- Program: [cuopt_worker.py](src/cuopt_worker.py)
- Library: [lps.py](src/lps.py)
