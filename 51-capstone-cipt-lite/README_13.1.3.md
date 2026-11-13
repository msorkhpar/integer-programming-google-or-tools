# 13.1.3 Value: NPV by Start Year, Risk Reduction From PoF/RUL, Weighted Value

The model of lesson 13.1.2 maximizes NPV, and finance is satisfied. The asset team is not: a plan
chosen on NPV alone funds what pays back fastest, and leaves aging breakers and towers whose
failures cost far more than their NPV says. The board wants the plan chosen on a **weighted value**
of two benefits, NPV and the risk the work removes, and it wants to see where every coefficient
came from. This milestone builds the three coefficient tables, one entry per start variable, from
the snapshot: NPV by start year (section 7.2), risk reduction from each asset's failure curve and
its predicted RUL (section 7.3), and the weighted value that combines them (section 7.4). Then it
swaps the objective and shows what the rules let each objective buy. GridCap is a fictional
utility; its benefit forecasts and failure curves are invented.

## The Model

The model of lesson 13.1.2, unchanged except for its objective: the same sets, parameters,
variables $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$, and the same rows
$`(\text{once}_i)`$, $`(\text{must}_i)`$, $`(\text{force}_i)`$, $`(\text{alt}_g)`$,
$`(\text{after}_{c,t})`$, $`(\text{budget}_y)`$, $`(\text{region}_{r,y})`$, $`(\text{crews}_{k,y})`$
and $`(\text{floor}_r)`$, written out in full there. New parameters, built in this lesson:
$`\text{rr}_{i,t}`$, the discounted risk removed over a ten-year window if project $`i`$ starts in
$`t`$ ($k); references $`R_{\text{npv}}`$ and $`R_{\text{risk}}`$ ($k) and weights
$`w_{\text{npv}} + w_{\text{risk}} = 1`$. **Changed: the objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_{i,t}\, x_{i,t},
\qquad
v_{i,t} = w_{\text{npv}} \frac{\text{npv}_{i,t}}{R_{\text{npv}}} + w_{\text{risk}} \frac{\text{rr}_{i,t}}{R_{\text{risk}}}
```

## NPV by Start Year Is One Cash Flow, Shifted and Discounted to One Date

GridCap's export carries an NPV for every start year, and CIPT must not take it on trust: the
milestone rebuilds it from the benefit forecast finance hands over and checks that the two agree.
GridCap's forecast gives each project one benefit in its start year, $`\rho_i\, \text{capex}_i`$,
which shrinks by a share $`\delta_i`$ for each year the project waits after its earliest start
$`e_i`$ (the risk carried meanwhile). Lesson 7.2.4's rule: shift the whole cash flow to the start
year, and discount every amount to one date, the plan's first year $`y_0 = 2027`$:

```math
\text{npv}_{i,t} = \rho_i\, \text{capex}_i\, (1 - \delta_i)^{t - e_i} (1 + r)^{-(t - y_0)} - \sum_{k} c_{i,k}\, (1 + r)^{-(t + k - y_0)}
```

rounded to a whole $k, with GridCap's rate $`r = 7\%`$. In code, one line per term:

```python
def npv(costs: tuple[int, ...], benefit: float, start: int, rate: float, first_year: int) -> float:
    """NPV on `first_year` of a project started in `start`: one benefit in the start year, costs
    spread over its years of work, each amount discounted from its own calendar year."""
    value = benefit * (1 + rate) ** -(start - first_year)
    for k, cost in enumerate(costs):
        value -= cost * (1 + rate) ** -(start + k - first_year)
    return value
```

`value_medium.py` rebuilds the whole table. GridCap's generator drew each project's $`\rho_i`$ and
$`\delta_i`$ and kept only the NPVs, so the program replays it to recover the forecast, as lesson
7.2.4 did; a real finance team would send the two columns.

```text
NPV table: 887 entries, 887 equal to GridCap's own table
P086 Valley breaker bay replace (A086): costs (3980, 1990), benefit ratio 1.962, decay 0.051
  start year                      2027      2028      2029      2030
  NPV ($k)                       5,875     4,927     4,105     3,394
```

Every entry agrees, so the export's NPV column is exactly this calculation and the model may use
either. P086 shows the shape every row has: each year of delay costs one year of discounting on the
benefit and the costs, plus 5.1% of the benefit, so the NPV falls by $948k, $822k and $711k a year.
Discounting every start to 2027 is what makes delay show its cost; valuing each start from its own
year would make waiting look free (lesson 7.2.4).

<!-- practice 1 -->

## Risk Reduction Starts From the RUL, Made a Point on the Weibull Curve

Each asset has a Weibull failure curve with shape $`\beta`$ and a catalog scale $`\eta`$ for its
kind, and a remaining useful life (RUL) that the asset-health model predicted for this asset. Lesson
7.3.2 showed that the RUL alone does not fix the probability of failure, and how to use it: keep the
fleet's shape, and choose the scale that makes the RUL the **median** remaining life of an asset of
this age $`a`$:

```math
\hat\eta = \left(\frac{(a + \text{RUL})^\beta - a^\beta}{\ln 2}\right)^{1/\beta}
```

The asset's yearly risk at age $`u`$ is its consequence of failure times the expected failures of
that year, $`\text{CoF}\,(\Lambda(u + 1) - \Lambda(u))`$ with $`\Lambda(u) = (u/\hat\eta)^\beta`$
(lesson 7.3.3). Work started in $`t`$ and lasting $`d`$ years leaves the asset aging until it ends;
from year $`t + d`$ the asset is $`\kappa`$ times the age it had reached, with $`\kappa = 0`$ for a
replacement and $`0.5`$ for a repair, and ages again (lesson 7.3.4). The coefficient adds the
difference over a fixed ten-year window from 2027, discounted:

```python
    done, total = start + duration, 0.0
    for y in range(first_year, first_year + WINDOW):
        before = age + (y - first_year)
        after = before if y < done else keep * (age + (done - first_year)) + (y - done)
        total += (yearly_risk(before, beta, eta, cof) - yearly_risk(after, beta, eta, cof)) \
            / (1 + rate) ** (y - first_year)
```

The window is fixed, not the plan's remaining years after the start, so that a late start is
charged for the risk it carries in the meantime instead of being compared over a shorter period.
P086's breaker bay, both ways:

```text
asset A086: age 24, beta 2.79, catalog eta 37.8, RUL 16, CoF $480k; eta that makes the RUL the median: 41.3
  risk removed, catalog eta      124.7     109.5      94.1      78.5
  risk removed, RUL-anchored      97.2      85.4      73.3      61.2
```

The asset-health model says A086 is in better shape than its kind's catalog curve: a median of 16
more years needs a scale of 41.3, not 37.8, so every year's expected failures are lower and the
replacement removes about a fifth less risk at every start. That is the point of anchoring: the
coefficient uses what is known about this asset, not only what is known about its kind.

<!-- practice 2 -->

## Weighted Value Divides by Fixed References and Weights by Swing Ratings

NPV and risk removed are both in $k, but they are not the same dollars: NPV is money the utility
gets back, risk is expected failure cost avoided, and the board does not trade them one for one.
Lesson 7.4.2's rule makes each a unitless score by dividing by a **reference**, the swing from no
benefit to a benefit the board can picture, fixed before any project is scored: $5,000k of NPV and
$2,000k of risk removed. Lesson 7.4.3's swing weighting turns the board's ratings of the two swings
into weights: risk 100, NPV 60, so each rating over their sum.

```python
def value_table(npv_of: dict, rr_of: dict, reference: dict = REFERENCE,
                ratings: dict = RATINGS) -> dict[tuple[str, int], float]:
    """v[i, t] = w_npv * npv / R_npv + w_risk * rr / R_risk, in value points."""
    w = weights(ratings)
    return {key: w["npv"] * npv_of[key] / reference["npv"] + w["risk"] * rr_of[key] / reference["risk"]
            for key in npv_of}
```

```text
weights from ratings: npv 0.375, risk 0.625; references: npv $5,000k, risk $2,000k
  value (points)                 0.471     0.396     0.331     0.274
table digests: npv 3c3b29a9c499, risk a9e13516747a, value cad3c83db82e
```

Read P086's 2027 value back into its parts: $`0.375 \times 5{,}875/5{,}000 = 0.441`$ from NPV and
$`0.625 \times 97.2/2{,}000 = 0.030`$ from risk. Section 7.4 built a value function of four
measures (reliability, safety, environment, finance); GridCap's export carries the inputs of two,
so CIPT Lite's value function has two, and a third measure is one more term with its own reference
and rating.

The last line is how the milestone is graded. A coefficient table is data, so it gets a digest like
the snapshot: every value rounded to three decimals, the rows sorted, the SHA-256 of the result. A
test pins the three digests, so any change to a formula, a reference or a weight is a failed test
and a reviewed decision, never a silent shift in every plan.

<!-- practice 3 -->

## The Objective Changes the Plan, Never the Rules

The three tables give three objectives on the same rows. `value_medium.py` solves each with the run
setting:

```text
objective   projects   NPV ($k)  risk removed ($k)
npv              209    219,054            232,484
value            242    182,952            431,580
risk             230    155,096            433,096
```

The weighted value buys $199,096k more risk removed than the NPV plan for $36,102k of NPV. Against
the plan that maximizes risk alone it gives up $1,516k of risk removed and keeps $27,856k more NPV.
Every plan in the table passes the same rows, because only the objective moved: the budgets, crews,
precedence and must-dos of lesson 13.1.2 hold for each. Which plan is right is the board's choice,
expressed in the ratings; milestone 6 shows planners the whole range between the two ends as a
frontier, so the choice can be made with the trade-off in view (lesson 8.3.3).

## Summary

- **NPV by start year is one cash flow, shifted and discounted to one date.** Rebuilt from the
  benefit forecast, all 887 entries equal GridCap's table; each year of delay costs discounting and
  the decay.
- **Risk reduction starts from the RUL, made a point on the Weibull curve.** The scale that makes
  the RUL the median, expected failures with and without the work over a fixed ten-year window,
  discounted; A086's anchored curve removes about a fifth less than its catalog curve.
- **Weighted value divides by fixed references and weights by swing ratings.** 0.375 for NPV and
  0.625 for risk, references fixed before scoring; each table has a pinned digest.
- **The objective changes the plan, never the rules.** The value plan removes $199,096k more risk
  than the NPV plan for $36,102k of NPV, under the same rows.

## Reference

| Table | Formula | Lesson |
| --- | --- | --- |
| $`\text{npv}_{i,t}`$ | benefit $`\rho_i\,\text{capex}_i (1-\delta_i)^{t-e_i}`$ and costs, discounted to $`y_0`$ | 7.2.4 |
| $`\hat\eta_a`$ | $`(((a + \text{RUL})^\beta - a^\beta)/\ln 2)^{1/\beta}`$ | 7.3.2 |
| yearly risk | $`\text{CoF}\,((\frac{u+1}{\hat\eta})^\beta - (\frac{u}{\hat\eta})^\beta)`$ | 7.3.3 |
| $`\text{rr}_{i,t}`$ | risk without minus with the work, over 2027-2036, discounted | 7.3.4 |
| $`v_{i,t}`$ | $`w_{\text{npv}}\,\text{npv}/R_{\text{npv}} + w_{\text{risk}}\,\text{rr}/R_{\text{risk}}`$ | 7.4.4 |

| Setting | Value |
| --- | --- |
| rate $`r`$ | 7% |
| window | ten years from 2027 |
| age kept after work $`\kappa`$ | replace, rebuild, underground 0; repair, trim, clear, widen 0.5 |
| references | NPV $5,000k, risk $2,000k |
| ratings and weights | risk 100 (0.625), NPV 60 (0.375) |

**Further reading:** [OR-Tools: MathOpt](https://developers.google.com/optimization/math_opt) (an objective set again on the same model before the next solve); [SciPy `weibull_min`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.weibull_min.html) (shape `c` and `scale`, the curve of section 7.3).

## Challenges

1. Finance changes the rate to 5%. Which of the three tables change, which digests a test pins
   would fail, and why does the risk table change too?
2. The asset team proposes counting risk only over the years after each start, to the end of the
   plan. Which starts gain and which lose, and what does that do to deferral?
3. The board raises NPV's rating from 60 to 100. Predict whether the value plan moves toward the
   NPV row of the table or the risk row, then say what you would solve to check.

## Design Note: Coefficients Are Inputs, So They Get Digests

The model sees none of the formulas of this lesson; it sees 887 numbers per table. A changed
discount rate, a new reference or a fixed bug in the RUL anchoring all reach the plan only through
those numbers, so the tables are inputs exactly as the snapshot is. CIPT Lite therefore treats
them the same way: computed from the snapshot by code under test, and named by a digest that a test
pins. Milestone 5's run manifest records the snapshot's digest and the objective a run used; a run
that solves on these tables records their digests beside it, so a plan can always be traced to the
coefficients that chose it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**value_medium.py.** Rebuilds GridCap medium's NPV table, computes risk reduction with and without
the RUL anchor, builds the weighted value, prints each table's digest, and solves the three
objectives (every section). *Try:* Set the NPV rating to 100. Predict how many projects the value
plan funds.

- Program: [value_medium.py](src/value_medium.py)

The milestone's library is `cipt_value.py`.

- Library: [cipt_value.py](src/cipt_value.py)
