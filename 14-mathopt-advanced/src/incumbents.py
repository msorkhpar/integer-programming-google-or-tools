"""A solve callback that watches every new incumbent, and one that stops the solve early.

The callback pattern follows the OR-Tools example `facility_location.py`, which registers
Event.MIP_SOLUTION and reads each new solution in the callback,
https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/facility_location.py
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import EXACT, build, refusal, solve

small = generate("small")
ONE_WORKER = mathopt.SolveParameters(relative_gap_tolerance=0.0, threads=1)   # repeatable CP-SAT runs
PARAMS = {mathopt.SolverType.GSCIP: EXACT, mathopt.SolverType.CP_SAT: ONE_WORKER,
          mathopt.SolverType.HIGHS: EXACT}

for solver, params in PARAMS.items():
    pm = build(small)
    seen = []

    def watch(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        npv = sum(small.project(p).npv[t] * data.solution[v] for (p, t), v in pm.x.items())
        seen.append(round(npv))
        return mathopt.CallbackResult()                  # nothing to ask of the solver

    registration = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION})
    result = solve(pm.model, solver, params=params, callback_reg=registration, cb=watch)
    print(f"{solver.name:6} {result.termination.reason.name}  NPV {result.objective_value():,.0f}"
          f"  callback calls {len(seen)}  incumbents {seen[:8]}{' ...' if len(seen) > 8 else ''}")

# Which events each solver accepts: a refused event raises before the solve starts.
for solver in PARAMS:
    accepted = []
    for event in (mathopt.Event.MIP_SOLUTION, mathopt.Event.MIP, mathopt.Event.MIP_NODE):
        calls = []
        try:
            solve(build(small).model, solver, params=PARAMS[solver],
                  callback_reg=mathopt.CallbackRegistration(events={event}),
                  cb=lambda data: calls.append(data.event) or mathopt.CallbackResult())
            accepted.append(f"{event.name} {'called' if calls else 'accepted, never called'}")
        except Exception as error:
            accepted.append(f"{event.name} refused ({refusal(error)})")
    print(f"{solver.name:6} " + "; ".join(accepted))

# Stop as soon as an incumbent is within 2% of the solver's bound.
pm = build(small)


def good_enough(data: mathopt.CallbackData) -> mathopt.CallbackResult:
    stats = data.mip_stats
    gap = (stats.dual_bound - stats.primal_bound) / abs(stats.primal_bound) if stats.primal_bound > 0 else 1.0
    return mathopt.CallbackResult(terminate=gap <= 0.02)


registration = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION})
result = solve(pm.model, mathopt.SolverType.GSCIP, callback_reg=registration, cb=good_enough)
print(f"stopped early: {result.termination.reason.name} ({result.termination.limit.name}),"
      f" NPV {result.objective_value():,.0f}, bound {result.termination.objective_bounds.dual_bound:,.0f}")
