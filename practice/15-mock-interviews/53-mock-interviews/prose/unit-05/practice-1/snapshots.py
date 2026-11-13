from __future__ import annotations

import hashlib
import json


def canonical(snapshot: dict) -> bytes:
    """One byte string per content: projects sorted by id, the must-do list sorted, keys sorted, no spaces."""
    # TODO: write the snapshot in its canonical form.
    return b""


def snapshot_digest(snapshot: dict) -> str:
    """The SHA-256 hex digest of the snapshot's canonical bytes."""
    # TODO: digest the canonical bytes.
    return ""


if __name__ == "__main__":
    print(snapshot_digest({"scenario": "base", "budgets": {"2027": 100}, "projects": [], "must_do": []}))
