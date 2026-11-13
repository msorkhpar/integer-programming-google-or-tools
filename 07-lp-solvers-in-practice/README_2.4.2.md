# 2.4.2 Reading an LP Solver Log

GridCap's weekly funding LP (lesson 2.4.1) is moving into a scheduled job. Most weeks nobody looks
at it. The week a planner says "the numbers look wrong" or "the run took an hour", the first thing
anyone asks for is the solver's **log**: the lines a solver writes while it works, saying what model
it received, what it removed, how each iteration went and how it ended. This lesson reads one log
from top to bottom, then two logs of runs that went wrong, then the same facts in GLOP's and PDLP's
words. GridCap is a fictional utility; its numbers are teaching data.

## The Model

The log below is the log of the funding LP of lesson 2.4.1, unchanged. Stated in full, so the log
can be checked against it line by line:

**Sets.** $`P`$ the candidate projects; $`Y`$ the plan's years, the first being $`y_0`$;
$`M \subseteq P`$ the must-do projects.

**Parameters.** $`c_{i,y}`$, what project $`i`$ spends in year $`y`$ if it starts at its earliest
start ($k, 0 in a year it is not worked); $`v_i`$, its NPV at its earliest start ($k); $`B_y`$, the
budget of year $`y`$ ($k).

**Variables.** $`0 \le f_i \le 1`$ for every $`i \in P`$, the share of project $`i`$ funded;
$`r_y \ge 0`$ for every $`y \in Y`$, the money carried out of year $`y`$, with $`r_{y_0 - 1} = 0`$.

**Objective and constraints.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} v_i\, f_i \\
\text{s.t. }& \sum_{i \in P} c_{i,y}\, f_i + r_y \le B_y + r_{y-1} && \forall y \in Y && \text{(cash}_y) \\
& f_i = 1 && \forall i \in M && \text{(must}_i)
\end{aligned}
```

On the medium portfolio, counted from the model the program built:

```text
cash rows 10, must rows 39; share variables 400, carry variables 10
```

## Ask for the Log With msg_cb, and Keep It as Lines

A solver writes nothing unless asked. MathOpt's `solve` takes a `msg_cb` argument, a function it
calls with each batch of new log lines. Passing a list's `extend` method collects the whole log,
in order, as a Python list:

```python
def solve_with_log(model: mathopt.Model, solver: mathopt.SolverType,
                   params: mathopt.SolveParameters | None = None) -> tuple[mathopt.SolveResult, list[str]]:
    """Solve, and keep every log line the solver wrote, in order, in a Python list."""
    lines: list[str] = []
    result = mathopt.solve(model, solver, params=params, msg_cb=lines.extend)
    return result, [mask_times(line) for line in lines]
```

A list is better than the terminal: a scheduled job can write it to a file next to the result,
and a test can search it. `mask_times` replaces every wall-clock time in the log with `<t>`,
because times change on every run and this page quotes the log exactly as the program printed it.
Nothing else in the log is changed. Every log below is the medium funding LP solved with
`solve_with_log`.

## The Header Says What the Solver Received

HiGHS, the course's default solver, starts by describing the model it was handed:

```text
LP funding-lp has 49 rows; 410 cols; 706 nonzeros
Coefficient ranges:
  Matrix  [1e+00, 6e+03]
  Cost    [1e+01, 6e+03]
  Bound   [1e+00, 1e+00]
  RHS     [1e+00, 4e+04]
```

Check the first line against the model before reading further: 49 rows are the 10 cash rows and
39 must rows, 410 columns (variables) are 400 shares and 10 carries. A count that does not match
what you meant to build is a bug found before any solving, such as a loop that added each row
twice. The 706 **nonzeros** are the entries of the constraint matrix that are not zero: each cash
row holds the spend of every project worked that year, plus its carry terms.

The four ranges give the smallest and largest absolute value of each kind of number, rounded to a
power of ten:

| Range | What it covers | Here |
| --- | --- | --- |
| Matrix | coefficients in the rows | 1 (a carry, a must row) to 5,990 (a project's spend) |
| Cost | objective coefficients | the NPVs, 12 to 5,875 |
| Bound | finite variable bounds other than 0 | the shares' upper bound, 1 |
| RHS | right-hand sides of the rows | 1 (must rows) to 42,870 (a budget) |

Ranges spanning a few powers of ten, as here, are normal. A matrix range like `[1e-04, 1e+07]`
is a warning: solvers compare numbers against tolerances near $`10^{-6}`$ to $`10^{-9}`$, and
coefficients eleven orders of magnitude apart make those comparisons unreliable. The usual fix is
to change units (money in $M rather than $, for instance) before building the model.

## Presolve Shrinks the Model Before Any Iteration

**Presolve** is a pass that simplifies the model before the algorithm starts: it fixes variables
whose value is forced, removes rows that say nothing new, and merges what can be merged. Section 3
covers it for integer models (lesson 3.3.2). In the log:

```text
Presolving model
10 rows, 370 cols, 603 nonzeros  <t>s
10 rows, 368 cols, 601 nonzeros  <t>s
Presolve reductions: rows 10(-39); columns 368(-42); nonzeros 601(-105)
Solving the presolved LP
```

Each line is the model's size after one round. `rows 10(-39)` reads "10 rows left, 39 removed":
the 39 must rows, since $`f_i = 1`$ fixes a variable, and a fixed variable is a number, not a
decision. 39 of the 42 removed columns are those fixed shares; the other 3 went in further
reductions (GLOP's log at the end of this lesson names its own steps). What remains is the real
problem: 10 cash rows over 368 columns. The algorithm solves that smaller LP, and **postsolve**
then maps its answer back to the original variables:

```text
Performed postsolve
Solving the original LP from the solution after postsolve
```

In the second line HiGHS solves the original model starting from that mapped-back answer, to
confirm it. Here that took no further pivots: the footer counts 14 iterations, the same 14 the
iteration lines show.

## The Iteration Lines Track the Objective and the Infeasibilities

```text
Using EKK dual simplex solver - serial
  Iteration        Objective     Infeasibilities num(sum)
          0     0.0000000000e+00 Ph1: 0(0) <t>s
         14    -2.3489812061e+05 Pr: 0(0) <t>s
```

The first line names the algorithm: dual simplex (lesson 2.4.1), run on one thread ("serial"). EKK
is the name of HiGHS's simplex code. Then one line every so often, with:

- **Iteration**: pivots so far.
- **Objective**: the objective at the current point. It is negative because HiGHS works on a
  minimization: maximizing $`\sum v_i f_i`$ is the same as minimizing $`-\sum v_i f_i`$, and the
  log shows the second. The sign flips back in the footer.
- **Infeasibilities num(sum)**: how many quantities are still wrong, and by how much in total.
  `Pr:` counts **primal infeasibilities**, rows or bounds the current point breaks. `Du:` counts
  **dual infeasibilities**, variables whose reduced cost (lesson 2.3.3) says the objective could
  still improve. `Ph1:` marks phase 1, the start-up phase that looks for a first point to work
  from. A line can carry both counts, separated by `;`.

On a run of 14 pivots there are only two lines. On a long run there are many, and the pattern to
look for is the counts falling to `0(0)` and the objective moving steadily. An objective that
stalls for thousands of iterations while the counts stay put is what a struggling run looks like.

## The Footer Is the Verdict: Status, Iterations, Objective

```text
Model name          : funding-lp
Model status        : Optimal
Simplex   iterations: 14
Objective value     :  2.3489812061e+05
P-D objective error :  0.0000000000e+00
HiGHS run time      :          <t>
WARNING: Method setLogCallback is deprecated: alternative method is setCallback
```

- **Model status** is the outcome. `Optimal` here.
- **Simplex iterations** counts all pivots. A barrier run prints `IPM iterations` instead, IPM
  standing for **interior point method** (lesson 2.4.1); the word before `iterations` names the
  kind.
- **Objective value** is in the model's own sense, so positive again: 234,898.12.
- **P-D objective error** is the relative difference between the primal objective and the dual
  objective. At an optimum they are equal (strong duality, lesson 2.3.2), so 0 means the solver's
  two views of the answer agree.
- **HiGHS run time** is the wall-clock time, masked here.
- The **WARNING** comes from the way OR-Tools 9.15 attaches itself to HiGHS's log, and it is
  printed on every run, good or bad. It says nothing about your model.

The same facts are on the `SolveResult`, and a program reads them there rather than from the log:

```python
print(f"termination: {result.termination.reason.name}")
print(f"simplex iterations: {result.solve_stats.simplex_iterations}")
print(f"objective: {result.objective_value():.4f}")
```

```text
termination: OPTIMAL
simplex iterations: 14
objective: 234898.1206
```

The log is for people, and for what the result does not carry: the size before and after
presolve, the coefficient ranges, the progress over time.

## A Failed Run's Objective Line Means Nothing

Cut 2027's budget to $1,000k, below the $3,040k the must-do projects spend that year, and solve
again:

```text
must-do spend in 2027: 3,040; budget cut to 1,000
LP funding-lp has 49 rows; 410 cols; 706 nonzeros
Coefficient ranges:
  Matrix  [1e+00, 6e+03]
  Cost    [1e+01, 6e+03]
  Bound   [1e+00, 1e+00]
  RHS     [1e+00, 4e+04]
Presolving model
10 rows, 330 cols, 558 nonzeros  <t>s
Problem status detected on presolve: Infeasible
Model name          : funding-lp
Model status        : Infeasible
Objective value     :  0.0000000000e+00
HiGHS run time      :          <t>
WARNING: Method setLogCallback is deprecated: alternative method is setCallback
termination: INFEASIBLE; has a feasible solution: False
```

Presolve found the contradiction before any iteration, so there is no iteration line and no
iteration count in the footer. Then the trap: the footer still prints `Objective value : 0.0`.
There is no plan, so there is no objective; the line is printed anyway. A script that reads the
objective line without the status line reports a plan worth $0.

The second run makes a common modelling slip: a new project's share is added to the objective
with coefficient 900, but its upper bound of 1 and its spend in the cash rows are both forgotten.
Nothing limits it:

```text
Problem status detected on presolve: Primal infeasible or unbounded
Solving the original LP with primal simplex to determine infeasible or unbounded
Using EKK primal simplex solver
  Iteration        Objective     Infeasibilities num(sum)
          0    -6.1239605605e-04 Ph1: 39(6352); Du: 39(39) <t>s
         39     2.7463000000e+04 Pr: 0(0); Du: 362(2754.69) <t>s
Using EKK primal simplex solver
  Iteration        Objective     Infeasibilities num(sum)
         39     2.7462927508e+04 Pr: 0(0); Du: 362(299134) <t>s
         47     1.9614404655e+05 Pr: 0(0); Du: 184(48742.1) <t>s
Model name          : funding-lp
Model status        : Unbounded
Simplex   iterations: 47
Objective value     :  1.9614404655e+05
P-D objective error :               inf
HiGHS run time      :          <t>
WARNING: Method setLogCallback is deprecated: alternative method is setCallback
termination: UNBOUNDED; has a feasible solution: True
```

**Unbounded** means the objective can grow without limit while every row holds. Presolve could only
tell that the model was infeasible *or* unbounded, so HiGHS ran primal simplex to decide which. Its
lines show it: primal infeasibilities reach `0(0)` (it found points that keep every row), while
dual infeasibilities never do (the objective can always still improve). The footer's objective,
196,144, is just where the solver stopped walking up an endless direction, and the P-D error is
`inf` because there is no finite dual objective. The result even holds a feasible point, which
is why the status, not the presence of a point or an objective, decides what a run means.

The rule for logs is the rule for results (lesson 1.1.3): read the status first. Only `Optimal`
makes the objective line an answer.

<!-- practice 1 -->

## GLOP and PDLP Logs Carry the Same Facts in Other Words

Every solver's log has a header, a presolve report, progress lines and a verdict, written in its
own format. GLOP, on the same LP:

```text
Initial problem: 49 rows, 410 columns, 706 entries with magnitude in [1.000000e+00, 5.990000e+03]
Objective stats: 400 non-zeros, range [1.200000e+01, 5.875000e+03]
Bounds stats: 488 non-zeros, range [1.000000e+00, 4.287000e+04]
Parameters: log_search_progress: true log_to_stdout: false
Starting presolve...
SingletonPreprocessor                        : 10(-39) rows, 409(-1) columns, 666(-40) entries. (<t>s)
FixedVariablePreprocessor                    : 10(-39) rows, 370(-40) columns, 603(-103) entries. (<t>s)
Reached fixed point after presolve pass #2
ProportionalColumnPreprocessor               : 10(-39) rows, 368(-42) columns, 601(-105) entries. (<t>s)
ScalingPreprocessor                          : 10(-39) rows, 368(-42) columns, 601(-105) entries. (<t>s)
Presolved problem: 10 rows, 368 columns, 601 entries with magnitude in [2.343434e-01, 1.000000e+00]
```

The same 49 rows, 410 columns and 706 entries, and the same reduction to 10 rows and 368 columns,
now step by step: a row with a single variable (each must row) fixes that variable, the fixed
variables leave, and columns that are multiples of one another are merged. Then
**scaling**: GLOP multiplies rows and columns by factors so that the coefficients sit between 0.23
and 1, which keeps its tolerances meaningful. Scaling changes numbers, never the model's size: the
row and column counts stay 10 and 368. GLOP's progress lines report the objective at some of its pivots,
and its verdict is at the very end:

```text
status: OPTIMAL
objective: 234898
iterations: 191
time: <t>
deterministic_time: 0.000442316
```

`deterministic_time` is a measure of work that, unlike `time`, is the same on every run of the
same model and parameters, so it is the one to compare between runs.

PDLP's progress lines are a table, one row every 64 iterations here:

```text
 iter# kkt_pass   time | rel_prim_res rel_dual_res      rel_gap |   prim_resid   dual_resid      obj_gap |     prim_obj     dual_obj |  prim_var_l2  dual_var_l2
     0      0.0    <t> |  5.05757e-05     0.999960      0.00000 |      6.24500      24886.7      0.00000 |     -0.00000     -0.00000 |      0.00000      0.00000
    64     65.0    <t> |  9.22564e-05  2.74251e-05 -1.11753e-05 |      11.3917     0.682546     -5.25024 |      234901.      234906. |      22738.0      3156.32
   128    129.0    <t> |  0.000130199  5.59101e-07  2.60708e-05 |      16.0767    0.0139147      12.2483 |      234910.      234898. |      23099.2      3156.32
   192    193.0    <t> |  4.02367e-06  1.07714e-17 -2.06312e-07 |     0.496835  2.68076e-13   -0.0969249 |      234898.      234898. |      23089.0      3156.32
   256    257.0    <t> |  3.92304e-08  3.21960e-09 -3.85560e-08 |   0.00484410  8.01284e-05   -0.0181135 |      234898.      234898. |      23088.3      3156.32
Termination reason: TERMINATION_REASON_OPTIMAL
```

The first two columns count work. `iter#` is the iteration number. **`kkt_pass`** counts passes
through the constraint matrix since the start: one pass is one product with the matrix and one with
its transpose (for a quadratic objective, also one with its matrix), the work of one PDLP
iteration (lesson 2.4.1). It is a decimal because a pass over part of the matrix counts as a
fraction. Here it runs one ahead of the iteration count (65.0 at iteration 64, 257.0 at 256), and it
is the fairer measure of PDLP's work between runs, since `time` depends on the machine.

The three columns after `time` are the three measures PDLP stops on (lesson 2.4.1), each relative to
the size of the data: **rel_prim_res**, how much the rows are broken; **rel_dual_res**, how far
the prices are from satisfying their own conditions; and **rel_gap**, the gap between the primal
and dual objectives. The gap can be negative, so it is its size that has to be small. PDLP checks
the three every so often (every 64 iterations in this run) and stops at the first check where all
three are below its tolerance, here iteration 256. The middle block
repeats the three in absolute terms: `prim_resid` is not zero at the end (0.0048 in the last table row), which is the sliver
by which PDLP's point breaks rows and the reason its objective sat just above the simplex one in
lesson 2.4.1.

After the verdict, PDLP's log ends with one more row in the same format as the table, under
`Final solution stats`:

```text
Termination reason: TERMINATION_REASON_OPTIMAL
Solution point type: POINT_TYPE_CURRENT_ITERATE
Final solution stats:
 iter# kkt_pass   time | rel_prim_res rel_dual_res      rel_gap |   prim_resid   dual_resid      obj_gap |     prim_obj     dual_obj |  prim_var_l2  dual_var_l2
   256    257.0    <t> |  1.57843e-07  3.71708e-09  2.67127e-08 |    0.0194902  9.25094e-05    0.0125496 |      234898.      234898. |      23088.4      3156.32
```

It repeats its own header, then gives the measures of the point PDLP actually returns. The line
`Solution point type` names that point: the current iterate, the last $`(x, y)`$ pair. PDLP's log
format documents that these final stats are measured on the original problem, whatever rescaling or
presolve was used. The progress rows can describe a different candidate point (the format lists
several, among them the average of the iterates since the last restart), which is why this row's
measures differ from the table's row 256 although the iteration is the same. All three are still
below $`10^{-6}`$. A program that parses the log meets this row like any progress row: it starts
with an iteration number, and it is the last one.

| Fact | HiGHS | GLOP | PDLP |
| --- | --- | --- | --- |
| size received | `LP ... has 49 rows; 410 cols; 706 nonzeros` | `Initial problem: 49 rows, 410 columns, 706 entries` | `There are 410 variables, 49 constraints, ...` |
| size after presolve | `Presolve reductions: rows 10(-39); ...` | `Presolved problem: 10 rows, 368 columns` | (no presolve report) |
| progress | `Iteration  Objective  Infeasibilities` lines | `Primal optimization phase, iteration # ...` | `iter# ... rel_prim_res rel_dual_res rel_gap` table |
| outcome | `Model status : Optimal` | `status: OPTIMAL` | `Termination reason: TERMINATION_REASON_OPTIMAL` |
| work done | `Simplex iterations: 14` | `iterations: 191` | the last `iter#` |

<!-- practice 2 -->

## Summary

- **Ask for the log with `msg_cb`, and keep it as lines.** A list can be saved with the result and
  searched by a test.
- **The header says what the solver received.** Check the sizes against the model; read the
  coefficient ranges for scaling trouble.
- **Presolve shrinks the model before any iteration.** Fixed variables and redundant rows leave
  first; postsolve maps the answer back.
- **The iteration lines track the objective and the infeasibilities.** `Pr:` counts broken rows,
  `Du:` counts possible improvements; both reach `0(0)` at an optimum.
- **The footer is the verdict.** Status first; only `Optimal` makes the objective line an answer.
- **GLOP and PDLP say the same things in other words.** PDLP stops when relative primal residual,
  dual residual and gap are all small.

## Reference

| HiGHS line | Meaning |
| --- | --- |
| `LP <name> has R rows; C cols; N nonzeros` | the model as received |
| `Matrix / Cost / Bound / RHS [lo, hi]` | smallest and largest absolute values of each kind |
| `Presolve reductions: rows r(-k); columns c(-j)` | r rows left, k removed; c columns left, j removed |
| `Problem status detected on presolve: ...` | presolve settled the outcome; no iterations follow |
| `Ph1: / Pr: / Du: n(s)` | phase 1 / primal / dual infeasibilities: count n, total s |
| `Model status : ...` | the outcome: Optimal, Infeasible, Unbounded, ... |
| `Simplex iterations: n`, `IPM iterations: n` | work done, by kind |
| `Objective value : v` | an answer only when the status is Optimal |
| `P-D objective error : e` | relative primal-dual objective difference; 0 at an optimum |

| MathOpt | Gives |
| --- | --- |
| `mathopt.solve(model, solver, msg_cb=lines.extend)` | the log, as a list of lines |
| `result.termination.reason` | the status |
| `result.solve_stats.simplex_iterations` (and `barrier_`, `first_order_`) | the work done |
| `result.has_primal_feasible_solution()` | whether the result holds an allowed point |

**Further reading:** [MathOpt `solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py) (the `msg_cb` argument of `solve`, which hands back the underlying solver's log line by line); [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (the tolerances behind "optimal", why badly scaled data defeats them, and why a solver's checks on the presolved model can disagree with the original, GLOP's `IMPRECISE`); [PDLP (OR-Tools)](https://developers.google.com/optimization/lp/pdlp_math) (the rescaling PDLP applies and the residuals and gap its log reports); [PDLP `solve_log.proto`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/solve_log.proto) (what a KKT matrix pass is, the point types, and the final solution stats measured on the original problem); [HiGHS, Solvers](https://ergo-code.github.io/HiGHS/dev/solvers/) (the dual simplex the log names as its default, and when interior point runs crossover).

## Challenges

1. A colleague's HiGHS header says `Matrix [1e-03, 1e+08]`. Their costs are in dollars and their
   hours in minutes. What do you change, and what range would you expect after?
2. The funding LP's must rows were written as variable bounds instead, `add_variable(lb=1, ub=1)`.
   Predict the header's row count and the `Presolve reductions` line.
3. A nightly job greps the HiGHS log for `Objective value` and stores the number. Write the two
   lines of Python that make it safe.

## Design Note: Keep the Log With the Result

A log printed to a terminal is gone when the job ends, and the week someone asks why a number
moved is never the week the job ran. Saving the list `solve_with_log` returns next to the result
costs a few kilobytes and answers the first three questions of any investigation: what model the
solver received, what it removed, and how it ended.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**solver_log.py.** `solve_with_log` and `mask_times`, used by the other programs. It prints nothing.

- Library: [solver_log.py](src/solver_log.py)

**highs_log.py.** The full HiGHS log of the medium funding LP, then the same facts read from the
result (*The Header*, *Presolve*, *The Iteration Lines*, *The Footer*). *Try:* Pass
`mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.BARRIER)` to `solve_with_log`. Predict
which footer line changes its first word.

- Program: [highs_log.py](src/highs_log.py)

**infeasible_log.py.** An infeasible run and an unbounded run, with their logs (*A Failed Run's
Objective Line Means Nothing*). *Try:* Give `f_NEW` an upper bound of 1 and run it. Predict the
status and whether the objective rises by 900.

- Program: [infeasible_log.py](src/infeasible_log.py)

**glop_pdlp_logs.py.** The GLOP and PDLP logs of the same LP (*GLOP and PDLP Logs*). *Try:* Pass
`mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX)` for GLOP. Predict which
log lines change.

- Program: [glop_pdlp_logs.py](src/glop_pdlp_logs.py)
