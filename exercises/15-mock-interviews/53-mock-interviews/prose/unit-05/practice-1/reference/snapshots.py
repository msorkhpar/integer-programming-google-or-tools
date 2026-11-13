from __future__ import annotations

import hashlib
import json


def canonical(snapshot: dict) -> bytes:
    """One byte string per content: projects sorted by id, the must-do list sorted, keys sorted, no spaces."""
    content = dict(snapshot)
    content["projects"] = sorted(snapshot["projects"], key=lambda p: p["pid"])
    content["must_do"] = sorted(snapshot["must_do"])
    text = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return text.encode("utf-8")


def snapshot_digest(snapshot: dict) -> str:
    """The SHA-256 hex digest of the snapshot's canonical bytes."""
    return hashlib.sha256(canonical(snapshot)).hexdigest()


if __name__ == "__main__":
    print(snapshot_digest({"scenario": "base", "budgets": {"2027": 100}, "projects": [], "must_do": []}))
