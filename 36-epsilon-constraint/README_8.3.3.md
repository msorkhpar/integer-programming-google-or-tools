# 8.3.3 Generating a Frontier and Presenting It to Planners

Lesson 8.3.2 left GridCap with 65 Pareto-optimal plans between the NPV plan and the risk plan. The
planning director has twenty minutes in the Pre-Opt review (lesson 7.1.3) and
asks for one page: "How much NPV does each extra step of risk reduction cost us, and where does it
stop being worth it?" Sixty-five rows of numbers do not answer that, and neither does a chart nobody
can quote in the minutes. This lesson turns a generated frontier into a page a planner can act on,
in five rules: generate it with a check that every point is non-dominated, show a short table, state
each step as a price, mark the knees, and say it in one sentence.

GridCap is a fictional utility generated for this course; its assets, projects and budgets describe
no real company.

## Generate the Frontier Once, and Check That No Point Dominates Another

The generator is `exact_frontier` from lesson 8.3.2, on the model of lesson 8.3.1 with the roles
that make it exact: risk removed is maximized, and NPV, whose values are whole $k, is the floor,
stepped by 1. Lesson 8.3.2 lists the conditions for exactness in full; the one that depends on the
data, a reward smaller than the closest gap in risk between neighbouring plans, was checked there
for this frontier.

**The model solved at each floor $`v`$** (lesson 8.3.2's AUGMECON problem with the roles swapped):

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of
project $`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ (whole $k) and $`\text{rr}_{i,t}`$ ($k) as in lesson 8.3.1;
$`c_{i,k}`$ and $`B_y`$, cost profile and yearly budget ($k); $`v`$, the NPV floor ($k);
$`r_2`$, the NPV range of the payoff table ($k); $`\rho = 10^{-3}`$, the weight of the slack
reward (lesson 8.3.2).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$; slack $`s \ge 0`$ ($k of
NPV above the floor).

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{rr}_{i,t}\, x_{i,t} \; + \; \frac{\rho}{r_2}\, s
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} - s &= v && && \text{(eps\_floor)} \\
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s' \in T_{p(c)},\, s' \le t - L_c} x_{p(c),s'} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

Generate once, and keep the result: every table, price and knee below is read from the same list
of points, with no further solve.

```python
points, _ = exact_frontier(two.model, two.risk, two.npv)       # first = risk removed, second = NPV
hull = supported(points)
```

A frontier that goes to a planner must be checked before it is read. The defining property is that
no point dominates another, and it is cheap to test: compare every pair.

```python
def dominated(points: list[Point]) -> list[tuple[Point, Point]]:
    """Every pair (q, p) of the list in which p dominates q. Empty for a true frontier."""
    return [(q, p) for q in points for p in points if dominates(p, q)]
```

Lesson 8.3.2's run printed `pairs where one plan dominates another: 0` for these 65 plans, and the
module's tests assert it. The check has to forgive solver noise: `dominates` counts two values as
equal when they are within `SAME` ($`10^{-3}`$, one dollar), because the same plan solved twice can
come back with an NPV of 17,064 and 17,064.00001. Without that, a plan would "dominate" itself.

The library takes any MathOpt model and any two objectives, both maximized; nothing in it names
GridCap. Lesson 9.2.3 (*Sensitivity for MIP*) builds a budget-value frontier, and passes value as the
first objective and minus the budget as the second.

<!-- practice 1 -->

## Show a Short Table, Each Row a Plan the Planner Could Pick

Sixty-five rows are too many for a review, and picking every fifth row hides the rows that matter.
Choose rows by what a planner would ask about: the two ends, the best plan at round risk targets
(every $1,000k), and the knees (defined below). Each row is a real plan, so each can be opened
project by project. The target lookup needs no solve: among the points that reach the target, take
the one with the most NPV.

```python
def best_reaching(points: list[Point], target: float) -> Point | None:
    """The frontier point with the most `second` among those with `first` >= target."""
    reaching = [p for p in points if p.first >= target - TOL]
    return max(reaching, key=lambda p: p.second) if reaching else None
```

```text
65 Pareto-optimal plans; the table shows the ends, the best NPV at each $1,000k of risk, the knees
why shown              | risk removed | NPV    | NPV given up | projects | vs max NPV plan | weighted sum finds it
max NPV plan           |       10,577 | 24,260 |            0 |       27 |        +0 -0 ~0 | yes
best at 11,000         |       11,006 | 24,180 |           80 |       25 |        +1 -3 ~3 | no
best at 12,000, knee   |       12,348 | 24,098 |          162 |       27 |        +2 -2 ~2 | yes
best at 13,000         |       13,221 | 23,815 |          445 |       29 |       +6 -4 ~10 | no
best at 14,000         |       14,064 | 23,670 |          590 |       29 |        +4 -2 ~4 | no
knee                   |       14,466 | 23,591 |          669 |       29 |        +5 -3 ~4 | yes
best at 15,000         |       15,049 | 23,035 |        1,225 |       28 |        +6 -5 ~5 | no
knee                   |       15,554 | 22,870 |        1,390 |       30 |        +8 -5 ~7 | yes
max risk plan          |       16,086 | 18,886 |        5,374 |       31 |       +10 -6 ~8 | yes
```

How to read a row. "NPV given up" is against the NPV plan. "vs max NPV plan" counts projects added
(+), dropped (−) and moved to another start year (~); a planner reads it as how much of the familiar
plan changes. "weighted sum finds it" says whether the plan is supported (lesson 8.1.2): four of the
round-target rows are not, so a tool built on weighted sums would never have shown them.

Two things in the table deserve a sentence in the review. The $13,000k row, lesson 8.3.1's answer to
the board, keeps 23 of the NPV plan's 27 projects but moves 10 of them to another start year, so much
of the change is timing, not selection. And the last row: the final $532k of
risk (from $15,554k to $16,086k) costs more NPV ($3,984k) than all the steps before it together
($1,390k).

## State Each Step as a Price: NPV Given Up per Dollar of Risk Removed

A planner compares options by what the next one costs. Between two plans on the frontier, the
**price** of moving from the first to the second is the NPV given up divided by the risk gained:

```math
\text{price}(A \to B) = \frac{\text{NPV}_A - \text{NPV}_B}{\text{risk}_B - \text{risk}_A} \quad \text{(\$ of NPV per \$ of risk)}
```

```python
    @property
    def price(self) -> float:
        """Units of `second` given up per unit of `first` gained."""
        return self.cost / self.gain
```

Walk the steps between consecutive **supported** plans, the hull, not between all 65:

```text
The trade-off, step by step along the supported plans:
  risk 10,577 -> 12,348: +$1,771k of risk removed for $162k of NPV, $0.09 of NPV per $1 of risk
  risk 12,348 -> 12,751: +$403k of risk removed for $79k of NPV, $0.20 of NPV per $1 of risk
  risk 12,751 -> 14,466: +$1,716k of risk removed for $428k of NPV, $0.25 of NPV per $1 of risk
  risk 14,466 -> 14,496: +$30k of risk removed for $18k of NPV, $0.60 of NPV per $1 of risk
  risk 14,496 -> 15,554: +$1,058k of risk removed for $703k of NPV, $0.66 of NPV per $1 of risk
  risk 15,554 -> 15,601: +$47k of risk removed for $195k of NPV, $4.19 of NPV per $1 of risk
  risk 15,601 -> 16,086: +$485k of risk removed for $3,789k of NPV, $7.81 of NPV per $1 of risk
Along all 65 plans the 64 steps' prices are not in order: 29 cost less than the step before
```

Along the hull the price only rises. That is what being the upper-right convex hull means: walking
it toward more risk, each segment gives up at least as much NPV per dollar of risk as the one
before it. Along all 65 plans it does not: 29 of the 64 steps are cheaper than the step before,
because an unsupported plan sits in a dent, and the step into a dent is cheap while the step out of
it is dear. A price list built from all 65 points would zig-zag and confuse the reader. Quote the
hull's prices, and show the unsupported plans as options between them.

The prices are the exchange rates that weights imply (lesson 8.1.1), read off the frontier instead
of chosen in advance. A weighted sum that values a dollar of risk at $`w`$ dollars of NPV,
$`\max\, \text{NPV} + w \cdot \text{risk}`$, gains $`w \cdot \text{gain} - \text{cost}`$ by a
step, so it takes every hull step priced below $`w`$ and stops where the next step costs more.

Mind the direction when you compare these prices with lesson 8.1.1's. There, the price
$`p = w_N / w_R`$ is in $k of risk removed per $1k of NPV: how much risk a dollar of NPV is worth.
Here a price is in dollars of NPV given up per dollar of risk removed: what a dollar of risk costs.
One is the reciprocal of the other, and the $`w`$ above is $`1/p`$. The same hull steps, priced
lesson 8.1.1's way:

```python
for s in steps(hull):
    print(f"  risk {s.a.first:,.0f} -> {s.b.first:,.0f}: ${s.price:.2f} of NPV per $1 of risk, "
          f"so {1 / s.price:.3f} $k of risk per $1k of NPV")
```

```text
The same steps priced as in lesson 8.1.1, $k of risk removed per $1k of NPV: the reciprocals
  risk 10,577 -> 12,348: $0.09 of NPV per $1 of risk, so 10.933 $k of risk per $1k of NPV
  risk 12,348 -> 12,751: $0.20 of NPV per $1 of risk, so 5.097 $k of risk per $1k of NPV
  risk 12,751 -> 14,466: $0.25 of NPV per $1 of risk, so 4.009 $k of risk per $1k of NPV
  risk 14,466 -> 14,496: $0.60 of NPV per $1 of risk, so 1.663 $k of risk per $1k of NPV
  risk 14,496 -> 15,554: $0.66 of NPV per $1 of risk, so 1.505 $k of risk per $1k of NPV
  risk 15,554 -> 15,601: $4.19 of NPV per $1 of risk, so 0.239 $k of risk per $1k of NPV
  risk 15,601 -> 16,086: $7.81 of NPV per $1 of risk, so 0.128 $k of risk per $1k of NPV
```

The right-hand column is lesson 8.1.1's table of break-even prices, read in the other order: the
last step, $7.81 of NPV per dollar of risk here, is the break-even price 0.128 there, and
1/0.128 = 7.81. A planner who hears "the price is 4" must ask which way up it is.

<!-- practice 2 -->

## A Knee Is Where the Price Jumps

A **knee** of a frontier is a plan where the price of the next step jumps: before it, risk is
cheap; after it, dear. This course defines a knee as a supported plan where the price of the step
after it is at least twice the price of the step before it (the factor is a parameter, and two is a
judgment, not a standard):

```python
def knees(hull: list[Point], ratio: float = 2.0) -> list[tuple[Point, float, float]]:
    """Hull points where the price of the next step is at least `ratio` times the price of the last.

    Returns (point, price before, price after) for each. Pass the supported points: along them the
    price can only rise, so a knee is where it rises sharply.
    """
    s = steps(hull)
    return [(before.b, before.price, after.price) for before, after in zip(s, s[1:])
            if after.price >= ratio * before.price]
```

```text
Knees (the price at least doubles):
  risk $12,348k, NPV $24,098k: $0.09 per $1 before, $0.20 after
  risk $14,466k, NPV $23,591k: $0.25 per $1 before, $0.60 after
  risk $15,554k, NPV $22,870k: $0.66 per $1 before, $4.19 after
```

Three knees, and they are not equal. At the first two the price doubles or so, from cents to cents.
At the third it multiplies by more than six, from $0.66 to $4.19 of NPV per dollar of risk. That is
the knee the director asked about: past $15,554k of risk removed, each further dollar of risk costs
several dollars of NPV.

A knee is a place to look, not an answer. Whether $4.19 is too much depends on what a dollar of
discounted failure cost is worth to GridCap, which is the swing-weighting question of lesson 7.4.3. What the frontier adds is that the question can
now be asked about one specific step, with both plans on the table.

## Say the Trade-Off in One Sentence

The minutes of the review will hold one sentence, so write it from the data, not by hand:

```text
In one sentence: up to $15,554k of risk removed, each extra $1 of risk costs at most $0.66 of NPV; beyond it, $4.19 to $7.81.
```

The sentence names the knee and the prices on both sides of it. Every number in it comes from the
same frontier as the table, so when the data changes and the frontier is regenerated, the sentence
changes with it.

## Summary

- **Generate the frontier once, and check that no point dominates another.** `exact_frontier` on
  GridCap small gives 65 plans; `dominated` finds no pair. Compare with a tolerance for solver noise.
- **Show a short table, each row a plan the planner could pick.** The ends, the best plan at round
  targets, and the knees: 9 rows instead of 65.
- **State each step as a price.** Along the hull the price rises from $0.09 to $7.81 of NPV per $1
  of risk; along all 65 plans it zig-zags.
- **A knee is where the price jumps.** GridCap small's sharpest knee is at $15,554k of risk, where
  the price goes from $0.66 to $4.19.
- **Say the trade-off in one sentence**, generated from the same data as the table.

## Reference

| Name | Meaning |
| --- | --- |
| `exact_frontier(model, first, second)` | every Pareto point (lesson 8.3.2); here `first` = risk, `second` = NPV |
| `dominated(points)` | every pair where one point dominates another; empty for a true frontier |
| `SAME` | $`10^{-3}`$: values this close count as equal when comparing plans |
| `supported(points)` | the supported points: on the upper-right convex hull, corners and points on its segments, the plans a weighted sum can reach (lesson 8.1.2) |
| `best_reaching(points, target)` | the point with the most `second` among those with `first` ≥ target |
| price of a step | $`(\text{NPV}_A - \text{NPV}_B) / (\text{risk}_B - \text{risk}_A)`$, $ of NPV per $1 of risk: the reciprocal of lesson 8.1.1's price $`p`$ ($k of risk per $1k of NPV) |
| knee | a hull point where the next step's price is at least `ratio` (2) times the last |

**Further reading:** [OR-Tools, MathOpt basic example](https://developers.google.com/optimization/math_opt/basic_example) (the solve and result calls the generator repeats at every floor); [GAMS model library, `epscmmip.gms`](https://gams.com/53/gamslib_ml/libhtml/gamslib_epscmmip.html) (an AUGMECON2 run that writes its payoff table, grid points and Pareto solutions to a results file, the raw form a planner's table is built from); [Mavrotas (2009), record and abstract at NTUA](https://dspace.lib.ntua.gr/xmlui/handle/123456789/19533) (generating methods show the decision maker the whole Pareto set before the choice, and the paper's interactive approach built on AUGMECON).

## Challenges

1. Change the knee factor from 2 to 3. Predict which of the three knees remain.
2. The director asks for the best plan with at most $1,000k of NPV given up. Which table row answers
   it, and is it supported?
3. A planner wants the table in $M with one decimal. Which column loses information that matters
   for reading knees?

## Design Note: Why No Chart

A frontier chart is the natural picture, and a learner who runs the programs can draw one in a few
lines. But a chart is hard to quote: the review's minutes, a rate-case filing and an email to finance
all carry text and tables. A chart also invites reading between the dots, and between two Pareto
plans there is no plan; the next option is the next dot. The table lists only plans that exist, the
prices put the slope into numbers, and the knees say where to look. Draw the chart for yourself, and
hand the planners the table and the sentence.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**present.py.** Generates GridCap small's frontier once, then prints the planner table, the prices
along the hull, the knees and the one-sentence summary (every section). *Try:* Use risk targets
every $500k instead of $1,000k. Predict how many of the new rows are unsupported.

- Program: [present.py](src/present.py)

**planner.py.** The reading functions: `best_reaching`, `Step` with its price, `steps` and `knees`.

- Library: [planner.py](src/planner.py)
