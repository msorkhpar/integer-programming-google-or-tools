# 1.1.2 Predictive vs. Prescriptive: Where PoF/RUL Predictions Stop and Optimization Starts

GridCap's asset analytics team has shipped a model. For every asset it predicts a **probability of
failure** (PoF) and a **remaining useful life** (RUL). At the planning meeting someone says: "We
have the risk scores now. Fund the riskiest assets first and we're done." That sentence mixes up
two jobs. A prediction says what is likely to happen if nothing changes. A prescription says what
to do about it, given the money and the rules. This lesson draws the line between them, in four
rules.

## A Prediction Describes the Future Without You; a Prescription Chooses What You Do

The analytics model hands over, per asset, the shape and scale of a Weibull failure curve
(section 7 explains them), an age, an RUL and a **consequence of failure** (CoF): what one failure costs in
outages, repairs and penalties. The first thing a planner can use is the chance the asset fails
*next year, given that it is working today*:

```math
\text{PoF}_{\text{next}}(a) = \frac{F(a+1) - F(a)}{1 - F(a)}, \qquad F(t) = 1 - e^{-(t/\eta)^{\beta}}
```

```python
def next_year_pof(age: float, beta: float, eta: float) -> float:
    """Probability it fails in the coming year, given that it is still working at `age`."""
    survived = 1 - cumulative_pof(age, beta, eta)
    return (cumulative_pof(age + 1, beta, eta) - cumulative_pof(age, beta, eta)) / survived
```

Multiply by the consequence and you get the **risk**, the expected failure cost per year, in $k:

```text
asset age RUL PoF next yr  CoF $k risk $k/yr
A001   13  14       0.033   3,317      109.5
A002   29  24       0.016   2,696       43.0
A003   18  15       0.030   2,170       65.2
A004   62   1       0.034     542       18.6
A005   10  24       0.011   3,513       39.2
A006   68   1       0.095   2,734      258.9
A008   17  25       0.019   1,096       21.2
```

Everything in this table is a *description*. It says nothing about which project to fund, because
it knows nothing about costs, budgets or rules. Look at A004: an RUL of 1 year, yet a PoF of only
3.4% next year. RUL and PoF come from different questions (when is the asset "used up", and how
likely is a failure in the next twelve months) and they do not have to agree. A planner who reads
"RUL 1" as "fails next year" overstates the urgency by a factor the table does not show.

## Ranking by Risk Is Not a Plan

"Fund the riskiest first" is a rule for building a plan, and it is the greedy rule of lesson 1.1.1
with a different sort key. To compare it fairly, give each project the risk it *removes*: a
replacement makes the asset new, and a repair or a trim takes it back to half its age.

```text
P001 replace     risk avoided  109.1 $k/yr  capex 2,150
P002 rebuild     risk avoided   43.0 $k/yr  capex 2,730
P003 replace     risk avoided   65.2 $k/yr  capex 2,470
P004 replace     risk avoided   18.4 $k/yr  capex 3,000
P005 trim        risk avoided   25.3 $k/yr  capex   250
P006 replace     risk avoided  258.9 $k/yr  capex 1,970
P007 repair      risk avoided  215.4 $k/yr  capex   290
P008 widen       risk avoided    6.5 $k/yr  capex   580
```

Now fund the riskiest assets first, and separately search every plan for the one that removes the
most risk within the rules:

```python
def riskiest_first() -> set[str]:
    plan: set[str] = set()
    for p in sorted(tiny.projects, key=lambda p: expected_failure_cost(tiny.asset(p.asset_id)), reverse=True):
        if sum(by_id[i].capex for i in plan) + p.capex <= tiny.capital_budget:
            plan.add(p.project_id)
    return plan
```

```text
riskiest first  ['P001', 'P003', 'P005', 'P006', 'P007'] avoids 674.0 breaks a rule
most avoided    ['P001', 'P002', 'P005', 'P006'] avoids 436.3 allowed
```

The risk ranking funds both the replacement and the repair of the same transformer (P006 and P007),
which counts the same risk twice, and it drops the must-do P002. Its 674.0 looks better than the
optimized 436.3 only because it is not a plan the utility can carry out. The ranking is still
useful: it tells you where the risk is. Deciding what to do about it is a different step.

Stepping back: the prediction gives you the **coefficients** (risk per asset, risk avoided per
project). The optimization gives you the **decision** (which projects, within which rules). Merging
the two steps into "sort by risk" throws away the rules.

<!-- practice 1 -->

## Predictions Enter the Model as Coefficients, and Their Errors Travel With Them

Every PoF is an estimate. If the analytics model is biased for one asset class, how wrong does it
have to be before the plan changes? Scale every distribution asset's PoF and solve again:

```python
if __name__ == "__main__":
    for scale in (0.3, 0.5, 1.0, 2.0):
        print(f"distribution PoF x{scale}: best plan {sorted(best_plan(scale))}")
```

```text
distribution PoF x0.3: best plan ['P002', 'P003', 'P005', 'P007', 'P008']
distribution PoF x0.5: best plan ['P001', 'P002', 'P005', 'P006']
distribution PoF x1.0: best plan ['P001', 'P002', 'P005', 'P006']
distribution PoF x2.0: best plan ['P001', 'P002', 'P005', 'P006']
```

The plan holds from half to double the predicted PoF. It has changed by the time the true PoFs are
0.3 of the prediction, a model that overstates distribution risk about three times over. That is the answer the director needs about the analytics
model: not "is the model accurate?" but "is it accurate enough for this decision?" Section 9 turns
this into a habit (sensitivity analysis), and section 10 makes sure that when the plan changes, it
changes because the data did and not because the solver ran differently.

## The Model Owns the Trade-off, and the Planner Owns the Decision

Three parties touch a capital plan, and confusing their jobs is how bad plans get approved:

- **The predictive model** estimates PoF, RUL and consequences. It is judged on accuracy.
- **The optimization model** finds the best plan for stated rules and an objective. It is judged on
  whether its plan is feasible, optimal for the question asked, and reproducible.
- **The planner** chooses the objective, signs off the rules, and decides whether to adopt the plan.

When a plan looks wrong, the first question is *which of the three is wrong*: a bad coefficient,
a missing rule, or the wrong objective. The optimizer cannot tell you which, and section 9 is
about the tools that help.

## The Model

The plan that removes the most risk is the model of lesson 1.1.1 with a different objective. The
prediction enters only as the coefficient $`a_i`$; the sets, the variables and the rules are
untouched.

**Parameters, new.** For each project $`i`$ on asset $`k(i)`$, the risk it avoids per year ($k):

```math
a_i = \text{CoF}_{k(i)} \Big( \text{PoF}_{\text{next}}\big(\text{age}_{k(i)}\big) - \text{PoF}_{\text{next}}\big(\rho_i\,\text{age}_{k(i)}\big) \Big)
```

where $`\rho_i`$ is the share of its age the asset keeps after the work: 0 for a replacement, a
rebuild or undergrounding, 0.5 for a repair, a trim, a clearing or a widening, in this lesson.

**Variables.** $`x_i \in \{0, 1\}`$ for each $`i \in P`$, as before.

**Objective.**

```math
\max \; \sum_{i \in P} a_i\, x_i
```

**Constraints.** The four rows of lesson 1.1.1, unchanged:

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

<!-- practice 2 -->

## Summary

- **A prediction describes the future without you; a prescription chooses what you do.** PoF, RUL
  and CoF are inputs, and PoF next year is conditional on the asset working today.
- **Ranking by risk is not a plan.** It ignores costs and rules, can fund two alternatives on one
  asset and can drop a must-do.
- **Predictions enter the model as coefficients, and their errors travel with them.** Ask how wrong
  a coefficient can be before the plan changes.
- **The model owns the trade-off, and the planner owns the decision.** When a plan looks wrong,
  find out whether the coefficient, the rule or the objective is at fault.

## Reference

| Quantity | Meaning | Comes from |
| --- | --- | --- |
| $`F(t)`$ | probability an asset has failed by age $`t`$ | the predictive model's curve |
| $`\text{PoF}_{\text{next}}(a)`$ | probability it fails in the next year, given it works at age $`a`$ | $`(F(a+1)-F(a))/(1-F(a))`$ |
| RUL | predicted years until the asset is "used up" | the predictive model, separately |
| CoF | cost of one failure, $k | asset and network data |
| Risk | expected failure cost per year, $k | $`\text{PoF}_{\text{next}} \times \text{CoF}`$ |
| Risk avoided | how much risk a project removes | risk now minus risk after the intervention |

**Further reading:** [MO-book 2.7, BIM production using demand forecasts](https://mobook.github.io/MO-book/notebooks/02/07-bim-demand-forecast.html) (a forecast entering an LP as fixed right-hand sides, the same hand-over from prediction to prescription); [NIST/SEMATECH e-Handbook, the Weibull distribution](https://www.itl.nist.gov/div898/handbook/apr/section1/apr162.htm) (the Weibull failure curve $`F(t)`$, its reliability and failure rate, and why a shape above 1 means a rising failure rate).

## Challenges

1. A004 has an RUL of 1 year and a PoF of 3.4%. Write the two sentences you would say to a
   director who wants it replaced this year.
2. The repair-or-replace pair P006 and P007 avoids 258.9 and 215.4 $k/yr. What would make the
   repair the better choice in the optimized plan?
3. Which coefficient in this lesson would you most want a confidence interval for, and why?

## Design Note: Why the Risk Coefficient Is Conditional

The unconditional probability $`F(a+1) - F(a)`$ is the chance that a *new* asset fails in exactly
that year of its life. For an old asset it is small, because most assets of its kind would have
failed earlier, and the one in front of you did not. On A006's curve:

```text
A006: beta 3.66, eta 57.8 years
age 10: unconditional 0.0007  conditional 0.0007
age 30: unconditional 0.0105  conditional 0.0115
age 50: unconditional 0.0240  conditional 0.0433
age 70: unconditional 0.0136  conditional 0.1018
age 90: unconditional 0.0012  conditional 0.1884
```

The unconditional number peaks near 50 and falls, so a 90-year-old transformer would look safer
than a 30-year-old one. Planners care about the asset that is still standing, so the course always
divides by $`1 - F(a)`$. The cost is one more term to explain; the gain is a risk that grows with
age, as the asset's real condition does.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**asset_risk.py.** Turns each asset's failure curve into next year's expected failure cost (*A Prediction Describes the Future*). *Try:* Print the risk for A004 at twice its age. Does its RUL of 1 year make more sense then?

- Program: [asset_risk.py](src/asset_risk.py)

**conditional_pof.py.** Compares conditional and unconditional next-year PoF for one asset as it ages (*Design Note*). *Try:* Run it for A001 instead of A006. Predict which column grows with age.

- Program: [conditional_pof.py](src/conditional_pof.py)

**rank_vs_optimize.py.** Compares funding the riskiest assets first with the plan that removes the most risk within the rules (*Ranking by Risk Is Not a Plan*). *Try:* Set every `AGE_AFTER` value to 0.0, so a repair is as good as a replacement. Predict which project the best plan swaps.

- Program: [rank_vs_optimize.py](src/rank_vs_optimize.py)

**prediction_error.py.** Scales the distribution assets' PoF and re-solves, to see when the plan changes (*Predictions Enter the Model as Coefficients*). *Try:* Add 0.4 and 0.8 to the scales. Between which two does the plan change?

- Program: [prediction_error.py](src/prediction_error.py)
