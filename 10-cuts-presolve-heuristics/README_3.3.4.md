# 3.3.4 Reading a Full MIP Log Line by Line

The five-year plan for GridCap medium is about to run every night. Most nights nobody will read its
log. The night a planner says "the plan changed and nothing in the data did", or "it says optimal,
but is it?", the log is where the answer is. Lesson 2.4.2 read an LP log; a MIP log has everything
an LP log has, plus a table of the search: the bounds closing in, the heuristics that found each
plan, the cuts, and the restarts. This lesson reads one complete HiGHS MIP log from the first line
to the last, with lessons 3.3.1 to 3.3.3 behind it. GridCap is a fictional utility; its numbers are
teaching data.

## The Model

The five-year selection model of lesson 3.3.2, solved by HiGHS with its default settings.

**Sets.** $`P`$ the projects; $`Y = \{2027, \dots, 2031\}`$; $`M \subseteq P`$ the must-do
projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$; $`\mathcal{G}`$ the
alternative groups.

**Parameters.** $`v_i`$ the NPV of project $`i`$ ($k); $`c_{i,y}`$ its spend in year $`y`$ at its
earliest start ($k); $`B_y`$ the budget of year $`y`$ ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is funded.

```math
\begin{aligned}
\max \;& \sum_{i \in P} v_i\, x_i \\
\text{s.t. }& \sum_{i \in P} c_{i,y}\, x_i \le B_y && \forall y \in Y && \text{(budget}_y) \\
& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& x_c \le x_{p(c)} && \forall c \in C && \text{(after}_c) \\
& \sum_{i \in g} x_i \le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
& x_i \in \{0, 1\} && \forall i \in P
\end{aligned}
```

On GridCap medium: 400 variables, and 80 rows (5 budget, 39 must, 18 after, 18 alt).

## Ask for the Log, and Mask Only What Changes Between Runs

MathOpt hands each batch of log lines to the function passed as `msg_cb`. Collecting them in a list
keeps the whole log, in order, for a person or a test to read:

```python
def solve_with_log(model: mathopt.Model, params: mathopt.SolveParameters | None = None,
                   solver: mathopt.SolverType = mathopt.SolverType.HIGHS) -> tuple[mathopt.SolveResult, list[str]]:
    """Solve and keep every log line the solver wrote, in order, with its times masked."""
    lines: list[str] = []
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        result = mathopt.solve(model, solver, params=params, msg_cb=lines.extend)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
    return result, [mask_times(line) for line in lines]
```

The `dup2` lines point the process's standard output at `/dev/null` during the solve, because the
HiGHS bundled with OR-Tools 9.15 prints a stray debug line on some MIP solves, even with no log
asked for: `HighsMipSolverData::transformNewIntegerFeasibleSolution tmpSolver.run();`. It is C
output, held in a buffer and written when the program exits, so `solve_with_log` flushes that buffer
into `/dev/null` (the `fflush` line) before it gives standard output back. The log itself arrives
through `msg_cb` and is not affected. `mask_times` replaces what changes
from run to run:

```python
TIMES = [
    (re.compile(r"(\s)\d+(\.\d+)?s$"), r"\1<t>s"),                     # presolve rounds, progress rows
    (re.compile(r"^(\s*Timing\s+)[\d.]+"), r"\1<t>"),                   # report: wall-clock seconds
    (re.compile(r"^(\s*P-D integral\s+)[\d.e+-]+"), r"\1<t>"),          # report: changes from run to run
]
```

Everything else in this log came out the same on every run of this program on the course's runner
image: same rows, same nodes, same values. The section 10 lesson *Where nondeterminism comes from:
threads, time limits, ties* explains when a solver's search is repeatable and when it is not; the
times never are.

The whole log is printed by `full_log.py`. The sections below take it a piece at a time, in order.

## The Header and Presolve Say What the Search Will Work On

```text
MIP selection has 80 rows; 400 cols; 443 nonzeros; 400 integer variables (400 binary)
Coefficient ranges:
  Matrix  [1e+00, 6e+03]
  Cost    [1e+01, 6e+03]
  Bound   [1e+00, 1e+00]
  RHS     [1e+00, 4e+04]
Presolving model
37 rows, 172 cols, 273 nonzeros  <t>s
17 rows, 172 cols, 271 nonzeros  <t>s
Presolve reductions: rows 17(-63); columns 172(-228); nonzeros 271(-172)
Objective function is integral with scale 1
```

- **The first line** checks the model you built: 80 rows and 400 columns, as counted above, and
  "400 integer variables (400 binary)". A MIP whose integer count is 0 has lost its integrality (a
  forgotten `is_integer=True`), and HiGHS would solve an LP.
- **Coefficient ranges** are read as in lesson 2.4.2: the smallest and largest absolute values, here
  spend of about $6,000k at most in the matrix, and budgets of about $40,000k on the right. Nothing
  spans more than five powers of ten.
- **Presolve** (lesson 3.3.2) leaves 17 rows and 172 columns: most of the 228 removed columns are
  projects with nothing to decide.
- **Objective function is integral with scale 1** means every objective coefficient is an integer
  (after multiplying by the scale, 1 here), and every variable of the objective is integer. So every
  plan's value is an integer. HiGHS uses that fact at the end, as this lesson shows.

```text
Solving MIP model with:
   17 rows
   172 cols (172 binary, 0 integer, 0 implied int., 0 continuous, 0 domain fixed)
   271 nonzeros
```

This is the model the search works on, after presolve: 172 binary columns and nothing else, so the
other column counts (`integer`, `implied int.`, `continuous`, `domain fixed`) are all 0.

## The Legend Names Every Source of a New Plan

```text
Src: B => Branching; C => Central rounding; F => Feasibility pump; H => Heuristic;
     I => Shifting; J => Feasibility jump; L => Sub-MIP; P => Empty MIP; R => Randomized rounding;
     S => Solve LP; T => Evaluate node; U => Unbounded; X => User solution; Y => HiGHS solution;
     Z => ZI Round; l => Trivial lower; p => Trivial point; u => Trivial upper; z => Trivial zero
```

Each row of the table that follows starts with one of these letters when a new incumbent was found,
and the letter says by what. Most name primal heuristics of lesson 3.3.3's kind: rounding (`R`,
`C`, `Z`), sub-MIPs (`L`, the family of RINS), shifting and feasibility pumps. `B` (branching) and
`T` (evaluate node) name plans the search itself turned up, and `X` a plan you supplied. Upper and
lower case differ: `Z` is ZI Round, `z` is the trivial zero plan. HiGHS's option list names several
of these heuristics, each with a switch: feasibility jump, RINS and RENS run by default, ZI Round
and shifting only when switched on (`mip_heuristic_run_zi_round`, `mip_heuristic_run_shifting`).
The letters are HiGHS's own; other solvers print other logs.

## Each Row of the Table Is a Snapshot of the Search

```text
        Nodes      |    B&B Tree     |            Objective Bounds              |  Dynamic Constraints |       Work
Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time
```

One row is the state of the search at one moment. HiGHS's documentation does not describe this
table. The meanings below come from the header, from numbers this log checks against its own report
and against the `SolveResult`, from HiGHS's documented terms (primal bound, dual bound, gap), and,
for `Leaves`, `Expl.`, `Cuts`, `InLp` and `Confl.`, from the HiGHS source code that prints the row
(`printDisplayLine` in `HighsMipSolverData.cpp`). The source quoted on this page is HiGHS 1.12.0,
the version whose number is in the HiGHS library OR-Tools 9.15 ships. The columns, in order:

| Column | Meaning |
| --- | --- |
| Src | the source letter of a new incumbent; blank on a periodic report |
| Proc. | nodes processed so far (79 on the last row, as the report's `Nodes` and `node_count` say) |
| InQueue | open nodes waiting to be explored |
| Leaves | leaf nodes of the tree, counted from the last restart |
| Expl. | the share of the search tree already closed, in percent |
| BestBound | the dual bound: no plan is worth more (for a maximization) |
| BestSol | the incumbent's value, the primal bound: the best plan found so far |
| Gap | $`\lvert \text{BestBound} - \text{BestSol} \rvert / \lvert \text{BestSol} \rvert`$ |
| Cuts | cuts held in HiGHS's cut pool right now (lesson 3.3.1); not a running total |
| InLp | cuts currently in the LP, the rows beyond the model's own |
| Confl. | conflicts held in HiGHS's conflict pool right now (below the table) |
| LpIters | LP iterations so far, in all LPs (9,738 on the last row, as in the report) |
| Time | wall-clock seconds (masked here) |

A **conflict** is a combination of variable fixings that HiGHS has found can lead to no plan worth
keeping. In the source, when a node's LP is infeasible, or its bound cannot beat the incumbent,
HiGHS works out which of the node's fixings caused it (`addInfeasibleConflict` and
`addBoundExceedingConflict` in `HighsSearch.cpp`) and stores that set in its conflict pool. Other
nodes that repeat the combination can then be cut off without solving their LP. `Confl.` is the
pool's current count (`getNumConflicts`: conflicts added minus conflicts deleted), so like `Cuts` it
can fall as well as rise.

The gap is the one number to watch. When it reaches the tolerance, the search stops.

## The Root Rows Show Heuristics Racing the Bound Down

```text
Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time

 z       0       0         0   0.00%   inf             163973             Large        0      0      0         0     <t>s
 p       0       0         0   0.00%   inf             176827             Large        0      0      0         0     <t>s
 J       0       0         0   0.00%   inf             177784             Large        0      0      0         0     <t>s
 R       0       0         0   0.00%   275164.826811   271757             1.25%        0      0      0        16     <t>s
 L       0       0         0   0.00%   275107.199141   274960             0.05%      906     39     29       116     <t>s
 L       0       0         0   0.00%   275097.381543   274969             0.05%      961     42     29       470     <t>s
```

Every row has `Proc.` 0: all of this happens at the root, before the first branch. Read down:

- **z, p, J**: three cheap plans (trivial zero, trivial point, feasibility jump) found before any LP
  is solved: `LpIters` is still 0. `BestSol` is always a value of the model you wrote, the columns
  presolve removed included (on the last row it is 274,979, the report's primal bound and the
  `SolveResult`'s objective), so even the trivial zero plan is worth 163,973, not 0. `BestBound` is
  `inf` because no LP has given a bound yet, and the gap is `Large`.
- **R**: the root LP is solved (16 simplex iterations) and its value, 275,164.826811, becomes the
  bound. It is the LP relaxation bound that GLOP printed in lesson 3.3.1 (275,164.8). Randomized
  rounding of the LP point gives a plan worth 271,757: gap 1.25%.
- **L, L**: cuts appear (906 in the pool, 39 of them in the LP) and the bound falls to 275,107.2,
  and two sub-MIP heuristics find 274,960 and 274,969. The gap is 0.05%.

The program `log_and_result.py` reads the lettered rows and recomputes each gap:

```text
new incumbents, in the order HiGHS found them:
  z Trivial zero         value   163,973  bound           inf  gap  none yet  (log says Large)
  p Trivial point        value   176,827  bound           inf  gap  none yet  (log says Large)
  J Feasibility jump     value   177,784  bound           inf  gap  none yet  (log says Large)
  R Randomized rounding  value   271,757  bound   275,164.827  gap   1.2540%  (log says 1.25%)
  L Sub-MIP              value   274,960  bound   275,107.199  gap   0.0535%  (log says 0.05%)
  L Sub-MIP              value   274,969  bound   275,097.382  gap   0.0467%  (log says 0.05%)
  L Sub-MIP              value   274,979  bound   275,063.709  gap   0.0308%  (log says 0.03%)
```

So HiGHS's gap is relative to the incumbent: $`(275{,}164.827 - 271{,}757) / 271{,}757 = 1.254\%`$.
The log rounds it to two decimals. Notice that both sides move: heuristics push the incumbent up,
and cuts push the bound down. Before any branching, the gap went from `Large` to 0.03%.

<!-- practice 1 -->

## A Restart Presolves Again With What the Root Learned

```text
51.2% inactive integer columns, restarting
Model after restart has 7 rows, 84 cols (84 bin., 0 int., 0 impl., 0 cont., 0 dom.fix.), and 112 nonzeros
         0       0         0   0.00%   275097.381543   274969             0.05%       19      0      0      1095     <t>s
         0       0         0   0.00%   275097.381543   274969             0.05%       19     19      2      1121     <t>s
 L       0       0         0   0.00%   275063.708991   274979             0.03%     1682     61      2      1286     <t>s
```

The message says that 51.2% of the 172 integer columns are now inactive, and the next line shows
what HiGHS does about it: it **restarts**, presolving the model again and starting the root again on
what is left, 7 rows and 84 columns. The numbers agree: 48.8% of 172 is 84, so the inactive columns
are the ones the restart removed. (The log does not say what made them inactive, and HiGHS's
documentation says only that restarts are on by default, option `mip_allow_restart`.) A restart
keeps the incumbent (274,969) and the bound, as the first rows after it show. The cut pool starts
again: `Cuts` falls from 961 to 19. A second restart follows the same way, and $`84 \times (1 -
0.131) = 73`$ columns remain:

```text
13.1% inactive integer columns, restarting
Model after restart has 7 rows, 73 cols (73 bin., 0 int., 0 impl., 0 cont., 0 dom.fix.), and 97 nonzeros
         0       0         0   0.00%   275063.185112   274979             0.03%       27      0      0      2789     <t>s
         0       0         0   0.00%   275063.185112   274979             0.03%       27     26      4      2835     <t>s
        79       0        15 100.00%   275006.946429   274979             0.01%     2131     32    782      9738     <t>s
```

The last row is the end of the search: 79 nodes processed, none left in the queue, the tree 100%
explored, the bound at 275,006.946429, the incumbent still 274,979, and 9,738 simplex iterations in
all. Branch-and-bound proper (lessons 3.2.1 to 3.2.4) happened between the last two rows; this log prints a row
only now and then, so most nodes have no row of their own.

## The Report Is the Verdict, and Optimal Means Within the Gap Tolerance

```text
Solving report
  Model             selection
  Status            Optimal
  Primal bound      274979
  Dual bound        275006
  Gap               0.00982% (tolerance: 0.01%)
  P-D integral      <t>
  Solution status   feasible
                    274979 (objective)
                    0 (bound viol.)
                    0 (int. viol.)
                    0 (row viol.)
  Timing            <t>
  Max sub-MIP depth 4
  Nodes             79
  Repair LPs        4 (0 feasible; 0 iterations)
  LP iterations     9738
                    2685 (strong br.)
                    1116 (separation)
                    4645 (heuristics)
WARNING: Method setLogCallback is deprecated: alternative method is setCallback
```

Line by line:

- **Status Optimal**: the gap is within the tolerance. Not "proved best": see below.
- **Primal bound 274979**: the incumbent's value. **Dual bound 275006**: the bound. It was
  275,006.946429 in the last row; because the objective is integral, no plan can be worth a
  fraction, so the bound is rounded down to the integer 275,006.
- **Gap 0.00982% (tolerance: 0.01%)**: $`(275{,}006 - 274{,}979) / 274{,}979 = 27 / 274{,}979`$. The
  tolerance is HiGHS's default relative gap, option `mip_rel_gap`, documented as
  $`\lvert ub - lb \rvert / \lvert ub \rvert`$ with default $`10^{-4}`$, where $`ub`$ is the primal bound
  (HiGHS minimizes internally). With the unrounded bound the gap would be
  $`27.946 / 274{,}979 = 0.0102\%`$, just over it; the integral objective is what brought the
  gap under the tolerance at this point.
- **P-D integral** is HiGHS's primal-dual integral (`primal_dual_integral` in its documented
  `HighsInfo`, which gives no more than the name). The source (`updatePrimalDualIntegral` in
  `HighsMipSolverData.cpp`) says what it is: every time the bound or the incumbent changes, HiGHS
  adds the seconds since the last change times the gap during those seconds. It is the area under
  the gap-against-time curve, small when the gap closes early. Because it is measured in seconds, it
  changes from run to run, so it is masked.
- **Solution status feasible**, then the incumbent checked against the original model: its
  objective, and its largest bound, integrality and row violations, all 0.
- **Max sub-MIP depth 4**: a sub-MIP heuristic (source letter `L`) solves a smaller MIP with many
  variables fixed, and that smaller MIP can run sub-MIPs of its own. In the source
  (`solveSubMip` in `HighsPrimalHeuristics.cpp`) each sub-MIP's depth is one more than its parent's,
  and the line reports the deepest nesting reached: here a sub-MIP four levels down.
- **Repair LPs 4 (0 feasible; 0 iterations)**: when a plan found on the presolved model breaks a
  bound, row or whole-number rule of the original model once presolve is undone, HiGHS tries to
  repair it. It rounds every integer variable, fixes it there, and solves an LP over the rest
  (`transformNewIntegerFeasibleSolution` in `HighsMipSolverData.cpp`). The line counts those LPs,
  sub-MIPs' included, and how many gave a plan; here none did, and the plans HiGHS kept came from
  elsewhere. The stray debug line of the first section is printed by this repair step, just before
  each repair LP is solved, which is why it appears on some MIP solves and not others. HiGHS's
  documentation describes neither line.
- **Nodes 79**, matching the last row.
- **LP iterations 9738**, split by what they were spent on: strong branching (trying candidate
  branches before choosing one, lesson 3.2.3), cut separation, and heuristics; the other 1,292 are
  not broken down. Nearly half of all the LP work here was heuristics.
- **WARNING** comes from HiGHS: OR-Tools 9.15 attaches to its log with a method HiGHS has
  deprecated. It is printed on every run, as in lesson 2.4.2, and says nothing about the model.

The same facts are on the `SolveResult`, which is where a program should read them:

```python
bounds = result.termination.objective_bounds
print("from the SolveResult:")
print(f"  termination {result.termination.reason.name}")
print(f"  primal bound {bounds.primal_bound:,.0f}, dual bound {bounds.dual_bound:,.0f}, "
      f"gap {relative_gap(bounds.dual_bound, bounds.primal_bound):.5%}")
print(f"  nodes {result.solve_stats.node_count}, LP iterations {result.solve_stats.simplex_iterations:,}")
```

```text
from the SolveResult:
  termination OPTIMAL
  primal bound 274,979, dual bound 275,006, gap 0.00982%
  nodes 79, LP iterations 9,738
```

"Optimal" with a 0.01% tolerance means the plan is within 0.01% of the best, not that it is the
best. To prove the best, set the tolerance to zero:

```text
the same model with relative_gap_tolerance=0:
  termination OPTIMAL, value 274,999, dual bound 274,999, nodes 582
```

A better plan existed, worth 274,999: 20 more than the default run's answer, and 582 nodes to find
and prove it instead of 79. On a portfolio measured in $k, 20 is $20,000, well inside the 0.01% that
the default run promised and kept. Whether that is acceptable is a business decision, and lessons
3.4.1 to 3.4.3 are about making it on purpose. For reading logs, the lesson is: the status
says the search stopped for a reason; the gap line says what that reason promises.

<!-- practice 2 -->

<!-- practice 3 -->

## Summary

- **Ask for the log with `msg_cb` and keep it as lines; mask only what changes between runs.**
  Everything but the times and the P-D integral repeated exactly.
- **The header and presolve say what the search will work on:** 400 binaries became 172 after
  presolve; an integral objective lets HiGHS round the bound.
- **The legend names every source of a new plan:** one letter per row, upper and lower case
  different.
- **Each row of the table is a snapshot:** nodes, bound, incumbent, gap, cuts and work so far.
- **The root rows show heuristics racing the bound down:** from `Large` to 0.03% before the first
  branch.
- **A restart presolves again with what the root learned**, keeping the incumbent and the bound.
- **The report is the verdict, and Optimal means within the gap tolerance:** the default run stopped
  at 274,979; the proved optimum is 274,999.

## Reference

| Log line | What to read in it |
| --- | --- |
| `MIP ... has R rows; C cols; ...; N integer variables` | the model as built; check the counts |
| `Presolve reductions: rows r(-k); columns c(-k)` | what the search works on |
| `Objective function is integral with scale s` | plan values are multiples of $`1/s`$; the bound can be rounded |
| `Src: ...` | the legend of the source letters |
| progress row with a letter | a new incumbent, found by that source |
| progress row without a letter | a periodic report |
| `x% inactive integer columns, restarting` | root fixings; presolve runs again |
| `Status` | `Optimal` = gap within tolerance |
| `Primal bound` / `Dual bound` / `Gap` | incumbent / bound / their relative difference |
| `Nodes`, `LP iterations` | the work, with LP iterations split by purpose |

| Letter | Source | Letter | Source |
| --- | --- | --- | --- |
| `B` | branching | `R` | randomized rounding |
| `C` | central rounding | `S` | solve LP |
| `F` | feasibility pump | `T` | evaluate node |
| `H` | heuristic | `U` | unbounded |
| `I` | shifting | `X` | user solution |
| `J` | feasibility jump | `Y` | HiGHS solution |
| `L` | sub-MIP | `Z` | ZI round |
| `P` | empty MIP | `l`, `p`, `u`, `z` | trivial lower, point, upper, zero |

**Further reading:** [MathOpt `SolveResult` and `ObjectiveBounds` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (the primal and dual bound, node count and iteration counts a program reads instead of the log); [HiGHS terminology: MIP](https://ergo-code.github.io/HiGHS/dev/terminology/) (primal bound, dual bound, and the gap relative to the primal bound); [HiGHS option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`mip_rel_gap`, `mip_abs_gap`, `mip_allow_restart`, `mip_min_logging_interval` and the heuristic switches behind the log's letters); [HiGHS `HighsInfo`](https://ergo-code.github.io/HiGHS/dev/structures/structs/HighsInfo/) (`mip_dual_bound`, `mip_gap`, `mip_node_count` and `primal_dual_integral`, the report's numbers as HiGHS stores them); [HiGHS source, `HighsMipSolverData.cpp`](https://github.com/ERGO-Code/HiGHS/blob/latest/highs/mip/HighsMipSolverData.cpp) (`printDisplayLine`, the function that prints each row of the progress table); HiGHS 1.12.0 source: [`HighsMipSolver.cpp`](https://github.com/ERGO-Code/HiGHS/blob/v1.12.0/highs/mip/HighsMipSolver.cpp) (the solving report), [`HighsMipSolverData.cpp`](https://github.com/ERGO-Code/HiGHS/blob/v1.12.0/highs/mip/HighsMipSolverData.cpp) (`updatePrimalDualIntegral`, and the repair LP in `transformNewIntegerFeasibleSolution`), [`HighsPrimalHeuristics.cpp`](https://github.com/ERGO-Code/HiGHS/blob/v1.12.0/highs/mip/HighsPrimalHeuristics.cpp) (`solveSubMip` and the sub-MIP depth), [`HighsSearch.cpp`](https://github.com/ERGO-Code/HiGHS/blob/v1.12.0/highs/mip/HighsSearch.cpp) and [`HighsConflictPool.h`](https://github.com/ERGO-Code/HiGHS/blob/v1.12.0/highs/mip/HighsConflictPool.h) (how conflicts enter the pool, and the count `Confl.` prints).

## Challenges

1. Solve the five-year model with `relative_gap_tolerance=0.0` and print its log. Find the row where
   `BestSol` reaches 274,999. Which letter found it?
2. With the default tolerance, what is the largest value the best plan could have, according to this
   log? Check it against 274,999.
3. Switch presolve off and print the log. Is there still a restart?

## Design Note: Keep the Log Next to the Plan

A plan without its log cannot be explained a month later. The nightly job should write the masked
log to a file next to the plan, with the solver's version and the parameters. Then "the plan
changed" becomes a diff of two logs: different row counts mean the data changed; same counts but a
different `Gap` or `Nodes` mean the search went differently; a `Status` other than `Optimal` means it
was stopped. The section 10 lesson *Versioned input snapshots, pinned solvers and run manifests*
builds that into a run manifest.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of
the code, so the course's own files never change.

**full_log.py.** Solves the five-year model with HiGHS and prints its whole log, times masked (every
section with a log excerpt). *Try:* Solve the small portfolio instead. Predict whether the log has a
restart.

- Program: [full_log.py](src/full_log.py)

**log_and_result.py.** Reads the lettered rows of the log, recomputes their gaps, prints the same
facts from the `SolveResult`, and solves again with a zero gap tolerance (*The Root Rows*, *The
Report*). *Try:* Set `relative_gap_tolerance` to 0.001. Predict the value of the plan it returns.

- Program: [log_and_result.py](src/log_and_result.py)

**mip_log.py.** The legend as a dict, a parser for the progress rows, and the gap formula.

- Library: [mip_log.py](src/mip_log.py)

**selection.py.** The five-year model, `solve_with_log` and `mask_times`.

- Library: [selection.py](src/selection.py)
