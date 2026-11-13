# 10.2.3 Alternative Optima and Deterministic Tie-Breaking

Lesson 10.2.1 left GridCap's board with two lists of 33 projects, both optimal, from two runs of the
same program. Pinning threads, seeds and limits (lesson 10.2.2) makes each run repeat, but it only
makes the program pick the *same* tied plan each time on one setup; a new solver version, a
different seed or a different build order can still pick another. The board needs one plan of
record, and a rule that says why it is that one. That rule is a **tie-break**: a way to choose among
equally good plans that does not depend on how the solver happened to search.

This lesson counts the tied plans, shows why "optimal" itself is a range, and builds two tie-breaks:
a second real criterion solved in two passes, and a single solve with a small weight ε. Both are
easy to get wrong in ways the programs show. GridCap is a fictional utility's portfolio.

## A Tied Model Has Many Optimal Plans, and "Optimal" Is a Range

Plans that reach the optimal objective value are called **alternative optima**. To count them, solve,
forbid the plan just found with a **no-good row**, and solve again with the objective held at its
optimum. If plan $`S`$ is the set of starts $`(i, t)`$ with $`x_{i,t} = 1`$, the no-good row says at
least one of them must go:

```math
\sum_{(i,t) \in S} x_{i,t} \;\le\; |S| - 1
```

```python
found = []
while len(found) < 20:
    result = solve_highs(plan.model, EXACT)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        break
    starts = schedule(plan, result)
    found.append(starts)
    chosen = [plan.x[pid, t] for pid, t in starts.items()]
    # no-good row: at least one of this plan's starts must be dropped
    plan.model.add_linear_constraint(sum(chosen) <= len(chosen) - 1, name=f"not_plan_{len(found)}")
```

The loop stops at 20 plans or when no other optimal plan exists. On the count question, with the
count held at 33 by a row `keep_count`, and then on the NPV question:

```text
most projects: 33; distinct plans found with 33: 20 (search stopped at 20)
plan 1 12f569bdae55 NPV 19,118
plan 2 f720644ae121 NPV 19,288
  only in plan 1: [('P008', 2031), ('P011', 2031), ('P013', 2028), ('P020', 2030), ('P024', 2030), ('P029', 2030)]
  only in plan 2: [('P008', 2030), ('P011', 2030), ('P013', 2029), ('P020', 2031), ('P024', 2028), ('P029', 2031)]
highest NPV: 24,260 with plan 092777a3fdd1; another plan with 24,260: INFEASIBLE
```

At least 20 plans fund 33 projects; the search stopped there, not the supply. The first two fund
the same 33 projects and differ only in when six of them start, which the count cannot see but
finance can: $170k of NPV apart. The NPV question has exactly one best plan, since forbidding it
leaves no other plan worth $24,260k. So ties come from the question, and a question that weighs
every project alike, or that ignores timing, has many.

There is a second, quieter way for "the optimal plan" to be several plans. A MIP solver stops when
its **gap** (the distance between the best plan found and the best bound, lesson 3.4.1) is within a
tolerance, and reports OPTIMAL. Gurobi's default relative tolerance, `MIPGap`, is $`10^{-4}`$, and
in lesson 10.2.2 four Gurobi settings all reported OPTIMAL on GridCap medium with four objectives
from 226,807 to 226,815: each was within 0.01% of the best bound, so each counted. HiGHS's
`mip_rel_gap` has the same default. Even a model with one true optimum can return different
"optimal" plans under different settings unless the gap tolerance is 0 (affordable on small models,
as in this lesson's programs) or the tie-break is wide enough to matter at that tolerance. Lesson
10.1.1 explains why tolerances exist at all. A seed, by contrast, changes only the search path; the
model, and so its true optimum, is the same for every seed.

## A Second Real Criterion, Solved in Two Passes, Picks One Plan

The best tie-break is a reason a planner would accept. Among the plans that fund the most projects,
finance prefers the one worth the most NPV. That is a **lexicographic** objective: first the count,
then the NPV, with the first never traded for the second (lesson 8.2.1 treats such hierarchies with
tolerances in general). Solved in two passes over lesson 10.2.1's model:

```math
\begin{aligned}
z_1 &= \max \sum_{i \in P} \sum_{t \in T_i} x_{i,t} && \text{(pass 1)} \\
z_2 &= \max \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \;\;\text{s.t.}\;\; \sum_{i \in P} \sum_{t \in T_i} x_{i,t} \ge z_1 && \text{(pass 2, row keep\_count)}
\end{aligned}
```

The count is a whole number, so pass 2 holds it exactly, with no tolerance. To check that the result
is a single plan, a third solve holds both values and adds a no-good row against the plan; if that
solve is infeasible, no other plan matches on both criteria:

```python
def two_pass_highs(portfolio, order) -> dict:
    plan = build(portfolio, order, objective="count")
    most = round(solve_highs(plan.model, EXACT).objective_value())              # pass 1
    plan.model.add_linear_constraint(sum(plan.x.values()) >= most, name="keep_count")
    npv = sum(portfolio.project(i).npv[t] * v for (i, t), v in plan.x.items())
    plan.model.maximize(npv)                                                    # pass 2
    result = solve_highs(plan.model, EXACT)
    starts, best_npv = schedule(plan, result), round(result.objective_value())
    plan.model.add_linear_constraint(npv >= best_npv, name="keep_npv")          # is it unique?
    chosen = [plan.x[k] for k in starts.items()]
    plan.model.add_linear_constraint(sum(chosen) <= len(chosen) - 1, name="not_this_plan")
    other = solve_highs(plan.model, EXACT).termination.reason.name
    return {"count": most, "npv": best_npv, "plan": digest(starts), "another plan": other}
```

`lexicographic.py` runs this in four processes with different hash seeds and the projects in a
set's order, the exact bug of lesson 10.2.1, and then does the same two passes with CP-SAT:

```text
highs hash seed 1: {"count": 33, "npv": 20082, "plan": "ca8479233142", "another plan": "INFEASIBLE"}
highs hash seed 2: {"count": 33, "npv": 20082, "plan": "ca8479233142", "another plan": "INFEASIBLE"}
highs hash seed 3: {"count": 33, "npv": 20082, "plan": "ca8479233142", "another plan": "INFEASIBLE"}
highs hash seed 4: {"count": 33, "npv": 20082, "plan": "ca8479233142", "another plan": "INFEASIBLE"}
cpsat hash seed 1: {"count": 33, "npv": 20082, "plan": "ca8479233142"}
cpsat hash seed 2: {"count": 33, "npv": 20082, "plan": "ca8479233142"}
cpsat hash seed 3: {"count": 33, "npv": 20082, "plan": "ca8479233142"}
cpsat hash seed 4: {"count": 33, "npv": 20082, "plan": "ca8479233142"}
```

Eight runs, two solvers, four build orders, one plan. The order still differs between the runs, but
it no longer has anything to choose between: the second criterion leaves a single plan, and the
third solve proves it. That is the strongest form of determinism there is, because it does not
depend on the solver at all. Any correct solver must return this plan.

When pass 2 can still tie (two plans with the same count and the same NPV), add a third criterion
the same way, or end with the stable weights of the last section.

<!-- practice 1 -->

## One Solve With an ε Weight Works Only Between Two Bounds

Two passes cost two solves. The one-solve version adds the second criterion to the first with a
small weight $`\varepsilon`$:

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} x_{i,t} \;+\; \varepsilon \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

It gives the lexicographic answer only if $`\varepsilon`$ sits between two bounds.

**Too large, and the second criterion outweighs the first.** Two counts differ by at least 1. If the
NPV term can ever be worth 1 or more, a plan with one project fewer and enough extra NPV wins. The
largest NPV any plan can have is at most $`S = \sum_i \max_t \text{npv}_{i,t}`$, so any
$`\varepsilon < 1/S`$ is safe; the program uses $`1/(S+1)`$.

**Too small, and the solver ignores it.** A solver stops when its gap is within its tolerances. HiGHS
stops when the gap is below `mip_rel_gap` (default $`10^{-4}`$) times the objective, or below
`mip_abs_gap` (default $`10^{-6}`$). Even with the relative gap set to 0, a tie-break term whose
differences are smaller than $`10^{-6}`$ is below what HiGHS promises to resolve.

```python
for label, eps in [("1e-3", 1e-3), (f"1/{most_npv + 1:,}", 1 / (most_npv + 1)), ("1e-9", 1e-9)]:
    plan = build(small, objective="count")
    npv = sum(small.project(i).npv[t] * v for (i, t), v in plan.x.items())
    plan.model.maximize(sum(plan.x.values()) + eps * npv)
    starts = schedule(plan, solve_highs(plan.model, mathopt.SolveParameters(relative_gap_tolerance=0.0)))
```

```text
largest NPV any plan could have: 38,238  -> safe eps below 1/38,239
eps 1e-3      projects 32  NPV 22,756  plan 27adc7bafd03
eps 1/38,239  projects 33  NPV 20,082  plan ca8479233142
eps 1e-9      projects 33  NPV 19,282  plan 22d7a89e7bcc
```

With $`\varepsilon = 10^{-3}`$ the NPV term is worth up to 38, far more than a project: the solve
funded 32 projects for $22,756k, a plan the board's rule forbids. With $`\varepsilon = 1/38{,}239`$
it returned the lexicographic plan, `ca8479233142`, the same as the two passes. With
$`\varepsilon = 10^{-9}`$ the count was right but the NPV was $800k short of the best: 800 times
$`10^{-9}`$ is $`8 \times 10^{-7}`$ of objective, under HiGHS's absolute gap of $`10^{-6}`$, so the
solver was entitled to stop. The gap tolerance cannot explain the lost project in the first line: a
relative gap of $`10^{-4}`$ on an objective near 33 is about 0.003, far below the 1 that a project is
worth.

The safe range here is $`10^{-6}/\Delta < \varepsilon < 1/S`$, where $`\Delta`$ is the smallest NPV
difference worth resolving. On a large portfolio the two bounds can cross, and then the two passes
are the only correct method. Notice also how the upper bound is built: the smallest gap between two
values of the first criterion (here 1, because counts are whole numbers) divided by the largest
value the second can add.

Call that smallest gap $`g`$, so the general bound is $`\varepsilon < g/S`$. When the first
criterion is not a count but a sum of whole-number scores $`p_i`$ (one per variable), you rarely
need the exact $`g`$; a safe lower bound for it is enough, because a smaller $`g`$ only makes
$`\varepsilon`$ smaller. The **greatest common divisor** of the scores gives one. Every plan's total
is a sum of some of the $`p_i`$, so the difference of two totals is a sum of scores taken with
signs $`+1`$, $`-1`$ or 0, and every such sum is a multiple of $`\gcd(p_i)`$. A positive difference
is therefore at least $`\gcd(p_i)`$. With scores 4 and 6, the gcd is 2, and the totals 0, 4, 6 and
10 are indeed never closer than 2. The bound can be loose: with scores 3 and 5 the gcd is 1, while
the totals 0, 3, 5 and 8 are never closer than 2. Using 1 there is still safe, only a little
smaller than it had to be. The smallest single score is *not* a safe bound: with scores 6, 10 and
15 the totals 15 and 16 differ by 1, less than 6.

<!-- practice 2 -->

## Tie-Break Weights Must Repeat in Every Process and Separate the Plans

Sometimes there is no second criterion a planner cares about, and any fixed choice will do, as long
as it is always the same choice. The usual trick is to give each variable a small arbitrary weight
$`w_{i,t}`$ and maximize $`\text{count} + \varepsilon \sum w_{i,t} x_{i,t}`$. A common
suggestion is to build those weights from `hash(asset_id)`. Three ways to make them, each
run in four processes with different hash seeds:

```python
def weights(keys: list[tuple[str, int]], kind: str) -> dict:
    n = len(keys)
    if kind == "hash()":                      # salted per process: a different weight every run
        return {k: hash(f"{k[0]}:{k[1]}") % n + 1 for k in keys}
    if kind == "sha256":                      # the same bytes give the same digest in every process
        return {k: int(hashlib.sha256(f"{k[0]}:{k[1]}".encode()).hexdigest(), 16) % n + 1 for k in keys}
    return {k: r + 1 for r, k in enumerate(sorted(keys))}      # "rank": 1, 2, ..., n
```

Each run uses $`\varepsilon = 1/(\sum w + 1)`$, so the weights can never outweigh a project, and a
zero gap tolerance:

```text
hash()  plans ['eb7f8c9acce1', '3933a4d2d3ef', 'f64829bfc258', 'ae17d74e7729']
        projects [33], tie-break weight of the plan [1519, 1442, 1526, 1685]
sha256  plans ['cd22d34fd5cb', 'cd22d34fd5cb', 'cd22d34fd5cb', 'cd22d34fd5cb']
        projects [33], tie-break weight of the plan [1478, 1478, 1478, 1478]
rank    plans ['d3f702c7161f', 'd3f702c7161f', '4c73ade9145e', 'd3f702c7161f']
        projects [33], tie-break weight of the plan [1281, 1281, 1281, 1281]
```

**`hash()` weights broke determinism instead of creating it.** Each process salted the hashes
differently (lesson 10.2.1), so each run maximized a different tie-break and returned a different
plan. The weights must come from something that depends only on the ids: a `hashlib` digest, or the
position in sorted order.

**Repeating weights are not enough; they must also separate the plans.** The rank weights repeat in
every process, yet two different plans came back, both with tie-break weight 1,281: two plans can
have the same total even when no two variables share a weight, and then the tie-break ties too.
Which of the tied plans a run returns then depends on the search, and the search changed between
processes: `tie_weights.py` builds the model with the projects in a set's order, which follows the
hash seed (lesson 10.2.1), so each process added the variables and rows in a different order. The
weights were identical in all four runs; the build order was the only thing that differed, and with
it HiGHS's search path, which settled the tie one way in three runs and the other way in one. The
SHA-256 weights happened to single out one plan in these runs, because their totals are spread
irregularly, but nothing guarantees it. Weights that do guarantee it are powers of two in sorted
order, $`w = 1, 2, 4, \dots, 2^{n-1}`$: every set of variables has its own total, as every whole
number has its own binary digits. They grow fast, though: GridCap small has 80 start variables, so
the largest weight would be $`2^{79}`$, about $`6 \times 10^{23}`$, and no $`\varepsilon`$ could
satisfy both bounds of the last section. Exact separation by weights is for a handful of variables.

For a real model, then, the order of preference is: a second criterion a planner accepts, solved in
two passes and checked with a no-good solve; a single solve with an ε between its bounds; and stable,
irregular weights (a digest, never `hash()`) as the last resort, with the run harness of lesson
10.2.5 to catch the cases it misses. CP-SAT's parameters proto shows the solver writers think the
same way: it has options that permute the variables and constraints at random, and it notes that
OR-Tools' own tests switch them on so that client code does not come to depend on one particular
solution when several are optimal.

<!-- practice 3 -->

## The Model

Lesson 10.2.1's timing model with the lexicographic tie-break, whole. New are the second pass, its
row $`\text{keep\_count}`$, and the uniqueness check.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of
project $`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,\tau}`$ ($k); $`B_y`$ ($k); $`z_1`$, the most
projects that fit (the value of pass 1); $`z_2`$, the best NPV with $`z_1`$ projects (the value of
pass 2); $`S^*`$, the starts of pass 2's plan.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$.

**Pass 1.** $`z_1 = \max \sum_{i \in P} \sum_{t \in T_i} x_{i,t}`$ subject to the rows below.

**Pass 2.** $`z_2 = \max \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}`$ subject to the
rows below and $`\text{keep\_count}`$.

**Uniqueness check.** Feasibility of the rows below with $`\text{keep\_count}`$,
$`\text{keep\_npv}`$ and $`\text{not\_this\_plan}`$; infeasible means pass 2's plan is the only one.

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{i \in P} \sum_{t \in T_i} x_{i,t} &\ge z_1 && && \text{(keep\_count)} \quad \leftarrow \text{pass 2 on} \\
\sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} &\ge z_2 && && \text{(keep\_npv)} \quad \leftarrow \text{check only} \\
\sum_{(i,t) \in S^*} x_{i,t} &\le |S^*| - 1 && && \text{(not\_this\_plan)} \quad \leftarrow \text{check only}
\end{aligned}
```

The one-solve variant drops pass 2 and the check, and maximizes
$`\sum x_{i,t} + \varepsilon \sum \text{npv}_{i,t}\, x_{i,t}`$ with
$`\varepsilon = 1 / (1 + \sum_i \max_t \text{npv}_{i,t})`$ and a zero gap tolerance.

## Summary

- **A tied model has many optimal plans, and "optimal" is a range.** At least 20 plans fund 33
  projects on GridCap small; the NPV question has one. A gap tolerance lets slightly different plans
  all count as optimal.
- **A second real criterion, solved in two passes, picks one plan.** Count, then NPV, with the count
  held exactly, gave one plan on two solvers and four build orders, and a no-good solve proved it
  unique.
- **One solve with an ε weight works only between two bounds.** Too large an ε traded a project for
  NPV; too small an ε fell under the solver's absolute gap and was ignored.
- **Tie-break weights must repeat in every process and separate the plans.** `hash()` weights gave
  four plans in four processes; rank weights repeated but left two plans with equal totals.

## Reference

| Tie-break | Exact? | Repeats across processes? | Cost |
| --- | --- | --- | --- |
| second criterion, two passes, `keep_count` row | yes, if it leaves one plan (check with a no-good solve) | yes | two or three solves |
| count + ε·second criterion, $`\varepsilon < g/S`$ | yes, if ε also exceeds the solver's tolerances | yes | one solve, gap tolerance 0 |
| ε·weights from `hash()` | no | no: salted per process | one solve |
| ε·weights by sorted rank | no: different plans can have equal totals | yes | one solve |
| ε·weights from a SHA-256 digest | usually separates, not guaranteed | yes | one solve |
| ε·powers of two by sorted rank | yes | yes | only for a few variables |

| Parameter | Default |
| --- | --- |
| Gurobi `MIPGap` (relative) | $`10^{-4}`$ |
| HiGHS `mip_rel_gap` | $`10^{-4}`$ |
| HiGHS `mip_abs_gap` | $`10^{-6}`$ |

**Further reading:** [CP-SAT parameters proto (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`permute_variable_randomly` and its note about not relying on one of several optimal solutions);
[MathOpt `SolveParameters` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py)
(`relative_gap_tolerance`);
[HiGHS options](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`mip_rel_gap`,
`mip_abs_gap`, `mip_feasibility_tolerance`);
[Gurobi parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
(`MIPGap`, `MIPGapAbs`);
[Python data model, `object.__hash__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
(salted `str` hashes) and [`hashlib`](https://docs.python.org/3/library/hashlib.html) (SHA-256
digests).

## Challenges

1. In `many_optima.py`, raise the limit from 20 to 200. Predict whether the loop ends by the limit
   or by INFEASIBLE, and how long it takes.
2. In `epsilon.py`, find by experiment the largest power of ten for ε that still funds 33 projects.
   Compare it with the bound $`1/38{,}239`$.
3. The board changes its rule: most projects, then the *earliest* starts. Write pass 2's objective
   and say whether it can tie.

## Design Note: Write the Tie-Break Into the Model, Not Into Luck

Every planning model has a question with ties somewhere: a count, a set of equal-cost options, a
carry-over amount (lesson 6.4.4). Leaving the choice to the solver means leaving it to thread
timing, seeds and versions. Write the rule a planner would give ("then the most NPV", "then the
earliest") as a second pass, keep its row in the model under a name, and record it in the run's
manifest. A tie-break that is part of the model can be explained to an auditor; one that is part of
the search cannot.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**many_optima.py.** Counts the plans that fund the most projects with no-good rows, and checks that
the NPV question has one best plan (*A Tied Model Has Many Optimal Plans*). *Try:* Print the NPV of
all 20 plans. Predict the range.

- Program: [many_optima.py](src/many_optima.py)

**lexicographic.py.** Most projects, then most NPV, in two passes, with a uniqueness check; four
processes per solver, each building from a set's order (*A Second Real Criterion*). *Try:* Drop
the `keep_count` row. Predict the count pass 2 returns.

- Program: [lexicographic.py](src/lexicographic.py)

**epsilon.py.** The one-solve version with three values of ε (*One Solve With an ε Weight*).
*Try:* Leave the gap tolerance at its default with ε = 1/38,239. Predict whether the plan changes.

- Program: [epsilon.py](src/epsilon.py)

**tie_weights.py.** Tie-break weights from `hash()`, SHA-256 and the sorted rank, in four processes
each (*Tie-Break Weights Must Repeat in Every Process*). *Try:* Add powers of two by sorted rank as
a fourth kind. Predict what happens to ε and to the plans.

- Program: [tie_weights.py](src/tie_weights.py)
