"""Lesson 14.2.7: scenarios over one stored snapshot of GridCap small, in a SQLite file.

GridCap small is a fictional utility's portfolio. The store lives in a temporary directory and is
deleted when the program ends.
"""

import sqlite3
import tempfile
from pathlib import Path

from export import gridcap_export
from steps import use

raw = gridcap_export("small")
cipt = use(7)
Scenario = cipt.scenario.Scenario

with tempfile.TemporaryDirectory() as tmp:
    store = cipt.store.Store(Path(tmp) / "cipt.db")
    snapshot = store.save_snapshot(raw)
    print(f"snapshot {snapshot[:12]}, saved twice: {store.save_snapshot(raw) == snapshot}")
    scenarios = [
        Scenario("base"),
        Scenario("cut 2029", budget={2029: 6000}, note="finance holds back $2,760k in 2029"),
        Scenario("hold P028", force_out=("P028",), note="P028 waits for a permit"),
        Scenario("P030 first", force_in=("P030",), note="the board wants the Valley rebuild"),
    ]
    for s in scenarios:
        store.save_scenario(s, snapshot)
    plans = {s.name: store.run(s.name) for s in scenarios}
    store.run("base")
    base = plans["base"]
    print("scenario      NPV ($k)   risk ($k)   selected   deferred   shifted")
    for name, plan in plans.items():
        d = cipt.scenario.diff(base, plan)
        print(f"{name:<11} {plan.npv:>10,.0f}   {plan.risk:>9,.1f}   {len(d.selected):>8}   "
              f"{len(d.deferred):>8}   {len(d.shifted):>7}")
    d = cipt.scenario.diff(base, plans["P030 first"])
    print("P030 first, selected: " + ", ".join(d.selected) + "; deferred: " + ", ".join(d.deferred))
    print("P030 first, shifted: " + ", ".join(f"{p} {a}->{b}" for p, a, b in d.shifted))
    runs = store.runs("base")
    print(f"base runs stored: {len(runs)}, same plan: {runs[0].starts == runs[1].starts}; "
          f"hold P028 and P030 first give one plan: {plans['hold P028'].starts == plans['P030 first'].starts}")
    with sqlite3.connect(Path(tmp) / "cipt.db") as db:
        print("tables: " + ", ".join(f"{t} {n}" for t, n in
              ((t, db.execute(f"SELECT count(*) FROM {t}").fetchone()[0]) for t in ("snapshot", "scenario", "run"))))

    both = Scenario("both", force_in=("P030", "P031"))
    request = cipt.scenario.apply(cipt.data.load_request(raw), both)
    print(cipt.diagnose.why_infeasible(request).message)
