# 6.5.6 Manual Overrides as Fixed Bounds

The optimizer has proposed a plan for GridCap's small portfolio, and the planners have notes on it.
Engineering wants the Coast repair P036 in 2028, because the asset failed an inspection. The Valley
repair P032 has to wait for a study, so it is out of this plan. No Coast crew is free before 2030,
so P021 may not start earlier. And the board wants the Ridge undergrounding P024 in the plan, in
whatever year suits. Each note is a **manual override**: a decision a person makes about one
project, which the model must respect without being rebuilt. This lesson writes overrides as bounds
on the start variables, undoes them, prices them, and checks them against the model's rules, in
four rules.

GridCap is a fictional utility's portfolio, generated for this course; the overrides are invented
for the lesson.

## An Override on Start Variables Is a Bound, Not a Row

Every start variable $`x_{i,t}`$ already has bounds: $`0 \le x_{i,t} \le 1`$, with integrality
making it 0 or 1. An override that fixes start variables only needs to change those bounds:

- **Start in year $`y`$**: lower bound of $`x_{i,y}`$ set to 1. The project's once row then forces
  its other years to 0; setting their upper bounds to 0 as well says so directly.
- **Never fund**: upper bound 0 on every $`x_{i,t}`$ of the project.
- **Not before year $`y`$**: upper bound 0 on $`x_{i,t}`$ for every $`t < y`$.

None of these adds a row. A bound is part of the variable, so the model's rows stay exactly as the
builder wrote them, and an override can never be mistaken for a business rule. The OR-Tools MathOpt sample
`time_indexed_scheduling.py` uses the same move for jobs with release times: a start variable for a
time before the release gets `upper_bound = 0`.

One kind of override is not about a single variable. **"Fund it, in any year"** is
$`\text{started}(i) = \sum_{t \in T_i} x_{i,t} = 1`$, a rule on a sum, and a sum needs a row. It is
the must-do row of lesson 6.5.1, added by a person instead of by the data.

```python
@dataclass(frozen=True)
class Override:
    pid: str
    kind: str              # "in" (fund, any year), "year" (start in `year`), "out" (never), "not_before"
    year: int | None = None


def apply(plan, o: Override) -> list:
    """Apply one override; return what undoes it: (variable, old lower, old upper) or a row to delete."""
    undo = []
    years = plan.portfolio.project(o.pid).starts()
    if o.kind == "in":                                   # a rule on a sum of variables: a row
        row = plan.model.add_linear_constraint(plan.started(o.pid) == 1, name=f"override_{o.pid}")
        return [row]
    for t in years:
        v = plan.x[o.pid, t]
        undo.append((v, v.lower_bound, v.upper_bound))
        if o.kind == "out" or (o.kind == "not_before" and t < o.year) or (o.kind == "year" and t != o.year):
            v.upper_bound = 0
        if o.kind == "year" and t == o.year:
            v.lower_bound = 1
    return undo
```

In MathOpt a variable's `lower_bound` and `upper_bound` are properties you can read and set on the
model you already built. `overrides.py` applies the planners' four notes to GridCap small:

```text
rows before 49, after 50
no overrides  NPV $24,260k
overrides     NPV $23,333k  costs $927k
  P036 year       2028  start - -> 2028
  P032 out              start 2027 -> -
  P021 not_before 2030  start 2029 -> -
  P024 in               start - -> 2028
other projects that changed: {'P005': (2029, '-'), 'P010': (2031, 2030), 'P014': (2028, '-'), 'P015': (2029, 2030), 'P020': (2030, 2031), 'P025': (2028, 2027), 'P031': (2028, 2027), 'P038': ('-', 2027), 'P039': (2028, 2027)}
undone        NPV $24,260k  rows 49
```

Three overrides changed only bounds; the fourth, "fund P024", added the one row. The overrides cost
$927k of NPV. Two of the results are worth reading closely. P021 was only told "not before 2030",
and 2030 is in its window, yet it left the plan: in 2030 it is worth $815k instead of $1,012k in
2029, and the money does more elsewhere. An override says what is allowed; the optimizer still
decides. And nine projects the planners never mentioned moved, two of them out of the plan, because
the four notes reshaped every year's budget. Show the planner that list, not only the four lines
they asked for.

## An Override Is Data, and Restoring the Bounds Undoes It

Each call to `apply` returns what it changed: the variable with its old bounds, or the row it added.
Undoing an override is putting those back:

```python
def undo(plan, changes: list) -> None:
    for change in changes:
        if isinstance(change, tuple):
            v, lower, upper = change
            v.lower_bound, v.upper_bound = lower, upper
        else:
            plan.model.delete_linear_constraint(change)
```

The last line of the output above is the model after every override was undone: the same 49 rows
and the same $24,260k as before any override. Two things follow, and both matter in a planning tool:

- **Overrides live outside the model**, as a list of records (who asked, what, when, why), and are
  applied to a freshly built model or undone from a solved one. Lesson 12.1.2 keeps exactly that
  list as an audit trail.
- **One model serves many what-ifs.** There is no need to rebuild the model to try an override, or
  to take one back; the next section prices four overrides on one model object.

<!-- practice 1 -->

## Price Every Override by Solving With and Without It

An override has a cost, measured the way lesson 6.5.1 measured a mandate's: the best NPV without
it, less the best NPV with it. With `apply` and `undo`, every price comes from the same model object,
built once:

```python
plan = build(small)                       # built once; every solve below reuses it
free = solve_highs(plan.model).objective_value()
print(f"no override   NPV {money(free)}")
for o in OVERRIDES:
    changes = apply(plan, o)
    value = solve_highs(plan.model).objective_value()
    undo(plan, changes)
    print(f"{o.pid} {o.kind:10} alone  NPV {money(value)}  costs {money(free - value)}")
```

```text
no override   NPV $24,260k
P036 year       alone  NPV $24,148k  costs $112k
P032 out        alone  NPV $24,148k  costs $112k
P021 not_before alone  NPV $24,139k  costs $121k
P024 in         alone  NPV $23,987k  costs $273k
all four together  NPV $23,333k  costs $927k
```

One at a time the four cost $112k + $112k + $121k + $273k = $618k; together they cost $927k, half as
much again. As with mandates, overrides interact through the budgets they share, so the joint cost
has to be measured, never added up. That table is what a planner takes to the meeting: "your four
notes cost $927k of value; the board's undergrounding request is the largest single one at $273k".

## A Conflicting Override Makes the Model Infeasible, or Quietly Changes It

An override is a person's decision, made without the model's rules in view, and it can contradict
them. Some contradictions make the model infeasible; one kind does something worse. Each can be
found from the override list and the data alone:

- **A child forced in while its parent is forced out** breaks the parent rows (lesson 6.5.2).
- **Two alternatives forced in** break the alternative row (lesson 6.5.3).
- **A must-do forced out** breaks its must row (lesson 6.5.1).
- **A start year outside the window** has no variable at all. `apply` sets the upper bound of every
  year that is not the requested one to 0, and with no variable for the requested year, that
  forces the project *out*, silently.

```python
def check(overrides: list[Override]) -> list[str]:
    """Conflicts between the overrides and the rules, readable by a planner."""
    problems = []
    out = {o.pid for o in overrides if o.kind == "out"}
    funded = {o.pid for o in overrides if funds(o)}
    for o in overrides:
        p = small.project(o.pid)
        if o.year is not None and o.kind == "year" and o.year not in p.starts():
            problems.append(f"{o.pid} cannot start in {o.year}: its window is {p.earliest_start}-{p.latest_start}")
        if o.pid in out and p.must_do:
            problems.append(f"{o.pid} is a must-do and cannot be overridden out")
        if o.pid in funded and p.parent in out:
            problems.append(f"{o.pid} is forced in, but its parent {p.parent} is forced out")
    for g, members in groups_of(small).items():
        both = [i for i in members if i in funded]
        if len(both) > 1:
            problems.append(f"{both} are forced in, but they are alternatives ({g})")
    return problems
```

`override_conflicts.py` checks four override lists, then applies each and solves:

```text
child in, parent out: ['P023 is forced in, but its parent P022 is forced out']; solve INFEASIBLE
both alternatives in: ["['P030', 'P031'] are forced in, but they are alternatives (G030)"]; solve INFEASIBLE
must-do out: ['P017 is a must-do and cannot be overridden out']; solve INFEASIBLE
outside the window: ['P038 cannot start in 2029: its window is 2027-2027']; solve OPTIMAL with P038 not funded
```

The first three give the solver's one word, `INFEASIBLE`, where the check gives a sentence a planner
can act on. The fourth is the dangerous one: a planner asked for P038 *in*, and the solve is
`OPTIMAL` with P038 *out*. Nothing failed, so nothing would be reported. Run the check before every
solve with overrides, and refuse an override it flags, rather than letting the model reinterpret it.

As in the earlier lessons of this module, the check is necessary, not sufficient: overrides that pass
it can still be infeasible together, for example when the projects forced in cost more than a year's
budget. Lesson 9.1.3 finds the rows that conflict when that happens.

<!-- practice 2 -->

## The Model

The planning model with the overrides of `overrides.py` marked. Overrides change bounds; only "fund
in any year" adds rows.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years of project
$`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$. The overrides:
$`O^{\text{yr}}`$ the pairs $`(i, y)`$ "start $`i`$ in year $`y`$", $`O^{\text{out}}`$ the projects
never to fund, $`O^{\text{nb}}`$ the pairs $`(i, y)`$ "not before $`y`$", $`O^{\text{in}}`$ the
projects to fund in any year.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year
of work ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$, with the bounds the
overrides set:

```math
\begin{aligned}
& x_{i,y} = 1,\ \ x_{i,t} = 0 \ \ (t \ne y) && \forall (i, y) \in O^{\text{yr}} && \leftarrow \text{this lesson, bounds} \\
& x_{i,t} = 0 && \forall i \in O^{\text{out}},\ t \in T_i && \leftarrow \text{this lesson, bounds} \\
& x_{i,t} = 0 && \forall (i, y) \in O^{\text{nb}},\ t \in T_i,\ t < y && \leftarrow \text{this lesson, bounds}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\text{started}(i) &= 1 && \forall i \in O^{\text{in}} && \text{(override}_i) \quad \leftarrow \text{this lesson, a row} \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\textstyle\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \textstyle\sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

with $`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$. In `overrides.py`,
$`O^{\text{yr}} = \{(P036, 2028)\}`$, $`O^{\text{out}} = \{P032\}`$, $`O^{\text{nb}} = \{(P021, 2030)\}`$
and $`O^{\text{in}} = \{P024\}`$; the row is named `override_P024`.

## Summary

- **An override on start variables is a bound, not a row.** Start in a year, never, and not before
  a year are bounds; "fund in any year" is a sum and needs a row. Here four overrides added one row.
- **An override is data, and restoring the bounds undoes it.** Keep overrides as records outside the
  model; one built model serves every what-if.
- **Price every override by solving with and without it.** Four overrides cost $618k one at a time
  and $927k together.
- **A conflicting override makes the model infeasible, or quietly changes it.** Check overrides
  against windows, must-dos, parents and alternatives before the solve; a year outside the window
  turned "fund it" into "drop it" with an `OPTIMAL` status.

## Reference

| Override | In MathOpt |
| --- | --- |
| start $`i`$ in year $`y`$ | `x[i, y].lower_bound = 1`; `x[i, t].upper_bound = 0` for $`t \ne y`$ |
| never fund $`i`$ | `x[i, t].upper_bound = 0` for every $`t`$ |
| $`i`$ not before $`y`$ | `x[i, t].upper_bound = 0` for $`t < y`$ |
| fund $`i`$ in any year | `add_linear_constraint(started(i) == 1)`, deleted to undo |
| undo | restore the saved `lower_bound` and `upper_bound`; `delete_linear_constraint(row)` |

| Check before the solve | Conflict |
| --- | --- |
| year in the window | a year outside it forces the project out silently |
| must-do not forced out | must row broken: `INFEASIBLE` |
| parent not out when the child is in | parent rows broken: `INFEASIBLE` |
| at most one alternative forced in | alternative row broken: `INFEASIBLE` |

**Further reading:** [MathOpt sample time_indexed_scheduling.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py) (fixes start variables through their bounds for release times, the move overrides make); [MathOpt sample integer_programming.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (checks the termination reason before reading a solution, which an override that makes the model infeasible needs); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (variable and constraint deletions and incremental solving, the features undoing an override uses).

## Challenges

1. Add an override "P036 not after 2028". Which bounds does it change?
2. In `override_cost.py`, price the overrides in pairs. Which pair interacts the most?
3. Extend `check` to flag a set of "start in year $`y`$" overrides whose spend in one year is more
   than that year's budget.

## Design Note: Refuse, Don't Reinterpret

A model that quietly turns an impossible override into something possible ("in 2029" into "not at
all") hides a disagreement between a person and the data. A planning tool should do the opposite:
check every override first, refuse the ones that conflict with a message that names the rule, and
apply only the rest. The solver then reports on a model that says what the planners meant, and the
audit trail (lesson 12.1.2) records both the overrides that were applied and the ones that were
refused, with the reason.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**overrides.py.** Applies four overrides to GridCap small as bounds and one row, solves, and undoes
them (*An Override on Start Variables Is a Bound, Not a Row*). *Try:* Change P021's override to
"not before 2029". Predict whether P021 stays in the plan.

- Program: [overrides.py](src/overrides.py)

**override_cost.py.** Prices each override alone and all four together on one model (*Price Every
Override by Solving With and Without It*). *Try:* Add "never fund P028". Predict whether it costs
more than the other four together.

- Program: [override_cost.py](src/override_cost.py)

**override_conflicts.py.** Checks four conflicting override lists before the solve and solves each
(*A Conflicting Override Makes the Model Infeasible, or Quietly Changes It*). *Try:* Force in P016
while forcing P015 out. Predict what the check and the solve report.

- Program: [override_conflicts.py](src/override_conflicts.py)

**override_tools.py.** The `Override` record, `apply` and `undo`, imported by the three programs.

- Library: [override_tools.py](src/override_tools.py)

**planning_model.py.** The model builder the programs import.

- Library: [planning_model.py](src/planning_model.py)
