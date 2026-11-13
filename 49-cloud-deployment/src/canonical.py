"""Copied from lesson 12.2.3 so this module runs on its own: one canonical byte string per snapshot content, and its sha256 digest.

Two snapshots with the same content give the same bytes, whatever order the export wrote keys or
records in and however a float was computed; any change to the content changes the bytes.
GridCap is a fictional utility.
"""

from __future__ import annotations

import hashlib
import json
import math

from snapshot import Snapshot

#: Lists whose order carries no meaning, with the fields that sort them. Every other list keeps its
#: order: `years`, a project's `cost_profile` (year of work 0, 1, ...) and `npv` (by start year).
UNORDERED = {"budget": ("year",), "crews": ("program", "year"), "region_floor": ("region",),
             "projects": ("project_id",)}
#: Decimal places kept from every float. Part of the schema version: changing it changes every id.
FLOAT_PLACES = 6


def fixed(value: float) -> float:
    """A float cut to FLOAT_PLACES decimals by fixed formatting; -0.0 becomes 0.0; NaN and inf are refused."""
    if not math.isfinite(value):
        raise ValueError(f"{value} has no canonical form")
    return float(f"{value:.{FLOAT_PLACES}f}") + 0.0           # + 0.0 turns -0.0 into 0.0


def normalize(value, key: str | None = None):
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return fixed(value)
    if isinstance(value, dict):
        return {k: normalize(v, k) for k, v in value.items()}
    items = [normalize(v) for v in value]
    if key in UNORDERED:
        items.sort(key=lambda record: tuple(record[f] for f in UNORDERED[key]))
    return items


def canonical(snap: Snapshot) -> bytes:
    """The snapshot's content as bytes: validated values, sorted keys and records, fixed floats."""
    tree = normalize(snap.model_dump(mode="json"))
    return json.dumps(tree, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def digest(snap: Snapshot) -> str:
    return hashlib.sha256(canonical(snap)).hexdigest()
