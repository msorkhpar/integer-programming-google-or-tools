"""The planner's entry point: a request in, a plan out."""

from __future__ import annotations

from .fleet import Transformer
from .model import build
from .request import Plan, Request
from .solve import is_feasible, read_plan, solve_quietly


def plan(fleet: list[Transformer], request: Request) -> Plan:
    """The replacements that remove the most risk within the request's rules."""
    built = build(fleet, request)
    return read_plan(built, solve_quietly(built.model))


def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool:
    """Does the model allow exactly these replacements? Every other unit is held at 'keep'."""
    built = build(fleet, request)
    for tid, var in built.x.items():
        var.lower_bound = var.upper_bound = 1 if tid in replace else 0
    return is_feasible(solve_quietly(built.model))
