# 12.1.2 Manual Overrides as Bounds, With an Audit Trail

It is the second week of the planning cycle, and GridCap's planners have opened a copy of the base
scenario called `q2-overrides`. Three planners and a manager change it over one morning. One
promises the Ridge customers that the P024 undergrounding starts in 2029, then moves the promise
to 2030. Another takes the Valley line P032 out until a study is done. A third keeps the Coast job P036
out of 2027 and 2028 for lack of crews, and adds an outage window to P021 that the manager later
lifts. Two requests are mistakes and must be refused. A month later an auditor asks why P024 starts
in 2030 and P032 is not in the plan. The answer cannot be "someone changed it": it has to name the
person, the time, the reason, and exactly what the change did to the model.

Lesson 6.5.6 showed the mechanics: an override that fixes start
variables is a change of their bounds, it can be undone by restoring them, and it is priced by
solving with and without it. This lesson builds the record keeping around those mechanics, which a
planning service needs and a model alone cannot give: a check before any bound moves, an
append-only **audit trail** (a log of every change, kept in the order it happened, that is only ever
added to), and a way to find which overrides broke a scenario that will not solve.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real. The
people (`planner-a`, `planner-b`, `planner-c`, `manager-a`) and their reasons are invented
placeholders.

## The Model

The model of lesson 12.1.1, whole, with this lesson's part marked: each override sets the bounds
$`l_{i,t}`$ and $`u_{i,t}`$ of its project's start variables. No override adds or removes a row.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years; $`O`$ the
overrides in force, at most one per project, each a triple (project $`i`$, kind, year $`y`$).

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k), from the scenario; $`l_{i,t}`$ and
$`u_{i,t}`$, the bounds of $`x_{i,t}`$, set by the table below (this lesson).

| Override on project $`i`$ | $`(l_{i,t}, u_{i,t})`$ for each $`t \in T_i`$ |
| --- | --- |
| none | $`(0, 1)`$ |
| `start_in` $`y`$ | $`(1, 1)`$ if $`t = y`$, else $`(0, 0)`$ |
| `out` | $`(0, 0)`$ |
| `not_before` $`y`$ | $`(0, 0)`$ if $`t < y`$, else $`(0, 1)`$ |
| `not_after` $`y`$ | $`(0, 0)`$ if $`t > y`$, else $`(0, 1)`$ |

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$, with
$`l_{i,t} \le x_{i,t} \le u_{i,t}`$ $`\leftarrow`$ this lesson. We write
$`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ and
$`\text{by}(i, t) = \sum_{s \in T_i,\, s \le t} x_{i,s}`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\text{by}(c, t) &\le \text{by}(p(c),\, t - L_c) && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
l_{i,t} \le x_{i,t} &\le u_{i,t} && \forall i \in P,\ t \in T_i && \text{(bounds)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

The bounds are part of each variable, not rows; `plan_model.build` sets them last, after every row
is written, with `x[key].lower_bound, x[key].upper_bound = lower, upper`. MathOpt's `Variable` has
setters for both properties, and the OR-Tools sample `time_indexed_scheduling.py` uses the same
move to forbid start times before a job's release. The one override kind of lesson 6.5.6 that is
not a bound, "fund it in any year", is a rule on the sum $`\text{started}(i) = 1`$ and needs a row;
this service does not accept it (see the design note).

## An Override Is a Request, Checked Against the Data Before Any Bound Moves

An override arrives as a request from a person, and a person can ask for something the data does
not allow. Lesson 6.5.6 found the dangerous case: a start year outside the project's window has no
variable at all, so "start in that year" quietly becomes "never". A service must catch that before
the bounds are written, not after a solve has hidden it. The override itself is a small frozen
record holding only what the model needs:

```python
@dataclass(frozen=True)
class Override:
    project: str
    kind: str                 # one of KINDS
    year: int | None = None   # None for "out"
```

`bounds_of` turns it into the bounds of the table above, and `check` refuses it when those bounds
would not mean what the planner asked for:

```python
def bounds_of(o: Override, p: Project) -> dict[tuple[str, int], tuple[int, int]]:
    """The (lower, upper) bounds the override puts on each of the project's start variables."""
    bounds = {}
    for t in p.starts():
        if o.kind == "start_in":
            bounds[p.project_id, t] = (1, 1) if t == o.year else (0, 0)
        elif o.kind == "out" or (o.kind == "not_before" and t < o.year) or (o.kind == "not_after" and t > o.year):
            bounds[p.project_id, t] = (0, 0)
        else:
            bounds[p.project_id, t] = FREE
    return bounds
```

```python
    if o.kind == "start_in" and o.year not in p.starts():
        return [f"{o.project} cannot start in {o.year}: its window is {window}"]
    leaves_none = all(b == (0, 0) for b in bounds_of(o, p).values())
    if o.kind in ("not_before", "not_after") and leaves_none:
        return [f"{o.text()} leaves {o.project} no start year in {window}"]
    if p.must_do and leaves_none:
        return [f"{o.project} is a must-do and cannot be overridden out"]
    return []
```

The rule behind `leaves_none` is general: an override that sets every start variable of a project
to $`(0, 0)`$ takes the project out of the plan, whatever it was called. That is correct for `out`,
a silent surprise for a `not_before` past the window's end, and impossible for a must-do, whose
must row $`\text{started}(i) = 1`$ would make the model infeasible.

`request` runs the check, writes an audit entry either way, and changes the scenario only when the
check passes. It is the per-request form of lesson 9.1.2's input validation (*Validating inputs
before the solve*):

```python
def request(s, trail: list[AuditEntry], o: Override, portfolio: Portfolio, by: str, at: str, why: str) -> AuditEntry:
    """Record a planner's override on scenario `s`: accepted as bounds, or refused with the reasons."""
    problems = check(o, portfolio)
    if problems:
        entry = AuditEntry(len(trail) + 1, s.scenario_id, "refused", o, by, at, why, tuple(problems))
    else:
        changes = bound_changes(s.overrides.get(o.project), o, portfolio.project(o.project))
        entry = AuditEntry(len(trail) + 1, s.scenario_id, "set", o, by, at, why, changes)
        s.overrides[o.project] = o
    trail.append(entry)
    return entry
```

`override_trail.py` sends the morning's seven requests and the manager's revocation. Here are the
two refused requests from its output:

```text
#4 2027-03-01T09:25Z planner-a refused P038 start_in 2029   bundle with P024 crews
      P038 cannot start in 2029: its window is 2027-2027
#5 2027-03-01T09:30Z planner-b refused P017 out             permit risk
      P017 is a must-do and cannot be overridden out
```

Each refusal says why in a sentence a planner can act on, and neither touched the scenario. Both
are in the trail anyway. A refused request is still something a person asked for, and an auditor
who hears "I asked for P038 in 2029" can see that the request was made, when, and why it was
turned down.

<!-- practice 1 -->

## The Trail Records Who, When, Why and the Bounds That Moved, and Is Only Ever Appended To

The `Override` record holds what the model needs; the `AuditEntry` around it holds what the people
need:

```python
@dataclass(frozen=True)
class AuditEntry:
    seq: int
    scenario_id: str
    action: str                  # "set", "revoke", "inherit" or "refused"
    override: Override
    by: str
    at: str                      # ISO 8601, UTC
    why: str
    changes: tuple[str, ...]     # "x_P024_2028 [0,1] -> [0,0]", or the reasons it was refused
```

The split is the one lesson 12.1.1 made between inputs and metadata. The scenario's snapshot covers
`Override` (project, kind, year) because the bounds change the model; it does not cover `by`, `at`
or `why`, which change nothing the solver sees. Two planners who make the same override give the
same snapshot, and the trail still says which of them did it.

`changes` is the line an auditor reads most closely: every start variable whose bounds moved, from
what to what. It is computed by comparing the bounds before and after, so it is exact even when one
override replaces another. The whole trail of the morning:

```text
#1 2027-03-01T09:10Z planner-a set     P024 start_in 2029   Ridge customers were promised a 2029 start
      x_P024_2028 [0,1] -> [0,0]
      x_P024_2029 [0,1] -> [1,1]
      x_P024_2030 [0,1] -> [0,0]
#2 2027-03-01T09:15Z planner-b set     P032 out             waiting for the Valley line study
      x_P032_2027 [0,1] -> [0,0]
      x_P032_2028 [0,1] -> [0,0]
      x_P032_2029 [0,1] -> [0,0]
#3 2027-03-01T09:20Z planner-c set     P036 not_before 2029 no Coast crew before 2029
      x_P036_2027 [0,1] -> [0,0]
      x_P036_2028 [0,1] -> [0,0]
#4 2027-03-01T09:25Z planner-a refused P038 start_in 2029   bundle with P024 crews
      P038 cannot start in 2029: its window is 2027-2027
#5 2027-03-01T09:30Z planner-b refused P017 out             permit risk
      P017 is a must-do and cannot be overridden out
#6 2027-03-01T09:35Z planner-c set     P021 not_before 2030 outage window
      x_P021_2028 [0,1] -> [0,0]
      x_P021_2029 [0,1] -> [0,0]
#7 2027-03-01T09:40Z planner-a set     P024 start_in 2030   promise moved to 2030 after the March review
      x_P024_2029 [1,1] -> [0,0]
      x_P024_2030 [0,0] -> [1,1]
#8 2027-03-01T09:45Z manager-a revoke  P021 not_before 2030 outage window confirmed open in 2029
      x_P021_2028 [0,0] -> [0,1]
      x_P021_2029 [0,0] -> [0,1]
```

Read entries 1 and 7 together. A project has at most one override in force, so P024's move to 2030
**supersedes** the 2029 one. Entry 7 lists only the two variables that moved: 2029 goes from fixed
at 1 to fixed at 0, 2030 the other way, and 2028 stays at $`(0, 0)`$, so it is not listed. Entry 1
is not edited or deleted; it stays, because it was true at 09:10 and an auditor may need to know that
the promise was once 2029.

Entries 6 and 8 show a **revocation**. The manager takes P021's override back, and the trail gains
an entry rather than losing one. The bounds return to $`(0, 1)`$, which is what lesson 6.5.6's undo
did on the model; here the undo is recorded too.

Because nothing is ever removed, the trail alone is enough to rebuild the overrides in force. That
is a check worth running, since it proves the scenario and its history agree:

```python
def replay(trail: list[AuditEntry], scenario_id: str) -> dict[str, Override]:
    """The overrides in force for a scenario, rebuilt from its audit trail alone."""
    active: dict[str, Override] = {}
    for e in sorted(trail, key=lambda e: e.seq):
        if e.scenario_id != scenario_id:
            continue
        if e.action in ("set", "inherit"):
            active[e.override.project] = e.override
        elif e.action == "revoke":
            active.pop(e.override.project, None)
    return active
```

```text
in force: ['P024 start_in 2030', 'P032 out', 'P036 not_before 2029']
replayed from the trail alone: ['P024 start_in 2030', 'P032 out', 'P036 not_before 2029']
replay equals the scenario: True
```

`replay` sorts by `seq`, the order the entries were made, not by their position in a list or by
their times: two requests in the same second still have a definite order. Refused entries change
nothing. `inherit` is the action a copied scenario uses for the overrides it starts with (lesson
12.1.4 writes one such entry per inherited override).

Then the scenario is optimized like any other, and its price and diff are measured against the
base, as lesson 6.5.6 priced overrides:

```text
base NPV $24,260k  q2-overrides NPV $22,989k  the overrides cost $1,271k
base -> q2-overrides: {'selected': ['P024', 'P038', 'P040'], 'deferred': ['P016', 'P032'], 'shifted': ['P008 2031->2029', 'P011 2031->2029', 'P018 2030->2031', 'P025 2028->2027', 'P031 2028->2027', 'P039 2028->2027']}
```

The three overrides cost $1,271k of NPV. P024 enters in 2030 as promised and P032 leaves, as
asked. Everything else on that line, two projects selected, one deferred and six shifted, is the
optimizer's answer to the new bounds, which nobody asked for by name. The audit trail explains the
three overrides; the diff explains what they did to the rest of the plan. A planner needs both.

<!-- practice 2 -->

## When Overrides Make a Scenario Infeasible, the Trail Finds Which Ones

Every override passed `check` one at a time, yet together they can still leave no feasible plan.
In the scenario `early-starts`, three planners each fix a different Valley or Plains project to
start in 2027, for good reasons of their own, and one adds an unrelated outage window:

```text
#1 set     P021 not_before 2030 problems: none
#2 set     P032 start_in 2027  problems: none
#3 set     P034 start_in 2027  problems: none
#4 set     P038 start_in 2027  problems: none
solve with all four: INFEASIBLE
2027 budget 8890 | forced into 2027: 5680 + 2130 + 1730
```

The three forced projects spend $9,540k in 2027 against a budget of $8,890k. The solver's answer is
one word, `INFEASIBLE`. Lesson 9.1.3 finds conflicts by asking a
solver for an **irreducible infeasible subsystem** (IIS), a smallest set of rows and bounds that cannot hold
together. The design note of lesson 9.3.2
explains why an override written as a bound is a poor fit for that tool: Gurobi's IIS never names
a binary variable's bounds (Gurobi's reference for its IIS attributes says so), so the very override that caused the conflict
could not appear in the explanation.

The trail gives another way, which needs no IIS and works with any solver. Each override in force
is an entry with a person and a reason. Drop the overrides one at a time, newest first, and re-solve:
an override whose removal leaves the scenario still infeasible is not needed for the conflict, so it
stays dropped; one whose removal makes the scenario solvable is part of the conflict, so it goes back.

```python
def culprits(s, trail) -> list:
    """Drop one override at a time, newest first; keep it dropped if the scenario stays infeasible."""
    keep = {e.override.project: e for e in trail if e.action == "set"}
    for e in sorted(keep.values(), key=lambda e: -e.seq):
        trial = {p: x.override for p, x in keep.items() if p != e.override.project}
        s.overrides = trial
        if optimize(s).status == "INFEASIBLE":
            del keep[e.override.project]
    s.overrides = {p: x.override for p, x in keep.items()}
    return sorted(keep.values(), key=lambda e: e.seq)
```

```text
needed for the conflict: #2 P032 start_in 2027  by planner-b at 2027-03-01T09:15Z: line rating expires in 2027
needed for the conflict: #3 P034 start_in 2027  by planner-a at 2027-03-01T09:20Z: substation tie-in agreed for 2027
needed for the conflict: #4 P038 start_in 2027  by planner-a at 2027-03-01T09:25Z: same outage as P034
solve with only those: INFEASIBLE
```

This is the **deletion filter** of lesson 9.1.3, run over overrides instead of rows. Four overrides
needed four solves. The outage window on P021 was dropped and stayed dropped, because the scenario
was still infeasible without it. Each of the other three was needed, and the three together are
still infeasible on their own. The filter keeps an override only when the solve without it was
feasible, so dropping any single one of the three makes the scenario solvable; that is what makes
the set irreducible. The answer is the sentence a planning meeting needs: these three 2027 starts,
by these two people, for these reasons, do not fit in the 2027 budget together; one of them has to
give.

The filter assumes the scenario without any override solves, which is true here because the base
solved. If the base itself were infeasible, the conflict would lie in the data or the rules, and
the IIS tools of lessons 9.1.3 to 9.1.5 are the right ones.

<!-- practice 3 -->

## Summary

- **An override is a request, checked against the data before any bound moves.** A start year
  outside the window, an override that leaves a project no start year, and a must-do taken out are
  refused with a sentence, and the refusal is recorded too.
- **The trail records who, when, why and the bounds that moved, and is only ever appended to.** A
  new override on the same project supersedes the old one; a revocation is a new entry; replaying
  the trail rebuilds the overrides in force.
- **When overrides make a scenario infeasible, the trail finds which ones.** Drop overrides one at
  a time and keep only those whose removal makes the scenario solvable; the entries name the people
  and reasons.

## Reference

| Override kind | Meaning | Refused when |
| --- | --- | --- |
| `start_in` $`y`$ | start in year $`y`$ exactly | $`y`$ is outside the window |
| `out` | never fund | the project is a must-do |
| `not_before` $`y`$ | no start before $`y`$ | it leaves no start year |
| `not_after` $`y`$ | no start after $`y`$ | it leaves no start year |

| Audit action | Writes | Changes the overrides in force |
| --- | --- | --- |
| `set` | the override and the bounds that moved | adds it, or supersedes the project's old one |
| `revoke` | the override taken back and the bounds that moved back | removes it |
| `inherit` | an override a copy starts with | adds it |
| `refused` | the request and the reasons | no |

**Further reading:** OR-Tools [MathOpt `variables.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/variables.py)
(`lower_bound` and `upper_bound` are properties with setters, so bounds can be changed on a built
model); the OR-Tools MathOpt sample
[`time_indexed_scheduling.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/time_indexed_scheduling.py)
(sets `upper_bound = 0` on start variables before a release time, the move every override here
makes); the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt)
(the model is built apart from the solver, so the same scenario rebuilds the same bounds on every
run).

## Challenges

1. A planner asks for P024 `not_after 2027`. Predict what `check` returns, using the window from
   the trail above, before you run it.
2. Change `culprits` to drop the oldest override first. Is the answer for `early-starts` the same?
   When could the two orders give different sets?
3. Should a refused request get a sequence number? Argue for and against, from an auditor's point
   of view.

## Design Note: A Service Accepts Only Overrides It Can State as Bounds

Lesson 6.5.6 allowed "fund it, in any year", which needs a row, and lesson 9.3.2 wrote every
forcing as a named row so an IIS could name it. This service takes the other side: every override
it accepts is a set of bounds, and a project that must be funded in some year is handled by
choosing the year (`start_in`), which a planner who promises a project to customers has to do
anyway. The gain is that an override never changes the model's rows, so two scenarios always have
the same rows and differ only in parameters and bounds, and the audit entry can list exactly which
variables moved. The cost is the one this lesson paid for in its last section: an IIS cannot name
a bound, so the service finds conflicting overrides with its own deletion filter over the trail.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**override_trail.py.** The morning's requests on `q2-overrides`: accepted, refused, superseded and
revoked, then the replay, the price and the diff (*An Override Is a Request*, *The Trail Records
Who, When, Why*). *Try:* add a request from `planner-c` for P036 `not_after 2028` after entry 3, and
predict which bounds its entry lists.

- Program: [override_trail.py](src/override_trail.py)

**override_culprit.py.** The infeasible `early-starts` scenario and the deletion filter over its
trail (*When Overrides Make a Scenario Infeasible*). *Try:* raise the 2027 budget by $650k in the
copy and predict the filter's answer.

- Program: [override_culprit.py](src/override_culprit.py)

**overrides.py.** `Override`, `bounds_of`, `check`, `AuditEntry`, `request`, `revoke` and
`replay`. It prints nothing itself.

- Library: [overrides.py](src/overrides.py)
