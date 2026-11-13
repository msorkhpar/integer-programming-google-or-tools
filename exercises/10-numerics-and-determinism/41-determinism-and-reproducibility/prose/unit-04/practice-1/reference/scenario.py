from __future__ import annotations

import hashlib
import json


def plain(value):
    """What json cannot write: a set becomes its sorted list."""
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f"cannot digest {type(value).__name__}")


def snapshot_digest(inputs: dict) -> str:
    """sha256 hex digest of the inputs, the same for equal inputs in every process."""
    text = json.dumps(inputs, sort_keys=True, separators=(",", ":"), default=plain)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print(snapshot_digest({"budget": {"2027": 4200}, "force_in": {"T-07", "T-11"}, "gap": 0.0}))
