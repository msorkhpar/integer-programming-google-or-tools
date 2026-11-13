"""Scenarios, their audit trail and their runs stored in SQLite (lesson 12.1.4).

The rules of lessons 12.1.1 to 12.1.3 move into the database: a scenario's inputs are one JSON
column with its snapshot beside it, a write names the version it read, a locked scenario cannot be
updated, the audit trail cannot be updated or deleted, and a cycle has at most one plan of record.
"""

from __future__ import annotations

import json
import sqlite3

from cycle import TRANSITIONS, Refused, Ticket
from overrides import AuditEntry, Override, bound_changes, check
from scenario import Result, Scenario

SCHEMA = """
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

CREATE UNIQUE INDEX one_plan_of_record ON scenario (cycle) WHERE state = 'Budget Lock';

CREATE TRIGGER locked_is_frozen BEFORE UPDATE ON scenario WHEN OLD.state = 'Budget Lock'
BEGIN SELECT RAISE(ABORT, 'scenario is locked; copy it to change it'); END;

CREATE TABLE audit (
    seq         INTEGER PRIMARY KEY,
    scenario_id TEXT NOT NULL REFERENCES scenario (scenario_id),
    action      TEXT NOT NULL CHECK (action IN ('set', 'revoke', 'inherit', 'refused')),
    project     TEXT NOT NULL,
    kind        TEXT NOT NULL,
    year        INTEGER,
    by_whom     TEXT NOT NULL,
    at          TEXT NOT NULL,
    why         TEXT NOT NULL,
    changes     TEXT NOT NULL CHECK (json_valid(changes))
) STRICT;

CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit
BEGIN SELECT RAISE(ABORT, 'the audit trail is append-only'); END;
CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit
BEGIN SELECT RAISE(ABORT, 'the audit trail is append-only'); END;

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
"""


def connect(path: str) -> sqlite3.Connection:
    """Open the store. The pragma must run before any transaction is open, or SQLite ignores it."""
    conn = sqlite3.connect(path, autocommit=True)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.autocommit = False
    conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    with conn:
        for statement in SCHEMA.split(";\n"):
            if statement.strip():
                conn.execute(statement)


def add(conn: sqlite3.Connection, s: Scenario, cycle: str) -> None:
    with conn:
        conn.execute("INSERT INTO scenario VALUES (?, ?, ?, ?, 'Initial', 1, ?, ?, ?, ?)",
                     (s.scenario_id, s.name, cycle, s.parent_id, json.dumps(s.inputs(), sort_keys=True, separators=(",", ":")),
                      s.snapshot(), s.created_by, s.created_at))


def read(conn: sqlite3.Connection, sid: str) -> tuple[Scenario, str, int]:
    row = conn.execute("SELECT * FROM scenario WHERE scenario_id = ?", (sid,)).fetchone()
    record = {**json.loads(row["inputs"]), "scenario_id": sid, "name": row["name"], "parent_id": row["parent_id"],
              "created_by": row["created_by"], "created_at": row["created_at"]}
    return Scenario.from_json(json.dumps(record)), row["state"], row["version"]


def _write(conn: sqlite3.Connection, s: Scenario, state: str, action: str, expected_version: int) -> int:
    """Move a scenario through one action, saving its inputs, if nobody wrote it since `expected_version`."""
    nxt = TRANSITIONS.get((state, action))
    if nxt is None:
        raise Refused(f"{s.scenario_id} is {state}; {action} is not allowed there")
    cur = conn.execute(
        "UPDATE scenario SET inputs = ?, snapshot = ?, state = ?, version = version + 1 "
        "WHERE scenario_id = ? AND version = ?",
        (json.dumps(s.inputs(), sort_keys=True, separators=(",", ":")), s.snapshot(), nxt, s.scenario_id, expected_version))
    if cur.rowcount == 0:
        raise Refused(f"{s.scenario_id} changed since version {expected_version}; read it again")
    return expected_version + 1


def edit(conn: sqlite3.Connection, s: Scenario, expected_version: int) -> int:
    state = read(conn, s.scenario_id)[1]
    with conn:
        return _write(conn, s, state, "edit", expected_version)


def check_inputs(conn: sqlite3.Connection, sid: str, expected_version: int) -> int:
    s, state, _ = read(conn, sid)
    with conn:
        return _write(conn, s, state, "check", expected_version)


def request(conn: sqlite3.Connection, sid: str, expected_version: int, o: Override, portfolio,
            by: str, at: str, why: str) -> int:
    """An override and its audit entry in one transaction: both are stored, or neither is."""
    s, state, _ = read(conn, sid)
    problems = check(o, portfolio)
    with conn:
        if problems:
            _audit(conn, sid, "refused", o, by, at, why, problems)
            return expected_version
        changes = bound_changes(s.overrides.get(o.project), o, portfolio.project(o.project))
        s.overrides[o.project] = o
        version = _write(conn, s, state, "edit", expected_version)
        _audit(conn, sid, "set", o, by, at, why, list(changes))
        return version


def _audit(conn, sid, action, o, by, at, why, changes) -> None:
    conn.execute("INSERT INTO audit (scenario_id, action, project, kind, year, by_whom, at, why, changes) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (sid, action, o.project, o.kind, o.year, by, at, why, json.dumps(changes)))


def trail(conn: sqlite3.Connection, sid: str) -> list[AuditEntry]:
    return [AuditEntry(r["seq"], r["scenario_id"], r["action"], Override(r["project"], r["kind"], r["year"]),
                       r["by_whom"], r["at"], r["why"], tuple(json.loads(r["changes"])))
            for r in conn.execute("SELECT * FROM audit WHERE scenario_id = ? ORDER BY seq", (sid,))]


def save_run(conn: sqlite3.Connection, ticket: Ticket, result: Result) -> int:
    """Store a run, its plan and the scenario's move to Post-Opt together, or nothing at all."""
    s, state, _ = read(conn, ticket.scenario_id)
    with conn:
        run_id = conn.execute("INSERT INTO run (scenario_id, version, snapshot, status, npv) VALUES (?, ?, ?, ?, ?)",
                              (ticket.scenario_id, ticket.version, result.snapshot, result.status,
                               result.npv)).lastrowid
        conn.executemany("INSERT INTO run_start VALUES (?, ?, ?)",
                         [(run_id, p, t) for p, t in result.starts.items()])
        _write(conn, s, state, "optimize", ticket.version)
        return run_id


def lock(conn: sqlite3.Connection, sid: str, expected_version: int) -> int:
    s, state, _ = read(conn, sid)
    with conn:
        return _write(conn, s, state, "lock", expected_version)


def start_run(conn: sqlite3.Connection, sid: str) -> Ticket:
    s, state, version = read(conn, sid)
    if (state, "optimize") not in TRANSITIONS:
        raise Refused(f"{sid} is {state}; optimize is not allowed there")
    return Ticket(sid, version, s)


DIFF = """
SELECT coalesce(a.project, b.project) AS project, a.start_year AS a_year, b.start_year AS b_year
FROM (SELECT project, start_year FROM run_start WHERE run_id = :a) AS a
FULL OUTER JOIN (SELECT project, start_year FROM run_start WHERE run_id = :b) AS b
     ON a.project = b.project
WHERE a.start_year IS NOT b.start_year
ORDER BY project
"""


def diff_runs(conn: sqlite3.Connection, a: int, b: int) -> dict[str, list]:
    """Selected, deferred and shifted from run a to run b, computed by the database."""
    out = {"selected": [], "deferred": [], "shifted": []}
    for r in conn.execute(DIFF, {"a": a, "b": b}):
        if r["a_year"] is None:
            out["selected"].append(r["project"])
        elif r["b_year"] is None:
            out["deferred"].append(r["project"])
        else:
            out["shifted"].append(f"{r['project']} {r['a_year']}->{r['b_year']}")
    return out


def copy(conn: sqlite3.Connection, sid: str, new_id: str, name: str, by: str, at: str) -> None:
    """A copy in Initial, with one 'inherit' audit entry per override it starts with."""
    from scenario import copy_scenario
    parent, _, _ = read(conn, sid)
    cycle = conn.execute("SELECT cycle FROM scenario WHERE scenario_id = ?", (sid,)).fetchone()["cycle"]
    child = copy_scenario(parent, new_id, name, by, at)
    add(conn, child, cycle)
    with conn:
        for o in child.overrides.values():
            _audit(conn, new_id, "inherit", o, by, at, f"copied from {sid}", [])
