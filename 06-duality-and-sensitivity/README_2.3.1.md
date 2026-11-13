# 2.3.1 The Dual LP and What Its Variables Price

GridCap's 2027 budget is $2,300k, and the planners split it between two programs: distribution
work, which returns $0.66k of NPV for every $1k spent, and transmission work, which returns
$0.43k. Each program can only absorb what its crews can do. An LP gives the best split. Then the
finance partner asks two different questions: "what would one more $1k of 2027 budget be worth?"
and "should we hire more transmission crews?" Neither is a question about the plan. They ask what
each *limit* is worth. Every LP has a second LP attached to it, the **dual**, whose variables are
exactly those values. This lesson builds it by hand, in four rules, and then lets code build it
for any LP. (GridCap is a fictional utility; its numbers come from the course's generator, not
from a real company.)

## The Model

We start from the smallest model that has the two questions in it: one year, two programs. In
this module an LP is called the **primal** when we want to tell it apart from its dual.

**Sets.** Two programs: distribution ($`d`$) and transmission ($`t`$). One year, 2027.

**Parameters.** All money is in $k (thousands of dollars).

- $`v_d = 0.66`$ and $`v_t = 0.43`$: NPV returned per $k spent, in each program. They are
  computed from the tiny GridCap portfolio: each program's projects' total NPV divided by their
  total cost, rounded to two decimals.
- $`B = 2300`$: the 2027 budget.
- $`D = 880`$ and $`T = 1720`$: the most distribution and transmission work the 2027 crews can do,
  in $k. GridCap gives crew-months per program and year (2 for distribution, 4 for
  transmission), and a crew-month delivers about $440k of distribution work or $430k of
  transmission work (each program's total cost over its total crew-months, rounded to tens).

**Variables.** $`d \ge 0`$ and $`t \ge 0`$: the $k spent on distribution and on transmission
in 2027. They are continuous: money can be split to the dollar.

**Objective.**

```math
\max \; 0.66\, d + 0.43\, t
```

**Constraints.**

```math
\begin{aligned}
d + t &\le 2300 && \text{(budget)} \\
d &\le 880 && \text{(crew\_d)} \\
t &\le 1720 && \text{(crew\_t)}
\end{aligned}
```

The code is the five parts of every MathOpt program (lesson 1.1.3): a model, variables with their
bounds, named rows, an objective, a solve.

```python
def primal(budget: float = B) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="one-year")
    d = model.add_variable(lb=0, name="d")      # $k spent on distribution in 2027
    t = model.add_variable(lb=0, name="t")      # $k spent on transmission in 2027
    model.add_linear_constraint(d + t <= budget, name="budget")
    model.add_linear_constraint(d <= D, name="crew_d")
    model.add_linear_constraint(t <= T, name="crew_t")
    model.maximize(v["distribution"] * d + v["transmission"] * t)
    return model, {"d": d, "t": t}
```

```text
value per $k: distribution 0.66, transmission 0.43
budget B = 2300, distribution crews D = 880, transmission crews T = 1720
primal: OPTIMAL, value 1,191.4, plan {'d': 880.0, 't': 1420.0}
```

The plan is what intuition says: fill distribution, the better program, up to its crews (880), and
put the rest of the budget into transmission (1,420). Its value is
$`0.66 \cdot 880 + 0.43 \cdot 1420 = 580.8 + 610.6 = 1191.4`$.

Two words for what the plan does to each row. A row is **binding** (or *tight*) when the plan
meets it with equality: the budget is all spent, and distribution uses all its crews. A row has
**slack** when there is room left: transmission uses $1,420k of its $1,720k of crews, a slack
of 300. Lesson 2.1.2 introduces slack in detail; here it is just "limit minus what is used".

## Any Nonnegative Prices on the Rows Give an Upper Bound

Before asking what a limit is worth, ask a simpler question: *without solving*, can we prove that
no plan is worth more than some number? Here is a way. Pick a number $`y \ge 0`$ for each row,
call it the row's **price**, multiply each row by its price, and add the rows up. With prices
$`y_b`$ (budget), $`y_d`$ (crew_d) and $`y_t`$ (crew_t):

```math
y_b\,(d + t) + y_d\, d + y_t\, t \;\le\; 2300\, y_b + 880\, y_d + 1720\, y_t
```

This holds for every plan that satisfies the three rows, because each row's left side is at most
its right side, and multiplying both sides by a number $`\ge 0`$ keeps the direction of
$`\le`$. (Multiplying by a negative number would flip it, which is why the prices must be
$`\ge 0`$.) Now regroup the left side by variable:

```math
(y_b + y_d)\, d + (y_b + y_t)\, t \;\le\; 2300\, y_b + 880\, y_d + 1720\, y_t
```

If the prices are chosen so that $`y_b + y_d \ge 0.66`$ and $`y_b + y_t \ge 0.43`$, then, because
$`d \ge 0`$ and $`t \ge 0`$, the plan's value $`0.66\, d + 0.43\, t`$ is at most the left side,
and so at most the right side. We say the prices **cover** the objective: for every variable, the
prices of the rows it appears in, weighted by its coefficients there, add up to at least its value
per unit. Covering prices turn the right side, $`2300\, y_b + 880\, y_d + 1720\, y_t`$, into a
number no plan can beat: an **upper bound** (lesson 1.1.3 met bounds from an LP relaxation; this
one needs no relaxation and no solver).

In code, a price system either covers the objective and proves a bound, or proves nothing:

```python
def bound(y_budget: float, y_d: float, y_t: float) -> float | None:
    """The upper bound a price system proves, or None if the prices do not cover the objective."""
    nonnegative = min(y_budget, y_d, y_t) >= 0
    covers_d = y_budget + y_d >= v["distribution"]       # the d column: 1 in budget, 1 in crew_d
    covers_t = y_budget + y_t >= v["transmission"]       # the t column: 1 in budget, 1 in crew_t
    if not (nonnegative and covers_d and covers_t):
        return None
    return B * y_budget + D * y_d + T * y_t
```

```text
prices (0.66, 0, 0): bound 1,518.0
prices (0.5, 0.16, 0): bound 1,290.8
prices (0.43, 0.23, 0): bound 1,191.4
prices (0.43, 0, 0): do not cover the objective
```

Read the lines one at a time:

- Pricing the budget at 0.66 and nothing else covers both programs (0.66 ≥ 0.66 and 0.66 ≥ 0.43),
  and proves that no plan is worth more than $`2300 \cdot 0.66 = 1518`$. True, but loose.
- Moving some of the price from the budget onto the distribution crews still covers both, and
  proves a smaller bound, 1,290.8.
- Prices (0.43, 0.23, 0) prove 1,191.4, which is the plan's own value. No plan can be worth more
  than 1,191.4, and our plan is worth exactly that, so the plan is **proven optimal**, without
  trusting the solver.
- Prices (0.43, 0, 0) do not cover distribution ($`0.43 + 0 < 0.66`$). A plan that only buys
  distribution could beat them, so they prove nothing.

Every covering price system gives a valid bound; some are better than others. That raises the
obvious question of how to find the best one.

<!-- practice 1 -->

## The Best Bound Is Itself an LP: the Dual

"Find nonnegative prices that cover the objective and make the bound as small as possible" is a
linear program. Its variables are the prices, its objective is the bound, and its constraints are
the cover conditions, one per primal variable. It is called the **dual LP** of the primal:

```math
\begin{aligned}
\min \;& 2300\, y_b + 880\, y_d + 1720\, y_t \\
\text{s.t. } & y_b + y_d \ge 0.66 && \text{(cover\_d)} \\
& y_b + y_t \ge 0.43 && \text{(cover\_t)} \\
& y_b,\ y_d,\ y_t \ge 0
\end{aligned}
```

Look at how the numbers moved. The primal's right-hand sides (2300, 880, 1720) became the dual's
objective. The primal's objective coefficients (0.66, 0.43) became the dual's right-hand sides.
Each primal **row** became a dual **variable**, and each primal **variable** became a dual
**row**, whose coefficients are that variable's column: $`d`$ appears in budget and in crew_d, so
cover_d is $`y_b + y_d`$. In matrix form (lesson 1.2.1 introduces the notation), the primal
$`\max\, c^\top x`$ subject to $`Ax \le b`$, $`x \ge 0`$ has the dual

```math
\min \; b^\top y \quad \text{s.t.} \quad A^\top y \ge c, \quad y \ge 0,
```

where $`A^\top`$, the **transpose** of $`A`$, is $`A`$ with its rows written as columns. That is
all "taking the dual" means: transpose the data, swap max for min, and turn each $`\le`$ into a
sign condition on a price. The dual of the dual is the primal again.

The dual is an LP like any other, so MathOpt solves it:

```python
def dual() -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="one-year dual")
    y_budget = model.add_variable(lb=0, name="y_budget")
    y_d = model.add_variable(lb=0, name="y_crew_d")
    y_t = model.add_variable(lb=0, name="y_crew_t")
    model.add_linear_constraint(y_budget + y_d >= v["distribution"], name="cover_d")
    model.add_linear_constraint(y_budget + y_t >= v["transmission"], name="cover_t")
    model.minimize(B * y_budget + D * y_d + T * y_t)
    return model, {"budget": y_budget, "crew_d": y_d, "crew_t": y_t}
```

```text
dual:   OPTIMAL, value 1,191.4, prices {'budget': 0.43, 'crew_d': 0.23, 'crew_t': 0.0}
```

The smallest bound is 1,191.4, the primal's optimal value, and the prices that prove it are
(0.43, 0.23, 0), the third line of the table above. That the two values meet is not luck: lesson
2.3.2 states it as **strong duality** and shows when it holds.

## Each Dual Variable Prices One Unit of Its Row's Limit

The dual was built to prove bounds, but its optimal prices answer the finance partner's questions.
Raise the budget by 1 and by 100 and re-solve the primal:

```python
base = mathopt.solve(primal()[0], mathopt.SolverType.GLOP).objective_value()
for extra in (1, 100):
    more = mathopt.solve(primal(B + extra)[0], mathopt.SolverType.GLOP).objective_value()
    print(f"budget + {extra:>3}: value {more:,.2f}, up {more - base:,.2f}")
```

```text
budget +   1: value 1,191.83, up 0.43
budget + 100: value 1,234.40, up 43.00
```

Each extra $1k of budget adds $0.43k of NPV, exactly the budget's dual price. Here is why. The
dual's constraints, cover_d and cover_t, do not contain the primal's right-hand sides; only the
dual's objective does. So when the budget changes from 2300 to 2301, the prices (0.43, 0.23, 0)
are still covering prices, and as long as they stay the best ones, the optimal value is
$`2301 \cdot 0.43 + 880 \cdot 0.23 + 1720 \cdot 0`$: it moves by 0.43 per unit of budget. A dual
price is therefore called a **shadow price**: the change in the optimal objective per unit
increase in a row's right-hand side, other data held fixed. "As long as they stay the best ones"
is a real condition, and lesson 2.3.3 measures how far it reaches.

The prices also make sense on their own:

- **Budget: 0.43.** An extra $1k goes to transmission, the program that still has crews free,
  and returns $0.43k.
- **Distribution crews: 0.23.** Another $1k of distribution crew capacity lets $1k move from
  transmission to distribution, gaining $`0.66 - 0.43 = 0.23`$.
- **Transmission crews: 0.** Transmission has 300 of slack. More transmission crews would sit
  idle, so they are worth nothing to this plan. That answers the second question: no, do not hire
  transmission crews for 2027.

## A Row's Direction Sets the Sign of Its Price

GridCap's wildfire plan adds a rule: at least $300k of vegetation work in 2027, a program that
returns $0.31k per $k and whose crews can do $680k. (The floor is this module's own assumption,
not part of the GridCap data.) The new row points the other way: $`v \ge 300`$. What price does a
$`\ge`$ row get?

Rewrite it as a $`\le`$ row by multiplying by $`-1`$: $`-v \le -300`$. That row takes a price
$`z \ge 0`$ like any other, and contributes $`-z`$ to the vegetation column and $`-300\, z`$ to
the bound. Writing $`y = -z`$ for the original row gives the rule: **in a maximization, a $`\ge`$
row's price is $`\le 0`$.** An equality row is a $`\le`$ row and a $`\ge`$ row at once, so its
price is the difference of a nonnegative and a nonpositive price, and may have either sign: it is
**free**. The whole recipe, for a maximization primal:

| Primal (max) | Dual (min) |
| --- | --- |
| row $`i`$: $`a_i^\top x \le b_i`$ | price $`y_i \ge 0`$ |
| row $`i`$: $`a_i^\top x \ge b_i`$ | price $`y_i \le 0`$ |
| row $`i`$: $`a_i^\top x = b_i`$ | price $`y_i`$ free |
| variable $`x_j \ge 0`$ | dual row $`\sum_i a_{ij}\, y_i \ge c_j`$ |
| variable $`x_j`$ free | dual row $`\sum_i a_{ij}\, y_i = c_j`$ |
| objective coefficients $`c`$, right-hand sides $`b`$ | right-hand sides $`c`$, objective $`\min\, b^\top y`$ |

The price's sign also has a plain meaning. A $`\le`$ row is a limit: raising it can only allow
more plans, so the value cannot fall, and the price is $`\ge 0`$. A $`\ge`$ row is a requirement:
raising it can only remove plans, so the value cannot rise, and the price is $`\le 0`$. An equality
can hurt in either direction.

The table is for a maximization. In a **minimization** every sign in the price column flips: a
$`\le`$ row's price is $`\le 0`$ and a $`\ge`$ row's is $`\ge 0`$. The reason is the same: raising a
limit can only allow more plans, so the lowest cost cannot rise. The OR-Tools guide "Advanced LP
Solving" has the smallest example there is, a primal with one row and its dual, which the guide
writes with the price $`y \le 0`$:

```math
\begin{aligned}
\min \;& -2x_1 - x_2 \\
\text{s.t. }& x_1 + x_2 \le 1 && \text{(c)} \\
& x_1,\ x_2 \ge 0
\end{aligned}
\qquad\qquad
\begin{aligned}
\max \;& y \\
\text{s.t. }& -2 - y \ge 0 && \text{(cover\_x1)} \\
& -1 - y \ge 0 && \text{(cover\_x2)} \\
& y \le 0
\end{aligned}
```

Solved with GLOP through MathOpt, and through `pywraplp`, the older OR-Tools linear solver wrapper
that the guide's first examples use:

```python
def with_mathopt() -> tuple[float, list[float], float, list[float]]:
    model = mathopt.Model(name="dual-example")
    x1 = model.add_variable(lb=0, name="x1")
    x2 = model.add_variable(lb=0, name="x2")
    row = model.add_linear_constraint(x1 + x2 <= 1, name="c")
    model.minimize(-2 * x1 - x2)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise SystemExit(result.termination.reason.name)
    return (result.objective_value(), result.variable_values([x1, x2]),
            result.dual_values(row), result.reduced_costs([x1, x2]))
```

```text
min -2 x1 - x2, x1 + x2 <= 1: value -2 at (x1, x2) = (1, 0)
MathOpt  dual_values  -2   reduced_costs (0, 1)
pywraplp dual_value   -2   reduced_cost  (0, 1)
```

The price is $`-2`$, the guide's $`y = -2`$, and negative as the flipped rule says: one more unit of
the limit lets $`x_1`$ grow by 1 and lowers the cost by 2. The two **reduced costs** (lesson 2.3.2
defines them; here, the objective coefficient minus the price of the row the variable uses) are the
left sides of the guide's two dual rows at $`y = -2`$: $`-2 - (-2) = 0`$ for $`x_1`$, which the plan
uses, and $`-1 - (-2) = 1`$ for $`x_2`$, which it does not. Both OR-Tools interfaces report the same
numbers with the same signs.

The recipe is mechanical, so code can apply it to any MathOpt model. `dualize` reads each row's
bounds to choose its price's sign, and each variable's column to write its cover row
(`column_nonzeros(var)` lists the rows a variable appears in, and `row.get_coefficient(var)` its
coefficient there):

```python
for row in primal.linear_constraints():
    lo, hi = row.lower_bound, row.upper_bound
    if lo == hi:                                    # == row: the price may have either sign
        price[row.name] = dual.add_variable(lb=-math.inf, ub=math.inf, name=f"y_{row.name}")
        rhs[row.name] = hi
    elif lo == -math.inf:                           # <= row: the price is >= 0
        price[row.name] = dual.add_variable(lb=0, name=f"y_{row.name}")
        rhs[row.name] = hi
    elif hi == math.inf:                            # >= row: the price is <= 0
        price[row.name] = dual.add_variable(lb=-math.inf, ub=0, name=f"y_{row.name}")
        rhs[row.name] = lo
```

```python
for var in primal.variables():
    if var.lower_bound != 0 or var.upper_bound != math.inf:
        raise ValueError(f"{var.name}: write every bound other than >= 0 as a row")
    column = sum(row.get_coefficient(var) * price[row.name] for row in primal.column_nonzeros(var))
    dual.add_linear_constraint(column >= primal.objective.get_linear_coefficient(var), name=f"cover_{var.name}")
dual.minimize(sum(rhs[name] * y for name, y in price.items()))
```

MathOpt stores $`d + t \le 2300`$ as a row with lower bound $`-\infty`$ and upper bound 2300, and
$`v \ge 300`$ as lower bound 300 and upper bound $`+\infty`$, which is how `dualize` tells the
directions apart. A row bounded on both sides, such as $`100 \le v \le 300`$, is two rows for the
recipe, so `dualize` refuses it; so does a variable with a bound other than $`\ge 0`$, which you
would write as a row first.

Run on the one-year model with vegetation and its floor, the dual's prices sit next to the prices
MathOpt itself reports for the primal, through `result.dual_values(row)`:

```text
primal: value 1,155.4, plan {'d': 880.0, 't': 1120.0, 'v': 300.0}
dual:   value 1,155.4
row         dual LP price  MathOpt dual_values
budget               0.43                 0.43
crew_d               0.23                 0.23
crew_t                0.0                  0.0
crew_v                0.0                  0.0
veg_floor           -0.12                -0.12
```

The floor's price is $`-0.12`$: each extra $1k of required vegetation work costs $0.12k of NPV,
because that $1k comes out of transmission ($`0.43 - 0.31 = 0.12`$). MathOpt's `dual_values` are
the same numbers, so from now on we read prices from the solver instead of building the dual.
Building it once by hand is what makes those numbers readable: each is a row's price, with a sign
fixed by the row's direction. Lesson 2.3.3 reads the solver's prices on the full GridCap model.

<!-- practice 2 -->

## Summary

- **Any nonnegative prices on the rows give an upper bound.** Multiply each $`\le`$ row by a price
  $`\ge 0`$ and add; if the prices cover every variable's objective coefficient, the combined right
  side bounds every plan's value.
- **The best bound is itself an LP: the dual.** Primal rows become dual variables, primal variables
  become dual rows, right-hand sides and objective coefficients swap places, and max becomes min.
- **Each dual variable prices one unit of its row's limit.** At the optimum, the dual price of a row
  is its shadow price: the change in the best value per unit increase of the row's right-hand side.
  A row with slack has price 0.
- **A row's direction sets the sign of its price.** In a maximization, $`\le`$ rows get prices
  $`\ge 0`$, $`\ge`$ rows get prices $`\le 0`$, and equality rows get free prices.

## Reference

| Primal (max) | Dual (min) |
| --- | --- |
| $`\max\, c^\top x`$, $`Ax \le b`$, $`x \ge 0`$ | $`\min\, b^\top y`$, $`A^\top y \ge c`$, $`y \ge 0`$ |
| $`\le`$ row | price $`\ge 0`$ |
| $`\ge`$ row | price $`\le 0`$ |
| $`=`$ row | price free |
| variable $`\ge 0`$ | cover row $`\ge c_j`$ |
| variable free | cover row $`= c_j`$ |
| (primal min instead) | every price sign flips: $`\le`$ row $`\le 0`$, $`\ge`$ row $`\ge 0`$ |

| Term | Meaning |
| --- | --- |
| price (dual variable) | a number attached to one primal row |
| cover | for every variable, its column times the prices is at least its objective coefficient |
| bound | $`b^\top y`$ for covering prices: no plan's value exceeds it |
| shadow price | an optimal dual price: the change in the optimal value per unit of a row's right-hand side |
| `result.dual_values(row)` | MathOpt's shadow price for `row` |

**Further reading:** [Advanced LP Solving (OR-Tools)](https://developers.google.com/optimization/lp/lp_advanced) (the primal-dual pair solved above, and the duality gap a solver checks before it reports an optimum); [MathOpt `solution.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solution.py) (the docstring of `DualSolution`: MathOpt's convention, written for $`\min c^\top x`$, $`Ax \ge b`$, $`x \ge 0`$, with prices $`y \ge 0`$ and reduced costs $`r = c - A^\top y \ge 0`$); [MO-book 2.6, Dual of the BIM production problem](https://mobook.github.io/MO-book/notebooks/02/06-bim-dual.html) (the dual derived from nonnegative multipliers on each row, as here, on a production model, and solved both directly and from the primal's dual values in Pyomo).

## Challenges

1. Price the one-year model's rows at (0.6, 0.06, 0.17). Do they cover the objective? What bound do
   they prove, and how far is it from 1,191.4?
2. Write the dual of the one-year model by hand after adding $`d \ge 200`$ (a distribution
   minimum). Which price must be $`\le 0`$, and what do you predict it is at the optimum?
3. Change the transmission crews $`T`$ from 1,720 to 1,400. Predict which prices change, then
   check with the program.

## Design Note: Why Learn the Dual When the Solver Reports Prices

A solver hands you `dual_values` for free, so building the dual by hand looks like a detour. It is
the only way to know what those numbers mean: which sign to expect, which unit they are in, and why
a row with slack has price 0. Without that, a negative price on a floor looks like a bug and a zero
price on a crew limit looks like missing data. The second reason is that the dual is a tool in its
own right: bounds from prices are how MILP solvers prune their search (section 3), and later
decomposition methods (section 11) are built on them.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**one_year.py.** Builds the one-year model, checks four price systems, solves the dual and
re-solves with a larger budget (*The Model* to *Each Dual Variable Prices One Unit of Its Row's
Limit*). *Try:* Add the price system (0.6, 0.06, 0.17) to the loop and predict, before running,
whether it proves a bound.

**dualize.py.** The recipe as code: the dual of any maximization LP whose variables are all
$`\ge 0`$ (*A Row's Direction Sets the Sign of Its Price*). It prints nothing; the next program
uses it.

**min_prices.py.** Adapted from the primal-dual example of the OR-Tools guide "Advanced LP
Solving": the minimization's price and reduced costs from MathOpt and from `pywraplp` (*A Row's
Direction Sets the Sign of Its Price*). *Try:* Change the row to $`x_1 + x_2 \ge 1`$ and predict the
status and the price before you run it.

**sign_rules.py.** The one-year model with vegetation and its floor, its dual from `dualize`, and
MathOpt's `dual_values` beside the dual's prices (*A Row's Direction Sets the Sign of Its Price*).
*Try:* Raise the floor from 300 to 700, above what the vegetation crews can do, and predict what
the solve reports.

- Program: [one_year.py](src/one_year.py)
- Library: [dualize.py](src/dualize.py)
- Program: [min_prices.py](src/min_prices.py)
- Program: [sign_rules.py](src/sign_rules.py)
- Library: [budget_lp.py](src/budget_lp.py)
