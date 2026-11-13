"""Lesson 12.2.1: the schema is a versioned contract, published as JSON Schema.

GridCap is a fictional utility.
"""

import json

from pydantic import ValidationError

from gridcap import generate
from snapshot import Snapshot, export

schema = Snapshot.model_json_schema()
print("required:", schema["required"])
print("additionalProperties:", schema["additionalProperties"])
print("schema_version:", schema["properties"]["schema_version"])
print("$defs:", sorted(schema["$defs"]))
print("ProjectIn.parent_lag:", schema["$defs"]["ProjectIn"]["properties"]["parent_lag"])
print("ProjectIn.project_id:", schema["$defs"]["ProjectIn"]["properties"]["project_id"])
print(f"published schema: {len(json.dumps(schema, sort_keys=True)):,} bytes of JSON")

doc = export(generate("small"))
old = {k: v for k, v in doc.items() if k != "schema_version"}                 # an export from before versions
for label, sent in [("no schema_version", old), ("schema_version 2", {**doc, "schema_version": 2})]:
    try:
        Snapshot.model_validate_json(json.dumps(sent))
    except ValidationError as error:
        e = error.errors()[0]
        print(f"{label:<18} refused: {e['loc'][0]}: {e['msg']}")


def upgrade(raw: dict) -> dict:
    """Bring an older export up to the current version, one explicit step per version."""
    if "schema_version" not in raw:                              # version 0: the column was called "lag"
        projects = [{("parent_lag" if k == "lag" else k): v for k, v in p.items()} for p in raw["projects"]]
        raw = {**raw, "projects": projects, "schema_version": 1}
    return raw


legacy = {**old, "projects": [{("lag" if k == "parent_lag" else k): v for k, v in p.items()} for p in old["projects"]]}
snap = Snapshot.model_validate_json(json.dumps(upgrade(legacy)))
print("version-0 export after upgrade(): accepted, P023 parent_lag =", snap.projects[22].parent_lag)
