"""Canonical bytes for a delivery-routing run record, so a determinism test can compare runs.

A record is a dict:
    "started_at": when the run started (text; a clock)
    "stats":      {"wall_seconds": float (a clock), "nodes": int}
    "cost":       float, the routes' total cost
    "routes":     {truck: [stops, in the order visited]}
    "unserved":   a set of stops no truck visits
"""

from __future__ import annotations

import json


def canonical(record: dict) -> bytes:
    """The record without its clocks, floats to 6 decimals, keys sorted, as compact JSON bytes."""
    # TODO
    return b""


def repeats(records: list[dict]) -> bool:
    """True when every record has the same canonical bytes."""
    # TODO
    return True


if __name__ == "__main__":
    run = {"started_at": "09:00", "stats": {"wall_seconds": 1.2, "nodes": 40}, "cost": 512.0,
           "routes": {"t1": ["a", "b"]}, "unserved": {"c"}}
    print(canonical(run))
