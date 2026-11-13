"""Solve a request and read the answer back as a Plan."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from .data import Request
from .model import Built
from .plan import Plan


def run_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Stub: lesson 14.2.1 solves the model with HiGHS. Until then, nothing is solved."""
    return None


def read_plan(built: Built, result: mathopt.SolveResult) -> Plan:
    """Stub: lesson 14.2.1 reads the solver's answer back. Until then, nothing is funded."""
    return Plan(status="not solved")


def solve(request: Request) -> Plan:
    """Stub: lesson 14.2.1 solves the model. Until then, nothing is funded."""
    return Plan(status="not solved")
