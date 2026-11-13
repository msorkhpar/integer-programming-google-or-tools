"""The planner's entry point: a request in, a plan out."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from .fleet import Transformer
from .model import build
from .request import Plan, Request
from .solve import is_feasible, read_plan, solve_quietly


def plan(fleet: list[Transformer], request: Request) -> Plan:
    """The replacements that remove the most risk within the request's rules."""
    built = build(fleet, request)
    params = mathopt.SolveParameters(relative_gap_tolerance=request.gap)
    return read_plan(built, solve_quietly(built.model, params))


def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool:
    """Does the model allow exactly these replacements (id -> year)? Every other choice is held at 0."""
    built = build(fleet, request)
    for (tid, y), var in built.x.items():
        var.lower_bound = var.upper_bound = 1 if replace.get(tid) == y else 0
    return is_feasible(solve_quietly(built.model))


def lp_bound(fleet: list[Transformer], request: Request) -> float:
    """Stub: the next lesson solves the LP relaxation here. Until then, 0."""
    return 0.0
