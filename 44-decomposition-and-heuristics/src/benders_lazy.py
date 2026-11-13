"""Benders inside one search: the same cuts sent as lazy constraints from a SCIP callback.

The callback pattern is lesson 4.3.5's (after the OR-Tools example `tsp.py`). HiGHS never calls a
callback (lesson 4.3.5 shows it), so this runs on SCIP.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate

from benders import TOL, cut_expression, monolithic
from capital import build, crew_use
from crew_costs import PROGRAMS, need_of, year_lp

small = generate("small")
cap = build(small)
theta = {y: cap.model.add_variable(lb=0, name=f"theta_{y}") for y in small.years}
cap.model.maximize(cap.model.objective.as_linear_expression() - sum(theta.values()))
use = crew_use(small, cap.x)
sent = {"feasibility": 0, "optimality": 0}


def separate(data: mathopt.CallbackData) -> mathopt.CallbackResult:
    """At every integer plan SCIP finds, solve the yearly LPs and send the cuts the plan breaks."""
    result = mathopt.CallbackResult()
    plan = {pid: t for (pid, t), v in cap.x.items() if data.solution[v] > 0.5}
    need = need_of(small, plan)
    for y in small.years:
        crews = {g: small.crews[g, y] for g in PROGRAMS}
        need_x = {g: use.get((g, y), mathopt.LinearExpression()) for g in PROGRAMS}
        m, rows = year_lp(small, y, {g: need[g, y] for g in PROGRAMS}, phase_one=True)
        short = mathopt.solve(m, mathopt.SolverType.GLOP)
        if short.objective_value() > TOL:
            result.add_lazy_constraint(cut_expression(short, rows, need_x, crews) <= 0)
            sent["feasibility"] += 1
            continue
        m, rows = year_lp(small, y, {g: need[g, y] for g in PROGRAMS})
        sub = mathopt.solve(m, mathopt.SolverType.GLOP)
        if data.solution[theta[y]] < sub.objective_value() - TOL:
            result.add_lazy_constraint(theta[y] >= cut_expression(sub, rows, need_x, crews))
            sent["optimality"] += 1
    return result


registration = mathopt.CallbackRegistration(events={mathopt.Event.MIP_SOLUTION}, add_lazy_constraints=True)
params = mathopt.SolveParameters(relative_gap_tolerance=0.0, threads=1, random_seed=1)
lazy = mathopt.solve(cap.model, mathopt.SolverType.GSCIP, params=params, callback_reg=registration, cb=separate)
_, mono = monolithic(small)
print(f"one SCIP search with lazy cuts: {lazy.termination.reason.name} {lazy.objective_value():,.2f}")
print(f"monolithic MILP:                {mono.objective_value():,.2f}")
print(f"agree within 1e-3: {abs(lazy.objective_value() - mono.objective_value()) <= 1e-3}")
print(f"cuts sent: {sent}")
