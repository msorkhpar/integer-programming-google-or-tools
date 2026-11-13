# 6.2.3 Indicator Constraints vs. Big-M

Lessons 6.2.1 and 6.2.2 spent their effort on one number: an $`M`$ large enough to switch GridCap's
crew rule off, and no larger. A planner reading the model asks the obvious question: the rule is
"if no contractor is hired, crew use stays within the in-house crews". Why not hand the solver
exactly that sentence, and let it worry about $`M`$? Some solvers accept that sentence directly, as
an **indicator constraint**, and CP-SAT has its own form of it. This lesson writes the crew rule
both ways, measures what changes, and sets out when to use which, in four rules.

## The Model

The model of lesson 6.2.1 with one change: the crew row is an implication instead of a big-M row,
so it has no $`M`$.

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i \subseteq Y`$ project $`i`$'s start years;
$`P^{\text{must}}`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the child
projects, with parent $`p(c)`$ and lag $`L_c`$; $`G`$ the programs, $`P_g`$ the projects of program
$`g`$; $`A_{g,y}`$ the pairs $`(i, t)`$, $`i \in P_g`$, $`t \in T_i`$, with project $`i`$ started in
$`t`$ still being worked on in year $`y`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, project $`i`$'s spend in its $`k`$-th year
of work ($k); $`B_y`$ the budget ($k); $`\kappa_i`$ the crew-months project $`i`$ needs per year of
work; $`K_{g,y}`$ the in-house crew-months; $`F = 300`$ the contractor fee ($k). No $`M`$.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$; $`h_{g,y} \in \{0, 1\}`$ for
$`g \in G`$, $`y \in Y`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \;-\; F \sum_{g \in G} \sum_{y \in Y} h_{g,y}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus P^{\text{must}} && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in P^{\text{must}} && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
h_{g,y} = 0 \;&\Longrightarrow\; \sum_{(i,t) \in A_{g,y}} \kappa_i\, x_{i,t} \le K_{g,y} && \forall g \in G,\ y \in Y && \text{(crews}_{g,y}) \quad \leftarrow \text{changed}
\end{aligned}
```

The pieces from lessons 6.4.1 to 6.4.4 read as in lesson 6.2.1: $`x_{i,t} = 1`$ says project $`i`$ starts in
year $`t`$; $`T_i`$ is its window, and a year outside it gets no variable; `started(i)`, the sum
$`\sum_{t \in T_i} x_{i,t}`$, is 1 when the project is funded; row after$`_{c,t}`$ says the child
can have started by year $`t`$ only if its parent had started by year $`t - L_c`$; and
$`A_{g,y}`$ lists the start choices that keep a crew of program $`g`$ busy in year $`y`$. Lessons
6.4.1 and 6.4.3, later in this section, treat them in full.

The arrow $`\Longrightarrow`$ reads "implies": when $`h_{g,y} = 0`$ the row must hold; when
$`h_{g,y} = 1`$ it says nothing. That is the business rule word for word.

## An Indicator Constraint States the Implication and Leaves M to the Solver

An **indicator constraint** is a pair: a binary variable (the **indicator**), and a linear row that
must hold whenever the indicator takes a given value. MathOpt writes it with
`add_indicator_constraint`. `crew_model.build` writes the crew row either way, depending on `form`:

```python
for (g, y), h in hire.items():
    crews = portfolio.crews[g, y]
    if form == "big_m":
        model.add_linear_constraint(use[g, y] <= crews + big[g, y] * h, name=f"crews_{g}_{y}")
    elif form == "indicator":
        model.add_indicator_constraint(indicator=h, activate_on_zero=True,
                                       implied_constraint=use[g, y] <= crews, name=f"crews_{g}_{y}")
```

The three arguments that matter:

| Argument | Meaning here |
| --- | --- |
| `indicator=h` | the binary that decides whether the row applies: $`h_{g,y}`$ |
| `activate_on_zero=True` | the row applies when $`h = 0`$ (no contractor); the default, `False`, applies it when $`h = 1`$ |
| `implied_constraint=use <= crews` | the linear row that must then hold, written as in `add_linear_constraint` |

Compare the two lines. The big-M line needs `big[g, y]`, a number someone had to derive and defend
(lesson 6.2.1). The indicator line needs nothing but the rule. It is also harder to get wrong:
there is no $`M`$ that can be too small and silently refuse plans, and no $`M`$ that can be huge and
leak through the tolerance (lesson 6.2.2).

That does not make the problem of $`M`$ go away. An LP relaxation is made only of linear rows, and an
implication is not one. To use an LP relaxation at all, a solver that takes an indicator must either
leave the row out of the LP and enforce it by branching on $`h`$, or turn it into a linear row
itself, which needs bounds on the row's left side, the same bounds lesson 6.2.1 used. The
indicator moves the work of finding $`M`$ from you to the solver; it does not remove it.

## Only Some Solvers Take Indicator Constraints

MathOpt accepts an indicator constraint into any model, but each solver behind it decides whether
it can solve one. HiGHS, the course's default MILP solver, cannot. SCIP, which ships with OR-Tools
and is selected with `mathopt.SolverType.GSCIP`, can. Here is the indicator model sent to both,
next to the big-M model with the tightest $`M`$:

```python
try:
    quiet_solve(cm.model, mathopt.SolverType.HIGHS, params=exact)
except Exception as error:                      # 9.15 raises AttributeError; the reason is in __context__
    print("HiGHS:", type(error).__name__, "| reason:", error.__context__)
```

```text
indicator constraints in the model: 15
HiGHS: AttributeError | reason: Highs does not support indicator constraints [INVALID_ARGUMENT]
SCIP, indicator     OPTIMAL  objective 23,341.0  hired [('transmission', 2031), ('vegetation', 2031)]
SCIP, tight big-M   OPTIMAL  objective 23,341.0  hired [('transmission', 2031), ('vegetation', 2031)]
HiGHS, tight big-M  OPTIMAL  objective 23,341.0  hired [('transmission', 2031), ('vegetation', 2031)]
```

Three things to take from it:

- **HiGHS refuses the model outright.** The error OR-Tools 9.15 raises is an unhelpful
  `AttributeError`; the real reason, "Highs does not support indicator constraints", is attached to
  the exception as `__context__`. A model meant for HiGHS cannot use indicators at all, so choosing
  indicators is also choosing a solver.
- **SCIP solves it, to the same plan and value** as the big-M model: both forms state the same rule,
  so they allow the same plans.
- **The output shows no speed.** Which form solves faster depends on the solver and the model, and
  the program prints no node counts, because SCIP's count for the indicator model was not the same
  from one run to the next. If speed matters, measure both forms on your own data, several times.

GLOP, an LP solver, refuses indicators too, even when every variable is relaxed to a continuous
one in $`[0, 1]`$. The program's last lines send it the relaxed indicator model:

```python
relaxed = build(small, None, integer=False, form="indicator")     # every variable continuous in [0, 1]
try:
    quiet_solve(relaxed.model, mathopt.SolverType.GLOP)
except Exception as error:
    print("GLOP, relaxed indicator model:", error.__context__)
```

```text
GLOP, relaxed indicator model: Glop does not support indicator constraints [INVALID_ARGUMENT]
```

So an indicator model has no LP relaxation you can solve directly. To get an LP bound for it, solve
the big-M form's relaxation.

<!-- practice 1 -->

## CP-SAT Enforces a Row Only When a Literal Is True

CP-SAT, OR-Tools' constraint-programming solver (lessons 4.4.1 to 4.4.4), was built around this idea. Every
constraint in CP-SAT can carry **enforcement literals**: Boolean variables, or their negations,
that must all be true for the constraint to apply. A **literal** is a Boolean variable `h` or its
negation `~h` ("not h"). The crew rule is one line per row:

```python
for (g, y), h in hire.items():
    use = sum(p.crew_months * x[p.project_id, t] for p in small.projects if p.program == g
              for t in p.starts() if active(p, t, y))
    model.add(use <= small.crews[g, y]).only_enforce_if(~h)
```

`only_enforce_if(~h)` reads "only if not hired": the row applies when `h` is false, which is
`activate_on_zero=True` in MathOpt's terms. The rest of the CP-SAT model (`cpsat_crews.py`) is the
same model with CP-SAT's names: `new_bool_var` for a binary, `add` for a linear row, `maximize` for
the objective. It returns the same plan:

```text
CP-SAT OPTIMAL  objective 23,341.0  hired [('transmission', 2031), ('vegetation', 2031)]
```

CP-SAT has two requirements MathOpt does not. Every coefficient must be an integer (crew-months,
$k of spend and NPV are all whole numbers in GridCap, so this model qualifies; lesson 4.4.3
covers scaling one that is not), and every variable must have finite bounds, because CP-SAT works
with integer variables over known ranges. Within those requirements, enforcement literals are its
native way of saying "if", and they need no $`M`$.

CP-SAT also enforces an **equality**, which SCIP through MathOpt does not. The OR-Tools guide
*Channeling constraints* writes an if-then-else, "if $`x < 5`$ then $`y = 0`$, else
$`y = 10 - x`$", with a Boolean $`b`$ that is true exactly when $`x \ge 5`$ and two enforced
equalities. `if_then_else.py` builds the guide's model, lists every solution, then writes the same
rule as MathOpt indicator constraints and sends it to SCIP:

```python
model.add(x >= 5).only_enforce_if(b)          # b == (x >= 5)
model.add(x < 5).only_enforce_if(~b)
model.add(y == 10 - x).only_enforce_if(b)     # b implies y == 10 - x
model.add(y == 0).only_enforce_if(~b)         # not b implies y == 0
```

```python
model.add_indicator_constraint(indicator=b, implied_constraint=y <= 10 - x, name="then_le")
model.add_indicator_constraint(indicator=b, implied_constraint=y >= 10 - x, name="then_ge")
model.add_indicator_constraint(indicator=b, activate_on_zero=True, implied_constraint=y <= 0, name="else")
```

```text
CP-SAT, all solutions (x, y, b): [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 5, 1), (6, 4, 1), (7, 3, 1), (8, 2, 1), (9, 1, 1), (10, 0, 1)]
SCIP, equality rows: gSCIP does not support indicator constraints with ranged implied constraints; bounds are: 10 <= ... <= 10 [INVALID_ARGUMENT]
SCIP, one-sided rows, x fixed 0 to 10: [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0), (5, 5, 1), (6, 4, 1), (7, 3, 1), (8, 2, 1), (9, 1, 1), (10, 0, 1)]
same table: True
```

SCIP refuses the indicator whose implied row is the equality $`y = 10 - x`$. MathOpt stores an
equality as a row with two equal bounds, here $`10 \le x + y \le 10`$, and SCIP (gSCIP, the SCIP that ships with OR-Tools) takes
only an implied row with **one** side; a ranged row, $`l \le a^\top x \le u`$ with both bounds
finite, is refused the same way (lesson 4.3.1 shows both). The fix is one indicator per side, on
the same binary: "$`y \le 10 - x`$" and "$`y \ge 10 - x`$" for the then-branch. For the
else-branch one side is enough, because $`y \ge 0`$ is already the variable's bound. With $`x`$
fixed at each of its 11 values, SCIP finds the same $`y`$ and $`b`$ as CP-SAT on every line.

<!-- practice 2 -->

## Use a Tight Big-M When the Bounds Are Known, an Indicator When They Are Not

Put the three lessons together and the choice is short:

| Situation | Write | Why |
| --- | --- | --- |
| HiGHS or another MILP solver without indicator support | big-M, with $`M`$ computed from the data (lesson 6.2.1) | the only option; keep $`M`$ tight and check the plan after solving (lesson 6.2.2) |
| a solver that takes indicators, and good bounds on the row | either; measure | both state the same rule, so only a measurement on your data can choose |
| a solver that takes indicators, and no finite bound on the row's left side | indicator | no valid $`M`$ exists at all (lesson 6.2.1), but the implication is still correct |
| an all-integer model in CP-SAT | `only_enforce_if` | native, no $`M`$ |

The third row is the case indicators exist for. If a switched quantity has no finite upper bound
in the model, the bound rule of lesson 6.2.1 gives no $`M`$, and any number you invent can be too
small for some data. An indicator states the rule without one. Before reaching for it, though, look
for the bound in the data (a budget, a capacity, a demand caps almost every real quantity) and
put that bound on the variable; it helps every form of the model.

Whatever the form, the post-solve check of lesson 6.2.2 stays. It costs a few lines, and it is the
only thing that reads the plan the way the business rule does.

## Summary

- **An indicator constraint states the implication and leaves M to the solver.** MathOpt's
  `add_indicator_constraint(indicator=h, activate_on_zero=True, implied_constraint=...)` writes "if
  h = 0 then the row holds"; the solver still needs bounds to relax it.
- **Only some solvers take indicator constraints.** HiGHS refuses them (the reason is on the
  exception's `__context__`); SCIP solves them, here to the same plan as the big-M form, but only
  when each implied row has one side.
- **CP-SAT enforces a row only when a literal is true.** `model.add(row).only_enforce_if(~h)`,
  equalities included; integer coefficients and bounded variables only.
- **Use a tight big-M when the bounds are known, an indicator when they are not.** And check the
  plan against the rule after every solve.

## Reference

| Tool | "row holds when h = 0" | "row holds when h = 1" |
| --- | --- | --- |
| big-M (any MILP solver) | $`a^\top x \le b + M h`$ | $`a^\top x \le b + M (1 - h)`$ |
| MathOpt indicator (SCIP; not HiGHS, not GLOP) | `add_indicator_constraint(indicator=h, activate_on_zero=True, implied_constraint=row)` | `add_indicator_constraint(indicator=h, implied_constraint=row)` |
| CP-SAT | `model.add(row).only_enforce_if(~h)` | `model.add(row).only_enforce_if(h)` |

The MathOpt row works for SCIP only when `row` has one side: `expr <= u` or `expr >= l`. An
equality `expr == b` or a ranged row `(l <= expr) <= u` is refused ("gSCIP does not support
indicator constraints with ranged implied constraints"); write it as two indicators on the same
binary, one per side. CP-SAT enforces equalities and ranged rows as they are.

| Term | Meaning |
| --- | --- |
| indicator constraint | a binary and a linear row that must hold when the binary has a given value |
| implication | "if A then B"; says nothing when A is false |
| literal | a Boolean variable or its negation, in CP-SAT `h` or `~h` |
| enforcement literal | a literal that must be true for a CP-SAT constraint to apply |

**Further reading:** [Channeling constraints (OR-Tools)](https://developers.google.com/optimization/cp/channeling) (the if-then-else adapted in `if_then_else.py`: `only_enforce_if` with a Boolean and its negation, two pairs of enforced rows, equalities among them); [CP-SAT sample channeling_sample_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/channeling_sample_sat.py) (the same model as a complete program that lists every solution); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt can call and its specialized MIP constraints, indicators among them); [MathOpt `Model.add_indicator_constraint` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (every argument, the implied row given whole or as `implied_lb`, `implied_expr` and `implied_ub`, and the rule that the indicator must be binary when the model is solved); [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver) (CP-SAT works over the integers only, and constraints with fractions must be scaled first).

## Challenges

1. Write the crew rule with `activate_on_zero=False`, using a binary "in-house only" instead of
   "hire". What changes in the objective?
2. A row should hold only when *two* binaries are both 0. Write it in CP-SAT with
   `only_enforce_if`, and as a big-M row. What is the big-M row's coefficient on each binary?
3. Print SCIP's `solve_stats.node_count` for both forms and run the program three times. What do you
   conclude about comparing the two forms by one run?

## Design Note: One Builder, Several Forms

`crew_model.build(..., form=...)` writes the same rule as a big-M row, as an indicator, or not at
all, and every other row is shared. That one switch is what made the measurements in this module
cheap: the forms differ in one line, so any difference in the output comes from that line. When you
are unsure which form a model should use, build it so that the choice is a parameter, measure on
your data, and keep the parameter.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**indicator_crews.py.** The crew rule as indicator constraints, refused by HiGHS and solved by SCIP,
next to the tight big-M model (*Only Some Solvers Take Indicator Constraints*). *Try:* Solve the
big-M model with SCIP using $`M = 10^6`$ instead of the tight values. Predict whether the plan
changes before running.

- Program: [indicator_crews.py](src/indicator_crews.py)

**cpsat_crews.py.** The whole crew model in CP-SAT, with the crew rule as `only_enforce_if`
(*CP-SAT Enforces a Row Only When a Literal Is True*). *Try:* Make the fee 1,000 and predict how many
contractors CP-SAT hires.

- Program: [cpsat_crews.py](src/cpsat_crews.py)

**if_then_else.py.** OR-Tools' if-then-else in CP-SAT, then as MathOpt indicators: refused by
SCIP with equality rows, solved with one-sided rows (*CP-SAT Enforces a Row Only When a Literal Is
True*). *Try:* Replace the two one-sided then-rows with a single ranged row,
`implied_constraint=(10 <= x + y) <= 10`. Moving $`x`$ to the left turns $`y = 10 - x`$ into
$`x + y = 10`$, written with both of its bounds, 10 and 10, the way MathOpt stores an equality.
Predict SCIP's answer from the rule above.

- Program: [if_then_else.py](src/if_then_else.py)

**crew_model.py.** The model builder, shared with lessons 6.2.1 and 6.2.2.

- Library: [crew_model.py](src/crew_model.py)
