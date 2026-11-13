"""The same gap, divided by different numbers: HiGHS and SCIP stopped at their first plan, max and min."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

medium = generate("medium")


def first_plan(model: mathopt.Model, solver: mathopt.SolverType) -> tuple[mathopt.SolveResult, list[str]]:
    """Stop at the first plan found, and keep the solver's log."""
    log: list[str] = []
    params = mathopt.SolveParameters(solution_limit=1, enable_output=True)
    if solver == mathopt.SolverType.HIGHS:
        return solve_highs(model, params, log=log), log
    return mathopt.solve(model, solver, params=params, msg_cb=log.extend), log


def footer_gap(log: list[str]) -> str:
    """The last line of the log that starts with "Gap": the solver's own final relative gap."""
    return [line.strip() for line in log if line.strip().startswith("Gap")][-1]


max_npv = build(medium)                                           # maximize NPV, as in the lesson
min_cost = build(medium)                                          # minimize capex, keeping NPV >= 200,000
min_cost.model.minimize(sum(p.capex * min_cost.x[p.project_id] for p in medium.projects))
min_cost.model.add_linear_constraint(
    sum(p.value * min_cost.x[p.project_id] for p in medium.projects) >= 200_000, name="npv_target")

for sense, sel in (("max NPV", max_npv), ("min capex", min_cost)):
    for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP):
        result, log = first_plan(sel.model, solver)
        p = result.termination.objective_bounds.primal_bound
        d = result.termination.objective_bounds.dual_bound
        absolute = abs(p - d)
        print(f"{sense}, {solver.name}: incumbent {p:,.0f}, best bound {d:,.1f}, absolute gap {absolute:,.1f}")
        print(f"  log says   {footer_gap(log)}")
        print(f"  |gap|/|incumbent| = {absolute / abs(p):.4%}   |gap|/|bound| = {absolute / abs(d):.4%}   "
              f"|gap|/min(|incumbent|, |bound|) = {absolute / min(abs(p), abs(d)):.4%}")
