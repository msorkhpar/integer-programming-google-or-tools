"""A planners' plan that overspends 2027 by a little: does the model refuse it in every unit?"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from loan_model import solve, spend_in

small = generate("small")
YEAR = 2027

# The planners' plan: the must-do projects, then the highest-NPV projects that fit 2027's budget.
plan = [p for p in small.projects if p.must_do]
for p in sorted(small.projects, key=lambda p: -p.value):
    if p not in plan and spend_in(p, YEAR) and sum(spend_in(q, YEAR) for q in plan) + spend_in(p, YEAR) <= small.budget[YEAR]:
        plan.append(p)
planned = sum(spend_in(p, YEAR) for p in plan)


def allowed(overrun_k: float, per_k: float, solver: mathopt.SolverType) -> str:
    """Fix the plan, set the budget `overrun_k` $k below its spend, write money in units of 1/per_k $k."""
    model = mathopt.Model(name="check")
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in small.projects}
    model.add_linear_constraint(
        sum(spend_in(p, YEAR) * per_k * x[p.project_id] for p in small.projects if spend_in(p, YEAR))
        <= (planned - overrun_k) * per_k, name=f"budget_{YEAR}")
    for p in small.projects:
        x[p.project_id].lower_bound = x[p.project_id].upper_bound = 1.0 if p in plan else 0.0
    result, _ = solve(model, solver)
    return "allowed" if result.has_primal_feasible_solution() else "refused"


if __name__ == "__main__":
    print(f"plan: {len(plan)} projects spending ${planned:,}k in {YEAR}")
    overruns = (0.0005, 0.005, 0.05, 0.5, 5)     # $0.50, $5, $50, $500, $5,000
    print(f"{'over by:':23}" + "".join(f"${o * 1000:<9,.2f}" for o in overruns))
    for unit, per_k in (("$k", 1), ("$M", 1e-3), ("$B", 1e-6)):
        for name, solver in (("HiGHS", mathopt.SolverType.HIGHS), ("SCIP", mathopt.SolverType.GSCIP)):
            print(f"{unit:16}{name:7}" + "".join(f"{allowed(o, per_k, solver):10}" for o in overruns))
