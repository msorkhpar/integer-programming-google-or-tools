# 6.7.1 Comparing Formulations by Their LP Bound

GridCap's planners add a cost the model has ignored so far. Before any project of a region's program
can start, for example any Ridge transmission project, GridCap must **mobilize** a work front there:
set up a materials yard, bring in a supervisor, sign local contracts. It is paid once for the whole
plan, whatever the number of projects the front then runs. Two analysts add the rule to the
multi-period model of lesson 6.4.1. Both models allow exactly the same plans and both return the
same best plan. One of them is far closer to that plan before the solver has branched even once.

Lessons 3.1.2, 6.1.3, 6.2.4 and 6.4.3 each compared two ways of writing one rule. This lesson turns
those comparisons into a method you can apply to any pair of formulations, in five rules: what
"stronger" means, how to prove it, how to measure it with one number, what the solver itself makes
of the difference, and what it costs in size.

GridCap is a fictional utility's portfolio, generated for this course. The mobilization fee is this
lesson's own addition: 10% of the front's total capex, rounded down to a multiple of $10k.

## The Model

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$; $`F`$ the **work
fronts**, one per region and program that has projects (12 on GridCap small); $`P_f \subseteq P`$
the projects of front $`f`$.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k); $`B_y`$, the budget of
year $`y`$ ($k); $`\phi_f`$, the mobilization fee of front $`f`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$: project $`i`$ starts in
year $`t`$. $`y_f \in \{0, 1\}`$ for every $`f \in F`$: front $`f`$ is mobilized.

**Objective.** NPV of the projects started, less the fees of the fronts mobilized:

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \;-\; \sum_{f \in F} \phi_f\, y_f
```

**Constraints.** The rows of lesson 6.4.1, then the front rule in one of two forms. Write
$`s_i = \sum_{t \in T_i} x_{i,t}`$ for "project $`i`$ is started" (an expression, not a variable).

```math
\begin{aligned}
s_i &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
s_i &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} s_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\textstyle\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \textstyle\sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\textstyle\sum_{i \in P_f} s_i &\le |P_f|\, y_f && \forall f \in F && \text{(front}_f\text{, aggregated)} \quad \leftarrow \text{this lesson} \\
s_i &\le y_f && \forall f \in F,\ i \in P_f && \text{(front}_{f,i}\text{, disaggregated)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

A model uses one of the two front rows, never both. The code names the rows `front_Ridge_transmission`
(aggregated) and `front_Ridge_transmission_P028` (disaggregated, one per project).

```python
def add_front(model, y, started: list, members: list[str], name: str, form: str) -> None:
    """No project of the front starts unless the front is mobilized (y = 1)."""
    if form == "aggregated":
        # One row: the number of projects started is at most the front's size, and 0 if y = 0.
        model.add_linear_constraint(sum(started) <= len(started) * y, name=f"front_{name}")
    elif form == "disaggregated":
        # One row per project: this project starts only if y = 1.
        for pid, s in zip(members, started):
            model.add_linear_constraint(s <= y, name=f"front_{name}_{pid}")
    else:
        raise ValueError(form)
```

Check both forms on whole numbers before anything else. With $`y_f = 0`$, the aggregated row reads
$`\sum s_i \le 0`$ and each disaggregated row $`s_i \le 0`$: no project of the front starts. With
$`y_f = 1`$, the aggregated row reads $`\sum s_i \le |P_f|`$, which the once rows already guarantee,
and each disaggregated row $`s_i \le 1`$, also guaranteed. So with binary values the two forms allow
exactly the same plans, and the two MILPs have the same optimum.

## A Formulation Is Judged by the Region Its LP Relaxation Allows

A **formulation** of a planning problem is one choice of variables and rows whose 0/1 solutions are
exactly the plans the rules allow. Call that set of allowed plans $`S`$. Two formulations of the same
problem have the same $`S`$; what differs is everything else.

Drop the whole-number requirement and each formulation becomes an LP, its **LP relaxation** (lesson
3.1.1). The points the relaxation allows form a region, written $`R_A`$ for formulation $`A`$. Every
plan of $`S`$ lies in $`R_A`$, plus many fractional points that no plan matches. The relaxation's
optimal value is the **LP bound**: when maximizing, no plan is worth more (lesson 3.1.2).

Formulation $`A`$ is **at least as strong** as $`B`$ when $`R_A \subseteq R_B`$: every point $`A`$'s
relaxation allows, $`B`$'s allows too. It is **stronger** when, in addition, $`R_B`$ has a point
$`R_A`$ does not. Why the region and not the bound? Because the region decides the bound for every
objective at once. Maximizing any objective over a smaller region can never give more than over a
larger one that contains it, so

```math
R_A \subseteq R_B \quad\Longrightarrow\quad z_{LP}(A) \le z_{LP}(B) \quad \text{for every objective (maximizing)}
```

and the reverse inequality when minimizing. A stronger formulation's bound is never looser, whatever
the NPVs and fees turn out to be next year.

There is a smallest possible region. Every relaxation contains all the plans of $`S`$, and with them
every weighted average of plans (an LP region has no holes, lesson 6.2.4). The set of all such
averages is the **convex hull** of $`S`$, written $`\text{conv}(S)`$. So

```math
\text{conv}(S) \;\subseteq\; R_{\text{strong}} \;\subseteq\; R_{\text{weak}}
```

A formulation whose relaxation is exactly $`\text{conv}(S)`$ gives the MILP's optimum as its LP bound,
for every objective. Vielma's survey (see Further reading) calls it **sharp**; it calls a
formulation **ideal** when, on top of that, every corner point of its relaxation (the points a simplex
solver returns) is a whole-number plan, so the LP returns a plan, not only its value. Real models are
rarely either. The question in practice is which of the formulations you can write sits closer to
$`\text{conv}(S)`$.

GridCap small, both forms, as LP and as MILP:

```text
aggregated    variables 92  rows 61  LP bound 22,893.58  MILP 17,748
              LP fronts: Coast distr 0.50, Coast trans 0.26, Coast veget 1.00, Plain distr 0.60, Plain trans 0.50, Plain veget 0.00, Ridge distr 0.25, Ridge trans 0.50, Ridge veget 0.67, Valle distr 1.00, Valle trans 0.67, Valle veget 0.75
              Ridge transmission: front 0.50, P007 started 0.00, P028 started 1.00
disaggregated variables 92  rows 89  LP bound 20,074.76  MILP 17,748
              LP fronts: Coast distr 1.00, Coast trans 1.00, Coast veget 1.00, Plain distr 1.00, Plain trans 0.50, Plain veget 0.00, Ridge distr 0.00, Ridge trans 1.00, Ridge veget 1.00, Valle distr 1.00, Valle trans 1.00, Valle veget 1.00
              Ridge transmission: front 1.00, P007 started 0.00, P028 started 1.00
fronts mobilized in the best plan: 9 of 12
gap closed by the disaggregated form: 54.8%
```

Same optimum, $17,748k, as the whole-number check promised. The LP bounds are $2,819k apart. Read
the Ridge transmission line of the aggregated LP: the front is mobilized at 0.50, yet P028 is
started in full. The aggregated row for a front of two projects reads
$`s_{P007} + s_{P028} \le 2\, y`$, and $`0 + 1 \le 2 \times 0.5`$ holds. So the LP runs a whole project
while paying half the fee, $395k instead of $790k. The disaggregated row
$`s_{P028} \le y`$ refuses that point: $`1 \le 0.5`$ is false. That one point is the proof that the
disaggregated region is strictly smaller than the aggregated one; the next rule proves it is
contained in it.

The disaggregated LP is not ideal either: it mobilizes Plains transmission at 0.50. Its rows say a
front is at least as mobilized as its most-started project, and some Plains project is half started.
A stronger formulation removes fractional points; it does not remove them all.

<!-- practice 1 -->

## Containment Is Proved Row by Row: Each Weak Row Is a Sum of Strong Ones

A bound comparison on one objective is evidence. A proof that $`R_{\text{strong}} \subseteq
R_{\text{weak}}`$ settles it for every objective, and for the work fronts it takes one line. Add the
disaggregated rows of front $`f`$, one per project, $`s_i - y_f \le 0`$:

```math
\sum_{i \in P_f} (s_i - y_f) \le 0 \quad\Longleftrightarrow\quad \sum_{i \in P_f} s_i \le |P_f|\, y_f
```

The sum is exactly the aggregated row. Any point that satisfies every disaggregated row satisfies
their sum, so it satisfies the aggregated row; every other row is common to both models. Hence every
point of the disaggregated relaxation lies in the aggregated one. This is the general test: **if each
row of formulation $`B`$ is a sum of rows of $`A`$, each multiplied by a nonnegative number, then
$`R_A \subseteq R_B`$** (when both formulations use the same variables). Multiplying a "$`\le`$" row by
a negative number would turn it around, which is why the multipliers must be nonnegative.

The program checks the proof on the models it builds, row by row, and then does what a skeptic would
do: it draws 30 other objectives (every NPV scaled by a random factor between 0.5 and 1.5, every fee
by one between 0 and 3) and solves both relaxations for each:

```python
    for pid in members:
        for term in rows[f"{name}_{pid}"].terms():
            total[term.variable.name] = total.get(term.variable.name, 0) + term.coefficient
```

```text
aggregated rows equal to a sum of disaggregated rows: 12 of 12
30 objectives: disaggregated bound lower in 30, equal in 0, higher in 0
```

Never higher, as the proof says it cannot be, and strictly lower in all 30 here.

When neither region contains the other, the bounds can rank the two formulations either way,
depending on the objective. Picture formulation $`A`$ whose relaxation lets $`u`$ reach 0.7 and $`v`$
reach 0.2, and $`B`$ whose relaxation lets $`u`$ reach 0.5 and $`v`$ reach 0.6: on "maximize
$`u`$", $`B`$ has the tighter bound, and on "maximize $`v`$", $`A`$ does. One objective cannot tell
you which is stronger in general; a row-by-row proof can, and many objectives that all agree are
good evidence when no proof is at hand.

<!-- practice 2 -->

## The Share of the Gap Closed Puts Two Bounds on One Scale

The $2,819k between the two bounds means little on its own: it depends on the size of the portfolio
and of the fees. Lesson 3.1.2 measured one formulation by its **integrality gap**, the distance from
its LP bound to the best plan. Two formulations are compared by how much of the weaker one's gap the
stronger one removes:

```math
\text{gap closed} = \frac{z_{LP}(\text{weak}) - z_{LP}(\text{strong})}{z_{LP}(\text{weak}) - z_{IP}}
```

```python
def gap_closed(weak: float, strong: float, optimum: float) -> float:
    """The share of the weak formulation's integrality gap that the strong one closes."""
    return (weak - strong) / (weak - optimum)
```

On GridCap small, $`(22{,}893.58 - 20{,}074.76) / (22{,}893.58 - 17{,}748) = 54.8\%`$, the last line of
the output above. A share of 0% means the stronger form's bound is no better; 100% means it reaches
the optimum. The same formula serves when minimizing, because both differences change sign together.
The measure needs $`z_{IP}`$, the best plan's value; when the MILP is too hard to solve to the end,
use the best plan found so far, which makes the share an estimate.

## The Solver's Root Bound Is the Second Measurement

An LP bound is what the formulation says by itself. A MILP solver does not branch on that LP
directly: it first presolves the model (lesson 3.3.2) and adds cuts of its own (lesson 3.3.1), and
only then branches. The bound it holds after that work, at the **root node** of its search, is a
second measurement. MathOpt reads it by stopping HiGHS after one node:

```python
def root_bound(model: mathopt.Model) -> float:
    """HiGHS's bound after its root node: the LP after presolve and the solver's own cuts."""
    result = solve_highs(model, mathopt.SolveParameters(relative_gap_tolerance=0.0, node_limit=1))
    return result.best_objective_bound()
```

`node_limit` is the MathOpt parameter that caps the number of nodes of the search; `best_objective_bound()`
is the best bound the solver has proved when it stops (lesson 3.4.2). Both forms on GridCap small:

```text
form           LP bound   HiGHS root bound  optimum  nodes
aggregated     22,893.58            18,112   17,748     72
disaggregated  20,074.76            18,127   17,748     82
```

HiGHS's root bound for the aggregated model, $18,112k, is no worse than for the disaggregated one,
$18,127k, although the two LP bounds were $2,819k apart. Since the root bound is the bound after
presolve and cuts, those steps recovered at least everything the aggregated rows had lost. The search
that follows took 72 nodes with the weak form and 82 with the strong one.

This is a measured fact about one solver on one model, and it carries two lessons. First, a stronger
formulation is not a promise of a smaller search: after the solver's own work the two models may
start level, and the rest of the search depends on choices the solver makes along the way. Second,
the strong form still has value the node count does not show. Its LP bound is the number you can
report without running a MILP solver, it does not depend on a solver's cuts (another solver, or
another version, may find fewer), and it is the form every later model builds on. Lesson 6.7.4 makes
the same measurements on the medium portfolio.

## Strength Has a Price in Size

The disaggregated model has 89 rows against 61: one row per project (40) instead of one per front
(12). That price grows with the portfolio: on GridCap medium, with lesson 6.7.4's other rows, the two
forms have 864 and 476 rows. Rows cost LP time at every node. Vielma's survey opens with exactly this trade-off:
a formulation can be too weak or too large, and the best one balances the two. The habit that
follows is to measure both columns before choosing: the bound or the share of the gap it closes,
and the size.

Sometimes strength costs nothing. A front of one project has the same row in both forms. And a
stronger form can let you drop something else: with the disaggregated rows, each $`y_f`$ is pushed
down by its fee and held up by $`y_f \ge s_i`$, so at a whole-number $`x`$ the best $`y_f`$ is already 0
or 1. Those $`y_f`$ could be declared continuous without changing the optimum; with the aggregated
row they could not, since $`y_f = (\text{started}) / |P_f|`$ would satisfy it with a fraction.

## Summary

- **A formulation is judged by the region its LP relaxation allows.** Same 0/1 plans, smaller
  region: stronger, with a bound no looser for any objective. The smallest region is the convex hull
  of the plans.
- **Containment is proved row by row.** If every weak row is a nonnegative sum of strong rows, the
  strong region lies inside the weak one; the aggregated front row is the sum of its disaggregated
  rows. Many objectives that agree are evidence; one objective is not.
- **The share of the gap closed puts two bounds on one scale.** On GridCap small, 54.8%.
- **The solver's root bound is the second measurement.** HiGHS's presolve and cuts brought both
  forms to about the same root bound, and the weak form's search was not larger.
- **Strength has a price in size.** One row per project instead of one per front: 89 rows against 61.

## Reference

| Term | Meaning |
| --- | --- |
| formulation | variables and rows whose 0/1 solutions are exactly the allowed plans $`S`$ |
| region $`R_A`$ | the points formulation $`A`$'s LP relaxation allows |
| at least as strong | $`R_A \subseteq R_B`$, with the same plans $`S`$ |
| convex hull $`\text{conv}(S)`$ | all weighted averages of plans; inside every relaxation |
| sharp | the relaxation is $`\text{conv}(S)`$, so the LP bound is the optimum for every objective |
| ideal | sharp, and every corner point of the relaxation is a whole-number plan |
| gap closed | $`(z_{LP}(\text{weak}) - z_{LP}(\text{strong})) / (z_{LP}(\text{weak}) - z_{IP})`$ |
| root bound | the solver's bound after presolve and its own cuts, before branching (`node_limit=1`) |

| Front rule | Rows | Region |
| --- | --- | --- |
| aggregated $`\sum_{i \in P_f} s_i \le \lvert P_f \rvert\, y_f`$ | one per front | larger |
| disaggregated $`s_i \le y_f`$ | one per project | smaller: the aggregated row is their sum |

**Further reading:** [MathOpt `SolveParameters`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py)
(OR-Tools source): `node_limit`, which caps the search and, for many solvers, makes it repeatable ·
[Mixed-Integer Programming](https://developers.google.com/optimization/mip) (OR-Tools guide) ·
[Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf)
(SIAM Review, 2015): section 2.2 defines the strength of a formulation by its LP relaxation, with
sharp and locally ideal formulations, and weighs strength against size; section 4 shows how extra
variables can make a formulation both strong and small.

## Challenges

1. Write the front rule as $`\sum_{i \in P_f} s_i \le 2\, y_f`$ for every front with more than two
   projects. Is it still a formulation of the same plans? Check it on a front of three projects.
2. The disaggregated LP left Plains transmission at 0.50. Make `front_forms.py` print the started share
   of each Plains transmission project, and say which row holds the front at 0.50.
3. In `containment.py`, give every fee a factor of 0 (no fees). Predict how many of the 30 objectives
   still show a lower bound for the disaggregated form, then run it.

## Design Note: Prove the Containment, Then Measure the Rest

Two formulations compared on one GridCap seed tell you about that seed. A row-by-row argument tells
you about every seed and every objective, and it is usually short, as the sum above was. So the
course's habit is: prove containment when you can, measure the bound and the share of the gap it
closes on the data you have, and then measure what the solver does with each form, because that last
number is the one that decides run time and the one no proof can give.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**front_forms.py.** Builds GridCap small with both front forms and solves each as an LP and as a
MILP (*A Formulation Is Judged by the Region Its LP Relaxation Allows*, *The Share of the Gap
Closed*). *Try:* Raise `FEE_SHARE` in `strong_model.py` to 0.25. Predict whether the share of the gap
closed rises or falls.

- Program: [front_forms.py](src/front_forms.py)

**containment.py.** Checks that every aggregated row is the sum of its disaggregated rows, and
compares the two bounds under 30 objectives (*Containment Is Proved Row by Row*). *Try:* Let the fee
factors range from 0 to 0.1. Predict whether any objective gives equal bounds.

- Program: [containment.py](src/containment.py)

**front_search.py.** HiGHS's root bound and node count for both forms (*The Solver's Root Bound Is
the Second Measurement*). *Try:* Solve with `presolve=mathopt.Emphasis.OFF` in the parameters.
Predict whether the two root bounds move apart.

- Program: [front_search.py](src/front_search.py)

**strong_model.py.** The model builder, with `add_front` in both forms, `add_precedence`,
`lp_bound`, `root_bound` and `gap_closed`.

- Library: [strong_model.py](src/strong_model.py)
