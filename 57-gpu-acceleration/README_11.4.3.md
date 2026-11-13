# 11.4.3 PDLP on CPU vs. GPU: a Measured Comparison With HiGHS (cuPDLP-C) and OR-Tools

GridCap's infrastructure team has to decide whether the nightly LP runs need a GPU. The vendor
slides say "up to 100× faster". The team's question is narrower: faster than what, on which LPs, at
which accuracy, on our machine? This lesson builds the program that answers it: one model
generator, every solver the machine has, every answer checked against a CPU reference, and the
times printed beside the accuracy. It runs on every machine; the GPU columns appear only where
there is a GPU. The numbers below are one machine's, and the lesson says so wherever it quotes
them. GridCap is a fictional utility; its numbers are teaching data.

## The Model

The transportation LP of lesson 11.4.2, grown: $`n`$ sources and $`n`$ destinations, $`n^2`$
variables, $`2n`$ rows and $`2n^2`$ nonzeros.

**Sets.** $`S`$ the sources and $`D`$ the destinations, $`\lvert S \rvert = \lvert D \rvert = n`$.

**Parameters.** $`a_i = 10n + (i \bmod 7)`$, the supply of source $`i`$; $`d_j`$, the demand of
destination $`j`$, the total supply split as evenly as integers allow; $`k_{i,j} \in \{1, \dots,
99\}`$, the unit cost, from a fixed-seed generator (the seed the toolchain's GPU probes used, so its
measurements and these describe the same LPs).

**Variables.** $`x_{i,j} \ge 0`$, the units moved from $`i`$ to $`j`$.

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

The sizes run from $`n = 30`$ (900 variables) to $`n = 1000`$ (a million variables, two million
nonzeros), the largest size this lesson runs, which leaves the build machine's 8 GB card room to
spare.

## A Fair Comparison Runs Every Solver on the Same Model and Checks Every Answer

`compare.py` builds each LP once and hands the same numbers to each solver:

- **HiGHS interior point** on the CPU (`solver="ipm"`), the reference: it converges to
  $`10^{-8}`$ by default and its answer is the yardstick for the others;
- **OR-Tools PDLP** on the CPU, one thread, at its default $`10^{-6}`$;
- **HiGHS PDLP on the GPU** (cuPDLP-C, `solver="pdlp"`), at HiGHS's default
  `pdlp_optimality_tolerance`, $`10^{-7}`$, only where `gpu_available()`;
- **cuOpt PDLP** (`method` set to PDLP), at its default tolerance, $`10^{-4}`$ relative, only where
  `gpu_available()`.

```python
for n in sizes:
    m = transport(n)
    ipm = highs(m, "ipm")
    pdlp = ortools_pdlp(m, 1e-6)
```

```python
    if gpu:
        hg = highs(m, "pdlp")
        co = cuopt(m, "pdlp")
```

Every answer is compared with the interior point objective, relatively. The CPU half runs on
every machine and prints the same numbers everywhere:

```text
Every answer against HiGHS interior point (CPU), relative difference of the objective
    n   variables      IPM objective   OR-Tools PDLP (CPU)  iterations
   30         900          38,917.00                7e-08         960
  100      10,000         227,777.00                5e-08       1,472
  300      90,000       1,000,038.00                5e-10       1,536
```

OR-Tools' PDLP lands within $`10^{-7}`$ of the interior point objective at every size. Its
iterations barely grow with the size: 960 for 900 variables, 1,536 for 90,000. That is the first
reason first-order methods scale: the work per iteration grows with the nonzeros, and on this
family the number of iterations hardly does.

Three rules make the comparison fair. The model is built once and every solver reads the same
numbers, so a difference is the solver's, never the builder's. Times cover the solve alone, not
the model building (lesson 11.1.1 measured the two apart). And no time is quoted without the
accuracy that was bought with it, because a solver that stops at $`10^{-4}`$ is doing less work than
one that stops at $`10^{-8}`$.

### Handing HiGHS a Whole Model: `highspy.HighsLp`

The module's `highs` function, like the first practice below, does not add variables and rows one
call at a time: it fills one `highspy.HighsLp` object with the whole model and passes it to HiGHS
with `passModel`. `highs_lp.py` shows every field on a three-variable toy (not GridCap data):
maximise $`5x_0 + 4x_1 + 2x_2`$ subject to $`2x_0 + 3x_1 + x_2 \le 5`$ (cap) and
$`x_0 + x_1 + 2x_2 \ge 1`$ (need), with $`x_0 \ge 0`$ integer, $`0 \le x_1 \le 1`$ and
$`x_2 \ge 0`$. It builds the matrix both ways:

```python
def build(colwise: bool, integer: bool = True) -> highspy.HighsLp:
    """The toy model as a HighsLp, its matrix stored column by column or row by row."""
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = 3, 2
    lp.col_cost_ = [5.0, 4.0, 2.0]
    lp.col_lower_ = [0.0, 0.0, 0.0]
    lp.col_upper_ = [inf, 1.0, inf]                     # kHighsInf: no upper bound
    lp.row_lower_ = [-inf, 1.0]                         # cap has no lower side
    lp.row_upper_ = [5.0, inf]                          # need has no upper side
    if colwise:                                         # column k's entries sit at start_[k] .. start_[k+1]-1
        lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        lp.a_matrix_.start_ = [0, 2, 4, 6]
        lp.a_matrix_.index_ = [0, 1, 0, 1, 0, 1]        # the row of each entry
        lp.a_matrix_.value_ = [2.0, 1.0, 3.0, 1.0, 1.0, 2.0]
    else:                                               # row r's entries sit at start_[r] .. start_[r+1]-1
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.start_ = [0, 3, 6]
        lp.a_matrix_.index_ = [0, 1, 2, 0, 1, 2]        # the column of each entry
        lp.a_matrix_.value_ = [2.0, 3.0, 1.0, 1.0, 1.0, 2.0]
    if integer:                                         # leave integrality_ unset for an LP
        lp.integrality_ = [highspy.HighsVarType.kInteger, highspy.HighsVarType.kContinuous,
                           highspy.HighsVarType.kContinuous]
    lp.sense_ = highspy.ObjSense.kMaximize              # kMinimize for a minimisation
    return lp
```

```text
column-wise, x0 integer     Optimal, objective 12, x = [2.0, 0.0, 1.0]
row-wise, x0 integer        Optimal, objective 12, x = [2.0, 0.0, 1.0]
column-wise, x0 continuous  Optimal, objective 12.5, x = [2.5, 0.0, 0.0]
```

- `num_col_` and `num_row_` give the sizes; `col_cost_`, `col_lower_` and `col_upper_` hold one
  entry per variable, `row_lower_` and `row_upper_` one per row. A row with one side gets
  `highspy.kHighsInf` (or its negative) on the other, as in lesson 11.4.1's two-sided rows.
- The matrix is three lists. **Column-wise** (`MatrixFormat.kColwise`), `start_[k]` is where column
  $`k`$'s entries begin in `index_` (their row numbers) and `value_`, and `start_` ends with the
  number of entries; **row-wise** (`kRowwise`, the form `lps.highs` uses) is the same with rows and
  columns swapped. Both give the same answer above.
- `integrality_` holds one `HighsVarType` per variable (`kInteger` or `kContinuous`); left unset,
  the model is an LP, which is why the third line reaches 12.5 with $`x_0 = 2.5`$.
- `sense_` is `ObjSense.kMaximize` or `ObjSense.kMinimize`.

<!-- practice 1 -->

## On the Build Machine's GPU, the Large LPs Are Where It Pays

The course ran `compare.py 30 100 300 1000` once on its build machine: an 8 GB laptop NVIDIA GPU,
in the GPU image (driver CUDA 13.2, runtime CUDA `13.3.29`, HiGHS
`1.14.0` built with CUDA, cuOpt `26.10.0`). Times are wall seconds of one run; cuOpt's column is
cuOpt's own solve time, which leaves out its process start and imports. They depend on the
machine, its load and the run, and your numbers will differ:

<!-- unverified -->
```text
seconds (this machine, this run):
    n     highs-ipm (CPU)  ortools-pdlp (CPU)    highs-pdlp (GPU)    cuopt-pdlp (GPU)
   30               0.007               0.011               0.250               0.188
  100               0.044               0.130               0.355               0.192
  300               0.675               1.686               0.595               0.390
 1000              12.973              11.097               2.386               1.123
```

At a million variables the GPU wins clearly: HiGHS's PDLP took 2.4 s against 13.0 s for the
interior point on the CPU, 5.4 times faster, and cuOpt's PDLP 1.1 s, 11.6 times faster. At
$`n = 300`$ the two GPU solvers and the CPU interior point are within a factor of two. At
$`n = 100`$ and below, the CPU wins by a wide margin: the interior point needed 0.007 s for 900
variables, and neither GPU solver finished in less than 0.18 s.

The CPU PDLP column shows that the algorithm alone is not the speed-up. On the CPU, OR-Tools' PDLP
is slower than the interior point at every size up to 300 and only a little faster at 1,000. PDLP
pays off when its matrix-vector products run on the card.

## Small LPs Lose to Start-Up and Fixed Costs

A GPU solve has costs that do not depend on the LP's size: copying the model to the card's
memory, starting its kernels, copying the answer back, and, for the first GPU solve in a process,
starting CUDA itself. `compare.py` measures that on a 100-variable LP before anything else:

<!-- unverified -->
```text
start-up: a 100-variable LP by HiGHS PDLP on the GPU, the process's first GPU solve 0.430 s, the same LP again 0.213 s
```

The first GPU solve took about 0.2 s more than the second, which is CUDA starting up; and even the
second took 0.21 s for an LP the CPU solves in milliseconds. Those are fixed costs, and a
small LP never earns them back. The HiGHS documentation says the same: the GPU helps mainly on
large LPs, and on small ones PDLP on a GPU can be slower than on the CPU. A service that solves many
small LPs keeps them on the CPU, and one that sends a large LP to the GPU starts CUDA once per
process, not once per solve. GridCap small's LP, at 80 variables, is a CPU job.

## Accuracy Differs by Default: 2e-9 Against 3e-5

The GPU answers on the same run, against the CPU interior point:

<!-- unverified -->
```text
the GPU answers against HiGHS interior point (CPU), relative difference of the objective
    n   HiGHS PDLP (GPU)  iterations   cuOpt PDLP (GPU)  iterations  cuOpt max violation
   30             3e-08       1,080              2e-06       1,700                3e-03
  100             3e-09       1,680              4e-06       2,700                8e-02
  300             2e-09       1,800              3e-05       2,900                2e+00
 1000             2e-09         520              2e-05       1,100                2e+01
```

The two GPU solvers run the same kind of algorithm and stop at different places. HiGHS's PDLP lands
within $`2 \times 10^{-9}`$ of the optimum on the large LPs; cuOpt's within about
$`3 \times 10^{-5}`$, because its default tolerance is $`10^{-4}`$ relative (its documentation lists
PDLP's default accuracy as $`10^{-4}`$, against $`10^{-8}`$ for its barrier method). cuOpt's plan
for the million-variable LP breaks a row by 20 units. Each supply row holds about 10,000 units, so
that is 0.2% of one row; the tolerance is measured against the norm of all 2,000 row bounds
together, not row by row (lesson 11.4.1).

So part of cuOpt's lead in the time table is accuracy it did not buy. Before comparing times,
either set the solvers to the same tolerance or state each one's beside its time, as this lesson
does. And a planner who needs every supply row kept to the unit cannot use a $`10^{-4}`$ answer as
it is, from any device.

<!-- practice 2 -->

## Summary

- **A fair comparison runs every solver on the same model and checks every answer.** One builder,
  times of the solve alone, and an accuracy beside every time.
- **On the build machine's GPU, the large LPs are where it pays.** At a million variables HiGHS's
  GPU PDLP was 5.4 times and cuOpt's 11.6 times faster than the CPU interior point; at 10,000 and
  below the CPU won.
- **Small LPs lose to start-up and fixed costs.** About 0.2 s to start CUDA once per process, and
  about 0.2 s per GPU solve even on a 100-variable LP.
- **Accuracy differs by default: 2e-9 against 3e-5.** HiGHS's PDLP stops at $`10^{-7}`$, cuOpt's at
  $`10^{-4}`$; cuOpt's million-variable plan broke a row by 20 units.

## Reference

| Solver | Device | Call in this module | Default tolerance |
| --- | --- | --- | --- |
| HiGHS interior point | CPU | `highs(m, "ipm")` | $`10^{-8}`$ (`ipm_optimality_tolerance`) |
| OR-Tools PDLP | CPU | `ortools_pdlp(m, 1e-6)` | $`10^{-6}`$ (`simple_optimality_criteria`) |
| HiGHS PDLP (cuPDLP-C) | GPU | `highs(m, "pdlp")` | $`10^{-7}`$ (`pdlp_optimality_tolerance`) |
| cuOpt PDLP | GPU | `cuopt(m, "pdlp")` | $`10^{-4}`$ relative (primal, dual and gap) |

**Further reading:** HiGHS,
[GPU acceleration](https://ergo-code.github.io/HiGHS/dev/guide/gpu/) (cuPDLP-C on NVIDIA GPUs,
help mainly on large LPs, slower than the CPU on small ones, lower accuracy than simplex and
interior point); NVIDIA cuOpt,
[LP and MILP settings](https://docs.nvidia.com/cuopt/user-guide/latest/lp-milp-settings.html)
(the `method` setting and PDLP's default $`10^{-4}`$ tolerances); Lu and Yang,
[cuPDLP.jl: A GPU Implementation of Restarted Primal-Dual Hybrid Gradient for Linear Programming in Julia](https://arxiv.org/abs/2311.12180)
(the first GPU implementation of restarted PDHG, compared with a commercial solver); Lu et al.,
[cuPDLP-C: A Strengthened Implementation of cuPDLP for Linear Programming by C language](https://arxiv.org/abs/2312.14832)
(the C implementation HiGHS builds as its GPU PDLP, measured on CPUs and GPUs); the parameter
comments in OR-Tools'
[`solvers.proto`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/solvers.proto)
(PDLP's default tolerance and threads).

## Challenges

1. Run `compare.py` with the sizes your machine can hold and find the size where the GPU first
   wins on your hardware. Predict it before you run.
2. Set cuOpt's tolerances to $`10^{-7}`$ (its `relative_gap_tolerance`, `relative_primal_tolerance`
   and `relative_dual_tolerance` settings) through `cuopt(m, "pdlp", settings=...)` and predict what
   happens to its iterations and its lead at $`n = 1000`$.
3. A vendor benchmark reports "40× faster than the CPU". List the questions this lesson taught you
   to ask before believing it.

## Design Note: The Comparison Prints What It Did Not Measure

`compare.py` prints its CPU half on every machine and its GPU half only where there is a GPU, and
the times table is labelled "this machine, this run". That keeps the program honest wherever it
runs: a learner without a GPU sees exactly what their machine did, the course's page states which
numbers came from the build machine, and the times never pretend to be a property of the
algorithm.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Without a GPU, `compare.py` prints the CPU
columns only.

**highs_lp.py.** A three-variable toy handed to HiGHS as one `HighsLp`, its matrix column-wise and
row-wise, with and without an integer column (*Handing HiGHS a Whole Model*). *Try:* Change
`sense_` to `kMinimize` and predict the plan.

**compare.py.** Transportation LPs of growing size, solved by every solver the machine has, with the
accuracy and the time of each (*A Fair Comparison*, *On the Build Machine's GPU*, *Small LPs*,
*Accuracy Differs*). Pass the sizes as arguments: `compare.py 30 100 300 1000`. *Try:* Add $`n =
600`$ and predict where its CPU interior point time falls between 0.7 s and 13 s.

- Program: [highs_lp.py](src/highs_lp.py)
- Program: [compare.py](src/compare.py)
- Library: [lps.py](src/lps.py)
