# 11.3.4 Column Generation in One Worked Example

GridCap's vegetation program has its season's tasks counted: 48 spans to trim, 30 hazard trees to
remove, 22 corridors to clear, 14 rights-of-way to widen and 17 sites of storm debris. Each kind of
task takes a known number of minutes, and one crew-day has 600 minutes of work in it. The
vegetation manager asks: how few crew-days cover the season? A crew-day is a **pattern**: so many
tasks of each kind that fit in 600 minutes. There are hundreds of possible patterns, and on a real
season with dozens of task kinds there are millions. **Column generation** solves the problem
without listing them: it starts with a handful, and asks a small optimization problem, the
**pricing problem**, for the one pattern that would improve the plan most, until no pattern
would. This lesson walks one example end to end: the model, the first iteration by hand, the loop,
the integer answer, and a check against a compact model solved directly.

The program is adapted from the OR-Tools MathOpt example `cutting_stock.py`, which cuts boards into
pieces; here a crew-day is "cut" into tasks. The task data is invented for the lesson; GridCap is a
fictional utility.

## The Model

**Sets.** $`K`$ the kinds of task (trim span, hazard tree, clear corridor, widen right-of-way,
storm debris); $`\Pi`$ every feasible pattern, a pattern $`p`$ being a vector of whole numbers
$`a_{k,p}`$, the tasks of kind $`k`$ done in one crew-day with pattern $`p`$.

**Parameters.** $`w_k`$, the minutes one task of kind $`k`$ takes (55, 110, 250, 340, 190);
$`d_k`$, the tasks of kind $`k`$ to do this season (48, 30, 22, 14, 17); $`W = 600`$, the minutes
in a crew-day. A pattern is feasible when $`\sum_k w_k\, a_{k,p} \le W`$ and $`0 \le a_{k,p} \le d_k`$.

**Variables.** $`\lambda_p \in \mathbb{Z}_{\ge 0}`$ for every $`p \in \Pi`$: the number of
crew-days worked with pattern $`p`$. In code, `days_0`, `days_1`, …

**Objective.**

```math
\min \; \sum_{p \in \Pi} \lambda_p
```

**Constraints.**

```math
\sum_{p \in \Pi} a_{k,p}\, \lambda_p \;\ge\; d_k \qquad \forall k \in K \qquad \text{(cover}_k)
```

Five rows and one column per pattern: a tall, thin matrix of the kind lesson 2.2.2's simplex
never sees all of at once. The rows are $`\ge`$, not $`=`$: a crew-day may finish a task kind early
and do fewer of something than its pattern allows (the OR-Tools sample writes equalities; with
$`\ge`$ the duals below are never negative, which keeps the pricing problem simple).

## Each Column Is a Pattern, and the Master LP Needs Only a Few of Them

Column generation works on the LP relaxation first ($`\lambda_p \ge 0`$, continuous) over a
**restricted master**: the same rows with only some of the columns. It starts from the simplest
patterns, one kind of task per day, as many as fit:

```python
for t, (minutes, need) in tasks.items():          # start: one single-task day per task
    add_pattern({t: min(need, day // minutes)})
```

A column enters the MathOpt model with an objective coefficient of 1 and its counts in the cover
rows, the way the OR-Tools sample adds one:

```python
lam = master.add_variable(lb=0, name=f"days_{len(patterns)}")
master.objective.set_linear_coefficient(lam, 1)
for t, count in pattern.items():
    cover[t].set_coefficient(lam, count)
```

`first_pricing.py` builds that first restricted master and solves it with GLOP:

```text
trim span            55 min x 48 tasks   start day: 10 per day
hazard tree         110 min x 30 tasks   start day:  5 per day
clear corridor      250 min x 22 tasks   start day:  2 per day
widen right-of-way  340 min x 14 tasks   start day:  1 per day
storm debris        190 min x 17 tasks   start day:  3 per day
master LP: 41.467 crew-days
```

With single-task days the LP needs 48/10 + 30/5 + 22/2 + 14/1 + 17/3 = 41.467 days. That is a
feasible LP plan of the restricted master, so the full master LP's optimum is at most 41.467. The
question is which pattern to add.

## The Master's Duals Price Each Task, and the Pricing Problem Finds the Best New Day

Read the dual value $`\pi_k`$ of each cover row (lesson 2.3.3): the crew-days one more task of kind
$`k`$ would cost the current plan. A new pattern $`p`$ costs one crew-day and does the work of
$`\sum_k \pi_k a_{k,p}`$ crew-days at those prices, so its **reduced cost** (lesson 2.3.3) is

```math
\bar c_p \;=\; 1 - \sum_{k \in K} \pi_k\, a_{k,p}.
```

A pattern with $`\bar c_p < 0`$ would lower the LP's optimum if added; if no pattern has one, the
restricted master's optimum is the full master's (the simplex optimality test of lesson 2.2.2,
applied to columns not yet written down). Finding the most negative reduced cost is itself an
optimization problem over all patterns, the **pricing problem**, here a bounded integer knapsack:

```math
v^* \;=\; \max \; \sum_{k \in K} \pi_k\, a_k \quad \text{s.t.} \quad \sum_{k \in K} w_k\, a_k \le W, \qquad a_k \in \{0, 1, \dots, d_k\} \;\; \forall k \in K \qquad \text{(day)}
```

`colgen.price_pattern` writes it in MathOpt and solves it with HiGHS (the OR-Tools sample uses
CP-SAT):

```python
m = mathopt.Model(name="pricing")
a = {t: m.add_integer_variable(lb=0, ub=need, name=f"a_{t}") for t, (_, need) in tasks.items()}
m.add_linear_constraint(sum(minutes * a[t] for t, (minutes, _) in tasks.items()) <= day, name="day")
m.maximize(sum(prices[t] * a[t] for t in tasks))
```

The first iteration, by hand and by program:

```text
prices (crew-days per task): trim span 0.100, hazard tree 0.200, clear corridor 0.500, widen right-of-way 1.000, storm debris 0.333
pricing: best day {'clear corridor': 1, 'widen right-of-way': 1} worth 1.500 days of work, reduced cost -0.500
```

Each price is one over the tasks a single-task day holds: a widen-right-of-way task takes a whole
day of its own (price 1.000), a corridor half a day. A day doing one corridor and one widening uses
250 + 340 = 590 minutes and does 1.5 days' worth of the current plan's work: reduced cost −0.5. Add
it, and the LP improves.

<!-- practice 1 -->

## Stop When No Day Has a Negative Reduced Cost; the Pricing Value Bounds the LP on the Way

Each iteration re-solves the master LP with the new column. `mathopt.IncrementalSolver`, as in the
OR-Tools sample, keeps GLOP's model between solves and receives only the added column (lesson 4.3.4
covers incremental solving):

```python
solver = mathopt.IncrementalSolver(master, mathopt.SolverType.GLOP)
```

```python
lp = solver.solve()
if lp.termination.reason != mathopt.TerminationReason.OPTIMAL or not lp.has_dual_feasible_solution():
    raise RuntimeError("master LP not solved")
prices = {t: lp.dual_values(cover[t]) for t in tasks}
worth, pattern = price_pattern(prices, tasks, day)
lower = lp.objective_value() / max(worth, 1.0)          # no plan uses fewer days than this
```

The `lower` line is a bound that holds before the loop ends. Every pattern does at most $`v^*`$ at
prices $`\pi`$, so the scaled prices $`\pi / v^*`$ are dual feasible for the *full* master LP; by
weak duality its optimum is at least $`\sum_k (\pi_k / v^*) d_k`$, and $`\sum_k \pi_k d_k`$ is the
restricted master's optimum $`z_{RMP}`$ (strong duality, lesson 2.3.2). So

```math
\frac{z_{RMP}}{v^*} \;\le\; z_{LP} \;\le\; z_{RMP}.
```

The same argument, one step at a time:

1. **What dual feasible means here.** The full master LP's dual has one price $`\rho_k \ge 0`$ per
   task kind, and one row per pattern: $`\sum_k a_{k,p}\, \rho_k \le 1`$ for every $`p \in \Pi`$
   (a pattern's work, valued at the prices, is worth at most the one crew-day it costs). Any such
   $`\rho`$ gives $`z_{LP} \ge \sum_k \rho_k d_k`$ (weak duality, lesson 2.3.2).
2. **The restricted master's prices may break some of those rows.** $`\pi`$ satisfies the rows of
   the patterns already in the master, but a missing pattern can be worth more than 1 at $`\pi`$.
   The pricing problem finds the worst one: no pattern is worth more than $`v^*`$.
3. **Dividing by $`v^*`$ repairs every row at once.** With $`\rho = \pi / v^*`$, each pattern's
   worth is divided by $`v^*`$ too: $`\sum_k a_{k,p}\, \pi_k / v^* \le v^* / v^* = 1`$. The prices
   stay nonnegative, so $`\rho`$ is dual feasible.
4. **Its value is the restricted master's optimum, scaled.** That is
   $`\sum_k \rho_k d_k = \bigl(\sum_k \pi_k d_k\bigr) / v^* = z_{RMP} / v^*`$, and step 1 makes
   that a lower bound on $`z_{LP}`$.

The code divides by $`\max(v^*, 1)`$: when no pattern is worth more than 1, $`\pi`$ is already dual
feasible and needs no scaling, and the bound is $`z_{RMP}`$ itself.

The loop prints both sides, keeping the best lower value seen:

```text
iter  1  master LP  41.467  best bound  27.644  best day worth 1.500  reduced cost -0.500  [1 clear corridor, 1 widen right-of-way]
iter  2  master LP  34.467  best bound  31.333  best day worth 1.100  reduced cost -0.100  [1 trim span, 2 clear corridor]
iter  3  master LP  34.067  best bound  31.938  best day worth 1.067  reduced cost -0.067  [2 hazard tree, 2 storm debris]
iter  4  master LP  33.500  best bound  31.938  best day worth 1.050  reduced cost -0.050  [3 hazard tree, 1 clear corridor]
iter  5  master LP  33.283  best bound  31.938  best day worth 1.050  reduced cost -0.050  [6 trim span, 1 clear corridor]
iter  6  master LP  33.100  best bound  33.100  best day worth 1.000  reduced cost +0.000  [5 hazard tree]
LP optimum 33.100 after 6 master solves, 10 columns; no plan uses fewer than 34 crew-days
```

The master LP falls from 41.467 to 33.1 and the bound rises from 27.644 to 33.1; at iteration 6 the
best day is worth exactly 1, no day has a negative reduced cost, and the two meet. Five columns were
added to the five starting ones: 10 columns out of the hundreds that exist. Because a crew-day count
is a whole number, the LP optimum 33.1 proves that **no plan uses fewer than 34 crew-days**. A loop
stopped early would still give an honest interval, for example $`[31.938, 33.5]`$ after iteration 4.

## Integer Answers Come From the Generated Columns, and the LP Bound Says How Good They Are

The LP answer uses fractional days. The simplest way to an integer plan is **price-and-branch**:
make the generated columns integer and solve the restricted master once as a MIP (the sample does
the same):

```python
for lam, _ in patterns:
    lam.integer = True
final = mathopt.solve(master, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
```

```text
integer master over those columns: 34 crew-days
   2 x  10 trim span  (550 min)
   2 x  5 hazard tree  (550 min)
   1 x  3 storm debris  (570 min)
  14 x  1 clear corridor, 1 widen right-of-way  (590 min)
   7 x  2 hazard tree, 2 storm debris  (600 min)
   2 x  3 hazard tree, 1 clear corridor  (580 min)
   6 x  6 trim span, 1 clear corridor  (580 min)
```

34 crew-days, and the LP said no plan uses fewer: this plan is optimal, proved by the bound, not by
listing patterns. That proof is luck of the data, not a property of the method. The best integer
plan may need a pattern the LP never priced, and then the integer master over the generated columns
ends above $`\lceil z_{LP} \rceil`$ with no proof either way. Closing that gap exactly needs
**branch-and-price**, which generates columns at every node of a branch-and-bound tree; MathOpt has
no built-in support for it, and it is beyond this lesson. The honest report in that case is the
interval $`[\lceil z_{LP} \rceil,\ z_{IP}]`$.

Some days in the plan do more than the season needs (the integer master may over-cover a $`\ge`$
row); a planner drops those tasks from the last days.

<!-- practice 2 -->

## A Compact Model of the Same Question Checks the Answer and Shows Why Patterns Help

OR-Tools' bin packing page writes the same kind of question with a variable per item and bin and a
yes/no per bin. `compact.py` does that here: a whole-number variable $`n_{k,j}`$ for the tasks of
kind $`k`$ on day $`j`$, a yes/no $`u_j`$ per day, cover rows, a 600-minute row per day, and
$`u_j \le u_{j-1}`$ so days are used in order. Any upper bound on the days will do for the number
of days; it uses 36:

```python
m.add_linear_constraint(sum(minutes * n[t, k] for t, (minutes, _) in TASKS.items()) <= DAY * use[k],
                        name=f"day_{k}")
```

```text
compact LP bound       32.383  -> proves at least 33 days
column generation LP   33.100  -> proves at least 34 days
compact MILP optimum   34 days (OPTIMAL); column generation found 34
```

Both agree on 34. The bounds do not: the compact model's LP relaxation is 32.383, the total minutes
divided by 600 (19,430 / 600), and proves only 33. Its LP may
split a 340-minute widening across two days; the pattern LP cannot, because every column is a whole
day that really fits. That is the general reason column generation is used: the pattern formulation
has a **stronger LP relaxation**, the same strength gap lesson 6.4.3 measured between aggregated
and cumulative rows, at the price of exponentially many columns that the pricing problem lets you
never write down. On this small season the compact MILP still solves. On a season with dozens of
task kinds and hundreds of days, its weaker bound and its interchangeable days (any reordering of
the days is the same plan, the symmetry lesson 6.7.3 breaks with ordering rows) work against
branch-and-bound, while the pattern model keeps one row per task kind; this lesson does not
measure that larger case.

## The Model

The restricted master and its pricing problem, whole, as column generation solves them.

**Sets.** $`K`$ the task kinds; $`\Pi' \subseteq \Pi`$ the patterns generated so far.

**Parameters.** $`w_k`$, $`d_k`$, $`W`$ as above; $`a_{k,p}`$ for $`p \in \Pi'`$; $`\pi_k`$, the
cover rows' duals after the last master solve.

**Variables.** Master LP: $`\lambda_p \ge 0`$, continuous, for $`p \in \Pi'`$ (integer, $`\lambda_p \in \mathbb{Z}_{\ge 0}`$, in the final price-and-branch solve). Pricing:
$`a_k \in \{0, 1, \dots, d_k\}`$ for every $`k \in K`$.

**Restricted master.**

```math
z_{RMP} \;=\; \min \sum_{p \in \Pi'} \lambda_p \qquad \text{s.t.} \qquad \sum_{p \in \Pi'} a_{k,p}\, \lambda_p \ge d_k \quad \forall k \in K \qquad \text{(cover}_k)
```

**Pricing problem.**

```math
v^* \;=\; \max \sum_{k \in K} \pi_k\, a_k \qquad \text{s.t.} \qquad \sum_{k \in K} w_k\, a_k \le W \qquad \text{(day)}
```

**Loop.** Add the pricing answer as a new column while $`v^* > 1`$ (its reduced cost $`1 - v^*`$ is
negative); then $`z_{RMP} = z_{LP}`$. At every iteration $`z_{RMP} / v^* \le z_{LP} \le z_{RMP}`$.

## Summary

- **Each column is a pattern, and the master LP needs only a few of them.** Start from simple
  patterns; the restricted master's optimum is an upper bound on the full LP.
- **The master's duals price each task, and the pricing problem finds the best new day.** The
  reduced cost of a pattern is $`1 - \sum_k \pi_k a_{k,p}`$; the pricing knapsack finds the most
  negative one.
- **Stop when no day has a negative reduced cost; the pricing value bounds the LP on the way.**
  $`z_{RMP}/v^*`$ is a lower bound at every iteration; here 6 master solves and 10 columns.
- **Integer answers come from the generated columns, and the LP bound says how good they are.**
  34 crew-days, proved optimal here by $`\lceil 33.1 \rceil = 34`$.
- **A compact model of the same question checks the answer and shows why patterns help.** The
  compact LP proves only 33.

## Reference

| Term | Meaning |
| --- | --- |
| column, pattern | one feasible way to fill a crew-day; one variable of the master |
| restricted master | the master LP over the columns generated so far |
| pricing problem | finds the column with the most negative reduced cost (here a bounded knapsack) |
| reduced cost of a pattern | $`1 - \sum_k \pi_k a_{k,p}`$ |
| pricing bound | $`z_{RMP} / v^* \le z_{LP}`$, valid at every iteration |
| price-and-branch | solve the integer master over the generated columns once; a heuristic with a bound |
| branch-and-price | columns generated at every node of a branch-and-bound tree; exact |

| MathOpt call | Use here |
| --- | --- |
| `mathopt.IncrementalSolver(model, SolverType.GLOP)` | re-solve the master after each added column |
| `objective.set_linear_coefficient(var, 1)` | the new column's cost |
| `constraint.set_coefficient(var, count)` | the new column's entry in a cover row |
| `result.dual_values(row)` | the task prices |
| `var.integer = True` | turn the columns integer for the final solve |

**Further reading:** [OR-Tools MathOpt sample `cutting_stock.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/cutting_stock.py) (the example adapted here: a leader LP over configurations solved with GLOP through `IncrementalSolver`, a knapsack worker on the leader's duals, a stop when the best configuration is worth at most 1 within a tolerance, and a final integer solve over the configurations generated); [Bin Packing (OR-Tools)](https://developers.google.com/optimization/pack/bin_packing) (the compact formulation with a variable per item and bin and a yes/no per bin, the model `compact.py` writes); [Applied Mathematical Programming, Chapter 12, Large-Scale Systems (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-12.pdf) (section 12.8, column generation and the cutting-stock problem: columns too many to write down, produced by a subproblem on the current prices); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the modeling API used for the master and the pricing problem).

## Challenges

1. Add a sixth task kind, "inspect span", 35 minutes, 60 tasks. Predict whether the LP optimum rises
   by more or less than $`60 \times 35 / 600 = 3.5`$ crew-days.
2. The pricing problem is a knapsack with five kinds. Solve it by dynamic programming over minutes
   instead of HiGHS, and check that the loop prints the same lines.
3. Write the cover rows as equalities, as the OR-Tools sample does. Which prices can now be
   negative, and what does a negative price mean for a task?
4. A second crew type works 480-minute days at the same cost. What changes in the master and in the
   pricing problem?

## Design Note: The Pricing Problem Is the Only Place the Day's Rules Live

The master knows nothing about minutes: it only counts tasks covered and days used. Every rule about
what one day can hold (the 600 minutes here, travel time between sites, a crew that cannot do
widening work) belongs in the pricing problem. That separation is what makes column generation
extendable: a new rule about a day changes one small model, and the master, its duals and its bound
stay as they are.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**first_pricing.py.** The first restricted master, its prices and the first pricing answer (*the first two sections*). *Try:* Change the clear-corridor time from 250 to 260 minutes. Predict the best first day.

**colgen.py.** The loop with its bounds, and the integer master over the generated columns (*the third and fourth sections*); adapted from the OR-Tools sample `cutting_stock.py`. *Try:* Start with no single-task days but one day of each task. Predict whether the loop needs more master solves.

**compact.py.** The compact model, its LP bound and its MILP optimum (*A Compact Model of the Same Question*). *Try:* Remove the `order_` rows. Predict whether the MILP optimum changes.

- Program: [first_pricing.py](src/first_pricing.py)
- Program: [colgen.py](src/colgen.py)
- Program: [compact.py](src/compact.py)
