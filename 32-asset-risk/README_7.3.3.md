# 7.3.3 Consequence of Failure and Risk = PoF × CoF

GridCap's reliability engineer brings two lists to the planning meeting. The first ranks assets by
probability of failure: an overgrown corridor and an aging transformer lead it. The second ranks
them by what a failure would cost: a vegetation circuit and a transmission line lead that one. "Which list do we fund from?" Neither. A planner needs one number per asset that puts
likelihood and cost on the same scale, and that number is **risk**: the expected cost of failure per
year. This lesson builds the consequence of failure from its parts, shows what "expected" means, why
the two lists and the risk list disagree, and which of two counting conventions the course uses, in
four rules.

GridCap is a fictional utility generated for this course; its assets, costs and customers describe
no real company. Its tiny, small and medium portfolios each number their assets from A001, so an ID
names a different asset in each: this lesson's simulation uses tiny's A006, a transformer, and its
rankings use small's A006, a vegetation corridor.

## Consequence Is the Cost of One Failure, Added Up From Its Parts

The **consequence of failure** (CoF) of an asset is what one failure of it costs the utility and
its customers, in dollars. It is a sum of parts, each of which someone has to estimate:

```math
\text{CoF} = \underbrace{\text{repair}}_{\text{crew, parts}} + \underbrace{N \cdot H \cdot v}_{\text{customer interruption}} + \underbrace{p_{\text{inj}}\, C_{\text{inj}}}_{\text{safety}} + \underbrace{p_{\text{env}}\, C_{\text{env}}}_{\text{environment}}
```

where $`N`$ is the number of customers who lose power, $`H`$ the hours until they are restored,
$`v`$ the cost to a customer of one hour without power, and each $`p\,C`$ is the chance that a
failure causes an injury or a spill times its cost. Utilities differ in which parts they count and
how they price them (a cost per customer-hour, a regulator's penalty, a safety weighting), so ask
for the parts, not only the total.

One invented substation transformer, with numbers made up for this lesson:

```python
interruption = customers_out * hours_out * cost_per_customer_hour
cof = repair + interruption + safety + environment
```

```text
repair $380k + interruption $630k + safety $100k + environment $30k = CoF $1,140k
one failure adds 0.035 interruptions per customer (SAIFI) and 12.6 minutes per customer (SAIDI)
```

The second line connects the consequence to the reliability measures regulators track. **SAIFI**
(System Average Interruption Frequency Index) is the number of customer interruptions in a year
divided by the customers served; **SAIDI** (System Average Interruption Duration Index) is the
customer-minutes (or hours) without power divided by the customers served. One failure of this
transformer interrupts 4,200 of the utility's 120,000 customers for 6 hours, so it adds
4,200 / 120,000 = 0.035 to SAIFI and 4,200 × 360 / 120,000 = 12.6 minutes to SAIDI. Lesson 7.4.1
uses those measures as benefits in their own right; here they are one way to price the
interruption part of CoF.

GridCap keeps it simple: each asset carries one integer `cof` in $k, which the generator draws
evenly between 50 and 4,000. It has no parts and no link to the asset's kind. That is enough for
the arithmetic of this section; a real plan needs the parts, because they are where planners and
regulators will push back.

<!-- practice 1 -->

## Risk Is the Expected Failure Cost per Year

Risk combines the two lists. For an asset of age $`a`$ that is working today:

```math
\text{risk}(a) = \text{PoF}(a) \times \text{CoF}
```

in $k per year, with PoF from lesson 7.3.1. It is an **expected value**: the average cost per year
over many imagined repetitions of the coming year, not the cost of any actual year. In a real year
the asset either fails, costing CoF, or does not, costing nothing. A simulation of tiny's A006, a
68-year-old transformer whose PoF is 0.0947, makes that concrete. `rng.random(100_000)` draws
100,000 numbers evenly between 0 and 1, and each one below the PoF is a year in which A006 fails:

```python
fails = rng.random(100_000) < pof              # 100,000 imagined copies of next year
cost = np.where(fails, a.cof, 0)
```

```text
A006: PoF next year 0.0947, CoF $2,734k, risk = PoF x CoF = $258.9k per year
in 100,000 simulated years: failure years 9,534, cost in any one year: [0, 2734], average $260.7k
```

No single year costs $258.9k; every year costs either 0 or $2,734k. The average over many years is
$260.7k, within sampling noise of PoF × CoF. That is why risk adds up across assets and years: the
expected cost of a portfolio is the sum of its assets' expected costs, whether or not their failures
are independent. And it is why risk is the right objective for a utility that runs thousands of
assets for decades, but says nothing about the spread: a plan that cuts expected cost can still
leave a small chance of a very bad year.

## PoF, CoF and Risk Rank Assets Differently, and a Risk Matrix Blurs Them

Rank the small portfolio's 38 assets three ways:

```python
print("top 5 by PoF :", top(lambda r: r[1]))
print("top 5 by CoF :", top(lambda r: r[2]))
print("top 5 by risk:", top(lambda r: r[1] * r[2]))
```

```text
38 assets
top 5 by PoF : A006, A027, A019, A011, A024
top 5 by CoF : A014, A025, A019, A017, A028
top 5 by risk: A019, A027, A024, A005, A033
  A019: PoF 0.1014 x CoF $3,779k = $383.1k per year
  A027: PoF 0.1125 x CoF $3,313k = $372.9k per year
  A024: PoF 0.0705 x CoF $3,385k = $238.8k per year
  A005: PoF 0.0645 x CoF $3,502k = $226.1k per year
  A033: PoF 0.0562 x CoF $3,390k = $190.6k per year
```

Only A019 is in all three lists. Small's A006 (a corridor, not the tiny transformer simulated
above), the most likely to fail, is out of the risk top five because its failure is cheap ($641k);
A014, the most expensive to lose, is out because it is young and unlikely to fail. Two of the risk
top five (A005 and A033) are in neither of the other lists: they are moderately likely *and*
moderately expensive. Sorting by one factor at a time misses exactly the assets where both are high
enough to matter.

Many utilities show risk as a **risk matrix**: PoF and CoF each cut into five bands, and each asset
placed in one of 25 colored cells. It is a good picture and a poor number. With PoF bands at 1%,
2%, 5% and 10% and CoF bands at $500k, $1,000k, $2,000k and $3,000k:

```text
busiest risk-matrix cell (PoF band 3, CoF band 5): 4 assets, risk from $103.8k (A001) to $168.7k (A023)
```

Four assets share a cell and a color, and the riskiest of them carries 1.6 times the risk of the
least. An optimizer that received the cell instead of the product would treat them as equal.
Use the matrix to show risk; give the model the product.

<!-- practice 2 -->

## Count Expected Failures When a Failed Asset Is Repaired and Kept

PoF counts *whether* the asset fails in the year: at most once. But a utility usually repairs a
failed breaker or line and puts it back in service, and a repaired asset can fail again in the same
year. If the repair returns the asset to working order without making it any younger, a convention
called **minimal repair**, its failures arrive at the rate $`h(t)`$ of lesson 7.3.1 for as long as
it is kept. Failures then follow a Poisson process whose expected count between ages $`a`$ and
$`a + 1`$ is the hazard accumulated over the year (the NIST handbook's power-law process, whose
expected count $`M(t) = (t/\eta)^\beta`$ is exactly the Weibull cumulative hazard):

```math
\text{failures}(a) = \Lambda(a+1) - \Lambda(a), \qquad \text{PoF}(a) = P(\text{at least one}) = 1 - e^{-\text{failures}(a)}
```

```python
def failures_next(age: float, beta: float, eta: float) -> float:
    """Expected failures in the coming year if every failure is repaired without making it younger."""
    return cumulative_hazard(age + 1, beta, eta) - cumulative_hazard(age, beta, eta)
```

So the two conventions in this course's earlier lessons are two counts of the same curve. Lesson
1.1.2 multiplied CoF by the PoF; lesson 6.6.4 multiplied it by the expected number of failures.
Since $`1 - e^{-x} \le x`$, the expected count is never smaller, and the two are close while both
are small:

```text
GridCap small: largest gap 0.0182, on A006 (age 28, beta 3.83, eta 25.8): PoF 0.1786, expected failures 0.1968
one invented worn-out asset, beta 4, eta 20:
  age 20: PoF 0.194, expected failures 0.216
  age 30: PoF 0.508, expected failures 0.710
  age 40: PoF 0.810, expected failures 1.661
```

The A006 in that first line is small's corridor again. On GridCap small the two never differ by more
than 0.018 a year. On a badly worn asset they part: at age
40 the invented asset fails 1.66 times a year on average, while the chance of at least one failure
can never pass 1. If each failure costs CoF, the expected yearly cost is CoF × expected failures,
not CoF × PoF. **This course uses the expected count from here on** (lesson 7.3.4 builds on it):

```python
def yearly_risk(age: float, beta: float, eta: float, cof: float) -> float:
    """Expected failure cost in the coming year, $k: expected failures times the cost of one."""
    return cof * failures_next(age, beta, eta)
```

It adds up exactly over years, because expected counts over consecutive years sum to the expected
count over the whole span. The PoF version answers a different question, "how likely is at least
one failure," which is the right one for an asset that is retired, not repaired, when it fails.

<!-- practice 3 -->

## Where This Enters the Model

Risk is still a coefficient, not a decision. Lesson 1.1.2 used one year's risk avoided as the
objective coefficient $`a_i`$ of a one-period selection model; lesson 7.3.4 sums the risk removed
year by year into $`\text{rr}_{i,s}`$, one coefficient per project and start year, for the
multi-period model of lesson 6.4.1. The rows of those models do not change.

## Summary

- **Consequence is the cost of one failure, added up from its parts.** Repair, customer
  interruption ($`N \cdot H \cdot v`$), safety and environment; the interruption part links to SAIFI
  and SAIDI. GridCap's `cof` is one number drawn between $50k and $4,000k.
- **Risk is the expected failure cost per year.** PoF × CoF is an average over many years; any one
  year costs 0 or the CoF.
- **PoF, CoF and risk rank assets differently, and a risk matrix blurs them.** Give the model the
  product, not the cell.
- **Count expected failures when a failed asset is repaired and kept.** Expected failures
  $`\Lambda(a+1) - \Lambda(a) \ge \text{PoF}`$; the course's yearly risk is CoF times that count.

## Reference

| Term | Meaning | Formula |
| --- | --- | --- |
| CoF | cost of one failure, $k | repair + $`N H v`$ + $`p_{\text{inj}}C_{\text{inj}}`$ + $`p_{\text{env}}C_{\text{env}}`$ |
| SAIFI | customer interruptions per customer served, per year | $`\sum_i N_i / N_{\text{total}}`$ |
| SAIDI | customer-minutes without power per customer served, per year | $`\sum_i N_i H_i / N_{\text{total}}`$ |
| risk (at most one failure) | expected failure cost next year, $k | $`\text{PoF}(a) \times \text{CoF}`$ |
| expected failures (minimal repair) | average failures next year | $`\Lambda(a+1) - \Lambda(a)`$ |
| yearly risk (this course) | expected failure cost next year, $k | $`\text{CoF}\,(\Lambda(a+1) - \Lambda(a))`$ |
| risk matrix | PoF and CoF bands on a grid | for display, not for the model |

**Further reading:** [Wikipedia, SAIDI](https://en.wikipedia.org/wiki/SAIDI) (the definition as customer outage time summed over locations and divided by customers served); [Wikipedia, SAIFI](https://en.wikipedia.org/wiki/SAIFI) (the definition as customer interruptions divided by customers served); [NIST/SEMATECH e-Handbook, the NHPP power law model](https://www.itl.nist.gov/div898/handbook/apr/section1/apr172.htm) (expected failures $`M(t) = at^b`$ for a repairable system, the Poisson probability of no failures, and its link to the Weibull); [NIST/SEMATECH e-Handbook, the failure (hazard) rate](https://www.itl.nist.gov/div898/handbook/apr/section1/apr123.htm) (the cumulative hazard the expected count is built from); [SciPy, `scipy.stats.weibull_min`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.weibull_min.html) (`logsf`, whose negative is the cumulative hazard the practices check against).

## Challenges

1. The transformer of the first section is moved to a ring circuit, so its customers are back in
   1 hour instead of 6. Recompute its CoF and its SAIDI contribution by hand.
2. Two assets each carry $100k of risk a year: one with PoF 0.5% and CoF $20,000k, one with PoF 10%
   and CoF $1,000k. Is a planner right to treat them as equal? What would you add to the objective
   if not?
3. Find the age at which the invented asset (shape 4, scale 20) expects exactly one failure a year.

## Design Note: Why Not Put the Risk Matrix's Score in the Model

A risk matrix often comes with a score per cell, such as the PoF band times the CoF band, from 1
to 25. Those scores are ranks, not amounts: a cell scored 20 does not hold twice the risk of one
scored 10, and two assets with the same score can differ by a factor of several. An optimizer adds its
coefficients and trades them against dollars of budget, so every coefficient must be an amount on a
common scale. PoF × CoF in $k per year is such an amount; a matrix score is not. When a utility's
only risk data is the matrix, ask for the underlying PoF and CoF; if they do not exist, say in the
plan's assumptions that the model ranks by a score, not by expected cost.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**consequence.py.** Adds up an invented transformer's CoF from its parts and its SAIFI and SAIDI contributions (*Consequence Is the Cost of One Failure*). *Try:* Halve `hours_out`. Predict which two printed numbers change.

- Program: [consequence.py](src/consequence.py)

**risk_is_expected.py.** Simulates 100,000 years of A006 and compares the average cost with PoF × CoF (*Risk Is the Expected Failure Cost per Year*). *Try:* Simulate 100 years instead. Predict how far the average lands from $258.9k.

- Program: [risk_is_expected.py](src/risk_is_expected.py)

**risk_rankings.py.** Ranks the small portfolio's assets by PoF, CoF and risk, and finds the busiest risk-matrix cell (*PoF, CoF and Risk Rank Assets Differently*). *Try:* Make the CoF bands $1,000k apart from $1,000k up. Predict whether the busiest cell gets more or fewer assets.

- Program: [risk_rankings.py](src/risk_rankings.py)

**two_conventions.py.** Compares PoF with the expected number of failures on GridCap small and on an invented worn-out asset (*Count Expected Failures*). *Try:* Print the invented asset at age 50. Predict whether the expected count passes 3.

- Program: [two_conventions.py](src/two_conventions.py)

**asset_curves.py.** The module's library, with `failures_next` and `yearly_risk`.

- Library: [asset_curves.py](src/asset_curves.py)
