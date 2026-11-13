# 9.2.3 Parametric Analysis: the Budget-Value Frontier

GridCap's board will set next year's capital budget somewhere between $38,000k and $39,000k, and
finance wants to know what each budget in that band buys. Lessons 9.2.1 and 9.2.2 showed that no
price answers that for the selection MILP. What does answer it is the curve itself: $`V(B)`$, the
best NPV at every budget $`B`$. Finding how a model's optimum changes as one of its numbers
moves is called **parametric analysis**, and for a MILP it is done by solving again. This lesson
builds the budget-value curve of GridCap's small portfolio by repeated solves, first on a grid,
then exactly, step by step. GridCap is fictional.

## The Model

Two models, both on the small portfolio's selection rules of lesson 9.2.1.

**Sets.** $`P`$ the projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$ the child
projects, each with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups.

**Parameters.** $`v_i`$, project $`i`$'s NPV ($k, a whole number); $`c_i`$, its cost ($k); and,
for the first model, the budget $`B`$; for the second, a value level $`\ell`$ ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: project $`i`$ is funded.

**The rules**, shared by both models:

```math
\begin{aligned}
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

**The value at a budget**, the curve's height at $`B`$ (lesson 9.2.1's model):

```math
V(B) \;=\; \max \sum_{i \in P} v_i\, x_i \qquad \text{s.t.} \quad \sum_{i \in P} c_i\, x_i \le B \quad \text{(budget)}, \quad \text{the rules}
```

**The cheapest plan worth at least $`\ell`$** (new in this lesson; it finds where the curve steps):

```math
K(\ell) \;=\; \min \sum_{i \in P} c_i\, x_i \qquad \text{s.t.} \quad \sum_{i \in P} v_i\, x_i \ge \ell \quad \text{(reach)}, \quad \text{the rules}
```

If no plan is worth $`\ell`$, the second model is infeasible. In the code, $`V`$ is
`best_value(portfolio, budget)` in `selection.py` and $`K`$ is
`cheapest_reaching(portfolio, level)` in `step_points.py`.

## Repeated Solves on a Grid Give Points of the Curve, Not Its Steps

The plain way to draw the curve is to solve the MILP at evenly spaced budgets. `budget_curve.py`
does it every $250k and every $50k across the board's band:

```python
for step in (250, 50):
    grid = [(b, best_value(small, b)) for b in range(LO, HI + 1, step)]
    levels = sorted({v for _, v in grid})
```

```text
grid every 250:  5 solves,  5 distinct values
    [(38000, 25174), (38250, 25290), (38500, 25429), (38750, 25569), (39000, 25732)]
grid every  50: 21 solves, 20 distinct values
```

Every point is a true value of $`V`$: at $38,250k the best plan is worth $25,290k. But the grid
shows nothing between its points. Between $38,000k and $38,250k the value rose by $116k; the grid
cannot say whether that came as one jump or ten, or at which budgets. A finer grid sees more
levels (20 instead of 5) for four times the solves, and still cannot say where a step is, only
which pair of grid points brackets it.

The curve has a shape that makes an exact answer possible. $`V`$ never falls as $`B`$ grows (a
bigger budget allows every plan a smaller one did), and it changes only at a budget equal to the
cost of some plan. So it is a **step function**: flat stretches, then a jump. Between two steps
nothing changes, and one solve anywhere in the stretch gives the whole stretch.

<!-- practice 1 -->

## The Next Step Is the Cheapest Plan Worth More: Two Solves per Step

Suppose the curve stands at level $`v = V(B)`$. Where is the next step? It is the smallest budget at
which some plan is worth more than $`v`$. NPVs are whole $k, so "worth more than $`v`$" means worth
at least $`v + 1`$, and the smallest budget that buys such a plan is exactly $`K(v + 1)`$, the
cheapest plan worth at least $`v + 1`$. At that budget the curve's new height is $`V(K(v+1))`$,
which can be more than $`v + 1`$: the plan that reaches the level most cheaply need not be the
best plan at its price. So each step takes two solves: $`K`$ to find where, then $`V`$ to find how
high.

```python
def cheapest_reaching(portfolio: Portfolio, level: int) -> int | None:
    """min cost  s.t.  value >= level and every selection rule: where V(B) first reaches `level`."""
    sel = build(portfolio, 0)
    sel.model.delete_linear_constraint(sel.budget)
    sel.model.add_linear_constraint(sel.value >= level, name="reach")
    sel.model.minimize(sel.cost)
    result = solve_highs(sel.model)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None                                   # no plan is worth that much
    return round(result.objective_value())
```

```python
def step_points(portfolio: Portfolio, lo: int, hi: int) -> list[tuple[int, int]]:
    """Every (B, V(B)) in [lo, hi] where V steps up, starting with (lo, V(lo))."""
    points = [(lo, best_value(portfolio, lo))]
    while True:
        budget = cheapest_reaching(portfolio, points[-1][1] + 1)
        if budget is None or budget > hi:
            return points
        points.append((budget, best_value(portfolio, budget)))   # V(budget) can pass level + 1
```

`cheapest_reaching` reuses the selection model: it deletes the budget row (MathOpt's
`delete_linear_constraint`), adds the reach row, and turns the objective around with `minimize`.
Both solves run HiGHS at a zero relative gap: a step point found at a nonzero gap would only be
"within the gap" of a step, and could be wrong.

```text
exact: 26 steps in [38,000, 39,000]
      B    V(B)  rise     LP(B)
 38,000  25,174     0  25,222.5
 38,090  25,178     4  25,275.3
 38,110  25,228    50  25,287.0
 38,170  25,253    25  25,322.2
 38,240  25,290    37  25,363.3
 38,260  25,298     8  25,375.0
 38,320  25,317    19  25,410.2
 38,390  25,336    19  25,451.3
 38,410  25,344     8  25,463.0
 38,420  25,350     6  25,468.9
 38,440  25,360    10  25,480.6
 38,470  25,429    69  25,498.2
   ...
 39,000  25,732
all 26 steps: rise 3 to 69, flat stretch 10 to 90
```

The band holds 26 steps, which took 54 solves to find: one $`V`$ at the start, then a $`K`$ and a
$`V`$ per step, and a last $`K`$ that lands past the band. The 21-point grid saw 20 of the band's
27 levels. The table shows the first 12 steps; over all 26, the rise at a step runs from $3k to
$69k, and the flat stretch between two steps from $10k to $90k. The $116k that the coarse grid saw
between $38,000k and $38,250k came in four steps: +4 at 38,090, +50 at 38,110, +25 at 38,170
and +37 at 38,240.

The step points are exact, not just close. One more line of the program checks a step against the
budget just below it:

```text
V(38,259) = 25,290, V(38,260) = 25,298: the step is at 38,260 exactly
```

The column LP(B) is the LP relaxation's value at the same budgets. It rises smoothly and stays
above $`V`$: the relaxation's curve is concave (lesson 9.2.1), and the MILP's steps sit under it.

<!-- practice 2 -->

## The Whole Curve Has 1,090 Steps on the Small Portfolio

The same function runs over the whole range, from the must-do projects' cost, the least budget any
plan fits, to the cost of all 40 projects:

```python
must_cost = sum(p.capex for p in small.projects if p.must_do)
points = step_points(small, must_cost, sum(p.capex for p in small.projects))
```

```text
must-do cost 7,630: V = 2,684; the curve steps 1,090 times and stops at B = 68,330, V = 36,852
first steps: [(7630, 2684), (7780, 2796), (7900, 2879), (7970, 2924), (8020, 2948)]
largest rise 302 at B = 9,760; longest flat stretch 590 from B = 65,470
median distance between steps: 40
```

Forty projects make many plans, and many of them are the best plan at some budget: 1,090 steps,
half of them at most $40k after the one before. The curve ends at $68,330k, where $`K`$ finds no plan
worth more than $36,852k. All 40 projects cost $69,810k together, but the rules forbid funding both
members of an alternative group, so no plan uses that much.

Seen from far away, 1,090 small steps look like a smooth curve, and lesson 9.2.4 uses that: over a
large change the LP relaxation's price is about right. Seen from close up, around any one budget,
the curve is flat and then jumps, and that is what "the next dollar" meets.

## Each Step Point Is an Efficient Plan of Cost Against Value

Each step point $`(B, V(B))`$ is a plan that no other plan beats on both cost and value. The
argument takes two lines:

- No plan costing at most $`B`$ is worth more than $`V(B)`$: that is what $`V(B)`$ means.
- No plan costing less than $`B`$ is worth as much as $`V(B)`$: if one did, $`V`$ would already
  have reached that level at its lower cost, and $`B`$ would not be a step. So a report that pairs
  a step with a cheaper best plan has the step's budget wrong; nothing in it fixes the plan's value.
  In plainer words: if a report lists a step at budget $`B`$ whose best plan costs less than
  $`B`$, the value is right and the budget is not. The step really begins at that plan's own cost,
  and the report should move the step there.

So the best plan at a step costs exactly $`B`$, and the step points are the **efficient**
(Pareto-optimal) plans for the two objectives "spend less" and "deliver more" (lesson 8.1.2). The
algorithm is the ε-constraint method of lesson 8.3.1 with cost as the objective and value as the
held objective, its level $`\ell`$ raised to just above the last point each time. Because NPVs are
whole $k, raising $`\ell`$ by 1 cannot skip an efficient plan, and the second solve, $`V`$ at the
new budget, picks the best plan at that cost, so no point is only weakly efficient (lesson 8.3.2).
A budget-value curve is a two-objective frontier, and the board's question, "how much budget?",
is a choice of a point on it.

## Summary

- **Repeated solves on a grid give points of the curve, not its steps.** Each grid point is
  exact, but a grid can only bracket where a step is.
- **The next step is the cheapest plan worth more: two solves per step.** $`K(v + 1)`$ gives where,
  $`V(K(v+1))`$ gives how high; whole-$k NPVs make $`v + 1`$ exact.
- **The whole curve has 1,090 steps on the small portfolio.** Far away it looks smooth; close up it
  is flat, then jumps.
- **Each step point is an efficient plan of cost against value.** The step algorithm is the
  ε-constraint method with cost minimized and value held at a level.

## Reference

| Want | Do |
| --- | --- |
| $`V`$ at a few budgets | one MILP per budget, zero gap |
| where the next step is after level $`v`$ | $`K(v+1)`$: min cost s.t. value $`\ge v+1`$ (integer values) |
| how high the curve goes there | $`V(K(v+1))`$, which can exceed $`v+1`$ |
| the curve in a band $`[lo, hi]`$ | start at $`(lo, V(lo))`$, repeat until $`K > hi`$ or infeasible |
| cost of the exact curve | $`2 \times`$ steps $`+ 2`$ solves |
| values not whole numbers | scale them to whole units, or raise $`\ell`$ by a stated tolerance and say so |

**Further reading:** [MathOpt `model.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`delete_linear_constraint`, `minimize` and `maximize`: the calls that turn the selection model into the cheapest-plan model); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (incremental solving among MathOpt's features; this lesson builds a fresh model per solve instead, for clarity); [Güzelsoy and Ralphs, Duality for Mixed Integer Linear Programs](https://coral.ise.lehigh.edu/%7Eted/files/papers/MILPD06.pdf) (section 2: the value function as the optimum for every right side; section 4.1: it is the most useful dual function for studying changes of the right side, but there is unlikely to be an efficient general method to construct it, which is why this lesson finds it one step at a time for one right side).

## Challenges

1. Values in a scenario come in $0.1k units. What changes in `step_points`, and why does "+1"
   become wrong?
2. The board narrows the band to $38,300k to $38,500k. How many solves does the exact curve need
   there? Count the steps from the table.
3. The longest flat stretch, $590k from $65,470k, is near the end of the curve. Explain why flat
   stretches grow as the budget nears $68,330k.

## Design Note: Solve for the Breakpoints, Not on a Schedule

A grid spends its solves where nothing happens and still misses where things do. The step method
spends exactly two solves per change in the answer, and its output, a list of breakpoints, is the
curve itself, with nothing to interpolate. When a model's value changes only at discrete points,
solve for the points.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**budget_curve.py.** Sweeps the band on two grids, then finds its exact step points and the LP
relaxation's value at each (*the first two sections*). *Try:* Move the band to $20,000k to
$21,000k. Predict whether it has more steps or fewer than this one.

**step_points.py.** The cheapest-plan model and the step algorithm, run over the small portfolio's
whole range (*The Next Step Is the Cheapest Plan Worth More* and *The Whole Curve*). *Try:* Make
P031 a must-do project. Predict where the curve now starts.

- Program: [budget_curve.py](src/budget_curve.py)
- Program: [step_points.py](src/step_points.py)
- Library: [selection.py](src/selection.py)
