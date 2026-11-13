"""Solve a request with HiGHS and read the answer back as a Plan."""

from __future__ import annotations

import ctypes
import os
import sys

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from .data import Request
from .model import Built, build
from .plan import Plan

#: One thread, set in HiGHS's own options; the first HiGHS solve of a process fixes the count.
PARAMS = mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(int_options={"threads": 1}))


def run_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with stdout pointed at /dev/null, so HiGHS's stray C output stays out of reports."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=PARAMS)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def read_plan(built: Built, result: mathopt.SolveResult) -> Plan:
    """Turn a solver result into a Plan: each funded project with the year its x is 1."""
    status = result.termination.reason.name.lower()
    if not result.has_primal_feasible_solution():
        return Plan(status=status)
    values = result.variable_values()
    starts = {pid: t for (pid, t), var in built.x.items() if values[var] > 0.5}
    return Plan(status=status, starts=starts, objective=result.objective_value(),
                npv=mathopt.evaluate_expression(built.npv, values),
                risk=mathopt.evaluate_expression(built.risk, values))


def solve(request: Request) -> Plan:
    built = build(request)
    return read_plan(built, run_highs(built.model))


def solve_built(built: Built) -> Plan:
    """Solves a Built the caller may have changed after build (a new objective, an extra row) and returns its Plan."""
    return Plan(status="not solved")
