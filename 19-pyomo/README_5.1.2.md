# 5.1.2 Solving With HiGHS and Reading Results

The Pyomo port of GridCap's five-year model (lesson 5.1.1) now runs every night, and the planners
want each run to say plainly what happened: an optimal plan, a plan that is good but not proven
best, or no plan at all and why. They also want to know what one more $k of budget would be worth.
All of that is in what the solver hands back, if you know where to read it. This lesson solves the
model with HiGHS through Pyomo, reads the results object field by field on four kinds of solve, and
then reads duals, including the case where Pyomo has none to give. GridCap is fictional.

## The Model

The model is lesson 5.1.1's, unchanged: $`x_{i,t} \in \{0, 1\}`$ for each allowed start
$`(i, t) \in S`$, the once, alternative, precedence and per-year budget rows, and
$`\max \sum_{(i,t) \in S} \text{npv}_{i,t}\, x_{i,t}`$. *The Model* of lesson 5.1.1 states it in
full. The last section of this lesson uses a second, smaller model, stated where it is used.

## HiGHS Is Called Through One of Two Pyomo Interfaces

Pyomo does not solve anything itself; a **solver interface** writes the model in the form a solver
reads, calls the solver, and brings the answer back. For HiGHS (the open-source solver section 4
used through MathOpt) Pyomo 6.10 has two interfaces, both talking to the `highspy` package in
process:

- the newer one, `pyomo.contrib.solver`, whose factory is imported from
  `pyomo.contrib.solver.common.factory`. Its `solve` returns a `Results` object with flat fields.
  The Pyomo documentation calls these interfaces a development preview whose API may still change.
- the older one, `pyo.SolverFactory("appsi_highs")` (or `"highs"`), which returns the classic
  `SolverResults` object that most existing Pyomo code reads.

This lesson reads both. `pyomo_timing.highs()` returns the older one with a zero gap and is what the
module's other programs use; the newer one has the clearer results, so it comes first:

```python
import pyomo.environ as pyo
from pyomo.contrib.solver.common.factory import SolverFactory

from gridcap import generate
from pyomo_timing import build

small = generate("small")
opt = SolverFactory("highs")          # Pyomo's newer solver interface to HiGHS (highspy)


def report(label, results):
    print(f"{label:16} {results.termination_condition.name:31} {results.solution_status.name:10}"
          f" incumbent {results.incumbent_objective}  bound {results.objective_bound}")
```

Options go to `solve` as keywords: `rel_gap`, `abs_gap`, `time_limit`, `threads` and `tee=True`
(which prints HiGHS's log) are common to the newer interface's solvers, and `solver_options={...}`
passes HiGHS's own options by their HiGHS names.

## Termination Condition and Solution Status Answer Different Questions

```python
m = build(small)
results = opt.solve(m, rel_gap=0.0)
report("rel_gap=0", results)
print("  loaded into the model: x[P031,2028] =", m.x["P031", 2028].value, " objective", pyo.value(m.value))
```

```text
rel_gap=0        convergenceCriteriaSatisfied    optimal    incumbent 24260.0  bound 24260.0
  loaded into the model: x[P031,2028] = 1.0  objective 24260.0
```

Four fields carry the answer:

- `termination_condition` says **why the solver stopped**. `convergenceCriteriaSatisfied` means it
  met its stopping rule, which for a MILP is "the gap is within the tolerance". Other values say it
  hit a limit (`maxTimeLimit`, `iterationLimit`), proved something (`provenInfeasible`,
  `unbounded`), or could not tell (`infeasibleOrUnbounded`, `error`).
- `solution_status` says **what the solution in hand is**: `optimal`, `feasible` (it satisfies every
  row, but nothing proves it is the best), `infeasible`, or `noSolution`.
- `incumbent_objective` is the objective of the best plan found, the **incumbent**.
- `objective_bound` is the best **bound** the solver proved: for this maximization, no plan can be
  worth more.

By default the newer interface **loads** the solution into the model, so the values sit on the
variables: `m.x["P031", 2028].value` is 1.0 (P031 starts in 2028, as lesson 6.4.1 found), and
`pyo.value(m.value)` evaluates the objective at those values. A program reads the plan from the
model, never from the log.

## The Incumbent and the Bound Give the Gap

`rel_gap=0.0` asked for a proven optimum. Without it, HiGHS uses its own default tolerance:

```python
results = opt.solve(build(small))
report("default gap", results)
gap = (results.objective_bound - results.incumbent_objective) / results.incumbent_objective
print(f"  relative gap {gap:.2e}")
```

```text
default gap      convergenceCriteriaSatisfied    optimal    incumbent 24260.0  bound 24262.0
  relative gap 8.24e-05
```

Both runs report `optimal`, but the second one stopped with the bound at 24,262 and the incumbent at
24,260: HiGHS proved only that no plan is worth more than $2k above this one, a relative gap of
0.0082%, within its default tolerance, HiGHS's `mip_rel_gap` of 0.0001 (0.01%). Here the incumbent happens to be the true optimum
(the first run proved it), but the default run did not prove it. "Optimal" from a MILP solver
always means "optimal within the gap tolerance"; when two runs or two solvers must agree to the
last $k, pass `rel_gap=0.0` (section 3.4 covers gaps and the denominators solvers use).

## An Infeasible Solve Raises Unless You Ask It to Return

Cut every budget to 0 and the must-do projects cannot be funded:

```python
broke = build(small)
for y in broke.Y:
    broke.budget[y] = 0
try:
    opt.solve(broke)
except Exception as error:
    print("infeasible        raises", type(error).__name__)
results = opt.solve(broke, raise_exception_on_nonoptimal_result=False, load_solutions=False)
report("  returned", results)
```

```text
infeasible        raises NoOptimalSolutionError
  returned       provenInfeasible                noSolution incumbent None  bound inf
```

With its defaults the newer interface raises `NoOptimalSolutionError` whenever the result is not an
optimal one, and it would also fail trying to load a solution that does not exist. A nightly job
that must report rather than crash passes `raise_exception_on_nonoptimal_result=False` and
`load_solutions=False`, then reads the fields: `provenInfeasible`, `noSolution`, no incumbent. The
bound printed as `inf` means no bound: with no plan there is nothing to bound.

`load_solutions=False` has a cost when there *is* a plan: nothing is put on the variables. The
results object still holds the plan, and `results.solution_loader.load_vars()` copies it onto the
model's variables when the program has checked that it wants it:

```python
kept = build(small)
results = opt.solve(kept, rel_gap=0.0, raise_exception_on_nonoptimal_result=False, load_solutions=False)
report("not loaded", results)
print("  before load_vars: x[P031,2028] =", kept.x["P031", 2028].value)
results.solution_loader.load_vars()
print("  after load_vars:  x[P031,2028] =", kept.x["P031", 2028].value, " objective", pyo.value(kept.value))
```

```text
not loaded       convergenceCriteriaSatisfied    optimal    incumbent 24260.0  bound 24260.0
  before load_vars: x[P031,2028] = None
  after load_vars:  x[P031,2028] = 1.0  objective 24260.0
```

So a job that never raises reads the fields first, and calls `load_vars()` only when the solution
status is `optimal` or `feasible`; for `noSolution` there is nothing to load.

A MILP that can improve without limit is a different failure that looks similar. Give the model a
new integer variable with no upper bound and a positive objective coefficient (a forgotten bound,
the commonest cause):

```python
loose = build(small)
loose.loan = pyo.Var(domain=pyo.NonNegativeIntegers)
loose.value.expr = loose.value.expr + loose.loan
results = opt.solve(loose, raise_exception_on_nonoptimal_result=False, load_solutions=False)
report("unbounded MILP", results)
```

```text
unbounded MILP   infeasibleOrUnbounded           noSolution incumbent None  bound inf
```

HiGHS stops with `infeasibleOrUnbounded`: for this MILP it did not establish which of the two it
is. A report that turns every non-optimal result into "infeasible" sends a planner looking for a
conflict between rows that does not exist; the fix here is a bound on `loan`, not a relaxed budget.
Solving the same model again is no fix either: the missing bound is in the model, not in the run.
Map each termination condition to its own message, and keep `infeasibleOrUnbounded` separate.

<!-- practice 1 -->

## A Limit Leaves a Feasible Plan That Is Not Proven Optimal

On GridCap medium (400 projects, 887 start variables), stop HiGHS after its first node of
branch-and-bound with its own option `mip_max_nodes`:

```python
medium = build(generate("medium"))
results = opt.solve(medium, solver_options={"mip_max_nodes": 1}, raise_exception_on_nonoptimal_result=False)
report("medium, 1 node", results)
print("  plan loaded:", sum(1 for v in medium.x.values() if v.value > 0.5), "starts; objective", pyo.value(medium.value))
```

```text
medium, 1 node   iterationLimit                  feasible   incumbent 226745.0  bound 226915.0
  plan loaded: 222 starts; objective 226745.0
```

The termination condition says a limit stopped the search; the solution status says the plan in
hand is `feasible`. The plan is loaded (here `load_solutions` was left on, and a feasible solution
can be loaded) and it is a real plan, worth $226,745k, within $170k (0.075%) of the bound. Whether
that is good enough is the planners' call, which is why a report should print the gap with every
plan that is not proven optimal. A wall-clock `time_limit` stops the search the same way, with
`maxTimeLimit`, but where it stops depends on the machine's speed; a node limit stops at the same
place on every run, which is why this lesson uses one.

## Older Code Reads a SolverResults Object

Most Pyomo code you inherit uses the older interface:

```python
legacy = pyo.SolverFactory("appsi_highs")
legacy.config.mip_gap = 0.0
old = legacy.solve(build(small))
print("legacy           ", old.solver.status, old.solver.termination_condition,
      " lower", old.problem.lower_bound, " upper", old.problem.upper_bound)
print("  check_optimal_termination:", pyo.check_optimal_termination(old))
```

```text
legacy            ok optimal  lower 24260.0  upper 24260.0
  check_optimal_termination: True
```

The same information sits in other places: `results.solver.status` (`ok`, `warning`, `error`),
`results.solver.termination_condition` (`optimal`, `infeasible`, `maxTimeLimit`, ...), and the
objective's two ends as `results.problem.lower_bound` and `upper_bound`, which for a maximization
are the incumbent and the bound. `pyo.check_optimal_termination(results)` is the usual one-line
test, and `pyo.assert_optimal_termination(results)` raises when it fails. The older interface also
raises on an infeasible model unless `solve` gets `load_solutions=False`; lesson 5.1.4 meets that
when a Pyomo tool needs a solver that reports instead of raising.

## A MILP Has No Duals; Fix the Integers and Re-Solve the LP

A **dual value** of a row (section 2.3) is how much the optimal objective changes per unit of the
row's right side: the value of one more $k of budget. Pyomo imports duals through a **Suffix**, a
component that holds one value per row (or per variable) and is filled by the solver interface:

```python
lp = build(small, integer=False)
lp.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
highs().solve(lp)
print(f"LP relaxation   NPV {pyo.value(lp.value):,.1f}  budget duals {budget_duals(lp)}")

milp = build(small)
milp.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
try:
    highs().solve(milp)
except RuntimeError as error:
    print("MILP with a dual Suffix:", type(error).__name__, str(error).splitlines()[0])
```

```text
LP relaxation   NPV 26,587.4  budget duals {2027: 0.64, 2028: 0.547, 2029: 0.465, 2030: 0.422, 2031: 0.316}
MILP with a dual Suffix: RuntimeError Solver does not currently have valid duals. Please check the termination condition.
```

The LP relaxation has duals: in it, one more $k of 2027 budget is worth $0.64k of NPV. But these
are the relaxation's prices, for a plan with fractional projects that nobody will fund. The MILP has
none at all: a MILP is not an LP, so the solver has no dual solution to hand over, and asking for
one makes the solve raise. Pyomo does not quietly do anything else for you: it does not fix the
integers and re-solve.

The usual way to price a MILP's plan is yours to write: solve the MILP, **fix** every integer
variable at its value (`v.fix(...)` turns a variable into a constant for the solver), turn
integrality off with the `core.relax_integer_vars` transformation, declare the Suffix and solve the
LP that is left:

```python
milp = build(small)
highs().solve(milp)
for v in milp.x.values():
    v.fix(round(v.value))
pyo.TransformationFactory("core.relax_integer_vars").apply_to(milp)
milp.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
highs().solve(milp)
print(f"fixed plan, LP  NPV {pyo.value(milp.value):,.1f}  budget duals {budget_duals(milp)}")
```

```text
fixed plan, LP  NPV 24,260.0  budget duals {2027: 0.0, 2028: 0.0, 2029: 0.0, 2030: 0.0, 2031: 0.0}
```

Every dual is 0, and that is the right answer for this model: once every $`x_{i,t}`$ is fixed,
nothing is left to decide, so one more $k of budget changes nothing. The **fixed-integer duals**
price the continuous part of a model, with the integer decisions held as they are. They say
something only when continuous variables remain.

A model that has some: lesson 5.1.4's contractor model. A one-period selection on GridCap small
funds projects within the capital budget, and its transmission projects need crew-months; GridCap's
crews cover 40, and every month beyond is bought from contractors at tiered prices. Its formulation:

**Sets.** $`P`$ the projects; $`T \subseteq P`$ the transmission projects; $`M \subseteq P`$ the
must-do projects. **Parameters.** $`\text{value}_i`$, $`\text{capex}_i`$ ($k);
$`\text{months}_i`$, the crew-months project $`i`$ needs; $`B = 38{,}390`$, the capital budget ($k);
$`O = 40`$, the crew-months GridCap's crews cover. **Variables.** $`x_i \in \{0, 1\}`$;
$`0 \le b \le 40`$, contractor crew-months bought; $`c \ge 0`$, what they cost ($k).

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{value}_i\, x_i - c \\
& \sum_{i \in P} \text{capex}_i\, x_i \le B && \text{(budget)} \\
& x_i = 1 && \forall i \in M && \text{(must\_do}_i) \\
& \sum_{i \in T} \text{months}_i\, x_i \le O + b && && \text{(crews)} \\
& c \ge 30\, b, \quad c \ge 300 + 45\,(b - 10), \quad c \ge 750 + 70\,(b - 20) && && \text{(tiers)}
\end{aligned}
```

The three tier rows say contractor months cost $30k each for the first 10, $45k for the next 10 and
$70k beyond (lesson 5.1.4 shows Pyomo writing exactly these rows). The same fix-and-re-solve:

```python
c = contractor_model.build(small, own=40)
highs().solve(c)
for v in c.x.values():
    v.fix(round(v.value))
pyo.TransformationFactory("core.relax_integer_vars").apply_to(c)
c.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
highs().solve(c)
print(f"contractors     bought {c.bought.value:g} months for ${c.contract.value:,.0f}k;"
      f" crews dual {c.dual[c.crews]:g}, budget dual {c.dual[c.budget]:g}")
```

```text
contractors     bought 21 months for $820k; crews dual 70, budget dual 0
```

With the funded projects held fixed, the plan buys 21 contractor months for $820k (10 at $30k, 10
at $45k, 1 at $70k), and the crews row's dual is 70: one more crew-month of GridCap's own saves one
contractor month in the $70k tier. That is a price the planners can use. The budget's dual is 0
because, with every project fixed, no spending can change. Lesson 9.2.2 takes this further: what
fixed-integer duals mean, and when they mislead.

<!-- practice 2 -->

## Summary

- **HiGHS is called through one of two Pyomo interfaces.** The newer `pyomo.contrib.solver` returns
  flat `Results`; the older `SolverFactory("appsi_highs")` returns a `SolverResults`.
- **Termination condition and solution status answer different questions.** Why it stopped, and
  what the solution in hand is; a loaded solution is read from the model's variables.
- **The incumbent and the bound give the gap.** HiGHS's default tolerance stopped with a bound of
  24,262 over an incumbent of 24,260; `rel_gap=0.0` proves the optimum.
- **An infeasible solve raises unless you ask it to return.** `raise_exception_on_nonoptimal_result=False`
  and `load_solutions=False`; an unbounded MILP came back `infeasibleOrUnbounded`, not infeasible.
- **A limit leaves a feasible plan that is not proven optimal.** `iterationLimit` with status
  `feasible`, and a gap to report.
- **Older code reads a SolverResults object.** `results.solver.termination_condition`,
  `results.problem` bounds, `check_optimal_termination`.
- **A MILP has no duals; fix the integers and re-solve the LP.** The Suffix raises on the MILP; the
  fixed-plan LP priced a contractor crew-month at $70k.

## Reference

| Newer interface (`pyomo.contrib.solver`) | Older interface (`pyo.SolverFactory`) |
| --- | --- |
| `SolverFactory("highs").solve(m, rel_gap=0.0)` | `s = pyo.SolverFactory("appsi_highs"); s.config.mip_gap = 0.0; s.solve(m)` |
| `results.termination_condition` | `results.solver.termination_condition` |
| `results.solution_status` | `results.solver.status` (`ok`, `warning`, `error`) |
| `results.incumbent_objective`, `results.objective_bound` | `results.problem.lower_bound`, `upper_bound` |
| `raise_exception_on_nonoptimal_result=False, load_solutions=False` | `load_solutions=False` |
| `results.solution_loader.load_vars()`, `.get_duals()` | `pyo.check_optimal_termination(results)` |

| Termination condition | Meaning |
| --- | --- |
| `convergenceCriteriaSatisfied` | optimal within the gap tolerance |
| `maxTimeLimit`, `iterationLimit` | a limit stopped the search; check `solution_status` for a plan |
| `provenInfeasible` | no plan satisfies the rows |
| `unbounded`, `infeasibleOrUnbounded` | the objective can improve forever, or the solver could not tell which |

| Duals of a MILP | How |
| --- | --- |
| LP relaxation | `build(..., integer=False)`, `m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)` |
| fixed-integer | solve, `v.fix(round(v.value))` for each integer variable, `core.relax_integer_vars`, Suffix, solve |

**Further reading.** Pyomo documentation, [Future Solver Interface Changes](https://pyomo.readthedocs.io/en/stable/explanation/experimental/solvers.html)
(the `pyomo.contrib.solver` factory names, the `Results` fields and how they replace the old
status fields, the solution loader); [Suffixes](https://pyomo.readthedocs.io/en/stable/explanation/modeling/math_programming/suffixes.html)
(importing `dual`, `check_optimal_termination` before reading a suffix). HiGHS documentation,
[option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/): `mip_rel_gap`
(default 0.0001, measured as $`|ub - lb| / |ub|`$), `mip_max_nodes` and `time_limit`.

## Challenges

1. Solve GridCap medium with `time_limit=2` twice. Do the two incumbents agree? Why might they not?
2. Read the newer interface's duals of the LP relaxation with `results.solution_loader.get_duals()`
   instead of a Suffix, and compare them with the printed ones.
3. In the contractor model, set `own=60`. Predict the crews dual before running.

## Design Note: Report Every Field, Not a Word

A nightly report that prints "optimal" or "failed" loses exactly what a planner needs: whether the
plan is proven, how far from proven it is, and whether "failed" means a conflict between rows or a
missing bound. Print the termination condition, the solution status, the incumbent and the bound,
and the gap computed from them. Section 9 builds the full planner message on these fields.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**reading_results.py.** Seven solves of the timing model (optimal, default gap, infeasible, loaded by hand, unbounded,
node-limited, older interface) and the fields that tell them apart (every section up to *Older
Code*). *Try:* Set `mip_max_nodes` to 50. Predict which of the two numbers on that line moves.

- Program: [reading_results.py](src/reading_results.py)

**duals.py.** Duals of the LP relaxation, the refusal on the MILP, and the fixed-integer re-solve on
two models (*A MILP Has No Duals*). *Try:* Print every row's dual of the fixed contractor LP. Which
are nonzero?

- Program: [duals.py](src/duals.py)

**contractor_model.py.** The contractor model the last section prices; lesson 5.1.4 explains its
`Piecewise` row.

- Library: [contractor_model.py](src/contractor_model.py)
