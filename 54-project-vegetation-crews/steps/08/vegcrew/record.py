"""A plan's record: everything needed to say which plan this is and to get it again, as canonical JSON.

Two runs gave the same plan if and only if their records are equal byte for byte. The record names the
input by a hash of its canonical JSON, and the solver by its version and settings, so a difference
points at its cause: other data, another OR-Tools, other settings, or a search that did not repeat.
"""

from __future__ import annotations

import hashlib
import json

import ortools

from vegcrew.data import Override
from vegcrew.planner import SETTINGS, Plan


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def fingerprint(raw: dict, overrides: tuple[Override, ...] = ()) -> str:
    """SHA-256 of the season and the overrides as canonical JSON: equal inputs, equal fingerprints."""
    given = {"season": raw, "overrides": [vars(o) for o in overrides]}
    return hashlib.sha256(canonical(given).encode()).hexdigest()


def plan_record(raw: dict, plan: Plan, overrides: tuple[Override, ...] = ()) -> dict:
    return {
        "input_sha256": fingerprint(raw, overrides),
        "ortools": ortools.__version__,
        "settings": SETTINGS,
        "status": plan.status,
        "risk_carried": plan.risk_carried,
        "cost": plan.cost,
        "trims": [f"{t.cid} on {t.crew} weeks {t.start}-{t.end - 1}" for t in sorted(plan.trims.values(),
                                                                                  key=lambda t: t.cid)],
        "explanation": list(plan.explanation),
    }


def dumps(record: dict) -> str:
    """The record as the text stored and compared: keys sorted, one level of indent, newline at the end."""
    return json.dumps(record, sort_keys=True, indent=1) + "\n"
