# 9.3.3 Scenario Diffs: Selected, Deferred, Shifted

Finance has asked what a smaller 2029 envelope would do: $6,000k instead of $8,760k. Lesson 7.1.3
answered the right way, with a **copy** of the base scenario, its own snapshot, and its own run, and
printed one line comparing the two plans. That line is what a planner reads first, and in a real
planning cycle it is read dozens of times: base against cut, cut against cut-plus-override, this
week's run against last week's. This lesson turns it into a report, the **scenario diff**, and
states the rules that keep it honest.

A diff that is not honest is easy to produce. Compare start variables instead of projects, and a
project that moved a year shows up as one project dropped and another added. Show the plans but not
the inputs, and nobody can say what caused the change. Change two inputs at once, and the diff
cannot say which one cost what. Leave out the change in NPV, and a reshuffle worth $8k looks as
important as one worth $1,174k. Each rule below closes one of these.

GridCap is a fictional utility, generated for this course; no number in it describes a real one.

## The Model

Both scenarios solve the model of lesson 9.3.2 with their own data; the cut changes one parameter,
$`B_{2029}`$. The last section adds one row, marked, to find the second-best plan.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$; $`F^{+}`$ and $`F^{-}`$
the projects a scenario forces in and out. For the last section, $`S^*`$ the set of pairs
$`(i,t)`$ with $`x_{i,t} = 1`$ in the best plan.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k): in the base scenario $`B_{2029} = 8{,}760`$,
in the cut scenario $`B_{2029} = 6{,}000`$, every other year the same.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$, with
$`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ and
$`\text{by}(i, t) = \sum_{s \in T_i,\, s \le t} x_{i,s}`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus (M \cup F^{+} \cup F^{-}) && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\text{started}(i) &= 1 && \forall i \in F^{+} \setminus M && \text{(in}_i) \\
\text{started}(i) &= 0 && \forall i \in F^{-} && \text{(out}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\text{by}(c, t) &\le \text{by}(p(c),\, t - L_c) && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\textstyle\sum_{(i,t) \in S^*} x_{i,t} - \sum_{(i,t) \notin S^*} x_{i,t} &\le |S^*| - 1 && && \text{(not\_best)} \quad \leftarrow \text{last section only}
\end{aligned}
```

**The diff.** Write a plan as a map from its funded projects to their start years: plan $`a`$ funds
$`P_a`$ and starts $`i`$ in $`a(i)`$. From plan $`a`$ to plan $`b`$:

```math
\begin{aligned}
\text{selected} &= P_b \setminus P_a \\
\text{deferred} &= P_a \setminus P_b \\
\text{shifted} &= \{\, i \in P_a \cap P_b : a(i) \ne b(i) \,\}, \text{ earlier when } b(i) < a(i), \text{ later when } b(i) > a(i)
\end{aligned}
```

The words follow lesson 9.3.2: a project the new plan funds and the old one did not is *selected*,
one the old plan funded and the new one does not is *deferred*, and one both fund in different
years is *shifted*.

## A Diff Compares Plans Project by Project, in Three Lists

`diffs.diff_scenarios` takes two runs and returns the three lists, with two more numbers that the
next rule asks for:

```python
def diff_scenarios(a: Run, b: Run) -> Diff:
    """Compare two runs project by project: never variable by variable, never by position in a list."""
    pa, pb = a.plan, b.plan
    sa, sb = real_spend(a.built.portfolio, pa), real_spend(b.built.portfolio, pb)
    return Diff(
        selected=sorted(set(pb) - set(pa)),
        deferred=sorted(set(pa) - set(pb)),
        shifted=[(p, pa[p], pb[p]) for p in sorted(set(pa) & set(pb)) if pa[p] != pb[p]],
        npv=b.npv - a.npv,
        spend={y: sb[y] - sa[y] for y in sa},
    )
```

The key is the project id. A diff of the start variables would see P008 lose $`x_{P008,2031}`$ and
gain $`x_{P008,2029}`$, two changes, where a planner sees one: P008 moved two years earlier. A diff
by position in a list is worse: one project added near the top of a sorted list moves every line
below it. Here is the base against the cut, from `scenario_diff.py`:

```text
plan changed:
  selected  ['P002', 'P037']
  deferred  ['P001', 'P005', 'P016']
  shifted earlier ['P008 2031->2029', 'P011 2031->2029', 'P012 2031->2030', 'P021 2029->2028']
  shifted later   ['P025 2028->2029', 'P035 2027->2028']
  NPV change $-1,174k
  spend change by year 2027: -120, 2028: +100, 2029: -2,940, 2030: +50, 2031: +80
```

These are the same changes lesson 7.1.3 printed in one line, now sorted into what a planner acts
on. Three readings are worth making every time.

- **Look for swaps inside alternative groups.** P001 is deferred and P002 selected, and both are
  options for asset A001 (group G001): this is one decision, "repair instead of replace", not two.
  A good report pairs them.
- **Shifts go both ways.** Four projects move earlier, into years the cut did not touch, and two move
  later. A cut in one year rearranges the whole plan, because the five budget rows are solved
  together.
- **Count changes, not only money.** Eleven projects change for one input; a planner who must tell
  eleven fleet teams wants that number as much as the NPV.

## A Plan Diff Needs the Input Diff and the Money Beside It

A diff of plans says what changed; it does not say why. The other half is a diff of the
**inputs**, which each scenario already holds in one canonical form for its snapshot (lesson 7.1.3).
`input_changes` walks two such dictionaries and lists every value that differs:

```python
def input_changes(a: dict, b: dict, where: str = "") -> list[str]:
    """Every input that differs between two scenarios' inputs, as 'key: old -> new'."""
    found = []
    for key in sorted(set(a) | set(b)):
        old, new = a.get(key, "absent"), b.get(key, "absent")
        if isinstance(old, dict) and isinstance(new, dict):
            found += input_changes(old, new, f"{where}{key}.")
        elif old != new:
            found.append(f"{where}{key}: {old} -> {new}")
    return found
```

```text
base: OPTIMAL NPV $24,260k, 27 funded, snapshot 5d3b8d36fe54
cut-2029: OPTIMAL NPV $23,086k, 26 funded, snapshot f07165929325

inputs changed:
  budget.2029: 8760 -> 6000
```

One input changed, so every line of the plan diff is its consequence. If the input diff listed
anything else, a changed cost profile, a solver setting, the portfolio's own hash, the plan diff
could no longer be read as the effect of the budget cut. The snapshots make the check cheap: equal
snapshots, equal inputs.

The money goes beside the plans for the same reason. The NPV change, $-1,174$k, is the price of the
cut. The spend change explains the shifts: 2029 spends $2,940k less, more than the $2,760k cut,
because the cut plan leaves $310k of 2029 unused against $130k in the base. And three other years
spend more, which is where the projects that moved went.

<!-- practice 1 -->

## Change One Input at a Time, or the Diff Cannot Be Charged to a Cause

Planners rarely stop at one change. Suppose they cut 2029 *and* force P024 in. `diff_chain.py`
reaches the same final scenario by two paths, one change per step, and diffs each step:

```text
base -> cut -> cut+P024
  base -> cut       NPV -1,174  selected ['P002', 'P037']  deferred ['P001', 'P005', 'P016']  shifted 6
   cut -> cut+P024  NPV   -205  selected ['P001', 'P024']  deferred ['P002', 'P023', 'P037']  shifted 8
  whole path      NPV -1,379  selected ['P024']  deferred ['P005', 'P016', 'P023']  shifted 9
base -> P024 -> cut+P024
  base -> P024      NPV   -273  selected ['P024', 'P037']  deferred ['P005', 'P009', 'P016']  shifted 3
  P024 -> cut+P024  NPV -1,106  selected ['P009']  deferred ['P023', 'P037']  shifted 7
  whole path      NPV -1,379  selected ['P024']  deferred ['P005', 'P016', 'P023']  shifted 9
```

The end is the same both ways: $-1,379$k, and the same plan. The steps are not. Forcing P024 in costs
$273k on the base and $205k after the cut; the cut costs $1,174k on the base and $1,106k once P024
is in. Neither number is wrong. Each is the cost of one change *given* the other, and the two changes
interact through the same budget rows. Even the project lists disagree: on the first path P001 is
deferred by the cut and selected again by the override, so the whole-path diff never shows it.

Three habits follow.

- **Diff each step, and keep the path.** A diff between two scenarios that differ in two inputs says
  what changed, not which input caused what. The chain of single-change diffs does.
- **State the order with every attribution.** "The override costs $205k" is true after the cut and
  false before it. Write "forcing P024 in, after the 2029 cut, costs $205k".
- **Add step costs only along one path.** $1,174k + $205k and $273k + $1,106k both give $1,379k;
  $1,174k + $273k does not, because those two steps start from the same scenario.

## A Diff Worth a Few Thousand Is a Near Tie, Not a Decision

The last check is the size of the diff against the plan. `near_tie.py` asks for the best plan of the
base scenario that is *not* the best plan, by adding the `not_best` row of *The Model*. The row's
left side reaches $`|S^*|`$ only when every start variable of the best plan is 1 and every other one
is 0, so it removes that one plan and nothing else:

```python
built.model.add_linear_constraint(sum(chosen) - sum(others) <= len(chosen) - 1, name="not_best")
second = solve(built)
```

```text
best   OPTIMAL  NPV $24,260k
second OPTIMAL  NPV $24,252k
  selected  []
  deferred  []
  shifted earlier ['P029 2031->2030']
  shifted later   ['P018 2030->2031']
  NPV change $-8k
  spend change by year 2027: +0, 2028: +0, 2029: +0, 2030: -10, 2031: +10
the two differ by 0.033% of the best NPV
```

A second plan exists $8k below the best, with two projects trading years. Every run in this module
solves to a relative gap of 0, so it must return a plan worth $24,260k, and the second plan is not
one. A solve allowed to stop at a relative gap of 0.1% has no such duty: both plans are within 0.1%
of the best bound, so it may stop at either, and a diff between two such runs could show P018 and
P029 moving with nothing in the inputs changed. Lesson 10.2.3 is about this case, alternative and nearly equal optima,
and how to break the tie on purpose.

So a diff must print its NPV change, and a reader must weigh changes by it. Two runs whose diff is
worth 0.033% of the plan have made the same decision with a coin toss on the details; two runs whose
diff is worth 5% have made different decisions. The same scale reads the forcing costs of lesson
9.3.2: the $8k there was this very plan.

<!-- practice 2 -->

## Summary

- **A diff compares plans project by project, in three lists.** Selected, deferred, shifted (earlier
  or later), keyed by project id, never by variable or position. Pair swaps within an alternative
  group.
- **A plan diff needs the input diff and the money beside it.** List every changed input (equal
  snapshots mean none), the NPV change and the spend change by year.
- **Change one input at a time, or the diff cannot be charged to a cause.** On GridCap the P024
  override costs $273k before the 2029 cut and $205k after it; report the path and the order.
- **A diff worth a few thousand is a near tie, not a decision.** GridCap small's second-best plan is
  $8k (0.033%) below the best and differs by two shifts.

## Reference

| List | Definition | GridCap base to cut-2029 |
| --- | --- | --- |
| selected | in $`b`$, not in $`a`$ | P002, P037 |
| deferred | in $`a`$, not in $`b`$ | P001, P005, P016 |
| shifted earlier | in both, $`b(i) < a(i)`$ | P008, P011, P012, P021 |
| shifted later | in both, $`b(i) > a(i)`$ | P025, P035 |

| A diff report holds | Why |
| --- | --- |
| the three lists, by project id | what changed, in the planner's terms |
| the inputs changed, and both snapshots | what caused it, and proof nothing else changed |
| the NPV change | how much it matters; small means a near tie |
| the spend change by year | where the money and the shifted work went |
| the path of single changes | which input is charged with which change, in which order |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt)
(a model kept apart from its solve, which is what lets two scenarios be built from data and solved
the same way); [MathOpt `linear_constraints.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/linear_constraints.py)
(a row added by `add_linear_constraint` to an existing model, as the `not_best` row is);
[MathOpt `result.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py)
(the docstring of `best_objective_bound`, the bound a gap tolerance is measured against);
[Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf)
(section 9.1: the multi-period cash-flow rows whose right-hand sides a scenario changes). The CIPT
job (lesson 9.3.1) asks for selected and deferred investments and differences between scenarios
among the outputs planners read.

## Challenges

1. Diff the base against a scenario whose 2029 budget is $9,760k ($1,000k more). Predict whether any
   project is deferred, then run it.
2. Add a fourth list to `diff_scenarios`, the swaps within alternative groups, and print it for the
   2029 cut.
3. Run `near_tie.py` again with the second-best plan also cut off. Predict whether the third-best
   plan is within $64k of the best, the cost of the cheapest forcing in lesson 9.3.2 that drops a
   project.

## Design Note: Diff Results, Not Models

It is tempting to diff the two *models*: which rows and bounds differ. That diff is easy to compute
and almost useless to a planner. One changed number on `budget_2029` explains nothing about P001 or
P035, and in a real system the two models may have been built by different code versions, so their
rows differ for reasons no scenario chose. Diff the inputs, which people changed, and the plans,
which people act on; leave the model out of it. When the inputs are equal and the plans are not, the
cause is in the run itself (settings, versions, ties), and lessons 10.2.1 to 10.2.4 are about that
case.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**scenario_diff.py.** Solves the base and the 2029-cut scenarios and prints the input diff and the
plan diff (*A Diff Compares Plans* and *A Plan Diff Needs the Input Diff*). *Try:* Cut 2028 instead of
2029, by the same $2,760k. Predict whether more or fewer projects shift.

- Program: [scenario_diff.py](src/scenario_diff.py)

**diff_chain.py.** Reaches the cut-plus-P024 scenario by two paths and diffs every step (*Change One
Input at a Time*). *Try:* Replace the P024 override with forcing P032 out. Predict whether the two
paths still charge different costs to each step.

- Program: [diff_chain.py](src/diff_chain.py)

**near_tie.py.** Finds the second-best plan with a no-good row and diffs it against the best (*A Diff
Worth a Few Thousand Is a Near Tie*). *Try:* Run it on the cut scenario instead. Predict whether its
runner-up is as close.

- Program: [near_tie.py](src/near_tie.py)

**diffs.py.** `diff_scenarios`, `input_changes` and the printed form of a diff. It runs nothing
itself.

- Library: [diffs.py](src/diffs.py)
