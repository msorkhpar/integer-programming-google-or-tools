# 2.3.4 Explaining a Dual Value to a Finance Partner

GridCap's finance partner has the LP's output in front of her and three questions for tomorrow's
rate-case meeting. "The model says the 2028 budget is worth 0.4019. If the regulator gives us
$6M more for 2028, is that $2.4M more NPV?" "The vegetation floor shows −0.12. Is the wildfire
commitment costing us $108k?" "And distribution crews show 0.215: should we pay a contractor
$60k a month for one more crew?" The numbers are right; each question reads one of them wrongly.
This lesson turns a dual value into a sentence a partner can act on and check, in four rules.
(GridCap is fictional; its numbers come from the course's generator.)

The model is the GridCap budget LP of lesson 2.3.2 (its formulation is in "The Model" there, and
repeated in lesson 2.3.3's reference). The prices and ranges below are the ones lesson 2.3.3 read
from MathOpt and HiGHS.

## Say a Price's Unit, Its Direction and Its Range

A shadow price is three facts, and a partner needs all three:

1. **The unit**: objective units per unit of the row. The cash row is in $k of budget and the
   objective in $k of NPV, so 0.4019 is "$0.40 of NPV per extra dollar of 2028 budget".
2. **The direction**: what happens when the limit goes *up*, other data fixed. For a budget, more
   value; for a requirement such as the floor, less.
3. **The range**: how far the slope holds. For the 2028 budget, from $2.98M to $8.14M (lesson
   2.3.3), that is from $0.3M below today's $3.28M to $4.86M above it.

So the sentence for the first number is: *"Each extra $1 of 2028 budget adds about $0.40 of NPV,
for increases up to $4.86M; beyond that, each dollar adds less, and we re-solve to say how much."*
It states the unit, the direction and the range, and the partner can check it.

The unit is the part most often lost. The crew rows are written in $k of crew capacity, so their
prices are per $k of capacity. A partner buys crew-months. Multiply by the $k of work one crew-month
delivers ($`k_g`$ in the model) to convert:

```python
for y in tiny.years:
    for g in ("distribution", "vegetation"):
        row = lp.crew[g, y]
        price = result.dual_values(row)
        print(f"{row.name:24} {clean(price):>12} {k[g]:>18} {clean(price * k[g], 1):>22}")
```

```text
crew row                 price per $k  $k per crew-month  value of a crew-month
crew_distribution_2027           0.23                440                  101.2
crew_vegetation_2027              0.0                170                    0.0
crew_distribution_2028          0.215                440                   94.6
crew_vegetation_2028           0.0079                170                    1.3
crew_distribution_2029         0.2009                440                   88.4
crew_vegetation_2029           0.0152                170                    2.6
```

One more distribution crew-month in 2028 adds $94.6k of NPV to the plan. That answers the third
question: a contractor at $60k a month is worth hiring, *if* the $60k does not come out of the same
2028 capital budget (if it does, it also uses 2028 cash, priced 0.4019 per $k). And it is worth
hiring for one month at least; for several, check the crew row's range first, because the price
holds only as far as its range reaches.

## A Price Answers a Small Change; a Large One Needs a Re-Solve

The first question multiplies the price by $6M. The program does the same, for a small and a large
increase, and compares each with a re-solve:

```python
for extra in (500, 6000):
    lp_more = build(tiny, budget={**tiny.budget, 2028: tiny.budget[2028] + extra})
    actual = solve_glop(lp_more.model).objective_value() - base
    print(f"2028 budget +{extra:,}: price x amount says +{price_2028 * extra:,.1f}, re-solve gives +{actual:,.1f}")
```

```text
plan value 4,109.6; 2028 cash price 0.4019
2028 budget +500: price x amount says +200.9, re-solve gives +200.9
2028 budget +6,000: price x amount says +2,411.2, re-solve gives +2,381.2
```

$500k is inside the range, and price × amount is exact. $6M is not: the range ends $4.86M above
today's budget. The first $4,860k earn 0.4019 each; past 8,140 the money is carried into 2029 and
earns that year's 0.3756 (lesson 2.3.3's sweep). Adding the two segments,
$`4860 \cdot 0.4019 + 1140 \cdot 0.3756 \approx 1953.2 + 428.2 = 2381.4`$, gives the re-solve's
2,381.2 up to the rounding of the printed prices. Price × amount overstates the gain by $30k. In a
maximization it can only overstate: past each breakpoint the slope falls, never rises, as the
sweep of lesson 2.3.3 showed (0.4097, then 0.4019, then 0.3756, then 0).

**Why the price can only fall.** Write $`V(b)`$ for the best value when the row's right-hand side
is $`b`$, everything else fixed. Take two right-hand sides $`b_1 < b_2`$ and a best plan at each,
$`x_1`$ and $`x_2`$. Now look at the halfway point $`\tfrac12(b_1 + b_2)`$ and the halfway plan
$`\tfrac12(x_1 + x_2)`$:

- the halfway plan is allowed there: every row is a sum of numbers times variables, so averaging
  two plans averages each row's left side. The changed row's left side is at most
  $`\tfrac12(b_1 + b_2)`$, and every other row still holds, since both plans met it;
- its value is $`\tfrac12(V(b_1) + V(b_2))`$, because the objective is linear too.

The best plan at the halfway point is at least as good as this one, so
$`V(\tfrac12(b_1 + b_2)) \ge \tfrac12(V(b_1) + V(b_2))`$: the value curve never sits below the
straight line (the **chord**) between two of its points. A curve with that property is called
**concave**. Now suppose a segment of the curve were steeper than the one before it. Take one point
on each segment, on either side of the breakpoint between them: the curve bends upward there, so
the chord between the two points passes above the breakpoint, and the curve sits below its chord,
which cannot happen. So each segment's slope, the shadow price, is at most the previous one's. In a
minimization the same argument with the inequality reversed shows the opposite: the value curve is
convex, and prices can only rise.

So the answer to the first question is: *"About $2.38M, not $2.41M: the first $4.86M earn $0.40
per dollar, and the rest only $0.38, because 2028's transmission crews are full and the money has
to wait for 2029."* For any change that leaves the range, or for two changes at once, the honest
tool is a re-solve.

<!-- practice 1 -->

## A Negative Price Is the Marginal Cost of a Commitment

The floor's price is $`-0.12`$ per $k. The second question multiplies it by the whole floor,
$900k, and calls $108k the cost of the commitment. The program compares that with what the
commitment really costs, the value gained by dropping the floor and re-solving:

```python
floor_price = result.dual_values(lp.floor)
without = solve_glop(build(tiny, floor=None).model).objective_value()
```

```text
vegetation floor of 900: price -0.12 x 900 says -108.0; dropping the floor gives +100.2
```

The floor costs $100.2k, not $108k. The price is the cost of the **last** $1k of floor: that $1k
has to be done in 2027, where it displaces transmission worth 0.43 and earns 0.31. The first
$680k of the floor are cheaper, because they go into 2028 and 2029, where the transmission they
displace is worth less (it is discounted) and the floor's range from lesson 2.3.3 ends at 680. A
price is a **marginal** value (the effect of one more unit), never an **average** over the whole
amount. Multiplying a marginal value by a whole quantity is the commonest misreading of a dual
value.

The sentence for the partner: *"The wildfire floor costs about $100k of NPV over the plan. Each
extra $1k of required vegetation work, up to $1.36M of floor, costs another $0.12k; each $1k less
saves $0.12k, down to a $680k floor."*

The negative price also explains two small positive prices that would otherwise look odd: the
vegetation crews in 2028 and 2029 are worth $1.3k and $2.6k per crew-month. Vegetation work is the
least valuable program, so its crews matter only because the floor forces the work. One more crew
in 2029 lets $170k of the floor move out of 2027, where it costs the most. Without the floor,
vegetation is idle (lesson 2.3.3), its crew rows have slack, and complementary slackness sets their
prices to 0.

<!-- practice 2 -->

## A Yes/No Model Has No Shadow Prices, Only Re-Solves

The partner's last question: "What is the shadow price of the budget in the *project selection*
model?" That is the tiny portfolio's selection model of lesson 1.1.3: binary $`x_i \in \{0,1\}`$
per project, a budget row, must-do, parent and alternative rows. Ask MathOpt for the budget row's
dual value after solving it as a MILP:

```python
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print(f"MILP {result.termination.reason.name}, value {result.objective_value():,.0f}")
try:
    result.dual_values(row)
except ValueError as error:
    print("dual_values:", error)
```

```text
MILP OPTIMAL, value 3,627
dual_values: Best solution does not have an associated dual feasible solution.
```

There is none. Duality, as these four lessons built it, needs the plans to form a region where
small changes are possible; with yes/no decisions a project is in or out, and the value does not
have a slope. The program shows what it has instead, solving the MILP and its LP relaxation (the
same model with $`0 \le x_i \le 1`$) at budgets from 7,000 to 7,800:

```python
for budget in range(7000, 7801, 100):
    milp = mathopt.solve(selection(budget, integer=True)[0], mathopt.SolverType.HIGHS)
    lp_model, lp_row = selection(budget, integer=False)
    lp = mathopt.solve(lp_model, mathopt.SolverType.GLOP)
```

```text
budget MILP value  LP value LP price
 7,000      3,504   3,577.9   0.4929
 7,100      3,627   3,627.2   0.4929
 7,200      3,627   3,676.5   0.4929
 7,300      3,627   3,725.8   0.4929
 7,400      3,627   3,775.1   0.4929
 7,500      3,641   3,824.4   0.4929
 7,600      3,641   3,873.7   0.4929
 7,700      3,764   3,922.9   0.4929
 7,800      3,764   3,972.2   0.4929
```

The MILP's value moves in steps: +123 from 7,000 to 7,100, nothing for the next $300k, +14, then
+123 again. "Per $1k of budget" has no fixed answer: the next $100k is worth $123k at one budget and
$0 at the next. The LP relaxation has a smooth price, 0.4929, but it prices fractions of projects
that the utility cannot build, so it is not the answer either.

For a model with yes/no decisions, answer a "what is X worth" question with **scenarios**: re-solve
at the values the partner cares about and report the differences, as the table does. Section 9
treats sensitivity for integer programs, and section 12 builds the scenario workflow. A dual value
is an LP tool; using it on a MILP is a mistake.

## Summary

- **Say a price's unit, its direction and its range.** And convert the unit to the partner's: a
  price per $k of crew capacity times $k per crew-month is a price per crew-month.
- **A price answers a small change; a large one needs a re-solve.** Inside its range, price ×
  amount is exact; beyond it, in a maximization, it overstates the gain.
- **A negative price is the marginal cost of a commitment.** It prices the last unit of a
  requirement; the commitment's total cost comes from re-solving without it.
- **A yes/no model has no shadow prices, only re-solves.** MathOpt raised an error when asked for
  the MILP's dual values; report scenarios instead.

## Reference

| Partner's question | What to answer with |
| --- | --- |
| "What is one more unit of this limit worth?" | the shadow price, with its unit, direction and range |
| "What is a change of this size worth?" | price × amount if inside the range; otherwise a re-solve |
| "What does this commitment cost in total?" | value without it minus value with it (re-solve) |
| "What would it take for this to be funded?" | the reduced cost: the coefficient must pass $`c_j - d_j`$ |
| "What is the budget worth in the selection model?" | scenario re-solves; a MILP has no dual values |

| Misreading | Correction |
| --- | --- |
| price × a large change | only inside the range; past it, re-solve |
| price × the whole commitment | the price is marginal; the total comes from a re-solve |
| price per $k read as per crew-month | multiply by the $k one crew-month delivers |
| a dual value on a MILP | none exists; use scenarios |

**Further reading:** [MathOpt `result.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (the docstring of `dual_values`: it raises `ValueError` when the best solution has no dual feasible solution, the error the MILP run printed); [MathOpt sample advanced_linear_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py) (checks `has_dual_feasible_solution()` before it reads any price, the guard a report on a model of unknown type needs); [MO-book 2.6, Dual of the BIM production problem](https://mobook.github.io/MO-book/notebooks/02/06-bim-dual.html) (each dual variable as the multiplier of one resource row, the reading this lesson turns into a sentence for finance).

## Challenges

1. Write the partner's sentence for the 2029 cash price, 0.3756, with its range of 1,660 to 3,810
   from lesson 2.3.3.
2. The contractor's $60k per crew-month is paid out of the 2028 capital budget. Is one 2028
   distribution crew-month still worth hiring? Use two prices and say what you assume.
3. The regulator offers +$1M in 2027 or +$1M in 2029, not both. Predict from the prices and ranges
   which is worth more, then check by re-solving.

## Design Note: Report Re-Solves, Explain With Prices

A deck for a rate-case meeting should show scenario values computed by re-solving, because they are
exact and survive any change in the model. The prices are for the conversation: they say why a
scenario came out as it did ("2028 transmission is the marginal use of money") and which limit to
ask about next (the one with the largest price per dollar of relief). Use each for what it is good
at, and never let a price × amount product stand in for a scenario the meeting will rely on.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**finance_answers.py.** Each of the partner's questions answered with a price and checked with a
re-solve: a small and a large budget change, the floor's total cost, and crew prices per crew-month
(*the first three sections*). *Try:* Change the large increase from 6,000 to 4,000 and predict
whether price × amount matches the re-solve.

**milp_has_no_prices.py.** The selection model as a MILP, its missing dual values, and its value
against its LP relaxation's at nine budgets (*A Yes/No Model Has No Shadow Prices, Only
Re-Solves*). *Try:* Extend the sweep to 8,500 and predict whether the MILP's steps get smaller.

- Program: [finance_answers.py](src/finance_answers.py)
- Program: [milp_has_no_prices.py](src/milp_has_no_prices.py)
- Library: [budget_lp.py](src/budget_lp.py)
