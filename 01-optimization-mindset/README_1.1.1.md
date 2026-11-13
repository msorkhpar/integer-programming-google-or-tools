# 1.1.1 Decisions, Objectives and Constraints: Turning a Planner's Question into a Model

GridCap's capital planning team has $7.39M to commit this cycle and eight candidate projects that
would cost $13.44M together. The director's question is short: *which projects do we fund?* An
analyst sorts the list by value per dollar and funds from the top until the money runs out. The
plan is cheap to make and easy to explain, and it breaks two of the utility's own rules. This
lesson turns the director's question into a model: the decisions, one number that ranks every
plan, and the rules that say which plans are allowed. Four rules, one per heading.

Here is the tiny GridCap portfolio. All money in this course is in thousands of dollars ($k).

```python
def show(portfolio: Portfolio) -> None:
    print(f"capital budget: ${portfolio.capital_budget:,}k")
    print(f"{'id':5} {'program':13} {'capex $k':>9} {'NPV $k':>7}  rules")
    for p in portfolio.projects:
        print(f"{p.project_id:5} {p.program:13} {p.capex:>9,} {p.value:>7,}  {rules_of(p)}")
```

```text
capital budget: $7,390k
id    program        capex $k  NPV $k  rules
P001  distribution      2,150   1,386
P002  transmission      2,730     871  must-do
P003  transmission      2,470     576
P004  transmission      3,000   2,120  needs P003
P005  vegetation          250     123
P006  distribution      1,970   1,247  alternative in G006
P007  distribution        290     265  alternative in G006
P008  vegetation          580     137
all eight: $13,440k
```

*Capex* is what a project costs over its life. *NPV* (net present value) is what it is worth to
the utility, in today's dollars, after paying for it; section 7 shows where these numbers come
from. The *rules* column holds the business rules this lesson turns into constraints.

## A Model Starts From the Decisions You Control, One Variable per Choice

The director cannot choose the budget, the costs or the values. Those are **data**. What the team
does control is, for each project, *fund it or not*. Each of those choices is a **decision
variable**, and a plan is one value for every variable.

In code, a plan starts as a set of project ids. The moment you want to write the rules as
arithmetic, write it as a vector with one 0/1 entry per project instead:

```python
def to_vector(plan: set[str]) -> list[int]:
    return [1 if pid in plan else 0 for pid in ids]
```

```text
ids: P001 P002 P003 P004 P005 P006 P007 P008
x:   1    1    0    0    0    1    0    0
```

Written mathematically, $`x_i = 1`$ if project $`i`$ is funded and $`x_i = 0`$ if it is not. A
variable that can only be 0 or 1 is a **binary** variable, and almost every capital planning
model in this course is built from them.

The common mistake is to start from the data ("we have NPVs, let's rank them") rather than from
the decision. Ranking answers *which project is best on its own*. The director asked *which
combination is best*, and the best combination can leave out the project with the top NPV, as
you will see below.

## The Objective Is One Number That Ranks Every Plan

To compare plans, the model needs one number per plan, the **objective**. Here it is the total
NPV of the funded projects, and we want it as large as possible:

```math
\text{maximize} \quad \sum_{i} \text{npv}_i \, x_i
```

```python
def objective(x: list[int]) -> int:
    return sum(p.value * xi for p, xi in zip(tiny.projects, x))
```

```text
objective = 3,504, spend = 6,850 <= 7,390
```

One number is a strong demand. "Maximize value and minimize risk" is two numbers, and a model
cannot rank plans with two numbers until you say how they trade off. Section 8 is about exactly
that. Until then each model has one objective, and everything else the planners care about has
to be either part of that number or a constraint.

What goes wrong when the objective is not the thing people care about? The model gives you the
best plan for the wrong question. Here is the best plan, with every rule below respected, when
GridCap counts *projects funded* instead of NPV:

```text
most projects: ['P001', 'P002', 'P005', 'P007', 'P008'] count 5 value $2,782k
```

It swaps the transformer replacement P006 for the cheaper repair P007 and adds a vegetation
project. Five projects instead of four, and $845k less value than the plan you will meet below.
A progress report that counts projects would call that an improvement.

## Constraints Decide Which Plans Are Allowed, and Business Rules Are Constraints Too

A **constraint** is a rule every allowed plan must satisfy. The budget is the obvious one:

```math
\sum_{i} \text{capex}_i \, x_i \le 7{,}390
```

Two plans, checked against it:

```python
for plan in ({"P001", "P002", "P006"}, {"P002", "P003", "P004"}):
    verdict = "within budget" if cost(plan) <= tiny.capital_budget else "over budget"
    print(sorted(plan), f"cost ${cost(plan):,}k", f"value ${value(plan):,}k", verdict)
```

```text
['P001', 'P002', 'P006'] cost $6,850k value $3,504k within budget
['P002', 'P003', 'P004'] cost $8,200k value $3,567k over budget
```

The second plan is worth more and is not allowed, so it is not a candidate at all. A plan that
satisfies every constraint is **feasible**. Optimization looks for the best feasible plan, never
the best plan.

The budget is not the only rule. The *rules* column holds three more, and each one is a
constraint as real as the budget:

- **Must-do.** P002 is a compliance project. Every allowed plan funds it: $`x_{P002} = 1`$.
- **Parent and child.** P004 (a breaker bay replacement) only makes sense if P003 (the tower set it
  sits on) is funded too. Funding the child without the parent is not allowed:
  $`x_{P004} \le x_{P003}`$.
- **Alternatives.** P006 replaces a substation transformer and P007 repairs the same one. The
  utility does one or neither: $`x_{P006} + x_{P007} \le 1`$.

Pause on the parent-child rule. Why is it $`x_{P004} \le x_{P003}`$ and not
$`x_{P004} = x_{P003}`$? Because the parent may be funded alone. The equation would force them
to go together in both directions, which is a different rule (an all-or-nothing bundle, lesson
6.5.2).

A rule that lives only in a planner's head is the costliest kind. The model has never heard of
it, so it will happily break it, and the plan that comes back looks optimal and is useless.
Section 6 is a catalogue of these rules and how to write each one.

<!-- practice 1 -->

## Checking a Plan Is Cheap; Finding the Best One Is Not

Back to the analyst's spreadsheet. Funding the best value per dollar first gives:

```python
def greedy() -> set[str]:
    plan: set[str] = set()
    for p in sorted(tiny.projects, key=lambda p: p.value / p.capex, reverse=True):
        if sum(by_id[i].capex for i in plan) + p.capex <= budget:
            plan.add(p.project_id)
    return plan
```

```text
greedy ['P001', 'P004', 'P005', 'P007', 'P008'] value $4,031k breaks a rule
```

It is within budget, but it funds P004 without its parent P003 and leaves out the must-do P002.
The greedy rule only knows about the budget. It cannot know about the other rules unless someone
writes them in, and once they are written in, "sort and fill" no longer works.

With eight projects there are only $`2^8 = 256`$ plans, so we can check every one:

```python
for k in range(len(by_id) + 1):
    for combo in combinations(by_id, k):
        checked += 1
        plan = set(combo)
        if allowed(plan) and (best is None or value(plan) > value(best)):
            best = plan
```

```text
best   ['P001', 'P002', 'P005', 'P006'] value $3,627k cost $7,100k
plans checked: 256
```

The best allowed plan is worth $3,627k. The greedy plan's $4,031k is not a better answer. It is
an answer to a question without the must-do and the parent rule.

Checking one plan takes a few additions. The trouble is the number of plans: it doubles with
every project. At a million plans a second:

```text
  8 projects: 2.56e+02 plans, 8.12e-12 years
 20 projects: 1.05e+06 plans, 3.33e-08 years
 40 projects: 1.10e+12 plans, 3.49e-02 years
 60 projects: 1.15e+18 plans, 3.66e+04 years
400 projects: 2.58e+120 plans, 8.19e+106 years
```

Forty projects take about two weeks, sixty take longer than recorded history, and GridCap's
medium portfolio has 400. A solver does not check every plan. It proves that whole regions of
plans cannot beat the best one found so far and skips them. How it does that is section 3.

<!-- practice 2 -->

## The Model

Everything this lesson built, as one model. Every allowed plan is a solution of it, and the
optimal plan is its best solution.

**Sets.** $`P`$ the candidate projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$
the child projects, each with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups, each a set
of projects (on GridCap tiny, $`\{P006, P007\}`$).

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ for each project ($k); $`B`$, the capital
budget ($7,390k on GridCap tiny).

**Variables.** $`x_i \in \{0, 1\}`$ for each $`i \in P`$: 1 if project $`i`$ is funded.

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

On GridCap tiny its optimum is the brute-force plan, `['P001', 'P002', 'P005', 'P006']`, worth
$3,627k. Lesson 1.1.3 hands this same model to a solver.

## Summary

- **A model starts from the decisions you control.** Write each yes/no choice as a binary
  variable; a plan is one value for each.
- **The objective is one number that ranks every plan.** A second goal is either folded into that
  number or written as a constraint, or the model answers a different question.
- **Constraints decide which plans are allowed.** Must-do, parent-child and alternative rules are
  constraints like the budget, and a rule the model does not know about is one it will break.
- **Checking a plan is cheap; finding the best one is not.** Greedy rules ignore everything but
  one constraint, and brute force doubles with every project.

## Reference

| Term | Meaning | In this lesson |
| --- | --- | --- |
| Data (parameter) | A number the decision maker cannot choose | capex, NPV, the $7,390k budget |
| Decision variable | A number the model chooses | $`x_i \in \{0, 1\}`$, fund project $`i`$ or not |
| Objective | The one number that ranks plans | $`\sum_i \text{npv}_i x_i`$, maximized |
| Constraint | A rule every allowed plan satisfies | budget, must-do, parent-child, alternatives |
| Feasible plan | A plan that satisfies every constraint | `['P001', 'P002', 'P006']` |
| Optimal plan | A feasible plan no other feasible plan beats | `['P001', 'P002', 'P005', 'P006']` |

| Business rule | Constraint on binaries |
| --- | --- |
| Project $`i`$ is must-do | $`x_i = 1`$ |
| Child $`c`$ needs parent $`p`$ | $`x_c \le x_p`$ |
| At most one of an alternative group $`G`$ | $`\sum_{i \in G} x_i \le 1`$ |
| Spend within budget $`B`$ | $`\sum_i \text{capex}_i x_i \le B`$ |

**Further reading:** [The Knapsack Problem (OR-Tools)](https://developers.google.com/optimization/pack/knapsack) (the budget row on its own is a knapsack, which OR-Tools solves for 50 items by branch and bound); [Get Started with OR-Tools for Python](https://developers.google.com/optimization/introduction/python) (the same pieces, variables, constraints and an objective, as the steps of an OR-Tools program); [Hands-On Mathematical Optimization with Python, Chapter 1](https://mobook.github.io/MO-book/notebooks/01/01.00.html) (decision variables, objective and constraints, and why modeling is iterative); [MO-book 1.1, A first production planning problem](https://mobook.github.io/MO-book/notebooks/01/01-production-planning.html) (the same three steps on a production plan).

## Challenges

1. The director asks to "fund as many vegetation projects as possible, then maximize NPV". Is that
   one objective or two? How would you write it?
2. Change the alternative rule to "exactly one of P006 and P007". What does the utility lose, and
   when would that rule be right?
3. Find a greedy rule (some other sort order) that returns the optimal plan for the tiny
   portfolio. Would you trust it on the small one?

## Design Note: Why the Rules Go Into the Model, Not Into a Post-Check

A tempting shortcut is to let a simple method propose a plan and then reject it if it breaks a
rule. On GridCap that rejects the greedy plan and leaves you with nothing to offer. Writing the
rules as constraints costs modeling time up front, and in return the solver only ever proposes
plans the utility can use, and can prove that none of them is better than the one it returns.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**portfolio_table.py.** Prints the tiny GridCap portfolio the lesson opens with. *Try:* Change `generate("tiny")` to `generate("small")`. How many projects and which rules appear?

- Program: [portfolio_table.py](src/portfolio_table.py)

**as_vector.py.** Writes a plan as a 0/1 vector and computes its objective and spend (*A Model Starts From the Decisions You Control*). *Try:* Change the plan passed to `to_vector` to one that funds P004 alone. Predict the objective and the spend before you run it.

- Program: [as_vector.py](src/as_vector.py)

**plan_value.py.** Checks two plans against the budget (*Constraints Decide Which Plans Are Allowed*). *Try:* Add a third plan to the loop that you think is allowed and worth more than both. Is it?

- Program: [plan_value.py](src/plan_value.py)

**greedy_vs_best.py.** Compares the value-per-dollar greedy plan with brute force over all 256 plans (*Checking a Plan Is Cheap*). *Try:* Sort the greedy by NPV alone instead of NPV per dollar (the `key=` in `greedy`). Predict whether its plan becomes allowed.

- Program: [greedy_vs_best.py](src/greedy_vs_best.py)

**wrong_objective.py.** Finds the best plan when the objective counts projects instead of NPV (*The Objective Is One Number*). *Try:* Make the objective count only vegetation projects. Which plan do you expect?

- Program: [wrong_objective.py](src/wrong_objective.py)

**growth.py.** Prints how long brute force would take as the portfolio grows. *Try:* Add 30 and 50 to the list of sizes. Where does brute force stop being usable for you?

- Program: [growth.py](src/growth.py)
