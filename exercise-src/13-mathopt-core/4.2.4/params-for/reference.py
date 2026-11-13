from __future__ import annotations

import datetime

from ortools.math_opt.python import mathopt

S = mathopt.SolverType
NO_THREADS = {S.HIGHS}
NO_SEED = {S.PDLP}
LP_SOLVERS = {S.GLOP, S.PDLP}


def params_for(solver: mathopt.SolverType, seconds: float, rel_gap: float, threads: int, seed: int,
               first_plan: bool = False) -> mathopt.SolveParameters:
    """The operators' settings, minus whatever this solver refuses through MathOpt (OR-Tools 9.15)."""
    params = mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=seconds),
                                     relative_gap_tolerance=rel_gap)
    if solver not in NO_THREADS:
        params.threads = threads
    if solver not in NO_SEED:
        params.random_seed = seed
    if first_plan and solver not in LP_SOLVERS:
        params.solution_limit = 1
    return params


if __name__ == "__main__":
    for solver in (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT):
        print(solver.name, params_for(solver, 30, 0.01, 4, 7))
