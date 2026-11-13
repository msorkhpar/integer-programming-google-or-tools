# 3.2.4 A Knapsack Branch-and-Bound in 116 Lines

The search of lessons 3.2.1 to 3.2.3 called GLOP at every node. That made it general (any rows at
all), at the price of an LP solve through MathOpt for every node, hundreds of them on small. GridCap's planners
often start from the simplest question the capital plan asks: with the must-do projects paid for,
which other projects give the most value for the budget that is left? That question has one row,
the budget, and an LP with one row needs no LP solver. It is solved by sorting.

This lesson builds a complete branch-and-bound for that one-row model in plain Python: the bound
in about 25 lines, the search in about 25 more, and the whole file, with its data classes, a brute
force check and the GridCap loader, in 116 lines (`knapsack.py`). The two
small programs that run it and trace it, `knapsack_run.py` and `knapsack_trace.py`, add 27 more:
143 lines in all, inside the title's 150. It then checks the result against brute
force and HiGHS, and solves the medium portfolio's 361 discretionary projects in 743 nodes.

## The Model

The budget-only selection, a **0-1 knapsack**: items with a value and a cost, a capacity, and the
question of which items to take. The name comes from packing a bag.

**Sets.** $`P`$, the projects; $`M \subseteq P`$, the must-do projects; $`D = P \setminus M`$, the
discretionary projects.

**Parameters.** $`v_i`$, the value of project $`i`$ ($k); $`c_i > 0`$, its capex ($k); $`B`$, the
capital budget ($k); $`B' = B - \sum_{i \in M} c_i`$, the budget left after the must-do projects.

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in D`$: 1 if project $`i`$ is funded. Must-do
projects are funded by definition and get no variable.

**Objective and constraint.**

```math
\begin{aligned}
\max \;& \sum_{i \in D} v_i\, x_i && \text{(plus the fixed } \textstyle\sum_{i \in M} v_i) \\
\text{s.t. }& \sum_{i \in D} c_i\, x_i \le B' && \text{(budget)}
\end{aligned}
```

This model drops the parent and alternative-group rows of lesson 3.2.1. Dropping a row is a
relaxation (lesson 3.2.1, first rule), so on the same portfolio this model's optimum is at least
the full model's, and its plan may break the dropped rules. The full model needs the GLOP-based
search of lessons 3.2.1 to 3.2.3; this lesson's point is the engine. In code, the must-do
projects are paid for before the search starts:

```python
must = [p for p in portfolio.projects if p.must_do]
items = [Item(p.project_id, p.value, p.capex) for p in portfolio.projects if not p.must_do]
return items, portfolio.capital_budget - sum(p.capex for p in must), [p.project_id for p in must]
```

## A One-Row LP Is Solved by Sorting: Dantzig's Bound

Sort the items by **ratio**, value per dollar $`r_i = v_i / c_i`$, best first. Then fill the
budget in that order: take each item whole while it fits, and take the fraction of the first item
that does not fit that uses up what is left. Stop there. The value of that fill is the LP
relaxation's optimum, and it is called **Dantzig's bound**, after George Dantzig, whose simplex
method lesson 2.2.2 built.

Why is the fill optimal for the LP? Every dollar of budget buys value at the rate of the item it
is spent on. Suppose some LP solution spends a dollar on an item with a lower ratio while an item
with a higher ratio is not fully taken. Move that dollar to the higher-ratio item: the cost is the
same and the value rises (or stays the same, on a tie). Repeat until no such move is left, and you
have the sorted fill. So no LP solution beats the fill, and since the fill obeys the row and the
bounds $`0 \le x_i \le 1`$, it is the LP optimum. At most one item, the **split item**, ends up at a
fraction.

```python
def by_ratio(items: list[Item]) -> list[Item]:
    """Best value per dollar first; ties by name, so every run takes the same path."""
    return sorted(items, key=lambda it: (-it.value / it.cost, it.name))
```

On GridCap small, after the four must-do projects are paid for:

```text
must-do P003, P010, P017, P039 funded first; 36 projects compete for $30,760k
  P034  value 2,123  cost 2,130  ratio 0.997  budget left 28,630
  P031  value 1,000  cost 1,020  ratio 0.980  budget left 27,610
  P025  value 1,009  cost 1,180  ratio 0.855  budget left 26,430
  ...
17 projects fit whole; P022 (cost 2,550) fits 0.122 of the way
Dantzig's bound: 23,168.867
```

Seventeen projects fit, and the eighteenth, P022, fits only 12.2% of the way. That fraction is the
LP's fractional variable, and it is the only one: a one-row LP has a single split item. So in this
search the variable rule of lesson 3.2.3 has nothing to choose. The split item is the branching
variable.

<!-- practice 1 -->

## Fixing an Item Changes the Budget, Not the Order

A node of the search has some items fixed at 0 and some at 1. Its LP is the same fill with two
changes: the items fixed at 1 are paid for first (whatever their ratio), and the items fixed at 0
are skipped. The free items keep their ratio order, so the list is sorted once, at the start, and
never again.

```python
def dantzig_bound(items: list[Item], budget: int, fixed: dict[str, int]) -> Relaxed | None:
    """The LP relaxation with `fixed` items held at 0 or 1. `items` must be in ratio order.

    None when the items fixed at 1 already cost more than the budget.
    """
    left = budget - sum(it.cost for it in items if fixed.get(it.name) == 1)
    if left < 0:
        return None
    value = float(sum(it.value for it in items if fixed.get(it.name) == 1))
    taken = {it.name: 1.0 for it in items if fixed.get(it.name) == 1}
    for it in items:
        if it.name in fixed:
            continue
        if it.cost <= left:
            left -= it.cost
            value += it.value
            taken[it.name] = 1.0
        else:
            share = left / it.cost
            if share > 0:
                value += share * it.value
                taken[it.name] = share
                return Relaxed(value, taken, it.name)
            return Relaxed(value, taken, None)
    return Relaxed(value, taken, None)
```

`Relaxed` holds the LP value, the items' values in the LP solution, and the split item, or `None`
when the solution is whole. Three cases end the loop. If the items fixed at 1 already cost more
than the budget, the node is infeasible and the function returns `None`. If an item does not fit and
some budget is left, that item is the split. If an item does not fit and the budget is exactly used
up (`share` is 0), or every free item fit, the LP solution is whole: an integral node.

Is this really the LP? GLOP can say. The same knapsack as a MathOpt LP (`knapsack_model` in
`selection.py`), solved at the root and at the two children of the split item:

```python
for fixed in ({}, {lp.split: 0}, {lp.split: 1}):
    glop = solve_lp(sel, fixed)
    ours = dantzig_bound(order, budget, fixed)
    print(f"fixed {str(fixed):<13} Dantzig {ours.value:>10,.3f}   GLOP {glop.value:>10,.3f}")
```

```text
fixed {}            Dantzig 23,168.867   GLOP 23,168.867
fixed {'P022': 0}   Dantzig 23,167.038   GLOP 23,167.038
fixed {'P022': 1}   Dantzig 23,100.385   GLOP 23,100.385
```

The same three values to the last digit printed, from a loop over a sorted list instead of an LP
solver. With $`n`$ items the fill takes at most $`n`$ steps, after one sort.

## The Search Is a Stack of Fixings

With the bound in hand, the search is lessons 3.2.1 and 3.2.2 put together: depth-first (a stack,
lesson 3.2.3), branching on the split item, and the three prunes.

```python
def solve(items: list[Item], budget: int, log: list[str] | None = None) -> Result:
    """The most valuable set of items whose costs fit the budget. `log`, if given, gets one line per node."""
    order = by_ratio(items)
    result = Result()
    stack: list[dict[str, int]] = [{}]
    while stack:
        fixed = stack.pop()
        result.nodes += 1
        lp = dantzig_bound(order, budget, fixed)
        if lp is None:
            result.pruned["infeasible"] += 1
            action = "infeasible"
        elif math.floor(lp.value + 1e-9) <= result.value:      # values are whole $k
            result.pruned["bound"] += 1
            action = f"bound {lp.value:,.1f} cannot beat {result.value:,}"
        elif lp.split is None:
            result.pruned["integral"] += 1
            result.value, result.plan = round(lp.value), sorted(lp.taken)
            action = f"integral: new incumbent {result.value:,}"
        else:
            stack.append({**fixed, lp.split: 0})
            stack.append({**fixed, lp.split: 1})                 # popped first: dive on taking it
            action = f"bound {lp.value:,.1f}, branch on {lp.split} = {lp.taken[lp.split]:.3f}"
```

Line by line against the earlier lessons:

- A node is a dict of fixings, as in lesson 3.2.1; the root fixes nothing.
- `result.value` is the incumbent, starting at $`-1`$ so that any plan, even one worth 0, beats it.
- The bound test rounds the LP value down, because GridCap's values are whole $k (lesson 3.2.2).
  The `1e-9` keeps a value such as 3,021.0000000002 from rounding below 3,021 by accident.
- The integral case takes the LP solution as the new plan. It is always better than the
  incumbent here, because the bound test ran first.
- The up child is pushed last, so it is popped first: the search dives by taking the split item.

The `log` lines are only for printing. On tiny, with P002 (must-do) paid for first, the whole
search is nine nodes:

```text
budget $4,660k after must-do P002; ratio order:
  P007  value   265  cost   290  ratio 0.914
  P004  value 2,120  cost 3,000  ratio 0.707
  P001  value 1,386  cost 2,150  ratio 0.645
  P006  value 1,247  cost 1,970  ratio 0.633
  P005  value   123  cost   250  ratio 0.492
  P008  value   137  cost   580  ratio 0.236
  P003  value   576  cost 2,470  ratio 0.233
 1 root                       bound 3,268.2, branch on P001 = 0.637
 2 P001=1                     bound 3,219.8, branch on P004 = 0.740
 3 P001=1 P004=1              infeasible
 4 P001=1 P004=0              integral: new incumbent 3,021
 5 P001=0                     bound 3,252.2, branch on P006 = 0.695
 6 P001=0 P006=1              bound 3,208.0, branch on P004 = 0.800
 7 P001=0 P006=1 P004=1       infeasible
 8 P001=0 P006=1 P004=0       bound 2,138.1 cannot beat 3,021
 9 P001=0 P006=0              bound 2,770.9 cannot beat 3,021
best 3,021: P001, P005, P006, P007
```

At the root, P007 and P004 fit (cost 3,290), leaving 1,370, and P001 takes 1,370 / 2,150 = 0.637
of itself. Node 2 takes P001 whole, which pushes P004 out to a fraction. Node 3 takes both: 2,150 +
3,000 is over 4,660, infeasible. Node 4 skips P004 and the fill is whole: P007, P001, P006 and P005
cost exactly 4,660, worth 3,021, the first incumbent. On the other side, P001 = 0, the bound
starts above 3,021 (3,252.2) and falls below it after two more splits, so nodes 8 and 9 are pruned
by bound.

With must-do P002's 871 added, the plan is worth 3,892, more than the full model's 3,627 from
lesson 3.2.1. That is the relaxation at work: this plan funds both P006 and P007, which are
alternatives, and the knapsack has no row to stop it.

## Check the Search Against Brute Force and Against HiGHS

A search that prunes wrongly still returns a plan, just not the best one, so nothing crashes to
warn you. Two independent checks catch it. Brute force tries all $`2^n`$ plans and is exact for
small $`n`$:

```python
def brute_force(items: list[Item], budget: int) -> int:
    """The best value by trying all 2^n plans: the check for small n."""
    best = 0
    for mask in range(1 << len(items)):
        chosen = [it for k, it in enumerate(items) if mask >> k & 1]
        if sum(it.cost for it in chosen) <= budget:
            best = max(best, sum(it.value for it in chosen))
    return best
```

Each `mask` from 0 to $`2^n - 1`$ is a plan: bit $`k`$ says whether item $`k`$ is taken. For larger
$`n`$, HiGHS solves the same knapsack as a MILP. On the three GridCap sizes:

```text
tiny     7 projects  ours   3,021 in   9 nodes   brute force 3,021
       root bound 3,268.17; pruned: {'infeasible': 2, 'bound': 2, 'integral': 1}
small   36 projects  ours  23,103 in 735 nodes   HiGHS 23,103
       root bound 23,168.87; pruned: {'infeasible': 43, 'bound': 314, 'integral': 11}
medium 361 projects  ours 203,107 in 743 nodes   HiGHS 203,107
       root bound 203,114.25; pruned: {'infeasible': 0, 'bound': 370, 'integral': 2}
```

The medium portfolio's 361 discretionary projects have $`2^{361}`$ plans, a number with 109 digits,
and the search proves the best one in 743 nodes. The bound is very tight on medium: with many small
projects, the split item is a small part of the budget, so the LP value is close to the best whole
plan (the root bound is 203,114.25 against the optimum 203,107). Close bounds prune early. On
small, 11 plans were found, each better than the last, before the final one was proven.

One instance can agree by luck. The module's tests also solve 20 random 12-item knapsacks and
compare each with brute force, and this program does the same against HiGHS for 20 more GridCap
small portfolios, one per seed:

```text
20 of 20 seeds agree with HiGHS; nodes per search from 1 to 2,909
nodes by seed: 865 955 697 935 1293 2909 1265 367 973 1 949 739 385 1637 267 737 619 603 1421 55
```

Every seed agrees. The node counts range from 1 (seed 10: the root's fill is already whole, so
the root is integral) to 2,909: the same algorithm and the same size, with work that varies by a
factor of thousands from one instance to the next. That spread is normal for branch-and-bound, and
it is why lesson 5.4.2 benchmarks solvers on many instances rather than one.

A third check comes with OR-Tools itself. Its knapsack page solves a 50-item knapsack (capacity 850)
with `KnapsackSolver`, a dedicated knapsack solver that is not a MILP solver, set to branch-and-bound
mode. The program below is adapted from that page's sample, `knapsack.py`:

```python
def ortools_solve(values: list[int], weights: list[int], capacity: int) -> tuple[int, list[int]]:
    """OR-Tools' own knapsack solver, in its branch-and-bound mode: the best value and the items packed."""
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "knapsack")
    solver.init(values, [weights], [capacity])
    value = solver.solve()
    return value, [i for i in range(len(values)) if solver.best_solution_contains(i)]
```

`init` takes a list of weight rows and a list of capacities, one per row ("multidimension"), so a
knapsack with one budget passes one of each. Values and weights must be whole numbers; the page says
to scale fractional data by a large enough integer first.

```text
OR-Tools example, 50 items, capacity 850
  KnapsackSolver: value 7,534, weight 850, 32 items packed
  our search:     value 733 from the 4 items of weight 0 + 6,801 = 7,534, in 175 nodes
GridCap small, 36 projects, budget left 30,760
  KnapsackSolver: value 23,103, 18 projects funded
```

Both searches find 7,534 on OR-Tools' data, and `KnapsackSolver` finds 23,103 on GridCap small, the
value of the table above. One detail needed care. Four of OR-Tools' items weigh 0, and `by_ratio`
divides by the cost, so this lesson's search cannot sort them. An item that costs nothing and is
worth something belongs in every best plan, so the program takes those four first, as the GridCap
loader takes must-do projects, and searches the other 46.

<!-- practice 2 -->

## Summary

- **A one-row LP is solved by sorting: Dantzig's bound.** Fill the budget in ratio order and take
  a fraction of the first item that does not fit; the exchange argument proves it optimal.
- **Fixing an item changes the budget, not the order.** Items fixed at 1 are paid first, items
  fixed at 0 are skipped, and the one sort at the start serves every node.
- **The search is a stack of fixings**, branching on the one split item, with the three prunes of
  lesson 3.2.2 and the bound rounded down for whole-dollar values.
- **Check the search against brute force and against HiGHS**, on many instances: a wrong prune
  returns a worse plan without any error.

## Reference

| Piece | What it does |
| --- | --- |
| `by_ratio(items)` | sort by $`v_i / c_i`$, best first, ties by name |
| `dantzig_bound(order, budget, fixed)` | the node's LP: value, LP solution, split item; `None` if infeasible |
| `solve(items, budget)` | depth-first search; returns value, plan, nodes and prune counts |
| `brute_force(items, budget)` | best value over all $`2^n`$ plans |
| `gridcap_knapsack(portfolio)` | discretionary items, budget left after must-dos, must-do ids |

| Instance | Items | Nodes | Optimum (without must-dos) |
| --- | --- | --- | --- |
| tiny | 7 | 9 | 3,021 |
| small | 36 | 735 | 23,103 |
| medium | 361 | 743 | 203,107 |
| OR-Tools' knapsack example | 46 (+ 4 of weight 0) | 175 | 7,534 |

**Further reading:** [The Knapsack Problem (OR-Tools)](https://developers.google.com/optimization/pack/knapsack) (the 50-item example, `KnapsackSolver` in branch-and-bound mode, and why its data must be integers); [OR-Tools sample knapsack.py](https://github.com/google/or-tools/blob/stable/ortools/algorithms/samples/knapsack.py) (the program this lesson adapts); [OR-Tools sample simple_knapsack_program.py](https://github.com/google/or-tools/blob/stable/ortools/algorithms/samples/simple_knapsack_program.py) (the same solver in its dynamic-programming mode, the table method of lesson 3.1.3); [Solving a Multiple Knapsacks Problem (OR-Tools)](https://developers.google.com/optimization/pack/multiple_knapsack) (several bins at once, solved with a MIP solver and with CP-SAT, where one sorted fill no longer gives the LP bound); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: capital budgeting and the knapsack as go/no-go programs; section 9.7: a branch-and-bound for 0-1 programs that solves no LP at all).

## Challenges

1. Make the search dive by skipping the split item first (swap the two `append` lines). Predict the
   node count on small, then run `knapsack_run.py`.
2. Add a primal heuristic: at every node, also fill greedily *past* the split item (skip it and keep
   taking items that still fit). That is a real plan; use it as an incumbent if it is better.
   Predict which size gains most.
3. Extend the knapsack with one alternative group (at most one of two items). Where does
   `dantzig_bound` stop being the LP, and what would you need instead?

## Design Note: What a MILP Solver Adds to These 116 Lines

This search and HiGHS run the same algorithm at heart: an LP bound, branching on a fractional
variable, pruning by infeasibility, integrality and bound. A production MILP solver adds four
layers on top, each the subject of a later lesson. **Presolve** shrinks the model before the search
(lesson 3.3.2). **Cutting planes** add rows that cut off fractional LP points without losing a
whole plan, so bounds fall faster (lesson 3.3.1). **Primal heuristics** find good plans early, as
challenge 2 starts to do (lesson 3.3.3). And **gap limits** stop the search when the plan is
provably close enough (lesson 3.4.2). Building the bare search first is what makes those layers
readable: each one makes a part of this loop prune sooner.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**dantzig.py.** Fills the small knapsack in ratio order and checks Dantzig's bound against GLOP at
three nodes (*A One-Row LP Is Solved by Sorting: Dantzig's Bound* and *Fixing an Item Changes the
Budget, Not the Order*). *Try:* Fix P034, the best-ratio project, at 0. Predict which project
becomes the split item.

- Program: [dantzig.py](src/dantzig.py)

**knapsack_trace.py.** The tiny search, one line per node (*The Search Is a Stack of Fixings*).
*Try:* Lower the budget by 250 in a copy. Predict whether node 4 is still integral.

- Program: [knapsack_trace.py](src/knapsack_trace.py)

**knapsack_run.py.** Our search on tiny, small and medium, checked against brute force and HiGHS
(*Check the Search Against Brute Force and Against HiGHS*). *Try:* Remove the rounding in the
bound test. Predict the node counts.

- Program: [knapsack_run.py](src/knapsack_run.py)

**seeds.py.** Twenty more small portfolios, our search against HiGHS on each (*Check the Search
Against Brute Force and Against HiGHS*). *Try:* Use the medium size. Predict the largest node count.

- Program: [seeds.py](src/seeds.py)

**ortools_knapsack.py.** Adapted from the OR-Tools example `knapsack.py`: OR-Tools' 50-item knapsack
solved by `KnapsackSolver` and by this lesson's search, then GridCap small by `KnapsackSolver`
(*Check the Search Against Brute Force and Against HiGHS*). *Try:* Switch the solver type to
`KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER`, the mode of the sample `simple_knapsack_program.py`. Predict
the value on GridCap small.

- Program: [ortools_knapsack.py](src/ortools_knapsack.py)

**knapsack.py.** The whole knapsack branch-and-bound: `Item`, `by_ratio`, `dantzig_bound`, `solve`,
`brute_force` and `gridcap_knapsack`. It prints nothing.

- Library: [knapsack.py](src/knapsack.py)
