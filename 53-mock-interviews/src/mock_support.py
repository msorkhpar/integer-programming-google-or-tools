"""Helpers the mock interviews' programs share: a quiet HiGHS solve and an allowed-plan check.

The HiGHS bundled in OR-Tools 9.15.6755 can print a stray line on some MIP solves with no log
requested (docs/FINDINGS.md, F9), so the solve runs with the process's standard output pointed at
/dev/null and the C buffer flushed before it is restored, as in lesson 6.4.1's `timing_model.py`.
"""

from __future__ import annotations

import ctypes
import os
import sys

from ortools.math_opt.python import mathopt


def quiet_solve(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
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


def allowed(model: mathopt.Model, x: dict, plan: dict) -> bool:
    """Fix every variable in x to the plan (1 for the keys listed, else 0) and ask whether the rows hold."""
    for key, var in x.items():
        value = 1.0 if plan.get(key, 0) else 0.0
        var.lower_bound = value
        var.upper_bound = value
    return quiet_solve(model).termination.reason == mathopt.TerminationReason.OPTIMAL
