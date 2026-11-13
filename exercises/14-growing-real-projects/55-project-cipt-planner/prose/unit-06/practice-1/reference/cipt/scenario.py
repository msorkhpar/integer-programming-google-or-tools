"""Scenarios: what planners change before a run. Stub: lesson 14.2.7 writes it."""

from __future__ import annotations

from dataclasses import dataclass, field

from .data import Request
from .plan import Plan


@dataclass(frozen=True)
class Scenario:
    name: str
    budget: dict[int, int] = field(default_factory=dict)
    force_in: tuple[str, ...] = ()
    force_out: tuple[str, ...] = ()
    fix_start: dict[str, int] = field(default_factory=dict)
    note: str = ""


def apply(request: Request, scenario: Scenario) -> Request:
    """The request with the scenario's budgets and overrides. Stub: the request unchanged."""
    return request


@dataclass(frozen=True)
class Diff:
    selected: tuple[str, ...]
    deferred: tuple[str, ...]
    shifted: tuple[tuple[str, int, int], ...]


def diff(base: Plan, other: Plan) -> Diff:
    """What changed between two plans. Stub: nothing."""
    return Diff((), (), ())
