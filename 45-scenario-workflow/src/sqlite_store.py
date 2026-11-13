"""Lesson 12.1.4: the scenario workflow on SQLite: copy, override three projects, re-optimize, diff in SQL.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
The people (`planner-a`, ...) are placeholders. The database lives in a temporary directory.
"""

import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

import store
from gridcap import generate
from overrides import Override, replay
from scenario import Clock, Result, create, diff_plans, optimize

small = generate("small")
clock = Clock()

with tempfile.TemporaryDirectory() as folder:
    path = str(Path(folder) / "scenarios.db")
    with closing(store.connect(path)) as conn:
        store.create_schema(conn)
        print("foreign keys on:", conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1)

        store.add(conn, create(small, "small", "S-001", "base", by="planner-a", at=clock.now()), cycle="2027 plan")
        v = store.check_inputs(conn, "S-001", 1)
        ticket = store.start_run(conn, "S-001")
        run_base = store.save_run(conn, ticket, optimize(ticket.inputs))

        store.copy(conn, "S-001", "S-002", "three-overrides", by="planner-b", at=clock.now())
        v = 1
        for o, by, why in [(Override("P024", "start_in", 2030), "planner-a", "Ridge customers were promised 2030"),
                           (Override("P032", "out"), "planner-b", "waiting for the Valley line study"),
                           (Override("P036", "not_before", 2029), "planner-c", "no Coast crew before 2029")]:
            v = store.request(conn, "S-002", v, o, small, by=by, at=clock.now(), why=why)
        v = store.check_inputs(conn, "S-002", v)
        ticket = store.start_run(conn, "S-002")
        run_three = store.save_run(conn, ticket, optimize(ticket.inputs))

        for row in conn.execute("SELECT run_id, scenario_id, version, substr(snapshot, 1, 12) AS snap, status, npv "
                                "FROM run ORDER BY run_id"):
            print(dict(row))
        in_sql = store.diff_runs(conn, run_base, run_three)
        print("diff in SQL:", in_sql)
        a, b = (Result("", "", "", None, {r["project"]: r["start_year"] for r in
                conn.execute("SELECT * FROM run_start WHERE run_id = ?", (run,))}) for run in (run_base, run_three))
        print("same as diff_plans in Python:", in_sql == diff_plans(a, b))
        for e in store.trail(conn, "S-002"):
            print(e.line())

        v1 = store.lock(conn, "S-001", 3)
        print("S-001 locked, version", v1)

        def refused(label, fn):
            try:
                fn()
                print(f"{label:<34} accepted")
            except (sqlite3.IntegrityError, store.Refused) as e:
                conn.rollback()
                print(f"{label:<34} {type(e).__name__}: {e}")

        refused("UPDATE the locked S-001", lambda: conn.execute(
            "UPDATE scenario SET name = 'edited' WHERE scenario_id = 'S-001'"))
        refused("DELETE an audit entry", lambda: conn.execute("DELETE FROM audit WHERE seq = 1"))
        refused("lock S-002 in the same cycle", lambda: store.lock(conn, "S-002", v + 1))
        s, _, _ = store.read(conn, "S-002")
        refused("edit S-002 from version 2", lambda: store.edit(conn, s, 2))
        runs_before = conn.execute("SELECT count(*) FROM run").fetchone()[0]
        bad = Result("S-002", s.snapshot(), "OPTIMAL", 1, {"P001": 2028, "P002": None})
        refused("save a run with a missing year", lambda: store.save_run(conn, store.start_run(conn, "S-002"), bad))
        print("runs before and after the failed save:", runs_before,
              conn.execute("SELECT count(*) FROM run").fetchone()[0])
        conn.commit()

    with closing(store.connect(path)) as again:
        s, state, version = store.read(again, "S-002")
        print(f"reopened: S-002 {state} version {version}, overrides {[o.text() for o in s.overrides.values()]}")
        print("snapshot matches its run:", s.snapshot() == again.execute(
            "SELECT snapshot FROM run WHERE run_id = ?", (run_three,)).fetchone()[0])
        print("trail replays to the stored overrides:", replay(store.trail(again, "S-002"), "S-002") == s.overrides)
