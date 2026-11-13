"""Lesson 12.2.1: at a machine boundary, refuse unknown keys and refuse guessed conversions.

The same Snapshot schema, validated with the config it declares (extra="forbid", strict=True) and
with the per-call overrides extra="ignore" and strict=False. GridCap is a fictional utility.
"""

import copy
import json

from pydantic import ValidationError

from gridcap import generate
from snapshot import Snapshot, export, project

doc = export(generate("small"))


def verdict(text: str, **overrides) -> str:
    try:
        snap = Snapshot.model_validate_json(text, **overrides)
    except ValidationError as error:
        e = error.errors()[0]
        return f"refused: {'.'.join(str(p) for p in e['loc'])}: {e['msg']}"
    return f"accepted, P023 parent_lag={snap.projects[22].parent_lag}, " \
           f"P001 must_do={snap.projects[0].must_do}, 2027 budget={snap.budget[0].amount}"


renamed = copy.deepcopy(doc)
project(renamed, "P023")["lag"] = project(renamed, "P023").pop("parent_lag")   # the export renamed a column
print("P023 sends 'lag' instead of 'parent_lag'")
print("  extra='ignore' ", verdict(json.dumps(renamed), extra="ignore"))
print("  extra='forbid' ", verdict(json.dumps(renamed)))

text = json.dumps(doc)
for label, old, new in [("budget 8890 sent as \"8890\"", '"amount": 8890', '"amount": "8890"'),
                        ("budget 8890 sent as 8890.0", '"amount": 8890', '"amount": 8890.0'),
                        ("budget 8890 sent as 8890.5", '"amount": 8890', '"amount": 8890.5'),
                        ("P001 must_do sent as \"no\"", '"must_do": false', '"must_do": "no"')]:
    sent = text.replace(old, new, 1)
    print(label)
    print("  strict=False   ", verdict(sent, strict=False))
    print("  strict=True    ", verdict(sent))

try:
    Snapshot.model_validate(doc)
except ValidationError as error:
    e = error.errors()[0]
    print("the export's Python dict, strict:", ".".join(map(str, e["loc"])), "|", e["msg"])
