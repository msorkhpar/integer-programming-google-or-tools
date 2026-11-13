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


def best(request: Request, first: str, floor: float | None = None) -> Plan:
    """Maximizes the goal named first ('npv' or 'risk'), with an optional floor on the risk removed as a row named risk_floor; then, holding the first goal at its best within KEEP, maximizes the other. Returns the second solve's Plan, or the first one's when it is not optimal."""
    return Plan(status="not solved")


def dominates(a: Point, b: Point) -> bool:
    """True when point a is at least as good as b on both goals and better on one, each comparison within the slack KEEP gives that goal."""
    return False
