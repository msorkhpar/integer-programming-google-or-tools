# 2.3.2 Weak and Strong Duality, Complementary Slackness

GridCap's planners now split the budget over three years, 2027 to 2029, across all three programs,
with crews, carry-over and the vegetation floor. A colleague built a plan in a spreadsheet: meet
the $900k vegetation floor evenly, $300k a year, fill distribution, and give the rest to
transmission. It is worth $4,108.7k. The solver's plan is worth $4,109.6k. Is the colleague's plan
"basically optimal"? How would you *prove* that the solver's plan is the best, to someone who does
not trust the solver, or that a plan is not, and what to change? Duality answers all three, with
three facts: weak duality, strong duality and complementary slackness. (GridCap is fictional; its
numbers come from the course's generator.)

## The Model

This is the module's running model, the GridCap budget LP on the tiny portfolio. It is the
one-year model of lesson 2.3.1 repeated for three years and three programs, with two links between
the years: money may be carried from one year to the next (the carry-over pattern of lesson
2.1.3), and the vegetation floor counts all three years together.

**Sets.** $`G`$ the programs (transmission, distribution, vegetation); $`Y = \{2027, 2028, 2029\}`$
the years, with $`y_0 = 2027`$ the first and $`\hat y = 2029`$ the last.

**Parameters.** Money in $k.

- $`v_g`$: NPV per $k spent in program $`g`$ in 2027: 0.43 (transmission), 0.66 (distribution),
  0.31 (vegetation), computed as in lesson 2.3.1.
- $`\delta_y = 1.07^{-(y - y_0)}`$: GridCap's 7% discount factor. A $k spent in 2028 returns
  $`v_g \delta_{2028}`$, worth less than the same work in 2027.
- $`B_y`$: the budget of year $`y`$: 2,300, 3,280 and 2,310.
- $`k_g`$: $k of work a crew-month delivers: 430, 440 and 170.
- $`C_{g,y}`$: crew-months available, from GridCap. Times $`k_g`$, the capacities in $k are:
  transmission 1,720, 5,160, 2,150; distribution 880, 2,640, 1,320; vegetation 680, 340, 340.
- $`F = 900`$: the vegetation floor over the three years (this module's assumption, not GridCap
  data).

**Variables.** $`s_{g,y} \ge 0`$ for every $`g \in G`$, $`y \in Y`$: $k spent on program $`g`$ in
year $`y`$. $`r_y \ge 0`$ for $`y \in Y \setminus \{\hat y\}`$: $k carried out of year $`y`$ into
the next. Money carried out of the last year has nowhere to go, so $`r_{\hat y}`$ does not exist;
for the formula below read $`r_{\hat y} = 0`$ and $`r_{y_0 - 1} = 0`$.

**Objective.**

```math
\max \; \sum_{g \in G} \sum_{y \in Y} v_g\, \delta_y\, s_{g,y}
```

**Constraints.**

```math
\begin{aligned}
\sum_{g \in G} s_{g,y} + r_y - r_{y-1} &\le B_y && \forall y \in Y && \text{(cash}_y) \\
s_{g,y} &\le k_g\, C_{g,y} && \forall g \in G,\ y \in Y && \text{(crew}_{g,y}) \\
\sum_{y \in Y} s_{\text{veg},y} &\ge F && && \text{(veg\_floor)}
\end{aligned}
```

The code names each row exactly as the formulation labels it (`cash_2028`,
`crew_distribution_2028`, `veg_floor`):

```python
spend = {(g, y): model.add_variable(lb=0, name=f"spend_{g}_{y}") for g in PROGRAMS for y in years}
carry = {y: model.add_variable(lb=0, name=f"carry_{y}") for y in years[:-1]}
cash, crew = {}, {}
for i, y in enumerate(years):
    carried_in = carry[years[i - 1]] if i else 0
    carried_out = carry.get(y, 0)
    cash[y] = model.add_linear_constraint(
        sum(spend[g, y] for g in PROGRAMS) + carried_out - carried_in <= budget[y], name=f"cash_{y}")
    for g in PROGRAMS:
        crew[g, y] = model.add_linear_constraint(spend[g, y] <= k[g] * portfolio.crews[g, y],
                                                 name=f"crew_{g}_{y}")
veg_floor = None
if floor is not None:
    veg_floor = model.add_linear_constraint(sum(spend["vegetation", y] for y in years) >= floor,
                                            name="veg_floor")
model.maximize(sum(v[g] * discount(portfolio, y) * spend[g, y] for g in PROGRAMS for y in years))
```

It has 11 variables and 13 rows, so its dual, written with `dualize` from lesson 2.3.1, has 13
price variables and 11 cover rows:

```text
primal: 11 variables, 13 rows; dual: 13 variables, 11 rows
```

## Weak Duality: No Plan Is Worth More Than Any Covering Prices' Bound

Lesson 2.3.1 showed, on the one-year model, that covering prices prove an upper bound. The same
holds for every LP, with every kind of row. Write the primal as maximizing $`\sum_j c_j x_j`$ with
$`x_j \ge 0`$, rows $`a_i^\top x \le b_i`$, $`\ge b_i`$ or $`= b_i`$, and prices $`y_i`$ with the
signs of lesson 2.3.1. **Dual feasible** prices are prices with those signs that cover every
variable: $`\sum_i a_{ij}\, y_i \ge c_j`$ for every $`j`$. Then for every feasible plan $`x`$:

```math
\sum_j c_j\, x_j \;\le\; \sum_j \Big(\sum_i a_{ij}\, y_i\Big) x_j \;=\; \sum_i y_i\, (a_i^\top x) \;\le\; \sum_i y_i\, b_i
```

The first $`\le`$ is the cover condition times $`x_j \ge 0`$. The middle $`=`$ only regroups the
same products by row instead of by column. The last $`\le`$ holds row by row: a $`\le`$ row has
$`a_i^\top x \le b_i`$ and $`y_i \ge 0`$; a $`\ge`$ row has $`a_i^\top x \ge b_i`$ and
$`y_i \le 0`$, and multiplying by a nonpositive number flips the direction back; an equality row
has $`a_i^\top x = b_i`$. This is **weak duality**: *every feasible plan's value is at most every
dual feasible price system's bound* $`\sum_i b_i\, y_i`$.

Three small functions check it on GridCap without solving anything. `reduced_cost` is the
variable's objective coefficient minus what its column costs at the given prices (the next sections
use it again); a price system is dual feasible when every price has its row's sign and no reduced
cost is positive, which is the cover condition rearranged:

```python
def reduced_cost(model: mathopt.Model, var: mathopt.Variable, prices: dict[str, float]) -> float:
    """The variable's objective coefficient less the price of everything one unit of it uses."""
    used = sum(row.get_coefficient(var) * prices[row.name] for row in model.column_nonzeros(var))
    return model.objective.get_linear_coefficient(var) - used
```

```python
def prices_are_feasible(model: mathopt.Model, prices: dict[str, float]) -> bool:
    """Dual feasible: each price has its row's sign, and no variable has a positive reduced cost."""
    for row in model.linear_constraints():
        y = prices[row.name]
        if row.lower_bound == -math.inf and y < -TOL:      # <= row needs y >= 0
            return False
        if row.upper_bound == math.inf and y > TOL:        # >= row needs y <= 0
            return False
    return all(reduced_cost(model, var, prices) <= TOL for var in model.variables())
```

```python
def price_bound(model: mathopt.Model, prices: dict[str, float]) -> float | None:
    """The upper bound the prices prove (the dual objective), or None if they prove nothing."""
    if not prices_are_feasible(model, prices):
        return None
    return sum(rhs(row) * prices[row.name] for row in model.linear_constraints())
```

`TOL` is $`10^{-6}`$: solvers compute in floating point, so "zero" means "within a tolerance".
The program checks three plans (the solver's, the colleague's, and one that funds transmission
first) and four price systems:

```text
plan   solver's plan               feasible True   value   4,109.6
plan   floor spread evenly         feasible True   value   4,108.7
plan   transmission first          feasible True   value   3,138.0
prices cash at 0.66                bound   5,207.4
prices cash 0.5, dist. crews 0.16  bound   4,719.4
prices solver's duals              bound   4,109.6
prices solver's cash duals only    prove nothing (not dual feasible)
best plan 4,109.6 <= smallest bound 4,109.6: True
```

Every plan is below every bound, as weak duality says. Two consequences are worth keeping:

- **A gap you can quote.** The colleague's plan is worth 4,108.7 and the solver's prices prove no
  plan exceeds 4,109.6, so the colleague's plan is at most $0.9k short of the best possible, out
  of $4,109.6k. You know this from one plan and one price system, without knowing the optimum.
  The same idea, a proven bound against the best plan found, is the *gap* every MILP solver reports
  (lesson 3.4.1).
- **A certificate of optimality.** If a plan's value equals some dual feasible bound, the plan is
  optimal: nothing can beat the bound, and the plan reaches it. The solver's plan and the solver's
  duals form such a pair.

The last price line is a warning. Keeping only the solver's cash prices and zeroing the crew prices
leaves distribution uncovered: its value 0.66 is more than the cash price 0.43. Prices that do not
cover every variable prove nothing, however reasonable they look.

## Strong Duality: At the Optimum the Two Values Are Equal

Weak duality says plan values sit below bounds. **Strong duality** says that the gap between them
closes: *if the primal LP has an optimal plan, the dual has optimal prices, and the two optimal
values are equal.* Its proof is longer than weak duality's (it follows from the simplex method of
lesson 2.2.2, or from a separation argument), and LP textbooks give it in full. What you need is the
statement, and to see it hold on GridCap: the program solves the budget LP and the dual that
`dualize` writes for it.

```python
primal = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
dual = mathopt.solve(dual_model, mathopt.SolverType.GLOP)
```

```text
primal OPTIMAL max 4,109.6030
dual   OPTIMAL min 4,109.6030
dual LP's prices equal MathOpt's dual_values on all 13 rows: True
```

The same number from two different LPs, and the dual LP's optimal prices are the prices MathOpt
reports for the primal. That is why a solver can return `dual_values` "for free": the simplex method
finds optimal prices together with the optimal plan, and they certify each other.

Strong duality has a statement for the cases where there is no optimum, too. Weak duality already
rules some combinations out (an unbounded primal would exceed every bound, so no bound can exist):

| Primal (max) | Dual (min) |
| --- | --- |
| has an optimal plan | has optimal prices, with the same value |
| unbounded (value can grow without limit) | infeasible (no covering prices exist) |
| infeasible (no plan satisfies the rows) | unbounded or infeasible |

Here is the third line on GridCap. A vegetation floor of $2,000k is more than the vegetation crews
can do in three years ($`680 + 340 + 340 = 1360`$), so no plan exists:

```python
too_high = build(tiny, floor=2000)
dual_model, _ = dualize(too_high.model)
```

```text
floor 2000: primal INFEASIBLE | dual with GLOP INFEASIBLE_OR_UNBOUNDED | dual with HiGHS UNBOUNDED
floor 2000: the floor-900 prices are still dual feasible, bound 3,977.6
```

The dual's constraints (the cover rows) do not depend on the primal's right-hand sides, so prices
that were dual feasible with a floor of 900 still are with a floor of 2,000: the dual is feasible.
A feasible dual whose primal has no plan must be unbounded: there is a direction in which the
prices can move, staying feasible, and push the bound down without end. GLOP only reports that the
dual is infeasible or unbounded; HiGHS says which. That direction, called a *dual ray*, is a proof
that the primal is infeasible, and section 9 uses it to find which rows conflict.

## Complementary Slackness: Slack Rows Have Price Zero, Used Variables Have Reduced Cost Zero

Strong duality says the optimal plan and prices have equal values. Look at *how* the gap between a
plan's value and a bound is made up, and you get a condition you can check row by row. Take any
feasible plan $`x`$ and any dual feasible prices $`y`$, and let $`d_j = c_j - \sum_i a_{ij} y_i`$
be the reduced cost of variable $`j`$ (the function above). Then

```math
\underbrace{\sum_i b_i\, y_i - \sum_j c_j\, x_j}_{\text{bound} \,-\, \text{value}}
\;=\; \sum_i y_i\, \big(b_i - a_i^\top x\big) \;+\; \sum_j x_j\, \big(-d_j\big)
```

(substitute $`c_j = d_j + \sum_i a_{ij} y_i`$ and regroup). Every term on the right is
$`\ge 0`$: a $`\le`$ row has $`y_i \ge 0`$ and $`b_i - a_i^\top x \ge 0`$; a $`\ge`$ row has both
$`\le 0`$; an equality row has $`b_i - a_i^\top x = 0`$; and dual feasibility gives $`d_j \le 0`$
with $`x_j \ge 0`$. A sum of nonnegative terms is zero only if every term is zero. So the gap is
zero (the plan and prices are both optimal) exactly when:

- **every row:** slack $`\times`$ price $`= 0`$. A row with slack has price 0; a row with a nonzero
  price is binding.
- **every variable:** value $`\times`$ reduced cost $`= 0`$. A variable the plan uses has reduced
  cost 0; a variable with a nonzero reduced cost is at 0.

This is **complementary slackness**. "Complementary" because in each pair at least one side is
zero. Note the direction: a binding row *may* also have price 0, and a variable at 0 *may* have
reduced cost 0. The rule forbids both sides being nonzero, nothing else.

The program prints both products for the solver's plan and prices. `slack` is the room a row has
left, $`\ge 0`$ for every row the plan satisfies:

```python
def slack(row: mathopt.LinearConstraint, plan: dict[str, float]) -> float:
    """How far the plan is from the row's limit: >= 0 when the row holds, 0 when it binds."""
    if row.upper_bound < math.inf and row.lower_bound > -math.inf:        # == row
        return -abs(activity(row, plan) - row.upper_bound)
    if row.upper_bound < math.inf:                                         # <= row
        return row.upper_bound - activity(row, plan)
    return activity(row, plan) - row.lower_bound                           # >= row
```

```text
row                           slack    price  product
cash_2027                       0.0     0.43      0.0
crew_transmission_2027        520.0      0.0      0.0
crew_distribution_2027          0.0     0.23      0.0
crew_vegetation_2027          460.0      0.0      0.0
cash_2028                       0.0   0.4019      0.0
crew_transmission_2028       4860.0      0.0      0.0
crew_distribution_2028          0.0    0.215      0.0
crew_vegetation_2028            0.0   0.0079      0.0
cash_2029                       0.0   0.3756      0.0
crew_transmission_2029       1500.0      0.0      0.0
crew_distribution_2029          0.0   0.2009      0.0
crew_vegetation_2029            0.0   0.0152      0.0
veg_floor                       0.0    -0.12      0.0

variable                      value red.cost  product
spend_transmission_2027      1200.0      0.0      0.0
spend_transmission_2028       300.0      0.0      0.0
spend_transmission_2029       650.0      0.0      0.0
spend_distribution_2027       880.0      0.0      0.0
spend_distribution_2028      2640.0      0.0      0.0
spend_distribution_2029      1320.0      0.0      0.0
spend_vegetation_2027         220.0      0.0      0.0
spend_vegetation_2028         340.0      0.0      0.0
spend_vegetation_2029         340.0      0.0      0.0
carry_2027                      0.0  -0.0281      0.0
carry_2028                      0.0  -0.0263      0.0
```

Every product is zero. The rows with slack (transmission crews in every year, and vegetation
crews in 2027) have price 0: more of those crews would not change the plan. Every program-year
that is funded has reduced cost 0: at these prices, each funded $k returns exactly what the
budget, crews and floor it uses are worth.

The carry variables are not used, and their reduced costs say why. Carrying $1k out of 2027 frees
$1k of 2027 cash, priced 0.43, and spends it in 2028, priced 0.4019. Its reduced cost is
$`0 - (0.43 - 0.4019) = -0.0281`$: every $1k carried would lose $0.0281k of value. A negative
reduced cost on a variable at 0 is the LP saying "using this would cost you this much per unit".

<!-- practice 1 -->

## Complementary Slackness Certifies a Plan Without a Solver

Complementary slackness can also be run backwards: from a plan alone, it tells you what the prices
would have to be if the plan were optimal. Then one check decides whether it is:

1. Every row with slack gets price 0.
2. Every variable the plan uses gets reduced cost 0: $`\sum_i a_{ij}\, y_i = c_j`$. That is one
   linear equation per used variable, in the prices of the binding rows.
3. Solve those equations. If the prices that come out are dual feasible (right signs, no positive
   reduced cost), the plan and the prices satisfy complementary slackness, so the gap is zero and
   the plan is optimal. If not, the plan is not optimal, and the violation shows what to change.

```python
def prices_from_plan(plan: dict[str, float]) -> dict[str, float]:
    """Price 0 on every row with slack; solve 'reduced cost = 0' for every variable the plan uses."""
    rows = [row for row in model.linear_constraints() if abs(slack(row, plan)) <= TOL]     # binding rows
    used = [var for var in model.variables() if plan[var.name] > TOL]                       # positive variables
    A = np.array([[row.get_coefficient(var) for row in rows] for var in used])              # one equation per variable
    c = np.array([model.objective.get_linear_coefficient(var) for var in used])
    y = np.linalg.solve(A, c)                                                               # needs as many of each
    prices = {row.name: 0.0 for row in model.linear_constraints()}
    prices.update({row.name: float(p) for row, p in zip(rows, y)})
    return prices
```

`np.linalg.solve(A, c)` solves the square system $`A y = c`$: here one row of `A` per used
variable, one column per binding row. Both plans below have as many binding rows as used variables
(9 and 8), so the system is square. The program applies it to the solver's plan, and to a plan that
meets the vegetation floor early: $680k of vegetation in 2027 (all its crews), $220k in 2028 and
none in 2029.

```text
solver's plan: value 4,109.60, prices dual feasible: True
floor met early: value 4,103.50, prices dual feasible: False
  crew_vegetation_2027: price -0.0079 has the wrong sign for a <= row
  spend_vegetation_2029: reduced cost 0.0073 > 0, so more of it would pay
```

The solver's plan is certified: the prices complementary slackness forces are the solver's own
duals, and they are dual feasible. Anyone with the model and these 13 numbers can check the proof
with a calculator.

The second plan is feasible but not optimal, and the two violations say why. The vegetation crew
limit in 2027 gets a negative price: the plan treats more 2027 vegetation capacity as a loss, so it
uses more than it should. And vegetation in 2029 has a positive reduced cost: at the prices this
plan implies, each $1k of vegetation work moved to 2029 would gain value. Both point to the same
move, the one the solver made: do the floor's vegetation work in 2028 and 2029, where it displaces
less valuable transmission work, and only the remainder in 2027.

The square-system shortcut needs the plan to have as many binding rows as used variables, which is
true of the corner-point plans the simplex method returns (lesson 2.2.2). When a plan has more
binding rows than used variables (a *degenerate* plan, lesson 2.2.3), several price systems fit
and you search among them with a small LP instead; the idea is unchanged.

<!-- practice 2 -->

## Summary

- **Weak duality: no plan is worth more than any covering prices' bound.** A plan and a dual
  feasible price system bracket the optimum, so the difference of their values is a proven gap.
- **Strong duality: at the optimum the two values are equal.** The optimal plan and the optimal
  prices certify each other; an infeasible primal has an infeasible or unbounded dual, and an
  unbounded primal has an infeasible dual.
- **Complementary slackness: slack rows have price zero, used variables have reduced cost zero.**
  The gap between bound and value is a sum of slack $`\times`$ price and value $`\times`$ reduced
  cost terms, all $`\ge 0`$, so it is zero exactly when each product is.
- **Complementary slackness certifies a plan without a solver.** Price slack rows at 0, solve
  "reduced cost = 0" for the used variables, and check the signs.

## Reference

| Fact | Statement (primal max, dual min) |
| --- | --- |
| weak duality | $`c^\top x \le b^\top y`$ for every feasible $`x`$ and dual feasible $`y`$ |
| strong duality | if the primal has an optimum, $`\max c^\top x = \min b^\top y`$ |
| reduced cost | $`d_j = c_j - \sum_i a_{ij}\, y_i`$; dual feasible means $`d_j \le 0`$ for every $`x_j \ge 0`$ |
| complementary slackness | $`\text{slack}_i \cdot y_i = 0`$ for every row, $`x_j \cdot d_j = 0`$ for every variable |
| optimality certificate | $`x`$ feasible, $`y`$ dual feasible, and complementary slackness (equivalently $`c^\top x = b^\top y`$) |

| Primal | Dual |
| --- | --- |
| optimal | optimal, same value |
| unbounded | infeasible |
| infeasible | unbounded or infeasible |

**Further reading:** [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (the duality gap as a solver's test of optimality, and why in simplex it is driven only by floating-point error); [MathOpt sample advanced_linear_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py) (asks the result whether it holds a dual feasible solution before reading the prices, which most LP solvers return with an optimum); [MO-book 2.6, Dual of the BIM production problem](https://mobook.github.io/MO-book/notebooks/02/06-bim-dual.html) (the dual derived from multipliers, as here, on a production model, and strong duality seen on its optimal values, with Pyomo); [HiGHS, Feasibility and optimality](https://ergo-code.github.io/HiGHS/dev/guide/kkt/) (the optimality conditions a solver checks, written for a minimization in equality form, including the complementarity condition $`x^\top s = 0`$); [Vanderbei, *Linear Programming: Foundations and Extensions*](https://vanderbei.princeton.edu/LPbook/) (the textbook's page, with its [Advanced Pivot Tool](https://vanderbei.princeton.edu/JAVA/pivot/advanced.html), which marks every primal and every dual infeasibility of a dictionary until both are gone).

## Challenges

1. A plan is worth 4,050 and you have dual feasible prices proving a bound of 4,140. What is the
   most the plan can be short of the optimum, and what can you not conclude about the optimum's
   value?
2. In the complementary slackness table, `crew_vegetation_2028` binds and has price 0.0079.
   Predict what happens to the plan's value if the 2028 vegetation crews grow by one crew-month
   ($170k of capacity), then check by changing the data.
3. Write a plan that spreads the floor as $300k a year (the colleague's plan) and run
   `prices_from_plan` on it. Before running, predict which row or variable will show a violation.

## Design Note: A Plan Without Its Prices Is Unverified

A solver's "OPTIMAL" is a claim. The prices are the evidence: with them, anyone can check
optimality in a few lines that do not depend on the solver's code, as `prices_are_feasible` and
`slack` do above. Production planning code that saves the plan should save the dual values with it,
and its tests can check complementary slackness on every solve. That catches a model that changed
under the plan (a row added, a sign flipped) much earlier than a planner will.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**weak_duality.py.** Three hand-made plans and four price systems on the budget LP, with every
value and bound (*Weak Duality*). *Try:* Add a price system with every cash price at 0.5 and every
crew price at 0. Predict whether it proves a bound.

**strong_duality.py.** The budget LP and its dual solved side by side, then a floor too high for
any plan (*The Model*, *Strong Duality*). *Try:* Set the floor to 1,360, exactly what the crews can
do. Predict both statuses.

**complementary.py.** Slack times price for every row, value times reduced cost for every variable
(*Complementary Slackness: Slack Rows Have Price Zero, Used Variables Have Reduced Cost Zero*).
*Try:* Build the model with `floor=None` and predict which products change.

**certify.py.** Prices from a plan by complementary slackness, and the sign check that certifies or
refutes it (*Complementary Slackness Certifies a Plan Without a Solver*). *Try:* Move $100k of
vegetation in the second plan from 2027 to 2029 (and $100k of transmission back) and predict
whether the violations disappear.

- Program: [weak_duality.py](src/weak_duality.py)
- Program: [strong_duality.py](src/strong_duality.py)
- Program: [complementary.py](src/complementary.py)
- Program: [certify.py](src/certify.py)
- Library: [certificates.py](src/certificates.py)
- Library: [budget_lp.py](src/budget_lp.py)
- Library: [dualize.py](src/dualize.py)
