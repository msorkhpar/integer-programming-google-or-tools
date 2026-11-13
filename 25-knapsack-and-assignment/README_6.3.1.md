# 6.3.1 0-1 and Multi-Dimensional Knapsack

GridCap's planners took lesson 3.2.4's budget-only plan to the finance team: 18 discretionary
projects worth $23,103k, fitting the capital budget with $10k to spare. Finance sent it back the same
day. The capital budget is a total over five years, but the money arrives one year at a time, and
the plan spends $12,780k in 2027, when only $7,720k is left after the must-do work. The plan fits
the one row it was given and breaks two rows it was never shown.

This lesson names the model behind both plans. The budget-only selection is the **0-1 knapsack**,
the oldest and simplest integer program; adding the five yearly budgets makes it the
**multi-dimensional knapsack**, one capacity row per resource. You will see how to solve the first
exactly without a MILP solver, why that trick and every simple ranking rule break on the second,
and what the LP relaxation looks like when there are several rows.

GridCap is a fictional utility's portfolio, generated for this course. None of its numbers describe
a real company.

## A Knapsack Is One Capacity Row Over Yes/No Items

A **knapsack problem** has a set of **items**, each with a **value** and a **weight**, and a
**capacity**. The question is which items to take so that their total weight stays within the
capacity and their total value is as large as possible. The name comes from a hiker packing a bag
with a weight limit. With one binary $`x_i`$ per item (1 if item $`i`$ is taken; lesson 3.1.1
introduced binaries) it is one row and one objective:

```math
\begin{aligned}
\max \;& \sum_{i \in I} v_i\, x_i \\
\text{s.t. }& \sum_{i \in I} w_i\, x_i \le b && \text{(capacity)} \\
& x_i \in \{0, 1\} && \forall i \in I
\end{aligned}
```

"0-1" says each item is taken whole or not at all, never twice and never in part. In GridCap's
version the items are the discretionary projects, the value is a project's NPV, the weight is its
capex and the capacity is the capital budget left after the must-do projects are paid for. Lesson
3.2.4 built this model and solved it with a branch-and-bound of its own; this module keeps the data
in a small structure, a `Row`, so that any number of capacity rows can be handed to one builder:

```python
def capital_row(portfolio: Portfolio) -> Row:
    """The capital budget, with the must-do projects paid for first (lesson 3.2.4)."""
    left = portfolio.capital_budget - sum(p.capex for p in must_do(portfolio))
    return Row("capital", {p.project_id: p.capex for p in discretionary(portfolio)}, left)
```

```python
def knapsack_model(values: dict[str, int], rows: list[Row], *, integer: bool = True):
    """max sum v_i x_i subject to every row; integer=False gives the LP relaxation (0 <= x <= 1)."""
    model = mathopt.Model(name="knapsack")
    x = {i: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}") for i in values}
    for row in rows:
        model.add_linear_constraint(sum(w * x[i] for i, w in row.weight.items()) <= row.capacity, name=row.name)
    model.maximize(sum(v * x[i] for i, v in values.items()))
    return model, x
```

`add_variable(lb=0, ub=1, is_integer=True)` is MathOpt's binary (the same as
`add_binary_variable`), and `is_integer=False` keeps the bounds and drops the whole-number
requirement, which gives the **LP relaxation**: the same model with each $`x_i`$ allowed anywhere in
$`[0, 1]`$ (lesson 3.1.1). Solved with HiGHS on GridCap small, and checked against what the plan
spends in each year if every project starts as early as it can:

```text
36 discretionary projects compete for $30,760k
best plan: 18 projects, value $23,103k, capex $30,750k
  budget_2027: the plan spends $12,780k of $7,720k left  over
  budget_2028: the plan spends $4,880k of $7,240k left
  budget_2029: the plan spends $4,580k of $8,760k left
  budget_2030: the plan spends $5,130k of $3,170k left  over
  budget_2031: the plan spends $3,380k of $7,710k left
```

The value and the plan are lesson 3.2.4's. The yearly check is new, and it is the planners' problem:
the knapsack had no way to know about 2027 and 2030, because nobody gave it those rows.

Two things the knapsack also leaves out on purpose. Lesson 3.2.4 dropped the parent and
alternative rules, so this plan funds both P030 and P031, which are alternatives (repair or replace
the same asset). Those rows are taught in lesson 6.1.3 and lessons 6.5.1 to 6.5.6; this module studies the capacity rows
on their own, and the selection model of lesson 6.3.2 puts the others back.

## A Table Over Budget Amounts Finds the Best Plan

A one-row knapsack with whole-number weights can be solved exactly without any LP. Lesson 3.1.3
counted the plans of each cost with a table over budget amounts, a method called **dynamic
programming**: solve the problem for every smaller budget, and build each answer from answers
already computed. The same table can keep the *best value* for each budget instead of a count.

Let `best[b]` be the most value the items seen so far can give within a budget of $`b`$. Before any
item, every entry is 0. When an item of weight $`w`$ and value $`v`$ arrives, the best plan for
budget $`b`$ either leaves it out (value `best[b]`, already in the table) or takes it, and then the
rest must fit in $`b - w`$ (value `best[b - w] + v`). So

```math
\text{best}_{\text{new}}[b] = \max\big(\text{best}[b],\; \text{best}[b - w] + v\big) \qquad \text{for } b \ge w
```

and the plan is recovered afterwards by remembering, for each item and budget, which choice won:

```python
def best_plan(items: list[tuple[str, int, int]], budget: int):
    """items are (name, value, cost) with whole-number costs. Returns best[0..budget] and one best plan."""
    best = [0] * (budget + 1)       # best[b]: the most value the items seen so far give within b
    took = []                       # took[k][b]: item k is in the best plan for budget b
    for name, value, cost in items:
        row = [False] * (budget + 1)
        for b in range(budget, cost - 1, -1):           # downward, so each item is used at most once
            if best[b - cost] + value > best[b]:
                best[b] = best[b - cost] + value
                row[b] = True
        took.append(row)
    plan, b = [], budget
    for (name, value, cost), row in zip(reversed(items), reversed(took)):
        if row[b]:                                      # item k was taken for budget b: undo it
            plan.append(name)
            b -= cost
    return best, plan[::-1]
```

The loop over $`b`$ runs downward for the reason lesson 3.1.3 gave: `best[b - cost]` must still hold
the value from *before* this item, so the item cannot join a plan that already contains it. The
recovery walks the items backwards. If item $`k`$ won at budget $`b`$, it is in the plan, and the
rest of the plan is the best plan of the earlier items for $`b - w_k`$; if it did not win, the plan
for $`b`$ is the earlier items' plan for $`b`$ itself.

Every GridCap amount is a multiple of $10k, so the program divides weights and budget by their
greatest common divisor first; the table then has one column per $10k:

```text
unit $10k; table of 36 items x 3,077 budget steps
best value $23,103k with 18 projects: P002 P004 P008 P011 P014 P015 P018 P019 P021 P025 P026 P028 P030 P031 P032 P034 P035 P038
HiGHS: $23,103k, same plan: True
the same table answers every smaller budget:
  $20,000k -> $16,225k
  $25,000k -> $19,447k
  $28,000k -> $21,394k
  $30,000k -> $22,635k
  $30,760k -> $23,103k
```

The table agrees with HiGHS, plan and value. It also answers a question HiGHS would need one solve
per budget for: the last entry of each column is the best value for that budget, so the planners
get the whole value-against-budget curve from one pass. The work is one step per item per budget
step, $`36 \times 3{,}077`$ here. As lesson 3.1.3 explained, that is **pseudo-polynomial**: it grows
with the size of the capacity as a number, so the same data in dollars instead of $10k would make
the table ten thousand times longer.

<!-- practice 1 -->

## Each Extra Resource Is One More Capacity Row

Finance's objection is that money is a resource *per year*. A project that starts in year $`s`$
spends $`\text{cost}_{i,k}`$ in year $`s + k`$ (its cost profile), and each year has its own
budget. Keep every project at its earliest start, as the one-period model does, and each year
becomes one more capacity row over the same binaries. The weight of project $`i`$ in year $`y`$'s
row is what it spends that year, $`a_{i,y}`$, which is 0 in a year it does not touch:

```python
def year_rows(portfolio: Portfolio) -> list[Row]:
    """One row per year: what each project spends that year if it starts as early as it can."""
    rows = []
    for year in portfolio.years:
        must = sum(p.spend(p.earliest_start).get(year, 0) for p in must_do(portfolio))
        weight = {p.project_id: p.spend(p.earliest_start)[year] for p in discretionary(portfolio)
                  if year in p.spend(p.earliest_start)}
        rows.append(Row(f"budget_{year}", weight, portfolio.budget[year] - must))
    return rows
```

A knapsack with several capacity rows over the same items is a **multi-dimensional knapsack**
(MKP): each row is one "dimension" of the bag (weight, volume, money in 2027, money in 2028, ...),
and an item must fit in all of them at once. It is the classic **capital budgeting** model: a set
of go/no-go investments, each using several limited resources, the most total value. The
`knapsack_model` builder above takes the rows as a list, so the MKP is the same call with six rows
instead of one:

```text
capital row only: 18 projects, value $23,103k
capital and 5 yearly rows: 21 projects, value $20,183k
row          uses     left   slack
capital     30,700   30,760      60
budget_2027  7,460    7,720     260
budget_2028  7,200    7,240      40
budget_2029  8,060    8,760     700
budget_2030  3,090    3,170      80
budget_2031  4,890    7,710   2,820
```

The plan finance can actually pay for is worth $20,183k, $2,920k less than the budget-only plan
promised. **Slack** is capacity left unused, $`b_r - \sum_i a_{r,i}\, x_i`$. Five of the six rows
end with less than $1,000k of slack, so five resources shape this plan, not one. The capital row
still matters: the yearly budgets add up to $34,600k, more than the $30,760k total, so without the
capital row the plan could overspend the total while keeping every year in budget.

OR-Tools also ships a solver for exactly this model, without MathOpt: `KnapsackSolver` in
`ortools.algorithms.python.knapsack_solver`, whose branch-and-bound solver type is named for the
multi-dimensional case. It takes the values, one list of weights *per row*, and one capacity per
row, all whole numbers. The program below is the OR-Tools knapsack example run on GridCap's rows:

```python
    weights = [[row.weight.get(p.project_id, 0) for p in projects] for row in rows]   # one list per row
    capacities = [row.capacity for row in rows]
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "GridCapSmall")
    solver.init(values, weights, capacities)
    best = solver.solve()
    packed = [p.project_id for k, p in enumerate(projects) if solver.best_solution_contains(k)]
```

```text
1 row(s): value $23,103k, 18 projects
6 row(s): value $20,183k, 21 projects
```

Same answers as HiGHS. `KnapsackSolver` only accepts this one shape (whole-number weights, `<=`
rows, items taken at most once), so as soon as the plan needs a must-do, a parent rule or a timing
choice, you are back in MathOpt. Here it serves as an independent check of the MIP, the way brute
force checked lesson 3.2.4's search; lesson 4.7.4 teaches its API and when to prefer it.

<!-- practice 2 -->

## With Several Rows, No Single Ratio Ranks the Items

With one row, lesson 3.2.4 ranked items by value per unit of weight, $`v_i / w_i`$, and filling the
budget in that order gave the LP optimum (Dantzig's bound) and a good whole plan. With six rows,
which weight? A project can be cheap in total and expensive in the one tight year. Three greedy
rules, each taking projects best score first and only if they still fit every row:

```python
def greedy(score) -> tuple[int, int]:
    """Take projects best score first, each one only if it still fits every row."""
    left = {row.name: row.capacity for row in rows}
    value = count = 0
    for p in sorted(projects, key=score, reverse=True):
        if all(row.weight.get(p.project_id, 0) <= left[row.name] for row in rows):
            for row in rows:
                left[row.name] -= row.weight.get(p.project_id, 0)
            value, count = value + p.value, count + 1
    return value, count
```

The third rule divides by a **scaled use**: the share of each row's capacity the project uses,
added up, so a project heavy in a tight year scores worse than one equally expensive in a slack one:

```python
def scaled_use(p) -> float:
    """The share of each row's capacity the project uses, added up over the rows."""
    return sum(row.weight.get(p.project_id, 0) / row.capacity for row in rows)
```

```text
greedy by value / capex                   $19,346k with 22 projects (-837)
greedy by value / first-year spend        $19,230k with 20 projects (-953)
greedy by value / scaled use of all rows  $19,855k with 22 projects (-328)
optimum                                  $20,183k
```

Every rule falls short, by $328k to $953k. The scaled rule does best, and it still misses, because
any single score has to fix the trade-off between rows *before* knowing which rows will end up
tight, and that depends on which projects are chosen. Greedy rules are useful starting plans
(lesson 3.3.3 treats such **primal heuristics**), never proofs.

The LP relaxation changes too. With one row it had a single fractional item, the split item. With
six rows:

```text
LP relaxation $21,149.21k; 4 fractional projects, 6 rows:
  P024 0.341, P030 0.339, P032 0.017, P036 0.088
```

Four fractional projects. A vertex optimum never has more than six, and here is why. When an LP has
an optimum, it has one at a **vertex** of the feasible region, and the simplex method returns such a
vertex (lessons 2.2.1 and 2.2.2). A vertex is a point where $`n`$ independent constraints hold with
equality, $`n`$ being the number of variables (36). Those tight constraints are rows or
bounds ($`x_i = 0`$ or $`x_i = 1`$). There are only 6 rows, so at least $`36 - 6 = 30`$ of them are
bounds, and those 30 variables sit at 0 or 1. At most $`m`$ variables, one per row, can be
fractional at a vertex of an $`m`$-row knapsack. With $`m = 1`$ that is Dantzig's single split
item; with many rows, many fractions to branch on.

Dynamic programming does not escape either. The table needs one axis per row, because "best value
within $`b`$" becomes "best value within $`b_1`$ in row 1 and $`b_2`$ in row 2 and ...":

```text
with all 6 rows the table needs one axis per row: 3.71e+17 cells per item
```

That is why the multi-dimensional knapsack is solved as a MILP, by branch-and-bound on the LP
relaxation, and why lesson 6.3.3 works on making that relaxation tighter.

## The Model

The multi-dimensional knapsack of GridCap small, with the 0-1 knapsack as its one-row case. Must-do
projects are paid for before the model is built and have no variable.

**Sets.** $`P`$, the discretionary projects (36 on GridCap small); $`R`$, the capacity rows: the
capital budget and one row per year $`y \in Y`$ (2027 to 2031).

**Parameters.** $`v_i`$, the NPV of project $`i`$ if it starts as early as it can ($k);
$`a_{r,i} \ge 0`$, what project $`i`$ uses of row $`r`$: its capex for the capital row, its spend in
year $`y`$ for row $`y`$ ($k); $`b_r`$, what is left of row $`r`$ after the must-do projects ($k).

**Variables.**

```math
x_i \in \{0, 1\} \quad \forall i \in P \qquad \text{(1 if project } i \text{ is funded)}
```

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B - \textstyle\sum_{j \in M} \text{capex}_j && && \text{(capital)} \\
\sum_{i \in P} a_{y,i}\, x_i &\le B_y - \textstyle\sum_{j \in M} a_{y,j} && \forall y \in Y && \text{(budget}_y) \quad \leftarrow \text{the extra dimensions}
\end{aligned}
```

$`M`$ is the set of must-do projects, $`B`$ the capital budget and $`B_y`$ year $`y`$'s budget.
The 0-1 knapsack is the model with the capital row alone. The code names the rows `capital` and
`budget_2027` to `budget_2031`.

## Summary

- **A knapsack is one capacity row over yes/no items.** $`\max \sum v_i x_i`$ subject to
  $`\sum w_i x_i \le b`$, $`x_i \in \{0,1\}`$; GridCap's budget-only selection is one.
- **A table over budget amounts finds the best plan.** With whole-number weights, dynamic
  programming takes one step per item per budget unit and gives the best value for every budget at
  once; its work grows with the capacity as a number (pseudo-polynomial).
- **Each extra resource is one more capacity row.** The multi-dimensional knapsack adds a row per
  resource; on GridCap small the five yearly budgets cut the plan from $23,103k to $20,183k.
- **With several rows, no single ratio ranks the items.** Greedy rules miss the optimum, the LP has
  up to one fractional item per row, and the DP table needs one axis per row.

## Reference

| Model | Rows | Solved by |
| --- | --- | --- |
| 0-1 knapsack | one capacity row | DP over budget amounts, branch-and-bound (lesson 3.2.4), any MILP solver |
| multi-dimensional knapsack | one row per resource | a MILP solver, or `KnapsackSolver` for the pure form |

| Fact | Why |
| --- | --- |
| LP of a 1-row knapsack has at most 1 fractional item | a vertex has at most one fractional variable per row |
| LP of an $`m`$-row knapsack has at most $`m`$ | same argument |
| DP work is $`n \times b`$ steps | one step per item per unit of capacity |

**Further reading:** [The Knapsack Problem (OR-Tools)](https://developers.google.com/optimization/pack/knapsack) (the example adapted in `knapsack_solver_run.py`: `KnapsackSolver` with its multidimensional branch-and-bound type, one list of weights per capacity, and whole-number data only); [OR-Tools sample knapsack.py](https://github.com/google/or-tools/blob/stable/ortools/algorithms/samples/knapsack.py) (the guide's example as a complete program); [MathOpt getting started (OR-Tools)](https://developers.google.com/optimization/math_opt/basic_example) (building a MathOpt model with `add_variable` and `add_linear_constraint`, solving it, and checking the termination reason before reading any value); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: capital budgeting as go/no-go investments under several resource rows, cash-flow rows by period, and the 0-1 knapsack as its one-row case).

## Challenges

1. Run `best_by_table.py` with the unit forced to $1k instead of $10k. Predict the table's size and
   whether the plan changes.
2. Drop the capital row from `yearly_rows.py` and keep the five yearly rows. Predict whether the
   value rises, and which row the new plan breaks.
3. Invent a greedy score that beats $19,855k on this instance. Is there one score that would find
   the optimum on every instance? Why not?

## Design Note: Keep the Rows as Data

The builder in this lesson takes rows as data (`Row(name, weight, capacity)`) rather than writing
each budget as its own line of model code. That made the multi-dimensional knapsack the same call as
the one-row knapsack, and it lets the same rows feed MathOpt, `KnapsackSolver`, the greedy rules and
lesson 6.3.3's cover cuts. When a model has many rows of one shape, build the shape once and
generate the rows from the data; a planner adding a sixth year then changes data, not code.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**one_row.py.** Solves GridCap small's budget-only knapsack and checks the plan against each year's
budget (*A Knapsack Is One Capacity Row Over Yes/No Items*). *Try:* Print the plan's spend in 2027
project by project. Predict which projects make it overspend.

- Program: [one_row.py](src/one_row.py)

**best_by_table.py.** The dynamic program, checked against HiGHS, with the best value for several
budgets (*A Table Over Budget Amounts Finds the Best Plan*). *Try:* Print `best` at every $1,000k.
Predict whether the curve ever falls as the budget rises.

- Program: [best_by_table.py](src/best_by_table.py)

**yearly_rows.py.** The multi-dimensional knapsack with the capital row and five yearly rows, and each
row's slack (*Each Extra Resource Is One More Capacity Row*). *Try:* Raise the 2030 budget by
$1,000k. Predict which row becomes the tightest.

- Program: [yearly_rows.py](src/yearly_rows.py)

**knapsack_solver_run.py.** OR-Tools' `KnapsackSolver` on the same one and six rows, adapted from the
OR-Tools example `ortools/algorithms/samples/knapsack.py` (*Each Extra Resource Is One More Capacity
Row*). *Try:* Pass a negative weight. Predict what the solver does with it.

- Program: [knapsack_solver_run.py](src/knapsack_solver_run.py)

**no_single_ratio.py.** Three greedy rules against the optimum, and the LP relaxation's fractional
projects (*With Several Rows, No Single Ratio Ranks the Items*). *Try:* Keep only the capital row.
Predict how many fractional projects the LP has.

- Program: [no_single_ratio.py](src/no_single_ratio.py)

**knapsack_models.py.** The rows, the knapsack builder, the selection model, the crews of lesson
6.3.2 and the quiet HiGHS solve that every program of this module shares. It prints nothing.

- Library: [knapsack_models.py](src/knapsack_models.py)
