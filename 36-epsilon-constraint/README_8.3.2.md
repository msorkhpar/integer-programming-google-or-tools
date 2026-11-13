# 8.3.2 AUGMECON: Avoiding Weakly Efficient Points

GridCap finance changes one convention before the next planning cycle: vegetation work (trims,
clearings, widenings) is compliance spending with no revenue, so finance now books every vegetation
project at an NPV of 0. Its risk reduction is unchanged. The planners rerun lesson 8.3.1's sweep, and
something is off: at a risk floor of $9,404k the model returns a plan with NPV $22,993k that removes
$9,675k of risk, and another plan exists with the *same* NPV that removes $10,370k. The model offered
a plan that is plainly worse than one it could have offered.

Lesson 8.3.1 warned that a plain ε-constraint answer is only guaranteed to be *weakly* efficient.
This lesson shows it happening, then builds Mavrotas's **augmented ε-constraint method**, AUGMECON,
which removes the problem, and its later refinement, AUGMECON2, which generates a whole frontier
exactly with about one solve per point. Five rules.

The NPV-0 vegetation convention is a variant of GridCap small made for this lesson. GridCap is a
fictional utility generated for this course; its assets, projects and budgets describe no real
company.

## Plain ε-Constraint Can Return a Weakly Efficient Plan

The program builds the variant (every vegetation project's NPV set to 0) and runs lesson 8.3.1's
plain ε-constraint over 11 risk floors. Next to it, it runs AUGMECON, built in the next section, at
the same floors:

```python
for floor in grid(a.second, b.second, 11):
    p = epsilon_constraint(two.model, two.npv, two.risk, floor)
    q, slack = augmecon(two.model, two.npv, two.risk, floor, span)
    verdict = "weakly efficient" if dominates(q, p) else "Pareto-optimal"
```

```text
risk floor |  plain: NPV, risk  | AUGMECON: NPV, risk | plain is
     8,662 |  23,133     8,662  |  23,133     8,662   | Pareto-optimal
     9,404 |  22,993     9,675  |  22,993    10,370   | weakly efficient
    10,147 |  22,993    10,280  |  22,993    10,370   | weakly efficient
    10,889 |  22,911    10,944  |  22,911    10,944   | Pareto-optimal
    11,632 |  22,885    12,244  |  22,885    12,707   | weakly efficient
    12,374 |  22,885    12,616  |  22,885    12,707   | weakly efficient
    13,116 |  22,753    13,414  |  22,753    13,876   | weakly efficient
    13,859 |  22,753    13,876  |  22,753    13,876   | Pareto-optimal
    14,601 |  21,897    14,677  |  21,897    14,677   | Pareto-optimal
    15,344 |  21,149    15,348  |  21,149    15,374   | weakly efficient
    16,086 |  17,064    16,086  |  17,064    16,086   | Pareto-optimal
plain ε-constraint returned 6 weakly efficient plans out of 11
```

Six of eleven plain answers are dominated. Each time, AUGMECON's plan has the same NPV and removes
more risk: at the $9,404k floor, $695k more. The reason is the tie. A vegetation project now adds
risk reduction and nothing to NPV. Wherever the budget leaves room for one, the ε problem has several
optimal plans with the same NPV and different risk, and the plain model has no reason to prefer the
one with more risk. It only has to clear the floor. Which tied plan HiGHS returns is up to its
search; here it returned the weaker one six times.

Ties of this kind come from ordinary modeling choices: whole-$k NPVs, projects with no NPV of
their own, a third objective that does not enter the model at all. On GridCap small itself, with every project's NPV
positive, the same 11-floor sweep returned no weakly efficient plan (lesson 8.3.1's sweep found only
Pareto-optimal ones). The fix below does not rely on luck either way.

## Reward the Floor's Slack With a Weight Too Small to Cost Any of the Objective

Mavrotas's fix (2009) is to make the floor an equality with a slack variable, and to give the
objective a tiny reward for that slack. Among plans tied on the main objective, the one with the most
slack, the most risk above the floor, now wins.

**The model.** Everything of lesson 8.3.1's ε problem, with the floor row and the objective changed:

**Sets.** As in lesson 8.3.1: $`P`$, $`Y`$, $`T_i`$, $`M`$, $`\mathcal{G}`$, $`C`$.

**Parameters.** As in lesson 8.3.1, plus $`r_2 > 0`$, the range of the floored objective over the
payoff table (risk plan's risk minus NPV plan's risk, $k), and $`\rho`$, the weight of the slack
reward, a small positive number
($`10^{-3}`$ here).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$; and the slack
$`s \ge 0`$, continuous ($k of risk above the floor). ← this lesson

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \; + \; \frac{\rho}{r_2}\, s \quad \leftarrow \text{this lesson}
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \sum_{t \in T_i} \text{rr}_{i,t}\, x_{i,t} - s &= \varepsilon && && \text{(eps\_floor)} \quad \leftarrow \text{this lesson} \\
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s' \in T_{p(c)},\, s' \le t - L_c} x_{p(c),s'} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

Because $`s \ge 0`$, the equality $`\text{risk} - s = \varepsilon`$ says exactly what the old floor
said, risk $`\ge \varepsilon`$, and it names the excess $`s`$. In code:

```python
    s = model.add_variable(lb=0.0, name="eps_slack")
    row = model.add_linear_constraint(second - s == floor, name="eps_floor")
    model.maximize(first + (rho / span) * s)
```

**Why the reward is $`\rho / r_2`$.** Dividing by the range $`r_2`$ makes the slack term unit-free:
the slack can never exceed the range, so $`s / r_2 \le 1`$ and the whole reward is at most
$`\rho`$, here $1 (0.001 of $1k), whatever units the floored objective is in. NPV is in whole $k,
so two plans that differ in NPV differ by at least 1 ($1k), more than the largest possible reward.
The augmented model therefore never gives up NPV for slack; it only breaks ties. If the main
objective were not whole numbers, $`\rho`$ must be smaller than the smallest NPV difference that
matters to you.

Get the scale wrong and the slack term becomes a second objective. The program below rewards each
$k of slack with 1 instead of $`\rho / r_2`$, on GridCap small at lesson 8.3.1's $13,000k floor:

```text
reward 1e-3/5,509 per $k of slack: NPV $23,815k, risk $13,221k, slack 221
reward 1 per $k of slack:       NPV $22,870k, risk $15,554k, slack 2,554
the big reward gave up $945k of NPV for $2,333k more risk
```

With the small reward, the answer is lesson 8.3.1's plan exactly. With a reward of 1 the model
maximizes NPV plus risk above the floor, a weighted sum in disguise. It returns a different plan
with $945k less NPV, which is no longer the answer to "the most NPV with at least $13,000k of risk".

<!-- practice 1 -->

## Build the Payoff Table Lexicographically

The same tie strikes the two ends. Maximizing NPV alone may return any of several plans with the
best NPV, and the risk at that end sets the bottom of the floor's range. AUGMECON computes each end
**lexicographically**: optimize the objective, then hold it at its best and optimize the other one.
(Lexicographic optimization is the subject of lessons 8.2.1 and 8.2.2; here the tolerance is
zero.)

```python
def best_of(model, objective, then=None) -> mathopt.SolveResult:
    """Maximize `objective`; with `then`, keep it at its best and maximize `then` as well."""
    model.maximize(objective)
    result = solve(model)
    if then is None or result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return result
    hold = model.add_linear_constraint(objective >= result.objective_value() - TOL, name="hold_best")
    model.maximize(then)
    result = solve(model)
    model.delete_linear_constraint(hold)
    return result
```

On the NPV-0 variant:

```text
payoff table, one pass    : max NPV end (23,133, 7,481), max risk end (17,064, 16,086)
payoff table, lexicographic: max NPV end (23,133, 8,662), max risk end (17,064, 16,086)
```

The one-pass NPV end has the best NPV, $23,133k, but removes $7,481k of risk; the lexicographic end
has the same NPV and removes $8,662k. The one-pass end is weakly efficient, and it would also stretch
the floor's range down by $1,181k of risk where no Pareto plan lives. The `TOL` of $`10^{-6}`$ lets
the second pass keep a plan whose NPV the solver reports a hair under the first pass's value
(lesson 8.2.2 shows a run where a solver does).

## Put the Whole-Number Objective in the Floor, Step by One, and Keep the Reward Below Every Gap: the Frontier Is Exact

Lesson 8.3.1 found that a grid on risk must be impossibly fine to be sure of every Pareto plan,
because risk takes any real value. NPV does not. Every coefficient $`\text{npv}_{i,t}`$ is a whole
number of $k, so every plan's NPV is a whole number. Flip the roles: **maximize risk, and put NPV in
the floor**. Then:

- every Pareto plan's NPV is one of the whole numbers from the risk plan's NPV ($18,886k) to the NPV
  plan's ($24,260k);
- the AUGMECON problem with floor $`v`$ returns the Pareto plan with the most risk among the plans
  with NPV at least $`v`$, provided the reward cannot pay for a loss of risk (the third condition
  below); the slack reward rules out the weakly efficient ones;
- so stepping the floor by 1 through that range visits every Pareto plan.

This is the condition stated in the AUGMECON2 paper (Mavrotas and Florios, 2013) and in the GAMS
model library's implementation of it, `epscmmip.gms`: with integer objective coefficients, a step of
at most 1 in the floored objective gives the exact Pareto set. The exactness also needs each solve to
be optimal, which is why every solve here runs HiGHS at a zero relative gap.

The swap adds a third condition, and this one depends on the data. The reward now sits on the
maximized objective, risk, and is worth up to $`\rho`$ of it: $1 of risk (0.001 of $1k). Suppose two
neighbouring Pareto plans differed in risk by less than that. At a floor both clear, the solve could
take the one with a little less risk and more NPV above the floor, because its larger slack earns the
larger reward. The bypass would then move the floor past the other plan's NPV, and that plan would
never be found. In the orientation of the first rules, where NPV is maximized, this cannot happen:
NPV moves in whole $k, and the reward is worth less than $1k. Risk is not whole numbers, so here the
gap is a fact about this data, checked after the run. So the full conditions for an exact frontier
are four: whole-number coefficients on the floored objective, a step of 1, optimal solves, and a
reward smaller than the closest gap in the maximized objective between neighbouring Pareto plans.

`exact.py` generates the frontier, then checks the fourth condition the sure way: it generates the
frontier again with no reward, two passes per floor (maximize risk, then hold it and maximize NPV,
the sweep of lesson 8.1.2), which needs no assumption about gaps, and compares.

```text
65 Pareto-optimal plans in 65 ε solves (plus 4 for the payoff table)
pairs where one plan dominates another: 0
supported (a weighted sum finds them): 8; unsupported: 57
first five, by NPV: (18,886, 16,086), (18,942, 15,974), (18,964, 15,945), (19,419, 15,939), (19,485, 15,939)
two passes per floor, no reward: 65 plans; the same as AUGMECON's: True
closest neighbours differ by $91 of risk; the reward is at most $1 (0.001 of $1k)
```

All 65 plans, with no plan in the list dominating another. The closest neighbours are $91 of risk
apart, far more than the $1 the reward can buy, and the slower two-pass sweep finds the same 65
plans. The range holds 5,375 whole-number
floors, though, and the run used 65 solves. The next rule is how.

## Jump Past Floors the Slack Already Covers, and Stop at the First Infeasible One

The slack says how far above its floor the answer landed. If the floor is $`v`$ and the answer's
NPV is $`v + s`$, then every floor from $`v`$ up to $`v + s`$ returns the same plan: the plan still
clears each of those floors, and every plan with more risk has NPV below $`v`$, so it is excluded
from all of them. Those solves are redundant. AUGMECON2 skips them with a **bypass**: after a solve with slack $`s`$, move
the floor up by $`1 + \lfloor s / \text{step} \rfloor`$ steps.

```python
        floor += (1 + math.floor(round(slack, 6) / step)) * step
```

(`round(slack, 6)` drops solver noise such as a slack of 4.9999999 that is really 5.) The program
compares both ways over the top $60k of the NPV range:

```text
every floor 24,200..24,260: 61 solves, 5 different plans
  floor 24,200: NPV 24,235, risk 10,670.6, slack 35 -> jump 36 floors
  floor 24,236: NPV 24,241, risk 10,646.7, slack 5 -> jump 6 floors
  floor 24,242: NPV 24,242, risk 10,606.6, slack 0 -> jump 1 floors
  floor 24,243: NPV 24,252, risk 10,597.6, slack 9 -> jump 10 floors
  floor 24,253: NPV 24,260, risk 10,576.6, slack 7 -> jump 8 floors
with the jump: 5 solves, 5 plans, the same ones: True
the whole range 18,886..24,260 holds 5,375 floors
```

Sixty-one solves found 5 plans; with the jump, 5 solves found the same 5. Over the whole range,
5,375 floors became 65 solves, one per Pareto plan.

The second saving is the **early exit** of the 2009 paper: when a floor is infeasible, every higher
floor is infeasible too, because it asks for more. The sweep stops at the first one. The whole loop,
from `exact_frontier` in `frontier.py`:

```python
    while floor <= top_second.second + TOL:
        found = augmecon(model, first, second, floor, span, rho)
        solves += 1
        if found is None:
            break                                    # early exit: every higher floor fails too
        point, slack = found
        points.append(point)
        floor += (1 + math.floor(round(slack, 6) / step)) * step
    return points, solves
```

With two objectives, early exit rarely saves much: the payoff table already gives the top of the
range. It matters with three or more objectives, where the grid is a lattice of floors and one
infeasible floor rules out a whole row of harder ones, as the GAMS implementation does.

<!-- practice 2 -->

## Summary

- **Plain ε-constraint can return a weakly efficient plan.** With vegetation booked at NPV 0, 6 of
  11 plain answers were dominated by a plan with the same NPV and more risk removed.
- **Reward the floor's slack with a weight too small to cost any of the objective.** Floor row
  $`f_2 - s = \varepsilon`$ with $`s \ge 0`$, objective $`f_1 + (\rho / r_2)\, s`$. A reward of 1
  per $k instead gave up $945k of NPV.
- **Build the payoff table lexicographically.** The one-pass NPV end removed $7,481k of risk; the
  lexicographic end, with the same NPV, $8,662k.
- **Put the whole-number objective in the floor, step by one, and keep the reward below every gap:
  the frontier is exact.** Solves must also be optimal. GridCap small has 65 Pareto plans, none
  dominating another; risk is not whole $k, so the gap was checked after the run, and a two-pass
  sweep with no reward found the same 65.
- **Jump past floors the slack already covers, and stop at the first infeasible one.** 5,375 floors
  became 65 solves.

## Reference

| Symbol or name | Meaning |
| --- | --- |
| $`s \ge 0`$ | slack of the floor row: how far the floored objective lands above $`\varepsilon`$ |
| $`r_2`$ | range of the floored objective over the payoff table |
| $`\rho`$ | small reward weight ($`10^{-3}`$); the slack term is at most $`\rho`$ (not the allowed loss $`\delta_k`$ of lessons 8.2.1 and 8.2.2) |
| AUGMECON (2009) | floor as equality with slack, objective $`f_1 + (\rho / r_2) s`$, lexicographic payoff table, early exit |
| AUGMECON2 (2013) | adds the bypass: jump $`1 + \lfloor s / \text{step} \rfloor`$ floors after each solve |
| exact condition | integer coefficients on the floored objective, a step of 1, optimal solves, and a reward (at most $`\rho`$) below the closest gap in the maximized objective between neighbouring Pareto plans: automatic when that objective is whole numbers, otherwise a fact about the data, checked after the run |
| `augmecon(model, first, second, floor, span, rho)` | one augmented solve; returns (point, slack) or `None` |
| `exact_frontier(model, first, second, step)` | the whole frontier with bypass and early exit; returns (points, solves) |

**Further reading:** [OR-Tools, MathOpt basic example](https://developers.google.com/optimization/math_opt/basic_example) (`add_variable` with a lower bound, `add_linear_constraint` with `==`, `maximize`, the calls the augmented model adds); [OR-Tools source, `ortools/math_opt/python/model.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`delete_linear_constraint` and `delete_variable`, used to remove the floor row and the slack after each solve); [Mavrotas (2009), record and abstract at NTUA](https://dspace.lib.ntua.gr/xmlui/handle/123456789/19533) (AUGMECON: avoiding weakly Pareto-optimal solutions and redundant iterations); [GAMS model library, `epscm.gms`](https://gams.com/53/gamslib_ml/libhtml/gamslib_epscm.html) (AUGMECON in code: slack in the floor rows, the reward divided by each objective's range, the lexicographic payoff table and the jump on infeasibility); [GAMS model library, `epscmmip.gms`](https://gams.com/53/gamslib_ml/libhtml/gamslib_epscmmip.html) (AUGMECON2 on a two-objective knapsack: the bypass from the slack, and a step of 1 for the exact Pareto set; cites Mavrotas and Florios, 2013, Applied Mathematics and Computation 219(18), 9652–9669).

## Challenges

1. Set $`\rho = 10`$ on GridCap small with NPV in the floor and risk maximized. Predict whether the
   frontier keeps 65 points, and which points could change.
2. A third objective, crew-months used (to be minimized), joins NPV and risk. How many floors does the
   AUGMECON grid have, and where does early exit start to pay?
3. With risk in the floor instead of NPV, what would the bypass jump be after a slack of $340.5k on a
   step of $100k? Would the sweep still be exact?

## Design Note: Why Not Two Passes Instead of a Reward

A second way to break ties is the two-pass solve of lesson 8.2.2: find the best NPV at the floor,
then hold it and maximize risk. That needs no $`\rho`$ and no assumption about whole numbers, so
it is exact for any coefficients. It also costs two solves per floor instead of one. AUGMECON gets the same answer in one solve
whenever the reward, at most $`\rho`$, is below the smallest difference in the main objective
between plans. In lesson 8.3.1's orientation the main objective is NPV in whole $k, so that holds
by construction. In `exact.py` the main objective is risk, which is not whole numbers: the reward
could in principle trade up to $1 of risk for slack. On GridCap small the closest Pareto
neighbours differ by $91 of risk (lesson 8.3.1), and `exact.py`'s two-pass sweep found the same 65
plans, but that is a fact about this data, checked after the run. When you cannot bound the gap, use the two passes.
The course's `frontier.py` uses the reward for the sweep, and the two-pass form, `best_of`, for the
payoff table, where the extra solves are paid once.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**weak_points.py.** Builds the NPV-0 vegetation variant, prints the payoff table in one pass and
lexicographically, and compares plain and augmented answers at 11 floors (*Plain ε-Constraint Can
Return a Weakly Efficient Plan*, *Build the Payoff Table Lexicographically*). *Try:* Book only
trims at NPV 0, not clearings or widenings. Predict whether fewer floors give weakly efficient
answers.

- Program: [weak_points.py](src/weak_points.py)

**reward_scale.py.** Solves the $13,000k floor with the scaled reward and with a reward of 1 per $k
(*Reward the Floor's Slack*). *Try:* Use a reward of 0.1 per $k. Predict whether the answer moves
off lesson 8.3.1's plan.

- Program: [reward_scale.py](src/reward_scale.py)

**exact.py.** Generates GridCap small's whole frontier with NPV in the floor, step 1, then again
with two passes per floor and no reward, to check the gap condition (*Put the Whole-Number Objective
in the Floor*). *Try:* Run it with `step=10`. Predict how many plans it
finds and whether any is dominated.

- Program: [exact.py](src/exact.py)

**bypass.py.** Solves every floor of the top $60k of the NPV range, then the same range with the
jump (*Jump Past Floors the Slack Already Covers*). *Try:* Widen the range to start at 24,000.
Predict the number of solves each way.

- Program: [bypass.py](src/bypass.py)
