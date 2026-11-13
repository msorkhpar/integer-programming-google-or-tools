"""Two rows that no point satisfies exactly, d apart: which solvers call the model feasible?"""

from ortools.glop import parameters_pb2 as glop_pb2
from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2
from ortools.math_opt.solvers.gscip import gscip_pb2

from loan_model import row_violations, solve


def squeezed(d: float, integer: bool) -> mathopt.Model:
    """max x  s.t.  x + y <= 1 (cap),  x + y >= 1 + d (floor),  0 <= x <= 1,  0 <= y <= 10."""
    model = mathopt.Model(name="squeezed")
    x = model.add_variable(lb=0, ub=1, is_integer=integer, name="x")
    y = model.add_variable(lb=0, ub=10, name="y")
    model.add_linear_constraint(x + y <= 1, name="cap")
    model.add_linear_constraint(x + y >= 1 + d, name="floor")
    model.maximize(x)
    return model


def verdict(d: float, solver: mathopt.SolverType, integer: bool, params=None) -> str:
    model = squeezed(d, integer)
    result, _ = solve(model, solver, params)
    if not result.has_primal_feasible_solution():
        return result.termination.reason.name
    broken = row_violations(model, result.variable_values())
    worst = max(broken.items(), key=lambda kv: kv[1], default=("-", 0.0))
    return f"{result.termination.reason.name} {worst[0]} off by {worst[1]:.0e}"


RUNS = (("HiGHS, LP", mathopt.SolverType.HIGHS, False), ("HiGHS, MIP", mathopt.SolverType.HIGHS, True),
        ("SCIP, MIP", mathopt.SolverType.GSCIP, True), ("GLOP, LP", mathopt.SolverType.GLOP, False))
GAPS = (5e-8, 5e-7, 5e-6)

if __name__ == "__main__":
    print(f"{'d':12}" + "".join(f"{d:<29.0e}" for d in GAPS))
    for label, solver, integer in RUNS:
        print(f"{label:12}" + "".join(f"{verdict(d, solver, integer):29}" for d in GAPS))

    tight_highs = mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(
        double_options={"primal_feasibility_tolerance": 1e-9, "mip_feasibility_tolerance": 1e-9}))
    tight_scip = mathopt.SolveParameters(gscip=gscip_pb2.GScipParameters(real_params={"numerics/feastol": 1e-9}))
    loose_highs = mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(
        double_options={"mip_feasibility_tolerance": 1e-4}))
    glop_primal = mathopt.SolveParameters(glop=glop_pb2.GlopParameters(primal_feasibility_tolerance=1e-9))
    glop_solution = mathopt.SolveParameters(glop=glop_pb2.GlopParameters(solution_feasibility_tolerance=1e-7))
    defaults = glop_pb2.GlopParameters()
    print(f"GLOP defaults: primal_feasibility_tolerance {defaults.primal_feasibility_tolerance:.0e}, "
          f"solution_feasibility_tolerance {defaults.solution_feasibility_tolerance:.0e}")
    print("with the tolerance changed:")
    for label, solver, integer, params in (
            ("HiGHS, MIP, 1e-9", mathopt.SolverType.HIGHS, True, tight_highs),
            ("SCIP, MIP, 1e-9", mathopt.SolverType.GSCIP, True, tight_scip),
            ("HiGHS, MIP, 1e-4", mathopt.SolverType.HIGHS, True, loose_highs),
            ("GLOP, primal 1e-9", mathopt.SolverType.GLOP, False, glop_primal),
            ("GLOP, solution 1e-7", mathopt.SolverType.GLOP, False, glop_solution)):
        print(f"{label:20}" + "".join(f"{verdict(d, solver, integer, params):29}" for d in GAPS))
