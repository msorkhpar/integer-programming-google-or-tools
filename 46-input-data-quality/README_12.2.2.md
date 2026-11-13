# 12.2.2 Data-Quality Checks That Prevent Infeasibility

The schema of lesson 12.2.1 now guards GridCap's optimization service: every snapshot it accepts
has every field typed and every id resolved, so the model can be built. That is not the same as a
model worth solving. This cycle's export passes the schema and still says that P015 must wait for
P016 while P016 waits for P015. Another passes and has every budget in millions of dollars where
the model expects thousands. One of these comes back from the solver `INFEASIBLE` with no reason
given; the other comes back `OPTIMAL` with two projects silently gone. This lesson adds the layer
between the schema and the model that catches both: a quality gate of named rules, each with a
severity. GridCap is a fictional utility; the planted errors are typical of real exports, the data
is not real.

Lesson 9.1.2 wrote five **pre-solve checks**: tests on the
input that can prove no plan exists without solving, such as a must-do project that alone overspends
every year it may start in. It also taught what makes a check **sound**: it fires only when no plan
can exist. This lesson builds on both. It turns checks into a gate the service runs on every
snapshot, adds rules that look across several projects at once, and separates findings that must
stop the run from findings that only need a reader.

## The Model

The gate reads the snapshot and reasons about the model's rows without building them. The model is
the one of lesson 12.2.1, unchanged, here whole so that each rule can name the rows it protects.

**Sets.** $`Y`$ the plan's years, in order; $`P`$ the candidate projects; $`T_i`$ the start years
of project $`i`$: the years $`t`$ with $`e_i \le t \le l_i`$ and $`t + d_i - 1 \le \max Y`$;
$`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$
the child projects, each with parent $`p(c)`$ and lag $`L_c`$; $`Q`$ the programs, with $`q(i)`$
the program of project $`i`$; $`R`$ the regions, with $`r(i)`$ the region of project $`i`$.

**Parameters.** $`e_i, l_i`$, the earliest and latest start years; $`c_{i,k}`$, what project $`i`$
spends in its $`k`$-th year of work ($k), $`d_i`$ its years of work, and
$`\text{capex}_i = \sum_k c_{i,k}`$; $`\text{npv}_{i,t}`$ ($k); $`m_i`$, crew-months per year of
work; $`B_y`$, the budget of year $`y`$ ($k); $`K_{q,y}`$, the crew-months of program $`q`$ in year
$`y`$; $`\text{floor}_r`$, the least region $`r`$ receives over the plan ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, 0 \le y - t < d_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{i:\, q(i) = q} \ \sum_{t \in T_i,\, 0 \le y - t < d_i} m_i\, x_{i,t} &\le K_{q,y} && \forall q \in Q,\ y \in Y && \text{(crews}_{q,y}) \\
\sum_{i:\, r(i) = r} \ \sum_{t \in T_i} \text{capex}_i\, x_{i,t} &\ge \text{floor}_r && \forall r \in R && \text{(floor}_r)
\end{aligned}
```

The precedence row $`\text{after}_{c,t}`$ is the cumulative form of lesson 6.4.3: if child $`c`$ has
started by year $`t`$, its parent has started by year $`t - L_c`$. On GridCap small the model solves
to an NPV of $22,741k, the base plan of lesson 9.1.1.

## A Quality Gate Runs Every Rule After the Schema and Before the Model

A **quality rule** is a function that reads a valid snapshot and returns findings. A **finding**
is a record, as in lesson 9.1.2's design note: which rule, how serious, about what, and the numbers.

```python
@dataclass(frozen=True)
class Finding:
    rule: str
    severity: Severity
    subject: str
    detail: str
```

`Severity` is `Literal["error", "warning"]`. An **error** blocks the solve; a **warning** lets it
run and goes into the run's report. The third section is about which is which.

The **gate** is the list of rules and one function that runs them all. It never stops at the first
finding, for the reason pydantic does not stop at the first bad field: the sender fixes everything
in one round.

```python
RULES: list[Callable[[Snapshot, Snapshot | None], list[Finding]]] = [
    parent_cycle, parent_too_late, required_over_budget, pulls_in_parent, budget_drift]


def gate(snap: Snapshot, previous: Snapshot | None = None) -> list[Finding]:
    """Run every rule and return every finding, errors first. Never stops at the first one."""
    found = [f for rule in RULES for f in rule(snap, previous)]
    return sorted(found, key=lambda f: (f.severity != "error", f.rule, f.subject))
```

Every rule takes the same two arguments: the snapshot, and the **last accepted snapshot** of the
same scenario (or `None`), for the rules that compare one cycle with the last. Adding a rule is
adding a function to `RULES`; lesson 9.1.2's five checks fit the same shape. The service runs, in
order: the schema (can the model be built?), the gate (is the data worth solving?), then the model.
On the clean export the gate is silent and the solve is the base plan:

```text
clean export                       schema: valid   solver: OPTIMAL, NPV $22,741k   blocked: False
   gate: no finding
```

## Rules Across Projects Catch Errors No Single Field Shows

Lesson 9.1.2's checks each read one project, one group or one region against one limit. The
errors that pass a schema most easily are the ones that need two or more projects to see. Two of
them, planted in `quality_gate.py`; the schema accepts both, because every field is well typed and
every parent exists.

**A parent cycle.** The export sets P015's parent to P016, with a lag of 1. P016's parent is already
P015. Each is now the other's prerequisite:

```text
P015's parent set to P016, lag 1   schema: valid   solver: OPTIMAL, NPV $22,637k   blocked: True
   error   parent-cycle         P015 -> P016 -> P015   a project cannot be a prerequisite of its own prerequisite
   warning parent-too-late      P015                   parent P016 starts [2030], lag 1; child starts [2029, 2030]
```

The solver does not say "infeasible". Neither project is must-do, so the plan that funds neither
satisfies every row, and the solver returns it, $104k below the base plan:

```text
clean  plan funds P015: True, P016: False
cycle  plan funds P015: False, P016: False
```

The base plan funds P015. With the cycle it cannot: funding P015 by year $`t`$ needs P016 by year
$`t - 1`$, which needs P015 by year $`t - 1`$, and so back until no year is left. This is the quiet
failure: an `OPTIMAL` plan that has lost a project because of a typo in a link, with nothing in the
result to say so. The rule follows each project's chain of parents and reports a project that comes
back to itself. The warning below it is a second rule seeing the same typo from another side; the
third section explains why it is only a warning.

**A must-do child whose parent cannot start early enough.** The export marks P023 must-do and types
its lag as 3 instead of 1. P023 may start only in 2029; its parent P022 may start from 2027:

```text
P023 must-do, its lag typed 3      schema: valid   solver: INFEASIBLE   blocked: True
   error   parent-too-late      P023                   parent P022 starts [2027, 2028, 2029], lag 3; child starts [2029]
   warning pulls-in-parent      P023                   must-do, so its optional parent P022 becomes required too
```

The rule compares the earliest the parent can start, plus the lag, with the latest the child can
start. If that is too late, no start year of the child has a parent start early enough, so every
row $`\text{after}_{c,t}`$ forces $`x_{c,t} = 0`$:

```python
        mine, theirs = starts(c, snap.years), starts(by_id[c.parent], snap.years)
        if mine and theirs and min(theirs) + c.parent_lag <= max(mine):
            continue
        severity = "error" if c.must_do else "warning"
```

`starts` gives $`T_i`$, the start years whose work ends inside the plan, the same function the model
builder uses, so the rule and the model cannot disagree on the windows. Here
$`\min T_{\text{P022}} + 3 = 2030 > 2029 = \max T_{\text{P023}}`$. For a must-do child that means
$`\text{must}_{\text{P023}}`$ cannot hold, and the solver's `INFEASIBLE` is certain; the rule says
why in one line, with the numbers.

The third cross-project rule adds up what every plan must pay for. A must-do project must be funded
($`\text{must}_i`$), and through $`\text{after}_{c,t}`$ so must its parent, and the parent's parent:

```python
def required(snap: Snapshot) -> set[str]:
    """Must-do projects and, through the precedence rows, every ancestor of one."""
    parent = {p.project_id: p.parent for p in snap.projects}
    need = set()
    for pid in (p.project_id for p in snap.projects if p.must_do):
        while pid is not None and pid not in need:
            need.add(pid)
            pid = parent[pid]
    return need
```

Every required project starts in a year of $`T_i`$, so all its work falls inside the plan, and adding
the budget rows over all years gives
$`\sum_{i \text{ required}} \text{capex}_i \le \sum_y B_y`$ in every plan. If the required total is
larger, no plan exists: the rule `required-over-budget` is sound. The walk up the parents makes it
stronger without making it unsound, because an ancestor of a must-do is funded in every plan too.
The `pid not in need` test also stops the walk on a cycle.

<!-- practice 1 -->

## Severity Follows What a Finding Proves: Errors Block, Warnings Report

A gate that blocks a good snapshot is worse than none: the planners lose a cycle and soon stop
trusting it. A gate that lets a broken snapshot through hands them a wrong plan. The severity of a
finding decides which mistake the gate can make, so it follows a rule:

- **Error:** the finding proves the snapshot breaks its contract (a parent cycle cannot exist in
  real work) or proves the model has no plan (a sound pre-solve check, as in lesson 9.1.2). The solve
  is refused.
- **Warning:** the finding is possible but unusual, and may be exactly what the planners meant. The
  solve runs, and the finding goes into the run's report next to the plan.

`severity.py` runs four snapshots through the gate, each compared with the last accepted one, the
clean export:

```text
P016 made must-do                    solver: OPTIMAL, NPV $20,069k   blocked: False
   warning pulls-in-parent      P016                   must-do, so its optional parent P015 becomes required too
P016's lag typed 2 (P016 optional)   solver: OPTIMAL, NPV $22,741k   blocked: False
   warning parent-too-late      P016                   parent P015 starts [2029, 2030], lag 2; child starts [2030]
budgets exported in $M               solver: INFEASIBLE   blocked: True
   error   required-over-budget plan                   required projects cost $7,630k; all budgets together $43k
   warning budget-drift         2027                   $8,890k last snapshot, $9k now
   warning budget-drift         2028                   $8,120k last snapshot, $8k now
   warning budget-drift         2029                   $8,760k last snapshot, $9k now
   warning budget-drift         2030                   $8,610k last snapshot, $9k now
   warning budget-drift         2031                   $7,850k last snapshot, $8k now
2029 budget cut 20%                  solver: OPTIMAL, NPV $22,352k   blocked: False
   gate: no finding
```

**A must-do child pulls in its parent.** Making P016 must-do is a planner's decision, and a
legitimate one. Its parent P015 is optional, so the model must fund P015 too, and does:

```text
P016 must-do: plan funds P015 in 2029 and P016 in 2030
```

The plan costs $2,672k of NPV against the base. That may surprise the planner who only asked for
P016, so the gate says why P015 is in the plan. It is a warning: nothing is wrong, and refusing the
run would refuse a decision the planners are entitled to make.

**The same rule, two severities.** `parent-too-late` fires on P016 when its lag is typed 2: P015 can
start in 2029 at the earliest, plus 2 is 2031, and P016 may start only in 2030. Since P016 is
optional, the model simply never funds it, which is a plan; the warning says P016 can never be
chosen, so a planner who wanted it knows to look. The same finding on the must-do P023 above proved
there is no plan, so there it was an error. The code that chooses is the line
`severity = "error" if c.must_do else "warning"`.

**A units error: one error and five warnings that explain it.** The budgets arrived in millions,
rounded to whole numbers: 9, 8, 9, 9, 8. The schema accepts them, since each is a non-negative
integer. `required-over-budget` proves no plan exists ($7,630k required against $43k) and blocks the
run. That error alone says *that* the data is wrong. The `budget-drift` warnings, which compare each
year's budget with the last accepted snapshot and fire when it moves by more than a factor of 3, say
*how*: every year shrank about a thousandfold, the signature of a units mistake.

**A real budget cut passes.** Finance cuts 2029 by 20%, to $7,008k. A factor of 0.8 is well inside
the drift limit, no rule fires, and the solve runs to an NPV of $22,352k. The gate must let such a
snapshot through: a cut is what the planning cycle is for.

Why is drift a warning and not an error, when it caught the units mistake? Because a large change is
not proof of a wrong one. A new regulatory program can triple a year's budget. The drift rule cannot
tell a tripling from a typo, so it reports and lets the sound rules decide whether to block. Here a
sound rule did block. On a snapshot where every budget grew fivefold, no sound rule would fire: the
solve would run, and the drift warnings would sit in the report beside a plan that a planner can
check.

<!-- practice 2 -->

## Summary

- **A quality gate runs every rule after the schema and before the model.** Each rule returns
  `Finding(rule, severity, subject, detail)`; the gate runs all of them and reports everything.
- **Rules across projects catch errors no single field shows.** A parent cycle drops projects from
  an `OPTIMAL` plan without a word; a must-do child whose parent cannot start early enough makes the
  model infeasible; the required projects, ancestors included, cannot cost more than all budgets.
- **Severity follows what a finding proves.** An error proves a broken contract or no plan, and
  blocks; a warning flags what is possible but unusual, and is reported with the plan. The same rule
  can be either, depending on whether the project is required.

## Reference

| Rule | Fires when | Severity | Rows it protects |
| --- | --- | --- | --- |
| `parent-cycle` | following parents from a project leads back to it | error (contract) | $`\text{after}_{c,t}`$ |
| `parent-too-late` | $`\min T_{p(c)} + L_c > \max T_c`$, or either window is empty | error if $`c \in M`$, else warning | $`\text{after}_{c,t}`$, $`\text{must}_c`$ |
| `required-over-budget` | $`\sum_{i \in \text{req}} \text{capex}_i > \sum_y B_y`$, with req the must-dos and their ancestors | error (sound) | $`\text{must}_i`$, $`\text{budget}_y`$ |
| `pulls-in-parent` | a must-do child has an optional parent | warning | $`\text{after}_{c,t}`$ |
| `budget-drift` | $`B_y`$ moved by more than a factor of 3 since the last accepted snapshot | warning | $`\text{budget}_y`$ |

| Term | Meaning |
| --- | --- |
| quality rule | a function from a valid snapshot (and the last accepted one) to findings |
| finding | rule, severity, subject, detail |
| error | proves a broken contract or no plan; blocks the solve |
| warning | possible but unusual; reported with the plan |
| last accepted snapshot | the previous snapshot of the same scenario that passed the gate |

**Further reading:** the [CP-SAT troubleshooting page](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md) in the OR-Tools repository, whose advice for an infeasible model starts with checking the input data; [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) for the model the gate stands in front of; Gurobi's [infeasibility example tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html), which picks up where the gate stops, when a snapshot passes every rule and the model is still infeasible (lessons 9.1.3 and 9.1.4); and [Pydantic: validators](https://pydantic.dev/docs/validation/latest/concepts/validators/), the layer below the gate.

## Challenges

1. Write a rule `alt-group-required`: two must-do projects in one alternative group. Which row does
   it protect, and what severity does it get?
2. `required-over-budget` sums over the whole plan. Write a stronger sound version that, for each
   year $`y`$, adds the spend of required projects whose every allowed start puts work in $`y`$.
3. The drift rule compares with the last accepted snapshot. What should it do on a scenario's first
   snapshot, and on a year that is new in this snapshot?

## Design Note: The Gate Never Repairs

The units error has an obvious repair: multiply every budget by 1,000. The gate does not make it.
A repair is a guess about what the sender meant, and a guess applied silently is the same kind of
quiet failure the gate exists to stop. The gate reports, with the numbers, and the sender fixes the
export; the fixed snapshot gets a new digest (lesson 12.2.3), so the record shows which data the plan
came from.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**quality_gate.py.** The clean export, the parent cycle and the must-do child with the wrong lag,
each through the schema, the solver and the gate (*A Quality Gate Runs Every Rule* and *Rules Across
Projects*). *Try:* Make P016 must-do in the cycle case as well. Predict the solver's answer.

- Program: [quality_gate.py](src/quality_gate.py)

**severity.py.** Four snapshots compared with the clean export: a must-do child, an optional child
with the wrong lag, budgets in $M, and a 20% cut (*Severity Follows What a Finding Proves*). *Try:*
Multiply every budget by 5. Predict which rules fire and whether the run is blocked.

- Program: [severity.py](src/severity.py)

The rules and the gate are in `quality.py`.

- Library: [quality.py](src/quality.py)
