"""Reading a refusal in OR-Tools 9.15: the exception you catch is not the one MathOpt meant to raise."""

import datetime

from ortools.math_opt import rpc_pb2
from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

milp = build(generate("small")).model
too_many = mathopt.SolveParameters(threads=2)

try:
    solve(milp, mathopt.SolverType.HIGHS, too_many)
except Exception as error:
    print("caught    :", type(error).__name__, "-", error)
    hidden = error.__context__
    print("__context__:", type(hidden).__name__)
    print("  .code   :", hidden.code)
    print("  .message:", hidden.message)
    print("__cause__  :", error.__cause__)


def solve_or_explain(model: mathopt.Model, solver: mathopt.SolverType,
                     params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve, and turn OR-Tools 9.15's AttributeError back into the exception MathOpt meant to raise."""
    try:
        return solve(model, solver, params)
    except AttributeError as error:
        hidden = error.__context__
        if hidden is None or not hasattr(hidden, "code"):
            raise                                       # a genuine AttributeError: leave it alone
        meant = mathopt.status_proto_to_exception(rpc_pb2.StatusProto(code=hidden.code, message=hidden.message))
        raise meant from None


tries = [
    ("HiGHS, threads=2", mathopt.SolverType.HIGHS, too_many),
    ("SCIP, threads=0", mathopt.SolverType.GSCIP, mathopt.SolveParameters(threads=0)),
    ("HiGHS, time_limit=-1s", mathopt.SolverType.HIGHS,
     mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=-1))),
    ("CP-SAT, node_limit=10", mathopt.SolverType.CP_SAT, mathopt.SolveParameters(node_limit=10)),
    ("GLOP, an integer model", mathopt.SolverType.GLOP, None),
]
for label, solver, params in tries:
    try:
        solve_or_explain(milp, solver, params)
        print(f"{label}: solved")
    except (ValueError, NotImplementedError, AssertionError, mathopt.InternalMathOptError) as error:
        print(f"{label}: {type(error).__name__}: {error}")
