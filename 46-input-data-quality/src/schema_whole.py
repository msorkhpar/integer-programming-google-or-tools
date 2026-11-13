"""Lesson 12.2.1: one schema validates the whole snapshot and reports every problem in one pass.

GridCap is a fictional utility; the planted errors are typical of a planning export.
"""

import copy
import json

from pydantic import ValidationError

from gridcap import generate
from snapshot import export, load, project

doc = export(generate("small"))
text = json.dumps(doc)
snap = load(text)
print(f"{len(text):,} bytes -> Snapshot: {len(snap.projects)} projects, {len(snap.years)} years, "
      f"{len(snap.budget)} budgets, {len(snap.crews)} crew limits, {len(snap.region_floor)} floors")
print("P039:", snap.projects[38].cost_profile, snap.projects[38].must_do, snap.projects[38].npv)

bad = copy.deepcopy(doc)
project(bad, "P007")["cost_profile"] = [2140, -720]          # a credit typed as a cost
project(bad, "P012")["region"] = "Coastal"                   # a region the model has no floor for
project(bad, "P030")["npv"] = [4374]                         # one NPV for a two-year window
bad["budget"][1]["amount"] = None                             # a blank cell
project(bad, "P016")["parent"] = "P099"                       # a parent that is not in the snapshot
try:
    load(json.dumps(bad))
except ValidationError as error:
    print(f"{error.error_count()} problems in one pass:")
    for e in error.errors():
        print("  ", ".".join(str(part) for part in e["loc"]) or "snapshot", "|", e["msg"])
    print("P016's unknown parent reported:", any("P099" in e["msg"] for e in error.errors()))

broken = copy.deepcopy(doc)
broken["projects"].append(copy.deepcopy(project(doc, "P001")))   # a project exported twice
project(broken, "P016")["parent"] = "P099"                      # a parent that is not in the snapshot
broken["budget"].pop()                                           # no budget row for 2031
broken["crews"] = [c for c in broken["crews"] if (c["program"], c["year"]) != ("vegetation", 2030)]
try:
    load(json.dumps(broken))
except ValidationError as error:
    e = error.errors()[0]
    print(f"{error.error_count()} error at loc {e['loc']}:")
    for problem in e["msg"].removeprefix("Value error, ").split("; "):
        print("  ", problem)
