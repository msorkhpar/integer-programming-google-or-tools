"""Two runs that end without a plan: an infeasible funding LP and an unbounded one (GridCap medium)."""

from ortools.math_opt.python import mathopt

from funding_lp import build, spend_in
from gridcap import generate
from solver_log import solve_with_log

medium = generate("medium")

# Infeasible: the first year's budget is cut below what the must-do projects spend in it.
lp = build(medium)
first = medium.years[0]
must_spend = sum(spend_in(p, first) for p in medium.projects if p.must_do)
print(f"must-do spend in {first}: {must_spend:,}; budget cut to 1,000")
lp.cash[first].upper_bound = 1000
result, log = solve_with_log(lp.model, mathopt.SolverType.HIGHS)
for line in log:
    print(line)
print(f"termination: {result.termination.reason.name}; has a feasible solution: {result.has_primal_feasible_solution()}")

# Unbounded: a new project's share is added to the objective, but its upper bound and its
# spend in the cash rows were both forgotten, so nothing limits it.
lp = build(medium)
new = lp.model.add_variable(lb=0, name="f_NEW")
lp.model.objective.set_linear_coefficient(new, 900)
result, log = solve_with_log(lp.model, mathopt.SolverType.HIGHS)
print("=" * 20)
for line in log:
    print(line)
print(f"termination: {result.termination.reason.name}; has a feasible solution: {result.has_primal_feasible_solution()}")
