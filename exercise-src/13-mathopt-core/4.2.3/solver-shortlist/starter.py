from __future__ import annotations

from ortools.math_opt.python import mathopt

S = mathopt.SolverType
CANDIDATES = (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT)


def shortlist(model: mathopt.Model, need_duals: bool = False) -> list[mathopt.SolverType]:
    """The candidate solvers that answer this model as written, in CANDIDATES order."""
    # TODO: drop the solvers each rule of the statement rules out.
    return list(CANDIDATES)


if __name__ == "__main__":
    model = mathopt.Model()
    model.add_binary_variable(name="ship")
    model.add_variable(lb=0, ub=40, name="tons")
    print([s.name for s in shortlist(model)])
