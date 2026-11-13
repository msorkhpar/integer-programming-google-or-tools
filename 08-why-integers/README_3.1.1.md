# 3.1.1 Yes/No Decisions, and Why Rounding an LP Fails

GridCap's planning team has 40 candidate projects in its small portfolio and a capital budget of
$38,390k. An analyst who has just finished section 2 solves the selection as a linear program,
because LPs are fast, and gets back a plan that funds 20 projects whole and 52.2% of a tower set
repair. "Round it," says the planning lead, "we'll either do the repair or we won't." This lesson
shows what each way of rounding does to that plan, and why the answer is a different kind of model,
in five rules.

GridCap is a fictional utility's portfolio, generated for this course. None of its numbers describe
a real company.

## A Yes/No Decision Is a Variable That May Only Be 0 or 1

A **decision variable** is a number the solver chooses. A **yes/no decision**, such as "fund
project P022", is a variable $`x_{P022}`$ that may take only two values: 1 for yes and 0 for no.
Such a variable is called **binary**, and its **domain** (the set of values it may take) is written

```math
x_i \in \{0, 1\}
```

Lesson 1.1.1 introduced binaries for GridCap's selection; this lesson looks at what happens when
that domain is weakened. Binaries are the most common case of an **integer variable**, one whose
domain is whole numbers. A count, such as "how many crews to hire", is an integer variable with
domain $`\{0, 1, 2, \dots\}`$ and usually an upper bound. A **mixed-integer linear program** (MILP)
is a linear program in which some variables must take whole-number values; lesson 1.1.3 met it on
GridCap tiny.

In OR-Tools MathOpt, a variable's domain is its lower bound, its upper bound, and whether it must
be integer. The selection model of this module builds every $`x_i`$ in one line, with the
integer requirement as a switch:

```python
x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
     for p in portfolio.projects}
```

With `is_integer=True`, `lb=0` and `ub=1`, the only values left are 0 and 1, which is a binary.
With `is_integer=False`, the same line allows every number from 0 to 1.

Why not simply leave the variable continuous and read "0.7" as "probably yes"? Because a funded
fraction has no meaning for the business: GridCap cannot repair 52.2% of a tower set and get 52.2%
of its value. The value and the cost of a project arrive whole or not at all. A model that allows a
fraction is answering a different question from the one the planner asked.

## The LP Relaxation Drops the Whole-Number Rule, and Answers With Fractions

Take a MILP and replace each $`x_i \in \{0, 1\}`$ by $`0 \le x_i \le 1`$, keeping every other row
exactly as it was. The result is a linear program called the model's **LP relaxation**: "relaxed"
because one requirement was loosened, and an LP because every variable is now continuous. Lessons
2.1.1 and 2.2.1 solve LPs of this kind;
GLOP is OR-Tools' own LP solver, and HiGHS solves both LPs and MILPs.

Here is GridCap small's selection model (written out in full in *The Model* below), relaxed and
solved with GLOP, and then solved as the MILP with HiGHS:

```python
lp = build(small, integer=False)
result = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
whole = [pid for pid, v in lp.x.items() if result.variable_values(v) > 1 - 1e-6]
```

```text
LP relaxation: OPTIMAL, value 25,451.27
  20 projects at 1, fractional: {'P022': 0.522}
  P022: Valley tower set repair (A022), capex 2,550, NPV 1,496
MILP: OPTIMAL, value 25,336.00, 20 projects funded
```

The LP funds 20 projects whole and 0.522 of P022, and every other $`x_i`$ is 0. The comparison
`> 1 - 1e-6` is there because a solver returns floating-point numbers, so "1" may come back as
0.9999999; section 10 treats these tolerances.

Why does a fraction appear at all? The LP is free to use every last dollar. Once the projects it
funds whole leave less room than the next project costs, buying part of that project still adds
value, so the LP does. The plan that results is the best *point* of the relaxation, and lesson
1.2.3 showed that such a best point sits at a corner of the region the rows cut out. Many of those
corners have fractional coordinates. Lesson 3.1.2 computes this fraction by hand.

The MILP's best plan is worth $25,336k, less than the LP's $25,451.27k. That is no accident, and
lesson 3.1.2 is about the difference. For now the question is the planning lead's: can we get a
plan by rounding the LP's answer instead of solving the MILP?

## Rounding Up, or to the Nearest Whole, Can Break the Budget

There are three obvious ways to turn the LP's $`x_i`$ into 0s and 1s. **Rounding up** funds every
project the LP touched at all. **Rounding to the nearest** funds a project when its share is 0.5 or
more. **Rounding down** funds only what the LP funded whole. Each is one test on the LP's value:

```python
RULES = {
    "up": lambda v: v > EPS,              # any share at all becomes a funded project
    "nearest": lambda v: v >= 0.5,
    "down": lambda v: v > 1 - EPS,        # only projects the LP funded whole
}
```

Each rounded plan is then checked against the model's rows. `broken_rows` returns the label of
every row the plan breaks: `budget`, `must_<id>`, `parent_<id>` or `alt_<group>`, the same names the
model gives its constraints:

```text
budget 38,390  LP bound 25,451.27
     up: spend 39,610, value 26,167, breaks ['budget']
nearest: spend 39,610, value 26,167, breaks ['budget']
   down: spend 37,060, value 24,671, breaks []
```

P022's share is 0.522, so rounding up and rounding to the nearest both fund it whole. The LP had
already spent the budget to the dollar: its 20 whole projects cost $37,060k (the rounded-down
spend) and its 0.522 of P022 the remaining $1,330k. Paying for all of P022 instead adds $1,220k, so
the plan spends $39,610k against $38,390k. It is worth $26,167k, more than
the LP's value, and that is exactly the warning sign: no plan that keeps the budget can be worth
more than the LP (lesson 3.1.2 proves it), so a rounded plan worth more must break a row.

One portfolio could be bad luck, so the same three roundings ran on 30 GridCap small portfolios,
seeds 1 to 30 (a **seed** is the number the generator starts from; each seed gives a different
portfolio of the same size):

```text
30 small portfolios (seeds 1-30)
     up: broke the budget in 30, an alternative group in 3
nearest: broke the budget in 13, an alternative group in 0
   down: broke the budget in  0, an alternative group in 0
```

Rounding up broke the budget every time. In 3 portfolios it also funded two projects of one
alternative group. The row $`x_a + x_b \le 1`$ lets the LP split the group's one allowed project
between two alternatives, say 0.3 of one and 0.7 of the other, and rounding up turns both shares
into funded projects. Rounding to the nearest broke the budget 13 times in 30: every share it
rounds up adds spend the LP never had. A rounding that breaks the budget in 13 of 30 portfolios is
not a planning method.

<!-- practice 1 -->

## Rounding Down Keeps This Model's Rows, and Still Misses the Best Plan

Rounding down never broke a row in the 30 runs. That follows from the shape of this model's rows,
not from luck:

- **budget**: every capex is positive, so lowering any $`x_i`$ from a fraction to 0 lowers spend.
  If the LP point was within budget, the rounded-down plan is too.
- **alt**: lowering a variable lowers the left side of $`\sum_{i \in g} x_i \le 1`$.
- **parent**: if $`x_c \le x_{p(c)}`$ holds and both are rounded down, it still holds: a parent
  below 1 forces its child below 1 too, so both become 0, and a parent at 1 stays 1.
- **must**: $`x_i = 1`$ is already whole, so rounding leaves it alone.

So rounding down gives an allowed plan here. It is not the best plan:

```text
   down: spend 37,060, value 24,671, breaks []
optimum: spend 38,390, value 25,336, breaks []
  in the optimum, not in round-down: ['P022', 'P029']
  in round-down, not in the optimum: ['P008', 'P026']
```

The rounded-down plan leaves $1,330k unspent and is worth $665k less than the optimum. More telling
is the last two lines: the optimum is not "the rounded-down plan plus something". It drops two
projects the LP funded whole (P008 and P026) to make room for P022 and P029. Rounding looks only at
one point, the LP's answer, and the best plan can sit somewhere else entirely. Over the 30 seeds:

```text
round down below the optimum: mean 3.1%, worst 11.8%
```

How bad can rounding down get? As bad as you like. Here is an invented two-project model, not
GridCap data, in which the LP funds the cheap project whole and almost all of the valuable one:

```text
trap 1: A costs 1 and is worth 2, B costs 100 and is worth 100, budget 100
  LP: x_A = 1.00, x_B = 0.99, value 101.00
  round down: ['A'], value 2
  optimum: ['B'], value 100
```

Rounding down keeps $2 of a possible $100. A has the better value per dollar, so the LP takes it
first, and B no longer fits whole. Multiply both projects' figures by a thousand and the same thing
happens to a real-sized budget.

Rounding down is safe only for rows like these, where lowering a variable can never break them.
A **≥ row** (a minimum to reach) is the opposite. Suppose a vegetation program must clear at least
400 km of corridor at least cost:

```text
trap 2: clear at least 400 km; C clears 200 km for 300, D 300 km for 500, E 250 km for 450
  LP: x_C = 1.00, x_D = 0.67, x_E = 0.00
  round down: ['C'], clears 200 km of the 400 required
```

Rounding down drops the 0.67 of D and the plan clears half the requirement. A model with both kinds
of row, such as a budget and a minimum spend per region, has no safe direction to round.

The same goes for a $`\le`$ row with a negative coefficient, and for integer variables that are not
yes/no. The OR-Tools documentation's "MIP with arrays" example (its sample `mip_var_array.py`) has
both: five whole-number variables with no upper bound, four $`\le`$ rows, and two negative
coefficients. Adapted to MathOpt, with the integer requirement as a switch as above:

```math
\begin{aligned}
\max \;& 7x_0 + 8x_1 + 2x_2 + 9x_3 + 6x_4 \\
\text{s.t. }& 5x_0 + 7x_1 + 9x_2 + 2x_3 + x_4 \le 250 && \text{(c0)} \\
& 18x_0 + 4x_1 - 9x_2 + 10x_3 + 12x_4 \le 285 && \text{(c1)} \\
& 4x_0 + 7x_1 + 3x_2 + 8x_3 + 5x_4 \le 211 && \text{(c2)} \\
& 5x_0 + 13x_1 + 16x_2 + 3x_3 - 7x_4 \le 315 && \text{(c3)} \\
& x_j \ge 0, \quad x_j \in \mathbb{Z} \quad \text{(MILP only)} && \forall j \in \{0, \dots, 4\}
\end{aligned}
```

```python
def build(integer: bool) -> tuple[mathopt.Model, list[mathopt.Variable]]:
    model = mathopt.Model(name="mip-var-array")
    x = [model.add_variable(lb=0, is_integer=integer, name=f"x{j}") for j in range(len(OBJ))]
    for i, (row, rhs) in enumerate(zip(ROWS, RHS)):
        model.add_linear_constraint(sum(a * v for a, v in zip(row, x)) <= rhs, name=f"c{i}")
    model.maximize(sum(c * v for c, v in zip(OBJ, x)))
    return model, x
```

```text
LP (GLOP): value 262.66 at (8.451, 22.843, 0.000, 0.000, 3.459)
  round down    (8, 22, 0, 0, 3): value 250, breaks []
  round nearest (8, 23, 0, 0, 3): value 258, breaks ['c3']
  round up      (9, 23, 0, 0, 4): value 271, breaks ['c1', 'c2', 'c3']
  rounding x4 down changes c3 by +3.21: its coefficient there is -7
MILP (HiGHS): OPTIMAL, value 260 at (9, 20, 2, 1, 4)
```

Rounding up breaks three rows and rounding to the nearest breaks one. Rounding down happens to keep
every row here, but nothing guaranteed it: $`x_4`$ has coefficient $`-7`$ in (c3), so lowering it
*raises* that row's left side, by 3.21, and only the drop from rounding $`x_0`$ and $`x_1`$ down kept
(c3) within 315. The best whole-number point is worth 260 against round-down's 250, and it uses
$`x_2`$ and $`x_3`$, which the LP left at 0. The OR-Tools page prints a different point with the same
value 260, $`(10, 16, 4, 4, 3)`$: this model has more than one best plan, and neither is a rounding
of the LP's answer.

## Rounding Down Then Filling Gives an Allowed Plan, Never a Proof

Rounding down leaves money unspent, so a natural repair is to **fill**: walk through the projects
not yet funded, best value per dollar first, and add each one that fits and keeps every rule.

```python
def fill(portfolio, plan: set[str]) -> set[str]:
    """Add projects best value per dollar first, each only if it fits and keeps every rule."""
    plan = set(plan)
    for p in sorted(portfolio.projects, key=lambda p: p.value / p.capex, reverse=True):
        if p.project_id not in plan and not broken_rows(portfolio, plan | {p.project_id}):
            plan.add(p.project_id)
    return plan
```

```text
round down, then fill: adds ['P004', 'P012', 'P029'], value 25,290, 46 short of the optimum
```

The filled plan is allowed and worth $25,290k, only $46k below the optimum. A method like this,
which builds an allowed plan quickly with no promise that it is the best, is called a
**heuristic**. Lesson 3.3.3 shows the heuristics MILP solvers run inside their search.

But notice how we know it is $46k short: the MILP was solved. Without that solve, all the filled
plan tells you is that $25,290k is achievable. What it cannot tell you is whether $25,336k, or
$27,000k, is. The LP gives half the missing information: its value, $25,451.27k, is a ceiling no
plan can pass, so the filled plan is at most $161.27k short. Whether that ceiling is close enough
to trust is the subject of lesson 3.1.2, and closing the distance to a proof is what a MILP solver
does (lessons 3.2.1 to 3.2.4).

<!-- practice 2 -->

## The Model

The selection model of lesson 1.1.1, on GridCap small. The MILP and its LP relaxation share every
row and differ only in the domain of $`x_i`$, marked below.

**Sets.** $`P`$ the candidate projects (40 on GridCap small); $`M \subseteq P`$ the must-do
projects; $`C \subseteq P`$ the child projects, each with parent $`p(c)`$; $`\mathcal{G}`$ the
alternative groups, each a set of projects.

**Parameters.** $`\text{capex}_i`$, the cost of project $`i`$ ($k); $`\text{npv}_i`$, its NPV if
it starts as early as it can ($k); $`B`$, the capital budget ($38,390k on GridCap small).

**Variables.** One per project, with domain

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(MILP: 1 if project } i \text{ is funded)} \\
& 0 \le x_i \le 1 && \forall i \in P && \text{(LP relaxation)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

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

The code names the rows `budget`, `must_<id>`, `parent_<id>` and `alt_<group>`. On GridCap small the
LP relaxation's value is $25,451.27k and the MILP's is $25,336k.

## Summary

- **A yes/no decision is a variable that may only be 0 or 1.** In MathOpt that is `lb=0, ub=1,
  is_integer=True`; a fraction of a project has no business meaning.
- **The LP relaxation drops the whole-number rule and answers with fractions.** On GridCap small it
  funds 0.522 of P022.
- **Rounding up, or to the nearest whole, can break the budget.** Rounding up broke it on all 30
  small portfolios tried; rounding to the nearest on 13.
- **Rounding down keeps this model's rows and still misses the best plan.** It is safe only for rows
  that lowering a variable cannot break, loses 3.1% on average here, and can lose almost
  everything; the best plan may share little with the LP's answer.
- **Rounding down then filling gives an allowed plan, never a proof.** Only a bound, or a MILP solve,
  says how far from the best it is.

## Reference

| Term | Meaning |
| --- | --- |
| binary variable | $`x \in \{0, 1\}`$: `add_variable(lb=0, ub=1, is_integer=True)` or `add_binary_variable()` |
| integer variable | a variable restricted to whole numbers, usually with bounds |
| MILP | a linear program in which some variables must be integer |
| LP relaxation | the same model with every integer requirement dropped, bounds kept |
| round up / nearest / down | fund a project if its LP share is $`> 0`$ / $`\ge 0.5`$ / $`= 1`$ |
| heuristic | a quick method that returns an allowed plan with no proof that it is best |

| Row shape | Rounding down | Rounding up |
| --- | --- | --- |
| $`\le`$ with nonnegative coefficients (budget, alt) | keeps it | can break it |
| $`x_c \le x_{p(c)}`$ (parent) | keeps it | keeps it |
| $`\ge`$ with nonnegative coefficients (a minimum) | can break it | keeps it |
| $`=`$ | can break it | can break it |
| $`\le`$ with a negative coefficient | can break it | can break it |

**Further reading:** [Solving a MIP Problem (OR-Tools)](https://developers.google.com/optimization/mip/mip_example) (a two-variable MIP whose LP answer, rounded to the nearest point, is not the best whole-number point); [MIP with arrays (OR-Tools)](https://developers.google.com/optimization/mip/mip_var_array) (the five-variable example of this lesson, built from arrays with the linear solver wrapper and SCIP); [MathOpt sample integer_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (the same two-variable MIP in MathOpt, with `add_integer_variable` and a check of the termination reason before reading values); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1 states capital budgeting as a go/no-go program with contingent and multiple-choice rows, the parent and alternative rows here; section 9.4 shows rounding an LP answer giving an infeasible or a far-from-best point); [MO-book 3.1, BIM production with perturbed data](https://mobook.github.io/MO-book/notebooks/03/01-bim-perturbed.html) (rounding an LP plan down keeps it feasible but loses value, and rounding up may break a row).

## Challenges

1. Rounding up keeps the parent rows (the table above says so). Explain why, with $`x_c = 0.3`$ and
   $`x_{p(c)} = 0.5`$ as an example.
2. Trap 1 used a budget of 100. Find a budget at which rounding down gives the optimum.
3. The fill step walks projects by value per dollar. Would walking by NPV alone have found a better
   plan on GridCap small? Change the `key=` in `fill` and predict before you run it.

## Design Note: Solve the MILP, Keep the Heuristic

A team that rounds an LP usually does it because the MILP "might be slow". On GridCap small the
MILP is solved by HiGHS at the first node of its search (lesson 3.1.3 counts the nodes), and the cost of rounding is a plan that either
breaks the budget or leaves value behind with no one knowing how much. The defensible order is the
reverse: solve the MILP, and keep a heuristic such as round-down-and-fill as a fallback that is
always allowed, reported together with the LP bound so the reader knows how far from the best it
can be.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**relax_small.py.** Solves GridCap small's selection as an LP relaxation with GLOP and as a MILP
with HiGHS, and lists the fractional variables (*The LP Relaxation Drops the Whole-Number Rule*).
*Try:* Run it on `generate("small", 5)` instead. Predict how many variables come back fractional.

- Program: [relax_small.py](src/relax_small.py)

**rounding.py.** Rounds the LP's answer up, to the nearest and down, checks each plan's rows,
compares the rounded-down plan with the optimum, and fills it (*Rounding Up*, *Rounding Down*,
*Rounding Down Then Filling*). *Try:* Change the nearest rule's threshold from 0.5 to 0.6. Predict
which rows the nearest plan breaks now.

- Program: [rounding.py](src/rounding.py)

**rounding_seeds.py.** Repeats the three roundings on 30 small portfolios and counts the rows they
break and the value rounding down loses. *Try:* Run it on the tiny size. Predict whether rounding
down loses more or less than on small.

- Program: [rounding_seeds.py](src/rounding_seeds.py)

**rounding_traps.py.** Two invented models where rounding down fails: a two-project budget and a
≥ row. *Try:* In trap 2, round up instead of down. Predict the km cleared and the cost.

- Program: [rounding_traps.py](src/rounding_traps.py)

**mip_arrays.py.** Adapted from the OR-Tools example `mip_var_array.py` ("MIP with arrays"): its LP
answer rounded down, to the nearest and up, and its MILP answer (*Rounding Down Keeps This Model's
Rows*). It also prints the node counts lesson 3.1.3 quotes. *Try:* Change the $`-7`$ in (c3) to
$`+7`$. Predict whether rounding down still keeps every row.

- Program: [mip_arrays.py](src/mip_arrays.py)

**selection.py.** The selection model builder and the helpers every program of this module shares:
`build`, `lp_values`, `best_plan`, `broken_rows`.

- Library: [selection.py](src/selection.py)
