# 2.1.1 Your First LP: Splitting a Maintenance Budget Across Programs

GridCap's 2027 maintenance budget is $8,890k, and three programs want it: transmission,
distribution and vegetation management (tree trimming). Last year the split was argued in a
meeting: each program director asked for more, and finance cut everyone by the same share. This
year the planning director wants a split she can defend: one that earns the most value, never
books more crew work than the crews can do, keeps the regulator's minimum on tree trimming, and
does not hand any single program more than half of what is spent. This lesson builds that split
as a **linear program** and solves it. GridCap is the course's fictional utility; every number
below is invented.

Lesson 1.1.3 met a linear program (LP) once: continuous variables, a linear objective, linear
constraints. There, the LP was a stand-in for a yes/no model, and its fractions were a problem.
Here the decisions really are amounts of money, so fractions are exactly right, and the LP is the
model itself. Four rules, one per heading.

## An LP Decides Amounts, So Each Variable Is a Continuous Quantity With Bounds

Start with the data. GridCap's small portfolio has 40 candidate projects across the three
programs. Averaged over a program's projects, two rates describe it: how much NPV (net present
value, lesson 1.1.1: what a project is worth today, after paying for it) a $k spent on
it returns (*value per $*), and how many crew-months each $1,000k of its work takes. Crews are
the people who do the work, counted in **crew-months** (one crew working for one month). The
portfolio says how many crew-months each program has in 2027.

```python
def show_data() -> None:
    print(f"{'program':13} {'value/$':>8} {'crew-mo per $1M':>16} {'crews':>6} {'crews allow $k':>15}")
    for k in PROGRAMS:
        crews = small.crews[k, YEAR]
        print(f"{k:13} {VALUE[k]:8.3f} {CREW[k]:16.2f} {crews:6} {crews * 1000 / CREW[k]:15,.1f}")
    print(f"budget {small.budget[YEAR]:,}  vegetation floor {FLOOR['vegetation']}  share cap {SHARE:.0%}")
```

```text
program        value/$  crew-mo per $1M  crews  crews allow $k
transmission     0.582             2.46     26        10,569.1
distribution     0.477             2.24      9         4,017.9
vegetation       0.561             6.41      2           312.0
budget 8,890  vegetation floor 300  share cap 50%
```

Read one row: a $k on transmission returns $0.582k of NPV, and $1,000k of transmission work takes
2.46 crew-months. With 26 crew-months, transmission crews can do at most
$`26 \times 1000 / 2.46 = 10{,}569.1`$ $k of work. Vegetation work is crew-heavy (6.41 crew-months
per $1,000k), and with 2 crew-months its crews can do only $312.0k.

**The decisions.** The director controls one thing: how many $k each program gets. That is one
**decision variable** per program, $`s_k`$, the amount spent on program $`k`$ in 2027, in $k.

**The domain.** A variable's *domain* is the set of values it may take. Money can be split to the
dollar, so $`s_k`$ is **continuous**: any real number, not only whole numbers. Money spent cannot
be negative, so $`s_k \ge 0`$. That $`0`$ is the variable's **lower bound**. It has no upper bound of
its own: the rules below limit it.

```python
s = {k: model.add_variable(lb=0, name=f"s_{k}") for k in PROGRAMS}
```

`add_variable(lb=0)` is $`s_k \ge 0`$: with no `ub` the upper bound is $`+\infty`$, and with no
`is_integer=True` the variable is continuous. Forget `lb=0` and the default lower bound is
$`-\infty`$ (lesson 2.1.2 prints a variable created with no bounds), which would let the model "spend" a negative amount on one program to free money for
another. Always state the domain.

**The objective.** The director wants the most value. If each $k on program $`k`$ returns
$`v_k`$, the split's value is

```math
\max \; \sum_{k \in K} v_k\, s_k
```

```python
model.maximize(sum(VALUE[k] * s[k] for k in PROGRAMS))
```

This line hides the main assumption of every LP. The value of program $`k`$ is **proportional** to
its spend: the 4,000th $k returns as much as the first. And the programs' values simply **add up**:
spending on one does not change what another returns. Those two properties, *proportionality* and
*additivity*, are what "linear" means. Together with *divisibility* (a variable may take any
fraction) and *certainty* (every number is known), they are the four assumptions an LP makes about
the world. When one fails badly, as with the diminishing returns of lesson 1.1.3's square-root
curve, the LP is the wrong model, or needs the piecewise trick of section 6.6.

## Every Rule Is One Linear Row, and a Ratio Is Multiplied Out Before It Is Written

A **constraint**, also called a *row* (each one is a row of the model's table of coefficients,
lesson 2.1.2), says which splits are allowed. In an LP, every constraint is a **linear
expression** (numbers times variables, added) compared with a number by $`\le`$, $`\ge`$ or $`=`$.
The director's four rules become four kinds of row.

**Budget.** The programs together get at most $`B = 8{,}890`$:
$`s_{\text{transmission}} + s_{\text{distribution}} + s_{\text{vegetation}} \le B`$. It is $`\le`$,
not $`=`$: nothing says the money must all be spent, and the solve below shows that the best split
does not spend it all.

**Crews.** Program $`k`$'s work needs $`m_k / 1000`$ crew-months per $k, and it has $`C_k`$
crew-months: $`(m_k / 1000)\, s_k \le C_k`$, one row per program.

**Floor.** The regulator requires at least $300k of tree trimming: $`s_{\text{vegetation}} \ge 300`$.

```python
rows = {"budget": model.add_linear_constraint(sum(s.values()) <= budget, name="budget")}
for k in PROGRAMS:
    rows[f"crew_{k}"] = model.add_linear_constraint(CREW[k] / 1000 * s[k] <= crews[k], name=f"crew_{k}")
for k, amount in floor.items():
    rows[f"floor_{k}"] = model.add_linear_constraint(s[k] >= amount, name=f"floor_{k}")
```

Each row has a `name`, its label in the formulation. When a model misbehaves, you search for
rows by these names.

**Share.** "No program gets more than half of what is spent" is a ratio:

```math
\frac{s_k}{\sum_{j \in K} s_j} \le 0.5
```

A ratio of variables is not linear: it divides by a variable. MathOpt refuses it outright:

```python
try:
    model.add_linear_constraint(s["transmission"] / total <= 0.5, name="share_transmission")
except TypeError as error:
    print("ratio refused:", type(error).__name__)
```

```text
ratio refused: TypeError
```

The fix is algebra. The total spend is never negative, so multiplying both sides by it keeps the
direction of $`\le`$, and the row becomes linear:

```math
s_k \le \alpha \sum_{j \in K} s_j, \qquad \alpha = 0.5
```

```python
row = model.add_linear_constraint(s["transmission"] <= 0.5 * total, name="share_transmission")
```

```text
stored as: -inf <= +0.5*s_transmission -0.5*s_distribution -0.5*s_vegetation <= 0.0
```

The second line is how MathOpt keeps the row: it moved every variable to the left-hand side
($`s_T - 0.5 s_T - 0.5 s_D - 0.5 s_V \le 0`$) and records the row as a lower bound
($`-\infty`$, none) and an upper bound ($`0`$) on that expression. Lesson 2.1.2 uses this shape.

One caution about multiplying out. It is safe here because the total is never negative. If the
denominator could be zero, the ratio rule says nothing (there is no ratio), while the multiplied
row says $`s_k \le 0`$, which happens to agree. If the denominator could be negative, multiplying
would flip $`\le`$ to $`\ge`$, and the row would be wrong. Check the sign of what you multiply by.

<!-- practice 1 -->

## GLOP Solves It: Read the Status, Then the Amounts, Then the Rows

GLOP is the LP solver Google wrote and ships with OR-Tools (lesson 1.1.3 used it once). The solve,
and a report:

```python
split = build(YEAR)
result = mathopt.solve(split.model, mathopt.SolverType.GLOP)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise SystemExit(result.termination.reason.name)
report(split, result)
```

```python
def report(split, result) -> None:
    print("status", result.termination.reason.name)
    for k, var in split.s.items():
        print(f"  s_{k:13} = {result.variable_values(var):9,.1f}")
    print(f"  NPV  {result.objective_value():,.1f}")
    for name, row in split.rows.items():
        lo, hi = row.lower_bound, row.upper_bound
        bound = f"<= {hi:,.1f}" if hi < float("inf") else f">= {lo:,.1f}"
        print(f"  {name:22} {activity(row, result):10,.1f}  {bound}")
```

The status comes first, as lesson 1.1.3 taught: `OPTIMAL` means the split returned is proven to
be the best one. Then the amounts, the objective, and for each row its **activity**, the value of
its left-hand side at the solution:

```python
def activity(row: mathopt.LinearConstraint, result: mathopt.SolveResult) -> float:
    """The row's left-hand side, a . x, at the solution."""
    values = result.variable_values()
    return sum(term.coefficient * values[term.variable] for term in row.terms())
```

`row.terms()` gives each variable of the row with its coefficient, so the activity is the sum of
coefficient × value. Here is the answer:

```text
status OPTIMAL
  s_transmission  =   4,329.9
  s_distribution  =   4,017.9
  s_vegetation    =     312.0
  NPV  4,611.5
  budget                    8,659.7  <= 8,890.0
  crew_transmission            10.7  <= 26.0
  crew_distribution             9.0  <= 9.0
  crew_vegetation               2.0  <= 2.0
  floor_vegetation            312.0  >= 300.0
  share_transmission            0.0  <= 0.0
  share_distribution         -312.0  <= 0.0
  share_vegetation         -4,017.9  <= 0.0
```

Read the rows. Three are **full**: the activity equals the bound. Distribution and vegetation have
used every crew-month, and transmission sits exactly at half of the spend
($`4{,}329.9 = 4{,}017.9 + 312.0`$, so its share row's activity is $`0`$). The other rows have room:
the budget has $`8{,}890 - 8{,}659.7 = 230.3`$ $k left, transmission's crews have $`15.3`$
crew-months idle, and vegetation got $`12`$ $k above its floor.

Now explain the answer from the rows, which is the skill this section is about.

- Vegetation gets its crew limit, $312.0k. It returns 0.561 per $, and its crews allow no more.
- Distribution gets its crew limit too, although it returns the least, 0.477. Why fund the worst
  program to the hilt? Because of the share rule: transmission may only match what the other two
  get together. Every $k given to distribution lets transmission take one more $k, so a $k to
  distribution really buys $`0.477 + 0.582`$ of value for $2k. The LP found that without being told.
- Transmission gets exactly what the share rule allows, $`4{,}017.9 + 312.0 = 4{,}329.9`$.
- So $230.3k of budget is left. No program can absorb it: two are out of crews, and the third is at
  its share. The best split leaves money unspent, which is why the budget row is $`\le`$. Written
  as $`=`$, it would force the plan to spend money that no rule lets it spend: the model would be
  **infeasible**, meaning no split satisfies every row.

The amounts are fractions of a $k (4,017.9, not 4,018). For money that is fine: the model's
domain says any real number. For crews, trucks or whole projects it would not be, and that is
where section 3's integer variables come in.

OR-Tools' own first MathOpt LP, the sample `linear_programming.py`, follows the same order: it
solves with GLOP, refuses to read anything unless the status is `OPTIMAL`, and only then prints the
values. Its LP has no story attached, three amounts and three limits:

```math
\begin{aligned}
\max \;& 10x_0 + 6x_1 + 4x_2 \\
\text{s.t. }& 10x_0 + 4x_1 + 5x_2 \le 600 && \text{(c1)} \\
& 2x_0 + 2x_1 + 6x_2 \le 300 && \text{(c2)} \\
& x_0 + x_1 + x_2 \le 100 && \text{(c3)} \\
& x_0,\ x_1,\ x_2 \ge 0
\end{aligned}
```

Adapted here, with the rows read as above:

```python
model = mathopt.Model(name="linear-programming-example")
x = [model.add_variable(lb=0.0, name=f"x{j}") for j in range(3)]
rows = [model.add_linear_constraint(10 * x[0] + 4 * x[1] + 5 * x[2] <= 600, name="c1"),
        model.add_linear_constraint(2 * x[0] + 2 * x[1] + 6 * x[2] <= 300, name="c2"),
        model.add_linear_constraint(sum(x) <= 100, name="c3")]
model.maximize(10 * x[0] + 6 * x[1] + 4 * x[2])
```

```python
result = mathopt.solve(model, mathopt.SolverType.GLOP)
if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
    raise RuntimeError(f"model failed to solve to optimality: {result.termination}")
```

```text
status OPTIMAL  objective 733.33
  x0 = 33.33  x1 = 66.67  x2 = 0.00
  c1  activity 600.00  <= 600  full
  c2  activity 200.00  <= 300  room 100.00
  c3  activity 100.00  <= 100  full
```

Two rows are full, c1 and c3, and they decide the answer: with $`x_2 = 0`$, the two equations
$`10x_0 + 4x_1 = 600`$ and $`x_0 + x_1 = 100`$ give $`x_0 = 33.33`$, $`x_1 = 66.67`$. Row c2 has 100
of room, so it played no part.

<!-- practice 2 -->

## A Changed Number Moves the Answer Only Through the Rows That Are Full

A planner's next question is always "what if?". Suppose GridCap can hire 3 more crew-months of
distribution work, 12 instead of 9. Re-solve, and list the full rows, the rows whose activity sits
on their bound:

```python
def full_rows(split, result, tol: float = 1e-6) -> list[str]:
    """Rows whose left-hand side sits on their bound: the rules the answer is pressed against."""
    names = []
    for name, row in split.rows.items():
        a = activity(row, result)
        if abs(a - row.upper_bound) <= tol or abs(a - row.lower_bound) <= tol:
            names.append(name)
    return names
```

The comparison uses a **tolerance** of $`10^{-6}`$, not `==`: a solver works in floating point, and
an activity of 8,889.9999999 is on its bound for every practical purpose.

```text
distribution crews  9: NPV 4,611.5  {'transmission': 4329.9, 'distribution': 4017.9, 'vegetation': 312.0}
   full rows: crew_distribution, crew_vegetation, share_transmission
distribution crews 12: NPV 4,733.5  {'transmission': 4445.0, 'distribution': 4133.0, 'vegetation': 312.0}
   full rows: budget, crew_vegetation, share_transmission
```

The NPV rises by $`4{,}733.5 - 4{,}611.5 = 122.0`$ $k. Distribution's crews no longer stop it, and a
new row is full instead: the budget. Distribution grows only until the money runs out, at
4,133.0, with crew-months to spare. Transmission still sits at half the spend,
$`8{,}890 / 2 = 4{,}445`$.

This is the pattern of every LP answer. The solution is pressed against a few full rows; they
decide it, and the rows with room do not. Change the number in a row with room, and nothing moves
until the room is used up. Change the number in a full row, and the answer moves, until another row
fills. Lesson 2.1.2 gives the room a name (slack), and lesson 2.3.1 puts a price on each full row (its
*dual value*: how much the objective rises per unit of the row's bound).

## The Model

**Sets.** $`K = \{\text{transmission}, \text{distribution}, \text{vegetation}\}`$, the programs.

**Parameters.**
$`v_k`$, the NPV returned per $k spent on program $`k`$ ($k per $k);
$`m_k`$, the crew-months program $`k`$'s work takes per $1,000k;
$`C_k`$, the crew-months program $`k`$ has in the year;
$`B`$, the year's budget ($k);
$`f`$, the regulator's floor on vegetation spend ($k);
$`\alpha`$, the largest share of the spend one program may get ($`\alpha = 0.5`$).
For 2027: the table in the first section, $`B = 8{,}890`$, $`f = 300`$.

**Variables.** $`s_k \ge 0`$ for every $`k \in K`$, continuous: the $k spent on program $`k`$.

**Objective.**

```math
\max \; \sum_{k \in K} v_k\, s_k
```

**Constraints.**

```math
\begin{aligned}
\sum_{k \in K} s_k &\le B && && \text{(budget)} \\
\frac{m_k}{1000}\, s_k &\le C_k && \forall k \in K && \text{(crew}_k) \\
s_{\text{vegetation}} &\ge f && && \text{(floor\_vegetation)} \\
s_k &\le \alpha \sum_{j \in K} s_j && \forall k \in K && \text{(share}_k) \\
s_k &\ge 0 && \forall k \in K
\end{aligned}
```

The labels are the row names in the code: `budget`, `crew_transmission`, `floor_vegetation`,
`share_distribution`, and so on.

## Summary

- **An LP decides amounts, so each variable is continuous with bounds.** State the domain every
  time: `lb=0` for money, or the default $`-\infty`$ lets money flow backwards. Linear means
  proportional and additive; an LP also assumes divisibility and known data.
- **Every rule is one linear row; a ratio is multiplied out first.** MathOpt refuses a division by a
  variable. Multiplying by a total that is never negative keeps the direction of the inequality.
- **Read the status, then the amounts, then the rows.** A row's activity against its bound tells
  you which rules decided the answer, and lets you explain it in the planner's words.
- **A changed number moves the answer only through full rows.** Rows with room do not matter until
  their room is gone.

## Reference

| Rule in words | Row |
| --- | --- |
| at most $`B`$ in total | $`\sum_k s_k \le B`$ |
| work within the crews | $`(m_k/1000)\, s_k \le C_k`$ |
| at least $`f`$ on program $`k`$ | $`s_k \ge f`$ |
| no program above share $`\alpha`$ | $`s_k \le \alpha \sum_j s_j`$ (multiplied out) |
| money is never negative | $`s_k \ge 0`$, `add_variable(lb=0)` |

| MathOpt | Meaning |
| --- | --- |
| `add_variable(lb=0)` | continuous variable, $`0 \le s < \infty`$ |
| `add_linear_constraint(expr <= b, name=...)` | one named row |
| `mathopt.solve(model, mathopt.SolverType.GLOP)` | solve an LP with GLOP |
| `row.terms()`, `row.lower_bound`, `row.upper_bound` | a row's coefficients and bounds, as stored |
| `result.variable_values(v)` | a variable's value in the solution |

**Further reading:** [MathOpt sample linear_programming.py](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/linear_programming.py) (the LP adapted above: variables with `lb=0.0`, named rows, GLOP, and the status checked before any value is read); [Solving an LP Problem (OR-Tools)](https://developers.google.com/optimization/lp/lp_example) (the same steps, variables, constraints, objective, solve, in OR-Tools' linear solver wrapper); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (what MathOpt is and the solvers it drives, GLOP and PDLP among them); [MO-book 2.1, BIM production planning](https://mobook.github.io/MO-book/notebooks/02/01-bim.html) (a two-product production LP, built and solved step by step); [MO-book 2.5, BIM production variants](https://mobook.github.io/MO-book/notebooks/02/05-bim-fractional.html) (a ratio in the *objective*, which unlike the share row cannot simply be multiplied out and needs a change of variables).

## Challenges

1. Finance proposes writing the budget row as an equation, "spend it all". Using the output above,
   explain what GLOP would report, and why.
2. The share rule changes to "no program gets more than 40%". Which rows would you expect to be full
   now? Write down your guess, then set `SHARE = 0.4` in `program_split.py` and check it.
3. A director says "distribution has the worst return; cut it". Explain to her, in two sentences and
   without the word "constraint", why the best split funds it to its crew limit.

## Design Note: Averages Make the Model Linear, and Hide the Projects

The value of a program is not really 0.582 per $: its projects differ, and funding half of a
transmission line returns nothing. The split model trades that detail for a model that is small,
fast and easy to explain, which is the right trade for a budget-level question ("how much per
program?"). The project-level question ("which projects?") needs yes/no variables and is section
3's model. Many utilities run both: the split sets each program's envelope, and the project model
fills it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**first_lp.py.** Prints the program data, builds the split for 2027, solves it with GLOP and reports
the amounts and every row's activity (*An LP Decides Amounts* and *GLOP Solves It*). *Try:* Lower the
vegetation floor to 0 in `program_split.py`. Predict whether any amount changes before you run it.

- Program: [first_lp.py](src/first_lp.py)

**ratio_rule.py.** Shows MathOpt refusing a ratio of variables and storing the multiplied-out share
row (*Every Rule Is One Linear Row*). *Try:* Change `0.5` to `0.4` in the multiplied-out row, and
predict the stored coefficients before you run it.

- Program: [ratio_rule.py](src/ratio_rule.py)

**what_if.py.** Re-solves with more distribution crews and lists the full rows (*A Changed Number
Moves the Answer*). *Try:* Give distribution 20 crew-months. Predict the NPV before you run it.

- Program: [what_if.py](src/what_if.py)

**or_tools_lp.py.** Adapted from the OR-Tools MathOpt sample `linear_programming.py`: its LP solved
with GLOP, the status checked first, then the values and each row's activity (*GLOP Solves It*).
*Try:* Raise c2's limit from 300 to 400. Predict whether any value moves before you run it.

- Program: [or_tools_lp.py](src/or_tools_lp.py)

**program_split.py.** The data and the `build` function the other programs of this module import.

- Library: [program_split.py](src/program_split.py)
