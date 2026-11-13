"""The solve call every module 16 program shares: one CP-SAT worker, so a printed schedule repeats.

CP-SAT runs several workers in parallel by default, and when two schedules tie on the objective,
which one it returns can change from run to run. One worker follows the same search every time on
the same version, so the lessons can quote its schedules. Lesson 4.6.3 covers reproducible runs
with many workers.
"""

from __future__ import annotations

from ortools.sat.python import cp_model


def solve(model: cp_model.CpModel) -> tuple[cp_model.CpSolver, str]:
    """Solve with one worker; return the solver (to read values) and the status name."""
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    status = solver.solve(model)
    return solver, solver.status_name(status)
