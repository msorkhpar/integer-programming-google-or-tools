from __future__ import annotations

import hashlib
import json
import math

#: Lists whose order means nothing, with the field that sorts their records (None: sort the values).
UNORDERED = {"segments": "id", "tags": None}
PLACES = 3


def fixed(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{value} has no canonical form")
    return float(f"{value:.{PLACES}f}") + 0.0


def normalize(value, key: str | None = None):
    if isinstance(value, float):
        return fixed(value)
    if isinstance(value, dict):
        return {k: normalize(v, k) for k, v in value.items()}
    if isinstance(value, list):
        items = [normalize(v) for v in value]
        if key in UNORDERED:
            field = UNORDERED[key]
            items.sort(key=(lambda r: r[field]) if field else None)
        return items
    return value


def digest(doc: dict) -> str:
    """sha256 of the survey's canonical bytes."""
    text = json.dumps(normalize(doc), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


if __name__ == "__main__":
    print(digest({"version": 1, "tags": ["b", "a"], "rate": 0.05}))
