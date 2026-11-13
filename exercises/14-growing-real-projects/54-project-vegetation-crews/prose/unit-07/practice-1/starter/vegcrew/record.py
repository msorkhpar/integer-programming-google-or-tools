"""Stub for lesson 14.1.7: a plan's record as canonical JSON."""

from __future__ import annotations

from vegcrew.data import Override
from vegcrew.planner import Plan


def fingerprint(raw: dict, overrides: tuple[Override, ...] = ()) -> str:
    return ""


def plan_record(raw: dict, plan: Plan, overrides: tuple[Override, ...] = ()) -> dict:
    return {}


def dumps(record: dict) -> str:
    return "{}"


def canonical(value) -> str:
    """Returns a value as JSON with sorted keys and no spaces, so equal values give equal text."""
    return ""
