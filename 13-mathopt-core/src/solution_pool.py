"""result.solutions: some solvers return more than one plan, best first."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

sel = build(generate("small"))
for solver in (mathopt.SolverType.GSCIP, mathopt.SolverType.HIGHS):
    result = solve(sel.model, solver, mathopt.SolveParameters(solution_pool_size=5)
                   if solver == mathopt.SolverType.GSCIP else None)
    values = [round(s.primal_solution.objective_value) for s in result.solutions]
    print(f"{solver.name}: len(result.solutions) = {len(result.solutions)}, objective values {values}")

best = result.solutions[0].primal_solution
print("solutions[0] is what objective_value() reads:", best.objective_value == result.objective_value())
