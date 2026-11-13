# 8.2.1 Hierarchical Objectives with Tolerances

Lesson 7.3.4 left GridCap's planners with two plans for the small portfolio. The plan with the
most NPV earns $24,260k and removes $10,577k of discounted failure cost (risk). The plan that
removes the most risk removes $16,086k and earns $18,886k. Lessons 8.1.1–8.1.2 blended the two
objectives into one with weights. GridCap's board asks for something else, in words:

> NPV is what the rate case is judged on. Keep it within 1% of the best NPV we can reach. Within
> that, remove as much risk as you can.

That request has no weights in it. It ranks the objectives (NPV first, risk second) and says how
much of the first one the second may spend (1%). This is a **lexicographic**, or **hierarchical**,
objective with a **tolerance**. Lesson 4.3.2 showed MathOpt's API for it, with total spend as the
second objective. This lesson is about the method itself: what the order means, what a tolerance
does to the second objective (measured, as a relative share and as an absolute amount), and how to
choose one. Lesson 8.2.2 then implements it three ways and checks that they agree. GridCap is a
fictional utility; its numbers come from a seeded generator, not from any real company.

## The Model

The start-year model of lessons 6.4.1–6.4.2, with two objectives in a fixed order.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups, each
a set of projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ (in $k, from
lesson 7.2.4); $`\text{rr}_{i,t}`$, the discounted risk it removes over the ten-year window (in $k,
from lesson 7.3.4); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k);
$`B_y`$, the budget of year $`y`$ ($k); $`a \ge 0`$, the **absolute tolerance** on NPV ($k), and
$`r \ge 0`$, the **relative tolerance** on NPV (a share of the best NPV).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objectives, in priority order.**

```math
\begin{aligned}
f_1(x) &= \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} && \text{(maximize first)} \\
f_2(x) &= \sum_{i \in P} \sum_{t \in T_i} \text{rr}_{i,t}\, x_{i,t} && \text{(maximize second)}
\end{aligned}
```

**Constraints.** Write $`X`$ for the plans that satisfy every rule of lesson 6.4.2:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

**The two passes.** A lexicographic objective is solved as a sequence of ordinary models. Pass 1
finds the best NPV, $`\Gamma_1`$. Pass 2 maximizes risk removed over the plans whose NPV is within
the allowed loss $`\delta_1`$ of $`\Gamma_1`$:

```math
\begin{aligned}
&\text{pass 1:} && \Gamma_1 = \max_{x \in X} f_1(x) \\
&\text{pass 2:} && \max_{x \in X} f_2(x) \quad \text{subject to} \quad f_1(x) \ge \Gamma_1 - \delta_1 && \text{(keep\_npv)} \\
&\text{where} && \delta_1 = \max\big(a,\; r \cdot |\Gamma_1|\big)
\end{aligned}
```

The row $`\text{keep\_npv}`$ is the only thing pass 2 adds to the model. Its name in the code is
`keep_npv`. With $`a = r = 0`$ it says "NPV stays at its best value", and the second objective can
only choose among plans that tie on NPV.

## A Lexicographic Order Lets a Later Objective Choose Only Among Plans the Earlier Ones Accept

The module's helper, `solve_levels`, runs the passes. Each objective is a `Level`: a name, a sense,
and its two tolerances (both 0 unless set). Lesson 8.2.2 opens the function; here only its results
matter. Five runs on the small portfolio:

```python
runs = {
    "NPV alone":                [Level("npv")],
    "NPV, then risk":           [Level("npv"), Level("risk")],
    "risk alone":               [Level("risk")],
    "risk, then NPV":           [Level("risk"), Level("npv")],
    "risk within 1%, then NPV": [Level("risk", rel_tol=0.01), Level("npv")],
}
```

```text
NPV alone                 NPV $ 24,260k  risk removed $10,576.6k  projects 27
NPV, then risk            NPV $ 24,260k  risk removed $10,576.6k  projects 27
risk alone                NPV $ 18,886k  risk removed $16,086.1k  projects 31
risk, then NPV            NPV $ 18,886k  risk removed $16,086.1k  projects 31
risk within 1%, then NPV  NPV $ 19,485k  risk removed $15,938.9k  projects 32
```

Read the first two rows together. With no tolerance, the risk pass is allowed only plans with NPV
exactly $24,260k, and it found none that removes more risk than the NPV plan already does. The same
holds the other way round: putting NPV second changed nothing about the risk plan. That is typical
of a model like this one. NPV and risk are sums of many different dollar amounts, so two different
plans almost never tie exactly on the first objective, and the second objective has nothing to
choose between. **With zero tolerance, a lexicographic objective is mostly a tie-breaker.**

The order is the planner's decision, and it decides everything. NPV first gives the NPV plan; risk
first gives the risk plan. The second objective never outvotes the first, however large its numbers
are. That is the difference from the weighted sums of lesson 8.1.1, where a large enough weight on
risk always wins.

The last row is the first sign of what a tolerance does. Allowing risk removed to fall by 1% of its
best (1% of $16,086.1k is $160.9k) let the NPV pass find a plan that gives up $147.2k of risk and
earns $599k more NPV.

## A Tolerance Turns the First Objective Into a Floor

The board's request, in code, is two levels: NPV with a 1% relative tolerance, then risk.

```python
levels = [Level("npv", rel_tol=0.01), Level("risk")]
out = solve_levels(sm, levels)
```

```text
pass 1: best NPV $24,260k, allowed loss $242.6k, floor $24,017.4k
pass 2: most risk removed with NPV >= floor: $12,750.5k
NPV plan  NPV $24,260k  risk removed $10,576.6k  projects 27
1% plan   NPV $24,019k  risk removed $12,750.5k  projects 27
```

Pass 1 finds $`\Gamma_1 = 24{,}260`$. The allowed loss is $`\delta_1 = 0.01 \times 24{,}260 = 242.6`$,
so the `keep_npv` row is $`f_1(x) \ge 24{,}017.4`$: a **floor** on NPV. From then on NPV is not an
objective anymore; it is a constraint. Pass 2 maximizes risk removed above that floor and finds a
plan with NPV $24,019k, $241k (0.99%) below the best, that removes $12,750.5k of risk. That is
$2,173.9k more risk removed than the NPV plan, 20.6% more, for less than 1% of NPV. This plan is
section 8's milestone: the lexicographic plan with a 1% NPV tolerance.

What changed between the two plans is what a planner will ask about:

```text
project  NPV plan  1% plan     NPV    risk  name
P004            -     2028    +116  +429.0  Plains circuit trim (A004)
P006            -     2031     +34  +605.1  Valley corridor widen (A006)
P011         2031     2030     +45   +54.5  Coast circuit trim (A011)
P014         2028        -    -195   -26.4  Coast circuit trim (A014)
P016         2030        -    -330   -85.8  Coast breaker bay replace (A016)
P018         2030     2031     -77    -8.0  Valley circuit clear (A018)
P020         2030        -     -79  -108.0  Ridge corridor widen (A020)
P027            -     2030    +245 +1,313.3  Coast substation transformer repair (A027)
```

Three projects leave the plan, three join it, and two start in a different year. The biggest single
move is P027, a transformer repair that removes $1,313.3k of risk. Each joining project has a
positive NPV, so the NPV plan did not leave it out for being unprofitable: within the budgets, that
money earned more NPV elsewhere. The 1% of slack is what lets pass 2 fund it.

**With a tolerance, the second pass can return a plan that a third pass would improve.** Pass 2
looks only at risk. If two plans removed exactly the same risk and both cleared the floor, pass 2
could return the one with less NPV, and that plan would be **dominated**: another plan is at least
as good on both objectives and better on one. A third pass settles it: maximize NPV again, with risk
kept at the value pass 2 reached.

```python
third = solve_levels(sm, levels + [Level("npv")]).plan        # pass 3: NPV again, risk kept at its best
```

```text
pass 3 (NPV again, risk kept): NPV $24,019k  risk removed $12,750.5k
```

On the small portfolio pass 3 changes nothing: the 1% plan is not dominated. The check costs one more
solve, and it is the lexicographic form of the problem lesson 8.3.2 (AUGMECON) solves inside a single
model.

## The Allowed Loss Is a Ceiling, and the Plan Moves in Steps

How much risk does each extra share of NPV buy? `tolerance_sweep.py` solves the same two levels
with eight relative tolerances and six absolute ones. "Allowed" is $`\delta_1`$, "taken" is the NPV
the final plan actually gives up, and "gained" is the risk removed beyond the NPV plan's $10,576.6k:

```text
tolerance  allowed  taken      NPV      risk   gained
    0.00%      0.0      0   24,260  10,576.6     +0.0
    0.10%     24.3     19   24,241  10,646.7    +70.1
    0.25%     60.6     25   24,235  10,670.6    +94.0
    0.50%    121.3    114   24,146  11,430.8   +854.1
    1.00%    242.6    241   24,019  12,750.5 +2,173.9
    2.00%    485.2    485   23,775  13,449.6 +2,873.0
    5.00%  1,213.0  1,156   23,104  14,837.1 +4,260.5
   10.00%  2,426.0  1,585   22,675  15,600.7 +5,024.0
     $10k     10.0      8   24,252  10,597.6    +20.9
     $50k     50.0     25   24,235  10,670.6    +94.0
    $100k    100.0     98   24,162  11,049.4   +472.7
  $242.6k    242.6    241   24,019  12,750.5 +2,173.9
    $500k    500.0    485   23,775  13,449.6 +2,873.0
  $1,000k  1,000.0    929   23,331  14,793.7 +4,217.0
```

Four things to read from this table:

- **The allowed loss is a ceiling, not a price.** Every "taken" is at or below its "allowed".
  At 10% the plan gives up $1,585k of the $2,426k it could: risk removed is already $15,600.7k,
  close to the risk plan's $16,086.1k, and no plan above the floor removes more.
- **The plan moves in steps.** Plans are made of whole projects, so the risk removed jumps from
  one plan to the next. A 0.25% tolerance ($60.6k) and a $50k one return the same plan, because no
  plan with more risk removed loses between $25k and $60.6k of NPV.
- **Equal allowed losses give equal plans, whatever their form.** 1% of $24,260k is $242.6k, and
  the relative 1% row and the absolute $242.6k row are the same plan. Pass 2 sees only the floor.
- **Each extra dollar of tolerance buys less.** The first $241k of NPV given up buys $2,173.9k of
  risk removed, about 9.0 dollars of risk per dollar of NPV. Going from 1% to 2% gives up $244k more
  for $699.1k more risk (2.9 per dollar), and from 5% to 10% $429k more for $763.5k (1.8 per dollar).

The sweep is the answer to give the board, rather than one plan. The tolerance is a business
decision, and this table shows what each choice costs and buys. It also shows that the 1% the board
asked for sits just past a large step: at 0.5% the gain is $854.1k, at 1% it is $2,173.9k.

<!-- practice 1 -->

## A Relative Tolerance Follows the Scenario; an Absolute One Stays Put

A relative tolerance is a share of $`|\Gamma_1|`$, so its dollar value moves whenever the best NPV
moves: in another budget scenario, another portfolio, or next year's data. An absolute tolerance is
the same dollar amount everywhere. `scenario_tolerance.py` scales every year's budget to 85%, 100%
and 120% and solves both ways, with the 1% and the $242.6k that agreed on the base case:

```python
scenario = replace(small, budget={y: round(b * share) for y, b in small.budget.items()})
```

```text
budgets  tolerance  best NPV  allowed  taken  risk removed
x0.85          1%    21,262    212.6    180      9,645.1
x0.85     $242.6k    21,262    242.6    229     10,344.2
x1.0           1%    24,260    242.6    241     12,750.5
x1.0      $242.6k    24,260    242.6    241     12,750.5
x1.2           1%    29,670    296.7    292     13,521.0
x1.2      $242.6k    29,670    242.6    233     13,328.5
```

With smaller budgets, 1% is only $212.6k, and the plan removes $699.1k less risk than the fixed
$242.6k allows. With larger budgets, 1% grows to $296.7k and the relative tolerance removes more.
Neither is right in general; they answer different requests:

- **Relative** when the request is a share: "no more than 1% of the best NPV". It scales with the
  scenario, so the planner's intent holds in every scenario of a study.
- **Absolute** when the request is an amount: "no more than $250k of NPV", for example a figure
  committed in a rate case. It means the same dollars in every scenario.

Two cases follow from the formula $`\delta = \max(a, r \cdot |\Gamma|)`$. When $`\Gamma`$ is close
to zero (an objective such as net cost, which can be near zero or negative), a relative tolerance
allows almost nothing, and only an absolute one gives room. The absolute value keeps the allowed loss
positive when $`\Gamma`$ is negative. When both tolerances are set, the larger allowed loss applies,
as lesson 4.3.2 showed for MathOpt; Gurobi's documentation says the same (lesson 8.2.2).

<!-- practice 2 -->

## Summary

- **A lexicographic order lets a later objective choose only among plans the earlier ones accept.**
  With zero tolerance on GridCap, the second objective changed nothing: exact ties are rare.
- **A tolerance turns the first objective into a floor.** 1% of NPV ($242.6k) bought $2,173.9k more
  risk removed (20.6%); a third pass confirmed no plan beats it on both objectives.
- **The allowed loss is a ceiling, and the plan moves in steps.** Show planners the sweep: the gain
  per dollar falls from about 9.0 to 1.8 as the tolerance grows.
- **A relative tolerance follows the scenario; an absolute one stays put.** Pick the form that
  matches how the request was stated.

## Reference

| Term | Meaning |
| --- | --- |
| lexicographic (hierarchical) objective | objectives in a strict order; each later one chooses only among plans the earlier ones accept |
| pass | one solve of the sequence: optimize one objective with the earlier ones kept as rows |
| $`\Gamma_k`$ | the best value of objective $`k`$ found in its pass |
| tolerance (degradation allowance) | how far an objective may fall from $`\Gamma_k`$ to make room for later ones |
| absolute tolerance $`a`$ | allowed loss in the objective's own units |
| relative tolerance $`r`$ | allowed loss as a share of $`\lvert\Gamma_k\rvert`$ |
| allowed loss $`\delta_k`$ | $`\max(a, r \cdot \lvert\Gamma_k\rvert)`$ |
| floor (kept row) | $`f_k(x) \ge \Gamma_k - \delta_k`$ for a maximized objective, $`f_k(x) \le \Gamma_k + \delta_k`$ for a minimized one |
| dominated plan | another plan is at least as good on every objective and better on one |

| GridCap small | NPV ($k) | risk removed ($k) |
| --- | --- | --- |
| NPV alone, or NPV then risk | 24,260 | 10,576.6 |
| risk alone, or risk then NPV | 18,886 | 16,086.1 |
| NPV within 1%, then risk (the milestone) | 24,019 | 12,750.5 |

**Further reading.** OR-Tools,
[`model_parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py):
the `ObjectiveParameters` docstring, which defines $`\Gamma`$, the passes in priority order and both
degradation tolerances. OR-Tools,
[`objectives.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/objectives.py):
priorities and auxiliary objectives. Gurobi,
[Multiple Objectives](https://docs.gurobi.com/projects/optimizer/en/current/features/multiobjective.html):
hierarchical passes and how the relative and absolute tolerances relax each one. GAMS Model Library,
[`epscm.gms`](https://gams.com/53/gamslib_ml/libhtml/gamslib_epscm.html): the augmented ε-constraint
method of Mavrotas (2009, the resource library's section 8 reference), which builds its payoff table
with lexicographic passes, one objective fixed before the next; lesson 8.3.2 builds on it.

## Challenges

1. The board changes its mind: risk first, with a 2% tolerance, then NPV. Before running anything,
   which rows does each pass add, and in which units is the 2% measured?
2. Without solving, name an absolute tolerance that must return the same plan as the 0.10% row, and
   say why it must.
3. A third objective, the least total spend, is added after risk. With no tolerance on risk, when
   can it change the plan at all?

## Design Note: A Tolerance Is a Question for the Planner, Not a Solver Setting

It is tempting to treat the tolerance like a gap or a feasibility tolerance: a small number an
engineer sets once. It is not. It states how much of the first objective the organization will give
up for the second, and the sweep shows that answer can move risk removed by thousands of dollars. Ask
the planner for it, in the form they think in (a share or an amount), record it with the run, and
show the sweep around it so they see what the next step would buy.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**orders.py.** Each objective alone, both lexicographic orders with no tolerance, and risk first with
a 1% tolerance (*A Lexicographic Order Lets a Later Objective Choose*). *Try:* Put NPV first with
`abs_tol=1`. Predict whether the plan moves.

- Program: [orders.py](src/orders.py)

**one_percent.py.** The milestone plan: NPV within 1%, then risk; the projects that change; and the
third pass (*A Tolerance Turns the First Objective Into a Floor*). *Try:* Change the tolerance to
0.5% and predict how many projects change.

- Program: [one_percent.py](src/one_percent.py)

**tolerance_sweep.py.** Relative and absolute NPV tolerances against the risk they buy (*The Allowed
Loss Is a Ceiling*). *Try:* Add a 3% row and predict whether its gain lies between the 2% and 5% rows.

- Program: [tolerance_sweep.py](src/tolerance_sweep.py)

**scenario_tolerance.py.** One relative and one absolute tolerance on three budget scenarios (*A
Relative Tolerance Follows the Scenario*). *Try:* Add a scenario at 70% of the budgets and predict
which form allows the larger loss.

- Program: [scenario_tolerance.py](src/scenario_tolerance.py)

**lex_model.py** builds the model and its three objectives; **lexicographic.py** runs the passes.

- Library: [lex_model.py](src/lex_model.py)
- Library: [lexicographic.py](src/lexicographic.py)
