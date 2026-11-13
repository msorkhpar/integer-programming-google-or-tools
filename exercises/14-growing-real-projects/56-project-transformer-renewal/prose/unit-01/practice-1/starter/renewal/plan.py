"""The planner's entry point: a request in, a plan out.

Stub: the next lesson replaces the ranking below with a model. Until then `plan` returns the
asset team's worst-first list, and `feasible` checks nothing.
"""

from __future__ import annotations

from .fleet import FIRST_YEAR, Transformer, risk
from .rank import worst_first
from .request import Plan, Request


def plan(fleet: list[Transformer], request: Request) -> Plan:
    """The replacements that remove the most risk within the request's rules."""
    chosen = worst_first(fleet, request.budget)
    by_id = {t.tid: t for t in fleet}
    return Plan({tid: FIRST_YEAR for tid in chosen}, sum(risk(by_id[tid]) for tid in chosen), 0.0, "NOT_SOLVED")


def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool:
    """Does the model allow exactly these replacements? Every other unit is held at 'keep'."""
    return True
