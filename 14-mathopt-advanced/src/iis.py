"""An infeasible GridCap scenario: MathOpt's IIS call, which solvers refuse it, and the subsystem by hand."""

from ortools.math_opt.python import mathopt

from find_iis import deletion_filter, report
from gridcap import generate
from plan_model import build, refusal, solve

small = generate("small")
pm = build(small)

# The scenario: the board promises P032 for 2027, and finance caps 2030 and 2031 at 5,000 each.
promised = pm.x["P032", 2027]
promised.lower_bound = 1.0
pm.budget[2030].upper_bound = 5000
pm.budget[2031].upper_bound = 5000
result = solve(pm.model)
print("solve:", result.termination.reason.name, "|", result.termination.detail or "(no detail)")

for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT,
               mathopt.SolverType.GUROBI):
    try:
        mathopt.compute_infeasible_subsystem(pm.model, solver)
    except Exception as error:
        print(f"compute_infeasible_subsystem, {solver.name:6} {type(error).__name__:14} {refusal(error)}")

iis = deletion_filter(pm.model, variables=[promised])
print(f"by hand: feasibility {iis.feasibility.name}, minimal {iis.is_minimal},"
      f" {len(iis.infeasible_subsystem.linear_constraints)} rows,"
      f" {len(iis.infeasible_subsystem.variable_bounds)} variable bounds")
for line in report(iis):
    print("  ", line)

# Read it against the data: what the must-do projects in the subsystem cost, by start year.
for row in iis.infeasible_subsystem.linear_constraints:
    if row.name.startswith("must_"):
        p = small.project(row.name.removeprefix("must_"))
        print(f"{p.project_id}: must start in {list(p.starts())}, cost profile {p.cost_profile}")
