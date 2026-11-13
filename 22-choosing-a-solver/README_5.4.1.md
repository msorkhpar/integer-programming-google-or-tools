# 5.4.1 The Landscape: Gurobi, CPLEX, Xpress, HiGHS, SCIP, CBC, CP-SAT

GridCap's architecture review meets before the planning service goes to production. One reviewer
asks the question every optimization team hears sooner or later: "Why HiGHS? Everyone says Gurobi is
the fastest. Shouldn't we just buy it?" Nobody in the room can answer with evidence. This module
builds that evidence. It surveys the solvers (this lesson), measures them honestly (5.4.2), prices
and packages them (5.4.3), and writes the recommendation the reviewer asked for (5.4.4). GridCap is
a fictional utility, and its numbers are teaching data.

This lesson maps the field: who makes each of the seven solvers in the title, what each one solves,
how you reach it from Python, and which of them you can actually run in the course runner, the
offline container every program in this course runs in (OR-Tools 9.15.6755). Lesson 4.1.2 already
listed the backends each OR-Tools API accepts and how each one refuses. This lesson does not repeat
that list. It asks what a person choosing a solver needs to know next: which solvers give the same
answer, which model features each accepts, and what each reports about the work it did.

Three terms used below. A **MILP solver** solves mixed-integer linear programs (lesson 1.1.3) by
branch and bound (lesson 3.2.1). A **commercial** solver is sold under a license that you pay for
beyond a free size or time limit. An **open-source** solver publishes its code under a license that
lets anyone use it without paying, a **permissive** license (Apache 2.0, MIT, EPL 2.0) being one that
also allows use inside a closed commercial product.

## Seven Solvers, Two Families: Three Commercial MIP Solvers and Four Open-Source Ones

The table gathers what each maker says about its solver on its own pages (opened 2026-11-11, listed
under Further reading), plus how this course reaches it. Prices and terms change, so each is
dated by the page it came from.

| Solver | Maker | License | From Python in this course | In the runner? |
| --- | --- | --- | --- | --- |
| Gurobi | Gurobi Optimization | commercial; pip package ships a size-limited license | `gurobipy` (lesson 5.3.1) | `gurobipy` is installed; MathOpt's `SolverType.GUROBI` cannot load its library, a version mismatch (lesson 4.1.2) |
| CPLEX | IBM | commercial; a free Community Edition limited to 1,000 variables and 1,000 constraints | none | no; the wrapper's `CreateSolver("CPLEX")` returns `None` (lesson 4.1.2) |
| Xpress | FICO | commercial; a free Community License limited to 5,000 rows plus columns for linear and mixed-integer models | none | no; the MathOpt page lists it, the Python `SolverType` of 9.15 has no member for it (lesson 4.1.2) |
| HiGHS | the HiGHS project | MIT | MathOpt `SolverType.HIGHS`, `highspy` | yes, the course default |
| SCIP | the SCIP Optimization Suite project | Apache 2.0 since version 8.0.3 | MathOpt `SolverType.GSCIP` | yes |
| CBC | COIN-OR | Eclipse Public License 2.0 | `pywraplp` `CreateSolver("CBC")`, PuLP (lesson 5.2.1) | yes |
| CP-SAT | Google, part of OR-Tools | Apache 2.0 | `cp_model`, MathOpt `SolverType.CP_SAT` | yes |

A few facts from those pages matter for the choice and are easy to get wrong:

- **"Commercial" does not mean "unusable for free".** Each commercial maker offers a free tier: the Gurobi
  pip package carries a size-limited license, the Xpress pip package runs under the free Community
  License, IBM's CPLEX Community Edition is free up to
  1,000 variables and 1,000 constraints, and Gurobi and FICO both offer evaluation licenses with no
  size limit for a trial period. Lesson 5.4.3 measures GridCap's models against those limits.
- **The open-source licenses differ, but all four allow commercial use.** SCIP moved from an academic
  license to Apache 2.0 with version 8.0.3; releases up to 8.0.2 are still under the old academic
  license, which matters if an old pin is lying around. CBC is maintained by a small group of
  volunteers under the non-profit COIN-OR Foundation, as its own README says.
- **CP-SAT is not a MILP solver in the usual sense.** It is OR-Tools' constraint programming solver
  built on SAT techniques. It takes integer data only: lesson 4.1.2 showed it refusing a 0.37
  coefficient while the model is being built.

## Public Benchmarks Compare Only Open-Source Solvers, Because the Commercial Three Withdrew

The reviewer's "everyone says Gurobi is fastest" usually traces back to public benchmarks. The best
known are Hans Mittelmann's *Benchmarks for Optimization Software* at Arizona State University. Its
front page, read on 2026-11-11, says that for many years the benchmarks included CPLEX, Gurobi and
Xpress, and that this ended: after an action by Gurobi at the 2018 INFORMS Annual Meeting, IBM and
FICO demanded that their results be removed, and Gurobi withdrew its own in August 2024.

So the current MILP benchmark (the page dated 28 Oct 2026: the 240 instances of the MIPLIB 2017
benchmark set, 2 hours each, 12 threads) lists COPT, SCIP, FiberSCIP, HiGHS (serial and parallel)
and Optverse, and no Gurobi, CPLEX or Xpress. It reports how many of the 240 each solved, and a
shifted geometric mean of run times scaled so that the best solver is 1 (lesson 5.4.2 explains
that mean). Two rows of its table:

| Solver on Mittelmann's MILP page (28 Oct 2026) | Solved (of 240) | Scaled mean (best = 1) |
| --- | --- | --- |
| COPT 9.0.0 | 225 | 1 |
| HiGHS 1.15.0, serial | 158 | 10.7 |
| SCIP 10.0.0 with SoPlex | 136 | 14.0 |

The newer MIPFEAS benchmark on the same site (dated 30 Oct 2026), which measures how fast a solver
finds good feasible plans rather than how fast it proves optimality, includes CPLEX, Xpress and COPT,
but only as one "virtual mean commercial solver": the vendors agreed to aggregated results, not
individual ones.

Three conclusions for the review:

1. **No current public benchmark ranks Gurobi, CPLEX and Xpress against each other or against
   HiGHS.** A claim that one of them is fastest cannot be checked on these pages today.
2. **A public benchmark is someone else's instances on someone else's machine.** MIPLIB 2017 is a
   standard test set built to compare MIP solvers, which is its strength; it is not GridCap. HiGHS
   solving 158 of 240 says little about whether it solves GridCap's portfolio in the nightly window.
3. **So the team benchmarks on its own models.** That is lesson 5.4.2, and the free evaluation
   licenses above are how a commercial solver enters that benchmark without buying it first.

## The Model

Every solver in this module solves the same model: GridCap's project-selection MILP from lesson
3.4.1, on a **program slice** of a GridCap medium portfolio. A slice keeps one program's projects
(transmission, distribution or vegetation), so the instance set of lesson 5.4.2 can have several
models of different difficulty that share one formulation.

**Sets.** $`P`$ the projects of one program in the medium portfolio drawn with a given seed, keeping
a child only when its parent is in the same program; $`Y`$ the plan's ten years; $`M \subseteq P`$
the must-do projects; $`\mathcal{G}`$ the alternative groups with at least two members in $`P`$;
$`C \subseteq P`$ the child projects, each with its parent $`p(c) \in P`$.

**Parameters.** $`v_i`$, the NPV of project $`i`$ started at its earliest start ($k); $`c_{i,y}`$,
what project $`i`$ spends in year $`y`$ when it starts at its earliest start ($k); $`B_y`$, the
budget of year $`y`$ in the whole portfolio ($k); $`S_y`$ and $`S^P_y`$, the year-$`y`$ spend of all
projects and of the slice's projects, each at earliest start ($k). The slice's budget is the whole
budget scaled to the slice's share, rounded down to whole $k:

```math
b_y = \left\lfloor \frac{B_y \, S^P_y}{S_y} \right\rfloor \qquad \forall y \in Y
```

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is in the plan.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(needs}_c) \\
\sum_{i \in P} c_{i,y}\, x_i &\le b_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

`instances.py` builds this model three times, once per API the solvers need: `build_mathopt` for
HiGHS and SCIP, `build_cpsat` for CP-SAT's own `cp_model` (so the program can read CP-SAT's
deterministic time, which MathOpt does not pass on), and `build_wrapper` for CBC through `pywraplp`,
the only API in the runner that has CBC. The rows carry the labels above as names (`must_P017`,
`alt_G03`, `needs_P212`, `budget_2029`). Here is the MathOpt version; the other two are the same
rows written in each API's syntax:

```python
def build_mathopt(inst: Instance) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    model = mathopt.Model(name=inst.name)
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in inst.projects}
    for p in inst.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
    for g, members in inst.groups().items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    for c in inst.children():
        model.add_linear_constraint(x[c.project_id] <= x[c.parent], name=f"needs_{c.project_id}")
    for y in inst.years:
        model.add_linear_constraint(
            sum(inst.spend(p, y) * x[p.project_id] for p in inst.projects) <= inst.budget[y],
            name=f"budget_{y}")
    model.maximize(sum(p.value * x[p.project_id] for p in inst.projects))
    return model, x
```

## In the Runner, Four Solvers Solve GridCap's Selection Model to the Same Optimum

`landscape.py` solves the transmission slice of the medium portfolio drawn with seed 2027 with each
solver the runner has. Every run uses one thread, a random seed of 1 where the API takes one, and a
relative gap target of 0, so each solver must prove optimality rather than stop at its own default
target (lesson 5.4.2 shows why that matters). `run` in `solvers.py` hides the three APIs behind one
call:

```python
for solver, api in (("HiGHS", "MathOpt"), ("SCIP", "MathOpt"), ("CP-SAT", "cp_model"), ("CBC", "pywraplp")):
    r = run(solver, inst, 1)
    work = ", ".join(f"{k} {v:g}" for k, v in r.work.items())
    print(f"  {solver:<7} via {api:<9} {r.status:<8} NPV {r.objective:,.0f}  bound {r.bound:,.0f}  "
          f"seed {'taken' if TAKES_SEED[solver] else 'not settable'}; reports {work}")
```

```text
instance transmission-2027: 130 binary variables, gap target 0, one thread, seed 1
  HiGHS   via MathOpt   optimal  NPV 145,971  bound 145,971  seed taken; reports lp_iterations 14289, nodes 316
  SCIP    via MathOpt   optimal  NPV 145,971  bound 145,971  seed taken; reports lp_iterations 5783, nodes 384
  CP-SAT  via cp_model  optimal  NPV 145,971  bound 145,971  seed taken; reports det_time 0.8529, branches 14269
  CBC     via pywraplp  optimal  NPV 145,971  bound 145,971  seed not settable; reports lp_iterations 7824, nodes 126
```

Read it in three passes.

**The answer is the same.** All four prove the same optimum, NPV $145,971k, with the bound equal to
it. On a pure-binary model with whole-number data, any correct solver must agree, and when one does
not, the disagreement is the finding (the next section shows a solver that quietly answers a
different model). Running a second solver on the same model is the cheapest correctness check a team
has.

**The work is reported in different units.** HiGHS, SCIP and CBC report **LP iterations** (simplex
pivots, the steps of the LP solves inside branch and bound) and **nodes** (subproblems of the search
tree). CP-SAT reports **deterministic time**, its own estimate of the work done, computed from what
the search did and meant to be close to a second (lesson 4.6.3), and **branches**, its search
decisions. These counts are **deterministic measures**: they depend only on the path the search
took, so a run that repeats its path repeats them. The program prints which one the benchmark of
lesson 5.4.2 ranks each solver by:

```text
the deterministic unit each reports, which the benchmark ranks it by:
  HiGHS   lp_iterations (also nodes)
  SCIP    lp_iterations (also nodes)
  CP-SAT  det_time (also branches)
  CBC     lp_iterations (also nodes)
```

The same name does not make the same unit. HiGHS's 14,289 LP iterations and SCIP's 5,783 come from
different LP solvers (SCIP runs SoPlex, lesson 4.1.2) on different subproblems, after different
presolves and cuts; a SCIP node and a CBC node are not the same amount of work either. **Never
compare one solver's count with another's.** A count compares runs of one solver: two settings, two
seeds, two versions. Lesson 5.4.2 builds on exactly that line.

**CBC takes no seed here.** The linear solver wrapper's common parameters have no seed, and the
way to pass a solver its own settings, `SetSolverSpecificParametersAsString`, is not supported for
CBC: the program asks, and the call returns `False` (it also writes a warning saying so to the log):

```python
cbc, _ = build_wrapper(inst, "CBC")
print("\nCBC accepts solver-specific settings such as a seed:",
      cbc.SetSolverSpecificParametersAsString("randomSeed 2"))
```

```text
CBC accepts solver-specific settings such as a seed: False
```

CBC runs on one fixed path, so its benchmark has one run per instance where the others have three.

<!-- practice 1 -->

## Model Features Decide Before Speed Does

Speed only matters among solvers that can solve your model at all. `capabilities.py` asks the three
MathOpt solvers about three tiny models, each with one feature that GridCap's models may grow: a
continuous variable (the carry-over $`r_y`$ of lesson 6.4.4), a quadratic objective, and an
**indicator constraint**, a row that applies only when a binary is 1 (lesson 4.3.1). Each model's
optimum is known by hand, so a wrong answer is visible:

```python
for make in (continuous, quadratic, indicator):
    print(f"{make.__name__}: {make.__doc__.split(':')[0]}")
    for name, kind in SOLVERS:
        model = make()
        try:
            result = mathopt.solve(model, kind)
            values = ", ".join(f"{v.name} = {result.variable_values(v):g}" for v in model.variables())
            print(f"  {name:<7} {result.termination.reason.name}, objective {result.objective_value():.4f} ({values})")
        except Exception as error:
            reason = getattr(error.__context__, "message", str(error))
            print(f"  {name:<7} refused: {reason}")
```

```text
continuous: max 1.01a + 2.9b, 0.37a + 1.13b <= 7.71, a in [0, 10] continuous, b in {0..10}
  HiGHS   OPTIMAL, objective 20.3078 (a = 8.62162, b = 4)
  SCIP    OPTIMAL, objective 20.3078 (a = 8.62162, b = 4)
  CP-SAT  OPTIMAL, objective 19.6800 (a = 8, b = 4)
quadratic: min (a - 3)^2 + (b - 6)^2, a + b <= 7, a, b in {0..10}
  HiGHS   refused: MathOpt does not currently support Highs models with quadratic objectives
  SCIP    OPTIMAL, objective 2.0000 (a = 2, b = 5)
  CP-SAT  refused: MathOpt does not currently support CP-SAT models with quadratic objectives
indicator: max a + 2z, z = 1 implies a <= 3, a in {0..10}, z binary
  HiGHS   refused: Highs does not support indicator constraints
  SCIP    OPTIMAL, objective 10.0000 (z = 0, a = 10)
  CP-SAT  refused: MathOpt does not currently support CP-SAT models with indicator constraints
```

Two kinds of "no" appear, and the second is the dangerous one:

- **A refusal.** HiGHS and CP-SAT refuse the quadratic objective and the indicator constraint through
  MathOpt; `mathopt.solve` raises, and the reason sits on the exception's `__context__` (lesson
  4.2.4). A refusal costs you a failed run, never a wrong plan.
- **A quiet change.** CP-SAT accepts the continuous model, reports `OPTIMAL`, and returns
  $`a = 8`$: it treated the continuous $`a`$ as an integer, and its "optimum" of 19.68 is below the
  true 20.3078 (lesson 4.2.3 met the same rounding on GridCap small). A benchmark that
  only checked statuses would score CP-SAT as correct here.

| Feature, through MathOpt in OR-Tools 9.15.6755 | HiGHS | SCIP | CP-SAT |
| --- | --- | --- | --- |
| binary and integer variables | yes | yes | yes |
| continuous variables, exactly | yes | yes | no: rounds them, reports `OPTIMAL` |
| quadratic objective | refused | yes | refused |
| indicator constraints | refused | yes (one-sided implied rows only, lesson 4.3.1) | refused |

CBC is outside MathOpt, so this probe does not reach it; through `pywraplp` it solves linear MILPs
like the selection model. The table is why GridCap's models are written with big-M or cumulative rows
rather than indicators (lessons 6.2.1 and 6.4.3): those forms run on every solver, so the solver can be
chosen on evidence instead of being forced by one feature.

<!-- practice 2 -->

## Summary

- **Seven solvers, two families.** Gurobi, CPLEX and Xpress are commercial, each with a free
  size-limited tier and evaluation licenses; HiGHS (MIT), SCIP (Apache 2.0 since 8.0.3), CBC (EPL 2.0)
  and CP-SAT (Apache 2.0) are open source. Four of the seven solve in the course runner.
- **Public benchmarks compare only open-source solvers.** Mittelmann's pages lost CPLEX and Xpress
  after 2018 and Gurobi in August 2024, so "X is fastest" cannot be checked there: benchmark your own
  models.
- **In the runner, four solvers find the same optimum on GridCap's selection model** and report their
  work in different deterministic units, which compare runs of one solver, never two solvers.
- **Model features decide before speed does.** SCIP alone takes quadratic objectives and indicator
  constraints through MathOpt; CP-SAT silently rounds continuous variables.

## Reference

| Solver | Reached in this course through | Deterministic work it reports here | Seed in this course's API |
| --- | --- | --- | --- |
| HiGHS | MathOpt `SolverType.HIGHS` | `solve_stats.simplex_iterations`, `solve_stats.node_count` | `SolveParameters(random_seed=...)` |
| SCIP | MathOpt `SolverType.GSCIP` | `solve_stats.simplex_iterations`, `solve_stats.node_count` | `SolveParameters(random_seed=...)` |
| CP-SAT | `cp_model.CpSolver` | `deterministic_time`, `num_branches` | `parameters.random_seed` |
| CBC | `pywraplp.Solver.CreateSolver("CBC")` | `iterations()`, `nodes()` | none |
| Gurobi | `gurobipy` (lesson 5.3.1) | not measured in this module | |
| CPLEX, Xpress | not installed in the runner | not measured in this module | |

| Term | Meaning |
| --- | --- |
| deterministic measure | a count that depends only on the search path (LP iterations, nodes, CP-SAT's deterministic time), so it repeats when the path repeats |
| refusal | the solver raises instead of solving a model with a feature it lacks |
| quiet change | the solver solves a different model (CP-SAT rounding a continuous variable) and reports success |

**Further reading:** [MathOpt](https://developers.google.com/optimization/math_opt) (the eight
solvers MathOpt supports, with Gurobi and Xpress needing a paid license); [OR-Tools on
GitHub](https://github.com/google/or-tools) (Apache 2.0, and what the suite contains, CP-SAT among
it); [MathOpt `SolveStats` in result.py, v9.15](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/result.py)
(simplex iterations, node count and wall-clock solve time);
[Benchmarks for Optimization Software](https://plato.asu.edu/bench.html) (H. Mittelmann; the end of
commercial participation, and the benchmark list); [MILP Benchmark, MIPLIB 2017](https://plato.asu.edu/ftp/milp.html)
(the solvers, solved counts and scaled means quoted above); [MIPFEAS Benchmark](https://plato.asu.edu/ftp/mipfeas.html)
(the virtual mean commercial solver); [MIPLIB 2017](https://miplib.zib.de/) (the benchmark set of 240
instances, a standard test set for MIP solvers); [HiGHS documentation](https://ergo-code.github.io/HiGHS/dev/)
(MIT license, what HiGHS solves); [SCIP Optimization Suite](https://www.scipopt.org/) (Apache 2.0
from 8.0.3, the academic license before); [Cbc on GitHub](https://github.com/coin-or/Cbc) (EPL 2.0,
volunteer maintenance); [Gurobi licensing](https://www.gurobi.com/solutions/licensing/) (free trial,
academic and evaluation licenses); [IBM ILOG CPLEX Optimization Studio pricing](https://www.ibm.com/products/ilog-cplex-optimization-studio/pricing)
(the Community Edition's limits); [FICO Xpress license options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options)
(community, academic, evaluation and commercial licenses).

## Challenges

1. Add a fourth tiny model to `capabilities.py` with an integer variable whose bounds are
   $`[-5, 5]`$ and an objective that rewards a negative value. Predict whether every solver handles
   the negative range.
2. Run `landscape.py` on the vegetation slice instead (`"vegetation-2027"`). Predict which counts
   fall to almost nothing, and why a benchmark made only of such instances would tell you little.
3. Write down which solver you would pick for a model that needs an indicator constraint *and*
   must run on CP-SAT for a scheduling part. What would you change in the model instead?

## Design Note: Keep the Model Solver-Neutral as Long as You Can

Every feature you use that only one solver accepts narrows the choice to that solver, and every later
argument about speed, license or price becomes moot. GridCap's formulation sticks to what all the
candidates solve exactly: binaries, linear rows, and big-M or cumulative forms where an indicator
would be shorter. When a feature is worth the lock-in, take it on purpose, write down which solvers it
leaves, and keep a test that solves the model with the second-best one, so the day the license or the
version changes you are not starting from zero.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**landscape.py.** The transmission slice solved by HiGHS, SCIP, CP-SAT and CBC, with what each
reports (*In the Runner, Four Solvers Solve GridCap's Selection Model to the Same Optimum*). *Try:*
Change the seed from 1 to 2. Predict which lines change and which stay the same.

- Program: [landscape.py](src/landscape.py)

**capabilities.py.** Three tiny models, each with one feature, asked of the MathOpt solvers (*Model
Features Decide Before Speed Does*). *Try:* Make `a` an integer in the continuous model. Predict
CP-SAT's objective.

- Program: [capabilities.py](src/capabilities.py)

**instances.py, solvers.py and quiet.py.** The instance set and its three builders; one run of one
solver with its deterministic measures; and the helper that keeps HiGHS's stray C output (a debug line it can print on a MIP
solve, even with no log requested) off the program's output.

- Library: [instances.py](src/instances.py)
- Library: [solvers.py](src/solvers.py)
- Library: [quiet.py](src/quiet.py)
