# 6.5.3 Mutually Exclusive Alternatives (Repair vs. Replace)

Two aging assets in GridCap's small portfolio each come with two candidate projects. Asset A001, a
45-year-old Plains transmission asset, can be replaced (P001, $2,640k) or repaired (P002, $460k).
Asset A030, a Valley transmission asset, can be replaced (P030, $5,840k) or repaired (P031, $1,020k). The
planners' question for each is the one asset managers ask every cycle: **repair, replace, or leave
it alone**, and if replace, now or later? The options are **mutually exclusive alternatives**: the
plan picks at most one of them for each asset. This lesson writes that as rows, makes "leave it
alone" an option with a price, and handles the case where two options are allowed in sequence, in
three rules.

GridCap is a fictional utility's portfolio, generated for this course. Its data puts each pair in
an **alternative group** (G001 and G030); the two-year gap below is invented for the lesson.

## Alternatives for One Asset Share One At-Most-One Row

Repairing an asset and replacing it in the same plan pays for the same risk reduction twice. The
model stops that with one row per alternative group $`g`$, the "multiple-choice" row of capital
budgeting (MIT 15.053, section 9.1):

```math
\sum_{i \in g} \text{started}(i) \le 1 \qquad \forall g \in \mathcal{G} \qquad \text{(alt}_g)
```

with $`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ as in lesson 6.4.1. Because it sums every
start variable of every member, the row also says that no two *years* of the group are chosen: one
member, in one year, or nothing. `alternative_rows.py` solves GridCap small with and without the two
rows:

```text
G001 asset A001 | P001 replace 2,640 may start [2028, 2029, 2030]; P002 repair 460 may start [2027, 2028]
G030 asset A030 | P030 replace 5,840 may start [2029, 2030]; P031 repair 1,020 may start [2027, 2028]
with alt rows  NPV $24,260k  {'G001': ['P001 replace 2028'], 'G030': ['P031 repair 2028']}
without        NPV $24,397k  {'G001': ['P001 replace 2028', 'P002 repair 2028'], 'G030': ['P031 repair 2028']}
```

Without the row, the plan replaces A001 *and* repairs it, both in 2028, and reports $137k more NPV.
That NPV is not real: GridCap values each option as if it were the only thing done to the asset, so
the second option's value is counted on risk the first one already removed. The model has no way to
know that; only the alternative row tells it.

The row is one row per group, not one per pair of members. When a group has three or more options
(repair, refurbish, replace), every pair conflicts, and lesson 6.1.3 showed that one row on the
whole group allows the same 0/1 plans as the pair rows and gives the tighter LP bound.

## Doing Nothing Is an Alternative Too, and It Has a Price

The alternative row allows a plan that does nothing to the asset: the sum is 0. That is often the
right answer, but it is an answer the model gives silently, and it hides a cost the NPV does not
carry: the risk of leaving an aging asset in service. Make the option explicit. Give each group a
binary $`k_g`$, "keep the asset as it is", and turn the row into an equality:

```math
\sum_{i \in g} \text{started}(i) + k_g = 1 \qquad \forall g \in \mathcal{G} \qquad \text{(choose}_g)
```

Now every asset gets exactly one of its options, "keep" included, and the plan names the choice for
each. With $`k_g`$ in the model, its price can go in the objective. Lesson 1.1.2 measured an asset's
risk as its chance of failure times its consequence of failure. Here the chance is that of failing
within the plan's five years, given that the asset has survived to its present age (the Weibull
curve's conditional form), and the price of keeping is

```math
\text{risk}_g = \text{PoF}_g \times \text{CoF}_g, \qquad \max \; \sum_{i,t} \text{npv}_{i,t}\, x_{i,t} - \sum_{g} \text{risk}_g\, k_g
```

```python
def pof_within(asset, years: int) -> float:
    """Chance the asset fails within `years`, given that it has survived to its age (Weibull)."""
    now = (asset.age / asset.weibull_eta) ** asset.weibull_beta
    later = ((asset.age + years) / asset.weibull_eta) ** asset.weibull_beta
    return 1 - math.exp(-(later - now))
```

```python
    for g, members in groups.items():
        keep[g] = plan.model.add_binary_variable(name=f"keep_{g}")
        plan.model.add_linear_constraint(sum(plan.started(i) for i in members) + keep[g] == 1,
                                         name=f"choose_{g}")
    if price_risk:
        npv = plan.model.objective.as_linear_expression()
        plan.model.maximize(npv - sum(risk[g] * keep[g] for g in groups))
```

`do_nothing.py` solves with the generated budgets and with 2027's budget cut to $6,000k, each time
with NPV alone and with the risk of keeping subtracted:

```text
G001 A001: age 45, PoF in 5 years 0.170, CoF $3,215k, risk of doing nothing $547k
G030 A030: age 16, PoF in 5 years 0.175, CoF $2,026k, risk of doing nothing $354k
generated budgets
  NPV only    objective $24,260k  NPV $24,260k  {'G001': 'P001 replace 2028', 'G030': 'P031 repair 2028'}
  NPV - risk  objective $24,260k  NPV $24,260k  {'G001': 'P001 replace 2028', 'G030': 'P031 repair 2028'}
2027 cut to $6,000k
  NPV only    objective $22,649k  NPV $22,649k  {'G001': 'keep (do nothing)', 'G030': 'P031 repair 2028'}
  NPV - risk  objective $22,606k  NPV $22,606k  {'G001': 'P002 repair 2027', 'G030': 'P031 repair 2028'}
```

With the generated budgets both assets are worked on either way, so the price changes nothing.
After the cut, the NPV-only plan leaves A001 alone and spends the money elsewhere. Priced, keeping
A001 costs $547k of risk: the NPV-only plan is then worth $22,649k − $547k = $22,102k, and the
solver prefers to repair A001 in 2027 for $460k, giving up $43k of NPV to remove $547k of risk.
Where the two models differ, the second one's report reads "repair A001" and the first one's reads
nothing at all, because the first never wrote down that leaving A001 alone was a decision.

`keep` is binary, but it need not be declared so: the equality forces it to $`1 - \sum`$ of binaries
that sum to at most 1, so it is 0 or 1 whenever they are. Declaring it binary costs nothing and
states the intent.

<!-- practice 1 -->

## Repair Now, Replace Later Is a Sequence: Exclusion Can Depend on the Years

"Replace now or replace later" needs no new row: the replace project's start variables are already
alternatives to each other, through its once row. "Repair now, *then* replace later" is different:
it is two members of the group in one plan, which the alternative row forbids. Suppose the asset
engineers say a repair buys at least two years, so a replacement may follow a repair if it starts
$`G = 2`$ or more years after it, and a repair never follows a replacement.

The exclusion now depends on the years. A replacement in year $`t`$ conflicts with a repair in year
$`s`$ when $`s > t - G`$: a repair too close before it, in the same year, or after it. For each
replacement year that is a set of variables of which at most one may be 1:

```math
x_{\text{rep},t} + \sum_{s \in T_{\text{fix}},\ s > t - G} x_{\text{fix},s} \le 1 \qquad \forall t \in T_{\text{rep}} \qquad \text{(gap}_t)
```

with "rep" the replace project and "fix" the repair. The repair's own variables already exclude each
other (its once row), so each gap row is again a group in which every pair conflicts, written as one
row. The alternative row on the whole group is dropped, because it would forbid the sequence.

```python
def gap_rows(plan):                     # both allowed if the replacement is at least GAP years later
    for t in small.project(REPLACE).starts():
        too_close = [s for s in small.project(REPAIR).starts() if s > t - GAP]
        plan.model.add_linear_constraint(
            plan.x[REPLACE, t] + sum(plan.x[REPAIR, s] for s in too_close) <= 1,
            name=f"gap_{REPLACE}_{t}")
```

`repair_then_replace.py` applies it to A001 (repair P002, replace P001). It lists the conflicts,
solves four versions, and then fixes six pairs of years to see which each rule accepts:

```text
P002 repair may start [2027, 2028], P001 replace may start [2028, 2029, 2030]
  replace in 2028 conflicts with a repair in [2027, 2028]
  replace in 2029 conflicts with a repair in [2028]
  replace in 2030 conflicts with a repair in []
never both        NPV $24,260k  P002 -  P001 2028
gap of 2          NPV $24,260k  P002 -  P001 2028
gap, repair 2027  NPV $24,148k  P002 2027  P001 -
no rule           NPV $24,397k  P002 2028  P001 2028
repair 2027, replace 2029: never both refused, gap of 2 allowed
repair 2027, replace 2030: never both refused, gap of 2 allowed
repair 2028, replace 2030: never both refused, gap of 2 allowed
repair 2027, replace 2028: never both refused, gap of 2 refused
repair 2028, replace 2029: never both refused, gap of 2 refused
repair 2028, replace 2028: never both refused, gap of 2 refused
```

The last six lines are the rule itself: the gap rows accept exactly the three sequences with a
replacement two or more years after the repair, and "never both" accepts none. The solves show
that allowing a sequence does not mean the plan uses it. With these values the best plan replaces
A001 in 2028 under both rules; even with the repair fixed in 2027, the best plan adds no
replacement, because a later replacement is worth less (P001's NPV falls from $1,401k in 2028 to
$1,189k in 2029). "No rule" funds a repair and a replacement in the same year, the double count of
the first section.

A model that allows a sequence needs one more thing from its data: the value of the replacement
*after* a repair. GridCap gives each option's value as if it were done alone, so a plan that does
both counts both in full. When you allow a sequence, ask for its value, or model it as its own
option ("repair 2027, replace 2030") with its own NPV, which keeps the plain alternative row.

<!-- practice 2 -->

## The Model

The planning model with this lesson's rows marked. `do_nothing.py` adds the keep variables and
choose rows; `repair_then_replace.py` replaces the alternative row of G001 by its gap rows.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$; for a group allowed in
sequence, its repair project "fix" and replace project "rep".

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k); $`\text{risk}_g =
\text{PoF}_g \times \text{CoF}_g`$, the risk of keeping group $`g`$'s asset as it is ($k);
$`G = 2`$, the fewest years from a repair to a replacement.

**Variables.**

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(project } i \text{ starts in year } t\text{)} \\
& k_g \in \{0, 1\} && \forall g \in \mathcal{G} && \text{(keep group } g\text{'s asset as it is)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} - \sum_{g \in \mathcal{G}} \text{risk}_g\, k_g \quad \leftarrow \text{risk term: this lesson}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) + k_g &= 1 && \forall g \in \mathcal{G} && \text{(choose}_g) \quad \leftarrow \text{this lesson, in place of alt}_g \\
x_{\text{rep},t} + \textstyle\sum_{s \in T_{\text{fix}},\, s > t - G} x_{\text{fix},s} &\le 1 && \forall t \in T_{\text{rep}} && \text{(gap}_t) \quad \leftarrow \text{this lesson, for a sequence} \\
\textstyle\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \textstyle\sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

Without the keep variables, choose$`_g`$ is the alternative row alt$`_g`$:
$`\sum_{i \in g} \text{started}(i) \le 1`$. A group allowed in sequence has gap rows and no choose or
alt row.

| Label | Row name in the code |
| --- | --- |
| alt$`_g`$ | `alt_G001` |
| choose$`_g`$, $`k_g`$ | `choose_G001`, `keep_G001` |
| gap$`_t`$ | `gap_P001_2029` |

## Summary

- **Alternatives for one asset share one at-most-one row.** Without it the plan repaired and
  replaced A001 in the same year and claimed $137k of NPV that does not exist.
- **Doing nothing is an alternative too, and it has a price.** A keep variable makes the row an
  equality, names the choice in the report, and lets the risk of keeping enter the objective; after
  a budget cut it turned "leave A001 alone" into "repair A001".
- **Repair now, replace later is a sequence: exclusion can depend on the years.** One row per
  replacement year, over the repair years too close to it, replaces the group row. Value the
  sequence, not each option alone.

## Reference

| Rule in words | Rows |
| --- | --- |
| at most one option per asset | $`\sum_{i \in g} \text{started}(i) \le 1`$ |
| exactly one option, "keep" included | $`\sum_{i \in g} \text{started}(i) + k_g = 1`$, $`k_g \in \{0,1\}`$ |
| price of keeping | objective term $`-\text{risk}_g\, k_g`$ |
| replace at least $`G`$ years after a repair, never before it | $`x_{\text{rep},t} + \sum_{s > t - G} x_{\text{fix},s} \le 1`$ for each $`t`$ |
| replace now or later | nothing new: the replace project's once row |

| Term | Meaning |
| --- | --- |
| alternative group | the projects that are options for one asset; at most one is done |
| conditional PoF | the chance of failing within a period, given survival to the present age |

**Further reading:** [MathOpt sample time_indexed_scheduling.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (its "no two jobs overlap" rows are one row per time over the start variables that conflict there, the same shape as the gap rows); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1: multiple-choice constraints; section 9.2: alternative constraints, at least one of two rows switched by a binary); [MO-book 3.11, Maintenance planning](https://mobook.github.io/MO-book/notebooks/03/11-maintenance-planning.html) (spaces maintenance shutdowns with one row per window of start days, and writes the shutdown as a disjunction).

## Challenges

1. Give A030 a third option, "refurbish", that costs $2,000k. How many alternative rows does G030
   need now?
2. In `do_nothing.py`, double every CoF. Predict whether the plan with the generated budgets
   changes.
3. Write the gap rows for "a replacement at least 2 years after a repair, and a repair at least 3
   years after a replacement".

## Design Note: Keep Is a Decision, So Report It

Planners and auditors ask about the assets a plan did *not* touch as often as about those it did.
A model with an explicit keep variable per asset answers from the solution itself: every asset has
exactly one chosen option. Without it, the report has to infer "kept" from an absence, and an asset
that was never in a group at all looks the same as one the optimizer decided to leave. Lesson 9.3.2
explains such decisions to planners by forcing an option in and out.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**alternative_rows.py.** Solves GridCap small with and without the alternative rows (*Alternatives
for One Asset Share One At-Most-One Row*). *Try:* Remove only G030's row. Predict whether A030 gets
two projects.

- Program: [alternative_rows.py](src/alternative_rows.py)

**do_nothing.py.** Adds a keep variable per group and prices it by the asset's risk (*Doing Nothing
Is an Alternative Too*). *Try:* Cut 2027 to $4,000k as well. Predict what A001 gets with and without
the price.

- Program: [do_nothing.py](src/do_nothing.py)

**repair_then_replace.py.** Allows "repair, then replace two years later" on A001 and checks which
pairs of years the rows accept (*Repair Now, Replace Later Is a Sequence*). *Try:* Set `GAP = 1`.
Predict which of the six pairs change.

- Program: [repair_then_replace.py](src/repair_then_replace.py)

**planning_model.py.** The model builder the programs import; `groups_of` lists the alternative
groups.

- Library: [planning_model.py](src/planning_model.py)
