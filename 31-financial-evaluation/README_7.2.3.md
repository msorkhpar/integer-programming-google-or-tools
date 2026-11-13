# 7.2.3 Annuities, Lifecycle Cost, Equivalent Annual Cost

Asset A006, a Valley substation transformer, has two projects in GridCap tiny: P006 replaces it for
$1,970k and P007 repairs it for $290k, and lesson 6.5.3 makes them mutually exclusive. The repair is
far cheaper today. But a repaired transformer lasts ten more years and keeps costing money to run
and patch; a new one lasts forty. Comparing $290k with $1,970k compares two different things. This
lesson builds the tools that make them comparable: the present value of a level stream of payments
(an annuity), the **lifecycle cost** of owning an asset, and the **equivalent annual cost** that
puts options with different lives on the same yearly footing. Four rules, with
numpy-financial checking each number.

GridCap is a fictional utility's portfolio. It stores no running costs or asset lives, so the O&M
costs, lives and overhaul in this lesson are invented for it; the capex of the two options are
P006's and P007's.

## An Annuity's Present Value Has a Closed Form

An **annuity** is the same payment $`A`$ at the end of each of $`n`$ years: a maintenance contract, a
lease, a yearly saving. Its present value is a sum of $`n`$ discounted payments,

```math
\text{PV} = \sum_{t=1}^{n} \frac{A}{(1 + r)^t}
```

and that sum has a closed form. Write $`v = 1/(1 + r)`$. The sum is $`A(v + v^2 + \dots + v^n)`$, a
geometric series. Multiply it by $`v`$ and subtract: everything cancels except the first and the
last term, $`S - vS = A(v - v^{n+1})`$, so $`S = A v (1 - v^n)/(1 - v)`$. Since
$`v/(1 - v) = 1/r`$,

```math
\text{PV} = A \cdot \underbrace{\frac{1 - (1 + r)^{-n}}{r}}_{\text{annuity factor } a(r, n)}
```

The **annuity factor** $`a(r, n)`$ is the present value of $1 a year for $`n`$ years. At a zero rate
it is just $`n`$ (no discounting), which the code handles separately because the formula would
divide by zero:

```python
def annuity_factor(rate: float, years: int) -> float:
    """Present value of $1 paid at the end of each of the next `years` years."""
    if rate == 0:
        return float(years)
    return (1 - (1 + rate) ** -years) / rate
```

For $100k a year for 20 years at 7%, the loop, the closed form and numpy-financial agree:

```text
sum of 20 discounted payments         1059.40
closed form A(1 - (1+r)^-n)/r         1059.40
npf.pv(0.07, 20, -100)                1059.40
payments at the start of each year    1133.56
closed form times 1.07                1133.56
forever (perpetuity) A / r            1428.57
npf.pmt(0.07, 20, 1000)                -94.39
1000 / annuity factor                   94.39
```

Twenty payments of $100k, $2,000k in total, are worth $1,059k today. Three variations matter:

- **Payments at the start of each year** (an *annuity due*) are each one year less discounted, so
  the PV is the ordinary annuity's times $`(1 + r)`$. numpy-financial's `when='begin'` does this.
- **A payment forever** (a *perpetuity*) has $`(1 + r)^{-n} \to 0`$, so its PV is $`A/r`$: $1,429k.
  Twenty years already capture 74% of forever at 7%, which is why distant years matter so little.
- **The payment from the PV** inverts the factor: $`A = \text{PV} / a(r, n)`$. `npf.pmt` returns it,
  and the next two rules lean on it.

numpy-financial's functions follow a cash-sign convention: money paid and money received have
opposite signs. `npf.pv(0.07, 20, -100)` reads "paying 100 a year is worth receiving 1,059.40 now",
and `npf.pmt(0.07, 20, 1000)` returns −94.39 because receiving 1,000 now is repaid by paying 94.39
a year. When you compare with your own functions, which use positive costs, flip the sign.

## Lifecycle Cost Is Every Cost of Owning the Asset, Discounted to One Date

The price of an asset is only its first cost. Over its life it also has running costs (operations
and maintenance, **O&M**: inspections, oil tests, repairs after faults), occasional large one-off
costs (an overhaul), and sometimes a value at the end (salvage). The **lifecycle cost** (LCC) is
all of them, discounted to the date of the decision:

```math
\text{LCC} = \text{capex} + \text{O\&M} \cdot a(r, L) + \sum_{j} \frac{\text{one-off}_j}{(1 + r)^{j}}
- \frac{\text{salvage}}{(1 + r)^{L}}
```

with $`L`$ the life in years and $`j`$ the year of life of each one-off. Two options for A006, with
invented running costs, in 2027 dollars at the real rate of 7%:

```python
options = {
    # name: (capex now, O&M each year, life in years, {year of life: one-off cost})
    "replace": (1_970, 25, 40, {20: 300}),
    "repair": (290, 150, 10, {}),
}
```

The new transformer costs $25k a year to run and needs a $300k mid-life overhaul in year 20. The
repaired one costs $150k a year, because an old unit needs constant attention, and lasts ten years.

```text
option   life  capex  PV O&M  PV one-off  lifecycle  EAC     npf.pmt
replace    40   1970   333.3        77.5     2380.8   178.6   178.6
repair     10    290  1053.5         0.0     1343.5   191.3   191.3
```

Read the lifecycle column first. Running costs change the picture a lot: the repair's $290k becomes
$1,343k once ten years of O&M are counted, nearly five times its price. The replacement's 40 years
of O&M add only $333k, because most of those years are far away, and its overhaul, $300k in year 20,
is worth $77.5k today. On lifecycle cost the repair still looks better: $1,343k against $2,381k.

That comparison is wrong, and it is the most common mistake with lifecycle costs. The repair's
$1,343k buys ten years of service; the replacement's $2,381k buys forty. The two numbers are not
costs of the same thing.

<!-- practice 1 -->

## Equivalent Annual Cost Compares Options With Different Lives

Turn each lifecycle cost into a level yearly payment over its own life, the payment whose annuity
has the same present value. That is the **equivalent annual cost** (EAC):

```math
\text{EAC} = \frac{\text{LCC}}{a(r, L)} = \text{LCC} \cdot \frac{r}{1 - (1 + r)^{-L}}
```

It answers "what does a year of service from this option cost?", which is comparable across lives.

```python
def equivalent_annual_cost(present_cost: float, rate: float, years: int) -> float:
    """The level end-of-year payment over `years` years with the same present value."""
    return present_cost / annuity_factor(rate, years)
```

In the table above, the replacement costs $178.6k per year of service and the repair $191.3k. The
ranking has reversed: replacing is cheaper, by $12.7k a year, even though its lifecycle cost is
$1,037k higher. `npf.pmt` gives the same EAC, which is a useful check, since EAC is exactly the
payment of a loan of LCC over the asset's life.

Do not shortcut EAC to $`\text{LCC}/L`$. Dividing by the life ignores the time value of the money
spent up front: for the replacement it gives $2,380.8k / 40 = $59.5k a year, a third of the real
figure, because it spreads the $1,970k of capex over forty years as if that money cost nothing to
tie up. The divisor is the annuity factor, not the number of years (they are equal only at a zero
rate).

<!-- practice 2 -->

## Equivalent Annual Cost Assumes the Option Is Repeated Like for Like

Why is EAC the right comparison? Picture forty years of service from A006. One replacement provides
them. Four repairs in a row provide them too, if each repair costs what the first did and lasts as
long. Value both plans over the same forty years:

```python
repair_lcc = 290 + 150 * annuity_factor(rate, 10)
chain = present_value({0: repair_lcc, 10: repair_lcc, 20: repair_lcc, 30: repair_lcc}, rate, 0)
```

```text
over 40 years: four repairs 2550.2, one replacement 2380.8
```

On a common horizon the replacement is cheaper, the same verdict as EAC, and this is no
coincidence: when an option repeats like for like, its EAC is the level yearly cost of the whole
chain, so comparing EACs is comparing chains over any common horizon. EAC is the shortcut that
saves you from building the chains.

The shortcut carries the chain's assumption, and that is what a planner should hear with the
number: each repair is followed by another like it, at the same real cost. In reality, an old
transformer cannot be repaired four times in a row, and the second repair would be on an even older
unit. When the assumption fails, build the actual sequence of decisions over a common horizon and
compare present values directly. That is what a multi-period model does: lesson 6.5.3 makes repair
and replace alternatives inside one plan, and lesson 6.6.4 values partial renewals with a lifecycle
value curve.

## Summary

- **An annuity's present value has a closed form.** $`\text{PV} = A \cdot a(r, n)`$ with
  $`a(r, n) = (1 - (1 + r)^{-n})/r`$; at zero rate, $`a = n`$; forever, $`A/r`$.
- **Lifecycle cost is every cost of owning the asset, discounted to one date.** Capex, O&M,
  one-offs, less discounted salvage. LCCs of options with different lives are not comparable.
- **Equivalent annual cost compares options with different lives.** $`\text{EAC} = \text{LCC}/a(r, L)`$,
  never $`\text{LCC}/L`$; on A006 it reverses the LCC ranking.
- **Equivalent annual cost assumes the option is repeated like for like.** When it is not, compare
  present values over a common horizon.

## Reference

| Quantity | Formula | numpy-financial (sign flipped) |
| --- | --- | --- |
| annuity factor | $`a(r, n) = (1 - (1 + r)^{-n})/r`$ | `npf.pv(r, n, -1)` |
| PV of $`A`$ a year, end of year | $`A \cdot a(r, n)`$ | `npf.pv(r, n, -A)` |
| PV of $`A`$ a year, start of year | $`A \cdot a(r, n)(1 + r)`$ | `npf.pv(r, n, -A, when='begin')` |
| perpetuity | $`A/r`$ | — |
| lifecycle cost | capex + O&M $`\cdot\, a(r, L)`$ + PV(one-offs) − PV(salvage) | — |
| equivalent annual cost | $`\text{LCC}/a(r, L)`$ | `-npf.pmt(r, L, LCC)` |

**Further reading:** [numpy-financial: `pmt`](https://numpy.org/numpy-financial/latest/_api_stubs/numpy_financial.pmt.html)
(the payment equation, the `when` argument and the sign convention); [numpy-financial
API](https://numpy.org/numpy-financial/latest/api.html) (`pv`, `fv` and the rest of the family).

## Challenges

1. Give the repaired transformer a salvage value of $40k at the end of its ten years. Does the
   ranking change?
2. At what O&M cost per year would the repair and the replacement have the same EAC?
3. The replacement's overhaul slips from year 20 to year 25. Predict the direction of the change in
   its EAC before computing.

## Design Note: EAC Outside the Model, Present Values Inside It

EAC is a screening tool: it ranks options that would each be repeated forever, one asset at a time.
A capital-planning MILP does not need it. The model chooses among projects whose cash flows it
already sees year by year over a fixed horizon, so it compares present values, and the "repeat like
for like" assumption never enters. Use EAC to explain a repair-or-replace choice to a planner, and
to sanity-check an alternative group's coefficients; put present values in the objective.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**annuities.py.** Values a 20-year annuity by a loop, by the closed form and with numpy-financial,
then the annuity due, the perpetuity and the payment back (*An Annuity's Present Value Has a Closed
Form*). *Try:* Set the rate to 0.0001. Predict the annuity's PV before running.

- Program: [annuities.py](src/annuities.py)

**lifecycle.py.** Lifecycle cost and EAC of replacing and repairing A006, and the four-repair chain
(*the last three sections*). *Try:* Shorten the replacement's life to 25 years. Predict whether
replacing still wins on EAC.

- Program: [lifecycle.py](src/lifecycle.py)
