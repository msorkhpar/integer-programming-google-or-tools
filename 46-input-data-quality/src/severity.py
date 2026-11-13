"""Lesson 12.2.2: an error proves the snapshot wrong or the model plan-less; a warning only doubts.

Each case is compared with the last accepted snapshot (GridCap small as exported). GridCap is a
fictional utility.
"""

import copy
import json

from gridcap import generate
from plan_model import build, outcome, plan, solve
from quality import blocked, gate, report
from snapshot import export, load, project

base = export(generate("small"))
previous = load(json.dumps(base))


def planted(edit) -> dict:
    doc = copy.deepcopy(base)
    edit(doc)
    return doc


def in_dollars_m(doc):
    doc["budget"] = [{"year": b["year"], "amount": round(b["amount"] / 1000)} for b in doc["budget"]]


cases = [
    ("P016 made must-do", planted(lambda d: project(d, "P016").update(must_do=True))),
    ("P016's lag typed 2 (P016 optional)", planted(lambda d: project(d, "P016").update(parent_lag=2))),
    ("budgets exported in $M", planted(in_dollars_m)),
    ("2029 budget cut 20%", planted(lambda d: d["budget"][2].update(amount=round(0.8 * d["budget"][2]["amount"])))),
]
for label, doc in cases:
    snap = load(json.dumps(doc))
    findings = gate(snap, previous)
    print(f"{label:<36} solver: {outcome(snap)}   blocked: {blocked(findings)}")
    report(findings)

forced = load(json.dumps(cases[0][1]))
pm = build(forced)
chosen = plan(pm, solve(pm))
print("P016 must-do: plan funds P015 in", chosen.get("P015"), "and P016 in", chosen.get("P016"))
