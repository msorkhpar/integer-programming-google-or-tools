# 12.1.4 Storing Scenarios and Results in SQLite

The scenario service of lessons 12.1.1 to 12.1.3 forgets everything when its process stops. Its
rules also live only in Python: any script that opens the data directly can edit a locked scenario,
delete an audit entry, or save half a run. GridCap's planners need the base scenario, the
`three-overrides` copy, the trail of who changed what, and both runs to be there tomorrow, exactly as
they were left, and they need the rules to hold whoever writes to the store.

This lesson stores scenarios, audit entries and runs in **SQLite**, a database engine that keeps a
whole database in one file and ships with Python as the `sqlite3` module, so it needs no server and
runs in the course's offline runner. It moves the rules of the earlier lessons into the database
where it can: transactions keep a change and its audit entry together, the version check becomes
part of the `UPDATE`, and triggers and a partial unique index refuse what no caller may do. The
lesson ends with the module's whole workflow: copy a scenario, override three projects, re-optimize,
and diff the two runs in SQL.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real. The
people (`planner-a`, ...) are placeholders. The programs put their database in a temporary directory
and delete it when they finish.

## The Model

Storage does not change the model: every run stored here solved the model of lesson 12.1.2,
restated here.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k), from the scenario's stored inputs;
$`l_{i,t}`$ and $`u_{i,t}`$, the bounds set by the scenario's overrides (lesson 12.1.2).

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

A stored run keeps the solution $`x^*`$ as one row per funded project, `(project, start_year)`,
which is the pair $`(i, t)`$ with $`x^*_{i,t} = 1`$.

## A Scenario's Inputs Are One JSON Column, and a Run's Plan Is Rows

Four tables hold everything. Here are the scenario and run tables of `store.SCHEMA`:

```python
CREATE TABLE scenario (
    scenario_id TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    cycle       TEXT NOT NULL,
    parent_id   TEXT REFERENCES scenario (scenario_id),
    state       TEXT NOT NULL CHECK (state IN ('Initial', 'Pre-Opt', 'Post-Opt', 'Budget Lock')),
    version     INTEGER NOT NULL,
    inputs      TEXT NOT NULL CHECK (json_valid(inputs)),
    snapshot    TEXT NOT NULL,
    created_by  TEXT NOT NULL,
    created_at  TEXT NOT NULL
) STRICT;
```

```python
CREATE TABLE run (
    run_id      INTEGER PRIMARY KEY,
    scenario_id TEXT NOT NULL REFERENCES scenario (scenario_id),
    version     INTEGER NOT NULL,
    snapshot    TEXT NOT NULL,
    status      TEXT NOT NULL,
    npv         INTEGER
) STRICT;

CREATE TABLE run_start (
    run_id      INTEGER NOT NULL REFERENCES run (run_id),
    project     TEXT NOT NULL,
    start_year  INTEGER NOT NULL,
    PRIMARY KEY (run_id, project)
) STRICT;
```

The fourth table, `audit`, has one column per field of lesson 12.1.2's `AuditEntry`, with the bound
changes in a JSON column.

Two choices shape the schema, and they go opposite ways for a reason.

**A scenario's inputs are one JSON text column.** The service always reads and writes the inputs as
a whole: to build a model, to compute the snapshot, to copy. Nobody asks the database "which
scenarios have a 2030 budget above $8,000k". So the inputs are stored as the same canonical JSON
that `Scenario.inputs()` produces, and the snapshot sits in its own column beside them. SQLite keeps
JSON as ordinary text, and the `CHECK (json_valid(inputs))` refuses text that is not well-formed
JSON. The state, version, cycle and names are separate columns because the service does query them:
every write filters on `version`, and the lock rule below filters on `cycle` and `state`.

**A run's plan is rows**, one per funded project, because plans *are* queried: the diff at the end of
this lesson compares two runs project by project in SQL. The primary key `(run_id, project)` makes
"one start year per project per run" a rule the database keeps.

`STRICT` after a table makes SQLite enforce the declared column types, which ordinary SQLite tables
do not: without it, a text value such as `'soon'` in the `INTEGER` column `start_year` would be
stored as it is. A `STRICT` table converts a value only when nothing is lost, and refuses the rest.
`INTEGER PRIMARY KEY` gives each run an id the database assigns, which is where ids come from in a
real service (lesson 12.1.1's design note). The run keeps the `version` and `snapshot` it was solved
on, so lesson 12.1.3's question "does this run belong to the scenario's current inputs?" can be
answered from the tables.

## Foreign Keys Are Off Until a Connection Turns Them On, Outside Any Transaction

`REFERENCES scenario (scenario_id)` declares a **foreign key**: every run must name a scenario that
exists. SQLite's documentation says foreign key enforcement is off by default, must be switched on
by each connection with `PRAGMA foreign_keys = ON`, and cannot be switched on in the middle of a
transaction, where the pragma does nothing and reports no error. Python's `sqlite3` adds a twist.
With `autocommit=False`, which its documentation recommends, a transaction is always open, starting
with `connect()` itself. `fk_pragma.py` tries both orders on two in-memory databases.

Two of the features this lesson uses are recent, so check your versions before you copy the code.
The `autocommit` argument of `sqlite3.connect()` and the `Connection.autocommit` attribute exist
from Python `3.12` on; on an older Python, `connect()` refuses the argument. `FULL OUTER JOIN`, used by
the diff query at the end of this lesson and by its last practice, is understood by the SQLite
library from version `3.39.0` on; an older library reports a syntax error. Python's `sqlite3` uses
the SQLite library it was built with, which is not always the newest one on the machine. The first
line `fk_pragma.py` prints is the runner's two versions, both new enough:

```python
print("Python", sys.version.split()[0], "  SQLite library", sqlite3.sqlite_version)
```

```text
Python 3.14.7   SQLite library 3.46.1
```

The rest of the program tries the two orders:

```python
conn = sqlite3.connect(":memory:", autocommit=False)
conn.execute("PRAGMA foreign_keys = ON")
print("autocommit=False opens a transaction at once:", conn.in_transaction)
```

```text
autocommit=False opens a transaction at once: True
pragma sent inside that transaction      foreign_keys=0  orphan run stored
pragma sent first, then autocommit=False foreign_keys=1  refused: FOREIGN KEY constraint failed
```

In the first database the pragma was swallowed, and a run for the scenario `S-999`, which does not
exist, was stored. Nothing failed. The store opens its connections the second way:

```python
def connect(path: str) -> sqlite3.Connection:
    """Open the store. The pragma must run before any transaction is open, or SQLite ignores it."""
    conn = sqlite3.connect(path, autocommit=True)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.autocommit = False
    conn.row_factory = sqlite3.Row
    return conn
```

It connects in autocommit mode, where no transaction is open, sends the pragma, and only then
switches to `autocommit=False`. `sqlite3.Row` lets the code read columns by name (`row["state"]`).
The first line `sqlite_store.py` prints is the check that it worked:

```text
foreign keys on: True
```

## A Change and Its Audit Entry Commit Together, or Not at All

A **transaction** is a group of statements the database applies as one: all of them, or none. In
`sqlite3`, a connection used as a context manager (`with conn:`) commits when the block ends normally
and rolls back when it raises; it does not close the connection, which the programs do with
`contextlib.closing`. The store wraps every change that belongs together in one such block. An
override and its audit entry are one change:

```python
    with conn:
        if problems:
            _audit(conn, sid, "refused", o, by, at, why, problems)
            return expected_version
        changes = bound_changes(s.overrides.get(o.project), o, portfolio.project(o.project))
        s.overrides[o.project] = o
        version = _write(conn, s, state, "edit", expected_version)
        _audit(conn, sid, "set", o, by, at, why, list(changes))
        return version
```

If `_write` refuses (a stale version, below), the block raises and the audit entry is never stored,
so the trail cannot claim an override that the scenario does not have. The reverse holds too: an
override cannot be stored without its entry. Lesson 12.1.2's check that the trail replays to the
overrides in force depends on this.

A run is three changes: the `run` row, its `run_start` rows, and the scenario's move to Post-Opt.

```python
    with conn:
        run_id = conn.execute("INSERT INTO run (scenario_id, version, snapshot, status, npv) VALUES (?, ?, ?, ?, ?)",
                              (ticket.scenario_id, ticket.version, result.snapshot, result.status,
                               result.npv)).lastrowid
        conn.executemany("INSERT INTO run_start VALUES (?, ?, ?)",
                         [(run_id, p, t) for p, t in result.starts.items()])
        _write(conn, s, state, "optimize", ticket.version)
        return run_id
```

Every value reaches SQL through a `?` placeholder, never through string formatting. The `sqlite3`
documentation insists on this to prevent SQL injection: a planner's reason containing a quote, such
as `no crew ' OR 1=1 --`, stays text instead of becoming SQL. `sqlite_store.py` tries to save a run
whose plan has a project with no start year, which the `NOT NULL` on `start_year` refuses after the
`run` row was already inserted:

```text
save a run with a missing year     IntegrityError: NOT NULL constraint failed: run_start.start_year
runs before and after the failed save: 2 2
```

Still two runs. The `run` row inserted before the failure was rolled back with it, so the store
never holds a run without its plan, which a diff would read as "funds nothing".

<!-- practice 1 -->

## The Version Check Is the UPDATE's WHERE Clause, and rowcount Says Whether It Held

Lesson 12.1.3 compared versions in Python. Reading the version and then writing is two steps, and
another process could write in between. In SQL the check and the write are one statement:

```python
    cur = conn.execute(
        "UPDATE scenario SET inputs = ?, snapshot = ?, state = ?, version = version + 1 "
        "WHERE scenario_id = ? AND version = ?",
        (json.dumps(s.inputs(), sort_keys=True, separators=(",", ":")), s.snapshot(), nxt, s.scenario_id, expected_version))
    if cur.rowcount == 0:
        raise Refused(f"{s.scenario_id} changed since version {expected_version}; read it again")
```

The `UPDATE` changes the row only if it still has the version the caller read. `Cursor.rowcount`
reports how many rows an `UPDATE` changed, so 0 means somebody else wrote first.
`version = version + 1` is computed by the database from the row it is changing, never from a number the caller sends.
`sqlite_store.py` sends an edit of `S-002` stamped with version 2 after the scenario has
moved on:

```text
edit S-002 from version 2          Refused: S-002 changed since version 2; read it again
```

`_write` also runs lesson 12.1.3's transition table before the `UPDATE` (`TRANSITIONS.get((state,
action))`), so the state machine and the version check guard every path that changes a scenario.

## The Database Refuses What No Caller May Do

Some rules must hold even for code that never calls the service: a maintenance script, a
colleague's notebook, a bug in a future handler. Those rules go into the schema.

```python
CREATE UNIQUE INDEX one_plan_of_record ON scenario (cycle) WHERE state = 'Budget Lock';

CREATE TRIGGER locked_is_frozen BEFORE UPDATE ON scenario WHEN OLD.state = 'Budget Lock'
BEGIN SELECT RAISE(ABORT, 'scenario is locked; copy it to change it'); END;
```

```python
CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit
BEGIN SELECT RAISE(ABORT, 'the audit trail is append-only'); END;
CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit
BEGIN SELECT RAISE(ABORT, 'the audit trail is append-only'); END;
```

A **trigger** is SQL the database runs when a table is changed. `BEFORE UPDATE ... WHEN OLD.state =
'Budget Lock'` fires on any update of a row that is locked (`OLD` is the row before the change), and
`RAISE(ABORT, ...)` stops the statement, undoes what it did, and returns the message as an error.
The audit triggers fire on every update or delete of the trail, which makes it append-only for
every writer.

A **partial index** indexes only the rows its `WHERE` clause selects. Declared `UNIQUE`, it makes a
column unique among those rows only: here, `cycle` is unique among locked scenarios, so a cycle has
at most one plan of record, while any number of unlocked scenarios share it. That is lesson 12.1.3's
loop over all scenarios, kept by the database.

After locking `S-001`, `sqlite_store.py` goes around the service with raw SQL and tries each rule:

```text
S-001 locked, version 4
UPDATE the locked S-001            IntegrityError: scenario is locked; copy it to change it
DELETE an audit entry              IntegrityError: the audit trail is append-only
lock S-002 in the same cycle       IntegrityError: UNIQUE constraint failed: scenario.cycle
```

The first two came from raw `UPDATE` and `DELETE` statements that no service code wrote; the third
came through `store.lock`, whose own Python has no "one per cycle" check at all. All three are
refused by the database. The message of the last one is the database's, not a planner's sentence; a
service catches `IntegrityError` and translates it, as lesson 9.1.6 translates
rows into rules.

<!-- practice 2 -->

## Copy, Override Three Projects, Re-Optimize, and Diff the Runs in SQL

`sqlite_store.py` runs the whole workflow of this module against the store. It creates and solves
the base scenario, copies it to `S-002`, has three planners override three projects (the three
overrides that stayed in force in lesson 12.1.2), checks and solves the copy, and lists the runs:

```text
{'run_id': 1, 'scenario_id': 'S-001', 'version': 2, 'snap': 'b752239b45c2', 'status': 'OPTIMAL', 'npv': 24260}
{'run_id': 2, 'scenario_id': 'S-002', 'version': 5, 'snap': 'fccf226e6497', 'status': 'OPTIMAL', 'npv': 22989}
```

Each run records the version and snapshot it was solved on. Run 1 started from version 2 of the
base (after its `check`); run 2 from version 5 of the copy, after three overrides and a `check`.
The trail of the copy, read back from the `audit` table:

```text
#1 2027-03-01T09:10Z planner-a set     P024 start_in 2030   Ridge customers were promised 2030
#2 2027-03-01T09:15Z planner-b set     P032 out             waiting for the Valley line study
#3 2027-03-01T09:20Z planner-c set     P036 not_before 2029 no Coast crew before 2029
```

The diff of the two runs is one query. A **full outer join** keeps every project that is in either
plan, with `NULL` on the side that lacks it, which is exactly the shape of selected, deferred and
shifted:

```python
DIFF = """
SELECT coalesce(a.project, b.project) AS project, a.start_year AS a_year, b.start_year AS b_year
FROM (SELECT project, start_year FROM run_start WHERE run_id = :a) AS a
FULL OUTER JOIN (SELECT project, start_year FROM run_start WHERE run_id = :b) AS b
     ON a.project = b.project
WHERE a.start_year IS NOT b.start_year
ORDER BY project
"""
```

A row with no year in run a is selected, one with no year in run b is deferred, and one with two
different years is shifted. `IS NOT` treats `NULL` as an ordinary value, so a project present on
one side only passes the filter; with `<>`, any comparison with `NULL` is unknown and the row would
be dropped. `:a` and `:b` are
named placeholders, the other style the `sqlite3` documentation describes.

```text
diff in SQL: {'selected': ['P024', 'P038', 'P040'], 'deferred': ['P016', 'P032'], 'shifted': ['P008 2031->2029', 'P011 2031->2029', 'P018 2030->2031', 'P025 2028->2027', 'P031 2028->2027', 'P039 2028->2027']}
same as diff_plans in Python: True
```

It is the diff lesson 12.1.2 printed in memory, and the program checks that the SQL answer equals
`diff_plans` on the same two plans. Last, the program closes the database, opens the file again
with a new connection, and reads `S-002` back:

```text
reopened: S-002 Post-Opt version 6, overrides ['P024 start_in 2030', 'P032 out', 'P036 not_before 2029']
snapshot matches its run: True
trail replays to the stored overrides: True
```

The scenario survived the restart in its state and version, its recomputed snapshot equals the one
stored with its run (so the run is current), and replaying the stored trail gives the stored
overrides, the check of lesson 12.1.2, now against the database.

<!-- practice 3 -->

## Summary

- **A scenario's inputs are one JSON column, and a run's plan is rows.** Store as a whole what is
  used as a whole; store as rows what is queried. `STRICT` enforces column types.
- **Foreign keys are off until a connection turns them on, outside any transaction.** With
  `autocommit=False` the pragma is silently ignored; send it first.
- **A change and its audit entry commit together, or not at all.** `with conn:` commits or rolls
  back the whole block; values go through `?` placeholders.
- **The version check is the UPDATE's WHERE clause, and rowcount says whether it held.** Zero rows
  changed means a stale read.
- **The database refuses what no caller may do.** Triggers freeze locked scenarios and the audit
  trail; a partial unique index allows one plan of record per cycle.
- **Diff runs in SQL** with a full outer join over the plan rows.

## Reference

| Rule | Where it is enforced |
| --- | --- |
| state names are the four stages | `CHECK (state IN (...))` |
| inputs are JSON | `CHECK (json_valid(inputs))` |
| a run names an existing scenario | `REFERENCES`, with `PRAGMA foreign_keys = ON` |
| one start year per project per run | `PRIMARY KEY (run_id, project)` |
| a locked scenario never changes | trigger `locked_is_frozen` |
| the trail is append-only | triggers `audit_no_update`, `audit_no_delete` |
| one plan of record per cycle | partial unique index `one_plan_of_record` |
| no stale write | `UPDATE ... WHERE version = ?` and `rowcount` |
| a change and its entry together | `with conn:` |

| `sqlite3` | Meaning |
| --- | --- |
| `connect(path, autocommit=True)` | no implicit transactions; needed to send `PRAGMA foreign_keys` |
| `conn.autocommit = False` | a transaction is always open; `commit()` and `rollback()` end it |
| `with conn:` | commit on success, roll back on an exception; does not close |
| `?`, `:name` | placeholders for values; never format values into SQL |
| `cursor.rowcount` | rows changed by the last `UPDATE`, `INSERT` or `DELETE` |
| `conn.row_factory = sqlite3.Row` | rows readable by column name |

**Further reading:** Python's [`sqlite3` module](https://docs.python.org/3/library/sqlite3.html)
(placeholders and SQL injection, `autocommit`, the connection as a context manager, `rowcount`,
`sqlite3.Row`); SQLite's [foreign key support](https://www.sqlite.org/foreignkeys.html) (off by
default, per connection, not inside a transaction); SQLite's
[`CREATE TRIGGER`](https://www.sqlite.org/lang_createtrigger.html) and
[`ON CONFLICT`](https://www.sqlite.org/lang_conflict.html) (what `RAISE(ABORT, ...)` undoes);
SQLite's [`3.39.0` release notes](https://www.sqlite.org/releaselog/3_39_0.html) (where `RIGHT`
and `FULL OUTER JOIN` were added); SQLite's [partial indexes](https://www.sqlite.org/partialindex.html) (the one-leader-per-team
example is the same shape as one plan of record per cycle); SQLite's
[STRICT tables](https://www.sqlite.org/stricttables.html) and [JSON functions](https://www.sqlite.org/json1.html)
(`json_valid`); FastAPI's [SQL databases tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
(a SQLite database behind an API, with one session per request, which lesson 12.4.1 builds on).

## Challenges

1. Add a query that lists every scenario whose latest run is stale: its snapshot differs from the
   scenario's. Which columns does it need?
2. The `audit` triggers stop `UPDATE` and `DELETE`. What would still let someone rewrite history,
   and how would a content hash of each entry chained to the one before it catch it?
3. A planner wants to search scenarios by their 2030 budget. Write the query with `->>` on the
   `inputs` column, and say when it would be worth adding a column instead.

## Design Note: Rules in Two Places, on Purpose

Several rules here exist twice: the Python service checks the transition table and the lock
conditions, and the database refuses locked updates and a second plan of record. The service's
checks give a planner a clear sentence and run before any SQL; the database's checks hold for every
writer, including ones that skip the service. A rule kept only in Python is a convention; a rule
kept only in the database answers with messages like `UNIQUE constraint failed: scenario.cycle`.
Keeping both, and testing that they agree (lesson 12.3.1), gives clear
messages and rules that hold.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**fk_pragma.py.** The foreign key pragma sent inside and outside a transaction (*Foreign Keys Are
Off Until a Connection Turns Them On*). *Try:* connect with no `autocommit` argument at all, send
the pragma, and predict which line you get.

- Program: [fk_pragma.py](src/fk_pragma.py)

**sqlite_store.py.** The module's workflow on SQLite: base and copy, three overrides, two runs, the
diff in SQL, the refusals, and the reopened database (every section of this lesson). *Try:* lock
`S-002` before `S-001` and predict which lock is refused.

- Program: [sqlite_store.py](src/sqlite_store.py)

**store.py.** The schema, `connect`, and the store's functions: `add`, `read`, `edit`,
`check_inputs`, `request`, `trail`, `start_run`, `save_run`, `lock`, `copy` and `diff_runs`. It prints
nothing itself.

- Library: [store.py](src/store.py)
