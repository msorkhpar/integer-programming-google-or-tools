from __future__ import annotations

import hashlib
import json

#: The fields a run is computed from. Everything else in a record is metadata.
INPUT_KEYS = ("demand", "budget", "settings")


def snapshot(record: dict) -> str:
    """sha256 hex of the record's inputs, written as canonical JSON."""
    # TODO: hash only the inputs, written so that equal inputs always give equal text.
    return hashlib.sha256(b"").hexdigest()


if __name__ == "__main__":
    plan = {"id": "W-1", "name": "base", "owner": "analyst-a",
            "demand": {"north": 41, "south": 37}, "budget": {2027: 900, 2028: 950},
            "settings": {"solver": "HIGHS", "gap": 0.0}}
    print(snapshot(plan))
