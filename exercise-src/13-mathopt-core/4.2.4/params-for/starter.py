from __future__ import annotations

import datetime

from ortools.math_opt.python import mathopt

S = mathopt.SolverType


def params_for(solver: mathopt.SolverType, seconds: float, rel_gap: float, threads: int, seed: int,
               first_plan: bool = False) -> mathopt.SolveParameters:
    """The operators' settings, minus whatever this solver refuses through MathOpt (OR-Tools 9.15)."""
    # TODO: set each setting for the solvers that accept it.
    return mathopt.SolveParameters()


if __name__ == "__main__":
    for solver in (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT):
        print(solver.name, params_for(solver, 30, 0.01, 4, 7))
