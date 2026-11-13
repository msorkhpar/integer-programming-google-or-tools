# 8.1.2 Supported and Unsupported Pareto Points

Lesson 8.1.1 gave the GridCap board eight plans,
one for each range of prices between NPV and risk removed. The planners come back with a question of
their own: "Keep NPV within 5% of the best, and remove as much risk as you can." The best NPV is
$24,260k, so the floor is $23,047k, and the answer is a plan with $23,104k of NPV that removes
$14,837k of risk. It is not one of the eight. The board asks the natural follow-up: which weights
give that plan, so we can state our price? None do. No weighting of NPV and risk, at any price,
returns it, although no other plan beats it on both counts. This lesson shows why, proves it for
that plan, counts how common such plans are on GridCap small (57 of its 65 Pareto-optimal plans),
and shows that the integer variables are what create them. Five rules, one per heading.

GridCap is a fictional utility generated for this course; its projects, assets and budgets describe
no real company.

## A Supported Point Is One Some Weighted Sum Returns

Lesson 8.1.1 defined dominance and Pareto optimality. Two more terms split the Pareto-optimal plans
in two:

- a Pareto-optimal plan is **supported** when it is an optimal plan of the weighted sum for some
  positive weights, and its objective values are a **supported point** of the front;
- it is **unsupported** when it is Pareto optimal but no weighting, positive or with a zero weight,
  makes it optimal.

Two edge cases decide where the line between the two falls, and this course settles both the same
way everywhere.

- **Zero weights add nothing for a Pareto-optimal plan.** Suppose a Pareto-optimal plan is optimal
  for weights (1, 0): it has the most NPV, and since nothing dominates it, the most risk removed
  among the plans with that NPV. Give risk a weight $`\varepsilon > 0`$ instead of 0. A plan with
  less NPV loses by at least the smallest NPV difference between plans, which a small enough
  $`\varepsilon`$ times a risk difference cannot make up, because there are finitely many plans;
  a plan with the same NPV removes no more risk. So the plan is also optimal for the positive weights
  $`(1, \varepsilon)`$, and it is supported. Every Pareto-optimal plan is therefore exactly one of
  the two, supported or unsupported. A plan that is optimal *only* at a zero weight ties on NPV and
  removes less risk than another: it is weakly Pareto optimal (lesson 8.1.1), not Pareto optimal,
  and neither word applies to it.
- **A point on a straight stretch counts as supported.** A Pareto point lying exactly on the segment
  between two others ties with both at that segment's price, so it is optimal for those positive
  weights and is supported, even though a solver that breaks the tie may return an end instead.

The smallest example needs three plans, of which a planner may pick exactly one. Plan A scores
(10, 1) on two objectives to maximize, B scores (1, 10) and C scores (5, 5):

```text
A (10, 1): dominated by nothing
B (1, 10): dominated by nothing
C (5, 5): dominated by nothing
```

All three are Pareto optimal: A has the most of objective 1, B the most of objective 2, and C beats
A on the second and B on the first. Now weight them, with share $`s`$ on objective 1:

```python
for k in range(11):
    s = k / 10
    scores = {name: s * a + (1 - s) * b for name, (a, b) in plans.items()}
    pick = max(scores, key=scores.get)
```

```text
share on objective 1 -> weighted scores of A, B, C -> pick
  0.0: A  1.0  B 10.0  C  5.0  -> B
  0.1: A  1.9  B  9.1  C  5.0  -> B
  0.2: A  2.8  B  8.2  C  5.0  -> B
  0.3: A  3.7  B  7.3  C  5.0  -> B
  0.4: A  4.6  B  6.4  C  5.0  -> B
  0.5: A  5.5  B  5.5  C  5.0  -> A
  0.6: A  6.4  B  4.6  C  5.0  -> A
  0.7: A  7.3  B  3.7  C  5.0  -> A
  0.8: A  8.2  B  2.8  C  5.0  -> A
  0.9: A  9.1  B  1.9  C  5.0  -> A
  1.0: A 10.0  B  1.0  C  5.0  -> A
```

(At 0.5, A and B tie at 5.5 and `max` keeps the first.) C never wins, and not because the grid is
coarse: C's score is always 5, while the better of A and B scores $`\max(1 + 9s,\ 10 - 9s)`$, which
is never below 5.5. C is the compromise many planners would choose, and it is unsupported.

## Supported Points Lie on the Upper Convex Hull of the Front

Draw the Pareto points with NPV across and risk removed up. For a share $`s`$, the plans with equal
weighted score $`sN + (1 - s)R`$ lie on a straight line, and maximizing the score pushes that line
up and to the right until only the last point it touches remains. So a weighted sum can only return
a point that some straight line touches with every other point on or below it. Those points form the
**upper convex hull** of the front: the polygon you get by stretching a string over the points from
the leftmost to the rightmost, keeping it above all of them. A point inside the string, below the
segment joining two hull points, is unsupported.

That gives a test that needs no solver once the front is known. Walk the points in order of NPV and
keep a chain; drop the last kept point whenever it lies below the line from the one before it to
the new point:

```python
def supported(points: list[tuple[int, float]]) -> list[tuple[int, float]]:
    """The points on the upper-right convex hull of a Pareto front: the ones a weighted sum can reach."""
    hull = []
    for p in sorted(points):                                  # NPV up, so risk down along the front
        while len(hull) >= 2:
            (n1, r1), (n2, r2) = hull[-2], hull[-1]
            if (n2 - n1) * (p[1] - r1) - (r2 - r1) * (p[0] - n1) > 1e-9:
                hull.pop()                                    # hull[-1] lies below the line to p
            else:
                break
        hull.append(p)
    return hull
```

The test inside the loop is the sign of a cross product: positive when the new point $`p`$ lies
above the line through the last two kept points, which means the last kept point is under the
string. A point exactly on a segment between two hull points is kept: it ties with both ends at the
segment's break-even price, so it is supported, though a solver may return either end instead.

## GridCap Small Has 65 Pareto-Optimal Plans, and Weighted Sums Reach 8

To test every Pareto-optimal plan, first find them all. The program does it with the ε-constraint
method, the subject of lesson 8.3.1 (*The epsilon-constraint method*): maximize risk
removed with NPV held at or above a floor, then raise the floor past the plan just found and solve
again. Two details make the sweep exact here, and lesson 8.3.2 explains both in depth. A second
pass maximizes NPV among the plans with that much risk removed, so a plan that only ties on risk
and earns less NPV (weakly Pareto optimal) is never recorded. And GridCap's NPV coefficients are whole $k, so a floor $1k above the last plan's NPV skips no plan; with fractional
coefficients a fixed step could jump over a point.

```python
def frontier(sm) -> list[tuple[int, float]]:
    """Every Pareto point (NPV, risk), by an epsilon sweep on NPV in $1k steps (lesson 8.3.1)."""
    points, floor = [], None
    while True:
        rows = [] if floor is None else [sm.model.add_linear_constraint(sm.npv_of() >= floor, name="npv_floor")]
        sm.model.maximize(sm.risk_of())                       # pass 1: the most risk at this NPV floor
        result = solve_highs(sm.model)
        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            for row in rows:                                  # no plan reaches this floor: done
                sm.model.delete_linear_constraint(row)
            return points
        rows.append(sm.model.add_linear_constraint(sm.risk_of() >= result.objective_value() - 1e-6))
        sm.model.maximize(sm.npv_of())                        # pass 2: the most NPV at that risk
        npv, risk = score(sm, plan_of(sm, solve_highs(sm.model)))
        points.append((npv, risk))
        floor = npv + 1                                       # NPV is whole $k: the next point has more
        for row in rows:
            sm.model.delete_linear_constraint(row)
```

The sweep takes two solves per point, plus a last one that finds no plan above the highest floor, and returns the whole front; the hull test then sorts it:

```text
65 Pareto-optimal plans, 8 supported, 57 unsupported
supported: (18,886, 16,086), (22,675, 15,601), (22,870, 15,554), (23,573, 14,496), (23,591, 14,466), (24,019, 12,751), (24,098, 12,348), (24,260, 10,577)
deepest unsupported plans, $k of risk below the hull: (24,156, 11,073) 640, (24,163, 11,009) 628, (24,162, 11,049) 599
```

The eight supported points are exactly the eight plans lesson 8.1.1's sweep of 101 weightings
found, which is what the rule predicts: every weighting returns a hull point, and every hull point
here holds over some range of prices. The other 57 Pareto-optimal plans, seven in eight, can never
come out of a weighted sum. The deepest, with $24,156k of NPV, removes $640k less risk than the
straight line between its supported neighbours would, yet nothing beats it on both counts.

Finding the supported points does not need the whole front. A weighted sum returns hull points
directly, and choosing each new weighting from the two hull points already known finds every corner
of the hull with a few solves. (A point exactly on a segment ties with the corners at its ends at the
only share where it is optimal, and a solver may return a corner there instead, so a search by
weights is only sure to find the corners.) The next practice builds that search, because a fixed grid can miss a hull
point whose price range is narrow: in lesson 8.1.1, the plan with $23,573k of NPV holds only for
shares 0.61 to 0.62.

<!-- practice 1 -->

## No Weight Reaches a Point Below the Segment Between Its Supported Neighbours

Back to the planners' plan $`q`$. The program asks the same question they did, with an NPV floor at
95% of the best, and checks the answer against the front and the hull:

```text
most risk with NPV >= $23,047k: NPV $23,104k, risk $14,837k; Pareto point: True, supported: False
neighbours a = (22,870, 15,554) and b = (23,573, 14,496)
```

Its supported neighbours are $`a`$, the 50/50 plan of lesson 8.1.1, and $`b`$. Here is the proof
that no share $`s \in [0, 1]`$ makes $`q`$ the weighted optimum. For $`q`$ to win, it must at least
tie with $`a`$ and with $`b`$:

```math
\begin{aligned}
s\,N_q + (1 - s)\,R_q \ge s\,N_a + (1 - s)\,R_a \;&\iff\; s \ge \frac{R_a - R_q}{(N_q - N_a) + (R_a - R_q)} && \text{(beat } a) \\
s\,N_q + (1 - s)\,R_q \ge s\,N_b + (1 - s)\,R_b \;&\iff\; s \le \frac{R_q - R_b}{(N_b - N_q) + (R_q - R_b)} && \text{(beat } b)
\end{aligned}
```

Both equivalences divide by a positive number, because $`N_a < N_q < N_b`$ and
$`R_a > R_q > R_b`$. With the numbers:

```python
low = (a[1] - q[1]) / ((q[0] - a[0]) + (a[1] - q[1]))       # q beats a only if share >= low
high = (q[1] - b[1]) / ((b[0] - q[0]) + (q[1] - b[1]))      # q beats b only if share <= high
```

```text
beat a: share >= 0.7539; beat b: share <= 0.4209; both: impossible, 0.7539 > 0.4209
the segment a-b at NPV $23,104k removes $15,202k; q removes $14,837k
```

Any share that beats $`a`$ loses to $`b`$, and the other way round. Since $`q`$ must beat both to be
returned, no weighting returns it. The argument only needed two feasible plans, so it holds whatever
other plans exist. The last line says the same thing geometrically: at $`q`$'s NPV, the segment from
$`a`$ to $`b`$ sits at $15,202k of risk removed, $365k above $`q`$. Every point strictly below such a
segment, with an NPV strictly between the two ends, fails the two inequalities in the same way.

So the board's question has an exact answer: there is no price at which this plan is the best one.
The plan is still a good one, and nothing dominates it. The board can either accept it as the answer
to the question it actually asked (an NPV floor, which lessons 8.3.1 to 8.3.3 turn into a full method), or pick
$`a`$ or $`b`$ and state the price range that supports it, as lesson 8.1.1 did.

<!-- practice 2 -->

## Integer Variables Create Unsupported Points; an LP Has None

Go back to A, B and C. If the planner could take half of A and half of B, that mix would score
(5.5, 5.5):

```text
half of A plus half of B: (5.5, 5.5), which dominates C: True
```

C is unsupported because the mixes that would beat it are not allowed: a project is funded or not.
In a linear program, where every variable is continuous, the mixes are allowed. Any average of two
feasible LP solutions is feasible (the constraints are linear), and its objective values are the
same average of theirs. So the set of reachable $`(N, R)`$ values is convex, no point can sit below
the segment between two others, and every Pareto-optimal point of a multi-objective LP is
supported. That is a theorem (Isermann, 1974, as quoted by Könen and Stiglmayr): for linear
programs, the weighted sum finds every efficient solution.

GridCap shows it on the LP relaxation of the same model, each $`x_{i,t}`$ in $`[0, 1]`$ instead of
$`\{0, 1\}`$ (`build(small, integer=False)`). Ask the planners' question at $`q`$'s NPV, read the
dual value of the NPV floor (the risk the last $1k of floor costs: its shadow price, lesson 2.3.3), and use it as the price of a weighted sum:

```python
mu = -result.dual_values(row)                        # $k of risk the last $1k of NPV floor costs
```

```python
lp.model.maximize(mu * lp.npv_of() + lp.risk_of())  # the weighted sum with price mu on NPV
```

```text
LP, most risk with NPV >= $23,104k: NPV $23,104k, risk $16,176k, 7 fractional starts, dual of the NPV floor 0.0522
LP weighted sum, weights (0.0522, 1): optimum 17,381.2; the epsilon answer scores 17,381.2
```

The LP's answer scores exactly the weighted optimum at price 0.0522, so that weighted sum supports
it (the solver may return another plan with the same score; the price makes them tie). The LP gets
there with 7 fractional starts, fractions of projects that cannot be built, and it removes $16,176k
of risk at that NPV, more than any integer plan removes at any NPV. That is the gap the integer
restriction opens, and the unsupported points live in it.

One claim to correct while here: integer fronts are sometimes described as "non-convex". The front
of an integer program is a finite set of points, and the precise statement is that some of them can
lie strictly inside the convex hull of the others. How many is an empirical matter: the paper above
reports that in combinatorial problems unsupported points typically outnumber supported ones, and
on GridCap small they are 57 of 65.

## Choose the Method by the Question

The two lessons together give a working rule for multi-objective planning:

- **To show the trade-off as prices**, use weighted sums and report each supported plan with its
  break-even prices (lesson 8.1.1). Every plan is Pareto optimal and comes with an argument a board
  can read: "best for any price between 0.239 and 1.505".
- **To answer a question with a floor or a cap** ("keep NPV within 5%", "remove at least $15M of
  risk"), use a constraint on one objective and optimize the other: the ε-constraint method of
  lessons 8.3.1 to 8.3.3. It reaches unsupported plans, which are most of the front here.
- **To put one objective strictly first**, solve in priority order (lessons 8.2.1 and 8.2.2, *Lexicographic
  objectives*, and lesson 4.3.2).

A weighted sum is not wrong for integer programs; it answers a narrower question than it seems to.
It finds the plans that are best at some price, and the planners' "within 5%" plan is best at none.

## Summary

- **A supported point is one some weighted sum returns.** An unsupported point is Pareto optimal and
  returned by no weighting; with three plans (10, 1), (1, 10) and (5, 5), the compromise (5, 5) is
  never picked.
- **Supported points lie on the upper convex hull of the front.** A point below the segment between
  two hull points is unsupported.
- **GridCap small has 65 Pareto-optimal plans, and weighted sums reach 8.** They are the eight plans
  of lesson 8.1.1's sweep.
- **No weight reaches a point below the segment between its supported neighbours.** Beating $`a`$
  needs $`s \ge 0.7539`$ and beating $`b`$ needs $`s \le 0.4209`$ for the planners' plan.
- **Integer variables create unsupported points; an LP has none.** The LP relaxation's answer at the
  same NPV is reached by the weighted sum with its dual price, 0.0522.

## Reference

| Term | Meaning |
| --- | --- |
| supported plan (point) | Pareto optimal, and optimal for the weighted sum at some positive weights; includes a point exactly on a segment between two hull corners, and a plan optimal at a zero weight (it is also optimal at a small positive one) |
| unsupported plan (point) | Pareto optimal, and optimal for no weighted sum, even with a zero weight; it lies strictly below a hull segment |
| optimal only at a zero weight | weakly Pareto optimal, not Pareto optimal; neither supported nor unsupported |
| upper convex hull | the points a string stretched above the front touches, corners and points on its segments; the supported points |
| hull test | drop the last kept point while it lies below the line from the one before it to the next point |
| proof for $`q`$ between hull neighbours $`a`$, $`b`$ | beat $`a`$: $`s \ge (R_a - R_q)/((N_q - N_a) + (R_a - R_q))`$; beat $`b`$: $`s \le (R_q - R_b)/((N_b - N_q) + (R_q - R_b))`$; empty |
| multi-objective LP | every efficient solution is supported (Isermann's theorem) |

| Code | What it does |
| --- | --- |
| `frontier(sm)` | every Pareto point of the model, by an ε sweep with a second pass (`gridcap_frontier.py`) |
| `supported(points)` | the hull points of a front |
| `build(small, integer=False)` | the LP relaxation of the module's model |
| `result.dual_values(row)` | a row's dual value in an LP solve (MathOpt) |

**Further reading:** [OR-Tools, MathOpt basic example](https://developers.google.com/optimization/math_opt/basic_example)
(building, solving and reading a MathOpt model, the calls the sweep repeats); [OR-Tools, MathOpt](https://developers.google.com/optimization/math_opt)
(the solvers MathOpt reaches, HiGHS among them); [Könen and Stiglmayr, On Supportedness in
Multi-Objective Combinatorial Optimization (arXiv 2501.13842)](https://arxiv.org/html/2501.13842v2)
(section 1: supported, weakly supported and unsupported points, Isermann's theorem for linear
programs, and the observation that unsupported points typically outnumber supported ones);
[Przybylski, Klamroth and Lacour, A simple and efficient dichotomic search algorithm for
multi-objective mixed integer linear programs (arXiv 1911.08937)](https://arxiv.org/abs/1911.08937)
(finding all supported extreme points by weighted sums, the idea behind the first practice);
[Wikipedia, Multi-objective optimization](https://en.wikipedia.org/wiki/Multi-objective_optimization)
(the scalarizing section: a linear scalarization finds only the supported solutions).

## Challenges

1. Add a fourth plan D = (7, 6) to A, B and C. Which plans are Pareto optimal now, and which are
   supported?
2. The deepest unsupported plan has $24,156k of NPV. Name its two supported neighbours from the
   output and compute the two bounds on $`s`$ for it.
3. A planner proposes to reach unsupported plans with a weighted sum on squared objectives,
   $`s N^2 + (1 - s) R^2`$. What would that do to the model?

## Design Note: Keep the Front, Not Only the Plan

The sweep in this lesson cost 131 solves (two per point and a last, infeasible one), and it bought something a single solve cannot: a list of
every plan nothing beats, against which any later question can be checked without solving again.
Is the planners' plan Pareto optimal? Look it up. Is it supported? Look it up. What is the most risk
any plan removes above $24,000k of NPV? Read it off. When a front is affordable to compute, store it
with the run, with each point's plan, and answer the board's follow-up questions from it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**three_plans.py.** Three plans, pick one: checks dominance, weights them at eleven shares and
mixes A and B (*A Supported Point Is One Some Weighted Sum Returns*, *Integer Variables Create
Unsupported Points*). *Try:* Change C to (6, 6). Predict whether a weighting picks it now.

- Program: [three_plans.py](src/three_plans.py)

**gridcap_frontier.py.** Finds GridCap small's whole Pareto front by an ε sweep, sorts it into
supported and unsupported points, and proves that no weighting reaches the planners' plan (*Supported
Points Lie on the Upper Convex Hull*, *GridCap Small Has 65 Pareto-Optimal Plans*, *No Weight
Reaches a Point Below the Segment*). *Try:* Set the floor to 90% of the best NPV. Predict whether
the answer is supported.

- Program: [gridcap_frontier.py](src/gridcap_frontier.py)

**lp_relaxation.py.** Solves the planners' question on the LP relaxation and reaches the answer
with a weighted sum priced by the floor's dual value (*Integer Variables Create Unsupported Points;
an LP Has None*). *Try:* Raise the floor to $24,000k. Predict whether the dual value rises or falls.

- Program: [lp_relaxation.py](src/lp_relaxation.py)
