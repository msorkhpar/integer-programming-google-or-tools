"""Which common SolveParameters each solver accepts through MathOpt in OR-Tools 9.15.

Each cell is one solve of GridCap small: the LP relaxation for the LP columns, the MILP for the rest.
"ok" means the solve ran; "--" means mathopt.solve raised instead of solving.
"""

import datetime

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

S, P, E = mathopt.SolverType, mathopt.SolveParameters, mathopt.Emphasis
small = generate("small")
lp, milp = build(small, integer=False).model, build(small).model
columns = [("GLOP", S.GLOP, lp), ("PDLP", S.PDLP, lp), ("HiGHS-LP", S.HIGHS, lp), ("SCIP-LP", S.GSCIP, lp),
           ("HiGHS", S.HIGHS, milp), ("SCIP", S.GSCIP, milp), ("CP-SAT", S.CP_SAT, milp)]
asks = {
    "time_limit": P(time_limit=datetime.timedelta(seconds=10)),
    "iteration_limit": P(iteration_limit=100_000),
    "node_limit": P(node_limit=1_000),
    "solution_limit=1": P(solution_limit=1),
    "cutoff_limit": P(cutoff_limit=1_000.0),
    "objective_limit": P(objective_limit=1e9),
    "best_bound_limit": P(best_bound_limit=1.0),
    "relative_gap_tolerance": P(relative_gap_tolerance=0.001),
    "absolute_gap_tolerance": P(absolute_gap_tolerance=1.0),
    "threads=1": P(threads=1),
    "random_seed": P(random_seed=7),
    "solution_pool_size": P(solution_pool_size=3),
    "lp_algorithm": P(lp_algorithm=mathopt.LPAlgorithm.DUAL_SIMPLEX),
    "presolve=OFF": P(presolve=E.OFF),
    "cuts=OFF": P(cuts=E.OFF),
    "heuristics=OFF": P(heuristics=E.OFF),
    "scaling=OFF": P(scaling=E.OFF),
}


def accepted(solver: mathopt.SolverType, model: mathopt.Model, params: mathopt.SolveParameters) -> bool:
    try:
        solve(model, solver, params)
        return True
    except Exception:                    # the refusal; read_refusal.py shows how to read why
        return False


print(f"{'parameter':<23}" + "".join(f"{name:>9}" for name, _, _ in columns))
for label, params in asks.items():
    cells = ["ok" if accepted(solver, model, params) else "--" for _, solver, model in columns]
    print(f"{label:<23}" + "".join(f"{cell:>9}" for cell in cells))
