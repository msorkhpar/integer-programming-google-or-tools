# 2.1.3 LP Patterns: Blending, Flows, Multi-Period Carry-Over

Three requests reach GridCap's planning team in the same week. Procurement must buy 20,000 hours
of tree trimming from three contractors, and the regulator wants the season's average rework rate
at 4% or below. Stores must move spare transformers from two depots to four regions, some through
a central hub, at the least shipping cost. And finance asks for lesson 2.1.1's program split over
all five years of the plan, with money a year leaves unspent allowed to roll into the next.

Each is a new LP, and each is an instance of a **pattern**: a shape of model that recurs across
industries, with its own kind of variable and its own kind of row. Blending bounds an average.
Flows balance what enters and leaves each place. Multi-period models carry a stock from one period
to the next. Recognizing the pattern is most of the modeling work, and it is what interviewers ask
about. GridCap, its contractors, depots and numbers are all fictional. Three rules, one per heading.

## A Blend Rule Bounds an Average, and the Average Is Linear Once Multiplied by the Total

The three contractors (invented for this course):

```python
#: contractor -> ($ per crew-hour, rework rate in %, hours it can supply)
CONTRACTORS = {"Northline": (95, 2.0, 10_000), "Birch & Sons": (78, 5.5, 12_000), "Canopy Co": (70, 7.0, 10_000)}
HOURS = 20_000          # crew-hours of trimming GridCap needs this season
TARGET = 4.0            # the average rework rate may be at most 4.0%
```

A contractor's *rework rate* is the share of its work that must be redone; the cheaper
contractors redo more. The decisions are amounts: $`h_c \ge 0`$, the hours bought from
contractor $`c`$, continuous and at most its capacity $`u_c`$. Hours must add up to the need,
$`\sum_c h_c = H`$, and the cost $`\sum_c p_c h_c`$ is minimized, with $`p_c`$ the price per hour.

The new rule is the average. The season's rework rate is the hours-weighted average of the
contractors' rates:

```math
\frac{\sum_c q_c\, h_c}{\sum_c h_c} \le \bar q
```

with $`q_c`$ contractor $`c`$'s rate and $`\bar q = 4.0`$ the target. Like the share rule of lesson
2.1.1, it divides by variables, so it is not linear. Multiply both sides by the total hours (never
negative), and move everything to one side:

```math
\sum_c q_c\, h_c \le \bar q \sum_c h_c
\quad\iff\quad
\sum_c (q_c - \bar q)\, h_c \le 0
```

The second form reads well. Each hour from a contractor better than the target earns a credit
($`q_c - \bar q < 0`$): Northline's earns $`-2.0`$. Each hour from a worse one spends credit:
Birch & Sons $`+1.5`$, Canopy Co $`+3.0`$. The blend is allowed when the credits cover the
spending.

```python
model.add_linear_constraint(sum(h.values()) == HOURS, name="hours")
if blend:
    # average rework <= TARGET, multiplied out by the total hours:  sum (q_c - TARGET) h_c <= 0
    model.add_linear_constraint(sum((q - TARGET) * h[c] for c, (_, q, _) in CONTRACTORS.items()) <= 0,
                                name="rework")
```

The program solves three versions: no rework rule, the blend rule, and a common misreading of it,
"every contractor must be at or under 4%", which excludes the two cheaper contractors:

```python
if per_contractor:
    # the misreading: every contractor at or under the target, so only they may be hired
    for c, (_, q, _) in CONTRACTORS.items():
        if q > TARGET:
            model.add_linear_constraint(h[c] == 0, name=f"exclude_{c}")
```

```text
cheapest, no rule      cost $1,480,000  rework 6.25%  Northline 0  Birch & Sons 10,000  Canopy Co 10,000
average rework <= 4%   cost $1,703,333  rework 4.00%  Northline 10,000  Birch & Sons 6,667  Canopy Co 3,333
each contractor <= 4%  INFEASIBLE
```

With no rule, GridCap buys the two cheapest contractors to capacity, and the season's rework is
6.25%. With the blend rule, the answer is a **mix**: all of Northline's 10,000 hours, which earn
$`10{,}000 \times 2.0 = 20{,}000`$ points of credit, and the other 10,000 hours split so that they
spend exactly that credit. The mix can be checked by hand from the two binding rows:

```math
h_B + h_C = 10{,}000, \qquad 1.5\, h_B + 3.0\, h_C = 20{,}000
\quad\Rightarrow\quad h_B = 6{,}666.7,\ h_C = 3{,}333.3
```

Canopy Co is cheaper per hour, but each of its hours spends twice the credit of a Birch & Sons
hour, so the LP buys Birch & Sons first. The average is exactly 4.00%: the rework row is binding.
The rule cost $`1{,}703{,}333 - 1{,}480{,}000 = 223{,}333`$ dollars.

The misreading is infeasible: only Northline meets 4% on its own, and its 10,000 hours cannot cover
20,000. An average limits the mix, not each ingredient; a blend is valuable precisely because
good ingredients make room for cheap ones.

The same pattern is everywhere: the sulfur content of a fuel blend, the protein in animal feed, the
average age of a vehicle fleet, the average risk score of a portfolio of projects. The recipe is
always the same: write the average, multiply by the total, collect the terms.

The oldest model of this family is the **diet problem**, and OR-Tools ships it as the sample
`stigler_diet.py` (the OR-Tools page on the Stigler diet tells its story). In 1944 the economist
George Stigler asked for the cheapest set of foods, at 1939 prices, that meets nine daily nutrient
minimums. Its data gives, for each of 77 foods, how much of each nutrient one dollar of that food
buys. Adapted to MathOpt, with the sample's own data:

**Sets.** $`F`$, the 77 foods; $`N`$, the 9 nutrients. **Parameters.** $`a_{n,f}`$, the amount of
nutrient $`n`$ that $1 of food $`f`$ buys; $`m_n`$, the daily minimum of nutrient $`n`$ (calories
in thousands of kcal). **Variables.** $`x_f \ge 0`$ for $`f \in F`$, continuous: the dollars a day
spent on food $`f`$. **Units.** The minimums are daily, so the model is a one-day model: its
objective is the cost of the diet in dollars **a day**. The yearly figures in the output are not in
the model; the program multiplies the daily optimum, and each food's daily $`x_f`$, by 365 when it
prints them, as the OR-Tools sample does:

```math
\text{annual cost} = 365 \sum_{f \in F} x_f^*, \qquad \text{annual spend on food } f = 365\, x_f^*
```

```math
\begin{aligned}
\min \;& \sum_{f \in F} x_f \\
\text{s.t. }& \sum_{f \in F} a_{n,f}\, x_f \ge m_n && \forall n \in N && \text{(nutrient}_n) \\
& x_f \ge 0 && \forall f \in F
\end{aligned}
```

```python
model = mathopt.Model(name="stigler-diet")
spend = {food[0]: model.add_variable(lb=0.0, name=food[0]) for food in FOODS}     # $ a day on each food
rows = {}
for i, (nutrient, minimum) in enumerate(NUTRIENTS):
    rows[nutrient] = model.add_linear_constraint(
        sum(food[3 + i] * spend[food[0]] for food in FOODS) >= minimum, name=nutrient)
model.minimize(sum(spend.values()))
```

```text
77 foods, 9 nutrient rows: OPTIMAL, annual cost $39.66
  Wheat Flour (Enriched)   $ 10.77 a year
  Liver (Beef)             $  0.69 a year
  Cabbage                  $  4.09 a year
  Spinach                  $  1.83 a year
  Navy Beans, Dried        $ 22.28 a year
  Calories (1000 kcal)    3.00  min 3     at the minimum
  Protein (g)           147.41  min 70    above
  Calcium (g)             0.80  min 0.8   at the minimum
  Iron (mg)              60.47  min 12    above
  Vitamin A (KIU)         5.00  min 5     at the minimum
  Vitamin B1 (mg)         4.12  min 1.8   above
  Vitamin B2 (mg)         2.70  min 2.7   at the minimum
  Niacin (mg)            27.32  min 18    above
  Vitamin C (mg)         75.00  min 75    at the minimum
```

$39.66 a year, the figure the OR-Tools page reports; Stigler's own diet, found without an LP
solver, cost $39.93. The solver's own optimum is the daily cost, $`39.66 / 365 \approx 0.109`$
dollars, about 11 cents a day at 1939 prices; every "a year" line is that day's spend times 365. Two things to read in it. First, each nutrient row bounds a **total**, not an
average, so it is linear as written and nothing needs multiplying out. A rule such as "at most 30%
of the calories from fat" would bound a ratio of two totals, and it would be multiplied out exactly
like the rework rule. Second, of 77 foods the diet buys only five, and five rows sit at their
minimum. That is the shape of every corner answer. Give each row a surplus amount, so that each of
the 9 rows becomes an equation; there are then 86 amounts (77 foods and 9 surpluses), and a corner
is a point where so many of them sit at their bound 0 that the 9 equations leave only one choice
for the rest. Nine equations can fix at most nine unknowns, so at a corner at most 9 amounts are
nonzero. Here the four rows with surplus use four of the nine, which leaves room for at most five
foods. Lesson 2.2.2 makes this exact: the nonzero amounts of a corner are its **basis**.

<!-- practice 1 -->

## A Flow Model Has One Balance Row per Node: What Comes In, Less What Goes Out

GridCap keeps spare transformers at two depots and needs them in four regions. Some routes are
direct; others go through a central hub (all invented for this course):

```python
SUPPLY = {"Northgate": 45, "Southport": 35}                         # spares on the shelf
DEMAND = {"Ridge": 15, "Valley": 25, "Coast": 18, "Plains": 12}      # spares each region needs
HUB = "Central"
```

The routes, their costs and their capacities, as `ARCS` in `flow.py` sets them:

| From | To | Cost ($k per transformer) | Capacity (transformers) |
| --- | --- | ---: | ---: |
| Northgate | Ridge | 4 | 20 |
| Northgate | Valley | 6 | 10 |
| Northgate | Central | 2 | 40 |
| Southport | Coast | 3 | 25 |
| Southport | Plains | 7 | 10 |
| Southport | Central | 2 | 30 |
| Central | Ridge | 3 | 30 |
| Central | Valley | 3 | 30 |
| Central | Coast | 4 | 30 |
| Central | Plains | 3 | 30 |

A flow model is drawn as a **network**: **nodes** (the depots, the hub, the regions) joined by
**arcs**, one-way routes, each with a cost per unit moved and a **capacity**, the most it can
carry. The decision on each arc $`(i, j)`$ is the **flow** $`f_{ij}`$: how many units move from
$`i`$ to $`j`$, with $`0 \le f_{ij} \le u_{ij}`$.

```python
f = {(i, j): model.add_variable(lb=0, ub=cap, name=f"f_{i}_{j}") for (i, j), (_, cap) in ARCS.items()}
```

The rows come from one idea, applied at every node: **conservation of flow**. Units do not appear
or vanish on the way; what enters a node, less what leaves it, is what the node keeps.

```math
\sum_{(i,n)} f_{in} - \sum_{(n,j)} f_{nj} \;=\; \text{what node } n \text{ keeps}
```

What each node keeps is set by its role:

- A **region** keeps exactly its demand: in − out $`= d_n`$.
- The **hub** stores nothing: in − out $`= 0`$. A node like this is a *transshipment* node.
- A **depot** sends out at most what is on its shelf: out − in $`\le`$ supply. It is $`\le`$
  because spares may stay on the shelf: the depots hold 80 and the regions need 70. Written as an
  equation, the depots would have to ship all 80 spares into regions that accept exactly 70 between
  them, and no flow could satisfy every row: the model would be infeasible.

```python
for n, amount in SUPPLY.items():
    model.add_linear_constraint(outflow(n) - inflow(n) <= amount, name=f"supply_{n}")   # spares may stay put
model.add_linear_constraint(inflow(HUB) - outflow(HUB) == 0, name=f"balance_{HUB}")   # the hub stores nothing
for n, amount in DEMAND.items():
    model.add_linear_constraint(inflow(n) - outflow(n) == amount, name=f"demand_{n}")
model.minimize(sum(cost * f[a] for a, (cost, _) in ARCS.items()))
```

`inflow(n)` and `outflow(n)` are two small helpers that add up the flow variables of the arcs into
and out of node `n`. The answer:

```text
OPTIMAL, cost $299k
  Northgate  -> Ridge     15.0
  Northgate  -> Central   30.0
  Southport  -> Coast     18.0
  Southport  -> Central    7.0
  Central    -> Valley    25.0
  Central    -> Plains    12.0
```

Check the balance rows on the output. The hub takes in $`30 + 7 = 37`$ and sends out
$`25 + 12 = 37`$. Northgate sends $`15 + 30 = 45`$, its whole shelf; Southport sends
$`18 + 7 = 25`$ of its 35. Each route choice is a cost comparison the LP made for every region at
once: Valley is cheaper through the hub ($`2 + 3 = 5`$ per unit) than direct from Northgate
(6), while Coast is cheaper direct from Southport (3) than through the hub ($`2 + 4 = 6`$). Every
number here is in the arc table above, so you can price the plan yourself:
$`15 \cdot 4 + 30 \cdot 2 + 18 \cdot 3 + 7 \cdot 2 + 25 \cdot 3 + 12 \cdot 3 = 299`$ $k.

The flows came out as whole transformers, although every variable was continuous. For a network
model that is not luck. When every supply, demand and capacity is a whole number, a flow LP that
has a best solution has one in whole numbers, and every corner answer, the kind GLOP returns, is
one of them. That follows from the special structure of its rows (each flow
variable appears in exactly two balance rows, with $`+1`$ in one and $`-1`$ in the other). So a
shipping plan, a crew assignment or a routing of units can often be solved as an LP even though the
units are whole. Section 3 explains why this matters: in most models it does not hold, and integer
variables cost a search.

<!-- practice 2 -->

## Multi-Period Carry-Over Is a Stock Variable That Links Each Year's Cash Row to the Next

Lesson 2.1.1's split left $230.3k of the 2027 budget unspent: no program could absorb it. Finance
now asks for the split over all five years of the small portfolio, 2027 to 2031, with each year's
own crews and budget. Without anything new, that is five copies of lesson 2.1.1's model side by
side, $`s_{k,y}`$ for each program and year, and each year's budget row on its own. The new rule is
**carry-over**: money a year leaves unspent may roll into the next year.

The amount carried is something the plan chooses, so it is a variable: $`r_y \ge 0`$, the money
carried out of year $`y`$ into year $`y + 1`$. Each year may spend its budget plus what came in,
less what it sends on:

```math
\sum_{k \in K} s_{k,y} + r_y \;\le\; B_y + r_{y-1}, \qquad r_{y_0 - 1} = 0
```

This is the **cash row** of year $`y`$, and $`y_0`$ is the first year, which has nothing coming in.
A variable like $`r_y`$, which links one period to the next, is a **stock** variable: it is the
amount held between periods. The same shape models inventory (what is in the warehouse at the end
of a month), water in a reservoir and money in an account.

```python
for i, y in enumerate(YEARS):
    if carry:
        incoming = r[YEARS[i - 1]] if i else 0
        model.add_linear_constraint(spend[y] + r[y] <= small.budget[y] + incoming, name=f"cash_{y}")
    else:
        model.add_linear_constraint(spend[y] <= small.budget[y], name=f"budget_{y}")
```

Why $`\le`$ and not $`=`$? Money a year neither spends nor carries **lapses**: it goes back to the
utility at year end. The gap between the two sides of the row is the lapsed amount. An equation
would force every dollar to be spent or carried, and as 2031 below shows, there are years where it
cannot be spent. Lesson 6.4.4 meets the same row in a project model, with caps on the carry.

The objective adds up value over the years, but a dollar of value earned in 2031 is worth less
today than one earned in 2027. So each year's value is **discounted**: divided by
$`(1 + \rho)^{y - y_0}`$, where $`\rho = 0.07`$ is GridCap's discount rate. That is the same idea as
the NPV of lesson 1.1.1: money later is worth less now.

```python
# A dollar of value earned in a later year is worth less today: discount it to the first year.
model.maximize(sum(VALUE[k] / (1 + RATE) ** (y - YEARS[0]) * s[k, y] for k in PROGRAMS for y in YEARS))
```

```text
no carry-over: OPTIMAL, NPV 18,274.8
  2027: budget 8,890  spent   8,659.7
  2028: budget 8,120  spent   8,120.0
  2029: budget 8,760  spent   8,760.0
  2030: budget 8,610  spent   8,610.0
  2031: budget 7,850  spent   4,195.5
with carry-over: OPTIMAL, NPV 18,388.8
  2027: budget 8,890  spent   8,659.7  carried out   230.3
  2028: budget 8,120  spent   8,350.3  carried out     0.0
  2029: budget 8,760  spent   8,760.0  carried out     0.0
  2030: budget 8,610  spent   8,610.0  carried out     0.0
  2031: budget 7,850  spent   4,195.5  carried out     0.0
```

Without carry-over, 2027 spends $8,659.7k, as in lesson 2.1.1, and 2031 spends only $4,195.5k of
its $7,850k: its crews are few (distribution and vegetation can do only $1,785.7k and $312.0k of
work), and transmission may only match the other two. The other three years spend their whole
budget.

With carry-over, 2027's $230.3k moves into 2028, a year whose budget was full, and is spent there:
$`8{,}120 + 230.3 = 8{,}350.3`$. The NPV rises by $`18{,}388.8 - 18{,}274.8 = 114.0`$ $k. But 2031's
$3,654.5k still lapses: carry-over moves money forward, never back, and there is no year after 2031
in the plan to send it to. If finance wanted 2031's money used, the plan would need borrowing ahead
(lesson 6.4.4's practice) or more crews.

With every $`r_y = 0`$, the cash rows are the old budget rows, so the carry-over model allows every
plan the yearly model allows and more: its value can only be the same or higher. The module's tests
check exactly that.

<!-- practice 3 -->

## The Model

The lesson built three models, one per pattern, and adapted OR-Tools' diet model. Each is complete here.

**Blending** (`blend.py`). **Sets.** $`J`$, the contractors. **Parameters.** $`p_c`$, price per
crew-hour ($); $`q_c`$, rework rate (%); $`u_c`$, hours contractor $`c`$ can supply; $`H = 20{,}000`$,
hours needed; $`\bar q = 4.0`$, the target average rework rate (%). **Variables.**
$`0 \le h_c \le u_c`$ for $`c \in J`$, continuous: hours bought from $`c`$.

```math
\begin{aligned}
\min \;& \sum_{c \in J} p_c\, h_c \\
\text{s.t. }& \sum_{c \in J} h_c = H && && \text{(hours)} \\
& \sum_{c \in J} (q_c - \bar q)\, h_c \le 0 && && \text{(rework)} \\
& 0 \le h_c \le u_c && \forall c \in J
\end{aligned}
```

**Diet** (`stigler_diet.py`, adapted from OR-Tools). **Sets.** $`F`$, the foods; $`N`$, the
nutrients. **Parameters.** $`a_{n,f}`$, nutrient $`n`$ bought by $1 of food $`f`$; $`m_n`$, the daily
minimum of nutrient $`n`$. **Variables.** $`x_f \ge 0`$ for $`f \in F`$, continuous: $ a day on food
$`f`$. The objective is the daily cost in dollars; the program prints $`365 \sum_f x_f^*`$ as the
annual cost.

```math
\begin{aligned}
\min \;& \sum_{f \in F} x_f \\
\text{s.t. }& \sum_{f \in F} a_{n,f}\, x_f \ge m_n && \forall n \in N && \text{(nutrient}_n) \\
& x_f \ge 0 && \forall f \in F
\end{aligned}
```

**Flow** (`flow.py`). **Sets.** $`S`$, the depots; $`h`$, the hub; $`R`$, the regions;
$`A`$, the arcs $`(i, j)`$. **Parameters.** $`a_n`$, the spares on depot $`n`$'s shelf; $`d_n`$,
region $`n`$'s demand; $`c_{ij}`$, the cost per unit on arc $`(i,j)`$ ($k); $`u_{ij}`$, its capacity.
**Variables.** $`0 \le f_{ij} \le u_{ij}`$ for $`(i, j) \in A`$, continuous: units moved on the arc.

```math
\begin{aligned}
\min \;& \sum_{(i,j) \in A} c_{ij}\, f_{ij} \\
\text{s.t. }& \sum_{(n,j) \in A} f_{nj} - \sum_{(i,n) \in A} f_{in} \le a_n && \forall n \in S && \text{(supply}_n) \\
& \sum_{(i,h) \in A} f_{ih} - \sum_{(h,j) \in A} f_{hj} = 0 && && \text{(balance\_Central)} \\
& \sum_{(i,n) \in A} f_{in} - \sum_{(n,j) \in A} f_{nj} = d_n && \forall n \in R && \text{(demand}_n) \\
& 0 \le f_{ij} \le u_{ij} && \forall (i,j) \in A
\end{aligned}
```

**Multi-period split with carry-over** (`carry_over_lp.py`). **Sets.** $`K`$, the programs;
$`Y = \{2027, \dots, 2031\}`$, the years, $`y_0 = 2027`$ the first. **Parameters.** $`v_k`$, $`m_k`$,
$`f`$, $`\alpha`$ as in lesson 2.1.1; $`C_{k,y}`$, program $`k`$'s crew-months in year $`y`$;
$`B_y`$, year $`y`$'s budget ($k); $`\rho = 0.07`$, the discount rate. **Variables.**
$`s_{k,y} \ge 0`$, the $k spent on program $`k`$ in year $`y`$; $`r_y \ge 0`$, the $k carried out of
year $`y`$; both continuous, with $`r_{y_0 - 1} = 0`$.

```math
\begin{aligned}
\max \;& \sum_{y \in Y} \sum_{k \in K} \frac{v_k}{(1 + \rho)^{y - y_0}}\, s_{k,y} \\
\text{s.t. }& \sum_{k \in K} s_{k,y} + r_y \le B_y + r_{y-1} && \forall y \in Y && \text{(cash}_y) \quad \leftarrow \text{new} \\
& \frac{m_k}{1000}\, s_{k,y} \le C_{k,y} && \forall k \in K,\ y \in Y && \text{(crew}_{k,y}) \\
& s_{\text{vegetation},y} \ge f && \forall y \in Y && \text{(floor\_vegetation}_y) \\
& s_{k,y} \le \alpha \sum_{j \in K} s_{j,y} && \forall k \in K,\ y \in Y && \text{(share}_{k,y}) \\
& s_{k,y} \ge 0,\ r_y \ge 0 && \forall k \in K,\ y \in Y
\end{aligned}
```

Without carry-over, the cash rows are replaced by $`\sum_k s_{k,y} \le B_y`$, labelled
$`\text{(budget}_y)`$, and there are no $`r_y`$.

## Summary

- **A blend rule bounds an average.** Multiply by the total and collect terms:
  $`\sum_c (q_c - \bar q)\, h_c \le 0`$. It limits the mix, not each ingredient.
- **A flow model has one balance row per node**: in − out equals what the node keeps; $`\le`$ at a
  source that may keep stock, $`=`$ where nothing is stored. With whole-number data, a flow LP has
  a whole-number best solution.
- **Carry-over is a stock variable** linking each period's row to the next. The cash row is
  $`\le`$ because unspent money lapses; carry-over moves money forward only.

## Reference

| Pattern | Variables | Typical row |
| --- | --- | --- |
| blending | amount of each input, $`h_c \ge 0`$ | $`\sum_c (q_c - \bar q)\, h_c \le 0`$ |
| flow (network) | flow on each arc, $`0 \le f_{ij} \le u_{ij}`$ | in − out = demand (or $`\le`$ supply, or $`= 0`$) |
| multi-period stock | amount per period, stock between periods, $`r_y \ge 0`$ | $`\text{use}_y + r_y \le \text{new}_y + r_{y-1}`$ |
| discounting | | coefficient $`v / (1 + \rho)^{y - y_0}`$ |
| diet (covering) | amount of each food, $`x_f \ge 0`$ | total of a nutrient $`\ge`$ its minimum |

**Further reading:** [The Stigler Diet Problem (OR-Tools)](https://developers.google.com/optimization/lp/stigler_diet) (the diet model adapted above, its history, and GLOP's answer of $39.66 against Stigler's $39.93); [OR-Tools sample stigler_diet.py](https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/stigler_diet.py) (the same model in the linear solver wrapper, `pywraplp`, with the full data); [Minimum Cost Flows (OR-Tools)](https://developers.google.com/optimization/flow/mincostflow) (OR-Tools' dedicated network solver, `SimpleMinCostFlow`, on the same kind of supply, demand and transshipment model, with whole-number data); [Network Flows (OR-Tools)](https://developers.google.com/optimization/flow) (the flow problems OR-Tools has special solvers for); [MO-book, Chapter 2: Linear optimization](https://mobook.github.io/MO-book/notebooks/02/02.00.html) (more LP patterns, among them regression and portfolio models, each built in Pyomo).

## Challenges

1. Procurement wants at least 30% of the hours from local contractors (say Birch & Sons and Canopy
   Co). Write the row, multiplied out, and predict whether today's blend already satisfies it.
2. In the flow model, the hub can store up to 5 spares for next season. Which row changes, and how?
3. Finance offers 2% interest on carried money. Change the cash row's coefficient of $`r_{y-1}`$,
   and say whether the NPV can fall.

## Design Note: Patterns Combine

Real models are rarely one pattern. GridCap's capital plan is a multi-period model (stocks of money
across years) whose spend is fed by projects (section 3's yes/no decisions), with blend-like
rules on regional shares and flow-like rules on crews moving between regions. Name the pattern of
each rule when you write it: the row's shape follows, and so do its pitfalls (the ratio that must be
multiplied out, the balance row that must be $`\le`$ where stock may stay, the cash row that must
allow money to lapse).

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**blend.py.** Buys trimming hours from three contractors under an average rework rule, and shows the
per-contractor misreading (*A Blend Rule Bounds an Average*). *Try:* Lower the target to 3.0%.
Predict whether a blend still exists before you run it.

- Program: [blend.py](src/blend.py)

**stigler_diet.py.** Adapted from the OR-Tools sample `stigler_diet.py`: the cheapest 1939 diet
that meets nine nutrient minimums, solved with GLOP through MathOpt (*A Blend Rule Bounds an
Average*). *Try:* Delete Navy Beans from `FOODS`. Predict whether the annual cost rises, and by
more or less than a dollar.

- Program: [stigler_diet.py](src/stigler_diet.py)

**flow.py.** Ships spare transformers from two depots, direct or through a hub, to four regions
(*A Flow Model Has One Balance Row per Node*). *Try:* Cut the Central → Valley capacity to 20.
Predict where the other 5 spares for Valley come from.

- Program: [flow.py](src/flow.py)

**carry_over_lp.py.** The five-year program split, with and without carry-over (*Multi-Period
Carry-Over*). *Try:* Give 2031 eight distribution crew-months instead of four. Predict whether any
money still lapses in 2031.

- Program: [carry_over_lp.py](src/carry_over_lp.py)
