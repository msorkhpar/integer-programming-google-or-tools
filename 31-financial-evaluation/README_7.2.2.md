# 7.2.2 Escalation; Real vs. Nominal Dollars

GridCap's cost profiles are price quotes. P022, a Valley tower set repair, is listed at $360k, $720k
and $1,470k for its three years of work, priced when the estimate was made, in 2027. If the work
starts in 2029, the crews and steel will be bought at 2029–2031 prices, and prices rise. Finance
calls that rise **escalation**. Once costs escalate, the discount rate of lesson 7.2.1 has to be
the right *kind* of rate too, or the escalation is counted twice or not at all. This lesson gives
the rule for escalating a quote, the rule that pairs dollars with rates, the one case where
escalation changes a real model, and a check for borrowed formulas, which two common ones fail.

GridCap is a fictional utility's portfolio, generated for this course. The escalation and inflation
rates in this lesson are assumptions made for it.

## Escalation Turns a Price Quoted in One Year Into the Price Paid in Another

A cost estimate is quoted in the prices of one year, its **price base year** $`b`$. If prices for
that kind of work rise by $`e`$ a year, an amount $`c`$ quoted in year $`b`$ costs, when paid in
year $`y`$,

```math
c^{\text{nom}}_y = c \,(1 + e)^{\,y - b}
```

The exponent counts the years **from the price base year to the year of payment**. It is the
compounding of lesson 7.2.1, applied to prices instead of money in an account. Amounts at the prices
of the year they are paid in are **nominal** (or "then-year") dollars; amounts at the prices of one
fixed base year are **real** (or "constant") dollars. A cost profile straight from an estimate is
real: every entry is in base-year prices.

```python
p = generate("small").project("P022")
price_year, e = 2027, 0.03
print(f"{p.project_id} cost profile in {price_year} dollars: {p.cost_profile}, total {p.capex:,}")
for start in p.starts():
    nominal = {start + k: escalate(c, e, start + k - price_year) for k, c in enumerate(p.cost_profile)}
```

```text
P022 cost profile in 2027 dollars: (360, 720, 1470), total 2,550
start 2027: 2027: 360.0, 2028: 741.6, 2029: 1,559.5  total 2,661.1
start 2028: 2028: 370.8, 2029: 763.8, 2030: 1,606.3  total 2,741.0
start 2029: 2029: 381.9, 2030: 786.8, 2031: 1,654.5  total 2,823.2
```

At 3% a year, the same work costs $2,661k if it starts in 2027 and $2,823k if it starts in 2029.
Every year of delay adds escalation to every year of work, because each payment moves one year
further from 2027. The first year of a 2027 start is paid in the price base year, so it is not
escalated at all ($360.0k).

The exponent is the part people get wrong. A tempting shortcut escalates the $`k`$-th year of work
by $`(1 + e)^k`$, counting from the project's own start, as if every project's estimate were priced
in the year it begins. It gives the same answer for a project that starts in the price base year,
and the wrong answer for every other start:

```python
for start in p.starts():
    from_base = {start + k: escalate(c, e, start + k - price_year) for k, c in enumerate(p.cost_profile)}
    from_start = {start + k: escalate(c, e, k) for k, c in enumerate(p.cost_profile)}
```

```text
start  nominal from 2027  nominal from start   PV from 2027  PV from start
2027            2,661.1             2,661.1        2,415.2        2,415.2
2028            2,741.0             2,661.1        2,324.9        2,257.2
2029            2,823.2             2,661.1        2,238.0        2,109.6
```

Counted from the start, P022 costs $2,661k whenever it starts: two years of delay come free of
price rises. Both present-value columns discount to the start of 2027 at 7% in the same way, so the
whole gap ($128k for a 2029 start) is escalation the shortcut forgot. In a start-year model that
gap makes later starts look cheaper than they are, so the solver defers work for a saving that does
not exist.

**This course measures escalation from the price base year, never from the project's start.** For
GridCap that base year is 2027, the year the estimates were priced and also the plan's valuation
date. To spot the shortcut in someone else's formula, find the exponent on $`(1 + e)`$ and ask
whether it changes when the start year changes. If it depends only on the year of work
($`k`$ or $`\tau`$ counted from the start), it is the shortcut.

<!-- practice 1 -->

## Real Dollars Pair With a Real Rate, Nominal Dollars With a Nominal Rate

General **inflation** is the rise in prices across the whole economy, at rate $`i`$ a year. A discount
rate can be quoted two ways. A **nominal** rate $`n`$ is what money actually earns or costs, in
then-year dollars: a loan at 6.6% is a nominal rate. A **real** rate $`r`$ is what money earns in
purchasing power, after inflation. The two are tied by the **Fisher relation**:

```math
(1 + n) = (1 + r)(1 + i) \qquad\Longleftrightarrow\qquad r = \frac{1 + n}{1 + i} - 1
```

The familiar shortcut $`n \approx r + i`$ drops the small product $`r \cdot i`$. With a real rate of 4%
and inflation of 2.5%:

```text
nominal rate 6.6000% (the sum 6.5000% is the approximation)
real rate back from nominal: 4.0000%
```

Now value P022, started in 2028, at the start of 2027. Assume its costs escalate at exactly general
inflation, so its real costs are the 2027 quotes and its nominal costs are those quotes escalated at
2.5%. There are four ways to pair flows with a rate, and an approximate fifth:

```python
cases = [("real flows,    real rate   ", real_flows, real),
         ("nominal flows, nominal rate", nominal_flows, nominal),
         ("nominal flows, real rate   ", nominal_flows, real),
         ("real flows,    nominal rate", real_flows, nominal),
         ("nominal flows, approx rate ", nominal_flows, real + inflation)]
for label, flows, rate in cases:
    print(f"{label}  PV {present_value(flows, rate, price_year):>9,.2f}")
```

```text
real flows,    real rate     PV -2,318.66
nominal flows, nominal rate  PV -2,318.66
nominal flows, real rate     PV -2,461.50
real flows,    nominal rate  PV -2,184.83
nominal flows, approx rate   PV -2,323.92
```

The first two lines are equal, to the cent, and they must be: each nominal amount is the real amount
times $`(1 + i)^{y - b}`$, and the nominal rate's discount factor is the real one divided by
$`(1 + i)^{y - b}`$, so inflation cancels year by year. That is the rule. **Either** escalate
everything and discount at a nominal rate, **or** keep everything in base-year dollars and discount
at a real rate. The answer is the same.

The next two lines are the two mixes, and they err in opposite directions:

- **Nominal flows at a real rate** count inflation in the flows and never take it out: the cost
  looks $143k bigger. Later costs are hurt most, so long projects and late starts look too expensive.
- **Real flows at a nominal rate** take inflation out of the rate without ever putting it into the
  flows: the cost looks $134k smaller. Here later costs look too cheap, and a model defers work to
  "save" money that was never saved.

The last line shows that the $`r + i`$ shortcut is close but not exact: $5k on one project. It is
small here and grows with the rates and the horizon. When the numbers feed a table that is
supposed to reconcile with finance's, use the exact Fisher relation.

GridCap applies no escalation anywhere: its cost profiles are 2027 quotes, used unchanged in every
year, and its 7% rate is applied to them. So the course reads GridCap's amounts as real 2027 dollars
and its 7% as a real rate. That is the consistent reading; GridCap's data does not say it, and
lesson 7.2.4 states it with the model.

<!-- practice 2 -->

## Only Escalation Above Inflation Changes a Real Model

If a cost escalates at exactly general inflation, a real model can ignore it: in base-year dollars
the cost does not change. Costs rarely do that. Skilled labour, copper and transformers have all at
times risen faster than prices in general. What a real model needs is the **real escalation**, the
part above inflation, given by the same Fisher arithmetic:

```math
e_{\text{real}} = \frac{1 + e}{1 + i} - 1
```

```text
labour escalating 4.5% with inflation 2.5%: real escalation 1.9512%
```

So in a real-dollar model, labour-heavy work should escalate at about 1.95% a year, not 4.5% (that
would count inflation twice) and not 0% (that would ignore the part of the rise that is real). A
cost that rises *slower* than inflation has a negative real escalation and gets cheaper in real
terms. Mixed projects escalate each cost component at its own rate before the profile is summed.

## Check a Borrowed Formula's Indices Before You Use It

Interview-prep material is full of NPV formulas, and a formula can be dimensionally fine and still
wrong for a start-year model. Take one that writes the NPV of project $`i`$ started in year $`t`$,
with years numbered $`1, \dots, T`$, escalation $`e`$ and discount rate $`r`$, as

```math
\text{NPV}_{i,t} = \sum_{\tau = t}^{T} \frac{\text{CF}_{i,\tau}\,(1 + e)^{\tau - 1}}{(1 + r)^{\tau}}
```

Two questions find its problems.

**What is $`\text{CF}_{i,\tau}`$ indexed by?** The calendar year $`\tau`$, and it has no $`t`$. Read
literally, the cash flow does not move when the start moves; a later start only cuts off the early
years of the sum. Written for P022 as if it started in year 1, a start in year 3 keeps only the
$1,470k of the third year:

```python
def literal(cf: dict[int, float], t: int, e: float) -> float:
    return sum(cf.get(tau, 0) * (1 + e) ** (tau - 1) / (1 + r) ** tau for tau in range(t, T + 1))


def shifted(t: int, e: float) -> float:
    """The cost profile moved to start in year t, same exponents as the borrowed formula."""
    return sum(c * (1 + e) ** (t + k - 1) / (1 + r) ** (t + k) for k, c in enumerate(profile))
```

```text
start  literal   shifted   (PV of cost, e = 3%)
    1   2257.2    2257.2
    2   1920.8    2172.8
    3   1273.0    2091.6
```

The literal reading says a year-3 start costs $1,273k in present value, $819k less than the shifted
profile's $2,092k, because the first two years of cost have vanished from the sum. The cost must be shifted with the start: the amount paid in year $`\tau`$ by
a project started in $`t`$ is its profile entry $`c_{i,\tau - t}`$, exactly the
$`c_{i,\,y - t}`$ of lesson 6.4.2's budget rows. The "shifted" column does that and keeps
everything else.

**Where do the exponents start?** Escalation has exponent $`\tau - 1`$, discounting $`\tau`$. So prices
are those of year 1 (no escalation in year 1), but money is valued one year earlier, at time 0, with
year 1 discounted once. That is consistent only if both choices are intended. The test is to set
$`e = r`$: if escalation and discounting start from the same date, they cancel and the PV equals the
undiscounted cost. Here they do not:

```text
e = r, start 1: shifted 2383.18, undiscounted cost 2550, cost / (1 + r) 2383.18
```

The formula leaves one year of discounting over, so it values year-1 prices at time 0. That is a
defensible convention, but it must be stated, and every other number in the model must use the same
one. The course's convention avoids the offset: the price base year and the valuation date are both
the start of 2027, and amounts are paid at the start of their year (lesson 7.2.1). The shortcut of
the first rule, escalation counted from the project's start, fails the other test (does the
escalation exponent move with the start?), so between them the two formulas show both ways to get
an escalation exponent wrong.

## Summary

- **Escalation turns a price quoted in one year into the price paid in another.** Escalate by
  $`(1 + e)^{y - b}`$, counted from the price base year $`b`$; counting from the project's start makes
  later starts look cheaper (P022 at 2029: $128k of PV missing).
- **Real dollars pair with a real rate, nominal dollars with a nominal rate.** Both give the same
  PV; the two mixes err in opposite directions; use the exact Fisher relation.
- **Only escalation above inflation changes a real model.** $`e_{\text{real}} = (1 + e)/(1 + i) - 1`$.
- **Check a borrowed formula's indices before you use it.** The cash flow must shift with the start,
  and $`e = r`$ should cancel exactly when the price base year and the valuation date coincide.

## Reference

| Quantity | Formula |
| --- | --- |
| nominal cost paid in year $`y`$ | $`c \,(1 + e)^{y - b}`$, $`b`$ the price base year |
| Fisher relation | $`(1 + n) = (1 + r)(1 + i)`$ |
| real rate from nominal | $`r = (1 + n)/(1 + i) - 1`$ |
| real escalation | $`(1 + e)/(1 + i) - 1`$ |
| consistent pairs | nominal flows at $`n`$, or real flows at $`r`$ |

| Mistake | Effect on a cost's PV |
| --- | --- |
| escalation counted from the project's start | later starts too cheap |
| nominal flows, real rate | too large |
| real flows, nominal rate | too small |
| $`n \approx r + i`$ | slightly off, more over long horizons |
| cash flow indexed by calendar year, not shifted | later starts lose costs |

**Further reading:** [numpy-financial: `npv`](https://numpy.org/numpy-financial/latest/_api_stubs/numpy_financial.npv.html)
(the per-period rate must match the period of the cash flows); [Klevorick, *Mathematical Programming
and Capital Budgeting Under Risk*, 1966](https://www.princeton.edu/%7Eerp/ERParchives/archivepdfs/R14.pdf)
(a project as a vector of cash outlays and returns per period, against a budget per period).

## Challenges

1. P022's estimate is re-priced in 2029 at $380k, $760k and $1,550k. Which price base year do you
   escalate from now, and what is a 2030 start's first-year cost at 3%?
2. A regulator gives you a nominal rate of 8% and inflation of 3%. What real rate do you use for
   GridCap's 2027-dollar costs?
3. Rewrite the borrowed formula so the cash flow shifts with the start and the exponents follow the
   course's convention.

## Design Note: Why the Course Models in Real Dollars

A real-dollar model has one fewer number to forecast (inflation) and keeps every year's budget
comparable with every other. Its risk is the one this lesson names: a cost that escalates faster
than inflation must be escalated at its real rate, or the model treats late work as too cheap. A
nominal model matches what finance books and what a budget actually pays, so reports often need
nominal numbers. Keep the model in one kind of dollar, and convert at the edge, in the report.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**escalation.py.** Escalates P022's cost profile from 2027 prices for each start year (*Escalation
Turns a Price Quoted in One Year Into the Price Paid in Another*). *Try:* Set the escalation to 0.
Predict the three totals.

- Program: [escalation.py](src/escalation.py)

**escalation_base.py.** Compares escalation counted from the price base year with escalation
counted from the start (*the same section*). *Try:* Make the price base year 2029. Predict which
start the two conventions now agree on.

- Program: [escalation_base.py](src/escalation_base.py)

**real_nominal.py.** Values P022 with real and nominal flows and rates, the two mixes and the
approximate rate, and computes a real escalation (*Real Dollars Pair With a Real Rate* and *Only
Escalation Above Inflation*). *Try:* Raise inflation to 6%. Predict whether the gap between the
exact and approximate lines grows.

- Program: [real_nominal.py](src/real_nominal.py)

**tutorial_formula.py.** Evaluates the borrowed formula literally and with the profile shifted, and
runs the $`e = r`$ test (*Check a Borrowed Formula's Indices*). *Try:* Change the escalation
exponent to `tau` and rerun the test. Predict the result.

- Program: [tutorial_formula.py](src/tutorial_formula.py)
