"""Two goals at once: the trade between NPV and the risk a plan removes.

`frontier` finds plans none of which beats another on both goals, by the epsilon-constraint
method (lesson 8.3.1): maximize NPV while the risk removed must reach a floor, for floors spread
between the two single-goal plans. Each point is finished by a second, lexicographic solve
(lesson 8.2.1) that keeps its NPV and takes as much risk as that NPV allows, so no point is beaten
on one goal by a plan equal on the other (lesson 8.3.2).
"""

from __future__ import annotations

from dataclasses import dataclass

from .data import Request
from .model import build
from .plan import Plan
from .solve import solve_built

#: Slack on a goal a second pass must keep: NPV is whole $k; risk is a float sum.
KEEP = {"npv": 0.5, "risk": 1e-6}


@dataclass(frozen=True)
class Point:
    npv: float
    risk: float
    plan: Plan


def best(request: Request, first: str, floor: float | None = None) -> Plan:
    """Maximize `first`, then the other goal with `first` held at its best (two solves)."""
    built = build(request)
    goal = {"npv": built.npv, "risk": built.risk}
    if floor is not None:
        built.add("risk_floor", built.risk >= floor)
    built.model.maximize(goal[first])
    plan = solve_built(built)
    if plan.status != "optimal":
        return plan
    other = "risk" if first == "npv" else "npv"
    built.add(f"keep_{first}", goal[first] >= getattr(plan, first) - KEEP[first])
    built.model.maximize(goal[other])
    return solve_built(built)


def dominates(a: Point, b: Point) -> bool:
    return a.npv >= b.npv - KEEP["npv"] and a.risk >= b.risk - KEEP["risk"] and \
        (a.npv > b.npv + KEEP["npv"] or a.risk > b.risk + KEEP["risk"])


def frontier(request: Request, points: int = 5) -> list[Point]:
    """Up to `points` non-dominated plans, from the best NPV to the most risk removed."""
    ends = [best(request, "npv"), best(request, "risk")]
    if any(p.status != "optimal" for p in ends):
        return []
    low, high = ends[0].risk, ends[1].risk
    plans = [ends[0]]
    for k in range(1, points - 1):
        plans.append(best(request, "npv", floor=low + k * (high - low) / (points - 1)))
    plans.append(ends[1])
    found: list[Point] = []
    for plan in plans:
        point = Point(plan.npv, plan.risk, plan)
        if plan.status == "optimal" and not any(abs(point.npv - q.npv) <= KEEP["npv"] for q in found):
            found.append(point)
    return [p for p in found if not any(dominates(q, p) for q in found)]
