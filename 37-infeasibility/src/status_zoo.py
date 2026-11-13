"""Lesson 9.1.1: what five solvers say about an infeasible model, an unbounded one, and one that is both.

Three two-variable models, each solved as an LP and as a MIP through MathOpt, with presolve on (the
default) and off. The table is what each solver's termination reason was in OR-Tools 9.15.
"""

from ortools.math_opt.python import mathopt

from lock_model import quiet, refusal

S = mathopt.SolverType


def tiny(kind: str, integer: bool) -> mathopt.Model:
    """max x + y over x, y >= 0 with the rows of one kind of model."""
    m = mathopt.Model(name=kind)
    x = m.add_variable(lb=0, is_integer=integer, name="x")
    y = m.add_variable(lb=0, is_integer=integer, name="y")
    if kind == "infeasible":                     # no point has x + y both <= 4 and >= 6
        m.add_linear_constraint(x + y <= 4, name="cap")
        m.add_linear_constraint(x + y >= 6, name="need")
    elif kind == "unbounded":                    # x = y = t keeps the row for every t
        m.add_linear_constraint(x - y <= 2, name="gap")
    else:                                        # "both": no point, and the dual has none either
        m.add_linear_constraint(x - y >= 1, name="above")
        m.add_linear_constraint(x - y <= -1, name="below")
    m.maximize(x + y)
    return m


def reason(kind: str, integer: bool, solver: S, presolve: bool) -> str:
    params = mathopt.SolveParameters() if presolve else mathopt.SolveParameters(presolve=mathopt.Emphasis.OFF)
    try:
        with quiet():
            return mathopt.solve(tiny(kind, integer), solver, params=params).termination.reason.name
    except Exception as error:                                    # the solver's reason is on __context__
        clauses = refusal(error).split("; ")
        return "error: " + clauses[0] + (" ..." if len(clauses) > 1 else "")   # first clause, whole


print(f"{'model':<11}{'type':<5}{'solver':<8}{'presolve on':<26}presolve off")
for kind in ("infeasible", "unbounded", "both"):
    for integer in (False, True):
        for solver in (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT):
            if integer and solver in (S.GLOP, S.PDLP):
                continue                                          # LP solvers: no integer variables
            on = reason(kind, integer, solver, True)
            off = reason(kind, integer, solver, False)
            print(f"{kind:<11}{'MIP' if integer else 'LP':<5}{solver.name:<8}{on:<26}{off}")
