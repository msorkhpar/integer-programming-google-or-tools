"""HiGHS's thread count: refused as a common parameter, and fixed by the first HiGHS solve of the process."""

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from gridcap import generate
from selection import build, solve

milp = build(generate("small")).model


def highs_threads(count: int | None) -> mathopt.SolveParameters:
    if count is None:
        return mathopt.SolveParameters()
    return mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(int_options={"threads": count}))


asks = [("common threads=1", mathopt.SolveParameters(threads=1)),
        ("highs threads=1 (first HiGHS solve)", highs_threads(1)),
        ("highs threads=1 again", highs_threads(1)),
        ("highs threads=2", highs_threads(2)),
        ("no thread option", highs_threads(None))]
for label, params in asks:
    try:
        result = solve(milp, mathopt.SolverType.HIGHS, params)
        print(f"{label:<36} {result.termination.reason.name}")
    except Exception as error:
        print(f"{label:<36} refused: {error.__context__}")
