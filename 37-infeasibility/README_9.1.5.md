# 9.1.5 CP-SAT Assumptions as a Conflict Finder

Lesson 4.6.2 met CP-SAT's **assumptions**: guard each rule with a Boolean flag, assume every flag
true, and when the model is infeasible the solver names a set of flags that cannot all hold. On
GridCap small at 60% of the budget it named all 28 flags, and a deletion filter cut them to 3. The
Budget Lock scenario is a different case: it has three conflicts (lesson 9.1.3), and the planners
want all of them, in the rows they can change, with as few solves as possible. This lesson runs the
same scenario through CP-SAT. It lists every conflict, controls which conflict a filter returns,
filters whole families of rules before single rows, and finds the fewest rules to switch off.
GridCap is a fictional utility; none of its numbers are real.

## The Model

The model of lesson 9.1.1 with one change, marked: every row except once$`_i`$ holds only when its
flag is 1. `convert.to_cpsat(model, flagged=...)` copies the MathOpt model into CP-SAT row for
row, which works because CP-SAT works over the integers and all of GridCap's data are integers,
and guards each named row with
`.only_enforce_if(flag)`.

**Sets.** As in lesson 9.1.1, plus $`\mathcal{R}`$, the flagged rows: every row except once$`_i`$
(34 on the Budget Lock scenario). $`\leftarrow`$ new

**Parameters.** As in lesson 9.1.1, with the Budget Lock scenario's values.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$, as before; and
$`f_r \in \{0, 1\}`$ for every $`r \in \mathcal{R}`$: rule $`r`$ is on. $`\leftarrow`$ new

**Objective.** None for the conflict questions: each is a feasibility question, so the copy's
objective is cleared. The last section maximizes $`\sum_{r \in \mathcal{R}} f_r`$.

**Constraints.** once$`_i`$ as in lesson 9.1.1, and every other row of that lesson guarded by its
flag ($`f_r \Rightarrow \text{row } r`$):

```math
\begin{aligned}
& \sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
f_r \Rightarrow\;& \ell_r \le a_r^\top x \le u_r && \forall r \in \mathcal{R} && (r) \quad \leftarrow \text{new}
\end{aligned}
```

Here $`\ell_r \le a_r^\top x \le u_r`$ is row $`r`$ of lesson 9.1.1 written with both of its
bounds (one of them infinite for an inequality). For example, $`f_{\text{budget}_{2028}}
\Rightarrow \sum_i \sum_t c_{i,2028-t}\, x_{i,t} \le 6{,}000`$. The **assumptions** are
$`f_r = 1`$ for every $`r`$ in the set being asked about. A flag that is not assumed is a free
variable, so the solver may set it to 0 and switch its rule off.

## Assumptions Need Flags, One Worker and a Map From Index to Name

Lesson 4.6.2 set out the mechanics, and `conflict` here uses them unchanged. It builds the flagged
copy, assumes the named flags, solves with one worker, and turns the indices the solver returns
back into row names:

```python
def conflict(assumed: list[str]) -> list[str] | None:
    """Solve with the named flags assumed true. None if feasible, else the flags the solver names."""
    global solves
    solves += 1
    model, flags = to_cpsat(lm.model, flagged=RULES)
    model.clear_objective()                           # a feasibility question
    model.add_assumptions([flags[n] for n in assumed])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1                 # assumptions need a single worker
    if solver.solve(model) != cp_model.INFEASIBLE:
        return None
    name = {flags[n].index: n for n in RULES}
    return [name[i] for i in solver.sufficient_assumptions_for_infeasibility()]
```

Three points carry over from lesson 4.6.2 and the CP-SAT troubleshooting page.
`sufficient_assumptions_for_infeasibility()` returns variable indices, not names. Assumptions do
not work with parallel search, hence one worker. And the set is **sufficient**: it is reduced, but
not promised to be minimal. A common claim says it returns "a minimal core". The troubleshooting
page does not say that, and lesson 4.6.2 measured a set of all 28 flags.

The flagged model is built afresh for every question, so that no assumption from an earlier
question stays behind (`model.clear_assumptions()` would also do).

## Here the Solver Named a Minimal Set at Once, So Every Conflict Costs One Solve

All 34 flags assumed:

```text
34 flags assumed; sufficient set: 3 flags, ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017']
```

This time CP-SAT named three flags, P017's conflict, the same three rows the reversed deletion filter
found in lesson 9.1.3. How small the set comes out depends on how the solver proved infeasibility,
and that changes from model to model. Here it was small. On lesson 4.6.2's scenario it was
everything.

When the named sets are small, listing every conflict is cheap. Switch off one named row (one the
planners set, when there is one), ask again, and repeat:

```python
assumed = list(RULES)
while (named := conflict(assumed)) is not None:
    off = next((n for n in named if n.startswith(PLANNERS)), named[0])   # a planners' row if there is one
    print(f"named {sorted(named)} -> switch off {off}")
    assumed.remove(off)
```

```text
named ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017'] -> switch off crews_transmission_2030
named ['after_P023_2029', 'budget_2028', 'force_P023', 'force_P032_2028'] -> switch off budget_2028
named ['after_P023_2029', 'crews_transmission_2028', 'force_P023', 'force_P032_2028'] -> switch off crews_transmission_2028
feasible with 3 rows off (4 solves)
```

The three conflicts of lesson 9.1.3, in 4 solves. The HiGHS loop of that lesson needed 211: a
deletion filter costs one solve per active row, and each conflict found switched one row off, so
the three filters cost 70, 69 and 68 solves, plus 4 checks of whether the active rows were still
infeasible (70 + 69 + 68 + 4 = 211). Each set CP-SAT named here is one of the
irreducible sets that lesson found, so no filter was needed this time. Nothing promises that, so a
program that reports conflicts must still check: run the deletion filter on the named set, which
costs one solve per named row. On a set of 3 or 4 that is cheap. On 28 it is lesson 4.6.2's case.

<!-- practice 1 -->

## The Order of a Deletion Filter Chooses Which Conflict You Get

When the named set is large, or when you want a conflict made of certain rows, run the deletion
filter yourself on the flags. `minimal` is lesson 4.6.2's filter. As lesson 9.1.3 showed, it keeps
the conflict whose rows come last in its order. Here it runs over all 34 flags twice, once with the
rows planners set (budgets, crews, floors, overrides) first and once with them last:

```python
for label, order in (("planners' rows tested first", theirs + model_rules),
                     ("planners' rows tested last ", model_rules + theirs)):
```

```text
planners' rows tested first: ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017']  (34 solves)
planners' rows tested last : ['after_P023_2029', 'crews_transmission_2028', 'force_P023', 'force_P032_2028']  (34 solves)
```

Tested first, the planners' rows are dropped whenever another conflict can hold without them. The
2028 rows and the overrides go, and P017's conflict survives, because its must-do row is tested
late. Tested last, the must-do row is dropped early, and the conflict that survives is the
overrides' one, made almost entirely of rows the planners set. For a message to the board, the
second order gives the conflict they can act on. Either way the cost is one solve per flag.

## Filter Whole Families First, Then the Rows Inside Them

Lesson 4.6.2's design note suggested a cheaper pass on large models: one switch per rule
**family** first, then single rows only inside the families that matter. A family here is the
prefix of a row's name: `budget`, `crews`, `floor`, `force`, `must`, `alt`, `after`. The first pass
is a deletion filter whose items are whole families:

```python
family = {n: n.split("_")[0] for n in RULES}                   # budget_2028 -> budget
solves = 0
kept = sorted(set(family.values()))
for f in list(kept):
    if conflict([n for n in RULES if family[n] in kept and family[n] != f]) is not None:
        kept.remove(f)
```

```text
families: ['after', 'alt', 'budget', 'crews', 'floor', 'force', 'must'] -> needed ['crews', 'must']  (7 solves)
rows of those families: 19; minimal: ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017']  (26 solves in all)
```

Seven solves to learn that crews and must-do rows alone are enough for a conflict, then 19 to
filter the 19 rows of those two families: 26 solves against 34. The saving grows with the model: a
family pass costs one solve per family, however many rows each family holds. The first pass drops
the `after` family first, which is why the override conflicts (which need P023's precedence row)
do not survive it. The order of the families matters just as the order of the rows did.

<!-- practice 2 -->

## The Fewest Rules to Switch Off Is an Optimization, Not an Assumption

A minimal conflict answers "which rules clash?". The planners' next question is "what is the
fewest rules we could drop to get a plan?". That is a different set: one that meets every conflict
(it **hits** each one), rather than one conflict. Assumptions do not answer it. An objective does.
Make every flag free, with no assumptions, and maximize the number of flags left on:

```python
model, flags = to_cpsat(lm.model, flagged=RULES)
model.maximize(sum(flags.values()))
```

```text
fewest rows off: 2, ['crews_transmission_2030', 'force_P032_2028']
```

Two rows: the 2030 transmission crews (P017 can then start in 2030) and the board's P032 override,
which is in both override conflicts. The counting objective of lesson 9.1.4 also found 2, with a
different pair, `must_P017` and `force_P023`. Both pairs hit all three conflicts, and the count
proves no single row does. When several answers tie, a solver returns one of them, so a report
should say "for example" or add a rule that breaks the tie, such as weights that make must-do rows
expensive. The CP-SAT troubleshooting page makes a similar point about minimality. For a set that
is truly smallest, optimize over the literals rather than rely on the sufficient set.

## Summary

- **Assumptions need flags, one worker and a map from index to name.** The set the solver names is
  sufficient, not promised minimal.
- **Here the solver named a minimal set at once, so every conflict cost one solve:** the three
  conflicts in 4 solves, against 211 with HiGHS and a filter. Check a named set with a filter
  before reporting it as minimal.
- **The order of a deletion filter chooses which conflict you get.** Put the rows you want named
  last. One solve per flag.
- **Filter whole families first, then the rows inside them:** 7 + 19 = 26 solves instead of 34.
- **The fewest rules to switch off is an optimization, not an assumption.** Maximize the flags
  left on. Two rows here, and the answer ties with lesson 9.1.4's.

## Reference

| Call | What it does |
| --- | --- |
| `ct.only_enforce_if(flag)` | the row holds only when `flag` is 1 |
| `model.add_assumptions([f, ...])` | the solver must take these literals as true |
| `model.clear_assumptions()`, `model.clear_objective()` | remove every assumption; drop the objective |
| `solver.parameters.num_workers = 1` | required with assumptions |
| `solver.sufficient_assumptions_for_infeasibility()` | after `INFEASIBLE`: indices of assumed literals that together are infeasible |
| `model.maximize(sum(flags))` with no assumptions | fewest rules switched off |

| Question | Method | Solves here |
| --- | --- | --- |
| one conflict | assume all, read the sufficient set | 1 |
| every conflict | read, switch one row off, repeat | 4 |
| a minimal conflict of chosen rows | deletion filter, chosen rows last | 34 |
| the same, cheaper | families first, then rows | 26 |
| fewest rules to drop | maximize the flags left on | 1 (an optimization) |

**Further reading:** OR-Tools,
[CP-SAT troubleshooting](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md)
(assumptions, one worker, a sufficient set that is not guaranteed minimal), the sample
[`assumptions_sample_sat.py`](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/assumptions_sample_sat.py),
and the [CP-SAT solver page](https://developers.google.com/optimization/cp/cp_solver) (its
statuses, and that CP-SAT works over the integers). Gurobi's
[infeasibility example tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html)
(`workforce2`, the same "find, remove one, look again" loop with an IIS).

## Challenges

1. Run the "every conflict" loop switching off `named[-1]` instead of a planners' row. Predict how
   many conflicts it reports.
2. Order the family pass so that `crews` comes first. Predict which families it keeps.
3. Add the constraint "must-do flags stay on" to the fewest-rows model. Predict the new count.

## Design Note: Ask the Solver for the Cheap Part, Check the Rest Yourself

CP-SAT's sufficient set costs nothing extra: it comes with the `INFEASIBLE` answer. Whether it is
minimal costs one solve per member to check. A conflict finder that uses the free answer, then
checks it before reporting, gets the speed of the first and the guarantee of the second. When the
check finds the set already minimal, as on every set here, it has cost a few solves. When it does
not, as in lesson 4.6.2, the planners never see 28 rules called "the conflict".

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**assume_lock.py.** The sufficient set, every conflict, the deletion filter in two orders, the
family pass, and the fewest rows to switch off (*every section*). *Try:* Leave `num_workers` at its
default. Predict what the solver does with the assumptions.

- Program: [assume_lock.py](src/assume_lock.py)

The CP-SAT copy is built by a library.

- Library: [convert.py](src/convert.py)
