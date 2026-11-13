"""Solver-specific parameters: each solver's own options, set inside SolveParameters."""

from ortools.glop import parameters_pb2 as glop_parameters_pb2
from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2
from ortools.math_opt.solvers.gscip import gscip_pb2
from ortools.sat import sat_parameters_pb2

from gridcap import generate
from selection import build, solve

S, P = mathopt.SolverType, mathopt.SolveParameters
small = generate("small")
milp, lp = build(small).model, build(small, integer=False).model
medium = build(generate("medium")).model


def run(label: str, model: mathopt.Model, solver: mathopt.SolverType, params: mathopt.SolveParameters) -> None:
    try:
        result = solve(model, solver, params)
    except Exception as error:
        print(f"{label:<44} refused: {str(error.__context__ or error).split(' [')[0]}")
        return
    term = result.termination
    limit = term.limit.name if term.limit else "-"
    nodes = f"  nodes {result.solve_stats.node_count}" if solver == S.HIGHS else ""   # HiGHS only
    print(f"{label:<44} {term.reason.name:<8} limit {limit:<12} {result.objective_value():,.0f}{nodes}")


# One option per solver, each in that solver's own message type.
run("HiGHS   highs.int_options mip_max_nodes=1", medium, S.HIGHS,
    P(highs=highs_pb2.HighsOptionsProto(int_options={"mip_max_nodes": 1})))
run("HiGHS   common node_limit=1", medium, S.HIGHS, P(node_limit=1))
run("SCIP    gscip.long_params limits/nodes=1", medium, S.GSCIP,
    P(gscip=gscip_pb2.GScipParameters(long_params={"limits/nodes": 1})))
run("CP-SAT  cp_sat stop_after_first_solution", milp, S.CP_SAT,
    P(cp_sat=sat_parameters_pb2.SatParameters(stop_after_first_solution=True, num_workers=1)))
run("GLOP    glop use_dual_simplex", lp, S.GLOP, P(glop=glop_parameters_pb2.GlopParameters(use_dual_simplex=True)))

# Set in both places, the solver-specific value wins.
run("HiGHS   node_limit=1 and mip_max_nodes=50", medium, S.HIGHS,
    P(node_limit=1, highs=highs_pb2.HighsOptionsProto(int_options={"mip_max_nodes": 50})))

# Another solver's options are ignored, even a nonsense value.
run("HiGHS   with cp_sat num_workers=99", milp, S.HIGHS, P(cp_sat=sat_parameters_pb2.SatParameters(num_workers=99)))
run("HiGHS   with gurobi Threads=2", milp, S.HIGHS, P(gurobi=mathopt.GurobiParameters(param_values={"Threads": "2"})))

# A misspelled option of the solver in use is refused.
run("HiGHS   highs.int_options mip_max_node=1", milp, S.HIGHS,
    P(highs=highs_pb2.HighsOptionsProto(int_options={"mip_max_node": 1})))
