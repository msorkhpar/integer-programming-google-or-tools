# 11.4.1 Why First-Order LP Methods Suit a GPU: PDHG and PDLP

GridCap's analysts solve the LP relaxation of the capital plan many times a night: once per
scenario, per region, per budget case. The relaxation is the plan with "fund it or not" loosened
to "fund any share from 0 to 1" (lesson 3.1.1), and its optimum is an upper bound on what any real
plan can be worth. A colleague asks whether a **GPU** (graphics processing unit: a card with
thousands of small arithmetic cores that run the same instruction on many numbers at once) would
make those solves faster. The answer depends on the algorithm. Simplex and interior point, the
methods of lessons 2.2.2 and 2.4.1, spend their time solving systems of linear equations, and that
work does not spread well over thousands of cores. A **first-order method** spends its time on
matrix-vector products, and those do. This lesson shows the first-order method HiGHS, cuOpt and
OR-Tools share, PDHG, on GridCap's numbers; what PDLP adds to it; and what it gives up: it stops at
a tolerance, not at a vertex. GridCap is a fictional utility; its numbers are teaching data.

Lesson 2.4.1 met PDHG on a two-variable LP with rows of the form $`Ax \le b`$. Here the rows are
GridCap's, some of them equalities, and the program runs on the matrix as a whole.

## The Model

The LP relaxation of GridCap small's start-year model (lesson 6.4.1, without its parent-child
rows), built by `lps.gridcap_timing("small")`:

**Sets.** $`P`$ the 40 projects; $`Y`$ the years 2027 to 2031; $`T_i \subseteq Y`$ the years
project $`i`$ may start in; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the
alternative groups.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`s_{i,t,y}`$, what project $`i`$ started in $`t`$ spends in year $`y`$ ($k); $`B_y`$, the budget
of year $`y`$ ($k).

**Variables.** $`0 \le x_{i,t} \le 1`$ for every $`i \in P`$, $`t \in T_i`$: the share of project
$`i`$ started in year $`t`$ (80 variables).

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{i \in P} \sum_{t \in T_i} s_{i,t,y}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The code names each row by its label: `once_P001`, `must_P003`, `alt_G001`, `budget_2029`. The 47
rows and 80 columns hold 204 nonzero coefficients.

The module's programs keep a model as a plain dict (objective, rows in compressed sparse row form,
row bounds, variable bounds), so HiGHS, OR-Tools' PDLP and cuOpt all read the same numbers. In that
form every row is two-sided: $`\ell^c_r \le a_r x \le u^c_r`$, with $`\ell^c_r = -\infty`$ for a
$`\le`$ row and $`\ell^c_r = u^c_r = 1`$ for a must row.

## Every LP Is a Saddle Point: the Plan Maximises, the Prices Minimise

Write the model as $`\max c^\top x`$ subject to $`\ell^c \le Ax \le u^c`$ and
$`\ell \le x \le u`$. Give each row $`r`$ one price $`y_r`$ of any sign: $`y_r > 0`$ prices the row's
upper side ($`a_r x \le u^c_r`$), $`y_r < 0`$ its lower side. With $`[y]_+ = \max(y, 0)`$ and
$`[y]_- = \max(-y, 0)`$, the **Lagrangian** is

```math
L(x, y) = c^\top x - y^\top A x + \sum_r \bigl( u^c_r\,[y_r]_+ - \ell^c_r\,[y_r]_- \bigr)
```

For a price $`y_r \ge 0`$ the row's term is $`y_r (u^c_r - a_r x)`$, its slack valued at the price,
exactly lesson 2.4.1's $`y^\top (b - Ax)`$. For $`y_r \le 0`$ it is $`|y_r| (a_r x - \ell^c_r)`$,
the slack above the lower side. A row with no lower side ($`\ell^c_r = -\infty`$) can only take a
price $`y_r \ge 0`$, and a row with no upper side only $`y_r \le 0`$.

The optimal plan and the optimal prices form a **saddle point** of $`L`$:

```math
\max_{\ell \le x \le u} \; \min_{y} \; L(x, y)
```

The plan $`x`$ makes $`L`$ as large as it can, the prices make it as small as they can, and at the
saddle point neither can gain by moving alone. The inner minimum is $`c^\top x`$ when $`x`$ keeps
every row (the best price on a kept row is 0) and $`-\infty`$ when it breaks one, so the outer
maximum is the LP. The OR-Tools PDLP documentation writes the same problem with a minimisation
outside, the objective's sign flipped, and $`K = -A`$; the content is the same.

## A PDHG Iteration Is Two Matrix-Vector Products and Two Clips

**PDHG**, the primal-dual hybrid gradient method, moves the plan up its gradient and the prices
down theirs, in turn. With step sizes $`\tau, \sigma > 0`$, one iteration is

```math
\begin{aligned}
x^{k+1} &= \operatorname{clip}_{[\ell,\,u]}\bigl( x^k + \tau\,(c - A^\top y^k) \bigr) \\
v &= y^k + \sigma\, A\,(2x^{k+1} - x^k) \\
y^{k+1}_r &= \max\bigl(0,\; v_r - \sigma u^c_r\bigr) + \min\bigl(0,\; v_r - \sigma \ell^c_r\bigr) && \forall r
\end{aligned}
```

The first line is lesson 2.4.1's primal step: $`c - A^\top y`$ is each variable's reduced cost at
prices $`y`$, and the clip puts each variable back between its bounds. The second and third lines
are the dual step at the look-ahead point $`2x^{k+1} - x^k`$. The third line is the clip for a
two-sided row: if the plan overshoots the upper side, the first term raises the upper price; if it
falls below the lower side, the second term makes the price negative; if it sits between, both
terms shrink toward 0. When $`\ell^c_r = -\infty`$ the second term is always 0, and the line becomes
2.4.1's $`\max(0, \cdot)`$. `pdhg_gridcap.py` writes it with NumPy and SciPy, on the whole matrix:

```python
        x_new = np.clip(x + tau * (c - A.T @ y), lo, hi)                          # primal: up the gradient, clip
        v = y + sigma * (A @ (2 * x_new - x))                                      # dual: at the look-ahead point
        y = np.maximum(0.0, v - sigma * row_hi) + np.minimum(0.0, v - sigma * row_lo)   # clip by the row's sides
        x = x_new
```

```text
A: 47 x 80, 204 nonzeros, entries from 1 to 5680; simplex optimum 26,587.4415
work per iteration: 2 x 204 multiply-adds for A x and A'y, plus 127 clips; no factorization
```

Constant steps converge when $`\tau \sigma \lVert A \rVert_2^2 \le 1`$, where $`\lVert A \rVert_2`$ is
the matrix's largest singular value (the PDLP paper cites this condition). The program uses
$`\tau = \sigma = 0.9 / \lVert A \rVert_F`$; the Frobenius norm (the square root of the sum of all
squared entries) is never smaller than $`\lVert A \rVert_2`$, so the condition holds.

<!-- practice 1 -->

## Those Products Are What a GPU Does Best

An iteration reads each nonzero of $`A`$ twice, once for $`A x`$ and once for $`A^\top y`$, and
then clips two vectors element by element. Every row of $`A x`$ is a separate sum that needs
nothing from the other rows, and every clip is separate too. That is the shape of work a GPU is
built for: thousands of cores each take a few rows, with no core waiting for another, and the
speed is set by how fast the card's memory streams the matrix past them. PDHG never solves for the
prices exactly: each iteration moves them by one dual step (the second and third lines of the
iteration above), and the next iteration starts from there.

Simplex and interior point do different work. A simplex iteration solves linear systems with the
current basis, and an interior point iteration solves one with a matrix built from $`A`$ and the
current point (lesson 2.4.1). Both **factorize** a matrix (split it into triangular factors, the
LU or Cholesky factorization), and a factorization is a chain of steps where each one needs the
ones before it, and it can fill zero entries with nonzeros, so it needs more memory than $`A`$.
That chain does not split cleanly into thousands of independent pieces. A first-order method never
factorizes anything: it needs memory for $`A`$ and a few vectors, and nothing else. The PDLP paper
gives this as the reason it scales, since its core operation is the matrix-vector product, and the
cuPDLP papers built GPU versions on it (lesson 11.4.3 measures two of them).

## Plain PDHG Stalls on GridCap's Numbers; Rescaling Rescues It

The bare iteration above, run 100,000 times on GridCap small, and then again after rescaling the
rows and columns:

```text
as built: tau = sigma = 4.66e-05
  iteration     objective   rel. error  max violation
         10   28,383.9184     6.8e-02        1.9e+03
        100   29,578.0375     1.1e-01        3.2e+01
      1,000   30,102.3582     1.3e-01        3.0e+00
     10,000   30,128.5125     1.3e-01        3.0e+00
    100,000   30,124.1275     1.3e-01        3.0e+00
rescaled: tau = sigma = 7.06e-02
  iteration     objective   rel. error  max violation
         10   35,847.4012     3.5e-01        4.9e+03
        100   26,209.4291     1.4e-02        3.1e+01
      1,000   26,576.2338     4.2e-04        6.3e-03
     10,000   26,594.5823     2.7e-04        2.9e+00
    100,000   26,587.3141     4.8e-06        5.9e-05
```

As built, the method is stuck: after 100,000 iterations the plan is 13% above the optimum and
still breaks a row by 3.0. The reason is in the first output line: the entries of $`A`$ run from 1
(the once and must rows) to 5,680 (a budget row). The step sizes must suit the largest entries, so
they are tiny ($`4.66 \times 10^{-5}`$). A price moves by $`\sigma`$ times its row's breach per
iteration, about $`1.4 \times 10^{-4}`$ for the breach of 3.0 in the table, so the prices crawl
and the plan with them. After rescaling the steps are 1,500 times larger. Raising the steps that
far by hand is no cure: with the entries as built, steps 1,500 times larger break the convergence
condition above many times over. Rescaling shrinks the large entries, so that the condition itself
allows the larger steps.

**Rescaling** (also called **diagonal preconditioning**) fixes the units. It multiplies row $`j`$
by a number $`r_j`$ and column $`i`$ by a number $`s_i`$, so that the rescaled matrix is
$`\operatorname{diag}(r)\, A \, \operatorname{diag}(s)`$ and every row's and column's largest
entry is near 1, solves the rescaled LP for $`x' = x / s`$, and maps the answer back. The Ruiz
method does it by repeatedly dividing by the square root of each row's and column's largest entry:

```python
def ruiz(A, rounds: int = 10):
    """Row and column scalings r, s that bring every row's and column's largest |entry| near 1."""
    r, s = np.ones(A.shape[0]), np.ones(A.shape[1])
    for _ in range(rounds):
        B = scipy.sparse.diags(r) @ A @ scipy.sparse.diags(s)
        r /= np.sqrt(abs(B).max(axis=1).toarray().ravel())
        s /= np.sqrt(abs(B).max(axis=0).toarray().ravel())
    return r, s
```

```text
rescaled: entries from 0.24 to 1.00
```

The same iteration on the rescaled LP reaches a relative error of $`4.2 \times 10^{-4}`$ in 1,000
iterations and $`4.8 \times 10^{-6}`$ in 100,000. Rescaling changes the units, not the LP: the plan
mapped back is a plan of the original model, and the row bounds and objective scale with it. It is
still slow, and it wanders (at 10,000 iterations the violation is back up to 2.9), which is what
PDLP's other additions are for.

## PDLP Adds Restarts, Rescaling, Adaptive Steps and a Primal Weight

**PDLP** (primal-dual hybrid gradient for LP) is PDHG with enhancements that make it practical.
The PDLP paper names diagonal preconditioning, presolving, adaptive step sizes and adaptive
restarting, and its algorithm also updates a primal weight. OR-Tools' parameters
(`PrimalDualHybridGradientParams` in `solvers.proto`) let you switch each one off:

- **Rescaling.** Ruiz rescaling (`l_inf_ruiz_iterations`, 5 rounds by default) and then a rescaling
  by the rows' and columns' 2-norms (`l2_norm_rescaling`, on), as in the section above.
- **Adaptive restarts** (`restart_strategy`, `ADAPTIVE_HEURISTIC`). PDHG's average of recent
  iterates is often closer to the optimum than its last iterate, but averaging over a long run
  slows it down. PDLP periodically restarts the method from the better of the two, judged by a
  measure of distance from optimality, which keeps the progress and drops the slow tail.
- **Adaptive step sizes** (`linesearch_rule`, `ADAPTIVE_LINESEARCH_RULE`). Instead of the safe but
  pessimistic $`0.9 / \lVert A \rVert`$, PDLP tries a larger step, checks a condition from the
  convergence theory, and reduces it and tries again only if the step fails it.
- **Primal weight** $`\omega`$ (`primal_weight_update_smoothing`). The steps are
  $`\tau = \eta / \omega`$ and $`\sigma = \eta\,\omega`$, so $`\omega`$ trades how far the plan moves
  against how far the prices move. PDLP starts it from the ratio of the objective's norm to the
  bounds' norm and updates it at each restart, so that neither side lags.
- **Presolve** (`presolve_options.use_glop`, off by default in OR-Tools): simplifications before
  the method starts.

`pdlp_gridcap.py` solves GridCap small with OR-Tools' PDLP through its direct API (the one
OR-Tools' `simple_pdlp_program.py` sample uses), once with the defaults and once with each feature
switched off:

```python
    features = {
        "PDLP defaults": {},
        "no restarts": {"restart_strategy": solvers_pb2.PrimalDualHybridGradientParams.NO_RESTARTS},
        "no rescaling": {"l_inf_ruiz_iterations": 0, "l2_norm_rescaling": False},
        "constant step size": {"linesearch_rule": solvers_pb2.PrimalDualHybridGradientParams.CONSTANT_STEP_SIZE_RULE},
        "fixed primal weight": {"primal_weight_update_smoothing": 0.0},
    }
```

```text
What PDLP adds to plain PDHG: iterations to 1e-6 with one feature switched off (limit 100,000)
PDLP defaults            576 iterations  OPTIMAL
no restarts             7616 iterations  OPTIMAL
no rescaling          100000 iterations  ITERATION_LIMIT
constant step size      1024 iterations  OPTIMAL
fixed primal weight      640 iterations  OPTIMAL
```

With everything on, PDLP reaches the tolerance in 576 iterations, against the 100,000 that plain
PDHG did not finish. Each feature's share, on this model: without rescaling it does not finish
either (the stall of the section above); without restarts it needs 13 times the iterations; a
constant step needs 1.8 times; a frozen primal weight costs 11% more. These are one model's
numbers; the PDLP paper measures each feature over hundreds of LPs.

None of these features adds a factorization. Each iteration is still matrix-vector products and
clips, plus a few vector norms, so PDLP keeps the property that puts it on a GPU.

## A First-Order Method Stops at a Tolerance, Not at a Vertex

Simplex ends on a **vertex** with a **basis**: an exact corner of the feasible region, with the
list of variables that define it (lessons 2.2.1 and 2.2.2). PDLP has neither. It stops when its point is
close enough, by three measures from the PDLP paper, each relative to the size of the data:

```math
\begin{aligned}
\lvert \text{dual objective} - \text{primal objective} \rvert &\le \varepsilon\,\bigl(1 + \lvert \text{dual objective} \rvert + \lvert \text{primal objective} \rvert\bigr) && \text{(gap)} \\
\lVert \text{how far } x \text{ breaks the rows} \rVert_2 &\le \varepsilon\,\bigl(1 + \lVert \text{row bounds} \rVert_2\bigr) && \text{(primal)} \\
\lVert \text{reduced costs of the wrong sign} \rVert_2 &\le \varepsilon\,\bigl(1 + \lVert c \rVert_2\bigr) && \text{(dual)}
\end{aligned}
```

OR-Tools sets $`\varepsilon`$ in `simple_optimality_criteria` (both the relative and the absolute
part default to $`10^{-6}`$); `ortools_pdlp` in `lps.py` sets both to the tolerance it is given:

```python
    criteria = params.termination_criteria.simple_optimality_criteria
    criteria.eps_optimal_relative = eps
    criteria.eps_optimal_absolute = eps
```

```text
HiGHS simplex (CPU): Optimal, objective 26587.441510, 25 iterations, 72 of 80 values exactly 0 or 1

PDLP (CPU, 1 thread): where it stops is set by the tolerance
tolerance  iterations   objective      rel. error  max violation  values exactly 0 or 1
    1e-02          64    26607.7410     7.6e-04        2.6e+01                     69
    1e-04         192    26587.6557     8.1e-06        1.4e-01                     69
    1e-06         576    26587.4632     8.2e-07        1.2e-02                     70
    1e-08         896    26587.4413     8.7e-09        6.3e-08                     70
```

Read it row by row:

- **The tolerance sets the cost.** Each factor of 100 in accuracy costs more iterations: 64, 192,
  576, 896. The answer is as accurate as asked and no more.
- **The relative error tracks the tolerance.** At every row the objective is within the tolerance
  of the simplex optimum, relatively.
- **"Optimal" allows broken rows.** At $`10^{-6}`$ the plan breaks a row by 0.012, in $k. That is
  allowed: the primal measure compares the breach with the size of all the row bounds together,
  and GridCap's budgets run to thousands. A planner who reads "optimal" as "keeps every budget to
  the dollar" is wrong at every tolerance above. At $`10^{-8}`$ the breach is $`6.3 \times 10^{-8}`$.
- **It is not the vertex.** Simplex ends with 72 of the 80 values exactly 0 or 1; PDLP, even at
  $`10^{-8}`$, has 70. Its point is near the optimal face, not on its corner, and it returns no
  basis. A model that needs a basis (for the warm starts of lesson 4.3.3, or for sensitivity ranges
  read from it) needs a simplex solve, or a crossover step that some solvers run after PDLP to
  move to a vertex.

The trace shows how it gets there:

```text
PDLP at 1e-8, every 64th iteration (its average iterate):
iteration   primal obj.     dual obj.   primal res.  dual res.
        0        -0.000        -0.000      2.0e+00    1.2e+04
       64     26615.611     26583.280      2.7e+01    3.2e+01
      128     26570.822     26587.898      4.9e-03    6.3e-01
      192     26587.656     26587.555      2.1e-01    6.5e-01
      256     26585.635     26587.466      5.2e-04    2.7e-01
      320     26588.463     26587.441      8.5e-01    4.4e-03
      384     26587.766     26587.451      2.7e-01    4.4e-02
      448     26587.483     26587.443      3.8e-02    1.4e-02
```

The primal and dual objectives close in on each other from both sides, but not steadily: the
primal residual (how far the rows are broken) falls to $`5.2 \times 10^{-4}`$ at iteration 256 and
rises to 0.85 at 320. The residuals are not monotone, which is why PDLP checks all three measures
together, and why "how many iterations" has no answer before the run.

<!-- practice 2 -->

## Summary

- **Every LP is a saddle point: the plan maximises, the prices minimise.** One price per row, of
  either sign for a two-sided row; at the saddle point neither side gains by moving.
- **A PDHG iteration is two matrix-vector products and two clips.** The dual clip for a two-sided
  row is $`\max(0, v - \sigma u^c) + \min(0, v - \sigma \ell^c)`$.
- **Those products are what a GPU does best.** Each row's sum is independent, and there is no
  factorization to chain the work or fill the memory.
- **Plain PDHG stalls on GridCap's numbers; rescaling rescues it.** As built, 13% off after 100,000
  iterations; rescaled, $`4.8 \times 10^{-6}`$.
- **PDLP adds restarts, rescaling, adaptive steps and a primal weight.** 576 iterations to
  $`10^{-6}`$ with all of them; without rescaling, not done in 100,000.
- **A first-order method stops at a tolerance, not at a vertex.** Relative criteria on the gap and
  the two residuals; rows broken by up to 0.012 at $`10^{-6}`$; no basis.

## Reference

| Term | Meaning here |
| --- | --- |
| first-order method | a method whose steps use only gradients (here: products with $`A`$ and $`A^\top`$), never a factorization |
| PDHG | primal-dual hybrid gradient: a primal step up $`c - A^\top y`$, a dual step at $`2x^{k+1} - x^k`$, each clipped |
| PDLP | PDHG with rescaling, adaptive restarts, adaptive steps, a primal weight and optional presolve |
| tolerance $`\varepsilon`$ | the relative accuracy at which PDLP stops: gap, primal and dual residuals |

| OR-Tools PDLP parameter | Default | Off |
| --- | --- | --- |
| `restart_strategy` | `ADAPTIVE_HEURISTIC` | `NO_RESTARTS` |
| `l_inf_ruiz_iterations`, `l2_norm_rescaling` | 5, true | 0, false |
| `linesearch_rule` | `ADAPTIVE_LINESEARCH_RULE` | `CONSTANT_STEP_SIZE_RULE` |
| `primal_weight_update_smoothing` | 0.5 | 0.0 (frozen) |
| `termination_criteria.simple_optimality_criteria` | $`10^{-6}`$, $`10^{-6}`$ | |
| `num_threads` | 1 | |

**Further reading:** OR-Tools,
[PDLP: the math](https://developers.google.com/optimization/lp/pdlp_math)
(the primal and dual problems, the saddle-point form with $`K = -A`$, rescaling by diagonal
matrices); the OR-Tools sample
[`simple_pdlp_program.py`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/samples/simple_pdlp_program.py)
(the direct PDLP API this lesson's `ortools_pdlp` uses); the parameter comments in
[`solvers.proto`](https://github.com/google/or-tools/blob/stable/ortools/pdlp/solvers.proto)
(restart strategies, line search rules, Ruiz and 2-norm rescaling, the primal weight, termination
criteria and their defaults); Applegate et al.,
[Practical Large-Scale Linear Programming using Primal-Dual Hybrid Gradient](https://arxiv.org/abs/2106.04756)
(the PDLP paper: the saddle point and PDHG update, the step condition, adaptive steps and restarts,
primal weight, Ruiz and Pock-Chambolle preconditioning, the termination criteria, and the
matrix-vector product as the reason PDLP scales).

## Challenges

1. In `pdhg_gridcap.py`, change the equal steps to $`\tau = 0.9 / (\omega \lVert A \rVert_F)`$ and
   $`\sigma = 0.9\,\omega / \lVert A \rVert_F`$ with $`\omega = 0.1`$ and with $`\omega = 10`$ on the
   rescaled LP. Predict which converges faster, and why the primal weight is a ratio.
2. Switch off two PDLP features at once in `pdlp_gridcap.py`, restarts and adaptive steps. Predict
   whether the iterations multiply (13 × 1.8) or not.
3. A planner asks for "the LP bound to the dollar" from PDLP. Which tolerance would you set, and
   what would you tell them about the 47 rows?

## Design Note: One Model Format for Every Solver

Every program of this module builds its model once, as a dict of plain lists, and hands the same
numbers to HiGHS, to OR-Tools' PDLP (through SciPy's sparse matrices) and to cuOpt (as JSON, in a
separate process). A comparison between solvers is then a comparison between algorithms and
devices, never between two model builders that might disagree on a row. `violation` checks any
solver's answer against those same lists, so no solver grades its own work.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Both run on the CPU, with or without a GPU.

**pdhg_gridcap.py.** Plain PDHG on GridCap small's LP relaxation, as built and after Ruiz
rescaling (*A PDHG Iteration*, *Plain PDHG Stalls*). *Try:* Change `rounds` in `ruiz` from 10 to
1 and predict the relative error after 1,000 iterations.

**pdlp_gridcap.py.** OR-Tools' PDLP on the same LP at four tolerances, its trace, and each feature
switched off (*PDLP Adds*, *A First-Order Method Stops at a Tolerance*). *Try:* Turn on
`presolve_options.use_glop` through `tweaks` and predict whether the iterations to $`10^{-6}`$
change.

- Program: [pdhg_gridcap.py](src/pdhg_gridcap.py)
- Program: [pdlp_gridcap.py](src/pdlp_gridcap.py)
- Library: [lps.py](src/lps.py)
