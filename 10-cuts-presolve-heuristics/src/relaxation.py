"""The budget knapsack on GridCap tiny: its LP relaxation, its integer optimum, and the gap between."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import funded, knapsack, solve_quiet

tiny = generate("tiny")
print(f"budget {tiny.capital_budget:,}")
for p in tiny.projects:
    print(f"  {p.project_id}  cost {p.capex:>5,}  value {p.value:>5,}  value per $k {p.value / p.capex:.3f}")

lp = knapsack(tiny, integer=False)
relaxed = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
x = {i: relaxed.variable_values(v) for i, v in lp.x.items()}
print(f"LP relaxation: value {relaxed.objective_value():,.1f}")
print("  " + ", ".join(f"x[{i}] = {v:.4f}" for i, v in x.items() if v > 1e-9))

milp = knapsack(tiny)
best = solve_quiet(milp.model)
print(f"integer optimum: value {best.objective_value():,.0f}, funds {', '.join(funded(milp, best))}")
print(f"integrality gap: {relaxed.objective_value() - best.objective_value():,.1f}")
