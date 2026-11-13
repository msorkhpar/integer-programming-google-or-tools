"""Solve with HiGHS and read the plan back."""

from __future__ import annotations

import ctypes
import os
import sys

from ortools.math_opt.python import mathopt

from .fleet import FIRST_YEAR
from .request import Plan

FOUND = (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE)


def solve_quietly(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, with the process's standard output pointed at /dev/null for the solve.

    The HiGHS bundled in OR-Tools 9.15 can print a stray debug line on a MIP solve with no log asked
    for; it is buffered C output, so it is flushed before the output is restored.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def is_feasible(result: mathopt.SolveResult) -> bool:
    return result.termination.reason in FOUND


def read_plan(built, result: mathopt.SolveResult) -> Plan:
    if not is_feasible(result):
        return Plan({}, 0.0, 0.0, result.termination.reason.name)
    replace = {tid: FIRST_YEAR for tid, var in built.x.items() if result.variable_values(var) > 0.5}
    return Plan(replace, result.objective_value(), result.termination.objective_bounds.dual_bound,
                result.termination.reason.name)
