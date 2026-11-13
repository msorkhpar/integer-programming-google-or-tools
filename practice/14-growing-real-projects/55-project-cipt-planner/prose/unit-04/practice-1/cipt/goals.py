"""Two goals at once. Stub: lesson 14.2.5 writes it; until then there is no frontier."""

from __future__ import annotations

from dataclasses import dataclass

from .data import Request
from .plan import Plan


@dataclass(frozen=True)
class Point:
    npv: float
    risk: float
    plan: Plan


def frontier(request: Request, points: int = 5) -> list[Point]:
    """Non-dominated plans from the best NPV to the most risk removed. Stub."""
    return []
