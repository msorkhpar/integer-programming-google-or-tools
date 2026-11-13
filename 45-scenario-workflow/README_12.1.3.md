# 12.1.3 Planning-Cycle States and Locking

Lesson 7.1.3 set out what each
stage of GridCap's planning cycle allows, and enforced it with a dictionary and one `if` in a
single program. A planning service has more to guard against than one program does. Several
planners work on the same scenario at once, from different browser tabs. A solve takes minutes,
and somebody edits the scenario while it runs. Two managers each believe their scenario is the
one going to finance. This lesson turns the stages into rules a service checks on every request:
a transition table, a version number on every scenario, and a lock that admits one plan of record
per planning cycle.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real. The
people (`planner-a`, `manager-a`, ...) are placeholders. The service here keeps its scenarios in
memory, so the rules can be read without a database; lesson 12.1.4 moves the same rules into SQLite.

## The Model

The rules of this lesson decide *when* a scenario may be optimized, not *what* is optimized. Every
run solves the model of lesson 12.1.2, unchanged, restated here.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k), from the scenario; $`l_{i,t}`$ and
$`u_{i,t}`$, the bounds that the scenario's overrides set (lesson 12.1.2), $`0`$ and $`1`$ by default.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ with $`l_{i,t} \le x_{i,t} \le u_{i,t}`$ for every
$`i \in P`$ and $`t \in T_i`$; $`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ and
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
l_{i,t} \le x_{i,t} &\le u_{i,t} && \forall i \in P,\ t \in T_i && \text{(bounds)}
\end{aligned}
```

## Every Request Is Checked Against One Transition Table

A **state machine** is a set of states, a set of actions, and a table that says, for each state and
action, which state comes next, or that the action is refused. Writing the planning cycle this way
puts every rule of lesson 7.1.3 in one place:

```python
TRANSITIONS = {
    ("Initial", "edit"): "Initial",
    ("Initial", "check"): "Pre-Opt",
    ("Pre-Opt", "edit"): "Pre-Opt",
    ("Pre-Opt", "optimize"): "Post-Opt",
    ("Post-Opt", "edit"): "Pre-Opt",
    ("Post-Opt", "optimize"): "Post-Opt",
    ("Post-Opt", "lock"): "Budget Lock",
}
```

A pair that is not in the dictionary is refused. `cycle_states.py` prints the whole table, every
state against every action:

```text
state       edit         check        optimize     lock
Initial     Initial      Pre-Opt      refused      refused
Pre-Opt     Pre-Opt      refused      Post-Opt     refused
Post-Opt    Pre-Opt      refused      Post-Opt     Budget Lock
Budget Lock refused      refused      refused      refused
```

Each cell is a rule a planner can read:

- **Initial** takes edits and moves to Pre-Opt on `check`, the data checks that must pass before a
  scenario may be solved. This service records only the move; the checks themselves are those of
  lessons 9.1.2 and 12.2.2.
- **Pre-Opt** takes edits and moves to Post-Opt when a run finishes.
- **Post-Opt** allows a rerun of the same inputs (an "ad hoc rerun")
  and stays there. An edit sends the scenario back to Pre-Opt, because its plan no longer matches
  its inputs, which is lesson 7.1.3's rule that every override needs a rerun.
- **Budget Lock** refuses everything. A change after lock is a copy.

One function moves a scenario, and every request goes through it:

```python
    def _move(self, rec: Record, action: str) -> None:
        nxt = TRANSITIONS.get((rec.state, action))
        if nxt is None:
            raise Refused(f"{rec.scenario.scenario_id} is {rec.state}; {action} is not allowed there")
        rec.state = nxt
```

The program walks the base scenario through the cycle, trying a few things the table forbids:

```text
optimize in Initial          refused: S-001 is Initial; optimize is not allowed there
check                        ok       -> Pre-Opt, version 2
lock in Pre-Opt              refused: S-001 is Pre-Opt; lock is not allowed there
optimize                     ok       -> Post-Opt, version 3
lock                         ok       -> Budget Lock, version 4
edit the locked scenario     refused: S-001 is Budget Lock; edit is not allowed there
optimize the locked one      refused: S-001 is Budget Lock; optimize is not allowed there
copy of the locked scenario: S-002 is Initial, version 1, parent S-001
```

Keeping the rules in a table, rather than in `if` statements spread across the handlers, has two
practical gains. The table can be printed, as above, and reviewed by someone who does not read
Python. And adding a stage or an action changes one dictionary, with every handler picking it up,
instead of a hunt for every `if` that should have changed.

A copy is not in the table because it does not change the scenario it copies. Any scenario may be
copied, a locked one included, and the copy always starts in Initial with a `parent_id`, as in
lesson 12.1.1.

<!-- practice 1 -->

## A Write Names the Version It Read, and a Stale Write Is Refused

Two planners open `S-001` in two tabs. `planner-a` cuts the 2029 budget and saves; a minute later
`planner-b`, whose tab still shows the old budgets, changes 2031 and saves. If the service simply
stored whatever arrived, `planner-b`'s save would write back the old 2029 budget along with the new
2031 one, and `planner-a`'s cut would vanish without a trace. That is a **lost update**.

The cure used here is **optimistic locking**: every scenario has a version number, every read
returns it, every write must state the version it read, and the service refuses a write whose
version is no longer current. Nothing is held locked while a planner thinks, which is why it is
called optimistic; the conflict is caught when it happens, at the write.

```python
    def _current(self, sid: str, expected_version: int) -> Record:
        rec = self.records[sid]
        if rec.version != expected_version:
            raise Refused(f"{sid} is at version {rec.version}, not {expected_version}; read it again")
        return rec
```

```python
    def read(self, sid: str) -> tuple[Scenario, str, int]:
        """A private copy of the scenario, its state and its version: editing the copy changes nothing stored."""
        rec = self.records[sid]
        return copy.deepcopy(rec.scenario), rec.state, rec.version
```

`read` hands back a deep copy, so a planner's unsaved changes live only in that copy: the stored
scenario changes only through `edit`, which checks the version first. `concurrent_edits.py` plays the
two tabs:

```text
planner-a and planner-b both read version 1
planner-a saves 2029 = 8000:   version 2
planner-b saves 2031 = 7000:  refused: S-001 is at version 2, not 1; read it again
planner-b reads again, saves:  version 3 | budgets 2029 and 2031: 8000 7000
```

`planner-b`'s first save is refused, not merged. The service cannot know whether the 2031 change
still makes sense with the new 2029 budget, so it asks the person to read the scenario again and
decide. After the second read and save, both changes are in the scenario: 8,000 for 2029 and 7,000
for 2031.

Every successful write adds one to the version, state moves included, so a version number names
exactly one state of the scenario.

<!-- practice 2 -->

## A Run Belongs to the Version It Started From

A solve on GridCap medium or large can take minutes (lesson 12.4.2 runs such
solves as jobs). While it runs, a planner may edit the scenario. When the run finishes, its plan
answers the old inputs. If the service attached it anyway, the scenario would sit in Post-Opt with
a plan that no run of its current inputs produced.

So a run carries a **ticket**: the scenario id, the version it started from, and a private copy of
the inputs it solves. The ticket is taken when the run starts, and the run is attached only if the
scenario is still at that version:

```python
    def start_run(self, sid: str) -> Ticket:
        rec = self.records[sid]
        if (rec.state, "optimize") not in TRANSITIONS:
            raise Refused(f"{sid} is {rec.state}; optimize is not allowed there")
        return Ticket(sid, rec.version, copy.deepcopy(rec.scenario))

    def finish_run(self, ticket: Ticket, result: Result) -> int:
        """Attach a finished run, unless the scenario was changed while it ran."""
        rec = self._current(ticket.scenario_id, ticket.version)
        self._move(rec, "optimize")
        rec.result, rec.version = result, rec.version + 1
        return rec.version
```

The run solves `ticket.inputs`, never the stored scenario, which may change under it. In the
program a planner edits the 2030 budget while the run is out:

```text
run started at version 4; planner-a edits 2030 meanwhile: version 5
run finished, attach: refused: S-001 is at version 5, not 4; read it again
rerun on version 5: attached, Post-Opt, NPV $23,508k (the stale run said $23,866k)
```

The stale run's NPV, $23,866k, is a real number for the inputs of version 4. Shown beside the
budgets of version 5 it would overstate the plan by $358k. The service refuses it, the scenario
stays in Pre-Opt, and the rerun on version 5 is the one attached. This is the "result current" check
of lesson 12.1.1 made into a rule: there it was a function a caller could forget to call, here the
service will not attach a run that fails it.

## Budget Lock Needs a Current Optimal Run, and a Cycle Has One Plan of Record

Locking is the last move, and the most consequential one: the locked plan is the **plan of
record**, the one finance budgets against and the regulator sees (lesson 7.1.3). `lock` checks
three things before it moves the scenario:

```python
        if (rec.state, "lock") not in TRANSITIONS:
            raise Refused(f"{sid} is {rec.state}; lock is not allowed there")
        if rec.result is None or rec.result.snapshot != rec.scenario.snapshot():
            raise Refused(f"{sid} has no run on its current inputs")
        if rec.result.status != "OPTIMAL":
            raise Refused(f"{sid}'s run is {rec.result.status}, not a plan")
        for other in self.records.values():
            if other.cycle == rec.cycle and other.state == "Budget Lock":
                raise Refused(f"{rec.cycle} already has a plan of record: {other.scenario.scenario_id}")
```

- **The table.** Only a Post-Opt scenario may be locked.
- **A current, optimal run.** The run's snapshot must equal the scenario's, and the run must have
  found a plan. In this service the table already guarantees the first, because any edit leaves
  Post-Opt; the check stays as a second line of defence, since a lock is too important to rest on one
  rule. An infeasible run also ends in Post-Opt (a run finished), so the status check is not
  redundant: an infeasible scenario has no plan to lock.
- **One plan of record per cycle.** Every scenario belongs to a planning cycle, here `2027 plan`.
  If another scenario of the same cycle is already locked, the lock is refused.

The end of `concurrent_edits.py` locks `S-001`, then tries to lock an alternative scenario of the
same cycle:

```text
lock S-002: refused: 2027 plan already has a plan of record: S-001
```

Without that rule, two locked scenarios could both claim to be the plan of record, and finance and
the regulator could be handed different plans, each correctly locked. Replacing a plan of record is
a decision, which this service would model as an explicit action (unlock the old one with a reason,
then lock the new one), never as a side effect of locking something else. Lesson 12.1.4 enforces
this rule in the database itself, where two service processes cannot both pass it.

<!-- practice 3 -->

## Summary

- **Every request is checked against one transition table.** A state and an action give the next
  state, or a refusal; the table is printable and is the only place the rules live.
- **A write names the version it read, and a stale write is refused.** Optimistic locking prevents
  lost updates without holding anything locked while people think.
- **A run belongs to the version it started from.** A run solves a private copy of the inputs and is
  attached only if the scenario has not changed since it started.
- **Budget Lock needs a current optimal run, and a cycle has one plan of record.** Locking checks
  the table, the run's snapshot and status, and the other scenarios of the cycle.

## Reference

| Action | Allowed in | Moves to | Adds to the version |
| --- | --- | --- | --- |
| `edit` | Initial, Pre-Opt, Post-Opt | Initial, Pre-Opt, Pre-Opt | 1 |
| `check` | Initial | Pre-Opt | 1 |
| `optimize` (finish a run) | Pre-Opt, Post-Opt | Post-Opt | 1 |
| `lock` | Post-Opt, with a current optimal run, none locked in the cycle | Budget Lock | 1 |
| copy | any state | a new scenario in Initial, version 1 | 0 (the original is untouched) |

| Term | Meaning |
| --- | --- |
| state machine | states, actions, and a table of the allowed moves |
| lost update | a write based on an old read that silently undoes someone else's write |
| optimistic locking | refuse a write whose stated version is no longer current |
| ticket | a run's scenario id, starting version and private copy of the inputs |
| plan of record | the one locked plan of a planning cycle |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt)
(a model is built apart from the solver, which is what lets a run solve a private copy of the inputs
while the stored scenario changes); Python's [`copy` module](https://docs.python.org/3/library/copy.html)
(`deepcopy`, which `read` and `start_run` use so that no caller holds the stored scenario).

## Challenges

1. Add a stage `Review` between Post-Opt and Budget Lock, which takes no edits. Write the new rows
   of `TRANSITIONS`, and predict which program lines change.
2. `finish_run` refuses a stale run outright. Design a variant that keeps the stale result as
   history without attaching it. What must a planner's screen say about it?
3. Why does `lock` check the snapshot when the table already makes it equal? Find a change to the
   service that would make the snapshot check catch something.

## Design Note: Refuse, Don't Merge

Both conflicts in this lesson, two planners editing one scenario and an edit during a run, could be
"resolved" automatically: merge the two budget changes, or attach the stale run with a warning. The
service refuses both instead, and asks a person to look again. A merged scenario is one that no
person reviewed, and an attached stale run is a plan that no run of the current inputs produced.
Lesson 7.1.3's rule was that every change goes back through the model; this lesson adds that every
change goes back through a person who saw the current version.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**cycle_states.py.** Prints the transition table and walks the base scenario from Initial to Budget
Lock, with the refusals on the way and a copy of the locked scenario (*Every Request Is Checked
Against One Transition Table*). *Try:* call `svc.check` again right after the first `check`, and
predict the message.

- Program: [cycle_states.py](src/cycle_states.py)

**concurrent_edits.py.** Two planners and a stale save, a run overtaken by an edit, and a second
lock in the same cycle (*A Write Names the Version It Read*, *A Run Belongs to the Version It
Started From*, *Budget Lock Needs a Current Optimal Run*). *Try:* put `S-002` in a cycle called
`2027 plan revision` and predict whether its lock succeeds.

- Program: [concurrent_edits.py](src/concurrent_edits.py)

**cycle.py.** The transition table and the in-memory `Service` with `read`, `edit`, `check`,
`start_run`, `finish_run`, `lock` and `copy`. It prints nothing itself.

- Library: [cycle.py](src/cycle.py)
