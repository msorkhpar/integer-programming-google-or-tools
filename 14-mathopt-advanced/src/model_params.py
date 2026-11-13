"""The other fields of ModelSolveParameters: filters, a starting basis, and the hints solvers may ignore."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, refusal, solve

small = generate("small")
pm = build(small)

# Filters: ask for fewer values back. skip_zero_values drops exact zeros only.
nonzero = mathopt.ModelSolveParameters(variable_values_filter=mathopt.VariableFilter(skip_zero_values=True))
for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP):
    values = solve(pm.model, solver, model_params=nonzero).variable_values()
    odd = {v.name: val for v, val in values.items() if abs(val - 1) > 1e-9}
    print(f"{solver.name:5} skip_zero_values: {len(values)} values back, not 1: {odd}")

watch = [pm.x["P032", t] for t in small.project("P032").starts()]
only = mathopt.ModelSolveParameters(variable_values_filter=mathopt.VariableFilter(filtered_items=watch))
print("filtered_items:", {v.name: val for v, val in solve(pm.model, model_params=only).variable_values().items()})

# Accepted by every MIP solver here; whether one acts on them is up to the solver.
extras = mathopt.ModelSolveParameters(branching_priorities={pm.x["P032", 2027]: 10},
                                      lazy_linear_constraints={pm.budget[2027]})
for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT):
    try:
        result = solve(pm.model, solver, model_params=extras)
        print(f"{solver.name:6} priorities + lazy rows: {result.termination.reason.name},"
              f" NPV {result.objective_value():,.0f}")
    except Exception as error:
        print(f"{solver.name:6} refused: {refusal(error)}")

# An LP's starting point is a basis, not a hint: hand GLOP the basis of an earlier solve.
lp = build(generate("medium"))
for v in lp.x.values():
    v.integer = False                                    # the LP relaxation, in place
first = solve(lp.model, mathopt.SolverType.GLOP)
basis = first.solutions[0].basis
lp.budget[2030].upper_bound *= 0.9
cold = solve(lp.model, mathopt.SolverType.GLOP)
warm = solve(lp.model, mathopt.SolverType.GLOP, model_params=mathopt.ModelSolveParameters(initial_basis=basis))
print(f"GLOP after a 2030 cut: cold {cold.solve_stats.simplex_iterations} iterations,"
      f" from the old basis {warm.solve_stats.simplex_iterations}; objectives {cold.objective_value():,.2f}"
      f" and {warm.objective_value():,.2f}")
