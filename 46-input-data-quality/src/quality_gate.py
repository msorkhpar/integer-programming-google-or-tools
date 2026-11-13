"""Lesson 12.2.2: the quality gate runs every rule on a valid snapshot before the model is built.

Each planted error passes the schema of lesson 12.2.1: every field is well typed and every id
resolves. GridCap is a fictional utility.
"""

import copy
import json

from gridcap import generate
from plan_model import build, outcome, plan, solve
from quality import blocked, gate, report
from snapshot import export, load, project

base = export(generate("small"))


def planted(edit) -> dict:
    doc = copy.deepcopy(base)
    edit(doc)
    return doc


cases = [
    ("clean export", planted(lambda d: None)),
    ("P015's parent set to P016, lag 1", planted(lambda d: project(d, "P015").update(parent="P016", parent_lag=1))),
    ("P023 must-do, its lag typed 3", planted(lambda d: project(d, "P023").update(must_do=True, parent_lag=3))),
]
for label, doc in cases:
    snap = load(json.dumps(doc))                                  # the schema accepts every one
    findings = gate(snap)
    print(f"{label:<34} schema: valid   solver: {outcome(snap)}   blocked: {blocked(findings)}")
    report(findings)

clean, cycled = (load(json.dumps(doc)) for _, doc in cases[:2])
for name, snap in [("clean", clean), ("cycle", cycled)]:
    pm = build(snap)
    chosen = plan(pm, solve(pm))
    print(f"{name:<6} plan funds P015: {'P015' in chosen}, P016: {'P016' in chosen}")
