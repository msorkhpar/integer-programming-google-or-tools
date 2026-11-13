"""Which stopping parameters each MILP solver accepts through MathOpt (OR-Tools 9.15)."""

import datetime

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

sel = build(generate("small"))

asks = {
    "relative_gap_tolerance": mathopt.SolveParameters(relative_gap_tolerance=0.01),
    "absolute_gap_tolerance": mathopt.SolveParameters(absolute_gap_tolerance=10),
    "time_limit": mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=10)),
    "node_limit": mathopt.SolveParameters(node_limit=10),
    "solution_limit=1": mathopt.SolveParameters(solution_limit=1),
    "solution_limit=3": mathopt.SolveParameters(solution_limit=3),
    "objective_limit": mathopt.SolveParameters(objective_limit=20_000),
    "best_bound_limit": mathopt.SolveParameters(best_bound_limit=25_000),
    "cutoff_limit": mathopt.SolveParameters(cutoff_limit=20_000),
}


def attempt(solver: mathopt.SolverType, params: mathopt.SolveParameters) -> str:
    try:
        if solver == mathopt.SolverType.HIGHS:
            solve_highs(sel.model, params)
        else:
            mathopt.solve(sel.model, solver, params=params)
        return "accepted"
    except Exception as error:  # OR-Tools 9.15 raises AttributeError; the reason is on __context__
        reason = str(error.__context__ or error)
        return "refused: " + reason.split(" [")[0]


for name, params in asks.items():
    print(name)
    for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT):
        print(f"  {solver.name:<6} {attempt(solver, params)}")
