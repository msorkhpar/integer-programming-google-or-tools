"""Other data changes on the same solver: a revised NPV, a new project, a new rule (GridCap medium)."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate

medium = generate("medium")
lp = build(medium)
solver = mathopt.IncrementalSolver(lp.model, mathopt.SolverType.GLOP)
base = solver.solve()
carried = sum(base.variable_values(v) for v in lp.carry.values())
print(f"base               objective {base.objective_value():.4f}  P004 share {base.variable_values(lp.f['P004']):.2f}"
      f"  total carried {carried:,.0f}")


def report(label: str, extra: str = "") -> None:
    warm = solver.solve()
    cold = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    print(f"{label:18} objective {warm.objective_value():.4f}  iterations warm {warm.solve_stats.simplex_iterations:3}"
          f"  cold {cold.solve_stats.simplex_iterations:3}{extra and '  ' + extra}")


# A revised estimate: P004's NPV is three times what the portfolio said.
p004 = medium.project("P004")
lp.model.objective.set_linear_coefficient(lp.f["P004"], 3 * p004.value)
report("P004 NPV x3")

# A new candidate project: spends 500 in 2028 and 700 in 2029, NPV 900.
new = lp.model.add_variable(lb=0, ub=1, name="f_NEW")
lp.cash[2028].set_coefficient(new, 500)
lp.cash[2029].set_coefficient(new, 700)
lp.model.objective.set_linear_coefficient(new, 900)
report("new project")

# A new rule: at most 5,000 carried in total over the plan.
lp.model.add_linear_constraint(sum(lp.carry.values()) <= 5000, name="carry_total")
report("carry_total row")
solver.close()
