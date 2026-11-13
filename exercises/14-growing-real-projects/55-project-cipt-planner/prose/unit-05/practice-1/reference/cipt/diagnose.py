"""Why a request has no plan, and why a project was left out. Stub: lesson 14.2.6 writes it."""

from __future__ import annotations

from dataclasses import dataclass

from .data import Request


@dataclass(frozen=True)
class Conflict:
    rows: list[str]
    message: str


@dataclass(frozen=True)
class Deferral:
    project: str
    npv_cost: float
    displaced: tuple[str, ...]
    conflict: Conflict | None


def why_infeasible(request: Request) -> Conflict | None:
    """The rows that clash. Stub: reports none."""
    return None


def why_deferred(request: Request, plan, project_id: str) -> Deferral:
    """What funding `project_id` would cost. Stub: nothing."""
    return Deferral(project_id, 0.0, (), None)
