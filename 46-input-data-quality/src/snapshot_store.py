"""Lesson 12.2.3: versioned snapshots stored under their digest, and checked again on every read.

GridCap is a fictional utility.
"""

import copy
import json
import tempfile
from pathlib import Path

from gridcap import generate
from snapshot import export, load, project
from store import Corrupted, SnapshotStore, changes

doc = export(generate("small"))
cycle = copy.deepcopy(doc)
cycle["budget"][2]["amount"] = 7000                            # finance cuts 2029
project(cycle, "P024")["must_do"] = True                       # a planner commits P024

with tempfile.TemporaryDirectory() as tmp:
    store = SnapshotStore(Path(tmp))
    v1 = store.put(load(json.dumps(doc)), "planning export")
    again = store.put(load(json.dumps(doc, indent=2)), "same export, re-sent")
    v2 = store.put(load(json.dumps(cycle)), "2029 cut, P024 committed")
    for e in store.versions("GridCap small"):
        print(f"v{e['version']}  {e['digest'][:12]}  parent {str(e['parent'])[:12]:<12}  {e['note']}")
    print("re-sent export stored as v1 again:", again == v1, "| files:", len(list(Path(tmp).glob("*.json"))))
    print("v1 -> v2:", "; ".join(changes(store.get(v1), store.get(v2))))

    path = Path(tmp) / f"{v2}.json"
    path.write_bytes(path.read_bytes().replace(b'"amount":7000', b'"amount":7900'))   # an edit in place
    try:
        store.get(v2)
    except Corrupted as error:
        print("read v2 after an edit in place: refused,", error)
