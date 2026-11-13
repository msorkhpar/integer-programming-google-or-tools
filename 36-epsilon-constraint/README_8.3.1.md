# 8.3.1 The ε-Constraint Method

GridCap's planners have two plans from lesson 7.3.4. The NPV plan earns $24,260k of NPV and removes $10,577k of discounted failure risk; the risk
plan removes $16,086k and earns $18,886k. Now the board brings a question in its own words: "We told
the regulator we would remove at least $13 million of failure risk over the window. What is the most
NPV we can keep while doing that?"

A weighted sum (lesson 8.1.1) cannot take that
question as asked. It wants a price, so many dollars of NPV per dollar of risk, and then picks
whatever plan that price favors, which may remove $11 million or $15 million. The board did not name
a price. It named a floor. The **ε-constraint method** turns the question into a model directly:
keep one objective as the objective, and make the other a constraint with a floor $`\varepsilon`$
(the Greek letter epsilon, by tradition). This lesson builds it on GridCap small in five rules.

GridCap is a fictional utility generated for this course; its assets, projects and budgets describe
no real company.

## Keep One Objective, and Turn the Other Into a Floor

The two objectives are lesson 7.3.4's: the plan's NPV, $`\sum \text{npv}_{i,t}\, x_{i,t}`$, and the
risk it removes, $`\sum \text{rr}_{i,t}\, x_{i,t}`$. The ε-constraint problem for the board's
question maximizes NPV and adds one row: risk removed must be at least $`\varepsilon`$. Everything
else is the start-year model of lesson 6.4.2, unchanged.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k, whole
numbers); $`\text{rr}_{i,t}`$, the discounted risk it removes over the ten-year window if started in
$`t`$ ($k, lesson 7.3.4); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k);
$`B_y`$, the budget of year $`y`$ ($k); $`\varepsilon`$, the least risk the plan must remove ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \sum_{t \in T_i} \text{rr}_{i,t}\, x_{i,t} &\ge \varepsilon && && \text{(eps\_risk)} \quad \leftarrow \text{this lesson} \\
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The module's `objectives.py` builds the rows of lesson 6.4.2 and sets no objective; it hands back
the two objectives as MathOpt linear expressions, `two.npv` and `two.risk`. (MathOpt is the
OR-Tools modeling layer of section 4: `add_linear_constraint` adds a row, `maximize` sets the
objective, and `solve` runs a solver, here HiGHS at a zero gap.) The ε row is then one line:

```python
floor = 13_000                        # ε: risk removed must be at least this, $k
row = two.model.add_linear_constraint(two.risk >= floor, name="eps_risk")
two.model.maximize(two.npv)
result = solve(two.model)
```

```text
max NPV s.t. risk removed >= $13,000k: OPTIMAL
  NPV $23,815k, risk removed $13,221k, 29 projects
  the floor's slack: $221k of risk above ε
```

That is the board's answer: keeping the $13 million promise costs $445k of NPV against the NPV plan
($24,260k − $23,815k). Notice that the plan removes $221k more than it was asked to. The floor is a
minimum, not a target. Projects come whole, so the best plan above $13,000k need not land on it.

Which objective becomes the floor is a modeling choice. Put the one the stakeholder states as a
commitment ("at least $13M of risk", "no less than 95% of the best NPV") in the floor, and the one
they want as much of as possible in the objective.

## The Payoff Table Sets the Range of ε

Not every $`\varepsilon`$ is worth trying. Solve each objective alone first. The two plans, each
scored on both objectives, form the **payoff table**:

```python
npv_plan, risk_plan = payoff_table(two.model, two.npv, two.risk)
```

```text
payoff table      |   NPV $k | risk removed $k
max NPV plan      |   24,260 |          10,577
max risk plan     |   18,886 |          16,086
risk >=  8,000: NPV $24,260k, risk $10,577k
risk >= 10,576: NPV $24,260k, risk $10,577k
risk >= 14,000: NPV $23,670k, risk $14,064k
risk >= 16,086: NPV $18,886k, risk $16,086k
risk >= 16,200: no plan reaches it
```

The table fixes the useful range of the floor, from the NPV plan's risk ($10,577k) to the most risk
any plan can remove ($16,086k):

- **Below the range** the floor does nothing. At $8,000k the NPV plan already clears it, so the
  answer is the NPV plan.
- **Inside the range** each floor gives a plan between the two ends (at $14,000k: NPV $23,670k).
- **At the top** the floor forces the risk plan itself.
- **Above the range** no plan can remove that much risk. The solve finds no plan, and the function
  returns `None` instead of a plan:

```python
def epsilon_constraint(model, first, second, floor: float) -> Point | None:
    """Plain ε-constraint: maximize `first` subject to `second >= floor`. None if no plan reaches it."""
    row = model.add_linear_constraint(second >= floor, name="eps_floor")
    model.maximize(first)
    result = solve(model)
    model.delete_linear_constraint(row)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return score(first, second, result.variable_values())
```

The row is added, the model is solved, and the row is deleted again with
`delete_linear_constraint`, so one model serves every floor. The function is written for any two
objectives, both maximized: `first` is the one the solve maximizes, `second` the one held at the
floor. Lesson 9.2.3 uses the same method for a budget-value curve.

<!-- practice 1 -->

## Every Answer Is at Least Weakly Pareto-Optimal

Three words, defined here because the rest of the section depends on them. Both objectives are
maximized.

- Plan $`A`$ **dominates** plan $`B`$ when $`A`$ is at least as good on both objectives and better
  on at least one.
- A plan is **Pareto-optimal** (also called *efficient*) when no feasible plan dominates it. The set
  of Pareto-optimal plans, drawn as points (NPV, risk), is the **Pareto frontier**.
- A plan is **weakly efficient** when no feasible plan is *strictly* better on *both* objectives.
  Every Pareto-optimal plan is weakly efficient, but not the other way round: a weakly efficient
  plan can be dominated by a plan that ties it on one objective and beats it on the other.

The ε-constraint answer is always at least weakly efficient. Suppose plan $`Q`$ were strictly better
on both objectives than the answer $`A`$. Then $`Q`$ removes more risk than $`A`$, which is at least
$`\varepsilon`$, so $`Q`$ satisfies the floor; and $`Q`$ has more NPV than $`A`$. So $`A`$ was not
the best plan with risk at least $`\varepsilon`$, a contradiction.

When the ε problem has only one optimal plan, that plan is Pareto-optimal: a plan dominating it would
satisfy the floor and have at least its NPV, so it would be a second optimal plan. When the problem
has several optimal plans that tie on NPV and differ in risk, the solver may return the one with
less risk, which another optimal plan dominates. Lesson 8.3.2 shows this happening on a GridCap
variant, and fixes it.

## ε-Constraint Reaches Plans No Weighted Sum Can

Lesson 8.1.2 showed that a weighted sum only finds **supported** Pareto points: those that are
optimal for some positive weights, which are the points on the upper-right convex hull of the
frontier, its corners and any point lying exactly on a segment between two corners. A Pareto-optimal
plan that sits in a dent of the frontier, below the straight line joining two neighbours, is
**unsupported**, and no choice of weights picks it.

The ε-constraint has no such blind spot. The floor cuts away every plan below it, and the best NPV
among the plans that remain can sit in a dent. The program below lists all 65 Pareto-optimal plans
of GridCap small (lesson 8.3.2 shows how `exact_frontier` finds them all), then sweeps the risk floor
over a grid of 5, 11 and 21 evenly spaced values from the NPV plan's risk to the risk plan's:

```python
for n in (5, 11, 21):
    floors = grid(npv_plan.second, risk_plan.second, n)          # risk floors, both ends included
    points = set()
    for floor in floors:
        p = epsilon_constraint(two.model, two.npv, two.risk, floor)
        points.add((round(p.first), round(p.second, 3)))
```

```text
Pareto-optimal plans: 65, of which a weighted sum reaches 8
 5 floors:  5 different plans,  5 Pareto-optimal,  2 unsupported (no weighted sum finds them)
11 floors: 11 different plans, 11 Pareto-optimal,  6 unsupported (no weighted sum finds them)
21 floors: 20 different plans, 20 Pareto-optimal, 14 unsupported (no weighted sum finds them)
```

Only 8 of the 65 Pareto-optimal plans are supported. Even the 5-floor sweep found two unsupported
plans, and every plan any sweep returned is on the frontier. The board's $13,000k plan of the first
section is one of the unsupported ones (lesson 8.3.3's table marks it): a weighted sum would never
have offered it, whatever the weights.

<!-- practice 2 -->

## A Sweep Finds at Most One Plan per Floor, So Its Steps Must Fit the Data

A common summary says "sweeping ε gives the exact Pareto frontier". The output above says otherwise.
Each floor returns one plan, so 11 floors find at most 11 of the 65 plans, and 21 floors found only
20, because two floors fell between the same pair of neighbours and returned the same plan.

A floor sweep finds *every* Pareto plan only when its steps are finer than the gaps in the data.
Sort the Pareto plans by risk. Plan $`k`$ is the answer for every floor above plan $`k-1`$'s risk
and up to its own, so a grid misses it when no floor lands in that interval. The same program
measures the narrowest interval:

```text
closest neighbours on the frontier differ by $91 of risk; a risk grid that cannot miss a plan needs 60,544 floors
```

Two neighbouring Pareto plans differ by $91 of discounted risk on a range of more than $5.5 million.
A grid on risk with steps that fine needs over 60,000 solves, and on other data the narrowest gap
could be smaller still, with no way to know it before the frontier is found. So the claim is true
only with a step fine enough for the data. Lesson 8.3.2 gets the same 65 plans in 65 solves, by
putting NPV, whose values are whole $k, in the floor and stepping by $1k, and by skipping floors that
cannot change the answer.

## Summary

- **Keep one objective, and turn the other into a floor.** Maximize NPV subject to risk removed
  $`\ge \varepsilon`$ and every rule of the model. On GridCap small, a $13,000k floor keeps $23,815k
  of NPV and removes $13,221k.
- **The payoff table sets the range of ε.** Below the NPV plan's risk the floor does nothing; above
  the most removable risk ($16,086k) no plan exists.
- **Every answer is at least weakly Pareto-optimal**, and Pareto-optimal when the ε problem has a
  single optimal plan.
- **ε-constraint reaches plans no weighted sum can.** 57 of GridCap small's 65 Pareto plans are
  unsupported; an 11-floor sweep found 6 of them.
- **A sweep finds at most one plan per floor, so its steps must fit the data.** 21 floors found 20
  of 65 plans; a risk grid sure to find them all needs 60,544 floors.

## Reference

| Term | Meaning |
| --- | --- |
| ε-constraint problem | $`\max f_1(x)`$ subject to $`f_2(x) \ge \varepsilon`$ and the model's rules |
| payoff table | each objective's best plan, scored on every objective; its columns give the range of ε |
| dominates | at least as good on every objective and better on one |
| Pareto-optimal (efficient) | no feasible plan dominates it |
| unsupported point | a Pareto point no weighting returns, even with a zero weight; it lies strictly below a hull segment |
| weakly efficient | no feasible plan is strictly better on every objective |
| supported point | a Pareto point optimal for some positive weights: on the upper-right convex hull, a corner or a point exactly on a segment between two corners (lesson 8.1.2) |
| `epsilon_constraint(model, first, second, floor)` | one ε solve on any MathOpt model; `None` when no plan reaches the floor |
| `grid(low, high, n)` | `n` evenly spaced floors, both ends included |

**Further reading:** [OR-Tools, MathOpt basic example](https://developers.google.com/optimization/math_opt/basic_example) (building a model, `add_linear_constraint`, `maximize`, `solve` and reading the termination reason, the calls every ε solve makes); [OR-Tools source, `ortools/math_opt/python/model.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`delete_linear_constraint`, which lets one model serve every floor); [Mavrotas (2009), *Effective implementation of the ε-constraint method in Multi-Objective Mathematical Programming problems*, Applied Mathematics and Computation 213(2), 455–465, record and abstract at NTUA](https://dspace.lib.ntua.gr/xmlui/handle/123456789/19533) (the ε-constraint method as an a posteriori, generating method, and its weakly efficient answers); [GAMS model library, `epscm.gms`](https://gams.com/53/gamslib_ml/libhtml/gamslib_epscm.html) (a complete ε-constraint implementation with a payoff table and a grid of floors).

## Challenges

1. Swap the roles: maximize risk removed subject to NPV $`\ge 23{,}000`$. Predict whether the
   answer is on the frontier, and whether its NPV lands exactly on 23,000.
2. The regulator adds a second commitment: at least $2,000k of the risk removed must be in the
   Coast region. Write the extra row. How many floors does a sweep now have to choose?
3. A grid of 11 floors returned 11 different plans on GridCap small. Is there a number of floors
   above which a grid on risk is sure to find no new plan? What does it depend on?

## Design Note: Why Not Just Report the Two Ends

Many planning tools show the NPV plan and the risk plan and stop. The payoff table is cheap, two
solves, and it does bound everything. But the interesting plans are in between: on GridCap small,
$445k of NPV buys $2,644k more risk removed at the $13,000k floor, while the last $485k of risk on
the way to the risk plan costs $3,789k (lesson 8.3.3 measures each step). A planner who sees only
the ends cannot see that the first steps are cheap and the last ones dear. The floor form is also the
one the board speaks in, so the model's answer can be read back to them as their own sentence.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**one_floor.py.** Solves the board's question: the most NPV with at least $13,000k of risk removed
(*Keep One Objective, and Turn the Other Into a Floor*). *Try:* Raise the floor to $15,500k.
Predict whether the slack above the floor grows or shrinks.

- Program: [one_floor.py](src/one_floor.py)

**range_of_eps.py.** Prints the payoff table and solves five floors below, inside, at and above its
range (*The Payoff Table Sets the Range of ε*). *Try:* Add a floor of $10,577k, a hair above the NPV
plan's risk of $10,576.65k. Predict whether the answer is still the NPV plan.

- Program: [range_of_eps.py](src/range_of_eps.py)

**grid_vs_exact.py.** Sweeps 5, 11 and 21 risk floors and compares what they find with all 65
Pareto plans (*ε-Constraint Reaches Plans No Weighted Sum Can*, *A Sweep Finds at Most One Plan per
Floor*). *Try:* Sweep 41 floors. Predict how many different plans you get.

- Program: [grid_vs_exact.py](src/grid_vs_exact.py)

**objectives.py.** The start-year model of lesson 6.4.2 with no objective, and the two objective
expressions.

- Library: [objectives.py](src/objectives.py)

**frontier.py.** The module's frontier library: `payoff_table`, `epsilon_constraint`, `augmecon`,
`grid`, `exact_frontier` and the dominance checks.

- Library: [frontier.py](src/frontier.py)
