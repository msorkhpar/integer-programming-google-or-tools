"""Lesson 12.2.3: a content-addressed snapshot store on disk, with a version log per scenario name.

Each snapshot is written once, as its canonical bytes, to `<digest>.json`. Reading it back hashes the
bytes again and refuses a file whose digest no longer matches its name. GridCap is a fictional utility.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from canonical import canonical
from snapshot import Snapshot


class Corrupted(Exception):
    pass


class SnapshotStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.log = root / "versions.jsonl"

    def put(self, snap: Snapshot, note: str) -> str:
        """Store a snapshot; return its digest. Equal content is stored once."""
        data = canonical(snap)
        key = hashlib.sha256(data).hexdigest()
        path = self.root / f"{key}.json"
        if not path.exists():
            path.write_bytes(data)
        versions = self.versions(snap.name)
        if not versions or versions[-1]["digest"] != key:
            entry = {"name": snap.name, "version": len(versions) + 1, "digest": key,
                     "parent": versions[-1]["digest"] if versions else None, "note": note}
            with self.log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return key

    def get(self, key: str) -> Snapshot:
        """Read a snapshot back, re-hash it, and validate it again; refuse a file that changed."""
        data = (self.root / f"{key}.json").read_bytes()
        found = hashlib.sha256(data).hexdigest()
        if found != key:
            raise Corrupted(f"{key[:12]}.json now hashes to {found[:12]}")
        return Snapshot.model_validate_json(data)

    def versions(self, name: str) -> list[dict]:
        if not self.log.exists():
            return []
        entries = [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]
        return [e for e in entries if e["name"] == name]


def changes(old: Snapshot, new: Snapshot) -> list[str]:
    """What differs between two versions: budgets by year, projects by id and field."""
    found = []
    before, after = {b.year: b.amount for b in old.budget}, {b.year: b.amount for b in new.budget}
    found += [f"budget {y}: {before.get(y)} -> {after.get(y)}" for y in sorted(before | after)
              if before.get(y) != after.get(y)]
    a, b = {p.project_id: p for p in old.projects}, {p.project_id: p for p in new.projects}
    for pid in sorted(a.keys() | b.keys()):
        if pid not in a or pid not in b:
            found.append(f"{pid}: {'added' if pid in b else 'removed'}")
            continue
        for field in type(a[pid]).model_fields:
            if getattr(a[pid], field) != getattr(b[pid], field):
                found.append(f"{pid}.{field}: {getattr(a[pid], field)} -> {getattr(b[pid], field)}")
    return found
