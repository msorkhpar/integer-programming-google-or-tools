# 4.6.2 Hints, Assumptions and `SufficientAssumptionsForInfeasibility`

Every year GridCap re-plans its portfolio, and two questions come back each time. First: last
year's plan was good, so can the solver start from it instead of from nothing? Second: when the
regulator's scenario cuts the budget and the model answers `INFEASIBLE` (no plan keeps every rule),
which of the dozens of rules are to blame? CP-SAT answers the first with **solution hints** and the
second with **assumptions**. This lesson shows both on GridCap, and what each one does and does not
promise.

GridCap is a fictional utility's portfolio; none of its numbers are real. The model is the one
of lesson 4.6.1, `cpsat_plan.build`.

## The Model

The plan is lesson 4.6.1's model with one change, marked below: every rule group except "once"
gets its own Boolean **flag**, and the rule holds only when its flag is 1. This is what
`cpsat_plan.build(portfolio, flags=True)` builds; the rule names are the labels.

**Sets.** $`P`$ the projects; $`Y`$ the years; $`T_i`$ the start years of project $`i`$; $`M`$
the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C`$ the child projects, with parent
$`p(c)`$ and lag $`L_c`$; $`G`$ the programs; $`R`$ the rule names: one per must-do project, group,
child and start year, budget year, and program and year with crew work.

**Parameters.** $`\text{npv}_{i,t}`$, $`c_{i,k}`$, $`B_y`$, $`m_i`$, $`K_{g,y}`$, $`d_i`$ as in
lesson 4.6.1; $`s`$, the scenario's budget factor (0.97 for the budget cut in the hint sections,
0.6 in the infeasible scenario).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$: project $`i`$ starts
in year $`t`$. $`f_r \in \{0, 1\}`$ for every $`r \in R`$: rule $`r`$ is on. $`\leftarrow`$ new

**Objective.** $`\max \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}`$

**Constraints.** Each row except once$`_i`$ holds only if its flag is 1 ($`f \Rightarrow \text{row}`$,
written `.only_enforce_if(flag)`).

```math
\begin{aligned}
& \sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P && \text{(once}_i) \\
f_{\text{must}_i} \Rightarrow\;& \sum_{t \in T_i} x_{i,t} \ge 1 && \forall i \in M && \text{(must}_i) \\
f_{\text{alt}_g} \Rightarrow\;& \sum_{i \in g} \sum_{t \in T_i} x_{i,t} \le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
f_{\text{after}_{c,t}} \Rightarrow\;& \sum_{u \in T_c,\, u \le t} x_{c,u} \le \sum_{r \in T_{p(c)},\, r \le t - L_c} x_{p(c),r} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
f_{\text{budget}_y} \Rightarrow\;& \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} \le \lfloor s\, B_y \rfloor && \forall y \in Y && \text{(budget}_y) \\
f_{\text{crews}_{g,y}} \Rightarrow\;& \sum_{i:\ \text{program}(i) = g} \ \sum_{t \in T_i,\ t \le y < t + d_i} m_i\, x_{i,t} \le K_{g,y} && \forall g \in G,\ y \in Y && \text{(crews}_{g,y})
\end{aligned}
```

The **assumptions** are $`f_r = 1`$ for every $`r \in R`$: the solver must treat every rule as on.
Without assumptions, the flags are ordinary variables and the solver would switch rules off to
earn more NPV. The table maps labels to rule names, as in lesson 4.6.1:

| Label | Rule name |
| --- | --- |
| must$`_i`$, alt$`_g`$ | `must_P017`, `alt_G001` |
| after$`_{c,t}`$ | `after_P023_2029` |
| budget$`_y`$, crews$`_{g,y}`$ | `budget_2030`, `crews_vegetation_2031` |

The flagged model is used from the section on assumptions on. The hint sections use the plain
model of lesson 4.6.1.

## A Hint Is a Suggested Plan, Never a Constraint

A **solution hint** is a value you suggest for a variable: `model.add_hint(var, value)`. The
OR-Tools sample `solution_hinting_sample_sat.py` hints two of three variables; the CP-SAT docs say
a hint may cover only some variables, may even be infeasible, and that the solver tries to follow it
for a while before returning to its usual search. It is guidance, not a rule: no plan is ever
refused for disagreeing with a hint.

The natural hint is last cycle's plan. The program takes the plan one worker finds on GridCap
medium with 3 units of work, then re-plans with 1 unit, with and without hinting it. Each start
variable gets a hint, 1 if the old plan starts the project in that year and 0 otherwise:

```python
def hint_plan(plan, starts: dict[str, int]) -> None:
    """Hint every start variable: 1 for the year the old plan starts the project, 0 otherwise."""
    for (pid, t), var in plan.x.items():
        plan.model.add_hint(var, 1 if starts.get(pid) == t else 0)
```

A solution callback (lesson 4.4.3) records the first plan found and counts the improving plans:

```text
last cycle's plan: $215,024k, 210 projects
same budgets    no hint  FEASIBLE  first $208,873k  best $214,532k  plans 13
same budgets    hint     FEASIBLE  first $215,024k  best $215,109k  plans 5
```

With the hint, the first plan the solver reports is the hint itself, $215,024k, and the search
improves on it to $215,109k. Without it, the solver starts at $208,873k and ends at $214,532k with
the same work. When the rules have not changed, a hint is a head start.

Now cut every year's budget by 3%, the kind of change a rate case brings:

```text
budgets cut 3%  no hint  FEASIBLE  first $207,700k  best $210,101k  plans 12
budgets cut 3%  hint     FEASIBLE  first $203,373k  best $209,900k  plans 12
```

The old plan overspends the new budgets, so it is no longer a plan at all. The hinted run still
works (a hint is never a constraint), but it is no better: its first plan is worse than the
unhinted one, and it ends $201k lower. A hint helps when it is a plan of the model you are solving.
Before trusting one, check it.

Two related settings from the parameters proto: `use_optimization_hints` (on by default) makes the
search follow the hint, and `repair_hint` asks the solver to try to repair an infeasible hint into a
feasible one. `model.clear_hints()` removes every hint, for example before trying another one.

## Fixing Every Variable to Its Hint Tests Whether the Hint Is Feasible

`solver.parameters.fix_variables_to_their_hinted_value = True` turns the hint into a constraint:
every hinted variable is fixed to its hinted value. If every variable is hinted, nothing is left to
decide, and the solve answers one question: does this exact plan keep every rule? The CP-SAT Primer
recommends this as the dependable way to check a hint.

```python
check = build(medium, budget_scale=scale)
hint_plan(check, last_cycle)
solver = one_worker()
solver.parameters.fix_variables_to_their_hinted_value = True
status = solver.solve(check.model)
```

```text
same budgets    is last cycle's plan still feasible? OPTIMAL
budgets cut 3%  is last cycle's plan still feasible? INFEASIBLE
```

`OPTIMAL` here means "the one plan left is feasible, so it is also the best of the plans left",
and `INFEASIBLE` means the old plan breaks a rule of the new model. Hint *every* variable, the
zeros included. The setting fixes hinted variables only; a variable with no hint stays free for the
solver to set. A check that hints only the ones would therefore accept a plan that leaves out a
must-do project, since the solver is free to switch that project on.

<!-- practice 1 -->

## An Assumption Is a Literal the Solver Must Take as True

A **literal** is a Boolean variable or its negation. An **assumption** is a literal the solver must
treat as true for this solve: `model.add_assumptions([a, b, c])`. It works like adding $`a = 1`$,
with one difference that is the point of this lesson: when the model is infeasible, the solver can
report which assumptions it needed to prove that. So you guard each rule with its own flag, written
`model.add(...).only_enforce_if(flag)` (lesson 4.4.2), and assume every flag.

The OR-Tools sample `assumptions_sample_sat.py` shows the mechanics with three rules that cannot
hold together, $`x > y`$, $`y > z`$ and $`z > x`$, each guarded by a flag:

```python
model.add(x > y).only_enforce_if(a)
model.add(y > z).only_enforce_if(b)
model.add(z > x).only_enforce_if(c)
model.add_assumptions([a, b, c])

solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
status = solver.solve(model)
```

```text
cycle: INFEASIBLE, sufficient assumptions [3, 4, 5]
variable indices: {'x': 0, 'y': 1, 'z': 2, 'a': 3, 'b': 4, 'c': 5}
```

`solver.sufficient_assumptions_for_infeasibility()` returns **variable indices**, not names or
variable objects: 3, 4 and 5 are the indices of `a`, `b` and `c` (each variable's `.index`). Your
program keeps a map from index to rule name to turn them back into something a planner can read.
The name in this lesson's title, `SufficientAssumptionsForInfeasibility`, is the C++ spelling; the
Python API of OR-Tools 9.15 spells it in snake_case.

The OR-Tools troubleshooting page adds a requirement: assumptions do not work with parallel search,
so set `num_workers = 1` for these solves. Every program in this lesson does.

## sufficient_assumptions_for_infeasibility Names Flags That Clash, Not Always the Fewest

The name says what the method promises: a set of assumptions that is **sufficient** to make the
model infeasible. The troubleshooting page says the set is minimized but not guaranteed minimal.
How far from minimal it can be depends on the model, and two runs show both ends.

With four flagged rules of which only two clash, "at least 5 crews" and "at most 3 crews", the
solver names exactly those two:

```python
by_index = {flag.index: name for name, flag in flags.items()}
print(f"four rules: {solver.status_name(status)}, sufficient assumptions "
      f"{[by_index[i] for i in solver.sufficient_assumptions_for_infeasibility()]}")
```

```text
four rules: INFEASIBLE, sufficient assumptions ['crews_min', 'crews_max']
```

Now GridCap. The scenario keeps 60% of every year's budget on the small portfolio, every rule group
has a flag, and every flag is assumed:

```python
def conflict(assumed: list[str]) -> list[str] | None:
    """Solve with the named flags assumed. None if feasible, else the flags the solver names."""
    plan = build(small, budget_scale=SCENARIO, flags=True)
    plan.model.add_assumptions([plan.flags[name] for name in assumed])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1                # assumptions need a single worker
    status = solver.solve(plan.model)
    if status != cp_model.INFEASIBLE:
        return None
    by_index = {flag.index: name for name, flag in plan.flags.items()}
    return [by_index[i] for i in solver.sufficient_assumptions_for_infeasibility()]
```

```text
28 rule flags, e.g. must_P003, alt_G001, crews_vegetation_2031
sufficient set: 28 of 28 flags
```

Every flag comes back. The answer is true (all 28 rules together are infeasible) but useless: it
tells the planners nothing they did not know. The method never promised a short list, only a
sufficient one. To get an answer a planner can act on, shrink it.

<!-- practice 2 -->

## A Deletion Filter Shrinks the Named Flags to a Minimal Set

A set of rules is a **minimal** clash when the rules in it cannot all hold, but dropping any one of
them leaves a set that can. (This is the CP-SAT counterpart of the irreducible infeasible subsystem,
or IIS, that MathOpt's `compute_infeasible_subsystem` finds in lesson 4.3.5.)

The **deletion filter** finds one with one solve per rule. Start from the sufficient set. For each
rule in turn, solve with that rule switched off and the rest still assumed. If the model is still
infeasible, the rule was not needed: leave it out for good. If it becomes feasible, the rule is part
of the clash: keep it.

```python
def minimal(core: list[str]) -> list[str]:
    """Deletion filter: drop each flag in turn and keep it out if the rest is still infeasible."""
    kept = list(core)
    for name in list(core):
        trial = [n for n in kept if n != name]
        if conflict(trial) is not None:
            kept = trial
    return kept
```

Switching a rule off is just not assuming its flag: the flag is then a free variable, and the
solver sets it to 0 whenever the rule is in the way.

```text
minimal set: ['must_P017', 'budget_2030', 'budget_2031']
  drop must_P017    -> feasible
  drop budget_2030  -> feasible
  drop budget_2031  -> feasible
P017: must-do, costs $5,310k, may start 2030-2031; 2030 budget $5,166k, 2031 budget $4,710k
```

Twenty-eight rules shrink to three, and the three tell a story a planner understands at once: P017
is a must-do project costing $5,310k in a single year, it may start only in 2030 or 2031, and at
60% neither year's budget can pay for it. Every check the program prints confirms the set is
minimal: dropping any one of the three rules makes the scenario feasible. The three answers are
also the three ways out: make P017 optional, or raise the 2030 or the 2031 budget.

Two cautions. The filter costs one solve per rule in the sufficient set, so on a model with
thousands of flags, group rules (one flag per budget year rather than per row, as here) before you
start. And a model can hold several separate clashes; the filter returns one of them. Fix it, run
again, and the next one appears.

<!-- practice 3 -->

## Summary

- **A hint is a suggested plan, never a constraint.** Last cycle's plan is a head start when it
  is still feasible, and no help when it is not.
- **Fixing every variable to its hint tests whether the hint is feasible.** Hint every variable,
  zeros included, and set `fix_variables_to_their_hinted_value`.
- **An assumption is a literal the solver must take as true.** Guard each rule with a flag via
  `only_enforce_if`, assume every flag, and use one worker.
- **`sufficient_assumptions_for_infeasibility` names flags that clash, not always the fewest.** It
  returns variable indices; map them to rule names. On GridCap it named all 28.
- **A deletion filter shrinks the named flags to a minimal set.** One solve per rule; what is left
  is a clash with no rule to spare.

## Reference

| Call or setting | What it does |
| --- | --- |
| `model.add_hint(var, value)` | suggest a value; never a constraint |
| `model.clear_hints()` | remove every hint |
| `solver.parameters.fix_variables_to_their_hinted_value = True` | fix every hinted variable to its hint |
| `model.add(row).only_enforce_if(flag)` | the row holds only when `flag` is 1 |
| `model.add_assumptions([f1, f2])`, `model.add_assumption(f)` | the solver must take these literals as true |
| `model.clear_assumptions()` | remove every assumption |
| `solver.sufficient_assumptions_for_infeasibility()` | after `INFEASIBLE`: indices of assumed literals that together are infeasible |
| `var.index` | a variable's index, to map indices back to names |

| Question | Tool |
| --- | --- |
| Can the solver start from last cycle's plan? | `add_hint` on every variable |
| Is last cycle's plan still feasible? | hints plus `fix_variables_to_their_hinted_value` |
| Which rules make the scenario infeasible? | flags, assumptions, `sufficient_assumptions_for_infeasibility` |
| Which of those are really needed? | deletion filter |

**Further reading:** [CP-SAT samples: `assumptions_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/assumptions_sample_sat.py)
and [`solution_hinting_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/solution_hinting_sample_sat.py),
[CP-SAT model docs: solution hints](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/model.md),
[CP-SAT troubleshooting: assumptions](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md),
[CP-SAT parameters proto](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`fix_variables_to_their_hinted_value`, `repair_hint`, `use_optimization_hints`), and
[The CP-SAT Primer: Parameters](https://d-krupke.github.io/cpsat-primer/parameters.html) (hints and
assumptions).

## Challenges

1. Change `which_flags.py` to use 70% of the budget. Is the scenario still infeasible?
2. Instead of a minimal clash, a planner may want the fewest rules to switch off to make the
   scenario feasible. Write it: make the flags free, and maximize the number of flags that are 1.
3. Hint only the projects last cycle's plan starts, not the zeros, and set
   `fix_variables_to_their_hinted_value`. Which plan does the solver return, and why is it not last
   cycle's?

## Design Note: One Flag per Rule Group

`cpsat_plan.build` gives one flag to each must-do project, group, budget year and program-year,
not one per variable or per coefficient. That choice sets the vocabulary of the answer: the deletion
filter can only name things that have flags. A flag per row is the finest answer a planner can act
on (a row is a rule they wrote); a flag per rule family ("all budgets", "all crews") is cheaper to
filter and is a good first pass on a large model, followed by a finer pass inside the family it
names.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**hints.py.** Last cycle's plan as a hint on GridCap medium, with the same budgets and with a 3%
cut, and the fixed-hint feasibility check (*A Hint Is a Suggested Plan, Never a Constraint* and
*Fixing Every Variable to Its Hint Tests Whether the Hint Is Feasible*). *Try:* Hint only every
second project. Predict the first plan's value before you run it.

- Program: [hints.py](src/hints.py)

**assumptions_sample.py.** The OR-Tools assumptions sample, adapted, and a second model where only
two of four rules clash (*An Assumption Is a Literal the Solver Must Take as True*). *Try:* Add a
fifth rule `crews >= 4` with its own flag. Which flags come back?

- Program: [assumptions_sample.py](src/assumptions_sample.py)

**which_flags.py.** The GridCap scenario at 60% of the budget: all flags assumed, the sufficient
set, and the deletion filter (*A Deletion Filter Shrinks the Named Flags to a Minimal Set*).
*Try:* Remove `must_P017` from the assumed flags first. Which clash does the filter find next?

- Program: [which_flags.py](src/which_flags.py)
