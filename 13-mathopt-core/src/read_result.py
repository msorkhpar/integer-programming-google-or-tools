"""Every part of a SolveResult, read from one MILP solve of GridCap small with HiGHS."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

small = generate("small")
sel = build(small)
result = solve(sel.model, mathopt.SolverType.HIGHS)

# 1. Termination: how the solve ended, and what the solver claims about the problem.
term = result.termination
print("reason        :", term.reason.name)
print("limit         :", term.limit)
print("detail        :", repr(term.detail))
print("problem_status:", term.problem_status.primal_status.name, "/", term.problem_status.dual_status.name)
print("bounds        :", term.objective_bounds.primal_bound, "/", term.objective_bounds.dual_bound)

# 2. The primal solution: the plan and its value.
print("has_primal_feasible_solution:", result.has_primal_feasible_solution())
print("objective_value:", result.objective_value(), "| best_objective_bound:", result.best_objective_bound())
x = sel.x
print("one variable   :", result.variable_values(x["P001"]))
print("a list         :", result.variable_values([x["P001"], x["P002"], x["P003"]]))
print("all, as a dict :", len(result.variable_values()), "entries")

# 3. The dual solution: a MILP has none.
print("has_dual_feasible_solution:", result.has_dual_feasible_solution())
try:
    result.dual_values(sel.budget[2027])
except ValueError as error:
    print("dual_values raised ValueError:", error)

# 4. Statistics: what the search did.
stats = result.solve_stats
print("nodes:", stats.node_count, "| simplex iterations:", stats.simplex_iterations,
      "| solve_time is a", type(stats.solve_time).__name__)
