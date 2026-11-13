from __future__ import annotations

from ortools.math_opt.python import mathopt

S = mathopt.SolverType
CANDIDATES = (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT)
LP_ONLY = {S.GLOP, S.PDLP}
GIVES_LP_DUALS = {S.GLOP, S.PDLP, S.HIGHS}


def shortlist(model: mathopt.Model, need_duals: bool = False) -> list[mathopt.SolverType]:
    """The candidate solvers that answer this model as written, in CANDIDATES order."""
    flags = [v.integer for v in model.variables()]
    has_integer, has_continuous = any(flags), not all(flags)
    if need_duals and has_integer:
        return []
    chosen = []
    for solver in CANDIDATES:
        if solver in LP_ONLY and has_integer:
            continue
        if solver == S.CP_SAT and has_continuous:
            continue
        if need_duals and solver not in GIVES_LP_DUALS:
            continue
        chosen.append(solver)
    return chosen


if __name__ == "__main__":
    model = mathopt.Model()
    model.add_binary_variable(name="ship")
    model.add_variable(lb=0, ub=40, name="tons")
    print([s.name for s in shortlist(model)])
