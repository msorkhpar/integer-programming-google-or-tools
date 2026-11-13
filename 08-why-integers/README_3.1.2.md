# 3.1.2 The Integrality Gap, Measured on GridCap

GridCap's finance partner has read lesson 3.1.1's warning and asks a sharper question. "Your LP says
the small portfolio could be worth $25,451k. Your MILP says $25,336k. Which number goes in the
board pack, and how much should I trust the other one?" The answer is that both are useful, for
different reasons: one is a plan, the other is a ceiling, and the distance between them has a name.
This lesson measures that distance on GridCap, in five rules.

GridCap is a fictional utility's portfolio, generated for this course. None of its numbers describe
a real company.

## Every Allowed Plan Is a Point of the Relaxation, So the LP Value Bounds Every Plan

Recall the two models of lesson 3.1.1. The MILP allows $`x_i \in \{0, 1\}`$; its LP relaxation
allows $`0 \le x_i \le 1`$ and keeps every other row. Write $`z_{LP}`$ for the relaxation's optimal
value and $`z_{IP}`$ for the MILP's ("IP" for integer program).

Take any plan the MILP allows. Each of its $`x_i`$ is 0 or 1, and 0 and 1 both lie between 0 and 1,
so the same plan is also a point the relaxation allows; every other row is identical in both models.
The relaxation found the best point it allows, so its value is at least the value of this plan.
That holds for every allowed plan, including the best one:

```math
z_{IP} \le z_{LP} \qquad \text{(maximizing)}
```

A number that no plan can beat is a **bound**; when maximizing it is an **upper bound**, a ceiling.
When minimizing, the same argument gives $`z_{LP} \le z_{IP}`$, a **lower bound**, a floor no plan
can go under. The argument uses nothing about GridCap: any MILP and its LP relaxation obey it.

On GridCap small, $`z_{LP} = 25{,}451.27`$ and $`z_{IP} = 25{,}336`$. So the finance partner can
read the LP value as "no plan under these rules can be worth more than $25,451.27k", and the MILP
value as "this plan, worth $25,336k, is the best there is".

The argument works for any **relaxation**: any model whose allowed points include every plan the
original allows. Dropping the whole-number rule is one way to relax; dropping a row is another. The
more you drop, the more points are allowed, and the higher (looser) the ceiling. The next rule
shows one.

## A One-Budget Relaxation Is Solved by Hand: Best Value per Dollar, Then a Fraction

Lesson 3.1.1 asked why the LP stops partway through one project. For a model with one budget row
and nothing else, the LP relaxation can be solved by hand, and the hand method shows why.

Each dollar spent on project $`i`$ earns $`\text{npv}_i / \text{capex}_i`$ of NPV. With fractions
allowed, the best use of the budget is to spend it on the project with the highest NPV per dollar
until that project is fully funded, then on the next best, and so on. When the next project no
longer fits whole, buy the share that fits, $`\text{room} / \text{capex}_i`$, and stop: the budget
is spent. Must-do projects are paid for first, because the row $`x_i = 1`$ leaves no choice.

```python
for p in sorted((p for p in portfolio.projects if not p.must_do), key=lambda p: p.value / p.capex, reverse=True):
    share = min(1.0, room / p.capex)
    room -= share * p.capex
    bound += share * p.value
    taken.append((p.project_id, share))
    if share < 1:
        break
```

Why is this the best point? Any point that spends a dollar on a lower-ratio project while a
higher-ratio project is not fully funded can move that dollar across and gain value. So at the
best point every project above the stopping one is fully funded and every project below it is
not funded at all. This is the classic bound for the **knapsack** problem ("pick items of given
size and value to fit one capacity", exactly GridCap's one-budget selection). The branch-and-bound of lessons 3.2.1 to 3.2.4 uses it at every step.

On GridCap small:

```text
must-do first: ['P003', 'P010', 'P017', 'P039']
then by NPV per $k, the last three taken:
  P026  NPV/capex 0.644  capex 1,350  share 1.000
  P021  NPV/capex 0.614  capex 2,020  share 1.000
  P022  NPV/capex 0.587  capex 2,550  share 0.122
greedy bound                   25,852.87
GLOP, budget and must-do only  25,852.87
GLOP, every rule               25,451.27
rows the greedy's whole projects break: ['alt_G030']
```

The hand bound, $25,852.87k, equals what GLOP returns for the model with only the budget and
must-do rows. It is higher than the full LP's $25,451.27k because the hand method ignores the
parent and alternative rows: here it funded both alternatives of group G030, which the full model
forbids. It is still a valid ceiling, since the budget-only relaxation allows every allowed plan
and more. Three numbers now line up, each a ceiling on the next:

```math
25{,}852.87 \;\ge\; 25{,}451.27 \;\ge\; 25{,}336
```

The first drops the whole-number rule and two kinds of row, the second drops only the whole-number
rule, and the third is the best plan.

<!-- practice 1 -->

## The Integrality Gap Is the Distance From the LP Bound to the Best Plan

The **integrality gap** of a model is how far its LP bound sits above the best plan. As an absolute
number it is $`z_{LP} - z_{IP}`$, in $k. As a share of the best plan, which lets you compare
portfolios of different sizes, it is

```math
\text{gap} = \frac{z_{LP} - z_{IP}}{|z_{IP}|} \qquad \text{(maximizing; } z_{IP} - z_{LP} \text{ on top when minimizing)}
```

```python
def integrality_gap(lp_bound: float, optimum: float) -> float:
    """How far above the best plan the LP bound sits, as a share of the best plan (maximizing)."""
    return (lp_bound - optimum) / abs(optimum)
```

Some texts define it as the ratio $`z_{LP} / z_{IP}`$ instead; that is 1 plus the number above, so
the two carry the same information. The gap is never negative, by the first rule. It is 0 exactly
when the LP relaxation already has a whole-number best point.

Some models have that luck built in. The OR-Tools MathOpt sample `writing_seminar.py` assigns
students to writing seminars, and it has a switch that solves the LP relaxation instead of the
MILP. Adapted here with the sample's own sizes (50 seminars, 12 students per seminar, 5 ranked
choices each) and a fixed seed:

**Sets.** $`S`$ the students; $`J`$ the seminars; $`R_i \subseteq J`$ the 5 seminars student $`i`$
ranked, $`j_{i,k}`$ the one ranked $`k`$-th. **Parameters.** $`q`$ the seats per seminar (15, then
11); $`p_k`$ the penalty for a $`k`$-th choice (0, 1, 5, 20, 100); $`P = 1{,}000`$ the penalty for a
student left without a seminar. **Variables.** $`x_{i,j} \in \{0, 1\}`$ for $`j \in R_i`$: student
$`i`$ takes seminar $`j`$; $`y_i \in \{0, 1\}`$: student $`i`$ gets none (in the LP relaxation, both
in $`[0, 1]`$).

```math
\begin{aligned}
\min \;& \sum_{i \in S} P\, y_i + \sum_{i \in S} \sum_{k=1}^{5} p_k\, x_{i, j_{i,k}} \\
\text{s.t. }& y_i + \sum_{j \in R_i} x_{i,j} = 1 && \forall i \in S && \text{(one}_i) \\
& \sum_{i \,:\, j \in R_i} x_{i,j} \le q && \forall j \in J && \text{(seats}_j)
\end{aligned}
```

```python
for i in range(len(ranked)):
    model.add_linear_constraint(y[i] + sum(x[i].values()) == 1, name=f"one_{i}")
for j in range(num_classes):
    model.add_linear_constraint(sum(xi[j] for xi in x if j in xi) <= capacity, name=f"seats_{j}")
```

```text
600 students, 50 seminars of 15 seats, 3600 variables
  LP relaxation (GLOP): 24.00, fractional variables: 0
  MILP (HiGHS):         24.00, nodes 1
600 students, 50 seminars of 11 seats, 3600 variables
  LP relaxation (GLOP): 50,052.00, fractional variables: 0
  MILP (HiGHS):         50,052.00, nodes 1
```

Both times the LP answer is already whole, so the gap is 0 and the MILP adds nothing. With 11 seats
for 12 students per seminar, 50 students must go without (50 × 1,000 of the 50,052), and still no
fraction appears. Each $`x_{i,j}`$ sits in one student row and one seminar row, and nothing else: an
assignment, which is a network model. MIT's chapter on integer programming (see Further reading)
opens with this point: when the rows have that network shape, solving the LP gives a whole-number
answer. GridCap's budget row, whose coefficients are project costs, has no such shape, which is why
it leaves a fraction.

GridCap's three default portfolios:

```text
size    projects     LP bound    optimum   abs gap      gap
tiny           8     3,770.15      3,627    143.15   3.947%
small         40    25,451.27     25,336    115.27   0.455%
medium       400   229,757.73    229,745     12.73   0.006%
```

And ten seeds of each size, to see whether that pattern is chance:

```text
tiny    gap min 0.539%  median 6.846%  max 15.049%   abs gap median 278
small   gap min 0.111%  median 0.184%  max 0.608%   abs gap median 51
medium  gap min 0.001%  median 0.005%  max 0.014%   abs gap median 11
```

The gap shrinks as the portfolio grows. The hand method of the previous rule explains why. The LP's
answer is a whole-number plan plus a share of one project (two or so when the alternative and parent
rows bind), so the LP's extra value is at most a project or two's NPV. A bigger portfolio has more
total value to divide that by, and more small projects with which a real plan can fill the leftover
budget nearly as well as the fraction does. On the medium portfolio the ceiling is within 0.006% of
the best plan.

What the gap means in practice: a MILP solver keeps two numbers while it searches, the best plan
found so far and the best ceiling it can prove, and it stops when they meet, or come within a
tolerance of each other (lesson 3.4.3: HiGHS's default is 0.01%). Before any search, its
ceiling is the LP bound (tightened by presolve and cuts, lessons 3.3.1 and 3.3.2). So the
integrality gap is the distance the search starts with. A model with a small gap starts its search
close to the finish; lessons 3.4.1 to 3.4.3 read these two numbers from a solver's result.

<!-- practice 2 -->

## Two Correct Formulations Can Have Different Gaps

A **formulation** is one way of writing a rule set as variables and rows. Two formulations can
allow exactly the same 0/1 plans and still have different LP relaxations.

Take GridCap's parent rule, "fund the child only if the parent is funded". Lesson 1.1.1 wrote it
$`x_c \le x_{p(c)}`$. Here is another way: $`x_c \le 2\, x_{p(c)}`$. Check it on the four 0/1 cases.
With the parent at 0, the row reads $`x_c \le 0`$, so the child is off. With the parent at 1, it
reads $`x_c \le 2`$, which a binary always satisfies. Both rows allow exactly the plans the rule
allows. Call the first **tight** and the second **loose**:

```python
room = 1 if parent_form == "tight" else 2
model.add_linear_constraint(x[p.project_id] <= room * x[p.parent], name=f"parent_{p.project_id}")
```

```text
tiny   tight  LP bound    3,770.15  optimum     3,627  gap 3.947%  fractional {'P003': 0.099, 'P004': 0.099}
tiny   loose  LP bound    3,811.04  optimum     3,627  gap 5.074%  fractional {'P003': 0.064, 'P004': 0.128}
medium tight  LP bound  229,757.73  optimum   229,745  gap 0.006%  fractional {'P251': 0.275}
medium loose  LP bound  229,820.83  optimum   229,745  gap 0.033%  fractional {'P065': 0.5, 'P251': 0.398}
```

The optimum is the same, as it must be: the 0/1 plans are the same. The LP bound is not. On GridCap
tiny, P004 (the child) and P003 (its parent) have the same share, 0.099, under the tight row,
because P004 is worth more per dollar and the row lets it go no higher than its parent. The loose
row lets the child sit at twice its parent's share, 0.128 against 0.064, so the LP buys more of the
valuable child for less of the parent and its value rises to $3,811.04k. On medium, the loose row
lets P065 reach 0.5 too, and the gap grows more than fivefold, from 0.006% to 0.033%.

So the gap belongs to the formulation, not only to the problem. A **stronger** (tighter)
formulation is one whose LP relaxation allows fewer fractional points while allowing the same 0/1
plans, so its bound is closer to the best plan and the solver's search starts closer to the
finish. The loose row is what a careless **big-M** row looks like: a constant ($`M = 2`$ here)
larger than it needs to be. Section 6 (*Formulation craft*) is about choosing the strongest
formulation, and lesson 6.4.3 shows the same effect for precedence over time.

## A Small Gap Means a Close Bound, Not a Safe Rounding

A small gap is good news about the bound. It is not news about rounding. Return to lesson 3.1.1's
first trap, an invented two-project model:

```text
trap 1: A costs 1 and is worth 2, B costs 100 and is worth 100, budget 100
  LP: x_A = 1.00, x_B = 0.99, value 101.00
  round down: ['A'], value 2
  optimum: ['B'], value 100
```

Its integrality gap is $`(101 - 100) / 100 = 1\%`$: the LP value is an excellent ceiling. Yet the
LP's *point*, rounded down, is worth 2. The bound and the point are different things. The gap
compares two values; it says the best plan is worth almost as much as the LP claims. It says nothing
about whether the best plan looks like the LP's answer, and here it does not: the LP funds A whole,
the best plan leaves A out.

This is why the board pack gets the MILP's plan, and the LP value goes next to it as the ceiling
that shows how little any other plan could add.

## The Model

The selection model of lesson 3.1.1 on GridCap, with its relaxation and this lesson's gap marked.

**Sets.** $`P`$ the candidate projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$ the
child projects, each with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups.

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ for each project ($k); $`B`$, the capital
budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for each $`i \in P`$ in the MILP; $`0 \le x_i \le 1`$ in the LP
relaxation.

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c\text{, tight; loose: } x_c \le 2\, x_{p(c)}) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

**Measured.** With $`z_{LP}`$ the relaxation's optimal value and $`z_{IP}`$ the MILP's:

```math
z_{IP} \le z_{LP}, \qquad \text{gap} = \frac{z_{LP} - z_{IP}}{|z_{IP}|} \quad \leftarrow \text{this lesson}
```

On GridCap small: $`z_{LP} = 25{,}451.27`$, $`z_{IP} = 25{,}336`$, gap 0.455%.

## Summary

- **Every allowed plan is a point of the relaxation, so the LP value bounds every plan.** A ceiling
  when maximizing, a floor when minimizing, for any MILP.
- **A one-budget relaxation is solved by hand.** Must-dos first, then best NPV per dollar, then a
  share of the first project that does not fit. Dropping rows gives a looser but still valid bound.
- **The integrality gap is the distance from the LP bound to the best plan.** On GridCap it is 3.9%
  on tiny, 0.455% on small and 0.006% on medium, and it shrinks as portfolios grow.
- **Two correct formulations can have different gaps.** The loose parent row allows the same plans
  and a higher bound; a stronger formulation starts the solver's search closer to the finish.
- **A small gap means a close bound, not a safe rounding.** A 1% gap can sit next to a rounded plan
  worth 2% of the best.

## Reference

| Term | Meaning |
| --- | --- |
| $`z_{LP}`$, $`z_{IP}`$ | optimal values of the LP relaxation and of the MILP |
| bound | a value no allowed plan can beat: upper when maximizing, lower when minimizing |
| relaxation | a model that allows every plan the original allows, and possibly more |
| integrality gap | $`(z_{LP} - z_{IP}) / \lvert z_{IP} \rvert`$ when maximizing |
| knapsack bound | must-dos first, then best value per dollar, then a share of the first that does not fit |
| stronger formulation | same 0/1 plans, fewer fractional points, a bound closer to the best plan |

| GridCap (default seed) | $`z_{LP}`$ | $`z_{IP}`$ | gap |
| --- | --- | --- | --- |
| tiny | 3,770.15 | 3,627 | 3.947% |
| small | 25,451.27 | 25,336 | 0.455% |
| medium | 229,757.73 | 229,745 | 0.006% |

**Further reading:** [The Knapsack Problem (OR-Tools)](https://developers.google.com/optimization/pack/knapsack) (the one-budget model of the second rule, solved by OR-Tools' own knapsack solver); [MathOpt sample writing_seminar.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/writing_seminar.py) (the assignment of this lesson, with a switch that solves the LP relaxation instead of the MILP); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (the chapter's opening on network models whose LP is already whole, and section 9.5 on the LP value as an upper bound); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2: two valid formulations of one rule can have LP relaxations of different strength, and the root LP bound predicts how a solver will do); [MO-book 3.6, Facility location](https://mobook.github.io/MO-book/notebooks/03/06-facility-location.html) (an aggregated, big-M-like row against one row per pair: same integer plans, a looser relaxation).

## Challenges

1. A cost-minimizing model has an LP relaxation worth 9,700 and a best plan worth 10,000. Which is
   the bound, which side is it on, and what is the gap?
2. Why can the hand method of the second rule not handle the parent rows? Try it on GridCap tiny,
   where the child P004 has a better ratio than its parent P003.
3. Write the parent rule with $`M = 10`$ instead of 2. Predict whether tiny's LP bound rises above
   3,811.04, and check it by changing `room` in `selection.py`.

## Design Note: Report the Bound Next to the Plan

A plan on its own invites the question "could we do better?", and nobody can answer it from the
plan. The bound answers it: on GridCap small, no plan under these rules is worth more than $115.27k
above the one proposed. So report each plan together with its bound; section 9 turns that pair
into a planner-facing explanation.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**fractional_bound.py.** Computes GridCap small's knapsack bound by hand and compares it with GLOP
on the budget-only and on the full relaxation (*A One-Budget Relaxation Is Solved by Hand*). *Try:*
Sort by `p.value` instead of `p.value / p.capex`. Predict whether the result is still a valid bound.

- Program: [fractional_bound.py](src/fractional_bound.py)

**gap_by_size.py.** The LP bound, the optimum and the integrality gap on the tiny, small and medium
portfolios (*The Integrality Gap*). *Try:* Halve each portfolio's capital budget with
`dataclasses.replace`. Predict whether the gaps grow or shrink.

- Program: [gap_by_size.py](src/gap_by_size.py)

**gap_seeds.py.** The same measurement over ten seeds of each size. *Try:* Add the large size for
two seeds. Predict the median gap before you run it.

- Program: [gap_seeds.py](src/gap_seeds.py)

**loose_parent.py.** Solves tiny and medium with the tight and the loose parent row (*Two Correct
Formulations*). *Try:* Run it on GridCap small. Its LP answer has no fractional parent, so predict
whether the two bounds differ.

- Program: [loose_parent.py](src/loose_parent.py)

**seminar.py.** Adapted from the OR-Tools MathOpt sample `writing_seminar.py`: the assignment of
students to seminars solved as an LP relaxation with GLOP and as a MILP with HiGHS (*The Integrality
Gap*). *Try:* Give the even-numbered seminars 11 seats and the others 12. Predict how many students
go without a seminar, and whether any variable comes back fractional.

- Program: [seminar.py](src/seminar.py)

**rounding_traps.py.** Lesson 3.1.1's invented models; trap 1 is the small-gap example of the last
rule.

- Program: [rounding_traps.py](src/rounding_traps.py)

**selection.py.** The selection model builder, with the `parent_form` switch, and the shared
helpers.

- Library: [selection.py](src/selection.py)
