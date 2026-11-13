# 3.3.3 Primal Heuristics: Rounding, Diving, RINS

A GridCap planner runs the five-year plan with a 10-second limit before a board meeting. If the
search has not finished, she still needs a plan to show, and the best one the solver has. Where does
that plan come from, if branch-and-bound has not reached the bottom of its tree? From **primal
heuristics**: fast procedures that try to build good plans from the LP relaxation, alongside the
search. This lesson writes four of them, runs them on the five-year model, and compares what each
finds with the true optimum. GridCap is a fictional utility; its numbers are teaching data.

## The Model

The five-year selection model of lesson 3.3.2, unchanged; the heuristics only read it.

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

On GridCap medium its optimum, proved by HiGHS with a zero gap tolerance in lesson 3.3.2, is
274,999, and its LP relaxation bound is 275,164.8. Every heuristic below is measured against those
two numbers.

## A Heuristic Finds Plans, and the Best One So Far Is the Incumbent

A **heuristic** is a procedure that usually finds a good answer fast and promises nothing: not that
it finds a plan, and not that the plan is optimal. A **primal heuristic** finds feasible plans
("primal" because a plan is a point of the primal model, as opposed to a bound from the dual side).

The best feasible plan found so far is the **incumbent**, and its value is the **primal bound**: the
optimum is at least that good. The LP relaxation gives the other side, the **dual bound**: the
optimum is at most that. The **gap** between them says how far from proved the answer is. Lesson
3.4.1 defines it exactly; this lesson uses HiGHS's form,
$`(\text{dual bound} - \text{incumbent}) / \text{incumbent}`$.

Branch-and-bound (lessons 3.2.1 to 3.2.4) needs an incumbent to prune: a node whose LP bound is below the
incumbent's value cannot hold a better plan and is dropped. With no incumbent nothing is pruned, so
a good plan found early saves search everywhere. That is why solvers run heuristics before the first
branch and keep running them during the search.

In the code below, a plan is a dict from variable name to 0 or 1, and the model's rows are read into
the `BinaryModel` of lesson 3.3.2. Two helpers check a plan:

```python
def broken(m: BinaryModel, plan: dict[str, int]) -> list[str]:
    """The rows a 0-1 plan breaks."""
    out = []
    for name, row in m.rows.items():
        lhs = sum(a * plan[j] for j, a in row.coefs.items())
        if lhs > row.rhs + EPS or (row.sense == "==" and lhs < row.rhs - EPS):
            out.append(name)
    return out


def value(m: BinaryModel, plan: dict[str, int]) -> float:
    return sum(c * plan[j] for j, c in m.objective.items())
```

## Rounding Down Keeps a Packing Plan Feasible, Rounding to Nearest Does Not

The LP relaxation's optimum is almost a plan: on the five-year model only five of 400 variables are
fractional. The obvious move is to round them. There are two obvious ways:

```python
def round_down(x: dict[str, float]) -> dict[str, int]:
    return {j: int(v > 1 - EPS) for j, v in x.items()}


def round_nearest(x: dict[str, float]) -> dict[str, int]:
    return {j: int(v >= 0.5) for j, v in x.items()}
```

`EPS` is $`10^{-6}`$: an LP solver returns 0.9999999 for a value that is 1 up to its tolerance, and
`round_down` must count it as 1.

```text
LP bound 275,164.8; fractional variables: x_P137 = 0.467, x_P152 = 0.200, x_P181 = 0.733, x_P275 = 0.890, x_P276 = 0.890
round down:    value 271,019, breaks no row
round nearest: value 275,729, breaks ['budget_2028', 'budget_2029']
```

Rounding to nearest gives a "plan" worth more than the LP bound, which is impossible for a real plan:
it overspends 2028 and 2029. Rounding down is feasible, and that is no luck. The budget and
alternative rows have only nonnegative coefficients (rows like that are called **packing rows**):
lowering any variable lowers the left side, so a point that fits keeps fitting. The `after` rows
$`x_c - x_{p(c)} \le 0`$ survive too: if the parent is fractional, the child is at most that
fraction, so both round to 0; if the parent is 1, the child's row allows anything. The must-do
variables are already 1. So for this model, rounding down always gives a plan. For a model with
$`\ge`$ rows (a minimum spend per region, say) it can break those, and no single rounding direction
is safe.

The price is value: 271,019 is 1.5% below the LP bound. Rounding down dropped five projects, and the
money they would have used is now unspent.

## A Greedy Fill Spends What Rounding Left Unspent

Repair the rounded plan: go through the projects not funded, best value per $k first, and add each
one that keeps the plan feasible.

```python
def greedy_fill(m: BinaryModel, plan: dict[str, int], weight: dict[str, float]) -> dict[str, int]:
    """Add unfunded projects, best value per unit of `weight` first, whenever the plan stays feasible."""
    plan = dict(plan)
    for j in sorted((j for j in plan if not plan[j]), key=lambda j: (-m.objective[j] / max(weight[j], 1), j)):
        plan[j] = 1
        if broken(m, plan):
            plan[j] = 0
    return plan
```

The weight of a project is its total spend over the five plan years (`max(..., 1)` keeps a project
with no spend in those years from dividing by zero). Every candidate is tried, not only until the
first one that does not fit: a large project may not fit in what is left while a small one further
down the list does.

```text
round down, then greedy fill: adds x_P010, x_P020, x_P077, x_P103, x_P117, x_P137, x_P142, x_P218, x_P244, x_P284, x_P353, x_P380, x_P381; value 274,418, breaks no row
  gap to the LP bound: 0.2721%
```

Thirteen projects added, among them P137, one of the five that rounding dropped, and the plan is now
within 0.27% of the LP bound. The true optimum, 274,999, is 581 above it. Rounding plus a greedy
repair costs one LP solve and a pass over the projects, and on this model it gets within a third of
a percent.

<!-- practice 1 -->

## Diving Fixes One Variable, Re-Solves the LP, and Repeats

Rounding decides all five fractional variables at once, from one LP point. **Diving** decides them
one at a time and lets the LP react to each decision: fix one variable, solve the LP again with that
fixing, look at the new point, fix another. It is a single path down the branch-and-bound tree,
taken without ever coming back.

Which variable, and which way? This dive, **fractional diving**, picks the variable closest to a
whole number (the least fractional, $`\min(x_j, 1 - x_j)`$ smallest) and rounds it to its nearest
value: that is the decision the LP is most sure of. If the fixing makes the LP infeasible, it fixes
the variable the other way.

```python
def dive(lp: Relaxation, max_depth: int = 1000) -> tuple[dict[str, int] | None, list[DiveStep]]:
    """Fractional diving: round the least fractional variable to its nearest value, re-solve, repeat.

    If that fixing makes the LP infeasible, fix the variable the other way. Stops at an LP optimum
    with no fractional variable (a feasible 0-1 plan) or when both fixings fail.
    """
    fixed: dict[str, int] = {}
    steps: list[DiveStep] = []
    bound, x = lp.solve(fixed)
    for depth in range(1, max_depth + 1):
        if bound is None:
            return None, steps
        candidates = fractional(x)
        if not candidates:
            return {j: round(v) for j, v in x.items()}, steps
        j = min(candidates, key=lambda j: (min(x[j], 1 - x[j]), j))
        first = int(x[j] >= 0.5)
        for target in (first, 1 - first):
            new_bound, new_x = lp.solve({**fixed, j: target})
            if new_bound is not None:
                break
        steps.append(DiveStep(depth, j, x[j], target, new_bound if new_bound is not None else float("nan")))
        fixed[j] = target
        bound, x = new_bound, new_x
    return None, steps
```

`Relaxation.solve(fixed)` sets the bounds of every fixed variable to its value, every other to
$`[0, 1]`$, solves the LP with GLOP, and returns `(None, {})` if the LP has no solution. The dive
ends when the LP optimum has no fractional variable left: that point satisfies every row and is
0-1, so it is a plan.

```text
root LP bound 275,164.8
  depth   1: x_P275 at 0.890, fix to 1; LP bound 275,152.8
  depth   2: x_P152 at 0.200, fix to 0; LP bound 275,151.8
  depth   3: x_P333 at 0.065, fix to 0; LP bound 275,150.9
  depth   4: x_P181 at 0.733, fix to 1; LP bound 275,137.3
  depth   5: x_P110 at 0.805, fix to 1; LP bound 275,124.9
  ...
  depth 121: x_P048 at 0.147, fix to 0; LP bound 274,898.3
  depth 122: x_P148 at 0.333, fix to 0; LP bound 274,894.9
  depth 123: x_P057 at 0.357, fix to 0; LP bound 274,886.0
dive ends after 123 fixings (0 fixed the other way after an infeasible LP)
plan value 274,886, breaks no row
```

Read three things in it. First, new fractional variables keep appearing: P333 was 0 at the root and
is 0.065 at depth 3, because fixing P275 and P152 moved the LP point. That is why the dive takes 123
fixings to settle five fractional variables. Second, the "LP bound" column falls at every step. It
is the bound of the LP *with the fixings so far*, so it bounds only the plans the dive can still
reach, not the whole model; once it drops below a known incumbent, the dive cannot beat it and a
solver would stop it early. Third, the result: 274,886, better than rounding and filling by 468, at
the cost of 124 LP solves instead of one.

<!-- practice 2 -->

## RINS Solves a Small MIP Where the Incumbent and the LP Disagree

Once there is an incumbent, a different idea works. Compare it with the LP optimum. Where both say 1,
or both say 0, the decision is probably right. Where they disagree, it is in doubt. **RINS**
(Relaxation Induced Neighborhood Search) fixes every variable on which they agree and solves the
MIP that is left, which is small, exactly:

```python
def rins_fixings(incumbent: dict[str, int], x: dict[str, float]) -> dict[str, int]:
    """Where the incumbent and the LP optimum agree on a 0 or a 1, fix that value."""
    return {j: incumbent[j] for j in incumbent if abs(x[j] - incumbent[j]) < EPS}


def rins(model: mathopt.Model, incumbent: dict[str, int], x: dict[str, float]) -> tuple[dict[str, int], int]:
    """Solve the sub-MIP left after fixing every variable the incumbent and the LP agree on."""
    fix = rins_fixings(incumbent, x)
    variables = {v.name: v for v in model.variables()}
    for j, v in variables.items():
        v.integer = True
        v.lower_bound, v.upper_bound = (fix[j], fix[j]) if j in fix else (0.0, 1.0)
    result = solve_quiet(model, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    plan = {j: round(result.variable_values(v)) for j, v in variables.items()}
    for v in variables.values():
        v.lower_bound, v.upper_bound = 0.0, 1.0
    return plan, len(variables) - len(fix)
```

A MIP solved inside a heuristic is a **sub-MIP**. Its **neighbourhood** is the set of plans it can
reach: those that keep every fixed variable at its value. The incumbent is one of them, so RINS
never returns a worse plan. Run from both incumbents found so far:

```text
root LP bound 275,164.8
incumbent from round down, then fill: 274,418
  it agrees with the LP on 383 of 400 variables (292 at 1, 91 at 0)
  sub-MIP over the 17 free variables: value 274,418, breaks no row, changes 0 decisions
incumbent from the dive: 274,886
  it agrees with the LP on 388 of 400 variables (288 at 1, 100 at 0)
  sub-MIP over the 12 free variables: value 274,922, breaks no row, changes 2 decisions
```

From the filled plan, the 17 free variables hold no better plan: the incumbent was already the best
in its neighbourhood. From the dive's plan, 12 variables are free, and the sub-MIP swaps two
decisions for a plan worth 274,922, 36 more. Neither run reaches 274,999: the better plans need
changes to variables that both the LP and the incumbent agree on, and RINS never touches those.

The size of the neighbourhood is the dial. Too many free variables and the sub-MIP is as hard as the
whole model; too few and it holds nothing new. So a RINS step inside a search should give its
sub-MIP a node or time limit, and is worth running only when the incumbent and the LP disagree on
enough variables to leave something to find.

<!-- practice 3 -->

## Solvers Run Many Heuristics and Say Which One Found Each Plan

The three ideas above have many relatives in every MIP solver: feasibility pump, shifting, local
branching, RENS (a cousin of RINS that needs no incumbent: it fixes the variables the LP already has
at whole values). They run at the root and at some nodes, and a solver tracks which one found each
new incumbent. Switching them off through MathOpt's common `heuristics` parameter, on SCIP:

```python
for label, heuristics in (("heuristics on (default)", None), ("heuristics off", mathopt.Emphasis.OFF)):
    result = solve_quiet(model, mathopt.SolverType.GSCIP, mathopt.SolveParameters(heuristics=heuristics))
    print(f"SCIP, {label:23}: {result.termination.reason.name}, value {result.objective_value():,.0f}, "
          f"nodes {result.solve_stats.node_count:,}, LP iterations {result.solve_stats.simplex_iterations:,}")
```

```text
SCIP, heuristics on (default): OPTIMAL, value 274,999, nodes 718, LP iterations 4,547
SCIP, heuristics off         : OPTIMAL, value 274,999, nodes 1,333, LP iterations 8,278
```

The answer is the same, since heuristics never change the optimum, only how soon good plans appear.
Without them SCIP needed 1,333 nodes instead of 718 and nearly twice the LP iterations. That is what
the pruning rule predicts: with fewer good plans found early, fewer nodes can be dropped.

HiGHS's log names the source of every new incumbent in its first column, with a letter: `R` for
randomized rounding, `L` for a sub-MIP heuristic (the family RINS belongs to), `J` for feasibility
jump, and so on. On the five-year model, the incumbents HiGHS found before its first branch came
from five different sources, among them randomized rounding and sub-MIPs. HiGHS's option list
has a switch for several of its heuristics: feasibility jump, RINS and RENS are on by default, ZI
Round and shifting off, and `mip_heuristic_effort` (0.05 by default, on a scale from 0 to 1) sets
the effort spent on them. Lesson 3.3.4 reads that log line by line.

## Summary

- **A heuristic finds plans, and the best one so far is the incumbent.** Its value is the primal
  bound; the LP relaxation's value is the dual bound; the gap between them measures what is left to
  prove.
- **Rounding down keeps a packing plan feasible, rounding to nearest does not.** On the five-year
  model, nearest overspends two years; down gives 271,019.
- **A greedy fill spends what rounding left unspent:** 274,418, within 0.27% of the LP bound.
- **Diving fixes one variable, re-solves the LP, and repeats:** 274,886 after 123 fixings.
- **RINS solves a small MIP where the incumbent and the LP disagree:** from the dive's plan, 12 free
  variables give 274,922. It never returns a worse plan.
- **Solvers run many heuristics and say which one found each plan.** SCIP without them needed 1,333
  nodes instead of 718.

## Reference

| Term | Meaning |
| --- | --- |
| primal heuristic | a fast procedure that tries to find feasible plans, with no guarantee |
| incumbent | the best feasible plan found so far; its value is the primal bound |
| dual bound | a value no plan can beat, such as the LP relaxation's (for a maximization) |
| packing row | a $`\le`$ row with nonnegative coefficients; rounding down never breaks it |
| greedy fill | add unfunded items, best value per unit of weight first, when they fit |
| diving | fix one variable, re-solve the LP, repeat until the LP point is integral |
| fractional diving | fix the least fractional variable to its nearest value |
| RINS | fix variables where incumbent and LP optimum agree; solve the sub-MIP left |
| sub-MIP | a MIP solved inside a heuristic, usually with a node or time limit |
| neighbourhood | the plans a sub-MIP can reach |

**Further reading:** [MathOpt `SolveParameters` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py) (the common `heuristics` parameter, the effort spent finding feasible plans beyond the search itself); [MathOpt `ModelSolveParameters` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py) (`solution_hints`, the way to hand a MIP solver your own plan); [HiGHS option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (the `mip_heuristic_*` switches: feasibility jump, RINS, RENS, ZI Round, shifting, and the effort setting); [HiGHS: Further features, MIP](https://ergo-code.github.io/HiGHS/dev/guide/further/) (a supplied plan becomes HiGHS's first primal bound); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.5: a good integer solution found early lets branch-and-bound drop many subdivisions).

| Heuristic | Five-year model value | LP solves or sub-MIPs |
| --- | --- | --- |
| round down | 271,019 | 1 LP |
| round down, then fill | 274,418 | 1 LP |
| fractional diving | 274,886 | 124 LPs |
| RINS from the dive's plan | 274,922 | 1 sub-MIP over 12 variables |
| optimum | 274,999 | (HiGHS, zero gap tolerance) |

## Challenges

1. Change `greedy_fill` to sort by value alone, not value per $k. Predict whether the plan gets
   better or worse, then run it.
2. Change the dive to pick the *most* fractional variable instead. How many fixings does it take, and
   what does it find?
3. Run RINS from the plain rounded-down plan (271,019). How many variables are free, and how good is
   the sub-MIP's plan?

## Design Note: Give the Solver Your Own Plan

Planners often have a plan already: last year's portfolio rolled forward, or a ranking a team agreed
on. Handing it to the solver as a starting incumbent (a **MIP start**, or "hint") gives the search a
primal bound from the first node and RINS a neighbourhood to search, at no cost. Lesson 2.4.3
covered warm starts for LPs; for a MIP, MathOpt passes such a plan as a solution hint,
`ModelSolveParameters(solution_hints=[...])`, and a solver that accepts only one hint takes the
first. HiGHS's documentation describes what it does with a plan supplied through its own interface:
it solves the model with the plan's integer values fixed, and a feasible result gives the search its
first primal bound. A plan the business already trusts is also a good test: if the solver's
answer is worse than it, the model is wrong.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of
the code, so the course's own files never change.

**rounding.py.** Rounds the five-year model's LP optimum down and to nearest, then fills greedily
(*Rounding Down*, *A Greedy Fill*). *Try:* Fill from the nearest-rounded plan with the overspending
projects removed. Predict whether it beats 274,418.

- Program: [rounding.py](src/rounding.py)

**diving.py.** Fractional diving on the five-year model, printing the first and last fixings
(*Diving*). *Try:* Print every step. Predict at which depth the LP bound first drops below 275,000.

- Program: [diving.py](src/diving.py)

**rins.py.** RINS from two incumbents: rounding with fill, and the dive (*RINS*). *Try:* Fix only the
variables where both say 1 and leave every 0 free. Predict how many variables become free.

- Program: [rins.py](src/rins.py)

**heuristics_off.py.** SCIP on the five-year model with its heuristics on and off (*Solvers Run Many
Heuristics*). *Try:* Set `heuristics` to `mathopt.Emphasis.HIGH`. Predict the node count.

- Program: [heuristics_off.py](src/heuristics_off.py)

**heuristics.py.** `Relaxation`, `broken`, `value`, the two roundings, `greedy_fill`, `dive`, and RINS.

- Library: [heuristics.py](src/heuristics.py)

**presolve.py.** The `BinaryModel` the heuristics check plans against (lesson 3.3.2).

- Library: [presolve.py](src/presolve.py)
